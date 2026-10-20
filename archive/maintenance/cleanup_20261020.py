"""One-time workspace reorganization; executed from the repository root."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]  # Stored under archive/maintenance after use.
ARCHIVE = ROOT / 'archive'
EXPERIMENTS = (
    'baseline', 'c1_recalibration', 'c1_sweep', 'c2_real', 'c2_real_vnweights',
    'c2_real_vnweights_full_p2', 'c2_sensitivity', 'c2_variants', 'c3_sweep',
    'exp1_C2', 'exp2_C1C2', 'exp3_C1C2C3', 'gate_sweep', 'latency', 'realtime',
    'q1_diagnostic_plan_20261019',
)
HISTORICAL_DOCS = (
    'GT_COMPLETION_20261012.md', 'GT_RECONCILED_20261013.md',
    'GT_AUDIT_RECONCILIATION.md', 'PAPER_STEP1_PROTOCOL.md',
    'Q1_DIAGNOSTIC_EXECUTION_PLAN_20261019.md', 'ACCIDENT_VEHICLE_CLEANING_PLAN.md',
)
DETECTOR_DOCS = (
    'ACCIDENT_DATASET_REVIEW_WORKFLOW.md', 'ACCIDENT_DATA_SPEC.md',
    'DETECTOR_PREVIEW.md', 'DETECTOR_TRIAL_WORKFLOW.md', 'KAGGLE_DETECTOR_TRAINING.md',
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected_state():
    """Fingerprint files without exposing local footage/annotation filenames."""
    result = {}
    for name in ('data', 'weights', 'ket_qua_train', 'experiments/gt_qa',
                 'experiments/gt_newcam', 'experiments/gt_ablation',
                 'experiments/c2_final', 'experiments/c2_real_vnweights_full'):
        directory = ROOT / name
        digest = hashlib.sha256()
        count = size = 0
        review_digest = hashlib.sha256()
        # Footage/frame and detector-label trees can contain hundreds of
        # thousands of files. Their paths are excluded from every move; record
        # their top-level inventory instead of rereading the whole dataset.
        if name == 'data':
            for path in sorted(directory.iterdir()):
                stat = path.stat()
                digest.update(f'{path.name}\0{stat.st_size}\0{stat.st_mtime_ns}\n'.encode())
            result[name] = dict(top_level_metadata_sha256=digest.hexdigest(),
                                protection='No data path or ancestor occurs in the move plan')
            continue
        for path in sorted(p for p in directory.rglob('*') if p.is_file()):
            if '__pycache__' in path.parts:
                continue
            stat = path.stat()
            relative = path.relative_to(ROOT).as_posix()
            digest.update(f'{relative}\0{stat.st_size}\0{stat.st_mtime_ns}\n'.encode())
            if path.suffix.lower() in {'.csv', '.json', '.jsonl', '.txt'}:
                review_digest.update(relative.encode() + b'\0' + sha(path).encode())
            count += 1
            size += stat.st_size
        result[name] = dict(files=count, bytes=size, metadata_sha256=digest.hexdigest(),
                            records_sha256=review_digest.hexdigest())
        print(f'Checked protected state: {name}', flush=True)
    credential = ROOT / 'configs/tele_api.yaml'
    if credential.is_file():
        result['local_credentials'] = dict(sha256=sha(credential))
    return result


def main():
    if ARCHIVE.exists():
        raise RuntimeError('Archive already exists; migration must not run twice')
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    tracked = [p for p in tracked if p]
    moves = [('paper', 'archive/paper')]
    moves += [(f'experiments/{n}', f'archive/experiments/{n}') for n in EXPERIMENTS]
    moves += [('experiments/ablation_synthetic_summary.md',
               'archive/experiments/ablation_synthetic_summary.md')]
    moves += [(f'docs/{n}', f'archive/docs/{n}') for n in HISTORICAL_DOCS]
    moves += [(f'docs/{n}', f'docs/detector/{n}') for n in DETECTOR_DOCS]
    moves += [('docs/GT_REVIEW_WORKFLOW.md', 'archive/docs/GT_REVIEW_WORKFLOW_pre_cleanup.md')]
    moves += [(p, f'tools/launchers/{p}') for p in tracked
              if p.endswith('.cmd') and '/' not in p and p != 'review_gt_duongbatrac.cmd']
    moves += [('code/scripts/make_paper_figures.py', 'archive/tools/make_paper_figures.py')]
    before = protected_state()
    entries = []
    # Validate every absolute source and destination before moving directories.
    for old, new in moves:
        source, destination = (ROOT / old).resolve(), (ROOT / new).resolve()
        source.relative_to(ROOT)
        destination.relative_to(ROOT)
        if not source.exists() or destination.exists():
            raise RuntimeError(f'Invalid move: {old} -> {new}')
        for path in tracked:
            if path == old or path.startswith(old + '/'):
                entries.append(dict(source=path, destination=new + path[len(old):],
                                    sha256_before=sha(ROOT / path)))
    for old, new in moves:
        destination = ROOT / new
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(ROOT / old), str(destination))
    # Archived content and all local artifacts within the moved directories are
    # preserved. Active launchers need the repository, not their new own folder.
    for path in (ROOT / 'tools/launchers').glob('*.cmd'):
        raw = path.read_bytes()
        raw = raw.replace(b'cd /d "%~dp0"', b'cd /d "%~dp0..\\.."')
        path.write_bytes(raw)
    # Stale, ignored agent notes must stop presenting old claims as current scope.
    private = ARCHIVE / 'local-notes'
    private.mkdir(parents=True)
    for name in ('CLAUDE.md', 'SCOPE.md', 'kernel.errors.txt'):
        source = ROOT / name
        if source.exists():
            shutil.move(str(source), str(private / name))
    for entry in entries:
        entry['sha256_after'] = sha(ROOT / entry['destination'])
        entry['content_unchanged'] = entry['sha256_before'] == entry['sha256_after']
    after = protected_state()
    if before != after:
        raise RuntimeError('Protected local state changed; inspect before proceeding')
    manifest = dict(date_local='2026-10-20', baseline_commit=subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
        reason='Separate current tools and evidence from superseded drafts and exploratory runs',
        moves=[dict(source=a, destination=b) for a, b in moves], files=entries,
        protected_state={k: v for k, v in before.items() if k != 'local_credentials'},
        protected_state_unchanged=True, local_credentials_unchanged=True,
        notes=['No new scientific direction approved by cleanup',
               'No footage, annotations, weights, caches or review decisions deleted',
               'Archived scripts retain historical paths; use baseline commit for exact reproduction'])
    (ARCHIVE / 'cleanup_20261020_manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(dict(moved_tracked_files=len(entries),
                         moved_groups=len(moves), protected_state_unchanged=True)))


if __name__ == '__main__':
    main()
