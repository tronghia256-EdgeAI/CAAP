"""
code/seedbias/experiment.py
───────────────────────────
Run the experiments of PROTOCOL.md (section 4, A1, A3, A4) on preprocessed
tracks: the θ grid for every seed system (H1, H2 ranking), the H2 null model
and the H3 protocols on the r-slice S_r, and secondary metrics at θ_ref.
Summaries are in code.seedbias.analysis.

    python -m code.seedbias.experiment --dataset fasttrack --out data/processed/seed_bias

IDF1 on every simulated GT is computed exactly as TrackEval's Identity metric
does it (counts of same-frame pairs with IoU >= 0.5, then a maximum-weight
id matching), but from IoU pairs precomputed once against the GT rows and the
seed rows, because every GT_S box carries either GT or seed geometry. A test
checks this against the TrackEval bridge.
"""

from __future__ import annotations

import argparse
import itertools
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import scipy.optimize
import scipy.sparse
import scipy.sparse.csgraph

from code.annotation_sim.simulate import Reviewer, _validated, match, prepare, read_mot, simulate
from code.seedbias import analysis as AN
from code.seedbias import data as D
from code.seedbias.evaluate import _BaseDataset, evaluate_sequence, summarize
from code.seedbias.null_model import null_gt
from code.seedbias.protocols import consensus_seed, union_seed
from code.utils.files import git_state, sha256, source_hash

SOURCES = ('code/annotation_sim/simulate.py', 'code/seedbias/experiment.py', 'code/seedbias/analysis.py',
           'code/seedbias/null_model.py', 'code/seedbias/protocols.py', 'code/seedbias/evaluate.py')

GRID = dict(r=(0, 0.25, 0.5, 0.75, 0.9, 1), p_fp=(0, 0.1, 0.25, 0.5), q=(0, 0.5, 0.9, 1), a=(1, 0))
THETA_REF = dict(r=0.75, p_fp=0.1, q=0.5, a=1)
N_SEEDS = 10
CELLS = [dict(zip(GRID, v)) for v in itertools.product(*GRID.values())]
REF = CELLS.index(THETA_REF)
SLICE = [CELLS.index({**THETA_REF, 'r': r}) for r in GRID['r']]     # S_r (A4 item 2)
SHARED, OTHER = 'yolo11x', 'yolo11n'
TRACKERS = ('botsort', 'bytetrack', 'ocsort', 'sort')


@dataclass
class Unit:
    seq: str
    cls: str
    n_frames: int
    gt: np.ndarray
    tracks: dict            # tracker → [frame, id, x1, y1, x2, y2]


def load_units(tracks_root: Path, dataset: str, systems) -> list:
    """One unit per (sequence, class); tracks keyed by system name '<detector>/<tracker>'."""
    units = []
    for seq_dir in sorted((tracks_root / dataset / 'gt').iterdir()):
        n_frames = json.loads((seq_dir / 'seqinfo.json').read_text())['n_frames']
        for cls in D.SPEC[dataset]['classes']:
            tracks = {}
            for system in systems:
                det, trk = system.split('/')
                tracks[system] = _validated(read_mot(tracks_root / dataset / det / seq_dir.name / cls / f'{trk}.txt'),
                                            system)                  # rejects duplicate (frame, id) rows
            units.append(Unit(seq_dir.name, cls, n_frames, read_mot(seq_dir / f'{cls}.txt'), tracks))
    return units


def _rng(*key):
    return np.random.default_rng(list(key))


def iou_pairs(a: np.ndarray, b: np.ndarray, thr: float = 0.5):
    """All same-frame (row of a, row of b) pairs with IoU >= thr, IoU as computed by TrackEval."""
    ai, bi = [], []
    fa, fb = _groups(a[:, 0]), _groups(b[:, 0])
    for f in fa.keys() & fb.keys():
        ia, ib = fa[f], fb[f]
        iou = _BaseDataset._calculate_box_ious(a[ia, 2:6], b[ib, 2:6], box_format='x0y0x1y1')
        r, c = np.nonzero(iou >= thr)
        ai.append(ia[r])
        bi.append(ib[c])
    cat = lambda x: np.concatenate(x) if x else np.empty(0, dtype=int)
    return cat(ai), cat(bi)


