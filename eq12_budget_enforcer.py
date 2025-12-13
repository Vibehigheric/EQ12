"""
Budget Policy Enforcement System for EQ12
Ensures strict compliance with $120/month and $4/day limits
"""

import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class BudgetPolicyEnforcer:
    """Enforces strict budget compliance with intelligent routing"""

    def __init__(self, policy_path: str | None = None):
        if not policy_path:
            # Try multiple locations for config file
            possible_paths = [
                Path(__file__).parent / "configs" / "eq12_budget_policy.yaml",
                Path(__file__).parent.parent / "configs" / "eq12_budget_policy.yaml",
                Path("C:/EQ12/configs/eq12_budget_policy.yaml"),
            ]

            policy_path = None
            for path in possible_paths:
                if path.exists():
                    policy_path = path
                    break

            if not policy_path:
                policy_path = possible_paths[-1]  # Default to C:/EQ12/configs

        with open(policy_path) as f:
            self.policy = yaml.safe_load(f)

        month_str = datetime.now(UTC).strftime("%Y%m")
        self.usage_file = Path("C:/EQ12/logs") / f"budget_usage_{month_str}.json"
        self._load_usage()

    def _load_usage(self):
        """Load current usage statistics"""
        try:
            if self.usage_file.exists():
                with open(self.usage_file) as f:
                    self.usage = json.load(f)
            else:
                self._reset_usage()
        except Exception as e:
            logger.warning(f"Failed to load usage, resetting: {e}")
            self._reset_usage()

    def _reset_usage(self):
        """Reset usage tracking"""
        self.usage = {
            "daily": {},
            "monthly_total": 0.0,
            "buckets": {bucket: {"daily": {}, "monthly": 0.0} for bucket in self.policy["buckets"]},
            "features": {},
        }

    def _save_usage(self):
        """Save current usage to file"""
        try:
            with open(self.usage_file, "w") as f:
                json.dump(self.usage, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save usage: {e}")

    def _get_today_key(self) -> str:
        """Get today's date key"""
        return datetime.now(UTC).strftime("%Y-%m-%d")

    def _get_daily_usage(self, bucket: str | None = None) -> float:
        """Get today's usage for a bucket or total"""
        today = self._get_today_key()

        if bucket:
            return self.usage["buckets"][bucket]["daily"].get(today, 0.0)
        else:
            return self.usage["daily"].get(today, 0.0)

    def check_request_allowed(
        self, feature: str, model: str, input_tokens: int, output_tokens: int
    ) -> tuple[bool, str, dict[str, Any]]:
        """
        Check if a request is allowed under budget policy
        Returns: (allowed, reason, routing_info)
        """
        # Get feature config
        if feature not in self.policy["routing"]:
            return False, f"Feature {feature} not in policy", {}

        feature_config = self.policy["routing"][feature]
        bucket = feature_config["require_budget"]

        # Calculate cost
        model_config = self.policy["buckets"][bucket]["models"].get(model)
        if not model_config:
            return False, f"Model {model} not allowed for bucket {bucket}", {}

        cost = self._calculate_cost(model, input_tokens, output_tokens)

        # Check daily caps
        daily_usage = self._get_daily_usage()
        bucket_daily_usage = self._get_daily_usage(bucket)

        if daily_usage + cost > self.policy["daily_cap_usd"]:
            msg = (
                f"Daily cap exceeded: ${daily_usage:.3f} + ${cost:.3f} "
                f"> ${self.policy['daily_cap_usd']}"
            )
            return False, msg, {}

        if bucket_daily_usage + cost > self.policy["buckets"][bucket]["cap_usd"]:
            return False, f"Bucket {bucket} daily cap exceeded", {}

        # Check monthly cap
        if self.usage["monthly_total"] + cost > self.policy["monthly_cap_usd"]:
            return False, "Monthly cap exceeded", {}

        # Check feature limits
        today = self._get_today_key()
        feature_usage = self.usage["features"].get(feature, {}).get(today, {"calls": 0})

        if "max_calls_day" in feature_config:
            if feature_usage["calls"] >= feature_config["max_calls_day"]:
                return False, f"Feature {feature} daily call limit exceeded", {}

        # Check token limits
        max_input = feature_config.get("max_tokens_input")
        if max_input and input_tokens > max_input:
            msg = f"Input tokens exceed limit: {input_tokens} > {max_input}"
            return False, msg, {}

        max_output = feature_config.get("max_tokens_output")
        if max_output and output_tokens > max_output:
            msg = f"Output tokens exceed limit: {output_tokens} > {max_output}"
            return False, msg, {}  # Determine routing
        routing_info = {
            "model": model,
            "cost": cost,
            "bucket": bucket,
            "feature": feature,
            "priority": feature_config.get("priority", "medium"),
            "degraded": False,
        }

        # Check for degradation
        usage_percent = daily_usage / self.policy["daily_cap_usd"]
        if usage_percent >= 0.90:
            degradation_rules = self.policy["degradation"]["at_90_percent"]
            if any(rule.get("switch_to_mini") for rule in degradation_rules):
                bucket_models = self.policy["buckets"][bucket]["models"]
                if model == "gpt-4o" and "gpt-4o-mini" in bucket_models:
                    routing_info["model"] = "gpt-4o-mini"
                    routing_info["degraded"] = True
                    cost = self._calculate_cost("gpt-4o-mini", input_tokens, output_tokens)
                    routing_info["cost"] = cost

        if usage_percent >= 0.95:
            degradation_rules = self.policy["degradation"]["at_95_percent"]
            if any(rule.get("block_new_requests") for rule in degradation_rules):
                allowed_features = []
                for rule in degradation_rules:
                    if "allow_only" in rule:
                        allowed_features.extend(rule["allow_only"])

                if feature not in allowed_features:
                    return False, "Budget at 95%, blocking non-critical requests", {}

        if usage_percent >= 1.0:
            return False, "Daily budget exhausted", {}

        return True, "Request allowed", routing_info

    def record_usage(
        self, feature: str, model: str, input_tokens: int, output_tokens: int, cost: float
    ):
        """Record actual usage after API call"""
        today = self._get_today_key()

        # Update daily total
        if today not in self.usage["daily"]:
            self.usage["daily"][today] = 0.0
        self.usage["daily"][today] += cost

        # Update monthly total
        self.usage["monthly_total"] += cost

        # Update bucket usage
        feature_config = self.policy["routing"][feature]
        bucket = feature_config["require_budget"]

        if today not in self.usage["buckets"][bucket]["daily"]:
            self.usage["buckets"][bucket]["daily"][today] = 0.0
        self.usage["buckets"][bucket]["daily"][today] += cost
        self.usage["buckets"][bucket]["monthly"] += cost

        # Update feature usage
        if feature not in self.usage["features"]:
            self.usage["features"][feature] = {}
        if today not in self.usage["features"][feature]:
            self.usage["features"][feature][today] = {"calls": 0, "cost": 0.0}

        self.usage["features"][feature][today]["calls"] += 1
        self.usage["features"][feature][today]["cost"] += cost

        self._save_usage()

        # Log usage
        daily_total = self.usage["daily"][today]
        monthly_total = self.usage["monthly_total"]
        logger.info(
            f"Budget usage recorded: {feature} {model} ${cost:.4f} "
            f"(daily: ${daily_total:.3f}, monthly: ${monthly_total:.3f})"
        )

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a request"""
        # Find model pricing in any bucket
        for bucket_config in self.policy["buckets"].values():
            if model in bucket_config["models"]:
                model_config = bucket_config["models"][model]
                input_rate = model_config["cost_per_1k_input"]
                output_rate = model_config["cost_per_1k_output"]
                input_cost = (input_tokens / 1000) * input_rate
                output_cost = (output_tokens / 1000) * output_rate
                return input_cost + output_cost

        # Fallback pricing
        fallback_pricing = {
            "gpt-4o": {"input": 0.0025, "output": 0.01},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        }

        if model in fallback_pricing:
            pricing = fallback_pricing[model]
            input_cost = (input_tokens / 1000) * pricing["input"]
            output_cost = (output_tokens / 1000) * pricing["output"]
            return input_cost + output_cost

        return 0.01  # Safe fallback

    def get_status(self) -> dict[str, Any]:
        """Get current budget status"""
        daily_usage = self._get_daily_usage()
        daily_cap = self.policy["daily_cap_usd"]
        monthly_cap = self.policy["monthly_cap_usd"]
        monthly_usage = self.usage["monthly_total"]

        status = {
            "daily_usage": daily_usage,
            "daily_cap": daily_cap,
            "daily_remaining": max(0, daily_cap - daily_usage),
            "daily_percent": (daily_usage / daily_cap) * 100,
            "monthly_usage": monthly_usage,
            "monthly_cap": monthly_cap,
            "monthly_remaining": max(0, monthly_cap - monthly_usage),
            "monthly_percent": (monthly_usage / monthly_cap) * 100,
            "buckets": {},
        }

        # Bucket status
        for bucket, bucket_config in self.policy["buckets"].items():
            bucket_usage = self._get_daily_usage(bucket)
            status["buckets"][bucket] = {
                "usage": bucket_usage,
                "cap": bucket_config["cap_usd"],
                "remaining": max(0, bucket_config["cap_usd"] - bucket_usage),
                "percent": (bucket_usage / bucket_config["cap_usd"]) * 100,
            }

        return status

    def cleanup_old_usage(self, days_to_keep: int = 32):
        """Clean up old usage data"""
        cutoff = datetime.now(UTC) - timedelta(days=days_to_keep)
        cutoff_str = cutoff.strftime("%Y-%m-%d")

        # Clean daily usage
        self.usage["daily"] = {
            date: usage for date, usage in self.usage["daily"].items() if date >= cutoff_str
        }

        # Clean bucket daily usage
        for bucket in self.usage["buckets"]:
            bucket_daily = self.usage["buckets"][bucket]["daily"]
            self.usage["buckets"][bucket]["daily"] = {
                date: usage for date, usage in bucket_daily.items() if date >= cutoff_str
            }

        # Clean feature usage
        for feature in self.usage["features"]:
            self.usage["features"][feature] = {
                date: usage
                for date, usage in self.usage["features"][feature].items()
                if date >= cutoff_str
            }

        self._save_usage()


# Global instance


budget_enforcer = BudgetPolicyEnforcer()
