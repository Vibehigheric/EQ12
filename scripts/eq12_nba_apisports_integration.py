#!/usr/bin/env python3
"""
EQ12 NBA API-Sports.io Integration System
Enhanced NBA betting intelligence with real-time data integration
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import UTC, datetime, timedelta
from typing import Any

import requests

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/nba_apisports.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class EQ12NBAAPISportsIntegration:
    """
    EQ12 NBA API-Sports.io Integration for Premium NBA Betting Intelligence
    """

    def __init__(self, api_key: str | None = None):
        """Initialize NBA API-Sports integration with premium features"""
        self.api_key = api_key or os.getenv(
            "APISPORTS_NBA_KEY", "8716c77c5ce79d828b73eccc10819a10")

        # API-Sports.io endpoints and configuration
        self.base_urls = {
            "rapidapi": "https://api-basketball.p.rapidapi.com",
            "direct": "https://v3.basketball.api-sports.io",  # Direct API-Sports access
        }

        self.headers_rapidapi = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "api-basketball.p.rapidapi.com",
        }

        self.headers_direct = {"x-apisports-key": self.api_key}

        # NBA League IDs for different providers
        self.nba_leagues = {
            "nba_main": 12,  # NBA Main League
            "nba_summer": 16,  # NBA Summer League
            "nba_preseason": 15,  # NBA Preseason
        }

        self.session = requests.Session()
        self.rate_limit_delay = 1.0  # 1 second between requests for safety

        logger.info("🏀 EQ12 NBA API-Sports Integration initialized")
        logger.info(f"🔑 API Key configured: {self.api_key[:8]}...")

    def test_api_access(self) -> dict[str, Any]:
        """Test API access and determine best endpoint"""
        logger.info("🧪 Testing NBA API-Sports access...")

        test_results = {
            "rapidapi_access": False,
            "direct_access": False,
            "best_endpoint": None,
            "account_info": None,
            "rate_limits": None,
        }

        # Test RapidAPI endpoint
        try:
            url = f"{self.base_urls['rapidapi']}/status"
            response = self.session.get(url, headers=self.headers_rapidapi, timeout=10)

            if response.status_code == 200:
                test_results["rapidapi_access"] = True
                test_results["best_endpoint"] = "rapidapi"
                logger.info("✅ RapidAPI endpoint accessible")

                data = response.json()
                if "response" in data:
                    test_results["account_info"] = data["response"]

        except Exception as e:
            logger.warning(f"⚠️ RapidAPI endpoint failed: {e}")

        # Test direct API-Sports endpoint
        try:
            url = f"{self.base_urls['direct']}/status"
            response = self.session.get(url, headers=self.headers_direct, timeout=10)

            if response.status_code == 200:
                test_results["direct_access"] = True
                if not test_results["best_endpoint"]:
                    test_results["best_endpoint"] = "direct"
                logger.info("✅ Direct API-Sports endpoint accessible")

                data = response.json()
                if "response" in data:
                    test_results["account_info"] = data["response"]

        except Exception as e:
            logger.warning(f"⚠️ Direct API-Sports endpoint failed: {e}")

        return test_results

    def get_nba_teams(self) -> dict[str, Any]:
        """Get all NBA teams with enhanced data"""
        logger.info("🏀 Fetching NBA teams...")

        test_access = self.test_api_access()
        if not test_access["best_endpoint"]:
            logger.error("❌ No API endpoint accessible")
            return {"success": False, "error": "No API access"}

        endpoint = test_access["best_endpoint"]
        base_url = self.base_urls[endpoint]
        headers = self.headers_rapidapi if endpoint == "rapidapi" else self.headers_direct

        try:
            url = f"{base_url}/teams"
            params = {"league": self.nba_leagues["nba_main"], "season": "2024-2025"}

            response = self.session.get(url, headers=headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Retrieved NBA teams data")
                return {
                    "success": True,
                    "teams": data.get("response", []),
                    "endpoint_used": endpoint,
                    "total_teams": len(data.get("response", [])),
                }
            else:
                logger.error(f"❌ NBA teams request failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"❌ NBA teams request error: {e}")
            return {"success": False, "error": str(e)}

    def get_live_nba_games(self) -> dict[str, Any]:
        """Get live NBA games with real-time data"""
        logger.info("🎮 Fetching live NBA games...")

        test_access = self.test_api_access()
        if not test_access["best_endpoint"]:
            logger.error("❌ No API endpoint accessible")
            return {"success": False, "error": "No API access"}

        endpoint = test_access["best_endpoint"]
        base_url = self.base_urls[endpoint]
        headers = self.headers_rapidapi if endpoint == "rapidapi" else self.headers_direct

        try:
            # Get today's games
            today = datetime.now().strftime("%Y-%m-%d")
            url = f"{base_url}/games"
            params = {
                "league": self.nba_leagues["nba_main"],
                "season": "2024-2025",
                "date": today,
            }

            response = self.session.get(url, headers=headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                games = data.get("response", [])

                # Filter for live games
                live_games = []
                for game in games:
                    if game.get("status", {}).get("short") in [
                        "1H",
                        "2H",
                        "3H",
                        "4H",
                        "OT",
                        "HT",
                    ]:
                        live_games.append(game)

                logger.info(f"🎮 Found {len(live_games)} live NBA games")
                return {
                    "success": True,
                    "live_games": live_games,
                    "total_today": len(games),
                    "endpoint_used": endpoint,
                    "date_checked": today,
                }
            else:
                logger.error(f"❌ Live games request failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"❌ Live games request error: {e}")
            return {"success": False, "error": str(e)}

    def get_nba_odds(self, game_id: int | None = None) -> dict[str, Any]:
        """Get NBA betting odds for games"""
        logger.info(
            f"💰 Fetching NBA odds{
                f' for game {game_id}' if game_id else ''}...")

        test_access = self.test_api_access()
        if not test_access["best_endpoint"]:
            logger.error("❌ No API endpoint accessible")
            return {"success": False, "error": "No API access"}

        endpoint = test_access["best_endpoint"]
        base_url = self.base_urls[endpoint]
        headers = self.headers_rapidapi if endpoint == "rapidapi" else self.headers_direct

        try:
            url = f"{base_url}/odds"
            params = {"league": self.nba_leagues["nba_main"]}

            if game_id:
                params["game"] = game_id
            else:
                # Get today's odds
                params["date"] = datetime.now().strftime("%Y-%m-%d")

            response = self.session.get(url, headers=headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                odds_data = data.get("response", [])

                logger.info(f"💰 Retrieved odds for {len(odds_data)} games")
                return {
                    "success": True,
                    "odds": odds_data,
                    "endpoint_used": endpoint,
                    "game_id": game_id,
                }
            else:
                logger.error(f"❌ Odds request failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"❌ Odds request error: {e}")
            return {"success": False, "error": str(e)}

    def generate_nba_intelligence_report(self) -> dict[str, Any]:
        """Generate comprehensive NBA intelligence report"""
        logger.info("📊 Generating comprehensive NBA intelligence report...")

        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "api_status": None,
            "teams_analysis": None,
            "live_games": None,
            "betting_opportunities": [],
            "system_health": "unknown",
        }

        # Test API access
        api_test = self.test_api_access()
        report["api_status"] = api_test

        if api_test["best_endpoint"]:
            logger.info("✅ API access confirmed, gathering intelligence...")

            # Get teams data
            teams_data = self.get_nba_teams()
            report["teams_analysis"] = teams_data

            # Get live games
            live_games = self.get_live_nba_games()
            report["live_games"] = live_games

            # Analyze betting opportunities
            if live_games.get("success") and live_games.get("live_games"):
                for game in live_games["live_games"]:
                    opportunity = {
                        "game_id": game.get("id"),
                        "teams": f"{game.get(
                            'teams',
                            {}).get('away',
                                    {}).get('name',
                                            'Unknown')} @ {game.get('teams',
                                                                    {}).get('home',
                                                                            {}).get('name',
                                                                                    'Unknown'
                                                                                    )}",
                        "status": game.get("status", {}).get("long", "Unknown"),
                        "score": f"{game.get(
                            'scores',
                            {}).get('away',
                                    {}).get('total',
                                            0)} - {game.get('scores',
                                                            {}).get('home',
                                                                    {}).get('total',
                                                                            0
                                                                            )}",
                        "betting_value": (
                            "HIGH"
                            if game.get("status", {}).get("short") in ["4H", "OT"]
                            else "MEDIUM"
                        ),
                    }
                    report["betting_opportunities"].append(opportunity)

            report["system_health"] = "operational"
        else:
            logger.warning("⚠️ API access issues detected")
            report["system_health"] = "degraded"

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"C:/EQ12/logs/nba_intelligence_report_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"📋 NBA intelligence report saved: {report_file}")
        return report


def main():
    """Main execution function with comprehensive NBA intelligence"""
    parser = argparse.ArgumentParser(description="EQ12 NBA API-Sports Integration")
    parser.add_argument("--api-key", help="API-Sports.io API key")
    parser.add_argument("--test-access", action="store_true", help="Test API access")
    parser.add_argument("--get-teams", action="store_true", help="Get NBA teams")
    parser.add_argument("--live-games", action="store_true", help="Get live games")
    parser.add_argument("--get-odds", action="store_true", help="Get betting odds")
    parser.add_argument(
        "--intelligence-report",
        action="store_true",
        help="Generate intelligence report",
    )
    parser.add_argument("--monitor", type=int, help="Monitor live games for N minutes")

    args = parser.parse_args()

    # Initialize NBA integration
    nba_system = EQ12NBAAPISportsIntegration(api_key=args.api_key)

    print("🏀 EQ12 NBA API-SPORTS INTEGRATION SYSTEM")
    print("=" * 80)

    if args.test_access:
        print("🧪 Testing API access...")
        result = nba_system.test_api_access()
        print(f"📊 Access Results: {json.dumps(result, indent=2)}")

    elif args.get_teams:
        print("🏀 Retrieving NBA teams...")
        result = nba_system.get_nba_teams()
        if result["success"]:
            print(f"✅ Found {result['total_teams']} NBA teams")
        else:
            print(f"❌ Error: {result['error']}")

    elif args.live_games:
        print("🎮 Checking live NBA games...")
        result = nba_system.get_live_nba_games()
        if result["success"]:
            print(
                f"🎮 Found {len(result['live_games'])} live games out of {result['total_today']} today"
            )
            for game in result["live_games"]:
                away_team = game.get("teams", {}).get("away", {}).get("name", "Unknown")
                home_team = game.get("teams", {}).get("home", {}).get("name", "Unknown")
                status = game.get("status", {}).get("long", "Unknown")
                print(f"   🏀 {away_team} @ {home_team} - {status}")
        else:
            print(f"❌ Error: {result['error']}")

    elif args.get_odds:
        print("💰 Retrieving NBA betting odds...")
        result = nba_system.get_nba_odds()
        if result["success"]:
            print(f"💰 Found odds for {len(result['odds'])} games")
        else:
            print(f"❌ Error: {result['error']}")

    elif args.intelligence_report:
        print("📊 Generating NBA intelligence report...")
        result = nba_system.generate_nba_intelligence_report()
        print(f"📋 Report status: {result['system_health']}")

    elif args.monitor:
        print(f"⏰ Starting {args.monitor}-minute NBA live monitoring...")
        end_time = datetime.now() + timedelta(minutes=args.monitor)

        while datetime.now() < end_time:
            result = nba_system.get_live_nba_games()
            if result["success"] and result["live_games"]:
                print(f"🎮 {len(result['live_games'])} live games detected:")
                for game in result["live_games"]:
                    away_team = game.get(
                        "teams",
                        {}).get(
                        "away",
                        {}).get(
                        "name",
                        "Unknown")
                    home_team = game.get(
                        "teams",
                        {}).get(
                        "home",
                        {}).get(
                        "name",
                        "Unknown")
                    status = game.get("status", {}).get("long", "Unknown")
                    away_score = game.get("scores", {}).get("away", {}).get("total", 0)
                    home_score = game.get("scores", {}).get("home", {}).get("total", 0)
                    print(
                        f"   🏀 {away_team} {away_score} - {home_score} {home_team} ({status})")
            else:
                print("🔍 No live NBA games currently")

            time.sleep(60)  # Check every minute

    else:
        # Default: run intelligence report
        print("📊 Running default NBA intelligence analysis...")
        result = nba_system.generate_nba_intelligence_report()

        print("\n📋 NBA Intelligence Summary:")
        print(
            f"   🔌 API Status: {
                '✅ Active' if result['api_status']['best_endpoint'] else '❌ Offline'}")

        if result["teams_analysis"] and result["teams_analysis"]["success"]:
            print(f"   🏀 NBA Teams: {result['teams_analysis']['total_teams']} loaded")

        if result["live_games"] and result["live_games"]["success"]:
            live_count = len(result["live_games"]["live_games"])
            total_count = result["live_games"]["total_today"]
            print(f"   🎮 Live Games: {live_count}/{total_count} games active today")

        betting_ops = len(result["betting_opportunities"])
        print(f"   💰 Betting Opportunities: {betting_ops} identified")

        print(f"   🏥 System Health: {result['system_health'].upper()}")

    print("\n✅ EQ12 NBA API-Sports Integration Complete!")


if __name__ == "__main__":
    main()
