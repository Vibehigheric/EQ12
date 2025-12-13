#!/usr/bin/env python3
"""
EQ12 National Weather Service (NWS) API Integration
FREE government weather data - perfect complement to OpenWeather
Completely free with generous rate limits for the EQ12 betting system
"""

import logging
from datetime import UTC, datetime
from typing import Any

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - EQ12NWS - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:\\\\EQ12\\logs\\nws_weather_client.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EQ12NWSWeatherClient:
    """
    National Weather Service API client for EQ12 betting system
    100% FREE with no API key required - perfect for unlimited use
    """

    def __init__(self):
        # NWS API requires User-Agent header for identification
        self.base_url = "https://api.weather.gov"
        self.headers = {
            "User-Agent": "EQ12-Betting-System (support@eq12.com) - Sports weather analysis"}

        # NHL arena coordinates for quick lookup
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
            "Chicago": {"lat": 41.880658, "lon": -87.674120, "arena": "United Center"},
            "Detroit": {
                "lat": 42.341483,
                "lon": -83.055325,
                "arena": "Little Caesars Arena",
            },
            "Pittsburgh": {
                "lat": 40.439400,
                "lon": -79.989052,
                "arena": "PPG Paints Arena",
            },
            "Washington": {
                "lat": 38.898056,
                "lon": -77.020833,
                "arena": "Capital One Arena",
            },
        }

        # Weather impact scoring for betting analysis
        self.impact_thresholds = {
            "temperature": {"extreme_cold": 10, "very_cold": 20, "cold": 32},
            "wind": {"high": 15, "very_high": 25, "extreme": 35},
            "precipitation": {"light": 0.1, "moderate": 0.3, "heavy": 0.7},
            "visibility": {"poor": 3, "very_poor": 1},
        }

    def get_nhl_weather_analysis(
        self, team: str, game_datetime: str | None = None
    ) -> dict[str, Any]:
        """
        Complete NWS weather analysis for NHL games
        Uses free government data with no rate limits
        """
        try:
            # Get arena coordinates
            arena_info = self.nhl_arenas.get(team)
            if not arena_info:
                logger.warning(f"Arena not found for team: {team}")
                return {"error": f"Team {team} not found in NHL arena database"}

            lat, lon = arena_info["lat"], arena_info["lon"]
            arena_name = arena_info["arena"]

            # Get NWS point data for coordinates
            point_data = self._get_point_data(lat, lon)
            if "error" in point_data:
                return point_data

            # Get current weather observations
            current_weather = self._get_current_observations(point_data)

            # Get weather forecast
            forecast_data = self._get_forecast_data(point_data)

            # Get weather alerts
            alerts = self._get_weather_alerts(lat, lon)

            # Analyze betting impact
            betting_impact = self._analyze_nws_betting_impact(
                current_weather, forecast_data, alerts
            )

            analysis = {
                "team": team,
                "arena": arena_name,
                "coordinates": {
                    "lat": lat,
                    "lon": lon},
                "timestamp": datetime.now(UTC).isoformat(),
                "game_datetime": game_datetime,
                "nws_office": point_data.get(
                    "properties",
                    {}).get(
                    "forecastOffice",
                    "Unknown"),
                "current_weather": current_weather,
                "forecast": forecast_data,
                "weather_alerts": alerts,
                "betting_impact": betting_impact,
                "eq12_recommendations": self._get_eq12_nws_recommendations(betting_impact),
                "data_source": "National Weather Service (FREE)",
            }

            # Log analysis
            logger.info(f"NWS weather analysis complete for {team} at {arena_name}")
            logger.info(
                f"Betting Impact: {
                    betting_impact['impact_level']} ({
                    betting_impact['impact_score']}/10)")

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing NWS weather for {team}: {e!s}")
            return {"error": f"NWS weather analysis failed: {e!s}"}

    def _get_point_data(self, lat: float, lon: float) -> dict[str, Any]:
        """Get NWS point metadata for coordinates"""

        try:
            url = f"{self.base_url}/points/{lat:.4f},{lon:.4f}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"NWS point data request failed: {e!s}")
            return {"error": f"NWS point data request failed: {e!s}"}

    def _get_current_observations(self, point_data: dict) -> dict[str, Any]:
        """Get current weather observations from nearest NWS station"""

        try:
            properties = point_data.get("properties", {})
            stations_url = properties.get("observationStations")

            if not stations_url:
                return {"error": "No observation stations available"}

            # Get list of stations
            stations_response = requests.get(
                stations_url, headers=self.headers, timeout=10)
            stations_response.raise_for_status()
            stations_data = stations_response.json()

            # Get latest observation from first available station
            features = stations_data.get("features", [])
            if not features:
                return {"error": "No observation stations found"}

            for station_feature in features[:3]:  # Try up to 3 stations
                try:
                    station_id = station_feature["properties"]["stationIdentifier"]
                    obs_url = f"{
                        self.base_url}/stations/{station_id}/observations/latest"

                    obs_response = requests.get(
                        obs_url, headers=self.headers, timeout=10)
                    obs_response.raise_for_status()
                    obs_data = obs_response.json()

                    # Parse observation data
                    props = obs_data.get("properties", {})

                    return {
                        "station": station_id,
                        "timestamp": props.get("timestamp"),
                        "temperature": self._extract_value(props.get("temperature")),
                        "dewpoint": self._extract_value(props.get("dewpoint")),
                        "wind_speed": self._extract_value(props.get("windSpeed")),
                        "wind_direction": self._extract_value(props.get("windDirection")),
                        "wind_gust": self._extract_value(props.get("windGust")),
                        "barometric_pressure": self._extract_value(props.get("barometricPressure")),
                        "visibility": self._extract_value(props.get("visibility")),
                        "relative_humidity": self._extract_value(props.get("relativeHumidity")),
                        "heat_index": self._extract_value(props.get("heatIndex")),
                        "wind_chill": self._extract_value(props.get("windChill")),
                        "text_description": props.get("textDescription", "No description"),
                    }

                except Exception as station_error:
                    logger.warning(
                        f"Station {
                            station_id if 'station_id' in locals() else 'unknown'} failed: {station_error}")
                    continue

            return {"error": "No stations provided current data"}

        except Exception as e:
            logger.warning(f"Current observations unavailable: {e!s}")
            return {"error": f"Current observations failed: {e!s}"}

    def _get_forecast_data(self, point_data: dict) -> dict[str, Any]:
        """Get NWS forecast data"""

        try:
            properties = point_data.get("properties", {})
            forecast_url = properties.get("forecast")
            forecast_hourly_url = properties.get("forecastHourly")

            forecast_data = {"periods": [], "hourly": []}

            # Get general forecast (12-hour periods)
            if forecast_url:
                forecast_response = requests.get(
                    forecast_url, headers=self.headers, timeout=10)
                forecast_response.raise_for_status()
                forecast_json = forecast_response.json()

                periods = forecast_json.get("properties", {}).get("periods", [])
                forecast_data["periods"] = periods[:6]  # Next 3 days (6 periods)

            # Get hourly forecast
            if forecast_hourly_url:
                hourly_response = requests.get(
                    forecast_hourly_url, headers=self.headers, timeout=10
                )
                hourly_response.raise_for_status()
                hourly_json = hourly_response.json()

                hourly_periods = hourly_json.get("properties", {}).get("periods", [])
                forecast_data["hourly"] = hourly_periods[:24]  # Next 24 hours

            return forecast_data

        except Exception as e:
            logger.warning(f"Forecast data unavailable: {e!s}")
            return {"error": f"Forecast data failed: {e!s}"}

    def _get_weather_alerts(self, lat: float, lon: float) -> list[dict]:
        """Get active weather alerts for the area"""

        try:
            # Get active alerts for the point
            alerts_url = f"{self.base_url}/alerts/active"
            params = {"point": f"{lat},{lon}"}

            alerts_response = requests.get(
                alerts_url, params=params, headers=self.headers, timeout=10
            )
            alerts_response.raise_for_status()
            alerts_data = alerts_response.json()

            # Parse alerts
            features = alerts_data.get("features", [])
            parsed_alerts = []

            for alert_feature in features:
                props = alert_feature.get("properties", {})
                parsed_alerts.append(
                    {
                        "event": props.get("event", "Unknown Alert"),
                        "severity": props.get("severity", "Unknown"),
                        "urgency": props.get("urgency", "Unknown"),
                        "certainty": props.get("certainty", "Unknown"),
                        "headline": props.get("headline", "No headline"),
                        "description": props.get("description", "No description"),
                        "effective": props.get("effective"),
                        "expires": props.get("expires"),
                        "area": props.get("areaDesc", "Unknown area"),
                    }
                )

            return parsed_alerts

        except Exception as e:
            logger.warning(f"Weather alerts unavailable: {e!s}")
            return []

    def _extract_value(self, weather_param: Any) -> float | None:
        """Extract numeric value from NWS weather parameter"""

        if not weather_param:
            return None

        if isinstance(weather_param, dict):
            value = weather_param.get("value")
            if value is not None:
                # Convert common units
                unit = weather_param.get("unitCode", "")
                if "fahrenheit" in unit.lower() or "degF" in unit:
                    return value  # Already in Fahrenheit
                elif "celsius" in unit.lower() or "degC" in unit:
                    return (value * 9 / 5) + 32  # Convert to Fahrenheit
                elif "km" in unit and "visibility" in str(weather_param):
                    return value * 0.621371  # Convert km to miles
                else:
                    return value

        return weather_param

    def _analyze_nws_betting_impact(
        self, current: dict, forecast: dict, alerts: list
    ) -> dict[str, Any]:
        """Analyze weather impact using NWS data for betting decisions"""

        impact_score = 0
        impact_factors = []

        # Current conditions analysis
        if current and "error" not in current:
            temp = current.get("temperature")
            wind_speed = current.get("wind_speed")
            wind_gust = current.get("wind_gust")
            visibility = current.get("visibility")

            # Temperature impact
            if temp is not None:
                if temp < self.impact_thresholds["temperature"]["extreme_cold"]:
                    impact_score += 3
                    impact_factors.append(
                        f"Extreme cold: {temp}°F - Major travel/fan impact")
                elif temp < self.impact_thresholds["temperature"]["very_cold"]:
                    impact_score += 2
                    impact_factors.append(
                        f"Very cold: {temp}°F - Significant travel impact")
                elif temp < self.impact_thresholds["temperature"]["cold"]:
                    impact_score += 1
                    impact_factors.append(f"Cold conditions: {temp}°F - Minor impact")

            # Wind impact - safely handle wind speed values
            wind_speed_val = wind_speed if isinstance(wind_speed, (int, float)) else 0
            wind_gust_val = wind_gust if isinstance(wind_gust, (int, float)) else 0
            max_wind = max(wind_speed_val, wind_gust_val)

            if max_wind >= self.impact_thresholds["wind"]["extreme"]:
                impact_score += 3
                impact_factors.append(
                    f"Extreme wind: {max_wind} mph - Major disruptions likely")
            elif max_wind >= self.impact_thresholds["wind"]["very_high"]:
                impact_score += 2
                impact_factors.append(
                    f"Very high wind: {max_wind} mph - Significant delays possible"
                )
            elif max_wind >= self.impact_thresholds["wind"]["high"]:
                impact_score += 1
                impact_factors.append(
                    f"High wind: {max_wind} mph - Minor delays possible")

            # Visibility impact - safely handle visibility values
            if (
                visibility is not None
                and isinstance(visibility, (int, float))
                and visibility < self.impact_thresholds["visibility"]["poor"]
            ):
                if visibility < self.impact_thresholds["visibility"]["very_poor"]:
                    impact_score += 3
                    impact_factors.append(
                        f"Very poor visibility: {visibility} mi - Major disruptions"
                    )
                else:
                    impact_score += 2
                    impact_factors.append(
                        f"Poor visibility: {visibility} mi - Travel delays likely"
                    )

        # Forecast analysis - check next 12 hours for game-time conditions
        if forecast and "hourly" in forecast:
            precip_periods = 0
            severe_weather = 0

            for period in forecast["hourly"][:12]:  # Next 12 hours
                short_forecast = period.get("shortForecast", "").lower()
                detailed_forecast = period.get("detailedForecast", "").lower()

                # Check for precipitation
                precip_keywords = ["rain", "snow", "sleet", "hail", "storm", "showers"]
                if any(
                    keyword in short_forecast or keyword in detailed_forecast
                    for keyword in precip_keywords
                ):
                    precip_periods += 1

                # Check for severe weather
                severe_keywords = [
                    "thunderstorm",
                    "blizzard",
                    "heavy",
                    "severe",
                    "warning",
                ]
                if any(
                    keyword in short_forecast or keyword in detailed_forecast
                    for keyword in severe_keywords
                ):
                    severe_weather += 1

            # Precipitation impact
            if precip_periods >= 8:  # Most of next 12 hours
                impact_score += 3
                impact_factors.append(
                    f"Extended precipitation expected - {precip_periods}/12 hours affected")
            elif precip_periods >= 4:
                impact_score += 2
                impact_factors.append(
                    f"Significant precipitation expected - {precip_periods}/12 hours affected")
            elif precip_periods >= 1:
                impact_score += 1
                impact_factors.append(
                    f"Some precipitation expected - {precip_periods}/12 hours affected"
                )

            # Severe weather impact
            if severe_weather > 0:
                impact_score += severe_weather
                impact_factors.append(
                    f"Severe weather conditions expected - {severe_weather} periods"
                )

        # Weather alerts impact (high priority)
        for alert in alerts:
            severity = alert.get("severity", "").lower()
            urgency = alert.get("urgency", "").lower()

            if severity in ["extreme", "severe"] or urgency == "immediate":
                impact_score += 4
                impact_factors.append(
                    f"CRITICAL ALERT: {alert.get('event')} - {alert.get('headline')}"
                )
            elif severity == "moderate" or urgency == "expected":
                impact_score += 2
                impact_factors.append(
                    f"Weather Alert: {alert.get('event')} - {alert.get('headline')}"
                )
            else:
                impact_score += 1
                impact_factors.append(f"Weather Advisory: {alert.get('event')}")

        # Cap impact score at 10
        impact_score = min(impact_score, 10)

        # Determine impact level
        if impact_score >= 8:
            impact_level = "CRITICAL"
        elif impact_score >= 6:
            impact_level = "HIGH"
        elif impact_score >= 4:
            impact_level = "MEDIUM"
        elif impact_score >= 2:
            impact_level = "LOW"
        else:
            impact_level = "MINIMAL"

        return {
            "impact_score": impact_score,
            "impact_level": impact_level,
            "impact_factors": impact_factors,
            "data_quality": "Excellent - Government source",
            "confidence": "High - Official NWS data",
        }

    def _get_eq12_nws_recommendations(self, betting_impact: dict) -> dict[str, Any]:
        """Get EQ12 betting recommendations based on NWS weather analysis"""

        impact_level = betting_impact["impact_level"]
        betting_impact["impact_score"]

        recommendations = {
            "overall_strategy": "",
            "game_props": [],
            "player_props": [],
            "risk_management": [],
            "confidence_adjustment": 0,
            "nws_advantages": [],
        }

        if impact_level == "CRITICAL":
            recommendations.update(
                {
                    "overall_strategy": "AVOID ALL BETTING - Government weather warnings active",
                    "game_props": [
                        "High postponement risk",
                        "Avoid all Over/Under bets",
                    ],
                    "player_props": [
                        "Cancel all player prop bets",
                        "Extreme variance expected",
                    ],
                    "risk_management": [
                        "Reduce positions by 80%",
                        "Monitor NWS updates every hour",
                    ],
                    "confidence_adjustment": -60,
                    "nws_advantages": [
                        "Official government alerts",
                        "Real-time NWS monitoring",
                    ],
                })

        elif impact_level == "HIGH":
            recommendations.update(
                {
                    "overall_strategy": "EXTREME CAUTION - Significant government weather warnings",
                    "game_props": [
                        "Lower scoring likely",
                        "Strong Under bias",
                        "Avoid period props",
                    ],
                    "player_props": [
                        "Reduce all player prop confidence by 60%",
                        "Focus on defensive stats only",
                    ],
                    "risk_management": [
                        "Reduce positions by 60%",
                        "Set automatic stops",
                        "Monitor NWS hourly",
                    ],
                    "confidence_adjustment": -40,
                    "nws_advantages": [
                        "Precise forecast timing",
                        "Government-grade accuracy",
                    ],
                })

        elif impact_level == "MEDIUM":
            recommendations.update(
                {
                    "overall_strategy": "CAUTIOUS BETTING - Monitor NWS updates closely",
                    "game_props": [
                        "Moderate scoring impact possible",
                        "Slight Under bias",
                    ],
                    "player_props": [
                        "Reduce player prop confidence by 30%",
                        "Monitor travel conditions",
                    ],
                    "risk_management": [
                        "Reduce positions by 30%",
                        "Increase monitoring frequency",
                    ],
                    "confidence_adjustment": -25,
                    "nws_advantages": [
                        "Detailed hourly forecasts",
                        "Local NWS office expertise",
                    ],
                })

        elif impact_level == "LOW":
            recommendations.update(
                {
                    "overall_strategy": "STANDARD BETTING - Minor weather considerations",
                    "game_props": [
                        "Minimal scoring impact",
                        "Normal game flow expected",
                    ],
                    "player_props": [
                        "Standard confidence levels",
                        "Minor travel considerations",
                    ],
                    "risk_management": [
                        "Normal position sizes",
                        "Standard monitoring"],
                    "confidence_adjustment": -10,
                    "nws_advantages": [
                        "Free reliable data",
                        "No rate limits"],
                })

        else:  # MINIMAL
            recommendations.update(
                {
                    "overall_strategy": "OPTIMAL CONDITIONS - Weather advantage confirmed",
                    "game_props": [
                        "Perfect conditions for analysis",
                        "High confidence in totals",
                    ],
                    "player_props": [
                        "Full confidence in player analysis",
                        "No weather adjustments",
                    ],
                    "risk_management": [
                        "Full position sizes acceptable",
                        "Minimal monitoring needed",
                    ],
                    "confidence_adjustment": 0,
                    "nws_advantages": [
                        "Government verification",
                        "Cost-free operation",
                    ],
                })

        return recommendations

    def get_nws_weather_summary(self, teams: list[str]) -> dict[str, Any]:
        """Get comprehensive NWS weather summary for multiple teams"""

        summary = {
            "timestamp": datetime.now(UTC).isoformat(),
            "teams_analyzed": len(teams),
            "nws_weather_impacts": {},
            "critical_weather_games": [],
            "optimal_weather_games": [],
            "overall_weather_risk": "LOW",
            "nws_data_quality": "Government Grade - FREE",
        }

        critical_count = 0

        for team in teams:
            analysis = self.get_nhl_weather_analysis(team)

            if "error" not in analysis:
                impact = analysis["betting_impact"]["impact_level"]
                summary["nws_weather_impacts"][team] = {
                    "impact_level": impact,
                    "impact_score": analysis["betting_impact"]["impact_score"],
                    "arena": analysis.get(
                        "arena",
                        "Unknown"),
                    "nws_office": analysis.get(
                        "nws_office",
                        "Unknown"),
                    "recommendation": analysis["eq12_recommendations"]["overall_strategy"],
                    "alerts_count": len(
                        analysis.get(
                            "weather_alerts",
                            [])),
                }

                if impact in ["HIGH", "CRITICAL"]:
                    summary["critical_weather_games"].append(team)
                    critical_count += 1
                elif impact == "MINIMAL":
                    summary["optimal_weather_games"].append(team)

        # Calculate overall risk using government data
        risk_percentage = (critical_count / len(teams)) * 100 if teams else 0
        if risk_percentage > 40:
            summary["overall_weather_risk"] = "CRITICAL"
        elif risk_percentage > 20:
            summary["overall_weather_risk"] = "HIGH"
        elif risk_percentage > 10:
            summary["overall_weather_risk"] = "MEDIUM"

        return summary


