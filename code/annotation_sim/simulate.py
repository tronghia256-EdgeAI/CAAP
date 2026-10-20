"""
code/annotation_sim/simulate.py
───────────────────────────────
Simulate the ground truth a reviewer produces when correcting a seed
tracker's output (docs/PROTOCOL.md, section 4 and Amendment A1).

Track arrays have one row per box: [frame, id, x1, y1, x2, y2], integer
frames, unique (frame, id). Run one class at a time; the caller splits
multi-class data and applies the same ignore/distractor filtering to the
seed and to GT_true beforehand.

prepare(seed, gt) does everything that does not depend on the reviewer:
  * per-frame matching of seed to GT boxes (Hungarian, gated at IoU >= thr);
  * identity matching of seed ids to GT ids (Hungarian on matched-box counts,
    as in IDF1); label(g) is the seed id matched to GT id g, or a fresh label;
  * ID-error episodes: a (seed id, GT id) pair outside the identity matching
    is an error; error pairs whose correction would collide in a frame are
    one episode (e.g. both halves of a swap);
  * missed runs (frame-contiguous unmatched boxes of one GT id) and FP runs
    (frame-contiguous unmatched boxes of one seed id);
  * localisation partners: an unmatched seed box overlapping an unmatched GT
    box in the same frame (IoU >= LOC_THR), i.e. a drifted box.

simulate(prep, reviewer, rng) then draws, in a fixed order:
  * each episode is fixed with probability q: its boxes take label(g), else
    they keep their seed id;
  * each missed run is added with probability r, with GT geometry and
    label(g) (a fresh label if label(g) is taken in one of its frames);
  * each FP run is kept with probability p_fp, minus boxes whose GT partner
    was added (the reviewer replaced them), with its seed id (fresh if taken);
  * each matched box keeps the seed geometry with probability a, else GT's.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import scipy.optimize

IOU_MATCH_THRESHOLD = 0.5
LOC_THR = 0.1
_EPS = np.finfo(float).eps


@dataclass(frozen=True)
class Reviewer:
    r: float        # P(add a missed GT run)
    p_fp: float     # P(keep a false-positive seed run)
    q: float        # P(fix an ID-error episode)
    a: float = 1.0  # P(keep seed geometry on a matched box)

    def __post_init__(self):
        for k in ('r', 'p_fp', 'q', 'a'):
            if not 0.0 <= getattr(self, k) <= 1.0:
                raise ValueError(f'{k} must be in [0, 1], got {getattr(self, k)}')


def read_mot(path, keep=None) -> np.ndarray:
    """MOT txt → [frame, id, x1, y1, x2, y2] rows. keep(raw) → bool mask over raw rows (all columns)."""
    text = Path(path).read_text(encoding='utf-8').strip()
    if not text:
        return np.empty((0, 6))
    raw = np.loadtxt(text.splitlines(), delimiter=',', ndmin=2)
    if raw.size == 0:
        return np.empty((0, 6))
    if keep is not None:
        raw = raw[keep(raw)]
    out = raw[:, :6].copy()
    out[:, 4:6] += out[:, 2:4]
    return out


def write_mot(path, tracks: np.ndarray, cls: int = 1) -> None:
    rows = _validated(tracks, 'tracks')
    lines = [f'{int(f)},{int(i)},{x1:.2f},{y1:.2f},{x2 - x1:.2f},{y2 - y1:.2f},1,{cls},1'
             for f, i, x1, y1, x2, y2 in rows]
    Path(path).write_text('\n'.join(lines) + ('\n' if lines else ''), encoding='utf-8')


def iou_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Plain geometric IoU between (n,4) and (m,4) xyxy boxes, as in code.evaluation.metrics."""
    iw = np.clip(np.minimum(a[:, None, 2], b[None, :, 2]) - np.maximum(a[:, None, 0], b[None, :, 0]), 0, None)
    ih = np.clip(np.minimum(a[:, None, 3], b[None, :, 3]) - np.maximum(a[:, None, 1], b[None, :, 1]), 0, None)
    inter = iw * ih
    area_a = (a[:, 2] - a[:, 0]) * (a[:, 3] - a[:, 1])
    area_b = (b[:, 2] - b[:, 0]) * (b[:, 3] - b[:, 1])
    union = area_a[:, None] + area_b[None, :] - inter
    return np.divide(inter, union, out=np.zeros_like(inter), where=union > 0)


