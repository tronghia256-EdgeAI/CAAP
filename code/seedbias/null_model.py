"""
code/seedbias/null_model.py
───────────────────────────
H2 null model (PROTOCOL.md A4 item 3): the same number and sizes of errors as
one simulated GT_S draw, placed at random on GT_true, independent of trackers.

null_gt() returns the labels of the kept GT rows (GT geometry; -1 = deleted)
and the extra FP rows [frame, label, x1, y1, x2, y2] (time-shifted copies of
GT track segments), which FastIdentity.idtp scores directly.
"""

from __future__ import annotations

import numpy as np


def _tracks(gt):
    order = np.lexsort((gt[:, 0], gt[:, 1]))
    ids = gt[order, 1]
    return np.split(order, np.flatnonzero(np.diff(ids)) + 1) if len(order) else []


def null_gt(gt: np.ndarray, n_frames: int, missed_lengths, unfixed_pairs, kept_fp_lengths,
            rng: np.random.Generator):
    """gt: canonical GT rows (prep.gt). Returns (labels per GT row, -1 if deleted; extra FP rows; skipped count)."""
    tracks = _tracks(gt)
    order = np.concatenate(tracks) if tracks else np.empty(0, dtype=int)     # rows, track by track
    track_of = np.repeat(np.arange(len(tracks)), [len(t) for t in tracks])  # track index per position
    pos_in_track = np.concatenate([np.arange(len(t)) for t in tracks]) if tracks else np.empty(0, dtype=int)
    _, labels = np.unique(gt[:, 1], return_inverse=True)
    labels = labels.reshape(-1).astype(int)
    fresh = labels.max() + 1 if len(labels) else 0
    alive = np.ones(len(gt), dtype=bool)
    skipped = 0

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

    for n in missed_lengths:
        hit = pick(n, alive)
        if hit is None:
            skipped += 1
            continue
        t, s = hit
        alive[tracks[t][s:s + n]] = False

    relabeled = np.zeros(len(gt), dtype=bool)
    for n, merge in unfixed_pairs:
        hit = pick(n, alive & ~relabeled)
        if hit is None:
            skipped += 1
            continue
        t, s = hit
        seg = tracks[t][s:s + n]
        relabeled[seg] = True
        target = None
        if merge:
            frames = set(gt[seg, 0].tolist())
            others = [u for u, rows in enumerate(tracks)
                      if u != t and frames.isdisjoint(gt[rows[alive[rows]], 0].tolist())]
            if others:
                target = int(labels[tracks[others[rng.integers(len(others))]][0]])
        if target is None:
            target, fresh = fresh, fresh + 1
        labels[seg] = target

    extra = []
    for n in kept_fp_lengths:
        hit = pick(n, np.ones(len(gt), dtype=bool))
        if hit is None:
            skipped += 1
            continue
        t, s = hit
        seg = tracks[t][s:s + n]
        f0, f1 = gt[seg, 0].min(), gt[seg, 0].max()
        shifts = [d for d in range(int(1 - f0), int(n_frames - f1) + 1) if d != 0]
        if not shifts:
            skipped += 1
            continue
        d = shifts[rng.integers(len(shifts))]
        rows = gt[seg].copy()
        rows[:, 0] += d
        rows[:, 1] = fresh
        fresh += 1
        extra.append(rows)

    labels[~alive] = -1
    return labels, (np.concatenate(extra) if extra else np.empty((0, 6))), skipped
