# eq12_advanced_token_rate_manager.py
"""
EQ12 Advanced Token Management & Rate Limiting System
Comprehensive RPM/TPM management, cached input pricing, 429 handling, quota management
"""

import asyncio
import json
import logging
import sqlite3
import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from eq12_helpers import setup_utf8_logging

setup_utf8_logging()


class ServiceType(Enum):
    """AI service types for quota management"""

    OPENAI_GPT = "openai_gpt"
    OPENAI_EMBEDDING = "openai_embedding"
    OPENAI_WHISPER = "openai_whisper"
    ANTHROPIC_CLAUDE = "anthropic_claude"
    GOOGLE_GEMINI = "google_gemini"
    LOCAL_LLM = "local_llm"


class QuotaPriority(Enum):
    """Request priority levels"""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class RateLimitConfig:
    """Rate limit configuration per service"""

    requests_per_minute: int
    tokens_per_minute: int
    requests_per_day: int
    tokens_per_day: int
    burst_allowance: int = 10  # Extra requests allowed in burst
    burst_window_seconds: int = 60


@dataclass
class TokenQuota:
    """Token quota tracking"""

    service: ServiceType
    allocated_tokens: int
    used_tokens: int
    reserved_tokens: int
    priority_allocation: dict[QuotaPriority, int] = field(default_factory=dict)
    reset_time: datetime = field(default_factory=datetime.now)


@dataclass
class RequestMetrics:
    """Request performance metrics"""

    timestamp: datetime
    service: ServiceType
    tokens_used: int
    latency_ms: float
    success: bool
    priority: QuotaPriority
    queue_wait_ms: float = 0.0


class SlidingWindowRateLimiter:
    """Sliding window rate limiter with burst support"""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.request_times = deque()
        self.token_usage = deque()
        self.lock = threading.Lock()
        self.burst_requests = deque()

    def can_make_request(self, tokens_needed: int = 1) -> tuple[bool, float]:
        """Check if request can be made, return (allowed, wait_time)"""

        with self.lock:
            now = time.time()

            # Clean old requests (1 minute window)
            self._cleanup_old_entries(now, 60)

            # Check minute limits
            requests_this_minute = len(self.request_times)
            tokens_this_minute = sum(usage[1] for usage in self.token_usage)

            # Check burst allowance
            burst_available = self._check_burst_allowance(now)

            # Calculate if request fits
            rpm_ok = requests_this_minute < self.config.requests_per_minute or burst_available
            tpm_ok = tokens_this_minute + tokens_needed <= self.config.tokens_per_minute

            if rpm_ok and tpm_ok:
                return True, 0.0

            # Calculate wait time
            if not rpm_ok:
                oldest_request = self.request_times[0] if self.request_times else now
                wait_time = 60 - (now - oldest_request)
            else:
                # Token limit exceeded, wait for tokens to free up
                oldest_token_usage = self.token_usage[0] if self.token_usage else (now, 0)
                wait_time = 60 - (now - oldest_token_usage[0])

            return False, max(0.1, wait_time)

    def record_request(self, tokens_used: int):
        """Record a successful request"""

        with self.lock:
            now = time.time()
            self.request_times.append(now)
            self.token_usage.append((now, tokens_used))

            # Check if this was a burst request
            if len(self.request_times) > self.config.requests_per_minute:
                self.burst_requests.append(now)

    def _cleanup_old_entries(self, current_time: float, window_seconds: int):
        """Remove entries older than window"""

        cutoff = current_time - window_seconds

        while self.request_times and self.request_times[0] < cutoff:
            self.request_times.popleft()

        while self.token_usage and self.token_usage[0][0] < cutoff:
            self.token_usage.popleft()

        while self.burst_requests and self.burst_requests[0] < cutoff:
            self.burst_requests.popleft()

    def _check_burst_allowance(self, current_time: float) -> bool:
        """Check if burst requests are available"""

        burst_window_start = current_time - self.config.burst_window_seconds
        recent_bursts = sum(1 for t in self.burst_requests if t > burst_window_start)

        return recent_bursts < self.config.burst_allowance

    def get_current_usage(self) -> dict[str, Any]:
        """Get current usage statistics"""

        with self.lock:
            now = time.time()
            self._cleanup_old_entries(now, 60)

            requests_this_minute = len(self.request_times)
            tokens_this_minute = sum(usage[1] for usage in self.token_usage)

            return {
                "requests_per_minute": requests_this_minute,
                "tokens_per_minute": tokens_this_minute,
                "rpm_limit": self.config.requests_per_minute,
                "tpm_limit": self.config.tokens_per_minute,
                "rpm_utilization": requests_this_minute / self.config.requests_per_minute,
                "tpm_utilization": tokens_this_minute / self.config.tokens_per_minute,
                "burst_requests_used": len(self.burst_requests),
            }


