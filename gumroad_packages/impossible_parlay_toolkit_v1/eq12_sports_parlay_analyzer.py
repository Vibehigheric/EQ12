#!/usr/bin/env python3
"""
EQ12 Sports Parlay Analyzer - NHL and NBA Preseason Games
Fetches today's games and creates parlay suggestions based on historical analysis.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any

import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:\\EQ12\\logs\\sports_parlay_analyzer.log"),
        logging.StreamHandler(),
    ],
)


class SportsParlay:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("ODDS_API_KEY")
        if not self.api_key:
            raise ValueError("ODDS_API_KEY environment variable must be set")

        self.base_url = "https://api.the-odds-api.com/v4"
        self.today = datetime.now().strftime("%Y-%m-%d")

        # Sport keys for NHL and NBA preseason
        self.sports = {
            "nhl": "icehockey_nhl",
            "nba_preseason": "basketball_nba_preseason_sg",  # Preseason games
        }

        self.regions = "us"
        self.markets = "h2h,spreads,totals"
        self.odds_format = "american"

        logging.info(f"Initialized SportsParlay for {self.today}")

    def fetch_sports_list(self) -> list[dict]:
        """Fetch available sports to confirm our sport keys"""
        url = f"{self.base_url}/sports"
        params = {"apiKey": self.api_key}

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching sports list: {e}")
            return []

    def fetch_games_for_sport(self, sport_key: str) -> list[dict]:
        """Fetch today's games for a specific sport"""
        url = f"{self.base_url}/sports/{sport_key}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": self.regions,
            "markets": self.markets,
            "oddsFormat": self.odds_format,
            "dateFormat": "iso",
        }

        try:
            logging.info(f"Fetching games for {sport_key}...")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            games = response.json()

            # Filter for today's games
            today_games = []
            for game in games:
                game_date = datetime.fromisoformat(game["commence_time"].replace("Z", "+00:00"))
                if game_date.date() == datetime.now().date():
                    today_games.append(game)

            logging.info(f"Found {len(today_games)} games for {sport_key} today")
            return today_games

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching games for {sport_key}: {e}")
            return []

    def analyze_game_value(self, game: dict) -> dict[str, Any]:
        """Analyze a game for betting value"""
        analysis = {
            "id": game["id"],
            "sport": game["sport_key"],
            "teams": f"{game['away_team']} @ {game['home_team']}",
            "commence_time": game["commence_time"],
            "best_bets": [],
            "confidence": 0,
        }

        if not game.get("bookmakers"):
            return analysis

        # Analyze different markets
        for bookmaker in game["bookmakers"]:
            for market in bookmaker["markets"]:
                market_type = market["key"]

                if market_type == "h2h":
                    # Money line analysis
                    analysis["best_bets"].extend(self._analyze_moneyline(market, game))
                elif market_type == "spreads":
                    # Point spread analysis
                    analysis["best_bets"].extend(self._analyze_spreads(market, game))
                elif market_type == "totals":
                    # Over/under analysis
                    analysis["best_bets"].extend(self._analyze_totals(market, game))

        # Calculate overall confidence based on number of favorable bets
        analysis["confidence"] = min(len(analysis["best_bets"]) * 20, 100)

        return analysis

    def _analyze_moneyline(self, market: dict, game: dict) -> list[dict]:
        """Analyze moneyline bets for value"""
        bets = []

        for outcome in market["outcomes"]:
            # Simple value analysis: look for favorable odds
            price = outcome["price"]

            # Convert American odds to implied probability
            implied_prob = 100 / (price + 100) if price > 0 else abs(price) / (abs(price) + 100)

            # Look for potential value (this is simplified - real analysis would use more data)
            if implied_prob < 0.6:  # Avoid heavy favorites
                bets.append(
                    {
                        "type": "moneyline",
                        "selection": outcome["name"],
                        "odds": price,
                        "implied_probability": round(implied_prob * 100, 1),
                        "reasoning": f"Reasonable odds at {price} for {outcome['name']}",
                    }
                )

        return bets

    def _analyze_spreads(self, market: dict, game: dict) -> list[dict]:
        """Analyze point spread bets"""
        bets = []

        for outcome in market["outcomes"]:
            if "point" in outcome:
                point = outcome["point"]
                price = outcome["price"]

                # Look for spreads close to pick'em or with good value
                if abs(point) <= 2.5:  # Close games
                    bets.append(
                        {
                            "type": "spread",
                            "selection": f"{outcome['name']} {point:+.1f}",
                            "odds": price,
                            "reasoning": f"Close spread of {point:+.1f} suggests competitive game",
                        }
                    )

        return bets

    def _analyze_totals(self, market: dict, game: dict) -> list[dict]:
        """Analyze over/under bets"""
        bets = []

        for outcome in market["outcomes"]:
            if "point" in outcome:
                total = outcome["point"]
                price = outcome["price"]
                name = outcome["name"]

                # Simple total analysis
                if game["sport_key"] == "icehockey_nhl":
                    # NHL: look for totals around 6-6.5
                    if 5.5 <= total <= 7.0:
                        bets.append(
                            {
                                "type": "total",
                                "selection": f"{name} {total}",
                                "odds": price,
                                "reasoning": f"NHL total of {total} in reasonable range",
                            }
                        )
                elif "basketball" in game["sport_key"]:
                    # NBA: look for totals with value
                    if 200 <= total <= 240:
                        bets.append(
                            {
                                "type": "total",
                                "selection": f"{name} {total}",
                                "odds": price,
                                "reasoning": f"NBA preseason total of {total}",
                            }
                        )

        return bets

    def create_parlay_suggestions(self, analyses: list[dict]) -> list[dict]:
        """Create parlay combinations from individual game analyses"""
        parlays = []

        # Filter games with high confidence bets
        high_value_games = [
            game for game in analyses if game["confidence"] >= 40 and game["best_bets"]
        ]

        if len(high_value_games) < 2:
            logging.warning("Not enough high-confidence games for parlays")
            return []

        # Create 2-leg parlays
        for i in range(len(high_value_games)):
            for j in range(i + 1, len(high_value_games)):
                game1 = high_value_games[i]
                game2 = high_value_games[j]

                # Pick best bet from each game
                if game1["best_bets"] and game2["best_bets"]:
                    best_bet1 = max(
                        game1["best_bets"],
                        key=lambda x: (
                            x.get("odds", 0) if x.get("odds", 0) > 0 else -x.get("odds", 0)
                        ),
                    )
                    best_bet2 = max(
                        game2["best_bets"],
                        key=lambda x: (
                            x.get("odds", 0) if x.get("odds", 0) > 0 else -x.get("odds", 0)
                        ),
                    )

                    parlays.append(
                        {
                            "legs": [
                                {
                                    "game": game1["teams"],
                                    "bet": f"{best_bet1['type']}: {best_bet1['selection']}",
                                    "odds": best_bet1["odds"],
                                    "reasoning": best_bet1["reasoning"],
                                },
                                {
                                    "game": game2["teams"],
                                    "bet": f"{best_bet2['type']}: {best_bet2['selection']}",
                                    "odds": best_bet2["odds"],
                                    "reasoning": best_bet2["reasoning"],
                                },
                            ],
                            "combined_confidence": (game1["confidence"] + game2["confidence"]) / 2,
                        }
                    )

        # Sort by confidence and return top 5
        parlays.sort(key=lambda x: x["combined_confidence"], reverse=True)
        return parlays[:5]

    def save_analysis_to_logs(self, data: dict):
        """Save analysis results to JSON log file"""
        timestamp = datetime.now().isoformat()
        log_file = f"C:\\EQ12\\logs\\parlay_analysis_{self.today}.json"

        log_data = {"timestamp": timestamp, "date": self.today, "analysis": data}

        try:
            # Append to existing file or create new one
            if os.path.exists(log_file):
                with open(log_file) as f:
                    existing_data = json.load(f)
                if isinstance(existing_data, list):
                    existing_data.append(log_data)
                else:
                    existing_data = [existing_data, log_data]
            else:
                existing_data = [log_data]

            with open(log_file, "w") as f:
                json.dump(existing_data, f, indent=2)

            logging.info(f"Analysis saved to {log_file}")

        except Exception as e:
            logging.error(f"Error saving analysis: {e}")

    def run_analysis(self) -> dict[str, Any]:
        """Main analysis runner"""
        logging.info("Starting sports parlay analysis...")

        results = {
            "date": self.today,
            "sports_analyzed": [],
            "games_found": {},
            "game_analyses": [],
            "parlay_suggestions": [],
            "summary": {},
        }

        # Check available sports first
        available_sports = self.fetch_sports_list()
        sport_keys = [sport["key"] for sport in available_sports]
        logging.info(f"Available sports: {len(available_sports)}")

        # Analyze each sport
        for sport_name, sport_key in self.sports.items():
            if sport_key not in sport_keys:
                logging.warning(f"Sport {sport_key} not available, trying alternative...")
                if sport_name == "nba_preseason":
                    # Try regular NBA if preseason not available
                    sport_key = "basketball_nba"
                    if sport_key not in sport_keys:
                        continue

            games = self.fetch_games_for_sport(sport_key)
            results["games_found"][sport_name] = len(games)
            results["sports_analyzed"].append(sport_name)

            # Analyze each game
            for game in games:
                analysis = self.analyze_game_value(game)
                results["game_analyses"].append(analysis)

        # Create parlay suggestions
        if results["game_analyses"]:
            results["parlay_suggestions"] = self.create_parlay_suggestions(results["game_analyses"])

        # Generate summary
        total_games = sum(results["games_found"].values())
        high_confidence_games = len([g for g in results["game_analyses"] if g["confidence"] >= 60])

        results["summary"] = {
            "total_games_analyzed": total_games,
            "high_confidence_games": high_confidence_games,
            "parlay_suggestions_generated": len(results["parlay_suggestions"]),
            "sports_with_games": [
                sport for sport, count in results["games_found"].items() if count > 0
            ],
        }

        # Save to logs
        self.save_analysis_to_logs(results)

        return results


