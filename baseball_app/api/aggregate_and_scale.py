import os
import argparse
from glob import glob
import pandas as pd
import numpy as np

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", default="processed_data", help="Directory with per-team CSVs")
    p.add_argument("--output-dir", default="aggregated_data", help="Where to write formatted outputs")
    p.add_argument("--level", default=None, help="Level to filter on (e.g. MLB). If omitted, uses all files")
    return p.parse_args()

def read_and_concat(input_dir):
    files = glob(os.path.join(input_dir, "*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {input_dir}")
    dfs = []
    for f in files:
        df = pd.read_csv(f)
        df["__source_file"] = os.path.basename(f)
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True, sort=False)

def compute_z_scaled(series):
    """Return z-score and scaled_0_100 for a numeric series.
       scaled = 50 + z*10 clipped to [0,100].
       If std==0, z=0 for all and scaled=50.
    """
    s = pd.to_numeric(series, errors="coerce")
    mean = s.mean()
    std = s.std(ddof=0)  # population std for deterministic behavior
    if pd.isna(std) or std == 0:
        z = (s - mean).fillna(0) * 0.0
    else:
        z = (s - mean) / std
    scaled = (50.0 + z * 10.0).clip(0.0, 100.0)
    return z, scaled

def get_perf_share():
    """Return performance_share from batter_weights if present, else default 0.7"""
    try:
        import batter_weights as bw
        if hasattr(bw, "WEIGHTS") and isinstance(bw.WEIGHTS, dict) and "performance_share" in bw.WEIGHTS:
            return float(bw.WEIGHTS["performance_share"])
    except Exception:
        pass
    return 0.7

def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    all_df = read_and_concat(args.input_dir)

    # Filter by Level column if provided
    if args.level:
        if "Level" in all_df.columns:
            mask = all_df["Level"].astype(str).str.upper() == str(args.level).upper()
            level_df = all_df[mask].copy()
        else:
            # No Level column -> assume files passed are of the requested level
            level_df = all_df.copy()
    else:
        level_df = all_df.copy()

    if level_df.empty:
        raise SystemExit(f"No players found for level='{args.level}'")

    # Ensure required metric columns exist
    if "PerformanceMetric" not in level_df.columns:
        raise SystemExit("PerformanceMetric not found in input CSVs. Run evaluator first.")
    if "UsageMetric" not in level_df.columns:
        raise SystemExit("UsageMetric not found in input CSVs. Run evaluator first.")

    # Compute scaled PerformanceMetric (0-100)
    _, perf_scaled = compute_z_scaled(level_df["PerformanceMetric"])
    level_df["perf_scaled"] = perf_scaled.round(6)

    # Compute scaled UsageMetric (0-100) using same deterministic mapping
    _, use_scaled = compute_z_scaled(level_df["UsageMetric"])
    level_df["use_scaled"] = use_scaled.round(6)

    # Combined using perf_share
    perf_share = get_perf_share()
    level_df["combined_scaled"] = (perf_share * level_df["perf_scaled"] + (1.0 - perf_share) * level_df["use_scaled"]).round(6)

    # Build the compact output
    # team.csv column will be the filename stored in __source_file
    output_df = pd.DataFrame({
        "Player": level_df.get("Player", ""),
        "B": level_df.get("B", ""),
        "Age": level_df.get("Age", ""),
        "PO": level_df.get("PO", ""),
        "AB": level_df.get("AB", ""),
        "team.csv": level_df.get("__source_file", ""),
        "perf": level_df["perf_scaled"],
        "use": level_df["use_scaled"],
        "combined": level_df["combined_scaled"],
    })

    # Save master aggregated file
    level_tag = args.level.upper() if args.level else "ALL"
    master_out = os.path.join(args.output_dir, f"all_players_{level_tag}_formatted.csv")
    output_df.to_csv(master_out, index=False)
    print(f"Formatted aggregated file written: {master_out} (n={len(output_df)})")

if __name__ == "__main__":
    main()