"""
code/seedbias/run_tracks.py
───────────────────────────
Run every tracker on every cached sequence and evaluation class, write the
preprocessed tracks and GT_true, then a baseline table against GT_true.

    python -m code.seedbias.run_tracks --dets data/processed/dets --out data/processed/tracks

Layout: <out>/<dataset>/gt/<seq>/<class>.txt and
        <out>/<dataset>/<detector>/<seq>/<class>/<tracker>.txt
Every output is keyed by the hashes of its inputs, of the preprocessing/tracker source and the
trackers version (<out>/manifest.json); a file is reused only when its key is unchanged, otherwise
it is regenerated. Files are written as .part, then renamed.
"""

from __future__ import annotations

import argparse
import json
import hashlib
import os
from concurrent.futures import ProcessPoolExecutor
from importlib.metadata import version
from pathlib import Path

import numpy as np

from code.annotation_sim.simulate import read_mot, write_mot
from code.seedbias import data as D
from code.seedbias.evaluate import evaluate_sequence, summarize
from code.seedbias.track import TRACKERS, run_tracker
from code.utils.files import git_state, sha256, source_hash

SOURCES = ('code/seedbias/data.py', 'code/seedbias/track.py', 'code/annotation_sim/simulate.py',
           'code/seedbias/evaluate.py')


def _write(path: Path, tracks) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + '.part')
    write_mot(part, tracks)
    os.replace(part, path)


def _key(*parts) -> str:
    return hashlib.sha256('|'.join(map(str, parts)).encode()).hexdigest()


def _job(args):
    dataset, seq_dir, detector, cls, tracker, out = args
    seq = D.load(seq_dir, dataset, detector)
    tracks = run_tracker(tracker, D.class_dets(seq, cls), seq.frame_rate, seq.n_frames)
    _write(out, D.preprocess(seq, tracks, cls))


def sequences(dets_root: Path, dataset: str):
    return sorted(p for p in (dets_root / dataset).iterdir() if (p / 'done.json').exists())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--dets', type=Path, default=Path('data/processed/dets'))
    ap.add_argument('--out', type=Path, default=Path('data/processed/tracks'))
    ap.add_argument('--datasets', nargs='+', default=sorted(D.SPEC))
    ap.add_argument('--detectors', nargs='+', default=['yolo11x', 'yolo11n'])
    ap.add_argument('--trackers', nargs='+', default=sorted(TRACKERS))
    ap.add_argument('--workers', type=int, default=2, help='parallel tracker processes (laptop: keep small)')
    args = ap.parse_args(argv)

    datasets = [d for d in args.datasets if (args.dets / d).is_dir()]
    code_key = source_hash(*SOURCES)
    manifest_path = args.out / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    inputs = {p.relative_to(args.dets).as_posix(): sha256(p)
              for d in datasets for p in sorted((args.dets / d).rglob('*.txt'))}
    rel = lambda p: p.relative_to(args.out).as_posix()
    jobs, keys = [], {}
    for dataset in datasets:
        for seq_dir in sequences(args.dets, dataset):
            gt_seq = D.load(seq_dir, dataset, args.detectors[0])
            info = args.out / dataset / 'gt' / seq_dir.name / 'seqinfo.json'
            info.parent.mkdir(parents=True, exist_ok=True)
            info.write_text(json.dumps({'n_frames': gt_seq.n_frames, 'frame_rate': gt_seq.frame_rate}))
            gt_hash = inputs[f'{dataset}/{seq_dir.name}/gt.txt']
            for cls in D.SPEC[dataset]['classes']:
                gt_file = args.out / dataset / 'gt' / seq_dir.name / f'{cls}.txt'
                key = _key(code_key, gt_hash, cls)
                if not gt_file.exists() or manifest.get(rel(gt_file)) != key:
                    _write(gt_file, D.gt_true(gt_seq, cls))
                    manifest[rel(gt_file)] = key
                for detector in args.detectors:
                    det_hash = inputs[f'{dataset}/{seq_dir.name}/det_{detector}.txt']
                    for tracker in args.trackers:
                        out = args.out / dataset / detector / seq_dir.name / cls / f'{tracker}.txt'
                        keys[rel(out)] = _key(code_key, version('trackers'), gt_hash, det_hash, cls, tracker)
                        jobs.append((dataset, seq_dir, detector, cls, tracker, out))
    todo = [j for j in jobs if not j[-1].exists() or manifest.get(rel(j[-1])) != keys[rel(j[-1])]]
    print(f'{len(jobs)} track files, {len(todo)} to (re)run with {args.workers} workers', flush=True)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for i, (job, _) in enumerate(zip(todo, pool.map(_job, todo)), 1):
            manifest[rel(job[-1])] = keys[rel(job[-1])]
            if i % 20 == 0 or i == len(todo):
                manifest_path.write_text(json.dumps(manifest, indent=0))
                print(f'  {i}/{len(todo)}', flush=True)
    manifest_path.write_text(json.dumps(manifest, indent=0))

    baseline = {}
    for dataset in datasets:
        seqs = sequences(args.dets, dataset)
        for detector in args.detectors:
            for tracker in args.trackers:
                per_seq = []
                for seq_dir in seqs:
                    n_frames = D.load(seq_dir, dataset, detector).n_frames
                    for cls in D.SPEC[dataset]['classes']:
                        per_seq.append(evaluate_sequence(
                            read_mot(args.out / dataset / detector / seq_dir.name / cls / f'{tracker}.txt'),
                            read_mot(args.out / dataset / 'gt' / seq_dir.name / f'{cls}.txt'), n_frames))
                baseline[f'{dataset}/{detector}/{tracker}'] = summarize(per_seq)
                print(dataset, detector, tracker, {k: round(v, 4) for k, v in baseline[f'{dataset}/{detector}/{tracker}'].items()})

    (args.out / 'baseline.json').write_text(json.dumps(baseline, indent=2))
    (args.out / 'provenance.json').write_text(json.dumps({
        **git_state(), 'source_hash': code_key, 'trackers': version('trackers'), 'trackeval_commit': '12c8791b303e0a0b50f753af204249e622d0281a',
        'numpy': np.__version__, 'inputs_sha256': inputs}, indent=2))


if __name__ == '__main__':
    main()
