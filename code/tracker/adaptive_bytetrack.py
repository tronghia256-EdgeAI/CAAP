"""
code/tracker/adaptive_bytetrack.py
────────────────────────────────────
Modified ByteTrack that integrates C1 + C2.

Wraps the original ByteTrack (ifzhang/ByteTrack) and adds:
  1. Receives Params from AdaptiveController each frame → applies conf + buffer
  2. Routes each track to CTRVMotionModel (motorcycle) or default Kalman (others)

Step-by-step reading order before implementing this file:
  1. ByteTrack/yolox/tracker/byte_tracker.py   -- main tracker class
  2. ByteTrack/yolox/tracker/kalman_filter.py  -- linear Kalman implementation
  3. ByteTrack/yolox/tracker/basetrack.py      -- track state machine

Author  : Trọng Nghĩa
"""

from __future__ import annotations

# TODO: once ByteTrack is cloned, add:
# from ByteTrack.yolox.tracker.byte_tracker import BYTETracker, STrack
# from ..models import CTRVMotionModel, Params


class AdaptiveBYTETracker:
    """
    ByteTrack wrapper with:
      - Dynamic confidence threshold (from Params)
      - Dynamic buffer length     (from Params)
      - Class-conditioned motion model (CTRV for motorcycle, Kalman for others)

    Usage:
        tracker = AdaptiveBYTETracker(args)
        tracks = tracker.update(detections, params)
    """

    def __init__(self, args) -> None:
        # TODO: init original BYTETracker with args
        # TODO: keep a dict {track_id: CTRVMotionModel} for motorcycle tracks
        raise NotImplementedError

    def update(self, detections, params):  # params: Params
        """
        Args:
            detections : output from YOLOv8 inference
            params     : Params from AdaptiveController

        Returns:
            List of active STrack objects with reliability hooks added.
        """
        # TODO:
        # 1. Apply params.yolo_conf as detection filter threshold
        # 2. Apply params.buffer_len to tracker lost-track buffer
        # 3. For each newly created motorcycle track → init CTRVMotionModel
        # 4. For each predict step   → dispatch to CTRV or Kalman by class
        # 5. Return updated tracks
        raise NotImplementedError

    # ── Private ──────────────────────────────────────────────────────

    def _predict_with_class_model(self, track, params) -> None:
        """Select and apply the correct motion model for this track."""
        # TODO: if track.class == 'motorcycle' and params.motion_model != 'standard'
        #           use CTRVMotionModel
        #       else
        #           use original Kalman
        raise NotImplementedError
