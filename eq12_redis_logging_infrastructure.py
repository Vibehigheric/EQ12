# eq12_redis_logging_infrastructure.py
"""
EQ12 Enhanced Redis Caching & Structured Logging Infrastructure
Advanced cron scheduling, performance monitoring, distributed cache optimization
"""

import asyncio
import hashlib
import json
import logging
import pickle
import sqlite3
import statistics
import threading
import time
import zlib
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import redis.asyncio as aioredis
import schedule

from eq12_helpers import setup_utf8_logging

setup_utf8_logging()


class CacheStrategy(Enum):
    """Cache eviction strategies"""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    FIFO = "fifo"  # First In, First Out


class LogLevel(Enum):
    """Enhanced log levels"""

    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    AUDIT = "audit"
    SECURITY = "security"


@dataclass
class CacheMetrics:
    """Cache performance metrics"""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    memory_usage: int = 0
    avg_latency_ms: float = 0.0
    hit_rate: float = 0.0

    def calculate_hit_rate(self):
        total = self.hits + self.misses
        self.hit_rate = self.hits / total if total > 0 else 0.0


@dataclass
class LogEntry:
    """Structured log entry"""

    timestamp: datetime
    level: LogLevel
    service: str
    component: str
    message: str
    metadata: dict[str, Any]
    trace_id: str | None = None
    span_id: str | None = None
    user_id: str | None = None
    request_id: str | None = None
    correlation_id: str | None = None


