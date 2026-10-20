"""
code/seedbias/analysis.py
─────────────────────────
Summaries of the experiment arrays (PROTOCOL.md A3, A4, A5): H1 self-seed
advantage, H2 ranking distortion vs the null model, H3 protocol distortion
and cost, and the A5 diagnostics. Dataset-level IDF1 pools IDTP and box
counts over units. Uncertainty comes from the sequence (all classes of a
sequence move together): weight column 0 is the point estimate, then N_BOOT
bootstrap columns, then one leave-one-sequence-out column per sequence.
The reported 95% interval is BCa (A5); the percentile interval and the
leave-one-out range are reported beside it.
"""

from __future__ import annotations

import itertools

import numpy as np
from scipy.stats import norm

N_BOOT = 10_000
DELTA = 0.01            # A5: magnitude threshold for H1 regions, rank flips and the stop rule


def idf1(idtp, ngt, ntr):
    return 2.0 * idtp / np.maximum(ngt + ntr, 1)


def per_group(x: np.ndarray, group_of_unit: np.ndarray) -> np.ndarray:
    """Sum the last (unit) axis into groups (sequences or classes)."""
    return np.stack([x[..., group_of_unit == g].sum(-1) for g in range(group_of_unit.max() + 1)], -1)


def tau_and_flips(x: np.ndarray, y: np.ndarray, margin: float = 0.0):
    """Kendall τ-b between x[..., n] and y[..., n] (broadcast), and the number of discordant pairs
    among the pairs whose x gap exceeds `margin` (A5: flips count only pairs separated by more than δ)."""
    i, j = np.array(list(itertools.combinations(range(x.shape[-1]), 2))).T
    gx, gy = x[..., i] - x[..., j], y[..., i] - y[..., j]
    gx, gy = np.broadcast_arrays(gx, gy)
    sx, sy = np.sign(gx), np.sign(gy)
    c, d = (sx * sy > 0).sum(-1), (sx * sy < 0).sum(-1)
    n0 = len(i)
    n1, n2 = (sx == 0).sum(-1), (sy == 0).sum(-1)
    with np.errstate(invalid='ignore', divide='ignore'):
        tau = (c - d) / np.sqrt((n0 - n1) * (n0 - n2))
    return tau, ((sx * sy < 0) & (np.abs(gx) > margin)).sum(-1)


class Pooled:
    """Dataset-level IDF1 for the point estimate, bootstrap and leave-one-out weight columns.

    weights: optional [groups, W] matrix replacing the default columns (e.g. one-hot columns for
    per-sequence or per-class values); then ci() is not meaningful.
    """

    def __init__(self, res: dict, group_of_unit: np.ndarray, n_boot: int | None = None, weights=None):
        self.g = group_of_unit
        n = group_of_unit.max() + 1
        if weights is None:
            n_boot = N_BOOT if n_boot is None else n_boot
            rng = np.random.default_rng(0)
            boot = rng.multinomial(n, np.full(n, 1 / n), n_boot).T
            jack = 1 - np.eye(n)
            weights = np.hstack([np.ones((n, 1)), boot, jack])
            self.n_boot = n_boot
        self.w = weights
        self.ntr = per_group(res['ntr'], group_of_unit) @ self.w                          # [T, W]
        self.true = idf1(per_group(res['idtp_true'], group_of_unit) @ self.w,
                         per_group(res['ngt_true'], group_of_unit) @ self.w, self.ntr)     # [T, W]

    def sim(self, idtp, ngt):
        """idtp[..., T, U], ngt[..., U] → IDF1[..., T, W]."""
        return idf1(per_group(idtp, self.g) @ self.w, (per_group(ngt, self.g) @ self.w)[..., None, :], self.ntr)

    def ci(self, values_w: np.ndarray) -> dict:
        """values_w[..., W] → point, BCa 95% CI, percentile 95% CI, leave-one-sequence-out range."""
        values_w = np.asarray(values_w, dtype=float)
        point = values_w[..., 0]
        boot = values_w[..., 1:1 + self.n_boot]
        jack = values_w[..., 1 + self.n_boot:]
        pct = np.percentile(boot, [2.5, 97.5], axis=-1)
        return dict(point=point.tolist(), ci95=[b.tolist() for b in _bca(point, boot, jack)],
                    ci95_percentile=[p.tolist() for p in pct],
                    loo_range=[jack.min(-1).tolist(), jack.max(-1).tolist()])


