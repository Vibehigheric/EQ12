#!/usr/bin/env python3
"""
EQ12 GODSTACK - HTTP Web Retriever
Web scraping and API retriever implementation

Core Features:
- HTTP/HTTPS web page scraping
- REST API integration
- Content extraction and cleanup
- Rate limiting and retry logic
- Multiple user agents and proxies
"""

import asyncio
import html
import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

from .base_retriever import (
    BaseRetriever,
    RetrievalResult,
    RetrievalStatus,
    RetrievedDocument,
    SourceType,
)

# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class HTTPConfig:
    """HTTP retriever configuration"""

    # Request settings
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: int = 2

    # Content settings
    max_content_length: int = 1_000_000  # 1MB
    extract_text_only: bool = True
    follow_redirects: bool = True

    # Headers and user agents
    user_agents: list[str] = None
    custom_headers: dict[str, str] = None

    # Proxy settings
    proxies: list[str] = None
    rotate_proxies: bool = False

    # Content filtering
    allowed_domains: list[str] = None
    blocked_domains: list[str] = None
    content_types: list[str] = None

    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ]

        if self.custom_headers is None:
            self.custom_headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }

        if self.content_types is None:
            self.content_types = [
                "text/html",
                "application/json",
                "text/plain",
                "application/xml",
            ]


