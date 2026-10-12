"""
code/scripts/gt_newcam.py
─────────────────────────
Ground truth for held-out cameras, reusing the mixed-review workflow unchanged.
The cameras were audited clean against the detector's training images
(experiments/detector_leakage/evidence.md).

Per camera:
  select    pre-registered window rule, fixed before any tracker runs: the
            densest 600-frame window that starts after frame WARMUP, on a
            25-frame grid. Density = mean count of detections with score
            >= 0.5 (accident class excluded) from best.pt at 448 px, on every
            5th frame. (The NKKN segments were chosen by tracks/frame of a full
            C2 run; this is the same idea without a tracker in the loop.)
  cache     detections of the paper's accuracy detector, yolo11_vn.pt at
            1280 px with the 0.1 confidence floor (as for NKKN), for frames
            [start - WARMUP, end)
  prelabel  baseline ByteTrack on those detections -> MOT pre-labels and frames
            under data/annotations/prelabels/<camera>/ and a review bundle
            (gt_mixed_review.prepare) under experiments/gt_qa/<camera>_review/
  replay    the paper's tracker variants on the cached detections, as dumps
            with absolute frame indices for scoring the reviewed GT
  finalize  finalize_mixed into experiments/gt_newcam/<camera>/reviewed, labelled
            held-out. Not the app's finish button: that writes into the mixed
            segment's folder with the mixed segment's 'development' label.

Review in the existing app (draw the camera's own ROI there first):
  review_gt_mixed.cmd --bundle experiments/gt_qa/<camera>_review
      --tracks-dir experiments/gt_newcam/<camera>/dumps
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from code.scripts.compare_motion_models import VARIANTS, open_video
from code.scripts.sweep_c2_sensitivity import replay

CAMERAS = {
    "conghoa_uttich_1715": ("data/raw/videos/CongHoa-UtTich1 2017-07-17_17.15.asf", 17),
    "conghoa_truongchinh_1700": ("data/raw/videos/CongHoa-TruongChinh 2017-07-18_17_00_00_000.asf", 17),
    "duongbatrac_0800": ("data/raw/videos/DuongBaTrac-TaQuangBuu1 2017-07-18_08_00_00_000.asf", 8),
}
WINDOW, GRID, WARMUP, STEP, DENSITY_CONF = 600, 25, 1000, 5, 0.5
SELECT_WEIGHTS, SELECT_IMGSZ = "ket_qua_train/best.pt", 448
EVAL_WEIGHTS, EVAL_IMGSZ = "weights/yolo11_vn.pt", 1280
ACCIDENT = 4
ROOT = Path("experiments/gt_newcam")
PAPER_VARIANTS = ("baseline", "ctrv_gate_nsa", "c1_ctrv_gate", "c1c2c3")
HELD_OUT_ROLE = ("held-out test: camera never used to develop or tune the method; the training-image "
                 "overlap audit covers best.pt's export only, not yolo11_vn.pt "
                 "(experiments/detector_leakage/evidence.md)")


def detector(weights: str, imgsz: int, task: str | None = None):
    """Detector that refuses to start without its weights: Detector itself
    falls back to COCO yolo11n, which finds ~1.5 vehicles/frame on this
    footage and would silently corrupt the window choice and the cache."""
    from code.detection.detector import Detector
    if not Path(weights).is_file():
        raise SystemExit(f"weights not found: {weights}")
    return Detector(weights, img_size=imgsz, task=task)


def densest_window(counts: dict[int, int], n_frames: int) -> tuple[int, float]:
    """Start of the densest WINDOW (mean of the sampled counts inside it)."""
    best = None
    for s in range(WARMUP, n_frames - WINDOW + 1, GRID):
        inside = [c for f, c in counts.items() if s <= f < s + WINDOW]
        mean = sum(inside) / len(inside)
        if best is None or mean > best[1]:
            best = (s, mean)
    return best


def select(camera: str) -> None:
    import cv2
    video, _ = CAMERAS[camera]
    det = detector(SELECT_WEIGHTS, SELECT_IMGSZ, task="detect")
    cap, counts, n = cv2.VideoCapture(video), {}, 0
    while cap.grab():
        if n % STEP == 0:
            ok, frame = cap.retrieve()
            if ok:
                d = det.detect(frame)
                counts[n] = int(((d[:, 4] >= DENSITY_CONF) & (d[:, 5] != ACCIDENT)).sum())
        n += 1
    cap.release()
    start, mean = densest_window(counts, n)
    out = ROOT / camera
    out.mkdir(parents=True, exist_ok=True)
    (out / "window.json").write_text(json.dumps({
        "camera": camera, "video": video, "frames_decoded": n,
        "rule": f"densest {WINDOW}-frame window starting >= {WARMUP} on a {GRID}-frame grid; "
                f"density = detections with score >= {DENSITY_CONF} (no accident class), "
                f"every {STEP}th frame, {SELECT_WEIGHTS} @{SELECT_IMGSZ}",
        "start": start, "end": start + WINDOW, "mean_density": round(mean, 2),
        "profile": {str(f): c for f, c in counts.items()}}, indent=1), encoding="utf-8")
    print(f"{camera}: {n} frames, window [{start}, {start + WINDOW}) density {mean:.1f}")


def cache(camera: str) -> None:
    video, _ = CAMERAS[camera]
    w = json.loads((ROOT / camera / "window.json").read_text(encoding="utf-8"))
    first, end = w["start"] - WARMUP, w["end"]
    det = detector(EVAL_WEIGHTS, EVAL_IMGSZ)
    cap, dets = open_video(video, first), []
    for _ in range(first, end):
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError(f"{video} ended before frame {end}")
        dets.append(det.detect(frame).astype(np.float32))
    cap.release()
    meta = {"video": video, "start_frame": first, "num_frames": len(dets),
            "weights": EVAL_WEIGHTS, "imgsz": EVAL_IMGSZ, "conf_floor": 0.1}
    np.savez_compressed(ROOT / camera / "detections.npz",
                        **{f"f{i}": d for i, d in enumerate(dets)}, meta=json.dumps(meta))
    print(f"{camera}: cached frames [{first}, {end})")


def absolute_dets(camera: str) -> tuple[list, int, int, dict]:
    """Cached detections indexed by absolute frame (None before the cache)."""
    npz = np.load(ROOT / camera / "detections.npz", allow_pickle=True)
    meta = json.loads(str(npz["meta"]))
    first = meta["start_frame"]
    dets = [None] * first + [npz[f"f{i}"] for i in range(meta["num_frames"])]
    return dets, first, first + meta["num_frames"], meta


def run_variants(camera: str, names=PAPER_VARIANTS) -> Path:
    """Replay the paper's variants; dumps keep absolute indices (start_frame 0)."""
    from code.pipeline import Pipeline
    from code.tracker.adaptive_bytetrack import ClassAwareSTrack
    dets, first, end, meta = absolute_dets(camera)
    out = ROOT / camera / "dumps"
    out.mkdir(parents=True, exist_ok=True)
    for name in names:
        config, overrides = VARIANTS[name]
        pipe = Pipeline.from_config(config, dry_run_alerts=True, build_detector=False)
        pipe.reset()
        pipe.tracker.uncertainty_gating = overrides.get(
            "uncertainty_gating", pipe.tracker.uncertainty_gating)
        ClassAwareSTrack.ctrv_scale_adaptive = overrides.get(
            "scale_adaptive", ClassAwareSTrack.ctrv_scale_adaptive)
        ClassAwareSTrack.ctrv_nsa = overrides.get("nsa", ClassAwareSTrack.ctrv_nsa)
        pipe.context_estimator.hour_override = CAMERAS[camera][1]
        frames = replay(pipe, dets, first, end)
        (out / f"tracks_{name}.json").write_text(json.dumps(
            {**meta, "start_frame": 0, "num_frames": end, "variant": name,
             "warmup_from": first, "frames": frames}), encoding="utf-8")
        print(f"  {camera}: replayed {name}")
    return out


