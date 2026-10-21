# CAAP — seed bias in MOT ground truth

Research question (fixed 20 October 2026): when tracking GT is created by reviewing the output of a
tracker, how much does that GT favour the seed tracker, when are tracker rankings reversed, and which
cheap protocol removes that bias? The experiments use public GT (FastTrack, MOT17, DanceTrack) as the reference.

- Scope and decisions: [docs/PAPER_SCOPE.md](docs/PAPER_SCOPE.md)
- Frozen protocol: [docs/PROTOCOL.md](docs/PROTOCOL.md)

## Repository contents

| Directory | Contents |
|---|---|
| `code/evaluation/` | Tracking/detection metrics (MOTA, IDF1, IoU matching), cross-checked against `motmetrics` |
| `code/utils/files.py` | `sha256`, `atomic_write` for provenance |
| `code/annotation_sim/` | Seed-then-review GT simulator (`prepare`, `simulate`; protocol section 4 + A1) |
| `tests/` | pytest |
| `tools/caap.py` | CLI (`status`, `test`) |
| `tools/kaggle_detect_cache.py` | YOLO11 (COCO) detection cache on Kaggle for FastTrack/MOT17/DanceTrack |
| `notebooks/caap-q1.ipynb` | Kaggle notebook that runs the script above (cell 0 writes the script with `%%writefile`) |
| `data/`, `weights/` | Local data and weights, gitignored (`weights/yolo11n.pt` is YOLO11n pretrained on COCO) |

The old detector code and data (dataset tool, vendored ByteTrack, training labels, `detector.pt`, HCMC videos)
have been moved to `C:/Users/ASUS/Desktop/CAAP_detector_backup_20261020` (with `MANIFEST.sha256`) and
remain in the Git history.

## Getting started

```powershell
.\caap.cmd status
.\caap.cmd test -q
```

To install on another machine:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
```