def _bca(point, boot, jack):
    """Bias-corrected and accelerated interval (Efron 1987), acceleration from the jackknife."""
    point = np.asarray(point, dtype=float)
    b = boot.shape[-1]
    if np.all(boot == point[..., None]):
        return point, point
    tol = 1e-12 * np.maximum(1.0, np.abs(point))[..., None]       # same value up to summation round-off
    prop = (boot < point[..., None] - tol).mean(-1) + 0.5 * (np.abs(boot - point[..., None]) <= tol).mean(-1)
    z0 = norm.ppf(np.clip(prop, 1 / (b + 1), b / (b + 1)))
    dev = jack.mean(-1, keepdims=True) - jack
    den = 6 * ((dev ** 2).sum(-1)) ** 1.5
    a = np.divide((dev ** 3).sum(-1), den, out=np.zeros_like(den), where=den > 0)
    srt = np.sort(boot, axis=-1)
    bounds = []
    for z in norm.ppf([0.025, 0.975]):
        alpha = norm.cdf(z0 + (z0 + z) / (1 - a * (z0 + z)))
        pos = np.clip(alpha * (b - 1), 0, b - 1)                      # linear interpolation, as np.percentile
        lo_i = np.floor(pos).astype(int)
        hi_i = np.minimum(lo_i + 1, b - 1)
        lo_v = np.take_along_axis(srt, np.asarray(lo_i)[..., None], -1)[..., 0]
        hi_v = np.take_along_axis(srt, np.asarray(hi_i)[..., None], -1)[..., 0]
        bounds.append(lo_v + (pos - lo_i) * (hi_v - lo_v))
    return bounds[0], bounds[1]


def sa_matrix(res, pooled: Pooled, c, seed_sys, per_seed=False):
    """SA[A, T, W] for grid cell c, averaged over rng seeds (or SA[A, k, T, W] with per_seed);
    T runs over all evaluated systems."""
    sim = pooled.sim(res['idtp'][:, c], res['ngt'][:, c])                              # [A, k, T, W]
    own = sim[np.arange(len(seed_sys)), :, seed_sys]                                    # [A, k, W]
    sa = (own[:, :, None] - sim) - (pooled.true[seed_sys][:, None, None] - pooled.true[None, None])
    return sa if per_seed else sa.mean(1)


def _pair_masks(seed_sys, x_sys, n_sys, n_t, exclude=()):
    same = np.array([[t in x_sys and t != seed_sys[a] and t not in exclude and seed_sys[a] not in exclude
                      for t in range(n_t)] for a in range(len(seed_sys))])
    other = np.array([[t in n_sys for t in range(n_t)] for a in range(len(seed_sys))])
    return same, other


def h1(res, pooled: Pooled, seed_sys, x_sys, n_sys, cells) -> list:
    """Per cell: mean SA over same-detector ordered pairs (endpoint) and over seed→other-detector pairs,
    with the A5 region flags (BCa lower bound > 0 and > δ)."""
    out = []
    for c in range(len(cells)):
        sa_k = sa_matrix(res, pooled, c, seed_sys, per_seed=True)                       # [A, k, T, W]
        sa = sa_k.mean(1)
        same, other = _pair_masks(seed_sys, x_sys, n_sys, sa.shape[1])
        s = pooled.ci(sa[same].mean(0))
        out.append(dict(cell=cells[c], sa_same_detector=s, above_zero=s['ci95'][0] > 0,
                        above_delta=s['ci95'][0] > DELTA,
                        sa_sd_over_seeds=float(sa_k[..., 0].transpose(0, 2, 1)[same].mean(0).std()),
                        sa_other_detector=pooled.ci(sa[other].mean(0)) if other.any() else None,
                        sa_pairs=sa[..., 0].tolist()))
    return out


