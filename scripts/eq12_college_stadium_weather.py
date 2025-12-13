"""
EQ12 College Football Stadium Location & Weather Intelligence

Comprehensive system to:
1. Extract college games from our sports data pull
2. Map team names to their home stadiums with GPS coordinates
3. Pull current weather conditions and forecasts for each location
4. Integrate weather intelligence into betting analysis
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


class CollegeStadiumWeatherIntelligence:
    """Map college football teams to stadiums and get weather data"""

    def __init__(self):
        # Comprehensive college football stadium database
        self.stadium_database = {
            # Major conferences with GPS coordinates
            "Alabama Crimson Tide": {
                "stadium": "Bryant-Denny Stadium",
                "city": "Tuscaloosa",
                "state": "Alabama",
                "lat": 33.2080,
                "lon": -87.5502,
                "capacity": 101821,
                "surface": "Grass",
            },
            "Colorado State Rams": {
                "stadium": "Canvas Stadium",
                "city": "Fort Collins",
                "state": "Colorado",
                "lat": 40.5740,
                "lon": -105.0900,
                "capacity": 41200,
                "surface": "Grass",
            },
            "Washington Huskies": {
                "stadium": "Alaska Airlines Field at Husky Stadium",
                "city": "Seattle",
                "state": "Washington",
                "lat": 47.6507,
                "lon": -122.3017,
                "capacity": 70138,
                "surface": "FieldTurf",
            },
            "Missouri Tigers": {
                "stadium": "Faurot Field at Memorial Stadium",
                "city": "Columbia",
                "state": "Missouri",
                "lat": 38.9356,
                "lon": -92.3341,
                "capacity": 62621,
                "surface": "Grass",
            },
            "Akron Zips": {
                "stadium": "InfoCision Stadium",
                "city": "Akron",
                "state": "Ohio",
                "lat": 41.0766,
                "lon": -81.5114,
                "capacity": 30000,
                "surface": "FieldTurf",
            },
            "Army Black Knights": {
                "stadium": "Michie Stadium",
                "city": "West Point",
                "state": "New York",
                "lat": 41.3915,
                "lon": -73.9540,
                "capacity": 38000,
                "surface": "FieldTurf",
            },
            "Fresno State Bulldogs": {
                "stadium": "Valley Children's Stadium",
                "city": "Fresno",
                "state": "California",
                "lat": 36.8138,
                "lon": -119.7428,
                "capacity": 41031,
                "surface": "FieldTurf",
            },
            "Rutgers Scarlet Knights": {
                "stadium": "SHI Stadium",
                "city": "Piscataway",
                "state": "New Jersey",
                "lat": 40.5140,
                "lon": -74.4647,
                "capacity": 52454,
                "surface": "FieldTurf",
            },
            "Miami (OH) RedHawks": {
                "stadium": "Yager Stadium",
                "city": "Oxford",
                "state": "Ohio",
                "lat": 39.5103,
                "lon": -84.7333,
                "capacity": 30012,
                "surface": "Grass",
            },
            "Charlotte 49ers": {
                "stadium": "Jerry Richardson Stadium",
                "city": "Charlotte",
                "state": "North Carolina",
                "lat": 35.3077,
                "lon": -80.7351,
                "capacity": 15314,
                "surface": "Grass",
            },
        }

        # Weather impact factors for betting
        self.weather_factors = {
            "wind_mph": {
                "high_threshold": 15,  # Strong winds affect passing/kicking
                "extreme_threshold": 25,  # Extreme winds drastically impact game
            },
            "precipitation": {
                "light_mm": 2.5,  # Light rain/snow
                "heavy_mm": 10.0,  # Heavy precipitation
            },
            "temperature": {
                "cold_f": 32,  # Freezing affects ball handling
                "hot_f": 85,  # Heat affects player performance
            },
        }

        # Load our college football games
        self.college_games = self._load_college_games()

    def _load_college_games(self) -> list[dict[str, Any]]:
        """Load college football games from our recent data pull"""
        try:
            with open("C:\\\\EQ12\\\\data\\\\sports_pull_20251010_181611.json") as f:
                data = json.load(f)

            games_found = data.get("games_found", {})
            college_games = games_found.get("college_football_2025_10_11", [])

            logger.info(f"Loaded {len(college_games)} college football games")
            return college_games

        except Exception as e:
            logger.error(f"Could not load college games: {e}")
            return []

    def get_stadium_info(self, team_name: str) -> dict[str, Any] | None:
        """Get stadium information for a team"""

        # Direct match first
        if team_name in self.stadium_database:
            return self.stadium_database[team_name]

        # Try partial matching for variations
        for db_team, stadium_info in self.stadium_database.items():
            if any(word in db_team.lower() for word in team_name.lower().split()):
                return stadium_info

        logger.warning(f"No stadium found for team: {team_name}")
        return None

    def get_weather_data(self, lat: float, lon: float, city: str,
                         state: str) -> dict[str, Any]:
        """Get current weather and forecast for stadium location"""

        weather_data = {
            "current": {},
            "forecast": {},
            "betting_impact": {},
            "data_source": "NWS + Fallback",
        }

        try:
            # Try NWS first (free, accurate for US)
            nws_url = f"https://api.weather.gov/points/{lat},{lon}"
            response = requests.get(nws_url, timeout=10)

            if response.status_code == 200:
                point_data = response.json()

                # Get current conditions
                forecast_url = point_data["properties"]["forecast"]
                forecast_response = requests.get(forecast_url, timeout=10)

                if forecast_response.status_code == 200:
                    forecast_data = forecast_response.json()
                    periods = forecast_data["properties"]["periods"]

                    if periods:
                        current_period = periods[0]
                        weather_data["current"] = {
                            "temperature_": current_period.get(
                                "temperature", 70), "wind_speed": current_period.get(
                                "windSpeed", "0 mph"), "wind_direction": current_period.get(
                                "windDirection", "N"), "conditions": current_period.get(
                                "detailedForecast", "Clear"), "short_forecast": current_period.get(
                                "shortForecast", "Clear"), }

                        weather_data["forecast"] = {
                            "periods": periods[:3]}  # Next 3 periods

                        logger.info(f"Got NWS weather for {city}, {state}")

            else:
                raise Exception("NWS API not available")

        except Exception as e:
            logger.warning(f"NWS failed for {city}, {state}: {e}")

            # Fallback to simulated data based on location and season
            weather_data = self._get_simulated_weather(lat, lon, city, state)

        # Calculate betting impact
        weather_data["betting_impact"] = self._calculate_betting_impact(weather_data)

        return weather_data

    def _get_simulated_weather(
        self, lat: float, lon: float, city: str, state: str
    ) -> dict[str, Any]:
        """Generate realistic weather simulation based on location and October conditions"""

        # October weather patterns by region
        temp_base = 65  # Default fall temperature

        # Adjust by latitude (colder up north)
        if lat > 45:  # Northern states
            temp_base = 55
        elif lat > 40:  # Mid-latitude
            temp_base = 60
        elif lat > 35:  # Southern states
            temp_base = 70
        else:  # Deep south
            temp_base = 75

        # Adjust by longitude (mountain/coastal effects)
        if -120 < lon < -100:  # Mountain West
            temp_base -= 10
        elif lon > -90:  # Eastern seaboard
            temp_base += 5

        # Simulate conditions
        import random

        random.seed(int(lat * lon * 1000))  # Deterministic "randomness"

        temp_variation = random.randint(-15, 15)
        wind_speed = random.randint(3, 18)

        conditions = ["Clear", "Partly Cloudy", "Overcast", "Light Rain"]
        condition = random.choice(conditions)

        return {
            "current": {
                "temperature_f": temp_base + temp_variation,
                "wind_speed": f"{wind_speed} mph",
                "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
                "conditions": f"{condition} conditions expected",
                "short_forecast": condition,
            },
            "forecast": {
                "periods": [
                    {
                        "name": "Game Time",
                        "temperature": temp_base + temp_variation,
                        "shortForecast": condition,
                        "detailedForecast": f"{condition} with {wind_speed} mph winds",
                    }
                ]
            },
            "data_source": "Simulated (NWS unavailable)",
        }

    def _calculate_betting_impact(self, weather_data: dict[str, Any]) -> dict[str, Any]:
        """Calculate how weather conditions impact betting angles"""

        impact = {
            "total_impact": "neutral",  # under/over impact
            "spread_impact": "neutral",  # point spread impact
            "factors": [],
            "confidence_modifier": 0.0,  # -0.2 to +0.2 adjustment
        }

        current = weather_data.get("current", {})
        temp = current.get("temperature_f", 70)
        wind_str = current.get("wind_speed", "0 mph")
        conditions = current.get("conditions", "").lower()

        # Extract wind speed
        wind_mph = 0
        try:
            wind_mph = int("".join(filter(str.isdigit, wind_str)))
        except BaseException:
            wind_mph = 0

        # Temperature impacts
        if temp < 32:
            impact["factors"].append("Cold weather - fumbles more likely")
            impact["total_impact"] = "under"
            impact["confidence_modifier"] -= 0.1
        elif temp > 85:
            impact["factors"].append("Hot weather - fatigue factor")
            impact["confidence_modifier"] -= 0.05

        # Wind impacts
        if wind_mph > 15:
            impact["factors"].append(f"Strong winds ({wind_mph} mph) - affects passing")
            impact["total_impact"] = "under"
            impact["confidence_modifier"] -= 0.15

            if wind_mph > 25:
                impact["factors"].append("Extreme winds - major game impact")
                impact["confidence_modifier"] -= 0.25

        # Precipitation impacts
        if any(word in conditions for word in ["rain", "snow", "storm"]):
            impact["factors"].append("Precipitation expected - affects ball handling")
            impact["total_impact"] = "under"
            impact["confidence_modifier"] -= 0.2

        return impact

    def analyze_all_games(self) -> dict[str, Any]:
        """Analyze stadium locations and weather for all college games"""

        analysis = {
            "timestamp": datetime.now(UTC).isoformat(),
            "games_analyzed": 0,
            "stadiums_found": 0,
            "weather_data": {},
            "betting_insights": [],
            "games": [],
        }

        logger.info("Starting comprehensive stadium and weather analysis...")

        for game in self.college_games:
            game_analysis = {
                "matchup": f"{game.get('away_team', '')} @ {game.get('home_team', '')}",
                "commence_time": game.get("commence_time", ""),
                "stadium_info": None,
                "weather_data": None,
                "betting_impact": None,
            }

            # Get stadium for home team
            home_team = game.get("home_team", "")
            stadium_info = self.get_stadium_info(home_team)

            if stadium_info:
                game_analysis["stadium_info"] = stadium_info
                analysis["stadiums_found"] += 1

                # Get weather for stadium location
                weather_data = self.get_weather_data(
                    stadium_info["lat"],
                    stadium_info["lon"],
                    stadium_info["city"],
                    stadium_info["state"],
                )

                game_analysis["weather_data"] = weather_data
                game_analysis["betting_impact"] = weather_data.get("betting_impact", {})

                # Add to weather summary
                location_key = f"{stadium_info['city']}, {stadium_info['state']}"
                analysis["weather_data"][location_key] = weather_data

                # Check for significant betting insights
                impact = weather_data.get("betting_impact", {})
                if impact.get("confidence_modifier", 0) < -0.1:
                    analysis["betting_insights"].append(
                        {
                            "game": game_analysis["matchup"],
                            "stadium": stadium_info["stadium"],
                            "insight": f"Weather favors UNDER - {', '.join(impact.get('factors', []))}",
                        }
                    )

                # Small delay to be respectful to APIs
                time.sleep(0.5)

            analysis["games"].append(game_analysis)
            analysis["games_analyzed"] += 1

        logger.info(
            f"Analysis complete: {
                analysis['games_analyzed']} games, {
                analysis['stadiums_found']} stadiums found")

        return analysis

    def save_analysis(self, analysis: dict[str, Any]) -> str:
        """Save analysis to JSON file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\\\EQ12\\\\data\\college_stadium_weather_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(analysis, f, indent=2)

            logger.info(f"Analysis saved to {filename}")
            return filename

        except Exception as e:
            logger.error(f"Could not save analysis: {e}")
            return ""


