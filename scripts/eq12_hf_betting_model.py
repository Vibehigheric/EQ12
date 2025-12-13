#!/usr/bin/env python3
"""
EQ12 Betting Model Framework
Based on reverse-engineered Hugging Face betting models
"""


import numpy as np

try:
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.neural_network import MLPRegressor

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


class EQ12BettingModel:
    """EQ12 NHL Betting Prediction Model"""

    def __init__(self, model_type: str = "ensemble"):
        self.model_type = model_type
        self.models = {}
        self.feature_importance = {}
        self.last_updated = None

        if ML_AVAILABLE:
            self._initialize_models()

    def _initialize_models(self):
        """Initialize ML models based on HF patterns"""

        # Ensemble approach like Multichem models
        self.models = {
            "moneyline": GradientBoostingRegressor(n_estimators=100, random_state=42),
            "puck_line": RandomForestRegressor(n_estimators=100, random_state=42),
            "total_goals": MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42),
            "player_props": GradientBoostingRegressor(n_estimators=100, random_state=42),
        }

    def prepare_nhl_features(self, game_data: dict) -> np.ndarray:
        """Prepare NHL game features like HF models"""

        features = []

        # Team statistics (based on reverse engineering)
        team_stats = [
            game_data.get("home_goals_per_game", 3.0),
            game_data.get("away_goals_per_game", 2.8),
            game_data.get("home_goals_against", 2.5),
            game_data.get("away_goals_against", 3.1),
            game_data.get("home_pp_percent", 0.20),
            game_data.get("away_pp_percent", 0.18),
            game_data.get("home_pk_percent", 0.82),
            game_data.get("away_pk_percent", 0.80),
        ]
        features.extend(team_stats)

        # Goalie statistics
        goalie_stats = [
            game_data.get("home_goalie_save_pct", 0.915),
            game_data.get("away_goalie_save_pct", 0.908),
            game_data.get("home_goalie_gaa", 2.75),
            game_data.get("away_goalie_gaa", 3.10),
        ]
        features.extend(goalie_stats)

        # Recent form (last 10 games)
        recent_form = [
            game_data.get("home_last10_wins", 6),
            game_data.get("away_last10_wins", 4),
            game_data.get("home_last5_goals", 15),
            game_data.get("away_last5_goals", 12),
        ]
        features.extend(recent_form)

        # Schedule factors
        schedule_factors = [
            game_data.get("home_rest_days", 1),
            game_data.get("away_rest_days", 0),
            game_data.get("home_back_to_back", 0),  # 1 if B2B
            game_data.get("away_back_to_back", 1),
        ]
        features.extend(schedule_factors)

        return np.array(features).reshape(1, -1)

    def predict_nhl_game(self, game_data: dict) -> dict:
        """Predict NHL game outcomes like HF models"""

        if not ML_AVAILABLE:
            return self._mock_predictions(game_data)

        features = self.prepare_nhl_features(game_data)

        predictions = {}

        # Moneyline prediction (home win probability)
        if "moneyline" in self.models:
            home_win_prob = max(
                0.1, min(
                    0.9, self.models["moneyline"].predict(features)[0]))
            predictions["home_win_probability"] = home_win_prob
            predictions["away_win_probability"] = 1 - home_win_prob

        # Puck line prediction (spread)
        if "puck_line" in self.models:
            puck_line_value = self.models["puck_line"].predict(features)[0]
            predictions["puck_line_prediction"] = round(puck_line_value, 1)

        # Total goals prediction
        if "total_goals" in self.models:
            total_goals = max(
                4.5, min(
                    8.5, self.models["total_goals"].predict(features)[0]))
            predictions["total_goals_prediction"] = round(total_goals, 1)
            predictions["over_under_6_5"] = "OVER" if total_goals > 6.5 else "UNDER"

        # Player props (simplified)
        if "player_props" in self.models:
            mcdavid_points = max(
                0.5, min(
                    3.0, self.models["player_props"].predict(features)[0]))
            predictions["star_player_points"] = round(mcdavid_points, 1)

        # Add confidence scores (simulate HF model confidence)
        predictions["confidence"] = {
            "moneyline": min(0.95, max(0.60, abs(home_win_prob - 0.5) * 2)),
            "total_goals": 0.75,
            "overall": 0.80,
        }

        return predictions

    def _mock_predictions(self, game_data: dict) -> dict:
        """Mock predictions when ML not available"""

        # Simulate realistic NHL predictions
        home_advantage = 0.55  # Slight home ice advantage

        return {
            "home_win_probability": home_advantage,
            "away_win_probability": 1 - home_advantage,
            "puck_line_prediction": -1.5,
            "total_goals_prediction": 6.2,
            "over_under_6_5": "UNDER",
            "star_player_points": 1.8,
            "confidence": {"moneyline": 0.72, "total_goals": 0.68, "overall": 0.70},
        }

    def generate_parlays(self, predictions: dict) -> list[dict]:
        """Generate parlays based on model predictions (HF pattern)"""

        parlays = []

        # High confidence moneyline + total parlay
        if predictions["confidence"]["moneyline"] > 0.70:
            parlays.append(
                {
                    "type": "Safe SGP",
                    "legs": [
                        f"Home Team ML ({predictions['home_win_probability']:.1%})",
                        f"Total {predictions['over_under_6_5']} 6.5",
                    ],
                    "confidence": predictions["confidence"]["overall"],
                    "expected_odds": "+200",
                    "recommendation": (
                        "PLAY" if predictions["confidence"]["overall"] > 0.75 else "PASS"
                    ),
                }
            )

        # Star player + team result correlation
        if predictions.get("star_player_points", 0) > 1.5:
            parlays.append(
                {
                    "type": "Player Correlation",
                    "legs": [
                        f"McDavid {predictions['star_player_points']:.1f}+ Points",
                        "Edmonton ML",
                    ],
                    "confidence": 0.65,
                    "expected_odds": "+350",
                    "recommendation": "MODERATE PLAY",
                }
            )

        return parlays


# Global model instance for EQ12 system
eq12_betting_model = EQ12BettingModel()
