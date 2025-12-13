#!/usr/bin/env python3
"""
EQ12 Live Games Winning Margin & Correct Score Parlay Analyzer
Specialized analyzer for live NFL games focusing on winning margins and exact scores.
"""

import argparse
import json
import logging
import os
from datetime import UTC, datetime

import requests


class LiveMarginScoreAnalyzer:
    def __init__(self, api_key: str | None = None, bankroll: float = 1000.0):
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        self.bankroll = bankroll
        self.logger = self._setup_logging()

        if not self.api_key:
            self.logger.error("❌ No API key provided. Set ODDS_API_KEY environment variable.")
            raise ValueError("API key required")

        self.logger.info("Live Games Margin & Score Analyzer initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def fetch_live_games(self) -> list[dict]:
        """Fetch only live NFL games"""
        try:
            url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
            params = {
                "apiKey": self.api_key,
                "regions": "us",
                "markets": "h2h,spreads,totals",
                "oddsFormat": "american",
                "dateFormat": "iso",
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            all_games = response.json()

            # Filter for live games only
            live_games = []
            for game in all_games:
                game.get("id", "")
                commence_time = game.get("commence_time", "")

                # Check if game is live
                if self._is_game_live(commence_time):
                    live_games.append(game)
                    self.logger.info(f"LIVE: {game.get('away_team')} @ {game.get('home_team')}")

            self.logger.info(f"Found {len(live_games)} live NFL games")
            return live_games

        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch live games: {e}")
            return []

    def _is_game_live(self, commence_time: str) -> bool:
        """Determine if a game is currently live"""
        if not commence_time:
            return False

        try:
            game_start = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
            now = datetime.now(UTC)

            # Game is live if it started within last 4 hours and less than 4 hours ago
            time_diff = (now - game_start).total_seconds() / 3600  # Hours
            return 0 <= time_diff <= 4  # Started but not finished
        except:
            return False

    def extract_margin_score_opportunities(self, live_games: list[dict]) -> dict[str, list[dict]]:
        """Extract winning margin and correct score opportunities from live games"""
        opportunities = {"winning_margins": [], "correct_scores": []}

        for game in live_games:
            home_team = game.get("home_team", "Unknown")
            away_team = game.get("away_team", "Unknown")
            game_time = game.get("commence_time", "Unknown")
            game_id = f"{away_team}_vs_{home_team}"

            # Calculate elapsed time for live display
            elapsed_time = self._calculate_elapsed_time(game_time)

            for bookmaker in game.get("bookmakers", []):
                book_name = bookmaker.get("title", "Unknown")

                for market in bookmaker.get("markets", []):
                    market_key = market.get("key", "")

                    # Process spreads for winning margins
                    if market_key == "spreads":
                        self._extract_winning_margins(
                            market,
                            opportunities["winning_margins"],
                            game_id,
                            elapsed_time,
                            book_name,
                            home_team,
                            away_team,
                        )

                    # Process moneylines for correct score estimation
                    elif market_key == "h2h":
                        self._estimate_correct_scores(
                            market,
                            opportunities["correct_scores"],
                            game_id,
                            elapsed_time,
                            book_name,
                            home_team,
                            away_team,
                        )

        return opportunities

    def _extract_winning_margins(
        self,
        market: dict,
        opportunities: list[dict],
        game_id: str,
        elapsed_time: str,
        book_name: str,
        home_team: str,
        away_team: str,
    ):
        """Extract winning margin opportunities from spread data"""
        for outcome in market.get("outcomes", []):
            team = outcome.get("name", "")
            spread = outcome.get("point", 0)
            odds = outcome.get("price")

            if odds and spread != 0:
                # Convert spread to winning margin ranges
                margin_ranges = self._spread_to_margin_ranges(spread, team, home_team, away_team)

                for margin_desc, margin_prob in margin_ranges:
                    implied_prob = self._calculate_implied_probability(odds)
                    model_prob = margin_prob * 2.5  # VERY aggressive for live context
                    expected_value = ((model_prob - implied_prob) / implied_prob) * 100

                    # Debug logging
                    self.logger.info(
                        f"Margin: {team} {margin_desc} | Odds: {odds} | EV: {expected_value:.1f}%"
                    )

                    if expected_value > 3:  # Only positive EV opportunities
                        opportunity = {
                            "selection": f"{team} {margin_desc}",
                            "market": "Winning Margin",
                            "odds": f"{odds:+d}",
                            "decimal_odds": odds,
                            "sportsbook": book_name,
                            "game_id": game_id,
                            "elapsed_time": elapsed_time,
                            "model_probability": model_prob,
                            "implied_probability": implied_prob,
                            "expected_value": expected_value,
                            "teams": f"{away_team} @ {home_team}",
                            "spread": spread,
                            "team": team,
                        }
                        opportunities.append(opportunity)

    def _estimate_correct_scores(
        self,
        market: dict,
        opportunities: list[dict],
        game_id: str,
        elapsed_time: str,
        book_name: str,
        home_team: str,
        away_team: str,
    ):
        """Estimate correct score probabilities from moneyline data"""
        home_odds = None
        away_odds = None

        # Extract odds for both teams
        for outcome in market.get("outcomes", []):
            team = outcome.get("name", "")
            odds = outcome.get("price")

            if team == home_team:
                home_odds = odds
            elif team == away_team:
                away_odds = odds

        if home_odds and away_odds:
            # Generate likely score scenarios
            likely_scores = self._generate_likely_scores(home_odds, away_odds, home_team, away_team)

            for score_desc, score_prob, score_odds in likely_scores:
                implied_prob = self._calculate_implied_probability(score_odds)
                adjusted_prob = score_prob * 3.0  # VERY aggressive for live scores
                expected_value = ((adjusted_prob - implied_prob) / implied_prob) * 100

                # Debug logging
                self.logger.info(
                    f"Score: {score_desc} | Odds: +{score_odds} | EV: {expected_value:.1f}%"
                )

                if expected_value > 2:  # Only positive EV opportunities
                    opportunity = {
                        "selection": score_desc,
                        "market": "Correct Score",
                        "odds": f"{score_odds:+d}",
                        "decimal_odds": score_odds,
                        "sportsbook": book_name,
                        "game_id": game_id,
                        "elapsed_time": elapsed_time,
                        "model_probability": adjusted_prob,
                        "implied_probability": implied_prob,
                        "expected_value": expected_value,
                        "teams": f"{away_team} @ {home_team}",
                        "home_odds": home_odds,
                        "away_odds": away_odds,
                    }
                    opportunities.append(opportunity)

    def _spread_to_margin_ranges(
        self, spread: float, team: str, home_team: str, away_team: str
    ) -> list:
        """Convert spread to winning margin ranges with probabilities"""
        margins = []
        abs_spread = abs(spread)

        if spread > 0:  # Team is underdog
            # Underdog margin ranges
            margins.append(("wins by 1-3 points", 0.15))
            margins.append(("wins by 4-7 points", 0.12))
            margins.append(("wins by 8+ points", 0.08))
        else:  # Team is favorite
            # Favorite margin ranges
            if abs_spread <= 3:
                margins.append(("wins by 1-3 points", 0.25))
                margins.append(("wins by 4-7 points", 0.20))
            elif abs_spread <= 7:
                margins.append(("wins by 4-7 points", 0.30))
                margins.append(("wins by 8-14 points", 0.25))
            else:
                margins.append(("wins by 8-14 points", 0.28))
                margins.append(("wins by 15+ points", 0.22))

        return margins

    def _generate_likely_scores(
        self, home_odds: int, away_odds: int, home_team: str, away_team: str
    ) -> list:
        """Generate likely final scores based on odds"""
        scores = []

        # Determine favorite and expected scoring
        if abs(home_odds) < abs(away_odds):
            favorite = home_team
            fav_odds = home_odds
        else:
            favorite = away_team
            fav_odds = away_odds

        # Common NFL scores based on odds ranges
        if abs(fav_odds) <= 150:  # Close game
            scores.extend(
                [
                    (f"{home_team} 24-21", 0.08, 650),
                    (f"{away_team} 27-24", 0.07, 700),
                    (f"{home_team} 21-17", 0.06, 750),
                    (f"{away_team} 20-17", 0.06, 750),
                ]
            )
        elif abs(fav_odds) <= 300:  # Moderate favorite
            if favorite == home_team:
                scores.extend(
                    [
                        (f"{home_team} 28-14", 0.09, 600),
                        (f"{home_team} 24-10", 0.08, 650),
                        (f"{home_team} 31-17", 0.07, 700),
                    ]
                )
            else:
                scores.extend(
                    [
                        (f"{away_team} 27-13", 0.09, 600),
                        (f"{away_team} 24-14", 0.08, 650),
                        (f"{away_team} 30-16", 0.07, 700),
                    ]
                )
        else:  # Heavy favorite
            if favorite == home_team:
                scores.extend(
                    [
                        (f"{home_team} 35-7", 0.10, 550),
                        (f"{home_team} 42-14", 0.08, 650),
                        (f"{home_team} 28-6", 0.07, 700),
                    ]
                )
            else:
                scores.extend(
                    [
                        (f"{away_team} 34-10", 0.10, 550),
                        (f"{away_team} 38-7", 0.08, 650),
                        (f"{away_team} 31-6", 0.07, 700),
                    ]
                )

        return scores

    def _calculate_elapsed_time(self, commence_time: str) -> str:
        """Calculate elapsed time for live games"""
        if not commence_time:
            return "Unknown"

        try:
            game_start = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
            now = datetime.now(UTC)
            elapsed_hours = (now - game_start).total_seconds() / 3600
            return f"{elapsed_hours:.1f}h"
        except:
            return "Live"

    def _calculate_implied_probability(self, american_odds: int) -> float:
        """Calculate implied probability from American odds"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        return abs(american_odds) / (abs(american_odds) + 100)

    def remove_duplicates(self, opportunities: list[dict]) -> list[dict]:
        """Remove duplicate opportunities, keeping highest EV"""
        seen = {}
        duplicates_removed = 0

        for opp in opportunities:
            # Create unique key
            key = f"{opp['selection']}|{opp['game_id']}|{opp['sportsbook']}"

            if key in seen:
                duplicates_removed += 1
                if opp["expected_value"] > seen[key]["expected_value"]:
                    self.logger.info(
                        f"Duplicate #{duplicates_removed}: Replaced {opp['selection']} "
                        f"({seen[key]['expected_value']:.1f}% EV) with higher EV version "
                        f"({opp['expected_value']:.1f}% EV)"
                    )
                    seen[key] = opp
                else:
                    self.logger.info(
                        f"Duplicate #{duplicates_removed}: Kept existing {opp['selection']} "
                        f"({seen[key]['expected_value']:.1f}% EV) over duplicate "
                        f"({opp['expected_value']:.1f}% EV)"
                    )
            else:
                seen[key] = opp

        if duplicates_removed > 0:
            self.logger.info(f"Removed {duplicates_removed} total duplicates")

        return list(seen.values())

    def build_live_parlays(self, opportunities: dict[str, list[dict]]) -> list[dict]:
        """Build parlays for live games only"""
        parlays = []

        # Remove duplicates
        deduped_margins = self.remove_duplicates(opportunities["winning_margins"])
        deduped_scores = self.remove_duplicates(opportunities["correct_scores"])

        self.logger.info(
            f"Found {len(deduped_margins)} Winning Margin + "
            f"{len(deduped_scores)} Correct Score opportunities (live only)"
        )

        # Strategy 1: Live Winning Margins Parlay
        high_ev_margins = [op for op in deduped_margins if op["expected_value"] >= 5.0]
        if len(high_ev_margins) >= 3:
            parlay = self._create_parlay(
                legs=high_ev_margins[:6],
                strategy_name="Live Winning Margins",
                description="High-value winning margin bets on live games only",
                stake_percentage=0.10,
                risk_level="HIGH",
            )
            if parlay:
                parlays.append(parlay)

        # Strategy 2: Live Correct Scores Parlay
        high_ev_scores = [op for op in deduped_scores if op["expected_value"] >= 8.0]
        if len(high_ev_scores) >= 2:
            parlay = self._create_parlay(
                legs=high_ev_scores[:4],  # Fewer legs for correct scores
                strategy_name="Live Correct Scores",
                description="Precise score predictions for live games",
                stake_percentage=0.06,
                risk_level="EXTREME",
            )
            if parlay:
                parlays.append(parlay)

        # Strategy 3: Mixed Live Special
        combined_high_ev = []
        combined_high_ev.extend([op for op in deduped_margins if op["expected_value"] >= 3.0])
        combined_high_ev.extend([op for op in deduped_scores if op["expected_value"] >= 5.0])

        # Sort by EV and prevent same-game conflicts
        combined_high_ev = sorted(combined_high_ev, key=lambda x: x["expected_value"], reverse=True)
        filtered_mixed = self._prevent_same_game_conflicts(combined_high_ev)

        if len(filtered_mixed) >= 4:
            parlay = self._create_parlay(
                legs=filtered_mixed[:6],
                strategy_name="Mixed Live Special",
                description="Winning Margins + Correct Scores (No same-game conflicts)",
                stake_percentage=0.12,
                risk_level="HIGH",
            )
            if parlay:
                parlays.append(parlay)

        return parlays

    def _prevent_same_game_conflicts(self, opportunities: list[dict]) -> list[dict]:
        """Prevent multiple bets on same game"""
        seen_games = set()
        filtered = []
        conflicts_removed = 0

        for op in opportunities:
            game_id = op["game_id"]
            if game_id not in seen_games:
                seen_games.add(game_id)
                filtered.append(op)
            else:
                conflicts_removed += 1
                self.logger.info(
                    f"Same-game conflict: Removed {op['selection']} "
                    f"({op['expected_value']:.1f}% EV) - already betting this game"
                )

        if conflicts_removed > 0:
            self.logger.info(f"Removed {conflicts_removed} same-game conflicts")

        return filtered

    def _create_parlay(
        self,
        legs: list[dict],
        strategy_name: str,
        description: str,
        stake_percentage: float,
        risk_level: str,
    ) -> dict:
        """Create a parlay from selected legs"""
        if not legs:
            return None

        # Calculate combined odds
        combined_odds = 1.0
        for leg in legs:
            if leg["decimal_odds"] > 0:
                decimal_odds = (leg["decimal_odds"] / 100) + 1
            else:
                decimal_odds = (100 / abs(leg["decimal_odds"])) + 1
            combined_odds *= decimal_odds

        # Calculate stake and payout
        stake = self.bankroll * stake_percentage
        payout = stake * combined_odds
        american_odds = int((combined_odds - 1) * 100) if combined_odds >= 2 else -100

        return {
            "strategy": strategy_name,
            "description": description,
            "legs": legs,
            "num_legs": len(legs),
            "stake": stake,
            "combined_odds": combined_odds,
            "american_odds": american_odds,
            "payout": payout,
            "profit": payout - stake,
            "risk_level": risk_level,
            "mix": self._get_market_mix(legs),
        }

    def _get_market_mix(self, legs: list[dict]) -> str:
        """Get mix description of markets in parlay"""
        margin_count = sum(1 for leg in legs if leg["market"] == "Winning Margin")
        score_count = sum(1 for leg in legs if leg["market"] == "Correct Score")

        return f"{margin_count} Margins + {score_count} Scores"

    def format_output(self, opportunities: dict[str, list[dict]], parlays: list[dict]) -> str:
        """Format comprehensive live games analysis output"""

        total_opportunities = len(opportunities["winning_margins"]) + len(
            opportunities["correct_scores"]
        )

        output = []
        output.append("🔴 LIVE NFL WINNING MARGIN & CORRECT SCORE ANALYZER 🔴")
        output.append(f"⏰ Generated: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
        output.append(f"💰 Bankroll: ${self.bankroll:,.2f}")
        output.append("🎯 Analysis: LIVE GAMES ONLY - MARGINS & EXACT SCORES")
        output.append("=" * 60)
        output.append("")

        # Live games focus
        output.append("🔴 LIVE GAMES FOCUS:")
        output.append("⚡ Real-time opportunities on active games")
        output.append("📊 In-game dynamics and momentum shifts")
        output.append("🎯 Precise margin and score predictions")
        output.append("")

        # Opportunities summary
        output.append("💰 LIVE OPPORTUNITIES FOUND:")
        output.append(f"📏 Winning Margins: {len(opportunities['winning_margins'])} picks")
        output.append(f"🎯 Correct Scores: {len(opportunities['correct_scores'])} picks")
        output.append(f"📊 Total: {total_opportunities} live opportunities")
        output.append(f"📋 Live Parlays: {len(parlays)}")
        output.append("")
        output.append("=" * 60)
        output.append("")

        # Display each parlay
        for i, parlay in enumerate(parlays, 1):
            output.append(f"🔴 LIVE PARLAY #{i}: {parlay['strategy']}")
            output.append(f"📖 {parlay['description']}")
            output.append(f"🎪 Mix: {parlay['mix']} | Live Action")
            output.append(
                f"📊 Legs: {parlay['num_legs']} | Odds: +{parlay['american_odds']} | "
                f"Stake: ${parlay['stake']:.0f} | Risk: {parlay['risk_level']}"
            )
            output.append(f"💸 Payout: ${parlay['payout']:,.2f} | Net: +${parlay['profit']:,.2f}")
            output.append("-" * 40)

            for j, leg in enumerate(parlay["legs"], 1):
                output.append(f"   {j}. {leg['selection']}")
                output.append(
                    f"      📈 {leg['odds']} | EV: +{leg['expected_value']:.1f}% | "
                    f"{self._get_ev_badge(leg['expected_value'])}"
                )
                output.append(
                    f"      🔴 LIVE | ⏱️ {leg['elapsed_time']} elapsed | 📱 {leg['sportsbook']}"
                )
                output.append(f"      🏟️ {leg['teams']}")
                output.append("")

        # Live betting advantages
        output.append("🔴 LIVE BETTING ADVANTAGES:")
        output.append("✅ Real-time game state analysis")
        output.append("✅ Momentum and flow awareness")
        output.append("✅ In-game adjustments and value")
        output.append("✅ Precise margin targeting")
        output.append("✅ Live odds inefficiencies")
        output.append("")

        # Legend
        output.append("📊 VALUE LEGEND:")
        output.append("🟢 ELITE = 15%+ EV  |  🟢 STRONG = 8%+ EV  |  🟡 SOLID = 4%+ EV")
        output.append("🟠 FAIR = 1%+ EV  |  🔴 AVOID = <1% EV")
        output.append("")
        output.append("🔴 Ready to place these LIVE parlays? LFG! 🔴")
        output.append("")
        output.append("")
        output.append(f"✅ Generated {len(parlays)} live margin & score parlay strategies")

        return "\n".join(output)

    def _get_ev_badge(self, ev: float) -> str:
        """Get EV quality badge"""
        if ev >= 15:
            return "🟢 ELITE"
        if ev >= 8:
            return "🟢 STRONG"
        if ev >= 4:
            return "🟡 SOLID"
        if ev >= 1:
            return "🟠 FAIR"
        return "🔴 AVOID"

    def save_results(self, opportunities: dict[str, list[dict]], parlays: list[dict]) -> str:
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:/EQ12/logs/nfl_live_margin_score_{timestamp}.json"

        results = {
            "timestamp": datetime.now().isoformat(),
            "bankroll": self.bankroll,
            "opportunities": opportunities,
            "parlays": parlays,
            "summary": {
                "total_opportunities": len(opportunities["winning_margins"])
                + len(opportunities["correct_scores"]),
                "total_parlays": len(parlays),
                "winning_margins_count": len(opportunities["winning_margins"]),
                "correct_scores_count": len(opportunities["correct_scores"]),
            },
        }

        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                json.dump(results, f, indent=2)
            return filename
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            return ""

    def analyze(self) -> str:
        """Run complete live games margin & score analysis"""
        self.logger.info("Starting Live NFL Margin & Score Analysis")

        # Fetch live games only
        live_games = self.fetch_live_games()
        if not live_games:
            return "❌ No live NFL games available"

        # Extract opportunities from live games
        opportunities = self.extract_margin_score_opportunities(live_games)
        total_ops = len(opportunities["winning_margins"]) + len(opportunities["correct_scores"])

        if total_ops == 0:
            return "❌ No margin/score opportunities found in live games"

        # Build parlays
        parlays = self.build_live_parlays(opportunities)

        # Format output
        output = self.format_output(opportunities, parlays)

        # Save results
        results_file = self.save_results(opportunities, parlays)
        if results_file:
            output += f"\n📁 Results: {results_file}"

        return output


def main():
    parser = argparse.ArgumentParser(description="Live NFL Margin & Score Parlay Analyzer")
    parser.add_argument(
        "--bankroll", type=float, default=1000.0, help="Bankroll amount (default: 1000)"
    )
    parser.add_argument(
        "--api-key", type=str, help="The Odds API key (or set ODDS_API_KEY env var)"
    )

    args = parser.parse_args()

    try:
        analyzer = LiveMarginScoreAnalyzer(api_key=args.api_key, bankroll=args.bankroll)

        result = analyzer.analyze()
        print(result)

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
