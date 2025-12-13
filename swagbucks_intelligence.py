#!/usr/bin/env python3
"""
EQ12 Swagbucks Intelligence Module
Integrates Swagbucks offer scraping with EQ12 stack-specific intelligence and routing.

Author: EQ12 AI Assistant
Created: 2025-01-27
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

# Add paths for integration
BASE_DIR = Path(__file__).resolve().parent
GODSTACK2_DIR = Path(r"C:\EQ12\eq12_godstack2")
sys.path.insert(0, str(GODSTACK2_DIR))

# Import existing Swagbucks scraper
try:
    from swagbucks_offers import CATEGORIES, scrape_offers

    SWAGBUCKS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Swagbucks scraper not available: {e}")
    SWAGBUCKS_AVAILABLE = False

# Import enhanced database for intelligence storage
try:
    sys.path.insert(0, str(BASE_DIR / "eq12_meta_search"))
    from enhanced_db import (
        cache_stack_analysis,
        get_cached_analysis,
        record_performance_metric,
        upsert_enhanced_results,
    )

    ENHANCED_DB_AVAILABLE = True
except ImportError:
    ENHANCED_DB_AVAILABLE = False

logger = logging.getLogger("swagbucks_intelligence")


class SwagbucksIntelligence:
    """
    Enhanced Swagbucks integration with EQ12 stack intelligence
    """

    # Stack-specific offer categories and keywords
    STACK_OFFER_MAPPING = {
        "betting": {
            "keywords": [
                "draftkings",
                "fanduel",
                "caesars",
                "betmgm",
                "sportsbook",
                "fantasy",
                "sports",
                "gaming",
                "casino",
                "poker",
            ],
            "categories": ["gaming", "sports", "fantasy"],
            "priority_multiplier": 1.5,
            "telegram_emoji": "🎲",
        },
        "travel": {
            "keywords": [
                "expedia",
                "booking",
                "hotels",
                "airfare",
                "flight",
                "travel",
                "vacation",
                "rental car",
                "uber",
                "lyft",
                "airline",
                "trip",
            ],
            "categories": ["travel", "hotels", "flights", "transportation"],
            "priority_multiplier": 1.8,
            "telegram_emoji": "✈️",
        },
        "cannabis": {
            "keywords": [
                "cbd",
                "hemp",
                "wellness",
                "health",
                "supplements",
                "natural",
                "organic",
                "headshop",
                "vape",
                "smoke",
                "glass",
            ],
            "categories": ["health", "wellness", "lifestyle"],
            "priority_multiplier": 1.3,
            "telegram_emoji": "🌿",
        },
        "finance": {
            "keywords": [
                "credit card",
                "bank",
                "financial",
                "investment",
                "crypto",
                "bitcoin",
                "trading",
                "cashback",
                "rewards",
                "loan",
                "mortgage",
                "insurance",
            ],
            "categories": ["financial", "banking", "insurance", "credit"],
            "priority_multiplier": 2.0,
            "telegram_emoji": "💰",
        },
        "fleet": {
            "keywords": [
                "auto",
                "car",
                "vehicle",
                "insurance",
                "gas",
                "fuel",
                "tires",
                "maintenance",
                "rental",
                "lease",
                "financing",
                "dealership",
            ],
            "categories": ["automotive", "insurance", "fuel"],
            "priority_multiplier": 1.4,
            "telegram_emoji": "🚗",
        },
    }

    # Enhanced Swagbucks categories with stack mapping
    ENHANCED_CATEGORIES = [
        ("https://www.swagbucks.com/g/shop", "shopping", ["finance", "fleet"]),
        ("https://www.swagbucks.com/g/best-offers", "best", ["finance", "travel"]),
        ("https://www.swagbucks.com/g/travel", "travel", ["travel"]),
        ("https://www.swagbucks.com/g/games", "gaming", ["betting"]),
        ("https://www.swagbucks.com/g/financial", "financial", ["finance"]),
        ("https://www.swagbucks.com/g/health", "health", ["cannabis"]),
        ("https://www.swagbucks.com/g/services", "services", ["fleet", "finance"]),
    ]

    def __init__(self, verbose: bool = False):
        """Initialize Swagbucks intelligence module"""
        self.verbose = verbose
        self.setup_logging()

        if not SWAGBUCKS_AVAILABLE:
            raise ValueError("Swagbucks scraper not available - check godstack2 installation")

    def setup_logging(self):
        """Setup EQ12-standard logging"""
        log_level = logging.INFO if self.verbose else logging.WARNING
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def detect_offer_stack(self, offer: dict[str, Any]) -> str | None:
        """
        Detect which EQ12 stack an offer belongs to

        Args:
            offer: Swagbucks offer dictionary

        Returns:
            Stack name or None if no clear match
        """
        title = offer.get("title", "").lower()
        reward = offer.get("reward", "").lower()
        category = offer.get("category", "").lower()

        # Combine all text for analysis
        offer_text = f"{title} {reward} {category}"

        stack_scores = {}

        # Score based on keywords
        for stack, config in self.STACK_OFFER_MAPPING.items():
            score = 0
            for keyword in config["keywords"]:
                if keyword in offer_text:
                    score += 1

            # Category boost
            if category in config.get("categories", []):
                score += 2

            if score > 0:
                stack_scores[stack] = score * config.get("priority_multiplier", 1.0)

        if stack_scores:
            # Return stack with highest score
            best_stack = max(stack_scores.keys(), key=lambda k: stack_scores[k])
            confidence = min(1.0, stack_scores[best_stack] / 5.0)  # Normalize to 0-1

            if confidence >= 0.3:  # Minimum confidence threshold
                return best_stack

        return None

    def enhance_offers_with_intelligence(
        self, offers: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Enhance Swagbucks offers with EQ12 intelligence metadata

        Args:
            offers: List of raw Swagbucks offers

        Returns:
            List of enhanced offers with intelligence metadata
        """
        enhanced_offers = []

        for offer in offers:
            # Detect stack
            detected_stack = self.detect_offer_stack(offer)

            # Calculate confidence and relevance
            confidence = 0.7 if detected_stack else 0.2

            # Enhance offer with metadata
            enhanced_offer = {
                **offer,
                # Intelligence metadata
                "detected_stack": detected_stack,
                "confidence_score": confidence,
                "intelligence_used": True,
                "enhancement_source": "swagbucks_intelligence",
                # Stack-specific metadata
                "stack_priority": self._calculate_stack_priority(offer, detected_stack),
                "telegram_emoji": self._get_telegram_emoji(detected_stack),
                # Analysis metadata
                "keywords_matched": self._extract_matched_keywords(offer, detected_stack),
                "offer_quality": self._assess_offer_quality(offer),
                "urgency_score": self._calculate_urgency(offer),
                # EQ12 integration fields
                "source": "swagbucks_intelligence",
                "content_type": "offer",
                "primary_category": "deals",
                "secondary_category": detected_stack or "general",
            }

            enhanced_offers.append(enhanced_offer)

        return enhanced_offers

    def _calculate_stack_priority(self, offer: dict, stack: str | None) -> float:
        """Calculate priority score for offer based on stack relevance"""
        if not stack:
            return 0.2

        config = self.STACK_OFFER_MAPPING.get(stack, {})
        base_priority = config.get("priority_multiplier", 1.0)

        # Boost for high-value rewards
        reward_text = offer.get("reward", "").lower()
        if any(term in reward_text for term in ["$50", "$100", "50%", "free"]):
            base_priority *= 1.3

        # Boost for time-limited offers
        title_text = offer.get("title", "").lower()
        if any(term in title_text for term in ["limited", "today", "expires", "hurry"]):
            base_priority *= 1.2

        return min(2.0, base_priority)  # Cap at 2.0

    def _get_telegram_emoji(self, stack: str | None) -> str:
        """Get emoji for Telegram alerts based on stack"""
        if not stack:
            return "💎"
        return self.STACK_OFFER_MAPPING.get(stack, {}).get("telegram_emoji", "💎")

    def _extract_matched_keywords(self, offer: dict, stack: str | None) -> list[str]:
        """Extract keywords that matched for this offer"""
        if not stack:
            return []

        offer_text = f"{offer.get('title', '')} {offer.get('reward', '')}".lower()
        config = self.STACK_OFFER_MAPPING.get(stack, {})

        matched = []
        for keyword in config.get("keywords", []):
            if keyword in offer_text:
                matched.append(keyword)

        return matched

    def _assess_offer_quality(self, offer: dict) -> str:
        """Assess the quality of an offer"""
        reward_text = offer.get("reward", "").lower()
        title_text = offer.get("title", "").lower()

        # High quality indicators
        high_indicators = ["$50", "$100", "50%", "free", "bonus", "cashback"]
        if any(term in reward_text for term in high_indicators):
            return "high"

        # Medium quality indicators
        medium_indicators = ["$10", "$20", "25%", "discount", "deal"]
        if any(term in reward_text for term in medium_indicators):
            return "medium"

        # Check title for quality indicators
        if any(term in title_text for term in ["premium", "exclusive", "vip"]):
            return "high"

        return "standard"

    def _calculate_urgency(self, offer: dict) -> float:
        """Calculate urgency score (0.0-1.0) based on time-sensitive language"""
        text = f"{offer.get('title', '')} {offer.get('reward', '')}".lower()

        urgency_terms = {
            "expires today": 1.0,
            "limited time": 0.8,
            "ends soon": 0.7,
            "while supplies last": 0.6,
            "hurry": 0.5,
            "act now": 0.8,
            "today only": 0.9,
        }

        max_urgency = 0.0
        for term, score in urgency_terms.items():
            if term in text:
                max_urgency = max(max_urgency, score)

        return max_urgency

    def scrape_stack_specific_offers(self, stack: str, limit: int = 20) -> list[dict[str, Any]]:
        """
        Scrape Swagbucks offers specifically relevant to an EQ12 stack

        Args:
            stack: EQ12 stack name (betting, travel, cannabis, finance, fleet)
            limit: Maximum number of offers to return

        Returns:
            List of stack-relevant offers with intelligence enhancement
        """
        start_time = time.time()

        # Get relevant categories for this stack
        relevant_categories = []
        for url, category, stacks in self.ENHANCED_CATEGORIES:
            if stack in stacks:
                relevant_categories.append((url, category))

        # If no specific categories, use general ones
        if not relevant_categories:
            relevant_categories = CATEGORIES

        all_offers = []

        # Scrape each relevant category
        for url, category in relevant_categories:
            try:
                if self.verbose:
                    logger.info(f"Scraping {category} offers for {stack} stack")

                # Use existing scraper from godstack2
                offers = scrape_offers(url, category, limit)
                all_offers.extend(offers)

            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")

        # Enhance offers with intelligence
        enhanced_offers = self.enhance_offers_with_intelligence(all_offers)

        # Filter for stack relevance
        stack_offers = [
            offer
            for offer in enhanced_offers
            if offer.get("detected_stack") == stack or offer.get("detected_stack") is None
        ]

        # Sort by priority and confidence
        stack_offers.sort(
            key=lambda x: (x.get("stack_priority", 0), x.get("confidence_score", 0)),
            reverse=True,
        )

        # Record performance metrics
        processing_time = (time.time() - start_time) * 1000
        if ENHANCED_DB_AVAILABLE:
            try:
                record_performance_metric(
                    "swagbucks_scrape_time",
                    processing_time,
                    stack=stack,
                    source="swagbucks_intelligence",
                    metadata={
                        "offers_found": len(stack_offers),
                        "categories_scraped": len(relevant_categories),
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to record performance metric: {e}")

        return stack_offers[:limit]

    def search_offers_with_analysis(
        self, query: str, stack: str | None = None, count: int = 10
    ) -> dict[str, Any]:
        """
        Search and analyze Swagbucks offers with intelligence

        Args:
            query: Search query to influence offer selection
            stack: Target stack (optional, will auto-detect if not provided)
            count: Number of offers to return

        Returns:
            Dictionary with offers and analysis
        """
        start_time = time.time()

        # Auto-detect stack if not provided
        if not stack:
            # This would ideally use the query router, but for now use simple detection
            query_lower = query.lower()
            for stack_name, config in self.STACK_OFFER_MAPPING.items():
                for keyword in config["keywords"]:
                    if keyword in query_lower:
                        stack = stack_name
                        break
                if stack:
                    break

        # Scrape offers
        if stack:
            offers = self.scrape_stack_specific_offers(stack, count * 2)  # Get extra for filtering
        else:
            # General scraping
            all_offers = []
            for url, category in CATEGORIES:
                try:
                    offers_batch = scrape_offers(url, category, count)
                    enhanced_batch = self.enhance_offers_with_intelligence(offers_batch)
                    all_offers.extend(enhanced_batch)
                except Exception as e:
                    logger.error(f"Failed to scrape {url}: {e}")

            offers = all_offers

        # Filter and rank offers
        if query:
            query_terms = query.lower().split()
            filtered_offers = []

            for offer in offers:
                offer_text = f"{offer.get('title', '')} {offer.get('reward', '')}".lower()
                relevance = sum(1 for term in query_terms if term in offer_text)

                if relevance > 0:
                    offer["relevance_score"] = relevance / len(query_terms)
                    filtered_offers.append(offer)

            # Sort by relevance and priority
            filtered_offers.sort(
                key=lambda x: (x.get("relevance_score", 0), x.get("stack_priority", 0)),
                reverse=True,
            )
            offers = filtered_offers

        # Limit results
        final_offers = offers[:count]

        # Generate analysis
        analysis = self._generate_offers_analysis(final_offers, query, stack)

        # Record processing time
        processing_time = (time.time() - start_time) * 1000

        return {
            "query": query,
            "detected_stack": stack,
            "results": final_offers,
            "analysis": analysis,
            "metadata": {
                "total_offers_found": len(offers),
                "processing_time_ms": int(processing_time),
                "intelligence_used": True,
                "enhancement_source": "swagbucks_intelligence",
            },
        }

    def _generate_offers_analysis(
        self, offers: list[dict], query: str, stack: str | None
    ) -> dict[str, Any]:
        """Generate analysis of Swagbucks offers"""
        if not offers:
            return {"summary": "No relevant offers found"}

        analysis = {
            "total_offers": len(offers),
            "stack_distribution": {},
            "quality_distribution": {},
            "avg_urgency": 0.0,
            "top_keywords": [],
            "recommendations": [],
        }

        # Stack distribution
        for offer in offers:
            stack_name = offer.get("detected_stack", "general")
            analysis["stack_distribution"][stack_name] = (
                analysis["stack_distribution"].get(stack_name, 0) + 1
            )

        # Quality distribution
        for offer in offers:
            quality = offer.get("offer_quality", "standard")
            analysis["quality_distribution"][quality] = (
                analysis["quality_distribution"].get(quality, 0) + 1
            )

        # Average urgency
        urgency_scores = [offer.get("urgency_score", 0.0) for offer in offers]
        analysis["avg_urgency"] = (
            sum(urgency_scores) / len(urgency_scores) if urgency_scores else 0.0
        )

        # Top keywords
        all_keywords = []
        for offer in offers:
            all_keywords.extend(offer.get("keywords_matched", []))

        from collections import Counter

        keyword_counts = Counter(all_keywords)
        analysis["top_keywords"] = [kw for kw, count in keyword_counts.most_common(5)]

        # Recommendations
        high_quality = analysis["quality_distribution"].get("high", 0)
        if high_quality > 0:
            analysis["recommendations"].append(f"Found {high_quality} high-quality offers")

        if analysis["avg_urgency"] > 0.5:
            analysis["recommendations"].append("Several time-sensitive offers available")

        if stack and analysis["stack_distribution"].get(stack, 0) > 3:
            analysis["recommendations"].append(f"Strong {stack} stack representation")

        return analysis


# Integration functions for EQ12 system
def search_swagbucks_for_stack(stack: str, count: int = 10) -> dict[str, Any]:
    """Convenience function for stack-specific Swagbucks search"""
    intel = SwagbucksIntelligence()
    return intel.search_offers_with_analysis("", stack=stack, count=count)


def analyze_swagbucks_query(query: str, count: int = 10) -> dict[str, Any]:
    """Convenience function for query-based Swagbucks analysis"""
    intel = SwagbucksIntelligence()
    return intel.search_offers_with_analysis(query, count=count)


# CLI interface
def main():
    """CLI interface for Swagbucks intelligence module"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Swagbucks Intelligence Module")
    parser.add_argument("--query", help="Search query for offers")
    parser.add_argument(
        "--stack",
        choices=["betting", "travel", "cannabis", "finance", "fleet"],
        help="Target EQ12 stack",
    )
    parser.add_argument("--count", type=int, default=10, help="Number of offers to return")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    try:
        intel = SwagbucksIntelligence(verbose=args.verbose)

        if args.stack and not args.query:
            # Stack-specific search
            results = intel.search_offers_with_analysis("", stack=args.stack, count=args.count)
        else:
            # Query-based search
            query = args.query or "general offers"
            results = intel.search_offers_with_analysis(query, stack=args.stack, count=args.count)

        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            print("🎯 Swagbucks Intelligence Results")
            print(f"Query: {results['query']}")
            print(f"Stack: {results['detected_stack'] or 'Auto-detect'}")
            print(f"Offers Found: {len(results['results'])}")
            print()

            for i, offer in enumerate(results["results"][:5], 1):
                emoji = offer.get("telegram_emoji", "💎")
                priority = offer.get("stack_priority", 0)
                quality = offer.get("offer_quality", "standard")

                print(f"{i}. {emoji} {offer.get('title', 'No title')}")
                print(f"   Reward: {offer.get('reward', 'N/A')}")
                print(
                    f"   Stack: {offer.get('detected_stack', 'general')} (priority: {priority:.1f})"
                )
                print(f"   Quality: {quality}")
                print(f"   URL: {offer.get('url', '')}")
                print()

            # Show analysis
            analysis = results.get("analysis", {})
            if analysis.get("recommendations"):
                print("📊 Recommendations:")
                for rec in analysis["recommendations"]:
                    print(f"  • {rec}")

    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