class IntelligentQuotaManager:
    """Intelligent quota management with priority-based allocation"""

    def __init__(self):
        self.quotas: dict[ServiceType, TokenQuota] = {}
        self.allocations = {
            QuotaPriority.CRITICAL: 0.4,  # 40% for critical
            QuotaPriority.HIGH: 0.3,  # 30% for high
            QuotaPriority.MEDIUM: 0.2,  # 20% for medium
            QuotaPriority.LOW: 0.08,  # 8% for low
            QuotaPriority.BACKGROUND: 0.02,  # 2% for background
        }
        self.lock = threading.Lock()

    def initialize_quota(self, service: ServiceType, total_tokens: int):
        """Initialize quota for a service"""

        with self.lock:
            priority_allocation = {}

            for priority, percentage in self.allocations.items():
                priority_allocation[priority] = int(total_tokens * percentage)

            self.quotas[service] = TokenQuota(
                service=service,
                allocated_tokens=total_tokens,
                used_tokens=0,
                reserved_tokens=0,
                priority_allocation=priority_allocation,
                reset_time=datetime.now() + timedelta(days=1),
            )

    def reserve_tokens(
        self, service: ServiceType, tokens_needed: int, priority: QuotaPriority
    ) -> bool:
        """Reserve tokens for a request"""

        with self.lock:
            if service not in self.quotas:
                return False

            quota = self.quotas[service]

            # Check if quota needs reset (daily reset)
            if datetime.now() > quota.reset_time:
                self._reset_quota(service)
                quota = self.quotas[service]

            # Check priority allocation
            priority_available = quota.priority_allocation[priority] - self._get_priority_usage(
                service, priority
            )

            # Allow borrowing from lower priorities if needed
            if priority_available < tokens_needed:
                available = self._try_borrow_tokens(service, priority, tokens_needed)
                if not available:
                    return False

            # Reserve tokens
            quota.reserved_tokens += tokens_needed

            return True

    def commit_tokens(self, service: ServiceType, tokens_used: int, priority: QuotaPriority):
        """Commit reserved tokens as used"""

        with self.lock:
            if service in self.quotas:
                quota = self.quotas[service]
                quota.used_tokens += tokens_used
                quota.reserved_tokens = max(0, quota.reserved_tokens - tokens_used)

    def release_tokens(self, service: ServiceType, tokens_to_release: int):
        """Release reserved but unused tokens"""

        with self.lock:
            if service in self.quotas:
                quota = self.quotas[service]
                quota.reserved_tokens = max(0, quota.reserved_tokens - tokens_to_release)

    def _reset_quota(self, service: ServiceType):
        """Reset daily quota"""

        quota = self.quotas[service]
        total_tokens = quota.allocated_tokens

        # Reinitialize with same allocation
        self.quotas[service] = TokenQuota(
            service=service,
            allocated_tokens=total_tokens,
            used_tokens=0,
            reserved_tokens=0,
            priority_allocation=quota.priority_allocation.copy(),
            reset_time=datetime.now() + timedelta(days=1),
        )

    def _get_priority_usage(self, service: ServiceType, priority: QuotaPriority) -> int:
        """Get tokens used by specific priority (simplified - would track in DB)"""
        # In production, this would query usage by priority from database
        return 0

    def _try_borrow_tokens(
        self, service: ServiceType, priority: QuotaPriority, tokens_needed: int
    ) -> bool:
        """Try to borrow tokens from lower priority allocations"""

        quota = self.quotas[service]

        # Can borrow from lower priorities
        for lower_priority in QuotaPriority:
            if lower_priority.value > priority.value:
                available = quota.priority_allocation[lower_priority] - self._get_priority_usage(
                    service, lower_priority
                )

                if available >= tokens_needed:
                    return True

        return False

    def get_quota_status(self, service: ServiceType) -> dict[str, Any]:
        """Get current quota status"""

        with self.lock:
            if service not in self.quotas:
                return {"error": "Service not found"}

            quota = self.quotas[service]

            return {
                "service": service.value,
                "total_allocated": quota.allocated_tokens,
                "used_tokens": quota.used_tokens,
                "reserved_tokens": quota.reserved_tokens,
                "available_tokens": (
                    quota.allocated_tokens - quota.used_tokens - quota.reserved_tokens
                ),
                "utilization": quota.used_tokens / quota.allocated_tokens,
                "reset_time": quota.reset_time.isoformat(),
                "priority_allocations": {
                    p.name: alloc for p, alloc in quota.priority_allocation.items()
                },
            }


