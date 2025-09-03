#!/usr/bin/env python3
"""Black & white faceted histogram of replication counts by num_samples.

Input CSV columns required:
  outload_key, num_samples, number_of_replications

Chart:
    x-axis: number_of_replications (integer levels)
    y-axis: frequency (count of outload_key rows producing that replication depth)
    Faceted (side-by-side histograms) for num_samples (2,4,6) in black & white, LaTeX friendly.

Outputs PDF by default; optional PGF for LaTeX inclusion.

Usage example:
  python scripts/plot_replications_lollipop_bw.py \
      --input data/results/phase1_number_of_replications.csv \
      --output data/results/replications_lollipop_bw.pdf

Optional:
    --pgf data/results/replications_hist_bw.pgf
    --min-rep 1 --max-rep 7
    --samples 2 4 6   (filter/ordering)
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

MARKER_STYLE = {
    2: ('o', '-'),
    4: ('o', '-'),
    6: ('o', '-'),
}

DEFAULT_MARKERS = [('o','-')] * 4

# Hardcoded defaults for zero-argument execution
DEFAULT_INPUT = Path("data/results/phase1_number_of_replications.csv")
DEFAULT_OUTPUT = Path("data/results/replications_lollipop_faceted_bw.pdf")
DEFAULT_PGF = None  # e.g., Path("data/results/replications_lollipop_faceted_bw.pgf") if desired
DEFAULT_MIN_REP = 3  # adjusted per request to start at replication level 3
DEFAULT_MAX_REP = 7
DEFAULT_SAMPLES = [2, 4, 6]
DEFAULT_FACET = True
DEFAULT_USETEX = False

def parse_args():
    p = argparse.ArgumentParser(description="Black & white lollipop frequency chart")
    p.add_argument('--input', type=Path, required=True, help='Input CSV file')
    p.add_argument('--output', type=Path, required=True, help='Output PDF (or other format)')
    p.add_argument('--pgf', type=Path, help='Optional PGF output for LaTeX')
    p.add_argument('--min-rep', type=int, default=1, help='Minimum replication level to display (default 1)')
    p.add_argument('--max-rep', type=int, default=7, help='Maximum replication level to display (default 7)')
    p.add_argument('--samples', type=int, nargs='*', help='Subset/order of num_samples values to plot (e.g. 2 4 6)')
    p.add_argument('--usetex', action='store_true', help='Enable LaTeX text rendering (requires TeX)')
    p.add_argument('--facet', action='store_true', help='Create separate side-by-side subplots for each num_samples value')
    if len(sys.argv) == 1:
        # No arguments provided: return namespace with hardcoded defaults
        return argparse.Namespace(
            input=DEFAULT_INPUT,
            output=DEFAULT_OUTPUT,
            pgf=DEFAULT_PGF,
            min_rep=DEFAULT_MIN_REP,
            max_rep=DEFAULT_MAX_REP,
            samples=DEFAULT_SAMPLES,
            usetex=DEFAULT_USETEX,
            facet=DEFAULT_FACET,
        )
    return p.parse_args()

def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    needed = {"outload_key", "num_samples", "number_of_replications"}
    missing = needed - set(df.columns)
    if missing:
        raise SystemExit(f"Missing columns: {missing}")
    return df

def compute_freq(df: pd.DataFrame, min_rep: int, max_rep: int, samples: list[int] | None):
    if samples:
        df = df[df['num_samples'].isin(samples)]
    freq = (df.groupby(['num_samples','number_of_replications'])
              .size()
              .reset_index(name='count'))
    # Ensure full replication grid
    rep_levels = list(range(min_rep, max_rep+1))
    all_rows = []
    for s in sorted(freq['num_samples'].unique()):
        existing = {(r, ) for r in freq[freq.num_samples==s]['number_of_replications']}
        for r in rep_levels:
            sub = freq[(freq.num_samples==s) & (freq.number_of_replications==r)]
            if sub.empty:
                all_rows.append({'num_samples': s, 'number_of_replications': r, 'count': 0})
    if all_rows:
        freq = pd.concat([freq, pd.DataFrame(all_rows)], ignore_index=True)
    return freq

def plot_lollipop(freq: pd.DataFrame, output: Path, pgf: Path | None, min_rep: int, max_rep: int, usetex: bool):
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

    fig, ax = plt.subplots(figsize=(3.1, 2.2))

    samples_order = sorted(freq['num_samples'].unique())
    # If user gave specific order, preserve by re-sorting with key of index in that list
    # We'll detect if MARKER_STYLE covers; else assign from fallback cycle.

    fallback_iter = iter(DEFAULT_MARKERS)
    for s in samples_order:
        style = MARKER_STYLE.get(s)
        if style is None:
            try:
                style = next(fallback_iter)
            except StopIteration:
                style = ('o','-')
        marker, linestyle = style
        sub = (freq[freq.num_samples==s]
                 .sort_values('number_of_replications'))
        x = sub['number_of_replications'].values
        y = sub['count'].values
        # Draw stems
        for xi, yi in zip(x, y):
            ax.vlines(x=xi, ymin=0, ymax=yi, colors='black', linewidth=0.8)
        # Draw markers
        ax.plot(x, y, linestyle=linestyle, marker=marker, color='black', label=f"{s}", markersize=4, linewidth=0.9)
        # Optional: annotate counts just above markers (commented out)
        # for xi, yi in zip(x,y):
        #     if yi>0:
        #         ax.text(xi, yi+0.3, str(int(yi)), ha='center', va='bottom', fontsize=7)

    ax.set_xlabel('Replications Level')
    ax.set_ylabel('Frequency')
    ax.set_xlim(min_rep-0.4, max_rep+0.4)
    ax.set_xticks(range(min_rep, max_rep+1))
    # y-axis integer ticks only
    ymax = freq['count'].max()
    ax.set_ylim(0, ymax*1.1 + 0.5)
    ax.yaxis.get_major_locator().set_params(integer=True)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    leg = ax.legend(title='Samples', loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=False, handlelength=1.2, handletextpad=0.5)

    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches='tight')
    if pgf is not None:
        pgf.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(pgf)
    plt.close(fig)


def plot_lollipop_faceted(freq: pd.DataFrame, output: Path, pgf: Path | None, min_rep: int, max_rep: int, usetex: bool, samples_order: list[int]):
    """(Repurposed) Plot faceted histograms (one per num_samples)."""
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

    n = len(samples_order)
    fig, axes = plt.subplots(1, n, figsize=(1.9*n, 2.2), sharey=True)
    if n == 1:
        axes = [axes]

    # Determine global y max for consistent scaling
    ymax = freq['count'].max()
    bar_width = 0.65

    for ax, s in zip(axes, samples_order):
        sub = (freq[freq.num_samples==s]
                 .sort_values('number_of_replications'))
        x = sub['number_of_replications'].values
        y = sub['count'].values
        bars = ax.bar(x, y, color='white', edgecolor='black', width=bar_width, linewidth=0.8)
        # Add small horizontal baseline for clarity (optional)
        ax.hlines(0, min_rep-0.5, max_rep+0.5, colors='black', linewidth=0.6)
        ax.set_title(f"Samples = {s}", pad=4)
        ax.set_xlim(min_rep-0.5, max_rep+0.5)
        ax.set_xticks(range(min_rep, max_rep+1))
        ax.set_ylim(0, ymax*1.1 + 0.5)
        ax.yaxis.get_major_locator().set_params(integer=True)
        if ax is axes[0]:
            ax.set_ylabel('Frequency')
        else:
            ax.set_ylabel('')
        ax.set_xlabel('Replications')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Annotate bar counts
        for rect in bars:
            height = rect.get_height()
            if height > 0:
                ax.text(rect.get_x() + rect.get_width()/2.0, height + max(0.05, ymax*0.015), f"{int(height)}",
                        ha='center', va='bottom', fontsize=7)

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
    freq = compute_freq(df, args.min_rep, args.max_rep, args.samples)
    # Determine order of samples for faceting or grouped plot
    samples_order = sorted(freq['num_samples'].unique())
    if args.samples:
        # Preserve provided order and filter to those present
        samples_order = [s for s in args.samples if s in samples_order]

    if args.facet:
        plot_lollipop_faceted(freq, args.output, args.pgf, args.min_rep, args.max_rep, args.usetex, samples_order)
        print(f"Saved faceted lollipop chart to {args.output}" + (f" and {args.pgf}" if args.pgf else ""))
    else:
        plot_lollipop(freq, args.output, args.pgf, args.min_rep, args.max_rep, args.usetex)
        print(f"Saved lollipop chart to {args.output}" + (f" and {args.pgf}" if args.pgf else ""))

if __name__ == '__main__':
    main()
