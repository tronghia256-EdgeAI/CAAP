"""
code/evaluation/metrics.py
───────────────────────────
All evaluation metrics for Paper 2.

Tracking : MOTA, IDF1, Track Fragmentation Rate
Detection : Precision, Recall, F1, mAP@0.5
Severity  : Accuracy, Confusion Matrix (3-class)
System    : FPS, Latency

Reference: Bernardin & Stiefelhagen, EURASIP 2008 (CLEAR MOT metrics)

Author  : Trọng Nghĩa
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np


# ── Result containers ────────────────────────────────────────────────

@dataclass
class TrackingMetrics:
    mota: float                  # Multiple Object Tracking Accuracy
    idf1: float                  # ID F1 Score
    track_fragmentation_rate: float  # ID switches / GT tracks

@dataclass
class DetectionMetrics:
    precision: float
    recall: float
    f1: float
    map50: float                 # mAP @ IoU 0.5

@dataclass
class SeverityMetrics:
    accuracy: float
    confusion_matrix: np.ndarray  # (3, 3)

@dataclass
class SystemMetrics:
    fps: float
    latency_ms: float


# ── Metric calculators ───────────────────────────────────────────────

def compute_tracking_metrics(pred_tracks, gt_tracks) -> TrackingMetrics:
    """
    Args:
        pred_tracks: list of predicted track sequences
        gt_tracks  : list of ground-truth track sequences

    Returns:
        TrackingMetrics
    """
    # TODO: implement MOTA, IDF1
    # Hint: use py-motmetrics library as reference,
    #       but understand each formula before using it
    raise NotImplementedError


def compute_detection_metrics(pred_boxes, gt_boxes, iou_threshold: float = 0.5) -> DetectionMetrics:
    """
    Args:
        pred_boxes: list of [x1,y1,x2,y2,conf,class_id]
        gt_boxes  : list of [x1,y1,x2,y2,class_id]

    Returns:
        DetectionMetrics
    """
    # TODO: implement TP/FP/FN counting, then P/R/F1/mAP
    raise NotImplementedError


def compute_severity_metrics(pred_labels: List[int], gt_labels: List[int]) -> SeverityMetrics:
    """
    Args:
        pred_labels: list of predicted severity class (0/1/2)
        gt_labels  : list of ground-truth severity class

    Returns:
        SeverityMetrics with accuracy and 3×3 confusion matrix
    """
    # TODO: accuracy = correct / total
    # TODO: confusion matrix (sklearn.metrics.confusion_matrix is fine to use here)
    raise NotImplementedError


def compute_iou(box_a: np.ndarray, box_b: np.ndarray) -> float:
    """Compute IoU between two boxes [x1,y1,x2,y2]."""
    # TODO: implement intersection / union
    raise NotImplementedError
