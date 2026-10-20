"""
tests/synthetic.py
──────────────────
Thin re-export: the trajectory generators live in code/utils/synthetic.py
as reusable synthetic inputs for the tracker tests.
"""

from code.utils.synthetic import (  # noqa: F401
    CLASS_CAR,
    CLASS_MOTORCYCLE,
    CLASS_BUS,
    CLASS_TRUCK,
    straight,
    constant_turn,
    weaving,
    centers_to_bboxes,
    to_detections,
)
