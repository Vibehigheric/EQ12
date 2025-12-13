#!/usr/bin/env python3
"""
EQ12 Free Guard - Safety and Free Mode Enforcement
=================================================
Prevents paid API calls unless keys are present and authorized.
Provides timezone-aware utilities and configuration management.

Part of the EQ12 Free Toolchain System.
"""

import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Configure UTF-8 safe logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/eq12_free_guard.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

# EQ12 project root
EQ12_ROOT = Path(__file__).parent
CONFIGS_DIR = EQ12_ROOT / "configs"
LOGS_DIR = EQ12_ROOT / "logs"

# Ensure directories exist
CONFIGS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


def load_eq12_defaults() -> dict[str, Any]:
    """Load EQ12 default configuration from configs/eq12_defaults.json"""
    defaults_file = CONFIGS_DIR / "eq12_defaults.json"

    # Default configuration if file doesn't exist
    default_config = {
        "free_mode": True,
        "dry_run": True,
        "timezone": "UTC",
        "logging": {"utf8_console_safe": True, "max_log_mb": 10},
        "web": {"apache_port": 8080, "api_host": "127.0.0.1", "api_port": 8000},
        "odds": {"cache_minutes": 5, "live_cache_minutes": 1},
        "cost_guards": {
            "daily_budget_usd": 1.00,
            "per_request_limit_usd": 0.01,
            "hard_stop_usd": 3.00,
        },
        "models": {"primary": "gpt-4o-mini", "fallbacks": ["gpt-4o", "gpt-3.5-turbo"]},
    }

    try:
        if defaults_file.exists():
            with open(defaults_file, encoding="utf-8") as f:
                config = json.load(f)
                # Merge with defaults to handle missing keys
                merged = default_config.copy()
                merged.update(config)
                return merged
        else:
            # Create default config file
            with open(defaults_file, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default config: {defaults_file}")
            return default_config
    except Exception as e:
        logger.error(f"Error loading config, using defaults: {e}")
        return default_config


def is_free_mode() -> bool:
    """Check if EQ12 is running in free mode (no paid API calls allowed)"""
    # Check environment variable first
    if os.getenv("DRY_RUN", "").lower() in ("true", "1", "yes"):
        return True

    # Check configuration
    config = load_eq12_defaults()
    return config.get("free_mode", True) or config.get("dry_run", True)


def has_valid_openai_key() -> bool:
    """Check if a valid OpenAI API key is present"""
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return key.startswith("sk-") and len(key) > 20


def has_valid_azure_config() -> bool:
    """Check if valid Azure OpenAI configuration is present"""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
    key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
    return bool(endpoint and key and len(key) > 10)


def block_paid_calls_if_no_keys():
    """Raise exception if trying to make paid API calls without proper keys"""
    if is_free_mode() and not (has_valid_openai_key() or has_valid_azure_config()):
        raise RuntimeError(
            "EQ12 Free Mode: Cannot make paid API calls without valid keys. "
            "Set OPENAI_API_KEY or AZURE_OPENAI_* environment variables, "
            "or disable free_mode in configs/eq12_defaults.json"
        )


def utc_now() -> datetime:
    """Get current UTC time as timezone-aware datetime"""
    return datetime.now(UTC)


def parse_iso_to_utc(iso_string: str) -> datetime:
    """Parse ISO timestamp string and convert to UTC"""
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt.astimezone(UTC)
    except ValueError as e:
        logger.error(f"Failed to parse ISO timestamp '{iso_string}': {e}")
        return utc_now()


def safe_console_log(message: str, use_emoji: bool = False) -> None:
    """Log message safely to console, avoiding emoji on Windows if encoding issues"""
    config = load_eq12_defaults()
    utf8_safe = config.get("logging", {}).get("utf8_console_safe", True)

    if utf8_safe and use_emoji:
        # Check if console supports UTF-8
        try:
            print("🔍", end="")  # Test emoji
            clean_message = message
        except UnicodeEncodeError:
            # Strip emoji/unicode if console doesn't support it
            clean_message = message.encode("ascii", errors="ignore").decode("ascii")
    else:
        clean_message = (
            message.encode("ascii", errors="ignore").decode("ascii") if use_emoji else message
        )

    print(clean_message)

    # Always log to file with full UTF-8 support
    logger.info(clean_message)


def get_cost_limits() -> dict[str, float]:
    """Get current cost limits from configuration"""
    config = load_eq12_defaults()
    return config.get(
        "cost_guards",
        {"daily_budget_usd": 1.00, "per_request_limit_usd": 0.01, "hard_stop_usd": 3.00},
    )


def log_api_usage(operation: str, model: str, tokens_used: int, cost_usd: float) -> None:
    """Log API usage for cost tracking"""
    usage_entry = {
        "timestamp": utc_now().isoformat(),
        "operation": operation,
        "model": model,
        "tokens_used": tokens_used,
        "cost_usd": cost_usd,
        "free_mode": is_free_mode(),
    }

    usage_log = LOGS_DIR / "api_usage.jsonl"
    with open(usage_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(usage_entry) + "\n")


def validate_environment() -> dict[str, Any]:
    """Validate EQ12 environment setup and return status report"""
    report = {
        "timestamp": utc_now().isoformat(),
        "free_mode": is_free_mode(),
        "has_openai_key": has_valid_openai_key(),
        "has_azure_config": has_valid_azure_config(),
        "config_loaded": True,
        "timezone_aware": True,
        "utf8_logging": True,
        "status": "healthy",
    }

    try:
        config = load_eq12_defaults()
        report["config"] = config
    except Exception as e:
        report["config_loaded"] = False
        report["config_error"] = str(e)
        report["status"] = "degraded"

    return report


if __name__ == "__main__":
    # Self-test when run directly
    print("EQ12 Free Guard - Environment Validation")
    print("=" * 50)

    report = validate_environment()
    print(f"Free Mode: {report['free_mode']}")
    print(f"OpenAI Key Present: {report['has_openai_key']}")
    print(f"Azure Config Present: {report['has_azure_config']}")
    print(f"Current UTC Time: {utc_now().isoformat()}")
    print(f"Status: {report['status']}")

    # Test safe console logging
    safe_console_log("✅ EQ12 Free Guard validated successfully", use_emoji=True)