def _groups(frames):
    order = np.argsort(frames, kind='stable')
    uniq, starts = np.unique(frames[order], return_index=True)
    return dict(zip(uniq.tolist(), np.split(order, starts[1:])))


def max_matching(rows: np.ndarray, cols: np.ndarray) -> int:
    """Maximum total count of a one-to-one matching, counts = multiplicity of (row, col) pairs."""
    if not rows.size:
        return 0
    pairs, w = np.unique(np.column_stack([rows, cols]), axis=0, return_counts=True)
    r_ids, r = np.unique(pairs[:, 0], return_inverse=True)
    c_ids, c = np.unique(pairs[:, 1], return_inverse=True)
    n_r, n_c = len(r_ids), len(c_ids)
    graph = scipy.sparse.coo_matrix((np.ones(len(w)), (r, n_r + c)), shape=(n_r + n_c, n_r + n_c))
    _, comp = scipy.sparse.csgraph.connected_components(graph, directed=False)
    total = 0
    edge_comp = comp[r]
    for k in np.unique(edge_comp):
        e = edge_comp == k
        rr, rinv = np.unique(r[e], return_inverse=True)
        cc, cinv = np.unique(c[e], return_inverse=True)
        m = np.zeros((len(rr), len(cc)))
        m[rinv, cinv] = w[e]
        i, j = scipy.optimize.linear_sum_assignment(m, maximize=True)
        total += int(m[i, j].sum())
    return total


class FastIdentity:
    """IDTP of each tracker against a GT made of GT-geometry and seed-geometry boxes of one unit.

    gt_rows / seed_rows must be the arrays that `origin` indexes (prep.gt / prep.seed, which prepare()
    puts in canonical order — not the unit's own row order).
    """

    def __init__(self, unit: Unit, gt_rows: np.ndarray, seed_rows: np.ndarray | None):
        self.tracks = unit.tracks
        self.n_tr = {t: len(x) for t, x in unit.tracks.items()}
        self.tid = {t: np.unique(x[:, 1], return_inverse=True)[1].reshape(-1) for t, x in unit.tracks.items()}
        self.to_gt = {t: iou_pairs(x, gt_rows) for t, x in unit.tracks.items()}
        self.to_seed = ({t: iou_pairs(x, seed_rows) for t, x in unit.tracks.items()}
                        if seed_rows is not None else None)
        self.n_gt_rows = len(gt_rows)
        self.n_seed_rows = 0 if seed_rows is None else len(seed_rows)

    def idtp(self, labels: np.ndarray, origin: np.ndarray, extra: np.ndarray | None = None) -> dict:
        """labels/origin as returned by simulate(with_origin=True); extra: further GT rows
        [frame, label, x1, y1, x2, y2] with their own geometry (null-model FP copies)."""
        lab_gt = np.full(self.n_gt_rows, -1)
        lab_seed = np.full(self.n_seed_rows, -1)
        g = origin[:, 0] == 1
        lab_gt[origin[g, 1]] = labels[g]
        lab_seed[origin[~g, 1]] = labels[~g]
        out = {}
        for t in self.n_tr:
            ti, gi = self.to_gt[t]
            lab, trk = [lab_gt[gi]], [self.tid[t][ti]]
            if self.to_seed is not None:
                ti2, si = self.to_seed[t]
                lab.append(lab_seed[si])
                trk.append(self.tid[t][ti2])
            if extra is not None and len(extra):
                ti3, ei = iou_pairs(self.tracks[t], extra)
                lab.append(extra[ei, 1].astype(int))
                trk.append(self.tid[t][ti3])
            lab, trk = np.concatenate(lab), np.concatenate(trk)
            keep = lab >= 0
            out[t] = max_matching(lab[keep], trk[keep])
        return out


