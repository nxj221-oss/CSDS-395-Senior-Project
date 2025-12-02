#!/usr/bin/env python3
"""
aggregate_and_scale.py

Reads per-team CSV files from --input-dir, applies level-aware age penalties
(using configs in batter_weights.AGE_PENALTY), computes z-scaled performance
and usage metrics, applies a level multiplier from batter_weights.LEVEL_WEIGHTS,
and writes a compact aggregated CSV per requested level (or ALL if --level omitted).
"""

import os
import argparse
from glob import glob
import pandas as pd
import numpy as np
import math
import sys

import batter_weights as bw

# -----------------------
# CLI
# -----------------------
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", default="processed_data", help="Directory with per-team CSVs")
    p.add_argument("--output-dir", default="aggregated_data", help="Where to write formatted outputs")
    p.add_argument("--level", default=None, help="Level to filter on (e.g. MLB). If omitted, uses all files")
    p.add_argument(
        "--per-level-scale",
        action="store_true",
        help="If set, computes perf/use z-scores within each Level group instead of globally."
    )
    return p.parse_args()

# -----------------------
# IO helpers
# -----------------------
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

# -----------------------
# scaling helpers
# -----------------------
def compute_z_scaled(series):
    s = pd.to_numeric(series, errors="coerce")
    mean = s.mean()
    std = s.std(ddof=0)
    if pd.isna(std) or std == 0:
        z = (s - mean).fillna(0) * 0.0
    else:
        z = (s - mean) / std
    scaled = (50.0 + z * 10.0).clip(0.0, 100.0)
    return z, scaled

def get_perf_share():
    try:
        if hasattr(bw, "performance_weighting_percent"):
            return float(getattr(bw, "performance_weighting_percent"))
    except Exception:
        pass
    try:
        if hasattr(bw, "WEIGHTS") and isinstance(bw.WEIGHTS, dict) and "performance_share" in bw.WEIGHTS:
            return float(bw.WEIGHTS["performance_share"])
    except Exception:
        pass
    return 0.7

# -----------------------
# Age penalty helpers (level-aware)
# -----------------------
def _canonicalize_level(level_str):
    if level_str is None:
        return None
    s = str(level_str).strip()
    if not s:
        return None
    s_up = s.upper()
    if s_up in {"MLB", "AAA", "AA", "A+", "A", "ROOKIE"}:
        if s_up == "A+":
            return "A+"
        if s_up == "ROOKIE":
            return "Rookie"
        return s_up
    cleaned = s_up.replace("HIGHA", "A+").replace("HIGH-A", "A+").replace("HIGH_A", "A+")
    cleaned = cleaned.replace("LOWA", "A").replace("LOW-A", "A").replace("LOW_A", "A")
    cleaned = cleaned.replace("APLUS", "A+").replace("A-ADVANCED", "A+")
    cleaned = cleaned.replace(".", "").replace(" ", "").replace("_", "")
    return cleaned

def _get_age_penalty_config_for_level(level):
    try:
        all_cfg = getattr(bw, "AGE_PENALTY", {}) or {}
        lvl = _canonicalize_level(level) or "default"
        if isinstance(all_cfg, dict):
            if lvl in all_cfg:
                cfg = all_cfg[lvl]
            elif lvl.upper() in all_cfg:
                cfg = all_cfg[lvl.upper()]
            elif lvl.title() in all_cfg:
                cfg = all_cfg[lvl.title()]
            else:
                cfg = all_cfg.get("default", {})
        else:
            cfg = {}
    except Exception:
        cfg = {}
    return {
        "cutoff_age": float(cfg.get("cutoff_age", 33.0)),
        "rate": float(cfg.get("rate", cfg.get("penalty_rate", 0.5))),
        "exponent": float(cfg.get("exponent", 1.25)),
        "min_multiplier": cfg.get("min_multiplier", cfg.get("min_mult", None)),
    }

def compute_age_multiplier(age, level=None):
    try:
        age_val = float(age)
    except Exception:
        return 1.0
    cfg = _get_age_penalty_config_for_level(level)
    cutoff = cfg["cutoff_age"]
    rate = cfg["rate"]
    exponent = cfg["exponent"]
    min_mult = cfg["min_multiplier"]
    if age_val <= cutoff:
        return 1.0
    years_past = age_val - cutoff
    if years_past <= 0:
        return 1.0
    try:
        mult = math.exp(-rate * (years_past ** exponent))
    except Exception:
        mult = 1.0
    if min_mult is not None:
        try:
            mm = float(min_mult)
            mult = max(mm, mult)
        except Exception:
            pass
    mult = max(0.0, min(1.0, float(mult)))
    return mult

