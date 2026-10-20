import numpy as np
import pytest

from code.evaluation.metrics import compute_tracking_metrics
from code.seedbias import data as D
from code.seedbias.evaluate import evaluate_sequence, summarize
from code.seedbias.track import TRACKERS, run_tracker


def moving(n_obj=4, T=60, jitter=0.0, rng=None):
    """Objects moving right at 2 px/frame on separate rows; [frame, id, x1, y1, x2, y2]."""
    rng = rng or np.random.default_rng(0)
    rows = []
    for k in range(1, n_obj + 1):
        for t in range(1, T + 1):
            x, y = 10 + 2 * t, 60 * k
            rows.append([t, k, x, y, x + 30, y + 40])
    a = np.array(rows, float)
    a[:, 2:6] += rng.normal(0, jitter, (len(a), 4)) if jitter else 0
    return a


def noisy_tracker(gt, rng):
    """GT with box noise, 10% dropped boxes, one ID switch and a few FPs."""
    t = gt.copy()
    t[:, 2:6] += rng.normal(0, 2, (len(t), 4))
    t = t[rng.random(len(t)) > 0.1]
    t[(t[:, 1] == 1) & (t[:, 0] > 30), 1] = 99
    fp = np.array([[f, 50, 500, 500, 530, 540] for f in range(5, 15)], float)
    return np.concatenate([t, fp])


def write_mot_raw(path, tracks):
    lines = [f'{int(f)},{int(i)},{x1},{y1},{x2 - x1},{y2 - y1},1,1,1' for f, i, x1, y1, x2, y2 in tracks]
    path.write_text('\n'.join(lines) + '\n')


def official_trackeval(tmp_path, gt, tracks, n_frames):
    """TrackEval's own file-based MOTChallenge evaluation, preprocessing off."""
    import trackeval
    seq = 'SYN-01'
    gt_dir = tmp_path / 'gt' / 'MOT17-train' / seq
    (gt_dir / 'gt').mkdir(parents=True)
    write_mot_raw(gt_dir / 'gt' / 'gt.txt', gt)
    (gt_dir / 'seqinfo.ini').write_text(f'[Sequence]\nname={seq}\nseqLength={n_frames}\n')
    trk_dir = tmp_path / 'trk' / 'MOT17-train' / 'T' / 'data'
    trk_dir.mkdir(parents=True)
    write_mot_raw(trk_dir / f'{seq}.txt', tracks)
    seqmap = tmp_path / 'seqmap.txt'
    seqmap.write_text(f'name\n{seq}\n')
    ev = trackeval.Evaluator({'USE_PARALLEL': False, 'PRINT_RESULTS': False, 'PRINT_CONFIG': False,
                              'OUTPUT_SUMMARY': False, 'OUTPUT_DETAILED': False, 'PLOT_CURVES': False,
                              'TIME_PROGRESS': False, 'DISPLAY_LESS_PROGRESS': True, 'OUTPUT_EMPTY_CLASSES': False})
    ds = trackeval.datasets.MotChallenge2DBox({
        'GT_FOLDER': str(tmp_path / 'gt'), 'TRACKERS_FOLDER': str(tmp_path / 'trk'), 'BENCHMARK': 'MOT17',
        'SPLIT_TO_EVAL': 'train', 'TRACKERS_TO_EVAL': ['T'], 'SEQMAP_FILE': str(seqmap),
        'DO_PREPROC': False, 'PRINT_CONFIG': False})
    metrics = [trackeval.metrics.HOTA(), trackeval.metrics.CLEAR({'PRINT_CONFIG': False}),
               trackeval.metrics.Identity({'PRINT_CONFIG': False})]
    res, _ = ev.evaluate([ds], metrics)
    r = res['MotChallenge2DBox']['T'][seq]['pedestrian']
    return r


def test_bridge_equals_official_trackeval(tmp_path):
    rng = np.random.default_rng(1)
    gt = moving(jitter=0.5, rng=rng)
    gt = gt[~((gt[:, 1] == 2) & (gt[:, 0] > 20) & (gt[:, 0] < 26))]   # an occlusion gap
    tracks = noisy_tracker(gt, rng)
    ours = evaluate_sequence(tracks, gt, 60)
    ref = official_trackeval(tmp_path, gt, tracks, 60)
    for metric, fields in (('Identity', ['IDF1', 'IDTP']), ('CLEAR', ['MOTA', 'IDSW', 'CLR_FP']),
                           ('HOTA', ['HOTA', 'DetA', 'AssA'])):
        for f in fields:
            np.testing.assert_allclose(ours[metric][f], ref[metric][f], rtol=0, atol=1e-12)


