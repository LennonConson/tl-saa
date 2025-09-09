#!/usr/bin/env python3
"""Black & white faceted histogram for replication counts by num_samples.

Input CSV columns required:
  outload_key, num_samples, number_of_replications

Chart:
    x-axis: number_of_replications (integer levels)
    y-axis: frequency (count of outload_key rows producing that number of replications)
    Faceted: one subplot per num_samples value (default 2,4,6), rendered as black-outline, white-fill bars with count labels.

Run with no arguments to use hardcoded defaults:
  input  = data/results/phase1_number_of_replications.csv
  output = data/results/replications_stacked_faceted_bw.pdf

Options (if passing arguments):
  --usetex  Enable LaTeX rendering
  --samples Subset/order of num_samples values (e.g. 2 4 6)
  --pgf     Also emit PGF file
  --min-count / --max-count to control x-axis range
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Hardcoded defaults for zero-argument execution
DEFAULT_INPUT = Path("data/results/phase1_number_of_replications.csv")
DEFAULT_OUTPUT = Path("data/results/replications_stacked_faceted_bw.pdf")
DEFAULT_PGF = None
DEFAULT_SAMPLES = [2, 4, 6]
DEFAULT_FACET = True
DEFAULT_USETEX = False

MARKER = ('o', '-')  # retained if we later re-enable lollipop option (unused now)


def parse_args():
    p = argparse.ArgumentParser(description="Bar frequency chart for replication counts")
    p.add_argument('--input', type=Path, required=True, help='Input CSV file')
    p.add_argument('--output', type=Path, required=True, help='Output PDF (or other format)')
    p.add_argument('--pgf', type=Path, help='Optional PGF output for LaTeX inclusion')
    p.add_argument('--samples', type=int, nargs='*', help='Subset/order of num_samples values (e.g. 2 4 6)')
    p.add_argument('--usetex', action='store_true', help='Enable LaTeX text rendering (requires TeX)')
    p.add_argument('--min-count', type=int, help='Minimum x (number_of_replications) to display')
    p.add_argument('--max-count', type=int, help='Maximum x (number_of_replications) to display')
    p.add_argument('--facet', action='store_true', help='Facet into subplots by num_samples')
    if len(sys.argv) == 1:
        return argparse.Namespace(
            input=DEFAULT_INPUT,
            output=DEFAULT_OUTPUT,
            pgf=DEFAULT_PGF,
            samples=DEFAULT_SAMPLES,
            usetex=DEFAULT_USETEX,
            min_count=None,
            max_count=None,
            facet=DEFAULT_FACET,
        )
    return p.parse_args()


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    needed = {"outload_key", "num_samples", "number_of_replications"}
    miss = needed - set(df.columns)
    if miss:
        raise SystemExit(f"Missing columns: {miss}")
    return df


def compute_freq(df: pd.DataFrame, samples: list[int] | None):
    if samples:
        df = df[df['num_samples'].isin(samples)]
    freq = (df.groupby(['num_samples', 'number_of_replications'])
              .size()
              .reset_index(name='count'))
    return freq


def plot_faceted(freq: pd.DataFrame, output: Path, pgf: Path | None, usetex: bool, samples_order: list[int], min_count: int | None, max_count: int | None):
    plt.rcParams.update({
        'figure.dpi': 150,
        'font.size': 10,
        'axes.edgecolor': 'black',
        'axes.labelcolor': 'black',
        'text.color': 'black',
        'xtick.color': 'black',
        'ytick.color': 'black',
        'text.usetex': usetex,
        'axes.unicode_minus': False,
    })

    # Determine global x & y ranges
    overall_min = freq['number_of_replications'].min() if min_count is None else min_count
    overall_max = freq['number_of_replications'].max() if max_count is None else max_count
    ymax = freq['count'].max()

    n = len(samples_order)
    fig, axes = plt.subplots(1, n, figsize=(1.9*n, 2.2), sharey=True)
    if n == 1:
        axes = [axes]

    for ax, s in zip(axes, samples_order):
        sub = (freq[freq.num_samples==s]
                 .sort_values('number_of_replications'))
        # Ensure full x range (insert missing counts with zero freq)
        existing = set(sub['number_of_replications'])
        filler_rows = []
        for c in range(overall_min, overall_max+1):
            if c not in existing:
                filler_rows.append({'num_samples': s, 'number_of_replications': c, 'count': 0})
        if filler_rows:
            sub = pd.concat([sub, pd.DataFrame(filler_rows)], ignore_index=True).sort_values('number_of_replications')
        x = sub['number_of_replications'].values
        y = sub['count'].values
        bars = ax.bar(x, y, color='white', edgecolor='black', width=0.65, linewidth=0.8)
        for rect in bars:
            h = rect.get_height()
            if h > 0:
                ax.text(rect.get_x() + rect.get_width()/2.0, h + max(0.05, ymax*0.015), f"{int(h)}", ha='center', va='bottom', fontsize=7)
        ax.set_title(f"Samples = {s}", pad=4)
        ax.set_xlim(overall_min - 0.4, overall_max + 0.4)
        ax.set_xticks(range(overall_min, overall_max+1))
        ax.set_ylim(0, ymax*1.1 + 0.5)
        ax.yaxis.get_major_locator().set_params(integer=True)
        if ax is axes[0]:
            ax.set_ylabel('Frequency')
        ax.set_xlabel('Replications')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    fig.tight_layout(w_pad=0.6)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches='tight')
    if pgf is not None:
        pgf.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(pgf)
    plt.close(fig)


def main():
    args = parse_args()
    df = load_data(args.input)
    freq = compute_freq(df, args.samples)
    samples_order = sorted(freq['num_samples'].unique())
    if args.samples:
        samples_order = [s for s in args.samples if s in samples_order]
    plot_faceted(freq, args.output, args.pgf, args.usetex, samples_order, args.min_count, args.max_count)
    print(f"Saved replications bar chart to {args.output}" + (f" and {args.pgf}" if args.pgf else ""))

if __name__ == '__main__':
    main()
