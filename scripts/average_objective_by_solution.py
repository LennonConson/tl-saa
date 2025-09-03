#!/usr/bin/env python3
"""Compute average objective value grouped by (outload_key, num_samples, y_open[6..11]).

Reads phase1_lshaped_results.csv and outputs a CSV with:
  outload_key, num_samples, y_open[6], y_open[7], y_open[8], y_open[9], y_open[10], y_open[11], avg_obj, count

Hardcoded defaults allow running with no CLI args.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
import pandas as pd

DEFAULT_INPUT = Path("data/results/phase1_lshaped_results.csv")
DEFAULT_OUTPUT = Path("data/results/average_objective_by_solution.csv")

Y_COLS = [
    "y_open[6]","y_open[7]","y_open[8]","y_open[9]","y_open[10]","y_open[11]"
]

REQUIRED = {"outload_key","num_samples","obj"} | set(Y_COLS)

def parse_args():
    p = argparse.ArgumentParser(description="Average objective by unique solution combination")
    p.add_argument('--input', type=Path, required=True, help='Input phase1_lshaped_results.csv')
    p.add_argument('--output', type=Path, required=True, help='Output CSV path')
    if len(sys.argv) == 1:
        return argparse.Namespace(input=DEFAULT_INPUT, output=DEFAULT_OUTPUT)
    return p.parse_args()


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"Input file not found: {path}")
    df = pd.read_csv(path)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise SystemExit(f"Missing required columns: {missing}")
    return df


def compute(df: pd.DataFrame) -> pd.DataFrame:
    # Drop rows with missing objective just in case
    df = df.dropna(subset=['obj'])
    group_cols = ['outload_key','num_samples', *Y_COLS]
    agg = (df.groupby(group_cols, dropna=False)
             .agg(avg_obj=('obj','mean'), count=('obj','size'))
             .reset_index())
    # Sort for readability
    agg = agg.sort_values(['outload_key','num_samples', *Y_COLS]).reset_index(drop=True)
    return agg


def main():
    args = parse_args()
    df = load_data(args.input)
    result = compute(df)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Wrote {len(result)} grouped rows to {args.output}")

if __name__ == '__main__':
    main()
