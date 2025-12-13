#!/usr/bin/env python3
"""
EQ12 NFL Totals (Over/Under) Analyzer
Specialized for game totals betting with advanced O/U analysis
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import UTC, datetime

import requests


class EQ12NFLTotalsAnalyzer:
    def __init__(self):
        self.api_key = "8eb822610b7753d45f76dcac8230a7d1"
        self.bankroll = 1000.0

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("NFL Totals (O/U) Analyzer initialized")

    def get_nfl_totals_data(self) -> dict:
        """Fetch NFL odds focusing on totals (Over/Under)"""
        try:
            url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
            params = {
                "apiKey": self.api_key,
                "regions": "us",
                "markets": "totals",  # Focus only on totals (O/U)
                "oddsFormat": "american",
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            games = response.json()

            self.logger.info(f"Fetched {len(games)} NFL games with totals")
            return {"success": True, "games": games}

        except Exception as e:
            self.logger.error(f"Failed to fetch NFL totals: {e}")
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
                today = datetime.now().date()
                game_date = local_time.date()

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
                elif game_date == today:
                    # Only include today's upcoming games
                    game_info["status"] = "UPCOMING"
                    upcoming_games.append(game_info)
                    self.logger.info(
                        f"UPCOMING: {game['away_team']} @ {game['home_team']} at {local_time.strftime('%I:%M %p')}"
                    )
                else:
                    self.logger.info(
                        f"FUTURE: {game['away_team']} @ {game['home_team']} ({game_date})"
                    )

            except Exception as e:
                self.logger.warning(f"Could not parse game: {e}")

        return {
            "live": live_games,
            "upcoming": upcoming_games,
            "finished": finished_games,
        }

    def extract_totals_opportunities(self, games: list) -> list:
        """Extract Over/Under betting opportunities"""
        totals_ops = []

        for game in games:
            try:
                for bookmaker in game.get("bookmakers", []):
                    for market in bookmaker.get("markets", []):
                        if market["key"] == "totals":
                            for outcome in market["outcomes"]:
                                name = outcome["name"]  # "Over" or "Under"
                                total = outcome["point"]  # Total points line
                                odds = outcome["price"]

                                # Advanced totals analysis
                                totals_analysis = self.analyze_total_value(
                                    total,
                                    odds,
                                    name,
                                    game["home_team"],
                                    game["away_team"],
                                )

                                ev_percent = totals_analysis["expected_value"]

                                if ev_percent > 1:  # Only positive EV
                                    totals_ops.append(
                                        {
                                            "game_id": f"{game['away_team']}_at_{game['home_team']}",
                                            "teams": f"{game['away_team']} @ {game['home_team']}",
                                            "bet_type": name,  # "Over" or "Under"
                                            "total": total,
                                            "odds": odds,
                                            "sportsbook": bookmaker["title"],
                                            "expected_value": ev_percent,
                                            "implied_prob": totals_analysis["implied_prob"],
                                            "model_prob": totals_analysis["model_prob"],
                                            "status": game.get("status", "UNKNOWN"),
                                            "game_time": game.get("game_time_local", "Unknown"),
                                            "elapsed_hours": game.get("elapsed_hours", 0),
                                            "market": "Totals",
                                            "value_grade": self.grade_totals_value(
                                                ev_percent, total
                                            ),
                                            "total_category": self.categorize_total(total),
                                            "pace_factor": totals_analysis["pace_factor"],
                                            "weather_factor": totals_analysis["weather_factor"],
                                        }
                                    )

            except Exception as e:
                self.logger.warning(f"Error processing totals: {e}")

        totals_ops.sort(key=lambda x: x["expected_value"], reverse=True)
        self.logger.info(f"Found {len(totals_ops)} totals opportunities")
        return totals_ops

    def analyze_total_value(
        self, total: float, odds: int, bet_type: str, home_team: str, away_team: str
    ) -> dict:
        """Advanced analysis of total betting value"""

        # Calculate implied probability
        implied_prob = self.implied_probability(odds)

        # Model probability based on multiple factors
        model_prob = 0.5  # Base 50/50

        # Team-specific scoring analysis
        team_factors = self.analyze_team_scoring(home_team, away_team)

        # Total range analysis
        total_factor = self.analyze_total_range(total)

        # Pace and style factors
        pace_factor = self.analyze_pace_factors(home_team, away_team)
        weather_factor = self.analyze_weather_factors()

        # Adjust model probability based on bet type
        if bet_type == "Over":
            # Over adjustments
            model_prob += team_factors["offensive_boost"]
            model_prob += pace_factor["fast_pace_boost"]
            model_prob += total_factor["over_edge"]
            model_prob -= weather_factor["weather_penalty"]
        else:  # Under
            # Under adjustments
            model_prob += team_factors["defensive_boost"]
            model_prob += pace_factor["slow_pace_boost"]
            model_prob += total_factor["under_edge"]
            model_prob += weather_factor["weather_bonus"]

        # Keep probability in reasonable bounds
        model_prob = max(0.1, min(0.9, model_prob))

        # Calculate expected value
        if odds > 0:
            ev = (model_prob * odds - (1 - model_prob) * 100) / 100
        else:
            ev = (model_prob * 100 - (1 - model_prob) * abs(odds)) / abs(odds)

        return {
            "expected_value": ev * 100,
            "implied_prob": implied_prob,
            "model_prob": model_prob,
            "pace_factor": pace_factor,
            "weather_factor": weather_factor,
        }

    def analyze_team_scoring(self, home_team: str, away_team: str) -> dict:
        """Analyze team scoring tendencies"""

        # High-scoring offensive teams
        high_offense = [
            "Buffalo Bills",
            "Miami Dolphins",
            "Dallas Cowboys",
            "Kansas City Chiefs",
            "Philadelphia Eagles",
            "Detroit Lions",
        ]

        # Strong defensive teams (low scoring)
        strong_defense = [
            "Pittsburgh Steelers",
            "Baltimore Ravens",
            "Cleveland Browns",
            "New England Patriots",
            "Denver Broncos",
            "Chicago Bears",
        ]

        offensive_boost = 0
        defensive_boost = 0

        # Check both teams for offensive firepower
        if home_team in high_offense:
            offensive_boost += 0.05
        if away_team in high_offense:
            offensive_boost += 0.05

        # Check for defensive strength
        if home_team in strong_defense:
            defensive_boost += 0.04
        if away_team in strong_defense:
            defensive_boost += 0.04

        return {"offensive_boost": offensive_boost, "defensive_boost": defensive_boost}

    def analyze_total_range(self, total: float) -> dict:
        """Analyze total point range for betting edges"""

        over_edge = 0
        under_edge = 0

        # NFL scoring analysis
        if total < 40:
            # Very low totals - often bet up
            under_edge += 0.03
        elif total > 52:
            # Very high totals - often inflated
            under_edge += 0.02
        elif 44 <= total <= 48:
            # Sweet spot totals - often accurate
            pass  # No adjustment
        else:
            # Mid-range totals slightly favor over
            over_edge += 0.01

        return {"over_edge": over_edge, "under_edge": under_edge}

    def analyze_pace_factors(self, home_team: str, away_team: str) -> dict:
        """Analyze game pace factors"""

        # Fast-paced teams (more plays = more scoring opportunities)
        fast_pace_teams = [
            "Buffalo Bills",
            "Miami Dolphins",
            "Kansas City Chiefs",
            "Philadelphia Eagles",
            "Cincinnati Bengals",
            "Detroit Lions",
        ]

        # Slow-paced teams (fewer plays = lower scoring)
        slow_pace_teams = [
            "Tennessee Titans",
            "Chicago Bears",
            "Pittsburgh Steelers",
            "Baltimore Ravens",
            "Cleveland Browns",
        ]

        fast_pace_boost = 0
        slow_pace_boost = 0

        if home_team in fast_pace_teams:
            fast_pace_boost += 0.02
        if away_team in fast_pace_teams:
            fast_pace_boost += 0.02

        if home_team in slow_pace_teams:
            slow_pace_boost += 0.02
        if away_team in slow_pace_teams:
            slow_pace_boost += 0.02

        return {"fast_pace_boost": fast_pace_boost, "slow_pace_boost": slow_pace_boost}

    def analyze_weather_factors(self) -> dict:
        """Analyze weather impact (simplified for demo)"""
        # In real implementation, would check weather APIs
        # For now, assume neutral conditions

        return {
            "weather_penalty": 0.01,  # Slight penalty for outdoor games
            "weather_bonus": 0.01,  # Slight bonus for under in bad weather
        }

    def categorize_total(self, total: float) -> str:
        """Categorize total into ranges"""
        if total < 40:
            return "VERY LOW"
        if total < 44:
            return "LOW"
        if total <= 48:
            return "AVERAGE"
        if total <= 52:
            return "HIGH"
        return "VERY HIGH"

    def implied_probability(self, odds: int) -> float:
        """Convert American odds to implied probability"""
        if odds > 0:
            return 100 / (odds + 100)
        return abs(odds) / (abs(odds) + 100)

    def grade_totals_value(self, ev: float, total: float) -> str:
        """Grade total betting value"""
        if ev >= 10:
            return "🟢 ELITE"
        if ev >= 6:
            return "🟢 STRONG"
        if ev >= 3:
            return "🟡 SOLID"
        if ev >= 1:
            return "🟠 FAIR"
        return "🔴 AVOID"

    def dedupe_games(self, opportunities: list) -> list:
        """Keep only best O/U pick per game"""
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

    def build_totals_parlays(self, totals_ops: list) -> list:
        """Build specialized totals parlays"""
        parlays = []

        # Dedupe to one pick per game
        totals_deduped = self.dedupe_games(totals_ops)

        # Strategy 1: Live Totals Special
        live_totals = [op for op in totals_ops if op["status"] == "LIVE"]
        live_deduped = self.dedupe_games(live_totals)[:6]

        if len(live_deduped) >= 3:
            parlays.append(
                {
                    "strategy": "Live Totals Special",
                    "description": "In-play Over/Under opportunities",
                    "legs": live_deduped,
                    "stake_pct": 0.05,  # 5% of bankroll
                    "risk_level": "HIGH",
                }
            )

        # Strategy 2: Elite Totals Only
        elite_totals = [op for op in totals_deduped if "ELITE" in op["value_grade"]][:8]

        if len(elite_totals) >= 4:
            parlays.append(
                {
                    "strategy": "Elite Totals Only",
                    "description": "Highest value O/U bets",
                    "legs": elite_totals,
                    "stake_pct": 0.08,  # 8% of bankroll
                    "risk_level": "MEDIUM",
                }
            )

        # Strategy 3: Over/Under Balance
        over_bets = [
            op for op in totals_deduped if op["bet_type"] == "Over" and op["expected_value"] >= 3
        ][:3]
        under_bets = [
            op for op in totals_deduped if op["bet_type"] == "Under" and op["expected_value"] >= 3
        ][:3]
        balanced_legs = over_bets + under_bets

        if len(balanced_legs) >= 4:
            parlays.append(
                {
                    "strategy": "Over/Under Balance",
                    "description": "Mixed Over and Under strategy",
                    "legs": balanced_legs,
                    "stake_pct": 0.06,  # 6% of bankroll
                    "risk_level": "MEDIUM",
                }
            )

        # Strategy 4: Today's Conservative Totals
        today_totals = [op for op in totals_ops if op["status"] == "UPCOMING"]
        today_deduped = self.dedupe_games(today_totals)
        conservative = [op for op in today_deduped if op["expected_value"] >= 5][:5]

        if len(conservative) >= 3:
            parlays.append(
                {
                    "strategy": "Today's Conservative Totals",
                    "description": "High-confidence upcoming totals",
                    "legs": conservative,
                    "stake_pct": 0.1,  # 10% of bankroll
                    "risk_level": "LOW",
                }
            )

        return parlays

    def calculate_parlay_odds(self, legs: list) -> tuple:
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

    def format_totals_output(self, parlays: list, totals_ops: list, game_status: dict) -> str:
        """Format comprehensive totals output"""

        output = f"""