def match(seed: np.ndarray, gt: np.ndarray, thr: float = IOU_MATCH_THRESHOLD) -> np.ndarray:
    """For each seed row, the matched GT row index, or -1 (Hungarian over pairs with IoU >= thr)."""
    seed = np.asarray(seed, dtype=float).reshape(-1, 6)
    gt = np.asarray(gt, dtype=float).reshape(-1, 6)
    return _gated_match(seed, gt, np.arange(len(seed)), np.arange(len(gt)), thr)


def _gated_match(seed, gt, s_rows, g_rows, thr):
    out = np.full(len(seed), -1, dtype=int)
    seed_frames, gt_frames = _by_frame(seed[s_rows, 0]), _by_frame(gt[g_rows, 0])
    for f in seed_frames.keys() & gt_frames.keys():
        si, gi = s_rows[seed_frames[f]], g_rows[gt_frames[f]]
        iou = iou_matrix(seed[si, 2:6], gt[gi, 2:6])
        ok = iou >= thr - _EPS
        if not ok.any():
            continue
        rows, cols = scipy.optimize.linear_sum_assignment(np.where(ok, iou, 0.0), maximize=True)
        keep = ok[rows, cols]
        out[si[rows[keep]]] = gi[cols[keep]]
    return out


def _by_frame(frames: np.ndarray) -> dict:
    order = np.argsort(frames, kind='stable')
    uniq, starts = np.unique(frames[order], return_index=True)
    return dict(zip(uniq.tolist(), np.split(order, starts[1:])))


def _validated(tracks, name) -> np.ndarray:
    t = np.asarray(tracks, dtype=float).reshape(-1, 6)
    if not np.isfinite(t).all():
        raise ValueError(f'{name}: non-finite values')
    if not np.array_equal(t[:, :2], np.round(t[:, :2])):
        raise ValueError(f'{name}: frames and ids must be integers')
    if len(np.unique(t[:, :2], axis=0)) != len(t):
        raise ValueError(f'{name}: duplicate (frame, id) rows')
    return t[np.lexsort(t[:, ::-1].T)]   # canonical order: frame, id, box


def _runs(tracks, rows):
    """Split rows (one id each run) into frame-contiguous runs, ordered by (id, start frame)."""
    rows = rows[np.lexsort((tracks[rows, 0], tracks[rows, 1]))]
    if not len(rows):
        return []
    brk = (np.diff(tracks[rows, 1]) != 0) | (np.diff(tracks[rows, 0]) != 1)
    return np.split(rows, np.flatnonzero(brk) + 1)


class _UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        self.parent[self.find(x)] = self.find(y)


@dataclass
class Prepared:
    seed: np.ndarray            # canonical seed rows
    gt: np.ndarray              # canonical GT rows
    m: np.ndarray               # seed row → matched GT row or -1
    tp: np.ndarray              # matched seed rows
    seed_label: np.ndarray      # seed row → label of its seed id
    gt_label: np.ndarray        # GT row → label(g)
    tp_episode: np.ndarray      # matched seed row (index into tp) → episode index or -1
    err_pairs: np.ndarray       # per error pair: [episode, n boxes, merge] (merge: its seed id is also on another GT id)
    n_episodes: int
    fn_runs: list               # lists of GT rows
    fp_runs: list               # lists of seed rows
    loc_partner: np.ndarray     # GT row → partnered unmatched seed row or -1
    fresh_base: int             # labels >= fresh_base are free for fresh ids
    stats: dict


