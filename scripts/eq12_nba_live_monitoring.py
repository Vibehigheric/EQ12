#!/usr/bin/env python3
"""
EQ12 NBA Live Monitoring System
Real-time NBA game monitoring with betting intelligence and weather correlation
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

# Import our NBA Weather Intelligence
sys.path.append("C:/EQ12/scripts")
try:
    from eq12_nba_weather_intelligence import EQ12NBAWeatherIntelligence
except ImportError:
    logger.warning("NBA Weather Intelligence module not available")
    EQ12NBAWeatherIntelligence = None

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/nba_live_monitoring.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class EQ12NBALiveMonitoring:
    """
    EQ12 NBA Live Monitoring System
    Real-time game monitoring with integrated weather intelligence and betting alerts
    """

    def __init__(self, api_key: str | None = None):
        """Initialize NBA Live Monitoring System"""
        self.api_key = api_key or os.getenv(
            "NBA_API_KEY", "8716c77c5ce79d828b73eccc10819a10")

        # Initialize weather intelligence if available
        self.weather_intel = EQ12NBAWeatherIntelligence() if EQ12NBAWeatherIntelligence else None

        # NBA game simulation data for demo (since API access limited)
        self.simulated_games = [
            {
                "id": "nba_20251010_001",
                "away_team": "Boston Celtics",
                "home_team": "Los Angeles Lakers",
                "status": "Live",
                "period": "2nd Quarter",
                "time_remaining": "8:42",
                "away_score": 52,
                "home_score": 48,
                "last_play": "Tatum 3-point shot made (assisted by Brown)",
                "betting_line": {
                    "spread": -2.5,
                    "total": 218.5,
                    "ml_home": +110,
                    "ml_away": -130,
                },
            },
            {
                "id": "nba_20251010_002",
                "away_team": "Miami Heat",
                "home_team": "Denver Nuggets",
                "status": "Live",
                "period": "3rd Quarter",
                "time_remaining": "5:23",
                "away_score": 78,
                "home_score": 82,
                "last_play": "Jokic offensive rebound and putback",
                "betting_line": {
                    "spread": -4.0,
                    "total": 225.0,
                    "ml_home": -180,
                    "ml_away": +150,
                },
            },
            {
                "id": "nba_20251010_003",
                "away_team": "Golden State Warriors",
                "home_team": "Chicago Bulls",
                "status": "Pre-Game",
                "start_time": "20:00 ET",
                "betting_line": {
                    "spread": -6.5,
                    "total": 232.0,
                    "ml_home": +240,
                    "ml_away": -300,
                },
            },
            {
                "id": "nba_20251010_004",
                "away_team": "Phoenix Suns",
                "home_team": "Milwaukee Bucks",
                "status": "Pre-Game",
                "start_time": "20:30 ET",
                "betting_line": {
                    "spread": -3.0,
                    "total": 228.5,
                    "ml_home": -140,
                    "ml_away": +120,
                },
            },
        ]

        # Betting opportunity thresholds
        self.opportunity_thresholds = {
            "score_differential": 10,  # Points difference from expected
            "momentum_shift": 8,  # Points in last 5 minutes
            "pace_change": 15,  # Total vs expected at time
            "weather_factor": 1.15,  # Weather impact multiplier
        }

        self.session = requests.Session()
        logger.info("NBA Live Monitoring System initialized")
        logger.info(
            f"Weather Intelligence: {
                'Enabled' if self.weather_intel else 'Disabled'}")

    def get_live_nba_games(self) -> list[dict[str, Any]]:
        """Get current live NBA games (simulated for demo)"""
        logger.info("Fetching live NBA games...")

        # Simulate realistic game progression
        current_time = datetime.now()

        live_games = []
        for game in self.simulated_games:
            if game["status"] == "Live":
                # Simulate score changes
                if game["id"] == "nba_20251010_001":  # Celtics vs Lakers
                    game["away_score"] += 2 if current_time.second % 30 < 15 else 0
                    game["home_score"] += 3 if current_time.second % 20 < 10 else 0

                elif game["id"] == "nba_20251010_002":  # Heat vs Nuggets
                    game["away_score"] += 1 if current_time.second % 25 < 12 else 0
                    game["home_score"] += 2 if current_time.second % 35 < 18 else 0

                live_games.append(game)

        logger.info(f"Found {len(live_games)} live NBA games")
        return live_games

    def analyze_betting_opportunities(
            self, live_games: list[dict]) -> list[dict[str, Any]]:
        """Analyze live games for betting opportunities"""
        opportunities = []

        for game in live_games:
            opportunity = {
                "game_id": game["id"],
                "matchup": f"{game['away_team']} @ {game['home_team']}",
                "current_score": f"{game['away_score']} - {game['home_score']}",
                "status": f"{game['status']} - {game.get('period', 'Unknown')}",
                "opportunities": [],
                "weather_factor": 1.0,
                "overall_rating": "STANDARD",
            }

            # Analyze score differential vs expectations
            if "betting_line" in game:
                spread = game["betting_line"].get("spread", 0)
                actual_diff = game["home_score"] - game["away_score"]
                expected_diff = -spread  # Negative spread means home favored

                differential = abs(actual_diff - expected_diff)

                if differential >= self.opportunity_thresholds["score_differential"]:
                    opportunity["opportunities"].append(
                        {
                            "type": "SPREAD_VALUE",
                            "description": f"Large deviation from expected spread ({differential:.1f} points)",
                            "confidence": "HIGH" if differential > 15 else "MEDIUM",
                        }
                    )

            # Analyze total points progression
            if "betting_line" in game and game["status"] == "Live":
                total_line = game["betting_line"].get("total", 0)
                current_total = game["away_score"] + game["home_score"]

                # Estimate final total based on current pace
                periods_played = 1.5 if "2nd" in game.get("period", "") else 2.5
                estimated_final = (current_total / periods_played) * 4

                total_diff = abs(estimated_final - total_line)

                if total_diff >= self.opportunity_thresholds["pace_change"]:
                    opportunity["opportunities"].append(
                        {
                            "type": "TOTAL_VALUE",
                            "description": f"Pace suggests {
                                'over' if estimated_final > total_line else 'under'} ({
                                estimated_final:.1f} vs {total_line})",
                            "confidence": "MEDIUM",
                        })

            # Add weather intelligence if available
            if self.weather_intel:
                try:
                    weather_analysis = self.weather_intel.analyze_matchup_weather_intelligence(
                        game["home_team"], game["away_team"])

                    if weather_analysis.get("betting_edge"):
                        edge = weather_analysis["betting_edge"]
                        if edge["edge_strength"] > 0.05:
                            opportunity["weather_factor"] = 1.0 + edge["edge_strength"]
                            opportunity["opportunities"].append(
                                {
                                    "type": "WEATHER_EDGE",
                                    "description": f"Weather advantage for {
                                        edge['recommended_side']} team",
                                    "confidence": edge["confidence"],
                                })

                except Exception as e:
                    logger.warning(f"Weather analysis error: {e}")

            # Calculate overall opportunity rating
            if len(opportunity["opportunities"]) >= 2:
                opportunity["overall_rating"] = "HIGH_VALUE"
            elif len(opportunity["opportunities"]) == 1:
                opportunity["overall_rating"] = "MEDIUM_VALUE"

            # Apply weather factor to rating
            if opportunity["weather_factor"] > self.opportunity_thresholds["weather_factor"]:
                if opportunity["overall_rating"] == "MEDIUM_VALUE":
                    opportunity["overall_rating"] = "HIGH_VALUE"
                elif opportunity["overall_rating"] == "STANDARD":
                    opportunity["overall_rating"] = "MEDIUM_VALUE"

            opportunities.append(opportunity)

        return opportunities

    def monitor_live_games(self, duration_minutes: int = 30) -> dict[str, Any]:
        """Monitor live NBA games for specified duration"""
        logger.info(f"Starting {duration_minutes}-minute live NBA monitoring...")

        monitoring_results = {
            "start_time": datetime.now().isoformat(),
            "duration_minutes": duration_minutes,
            "total_checks": 0,
            "opportunities_found": 0,
            "alerts_sent": 0,
            "monitoring_log": [],
        }

        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        check_interval = 60  # Check every minute

        while datetime.now() < end_time:
            try:
                check_time = datetime.now()
                monitoring_results["total_checks"] += 1

                # Get live games
                live_games = self.get_live_nba_games()

                if live_games:
                    # Analyze opportunities
                    opportunities = self.analyze_betting_opportunities(live_games)

                    # Count high-value opportunities
                    high_value_count = sum(
                        1 for opp in opportunities if opp["overall_rating"] == "HIGH_VALUE")
                    monitoring_results["opportunities_found"] += high_value_count

                    # Log monitoring data
                    log_entry = {
                        "timestamp": check_time.isoformat(),
                        "live_games_count": len(live_games),
                        "opportunities_count": len(opportunities),
                        "high_value_count": high_value_count,
                        "games": [
                            {
                                "matchup": game["away_team"] + " @ " + game["home_team"],
                                "score": f"{game['away_score']} - {game['home_score']}",
                                "status": game.get("period", game["status"]),
                            }
                            for game in live_games
                        ],
                    }

                    monitoring_results["monitoring_log"].append(log_entry)

                    # Send alerts for high-value opportunities
                    for opp in opportunities:
                        if opp["overall_rating"] == "HIGH_VALUE":
                            self._send_betting_alert(opp)
                            monitoring_results["alerts_sent"] += 1

                    # Display real-time update
                    print(
                        f"\r🔄 {
                            check_time.strftime('%H:%M:%S')} - {
                            len(live_games)} live games, {high_value_count} high-value opportunities",
                        end="",
                        flush=True,
                    )

                else:
                    print(
                        f"\r🔄 {
                            check_time.strftime('%H:%M:%S')} - No live games detected",
                        end="",
                        flush=True,
                    )

                # Wait until next check
                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(10)  # Short pause on error

        monitoring_results["end_time"] = datetime.now().isoformat()

        # Save monitoring results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"C:/EQ12/logs/nba_monitoring_session_{timestamp}.json"

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(monitoring_results, f, indent=2, ensure_ascii=False)

        logger.info(f"Monitoring session complete. Results saved: {results_file}")
        return monitoring_results

    def _send_betting_alert(self, opportunity: dict[str, Any]) -> None:
        """Send betting opportunity alert"""
        alert_message = f"🚨 HIGH-VALUE NBA OPPORTUNITY: {opportunity['matchup']}"

        logger.info(f"BETTING ALERT: {alert_message}")
        logger.info(f"Current Score: {opportunity['current_score']}")
        logger.info(f"Status: {opportunity['status']}")
        logger.info(f"Weather Factor: {opportunity['weather_factor']:.3f}")

        for opp in opportunity["opportunities"]:
            logger.info(
                f"• {
                    opp['type']}: {
                    opp['description']} ({
                    opp['confidence']} confidence)")

    def generate_live_intelligence_report(self) -> dict[str, Any]:
        """Generate comprehensive live NBA intelligence report"""
        logger.info("Generating live NBA intelligence report...")

        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "live_games": self.get_live_nba_games(),
            "betting_opportunities": [],
            "weather_intelligence": None,
            "system_status": "operational",
        }

        # Analyze current opportunities
        if report["live_games"]:
            report["betting_opportunities"] = self.analyze_betting_opportunities(
                report["live_games"]
            )

        # Add weather intelligence summary
        if self.weather_intel:
            try:
                weather_report = self.weather_intel.generate_daily_nba_weather_report()
                report["weather_intelligence"] = {
                    "system_active": True, "weather_alerts": weather_report.get(
                        "weather_alerts_count", 0), "high_impact_venues": weather_report.get(
                        "high_impact_count", 0), "betting_opportunities": weather_report.get(
                        "betting_opportunities_count", 0), }
            except Exception as e:
                logger.warning(f"Weather intelligence error: {e}")
                report["weather_intelligence"] = {
                    "system_active": False,
                    "error": str(e),
                }

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"C:/EQ12/logs/nba_live_intelligence_report_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Live intelligence report saved: {report_file}")
        return report


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EQ12 NBA Live Monitoring System")
    parser.add_argument("--api-key", help="NBA API key")
    parser.add_argument(
        "--live-games",
        action="store_true",
        help="Get current live games")
    parser.add_argument(
        "--opportunities",
        action="store_true",
        help="Analyze current betting opportunities",
    )
    parser.add_argument("--monitor", type=int, help="Monitor live games for N minutes")
    parser.add_argument(
        "--intelligence-report",
        action="store_true",
        help="Generate live intelligence report",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demo monitoring session")

    args = parser.parse_args()

    # Initialize NBA Live Monitoring
    nba_monitor = EQ12NBALiveMonitoring(api_key=args.api_key)

    print("EQ12 NBA LIVE MONITORING SYSTEM")
    print("=" * 80)

    if args.live_games:
        print("Fetching current live NBA games...")
        games = nba_monitor.get_live_nba_games()

        if games:
            print(f"🏀 {len(games)} Live NBA Games:")
            for game in games:
                print(
                    f"   {
                        game['away_team']} {
                        game['away_score']} - {
                        game['home_score']} {
                        game['home_team']}")
                print(
                    f"      Status: {game['status']} - {game.get('period', 'Unknown')}")
        else:
            print("No live NBA games currently")

    elif args.opportunities:
        print("Analyzing current betting opportunities...")
        games = nba_monitor.get_live_nba_games()

        if games:
            opportunities = nba_monitor.analyze_betting_opportunities(games)

            for opp in opportunities:
                print(f"\n🎯 {opp['matchup']} - {opp['overall_rating']}")
                print(f"   Score: {opp['current_score']} | Status: {opp['status']}")
                print(f"   Weather Factor: {opp['weather_factor']:.3f}")

                for opportunity in opp["opportunities"]:
                    print(f"   • {opportunity['type']}: {opportunity['description']}")
        else:
            print("No live games available for opportunity analysis")

    elif args.monitor:
        print(f"Starting {args.monitor}-minute live monitoring session...")
        result = nba_monitor.monitor_live_games(args.monitor)

        print("\n📊 Monitoring Session Complete:")
        print(f"   Duration: {result['duration_minutes']} minutes")
        print(f"   Total Checks: {result['total_checks']}")
        print(f"   Opportunities Found: {result['opportunities_found']}")
        print(f"   Alerts Sent: {result['alerts_sent']}")

    elif args.intelligence_report:
        print("Generating live NBA intelligence report...")
        result = nba_monitor.generate_live_intelligence_report()

        print("\n📋 Live NBA Intelligence Summary:")
        print(f"   Live Games: {len(result['live_games'])}")
        print(f"   Betting Opportunities: {len(result['betting_opportunities'])}")

        if result["weather_intelligence"]:
            weather = result["weather_intelligence"]
            if weather["system_active"]:
                print("   Weather Intelligence: ACTIVE")
                print(f"      Weather Alerts: {weather['weather_alerts']}")
                print(f"      High-Impact Venues: {weather['high_impact_venues']}")
            else:
                print("   Weather Intelligence: INACTIVE")

    elif args.demo:
        print("Running NBA Live Monitoring Demo...")
        print("This demo simulates live game monitoring with betting intelligence")
        print("Press Ctrl+C to stop monitoring\n")

        result = nba_monitor.monitor_live_games(5)  # 5-minute demo

        print("\n🎉 Demo Complete!")
        print(f"   Monitoring Checks: {result['total_checks']}")
        print(f"   Opportunities Detected: {result['opportunities_found']}")

    else:
        # Default: run intelligence report
        print("Running default NBA live intelligence analysis...")
        result = nba_monitor.generate_live_intelligence_report()

        print("\nNBA Live Intelligence Dashboard:")
        print(f"   System Status: {result['system_status'].upper()}")
        print(f"   Live Games: {len(result['live_games'])}")

        high_value_count = sum(
            1 for opp in result["betting_opportunities"] if opp["overall_rating"] == "HIGH_VALUE")
        print(f"   High-Value Opportunities: {high_value_count}")

        if result["weather_intelligence"] and result["weather_intelligence"]["system_active"]:
            print("   Weather Intelligence: ACTIVE")
        else:
            print("   Weather Intelligence: INACTIVE")

    print("\n✅ EQ12 NBA Live Monitoring Complete!")


if __name__ == "__main__":
    main()
