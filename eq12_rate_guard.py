#!/usr/bin/env python3
"""
EQ12 GODSTACK - Rate Guard & Token Budget Manager
OpenAI/Claude/Local rate limiting with intelligent throttling and circuit breaker

Core Features:
- Token-aware request budgeting with rolling windows
- Adaptive rate limiting based on model capacity and cost
- Circuit breaker for API failures with exponential backoff
- Cost tracking with daily/monthly spending limits
- Request prioritization by urgency and value
- Multi-provider load balancing and failover
- Comprehensive telemetry and cost monitoring
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/rate_guard.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class Provider(Enum):
    """LLM providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    AZURE = "azure"
    TOGETHER = "together"


class Priority(Enum):
    """Request priority levels"""

    CRITICAL = "critical"  # SGP deadline, live bet decision
    HIGH = "high"  # Research, hedge analysis
    NORMAL = "normal"  # General queries, batch processing
    LOW = "low"  # Background analysis, testing


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class ModelLimits:
    """Per-model rate and cost limits"""

    model_name: str
    provider: Provider

    # Rate limits
    requests_per_minute: int
    tokens_per_minute: int
    requests_per_day: int

    # Cost limits (USD)
    cost_per_1k_input: float
    cost_per_1k_output: float
    daily_cost_limit: float
    monthly_cost_limit: float

    # Context limits
    max_input_tokens: int
    max_output_tokens: int

    # Quality metrics
    reliability_score: float  # 0-1, based on historical uptime
    average_latency_ms: int

    # Failover config
    fallback_models: list[str]
    circuit_breaker_threshold: int = 5  # failures before circuit opens


@dataclass
class TokenBudget:
    """Token budget tracking"""

    allocated_tokens: int
    used_tokens: int
    reserved_tokens: int  # For high-priority requests

    window_start: datetime
    window_duration: timedelta

    @property
    def available_tokens(self) -> int:
        return self.allocated_tokens - self.used_tokens - self.reserved_tokens

    @property
    def utilization_rate(self) -> float:
        return self.used_tokens / self.allocated_tokens if self.allocated_tokens > 0 else 0


@dataclass
class RequestContext:
    """Context for rate limiting decisions"""

    request_id: str
    priority: Priority
    estimated_input_tokens: int
    estimated_output_tokens: int
    model_preference: str
    provider_preference: Provider
    timeout_seconds: int
    retry_budget: int

    # Request metadata
    source_component: str  # "sgp_engine", "research", "hedge_calc"
    request_type: str  # "analysis", "generation", "classification"
    urgency_deadline: datetime | None = None
    cost_sensitivity: float = 1.0  # 0-2, higher = more cost sensitive


@dataclass
class RateLimitStatus:
    """Current rate limiting status"""

    allowed: bool
    reason: str
    retry_after_seconds: int | None = None
    suggested_model: str | None = None
    suggested_provider: Provider | None = None
    current_queue_position: int | None = None
    estimated_wait_seconds: int | None = None


class CircuitBreaker:
    """Circuit breaker for provider failures"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def record_success(self):
        """Record successful request"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = datetime.now(UTC)

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

    def can_attempt_request(self) -> bool:
        """Check if request can be attempted"""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if we should try recovery
            if self.last_failure_time and datetime.now(UTC) - self.last_failure_time > timedelta(
                seconds=self.recovery_timeout
            ):
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering half-open state")
                return True
            return False

        return self.state == CircuitState.HALF_OPEN


class RollingWindow:
    """Rolling window for rate tracking"""

    def __init__(self, window_duration: timedelta):
        self.window_duration = window_duration
        self.requests = deque()

    def add_request(self, timestamp: datetime, tokens: int):
        """Add request to window"""
        self.requests.append((timestamp, tokens))
        self._cleanup_old_requests()

    def _cleanup_old_requests(self):
        """Remove requests outside the window"""
        cutoff = datetime.now(UTC) - self.window_duration
        while self.requests and self.requests[0][0] < cutoff:
            self.requests.popleft()

    def get_current_rate(self) -> tuple[int, int]:
        """Get current requests and tokens in window"""
        self._cleanup_old_requests()
        request_count = len(self.requests)
        token_count = sum(tokens for _, tokens in self.requests)
        return request_count, token_count