def prepare(seed, gt, thr: float = IOU_MATCH_THRESHOLD) -> Prepared:
    seed, gt = _validated(seed, 'seed'), _validated(gt, 'gt')
    m = _gated_match(seed, gt, np.arange(len(seed)), np.arange(len(gt)), thr)
    tp = np.flatnonzero(m >= 0)

    s_ids, s_idx = np.unique(seed[:, 1], return_inverse=True)
    g_ids, g_idx = np.unique(gt[:, 1], return_inverse=True)
    seed_label = s_idx.astype(int)
    n_s, n_g = len(s_ids), len(g_ids)

    # Identity matching (IDF1-style) → label(g): its matched seed id, else a fresh label n_s + g.
    counts = np.zeros((n_s, n_g))
    np.add.at(counts, (s_idx[tp], g_idx[m[tp]]), 1)
    gt_id_label = n_s + np.arange(n_g)
    if tp.size:
        rows, cols = scipy.optimize.linear_sum_assignment(counts, maximize=True)
        ok = counts[rows, cols] > 0
        gt_id_label[cols[ok]] = rows[ok]
    gt_label = gt_id_label[g_idx]

    # Error pairs (seed id ≠ label(g)), grouped into episodes by frame collisions on correction.
    pair_s, pair_g = s_idx[tp], g_idx[m[tp]]
    pairs, pair_of_tp = np.unique(np.column_stack([pair_s, pair_g]), axis=0, return_inverse=True)
    pair_of_tp = pair_of_tp.reshape(-1)
    error = pairs[:, 0] != gt_id_label[pairs[:, 1]]
    by_pair = np.argsort(pair_of_tp, kind='stable')
    tp_of_pair = np.split(by_pair, np.cumsum(np.bincount(pair_of_tp, minlength=len(pairs)))[:-1])
    frames_of_pair = {p: set(seed[tp[tp_of_pair[p]], 0].tolist()) for p in np.flatnonzero(error)}
    uf = _UnionFind(len(pairs))
    by_seed = {}
    for p in np.flatnonzero(error):
        by_seed.setdefault(pairs[p, 0], []).append(p)
    for x in np.flatnonzero(error):
        target = gt_id_label[pairs[x, 1]]          # the label x would take if fixed
        for y in by_seed.get(target, []):
            if not frames_of_pair[x].isdisjoint(frames_of_pair[y]):
                uf.union(x, y)
    roots = [uf.find(p) for p in np.flatnonzero(error)]
    # Episodes in a fixed order: by first frame, then root pair.
    first = {}
    for p, rt in zip(np.flatnonzero(error), roots):
        first[rt] = min(first.get(rt, np.inf), min(frames_of_pair[p]))
    order = sorted(first, key=lambda rt: (first[rt], rt))
    ep_of_root = {rt: i for i, rt in enumerate(order)}
    pair_episode = np.full(len(pairs), -1, dtype=int)
    for p, rt in zip(np.flatnonzero(error), roots):
        pair_episode[p] = ep_of_root[rt]
    tp_episode = pair_episode[pair_of_tp] if tp.size else np.empty(0, dtype=int)

    unmatched_gt = np.setdiff1d(np.arange(len(gt)), m[tp])
    unmatched_seed = np.flatnonzero(m < 0)
    fn_runs, fp_runs = _runs(gt, unmatched_gt), _runs(seed, unmatched_seed)

    # Localisation partners: unmatched seed vs unmatched GT boxes in the same frame.
    partner_of_seed = _gated_match(seed, gt, unmatched_seed, unmatched_gt, LOC_THR)
    loc_partner = np.full(len(gt), -1, dtype=int)
    has = np.flatnonzero(partner_of_seed >= 0)
    loc_partner[partner_of_seed[has]] = has

    stats = dict(tp=int(tp.size), error_pairs=int(error.sum()), episodes=len(order),
                 episode_sizes=np.bincount(pair_episode[error], minlength=len(order)).tolist(),
                 fn_runs=len(fn_runs), fp_runs=len(fp_runs), loc_pairs=int(has.size))
    err = np.flatnonzero(error)
    n_pairs_of_seed = np.bincount(pairs[:, 0], minlength=n_s) if len(pairs) else np.zeros(n_s, dtype=int)
    err_pairs = np.column_stack([pair_episode[err], [len(tp_of_pair[p]) for p in err],
                                 n_pairs_of_seed[pairs[err, 0]] > 1]).astype(int).reshape(-1, 3)
    return Prepared(seed, gt, m, tp, seed_label, gt_label, tp_episode, err_pairs, len(order),
                    fn_runs, fp_runs, loc_partner, n_s + n_g, stats)


