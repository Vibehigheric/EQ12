#!/usr/bin/env python3
"""
EQ12 Travel Stack + Bing Intelligence Integration
Enhances existing travel deals scraper with Bing search intelligence.
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))

try:
    from bing_web_search import EQ12BingSearch, send_urgent_alert, setup_eq12_logging
except ImportError as e:
    print(f"❌ Error importing EQ12 Bing core: {e}")
    sys.exit(1)


class EQ12TravelIntelligence:
    """
    Travel Intelligence Engine for EQ12
    Integrates with existing travel automation and affiliate systems
    """

    def __init__(self, verbose: bool = False):
        self.bing = EQ12BingSearch(verbose)
        self.logger = setup_eq12_logging(verbose)
        self.eq12_root = Path("C:/EQ12")

        # Popular departure airports (Buffalo area)
        self.departure_codes = ["BUF", "ROC", "SYR", "YTZ"]

        # Popular destinations from Buffalo
        self.popular_destinations = [
            "LAX",
            "MIA",
            "LAS",
            "DEN",
            "ATL",
            "MCO",
            "FLL",
            "PHX",
            "SEA",
            "SAN",
            "BOS",
            "NYC",
            "JFK",
            "LGA",
        ]

        # Travel deal keywords for filtering
        self.deal_keywords = [
            "deal",
            "sale",
            "discount",
            "special",
            "promo",
            "offer",
            "$",
            "cheap",
            "low fare",
            "error fare",
            "flash sale",
            "limited time",
            "today only",
            "weekend sale",
            "clearance",
        ]

        # Hotel chains for affiliate tracking
        self.hotel_chains = [
            "Marriott",
            "Hilton",
            "Hyatt",
            "IHG",
            "Choice Hotels",
            "Best Western",
            "Wyndham",
            "Radisson",
            "Omni",
        ]

    def find_flight_deals(
        self, departure: str = "BUF", destinations: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Find flight deals from specific departure city"""

        if destinations is None:
            destinations = self.popular_destinations[:8]  # Limit to avoid too many API calls

        self.logger.info(f"✈️ Searching flight deals from {departure}...")

        # Generate time-aware search queries
        next_month = (datetime.now() + timedelta(days=30)).strftime("%B %Y")
        season = self._get_current_season()

        queries = []
        for dest in destinations:
            queries.extend(
                [
                    f"cheap flights {departure} to {dest} {next_month}",
                    f"flight deals Buffalo to {dest} {season} 2025",
                    f"{departure} {dest} airline sale discount error fare",
                    f"Southwest JetBlue {departure} {dest} special offer",
                ]
            )

        # Limit queries to avoid hitting rate limits
        queries = queries[:20]

        results = self.bing.search_for_stack(queries, "travel_flights", "web")

        # Filter for actual deals
        deal_results = self._filter_flight_deals(results)

        # Send alerts for exceptional deals
        if deal_results:
            self._send_travel_alerts(deal_results, "flight_deals")

        return deal_results

    def _get_current_season(self) -> str:
        """Get current travel season for targeted searches"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        if month in [3, 4, 5]:
            return "spring"
        if month in [6, 7, 8]:
            return "summer"
        return "fall"

    def _filter_flight_deals(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter search results to identify actual flight deals"""
        deal_results = []

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            # Calculate deal score
            deal_score = 0
            matched_keywords = []

            # Check for deal keywords
            for keyword in self.deal_keywords:
                if keyword in text:
                    deal_score += 2 if keyword in ["$", "error fare", "flash sale"] else 1
                    matched_keywords.append(keyword)

            # Check for price indicators
            price_patterns = [
                r"\\$\\d+",
                r"\\d+% off",
                r"save \\$\\d+",
                r"from \\$\\d+",
            ]
            for pattern in price_patterns:
                if re.search(pattern, text):
                    deal_score += 3
                    matched_keywords.append("price_found")

            # Check for urgency indicators
            urgency_patterns = [
                "today only",
                "limited time",
                "expires",
                "hurry",
                "last chance",
            ]
            for urgency in urgency_patterns:
                if urgency in text:
                    deal_score += 2
                    matched_keywords.append(f"urgent:{urgency}")

            # Mark as deal if score meets threshold
            if deal_score >= 3:
                result["deal_score"] = deal_score
                result["matched_keywords"] = matched_keywords
                result["deal_type"] = "flight"
                deal_results.append(result)

                self.logger.info(f"💰 FLIGHT DEAL: {result['title'][:60]}... (Score: {deal_score})")

        return deal_results

    def monitor_hotel_deals(self, cities: list[str] | None = None) -> list[dict[str, Any]]:
        """Monitor hotel deals in target cities"""

        if cities is None:
            cities = [
                "Buffalo",
                "Niagara Falls",
                "Rochester",
                "Las Vegas",
                "Miami",
                "Orlando",
            ]

        self.logger.info(f"🏨 Monitoring hotel deals in {len(cities)} cities...")

        queries = []
        for city in cities:
            for chain in self.hotel_chains[:5]:  # Limit to major chains
                queries.append(f"{chain} hotel deals {city} winter 2025")

            queries.extend(
                [
                    f"hotel deals {city} weekend getaway packages",
                    f"cheap hotels {city} last minute bookings",
                    f"{city} hotel sale discount code promo",
                ]
            )

        # Limit total queries
        queries = queries[:25]

        results = self.bing.search_for_stack(queries, "travel_hotels", "web")

        # Filter for hotel deals
        hotel_deals = self._filter_hotel_deals(results)

        if hotel_deals:
            self._send_travel_alerts(hotel_deals, "hotel_deals")

        return hotel_deals

    def _filter_hotel_deals(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter results for genuine hotel deals"""
        deal_results = []

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            # Must mention hotels
            hotel_indicators = ["hotel", "resort", "inn", "lodge", "suite", "motel"]
            if not any(indicator in text for indicator in hotel_indicators):
                continue

            # Calculate deal score
            deal_score = 0
            matched_keywords = []

            # Deal keywords
            for keyword in self.deal_keywords:
                if keyword in text:
                    deal_score += 1
                    matched_keywords.append(keyword)

            # Percentage/price discounts
            if re.search(r"\\d+% off|save \\d+%|up to \\d+% off", text):
                deal_score += 3
                matched_keywords.append("percentage_discount")

            # Free amenities
            free_amenities = [
                "free wifi",
                "free breakfast",
                "free parking",
                "free cancellation",
            ]
            for amenity in free_amenities:
                if amenity in text:
                    deal_score += 1
                    matched_keywords.append(f"amenity:{amenity}")

            if deal_score >= 2:
                result["deal_score"] = deal_score
                result["matched_keywords"] = matched_keywords
                result["deal_type"] = "hotel"
                deal_results.append(result)

        return deal_results

    def monitor_travel_news(self) -> list[dict[str, Any]]:
        """Monitor travel-related news for opportunities and alerts"""

        queries = [
            "Buffalo airport news flight routes 2025",
            "new airline service Buffalo Niagara airport",
            "travel restrictions lifted destinations December",
            "airline sale winter 2025 routes from Buffalo",
            "travel deals Buffalo residents exclusive offers",
            "Buffalo tourism incentives visitor packages",
            "Southwest Airlines JetBlue new routes Buffalo",
        ]

        results = self.bing.search_for_stack(queries, "travel_news", "news")

        # Filter for actionable travel news
        actionable_news = []

        news_keywords = [
            "new route",
            "new service",
            "expansion",
            "launch",
            "inaugural",
            "restrictions lifted",
            "reopening",
            "sale",
            "promotion",
            "incentive",
        ]

        for result in results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            if any(keyword in text for keyword in news_keywords):
                result["news_type"] = "actionable"
                actionable_news.append(result)
                self.logger.info(f"📰 TRAVEL NEWS: {result['title'][:60]}...")

        return actionable_news

    def find_destination_intelligence(self, destination: str) -> list[dict[str, Any]]:
        """Gather intelligence about a specific destination"""

        queries = [
            f"{destination} travel guide 2025 winter attractions",
            f"{destination} weather forecast December 2025 travel",
            f"{destination} hotel deals restaurant recommendations",
            f"{destination} travel warnings safety updates",
            f"{destination} events festivals December 2025 calendar",
            f"best time visit {destination} winter activities",
        ]

        results = self.bing.search_for_stack(
            queries, f"travel_dest_{destination.replace(' ', '_')}", "web"
        )

        self.logger.info(f"🌍 {destination} intelligence: {len(results)} insights gathered")
        return results

    def _send_travel_alerts(self, deals: list[dict[str, Any]], alert_type: str):
        """Send travel deal alerts via Telegram"""

        if not deals:
            return

        # Sort by deal score and send top deals
        top_deals = sorted(deals, key=lambda x: x.get("deal_score", 0), reverse=True)[:3]

        for deal in top_deals:
            if deal.get("deal_score", 0) >= 5:  # High-value deals only
                alert_msg = self._format_travel_alert(deal, alert_type)
                send_urgent_alert(alert_msg)

        self.logger.info(
            f"📱 Sent {len([d for d in top_deals if d.get('deal_score', 0) >= 5])} travel alerts"
        )

    def _format_travel_alert(self, deal: dict[str, Any], alert_type: str) -> str:
        """Format travel deal alert for Telegram"""

        emoji_map = {"flight_deals": "✈️", "hotel_deals": "🏨", "travel_news": "📰"}

        emoji = emoji_map.get(alert_type, "🎯")
        keywords_str = ", ".join(deal.get("matched_keywords", [])[:4])

        message = f"""{emoji} **TRAVEL DEAL ALERT**

**{deal["title"]}**

{deal["snippet"][:200]}...

**Deal Score:** {deal.get("deal_score", 0)}/10
**Keywords:** {keywords_str}
**Source:** {deal["url"]}

💰 *Check for affiliate opportunities*"""

        return message

    def generate_travel_report(self) -> dict[str, Any]:
        """Generate comprehensive travel intelligence report"""

        self.logger.info("📋 Generating travel intelligence report...")

        # Gather intelligence
        flight_deals = self.find_flight_deals()
        hotel_deals = self.monitor_hotel_deals()
        travel_news = self.monitor_travel_news()

        # Generate summary
        report = {
            "generated_at": datetime.now().isoformat(),
            "intelligence_summary": {
                "total_flight_deals": len(flight_deals),
                "high_value_flight_deals": len(
                    [d for d in flight_deals if d.get("deal_score", 0) >= 5]
                ),
                "total_hotel_deals": len(hotel_deals),
                "high_value_hotel_deals": len(
                    [d for d in hotel_deals if d.get("deal_score", 0) >= 4]
                ),
                "travel_news_items": len(travel_news),
            },
            "flight_deals": flight_deals,
            "hotel_deals": hotel_deals,
            "travel_news": travel_news,
            "recommendations": self._generate_travel_recommendations(
                flight_deals, hotel_deals, travel_news
            ),
        }

        # Save report
        report_file = (
            self.eq12_root
            / "logs"
            / f"travel_intelligence_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"✅ Travel report saved: {report_file}")
        return report

    def _generate_travel_recommendations(
        self, flight_deals: list[dict], hotel_deals: list[dict], travel_news: list[dict]
    ) -> list[str]:
        """Generate actionable travel recommendations"""

        recommendations = []

        # Flight deal recommendations
        high_flight_deals = [d for d in flight_deals if d.get("deal_score", 0) >= 5]
        if high_flight_deals:
            recommendations.append(
                f"✈️ {len(high_flight_deals)} exceptional flight deals - create affiliate content"
            )

        # Hotel deal recommendations
        high_hotel_deals = [d for d in hotel_deals if d.get("deal_score", 0) >= 4]
        if high_hotel_deals:
            recommendations.append(
                f"🏨 {len(high_hotel_deals)} hotel deals - build destination packages"
            )

        # News-based recommendations
        if travel_news:
            recommendations.append(
                f"📰 {len(travel_news)} travel news items - content opportunities"
            )

        # Seasonal recommendations
        season = self._get_current_season()
        if season == "winter":
            recommendations.append("🎿 Winter season - focus on warm destinations and ski packages")

        # General recommendations
        if flight_deals or hotel_deals:
            recommendations.append("💰 Update affiliate links and create deal alert content")
            recommendations.append("📊 Cross-reference with existing travel scraper data")

        return recommendations


def main():
    """Main EQ12 travel intelligence runner"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Travel Intelligence")
    parser.add_argument(
        "--mode",
        choices=["flights", "hotels", "news", "destination", "report"],
        default="flights",
        help="Intelligence gathering mode",
    )
    parser.add_argument("--departure", default="BUF", help="Departure airport code")
    parser.add_argument("--destination", help="Specific destination for intelligence")
    parser.add_argument("--cities", nargs="+", help="Cities for hotel search")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    try:
        intel = EQ12TravelIntelligence(verbose=args.verbose)

        if args.mode == "flights":
            results = intel.find_flight_deals(args.departure)
            print(f"✅ Flight deals: {len(results)} deals found from {args.departure}")

        elif args.mode == "hotels":
            results = intel.monitor_hotel_deals(args.cities)
            cities_str = ", ".join(args.cities) if args.cities else "default cities"
            print(f"✅ Hotel deals: {len(results)} deals found in {cities_str}")

        elif args.mode == "news":
            results = intel.monitor_travel_news()
            print(f"✅ Travel news: {len(results)} actionable items found")

        elif args.mode == "destination":
            if not args.destination:
                print("❌ Destination mode requires --destination")
                return
            results = intel.find_destination_intelligence(args.destination)
            print(f"✅ Destination intelligence: {len(results)} insights for {args.destination}")

        elif args.mode == "report":
            report = intel.generate_travel_report()
            print("✅ Travel intelligence report generated")
            print(f"📊 Summary: {report['intelligence_summary']}")
            for rec in report["recommendations"]:
                print(f"   💡 {rec}")

        print("\\n🎯 Integration: Check C:\\EQ12\\logs for detailed results")
        print("🔗 Affiliate: Intelligence ready for content creation")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
