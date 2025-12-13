#!/usr/bin/env python3
"""
EQ12 GODSTACK - DevTools Agent Integration
Provides browser-native scraping with Chrome DevTools MCP integration for robust data extraction.

Author: EQ12-GODSTACK
Created: 2025-09-27
"""

import json
import logging
import os
import time
from typing import Any

from playwright.sync_api import sync_playwright

# Constants
DEVTOOLS_ENABLED = os.getenv("EQ12_DEVTOOLS_ENABLED", "false").lower() == "true"
DEVTOOLS_PORT = int(os.getenv("EQ12_DEVTOOLS_PORT", "9222"))


def setup_logging():
    """Setup logging for DevTools agent."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("C:/EQ12/logs/devtools_agent.log"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


class DevToolsAgent:
    """
    Chrome DevTools MCP integration for advanced browser automation.
    Provides DOM inspection, network tracing, and JS profiling capabilities.
    """

    def __init__(self, use_devtools: bool = DEVTOOLS_ENABLED):
        self.logger = setup_logging()
        self.use_devtools = use_devtools
        self.browser = None
        self.page = None
        self.devtools_connected = False

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

    def start(self):
        """Start browser with optional DevTools connection."""
        self.logger.info("Starting DevTools Agent")

        playwright = sync_playwright().start()

        if self.use_devtools:
            try:
                # Launch Chrome with DevTools enabled
                self.browser = playwright.chromium.launch(
                    headless=False,
                    args=[
                        f"--remote-debugging-port={DEVTOOLS_PORT}",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage",
                        "--no-sandbox",
                    ],
                )
                self.devtools_connected = True
                self.logger.info(f"DevTools enabled on port {DEVTOOLS_PORT}")

            except Exception as e:
                self.logger.warning(f"DevTools connection failed, falling back to Playwright: {e}")
                self.browser = playwright.chromium.launch(headless=True)
                self.devtools_connected = False
        else:
            # Standard Playwright launch
            self.browser = playwright.chromium.launch(headless=True)
            self.devtools_connected = False

        self.page = self.browser.new_page()

        # Set user agent to avoid detection
        self.page.set_extra_http_headers(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def stop(self):
        """Stop browser and cleanup."""
        if self.browser:
            self.browser.close()
        self.logger.info("DevTools Agent stopped")

    def inspect_dom(self, url: str, selector: str | None = None) -> dict:
        """
        Inspect DOM structure with DevTools-level detail.

        Args:
            url: Target URL to inspect
            selector: Optional CSS selector to focus on

        Returns:
            DOM inspection results
        """
        try:
            self.logger.info(f"Inspecting DOM: {url}")
            self.page.goto(url, wait_until="networkidle")

            # Basic DOM extraction
            if selector:
                elements = self.page.query_selector_all(selector)
                dom_data = []
                for element in elements[:10]:  # Limit to 10 elements
                    dom_data.append(
                        {
                            "tag": element.tag_name,
                            "text": element.text_content()[:200],
                            "attributes": element.get_attribute("class")
                            or element.get_attribute("id")
                            or "",
                            "innerHTML": (
                                element.inner_html()[:500] if element.inner_html() else ""
                            ),
                        }
                    )
            else:
                # Full page structure
                dom_data = {
                    "title": self.page.title(),
                    "url": self.page.url,
                    "meta_description": self.page.locator('meta[name="description"]').get_attribute(
                        "content"
                    )
                    or "",
                    "headings": [
                        h.text_content() for h in self.page.query_selector_all("h1, h2, h3")[:10]
                    ],
                    "links": [
                        {
                            "text": link.text_content()[:50],
                            "href": link.get_attribute("href"),
                        }
                        for link in self.page.query_selector_all("a[href]")[:20]
                    ],
                    "images": [
                        img.get_attribute("src")
                        for img in self.page.query_selector_all("img[src]")[:10]
                    ],
                }

            # Enhanced inspection with DevTools (if available)
            if self.devtools_connected:
                dom_data = self._enhance_dom_inspection(dom_data, url)

            return {
                "status": "success",
                "url": url,
                "selector": selector,
                "devtools_enabled": self.devtools_connected,
                "dom_data": dom_data,
                "timestamp": time.time(),
            }

        except Exception as e:
            self.logger.error(f"DOM inspection failed for {url}: {e}")
            return {
                "status": "error",
                "url": url,
                "error": str(e),
                "devtools_enabled": self.devtools_connected,
            }

    def trace_network(self, url: str, duration: int = 10) -> dict:
        """
        Trace network activity with DevTools-level detail.

        Args:
            url: Target URL to monitor
            duration: How long to monitor (seconds)

        Returns:
            Network tracing results
        """
        try:
            self.logger.info(f"Tracing network for {url} ({duration}s)")

            # Setup request/response tracking
            requests = []
            responses = []

            def handle_request(request):
                requests.append(
                    {
                        "url": request.url,
                        "method": request.method,
                        "headers": dict(request.headers),
                        "timestamp": time.time(),
                    }
                )

            def handle_response(response):
                responses.append(
                    {
                        "url": response.url,
                        "status": response.status,
                        "headers": dict(response.headers),
                        "size": len(response.body()) if response.body() else 0,
                        "timestamp": time.time(),
                    }
                )

            self.page.on("request", handle_request)
            self.page.on("response", handle_response)

            # Navigate and monitor
            time.time()
            self.page.goto(url, wait_until="networkidle")

            # Monitor for specified duration
            time.sleep(duration)

            # Enhanced network analysis with DevTools (if available)
            network_analysis = {
                "total_requests": len(requests),
                "total_responses": len(responses),
                "unique_domains": len(
                    {req["url"].split("/")[2] for req in requests if len(req["url"].split("/")) > 2}
                ),
                "status_codes": {},
                "content_types": {},
                "total_bytes": sum(resp.get("size", 0) for resp in responses),
            }

            # Analyze status codes
            for resp in responses:
                status = resp["status"]
                network_analysis["status_codes"][status] = (
                    network_analysis["status_codes"].get(status, 0) + 1
                )

            # Analyze content types
            for resp in responses:
                content_type = resp["headers"].get("content-type", "unknown").split(";")[0]
                network_analysis["content_types"][content_type] = (
                    network_analysis["content_types"].get(content_type, 0) + 1
                )

            if self.devtools_connected:
                network_analysis = self._enhance_network_tracing(network_analysis, url)

            return {
                "status": "success",
                "url": url,
                "duration": duration,
                "devtools_enabled": self.devtools_connected,
                "requests": requests[:50],  # Limit for performance
                "responses": responses[:50],
                "analysis": network_analysis,
                "timestamp": time.time(),
            }

        except Exception as e:
            self.logger.error(f"Network tracing failed for {url}: {e}")
            return {
                "status": "error",
                "url": url,
                "error": str(e),
                "devtools_enabled": self.devtools_connected,
            }

    def profile_js(self, url: str, duration: int = 5) -> dict:
        """
        Profile JavaScript execution with DevTools-level detail.

        Args:
            url: Target URL to profile
            duration: How long to profile (seconds)

        Returns:
            JS profiling results
        """
        try:
            self.logger.info(f"Profiling JS for {url} ({duration}s)")

            # Basic JS analysis
            self.page.goto(url, wait_until="networkidle")

            # Check for common JS issues
            js_analysis = {
                "console_errors": [],
                "js_files_loaded": 0,
                "inline_scripts": 0,
                "external_scripts": 0,
            }

            # Capture console errors
            def handle_console(msg):
                if msg.type in ["error", "warning"]:
                    js_analysis["console_errors"].append(
                        {"type": msg.type, "text": msg.text, "timestamp": time.time()}
                    )

            self.page.on("console", handle_console)

            # Analyze script tags
            script_tags = self.page.query_selector_all("script")
            for script in script_tags:
                src = script.get_attribute("src")
                if src:
                    js_analysis["external_scripts"] += 1
                    js_analysis["js_files_loaded"] += 1
                else:
                    js_analysis["inline_scripts"] += 1

            # Wait and collect data
            time.sleep(duration)

            # Enhanced profiling with DevTools (if available)
            if self.devtools_connected:
                js_analysis = self._enhance_js_profiling(js_analysis, url)

            return {
                "status": "success",
                "url": url,
                "duration": duration,
                "devtools_enabled": self.devtools_connected,
                "analysis": js_analysis,
                "timestamp": time.time(),
            }

        except Exception as e:
            self.logger.error(f"JS profiling failed for {url}: {e}")
            return {
                "status": "error",
                "url": url,
                "error": str(e),
                "devtools_enabled": self.devtools_connected,
            }

    def smart_scrape(
        self, url: str, target_data: str, fallback_selectors: list[str] | None = None
    ) -> dict:
        """
        Intelligent scraping that adapts to page structure changes.

        Args:
            url: Target URL to scrape
            target_data: Description of what data to extract
            fallback_selectors: List of CSS selectors to try

        Returns:
            Extracted data with resilience info
        """
        try:
            self.logger.info(f"Smart scraping {target_data} from {url}")

            self.page.goto(url, wait_until="networkidle")

            scraped_data = []
            successful_selectors = []

            # Try fallback selectors if provided
            if fallback_selectors:
                for selector in fallback_selectors:
                    try:
                        elements = self.page.query_selector_all(selector)
                        if elements:
                            for element in elements[:10]:  # Limit results
                                text = element.text_content().strip()
                                if text:  # Only add non-empty text
                                    scraped_data.append(
                                        {
                                            "text": text,
                                            "selector": selector,
                                            "tag": element.tag_name,
                                            "attributes": {
                                                "class": element.get_attribute("class"),
                                                "id": element.get_attribute("id"),
                                            },
                                        }
                                    )
                            successful_selectors.append(selector)
                    except Exception as e:
                        self.logger.debug(f"Selector {selector} failed: {e}")
                        continue

            # Enhanced smart scraping with DevTools (if available)
            if self.devtools_connected:
                scraped_data = self._enhance_smart_scraping(scraped_data, target_data, url)

            return {
                "status": "success",
                "url": url,
                "target_data": target_data,
                "devtools_enabled": self.devtools_connected,
                "data": scraped_data,
                "successful_selectors": successful_selectors,
                "resilience_score": (
                    len(successful_selectors) / len(fallback_selectors)
                    if fallback_selectors
                    else 1.0
                ),
                "timestamp": time.time(),
            }

        except Exception as e:
            self.logger.error(f"Smart scraping failed for {url}: {e}")
            return {
                "status": "error",
                "url": url,
                "target_data": target_data,
                "error": str(e),
                "devtools_enabled": self.devtools_connected,
            }

    def _enhance_dom_inspection(self, dom_data: Any, url: str) -> Any:
        """Enhance DOM inspection with DevTools MCP capabilities."""
        # Placeholder for DevTools MCP integration
        # In production, this would use chrome-devtools-mcp
        self.logger.debug("DevTools DOM enhancement (placeholder)")
        return dom_data

    def _enhance_network_tracing(self, analysis: dict, url: str) -> dict:
        """Enhance network tracing with DevTools MCP capabilities."""
        # Placeholder for DevTools MCP integration
        self.logger.debug("DevTools network enhancement (placeholder)")
        return analysis

    def _enhance_js_profiling(self, analysis: dict, url: str) -> dict:
        """Enhance JS profiling with DevTools MCP capabilities."""
        # Placeholder for DevTools MCP integration
        self.logger.debug("DevTools JS enhancement (placeholder)")
        return analysis

    def _enhance_smart_scraping(self, data: list, target: str, url: str) -> list:
        """Enhance smart scraping with DevTools MCP capabilities."""
        # Placeholder for DevTools MCP integration
        self.logger.debug("DevTools scraping enhancement (placeholder)")
        return data


# Convenience functions for common EQ12 use cases


def scrape_swagbucks_offers_enhanced(max_offers: int = 20) -> dict:
    """Enhanced Swagbucks scraping using DevTools agent."""

    swagbucks_selectors = [
        ".offerToro .reward-item",
        ".sb-offer .offer-card",
        ".discover-offer-card",
        "[data-offer-id]",
        ".offer-container .offer-item",
    ]

    with DevToolsAgent() as agent:
        result = agent.smart_scrape(
            url="https://www.swagbucks.com/discover",
            target_data="cashback offers and rewards",
            fallback_selectors=swagbucks_selectors,
        )

        if result["status"] == "success":
            # Process offers data
            offers = []
            for item in result["data"][:max_offers]:
                offers.append(
                    {
                        "title": item["text"][:100],
                        "selector_used": item["selector"],
                        "resilience": result["resilience_score"],
                    }
                )

            return {
                "status": "success",
                "offers": offers,
                "total_found": len(result["data"]),
                "resilience_score": result["resilience_score"],
                "devtools_used": result["devtools_enabled"],
            }

    return {"status": "error", "error": "DevTools agent initialization failed"}


def analyze_betting_site_changes(url: str) -> dict:
    """Analyze betting site for UI changes that might break scrapers."""

    with DevToolsAgent() as agent:
        dom_result = agent.inspect_dom(url)
        network_result = agent.trace_network(url, duration=5)

        analysis = {
            "site_health": "unknown",
            "api_endpoints": [],
            "ui_stability": "unknown",
            "recommendations": [],
        }

        if dom_result["status"] == "success" and network_result["status"] == "success":
            # Analyze for betting site patterns
            if any("odds" in str(data).lower() for data in dom_result["dom_data"]):
                analysis["ui_stability"] = "odds_elements_found"
                analysis["recommendations"].append("Odds elements detected - scraper should work")

            # Check for API endpoints
            api_requests = [
                req for req in network_result["requests"] if "api" in req["url"].lower()
            ]
            analysis["api_endpoints"] = [req["url"] for req in api_requests[:5]]

            if api_requests:
                analysis["recommendations"].append(
                    "Consider using API endpoints instead of scraping"
                )

        return analysis


def main():
    """CLI interface for DevTools agent."""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 DevTools Agent")
    parser.add_argument("--url", required=True, help="URL to analyze")
    parser.add_argument(
        "--action",
        choices=["dom", "network", "js", "smart-scrape"],
        default="dom",
        help="Action to perform",
    )
    parser.add_argument("--selector", help="CSS selector for DOM inspection")
    parser.add_argument("--target-data", help="Description of data to extract (for smart-scrape)")
    parser.add_argument("--duration", type=int, default=5, help="Duration for network/JS analysis")
    parser.add_argument("--devtools", action="store_true", help="Force DevTools mode")

    args = parser.parse_args()

    if args.devtools:
        os.environ["EQ12_DEVTOOLS_ENABLED"] = "true"

    with DevToolsAgent() as agent:
        if args.action == "dom":
            result = agent.inspect_dom(args.url, args.selector)
        elif args.action == "network":
            result = agent.trace_network(args.url, args.duration)
        elif args.action == "js":
            result = agent.profile_js(args.url, args.duration)
        elif args.action == "smart-scrape":
            result = agent.smart_scrape(args.url, args.target_data or "general content")

        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
