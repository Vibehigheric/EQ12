#!/usr/bin/env python3
"""
EQ12 Real-Time Sports Intelligence System
Integrates TheSportsDB V2 API for live scores, real-time betting adjustments, and dynamic analysis.

This system provides:
1. Live score monitoring for active games
2. Real-time betting opportunity identification
3. Weather-enhanced live game analysis
4. Dynamic parlay adjustment recommendations
5. Prime-time game detection and prioritization

Author: EQ12 Weather Intelligence Team
Date: 2025-10-10
Version: 3.0.0 - Real-Time Intelligence Integration
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime, timedelta

import requests


class EQ12RealTimeSportsIntelligence:
    """Real-time sports intelligence system with TheSportsDB V2 integration."""

    def __init__(self, api_key: str | None = None):
        """Initialize real-time sports intelligence system."""
        self.base_url_v1 = "https://www.thesportsdb.com/api/v1/json/123"
        self.base_url_v2 = "https://www.thesportsdb.com/api/v2/json"
        self.api_key = api_key or os.getenv("THESPORTSDB_API_KEY")

        # Setup logging
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        # Initialize session for connection pooling
        self.session = requests.Session()

        # Real-time monitoring state
        self.live_games = {}
        self.monitoring_active = False
        self.score_alerts = []
        self.betting_opportunities = []

        # Sports configuration for EQ12 focus
        self.eq12_sports = {
            "american_football": {"display_name": "NFL", "priority": "HIGH"},
            "basketball": {"display_name": "NBA", "priority": "MEDIUM"},
            "ice_hockey": {"display_name": "NHL", "priority": "HIGH"},
            "baseball": {"display_name": "MLB", "priority": "MEDIUM"},
            "soccer": {"display_name": "Soccer", "priority": "LOW"},
        }

        # Alert thresholds for betting opportunities
        self.alert_config = {
            "large_score_change": 14,  # Points difference that triggers alert
            "momentum_shift_threshold": 10,  # Quick scoring in short time
            "overtime_alert": True,
            "close_game_threshold": 7,  # Points for close game alerts
        }

    def _make_v2_request(self, endpoint: str, params: dict |
                         None = None) -> dict | None:
        """Make V2 API request with premium authentication."""
        if not self.api_key:
            self.logger.error(
                "🔒 V2 API requires premium subscription - set THESPORTSDB_API_KEY")
            return None

        try:
            url = f"{self.base_url_v2}/{endpoint}"
            headers = {"X-API-KEY": self.api_key}

            response = self.session.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            self.logger.debug(f"✅ V2 API call successful: {endpoint}")
            return data

        except requests.RequestException as e:
            self.logger.error(f"❌ V2 API error for {endpoint}: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON decode error for {endpoint}: {e}")
            return None

    def get_live_scores_all_sports(self) -> dict:
        """Get live scores for all sports with EQ12 prioritization."""

        if not self.api_key:
            return {
                "error": "Premium API key required for live scores",
                "upgrade_info": "Subscribe to TheSportsDB Premium for €9/month",
                "demo_mode": True,
            }

        self.logger.info("📺 Fetching live scores across all sports")

        all_live_scores = {}
        priority_games = []

        for sport_key, sport_info in self.eq12_sports.items():
            self.logger.info(f"🔍 Checking live scores for {sport_info['display_name']}")

            # Get sport-specific live scores
            live_data = self._make_v2_request(f"livescore/{sport_key}")

            if live_data and live_data.get("events"):
                processed_events = []

                for event in live_data["events"]:
                    processed_event = {
                        "event_id": event.get("idEvent"),
                        "sport": sport_info["display_name"],
                        "sport_key": sport_key,
                        "date": event.get("dateEvent"),
                        "time": event.get("strTime"),
                        "home_team": event.get("strHomeTeam"),
                        "away_team": event.get("strAwayTeam"),
                        "home_score": int(event.get("intHomeScore") or 0),
                        "away_score": int(event.get("intAwayScore") or 0),
                        "status": event.get("strStatus"),
                        "progress": event.get("strProgress"),
                        "venue": event.get("strVenue"),
                        "round": event.get("intRound"),
                        "season": event.get("strSeason"),
                        "priority": sport_info["priority"],
                        "score_differential": abs(
                            int(event.get("intHomeScore") or 0)
                            - int(event.get("intAwayScore") or 0)
                        ),
                        "live_betting_value": self._calculate_live_betting_value(event, sport_key),
                    }
                    processed_events.append(processed_event)

                    # Add to priority games if high-value
                    if (
                        sport_info["priority"] == "HIGH"
                        or processed_event["score_differential"]
                        <= self.alert_config["close_game_threshold"]
                    ):
                        priority_games.append(processed_event)

                all_live_scores[sport_key] = {
                    "sport": sport_info["display_name"],
                    "event_count": len(processed_events),
                    "events": processed_events,
                }

                self.logger.info(
                    f"✅ Found {
                        len(processed_events)} live {
                        sport_info['display_name']} games")

            # Rate limiting for premium tier
            time.sleep(0.6)

        # Compile comprehensive report
        live_intelligence = {
            "timestamp": datetime.now().isoformat(),
            "total_sports": len(all_live_scores),
            "total_live_games": sum(sport["event_count"] for sport in all_live_scores.values()),
            "priority_games": sorted(
                priority_games, key=lambda x: x["live_betting_value"], reverse=True
            ),
            "sports_breakdown": all_live_scores,
            "betting_alerts": self._generate_betting_alerts(priority_games),
            "weather_correlation_opportunities": self._identify_weather_opportunities(
                priority_games
            ),
        }

        return live_intelligence

    def _calculate_live_betting_value(self, event: dict, sport_key: str) -> float:
        """Calculate live betting value score based on game situation."""

        home_score = int(event.get("intHomeScore") or 0)
        away_score = int(event.get("intAwayScore") or 0)
        score_diff = abs(home_score - away_score)
        total_score = home_score + away_score

        # Base value from close games
        value_score = 0.0

        # Close game bonus (higher value)
        if score_diff <= 3:
            value_score += 10.0
        elif score_diff <= 7:
            value_score += 7.0
        elif score_diff <= 14:
            value_score += 3.0

        # High-scoring game bonus
        if (sport_key == "american_football" and total_score > 45) or (
            sport_key == "basketball" and total_score > 200
        ):
            value_score += 5.0

        # Progress-based adjustments
        progress = event.get("strProgress", "").lower()
        if "overtime" in progress or "ot" in progress:
            value_score += 15.0  # Overtime = high value
        elif "final" in progress or "ended" in progress:
            value_score = 0.0  # Game over = no value

        # Status-based adjustments
        status = event.get("strStatus", "").lower()
        if "live" in status or "in progress" in status:
            value_score += 5.0

        return round(value_score, 2)

    def _generate_betting_alerts(self, priority_games: list[dict]) -> list[dict]:
        """Generate real-time betting alerts based on game situations."""

        alerts = []

        for game in priority_games:
            alert_reasons = []

            # Close game alerts
            if game["score_differential"] <= 3:
                alert_reasons.append(
                    f"CLOSE GAME: {
                        game['score_differential']} point difference")

            # High live betting value
            if game["live_betting_value"] >= 15:
                alert_reasons.append(
                    f"HIGH VALUE: {
                        game['live_betting_value']} betting score")

            # Overtime detection
            if game.get("progress", "").lower() in ["overtime", "ot"]:
                alert_reasons.append("OVERTIME: Maximum betting volatility")

            # Priority sport in close game
            if game["priority"] == "HIGH" and game["score_differential"] <= 7:
                alert_reasons.append(f"PRIORITY: {game['sport']} close game")

            if alert_reasons:
                alert = {
                    "game_id": game["event_id"],
                    "matchup": f"{game['home_team']} vs {game['away_team']}",
                    "sport": game["sport"],
                    "score": f"{game['home_score']} - {game['away_score']}",
                    "alert_level": ("HIGH" if game["live_betting_value"] >= 15 else "MEDIUM"),
                    "reasons": alert_reasons,
                    "live_betting_value": game["live_betting_value"],
                    "venue": game.get("venue"),
                    "recommended_action": self._get_betting_recommendation(game),
                }
                alerts.append(alert)

        return sorted(alerts, key=lambda x: x["live_betting_value"], reverse=True)

    def _get_betting_recommendation(self, game: dict) -> str:
        """Get specific betting recommendation based on game situation."""

        score_diff = game["score_differential"]
        live_value = game["live_betting_value"]

        if game.get("progress", "").lower() in ["overtime", "ot"]:
            return "MONITOR: Overtime = high volatility, wait for stabilization"
        elif score_diff <= 3 and live_value >= 10:
            return "ACTION: Consider live over/under or spread adjustments"
        elif score_diff <= 7 and game["priority"] == "HIGH":
            return "WATCH: Close high-priority game, prepare for movement"
        elif live_value >= 15:
            return "ALERT: High-value live betting opportunity identified"
        else:
            return "MONITOR: Track for potential opportunities"

    def _identify_weather_opportunities(self, priority_games: list[dict]) -> list[dict]:
        """Identify games where weather intelligence could enhance betting."""

        weather_opportunities = []

        for game in priority_games:
            venue = game.get("venue")
            sport = game.get("sport_key")

            # Focus on outdoor sports where weather matters
            if sport in ["american_football"] and venue:
                opportunity = {
                    "game_id": game["event_id"],
                    "matchup": f"{
                        game['home_team']} vs {
                        game['away_team']}",
                    "venue": venue,
                    "sport": game["sport"],
                    "weather_factor": (
                        "HIGH" if sport == "american_football" else "MEDIUM"),
                    "integration_potential": [
                        "Real-time weather impact on scoring",
                        "Wind effects on field goals/passing",
                        "Temperature impact on player performance",
                        "Precipitation effects on ball handling",
                    ],
                    "live_betting_value": game["live_betting_value"],
                }
                weather_opportunities.append(opportunity)

        return weather_opportunities

    def start_live_monitoring(
            self,
            duration_minutes: int = 30,
            update_interval: int = 60) -> dict:
        """Start continuous live score monitoring with alerts."""

        if not self.api_key:
            return {
                "error": "Premium API required for live monitoring",
                "demo_available": True,
                "upgrade_info": "Get real-time monitoring with TheSportsDB Premium €9/month",
            }

        self.logger.info(
            f"🔄 Starting live monitoring for {duration_minutes} minutes (updates every {update_interval}s)")

        monitoring_results = {
            "start_time": datetime.now().isoformat(),
            "duration_minutes": duration_minutes,
            "update_interval_seconds": update_interval,
            "updates": [],
            "total_alerts_generated": 0,
            "highest_value_opportunities": [],
        }

        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        update_count = 0

        while datetime.now() < end_time:
            update_count += 1
            self.logger.info(f"🔄 Live update #{update_count}")

            # Get current live scores
            live_data = self.get_live_scores_all_sports()

            if not live_data.get("error"):
                update_summary = {
                    "update_number": update_count,
                    "timestamp": datetime.now().isoformat(),
                    "total_live_games": live_data["total_live_games"],
                    "priority_games_count": len(
                        live_data["priority_games"]),
                    "new_alerts": len(
                        live_data["betting_alerts"]),
                    "top_opportunity": (
                        live_data["betting_alerts"][0] if live_data["betting_alerts"] else None),
                }

                monitoring_results["updates"].append(update_summary)
                monitoring_results["total_alerts_generated"] += update_summary["new_alerts"]

                # Track highest value opportunities
                if live_data["betting_alerts"]:
                    top_alert = live_data["betting_alerts"][0]
                    monitoring_results["highest_value_opportunities"].append(top_alert)

                self.logger.info(
                    f"📊 Update {update_count}: {
                        live_data['total_live_games']} live games, {
                        len(
                            live_data['betting_alerts'])} alerts")

                # Show real-time alerts if any
                for alert in live_data["betting_alerts"][:2]:  # Top 2 alerts
                    self.logger.info(
                        f"🚨 {alert['alert_level']}: {alert['matchup']} - {alert['recommended_action']}"
                    )

            # Wait for next update (unless it's the last iteration)
            if datetime.now() + timedelta(seconds=update_interval) < end_time:
                time.sleep(update_interval)

        monitoring_results["end_time"] = datetime.now().isoformat()
        monitoring_results["total_updates"] = update_count

        self.logger.info(
            f"✅ Live monitoring complete: {update_count} updates, {
                monitoring_results['total_alerts_generated']} total alerts")

        return monitoring_results

    def generate_demo_live_data(self) -> dict:
        """Generate realistic demo live data for systems without premium API."""

        self.logger.info("🎮 Generating demo live sports data (no API key required)")

        # Simulate realistic live games
        demo_games = [
            {
                "event_id": "demo_nfl_001",
                "sport": "NFL",
                "sport_key": "american_football",
                "home_team": "Kansas City Chiefs",
                "away_team": "Buffalo Bills",
                "home_score": 21,
                "away_score": 24,
                "status": "Live",
                "progress": "4th Quarter - 8:23",
                "venue": "Arrowhead Stadium",
                "priority": "HIGH",
                "score_differential": 3,
                "live_betting_value": 12.5,
            },
            {
                "event_id": "demo_nba_001",
                "sport": "NBA",
                "sport_key": "basketball",
                "home_team": "Los Angeles Lakers",
                "away_team": "Boston Celtics",
                "home_score": 98,
                "away_score": 96,
                "status": "Live",
                "progress": "4th Quarter - 3:45",
                "venue": "Crypto.com Arena",
                "priority": "MEDIUM",
                "score_differential": 2,
                "live_betting_value": 15.0,
            },
            {
                "event_id": "demo_nhl_001",
                "sport": "NHL",
                "sport_key": "ice_hockey",
                "home_team": "Toronto Maple Leafs",
                "away_team": "Montreal Canadiens",
                "home_score": 2,
                "away_score": 2,
                "status": "Live",
                "progress": "Overtime - 2:15",
                "venue": "Scotiabank Arena",
                "priority": "HIGH",
                "score_differential": 0,
                "live_betting_value": 18.5,
            },
        ]

        # Generate alerts for demo games
        demo_alerts = self._generate_betting_alerts(demo_games)
        demo_weather_ops = self._identify_weather_opportunities(demo_games)

        demo_data = {
            "demo_mode": True,
            "timestamp": datetime.now().isoformat(),
            "total_live_games": len(demo_games),
            "priority_games": demo_games,
            "betting_alerts": demo_alerts,
            "weather_correlation_opportunities": demo_weather_ops,
            "upgrade_benefits": {
                "real_time_data": "Live scores updated every minute",
                "all_sports_coverage": "NFL, NBA, NHL, MLB, and more",
                "instant_alerts": "Immediate notifications for betting opportunities",
                "weather_integration": "Combine live scores with weather intelligence",
                "cost": "Only €9/month for premium features",
            },
        }

        return demo_data


def main():
    """Main execution function for real-time sports intelligence."""
    parser = argparse.ArgumentParser(
        description="EQ12 Real-Time Sports Intelligence System")
    parser.add_argument("--api-key", help="TheSportsDB Premium API key")
    parser.add_argument(
        "--live-scores",
        action="store_true",
        help="Get current live scores")
    parser.add_argument(
        "--monitor",
        type=int,
        help="Start live monitoring for X minutes")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demo mode (no API key required)")
    parser.add_argument(
        "--sport",
        help="Get live scores for specific sport (american_football, basketball, etc.)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize system
    intelligence = EQ12RealTimeSportsIntelligence(api_key=args.api_key)

    try:
        if args.demo:
            print("🎮 EQ12 REAL-TIME SPORTS INTELLIGENCE - DEMO MODE")
            print("=" * 60)

            demo_data = intelligence.generate_demo_live_data()

            print(
                f"📺 LIVE GAMES SIMULATION: {
                    demo_data['total_live_games']} active games")
            print()

            print("🏈 HIGH-VALUE LIVE GAMES:")
            for game in demo_data["priority_games"]:
                score = f"{game['home_score']} - {game['away_score']}"
                print(f"   {game['sport']}: {game['home_team']} vs {game['away_team']}")
                print(
                    f"      Score: {score} | {
                        game['progress']} | Value: {
                        game['live_betting_value']}")
            print()

            if demo_data["betting_alerts"]:
                print("🚨 LIVE BETTING ALERTS:")
                for alert in demo_data["betting_alerts"]:
                    print(f"   {alert['alert_level']}: {alert['matchup']}")
                    print(f"      Action: {alert['recommended_action']}")
                    print(f"      Reasons: {', '.join(alert['reasons'])}")
                print()

            print("💰 UPGRADE TO PREMIUM:")
            for benefit, description in demo_data["upgrade_benefits"].items():
                if benefit != "cost":
                    print(f"   ✅ {benefit.replace('_', ' ').title()}: {description}")
            print(f"   💳 {demo_data['upgrade_benefits']['cost']}")

        elif args.live_scores:
            print("📺 EQ12 LIVE SPORTS INTELLIGENCE")
            print("=" * 60)

            live_data = intelligence.get_live_scores_all_sports()

            if live_data.get("error"):
                print(f"❌ {live_data['error']}")
                if live_data.get("demo_mode"):
                    print("💡 Use --demo flag for demonstration without API key")
            else:
                print("📊 LIVE GAMES OVERVIEW:")
                print(f"   Total Sports: {live_data['total_sports']}")
                print(f"   Total Live Games: {live_data['total_live_games']}")
                print(f"   Priority Games: {len(live_data['priority_games'])}")
                print(f"   Betting Alerts: {len(live_data['betting_alerts'])}")
                print()

                if live_data["betting_alerts"]:
                    print("🚨 TOP BETTING OPPORTUNITIES:")
                    for alert in live_data["betting_alerts"][:3]:
                        print(
                            f"   {
                                alert['alert_level']}: {
                                alert['matchup']} ({
                                alert['sport']})")
                        print(
                            f"      {
                                alert['score']} | Value: {
                                alert['live_betting_value']}")
                        print(f"      Action: {alert['recommended_action']}")
                    print()

                if live_data["weather_correlation_opportunities"]:
                    print("🌤️  WEATHER INTEGRATION OPPORTUNITIES:")
                    for opp in live_data["weather_correlation_opportunities"][:2]:
                        print(f"   {opp['matchup']} at {opp['venue']}")
                        print(f"      Weather Factor: {opp['weather_factor']}")

        elif args.monitor:
            print(f"🔄 EQ12 LIVE MONITORING - {args.monitor} MINUTES")
            print("=" * 60)

            monitoring_results = intelligence.start_live_monitoring(
                duration_minutes=args.monitor)

            if monitoring_results.get("error"):
                print(f"❌ {monitoring_results['error']}")
                if monitoring_results.get("demo_available"):
                    print("💡 Use --demo flag for demonstration")
            else:
                print("✅ Monitoring complete!")
                print(f"   Updates: {monitoring_results['total_updates']}")
                print(
                    f"   Total Alerts: {
                        monitoring_results['total_alerts_generated']}")

                if monitoring_results["highest_value_opportunities"]:
                    best_opp = max(
                        monitoring_results["highest_value_opportunities"],
                        key=lambda x: x["live_betting_value"],
                    )
                    print(
                        f"   Best Opportunity: {
                            best_opp['matchup']} (Value: {
                            best_opp['live_betting_value']})")

        else:
            print("🚀 EQ12 REAL-TIME SPORTS INTELLIGENCE SYSTEM")
            print("=" * 60)
            print("Available commands:")
            print("  --live-scores    : Get current live scores and alerts")
            print("  --monitor X      : Start live monitoring for X minutes")
            print("  --demo          : Run demonstration mode (no API key)")
            print("  --api-key KEY   : Use premium API key for full features")
            print()
            print("Premium Features (€9/month):")
            print("  ✅ Real-time live scores across all sports")
            print("  ✅ Instant betting opportunity alerts")
            print("  ✅ Continuous monitoring capabilities")
            print("  ✅ Weather correlation analysis")

        # Save results if we have data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if args.live_scores and not args.demo:
            live_data = intelligence.get_live_scores_all_sports()
            if not live_data.get("error"):
                results_file = f"C:/EQ12/logs/live_sports_intelligence_{timestamp}.json"
                with open(results_file, "w") as f:
                    json.dump(live_data, f, indent=2, default=str)
                print(f"\n💾 Live data saved to: {results_file}")

        elif args.demo:
            demo_data = intelligence.generate_demo_live_data()
            results_file = f"C:/EQ12/logs/demo_sports_intelligence_{timestamp}.json"
            with open(results_file, "w") as f:
                json.dump(demo_data, f, indent=2, default=str)
            print(f"\n💾 Demo data saved to: {results_file}")

        print("\n🚀 EQ12 Real-Time Sports Intelligence Complete!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        logging.exception("Real-time intelligence error occurred")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