def _infer_level_from_source_file(src_filename):
    if not src_filename:
        return None
    name = os.path.basename(str(src_filename))
    if name.lower().endswith(".csv"):
        name = name[:-4]
    parts = name.replace("_", "-").split("-")
    last = parts[-1].strip()
    last_up = last.upper()
    if last_up in ("MLB", "AAA", "AA", "A"):
        return last_up
    if last_up in ("A+", "APLUS", "A-ADVANCED", "HIGHA", "HIGH-A", "HIGH_A"):
        return "A+"
    if "ROOKIE" in last_up:
        return "Rookie"
    return last_up

# -----------------------
# Level weighting helper (new)
# -----------------------
def get_level_multiplier(level):
    """
    Lookup LEVEL_WEIGHTS in batter_weights with safe fallback.
    Returns float >= 0.0 (default 1.0).
    """
    try:
        lvl = _canonicalize_level(level) or "default"
        all_lvl = getattr(bw, "LEVEL_WEIGHTS", {}) or {}
        # Try exact/title/upper fallbacks
        if lvl in all_lvl:
            val = all_lvl[lvl]
        elif lvl.upper() in all_lvl:
            val = all_lvl[lvl.upper()]
        elif lvl.title() in all_lvl:
            val = all_lvl[lvl.title()]
        else:
            val = all_lvl.get("default", 1.0)
        return float(val)
    except Exception:
        return 1.0

# -----------------------
# apply age penalty
# -----------------------
def apply_age_penalty_to_df(df):
    if "Age" not in df.columns:
        return df
    df = df.copy()
    if "Level" not in df.columns:
        if "__source_file" in df.columns:
            df["Level"] = df["__source_file"].apply(_infer_level_from_source_file)
        else:
            df["Level"] = None
    df["_age_mult"] = df.apply(lambda r: compute_age_multiplier(r.get("Age", None), level=r.get("Level", None)), axis=1)
    if "PerformanceMetric" in df.columns:
        df["PerformanceMetric"] = pd.to_numeric(df["PerformanceMetric"], errors="coerce").fillna(0.0) * df["_age_mult"]
    if "UsageMetric" in df.columns:
        df["UsageMetric"] = pd.to_numeric(df["UsageMetric"], errors="coerce").fillna(0.0) * df["_age_mult"]
    return df

# -----------------------
# main flow
# -----------------------
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
            level_df = all_df.copy()
    else:
        level_df = all_df.copy()

    if level_df.empty:
        raise SystemExit(f"No players found for level='{args.level}'")

    if "PerformanceMetric" not in level_df.columns:
        raise SystemExit("PerformanceMetric not found in input CSVs. Run evaluator first.")
    if "UsageMetric" not in level_df.columns:
        raise SystemExit("UsageMetric not found in input CSVs. Run evaluator first.")

    # Apply aging penalty (level-aware)
    level_df = apply_age_penalty_to_df(level_df)

    # show counts per Level for diagnostics
    try:
        grp = level_df.groupby("Level", dropna=False).size().sort_values(ascending=False)
        print("Counts by Level after inference:")
        print(grp.to_string())
    except Exception:
        pass

    # Compute scaled PerformanceMetric and UsageMetric
    if args.per_level_scale:
        def scale_group(g):
            _, scaled_perf = compute_z_scaled(g["PerformanceMetric"])
            g["perf_scaled"] = scaled_perf.round(6)
            _, scaled_use = compute_z_scaled(g["UsageMetric"])
            g["use_scaled"] = scaled_use.round(6)
            return g
        level_df = level_df.groupby("Level", dropna=False, group_keys=False).apply(scale_group)
    else:
        _, perf_scaled = compute_z_scaled(level_df["PerformanceMetric"])
        level_df["perf_scaled"] = perf_scaled.round(6)
        _, use_scaled = compute_z_scaled(level_df["UsageMetric"])
        level_df["use_scaled"] = use_scaled.round(6)

    # Combined using perf_share
    perf_share = get_perf_share()
    level_df["combined_scaled"] = (perf_share * level_df["perf_scaled"] + (1.0 - perf_share) * level_df["use_scaled"]).round(6)

    # -----------------------
    # Apply level multiplier (new)
    # -----------------------
    # compute and attach multiplier per-row
    level_df["_level_mult"] = level_df["Level"].apply(get_level_multiplier)
    # apply to combined score and clamp to [0,100]
    level_df["combined_scaled"] = (level_df["combined_scaled"] * level_df["_level_mult"]).clip(0.0, 100.0).round(6)

    # optional: print some stats about multipliers used
    try:
        print("Level multipliers summary:")
        print(level_df.groupby("_level_mult").size().sort_values(ascending=False).to_string())
    except Exception:
        pass

    # Build the compact output
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

    level_tag = args.level.upper() if args.level else "ALL"
    master_out = os.path.join(args.output_dir, f"all_players_{level_tag}_formatted.csv")
    output_df.to_csv(master_out, index=False)
    print(f"Formatted aggregated file written: {master_out} (n={len(output_df)})")

if __name__ == "__main__":
    main()