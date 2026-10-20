"""
code/seedbias/null_model.py
───────────────────────────
H2 null model (PROTOCOL.md A4 item 3, A6 item 2): the same number and sizes of
errors as one simulated GT_S draw, placed at random on GT_true, independent of
trackers.

null_gt() returns the labels of the kept GT rows (GT geometry; -1 = deleted),
the extra FP rows [frame, label, x1, y1, x2, y2] (time-shifted copies of GT
track segments that overlap no GT_true object in their new frames), and the
number of requested and skipped error boxes per error type.
"""

from __future__ import annotations

import numpy as np

from code.annotation_sim.simulate import iou_matrix

FP_TRIES = 100


def _tracks(gt):
    order = np.lexsort((gt[:, 0], gt[:, 1]))
    ids = gt[order, 1]
    return np.split(order, np.flatnonzero(np.diff(ids)) + 1) if len(order) else []


def null_gt(gt: np.ndarray, n_frames: int, missed_lengths, unfixed_pairs, kept_fp_lengths,
            rng: np.random.Generator):
    """gt: canonical GT rows (prep.gt).

    Returns (labels per GT row, -1 if deleted; extra FP rows; counts) where counts has, per error
    type ('fn', 'id', 'fp'), the requested and the skipped number of error boxes.
    """
    tracks = _tracks(gt)
    order = np.concatenate(tracks) if tracks else np.empty(0, dtype=int)     # rows, track by track
    track_of = np.repeat(np.arange(len(tracks)), [len(t) for t in tracks])  # track index per position
    pos_in_track = np.concatenate([np.arange(len(t)) for t in tracks]) if tracks else np.empty(0, dtype=int)
    _, labels = np.unique(gt[:, 1], return_inverse=True)
    labels = labels.reshape(-1).astype(int)
    fresh = labels.max() + 1 if len(labels) else 0
    alive = np.ones(len(gt), dtype=bool)
    occupied = {}                                   # label → frames it holds among alive rows
    for row, lab in enumerate(labels):
        occupied.setdefault(int(lab), set()).add(gt[row, 0])
    gt_by_frame = {}
    for row, f in enumerate(gt[:, 0].tolist()):
        gt_by_frame.setdefault(f, []).append(row)
    counts = {k: dict(requested=0, skipped=0) for k in ('fn', 'id', 'fp')}

    def pick(n, usable):
        """Random (track, start) uniformly among windows of n consecutive usable rows of one track."""
        if n <= 0 or n > len(order):
            return None
        c = np.concatenate([[0], np.cumsum(usable[order])])
        ok = (c[n:] - c[:-n] == n) & (track_of[:len(order) - n + 1] == track_of[n - 1:])
        options = np.flatnonzero(ok)
        if not options.size:
            return None
        p = options[rng.integers(options.size)]
        return int(track_of[p]), int(pos_in_track[p])

    def move(rows, new_label):
        for r in rows:
            occupied[int(labels[r])].discard(gt[r, 0])
            if new_label is not None:
                occupied.setdefault(new_label, set()).add(gt[r, 0])
                labels[r] = new_label

    for n in sorted(missed_lengths, reverse=True):                 # largest first: fewer packing failures
        counts['fn']['requested'] += n
        hit = pick(n, alive)
        if hit is None:
            counts['fn']['skipped'] += n
            continue
        t, s = hit
        seg = tracks[t][s:s + n]
        move(seg, None)
        alive[seg] = False

    relabeled = np.zeros(len(gt), dtype=bool)
    for n, merge in sorted(unfixed_pairs, key=lambda p: -p[0]):
        counts['id']['requested'] += n
        hit = pick(n, alive & ~relabeled)
        if hit is None:
            counts['id']['skipped'] += n
            continue
        t, s = hit
        seg = tracks[t][s:s + n]
        relabeled[seg] = True
        target = None
        if merge:
            frames = set(gt[seg, 0].tolist())
            own = int(labels[seg[0]])
            options = sorted(lab for lab, fs in occupied.items() if lab != own and fs and fs.isdisjoint(frames))
            if options:
                target = options[rng.integers(len(options))]
        if target is None:
            target, fresh = fresh, fresh + 1
        move(seg, target)

    extra = []
    every = np.ones(len(gt), dtype=bool)
    for n in sorted(kept_fp_lengths, reverse=True):
        counts['fp']['requested'] += n
        placed = None
        for _ in range(FP_TRIES):
            hit = pick(n, every)
            if hit is None:
                break
            t, s = hit
            seg = tracks[t][s:s + n]
            f0, f1 = gt[seg, 0].min(), gt[seg, 0].max()
            lo, hi = int(1 - f0), int(n_frames - f1)
            if hi - lo < 1:
                continue
            d = int(rng.integers(lo, hi))
            d = d + 1 if d >= 0 else d                          # uniform over [lo, hi] without 0
            rows = gt[seg].copy()
            rows[:, 0] += d
            if not any(len(gt_by_frame.get(f, [])) and
                       (iou_matrix(rows[i:i + 1, 2:6], gt[gt_by_frame[f], 2:6]) >= 0.5).any()
                       for i, f in enumerate(rows[:, 0].tolist())):
                placed = rows
                break
        if placed is None:
            counts['fp']['skipped'] += n
            continue
        placed[:, 1] = fresh
        fresh += 1
        extra.append(placed)

    labels[~alive] = -1
    keep = labels >= 0
    if len(np.unique(np.column_stack([gt[keep, 0], labels[keep]]), axis=0)) != keep.sum():
        raise RuntimeError('null GT has duplicate (frame, label) rows')
    return labels, (np.concatenate(extra) if extra else np.empty((0, 6))), counts
