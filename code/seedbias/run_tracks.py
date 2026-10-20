"""
code/seedbias/run_tracks.py
───────────────────────────
Run every tracker on every cached sequence and evaluation class, write the
preprocessed tracks and GT_true, then a baseline table against GT_true.

    python -m code.seedbias.run_tracks --dets data/processed/dets --out data/processed/tracks

Layout: <out>/<dataset>/gt/<seq>/<class>.txt and
        <out>/<dataset>/<detector>/<seq>/<class>/<tracker>.txt
A finished file is skipped on rerun (files are written as .part, then renamed).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor
from importlib.metadata import version
from pathlib import Path

import numpy as np

from code.annotation_sim.simulate import read_mot, write_mot
from code.seedbias import data as D
from code.seedbias.evaluate import evaluate_sequence, summarize
from code.seedbias.track import TRACKERS, run_tracker
from code.utils.files import sha256


def _write(path: Path, tracks) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + '.part')
    write_mot(part, tracks)
    os.replace(part, path)


def _job(args):
    dataset, seq_dir, detector, cls, tracker, out = args
    if out.exists():
        return
    seq = D.load(seq_dir, dataset, detector)
    tracks = run_tracker(tracker, D.class_dets(seq, cls), seq.frame_rate, seq.n_frames)
    _write(out, D.preprocess(seq, tracks))


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
    jobs = []
    for dataset in datasets:
        for seq_dir in sequences(args.dets, dataset):
            gt_seq = D.load(seq_dir, dataset, args.detectors[0])
            for cls in D.SPEC[dataset]['classes']:
                gt_file = args.out / dataset / 'gt' / seq_dir.name / f'{cls}.txt'
                if not gt_file.exists():
                    _write(gt_file, D.gt_true(gt_seq, cls))
                for detector in args.detectors:
                    for tracker in args.trackers:
                        out = args.out / dataset / detector / seq_dir.name / cls / f'{tracker}.txt'
                        jobs.append((dataset, seq_dir, detector, cls, tracker, out))
    todo = [j for j in jobs if not j[-1].exists()]
    print(f'{len(jobs)} track files, {len(todo)} to run with {args.workers} workers', flush=True)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for i, _ in enumerate(pool.map(_job, todo), 1):
            if i % 20 == 0 or i == len(todo):
                print(f'  {i}/{len(todo)}', flush=True)

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

    git = lambda *a: subprocess.run(['git', *a], capture_output=True, text=True).stdout.strip()
    inputs = {p.relative_to(args.dets).as_posix(): sha256(p)
              for d in datasets for p in sorted((args.dets / d).rglob('*.txt'))}
    (args.out / 'baseline.json').write_text(json.dumps(baseline, indent=2))
    (args.out / 'provenance.json').write_text(json.dumps({
        'commit': git('rev-parse', 'HEAD'), 'dirty': bool(git('status', '--porcelain', '--', 'code', 'tools')),
        'trackers': version('trackers'), 'trackeval_commit': '12c8791b303e0a0b50f753af204249e622d0281a',
        'numpy': np.__version__, 'inputs_sha256': inputs}, indent=2))


if __name__ == '__main__':
    main()
