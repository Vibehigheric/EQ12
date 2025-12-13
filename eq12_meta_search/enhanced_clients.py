#!/usr/bin/env python3
"""
Enhanced EQ12 BingClient with Intelligence Module Integration
Extends the existing meta-search BingClient to work with stack-specific intelligence modules.

Author: EQ12 AI Assistant
Created: 2025-01-27
"""

import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests

# Add intelligence module paths
BASE_DIR = Path(__file__).resolve().parent
BING_INTEL_DIR = BASE_DIR / "bing_intelligence"
sys.path.insert(0, str(BING_INTEL_DIR / "core"))
sys.path.insert(0, str(BING_INTEL_DIR))

logger = logging.getLogger("enhanced_bing_client")

# Import intelligence modules if available
try:
    from betting.bing_betting_intel import BingBettingIntel
    from bing_web_search import EQ12BingSearch
    from cannabis.bing_cannabis_intel import BingCannabisIntel
    from finance.bing_finance_intel import BingFinanceIntel
    from fleet.bing_fleet_intel import BingFleetIntel
    from travel.bing_travel_intel import BingTravelIntel

    INTELLIGENCE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Intelligence modules not available: {e}")
    INTELLIGENCE_AVAILABLE = False

# Original retry logic from meta-search
DEFAULT_TIMEOUT = 20
RETRY_BACKOFF = [0.5, 1.0, 2.0]


def _request_with_retries(method: str, url: str, **kwargs):
    """Original retry logic from meta-search system"""
    last_exc = None
    for _i, delay in enumerate([0.0, *RETRY_BACKOFF]):
        if delay:
            time.sleep(delay)
        try:
            resp = requests.request(
                method, url, timeout=kwargs.pop("timeout", DEFAULT_TIMEOUT), **kwargs
            )
            resp.raise_for_status()
            return resp
        except Exception as e:
            last_exc = e
    raise last_exc


class EnhancedBingClient:
    """
    Enhanced BingClient that combines meta-search functionality with intelligence modules

    Maintains backward compatibility with original BingClient while adding:
    - Stack-specific intelligence routing
    - Enhanced analysis capabilities
    - Automatic stack detection
    - Rich metadata extraction
    """

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

    def __init__(
        self,
        api_key: str | None = None,
        endpoint: str | None = None,
        enable_intelligence: bool = True,
        verbose: bool = False,
    ):
        """
        Initialize enhanced BingClient

        Args:
            api_key: Bing API key (from BING_KEY env var if not provided)
            endpoint: Bing API endpoint
            enable_intelligence: Whether to enable intelligence module routing
            verbose: Enable verbose logging
        """
        self.api_key = api_key or os.getenv("BING_KEY")
        self.endpoint = endpoint or os.getenv(
            "BING_ENDPOINT", "https://api.bing.microsoft.com/v7.0/search"
        )
        self.enable_intelligence = enable_intelligence and INTELLIGENCE_AVAILABLE
        self.verbose = verbose

        if not self.api_key:
            raise ValueError("EnhancedBingClient: missing API key (set BING_KEY).")

        # Initialize intelligence modules if enabled
        self.intelligence_modules = {}
        if self.enable_intelligence:
            try:
                self.intelligence_modules = {
                    "betting": BingBettingIntel(verbose),
                    "travel": BingTravelIntel(verbose),
                    "cannabis": BingCannabisIntel(verbose),
                    "finance": BingFinanceIntel(verbose),
                    "fleet": BingFleetIntel(verbose),
                }
                logger.info(
                    f"Enhanced BingClient initialized with {len(self.intelligence_modules)} intelligence modules"
                )
            except Exception as e:
                logger.warning(f"Intelligence module initialization failed: {e}")
                self.enable_intelligence = False

    def detect_stack(self, query: str) -> str | None:
        """Detect which stack a query belongs to based on keywords"""
        query_lower = query.lower()

        stack_scores = {}
        for stack, keywords in self.STACK_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                stack_scores[stack] = score

        if stack_scores:
            # Return the stack with highest keyword match score
            best_stack = max(stack_scores.keys(), key=lambda k: stack_scores[k])
            if self.verbose:
                logger.info(f"Detected stack '{best_stack}' for query: {query}")
            return best_stack

        return None

    def web_search(self, query: str, count: int = 10) -> list[dict]:
        """
        Basic web search - maintains backward compatibility with original BingClient

        Args:
            query: Search query
            count: Number of results to return

        Returns:
            List of search results in original meta-search format
        """
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {
            "q": query,
            "count": count,
            "textDecorations": False,
            "textFormat": "Raw",
        }

        resp = _request_with_retries("GET", self.endpoint, headers=headers, params=params)
        js = resp.json()

        out = []
        for item in js.get("webPages", {}).get("value", []):
            out.append(
                {
                    "title": item.get("name"),
                    "url": item.get("url"),
                    "snippet": item.get("snippet"),
                    "source": "bing",
                    "published_at": item.get("dateLastCrawled"),
                }
            )

        return out

    def web_search_enhanced(
        self,
        query: str,
        count: int = 10,
        stack: str | None = None,
        force_basic: bool = False,
    ) -> dict[str, Any]:
        """
        Enhanced web search with intelligence module integration

        Args:
            query: Search query
            count: Number of results to return
            stack: Force specific stack (auto-detect if None)
            force_basic: Force basic search without intelligence

        Returns:
            Dictionary with enhanced results and analysis
        """
        result = {
            "query": query,
            "detected_stack": None,
            "basic_results": [],
            "intelligence_results": None,
            "analysis": None,
            "enhancement_used": False,
        }

        # Get basic results first
        try:
            basic_results = self.web_search(query, count)
            result["basic_results"] = basic_results
        except Exception as e:
            logger.error(f"Basic search failed: {e}")
            raise

        # Skip intelligence if disabled or forced basic
        if not self.enable_intelligence or force_basic:
            return result

        # Detect stack if not provided
        if not stack:
            stack = self.detect_stack(query)

        result["detected_stack"] = stack

        # Use intelligence module if stack detected and available
        if stack and stack in self.intelligence_modules:
            try:
                intel_module = self.intelligence_modules[stack]

                if hasattr(intel_module, "search_with_analysis"):
                    intel_results = intel_module.search_with_analysis(query, count)
                    result["intelligence_results"] = intel_results
                    result["enhancement_used"] = True

                    # Extract analysis if available
                    if isinstance(intel_results, dict) and "analysis" in intel_results:
                        result["analysis"] = intel_results["analysis"]

                    if self.verbose:
                        logger.info(f"Enhanced search completed using {stack} intelligence module")

            except Exception as e:
                logger.error(f"Intelligence enhancement failed for stack '{stack}': {e}")
                # Continue with basic results

        return result

    def search_stack_specific(self, query: str, stack: str, count: int = 10) -> Any:
        """
        Search using a specific intelligence module

        Args:
            query: Search query
            stack: Stack name (betting, travel, cannabis, finance, fleet)
            count: Number of results

        Returns:
            Results from the specific intelligence module
        """
        if not self.enable_intelligence:
            raise ValueError("Intelligence modules not available")

        if stack not in self.intelligence_modules:
            raise ValueError(f"Intelligence module '{stack}' not available")

        intel_module = self.intelligence_modules[stack]

        if hasattr(intel_module, "search_with_analysis"):
            return intel_module.search_with_analysis(query, count)
        raise ValueError(f"Intelligence module '{stack}' doesn't support search_with_analysis")

    def get_available_stacks(self) -> list[str]:
        """Get list of available intelligence stacks"""
        if not self.enable_intelligence:
            return []
        return list(self.intelligence_modules.keys())

    def is_intelligence_available(self) -> bool:
        """Check if intelligence modules are available"""
        return self.enable_intelligence and len(self.intelligence_modules) > 0


