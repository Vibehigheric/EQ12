"""
EQ12 Budget Guard
================

Cost tracking and circuit breaker system for OpenAI API usage.
Integrates with existing eq12_cost_guards if available.
"""

import json
import logging
import threading
from datetime import UTC, datetime
from typing import Any

from .config import get_config

logger = logging.getLogger(__name__)


class BudgetGuard:
    """
    Budget enforcement with daily/monthly limits and circuit breaker.
    Thread-safe cost tracking with automatic reset.
    """

    def __init__(self):
        self.config = get_config()
        self.lock = threading.Lock()

        # Cost tracking file
        self.cost_file = self.config.log_directory / "budget_tracking.json"

        # Circuit breaker state
        self.circuit_breaker_active = False
        self.circuit_breaker_reason = None

        # Cost per model (tokens)
        self.cost_schedule = {
            "gpt-4o": {"input": 0.0025, "output": 0.010},  # per 1K tokens
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "text-embedding-3-small": {"input": 0.00002, "output": 0.0},
            "text-embedding-3-large": {"input": 0.00013, "output": 0.0},
            "whisper-1": {"input": 0.006, "output": 0.0},  # per minute
            "tts-1": {"input": 0.015, "output": 0.0},  # per 1K chars
            "dall-e-3": {"input": 0.040, "output": 0.0},  # per image (standard)
        }

        # Load existing cost data
        self.cost_data = self._load_cost_data()

        # Try to integrate with existing cost guards
        self.external_guard = None
        try:
            import eq12_cost_guards

            self.external_guard = eq12_cost_guards.CostGuard()
            logger.info("Integrated with existing eq12_cost_guards")
        except ImportError:
            logger.info("Using internal budget guard (eq12_cost_guards not found)")

    def _load_cost_data(self) -> dict[str, Any]:
        """Load cost tracking data from file"""
        if not self.cost_file.exists():
            return self._create_default_cost_data()

        try:
            with open(self.cost_file, encoding="utf-8") as f:
                data = json.load(f)

            # Check if we need to reset daily/monthly counters
            now = datetime.now(UTC)
            last_update = datetime.fromisoformat(data.get("last_update", now.isoformat()))

            # Reset daily if new day
            if now.date() > last_update.date():
                data["daily_spent"] = 0.0
                data["daily_calls"] = 0
                logger.info("Daily budget counter reset")

            # Reset monthly if new month
            if now.month != last_update.month or now.year != last_update.year:
                data["monthly_spent"] = 0.0
                data["monthly_calls"] = 0
                logger.info("Monthly budget counter reset")

            return data

        except Exception as e:
            logger.error(f"Error loading cost data: {e}")
            return self._create_default_cost_data()

    def _create_default_cost_data(self) -> dict[str, Any]:
        """Create default cost tracking structure"""
        return {
            "daily_spent": 0.0,
            "monthly_spent": 0.0,
            "daily_calls": 0,
            "monthly_calls": 0,
            "last_update": datetime.now(UTC).isoformat(),
            "circuit_breaker_triggered": [],
        }

    def _save_cost_data(self):
        """Save cost data to file"""
        self.cost_data["last_update"] = datetime.now(UTC).isoformat()

        try:
            self.cost_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cost_file, "w", encoding="utf-8") as f:
                json.dump(self.cost_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cost data: {e}")

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int = 0) -> float:
        """Estimate cost for a model call"""
        if model not in self.cost_schedule:
            logger.warning(f"Unknown model for cost estimation: {model}")
            return 0.0

        schedule = self.cost_schedule[model]

        # Calculate cost in dollars
        input_cost = (input_tokens / 1000) * schedule["input"]
        output_cost = (output_tokens / 1000) * schedule["output"]

        return input_cost + output_cost

    def check_budget_limits(self, estimated_cost: float = 0.0) -> dict[str, Any]:
        """
        Check if request would exceed budget limits.
        Returns status and whether to allow the request.
        """
        with self.lock:
            daily_projected = self.cost_data["daily_spent"] + estimated_cost
            monthly_projected = self.cost_data["monthly_spent"] + estimated_cost

            # Calculate usage percentages
            daily_usage = (daily_projected / self.config.eq12_budget_daily) * 100
            monthly_usage = (monthly_projected / self.config.eq12_budget_monthly) * 100

            # Determine status
            status = "ok"
            allow_request = True
            warnings = []

            # Check daily limits
            if daily_usage >= 100:
                status = "daily_exceeded"
                allow_request = False
                self.circuit_breaker_active = True
                self.circuit_breaker_reason = "Daily budget exceeded"
            elif daily_usage >= 90:
                status = "daily_warning"
                warnings.append(f"Daily budget at {daily_usage:.1f}%")

            # Check monthly limits
            if monthly_usage >= 100:
                status = "monthly_exceeded"
                allow_request = False
                self.circuit_breaker_active = True
                self.circuit_breaker_reason = "Monthly budget exceeded"
            elif monthly_usage >= 90:
                if status == "ok":
                    status = "monthly_warning"
                warnings.append(f"Monthly budget at {monthly_usage:.1f}%")

            return {
                "status": status,
                "allow_request": allow_request,
                "daily_usage_percent": daily_usage,
                "monthly_usage_percent": monthly_usage,
                "daily_remaining": max(0, self.config.eq12_budget_daily - daily_projected),
                "monthly_remaining": max(0, self.config.eq12_budget_monthly - monthly_projected),
                "warnings": warnings,
                "circuit_breaker_active": self.circuit_breaker_active,
            }

    def record_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int = 0,
        actual_cost: float | None = None,
    ):
        """Record actual API usage and cost"""
        with self.lock:
            # Use actual cost if provided, otherwise estimate
            cost = actual_cost or self.estimate_cost(model, input_tokens, output_tokens)

            # Update counters
            self.cost_data["daily_spent"] += cost
            self.cost_data["monthly_spent"] += cost
            self.cost_data["daily_calls"] += 1
            self.cost_data["monthly_calls"] += 1

            # Save to file
            self._save_cost_data()

            # Log usage
            logger.info(
                f"Recorded usage: {model} ${cost:.4f} "
                f"(daily: ${self.cost_data['daily_spent']:.2f}, "
                f"monthly: ${self.cost_data['monthly_spent']:.2f})"
            )

            # Check if we've crossed thresholds
            budget_check = self.check_budget_limits()
            if budget_check["warnings"]:
                for warning in budget_check["warnings"]:
                    logger.warning(f"Budget alert: {warning}")

    def reset_circuit_breaker(self):
        """Manually reset circuit breaker (admin function)"""
        with self.lock:
            self.circuit_breaker_active = False
            self.circuit_breaker_reason = None
            logger.info("Circuit breaker manually reset")

    def get_status(self) -> dict[str, Any]:
        """Get current budget status for health endpoint"""
        with self.lock:
            budget_check = self.check_budget_limits()

            return {
                "daily_budget": self.config.eq12_budget_daily,
                "monthly_budget": self.config.eq12_budget_monthly,
                "daily_spent": self.cost_data["daily_spent"],
                "monthly_spent": self.cost_data["monthly_spent"],
                "daily_calls": self.cost_data["daily_calls"],
                "monthly_calls": self.cost_data["monthly_calls"],
                "daily_usage_percent": budget_check["daily_usage_percent"],
                "monthly_usage_percent": budget_check["monthly_usage_percent"],
                "circuit_breaker_active": self.circuit_breaker_active,
                "circuit_breaker_reason": self.circuit_breaker_reason,
                "status": budget_check["status"],
            }

    def is_request_allowed(self, estimated_cost: float = 0.0) -> bool:
        """Simple check if request should be allowed"""
        if not self.config.enable_budget_guard:
            return True

        # Use external guard if available
        if self.external_guard:
            try:
                return self.external_guard.is_request_allowed(estimated_cost)
            except Exception as e:
                logger.error(f"Error with external cost guard: {e}")

        # Use internal logic
        budget_check = self.check_budget_limits(estimated_cost)
        return budget_check["allow_request"]
