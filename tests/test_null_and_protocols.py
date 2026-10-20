import numpy as np

from code.annotation_sim import Reviewer, prepare, simulate
from code.seedbias import experiment as E
from code.seedbias.evaluate import evaluate_sequence
from code.seedbias.null_model import null_gt
from code.seedbias.protocols import consensus_seed, union_seed
from tests.test_experiment import T, make_unit


def materialise(gt, labels, extra):
    keep = labels >= 0
    rows = np.column_stack([gt[keep, 0], labels[keep], gt[keep, 2:6]])
    return np.concatenate([rows, extra]) if len(extra) else rows


def test_null_matches_requested_error_sizes_and_stays_valid():
    rng = np.random.default_rng(0)
    for _ in range(30):
        unit = make_unit(rng)
        gt = prepare(np.empty((0, 6)), unit.gt).gt
        missed = list(rng.integers(1, 6, rng.integers(0, 4)))
        pairs = [[int(rng.integers(1, 5)), int(rng.integers(0, 2))] for _ in range(rng.integers(0, 4))]
        fps = list(rng.integers(1, 6, rng.integers(0, 3)))
        labels, extra, counts = null_gt(gt, T, missed, pairs, fps, rng)
        assert counts['fn']['requested'] == sum(missed) and counts['fp']['requested'] == sum(fps)
        assert (labels < 0).sum() == sum(missed) - counts['fn']['skipped']
        assert len(extra) == sum(fps) - counts['fp']['skipped']
        out = materialise(gt, labels, extra)
        assert len(np.unique(out[:, :2], axis=0)) == len(out)          # one box per (frame, id)
        assert out[:, 0].min() >= 1 and out[:, 0].max() <= T


def test_null_with_no_errors_is_gt_true():
    rng = np.random.default_rng(1)
    unit = make_unit(rng)
    gt = prepare(np.empty((0, 6)), unit.gt).gt
    labels, extra, _ = null_gt(gt, T, [], [], [], rng)
    assert (labels >= 0).all() and len(extra) == 0
    assert len(np.unique(labels)) == len(np.unique(gt[:, 1]))


def test_fast_identity_scores_null_gt_like_trackeval():
    rng = np.random.default_rng(2)
    for _ in range(10):
        unit = make_unit(rng)
        prep = prepare(unit.tracks['a'], unit.gt)
        _, st, _ = simulate(prep, Reviewer(0.5, 0.5, 0.5, 1), rng, with_origin=True)
        labels, extra, _ = null_gt(prep.gt, T, st['missed_lengths'], st['unfixed_pairs'],
                                   st['kept_fp_lengths'], rng)
        fast = E.FastIdentity(unit, prep.gt, None)
        keep = labels >= 0
        origin = np.column_stack([np.ones(keep.sum(), dtype=int), np.flatnonzero(keep)])
        idtp = fast.idtp(labels[keep], origin, extra)
        gts = materialise(prep.gt, labels, extra)
        for name, tr in unit.tracks.items():
            assert idtp[name] == evaluate_sequence(tr, gts, T)['Identity']['IDTP']


def test_null_merges_never_duplicate_labels_with_many_short_tracks():
    rng = np.random.default_rng(3)
    for _ in range(300):
        rows = []
        for k in range(1, 9):                                    # short tracks staggered in time
            start = int(rng.integers(1, 30))
            rows += [[t, k, 10.0 * k, 0, 10.0 * k + 8, 20] for t in range(start, start + int(rng.integers(3, 12)))]
        gt = prepare(np.empty((0, 6)), np.array(rows, float)).gt
        pairs = [[int(rng.integers(1, 4)), 1] for _ in range(int(rng.integers(1, 8)))]
        labels, extra, _ = null_gt(gt, 45, [], pairs, [], rng)    # raises on a duplicate (frame, label)
        out = materialise(gt, labels, extra)
        assert len(np.unique(out[:, :2], axis=0)) == len(out)


def test_null_fp_copies_do_not_land_on_real_objects():
    rng = np.random.default_rng(4)
    gt = np.array([[t, 1, 0, 0, 10, 10] for t in range(1, 41)]                # a static object
                  + [[t, 2, 100, 0, 110, 10] for t in range(1, 11)], float)    # a short one elsewhere
    gt = prepare(np.empty((0, 6)), gt).gt
    for _ in range(30):
        labels, extra, counts = null_gt(gt, 40, [], [], [5], rng)
        if len(extra):                                          # a copy of the static track would overlap it
            assert not ((extra[:, 2] == 0) & (extra[:, 3] == 0)).any()
        assert counts['fp']['requested'] == 5


def test_union_seed_drops_duplicates_and_keeps_ids_apart():
    a = np.array([[1, 1, 0, 0, 10, 10], [2, 1, 1, 0, 11, 10]], float)
    b = np.array([[1, 1, 0, 0, 10, 10], [1, 2, 50, 0, 60, 10], [3, 1, 2, 0, 12, 10]], float)
    u = union_seed([a, b])
    assert len(u) == 4                                       # b's frame-1 duplicate dropped
    assert len(np.unique(u[:, :2], axis=0)) == 4
    assert set(u[u[:, 0] == 1, 1]) == {0, 2}                 # a's id 0, b's id 2 (b ids offset by a's count)


def test_consensus_mean_geometry_candidates_and_majority_links():
    a = np.array([[t, 1, t, 0, t + 10, 10] for t in range(1, 6)] + [[1, 2, 50, 0, 60, 10]], float)
    b = np.array([[t, 7, t + 1, 0, t + 11, 10] for t in range(1, 6)], float)
    c = np.array([[t, 3, t, 0, t + 10, 10] for t in range(1, 6)], float)
    seed, cand = consensus_seed([a, b, c])
    assert len(seed) == 5 and len(cand) == 1                 # the lone a box is a candidate
    np.testing.assert_allclose(seed[seed[:, 0] == 1, 2], 4 / 3)          # mean of x1 = 1, 2, 1
    assert len(np.unique(seed[:, 1])) == 1


def test_consensus_is_not_broken_by_one_fragmenting_member_or_a_gap():
    frames = [t for t in range(1, 41) if t not in (10, 11)]   # a two-frame detection gap
    steady = lambda i: np.array([[t, i, t, 0, t + 10, 10] for t in frames], float)
    fragmenting = np.array([[t, 100 + t // 5, t, 0, t + 10, 10] for t in frames], float)   # new id every 5 frames
    seed, _ = consensus_seed([steady(1), steady(2), steady(3), fragmenting])
    assert len(np.unique(seed[:, 1])) == 1                   # 3 of 4 agree across the gap and the id changes
