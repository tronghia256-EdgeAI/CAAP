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

from code.annotation_sim.simulate import match

# evaluation class → (GT class ids, COCO class ids)  (PROTOCOL.md A1 item 9)
SPEC = {
    'fasttrack': {
        'classes': {'person': ([1], [0]), 'bus': ([2, 3], [5]), 'truck': ([4, 5], [7]),
                    'car': ([6], [2]), 'bicycle': ([7], [1]), 'motorbike': ([8], [3])},
        'ignore': list(range(9, 16)),      # ignore_region and classes outside the mapping
    },
    'mot17': {'classes': {'person': ([1], [0])}, 'distractors': [2, 7, 8, 12]},
    'dancetrack': {'classes': {'person': ([1], [0])}},
}


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


def preprocess(seq: Sequence, tracks: np.ndarray) -> np.ndarray:
    """Remove tracker boxes the evaluation must not count (applied to seeds and evaluated trackers alike).

    MOT17: TrackEval's rule — Hungarian-match tracker boxes to all GT rows of the frame
    (IoU >= 0.5) and drop those matched to a distractor class.
    FastTrack: drop boxes whose centre lies inside an ignore box of the same frame.
    """
    tracks = np.asarray(tracks, dtype=float).reshape(-1, 6)
    spec, raw = SPEC[seq.dataset], seq.gt_raw
    if seq.dataset == 'mot17' and len(tracks):
        all_gt = np.column_stack([raw[:, 0], np.arange(len(raw)), _xyxy(raw)])
        m = match(tracks, all_gt)
        hit = m >= 0
        drop = np.zeros(len(tracks), dtype=bool)
        drop[hit] = np.isin(raw[m[hit], 7], spec['distractors'])
        return tracks[~drop]
    if seq.dataset == 'fasttrack' and len(tracks):
        ign = raw[np.isin(raw[:, 7], spec['ignore'])]
        if not len(ign):
            return tracks
        ign_boxes = _xyxy(ign)
        cx = (tracks[:, 2] + tracks[:, 4]) / 2
        cy = (tracks[:, 3] + tracks[:, 5]) / 2
        drop = np.zeros(len(tracks), dtype=bool)
        for f in np.intersect1d(tracks[:, 0], ign[:, 0]):
            ti, b = np.flatnonzero(tracks[:, 0] == f), ign_boxes[ign[:, 0] == f]
            inside = ((cx[ti, None] >= b[None, :, 0]) & (cx[ti, None] <= b[None, :, 2])
                      & (cy[ti, None] >= b[None, :, 1]) & (cy[ti, None] <= b[None, :, 3]))
            drop[ti] = inside.any(axis=1)
        return tracks[~drop]
    return tracks
