import itertools

import numpy as np
import pytest

from code.annotation_sim import Reviewer, match, prepare, read_mot, simulate, write_mot
from code.evaluation.metrics import compute_tracking_metrics

FRAMES = range(1, 31)
PERFECT = Reviewer(r=1, p_fp=0, q=1, a=0)
PASSIVE = Reviewer(r=0, p_fp=1, q=0, a=1)


def box(k, t, dx=0.0):
    x = 100.0 * k + t + dx
    return [x, 0.0, x + 20.0, 40.0]


def scenario():
    """GT g1..g4; seed has a crossing swap (s10/s20 at frame 16), misses g3 entirely
    and g4 at frame 13, fragments g4 (s30 → s31), and has an FP run (s40)."""
    gt = [[t, k, *box(k, t)] for k in (1, 2, 3) for t in FRAMES]
    gt += [[t, 4, *box(4, t)] for t in range(5, 26)]
    seed = [[t, 10, *box(1 if t <= 15 else 2, t, 1)] for t in FRAMES]
    seed += [[t, 20, *box(2 if t <= 15 else 1, t, 1)] for t in FRAMES]
    seed += [[t, 30, *box(4, t, 1)] for t in range(5, 13)]
    seed += [[t, 31, *box(4, t, 1)] for t in range(14, 26)]
    seed += [[t, 40, *box(9, t)] for t in range(3, 9)]
    return np.array(seed, float), np.array(gt, float)


def partition(tracks):
    """Map (frame, box) → id, after checking it is one-to-one."""
    keys = {(int(f), *np.round(b, 9)): int(i) for f, i, *b in tracks}
    assert len(keys) == len(tracks)
    return keys


def same_tracks(a, b):
    pa, pb = partition(a), partition(b)
    if pa.keys() != pb.keys():
        return False
    pairs = {(pa[k], pb[k]) for k in pa}
    return len(pairs) == len({x for x, _ in pairs}) == len({y for _, y in pairs})


def run(seed, gt, reviewer, s=0):
    return simulate(prepare(seed, gt), reviewer, np.random.default_rng(s))


def frame_list(tracks, frames=FRAMES):
    return [[(int(i), list(b)) for f, i, *b in tracks if f == t] for t in frames]


def random_case(rng):
    """GT with occlusion gaps; seed ids that hop between objects, leave and re-enter,
    duplicate detections on one object, and far-away FP boxes."""
    n_obj, T = int(rng.integers(1, 6)), int(rng.integers(5, 25))
    gt = []
    for k in range(1, n_obj + 1):
        present = rng.random(T) > 0.2
        gt += [[t, k, *box(k, t)] for t in range(1, T + 1) if present[t - 1]]
    gt = np.array(gt, float).reshape(-1, 6)
    present = {(int(f), int(k)) for f, k, *_ in gt}
    seed = []
    for sid in range(1, int(rng.integers(1, 7)) + 1):
        t = 1
        while t <= T:
            length, k = int(rng.integers(1, 6)), int(rng.integers(1, n_obj + 2))
            for u in range(t, min(T, t + length - 1) + 1):
                if k == n_obj + 1:
                    seed.append([u, sid, *box(20 + sid, u)])
                elif (u, k) in present and rng.random() > 0.1:
                    seed.append([u, sid, *box(k, u, rng.uniform(-1, 1))])
            t += length + int(rng.integers(0, 3))
    return np.array(seed, float).reshape(-1, 6), gt


def test_perfect_reviewer_recovers_gt():
    seed, gt = scenario()
    out, _ = run(seed, gt, PERFECT)
    assert same_tracks(out, gt)


def test_passive_reviewer_returns_seed_and_seed_scores_one():
    seed, gt = scenario()
    out, _ = run(seed, gt, PASSIVE)
    assert same_tracks(out, seed)
    assert compute_tracking_metrics(frame_list(seed), frame_list(out)).idf1 == pytest.approx(1.0)


def test_identities_hold_on_random_hard_inputs():
    rng = np.random.default_rng(123)
    for _ in range(300):
        seed, gt = random_case(rng)
        assert same_tracks(run(seed, gt, PERFECT)[0], gt)
        assert same_tracks(run(seed, gt, PASSIVE)[0], seed)


def test_scenario_counts():
    seed, gt = scenario()
    st = prepare(seed, gt).stats
    # swap: (s10,g2) and (s20,g1) are one episode; fragment (s31,g4) is another
    assert (st['episodes'], st['episode_sizes'], st['fn_runs'], st['fp_runs']) == (2, [1, 2], 2, 1)  # by first frame


def one_episode_outcomes(seed, gt):
    """Over many draws at q=0.5: GT_S is the seed iff the single episode is unfixed, GT_true iff fixed
    (seed boxes equal GT boxes here, so geometry does not matter)."""
    prep = prepare(seed, gt)
    assert prep.n_episodes == 1
    outcomes = []
    for s in range(200):
        out, st = simulate(prep, Reviewer(r=1, p_fp=0, q=0.5, a=1), np.random.default_rng(s))
        is_seed, is_gt = same_tracks(out, seed), same_tracks(out, gt)
        assert is_gt == bool(st['episodes_fixed']) and is_seed == (not st['episodes_fixed'])
        outcomes.append(is_gt)
    assert 0.35 < np.mean(outcomes) < 0.65


