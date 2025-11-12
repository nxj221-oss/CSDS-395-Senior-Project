# B,Age,PO,PA,AB,R,H,2B,3B,HR,RBI,BB,SO,SB,CS

performance_weighting_percent = 0.5  # Percentage weight for performance vs. usage

# Configuration and Weights
PERFORMANCE_WEIGHTS = {
    # Performance Metrics -- all weights are correlated with their plate appearances
    "R": 1.0,  # Runs
    "HR": 1.4,  # Home Runs
    "RBI": 1.2,  # Runs Batted In
    "SB": 1.5,  # Stolen Bases
    "AVG": 3.0,  # Batting Average
    "OBP": 4.0,  # On-Base Percentage
    "SLG": 3.5,  # Slugging Percentage
    "K": -2.0,  # Strikeouts (negative weight)
    "BB": 1.0,  # Walks
}

USAGE_WEIGHTS = {
    # Usage Metrics
    "defensive-position": 1.0,  # Defensive Position
    "handedness": 0.125,  # Handedness (left/right)
    "age-to-level": 1.0,  # Age relative to league level
    "games-played": 1.0, # Games Played
}

# Positional Adjustment Factors
POSITIONAL_WEIGHTS = {
    "C": 2.0,
    "1B": 0.75,
    "2B": 1.25,
    "3B": 1.0,
    "SS": 1.5,
    "LF": 1.0,
    "CF": 1.5,
    "RF": 1.0,
    "DH": 0.5,
}

# Handedness Adjustment Factors
HANDEDNESS_WEIGHTS = {
    "L": 1.0,  # Left-handed
    "R": 0.85,  # Right-handed
    "S": 1.25, # Switch-hitter
}

# Age-to-Level Adjustment Factors
AGE_TO_LEVEL_WEIGHTS = {
    "Rookie": {"age": 19, "deviation": 2.0},
    "A": {"age": 21, "deviation": 2.5},
    "A+": {"age": 22.5, "deviation": 2.5},
    "AA": {"age": 24, "deviation": 3},
    "AAA": {"age": 27, "deviation": 3.5},
    "MLB": {"age": 29.5, "deviation": 3.75},
}