class AdvancedRedisCache:
    """Enhanced Redis cache with advanced features"""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis: aioredis.Redis | None = None
        self.metrics = CacheMetrics()
        self.strategy = CacheStrategy.LRU

        # Performance tracking
        self.operation_times = []
        self.lock = threading.Lock()

        # Cache configuration
        self.default_ttl = 3600  # 1 hour
        self.max_memory_mb = 512
        self.compression_threshold = 1024  # Compress values > 1KB

        # Key prefixes for organization
        self.prefixes = {
            "odds": "odds:",
            "analysis": "analysis:",
            "user": "user:",
            "session": "session:",
            "temp": "temp:",
            "lock": "lock:",
        }

    async def connect(self):
        """Initialize Redis connection with advanced configuration"""

        self.redis = aioredis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=False,  # Handle binary data
            retry_on_timeout=True,
            retry_on_error=[ConnectionError, TimeoutError],
            health_check_interval=30,
            max_connections=20,
            socket_keepalive=True,
            socket_keepalive_options={},
        )

        # Configure Redis for optimal performance
        try:
            await self.redis.config_set("maxmemory", f"{self.max_memory_mb}mb")
            await self.redis.config_set("maxmemory-policy", "allkeys-lru")
            await self.redis.config_set("save", "")  # Disable persistence for cache

            # Test connection
            await self.redis.ping()
            logging.info("✅ Redis cache connected successfully")

        except Exception as e:
            logging.error(f"Redis connection failed: {e}")
            raise

    def _serialize_value(self, value: Any) -> bytes:
        """Serialize and optionally compress cache value"""

        # Serialize with pickle for Python objects
        serialized = pickle.dumps(value)

        # Compress if large enough
        if len(serialized) > self.compression_threshold:
            serialized = zlib.compress(serialized)
            return b"compressed:" + serialized

        return serialized

    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize and decompress cache value"""

        if data.startswith(b"compressed:"):
            # Decompress first
            compressed_data = data[11:]  # Remove 'compressed:' prefix
            decompressed = zlib.decompress(compressed_data)
            return pickle.loads(decompressed)

        return pickle.loads(data)

    def _generate_key(self, prefix: str, identifier: str, *args) -> str:
        """Generate cache key with consistent format"""

        key_parts = [self.prefixes.get(prefix, ""), identifier]
        key_parts.extend(str(arg) for arg in args)

        # Create hash for very long keys
        key = ":".join(filter(None, key_parts))
        if len(key) > 200:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            return f"{self.prefixes.get(prefix, '')}{key_hash}"

        return key

    async def get(self, prefix: str, identifier: str, *args) -> Any | None:
        """Get value from cache with metrics tracking"""

        start_time = time.time()
        key = self._generate_key(prefix, identifier, *args)

        try:
            data = await self.redis.get(key)

            if data:
                value = self._deserialize_value(data)
                self.metrics.hits += 1

                # Update access time for LRU
                await self.redis.expire(key, self.default_ttl)

                logging.debug(f"Cache hit: {key}")
                return value
            self.metrics.misses += 1
            logging.debug(f"Cache miss: {key}")
            return None

        except Exception as e:
            logging.error(f"Cache get error: {e}")
            self.metrics.misses += 1
            return None

        finally:
            latency = (time.time() - start_time) * 1000
            with self.lock:
                self.operation_times.append(latency)
                if len(self.operation_times) > 1000:
                    self.operation_times.pop(0)

    async def set(
        self, prefix: str, identifier: str, value: Any, ttl: int | None = None, *args
    ) -> bool:
        """Set value in cache with compression and TTL"""

        start_time = time.time()
        key = self._generate_key(prefix, identifier, *args)
        ttl = ttl or self.default_ttl

        try:
            serialized_value = self._serialize_value(value)

            await self.redis.setex(key, ttl, serialized_value)

            logging.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logging.error(f"Cache set error: {e}")
            return False

        finally:
            latency = (time.time() - start_time) * 1000
            with self.lock:
                self.operation_times.append(latency)

    async def delete(self, prefix: str, identifier: str, *args) -> bool:
        """Delete value from cache"""

        key = self._generate_key(prefix, identifier, *args)

        try:
            deleted = await self.redis.delete(key)
            logging.debug(f"Cache delete: {key}")
            return deleted > 0

        except Exception as e:
            logging.error(f"Cache delete error: {e}")
            return False

    async def exists(self, prefix: str, identifier: str, *args) -> bool:
        """Check if key exists in cache"""

        key = self._generate_key(prefix, identifier, *args)

        try:
            return bool(await self.redis.exists(key))
        except Exception as e:
            logging.error(f"Cache exists error: {e}")
            return False

    async def increment(self, prefix: str, identifier: str, amount: int = 1, *args) -> int:
        """Increment counter in cache"""

        key = self._generate_key(prefix, identifier, *args)

        try:
            result = await self.redis.incrby(key, amount)
            await self.redis.expire(key, self.default_ttl)
            return result
        except Exception as e:
            logging.error(f"Cache increment error: {e}")
            return 0

    async def get_hash(
        self, prefix: str, identifier: str, field: str | None = None, *args
    ) -> dict | Any | None:
        """Get hash field(s) from cache"""

        key = self._generate_key(prefix, identifier, *args)

        try:
            if field:
                data = await self.redis.hget(key, field)
                return self._deserialize_value(data) if data else None
            hash_data = await self.redis.hgetall(key)
            return (
                {k.decode(): self._deserialize_value(v) for k, v in hash_data.items()}
                if hash_data
                else {}
            )

        except Exception as e:
            logging.error(f"Cache hash get error: {e}")
            return None

    async def set_hash(self, prefix: str, identifier: str, field: str, value: Any, *args) -> bool:
        """Set hash field in cache"""

        key = self._generate_key(prefix, identifier, *args)

        try:
            serialized_value = self._serialize_value(value)
            await self.redis.hset(key, field, serialized_value)
            await self.redis.expire(key, self.default_ttl)
            return True

        except Exception as e:
            logging.error(f"Cache hash set error: {e}")
            return False

    @asynccontextmanager
    async def distributed_lock(self, prefix: str, identifier: str, timeout: int = 30, *args):
        """Distributed lock using Redis"""

        lock_key = self._generate_key("lock", f"{prefix}:{identifier}", *args)
        lock_value = f"{time.time()}:{id(self)}"
        acquired = False

        try:
            # Try to acquire lock
            acquired = await self.redis.set(lock_key, lock_value, nx=True, ex=timeout)

            if acquired:
                logging.debug(f"Distributed lock acquired: {lock_key}")
                yield True
            else:
                logging.warning(f"Failed to acquire distributed lock: {lock_key}")
                yield False

        except Exception as e:
            logging.error(f"Distributed lock error: {e}")
            yield False

        finally:
            if acquired:
                try:
                    # Release lock only if we still own it
                    lua_script = """
                    if redis.call("get", KEYS[1]) == ARGV[1] then
                        return redis.call("del", KEYS[1])
                    else
                        return 0
                    end
                    """
                    await self.redis.eval(lua_script, 1, lock_key, lock_value)
                    logging.debug(f"Distributed lock released: {lock_key}")
                except Exception as e:
                    logging.error(f"Lock release error: {e}")

    async def get_metrics(self) -> dict[str, Any]:
        """Get comprehensive cache metrics"""

        self.metrics.calculate_hit_rate()

        # Redis memory info
        memory_info = await self.redis.info("memory")

        # Calculate average latency
        with self.lock:
            avg_latency = statistics.mean(self.operation_times) if self.operation_times else 0
            p95_latency = (
                statistics.quantiles(self.operation_times, n=20)[18]
                if len(self.operation_times) > 20
                else 0
            )

        return {
            "hits": self.metrics.hits,
            "misses": self.metrics.misses,
            "hit_rate": self.metrics.hit_rate,
            "evictions": self.metrics.evictions,
            "avg_latency_ms": avg_latency,
            "p95_latency_ms": p95_latency,
            "redis_memory_used": memory_info.get("used_memory", 0),
            "redis_memory_peak": memory_info.get("used_memory_peak", 0),
            "redis_keyspace_hits": memory_info.get("keyspace_hits", 0),
            "redis_keyspace_misses": memory_info.get("keyspace_misses", 0),
            "connected_clients": memory_info.get("connected_clients", 0),
            "total_operations": len(self.operation_times),
        }

    async def cleanup_expired(self):
        """Clean up expired keys and optimize memory"""

        try:
            # Get keys with TTL information
            all_keys = await self.redis.keys("*")
            expired_keys = []

            for key in all_keys:
                ttl = await self.redis.ttl(key)
                if ttl == -2:  # Key doesn't exist
                    expired_keys.append(key)

            if expired_keys:
                await self.redis.delete(*expired_keys)
                logging.info(f"Cleaned up {len(expired_keys)} expired cache keys")

        except Exception as e:
            logging.error(f"Cache cleanup error: {e}")


class StructuredLogger:
    """Advanced structured logging with Winston-style features"""

    def __init__(self, service_name: str = "eq12"):
        self.service_name = service_name
        self.db_path = Path("C:/EQ12/data/structured_logs.db")
        self.setup_database()

        # Configure Python logging
        self.setup_python_logging()

        # Log levels mapping
        self.level_mapping = {
            LogLevel.TRACE: 5,
            LogLevel.DEBUG: 10,
            LogLevel.INFO: 20,
            LogLevel.WARNING: 30,
            LogLevel.ERROR: 40,
            LogLevel.CRITICAL: 50,
            LogLevel.AUDIT: 25,
            LogLevel.SECURITY: 45,
        }

    def setup_database(self):
        """Initialize structured logging database"""

        self.db_path.parent.mkdir(exist_ok=True, parents=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS log_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                service TEXT NOT NULL,
                component TEXT NOT NULL,
                message TEXT NOT NULL,
                metadata TEXT,
                trace_id TEXT,
                span_id TEXT,
                user_id TEXT,
                request_id TEXT,
                correlation_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create indexes for performance
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_timestamp ON log_entries(timestamp)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_level ON log_entries(level)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_service ON log_entries(service)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_trace_id ON log_entries(trace_id)
        """
        )

        conn.commit()
        conn.close()

    def setup_python_logging(self):
        """Configure Python logging integration"""

        # Create custom formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # File handler with rotation
        file_handler = logging.FileHandler("C:/EQ12/logs/structured.log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    def log(
        self,
        level: LogLevel,
        component: str,
        message: str,
        metadata: dict[str, Any] | None = None,
        trace_id: str | None = None,
        span_id: str | None = None,
        user_id: str | None = None,
        request_id: str | None = None,
        correlation_id: str | None = None,
    ):
        """Log structured entry"""

        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            service=self.service_name,
            component=component,
            message=message,
            metadata=metadata or {},
            trace_id=trace_id,
            span_id=span_id,
            user_id=user_id,
            request_id=request_id,
            correlation_id=correlation_id,
        )

        # Store in database
        self._store_entry(entry)

        # Also log to Python logging
        python_level = self.level_mapping.get(level, logging.INFO)

        log_data = {
            "component": component,
            "metadata": metadata,
            "trace_id": trace_id,
            "request_id": request_id,
        }

        logging.log(python_level, f"{message} | {json.dumps(log_data)}")

    def _store_entry(self, entry: LogEntry):
        """Store log entry in database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO log_entries
            (timestamp, level, service, component, message, metadata,
             trace_id, span_id, user_id, request_id, correlation_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                entry.timestamp.isoformat(),
                entry.level.value,
                entry.service,
                entry.component,
                entry.message,
                json.dumps(entry.metadata),
                entry.trace_id,
                entry.span_id,
                entry.user_id,
                entry.request_id,
                entry.correlation_id,
            ),
        )

        conn.commit()
        conn.close()

    def query_logs(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        level: LogLevel | None = None,
        component: str | None = None,
        trace_id: str | None = None,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        """Query structured logs with filters"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM log_entries WHERE 1=1"
        params = []

        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())

        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())

        if level:
            query += " AND level = ?"
            params.append(level.value)

        if component:
            query += " AND component = ?"
            params.append(component)

        if trace_id:
            query += " AND trace_id = ?"
            params.append(trace_id)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        results = cursor.fetchall()

        conn.close()

        # Convert to dictionaries
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in results]

    def get_log_analytics(self, hours: int = 24) -> dict[str, Any]:
        """Get log analytics for specified time period"""

        start_time = datetime.now() - timedelta(hours=hours)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Log level distribution
        cursor.execute(
            """
            SELECT level, COUNT(*) as count
            FROM log_entries
            WHERE timestamp >= ?
            GROUP BY level
        """,
            (start_time.isoformat(),),
        )

        level_stats = cursor.fetchall()

        # Component activity
        cursor.execute(
            """
            SELECT component, COUNT(*) as count
            FROM log_entries
            WHERE timestamp >= ?
            GROUP BY component
            ORDER BY count DESC
            LIMIT 10
        """,
            (start_time.isoformat(),),
        )

        component_stats = cursor.fetchall()

        # Error rate over time (hourly buckets)
        cursor.execute(
            """
            SELECT
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                COUNT(*) as total,
                SUM(CASE WHEN level IN ('error', 'critical') THEN 1 ELSE 0 END) as errors
            FROM log_entries
            WHERE timestamp >= ?
            GROUP BY hour
            ORDER BY hour
        """,
            (start_time.isoformat(),),
        )

        hourly_stats = cursor.fetchall()

        conn.close()

        return {
            "period_hours": hours,
            "level_distribution": [{"level": row[0], "count": row[1]} for row in level_stats],
            "top_components": [{"component": row[0], "count": row[1]} for row in component_stats],
            "hourly_error_rate": [
                {
                    "hour": row[0],
                    "total_logs": row[1],
                    "error_logs": row[2],
                    "error_rate": row[2] / row[1] if row[1] > 0 else 0,
                }
                for row in hourly_stats
            ],
        }


