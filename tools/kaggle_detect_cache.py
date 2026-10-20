"""Cache COCO-YOLO11 detections for the seed-bias study (docs/PROTOCOL.md, section 3).

Runs on a Kaggle GPU notebook with internet on. Standalone (no repo imports):

    !pip -q install ultralytics==8.4.92
    !python kaggle_detect_cache.py --dataset fasttrack
    !python kaggle_detect_cache.py --dataset mot17
    !python kaggle_detect_cache.py --dataset dancetrack

Each sequence is downloaded, extracted, detected with every model, then its
images are deleted. Output, per sequence: det_<model>.txt in MOT format
(frame, -1, left, top, w, h, conf, coco_class, -1), the dataset's gt.txt and
seqinfo.ini. A finished sequence has a done.json and is skipped on rerun.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

FASTTRACK = 'https://huggingface.co/datasets/Hamidreza-Hashemp/FastTracker-Benchmark/resolve/main/train/{}.zip'
FASTTRACK_SEQS = [
    'task_day_left_turn', 'task_day_occlusion', 'task_day_pedestrian_crossing', 'task_day_right_turn',
    'task_day_right_turn_occlusion', 'task_day_right_turn_pedestrian', 'task_night_far_objects',
    'task_night_occlusion', 'task_night_occlusion_far_objects', 'task_night_right_turn_pedestrian',
    'task_night_right_turn_pedestrian_occlusion', 'task_tunnel',
]
MOT17 = 'https://motchallenge.net/data/MOT17.zip'
DANCETRACK_VAL = 'https://huggingface.co/datasets/noahcao/dancetrack/resolve/main/val.zip'
# COCO ids: person, bicycle, car, motorcycle, bus, truck (mapping in PROTOCOL.md, Amendment A1).
CLASSES = {'fasttrack': [0, 1, 2, 3, 5, 7], 'mot17': [0], 'dancetrack': [0]}


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest):
    if not dest.exists():
        subprocess.run(['wget', '-q', '-O', str(dest) + '.part', url], check=True)
        Path(str(dest) + '.part').rename(dest)
    return dest


def sequence_dirs(archive, keep=lambda name: True):
    """{sequence name: archive prefix} for every '<prefix>/<name>/img1/' inside a zip."""
    found = {}
    for n in zipfile.ZipFile(archive).namelist():
        parts = n.split('/')
        if '__MACOSX' in parts or 'img1' not in parts:
            continue
        i = parts.index('img1')
        if i >= 1 and keep(parts[i - 1]):
            found[parts[i - 1]] = '/'.join(parts[:i]) + '/'
    return dict(sorted(found.items()))


def sequences(dataset, tmp):
    """Yield (name, extract) where extract() returns the extracted sequence dir."""
    if dataset == 'fasttrack':
        for name in FASTTRACK_SEQS:
            def extract(name=name):
                archive = download(FASTTRACK.format(name), tmp / f'{name}.zip')
                return _extract(archive, tmp, sequence_dirs(archive)[name])
            yield name, extract
        return
    if dataset == 'mot17':
        archive = download(MOT17, tmp / 'MOT17.zip')
        dirs = sequence_dirs(archive, lambda s: s.endswith('-FRCNN'))  # same images under DPM/FRCNN/SDP
        dirs = {k: v for k, v in dirs.items() if '/train/' in f'/{v}'}
    else:
        archive = download(DANCETRACK_VAL, tmp / 'dancetrack_val.zip')
        dirs = sequence_dirs(archive)
    for name, prefix in dirs.items():
        yield name, lambda prefix=prefix: _extract(archive, tmp, prefix)


def _extract(archive, tmp, prefix):
    with zipfile.ZipFile(archive) as z:
        z.extractall(tmp, [n for n in z.namelist() if n.startswith(prefix)])
    return tmp / prefix


def detect(model, images, classes, imgsz, conf, out):
    lines = []
    for img in images:
        frame = int(img.stem)
        r = model.predict(str(img), imgsz=imgsz, conf=conf, classes=classes, verbose=False)[0]
        for (x1, y1, x2, y2), c, k in zip(r.boxes.xyxy.tolist(), r.boxes.conf.tolist(), r.boxes.cls.tolist()):
            lines.append(f'{frame},-1,{x1:.2f},{y1:.2f},{x2 - x1:.2f},{y2 - y1:.2f},{c:.4f},{int(k)},-1')
    out.write_text('\n'.join(lines) + '\n')
    return len(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', required=True, choices=sorted(CLASSES))
    ap.add_argument('--models', nargs='+', default=['yolo11x.pt', 'yolo11n.pt'])
    ap.add_argument('--imgsz', type=int, default=1280)
    ap.add_argument('--conf', type=float, default=0.05)
    ap.add_argument('--out', default='/kaggle/working/dets')
    ap.add_argument('--tmp', default='/kaggle/tmp')
    ap.add_argument('--seqs', nargs='*', help='only these sequence names (default: all)')
    args = ap.parse_args()

    import ultralytics
    from ultralytics import YOLO
    models = {Path(m).stem: YOLO(m) for m in args.models}
    tmp = Path(args.tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    root = Path(args.out) / args.dataset
    for name, extract in sequences(args.dataset, tmp):
        dest = root / name
        if (args.seqs and name not in args.seqs) or (dest / 'done.json').exists():
            continue
        seq = extract()
        dest.mkdir(parents=True, exist_ok=True)
        images = sorted((seq / 'img1').glob('*.jpg'))
        for f in ('gt/gt.txt', 'gt/labels.txt', 'seqinfo.ini'):
            if (seq / f).exists():
                shutil.copy(seq / f, dest / Path(f).name)
        counts = {k: detect(m, images, CLASSES[args.dataset], args.imgsz, args.conf, dest / f'det_{k}.txt')
                  for k, m in models.items()}
        (dest / 'done.json').write_text(json.dumps({
            'frames': len(images), 'boxes': counts, 'imgsz': args.imgsz, 'conf': args.conf,
            'classes': CLASSES[args.dataset], 'ultralytics': ultralytics.__version__,
            'weights_sha256': {k: sha256(m.ckpt_path) for k, m in models.items()},
        }, indent=2))
        shutil.rmtree(tmp / Path(*seq.relative_to(tmp).parts[:1]))
        if args.dataset == 'fasttrack':
            (tmp / f'{name}.zip').unlink()
        print(name, len(images), counts, flush=True)


if __name__ == '__main__':
    main()
