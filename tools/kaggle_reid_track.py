"""Run an appearance-based (ReID) tracker on the cached YOLO11x detections (docs/PROTOCOL.md, A9).

Runs on a Kaggle GPU notebook with internet on, from a clone of this repository:

    !pip -q install boxmot==25.0.0
    !python tools/kaggle_reid_track.py --dataset mot17 --dets /kaggle/input/<caap-reid-inputs>
    !python tools/kaggle_reid_track.py --dataset dancetrack --dets /kaggle/input/<caap-reid-inputs>

The tracker is BoxMOT's BotSort with its default ReID weights (OSNet x0.25, MSMT17) and constructor
defaults, except use_cmc=False as for the motion-only BoT-SORT. It is fed exactly the cached
det_yolo11x.txt person boxes the other trackers saw. Frames are downloaded as in
kaggle_detect_cache.py and deleted after each sequence. Output, per sequence:
<out>/<dataset>/<seq>.txt in MOT format (frame, id, left, top, w, h, conf, -1, -1, -1) and a
done.json; a finished sequence is skipped on rerun.
"""
import argparse
import configparser
import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from kaggle_detect_cache import sequences, sha256  # noqa: E402

REID = 'osnet_x0_25_msmt17.pt'


def find_inputs(root: Path, dataset: str) -> dict:
    """{sequence name: folder holding det_yolo11x.txt and seqinfo.ini} for one dataset."""
    found = {p.parent.name: p.parent for p in root.rglob('det_yolo11x.txt') if p.parent.parent.name == dataset}
    if not found:
        raise SystemExit(f'no {dataset}/<seq>/det_yolo11x.txt under {root}')
    return found


def load_dets(seq_dir: Path):
    ini = configparser.ConfigParser()
    ini.read(seq_dir / 'seqinfo.ini')
    s = ini['Sequence']
    n_frames, frame_rate = int(s['seqLength']), float(s['frameRate'])
    d = np.loadtxt(seq_dir / 'det_yolo11x.txt', delimiter=',', ndmin=2)
    d = d[(d[:, 7] == 0) & (d[:, 0] <= n_frames)]                      # person, as data.class_dets
    boxes = np.column_stack([d[:, 2], d[:, 3], d[:, 2] + d[:, 4], d[:, 3] + d[:, 5], d[:, 6], np.zeros(len(d))])
    return d[:, 0].astype(int), boxes, n_frames, frame_rate


def track(images, frames, boxes, n_frames, frame_rate, device):
    import cv2
    from boxmot import BotSort
    tracker = BotSort(reid_weights=Path(REID), device=device, half=device != 'cpu', use_cmc=False,
                      frame_rate=int(round(frame_rate)))
    by_name = {int(p.stem): p for p in images}
    lines = []
    for f in range(1, n_frames + 1):
        img = cv2.imread(str(by_name[f]))
        out = tracker.update(boxes[frames == f], img)
        for x1, y1, x2, y2, tid, conf, *_ in out.reshape(-1, 8).tolist():
            lines.append(f'{f},{int(tid) + 1},{x1:.2f},{y1:.2f},{x2 - x1:.2f},{y2 - y1:.2f},{conf:.4f},-1,-1,-1')
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', required=True, choices=['mot17', 'dancetrack'])
    ap.add_argument('--dets', required=True, help='folder with <dataset>/<seq>/det_yolo11x.txt (uploaded inputs)')
    ap.add_argument('--out', default='/kaggle/working/reid_tracks')
    ap.add_argument('--tmp', default='/kaggle/tmp')
    ap.add_argument('--device', default='0')
    ap.add_argument('--seqs', nargs='*', help='only these sequence names (default: all)')
    args = ap.parse_args()

    import boxmot
    inputs = find_inputs(Path(args.dets), args.dataset)
    tmp = Path(args.tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    root = Path(args.out) / args.dataset
    root.mkdir(parents=True, exist_ok=True)
    for name, extract in sequences(args.dataset, tmp):
        done = root / f'{name}.done.json'
        if name not in inputs or (args.seqs and name not in args.seqs) or done.exists():
            continue
        frames, boxes, n_frames, frame_rate = load_dets(inputs[name])
        seq = extract()
        images = sorted((seq / 'img1').glob('*.jpg'))
        if len(images) < n_frames:
            raise SystemExit(f'{name}: {len(images)} images for {n_frames} frames')
        lines = track(images, frames, boxes, n_frames, frame_rate, args.device)
        (root / f'{name}.txt').write_text('\n'.join(lines) + '\n')
        weights = next(Path(boxmot.__file__).parent.rglob(REID), None)
        done.write_text(json.dumps({
            'frames': n_frames, 'detections': len(boxes), 'track_rows': len(lines), 'boxmot': boxmot.__version__,
            'reid_weights': REID, 'reid_sha256': sha256(weights) if weights else None,
            'dets_sha256': hashlib.sha256((inputs[name] / 'det_yolo11x.txt').read_bytes()).hexdigest(),
        }, indent=2))
        shutil.rmtree(tmp / Path(*seq.relative_to(tmp).parts[:1]))
        print(name, n_frames, len(lines), flush=True)


if __name__ == '__main__':
    main()