class CachedInputOptimizer:
    """Optimize costs using cached inputs and deduplication"""

    def __init__(self):
        self.cache_db = Path("C:/EQ12/data/input_cache.db")
        self.setup_cache_database()
        self.cache_hit_rate = 0.0
        self.total_requests = 0
        self.cache_hits = 0

    def setup_cache_database(self):
        """Initialize cache database"""

        self.cache_db.parent.mkdir(exist_ok=True, parents=True)

        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS input_cache (
                input_hash TEXT PRIMARY KEY,
                input_content TEXT,
                response_content TEXT,
                model TEXT,
                tokens_saved INTEGER,
                cost_saved REAL,
                created_at TEXT,
                last_used TEXT,
                use_count INTEGER DEFAULT 1
            )
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_last_used ON input_cache(last_used)
        """
        )

        conn.commit()
        conn.close()

    def get_cache_key(self, messages: list[dict[str, str]], model: str) -> str:
        """Generate cache key for input"""

        # Create deterministic hash of input
        import hashlib

        content = json.dumps({"messages": messages, "model": model}, sort_keys=True)

        return hashlib.sha256(content.encode()).hexdigest()

    def check_cache(self, messages: list[dict[str, str]], model: str) -> dict[str, Any] | None:
        """Check if response is cached"""

        cache_key = self.get_cache_key(messages, model)

        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT response_content, tokens_saved, cost_saved, use_count
            FROM input_cache
            WHERE input_hash = ?
        """,
            (cache_key,),
        )

        result = cursor.fetchone()

        if result:
            # Update usage statistics
            cursor.execute(
                """
                UPDATE input_cache
                SET last_used = ?, use_count = use_count + 1
                WHERE input_hash = ?
            """,
                (datetime.now().isoformat(), cache_key),
            )

            conn.commit()

            self.cache_hits += 1
            self.total_requests += 1
            self.cache_hit_rate = self.cache_hits / self.total_requests

            conn.close()

            return {
                "response": json.loads(result[0]),
                "tokens_saved": result[1],
                "cost_saved": result[2],
                "cache_hit": True,
                "use_count": result[3] + 1,
            }

        conn.close()
        self.total_requests += 1
        self.cache_hit_rate = self.cache_hits / self.total_requests

        return None

    def store_response(
        self,
        messages: list[dict[str, str]],
        model: str,
        response: dict[str, Any],
        tokens_saved: int,
        cost_saved: float,
    ):
        """Store response in cache"""

        cache_key = self.get_cache_key(messages, model)

        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO input_cache
            (input_hash, input_content, response_content, model,
             tokens_saved, cost_saved, created_at, last_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                cache_key,
                json.dumps(messages),
                json.dumps(response),
                model,
                tokens_saved,
                cost_saved,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    def cleanup_cache(self, days_old: int = 30):
        """Clean up old cache entries"""

        cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()

        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM input_cache
            WHERE last_used < ? AND use_count < 3
        """,
            (cutoff_date,),
        )

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        logging.info(f"Cleaned up {deleted} old cache entries")

        return deleted

    def get_cache_statistics(self) -> dict[str, Any]:
        """Get cache performance statistics"""

        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        # Total entries and savings
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_entries,
                SUM(tokens_saved) as total_tokens_saved,
                SUM(cost_saved) as total_cost_saved,
                AVG(use_count) as avg_use_count
            FROM input_cache
        """
        )

        stats = cursor.fetchone()

        # Most used entries
        cursor.execute(
            """
            SELECT model, use_count, cost_saved
            FROM input_cache
            ORDER BY use_count DESC
            LIMIT 5
        """
        )

        top_entries = cursor.fetchall()

        conn.close()

        return {
            "total_cache_entries": stats[0] or 0,
            "total_tokens_saved": stats[1] or 0,
            "total_cost_saved": stats[2] or 0.0,
            "average_use_count": stats[3] or 0.0,
            "cache_hit_rate": self.cache_hit_rate,
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "top_cached_entries": [
                {"model": row[0], "use_count": row[1], "cost_saved": row[2]} for row in top_entries
            ],
        }