class HTTPRetriever(BaseRetriever):
    """HTTP-based web scraping and API retriever"""

    def __init__(self, name: str, config: dict[str, Any] | None = None):
        super().__init__(name, config)

        # HTTP-specific configuration
        self.http_config = HTTPConfig()

        # Override defaults with config
        if config:
            http_settings = config.get("http", {})
            for key, value in http_settings.items():
                if hasattr(self.http_config, key):
                    setattr(self.http_config, key, value)

        # Session for connection pooling
        self.session: aiohttp.ClientSession | None = None

        logger.info(f"HTTPRetriever initialized: {self.name}")

    async def _ensure_session(self):
        """Ensure aiohttp session is created"""

        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=10,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )

            timeout = aiohttp.ClientTimeout(total=self.http_config.timeout_seconds)

            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.http_config.custom_headers,
            )

    async def retrieve(self, query: str, max_results: int = 10, **kwargs) -> RetrievalResult:
        """Retrieve documents from HTTP sources"""

        start_time = datetime.now(UTC)

        # Check rate limiting
        if self.is_rate_limited():
            return RetrievalResult(
                retriever_name=self.name,
                query=query,
                status=RetrievalStatus.RATE_LIMITED,
                documents=[],
                total_found=0,
                total_returned=0,
                execution_time_ms=0,
                api_calls_made=0,
                cache_hits=0,
                error_message="Rate limited",
            )

        self.record_request()

        try:
            await self._ensure_session()

            # Determine URLs to fetch
            urls = self._get_urls_for_query(query, max_results, **kwargs)

            if not urls:
                return RetrievalResult(
                    retriever_name=self.name,
                    query=query,
                    status=RetrievalStatus.NO_RESULTS,
                    documents=[],
                    total_found=0,
                    total_returned=0,
                    execution_time_ms=0,
                    api_calls_made=0,
                    cache_hits=0,
                    error_message="No URLs found for query",
                )

            # Fetch documents in parallel
            tasks = []
            for url in urls[:max_results]:
                task = asyncio.create_task(self._fetch_document(url, query))
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            documents = []
            api_calls = len(urls)
            errors = []

            for i, result in enumerate(results):
                if isinstance(result, RetrievedDocument):
                    documents.append(result)
                elif isinstance(result, Exception):
                    error_msg = f"Failed to fetch {urls[i]}: {result!s}"
                    errors.append(error_msg)
                    logger.warning(error_msg)

            # Calculate execution time
            end_time = datetime.now(UTC)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

            # Determine status
            if documents:
                if len(documents) == len(urls):
                    status = RetrievalStatus.SUCCESS
                else:
                    status = RetrievalStatus.PARTIAL_SUCCESS
            else:
                status = RetrievalStatus.NO_RESULTS

            result = RetrievalResult(
                retriever_name=self.name,
                query=query,
                status=status,
                documents=documents,
                total_found=len(urls),
                total_returned=len(documents),
                execution_time_ms=execution_time_ms,
                api_calls_made=api_calls,
                cache_hits=0,
                started_at=start_time,
                completed_at=end_time,
            )

            if errors:
                result.warnings = errors[:3]  # First 3 errors

            return result

        except Exception as e:
            error_msg = f"HTTP retrieval failed: {e!s}"
            self.record_error(error_msg)

            end_time = datetime.now(UTC)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

            return RetrievalResult(
                retriever_name=self.name,
                query=query,
                status=RetrievalStatus.ERROR,
                documents=[],
                total_found=0,
                total_returned=0,
                execution_time_ms=execution_time_ms,
                api_calls_made=0,
                cache_hits=0,
                error_message=error_msg,
                started_at=start_time,
                completed_at=end_time,
            )

    def _get_urls_for_query(self, query: str, max_results: int, **kwargs) -> list[str]:
        """Get URLs to fetch for query"""

        # Check if URLs are provided directly
        if "urls" in kwargs:
            return kwargs["urls"]

        # Check if base_url is configured for API calls
        base_url = self.config.get("base_url")
        if base_url:
            # API-style retrieval
            return self._build_api_urls(base_url, query, max_results, **kwargs)

        # Search engine or web scraping mode
        search_engines = self.config.get("search_engines", ["google", "bing"])
        return self._build_search_urls(query, max_results, search_engines)

    def _build_api_urls(self, base_url: str, query: str, max_results: int, **kwargs) -> list[str]:
        """Build API URLs for query"""

        urls = []

        # Simple API URL building
        api_key = self.config.get("api_key", "")

        # Build query parameters
        params = {
            "q": query,
            "limit": min(max_results, 50),
        }

        if api_key:
            params["apikey"] = api_key

        # Add custom parameters
        custom_params = self.config.get("params", {})
        params.update(custom_params)

        # Override with kwargs
        params.update(kwargs.get("params", {}))

        # Build URL
        from urllib.parse import urlencode

        query_string = urlencode(params)
        full_url = f"{base_url}?{query_string}"

        urls.append(full_url)

        return urls

    def _build_search_urls(
        self, query: str, max_results: int, search_engines: list[str]
    ) -> list[str]:
        """Build search engine URLs"""

        urls = []

        for engine in search_engines[:2]:  # Max 2 search engines
            if engine == "google":
                # Note: This would require search API access in practice
                google_url = f"https://www.google.com/search?q={query}&num={min(max_results, 10)}"
                # In practice, you'd use Google Custom Search API
                urls.append(google_url)

            elif engine == "bing":
                # Note: This would require Bing API access in practice
                bing_url = f"https://www.bing.com/search?q={query}&count={min(max_results, 20)}"
                urls.append(bing_url)

        return urls

    async def _fetch_document(self, url: str, query: str) -> RetrievedDocument:
        """Fetch single document from URL"""

        # Check domain filtering
        if not self._is_url_allowed(url):
            raise ValueError(f"URL not allowed: {url}")

        # Select user agent
        import random

        user_agent = random.choice(self.http_config.user_agents)

        headers = dict(self.http_config.custom_headers)
        headers["User-Agent"] = user_agent

        # Retry logic
        last_exception = None

        for attempt in range(self.http_config.max_retries):
            try:
                async with self.session.get(url, headers=headers) as response:
                    # Check content type
                    content_type = response.headers.get("content-type", "").lower()
                    if not any(
                        allowed_type in content_type
                        for allowed_type in self.http_config.content_types
                    ):
                        raise ValueError(f"Unsupported content type: {content_type}")

                    # Check content length
                    content_length = response.headers.get("content-length")
                    if content_length and int(content_length) > self.http_config.max_content_length:
                        raise ValueError(f"Content too large: {content_length}")

                    # Read content
                    content_bytes = await response.read()

                    if len(content_bytes) > self.http_config.max_content_length:
                        raise ValueError(f"Content too large: {len(content_bytes)}")

                    # Decode content
                    encoding = self._detect_encoding(response.headers, content_bytes)
                    raw_content = content_bytes.decode(encoding, errors="replace")

                    # Extract and clean content
                    if "json" in content_type:
                        extracted_content = self._extract_json_content(raw_content, query)
                        title = f"API Response: {urlparse(url).netloc}"
                        source_type = SourceType.API_RESPONSE
                    else:
                        extracted_content, title = self._extract_html_content(raw_content)
                        source_type = SourceType.WEB_PAGE

                    # Create document
                    metadata = {
                        "title": title,
                        "url": str(response.url),  # Final URL after redirects
                        "source_type": source_type.value,
                        "extraction_method": "http_fetch",
                        "domain": urlparse(str(response.url)).netloc,
                        "status_code": response.status,
                        "content_type": content_type,
                    }

                    document = self.normalize_document(extracted_content, metadata)

                    return document

            except Exception as e:
                last_exception = e

                if attempt < self.http_config.max_retries - 1:
                    await asyncio.sleep(self.http_config.retry_delay_seconds)
                    logger.debug(f"Retrying {url} (attempt {attempt + 1}): {e!s}")

        # All retries failed
        raise last_exception or Exception("Unknown error in fetch_document")

    def _is_url_allowed(self, url: str) -> bool:
        """Check if URL is allowed by domain filtering"""

        domain = urlparse(url).netloc.lower()

        # Check blocked domains
        if self.http_config.blocked_domains:
            if any(blocked in domain for blocked in self.http_config.blocked_domains):
                return False

        # Check allowed domains (if specified)
        if self.http_config.allowed_domains:
            if not any(allowed in domain for allowed in self.http_config.allowed_domains):
                return False

        return True

    def _detect_encoding(self, headers: dict[str, str], content_bytes: bytes) -> str:
        """Detect content encoding"""

        # Check Content-Type header
        content_type = headers.get("content-type", "")

        # Look for charset in content-type
        import re

        charset_match = re.search(r"charset=([^;\s]+)", content_type, re.IGNORECASE)
        if charset_match:
            return charset_match.group(1)

        # Try to detect from content (simplified)
        try:
            # Look for HTML meta charset
            content_start = content_bytes[:2048].decode("utf-8", errors="ignore")
            meta_match = re.search(
                r'<meta[^>]+charset[^>]*=[\'""]?([^\'\">\s]+)',
                content_start,
                re.IGNORECASE,
            )
            if meta_match:
                return meta_match.group(1)
        except:
            pass

        # Default to UTF-8
        return "utf-8"

    def _extract_html_content(self, html_content: str) -> tuple[str, str]:
        """Extract clean text content from HTML"""

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Extract title
            title_tag = soup.find("title")
            title = title_tag.get_text().strip() if title_tag else "Untitled"

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
                element.decompose()

            # Get main content areas
            main_content = ""

            # Try to find main content areas
            content_selectors = [
                "main",
                "article",
                ".content",
                "#content",
                ".post-content",
                ".entry-content",
                ".article-content",
            ]

            for selector in content_selectors:
                content_elements = soup.select(selector)
                if content_elements:
                    main_content = " ".join(elem.get_text() for elem in content_elements)
                    break

            # Fallback to body content
            if not main_content:
                body = soup.find("body")
                main_content = body.get_text() if body else soup.get_text()

            # Clean up text
            lines = main_content.split("\n")
            cleaned_lines = []

            for line in lines:
                line = line.strip()
                if line and len(line) > 3:  # Skip very short lines
                    cleaned_lines.append(line)

            cleaned_content = "\n".join(cleaned_lines)

            # Decode HTML entities
            cleaned_content = html.unescape(cleaned_content)

            return cleaned_content, title

        except Exception as e:
            logger.warning(f"HTML parsing failed: {e!s}")

            # Fallback - simple text extraction
            text = re.sub(r"<[^>]+>", " ", html_content)
            text = html.unescape(text)
            text = re.sub(r"\s+", " ", text).strip()

            return text[:5000], "Extracted Text"  # Limit to 5000 chars

    def _extract_json_content(self, json_content: str, query: str) -> str:
        """Extract relevant content from JSON response"""

        try:
            import json as json_module

            data = json_module.loads(json_content)

            # Simple extraction - look for common text fields
            text_fields = []

            def extract_text_recursive(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{path}.{key}" if path else key

                        # Look for likely text fields
                        if (
                            key.lower()
                            in [
                                "text",
                                "content",
                                "description",
                                "summary",
                                "body",
                                "message",
                                "title",
                            ]
                            and isinstance(value, str)
                            and len(value) > 20
                        ):
                            text_fields.append(f"[{key}]: {value}")

                        extract_text_recursive(value, new_path)

                elif isinstance(obj, list):
                    for i, item in enumerate(obj[:10]):  # Limit to first 10 items
                        extract_text_recursive(item, f"{path}[{i}]")

            extract_text_recursive(data)

            if text_fields:
                return "\n\n".join(text_fields)
            # Fallback - return formatted JSON
            return json_module.dumps(data, indent=2)[:3000]

        except Exception as e:
            logger.warning(f"JSON parsing failed: {e!s}")
            return json_content[:3000]  # Return first 3000 chars

    def get_supported_parameters(self) -> list[str]:
        """Get supported query parameters"""

        return [
            "urls",  # Direct URLs to fetch
            "base_url",  # Base URL for API calls
            "params",  # Additional query parameters
            "max_retries",  # Override retry count
            "timeout",  # Override timeout
            "headers",  # Additional headers
            "user_agent",  # Override user agent
        ]

    async def close(self):
        """Close HTTP session"""

        if self.session and not self.session.closed:
            await self.session.close()


def main():
    """CLI testing interface"""

    import argparse

    parser = argparse.ArgumentParser(description="EQ12 HTTP Retriever")
    parser.add_argument("query", help="Query to search for")
    parser.add_argument("--urls", nargs="+", help="Direct URLs to fetch")
    parser.add_argument("--max-results", type=int, default=5, help="Maximum results")
    parser.add_argument("--base-url", help="Base API URL")

    args = parser.parse_args()

    # Create retriever
    config = {}

    if args.base_url:
        config["base_url"] = args.base_url

    retriever = HTTPRetriever("test_http", config)

    async def run_test():
        kwargs = {}
        if args.urls:
            kwargs["urls"] = args.urls

        result = await retriever.retrieve(args.query, args.max_results, **kwargs)

        print("📄 HTTP Retrieval Results")
        print(f"   Query: {args.query}")
        print(f"   Status: {result.status.value}")
        print(f"   Found: {result.total_found}")
        print(f"   Returned: {result.total_returned}")
        print(f"   Execution Time: {result.execution_time_ms}ms")

        if result.error_message:
            print(f"   Error: {result.error_message}")

        if result.warnings:
            print(f"   Warnings: {len(result.warnings)}")
            for warning in result.warnings:
                print(f"      - {warning}")

        print(f"\n📋 Documents ({len(result.documents)}):")

        for i, doc in enumerate(result.documents, 1):
            print(f"\n   {i}. {doc.title}")
            print(f"      URL: {doc.source_url}")
            print(f"      Type: {doc.source_type.value}")
            print(f"      Length: {doc.content_length}")
            print(f"      Confidence: {doc.confidence_score:.2f}")
            print(f"      Content Preview: {doc.content[:200]}...")

        await retriever.close()

    asyncio.run(run_test())


if __name__ == "__main__":
    main()