class AdvancedCronScheduler:
    """Advanced cron scheduler with monitoring and error handling"""

    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.jobs = {}
        self.job_stats = {}
        self.running = False

    def schedule_job(self, name: str, func: Callable, schedule_str: str, *args, **kwargs):
        """Schedule a job with cron-like syntax"""

        job = schedule.every()

        # Parse schedule string (simplified parser)
        if schedule_str == "daily":
            job = job.day
        elif schedule_str == "hourly":
            job = job.hour
        elif schedule_str.startswith("every"):
            # Parse "every 5 minutes" format
            parts = schedule_str.split()
            if len(parts) >= 3:
                interval = int(parts[1])
                unit = parts[2].rstrip("s")  # Remove plural

                if unit == "minute":
                    job = job(interval).minutes
                elif unit == "hour":
                    job = job(interval).hours
                elif unit == "day":
                    job = job(interval).days

        # Wrap function with error handling and logging
        def wrapped_func():
            start_time = time.time()

            try:
                self.logger.log(LogLevel.INFO, "scheduler", f"Starting scheduled job: {name}")

                result = func(*args, **kwargs)

                duration = time.time() - start_time

                # Update job statistics
                if name not in self.job_stats:
                    self.job_stats[name] = {
                        "executions": 0,
                        "failures": 0,
                        "total_duration": 0,
                        "last_execution": None,
                    }

                stats = self.job_stats[name]
                stats["executions"] += 1
                stats["total_duration"] += duration
                stats["last_execution"] = datetime.now().isoformat()

                self.logger.log(
                    LogLevel.INFO,
                    "scheduler",
                    f"Completed scheduled job: {name}",
                    metadata={
                        "duration_seconds": duration,
                        "result": str(result)[:200] if result else None,
                    },
                )

            except Exception as e:
                duration = time.time() - start_time

                # Update failure stats
                if name in self.job_stats:
                    self.job_stats[name]["failures"] += 1

                self.logger.log(
                    LogLevel.ERROR,
                    "scheduler",
                    f"Scheduled job failed: {name}",
                    metadata={"error": str(e), "duration_seconds": duration},
                )

        job.do(wrapped_func)
        self.jobs[name] = job

        self.logger.log(
            LogLevel.INFO,
            "scheduler",
            f"Scheduled job registered: {name}",
            metadata={"schedule": schedule_str},
        )

    async def run_scheduler(self):
        """Run the scheduler in async loop"""

        self.running = True

        self.logger.log(LogLevel.INFO, "scheduler", "Cron scheduler started")

        while self.running:
            schedule.run_pending()
            await asyncio.sleep(1)

        self.logger.log(LogLevel.INFO, "scheduler", "Cron scheduler stopped")

    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False

    def get_job_statistics(self) -> dict[str, Any]:
        """Get job execution statistics"""

        stats = {}

        for name, job_stats in self.job_stats.items():
            executions = job_stats["executions"]
            failures = job_stats["failures"]
            total_duration = job_stats["total_duration"]

            stats[name] = {
                "executions": executions,
                "failures": failures,
                "success_rate": ((executions - failures) / executions if executions > 0 else 0),
                "avg_duration_seconds": (total_duration / executions if executions > 0 else 0),
                "last_execution": job_stats["last_execution"],
            }

        return stats