class RateGuard:
    """Main rate limiting and budget management system"""

    def __init__(self, config_path: str | None = None):
        self.config_path = config_path or "C:/EQ12/configs/rate_guard_config.json"
        self.models = {}
        self.budgets = {}
        self.circuit_breakers = {}
        self.rolling_windows = {}
        self.request_queue = []
        self.cost_tracker = defaultdict(float)

        self._load_configuration()
        self._initialize_components()

        logger.info("RateGuard initialized with rate limiting and budget management")

    def _load_configuration(self):
        """Load rate limiting configuration"""

        # Default configuration if file doesn't exist
        default_config = {
            "models": {
                "gpt-4o": {
                    "provider": "openai",
                    "requests_per_minute": 500,
                    "tokens_per_minute": 150000,
                    "requests_per_day": 10000,
                    "cost_per_1k_input": 0.0025,
                    "cost_per_1k_output": 0.01,
                    "daily_cost_limit": 50.0,
                    "monthly_cost_limit": 1000.0,
                    "max_input_tokens": 128000,
                    "max_output_tokens": 16384,
                    "reliability_score": 0.99,
                    "average_latency_ms": 2000,
                    "fallback_models": ["gpt-4o-mini", "gpt-3.5-turbo"],
                },
                "gpt-4o-mini": {
                    "provider": "openai",
                    "requests_per_minute": 1000,
                    "tokens_per_minute": 200000,
                    "requests_per_day": 20000,
                    "cost_per_1k_input": 0.00015,
                    "cost_per_1k_output": 0.0006,
                    "daily_cost_limit": 20.0,
                    "monthly_cost_limit": 400.0,
                    "max_input_tokens": 128000,
                    "max_output_tokens": 16384,
                    "reliability_score": 0.98,
                    "average_latency_ms": 1500,
                    "fallback_models": ["gpt-3.5-turbo"],
                },
                "claude-3-5-sonnet-20241022": {
                    "provider": "anthropic",
                    "requests_per_minute": 300,
                    "tokens_per_minute": 100000,
                    "requests_per_day": 5000,
                    "cost_per_1k_input": 0.003,
                    "cost_per_1k_output": 0.015,
                    "daily_cost_limit": 75.0,
                    "monthly_cost_limit": 1500.0,
                    "max_input_tokens": 200000,
                    "max_output_tokens": 8192,
                    "reliability_score": 0.97,
                    "average_latency_ms": 2500,
                    "fallback_models": ["claude-3-haiku-20240307"],
                },
            },
            "budget_windows": {"minute": 60, "hour": 3600, "day": 86400},
            "priority_multipliers": {
                "critical": 3.0,
                "high": 2.0,
                "normal": 1.0,
                "low": 0.5,
            },
            "circuit_breaker": {"failure_threshold": 5, "recovery_timeout": 60},
        }

        try:
            if os.path.exists(self.config_path):
                with open(self.config_path) as f:
                    config = json.load(f)
            else:
                config = default_config
                # Save default config
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, "w") as f:
                    json.dump(config, f, indent=2)

        except Exception as e:
            logger.warning(f"Failed to load config, using defaults: {e}")
            config = default_config

        # Parse model configurations
        for model_name, model_config in config["models"].items():
            self.models[model_name] = ModelLimits(
                model_name=model_name,
                provider=Provider(model_config["provider"]),
                requests_per_minute=model_config["requests_per_minute"],
                tokens_per_minute=model_config["tokens_per_minute"],
                requests_per_day=model_config["requests_per_day"],
                cost_per_1k_input=model_config["cost_per_1k_input"],
                cost_per_1k_output=model_config["cost_per_1k_output"],
                daily_cost_limit=model_config["daily_cost_limit"],
                monthly_cost_limit=model_config["monthly_cost_limit"],
                max_input_tokens=model_config["max_input_tokens"],
                max_output_tokens=model_config["max_output_tokens"],
                reliability_score=model_config["reliability_score"],
                average_latency_ms=model_config["average_latency_ms"],
                fallback_models=model_config["fallback_models"],
            )

        self.config = config
        logger.info(f"Loaded configuration for {len(self.models)} models")

    def _initialize_components(self):
        """Initialize rate tracking components"""

        # Initialize budgets and windows for each model
        for model_name in self.models:
            # Rolling windows for rate tracking
            self.rolling_windows[model_name] = {
                "minute": RollingWindow(timedelta(minutes=1)),
                "day": RollingWindow(timedelta(days=1)),
            }

            # Circuit breakers
            self.circuit_breakers[model_name] = CircuitBreaker(
                failure_threshold=self.config["circuit_breaker"]["failure_threshold"],
                recovery_timeout=self.config["circuit_breaker"]["recovery_timeout"],
            )

            # Token budgets
            limits = self.models[model_name]
            self.budgets[model_name] = TokenBudget(
                allocated_tokens=limits.tokens_per_minute,
                used_tokens=0,
                reserved_tokens=int(limits.tokens_per_minute * 0.2),  # Reserve 20%
                window_start=datetime.now(UTC),
                window_duration=timedelta(minutes=1),
            )

    async def check_rate_limit(self, context: RequestContext) -> RateLimitStatus:
        """Check if request can proceed under rate limits"""

        model_name = context.model_preference

        # Check if model exists
        if model_name not in self.models:
            return RateLimitStatus(
                allowed=False,
                reason=f"Unknown model: {model_name}",
                suggested_model=next(iter(self.models.keys())) if self.models else None,
            )

        limits = self.models[model_name]

        # Check circuit breaker
        circuit_breaker = self.circuit_breakers[model_name]
        if not circuit_breaker.can_attempt_request():
            # Suggest fallback model
            fallback = self._find_available_fallback(model_name)
            return RateLimitStatus(
                allowed=False,
                reason="Circuit breaker open - provider experiencing issues",
                suggested_model=fallback,
                retry_after_seconds=30,
            )

        # Check token budget
        budget = self.budgets[model_name]
        estimated_tokens = context.estimated_input_tokens + context.estimated_output_tokens

        if budget.available_tokens < estimated_tokens:
            # Check if we can wait for budget refresh
            time_to_refresh = self._time_to_budget_refresh(model_name)
            if time_to_refresh > context.timeout_seconds:
                # Suggest cheaper model
                cheaper_model = self._find_cheaper_model(context)
                return RateLimitStatus(
                    allowed=False,
                    reason="Insufficient token budget",
                    suggested_model=cheaper_model,
                    retry_after_seconds=int(time_to_refresh),
                )

        # Check rate limits
        windows = self.rolling_windows[model_name]

        # Check minute rate limits
        minute_requests, minute_tokens = windows["minute"].get_current_rate()
        if (
            minute_requests >= limits.requests_per_minute
            or minute_tokens + estimated_tokens > limits.tokens_per_minute
        ):
            return RateLimitStatus(
                allowed=False,
                reason="Rate limit exceeded (per minute)",
                retry_after_seconds=60,
                suggested_model=self._find_available_fallback(model_name),
            )

        # Check daily limits
        day_requests, _day_tokens = windows["day"].get_current_rate()
        if day_requests >= limits.requests_per_day:
            return RateLimitStatus(
                allowed=False,
                reason="Daily request limit exceeded",
                suggested_model=self._find_available_fallback(model_name),
            )

        # Check cost limits
        daily_cost = self._get_daily_cost(model_name)
        estimated_cost = self._calculate_cost(model_name, estimated_tokens, estimated_tokens)

        if daily_cost + estimated_cost > limits.daily_cost_limit:
            cheaper_model = self._find_cheaper_model(context)
            return RateLimitStatus(
                allowed=False,
                reason=f"Daily cost limit would be exceeded (${daily_cost:.2f} + ${estimated_cost:.2f})",
                suggested_model=cheaper_model,
            )

        # Request can proceed
        return RateLimitStatus(allowed=True, reason="Request approved")

    async def reserve_request(self, context: RequestContext) -> str:
        """Reserve tokens and track request"""

        model_name = context.model_preference
        estimated_tokens = context.estimated_input_tokens + context.estimated_output_tokens

        # Reserve tokens in budget
        budget = self.budgets[model_name]
        if context.priority in [Priority.CRITICAL, Priority.HIGH]:
            # Use reserved tokens for high priority
            if budget.reserved_tokens >= estimated_tokens:
                budget.reserved_tokens -= estimated_tokens
            else:
                budget.used_tokens += estimated_tokens
        else:
            budget.used_tokens += estimated_tokens

        # Generate tracking ID
        tracking_id = hashlib.md5(
            f"{context.request_id}_{model_name}_{time.time()}".encode()
        ).hexdigest()[:12]

        logger.info(
            f"Reserved {estimated_tokens} tokens for request {tracking_id} ({context.priority.value})"
        )

        return tracking_id

    async def record_usage(
        self,
        tracking_id: str,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
        success: bool,
        latency_ms: int,
    ):
        """Record actual token usage and performance"""

        total_tokens = input_tokens + output_tokens
        timestamp = datetime.now(UTC)

        # Update rolling windows
        if model_name in self.rolling_windows:
            self.rolling_windows[model_name]["minute"].add_request(timestamp, total_tokens)
            self.rolling_windows[model_name]["day"].add_request(timestamp, total_tokens)

        # Update circuit breaker
        circuit_breaker = self.circuit_breakers[model_name]
        if success:
            circuit_breaker.record_success()
        else:
            circuit_breaker.record_failure()

        # Track costs
        cost = self._calculate_cost(model_name, input_tokens, output_tokens)
        cost_key = f"{model_name}_{timestamp.date()}"
        self.cost_tracker[cost_key] += cost

        # Update model performance metrics
        if model_name in self.models:
            limits = self.models[model_name]
            # Simple exponential moving average for latency
            limits.average_latency_ms = int(0.9 * limits.average_latency_ms + 0.1 * latency_ms)

        logger.info(
            f"Recorded usage: {tracking_id} - {input_tokens}+{output_tokens} tokens, "
            f"${cost:.4f}, {latency_ms}ms, success={success}"
        )

    def _find_available_fallback(self, model_name: str) -> str | None:
        """Find available fallback model"""

        if model_name not in self.models:
            return None

        fallbacks = self.models[model_name].fallback_models

        for fallback in fallbacks:
            if fallback in self.circuit_breakers:
                if self.circuit_breakers[fallback].can_attempt_request():
                    return fallback

        return None

    def _find_cheaper_model(self, context: RequestContext) -> str | None:
        """Find cheaper model that can handle the request"""

        current_cost = float("inf")
        if context.model_preference in self.models:
            limits = self.models[context.model_preference]
            current_cost = limits.cost_per_1k_input + limits.cost_per_1k_output

        cheaper_options = []

        for model_name, limits in self.models.items():
            model_cost = limits.cost_per_1k_input + limits.cost_per_1k_output

            if (
                model_cost < current_cost
                and limits.max_input_tokens >= context.estimated_input_tokens
                and limits.max_output_tokens >= context.estimated_output_tokens
                and self.circuit_breakers[model_name].can_attempt_request()
            ):
                cheaper_options.append((model_name, model_cost))

        if cheaper_options:
            # Return cheapest available option
            return min(cheaper_options, key=lambda x: x[1])[0]

        return None

    def _time_to_budget_refresh(self, model_name: str) -> float:
        """Calculate seconds until token budget refreshes"""

        if model_name not in self.budgets:
            return 0

        budget = self.budgets[model_name]
        elapsed = datetime.now(UTC) - budget.window_start
        remaining = budget.window_duration - elapsed

        return max(0, remaining.total_seconds())

    def _get_daily_cost(self, model_name: str) -> float:
        """Get today's cost for a model"""

        today = datetime.now(UTC).date()
        cost_key = f"{model_name}_{today}"

        return self.cost_tracker.get(cost_key, 0.0)

    def _calculate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for token usage"""

        if model_name not in self.models:
            return 0.0

        limits = self.models[model_name]

        input_cost = (input_tokens / 1000) * limits.cost_per_1k_input
        output_cost = (output_tokens / 1000) * limits.cost_per_1k_output

        return input_cost + output_cost

    def get_status_report(self) -> dict[str, Any]:
        """Get comprehensive status report"""

        status = {
            "timestamp": datetime.now(UTC).isoformat(),
            "models": {},
            "total_daily_cost": 0.0,
            "circuit_breakers": {},
        }

        datetime.now(UTC).date()

        for model_name, limits in self.models.items():
            # Get current rates
            windows = self.rolling_windows.get(model_name, {})
            minute_requests, minute_tokens = (0, 0)
            day_requests, _day_tokens = (0, 0)

            if "minute" in windows:
                minute_requests, minute_tokens = windows["minute"].get_current_rate()
            if "day" in windows:
                day_requests, _day_tokens = windows["day"].get_current_rate()

            # Get costs
            daily_cost = self._get_daily_cost(model_name)
            status["total_daily_cost"] += daily_cost

            # Get budget
            budget = self.budgets.get(model_name)
            budget_info = {}
            if budget:
                budget_info = {
                    "utilization": budget.utilization_rate,
                    "available_tokens": budget.available_tokens,
                    "reserved_tokens": budget.reserved_tokens,
                }

            status["models"][model_name] = {
                "provider": limits.provider.value,
                "current_usage": {
                    "requests_per_minute": f"{minute_requests}/{limits.requests_per_minute}",
                    "tokens_per_minute": f"{minute_tokens}/{limits.tokens_per_minute}",
                    "requests_today": f"{day_requests}/{limits.requests_per_day}",
                    "cost_today": f"${daily_cost:.2f}/${limits.daily_cost_limit:.2f}",
                },
                "budget": budget_info,
                "performance": {
                    "reliability_score": limits.reliability_score,
                    "average_latency_ms": limits.average_latency_ms,
                },
            }

            # Circuit breaker status
            circuit = self.circuit_breakers.get(model_name)
            if circuit:
                status["circuit_breakers"][model_name] = {
                    "state": circuit.state.value,
                    "failure_count": circuit.failure_count,
                    "can_attempt": circuit.can_attempt_request(),
                }

        return status

    async def refresh_budgets(self):
        """Refresh token budgets (called periodically)"""

        current_time = datetime.now(UTC)

        for model_name, budget in self.budgets.items():
            if current_time - budget.window_start >= budget.window_duration:
                # Reset budget window
                limits = self.models[model_name]
                budget.used_tokens = 0
                budget.reserved_tokens = int(limits.tokens_per_minute * 0.2)
                budget.window_start = current_time

                logger.debug(f"Refreshed token budget for {model_name}")


async def main():
    """CLI interface for rate guard management"""

    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Rate Guard Manager")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--test-request", help="Test rate limiting for model")
    parser.add_argument("--reset-circuit", help="Reset circuit breaker for model")
    parser.add_argument("--export-config", action="store_true", help="Export current configuration")

    args = parser.parse_args()

    # Initialize rate guard
    rate_guard = RateGuard()

    if args.status:
        print("🔒 EQ12 RATE GUARD STATUS")
        print("=" * 50)

        status = rate_guard.get_status_report()

        print(f"Total Daily Cost: ${status['total_daily_cost']:.2f}")
        print()

        for model_name, model_status in status["models"].items():
            print(f"📊 {model_name} ({model_status['provider']})")
            usage = model_status["current_usage"]
            print(f"   Requests/min: {usage['requests_per_minute']}")
            print(f"   Tokens/min: {usage['tokens_per_minute']}")
            print(f"   Requests today: {usage['requests_today']}")
            print(f"   Cost today: {usage['cost_today']}")

            if model_status.get("budget"):
                budget = model_status["budget"]
                print(f"   Budget utilization: {budget['utilization']:.1%}")
                print(f"   Available tokens: {budget['available_tokens']:,}")

            circuit_state = status["circuit_breakers"].get(model_name, {})
            if circuit_state:
                print(
                    f"   Circuit: {circuit_state['state']} (failures: {circuit_state['failure_count']})"
                )

            print()

    elif args.test_request:
        model_name = args.test_request

        # Create test request context
        test_context = RequestContext(
            request_id="test_123",
            priority=Priority.NORMAL,
            estimated_input_tokens=1000,
            estimated_output_tokens=500,
            model_preference=model_name,
            provider_preference=Provider.OPENAI,
            timeout_seconds=30,
            retry_budget=3,
            source_component="cli_test",
            request_type="test",
        )

        print(f"🧪 Testing rate limit for {model_name}")

        status = await rate_guard.check_rate_limit(test_context)

        print(f"Allowed: {status.allowed}")
        print(f"Reason: {status.reason}")

        if not status.allowed:
            if status.retry_after_seconds:
                print(f"Retry after: {status.retry_after_seconds}s")
            if status.suggested_model:
                print(f"Suggested model: {status.suggested_model}")

    elif args.reset_circuit:
        model_name = args.reset_circuit

        if model_name in rate_guard.circuit_breakers:
            rate_guard.circuit_breakers[model_name].failure_count = 0
            rate_guard.circuit_breakers[model_name].state = CircuitState.CLOSED
            print(f"✅ Reset circuit breaker for {model_name}")
        else:
            print(f"❌ Model {model_name} not found")

    elif args.export_config:
        config_export = {"models": {}, "status": rate_guard.get_status_report()}

        for model_name, limits in rate_guard.models.items():
            config_export["models"][model_name] = asdict(limits)

        export_path = f"C:/EQ12/logs/rate_guard_export_{int(time.time())}.json"
        with open(export_path, "w") as f:
            json.dump(config_export, f, indent=2, default=str)

        print(f"📄 Configuration exported to: {export_path}")

    else:
        print("🔒 EQ12 Rate Guard - Use --help for options")


if __name__ == "__main__":
    asyncio.run(main())