def test_bridge_idf1_matches_repo_metrics():
    rng = np.random.default_rng(2)
    gt = moving(jitter=0.5, rng=rng)
    tracks = noisy_tracker(gt, rng)
    fl = lambda a: [[(int(i), list(b)) for f, i, *b in a if f == t] for t in range(1, 61)]
    assert summarize([evaluate_sequence(tracks, gt, 60)])['IDF1'] == pytest.approx(
        compute_tracking_metrics(fl(tracks), fl(gt)).idf1, abs=1e-12)


def test_summarize_perfect_and_empty():
    gt = moving()
    perfect = summarize([evaluate_sequence(gt, gt, 60)])
    assert perfect['IDF1'] == pytest.approx(1) and perfect['HOTA50'] == pytest.approx(1)
    assert summarize([evaluate_sequence(np.empty((0, 6)), gt, 60)])['IDF1'] == 0


@pytest.mark.parametrize('name', sorted(TRACKERS))
def test_trackers_follow_clean_detections(name):
    gt = moving()
    dets = np.column_stack([gt[:, 0], gt[:, 2:6], np.full(len(gt), 0.9)])
    tracks = run_tracker(name, dets, frame_rate=30, n_frames=60)
    assert summarize([evaluate_sequence(tracks, gt, 60)])['IDF1'] > 0.9


def seq(dataset, gt_rows, n_frames=10):
    return D.Sequence(dataset, 'S', 30.0, n_frames, np.array(gt_rows, float), np.empty((0, 9)))


def test_mot17_preprocessing_follows_trackeval():
    s = seq('mot17', [[1, 1, 0, 0, 10, 20, 1, 1, 1],      # pedestrian
                      [1, 2, 100, 0, 10, 20, 0, 8, 1],    # distractor
                      [1, 3, 200, 0, 10, 20, 0, 1, 1]])   # zero-marked pedestrian
    tracks = np.array([[1, 7, 0, 0, 10, 20], [1, 8, 100, 0, 110, 20], [1, 9, 200, 0, 210, 20],
                       [1, 10, 400, 0, 410, 20]], float)
    kept = D.preprocess(s, tracks)
    assert sorted(kept[:, 1]) == [7, 9, 10]                # only the distractor match is dropped
    assert D.gt_true(s, 'person')[:, 1].tolist() == [1]


def test_fasttrack_ignore_regions_and_class_mapping():
    s = seq('fasttrack', [[1, 1, 0, 0, 50, 50, 1, 9, 1],     # ignore_region
                          [1, 2, 200, 0, 20, 20, 1, 2, 1],   # bus_small
                          [1, 3, 300, 0, 20, 20, 1, 3, 1],   # bus_big
                          [1, 4, 400, 0, 20, 20, 1, 6, 1]])  # car
    tracks = np.array([[1, 1, 10, 10, 30, 30], [1, 2, 40, 40, 80, 80], [2, 3, 10, 10, 30, 30]], float)
    assert D.preprocess(s, tracks)[:, 1].tolist() == [2, 3]  # centre (20,20) inside the frame-1 ignore box
    assert sorted(D.gt_true(s, 'bus')[:, 1]) == [2, 3] and D.gt_true(s, 'car')[:, 1].tolist() == [4]


def test_load_and_class_dets(tmp_path):
    d = tmp_path / 'task_x'
    d.mkdir()
    (d / 'seqinfo.ini').write_text('[Sequence]\nname=task_x\nframeRate=25\nseqLength=3\n')
    (d / 'gt.txt').write_text('1,1,0,0,10,10,1,6,1\n4,1,0,0,10,10,1,6,1\n')
    (d / 'det_m.txt').write_text('1,-1,0,0,10,10,0.9,2,-1\n1,-1,5,5,10,10,0.8,0,-1\n')
    s = D.load(d, 'fasttrack', 'm')
    assert (s.frame_rate, s.n_frames) == (25.0, 3)
    assert D.gt_true(s, 'car').tolist() == [[1, 1, 0, 0, 10, 10]]       # frame 4 > seqLength dropped
    assert D.class_dets(s, 'car').tolist() == [[1, 0, 0, 10, 10, 0.9]]
