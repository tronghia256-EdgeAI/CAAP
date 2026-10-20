"""
code/seedbias/report.py
───────────────────────
Condense the per-dataset summary.json files into one Markdown report of the
pre-registered quantities (PROTOCOL.md A3-A7).

    python -m code.seedbias.report --in data/processed/seed_bias --out results/seed_bias_results.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from code.seedbias import analysis as AN
from code.seedbias import experiment as E

DATASETS = ('mot17', 'dancetrack', 'fasttrack')
DELTA = 0.01


def f(x, d=3):
    return f'{x:+.{d}f}' if isinstance(x, (int, float)) else str(x)


def ci(c, d=3):
    return f"{f(c['point'], d)} [{c['ci95'][0]:.{d}f}, {c['ci95'][1]:.{d}f}]"


def h1_without_classes(src: Path, dataset: str, summary: dict, drop) -> dict:
    """A5 item 5: H1 at θ_ref recomputed on the units of the remaining classes (BCa over sequences)."""
    z = np.load(src / dataset / 'arrays.npz')
    keep = np.array([cls not in drop for _, cls in summary['units']])
    ref = E.CELLS.index(summary['theta_ref'])
    res = dict(idtp=z['idtp'][:, [ref]][..., keep], ngt=z['ngt'][:, [ref]][..., keep],
               idtp_true=z['idtp_true'][..., keep], ngt_true=z['ngt_true'][..., keep], ntr=z['ntr'][..., keep])
    seq = np.unique(z['seq_of_unit'][keep], return_inverse=True)[1].reshape(-1)
    systems = summary['systems']
    seeds = [systems.index(x) for x in summary['seed_systems']]
    others = [i for i in range(len(systems)) if i not in seeds]
    return AN.h1(res, AN.Pooled(res, seq), seeds, seeds, others, [summary['theta_ref']])[0]['sa_same_detector']


def cell_key(theta):
    return (theta['r'], theta['p_fp'], theta['q'], theta['a'])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='src', type=Path, default=Path('data/processed/seed_bias'))
    ap.add_argument('--out', type=Path, default=Path('results/seed_bias_results.md'))
    args = ap.parse_args(argv)
    S = {d: json.loads((args.src / d / 'summary.json').read_text()) for d in DATASETS}
    ref = S['mot17']['theta_ref']
    L = ['# Seed-bias results (pre-registered quantities)', '',
         f"θ_ref = {ref}; δ = {DELTA}; 95% intervals are BCa over sequences (A5), unless marked.", '']

    L += ['## H1 — self-seed advantage at θ_ref (IDF1)', '',
          '| Dataset | seqs | SA same detector | percentile CI | leave-one-seq-out | SA vs other detector | BCa low > δ |',
          '|---|---|---|---|---|---|---|']
    for d, s in S.items():
        h = next(c for c in s['h1'] if c['cell'] == ref)
        sa = h['sa_same_detector']
        L.append(f"| {d} | {len(s['sequences'])} | {ci(sa)} | [{sa['ci95_percentile'][0]:.3f}, {sa['ci95_percentile'][1]:.3f}]"
                 f" | [{sa['loo_range'][0]:.3f}, {sa['loo_range'][1]:.3f}] | {ci(h['sa_other_detector'])} | {h['above_delta']} |")
    L += ['', 'GT_true IDF1 per system:', '']
    systems = S['mot17']['systems']
    L += ['| Dataset | ' + ' | '.join(systems) + ' |', '|---|' + '---|' * len(systems)]
    for d, s in S.items():
        L.append(f'| {d} | ' + ' | '.join(f"{s['idf1_true'][x]:.3f}" for x in systems) + ' |')

    L += ['', '### SA(A, B) at θ_ref (rows: seed A; cols: evaluated B)', '']
    for d, s in S.items():
        h = next(c for c in s['h1'] if c['cell'] == ref)
        rows, cols = s['sa_pairs_axes']['rows'], s['sa_pairs_axes']['cols']
        L += [f'**{d}**', '', '| A \\ B | ' + ' | '.join(c.split('/')[0][-1] + '/' + c.split('/')[1] for c in cols) + ' |',
              '|---|' + '---|' * len(cols)]
        for a, row in zip(rows, h['sa_pairs']):
            L.append(f'| {a} | ' + ' | '.join(f'{v:+.3f}' for v in row) + ' |')
        L.append('')

    L += ['## H1 sensitivity and diagnostics at θ_ref', '',
          '| Dataset | SD over seeds | thr 0.4 | thr 0.6 | sort_all as seed | without SORT pairs | geometry same det a1/a0 | geometry other det a1/a0 | per-seq unweighted mean |',
          '|---|---|---|---|---|---|---|---|---|']
    for d, s in S.items():
        h = next(c for c in s['h1'] if c['cell'] == ref)
        g = s['h1_diagnostics']
        th = {t['threshold']: t['h1']['sa_same_detector'] for t in s['threshold_sensitivity']}
        sa_all = s['sort_all_sensitivity']
        sa_all_txt = ci(sa_all['h1']['sa_same_detector']) if 'h1' in sa_all else sa_all.get('skipped')
        L.append(f"| {d} | {h['sa_sd_over_seeds']:.4f} | {ci(th[0.4])} | {ci(th[0.6])} | {sa_all_txt} | {f(g['sa_without_excluded'])}"
                 f" | {f(g['geometry_same_detector']['a1'])}/{f(g['geometry_same_detector']['a0'])}"
                 f" | {f(g['geometry_other_detector']['a1'])}/{f(g['geometry_other_detector']['a0'])}"
                 f" | {f(g['per_sequence_unweighted_mean'])} |")
    L += ['', 'Per-class SA (FastTrack): ' + ', '.join(f'{k} {f(v)}' for k, v in S['fasttrack']['h1_diagnostics']['per_class'].items()), '']
    L += ['Class confusion (FastTrack, share of seed boxes matching another class\'s GT; zero-GT units):', '']
    for k, v in S['fasttrack']['class_confusion'].items():
        L.append(f"- {k}: share {v['share']:.3f}, seed boxes {v['seed_boxes']}, zero-GT units {v['zero_gt_units']}")
    confused = [k for k, v in S['fasttrack']['class_confusion'].items() if v['share'] > 0.10]
    if confused:
        L += ['', f"A5 item 5 (share > 10%: {', '.join(confused)}): FastTrack SA without them = "
              f"{ci(h1_without_classes(args.src, 'fasttrack', S['fasttrack'], confused))}"]
    vehicle = args.src / 'fasttrack_vehicle' / 'summary.json'
    if vehicle.exists():
        v = json.loads(vehicle.read_text())
        h = next(c for c in v['h1'] if c['cell'] == ref)
        L += [f"A5 item 5 merged-vehicle sensitivity (car+bus+truck as one class): SA = {ci(h['sa_same_detector'])}"]
    else:
        L += ['A5 item 5 merged-vehicle sensitivity: not run yet']
    L += ['', 'Reviewer diagnostics (realised fix rate by episode size at θ_ref, nominal q = 0.5):', '']
    for d, s in S.items():
        r = s['reviewer_diagnostics']
        L.append(f"- {d}: " + ', '.join(f'{k}: {v:.2f} (n={n})' for (k, v), n in
                                       zip(r['realised_fix_rate_by_episode_size'].items(), r['episodes_by_size']) if n))
        L.append(f"  - kept FP boxes carrying a real track's label (S_r): "
                 + ', '.join(f'{v:.3f}' for v in r['kept_fp_sharing_a_track_label_share'].values()))

    L += ['', '## SA curves through θ_ref (one parameter at a time, a = 1)', '']
    for d, s in S.items():
        cells = {cell_key(c['cell']): c for c in s['h1']}
        for name, values in (('r', (0, 0.25, 0.5, 0.75, 0.9, 1)), ('q', (0, 0.5, 0.9, 1)), ('p_fp', (0, 0.1, 0.25, 0.5))):
            parts = []
            for v in values:
                th = dict(ref, **{name: v})
                c = cells[cell_key(th)]
                parts.append(f"{name}={v}: {c['sa_same_detector']['point']:+.3f}")
            L.append(f'- {d}: ' + '; '.join(parts))
        n_delta = sum(c['above_delta'] for c in s['h1'])
        n_zero = sum(c['above_zero'] for c in s['h1'])
        L.append(f'  - cells with BCa lower bound > 0: {n_zero}/192; > δ: {n_delta}/192 (descriptive, A6 item 7)')
    L += ['', '## Ranking (IDF1, 8 systems) at θ_ref', '']
    for d, s in S.items():
        c = next(c for c in s['ranking'] if c['cell'] == ref)
        L.append(f"- {d}: τ-b mean {c['tau_mean']:.3f}; δ-margin flips mean {c['flips_delta_mean']:.2f}; "
                 f"draws with ≥1 δ-margin flip {c['flips_delta_any']:.2f}; raw flips mean {c['flips_mean']:.2f}")

    L += ['', '## H2 — seed-correlated vs null errors (endpoint: a = 0, θ_ref)', '',
          '| Dataset | units | τ_null − τ_seed (a=0) | flips_seed − flips_null (a=0) | τ_seed / τ_null (a=0) | τ_null − τ_seed (a=1) | null skip share fn/id/fp |',
          '|---|---|---|---|---|---|---|']
    for d, s in S.items():
        h = next(c for c in s['h2'] if c['is_ref'])
        sk = h['null_skip_share']
        L.append(f"| {d} | {s['h2_units']} | {ci(h['a0']['tau_null_minus_seed'])} | {ci(h['a0']['flips_seed_minus_null'], 2)}"
                 f" | {h['a0']['tau_seed']:.3f} / {h['tau_null']:.3f} | {ci(h['a1']['tau_null_minus_seed'])}"
                 f" | {sk['fn']:.3f}/{sk['id']:.3f}/{sk['fp']:.3f} |")
    L += ['', 'H2 along r (a = 0): τ_null − τ_seed point estimates', '']
    for d, s in S.items():
        L.append(f'- {d}: ' + '; '.join(f"r={c['cell']['theta']['r']}: {c['a0']['tau_null_minus_seed']['point']:+.3f}" for c in s['h2']))

    L += ['', '## H3 — protocols at θ_ref (IDF1 distortion D; costs relative to GT_true boxes)', '']
    for d, s in S.items():
        rows = s['h3'][str(ref)]
        L += [f'**{d}**', '', '| Protocol | D (4 seed systems) | D (8 systems) | D_P − D_P0 (4) | member SA vs YOLO11n | member SA vs held-out | cost verify | cost draw |',
              '|---|---|---|---|---|---|---|---|']
        for name, e in rows.items():
            if name == 'P3 bracket':
                continue
            L.append(f"| {name} | {ci(e['D_seed_systems'])} | {ci(e['D_all_systems'])} | "
                     f"{ci(e['D_minus_P0_seed_systems']) if 'D_minus_P0_seed_systems' in e else '—'} | "
                     f"{ci(e['member_sa_vs_other_detector']) if 'member_sa_vs_other_detector' in e else '—'} | "
                     f"{ci(e['member_sa_vs_held_out']) if 'member_sa_vs_held_out' in e else '—'} | "
                     f"{e['cost_verify']:.2f} | {e['cost_drawn']:.2f} |")
        b = rows['P3 bracket']
        L += ['', f"P3 bracket: width {ci(b['width'])}; cost verify {b['cost_verify']:.2f}, draw {b['cost_drawn']:.2f}; coverage per system: "
              + ', '.join(f"{k.split('/')[1]} {v['point']:.2f} [{v['ci95'][0]:.2f}, {v['ci95'][1]:.2f}]" for k, v in b['coverage_per_system'].items()), '']

    L += ['## Secondary metrics at θ_ref (TrackEval, mean over seeds; SA analogue = own − others on GT_A minus on GT_true)', '']
    for d, s in S.items():
        seeds = s['seed_systems']
        for metric in ('IDF1', 'HOTA50', 'AssA50', 'DetA50', 'MOTA'):
            vals = []
            for a in seeds:
                for b in seeds:
                    if a == b:
                        continue
                    sim = lambda x: sum(s['secondary'][a][f'{k}|{x}'][metric] for k in range(10)) / 10
                    vals.append((sim(a) - sim(b)) - (s['secondary_true'][a][metric] - s['secondary_true'][b][metric]))
            L.append(f'- {d} {metric}: mean SA {sum(vals) / len(vals):+.4f}')
    L += ['', '## Stop rule (A5 item 3)', '']
    stop = []
    for d, s in S.items():
        cells = [c for c in s['h1'] if c['cell']['r'] >= 0.5]
        stop.append(all(c['sa_same_detector']['ci95'][1] < DELTA for c in cells))
    L.append(f"Upper BCa bound < δ for every θ with r ≥ 0.5 in all datasets: {all(stop)} → stop rule {'TRIGGERED' if all(stop) else 'not triggered'}.")
    L.append('')
    L.append('Provenance: ' + ', '.join(f"{d} commit {s['provenance']['commit'][:7]} run {s['provenance']['run_key'][:12]} dirty={s['provenance']['dirty']}"
                                         for d, s in S.items()))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text('\n'.join(L) + '\n', encoding='utf-8')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