def main():
    """Run comprehensive college stadium and weather analysis"""

    print("🏈 EQ12 COLLEGE FOOTBALL STADIUM & WEATHER INTELLIGENCE")
    print("=" * 60)

    # Initialize analyzer
    analyzer = CollegeStadiumWeatherIntelligence()

    # Run analysis
    analysis = analyzer.analyze_all_games()

    # Save results
    filename = analyzer.save_analysis(analysis)

    # Display summary
    print("\n📊 ANALYSIS SUMMARY:")
    print(f"Games analyzed: {analysis['games_analyzed']}")
    print(f"Stadiums found: {analysis['stadiums_found']}")
    print(f"Weather locations: {len(analysis['weather_data'])}")

    print("\n🌤️ WEATHER INSIGHTS:")
    for insight in analysis["betting_insights"]:
        print(f"• {insight['game']}")
        print(f"  {insight['stadium']} - {insight['insight']}")

    print("\n📍 STADIUM LOCATIONS:")
    for game in analysis["games"][:10]:  # Show first 10
        if game["stadium_info"]:
            stadium = game["stadium_info"]
            weather = game["weather_data"]["current"] if game["weather_data"] else {}
            temp = weather.get("temperature_", "N/A")
            wind = weather.get("wind_speed", "N/A")

            print(f"• {game['matchup']}")
            print(f"  {stadium['stadium']} ({stadium['city']}, {stadium['state']})")
            print(f"  Weather: {temp}°F, {wind} wind")

    if filename:
        print(f"\n💾 Full analysis saved to: {filename}")

    print("\n✅ Stadium and weather analysis complete!")


if __name__ == "__main__":
    main()
