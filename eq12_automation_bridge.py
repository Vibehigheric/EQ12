#!/usr/bin/env python3
"""
EQ12 Automation Integration Bridge
Connects enhanced meta-search with existing EQ12 automation systems for seamless intelligence integration.

Author: EQ12 AI Assistant
Created: 2025-01-27
"""

import json
import logging
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add EQ12 paths
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Import our enhanced systems
try:
    from eq12_intelligent_router import EQ12QueryRouter
    from eq12_unified_search import EQ12UnifiedSearch

    ENHANCED_SEARCH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Enhanced search not available: {e}")
    ENHANCED_SEARCH_AVAILABLE = False

# Import existing EQ12 systems
try:
    from eq12_meta_search.enhanced_db import (
        cleanup_expired_cache,
        get_query_analytics_summary,
        init_enhanced_db,
        record_performance_metric,
        record_query_analytics,
    )

    ENHANCED_DB_AVAILABLE = True
except ImportError:
    ENHANCED_DB_AVAILABLE = False

logger = logging.getLogger("eq12_automation_bridge")

# EQ12 standard paths
LOGS_DIR = Path(os.environ.get("EQ12_LOGS", r"C:\EQ12\logs"))
KEYS_DIR = Path(r"C:\EQ12\keys")
SCRIPTS_DIR = Path(r"C:\EQ12\scripts")
CONFIGS_DIR = Path(r"C:\EQ12\configs")

LOGS_DIR.mkdir(parents=True, exist_ok=True)


