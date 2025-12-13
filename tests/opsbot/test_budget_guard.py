"""Test budget guard functionality and cost tracking."""

import threading
import time
from unittest.mock import patch

from eq12_opsbot.budget_guard import BudgetGuard


class TestBudgetGuard:
    """Test budget guard cost tracking and limits."""

    def test_budget_guard_initialization(self, temp_eq12_dir):
        """Test budget guard initializes with correct defaults."""
        budget_guard = BudgetGuard(daily_limit=5.0, monthly_limit=120.0, eq12_root=temp_eq12_dir)

        assert budget_guard.daily_limit == 5.0
        assert budget_guard.monthly_limit == 120.0
        assert not budget_guard.circuit_breaker_active
        assert budget_guard.usage_data["daily_spent"] == 0.0
        assert budget_guard.usage_data["monthly_spent"] == 0.0

    def test_cost_estimation(self, temp_eq12_dir):
        """Test model cost estimation accuracy."""
        budget_guard = BudgetGuard(eq12_root=temp_eq12_dir)

        # Test GPT-4o-mini cost (should be cheaper)
        cost_mini = budget_guard.estimate_cost("gpt-4o-mini", 1000, 500)

        # Test GPT-4o cost (should be more expensive)
        cost_4o = budget_guard.estimate_cost("gpt-4o", 1000, 500)

        assert cost_mini > 0
        assert cost_4o > cost_mini
        assert isinstance(cost_mini, float)
        assert isinstance(cost_4o, float)

    def test_usage_recording(self, temp_eq12_dir):
        """Test usage recording updates daily and monthly totals."""
        budget_guard = BudgetGuard(eq12_root=temp_eq12_dir)

        initial_daily = budget_guard.usage_data["daily_spent"]
        initial_monthly = budget_guard.usage_data["monthly_spent"]

        # Record usage
        test_cost = 1.50
        budget_guard.record_usage("gpt-4o-mini", test_cost)

        assert budget_guard.usage_data["daily_spent"] == initial_daily + test_cost
        assert budget_guard.usage_data["monthly_spent"] == initial_monthly + test_cost

    def test_budget_limit_warnings(self, temp_eq12_dir):
        """Test budget limit warning thresholds."""
        budget_guard = BudgetGuard(daily_limit=10.0, monthly_limit=100.0, eq12_root=temp_eq12_dir)

        # Record usage below warning threshold (< 70%)
        budget_guard.record_usage("gpt-4o-mini", 5.0)
        result = budget_guard.check_budget_limits("gpt-4o-mini", 1000, 500)
        assert result["status"] == "ok"

        # Record usage to warning threshold (70-90%)
        budget_guard.record_usage("gpt-4o-mini", 2.0)  # Now at 7.0/10.0 = 70%
        result = budget_guard.check_budget_limits("gpt-4o-mini", 1000, 500)
        assert result["status"] == "warning"

        # Record usage to critical threshold (90-100%)
        budget_guard.record_usage("gpt-4o-mini", 2.0)  # Now at 9.0/10.0 = 90%
        result = budget_guard.check_budget_limits("gpt-4o-mini", 1000, 500)
        assert result["status"] == "critical"

    def test_circuit_breaker_activation(self, temp_eq12_dir):
        """Test circuit breaker activates when budget exceeded."""
        budget_guard = BudgetGuard(daily_limit=5.0, monthly_limit=50.0, eq12_root=temp_eq12_dir)

        # Exceed daily budget
        budget_guard.record_usage("gpt-4o", 6.0)

        result = budget_guard.check_budget_limits("gpt-4o", 1000, 500)

        assert result["status"] == "blocked"
        assert budget_guard.circuit_breaker_active
        assert "circuit breaker" in result["message"].lower()

    def test_thread_safety(self, temp_eq12_dir):
        """Test budget guard is thread-safe for concurrent usage."""
        budget_guard = BudgetGuard(eq12_root=temp_eq12_dir)

        def record_concurrent_usage():
            for _ in range(10):
                budget_guard.record_usage("gpt-4o-mini", 0.1)
                time.sleep(0.01)

        threads = [threading.Thread(target=record_concurrent_usage) for _ in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have recorded 5 threads * 10 calls * $0.1 = $5.0
        assert budget_guard.usage_data["daily_spent"] == 5.0

    def test_usage_persistence(self, temp_eq12_dir):
        """Test usage data persists to file correctly."""
        budget_guard1 = BudgetGuard(eq12_root=temp_eq12_dir)
        budget_guard1.record_usage("gpt-4o-mini", 2.50)

        # Create new instance (should load persisted data)
        budget_guard2 = BudgetGuard(eq12_root=temp_eq12_dir)

        assert budget_guard2.usage_data["daily_spent"] == 2.50
        assert budget_guard2.usage_data["monthly_spent"] == 2.50

    def test_external_integration_fallback(self, temp_eq12_dir):
        """Test fallback when eq12_cost_guards not available."""
        with patch("eq12_opsbot.budget_guard.import_module") as mock_import:
            mock_import.side_effect = ImportError("Module not found")

            budget_guard = BudgetGuard(eq12_root=temp_eq12_dir)

            # Should still work with internal implementation
            result = budget_guard.check_budget_limits("gpt-4o-mini", 1000, 500)
            assert result["status"] == "ok"

    def test_reset_circuit_breaker(self, temp_eq12_dir):
        """Test manual circuit breaker reset functionality."""
        budget_guard = BudgetGuard(daily_limit=1.0, eq12_root=temp_eq12_dir)

        # Trigger circuit breaker
        budget_guard.record_usage("gpt-4o", 2.0)
        assert budget_guard.circuit_breaker_active

        # Reset circuit breaker
        budget_guard.reset_circuit_breaker()
        assert not budget_guard.circuit_breaker_active

    def test_get_budget_summary(self, temp_eq12_dir):
        """Test budget summary provides correct statistics."""
        budget_guard = BudgetGuard(daily_limit=10.0, monthly_limit=100.0, eq12_root=temp_eq12_dir)

        budget_guard.record_usage("gpt-4o-mini", 3.0)
        budget_guard.record_usage("gpt-4o", 2.0)

        summary = budget_guard.get_budget_summary()

        assert summary["daily_spent"] == 5.0
        assert summary["monthly_spent"] == 5.0
        assert summary["daily_percentage"] == 50.0
        assert summary["monthly_percentage"] == 5.0
        assert not summary["circuit_breaker_active"]
        assert "models_used" in summary
