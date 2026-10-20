"""
code/seedbias/protocols.py
──────────────────────────
Seeds for the H3 protocols (PROTOCOL.md A4 item 4 as amended by A6).

union_seed: outputs merged in the given order; a later system's box is
dropped where it matches (Hungarian, IoU >= 0.5) a box already in the union;
ids are kept apart per system; geometry unchanged. (Under a shared detector
this reduces to the first system's output, so A6 does not run it as a
protocol; it is still used to de-duplicate candidate boxes.)

consensus_seed (P2): boxes all systems agree on (chained matches to the first
system's boxes), with mean geometry. A consensus box is linked to the
earliest later consensus box within MAX_GAP frames on which a majority of
systems keep the same id. Returns (seed, candidates): candidates are the
other systems' boxes, de-duplicated across systems, with per-system ids.
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
    outputs = [np.asarray(o, dtype=float).reshape(-1, 6) for o in outputs]
    m = len(outputs)
    majority = m // 2 + 1
    base = outputs[0]
    members = [np.arange(len(base))]          # per system: matched row for each base row (-1 if none)
    for out in outputs[1:]:
        hit = match(out, base) if len(out) and len(base) else np.full(len(out), -1)
        row = np.full(len(base), -1)
        row[hit[hit >= 0]] = np.flatnonzero(hit >= 0)
        members.append(row)
    members = np.stack(members)               # [system, base row]
    cols = np.flatnonzero((members >= 0).all(0))
    in_consensus = [set(members[s, cols].tolist()) for s in range(m)]
    rest = [o[[r for r in range(len(o)) if r not in in_consensus[s]]] for s, o in enumerate(outputs)]
    candidates = union_seed(rest)
    if not len(cols):
        return np.empty((0, 6)), candidates

    frames = base[cols, 0]
    boxes = np.mean([outputs[s][members[s, cols], 2:6] for s in range(m)], axis=0)
    sys_ids = np.stack([outputs[s][members[s, cols], 1] for s in range(m)])   # [system, consensus box]
    order = np.argsort(frames, kind='stable')
    # per system and id: consensus boxes in frame order, to find each box's next box with that id
    nxt = np.full((m, len(cols)), -1)
    for s in range(m):
        last = {}
        for i in order[::-1]:
            key = sys_ids[s, i]
            nxt[s, i] = last.get(key, -1)
            last[key] = i
    succ = np.full(len(cols), -1)
    has_pred = np.zeros(len(cols), dtype=bool)
    for i in order:
        votes = {}
        for s in range(m):
            j = nxt[s, i]
            if j >= 0 and frames[j] - frames[i] <= max_gap:
                votes[j] = votes.get(j, 0) + 1
        good = [j for j, v in votes.items() if v >= majority and not has_pred[j]]
        if good:
            j = min(good, key=lambda j: (frames[j], j))
            succ[i], has_pred[j] = j, True
    track = np.full(len(cols), -1)
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
