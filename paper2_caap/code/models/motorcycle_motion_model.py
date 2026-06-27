"""
motorcycle_motion_model.py
───────────────────────────
C2 Component: CTRV Motion Model for Motorcycles

Constant Turn Rate and Velocity (CTRV) model.
Replaces the linear Kalman filter in ByteTrack for tracks
whose class is 'motorcycle'.

State vector: x = [px, py, v, theta, omega]^T
  px    : x position (pixels)
  py    : y position (pixels)
  v     : speed (pixels/frame)
  theta : heading angle (radians)
  omega : turn rate (radians/frame)

Prediction (dt = 1 frame by default):
  px_{k+1}    = px_k + v_k * cos(theta_k) * dt
  py_{k+1}    = py_k + v_k * sin(theta_k) * dt
  v_{k+1}     = v_k
  theta_{k+1} = theta_k + omega_k * dt
  omega_{k+1} = omega_k

Reference:
  Schubert, R., Richter, E., & Wanielik, G. (2008).
  "Comparison and Evaluation of Advanced Motion Models for Vehicle Tracking."
  FUSION 2008.

Author  : Trọng Nghĩa
Paper   : Context-Aware Adaptive Perception for Mixed Traffic
Target  : IEEE T-ITS
"""

from __future__ import annotations

import numpy as np


# ── Constants ────────────────────────────────────────────────────────

STATE_DIM  = 5   # [px, py, v, theta, omega]
MEASURE_DIM = 2  # [px, py]  (observation from detection bbox center)

# Process noise (diagonal, TODO: tune from real data)
# Larger Q → model trusts measurements more
Q_DIAG = [1.0, 1.0, 0.5, 0.1, 0.05]  # TODO: tune

# Measurement noise (diagonal, TODO: tune from real data)
R_DIAG = [10.0, 10.0]  # TODO: tune


# ── Main class ───────────────────────────────────────────────────────

class CTRVMotionModel:
    """
    Extended Kalman Filter with CTRV process model.

    One instance per motorcycle track.

    Usage:
        model = CTRVMotionModel()
        model.init(bbox)           # initialise from first detection
        pred_bbox = model.predict()
        model.update(bbox)         # update with new detection
    """

    def __init__(self, dt: float = 1.0) -> None:
        """
        Args:
            dt: time step in frames (default 1.0).
        """
        self.dt = dt

        # State vector and covariance (initialised in .init())
        self.x: np.ndarray | None = None   # (5,)
        self.P: np.ndarray | None = None   # (5, 5)

        # Process and measurement noise covariance matrices
        self.Q = np.diag(Q_DIAG)           # (5, 5)
        self.R = np.diag(R_DIAG)           # (2, 2)

    # ── Public API ───────────────────────────────────────────────────

    def init(self, bbox: np.ndarray) -> None:
        """
        Initialise state from first detection bounding box.

        Args:
            bbox: [x1, y1, x2, y2] in pixels.
        """
        # TODO: compute cx, cy from bbox
        # TODO: initialise self.x = [cx, cy, 0, 0, 0]
        # TODO: initialise self.P = np.eye(STATE_DIM) * large_value
        raise NotImplementedError

    def predict(self) -> np.ndarray:
        """
        Apply CTRV prediction step.

        Returns:
            Predicted bbox [x1, y1, x2, y2] for association.
        """
        # TODO: implement F = Jacobian of CTRV at current state
        # TODO: self.x = f(self.x, self.dt)
        # TODO: self.P = F @ self.P @ F.T + self.Q
        # TODO: convert predicted state back to bbox
        raise NotImplementedError

    def update(self, bbox: np.ndarray) -> None:
        """
        EKF update step with a new detection.

        Args:
            bbox: [x1, y1, x2, y2] in pixels.
        """
        # TODO: extract measurement z = [cx, cy] from bbox
        # TODO: Kalman gain K
        # TODO: update self.x and self.P
        raise NotImplementedError

    # ── Private helpers ──────────────────────────────────────────────

    def _f(self, x: np.ndarray) -> np.ndarray:
        """CTRV nonlinear process function."""
        # TODO: implement the 5 prediction equations
        raise NotImplementedError

    def _F_jacobian(self, x: np.ndarray) -> np.ndarray:
        """Jacobian of _f with respect to state x (5×5)."""
        # TODO: compute analytically
        # Reference: Schubert et al. 2008, Appendix
        raise NotImplementedError

    def _bbox_to_state(self, bbox: np.ndarray) -> np.ndarray:
        """Convert [x1,y1,x2,y2] to observation [cx, cy]."""
        # TODO: cx = (x1+x2)/2,  cy = (y1+y2)/2
        raise NotImplementedError

    def _state_to_bbox(self, x: np.ndarray, wh: np.ndarray) -> np.ndarray:
        """Convert state [cx, cy, ...] back to [x1,y1,x2,y2]."""
        # TODO: needs stored width/height from last detection
        raise NotImplementedError
