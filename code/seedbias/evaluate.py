"""
code/seedbias/evaluate.py
─────────────────────────
In-memory bridge to the official TrackEval metrics (JonathonLuiten/TrackEval
@12c8791): IDF1, HOTA (α-averaged and at α = 0.5), CLEAR MOT. Preprocessing is
done beforehand (code.seedbias.data.preprocess), so no dataset class is used.

evaluate_sequence() returns TrackEval's raw per-sequence results; summarize()
combines any subset of them (used for bootstrap resampling over sequences).
"""

from __future__ import annotations

import numpy as np

# TrackEval @12c8791 still uses aliases that numpy 1.24 removed.
for _alias, _type in (('float', float), ('int', int), ('bool', bool)):
    if not hasattr(np, _alias):
        setattr(np, _alias, _type)

from trackeval.datasets._base_dataset import _BaseDataset  # noqa: E402
from trackeval.metrics import CLEAR, HOTA, Identity  # noqa: E402

METRICS = {'HOTA': HOTA(), 'CLEAR': CLEAR({'THRESHOLD': 0.5, 'PRINT_CONFIG': False}),
           'Identity': Identity({'THRESHOLD': 0.5, 'PRINT_CONFIG': False})}
ALPHA_05 = int(np.flatnonzero(np.isclose(METRICS['HOTA'].array_labels, 0.5))[0])


def _remap(ids):
    uniq, inv = np.unique(ids, return_inverse=True)
    return inv.reshape(-1), len(uniq)


def to_trackeval(tracks: np.ndarray, gt: np.ndarray, n_frames: int) -> dict:
    """Build TrackEval's per-sequence data dict from [frame, id, x1, y1, x2, y2] arrays."""
    tracks = np.asarray(tracks, dtype=float).reshape(-1, 6)
    gt = np.asarray(gt, dtype=float).reshape(-1, 6)
    t_ids, n_t = _remap(tracks[:, 1])
    g_ids, n_g = _remap(gt[:, 1])
    t_frame, g_frame = tracks[:, 0].astype(int), gt[:, 0].astype(int)
    data = dict(num_timesteps=n_frames, num_gt_ids=n_g, num_tracker_ids=n_t,
                num_gt_dets=len(gt), num_tracker_dets=len(tracks),
                gt_ids=[], tracker_ids=[], similarity_scores=[])
    t_rows = {f: r for f, r in _group(t_frame)}
    g_rows = {f: r for f, r in _group(g_frame)}
    empty = np.empty(0, dtype=int)
    for f in range(1, n_frames + 1):
        ti, gi = t_rows.get(f, empty), g_rows.get(f, empty)
        data['gt_ids'].append(g_ids[gi])
        data['tracker_ids'].append(t_ids[ti])
        data['similarity_scores'].append(
            _BaseDataset._calculate_box_ious(gt[gi, 2:6], tracks[ti, 2:6], box_format='x0y0x1y1'))
    return data


def _group(frames):
    order = np.argsort(frames, kind='stable')
    uniq, starts = np.unique(frames[order], return_index=True)
    return zip(uniq.tolist(), np.split(order, starts[1:]))


def evaluate_sequence(tracks, gt, n_frames: int) -> dict:
    data = to_trackeval(tracks, gt, n_frames)
    return {name: metric.eval_sequence(data) for name, metric in METRICS.items()}


def summarize(results: list) -> dict:
    """Combine per-sequence results (as from evaluate_sequence) into headline numbers."""
    combined = {name: metric.combine_sequences({str(i): r[name] for i, r in enumerate(results)})
                for name, metric in METRICS.items()}
    hota, clear, ident = combined['HOTA'], combined['CLEAR'], combined['Identity']
    return dict(IDF1=float(ident['IDF1']), HOTA50=float(hota['HOTA'][ALPHA_05]),
                DetA50=float(hota['DetA'][ALPHA_05]), AssA50=float(hota['AssA'][ALPHA_05]),
                HOTA=float(np.mean(hota['HOTA'])), MOTA=float(clear['MOTA']), IDSW=int(clear['IDSW']))
