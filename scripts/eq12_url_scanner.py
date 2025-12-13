#!/usr/bin/env python3
"""
EQ12 Intelligent URL Scanner and Learning System
Automatically scans URLs, extracts information, learns from content,
and updates EQ12 folders based on intelligent analysis.

Author: EQ12 AI System
Version: 1.0.0
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import feedparser

# Web scraping and parsing
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# AI and NLP
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
    # GPT-5 and latest model support
    OPENAI_MODELS = {
        "gpt-5": "gpt-5",  # GPT-5 when available
        "gpt-4-turbo": "gpt-4-turbo-preview",
        "gpt-4": "gpt-4",
        "gpt-3.5-turbo": "gpt-3.5-turbo",
        "o1-preview": "o1-preview",  # Latest reasoning model
        "o1-mini": "o1-mini",  # Fast reasoning model
    }
except ImportError:
    OPENAI_AVAILABLE = False
    OPENAI_MODELS = {}
    print("Warning: OpenAI not available. Install with: pip install openai>=1.3.0")

# Text processing
try:
    from transformers import pipeline

    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("Warning: Transformers not available. Install with: pip install transformers")

# EQ12 imports
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/url_scanner.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("EQ12URLScanner")


# Data models
@dataclass
class URLScanResult:
    """Result of URL scanning operation"""

    url: str
    title: str
    content: str
    metadata: dict[str, Any]
    extracted_data: dict[str, Any]
    classification: str
    confidence: float
    scan_timestamp: str
    processing_time: float
    error: str | None = None


@dataclass
class LearningInsight:
    """Insight learned from URL content"""

    insight_id: str
    category: str
    description: str
    confidence: float
    source_url: str
    applicable_folders: list[str]
    update_actions: list[dict[str, Any]]
    created_at: str


@dataclass
class EQ12FolderUpdate:
    """Update to be applied to EQ12 folders"""

    folder_path: str
    update_type: str  # create, modify, append, delete
    file_name: str
    content: str
    metadata: dict[str, Any]
    priority: int
    created_at: str


class EQ12URLScanner:
    """Main URL scanner and learning system"""

    def __init__(self):
        self.db_path = "C:/EQ12/url_scanner.db"
        self.data_dir = "C:/EQ12/data/url_scanner"
        self.logs_dir = "C:/EQ12/logs"

        # Initialize directories
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

        # Initialize database
        self._init_database()

        # Initialize AI clients with GPT-5 support
        self.openai_client = None
        self.openai_model = self._get_best_available_model()
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            try:
                self.openai_client = OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY"), max_retries=0, timeout=30.0
                )
                logger.info(
                    f"OpenAI client initialized with model: {
                        self.openai_model}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None

        # Initialize HuggingFace pipelines
        self.classifier = None
        self.summarizer = None
        if HF_AVAILABLE:
            try:
                self.classifier = pipeline(
                    "text-classification",
                    model="facebook/bart-large-mnli")
                self.summarizer = pipeline(
                    "summarization", model="facebook/bart-large-cnn")
            except Exception as e:
                logger.warning(f"Failed to load HF models: {e}")

        # EQ12 folder mappings
        self.eq12_folders = {
            "betting": ["scripts", "EdgeGodParlays", "scraper_starter"],
            "automation": ["scripts", "omni_scraper", "modules"],
            "finance": ["data", "configs"],
            "ai": ["openai-python-project", "scripts"],
            "dashboard": ["dashboard", "logs"],
            "config": ["configs", "keys"],
            "data": ["data", "logs"],
        }

    def _get_best_available_model(self) -> str:
        """Determine the best available OpenAI model based on environment and capabilities"""
        # Check for explicit model preference
        preferred_model = os.getenv("EQ12_OPENAI_MODEL")
        if preferred_model and OPENAI_AVAILABLE and preferred_model in OPENAI_MODELS:
            return OPENAI_MODELS[preferred_model]

        # Auto-detect best available model (preference order)
        model_priority = [
            "gpt-5",  # GPT-5 (when available)
            "o1-preview",  # Latest reasoning model
            "gpt-4-turbo",  # GPT-4 Turbo
            "gpt-4",  # GPT-4
            "o1-mini",  # Fast reasoning
            "gpt-3.5-turbo",  # Fallback
        ]

        if OPENAI_AVAILABLE:
            for model_key in model_priority:
                if model_key in OPENAI_MODELS:
                    return OPENAI_MODELS[model_key]

        return "gpt-4o-mini"  # Final fallback

    def _init_database(self):
        """Initialize SQLite database for URL scanner"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # URL scan results table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS url_scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT,
                    content_hash TEXT,
                    classification TEXT,
                    confidence REAL,
                    scan_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    processing_time REAL,
                    metadata TEXT,
                    extracted_data TEXT,
                    error TEXT
                )
            """
            )

            # Learning insights table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_id TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    confidence REAL,
                    source_url TEXT,
                    applicable_folders TEXT,
                    update_actions TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    applied BOOLEAN DEFAULT FALSE
                )
            """
            )

            # EQ12 folder updates table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS eq12_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    update_id TEXT UNIQUE NOT NULL,
                    folder_path TEXT NOT NULL,
                    update_type TEXT NOT NULL,
                    file_name TEXT,
                    content_hash TEXT,
                    priority INTEGER DEFAULT 5,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    applied_at DATETIME,
                    metadata TEXT
                )
            """
            )

            # URL submission log
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS url_submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    submitted_by TEXT,
                    submission_method TEXT,
                    processed BOOLEAN DEFAULT FALSE,
                    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    processed_at DATETIME
                )
            """
            )

            conn.commit()
            conn.close()
            logger.info("URL scanner database initialized")

        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    async def scan_url(self, url: str) -> URLScanResult:
        """Scan a single URL and extract information"""
        start_time = time.time()

        try:
            logger.info(f"Scanning URL: {url}")

            # Validate URL
            if not self._is_valid_url(url):
                raise ValueError(f"Invalid URL format: {url}")

            # Check if already scanned recently
            if self._is_recently_scanned(url):
                logger.info(f"URL recently scanned, using cached data: {url}")
                return self._get_cached_scan(url)

            # Extract content
            content_data = await self._extract_url_content(url)

            # Classify content
            classification, confidence = await self._classify_content(
                content_data["title"], content_data["content"]
            )

            # Extract structured data
            extracted_data = await self._extract_structured_data(
                url, content_data["content"], content_data["soup"]
            )

            # Create result
            scan_result = URLScanResult(
                url=url,
                title=content_data["title"],
                content=content_data["content"][:5000],  # Truncate for storage
                metadata=content_data["metadata"],
                extracted_data=extracted_data,
                classification=classification,
                confidence=confidence,
                scan_timestamp=datetime.now(UTC).isoformat(),
                processing_time=time.time() - start_time,
            )

            # Store in database
            self._store_scan_result(scan_result)

            logger.info(
                f"URL scan completed: {url} -> {classification} ({confidence:.2f})")
            return scan_result

        except Exception as e:
            error_msg = f"Error scanning URL {url}: {e}"
            logger.error(error_msg)

            return URLScanResult(
                url=url,
                title="",
                content="",
                metadata={},
                extracted_data={},
                classification="error",
                confidence=0.0,
                scan_timestamp=datetime.now(UTC).isoformat(),
                processing_time=time.time() - start_time,
                error=error_msg,
            )

    async def _extract_url_content(self, url: str) -> dict[str, Any]:
        """Extract content from URL using multiple methods"""

        # Method 1: Try with httpx first (fast)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")

                # Extract basic content
                title = self._extract_title(soup)
                content = self._extract_text_content(soup)
                metadata = self._extract_metadata(soup, response)

                if content.strip():
                    return {
                        "title": title,
                        "content": content,
                        "soup": soup,
                        "metadata": metadata,
                        "method": "httpx",
                    }

        except Exception as e:
            logger.warning(f"httpx extraction failed for {url}: {e}")

        # Method 2: Try with Playwright for dynamic content
        try:
            content_data = await self._extract_with_playwright(url)
            if content_data:
                return content_data
        except Exception as e:
            logger.warning(f"Playwright extraction failed for {url}: {e}")

        # Method 3: Try RSS feed parsing
        try:
            if any(keyword in url.lower() for keyword in ["rss", "feed", "xml"]):
                return self._extract_from_feed(url)
        except Exception as e:
            logger.warning(f"Feed extraction failed for {url}: {e}")

        raise Exception("All extraction methods failed")

    async def _extract_with_playwright(self, url: str) -> dict[str, Any] | None:
        """Extract content using Playwright for dynamic sites"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(url, wait_until="networkidle", timeout=30000)

                # Get page content
                content = await page.content()
                title = await page.title()

                soup = BeautifulSoup(content, "html.parser")
                text_content = self._extract_text_content(soup)
                metadata = {"method": "playwright", "title": title}

                await browser.close()

                return {
                    "title": title,
                    "content": text_content,
                    "soup": soup,
                    "metadata": metadata,
                    "method": "playwright",
                }

        except Exception as e:
            logger.error(f"Playwright extraction error: {e}")
            return None

    def _extract_from_feed(self, url: str) -> dict[str, Any]:
        """Extract content from RSS/Atom feeds"""
        feed = feedparser.parse(url)

        if feed.bozo:
            raise Exception("Invalid feed format")

        # Combine feed entries into content
        content_parts = []
        for entry in feed.entries[:10]:  # Limit to 10 entries
            content_parts.append(f"{entry.title}: {entry.summary}")

        return {
            "title": feed.feed.get("title", "RSS Feed"),
            "content": "\n\n".join(content_parts),
            "soup": None,
            "metadata": {
                "method": "feedparser",
                "feed_title": feed.feed.get("title", ""),
                "entry_count": len(feed.entries),
            },
        }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try multiple title sources
        title_selectors = [
            "h1",
            "title",
            '[property="og:title"]',
            '[name="twitter:title"]',
            ".title",
            ".headline",
        ]

        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = (
                    element.get_text(strip=True)
                    if selector in ["h1", "title"]
                    else element.get("content", "")
                )
                if title:
                    return title[:200]  # Limit length

        return "No Title Found"

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract meaningful text content"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Focus on main content areas
        content_selectors = [
            "article",
            "main",
            ".content",
            ".post-content",
            ".entry-content",
            "#content",
            "body",
        ]

        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(separator="\n", strip=True)
                if len(text) > 100:
                    return text[:10000]  # Limit to 10k chars

        # Fallback to body text
        return soup.get_text(separator="\n", strip=True)[:10000]

    def _extract_metadata(self, soup: BeautifulSoup, response=None) -> dict[str, Any]:
        """Extract metadata from page"""
        metadata = {}

        # Meta tags
        meta_tags = {
            "description": ["name='description'", "property='og:description'"],
            "keywords": ["name='keywords'"],
            "author": ["name='author'"],
            "published": [
                "name='article:published_time'",
                "property='article:published_time'",
            ],
            "image": ["property='og:image'", "name='twitter:image'"],
        }

        for key, selectors in meta_tags.items():
            for selector in selectors:
                element = soup.select_one(f"meta[{selector}]")
                if element:
                    metadata[key] = element.get("content", "")
                    break

        # Response metadata
        if response:
            metadata.update(
                {
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type", ""),
                    "content_length": len(response.content),
                }
            )

        return metadata

    async def _classify_content(self, title: str, content: str) -> tuple[str, float]:
        """Classify content into EQ12 categories"""

        # Combine title and content for classification
        text = f"{title}\n{content}"[:1000]  # Limit for processing

        # Define EQ12 categories and keywords
        categories = {
            "betting": [
                "bet",
                "odds",
                "sportsbook",
                "parlay",
                "gambling",
                "wager",
                "spread",
                "moneyline",
            ],
            "automation": [
                "automation",
                "script",
                "bot",
                "scraper",
                "api",
                "webhook",
                "integration",
            ],
            "finance": [
                "stock",
                "crypto",
                "portfolio",
                "investment",
                "trading",
                "market",
                "price",
            ],
            "ai": [
                "ai",
                "machine learning",
                "gpt",
                "openai",
                "model",
                "nlp",
                "chatbot",
            ],
            "dashboard": [
                "dashboard",
                "analytics",
                "metrics",
                "monitoring",
                "visualization",
            ],
            "config": [
                "config",
                "settings",
                "environment",
                "variables",
                "keys",
                "credentials",
            ],
            "data": ["data", "database", "json", "csv", "export", "import", "analysis"],
        }

        # Method 1: Keyword-based classification
        keyword_scores = {}
        text_lower = text.lower()

        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            keyword_scores[category] = score / len(keywords)

        # Method 2: AI-based classification if available
        ai_scores = {}
        if self.openai_client:
            try:
                ai_category, ai_confidence = await self._classify_with_openai(text)
                if ai_category in categories:
                    ai_scores[ai_category] = ai_confidence
            except Exception as e:
                logger.warning(f"OpenAI classification failed: {e}")

        # Method 3: HuggingFace classification if available
        hf_scores = {}
        if self.classifier:
            try:
                for category in categories:
                    result = self.classifier(text, [f"This is about {category}"])
                    hf_scores[category] = result["scores"][0]
            except Exception as e:
                logger.warning(f"HF classification failed: {e}")

        # Combine scores
        final_scores = {}
        for category in categories:
            score = (
                keyword_scores.get(category, 0) * 0.4
                + ai_scores.get(category, 0) * 0.4
                + hf_scores.get(category, 0) * 0.2
            )
            final_scores[category] = score

        # Get best classification
        if final_scores:
            best_category = max(final_scores, key=final_scores.get)
            confidence = final_scores[best_category]

            # Require minimum confidence
            if confidence > 0.1:
                return best_category, confidence

        return "general", 0.1

    async def _classify_with_openai(self, text: str) -> tuple[str, float]:
        """Classify content using OpenAI"""
        prompt = """
        Classify this content into one of these categories for the EQ12 automation system:
        - betting: Sports betting, odds, parlays, gambling
        - automation: Scripts, bots, automation tools
        - finance: Stocks, crypto, trading, investments
        - ai: AI, machine learning, GPT, models
        - dashboard: Analytics, dashboards, monitoring
        - config: Configuration, settings, environment
        - data: Data analysis, databases, exports

        Content: {text}

        Respond with just the category name and confidence (0.0-1.0) like: "betting 0.85"
        """

        response = await self.openai_client.chat.completions.create(
            model=self.openai_model or "gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.3,
        )

        result = response.choices[0].message.content.strip().split()
        category = result[0]
        confidence = float(result[1]) if len(result) > 1 else 0.5

        return category, confidence

    async def _extract_structured_data(
        self, url: str, content: str, soup: BeautifulSoup | None
    ) -> dict[str, Any]:
        """Extract structured data specific to EQ12 needs"""
        extracted = {}

        # Extract URLs and links
        if soup:
            links = []
            for link in soup.find_all("a", href=True):
                href = urljoin(url, link["href"])
                links.append(
                    {
                        "url": href,
                        "text": link.get_text(strip=True)[:100],
                        "title": link.get("title", ""),
                    }
                )
            extracted["links"] = links[:20]  # Limit to 20 links

        # Extract code snippets
        code_patterns = [
            r"```[\s\S]*?```",  # Markdown code blocks
            r"<code>[\s\S]*?</code>",  # HTML code tags
            r"<pre>[\s\S]*?</pre>",  # Pre tags
        ]

        code_snippets = []
        for pattern in code_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            code_snippets.extend(matches[:5])  # Limit snippets

        if code_snippets:
            extracted["code_snippets"] = code_snippets

        # Extract API endpoints
        api_patterns = [
            r"https?://[^\s]+/api/[^\s]+",
            r"/api/[a-zA-Z0-9/_-]+",
            r"POST|GET|PUT|DELETE\s+[/\w-]+",
        ]

        api_endpoints = []
        for pattern in api_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            api_endpoints.extend(matches[:10])

        if api_endpoints:
            extracted["api_endpoints"] = api_endpoints

        # Extract configuration data
        config_patterns = [
            r"[A-Z_]+_API_KEY",
            r"[A-Z_]+_TOKEN",
            r"config\.[a-zA-Z_]+",
            r"env\.[A-Z_]+",
        ]

        config_items = []
        for pattern in config_patterns:
            matches = re.findall(pattern, content)
            config_items.extend(matches[:10])

        if config_items:
            extracted["config_items"] = list(set(config_items))

        # Extract betting-related data
        betting_patterns = [
            r"[-+]?\d+\.?\d*\s*odds",
            r"spread\s*[-+]?\d+\.?\d*",
            r"\$\d+\.?\d*\s*bet",
            r"parlay\s*\d+",
        ]

        betting_data = []
        for pattern in betting_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            betting_data.extend(matches[:5])

        if betting_data:
            extracted["betting_data"] = betting_data

        return extracted

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except BaseException:
            return False

    def _is_recently_scanned(self, url: str, hours: int = 24) -> bool:
        """Check if URL was scanned recently"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT scan_timestamp FROM url_scans
                WHERE url = ?
                ORDER BY scan_timestamp DESC
                LIMIT 1
            """,
                (url,),
            )

            result = cursor.fetchone()
            conn.close()

            if result:
                last_scan = datetime.fromisoformat(result[0])
                age = datetime.now(UTC) - last_scan
                return age.total_seconds() < hours * 3600

            return False
        except BaseException:
            return False

    def _get_cached_scan(self, url: str) -> URLScanResult:
        """Get cached scan result"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM url_scans
                WHERE url = ?
                ORDER BY scan_timestamp DESC
                LIMIT 1
            """,
                (url,),
            )

            row = cursor.fetchone()
            conn.close()

            if row:
                return URLScanResult(
                    url=row[1],
                    title=row[2] or "",
                    content="[Cached result]",
                    metadata=json.loads(row[8] or "{}"),
                    extracted_data=json.loads(row[9] or "{}"),
                    classification=row[4] or "general",
                    confidence=row[5] or 0.0,
                    scan_timestamp=row[6],
                    processing_time=row[7] or 0.0,
                )
        except Exception as e:
            logger.error(f"Error getting cached scan: {e}")

        # Fallback
        return URLScanResult(
            url=url,
            title="Cached (Error)",
            content="",
            metadata={},
            extracted_data={},
            classification="error",
            confidence=0.0,
            scan_timestamp=datetime.now(UTC).isoformat(),
            processing_time=0.0,
        )

    def _store_scan_result(self, result: URLScanResult):
        """Store scan result in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            content_hash = hashlib.md5(result.content.encode()).hexdigest()

            cursor.execute(
                """
                INSERT OR REPLACE INTO url_scans
                (url, title, content_hash, classification, confidence,
                 scan_timestamp, processing_time, metadata, extracted_data, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    result.url,
                    result.title,
                    content_hash,
                    result.classification,
                    result.confidence,
                    result.scan_timestamp,
                    result.processing_time,
                    json.dumps(result.metadata),
                    json.dumps(result.extracted_data),
                    result.error,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error storing scan result: {e}")

    async def learn_from_scan(
            self,
            scan_result: URLScanResult) -> list[LearningInsight]:
        """Generate learning insights from scan result"""
        insights = []

        try:
            # Generate insights based on classification and content
            if scan_result.classification == "betting":
                insights.extend(await self._generate_betting_insights(scan_result))
            elif scan_result.classification == "automation":
                insights.extend(await self._generate_automation_insights(scan_result))
            elif scan_result.classification == "finance":
                insights.extend(await self._generate_finance_insights(scan_result))
            elif scan_result.classification == "ai":
                insights.extend(await self._generate_ai_insights(scan_result))

            # General insights for all content
            insights.extend(await self._generate_general_insights(scan_result))

            # Store insights
            for insight in insights:
                self._store_learning_insight(insight)

            logger.info(f"Generated {len(insights)} insights from {scan_result.url}")
            return insights

        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []

    async def _generate_betting_insights(
            self, scan_result: URLScanResult) -> list[LearningInsight]:
        """Generate betting-specific insights"""
        insights = []

        # Look for new sportsbooks or odds sources
        if "sportsbook" in scan_result.content.lower():
            insights.append(
                LearningInsight(
                    insight_id=f"betting_sportsbook_{hash(scan_result.url)}",
                    category="betting",
                    description=f"New sportsbook source found: {scan_result.title}",
                    confidence=0.8,
                    source_url=scan_result.url,
                    applicable_folders=["EdgeGodParlays", "scripts", "scraper_starter"],
                    update_actions=[
                        {
                            "action": "add_sportsbook_config",
                            "url": scan_result.url,
                            "title": scan_result.title,
                        }
                    ],
                    created_at=datetime.now(UTC).isoformat(),
                )
            )

        # Look for new betting strategies
        if any(term in scan_result.content.lower()
               for term in ["kelly", "edge", "value"]):
            insights.append(
                LearningInsight(
                    insight_id=f"betting_strategy_{hash(scan_result.url)}",
                    category="betting",
                    description=f"Betting strategy content found: {scan_result.title}",
                    confidence=0.7,
                    source_url=scan_result.url,
                    applicable_folders=["scripts", "EdgeGodParlays"],
                    update_actions=[
                        {
                            "action": "save_strategy_reference",
                            "content": scan_result.content[:500],
                        }
                    ],
                    created_at=datetime.now(UTC).isoformat(),
                )
            )

        return insights

    async def _generate_automation_insights(
        self, scan_result: URLScanResult
    ) -> list[LearningInsight]:
        """Generate automation-specific insights"""
        insights = []

        # Look for new APIs or integrations
        if "api_endpoints" in scan_result.extracted_data:
            insights.append(
                LearningInsight(
                    insight_id=f"automation_api_{hash(scan_result.url)}",
                    category="automation",
                    description=(
                        f"New API endpoints found: {len(scan_result.extracted_data['api_endpoints'])} endpoints",
                    )
                    confidence=0.9,
                    source_url=scan_result.url,
                    applicable_folders=["scripts", "omni_scraper"],
                    update_actions=[
                        {
                            "action": "add_api_config",
                            "endpoints": scan_result.extracted_data["api_endpoints"],
                        }
                    ],
                    created_at=datetime.now(UTC).isoformat(),
                )
            )

        return insights

    async def _generate_finance_insights(
            self, scan_result: URLScanResult) -> list[LearningInsight]:
        """Generate finance-specific insights"""
        insights = []

        # Look for new data sources
        if any(term in scan_result.content.lower() for term in ["api", "data", "feed"]):
            insights.append(
                LearningInsight(
                    insight_id=f"finance_data_{hash(scan_result.url)}",
                    category="finance",
                    description=f"Financial data source found: {scan_result.title}",
                    confidence=0.7,
                    source_url=scan_result.url,
                    applicable_folders=["data", "configs"],
                    update_actions=[{"action": "add_data_source", "url": scan_result.url}],
                    created_at=datetime.now(UTC).isoformat(),
                )
            )

        return insights

    async def _generate_ai_insights(
            self, scan_result: URLScanResult) -> list[LearningInsight]:
        """Generate AI-specific insights"""
        insights = []

        # Look for new models or techniques
        if any(term in scan_result.content.lower() for term in ["model", "gpt", "api"]):
            insights.append(
                LearningInsight(
                    insight_id=f"ai_model_{hash(scan_result.url)}",
                    category="ai",
                    description=f"AI model or technique found: {scan_result.title}",
                    confidence=0.6,
                    source_url=scan_result.url,
                    applicable_folders=["openai-python-project", "scripts"],
                    update_actions=[
                        {
                            "action": "save_ai_reference",
                            "content": scan_result.content[:500],
                        }
                    ],
                    created_at=datetime.now(UTC).isoformat(),
                )
            )

        return insights

    async def _generate_general_insights(
            self, scan_result: URLScanResult) -> list[LearningInsight]:
        """Generate general insights applicable to all content"""
        insights = []

        # Configuration insights
        if "config_items" in scan_result.extracted_data:
            insights.append(
                LearningInsight(
                    insight_id=f"config_{hash(scan_result.url)}",
                    category="config",
                    description=(
                        f"Configuration items found: {len(scan_result.extracted_data['config_items'])} items",
                    )
                    confidence=0.8,
                    source_url=scan_result.url,
                    applicable_folders=["configs"],
                    update_actions=[
                        {
                            "action": "update_config_template",
                            "items": scan_result.extracted_data["config_items"],
                        }
                    ],
                    created_at=datetime.now(UTC).isoformat(),
                )
            )

        return insights

    def _store_learning_insight(self, insight: LearningInsight):
        """Store learning insight in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO learning_insights
                (insight_id, category, description, confidence, source_url,
                 applicable_folders, update_actions, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    insight.insight_id,
                    insight.category,
                    insight.description,
                    insight.confidence,
                    insight.source_url,
                    json.dumps(insight.applicable_folders),
                    json.dumps(insight.update_actions),
                    insight.created_at,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error storing insight: {e}")

    async def apply_insights_to_eq12(
        self, insights: list[LearningInsight]
    ) -> list[EQ12FolderUpdate]:
        """Apply insights to update EQ12 folders"""
        updates = []

        for insight in insights:
            try:
                folder_updates = await self._generate_folder_updates(insight)
                updates.extend(folder_updates)

                # Mark insight as applied
                self._mark_insight_applied(insight.insight_id)

            except Exception as e:
                logger.error(f"Error applying insight {insight.insight_id}: {e}")

        # Apply updates to filesystem
        for update in updates:
            await self._apply_folder_update(update)

        logger.info(f"Applied {len(updates)} updates to EQ12 folders")
        return updates

    async def _generate_folder_updates(
            self, insight: LearningInsight) -> list[EQ12FolderUpdate]:
        """Generate folder updates from insight"""
        updates = []

        for action in insight.update_actions:
            action_type = action.get("action", "")

            if action_type == "add_sportsbook_config":
                updates.append(
                    EQ12FolderUpdate(
                        folder_path="C:/EQ12/configs",
                        update_type="append",
                        file_name="sportsbook_sources.json",
                        content=json.dumps(
                            {
                                "url": action["url"],
                                "title": action["title"],
                                "added_at": datetime.now(UTC).isoformat(),
                                "source_insight": insight.insight_id,
                            },
                            indent=2,
                        ),
                        metadata={"insight_id": insight.insight_id},
                        priority=7,
                        created_at=datetime.now(UTC).isoformat(),
                    )
                )

            elif action_type == "save_strategy_reference":
                updates.append(
                    EQ12FolderUpdate(
                        folder_path="C:/EQ12/data",
                        update_type="create",
                        file_name=f"strategy_ref_{insight.insight_id[-8:]}.md",
                        content=(
                            f"# Betting Strategy Reference\n\nSource: {insight.source_url}\n\n{action['content']}",
                        )
                        metadata={"insight_id": insight.insight_id},
                        priority=5,
                        created_at=datetime.now(UTC).isoformat(),
                    )
                )

            elif action_type == "add_api_config":
                updates.append(
                    EQ12FolderUpdate(
                        folder_path="C:/EQ12/configs",
                        update_type="append",
                        file_name="api_endpoints.json",
                        content=json.dumps(
                            {
                                "endpoints": action["endpoints"],
                                "source": insight.source_url,
                                "added_at": datetime.now(UTC).isoformat(),
                            },
                            indent=2,
                        ),
                        metadata={"insight_id": insight.insight_id},
                        priority=6,
                        created_at=datetime.now(UTC).isoformat(),
                    )
                )

            elif action_type == "update_config_template":
                config_content = "# Configuration Template\n\n"
                for item in action["items"]:
                    config_content += f"# {item}=your_value_here\n"

                updates.append(
                    EQ12FolderUpdate(
                        folder_path="C:/EQ12/configs",
                        update_type="modify",
                        file_name="config_template.env",
                        content=config_content,
                        metadata={"insight_id": insight.insight_id},
                        priority=3,
                        created_at=datetime.now(UTC).isoformat(),
                    )
                )

        return updates

    async def _apply_folder_update(self, update: EQ12FolderUpdate):
        """Apply update to filesystem"""
        try:
            # Ensure directory exists
            os.makedirs(update.folder_path, exist_ok=True)

            file_path = os.path.join(update.folder_path, update.file_name)

            if update.update_type == "create":
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(update.content)

            elif update.update_type == "append":
                # Load existing JSON and append
                existing_data = []
                if os.path.exists(file_path):
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            existing_data = json.load(f)
                    except BaseException:
                        existing_data = []

                if not isinstance(existing_data, list):
                    existing_data = [existing_data]

                new_data = json.loads(update.content)
                existing_data.append(new_data)

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(existing_data, f, indent=2)

            elif update.update_type == "modify":
                # Append to existing file
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(
                        f"\n# Added from URL scan: {
                            update.metadata.get(
                                'insight_id', '')}\n")
                    f.write(update.content)

            logger.info(f"Applied update: {update.update_type} -> {file_path}")

            # Store update record
            self._store_folder_update(update, "completed")

        except Exception as e:
            logger.error(f"Error applying folder update: {e}")
            self._store_folder_update(update, "failed")

    def _store_folder_update(self, update: EQ12FolderUpdate, status: str):
        """Store folder update record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            update_id = (
                f"update_{hash(f'{update.folder_path}{update.file_name}{update.created_at}')}"
            )
            content_hash = hashlib.md5(update.content.encode()).hexdigest()

            cursor.execute(
                """
                INSERT OR REPLACE INTO eq12_updates
                (update_id, folder_path, update_type, file_name, content_hash,
                 priority, status, created_at, applied_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    update_id,
                    update.folder_path,
                    update.update_type,
                    update.file_name,
                    content_hash,
                    update.priority,
                    status,
                    update.created_at,
                    datetime.now(UTC).isoformat() if status == "completed" else None,
                    json.dumps(update.metadata),
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error storing folder update: {e}")

    def _mark_insight_applied(self, insight_id: str):
        """Mark insight as applied"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE learning_insights
                SET applied = TRUE
                WHERE insight_id = ?
            """,
                (insight_id,),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error marking insight applied: {e}")

    async def process_url_submission(
        self, url: str, submitted_by: str = "copilot", submission_method: str = "auto"
    ) -> dict[str, Any]:
        """Process a URL submission from Copilot or other sources"""

        # Log submission
        self._log_url_submission(url, submitted_by, submission_method)

        try:
            # Scan URL
            scan_result = await self.scan_url(url)

            if scan_result.error:
                return {"success": False, "error": scan_result.error, "url": url}

            # Generate insights
            insights = await self.learn_from_scan(scan_result)

            # Apply insights to EQ12 folders
            updates = await self.apply_insights_to_eq12(insights)

            # Mark submission as processed
            self._mark_submission_processed(url)

            result = {
                "success": True,
                "url": url,
                "classification": scan_result.classification,
                "confidence": scan_result.confidence,
                "insights_generated": len(insights),
                "updates_applied": len(updates),
                "processing_time": scan_result.processing_time,
                "scan_result": asdict(scan_result),
                "insights": [asdict(insight) for insight in insights],
                "updates": [asdict(update) for update in updates],
            }

            logger.info(f"Successfully processed URL submission: {url}")
            return result

        except Exception as e:
            error_msg = f"Error processing URL submission: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "url": url}

    def _log_url_submission(self, url: str, submitted_by: str, submission_method: str):
        """Log URL submission"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO url_submissions
                (url, submitted_by, submission_method)
                VALUES (?, ?, ?)
            """,
                (url, submitted_by, submission_method),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error logging URL submission: {e}")

    def _mark_submission_processed(self, url: str):
        """Mark URL submission as processed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE url_submissions
                SET processed = TRUE, processed_at = ?
                WHERE url = ? AND processed = FALSE
            """,
                (datetime.now(UTC).isoformat(), url),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error marking submission processed: {e}")

    def get_scanner_status(self) -> dict[str, Any]:
        """Get current scanner status and statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get scan statistics
            cursor.execute(
                """
                SELECT
                    COUNT(*) as total_scans,
                    COUNT(DISTINCT classification) as categories,
                    AVG(confidence) as avg_confidence,
                    AVG(processing_time) as avg_processing_time
                FROM url_scans
                WHERE scan_timestamp > datetime('now', '-7 days')
            """
            )
            scan_stats = cursor.fetchone()

            # Get insight statistics
            cursor.execute(
                """
                SELECT
                    COUNT(*) as total_insights,
                    COUNT(CASE WHEN applied = TRUE THEN 1 END) as applied_insights,
                    COUNT(DISTINCT category) as insight_categories
                FROM learning_insights
                WHERE created_at > datetime('now', '-7 days')
            """
            )
            insight_stats = cursor.fetchone()

            # Get update statistics
            cursor.execute(
                """
                SELECT
                    COUNT(*) as total_updates,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_updates
                FROM eq12_updates
                WHERE created_at > datetime('now', '-7 days')
            """
            )
            update_stats = cursor.fetchone()

            conn.close()

            return {
                "status": "active",
                "last_7_days": {
                    "total_scans": scan_stats[0] or 0,
                    "categories_detected": scan_stats[1] or 0,
                    "average_confidence": scan_stats[2] or 0.0,
                    "average_processing_time": scan_stats[3] or 0.0,
                    "total_insights": insight_stats[0] or 0,
                    "applied_insights": insight_stats[1] or 0,
                    "insight_categories": insight_stats[2] or 0,
                    "total_updates": update_stats[0] or 0,
                    "completed_updates": update_stats[1] or 0,
                },
                "capabilities": {
                    "openai_available": OPENAI_AVAILABLE and bool(self.openai_client),
                    "huggingface_available": HF_AVAILABLE,
                    "playwright_available": True,
                    "supported_categories": list(self.eq12_folders.keys()),
                },
            }

        except Exception as e:
            logger.error(f"Error getting scanner status: {e}")
            return {"status": "error", "error": str(e)}


# Main entry point
async def main():
    """Main entry point for URL scanner"""
    scanner = EQ12URLScanner()

    # Test with a sample URL
    test_url = "https://github.com/microsoft/playwright"
    result = await scanner.process_url_submission(test_url, "test", "manual")

    print(f"Processing result: {json.dumps(result, indent=2)}")

    # Print status
    status = scanner.get_scanner_status()
    print(f"Scanner status: {json.dumps(status, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
