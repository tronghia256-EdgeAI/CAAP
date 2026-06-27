"""
context_estimator.py
────────────────────
C1 Component: Context Estimator

Reads 4 traffic context signals from the current frame and track history,
and returns a TrafficState dataclass used by AdaptiveController.

Signals:
    density    -- number of currently active tracks
    hour       -- hour of day (0–23), proxy for rush-hour vs off-peak
    brightness -- mean pixel intensity of the frame, proxy for lighting
    fp_rate    -- fraction of tracks with age < MIN_AGE (likely false positives)

Author  : Trọng Nghĩa
Paper   : Context-Aware Adaptive Perception for Mixed Traffic
Target  : IEEE T-ITS
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np


# ── Data structures ──────────────────────────────────────────────────

@dataclass
class TrafficState:
    """Snapshot of traffic context at a single timestep."""
    density: int        # number of active tracks
    hour: int           # 0–23
    brightness: float   # 0.0–255.0 (mean frame intensity)
    fp_rate: float      # 0.0–1.0 (fraction of short-lived tracks)

    # TODO: add derived flag fields if useful, e.g.
    #   is_peak_hour: bool = False
    #   is_nighttime: bool = False


# ── Constants ────────────────────────────────────────────────────────

# TODO: tune these thresholds empirically from VN footage
MIN_TRACK_AGE = 3        # tracks younger than this are likely FPs
NIGHT_BRIGHTNESS = 80.0  # below this → nighttime condition
PEAK_HOURS = (7, 9, 17, 20)  # morning and evening rush-hour range


# ── Main class ───────────────────────────────────────────────────────

class ContextEstimator:
    """
    Estimates the current traffic context from one frame and track history.

    Usage:
        estimator = ContextEstimator()
        state = estimator.estimate(frame, tracks)
    """

    def __init__(self) -> None:
        # TODO: add any stateful fields here if needed
        #       (e.g., rolling FP rate window, exponential smoothing)
        pass

    # ── Public API ───────────────────────────────────────────────────

    def estimate(self, frame: np.ndarray, tracks: List) -> TrafficState:
        """
        Args:
            frame  : BGR frame (H, W, 3) as np.ndarray
            tracks : list of active track objects from ByteTrack
                     Each track must expose a `.frame_id` or `.age` attribute.

        Returns:
            TrafficState with all 4 context signals filled.
        """
        # TODO: implement each sub-method below and assemble here
        density    = self._compute_density(tracks)
        hour       = self._get_hour()
        brightness = self._compute_brightness(frame)
        fp_rate    = self._compute_fp_rate(tracks)

        return TrafficState(
            density=density,
            hour=hour,
            brightness=brightness,
            fp_rate=fp_rate,
        )

    # ── Private sub-methods ──────────────────────────────────────────

    def _compute_density(self, tracks: List) -> int:
        """Return the number of currently active tracks."""
        # TODO: implement
        raise NotImplementedError

    def _get_hour(self) -> int:
        """Return the current hour of day (0–23)."""
        # TODO: implement using datetime.now().hour
        raise NotImplementedError

    def _compute_brightness(self, frame: np.ndarray) -> float:
        """Compute mean pixel intensity as a lighting proxy."""
        # TODO: implement
        # Hint: frame.mean() on grayscale channel
        raise NotImplementedError

    def _compute_fp_rate(self, tracks: List) -> float:
        """
        Estimate false-positive rate as fraction of tracks
        younger than MIN_TRACK_AGE.
        """
        # TODO: implement
        # Hint: len([t for t in tracks if t.age < MIN_TRACK_AGE]) / max(len(tracks), 1)
        raise NotImplementedError
