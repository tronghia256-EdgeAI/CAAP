"""
code/seedbias/experiment.py
───────────────────────────
Run the θ grid of PROTOCOL.md (section 4, A1, A3) on preprocessed tracks and
summarise H1 (self-seed advantage) and the ranking part of H2.

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
import json
import subprocess
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import scipy.optimize
import scipy.sparse
import scipy.sparse.csgraph
import scipy.stats

from code.annotation_sim.simulate import Reviewer, prepare, read_mot, simulate
from code.seedbias import data as D
from code.seedbias.evaluate import _BaseDataset

GRID = dict(r=(0, 0.25, 0.5, 0.75, 0.9, 1), p_fp=(0, 0.1, 0.25, 0.5), q=(0, 0.5, 0.9, 1), a=(1, 0))
THETA_REF = dict(r=0.75, p_fp=0.1, q=0.5, a=1)
N_SEEDS = 10
N_BOOT = 10_000
CELLS = [dict(zip(GRID, v)) for v in itertools.product(*GRID.values())]
REF = CELLS.index(THETA_REF)


@dataclass
class Unit:
    seq: str
    cls: str
    n_frames: int
    gt: np.ndarray
    tracks: dict            # tracker → [frame, id, x1, y1, x2, y2]


def load_units(tracks_root: Path, dataset: str, detector: str, trackers) -> list:
    units = []
    for seq_dir in sorted((tracks_root / dataset / 'gt').iterdir()):
        info = tracks_root / dataset / detector / seq_dir.name
        n_frames = json.loads((seq_dir / 'seqinfo.json').read_text())['n_frames']
        for cls in D.SPEC[dataset]['classes']:
            units.append(Unit(seq_dir.name, cls, n_frames, read_mot(seq_dir / f'{cls}.txt'),
                              {t: read_mot(info / cls / f'{t}.txt') for t in trackers}))
    return units


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
        self.n_tr = {t: len(x) for t, x in unit.tracks.items()}
        self.tid = {t: np.unique(x[:, 1], return_inverse=True)[1].reshape(-1) for t, x in unit.tracks.items()}
        self.to_gt = {t: iou_pairs(x, gt_rows) for t, x in unit.tracks.items()}
        self.to_seed = ({t: iou_pairs(x, seed_rows) for t, x in unit.tracks.items()}
                        if seed_rows is not None else None)
        self.n_gt_rows = len(gt_rows)
        self.n_seed_rows = 0 if seed_rows is None else len(seed_rows)

    def idtp(self, labels: np.ndarray, origin: np.ndarray) -> dict:
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
            lab, trk = np.concatenate(lab), np.concatenate(trk)
            keep = lab >= 0
            out[t] = max_matching(lab[keep], trk[keep])
        return out


def _run_seed(args):
    """All cells × rng seeds for one seed tracker: idtp[cell, k, tracker, unit], ngt[cell, k, unit]."""
    tracks_root, dataset, detector, trackers, a_idx = args
    units = load_units(Path(tracks_root), dataset, detector, trackers)
    seed_name = trackers[a_idx]
    idtp = np.zeros((len(CELLS), N_SEEDS, len(trackers), len(units)), dtype=np.int64)
    ngt = np.zeros((len(CELLS), N_SEEDS, len(units)), dtype=np.int64)
    episodes = np.zeros((len(units), 2), dtype=np.int64)       # episodes, error pairs (diagnostic)
    for u, unit in enumerate(units):
        prep = prepare(unit.tracks[seed_name], unit.gt)
        episodes[u] = prep.n_episodes, prep.stats['error_pairs']
        fast = FastIdentity(unit, prep.gt, prep.seed)
        for k in range(N_SEEDS):
            for c, cell in enumerate(CELLS):
                rng = np.random.default_rng([k, a_idx, u])    # common random numbers across cells
                out, _, origin = simulate(prep, Reviewer(**cell), rng, with_origin=True)
                ngt[c, k, u] = len(out)
                res = fast.idtp(out[:, 1].astype(int), origin)
                idtp[c, k, :, u] = [res[t] for t in trackers]
    return idtp, ngt, episodes


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


def idf1(idtp, ngt, ntr):
    return 2.0 * idtp / np.maximum(ngt + ntr, 1)


def analyse(res: dict, seq_of_unit: np.ndarray, trackers, rng_seed: int = 0) -> dict:
    """SA (H1) with sequence bootstrap; Kendall τ and flips (H2 ranking part)."""
    n_seq = seq_of_unit.max() + 1
    agg = lambda x: np.stack([x[..., seq_of_unit == s].sum(-1) for s in range(n_seq)], -1)  # units → seqs
    idtp_s, ngt_s = agg(res['idtp']), agg(res['ngt'])             # [A, cell, k, T, S], [A, cell, k, S]
    true_s, ngt_true_s, ntr_s = agg(res['idtp_true']), agg(res['ngt_true']), agg(res['ntr'])
    n_t = len(trackers)
    rng = np.random.default_rng(rng_seed)
    weights = np.vstack([np.ones(n_seq), rng.multinomial(n_seq, np.full(n_seq, 1 / n_seq), N_BOOT)])  # row 0 = point

    def sa_all(cell):
        """SA[w, A, B] averaged over rng seeds, for every bootstrap weight row w."""
        s_true = idf1(true_s @ weights.T, ngt_true_s @ weights.T, ntr_s @ weights.T)    # [T, W]
        sim = idf1(idtp_s[:, cell] @ weights.T,                                         # [A, k, T, W]
                   (ngt_s[:, cell] @ weights.T)[:, :, None, :], (ntr_s @ weights.T)[None, None])
        own = sim[np.arange(n_t), :, np.arange(n_t)]                                    # [A, k, W]
        delta_true = s_true[:, None, :] - s_true[None, :, :]                            # [A, B, W]
        sa = (own[:, :, None, :] - sim) - delta_true[:, None, :, :]                     # [A, k, B, W]
        return sa.mean(1).transpose(2, 0, 1)                                            # [W, A, B]

    off = ~np.eye(n_t, dtype=bool)
    cells_out = []
    for c, cell in enumerate(CELLS):
        sa = sa_all(c)
        mean_sa = sa[:, off].mean(1)                                                     # [W]
        lo, hi = np.percentile(mean_sa[1:], [2.5, 97.5])
        sim_point = idf1(res['idtp'][:, c].sum(-1), res['ngt'][:, c].sum(-1)[..., None],
                         res['ntr'].sum(-1)[None, None])                                 # [A, k, T]
        true_point = idf1(res['idtp_true'].sum(-1), res['ngt_true'].sum(), res['ntr'].sum(-1))
        taus, flips = [], []
        for a in range(n_t):
            for k in range(N_SEEDS):
                tau = scipy.stats.kendalltau(true_point, sim_point[a, k]).statistic
                taus.append(tau)
                flips.append(sum((true_point[i] - true_point[j]) * (sim_point[a, k, i] - sim_point[a, k, j]) < 0
                                 for i, j in itertools.combinations(range(n_t), 2)))
        cells_out.append(dict(cell=cell, mean_sa=float(mean_sa[0]), ci95=[float(lo), float(hi)],
                              sa_pairs=sa[0].tolist(), kendall_tau_mean=float(np.nanmean(taus)) if np.isfinite(taus).any() else float('nan'),
                              flips_mean=float(np.mean(flips)), flips_any=float(np.mean(np.array(flips) > 0))))
    return dict(trackers=list(trackers), idf1_true=true_point.tolist(), theta_ref=CELLS[REF],
                h1=cells_out[REF], cells=cells_out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--tracks', type=Path, default=Path('data/processed/tracks'))
    ap.add_argument('--dataset', required=True, choices=sorted(D.SPEC))
    ap.add_argument('--detector', default='yolo11x')
    ap.add_argument('--trackers', nargs='+', default=['botsort', 'bytetrack', 'ocsort', 'sort'])
    ap.add_argument('--out', type=Path, default=Path('data/processed/seed_bias'))
    ap.add_argument('--workers', type=int, default=2)
    args = ap.parse_args(argv)

    trackers = sorted(args.trackers)
    units = load_units(args.tracks, args.dataset, args.detector, trackers)
    idtp_true, ngt_true, ntr = true_scores(units, trackers)
    jobs = [(str(args.tracks), args.dataset, args.detector, trackers, a) for a in range(len(trackers))]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        per_seed = list(pool.map(_run_seed, jobs))
    res = dict(idtp=np.stack([p[0] for p in per_seed]), ngt=np.stack([p[1] for p in per_seed]),
               episodes=np.stack([p[2] for p in per_seed]), idtp_true=idtp_true, ngt_true=ngt_true, ntr=ntr)
    seqs = sorted({u.seq for u in units})
    seq_of_unit = np.array([seqs.index(u.seq) for u in units])
    out = args.out / args.dataset / args.detector
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / 'grid.npz', seq_of_unit=seq_of_unit, **res)
    summary = analyse(res, seq_of_unit, trackers)
    summary['units'] = [[u.seq, u.cls] for u in units]
    summary['commit'] = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    (out / 'summary.json').write_text(json.dumps(summary, indent=1))
    h1 = summary['h1']
    print(f"H1 at θ_ref {summary['theta_ref']}: mean SA = {h1['mean_sa']:+.4f} IDF1, 95% CI {h1['ci95']}")


if __name__ == '__main__':
    main()