def test_swap_is_one_episode_fixed_with_probability_q():
    gt = np.array([[t, k, *box(k, t)] for k in (1, 2) for t in FRAMES], float)
    seed = np.array([[t, 10, *box(1 if t <= 15 else 2, t)] for t in FRAMES]
                    + [[t, 20, *box(2 if t <= 15 else 1, t)] for t in FRAMES], float)
    one_episode_outcomes(seed, gt)


def test_excursion_is_one_episode_fixed_with_probability_q():
    gt = np.array([[1, 1, *box(1, 1)], [3, 1, *box(1, 3)], [2, 2, *box(2, 2)]], float)
    seed = np.array([[1, 10, *box(1, 1)], [2, 10, *box(2, 2)], [3, 10, *box(1, 3)]], float)
    one_episode_outcomes(seed, gt)


def test_fragment_is_one_episode_fixed_with_probability_q():
    gt = np.array([[t, 1, *box(1, t)] for t in FRAMES], float)
    seed = np.array([[t, 10 if t <= 20 else 11, *box(1, t)] for t in FRAMES], float)
    one_episode_outcomes(seed, gt)


def test_matching_is_gated_before_assignment():
    seed = np.array([[1, 10, 38, 0, 65, 40], [1, 20, 20, 0, 59, 40]], float)
    gt = np.array([[1, 1, 38, 0, 52, 40], [1, 2, 52, 0, 77, 40]], float)
    assert (match(seed, gt) >= 0).sum() == 1


def test_runs_split_at_frame_gaps():
    gt = np.array([[t, 1, *box(1, t)] for t in (1, 2, 3, 8, 9, 10)], float)
    seed = np.array([[t, 10, *box(5, t)] for t in (1, 2, 9, 10)], float)
    st = prepare(seed, gt).stats
    assert (st['fn_runs'], st['fp_runs']) == (2, 2)


def test_added_gt_box_replaces_drifted_seed_box():
    gt = np.array([[t, 1, 0, 0, 20, 40] for t in FRAMES], float)
    seed = np.array([[t, 10, 0 if t <= 10 or t > 20 else 7.5, 0, (0 if t <= 10 or t > 20 else 7.5) + 20, 40]
                     for t in FRAMES], float)          # IoU 0.45 on frames 11–20
    out, st = run(seed, gt, Reviewer(r=1, p_fp=1, q=0, a=1))
    assert st['fp_replaced_boxes'] == 10 and st['fp_kept_boxes'] == 0
    assert np.bincount(out[:, 0].astype(int)).max() == 1          # never two boxes for one object
    assert same_tracks(out, gt)


@pytest.mark.parametrize('r,p_fp,q,a', list(itertools.product((0, 0.5, 1), (0, 0.5, 1), (0, 0.5, 1), (0, 1))))
def test_any_reviewer_gives_valid_deterministic_gt(r, p_fp, q, a):
    seed, gt = scenario()
    prep = prepare(seed, gt)
    for s in range(5):
        out, st = simulate(prep, Reviewer(r, p_fp, q, a), np.random.default_rng(s))
        again, _ = simulate(prep, Reviewer(r, p_fp, q, a), np.random.default_rng(s))
        np.testing.assert_array_equal(out, again)
        assert len(out) == prep.tp.size + st['fn_added_boxes'] + st['fp_kept_boxes']
        partition(out)


def test_row_order_does_not_change_the_result():
    rng = np.random.default_rng(7)
    for _ in range(50):
        seed, gt = random_case(rng)
        a, _ = run(seed, gt, Reviewer(0.5, 0.5, 0.5, 0.5), 3)
        b, _ = run(seed[rng.permutation(len(seed))], gt[rng.permutation(len(gt))], Reviewer(0.5, 0.5, 0.5, 0.5), 3)
        np.testing.assert_array_equal(a, b)


@pytest.mark.parametrize('bad', [
    [[1, 1, 0, 0, 1, 1], [1, 1, 2, 2, 3, 3]],      # duplicate (frame, id)
    [[1.5, 1, 0, 0, 1, 1]],                        # non-integer frame
    [[1, 1, np.nan, 0, 1, 1]],                     # NaN
])
def test_invalid_input_is_rejected(bad):
    with pytest.raises(ValueError):
        prepare(np.array(bad, float), np.empty((0, 6)))


def test_reviewer_parameters_are_checked():
    with pytest.raises(ValueError):
        Reviewer(r=1.5, p_fp=0, q=0)


def test_empty_seed_gives_reviewer_added_gt_only():
    _, gt = scenario()
    out, st = run(np.empty((0, 6)), gt, PERFECT)
    assert same_tracks(out, gt) and st['fn_added'] == 4


def test_mot_roundtrip_filter_and_empty(tmp_path):
    seed, _ = scenario()
    write_mot(tmp_path / 'x.txt', seed)
    np.testing.assert_allclose(read_mot(tmp_path / 'x.txt'), seed[np.lexsort(seed[:, ::-1].T)], atol=0.01)
    assert len(read_mot(tmp_path / 'x.txt', keep=lambda raw: raw[:, 1] == 10)) == 30
    (tmp_path / 'e.txt').write_text('')
    assert read_mot(tmp_path / 'e.txt').shape == (0, 6)
