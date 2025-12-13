#!/usr/bin/env python3
"""
EQ12 Master Search Ecosystem Controller
Unified controller integrating meta-search, Bing intelligence, Swagbucks, news, autosuggest, and godstack2 components.

Author: EQ12 AI Assistant
Created: 2025-01-27
"""

import json
import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add paths for all integrations
BASE_DIR = Path(__file__).resolve().parent
GODSTACK2_DIR = Path(r"C:\EQ12\eq12_godstack2")
METASEARCH_DIR = BASE_DIR / "eq12_meta_search"

# System path setup
for path in [str(BASE_DIR), str(GODSTACK2_DIR), str(METASEARCH_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import all EQ12 intelligence modules
try:
    from autosuggest_intelligence import AutosuggestIntelligence
    from eq12_intelligent_router import EQ12IntelligentRouter
    from eq12_unified_search import EQ12UnifiedSearch
    from news_intelligence import NewsIntelligence
    from swagbucks_intelligence import SwagbucksIntelligence

    CORE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Core modules not available: {e}")
    CORE_MODULES_AVAILABLE = False

# Import enhanced database
try:
    from enhanced_db import (
        cache_stack_analysis,
        create_tables,
        get_cached_analysis,
        record_performance_metric,
        upsert_enhanced_results,
    )

    ENHANCED_DB_AVAILABLE = True
except ImportError:
    ENHANCED_DB_AVAILABLE = False

# Import automation bridge
try:
    from eq12_automation_bridge import EQ12AutomationBridge

    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False

logger = logging.getLogger("eq12_ecosystem")


class EQ12MasterController:
    """
    Master controller for the complete EQ12 search ecosystem
    """

    # Supported search modes
    SEARCH_MODES = {
        "unified": "Complete unified search across all sources",
        "intelligence": "Intelligence-only search with stack routing",
        "news": "News-focused search with sentiment analysis",
        "offers": "Swagbucks offers with stack categorization",
        "expansion": "Query expansion and autosuggest",
        "automation": "Integration with EQ12 automation systems",
    }

    # Stack priorities for different query types
    STACK_ROUTING_PRIORITIES = {
        "sports": ["betting", "news", "intelligence"],
        "betting": ["betting", "news", "offers", "intelligence"],
        "travel": ["travel", "offers", "news", "intelligence"],
        "cannabis": ["cannabis", "news", "offers", "intelligence"],
        "finance": ["finance", "news", "intelligence", "offers"],
        "auto": ["fleet", "news", "offers", "intelligence"],
        "general": ["intelligence", "news", "offers", "expansion"],
    }

    def __init__(self, verbose: bool = False, enable_caching: bool = True):
        """Initialize EQ12 Master Controller"""
        self.verbose = verbose
        self.enable_caching = enable_caching
        self.setup_logging()

        if not CORE_MODULES_AVAILABLE:
            raise ValueError("Core EQ12 modules not available - check installation")

        # Initialize all intelligence modules
        self.unified_search = EQ12UnifiedSearch(verbose=verbose)
        self.intelligent_router = EQ12IntelligentRouter(verbose=verbose)
        self.swagbucks_intel = SwagbucksIntelligence(verbose=verbose)
        self.news_intel = NewsIntelligence(verbose=verbose)
        self.autosuggest_intel = AutosuggestIntelligence(verbose=verbose)

        # Initialize automation bridge if available
        self.automation_bridge = None
        if AUTOMATION_AVAILABLE:
            try:
                self.automation_bridge = EQ12AutomationBridge(verbose=verbose)
            except Exception as e:
                logger.warning(f"Automation bridge initialization failed: {e}")

        # Thread pool for parallel operations
        self.executor = ThreadPoolExecutor(max_workers=8)

        # Initialize database if available
        if ENHANCED_DB_AVAILABLE and self.enable_caching:
            try:
                create_tables()
            except Exception as e:
                logger.warning(f"Database initialization failed: {e}")

    def setup_logging(self):
        """Setup EQ12-standard logging"""
        log_level = logging.INFO if self.verbose else logging.WARNING
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def detect_query_type(self, query: str) -> tuple[str, str, float]:
        """
        Detect query type and optimal search strategy

        Args:
            query: Search query

        Returns:
            Tuple of (query_type, recommended_stack, confidence)
        """
        query_lower = query.lower()

        # Sports/Betting detection
        sports_terms = [
            "nfl",
            "nba",
            "mlb",
            "nhl",
            "football",
            "basketball",
            "baseball",
            "hockey",
            "odds",
            "betting",
            "pick",
            "prediction",
            "injury",
            "lineup",
            "roster",
        ]
        if any(term in query_lower for term in sports_terms):
            return "sports", "betting", 0.9

        # Travel detection
        travel_terms = [
            "flight",
            "hotel",
            "travel",
            "vacation",
            "trip",
            "booking",
            "airline",
            "airport",
            "destination",
            "buffalo",
        ]
        if any(term in query_lower for term in travel_terms):
            return "travel", "travel", 0.8

        # Cannabis detection
        cannabis_terms = [
            "cannabis",
            "marijuana",
            "weed",
            "dispensary",
            "thc",
            "cbd",
            "strain",
        ]
        if any(term in query_lower for term in cannabis_terms):
            return "cannabis", "cannabis", 0.9

        # Finance detection
        finance_terms = [
            "stock",
            "crypto",
            "bitcoin",
            "investment",
            "trading",
            "price",
            "market",
            "earnings",
            "dividend",
            "ipo",
        ]
        if any(term in query_lower for term in finance_terms):
            return "finance", "finance", 0.8

        # Auto/Fleet detection
        auto_terms = [
            "car",
            "auto",
            "vehicle",
            "truck",
            "suv",
            "dealer",
            "lease",
            "buy car",
        ]
        if any(term in query_lower for term in auto_terms):
            return "auto", "fleet", 0.8

        return "general", "intelligence", 0.5

    def comprehensive_search(
        self,
        query: str,
        mode: str = "unified",
        stack: str | None = None,
        count: int = 20,
        include_news: bool = True,
        include_offers: bool = True,
        include_expansion: bool = True,
        time_window_hours: int = 24,
    ) -> dict[str, Any]:
        """
        Perform comprehensive search across all EQ12 systems

        Args:
            query: Search query
            mode: Search mode (unified, intelligence, news, offers, expansion, automation)
            stack: Target stack (auto-detected if None)
            count: Number of results per source
            include_news: Include news intelligence
            include_offers: Include Swagbucks offers
            include_expansion: Include query expansion
            time_window_hours: Time window for news (hours)

        Returns:
            Comprehensive search results dictionary
        """
        start_time = time.time()

        # Auto-detect stack and query type if not provided
        if not stack:
            query_type, detected_stack, confidence = self.detect_query_type(query)
        else:
            query_type = "manual"
            detected_stack = stack
            confidence = 1.0

        logger.info(
            f"Starting comprehensive search: query='{query}', mode='{mode}', stack='{detected_stack}'"
        )

        # Initialize result structure
        results = {
            "query": query,
            "mode": mode,
            "detected_stack": detected_stack,
            "stack_confidence": confidence,
            "query_type": query_type,
            # Results from each system
            "unified_results": [],
            "news_results": [],
            "offers_results": [],
            "expansion_results": {},
            "automation_results": {},
            # Aggregated analysis
            "consolidated_analysis": {},
            "recommendations": [],
            # Metadata
            "metadata": {
                "search_start_time": datetime.now(UTC).isoformat(),
                "processing_time_ms": 0,
                "sources_queried": [],
                "total_results": 0,
            },
        }

        # Execute searches in parallel based on mode
        futures = {}

        if mode in ["unified", "intelligence"]:
            # Core unified search
            futures["unified"] = self.executor.submit(
                self._execute_unified_search, query, detected_stack, count
            )
            results["metadata"]["sources_queried"].append("unified_search")

        if mode in ["unified", "news"] and include_news:
            # News intelligence search
            futures["news"] = self.executor.submit(
                self._execute_news_search,
                query,
                detected_stack,
                count,
                time_window_hours,
            )
            results["metadata"]["sources_queried"].append("news_intelligence")

        if mode in ["unified", "offers"] and include_offers:
            # Swagbucks offers search
            futures["offers"] = self.executor.submit(
                self._execute_offers_search, query, detected_stack, count
            )
            results["metadata"]["sources_queried"].append("swagbucks_offers")

        if mode in ["unified", "expansion"] and include_expansion:
            # Query expansion and autosuggest
            futures["expansion"] = self.executor.submit(
                self._execute_expansion_search, query, detected_stack, count
            )
            results["metadata"]["sources_queried"].append("autosuggest_expansion")

        if mode in ["unified", "automation"] and self.automation_bridge:
            # Automation system integration
            futures["automation"] = self.executor.submit(
                self._execute_automation_search, query, detected_stack
            )
            results["metadata"]["sources_queried"].append("automation_bridge")

        # Collect results as they complete
        for future_name, future in futures.items():
            try:
                result = future.result(timeout=30)  # 30 second timeout per source

                if future_name == "unified":
                    results["unified_results"] = result.get("results", [])
                elif future_name == "news":
                    results["news_results"] = result.get("results", [])
                elif future_name == "offers":
                    results["offers_results"] = result.get("results", [])
                elif future_name == "expansion":
                    results["expansion_results"] = result
                elif future_name == "automation":
                    results["automation_results"] = result

            except Exception as e:
                logger.error(f"{future_name} search failed: {e}")
                results["metadata"][f"{future_name}_error"] = str(e)

        # Generate consolidated analysis
        results["consolidated_analysis"] = self._generate_consolidated_analysis(results)

        # Generate actionable recommendations
        results["recommendations"] = self._generate_recommendations(results, detected_stack)

        # Update metadata
        processing_time = (time.time() - start_time) * 1000
        results["metadata"]["processing_time_ms"] = int(processing_time)
        results["metadata"]["total_results"] = (
            len(results["unified_results"])
            + len(results["news_results"])
            + len(results["offers_results"])
        )

        # Record performance metrics
        if ENHANCED_DB_AVAILABLE and self.enable_caching:
            try:
                record_performance_metric(
                    "comprehensive_search_time",
                    processing_time,
                    stack=detected_stack,
                    source="master_controller",
                    metadata={
                        "mode": mode,
                        "sources_count": len(results["metadata"]["sources_queried"]),
                        "total_results": results["metadata"]["total_results"],
                        "query": query,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to record performance metric: {e}")

        return results

    def _execute_unified_search(self, query: str, stack: str | None, count: int) -> dict[str, Any]:
        """Execute unified search with intelligence routing"""
        try:
            return self.unified_search.search_unified(query, count=count)
        except Exception as e:
            logger.error(f"Unified search failed: {e}")
            return {"results": [], "error": str(e)}

    def _execute_news_search(
        self, query: str, stack: str | None, count: int, hours: int
    ) -> dict[str, Any]:
        """Execute news intelligence search"""
        try:
            return self.news_intel.aggregate_news_with_analysis(
                query, stack=stack, count=count, hours=hours
            )
        except Exception as e:
            logger.error(f"News search failed: {e}")
            return {"results": [], "error": str(e)}

    def _execute_offers_search(self, query: str, stack: str | None, count: int) -> dict[str, Any]:
        """Execute Swagbucks offers search"""
        try:
            return self.swagbucks_intel.analyze_offers_for_query(query, stack=stack, limit=count)
        except Exception as e:
            logger.error(f"Offers search failed: {e}")
            return {"results": [], "error": str(e)}

    def _execute_expansion_search(
        self, query: str, stack: str | None, count: int
    ) -> dict[str, Any]:
        """Execute query expansion and autosuggest"""
        try:
            return self.autosuggest_intel.comprehensive_query_expansion(
                query, stack=stack, count=count
            )
        except Exception as e:
            logger.error(f"Expansion search failed: {e}")
            return {"suggestions": [], "error": str(e)}

    def _execute_automation_search(self, query: str, stack: str | None) -> dict[str, Any]:
        """Execute automation system integration"""
        try:
            if not self.automation_bridge:
                return {
                    "integrations": [],
                    "message": "Automation bridge not available",
                }

            return self.automation_bridge.search_for_automation(query, stack=stack)
        except Exception as e:
            logger.error(f"Automation search failed: {e}")
            return {"integrations": [], "error": str(e)}

    def _generate_consolidated_analysis(self, results: dict[str, Any]) -> dict[str, Any]:
        """Generate consolidated analysis across all search results"""
        analysis = {
            "total_sources": len(results["metadata"]["sources_queried"]),
            "unified_count": len(results["unified_results"]),
            "news_count": len(results["news_results"]),
            "offers_count": len(results["offers_results"]),
            "expansion_count": len(results["expansion_results"].get("suggestions", [])),
            "quality_distribution": {"high": 0, "medium": 0, "low": 0},
            "stack_confidence_avg": 0.0,
            "urgency_distribution": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "normal": 0,
            },
            "content_types": [],
            "top_sources": [],
            "key_themes": [],
        }

        # Analyze unified results
        for result in results["unified_results"]:
            confidence = result.get("confidence_score", 0)
            if confidence >= 0.7:
                analysis["quality_distribution"]["high"] += 1
            elif confidence >= 0.4:
                analysis["quality_distribution"]["medium"] += 1
            else:
                analysis["quality_distribution"]["low"] += 1

        # Analyze news results
        urgency_counts = {"critical": 0, "high": 0, "medium": 0, "normal": 0}
        for result in results["news_results"]:
            urgency = result.get("time_sensitivity", "normal")
            urgency_counts[urgency] += 1

        analysis["urgency_distribution"] = urgency_counts

        # Calculate averages
        all_confidences = []
        for result in results["unified_results"] + results["news_results"]:
            confidence = result.get("confidence_score", 0)
            if confidence > 0:
                all_confidences.append(confidence)

        if all_confidences:
            analysis["stack_confidence_avg"] = sum(all_confidences) / len(all_confidences)

        # Extract content types and sources
        content_types = set()
        sources = []

        for result in results["unified_results"] + results["news_results"]:
            content_types.add(result.get("content_type", "unknown"))
            source = result.get("source", "unknown")
            if source != "unknown":
                sources.append(source)

        analysis["content_types"] = list(content_types)

        # Count sources
        from collections import Counter

        source_counts = Counter(sources)
        analysis["top_sources"] = [source for source, count in source_counts.most_common(5)]

        return analysis

    def _generate_recommendations(self, results: dict[str, Any], stack: str | None) -> list[str]:
        """Generate actionable recommendations based on search results"""
        recommendations = []

        analysis = results["consolidated_analysis"]
        total_results = results["metadata"]["total_results"]

        # Result volume recommendations
        if total_results > 50:
            recommendations.append(
                "High result volume - consider refining query for better targeting"
            )
        elif total_results < 5:
            recommendations.append(
                "Low result volume - try broader search terms or different stacks"
            )

        # Quality recommendations
        high_quality_pct = analysis["quality_distribution"]["high"] / max(1, total_results)
        if high_quality_pct > 0.7:
            recommendations.append("Excellent result quality - high confidence in recommendations")
        elif high_quality_pct < 0.3:
            recommendations.append("Mixed result quality - verify sources and cross-reference")

        # Stack-specific recommendations
        if stack == "betting":
            news_count = analysis["news_count"]
            if news_count > 5:
                recommendations.append(
                    "Strong news coverage - check for injury/lineup updates affecting odds"
                )
            if analysis["urgency_distribution"]["critical"] > 0:
                recommendations.append(
                    "⚠️ Critical news detected - immediate attention required for betting decisions"
                )

        elif stack == "travel":
            offers_count = analysis["offers_count"]
            if offers_count > 3:
                recommendations.append(
                    "Travel offers available - check Swagbucks for cashback opportunities"
                )
            if analysis["urgency_distribution"]["high"] > 0:
                recommendations.append("⏰ Time-sensitive travel deals detected - act quickly")

        elif stack in ["cannabis", "finance", "fleet"]:
            news_count = analysis["news_count"]
            if news_count > 3:
                recommendations.append(
                    f"Active {stack} news - monitor for regulatory or market changes"
                )

        # Expansion recommendations
        expansion_results = results["expansion_results"]
        if expansion_results.get("analysis", {}).get("avg_long_tail", 0) > 0.6:
            recommendations.append("Good long-tail query potential - consider SEO optimization")

        # Automation recommendations
        if results["automation_results"].get("integrations"):
            recommendations.append(
                "EQ12 automation opportunities detected - consider workflow integration"
            )

        # Source diversity recommendations
        if len(analysis["top_sources"]) < 3:
            recommendations.append("Limited source diversity - consider expanding search scope")

        return recommendations

    def quick_stack_search(self, query: str, stack: str, mode: str = "focused") -> dict[str, Any]:
        """
        Optimized search focused on a specific stack

        Args:
            query: Search query
            stack: Target stack
            mode: Search focus (focused, comprehensive, news-only, offers-only)

        Returns:
            Stack-focused search results
        """
        if mode == "focused":
            # Focused search with reduced result sets
            return self.comprehensive_search(
                query,
                mode="intelligence",
                stack=stack,
                count=10,
                include_news=True,
                include_offers=True,
                include_expansion=False,
            )
        if mode == "news-only":
            return self.comprehensive_search(
                query,
                mode="news",
                stack=stack,
                count=15,
                include_news=True,
                include_offers=False,
                include_expansion=False,
            )
        if mode == "offers-only":
            return self.comprehensive_search(
                query,
                mode="offers",
                stack=stack,
                count=10,
                include_news=False,
                include_offers=True,
                include_expansion=False,
            )
        # comprehensive
        return self.comprehensive_search(
            query,
            mode="unified",
            stack=stack,
            count=20,
            include_news=True,
            include_offers=True,
            include_expansion=True,
        )

    def multi_query_analysis(self, queries: list[str], stack: str | None = None) -> dict[str, Any]:
        """
        Analyze multiple related queries for comprehensive insights

        Args:
            queries: List of search queries
            stack: Target stack (auto-detect if None)

        Returns:
            Multi-query analysis results
        """
        start_time = time.time()

        # Execute searches for all queries
        query_results = {}
        futures = {}

        for query in queries:
            futures[query] = self.executor.submit(
                self.comprehensive_search,
                query,
                mode="intelligence",
                stack=stack,
                count=10,
                include_news=True,
                include_offers=False,
                include_expansion=False,
            )

        # Collect results
        for query, future in futures.items():
            try:
                query_results[query] = future.result(timeout=45)
            except Exception as e:
                logger.error(f"Multi-query search failed for '{query}': {e}")
                query_results[query] = {"error": str(e)}

        # Generate cross-query analysis
        analysis = self._analyze_multi_query_results(query_results, stack)

        # Update timing
        processing_time = (time.time() - start_time) * 1000
        analysis["metadata"]["processing_time_ms"] = int(processing_time)
        analysis["metadata"]["queries_processed"] = len(queries)

        return analysis

    def _analyze_multi_query_results(
        self, query_results: dict[str, dict], target_stack: str | None
    ) -> dict[str, Any]:
        """Analyze results across multiple queries for patterns and insights"""
        analysis = {
            "queries": list(query_results.keys()),
            "target_stack": target_stack,
            "cross_query_patterns": {},
            "sentiment_trends": {},
            "source_authority": {},
            "recommendations": [],
            "metadata": {},
        }

        # Analyze patterns across queries
        all_sources = []
        all_sentiments = []
        stack_distributions = {}

        for _query, result in query_results.items():
            if "error" in result:
                continue

            # Extract sources
            for res in result.get("unified_results", []) + result.get("news_results", []):
                source = res.get("source", "unknown")
                all_sources.append(source)

                # Sentiment analysis
                sentiment = res.get("sentiment_analysis", {}).get("overall_sentiment", "neutral")
                all_sentiments.append(sentiment)

            # Stack distribution
            detected_stack = result.get("detected_stack")
            if detected_stack:
                stack_distributions[detected_stack] = stack_distributions.get(detected_stack, 0) + 1

        # Source authority analysis
        from collections import Counter

        source_counts = Counter(all_sources)
        analysis["source_authority"] = {
            "top_sources": source_counts.most_common(5),
            "source_diversity": len(set(all_sources)),
            "total_sources": len(all_sources),
        }

        # Sentiment trends
        sentiment_counts = Counter(all_sentiments)
        analysis["sentiment_trends"] = dict(sentiment_counts)

        # Cross-query patterns
        analysis["cross_query_patterns"] = {
            "stack_distribution": stack_distributions,
            "dominant_stack": (
                max(stack_distributions.keys(), key=stack_distributions.get)
                if stack_distributions
                else None
            ),
            "pattern_confidence": (
                max(stack_distributions.values()) / len(query_results) if stack_distributions else 0
            ),
        }

        # Generate multi-query recommendations
        if analysis["cross_query_patterns"]["pattern_confidence"] > 0.7:
            dominant = analysis["cross_query_patterns"]["dominant_stack"]
            analysis["recommendations"].append(
                f"Strong {dominant} pattern detected across queries - focus search strategy"
            )

        if analysis["sentiment_trends"].get("negative", 0) > analysis["sentiment_trends"].get(
            "positive", 0
        ):
            analysis["recommendations"].append(
                "Negative sentiment trend - monitor risks and develop mitigation strategies"
            )

        if analysis["source_authority"]["source_diversity"] > 10:
            analysis["recommendations"].append("High source diversity - good information coverage")

        return analysis

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive status of all EQ12 ecosystem components"""
        status = {
            "timestamp": datetime.now(UTC).isoformat(),
            "components": {},
            "overall_health": "unknown",
            "capabilities": list(self.SEARCH_MODES.keys()),
            "database_status": "unknown",
            "automation_status": "unknown",
        }

        # Test each component
        test_query = "test query"

        # Unified search
        try:
            self.unified_search.search_unified(test_query, count=1)
            status["components"]["unified_search"] = "healthy"
        except Exception as e:
            status["components"]["unified_search"] = f"error: {e}"

        # News intelligence
        try:
            self.news_intel.aggregate_news_with_analysis(test_query, count=1, hours=1)
            status["components"]["news_intelligence"] = "healthy"
        except Exception as e:
            status["components"]["news_intelligence"] = f"error: {e}"

        # Swagbucks intelligence
        try:
            self.swagbucks_intel.analyze_offers_for_query(test_query, limit=1)
            status["components"]["swagbucks_intelligence"] = "healthy"
        except Exception as e:
            status["components"]["swagbucks_intelligence"] = f"error: {e}"

        # Autosuggest intelligence
        try:
            self.autosuggest_intel.comprehensive_query_expansion(test_query, count=1)
            status["components"]["autosuggest_intelligence"] = "healthy"
        except Exception as e:
            status["components"]["autosuggest_intelligence"] = f"error: {e}"

        # Database status
        if ENHANCED_DB_AVAILABLE:
            try:
                record_performance_metric(
                    "health_check", 1.0, stack="system", source="master_controller"
                )
                status["database_status"] = "healthy"
            except Exception as e:
                status["database_status"] = f"error: {e}"
        else:
            status["database_status"] = "not_available"

        # Automation status
        if self.automation_bridge:
            try:
                self.automation_bridge.search_for_automation(test_query, stack="general")
                status["automation_status"] = "healthy"
            except Exception as e:
                status["automation_status"] = f"error: {e}"
        else:
            status["automation_status"] = "not_available"

        # Determine overall health
        healthy_count = sum(
            1 for comp_status in status["components"].values() if comp_status == "healthy"
        )
        total_count = len(status["components"])

        if healthy_count == total_count:
            status["overall_health"] = "excellent"
        elif healthy_count >= total_count * 0.8:
            status["overall_health"] = "good"
        elif healthy_count >= total_count * 0.5:
            status["overall_health"] = "degraded"
        else:
            status["overall_health"] = "critical"

        return status


# Convenience functions for common operations
def unified_eq12_search(query: str, stack: str | None = None, count: int = 20) -> dict[str, Any]:
    """Convenience function for unified EQ12 search"""
    controller = EQ12MasterController()
    return controller.comprehensive_search(query, mode="unified", stack=stack, count=count)


def quick_news_search(query: str, stack: str | None = None, hours: int = 24) -> dict[str, Any]:
    """Convenience function for news-focused search"""
    controller = EQ12MasterController()
    return controller.comprehensive_search(
        query,
        mode="news",
        stack=stack,
        include_news=True,
        include_offers=False,
        include_expansion=False,
        time_window_hours=hours,
    )


def stack_intelligence_search(query: str, stack: str) -> dict[str, Any]:
    """Convenience function for stack-specific intelligence search"""
    controller = EQ12MasterController()
    return controller.quick_stack_search(query, stack, mode="focused")


# CLI interface
def main():
    """CLI interface for EQ12 Master Controller"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Master Search Ecosystem Controller")
    parser.add_argument("--query", help="Search query")
    parser.add_argument(
        "--mode",
        choices=list(EQ12MasterController.SEARCH_MODES.keys()),
        default="unified",
        help="Search mode",
    )
    parser.add_argument(
        "--stack",
        choices=["betting", "travel", "cannabis", "finance", "fleet"],
        help="Target EQ12 stack",
    )
    parser.add_argument("--count", type=int, default=15, help="Number of results per source")
    parser.add_argument("--hours", type=int, default=24, help="News time window (hours)")
    parser.add_argument("--multi-query", nargs="+", help="Multiple queries for cross-analysis")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    try:
        controller = EQ12MasterController(verbose=args.verbose)

        if args.status:
            # System status check
            status = controller.get_system_status()
            if args.json:
                print(json.dumps(status, indent=2, default=str))
            else:
                print("🔧 EQ12 Ecosystem Status")
                print(f"Overall Health: {status['overall_health'].upper()}")
                print(f"Timestamp: {status['timestamp']}")
                print()
                print("Component Status:")
                for component, comp_status in status["components"].items():
                    emoji = "✅" if comp_status == "healthy" else "❌"
                    print(f"  {emoji} {component}: {comp_status}")
                print()
                print(f"Database: {status['database_status']}")
                print(f"Automation: {status['automation_status']}")
            return 0

        if args.multi_query:
            # Multi-query analysis
            results = controller.multi_query_analysis(args.multi_query, stack=args.stack)
        else:
            # Single query search
            if not args.query:
                print("❌ Error: --query required (or use --multi-query or --status)")
                return 1

            results = controller.comprehensive_search(
                args.query,
                mode=args.mode,
                stack=args.stack,
                count=args.count,
                time_window_hours=args.hours,
            )

        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            # Formatted output
            if args.multi_query:
                print("🔍 Multi-Query Analysis Results")
                print(f"Queries: {', '.join(results['queries'])}")
                print(f"Target Stack: {results['target_stack'] or 'Auto-detect'}")
                print(f"Processing Time: {results['metadata']['processing_time_ms']}ms")
                print()

                patterns = results.get("cross_query_patterns", {})
                if patterns.get("dominant_stack"):
                    print(
                        f"📊 Dominant Stack: {patterns['dominant_stack']} ({patterns['pattern_confidence']:.2f} confidence)"
                    )

                if results.get("recommendations"):
                    print("\n💡 Recommendations:")
                    for rec in results["recommendations"]:
                        print(f"  • {rec}")
            else:
                print("🔍 EQ12 Ecosystem Search Results")
                print(f"Query: {results['query']}")
                print(f"Mode: {results['mode']}")
                print(f"Detected Stack: {results['detected_stack'] or 'General'}")
                print(f"Processing Time: {results['metadata']['processing_time_ms']}ms")
                print(f"Sources Queried: {', '.join(results['metadata']['sources_queried'])}")
                print(f"Total Results: {results['metadata']['total_results']}")
                print()

                # Show sample results from each source
                if results["unified_results"]:
                    print(f"📋 Unified Search Results ({len(results['unified_results'])}):")
                    for i, result in enumerate(results["unified_results"][:3], 1):
                        confidence = result.get("confidence_score", 0)
                        stack = result.get("detected_stack", "general")
                        print(
                            f"  {i}. {result.get('title', 'No title')} (stack: {stack}, confidence: {confidence:.2f})"
                        )
                    print()

                if results["news_results"]:
                    print(f"📰 News Results ({len(results['news_results'])}):")
                    for i, result in enumerate(results["news_results"][:3], 1):
                        urgency = result.get("time_sensitivity", "normal")
                        sentiment = result.get("sentiment_analysis", {}).get(
                            "overall_sentiment", "neutral"
                        )
                        print(
                            f"  {i}. {result.get('title', 'No title')} (urgency: {urgency}, sentiment: {sentiment})"
                        )
                    print()

                if results["offers_results"]:
                    print(f"💰 Offers Results ({len(results['offers_results'])}):")
                    for i, result in enumerate(results["offers_results"][:3], 1):
                        stack = result.get("detected_stack", "general")
                        quality = result.get("offer_quality", {}).get("overall_score", 0)
                        print(
                            f"  {i}. {result.get('title', 'No title')} (stack: {stack}, quality: {quality:.2f})"
                        )
                    print()

                # Show recommendations
                if results.get("recommendations"):
                    print("💡 Recommendations:")
                    for rec in results["recommendations"]:
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
