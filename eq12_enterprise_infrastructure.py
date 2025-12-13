# eq12_enterprise_infrastructure.py
"""
EQ12 Enterprise Infrastructure
Redis caching, WebSocket streaming, observability, metrics, rate limiting
"""

import asyncio
import json
import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import aioredis
import psutil
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
from websockets.server import WebSocketServerProtocol

from eq12_helpers import env_get, setup_utf8_logging

setup_utf8_logging()


@dataclass
class MetricsSnapshot:
    """System metrics snapshot for observability"""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    active_connections: int
    cache_hit_rate: float
    api_requests_per_minute: int
    error_rate: float


@dataclass
class StreamMessage:
    """WebSocket message structure"""

    type: str
    payload: dict[str, Any]
    timestamp: datetime
    client_id: str | None = None


class PrometheusMetrics:
    """Prometheus metrics collector for EQ12"""

    def __init__(self):
        self.registry = CollectorRegistry()

        # Request metrics
        self.request_count = Counter(
            "eq12_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        self.request_duration = Histogram(
            "eq12_request_duration_seconds",
            "Request duration in seconds",
            ["method", "endpoint"],
            registry=self.registry,
        )

        # Cache metrics
        self.cache_operations = Counter(
            "eq12_cache_operations_total",
            "Total cache operations",
            ["operation", "result"],
            registry=self.registry,
        )

        # System metrics
        self.cpu_usage = Gauge(
            "eq12_cpu_usage_percent", "CPU usage percentage", registry=self.registry
        )

        self.memory_usage = Gauge(
            "eq12_memory_usage_percent",
            "Memory usage percentage",
            registry=self.registry,
        )

        # Application metrics
        self.active_sessions = Gauge(
            "eq12_active_sessions",
            "Number of active WebSocket sessions",
            registry=self.registry,
        )

        self.parlay_generations = Counter(
            "eq12_parlay_generations_total",
            "Total parlay generations",
            ["status"],
            registry=self.registry,
        )

        # Start system metrics collector
        self._start_system_metrics()

    def _start_system_metrics(self):
        """Start background system metrics collection"""

        async def collect():
            while True:
                try:
                    self.cpu_usage.set(psutil.cpu_percent())
                    self.memory_usage.set(psutil.virtual_memory().percent)
                except Exception as e:
                    logging.warning(f"Failed to collect system metrics: {e}")
                await asyncio.sleep(10)

        asyncio.create_task(collect())


class RateLimiter:
    """Distributed rate limiter using Redis"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)

    async def check_rate_limit(
        self, key: str, limit: int, window_seconds: int = 60
    ) -> tuple[bool, int]:
        """
        Check if request is within rate limit
        Returns (is_allowed, remaining_requests)
        """
        try:
            pipeline = self.redis.pipeline()
            pipeline.incr(key)
            pipeline.expire(key, window_seconds)
            results = await pipeline.execute()

            current_count = results[0]

            if current_count <= limit:
                return True, limit - current_count
            return False, 0

        except Exception as e:
            self.logger.error(f"Rate limit check failed: {e}")
            return True, limit  # Fail open


class DistributedCache:
    """Enterprise Redis caching layer"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        self.metrics = PrometheusMetrics()

    async def get(self, key: str) -> Any | None:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value:
                self.metrics.cache_operations.labels(operation="get", result="hit").inc()
                return json.loads(value)
            self.metrics.cache_operations.labels(operation="get", result="miss").inc()
            return None
        except Exception as e:
            self.logger.error(f"Cache get failed for {key}: {e}")
            self.metrics.cache_operations.labels(operation="get", result="error").inc()
            return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        try:
            await self.redis.setex(key, ttl, json.dumps(value))
            self.metrics.cache_operations.labels(operation="set", result="success").inc()
            return True
        except Exception as e:
            self.logger.error(f"Cache set failed for {key}: {e}")
            self.metrics.cache_operations.labels(operation="set", result="error").inc()
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            result = await self.redis.delete(key)
            self.metrics.cache_operations.labels(
                operation="delete", result="success" if result else "miss"
            ).inc()
            return bool(result)
        except Exception as e:
            self.logger.error(f"Cache delete failed for {key}: {e}")
            self.metrics.cache_operations.labels(operation="delete", result="error").inc()
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            result = await self.redis.exists(key)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Cache exists check failed for {key}: {e}")
            return False


