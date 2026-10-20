"""
code/seedbias/figures.py
────────────────────────
Publication figures from the per-dataset summary.json files.

    python -m code.seedbias.figures --in data/processed/seed_bias --out paper/figures

Static journal output: TrueType fonts embedded, physical sizes (single column
3.5 in, double column 7.16 in), text >= 7 pt, light surface, direct labels plus
marker shapes so identity never rests on colour alone (the palette's third slot
is below 3:1 contrast on white; the full numbers are in the manuscript tables).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

DATASETS = (('mot17', 'MOT17'), ('dancetrack', 'DanceTrack'), ('fasttrack', 'FastTrack'))
COLORS = ('#2a78d6', '#eb6834', '#1baf7a')      # categorical slots 1-3, validated on #ffffff
MARKERS = ('o', 's', '^')
INK, MUTED, GRID = '#0b0b0b', '#52514e', '#e1e0d9'
DELTA = 0.01

plt.rcParams.update({
    'pdf.fonttype': 42, 'ps.fonttype': 42, 'font.size': 7.5, 'axes.labelsize': 7.5,
    'xtick.labelsize': 7, 'ytick.labelsize': 7, 'axes.edgecolor': '#c3c2b7', 'axes.labelcolor': INK,
    'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.spines.top': False, 'axes.spines.right': False,
    'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.5, 'lines.linewidth': 1.4,
    'figure.dpi': 300, 'savefig.bbox': 'tight', 'savefig.pad_inches': 0.02,
})


def load(src: Path) -> dict:
    return {d: json.loads((src / d / 'summary.json').read_text()) for d, _ in DATASETS}


def sa_curve(summary, name, values):
    ref = summary['theta_ref']
    cells = {tuple(c['cell'].values()): c['sa_same_detector'] for c in summary['h1']}
    pts = [cells[tuple(dict(ref, **{name: v}).values())] for v in values]
    return [p['point'] for p in pts], [p['ci95'][0] for p in pts], [p['ci95'][1] for p in pts]


def label_end(ax, x, y, text, color, dy=0.0):
    ax.annotate(text, (x, y), xytext=(4, dy), textcoords='offset points', va='center', ha='left',
                fontsize=7, color=INK)


def fig_sa_curves(S, out: Path):
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.4), gridspec_kw=dict(wspace=0.32))
    for ax, (name, values, xlabel) in zip(axes, (
            ('r', (0, 0.25, 0.5, 0.75, 0.9, 1), 'reviewer recall r (missed runs added)'),
            ('q', (0, 0.5, 0.9, 1), 'ID-error fix probability q'))):
        ends = []
        for (key, title), color, marker in zip(DATASETS, COLORS, MARKERS):
            y, lo, hi = sa_curve(S[key], name, values)
            ax.fill_between(values, lo, hi, color=color, alpha=0.15, linewidth=0)
            ax.plot(values, y, color=color, marker=marker, markersize=4, markeredgecolor='white',
                    markeredgewidth=0.6, label=title)
            ends.append((y[-1], title, color))
        direct = name != 'q'                  # endpoints converge near q = 1: there the legend carries identity
        if direct:
            offsets = _spread([e[0] for e in ends], 0.09 * ax.get_ylim()[1])
            for (y_end, title, color), y_lab in zip(ends, offsets):
                ax.annotate(title, (values[-1], y_end), xytext=(values[-1] + (values[-1] - values[0]) * 0.03, y_lab),
                            textcoords='data', va='center', ha='left', fontsize=7, color=INK,
                            arrowprops=dict(arrowstyle='-', color=color, lw=0.6) if abs(y_lab - y_end) > 0.004 else None)
        ax.axhline(DELTA, color=MUTED, linewidth=0.8, linestyle=(0, (3, 2)))
        ref = S['mot17']['theta_ref'][name]
        ax.axvline(ref, color=MUTED, linewidth=0.6, linestyle=(0, (1, 2)), zorder=0)
        ax.annotate('θ$_{ref}$', (ref, 1), xycoords=('data', 'axes fraction'), xytext=(2, -8),
                    textcoords='offset points', fontsize=6.5, color=MUTED)
        ax.annotate('δ', (values[0], DELTA), xytext=(1, 2), textcoords='offset points', fontsize=6.5, color=MUTED)
        ax.set_xlabel(xlabel)
        ax.set_xticks(values)
        ax.set_xticklabels([f'{v:g}' for v in values])
        ax.set_xlim(values[0] - 0.03, values[-1] + (values[-1] - values[0]) * (0.32 if direct else 0.05))
        ax.set_ylim(0, None)
        ax.grid(axis='x', visible=False)
        ax.set_ylabel('self-seed advantage SA (IDF1)')
        ax.set_title('(a)' if name == 'r' else '(b)', loc='left', fontsize=7.5, color=INK)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=3, frameon=False, fontsize=7, bbox_to_anchor=(0.5, 1.06))
    fig.savefig(out / 'fig_sa_curves.pdf')
    plt.close(fig)


def fig_h2(S, out: Path):
    fig, ax = plt.subplots(figsize=(3.5, 2.3))
    ends = []
    for (key, title), color, marker in zip(DATASETS, COLORS, MARKERS):
        rows = S[key]['h2']
        r = [row['cell']['theta']['r'] for row in rows]
        y = [row['a0']['tau_null_minus_seed']['point'] for row in rows]
        lo = [row['a0']['tau_null_minus_seed']['ci95'][0] for row in rows]
        hi = [row['a0']['tau_null_minus_seed']['ci95'][1] for row in rows]
        ax.fill_between(r, lo, hi, color=color, alpha=0.15, linewidth=0)
        ax.plot(r, y, color=color, marker=marker, markersize=4, markeredgecolor='white', markeredgewidth=0.6,
                label=title)
        ends.append((y[-1], title, color))
    for (y_end, title, color), y_lab in zip(ends, _spread([e[0] for e in ends], 0.03)):
        ax.annotate(title, (1, y_end), xytext=(1.03, y_lab), textcoords='data', va='center', fontsize=7, color=INK,
                    arrowprops=dict(arrowstyle='-', color=color, lw=0.6) if abs(y_lab - y_end) > 0.01 else None)
    ax.axhline(0, color='#c3c2b7', linewidth=0.8)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 0.9, 1])
    ax.set_xticklabels(['0', '0.25', '0.5', '0.75', '0.9', '1'])
    ax.grid(axis='x', visible=False)
    ax.set_xlim(-0.03, 1.3)
    ax.set_xlabel('reviewer recall r')
    ax.set_ylabel('τ$_{null}$ − τ$_{seed}$ (Kendall τ-b)')
    ax.legend(loc='upper center', ncol=3, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, 1.15), handlelength=1.6)
    fig.savefig(out / 'fig_h2.pdf')
    plt.close(fig)


def _spread(values, gap):
    """Label positions: the values, pushed apart so neighbours are at least `gap` apart."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    pos = [values[i] for i in order]
    for i in range(1, len(pos)):
        pos[i] = max(pos[i], pos[i - 1] + gap)
    out = [0.0] * len(values)
    for i, p in zip(order, pos):
        out[i] = p
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='src', type=Path, default=Path('data/processed/seed_bias'))
    ap.add_argument('--out', type=Path, default=Path('paper/figures'))
    args = ap.parse_args(argv)
    args.out.mkdir(parents=True, exist_ok=True)
    S = load(args.src)
    fig_sa_curves(S, args.out)
    fig_h2(S, args.out)
    print('written', sorted(p.name for p in args.out.glob('*.pdf')))


if __name__ == '__main__':
    main()
