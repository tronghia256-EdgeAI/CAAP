import itertools

import numpy as np
import pytest
import scipy.optimize

from code.annotation_sim import Reviewer, prepare, simulate
from code.seedbias import experiment as E
from code.seedbias.evaluate import evaluate_sequence

T = 40


def world(rng, n_obj=5):
    gt = []
    for k in range(1, n_obj + 1):
        present = rng.random(T) > 0.15
        gt += [[t, k, 3.0 * t, 50.0 * k, 3.0 * t + 30, 50.0 * k + 40] for t in range(1, T + 1) if present[t - 1]]
    return np.array(gt, float)


def tracker_output(gt, rng, noise):
    out = gt.copy()
    out[:, 2:6] += rng.normal(0, noise, (len(out), 4))
    out = out[rng.random(len(out)) > 0.1]
    switch = (out[:, 0] > rng.integers(5, T)) & (out[:, 1] == rng.integers(1, 6))
    out[switch, 1] += 100                                     # a fragment
    fp = [[f, 77, 400, 400, 430, 440] for f in range(1, int(rng.integers(2, 10)))]
    return np.concatenate([out, np.array(fp, float)])


def make_unit(rng):
    gt = world(rng)
    tracks = {name: tracker_output(gt, rng, noise) for name, noise in (('a', 1.0), ('b', 3.0), ('c', 6.0))}
    return E.Unit('S', 'person', T, gt, tracks)


def test_fast_identity_equals_trackeval_on_simulated_gt():
    rng = np.random.default_rng(0)
    for _ in range(15):
        unit = make_unit(rng)
        prep = prepare(unit.tracks['a'], unit.gt)
        fast = E.FastIdentity(unit, prep.gt, prep.seed)
        theta = Reviewer(*rng.choice([0, 0.5, 1], 3), a=float(rng.choice([0, 1])))
        gts, _, origin = simulate(prep, theta, rng, with_origin=True)
        idtp = fast.idtp(gts[:, 1].astype(int), origin)
        for name, tr in unit.tracks.items():
            ref = evaluate_sequence(tr, gts, T)['Identity']
            assert idtp[name] == ref['IDTP']


def test_true_scores_equal_trackeval():
    rng = np.random.default_rng(1)
    units = [make_unit(rng) for _ in range(3)]
    idtp, ngt, ntr = E.true_scores(units, ['a', 'b', 'c'])
    for u, unit in enumerate(units):
        for i, name in enumerate('abc'):
            assert idtp[i, u] == evaluate_sequence(unit.tracks[name], unit.gt, T)['Identity']['IDTP']
    assert ngt.tolist() == [len(u.gt) for u in units]


def test_max_matching_equals_dense_hungarian():
    rng = np.random.default_rng(2)
    for _ in range(50):
        rows, cols = rng.integers(0, 8, 60), rng.integers(0, 6, 60)
        m = np.zeros((8, 6))
        np.add.at(m, (rows, cols), 1)
        i, j = scipy.optimize.linear_sum_assignment(m, maximize=True)
        assert E.max_matching(rows, cols) == m[i, j].sum()


def test_grid_contains_theta_ref_and_both_geometries():
    assert E.CELLS[E.REF] == E.THETA_REF and len(E.CELLS) == 6 * 4 * 4 * 2


def test_analyse_gives_zero_sa_when_simulated_gt_is_the_truth():
    rng = np.random.default_rng(3)
    n_t, n_u = 3, 4
    idtp_true = rng.integers(50, 100, (n_t, n_u))
    ngt_true = np.full(n_u, 120)
    ntr = rng.integers(90, 130, (n_t, n_u))
    idtp = np.broadcast_to(idtp_true, (n_t, len(E.CELLS), E.N_SEEDS, n_t, n_u)).copy()
    ngt = np.broadcast_to(ngt_true, (n_t, len(E.CELLS), E.N_SEEDS, n_u)).copy()
    res = dict(idtp=idtp, ngt=ngt, idtp_true=idtp_true, ngt_true=ngt_true, ntr=ntr)
    out = E.analyse(res, np.array([0, 0, 1, 2]), ['a', 'b', 'c'])
    assert out['h1']['mean_sa'] == pytest.approx(0) and out['h1']['ci95'] == pytest.approx([0, 0])
    assert out['h1']['flips_mean'] == 0 and out['h1']['kendall_tau_mean'] == pytest.approx(1)


def test_analyse_detects_a_planted_self_advantage():
    rng = np.random.default_rng(4)
    n_t, n_u = 3, 6
    idtp_true = np.full((n_t, n_u), 80)
    ngt_true = np.full(n_u, 100)
    ntr = np.full((n_t, n_u), 100)
    idtp = np.broadcast_to(idtp_true, (n_t, len(E.CELLS), E.N_SEEDS, n_t, n_u)).copy()
    for a in range(n_t):
        idtp[a, :, :, a, :] += 10                          # each seed scores 0.1 IDF1 higher on its own GT
    ngt = np.broadcast_to(ngt_true, (n_t, len(E.CELLS), E.N_SEEDS, n_u)).copy()
    out = E.analyse(dict(idtp=idtp, ngt=ngt, idtp_true=idtp_true, ngt_true=ngt_true, ntr=ntr),
                    np.arange(n_u), ['a', 'b', 'c'])
    assert out['h1']['mean_sa'] == pytest.approx(0.1)
    assert out['h1']['ci95'][0] > 0.09
