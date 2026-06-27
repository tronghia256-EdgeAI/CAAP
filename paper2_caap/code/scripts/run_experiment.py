"""
code/scripts/run_experiment.py
───────────────────────────────
CLI entry point for running a single ablation experiment.

Usage:
    python code/scripts/run_experiment.py --config configs/baseline.yaml
    python code/scripts/run_experiment.py --config configs/exp3_full.yaml

Author  : Trọng Nghĩa
"""

import argparse

# TODO: import Pipeline, evaluation utilities


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a Paper 2 ablation experiment."
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to YAML config file (e.g. configs/default.yaml)",
    )
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Override video source path from config.",
    )
    parser.add_argument(
        "--save-metrics",
        action="store_true",
        help="Save metrics JSON to experiments/ folder.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # TODO: 1. Load config from args.config
    # TODO: 2. Build Pipeline from config
    # TODO: 3. Open video source
    # TODO: 4. Run frame loop
    # TODO: 5. Collect metrics each frame
    # TODO: 6. Compute and print final metrics
    # TODO: 7. If --save-metrics, write JSON to experiments/

    raise NotImplementedError("run_experiment.py not yet implemented")


if __name__ == "__main__":
    main()
