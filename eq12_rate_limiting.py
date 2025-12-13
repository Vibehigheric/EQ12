"""
EQ12 Rate Limiting & Exponential Backoff Implementation
Handles OpenAI rate limits, quota exhaustion, and intelligent retry logic
"""

import json
import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""

    base_delay: float = 0.5  # Base delay in seconds
    max_delay: float = 60.0  # Maximum delay cap
    backoff_factor: float = 2.0  # Exponential backoff multiplier
    max_retries: int = 6  # Maximum retry attempts
    jitter: bool = True  # Add randomness to delays
    respect_retry_after: bool = True  # Honor Retry-After headers


class ExponentialBackoff:
    """Implements exponential backoff with jitter for API calls"""

    def __init__(self, config: RetryConfig | None = None):
        self.config = config or RetryConfig()
        self.logger = logging.getLogger(__name__)

    def calculate_delay(self, attempt: int, retry_after: float | None = None) -> float:
        """
        Calculate delay for given attempt number

        Args:
            attempt: Current attempt number (0-based)
            retry_after: Server-provided Retry-After value in seconds

        Returns:
            Delay in seconds
        """
        if retry_after and self.config.respect_retry_after:
            # Honor server's Retry-After header
            delay = min(retry_after, self.config.max_delay)
            self.logger.info(f"Using server Retry-After: {delay}s")
            return delay

        # Calculate exponential backoff
        delay = self.config.base_delay * (self.config.backoff_factor**attempt)
        delay = min(delay, self.config.max_delay)

        if self.config.jitter:
            # Add full jitter: random value between 0 and calculated delay
            delay = random.uniform(0, delay)

        return delay

    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """
        Determine if request should be retried based on attempt and exception

        Args:
            attempt: Current attempt number (0-based)
            exception: Exception that occurred

        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.config.max_retries:
            return False

        # Check exception type for retry decision
        if self._is_rate_limit_error(exception):
            return True

        if self._is_quota_exceeded_error(exception):
            # Don't retry quota errors - circuit breaker should handle
            self.logger.warning("Quota exceeded - not retrying")
            return False

        if self._is_transient_error(exception):
            return True

        # Don't retry other errors (auth, invalid request, etc.)
        return False

    def _is_rate_limit_error(self, exception: Exception) -> bool:
        """Check if exception indicates rate limiting"""
        error_msg = str(exception).lower()
        return any(
            phrase in error_msg
            for phrase in [
                "rate limit",
                "too many requests",
                "429",
                "quota exceeded per minute",
            ]
        )

    def _is_quota_exceeded_error(self, exception: Exception) -> bool:
        """Check if exception indicates quota exhaustion"""
        error_msg = str(exception).lower()
        return any(
            phrase in error_msg
            for phrase in [
                "insufficient quota",
                "quota exceeded",
                "billing",
                "usage limit",
            ]
        )

    def _is_transient_error(self, exception: Exception) -> bool:
        """Check if exception is transient (network, server error)"""
        error_msg = str(exception).lower()
        return any(
            phrase in error_msg
            for phrase in [
                "connection",
                "timeout",
                "500",
                "502",
                "503",
                "504",
                "network",
            ]
        )

    def execute_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with exponential backoff retry logic

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Result of successful function execution

        Raises:
            Exception: Last exception if all retries failed
        """
        last_exception = None

        for attempt in range(self.config.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    self.logger.info(f"Request succeeded on attempt {attempt + 1}")
                return result

            except Exception as e:
                last_exception = e

                if not self.should_retry(attempt, e):
                    self.logger.error(f"Not retrying after attempt {attempt + 1}: {e}")
                    break

                if attempt < self.config.max_retries:
                    # Extract Retry-After from response if available
                    retry_after = self._extract_retry_after(e)
                    delay = self.calculate_delay(attempt, retry_after)

                    self.logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)

        # All retries exhausted
        self.logger.error(f"All {self.config.max_retries + 1} attempts failed")
        raise last_exception

    def _extract_retry_after(self, exception: Exception) -> float | None:
        """Extract Retry-After value from exception if available"""
        try:
            # Try to extract from OpenAI exception
            if hasattr(exception, "response") and exception.response:
                headers = getattr(exception.response, "headers", {})
                retry_after = headers.get("Retry-After") or headers.get("retry-after")
                if retry_after:
                    return float(retry_after)

            # Try to parse from error message
            error_str = str(exception)
            if "retry after" in error_str.lower():
                # Extract number from messages like "retry after 20 seconds"
                import re

                match = re.search(r"retry after (\d+)", error_str.lower())
                if match:
                    return float(match.group(1))

        except (ValueError, AttributeError):
            pass

        return None


