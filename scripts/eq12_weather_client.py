#!/usr/bin/env python3
"""
EQ12 OpenWeather Integration Client
Production-ready weather analysis for sports betting
Hardcoded for immediate use with your existing system
"""

import logging
import os
from datetime import UTC, datetime
from typing import Any

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - EQ12Weather - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:\\\\EQ12\\logs\\weather_client.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EQ12WeatherClient:
    """
    Production OpenWeather client for EQ12 betting system
    Optimized for NHL and sports betting analysis
    """

    def __init__(self):
        # Hardcoded for EQ12 system - get free key from openweathermap.org
        self.api_key = os.environ.get("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")

        # API endpoints
        self.onecall_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.current_url = "https://api.openweathermap.org/data/2.5/weather"
        self.air_pollution_url = "http://api.openweathermap.org/data/2.5/air_pollution"

        # NHL arena locations for quick lookup
        self.nhl_arenas = {
            "Boston": {"lat": 42.366303, "lon": -71.062228, "arena": "TD Garden"},
            "New York Rangers": {
                "lat": 40.750354,
                "lon": -73.993150,
                "arena": "Madison Square Garden",
            },
            "Montreal": {"lat": 45.496216, "lon": -73.569454, "arena": "Bell Centre"},
            "Toronto": {
                "lat": 43.643470,
                "lon": -79.379173,
                "arena": "Scotiabank Arena",
            },
            "Tampa Bay": {"lat": 27.942806, "lon": -82.451773, "arena": "Amalie Arena"},
            "Colorado": {"lat": 39.748621, "lon": -105.007679, "arena": "Ball Arena"},
            "Vegas": {"lat": 36.102743, "lon": -115.178581, "arena": "T-Mobile Arena"},
            "Seattle": {
                "lat": 47.622054,
                "lon": -122.354197,
                "arena": "Climate Pledge Arena",
            },
        }

        # Weather impact thresholds for betting analysis
        self.impact_thresholds = {
            "temperature": {"extreme_cold": 20, "extreme_hot": 85},
            "wind": {"high": 15, "extreme": 25},
            "precipitation": {"light": 0.1, "heavy": 0.5},
            "visibility": {"poor": 3, "very_poor": 1},
        }

    def get_nhl_game_weather_analysis(
        self, home_team: str, game_datetime: str | None = None
    ) -> dict[str, Any]:
        """
        Complete weather analysis for NHL games
        Includes current conditions, forecasts, and betting impact
        """
        try:
            # Get arena coordinates
            arena_info = self.nhl_arenas.get(home_team)
            if not arena_info:
                logger.warning(f"Arena not found for team: {home_team}")
                return self._get_city_weather_analysis(home_team, game_datetime)

            lat, lon = arena_info["lat"], arena_info["lon"]
            arena_name = arena_info["arena"]

            # Get comprehensive weather data
            weather_data = self._get_onecall_weather(lat, lon)
            if "error" in weather_data:
                return weather_data

            # Get air quality data
            air_quality = self._get_air_quality(lat, lon)

            # Analyze betting impact
            betting_impact = self._analyze_nhl_betting_impact(weather_data, air_quality)

            analysis = {
                "team": home_team,
                "arena": arena_name,
                "coordinates": {"lat": lat, "lon": lon},
                "timestamp": datetime.now(UTC).isoformat(),
                "game_datetime": game_datetime,
                "current_weather": weather_data.get("current", {}),
                "hourly_forecast": weather_data.get("hourly", [])[:12],  # Next 12 hours
                "daily_forecast": weather_data.get("daily", [])[:3],  # Next 3 days
                "weather_alerts": weather_data.get("alerts", []),
                "air_quality": air_quality,
                "betting_impact": betting_impact,
                "eq12_recommendations": self._get_eq12_betting_recommendations(betting_impact),
            }

            # Log analysis
            logger.info(f"Weather analysis complete for {home_team} at {arena_name}")
            logger.info(
                f"Betting Impact: {betting_impact['impact_level']} ({betting_impact['impact_score']}/10)"
            )

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing weather for {home_team}: {e!s}")
            return {"error": f"Weather analysis failed: {e!s}"}

    def _get_onecall_weather(self, lat: float, lon: float) -> dict[str, Any]:
        """Get comprehensive weather data from One Call API 3.0"""

        if self.api_key == "YOUR_API_KEY_HERE":
            logger.warning("OpenWeather API key not configured")
            return {"error": "API key required - get free key from openweathermap.org"}

        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "imperial",
                "exclude": "minutely",  # Skip minutely data to save API calls
            }

            response = requests.get(self.onecall_url, params=params, timeout=10)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"OneCall API request failed: {e!s}")
            return {"error": f"Weather API request failed: {e!s}"}

    def _get_air_quality(self, lat: float, lon: float) -> dict[str, Any]:
        """Get air quality data for player performance analysis"""

        try:
            params = {"lat": lat, "lon": lon, "appid": self.api_key}

            response = requests.get(self.air_pollution_url, params=params, timeout=10)
            response.raise_for_status()

            air_data = response.json()

            # Simplify air quality data
            if air_data.get("list"):
                aqi_data = air_data["list"][0]
                return {
                    "aqi": aqi_data.get("main", {}).get("aqi", 0),
                    "aqi_description": self._get_aqi_description(
                        aqi_data.get("main", {}).get("aqi", 0)
                    ),
                    "components": aqi_data.get("components", {}),
                    "timestamp": datetime.fromtimestamp(aqi_data.get("dt", 0), UTC).isoformat(),
                }

            return {"aqi": 0, "aqi_description": "Data unavailable"}

        except Exception as e:
            logger.warning(f"Air quality data unavailable: {e!s}")
            return {"aqi": 0, "aqi_description": "Data unavailable"}

    def _analyze_nhl_betting_impact(self, weather_data: dict, air_quality: dict) -> dict[str, Any]:
        """Analyze weather impact specifically for NHL betting"""

        current = weather_data.get("current", {})
        alerts = weather_data.get("alerts", [])

        # Extract key weather metrics
        temp = current.get("temp", 70)
        feels_like = current.get("feels_like", temp)
        humidity = current.get("humidity", 50)
        wind_speed = current.get("wind_speed", 0)
        visibility = current.get("visibility", 10000) / 1609.34  # Convert to miles
        precipitation = 0

        # Check for precipitation in forecast
        if "rain" in current:
            precipitation = current["rain"].get("1h", 0) / 25.4  # Convert to inches
        elif "snow" in current:
            precipitation = current["snow"].get("1h", 0) / 25.4

        # Calculate impact score (0-10 scale)
        impact_score = 0
        impact_factors = []

        # Temperature impact (indoor NHL games less affected, but travel/fan attendance matters)
        if temp < self.impact_thresholds["temperature"]["extreme_cold"]:
            impact_score += 1
            impact_factors.append(f"Extreme cold: {temp}°F - Travel disruptions likely")
        elif temp > self.impact_thresholds["temperature"]["extreme_hot"]:
            impact_score += 1
            impact_factors.append(f"Extreme heat: {temp}°F - Fan comfort affected")

        # Wind impact (affects travel, outdoor activities)
        if wind_speed > self.impact_thresholds["wind"]["extreme"]:
            impact_score += 2
            impact_factors.append(f"Extreme wind: {wind_speed} mph - Flight delays possible")
        elif wind_speed > self.impact_thresholds["wind"]["high"]:
            impact_score += 1
            impact_factors.append(f"High wind: {wind_speed} mph - Minor travel impact")

        # Precipitation impact (major factor for travel and attendance)
        if precipitation > self.impact_thresholds["precipitation"]["heavy"]:
            impact_score += 3
            impact_factors.append(
                f'Heavy precipitation: {precipitation:.1f}" - Major travel disruption'
            )
        elif precipitation > self.impact_thresholds["precipitation"]["light"]:
            impact_score += 1
            impact_factors.append(
                f'Light precipitation: {precipitation:.1f}" - Minor travel impact'
            )

        # Visibility impact
        if visibility < self.impact_thresholds["visibility"]["very_poor"]:
            impact_score += 3
            impact_factors.append(
                f"Very poor visibility: {visibility:.1f} miles - Major disruptions"
            )
        elif visibility < self.impact_thresholds["visibility"]["poor"]:
            impact_score += 2
            impact_factors.append(f"Poor visibility: {visibility:.1f} miles - Travel delays likely")

        # Weather alerts (high impact)
        for alert in alerts:
            impact_score += 2
            impact_factors.append(f"Weather Alert: {alert.get('event', 'Unknown')}")

        # Air quality impact (affects player performance)
        aqi = air_quality.get("aqi", 0)
        if aqi >= 4:  # Unhealthy
            impact_score += 2
            impact_factors.append(
                f"Poor air quality (AQI {aqi}) - Player performance may be affected"
            )
        elif aqi >= 3:  # Moderate
            impact_score += 1
            impact_factors.append(f"Moderate air quality (AQI {aqi}) - Minor performance impact")

        # Cap impact score at 10
        impact_score = min(impact_score, 10)

        # Determine impact level
        if impact_score >= 7:
            impact_level = "CRITICAL"
        elif impact_score >= 5:
            impact_level = "HIGH"
        elif impact_score >= 3:
            impact_level = "MEDIUM"
        elif impact_score >= 1:
            impact_level = "LOW"
        else:
            impact_level = "MINIMAL"

        return {
            "impact_score": impact_score,
            "impact_level": impact_level,
            "impact_factors": impact_factors,
            "weather_metrics": {
                "temperature": temp,
                "feels_like": feels_like,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "visibility": visibility,
                "precipitation": precipitation,
                "air_quality_index": aqi,
            },
        }

    def _get_eq12_betting_recommendations(self, betting_impact: dict) -> dict[str, Any]:
        """Get specific betting recommendations for EQ12 system"""

        impact_level = betting_impact["impact_level"]
        betting_impact["impact_score"]

        recommendations = {
            "overall_strategy": "",
            "game_props": [],
            "player_props": [],
            "risk_management": [],
            "confidence_adjustment": 0,
        }

        if impact_level == "CRITICAL":
            recommendations.update(
                {
                    "overall_strategy": "AVOID BETTING - High postponement/delay risk",
                    "game_props": [
                        "Avoid Over/Under bets",
                        "Consider postponement insurance",
                    ],
                    "player_props": [
                        "Avoid all player props",
                        "High variance expected",
                    ],
                    "risk_management": [
                        "Reduce position sizes by 75%",
                        "Monitor for cancellations",
                    ],
                    "confidence_adjustment": -50,  # Reduce confidence by 50%
                }
            )

        elif impact_level == "HIGH":
            recommendations.update(
                {
                    "overall_strategy": "CAUTIOUS BETTING - Significant weather impact expected",
                    "game_props": [
                        "Lower scoring games likely",
                        "Consider Under bets",
                        "Avoid period props",
                    ],
                    "player_props": [
                        "Reduce player prop confidence",
                        "Focus on defensive stats",
                    ],
                    "risk_management": [
                        "Reduce position sizes by 50%",
                        "Set tight stop losses",
                    ],
                    "confidence_adjustment": -30,
                }
            )

        elif impact_level == "MEDIUM":
            recommendations.update(
                {
                    "overall_strategy": "STANDARD BETTING - Monitor weather conditions",
                    "game_props": [
                        "Slight scoring impact possible",
                        "Normal game flow expected",
                    ],
                    "player_props": [
                        "Standard player prop confidence",
                        "Monitor travel delays",
                    ],
                    "risk_management": [
                        "Normal position sizes",
                        "Standard risk management",
                    ],
                    "confidence_adjustment": -15,
                }
            )

        elif impact_level == "LOW":
            recommendations.update(
                {
                    "overall_strategy": "NORMAL BETTING - Minimal weather impact",
                    "game_props": [
                        "Weather unlikely to affect scoring",
                        "Standard game analysis",
                    ],
                    "player_props": [
                        "Full confidence in player props",
                        "No weather adjustments needed",
                    ],
                    "risk_management": [
                        "Normal position sizes",
                        "Standard strategies apply",
                    ],
                    "confidence_adjustment": -5,
                }
            )

        else:  # MINIMAL
            recommendations.update(
                {
                    "overall_strategy": "OPTIMAL BETTING CONDITIONS - No weather concerns",
                    "game_props": [
                        "Perfect conditions for analysis",
                        "High confidence bets",
                    ],
                    "player_props": [
                        "Maximum confidence in player props",
                        "Weather advantage negligible",
                    ],
                    "risk_management": [
                        "Full position sizes acceptable",
                        "Standard risk only",
                    ],
                    "confidence_adjustment": 0,
                }
            )

        return recommendations

    def _get_city_weather_analysis(
        self, city: str, game_datetime: str | None = None
    ) -> dict[str, Any]:
        """Fallback method for non-NHL teams or custom locations"""

        try:
            # Get city coordinates
            geo_params = {"q": city, "limit": 1, "appid": self.api_key}
            geo_response = requests.get(self.geocoding_url, params=geo_params, timeout=10)
            geo_response.raise_for_status()

            geo_data = geo_response.json()
            if not geo_data:
                return {"error": f"Location not found: {city}"}

            location = geo_data[0]
            lat, lon = location["lat"], location["lon"]

            # Get weather data
            weather_data = self._get_onecall_weather(lat, lon)
            if "error" in weather_data:
                return weather_data

            # Get air quality
            air_quality = self._get_air_quality(lat, lon)

            # Analyze impact
            betting_impact = self._analyze_nhl_betting_impact(weather_data, air_quality)

            return {
                "city": city,
                "coordinates": {"lat": lat, "lon": lon},
                "timestamp": datetime.now(UTC).isoformat(),
                "game_datetime": game_datetime,
                "current_weather": weather_data.get("current", {}),
                "hourly_forecast": weather_data.get("hourly", [])[:12],
                "weather_alerts": weather_data.get("alerts", []),
                "air_quality": air_quality,
                "betting_impact": betting_impact,
                "eq12_recommendations": self._get_eq12_betting_recommendations(betting_impact),
            }

        except Exception as e:
            logger.error(f"Error analyzing weather for {city}: {e!s}")
            return {"error": f"Weather analysis failed: {e!s}"}

    def _get_aqi_description(self, aqi: int) -> str:
        """Convert AQI number to description"""
        descriptions = {
            1: "Good - No health concerns",
            2: "Fair - Minor health concerns for sensitive individuals",
            3: "Moderate - Health concerns for sensitive groups",
            4: "Poor - Health warnings, exercise caution",
            5: "Very Poor - Health alert, avoid outdoor activities",
        }
        return descriptions.get(aqi, "Unknown air quality")

    def get_weather_summary_for_betting(self, teams: list[str]) -> dict[str, Any]:
        """Get weather summary for multiple teams/games for betting dashboard"""

        summary = {
            "timestamp": datetime.now(UTC).isoformat(),
            "teams_analyzed": len(teams),
            "weather_impacts": {},
            "high_risk_games": [],
            "optimal_betting_games": [],
            "overall_weather_risk": "LOW",
        }

        high_risk_count = 0

        for team in teams:
            analysis = self.get_nhl_game_weather_analysis(team)

            if "error" not in analysis:
                impact = analysis["betting_impact"]["impact_level"]
                summary["weather_impacts"][team] = {
                    "impact_level": impact,
                    "impact_score": analysis["betting_impact"]["impact_score"],
                    "arena": analysis.get("arena", "Unknown"),
                    "recommendation": analysis["eq12_recommendations"]["overall_strategy"],
                }

                if impact in ["HIGH", "CRITICAL"]:
                    summary["high_risk_games"].append(team)
                    high_risk_count += 1
                elif impact == "MINIMAL":
                    summary["optimal_betting_games"].append(team)

        # Calculate overall risk
        risk_percentage = (high_risk_count / len(teams)) * 100 if teams else 0
        if risk_percentage > 50:
            summary["overall_weather_risk"] = "HIGH"
        elif risk_percentage > 25:
            summary["overall_weather_risk"] = "MEDIUM"

        return summary


