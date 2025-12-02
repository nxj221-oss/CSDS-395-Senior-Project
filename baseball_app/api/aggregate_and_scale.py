#!/usr/bin/env python3
"""
aggregate_and_scale.py

Reads per-team CSV files from --input-dir, applies level-aware age penalties
(using configs in batter_weights.AGE_PENALTY), applies age-to-level adjustments
(using AGE_TO_LEVEL_WEIGHTS), computes z-scaled performance and usage metrics,
applies a level multiplier from batter_weights.LEVEL_WEIGHTS, and writes a compact
aggregated CSV per requested level (or ALL if --level omitted).
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
# Level canonicalization + inference
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
# AB penalty helpers (level-aware)
# -----------------------
def _get_ab_penalty_config_for_level(level):
    """
    Look up level-specific AB penalty config from bw.AB_PENALTY.
    Returns a dict with keys:
      - min_ab: AB threshold where penalty stops (default 200.0)
      - exponent: exponent for scaling (default 1.0)
      - min_multiplier: floor for multiplier (default 0.0 / None -> no floor)
    """
    try:
        all_cfg = getattr(bw, "AB_PENALTY", {}) or {}
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
        "min_ab": float(cfg.get("min_ab", cfg.get("threshold", 200.0))),
        "exponent": float(cfg.get("exponent", 1.0)),
        "min_multiplier": cfg.get("min_multiplier", cfg.get("min_mult", None)),
    }

def compute_ab_multiplier(ab, level=None):
    """
    Compute an AB-based multiplier (0..1).
    - If AB is >= min_ab -> 1.0
    - If AB is missing or invalid -> 1.0 (no penalty)
    - Otherwise multiplier = (AB / min_ab) ** exponent, clamped and floored by min_multiplier.
    """
    try:
        ab_val = float(ab)
    except Exception:
        return 1.0

    cfg = _get_ab_penalty_config_for_level(level)
    min_ab = max(0.0, float(cfg.get("min_ab", 200.0)))
    exponent = float(cfg.get("exponent", 1.0))
    min_mult = cfg.get("min_multiplier", None)

    if min_ab <= 0:
        return 1.0

    if ab_val >= min_ab:
        return 1.0

    if ab_val <= 0:
        mult = 0.0
    else:
        try:
            ratio = ab_val / min_ab
            mult = ratio ** exponent
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

# -----------------------
# Age penalty helpers (level-aware)
# -----------------------
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

# -----------------------
# AGE_TO_LEVEL helpers (new)
# -----------------------
def _get_age_to_level_cfg(level):
    """
    Return the config dict from bw.AGE_TO_LEVEL_WEIGHTS for the canonical level.
    Fallback: None (no adjustment).
    """
    try:
        all_cfg = getattr(bw, "AGE_TO_LEVEL_WEIGHTS", {}) or {}
        lvl = _canonicalize_level(level)
        if not lvl:
            return None
        # try common forms
        if lvl in all_cfg:
            return all_cfg[lvl]
        if lvl.title() in all_cfg:
            return all_cfg[lvl.title()]
        if lvl.upper() in all_cfg:
            return all_cfg[lvl.upper()]
    except Exception:
        return None
    return None

def compute_age_to_level_multiplier(age, level):
    """
    Compute multiplier based on AGE_TO_LEVEL_WEIGHTS:
    - If player is significantly younger than expected -> boost up to younger_boost
    - If player is significantly older -> penalty up to older_penalty
    Linear ramp over one 'deviation' window; clamped.
    """
    try:
        age_val = float(age)
    except Exception:
        return 1.0

    cfg = _get_age_to_level_cfg(level)
    if not cfg:
        return 1.0

    expected = float(cfg.get("age", cfg.get("expected_age", cfg.get("expected", float("nan")))))
    deviation = float(cfg.get("deviation", 0.0))
    younger_boost = float(cfg.get("younger_boost", 0.0))
    older_penalty = float(cfg.get("older_penalty", 0.0))

    # defensive
    if math.isnan(expected) or deviation <= 0:
        return 1.0

    diff = age_val - expected
    # Player much younger than expected_age - deviation => boost
    if diff < -deviation:
        amount = (expected - deviation) - age_val  # positive
        normalized = min(1.0, amount / deviation)  # 0..1
        mult = 1.0 + younger_boost * normalized
        return max(0.0, float(mult))
    # Player much older than expected_age + deviation => penalty
    if diff > deviation:
        amount = age_val - (expected + deviation)
        normalized = min(1.0, amount / deviation)
        mult = 1.0 - older_penalty * normalized
        return max(0.0, float(mult))
    # within acceptable band
    return 1.0

# -----------------------
# Level weighting helper
# -----------------------
def get_level_multiplier(level):
    try:
        lvl = _canonicalize_level(level) or "default"
        all_lvl = getattr(bw, "LEVEL_WEIGHTS", {}) or {}
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
# apply age penalty + age-to-level adjustments
# -----------------------
def apply_age_penalty_to_df(df):
    """
    - infers Level if missing (from __source_file)
    - computes _age_mult (exponential penalty for older players)
    - computes _age_level_mult (based on AGE_TO_LEVEL_WEIGHTS boost/penalty for being young/old relative to level)
    - multiplies both together and applies to PerformanceMetric and UsageMetric
    """
    if "Age" not in df.columns:
        return df

    df = df.copy()

    if "Level" not in df.columns:
        if "__source_file" in df.columns:
            df["Level"] = df["__source_file"].apply(_infer_level_from_source_file)
        else:
            df["Level"] = None

        # compute both multipliers per-row
    def _compute_mults(row):
        age = row.get("Age", None)
        level = row.get("Level", None)
        age_mult = compute_age_multiplier(age, level)
        age_level_mult = compute_age_to_level_multiplier(age, level)

        # AB penalty
        ab = row.get("AB", None)
        ab_mult = compute_ab_multiplier(ab, level)

        total = float(age_mult) * float(age_level_mult) * float(ab_mult)
        # clamp (0..1)
        total = max(0.0, min(1.0, total))
        return pd.Series({
            "_age_mult": age_mult,
            "_age_level_mult": age_level_mult,
            "_ab_mult": ab_mult,
            "_total_age_mult": total
        })

    mults = df.apply(_compute_mults, axis=1)
    df = pd.concat([df, mults], axis=1)

    # apply total multiplier to metrics
    if "PerformanceMetric" in df.columns:
        df["PerformanceMetric"] = pd.to_numeric(df["PerformanceMetric"], errors="coerce").fillna(0.0) * df["_total_age_mult"]
    if "UsageMetric" in df.columns:
        df["UsageMetric"] = pd.to_numeric(df["UsageMetric"], errors="coerce").fillna(0.0) * df["_total_age_mult"]

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

    # Ensure required metric columns exist
    if "PerformanceMetric" not in level_df.columns:
        raise SystemExit("PerformanceMetric not found in input CSVs. Run evaluator first.")
    if "UsageMetric" not in level_df.columns:
        raise SystemExit("UsageMetric not found in input CSVs. Run evaluator first.")

    # Apply aging penalty + age-to-level adjustment (level-aware)
    level_df = apply_age_penalty_to_df(level_df)

    # Diagnostic: counts by level
    try:
        grp = level_df.groupby("Level", dropna=False).size().sort_values(ascending=False)
        print("Counts by Level after inference:")
        print(grp.to_string())
    except Exception:
        pass

    # -------------------------
    # Compute scaled PerformanceMetric and UsageMetric
    # Option: per-level scaling if requested (--per-level-scale)
    # -------------------------
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

    # Apply level multiplier (existing)
    level_df["_level_mult"] = level_df["Level"].apply(get_level_multiplier)
    level_df["combined_scaled"] = (level_df["combined_scaled"] * level_df["_level_mult"]).clip(0.0, 100.0).round(6)

    # Remove duplicate players by taking the highest number of AB's
    def dedupe_highest_ab(df):
        if "Player" not in df.columns:
            return df
        df["_player_key"] = df["Player"].astype(str).str.strip().str.casefold()
        # ensure numeric AB
        df["_AB_numeric"] = pd.to_numeric(df.get("AB", 0), errors="coerce").fillna(0)
        idx = df.groupby("_player_key")["_AB_numeric"].idxmax().dropna().astype(int)
        deduped = df.loc[idx].copy()
        deduped = deduped.drop(columns=["_player_key", "_AB_numeric"])
        return deduped

    level_df = dedupe_highest_ab(level_df)

    # optional: summarize multipliers used
    try:
        print("Age multipliers summary (age_penalty, age_to_level, total):")
        print(level_df[["_age_mult", "_age_level_mult", "_total_age_mult"]].describe().to_string())
        print("Level multipliers summary (by _level_mult):")
        print(level_df.groupby("_level_mult").size().to_string())
    except Exception:
        pass

    # Build compact output (keeps team.csv source)
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