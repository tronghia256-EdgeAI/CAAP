"""
code/seedbias/reid_check.py
───────────────────────────
Exploratory (PROTOCOL.md A9): an appearance-based (ReID) tracker, BoxMOT BotSort on the same
YOLO11x person boxes (tools/kaggle_reid_track.py), on MOT17 and DanceTrack at θ_ref.

(a) ReID tracker as seed: its SA over the four YOLO11x motion trackers and the four YOLO11n systems,
    at q = 0, 0.5 (θ_ref) and 1.
(b) ReID tracker as an evaluated system: each motion seed's SA over it on the motion seed's GT,
    regenerated with the main run's random streams, against its SA over the other motion trackers.
    The regenerated GTs must reproduce the main run's IDTP for the eight systems exactly.
(c) True IDF1 and ID-error episodes.

    python -m code.seedbias.reid_check --reid data/processed/reid_tracks
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from code.annotation_sim.simulate import Reviewer, prepare, read_mot, simulate, write_mot
from code.seedbias import analysis as AN
from code.seedbias import data as D
from code.seedbias import experiment as E

REID = 'yolo11x/botsort_reid'
QS = (0, 0.5, 1)


def import_tracks(reid_root: Path, tracks: Path, dets: Path, dataset: str) -> None:
    """Kaggle output → preprocessed tracks next to the other systems' (same A2 preprocessing)."""
    for seq_dir in sorted((tracks / dataset / 'gt').iterdir()):
        seq = D.load(dets / dataset / seq_dir.name, dataset, E.SHARED)
        raw = reid_root / dataset / f'{seq_dir.name}.txt'
        if not (reid_root / dataset / f'{seq_dir.name}.done.json').exists():
            raise SystemExit(f'missing ReID output for {dataset}/{seq_dir.name}')
        dest = tracks / dataset / E.SHARED / seq_dir.name / 'person' / 'botsort_reid.txt'
        dest.parent.mkdir(parents=True, exist_ok=True)
        write_mot(dest,D.preprocess(seq, read_mot(raw), 'person'))


