#!/usr/bin/env python3
"""
EQ12 Unified Search Controller
Combines existing meta-search with new Bing intelligence suite for comprehensive search automation.

Author: EQ12 AI Assistant
Created: 2025-01-27
"""

import argparse
import json
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add paths for both systems
BASE_DIR = Path(__file__).resolve().parent
METASEARCH_DIR = BASE_DIR / "eq12_meta_search"
BING_INTEL_DIR = BASE_DIR / "bing_intelligence"

sys.path.insert(0, str(METASEARCH_DIR))
sys.path.insert(0, str(BING_INTEL_DIR / "core"))
sys.path.insert(0, str(BING_INTEL_DIR))

# Import existing meta-search components
try:
    from alert_pipe import format_markdown, send_telegram
    from clients import BingClient as MetaBingClient
    from clients import GoogleClient
    from db import init_db, latest_by_query, upsert_results

    METASEARCH_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Meta-search system not available: {e}")
    METASEARCH_AVAILABLE = False

# Import new Bing intelligence suite
try:
    from betting.bing_betting_intel import BingBettingIntel
    from bing_web_search import EQ12BingSearch, send_urgent_alert, setup_eq12_logging
    from cannabis.bing_cannabis_intel import BingCannabisIntel
    from finance.bing_finance_intel import BingFinanceIntel
    from fleet.bing_fleet_intel import BingFleetIntel
    from travel.bing_travel_intel import BingTravelIntel

    BING_INTEL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Bing intelligence suite not available: {e}")
    BING_INTEL_AVAILABLE = False

# EQ12 standard logging
logger = logging.getLogger("eq12_unified_search")
LOGS_DIR = Path(os.environ.get("EQ12_LOGS", r"C:\EQ12\logs"))
LOGS_DIR.mkdir(parents=True, exist_ok=True)


class StackDetector:
    """Intelligent detection of which EQ12 stack a query belongs to"""

    STACK_KEYWORDS = {
        "betting": [
            "odds",
            "sportsbook",
            "bet",
            "betting",
            "wager",
            "moneyline",
            "spread",
            "over/under",
            "parlay",
            "prop bet",
            "futures",
            "live betting",
            "injury",
            "roster",
            "lineup",
            "team news",
            "player stats",
            "game prediction",
            "nfl",
            "nba",
            "mlb",
            "nhl",
            "ncaa",
            "soccer",
            "mma",
            "boxing",
        ],
        "travel": [
            "flight",
            "hotel",
            "airfare",
            "booking",
            "travel deal",
            "vacation",
            "airline",
            "resort",
            "destination",
            "trip",
            "fare",
            "ticket",
            "expedia",
            "kayak",
            "priceline",
            "skyscanner",
            "tripadvisor",
            "buffalo to",
            "buf to",
            "airport",
            "tsa",
            "baggage",
            "itinerary",
        ],
        "cannabis": [
            "dispensary",
            "cannabis",
            "marijuana",
            "cbd",
            "thc",
            "weed",
            "medical marijuana",
            "recreational",
            "strain",
            "edibles",
            "vape",
            "concentrates",
            "flower",
            "budtender",
            "cultivation",
            "license",
            "regulation",
            "legalization",
            "hemp",
            "terpenes",
        ],
        "finance": [
            "stock",
            "trading",
            "investment",
            "market",
            "crypto",
            "bitcoin",
            "portfolio",
            "earnings",
            "dividend",
            "ipo",
            "options",
            "futures",
            "forex",
            "etf",
            "mutual fund",
            "bond",
            "commodity",
            "analysis",
            "finance",
            "economy",
            "fed",
            "interest rate",
            "inflation",
        ],
        "fleet": [
            "turo",
            "car rental",
            "vehicle",
            "auto",
            "truck",
            "fleet",
            "insurance",
            "maintenance",
            "repair",
            "recall",
            "safety",
            "automotive",
            "dealership",
            "financing",
            "lease",
            "mpg",
            "fuel efficiency",
            "electric vehicle",
            "hybrid",
            "car market",
        ],
    }

    @classmethod
    def detect_stack(cls, query: str) -> str | None:
        """Detect which stack a query belongs to based on keywords"""
        query_lower = query.lower()

        stack_scores = {}
        for stack, keywords in cls.STACK_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                stack_scores[stack] = score

        if stack_scores:
            # Return the stack with highest keyword match score
            return max(stack_scores.keys(), key=lambda k: stack_scores[k])

        return None


