"""
code/pipeline.py
─────────────────
Main inference pipeline — ties all components together.

Data flow:
    Camera frame
        → ContextEstimator   → TrafficState
        → AdaptiveController → Params
        → Detector           → raw detections (filtered by Params.yolo_conf)
        → AdaptiveBYTETracker→ active tracks  (CTRV or Kalman by class)
        → TrackReliabilityScorer → ReliabilityScore per track
        → AccidentClassifier (tracks reliable_for_accident)
        → TelegramAlert      (if severity MINOR or SEVERE)
        → MAPPO Observations (tracks reliable_for_mappo)

Author  : Trọng Nghĩa
"""

from __future__ import annotations

import numpy as np

from code.models import (
    ContextEstimator,
    AdaptiveController,
    TrackReliabilityScorer,
)
from code.tracker.adaptive_bytetrack import AdaptiveBYTETracker
from code.detection.detector import Detector
from code.detection.accident_classifier import AccidentClassifier, Severity
from code.alert.telegram_alert import TelegramAlert


class Pipeline:
    """
    End-to-end adaptive perception pipeline.

    Usage:
        pipeline = Pipeline.from_config('configs/default.yaml')
        for frame in video_source:
            result = pipeline.process(frame)
    """

    def __init__(
        self,
        detector: Detector,
        tracker: AdaptiveBYTETracker,
        context_estimator: ContextEstimator,
        adaptive_controller: AdaptiveController,
        reliability_scorer: TrackReliabilityScorer,
        accident_classifier: AccidentClassifier,
        alert: TelegramAlert,
    ) -> None:
        self.detector            = detector
        self.tracker             = tracker
        self.context_estimator   = context_estimator
        self.adaptive_controller = adaptive_controller
        self.reliability_scorer  = reliability_scorer
        self.accident_classifier = accident_classifier
        self.alert               = alert

    @classmethod
    def from_config(cls, config_path: str) -> "Pipeline":
        """Build pipeline from YAML config file."""
        # TODO: load configs/default.yaml
        # TODO: instantiate all components with config values
        raise NotImplementedError

    def process(self, frame: np.ndarray) -> dict:
        """
        Process one frame end-to-end.

        Returns:
            {
              'tracks_accident' : list of track objects (reliable_for_accident),
              'tracks_mappo'    : list of track objects (reliable_for_mappo),
              'scores'          : dict {track_id: ReliabilityScore},
              'params'          : Params used this frame,
              'state'           : TrafficState this frame,
            }
        """
        # TODO: implement step by step following the data flow above
        raise NotImplementedError
