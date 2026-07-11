"""
code/detection/detector.py
───────────────────────────
YOLO11 (Ultralytics) detector wrapper.

Provides a thin interface so the rest of the pipeline does not
import ultralytics directly everywhere (lazy import — tracker tests
never load torch).

IMPORTANT (D3): the detector always runs at a LOW fixed confidence
(DETECTOR_CONF = 0.1). The adaptive confidence from AdaptiveController
is applied as the tracker's track_thresh — BYTE's second association
stage *needs* the low-score detections, so filtering here would
silently disable half the algorithm.

Fallback (D6): if the VN-trained weights are missing, fall back to
COCO-pretrained yolo11n and remap COCO ids → project ids
(car 2→0, motorcycle 3→1, bus 5→2, truck 7→3). COCO has no accident
class, so the accident branch is disabled upstream in that case.

Project class ids: 0 car, 1 motorcycle, 2 bus, 3 truck, 4 accident.

Author  : Trọng Nghĩa
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

DETECTOR_CONF = 0.1   # fixed low conf — see module docstring (D3)

# Prefer the already-downloaded copy in weights/ (gitignored); a bare
# model name makes ultralytics auto-download to the CWD.
COCO_FALLBACK_WEIGHTS = (
    "weights/yolo11n.pt" if Path("weights/yolo11n.pt").exists() else "yolo11n.pt"
)
COCO_TO_PROJECT = {2: 0, 3: 1, 5: 2, 7: 3}   # car, motorcycle, bus, truck


class Detector:
    """
    Wraps YOLO11 inference.

    Usage:
        detector = Detector(weights='weights/yolo11_vn.pt')
        detections = detector.detect(frame)     # N×6 numpy
    """

    def __init__(self, weights_path: str, img_size: int = 640) -> None:
        from ultralytics import YOLO  # lazy: only pipeline runs need torch

        self.img_size = img_size
        if Path(weights_path).exists():
            self.model = YOLO(weights_path)
            self.using_coco_fallback = False
        else:
            logger.warning(
                "Weights %s not found — falling back to COCO-pretrained %s. "
                "Only car/motorcycle/bus/truck are detected; the accident "
                "class is unavailable in this mode.",
                weights_path, COCO_FALLBACK_WEIGHTS,
            )
            self.model = YOLO(COCO_FALLBACK_WEIGHTS)
            self.using_coco_fallback = True

    def detect(self, frame: np.ndarray) -> np.ndarray:
        """
        Args:
            frame: BGR frame (H, W, 3)

        Returns:
            N×6 numpy [x1, y1, x2, y2, score, class_id] in frame-native
            pixels, project class ids.
        """
        results = self.model(frame, conf=DETECTOR_CONF, imgsz=self.img_size,
                             verbose=False)
        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            return np.empty((0, 6))

        xyxy = boxes.xyxy.cpu().numpy()
        conf = boxes.conf.cpu().numpy()
        cls = boxes.cls.cpu().numpy().astype(int)

        if self.using_coco_fallback:
            keep = np.array([c in COCO_TO_PROJECT for c in cls])
            if not keep.any():
                return np.empty((0, 6))
            xyxy, conf = xyxy[keep], conf[keep]
            cls = np.array([COCO_TO_PROJECT[c] for c in cls[keep]])

        return np.column_stack([xyxy, conf, cls]).astype(float)
