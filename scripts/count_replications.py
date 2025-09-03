import pandas as pd
from pathlib import Path

INPUT_CSV = Path("data/results/phase1_lshaped_results.csv")
OUTPUT_CSV = Path("data/results/phase1_number_of_replications.csv")

REQUIRED_COLUMNS = {"outload_key", "num_samples"}

def main():
    if not INPUT_CSV.exists():
        raise SystemExit(f"Input file not found: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise SystemExit(f"Missing required columns in input CSV: {missing}")

    # number_of_replications defined as max(replication) + 1 (replication assumed 0-indexed)
    if "replication" not in df.columns:
        raise SystemExit("Missing 'replication' column required to compute number_of_replications")

    counts = (
        df.groupby(["outload_key", "num_samples"])['replication']
          .max()
          .add(1)
          .astype(int)
          .reset_index(name="number_of_replications")
    )

    # Enforce column order explicitly
    counts = counts[["outload_key", "num_samples", "number_of_replications"]]

    # Sort for readability
    counts = counts.sort_values(["outload_key", "num_samples"]).reset_index(drop=True)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    counts.to_csv(OUTPUT_CSV, index=False)

    print(f"Wrote {len(counts)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
