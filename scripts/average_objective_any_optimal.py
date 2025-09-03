#!/usr/bin/env python3
"""Compute average objective per (outload_key, num_samples) for fixed solutions.

Filters to rows where is_fixed == True (case-insensitive), then groups by
(outload_key, num_samples) and outputs a CSV with columns:
  outload_key, num_samples, avg_obj

Hardcoded defaults allow running with no arguments.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
import pandas as pd

DEFAULT_INPUT = Path("data/results/phase1_lshaped_results.csv")
DEFAULT_OUTPUT = Path("data/results/average_objective_any_optimal.csv")
REQUIRED_COLS = {"outload_key", "num_samples", "is_fixed", "obj"}

def parse_args():
    p = argparse.ArgumentParser(description="Average objective for is_fixed==True by (outload_key, num_samples)")
    p.add_argument('--input', type=Path, required=True, help='Input CSV (phase1_lshaped_results.csv)')
    p.add_argument('--output', type=Path, required=True, help='Output CSV path')
    if len(sys.argv) == 1:
        return argparse.Namespace(input=DEFAULT_INPUT, output=DEFAULT_OUTPUT)
    return p.parse_args()

def load_filter(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"Input file not found: {path}")
    df = pd.read_csv(path)
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise SystemExit(f"Missing required columns: {missing}")
    # Normalize is_fixed to boolean
    df['is_fixed_norm'] = df['is_fixed'].astype(str).str.lower().map({'true': True, 'false': False})
    df = df[df['is_fixed_norm'] == False]
    if df.empty:
        raise SystemExit("No rows with is_fixed==True after filtering.")
    return df

def compute_avg(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (df.groupby(['outload_key','num_samples'], as_index=False)
                 .agg(avg_obj=('obj','mean')))
    # Sort for readability
    return grouped.sort_values(['outload_key','num_samples']).reset_index(drop=True)

def main():
    args = parse_args()
    df = load_filter(args.input)
    result = compute_avg(df)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    print(f"Wrote {len(result)} rows to {args.output}")

if __name__ == '__main__':
    main()
