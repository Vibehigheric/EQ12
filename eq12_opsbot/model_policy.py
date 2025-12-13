"""
EQ12 Model Policy Enforcement
============================

YAML-based allow/deny lists with client-layer blocking.
Prevents usage of unauthorized models.
"""

import logging
import re
from pathlib import Path
from typing import Any

from .config import get_config

logger = logging.getLogger(__name__)


class ModelPolicyError(Exception):
    """Raised when a model is blocked by policy"""

    pass


class ModelPolicy:
    """Model allow/deny policy enforcement"""

    def __init__(self):
        self.config = get_config()

        # Default allowed models (production-safe)
        self.default_allowed = {
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4",
            "gpt-3.5-turbo",
            "text-embedding-3-small",
            "text-embedding-3-large",
            "whisper-1",
            "tts-1",
            "dall-e-3",
        }

        # Default deny patterns (risky/preview models)
        self.default_denied_patterns = [
            r".*-preview$",
            r".*-beta$",
            r".*-alpha$",
            r".*-experimental$",
            r"^o1-.*",  # O1 models (expensive)
            r"^gpt-5-.*",  # GPT-5 variants
            r".*-instruct-.*",
            r".*-vision-.*",
        ]

        # Load custom policy
        self.allowed_models = set(self.default_allowed)
        self.denied_patterns = list(self.default_denied_patterns)

        self._load_policy()

    def _load_policy(self):
        """Load model policy from YAML file"""
        try:
            import yaml

            policy_file = Path("C:/EQ12/configs/models_allowlist.yaml")

            if policy_file.exists():
                with open(policy_file, encoding="utf-8") as f:
                    policy_data = yaml.safe_load(f)

                if policy_data:
                    # Load allowed models
                    if "allowed_models" in policy_data:
                        allowed = policy_data["allowed_models"]
                        if isinstance(allowed, list):
                            self.allowed_models = set(allowed)

                    # Load denied patterns
                    if "denied_patterns" in policy_data:
                        denied = policy_data["denied_patterns"]
                        if isinstance(denied, list):
                            self.denied_patterns = denied

                    # Additional allowed models
                    if "additional_allowed" in policy_data:
                        additional = policy_data["additional_allowed"]
                        if isinstance(additional, list):
                            self.allowed_models.update(additional)

                logger.info(f"Loaded model policy from {policy_file}")
            else:
                logger.info("Using default model policy (no config file found)")

        except ImportError:
            logger.warning("PyYAML not available, using default model policy")
        except Exception as e:
            logger.error(f"Error loading model policy: {e}")

    def is_model_allowed(self, model: str) -> bool:
        """Check if a model is allowed by policy"""
        if not self.config.enable_model_policy:
            return True

        # Check explicit allow list first
        if model in self.allowed_models:
            return True

        # Check deny patterns
        for pattern in self.denied_patterns:
            if re.match(pattern, model, re.IGNORECASE):
                return False

        # If not in allow list and no deny pattern matched,
        # default to deny (whitelist approach)
        return False

    def check_model(self, model: str) -> None:
        """Check model and raise exception if blocked"""
        if not self.is_model_allowed(model):
            # Find which pattern blocked it
            blocked_by = "not in allowlist"
            for pattern in self.denied_patterns:
                if re.match(pattern, model, re.IGNORECASE):
                    blocked_by = f"matches deny pattern: {pattern}"
                    break

            raise ModelPolicyError(
                f"Model '{model}' is blocked by policy ({blocked_by}). "
                f"Allowed models: {sorted(self.allowed_models)[:5]}..."
            )

    def get_allowed_models(self) -> list[str]:
        """Get list of explicitly allowed models"""
        return sorted(self.allowed_models)

    def get_denied_patterns(self) -> list[str]:
        """Get list of deny patterns"""
        return self.denied_patterns

    def add_allowed_model(self, model: str) -> None:
        """Add a model to the allow list (runtime only)"""
        self.allowed_models.add(model)
        logger.info(f"Added {model} to allowed models (runtime only)")

    def remove_allowed_model(self, model: str) -> None:
        """Remove a model from allow list (runtime only)"""
        self.allowed_models.discard(model)
        logger.info(f"Removed {model} from allowed models (runtime only)")

    def get_status(self) -> dict[str, Any]:
        """Get policy status for health endpoint"""
        return {
            "enabled": self.config.enable_model_policy,
            "allowed_models": self.get_allowed_models(),
            "denied_patterns": self.denied_patterns,
            "total_allowed": len(self.allowed_models),
            "total_deny_patterns": len(self.denied_patterns),
        }

    def suggest_alternative(self, blocked_model: str) -> str:
        """Suggest an allowed alternative for a blocked model"""
        # Simple mapping of blocked to allowed alternatives
        alternatives = {
            "gpt-4-preview": "gpt-4o",
            "gpt-4-turbo-preview": "gpt-4o",
            "gpt-3.5-turbo-instruct": "gpt-3.5-turbo",
            "o1-preview": "gpt-4o",
            "o1-mini": "gpt-4o-mini",
        }

        # Direct mapping
        if blocked_model in alternatives:
            return alternatives[blocked_model]

        # Pattern-based suggestions
        if "gpt-5" in blocked_model.lower():
            return "gpt-4o"
        elif "preview" in blocked_model.lower():
            return "gpt-4o-mini"
        elif "instruct" in blocked_model.lower():
            return "gpt-3.5-turbo"

        # Default fallback
        return "gpt-4o-mini"
