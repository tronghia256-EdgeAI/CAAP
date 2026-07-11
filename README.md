# Context-Aware Adaptive Perception for Mixed Traffic

**Author:** Trọng Nghĩa
**Target:** ICRA 2027 (primary) · IEEE IV 2027 (backup)
**Status:** full pipeline implemented & tested on synthetic benchmarks — awaiting VN footage for real ablations

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

# Run the test suite (96 tests) — from the repo root
pytest tests/ -q

# Run an ablation experiment on the synthetic benchmark (no weights/footage needed)
python -m code.scripts.run_experiment --config configs/exp1_C2.yaml --synthetic --save-metrics

# Run on real footage (COCO yolov8n fallback engages if VN weights are absent)
python -m code.scripts.run_experiment --config configs/baseline.yaml --video data/raw/videos/<clip>.mp4 --save-metrics
```

> Run scripts as modules (`python -m code.scripts.run_experiment`) from the
> repo root — the project package is named `code`, which shadows a stdlib
> module (see `code/__init__.py`).

## Ablation configs

| Config file | C1 | C2 | C3 | Maps to |
|---|---|---|---|---|
| `configs/baseline.yaml` | ✗ | ✗ | ✗ | Exp 0 — vanilla YOLOv8 + ByteTrack |
| `configs/exp1_C2.yaml` | ✗ | ✓ | ✗ | Exp 1 — +CTRV motion model |
| `configs/exp2_C1C2.yaml` | ✓ | ✓ | ✗ | Exp 2 — +context adaptation |
| `configs/exp3_C1C2C3.yaml` / `default.yaml` | ✓ | ✓ | ✓ | Exp 3 — proposed method |

Synthetic evidence so far (details & caveats in `experiments/`):

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
│   ├── detection/                  ← YOLOv8 wrapper (COCO fallback),
│   │                                  EfficientNet-B0 severity classifier
│   ├── alert/                      ← Telegram bot (rate-limited, dry_run)
│   ├── evaluation/metrics.py       ← self-implemented MOTA/IDF1/frag,
│   │                                  cross-validated vs py-motmetrics
│   ├── utils/synthetic.py          ← trajectory generators (tests + harness)
│   └── scripts/run_experiment.py   ← CLI: --synthetic | --video
├── configs/                        ← default + per-experiment YAML
├── tests/                          ← 96 tests (pytest)
├── experiments/                    ← results JSON + evidence notes per run
├── data/                           ← gitignored (IP protection)
├── weights/                        ← gitignored
└── lib/ByteTrack/                  ← gitignored reference clone (optional)
```

## Blockers & fallbacks

| Missing | Effect | Fallback in place |
|---|---|---|
| VN footage + annotations | final ablation numbers, C1 threshold calibration | synthetic benchmark covers all code paths |
| `weights/yolov8_vn.pt` | accident class detection | COCO yolov8n auto-fallback (car/motorcycle/bus/truck) |
| `weights/efficientnet_severity.pt` | severity classification | branch auto-disables with a logged warning |

## Data policy (IP protection)

- `data/` is **gitignored** — never commit footage or labels.
- `weights/` is **gitignored** — never commit trained model weights.
- Telegram credentials live in gitignored `configs/tele_api.yaml`
  (copy from `configs/tele_api.example.yaml`).
- Only pseudocode is published in the paper.
