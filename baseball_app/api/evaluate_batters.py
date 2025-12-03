#!/usr/bin/env python3
import sys
import math
import pandas as pd
import numpy as np

# Import your config file
import batter_weights as bw

# -------- helpers --------
# Safely convert a value to float, returning a default if invalid
def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

# Safe division: return 0 if denominator is zero
def safe_div(n, d):
    if d:
        return n / d
    return 0.0

# Compute rate-based offensive statistics (AVG, OBP, SLG)
def compute_rate_stats(df):
    """Compute AVG, OBP, SLG, and helpful counts. Keep numeric types."""
    df = df.copy()
    # Convert key counting stats to numeric (non-numeric -> 0)
    for c in ["PA", "AB", "R", "H", "2B", "3B", "HR", "RBI", "BB", "SO", "SB", "CS"]:
        df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0.0)
        
    # Compute derived stats
    df["1B"] = df["H"] - df["2B"] - df["3B"] - df["HR"]
    df["TB"] = df["1B"] + 2 * df["2B"] + 3 * df["3B"] + 4 * df["HR"]

    # AVG = H / AB
    df["AVG"] = df.apply(lambda r: safe_div(r["H"], r["AB"]), axis=1)
    # OBP approx = (H + BB) / PA   (no sacrifice fly data available)
    df["OBP"] = df.apply(lambda r: safe_div((r["H"] + r["BB"]), r["PA"]), axis=1)

    # SLG = TB / AB
    df["SLG"] = df.apply(lambda r: safe_div(r["TB"], r["AB"]), axis=1)
    return df

# Lookup positional weight from config
def positional_factor(pos):
    pos = str(pos).strip().upper()
    return bw.POSITIONAL_WEIGHTS.get(pos, bw.POSITIONAL_WEIGHTS.get("DEFAULT", 1.0))

# Lookup handedness weight from config
def handedness_factor(bats):
    bats = str(bats).strip().upper()
    return bw.HANDEDNESS_WEIGHTS.get(bats, bw.HANDEDNESS_WEIGHTS.get("DEFAULT", 1.0))

# Age-to-level scoring with asymmetric penalties + exponential tail
def age_to_level_score(age, level):
    """
    Aggressive tail penalty WITHOUT a floor:
      - For age <= cutoff (target + cutoff_offset): use a smooth asymmetric curve.
      - For age > cutoff: apply an exponential decay tail (no floor).
      - Params available per-level via AGE_TO_LEVEL_WEIGHTS:
        "age", "deviation", "younger_boost", "older_penalty",
        "cutoff_offset", "tail_alpha", "tail_beta"
    """
    # Try to interpret age as float
    try:
        age = float(age)
    except Exception:
        return 1.0

    # Get level-specific parameters
    level = str(level).strip()
    level_data = bw.AGE_TO_LEVEL_WEIGHTS.get(level)
    if not level_data:
        return 1.0
        
    # Extract parameters with defaults
    target = float(level_data.get("age", age))
    dev = float(level_data.get("deviation", 3.0))
    younger_boost = float(level_data.get("younger_boost", 0.25))
    older_penalty = float(level_data.get("older_penalty", 0.20))
    cutoff_offset = float(level_data.get("cutoff_offset", 3.0))
    tail_alpha = float(level_data.get("tail_alpha", 0.4))
    tail_beta = float(level_data.get("tail_beta", 1.5))

    # Compute cutoff: after this age, use the exponential tail
    cutoff = target + cutoff_offset

    # If player is within normal age range, use smooth curve
    if age <= cutoff:
        asym = (target - age) / dev
        proximity = math.exp(-((age - target) ** 2) / (2 * (dev ** 2)))
        signed = math.tanh(asym)
        
        # Younger → positive signed; older → negative
        if signed > 0:
            return 1.0 + signed * younger_boost * proximity
        else:
            return 1.0 + signed * older_penalty * proximity

    # Player is older than cutoff → apply exponential decay    years_past = age - cutoff
    tail_val = math.exp(-tail_alpha * (years_past ** tail_beta))
    return tail_val

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
                perf += df[col].astype(float)perf += pd.to_numeric(df[col], errors="coerce").fillna(0.0) * float(weight)* float(weight)
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

    # Defensive position component
    if u.get("defensive-position", 0):
        pos_vals = df["PO"].apply(positional_factor) if "PO" in df.columns else pd.Series(1.0, index=df.index)
        usage += pos_vals.astype(float) * float(u.get("defensive-position", 0.0))

    # Handedness component (B = batting side)
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

# Normalize name column: accept Player or Name, store as Player
def normalize_player_name(df):
    if "Player" in df.columns:
        df["Player"] = df["Player"].astype(str)
    elif "Name" in df.columns:
        df["Player"] = df["Name"].astype(str)
    else:
        raise ValueError("Neither 'Player' nor 'Name' column found in input file.")

    # Optional cleanup: strip whitespace
    df["Player"] = df["Player"].str.strip()
    return df

# -------- main flow --------
def evaluate_players(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    
    # Normalize identity + compute basic rate stats
    df = normalize_player_name(df)
    df = compute_rate_stats(df)

    # compute raw metrics
    df["PerformanceMetric"] = compute_performance_raw(df)
    df["UsageMetric"] = compute_usage_raw(df)

    # Weighted blend of performance + usage
    df["CombinedMetric"] = (
        bw.performance_weighting_percent * df["PerformanceMetric"]
        + (1.0 - bw.performance_weighting_percent) * df["UsageMetric"]
    )

    # Round metrics moderately for CSV cleanliness (you can remove rounding if you want full precision)
    df[["PerformanceMetric", "UsageMetric", "CombinedMetric"]] = \
    df[["PerformanceMetric", "UsageMetric", "CombinedMetric"]].round(6)

    # Build the requested output columns in order; create missing ones as NaN
    out_cols = ["Player", "B", "Age", "PO", "AB", "PerformanceMetric", "UsageMetric", "CombinedMetric"]
    out_df = pd.DataFrame(index=df.index)
    for c in out_cols:
        out_df[c] = df[c] if c in df.columns else np.nan

    out_df.to_csv(output_csv, index=False)
    #print(f"✅ Evaluation complete — saved to {output_csv}")

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
