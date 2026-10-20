"""
code/seedbias/exploratory.py
────────────────────────────
Exploratory analyses listed in PROTOCOL.md A8 item 2, computed after the
confirmatory results from the saved arrays (no new simulation). Every output
is labelled exploratory in the paper.

    python -m code.seedbias.exploratory --in data/processed/seed_bias --out results/exploratory.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from code.seedbias import analysis as AN
from code.seedbias import experiment as E

DATASETS = ('mot17', 'dancetrack', 'fasttrack')


def load(src: Path, d: str):
    z = dict(np.load(src / d / 'arrays.npz'))
    summary = json.loads((src / d / 'summary.json').read_text())
    return z, summary


def without_seed_ranking(z, summary):
    """H2 analogue on the seven systems other than the seed (a = 0 at θ_ref, null at the same r)."""
    with_gt = np.flatnonzero(z['ngt_true'] > 0)
    res = {k: v[..., with_gt] for k, v in z.items() if k.startswith(('idtp', 'ngt', 'null_', 'ntr'))}
    seq = np.unique(z['seq_of_unit'][with_gt], return_inverse=True)[1].reshape(-1)
    pooled = AN.Pooled(res, seq)
    systems = summary['systems']
    seed_sys = [systems.index(s) for s in summary['seed_systems']]
    c = E.CELLS.index({**E.THETA_REF, 'a': 0})
    j = E.SLICE.index(E.REF)
    sim = pooled.sim(res['idtp'][:, c], res['ngt'][:, c])                     # [A, k, T, W]
    null = pooled.sim(res['null_idtp'][:, j], res['null_ngt'][:, j])
    d_tau, t_seed_all, t_null_all = [], [], []
    for a, s in enumerate(seed_sys):
        keep = [t for t in range(len(systems)) if t != s]
        true = pooled.true[keep].T[None]                                       # [1, W, 7]
        t_seed, _ = AN.tau_and_flips(true, np.moveaxis(sim[a][:, keep], -1, -2))  # [k, W]
        t_null, _ = AN.tau_and_flips(true, np.moveaxis(null[a][:, keep], -1, -2))
        d_tau.append(np.nanmean(t_null - t_seed, axis=0))
        t_seed_all.append(np.nanmean(t_seed[:, 0]))
        t_null_all.append(np.nanmean(t_null[:, 0]))
    return dict(tau_seed=float(np.mean(t_seed_all)), tau_null=float(np.mean(t_null_all)),
                tau_null_minus_seed=pooled.ci(np.mean(d_tau, axis=0)))


def kin_bias(summary):
    """SA of seed A over the YOLO11n system running A's tracker vs over the other YOLO11n systems."""
    ref = next(c for c in summary['h1'] if c['cell'] == summary['theta_ref'])
    rows, cols = summary['sa_pairs_axes']['rows'], summary['sa_pairs_axes']['cols']
    out, smaller = {}, 0
    for a, row in zip(rows, ref['sa_pairs']):
        trk = a.split('/')[1]
        same = row[cols.index(f'{E.OTHER}/{trk}')]
        others = [row[i] for i, c in enumerate(cols) if c.startswith(E.OTHER) and c.split('/')[1] != trk]
        out[a] = dict(same_tracker=same, other_trackers_mean=float(np.mean(others)))
        smaller += same < np.mean(others)
    return dict(per_seed=out, same_tracker_gains_more_in=f'{smaller}/{len(rows)}')


def q_exchange_rate(summary):
    """SA along q at θ_ref: linear interpolation error and SA per tenth of episodes left unfixed."""
    cells = {tuple(c['cell'].values()): c['sa_same_detector']['point'] for c in summary['h1']}
    ref = summary['theta_ref']
    sa = {q: cells[tuple(dict(ref, q=q).values())] for q in (0, 0.5, 0.9, 1)}
    lin = lambda q: sa[0] + (sa[1] - sa[0]) * q
    return dict(sa_by_q=sa, per_tenth_unfixed=(sa[0] - sa[1]) / 10,
                interpolation_error={q: sa[q] - lin(q) for q in (0.5, 0.9)},
                cells_at_or_below_delta_by_q={str(q): sum(1 for c in summary['h1'] if c['cell']['q'] == q and
                                                          not c['above_delta']) for q in (0, 0.5, 0.9, 1)})


def per_seed(z, summary):
    """SA per seed (mean over its same-detector targets) next to the seed's true IDF1 and episode count."""
    ref = next(c for c in summary['h1'] if c['cell'] == summary['theta_ref'])
    cols = summary['sa_pairs_axes']['cols']
    out = {}
    for a, (name, row) in enumerate(zip(summary['sa_pairs_axes']['rows'], ref['sa_pairs'])):
        same = [row[i] for i, c in enumerate(cols) if c.startswith(E.SHARED) and c != name]
        out[name] = dict(sa=float(np.mean(same)), true_idf1=summary['idf1_true'][name],
                         id_error_episodes=int(z['episodes'][a, 0].sum()))
    return out


def non_seed_distortion(z, summary):
    """Largest difference between two non-seed YOLO11x systems' biases b(T, A) = M(T; GT_A) − M(T; GT_true)."""
    pooled = AN.Pooled(z, z['seq_of_unit'], weights=np.ones((z['seq_of_unit'].max() + 1, 1)))
    systems = summary['systems']
    seed_sys = [systems.index(s) for s in summary['seed_systems']]
    sim = pooled.sim(z['idtp'][:, E.REF], z['ngt'][:, E.REF])[..., 0].mean(1)   # [A, T]
    bias = sim - pooled.true[:, 0][None]
    worst = {}
    for a, s in enumerate(seed_sys):
        others = [t for t in seed_sys if t != s]
        b = bias[a, others]
        worst[systems[s]] = float(b.max() - b.min())
    return dict(max_bias_gap_between_non_seeds=worst, overall=max(worst.values()),
                min_bias_any=float(bias[:, seed_sys].min()))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='src', type=Path, default=Path('data/processed/seed_bias'))
    ap.add_argument('--out', type=Path, default=Path('results/exploratory.json'))
    args = ap.parse_args(argv)
    out = {}
    for d in DATASETS:
        z, summary = load(args.src, d)
        out[d] = dict(without_seed_ranking=without_seed_ranking(z, summary), kin_bias=kin_bias(summary),
                      q_exchange_rate=q_exchange_rate(summary), per_seed=per_seed(z, summary),
                      non_seed_distortion=non_seed_distortion(z, summary))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1))
    for d, o in out.items():
        w = o['without_seed_ranking']
        print(d, '| 7-system tau seed/null', round(w['tau_seed'], 3), round(w['tau_null'], 3),
              '| d_tau', round(w['tau_null_minus_seed']['point'], 3), [round(x, 3) for x in w['tau_null_minus_seed']['ci95']],
              '| kin', o['kin_bias']['same_tracker_gains_more_in'],
              '| per tenth q', round(o['q_exchange_rate']['per_tenth_unfixed'], 4),
              '| interp err', {k: round(v, 4) for k, v in o['q_exchange_rate']['interpolation_error'].items()},
              '| non-seed gap', round(o['non_seed_distortion']['overall'], 4), 'min bias', round(o['non_seed_distortion']['min_bias_any'], 4))
        print('   per seed', {k.split('/')[1]: (round(v['sa'], 3), round(v['true_idf1'], 3), v['id_error_episodes']) for k, v in o['per_seed'].items()})
        print('   cells <= delta by q', o['q_exchange_rate']['cells_at_or_below_delta_by_q'])


if __name__ == '__main__':
    main()
