"""
code/seedbias/paper_numbers.py
──────────────────────────────
Every number the manuscript quotes, with its unrounded value, in one JSON file
(results/paper_numbers.json). Ranges are emitted as [floor, ceil] at the
printed precision so that a printed bound always holds for the unrounded value.

    python -m code.seedbias.paper_numbers
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

SRC = Path('data/processed/seed_bias')
DATASETS = ('mot17', 'dancetrack', 'fasttrack')


def lo(x, d=3):
    return math.floor(x * 10 ** d) / 10 ** d


def hi(x, d=3):
    return math.ceil(x * 10 ** d) / 10 ** d


def rng(values, d=3):
    """Printed range that contains every unrounded value."""
    return [lo(min(values), d), hi(max(values), d)]


def main():
    S = {d: json.loads((SRC / d / 'summary.json').read_text()) for d in DATASETS}
    X = json.loads(Path('results/exploratory.json').read_text())
    ext = json.loads(Path('results/external_seed_mpntrack.json').read_text())
    veh = json.loads((SRC / 'fasttrack_vehicle' / 'summary.json').read_text())
    ref = S['mot17']['theta_ref']
    out = {}
    cell = lambda s, **kw: next(c for c in s['h1'] if c['cell'] == dict(ref, **kw))
    for d, s in S.items():
        h = cell(s)
        o = out[d] = {}
        o['sa'] = h['sa_same_detector']
        o['sa_other_detector'] = h['sa_other_detector']
        o['sa_q'] = {q: cell(s, q=q)['sa_same_detector']['point'] for q in (0, 0.5, 0.9, 1)}
        o['sa_q1_ci'] = cell(s, q=1)['sa_same_detector']['ci95']
        o['sa_r'] = {r: cell(s, r=r)['sa_same_detector']['point'] for r in (0, 0.25, 0.5, 0.75, 0.9, 1)}
        o['sa_pfp'] = {p: cell(s, p_fp=p)['sa_same_detector']['point'] for p in (0, 0.1, 0.25, 0.5)}
        o['cells_above_delta'] = sum(c['above_delta'] for c in s['h1'])
        o['true_idf1_seed_systems'] = {k: v for k, v in s['idf1_true'].items() if k in s['seed_systems']}
        g = s['h1_diagnostics']
        o['without_sort'] = g['sa_without_excluded']
        o['geometry'] = dict(same=abs(g['geometry_same_detector']['a1'] - g['geometry_same_detector']['a0']),
                             other=abs(g['geometry_other_detector']['a1'] - g['geometry_other_detector']['a0']),
                             other_a1=g['geometry_other_detector']['a1'], other_a0=g['geometry_other_detector']['a0'])
        o['threshold'] = {t['threshold']: t['h1']['sa_same_detector']['point'] for t in s['threshold_sensitivity']}
        o['sort_all'] = s['sort_all_sensitivity']['h1']['sa_same_detector']['point']
        o['sd_over_seeds'] = h['sa_sd_over_seeds']
        sec = s['secondary']
        for metric in ('HOTA50', 'AssA50', 'DetA50', 'MOTA'):
            vals = [((sum(sec[a][f'{k}|{a}'][metric] for k in range(10)) - sum(sec[a][f'{k}|{b}'][metric] for k in range(10))) / 10
                     - (s['secondary_true'][a][metric] - s['secondary_true'][b][metric]))
                    for a in s['seed_systems'] for b in s['seed_systems'] if a != b]
            o[f'sa_{metric}'] = float(np.mean(vals))
        r = next(c for c in s['ranking'] if c['cell'] == ref)
        o['ranking'] = r
        h2 = next(c for c in s['h2'] if c['is_ref'])
        o['h2'] = dict(a0=h2['a0'], a1_tau=h2['a1']['tau_null_minus_seed'], tau_null=h2['tau_null'],
                       skip=h2['null_skip_share'])
        o['h2_curve'] = {c['cell']['theta']['r']: c['a0']['tau_null_minus_seed'] for c in s['h2']}
        o['fp_label_share'] = [v for k, v in s['reviewer_diagnostics']['kept_fp_sharing_a_track_label_share'].items()
                               if "'r': 0.75" in k][0]
        o['h3'] = s['h3'][str(ref)]
        o['exploratory'] = X[d]
    out['vehicle'] = cell(veh)['sa_same_detector'] if 'h1' in veh else None
    out['fasttrack']['per_class'] = S['fasttrack']['h1_diagnostics']['per_class']
    out['fasttrack']['class_confusion'] = {k: v['share'] for k, v in S['fasttrack']['class_confusion'].items()}
    out['external_mpntrack'] = ext
    out['reid'] = json.loads(Path('results/reid_check.json').read_text())          # A9, exploratory
    # ranges used in the text (printed precision 3 unless stated)
    D = DATASETS
    out['ranges'] = {
        'sa_q1': rng([out[d]['sa_q'][1] for d in D]),
        'sa_r1': rng([out[d]['sa_r'][1] for d in D]),
        'sort_all': rng([out[d]['sort_all'] for d in D]),
        'without_sort': rng([out[d]['without_sort'] for d in D]),
        'hota50': rng([out[d]['sa_HOTA50'] for d in D]), 'assa50': rng([out[d]['sa_AssA50'] for d in D]),
        'deta50': rng([out[d]['sa_DetA50'] for d in D]),
        'threshold_change_max': hi(max(abs(out[d]['threshold'][t] - out[d]['sa']['point']) for d in D for t in (0.4, 0.6))),
        'pfp_change_max': hi(max(max(out[d]['sa_pfp'].values()) - min(out[d]['sa_pfp'].values()) for d in D)),
        'geometry_other_max': hi(max(out[d]['geometry']['other'] for d in D)),
        'geometry_same_max': max(out[d]['geometry']['same'] for d in D),
        'per_tenth_q': rng([out[d]['exploratory']['q_exchange_rate']['per_tenth_unfixed'] for d in D]),
        'q_interp_err_max': {d: hi(max(abs(v) for v in out[d]['exploratory']['q_exchange_rate']['interpolation_error'].values()))
                             for d in D},
        'fp_label_share_pct': rng([100 * out[d]['fp_label_share'] for d in D], 0),
        'non_seed_gap_max': hi(max(out[d]['exploratory']['non_seed_distortion']['overall'] for d in D)),
        'min_bias_any': lo(min(out[d]['exploratory']['non_seed_distortion']['min_bias_any'] for d in D)),
        'per_class': rng(list(out['fasttrack']['per_class'].values())),
        'appearance_seeds': rng([ext['sa_vs_all_eight'][str(dict(ref, q=0.5))]['point']]
                                + [out['reid'][d]['a_reid_seed']['0.5']['over_yolo11x_motion']['point']
                                   for d in ('mot17', 'dancetrack')]),
    }
    Path('results/paper_numbers.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out['ranges'], indent=1))


if __name__ == '__main__':
    main()
