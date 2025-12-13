#!/usr/bin/env python3
"""
EQ12 GODSTACK - Base Retriever Interface
Modular data retrieval system with pluggable retrievers

Core Features:
- Abstract base class for all retrievers
- Standardized retrieval interface
- Rate limiting and error handling
- Result normalization and scoring
- Caching and deduplication support
"""

import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/retrievers.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class RetrievalStatus(Enum):
    """Retrieval operation status"""

    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    TIMEOUT = "timeout"
    NO_RESULTS = "no_results"


class SourceType(Enum):
    """Source types for retrieved documents"""

    WEB_PAGE = "web_page"
    API_RESPONSE = "api_response"
    RSS_FEED = "rss_feed"
    DATABASE_RECORD = "database_record"
    VECTOR_MATCH = "vector_match"
    CACHED_RESULT = "cached_result"


@dataclass
class RetrievedDocument:
    """Individual retrieved document/result"""

    # Core content
    content: str
    title: str
    source_url: str
    source_type: SourceType

    # Metadata
    retriever_name: str
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Quality scores
    relevance_score: float = 0.0
    authority_score: float = 0.0
    freshness_score: float = 0.0
    confidence_score: float = 0.0

    # Source metadata
    published_at: datetime | None = None
    author: str | None = None
    domain: str | None = None
    content_length: int = 0

    # Processing metadata
    extraction_method: str = "unknown"
    processing_notes: list[str] = field(default_factory=list)

    # Unique identifier
    doc_id: str = field(default="")

    def __post_init__(self):
        if not self.doc_id:
            # Generate doc ID from content hash
            content_str = f"{self.title}:{self.source_url}:{self.content[:500]}"
            self.doc_id = hashlib.md5(content_str.encode()).hexdigest()[:12]

        if not self.content_length:
            self.content_length = len(self.content)

        if not self.domain and self.source_url:
            try:
                from urllib.parse import urlparse

                self.domain = urlparse(self.source_url).netloc
            except:
                self.domain = "unknown"


@dataclass
class RetrievalResult:
    """Results from retrieval operation"""

    # Operation metadata
    retriever_name: str
    query: str
    status: RetrievalStatus

    # Results
    documents: list[RetrievedDocument]
    total_found: int
    total_returned: int

    # Performance metrics
    execution_time_ms: int
    api_calls_made: int
    cache_hits: int

    # Quality metrics
    average_relevance: float = 0.0
    highest_confidence: float = 0.0

    # Error information
    error_message: str | None = None
    warnings: list[str] = field(default_factory=list)

    # Timestamps
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self):
        # Calculate quality metrics
        if self.documents:
            relevance_scores = [
                doc.relevance_score for doc in self.documents if doc.relevance_score > 0
            ]
            confidence_scores = [
                doc.confidence_score for doc in self.documents if doc.confidence_score > 0
            ]

            self.average_relevance = (
                sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
            )
            self.highest_confidence = max(confidence_scores) if confidence_scores else 0.0