class AdvancedRateManager:
    """Main rate management orchestrator"""

    def __init__(self):
        self.rate_limiters: dict[ServiceType, SlidingWindowRateLimiter] = {}
        self.quota_manager = IntelligentQuotaManager()
        self.cache_optimizer = CachedInputOptimizer()
        self.metrics: list[RequestMetrics] = []

        # Initialize default configurations
        self._initialize_default_configs()

        # Performance tracking
        self.db_path = Path("C:/EQ12/data/rate_management.db")
        self.setup_database()

    def _initialize_default_configs(self):
        """Initialize default rate limit configurations"""

        configs = {
            ServiceType.OPENAI_GPT: RateLimitConfig(
                requests_per_minute=500,
                tokens_per_minute=200000,
                requests_per_day=10000,
                tokens_per_day=2000000,
                burst_allowance=50,
            ),
            ServiceType.OPENAI_EMBEDDING: RateLimitConfig(
                requests_per_minute=3000,
                tokens_per_minute=1000000,
                requests_per_day=50000,
                tokens_per_day=10000000,
                burst_allowance=100,
            ),
            ServiceType.ANTHROPIC_CLAUDE: RateLimitConfig(
                requests_per_minute=100,
                tokens_per_minute=100000,
                requests_per_day=2000,
                tokens_per_day=1000000,
                burst_allowance=20,
            ),
        }

        # Initialize rate limiters and quotas
        for service, config in configs.items():
            self.rate_limiters[service] = SlidingWindowRateLimiter(config)
            self.quota_manager.initialize_quota(service, config.tokens_per_day)

    def setup_database(self):
        """Initialize metrics database"""

        self.db_path.parent.mkdir(exist_ok=True, parents=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS request_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                service TEXT,
                tokens_used INTEGER,
                latency_ms REAL,
                success INTEGER,
                priority TEXT,
                queue_wait_ms REAL
            )
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_timestamp ON request_metrics(timestamp)
        """
        )

        conn.commit()
        conn.close()

    async def request_permission(
        self,
        service: ServiceType,
        tokens_needed: int,
        priority: QuotaPriority = QuotaPriority.MEDIUM,
        messages: list[dict[str, str]] | None = None,
        model: str = "",
    ) -> dict[str, Any]:
        """Request permission for API call with full optimization"""

        start_time = time.time()

        # Check cache first
        if messages and model:
            cached_response = self.cache_optimizer.check_cache(messages, model)
            if cached_response:
                return {
                    "allowed": True,
                    "wait_time": 0.0,
                    "cached_response": cached_response,
                    "tokens_saved": cached_response["tokens_saved"],
                    "cost_saved": cached_response["cost_saved"],
                }

        # Check quota availability
        quota_available = self.quota_manager.reserve_tokens(service, tokens_needed, priority)

        if not quota_available:
            return {
                "allowed": False,
                "reason": "quota_exceeded",
                "quota_status": self.quota_manager.get_quota_status(service),
            }

        # Check rate limits
        if service in self.rate_limiters:
            limiter = self.rate_limiters[service]
            can_proceed, wait_time = limiter.can_make_request(tokens_needed)

            if not can_proceed:
                # Release reserved quota
                self.quota_manager.release_tokens(service, tokens_needed)

                return {
                    "allowed": False,
                    "reason": "rate_limited",
                    "wait_time": wait_time,
                    "rate_limit_status": limiter.get_current_usage(),
                }

        queue_wait_ms = (time.time() - start_time) * 1000

        return {
            "allowed": True,
            "wait_time": 0.0,
            "queue_wait_ms": queue_wait_ms,
            "quota_reserved": True,
        }

    def record_request_completion(
        self,
        service: ServiceType,
        tokens_used: int,
        latency_ms: float,
        success: bool,
        priority: QuotaPriority = QuotaPriority.MEDIUM,
        queue_wait_ms: float = 0.0,
        response: dict | None = None,
        messages: list[dict] | None = None,
        model: str = "",
    ):
        """Record completed request"""

        # Update rate limiter
        if service in self.rate_limiters:
            self.rate_limiters[service].record_request(tokens_used)

        # Commit quota usage
        self.quota_manager.commit_tokens(service, tokens_used, priority)

        # Store in cache if successful and not already cached
        if success and response and messages and model:
            # Calculate savings (simplified)
            tokens_saved = tokens_used // 2  # Assume 50% savings on cache hit
            cost_saved = tokens_saved * 0.001  # Simplified cost calculation

            self.cache_optimizer.store_response(messages, model, response, tokens_saved, cost_saved)

        # Record metrics
        metric = RequestMetrics(
            timestamp=datetime.now(),
            service=service,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            success=success,
            priority=priority,
            queue_wait_ms=queue_wait_ms,
        )

        self.metrics.append(metric)

        # Store in database
        self._store_metric(metric)

    def _store_metric(self, metric: RequestMetrics):
        """Store metric in database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO request_metrics
            (timestamp, service, tokens_used, latency_ms, success, priority, queue_wait_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                metric.timestamp.isoformat(),
                metric.service.value,
                metric.tokens_used,
                metric.latency_ms,
                1 if metric.success else 0,
                metric.priority.name,
                metric.queue_wait_ms,
            ),
        )

        conn.commit()
        conn.close()

    def get_performance_analytics(self, hours: int = 24) -> dict[str, Any]:
        """Get comprehensive performance analytics"""

        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Filter recent metrics
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff_time]

        if not recent_metrics:
            return {"error": "No recent metrics available"}

        # Calculate statistics
        total_requests = len(recent_metrics)
        successful_requests = sum(1 for m in recent_metrics if m.success)
        total_tokens = sum(m.tokens_used for m in recent_metrics)

        latencies = [m.latency_ms for m in recent_metrics if m.success]
        queue_waits = [m.queue_wait_ms for m in recent_metrics]

        # Service breakdown
        service_stats = defaultdict(lambda: {"requests": 0, "tokens": 0, "failures": 0})

        for metric in recent_metrics:
            stats = service_stats[metric.service]
            stats["requests"] += 1
            stats["tokens"] += metric.tokens_used
            if not metric.success:
                stats["failures"] += 1

        # Priority breakdown
        priority_stats = defaultdict(lambda: {"requests": 0, "avg_latency": 0})

        for metric in recent_metrics:
            priority_stats[metric.priority]["requests"] += 1

        return {
            "period_hours": hours,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": (successful_requests / total_requests if total_requests > 0 else 0),
            "total_tokens_used": total_tokens,
            "average_latency_ms": statistics.mean(latencies) if latencies else 0,
            "median_latency_ms": statistics.median(latencies) if latencies else 0,
            "p95_latency_ms": (
                statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else 0
            ),
            "average_queue_wait_ms": statistics.mean(queue_waits) if queue_waits else 0,
            "service_breakdown": dict(service_stats),
            "priority_breakdown": dict(priority_stats),
            "cache_statistics": self.cache_optimizer.get_cache_statistics(),
            "quota_status": {
                service.value: self.quota_manager.get_quota_status(service)
                for service in ServiceType
            },
        }