🏈 NFL TOTALS (OVER/UNDER) ANALYZER 🏈
⏰ Generated: {datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")}
💰 Bankroll: ${self.bankroll:,.2f}
🎯 Focus: GAME TOTALS ONLY
============================================================

📊 GAME STATUS SUMMARY:
🔴 Live Games: {len(game_status["live"])}
🕐 Upcoming Games: {len(game_status["upcoming"])}
⚫ Finished Games: {len(game_status["finished"])}

💰 TOTALS OPPORTUNITIES:
🎲 Total O/U Picks: {len(totals_ops)}
🎯 Parlay Strategies: {len(parlays)}

============================================================

"""

        for i, parlay in enumerate(parlays, 1):
            odds, multiplier = self.calculate_parlay_odds(parlay["legs"])
            stake = self.bankroll * parlay["stake_pct"]
            payout = stake * multiplier

            output += f"""🎯 TOTALS PARLAY #{i}: {parlay["strategy"]}
📖 {parlay["description"]}
📊 Legs: {len(parlay["legs"])} | Odds: {odds:+.0f} | Stake: ${stake:.0f} | Risk: {parlay["risk_level"]}
💸 Payout: ${payout:,.2f} | Net: +${payout - stake:,.2f}
----------------------------------------
"""

            for j, leg in enumerate(parlay["legs"], 1):
                status_icon = (
                    "🔴"
                    if leg["status"] == "LIVE"
                    else "🕐" if leg["status"] == "UPCOMING" else "⚫"
                )

                output += f"""   {j}. {leg["bet_type"]} {leg["total"]} ({leg["teams"]})
      📈 {leg["odds"]:+} | EV: {leg["expected_value"]:+.1f}% | {leg["value_grade"]}
      🏷️ {leg["total_category"]} TOTAL | {status_icon} {leg["status"]}
      🕐 {leg["game_time"]} | 📱 {leg["sportsbook"]}
"""

            output += "\n"

        # Live games detail
        if game_status["live"]:
            output += "\n🔴 LIVE TOTALS ANALYSIS:\n"
            for game in game_status["live"]:
                output += f"   {game['away_team']} @ {game['home_team']} - {game['elapsed_hours']:.1f}h elapsed\n"
            output += "\n"

        # Totals breakdown
        over_count = len([op for op in totals_ops if op["bet_type"] == "Over"])
        under_count = len([op for op in totals_ops if op["bet_type"] == "Under"])

        output += f"""📊 TOTALS BREAKDOWN:
📈 Over Bets: {over_count}
📉 Under Bets: {under_count}
🎯 Elite Opportunities: {len([op for op in totals_ops if "ELITE" in op["value_grade"]])}

🎲 TOTAL RANGES:
• VERY LOW (<40): {len([op for op in totals_ops if op["total_category"] == "VERY LOW"])} games
• LOW (40-44): {len([op for op in totals_ops if op["total_category"] == "LOW"])} games
• AVERAGE (44-48): {len([op for op in totals_ops if op["total_category"] == "AVERAGE"])} games
• HIGH (48-52): {len([op for op in totals_ops if op["total_category"] == "HIGH"])} games
• VERY HIGH (52+): {len([op for op in totals_ops if op["total_category"] == "VERY HIGH"])} games

📊 VALUE LEGEND:
🟢 ELITE = 10%+ EV  |  🟢 STRONG = 6%+ EV  |  🟡 SOLID = 3%+ EV
🟠 FAIR = 1%+ EV  |  🔴 AVOID = <1% EV

🚀 Ready to hammer these totals? LFG! 🚀
"""

        return output

    async def run_totals_analysis(self) -> dict:
        """Main totals analysis execution"""
        try:
            self.logger.info("Starting NFL Totals (O/U) Analysis")

            # Fetch totals data
            data = self.get_nfl_totals_data()
            if not data["success"]:
                return {"success": False, "message": data["error"]}

            # Analyze game status
            game_status = self.analyze_game_status(data["games"])

            # Extract totals opportunities
            all_games = game_status["live"] + game_status["upcoming"]
            totals_ops = self.extract_totals_opportunities(all_games)

            # Build totals parlays
            parlays = self.build_totals_parlays(totals_ops)

            # Generate output
            output = self.format_totals_output(parlays, totals_ops, game_status)
            print(output)

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results = {
                "timestamp": datetime.now().isoformat(),
                "bankroll": self.bankroll,
                "game_status": game_status,
                "totals_opportunities": totals_ops,
                "parlays": parlays,
                "summary": {
                    "total_opportunities": len(totals_ops),
                    "total_parlays": len(parlays),
                    "live_games": len(game_status["live"]),
                    "upcoming_games": len(game_status["upcoming"]),
                    "over_bets": len([op for op in totals_ops if op["bet_type"] == "Over"]),
                    "under_bets": len([op for op in totals_ops if op["bet_type"] == "Under"]),
                },
            }

            filename = f"C:/EQ12/logs/nfl_totals_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(results, f, indent=2, default=str)

            return {
                "success": True,
                "message": f"Generated {len(parlays)} totals parlay strategies",
                "results_file": filename,
            }

        except Exception as e:
            self.logger.error(f"Totals analysis failed: {e}")
            return {"success": False, "message": str(e)}


def main():
    parser = argparse.ArgumentParser(description="NFL Totals (O/U) Analyzer")
    parser.add_argument("--bankroll", type=float, default=1000.0, help="Bankroll amount")

    args = parser.parse_args()

    analyzer = EQ12NFLTotalsAnalyzer()
    analyzer.bankroll = args.bankroll

    try:
        result = asyncio.run(analyzer.run_totals_analysis())
        if result["success"]:
            print(f"\n✅ {result['message']}")
            if "results_file" in result:
                print(f"📁 Results: {result['results_file']}")
        else:
            print(f"\n❌ {result['message']}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Totals analysis stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Totals analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
