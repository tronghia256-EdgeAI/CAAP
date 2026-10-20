"""
code/seedbias/data.py
─────────────────────
Load a cached sequence (tools/kaggle_detect_cache.py output) and apply the
shared preprocessing of PROTOCOL.md Amendment A1 item 8 / A2, so that GT_true,
the seeds and every evaluated tracker see the same filtering.

Track arrays: [frame, id, x1, y1, x2, y2]. Detection arrays: [frame, x1, y1, x2, y2, conf].
"""

from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import scipy.optimize

from code.annotation_sim.simulate import _validated, match
from code.seedbias.evaluate import _BaseDataset

# evaluation class → (GT class ids, COCO class ids)  (PROTOCOL.md A1 item 9)
SPEC = {
    'fasttrack': {
        'classes': {'person': ([1], [0]), 'bus': ([2, 3], [5]), 'truck': ([4, 5], [7]),
                    'car': ([6], [2]), 'bicycle': ([7], [1]), 'motorbike': ([8], [3])},
        'ignore': list(range(9, 16)),      # ignore_region and classes outside the mapping
        'labels': ['person', 'bus_small', 'bus_big', 'truck_small', 'truck_big', 'car', 'bike', 'motorbike',
                   'ignore_region', 'tractor', 'trailor', 'wheelchair', 'heavy_equipment', 'pm', 'umbrella'],
    },
    'mot17': {'classes': {'person': ([1], [0])}, 'distractors': [2, 7, 8, 12]},
    # A5 item 5 sensitivity: FastTrack with car, bus and truck merged into one class (same dets and GT files).
    'dancetrack': {'classes': {'person': ([1], [0])}},
}
SPEC['fasttrack_vehicle'] = dict(SPEC['fasttrack'], classes={'vehicle': ([2, 3, 4, 5, 6], [2, 5, 7])}, source='fasttrack')


def source(dataset: str) -> str:
    """Name of the cached-detection folder a dataset reads from."""
    return SPEC[dataset].get('source', dataset)


@dataclass
class Sequence:
    dataset: str
    name: str
    frame_rate: float
    n_frames: int
    gt_raw: np.ndarray      # gt.txt as loaded: frame, id, l, t, w, h, consider, class, visibility
    dets: np.ndarray        # det file as loaded: frame, -1, l, t, w, h, conf, coco_class, -1


def _load(path) -> np.ndarray:
    text = Path(path).read_text(encoding='utf-8').strip()
    return np.loadtxt(text.splitlines(), delimiter=',', ndmin=2) if text else np.empty((0, 9))


def load(seq_dir, dataset: str, detector: str) -> Sequence:
    seq_dir = Path(seq_dir)
    ini = configparser.ConfigParser()
    ini.read(seq_dir / 'seqinfo.ini')
    s = ini['Sequence']
    labels = SPEC[dataset].get('labels')
    if labels and (seq_dir / 'labels.txt').read_text(encoding='utf-8').split() != labels:
        raise ValueError(f'{seq_dir}: labels.txt differs from the class mapping in PROTOCOL.md A1 item 9')
    return Sequence(dataset, seq_dir.name, float(s['frameRate']), int(s['seqLength']),
                    _load(seq_dir / 'gt.txt'), _load(seq_dir / f'det_{detector}.txt'))


def _xyxy(raw, cols=slice(2, 6)):
    b = raw[:, cols].astype(float).copy()
    b[:, 2:4] += b[:, 0:2]
    return b


def gt_true(seq: Sequence, cls: str) -> np.ndarray:
    """GT_true rows of one evaluation class (MOT17: consider == 1 and class 1 only)."""
    gt_classes = SPEC[seq.dataset]['classes'][cls][0]
    raw = seq.gt_raw
    keep = np.isin(raw[:, 7], gt_classes) & (raw[:, 0] <= seq.n_frames)
    if seq.dataset == 'mot17':
        keep &= raw[:, 6] != 0
    raw = raw[keep]
    return np.column_stack([raw[:, 0], raw[:, 1], _xyxy(raw)])


def class_dets(seq: Sequence, cls: str) -> np.ndarray:
    coco = SPEC[seq.dataset]['classes'][cls][1]
    d = seq.dets[np.isin(seq.dets[:, 7], coco) & (seq.dets[:, 0] <= seq.n_frames)]
    return np.column_stack([d[:, 0], _xyxy(d), d[:, 6]])


def preprocess(seq: Sequence, tracks: np.ndarray, cls: str) -> np.ndarray:
    """Remove tracker boxes the evaluation must not count (applied to seeds and evaluated trackers alike).

    Tracks are first put in canonical (frame, id, box) order, the order write_mot uses, so that
    preprocessing the written file would give the same result.
    MOT17 (A2 item 2): TrackEval's recipe, frame by frame: IoU of every GT row (file order) with every
    tracker box, scores below 0.5 - eps set to 0, Hungarian on the negated scores, keep matches > eps,
    drop tracker boxes matched to a distractor class.
    FastTrack and fasttrack_vehicle (A5): drop a box whose centre lies inside an ignore box of the same frame, unless it is
    matched (IoU >= 0.5) to a GT_true box of the evaluated class in that frame.
    """
    tracks = _validated(tracks, 'tracks')
    spec, raw = SPEC[seq.dataset], seq.gt_raw
    eps = np.finfo('float').eps
    if seq.dataset == 'mot17' and len(tracks):
        drop = np.zeros(len(tracks), dtype=bool)
        gt_by_frame = _by_frame(raw[:, 0])
        for f, ti in _by_frame(tracks[:, 0]).items():
            gi = gt_by_frame.get(f)
            if gi is None:
                continue
            score = _BaseDataset._calculate_box_ious(_xyxy(raw[gi]), tracks[ti, 2:6], box_format='x0y0x1y1').copy()
            score[score < 0.5 - eps] = 0
            r, c = scipy.optimize.linear_sum_assignment(-score)
            ok = score[r, c] > 0 + eps
            r, c = r[ok], c[ok]
            drop[ti[c[np.isin(raw[gi[r], 7], spec['distractors'])]]] = True
        return tracks[~drop]
    if 'ignore' in spec and len(tracks):
        ign = raw[np.isin(raw[:, 7], spec['ignore']) & (raw[:, 0] <= seq.n_frames)]
        if not len(ign):
            return tracks
        ign_boxes = _xyxy(ign)
        matched = match(tracks, gt_true(seq, cls)) >= 0
        cx = (tracks[:, 2] + tracks[:, 4]) / 2
        cy = (tracks[:, 3] + tracks[:, 5]) / 2
        drop = np.zeros(len(tracks), dtype=bool)
        ign_by_frame = _by_frame(ign[:, 0])
        for f, ti in _by_frame(tracks[:, 0]).items():
            ii = ign_by_frame.get(f)
            if ii is None:
                continue
            b = ign_boxes[ii]
            inside = ((cx[ti, None] >= b[None, :, 0]) & (cx[ti, None] <= b[None, :, 2])
                      & (cy[ti, None] >= b[None, :, 1]) & (cy[ti, None] <= b[None, :, 3]))
            drop[ti] = inside.any(axis=1) & ~matched[ti]
        return tracks[~drop]
    return tracks


def _by_frame(frames) -> dict:
    """frame → row indices in their original (file) order."""
    order = np.argsort(frames, kind='stable')
    uniq, starts = np.unique(frames[order], return_index=True)
    return dict(zip(uniq.tolist(), np.split(order, starts[1:])))
