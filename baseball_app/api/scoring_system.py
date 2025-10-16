from typing import Dict, List
import numpy as np

class PlayerEvaluator:
    def __init__(self, stat_weights: Dict[str, float], level_ages: Dict[str, float], usage_weight: float = 1.0):
        """
        stat_weights: {stat_name: weight} for performance metrics
        level_ages: {level_name: avg_age} for age-to-level adjustment
        usage_weight: multiplier for normalized usage score
        """
        self.stat_weights = stat_weights
        self.level_ages = level_ages
        self.usage_weight = usage_weight

    def normalize_stats(self, players: List[Dict[str, float]]) -> List[Dict[str, float]]:
        stats = self.stat_weights.keys()
        means = {s: np.mean([p[s] for p in players if s in p]) for s in stats}
        stds = {s: np.std([p[s] for p in players if s in p]) for s in stats}

        for p in players:
            for s in stats:
                if stds[s] > 0:
                    p[f"z_{s}"] = (p[s] - means[s]) / stds[s]
                else:
                    p[f"z_{s}"] = 0.0
        return players

    def compute_usage_zscores(self, players: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """
        Compute z-scores for age-to-level deltas.
        """
        deltas = []
        for p in players:
            age = p.get("age")
            level = p.get("level")
            avg_age = self.level_ages.get(level)
            if age is not None and avg_age is not None:
                p["age_delta"] = avg_age - age
                deltas.append(p["age_delta"])
            else:
                p["age_delta"] = 0.0  # default if missing

        mean_delta = np.mean(deltas) if deltas else 0.0
        std_delta = np.std(deltas) if deltas else 1.0

        for p in players:
            if std_delta > 0:
                p["z_usage"] = (p["age_delta"] - mean_delta) / std_delta
            else:
                p["z_usage"] = 0.0
        return players

    def performance_score(self, player: Dict[str, float]) -> float:
        score = 0.0
        for stat, weight in self.stat_weights.items():
            score += weight * player.get(f"z_{stat}", 0.0)
        return score

    def usage_score(self, player: Dict[str, float]) -> float:
        return self.usage_weight * player.get("z_usage", 0.0)

    def evaluate_player(self, player: Dict[str, float]) -> float:
        return self.performance_score(player) + self.usage_score(player)

    def evaluate_all(self, players: List[Dict[str, float]]) -> List[Dict[str, float]]:
        players = self.normalize_stats(players)
        players = self.compute_usage_zscores(players)
        for p in players:
            p["perf_score"] = self.performance_score(p)
            p["usage_score"] = self.usage_score(p)
            p["score"] = p["perf_score"] + p["usage_score"]
        return players

# TODO: Replace this with the data from the web scraping
ps = [
    {"name": "Player A", "OBP": 0.350, "SLG": 0.500, "K%": 0.20, "BB%": 0.10, "age": 20, "level": "AA"},
    {"name": "Player B", "OBP": 0.320, "SLG": 0.400, "K%": 0.25, "BB%": 0.08, "age": 24, "level": "AA"},
    {"name": "Player C", "OBP": 0.323, "SLG": 0.367, "K%": 0.23, "BB%": 0.15, "age": 19, "level": "A"},
    {"name": "Player D", "OBP": 0.294, "SLG": 0.333, "K%": 0.16, "BB%": 0.12, "age": 25, "level": "AAA"},
    {"name": "Player E", "OBP": 0.368, "SLG": 0.425, "K%": 0.094, "BB%": 0.098, "age": 24, "level": "AAA"},
    {"name": "Player F", "OBP": 0.288, "SLG": 0.486, "K%": 0.318, "BB%": 0.026, "age": 20, "level": "A"},
]

weights = {"OBP": 0.3, "SLG": 0.3, "K%": -0.2, "BB%": 0.2}
avg_ages = {"A": 21.0, "AA": 23.0, "AAA": 25.0}

# Evaluate the players
evaluator = PlayerEvaluator(weights, avg_ages, usage_weight=0.5)
scored_players = evaluator.evaluate_all(ps)

# TODO: Replace printing out the results with what we will display the data with
print("{:<10} {:<5} {:<6} {:<12} {:<6} {:<8}".format("Name", "Age", "Level", "performance", "usage", "overall"))
for p in scored_players:    
    print("{:<10} {:<5} {:<6} {:<12} {:<6} {:<8}".format(p['name'], p['age'], p['level'], round(p['perf_score'], 2), round(p['usage_score'], 2), round(p['score'], 2)))
