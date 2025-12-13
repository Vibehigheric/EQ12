#!/usr/bin/env python3
"""
EQ12 Betting Stack + Bing Intelligence Integration
Enhances existing EdgeGod parlay system with real-time injury and news intelligence.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add core directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))

try:
    from bing_web_search import EQ12BingSearch, send_urgent_alert, setup_eq12_logging
except ImportError as e:
    print(f"❌ Error importing EQ12 Bing core: {e}")
    print("Make sure you've run Setup-BingIntegration.ps1 first")
    sys.exit(1)


class EQ12BettingIntelligence:
    """
    Betting Intelligence Engine for EQ12
    Integrates with existing EdgeGod parlays and Odds API systems
    """

    def __init__(self, verbose: bool = False):
        self.bing = EQ12BingSearch(verbose)
        self.logger = setup_eq12_logging(verbose)
        self.eq12_root = Path("C:/EQ12")

        # Integration with existing EQ12 systems
        self.edgegod_dir = self.eq12_root / "EdgeGodParlays"
        self.odds_api_exists = (self.eq12_root / "scripts" / "odds_parser.py").exists()

        # Urgent alert keywords that trigger immediate Telegram alerts
        self.urgent_keywords = [
            # Injury keywords
            "injury",
            "injured",
            "hurt",
            "ruled out",
            "questionable",
            "doubtful",
            "scratched",
            "benched",
            "sidelined",
            "IR",
            "IL",
            # Lineup changes
            "starting lineup",
            "lineup change",
            "rotation change",
            "demoted",
            "promoted",
            "called up",
            "sent down",
            "activated",
            "deactivated",
            # Suspensions/discipline
            "suspended",
            "suspension",
            "arrested",
            "violation",
            "banned",
            # Performance impact
            "struggling",
            "slump",
            "hot streak",
            "career high",
            "record",
        ]

    def check_injury_news(self, sport: str = "mlb") -> list[dict[str, Any]]:
        """Check for breaking injury news that might affect betting odds"""

        self.logger.info(f"🩹 Checking {sport.upper()} injury intel...")

        # Sport-specific queries for injury intelligence
        sport_queries = {
            "mlb": [
                f"MLB injury report today {datetime.now().strftime('%B %Y')}",
                "baseball player injured today breaking news",
                "MLB starting pitcher injury latest update",
                "baseball lineup changes today injury report",
            ],
            "nfl": [
                f"NFL injury report today {datetime.now().strftime('%B %Y')}",
                "football player injured today breaking news",
                "NFL starting lineup injury updates",
                "quarterback injury report today NFL",
            ],
            "nba": [
                f"NBA injury report today {datetime.now().strftime('%B %Y')}",
                "basketball player injured today breaking news",
                "NBA starting lineup injury updates",
                "NBA star player injury latest news",
            ],
            "nhl": [
                f"NHL injury report today {datetime.now().strftime('%B %Y')}",
                "hockey player injured today breaking news",
                "NHL goalie injury latest updates",
                "hockey lineup changes injury report",
            ],
        }

        queries = sport_queries.get(sport, sport_queries["mlb"])

        # Search for injury news
        results = self.bing.search_for_stack(queries, f"betting_{sport}_injury", "news")

        # Filter and analyze results
        urgent_results = self._analyze_urgency(results)

        # Cross-reference with existing EdgeGod/Odds API data if available
        enhanced_results = self._cross_reference_odds(urgent_results, sport)

        # Send alerts for urgent findings
        if urgent_results:
            self._send_injury_alerts(urgent_results, sport)

        return enhanced_results

    def _analyze_urgency(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Analyze search results to identify urgent betting-relevant information"""
        urgent_results = []

        for result in results:
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()
            combined_text = f"{title} {snippet}"

            # Check for urgent keywords
            urgency_score = 0
            matched_keywords = []

            for keyword in self.urgent_keywords:
                if keyword in combined_text:
                    urgency_score += 1
                    matched_keywords.append(keyword)

            # Additional urgency factors
            time_factors = ["today", "breaking", "just in", "latest", "now", "urgent"]
            for factor in time_factors:
                if factor in combined_text:
                    urgency_score += 2
                    matched_keywords.append(f"time:{factor}")

            # Impact factors
            impact_factors = [
                "star",
                "MVP",
                "All-Star",
                "starting",
                "key player",
                "captain",
            ]
            for factor in impact_factors:
                if factor in combined_text:
                    urgency_score += 1
                    matched_keywords.append(f"impact:{factor}")

            # Mark as urgent if score meets threshold
            if urgency_score >= 2:
                result["urgency_score"] = urgency_score
                result["matched_keywords"] = matched_keywords
                result["betting_relevance"] = "HIGH"
                urgent_results.append(result)

                self.logger.warning(
                    f"🚨 URGENT BETTING INTEL: {result['title'][:60]}... (Score: {urgency_score})"
                )

        return urgent_results

    def _cross_reference_odds(
        self, results: list[dict[str, Any]], sport: str
    ) -> list[dict[str, Any]]:
        """Cross-reference news with existing Odds API data if available"""

        if not self.odds_api_exists:
            self.logger.debug("Odds API integration not available")
            return results

        try:
            # Try to import and use existing odds parser
            odds_file = self.eq12_root / "logs" / f"odds_{sport}.json"

            if odds_file.exists():
                with open(odds_file) as f:
                    odds_data = json.load(f)

                self.logger.info(f"📊 Cross-referencing with {len(odds_data)} odds entries")

                # Add odds context to results
                for result in results:
                    result["odds_context"] = "Available"
                    result["odds_timestamp"] = odds_data.get("timestamp", "Unknown")

            else:
                self.logger.debug(f"No recent odds data found for {sport}")

        except Exception as e:
            self.logger.error(f"Failed to cross-reference odds: {e}")

        return results

    def _send_injury_alerts(self, urgent_results: list[dict[str, Any]], sport: str):
        """Send urgent injury alerts via EQ12 Telegram integration"""

        if not urgent_results:
            return

        # Group alerts by urgency score
        high_urgency = [r for r in urgent_results if r.get("urgency_score", 0) >= 4]
        medium_urgency = [r for r in urgent_results if r.get("urgency_score", 0) == 3]

        # Send high urgency alerts immediately
        for result in high_urgency:
            alert_msg = self._format_telegram_alert(result, sport, "🚨 CRITICAL")
            send_urgent_alert(alert_msg)

        # Batch medium urgency alerts
        if medium_urgency:
            batch_msg = f"⚠️ **{sport.upper()} BETTING INTEL SUMMARY**\\n\\n"
            for result in medium_urgency[:3]:  # Limit to 3 to avoid message length
                batch_msg += f"• {result['title']}\\n  {result['url']}\\n\\n"

            send_urgent_alert(batch_msg)

        self.logger.info(
            f"📱 Sent {len(high_urgency)} critical + {len(medium_urgency)} medium alerts"
        )

    def _format_telegram_alert(self, result: dict[str, Any], sport: str, priority: str) -> str:
        """Format betting intelligence alert for Telegram"""

        keywords_str = ", ".join(result.get("matched_keywords", [])[:5])

        message = f"""{priority} **{sport.upper()} BETTING ALERT**

**{result["title"]}**

{result["snippet"][:200]}...

**Keywords:** {keywords_str}
**Urgency:** {result.get("urgency_score", 0)}/10
**Source:** {result["url"]}

🎯 *Check EdgeGod parlays for line movement impact*"""

        return message

    def monitor_line_movement_news(self, sport: str = "mlb") -> list[dict[str, Any]]:
        """Monitor news that might cause line movements"""

        queries = [
            f"{sport} line movement betting odds change today",
            f"{sport} betting odds shift injury news",
            f"sportsbook {sport} odds adjustment latest",
            f"{sport} sharp money public betting trends",
        ]

        results = self.bing.search_for_stack(queries, f"betting_{sport}_lines", "news")

        # Look for line movement indicators
        movement_results = []
        movement_keywords = [
            "line moved",
            "odds shifted",
            "sharp money",
            "big bet",
            "line adjustment",
        ]

        for result in results:
            text = f"{result['title']} {result['snippet']}".lower()
            if any(keyword in text for keyword in movement_keywords):
                result["movement_type"] = "line_shift"
                movement_results.append(result)

        if movement_results:
            self.logger.info(f"📈 Found {len(movement_results)} line movement indicators")

        return movement_results

    def get_matchup_intelligence(
        self, team1: str, team2: str, sport: str = "mlb"
    ) -> list[dict[str, Any]]:
        """Get intelligence for specific matchup"""

        queries = [
            f"{team1} vs {team2} {sport} injury report today",
            f"{team1} {team2} {sport} betting preview analysis",
            f"{team1} {team2} head to head {sport} recent news",
            f"{team1} {team2} {sport} weather conditions forecast",
        ]

        results = self.bing.search_for_stack(queries, f"betting_matchup_{team1}_{team2}", "web")

        self.logger.info(f"🥊 {team1} vs {team2} intelligence: {len(results)} insights found")
        return results

    def generate_betting_report(self, sport: str = "mlb") -> dict[str, Any]:
        """Generate comprehensive betting intelligence report"""

        self.logger.info(f"📋 Generating comprehensive {sport.upper()} betting report...")

        # Gather all intelligence types
        injury_intel = self.check_injury_news(sport)
        movement_intel = self.monitor_line_movement_news(sport)

        # Generate summary
        report = {
            "sport": sport,
            "generated_at": datetime.now().isoformat(),
            "intelligence_summary": {
                "total_injury_alerts": len(injury_intel),
                "urgent_alerts": len([r for r in injury_intel if r.get("urgency_score", 0) >= 4]),
                "line_movement_alerts": len(movement_intel),
            },
            "injury_intelligence": injury_intel,
            "line_movement_intelligence": movement_intel,
            "recommendations": self._generate_recommendations(injury_intel, movement_intel),
        }

        # Save report
        report_file = (
            self.eq12_root
            / "logs"
            / f"betting_intelligence_{sport}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"✅ Betting report saved: {report_file}")
        return report

    def _generate_recommendations(
        self, injury_intel: list[dict], movement_intel: list[dict]
    ) -> list[str]:
        """Generate actionable betting recommendations"""

        recommendations = []

        # Injury-based recommendations
        high_urgency = [r for r in injury_intel if r.get("urgency_score", 0) >= 4]
        if high_urgency:
            recommendations.append(
                f"🚨 {len(high_urgency)} critical injury alerts - check line movement immediately"
            )

        # Line movement recommendations
        if movement_intel:
            recommendations.append(
                f"📈 {len(movement_intel)} line movements detected - investigate sharp money"
            )

        # General recommendations
        if injury_intel or movement_intel:
            recommendations.append("🔄 Update EdgeGod parlay models with latest intelligence")
            recommendations.append("📊 Cross-reference findings with current Odds API data")

        if not injury_intel and not movement_intel:
            recommendations.append("✅ No urgent alerts - market appears stable")

        return recommendations


def main():
    """Main EQ12 betting intelligence runner"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Betting Intelligence")
    parser.add_argument(
        "--sport",
        choices=["mlb", "nfl", "nba", "nhl"],
        default="mlb",
        help="Sport to monitor",
    )
    parser.add_argument(
        "--mode",
        choices=["injury", "lines", "matchup", "report"],
        default="injury",
        help="Intelligence gathering mode",
    )
    parser.add_argument("--team1", help="First team for matchup analysis")
    parser.add_argument("--team2", help="Second team for matchup analysis")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    try:
        intel = EQ12BettingIntelligence(verbose=args.verbose)

        if args.mode == "injury":
            results = intel.check_injury_news(args.sport)
            print(f"✅ Injury intelligence: {len(results)} alerts processed")

        elif args.mode == "lines":
            results = intel.monitor_line_movement_news(args.sport)
            print(f"✅ Line movement intelligence: {len(results)} indicators found")

        elif args.mode == "matchup":
            if not args.team1 or not args.team2:
                print("❌ Matchup mode requires --team1 and --team2")
                return
            results = intel.get_matchup_intelligence(args.team1, args.team2, args.sport)
            print(
                f"✅ Matchup intelligence: {len(results)} insights for {args.team1} vs {args.team2}"
            )

        elif args.mode == "report":
            report = intel.generate_betting_report(args.sport)
            print("✅ Complete betting report generated")
            print(f"📊 Summary: {report['intelligence_summary']}")
            for rec in report["recommendations"]:
                print(f"   💡 {rec}")

        print("\\n🎯 Integration: Check C:\\EQ12\\logs for detailed results")
        print("🤖 EdgeGod: Intelligence integrated with existing parlay systems")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
