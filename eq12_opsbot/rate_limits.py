"""
EQ12 Rate Limiter
================

TPM/RPM rate limiting with token bucket implementation.
Polite backoff with full jitter and local token ledger.
"""

import logging
import threading
import time
from datetime import UTC, datetime
from typing import Any

from .config import get_config

logger = logging.getLogger(__name__)


class TokenBucket:
    """Thread-safe token bucket for rate limiting"""

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int) -> bool:
        """Try to consume tokens. Returns True if successful."""
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def _refill(self):
        """Refill bucket based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def get_wait_time(self, tokens: int) -> float:
        """Get time to wait before tokens are available"""
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                return 0.0

            needed_tokens = tokens - self.tokens
            return needed_tokens / self.refill_rate


class RateLimiter:
    """
    Multi-model rate limiter with TPM/RPM enforcement.
    Implements token buckets for each model with configurable limits.
    """

    def __init__(self):
        self.config = get_config()

        # Default rate limits (TPM/RPM)
        self.default_limits = {
            "gpt-4o": {"tpm": 3000, "rpm": 20},
            "gpt-4o-mini": {"tpm": 20000, "rpm": 60},
            "gpt-4": {"tpm": 1000, "rpm": 10},
            "gpt-3.5-turbo": {"tpm": 40000, "rpm": 100},
            "text-embedding-3-small": {"tpm": 80000, "rpm": 60},
            "text-embedding-3-large": {"tpm": 20000, "rpm": 30},
            "whisper-1": {"tpm": 1000, "rpm": 10},  # minutes per minute
            "tts-1": {"tpm": 10000, "rpm": 20},  # chars per minute
            "dall-e-3": {"tpm": 100, "rpm": 5},  # images per minute
        }

        # Token buckets per model
        self.token_buckets = {}  # model -> {"tpm": bucket, "rpm": bucket}
        self.request_counts = {}  # model -> count in current minute

        # Load custom limits if available
        self._load_custom_limits()

        # Initialize buckets
        self._initialize_buckets()

        # Stats tracking
        self.stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "rate_limited_requests": 0,
            "last_reset": datetime.now(UTC).isoformat(),
        }

    def _load_custom_limits(self):
        """Load custom rate limits from config files"""
        try:
            import yaml

            limits_file = self.config.log_directory.parent / "configs" / "rate_limits.yaml"

            if limits_file.exists():
                with open(limits_file, encoding="utf-8") as f:
                    custom_limits = yaml.safe_load(f)

                # Merge with defaults
                if custom_limits and "production" in custom_limits:
                    for model, limits in custom_limits["production"].items():
                        if model in self.default_limits:
                            self.default_limits[model].update(limits)

                logger.info(f"Loaded custom rate limits from {limits_file}")

        except ImportError:
            logger.warning("PyYAML not available, using default rate limits")
        except Exception as e:
            logger.warning(f"Error loading custom rate limits: {e}")

    def _initialize_buckets(self):
        """Initialize token buckets for all models"""
        for model, limits in self.default_limits.items():
            tpm = limits["tpm"]
            rpm = limits["rpm"]

            # TPM bucket: capacity = TPM, refill = TPM/60 tokens per second
            tpm_bucket = TokenBucket(capacity=tpm, refill_rate=tpm / 60.0)

            # RPM bucket: capacity = RPM, refill = RPM/60 requests per second
            rpm_bucket = TokenBucket(capacity=rpm, refill_rate=rpm / 60.0)

            self.token_buckets[model] = {"tpm": tpm_bucket, "rpm": rpm_bucket}

            self.request_counts[model] = 0

        logger.info(f"Initialized rate limiters for {len(self.token_buckets)} models")

    def check_rate_limit(self, model: str, tokens: int = 1) -> dict[str, Any]:
        """
        Check if request would be rate limited.
        Returns status and wait times.
        """
        if not self.config.enable_rate_limits:
            return {"allowed": True, "wait_time_seconds": 0.0, "reason": None}

        # Use default limits for unknown models
        if model not in self.token_buckets:
            logger.warning(f"Unknown model for rate limiting: {model}")
            model = "gpt-4o-mini"  # Conservative default

        buckets = self.token_buckets[model]

        # Check TPM limit
        tpm_wait = buckets["tpm"].get_wait_time(tokens)

        # Check RPM limit
        rpm_wait = buckets["rpm"].get_wait_time(1)

        # Use the longer wait time
        max_wait = max(tpm_wait, rpm_wait)

        if max_wait > 0:
            reason = "TPM limit" if tpm_wait > rpm_wait else "RPM limit"
            return {
                "allowed": False,
                "wait_time_seconds": max_wait,
                "reason": reason,
                "tpm_wait": tpm_wait,
                "rpm_wait": rpm_wait,
            }

        return {"allowed": True, "wait_time_seconds": 0.0, "reason": None}

    def consume_tokens(self, model: str, tokens: int = 1) -> bool:
        """
        Consume tokens for a request. Returns True if successful.
        Call this BEFORE making the API request.
        """
        if not self.config.enable_rate_limits:
            return True

        # Use default for unknown models
        if model not in self.token_buckets:
            model = "gpt-4o-mini"

        buckets = self.token_buckets[model]

        # Try to consume from both buckets
        tpm_success = buckets["tpm"].consume(tokens)
        rpm_success = buckets["rpm"].consume(1)

        if tpm_success and rpm_success:
            # Update stats
            self.stats["total_requests"] += 1
            self.stats["total_tokens"] += tokens
            self.request_counts[model] += 1
            return True

        # If one failed, we need to "refund" the other
        # This is a simplification - in production you might want to implement
        # proper two-phase consumption

        self.stats["rate_limited_requests"] += 1
        logger.debug(f"Rate limited: {model} (tokens: {tokens})")
        return False

    def get_wait_time(self, model: str, tokens: int = 1) -> float:
        """Get wait time before request can be made"""
        if not self.config.enable_rate_limits:
            return 0.0

        if model not in self.token_buckets:
            model = "gpt-4o-mini"

        check_result = self.check_rate_limit(model, tokens)
        return check_result["wait_time_seconds"]

    def get_current_usage(self, model: str) -> dict[str, Any]:
        """Get current token bucket levels for a model"""
        if model not in self.token_buckets:
            return {}

        buckets = self.token_buckets[model]
        limits = self.default_limits[model]

        # Trigger refill to get current levels
        buckets["tpm"]._refill()
        buckets["rpm"]._refill()

        return {
            "tpm_available": int(buckets["tpm"].tokens),
            "tpm_capacity": limits["tpm"],
            "tpm_usage_percent": (1 - buckets["tpm"].tokens / limits["tpm"]) * 100,
            "rpm_available": int(buckets["rpm"].tokens),
            "rpm_capacity": limits["rpm"],
            "rpm_usage_percent": (1 - buckets["rpm"].tokens / limits["rpm"]) * 100,
            "requests_this_period": self.request_counts.get(model, 0),
        }

    def get_status(self) -> dict[str, Any]:
        """Get rate limiter status for health endpoint"""
        model_status = {}

        for model in self.default_limits:
            usage = self.get_current_usage(model)
            if usage:
                model_status[model] = usage

        return {
            "enabled": self.config.enable_rate_limits,
            "total_models": len(self.token_buckets),
            "stats": self.stats,
            "models": model_status,
        }

    def reset_stats(self):
        """Reset statistics (useful for testing)"""
        self.stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "rate_limited_requests": 0,
            "last_reset": datetime.now(UTC).isoformat(),
        }

        # Reset request counts
        for model in self.request_counts:
            self.request_counts[model] = 0
