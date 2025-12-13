#!/usr/bin/env python3
"""
EQ12 Intelligent Query Router
Advanced query analysis and routing system for directing searches to appropriate stack intelligence modules.

Author: EQ12 AI Assistant
Created: 2025-01-27
"""

import logging
import re
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("eq12_query_router")


@dataclass
class StackMatch:
    """Represents a potential stack match for a query"""

    stack: str
    confidence: float
    matched_keywords: list[str]
    context_indicators: list[str]
    priority_score: float
    reasoning: str


class EQ12QueryRouter:
    """
    Intelligent query routing system that analyzes queries and determines
    the most appropriate EQ12 stack for processing
    """

    # Enhanced keyword mapping with weights and context
    STACK_DEFINITIONS = {
        "betting": {
            "primary_keywords": {
                # Core betting terms (high weight)
                "odds": 3.0,
                "sportsbook": 3.0,
                "bet": 2.5,
                "betting": 3.0,
                "wager": 2.5,
                "moneyline": 3.0,
                "spread": 2.5,
                "over/under": 3.0,
                "parlay": 3.0,
                "prop bet": 3.0,
                "futures": 2.5,
                "live betting": 3.0,
                # Sports injury/roster (medium-high weight)
                "injury": 2.0,
                "roster": 2.0,
                "lineup": 2.5,
                "team news": 2.5,
                "player stats": 2.0,
                "game prediction": 2.5,
                "matchup": 2.0,
                # Sports leagues (medium weight)
                "nfl": 1.5,
                "nba": 1.5,
                "mlb": 1.5,
                "nhl": 1.5,
                "ncaa": 1.5,
                "soccer": 1.5,
                "mma": 2.0,
                "boxing": 2.0,
                "ufc": 2.0,
                # Betting platforms (high weight)
                "draftkings": 2.5,
                "fanduel": 2.5,
                "caesars": 2.5,
                "betmgm": 2.5,
            },
            "context_patterns": [
                r"tonight.*(game|match|fight)",
                r"(who|what).*(favored|favorite)",
                r"(pick|picks).*(today|tonight)",
                r"(line|lines).*(moved|movement)",
                r"(sharp|public).*(money|action)",
                r"(injury|out).*(report|update)",
            ],
            "negative_indicators": [
                "flight",
                "hotel",
                "dispensary",
                "stock",
                "car rental",
            ],
            "priority_domains": [
                "espn.com",
                "draftkings.com",
                "fanduel.com",
                "vegas.com",
            ],
        },
        "travel": {
            "primary_keywords": {
                # Core travel terms (high weight)
                "flight": 3.0,
                "hotel": 3.0,
                "airfare": 3.0,
                "booking": 2.5,
                "travel deal": 3.0,
                "vacation": 2.5,
                "airline": 2.5,
                "resort": 2.5,
                # Destinations and routing (medium-high weight)
                "buffalo to": 3.0,
                "buf to": 3.0,
                "destination": 2.0,
                "trip": 2.0,
                "fare": 2.5,
                "ticket": 2.0,
                "itinerary": 2.5,
                "airport": 2.0,
                # Travel platforms (high weight)
                "expedia": 2.5,
                "kayak": 2.5,
                "priceline": 2.5,
                "skyscanner": 2.5,
                "tripadvisor": 2.0,
                "booking.com": 2.5,
                "orbitz": 2.5,
                # Travel logistics (medium weight)
                "tsa": 1.5,
                "baggage": 1.5,
                "check-in": 1.5,
                "layover": 2.0,
            },
            "context_patterns": [
                r"(fly|flying).*(to|from)",
                r"(cheap|best).*(flight|fare)",
                r"(hotel|room).*(deal|discount)",
                r"(vacation|trip).*(package|deal)",
                r"(airport|terminal)",
                r"(round.?trip|one.?way)",
            ],
            "negative_indicators": ["betting", "odds", "dispensary", "stock", "casino"],
            "priority_domains": [
                "expedia.com",
                "kayak.com",
                "tripadvisor.com",
                "booking.com",
            ],
        },
        "cannabis": {
            "primary_keywords": {
                # Core cannabis terms (high weight)
                "dispensary": 3.0,
                "cannabis": 3.0,
                "marijuana": 3.0,
                "cbd": 2.5,
                "thc": 2.5,
                "weed": 2.0,
                "medical marijuana": 3.0,
                "recreational": 2.5,
                # Products and strains (medium-high weight)
                "strain": 2.5,
                "edibles": 2.5,
                "vape": 2.0,
                "concentrates": 2.5,
                "flower": 2.0,
                "budtender": 2.0,
                "cultivation": 2.0,
                "hemp": 1.5,
                "terpenes": 2.0,
                "indica": 2.0,
                "sativa": 2.0,
                "hybrid": 1.5,
                # Legal/regulatory (medium weight)
                "license": 1.5,
                "regulation": 1.5,
                "legalization": 2.0,
                "medical card": 2.5,
                "dispensary license": 2.5,
                # Buffalo-specific (high weight for local)
                "buffalo dispensary": 3.5,
                "ny cannabis": 3.0,
                "new york marijuana": 3.0,
            },
            "context_patterns": [
                r"(dispensary|cannabis).*(near|buffalo|ny)",
                r"(medical|recreational).*(marijuana|cannabis)",
                r"(buy|purchase).*(weed|cannabis|cbd)",
                r"(strain|product).*(review|effect)",
                r"(dosage|dose).*(cbd|thc|edible)",
                r"(legal|law).*(cannabis|marijuana)",
            ],
            "negative_indicators": ["flight", "betting", "stock", "car", "hotel"],
            "priority_domains": ["leafly.com", "weedmaps.com", "cannabis.net"],
        },
        "finance": {
            "primary_keywords": {
                # Core finance terms (high weight)
                "stock": 3.0,
                "trading": 3.0,
                "investment": 3.0,
                "market": 2.5,
                "crypto": 3.0,
                "bitcoin": 3.0,
                "portfolio": 2.5,
                "earnings": 2.5,
                # Financial instruments (medium-high weight)
                "dividend": 2.5,
                "ipo": 2.5,
                "options": 2.5,
                "futures": 2.0,
                "forex": 2.5,
                "etf": 2.5,
                "mutual fund": 2.5,
                "bond": 2.0,
                "commodity": 2.0,
                "reit": 2.0,
                # Market analysis (medium weight)
                "analysis": 1.5,
                "finance": 2.0,
                "economy": 2.0,
                "fed": 2.0,
                "interest rate": 2.5,
                "inflation": 2.0,
                "recession": 2.0,
                # Crypto specific (high weight)
                "ethereum": 3.0,
                "blockchain": 2.5,
                "defi": 2.5,
                "nft": 2.0,
            },
            "context_patterns": [
                r"(stock|share).*(price|buy|sell)",
                r"(crypto|bitcoin).*(price|chart)",
                r"(market|trading).*(analysis|strategy)",
                r"(investment|invest).*(advice|tip)",
                r"(portfolio|401k|ira)",
                r"(dividend|yield).*(stock|fund)",
            ],
            "negative_indicators": [
                "flight",
                "dispensary",
                "betting",
                "hotel",
                "car rental",
            ],
            "priority_domains": [
                "yahoo.com",
                "bloomberg.com",
                "marketwatch.com",
                "coinbase.com",
            ],
        },
        "fleet": {
            "primary_keywords": {
                # Core fleet/auto terms (high weight)
                "turo": 3.0,
                "car rental": 3.0,
                "vehicle": 2.5,
                "auto": 2.0,
                "truck": 2.0,
                "fleet": 3.0,
                "rental car": 3.0,
                # Auto services (medium-high weight)
                "insurance": 2.0,
                "maintenance": 2.5,
                "repair": 2.5,
                "recall": 2.5,
                "safety": 1.5,
                "automotive": 2.5,
                "dealership": 2.0,
                # Financial aspects (medium weight)
                "financing": 2.0,
                "lease": 2.5,
                "car loan": 2.5,
                "trade-in": 2.0,
                # Efficiency/tech (medium weight)
                "mpg": 2.0,
                "fuel efficiency": 2.5,
                "electric vehicle": 2.5,
                "hybrid": 2.0,
                "car market": 2.0,
                "used car": 2.0,
            },
            "context_patterns": [
                r"(rent|rental).*(car|vehicle)",
                r"(car|auto).*(insurance|loan)",
                r"(vehicle|car).*(maintenance|repair)",
                r"(mpg|fuel).*(economy|efficiency)",
                r"(electric|hybrid).*(car|vehicle)",
                r"(turo|zipcar|hertz)",
            ],
            "negative_indicators": [
                "flight",
                "dispensary",
                "betting",
                "stock",
                "hotel",
            ],
            "priority_domains": [
                "turo.com",
                "cars.com",
                "autotrader.com",
                "edmunds.com",
            ],
        },
    }

    # Geographic and temporal indicators
    LOCATION_INDICATORS = {
        "buffalo": ["buffalo", "buf", "716", "western ny", "wny", "erie county"],
        "new_york": ["ny", "new york", "nyc", "manhattan", "brooklyn", "queens"],
        "general": ["near me", "local", "nearby", "around here"],
    }

    TEMPORAL_INDICATORS = {
        "immediate": ["now", "today", "tonight", "asap", "urgent", "breaking"],
        "short_term": ["tomorrow", "this week", "weekend", "soon", "upcoming"],
        "long_term": ["next month", "planning", "future", "eventually"],
    }

    def __init__(self):
        """Initialize the query router with compiled patterns"""
        self.compiled_patterns = {}

        # Compile regex patterns for each stack
        for stack, config in self.STACK_DEFINITIONS.items():
            self.compiled_patterns[stack] = [
                re.compile(pattern, re.IGNORECASE) for pattern in config.get("context_patterns", [])
            ]

        logger.info(f"Query router initialized with {len(self.STACK_DEFINITIONS)} stacks")

    def analyze_query(self, query: str, context: dict | None = None) -> list[StackMatch]:
        """
        Analyze a query and return ranked stack matches

        Args:
            query: The search query to analyze
            context: Optional context (user history, preferences, etc.)

        Returns:
            List of StackMatch objects ranked by confidence
        """
        query_lower = query.lower()
        matches = []

        for stack, config in self.STACK_DEFINITIONS.items():
            match = self._analyze_stack_match(query, query_lower, stack, config, context)
            if match.confidence > 0.1:  # Only include reasonable matches
                matches.append(match)

        # Sort by confidence, then by priority score
        matches.sort(key=lambda x: (x.confidence, x.priority_score), reverse=True)

        return matches

    def _analyze_stack_match(
        self,
        original_query: str,
        query_lower: str,
        stack: str,
        config: dict,
        context: dict | None,
    ) -> StackMatch:
        """Analyze how well a query matches a specific stack"""

        matched_keywords = []
        keyword_score = 0.0
        context_indicators = []

        # Check primary keywords with weights
        primary_keywords = config.get("primary_keywords", {})
        for keyword, weight in primary_keywords.items():
            if keyword in query_lower:
                matched_keywords.append(keyword)
                keyword_score += weight

        # Check context patterns
        pattern_score = 0.0
        patterns = self.compiled_patterns.get(stack, [])
        for pattern in patterns:
            if pattern.search(query_lower):
                pattern_score += 1.0
                context_indicators.append(pattern.pattern)

        # Check for negative indicators (reduce score)
        negative_penalty = 0.0
        negative_indicators = config.get("negative_indicators", [])
        for neg_keyword in negative_indicators:
            if neg_keyword in query_lower:
                negative_penalty += 2.0  # Strong penalty for negative indicators

        # Calculate base confidence
        base_confidence = (keyword_score + pattern_score) - negative_penalty

        # Apply location boost
        location_boost = self._calculate_location_boost(query_lower, stack)

        # Apply temporal boost
        temporal_boost = self._calculate_temporal_boost(query_lower, stack)

        # Apply context boost if provided
        context_boost = self._calculate_context_boost(context, stack) if context else 0.0

        # Calculate final confidence (normalized to 0-1)
        raw_confidence = base_confidence + location_boost + temporal_boost + context_boost
        confidence = min(1.0, max(0.0, raw_confidence / 10.0))  # Normalize to 0-1

        # Calculate priority score
        priority_score = self._calculate_priority_score(stack, matched_keywords, context_indicators)

        # Generate reasoning
        reasoning = self._generate_reasoning(
            stack,
            matched_keywords,
            context_indicators,
            location_boost,
            temporal_boost,
            negative_penalty,
        )

        return StackMatch(
            stack=stack,
            confidence=confidence,
            matched_keywords=matched_keywords,
            context_indicators=context_indicators,
            priority_score=priority_score,
            reasoning=reasoning,
        )

    def _calculate_location_boost(self, query_lower: str, stack: str) -> float:
        """Calculate boost based on location indicators"""
        boost = 0.0

        # Buffalo-specific boost
        for buffalo_term in self.LOCATION_INDICATORS["buffalo"]:
            if buffalo_term in query_lower:
                if stack in ["cannabis", "travel", "fleet"]:
                    boost += 1.0  # Local services get boost
                elif stack == "betting":
                    boost += 0.5  # Sports betting gets moderate boost

        # General location boost
        for general_term in self.LOCATION_INDICATORS["general"]:
            if general_term in query_lower and stack in ["cannabis", "fleet"]:
                boost += 0.5  # Local services benefit from "near me" queries

        return boost

    def _calculate_temporal_boost(self, query_lower: str, stack: str) -> float:
        """Calculate boost based on temporal indicators"""
        boost = 0.0

        # Immediate temporal indicators
        for immediate_term in self.TEMPORAL_INDICATORS["immediate"]:
            if immediate_term in query_lower:
                if stack == "betting":
                    boost += 1.5  # Betting benefits from immediate queries
                elif stack == "travel":
                    boost += 0.5  # Travel can benefit but less so

        # Planning temporal indicators
        for long_term in self.TEMPORAL_INDICATORS["long_term"]:
            if long_term in query_lower and stack in ["travel", "finance"]:
                boost += 0.5  # Travel and finance benefit from planning queries

        return boost

    def _calculate_context_boost(self, context: dict, stack: str) -> float:
        """Calculate boost based on user context/history"""
        boost = 0.0

        if not context:
            return boost

        # User preferences
        preferences = context.get("preferences", {})
        if preferences.get("preferred_stacks") and stack in preferences["preferred_stacks"]:
            boost += 0.5

        # Recent search history
        recent_searches = context.get("recent_searches", [])
        recent_stack_counts = Counter(
            search.get("detected_stack") for search in recent_searches[-10:]
        )

        if recent_stack_counts.get(stack, 0) >= 3:
            boost += 0.3  # User has been searching this stack recently

        # Success history
        success_history = context.get("success_history", {})
        if success_history.get(stack, 0) > 0.8:
            boost += 0.2  # This stack has been successful for user

        return boost

    def _calculate_priority_score(
        self, stack: str, matched_keywords: list[str], context_indicators: list[str]
    ) -> float:
        """Calculate priority score for ranking equal confidence matches"""

        # Base priority by stack importance (subjective)
        base_priorities = {
            "betting": 0.9,  # High priority - time-sensitive
            "travel": 0.8,  # High priority - time-sensitive
            "cannabis": 0.7,  # Medium-high - local importance
            "finance": 0.6,  # Medium - important but not time-sensitive
            "fleet": 0.5,  # Medium - utility focused
        }

        base_score = base_priorities.get(stack, 0.5)

        # Boost for high-value keywords
        high_value_keywords = {
            "betting": ["odds", "sportsbook", "parlay", "live betting"],
            "travel": ["flight", "hotel", "buffalo to", "travel deal"],
            "cannabis": ["dispensary", "cannabis", "medical marijuana"],
            "finance": ["stock", "crypto", "bitcoin", "trading"],
            "fleet": ["turo", "car rental", "fleet"],
        }

        keyword_boost = 0.0
        high_value = high_value_keywords.get(stack, [])
        for keyword in matched_keywords:
            if keyword in high_value:
                keyword_boost += 0.1

        # Boost for context patterns
        context_boost = len(context_indicators) * 0.05

        return min(1.0, base_score + keyword_boost + context_boost)

    def _generate_reasoning(
        self,
        stack: str,
        matched_keywords: list[str],
        context_indicators: list[str],
        location_boost: float,
        temporal_boost: float,
        negative_penalty: float,
    ) -> str:
        """Generate human-readable reasoning for the match"""

        reasons = []

        if matched_keywords:
            reasons.append(
                f"Matched {len(matched_keywords)} keywords: {', '.join(matched_keywords[:3])}"
            )

        if context_indicators:
            reasons.append(f"Matched {len(context_indicators)} context patterns")

        if location_boost > 0:
            reasons.append("Location indicators present")

        if temporal_boost > 0:
            reasons.append("Temporal indicators favor this stack")

        if negative_penalty > 0:
            reasons.append(f"Negative indicators present (penalty: {negative_penalty})")

        if not reasons:
            reasons.append("Weak or no match indicators")

        return "; ".join(reasons)

    def route_query(
        self, query: str, context: dict | None = None, confidence_threshold: float = 0.3
    ) -> str | None:
        """
        Route a query to the most appropriate stack

        Args:
            query: The search query
            context: Optional user context
            confidence_threshold: Minimum confidence required for routing

        Returns:
            Stack name or None if no confident match
        """
        matches = self.analyze_query(query, context)

        if matches and matches[0].confidence >= confidence_threshold:
            return matches[0].stack

        return None

    def get_routing_explanation(self, query: str, context: dict | None = None) -> dict[str, Any]:
        """
        Get detailed explanation of routing decision

        Args:
            query: The search query
            context: Optional user context

        Returns:
            Dictionary with routing analysis and explanation
        """
        matches = self.analyze_query(query, context)

        explanation = {
            "query": query,
            "analysis_timestamp": datetime.now(UTC).isoformat(),
            "total_matches": len(matches),
            "recommended_stack": matches[0].stack if matches else None,
            "confidence": matches[0].confidence if matches else 0.0,
            "all_matches": [],
        }

        for match in matches:
            explanation["all_matches"].append(
                {
                    "stack": match.stack,
                    "confidence": round(match.confidence, 3),
                    "priority_score": round(match.priority_score, 3),
                    "matched_keywords": match.matched_keywords,
                    "context_indicators": match.context_indicators,
                    "reasoning": match.reasoning,
                }
            )

        return explanation

    def learn_from_feedback(
        self, query: str, detected_stack: str, actual_stack: str, feedback_score: float
    ):
        """
        Learn from user feedback to improve routing (placeholder for ML enhancement)

        Args:
            query: Original query
            detected_stack: What we detected
            actual_stack: What it actually was
            feedback_score: User satisfaction (0.0-1.0)
        """
        # This is a placeholder for future ML enhancement
        # Could update weights, add new keywords, adjust patterns

        feedback_data = {
            "query": query,
            "detected_stack": detected_stack,
            "actual_stack": actual_stack,
            "feedback_score": feedback_score,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # For now, just log for analysis
        logger.info(f"Routing feedback: {feedback_data}")

        # Future: Update keyword weights, pattern weights, etc.
        # based on feedback patterns

    def get_stack_statistics(self) -> dict[str, Any]:
        """Get statistics about the routing system"""
        stats = {"total_stacks": len(self.STACK_DEFINITIONS), "stacks": {}}

        for stack, config in self.STACK_DEFINITIONS.items():
            stats["stacks"][stack] = {
                "total_keywords": len(config.get("primary_keywords", {})),
                "context_patterns": len(config.get("context_patterns", [])),
                "negative_indicators": len(config.get("negative_indicators", [])),
                "priority_domains": len(config.get("priority_domains", [])),
            }

        return stats


# Convenience functions for integration
def route_query_simple(query: str) -> str | None:
    """Simple routing function for basic integration"""
    router = EQ12QueryRouter()
    return router.route_query(query)


def analyze_query_simple(query: str) -> dict[str, Any]:
    """Simple analysis function for basic integration"""
    router = EQ12QueryRouter()
    return router.get_routing_explanation(query)


# Testing and CLI interface
def main():
    """Test the query router with sample queries"""
    import argparse

    parser = argparse.ArgumentParser(description="Test EQ12 Query Router")
    parser.add_argument("query", help="Query to analyze")
    parser.add_argument("--explain", action="store_true", help="Show detailed explanation")
    parser.add_argument("--stats", action="store_true", help="Show router statistics")

    args = parser.parse_args()

    router = EQ12QueryRouter()

    if args.stats:
        print("📊 Query Router Statistics:")
        stats = router.get_stack_statistics()
        for stack, stack_stats in stats["stacks"].items():
            print(
                f"  {stack}: {stack_stats['total_keywords']} keywords, "
                f"{stack_stats['context_patterns']} patterns"
            )
        print()

    if args.explain:
        explanation = router.get_routing_explanation(args.query)
        print(f"🔍 Query Analysis: {explanation['query']}")
        print(f"📈 Recommended Stack: {explanation['recommended_stack']}")
        print(f"🎯 Confidence: {explanation['confidence']:.3f}")
        print("\nAll Matches:")
        for match in explanation["all_matches"]:
            print(f"  {match['stack']}: {match['confidence']:.3f} confidence")
            print(f"    Keywords: {', '.join(match['matched_keywords'])}")
            print(f"    Reasoning: {match['reasoning']}")
            print()
    else:
        # Simple routing
        result = router.route_query(args.query)
        if result:
            print(f"🎯 Route to: {result}")
        else:
            print("❓ No confident routing found")


if __name__ == "__main__":
    main()