class BaseRetriever(ABC):
    """Abstract base class for all retrievers"""

    def __init__(self, name: str, config: dict[str, Any] | None = None):
        self.name = name
        self.config = config or {}

        # Rate limiting
        self.rate_limit_rpm = self.config.get("rate_limit", {}).get("rpm", 60)
        self.rate_limit_burst = self.config.get("rate_limit", {}).get("burst", 10)

        # Configuration
        self.enabled = self.config.get("enabled", True)
        self.priority = self.config.get("priority", 5)
        self.timeout_seconds = self.config.get("timeout_seconds", 30)

        # State
        self.request_history: list[datetime] = []
        self.error_count = 0
        self.last_error: str | None = None

        logger.info(f"Initialized retriever: {self.name}")

    @abstractmethod
    async def retrieve(self, query: str, max_results: int = 10, **kwargs) -> RetrievalResult:
        """Retrieve documents for query (abstract method)"""
        pass

    @abstractmethod
    def get_supported_parameters(self) -> list[str]:
        """Get list of supported query parameters"""
        pass

    def is_rate_limited(self) -> bool:
        """Check if retriever is currently rate limited"""

        now = datetime.now(UTC)

        # Clean old requests (older than 1 minute)
        minute_ago = now.timestamp() - 60
        self.request_history = [
            req_time for req_time in self.request_history if req_time.timestamp() > minute_ago
        ]

        # Check rate limits
        if len(self.request_history) >= self.rate_limit_rpm:
            return True

        # Check burst limit (last 10 seconds)
        ten_seconds_ago = now.timestamp() - 10
        recent_requests = [
            req_time for req_time in self.request_history if req_time.timestamp() > ten_seconds_ago
        ]

        return len(recent_requests) >= self.rate_limit_burst

    def record_request(self):
        """Record a request for rate limiting"""
        self.request_history.append(datetime.now(UTC))

    def record_error(self, error_message: str):
        """Record an error"""
        self.error_count += 1
        self.last_error = error_message
        logger.error(f"Retriever {self.name} error: {error_message}")

    def is_healthy(self) -> bool:
        """Check if retriever is healthy"""

        if not self.enabled:
            return False

        if self.is_rate_limited():
            return False

        # Check error rate (more than 5 errors in last 10 minutes is unhealthy)
        if self.error_count > 5:
            # Could add time-based error rate checking here
            return False

        return True

    def get_health_status(self) -> dict[str, Any]:
        """Get detailed health status"""

        return {
            "name": self.name,
            "enabled": self.enabled,
            "healthy": self.is_healthy(),
            "rate_limited": self.is_rate_limited(),
            "error_count": self.error_count,
            "last_error": self.last_error,
            "recent_requests": len(self.request_history),
            "rate_limit_rpm": self.rate_limit_rpm,
            "priority": self.priority,
        }

    def normalize_document(self, raw_content: str, metadata: dict[str, Any]) -> RetrievedDocument:
        """Normalize raw content into RetrievedDocument"""

        # Extract basic fields
        title = metadata.get("title", "Untitled")
        source_url = metadata.get("url", "")
        source_type = SourceType(metadata.get("source_type", "web_page"))

        # Create document
        doc = RetrievedDocument(
            content=raw_content,
            title=title,
            source_url=source_url,
            source_type=source_type,
            retriever_name=self.name,
            extraction_method=metadata.get("extraction_method", "unknown"),
        )

        # Add optional metadata
        if "published_at" in metadata:
            doc.published_at = metadata["published_at"]

        if "author" in metadata:
            doc.author = metadata["author"]

        # Calculate scores
        doc.relevance_score = self.calculate_relevance_score(raw_content, metadata)
        doc.authority_score = self.calculate_authority_score(metadata)
        doc.freshness_score = self.calculate_freshness_score(doc.published_at)
        doc.confidence_score = self.calculate_confidence_score(doc)

        return doc

    def calculate_relevance_score(self, content: str, metadata: dict[str, Any]) -> float:
        """Calculate relevance score (0-1)"""

        # Basic scoring - can be overridden in subclasses
        score = 0.5  # Default baseline

        # Content length factor
        content_length = len(content)
        if content_length > 1000:
            score += 0.2
        elif content_length > 500:
            score += 0.1

        # Title relevance (if available)
        if metadata.get("title"):
            title_len = len(metadata["title"])
            if 10 <= title_len <= 100:
                score += 0.1

        # API vs web content preference
        if metadata.get("source_type") == "api_response":
            score += 0.2

        return min(score, 1.0)

    def calculate_authority_score(self, metadata: dict[str, Any]) -> float:
        """Calculate authority score based on source"""

        # Domain-based authority scoring
        domain = metadata.get("domain", "")

        high_authority_domains = [
            "mlb.com",
            "fangraphs.com",
            "statcast",
            "espn.com",
            "athletic.com",
            "rotowire.com",
        ]

        medium_authority_domains = ["cbssports.com", "yahoo.com", "bleacherreport.com"]

        if any(auth_domain in domain for auth_domain in high_authority_domains):
            return 0.9
        if any(med_domain in domain for med_domain in medium_authority_domains):
            return 0.7
        return 0.5  # Default authority

    def calculate_freshness_score(self, published_at: datetime | None) -> float:
        """Calculate freshness score based on publish time"""

        if not published_at:
            return 0.5  # Unknown freshness

        now = datetime.now(UTC)
        age_hours = (now - published_at).total_seconds() / 3600

        # Fresher is better for sports content
        if age_hours <= 6:
            return 1.0
        if age_hours <= 24:
            return 0.8
        if age_hours <= 72:
            return 0.6
        if age_hours <= 168:  # 1 week
            return 0.4
        return 0.2

    def calculate_confidence_score(self, doc: RetrievedDocument) -> float:
        """Calculate overall confidence score"""

        # Weighted combination of other scores
        confidence = (
            doc.relevance_score * 0.4 + doc.authority_score * 0.3 + doc.freshness_score * 0.3
        )

        # Boost confidence for longer content
        if doc.content_length > 2000:
            confidence = min(confidence + 0.1, 1.0)

        return confidence


