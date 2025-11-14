#!/usr/bin/env python3
import sys
import math
import pandas as pd
import numpy as np

# Import your config file
import batter_weights as bw

# -------- helpers --------
def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def safe_div(n, d):
    if d:
        return n / d
    return 0.0

def compute_rate_stats(df):
    """Compute AVG, OBP, SLG, and helpful counts. Keep numeric types."""
    df = df.copy()
    for c in ["PA", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "SB", "CS"]:
        df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0.0)

    df["1B"] = df["H"] - df["2B"] - df["3B"] - df["HR"]
    df["TB"] = df["1B"] + 2 * df["2B"] + 3 * df["3B"] + 4 * df["HR"]
    df["AVG"] = df.apply(lambda r: safe_div(r["H"], r["AB"]), axis=1)
    # OBP approx: (H + BB) / PA (sac flies not available)
    df["OBP"] = df.apply(lambda r: safe_div((r["H"] + r["BB"]), r["PA"]), axis=1)
    df["SLG"] = df.apply(lambda r: safe_div(r["TB"], r["AB"]), axis=1)
    return df

def positional_factor(pos):
    pos = str(pos).strip().upper()
    return bw.POSITIONAL_WEIGHTS.get(pos, bw.POSITIONAL_WEIGHTS.get("DEFAULT", 1.0))

def handedness_factor(bats):
    bats = str(bats).strip().upper()
    return bw.HANDEDNESS_WEIGHTS.get(bats, bw.HANDEDNESS_WEIGHTS.get("DEFAULT", 1.0))

def age_to_level_score(age, level):
    """Gaussian-like score in [0,1] based on distance from target age for the level."""
    try:
        age = float(age)
    except Exception:
        return 1.0
    level = str(level).strip()
    level_data = bw.AGE_TO_LEVEL_WEIGHTS.get(level)
    if not level_data:
        return 1.0
    target = float(level_data.get("age", age))
    dev = float(level_data.get("deviation", 3.0))
    # exp(- (age - target)^2 / (2*sigma^2)) gives 0..1
    return math.exp(-((age - target) ** 2) / (2 * (dev ** 2)))

# -------- metrics (NO RESCALING) --------
def compute_performance_raw(df):
    """
    Compute a raw performance metric (not scaled).
    Rate stats (AVG/OBP/SLG) use direct values.
    Counting stats use per-PA to control for opportunity.
    """
    perf = pd.Series(0.0, index=df.index, dtype=float)

    # iterate configured performance weights
    for stat, weight in bw.PERFORMANCE_WEIGHTS.items():
        if stat == "K":  # mapping
            col = "SO"
        else:
            col = stat

        # If it's a rate stat (AVG, OBP, SLG) we take it directly
        if col in ("AVG", "OBP", "SLG"):
            if col in df.columns:
                perf += df[col].astype(float) * float(weight)
        else:
            # For counting stats, convert to per-PA rate to avoid opportunity bias
            if col in df.columns:
                per_pa = df.apply(lambda r: safe_div(r.get(col, 0.0), r.get("PA", 0.0)), axis=1)
                perf += per_pa * float(weight)

    return perf

def compute_usage_raw(df):
    """
    Compute raw usage score as a deterministic weighted sum:
    pos_factor * USAGE_WEIGHTS['defensive-position']
    + handedness_factor * USAGE_WEIGHTS['handedness']
    + age_score * USAGE_WEIGHTS['age-to-level']
    + PA * USAGE_WEIGHTS['games-played']   (PA is absolute)
    """
    usage = pd.Series(0.0, index=df.index, dtype=float)

    u = bw.USAGE_WEIGHTS

    # defensive-position
    if u.get("defensive-position", 0):
        pos_vals = df["PO"].apply(positional_factor) if "PO" in df.columns else pd.Series(1.0, index=df.index)
        usage += pos_vals.astype(float) * float(u.get("defensive-position", 0.0))

    # handedness
    if u.get("handedness", 0) and "B" in df.columns:
        hand_vals = df["B"].apply(handedness_factor)
        usage += hand_vals.astype(float) * float(u.get("handedness", 0.0))

    # age-to-level
    if u.get("age-to-level", 0) and "Age" in df.columns and "Level" in df.columns:
        age_vals = df.apply(lambda r: age_to_level_score(r.get("Age", np.nan), r.get("Level", "")), axis=1)
        usage += age_vals.astype(float) * float(u.get("age-to-level", 0.0))

    # games-played (absolute usage) - PA is used as proxy
    if u.get("games-played", 0) and "PA" in df.columns:
        usage += df["PA"].astype(float) * float(u.get("games-played", 0.0))

    return usage

# -------- main flow --------
def evaluate_players(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df = compute_rate_stats(df)

    # compute raw metrics
    df["PerformanceMetric"] = compute_performance_raw(df)
    df["UsageMetric"] = compute_usage_raw(df)

    # combined: use configurable performance_share if present
    perf_share = 0.7
    if hasattr(bw, "WEIGHTS") and isinstance(bw.WEIGHTS, dict) and "performance_share" in bw.WEIGHTS:
        try:
            perf_share = float(bw.WEIGHTS["performance_share"])
        except Exception:
            pass

    df["CombinedMetric"] = (perf_share * df["PerformanceMetric"] + (1.0 - perf_share) * df["UsageMetric"])

    # Round metrics moderately for CSV cleanliness (you can remove rounding if you want full precision)
    df["PerformanceMetric"] = df["PerformanceMetric"].round(6)
    df["UsageMetric"] = df["UsageMetric"].round(6)
    df["CombinedMetric"] = df["CombinedMetric"].round(6)

    # Build the requested output columns in order; create missing ones as NaN
    out_cols = ["Player", "B", "Age", "PO", "AB", "PerformanceMetric", "UsageMetric", "CombinedMetric"]
    out_df = pd.DataFrame(index=df.index)
    for c in out_cols:
        out_df[c] = df[c] if c in df.columns else np.nan

    out_df.to_csv(output_csv, index=False)
    print(f"✅ Evaluation complete — saved to {output_csv}")

# -----------------------
# CLI entrypoint
# -----------------------
if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv = ["evaluate_batters.py", "cardinals_batters.csv", "evaluated_cardinals_batters.csv"]
    elif len(sys.argv) != 3:
        print("Usage: python evaluate_batters.py input.csv output.csv")
        sys.exit(1)
    evaluate_players(sys.argv[1], sys.argv[2])