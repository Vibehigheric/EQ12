#!/usr/bin/env python3
"""
EQ12 Fleet Stack + Bing Intelligence Integration
Monitors vehicle recalls, rental market trends, and fleet management opportunities.
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))

try:
    from bing_web_search import EQ12BingSearch, send_urgent_alert, setup_eq12_logging
except ImportError as e:
    print(f"❌ Error importing EQ12 Bing core: {e}")
    sys.exit(1)


class EQ12FleetIntelligence:
    """
    Fleet Intelligence Engine for EQ12
    Monitors vehicle recalls, Turo market, and fleet management opportunities
    """

    def __init__(self, verbose: bool = False):
        self.bing = EQ12BingSearch(verbose)
        self.logger = setup_eq12_logging(verbose)
        self.eq12_root = Path("C:/EQ12")

        # Vehicle makes to monitor for recalls
        self.vehicle_makes = [
            "Toyota",
            "Honda",
            "Ford",
            "Chevrolet",
            "Nissan",
            "Hyundai",
            "Kia",
            "Subaru",
            "Mazda",
            "Volkswagen",
            "BMW",
            "Mercedes",
            "Audi",
            "Lexus",
            "Acura",
            "Infiniti",
            "Cadillac",
            "Buick",
        ]

        # Fleet management keywords
        self.fleet_keywords = [
            "fleet management",
            "rental car",
            "car sharing",
            "Turo",
            "Getaround",
            "vehicle maintenance",
            "fleet insurance",
            "commercial vehicle",
            "car rental",
            "vehicle depreciation",
            "fleet tracking",
        ]

        # Safety/recall keywords for urgent monitoring
        self.safety_keywords = [
            "recall",
            "safety",
            "defect",
            "malfunction",
            "fire risk",
            "injury",
            "accident",
            "brake",
            "airbag",
            "engine",
            "transmission",
            "steering",
            "NHTSA",
            "investigation",
            "fix",
            "repair",
            "replacement",
            "software update",
        ]

        # Market opportunity keywords
        self.market_keywords = [
            "car shortage",
            "rental shortage",
            "high demand",
            "low supply",
            "price increase",
            "rate increase",
            "market opportunity",
            "expansion",
            "new market",
            "underserved",
            "competition",
            "profit margin",
        ]

    def monitor_vehicle_recalls(self, year_range: int = 5) -> list[dict[str, Any]]:
        """Monitor vehicle recalls that might affect fleet operations"""

        self.logger.info("🚗 Monitoring vehicle recalls and safety alerts...")

        # Focus on recent model years
        current_year = datetime.now().year
        list(range(current_year - year_range, current_year + 1))

        queries = []

        # General recall queries
        queries.extend(
            [
                "vehicle recall December 2025 NHTSA safety alert",
                f"car recall announcement latest {current_year}",
                "automotive safety recall December 2025 urgent",
                "NHTSA investigation vehicle defect December 2025",
            ]
        )

        # Brand-specific recalls (limited to avoid too many API calls)
        for make in self.vehicle_makes[:10]:
            queries.append(f"{make} recall {current_year} safety defect alert")

        results = self.bing.search_for_stack(queries, "fleet_recalls", "news")

        # Filter for genuine recall alerts
        recall_alerts = self._filter_recall_alerts(results)

        # Send urgent alerts for safety-critical recalls
        if recall_alerts:
            self._send_fleet_alerts(recall_alerts, "vehicle_recalls")

        return recall_alerts

    def _filter_recall_alerts(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter results for genuine vehicle recall alerts"""
        recall_results = []

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            # Must be vehicle-related
            vehicle_indicators = [
                "vehicle",
                "car",
                "truck",
                "SUV",
                "sedan",
                "auto",
                "recall",
            ]
            if not any(indicator in text for indicator in vehicle_indicators):
                continue

            # Calculate safety score
            safety_score = 0
            matched_keywords = []

            # Check for safety keywords
            for keyword in self.safety_keywords:
                if keyword in text:
                    # Higher weight for critical safety terms
                    weight = 3 if keyword in ["fire risk", "injury", "brake", "airbag"] else 1
                    safety_score += weight
                    matched_keywords.append(keyword)

            # Check for official sources
            official_sources = [
                "NHTSA",
                "EPA",
                "manufacturer",
                "official",
                "company",
                "automaker",
            ]
            for source in official_sources:
                if source in text:
                    safety_score += 2
                    matched_keywords.append(f"official:{source}")

            # Check for urgency indicators
            urgency_terms = [
                "urgent",
                "immediate",
                "stop driving",
                "fire risk",
                "death",
                "injury",
            ]
            for term in urgency_terms:
                if term in text:
                    safety_score += 4
                    matched_keywords.append(f"urgent:{term}")

            # Look for affected vehicle counts
            if re.search(r"\\d+,\\d+|\\d+ million|\\d+ thousand", text):
                safety_score += 2
                matched_keywords.append("large_scale")

            if safety_score >= 3:
                result["safety_score"] = safety_score
                result["matched_keywords"] = matched_keywords
                result["intel_type"] = "recall_alert"
                recall_results.append(result)

                self.logger.warning(
                    f"🚨 RECALL ALERT: {result['title'][:60]}... (Score: {safety_score})"
                )

        return recall_results

    def monitor_rental_market(self) -> list[dict[str, Any]]:
        """Monitor car rental and sharing market trends"""

        self.logger.info("🚙 Monitoring rental and car sharing market...")

        queries = [
            "Turo car sharing Buffalo NY December 2025 rates",
            "car rental shortage Buffalo airport December 2025",
            "rental car prices Buffalo NY December 2025",
            "Getaround car sharing Western New York expansion",
            "Buffalo car rental demand December 2025 supply",
            "peer to peer car sharing Buffalo market opportunity",
            "car rental business Buffalo NY December 2025",
        ]

        results = self.bing.search_for_stack(queries, "fleet_rental_market", "web")

        # Filter for market opportunities
        market_intel = []

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            market_score = 0
            matched_keywords = []

            # Market opportunity indicators
            for keyword in self.market_keywords:
                if keyword in text:
                    market_score += 2
                    matched_keywords.append(keyword)

            # Pricing indicators
            price_patterns = [
                r"\\$\\d+/day",
                r"\\$\\d+/hour",
                r"\\d+% increase",
                r"rates up",
            ]
            for pattern in price_patterns:
                if re.search(pattern, text):
                    market_score += 2
                    matched_keywords.append("pricing_data")

            # Platform mentions
            platforms = ["Turo", "Getaround", "Zipcar", "rental", "sharing"]
            for platform in platforms:
                if platform in text:
                    market_score += 1
                    matched_keywords.append(f"platform:{platform}")

            if market_score >= 3:
                result["market_score"] = market_score
                result["matched_keywords"] = matched_keywords
                result["intel_type"] = "market_opportunity"
                market_intel.append(result)

        return market_intel

    def track_fuel_prices(self) -> list[dict[str, Any]]:
        """Track fuel price trends affecting fleet costs"""

        self.logger.info("⛽ Tracking fuel price trends...")

        queries = [
            "gas prices Buffalo NY December 2025 forecast",
            "fuel prices Western New York December 2025",
            "gasoline cost Buffalo area stations cheapest",
            "diesel fuel prices Buffalo NY December 2025",
            "gas price trends Buffalo forecast December",
            "fuel cost calculator Buffalo NY December 2025",
        ]

        results = self.bing.search_for_stack(queries, "fleet_fuel_prices", "web")

        # Filter for fuel price data
        fuel_intel = []

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            # Look for fuel price indicators
            fuel_terms = ["gas", "gasoline", "fuel", "diesel", "price", "cost"]
            price_patterns = [r"\\$\\d+\\.\\d+", r"\\d+¢", r"\\d+ cents"]

            if any(term in text for term in fuel_terms) and any(
                re.search(pattern, text) for pattern in price_patterns
            ):
                result["intel_type"] = "fuel_pricing"
                fuel_intel.append(result)

        return fuel_intel

    def monitor_vehicle_maintenance(self) -> list[dict[str, Any]]:
        """Monitor vehicle maintenance trends and costs"""

        queries = [
            "vehicle maintenance costs 2025 trends increase",
            "auto repair prices Buffalo NY December 2025",
            "car maintenance schedule 2025 vehicles recommendations",
            "fleet maintenance software December 2025 solutions",
            "automotive service costs Buffalo area December",
            "vehicle inspection New York requirements 2025",
        ]

        results = self.bing.search_for_stack(queries, "fleet_maintenance", "web")

        # Filter for maintenance intelligence
        maintenance_intel = []

        maintenance_terms = [
            "maintenance",
            "service",
            "repair",
            "inspection",
            "oil change",
            "tire",
            "brake",
            "tune-up",
            "diagnostic",
            "parts",
            "labor",
        ]

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            if any(term in text for term in maintenance_terms):
                result["intel_type"] = "maintenance"
                maintenance_intel.append(result)

        return maintenance_intel

    def _send_fleet_alerts(self, results: list[dict[str, Any]], alert_type: str):
        """Send fleet intelligence alerts via Telegram"""

        if not results:
            return

        # Sort by safety/market score
        score_key = "safety_score" if alert_type == "vehicle_recalls" else "market_score"
        top_results = sorted(results, key=lambda x: x.get(score_key, 0), reverse=True)[:3]

        alert_count = 0
        for result in top_results:
            if result.get(score_key, 0) >= 5:  # High-priority alerts only
                alert_msg = self._format_fleet_alert(result, alert_type)
                send_urgent_alert(alert_msg)
                alert_count += 1

        self.logger.info(f"📱 Sent {alert_count} fleet intelligence alerts")

    def _format_fleet_alert(self, result: dict[str, Any], alert_type: str) -> str:
        """Format fleet intelligence alert for Telegram"""

        emoji_map = {
            "vehicle_recalls": "🚨",
            "market_opportunity": "🚙",
            "fuel_pricing": "⛽",
            "maintenance": "🔧",
        }

        emoji = emoji_map.get(alert_type, "🚗")
        keywords_str = ", ".join(result.get("matched_keywords", [])[:5])

        score_key = next((k for k in result if k.endswith("_score")), "score")
        score = result.get(score_key, 0)

        message = f"""{emoji} **FLEET INTEL ALERT**

**{result["title"]}**

{result["snippet"][:200]}...

**Intel Score:** {score}/10
**Keywords:** {keywords_str}
**Source:** {result["url"]}

🚗 *Monitor for fleet impact and opportunities*"""

        return message

    def generate_fleet_report(self) -> dict[str, Any]:
        """Generate comprehensive fleet intelligence report"""

        self.logger.info("📋 Generating fleet intelligence report...")

        # Gather all intelligence types
        recall_intel = self.monitor_vehicle_recalls()
        market_intel = self.monitor_rental_market()
        fuel_intel = self.track_fuel_prices()
        maintenance_intel = self.monitor_vehicle_maintenance()

        # Generate summary
        report = {
            "generated_at": datetime.now().isoformat(),
            "intelligence_summary": {
                "recall_alerts": len(recall_intel),
                "critical_recalls": len([r for r in recall_intel if r.get("safety_score", 0) >= 6]),
                "market_opportunities": len(market_intel),
                "high_value_market": len(
                    [m for m in market_intel if m.get("market_score", 0) >= 5]
                ),
                "fuel_insights": len(fuel_intel),
                "maintenance_insights": len(maintenance_intel),
            },
            "recall_intelligence": recall_intel,
            "market_intelligence": market_intel,
            "fuel_intelligence": fuel_intel,
            "maintenance_intelligence": maintenance_intel,
            "recommendations": self._generate_fleet_recommendations(
                recall_intel, market_intel, fuel_intel, maintenance_intel
            ),
        }

        # Save report
        report_file = (
            self.eq12_root
            / "logs"
            / f"fleet_intelligence_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"✅ Fleet report saved: {report_file}")
        return report

    def _generate_fleet_recommendations(
        self,
        recall_intel: list[dict],
        market_intel: list[dict],
        fuel_intel: list[dict],
        maintenance_intel: list[dict],
    ) -> list[str]:
        """Generate actionable fleet intelligence recommendations"""

        recommendations = []

        # Recall recommendations
        critical_recalls = [r for r in recall_intel if r.get("safety_score", 0) >= 6]
        if critical_recalls:
            recommendations.append(
                f"🚨 {len(critical_recalls)} critical vehicle recalls - immediate fleet review needed"
            )

        # Market opportunity recommendations
        high_market = [m for m in market_intel if m.get("market_score", 0) >= 5]
        if high_market:
            recommendations.append(
                f"🚙 {len(high_market)} high-value rental market opportunities in Buffalo"
            )

        # Fuel cost recommendations
        if fuel_intel:
            recommendations.append(
                f"⛽ {len(fuel_intel)} fuel pricing insights - monitor for route optimization"
            )

        # Maintenance recommendations
        if maintenance_intel:
            recommendations.append(
                f"🔧 {len(maintenance_intel)} maintenance trends - budget planning opportunities"
            )

        # Seasonal recommendations
        month = datetime.now().month
        if month in [11, 12, 1, 2]:
            recommendations.append(
                "❄️ Winter season - monitor for weather-related vehicle demand spikes"
            )

        # Platform-specific recommendations
        if any("Turo" in str(result) for result in market_intel):
            recommendations.append(
                "🎯 Turo opportunities detected - consider peer-to-peer expansion"
            )

        # General recommendations
        if recall_intel or market_intel:
            recommendations.append(
                "📊 Cross-reference fleet composition with recall and market data"
            )
            recommendations.append("💰 Update insurance and liability coverage based on recalls")

        return recommendations


def main():
    """Main EQ12 fleet intelligence runner"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Fleet Intelligence")
    parser.add_argument(
        "--mode",
        choices=["recalls", "market", "fuel", "maintenance", "report"],
        default="recalls",
        help="Intelligence gathering mode",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    try:
        intel = EQ12FleetIntelligence(verbose=args.verbose)

        if args.mode == "recalls":
            results = intel.monitor_vehicle_recalls()
            print(f"✅ Recall intelligence: {len(results)} alerts monitored")

        elif args.mode == "market":
            results = intel.monitor_rental_market()
            print(f"✅ Market intelligence: {len(results)} opportunities found")

        elif args.mode == "fuel":
            results = intel.track_fuel_prices()
            print(f"✅ Fuel intelligence: {len(results)} pricing insights")

        elif args.mode == "maintenance":
            results = intel.monitor_vehicle_maintenance()
            print(f"✅ Maintenance intelligence: {len(results)} insights gathered")

        elif args.mode == "report":
            report = intel.generate_fleet_report()
            print("✅ Fleet intelligence report generated")
            print(f"📊 Summary: {report['intelligence_summary']}")
            for rec in report["recommendations"]:
                print(f"   💡 {rec}")

        print("\\n🎯 Integration: Check C:\\EQ12\\logs for detailed results")
        print("🚗 Fleet Intel: Monitor for safety and market opportunities")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