# Backward compatibility: create alias to original name
BingClient = EnhancedBingClient


class BingClientLegacy:
    """
    Legacy BingClient class - exact copy of original for backward compatibility
    Use this if you need the original functionality without enhancements
    """

    def __init__(self, api_key: str | None = None, endpoint: str | None = None):
        self.api_key = api_key or os.getenv("BING_KEY")
        self.endpoint = endpoint or os.getenv(
            "BING_ENDPOINT", "https://api.bing.microsoft.com/v7.0/search"
        )
        if not self.api_key:
            raise ValueError("BingClient: missing API key (set BING_KEY).")

    def web_search(self, query: str, count: int = 10) -> list[dict]:
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {
            "q": query,
            "count": count,
            "textDecorations": False,
            "textFormat": "Raw",
        }
        resp = _request_with_retries("GET", self.endpoint, headers=headers, params=params)
        js = resp.json()
        out = []
        for item in js.get("webPages", {}).get("value", []):
            out.append(
                {
                    "title": item.get("name"),
                    "url": item.get("url"),
                    "snippet": item.get("snippet"),
                    "source": "bing",
                    "published_at": item.get("dateLastCrawled"),
                }
            )
        return out


# Usage examples and testing
def main():
    """Test the enhanced BingClient"""
    import argparse

    parser = argparse.ArgumentParser(description="Test Enhanced BingClient")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--count", type=int, default=5, help="Number of results")
    parser.add_argument(
        "--stack",
        choices=["betting", "travel", "cannabis", "finance", "fleet"],
        help="Force specific stack",
    )
    parser.add_argument("--basic", action="store_true", help="Force basic search")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        client = EnhancedBingClient(verbose=args.verbose)

        if args.basic:
            print("🔍 Basic Search Results:")
            results = client.web_search(args.query, args.count)
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   {result['url']}")
                print(f"   {result['snippet'][:100]}...")
                print()
        else:
            print("🧠 Enhanced Search Results:")
            results = client.web_search_enhanced(args.query, args.count, args.stack)

            print(f"Query: {results['query']}")
            print(f"Detected Stack: {results['detected_stack']}")
            print(f"Enhancement Used: {results['enhancement_used']}")
            print()

            if results["basic_results"]:
                print("Basic Results:")
                for i, result in enumerate(results["basic_results"][:3], 1):
                    print(f"  {i}. {result['title']}")
                    print(f"     {result['url']}")
                print()

            if results["intelligence_results"]:
                print("Intelligence Results:")
                intel = results["intelligence_results"]
                if isinstance(intel, dict) and "results" in intel:
                    for i, result in enumerate(intel["results"][:3], 1):
                        print(f"  {i}. {result.get('title', 'No title')}")
                        print(f"     {result.get('url', '')}")
                print()

            if results["analysis"]:
                print("Analysis:")
                for key, value in results["analysis"].items():
                    print(f"  {key}: {value}")

        print(f"✅ Available stacks: {client.get_available_stacks()}")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