async def main():
    """Demonstrate advanced rate management"""

    setup_utf8_logging()
    logging.info("🚀 Starting Advanced Token & Rate Management System")

    # Initialize rate manager
    rate_manager = AdvancedRateManager()

    # Test request permission
    permission = await rate_manager.request_permission(
        ServiceType.OPENAI_GPT, tokens_needed=1000, priority=QuotaPriority.HIGH
    )

    print("✅ Permission granted: {permission['allowed']}")

    if permission["allowed"]:
        # Simulate request completion
        rate_manager.record_request_completion(
            ServiceType.OPENAI_GPT,
            tokens_used=1000,
            latency_ms=250.0,
            success=True,
            priority=QuotaPriority.HIGH,
        )
        print("✅ Request completed and recorded")

    # Get analytics
    rate_manager.get_performance_analytics()
    print("\n📊 Performance Analytics:")
    print("Success Rate: {analytics['success_rate']:.1%}")
    print("Average Latency: {analytics['average_latency_ms']:.1f}ms")
    print("Cache Hit Rate: {analytics['cache_statistics']['cache_hit_rate']:.1%}")

    # Test cache optimization
    sample_messages = [{"role": "user", "content": "What is 2+2?"}]

    rate_manager.cache_optimizer.check_cache(sample_messages, "gpt-4")
    print("\n💾 Cache test: {'Hit' if cached else 'Miss'}")

    print("\n🎉 Advanced Token & Rate Management System Ready!")


if __name__ == "__main__":
    asyncio.run(main())