def h1_diagnostics(res, seq_of_unit, class_of_unit, seed_sys, x_sys, n_sys, ref, ref_a0, exclude) -> dict:
    """A5 diagnostics at θ_ref: per-sequence and per-class SA, SA without SORT, and the geometry
    contrast (a = 1 vs a = 0) for same- and cross-detector pairs."""
    n_t = res['idtp'].shape[3]
    same, other = _pair_masks(seed_sys, x_sys, n_sys, n_t)
    same_x, _ = _pair_masks(seed_sys, x_sys, n_sys, n_t, exclude)
    out = {}
    for name, group in (('per_sequence', seq_of_unit), ('per_class', class_of_unit)):
        view = Pooled(res, group, weights=np.eye(group.max() + 1))
        sa = sa_matrix(res, view, ref, seed_sys)                                        # [A, T, G]
        out[name] = sa[same].mean(0).tolist()
    out['per_sequence_unweighted_mean'] = float(np.mean(out['per_sequence']))
    point = Pooled(res, seq_of_unit, weights=np.ones((seq_of_unit.max() + 1, 1)))
    sa1, sa0 = sa_matrix(res, point, ref, seed_sys)[..., 0], sa_matrix(res, point, ref_a0, seed_sys)[..., 0]
    out['sa_without_excluded'] = float(sa1[same_x].mean()) if same_x.any() else None
    out['geometry_same_detector'] = dict(a1=float(sa1[same].mean()), a0=float(sa0[same].mean()))
    if other.any():
        out['geometry_other_detector'] = dict(a1=float(sa1[other].mean()), a0=float(sa0[other].mean()))
    return out


def ranking(res, pooled: Pooled, cells) -> list:
    """Per cell (point estimates): Kendall τ-b, raw flips and δ-margin flips, GT_A vs GT_true, over (A, k)."""
    true = pooled.true[:, 0]
    out = []
    for c in range(len(cells)):
        sim = pooled.sim(res['idtp'][:, c], res['ngt'][:, c])[..., 0]                   # [A, k, T]
        tau, flips = tau_and_flips(true, sim)
        _, flips_d = tau_and_flips(true, sim, DELTA)
        out.append(dict(cell=cells[c], tau_mean=float(np.nanmean(tau)), flips_mean=float(flips.mean()),
                        flips_delta_mean=float(flips_d.mean()), flips_delta_any=float((flips_d > 0).mean())))
    return out


def h2(res, pooled: Pooled, cells_a0, cells_a1, slice_thetas, ref_pos, seed_names) -> list:
    """H2 per slice position j (A4 item 3, A6 item 1): τ and δ-margin flips for seed-correlated vs null
    errors, paired by (A, k). The endpoint uses the a = 0 cells (structure vs structure); the a = 1
    difference is reported as structure plus geometry. Skipped null error boxes are reported as shares."""
    true = pooled.true.T[None, None]                                                    # [1, 1, W, T]
    out = []
    for j, theta in enumerate(slice_thetas):
        null = pooled.sim(res['null_idtp'][:, j], res['null_ngt'][:, j])
        t_null, f_null = tau_and_flips(true, np.moveaxis(null, -1, -2), DELTA)           # [A, k, W]
        row = dict(cell=theta, is_ref=j == ref_pos, tau_null=float(np.nanmean(t_null[..., 0])))
        for tag, c in (('a0', cells_a0[j]), ('a1', cells_a1[j])):
            sim = pooled.sim(res['idtp'][:, c], res['ngt'][:, c])                       # [A, k, T, W]
            t_seed, f_seed = tau_and_flips(true, np.moveaxis(sim, -1, -2), DELTA)
            row[tag] = dict(tau_null_minus_seed=pooled.ci(np.nanmean(t_null - t_seed, axis=(0, 1))),
                            flips_seed_minus_null=pooled.ci((f_seed - f_null).mean(axis=(0, 1))),
                            tau_seed=float(np.nanmean(t_seed[..., 0])),
                            per_seed={seed_names[a]: dict(tau_seed=float(np.nanmean(t_seed[a, :, 0])),
                                                          tau_null=float(np.nanmean(t_null[a, :, 0])),
                                                          flips_seed=float(f_seed[a, :, 0].mean()),
                                                          flips_null=float(f_null[a, :, 0].mean()))
                                      for a in range(len(seed_names))})
        req = res['null_req'][:, j].sum(axis=(0, 1, 3))
        skip = res['null_skip'][:, j].sum(axis=(0, 1, 3))
        row['null_skip_share'] = dict(zip(('fn', 'id', 'fp'), (skip / np.maximum(req, 1)).tolist()))
        row['null_skip_over_1pct'] = bool((skip / np.maximum(req, 1) > 0.01).any())
        out.append(row)
    return out


