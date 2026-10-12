# Detector operating points: the accuracy cost of real time

**Question.** How much tracking accuracy does the real-time detector operating
point cost on motorcycle-dominant footage, and where does the cost come from?

**Method.** `python -m code.scripts.operating_points data/processed/paper_runs/best85_roi_20261013_v5`
writes `operating_points.json`. It scores the three reconciled ROI GTs
(`docs/GT_RECONCILED_20261013.md`) with the repository evaluator at IoU 0.5.
Three operating points are compared:

- **yolo11_vn@1280\*** — the old cached tracks. Tracking ran on the full frame,
  and the ROI was applied only at scoring time. The GTs were seeded from these
  trackers' outputs, so this row is favoured by the seed (see
  `experiments/seed_bias/evidence.md`).
- **best.pt@640** and **best.pt@448** — paper run v5: ROI mask before the
  detector, state expiry, one detection cache shared by all trackers.

**Motorcycle IDF1.** Columns are baseline / C2 (ctrv_gate_nsa) / C1+C2
(c1_ctrv_gate) / OC-SORT at matched thresholds (0.5 + BYTE).

| Operating point | dense | freeflow | mixed |
|---|---|---|---|
| yolo11_vn@1280\* | 0.866 / 0.911 / 0.900 / 0.785 | 0.932 / 0.962 / 0.894 / 0.888 | 0.986 / 0.950 / 0.958 / 0.897 |
| best.pt@640 | 0.590 / 0.602 / 0.610 / 0.626 | 0.693 / 0.698 / 0.723 / 0.726 | 0.726 / 0.729 / 0.748 / 0.757 |
| best.pt@448 | 0.477 / 0.499 / 0.517 / 0.551 | 0.516 / 0.536 / 0.558 / 0.588 | 0.565 / 0.574 / 0.587 / 0.646 |

**The drop is driven by misses.** For C2 on dense, FN / FP are:

| Operating point | FN | FP |
|---|---:|---:|
| yolo11_vn@1280\* | 883 | 1,247 |
| best.pt@640 | 9,870 | 1,148 |
| best.pt@448 | 12,263 | 883 |

**Miss rate by GT box height.** C2 on dense, per-frame one-to-one matching
(800×450 frames):

| Operating point | < 20 px | 20–40 px | ≥ 40 px |
|---|---:|---:|---:|
| yolo11_vn@1280\* | 0.10 | 0.03 | 0.03 |
| best.pt@640 | 0.99 | 0.47 | 0.12 |
| best.pt@448 | 1.00 | 0.71 | 0.20 |

Small motorcycles are common in the GT, so these misses weigh heavily:

| Segment | < 20 px | 20–40 px | ≥ 40 px |
|---|---:|---:|---:|
| dense | 28% | 43% | 29% |
| freeflow | 38% | 38% | 24% |
| mixed | 22% | 47% | 31% |

**Findings.**

1. **The real-time operating points lose small motorcycles.**
   - At 640, nearly every motorcycle under 20 px and about half of those at
     20–40 px are missed.
   - At 448, every motorcycle under 20 px and about two thirds of those at
     20–40 px are missed.
   - Motorcycles of 40 px and taller are tracked almost as well as at 1280.

   The input is 800 px wide, so 640 downscales it, whereas 1280 upscaled it.
2. **The tracker ordering is the same at 640 and 448.** C1+C2 beats C2, which
   beats baseline, and OC-SORT at matched thresholds leads.
3. **The detector-level seed caveat does not explain the drop.** Between 59%
   and 92% of best.pt's unmatched predictions lie where the GT has no box of
   any class. Some of these may be real vehicles: the GTs were seeded from
   yolo11_vn trackers, so boxes only best.pt finds were never shown to a
   reviewer. Even so, FP is an order of magnitude smaller than FN.

**Not covered here.**

- Latency at these operating points: v5's benchmark ran on a throttled CPU
  (41–49% processor performance) and is not reportable.
- Whether best.pt at a larger input (960, 1280) recovers the small motorcycles.