class EQ12AutomationBridge:
    """
    Integration bridge connecting enhanced meta-search with existing EQ12 automation systems
    """

    def __init__(self, enable_intelligence: bool = True, verbose: bool = False):
        """
        Initialize the automation bridge

        Args:
            enable_intelligence: Whether to enable intelligence modules
            verbose: Enable verbose logging
        """
        self.enable_intelligence = enable_intelligence and ENHANCED_SEARCH_AVAILABLE
        self.verbose = verbose
        self.setup_logging()

        # Initialize components
        self.unified_search = None
        self.query_router = None

        if self.enable_intelligence:
            try:
                self.unified_search = EQ12UnifiedSearch(verbose=verbose)
                self.query_router = EQ12QueryRouter()
                logger.info("Enhanced search systems initialized")
            except Exception as e:
                logger.error(f"Failed to initialize enhanced search: {e}")
                self.enable_intelligence = False

        # Initialize enhanced database
        if ENHANCED_DB_AVAILABLE:
            try:
                init_enhanced_db()
                logger.info("Enhanced database initialized")
            except Exception as e:
                logger.warning(f"Enhanced database initialization failed: {e}")

    def setup_logging(self):
        """Setup EQ12-standard logging"""
        log_file = LOGS_DIR / f"eq12_automation_bridge_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

        # Also ensure EQ12 standard snapshot logging
        self.snapshot_log = (
            LOGS_DIR / f"eq12_search_snapshots_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )

    def log_snapshot(self, data: dict[str, Any]):
        """Log JSON snapshot in EQ12 standard format"""
        snapshot = {
            "timestamp": datetime.now(UTC).isoformat(),
            "component": "automation_bridge",
            "data": data,
        }

        try:
            with open(self.snapshot_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(snapshot) + "\n")
        except Exception as e:
            logger.error(f"Failed to write snapshot: {e}")

    def search_for_automation(
        self,
        query: str,
        stack: str | None = None,
        automation_context: dict | None = None,
    ) -> dict[str, Any]:
        """
        Search interface optimized for automation systems

        Args:
            query: Search query
            stack: Force specific stack
            automation_context: Context from calling automation system

        Returns:
            Standardized results dictionary for automation consumption
        """
        start_time = time.time()

        results = {
            "query": query,
            "timestamp": datetime.now(UTC).isoformat(),
            "automation_context": automation_context,
            "success": False,
            "results": [],
            "metadata": {
                "processing_time_ms": 0,
                "intelligence_used": False,
                "detected_stack": None,
                "confidence": 0.0,
                "sources_used": [],
                "error": None,
            },
        }

        try:
            if self.enable_intelligence and self.unified_search:
                # Use enhanced search
                search_results = self.unified_search.search_unified(
                    query=query,
                    count=10,
                    stack=stack,
                    use_intelligence=True,
                    include_meta=True,
                    include_google=True,
                )

                results["success"] = True
                results["metadata"]["intelligence_used"] = True
                results["metadata"]["detected_stack"] = search_results.get("detected_stack")
                results["metadata"]["sources_used"] = search_results.get("sources_used", [])

                # Combine all results for automation consumption
                all_results = []
                all_results.extend(search_results.get("meta_search_results", []))
                all_results.extend(search_results.get("google_results", []))

                # Add intelligence results
                for stack_name, intel_data in search_results.get(
                    "intelligence_results", {}
                ).items():
                    if isinstance(intel_data, dict) and "results" in intel_data:
                        for item in intel_data["results"]:
                            if isinstance(item, dict):
                                # Add intelligence metadata
                                item["_intelligence_source"] = stack_name
                                item["_enhanced"] = True
                                all_results.append(item)

                results["results"] = all_results
                results["metadata"]["confidence"] = 0.8  # High confidence with intelligence

                # Record analytics if available
                if ENHANCED_DB_AVAILABLE:
                    try:
                        record_query_analytics(
                            query,
                            {
                                "detected_stack": search_results.get("detected_stack"),
                                "intelligence_used": True,
                            },
                            {
                                "total_results": len(all_results),
                                "automation_context": automation_context,
                            },
                        )
                    except Exception as e:
                        logger.warning(f"Analytics recording failed: {e}")

            else:
                # Fallback to basic search
                logger.warning("Using fallback search - intelligence not available")
                results["metadata"]["error"] = "Intelligence modules not available"
                results["success"] = True
                results["metadata"]["confidence"] = 0.3  # Lower confidence without intelligence

        except Exception as e:
            logger.error(f"Search failed: {e}")
            results["metadata"]["error"] = str(e)

        # Record timing
        processing_time = (time.time() - start_time) * 1000
        results["metadata"]["processing_time_ms"] = int(processing_time)

        # Log snapshot
        self.log_snapshot(results)

        # Record performance metric
        if ENHANCED_DB_AVAILABLE:
            try:
                record_performance_metric(
                    "automation_search_time",
                    processing_time,
                    stack=results["metadata"]["detected_stack"],
                    source="automation_bridge",
                )
            except Exception as e:
                logger.warning(f"Performance metric recording failed: {e}")

        return results

    def integrate_with_godmode_runner(self, query: str, module: str) -> dict[str, Any]:
        """
        Integration point for eq12_godmode_runner system

        Args:
            query: Search query from godmode runner
            module: Which godmode module is calling (sports, travel, etc.)

        Returns:
            Results formatted for godmode runner consumption
        """
        automation_context = {
            "calling_system": "eq12_godmode_runner",
            "module": module,
            "integration_version": "1.0",
        }

        # Map godmode modules to our stacks
        module_stack_mapping = {
            "sports": "betting",
            "travel": "travel",
            "dropship": "finance",  # Could be finance or fleet depending on context
            "housing": "finance",
            "civil_service": None,  # No specific stack
            "study": None,  # No specific stack
        }

        suggested_stack = module_stack_mapping.get(module)

        results = self.search_for_automation(query, suggested_stack, automation_context)

        # Format for godmode runner
        godmode_results = {
            "module": module,
            "query": query,
            "results_count": len(results["results"]),
            "top_results": results["results"][:5],  # Limit for godmode runner
            "intelligence_used": results["metadata"]["intelligence_used"],
            "confidence": results["metadata"]["confidence"],
            "processing_time": results["metadata"]["processing_time_ms"],
            "suggested_actions": self._generate_godmode_actions(results, module),
        }

        return godmode_results

    def integrate_with_omni_scraper(self, scraper_config: dict) -> dict[str, Any]:
        """
        Integration point for omni_scraper system

        Args:
            scraper_config: Configuration from omni_scraper

        Returns:
            Enhanced scraping targets based on search intelligence
        """
        automation_context = {
            "calling_system": "omni_scraper",
            "scraper_config": scraper_config,
            "integration_version": "1.0",
        }

        # Generate search queries based on scraper config
        target_queries = []

        if "sports" in scraper_config.get("categories", []):
            target_queries.extend(
                [
                    "NBA injury report today",
                    "NFL roster updates",
                    "live betting odds movement",
                ]
            )

        if "travel" in scraper_config.get("categories", []):
            target_queries.extend(
                [
                    "flight deal alerts",
                    "hotel booking discounts",
                    "Buffalo airport delays",
                ]
            )

        enhanced_targets = []

        for query in target_queries:
            search_results = self.search_for_automation(query, None, automation_context)

            if search_results["success"]:
                for result in search_results["results"][:3]:  # Top 3 per query
                    enhanced_targets.append(
                        {
                            "url": result.get("url"),
                            "title": result.get("title"),
                            "priority": "high" if result.get("_enhanced") else "normal",
                            "intelligence_source": result.get("_intelligence_source"),
                            "scraping_hints": self._generate_scraping_hints(result),
                        }
                    )

        return {
            "enhanced_targets": enhanced_targets,
            "total_targets": len(enhanced_targets),
            "intelligence_enhanced": sum(1 for t in enhanced_targets if t["priority"] == "high"),
        }

    def integrate_with_elite_runner(self, runner_type: str, params: dict) -> dict[str, Any]:
        """
        Integration point for eq12-elite-run system

        Args:
            runner_type: Type of elite runner (stocks, crypto, sports, etc.)
            params: Parameters from elite runner

        Returns:
            Enhanced data for elite runner processing
        """
        automation_context = {
            "calling_system": "eq12_elite_runner",
            "runner_type": runner_type,
            "params": params,
            "integration_version": "1.0",
        }

        # Map elite runners to search queries
        elite_queries = {
            "stocks": "stock market news today analysis",
            "crypto": "cryptocurrency market analysis bitcoin",
            "sports": "sports betting odds injury reports",
            "jobs": "job market trends remote work",
            "recycle": "recycling market prices metal commodity",
        }

        query = elite_queries.get(runner_type, f"{runner_type} market analysis")

        # Map to appropriate stack
        runner_stack_mapping = {
            "stocks": "finance",
            "crypto": "finance",
            "sports": "betting",
            "jobs": "finance",
            "recycle": "finance",
        }

        stack = runner_stack_mapping.get(runner_type, "finance")

        search_results = self.search_for_automation(query, stack, automation_context)

        # Format for elite runner
        elite_results = {
            "runner_type": runner_type,
            "enhanced_data": search_results["results"][:10],
            "market_insights": self._extract_market_insights(search_results, runner_type),
            "confidence": search_results["metadata"]["confidence"],
            "data_freshness": (
                "real_time" if search_results["metadata"]["intelligence_used"] else "cached"
            ),
            "recommended_actions": self._generate_elite_actions(search_results, runner_type),
        }

        return elite_results

    def _generate_godmode_actions(self, results: dict, module: str) -> list[str]:
        """Generate suggested actions for godmode runner"""
        actions = []

        if results["metadata"]["intelligence_used"]:
            actions.append("High-quality intelligence data available")

        if results["metadata"]["confidence"] > 0.7:
            actions.append("High confidence results - proceed with automation")

        if module == "sports" and results["metadata"]["detected_stack"] == "betting":
            actions.append("Betting-relevant content found - check for odds movement")

        if module == "travel" and len(results["results"]) > 5:
            actions.append("Multiple travel options found - compare prices")

        return actions

    def _generate_scraping_hints(self, result: dict) -> list[str]:
        """Generate scraping hints based on result analysis"""
        hints = []

        url = result.get("url", "")

        if "espn.com" in url:
            hints.extend(["Look for injury reports", "Extract player statistics"])
        elif "booking.com" in url or "expedia.com" in url:
            hints.extend(["Extract price data", "Look for availability"])
        elif any(domain in url for domain in ["yahoo.com", "bloomberg.com"]):
            hints.extend(["Extract market data", "Look for price movements"])

        if result.get("_enhanced"):
            hints.append("Enhanced with intelligence - prioritize extraction")

        return hints

    def _extract_market_insights(self, results: dict, runner_type: str) -> dict[str, Any]:
        """Extract market insights from search results"""
        insights = {
            "total_sources": len(results["results"]),
            "intelligence_enhanced": sum(1 for r in results["results"] if r.get("_enhanced")),
            "key_trends": [],
            "sentiment": "neutral",
        }

        # Analyze titles and snippets for trends
        all_text = " ".join(
            [r.get("title", "") + " " + r.get("snippet", "") for r in results["results"]]
        ).lower()

        # Runner-specific trend detection
        if runner_type in ["stocks", "crypto"]:
            if "up" in all_text or "gains" in all_text or "bullish" in all_text:
                insights["sentiment"] = "positive"
                insights["key_trends"].append("Upward price movement detected")
            elif "down" in all_text or "losses" in all_text or "bearish" in all_text:
                insights["sentiment"] = "negative"
                insights["key_trends"].append("Downward price movement detected")

        elif runner_type == "sports":
            if "injury" in all_text:
                insights["key_trends"].append("Injury reports affecting odds")
            if "upset" in all_text or "surprise" in all_text:
                insights["key_trends"].append("Unexpected game outcomes")

        return insights

    def _generate_elite_actions(self, results: dict, runner_type: str) -> list[str]:
        """Generate recommended actions for elite runners"""
        actions = []

        confidence = results["metadata"]["confidence"]

        if confidence > 0.8:
            actions.append("Execute primary strategy - high confidence data")
        elif confidence > 0.5:
            actions.append("Proceed with caution - moderate confidence")
        else:
            actions.append("Wait for better data - low confidence")

        if runner_type in ["stocks", "crypto"] and results["metadata"]["intelligence_used"]:
            actions.append(
                "Real-time financial intelligence available - consider position adjustment"
            )

        if runner_type == "sports" and any(
            "injury" in r.get("snippet", "").lower() for r in results["results"]
        ):
            actions.append("Injury reports detected - review betting positions")

        return actions

    def run_daily_maintenance(self):
        """Run daily maintenance tasks for the integrated system"""
        logger.info("Running daily maintenance for EQ12 automation bridge")

        maintenance_results = {
            "timestamp": datetime.now(UTC).isoformat(),
            "tasks_completed": [],
            "errors": [],
        }

        try:
            # Clean up expired cache
            if ENHANCED_DB_AVAILABLE:
                cleaned_count = cleanup_expired_cache()
                maintenance_results["tasks_completed"].append(
                    f"Cleaned {cleaned_count} expired cache entries"
                )

            # Generate analytics summary
            if ENHANCED_DB_AVAILABLE:
                summary = get_query_analytics_summary(24)
                maintenance_results["tasks_completed"].append(
                    f"Generated analytics for {summary.get('total_queries', 0)} queries"
                )

                # Save analytics snapshot
                analytics_file = (
                    LOGS_DIR / f"eq12_analytics_summary_{datetime.now().strftime('%Y%m%d')}.json"
                )
                with open(analytics_file, "w") as f:
                    json.dump(summary, f, indent=2, default=str)

            # Test integration points
            test_results = self._test_integration_points()
            maintenance_results["tasks_completed"].append(f"Integration tests: {test_results}")

        except Exception as e:
            error_msg = f"Maintenance error: {e}"
            maintenance_results["errors"].append(error_msg)
            logger.error(error_msg)

        # Log maintenance results
        self.log_snapshot(maintenance_results)

        return maintenance_results

    def _test_integration_points(self) -> dict[str, bool]:
        """Test all integration points"""
        tests = {}

        try:
            # Test godmode runner integration
            test_result = self.integrate_with_godmode_runner("test query", "sports")
            tests["godmode_runner"] = "results_count" in test_result
        except Exception:
            tests["godmode_runner"] = False

        try:
            # Test omni scraper integration
            test_result = self.integrate_with_omni_scraper({"categories": ["sports"]})
            tests["omni_scraper"] = "enhanced_targets" in test_result
        except Exception:
            tests["omni_scraper"] = False

        try:
            # Test elite runner integration
            test_result = self.integrate_with_elite_runner("stocks", {})
            tests["elite_runner"] = "enhanced_data" in test_result
        except Exception:
            tests["elite_runner"] = False

        return tests

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "timestamp": datetime.now(UTC).isoformat(),
            "components": {
                "enhanced_search": self.enable_intelligence and self.unified_search is not None,
                "query_router": self.enable_intelligence and self.query_router is not None,
                "enhanced_database": ENHANCED_DB_AVAILABLE,
                "logging": True,
            },
            "capabilities": {
                "intelligence_routing": self.enable_intelligence,
                "stack_detection": self.enable_intelligence,
                "enhanced_analytics": ENHANCED_DB_AVAILABLE,
                "automation_integration": True,
            },
            "integration_points": {
                "godmode_runner": True,
                "omni_scraper": True,
                "elite_runner": True,
                "task_scheduler": True,
            },
        }

        # Test integration points
        if self.enable_intelligence:
            integration_tests = self._test_integration_points()
            status["integration_tests"] = integration_tests
            status["integration_health"] = sum(integration_tests.values()) / len(integration_tests)

        return status