def simulate(prep: Prepared, reviewer: Reviewer, rng: np.random.Generator, with_origin: bool = False):
    """Return (GT_S, stats): simulated reviewed ground truth [frame, id, x1, y1, x2, y2] and counts.

    with_origin=True also returns origin, one row per GT_S row: (0, seed row) when the box has seed
    geometry, (1, GT row) when it has GT geometry; rows index prep.seed / prep.gt.
    The random draws do not depend on the reviewer, so one rng seed gives common random numbers across θ.
    """
    seed, gt, tp = prep.seed, prep.gt, prep.tp
    u_ep = rng.random(prep.n_episodes)
    u_fn = rng.random(len(prep.fn_runs))
    u_fp = rng.random(len(prep.fp_runs))
    u_geo = rng.random(tp.size)

    fixed = u_ep < reviewer.q
    tp_fixed = np.zeros(tp.size, dtype=bool)
    has_ep = prep.tp_episode >= 0
    tp_fixed[has_ep] = fixed[prep.tp_episode[has_ep]]
    labels = np.where(tp_fixed, prep.gt_label[prep.m[tp]], prep.seed_label[tp])
    boxes = seed[tp, 2:6].copy()
    use_gt = u_geo >= reviewer.a
    boxes[use_gt] = gt[prep.m[tp[use_gt]], 2:6]
    parts = [np.column_stack([seed[tp, 0], labels, boxes])]
    origins = [np.column_stack([use_gt.astype(int), np.where(use_gt, prep.m[tp], tp)])]
    taken = set(zip(seed[tp, 0].tolist(), labels.tolist()))
    fresh = prep.fresh_base
    stats = dict(episodes_fixed=int(fixed.sum()), fn_added=0, fn_added_boxes=0, fn_fresh=0,
                 fp_kept=0, fp_kept_boxes=0, fp_replaced_boxes=0, fp_fresh=0,
                 missed_lengths=[len(run) for run, u in zip(prep.fn_runs, u_fn) if u >= reviewer.r],
                 unfixed_pairs=prep.err_pairs[~fixed[prep.err_pairs[:, 0]], 1:].tolist() if len(prep.err_pairs) else [],
                 kept_fp_lengths=[])

    replaced = set()
    for run, u in zip(prep.fn_runs, u_fn):
        if u >= reviewer.r:
            continue
        label = int(prep.gt_label[run[0]])
        if any((f, label) in taken for f in gt[run, 0].tolist()):
            label, fresh = fresh, fresh + 1
            stats['fn_fresh'] += 1
        taken.update((f, label) for f in gt[run, 0].tolist())
        replaced.update(int(s) for s in prep.loc_partner[run] if s >= 0)
        parts.append(np.column_stack([gt[run, 0], np.full(len(run), label), gt[run, 2:6]]))
        origins.append(np.column_stack([np.ones(len(run), dtype=int), run]))
        stats['fn_added'] += 1
        stats['fn_added_boxes'] += len(run)

    for run, u in zip(prep.fp_runs, u_fp):
        if u >= reviewer.p_fp:
            continue
        kept = np.array([s for s in run if s not in replaced], dtype=int)
        stats['fp_replaced_boxes'] += len(run) - len(kept)
        if not kept.size:
            continue
        label = int(prep.seed_label[kept[0]])
        if any((f, label) in taken for f in seed[kept, 0].tolist()):
            label, fresh = fresh, fresh + 1
            stats['fp_fresh'] += 1
        taken.update((f, label) for f in seed[kept, 0].tolist())
        parts.append(np.column_stack([seed[kept, 0], np.full(len(kept), label), seed[kept, 2:6]]))
        origins.append(np.column_stack([np.zeros(len(kept), dtype=int), kept]))
        stats['fp_kept'] += 1
        stats['fp_kept_boxes'] += len(kept)
        stats['kept_fp_lengths'].append(len(kept))

    out = np.concatenate(parts)
    origin = np.concatenate(origins).astype(int)
    _, ids = np.unique(out[:, 1], return_inverse=True)
    out[:, 1] = ids.reshape(-1) + 1
    order = np.lexsort((out[:, 1], out[:, 0]))
    out, origin = out[order], origin[order]
    if len(np.unique(out[:, :2], axis=0)) != len(out):
        raise RuntimeError('simulated GT has duplicate (frame, id) rows')
    return (out, stats, origin) if with_origin else (out, stats)
