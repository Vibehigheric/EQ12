#!/usr/bin/env python3
"""
EQ12 Sports Betting Automation System
Professional-grade sports betting with risk management
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import requests


class EQ12SportsBetting:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.db_path = self.base_dir / "logs" / "sports_betting.db"
        self.config_path = self.base_dir / "configs" / "sports_betting_config.json"
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_path) as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print("Configuration file not found. Using defaults.")
            self.config = {"api_settings": {}, "risk_management": {}}

    def fetch_odds(self, sport="americanfootball_nfl"):
        """Fetch current odds from The Odds API"""
        api_key = os.getenv("ODDS_API_KEY")
        if not api_key:
            print("ODDS_API_KEY not set. Using demo mode.")
            return self.demo_odds()

        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
            params = {
                "apiKey": api_key,
                "regions": "us",
                "markets": "h2h,spreads,totals",
                "oddsFormat": "decimal",
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            print(f"Error fetching odds: {e}")
            return []

    def demo_odds(self):
        """Demo odds data for testing"""
        return [
            {
                "id": "demo_game_1",
                "home_team": "Team A",
                "away_team": "Team B",
                "commence_time": datetime.now().isoformat(),
                "bookmakers": [
                    {
                        "key": "fanduel",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Team A", "price": 1.95},
                                    {"name": "Team B", "price": 1.87},
                                ],
                            }
                        ],
                    }
                ],
            }
        ]

    def calculate_kelly_stake(self, odds, true_prob, bankroll):
        """Calculate Kelly Criterion stake"""
        implied_prob = 1 / odds
        edge = true_prob - implied_prob

        if edge <= 0:
            return 0

        # Kelly formula
        b = odds - 1
        kelly_fraction = (b * true_prob - (1 - true_prob)) / b

        # Apply fractional Kelly
        kelly_fraction *= self.config.get("kelly_settings", {}).get("kelly_fraction", 0.25)

        # Apply maximum bet constraint
        max_bet = self.config.get("risk_management", {}).get("max_bet_percentage", 0.05)
        kelly_fraction = min(kelly_fraction, max_bet)

        return max(0, kelly_fraction * bankroll)

    def run_analysis(self):
        """Run sports betting analysis"""
        print("EQ12 Sports Betting Analysis")
        print("=" * 40)

        odds_data = self.fetch_odds()
        print(f"Fetched odds for {len(odds_data)} games")

        # Demo analysis
        if odds_data:
            game = odds_data[0]
            print(f"Sample Game: {game['away_team']} @ {game['home_team']}")

            if game.get("bookmakers"):
                bookmaker = game["bookmakers"][0]
                if bookmaker.get("markets"):
                    market = bookmaker["markets"][0]
                    if market.get("outcomes"):
                        for outcome in market["outcomes"]:
                            odds = outcome["price"]
                            implied_prob = 1 / odds
                            print(f"  {outcome['name']}: {odds} (implied: {implied_prob:.1%})")

        print("Analysis complete!")


def main():
    parser = argparse.ArgumentParser(description="EQ12 Sports Betting System")
    parser.add_argument("--sport", default="americanfootball_nfl", help="Sport to analyze")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")

    parser.parse_args()

    betting_system = EQ12SportsBetting()
    betting_system.run_analysis()


if __name__ == "__main__":
    main()
