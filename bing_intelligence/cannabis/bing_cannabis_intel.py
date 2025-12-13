#!/usr/bin/env python3
"""
EQ12 Cannabis Stack + Bing Intelligence Integration
Monitors cannabis industry news, dispensary tracking, and regulatory updates.
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


class EQ12CannabisIntelligence:
    """
    Cannabis Industry Intelligence Engine for EQ12
    Monitors dispensaries, regulations, and cannabis tourism opportunities
    """

    def __init__(self, verbose: bool = False):
        self.bing = EQ12BingSearch(verbose)
        self.logger = setup_eq12_logging(verbose)
        self.eq12_root = Path("C:/EQ12")

        # New York cannabis regions to monitor
        self.ny_regions = [
            "Buffalo",
            "Rochester",
            "Syracuse",
            "Albany",
            "NYC",
            "Long Island",
            "Westchester",
            "Hudson Valley",
            "Capital Region",
            "Western NY",
        ]

        # License types to track
        self.license_types = [
            "dispensary",
            "retail",
            "adult-use",
            "medical",
            "delivery",
            "cultivation",
            "processor",
            "distributor",
            "testing lab",
        ]

        # Regulatory keywords for urgent monitoring
        self.regulatory_keywords = [
            "license",
            "application",
            "approval",
            "permit",
            "regulation",
            "compliance",
            "violation",
            "fine",
            "penalty",
            "suspension",
            "revocation",
            "law change",
            "tax",
            "fee",
            "ordinance",
        ]

        # Tourism and business opportunity keywords
        self.opportunity_keywords = [
            "tourism",
            "tour",
            "experience",
            "package",
            "visit",
            "attraction",
            "investment",
            "business opportunity",
            "partnership",
            "franchise",
            "real estate",
            "commercial space",
            "zoning",
            "development",
        ]

    def track_dispensary_licenses(self, region: str = "Buffalo") -> list[dict[str, Any]]:
        """Track new dispensary licenses and openings in specific region"""

        self.logger.info(f"🏪 Tracking dispensary licenses in {region}...")

        queries = [
            f"{region} dispensary license application approved 2025",
            f"{region} cannabis retail license issued new",
            f"New York cannabis {region} dispensary opening soon",
            f"{region} marijuana dispensary grand opening December",
            f"cannabis license {region} NY OCM approval latest",
            f"{region} dispensary location address new store",
        ]

        results = self.bing.search_for_stack(queries, f"cannabis_licenses_{region.lower()}", "news")

        # Filter for actual license/opening news
        license_results = self._filter_license_news(results)

        # Send alerts for new openings
        if license_results:
            self._send_cannabis_alerts(license_results, "dispensary_licenses", region)

        return license_results

    def _filter_license_news(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter results for genuine license/opening news"""
        license_results = []

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            # Must be cannabis-related
            cannabis_indicators = [
                "cannabis",
                "marijuana",
                "dispensary",
                "weed",
                "THC",
                "CBD",
            ]
            if not any(indicator in text for indicator in cannabis_indicators):
                continue

            # Calculate relevance score
            relevance_score = 0
            matched_keywords = []

            # Check for license/opening keywords
            license_indicators = [
                "license",
                "permit",
                "approval",
                "opening",
                "approved",
                "issued",
                "granted",
            ]
            for indicator in license_indicators:
                if indicator in text:
                    relevance_score += 2
                    matched_keywords.append(indicator)

            # Check for business activity
            business_indicators = [
                "store",
                "location",
                "address",
                "grand opening",
                "now open",
                "coming soon",
            ]
            for indicator in business_indicators:
                if indicator in text:
                    relevance_score += 1
                    matched_keywords.append(f"business:{indicator}")

            # Check for official sources
            official_indicators = [
                "OCM",
                "department",
                "state",
                "official",
                "government",
                "commission",
            ]
            for indicator in official_indicators:
                if indicator in text:
                    relevance_score += 2
                    matched_keywords.append(f"official:{indicator}")

            if relevance_score >= 3:
                result["relevance_score"] = relevance_score
                result["matched_keywords"] = matched_keywords
                result["intel_type"] = "license_news"
                license_results.append(result)

                self.logger.info(
                    f"📋 LICENSE INTEL: {result['title'][:60]}... (Score: {relevance_score})"
                )

        return license_results

    def monitor_regulatory_updates(self) -> list[dict[str, Any]]:
        """Monitor New York cannabis regulatory changes"""

        self.logger.info("⚖️ Monitoring NY cannabis regulatory updates...")

        queries = [
            "New York cannabis regulation change December 2025",
            "NYS OCM cannabis rule update latest news",
            "New York marijuana law change tax update",
            "cannabis compliance New York December 2025",
            "NY cannabis license fee change regulation",
            "New York cannabis social equity program update",
            "OCM cannabis regulation enforcement December",
        ]

        results = self.bing.search_for_stack(queries, "cannabis_regulatory", "news")

        # Filter for regulatory updates
        regulatory_results = []

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            # Check for regulatory keywords
            regulatory_score = 0
            matched_keywords = []

            for keyword in self.regulatory_keywords:
                if keyword in text:
                    regulatory_score += 1
                    matched_keywords.append(keyword)

            # High priority regulatory terms
            high_priority = [
                "emergency",
                "immediate",
                "effective",
                "violation",
                "fine",
                "penalty",
            ]
            for term in high_priority:
                if term in text:
                    regulatory_score += 3
                    matched_keywords.append(f"urgent:{term}")

            if regulatory_score >= 2:
                result["regulatory_score"] = regulatory_score
                result["matched_keywords"] = matched_keywords
                result["intel_type"] = "regulatory"
                regulatory_results.append(result)

        # Send urgent alerts for high-impact regulatory changes
        urgent_regulatory = [r for r in regulatory_results if r.get("regulatory_score", 0) >= 4]
        if urgent_regulatory:
            self._send_cannabis_alerts(urgent_regulatory, "regulatory_urgent")

        return regulatory_results

    def scout_tourism_opportunities(self) -> list[dict[str, Any]]:
        """Scout cannabis tourism opportunities in NY"""

        self.logger.info("🎪 Scouting cannabis tourism opportunities...")

        queries = [
            "cannabis tourism New York Niagara Falls packages",
            "marijuana tour Buffalo NY dispensary experience",
            "cannabis friendly hotels New York state",
            "weed tourism package New York destinations",
            "cannabis events New York December 2025 calendar",
            "marijuana festival New York winter activities",
            "cannabis education tour New York dispensaries",
        ]

        results = self.bing.search_for_stack(queries, "cannabis_tourism", "web")

        # Filter for tourism opportunities
        tourism_results = []

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            tourism_score = 0
            matched_keywords = []

            # Tourism indicators
            for keyword in self.opportunity_keywords:
                if keyword in text:
                    tourism_score += 1
                    matched_keywords.append(keyword)

            # Business opportunity indicators
            business_terms = [
                "revenue",
                "profit",
                "market",
                "demand",
                "growth",
                "opportunity",
            ]
            for term in business_terms:
                if term in text:
                    tourism_score += 2
                    matched_keywords.append(f"business:{term}")

            if tourism_score >= 2:
                result["tourism_score"] = tourism_score
                result["matched_keywords"] = matched_keywords
                result["intel_type"] = "tourism"
                tourism_results.append(result)

        return tourism_results

    def track_market_prices(self) -> list[dict[str, Any]]:
        """Track cannabis market prices and trends"""

        queries = [
            "New York cannabis prices dispensary December 2025",
            "marijuana cost NY dispensary menu pricing",
            "cannabis tax New York consumer prices impact",
            "NY dispensary price comparison December 2025",
            "wholesale cannabis prices New York market",
            "cannabis product pricing trends New York",
        ]

        results = self.bing.search_for_stack(queries, "cannabis_pricing", "web")

        # Filter for price/market information
        price_results = []

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            # Look for price indicators
            price_patterns = [
                r"\\$\\d+",
                r"\\d+/gram",
                r"\\d+/ounce",
                r"price",
                r"cost",
                r"\\d+% tax",
            ]

            if any(re.search(pattern, text) for pattern in price_patterns):
                result["intel_type"] = "pricing"
                price_results.append(result)

        return price_results

    def _send_cannabis_alerts(
        self, results: list[dict[str, Any]], alert_type: str, region: str = "NY"
    ):
        """Send cannabis intelligence alerts via Telegram"""

        if not results:
            return

        # Sort by relevance/score
        if alert_type == "dispensary_licenses":
            top_results = sorted(results, key=lambda x: x.get("relevance_score", 0), reverse=True)[
                :3
            ]
        elif alert_type == "regulatory_urgent":
            top_results = sorted(results, key=lambda x: x.get("regulatory_score", 0), reverse=True)[
                :2
            ]
        else:
            top_results = results[:2]

        for result in top_results:
            if result.get("relevance_score", 0) >= 4 or result.get("regulatory_score", 0) >= 4:
                alert_msg = self._format_cannabis_alert(result, alert_type, region)
                send_urgent_alert(alert_msg)

        alert_count = len(
            [
                r
                for r in top_results
                if r.get("relevance_score", 0) >= 4 or r.get("regulatory_score", 0) >= 4
            ]
        )
        self.logger.info(f"📱 Sent {alert_count} cannabis intelligence alerts")

    def _format_cannabis_alert(
        self, result: dict[str, Any], alert_type: str, region: str = "NY"
    ) -> str:
        """Format cannabis intelligence alert for Telegram"""

        emoji_map = {
            "dispensary_licenses": "🏪",
            "regulatory_urgent": "⚖️",
            "tourism": "🎪",
            "pricing": "💰",
        }

        emoji = emoji_map.get(alert_type, "🌿")
        keywords_str = ", ".join(result.get("matched_keywords", [])[:5])
        score = (
            result.get("relevance_score")
            or result.get("regulatory_score")
            or result.get("tourism_score", 0)
        )

        message = f"""{emoji} **CANNABIS INTEL ALERT - {region.upper()}**

**{result["title"]}**

{result["snippet"][:200]}...

**Intel Score:** {score}/10
**Keywords:** {keywords_str}
**Source:** {result["url"]}

🌿 *Monitor for business opportunities*"""

        return message

    def generate_cannabis_report(self, region: str = "Buffalo") -> dict[str, Any]:
        """Generate comprehensive cannabis intelligence report"""

        self.logger.info(f"📋 Generating cannabis intelligence report for {region}...")

        # Gather all intelligence types
        license_intel = self.track_dispensary_licenses(region)
        regulatory_intel = self.monitor_regulatory_updates()
        tourism_intel = self.scout_tourism_opportunities()
        pricing_intel = self.track_market_prices()

        # Generate summary
        report = {
            "region": region,
            "generated_at": datetime.now().isoformat(),
            "intelligence_summary": {
                "new_licenses": len(license_intel),
                "high_relevance_licenses": len(
                    [l for l in license_intel if l.get("relevance_score", 0) >= 5]
                ),
                "regulatory_updates": len(regulatory_intel),
                "urgent_regulatory": len(
                    [r for r in regulatory_intel if r.get("regulatory_score", 0) >= 4]
                ),
                "tourism_opportunities": len(tourism_intel),
                "pricing_intel": len(pricing_intel),
            },
            "license_intelligence": license_intel,
            "regulatory_intelligence": regulatory_intel,
            "tourism_intelligence": tourism_intel,
            "pricing_intelligence": pricing_intel,
            "recommendations": self._generate_cannabis_recommendations(
                license_intel, regulatory_intel, tourism_intel, pricing_intel, region
            ),
        }

        # Save report
        report_file = (
            self.eq12_root
            / "logs"
            / f"cannabis_intelligence_{region.lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"✅ Cannabis report saved: {report_file}")
        return report

    def _generate_cannabis_recommendations(
        self,
        license_intel: list[dict],
        regulatory_intel: list[dict],
        tourism_intel: list[dict],
        pricing_intel: list[dict],
        region: str,
    ) -> list[str]:
        """Generate actionable cannabis intelligence recommendations"""

        recommendations = []

        # License-based recommendations
        high_relevance = [l for l in license_intel if l.get("relevance_score", 0) >= 5]
        if high_relevance:
            recommendations.append(
                f"🏪 {len(high_relevance)} high-priority license updates in {region}"
            )

        # Regulatory recommendations
        urgent_regulatory = [r for r in regulatory_intel if r.get("regulatory_score", 0) >= 4]
        if urgent_regulatory:
            recommendations.append(
                f"⚖️ {len(urgent_regulatory)} urgent regulatory changes - compliance review needed"
            )

        # Tourism opportunities
        if tourism_intel:
            recommendations.append(
                f"🎪 {len(tourism_intel)} tourism opportunities - content creation potential"
            )

        # Market intelligence
        if pricing_intel:
            recommendations.append(
                f"💰 {len(pricing_intel)} pricing insights - market analysis opportunities"
            )

        # Regional recommendations
        if region.lower() == "buffalo":
            recommendations.append(
                "🌊 Buffalo cannabis market - monitor Niagara Falls tourism integration"
            )

        # General recommendations
        if license_intel or regulatory_intel:
            recommendations.append(
                "📊 Cross-reference with local zoning and real estate opportunities"
            )
            recommendations.append(
                "🔗 Monitor for affiliate partnership opportunities with dispensaries"
            )

        return recommendations


def main():
    """Main EQ12 cannabis intelligence runner"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Cannabis Intelligence")
    parser.add_argument(
        "--mode",
        choices=["licenses", "regulatory", "tourism", "pricing", "report"],
        default="licenses",
        help="Intelligence gathering mode",
    )
    parser.add_argument("--region", default="Buffalo", help="Region to focus on")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    try:
        intel = EQ12CannabisIntelligence(verbose=args.verbose)

        if args.mode == "licenses":
            results = intel.track_dispensary_licenses(args.region)
            print(f"✅ License intelligence: {len(results)} updates found in {args.region}")

        elif args.mode == "regulatory":
            results = intel.monitor_regulatory_updates()
            print(f"✅ Regulatory intelligence: {len(results)} updates found")

        elif args.mode == "tourism":
            results = intel.scout_tourism_opportunities()
            print(f"✅ Tourism intelligence: {len(results)} opportunities found")

        elif args.mode == "pricing":
            results = intel.track_market_prices()
            print(f"✅ Pricing intelligence: {len(results)} insights found")

        elif args.mode == "report":
            report = intel.generate_cannabis_report(args.region)
            print(f"✅ Cannabis intelligence report generated for {args.region}")
            print(f"📊 Summary: {report['intelligence_summary']}")
            for rec in report["recommendations"]:
                print(f"   💡 {rec}")

        print("\\n🎯 Integration: Check C:\\EQ12\\logs for detailed results")
        print("🌿 Cannabis Intel: Monitor for business and regulatory opportunities")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
