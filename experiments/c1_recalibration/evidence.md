# C1 density threshold, recalibrated outside the GT segments (pre-registered)

**Problem.** Under the paper run v5 (best.pt with ROI), C1's controller never
left its DEFAULT row.

- `DENSE_PEAK` needs the tracker's own density EMA to reach
  `density_threshold`, which is 30. That value was set for the old full-frame
  yolo11_vn@1280 track counts, about 46 per frame on dense.
- Under v5 the density EMA peaked at 29 on dense at 640 and at 24 at 448.
  Brightness never fell below the NIGHT bound of 80 (minimum 89.7).
- In DEFAULT, `motion_model` is "standard". That turns CTRV off, and with it
  C2's gate and NSA (`adaptive_bytetrack.py`, line 284).
- The C1 arms were therefore ByteTrack at a 0.45 confirmation threshold with
  the linear model. Their IDF1 gain over C2 is a threshold effect, and C1's
  premise was not tested (finding by caap-b5, verified on
  `{640,448}/context_c1_ctrv_gate.json`).

**Decision (Nghĩa, 2026-10-13).** Recalibrate on frames outside the GT,
using a rule fixed in advance. No retuning on the evaluation segments.

**Rule.**

- Per input size, the threshold is the 75th percentile of the
  `c1_ctrv_gate` arm's own density EMA (the value the controller compares)
  over every NKKN frame outside the three GT segments. That is 9,500 of the
  11,300 frames run.
- The data source is v5's context log for that size, which recorded the
  DEFAULT regime.
- Computed by `c1_calibration.py`, which sits outside `code/` during the
  code freeze and moves to `code/scripts/` afterwards. Output:
  `calibration.json`.

**Thresholds, fixed before any C1 result under them exists.**

| Input size | p50 | p75 = threshold | p90 | p99 | Share of frames ≥ threshold: dense / freeflow / mixed |
|---|---:|---:|---:|---:|---|
| 640 | 6 | **18** | 21 | 27 | 0.84 / 0.00 / 0.31 |
| 448 | 5 | **14** | 17 | 22 | 0.84 / 0.00 / 0.35 |
| 960 | 7 | **21** | 26 | 32 | 0.87 / 0.00 / 0.27 |
| 1280 | 7 | **23** | 29 | 35 | 0.92 / 0.00 / 0.27 |

The last column is computed from the DEFAULT-regime density only. No GT and
no metric is involved. Once the controller switches, density shifts
(confirmation threshold 0.50 and CTRV in `DENSE_PEAK`), so the re-run must
log the actual regime per frame.

**In-run rule (2026-10-13, before the final run).** The Pareto run's C1 arm
did switch at 960 and 1280 (its density reached 34 and 36 under the old
threshold of 30), so its context log is not DEFAULT-regime density. The rule
is therefore applied inside `run_roi_paper.py` (`c1_calibrate`):

- after caching, `c1_ctrv_gate` is replayed with an infinite density
  threshold, so it never enters `DENSE_PEAK`;
- the threshold is the same percentile over the same frames, written to
  `{size}/c1_threshold.json` before any C1 arm runs;
- the frozen C1 configs carry `density_threshold: null`, and the C1 context
  logs record the regime applied in each frame.

On the v5 caches the probe's density equals v5's logged C1 density frame for
frame at 640 and 448, and gives 18 and 14. The 960 and 1280 rows above come
from the probe on the Pareto caches. The yolo11_vn@1280 threshold comes from
its own run by the same rule.
