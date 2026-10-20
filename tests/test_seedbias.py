import json

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
    kept = D.preprocess(s, tracks, 'person')
    assert sorted(kept[:, 1]) == [7, 9, 10]                # only the distractor match is dropped
    assert D.gt_true(s, 'person')[:, 1].tolist() == [1]


def test_fasttrack_ignore_regions_and_class_mapping():
    s = seq('fasttrack', [[1, 1, 0, 0, 50, 50, 1, 9, 1],     # ignore_region
                          [1, 2, 200, 0, 20, 20, 1, 2, 1],   # bus_small
                          [1, 3, 300, 0, 20, 20, 1, 3, 1],   # bus_big
                          [1, 4, 400, 0, 20, 20, 1, 6, 1]])  # car
    tracks = np.array([[1, 1, 10, 10, 30, 30], [1, 2, 40, 40, 80, 80], [2, 3, 10, 10, 30, 30]], float)
    assert D.preprocess(s, tracks, 'car')[:, 1].tolist() == [2, 3]  # centre (20,20) inside the frame-1 ignore box
    assert sorted(D.gt_true(s, 'bus')[:, 1]) == [2, 3] and D.gt_true(s, 'car')[:, 1].tolist() == [4]


def test_load_and_class_dets(tmp_path):
    d = tmp_path / 'task_x'
    d.mkdir()
    (d / 'seqinfo.ini').write_text('[Sequence]\nname=task_x\nframeRate=25\nseqLength=3\n')
    (d / 'gt.txt').write_text('1,1,0,0,10,10,1,6,1\n4,1,0,0,10,10,1,6,1\n')
    (d / 'det_m.txt').write_text('1,-1,0,0,10,10,0.9,2,-1\n1,-1,5,5,10,10,0.8,0,-1\n')
    (d / 'labels.txt').write_text('\n'.join(D.SPEC['fasttrack']['labels']) + '\n')
    s = D.load(d, 'fasttrack', 'm')
    assert (s.frame_rate, s.n_frames) == (25.0, 3)
    assert D.gt_true(s, 'car').tolist() == [[1, 1, 0, 0, 10, 10]]       # frame 4 > seqLength dropped
    assert D.class_dets(s, 'car').tolist() == [[1, 0, 0, 10, 10, 0.9]]


def test_fasttrack_labels_must_match_the_mapping(tmp_path):
    d = tmp_path / 'task_y'
    d.mkdir()
    (d / 'seqinfo.ini').write_text('[Sequence]\nname=task_y\nframeRate=25\nseqLength=3\n')
    (d / 'gt.txt').write_text('1,1,0,0,10,10,1,6,1\n')
    (d / 'det_m.txt').write_text('')
    (d / 'labels.txt').write_text('car\nperson\n')
    with pytest.raises(ValueError):
        D.load(d, 'fasttrack', 'm')


def test_fasttrack_ignore_keeps_boxes_matched_to_gt():
    s = seq('fasttrack', [[1, 1, 0, 0, 100, 100, 1, 9, 1],   # big ignore region
                          [1, 2, 10, 10, 20, 20, 1, 6, 1]])  # a car inside it
    tracks = np.array([[1, 1, 11, 10, 31, 30], [1, 2, 60, 60, 80, 80]], float)
    assert D.preprocess(s, tracks, 'car')[:, 1].tolist() == [1]   # matched car kept, unmatched box dropped


def official_preproc(tmp_path, gt_raw, tracks, n_frames):
    """TrackEval's file-based MOT17 evaluation with its own preprocessing on."""
    import trackeval
    from code.annotation_sim.simulate import write_mot
    seq_name = 'MOT17-99-FRCNN'
    gdir = tmp_path / 'gt' / 'MOT17-train' / seq_name
    (gdir / 'gt').mkdir(parents=True)
    (gdir / 'gt' / 'gt.txt').write_text('\n'.join(','.join(f'{v:g}' for v in r) for r in gt_raw) + '\n')
    (gdir / 'seqinfo.ini').write_text(f'[Sequence]\nname={seq_name}\nseqLength={n_frames}\n')
    tdir = tmp_path / 'trk' / 'MOT17-train' / 'T' / 'data'
    tdir.mkdir(parents=True)
    write_mot(tdir / f'{seq_name}.txt', tracks)
    (tmp_path / 'seqmap.txt').write_text(f'name\n{seq_name}\n')
    ev = trackeval.Evaluator({'USE_PARALLEL': False, 'PRINT_RESULTS': False, 'PRINT_CONFIG': False,
                              'OUTPUT_SUMMARY': False, 'OUTPUT_DETAILED': False, 'PLOT_CURVES': False,
                              'TIME_PROGRESS': False, 'DISPLAY_LESS_PROGRESS': True})
    ds = trackeval.datasets.MotChallenge2DBox({
        'GT_FOLDER': str(tmp_path / 'gt'), 'TRACKERS_FOLDER': str(tmp_path / 'trk'), 'BENCHMARK': 'MOT17',
        'SPLIT_TO_EVAL': 'train', 'TRACKERS_TO_EVAL': ['T'], 'SEQMAP_FILE': str(tmp_path / 'seqmap.txt'),
        'DO_PREPROC': True, 'PRINT_CONFIG': False})
    res, _ = ev.evaluate([ds], [trackeval.metrics.CLEAR({'PRINT_CONFIG': False}),
                                trackeval.metrics.Identity({'PRINT_CONFIG': False})])
    return res['MotChallenge2DBox']['T'][seq_name]['pedestrian']


