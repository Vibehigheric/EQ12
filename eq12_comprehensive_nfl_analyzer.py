#!/usr/bin/env python3
"""
EQ12 Comprehensive NFL Analyzer
Handles moneyline, spread, and live game analysis
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path

import requests


class EQ12ComprehensiveNFLAnalyzer:
    def __init__(self):
        self.setup_logging()
        self.api_key = "4b0b0cba11ff90531efaae3b7f546734"
        self.bankroll = 1000.0

    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("C:/EQ12/logs")
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_dir / "comprehensive_nfl.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("🏈 EQ12 Comprehensive NFL Analyzer initialized")

    def get_nfl_odds_data(self) -> dict[str, list[dict]]:
        """Fetch NFL odds for both moneylines and spreads"""
        try:
            url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
            params = {
                "apiKey": self.api_key,
                "regions": "us",
                "markets": "h2h,spreads",
                "oddsFormat": "american",
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            games = response.json()

            self.logger.info(f"📡 Fetched {len(games)} NFL games with ML+Spreads")
            return {"games": games, "fetch_time": datetime.now(UTC).isoformat()}

        except Exception as e:
            self.logger.error(f"❌ Failed to fetch NFL odds: {e}")
            return {"games": [], "fetch_time": datetime.now(UTC).isoformat()}

    def analyze_game_status(self, games: list[dict]) -> dict[str, list[dict]]:
        """Categorize games by status: live, upcoming, finished"""
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

                # Enhanced game info
                game_info = {
                    **game,
                    "game_time_local": local_time.strftime("%m/%d %I:%M %p"),
                    "elapsed_hours": elapsed_hours,
                    "game_time_utc": game_time.isoformat(),
                }

                if game_time <= current_time:
                    if elapsed_hours < 4:  # Game likely still live (NFL games ~3.5 hours)
                        game_info["status"] = "LIVE"
                        live_games.append(game_info)
                        self.logger.info(
                            f"🔴 LIVE: {game['away_team']} @ {game['home_team']} "
                            f"({elapsed_hours:.1f}h elapsed)"
                        )
                    else:
                        game_info["status"] = "FINISHED"
                        finished_games.append(game_info)
                        self.logger.info(f"⚫ FINISHED: {game['away_team']} @ {game['home_team']}")
                else:
                    game_info["status"] = "UPCOMING"
                    upcoming_games.append(game_info)
                    self.logger.info(
                        f"🕐 UPCOMING: {game['away_team']} @ {game['home_team']} "
                        f"at {local_time.strftime('%I:%M %p')}"
                    )

            except Exception as e:
                self.logger.warning(f"⚠️ Could not parse game: {e}")

        return {
            "live": live_games,
            "upcoming": upcoming_games,
            "finished": finished_games,
        }

    def extract_moneyline_opportunities(self, games: list[dict]) -> list[dict]:
        """Extract high-value moneyline betting opportunities"""
        ml_opportunities = []

        for game in games:
            try:
                for bookmaker in game.get("bookmakers", []):
                    for market in bookmaker.get("markets", []):
                        if market["key"] == "h2h":  # Head-to-head (moneyline)
                            for outcome in market["outcomes"]:
                                team = outcome["name"]
                                odds = outcome["price"]

                                # Calculate implied probability and model probability
                                implied_prob = self.implied_probability(odds)
                                model_prob = self.calculate_model_probability(
                                    team, game["home_team"], game["away_team"]
                                )

                                # Calculate expected value
                                if odds > 0:
                                    ev = (model_prob * odds - (1 - model_prob) * 100) / 100
                                else:
                                    ev = (model_prob * 100 - (1 - model_prob) * abs(odds)) / abs(
                                        odds
                                    )

                                ev_percent = ev * 100

                                # Only include positive EV bets
                                if ev_percent > 1:
                                    ml_opportunities.append(
                                        {
                                            "game_id": f"{game['away_team']}_at_{game['home_team']}",
                                            "team": team,
                                            "odds": odds,
                                            "sportsbook": bookmaker["title"],
                                            "implied_prob": implied_prob,
                                            "model_prob": model_prob,
                                            "expected_value": ev_percent,
                                            "game_status": game.get("status", "UNKNOWN"),
                                            "game_time": game.get("game_time_local", "Unknown"),
                                            "elapsed_hours": game.get("elapsed_hours", 0),
                                            "value_grade": self.grade_ml_value(ev_percent),
                                            "market": "Moneyline",
                                        }
                                    )

            except Exception as e:
                self.logger.warning(f"⚠️ Error processing ML for game: {e}")

        # Sort by expected value
        ml_opportunities.sort(key=lambda x: x["expected_value"], reverse=True)
        self.logger.info(f"💰 Found {len(ml_opportunities)} ML opportunities")
        return ml_opportunities

    def extract_spread_opportunities(self, games: list[dict]) -> list[dict]:
        """Extract high-value spread betting opportunities"""
        spread_opportunities = []

        for game in games:
            try:
                for bookmaker in game.get("bookmakers", []):
                    for market in bookmaker.get("markets", []):
                        if market["key"] == "spreads":
                            for outcome in market["outcomes"]:
                                team = outcome["name"]
                                spread = outcome["point"]
                                odds = outcome["price"]

                                # Analyze spread value
                                spread_analysis = self.analyze_spread_value(spread, odds)
                                ev_percent = spread_analysis["expected_value"]

                                # Only include positive EV spreads
                                if ev_percent > 1:
                                    spread_opportunities.append(
                                        {
                                            "game_id": f"{game['away_team']}_at_{game['home_team']}",
                                            "team": team,
                                            "spread": spread,
                                            "odds": odds,
                                            "sportsbook": bookmaker["title"],
                                            "expected_value": ev_percent,
                                            "is_hook": abs(spread) % 1 == 0.5,
                                            "is_key_number": abs(spread) in [3, 7, 10, 14, 17, 21],
                                            "game_status": game.get("status", "UNKNOWN"),
                                            "game_time": game.get("game_time_local", "Unknown"),
                                            "elapsed_hours": game.get("elapsed_hours", 0),
                                            "value_grade": self.grade_spread_value(
                                                ev_percent,
                                                spread,
                                                abs(spread) % 1 == 0.5,
                                            ),
                                            "market": "Spread",
                                        }
                                    )

            except Exception as e:
                self.logger.warning(f"⚠️ Error processing spreads for game: {e}")

        # Sort by expected value
        spread_opportunities.sort(key=lambda x: x["expected_value"], reverse=True)
        self.logger.info(f"📊 Found {len(spread_opportunities)} spread opportunities")
        return spread_opportunities

    def calculate_model_probability(self, team: str, home_team: str, away_team: str) -> float:
        """Calculate model probability for moneyline bets"""
        is_home = team == home_team

        # Base probability (50/50)
        base_prob = 0.5

        # Home field advantage
        if is_home:
            base_prob += 0.07  # 7% home field advantage

        # Team-specific adjustments (simplified model)
        strong_teams = [
            "Kansas City Chiefs",
            "Buffalo Bills",
            "Baltimore Ravens",
            "Philadelphia Eagles",
            "Dallas Cowboys",
            "Detroit Lions",
        ]
        weak_teams = [
            "Carolina Panthers",
            "Arizona Cardinals",
            "New England Patriots",
            "Washington Commanders",
            "Las Vegas Raiders",
        ]

        if team in strong_teams:
            base_prob += 0.1
        elif team in weak_teams:
            base_prob -= 0.1

        return max(0.1, min(0.9, base_prob))

    def analyze_spread_value(self, spread: float, odds: int) -> dict:
        """Analyze spread betting value"""
        # Calculate implied probability
        implied_prob = self.implied_probability(odds)

        # Model probability based on spread value
        # Hook spreads (half-points) are more valuable
        is_hook = abs(spread) % 1 == 0.5
        is_key_number = abs(spread) in [3, 7, 10, 14, 17, 21]

        # Base model probability around 50%
        model_prob = 0.52

        # Adjust for hooks (no push risk)
        if is_hook:
            model_prob += 0.03

        # Adjust for key numbers (more variance)
        if is_key_number:
            model_prob -= 0.02

        # Calculate expected value
        if odds > 0:
            ev = (model_prob * odds - (1 - model_prob) * 100) / 100
        else:
            ev = (model_prob * 100 - (1 - model_prob) * abs(odds)) / abs(odds)

        return {
            "expected_value": ev * 100,
            "implied_prob": implied_prob,
            "model_prob": model_prob,
            "is_hook": is_hook,
            "is_key_number": is_key_number,
        }

    def implied_probability(self, odds: int) -> float:
        """Convert American odds to implied probability"""
        if odds > 0:
            return 100 / (odds + 100)
        return abs(odds) / (abs(odds) + 100)

    def grade_ml_value(self, ev: float) -> str:
        """Grade moneyline expected value"""
        if ev >= 15:
            return "🟢 ELITE"
        if ev >= 10:
            return "🟢 STRONG"
        if ev >= 5:
            return "🟡 SOLID"
        if ev >= 2:
            return "🟠 FAIR"
        return "🔴 AVOID"

    def grade_spread_value(self, ev: float, spread: float, is_hook: bool) -> str:
        """Grade spread expected value"""
        if ev >= 8 and is_hook:
            return "🟢 ELITE"
        if ev >= 6:
            return "🟢 STRONG"
        if ev >= 4:
            return "🟡 SOLID"
        if ev >= 2:
            return "🟠 FAIR"
        return "🔴 AVOID"

    def build_comprehensive_parlays(self, ml_ops: list[dict], spread_ops: list[dict]) -> list[dict]:
        """Build comprehensive parlays mixing ML and spreads"""
        parlays = []

        # Dedupe to one pick per game
        ml_deduped = self.dedupe_games(ml_ops)
        spread_deduped = self.dedupe_games(spread_ops)

        # Strategy 1: Elite Mixed Parlay (Best of both worlds)
        elite_ml = [op for op in ml_deduped if "ELITE" in op["value_grade"]][:3]
        elite_spreads = [op for op in spread_deduped if "ELITE" in op["value_grade"]][:3]

        if len(elite_ml) + len(elite_spreads) >= 4:
            mixed_legs = elite_ml + elite_spreads
            odds, multiplier = self.calculate_parlay_odds(mixed_legs)
            stake = min(100, self.bankroll * 0.1)
            payout = stake * multiplier

            parlays.append(
                {
                    "strategy": "Elite Mixed Parlay",
                    "description": "Best ML + Spread combinations",
                    "legs": mixed_legs,
                    "leg_count": len(mixed_legs),
                    "american_odds": round(odds),
                    "multiplier": round(multiplier, 2),
                    "recommended_stake": round(stake, 2),
                    "potential_payout": round(payout, 2),
                    "net_profit": round(payout - stake, 2),
                }
            )

        # Strategy 2: Live Game Special
        live_ops = [op for op in ml_ops + spread_ops if op["game_status"] == "LIVE"]
        live_deduped = self.dedupe_games(live_ops)[:6]

        if len(live_deduped) >= 3:
            odds, multiplier = self.calculate_parlay_odds(live_deduped)
            stake = min(50, self.bankroll * 0.05)
            payout = stake * multiplier

            parlays.append(
                {
                    "strategy": "Live Game Special",
                    "description": "In-play opportunities",
                    "legs": live_deduped,
                    "leg_count": len(live_deduped),
                    "american_odds": round(odds),
                    "multiplier": round(multiplier, 2),
                    "recommended_stake": round(stake, 2),
                    "potential_payout": round(payout, 2),
                    "net_profit": round(payout - stake, 2),
                }
            )

        # Strategy 3: Upcoming Games Conservative
        upcoming_ops = [op for op in ml_ops + spread_ops if op["game_status"] == "UPCOMING"]
        upcoming_deduped = self.dedupe_games(upcoming_ops)
        conservative_upcoming = [op for op in upcoming_deduped if op["expected_value"] >= 5][:5]

        if len(conservative_upcoming) >= 3:
            odds, multiplier = self.calculate_parlay_odds(conservative_upcoming)
            stake = min(75, self.bankroll * 0.075)
            payout = stake * multiplier

            parlays.append(
                {
                    "strategy": "Upcoming Conservative",
                    "description": "High-confidence future games",
                    "legs": conservative_upcoming,
                    "leg_count": len(conservative_upcoming),
                    "american_odds": round(odds),
                    "multiplier": round(multiplier, 2),
                    "recommended_stake": round(stake, 2),
                    "potential_payout": round(payout, 2),
                    "net_profit": round(payout - stake, 2),
                }
            )

        return parlays

    def dedupe_games(self, opportunities: list[dict]) -> list[dict]:
        """Remove duplicates, keeping best pick per game"""
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

    def calculate_parlay_odds(self, legs: list[dict]) -> tuple[float, float]:
        """Calculate parlay odds and multiplier"""
        total_prob = 1.0

        for leg in legs:
            prob = self.implied_probability(leg["odds"])
            total_prob *= prob

        if total_prob > 0:
            multiplier = 1 / total_prob
            american_odds = self.decimal_to_american(multiplier)
            return american_odds, multiplier

        return 0, 1

    def decimal_to_american(self, decimal_odds: float) -> float:
        """Convert decimal odds to American format"""
        if decimal_odds >= 2:
            return (decimal_odds - 1) * 100
        return -100 / (decimal_odds - 1)

    def format_comprehensive_output(
        self,
        parlays: list[dict],
        ml_ops: list[dict],
        spread_ops: list[dict],
        game_status: dict,
    ) -> str:
        """Format comprehensive analysis output"""

        output = f"""