def main():
    """Demo the EQ12 NWS Weather Client"""

    print("🇺🇸 EQ12 NATIONAL WEATHER SERVICE CLIENT - DEMO")
    print("=" * 55)
    print("✅ 100% FREE - No API key required")
    print("✅ Government-grade accuracy")
    print("✅ No rate limits for typical use")
    print("")

    client = EQ12NWSWeatherClient()

    # Test with sample NHL teams
    test_teams = ["Boston", "Colorado", "Vegas", "Chicago"]

    print(f"📊 Testing NWS weather analysis for {len(test_teams)} teams...")

    for team in test_teams:
        print(f"\n🏒 Analyzing NWS weather for {team}...")

        analysis = client.get_nhl_weather_analysis(team)

        if "error" in analysis:
            print(f"   ❌ Error: {analysis['error']}")
        else:
            impact = analysis["betting_impact"]
            current = analysis.get("current_weather", {})
            alerts = analysis.get("weather_alerts", [])
            nws_office = analysis.get("nws_office", "Unknown")

            temp = current.get("temperature", "N/A")
            wind = current.get("wind_speed", "N/A")

            print(f"   🌡️ Temperature: {temp}°F")
            print(f"   💨 Wind Speed: {wind} mph")
            print(
                f"   ⚠️ Impact Level: {
                    impact['impact_level']} ({
                    impact['impact_score']}/10)")
            print(f"   🏛️ NWS Office: {nws_office}")
            print(f"   🚨 Active Alerts: {len(alerts)}")
            print(
                f"   🎲 Strategy: {
                    analysis['eq12_recommendations']['overall_strategy']}")

    # Test weather summary
    print("\n📈 NWS WEATHER SUMMARY FOR BETTING:")
    summary = client.get_nws_weather_summary(test_teams)
    print(f"   🎯 Overall Risk Level: {summary['overall_weather_risk']}")
    print(f"   ⚠️ Critical Weather Games: {len(summary['critical_weather_games'])}")
    print(f"   ✅ Optimal Weather Games: {len(summary['optimal_weather_games'])}")
    print(f"   🏛️ Data Quality: {summary['nws_data_quality']}")

    print("\n✅ EQ12 NWS Weather Client ready for integration!")
    print("   💰 Cost: $0 forever - Government provided data")
    print("   🚀 Rate Limits: Generous for typical betting use")
    print("   📊 Data Quality: Official U.S. government source")
    print("   🎯 Perfect complement to OpenWeather API")


if __name__ == "__main__":
    main()
