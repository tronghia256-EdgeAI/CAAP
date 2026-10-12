"""
code/scripts/audit_disagreements.py
───────────────────────────────────
Sampled human audit of the boxes a tracker and a reviewed GT disagree on.

A reviewed GT holds its seeding tracker's boxes, each one shown to the
reviewer. Boxes only the OTHER tracker outputs were never shown, so their
absence from the GT is a default, not a judgement (experiments/seed_bias).
This samples runs (consecutive frames of one ID) of
  extra    tracker box with no GT box at IoU >= 0.5 (an FP if the GT is right)
  missing  GT box with no tracker box at IoU >= 0.5 (an FN if the GT is right)
and renders the middle frame of each run as a numbered crop: red = audited
box, green = the other GT boxes. Verdicts go in verdicts.csv, which shows the
judge crop numbers only (key.csv maps them to tracker, GT and kind):
  Y  a real motorcycle at the red box, boxed about right
  N  no motorcycle there (ghost, other object, background)
  D  the motorcycle is already boxed in green (duplicate)
  ?  cannot tell

    python -m code.scripts.audit_disagreements sample
    python -m code.scripts.audit_disagreements score
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

from code.scripts.check_seed_bias import DUMPS, MOTO, REVIEWS
from code.scripts.compare_motion_models import open_video
from code.scripts.eval_hota_ci import iou_matrix
from code.scripts.gt_roi import filter_frames, load_roi
from code.scripts.import_gt import load_mot, to_framelist
from code.scripts.sweep_c2_sensitivity import moto_framelist

VIDEO = "data/raw/videos/NKKN-VoThiSau 2017-07-18_08_00_00_000.asf"
# (review, tracker that did NOT seed it): the unseen side of each GT
STRATA = [("mixed", "ctrv_gate_nsa"), ("dense", "baseline")]
PER_STRATUM, SEED, IOU = 40, 20261012, 0.5
AUDIT = Path("data/annotations/seed_bias_audit")      # gitignored: footage crops
OUT = Path("experiments/seed_bias/audit.json")
FIELDS = ["n", "review", "tracker", "kind", "track_id", "run_frames", "abs_frame",
          "x1", "y1", "x2", "y2", "verdict"]


def unmatched(a: list, b: list) -> list[int]:
    """Indices of boxes in frame list `a` with no one-to-one partner in `b` at IoU >= IOU."""
    if not a:
        return []
    if not b:
        return list(range(len(a)))
    iou = iou_matrix([x for _, x in a], [x for _, x in b])
    hit = {r for r, c in zip(*linear_sum_assignment(-iou)) if iou[r, c] >= IOU}
    return [i for i in range(len(a)) if i not in hit]


def runs(fl: list, flags: list[list[int]]) -> list[list[tuple]]:
    """Group flagged boxes into runs of (frame, id, box): same ID, consecutive frames."""
    open_, done = {}, []
    for k, idx in enumerate(flags):
        now = {}
        for i in idx:
            tid, box = fl[k][i]
            now[tid] = open_.pop(tid, []) + [(k, tid, box)]
        done += open_.values()
        open_ = now
    return done + list(open_.values())


def sample() -> None:
    rng = np.random.default_rng(SEED)
    rows, gt_boxes = [], {}
    for review, tracker in STRATA:
        run_dir, (s, e), _ = REVIEWS[review]
        roi = load_roi(Path(run_dir))
        truth = filter_frames(load_mot(Path(run_dir) / "gt_reviewed.txt"), roi)
        gt, gt_all = to_framelist(truth, e - s, MOTO), to_framelist(truth, e - s)
        pr = moto_framelist(DUMPS / f"tracks_{tracker}.json", s, e, roi)
        for kind, a, b in (("extra", pr, gt), ("missing", gt, pr)):
            found = runs(a, [unmatched(a[k], b[k]) for k in range(e - s)])
            pick = rng.choice(len(found), size=min(PER_STRATUM, len(found)), replace=False)
            for j in sorted(pick):
                k, tid, box = found[j][len(found[j]) // 2]
                rows.append(dict(review=review, tracker=tracker, kind=kind, track_id=tid,
                                 run_frames=len(found[j]), abs_frame=s + k,
                                 x1=round(box[0], 1), y1=round(box[1], 1),
                                 x2=round(box[2], 1), y2=round(box[3], 1), verdict=""))
                gt_boxes[s + k] = [x for _, x in gt_all[k]]
            print(f"{review}/{tracker}/{kind}: {len(found)} runs, sampled {len(pick)}")
    order = rng.permutation(len(rows))            # strata interleaved: the judge sees no labels
    rows = [dict(n=i + 1, **rows[j]) for i, j in enumerate(order)]
    AUDIT.mkdir(parents=True, exist_ok=True)
    render(rows, gt_boxes)
    with (AUDIT / "key.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS[:-1], extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    # The judge sees crop numbers only: which tracker or GT a crop came from stays in key.csv.
    (AUDIT / "verdicts.csv").write_text("n,verdict\n" + "".join(f"{r['n']},\n" for r in rows),
                                        encoding="utf-8")
    print(f"{len(rows)} crops -> {AUDIT}/sheet_*.png; verdicts go in {AUDIT / 'verdicts.csv'}")


def render(rows: list[dict], gt_boxes: dict[int, list]) -> None:
    import cv2
    frames, want, cap = {}, {r["abs_frame"] for r in rows}, open_video(VIDEO, 0)
    for n in range(max(want) + 1):
        ok, img = cap.read()
        if not ok:
            raise RuntimeError(f"{VIDEO} ended at frame {n}")
        if n in want:
            frames[n] = img
    cap.release()
    tiles = []
    for r in rows:
        img = frames[r["abs_frame"]].copy()
        for g in gt_boxes[r["abs_frame"]]:
            cv2.rectangle(img, (int(g[0]), int(g[1])), (int(g[2]), int(g[3])), (0, 200, 0), 1)
        x1, y1, x2, y2 = (int(r[k]) for k in ("x1", "y1", "x2", "y2"))
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        half = max(60, 2 * max(x2 - x1, y2 - y1))
        img = cv2.copyMakeBorder(img, half, half, half, half, cv2.BORDER_CONSTANT)   # square crops at edges
        cx, cy = (x1 + x2) // 2 + half, (y1 + y2) // 2 + half
        tile = cv2.resize(img[cy - half:cy + half, cx - half:cx + half], (240, 240),
                          interpolation=cv2.INTER_CUBIC)
        cv2.putText(tile, str(r["n"]), (6, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4)
        cv2.putText(tile, str(r["n"]), (6, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        tiles.append(tile)
    for i in range(0, len(tiles), 20):
        page = tiles[i:i + 20] + [np.zeros_like(tiles[0])] * (20 - len(tiles[i:i + 20]))
        sheet = np.vstack([np.hstack(page[j:j + 5]) for j in range(0, 20, 5)])
        cv2.imwrite(str(AUDIT / f"sheet_{i // 20 + 1:02d}.png"), sheet)


def wilson(k: int, n: int, z: float = 1.96) -> list[float]:
    if not n:
        return [0.0, 1.0]
    p, d = k / n, 1 + z * z / n
    c, h = (p + z * z / (2 * n)) / d, z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]


def score() -> None:
    verdict = {r["n"]: r["verdict"] for r in csv.DictReader((AUDIT / "verdicts.csv").open(encoding="utf-8"))}
    rows = [dict(r, verdict=verdict.get(r["n"], "")) for r in csv.DictReader((AUDIT / "key.csv").open(encoding="utf-8"))]
    if any(r["verdict"].strip().upper() not in {"Y", "N", "D", "?"} for r in rows):
        raise SystemExit("every row needs a verdict: Y, N, D or ?")
    result = {}
    for review, tracker in STRATA:
        for kind in ("extra", "missing"):
            v = [r["verdict"].strip().upper() for r in rows
                 if (r["review"], r["tracker"], r["kind"]) == (review, tracker, kind)]
            n = sum(x != "?" for x in v)
            # 'extra' boxes are GT omissions if real; 'missing' boxes are GT errors if not
            gt_wrong = sum(x == "Y" for x in v) if kind == "extra" else sum(x in "ND" for x in v)
            result[f"{review}/{tracker}/{kind}"] = dict(
                counts={x: v.count(x) for x in "YND?"}, judged=n,
                gt_wrong_share=round(gt_wrong / max(1, n), 3), wilson95=wilson(gt_wrong, n))
            print(f"{review}/{tracker}/{kind}: {result[f'{review}/{tracker}/{kind}']}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("step", choices=("sample", "score"))
    {"sample": sample, "score": score}[ap.parse_args().step]()


if __name__ == "__main__":
    main()