def distortion(sim_x, true_x):
    """Mean |pairwise difference error| over ordered pairs; sim_x[..., T, W], true_x[T, W] → [..., W]."""
    d = (sim_x[..., :, None, :] - sim_x[..., None, :, :]) - (true_x[:, None] - true_x[None, :])
    off = ~np.eye(true_x.shape[0], dtype=bool)
    return np.abs(d[..., off, :]).mean(-2)


def _member_sa(sim, true, members, others):
    """Mean over members A and non-members B of [M(A) − M(B)]_P − [..]_true; sim[k, T, W] → [W]."""
    vals = [((sim[:, a] - sim[:, b]) - (true[a] - true[b])).mean(0) for a in members for b in others]
    return np.mean(vals, axis=0)


def h3(res, pooled: Pooled, seed_sys, n_sys, systems, protocols, slice_thetas, ref_pos, ngt_total) -> dict:
    """H3 (A4 item 4 as amended by A6): distortion D on the seed systems and on all systems, the paired
    difference D_P − D_P0 (same bootstrap columns), member SA against systems outside the protocol,
    the bracket per system, and a two-part cost (boxes verified, boxes drawn) relative to GT_true."""
    all_sys = list(range(len(systems)))
    curves = {}
    for j, theta in enumerate(slice_thetas):
        c = theta['index']
        sim_p0 = pooled.sim(res['idtp'][:, c], res['ngt'][:, c])                        # [A, k, T, W]
        d0_x = distortion(sim_p0[:, :, seed_sys], pooled.true[seed_sys]).mean((0, 1))
        d0_all = distortion(sim_p0, pooled.true).mean((0, 1))
        rows = {'P0 single seed': dict(
            D_seed_systems=pooled.ci(d0_x), D_all_systems=pooled.ci(d0_all),
            cost_verify=float(res['ntr'][seed_sys].sum() / len(seed_sys) / ngt_total),
            cost_drawn=float(res['drawn'][:, j].sum(-1).mean() / ngt_total))}
        for p, proto in enumerate(protocols):
            sim = pooled.sim(res['proto_idtp'][p, j], res['proto_ngt'][p, j])           # [k, T, W]
            dx = distortion(sim[:, seed_sys], pooled.true[seed_sys]).mean(0)
            dall = distortion(sim, pooled.true).mean(0)
            members = [systems.index(m) for m in proto['members']]
            entry = dict(D_seed_systems=pooled.ci(dx), D_all_systems=pooled.ci(dall),
                         D_minus_P0_seed_systems=pooled.ci(dx - d0_x), D_minus_P0_all_systems=pooled.ci(dall - d0_all),
                         member_sa_vs_other_detector=pooled.ci(_member_sa(sim, pooled.true, members, n_sys)),
                         cost_verify=float(res['proto_verify'][p].sum() / ngt_total),
                         cost_drawn=float(res['proto_drawn'][p, j].sum(-1).mean() / ngt_total))
            if proto['held_out']:
                entry['member_sa_vs_held_out'] = pooled.ci(
                    _member_sa(sim, pooled.true, members, [systems.index(proto['held_out'])]))
            rows[proto['name']] = entry
        if j == ref_pos:
            p0x = sim_p0[:, :, seed_sys]
            lo, hi = p0x.min(0), p0x.max(0)                                              # [k, T, W]
            true_x = pooled.true[seed_sys][None]                                         # [1, T, W]
            covered = ((lo <= true_x) & (true_x <= hi)).mean(0)                          # [T, W]
            rows['P3 bracket'] = dict(
                width=pooled.ci((hi - lo).mean((0, 1))),
                coverage_per_system={systems[t]: pooled.ci(covered[i]) for i, t in enumerate(seed_sys)},
                cost_verify=float(res['ntr'][seed_sys].sum() / ngt_total),
                cost_drawn=float(res['drawn'][:, j].sum() / res['drawn'].shape[2] / ngt_total))
        curves[str(theta['theta'])] = rows
    return curves