def run(dataset: str, args) -> dict:
    import_tracks(args.reid, args.tracks, args.dets, dataset)
    motion = [f'{d}/{t}' for d in (E.SHARED, E.OTHER) for t in E.TRACKERS]
    systems = motion + [REID]
    r = len(motion)                                               # index of the ReID system
    units = E.load_units(args.tracks, dataset, systems)
    idtp_true, ngt_true, ntr = E.true_scores(units, systems)
    seq = np.array([sorted({u.seq for u in units}).index(u.seq) for u in units])
    main = np.load(args.main / dataset / 'arrays.npz')
    n_u, n_t = len(units), len(systems)

    # (b) motion seeds, θ_ref, the main run's random streams
    idtp_b = np.zeros((4, 1, E.N_SEEDS, n_t, n_u), dtype=np.int64)
    ngt_b = np.zeros((4, 1, E.N_SEEDS, n_u), dtype=np.int64)
    # (a) ReID seed, q in QS
    cells = [dict(E.THETA_REF, q=q) for q in QS]
    idtp_a = np.zeros((1, len(cells), E.N_SEEDS, n_t, n_u), dtype=np.int64)
    ngt_a = np.zeros((1, len(cells), E.N_SEEDS, n_u), dtype=np.int64)
    episodes = np.zeros((n_t, n_u), dtype=np.int64)
    for u, unit in enumerate(units):
        for a in range(4):
            prep = prepare(unit.tracks[systems[a]], unit.gt)
            fast = E.FastIdentity(unit, prep.gt, prep.seed)
            for k in range(E.N_SEEDS):
                out, _, origin = simulate(prep, Reviewer(**E.THETA_REF), E._rng(k, a, u), with_origin=True)
                ngt_b[a, 0, k, u] = len(out)
                res = fast.idtp(out[:, 1].astype(int), origin)
                idtp_b[a, 0, k, :, u] = [res[s] for s in systems]
            if not (np.array_equal(idtp_b[a, 0, :, :r, u], main['idtp'][a, E.REF, :, :, u])
                    and np.array_equal(ngt_b[a, 0, :, u], main['ngt'][a, E.REF, :, u])):
                raise SystemExit(f'{dataset}: regenerated GT of {systems[a]} differs from the main run (unit {u})')
        prep = prepare(unit.tracks[REID], unit.gt)
        fast = E.FastIdentity(unit, prep.gt, prep.seed)
        for k in range(E.N_SEEDS):
            for c, cell in enumerate(cells):
                out, _, origin = simulate(prep, Reviewer(**cell), E._rng(k, r, u), with_origin=True)
                ngt_a[0, c, k, u] = len(out)
                res = fast.idtp(out[:, 1].astype(int), origin)
                idtp_a[0, c, k, :, u] = [res[s] for s in systems]
        for t, s in enumerate(systems):
            episodes[t, u] = prepare(unit.tracks[s], unit.gt).n_episodes

    true = dict(idtp_true=idtp_true, ngt_true=ngt_true, ntr=ntr)
    res_a = dict(idtp=idtp_a, ngt=ngt_a, **true)
    pooled = AN.Pooled(res_a, seq)
    h1 = AN.h1(res_a, pooled, [r], [0, 1, 2, 3], [4, 5, 6, 7], cells)
    res_b = dict(idtp=idtp_b, ngt=ngt_b, **true)
    sa = AN.sa_matrix(res_b, AN.Pooled(res_b, seq), 0, [0, 1, 2, 3])                   # [A, T, W]
    over_reid = sa[:, r].mean(0)
    over_motion = np.mean([sa[a, t] for a in range(4) for t in range(4) if t != a], axis=0)
    return dict(
        idf1_true=dict(zip(systems, pooled.true[:, 0].tolist())),
        id_error_episodes=dict(zip(systems, episodes.sum(1).tolist())),
        a_reid_seed={str(h['cell']['q']): dict(over_yolo11x_motion=h['sa_same_detector'],
                                                over_yolo11n=h['sa_other_detector']) for h in h1},
        b_motion_seed_over_reid=pooled.ci(over_reid),
        b_motion_seed_over_motion=pooled.ci(over_motion),
        b_difference=pooled.ci(over_reid - over_motion),
        b_per_seed_over_reid={systems[a]: float(sa[a, r, 0]) for a in range(4)},
    )


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--reid', type=Path, default=Path('data/processed/reid_tracks'))
    ap.add_argument('--tracks', type=Path, default=Path('data/processed/tracks'))
    ap.add_argument('--dets', type=Path, default=Path('data/processed/dets'))
    ap.add_argument('--main', type=Path, default=Path('data/processed/seed_bias'))
    ap.add_argument('--datasets', nargs='+', default=['mot17', 'dancetrack'])
    ap.add_argument('--out', type=Path, default=Path('results/reid_check.json'))
    args = ap.parse_args(argv)
    out = dict(note='exploratory (PROTOCOL.md A9), run after the main results; BoxMOT 25.0.0 BotSort + '
                    'osnet_x0_25_msmt17, use_cmc=False, same YOLO11x person boxes')
    for dataset in args.datasets:
        out[dataset] = run(dataset, args)
        d = out[dataset]
        print(dataset, 'true IDF1 ReID', round(d['idf1_true'][REID], 3),
              '| ReID seed SA vs motion', round(d['a_reid_seed']['0.5']['over_yolo11x_motion']['point'], 4),
              d['a_reid_seed']['0.5']['over_yolo11x_motion']['ci95'],
              '| motion seeds over ReID', round(d['b_motion_seed_over_reid']['point'], 4),
              'vs over motion', round(d['b_motion_seed_over_motion']['point'], 4), flush=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
