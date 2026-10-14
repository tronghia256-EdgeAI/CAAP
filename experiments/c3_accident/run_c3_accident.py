"""C3 accident-branch test, pre-registered in experiments/c3_accident/evidence.md.

Runs the paper's full pipeline (c1c2c3, best.pt at the Table 2 size, C1 threshold of
that size from the final run) on every clip of data/raw/videos, full frame, and records
per frame the Accident-class tracks before C3 (raw) and in C3's accident output. One JSON
per clip under --out (gitignored data/), so an interrupted run resumes clip by clip.
    PYTHONPATH=. python experiments/c3_accident/run_c3_accident.py --size 448 [--max-frames N]
    PYTHONPATH=. python experiments/c3_accident/run_c3_accident.py --size 448 --analyze
"""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np
import yaml

ACCIDENT = 4                       # PROJECT_CLASSES['accident']
FINAL = Path("data/processed/paper_runs/best85_roi_final")
SEEN = "7_20_2017"                 # camera with frames in best.pt's training export
ACCIDENT_CLIP, ONSET, END = "accident_tonghop.mp4", 55, 480
VIDEO_EXT = {".asf", ".mkv", ".mov", ".mp4"}


def clip_hour(name):
    """Hour from the file name; the accident clip has none, its overlay reads 13:30."""
    if name == ACCIDENT_CLIP:
        return 13
    m = re.search(r"(\d{1,2})_\d\d_\d\d (AM|PM)", name)
    if m:
        return int(m.group(1)) % 12 + (12 if m.group(2) == "PM" else 0)
    return int(re.search(r"\d{4}-\d\d-\d\d[ _](\d\d)", name).group(1))


def pipeline(size, fps, hour):
    from code.pipeline import Pipeline
    cfg = yaml.safe_load((FINAL / str(size) / "configs/c1c2c3.yaml").read_text(encoding="utf-8"))
    cfg.pop("roi", None)                                   # these cameras have no ROI
    cfg["tracker"]["frame_rate"] = float(fps)
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        yaml.safe_dump(cfg, f)
    pipe = Pipeline.from_config(f.name, build_detector=False, dry_run_alerts=True)
    Path(f.name).unlink()
    from code.detection.detector import Detector     # as run_roi_paper.benchmark_trial attaches it
    pipe.detector = Detector(cfg["weights"]["yolo11"], img_size=size)
    pipe.alert, pipe.accident_classifier = None, None
    pipe.reset()
    pipe.adaptive_controller.density_threshold = json.loads(
        (FINAL / str(size) / "c1_threshold.json").read_text(encoding="utf-8"))["threshold"]
    pipe.context_estimator.hour_override = hour
    return pipe


def run_clip(path, size, out, max_frames=None):
    import torch
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    pipe = pipeline(size, fps, clip_hour(path.name))
    ok, frame = cap.read()
    pipe.detector.detect(frame)                            # warm-up before fixing threads, as run_roi_paper
    torch.set_num_threads(8)
    raw, c3, n_tracks, k = {}, {}, [], 0
    while ok and (max_frames is None or k < max_frames):
        r = pipe.process(frame)
        a = [int(t.track_id) for t in pipe._last_tracks if int(t.class_id) == ACCIDENT]
        b = [int(t.track_id) for t in r["tracks_accident"] if int(t.class_id) == ACCIDENT]
        if a:
            raw[k] = a
        if b:
            c3[k] = b
        n_tracks.append(len(pipe._last_tracks))
        k += 1
        ok, frame = cap.read()
    cap.release()
    out.write_text(json.dumps(dict(
        clip=path.name, fps=fps, frames=k, size=size, hour=clip_hour(path.name),
        c1_threshold=pipe.adaptive_controller.density_threshold, seen_camera=SEEN in path.name,
        commit=subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip(),
        mean_confirmed_tracks=float(np.mean(n_tracks)), accident_raw=raw, accident_c3=c3), indent=1), encoding="utf-8")


def episodes(frames, fps, n):
    """Maximal runs of alerting frames, merging gaps shorter than 1 s: [(start, end)]."""
    alert = sorted(int(k) for k in frames)
    runs = []
    for k in alert:
        if runs and k - runs[-1][1] <= max(1, round(fps)):
            runs[-1][1] = k
        else:
            runs.append([k, k])
    return [tuple(r) for r in runs]


def analyze(out_dir):
    rows, pooled = [], {"raw": [0, 0.0], "c3": [0, 0.0]}
    for f in sorted(out_dir.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        ep = {k: episodes(d[f"accident_{k}"], d["fps"], d["frames"]) for k in ("raw", "c3")}
        hours = d["frames"] / d["fps"] / 3600
        row = dict(clip=d["clip"], minutes=round(hours * 60, 1), seen_camera=d["seen_camera"],
                   episodes=ep, per_hour={k: round(len(v) / hours, 1) for k, v in ep.items()})
        if d["clip"] == ACCIDENT_CLIP:
            for k, v in ep.items():
                hit = [s for s, e in v if e >= ONSET and s <= END]
                row[f"{k}_alerts_on_accident"] = bool(hit)
                row[f"{k}_first_alert_frame"] = (max(min(hit), ONSET) if hit else None)
                row[f"{k}_latency_s"] = (round((max(min(hit), ONSET) - ONSET) / d["fps"], 2) if hit else None)
        elif not d["seen_camera"]:
            for k in pooled:
                pooled[k][0] += len(ep[k])
                pooled[k][1] += hours
        rows.append(row)
        print(json.dumps({k: v for k, v in row.items() if k != "episodes"}))
    summary = {k: dict(episodes=v[0], hours=round(v[1], 3), per_hour=round(v[0] / v[1], 2) if v[1] else None)
               for k, v in pooled.items()}
    print("pooled unseen normal clips:", summary)
    (out_dir / "summary.json").write_text(json.dumps(dict(pooled_unseen_normal=summary, clips=rows), indent=1),
                                          encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, required=True)
    ap.add_argument("--videos", default="data/raw/videos")
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-frames", type=int, help="smoke test only")
    ap.add_argument("--clips", nargs="*", help="subset of clip file names")
    ap.add_argument("--analyze", action="store_true")
    args = ap.parse_args()
    out_dir = Path(args.out or f"data/processed/c3_accident/{args.size}")
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.analyze:
        return analyze(out_dir)
    clips = sorted(p for p in Path(args.videos).iterdir() if p.suffix.lower() in VIDEO_EXT)
    clips = [p for p in clips if not args.clips or p.name in args.clips]
    for p in clips:
        out = out_dir / (p.stem + ".json")
        if out.exists():
            continue
        print("running", p.name, flush=True)
        run_clip(p, args.size, out, args.max_frames)


if __name__ == "__main__":
    main()