def prelabel(camera: str) -> None:
    from code.scripts.export_prelabels import extract_frames, write_mot
    from code.scripts.gt_mixed_review import prepare
    video, _ = CAMERAS[camera]
    w = json.loads((ROOT / camera / "window.json").read_text(encoding="utf-8"))
    seg = (w["start"], w["end"])
    dumps = run_variants(camera, ("baseline",))
    frames = json.loads((dumps / "tracks_baseline.json").read_text(encoding="utf-8"))["frames"]
    out_root = Path("data/annotations/prelabels")
    stats = write_mot(frames[seg[0]:seg[1]], out_root / camera)
    extract_frames(video, {camera: seg}, out_root)
    bundle = prepare(source=out_root / camera, bundle=Path(f"experiments/gt_qa/{camera}_review"),
                     segment=seg)
    print(f"{camera}: baseline pre-labels {stats} -> review bundle {bundle}")


def finalize(camera: str, reviewer: str) -> None:
    """finalize_mixed into this camera's folder, then replace its hard-coded
    'development' role (the mixed segment's) and record window and seeding."""
    from code.detection.detector import DETECTOR_CONF
    from code.scripts.gt_mixed_review import MixedStore, finalize_mixed, json_bytes
    out = finalize_mixed(MixedStore(Path(f"experiments/gt_qa/{camera}_review")), reviewer or "",
                         tracks_dir=ROOT / camera / "dumps", out_dir=ROOT / camera / "reviewed")
    report = json.loads((out / "review.json").read_text(encoding="utf-8"))
    window = json.loads((ROOT / camera / "window.json").read_text(encoding="utf-8"))
    old, report["evaluation_role"] = report["evaluation_role"], HELD_OUT_ROLE
    report["window"] = {k: v for k, v in window.items() if k != "profile"}
    report["prelabel_seed"] = dict(tracker="baseline", tracker_config=VARIANTS["baseline"][0],
                                   detector=EVAL_WEIGHTS, imgsz=EVAL_IMGSZ, conf_floor=DETECTOR_CONF)
    (out / "review.json").write_bytes(json_bytes(report))
    summary = out / "summary.md"
    summary.write_text(summary.read_text(encoding="utf-8").replace(old, HELD_OUT_ROLE), encoding="utf-8")
    print(f"{camera}: reviewed GT -> {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("step", choices=("select", "cache", "prelabel", "replay", "finalize"))
    ap.add_argument("--cameras", nargs="*", default=list(CAMERAS), choices=list(CAMERAS))
    ap.add_argument("--reviewer", help="finalize: name recorded in review.json")
    args = ap.parse_args()
    for camera in args.cameras:
        if args.step == "finalize":
            finalize(camera, args.reviewer)
            continue
        {"select": select, "cache": cache, "prelabel": prelabel,
         "replay": run_variants}[args.step](camera)


if __name__ == "__main__":
    main()
