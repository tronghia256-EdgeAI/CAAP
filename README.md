# Context-Aware Adaptive Perception for Mixed Traffic

**Author:** Trọng Nghĩa
**Target:** ICRA 2027 (primary) · IEEE IV 2027 (backup)
**Status:** C2 validated on human ground truth (`experiments/gt_ablation/evidence.md`) — C1 and C3 need re-tuning against GT before they can be claimed

A perception pipeline for motorcycle-dominant mixed traffic (~94% motorcycles
on Vietnamese urban roads) that adapts its detection/tracking parameters to
real-time traffic context and serves two downstream tasks — accident
detection and MAPPO-based signal control — without task-specific retuning.

## Contributions

| | Contribution | Where |
|---|---|---|
| **C1** | Context Estimator + Adaptive Parameter Controller — 4 traffic signals (density, hour, brightness, FP rate) drive per-frame tracker parameters, with EMA smoothing + 15-frame hysteresis | `code/models/context_estimator.py`, `code/models/adaptive_controller.py` |
| **C2** | Class-conditioned motion model — motorcycles get a CTRV EKF (state `[x, y, v, θ, ω]`, Schubert et al. 2008) inside ByteTrack; cars/trucks keep the linear Kalman filter | `code/models/motorcycle_motion_model.py`, `code/tracker/adaptive_bytetrack.py` |
| **C3** | Dual-task track reliability score — one scoring function, two thresholds: high τ_acc for accident-alert precision, lower τ_mappo for MAPPO observation recall | `code/models/track_reliability.py` |

## Quick start

```powershell
# Windows, Python 3.10
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt

# Run the test suite (134 tests) — from the repo root
pytest tests/ -q

# Run an ablation experiment on the synthetic benchmark (no weights/footage needed)
python -m code.scripts.run_experiment --config configs/exp1_C2.yaml --synthetic --save-metrics

# Run on real footage (COCO yolo11n fallback engages if VN weights are absent)
python -m code.scripts.run_experiment --config configs/baseline.yaml --video data/raw/videos/<clip>.mp4 --save-metrics
```

> Run scripts as modules (`python -m code.scripts.run_experiment`) from the
> repo root — the project package is named `code`, which shadows a stdlib
> module (see `code/__init__.py`).

## GT review

For the **Accident / Vehicle detection dataset**, open
`review_accident_dataset.cmd` to review related images, edit boxes, and publish
source-preserving grouped splits. The prepared version remains a draft until
review and provenance confirmation. See [dataset review instructions](docs/ACCIDENT_DATASET_REVIEW_WORKFLOW.md).

For development training on **Kaggle**, use
[CAAP_YOLO11_Kaggle.ipynb](notebooks/CAAP_YOLO11_Kaggle.ipynb) and the private
upload ZIP prepared by `python -m code.scripts.package_kaggle_detection`.
See [Kaggle setup and output instructions](docs/KAGGLE_DETECTOR_TRAINING.md).
Development validation metrics are not independent paper test results.

Double-click `review_gt.cmd`, or run
`python -m code.scripts.gt_review_app`. The local reviewer saves human CUT/KEEP
decisions, resumes pending candidates, and generates a new GT plus ablation
scores after completion. See [the review workflow](docs/GT_REVIEW_WORKFLOW.md).

For **mixed**, open `review_gt_mixed.cmd`: review merge/split/duplicate/short-track
questions, edit boxes/classes in the local video viewer, and audit all 600 frames.
It preserves the baseline seed and saves decisions plus an edit journal before
generating a reviewed GT and ablation report.

## Ablation configs

| Config file | C1 | C2 | C3 | Maps to |
|---|---|---|---|---|
| `configs/baseline.yaml` | ✗ | ✗ | ✗ | Exp 0 — vanilla YOLO11 + ByteTrack |
| `configs/exp1_C2.yaml` | ✗ | ✓ | ✗ | Exp 1 — +CTRV motion model |
| `configs/exp2_C1C2.yaml` | ✓ | ✓ | ✗ | Exp 2 — +context adaptation |
| `configs/exp3_C1C2C3.yaml` / `default.yaml` | ✓ | ✓ | ✓ | Exp 3 — proposed method |

## Results on human GT

600 human-labelled frames of the densest window (~47 tracks/frame), identical
detections for every row. Motorcycle class — the one C2 is about:

| variant | MOTA | IDF1 | ID switches |
|---|---|---|---|
| baseline (linear KF) | 0.843 | 0.844 | 189 |
| + CTRV | 0.857 | 0.850 | 158 |
| + CTRV + NSA | 0.869 | 0.869 | 123 |
| + CTRV + gating | 0.854 | 0.868 | 182 |
| **+ CTRV + gating + NSA (C2)** | **0.893** | **0.933** | **29** |
| + C1 (Exp 2, GT-tuned) | 0.878 | 0.909 | 99 |

**C2 vs baseline: IDF1 0.844 → 0.933, ID switches −85%** — but see the
caveat below before quoting these.

> ⚠️ **Identity numbers are provisional.** The GT contains ~74 over-merged
> identities (22% of tracks, two verified by eye): several motorcycles
> chained into one. This inflates C2 specifically, because an over-merged
> GT rewards any tracker that bridges occlusion gaps — which is what C2's
> uncertainty gate does. Splitting the flagged joins moves the margin from
> +0.089 to as little as +0.014 IDF1, with baseline *improving* and C2
> *degrading*. C2 still leads on every variant, but the magnitude is
> unsettled pending a GT re-review. Detection metrics, latency and the
> C1/C3 findings are unaffected. See `experiments/gt_qa/WRONG_MERGES.md`.