class WebSocketManager:
    """Enhanced WebSocket manager with room support and message routing"""

    def __init__(self):
        self.clients: dict[str, WebSocketServerProtocol] = {}
        self.rooms: dict[str, list[str]] = {}
        self.logger = logging.getLogger(__name__)
        self.metrics = PrometheusMetrics()

    async def register_client(
        self, websocket: WebSocketServerProtocol, client_id: str | None = None
    ) -> str:
        """Register new WebSocket client"""
        if not client_id:
            client_id = str(uuid.uuid4())

        self.clients[client_id] = websocket
        self.metrics.active_sessions.set(len(self.clients))

        self.logger.info(f"Client {client_id} connected. Total: {len(self.clients)}")
        return client_id

    async def unregister_client(self, client_id: str):
        """Unregister WebSocket client"""
        if client_id in self.clients:
            del self.clients[client_id]

            # Remove from all rooms
            for room_clients in self.rooms.values():
                if client_id in room_clients:
                    room_clients.remove(client_id)

        self.metrics.active_sessions.set(len(self.clients))
        self.logger.info(f"Client {client_id} disconnected. Total: {len(self.clients)}")

    async def join_room(self, client_id: str, room: str):
        """Add client to a room"""
        if room not in self.rooms:
            self.rooms[room] = []

        if client_id not in self.rooms[room]:
            self.rooms[room].append(client_id)
            self.logger.debug(f"Client {client_id} joined room {room}")

    async def leave_room(self, client_id: str, room: str):
        """Remove client from a room"""
        if room in self.rooms and client_id in self.rooms[room]:
            self.rooms[room].remove(client_id)
            self.logger.debug(f"Client {client_id} left room {room}")

    async def broadcast_to_room(self, room: str, message: StreamMessage):
        """Broadcast message to all clients in room"""
        if room not in self.rooms:
            return

        message_json = json.dumps(asdict(message), default=str)
        disconnected_clients = []

        for client_id in self.rooms[room]:
            if client_id in self.clients:
                try:
                    await self.clients[client_id].send(message_json)
                except Exception as e:
                    self.logger.warning(f"Failed to send to client {client_id}: {e}")
                    disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.unregister_client(client_id)

    async def send_to_client(self, client_id: str, message: StreamMessage):
        """Send message to specific client"""
        if client_id in self.clients:
            try:
                message_json = json.dumps(asdict(message), default=str)
                await self.clients[client_id].send(message_json)
            except Exception as e:
                self.logger.warning(f"Failed to send to client {client_id}: {e}")
                await self.unregister_client(client_id)


class HealthChecker:
    """System health monitoring and alerting"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        self.healthy = True
        self.checks: dict[str, Callable] = {}

    def register_check(self, name: str, check_func: Callable):
        """Register health check function"""
        self.checks[name] = check_func

    async def run_checks(self) -> dict[str, Any]:
        """Run all health checks"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_healthy": True,
            "checks": {},
        }

        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                results["checks"][name] = {"healthy": True, "result": result}
            except Exception as e:
                results["checks"][name] = {"healthy": False, "error": str(e)}
                results["overall_healthy"] = False

        self.healthy = results["overall_healthy"]
        return results

    async def redis_check(self) -> str:
        """Redis connectivity check"""
        await self.redis.ping()
        return "Redis connection OK"

    async def system_resources_check(self) -> dict[str, float]:
        """System resource utilization check"""
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

        if cpu > 90 or memory > 90 or disk > 95:
            raise Exception(f"High resource usage: CPU {cpu}%, Memory {memory}%, Disk {disk}%")

        return {"cpu_percent": cpu, "memory_percent": memory, "disk_percent": disk}


class CircuitBreakerService:
    """Distributed circuit breaker with Redis state"""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)

    async def call_with_circuit_breaker(
        self,
        service_name: str,
        func: Callable,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        *args,
        **kwargs,
    ):
        """Execute function with circuit breaker protection"""

        # Check circuit breaker state
        cb_key = f"circuit_breaker:{service_name}"
        state = await self.redis.hgetall(cb_key)

        if state and state.get("state") == "OPEN":
            # Check if timeout has passed
            last_failure = float(state.get("last_failure", 0))
            if time.time() - last_failure < timeout_seconds:
                raise Exception(f"Circuit breaker OPEN for {service_name}")
            # Move to half-open state
            await self.redis.hset(cb_key, "state", "HALF_OPEN")

        try:
            result = (
                await func(*args, **kwargs)
                if asyncio.iscoroutinefunction(func)
                else func(*args, **kwargs)
            )

            # Success - reset circuit breaker
            await self.redis.delete(cb_key)
            return result

        except Exception:
            # Failure - increment counter
            failure_count = int(state.get("failures", 0)) + 1

            if failure_count >= failure_threshold:
                # Open circuit breaker
                await self.redis.hmset(
                    cb_key,
                    {
                        "state": "OPEN",
                        "failures": failure_count,
                        "last_failure": time.time(),
                    },
                )
                await self.redis.expire(cb_key, timeout_seconds * 2)
            else:
                # Increment failure count
                await self.redis.hmset(cb_key, {"state": "CLOSED", "failures": failure_count})

            raise


