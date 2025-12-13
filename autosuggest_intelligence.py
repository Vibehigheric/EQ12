#!/usr/bin/env python3
"""
EQ12 Autosuggest Intelligence Module
Enhanced query expansion and SEO keyword generation with EQ12 stack intelligence integration.

Author: EQ12 AI Assistant
Created: 2025-01-27
"""

import json
import logging
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add paths for integration
BASE_DIR = Path(__file__).resolve().parent
GODSTACK2_DIR = Path(r"C:\EQ12\eq12_godstack2")
sys.path.insert(0, str(GODSTACK2_DIR))

# Import existing autosuggest and clients
try:
    from autosuggest_merge import google_suggest
    from clients import BingClient

    AUTOSUGGEST_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Autosuggest not available: {e}")
    AUTOSUGGEST_AVAILABLE = False

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

logger = logging.getLogger("autosuggest_intelligence")


class AutosuggestIntelligence:
    """
    Enhanced autosuggest and query expansion with EQ12 stack intelligence
    """

    # Stack-specific query expansion templates
    STACK_EXPANSION_PROFILES = {
        "betting": {
            "core_terms": [
                "odds",
                "betting",
                "prediction",
                "analysis",
                "picks",
                "tips",
                "injury report",
                "lineup",
                "roster",
                "stats",
                "trend",
                "form",
            ],
            "modifiers": [
                "today",
                "tonight",
                "this week",
                "live",
                "updated",
                "latest",
                "expert",
                "free",
                "premium",
                "sharp",
                "public",
                "contrarian",
            ],
            "sports_expansions": {
                "nfl": [
                    "nfl picks",
                    "nfl odds",
                    "nfl injury report",
                    "nfl predictions",
                ],
                "nba": [
                    "nba picks",
                    "nba odds",
                    "nba injury report",
                    "nba predictions",
                ],
                "mlb": ["mlb picks", "mlb odds", "mlb lineup", "mlb predictions"],
                "nhl": [
                    "nhl picks",
                    "nhl odds",
                    "nhl injury report",
                    "nhl predictions",
                ],
                "ncaa": [
                    "college basketball picks",
                    "march madness",
                    "ncaa tournament",
                ],
            },
            "long_tail_patterns": [
                "{query} picks today",
                "{query} odds",
                "{query} betting tips",
                "{query} injury report",
                "{query} prediction",
                "{query} analysis",
            ],
        },
        "travel": {
            "core_terms": [
                "deals",
                "cheap",
                "discount",
                "flights",
                "hotels",
                "vacation",
                "travel",
                "booking",
                "package",
                "last minute",
                "sale",
            ],
            "modifiers": [
                "buffalo",
                "from buffalo",
                "to buffalo",
                "near me",
                "today",
                "2024",
                "2025",
                "weekend",
                "family",
                "budget",
                "luxury",
            ],
            "destination_expansions": {
                "flights": [
                    "cheap flights",
                    "flight deals",
                    "airfare",
                    "airline tickets",
                ],
                "hotels": ["hotel deals", "cheap hotels", "accommodation", "booking"],
                "packages": ["vacation packages", "travel deals", "all inclusive"],
                "activities": ["things to do", "attractions", "tours", "activities"],
            },
            "long_tail_patterns": [
                "cheap {query}",
                "{query} deals",
                "{query} from buffalo",
                "{query} booking",
                "{query} discount",
                "{query} packages",
            ],
        },
        "cannabis": {
            "core_terms": [
                "dispensary",
                "cannabis",
                "marijuana",
                "weed",
                "thc",
                "cbd",
                "medical",
                "recreational",
                "legal",
                "strain",
                "product",
            ],
            "modifiers": [
                "near me",
                "buffalo",
                "new york",
                "ny",
                "open now",
                "delivery",
                "pickup",
                "menu",
                "prices",
                "reviews",
            ],
            "product_expansions": {
                "flower": ["cannabis flower", "marijuana buds", "weed strains"],
                "edibles": ["cannabis edibles", "thc gummies", "marijuana cookies"],
                "concentrates": ["cannabis concentrates", "dabs", "shatter", "wax"],
                "topicals": ["cannabis topicals", "thc cream", "cbd lotion"],
            },
            "long_tail_patterns": [
                "{query} near me",
                "{query} buffalo",
                "{query} dispensary",
                "{query} delivery",
                "{query} menu",
                "{query} reviews",
            ],
        },
        "finance": {
            "core_terms": [
                "stock",
                "crypto",
                "investment",
                "trading",
                "price",
                "analysis",
                "buy",
                "sell",
                "market",
                "news",
                "forecast",
                "target",
            ],
            "modifiers": [
                "today",
                "now",
                "live",
                "real time",
                "prediction",
                "analysis",
                "2024",
                "2025",
                "bull",
                "bear",
                "trend",
                "technical",
            ],
            "asset_expansions": {
                "stocks": [
                    "stock price",
                    "stock analysis",
                    "stock forecast",
                    "earnings",
                ],
                "crypto": [
                    "bitcoin price",
                    "ethereum price",
                    "crypto news",
                    "crypto analysis",
                ],
                "forex": ["usd", "eur", "currency", "exchange rate"],
                "commodities": ["gold price", "oil price", "commodity futures"],
            },
            "long_tail_patterns": [
                "{query} price",
                "{query} stock",
                "{query} analysis",
                "{query} prediction",
                "{query} news",
                "{query} forecast",
            ],
        },
        "fleet": {
            "core_terms": [
                "car",
                "auto",
                "vehicle",
                "truck",
                "suv",
                "lease",
                "buy",
                "price",
                "review",
                "dealer",
                "financing",
                "insurance",
            ],
            "modifiers": [
                "near me",
                "buffalo",
                "new",
                "used",
                "2024",
                "2025",
                "cheap",
                "best",
                "reliable",
                "fuel efficient",
                "electric",
            ],
            "vehicle_expansions": {
                "new_cars": ["new car prices", "new car deals", "car incentives"],
                "used_cars": ["used car prices", "used car dealers", "car history"],
                "electric": ["electric vehicles", "ev deals", "tesla", "charging"],
                "commercial": ["fleet vehicles", "commercial trucks", "business auto"],
            },
            "long_tail_patterns": [
                "{query} near me",
                "{query} buffalo",
                "{query} price",
                "{query} reviews",
                "{query} deals",
                "{query} financing",
            ],
        },
    }

    # SEO keyword patterns for different intent types
    SEO_INTENT_PATTERNS = {
        "informational": [
            "what is {query}",
            "how to {query}",
            "{query} guide",
            "{query} tips",
            "{query} explained",
            "{query} tutorial",
        ],
        "transactional": [
            "buy {query}",
            "{query} for sale",
            "{query} deals",
            "{query} discount",
            "cheap {query}",
            "{query} price",
        ],
        "local": [
            "{query} near me",
            "{query} buffalo",
            "{query} local",
            "{query} in buffalo",
            "buffalo {query}",
            "{query} western ny",
        ],
        "commercial": [
            "{query} reviews",
            "best {query}",
            "{query} comparison",
            "{query} vs",
            "top {query}",
            "{query} recommendations",
        ],
    }

    def __init__(self, verbose: bool = False):
        """Initialize Autosuggest Intelligence module"""
        self.verbose = verbose
        self.setup_logging()

        if not AUTOSUGGEST_AVAILABLE:
            raise ValueError("Autosuggest not available - check godstack2 installation")

        # Initialize clients
        self.bing_client = BingClient()

    def setup_logging(self):
        """Setup EQ12-standard logging"""
        log_level = logging.INFO if self.verbose else logging.WARNING
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def detect_query_stack(self, query: str) -> tuple[str | None, float]:
        """
        Detect which EQ12 stack a query relates to

        Args:
            query: Search query

        Returns:
            Tuple of (stack_name, confidence_score)
        """
        query_lower = query.lower()
        stack_scores = {}

        # Score each stack based on core terms
        for stack, profile in self.STACK_EXPANSION_PROFILES.items():
            score = 0

            # Check core terms
            for term in profile["core_terms"]:
                if term in query_lower:
                    score += 2

            # Check modifiers
            for modifier in profile["modifiers"]:
                if modifier in query_lower:
                    score += 1

            # Check expansions
            for category, _expansions in profile.get("sports_expansions", {}).items():
                if category in query_lower:
                    score += 3

            for category, _expansions in profile.get("destination_expansions", {}).items():
                if category in query_lower:
                    score += 3

            for category, _expansions in profile.get("product_expansions", {}).items():
                if category in query_lower:
                    score += 3

            for category, _expansions in profile.get("asset_expansions", {}).items():
                if category in query_lower:
                    score += 3

            for category, _expansions in profile.get("vehicle_expansions", {}).items():
                if category in query_lower:
                    score += 3

            if score > 0:
                # Normalize confidence
                confidence = min(1.0, score / 10.0)
                stack_scores[stack] = confidence

        if stack_scores:
            # Return stack with highest confidence
            best_stack = max(stack_scores.keys(), key=lambda k: stack_scores[k])
            confidence = stack_scores[best_stack]

            if confidence >= 0.2:  # Minimum threshold
                return best_stack, confidence

        return None, 0.0

    def generate_stack_expansions(self, query: str, stack: str, count: int = 10) -> list[str]:
        """
        Generate stack-specific query expansions

        Args:
            query: Base query
            stack: Target stack
            count: Number of expansions to generate

        Returns:
            List of expanded queries
        """
        if stack not in self.STACK_EXPANSION_PROFILES:
            return []

        profile = self.STACK_EXPANSION_PROFILES[stack]
        expansions = []

        # Apply long-tail patterns
        for pattern in profile.get("long_tail_patterns", []):
            expanded = pattern.format(query=query)
            expansions.append(expanded)

        # Combine with core terms
        for term in profile["core_terms"][:5]:  # Limit to top 5
            expansions.append(f"{query} {term}")
            expansions.append(f"{term} {query}")

        # Add modifiers
        for modifier in profile["modifiers"][:3]:  # Limit to top 3
            expansions.append(f"{query} {modifier}")

        # Remove duplicates and sort by relevance (simple length heuristic)
        unique_expansions = list(dict.fromkeys(expansions))
        unique_expansions.sort(key=lambda x: len(x.split()))

        return unique_expansions[:count]

    def generate_seo_keywords(
        self, query: str, intent_types: list[str] | None = None
    ) -> dict[str, list[str]]:
        """
        Generate SEO-focused keywords based on search intent

        Args:
            query: Base query
            intent_types: List of intent types to generate (default: all)

        Returns:
            Dictionary mapping intent types to keyword lists
        """
        if intent_types is None:
            intent_types = list(self.SEO_INTENT_PATTERNS.keys())

        seo_keywords = {}

        for intent in intent_types:
            if intent not in self.SEO_INTENT_PATTERNS:
                continue

            keywords = []
            for pattern in self.SEO_INTENT_PATTERNS[intent]:
                keyword = pattern.format(query=query)
                keywords.append(keyword)

            seo_keywords[intent] = keywords

        return seo_keywords

    def merge_autosuggest_sources(self, query: str, include_google: bool = True) -> list[str]:
        """
        Merge Bing and Google autosuggest results

        Args:
            query: Search query
            include_google: Whether to include Google suggestions

        Returns:
            List of merged suggestions
        """
        merged = []
        seen = set()

        # Get Bing autosuggest
        try:
            bing_suggestions = self.bing_client.autosuggest(query)
            for suggestion in bing_suggestions:
                if suggestion not in seen:
                    seen.add(suggestion)
                    merged.append(suggestion)
        except Exception as e:
            logger.warning(f"Bing autosuggest failed: {e}")

        # Get Google suggestions
        if include_google:
            try:
                google_suggestions = google_suggest(query)
                for suggestion in google_suggestions:
                    if suggestion not in seen:
                        seen.add(suggestion)
                        merged.append(suggestion)
            except Exception as e:
                logger.warning(f"Google suggest failed: {e}")

        return merged

    def enhance_suggestions_with_intelligence(
        self, suggestions: list[str], base_query: str, stack: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Enhance autosuggest results with EQ12 intelligence metadata

        Args:
            suggestions: Raw suggestion strings
            base_query: Original query
            stack: Detected stack (optional)

        Returns:
            List of enhanced suggestion dictionaries
        """
        enhanced_suggestions = []

        for suggestion in suggestions:
            # Detect stack for individual suggestion
            suggestion_stack, confidence = self.detect_query_stack(suggestion)

            # Use base stack if suggestion stack confidence is low
            if confidence < 0.3 and stack:
                suggestion_stack = stack
                confidence = 0.5  # Medium confidence from base query

            # Calculate suggestion quality metrics
            quality_metrics = self._calculate_suggestion_quality(suggestion, base_query)

            enhanced_suggestion = {
                "suggestion": suggestion,
                "base_query": base_query,
                "detected_stack": suggestion_stack,
                "confidence_score": confidence,
                "quality_metrics": quality_metrics,
                "seo_potential": self._estimate_seo_potential(suggestion),
                "search_intent": self._detect_search_intent(suggestion),
                "long_tail_score": self._calculate_long_tail_score(suggestion),
                # EQ12 integration fields
                "content_type": "autosuggest",
                "primary_category": "query_expansion",
                "secondary_category": suggestion_stack or "general",
                # Processing metadata
                "processing_timestamp": datetime.now(UTC).isoformat(),
                "relevance_score": confidence * quality_metrics.get("overall_quality", 0.5),
            }

            enhanced_suggestions.append(enhanced_suggestion)

        # Sort by relevance score
        enhanced_suggestions.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        return enhanced_suggestions

    def _calculate_suggestion_quality(self, suggestion: str, base_query: str) -> dict[str, float]:
        """Calculate quality metrics for a suggestion"""
        words = suggestion.split()
        base_words = base_query.split()

        # Length score (prefer moderate length)
        length_score = 1.0 - abs(len(words) - 4) / 10.0  # Optimal around 4 words
        length_score = max(0.1, length_score)

        # Relevance score (shared words with base query)
        shared_words = set(words) & set(base_words)
        relevance_score = len(shared_words) / max(len(base_words), 1)

        # Specificity score (more specific = higher value)
        specificity_score = min(1.0, len(words) / 6.0)

        # Commercial intent indicators
        commercial_terms = [
            "buy",
            "price",
            "deal",
            "cheap",
            "best",
            "review",
            "near me",
        ]
        commercial_score = sum(0.2 for term in commercial_terms if term in suggestion.lower())
        commercial_score = min(1.0, commercial_score)

        # Overall quality (weighted average)
        overall_quality = (
            length_score * 0.2
            + relevance_score * 0.4
            + specificity_score * 0.2
            + commercial_score * 0.2
        )

        return {
            "length_score": length_score,
            "relevance_score": relevance_score,
            "specificity_score": specificity_score,
            "commercial_score": commercial_score,
            "overall_quality": overall_quality,
        }

    def _estimate_seo_potential(self, suggestion: str) -> dict[str, float]:
        """Estimate SEO potential of a suggestion"""
        words = suggestion.split()

        # Long-tail potential (more words = higher long-tail potential)
        long_tail_potential = min(1.0, len(words) / 6.0)

        # Local SEO indicators
        local_terms = ["near me", "buffalo", "local", "in buffalo", "western ny"]
        local_potential = 1.0 if any(term in suggestion.lower() for term in local_terms) else 0.3

        # Commercial potential
        commercial_terms = ["buy", "price", "deal", "cheap", "best", "review"]
        commercial_potential = (
            0.8 if any(term in suggestion.lower() for term in commercial_terms) else 0.4
        )

        # Competition estimate (longer = less competitive)
        competition_estimate = 1.0 - min(0.8, len(words) / 10.0)

        return {
            "long_tail_potential": long_tail_potential,
            "local_potential": local_potential,
            "commercial_potential": commercial_potential,
            "competition_estimate": competition_estimate,
            "overall_seo_score": (long_tail_potential + local_potential + commercial_potential)
            / 3.0,
        }

    def _detect_search_intent(self, suggestion: str) -> str:
        """Detect search intent from suggestion text"""
        suggestion_lower = suggestion.lower()

        # Transactional intent
        if any(
            term in suggestion_lower
            for term in ["buy", "price", "cheap", "deal", "discount", "for sale"]
        ):
            return "transactional"

        # Local intent
        if any(term in suggestion_lower for term in ["near me", "local", "buffalo", "in buffalo"]):
            return "local"

        # Informational intent
        if any(
            term in suggestion_lower for term in ["what is", "how to", "guide", "tips", "tutorial"]
        ):
            return "informational"

        # Commercial investigation
        if any(term in suggestion_lower for term in ["review", "best", "vs", "compare", "top"]):
            return "commercial"

        return "navigational"

    def _calculate_long_tail_score(self, suggestion: str) -> float:
        """Calculate how "long-tail" a suggestion is"""
        words = len(suggestion.split())

        # 1-2 words = short-tail (0.1-0.3)
        # 3-4 words = medium-tail (0.4-0.6)
        # 5+ words = long-tail (0.7-1.0)

        if words <= 2:
            return 0.1 + (words - 1) * 0.2
        if words <= 4:
            return 0.4 + (words - 3) * 0.2
        return min(1.0, 0.7 + (words - 5) * 0.1)

    def comprehensive_query_expansion(
        self,
        query: str,
        stack: str | None = None,
        count: int = 20,
        include_seo: bool = True,
    ) -> dict[str, Any]:
        """
        Generate comprehensive query expansion with intelligence analysis

        Args:
            query: Base search query
            stack: Target stack (optional, will auto-detect)
            count: Total suggestions to generate
            include_seo: Whether to include SEO keyword generation

        Returns:
            Dictionary with expanded queries and analysis
        """
        start_time = time.time()

        # Auto-detect stack if not provided
        if not stack:
            stack, stack_confidence = self.detect_query_stack(query)
        else:
            stack_confidence = 1.0

        # Get base autosuggest results
        base_suggestions = self.merge_autosuggest_sources(query)

        # Generate stack-specific expansions
        stack_expansions = []
        if stack:
            stack_expansions = self.generate_stack_expansions(query, stack, count // 2)

        # Combine all suggestions
        all_suggestions = base_suggestions + stack_expansions

        # Remove duplicates while preserving order
        unique_suggestions = list(dict.fromkeys(all_suggestions))

        # Limit to requested count
        final_suggestions = unique_suggestions[:count]

        # Enhance with intelligence
        enhanced_suggestions = self.enhance_suggestions_with_intelligence(
            final_suggestions, query, stack
        )

        # Generate SEO keywords if requested
        seo_keywords = {}
        if include_seo:
            seo_keywords = self.generate_seo_keywords(query)

        # Generate analysis
        analysis = self._generate_expansion_analysis(enhanced_suggestions, query, stack)

        # Record performance metrics
        processing_time = (time.time() - start_time) * 1000
        if ENHANCED_DB_AVAILABLE:
            try:
                record_performance_metric(
                    "autosuggest_expansion_time",
                    processing_time,
                    stack=stack,
                    source="autosuggest_intelligence",
                    metadata={
                        "suggestions_generated": len(enhanced_suggestions),
                        "base_query": query,
                        "stack_detected": stack is not None,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to record performance metric: {e}")

        return {
            "base_query": query,
            "detected_stack": stack,
            "stack_confidence": stack_confidence,
            "suggestions": enhanced_suggestions,
            "seo_keywords": seo_keywords,
            "analysis": analysis,
            "metadata": {
                "total_suggestions": len(enhanced_suggestions),
                "base_autosuggest_count": len(base_suggestions),
                "stack_expansions_count": len(stack_expansions),
                "processing_time_ms": int(processing_time),
                "intelligence_used": True,
                "enhancement_source": "autosuggest_intelligence",
            },
        }

    def _generate_expansion_analysis(
        self, suggestions: list[dict], query: str, stack: str | None
    ) -> dict[str, Any]:
        """Generate analysis of query expansion results"""
        if not suggestions:
            return {"summary": "No suggestions generated"}

        analysis = {
            "total_suggestions": len(suggestions),
            "stack_distribution": {},
            "intent_distribution": {},
            "quality_stats": {
                "avg_quality": 0.0,
                "avg_seo_score": 0.0,
                "avg_long_tail": 0.0,
            },
            "top_commercial_suggestions": [],
            "top_long_tail_suggestions": [],
            "recommendations": [],
        }

        # Stack distribution
        for suggestion in suggestions:
            detected_stack = suggestion.get("detected_stack", "general")
            analysis["stack_distribution"][detected_stack] = (
                analysis["stack_distribution"].get(detected_stack, 0) + 1
            )

        # Intent distribution
        for suggestion in suggestions:
            intent = suggestion.get("search_intent", "unknown")
            analysis["intent_distribution"][intent] = (
                analysis["intent_distribution"].get(intent, 0) + 1
            )

        # Quality statistics
        quality_scores = [
            s.get("quality_metrics", {}).get("overall_quality", 0) for s in suggestions
        ]
        seo_scores = [s.get("seo_potential", {}).get("overall_seo_score", 0) for s in suggestions]
        long_tail_scores = [s.get("long_tail_score", 0) for s in suggestions]

        analysis["quality_stats"]["avg_quality"] = (
            sum(quality_scores) / len(quality_scores) if quality_scores else 0
        )
        analysis["quality_stats"]["avg_seo_score"] = (
            sum(seo_scores) / len(seo_scores) if seo_scores else 0
        )
        analysis["quality_stats"]["avg_long_tail"] = (
            sum(long_tail_scores) / len(long_tail_scores) if long_tail_scores else 0
        )

        # Top suggestions by category
        commercial_suggestions = [
            s for s in suggestions if s.get("search_intent") == "transactional"
        ]
        commercial_suggestions.sort(
            key=lambda x: x.get("quality_metrics", {}).get("commercial_score", 0),
            reverse=True,
        )
        analysis["top_commercial_suggestions"] = [
            s["suggestion"] for s in commercial_suggestions[:5]
        ]

        long_tail_suggestions = sorted(
            suggestions, key=lambda x: x.get("long_tail_score", 0), reverse=True
        )
        analysis["top_long_tail_suggestions"] = [s["suggestion"] for s in long_tail_suggestions[:5]]

        # Generate recommendations
        if analysis["quality_stats"]["avg_quality"] > 0.7:
            analysis["recommendations"].append(
                "High-quality suggestions generated - strong expansion potential"
            )

        if analysis["intent_distribution"].get("transactional", 0) > 5:
            analysis["recommendations"].append(
                "Strong commercial intent detected - good for conversion"
            )

        if analysis["quality_stats"]["avg_long_tail"] > 0.6:
            analysis["recommendations"].append(
                "Good long-tail potential - focus on specific targeting"
            )

        if stack and analysis["stack_distribution"].get(stack, 0) > len(suggestions) * 0.6:
            analysis["recommendations"].append(
                f"Strong {stack} stack alignment - highly relevant suggestions"
            )

        return analysis


# Integration functions for EQ12 system
def expand_query_for_stack(query: str, stack: str, count: int = 15) -> dict[str, Any]:
    """Convenience function for stack-specific query expansion"""
    intel = AutosuggestIntelligence()
    return intel.comprehensive_query_expansion(query, stack=stack, count=count)


def generate_seo_expansion(query: str, intent_types: list[str] | None = None) -> dict[str, Any]:
    """Convenience function for SEO-focused query expansion"""
    intel = AutosuggestIntelligence()
    result = intel.comprehensive_query_expansion(query, include_seo=True)

    if intent_types:
        # Filter SEO keywords by requested intents
        filtered_seo = {
            intent: keywords
            for intent, keywords in result["seo_keywords"].items()
            if intent in intent_types
        }
        result["seo_keywords"] = filtered_seo

    return result


# CLI interface
def main():
    """CLI interface for Autosuggest Intelligence module"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Autosuggest Intelligence Module")
    parser.add_argument("--query", required=True, help="Base search query")
    parser.add_argument(
        "--stack",
        choices=["betting", "travel", "cannabis", "finance", "fleet"],
        help="Target EQ12 stack",
    )
    parser.add_argument("--count", type=int, default=15, help="Number of suggestions to generate")
    parser.add_argument("--seo", action="store_true", help="Include SEO keyword generation")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    try:
        intel = AutosuggestIntelligence(verbose=args.verbose)

        results = intel.comprehensive_query_expansion(
            args.query, stack=args.stack, count=args.count, include_seo=args.seo
        )

        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            print("🔍 Autosuggest Intelligence Results")
            print(f"Base Query: {results['base_query']}")
            print(f"Detected Stack: {results['detected_stack'] or 'Auto-detect'}")
            print(f"Stack Confidence: {results['stack_confidence']:.2f}")
            print(f"Suggestions Generated: {len(results['suggestions'])}")
            print()

            for i, suggestion in enumerate(results["suggestions"][:10], 1):
                quality = suggestion.get("quality_metrics", {}).get("overall_quality", 0)
                intent = suggestion.get("search_intent", "unknown")
                long_tail = suggestion.get("long_tail_score", 0)

                print(f"{i:2d}. {suggestion['suggestion']}")
                print(
                    f"    Stack: {suggestion.get('detected_stack', 'general')} | Intent: {intent}"
                )
                print(f"    Quality: {quality:.2f} | Long-tail: {long_tail:.2f}")
                print()

            # Show SEO keywords if generated
            if args.seo and results.get("seo_keywords"):
                print("📈 SEO Keywords by Intent:")
                for intent, keywords in results["seo_keywords"].items():
                    print(f"  {intent.title()}:")
                    for keyword in keywords[:3]:
                        print(f"    • {keyword}")
                print()

            # Show analysis
            analysis = results.get("analysis", {})
            if analysis.get("recommendations"):
                print("💡 Recommendations:")
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
