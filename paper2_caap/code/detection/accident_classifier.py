"""
code/detection/accident_classifier.py
────────────────────────────────────────
EfficientNet-B0 severity classifier.

3-class output: non-accident / minor / severe

Input: cropped ROI from a track flagged as accident by YOLOv8.
Output: severity label + confidence.

Author  : Trọng Nghĩa
"""

from __future__ import annotations

from enum import Enum
import numpy as np

# TODO: import timm, torch, torchvision transforms


class Severity(Enum):
    NON_ACCIDENT = 0
    MINOR        = 1
    SEVERE       = 2


# Labels for relabeling reference (from CLAUDE.md):
#   SEVERE : xe lật, người bị văng, >2 xe liên quan, xe không di chuyển được
#   MINOR  : va chạm nhẹ, xe tự di chuyển được sau va chạm


class AccidentClassifier:
    """
    Wraps EfficientNet-B0 fine-tuned on VN accident dataset.

    Usage:
        classifier = AccidentClassifier('weights/efficientnet_severity.pt')
        severity, conf = classifier.classify(roi_frame)
    """

    def __init__(self, weights_path: str) -> None:
        # TODO: load EfficientNet-B0 from timm
        # TODO: load weights
        # TODO: set to eval mode
        raise NotImplementedError

    def classify(self, roi: np.ndarray) -> tuple[Severity, float]:
        """
        Args:
            roi: cropped accident region, BGR (H, W, 3)

        Returns:
            (Severity enum, confidence float 0.0–1.0)
        """
        # TODO: preprocess → tensor → model inference → argmax
        raise NotImplementedError
