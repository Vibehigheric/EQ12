#!/usr/bin/env python3
"""
EQ12 ML + Spread Analyzer with Live Game Detection
Extended from working spread optimizer
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import UTC, datetime

import requests


class EQ12MLSpreadAnalyzer:
    def __init__(self):
        self.api_key = "ODDS_API_KEY_PLACEHOLDER"
        self.bankroll = 1000.0

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("NFL ML + Spread Analyzer initialized")

    def get_nfl_data(self) -> dict:
        """Fetch NFL odds for both moneylines and spreads"""
        try:
            url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
            params = {
                "apiKey": self.api_key,
                "regions": "us",
                "markets": "h2h,spreads",  # Both moneylines and spreads
                "oddsFormat": "american",
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            games = response.json()

            self.logger.info(f"Fetched {len(games)} NFL games with ML+Spreads")
            return {"success": True, "games": games}

        except Exception as e:
            self.logger.error(f"Failed to fetch NFL data: {e}")
            return {"success": False, "error": str(e)}

    def analyze_game_status(self, games: list) -> dict:
        """Determine which games are live, upcoming, or finished"""
        current_time = datetime.now(UTC)

        live_games = []
        upcoming_games = []
        finished_games = []

        for game in games:
            try:
                game_time = datetime.fromisoformat(game["commence_time"].replace("Z", "+00:00"))
                local_time = game_time.astimezone()

                # Calculate elapsed time
                time_diff = current_time - game_time
                elapsed_hours = time_diff.total_seconds() / 3600

                game_info = {
                    **game,
                    "game_time_local": local_time.strftime("%m/%d %I:%M %p"),
                    "elapsed_hours": elapsed_hours,
                    "start_time_utc": game_time.isoformat(),
                }

                if game_time <= current_time:
                    if elapsed_hours < 4:  # NFL games ~3.5 hours
                        game_info["status"] = "LIVE"
                        live_games.append(game_info)
                        self.logger.info(
                            f"LIVE: {game['away_team']} @ {game['home_team']} ({elapsed_hours:.1f}h)"
                        )
                    else:
                        game_info["status"] = "FINISHED"
                        finished_games.append(game_info)
                        self.logger.info(f"FINISHED: {game['away_team']} @ {game['home_team']}")
                else:
                    game_info["status"] = "UPCOMING"
                    upcoming_games.append(game_info)
                    self.logger.info(
                        f"UPCOMING: {game['away_team']} @ {game['home_team']} at {local_time.strftime('%I:%M %p')}"
                    )

            except Exception as e:
                self.logger.warning(f"Could not parse game: {e}")

        return {
            "live": live_games,
            "upcoming": upcoming_games,
            "finished": finished_games,
        }

    def extract_ml_opportunities(self, games: list) -> list:
        """Extract moneyline betting opportunities"""
        ml_ops = []

        for game in games:
            try:
                for bookmaker in game.get("bookmakers", []):
                    for market in bookmaker.get("markets", []):
                        if market["key"] == "h2h":  # Moneyline market
                            for outcome in market["outcomes"]:
                                team = outcome["name"]
                                odds = outcome["price"]

                                # Simple EV calculation
                                self.implied_probability(odds)
                                model_prob = self.calculate_model_prob(
                                    team, game["home_team"], game["away_team"]
                                )

                                if odds > 0:
                                    ev = (model_prob * odds - (1 - model_prob) * 100) / 100
                                else:
                                    ev = (model_prob * 100 - (1 - model_prob) * abs(odds)) / abs(
                                        odds
                                    )

                                ev_percent = ev * 100

                                if ev_percent > 1:  # Only positive EV
                                    ml_ops.append(
                                        {
                                            "game_id": f"{game['away_team']}_at_{game['home_team']}",
                                            "team": team,
                                            "odds": odds,
                                            "sportsbook": bookmaker["title"],
                                            "expected_value": ev_percent,
                                            "status": game.get("status", "UNKNOWN"),
                                            "game_time": game.get("game_time_local", "Unknown"),
                                            "elapsed_hours": game.get("elapsed_hours", 0),
                                            "market": "Moneyline",
                                            "value_grade": self.grade_value(ev_percent),
                                        }
                                    )

            except Exception as e:
                self.logger.warning(f"Error processing ML: {e}")

        ml_ops.sort(key=lambda x: x["expected_value"], reverse=True)
        self.logger.info(f"Found {len(ml_ops)} ML opportunities")
        return ml_ops

    def extract_spread_opportunities(self, games: list) -> list:
        """Extract spread betting opportunities"""
        spread_ops = []

        for game in games:
            try:
                for bookmaker in game.get("bookmakers", []):
                    for market in bookmaker.get("markets", []):
                        if market["key"] == "spreads":
                            for outcome in market["outcomes"]:
                                team = outcome["name"]
                                spread = outcome["point"]
                                odds = outcome["price"]

                                # Spread value analysis
                                is_hook = abs(spread) % 1 == 0.5
                                self.implied_probability(odds)

                                # Simple spread model
                                model_prob = 0.52
                                if is_hook:
                                    model_prob += 0.03  # Hooks are valuable

                                if odds > 0:
                                    ev = (model_prob * odds - (1 - model_prob) * 100) / 100
                                else:
                                    ev = (model_prob * 100 - (1 - model_prob) * abs(odds)) / abs(
                                        odds
                                    )

                                ev_percent = ev * 100

                                if ev_percent > 1:
                                    spread_ops.append(
                                        {
                                            "game_id": f"{game['away_team']}_at_{game['home_team']}",
                                            "team": team,
                                            "spread": spread,
                                            "odds": odds,
                                            "sportsbook": bookmaker["title"],
                                            "expected_value": ev_percent,
                                            "is_hook": is_hook,
                                            "status": game.get("status", "UNKNOWN"),
                                            "game_time": game.get("game_time_local", "Unknown"),
                                            "elapsed_hours": game.get("elapsed_hours", 0),
                                            "market": "Spread",
                                            "value_grade": self.grade_value(ev_percent),
                                        }
                                    )

            except Exception as e:
                self.logger.warning(f"Error processing spreads: {e}")

        spread_ops.sort(key=lambda x: x["expected_value"], reverse=True)
        self.logger.info(f"Found {len(spread_ops)} spread opportunities")
        return spread_ops

    def calculate_model_prob(self, team: str, home_team: str, away_team: str) -> float:
        """Simple model probability calculation"""
        is_home = team == home_team
        base_prob = 0.5

        # Home field advantage
        if is_home:
            base_prob += 0.07

        # Team strength adjustments (simplified)
        strong_teams = [
            "Kansas City Chiefs",
            "Buffalo Bills",
            "Baltimore Ravens",
            "Philadelphia Eagles",
            "Detroit Lions",
            "Dallas Cowboys",
        ]
        weak_teams = ["Carolina Panthers", "Arizona Cardinals", "New England Patriots"]

        if team in strong_teams:
            base_prob += 0.1
        elif team in weak_teams:
            base_prob -= 0.1

        return max(0.1, min(0.9, base_prob))

    def implied_probability(self, odds: int) -> float:
        """Convert American odds to implied probability"""
        if odds > 0:
            return 100 / (odds + 100)
        return abs(odds) / (abs(odds) + 100)

    def grade_value(self, ev: float) -> str:
        """Grade expected value"""
        if ev >= 10:
            return "ELITE"
        if ev >= 6:
            return "STRONG"
        if ev >= 3:
            return "SOLID"
        return "FAIR"

    def dedupe_games(self, opportunities: list) -> list:
        """Keep only best pick per game"""
        seen_games = {}
        deduped = []

        for op in opportunities:
            game_id = op["game_id"]
            if game_id not in seen_games:
                seen_games[game_id] = op
                deduped.append(op)
            elif op["expected_value"] > seen_games[game_id]["expected_value"]:
                deduped.remove(seen_games[game_id])
                seen_games[game_id] = op
                deduped.append(op)

        return deduped

    def build_mixed_parlays(self, ml_ops: list, spread_ops: list) -> list:
        """Build mixed ML + Spread parlays"""
        parlays = []

        # Dedupe to one pick per game
        ml_deduped = self.dedupe_games(ml_ops)
        spread_deduped = self.dedupe_games(spread_ops)

        # Strategy 1: Live Game Special
        live_ops = [op for op in ml_ops + spread_ops if op["status"] == "LIVE"]
        live_deduped = self.dedupe_games(live_ops)[:6]

        if len(live_deduped) >= 3:
            parlays.append(
                {
                    "strategy": "Live Game Special",
                    "description": "In-play betting opportunities",
                    "legs": live_deduped,
                }
            )

        # Strategy 2: Elite Mixed (Best ML + Spread)
        elite_ml = [op for op in ml_deduped if op["value_grade"] == "ELITE"][:3]
        elite_spreads = [op for op in spread_deduped if op["value_grade"] == "ELITE"][:3]
        mixed_legs = elite_ml + elite_spreads

        if len(mixed_legs) >= 4:
            parlays.append(
                {
                    "strategy": "Elite Mixed Parlay",
                    "description": "Best ML + Spread combinations",
                    "legs": mixed_legs,
                }
            )

        # Strategy 3: Today's Conservative
        today_ops = [op for op in ml_ops + spread_ops if op["status"] == "UPCOMING"]
        today_deduped = self.dedupe_games(today_ops)
        conservative = [op for op in today_deduped if op["expected_value"] >= 5][:5]

        if len(conservative) >= 3:
            parlays.append(
                {
                    "strategy": "Today's Conservative",
                    "description": "High-confidence upcoming games",
                    "legs": conservative,
                }
            )

        return parlays

    def format_output(
        self, parlays: list, ml_ops: list, spread_ops: list, game_status: dict
    ) -> str:
        """Format comprehensive output"""

        output = f"""
