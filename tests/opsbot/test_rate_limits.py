"""Test rate limiting functionality."""

import threading
import time

from eq12_opsbot.rate_limits import RateLimiter


class TestRateLimiter:
    """Test rate limiting with token bucket algorithm."""

    def test_rate_limiter_initialization(self, temp_eq12_dir):
        """Test rate limiter initializes with correct defaults."""
        rate_limiter = RateLimiter(eq12_root=temp_eq12_dir)

        # Should have default models configured
        assert "gpt-4o-mini" in rate_limiter.limits
        assert "gpt-4o" in rate_limiter.limits

        # Check default limits
        assert rate_limiter.limits["gpt-4o-mini"]["tpm"] > 0
        assert rate_limiter.limits["gpt-4o-mini"]["rpm"] > 0

    def test_token_availability_check(self, temp_eq12_dir):
        """Test checking token availability without consuming."""
        rate_limiter = RateLimiter(eq12_root=temp_eq12_dir)

        # Fresh limiter should have tokens available
        available = rate_limiter.check_rate_limit("gpt-4o-mini", 100, 1)

        assert available["allowed"] is True
        assert available["wait_time"] == 0
        assert "tokens_available" in available
        assert "requests_available" in available

    def test_token_consumption(self, temp_eq12_dir):
        """Test token consumption reduces availability."""
        rate_limiter = RateLimiter(eq12_root=temp_eq12_dir)

        # Check initial availability
        before = rate_limiter.check_rate_limit("gpt-4o-mini", 1000, 1)
        initial_tokens = before["tokens_available"]

        # Consume tokens
        rate_limiter.consume_tokens("gpt-4o-mini", 1000, 1)

        # Check availability after consumption
        after = rate_limiter.check_rate_limit("gpt-4o-mini", 0, 0)

        assert after["tokens_available"] == initial_tokens - 1000

    def test_rate_limit_enforcement(self, temp_eq12_dir):
        """Test rate limiting blocks when limits exceeded."""
        # Create rate limiter with very low limits for testing
        custom_limits = {"gpt-4o-mini": {"tpm": 100, "rpm": 2}}

        rate_limiter = RateLimiter(eq12_root=temp_eq12_dir)
        rate_limiter.limits["gpt-4o-mini"] = custom_limits["gpt-4o-mini"]
        rate_limiter._initialize_buckets()

        # First two requests should be allowed
        result1 = rate_limiter.check_rate_limit("gpt-4o-mini", 40, 1)
        assert result1["allowed"] is True
        rate_limiter.consume_tokens("gpt-4o-mini", 40, 1)

        result2 = rate_limiter.check_rate_limit("gpt-4o-mini", 40, 1)
        assert result2["allowed"] is True
        rate_limiter.consume_tokens("gpt-4o-mini", 40, 1)

        # Third request should be rate limited (exceeds RPM)
        result3 = rate_limiter.check_rate_limit("gpt-4o-mini", 40, 1)
        assert result3["allowed"] is False
        assert result3["wait_time"] > 0

    def test_token_refill(self, temp_eq12_dir):
        """Test token buckets refill over time."""
        # Create rate limiter with small bucket for quick testing
        rate_limiter = RateLimiter(eq12_root=temp_eq12_dir)
        rate_limiter.limits["test-model"] = {"tpm": 60, "rpm": 60}  # 1 token/second
        rate_limiter._initialize_buckets()

        # Consume all tokens
        rate_limiter.consume_tokens("test-model", 60, 60)

        # Should be rate limited immediately
        result_before = rate_limiter.check_rate_limit("test-model", 1, 1)
        assert result_before["allowed"] is False

        # Wait for refill (simulate time passage)
        time.sleep(1.1)

        # Should have tokens available again
        result_after = rate_limiter.check_rate_limit("test-model", 1, 1)
        assert result_after["allowed"] is True

    def test_wait_time_calculation(self, temp_eq12_dir):
        """Test accurate wait time calculation when rate limited."""
        rate_limiter = RateLimiter(eq12_root=temp_eq12_dir)

        # Set very restrictive limits
        rate_limiter.limits["test-model"] = {"tpm": 30, "rpm": 2}
        rate_limiter._initialize_buckets()

        # Exhaust the buckets
        rate_limiter.consume_tokens("test-model", 30, 2)

        # Check wait time
        result = rate_limiter.check_rate_limit("test-model", 10, 1)

        assert result["allowed"] is False
        assert result["wait_time"] > 0
        assert result["wait_time"] <= 60  # Should be reasonable
        assert "limited_by" in result

    def test_thread_safety(self, temp_eq12_dir):
        """Test rate limiter is thread-safe."""
        rate_limiter = RateLimiter(eq12_root=temp_eq12_dir)

        successful_requests = []

        def make_requests():
            for i in range(10):
                result = rate_limiter.check_rate_limit("gpt-4o-mini", 100, 1)
                if result["allowed"]:
                    rate_limiter.consume_tokens("gpt-4o-mini", 100, 1)
                    successful_requests.append(i)
                time.sleep(0.01)

        threads = [threading.Thread(target=make_requests) for _ in range(3)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have some successful requests (exact number depends on timing)
        assert len(successful_requests) > 0

    def test_custom_limits_loading(self, temp_eq12_dir):
        """Test loading custom rate limits from YAML config."""
        # Create custom config
        config_dir = temp_eq12_dir / "configs"
        config_file = config_dir / "rate_limits.yaml"

        with open(config_file, "w") as f:
            f.write(
                """
production:
  gpt-4o-mini:
    tpm: 50000
    rpm: 100
  custom-model:
    tpm: 1000
    rpm: 10
"""
            )

        rate_limiter = RateLimiter(eq12_root=temp_eq12_dir)

        # Should load custom limits
        assert rate_limiter.limits["gpt-4o-mini"]["tpm"] == 50000
        assert "custom-model" in rate_limiter.limits

    def test_stats_tracking(self, temp_eq12_dir):
        """Test rate limiter tracks statistics correctly."""
        rate_limiter = RateLimiter(eq12_root=temp_eq12_dir)

        # Make some requests
        rate_limiter.consume_tokens("gpt-4o-mini", 100, 1)
        rate_limiter.consume_tokens("gpt-4o", 200, 1)

        stats = rate_limiter.get_stats()

        assert stats["total_requests"] >= 2
        assert "per_model_stats" in stats
        assert "gpt-4o-mini" in stats["per_model_stats"]
        assert stats["per_model_stats"]["gpt-4o-mini"]["requests"] >= 1

    def test_jitter_application(self, temp_eq12_dir):
        """Test jitter is applied to wait times."""
        rate_limiter = RateLimiter(eq12_root=temp_eq12_dir)

        # Exhaust limits to trigger wait time
        rate_limiter.limits["test-model"] = {"tpm": 10, "rpm": 1}
        rate_limiter._initialize_buckets()
        rate_limiter.consume_tokens("test-model", 10, 1)

        # Get multiple wait times - should vary due to jitter
        wait_times = []
        for _ in range(5):
            result = rate_limiter.check_rate_limit("test-model", 5, 1)
            wait_times.append(result["wait_time"])

        # Wait times should not all be identical (jitter applied)
        unique_wait_times = len(set(wait_times))
        assert unique_wait_times > 1 or wait_times[0] == 0