Three things this measurement changed, all written up with mechanisms in
`experiments/gt_ablation/evidence.md`:

- **Gating and NSA are super-additive.** Gating *alone* makes identity worse
  (182 vs 158 switches): without NSA the EKF over-smooths, so the innovation
  ellipse is mis-centred and rescues land on the wrong detection. C2 has to be
  reported as one mechanism, not two.
- **C1's shipped tuning was harmful, and C1 itself is still untested.** The
  shipped `DENSE_PEAK` guess pinned confidence at 0.35 for all 600 frames and
  cost 6255 FPs (MOTA 0.731). A GT sweep put the optimum at 0.50 / buffer 30,
  now applied — but that optimum *is* the fixed default, and it still loses to
  C1 off (0.905 vs 0.917). And `dense` never drops below C1's switching
  threshold (0/600 frames), so it cannot test adaptation at all; only `mixed`
  (switches 264/336) can. See `experiments/c1_sweep/evidence.md`.
- **C3's MAPPO branch cannot be made to help.** τ_mappo = 0.40 sits below the
  observed score floor of 0.435, so it filters nothing — and a full sweep shows
  every higher threshold is worse. The reliability score separates true from
  false tracks only weakly (ROC AUC 0.609) while false positives are just 5.5%
  of tracks, so the best cut-off still discards four true tracks per false one.
  The number to improve is the score, not the threshold. C3's precision claim
  lives on the accident branch, which this accident-free clip cannot test.
  See `experiments/c3_sweep/evidence.md`.

Cost of C2: **+22% tracker latency** (3.93 → 4.78 ms/frame, detector excluded;
dense-window p95 14.09 ms). Small against a YOLO11 inference budget of tens of
ms. Measure with one variant per process — see `experiments/latency/evidence.md`
for why a multi-variant run gets this wrong by 3×.

The GT was seeded from `ctrv_gate_nsa`'s own pre-labels, which biases that row
upward. Measured rather than assumed: correcting *every* still-flagged merge
candidate moves C2's margin over baseline only from +0.089 to +0.085 IDF1
(`experiments/gt_qa/sensitivity.md`). The bias is real, one-directional, and
bounded at ~0.004.

Synthetic evidence (superseded for headline numbers, still the unit-level
argument — details in `experiments/`):

- CTRV vs linear KF one-step prediction RMSE: **−48%** on constant turns,
  **−13%** on weaving, no regression on straight lines
- CTRV keeps the track ID through a 12-frame occlusion mid-turn where the
  linear baseline re-identifies (IDSW 0 vs 1)
- Documented boundary: an occlusion landing right after a turn-rate sign
  flip favors a straight coast — analysis material, see
  `experiments/exp1_C2/synthetic_evidence.md`

## Repository structure

```
CAAP/
├── code/
│   ├── pipeline.py                 ← end-to-end pipeline, ablation flags
│   ├── models/
│   │   ├── context_estimator.py    ← C1a: 4 traffic signals
│   │   ├── adaptive_controller.py  ← C1b: state → params (hysteresis)
│   │   ├── motorcycle_motion_model.py  ← C2: CTRV EKF
│   │   └── track_reliability.py    ← C3: dual-task score
│   ├── tracker/
│   │   ├── adaptive_bytetrack.py   ← ClassAwareSTrack + AdaptiveBYTETracker
│   │   └── vendor/                 ← ByteTrack files, compat-patched
│   │                                  (PATCHES.md — association unchanged)
│   ├── detection/                  ← YOLO11 wrapper (COCO fallback),
│   │                                  EfficientNet-B0 severity classifier
│   ├── alert/                      ← Telegram bot (rate-limited, dry_run)
│   ├── evaluation/metrics.py       ← self-implemented MOTA/IDF1/frag,
│   │                                  cross-validated vs py-motmetrics
│   ├── utils/synthetic.py          ← trajectory generators (tests + harness)
│   └── scripts/run_experiment.py   ← CLI: --synthetic | --video
├── configs/                        ← default + per-experiment YAML
├── tests/                          ← 134 tests (pytest)
├── experiments/                    ← results JSON + evidence notes per run
├── data/                           ← gitignored (IP protection)
├── weights/                        ← gitignored
└── lib/ByteTrack/                  ← gitignored reference clone (optional)
```

## Blockers & fallbacks

| Missing | Effect | Fallback in place |
|---|---|---|
| GT for `mixed` / `freeflow` | C1 threshold calibration; a segment not seeded from the proposed method | `dense` GT done — C2 numbers are real, C1/C3 still uncalibrated |
| Accident footage | the whole accident branch: alert P/R/F1, severity confusion matrix, and C3's `tau_acc` — the one place C3's asymmetry can be tested | none. Co-author is collecting; go/no-go 20 Sep |
| `weights/efficientnet_severity.pt` | severity classification | branch auto-disables with a logged warning |

`weights/yolo11_vn.pt` is **present** and does carry an `Accident` class
(id 0; `Detector` remaps by name, so its ordering does not matter). It is a
`task='segment'` checkpoint while the pipeline only reads `.boxes` — whether
that costs FPS for nothing is measured in the real-time benchmark.

Not a blocker but the current gate on every headline number: the `dense` GT is
over-merged (74/335 identities) and the re-review pass has not been run. See
the warning above.

## Data policy (IP protection)

- `data/` is **gitignored** — never commit footage or labels.
- `weights/` is **gitignored** — never commit trained model weights.
- Telegram credentials live in gitignored `configs/tele_api.yaml`
  (copy from `configs/tele_api.example.yaml`).
- Only pseudocode is published in the paper.
