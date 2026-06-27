"""
adaptive_controller.py
──────────────────────
C1 Component: Adaptive Parameter Controller

Reads a TrafficState and returns a Params dataclass that configures:
  - YOLO confidence threshold
  - ByteTrack lost-track buffer length
  - Motion model selector for ByteTrack

Traffic state categories (TODO: tune thresholds):
  DENSE_PEAK  : high density + peak hour
  NIGHT       : low brightness
  DEFAULT     : all other conditions

Author  : Trọng Nghĩa
Paper   : Context-Aware Adaptive Perception for Mixed Traffic
Target  : IEEE T-ITS
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal

from .context_estimator import TrafficState


# ── Data structures ──────────────────────────────────────────────────

MotionModelType = Literal["ctrv", "standard", "conservative"]


@dataclass
class Params:
    """Runtime parameters for detector + tracker."""
    yolo_conf: float           # YOLO confidence threshold  (0.0–1.0)
    buffer_len: int            # ByteTrack lost-track buffer (frames)
    motion_model: MotionModelType  # which motion model to activate


class TrafficCondition(Enum):
    """Categorical traffic condition inferred from TrafficState."""
    DENSE_PEAK   = auto()
    NIGHT        = auto()
    DEFAULT      = auto()
    # TODO: add more categories if experiments reveal distinct clusters
    #       e.g., SPARSE_NIGHT, RAINY (if rain detection is added)


# ── Thresholds (tune after baseline experiments) ─────────────────────

DENSITY_THRESHOLD  = 30    # TODO: determine from VN footage histogram
BRIGHTNESS_NIGHT   = 80.0  # TODO: verify against actual nighttime frames
PEAK_HOURS         = range(7, 21)  # TODO: narrow if data shows tighter peaks


# ── Parameter table (one row per condition) ──────────────────────────
# Format: TrafficCondition → Params
# TODO: all numeric values are initial guesses — tune via ablation

PARAM_TABLE: dict[TrafficCondition, Params] = {
    TrafficCondition.DENSE_PEAK: Params(
        yolo_conf=0.35,
        buffer_len=45,
        motion_model="ctrv",
    ),
    TrafficCondition.NIGHT: Params(
        yolo_conf=0.55,
        buffer_len=20,
        motion_model="conservative",
    ),
    TrafficCondition.DEFAULT: Params(
        yolo_conf=0.45,
        buffer_len=30,
        motion_model="standard",
    ),
}


# ── Main class ───────────────────────────────────────────────────────

class AdaptiveController:
    """
    Maps a TrafficState to a Params object for the current frame.

    Usage:
        controller = AdaptiveController()
        params = controller.get_params(state)
    """

    def get_params(self, state: TrafficState) -> Params:
        """
        Args:
            state: TrafficState from ContextEstimator.

        Returns:
            Params for the current frame.
        """
        condition = self._classify(state)
        return PARAM_TABLE[condition]

    # ── Private ──────────────────────────────────────────────────────

    def _classify(self, state: TrafficState) -> TrafficCondition:
        """
        Map a TrafficState to a TrafficCondition category.
        Priority: NIGHT > DENSE_PEAK > DEFAULT
        """
        # TODO: implement classification logic
        # Hint: check state.brightness, state.density, state.hour
        raise NotImplementedError
