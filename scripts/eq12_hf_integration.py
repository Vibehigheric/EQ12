#!/usr/bin/env python3
"""
EQ12 Hugging Face Betting Model Integration
Connect HF betting models with EQ12 parlay system
"""


from eq12_hf_betting_model import eq12_betting_model


class EQ12BettingIntegration:
    """Integration layer for HF betting models with EQ12 parlays"""

    def __init__(self):
        self.model = eq12_betting_model
        self.last_predictions = {}

    def analyze_tonights_games(self) -> Dict:
        """Analyze tonight's NHL games with HF models"""

        # Tonight's games (October 9, 2025)
        games = [
            {
                "matchup": "COL@VGK",
                "home_team": "Vegas",
                "away_team": "Colorado",
                "game_data": {
                    "home_goals_per_game": 3.2,
                    "away_goals_per_game": 3.8,
                    "home_goalie_save_pct": 0.912,
                    "away_goalie_save_pct": 0.925,
                    "away_back_to_back": 1,  # Colorado on B2B
                },
            },
            {
                "matchup": "BOS@TOR",
                "home_team": "Toronto",
                "away_team": "Boston",
                "game_data": {
                    "home_goals_per_game": 3.5,
                    "away_goals_per_game": 3.1,
                    "home_goalie_save_pct": 0.908,
                    "away_goalie_save_pct": 0.918,
                },
            },
            {
                "matchup": "CGY@EDM",
                "home_team": "Edmonton",
                "away_team": "Calgary",
                "game_data": {
                    "home_goals_per_game": 3.7,
                    "away_goals_per_game": 2.9,
                    "star_player_points": 2.2,  # McDavid factor
                },
            },
        ]

        predictions = {}

        for game in games:
            game_pred = self.model.predict_nhl_game(game["game_data"])
            game_pred["matchup"] = game["matchup"]
            game_pred["recommended_parlays"] = self.model.generate_parlays(game_pred)
            predictions[game["matchup"]] = game_pred

        return predictions

    def get_hf_enhanced_picks(self) -> List[Dict]:
        """Get HF model enhanced picks for tonight"""

        predictions = self.analyze_tonights_games()

        enhanced_picks = []

        for matchup, pred in predictions.items():
            if pred["confidence"]["overall"] > 0.75:
                enhanced_picks.append(
                    {
                        "game": matchup,
                        "pick_type": "HF Model High Confidence",
                        "selection": f"Home ML + {pred['over_under_6_5']} 6.5",
                        "probability": pred["confidence"]["overall"],
                        "model_source": "Reverse-engineered HF patterns",
                        "reasoning": f"Model confidence {pred['confidence']['overall']:.1%}",
                    }
                )

        return enhanced_picks


# Global integration instance
eq12_hf_integration = EQ12BettingIntegration()
