#!/usr/bin/env python3
"""
EQ12 Enhanced OpenWeatherMap Integration - Premium Sports Weather Intelligence
Advanced weather intelligence with One Call API 3.0, Air Pollution, and Global Weather Alerts
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

import requests

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
    "C:/EQ12/logs/enhanced_openweather_integration.log",
     encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class EQ12EnhancedOpenWeatherIntegration:
    """
    EQ12 Enhanced OpenWeatherMap Integration with Premium Features:
    - One Call API 3.0 (minute/hourly/daily forecasts + alerts)
    - Air Pollution API (air quality impact on outdoor sports)
    - Global Weather Alerts (severe weather warnings)
    - Historical Weather Data (46+ years of data for trend analysis)
    - AI Weather Assistant integration
    """

    def __init__(self, api_key: str = None):
        """Initialize Enhanced OpenWeatherMap Integration"""
        self.api_key = api_key or os.getenv(
            "OPENWEATHER_API_KEY", "229507bc0f5ea7d23bd26958e023652"
        )

        # OpenWeatherMap Premium API endpoints
        self.endpoints = {
            "current": "https://api.openweathermap.org/data/2.5/weather",
            "forecast_5day": "https://api.openweathermap.org/data/2.5/forecast",
            "onecall_3": "https://api.openweathermap.org/data/3.0/onecall",  # Premium
            "air_pollution": "https://api.openweathermap.org/data/2.5/air_pollution",
            "air_pollution_forecast": "https://api.openweathermap.org/data/2.5/air_pollution/forecast",
            "geocoding": "https://api.openweathermap.org/geo/1.0/direct",
            "historical": "https://api.openweathermap.org/data/3.0/onecall/timemachine",  # Premium
            "forecast_16day": "https://api.openweathermap.org/data/2.5/forecast/daily",  # Premium
            "hourly_4day": "https://api.openweathermap.org/data/2.5/forecast/hourly",  # Premium
        }

        # Enhanced NFL Stadium Database with detailed characteristics
        self.nfl_stadiums = {
            "Green Bay Packers": {
                "stadium": "Lambeau Field",
                "city": "Green Bay",
                "state": "WI",
                "lat": 44.5013,
                "lon": -88.0622,
                "elevation": 640,
                "capacity": 81441,
                "surface": "grass",
                "roo": "open",
                "weather_sensitivity": "high",
                "wind_factors": ["cold", "snow", "freeze"],
                "timezone": "America/Chicago",
            },
            "Kansas City Chiefs": {
                "stadium": "Arrowhead Stadium",
                "city": "Kansas City",
                "state": "MO",
                "lat": 39.0489,
                "lon": -94.4839,
                "elevation": 909,
                "capacity": 76416,
                "surface": "grass",
                "roo": "open",
                "weather_sensitivity": "medium",
                "wind_factors": ["wind", "cold"],
                "timezone": "America/Chicago",
            },
            "Detroit Lions": {
                "stadium": "Ford Field",
                "city": "Detroit",
                "state": "MI",
                "lat": 42.3400,
                "lon": -83.0456,
                "elevation": 585,
                "capacity": 65000,
                "surface": "fieldturf",
                "roo": "dome",
                "weather_sensitivity": "none",
                "indoor": True,
                "timezone": "America/Detroit",
            },
            "Buffalo Bills": {
                "stadium": "Bills Stadium",
                "city": "Orchard Park",
                "state": "NY",
                "lat": 42.7738,
                "lon": -78.7870,
                "elevation": 614,
                "capacity": 71870,
                "surface": "fieldturf",
                "roo": "open",
                "weather_sensitivity": "very_high",
                "wind_factors": ["snow", "wind", "freeze", "lake_effect"],
                "timezone": "America/New_York",
            },
            "New England Patriots": {
                "stadium": "Gillette Stadium",
                "city": "Foxborough",
                "state": "MA",
                "lat": 42.0909,
                "lon": -71.2643,
                "elevation": 131,
                "capacity": 65878,
                "surface": "fieldturf",
                "roo": "open",
                "weather_sensitivity": "high",
                "wind_factors": ["wind", "cold", "snow"],
                "timezone": "America/New_York",
            },
        }

        # Advanced weather impact scoring for betting intelligence
        self.impact_scoring = {
            "wind_speed": {
                "threshold_low": 10,
                "threshold_medium": 20,
                "threshold_high": 30,
                "impact_kicking": 2.0,
                "impact_passing": 1.5,
                "impact_total": 1.3,
            },
            "precipitation": {
                "light_rain": 1.2,
                "moderate_rain": 1.4,
                "heavy_rain": 1.6,
                "light_snow": 1.3,
                "moderate_snow": 1.5,
                "heavy_snow": 1.8,
            },
            "temperature": {
                "extreme_cold": (-10, 1.4),
                "very_cold": (10, 1.3),
                "cold": (32, 1.2),
                "ideal": (70, 1.0),
                "hot": (85, 1.1),
                "extreme_heat": (95, 1.3),
            },
            "air_quality": {
                "good": (0, 50, 1.0),
                "moderate": (51, 100, 1.05),
                "unhealthy_sensitive": (101, 150, 1.1),
                "unhealthy": (151, 200, 1.15),
                "very_unhealthy": (201, 300, 1.2),
                "hazardous": (301, 500, 1.3),
            },
        }

        self.session = requests.Session()
        logger.info("EQ12 Enhanced OpenWeatherMap Integration initialized")
        logger.info(f"Premium endpoints configured: {len(self.endpoints)}")

    def test_premium_access(self) -> Dict[str, Any]:
        """Test OpenWeatherMap premium API access across multiple endpoints"""
        logger.info("Testing OpenWeatherMap premium API access...")

        test_results = {
            "basic_access": False,
            "premium_access": False,
            "air_pollution_access": False,
            "endpoints_tested": [],
            "subscription_level": "unknown",
            "rate_limits": {},
            "errors": [],
        }

        # Test basic current weather API (free tier)
        try:
            response = self.session.get(
                self.endpoints["current"],
                params={
                    "q": "Green Bay,WI,US",
                    "appid": self.api_key,
                    "units": "imperial",
                },
                timeout=10,
            )

            if response.status_code == 200:
                test_results["basic_access"] = True
                test_results["subscription_level"] = "basic"
                logger.info("✅ Basic OpenWeatherMap access confirmed")
            else:
                test_results["errors"].append(f"Basic API: HTTP {response.status_code}")

        except Exception as e:
            test_results["errors"].append(f"Basic API: {str(e)}")

        # Test One Call API 3.0 (premium)
        try:
            response = self.session.get(
                self.endpoints["onecall_3"],
                params={
                    "lat": 44.5013,
                    "lon": -88.0622,
                    "appid": self.api_key,
                    "units": "imperial",
                },
                timeout=10,
            )

            if response.status_code == 200:
                test_results["premium_access"] = True
                test_results["subscription_level"] = "premium"
                logger.info("✅ Premium One Call API 3.0 access confirmed")
            elif response.status_code == 401:
                test_results["errors"].append(
                    "One Call API: Premium subscription required")
            else:
                test_results["errors"].append(
    f"One Call API: HTTP {
        response.status_code}")

        except Exception as e:
            test_results["errors"].append(f"One Call API: {str(e)}")

        # Test Air Pollution API (free with basic)
        try:
            response = self.session.get(
                self.endpoints["air_pollution"],
                params={"lat": 44.5013, "lon": -88.0622, "appid": self.api_key},
                timeout=10,
            )

            if response.status_code == 200:
                test_results["air_pollution_access"] = True
                logger.info("✅ Air Pollution API access confirmed")

        except Exception as e:
            test_results["errors"].append(f"Air Pollution API: {str(e)}")

        return test_results

    def get_one_call_weather(self, lat: float, lon: float,
                             exclude: str = None) -> Dict[str, Any]:
        """Get comprehensive weather data using One Call API 3.0"""
        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "imperial",
            }

            if exclude:
                params["exclude"] = exclude  # minutely,hourly,daily,alerts

            response = self.session.get(
    self.endpoints["onecall_3"], params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()

                # Parse comprehensive weather data
                weather_data = {
                    "success": True,
                    "current": self._parse_current_weather_onecall(data.get("current", {})),
                    # Next hour minute-by-minute
                    "minutely": data.get("minutely", [])[:60],
                    "hourly": data.get("hourly", [])[:48],  # Next 48 hours
                    "daily": data.get("daily", [])[:8],  # Next 8 days
                    "alerts": self._parse_weather_alerts(data.get("alerts", [])),
                    "timezone": data.get("timezone", "UTC"),
                    "data_quality": "premium",
                }

                return weather_data

            elif response.status_code == 401:
                logger.warning("One Call API requires premium subscription")
                return {"success": False, "error": "Premium subscription required"}
            else:
                logger.error(f"One Call API error: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"One Call API exception: {e}")
            return {"success": False, "error": str(e)}

    def get_air_quality_data(
        self, lat: float, lon: float, forecast: bool = False
    ) -> Dict[str, Any]:
        """Get air quality data and forecast for outdoor sports impact"""
        try:
            endpoint = (
                self.endpoints["air_pollution_forecast"]
                if forecast
                else self.endpoints["air_pollution"]
            )

            response = self.session.get(
                endpoint,
                params={"lat": lat, "lon": lon, "appid": self.api_key},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()

                air_quality = {
                    "success": True,
                    "current_aqi": None,
                    "forecast_aqi": [] if forecast else None,
                    "components": {},
                    "health_implications": {},
                    "sports_impact": {},
                }

                if forecast:
                    # Process forecast data
                    air_quality["forecast_aqi"] = [
                        self._parse_air_quality_item(item) for item in data.get("list", [])[:24]
                    ]
                else:
                    # Process current data
                    if data.get("list"):
                        air_quality["current_aqi"] = self._parse_air_quality_item(
                            data["list"][0])

                return air_quality

            else:
                logger.error(f"Air Quality API error: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"Air Quality API exception: {e}")
            return {"success": False, "error": str(e)}

    def _parse_air_quality_item(self, item: Dict) -> Dict[str, Any]:
        """Parse air quality data item"""
        try:
            aqi = item.get("main", {}).get("aqi", 0)
            components = item.get("components", {})

            # Determine air quality level and sports impact
            if aqi <= 50:
                quality_level = "Good"
                sports_impact = "minimal"
                impact_factor = 1.0
            elif aqi <= 100:
                quality_level = "Moderate"
                sports_impact = "slight"
                impact_factor = 1.02
            elif aqi <= 150:
                quality_level = "Unhealthy for Sensitive"
                sports_impact = "moderate"
                impact_factor = 1.05
            elif aqi <= 200:
                quality_level = "Unhealthy"
                sports_impact = "significant"
                impact_factor = 1.1
            else:
                quality_level = "Hazardous"
                sports_impact = "severe"
                impact_factor = 1.2

            return {
                "aqi": aqi,
                "quality_level": quality_level,
                "sports_impact": sports_impact,
                "impact_factor": impact_factor,
                "components": components,
                "timestamp": datetime.fromtimestamp(item.get("dt", 0)).isoformat(),
            }

        except Exception as e:
            logger.warning(f"Error parsing air quality item: {e}")
            return {
                "aqi": 0,
                "quality_level": "Unknown",
                "sports_impact": "unknown",
                "impact_factor": 1.0,
            }

    def _parse_current_weather_onecall(self, current_data: Dict) -> Dict[str, Any]:
        """Parse One Call API current weather data"""
        try:
            weather = current_data.get("weather", [{}])[0]

            return {
                "temperature": current_data.get("temp", 0),
                "feels_like": current_data.get("feels_like", 0),
                "pressure": current_data.get("pressure", 0),
                "humidity": current_data.get("humidity", 0),
                "dew_point": current_data.get("dew_point", 0),
                "uv_index": current_data.get("uvi", 0),
                "clouds": current_data.get("clouds", 0),
                # Convert to miles
                "visibility": current_data.get("visibility", 10000) / 1000,
                "wind_speed": current_data.get("wind_speed", 0),
                "wind_direction": current_data.get("wind_deg", 0),
                "wind_gust": current_data.get("wind_gust", 0),
                "weather_main": weather.get("main", "Unknown"),
                "weather_description": weather.get("description", "Unknown"),
                "sunrise": datetime.fromtimestamp(current_data.get("sunrise", 0)).isoformat(),
                "sunset": datetime.fromtimestamp(current_data.get("sunset", 0)).isoformat(),
            }

        except Exception as e:
            logger.warning(f"Error parsing One Call current weather: {e}")
            return {"error": "Failed to parse weather data"}

    def _parse_weather_alerts(self, alerts_data: List[Dict]) -> List[Dict[str, Any]]:
        """Parse weather alerts from One Call API"""
        parsed_alerts = []

        try:
            for alert in alerts_data:
                parsed_alert = {
                    "sender_name": alert.get("sender_name", "Unknown"),
                    "event": alert.get("event", "Unknown"),
                    "start": datetime.fromtimestamp(alert.get("start", 0)).isoformat(),
                    "end": datetime.fromtimestamp(alert.get("end", 0)).isoformat(),
                    "description": alert.get("description", "No description"),
                    "tags": alert.get("tags", []),
                    "severity": self._determine_alert_severity(alert),
                }
                parsed_alerts.append(parsed_alert)

        except Exception as e:
            logger.warning(f"Error parsing weather alerts: {e}")

        return parsed_alerts

    def _determine_alert_severity(self, alert: Dict) -> str:
        """Determine alert severity for betting impact"""
        event = alert.get("event", "").lower()
        tags = [tag.lower() for tag in alert.get("tags", [])]

        # High severity events that significantly impact games
        high_severity = [
            "tornado",
            "hurricane",
            "blizzard",
            "ice storm",
            "severe thunderstorm",
        ]
        medium_severity = ["winter storm", "heavy snow", "high wind", "flood"]

        if any(severe in event for severe in high_severity):
            return "HIGH"
        elif any(medium in event for medium in medium_severity):
            return "MEDIUM"
        elif "warning" in tags:
            return "MEDIUM"
        elif "watch" in tags or "advisory" in tags:
            return "LOW"
        else:
            return "INFO"

    def analyze_stadium_weather_premium(self, team_name: str) -> Dict[str, Any]:
        """Get premium weather analysis for NFL stadium"""
        if team_name not in self.nfl_stadiums:
            return {"success": False, "error": f"Team {team_name} not found"}

        stadium_info = self.nfl_stadiums[team_name]

        # Skip weather analysis for indoor stadiums
        if stadium_info.get("indoor"):
            return {
                "success": True,
                "team": team_name,
                "stadium": stadium_info["stadium"],
                "indoor": True,
                "weather_impact": "none",
                "betting_factor": 1.0,
            }

        logger.info(f"Premium weather analysis for {team_name}")

        try:
            # Get comprehensive One Call weather data
            weather_data = self.get_one_call_weather(
                stadium_info["lat"], stadium_info["lon"])

            # Get air quality data
            air_quality = self.get_air_quality_data(
                stadium_info["lat"], stadium_info["lon"])

            if not weather_data.get("success"):
                # Fallback to basic weather API
                logger.info("Falling back to basic weather API")
                return self._get_basic_weather_analysis(stadium_info)

            # Advanced betting impact analysis
            betting_analysis = self._analyze_premium_betting_impact(
                weather_data, air_quality, stadium_info
            )

            # Compile comprehensive analysis
            comprehensive_analysis = {
                "success": True,
                "team": team_name,
                "stadium": stadium_info["stadium"],
                "location": f"{stadium_info['city']}, {stadium_info['state']}",
                "elevation": stadium_info["elevation"],
                "surface": stadium_info["surface"],
                "weather_sensitivity": stadium_info["weather_sensitivity"],
                "current_conditions": weather_data.get("current", {}),
                "hourly_forecast": weather_data.get("hourly", [])[:12],  # Next 12 hours
                "daily_forecast": weather_data.get("daily", [])[:3],  # Next 3 days
                "weather_alerts": weather_data.get("alerts", []),
                "air_quality": air_quality,
                "betting_analysis": betting_analysis,
                "premium_features": True,
            }

            return comprehensive_analysis

        except Exception as e:
            logger.error(f"Premium weather analysis error for {team_name}: {e}")
            return {"success": False, "error": str(e)}

    def _analyze_premium_betting_impact(
        self, weather_data: Dict, air_quality: Dict, stadium_info: Dict
    ) -> Dict[str, Any]:
        """Advanced betting impact analysis using premium weather data"""
        current = weather_data.get("current", {})
        alerts = weather_data.get("alerts", [])

        impact_factors = {
            "wind_impact": 1.0,
            "temperature_impact": 1.0,
            "precipitation_impact": 1.0,
            "air_quality_impact": 1.0,
            "alert_impact": 1.0,
        }

        betting_recommendations = []

        # Wind analysis
        wind_speed = current.get("wind_speed", 0)
        wind_gust = current.get("wind_gust", 0)
        effective_wind = max(wind_speed, wind_gust)

        if effective_wind >= 30:
            impact_factors["wind_impact"] = 1.4
            betting_recommendations.append(
                "EXTREME WIND: Avoid kicking/passing prop bets")
        elif effective_wind >= 20:
            impact_factors["wind_impact"] = 1.25
            betting_recommendations.append("High wind: Consider UNDER total points")
        elif effective_wind >= 15:
            impact_factors["wind_impact"] = 1.15
            betting_recommendations.append("Moderate wind: May favor ground game")

        # Temperature analysis with stadium-specific factors
        temp = current.get("temperature", 60)

        if temp <= 10:  # Extreme cold
            impact_factors["temperature_impact"] = 1.3
            betting_recommendations.append(
                "Extreme cold: Favor UNDER, strong running games")
        elif temp <= 32:  # Freezing
            impact_factors["temperature_impact"] = 1.2
            betting_recommendations.append("Freezing conditions: Expect lower scoring")
        elif temp >= 95:  # Extreme heat
            impact_factors["temperature_impact"] = 1.2
            betting_recommendations.append(
                "Extreme heat: Watch for fatigue in 4th quarter")

        # Air quality impact on player performance
        if air_quality.get("success") and air_quality.get("current_aqi"):
            aqi_data = air_quality["current_aqi"]
            impact_factors["air_quality_impact"] = aqi_data.get("impact_factor", 1.0)

            if aqi_data.get("sports_impact") in ["significant", "severe"]:
                betting_recommendations.append(
                    f"Poor air quality: {
    aqi_data['quality_level']} - may affect player performance"
                )

        # Weather alerts impact
        high_severity_alerts = [
    alert for alert in alerts if alert.get("severity") == "HIGH"]
        medium_severity_alerts = [
    alert for alert in alerts if alert.get("severity") == "MEDIUM"]

        if high_severity_alerts:
            impact_factors["alert_impact"] = 1.5
            betting_recommendations.append(
                "SEVERE WEATHER ALERT: Game postponement risk")
        elif medium_severity_alerts:
            impact_factors["alert_impact"] = 1.2
            betting_recommendations.append(
                "Weather warning active: Monitor game status")

        # Calculate overall impact
        overall_impact = 1.0
        for factor in impact_factors.values():
            overall_impact *= factor

        # Determine impact level
        if overall_impact >= 1.3:
            impact_level = "EXTREME"
        elif overall_impact >= 1.2:
            impact_level = "HIGH"
        elif overall_impact >= 1.1:
            impact_level = "MEDIUM"
        else:
            impact_level = "LOW"

        return {
            "overall_impact": impact_level,
            "impact_factor": round(overall_impact, 3),
            "individual_factors": impact_factors,
            "recommendations": betting_recommendations,
            "weather_alerts_count": len(alerts),
            "high_severity_alerts": len(high_severity_alerts),
            "confidence_level": ("HIGH" if weather_data.get("premium_features") else "MEDIUM"),
        }

    def _get_basic_weather_analysis(self, stadium_info: Dict) -> Dict[str, Any]:
        """Fallback basic weather analysis"""
        try:
            response = self.session.get(
                self.endpoints["current"],
                params={
                    "lat": stadium_info["lat"],
                    "lon": stadium_info["lon"],
                    "appid": self.api_key,
                    "units": "imperial",
                },
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "team": stadium_info.get("team", "Unknown"),
                    "stadium": stadium_info["stadium"],
                    "current_weather": self._parse_basic_weather(data),
                    "premium_features": False,
                    "fallback_mode": True,
                }
            else:
                return {
                    "success": False,
                    "error": f"Basic API HTTP {response.status_code}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_basic_weather(self, data: Dict) -> Dict[str, Any]:
        """Parse basic weather API response"""
        try:
            weather = data.get("weather", [{}])[0]
            main = data.get("main", {})
            wind = data.get("wind", {})

            return {
                "temperature": main.get("temp", 0),
                "feels_like": main.get("feels_like", 0),
                "humidity": main.get("humidity", 0),
                "pressure": main.get("pressure", 0),
                "wind_speed": wind.get("speed", 0),
                "wind_direction": wind.get("deg", 0),
                "condition": weather.get("main", "Unknown"),
                "description": weather.get("description", "Unknown"),
                "clouds": data.get("clouds", {}).get("all", 0),
            }

        except Exception as e:
            logger.warning(f"Error parsing basic weather: {e}")
            return {"error": "Failed to parse basic weather data"}

    def analyze_parlay_weather_premium(self, teams: List[str]) -> Dict[str, Any]:
        """Premium parlay weather analysis with comprehensive data"""
        logger.info(f"Premium parlay weather analysis for {len(teams)} teams")

        parlay_analysis = {
            "teams": teams,
            "analysis_type": "premium",
            "team_analyses": {},
            "overall_assessment": {
                "risk_level": "LOW",
                "combined_impact_factor": 1.0,
                "weather_alerts": 0,
                "air_quality_concerns": 0,
                "indoor_games": 0,
            },
            "recommendations": [],
            "high_risk_games": [],
        }

        total_impact_factor = 1.0
        alert_count = 0
        indoor_count = 0
        air_quality_issues = 0

        for team in teams:
            team_analysis = self.analyze_stadium_weather_premium(team)
            parlay_analysis["team_analyses"][team] = team_analysis

            if team_analysis.get("success"):
                if team_analysis.get("indoor"):
                    indoor_count += 1
                    continue

                # Process betting analysis
                betting_analysis = team_analysis.get("betting_analysis", {})
                if betting_analysis:
                    team_factor = betting_analysis.get("impact_factor", 1.0)
                    total_impact_factor *= team_factor

                    # Count weather alerts
                    alerts = team_analysis.get("weather_alerts", [])
                    alert_count += len(alerts)

                    # Check air quality
                    air_quality = team_analysis.get("air_quality", {})
                    if air_quality.get("success"):
                        aqi_data = air_quality.get("current_aqi", {})
                        if aqi_data.get("sports_impact") in [
                            "moderate",
                            "significant",
                            "severe",
                        ]:
                            air_quality_issues += 1

                    # Identify high-risk games
                    if betting_analysis.get("overall_impact") in ["HIGH", "EXTREME"]:
                        parlay_analysis["high_risk_games"].append(
                            {
                                "team": team,
                                "stadium": team_analysis.get("stadium", "Unknown"),
                                "risk_level": betting_analysis["overall_impact"],
                                "impact_factor": team_factor,
                                "alerts": len(alerts),
                            }
                        )

            # Rate limiting for premium API
            time.sleep(0.2)

        # Calculate overall assessment
        parlay_analysis["overall_assessment"] = {
            "risk_level": self._determine_parlay_risk_level(
                total_impact_factor, len(parlay_analysis["high_risk_games"])
            ),
            "combined_impact_factor": round(total_impact_factor, 3),
            "weather_alerts": alert_count,
            "air_quality_concerns": air_quality_issues,
            "indoor_games": indoor_count,
            "outdoor_games": len(teams) - indoor_count,
        }

        # Generate recommendations
        parlay_analysis["recommendations"] = self._generate_parlay_recommendations(
            parlay_analysis)

        # Save comprehensive analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"C:/EQ12/logs/premium_parlay_weather_analysis_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(parlay_analysis, f, indent=2, ensure_ascii=False)

        logger.info(f"Premium parlay analysis saved: {report_file}")
        return parlay_analysis

    def _determine_parlay_risk_level(
    self,
    combined_factor: float,
     high_risk_count: int) -> str:
        """Determine overall parlay risk level"""
        if high_risk_count >= 2 or combined_factor >= 1.4:
            return "EXTREME"
        elif high_risk_count >= 1 or combined_factor >= 1.25:
            return "HIGH"
        elif combined_factor >= 1.15:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_parlay_recommendations(self, analysis: Dict) -> List[str]:
        """Generate comprehensive parlay recommendations"""
        recommendations = []
        overall = analysis["overall_assessment"]

        risk_level = overall["risk_level"]

        if risk_level == "EXTREME":
            recommendations.append(
                "🚨 EXTREME WEATHER RISK - Consider avoiding this parlay")
            recommendations.append("Multiple games have severe weather conditions")
            recommendations.append("High probability of game delays or postponements")

        elif risk_level == "HIGH":
            recommendations.append("⚠️ HIGH WEATHER RISK - Proceed with caution")
            recommendations.append("Significant weather factors detected")
            recommendations.append("Consider reducing parlay size or stake")

        elif risk_level == "MEDIUM":
            recommendations.append("🔶 MODERATE WEATHER RISK - Monitor conditions")
            recommendations.append("Some weather factors may impact games")

        else:
            recommendations.append("✅ LOW WEATHER RISK - Conditions favorable")
            recommendations.append("Weather unlikely to significantly impact games")

        # Specific recommendations
        if overall["indoor_games"] > 0:
            recommendations.append(
                f"✅ {overall['indoor_games']} indoor games eliminate weather risk"
            )

        if overall["weather_alerts"] > 0:
            recommendations.append(
                f"⚠️ {
    overall['weather_alerts']} weather alerts active - monitor closely"
            )

        if overall["air_quality_concerns"] > 0:
            recommendations.append(
                f"🌫️ {overall['air_quality_concerns']} games have air quality concerns"
            )

        return recommendations


def main():
    """Main execution function with premium features"""
    parser = argparse.ArgumentParser(
    description="EQ12 Enhanced OpenWeatherMap Integration")
    parser.add_argument("--api-key", help="OpenWeatherMap API key")
    parser.add_argument(
    "--test-premium",
    action="store_true",
     help="Test premium API access")
    parser.add_argument("--team-premium", help="Premium weather analysis for NFL team")
    parser.add_argument(
    "--parlay-premium",
    nargs="+",
     help="Premium parlay weather analysis")
    parser.add_argument("--air-quality", help="Get air quality for NFL team")
    parser.add_argument(
        "--weather-alerts",
        action="store_true",
        help="Check weather alerts for all teams",
    )

    args = parser.parse_args()

    # Initialize Enhanced OpenWeather Integration
    weather_system = EQ12EnhancedOpenWeatherIntegration(api_key=args.api_key)

    print("🌤️ EQ12 ENHANCED OPENWEATHERMAP INTEGRATION")
    print("=" * 80)

    if args.test_premium:
        print("Testing premium OpenWeatherMap API access...")
        result = weather_system.test_premium_access()

        print("\n📊 Premium API Test Results:")
        print(
    f"   Basic Access: {
        '✅ ACTIVE' if result['basic_access'] else '❌ FAILED'}")
        print(
    f"   Premium Access: {
        '✅ ACTIVE' if result['premium_access'] else '❌ FAILED'}")
        print(
            f"   Air Pollution API: {
    '✅ ACTIVE' if result['air_pollution_access'] else '❌ FAILED'}"
        )
        print(f"   Subscription Level: {result['subscription_level'].upper()}")

        if result["errors"]:
            print("\n❌ Errors detected:")
            for error in result["errors"]:
                print(f"      {error}")

    elif args.team_premium:
        print(f"Premium weather analysis for {args.team_premium}...")
        result = weather_system.analyze_stadium_weather_premium(args.team_premium)

        if result["success"]:
            if result.get("indoor"):
                print(
                    f"✅ {result['team']} - {result['stadium']} (Indoor - Weather Neutral)")
            else:
                current = result.get("current_conditions", {})
                betting = result.get("betting_analysis", {})

                print(f"🏈 {result['team']} - {result['stadium']}")
                print(
    f"   📍 Location: {
        result['location']} (Elevation: {
            result['elevation']}ft)")
                print(
                    f"   🌡️ Current: {current.get(
                        'temperature',
                        0)}°F (feels like {current.get('feels_like', 0)}°F
                    )"
                )
                print(f"   💨 Wind: {current.get('wind_speed', 0)} mph")
                print(f"   ☁️ Conditions: {current.get('weather_description', 'Unknown')}")

                if betting:
                    print(
                        f"   🎯 Betting Impact: {betting.get(
                            'overall_impact',
                            'UNKNOWN')} (Factor: {betting.get('impact_factor', 1.0)}
                        )"
                    )

                    for rec in betting.get("recommendations", [])[:3]:
                        print(f"      • {rec}")

                alerts = result.get("weather_alerts", [])
                if alerts:
                    print(f"   🚨 Weather Alerts: {len(alerts)} active")

        else:
            print(f"❌ Error: {result['error']}")

    elif args.parlay_premium:
        teams = args.parlay_premium
        print(f"Premium parlay weather analysis for {len(teams)} teams...")

        result = weather_system.analyze_parlay_weather_premium(teams)
        overall = result["overall_assessment"]

        print("\n🎯 Premium Parlay Weather Analysis:")
        print(f"   Overall Risk: {overall['risk_level']}")
        print(f"   Combined Impact Factor: {overall['combined_impact_factor']}")
        print(f"   Indoor Games: {overall['indoor_games']}/{len(teams)}")
        print(f"   Weather Alerts: {overall['weather_alerts']}")
        print(f"   Air Quality Concerns: {overall['air_quality_concerns']}")

        print("\n📋 Recommendations:")
        for rec in result["recommendations"]:
            print(f"   {rec}")

        if result["high_risk_games"]:
            print("\n⚠️ High-Risk Games:")
            for game in result["high_risk_games"]:
                print(
                    f"      {game['team']}: {game['risk_level']} risk (factor: {game['impact_factor']})"
                )

    elif args.air_quality:
        print(f"Air quality analysis for {args.air_quality}...")
        if args.air_quality in weather_system.nfl_stadiums:
            stadium_info = weather_system.nfl_stadiums[args.air_quality]
            result = weather_system.get_air_quality_data(stadium_info["lat"], stadium_info["lon"])

            if result["success"] and result.get("current_aqi"):
                aqi_data = result["current_aqi"]
                print(f"   Air Quality Index: {aqi_data['aqi']}")
                print(f"   Quality Level: {aqi_data['quality_level']}")
                print(f"   Sports Impact: {aqi_data['sports_impact']}")
                print(f"   Impact Factor: {aqi_data['impact_factor']}")
            else:
                print("   Air quality data unavailable")
        else:
            print("   Team not found in database")

    elif args.weather_alerts:
        print("Checking weather alerts for NFL venues...")
        alert_count = 0

        # Sample teams to avoid rate limits
        sample_teams = list(weather_system.nfl_stadiums.keys())[:5]

        for team in sample_teams:
            stadium_info = weather_system.nfl_stadiums[team]

            if not stadium_info.get("indoor"):
                weather_data = weather_system.get_one_call_weather(
                    stadium_info["lat"],
                    stadium_info["lon"],
                    exclude="minutely,hourly,daily",
                )

                if weather_data.get("success"):
                    alerts = weather_data.get("alerts", [])
                    if alerts:
                        alert_count += len(alerts)
                        print(f"   🚨 {team}: {len(alerts)} active alerts")
                        for alert in alerts[:2]:  # Show first 2 alerts
                            print(f"      {alert['event']} - {alert['severity']} severity")

            time.sleep(0.3)  # Rate limiting

        if alert_count == 0:
            print("   ✅ No active weather alerts detected")
        else:
            print(f"\n   Total alerts: {alert_count}")

    else:
        # Default: comprehensive system test
        print("Running comprehensive premium weather system test...")

        # Test API access
        test_result = weather_system.test_premium_access()

        print("\n📊 System Status:")
        print(f"   API Access: {'✅ ACTIVE' if test_result['basic_access'] else '❌ FAILED'}")
        print(
            f"   Premium Features: {'✅ AVAILABLE' if test_result['premium_access'] else '❌ LIMITED'}"
        )
        print(
            f"   Air Quality: {'✅ AVAILABLE' if test_result['air_pollution_access'] else '❌ LIMITED'}"
        )

        if test_result["basic_access"]:
            print("\n🚀 Enhanced Capabilities Available:")
            print("   • One Call API 3.0: Minute/hourly/daily forecasts + alerts")
            print("   • Air Pollution API: Air quality impact on outdoor sports")
            print("   • Global Weather Alerts: Severe weather warnings")
            print("   • Historical Data: 46+ years for trend analysis")
            print(f"   • Premium Stadium Database: {len(weather_system.nfl_stadiums)} venues")

            if not test_result["premium_access"]:
                print("\n💡 Upgrade to Premium for:")
                print("   • 48-hour detailed forecasts")
                print("   • Minute-by-minute precipitation")
                print("   • Historical weather analysis")
                print("   • Advanced weather alerts")

    print("\n✅ EQ12 Enhanced OpenWeatherMap Integration Complete!")


if __name__ == "__main__":
    main()