def test_mot17_preprocessing_equals_official_trackeval_with_ties(tmp_path):
    from code.annotation_sim.simulate import read_mot, write_mot
    rng = np.random.default_rng(11)
    for trial in range(25):
        n_frames, rows = 6, []
        for f in range(1, n_frames + 1):
            for gid in range(1, 7):
                x, y = 10 * rng.integers(0, 6), 10 * rng.integers(0, 3)     # coarse grid → exact ties
                cls = int(rng.choice([1, 1, 1, 2, 7, 8, 12, 3]))
                consider = 1 if cls == 1 and rng.random() > 0.2 else 0
                rows.append([f, gid, x, y, 20, 40, consider, cls, 1])
        gt_raw = np.array(rows, float)
        xy = np.array([[10 * rng.integers(0, 6), 10 * rng.integers(0, 3)] for _ in range(n_frames * 5)], float)
        xy += rng.uniform(-3, 3, xy.shape)
        frames_ids = np.array([[f, t] for f in range(1, n_frames + 1) for t in range(1, 6)], float)
        tracks = np.column_stack([frames_ids, xy, xy + [20, 40]])
        s = seq('mot17', gt_raw, n_frames)
        path = tmp_path / f'w{trial}.txt'
        write_mot(path, tracks)
        tracks = read_mot(path)                                  # the 2-decimal file both sides read
        ours = evaluate_sequence(D.preprocess(s, tracks, 'person'), D.gt_true(s, 'person'), n_frames)
        ref = official_preproc(tmp_path / f't{trial}', gt_raw, tracks, n_frames)
        for metric, field in (('Identity', 'IDF1'), ('Identity', 'IDTP'), ('CLEAR', 'MOTA'), ('CLEAR', 'CLR_FP')):
            assert ours[metric][field] == pytest.approx(ref[metric][field], abs=1e-12), (trial, field)


def test_run_tracks_regenerates_outputs_when_inputs_change(tmp_path, capsys):
    from code.seedbias import run_tracks
    seq_dir = tmp_path / 'dets' / 'dancetrack' / 'dancetrack0001'
    seq_dir.mkdir(parents=True)
    (seq_dir / 'seqinfo.ini').write_text('[Sequence]\nname=dancetrack0001\nframeRate=20\nseqLength=30\n')
    gt = moving(n_obj=2, T=30)
    (seq_dir / 'gt.txt').write_text(''.join(f'{int(f)},{int(i)},{a},{b},{c - a},{d - b},1,1,1\n' for f, i, a, b, c, d in gt))
    (seq_dir / 'done.json').write_text('{}')

    def write_dets(shift):
        (seq_dir / 'det_yolo11x.txt').write_text(
            ''.join(f'{int(f)},-1,{a + shift},{b},{c - a},{d - b},0.9,0,-1\n' for f, i, a, b, c, d in gt))

    args = ['--dets', str(tmp_path / 'dets'), '--out', str(tmp_path / 'tracks'), '--detectors', 'yolo11x',
            '--trackers', 'sort', '--workers', '1']
    out = tmp_path / 'tracks' / 'dancetrack' / 'yolo11x' / 'dancetrack0001' / 'person' / 'sort.txt'
    write_dets(0)
    run_tracks.main(args)
    first = out.read_text()
    run_tracks.main(args)
    assert '1 track files, 0 to (re)run' in capsys.readouterr().out
    write_dets(25)
    run_tracks.main(args)
    assert '1 track files, 1 to (re)run' in capsys.readouterr().out
    assert out.read_text() != first
    prov = json.loads((tmp_path / 'tracks' / 'provenance_dancetrack.json').read_text())
    assert prov['commit'] and len(prov['source_hash']) == 64


def test_fasttrack_vehicle_merges_car_bus_truck_on_the_fasttrack_files(tmp_path):
    d = tmp_path / 'task_v'
    d.mkdir()
    (d / 'seqinfo.ini').write_text('[Sequence]\nname=task_v\nframeRate=25\nseqLength=3\n')
    (d / 'gt.txt').write_text('1,1,0,0,10,10,1,6,1\n1,2,20,0,10,10,1,2,1\n1,3,40,0,10,10,1,5,1\n1,4,60,0,10,10,1,8,1\n')
    (d / 'det_m.txt').write_text('1,-1,0,0,10,10,0.9,2,-1\n1,-1,40,0,10,10,0.8,7,-1\n1,-1,60,0,10,10,0.8,3,-1\n')
    (d / 'labels.txt').write_text('\n'.join(D.SPEC['fasttrack']['labels']) + '\n')
    s = D.load(d, 'fasttrack_vehicle', 'm')
    assert D.source('fasttrack_vehicle') == 'fasttrack'
    assert sorted(D.gt_true(s, 'vehicle')[:, 1]) == [1, 2, 3]          # car, bus_small, truck_big; not motorbike
    assert len(D.class_dets(s, 'vehicle')) == 2                         # COCO car and truck, not motorcycle
