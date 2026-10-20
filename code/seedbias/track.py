"""
code/seedbias/track.py
──────────────────────
Run the evaluated trackers (Roboflow `trackers` 2.6.1, library defaults) on
cached detections, one evaluation class at a time (PROTOCOL.md A2).
"""

from __future__ import annotations

import numpy as np
import supervision as sv
import trackers

# name → (factory(frame_rate), minimum detection confidence fed to the tracker)
TRACKERS = {
    # SORT has no low-score stage; feed only detections that pass its own activation threshold.
    'sort': (lambda fr: trackers.SORTTracker(frame_rate=fr), 0.25),
    # A5 item 10 sensitivity only: SORT fed every cached detection (conf >= 0.05).
    'sort_all': (lambda fr: trackers.SORTTracker(frame_rate=fr), 0.0),
    'bytetrack': (lambda fr: trackers.ByteTrackTracker(frame_rate=fr), 0.0),
    'ocsort': (lambda fr: trackers.OCSORTTracker(frame_rate=fr), 0.0),
    # No camera-motion compensation: frames are not available offline.
    'botsort': (lambda fr: trackers.BoTSORTTracker(frame_rate=fr, enable_cmc=False), 0.0),
}


def run_tracker(name: str, dets: np.ndarray, frame_rate: float, n_frames: int) -> np.ndarray:
    """dets [frame, x1, y1, x2, y2, conf] → tracks [frame, id, x1, y1, x2, y2] for frames 1..n_frames."""
    make, min_conf = TRACKERS[name]
    tracker = make(frame_rate)
    dets = np.asarray(dets, dtype=float).reshape(-1, 6)
    dets = dets[dets[:, 5] >= min_conf]
    order = np.argsort(dets[:, 0], kind='stable')
    frames, starts = np.unique(dets[order, 0], return_index=True)
    by_frame = dict(zip(frames.astype(int).tolist(), np.split(order, starts[1:])))
    rows = []
    for f in range(1, n_frames + 1):
        d = dets[by_frame.get(f, [])]
        out = tracker.update(sv.Detections(xyxy=d[:, 1:5].reshape(-1, 4), confidence=d[:, 5],
                                           class_id=np.zeros(len(d), dtype=int)))
        if len(out) == 0:
            continue
        keep = np.asarray(out.tracker_id) >= 0
        if keep.any():
            rows.append(np.column_stack([np.full(keep.sum(), f), np.asarray(out.tracker_id)[keep],
                                         out.xyxy[keep]]))
    return np.concatenate(rows).astype(float) if rows else np.empty((0, 6))