🏈 EQ12 COMPREHENSIVE NFL ANALYZER 🏈
⏰ Generated: {datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")}
💰 Bankroll: ${self.bankroll:,.2f}
🎯 Analysis: MONEYLINE + SPREADS + LIVE DATA
============================================================

📊 GAME STATUS SUMMARY:
🔴 Live Games: {len(game_status["live"])}
🕐 Upcoming Games: {len(game_status["upcoming"])}
⚫ Finished Games: {len(game_status["finished"])}

💰 OPPORTUNITIES FOUND:
📈 Moneyline: {len(ml_ops)} valuable picks
📊 Spreads: {len(spread_ops)} valuable picks
🎯 Total Parlays: {len(parlays)}

============================================================

"""

        for i, parlay in enumerate(parlays, 1):
            output += f"""🎯 PARLAY #{i}: {parlay["strategy"]}
📖 {parlay["description"]}
📊 Legs: {parlay["leg_count"]} | Odds: {parlay["american_odds"]:+} | Stake: ${parlay["recommended_stake"]}
💸 Payout: ${parlay["potential_payout"]:,.2f} | Net: +${parlay["net_profit"]:,.2f}
----------------------------------------
"""

            for j, leg in enumerate(parlay["legs"], 1):
                market_info = f"{leg['market']}"
                if leg["market"] == "Spread":
                    market_info += f" {leg['spread']:+}"

                status_icon = (
                    "🔴"
                    if leg["game_status"] == "LIVE"
                    else "🕐" if leg["game_status"] == "UPCOMING" else "⚫"
                )

                output += f"""   {j}. {leg["team"]} ({market_info})
      📈 {leg["odds"]:+} | EV: {leg["expected_value"]:+.1f}% | {leg["value_grade"]}
      {status_icon} {leg["game_status"]} | {leg["game_time"]}
      🏟️  {leg["game_id"].replace("_at_", " @ ")}
"""

            output += "\n"

        # Live games detail
        if game_status["live"]:
            output += "\n🔴 LIVE GAMES ANALYSIS:\n"
            for game in game_status["live"]:
                output += f"   {game['away_team']} @ {game['home_team']} - {game['elapsed_hours']:.1f}h elapsed\n"

        output += """
📊 VALUE LEGEND:
🟢 ELITE = 8%+ EV  |  🟢 STRONG = 6%+ EV  |  🟡 SOLID = 4%+ EV
🟠 FAIR = 2%+ EV  |  🔴 AVOID = <2% EV

🚀 Ready to place these comprehensive parlays? LFG! 🚀
"""

        return output

    def save_comprehensive_results(
        self,
        parlays: list[dict],
        ml_ops: list[dict],
        spread_ops: list[dict],
        game_status: dict,
    ) -> str:
        """Save comprehensive analysis results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:/EQ12/logs/nfl_comprehensive_{timestamp}.json"

        results = {
            "timestamp": datetime.now().isoformat(),
            "bankroll": self.bankroll,
            "game_status": game_status,
            "moneyline_opportunities": ml_ops,
            "spread_opportunities": spread_ops,
            "parlays": parlays,
            "summary": {
                "total_ml_ops": len(ml_ops),
                "total_spread_ops": len(spread_ops),
                "total_parlays": len(parlays),
                "live_games": len(game_status["live"]),
                "upcoming_games": len(game_status["upcoming"]),
            },
        }

        with open(filename, "w") as f:
            json.dump(results, f, indent=2, default=str)

        self.logger.info(f"💾 Comprehensive results saved to {filename}")
        return filename

    async def run_comprehensive_analysis(self) -> dict:
        """Main comprehensive analysis execution"""
        try:
            self.logger.info("🚀 Starting EQ12 Comprehensive NFL Analysis")

            # Fetch odds data
            odds_data = self.get_nfl_odds_data()
            if not odds_data["games"]:
                return {"success": False, "message": "No games data available"}

            # Analyze game status
            game_status = self.analyze_game_status(odds_data["games"])

            # Extract opportunities
            ml_opportunities = self.extract_moneyline_opportunities(
                game_status["live"] + game_status["upcoming"]
            )
            spread_opportunities = self.extract_spread_opportunities(
                game_status["live"] + game_status["upcoming"]
            )

            # Build comprehensive parlays
            parlays = self.build_comprehensive_parlays(ml_opportunities, spread_opportunities)

            # Generate output
            output = self.format_comprehensive_output(
                parlays, ml_opportunities, spread_opportunities, game_status
            )
            print(output)

            # Save results
            results_file = self.save_comprehensive_results(
                parlays, ml_opportunities, spread_opportunities, game_status
            )

            return {
                "success": True,
                "message": f"Generated {len(parlays)} comprehensive parlay strategies",
                "results_file": results_file,
            }

        except Exception as e:
            self.logger.error(f"💥 Comprehensive analysis failed: {e}")
            return {"success": False, "message": str(e)}


def main():
    parser = argparse.ArgumentParser(description="EQ12 Comprehensive NFL Analyzer")
    parser.add_argument("--bankroll", type=float, default=1000.0, help="Bankroll amount")

    args = parser.parse_args()

    analyzer = EQ12ComprehensiveNFLAnalyzer()
    analyzer.bankroll = args.bankroll

    try:
        result = asyncio.run(analyzer.run_comprehensive_analysis())
        if result["success"]:
            print(f"\n✅ {result['message']}")
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
