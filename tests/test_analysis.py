import itertools
import json

import numpy as np
import pytest
import scipy.stats

from code.annotation_sim.simulate import write_mot
from code.seedbias import analysis as AN
from code.seedbias import experiment as E
from tests.test_experiment import T, make_unit


def planted(n_sys=4, n_seeds=2, n_units=6, n_cells=3, k=3, boost=0):
    """Arrays where every simulated GT reproduces GT_true, except a planted self-advantage `boost` (IDTP)."""
    idtp_true = np.full((n_sys, n_units), 80)
    ngt_true = np.full(n_units, 100)
    ntr = np.full((n_sys, n_units), 100)
    idtp = np.broadcast_to(idtp_true, (n_seeds, n_cells, k, n_sys, n_units)).copy()
    for a in range(n_seeds):
        idtp[a, :, :, a, :] += boost
    ngt = np.broadcast_to(ngt_true, (n_seeds, n_cells, k, n_units)).copy()
    return dict(idtp=idtp, ngt=ngt, idtp_true=idtp_true, ngt_true=ngt_true, ntr=ntr)


@pytest.mark.parametrize('boost, expected', [(0, 0.0), (10, 0.1)])
def test_h1_recovers_planted_advantage(boost, expected):
    res = planted(boost=boost)
    pooled = AN.Pooled(res, np.arange(6), n_boot=200)
    out = AN.h1(res, pooled, seed_sys=[0, 1], x_sys=[0, 1], n_sys=[2, 3], cells=[{}, {}, {}])
    assert out[0]['sa_same_detector']['point'] == pytest.approx(expected)
    assert out[0]['sa_other_detector']['point'] == pytest.approx(expected)
    assert out[0]['sa_same_detector']['ci95'][0] == pytest.approx(expected)
    assert out[0]['above_delta'] == (expected > AN.DELTA)


def test_tau_b_matches_scipy_with_ties():
    rng = np.random.default_rng(0)
    for _ in range(200):
        x, y = rng.integers(0, 4, 7).astype(float), rng.integers(0, 4, 7).astype(float)
        tau, flips = AN.tau_and_flips(x, y)
        ref = scipy.stats.kendalltau(x, y).statistic
        assert (np.isnan(tau) and np.isnan(ref)) or tau == pytest.approx(ref)
        assert flips == sum((x[i] - x[j]) * (y[i] - y[j]) < 0 for i in range(7) for j in range(i + 1, 7))


def test_distortion_is_zero_for_unbiased_and_positive_for_planted():
    true = np.array([[0.5], [0.6], [0.7]])
    assert AN.distortion(true, true)[0] == 0
    sim = true.copy()
    sim[0] += 0.1
    assert AN.distortion(sim, true)[0] == pytest.approx(0.1 * 4 / 6)


def write_dataset(root, rng, n_seq=3):
    """A tiny tracks/ tree: tracks/<dataset>/gt/<seq>/{person.txt, seqinfo.json} and per-system tracks."""
    for s in range(n_seq):
        unit = make_unit(rng)
        gdir = root / 'mot17' / 'gt' / f'SEQ-{s}'
        gdir.mkdir(parents=True)
        write_mot(gdir / 'person.txt', unit.gt)
        (gdir / 'seqinfo.json').write_text(json.dumps({'n_frames': T, 'frame_rate': 30}))
        outs = list(unit.tracks.values()) + [unit.tracks['a']]
        for i, system in enumerate(f'{d}/{t}' for d in (E.SHARED, E.OTHER) for t in E.TRACKERS):
            det, trk = system.split('/')
            tdir = root / 'mot17' / det / f'SEQ-{s}' / 'person'
            tdir.mkdir(parents=True, exist_ok=True)
            write_mot(tdir / f'{trk}.txt', outs[i % len(outs)])
        write_mot(root / 'mot17' / E.SHARED / f'SEQ-{s}' / 'person' / 'sort_all.txt', unit.tracks['b'])


