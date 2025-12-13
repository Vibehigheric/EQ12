"""
EQ12 NFL Weather-Enhanced Betting Analysis

Final NFL betting intelligence system that combines:
1. Real National Weather Service data for all outdoor NFL stadiums
2. NFL-specific weather impact factors (kicking, passing, fumbles)
3. Dome vs outdoor game analysis
4. Enhanced betting recommendations with confidence scoring
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NFLWeatherEnhancedBettingAnalyzer:
    """Advanced NFL betting analysis with comprehensive weather intelligence"""

    def __init__(self):
        # Load our NFL sports data and weather analysis
        self.nfl_sports_data = self._load_nfl_sports_data()
        self.nfl_weather_data = self._load_nfl_weather_analysis()

        # NFL weather betting factors (more specific than college)
        self.nfl_betting_factors = {
            "wind_kicking": {
                "12_mph": -0.10,  # Field goals become more difficult
                "18_mph": -0.20,  # Passing game significantly affected
                "25_mph": -0.35,  # Game-changing wind conditions
            },
            "precipitation": {
                "fumble_multiplier": 0.4,  # NFL players better at ball security
                "passing_reduction": 0.25,  # Less impact than college
                "total_impact": -0.20,  # Moderate UNDER impact
            },
            "temperature": {
                "cold_35f": -0.15,  # Cold weather affects ball handling
                "freezing_32f": -0.25,  # Extreme cold major impact
                "heat_85f": -0.05,  # Minimal heat impact in October
            },
            "dome_advantage": 0.05,  # Slight advantage for controlled conditions
        }

    def _load_nfl_sports_data(self) -> dict[str, Any]:
        """Load NFL sports betting data"""
        try:
            with open("C:\\\\EQ12\\\\data\\\\sports_pull_20251010_181611.json") as f:
                data = json.load(f)
            return data.get("games_found", {}).get("nfl_2025_10_12", [])
        except Exception as e:
            logger.error(f"Could not load NFL sports data: {e}")
            return []

    def _load_nfl_weather_analysis(self) -> dict[str, Any]:
        """Load our NFL weather analysis"""
        try:
            import glob

            nfl_weather_files = glob.glob(
                "C:\\\\EQ12\\\\data\\nfl_stadium_weather_*.json")
            if nfl_weather_files:
                latest_file = max(nfl_weather_files)
                with open(latest_file) as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Could not load NFL weather data: {e}")
        return {}

    def generate_nfl_enhanced_analysis(self) -> dict[str, Any]:
        """Generate comprehensive NFL weather-enhanced betting analysis"""

        analysis = {
            "report_metadata": {
                "generated_at": datetime.now(UTC).isoformat(),
                "game_date": "2025-10-12",
                "report_type": "NFL Weather-Enhanced Betting Analysis",
            },
            "executive_summary": {
                "total_nfl_games": len(self.nfl_sports_data),
                "outdoor_games": 0,
                "dome_games": 0,
                "weather_advantage_games": 0,
                "high_confidence_plays": 0,
            },
            "weather_enhanced_nfl_picks": [],
            "dome_game_analysis": [],
            "outdoor_weather_games": [],
            "top_betting_recommendations": [],
            "nfl_weather_strategy": [],
        }

        # Process each NFL game
        weather_games = self.nfl_weather_data.get("games", [])

        for sports_game in self.nfl_sports_data:
            game_analysis = self._analyze_nfl_game_with_weather(
                sports_game, weather_games)
            if game_analysis:
                analysis["weather_enhanced_nfl_picks"].append(game_analysis)

                # Update summary stats
                stadium_info = game_analysis.get("stadium_info", {})
                if stadium_info:
                    roof_type = stadium_info.get("roof_type", "Open")
                    if roof_type in ["Dome", "Retractable"]:
                        analysis["executive_summary"]["dome_games"] += 1
                        analysis["dome_game_analysis"].append(game_analysis)
                    else:
                        analysis["executive_summary"]["outdoor_games"] += 1
                        analysis["outdoor_weather_games"].append(game_analysis)

                        # Check for weather advantage
                        weather_impact = game_analysis.get("weather_impact", {})
                        impact_level = weather_impact.get("impact_level", "none")
                        if impact_level in ["moderate", "high", "extreme"]:
                            analysis["executive_summary"]["weather_advantage_games"] += 1

                # High confidence plays
                for bet in game_analysis.get("betting_recommendations", []):
                    if bet.get("confidence", 0) > 0.75:
                        analysis["executive_summary"]["high_confidence_plays"] += 1

        # Generate top recommendations
        analysis["top_betting_recommendations"] = self._select_top_nfl_weather_bets(
            analysis["weather_enhanced_nfl_picks"]
        )

        # Generate strategy recommendations
        analysis["nfl_weather_strategy"] = self._generate_nfl_weather_strategy(analysis)

        return analysis

    def _analyze_nfl_game_with_weather(
        self, sports_game: dict[str, Any], weather_games: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Analyze individual NFL game with weather enhancement"""

        home_team = sports_game.get("home_team", "")
        away_team = sports_game.get("away_team", "")
        matchup = f"{away_team} @ {home_team}"

        # Find corresponding weather data
        weather_game = None
        for w_game in weather_games:
            if w_game.get("matchup") == matchup:
                weather_game = w_game
                break

        if not weather_game:
            return None

        # Extract betting lines
        bookmakers = sports_game.get("bookmakers", [])
        consensus_lines = self._extract_nfl_consensus_lines(bookmakers)

        game_analysis = {
            "matchup": matchup,
            "commence_time": sports_game.get(
                "commence_time",
                ""),
            "stadium_info": weather_game.get("stadium_info"),
            "weather_data": weather_game.get("weather_data"),
            "weather_impact": weather_game.get(
                "weather_data",
                {}).get(
                "nfl_betting_impact",
                {}),
            "betting_lines": consensus_lines,
            "betting_recommendations": [],
        }

        # Generate betting recommendations
        if consensus_lines and game_analysis["weather_impact"]:
            game_analysis["betting_recommendations"] = self._generate_nfl_enhanced_bets(
                consensus_lines,
                game_analysis["weather_impact"],
                game_analysis["stadium_info"],
            )

        return game_analysis

    def _extract_nfl_consensus_lines(
            self, bookmakers: list[dict[str, Any]]) -> dict[str, Any]:
        """Extract consensus NFL betting lines"""

        lines = {"total": None, "spread": None, "moneyline": {}}

        if not bookmakers:
            return lines

        # Use first bookmaker for lines (in real system, would aggregate)
        bookmaker = bookmakers[0]
        markets = bookmaker.get("markets", [])

        for market in markets:
            if market["key"] == "totals":
                outcomes = market.get("outcomes", [])
                for outcome in outcomes:
                    if outcome["name"] == "Over":
                        lines["total"] = {
                            "number": outcome.get("point", 45),
                            "over_odds": outcome.get("price", -110),
                        }
                    elif outcome["name"] == "Under" and lines["total"]:
                        lines["total"]["under_odds"] = outcome.get("price", -110)

            elif market["key"] == "spreads":
                outcomes = market.get("outcomes", [])
                if len(outcomes) >= 2:
                    lines["spread"] = {
                        "favorite": outcomes[0]["name"],
                        "line": outcomes[0].get("point", -3),
                        "favorite_odds": outcomes[0].get("price", -110),
                        "underdog": outcomes[1]["name"],
                        "underdog_odds": outcomes[1].get("price", -110),
                    }

        return lines

    def _generate_nfl_enhanced_bets(
        self,
        lines: dict[str, Any],
        weather_impact: dict[str, Any],
        stadium_info: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Generate NFL betting recommendations enhanced with weather intelligence"""

        recommendations = []
        impact_level = weather_impact.get("impact_level", "none")

        if impact_level == "none":
            # Dome games - focus on skill-based bets
            if lines.get("total"):
                total = lines["total"]
                recommendations.append(
                    {
                        "bet_type": "TOTAL",
                        "selection": f"OVER {total['number']}",
                        "odds": total.get("over_odds", -110),
                        "confidence": 0.60,
                        "reasoning": "Dome game - weather neutral, favor offensive output",
                    }
                )
            return recommendations

        base_confidence = 0.65
        confidence_modifier = weather_impact.get("confidence_modifier", 0)

        # Total bets based on weather impact
        if lines.get("total"):
            total = lines["total"]

            if weather_impact.get("total_impact") == "under":
                final_confidence = base_confidence + abs(confidence_modifier)
                recommendations.append(
                    {
                        "bet_type": "TOTAL",
                        "selection": f"UNDER {total['number']}",
                        "odds": total.get("under_odds", -110),
                        "confidence": min(final_confidence, 0.95),  # Cap at 95%
                        "reasoning": f"Weather favors UNDER - {weather_impact.get(
                            'reasoning',
                            'Adverse conditions'
                        )}",
                    }
                )

        # Kicking-related bets
        if weather_impact.get("kicking_impact") == "difficult":
            recommendations.append(
                {
                    "bet_type": "PROP",
                    "selection": "Field Goal Attempts UNDER / Missed FGs",
                    "odds": "TBD",
                    "confidence": 0.75,
                    "reasoning": f"Weather affects kicking accuracy - {weather_impact.get(
                        'factors',
                        ['Wind conditions'])[0] if weather_impact.get('factors'
                                                                      ) else 'Difficult conditions'}",
                }
            )

        # Team total bets (if available)
        if impact_level in ["high", "extreme"] and lines.get("total"):
            total_num = lines["total"]["number"]
            team_total_estimate = total_num / 2  # Rough estimate

            recommendations.append(
                {
                    "bet_type": "TEAM TOTAL",
                    "selection": f"Both teams UNDER {
                        team_total_estimate:.1f} points each",
                    "odds": "Various",
                    "confidence": 0.70,
                    "reasoning": f"Extreme weather impact ({impact_level}) affects both offenses",
                })

        return recommendations

    def _select_top_nfl_weather_bets(
            self, all_games: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Select top NFL weather-enhanced betting opportunities"""

        top_bets = []

        for game in all_games:
            for bet in game.get("betting_recommendations", []):
                if bet.get("confidence", 0) > 0.70:  # High confidence threshold
                    enhanced_bet = {
                        "game": game["matchup"],
                        "stadium": game.get(
                            "stadium_info",
                            {}).get(
                            "stadium",
                            "Unknown"),
                        "weather_impact": game.get(
                            "weather_impact",
                            {}).get(
                            "impact_level",
                            "none"),
                        **bet,
                    }
                    top_bets.append(enhanced_bet)

        # Sort by confidence
        top_bets.sort(key=lambda x: x.get("confidence", 0), reverse=True)

        return top_bets[:6]  # Top 6 plays

    def _generate_nfl_weather_strategy(self, analysis: dict[str, Any]) -> list[str]:
        """Generate NFL weather betting strategy recommendations"""

        outdoor_games = analysis["executive_summary"]["outdoor_games"]
        weather_games = analysis["executive_summary"]["weather_advantage_games"]

        strategy = [
            f"NFL WEATHER EDGE: {weather_games}/{outdoor_games} outdoor games have weather advantages",
            "DOME STRATEGY: Favor OVER totals in controlled environments (Saints, Colts, Raiders)",
            "WIND FACTOR: NFL kicking game most affected - target FG props in windy conditions",
            "COLD WEATHER: October weather minimal impact vs late season freeze games",
            "SURFACE IMPACT: Natural grass + precipitation = increased fumble risk",
            "BANKROLL: Allocate 30% to weather-enhanced NFL plays, 70% to skill-based analysis",
        ]

        if weather_games > 3:
            strategy.append(
                "HIGH WEATHER WEEK: Multiple games with significant weather impact")

        return strategy

    def save_nfl_enhanced_analysis(self, analysis: dict[str, Any]) -> str:
        """Save NFL weather-enhanced analysis"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\\\EQ12\\\\data\\nfl_weather_enhanced_betting_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(analysis, f, indent=2)

            logger.info(f"NFL enhanced analysis saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Could not save NFL analysis: {e}")
            return ""


def main():
    """Generate comprehensive NFL weather-enhanced betting analysis"""

    print("🏈⚡ EQ12 NFL WEATHER-ENHANCED BETTING ANALYSIS")
    print("=" * 55)

    # Initialize analyzer
    analyzer = NFLWeatherEnhancedBettingAnalyzer()

    # Generate analysis
    analysis = analyzer.generate_nfl_enhanced_analysis()

    # Save results
    filename = analyzer.save_nfl_enhanced_analysis(analysis)

    # Display results
    print("\\n📊 NFL BETTING INTELLIGENCE SUMMARY:")
    summary = analysis["executive_summary"]
    print(f"Total NFL Games: {summary['total_nfl_games']}")
    print(f"Outdoor Games: {summary['outdoor_games']}")
    print(f"Dome Games: {summary['dome_games']}")
    print(f"Weather Advantage Games: {summary['weather_advantage_games']}")
    print(f"High Confidence Plays: {summary['high_confidence_plays']}")

    print("\\n🎯 TOP NFL WEATHER-ENHANCED BETS:")
    for i, bet in enumerate(analysis["top_betting_recommendations"][:4], 1):
        print(f"\\n{i}. {bet['game']}")
        print(f"   Stadium: {bet['stadium']}")
        print(f"   Weather Impact: {bet['weather_impact'].title()}")
        print(f"   BET: {bet['bet_type']} - {bet['selection']}")
        print(f"   ODDS: {bet['odds']} | CONFIDENCE: {bet['confidence']:.1%}")
        print(f"   REASONING: {bet['reasoning']}")

    print("\\n🏟️ DOME vs OUTDOOR BREAKDOWN:")
    dome_count = len(analysis["dome_game_analysis"])
    outdoor_count = len(analysis["outdoor_weather_games"])
    print(f"🏠 Dome Games: {dome_count} (Weather Neutral)")
    print(f"🌦️ Outdoor Games: {outdoor_count} (Weather Impact Possible)")

    if analysis["dome_game_analysis"]:
        print("\\n   Dome Games:")
        for dome_game in analysis["dome_game_analysis"][:3]:
            stadium = dome_game.get("stadium_info", {})
            print(f"   • {dome_game['matchup']} - {stadium.get('stadium', 'Unknown')}")

    print("\\n🎲 NFL WEATHER STRATEGY:")
    for strategy in analysis["nfl_weather_strategy"]:
        print(f"• {strategy}")

    if filename:
        print(f"\\n💾 Full NFL analysis saved to: {filename}")

    print("\\n✅ NFL WEATHER-ENHANCED BETTING ANALYSIS COMPLETE!")


if __name__ == "__main__":
    main()
