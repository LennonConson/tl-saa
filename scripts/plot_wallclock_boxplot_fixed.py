#!/usr/bin/env python3
"""Boxplot of wall_clock_time grouped by num_samples (2,4,6) using only is_fixed==True rows.

Reads phase1_lshaped_results.csv and outputs a black & white, LaTeX-friendly
boxplot PDF with optional PGF export. Runs with hardcoded defaults when no
arguments are provided.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Defaults
DEFAULT_INPUT = Path("data/results/phase1_lshaped_results.csv")
DEFAULT_OUTPUT = Path("data/results/fixed_first_wall_clock_boxplot.pdf")
DEFAULT_PGF = None  # e.g., Path("data/results/wall_clock_boxplot_fixed.pgf")
DEFAULT_SAMPLES = [2,4,6]
DEFAULT_USETEX = False


def parse_args():
    p = argparse.ArgumentParser(description="Wall clock time boxplot (is_fixed==True)")
    p.add_argument('--input', type=Path, required=True, help='Input CSV (phase1_lshaped_results.csv)')
    p.add_argument('--output', type=Path, required=True, help='Output PDF path')
    p.add_argument('--pgf', type=Path, help='Optional PGF output path')
    p.add_argument('--samples', type=int, nargs='*', help='Subset/order of num_samples (e.g. 2 4 6)')
    p.add_argument('--usetex', action='store_true', help='Enable LaTeX text rendering (requires TeX)')
    p.add_argument('--logy', action='store_true', help='Use log scale for y-axis')
    if len(sys.argv) == 1:
        return argparse.Namespace(
            input=DEFAULT_INPUT,
            output=DEFAULT_OUTPUT,
            pgf=DEFAULT_PGF,
            samples=DEFAULT_SAMPLES,
            usetex=DEFAULT_USETEX,
            logy=False,
        )
    return p.parse_args()


def load_and_filter(path: Path, samples: list[int] | None) -> pd.DataFrame:
    df = pd.read_csv(path)
    needed = {"num_samples", "is_fixed", "wall_clock_time"}
    miss = needed - set(df.columns)
    if miss:
        raise SystemExit(f"Missing required columns: {miss}")
    # Normalize is_fixed to boolean
    df['is_fixed'] = df['is_fixed'].astype(str).str.lower().map({'true': True, 'false': False})
    df = df[df['is_fixed'] == True]
    if samples:
        df = df[df['num_samples'].isin(samples)]
    if df.empty:
        raise SystemExit("No data after filtering (check is_fixed values or sample set).")
    return df


def make_boxplot(df: pd.DataFrame, output: Path, pgf: Path | None, usetex: bool, logy: bool, samples_order: list[int]):
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
        'boxplot.flierprops.marker': 'o',
        'boxplot.flierprops.markerfacecolor': 'white',
        'boxplot.flierprops.markeredgecolor': 'black',
    })

    # Ensure categorical ordering
    df = df.copy()
    cat_type = pd.CategoricalDtype(categories=samples_order, ordered=True)
    df['num_samples'] = df['num_samples'].astype(cat_type)

    fig, ax = plt.subplots(figsize=(3.0, 2.4))
    sns.boxplot(
        data=df,
        x='num_samples',
        y='wall_clock_time',
        color='white',
        width=0.65,
        fliersize=3,
        linewidth=0.9,
        ax=ax,
        showmeans=False,
        boxprops={'edgecolor': 'black'},
        medianprops={'color': 'black', 'linewidth': 1.1},
        whiskerprops={'color': 'black', 'linewidth': 0.9},
        capprops={'color': 'black', 'linewidth': 0.9},
    )

    ax.set_title('Solve Fixed First-Stage SMIP', pad=6)

    # Add jittered individual observations (optional, can comment out)
    # sns.stripplot(data=df, x='num_samples', y='wall_clock_time', color='black', size=2, jitter=0.15, alpha=0.6, ax=ax)

    # (Median annotations removed per request)

    ax.set_xlabel('Number of Samples')
    ax.set_ylabel('Wall Clock Time (s)')
    if logy:
        ax.set_yscale('log')
        ax.set_ylabel('Wall Clock Time (s, log scale)')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches='tight')
    if pgf is not None:
        pgf.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(pgf)
    plt.close(fig)


def main():
    args = parse_args()
    df = load_and_filter(args.input, args.samples)
    samples_order = sorted(df['num_samples'].unique(), key=lambda x: args.samples.index(x) if args.samples and x in args.samples else x)
    make_boxplot(df, args.output, args.pgf, args.usetex, args.logy, samples_order)
    print(f"Saved wall clock time boxplot to {args.output}" + (f" and {args.pgf}" if args.pgf else ""))

if __name__ == '__main__':
    main()