class EQ12UnifiedSearch:
    """Master controller combining meta-search and Bing intelligence suite"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.setup_logging()

        # Initialize meta-search components
        self.meta_bing = None
        self.google_client = None
        if METASEARCH_AVAILABLE:
            try:
                self.meta_bing = MetaBingClient()
                self.google_client = GoogleClient()
                init_db()  # Initialize meta-search database
                logger.info("Meta-search system initialized")
            except Exception as e:
                logger.warning(f"Meta-search initialization failed: {e}")

        # Initialize Bing intelligence suite
        self.intelligence_modules = {}
        if BING_INTEL_AVAILABLE:
            try:
                self.intelligence_modules = {
                    "betting": BingBettingIntel(verbose),
                    "travel": BingTravelIntel(verbose),
                    "cannabis": BingCannabisIntel(verbose),
                    "finance": BingFinanceIntel(verbose),
                    "fleet": BingFleetIntel(verbose),
                }
                logger.info(
                    f"Bing intelligence suite initialized with {len(self.intelligence_modules)} modules"
                )
            except Exception as e:
                logger.warning(f"Bing intelligence initialization failed: {e}")

    def setup_logging(self):
        """Setup EQ12-standard logging"""
        if BING_INTEL_AVAILABLE:
            setup_eq12_logging()
        else:
            # Fallback logging setup
            logging.basicConfig(
                level=logging.INFO if self.verbose else logging.WARNING,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )

    def search_unified(
        self,
        query: str,
        count: int = 10,
        stack: str | None = None,
        use_intelligence: bool = True,
        include_meta: bool = True,
        include_google: bool = True,
    ) -> dict[str, Any]:
        """
        Unified search that combines both meta-search and intelligence modules

        Args:
            query: Search query
            count: Number of results per source
            stack: Force specific stack (betting, travel, cannabis, finance, fleet)
            use_intelligence: Whether to use intelligence modules for enhanced analysis
            include_meta: Whether to include meta-search results (basic Bing)
            include_google: Whether to include Google search results

        Returns:
            Dictionary with results from different sources and analysis
        """
        results = {
            "query": query,
            "timestamp": datetime.now(UTC).isoformat(),
            "detected_stack": None,
            "meta_search_results": [],
            "google_results": [],
            "intelligence_results": {},
            "analysis": {},
            "total_results": 0,
            "sources_used": [],
        }

        # Detect stack if not specified
        if not stack and use_intelligence:
            stack = StackDetector.detect_stack(query)
            results["detected_stack"] = stack

        # Get meta-search results (basic Bing)
        if include_meta and METASEARCH_AVAILABLE and self.meta_bing:
            try:
                meta_results = self.meta_bing.web_search(query, count)
                results["meta_search_results"] = meta_results
                results["sources_used"].append("meta_bing")
                logger.info(f"Meta-search returned {len(meta_results)} results")
            except Exception as e:
                logger.error(f"Meta-search failed: {e}")

        # Get Google search results
        if include_google and METASEARCH_AVAILABLE and self.google_client:
            try:
                google_results = self.google_client.web_search(query, count)
                results["google_results"] = google_results
                results["sources_used"].append("google")
                logger.info(f"Google search returned {len(google_results)} results")
            except Exception as e:
                logger.error(f"Google search failed: {e}")

        # Get intelligence results if stack detected and intelligence available
        if (
            use_intelligence
            and stack
            and BING_INTEL_AVAILABLE
            and stack in self.intelligence_modules
        ):
            try:
                intel_module = self.intelligence_modules[stack]

                if hasattr(intel_module, "search_with_analysis"):
                    intel_results = intel_module.search_with_analysis(query, count)
                    results["intelligence_results"][stack] = intel_results
                    results["sources_used"].append(f"intelligence_{stack}")
                    logger.info(f"Intelligence module '{stack}' returned enriched results")

                    # Extract analysis if available
                    if isinstance(intel_results, dict) and "analysis" in intel_results:
                        results["analysis"][stack] = intel_results["analysis"]

            except Exception as e:
                logger.error(f"Intelligence module '{stack}' failed: {e}")

        # Store results in meta-search database for historical tracking
        if METASEARCH_AVAILABLE:
            try:
                all_results = results["meta_search_results"] + results["google_results"]

                # Add intelligence results to storage if they have standard format
                for stack_name, intel_data in results["intelligence_results"].items():
                    if isinstance(intel_data, dict) and "results" in intel_data:
                        intel_results = intel_data["results"]
                        if isinstance(intel_results, list):
                            for item in intel_results:
                                if isinstance(item, dict) and "url" in item:
                                    # Convert intelligence result to meta-search format
                                    meta_item = {
                                        "title": item.get("title", ""),
                                        "url": item.get("url", ""),
                                        "snippet": item.get("snippet", ""),
                                        "source": f"intelligence_{stack_name}",
                                        "published_at": item.get("published_at"),
                                    }
                                    all_results.append(meta_item)

                stored_count = upsert_results(query, all_results)
                results["stored_count"] = stored_count
                logger.info(f"Stored {stored_count} results to database")

            except Exception as e:
                logger.error(f"Database storage failed: {e}")

        results["total_results"] = (
            len(results["meta_search_results"])
            + len(results["google_results"])
            + sum(
                len(v.get("results", [])) if isinstance(v, dict) else 0
                for v in results["intelligence_results"].values()
            )
        )

        return results

    def search_stack_specific(self, query: str, stack: str, count: int = 10) -> dict[str, Any]:
        """Search using only the specified stack's intelligence module"""
        if not BING_INTEL_AVAILABLE or stack not in self.intelligence_modules:
            raise ValueError(f"Intelligence module '{stack}' not available")

        try:
            intel_module = self.intelligence_modules[stack]
            if hasattr(intel_module, "search_with_analysis"):
                results = intel_module.search_with_analysis(query, count)

                # Store in database if meta-search available
                if METASEARCH_AVAILABLE and isinstance(results, dict) and "results" in results:
                    meta_results = []
                    for item in results["results"]:
                        if isinstance(item, dict) and "url" in item:
                            meta_item = {
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "snippet": item.get("snippet", ""),
                                "source": f"intelligence_{stack}",
                                "published_at": item.get("published_at"),
                            }
                            meta_results.append(meta_item)

                    upsert_results(query, meta_results)

                return results
            raise ValueError(f"Intelligence module '{stack}' doesn't support analysis")

        except Exception as e:
            logger.error(f"Stack-specific search failed: {e}")
            raise

    def get_search_history(self, query: str, limit: int = 20) -> list[dict]:
        """Get historical search results for a query"""
        if not METASEARCH_AVAILABLE:
            raise ValueError("Meta-search system not available for history")

        return latest_by_query(query, limit)

    def send_results_alert(self, results: dict[str, Any], header: str | None = None) -> str | None:
        """Send search results via Telegram"""
        if not METASEARCH_AVAILABLE:
            logger.warning("Telegram alerts not available without meta-search system")
            return "Meta-search system required for alerts"

        # Combine all results for alert
        all_results = results["meta_search_results"] + results["google_results"]

        # Add intelligence results
        for stack_name, intel_data in results["intelligence_results"].items():
            if isinstance(intel_data, dict) and "results" in intel_data:
                intel_results = intel_data["results"]
                if isinstance(intel_results, list):
                    for item in intel_results:
                        if isinstance(item, dict) and "url" in item:
                            alert_item = {
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "source": f"🧠{stack_name}",
                            }
                            all_results.append(alert_item)

        if not header:
            stack_info = f" ({results['detected_stack']})" if results["detected_stack"] else ""
            header = f"🔍 EQ12 Unified Search{stack_info}: {results['query']}"

        return send_telegram(all_results, header)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="EQ12 Unified Search - Meta-search + Intelligence")

    # Query options
    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument("--query", help="Single search query")
    query_group.add_argument("--query-file", help="File with one query per line")

    # Search options
    parser.add_argument("--count", type=int, default=10, help="Results per source (default: 10)")
    parser.add_argument(
        "--stack",
        choices=["betting", "travel", "cannabis", "finance", "fleet"],
        help="Force specific stack intelligence module",
    )

    # Source control
    parser.add_argument(
        "--no-intelligence",
        action="store_true",
        help="Disable intelligence modules (basic search only)",
    )
    parser.add_argument("--no-meta", action="store_true", help="Disable meta Bing search")
    parser.add_argument("--no-google", action="store_true", help="Disable Google search")
    parser.add_argument(
        "--stack-only",
        action="store_true",
        help="Use only stack intelligence module (requires --stack)",
    )

    # Output options
    parser.add_argument("--telegram", action="store_true", help="Send results via Telegram")
    parser.add_argument(
        "--show-latest",
        action="store_true",
        help="Show latest historical results after search",
    )
    parser.add_argument(
        "--history-only",
        action="store_true",
        help="Show only historical results (no new search)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--json-output", action="store_true", help="Output results as JSON")

    return parser.parse_args()


