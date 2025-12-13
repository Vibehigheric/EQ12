"""
EQ12 Cost Guards System - Comprehensive budget protection and API quota management
Prevents runaway costs with intelligent rate limiting, budget alerts, and controls
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class CostThreshold:
    """Cost threshold configuration"""

    daily_budget: float
    warning_threshold: float = 0.7  # 70% of budget
    critical_threshold: float = 0.9  # 90% of budget
    emergency_threshold: float = 1.0  # 100% of budget


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""

    requests_per_minute: int = 60
    requests_per_hour: int = 500
    requests_per_day: int = 10000
    burst_allowance: int = 10  # Extra requests for burst


class CostGuards:
    """
    Comprehensive cost protection system

    Features:
    - Real-time budget tracking across all APIs
    - Intelligent rate limiting with burst protection
    - Automatic cost alerts and notifications
    - Emergency circuit breaker functionality
    - Usage analytics and forecasting
    """

    def __init__(self, config_file: str | None = None):
        # Load configuration
        self.config_file = config_file or "configs/cost_guards_config.json"
        self.config = self._load_config()

        # Initialize tracking
        self.usage_log_file = "logs/api_usage.jsonl"
        self.alerts_log_file = "logs/cost_alerts.jsonl"

        # Rate limiting state
        self.rate_limiters = {
            "openai": {"requests": [], "blocked_until": None},
            "azure_openai": {"requests": [], "blocked_until": None},
            "odds_api": {"requests": [], "blocked_until": None},
            "telegram": {"requests": [], "blocked_until": None},
        }

        # Cost tracking
        self.daily_costs = {}
        self.alert_history = []

        # Emergency state
        self.emergency_mode = False
        self.circuit_breaker_active = False

        # Ensure log directories exist
        os.makedirs(os.path.dirname(self.usage_log_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.alerts_log_file), exist_ok=True)

        logger.info("CostGuards system initialized")

    def _load_config(self) -> dict[str, Any]:
        """Load cost guards configuration"""
        default_config = {
            "budgets": {
                "openai": {"daily": 25.0, "monthly": 500.0},
                "azure_openai": {"daily": 25.0, "monthly": 500.0},
                "odds_api": {"daily": 5.0, "monthly": 100.0},
                "telegram": {"daily": 1.0, "monthly": 20.0},
                "total": {"daily": 50.0, "monthly": 1000.0},
            },
            "rate_limits": {
                "openai": {
                    "requests_per_minute": 60,
                    "requests_per_hour": 500,
                    "requests_per_day": 10000,
                },
                "azure_openai": {
                    "requests_per_minute": 60,
                    "requests_per_hour": 1000,
                    "requests_per_day": 20000,
                },
                "odds_api": {
                    "requests_per_minute": 10,
                    "requests_per_hour": 500,
                    "requests_per_day": 5000,
                },
                "telegram": {
                    "requests_per_minute": 20,
                    "requests_per_hour": 100,
                    "requests_per_day": 1000,
                },
            },
            "thresholds": {"warning": 0.7, "critical": 0.9, "emergency": 1.0},
            "alerts": {
                "telegram_notifications": True,
                "email_notifications": False,
                "log_file_alerts": True,
            },
            "circuit_breaker": {
                "enabled": True,
                "failure_threshold": 5,
                "reset_timeout": 300,  # 5 minutes
            },
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_file}: {e}")
        else:
            # Create default config file
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            try:
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created default config at {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to create config file: {e}")

        return default_config

    def check_request_allowed(self, service: str, estimated_cost: float = 0.0) -> tuple[bool, str]:
        """
        Check if a request is allowed based on rate limits and budget

        Args:
            service: Service name (openai, azure_openai, odds_api, etc.)
            estimated_cost: Estimated cost of the request

        Returns:
            Tuple of (allowed, reason)
        """
        # Check emergency mode
        if self.emergency_mode:
            return False, "Emergency mode active - all requests blocked"

        # Check circuit breaker
        if self.circuit_breaker_active:
            return False, "Circuit breaker active - system in recovery mode"

        # Check rate limits
        rate_limit_ok, rate_reason = self._check_rate_limits(service)
        if not rate_limit_ok:
            return False, rate_reason

        # Check budget constraints
        budget_ok, budget_reason = self._check_budget_constraints(service, estimated_cost)
        if not budget_ok:
            return False, budget_reason

        return True, "Request allowed"

    def log_request(
        self,
        service: str,
        cost: float,
        tokens_used: int = 0,
        request_type: str = "api_call",
        metadata: dict[str, Any] | None = None,
    ):
        """Log an API request for tracking and billing"""
        timestamp = datetime.now(UTC)

        # Record the request
        self._record_rate_limit_request(service, timestamp)

        # Log usage
        usage_record = {
            "timestamp": timestamp.isoformat(),
            "service": service,
            "cost": cost,
            "tokens_used": tokens_used,
            "request_type": request_type,
            "metadata": metadata or {},
        }

        try:
            with open(self.usage_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(usage_record) + "\n")
        except Exception as e:
            logger.error(f"Failed to log usage: {e}")

        # Update daily costs
        date_str = timestamp.date().isoformat()
        if date_str not in self.daily_costs:
            self.daily_costs[date_str] = {}
        if service not in self.daily_costs[date_str]:
            self.daily_costs[date_str][service] = 0.0

        self.daily_costs[date_str][service] += cost

        # Check for budget alerts
        self._check_budget_alerts(service, cost)

    def _check_rate_limits(self, service: str) -> tuple[bool, str]:
        """Check if service is within rate limits"""
        if service not in self.rate_limiters:
            return True, "No rate limits configured"

        # Check if service is temporarily blocked
        limiter = self.rate_limiters[service]
        if limiter["blocked_until"]:
            if datetime.now(UTC) < limiter["blocked_until"]:
                remaining = (limiter["blocked_until"] - datetime.now(UTC)).seconds
                return False, f"Rate limit cooldown: {remaining}s remaining"
            else:
                limiter["blocked_until"] = None

        # Get rate limit config
        service_config = self.config.get("rate_limits", {}).get(service, {})
        if not service_config:
            return True, "No rate limits configured for service"

        now = datetime.now(UTC)
        requests = limiter["requests"]

        # Clean old requests
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)

        recent_requests = [req for req in requests if req > minute_ago]
        limiter["requests"] = recent_requests

        # Check minute limit
        if len(recent_requests) >= service_config.get("requests_per_minute", 60):
            self._apply_rate_limit_cooldown(service, 60)
            return False, "Per-minute rate limit exceeded"

        # Check hour limit
        hourly_requests = [req for req in requests if req > hour_ago]
        if len(hourly_requests) >= service_config.get("requests_per_hour", 500):
            self._apply_rate_limit_cooldown(service, 3600)
            return False, "Per-hour rate limit exceeded"

        # Check daily limit
        daily_requests = [req for req in requests if req > day_ago]
        if len(daily_requests) >= service_config.get("requests_per_day", 10000):
            self._apply_rate_limit_cooldown(service, 86400)
            return False, "Daily rate limit exceeded"

        return True, "Within rate limits"

    def _check_budget_constraints(self, service: str, estimated_cost: float) -> tuple[bool, str]:
        """Check if request is within budget constraints"""
        budgets = self.config.get("budgets", {})
        service_budget = budgets.get(service, {})
        total_budget = budgets.get("total", {})

        today = datetime.now(UTC).date().isoformat()

        # Get current daily spending
        current_service_cost = self.daily_costs.get(today, {}).get(service, 0.0)
        current_total_cost = sum(self.daily_costs.get(today, {}).values())

        # Check service daily budget
        service_daily_limit = service_budget.get("daily", 1000.0)
        if current_service_cost + estimated_cost > service_daily_limit:
            msg = (
                f"{service} daily budget exceeded: "
                f"${current_service_cost:.2f} + ${estimated_cost:.2f} "
                f"> ${service_daily_limit:.2f}"
            )
            return False, msg

        # Check total daily budget
        total_daily_limit = total_budget.get("daily", 1000.0)
        if current_total_cost + estimated_cost > total_daily_limit:
            msg = (
                f"Total daily budget exceeded: "
                f"${current_total_cost:.2f} + ${estimated_cost:.2f} "
                f"> ${total_daily_limit:.2f}"
            )
            return False, msg

        return True, "Within budget constraints"

    def _record_rate_limit_request(self, service: str, timestamp: datetime):
        """Record a request for rate limiting"""
        if service in self.rate_limiters:
            self.rate_limiters[service]["requests"].append(timestamp)

    def _apply_rate_limit_cooldown(self, service: str, cooldown_seconds: int):
        """Apply cooldown period to a service"""
        cooldown_until = datetime.now(UTC) + timedelta(seconds=cooldown_seconds)
        self.rate_limiters[service]["blocked_until"] = cooldown_until

        alert = {
            "level": AlertLevel.WARNING.value,
            "service": service,
            "message": f"Rate limit cooldown applied: {cooldown_seconds}s",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self._send_alert(alert)

    def _check_budget_alerts(self, service: str, cost: float):
        """Check if budget thresholds are crossed and send alerts"""
        today = datetime.now(UTC).date().isoformat()
        budgets = self.config.get("budgets", {})
        thresholds = self.config.get("thresholds", {})

        # Check service budget
        service_budget = budgets.get(service, {}).get("daily", 1000.0)
        current_service_cost = self.daily_costs.get(today, {}).get(service, 0.0)
        service_usage = current_service_cost / service_budget

        # Check total budget
        total_budget = budgets.get("total", {}).get("daily", 1000.0)
        current_total_cost = sum(self.daily_costs.get(today, {}).values())
        total_usage = current_total_cost / total_budget

        # Determine alert level
        alert_level = None
        emergency_threshold = thresholds.get("emergency", 1.0)
        if service_usage >= emergency_threshold or total_usage >= emergency_threshold:
            alert_level = AlertLevel.EMERGENCY
            self.emergency_mode = True
        elif service_usage >= thresholds.get("critical", 0.9) or total_usage >= thresholds.get(
            "critical", 0.9
        ):
            alert_level = AlertLevel.CRITICAL
        elif service_usage >= thresholds.get("warning", 0.7) or total_usage >= thresholds.get(
            "warning", 0.7
        ):
            alert_level = AlertLevel.WARNING

        if alert_level:
            alert = {
                "level": alert_level.value,
                "service": service,
                "message": (
                    f"Budget threshold crossed - Service: {service_usage:.1%}, "
                    f"Total: {total_usage:.1%}"
                ),
                "timestamp": datetime.now(UTC).isoformat(),
                "details": {
                    "service_cost": current_service_cost,
                    "service_budget": service_budget,
                    "service_usage_pct": service_usage * 100,
                    "total_cost": current_total_cost,
                    "total_budget": total_budget,
                    "total_usage_pct": total_usage * 100,
                },
            }
            self._send_alert(alert)

    def _send_alert(self, alert: dict[str, Any]):
        """Send budget/rate limit alert"""
        # Log alert
        try:
            with open(self.alerts_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(alert) + "\n")
        except Exception as e:
            logger.error(f"Failed to log alert: {e}")

        # Console output
        level_colors = {"info": "🔵", "warning": "🟡", "critical": "🟠", "emergency": "🔴"}

        color = level_colors.get(alert["level"], "⚪")
        level_upper = alert["level"].upper()
        print(f"{color} COST GUARD ALERT [{level_upper}]: {alert['message']}")

        # Log to system logger
        log_func = {
            "info": logger.info,
            "warning": logger.warning,
            "critical": logger.error,
            "emergency": logger.critical,
        }.get(alert["level"], logger.info)

        log_func(f"Cost Guard Alert: {alert['message']}")

        # Add to alert history
        self.alert_history.append(alert)

        # Keep only recent alerts (last 100)
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]

        # TODO: Implement Telegram/email notifications if configured
        if self.config.get("alerts", {}).get("telegram_notifications"):
            self._send_telegram_alert(alert)

    def _send_telegram_alert(self, alert: dict[str, Any]):
        """Send alert via Telegram (placeholder)"""
        # TODO: Implement Telegram notification
        logger.info(f"Telegram alert: {alert['message']}")

    def get_usage_summary(self, days: int = 1) -> dict[str, Any]:
        """Get comprehensive usage and cost summary"""
        if not os.path.exists(self.usage_log_file):
            return {"error": "No usage log found"}

        try:
            cutoff_date = datetime.now(UTC) - timedelta(days=days)

            service_costs = {}
            service_requests = {}
            hourly_breakdown = {}

            with open(self.usage_log_file, encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        timestamp = datetime.fromisoformat(record["timestamp"])

                        if timestamp >= cutoff_date:
                            service = record.get("service", "unknown")
                            cost = float(record.get("cost", 0))

                            # Service totals
                            service_costs[service] = service_costs.get(service, 0) + cost
                            service_requests[service] = service_requests.get(service, 0) + 1

                            # Hourly breakdown
                            hour = timestamp.strftime("%Y-%m-%d %H:00")
                            if hour not in hourly_breakdown:
                                hourly_breakdown[hour] = {"cost": 0, "requests": 0}
                            hourly_breakdown[hour]["cost"] += cost
                            hourly_breakdown[hour]["requests"] += 1

                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

            total_cost = sum(service_costs.values())
            total_requests = sum(service_requests.values())

            # Get current budgets
            budgets = self.config.get("budgets", {})
            daily_budget = budgets.get("total", {}).get("daily", 50.0)

            return {
                "period_days": days,
                "total_cost": round(total_cost, 2),
                "total_requests": total_requests,
                "daily_budget": daily_budget,
                "budget_used_pct": round((total_cost / (daily_budget * days)) * 100, 1),
                "budget_remaining": round((daily_budget * days) - total_cost, 2),
                "service_breakdown": {
                    service: {
                        "cost": round(cost, 2),
                        "requests": service_requests.get(service, 0),
                        "avg_cost_per_request": round(
                            cost / max(service_requests.get(service, 1), 1), 4
                        ),
                    }
                    for service, cost in service_costs.items()
                },
                "hourly_breakdown": hourly_breakdown,
                "current_rate_limits": self._get_rate_limit_status(),
                "emergency_mode": self.emergency_mode,
                "circuit_breaker_active": self.circuit_breaker_active,
                "recent_alerts": self.alert_history[-5:],  # Last 5 alerts
            }

        except Exception as e:
            return {"error": f"Failed to analyze usage: {e}"}

    def _get_rate_limit_status(self) -> dict[str, Any]:
        """Get current rate limit status for all services"""
        status = {}

        for service, limiter in self.rate_limiters.items():
            now = datetime.now(UTC)

            # Clean old requests
            minute_ago = now - timedelta(minutes=1)
            recent_requests = [req for req in limiter["requests"] if req > minute_ago]

            # Get limits
            service_config = self.config.get("rate_limits", {}).get(service, {})
            minute_limit = service_config.get("requests_per_minute", 60)

            status[service] = {
                "requests_last_minute": len(recent_requests),
                "minute_limit": minute_limit,
                "utilization_pct": round((len(recent_requests) / minute_limit) * 100, 1),
                "blocked_until": (
                    limiter["blocked_until"].isoformat() if limiter["blocked_until"] else None
                ),
            }

        return status

    def reset_emergency_mode(self):
        """Reset emergency mode (admin function)"""
        self.emergency_mode = False
        logger.info("Emergency mode reset")

        alert = {
            "level": AlertLevel.INFO.value,
            "service": "system",
            "message": "Emergency mode reset by administrator",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self._send_alert(alert)

    def activate_circuit_breaker(self, reason: str):
        """Activate circuit breaker protection"""
        self.circuit_breaker_active = True

        alert = {
            "level": AlertLevel.CRITICAL.value,
            "service": "system",
            "message": f"Circuit breaker activated: {reason}",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self._send_alert(alert)

    def reset_circuit_breaker(self):
        """Reset circuit breaker (admin function)"""
        self.circuit_breaker_active = False
        logger.info("Circuit breaker reset")

        alert = {
            "level": AlertLevel.INFO.value,
            "service": "system",
            "message": "Circuit breaker reset by administrator",
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self._send_alert(alert)


# Global cost guards instance
_global_cost_guards = None


def get_cost_guards() -> CostGuards:
    """Get or create global cost guards instance"""
    global _global_cost_guards
    if _global_cost_guards is None:
        _global_cost_guards = CostGuards()
    return _global_cost_guards


def check_request_allowed(service: str, estimated_cost: float = 0.0) -> tuple[bool, str]:
    """Convenience function to check if request is allowed"""
    return get_cost_guards().check_request_allowed(service, estimated_cost)


def log_api_usage(service: str, cost: float, tokens: int = 0, request_type: str = "api_call"):
    """Convenience function to log API usage"""
    get_cost_guards().log_request(service, cost, tokens, request_type)


def test_cost_guards():
    """Test cost guards functionality"""
    try:
        guards = get_cost_guards()

        print("💰 Testing Cost Guards System...")

        # Test rate limiting
        allowed, reason = guards.check_request_allowed("openai", 0.01)
        print(f"✅ Request check: {allowed} - {reason}")

        # Test logging
        guards.log_request("openai", 0.01, 100, "test_request")
        print("✅ Request logged successfully")

        # Test usage summary
        summary = guards.get_usage_summary()
        print(f"📊 Usage Summary: ${summary.get('total_cost', 0):.3f} total cost")

        return True

    except Exception as e:
        print(f"❌ Cost guards test failed: {e}")
        return False


if __name__ == "__main__":
    test_cost_guards()
