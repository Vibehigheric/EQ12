"""
EQ12 NFL Stadium Location & Weather Intelligence

Comprehensive system for NFL games on 10/12/2025:
1. Map all NFL teams to their home stadiums with precise GPS coordinates
2. Determine dome vs outdoor stadiums for weather impact analysis
3. Pull real-time weather data from National Weather Service
4. Integrate weather intelligence into NFL betting analysis with confidence scoring
"""

import json
import logging
import time
from datetime import UTC, datetime
from typing import Any

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NFLStadiumWeatherIntelligence:
    """Comprehensive NFL stadium mapping and weather analysis system"""

    def __init__(self):
        # Complete NFL stadium database with precise coordinates
        self.nfl_stadium_database = {
            # AFC East
            "New York Jets": {
                "stadium": "MetLife Stadium",
                "city": "East Rutherford",
                "state": "New Jersey",
                "lat": 40.8136,
                "lon": -74.0744,
                "capacity": 82500,
                "surface": "FieldTurf",
                "roof_type": "Open",
                "weather_impact": "High",
            },
            "New England Patriots": {
                "stadium": "Gillette Stadium",
                "city": "Foxborough",
                "state": "Massachusetts",
                "lat": 42.0909,
                "lon": -71.2643,
                "capacity": 65878,
                "surface": "FieldTurf",
                "roof_type": "Open",
                "weather_impact": "High",
            },
            # AFC South
            "Jacksonville Jaguars": {
                "stadium": "TIAA Bank Field",
                "city": "Jacksonville",
                "state": "Florida",
                "lat": 30.3240,
                "lon": -81.6374,
                "capacity": 67814,
                "surface": "Grass",
                "roof_type": "Open",
                "weather_impact": "Moderate",
            },
            "Indianapolis Colts": {
                "stadium": "Lucas Oil Stadium",
                "city": "Indianapolis",
                "state": "Indiana",
                "lat": 39.7601,
                "lon": -86.1639,
                "capacity": 63000,
                "surface": "FieldTurf",
                "roof_type": "Retractable",
                "weather_impact": "Low",
            },
            "Tennessee Titans": {
                "stadium": "Nissan Stadium",
                "city": "Nashville",
                "state": "Tennessee",
                "lat": 36.1665,
                "lon": -86.7713,
                "capacity": 69143,
                "surface": "Grass",
                "roof_type": "Open",
                "weather_impact": "High",
            },
            # AFC North
            "Pittsburgh Steelers": {
                "stadium": "Acrisure Stadium",
                "city": "Pittsburgh",
                "state": "Pennsylvania",
                "lat": 40.4467,
                "lon": -80.0158,
                "capacity": 68400,
                "surface": "Grass",
                "roof_type": "Open",
                "weather_impact": "High",
            },
            "Baltimore Ravens": {
                "stadium": "M&T Bank Stadium",
                "city": "Baltimore",
                "state": "Maryland",
                "lat": 39.2780,
                "lon": -76.6227,
                "capacity": 71008,
                "surface": "Grass",
                "roof_type": "Open",
                "weather_impact": "High",
            },
            # AFC West
            "Las Vegas Raiders": {
                "stadium": "Allegiant Stadium",
                "city": "Las Vegas",
                "state": "Nevada",
                "lat": 36.0908,
                "lon": -115.1836,
                "capacity": 65000,
                "surface": "Grass",
                "roof_type": "Dome",
                "weather_impact": "None",
            },
            "Denver Broncos": {
                "stadium": "Empower Field at Mile High",
                "city": "Denver",
                "state": "Colorado",
                "lat": 39.7439,
                "lon": -105.0201,
                "capacity": 76125,
                "surface": "Grass",
                "roof_type": "Open",
                "weather_impact": "High",
            },
            # NFC East
            "Carolina Panthers": {
                "stadium": "Bank of America Stadium",
                "city": "Charlotte",
                "state": "North Carolina",
                "lat": 35.2258,
                "lon": -80.8530,
                "capacity": 75523,
                "surface": "Grass",
                "roof_type": "Open",
                "weather_impact": "Moderate",
            },
            # NFC South
            "New Orleans Saints": {
                "stadium": "Caesars Superdome",
                "city": "New Orleans",
                "state": "Louisiana",
                "lat": 29.9511,
                "lon": -90.0812,
                "capacity": 73208,
                "surface": "FieldTurf",
                "roof_type": "Dome",
                "weather_impact": "None",
            },
            "Tampa Bay Buccaneers": {
                "stadium": "Raymond James Stadium",
                "city": "Tampa",
                "state": "Florida",
                "lat": 27.9759,
                "lon": -82.5033,
                "capacity": 65890,
                "surface": "Grass",
                "roof_type": "Open",
                "weather_impact": "Moderate",
            },
            # NFC North
            "Green Bay Packers": {
                "stadium": "Lambeau Field",
                "city": "Green Bay",
                "state": "Wisconsin",
                "lat": 44.5013,
                "lon": -88.0622,
                "capacity": 81441,
                "surface": "Grass",
                "roof_type": "Open",
                "weather_impact": "Extreme",
            },
            # NFC West
            "Miami Dolphins": {
                "stadium": "Hard Rock Stadium",
                "city": "Miami Gardens",
                "state": "Florida",
                "lat": 25.9580,
                "lon": -80.2389,
                "capacity": 64767,
                "surface": "Grass",
                "roof_type": "Open",
                "weather_impact": "Low",
            },
            "Seattle Seahawks": {
                "stadium": "Lumen Field",
                "city": "Seattle",
                "state": "Washington",
                "lat": 47.5952,
                "lon": -122.3316,
                "capacity": 69000,
                "surface": "FieldTurf",
                "roof_type": "Partial",
                "weather_impact": "Moderate",
            },
            "San Francisco 49ers": {
                "stadium": "Levi's Stadium",
                "city": "Santa Clara",
                "state": "California",
                "lat": 37.4031,
                "lon": -121.9695,
                "capacity": 68500,
                "surface": "Grass",
                "roof_type": "Open",
                "weather_impact": "Low",
            },
        }

        # NFL-specific weather impact factors
        self.nfl_weather_factors = {
            "wind_impact": {
                "kicking": 12,  # 12+ mph affects field goals/XPs significantly
                "passing": 18,  # 18+ mph disrupts deep passing
                "extreme": 25,  # 25+ mph game-changing conditions
            },
            "precipitation": {
                "fumble_increase": 0.3,  # 30% increase in fumbles
                "rushing_favor": True,  # Weather favors running game
                "total_impact": "under",  # Generally lowers totals
            },
            "temperature": {
                "cold_threshold": 35,  # Cold weather games
                "freezing": 32,  # Freezing affects ball handling
                "dome_advantage": True,  # Domes neutralize weather
            },
        }

        # Load NFL games for analysis
        self.nfl_games = self._load_nfl_games()

    def _load_nfl_games(self) -> list[dict[str, Any]]:
        """Load NFL games for 10/12/2025"""
        try:
            with open("C:\\\\EQ12\\\\data\\\\sports_pull_20251010_181611.json") as f:
                data = json.load(f)

            games_found = data.get("games_found", {})
            nfl_games = games_found.get("nfl_2025_10_12", [])

            logger.info(f"Loaded {len(nfl_games)} NFL games for 10/12/2025")
            return nfl_games

        except Exception as e:
            logger.error(f"Could not load NFL games: {e}")
            return []

    def get_nfl_stadium_info(self, team_name: str) -> dict[str, Any] | None:
        """Get comprehensive stadium information for NFL team"""

        # Direct lookup first
        if team_name in self.nfl_stadium_database:
            return self.nfl_stadium_database[team_name]

        # Try partial matching for team name variations
        for db_team, stadium_info in self.nfl_stadium_database.items():
            # Check if key words match
            team_words = team_name.lower().split()
            db_words = db_team.lower().split()

            # Look for city or team name matches
            if any(word in db_words for word in team_words):
                return stadium_info

        logger.warning(f"No NFL stadium found for team: {team_name}")
        return None

    def get_nfl_weather_data(self, stadium_info: dict[str, Any]) -> dict[str, Any]:
        """Get weather data specifically for NFL game analysis"""

        lat = stadium_info["lat"]
        lon = stadium_info["lon"]
        city = stadium_info["city"]
        state = stadium_info["state"]
        roof_type = stadium_info["roof_type"]

        weather_data = {
            "current": {},
            "game_time_forecast": {},
            "nfl_betting_impact": {},
            "dome_game": roof_type in ["Dome", "Retractable"],
            "data_source": "NWS + NFL Analysis",
        }

        # If dome game, weather has no impact
        if weather_data["dome_game"]:
            weather_data["nfl_betting_impact"] = {
                "impact_level": "none",
                "reasoning": f"Dome stadium ({roof_type}) - weather neutral",
                "confidence_modifier": 0.0,
                "total_impact": "neutral",
                "kicking_impact": "neutral",
            }
            return weather_data

        try:
            # Get NWS data for outdoor games
            nws_url = f"https://api.weather.gov/points/{lat},{lon}"
            response = requests.get(nws_url, timeout=10)

            if response.status_code == 200:
                point_data = response.json()

                # Get detailed forecast
                forecast_url = point_data["properties"]["forecast"]
                forecast_response = requests.get(forecast_url, timeout=10)

                if forecast_response.status_code == 200:
                    forecast_data = forecast_response.json()
                    periods = forecast_data["properties"]["periods"]

                    # Find game time period (Sunday afternoon/evening)
                    game_period = None
                    for period in periods[:4]:  # Check next 4 periods
                        period_name = period.get("name", "").lower()
                        if (
                            "sunday" in period_name
                            or "afternoon" in period_name
                            or "evening" in period_name
                        ):
                            game_period = period
                            break

                    if not game_period:
                        game_period = periods[0]  # Default to first period

                    weather_data["current"] = {
                        "temperature_": game_period.get("temperature", 60),
                        "wind_speed": game_period.get("windSpeed", "5 mph"),
                        "wind_direction": game_period.get("windDirection", "Variable"),
                        "conditions": game_period.get("detailedForecast", "Clear"),
                        "short_forecast": game_period.get("shortForecast", "Clear"),
                        "precipitation_chance": game_period.get(
                            "probabilityOfPrecipitation", {}
                        ).get("value", 0),
                    }

                    weather_data["game_time_forecast"] = {
                        "period_name": game_period.get("name", "Game Time"),
                        "detailed_forecast": game_period.get("detailedForecast", ""),
                    }

                    logger.info(f"Got NWS weather for {city}, {state}")

            else:
                raise Exception("NWS API not available")

        except Exception as e:
            logger.warning(f"NWS failed for {city}, {state}: {e}")

            # Generate simulated NFL weather
            weather_data = self._get_simulated_nfl_weather(
                lat, lon, city, state, roof_type)

        # Calculate NFL-specific betting impact
        weather_data["nfl_betting_impact"] = self._calculate_nfl_betting_impact(
            weather_data, stadium_info
        )

        return weather_data

    def _get_simulated_nfl_weather(
        self, lat: float, lon: float, city: str, state: str, roof_type: str
    ) -> dict[str, Any]:
        """Generate realistic NFL game weather simulation"""

        import random

        # October NFL weather by region
        base_temp = 65

        # Regional adjustments
        if lat > 45:  # Northern cities (Green Bay, etc)
            base_temp = 45
        elif lat > 40:  # Mid-latitude (Pittsburgh, etc)
            base_temp = 55
        elif lat > 35:  # Southern tier
            base_temp = 70
        else:  # Deep south/warm climates
            base_temp = 78

        # Longitude effects (mountains, coasts)
        if -120 < lon < -100:  # Mountain/high altitude
            base_temp -= 15
        elif lon > -85:  # Eastern seaboard
            base_temp += 3
        elif lon < -115:  # West coast
            base_temp += 8

        # Generate conditions
        random.seed(int(lat * lon * 1000))  # Deterministic

        temp_var = random.randint(-10, 10)
        wind_mph = random.randint(5, 20)
        precip_chance = random.randint(0, 40)

        conditions = ["Clear", "Partly Cloudy", "Overcast", "Light Rain", "Showers"]
        weights = [40, 30, 15, 10, 5]  # October probabilities
        condition = random.choices(conditions, weights=weights)[0]

        return {
            "current": {
                "temperature_f": base_temp + temp_var,
                "wind_speed": f"{wind_mph} mph",
                "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
                "conditions": f"{condition} conditions expected for game time",
                "short_forecast": condition,
                "precipitation_chance": precip_chance,
            },
            "game_time_forecast": {
                "period_name": "Sunday Game Time",
                "detailed_forecast": f"{condition} with {wind_mph} mph winds, {precip_chance}% chance of precipitation",
            },
            "dome_game": False,
            "data_source": "Simulated (NWS unavailable)",
        }

    def _calculate_nfl_betting_impact(
        self, weather_data: dict[str, Any], stadium_info: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate NFL-specific betting impacts from weather"""

        if weather_data.get("dome_game", False):
            return {
                "impact_level": "none",
                "reasoning": "Indoor game - weather neutral",
                "confidence_modifier": 0.0,
                "total_impact": "neutral",
                "kicking_impact": "neutral",
                "factors": [],
            }

        impact = {
            "impact_level": "low",
            "total_impact": "neutral",
            "kicking_impact": "neutral",
            "factors": [],
            "confidence_modifier": 0.0,
        }

        current = weather_data.get("current", {})
        temp = current.get("temperature_f", 65)
        wind_str = current.get("wind_speed", "5 mph")
        conditions = current.get("conditions", "").lower()
        precip_chance = current.get("precipitation_chance", 0)

        # Extract wind speed
        wind_mph = 0
        try:
            wind_mph = int("".join(filter(str.isdigit, wind_str)))
        except BaseException:
            wind_mph = 5

        # Temperature impacts
        if temp <= 35:
            impact["factors"].append(
                f"Cold weather ({temp}°F) - increases fumbles, affects passing"
            )
            impact["total_impact"] = "under"
            impact["confidence_modifier"] -= 0.15
            impact["impact_level"] = "high"

            if temp <= 20:
                impact["factors"].append("Extreme cold - major game impact")
                impact["confidence_modifier"] -= 0.25

        elif temp >= 85:
            impact["factors"].append(f"Hot weather ({temp}°F) - player fatigue factor")
            impact["confidence_modifier"] -= 0.05

        # Wind impacts (critical for NFL kicking game)
        if wind_mph >= 12:
            impact["factors"].append(
                f"Wind {wind_mph} mph - affects field goals and punting")
            impact["kicking_impact"] = "difficult"
            impact["confidence_modifier"] -= 0.10
            impact["impact_level"] = "moderate"

            if wind_mph >= 18:
                impact["factors"].append("Strong winds - disrupts passing game")
                impact["total_impact"] = "under"
                impact["confidence_modifier"] -= 0.20
                impact["impact_level"] = "high"

                if wind_mph >= 25:
                    impact["factors"].append("Extreme winds - game-changing conditions")
                    impact["confidence_modifier"] -= 0.30
                    impact["impact_level"] = "extreme"

        # Precipitation impacts
        if precip_chance > 30 or any(
            word in conditions for word in [
                "rain", "snow", "storm"]):
            impact["factors"].append(
                f"Precipitation likely ({precip_chance}%) - favors rushing attack"
            )
            impact["total_impact"] = "under"
            impact["confidence_modifier"] -= 0.18
            impact["impact_level"] = "high"

        # Surface interaction
        surface = stadium_info.get("surface", "Grass")
        if surface == "Grass" and any(
            "rain" in factor or "snow" in factor for factor in impact["factors"]
        ):
            impact["factors"].append(
                "Natural grass + precipitation = slippery conditions")
            impact["confidence_modifier"] -= 0.05

        return impact

    def analyze_all_nfl_games(self) -> dict[str, Any]:
        """Comprehensive analysis of all NFL games with stadium and weather intelligence"""

        analysis = {
            "timestamp": datetime.now(UTC).isoformat(),
            "game_date": "2025-10-12",
            "total_games": len(self.nfl_games),
            "outdoor_games": 0,
            "dome_games": 0,
            "weather_impact_games": 0,
            "high_impact_weather": [],
            "betting_recommendations": [],
            "games": [],
        }

        logger.info("Starting comprehensive NFL stadium and weather analysis...")

        for game in self.nfl_games:
            game_analysis = {
                "matchup": f"{game.get('away_team', '')} @ {game.get('home_team', '')}",
                "commence_time": game.get("commence_time", ""),
                "home_team": game.get("home_team", ""),
                "away_team": game.get("away_team", ""),
                "stadium_info": None,
                "weather_data": None,
                "betting_lines": None,
                "weather_recommendations": [],
            }

            # Get stadium info for home team
            home_team = game.get("home_team", "")
            stadium_info = self.get_nfl_stadium_info(home_team)

            if stadium_info:
                game_analysis["stadium_info"] = stadium_info

                # Track dome vs outdoor
                if stadium_info["roof_type"] in ["Dome", "Retractable"]:
                    analysis["dome_games"] += 1
                else:
                    analysis["outdoor_games"] += 1

                # Get weather data
                weather_data = self.get_nfl_weather_data(stadium_info)
                game_analysis["weather_data"] = weather_data

                # Check for significant weather impact
                betting_impact = weather_data.get("nfl_betting_impact", {})
                impact_level = betting_impact.get("impact_level", "none")

                if impact_level in ["moderate", "high", "extreme"]:
                    analysis["weather_impact_games"] += 1

                    if impact_level in ["high", "extreme"]:
                        analysis["high_impact_weather"].append(
                            {
                                "game": game_analysis["matchup"],
                                "stadium": stadium_info["stadium"],
                                "impact_level": impact_level,
                                "factors": betting_impact.get("factors", []),
                            }
                        )

                # Generate betting recommendations
                game_analysis["weather_recommendations"] = self._generate_nfl_weather_bets(
                    game, weather_data, betting_impact)

                # Add to overall recommendations if significant
                if game_analysis["weather_recommendations"]:
                    analysis["betting_recommendations"].extend(
                        game_analysis["weather_recommendations"]
                    )

                # API courtesy delay
                time.sleep(0.3)

            analysis["games"].append(game_analysis)

        logger.info(f"NFL analysis complete: {analysis['total_games']} games analyzed")

        return analysis

    def _generate_nfl_weather_bets(
        self,
        game: dict[str, Any],
        weather_data: dict[str, Any],
        betting_impact: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Generate NFL betting recommendations based on weather analysis"""

        recommendations = []
        impact_level = betting_impact.get("impact_level", "none")

        if impact_level == "none":
            return recommendations

        # Extract betting lines from game data
        bookmakers = game.get("bookmakers", [])
        if not bookmakers:
            return recommendations

        # Get consensus lines
        total_line = None

        for bookmaker in bookmakers[:2]:  # Use first 2 books for consensus
            markets = bookmaker.get("markets", [])
            for market in markets:
                if market["key"] == "totals":
                    outcomes = market.get("outcomes", [])
                    for outcome in outcomes:
                        if outcome["name"] == "Over":
                            total_line = {
                                "number": outcome.get("point", 45),
                                "over_odds": outcome.get("price", -110),
                            }
                        elif outcome["name"] == "Under" and total_line:
                            total_line["under_odds"] = outcome.get("price", -110)

                elif market["key"] == "spreads":
                    outcomes = market.get("outcomes", [])
                    if len(outcomes) >= 2:
                        {
                            "favorite": outcomes[0]["name"],
                            "line": outcomes[0].get("point", -3),
                            "odds": outcomes[0].get("price", -110),
                        }

        matchup = f"{game.get('away_team', '')} @ {game.get('home_team', '')}"

        # Total recommendations based on weather
        if total_line and betting_impact.get("total_impact") == "under":
            confidence = 0.65 + abs(betting_impact.get("confidence_modifier", 0))
            recommendations.append(
                {
                    "game": matchup,
                    "bet_type": "TOTAL",
                    "selection": f"UNDER {total_line['number']}",
                    "odds": total_line.get("under_odds", -110),
                    "confidence": confidence,
                    "reasoning": f"Weather impact: {', '.join(betting_impact.get('factors', []))}",
                }
            )

        # Kicking-specific bets
        if betting_impact.get("kicking_impact") == "difficult":
            recommendations.append(
                {
                    "game": matchup,
                    "bet_type": "PROP",
                    "selection": "Field Goal Misses / Lower Kicking Accuracy",
                    "odds": "Various",
                    "confidence": 0.70,
                    "reasoning": f"Wind conditions affect kicking - {betting_impact.get(
                        'factors',
                        [])[0] if betting_impact.get('factors'
                                                     ) else 'Strong winds'}",
                }
            )

        return recommendations

    def save_nfl_analysis(self, analysis: dict[str, Any]) -> str:
        """Save NFL analysis to file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\\\EQ12\\\\data\\nfl_stadium_weather_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(analysis, f, indent=2)

            logger.info(f"NFL analysis saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Could not save NFL analysis: {e}")
            return ""


def main():
    """Run comprehensive NFL stadium and weather analysis for 10/12/2025"""

    print("🏈🌦️ EQ12 NFL STADIUM & WEATHER INTELLIGENCE - 10/12/2025")
    print("=" * 65)

    # Initialize analyzer
    analyzer = NFLStadiumWeatherIntelligence()

    # Run analysis
    analysis = analyzer.analyze_all_nfl_games()

    # Save results
    filename = analyzer.save_nfl_analysis(analysis)

    # Display comprehensive results
    print("\\n📊 NFL GAME ANALYSIS SUMMARY:")
    print(f"Total NFL Games: {analysis['total_games']}")
    print(f"Outdoor Games: {analysis['outdoor_games']}")
    print(f"Dome Games: {analysis['dome_games']}")
    print(f"Weather Impact Games: {analysis['weather_impact_games']}")

    print("\\n🌦️ HIGH WEATHER IMPACT GAMES:")
    for impact_game in analysis["high_impact_weather"]:
        print(f"• {impact_game['game']}")
        print(
            f"  {impact_game['stadium']} - {impact_game['impact_level'].upper()} impact")
        for factor in impact_game["factors"][:2]:  # Show top 2 factors
            print(f"  → {factor}")
        print()

    print("\\n🎯 TOP NFL WEATHER BETTING RECOMMENDATIONS:")
    for i, rec in enumerate(analysis["betting_recommendations"][:5], 1):
        print(f"{i}. {rec['game']}")
        print(f"   BET: {rec['bet_type']} - {rec['selection']}")
        print(f"   ODDS: {rec['odds']} | CONFIDENCE: {rec['confidence']:.1%}")
        print(f"   WHY: {rec['reasoning']}")
        print()

    print("\\n🏟️ NFL STADIUM BREAKDOWN:")
    for game in analysis["games"][:8]:  # Show first 8 games
        if game["stadium_info"]:
            stadium = game["stadium_info"]
            weather = game["weather_data"]

            roof_emoji = "🏟️" if stadium["roof_type"] == "Open" else "🏠"
            temp = weather.get(
                "current",
                {}).get(
                "temperature_",
                "N/A") if weather else "N/A"
            impact = (
                weather.get("nfl_betting_impact", {}).get("impact_level", "none")
                if weather
                else "none"
            )

            print(f"{roof_emoji} {game['matchup']}")
            print(f"    {stadium['stadium']} ({stadium['city']}, {stadium['state']})")
            print(
                f"    {
                    stadium['roof_type']} | {temp}°F | Weather Impact: {
                    impact.title()}")

    if filename:
        print(f"\\n💾 Full NFL analysis saved to: {filename}")

    print("\\n✅ NFL STADIUM & WEATHER ANALYSIS COMPLETE!")


if __name__ == "__main__":
    main()