NFL ML + SPREAD ANALYZER
Generated: {datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")}
Bankroll: ${self.bankroll:,.2f}
========================================

GAME STATUS:
Live Games: {len(game_status["live"])}
Upcoming Games: {len(game_status["upcoming"])}
Finished Games: {len(game_status["finished"])}

OPPORTUNITIES:
Moneyline: {len(ml_ops)} picks
Spreads: {len(spread_ops)} picks
Parlays: {len(parlays)}

========================================

"""

        for i, parlay in enumerate(parlays, 1):
            output += f"PARLAY #{i}: {parlay['strategy']}\n"
            output += f"Description: {parlay['description']}\n"
            output += f"Legs: {len(parlay['legs'])}\n"
            output += "----------------------------------------\n"

            for j, leg in enumerate(parlay["legs"], 1):
                market_info = leg["market"]
                if leg["market"] == "Spread":
                    market_info += f" {leg['spread']:+}"

                status_icon = (
                    "LIVE"
                    if leg["status"] == "LIVE"
                    else "UPCOMING" if leg["status"] == "UPCOMING" else "FINISHED"
                )

                output += f"   {j}. {leg['team']} ({market_info})\n"
                output += f"      Odds: {leg['odds']:+} | EV: {leg['expected_value']:+.1f}% | {leg['value_grade']}\n"
                output += f"      {status_icon} | {leg['game_time']}\n"
                output += f"      Game: {leg['game_id'].replace('_at_', ' @ ')}\n"

            output += "\n"

        # Live games detail
        if game_status["live"]:
            output += "LIVE GAMES ANALYSIS:\n"
            for game in game_status["live"]:
                output += f"   {game['away_team']} @ {game['home_team']} - {game['elapsed_hours']:.1f}h elapsed\n"
            output += "\n"

        return output

    async def run_analysis(self) -> dict:
        """Main analysis execution"""
        try:
            self.logger.info("Starting NFL ML + Spread Analysis")

            # Fetch data
            data = self.get_nfl_data()
            if not data["success"]:
                return {"success": False, "message": data["error"]}

            # Analyze game status
            game_status = self.analyze_game_status(data["games"])

            # Extract opportunities
            all_games = game_status["live"] + game_status["upcoming"]
            ml_ops = self.extract_ml_opportunities(all_games)
            spread_ops = self.extract_spread_opportunities(all_games)

            # Build parlays
            parlays = self.build_mixed_parlays(ml_ops, spread_ops)

            # Generate output
            output = self.format_output(parlays, ml_ops, spread_ops, game_status)
            print(output)

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results = {
                "timestamp": datetime.now().isoformat(),
                "bankroll": self.bankroll,
                "game_status": game_status,
                "moneyline_opportunities": ml_ops,
                "spread_opportunities": spread_ops,
                "parlays": parlays,
            }

            filename = f"C:/EQ12/logs/nfl_ml_spread_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(results, f, indent=2, default=str)

            return {
                "success": True,
                "message": f"Generated {len(parlays)} ML+Spread parlays",
                "results_file": filename,
            }

        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return {"success": False, "message": str(e)}


def main():
    parser = argparse.ArgumentParser(description="NFL ML + Spread Analyzer")
    parser.add_argument("--bankroll", type=float, default=1000.0, help="Bankroll amount")

    args = parser.parse_args()

    analyzer = EQ12MLSpreadAnalyzer()
    analyzer.bankroll = args.bankroll

    try:
        result = asyncio.run(analyzer.run_analysis())
        if result["success"]:
            print(f"\n✅ {result['message']}")
            if "results_file" in result:
                print(f"📁 Results: {result['results_file']}")
        else:
            print(f"\n❌ {result['message']}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Analysis stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
