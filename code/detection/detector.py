"""
code/detection/detector.py
───────────────────────────
YOLOv8 detector wrapper.

Provides a thin interface so the rest of the pipeline does not
import ultralytics directly everywhere.

Author  : Trọng Nghĩa
"""

from __future__ import annotations

import numpy as np

# TODO: from ultralytics import YOLO


class Detector:
    """
    Wraps YOLOv8 inference.

    Usage:
        detector = Detector(weights='weights/yolov8_vn.pt')
        detections = detector.detect(frame, conf_threshold=0.45)
    """

    def __init__(self, weights_path: str) -> None:
        # TODO: self.model = YOLO(weights_path)
        raise NotImplementedError

    def detect(self, frame: np.ndarray, conf_threshold: float = 0.45):
        """
        Args:
            frame          : BGR frame (H, W, 3)
            conf_threshold : minimum confidence score (from AdaptiveController)

        Returns:
            detections in ByteTrack-compatible format
            (numpy array of [x1, y1, x2, y2, score, class_id])
        """
        # TODO: run self.model(frame, conf=conf_threshold)
        # TODO: convert to numpy array
        raise NotImplementedError