def _run_seed(args):
    """Grid (all cells × rng seeds) and the null model on S_r, for one seed system.

    Each unit's result is checkpointed in parts_dir and reused on rerun (the directory name is
    keyed on code, inputs and grid, so stale parts are never mixed in).
    """
    tracks_root, dataset, systems, a, a_name, parts_dir = args
    parts_dir = Path(parts_dir)
    parts_dir.mkdir(parents=True, exist_ok=True)
    units = load_units(Path(tracks_root), dataset, systems)
    shape = (N_SEEDS, len(systems), len(units))
    idtp = np.zeros((len(CELLS),) + shape, dtype=np.int64)
    ngt = np.zeros((len(CELLS), N_SEEDS, len(units)), dtype=np.int64)
    null_idtp = np.zeros((len(SLICE),) + shape, dtype=np.int64)
    null_ngt = np.zeros((len(SLICE), N_SEEDS, len(units)), dtype=np.int64)
    null_skipped = np.zeros(len(SLICE), dtype=np.int64)
    episodes = np.zeros((len(units), 2), dtype=np.int64)
    for u, unit in enumerate(units):
        part = parts_dir / f"{a_name.replace('/', '_')}_u{u:04d}.npz"
        if part.exists():
            z = np.load(part)
            idtp[..., u], ngt[..., u], null_idtp[..., u], null_ngt[..., u] = z['idtp'], z['ngt'], z['null_idtp'], z['null_ngt']
            null_skipped += z['null_skipped']
            episodes[u] = z['episodes']
            continue
        skipped_before = null_skipped.copy()
        prep = prepare(unit.tracks[a_name], unit.gt)
        episodes[u] = prep.n_episodes, prep.stats['error_pairs']
        fast = FastIdentity(unit, prep.gt, prep.seed)
        fast_gt = FastIdentity(unit, prep.gt, None)
        for k in range(N_SEEDS):
            for c, cell in enumerate(CELLS):
                out, st, origin = simulate(prep, Reviewer(**cell), _rng(k, a, u), with_origin=True)
                ngt[c, k, u] = len(out)
                res = fast.idtp(out[:, 1].astype(int), origin)
                idtp[c, k, :, u] = [res[s] for s in systems]
                if c in SLICE:
                    j = SLICE.index(c)
                    labels, extra, skipped = null_gt(prep.gt, unit.n_frames, st['missed_lengths'],
                                                     st['unfixed_pairs'], st['kept_fp_lengths'], _rng(k, a, u, 1))
                    keep = labels >= 0
                    origin_n = np.column_stack([np.ones(keep.sum(), dtype=int), np.flatnonzero(keep)])
                    res_n = fast_gt.idtp(labels[keep], origin_n, extra)
                    null_idtp[j, k, :, u] = [res_n[s] for s in systems]
                    null_ngt[j, k, u] = keep.sum() + len(extra)
                    null_skipped[j] += skipped
        tmp = part.with_name(part.stem + '.part.npz')
        np.savez(tmp, idtp=idtp[..., u], ngt=ngt[..., u], null_idtp=null_idtp[..., u], null_ngt=null_ngt[..., u],
                 null_skipped=null_skipped - skipped_before, episodes=episodes[u])
        tmp.replace(part)
        print(f'  seed {a_name}: unit {u + 1}/{len(units)} ({unit.seq}/{unit.cls})', flush=True)
    return dict(idtp=idtp, ngt=ngt, null_idtp=null_idtp, null_ngt=null_ngt, null_skipped=null_skipped,
                episodes=episodes)


