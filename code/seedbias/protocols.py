"""
code/seedbias/protocols.py
──────────────────────────
Seeds for the H3 de-biasing protocols (PROTOCOL.md A4 item 4).

union_seed: outputs merged in the given order; a later system's box is
dropped where it matches (Hungarian, IoU >= 0.5) a box already in the union;
ids are kept apart per system; geometry unchanged.

consensus_seed: boxes all systems agree on (chained matches to the first
system's boxes), with mean geometry; two consensus boxes in consecutive
frames are linked iff every system keeps the same id across them.
Returns (seed, n_candidates): n_candidates = boxes of any system that are not
part of a consensus box (shown to the reviewer as anonymous candidates).
"""

from __future__ import annotations

import numpy as np

from code.annotation_sim.simulate import match


def union_seed(outputs: list) -> np.ndarray:
    union = np.empty((0, 6))
    offset = 0
    for out in outputs:
        out = np.asarray(out, dtype=float).reshape(-1, 6)
        ids, inv = np.unique(out[:, 1], return_inverse=True)
        out = out.copy()
        out[:, 1] = inv.reshape(-1) + offset
        offset += len(ids)
        if len(union):
            out = out[match(out, union) < 0]
        union = np.concatenate([union, out])
    return union


def consensus_seed(outputs: list):
    outputs = [np.asarray(o, dtype=float).reshape(-1, 6) for o in outputs]
    base = outputs[0]
    members = [np.arange(len(base))]          # per system: matched row for each base row (-1 if none)
    for out in outputs[1:]:
        m = match(out, base)
        row = np.full(len(base), -1)
        row[m[m >= 0]] = np.flatnonzero(m >= 0)
        members.append(row)
    members = np.stack(members)               # [system, base row]
    agreed = (members >= 0).all(0)
    cols = np.flatnonzero(agreed)
    boxes = np.mean([outputs[s][members[s, cols], 2:6] for s in range(len(outputs))], axis=0)
    frames = base[cols, 0]
    sys_ids = np.stack([outputs[s][members[s, cols], 1] for s in range(len(outputs))])   # [system, consensus box]

    # Link consecutive-frame consensus boxes whose system ids all agree; a link is unique per box,
    # because each system id appears at most once per frame.
    key = {(f, *sys_ids[:, i].tolist()): i for i, f in enumerate(frames.tolist())}
    parent = list(range(len(cols)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, f in enumerate(frames.tolist()):
        j = key.get((f + 1, *sys_ids[:, i].tolist()))
        if j is not None:
            parent[find(j)] = find(i)
    if not len(cols):
        return np.empty((0, 6)), sum(len(o) for o in outputs)
    _, ids = np.unique([find(i) for i in range(len(cols))], return_inverse=True)
    seed = np.column_stack([frames, ids.reshape(-1) + 1, boxes])
    n_in_consensus = len(cols) * len(outputs)
    n_candidates = sum(len(o) for o in outputs) - n_in_consensus
    return seed, n_candidates