def main():
    """Demo the EQ12 Weather Client"""

    print("🌤️ EQ12 OPENWEATHER CLIENT - DEMO")
    print("=" * 50)

    client = EQ12WeatherClient()

    # Test with sample NHL teams
    test_teams = ["Boston", "Colorado", "Vegas"]

    print(f"\n📊 Testing weather analysis for {len(test_teams)} teams...")

    for team in test_teams:
        print(f"\n🏒 Analyzing weather for {team}...")

        analysis = client.get_nhl_game_weather_analysis(team)

        if "error" in analysis:
            print(f"   ❌ Error: {analysis['error']}")
        else:
            impact = analysis["betting_impact"]
            temp = analysis["current_weather"].get("temp", "N/A")

            print(f"   🌡️ Temperature: {temp}°F")
            print(f"   ⚠️ Impact Level: {impact['impact_level']} ({impact['impact_score']}/10)")
            print(f"   🎲 Betting Strategy: {analysis['eq12_recommendations']['overall_strategy']}")

    # Test weather summary
    print("\n📈 WEATHER SUMMARY FOR BETTING:")
    summary = client.get_weather_summary_for_betting(test_teams)
    print(f"   🎯 Overall Risk Level: {summary['overall_weather_risk']}")
    print(f"   ⚠️ High Risk Games: {len(summary['high_risk_games'])}")
    print(f"   ✅ Optimal Betting Games: {len(summary['optimal_betting_games'])}")

    print("\n✅ EQ12 Weather Client ready for integration!")
    print("   Setup: Set OPENWEATHER_API_KEY environment variable")
    print("   Free tier: 1,000 calls/day - perfect for EQ12 betting needs")


if __name__ == "__main__":
    main()