class EnterpriseInfrastructure:
    """Main infrastructure orchestrator"""

    def __init__(self):
        self.redis_client = None
        self.cache = None
        self.rate_limiter = None
        self.websocket_manager = WebSocketManager()
        self.health_checker = None
        self.circuit_breaker = None
        self.metrics = PrometheusMetrics()
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """Initialize all infrastructure components"""
        try:
            # Initialize Redis
            redis_url = env_get("REDIS_URL", "redis://localhost:6379")
            self.redis_client = aioredis.from_url(redis_url)
            await self.redis_client.ping()

            # Initialize components
            self.cache = DistributedCache(self.redis_client)
            self.rate_limiter = RateLimiter(self.redis_client)
            self.health_checker = HealthChecker(self.redis_client)
            self.circuit_breaker = CircuitBreakerService(self.redis_client)

            # Register health checks
            self.health_checker.register_check("redis", self.health_checker.redis_check)
            self.health_checker.register_check("system", self.health_checker.system_resources_check)

            self.logger.info("Enterprise infrastructure initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize infrastructure: {e}")
            raise

    async def get_metrics_snapshot(self) -> MetricsSnapshot:
        """Get current system metrics snapshot"""
        return MetricsSnapshot(
            timestamp=datetime.now(),
            cpu_percent=psutil.cpu_percent(),
            memory_percent=psutil.virtual_memory().percent,
            disk_usage=psutil.disk_usage("/").percent,
            active_connections=len(self.websocket_manager.clients),
            cache_hit_rate=await self._calculate_cache_hit_rate(),
            api_requests_per_minute=await self._get_api_rpm(),
            error_rate=await self._calculate_error_rate(),
        )

    async def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate from Redis info"""
        try:
            info = await self.redis_client.info("stats")
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            total = hits + misses
            return (hits / total * 100) if total > 0 else 0.0
        except Exception:
            return 0.0

    async def _get_api_rpm(self) -> int:
        """Get API requests per minute from metrics"""
        # This would integrate with your API request counter
        return 0

    async def _calculate_error_rate(self) -> float:
        """Calculate error rate from metrics"""
        # This would calculate from your error metrics
        return 0.0

    async def shutdown(self):
        """Gracefully shutdown infrastructure"""
        if self.redis_client:
            await self.redis_client.close()
        self.logger.info("Infrastructure shutdown complete")


# WebSocket server handler
async def websocket_handler(websocket: WebSocketServerProtocol, path: str):
    """Handle WebSocket connections"""
    infrastructure = EnterpriseInfrastructure()
    await infrastructure.initialize()

    client_id = await infrastructure.websocket_manager.register_client(websocket)

    try:
        async for message in websocket:
            try:
                data = json.loads(message)

                # Handle different message types
                if data.get("type") == "join_room":
                    room = data.get("room")
                    if room:
                        await infrastructure.websocket_manager.join_room(client_id, room)

                elif data.get("type") == "subscribe_metrics":
                    # Send real-time metrics
                    await infrastructure.websocket_manager.join_room(client_id, "metrics")

            except json.JSONDecodeError:
                logger = logging.getLogger(__name__)
                logger.warning(f"Invalid JSON from client {client_id}")

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"WebSocket error for client {client_id}: {e}")
    finally:
        await infrastructure.websocket_manager.unregister_client(client_id)


async def main():
    """Demonstration of enterprise infrastructure"""
    setup_utf8_logging()

    # Initialize infrastructure
    infra = EnterpriseInfrastructure()
    await infra.initialize()

    # Run health checks
    health_result = await infra.health_checker.run_checks()
    print(f"Health Check: {health_result}")

    # Get metrics snapshot
    metrics = await infra.get_metrics_snapshot()
    print(f"Metrics: {asdict(metrics)}")

    # Test cache operations
    await infra.cache.set("test_key", {"data": "test_value"}, ttl=60)
    cached_value = await infra.cache.get("test_key")
    print(f"Cached value: {cached_value}")

    # Test rate limiting
    allowed, remaining = await infra.rate_limiter.check_rate_limit(
        "api:test_user", limit=100, window_seconds=60
    )
    print(f"Rate limit - Allowed: {allowed}, Remaining: {remaining}")

    # Cleanup
    await infra.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