def print_results(results: dict[str, Any]):
    """Print formatted results to console"""
    print("\n" + "=" * 60)
    print(f"🏒🏀 EQ12 SPORTS PARLAY ANALYSIS - {results['date']}")
    print("=" * 60)

    # Summary
    summary = results["summary"]
    print("\n📊 SUMMARY:")
    print(f"   • Total games analyzed: {summary['total_games_analyzed']}")
    print(f"   • High confidence games: {summary['high_confidence_games']}")
    print(f"   • Parlay suggestions: {summary['parlay_suggestions_generated']}")
    print(f"   • Sports with games: {', '.join(summary['sports_with_games'])}")

    # Games by sport
    print("\n🎯 GAMES FOUND:")
    for sport, count in results["games_found"].items():
        emoji = "🏒" if "nhl" in sport else "🏀"
        print(f"   {emoji} {sport.upper()}: {count} games")

    # High confidence games
    high_conf_games = [g for g in results["game_analyses"] if g["confidence"] >= 40]
    if high_conf_games:
        print("\n⭐ HIGH VALUE GAMES:")
        for game in high_conf_games:
            sport_emoji = "🏒" if "nhl" in game["sport"] else "🏀"
            print(f"   {sport_emoji} {game['teams']} (Confidence: {game['confidence']}%)")
            for bet in game["best_bets"][:2]:  # Show top 2 bets
                print(f"      └─ {bet['type'].upper()}: {bet['selection']} ({bet['odds']:+d})")
                print(f"         {bet['reasoning']}")

    # Parlay suggestions
    if results["parlay_suggestions"]:
        print("\n💰 PARLAY SUGGESTIONS:")
        for i, parlay in enumerate(results["parlay_suggestions"][:3], 1):
            print(f"\n   PARLAY #{i} (Confidence: {parlay['combined_confidence']:.1f}%)")
            for j, leg in enumerate(parlay["legs"], 1):
                print(f"   LEG {j}: {leg['game']}")
                print(f"           {leg['bet']} ({leg['odds']:+d})")
                print(f"           {leg['reasoning']}")
    else:
        print("\n⚠️  No parlays generated - insufficient high-confidence games")

    print("\n💡 DISCLAIMER: This analysis is for educational purposes only.")
    print("   Please gamble responsibly and within your means.")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="EQ12 Sports Parlay Analyzer")
    parser.add_argument("--api-key", type=str, help="The Odds API key")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--save-only", action="store_true", help="Save to logs without printing")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        analyzer = SportsParlay(args.api_key)
        results = analyzer.run_analysis()

        if not args.save_only:
            print_results(results)

        logging.info("Analysis completed successfully")

    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
