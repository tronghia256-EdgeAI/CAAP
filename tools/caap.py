"""Small entry point for existing CAAP workflows; no implicit experiments."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = {
    'review': ('code.scripts.gt_newcam_review', '--camera', 'duongbatrac_0800'),
    'reproduce': ('code.scripts.run_roi_paper',),
    'detector-review': ('code.scripts.clean_detection_app',),
    'detector-train': ('code.scripts.train_detection_trial',),
    'test': ('pytest',),
}
HELP = """CAAP - current workspace entry point

Usage: caap.cmd <command> [arguments passed to the existing tool]

  status            Show workspace locations (read-only)
  review            Resume DuongBaTrac annotation; no automatic tracker scoring
  reproduce         Existing NKKN development runner (explicit phases)
  detector-review   Open the detector dataset reviewer
  detector-train    Detector trial tool; requires explicit --prepare / --train
  test              Run pytest

Examples:
  caap.cmd status
  caap.cmd review --help
  caap.cmd reproduce --help
  caap.cmd test -q

Historical launchers: tools/launchers/
Current scope: docs/PAPER_SCOPE.md
Evidence and limits: docs/CURRENT_STATE.md
Older manuscripts and experiments: archive/README.md

No command is run when this launcher is opened without arguments.
"""


def status():
    print('CAAP workspace:', ROOT)
    print('Status: reassessing paper direction; no submission-ready claim.')
    for label, relative in (
        ('Scope', 'docs/PAPER_SCOPE.md'),
        ('Current state', 'docs/CURRENT_STATE.md'),
        ('GT review guide', 'docs/GT_REVIEW_WORKFLOW.md'),
        ('DuongBaTrac inputs', 'experiments/gt_newcam/duongbatrac_0800'),
        ('GT review sessions', 'experiments/gt_qa'),
        ('Development results', 'experiments/paper_final'),
        ('Historical snapshots', 'archive'),
    ):
        print(f"  {'OK' if (ROOT / relative).exists() else 'MISSING':7} {label}: {relative}")
    print('GT completeness and test independence require separate human verification.')
    return 0


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ('-h', '--help', 'help'):
        print(HELP)
        return 0
    command, *forwarded = args
    if command == 'status':
        if forwarded:
            print('status takes no arguments.', file=sys.stderr)
            return 2
        return status()
    if command not in COMMANDS:
        print(f'Unknown command: {command}. Use caap.cmd --help.', file=sys.stderr)
        return 2
    module, *defaults = COMMANDS[command]
    if command in ('reproduce', 'detector-train') and not forwarded:
        forwarded = ['--help']
    return subprocess.call([sys.executable, '-X', 'utf8', '-m', module,
                            *defaults, *forwarded], cwd=ROOT)


if __name__ == '__main__':
    raise SystemExit(main())
