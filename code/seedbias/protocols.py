"""
code/seedbias/protocols.py
──────────────────────────
Seeds for the H3 protocols (PROTOCOL.md A4 item 4 as amended by A6).

union_seed: outputs merged in the given order; a later system's box is
dropped where it matches (Hungarian, IoU >= 0.5) a box already in the union;
ids are kept apart per system; geometry unchanged. (Under a shared detector
this reduces to the first system's output, so A6 does not run it as a
protocol; it is still used to de-duplicate candidate boxes.)

consensus_seed (P2, A7): boxes are clustered across systems frame by frame
(IoU >= 0.5); a cluster supported by a majority of systems is a consensus box
with mean geometry. Each system that has a consensus box votes for its next
consensus box with the same id within MAX_GAP frames; the box with the most
votes is linked when it has at least 2 votes and a strict plurality (systems
that lose the id do not vote against). Returns (seed, candidates): candidates
are the clusters without majority support, one box per cluster.
"""

from __future__ import annotations

import numpy as np

from code.annotation_sim.simulate import match

MAX_GAP = 30


def union_seed(outputs: list) -> np.ndarray:
    union = np.empty((0, 6))
    offset = 0
    for out in outputs:
        out = np.asarray(out, dtype=float).reshape(-1, 6)
        ids, inv = np.unique(out[:, 1], return_inverse=True)
        out = out.copy()
        out[:, 1] = inv.reshape(-1) + offset
        offset += len(ids)
        if len(union) and len(out):
            out = out[match(out, union) < 0]
        union = np.concatenate([union, out])
    return union


def consensus_seed(outputs: list, max_gap: int = MAX_GAP):
    """P2 seed (A7): majority coverage, plurality id links. Returns (seed, candidates)."""
    outputs = [np.asarray(o, dtype=float).reshape(-1, 6) for o in outputs]
    m = len(outputs)
    majority = m // 2 + 1
    # Cluster boxes across systems frame by frame: each system's boxes are matched (Hungarian,
    # IoU >= 0.5) to the clusters built so far; unmatched boxes open new clusters.
    clusters = np.empty((0, 6))                  # [frame, cluster id, box of the first system that opened it]
    support = []                                 # per cluster: {system: row}
    for s_idx, out in enumerate(outputs):
        hit = match(out, clusters) if len(out) and len(clusters) else np.full(len(out), -1)
        for row in np.flatnonzero(hit >= 0):
            support[hit[row]][s_idx] = row
        new = np.flatnonzero(hit < 0)
        if new.size:
            add = out[new].copy()
            add[:, 1] = np.arange(len(clusters), len(clusters) + new.size)
            clusters = np.concatenate([clusters, add])
            support += [{s_idx: row} for row in new]
    agreed = np.array([len(sp) >= majority for sp in support], dtype=bool)
    mean_box = lambda sp: np.mean([outputs[s][r, 2:6] for s, r in sp.items()], axis=0)
    cand_idx = np.flatnonzero(~agreed)
    if cand_idx.size:
        # candidates keep a per-system id so frame-contiguous runs of one system form FP runs
        candidates = np.array([[clusters[c, 0], 1e6 * min(support[c]) + outputs[min(support[c])][support[c][min(support[c])], 1],
                                *mean_box(support[c])] for c in cand_idx])
        _, inv = np.unique(candidates[:, 1], return_inverse=True)
        candidates[:, 1] = inv.reshape(-1)
    else:
        candidates = np.empty((0, 6))
    cols = np.flatnonzero(agreed)
    if not cols.size:
        return np.empty((0, 6)), candidates

    frames = clusters[cols, 0]
    boxes = np.array([mean_box(support[c]) for c in cols])
    sys_ids = np.full((m, cols.size), np.nan)    # system id on each consensus box (nan: system absent)
    for i, c in enumerate(cols):
        for s_idx, r in support[c].items():
            sys_ids[s_idx, i] = outputs[s_idx][r, 1]
    order = np.argsort(frames, kind='stable')
    nxt = np.full((m, cols.size), -1)
    for s_idx in range(m):
        last = {}
        for i in order[::-1]:
            key = sys_ids[s_idx, i]
            if np.isnan(key):
                continue
            nxt[s_idx, i] = last.get(key, -1)
            last[key] = i
    succ = np.full(cols.size, -1)
    has_pred = np.zeros(cols.size, dtype=bool)
    for i in order:
        votes = {}
        for s_idx in range(m):
            j = nxt[s_idx, i]
            if j >= 0 and frames[j] - frames[i] <= max_gap:
                votes[j] = votes.get(j, 0) + 1
        if not votes:
            continue
        ranked = sorted(votes.items(), key=lambda kv: (-kv[1], frames[kv[0]], kv[0]))
        j, v = ranked[0]
        plurality = len(ranked) == 1 or v > ranked[1][1]
        if v >= 2 and plurality and not has_pred[j]:
            succ[i], has_pred[j] = j, True
    track = np.full(cols.size, -1)
    n_tracks = 0
    for i in order:
        if not has_pred[i]:
            j = i
            while j >= 0:
                track[j] = n_tracks
                j = succ[j]
            n_tracks += 1
    seed = np.column_stack([frames, track + 1, boxes])
    return seed, candidates
