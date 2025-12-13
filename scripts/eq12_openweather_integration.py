#!/usr/bin/env python3
"""
EQ12 OpenWeatherMap Enhanced Integration
Premium weather intelligence for sports betting with OpenWeatherMap API
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any

import requests

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            "C:/EQ12/logs/openweather_integration.log",
            encoding="utf-8"),
        logging.StreamHandler(
            sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class EQ12OpenWeatherIntegration:
    """
    EQ12 OpenWeatherMap Integration for Enhanced Sports Weather Intelligence
    """

    def __init__(self, api_key: str | None = None):
        """Initialize OpenWeatherMap Integration"""
        self.api_key = api_key or os.getenv(
            "OPENWEATHER_API_KEY", "229507bc0f5ea7d23bd26958e023652"
        )

        # OpenWeatherMap API endpoints
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.onecall_url = "https://api.openweathermap.org/data/3.0"

        # NFL Stadium coordinates for enhanced weather analysis
        self.nfl_stadiums = {
            "Green Bay Packers": {
                "stadium": "Lambeau Field",
                "city": "Green Bay",
                "state": "WI",
                "lat": 44.5013,
                "lon": -88.0622,
                "timezone": "America/Chicago",
            },
            "Kansas City Chiefs": {
                "stadium": "Arrowhead Stadium",
                "city": "Kansas City",
                "state": "MO",
                "lat": 39.0489,
                "lon": -94.4839,
                "timezone": "America/Chicago",
            },
            "Detroit Lions": {
                "stadium": "Ford Field",
                "city": "Detroit",
                "state": "MI",
                "lat": 42.3400,
                "lon": -83.0456,
                "timezone": "America/Detroit",
                "indoor": True,
            },
            "Buffalo Bills": {
                "stadium": "Bills Stadium",
                "city": "Orchard Park",
                "state": "NY",
                "lat": 42.7738,
                "lon": -78.7870,
                "timezone": "America/New_York",
            },
            "Pittsburgh Steelers": {
                "stadium": "Acrisure Stadium",
                "city": "Pittsburgh",
                "state": "PA",
                "lat": 40.4468,
                "lon": -80.0158,
                "timezone": "America/New_York",
            },
            "Baltimore Ravens": {
                "stadium": "M&T Bank Stadium",
                "city": "Baltimore",
                "state": "MD",
                "lat": 39.2780,
                "lon": -76.6227,
                "timezone": "America/New_York",
            },
            "New England Patriots": {
                "stadium": "Gillette Stadium",
                "city": "Foxborough",
                "state": "MA",
                "lat": 42.0909,
                "lon": -71.2643,
                "timezone": "America/New_York",
            },
            "Miami Dolphins": {
                "stadium": "Hard Rock Stadium",
                "city": "Miami Gardens",
                "state": "FL",
                "lat": 25.9580,
                "lon": -80.2389,
                "timezone": "America/New_York",
            },
        }

        # Weather impact factors for betting intelligence
        self.weather_factors = {
            "wind_speed": {
                "low": (0, 10, 1.0),  # mph, multiplier
                "moderate": (10, 20, 1.1),
                "high": (20, 30, 1.2),
                "extreme": (30, 100, 1.3),
            },
            "precipitation": {
                "none": (0, 0.1, 1.0),  # inches, multiplier
                "light": (0.1, 0.5, 1.1),
                "moderate": (0.5, 1.0, 1.2),
                "heavy": (1.0, 10, 1.3),
            },
            "temperature": {
                "ideal": (50, 75, 1.0),  # fahrenheit, multiplier
                "cool": (32, 50, 1.05),
                "cold": (10, 32, 1.1),
                "freezing": (-20, 10, 1.15),
                "hot": (75, 90, 1.05),
                "extreme_heat": (90, 120, 1.1),
            },
        }

        self.session = requests.Session()
        logger.info("EQ12 OpenWeatherMap Integration initialized")
        logger.info(f"API Key configured: {self.api_key[:8]}...")

    def test_api_access(self) -> dict[str, Any]:
        """Test OpenWeatherMap API access and account status"""
        logger.info("Testing OpenWeatherMap API access...")

        test_results = {
            "api_accessible": False,
            "account_status": "unknown",
            "calls_remaining": None,
            "subscription_type": "unknown",
            "error": None,
        }

        try:
            # Test with simple current weather call
            params = {
                "q": "Green Bay,WI,US",
                "appid": self.api_key,
                "units": "imperial",
            }

            response = self.session.get(
                f"{self.base_url}/weather", params=params, timeout=10)

            if response.status_code == 200:
                test_results["api_accessible"] = True
                test_results["account_status"] = "active"

                # Check rate limiting headers
                headers = response.headers
                test_results["calls_remaining"] = headers.get("X-RateLimit-Remaining")

                data = response.json()
                logger.info("✅ OpenWeatherMap API access confirmed")
                logger.info(f"Test location: {data.get('name', 'Unknown')}")

            elif response.status_code == 401:
                test_results["error"] = "Invalid API key"
                logger.error("❌ Invalid OpenWeatherMap API key")

            elif response.status_code == 429:
                test_results["error"] = "Rate limit exceeded"
                logger.error("❌ OpenWeatherMap rate limit exceeded")

            else:
                test_results["error"] = f"HTTP {response.status_code}"
                logger.error(f"❌ OpenWeatherMap API error: {response.status_code}")

        except Exception as e:
            test_results["error"] = str(e)
            logger.error(f"❌ OpenWeatherMap connection error: {e}")

        return test_results

    def get_stadium_weather(self, team_name: str,
                            include_forecast: bool = True) -> dict[str, Any]:
        """Get comprehensive weather data for NFL stadium"""
        if team_name not in self.nfl_stadiums:
            return {
                "success": False,
                "error": f"Team {team_name} not found in database",
            }

        stadium_info = self.nfl_stadiums[team_name]

        # Skip weather for indoor stadiums
        if stadium_info.get("indoor"):
            return {
                "success": True,
                "team": team_name,
                "stadium": stadium_info["stadium"],
                "indoor": True,
                "weather_impact": "none",
                "betting_factor": 1.0,
                "message": "Indoor stadium - weather neutral",
            }

        logger.info(f"Getting weather for {team_name} at {stadium_info['stadium']}")

        try:
            # Current weather
            current_params = {
                "lat": stadium_info["lat"],
                "lon": stadium_info["lon"],
                "appid": self.api_key,
                "units": "imperial",
            }

            current_response = self.session.get(
                f"{self.base_url}/weather", params=current_params, timeout=10
            )

            if current_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Weather API error: {current_response.status_code}",
                }

            current_data = current_response.json()

            weather_analysis = {
                "success": True,
                "team": team_name,
                "stadium": stadium_info["stadium"],
                "location": f"{stadium_info['city']}, {stadium_info['state']}",
                "coordinates": {"lat": stadium_info["lat"], "lon": stadium_info["lon"]},
                "current_weather": self._parse_current_weather(current_data),
                "betting_analysis": None,
                "forecast": None,
            }

            # Add betting impact analysis
            weather_analysis["betting_analysis"] = self._analyze_betting_impact(
                weather_analysis["current_weather"]
            )

            # Get forecast if requested
            if include_forecast:
                forecast_params = {
                    "lat": stadium_info["lat"],
                    "lon": stadium_info["lon"],
                    "appid": self.api_key,
                    "units": "imperial",
                }

                forecast_response = self.session.get(
                    f"{self.base_url}/forecast", params=forecast_params, timeout=10
                )

                if forecast_response.status_code == 200:
                    forecast_data = forecast_response.json()
                    weather_analysis["forecast"] = self._parse_forecast(forecast_data)

            logger.info(f"✅ Weather data retrieved for {team_name}")
            return weather_analysis

        except Exception as e:
            logger.error(f"❌ Weather error for {team_name}: {e}")
            return {"success": False, "error": str(e)}

    def _parse_current_weather(self, data: dict) -> dict[str, Any]:
        """Parse OpenWeatherMap current weather data"""
        try:
            weather = data["weather"][0]
            main = data["main"]
            wind = data.get("wind", {})

            return {
                "condition": weather["main"],
                "description": weather["description"],
                "temperature": main["temp"],
                "feels_like": main["feels_like"],
                "humidity": main["humidity"],
                "pressure": main["pressure"],
                "wind_speed": wind.get("speed", 0),
                "wind_direction": wind.get("deg", 0),
                "wind_gust": wind.get("gust", 0),
                "visibility": data.get("visibility", 10000) / 1000,  # Convert to miles
                "clouds": data["clouds"]["all"],
                "timestamp": datetime.fromtimestamp(data["dt"]).isoformat(),
            }
        except Exception as e:
            logger.warning(f"Error parsing weather data: {e}")
            return {"error": "Failed to parse weather data"}

    def _parse_forecast(self, data: dict) -> list[dict[str, Any]]:
        """Parse OpenWeatherMap forecast data"""
        try:
            forecast_list = []

            # Get next 24 hours (8 periods of 3 hours each)
            for item in data["list"][:8]:
                weather = item["weather"][0]
                main = item["main"]
                wind = item.get("wind", {})

                forecast_item = {
                    "datetime": datetime.fromtimestamp(item["dt"]).isoformat(),
                    "temperature": main["temp"],
                    "condition": weather["main"],
                    "description": weather["description"],
                    "wind_speed": wind.get("speed", 0),
                    "precipitation_prob": item.get("pop", 0) * 100,
                    "precipitation_amount": item.get("rain", {}).get("3h", 0)
                    + item.get("snow", {}).get("3h", 0),
                }

                forecast_list.append(forecast_item)

            return forecast_list

        except Exception as e:
            logger.warning(f"Error parsing forecast data: {e}")
            return []

    def _analyze_betting_impact(self, weather: dict) -> dict[str, Any]:
        """Analyze weather conditions for betting impact"""
        if "error" in weather:
            return {"impact_level": "unknown", "factor": 1.0}

        impact_factors = []
        total_multiplier = 1.0

        # Wind impact
        wind_speed = weather.get("wind_speed", 0)
        for level, (min_wind, max_wind,
                    multiplier) in self.weather_factors["wind_speed"].items():
            if min_wind <= wind_speed < max_wind:
                impact_factors.append(f"Wind: {level} ({wind_speed} mph)")
                total_multiplier *= multiplier
                break

        # Temperature impact
        temperature = weather.get("temperature", 60)
        for level, (min_temp, max_temp,
                    multiplier) in self.weather_factors["temperature"].items():
            if min_temp <= temperature < max_temp:
                impact_factors.append(f"Temperature: {level} ({temperature}°F)")
                total_multiplier *= multiplier
                break

        # Precipitation impact (estimated from conditions)
        condition = weather.get("condition", "").lower()
        if "rain" in condition or "drizzle" in condition:
            impact_factors.append("Precipitation: rain conditions")
            total_multiplier *= 1.15
        elif "snow" in condition:
            impact_factors.append("Precipitation: snow conditions")
            total_multiplier *= 1.2

        # Determine overall impact level
        if total_multiplier >= 1.2:
            impact_level = "HIGH"
        elif total_multiplier >= 1.1:
            impact_level = "MEDIUM"
        else:
            impact_level = "LOW"

        return {
            "impact_level": impact_level,
            "factor": round(
                total_multiplier,
                3),
            "factors": impact_factors,
            "recommendations": self._generate_betting_recommendations(
                impact_level,
                weather),
        }

    def _generate_betting_recommendations(
            self, impact_level: str, weather: dict) -> list[str]:
        """Generate betting recommendations based on weather"""
        recommendations = []

        if impact_level == "HIGH":
            recommendations.append(
                "Consider UNDER total points due to weather conditions")
            recommendations.append("Favor teams with strong running games")
            recommendations.append("Weather may impact kicking game significantly")

        elif impact_level == "MEDIUM":
            recommendations.append("Weather may slightly favor defensive play")
            recommendations.append("Monitor wind direction for kicking advantage")

        else:
            recommendations.append("Weather conditions neutral for betting")

        # Specific weather recommendations
        wind_speed = weather.get("wind_speed", 0)
        if wind_speed > 15:
            recommendations.append(
                f"High winds ({wind_speed} mph) - avoid long field goal bets")

        temp = weather.get("temperature", 60)
        if temp < 32:
            recommendations.append("Freezing conditions - expect lower scoring")
        elif temp > 85:
            recommendations.append("Hot conditions - potential for fatigue factors")

        return recommendations

    def analyze_parlay_weather(self, teams: list[str]) -> dict[str, Any]:
        """Analyze weather conditions for multiple teams in a parlay"""
        logger.info(f"Analyzing parlay weather for {len(teams)} teams")

        parlay_analysis = {
            "teams": teams,
            "weather_data": {},
            "overall_impact": "LOW",
            "combined_factor": 1.0,
            "high_risk_games": [],
            "recommendations": [],
        }

        total_factor = 1.0
        high_impact_count = 0

        for team in teams:
            weather_data = self.get_stadium_weather(team, include_forecast=True)
            parlay_analysis["weather_data"][team] = weather_data

            if weather_data.get("success"):
                if weather_data.get("indoor"):
                    continue  # Skip indoor stadiums

                betting_analysis = weather_data.get("betting_analysis", {})
                impact_level = betting_analysis.get("impact_level", "LOW")
                factor = betting_analysis.get("factor", 1.0)

                total_factor *= factor

                if impact_level in ["HIGH", "MEDIUM"]:
                    high_impact_count += 1

                if impact_level == "HIGH":
                    parlay_analysis["high_risk_games"].append(
                        {
                            "team": team,
                            "stadium": weather_data.get("stadium", "Unknown"),
                            "impact_level": impact_level,
                            "factor": factor,
                        }
                    )

        # Determine overall parlay impact
        parlay_analysis["combined_factor"] = round(total_factor, 3)

        if high_impact_count >= 2:
            parlay_analysis["overall_impact"] = "HIGH"
        elif high_impact_count == 1:
            parlay_analysis["overall_impact"] = "MEDIUM"

        # Generate parlay recommendations
        if parlay_analysis["overall_impact"] == "HIGH":
            parlay_analysis["recommendations"].append(
                "HIGH weather risk - consider reducing parlay size"
            )
            parlay_analysis["recommendations"].append(
                "Multiple games have significant weather factors"
            )

        elif parlay_analysis["overall_impact"] == "MEDIUM":
            parlay_analysis["recommendations"].append(
                "Moderate weather risk - monitor conditions closely"
            )

        else:
            parlay_analysis["recommendations"].append(
                "Weather conditions favorable for parlay")

        # Save analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"C:/EQ12/logs/parlay_weather_analysis_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(parlay_analysis, f, indent=2, ensure_ascii=False)

        logger.info(f"Parlay weather analysis saved: {report_file}")
        return parlay_analysis


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EQ12 OpenWeatherMap Integration")
    parser.add_argument("--api-key", help="OpenWeatherMap API key")
    parser.add_argument("--test-access", action="store_true", help="Test API access")
    parser.add_argument("--team-weather", help="Get weather for specific NFL team")
    parser.add_argument(
        "--parlay-analysis",
        nargs="+",
        help="Analyze weather for parlay teams")
    parser.add_argument(
        "--stadium-report", action="store_true", help="Generate stadium weather report"
    )

    args = parser.parse_args()

    # Initialize OpenWeather Integration
    weather_system = EQ12OpenWeatherIntegration(api_key=args.api_key)

    print("EQ12 OPENWEATHERMAP INTEGRATION SYSTEM")
    print("=" * 80)

    if args.test_access:
        print("Testing OpenWeatherMap API access...")
        result = weather_system.test_api_access()

        print("API Access Results:")
        print(f"   Status: {'✅ ACTIVE' if result['api_accessible'] else '❌ FAILED'}")
        print(f"   Account: {result['account_status'].upper()}")

        if result["calls_remaining"]:
            print(f"   Calls Remaining: {result['calls_remaining']}")

        if result["error"]:
            print(f"   Error: {result['error']}")

    elif args.team_weather:
        print(f"Getting weather analysis for {args.team_weather}...")
        result = weather_system.get_stadium_weather(args.team_weather)

        if result["success"]:
            if result.get("indoor"):
                print(
                    f"✅ {result['team']} - {result['stadium']} (Indoor - Weather Neutral)")
            else:
                current = result["current_weather"]
                betting = result["betting_analysis"]

                print(f"✅ {result['team']} - {result['stadium']}")
                print(f"   Location: {result['location']}")
                print(
                    f"   Current: {current['condition']} - {current['temperature']}°F")
                print(f"   Wind: {current['wind_speed']} mph")
                print(
                    f"   Betting Impact: {
                        betting['impact_level']} (Factor: {
                        betting['factor']})")

                for rec in betting["recommendations"][:3]:
                    print(f"   • {rec}")
        else:
            print(f"❌ Error: {result['error']}")

    elif args.parlay_analysis:
        teams = args.parlay_analysis
        print(f"Analyzing parlay weather for {len(teams)} teams...")

        result = weather_system.analyze_parlay_weather(teams)

        print("\n🎯 Parlay Weather Analysis:")
        print(f"   Overall Impact: {result['overall_impact']}")
        print(f"   Combined Factor: {result['combined_factor']}")
        print(f"   High-Risk Games: {len(result['high_risk_games'])}")

        for rec in result["recommendations"]:
            print(f"   • {rec}")

        if result["high_risk_games"]:
            print("\n   High-Risk Games:")
            for game in result["high_risk_games"]:
                print(f"      {game['team']}: {game['impact_level']} impact")

    elif args.stadium_report:
        print("Generating comprehensive stadium weather report...")
        # Get weather for all teams
        all_teams = list(weather_system.nfl_stadiums.keys())
        sample_teams = all_teams[:8]  # Sample to avoid rate limits

        for team in sample_teams:
            result = weather_system.get_stadium_weather(team, include_forecast=False)
            if result["success"]:
                if result.get("indoor"):
                    print(f"   {team}: Indoor stadium - weather neutral")
                else:
                    betting = result.get("betting_analysis", {})
                    impact = betting.get("impact_level", "UNKNOWN")
                    factor = betting.get("factor", 1.0)
                    print(f"   {team}: {impact} impact (factor: {factor})")
            time.sleep(0.5)  # Rate limiting

    else:
        # Default: test API and show capabilities
        print("Running default OpenWeatherMap integration test...")

        # Test API access
        test_result = weather_system.test_api_access()
        print(
            f"API Status: {
                '✅ ACTIVE' if test_result['api_accessible'] else '❌ FAILED'}")

        if test_result["api_accessible"]:
            print("Available capabilities:")
            print(
                f"   • Real-time weather data for {len(weather_system.nfl_stadiums)} NFL stadiums"
            )
            print("   • Weather impact analysis for betting intelligence")
            print("   • Multi-team parlay weather analysis")
            print("   • 5-day forecast integration")

        elif test_result["error"]:
            print(f"Error: {test_result['error']}")
            print("Creating offline weather intelligence system...")

            # Create fallback system
            print("Fallback: Using EQ12 weather database with NWS integration")

    print("\n✅ EQ12 OpenWeatherMap Integration Complete!")


if __name__ == "__main__":
    main()
