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


def test_experiment_end_to_end_on_a_tiny_grid(tmp_path, monkeypatch):
    grid = dict(r=(0.5, 0.75), p_fp=(0.1,), q=(0.5,), a=(1,))
    cells = [dict(zip(grid, v)) for v in [(0.5, 0.1, 0.5, 1), (0.75, 0.1, 0.5, 1)]]
    monkeypatch.setattr(E, 'GRID', grid)
    monkeypatch.setattr(E, 'CELLS', cells)
    monkeypatch.setattr(E, 'REF', 1)
    monkeypatch.setattr(E, 'SLICE', [0, 1])
    monkeypatch.setattr(E, 'N_SEEDS', 2)
    monkeypatch.setattr(AN, 'N_BOOT', 50)
    write_dataset(tmp_path / 'tracks', np.random.default_rng(5))
    E.main(['--tracks', str(tmp_path / 'tracks'), '--dataset', 'mot17', '--out', str(tmp_path / 'out'),
            '--workers', '0'])
    summary = json.loads((tmp_path / 'out' / 'mot17' / 'summary.json').read_text())
    assert len(summary['systems']) == 8 and len(summary['seed_systems']) == 4
    assert np.isfinite(summary['h1'][1]['sa_same_detector']['point'])
    assert len(summary['h2']) == 2 and summary['h2'][1]['is_ref']
    ref_rows = summary['h3'][str(cells[1])]
    assert {'P0 single seed', 'P2 consensus', 'P3 bracket'} <= ref_rows.keys()
    assert sum(name.startswith('P1 union') for name in ref_rows) == 6 + 4
    assert set(summary['secondary']) == set(summary['seed_systems'])