def format_results_text(results: dict[str, Any]) -> str:
    """Format search results as readable text"""
    lines = []

    lines.append(f"🔍 EQ12 Unified Search Results for: {results['query']}")
    lines.append(f"📅 Timestamp: {results['timestamp']}")

    if results["detected_stack"]:
        lines.append(f"🎯 Detected Stack: {results['detected_stack']}")

    lines.append(f"📊 Total Results: {results['total_results']}")
    lines.append(f"🔧 Sources Used: {', '.join(results['sources_used'])}")
    lines.append("")

    # Meta-search results
    if results["meta_search_results"]:
        lines.append("🔵 Meta Bing Search Results:")
        for i, item in enumerate(results["meta_search_results"][:5], 1):
            lines.append(f"  {i}. {item.get('title', 'No title')}")
            lines.append(f"     {item.get('url', '')}")
            lines.append(f"     {item.get('snippet', '')[:100]}...")
            lines.append("")

    # Google results
    if results["google_results"]:
        lines.append("🟢 Google Search Results:")
        for i, item in enumerate(results["google_results"][:5], 1):
            lines.append(f"  {i}. {item.get('title', 'No title')}")
            lines.append(f"     {item.get('url', '')}")
            lines.append(f"     {item.get('snippet', '')[:100]}...")
            lines.append("")

    # Intelligence results
    for stack_name, intel_data in results["intelligence_results"].items():
        lines.append(f"🧠 {stack_name.title()} Intelligence Results:")
        if isinstance(intel_data, dict):
            if "results" in intel_data:
                for i, item in enumerate(intel_data["results"][:5], 1):
                    lines.append(f"  {i}. {item.get('title', 'No title')}")
                    lines.append(f"     {item.get('url', '')}")
                    if item.get("snippet"):
                        lines.append(f"     {item['snippet'][:100]}...")
                    lines.append("")

            if "analysis" in intel_data:
                analysis = intel_data["analysis"]
                if isinstance(analysis, dict):
                    lines.append("  📈 Analysis Summary:")
                    for key, value in analysis.items():
                        if isinstance(value, (str, int, float)):
                            lines.append(f"    • {key}: {value}")
                lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point"""
    args = parse_args()

    # Validation
    if args.stack_only and not args.stack:
        print("Error: --stack-only requires --stack")
        return 1

    # Initialize unified search
    try:
        searcher = EQ12UnifiedSearch(verbose=args.verbose)
    except Exception as e:
        print(f"Error initializing unified search: {e}")
        return 1

    # Process queries
    queries = []
    if args.query:
        queries = [args.query]
    elif args.query_file:
        try:
            with open(args.query_file, encoding="utf-8") as f:
                queries = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Error reading query file: {e}")
            return 1

    for query in queries:
        try:
            # Handle different search modes
            if args.history_only:
                # Show only historical results
                if not METASEARCH_AVAILABLE:
                    print("Error: History requires meta-search system")
                    continue

                history = searcher.get_search_history(query)
                if args.json_output:
                    print(json.dumps({"query": query, "history": history}, indent=2))
                else:
                    print(f"\n📚 Search History for: {query}")
                    for item in history[:10]:
                        print(f"  • {item.get('title', 'No title')} ({item.get('source', '?')})")
                        print(f"    {item.get('url', '')}")
                        print(f"    {item.get('fetched_at', '')}")
                        print()
                continue

            if args.stack_only:
                # Use only intelligence module
                results = searcher.search_stack_specific(query, args.stack, args.count)
                if args.json_output:
                    print(json.dumps(results, indent=2, default=str))
                else:
                    print(f"\n🧠 {args.stack.title()} Intelligence Results for: {query}")
                    if isinstance(results, dict) and "results" in results:
                        for i, item in enumerate(results["results"][:10], 1):
                            print(f"  {i}. {item.get('title', 'No title')}")
                            print(f"     {item.get('url', '')}")
                            print()
            else:
                # Unified search
                results = searcher.search_unified(
                    query=query,
                    count=args.count,
                    stack=args.stack,
                    use_intelligence=not args.no_intelligence,
                    include_meta=not args.no_meta,
                    include_google=not args.no_google,
                )

                if args.json_output:
                    print(json.dumps(results, indent=2, default=str))
                else:
                    print(format_results_text(results))

                # Send Telegram alert if requested
                if args.telegram:
                    alert_result = searcher.send_results_alert(results)
                    if alert_result:
                        print(f"⚠️ Telegram alert failed: {alert_result}")
                    else:
                        print("✅ Telegram alert sent successfully")

                # Show latest results if requested
                if args.show_latest and METASEARCH_AVAILABLE:
                    print("\n📚 Latest Historical Results:")
                    history = searcher.get_search_history(query, 5)
                    for item in history:
                        print(f"  • {item.get('title', 'No title')} ({item.get('source', '?')})")

        except Exception as e:
            print(f"Error processing query '{query}': {e}")
            if args.verbose:
                import traceback

                traceback.print_exc()

    return 0


if __name__ == "__main__":
    sys.exit(main())
