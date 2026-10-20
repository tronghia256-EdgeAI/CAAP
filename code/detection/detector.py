"""YOLO detector with explicit local weights and canonical vehicle class IDs."""
from __future__ import annotations

from pathlib import Path

import numpy as np

DETECTOR_CONF = 0.1
PROJECT_CLASSES = {'car': 0, 'motorcycle': 1, 'bus': 2, 'truck': 3, 'accident': 4}


class Detector:
    """Return frame-native N×6 [x1,y1,x2,y2,score,class_id] detections.

    A missing checkpoint is an error. The wrapper never substitutes a different
    model or reuses a saved ROI from the retired evaluation dataset.
    """

    def __init__(self, weights_path: str, img_size: int = 640,
                 task: str | None = None) -> None:
        weights = Path(weights_path)
        if not weights.is_file():
            raise FileNotFoundError(f'Detector checkpoint not found: {weights}')
        if img_size <= 0:
            raise ValueError('img_size must be positive')
        from ultralytics import YOLO

        self.img_size = img_size
        self.model = YOLO(str(weights), **({'task': task} if task else {}))
        names = self.model.names
        items = names.items() if isinstance(names, dict) else enumerate(names)
        self.remap = {mid: PROJECT_CLASSES[name.lower()] for mid, name in items
                      if name.lower() in PROJECT_CLASSES}
        if not self.remap:
            raise ValueError(f'Model classes {names} contain no supported vehicle classes')

    def detect(self, frame: np.ndarray) -> np.ndarray:
        results = self.model(frame, conf=DETECTOR_CONF, imgsz=self.img_size, verbose=False)
        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            return np.empty((0, 6), dtype=float)
        xyxy = boxes.xyxy.cpu().numpy()
        conf = boxes.conf.cpu().numpy()
        classes = boxes.cls.cpu().numpy().astype(int)
        keep = np.array([cid in self.remap for cid in classes], dtype=bool)
        if not keep.any():
            return np.empty((0, 6), dtype=float)
        canonical = np.array([self.remap[cid] for cid in classes[keep]])
        return np.column_stack([xyxy[keep], conf[keep], canonical]).astype(float)
