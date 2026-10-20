"""
code/seedbias/analysis.py
─────────────────────────
Summaries of the experiment arrays (PROTOCOL.md A3, A4): H1 self-seed
advantage, H2 ranking distortion vs the null model, H3 protocol distortion
and cost. All dataset-level IDF1 values pool IDTP and box counts over units;
CIs are percentiles of a sequence bootstrap (all classes of a sequence move
together). Weight row 0 is the point estimate.
"""

from __future__ import annotations

import itertools

import numpy as np

N_BOOT = 10_000


def idf1(idtp, ngt, ntr):
    return 2.0 * idtp / np.maximum(ngt + ntr, 1)


def boot_weights(n_seq: int, n_boot: int = N_BOOT, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return np.vstack([np.ones(n_seq), rng.multinomial(n_seq, np.full(n_seq, 1 / n_seq), n_boot)]).T  # [S, W]


def per_seq(x: np.ndarray, seq_of_unit: np.ndarray) -> np.ndarray:
    """Sum the last (unit) axis into sequences."""
    return np.stack([x[..., seq_of_unit == s].sum(-1) for s in range(seq_of_unit.max() + 1)], -1)


def ci(values_w: np.ndarray) -> dict:
    """values_w[..., W] → point (row 0) and 95% percentile CI over rows 1..W."""
    lo, hi = np.percentile(values_w[..., 1:], [2.5, 97.5], axis=-1)
    return dict(point=values_w[..., 0].tolist(), ci95=[lo.tolist(), hi.tolist()])


def tau_and_flips(x: np.ndarray, y: np.ndarray):
    """Kendall τ-b between x[..., n] and y[..., n] (broadcast), and the number of discordant pairs."""
    i, j = np.array(list(itertools.combinations(range(x.shape[-1]), 2))).T
    sx, sy = np.sign(x[..., i] - x[..., j]), np.sign(y[..., i] - y[..., j])
    sx, sy = np.broadcast_arrays(sx, sy)
    c, d = (sx * sy > 0).sum(-1), (sx * sy < 0).sum(-1)
    n0 = len(i)
    n1, n2 = (sx == 0).sum(-1), (sy == 0).sum(-1)
    with np.errstate(invalid='ignore', divide='ignore'):
        tau = (c - d) / np.sqrt((n0 - n1) * (n0 - n2))
    return tau, d


class Pooled:
    """Bootstrap-weighted dataset-level IDF1 from per-unit arrays."""

    def __init__(self, res: dict, seq_of_unit: np.ndarray, n_boot: int | None = None):
        self.s = seq_of_unit
        self.w = boot_weights(seq_of_unit.max() + 1, N_BOOT if n_boot is None else n_boot)
        self.ntr = per_seq(res['ntr'], seq_of_unit) @ self.w                            # [T, W]
        self.true = idf1(per_seq(res['idtp_true'], seq_of_unit) @ self.w,
                         per_seq(res['ngt_true'], seq_of_unit) @ self.w, self.ntr)       # [T, W]

    def sim(self, idtp, ngt):
        """idtp[..., T, U], ngt[..., U] → IDF1[..., T, W]."""
        return idf1(per_seq(idtp, self.s) @ self.w, (per_seq(ngt, self.s) @ self.w)[..., None, :], self.ntr)


def h1(res, pooled: Pooled, seed_sys, x_sys, n_sys, cells) -> list:
    """Per cell: mean SA over same-detector ordered pairs (endpoint) and over seed→other-detector pairs."""
    out = []
    for c in range(len(cells)):
        sim = pooled.sim(res['idtp'][:, c], res['ngt'][:, c])                          # [A, k, T, W]
        own = sim[np.arange(len(seed_sys)), :, seed_sys]                                # [A, k, W]
        sa = (own[:, :, None] - sim) - (pooled.true[seed_sys][:, None, None] - pooled.true[None, None])
        sa = sa.mean(1)                                                                 # [A, T, W]
        same = np.array([[t in x_sys and t != seed_sys[a] for t in range(sa.shape[1])] for a in range(len(seed_sys))])
        other = np.array([[t in n_sys for t in range(sa.shape[1])] for a in range(len(seed_sys))])
        out.append(dict(cell=cells[c], sa_same_detector=ci(sa[same].mean(0)),
                        sa_other_detector=ci(sa[other].mean(0)) if other.any() else None,
                        sa_pairs=sa[..., 0].tolist()))
    return out


def ranking(res, pooled: Pooled, cells) -> list:
    """Per cell (point estimates): Kendall τ-b and flips of all systems, GT_A vs GT_true, over (A, k)."""
    true = pooled.true[:, 0]
    out = []
    for c in range(len(cells)):
        sim = pooled.sim(res['idtp'][:, c], res['ngt'][:, c])[..., 0]                   # [A, k, T]
        tau, flips = tau_and_flips(true, sim)
        out.append(dict(cell=cells[c], tau_mean=float(np.nanmean(tau)), flips_mean=float(flips.mean()),
                        flips_any=float((flips > 0).mean())))
    return out


def h2(res, pooled: Pooled, slice_cells, ref_pos) -> list:
    """Per slice cell: τ and flips for seed-correlated vs null errors, paired by (A, k), with CIs."""
    out = []
    for j, cell in enumerate(slice_cells):
        c = cell['index']
        sim = pooled.sim(res['idtp'][:, c], res['ngt'][:, c])                           # [A, k, T, W]
        null = pooled.sim(res['null_idtp'][:, j], res['null_ngt'][:, j])
        true = pooled.true.T[None, None]                                                # [1, 1, W, T]
        t_seed, f_seed = tau_and_flips(true, np.moveaxis(sim, -1, -2))                   # [A, k, W]
        t_null, f_null = tau_and_flips(true, np.moveaxis(null, -1, -2))
        out.append(dict(cell=cell['theta'], is_ref=j == ref_pos,
                        tau_null_minus_seed=ci(np.nanmean(t_null - t_seed, axis=(0, 1))),
                        flips_seed_minus_null=ci((f_seed - f_null).mean(axis=(0, 1))),
                        tau_seed=float(np.nanmean(t_seed[..., 0])), tau_null=float(np.nanmean(t_null[..., 0])),
                        null_skipped=int(res['null_skipped'][:, j].sum())))
    return out


def distortion(sim_x, true_x):
    """Mean |pairwise difference error| over ordered pairs; sim_x[..., T, W], true_x[T, W] → [..., W]."""
    d = (sim_x[..., :, None, :] - sim_x[..., None, :, :]) - (true_x[:, None] - true_x[None, :])
    off = ~np.eye(true_x.shape[0], dtype=bool)
    return np.abs(d[..., off, :]).mean(-2)


def h3(res, pooled: Pooled, seed_sys, seed_names, protocols, slice_cells, ref_pos, ngt_total) -> dict:
    """Distortion D (A4 item 4) and review cost for P0 (single seeds), P1/P2 (protocol runs), P3 (bracket)."""
    true_x = pooled.true[seed_sys]
    curves = {}
    for j, cell in enumerate(slice_cells):
        c = cell['index']
        sim_p0 = pooled.sim(res['idtp'][:, c], res['ngt'][:, c])[:, :, seed_sys]      # [A, k, T, W]
        rows = {'P0 single seed': dict(D=ci(distortion(sim_p0, true_x).mean((0, 1))),
                                       cost=float(res['ntr'][seed_sys].sum() / len(seed_sys) / ngt_total))}
        for p, proto in enumerate(protocols):
            sim = pooled.sim(res['proto_idtp'][p, j], res['proto_ngt'][p, j])[:, seed_sys]  # [k, T, W]
            entry = dict(D=ci(distortion(sim, true_x).mean(0)), cost=float(res['proto_cost'][p].sum() / ngt_total))
            members = [seed_names.index(m) for m in proto['members']] if proto['kind'] == 'union' else []
            outside = [t for t in range(len(seed_sys)) if t not in members]
            if members and outside:
                adv = [((sim[:, a] - sim[:, b]) - (true_x[a] - true_x[b])).mean(0) for a in members for b in outside]
                entry['member_sa'] = ci(np.mean(adv, axis=0))
            rows[proto['name']] = entry
        if j == ref_pos:
            lo, hi = sim_p0.min(0), sim_p0.max(0)                                        # [k, T, W] over seeds A
            covered = (lo[..., 0] <= true_x[None, :, 0]) & (true_x[None, :, 0] <= hi[..., 0])
            rows['P3 bracket'] = dict(width=ci((hi - lo).mean((0, 1))), coverage=float(covered.mean()),
                                      cost=float(res['ntr'][seed_sys].sum() / ngt_total))
        curves[str(cell['theta'])] = rows
    return curves