def test_experiment_end_to_end_on_a_tiny_grid(tmp_path, monkeypatch):
    grid = dict(r=(0.5, 0.75), p_fp=(0.1,), q=(0.5,), a=(1, 0))
    cells = [dict(zip(grid, v)) for v in itertools.product(*grid.values())]
    monkeypatch.setattr(E, 'GRID', grid)
    monkeypatch.setattr(E, 'CELLS', cells)
    monkeypatch.setattr(E, 'REF', cells.index(E.THETA_REF))
    monkeypatch.setattr(E, 'SLICE', [cells.index({**E.THETA_REF, 'r': r}) for r in grid['r']])
    monkeypatch.setattr(E, 'N_SEEDS', 2)
    monkeypatch.setattr(AN, 'N_BOOT', 50)
    write_dataset(tmp_path / 'tracks', np.random.default_rng(5))
    E.main(['--tracks', str(tmp_path / 'tracks'), '--dataset', 'mot17', '--out', str(tmp_path / 'out'),
            '--workers', '0'])
    summary = json.loads((tmp_path / 'out' / 'mot17' / 'summary.json').read_text())
    assert len(summary['systems']) == 8 and len(summary['seed_systems']) == 4
    assert np.isfinite(summary['h1'][E.CELLS.index(E.THETA_REF)]['sa_same_detector']['point'])
    assert len(summary['h2']) == 2 and summary['h2'][1]['is_ref']
    assert {'a0', 'a1', 'null_skip_share'} <= summary['h2'][1].keys()
    ref_rows = summary['h3'][str(E.THETA_REF)]
    assert {'P0 single seed', 'P2 consensus', 'P3 bracket'} <= ref_rows.keys()
    assert sum(name.startswith('P2 consensus without') for name in ref_rows) == 4
    assert 'member_sa_vs_held_out' in ref_rows['P2 consensus without sort']
    assert len(summary['threshold_sensitivity']) == 2
    assert set(summary['reviewer_diagnostics']['missed_run_length_histogram']) == set(summary['seed_systems'])
    assert set(summary['secondary']) == set(summary['seed_systems'])
    diag = summary['h1_diagnostics']
    assert len(diag['per_sequence']) == 3 and len(diag['per_class']) == 1
    assert {'a1', 'a0'} == diag['geometry_other_detector'].keys()
    assert 'person' in summary['class_confusion']
    sens = summary['sort_all_sensitivity']
    assert f'{E.SHARED}/sort_all' in sens['systems'] and np.isfinite(sens['h1']['sa_same_detector']['point'])
    prov = json.loads((tmp_path / 'out' / 'mot17' / 'provenance.json').read_text())
    parts = list((tmp_path / 'out' / 'mot17' / 'parts').rglob('*.npz'))
    assert prov['run_key'].startswith(parts[0].parent.name) and len(parts) == 4 * 3   # 4 seeds x 3 units
    first = (tmp_path / 'out' / 'mot17' / 'summary.json').read_text()
    E.main(['--tracks', str(tmp_path / 'tracks'), '--dataset', 'mot17', '--out', str(tmp_path / 'out'),
            '--workers', '0'])                                    # rerun: every unit comes from its checkpoint
    again = json.loads((tmp_path / 'out' / 'mot17' / 'summary.json').read_text())
    assert again['h1'] == json.loads(first)['h1']


def test_bca_is_close_to_percentile_for_a_symmetric_statistic():
    rng = np.random.default_rng(9)
    boot = rng.normal(0.05, 0.01, 4000)
    jack = 0.05 + rng.normal(0, 0.001, 12)
    lo, hi = AN._bca(np.array(0.05), boot[None], jack[None])
    plo, phi = np.percentile(boot, [2.5, 97.5])
    assert abs(lo[0] - plo) < 0.002 and abs(hi[0] - phi) < 0.002


def test_margin_flips_ignore_near_ties():
    true = np.array([0.700, 0.705, 0.80])      # first two within δ
    sim = np.array([0.706, 0.700, 0.80])       # their order flips
    _, raw = AN.tau_and_flips(true, sim)
    _, margin = AN.tau_and_flips(true, sim, AN.DELTA)
    assert raw == 1 and margin == 0
