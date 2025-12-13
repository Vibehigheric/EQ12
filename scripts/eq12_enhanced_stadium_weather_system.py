#!/usr/bin/env python3
"""
EQ12 Enhanced Stadium Weather Intelligence System
Integrates TheSportsDB venue data to improve stadium coordinate accuracy and weather precision.

This module enhances our existing weather intelligence by:
1. Cross-referencing our stadium database with TheSportsDB venue data
2. Improving GPS coordinate accuracy for weather forecasts
3. Adding missing stadium information and capacity data
4. Providing team logos and branding for enhanced reports

Author: EQ12 Weather Intelligence Team
Date: 2025-10-10
Version: 2.0.0 - TheSportsDB Integration Enhanced
"""

import argparse
import json
import logging
import time
from datetime import datetime

import requests


class EQ12EnhancedWeatherStadiumSystem:
    """Enhanced stadium weather system with TheSportsDB integration."""

    def __init__(self):
        """Initialize enhanced weather stadium system."""
        self.thesportsdb_base = "https://www.thesportsdb.com/api/v1/json/123"
        self.nws_base = "https://api.weather.gov"

        # Setup logging
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        # Our existing EQ12 stadium database (from college and NFL systems)
        self.eq12_stadiums = {
            # NFL Stadiums
            "Lambeau Field": {
                "city": "Green Bay",
                "state": "WI",
                "lat": 44.5013,
                "lon": -88.0622,
            },
            "MetLife Stadium": {
                "city": "East Rutherford",
                "state": "NJ",
                "lat": 40.8128,
                "lon": -74.0742,
            },
            "Arrowhead Stadium": {
                "city": "Kansas City",
                "state": "MO",
                "lat": 39.0489,
                "lon": -94.4839,
            },
            "Soldier Field": {
                "city": "Chicago",
                "state": "IL",
                "lat": 41.8623,
                "lon": -87.6167,
            },
            "AT&T Stadium": {
                "city": "Arlington",
                "state": "TX",
                "lat": 32.7473,
                "lon": -97.0945,
            },
            # College Stadiums (Sample from our analysis)
            "Michigan Stadium": {
                "city": "Ann Arbor",
                "state": "MI",
                "lat": 42.2658,
                "lon": -83.7488,
            },
            "Beaver Stadium": {
                "city": "University Park",
                "state": "PA",
                "lat": 40.8122,
                "lon": -77.8562,
            },
            "Ohio Stadium": {
                "city": "Columbus",
                "state": "OH",
                "lat": 40.0017,
                "lon": -83.0197,
            },
            "Tiger Stadium": {
                "city": "Baton Rouge",
                "state": "LA",
                "lat": 30.4118,
                "lon": -91.1838,
            },
            "Neyland Stadium": {
                "city": "Knoxville",
                "state": "TN",
                "lat": 35.9550,
                "lon": -83.9254,
            },
        }

        # Cache for API responses
        self.thesportsdb_cache = {}

    def enhance_stadium_with_thesportsdb(self, stadium_name: str) -> dict:
        """Enhance existing stadium data with TheSportsDB information."""

        # Rate limiting for free tier (30 requests/minute)
        time.sleep(2)

        try:
            # Search venue in TheSportsDB
            search_url = f"{self.thesportsdb_base}/searchvenues.php"
            params = {"v": stadium_name}

            self.logger.info(f"🔍 Searching TheSportsDB for: {stadium_name}")

            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()
            venue_data = response.json()

            if venue_data and venue_data.get("venues"):
                venue = venue_data["venues"][0]  # Take first match

                enhanced_data = {
                    "venue_found": True,
                    "official_name": venue.get("strVenue"),
                    "venue_id": venue.get("idVenue"),
                    "location": venue.get("strLocation"),
                    "country": venue.get("strCountry"),
                    "capacity": venue.get("intCapacity"),
                    "surface": venue.get("strSurface"),
                    "coordinates_thesportsdb": {
                        "lat": (
                            float(
                                venue.get("strLatitude")) if venue.get("strLatitude") else None),
                        "lon": (
                            float(
                                venue.get("strLongitude")) if venue.get("strLongitude") else None),
                    },
                    "images": {
                        "thumb": venue.get("strThumb"),
                        "fanart": venue.get("strFanart1"),
                        "stadium_image": venue.get("strStadium"),
                    },
                    "description": venue.get("strDescriptionEN"),
                    "website": venue.get("strWebsite"),
                }

                self.logger.info(f"✅ Enhanced data found for: {venue.get('strVenue')}")
                return enhanced_data

            else:
                self.logger.warning(
                    f"⚠️  No TheSportsDB data found for: {stadium_name}")
                return {"venue_found": False}

        except Exception as e:
            self.logger.error(f"❌ Error enhancing {stadium_name}: {e}")
            return {"venue_found": False, "error": str(e)}

    def get_enhanced_weather_forecast(
        self, stadium_name: str, enhanced_coords: dict | None = None
    ) -> dict:
        """Get weather forecast using enhanced coordinates if available."""

        # Use enhanced coordinates if available, otherwise fall back to EQ12 data
        if enhanced_coords and enhanced_coords.get(
                "lat") and enhanced_coords.get("lon"):
            lat, lon = enhanced_coords["lat"], enhanced_coords["lon"]
            coord_source = "TheSportsDB Enhanced"
            self.logger.info(f"🎯 Using enhanced coordinates for {stadium_name}")
        elif stadium_name in self.eq12_stadiums:
            eq12_data = self.eq12_stadiums[stadium_name]
            lat, lon = eq12_data["lat"], eq12_data["lon"]
            coord_source = "EQ12 Original"
            self.logger.info(f"📍 Using EQ12 coordinates for {stadium_name}")
        else:
            return {"error": f"No coordinates available for {stadium_name}"}

        try:
            # Get NWS grid point
            points_url = f"{self.nws_base}/points/{lat},{lon}"
            response = requests.get(points_url, timeout=30)
            response.raise_for_status()
            point_data = response.json()

            # Extract forecast URL
            forecast_url = point_data["properties"]["forecast"]

            # Get detailed forecast
            forecast_response = requests.get(forecast_url, timeout=30)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            # Process current and upcoming periods
            periods = forecast_data["properties"]["periods"][:3]  # Next 3 periods

            weather_summary = {
                "stadium": stadium_name,
                "coordinate_source": coord_source,
                "coordinates": {"lat": lat, "lon": lon},
                "forecast_periods": [],
            }

            for period in periods:
                period_info = {
                    "name": period["name"],
                    "temperature": period["temperature"],
                    "temperature_unit": period["temperatureUnit"],
                    "wind_speed": period["windSpeed"],
                    "wind_direction": period["windDirection"],
                    "short_forecast": period["shortForecast"],
                    "detailed_forecast": period["detailedForecast"],
                    "precipitation_probability": period.get(
                        "probabilityOfPrecipitation",
                        {}).get(
                        "value",
                        0),
                }
                weather_summary["forecast_periods"].append(period_info)

            self.logger.info(f"🌤️  Weather forecast retrieved for {stadium_name}")
            return weather_summary

        except Exception as e:
            self.logger.error(f"❌ Weather forecast error for {stadium_name}: {e}")
            return {"error": f"Weather forecast failed: {e}"}

    def compare_coordinate_accuracy(
            self,
            stadium_name: str,
            enhanced_data: dict) -> dict:
        """Compare EQ12 coordinates with TheSportsDB coordinates for accuracy analysis."""

        if not enhanced_data.get("venue_found"):
            return {"comparison": "No TheSportsDB data available"}

        enhanced_coords = enhanced_data.get("coordinates_thesportsdb", {})
        if not enhanced_coords.get("lat") or not enhanced_coords.get("lon"):
            return {"comparison": "No coordinates in TheSportsDB data"}

        if stadium_name not in self.eq12_stadiums:
            return {"comparison": "No EQ12 coordinates to compare"}

        eq12_coords = self.eq12_stadiums[stadium_name]

        # Calculate coordinate differences
        lat_diff = abs(eq12_coords["lat"] - enhanced_coords["lat"])
        lon_diff = abs(eq12_coords["lon"] - enhanced_coords["lon"])

        # Rough distance calculation (degrees to meters approximation)
        lat_meters = lat_diff * 111000  # ~111km per degree latitude
        lon_meters = (
            lon_diff * 111000 * abs(eq12_coords["lat"] / 90)
        )  # Longitude varies by latitude

        total_difference = (lat_meters**2 + lon_meters**2) ** 0.5

        accuracy_analysis = {
            "eq12_coordinates": eq12_coords,
            "thesportsdb_coordinates": enhanced_coords,
            "differences": {
                "latitude_degrees": lat_diff,
                "longitude_degrees": lon_diff,
                "approximate_distance_meters": round(total_difference, 2),
            },
            "recommendation": (
                "Use TheSportsDB coordinates"
                if total_difference > 100
                else "EQ12 coordinates acceptable"
            ),
            "accuracy_impact": (
                "HIGH" if total_difference > 500 else "MEDIUM" if total_difference > 100 else "LOW"
            ),
        }

        return accuracy_analysis

    def generate_enhanced_stadium_report(self) -> dict:
        """Generate comprehensive stadium enhancement report."""

        self.logger.info("🏟️  Generating comprehensive stadium enhancement report")

        enhancement_results = {}
        coordinate_improvements = []
        missing_data_found = []

        for stadium_name in self.eq12_stadiums:
            self.logger.info(f"Processing: {stadium_name}")

            # Enhance with TheSportsDB data
            enhanced_data = self.enhance_stadium_with_thesportsdb(stadium_name)

            # Compare coordinate accuracy
            coord_comparison = self.compare_coordinate_accuracy(
                stadium_name, enhanced_data)

            # Get weather with both coordinate sets if available
            weather_eq12 = self.get_enhanced_weather_forecast(stadium_name)

            enhanced_coords = None
            if enhanced_data.get("venue_found") and enhanced_data.get(
                    "coordinates_thesportsdb"):
                enhanced_coords = enhanced_data["coordinates_thesportsdb"]

            weather_enhanced = None
            if enhanced_coords:
                weather_enhanced = self.get_enhanced_weather_forecast(
                    stadium_name, enhanced_coords)

            # Compile results
            stadium_results = {
                "thesportsdb_enhancement": enhanced_data,
                "coordinate_comparison": coord_comparison,
                "weather_eq12_coords": weather_eq12,
                "weather_enhanced_coords": weather_enhanced,
            }

            enhancement_results[stadium_name] = stadium_results

            # Track improvements
            if coord_comparison.get(
                    "differences",
                    {}).get(
                    "approximate_distance_meters",
                    0) > 100:
                coordinate_improvements.append(
                    {
                        "stadium": stadium_name,
                        "improvement_meters": coord_comparison["differences"][
                            "approximate_distance_meters"
                        ],
                        "impact": coord_comparison.get("accuracy_impact", "UNKNOWN"),
                    }
                )

            # Track missing data we found
            if enhanced_data.get("venue_found"):
                missing_info = []
                if enhanced_data.get("capacity"):
                    missing_info.append(f"Capacity: {enhanced_data['capacity']}")
                if enhanced_data.get("surface"):
                    missing_info.append(f"Surface: {enhanced_data['surface']}")
                if enhanced_data.get("images", {}).get("stadium_image"):
                    missing_info.append("Stadium imagery available")

                if missing_info:
                    missing_data_found.append(
                        {"stadium": stadium_name, "new_data": missing_info})

        # Generate summary report
        summary_report = {
            "enhancement_date": datetime.now().isoformat(),
            "stadiums_processed": len(self.eq12_stadiums),
            "thesportsdb_matches": len(
                [
                    s
                    for s in enhancement_results.values()
                    if s["thesportsdb_enhancement"].get("venue_found")
                ]
            ),
            "coordinate_improvements": coordinate_improvements,
            "new_data_discovered": missing_data_found,
            "detailed_results": enhancement_results,
            "recommendations": {
                "high_priority_coord_updates": [
                    s for s in coordinate_improvements if s["impact"] == "HIGH"
                ],
                "medium_priority_updates": [
                    s for s in coordinate_improvements if s["impact"] == "MEDIUM"
                ],
                "integration_benefits": [
                    "More accurate weather forecasts from precise coordinates",
                    "Stadium capacity and surface data for enhanced analysis",
                    "Professional stadium imagery for reporting",
                    "Official venue names and descriptions",
                    "Cross-validation of existing coordinate accuracy",
                ],
            },
        }

        self.logger.info(
            f"📊 Enhancement complete: {
                summary_report['thesportsdb_matches']}/{
                summary_report['stadiums_processed']} stadiums enhanced")

        return summary_report


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="EQ12 Enhanced Stadium Weather Intelligence System"
    )
    parser.add_argument("--stadium", help="Enhance specific stadium")
    parser.add_argument(
        "--full-report",
        action="store_true",
        help="Generate comprehensive enhancement report",
    )
    parser.add_argument(
        "--compare-coords",
        help="Compare coordinates for specific stadium")
    parser.add_argument(
        "--weather-test",
        help="Test weather forecast with enhanced coordinates")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize system
    system = EQ12EnhancedWeatherStadiumSystem()

    try:
        if args.stadium:
            print(f"🏟️  ENHANCING STADIUM: {args.stadium}")
            print("=" * 60)

            enhanced_data = system.enhance_stadium_with_thesportsdb(args.stadium)
            coord_comparison = system.compare_coordinate_accuracy(
                args.stadium, enhanced_data)

            print(
                json.dumps(
                    {
                        "enhancement": enhanced_data,
                        "coordinate_analysis": coord_comparison,
                    },
                    indent=2,
                )
            )

        elif args.compare_coords:
            print(f"📍 COORDINATE COMPARISON: {args.compare_coords}")
            print("=" * 60)

            enhanced_data = system.enhance_stadium_with_thesportsdb(args.compare_coords)
            comparison = system.compare_coordinate_accuracy(
                args.compare_coords, enhanced_data)

            print(json.dumps(comparison, indent=2))

        elif args.weather_test:
            print(f"🌤️  WEATHER FORECAST TEST: {args.weather_test}")
            print("=" * 60)

            # Test with original coordinates
            weather_original = system.get_enhanced_weather_forecast(args.weather_test)
            print("ORIGINAL COORDINATES FORECAST:")
            print(json.dumps(weather_original, indent=2))

            # Test with enhanced coordinates if available
            enhanced_data = system.enhance_stadium_with_thesportsdb(args.weather_test)
            if enhanced_data.get("venue_found") and enhanced_data.get(
                    "coordinates_thesportsdb"):
                print("\nENHANCED COORDINATES FORECAST:")
                weather_enhanced = system.get_enhanced_weather_forecast(
                    args.weather_test, enhanced_data["coordinates_thesportsdb"]
                )
                print(json.dumps(weather_enhanced, indent=2))

        elif args.full_report:
            print("🚀 EQ12 ENHANCED STADIUM WEATHER INTELLIGENCE REPORT")
            print("=" * 60)

            report = system.generate_enhanced_stadium_report()

            print("📊 SUMMARY")
            print(f"   Stadiums Processed: {report['stadiums_processed']}")
            print(f"   TheSportsDB Matches: {report['thesportsdb_matches']}")
            print(
                f"   Coordinate Improvements: {len(report['coordinate_improvements'])}")
            print(f"   New Data Discovered: {len(report['new_data_discovered'])}")
            print()

            if report["coordinate_improvements"]:
                print("🎯 COORDINATE ACCURACY IMPROVEMENTS:")
                for improvement in report["coordinate_improvements"]:
                    impact_icon = {
                        "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[
                        improvement["impact"]]
                    print(
                        f"   {impact_icon} {
                            improvement['stadium']}: {
                            improvement['improvement_meters']:.1f}m improvement")
                print()

            if report["new_data_discovered"]:
                print("📋 NEW DATA DISCOVERED:")
                for data in report["new_data_discovered"]:
                    print(f"   🏟️  {data['stadium']}: {', '.join(data['new_data'])}")
                print()

            # Save comprehensive results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"C:/EQ12/logs/enhanced_stadium_weather_report_{timestamp}.json"

            with open(results_file, "w") as f:
                json.dump(report, f, indent=2, default=str)

            print(f"💾 Full report saved to: {results_file}")

        else:
            # Default: Show available stadiums and basic info
            print("🏟️  EQ12 ENHANCED STADIUM WEATHER SYSTEM")
            print("=" * 60)
            print(f"Available stadiums: {len(system.eq12_stadiums)}")

            for stadium in list(system.eq12_stadiums.keys())[:5]:
                print(f"   • {stadium}")

            print("\nUse --full-report for comprehensive analysis")
            print("Use --stadium 'Stadium Name' for individual enhancement")
            print("Use --weather-test 'Stadium Name' for weather forecast comparison")

        print("\n✅ EQ12 Enhanced Stadium Weather Intelligence Complete!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        logging.exception("Enhanced stadium system error")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
