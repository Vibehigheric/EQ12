#!/usr/bin/env python3
"""
EQ12 NFL Spread Parlay Optimizer - Sunday Edition
Specialized for spread betting with advanced line analysis
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import UTC, datetime

import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()


class EQ12SpreadParlayOptimizer:
    def __init__(self):
        self.odds_api_key = os.getenv("ODDS_API_KEY")
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.bankroll = 1000.0

        # Setup logging
        os.makedirs("C:/EQ12/logs", exist_ok=True)
        log_file = f"C:/EQ12/logs/nfl_spreads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("🏈 EQ12 Spread Parlay Optimizer initialized")

    def get_nfl_odds(self) -> list[dict]:
        """Fetch current NFL odds focusing on spreads"""
        if not self.odds_api_key:
            raise ValueError("ODDS_API_KEY not found")

        url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
        params = {
            "apiKey": self.odds_api_key,
            "regions": "us",
            "markets": "spreads",  # Focus only on spreads
            "oddsFormat": "american",
            "dateFormat": "iso",
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            games = response.json()
            self.logger.info(f"📡 Fetched {len(games)} NFL games with spreads")
            return games
        except Exception as e:
            self.logger.error(f"❌ Failed to fetch NFL odds: {e}")
            return []

    def filter_upcoming_games(self, games: list[dict]) -> list[dict]:
        """Filter games that haven't started yet AND are from today only"""
        filtered_games = []
        current_time = datetime.now(UTC)
        today = datetime.now().date()

        for game in games:
            try:
                game_time = datetime.fromisoformat(game["commence_time"].replace("Z", "+00:00"))
                local_game_time = game_time.astimezone()
                game_date = local_game_time.date()

                # Only include games from today that haven't started yet
                if game_time > current_time and game_date == today:
                    filtered_games.append(game)
                    self.logger.info(
                        f"✅ {game['away_team']} @ {game['home_team']} at {local_game_time.strftime('%I:%M %p')}"
                    )
                elif game_date != today:
                    self.logger.info(
                        f"📅 Skipped: {game['away_team']} @ {game['home_team']} (future date: {game_date})"
                    )
                else:
                    self.logger.info(
                        f"⏰ Skipped: {game['away_team']} @ {game['home_team']} (started)"
                    )
            except Exception as e:
                self.logger.warning(f"⚠️ Could not parse game time: {e}")

        self.logger.info(f"🎯 Found {len(filtered_games)} TODAY's upcoming games")
        return filtered_games

    def analyze_spread_value(self, spread: float, odds: int) -> dict:
        """Advanced spread analysis for EQ12 system"""
        # Key numbers in NFL spreads (most common margins of victory)
        key_numbers = [3, 7, 10, 14, 17, 21]

        # Calculate value metrics
        implied_prob = self.implied_probability(odds)

        # Spread analysis factors
        is_key_number = abs(spread) in key_numbers
        is_field_goal = abs(spread) == 3
        is_touchdown = abs(spread) == 7
        is_hook = abs(spread) % 1 == 0.5  # Half-point spreads

        # EQ12 edge calculation
        base_edge = 0.02  # Base 2% edge

        # Bonus edges for favorable situations
        if is_hook:
            base_edge += 0.03  # Hook spreads avoid pushes
        if is_key_number and not is_hook:
            base_edge -= 0.01  # Key numbers are tougher
        if abs(spread) <= 3:
            base_edge += 0.02  # Close games have more variance
        if abs(spread) >= 14:
            base_edge += 0.01  # Blowout potential

        model_prob = min(0.85, implied_prob + base_edge)
        ev = ((model_prob - implied_prob) / implied_prob) * 100

        return {
            "model_prob": model_prob,
            "expected_value": round(ev, 2),
            "is_key_number": is_key_number,
            "is_hook": is_hook,
            "is_field_goal": is_field_goal,
            "is_touchdown": is_touchdown,
            "value_grade": self.grade_spread_value(ev, spread, is_hook),
        }

    def grade_spread_value(self, ev: float, spread: float, is_hook: bool) -> str:
        """Grade spread value for display"""
        if ev >= 8 and is_hook:
            return "🟢 ELITE"
        if ev >= 6 and abs(spread) <= 3:
            return "🟢 STRONG"
        if ev >= 4:
            return "🟡 SOLID"
        if ev >= 2:
            return "🟠 FAIR"
        return "🔴 AVOID"

    def implied_probability(self, odds: int) -> float:
        """Convert American odds to implied probability"""
        if odds > 0:
            return 100 / (odds + 100)
        return abs(odds) / (abs(odds) + 100)

    def extract_spread_legs(self, games: list[dict]) -> list[dict]:
        """Extract all spread betting opportunities"""
        spread_legs = []

        for game in games:
            home_team = game["home_team"]
            away_team = game["away_team"]
            commence_time = game["commence_time"]

            for bookmaker in game.get("bookmakers", []):
                sportsbook = bookmaker["title"]

                for market in bookmaker.get("markets", []):
                    if market["key"] == "spreads":
                        for outcome in market["outcomes"]:
                            team = outcome["name"]
                            odds = outcome["price"]
                            spread = outcome.get("point", 0)

                            # Analyze this spread
                            analysis = self.analyze_spread_value(spread, odds)

                            # Only include positive EV spreads
                            if analysis["expected_value"] >= 2.0:
                                spread_legs.append(
                                    {
                                        "game_id": f"{away_team}_at_{home_team}",
                                        "team": team,
                                        "spread": spread,
                                        "odds": odds,
                                        "sportsbook": sportsbook,
                                        "commence_time": commence_time,
                                        "selection": f"{team} {spread:+}",
                                        **analysis,
                                    }
                                )

        # Sort by EV descending
        spread_legs.sort(key=lambda x: x["expected_value"], reverse=True)
        self.logger.info(f"🎲 Found {len(spread_legs)} valuable spread opportunities")
        return spread_legs

    def dedupe_games_in_parlay(self, legs: list[dict]) -> list[dict]:
        """Remove duplicate games, keeping only the best pick per game"""
        seen_games = {}
        deduped_legs = []

        for leg in legs:
            game_id = leg["game_id"]
            if game_id not in seen_games:
                seen_games[game_id] = leg
                deduped_legs.append(leg)
            elif leg["expected_value"] > seen_games[game_id]["expected_value"]:
                # Replace with higher EV pick from same game
                deduped_legs.remove(seen_games[game_id])
                seen_games[game_id] = leg
                deduped_legs.append(leg)

        return deduped_legs

    def build_spread_parlays(self, legs: list[dict], max_legs: int = 15) -> list[dict]:
        """Build spread-specific parlay strategies"""
        parlays = []

        if not legs:
            return parlays

        # Strategy 1: Elite Hooks (Hook spreads only - highest value)
        hook_legs = [leg for leg in legs if leg["is_hook"] and leg["expected_value"] >= 6]
        hook_legs = self.dedupe_games_in_parlay(hook_legs)[:10]
        if len(hook_legs) >= 4:
            odds, multiplier = self.calculate_parlay_odds(hook_legs)
            stake = min(75, self.bankroll * 0.075)
            payout = stake * multiplier

            parlays.append(
                {
                    "strategy": "Elite Hooks Only",
                    "description": "Half-point spreads avoid pushes - premium value",
                    "legs": hook_legs,
                    "leg_count": len(hook_legs),
                    "american_odds": round(odds),
                    "multiplier": round(multiplier, 2),
                    "recommended_stake": round(stake, 2),
                    "potential_payout": round(payout, 2),
                    "net_profit": round(payout - stake, 2),
                }
            )

        # Strategy 2: Key Number Contrarian (Bet against key numbers)
        contrarian_legs = [
            leg for leg in legs if not leg["is_key_number"] and leg["expected_value"] >= 4
        ]
        contrarian_legs = self.dedupe_games_in_parlay(contrarian_legs)[:8]
        if len(contrarian_legs) >= 5:
            odds, multiplier = self.calculate_parlay_odds(contrarian_legs)
            stake = min(50, self.bankroll * 0.05)
            payout = stake * multiplier

            parlays.append(
                {
                    "strategy": "Key Number Contrarian",
                    "description": "Avoiding trap key numbers (3,7,10)",
                    "legs": contrarian_legs,
                    "leg_count": len(contrarian_legs),
                    "american_odds": round(odds),
                    "multiplier": round(multiplier, 2),
                    "recommended_stake": round(stake, 2),
                    "potential_payout": round(payout, 2),
                    "net_profit": round(payout - stake, 2),
                }
            )

        # Strategy 3: Close Game Special (Spreads 3 or less)
        close_legs = [leg for leg in legs if abs(leg["spread"]) <= 3 and leg["expected_value"] >= 3]
        close_legs = self.dedupe_games_in_parlay(close_legs)[:12]
        if len(close_legs) >= 6:
            odds, multiplier = self.calculate_parlay_odds(close_legs)
            stake = min(40, self.bankroll * 0.04)
            payout = stake * multiplier

            parlays.append(
                {
                    "strategy": "Close Game Chaos",
                    "description": "Tight spreads (≤3 pts) - maximum variance",
                    "legs": close_legs,
                    "leg_count": len(close_legs),
                    "american_odds": round(odds),
                    "multiplier": round(multiplier, 2),
                    "recommended_stake": round(stake, 2),
                    "potential_payout": round(payout, 2),
                    "net_profit": round(payout - stake, 2),
                }
            )

        # Strategy 4: Maximum Spread Value (Top EV regardless of type)
        max_value_legs = self.dedupe_games_in_parlay(legs)[:max_legs]
        if len(max_value_legs) >= 5:
            odds, multiplier = self.calculate_parlay_odds(max_value_legs)
            stake = min(25, self.bankroll * 0.025)
            payout = stake * multiplier

            parlays.append(
                {
                    "strategy": "Maximum Spread Value",
                    "description": "Highest EV spreads across all games",
                    "legs": max_value_legs,
                    "leg_count": len(max_value_legs),
                    "american_odds": round(odds),
                    "multiplier": round(multiplier, 2),
                    "recommended_stake": round(stake, 2),
                    "potential_payout": round(payout, 2),
                    "net_profit": round(payout - stake, 2),
                }
            )

        return sorted(parlays, key=lambda x: x["net_profit"], reverse=True)

    def calculate_parlay_odds(self, legs: list[dict]) -> tuple[float, float]:
        """Calculate combined parlay odds"""
        total_multiplier = 1.0

        for leg in legs:
            odds = leg["odds"]
            decimal_odds = (odds / 100 + 1) if odds > 0 else (100 / abs(odds) + 1)
            total_multiplier *= decimal_odds

        # Convert to American odds
        american_odds = (
            (total_multiplier - 1) * 100
            if total_multiplier >= 2.0
            else -100 / (total_multiplier - 1)
        )
        return american_odds, total_multiplier

    def format_spread_output(self, parlays: list[dict]) -> str:
        """Format spread parlays for display"""
        output = "🏈 EQ12 NFL SPREAD PARLAY OPTIMIZER 🏈\n"
        output += f"⏰ Generated: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}\n"
        output += f"💰 Bankroll: ${self.bankroll:,.2f}\n"
        output += "🎯 Focus: SPREAD BETTING ONLY\n"
        output += "=" * 60 + "\n\n"

        if not parlays:
            output += "❌ No viable spread parlays found\n"
            return output

        for i, parlay in enumerate(parlays, 1):
            output += f"🎯 SPREAD PARLAY #{i}: {parlay['strategy']}\n"
            output += f"📖 {parlay['description']}\n"
            output += f"📊 Legs: {parlay['leg_count']} | Odds: {parlay['american_odds']:+} | Stake: ${parlay['recommended_stake']}\n"
            output += f"💸 Payout: ${parlay['potential_payout']:,.2f} | Net: +${parlay['net_profit']:,.2f}\n"
            output += "-" * 40 + "\n"

            for j, leg in enumerate(parlay["legs"], 1):
                spread_display = f"{leg['spread']:+}" if leg["spread"] != 0 else "PK"
                output += f"  {j:2d}. {leg['team']} {spread_display}\n"
                output += f"      📈 {leg['odds']:+} | EV: {leg['expected_value']:+.1f}% | {leg['value_grade']}\n"

                # Add spread analysis
                analysis_notes = []
                if leg["is_hook"]:
                    analysis_notes.append("HOOK")
                if leg["is_key_number"]:
                    analysis_notes.append("KEY#")
                if leg["is_field_goal"]:
                    analysis_notes.append("FG")
                if leg["is_touchdown"]:
                    analysis_notes.append("TD")

                if analysis_notes:
                    output += f"      🏷️  {' | '.join(analysis_notes)}\n"

                output += f"      🏟️  {leg['game_id'].replace('_', ' ')}\n"

            output += "\n"

        output += "📊 SPREAD LEGEND:\n"
        output += "🟢 ELITE = 8%+ EV + Hook  |  🟢 STRONG = 6%+ EV + Close Game\n"
        output += "🟡 SOLID = 4%+ EV  |  🟠 FAIR = 2%+ EV  |  🔴 AVOID = <2% EV\n"
        output += "HOOK = Half-point spread  |  KEY# = Key number (3,7,10,14,17,21)\n\n"
        output += "🚀 Ready to hammer these spreads? LFG! 🚀\n"
        return output

    def save_results(self, parlays: list[dict], legs: list[dict]) -> str:
        """Save spread results"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "strategy_type": "NFL Spread Parlays",
            "bankroll": self.bankroll,
            "total_spreads_analyzed": len(legs),
            "parlays": parlays,
            "all_spread_legs": legs,
        }

        filename = f"C:/EQ12/logs/nfl_spreads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"💾 Spread results saved to {filename}")
        return filename

    async def run_spread_optimizer(self) -> dict:
        """Main spread optimization workflow"""
        self.logger.info("🚀 Starting EQ12 Spread Parlay Analysis")

        # Get games with spreads
        games = self.get_nfl_odds()
        if not games:
            return {"success": False, "message": "No games available"}

        # Filter to upcoming games only
        upcoming_games = self.filter_upcoming_games(games)
        if not upcoming_games:
            return {"success": False, "message": "No upcoming games"}

        # Extract spread opportunities
        spread_legs = self.extract_spread_legs(upcoming_games)
        if not spread_legs:
            return {"success": False, "message": "No valuable spreads found"}

        # Build spread parlays
        parlays = self.build_spread_parlays(spread_legs)
        if not parlays:
            return {"success": False, "message": "No viable spread parlays"}

        # Format and display
        formatted_output = self.format_spread_output(parlays)
        print(formatted_output)

        # Save results
        results_file = self.save_results(parlays, spread_legs)

        return {
            "success": True,
            "parlays": parlays,
            "total_spreads": len(spread_legs),
            "results_file": results_file,
            "message": f"Generated {len(parlays)} spread parlay strategies",
        }


def main():
    parser = argparse.ArgumentParser(description="EQ12 NFL Spread Parlay Optimizer")
    parser.add_argument("--bankroll", type=float, default=1000.0, help="Bankroll amount")
    parser.add_argument("--max-legs", type=int, default=15, help="Maximum legs per parlay")
    parser.add_argument("--debug", action="store_true", help="Debug mode - show all game details")

    args = parser.parse_args()

    optimizer = EQ12SpreadParlayOptimizer()
    optimizer.bankroll = args.bankroll

    if args.debug:
        # Debug mode - show detailed game analysis
        games = optimizer.get_nfl_odds()
        current_time = datetime.now(UTC)
        print(f"\n🕐 Current time: {current_time}")
        print(f"📅 Current date: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"\n📊 Total games from API: {len(games)}")

        for game in games:
            game_time = datetime.fromisoformat(game["commence_time"].replace("Z", "+00:00"))
            local_time = game_time.astimezone()
            status = "🔮 FUTURE" if game_time > current_time else "⏰ PAST/LIVE"

            teams = f"{game['away_team']} @ {game['home_team']}"
            time_str = local_time.strftime("%m/%d %I:%M %p")
            print(f"{status}: {teams} - {time_str}")

        upcoming = optimizer.filter_upcoming_games(games)
        print(f"\n✅ Filtered to {len(upcoming)} upcoming games")
        return

    try:
        result = asyncio.run(optimizer.run_spread_optimizer())
        if result["success"]:
            print(f"\n✅ {result['message']}")
            print(f"📁 Results: {result['results_file']}")
        else:
            print(f"\n❌ {result['message']}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Spread optimization stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Spread optimization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
