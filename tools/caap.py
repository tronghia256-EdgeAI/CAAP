"""Entry point for the seed-bias research workspace."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = {
    'test': 'pytest',
    'track': 'code.seedbias.run_tracks',
}
HELP = '''CAAP - seed bias in tracker-assisted MOT ground truth

Usage: caap.cmd <command> [tool arguments]
  status             Read-only inventory
  test               Run tests
  track              Run trackers on cached detections, write tracks + baseline

Protocol: docs/PROTOCOL.md. Without a command, only this help is displayed.
'''


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ('help', '-h', '--help'):
        print(HELP)
        return 0
    command, *forwarded = args
    if command == 'status':
        if forwarded:
            return 2
        print('Workspace:', ROOT)
        for relative in ('docs/PROTOCOL.md', 'code/evaluation', 'weights/yolo11n.pt', 'data/raw/fasttrack'):
            print(('OK      ' if (ROOT / relative).exists() else 'MISSING ') + relative)
        return 0
    if command not in COMMANDS:
        print(f'Unknown command: {command}. Use caap.cmd --help.', file=sys.stderr)
        return 2
    return subprocess.call([sys.executable, '-X', 'utf8', '-m', COMMANDS[command], *forwarded], cwd=ROOT)


if __name__ == '__main__':
    raise SystemExit(main())
