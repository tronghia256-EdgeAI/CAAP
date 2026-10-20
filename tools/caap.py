"""Entry point for the minimal detector/baseline workspace."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = {
    'test': 'pytest',
    'detector-review': 'code.scripts.clean_detection_app',
    'detector-train': 'code.scripts.train_detection_trial',
    'detector-package': 'code.scripts.package_kaggle_detection',
    'detector-preview': 'code.scripts.preview_trained_detector',
}
HELP = '''CAAP - fresh workspace

Usage: caap.cmd <command> [tool arguments]
  status             Read-only inventory
  test               Run retained tests
  detector-review    Review the detector training dataset
  detector-train     Training tool (explicit --prepare / --train required)
  detector-package   Prepare a private training package (no upload)
  detector-preview   Preview tool (explicit arguments required)

No tracking GT, old experiment runner or paper pipeline is active.
Without a command, only this help is displayed.
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
        print('Fresh workspace:', ROOT)
        for relative in ('data/raw', 'data/annotations/accident_vehicle',
                         'data/annotations/accident_vehicle_clean', 'weights/detector.pt',
                         'training/detector', 'code/tracker/vendor'):
            print(('OK      ' if (ROOT / relative).exists() else 'MISSING ') + relative)
        print('Tracking GT: none. New paper protocol: not defined.')
        return 0
    if command not in COMMANDS:
        print(f'Unknown command: {command}. Use caap.cmd --help.', file=sys.stderr)
        return 2
    if command in ('detector-train', 'detector-package', 'detector-preview') and not forwarded:
        forwarded = ['--help']
    return subprocess.call([sys.executable, '-X', 'utf8', '-m', COMMANDS[command], *forwarded], cwd=ROOT)


if __name__ == '__main__':
    raise SystemExit(main())
