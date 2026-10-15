"""
ocsort_ctrv.py
──────────────
C2's class-conditioned motion model inside OC-SORT.

Motorcycle tracks are predicted by the CTRV extended Kalman filter of C2
(code/models/motorcycle_motion_model.py, with NSA when configured); every other
class keeps OC-SORT's linear Kalman filter. Association is OC-SORT's own
(OCM, OCR, BYTE second stage) and unchanged. C2's covariance gating is part of
ByteTrack's lost-track matching and has no counterpart here.

Observation-centric re-update (ORU) is reproduced for the CTRV filter exactly
as upstream does it for the linear one (kalmanfilter.KalmanFilterNew.freeze /
unfreeze): the filter state is saved at the first missed frame; when the track
is observed again, the state is restored and re-updated along a linearly
interpolated virtual trajectory between the last and the new observation, after
which the real observation is applied as usual (upstream applies it twice too,
since the last virtual box equals it).
"""

from __future__ import annotations

from copy import deepcopy

import numpy as np

from code.models.motorcycle_motion_model import CTRVMotionModel
from code.tracker.adaptive_bytetrack import MOTORCYCLE_CLASS_ID
from code.tracker.external.ocsort.ocsort import KalmanBoxTracker, OCSort, speed_direction


class CTRVBoxTracker(KalmanBoxTracker):
    """KalmanBoxTracker's bookkeeping (observations, velocity direction, hit
    counters, ids) with the CTRV filter in place of the linear one."""

    def __init__(self, bbox, delta_t=3, **ctrv):
        super().__init__(bbox, delta_t=delta_t)   # ids and bookkeeping; its linear KF stays unused
        self.ctrv = CTRVMotionModel(**ctrv)
        self.ctrv.init(np.asarray(bbox[:4], dtype=float))
        self.obs_history = []                     # one entry per update(): box or None
        self.saved = None                         # filter state at the first missed frame
        self.observed = False                     # as upstream: no re-update before the first update

    def _box(self):
        return self.ctrv._state_to_bbox(self.ctrv.x, self.ctrv.wh).reshape((1, 4))

    def update(self, bbox):
        if bbox is None:
            self.obs_history.append(None)
            if self.observed:
                self.saved = deepcopy(self.ctrv)
            self.observed = False
            return
        if self.last_observation.sum() >= 0:      # same velocity-direction rule as upstream
            previous_box = None
            for i in range(self.delta_t):
                dt = self.delta_t - i
                if self.age - dt in self.observations:
                    previous_box = self.observations[self.age - dt]
                    break
            if previous_box is None:
                previous_box = self.last_observation
            self.velocity = speed_direction(previous_box, bbox)
        self.last_observation = bbox
        self.observations[self.age] = bbox
        self.history_observations.append(bbox)
        self.time_since_update = 0
        self.history = []
        self.hits += 1
        self.hit_streak += 1
        box = np.asarray(bbox[:4], dtype=float)
        self.obs_history.append(box)
        if not self.observed and self.saved is not None:
            self._re_update()
        self.observed = True
        self.ctrv.update(box, score=float(bbox[4]) if len(bbox) > 4 else None)

    def _re_update(self):
        seen = [i for i, z in enumerate(self.obs_history) if z is not None]
        i1, i2 = seen[-2], seen[-1]
        b1, b2 = self.obs_history[i1], self.obs_history[i2]
        self.ctrv, self.saved = self.saved, None
        gap = i2 - i1
        for k in range(1, gap + 1):               # corners interpolate exactly like centre and size
            self.ctrv.update(b1 + (b2 - b1) * k / gap)
            if k < gap:
                self.ctrv.predict(lost=True)

    def predict(self):
        self.ctrv.predict(lost=self.time_since_update > 0)
        self.age += 1
        if self.time_since_update > 0:
            self.hit_streak = 0
        self.time_since_update += 1
        self.history.append(self._box())
        return self.history[-1]

    def get_state(self):
        return self._box()


class OCSortCTRV(OCSort):
    """OC-SORT whose motorcycle tracks use C2's CTRV filter."""

    def __init__(self, *args, ctrv=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctrv = dict(ctrv or {})

    def new_tracker(self, det, cls):
        if int(cls) == MOTORCYCLE_CLASS_ID:
            return CTRVBoxTracker(det, delta_t=self.delta_t, **self.ctrv)
        return super().new_tracker(det, cls)