class RateLimitTracker:
    """Tracks rate limit status and implements circuit breaker logic"""

    def __init__(self, offline_file: str = "logs/.llm_offline.json"):
        self.offline_file = offline_file
        self.logger = logging.getLogger(__name__)

    def is_offline(self) -> bool:
        """Check if service is currently offline due to rate limits"""
        try:
            with open(self.offline_file) as f:
                data = json.load(f)

            if not data.get("offline", False):
                return False

            # Check if offline period has expired
            until_str = data.get("until")
            if until_str:
                until_time = datetime.fromisoformat(until_str.replace("Z", "+00:00"))
                if datetime.now() < until_time.replace(tzinfo=None):
                    return True
                # Offline period expired, clear the flag
                self._clear_offline()
                return False

            return data.get("offline", False)

        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            return False

    def set_offline(self, duration_minutes: int = 60, reason: str = "Rate limit exceeded"):
        """Set service to offline mode for specified duration"""
        until_time = datetime.now() + timedelta(minutes=duration_minutes)

        offline_data = {
            "offline": True,
            "until": until_time.isoformat() + "Z",
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            import os

            os.makedirs(os.path.dirname(self.offline_file), exist_ok=True)

            with open(self.offline_file, "w") as f:
                json.dump(offline_data, f, indent=2)

            self.logger.warning(f"Service set offline until {until_time}: {reason}")

        except Exception as e:
            self.logger.error(f"Failed to set offline status: {e}")

    def _clear_offline(self):
        """Clear offline status"""
        try:
            import os

            if os.path.exists(self.offline_file):
                os.remove(self.offline_file)
            self.logger.info("Service back online")
        except Exception as e:
            self.logger.error(f"Failed to clear offline status: {e}")

    def handle_api_error(self, exception: Exception) -> bool:
        """
        Handle API error and determine if circuit breaker should trip

        Args:
            exception: API exception

        Returns:
            True if circuit breaker tripped, False otherwise
        """
        backoff = ExponentialBackoff()

        if backoff._is_quota_exceeded_error(exception):
            # Trip circuit breaker for quota errors
            self.set_offline(duration_minutes=120, reason=f"Quota exceeded: {exception}")
            return True

        if backoff._is_rate_limit_error(exception):
            # Extract suggested wait time from Retry-After or use default
            retry_after = backoff._extract_retry_after(exception)
            wait_minutes = int((retry_after or 60) / 60) + 5  # Add 5 min buffer

            self.set_offline(duration_minutes=wait_minutes, reason=f"Rate limit: {exception}")
            return True

        return False


# Global instances for easy access
default_backoff = ExponentialBackoff()
default_tracker = RateLimitTracker()


def with_backoff(config: RetryConfig | None = None):
    """Decorator for adding exponential backoff to functions"""

    def decorator(func):
        backoff_instance = ExponentialBackoff(config) if config else default_backoff

        def wrapper(*args, **kwargs):
            return backoff_instance.execute_with_backoff(func, *args, **kwargs)

        return wrapper

    return decorator


# Environment-based configuration
def get_retry_config_from_env() -> RetryConfig:
    """Load retry configuration from environment variables"""
    import os

    return RetryConfig(
        base_delay=float(os.getenv("EQ12_RETRY_BASE_DELAY", "0.5")),
        max_delay=float(os.getenv("EQ12_RETRY_MAX_DELAY", "60.0")),
        backoff_factor=float(os.getenv("EQ12_RETRY_BACKOFF_FACTOR", "2.0")),
        max_retries=int(os.getenv("EQ12_RETRY_MAX_RETRIES", "6")),
        jitter=os.getenv("EQ12_RETRY_JITTER", "1").lower() in ("1", "true", "yes"),
        respect_retry_after=os.getenv("EQ12_RESPECT_RETRY_AFTER", "1").lower()
        in ("1", "true", "yes"),
    )


if __name__ == "__main__":
    # Demo rate limiting behavior
    logging.basicConfig(level=logging.INFO)

    print("🔄 EQ12 Rate Limiting Demo")

    # Test backoff calculation
    backoff = ExponentialBackoff()
    for i in range(5):
        delay = backoff.calculate_delay(i)
        print(f"Attempt {i + 1}: delay = {delay:.2f}s")

    # Test circuit breaker
    tracker = RateLimitTracker()
    print(f"Is offline: {tracker.is_offline()}")

    # Simulate quota error
    quota_error = Exception("insufficient quota")
    if tracker.handle_api_error(quota_error):
        print("Circuit breaker tripped!")

    print("✅ Rate limiting demo complete")
