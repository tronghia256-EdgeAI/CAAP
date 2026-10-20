"""
code/seedbias/external_seed.py
──────────────────────────────
Exploratory (PROTOCOL.md A8 item 2): an external, appearance-based seed on
MOT17 — MPNTrack's MOT17-train outputs shipped with TrackEval's example data
(FRCNN sequences). MPNTrack was trained on MOT17 train, so it is a low-error
seed and is not ranked; the question is whether a seed with appearance cues
and its own detections still gives an advantage over our eight systems.

    python -m code.seedbias.external_seed --mpn data/raw/trackeval_example/mpntrack
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from code.annotation_sim.simulate import Reviewer, _validated, prepare, read_mot, simulate
from code.seedbias import analysis as AN
from code.seedbias import data as D
from code.seedbias import experiment as E

QS = (0, 0.5, 0.9, 1)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--mpn', type=Path, default=Path('data/raw/trackeval_example/mpntrack'))
    ap.add_argument('--tracks', type=Path, default=Path('data/processed/tracks'))
    ap.add_argument('--dets', type=Path, default=Path('data/processed/dets'))
    ap.add_argument('--out', type=Path, default=Path('results/external_seed_mpntrack.json'))
    args = ap.parse_args(argv)

    systems = [f'{d}/{t}' for d in (E.SHARED, E.OTHER) for t in E.TRACKERS]
    units = E.load_units(args.tracks, 'mot17', systems)
    for unit in units:                                   # add the external seed, preprocessed like every system
        seq = D.load(args.dets / 'mot17' / unit.seq, 'mot17', E.SHARED)
        unit.tracks['mpntrack'] = _validated(D.preprocess(seq, read_mot(args.mpn / f'{unit.seq}.txt'), 'person'), 'mpn')
    allsys = systems + ['mpntrack']
    idtp_true, ngt_true, ntr = E.true_scores(units, allsys)
    cells = [dict(E.THETA_REF, q=q) for q in QS]
    idtp = np.zeros((1, len(cells), E.N_SEEDS, len(allsys), len(units)), dtype=np.int64)
    ngt = np.zeros((1, len(cells), E.N_SEEDS, len(units)), dtype=np.int64)
    for u, unit in enumerate(units):
        prep = prepare(unit.tracks['mpntrack'], unit.gt)
        fast = E.FastIdentity(unit, prep.gt, prep.seed)
        for k in range(E.N_SEEDS):
            for c, cell in enumerate(cells):
                out, _, origin = simulate(prep, Reviewer(**cell), E._rng(k, 50, u), with_origin=True)
                ngt[0, c, k, u] = len(out)
                res = fast.idtp(out[:, 1].astype(int), origin)
                idtp[0, c, k, :, u] = [res[s] for s in allsys]
    res = dict(idtp=idtp, ngt=ngt, idtp_true=idtp_true, ngt_true=ngt_true, ntr=ntr)
    seq = np.array([sorted({x.seq for x in units}).index(x.seq) for x in units])
    pooled = AN.Pooled(res, seq)
    seed = [len(allsys) - 1]
    h1 = AN.h1(res, pooled, seed, list(range(len(allsys))), [], cells)
    by_detector = {}
    for c, cell in enumerate(cells):
        sa = AN.sa_matrix(res, pooled, c, seed)[0]                                   # [T, W]
        by_detector[str(cell)] = {det: pooled.ci(sa[[systems.index(s) for s in systems if s.startswith(det)]].mean(0))
                                  for det in (E.SHARED, E.OTHER)}
    out = dict(note='exploratory (A8 item 2); MPNTrack trained on MOT17 train: low-error seed, not ranked',
               idf1_true=dict(zip(allsys, pooled.true[:, 0].tolist())),
               sa_vs_all_eight={str(c['cell']): c['sa_same_detector'] for c in h1},
               sa_by_detector=by_detector,
               id_error_pairs=int(sum(prepare(u.tracks['mpntrack'], u.gt).stats['error_pairs'] for u in units)))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1))
    print('MPNTrack true IDF1', round(out['idf1_true']['mpntrack'], 3))
    for k, v in out['sa_vs_all_eight'].items():
        print(k, round(v['point'], 4), [round(x, 4) for x in v['ci95']])


if __name__ == '__main__':
    main()