class RetrieverManager:
    """Manages multiple retrievers and coordinates retrieval"""

    def __init__(self):
        self.retrievers: dict[str, BaseRetriever] = {}

        logger.info("RetrieverManager initialized")

    def register_retriever(self, retriever: BaseRetriever):
        """Register a retriever"""

        self.retrievers[retriever.name] = retriever
        logger.info(f"Registered retriever: {retriever.name}")

    def get_retriever(self, name: str) -> BaseRetriever | None:
        """Get retriever by name"""
        return self.retrievers.get(name)

    def list_retrievers(self) -> list[str]:
        """List all registered retrievers"""
        return list(self.retrievers.keys())

    def get_healthy_retrievers(self) -> list[BaseRetriever]:
        """Get all healthy retrievers"""

        healthy = []
        for retriever in self.retrievers.values():
            if retriever.is_healthy():
                healthy.append(retriever)

        return healthy

    async def retrieve_parallel(
        self,
        query: str,
        retriever_names: list[str],
        max_results_per_retriever: int = 10,
    ) -> list[RetrievalResult]:
        """Retrieve from multiple retrievers in parallel"""

        tasks = []

        for retriever_name in retriever_names:
            retriever = self.get_retriever(retriever_name)
            if retriever and retriever.is_healthy():
                task = asyncio.create_task(retriever.retrieve(query, max_results_per_retriever))
                tasks.append(task)

        if not tasks:
            logger.warning(f"No healthy retrievers available from: {retriever_names}")
            return []

        logger.info(f"Starting parallel retrieval with {len(tasks)} retrievers")

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, RetrievalResult):
                valid_results.append(result)
            else:
                logger.error(f"Retrieval failed with exception: {result}")

        return valid_results

    def get_retriever_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all retrievers"""

        status = {}

        for name, retriever in self.retrievers.items():
            status[name] = retriever.get_health_status()

        return status


def main():
    """CLI interface for retriever management"""

    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Retriever Manager")
    parser.add_argument("--list-retrievers", action="store_true", help="List registered retrievers")
    parser.add_argument("--status", action="store_true", help="Show retriever status")
    parser.add_argument("--test-query", help="Test query on healthy retrievers")

    args = parser.parse_args()

    manager = RetrieverManager()

    # Register example retrievers (would normally be done by main application)
    # This is just for demonstration

    if args.list_retrievers:
        retrievers = manager.list_retrievers()
        print(f"📋 Registered Retrievers ({len(retrievers)}):")

        for name in retrievers:
            retriever = manager.get_retriever(name)
            health_status = "✅" if retriever.is_healthy() else "❌"
            print(f"   {health_status} {name} (priority: {retriever.priority})")

    elif args.status:
        status = manager.get_retriever_status()

        print("📊 Retriever Status:")

        for name, retriever_status in status.items():
            health_icon = "✅" if retriever_status["healthy"] else "❌"
            enabled_icon = "🟢" if retriever_status["enabled"] else "🔴"

            print(f"\n   {health_icon} {name} {enabled_icon}")
            print(f"      Priority: {retriever_status['priority']}")
            print(f"      Rate Limited: {retriever_status['rate_limited']}")
            print(f"      Error Count: {retriever_status['error_count']}")
            print(f"      Recent Requests: {retriever_status['recent_requests']}")

            if retriever_status["last_error"]:
                print(f"      Last Error: {retriever_status['last_error']}")

    elif args.test_query:
        print(f"🧪 Testing query: {args.test_query}")

        healthy_retrievers = manager.get_healthy_retrievers()

        if not healthy_retrievers:
            print("❌ No healthy retrievers available")
        else:
            print(f"✅ Found {len(healthy_retrievers)} healthy retrievers")

            for retriever in healthy_retrievers:
                print(f"   - {retriever.name}")

            print("\n(Note: Actual retrieval testing requires specific retriever implementations)")

    else:
        print("🔧 EQ12 Retriever Manager - Use --help for options")


if __name__ == "__main__":
    main()
