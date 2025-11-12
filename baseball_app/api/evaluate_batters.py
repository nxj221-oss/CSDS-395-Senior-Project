#!/usr/bin/env python3
import sys
import math
import pandas as pd
# import numpy as np

# Import the weighting configuration
import batter_weights as bw

# -----------------------
# Helper functions
# -----------------------
def safe_div(n, d):
    try:
        return n / d if d else 0
    except Exception:
        return 0

def compute_rate_stats(df):
    """Compute AVG, OBP, and SLG to match the metrics expected by batter_weights."""
    df = df.copy()
    for c in ["PA","AB","R","H","2B","3B","HR","RBI","BB","SO","SB","CS"]:
        df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)

    df["1B"] = df["H"] - df["2B"] - df["3B"] - df["HR"]
    df["TB"] = df["1B"] + 2*df["2B"] + 3*df["3B"] + 4*df["HR"]
    df["AVG"] = df.apply(lambda x: safe_div(x["H"], x["AB"]), axis=1)
    df["OBP"] = df.apply(lambda x: safe_div(x["H"] + x["BB"], x["PA"]), axis=1)
    df["SLG"] = df.apply(lambda x: safe_div(x["TB"], x["AB"]), axis=1)
    return df

def positional_factor(pos):
    """Get positional adjustment factor."""
    pos = str(pos).strip().upper()
    return bw.POSITIONAL_WEIGHTS.get(pos, bw.USAGE_WEIGHTS["defensive-position"])

def handedness_factor(bats):
    """Get handedness adjustment factor."""
    bats = str(bats).strip().upper()
    return bw.HANDEDNESS_WEIGHTS.get(bats, bw.USAGE_WEIGHTS["handedness"])

def age_to_level_factor(age, level):
    """Score based on proximity to target age for level."""
    try:
        age = float(age)
    except Exception:
        return 1.0
    level_data = bw.AGE_TO_LEVEL_WEIGHTS.get(str(level).strip(), None)
    if not level_data:
        return 1.0
    target_age = level_data["age"]
    dev = level_data["deviation"]
    # Gaussian-like curve centered at target_age
    score = math.exp(-((age - target_age)**2) / (2 * dev**2))
    return score

def zscore(series):
    """Normalize by z-score."""
    m, s = series.mean(), series.std()
    if s == 0 or pd.isna(s):
        return pd.Series(0, index=series.index)
    return (series - m) / s

def rescale(series):
    """Rescale to 0-100."""
    mn, mx = series.min(), series.max()
    if mn == mx:
        return pd.Series(50, index=series.index)
    return (series - mn) / (mx - mn) * 100

# -----------------------
# Metric computation
# -----------------------
def compute_performance(df):
    perf = pd.Series(0, index=df.index, dtype=float)

    # Calculate per-stat contributions
    for stat, weight in bw.PERFORMANCE_WEIGHTS.items():
        col = stat
        if stat == "K":  # K maps to SO column
            col = "SO"
        if col not in df.columns:
            continue
        perf += zscore(df[col].astype(float)) * weight

    # Scale to 0–100
    return rescale(perf)

def compute_usage(df):
    """Compute usage metric based on USAGE_WEIGHTS config."""
    usage = pd.Series(0, index=df.index, dtype=float)

    # Defensive position weight
    if bw.USAGE_WEIGHTS.get("defensive-position", 0) != 0:
        pos_vals = df["PO"].apply(positional_factor)
        usage += zscore(pos_vals) * bw.USAGE_WEIGHTS["defensive-position"]

    # Handedness weight
    if "B" in df.columns and bw.USAGE_WEIGHTS.get("handedness", 0) != 0:
        hand_vals = df["B"].apply(handedness_factor)
        usage += zscore(hand_vals) * bw.USAGE_WEIGHTS["handedness"]

    # Age-to-level weight
    if "Age" in df.columns and "Level" in df.columns and bw.USAGE_WEIGHTS.get("age-to-level", 0) != 0:
        age_vals = df.apply(lambda x: age_to_level_factor(x["Age"], x["Level"]), axis=1)
        usage += zscore(age_vals) * bw.USAGE_WEIGHTS["age-to-level"]

    # Games played (proxied by PA)
    if "PA" in df.columns and bw.USAGE_WEIGHTS.get("games-played", 0) != 0:
        usage += zscore(df["PA"].astype(float)) * bw.USAGE_WEIGHTS["games-played"]

    return rescale(usage)

# -----------------------
# Main
# -----------------------
def evaluate_players(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    df = compute_rate_stats(df)

    df["PerformanceMetric"] = compute_performance(df)
    df["UsageMetric"] = compute_usage(df)
    df["CombinedMetric"] = (bw.performance_weighting_percent * df["PerformanceMetric"] +
                            (1.0-bw.performance_weighting_percent) * df["UsageMetric"]).round(2)

    df.to_csv(output_csv, index=False)
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