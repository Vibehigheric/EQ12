"""
EQ12 Enhanced Parlay Analysis with Validation
Integrates Azure OpenAI client with parlay validation for production-ready betting analysis
"""

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

from dotenv import load_dotenv

# Import our custom modules
from eq12_azure_openai_client import EQ12AzureOpenAIClient
from eq12_parlay_validator import ParlayValidator

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class EQ12ProductionParlayAnalyzer:
    """Production-ready parlay analysis with validation and Azure OpenAI integration"""

    def __init__(self):
        self.ai_client = EQ12AzureOpenAIClient()
        self.validator = ParlayValidator()
        self.logger = logging.getLogger(__name__)

        # Analysis settings
        self.max_legs_per_parlay = 8
        self.min_expected_value = 5.0
        self.allowed_sportsbooks = {"DraftKings", "FanDuel", "BetMGM"}

    def analyze_nfl_parlays(
        self, games_data: list[dict[str, Any]], bankroll: float = 1000.0
    ) -> dict[str, Any]:
        """
        Complete NFL parlay analysis with AI recommendations and validation

        Args:
            games_data: List of NFL game data with odds
            bankroll: Available betting bankroll

        Returns:
            Validated parlay recommendations with AI analysis
        """
        self.logger.info(f"Starting parlay analysis for {len(games_data)} games")

        # Step 1: Filter and prepare game data
        filtered_games = self._filter_upcoming_games(games_data)
        if not filtered_games:
            return {"error": "No upcoming games found", "parlays": []}

        self.logger.info(f"Filtered to {len(filtered_games)} upcoming games")

        # Step 2: Generate AI analysis and recommendations
        ai_analysis = self._get_ai_parlay_recommendations(filtered_games)

        # Step 3: Create structured parlays based on AI recommendations
        structured_parlays = self._create_structured_parlays(filtered_games, ai_analysis, bankroll)

        # Step 4: Validate all parlays for sportsbook compliance
        validation_results = self.validator.validate_parlay_set({"parlays": structured_parlays})

        # Step 5: Compile final results
        final_results = {
            "timestamp": datetime.now(UTC).isoformat(),
            "bankroll": bankroll,
            "total_legs_analyzed": len(filtered_games),
            "ai_analysis": ai_analysis,
            "validation_status": (
                "✅ VALIDATED" if not validation_results["invalid_parlays"] else "⚠️ ISSUES_FOUND"
            ),
            "validation_summary": {
                "valid_parlays": len(validation_results["valid_parlays"]),
                "invalid_parlays": len(validation_results["invalid_parlays"]),
                "fixes_applied": validation_results.get("fixes_applied", []),
            },
            "parlays": validation_results["valid_parlays"],
            "rejected_parlays": validation_results["invalid_parlays"],
        }

        # Save results
        self._save_analysis_results(final_results)

        return final_results

    def _filter_upcoming_games(self, games_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter to upcoming games with valid odds from allowed sportsbooks"""
        filtered = []
        now = datetime.now(UTC)

        for game in games_data:
            try:
                # Check if game is upcoming
                commence_str = game.get("commence_time", "")
                if not commence_str:
                    continue

                commence_time = datetime.fromisoformat(commence_str.replace("Z", "+00:00"))
                if commence_time <= now:
                    continue

                # Check for valid bookmakers
                bookmakers = game.get("bookmakers", [])
                valid_bookmakers = [
                    bm
                    for bm in bookmakers
                    if bm.get("key", "").replace("_", "").title().replace(" ", "")
                    in self.allowed_sportsbooks
                ]

                if valid_bookmakers:
                    game["bookmakers"] = valid_bookmakers
                    filtered.append(game)

            except Exception as e:
                self.logger.warning(f"Error filtering game: {e}")
                continue

        return filtered

    def _get_ai_parlay_recommendations(self, games: list[dict[str, Any]]) -> str:
        """Get AI-powered parlay recommendations"""
        # Prepare game summary for AI
        game_summaries = []
        for game in games[:10]:  # Limit to avoid token limits
            home = game.get("home_team", "Home")
            away = game.get("away_team", "Away")
            commence = game.get("commence_time", "")[:10]  # Date only

            # Get best odds for this game
            odds_summary = self._get_game_odds_summary(game)

            game_summaries.append(f"📅 {away} @ {home} ({commence})\n{odds_summary}")

        prompt = f"""Analyze these NFL games for smart parlay opportunities:

{chr(10).join(game_summaries)}

REQUIREMENTS:
- Only recommend bets from ONE sportsbook per parlay (DraftKings, FanDuel, or BetMGM)
- No contradictory selections (Over+Under, both sides) in same parlay
- Max 6 legs per parlay for realistic odds
- Focus on games with clear value and edge

Provide 3-4 parlay strategies:
1. Conservative (2-3 legs, safer picks)
2. Balanced (3-4 legs, mixed risk)
3. Aggressive (4-6 legs, higher risk/reward)
4. Favorites-only (heavy favorites, lower multiplier)

For each strategy, explain:
- Specific sportsbook to use
- Exact bet selections (spread/total/moneyline with numbers)
- Reasoning for each pick
- Expected confidence level
- Risk assessment"""

        try:
            return self.ai_client.ask(prompt, model="gpt-4o")
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return "AI analysis unavailable - using rule-based recommendations"

    def _get_game_odds_summary(self, game: dict[str, Any]) -> str:
        """Get concise odds summary for a game"""
        summaries = []

        for bookmaker in game.get("bookmakers", [])[:3]:  # Top 3 books
            bookmaker.get("title", "Unknown")
            markets = bookmaker.get("markets", [])

            for market in markets:
                market_key = market.get("key", "")
                if market_key in ["h2h", "spreads", "totals"]:
                    outcomes = market.get("outcomes", [])
                    if outcomes:
                        if market_key == "h2h":
                            ml_odds = [f"{out['name']} ({out['price']:+d})" for out in outcomes[:2]]
                            summaries.append(f"ML: {' | '.join(ml_odds)}")
                        elif market_key == "spreads" and len(outcomes) >= 2:
                            spread_info = f"Spread: {outcomes[0]['point']}"
                            summaries.append(spread_info)
                        elif market_key == "totals" and len(outcomes) >= 2:
                            total_info = f"Total: {outcomes[0]['point']}"
                            summaries.append(total_info)

        return " | ".join(summaries[:3]) if summaries else "No odds available"

    def _create_structured_parlays(
        self, games: list[dict[str, Any]], ai_analysis: str, bankroll: float
    ) -> list[dict[str, Any]]:
        """Create structured parlay tickets based on AI analysis and game data"""
        parlays = []

        # Strategy 1: Conservative (BetMGM only)
        conservative_parlay = self._build_conservative_parlay(games, bankroll)
        if conservative_parlay:
            parlays.append(conservative_parlay)

        # Strategy 2: Balanced (DraftKings only)
        balanced_parlay = self._build_balanced_parlay(games, bankroll)
        if balanced_parlay:
            parlays.append(balanced_parlay)

        # Strategy 3: Aggressive (FanDuel only)
        aggressive_parlay = self._build_aggressive_parlay(games, bankroll)
        if aggressive_parlay:
            parlays.append(aggressive_parlay)

        return parlays

    def _build_conservative_parlay(
        self, games: list[dict[str, Any]], bankroll: float
    ) -> dict[str, Any]:
        """Build conservative 2-3 leg parlay with heavy favorites"""
        legs = []

        # Find heavy favorites (ML < -200)
        for game in games[:5]:
            for bookmaker in game.get("bookmakers", []):
                if "betmgm" not in bookmaker.get("key", "").lower():
                    continue

                for market in bookmaker.get("markets", []):
                    if market.get("key") == "h2h":
                        outcomes = market.get("outcomes", [])
                        for outcome in outcomes:
                            odds = outcome.get("price", 0)
                            if odds < -200:  # Heavy favorite
                                legs.append(
                                    {
                                        "game_id": f"{game.get('away_team', 'Away')}_at_{game.get('home_team', 'Home')}",
                                        "market": "Moneyline",
                                        "selection": outcome.get("name", ""),
                                        "odds": odds,
                                        "sportsbook": "BetMGM",
                                        "model_prob": (
                                            abs(odds) / (abs(odds) + 100)
                                            if odds < 0
                                            else 100 / (odds + 100)
                                        ),
                                        "expected_value": 8.0,
                                        "kelly_stake": min(abs(odds), 200),
                                        "commence_time": game.get("commence_time", ""),
                                        "risk_score": "🟡 MEDIUM" if odds > -300 else "🟥 HIGH",
                                    }
                                )
                                break
                if len(legs) >= 3:
                    break
            if len(legs) >= 3:
                break

        if len(legs) >= 2:
            return self._calculate_parlay_odds(
                {
                    "strategy": "Conservative Heavy Favorites (BetMGM-only)",
                    "legs": legs[:3],
                    "recommended_stake": min(100, bankroll * 0.05),
                }
            )

        return None

    def _build_balanced_parlay(
        self, games: list[dict[str, Any]], bankroll: float
    ) -> dict[str, Any]:
        """Build balanced 3-4 leg parlay with mixed bet types"""
        legs = []

        # Mix of spread, total, and ML bets
        for i, game in enumerate(games[:4]):
            for bookmaker in game.get("bookmakers", []):
                if "draftkings" not in bookmaker.get("key", "").lower():
                    continue

                # Alternate bet types
                market_preference = ["spreads", "totals", "h2h"][i % 3]

                for market in bookmaker.get("markets", []):
                    if market.get("key") == market_preference:
                        outcomes = market.get("outcomes", [])
                        if outcomes:
                            outcome = outcomes[0]  # Take first outcome

                            market_name = {
                                "h2h": "Moneyline",
                                "spreads": "Spread",
                                "totals": "Total",
                            }.get(market_preference, "Unknown")

                            selection = outcome.get("name", "")
                            if market_preference == "spreads":
                                selection += f" {outcome.get('point', '')}"
                            elif market_preference == "totals":
                                selection = f"Over {outcome.get('point', '')}"

                            legs.append(
                                {
                                    "game_id": f"{game.get('away_team', 'Away')}_at_{game.get('home_team', 'Home')}",
                                    "market": market_name,
                                    "selection": selection,
                                    "odds": outcome.get("price", -110),
                                    "sportsbook": "DraftKings",
                                    "model_prob": 0.55,  # Estimated
                                    "expected_value": 10.0,
                                    "kelly_stake": 110,
                                    "commence_time": game.get("commence_time", ""),
                                    "risk_score": "🟡 MEDIUM",
                                }
                            )
                            break
                break

        if len(legs) >= 3:
            return self._calculate_parlay_odds(
                {
                    "strategy": "Balanced Mixed Markets (DraftKings-only)",
                    "legs": legs[:4],
                    "recommended_stake": min(50, bankroll * 0.03),
                }
            )

        return None

    def _build_aggressive_parlay(
        self, games: list[dict[str, Any]], bankroll: float
    ) -> dict[str, Any]:
        """Build aggressive 4-6 leg parlay for higher payouts"""
        legs = []

        # Look for plus-money opportunities and totals
        for game in games[:6]:
            for bookmaker in game.get("bookmakers", []):
                if "fanduel" not in bookmaker.get("key", "").lower():
                    continue

                # Prefer totals and underdogs for higher variance
                for market in bookmaker.get("markets", []):
                    market_key = market.get("key", "")
                    outcomes = market.get("outcomes", [])

                    if market_key == "totals" and outcomes:
                        # Randomly pick over or under
                        outcome = outcomes[len(legs) % 2]  # Alternate over/under

                        legs.append(
                            {
                                "game_id": f"{game.get('away_team', 'Away')}_at_{game.get('home_team', 'Home')}",
                                "market": "Total",
                                "selection": f"{outcome.get('name', 'Over')} {outcome.get('point', '')}",
                                "odds": outcome.get("price", -110),
                                "sportsbook": "FanDuel",
                                "model_prob": 0.52,
                                "expected_value": 8.0,
                                "kelly_stake": 88,
                                "commence_time": game.get("commence_time", ""),
                                "risk_score": "🟡 MEDIUM",
                            }
                        )
                        break
                break

        if len(legs) >= 4:
            return self._calculate_parlay_odds(
                {
                    "strategy": "Aggressive High-Variance (FanDuel-only)",
                    "legs": legs[:6],
                    "recommended_stake": min(25, bankroll * 0.02),
                }
            )

        return None

    def _calculate_parlay_odds(self, parlay: dict[str, Any]) -> dict[str, Any]:
        """Calculate accurate parlay odds and payouts"""
        legs = parlay.get("legs", [])

        # Calculate combined decimal odds
        total_decimal_odds = 1.0
        for leg in legs:
            american_odds = leg.get("odds", -110)
            if american_odds > 0:
                decimal_odds = (american_odds / 100) + 1
            else:
                decimal_odds = (100 / abs(american_odds)) + 1
            total_decimal_odds *= decimal_odds

        # Convert to American odds
        if total_decimal_odds >= 2.0:
            american_odds = int((total_decimal_odds - 1) * 100)
        else:
            american_odds = int(-100 / (total_decimal_odds - 1))

        # Calculate payouts
        stake = parlay.get("recommended_stake", 25)
        potential_payout = stake * total_decimal_odds
        net_profit = potential_payout - stake

        parlay.update(
            {
                "leg_count": len(legs),
                "american_odds": american_odds,
                "multiplier": round(total_decimal_odds, 2),
                "potential_payout": round(potential_payout, 2),
                "net_profit": round(net_profit, 2),
            }
        )

        return parlay

    def _save_analysis_results(self, results: dict[str, Any]):
        """Save analysis results to logs directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nfl_parlays_analysis_{timestamp}.json"
        filepath = f"C:/EQ12/logs/{filename}"

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Analysis saved to: {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")


def analyze_nfl_parlays_production(json_file_path: str) -> dict[str, Any]:
    """Production entry point for NFL parlay analysis"""
    analyzer = EQ12ProductionParlayAnalyzer()

    try:
        # Load game data
        with open(json_file_path, encoding="utf-8") as f:
            data = json.load(f)

        games_data = data.get("data", [])
        if not games_data:
            return {"error": "No game data found in file"}

        # Run analysis
        results = analyzer.analyze_nfl_parlays(games_data, bankroll=1000.0)

        return results

    except Exception as e:
        return {"error": f"Analysis failed: {e}"}


if __name__ == "__main__":
    # Test with the cleaned parlay data file
    print("🏈 Starting Production NFL Parlay Analysis...")

    # Use the cleaned/placeable parlay file for testing
    test_file = "C:/EQ12/logs/nfl_parlays_clean_20251005_placeable.json"

    if os.path.exists(test_file):
        results = analyze_nfl_parlays_production(test_file)

        if "error" in results:
            print(f"❌ Analysis failed: {results['error']}")
        else:
            print("✅ Analysis complete!")
            print(f"   Validation Status: {results.get('validation_status')}")
            print(f"   Valid Parlays: {results['validation_summary']['valid_parlays']}")
            print(f"   Invalid Parlays: {results['validation_summary']['invalid_parlays']}")

            if results.get("parlays"):
                print("\n📊 Top Parlay Recommendation:")
                top_parlay = results["parlays"][0]
                print(f"   Strategy: {top_parlay['strategy']}")
                print(f"   Legs: {top_parlay['leg_count']}")
                print(f"   Odds: {top_parlay['american_odds']:+d}")
                print(f"   Stake: ${top_parlay['recommended_stake']}")
                print(f"   Potential: ${top_parlay['potential_payout']}")
    else:
        print(f"❌ Test file not found: {test_file}")
        print("Make sure the clean parlay file exists")
