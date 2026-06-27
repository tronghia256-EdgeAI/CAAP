# Paper 2 — Context-Aware Adaptive Perception for Mixed Traffic

**Author:** Trọng Nghĩa  
**Target:** IEEE Transactions on Intelligent Transportation Systems (T-ITS, Q1)  
**Timeline:** 6 months

---

## Repository Structure

```
paper2_caap/
│
├── paper/                          ← LaTeX (Overleaf-ready)
│   ├── main.tex                    ← entry point, compile this
│   ├── references.bib              ← all citations (BibTeX)
│   ├── sections/
│   │   ├── 00_abstract.tex
│   │   ├── 01_introduction.tex
│   │   ├── 02_related_work.tex
│   │   ├── 03_methodology.tex      ← C1, C2, C3 with equations
│   │   ├── 04_experiments.tex
│   │   ├── 05_results.tex          ← fill after Month 4 experiments
│   │   └── 06_conclusion.tex
│   ├── figures/                    ← PDF figures (see figures/README.md)
│   └── tables/                     ← optional standalone .tex tables
│
├── code/
│   ├── pipeline.py                 ← main end-to-end pipeline
│   ├── models/
│   │   ├── __init__.py
│   │   ├── context_estimator.py    ← C1a: reads 4 traffic signals
│   │   ├── adaptive_controller.py  ← C1b: maps state → params
│   │   ├── motorcycle_motion_model.py  ← C2: CTRV EKF
│   │   └── track_reliability.py    ← C3: dual-task score
│   ├── tracker/
│   │   └── adaptive_bytetrack.py   ← ByteTrack wrapper (C1+C2 integrated)
│   ├── detection/
│   │   ├── detector.py             ← YOLOv8 wrapper
│   │   └── accident_classifier.py  ← EfficientNet-B0 severity
│   ├── alert/
│   │   └── telegram_alert.py       ← Telegram bot
│   ├── evaluation/
│   │   └── metrics.py              ← MOTA, IDF1, F1, mAP, etc.
│   ├── utils/                      ← visualization, video I/O helpers
│   └── scripts/
│       └── run_experiment.py       ← CLI for ablation experiments
│
├── configs/
│   ├── default.yaml                ← full pipeline (Exp 3 / proposed)
│   ├── baseline.yaml               ← ablation Exp 0 (no C1/C2/C3)
│   ├── exp1_C1.yaml                ← ablation Exp 1 (C1 only)
│   └── exp2_C1C2.yaml              ← ablation Exp 2 (C1+C2)
│
├── data/                           ← gitignored (IP protection)
│   ├── raw/                        ← original footage
│   ├── processed/                  ← preprocessed clips
│   └── annotations/                ← YOLO format labels
│
├── experiments/                    ← results JSON / logs per run
│   ├── baseline/
│   ├── exp1_C1/
│   ├── exp2_C1C2/
│   └── exp3_C1C2C3/
│
└── assets/                         ← demo videos, screenshots for README
```

---

## First Step (Month 1, Week 1)

```bash
# 1. Clone ByteTrack and read the source
git clone https://github.com/ifzhang/ByteTrack
# Read: byte_tracker.py → understand the track lifecycle
# Read: kalman_filter.py → understand what C2 will replace

# 2. Run ByteTrack on your VN footage, document 10+ failure cases
# Those failures = Section I motivation + Experiment 0 baseline numbers
```

---

## Overleaf Setup

1. Upload the `paper/` folder contents to a new Overleaf project.
2. Set compiler to **pdfLaTeX**.
3. Set main document to `main.tex`.
4. The `IEEEtran` class is pre-installed on Overleaf — no extra setup.

---

## Ablation Configs

| Config file | C1 | C2 | C3 | Maps to |
|---|---|---|---|---|
| `baseline.yaml` | ✗ | ✗ | ✗ | Exp 0 |
| `exp1_C1.yaml` | ✓ | ✗ | ✗ | Exp 1 |
| `exp2_C1C2.yaml` | ✓ | ✓ | ✗ | Exp 2 |
| `default.yaml` | ✓ | ✓ | ✓ | Exp 3 (proposed) |

---

## Data Policy (IP Protection)

- `data/` is **gitignored** — never commit footage or labels.
- `weights/` is **gitignored** — never commit trained model weights.
- Only pseudocode is published in the paper.
