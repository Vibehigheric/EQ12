"""
EQ12 Weather-Enhanced Parlay Analysis

Integrates stadium location and weather intelligence into college football betting analysis.
Uses real NWS weather data to identify games where conditions favor UNDER totals or
impact point spreads.
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherEnhancedParlayAnalyzer:
    """Integrate weather intelligence into betting analysis"""

    def __init__(self):
        # Load our sports data and weather analysis
        self.sports_data = self._load_sports_data()
        self.weather_data = self._load_weather_analysis()

        # Weather betting factors
        self.weather_weights = {
            "precipitation": -0.25,  # Rain/snow strongly favors UNDER
            "strong_winds": -0.20,  # Winds 15+ mph favor UNDER
            "extreme_winds": -0.35,  # Winds 25+ mph heavily favor UNDER
            "cold_weather": -0.15,  # <32°F increases fumbles, favors UNDER
            "hot_weather": -0.10,  # >85°F increases fatigue
        }

    def _load_sports_data(self) -> dict[str, Any]:
        """Load our comprehensive sports data"""
        try:
            with open("C:\\\\EQ12\\\\data\\\\sports_pull_20251010_181611.json") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Could not load sports data: {e}")
            return {}

    def _load_weather_analysis(self) -> dict[str, Any]:
        """Load our weather analysis results"""
        try:
            # Find the most recent weather analysis file
            import glob

            weather_files = glob.glob("C:\\\\EQ12\\\\data\\college_stadium_weather_*.json")
            if weather_files:
                latest_file = max(weather_files)
                with open(latest_file) as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Could not load weather data: {e}")
        return {}

    def analyze_weather_enhanced_picks(self) -> dict[str, Any]:
        """Generate betting picks enhanced with weather intelligence"""

        analysis = {
            "timestamp": datetime.now(UTC).isoformat(),
            "weather_enhanced_picks": [],
            "confidence_adjustments": {},
            "summary": {
                "games_with_weather": 0,
                "weather_favors_under": 0,
                "high_confidence_picks": 0,
            },
        }

        # Get college football games
        college_games = self.sports_data.get("games_found", {}).get(
            "college_football_2025_10_11", []
        )
        weather_games = self.weather_data.get("games", [])

        logger.info(f"Analyzing {len(college_games)} college games with weather data")

        for game in college_games:
            game_analysis = self._analyze_single_game(game, weather_games)
            if game_analysis:
                analysis["weather_enhanced_picks"].append(game_analysis)

                # Update summary stats
                if game_analysis.get("weather_impact"):
                    analysis["summary"]["games_with_weather"] += 1

                    impact = game_analysis["weather_impact"]
                    if impact.get("total_impact") == "under":
                        analysis["summary"]["weather_favors_under"] += 1

                    if game_analysis.get("adjusted_confidence", 0) > 0.75:
                        analysis["summary"]["high_confidence_picks"] += 1

        # Generate top picks based on weather + value
        analysis["top_weather_picks"] = self._select_top_weather_picks(
            analysis["weather_enhanced_picks"]
        )

        return analysis

    def _analyze_single_game(
        self, game: dict[str, Any], weather_games: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Analyze a single game with weather enhancement"""

        home_team = game.get("home_team", "")
        away_team = game.get("away_team", "")
        matchup = f"{away_team} @ {home_team}"

        # Find weather data for this game
        weather_info = None
        for w_game in weather_games:
            if w_game.get("matchup") == matchup:
                weather_info = w_game
                break

        if not weather_info or not weather_info.get("weather_data"):
            return None

        # Extract betting lines
        bookmakers = game.get("bookmakers", [])
        if not bookmakers:
            return None

        # Get consensus lines (using first bookmaker for demo)
        consensus_lines = self._get_consensus_lines(bookmakers)
        if not consensus_lines:
            return None

        # Weather impact analysis
        weather_data = weather_info.get("weather_data", {})
        weather_impact = weather_data.get("betting_impact", {})

        # Calculate weather-adjusted confidence
        base_confidence = 0.70  # Starting confidence
        weather_adjustment = weather_impact.get("confidence_modifier", 0.0)
        adjusted_confidence = max(0.1, min(0.95, base_confidence + weather_adjustment))

        game_analysis = {
            "matchup": matchup,
            "commence_time": game.get("commence_time", ""),
            "stadium": weather_info.get("stadium_info", {}).get("stadium", "Unknown"),
            "location": f"{weather_info.get(
                'stadium_info',
                {}).get('city',
                '')}, {weather_info.get('stadium_info',
                {}).get('state',
                ''
            )}",
            "weather_conditions": weather_data.get("current", {}),
            "weather_impact": weather_impact,
            "betting_lines": consensus_lines,
            "base_confidence": base_confidence,
            "weather_adjustment": weather_adjustment,
            "adjusted_confidence": adjusted_confidence,
            "recommended_bets": [],
        }

        # Generate weather-enhanced betting recommendations
        game_analysis["recommended_bets"] = self._generate_weather_bets(
            consensus_lines, weather_impact, adjusted_confidence
        )

        return game_analysis

    def _get_consensus_lines(self, bookmakers: list[dict[str, Any]]) -> dict[str, Any]:
        """Extract consensus betting lines from bookmakers"""

        lines = {"spread": None, "total": None, "moneyline": {}}

        for bookmaker in bookmakers[:3]:  # Use first 3 bookmakers
            markets = bookmaker.get("markets", [])

            for market in markets:
                if market["key"] == "spreads":
                    outcomes = market.get("outcomes", [])
                    if len(outcomes) >= 2:
                        lines["spread"] = {
                            "favorite": outcomes[0]["name"],
                            "line": outcomes[0].get("point", 0),
                            "odds": outcomes[0].get("price", -110),
                        }

                elif market["key"] == "totals":
                    outcomes = market.get("outcomes", [])
                    for outcome in outcomes:
                        if outcome["name"] == "Over":
                            lines["total"] = {
                                "number": outcome.get("point", 50),
                                "over_odds": outcome.get("price", -110),
                            }
                        elif outcome["name"] == "Under" and lines["total"]:
                            lines["total"]["under_odds"] = outcome.get("price", -110)

        return lines

    def _generate_weather_bets(
        self, lines: dict[str, Any], weather_impact: dict[str, Any], confidence: float
    ) -> list[dict[str, Any]]:
        """Generate specific betting recommendations based on weather"""

        recommendations = []

        # Total (Over/Under) recommendations
        if lines.get("total") and weather_impact.get("total_impact"):
            total_info = lines["total"]

            if weather_impact["total_impact"] == "under":
                recommendations.append(
                    {
                        "bet_type": "total",
                        "selection": "UNDER",
                        "line": total_info.get("number", 50),
                        "odds": total_info.get("under_odds", -110),
                        "confidence": confidence,
                        "reasoning": f"Weather favors UNDER - {', '.join(weather_impact.get('factors', []))}",
                    }
                )

        # Spread recommendations (weather can affect margin)
        if lines.get("spread") and weather_impact.get("spread_impact") == "neutral":
            # Only recommend spreads if weather is neutral (not a major factor)
            spread_info = lines["spread"]
            if confidence > 0.72:  # High confidence threshold
                recommendations.append(
                    {
                        "bet_type": "spread",
                        "selection": f"{spread_info['favorite']} {spread_info['line']}",
                        "odds": spread_info.get("odds", -110),
                        "confidence": confidence * 0.9,  # Slight reduction for spread
                        "reasoning": "High confidence pick with neutral weather impact",
                    }
                )

        return recommendations

    def _select_top_weather_picks(self, all_picks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Select the top weather-enhanced betting opportunities"""

        # Filter for games with weather impact and recommendations
        weather_picks = [
            pick
            for pick in all_picks
            if pick.get("weather_impact", {}).get("confidence_modifier", 0) < -0.1
            and pick.get("recommended_bets")
        ]

        # Sort by adjusted confidence
        weather_picks.sort(key=lambda x: x.get("adjusted_confidence", 0), reverse=True)

        return weather_picks[:8]  # Top 8 weather-enhanced picks

    def save_analysis(self, analysis: dict[str, Any]) -> str:
        """Save weather-enhanced analysis"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\\\EQ12\\\\data\\weather_enhanced_parlay_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(analysis, f, indent=2)

            logger.info(f"Weather-enhanced analysis saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Could not save analysis: {e}")
            return ""


def main():
    """Run weather-enhanced parlay analysis"""

    print("🌦️ EQ12 WEATHER-ENHANCED PARLAY ANALYSIS")
    print("=" * 50)

    # Initialize analyzer
    analyzer = WeatherEnhancedParlayAnalyzer()

    # Run analysis
    analysis = analyzer.analyze_weather_enhanced_picks()

    # Save results
    filename = analyzer.save_analysis(analysis)

    # Display results
    print("\\n📊 WEATHER ANALYSIS SUMMARY:")
    summary = analysis["summary"]
    print(f"Games with weather data: {summary['games_with_weather']}")
    print(f"Weather favors UNDER: {summary['weather_favors_under']}")
    print(f"High confidence picks: {summary['high_confidence_picks']}")

    print("\\n🌦️ TOP WEATHER-ENHANCED PICKS:")
    for i, pick in enumerate(analysis.get("top_weather_picks", [])[:5], 1):
        print(f"\\n{i}. {pick['matchup']}")
        print(f"   Stadium: {pick['stadium']}")
        print(f"   Location: {pick['location']}")

        weather = pick.get("weather_conditions", {})
        temp = weather.get("temperature_", "N/A")
        wind = weather.get("wind_speed", "N/A")
        conditions = weather.get("short_forecast", "N/A")
        print(f"   Weather: {temp}°F, {wind} wind, {conditions}")

        print(f"   Confidence: {pick.get('adjusted_confidence', 0):.1%}")

        for bet in pick.get("recommended_bets", []):
            bet_type = bet["bet_type"].upper()
            selection = bet["selection"]
            line = bet.get("line", "")
            odds = bet.get("odds", "")
            confidence = bet.get("confidence", 0)

            print(f"   → {bet_type}: {selection} {line} ({odds}) - {confidence:.1%}")
            print(f"     Reasoning: {bet['reasoning']}")

    if filename:
        print(f"\\n💾 Full analysis saved to: {filename}")

    print("\\n✅ Weather-enhanced parlay analysis complete!")


if __name__ == "__main__":
    main()
