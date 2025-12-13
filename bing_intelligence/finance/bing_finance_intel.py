#!/usr/bin/env python3
"""
EQ12 Finance Stack + Bing Intelligence Integration
Monitors housing market, credit opportunities, and macro-economic intelligence.
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


class EQ12FinanceIntelligence:
    """
    Financial Intelligence Engine for EQ12
    Monitors housing market, credit opportunities, and economic trends
    """

    def __init__(self, verbose: bool = False):
        self.bing = EQ12BingSearch(verbose)
        self.logger = setup_eq12_logging(verbose)
        self.eq12_root = Path("C:/EQ12")

        # Buffalo area markets to monitor
        self.buffalo_markets = [
            "Buffalo",
            "Amherst",
            "Clarence",
            "Orchard Park",
            "West Seneca",
            "Cheektowaga",
            "Tonawanda",
            "Kenmore",
            "Williamsville",
            "East Aurora",
        ]

        # Economic indicators to track
        self.economic_indicators = [
            "mortgage rates",
            "housing prices",
            "inventory",
            "foreclosure",
            "rent prices",
            "property tax",
            "home sales",
            "market trends",
            "affordability",
            "first time buyer",
            "down payment assistance",
        ]

        # Credit/financial opportunity keywords
        self.credit_keywords = [
            "credit repair",
            "credit score",
            "FICO",
            "credit report",
            "dispute",
            "debt consolidation",
            "personal loan",
            "refinance",
            "mortgage",
            "bankruptcy",
            "credit building",
            "secured card",
            "credit limit",
        ]

        # Investment opportunity indicators
        self.investment_keywords = [
            "investment property",
            "rental property",
            "ROI",
            "cap rate",
            "cash flow",
            "flip",
            "rehab",
            "distressed",
            "auction",
            "undervalued",
            "appreciation",
            "gentrification",
            "development",
        ]

    def track_housing_market(self, market: str = "Buffalo") -> list[dict[str, Any]]:
        """Track housing market trends and opportunities"""

        self.logger.info(f"🏠 Tracking housing market in {market}...")

        queries = [
            f"{market} housing market trends December 2025",
            f"{market} home prices median December 2025",
            f"{market} NY real estate market report latest",
            f"mortgage rates {market} December 2025 forecast",
            f"{market} foreclosure listings investment opportunities",
            f"{market} rental market vacancy rates December",
            f"first time home buyer programs {market} NY",
        ]

        results = self.bing.search_for_stack(queries, f"finance_housing_{market.lower()}", "news")

        # Filter for market intelligence
        market_intel = self._filter_housing_intelligence(results)

        # Send alerts for significant market changes
        if market_intel:
            self._send_finance_alerts(market_intel, "housing_market", market)

        return market_intel

    def _filter_housing_intelligence(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter results for genuine housing market intelligence"""
        market_results = []

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            # Calculate market relevance score
            relevance_score = 0
            matched_keywords = []

            # Check for economic indicators
            for indicator in self.economic_indicators:
                if indicator in text:
                    relevance_score += 2
                    matched_keywords.append(indicator)

            # Look for price/percentage data
            price_patterns = [
                r"\\$\\d+k",
                r"\\$\\d+,\\d+",
                r"\\d+%",
                r"\\d+\\.\\d+%",
                r"\\d+ basis points",
                r"median price",
                r"average price",
            ]

            for pattern in price_patterns:
                if re.search(pattern, text):
                    relevance_score += 3
                    matched_keywords.append("price_data")

            # Market movement indicators
            movement_terms = [
                "increase",
                "decrease",
                "rise",
                "fall",
                "surge",
                "drop",
                "up from",
                "down from",
                "compared to",
                "year over year",
            ]

            for term in movement_terms:
                if term in text:
                    relevance_score += 1
                    matched_keywords.append(f"movement:{term}")

            # Investment opportunity indicators
            for keyword in self.investment_keywords:
                if keyword in text:
                    relevance_score += 2
                    matched_keywords.append(f"investment:{keyword}")

            if relevance_score >= 4:
                result["relevance_score"] = relevance_score
                result["matched_keywords"] = matched_keywords
                result["intel_type"] = "housing_market"
                market_results.append(result)

                self.logger.info(
                    f"🏠 HOUSING INTEL: {result['title'][:60]}... (Score: {relevance_score})"
                )

        return market_results

    def monitor_credit_opportunities(self) -> list[dict[str, Any]]:
        """Monitor credit repair and financial opportunities"""

        self.logger.info("💳 Monitoring credit and financial opportunities...")

        queries = [
            "credit repair services Buffalo NY reviews 2025",
            "debt consolidation programs New York December",
            "credit score improvement tips December 2025",
            "personal loan rates Buffalo NY December 2025",
            "mortgage refinance rates New York December",
            "credit building secured cards December 2025",
            "bankruptcy alternatives New York state programs",
        ]

        results = self.bing.search_for_stack(queries, "finance_credit", "web")

        # Filter for credit opportunities
        credit_intel = []

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            credit_score = 0
            matched_keywords = []

            # Check for credit keywords
            for keyword in self.credit_keywords:
                if keyword in text:
                    credit_score += 1
                    matched_keywords.append(keyword)

            # Look for rates/offers
            rate_patterns = [
                r"\\d+\\.\\d+% APR",
                r"\\d+% interest",
                r"no fee",
                r"0% intro",
            ]
            for pattern in rate_patterns:
                if re.search(pattern, text):
                    credit_score += 2
                    matched_keywords.append("rate_offer")

            # Service indicators
            service_terms = [
                "consultation",
                "free",
                "guaranteed",
                "approved",
                "qualified",
            ]
            for term in service_terms:
                if term in text:
                    credit_score += 1
                    matched_keywords.append(f"service:{term}")

            if credit_score >= 3:
                result["credit_score"] = credit_score
                result["matched_keywords"] = matched_keywords
                result["intel_type"] = "credit_opportunity"
                credit_intel.append(result)

        return credit_intel

    def track_economic_indicators(self) -> list[dict[str, Any]]:
        """Track macro-economic indicators affecting Buffalo area"""

        self.logger.info("📊 Tracking economic indicators...")

        queries = [
            "Buffalo NY economic development December 2025",
            "Western New York employment rate December 2025",
            "inflation impact Buffalo housing December 2025",
            "Federal Reserve rate change mortgage impact",
            "New York state budget impact local economy",
            "Buffalo unemployment rate December 2025 statistics",
            "Western NY GDP growth economic forecast 2025",
        ]

        results = self.bing.search_for_stack(queries, "finance_economic", "news")

        # Filter for economic intelligence
        economic_intel = []

        economic_terms = [
            "GDP",
            "unemployment",
            "inflation",
            "interest rate",
            "Fed",
            "Federal Reserve",
            "employment",
            "job growth",
            "recession",
            "recovery",
            "economic growth",
            "consumer spending",
            "retail sales",
            "housing starts",
            "construction",
        ]

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            # Check for economic indicators
            if any(term in text for term in economic_terms):
                result["intel_type"] = "economic_indicator"
                economic_intel.append(result)

        return economic_intel

    def find_investment_opportunities(self) -> list[dict[str, Any]]:
        """Find real estate and investment opportunities in Buffalo area"""

        self.logger.info("💰 Scouting investment opportunities...")

        queries = []
        for market in self.buffalo_markets[:5]:  # Limit to avoid too many API calls
            queries.extend(
                [
                    f"{market} investment property for sale December 2025",
                    f"{market} rental property cash flow analysis",
                    f"{market} distressed property auction December 2025",
                    f"{market} commercial real estate investment December",
                ]
            )

        results = self.bing.search_for_stack(queries, "finance_investment", "web")

        # Filter for investment opportunities
        investment_intel = []

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            investment_score = 0
            matched_keywords = []

            # Investment opportunity keywords
            for keyword in self.investment_keywords:
                if keyword in text:
                    investment_score += 2
                    matched_keywords.append(keyword)

            # Financial metrics
            metric_patterns = [
                r"\\d+% return",
                r"cap rate",
                r"\\$\\d+/month",
                r"cash flow",
            ]
            for pattern in metric_patterns:
                if re.search(pattern, text):
                    investment_score += 3
                    matched_keywords.append("financial_metrics")

            # Property types
            property_types = [
                "duplex",
                "triplex",
                "multi-family",
                "commercial",
                "retail",
            ]
            for ptype in property_types:
                if ptype in text:
                    investment_score += 1
                    matched_keywords.append(f"property:{ptype}")

            if investment_score >= 3:
                result["investment_score"] = investment_score
                result["matched_keywords"] = matched_keywords
                result["intel_type"] = "investment_opportunity"
                investment_intel.append(result)

        return investment_intel

    def _send_finance_alerts(
        self, results: list[dict[str, Any]], alert_type: str, region: str = "Buffalo"
    ):
        """Send finance intelligence alerts via Telegram"""

        if not results:
            return

        # Sort by relevance score
        score_key = "relevance_score"
        if alert_type == "credit_opportunity":
            score_key = "credit_score"
        elif alert_type == "investment_opportunity":
            score_key = "investment_score"

        top_results = sorted(results, key=lambda x: x.get(score_key, 0), reverse=True)[:3]

        alert_count = 0
        for result in top_results:
            if result.get(score_key, 0) >= 5:  # High-value alerts only
                alert_msg = self._format_finance_alert(result, alert_type, region)
                send_urgent_alert(alert_msg)
                alert_count += 1

        self.logger.info(f"📱 Sent {alert_count} finance intelligence alerts")

    def _format_finance_alert(self, result: dict[str, Any], alert_type: str, region: str) -> str:
        """Format finance intelligence alert for Telegram"""

        emoji_map = {
            "housing_market": "🏠",
            "credit_opportunity": "💳",
            "investment_opportunity": "💰",
            "economic_indicator": "📊",
        }

        emoji = emoji_map.get(alert_type, "💼")
        keywords_str = ", ".join(result.get("matched_keywords", [])[:5])

        score_key = next((k for k in result if k.endswith("_score")), "score")
        score = result.get(score_key, 0)

        message = f"""{emoji} **FINANCE INTEL ALERT - {region.upper()}**

**{result["title"]}**

{result["snippet"][:200]}...

**Intel Score:** {score}/10
**Keywords:** {keywords_str}
**Source:** {result["url"]}

💼 *Monitor for financial opportunities*"""

        return message

    def generate_finance_report(self, market: str = "Buffalo") -> dict[str, Any]:
        """Generate comprehensive finance intelligence report"""

        self.logger.info(f"📋 Generating finance intelligence report for {market}...")

        # Gather all intelligence types
        housing_intel = self.track_housing_market(market)
        credit_intel = self.monitor_credit_opportunities()
        economic_intel = self.track_economic_indicators()
        investment_intel = self.find_investment_opportunities()

        # Generate summary
        report = {
            "market": market,
            "generated_at": datetime.now().isoformat(),
            "intelligence_summary": {
                "housing_insights": len(housing_intel),
                "high_relevance_housing": len(
                    [h for h in housing_intel if h.get("relevance_score", 0) >= 6]
                ),
                "credit_opportunities": len(credit_intel),
                "economic_indicators": len(economic_intel),
                "investment_opportunities": len(investment_intel),
                "high_value_investments": len(
                    [i for i in investment_intel if i.get("investment_score", 0) >= 5]
                ),
            },
            "housing_intelligence": housing_intel,
            "credit_intelligence": credit_intel,
            "economic_intelligence": economic_intel,
            "investment_intelligence": investment_intel,
            "recommendations": self._generate_finance_recommendations(
                housing_intel, credit_intel, economic_intel, investment_intel, market
            ),
        }

        # Save report
        report_file = (
            self.eq12_root
            / "logs"
            / f"finance_intelligence_{market.lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"✅ Finance report saved: {report_file}")
        return report

    def _generate_finance_recommendations(
        self,
        housing_intel: list[dict],
        credit_intel: list[dict],
        economic_intel: list[dict],
        investment_intel: list[dict],
        market: str,
    ) -> list[str]:
        """Generate actionable finance intelligence recommendations"""

        recommendations = []

        # Housing market recommendations
        high_housing = [h for h in housing_intel if h.get("relevance_score", 0) >= 6]
        if high_housing:
            recommendations.append(
                f"🏠 {len(high_housing)} significant housing market changes in {market}"
            )

        # Investment recommendations
        high_investment = [i for i in investment_intel if i.get("investment_score", 0) >= 5]
        if high_investment:
            recommendations.append(
                f"💰 {len(high_investment)} high-value investment opportunities identified"
            )

        # Credit opportunities
        if credit_intel:
            recommendations.append(
                f"💳 {len(credit_intel)} credit/financing opportunities available"
            )

        # Economic context
        if economic_intel:
            recommendations.append(
                f"📊 {len(economic_intel)} economic indicators - monitor macro trends"
            )

        # Market-specific recommendations
        if market.lower() == "buffalo":
            recommendations.append(
                "🌊 Buffalo market - consider Niagara Falls tourism impact on real estate"
            )

        # Seasonal recommendations
        month = datetime.now().month
        if month in [11, 12, 1]:
            recommendations.append(
                "❄️ Winter season - monitor for off-season investment opportunities"
            )

        # General recommendations
        if housing_intel or investment_intel:
            recommendations.append(
                "📈 Cross-reference with local employment and development projects"
            )
            recommendations.append("🔍 Monitor for tax assessment and zoning change opportunities")

        return recommendations


def main():
    """Main EQ12 finance intelligence runner"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Finance Intelligence")
    parser.add_argument(
        "--mode",
        choices=["housing", "credit", "economic", "investment", "report"],
        default="housing",
        help="Intelligence gathering mode",
    )
    parser.add_argument("--market", default="Buffalo", help="Market/region to focus on")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    try:
        intel = EQ12FinanceIntelligence(verbose=args.verbose)

        if args.mode == "housing":
            results = intel.track_housing_market(args.market)
            print(f"✅ Housing intelligence: {len(results)} market insights for {args.market}")

        elif args.mode == "credit":
            results = intel.monitor_credit_opportunities()
            print(f"✅ Credit intelligence: {len(results)} opportunities found")

        elif args.mode == "economic":
            results = intel.track_economic_indicators()
            print(f"✅ Economic intelligence: {len(results)} indicators tracked")

        elif args.mode == "investment":
            results = intel.find_investment_opportunities()
            print(f"✅ Investment intelligence: {len(results)} opportunities identified")

        elif args.mode == "report":
            report = intel.generate_finance_report(args.market)
            print(f"✅ Finance intelligence report generated for {args.market}")
            print(f"📊 Summary: {report['intelligence_summary']}")
            for rec in report["recommendations"]:
                print(f"   💡 {rec}")

        print("\\n🎯 Integration: Check C:\\EQ12\\logs for detailed results")
        print("💼 Finance Intel: Monitor for investment and market opportunities")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