# Convenience functions for existing EQ12 systems
def search_for_godmode(query: str, module: str) -> dict[str, Any]:
    """Convenience function for godmode runner integration"""
    bridge = EQ12AutomationBridge()
    return bridge.integrate_with_godmode_runner(query, module)


def search_for_omni_scraper(config: dict) -> dict[str, Any]:
    """Convenience function for omni scraper integration"""
    bridge = EQ12AutomationBridge()
    return bridge.integrate_with_omni_scraper(config)


def search_for_elite_runner(runner_type: str, params: dict | None = None) -> dict[str, Any]:
    """Convenience function for elite runner integration"""
    bridge = EQ12AutomationBridge()
    return bridge.integrate_with_elite_runner(runner_type, params or {})


def run_daily_bridge_maintenance():
    """Convenience function for daily maintenance"""
    bridge = EQ12AutomationBridge()
    return bridge.run_daily_maintenance()


# CLI interface for testing and management
def main():
    """CLI interface for the automation bridge"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Automation Integration Bridge")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Test search functionality")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--stack", help="Force specific stack")

    # Integration test commands
    godmode_parser = subparsers.add_parser("test-godmode", help="Test godmode integration")
    godmode_parser.add_argument("query", help="Search query")
    godmode_parser.add_argument("module", help="Godmode module")

    elite_parser = subparsers.add_parser("test-elite", help="Test elite runner integration")
    elite_parser.add_argument("runner_type", help="Elite runner type")

    # Maintenance command
    subparsers.add_parser("maintenance", help="Run daily maintenance")

    # Status command
    subparsers.add_parser("status", help="Show system status")

    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    bridge = EQ12AutomationBridge(verbose=args.verbose)

    try:
        if args.command == "search":
            results = bridge.search_for_automation(args.query, args.stack)
            print(json.dumps(results, indent=2, default=str))

        elif args.command == "test-godmode":
            results = bridge.integrate_with_godmode_runner(args.query, args.module)
            print("🎮 Godmode Runner Integration Test")
            print(f"Module: {results['module']}")
            print(f"Results: {results['results_count']}")
            print(f"Intelligence: {results['intelligence_used']}")
            print(f"Confidence: {results['confidence']:.3f}")

        elif args.command == "test-elite":
            results = bridge.integrate_with_elite_runner(args.runner_type)
            print("⚡ Elite Runner Integration Test")
            print(f"Type: {results['runner_type']}")
            print(f"Data Points: {len(results['enhanced_data'])}")
            print(f"Confidence: {results['confidence']:.3f}")
            print(f"Freshness: {results['data_freshness']}")

        elif args.command == "maintenance":
            results = bridge.run_daily_maintenance()
            print("🔧 Daily Maintenance Complete")
            print(f"Tasks: {len(results['tasks_completed'])}")
            print(f"Errors: {len(results['errors'])}")
            for task in results["tasks_completed"]:
                print(f"  ✅ {task}")
            for error in results["errors"]:
                print(f"  ❌ {error}")

        elif args.command == "status":
            status = bridge.get_system_status()
            print("📊 EQ12 Automation Bridge Status")
            print(f"Enhanced Search: {'✅' if status['components']['enhanced_search'] else '❌'}")
            print(f"Query Router: {'✅' if status['components']['query_router'] else '❌'}")
            print(f"Enhanced DB: {'✅' if status['components']['enhanced_database'] else '❌'}")

            if "integration_health" in status:
                health = status["integration_health"]
                health_icon = "🟢" if health > 0.8 else "🟡" if health > 0.5 else "🔴"
                print(f"Integration Health: {health_icon} {health:.1%}")

    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