def _run_ref_only(args):
    """θ_ref only, for one seed: idtp[1, k, system, unit], ngt[1, k, unit] (A5 item 10 sensitivity)."""
    tracks_root, dataset, systems, a, a_name = args
    units = load_units(Path(tracks_root), dataset, systems)
    idtp = np.zeros((1, N_SEEDS, len(systems), len(units)), dtype=np.int64)
    ngt = np.zeros((1, N_SEEDS, len(units)), dtype=np.int64)
    for u, unit in enumerate(units):
        prep = prepare(unit.tracks[a_name], unit.gt)
        fast = FastIdentity(unit, prep.gt, prep.seed)
        for k in range(N_SEEDS):
            out, _, origin = simulate(prep, Reviewer(**THETA_REF), _rng(k, a, u), with_origin=True)
            ngt[0, k, u] = len(out)
            res = fast.idtp(out[:, 1].astype(int), origin)
            idtp[0, k, :, u] = [res[s] for s in systems]
    return dict(idtp=idtp, ngt=ngt)


def protocol_list(seed_systems) -> list:
    """H3 protocols (A4 item 4), members in alphabetical order of tracker name."""
    protos = [dict(kind='union', name='P1 union ' + '+'.join(m.split('/')[1] for m in combo), members=list(combo))
              for k in (2, 3) for combo in itertools.combinations(sorted(seed_systems), k)]
    protos.append(dict(kind='consensus', name='P2 consensus', members=sorted(seed_systems)))
    return protos


def _run_protocol(args):
    """One H3 protocol on S_r: idtp[j, k, system, unit], ngt[j, k, unit], cost[unit]."""
    tracks_root, dataset, systems, p, proto = args
    units = load_units(Path(tracks_root), dataset, systems)
    idtp = np.zeros((len(SLICE), N_SEEDS, len(systems), len(units)), dtype=np.int64)
    ngt = np.zeros((len(SLICE), N_SEEDS, len(units)), dtype=np.int64)
    cost = np.zeros(len(units), dtype=np.int64)
    for u, unit in enumerate(units):
        outputs = [unit.tracks[m] for m in proto['members']]
        if proto['kind'] == 'union':
            seed, n_cand = union_seed(outputs), 0
        else:
            seed, n_cand = consensus_seed(outputs)
        cost[u] = len(seed) + n_cand
        prep = prepare(seed, unit.gt)
        fast = FastIdentity(unit, prep.gt, prep.seed)
        for k in range(N_SEEDS):
            for j, c in enumerate(SLICE):
                out, _, origin = simulate(prep, Reviewer(**CELLS[c]), _rng(k, 100 + p, u), with_origin=True)
                ngt[j, k, u] = len(out)
                res = fast.idtp(out[:, 1].astype(int), origin)
                idtp[j, k, :, u] = [res[s] for s in systems]
    return dict(idtp=idtp, ngt=ngt, cost=cost)


def _run_secondary(args):
    """Secondary metrics (A3 item 6) at θ_ref for one seed: summaries per (k, evaluated system)."""
    tracks_root, dataset, systems, a, a_name, evaluated = args
    units = load_units(Path(tracks_root), dataset, systems)
    per = {(k, s): [] for k in range(N_SEEDS) for s in evaluated}
    for u, unit in enumerate(units):
        prep = prepare(unit.tracks[a_name], unit.gt)
        for k in range(N_SEEDS):
            gts, _ = simulate(prep, Reviewer(**THETA_REF), _rng(k, a, u))   # the grid's θ_ref draw
            for s in evaluated:
                per[(k, s)].append(evaluate_sequence(unit.tracks[s], gts, unit.n_frames))
    return {f'{k}|{s}': summarize(r) for (k, s), r in per.items()}


def true_scores(units, trackers):
    """IDTP of each tracker on GT_true, per unit; plus GT and tracker box counts."""
    idtp = np.zeros((len(trackers), len(units)), dtype=np.int64)
    for u, unit in enumerate(units):
        fast = FastIdentity(unit, unit.gt, None)
        origin = np.column_stack([np.ones(len(unit.gt), dtype=int), np.arange(len(unit.gt))])
        labels = np.unique(unit.gt[:, 1], return_inverse=True)[1].reshape(-1)
        res = fast.idtp(labels, origin)
        idtp[:, u] = [res[t] for t in trackers]
    ngt = np.array([len(u.gt) for u in units])
    ntr = np.array([[len(u.tracks[t]) for u in units] for t in trackers])
    return idtp, ngt, ntr


