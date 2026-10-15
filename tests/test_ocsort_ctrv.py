import numpy as np

from code.tracker.external.ocsort.ocsort import KalmanBoxTracker, OCSort
from code.tracker.ocsort_ctrv import CTRVBoxTracker, OCSortCTRV

PARAMS = dict(det_thresh=0.5, max_age=30, min_hits=3, iou_threshold=0.3, delta_t=3,
              asso_func="iou", inertia=0.2, use_byte=True)
CTRV = dict(dt=1.0, q_diag=[0.5, 0.5, 0.1, 1e-3, 1e-4], r_diag=[10.0, 10.0], nsa=True)


def arc(k, cls=1):
    """A 20x30 box on a circle of radius 200 px, about 4 px/frame."""
    a = 0.02 * k
    cx, cy = 400 + 200 * np.cos(a), 300 + 200 * np.sin(a)
    return [cx - 10, cy - 15, cx + 10, cy + 15, 0.9, cls]


def test_motorcycles_get_ctrv_and_other_classes_keep_the_linear_filter():
    t = OCSortCTRV(**PARAMS, ctrv=CTRV)
    t.update(np.array([arc(0, 1), [10, 10, 60, 40, .9, 0]]))
    kinds = {int(trk.cls): type(trk) for trk in t.trackers}
    assert kinds == {1: CTRVBoxTracker, 0: KalmanBoxTracker}
    assert type(OCSort(**PARAMS).new_tracker(np.array(arc(0)[:5]), 1)) is KalmanBoxTracker


def test_ctrv_track_keeps_its_id_across_a_gap_with_re_update():
    t = OCSortCTRV(**PARAMS, ctrv=CTRV)
    ids = set()
    for k in range(40):
        dets = np.empty((0, 6)) if 20 <= k < 24 else np.array([arc(k)])
        out = t.update(dets)
        assert np.isfinite(out[:, :4]).all()
        ids |= {int(r[4]) for r in out}
    assert ids == {1}
    trk = t.trackers[0]
    assert isinstance(trk, CTRVBoxTracker) and trk.saved is None and trk.observed


def test_track_lost_right_after_birth_is_re_observed_without_re_update():
    t = OCSortCTRV(**PARAMS, ctrv=CTRV)
    for k, present in enumerate([1, 0, 0, 1, 1]):
        t.update(np.array([arc(k)]) if present else np.empty((0, 6)))
    assert len(t.trackers) == 1 and t.trackers[0].hits == 2
