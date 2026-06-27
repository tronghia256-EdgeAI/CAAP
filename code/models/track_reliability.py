"""
track_reliability.py
─────────────────────
C3 Component: Dual-Task Track Reliability Scorer

Assigns a scalar reliability score S ∈ [0, 1] to each active track.
The score combines four components:

  S(τ) = w1·age(τ) + w2·consistency(τ) + w3·smoothness(τ) + w4·class_stability(τ)

  age(τ)             : normalised consecutive confirmed-detection count
  consistency(τ)     : detection hit rate over last WINDOW_SIZE frames
  smoothness(τ)      : inverse of predicted-vs-detected IoU variance
  class_stability(τ) : fraction of frames with the dominant class label

Two task-specific thresholds split the output:
  τ_acc   : high threshold → precision branch (accident detection)
  τ_mappo : lower threshold → recall branch   (MAPPO observations)

Author  : Trọng Nghĩa
Paper   : Context-Aware Adaptive Perception for Mixed Traffic
Target  : IEEE T-ITS
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np


# ── Weights (must sum to 1.0) ────────────────────────────────────────
# TODO: verify empirically; initial guess from domain intuition

W_AGE             = 0.20
W_CONSISTENCY     = 0.30
W_SMOOTHNESS      = 0.30
W_CLASS_STABILITY = 0.20

assert abs(W_AGE + W_CONSISTENCY + W_SMOOTHNESS + W_CLASS_STABILITY - 1.0) < 1e-6


# ── Downstream thresholds ────────────────────────────────────────────
# TODO: tune via ablation study (Section V)

THRESHOLD_ACCIDENT = 0.70   # τ_acc   : precision branch
THRESHOLD_MAPPO    = 0.40   # τ_mappo : recall branch


# ── Window size for consistency / class stability ────────────────────

WINDOW_SIZE = 10   # last N frames


# ── Data structures ──────────────────────────────────────────────────

@dataclass
class ReliabilityScore:
    """Full breakdown of a track's reliability."""
    total: float                     # final weighted score (0.0–1.0)
    age_component: float
    consistency_component: float
    smoothness_component: float
    class_stability_component: float

    # Downstream flags
    reliable_for_accident: bool = field(init=False)
    reliable_for_mappo: bool    = field(init=False)

    def __post_init__(self) -> None:
        self.reliable_for_accident = self.total >= THRESHOLD_ACCIDENT
        self.reliable_for_mappo    = self.total >= THRESHOLD_MAPPO


# ── Main class ───────────────────────────────────────────────────────

class TrackReliabilityScorer:
    """
    Scores all active tracks and returns a dict of ReliabilityScore objects.

    Usage:
        scorer = TrackReliabilityScorer()
        scores = scorer.score_all(tracks)
        accident_tracks = [t for t, s in scores.items() if s.reliable_for_accident]
        mappo_tracks    = [t for t, s in scores.items() if s.reliable_for_mappo]
    """

    def score_all(self, tracks: List) -> Dict[int, ReliabilityScore]:
        """
        Args:
            tracks: list of active track objects.
                    Each track must expose: .track_id, .age,
                    .hit_history (List[bool]), .iou_history (List[float]),
                    .class_history (List[str]).

        Returns:
            Dict mapping track_id → ReliabilityScore.
        """
        # TODO: iterate over tracks and call .score() for each
        raise NotImplementedError

    def score(self, track) -> ReliabilityScore:
        """Score a single track."""
        age_c   = self._age_component(track)
        cons_c  = self._consistency_component(track)
        smooth_c = self._smoothness_component(track)
        cls_c   = self._class_stability_component(track)

        total = (W_AGE * age_c
                 + W_CONSISTENCY * cons_c
                 + W_SMOOTHNESS * smooth_c
                 + W_CLASS_STABILITY * cls_c)

        return ReliabilityScore(
            total=float(np.clip(total, 0.0, 1.0)),
            age_component=age_c,
            consistency_component=cons_c,
            smoothness_component=smooth_c,
            class_stability_component=cls_c,
        )

    # ── Component calculators ────────────────────────────────────────

    def _age_component(self, track) -> float:
        """
        Normalised track age.
        Older tracks → higher score.
        TODO: define max_age for normalisation (e.g., 30 frames = 1.0)
        """
        raise NotImplementedError

    def _consistency_component(self, track) -> float:
        """
        Detection hit rate over the last WINDOW_SIZE frames.
        hit_history: list of bool (True = detected, False = predicted-only).
        """
        raise NotImplementedError

    def _smoothness_component(self, track) -> float:
        """
        Inverse of IoU variance between predicted and detected boxes.
        iou_history: list of float IoU values per frame.
        Low variance → high smoothness → high score.
        """
        raise NotImplementedError

    def _class_stability_component(self, track) -> float:
        """
        Fraction of frames where the detected class equals the mode class.
        class_history: list of class label strings.
        """
        raise NotImplementedError