async def main():
    """Demonstrate Redis and logging infrastructure"""

    setup_utf8_logging()
    logging.info("🚀 Starting Redis & Logging Infrastructure")

    # Initialize components
    cache = AdvancedRedisCache()
    await cache.connect()

    logger = StructuredLogger("eq12-demo")
    scheduler = AdvancedCronScheduler(logger)

    # Test cache operations
    await cache.set("odds", "game_123", {"home": 1.85, "away": 1.95}, ttl=300)
    await cache.get("odds", "game_123")
    print("✅ Cache test: {odds}")

    # Test distributed lock
    async with cache.distributed_lock("analysis", "user_456") as acquired:
        if acquired:
            print("✅ Distributed lock acquired")
            await asyncio.sleep(1)  # Simulate work
        else:
            print("❌ Failed to acquire lock")

    # Test structured logging
    logger.log(
        LogLevel.INFO,
        "cache",
        "Cache operation completed",
        metadata={"operation": "get", "key": "odds:game_123"},
        request_id="req_12345",
    )

    # Schedule test job
    def test_job():
        logger.log(LogLevel.INFO, "scheduler", "Test job executed")
        return "Job completed successfully"

    scheduler.schedule_job("test_cleanup", test_job, "every 5 minutes")

    # Get metrics
    await cache.get_metrics()
    print("\n📊 Cache Metrics:")
    print("Hit Rate: {cache_metrics['hit_rate']:.2%}")
    print("Average Latency: {cache_metrics['avg_latency_ms']:.1f}ms")

    logger.get_log_analytics()
    print("\n📈 Log Analytics:")
    print("Total Components: {len(log_analytics['top_components'])}")

    job_stats = scheduler.get_job_statistics()
    print("\n⏰ Scheduler Stats:")
    for name, stats in job_stats.items():
        print(f"{name}: {stats['executions']} executions, {stats['success_rate']:.2%} success")

    print("\n🎉 Redis & Logging Infrastructure Ready!")


if __name__ == "__main__":
    asyncio.run(main())
