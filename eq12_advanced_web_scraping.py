# eq12_advanced_web_scraping.py
"""
EQ12 Advanced Web Scraping & Anti-Detection System
Puppeteer/Playwright integration, Cheerio parsing, stealth mode, intelligent retry
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Web scraping libraries
from playwright.async_api import Browser, BrowserContext, Page, async_playwright
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from eq12_helpers import setup_utf8_logging

setup_utf8_logging()


class ScrapingStrategy(Enum):
    """Web scraping strategies"""

    REQUESTS = "requests"
    PLAYWRIGHT = "playwright"
    STEALTH = "stealth"
    MOBILE = "mobile"
    PROXY_ROTATION = "proxy_rotation"


class DetectionLevel(Enum):
    """Anti-detection levels"""

    MINIMAL = "minimal"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    PARANOID = "paranoid"


@dataclass
class ScrapingTarget:
    """Scraping target configuration"""

    url: str
    name: str
    selectors: dict[str, str]
    strategy: ScrapingStrategy = ScrapingStrategy.PLAYWRIGHT
    detection_level: DetectionLevel = DetectionLevel.STANDARD
    rate_limit: float = 1.0  # Seconds between requests
    timeout: int = 30
    retries: int = 3
    custom_headers: dict[str, str] = field(default_factory=dict)
    proxy: str | None = None
    javascript_required: bool = True


@dataclass
class ScrapingResult:
    """Scraping operation result"""

    target: str
    success: bool
    data: dict[str, Any]
    metadata: dict[str, Any]
    timestamp: datetime
    duration_ms: float
    error: str | None = None
    response_code: int | None = None


class UserAgentManager:
    """Advanced user agent management"""

    def __init__(self):
        self.ua = UserAgent()
        self.custom_agents = [
            # Desktop Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Desktop Firefox
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            # Desktop Safari
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            # Mobile
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0",
        ]
        self.used_agents = set()

    def get_random_agent(self, mobile: bool = False) -> str:
        """Get random user agent"""

        if mobile:
            agents = [
                ua
                for ua in self.custom_agents
                if "Mobile" in ua or "iPhone" in ua or "Android" in ua
            ]
        else:
            agents = [
                ua
                for ua in self.custom_agents
                if "Mobile" not in ua and "iPhone" not in ua and "Android" not in ua
            ]

        # Try to get unused agent first
        available_agents = [ua for ua in agents if ua not in self.used_agents]

        if not available_agents:
            # Reset if all used
            self.used_agents.clear()
            available_agents = agents

        agent = random.choice(available_agents)
        self.used_agents.add(agent)

        return agent

    def get_matching_headers(self, user_agent: str) -> dict[str, str]:
        """Get headers that match the user agent"""

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

        # Add browser-specific headers
        if "Chrome" in user_agent:
            headers.update(
                {
                    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                }
            )
        elif "Firefox" in user_agent:
            headers.update({"Sec-GPC": "1"})
        elif "Safari" in user_agent and "Chrome" not in user_agent:
            # Remove Chrome-specific headers for Safari
            headers.pop("Sec-Fetch-Dest", None)
            headers.pop("Sec-Fetch-Mode", None)
            headers.pop("Sec-Fetch-Site", None)
            headers.pop("Sec-Fetch-User", None)

        return headers


class ProxyRotator:
    """Proxy rotation and management"""

    def __init__(self, proxy_list: list[str] | None = None):
        self.proxy_list = proxy_list or []
        self.current_index = 0
        self.failed_proxies = set()
        self.proxy_stats = {}

    def add_proxy(self, proxy: str):
        """Add proxy to rotation"""
        if proxy not in self.proxy_list:
            self.proxy_list.append(proxy)
            self.proxy_stats[proxy] = {
                "requests": 0,
                "failures": 0,
                "last_used": None,
                "avg_latency": 0,
            }

    def get_next_proxy(self) -> str | None:
        """Get next available proxy"""

        if not self.proxy_list:
            return None

        # Filter out failed proxies
        available_proxies = [p for p in self.proxy_list if p not in self.failed_proxies]

        if not available_proxies:
            # Reset failed proxies if all failed
            self.failed_proxies.clear()
            available_proxies = self.proxy_list

        if not available_proxies:
            return None

        # Round-robin selection
        proxy = available_proxies[self.current_index % len(available_proxies)]
        self.current_index += 1

        return proxy

    def mark_proxy_failed(self, proxy: str):
        """Mark proxy as failed"""
        self.failed_proxies.add(proxy)
        if proxy in self.proxy_stats:
            self.proxy_stats[proxy]["failures"] += 1

    def update_proxy_stats(self, proxy: str, latency: float):
        """Update proxy performance stats"""
        if proxy in self.proxy_stats:
            stats = self.proxy_stats[proxy]
            stats["requests"] += 1
            stats["last_used"] = datetime.now().isoformat()

            # Update average latency
            current_avg = stats["avg_latency"]
            requests = stats["requests"]
            stats["avg_latency"] = ((current_avg * (requests - 1)) + latency) / requests


class StealthBrowser:
    """Stealth browser with advanced anti-detection"""

    def __init__(self, detection_level: DetectionLevel = DetectionLevel.STANDARD):
        self.detection_level = detection_level
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.ua_manager = UserAgentManager()
        self.viewport_sizes = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1536, "height": 864},
            {"width": 1440, "height": 900},
            {"width": 1280, "height": 720},
        ]

    async def initialize(self, headless: bool = True, mobile: bool = False):
        """Initialize stealth browser"""

        playwright = await async_playwright().start()

        # Browser launch arguments for stealth
        launch_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--disable-gpu",
            "--window-size=1920,1080",
        ]

        if self.detection_level in [DetectionLevel.AGGRESSIVE, DetectionLevel.PARANOID]:
            launch_args.extend(
                [
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--disable-background-networking",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                    "--disable-field-trial-config",
                    "--disable-ipc-flooding-protection",
                    "--no-default-browser-check",
                    "--no-first-run",
                    "--disable-default-apps",
                ]
            )

        # Choose browser based on detection level
        if self.detection_level == DetectionLevel.PARANOID:
            # Use Firefox for maximum stealth
            self.browser = await playwright.firefox.launch(headless=headless, args=launch_args)
        else:
            self.browser = await playwright.chromium.launch(headless=headless, args=launch_args)

        # Create context with stealth settings
        user_agent = self.ua_manager.get_random_agent(mobile=mobile)
        viewport = random.choice(self.viewport_sizes)

        context_options = {
            "user_agent": user_agent,
            "viewport": viewport,
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "permissions": [],
            "extra_http_headers": self.ua_manager.get_matching_headers(user_agent),
            "ignore_https_errors": True,
        }

        if mobile:
            context_options["is_mobile"] = True
            context_options["has_touch"] = True

        self.context = await self.browser.new_context(**context_options)

        # Add stealth scripts to context
        await self._add_stealth_scripts()

    async def _add_stealth_scripts(self):
        """Add anti-detection scripts"""

        # WebDriver detection evasion
        webdriver_script = """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        """

        # Chrome runtime evasion
        chrome_script = """
        window.chrome = {
            runtime: {},
        };
        """

        # Permissions evasion
        permissions_script = """
        const originalQuery = window.navigator.permissions.query;
        return window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Cypress.config('granted') }) :
                originalQuery(parameters)
        );
        """

        # Plugin evasion
        plugins_script = """
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        """

        # Languages evasion
        languages_script = """
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        """

        scripts = [
            webdriver_script,
            chrome_script,
            permissions_script,
            plugins_script,
            languages_script,
        ]

        if self.detection_level in [DetectionLevel.AGGRESSIVE, DetectionLevel.PARANOID]:
            # Additional advanced evasion
            advanced_script = """
            // Randomize canvas fingerprinting
            const getContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(contextType, contextAttributes) {
                if (contextType === '2d') {
                    const context = getContext.call(this, contextType, contextAttributes);
                    const originalImageData = context.getImageData;
                    context.getImageData = function(sx, sy, sw, sh) {
                        const imageData = originalImageData.apply(this, arguments);
                        for (let i = 0; i < imageData.data.length; i += 4) {
                            imageData.data[i] += Math.floor(Math.random() * 10) - 5;
                            imageData.data[i + 1] += Math.floor(Math.random() * 10) - 5;
                            imageData.data[i + 2] += Math.floor(Math.random() * 10) - 5;
                        }
                        return imageData;
                    };
                    return context;
                }
                return getContext.call(this, contextType, contextAttributes);
            };

            // Randomize WebGL fingerprinting
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel(R) Iris(TM) Graphics 6100';
                }
                return getParameter.call(this, parameter);
            };
            """
            scripts.append(advanced_script)

        # Add all scripts to context
        for script in scripts:
            await self.context.add_init_script(script)

    async def new_page(self) -> Page:
        """Create new page with randomized settings"""

        if not self.context:
            raise RuntimeError("Browser not initialized")

        page = await self.context.new_page()

        # Randomize timing
        if self.detection_level in [DetectionLevel.AGGRESSIVE, DetectionLevel.PARANOID]:
            # Add random delays to mouse movements
            await page.evaluate(
                """
                const originalAddEventListener = EventTarget.prototype.addEventListener;
                EventTarget.prototype.addEventListener = function(type, listener, options) {
                    if (type === 'mousemove') {
                        const wrappedListener = function(event) {
                            setTimeout(() => listener.call(this, event), Math.random() * 10);
                        };
                        return originalAddEventListener.call(this, type, wrappedListener, options);
                    }
                    return originalAddEventListener.call(this, type, listener, options);
                };
            """
            )

        return page

    async def close(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()


class AdvancedScraper:
    """Advanced web scraper with intelligent anti-detection"""

    def __init__(self):
        self.stealth_browser: StealthBrowser | None = None
        self.proxy_rotator = ProxyRotator()
        self.ua_manager = UserAgentManager()
        self.session = None
        self.request_history = []
        self.rate_limit_delays = {}

        # Setup requests session with retries
        self.setup_requests_session()

    def setup_requests_session(self):
        """Setup requests session with advanced configuration"""

        self.session = requests.Session()

        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    async def scrape_target(self, target: ScrapingTarget) -> ScrapingResult:
        """Scrape a target with the specified strategy"""

        start_time = time.time()

        try:
            # Apply rate limiting
            await self._apply_rate_limit(target.url, target.rate_limit)

            # Choose scraping method based on strategy
            if target.strategy == ScrapingStrategy.REQUESTS:
                result_data = await self._scrape_with_requests(target)
            elif target.strategy in [
                ScrapingStrategy.PLAYWRIGHT,
                ScrapingStrategy.STEALTH,
            ]:
                result_data = await self._scrape_with_playwright(target)
            elif target.strategy == ScrapingStrategy.MOBILE:
                result_data = await self._scrape_mobile(target)
            else:
                result_data = await self._scrape_with_playwright(target)

            duration_ms = (time.time() - start_time) * 1000

            return ScrapingResult(
                target=target.name,
                success=True,
                data=result_data,
                metadata={
                    "strategy": target.strategy.value,
                    "detection_level": target.detection_level.value,
                    "url": target.url,
                },
                timestamp=datetime.now(),
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            logging.error(f"Scraping failed for {target.name}: {e!s}")

            return ScrapingResult(
                target=target.name,
                success=False,
                data={},
                metadata={"strategy": target.strategy.value, "url": target.url},
                timestamp=datetime.now(),
                duration_ms=duration_ms,
                error=str(e),
            )

    async def _apply_rate_limit(self, url: str, rate_limit: float):
        """Apply intelligent rate limiting"""

        domain = urlparse(url).netloc

        if domain in self.rate_limit_delays:
            last_request = self.rate_limit_delays[domain]
            elapsed = time.time() - last_request

            if elapsed < rate_limit:
                delay = rate_limit - elapsed
                # Add some jitter to avoid patterns
                jitter = random.uniform(0.1, 0.5)
                await asyncio.sleep(delay + jitter)

        self.rate_limit_delays[domain] = time.time()

    async def _scrape_with_requests(self, target: ScrapingTarget) -> dict[str, Any]:
        """Scrape using requests library"""

        headers = self.ua_manager.get_matching_headers(self.ua_manager.get_random_agent())
        headers.update(target.custom_headers)

        # Use proxy if available
        proxies = {}
        if target.proxy:
            proxies = {"http": target.proxy, "https": target.proxy}

        response = self.session.get(
            target.url,
            headers=headers,
            proxies=proxies,
            timeout=target.timeout,
            allow_redirects=True,
        )

        response.raise_for_status()

        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        return self._extract_data_with_selectors(soup, target.selectors)

    async def _scrape_with_playwright(self, target: ScrapingTarget) -> dict[str, Any]:
        """Scrape using Playwright with stealth mode"""

        if not self.stealth_browser:
            self.stealth_browser = StealthBrowser(target.detection_level)
            await self.stealth_browser.initialize()

        page = await self.stealth_browser.new_page()

        try:
            # Set extra headers if needed
            if target.custom_headers:
                await page.set_extra_http_headers(target.custom_headers)

            # Navigate with random delay patterns
            if target.detection_level in [
                DetectionLevel.AGGRESSIVE,
                DetectionLevel.PARANOID,
            ]:
                # Simulate human-like behavior
                await page.goto(target.url, wait_until="networkidle")

                # Random mouse movements
                for _ in range(random.randint(1, 3)):
                    x = random.randint(100, 800)
                    y = random.randint(100, 600)
                    await page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.1, 0.5))

                # Random scroll
                await page.evaluate(f"window.scrollTo(0, {random.randint(100, 500)})")
                await asyncio.sleep(random.uniform(0.5, 2.0))
            else:
                await page.goto(
                    target.url,
                    wait_until="domcontentloaded",
                    timeout=target.timeout * 1000,
                )

            # Extract data using selectors
            data = {}

            for key, selector in target.selectors.items():
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        elements = await page.locator(f"xpath={selector}").all()
                        data[key] = [await el.inner_text() for el in elements]
                    else:
                        # CSS selector
                        elements = await page.locator(selector).all()
                        if len(elements) == 1:
                            data[key] = await elements[0].inner_text()
                        else:
                            data[key] = [await el.inner_text() for el in elements]

                except Exception as e:
                    logging.warning(f"Failed to extract {key} with selector {selector}: {e}")
                    data[key] = None

            return data

        finally:
            await page.close()

    async def _scrape_mobile(self, target: ScrapingTarget) -> dict[str, Any]:
        """Scrape with mobile user agent and viewport"""

        stealth_browser = StealthBrowser(target.detection_level)
        await stealth_browser.initialize(mobile=True)

        page = await stealth_browser.new_page()

        try:
            await page.goto(target.url, wait_until="networkidle", timeout=target.timeout * 1000)

            # Mobile-specific interactions
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
            await asyncio.sleep(1)

            data = {}
            for key, selector in target.selectors.items():
                try:
                    element = await page.locator(selector).first
                    data[key] = await element.inner_text() if element else None
                except:
                    data[key] = None

            return data

        finally:
            await page.close()
            await stealth_browser.close()

    def _extract_data_with_selectors(
        self, soup: BeautifulSoup, selectors: dict[str, str]
    ) -> dict[str, Any]:
        """Extract data using CSS selectors with BeautifulSoup"""

        data = {}

        for key, selector in selectors.items():
            try:
                elements = soup.select(selector)

                if len(elements) == 0:
                    data[key] = None
                elif len(elements) == 1:
                    data[key] = elements[0].get_text(strip=True)
                else:
                    data[key] = [el.get_text(strip=True) for el in elements]

            except Exception as e:
                logging.warning(f"Failed to extract {key} with selector {selector}: {e}")
                data[key] = None

        return data

    async def close(self):
        """Cleanup resources"""
        if self.stealth_browser:
            await self.stealth_browser.close()

        if self.session:
            self.session.close()


# Sports betting specific scrapers
class SportsbookScraper(AdvancedScraper):
    """Specialized scraper for sportsbook odds"""

    def __init__(self):
        super().__init__()
        self.sportsbook_configs = {
            "draftkings": ScrapingTarget(
                url="https://sportsbook.draftkings.com/leagues/basketball/nba",
                name="DraftKings NBA",
                selectors={
                    "games": ".sportsbook-table tbody tr",
                    "teams": ".event-cell__name",
                    "odds": ".sportsbook-odds",
                },
                strategy=ScrapingStrategy.STEALTH,
                detection_level=DetectionLevel.AGGRESSIVE,
                rate_limit=2.0,
            ),
            "fanduel": ScrapingTarget(
                url="https://sportsbook.fanduel.com/basketball/nba",
                name="FanDuel NBA",
                selectors={
                    "games": '[data-test-id="MarketGrid"]',
                    "teams": '[data-test-id="TeamName"]',
                    "odds": '[data-test-id="OddsButton"]',
                },
                strategy=ScrapingStrategy.STEALTH,
                detection_level=DetectionLevel.AGGRESSIVE,
                rate_limit=3.0,
            ),
        }

    async def scrape_all_sportsbooks(self) -> list[ScrapingResult]:
        """Scrape all configured sportsbooks"""

        results = []

        for name, config in self.sportsbook_configs.items():
            try:
                result = await self.scrape_target(config)
                results.append(result)

                logging.info(f"Scraped {name}: {'Success' if result.success else 'Failed'}")

            except Exception as e:
                logging.error(f"Failed to scrape {name}: {e}")

        return results


async def main():
    """Demonstrate advanced web scraping"""

    setup_utf8_logging()
    logging.info("🕷️  Starting Advanced Web Scraping System")

    # Initialize scraper
    scraper = SportsbookScraper()

    # Example scraping target
    test_target = ScrapingTarget(
        url="https://httpbin.org/json",
        name="HTTPBin Test",
        selectors={"title": "title"},
        strategy=ScrapingStrategy.REQUESTS,
        detection_level=DetectionLevel.MINIMAL,
    )

    # Test basic scraping
    result = await scraper.scrape_target(test_target)
    print(f"✅ Test scraping: {'Success' if result.success else 'Failed'}")
    print(f"Duration: {result.duration_ms:.1f}ms")

    # Test sportsbook scraping (mock)
    logging.info("Testing sportsbook scraping patterns...")

    # Cleanup
    await scraper.close()

    print("\n🎉 Advanced Web Scraping System Ready!")


if __name__ == "__main__":
    asyncio.run(main())
