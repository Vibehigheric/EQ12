#!/usr/bin/env python3
"""
EQ12 Enhanced Odds API Integration
Based on: https://the-odds-api.com/sports-odds-data/sports-apis.html
"""


import requests


class EQ12EnhancedOddsAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.the-odds-api.com/v4"

        # Comprehensive sports mapping from The Odds API
        self.sports = {
            "nhl": "icehockey_nhl",
            "nfl": "americanfootball_nfl",
            "nba": "basketball_nba",
            "mlb": "baseball_mlb",
            "ncaa": "americanfootball_ncaaf",
            "ncaab": "basketball_ncaab",
        }

        # Major US bookmakers from The Odds API
        self.bookmakers = [
            "draftkings",
            "fanduel",
            "betmgm",
            "caesars",
            "bovada",
            "mybookieag",
            "betrivers",
            "pointsbetsus",
            "foxbet",
        ]

        # All available betting markets
        self.markets = [
            "h2h",  # Moneyline
            "spreads",  # Point spreads
            "totals",  # Over/under
            "outrights",  # Futures
            "h2h,spreads,totals",  # Combined markets
        ]

    def get_comprehensive_odds(self, sport: str, region: str = "us"):
        """Get comprehensive odds data for all markets and bookmakers"""

        sport_key = self.sports.get(sport.lower(), sport)

        all_odds = {}

        for market in self.markets:
            if market == "outrights":
                continue  # Skip futures for now

            url = f"{self.base_url}/sports/{sport_key}/odds"
            params = {
                "apiKey": self.api_key,
                "regions": region,
                "markets": market,
                "oddsFormat": "american",
                "dateFormat": "iso",
            }

            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    all_odds[market] = response.json()
                else:
                    print(f"Error fetching {market}: {response.status_code}")
            except Exception as e:
                print(f"Exception fetching {market}: {e}")

        return all_odds

    def detect_arbitrage_opportunities(self, odds_data: dict):
        """Detect arbitrage opportunities across bookmakers"""

        arbitrage_opps = []

        if "h2h" not in odds_data:
            return arbitrage_opps

        for game in odds_data["h2h"]:
            if len(game["bookmakers"]) < 2:
                continue

            # Find best odds for each outcome
            home_best = {"odds": float("-in"), "bookmaker": None}
            away_best = {"odds": float("-in"), "bookmaker": None}

            for bookmaker in game["bookmakers"]:
                for market in bookmaker["markets"]:
                    if market["key"] == "h2h":
                        for outcome in market["outcomes"]:
                            odds = outcome["price"]

                            if outcome["name"] == game["home_team"]:
                                if odds > home_best["odds"]:
                                    home_best = {
                                        "odds": odds,
                                        "bookmaker": bookmaker["title"],
                                    }
                            else:
                                if odds > away_best["odds"]:
                                    away_best = {
                                        "odds": odds,
                                        "bookmaker": bookmaker["title"],
                                    }

            # Calculate arbitrage
            if home_best["odds"] > 0 and away_best["odds"] > 0:
                home_implied = 100 / (home_best["odds"] + 100)
                away_implied = 100 / (away_best["odds"] + 100)
                total_implied = home_implied + away_implied

                if total_implied < 1.0:  # Arbitrage opportunity!
                    profit_margin = (1 - total_implied) * 100
                    arbitrage_opps.append(
                        {
                            "game": f"{game['away_team']} @ {game['home_team']}",
                            "profit_margin": f"{profit_margin:.2f}%",
                            "home_bet": f"{game['home_team']} {home_best['odds']} ({home_best['bookmaker']})",
                            "away_bet": f"{game['away_team']} {away_best['odds']} ({away_best['bookmaker']})",
                            "home_stake_pct": f"{home_implied / (home_implied + away_implied) * 100:.1f}%",
                            "away_stake_pct": f"{away_implied / (home_implied + away_implied) * 100:.1f}%",
                        }
                    )

        return arbitrage_opps

    def get_historical_odds(self, sport: str, date: str):
        """Get historical odds data for model training"""

        sport_key = self.sports.get(sport.lower(), sport)

        url = f"{self.base_url}/historical/sports/{sport_key}/odds"
        params = {
            "apiKey": self.api_key,
            "date": date,
            "regions": "us",
            "markets": "h2h,spreads,totals",
        }

        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else None


# Integration instance
enhanced_odds_api = EQ12EnhancedOddsAPI(os.getenv("ODDS_API_KEY"))
