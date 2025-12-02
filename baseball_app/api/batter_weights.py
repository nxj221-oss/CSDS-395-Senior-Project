# B,Age,PO,PA,AB,R,H,2B,3B,HR,RBI,BB,SO,SB,CS

performance_weighting_percent = 0.625  # Percentage weight for performance vs. usage

# Configuration and Weights
PERFORMANCE_WEIGHTS = {
    # Performance Metrics -- all weights are correlated with their plate appearances
    "R": 1.5,  # Runs
    "HR": 4.0,  # Home Runs
    "RBI": 1.2,  # Runs Batted In
    "SB": 3.0,  # Stolen Bases
    "AVG": 2.0,  # Batting Average
    "OBP": 1.5,  # On-Base Percentage
    "SLG": 2.5,  # Slugging Percentage
    "K": -3.0,  # Strikeouts (negative weight)
    "BB": 0.5,  # Walks
}

USAGE_WEIGHTS = {
    # Usage Metrics
    "defensive-position": 1.0, # 1.0,  # Defensive Position
    "handedness": 0.125, # 0.125,  # Handedness (left/right)
    "age-to-level": 2.5, #1.0,  # Age relative to league level
    "games-played": 0.5, #0.5, # Games Played
}

# Positional Adjustment Factors
POSITIONAL_WEIGHTS = {
    "C": 3.0,
    "1B": 0.5,
    "2B": 1.5,
    "3B": 1.0,
    "SS": 2.0,
    "LF": 1.0,
    "CF": 2.0,
    "RF": 0.75,
    "DH": 0.125,
}

# Handedness Adjustment Factors
HANDEDNESS_WEIGHTS = {
    "L": 1.0,  # Left-handed
    "R": 0.85,  # Right-handed
    "S": 1.25, # Switch-hitter
}

# Age-to-Level Adjustment Factors
AGE_TO_LEVEL_WEIGHTS = {
    "Rookie": {"age": 19, "deviation": 2.0, "younger_boost": 0.5, "older_penalty": 0.5},
    "A":      {"age": 21, "deviation": 2.5, "younger_boost": 0.5, "older_penalty": 0.5},
    "A+":     {"age": 22.5, "deviation": 2.5, "younger_boost": 0.5, "older_penalty": 0.5},
    "AA":     {"age": 24, "deviation": 3.0, "younger_boost": 0.5, "older_penalty": 0.5},
    "AAA":    {"age": 25.5, "deviation": 3.5, "younger_boost": 0.5, "older_penalty": 0.5},
    "MLB":    {"age": 29.5, "deviation": 3.75, "younger_boost": 0.25, "older_penalty": 0.50},
}

# Age Penalties
AGE_PENALTY = {
    "cutoff_age": 26.0, # 31.0
    "rate": 0.125, # 0.5
    "exponent": 0.25, # 1.25
    "min_multiplier": None,
}

# Level weighting: boost or damp players based on the level they play at.
LEVEL_WEIGHTS = {
    "default": 1.0,
    "MLB": 1.05,
    "AAA": 1.01,
    "AA": 1.00,
    "A+": 0.995,
    "A": 0.99,
    "Rookie": 0.98,
}