def class_confusion(units, seed_systems) -> dict:
    """A5 diagnostic: per class, share of seed boxes that miss their own class's GT but match
    (IoU >= 0.5) a GT box of another evaluation class in the same frame; and zero-GT units."""
    by_seq = {}
    for unit in units:
        by_seq.setdefault(unit.seq, []).append(unit)
    out = {}
    for unit in units:
        others = [v.gt for v in by_seq[unit.seq] if v is not unit and len(v.gt)]
        other_gt = np.concatenate(others) if others else np.empty((0, 6))
        c = out.setdefault(unit.cls, dict(seed_boxes=0, other_class_matches=0, zero_gt_units=0, zero_gt_boxes=0))
        for s in seed_systems:
            tr = unit.tracks[s]
            own = match(tr, unit.gt) >= 0 if len(unit.gt) else np.zeros(len(tr), dtype=bool)
            c['seed_boxes'] += len(tr)
            if len(other_gt) and (~own).any():
                c['other_class_matches'] += int((match(tr[~own], other_gt) >= 0).sum())
        if not len(unit.gt):
            c['zero_gt_units'] += 1
            c['zero_gt_boxes'] += sum(len(unit.tracks[s]) for s in seed_systems)
    for c in out.values():
        c['share'] = c['other_class_matches'] / max(c['seed_boxes'], 1)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--tracks', type=Path, default=Path('data/processed/tracks'))
    ap.add_argument('--dataset', required=True, choices=sorted(D.SPEC))
    ap.add_argument('--out', type=Path, default=Path('data/processed/seed_bias'))
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--skip', nargs='*', default=[], choices=['protocols', 'secondary', 'sort_all'])
    args = ap.parse_args(argv)

    systems = [f'{d}/{t}' for d in (SHARED, OTHER) for t in TRACKERS]
    seed_systems = [s for s in systems if s.startswith(SHARED + '/')]
    seed_sys = [systems.index(s) for s in seed_systems]
    other_sys = [systems.index(s) for s in systems if s not in seed_systems]
    units = load_units(args.tracks, args.dataset, systems)
    idtp_true, ngt_true, ntr = true_scores(units, systems)
    seqs = sorted({u.seq for u in units})
    seq_of_unit = np.array([seqs.index(u.seq) for u in units])
    classes = sorted({u.cls for u in units})
    class_of_unit = np.array([classes.index(u.cls) for u in units])
    out = args.out / args.dataset
    out.mkdir(parents=True, exist_ok=True)
    root = str(args.tracks)
    protos = protocol_list(seed_systems)
    inputs = {p.relative_to(args.tracks).as_posix(): sha256(p)
              for p in sorted((args.tracks / args.dataset).rglob('*.txt'))}
    run_key = hashlib.sha256(json.dumps([source_hash(*SOURCES), inputs, GRID, N_SEEDS, systems]).encode()).hexdigest()
    parts_dir = out / 'parts' / run_key[:16]
    provenance = dict(**git_state(), source_hash=source_hash(*SOURCES), run_key=run_key, grid=GRID,
                      theta_ref=THETA_REF, n_seeds=N_SEEDS, n_boot=AN.N_BOOT, systems=systems, inputs_sha256=inputs)
    (out / 'provenance.json').write_text(json.dumps(provenance, indent=1))

    pool = ProcessPoolExecutor(max_workers=args.workers) if args.workers > 0 else None
    pmap = pool.map if pool else map                          # --workers 0: in-process (tests)
    per_seed = list(pmap(_run_seed, [(root, args.dataset, systems, a, systems[a], str(parts_dir)) for a in seed_sys]))
    per_proto = ([] if 'protocols' in args.skip else list(pmap(
        _run_protocol, [(root, args.dataset, systems, p, pr) for p, pr in enumerate(protos)])))
    secondary = ([] if 'secondary' in args.skip else list(pmap(
        _run_secondary, [(root, args.dataset, systems, a, systems[a], seed_systems) for a in seed_sys])))
    alt = [s.replace('/sort', '/sort_all') if s == f'{SHARED}/sort' else s for s in seed_systems]
    sort_alt = None
    has_alt = all((args.tracks / args.dataset / SHARED / u.seq / u.cls / 'sort_all.txt').exists() for u in units)
    if 'sort_all' not in args.skip and has_alt:
        alt_units = load_units(args.tracks, args.dataset, alt)
        alt_true = true_scores(alt_units, alt)
        per_alt = list(pmap(_run_ref_only, [(root, args.dataset, alt, a, alt[a]) for a in range(len(alt))]))
        alt_res = dict(idtp=np.stack([r['idtp'] for r in per_alt]), ngt=np.stack([r['ngt'] for r in per_alt]),
                       idtp_true=alt_true[0], ngt_true=alt_true[1], ntr=alt_true[2])
        alt_pooled = AN.Pooled(alt_res, seq_of_unit)
        sort_alt = dict(systems=alt, h1=AN.h1(alt_res, alt_pooled, list(range(len(alt))), list(range(len(alt))),
                                               [], [THETA_REF])[0])
    if pool:
        pool.shutdown()
    res = {key: np.stack([r[key] for r in per_seed]) for key in per_seed[0]}
    res.update(idtp_true=idtp_true, ngt_true=ngt_true, ntr=ntr)
    if per_proto:
        res.update(proto_idtp=np.stack([r['idtp'] for r in per_proto]),
                   proto_ngt=np.stack([r['ngt'] for r in per_proto]),
                   proto_cost=np.stack([r['cost'] for r in per_proto]))
    np.savez_compressed(out / 'arrays.npz', seq_of_unit=seq_of_unit, **res)

    pooled = AN.Pooled(res, seq_of_unit)
    slice_cells = [dict(index=c, theta=CELLS[c]) for c in SLICE]
    summary = dict(
        systems=systems, seed_systems=seed_systems, units=[[u.seq, u.cls] for u in units], theta_ref=THETA_REF,
        idf1_true=dict(zip(systems, pooled.true[:, 0].tolist())),
        h1=AN.h1(res, pooled, seed_sys, seed_sys, other_sys, CELLS),
        h1_diagnostics=dict(classes=classes, **AN.h1_diagnostics(
            res, seq_of_unit, class_of_unit, seed_sys, seed_sys, other_sys, REF, CELLS.index({**THETA_REF, 'a': 0}),
            exclude=[systems.index(f'{SHARED}/sort')])),
        class_confusion=class_confusion(units, seed_systems),
        sort_all_sensitivity=sort_alt,
        ranking=AN.ranking(res, pooled, CELLS),
        h2=AN.h2(res, pooled, slice_cells, SLICE.index(REF)),
        h3=(AN.h3(res, pooled, seed_sys, seed_systems, protos, slice_cells, SLICE.index(REF), int(ngt_true.sum()))
            if per_proto else None),
        secondary=dict(zip(seed_systems, secondary)) if secondary else None,
        secondary_true=({s: summarize([evaluate_sequence(u.tracks[s], u.gt, u.n_frames) for u in units])
                         for s in seed_systems} if secondary else None),
        provenance=provenance)
    (out / 'summary.json').write_text(json.dumps(summary, indent=1))
    ref = summary['h1'][REF]['sa_same_detector']
    print(f"H1 at θ_ref {THETA_REF}: mean SA = {ref['point']:+.4f} IDF1, 95% CI {ref['ci95']}")


if __name__ == '__main__':
    main()
