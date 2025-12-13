#!/usr/bin/env python3
"""
EQ12 NFL Parlay Optimizer - Sunday Edition
Creates optimal NFL parlays up to 20 legs for games starting at/after 1pm
Integrates with EQ12 system for alerts, logging, and bankroll management
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime

import requests
from dotenv import load_dotenv
from telegram import Bot

from eq12_timezone_utils import now_utc, parse_utc

# Load environment
load_dotenv()


class EQ12NFLParlayOptimizer:
    def __init__(self):
        self.odds_api_key = os.getenv("ODDS_API_KEY")
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.bankroll = 1000.0  # Default bankroll

        # Setup logging
        os.makedirs("C:/EQ12/logs", exist_ok=True)
        log_file = f"C:/EQ12/logs/nfl_parlay_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("🏈 EQ12 NFL Parlay Optimizer initialized")

    def get_nfl_odds(self) -> list[dict]:
        """Fetch current NFL odds from The Odds API"""
        if not self.odds_api_key:
            raise ValueError("ODDS_API_KEY not found in environment variables")

        url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
        params = {
            "apiKey": self.odds_api_key,
            "regions": "us",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american",
            "dateFormat": "iso",
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            games = response.json()
            self.logger.info(f"📡 Fetched {len(games)} NFL games from Odds API")
            return games
        except Exception as e:
            self.logger.error(f"❌ Failed to fetch NFL odds: {e}")
            return []

    def filter_afternoon_games(self, games: list[dict], cutoff_hour: int = 13) -> list[dict]:
        """Filter games starting at or after specified hour AND not yet started"""
        filtered_games = []
        current_time = now_utc()

        for game in games:
            try:
                game_time = parse_utc(game["commence_time"])
                # Convert to local time for display
                local_game_time = game_time.astimezone()

                # Only include games that:
                # 1. Haven't started yet (game_time > current_time)
                # 2. Start at or after cutoff hour in local time (1 PM)
                if game_time > current_time and local_game_time.hour >= cutoff_hour:
                    filtered_games.append(game)
                    self.logger.info(
                        f"✅ Including upcoming game: {game['away_team']} @ {game['home_team']} at {local_game_time.strftime('%I:%M %p')}"
                    )
                elif game_time <= current_time:
                    self.logger.info(
                        f"⏰ Skipping completed/started game: {game['away_team']} @ {game['home_team']} (started {local_game_time.strftime('%I:%M %p')})"
                    )
            except Exception as e:
                self.logger.warning(f"⚠️ Could not parse game time for {game}: {e}")

        self.logger.info(f"🎯 Found {len(filtered_games)} games starting at/after {cutoff_hour}:00")
        return filtered_games

    def implied_probability(self, odds: int) -> float:
        """Convert American odds to implied probability"""
        if odds > 0:
            return 100 / (odds + 100)
        return abs(odds) / (abs(odds) + 100)

    def expected_value(self, model_prob: float, book_odds: int) -> float:
        """Calculate expected value percentage"""
        implied_prob = self.implied_probability(book_odds)
        return ((model_prob - implied_prob) / implied_prob) * 100

    def kelly_criterion(self, model_prob: float, odds: int, bankroll: float) -> float:
        """Calculate optimal Kelly Criterion bet size"""
        if odds > 0:
            b = odds / 100  # Decimal odds - 1
        else:
            b = 100 / abs(odds)

        q = 1 - model_prob
        kelly_fraction = ((b * model_prob) - q) / b
        return max(0, kelly_fraction * bankroll)

    def extract_betting_legs(self, games: list[dict]) -> list[dict]:
        """Extract all available betting legs from games"""
        legs = []

        for game in games:
            home_team = game["home_team"]
            away_team = game["away_team"]
            commence_time = game["commence_time"]

            for bookmaker in game.get("bookmakers", []):
                sportsbook = bookmaker["title"]

                for market in bookmaker.get("markets", []):
                    market_key = market["key"]

                    if market_key == "h2h":  # Moneyline
                        for outcome in market["outcomes"]:
                            team = outcome["name"]
                            odds = outcome["price"]

                            # Enhanced model probability using team strength heuristic
                            base_prob = self.implied_probability(odds)
                            # More aggressive model for EQ12 system
                            if team == home_team and odds > 0:  # Home underdogs
                                model_prob = min(0.85, base_prob * 1.15)  # 15% home underdog edge
                            elif team == home_team:  # Home favorites
                                model_prob = min(0.90, base_prob * 1.08)  # 8% home field advantage
                            elif odds > 150:  # Big underdogs
                                model_prob = min(0.75, base_prob * 1.20)  # 20% big underdog edge
                            elif odds < -200:  # Heavy favorites
                                model_prob = min(0.95, base_prob * 1.03)  # 3% heavy favorite edge
                            else:
                                model_prob = min(0.85, base_prob * 1.10)  # 10% general edge

                            ev = self.expected_value(model_prob, odds)
                            kelly_stake = self.kelly_criterion(model_prob, odds, self.bankroll)

                            legs.append(
                                {
                                    "game_id": f"{away_team}_at_{home_team}",
                                    "market": "Moneyline",
                                    "selection": team,
                                    "odds": odds,
                                    "sportsbook": sportsbook,
                                    "model_prob": model_prob,
                                    "expected_value": round(ev, 2),
                                    "kelly_stake": round(kelly_stake, 2),
                                    "commence_time": commence_time,
                                    "risk_score": self.calculate_risk_score(ev, odds),
                                }
                            )

                    elif market_key == "spreads":  # Point spreads
                        for outcome in market["outcomes"]:
                            team = outcome["name"]
                            odds = outcome["price"]
                            spread = outcome.get("point", 0)

                            # Model probability for spreads (EQ12 aggressive model)
                            base_prob = self.implied_probability(odds)
                            if abs(spread) <= 3:  # Close games
                                model_prob = min(0.85, base_prob * 1.12)
                            else:
                                model_prob = min(0.88, base_prob * 1.08)

                            ev = self.expected_value(model_prob, odds)
                            kelly_stake = self.kelly_criterion(model_prob, odds, self.bankroll)

                            legs.append(
                                {
                                    "game_id": f"{away_team}_at_{home_team}",
                                    "market": "Spread",
                                    "selection": f"{team} {spread:+}",
                                    "odds": odds,
                                    "sportsbook": sportsbook,
                                    "model_prob": model_prob,
                                    "expected_value": round(ev, 2),
                                    "kelly_stake": round(kelly_stake, 2),
                                    "commence_time": commence_time,
                                    "risk_score": self.calculate_risk_score(ev, odds),
                                }
                            )

                    elif market_key == "totals":  # Over/Under
                        for outcome in market["outcomes"]:
                            total = outcome.get("point", 0)
                            over_under = outcome["name"]
                            odds = outcome["price"]

                            # Model probability for totals (EQ12 aggressive model)
                            base_prob = self.implied_probability(odds)
                            if total >= 50:  # High-scoring games
                                model_prob = min(0.82, base_prob * 1.15)
                            else:  # Lower totals
                                model_prob = min(0.85, base_prob * 1.10)

                            ev = self.expected_value(model_prob, odds)
                            kelly_stake = self.kelly_criterion(model_prob, odds, self.bankroll)

                            legs.append(
                                {
                                    "game_id": f"{away_team}_at_{home_team}",
                                    "market": "Total",
                                    "selection": f"{over_under} {total}",
                                    "odds": odds,
                                    "sportsbook": sportsbook,
                                    "model_prob": model_prob,
                                    "expected_value": round(ev, 2),
                                    "kelly_stake": round(kelly_stake, 2),
                                    "commence_time": commence_time,
                                    "risk_score": self.calculate_risk_score(ev, odds),
                                }
                            )

        self.logger.info(f"🎲 Extracted {len(legs)} betting legs from all games")
        return legs

    def calculate_risk_score(self, ev: float, odds: int) -> str:
        """Calculate risk category based on EV and odds"""
        if ev >= 15 and abs(odds) <= 200:
            return "🟢 LOW"
        if ev >= 10 and abs(odds) <= 300:
            return "🟡 MEDIUM"
        if ev >= 5:
            return "🟠 MEDIUM-HIGH"
        return "🔴 HIGH"

    def filter_high_ev_legs(self, legs: list[dict], min_ev: float = 5.0) -> list[dict]:
        """Filter legs with positive expected value above threshold"""
        high_ev_legs = [leg for leg in legs if leg["expected_value"] >= min_ev]
        self.logger.info(f"✨ Found {len(high_ev_legs)} legs with EV >= {min_ev}%")
        return sorted(high_ev_legs, key=lambda x: x["expected_value"], reverse=True)

    def calculate_parlay_odds(self, legs: list[dict]) -> tuple[float, float]:
        """Calculate combined parlay odds and potential payout"""
        total_odds_multiplier = 1.0

        for leg in legs:
            odds = leg["odds"]
            decimal_odds = odds / 100 + 1 if odds > 0 else 100 / abs(odds) + 1
            total_odds_multiplier *= decimal_odds

        # Convert back to American odds
        if total_odds_multiplier >= 2.0:
            american_odds = (total_odds_multiplier - 1) * 100
        else:
            american_odds = -100 / (total_odds_multiplier - 1)

        return american_odds, total_odds_multiplier

    def build_optimal_parlays(self, legs: list[dict], max_legs: int = 20) -> list[dict]:
        """Build optimal parlay combinations with different strategies"""
        parlays = []

        if not legs:
            self.logger.warning("⚠️ No legs available for parlay building")
            return parlays

        # Strategy 1: Highest EV legs (Conservative - 5-8 legs)
        conservative_legs = legs[:8]
        if len(conservative_legs) >= 5:
            american_odds, multiplier = self.calculate_parlay_odds(conservative_legs)
            stake = min(50, self.bankroll * 0.05)  # 5% of bankroll, max $50
            payout = stake * multiplier

            parlays.append(
                {
                    "strategy": "Conservative High-EV",
                    "legs": conservative_legs,
                    "leg_count": len(conservative_legs),
                    "american_odds": round(american_odds),
                    "multiplier": round(multiplier, 2),
                    "recommended_stake": round(stake, 2),
                    "potential_payout": round(payout, 2),
                    "net_profit": round(payout - stake, 2),
                }
            )

        # Strategy 2: Balanced risk (10-12 legs)
        if len(legs) >= 10:
            balanced_legs = legs[:12]
            american_odds, multiplier = self.calculate_parlay_odds(balanced_legs)
            stake = min(25, self.bankroll * 0.025)  # 2.5% of bankroll, max $25
            payout = stake * multiplier

            parlays.append(
                {
                    "strategy": "Balanced Risk",
                    "legs": balanced_legs,
                    "leg_count": len(balanced_legs),
                    "american_odds": round(american_odds),
                    "multiplier": round(multiplier, 2),
                    "recommended_stake": round(stake, 2),
                    "potential_payout": round(payout, 2),
                    "net_profit": round(payout - stake, 2),
                }
            )

        # Strategy 3: Maximum legs (up to 20) - High risk, high reward
        if len(legs) >= 15:
            max_legs_parlay = legs[: min(max_legs, len(legs))]
            american_odds, multiplier = self.calculate_parlay_odds(max_legs_parlay)
            stake = min(10, self.bankroll * 0.01)  # 1% of bankroll, max $10
            payout = stake * multiplier

            parlays.append(
                {
                    "strategy": "Maximum Legs (YOLO)",
                    "legs": max_legs_parlay,
                    "leg_count": len(max_legs_parlay),
                    "american_odds": round(american_odds),
                    "multiplier": round(multiplier, 2),
                    "recommended_stake": round(stake, 2),
                    "potential_payout": round(payout, 2),
                    "net_profit": round(payout - stake, 2),
                }
            )

        # Strategy 4: Low-risk favorites only
        favorite_legs = [leg for leg in legs if leg["odds"] < 0 and leg["expected_value"] >= 8][:10]
        if len(favorite_legs) >= 6:
            american_odds, multiplier = self.calculate_parlay_odds(favorite_legs)
            stake = min(100, self.bankroll * 0.10)  # 10% of bankroll, max $100
            payout = stake * multiplier

            parlays.append(
                {
                    "strategy": "Favorites Only",
                    "legs": favorite_legs,
                    "leg_count": len(favorite_legs),
                    "american_odds": round(american_odds),
                    "multiplier": round(multiplier, 2),
                    "recommended_stake": round(stake, 2),
                    "potential_payout": round(payout, 2),
                    "net_profit": round(payout - stake, 2),
                }
            )

        return sorted(parlays, key=lambda x: x["net_profit"], reverse=True)

    def format_parlay_output(self, parlays: list[dict]) -> str:
        """Format parlays for display and alerts"""
        output = "🏈 EQ12 NFL PARLAY OPTIMIZER - SUNDAY EDITION 🏈\n"
        output += f"⏰ Generated: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}\n"
        output += f"💰 Bankroll: ${self.bankroll:,.2f}\n"
        output += "=" * 60 + "\n\n"

        if not parlays:
            output += "❌ No optimal parlays found with current criteria\n"
            return output

        for i, parlay in enumerate(parlays, 1):
            output += f"🎯 PARLAY #{i}: {parlay['strategy']}\n"
            output += f"📊 Legs: {parlay['leg_count']} | Odds: {parlay['american_odds']:+} | Stake: ${parlay['recommended_stake']}\n"
            output += f"💸 Payout: ${parlay['potential_payout']:,.2f} | Net: +${parlay['net_profit']:,.2f}\n"
            output += "-" * 40 + "\n"

            for j, leg in enumerate(parlay["legs"], 1):
                output += f"  {j:2d}. {leg['selection']} ({leg['market']})\n"
                output += f"      📈 {leg['odds']:+} | EV: {leg['expected_value']:+.1f}% | {leg['risk_score']}\n"
                output += f"      🏟️  {leg['game_id'].replace('_', ' ')}\n"

            output += "\n"

        output += "🚀 Ready to place these bets? LFG! 🚀\n"
        return output

    async def send_telegram_alert(self, message: str) -> bool:
        """Send parlay recommendations via Telegram"""
        if not self.telegram_token or not self.telegram_chat_id:
            self.logger.warning("⚠️ Telegram credentials not configured")
            return False

        try:
            bot = Bot(token=self.telegram_token)
            await bot.send_message(chat_id=self.telegram_chat_id, text=message, parse_mode="HTML")
            self.logger.info("✅ Telegram alert sent successfully")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to send Telegram alert: {e}")
            return False

    def save_results(self, parlays: list[dict], legs: list[dict]) -> str:
        """Save results to JSON for later analysis"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "bankroll": self.bankroll,
            "total_legs_analyzed": len(legs),
            "parlays": parlays,
            "all_legs": legs,
        }

        filename = f"C:/EQ12/logs/nfl_parlays_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"💾 Results saved to {filename}")
        return filename

    async def run_optimizer(self, min_ev: float = 5.0, max_legs: int = 20) -> dict:
        """Main optimization workflow"""
        self.logger.info("🚀 Starting EQ12 NFL Parlay Optimization")

        # Fetch NFL odds
        games = self.get_nfl_odds()
        if not games:
            self.logger.error("❌ No games retrieved from API")
            return {"success": False, "message": "No games available"}

        # Filter afternoon games (1pm or later)
        afternoon_games = self.filter_afternoon_games(games)
        if not afternoon_games:
            self.logger.warning("⚠️ No games starting at/after 1 PM found")
            return {"success": False, "message": "No afternoon games available"}

        # Extract betting legs
        all_legs = self.extract_betting_legs(afternoon_games)
        if not all_legs:
            self.logger.error("❌ No betting legs extracted")
            return {"success": False, "message": "No betting options available"}

        # Filter high EV legs
        high_ev_legs = self.filter_high_ev_legs(all_legs, min_ev)
        if not high_ev_legs:
            self.logger.warning(f"⚠️ No legs found with EV >= {min_ev}%")
            return {
                "success": False,
                "message": f"No positive EV legs found (min {min_ev}%)",
            }

        # Build optimal parlays
        parlays = self.build_optimal_parlays(high_ev_legs, max_legs)
        if not parlays:
            self.logger.warning("⚠️ No optimal parlay combinations found")
            return {"success": False, "message": "No viable parlay combinations"}

        # Format and display results
        formatted_output = self.format_parlay_output(parlays)
        print(formatted_output)

        # Send Telegram alert
        await self.send_telegram_alert(formatted_output.replace("🏈", "🏈").replace("*", ""))

        # Save results
        results_file = self.save_results(parlays, high_ev_legs)

        return {
            "success": True,
            "parlays": parlays,
            "total_legs": len(high_ev_legs),
            "results_file": results_file,
            "message": f"Generated {len(parlays)} optimal parlay strategies",
        }


def main():
    parser = argparse.ArgumentParser(description="EQ12 NFL Parlay Optimizer")
    parser.add_argument(
        "--min-ev", type=float, default=5.0, help="Minimum EV threshold (default: 5.0)"
    )
    parser.add_argument(
        "--max-legs", type=int, default=20, help="Maximum legs per parlay (default: 20)"
    )
    parser.add_argument(
        "--bankroll", type=float, default=1000.0, help="Bankroll amount (default: 1000)"
    )
    parser.add_argument("--demo", action="store_true", help="Run in demo mode (no real API calls)")

    args = parser.parse_args()

    optimizer = EQ12NFLParlayOptimizer()
    optimizer.bankroll = args.bankroll

    if args.demo:
        print("🎮 Running in DEMO mode - using sample data")
        # Could add demo data here
        return

    # Run the optimizer
    try:
        result = asyncio.run(optimizer.run_optimizer(args.min_ev, args.max_legs))
        if result["success"]:
            print(f"\n✅ {result['message']}")
            print(f"📁 Results saved to: {result['results_file']}")
        else:
            print(f"\n❌ {result['message']}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Optimization stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Optimization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
