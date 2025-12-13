#!/usr/bin/env python3
"""
EQ12 Common Configuration Module
Provides standardized environment variable loading, logging setup, and utility functions
"""

import json
import logging
import os
import pathlib
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# EQ12 Base paths
EQ12_ROOT = pathlib.Path("C:/EQ12") if os.name == "nt" else pathlib.Path("/workspaces/EQ12")
EQ12_LOGS = EQ12_ROOT / "logs"
EQ12_CONFIG = EQ12_ROOT / "configs"


def setup_eq12_logging(
    name: str,
    log_level: int = logging.INFO,
    log_to_file: bool = True,
    log_to_console: bool = True,
) -> logging.Logger:
    """
    Set up standardized EQ12 logging configuration

    Args:
        name: Logger name (usually __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        EQ12_LOGS.mkdir(parents=True, exist_ok=True)
        log_file = EQ12_LOGS / f"eq12_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def load_eq12_env(env_file_path: pathlib.Path | None = None) -> dict[str, str]:
    """
    Load environment variables from .env file with EQ12 standards

    Args:
        env_file_path: Optional path to .env file. Defaults to EQ12_ROOT/.env

    Returns:
        Dictionary of loaded environment variables
    """
    if env_file_path is None:
        env_file_path = EQ12_ROOT / ".env"

    loaded_vars = {}

    if env_file_path.exists():
        try:
            with open(env_file_path, encoding="utf-8") as f:
                for _, line in enumerate(f, 1):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue

                    # Parse KEY=VALUE format
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        # Remove quotes if present
                        if (value.startswith('"') and value.endswith('"')) or (
                            value.startswith("'") and value.endswith("'")
                        ):
                            value = value[1:-1]

                        # Only set if not already in environment
                        if key and value and not os.environ.get(key):
                            os.environ[key] = value
                            loaded_vars[key] = value

        except Exception as e:
            logging.warning(f"Failed to load .env file {env_file_path}: {e}")

    return loaded_vars


def get_api_key(
    key_name: str,
    prompt_text: str | None = None,
    allow_save: bool = True,
    logger: logging.Logger | None = None,
) -> str | None:
    """
    Get API key with standardized prompting and saving logic

    Args:
        key_name: Environment variable name (e.g., 'OPENAI_API_KEY')
        prompt_text: Custom prompt text, or auto-generated if None
        allow_save: Whether to offer saving the key
        logger: Logger instance for messages

    Returns:
        API key string or None if not provided
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    # Check if already in environment
    existing_key = os.environ.get(key_name)
    if existing_key:
        logger.info(f"✅ {key_name} loaded from environment")
        return existing_key

    # Interactive prompting
    if prompt_text is None:
        prompt_text = f"Enter your {key_name}"

    try:
        api_key = input(f"🔑 {prompt_text} (or press Enter to skip): ").strip()

        if not api_key:
            logger.warning(f"⚠️  {key_name} not provided - related features will be disabled")
            return None

        # Set for current session
        os.environ[key_name] = api_key
        logger.info(f"✅ {key_name} set for current session")

        # Offer to save if allowed
        if allow_save:
            save_choice = input("Save this API key for future use? (y/N): ").strip().lower()
            if save_choice.startswith("y"):
                save_api_key_to_env(key_name, api_key, logger)

        return api_key

    except (EOFError, KeyboardInterrupt):
        logger.warning(f"⚠️  {key_name} prompting cancelled")
        return None


def save_api_key_to_env(key_name: str, api_key: str, logger: logging.Logger | None = None) -> bool:
    """
    Save API key to .env file

    Args:
        key_name: Environment variable name
        api_key: API key value
        logger: Logger instance

    Returns:
        True if saved successfully, False otherwise
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    env_file = EQ12_ROOT / ".env"

    try:
        # Read existing content
        existing_lines = []
        if env_file.exists():
            with open(env_file, encoding="utf-8") as f:
                existing_lines = f.readlines()

        # Check if key already exists
        key_exists = False
        for i, line in enumerate(existing_lines):
            if line.strip().startswith(f"{key_name}="):
                existing_lines[i] = f"{key_name}={api_key}\n"
                key_exists = True
                break

        # Add new key if it doesn't exist
        if not key_exists:
            existing_lines.append(f"{key_name}={api_key}\n")

        # Write back to file
        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(existing_lines)

        logger.info(f"✅ {key_name} saved to {env_file}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to save {key_name}: {e}")
        return False


def write_eq12_snapshot(
    data: dict[str, Any], filename: str, logger: logging.Logger | None = None
) -> pathlib.Path:
    """
    Write data snapshot to EQ12 logs directory

    Args:
        data: Data to write as JSON
        filename: Filename (without .json extension)
        logger: Logger instance

    Returns:
        Path to written file
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    EQ12_LOGS.mkdir(parents=True, exist_ok=True)

    # Add timestamp and EQ12 metadata
    enhanced_data = {
        "timestamp": datetime.now().isoformat(),
        "eq12_version": "buffalo_stack_14215",
        "data": data,
    }

    snapshot_path = EQ12_LOGS / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    try:
        with open(snapshot_path, "w", encoding="utf-8") as f:
            try:
                json.dump(enhanced_data, f, indent=2, default=str)

            except OSError as e:
                logging.error(f"Failed to write JSON: {e}")

                raise

        logger.info(f"📝 Snapshot saved: {snapshot_path}")
        return snapshot_path

    except Exception as e:
        logger.error(f"❌ Failed to save snapshot {filename}: {e}")
        raise


def get_eq12_required_keys() -> list[str]:
    """Get list of EQ12 standard API keys"""
    return [
        "OPENAI_API_KEY",
        "ODDS_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
        "CODEX_API_KEY",
    ]


def validate_eq12_environment(logger: logging.Logger | None = None) -> dict[str, bool]:
    """
    Validate EQ12 environment setup

    Returns:
        Dictionary mapping requirement names to validation status
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    results = {}

    # Check directory structure
    results["eq12_root_exists"] = EQ12_ROOT.exists()
    results["eq12_logs_writable"] = True
    try:
        EQ12_LOGS.mkdir(parents=True, exist_ok=True)
        test_file = EQ12_LOGS / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
    except:
        results["eq12_logs_writable"] = False

    # Check for required files
    results["env_file_exists"] = (EQ12_ROOT / ".env").exists()
    results["requirements_exists"] = (EQ12_ROOT / "requirements.txt").exists()

    # Log summary
    passed = sum(results.values())
    total = len(results)
    logger.info(f"🔍 Environment validation: {passed}/{total} checks passed")

    for check, status in results.items():
        symbol = "✅" if status else "❌"
        logger.info(f"  {symbol} {check}")

    return results


# Initialize module logger
logger = setup_eq12_logging(__name__)
logger.info("EQ12 Common Configuration Module loaded")


# JSON Validation Utilities
def validate_json_file(
    file_path: str | Path, schema: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Validate a JSON file and optionally check against a schema.

    Args:
        file_path: Path to JSON file
        schema: Optional schema dictionary for validation

    Returns:
        Dictionary with validation results: {"valid": bool, "error": str, "content": Any}
    """
    result = {"valid": False, "error": None, "content": None}

    try:
        file_path = Path(file_path)
        if not file_path.exists():
            result["error"] = f"File not found: {file_path}"
            return result

        with open(file_path, encoding="utf-8") as f:
            content = json.load(f)

        result["valid"] = True
        result["content"] = content

        # Basic schema validation if provided
        if schema and isinstance(schema, dict) and isinstance(content, dict):
            for required_key in schema.get("required", []):
                if required_key not in content:
                    result["error"] = f"Missing required key: {required_key}"
                    result["valid"] = False
                    break

    except json.JSONDecodeError as e:
        result["error"] = f"JSON decode error: {e}"
    except Exception as e:
        result["error"] = f"Validation error: {e}"

    return result


def load_json_with_fallback(file_path: str | Path, fallback: Any = None) -> Any:
    """Load JSON with safe fallback handling.

    Args:
        file_path: Path to JSON file
        fallback: Value to return if loading fails

    Returns:
        JSON content or fallback value
    """
    try:
        file_path = Path(file_path)
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.warning(f"Failed to load JSON from {file_path}: {e}")
        return fallback


def write_json_safely(file_path: str | Path, data: Any, backup: bool = True) -> bool:
    """Write JSON with safe backup and error handling.

    Args:
        file_path: Path to write JSON file
        data: Data to write
        backup: Whether to create backup of existing file

    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = Path(file_path)

        # Create backup if file exists and backup is requested
        if backup and file_path.exists():
            backup_path = file_path.with_suffix(
                f"{file_path.suffix}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            shutil.copy2(file_path, backup_path)

        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write JSON with proper formatting
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True

    except Exception as e:
        logging.error(f"Failed to write JSON to {file_path}: {e}")
        return False


def get_config_schema(config_type: str) -> dict[str, Any]:
    """Get JSON schema for different config types.

    Args:
        config_type: Type of config ('job_search', 'edgegod_unified', etc.)

    Returns:
        Schema dictionary
    """
    schemas = {
        "job_search": {
            "required": ["keywords", "locations", "min_hourly", "recipient"],
            "optional": ["adzuna_app_id", "adzuna_app_key", "telegram_enabled"],
        },
        "edgegod_unified": {
            "required": ["email_recipient", "telegram_enabled"],
            "optional": ["min_ev_percent", "simulations", "caps"],
        },
        "watchlist": {
            "required": [],
            "optional": [
                "name",
                "url",
                "target_price",
                "store",
                "type",
                "min_discount",
            ],
        },
    }

    return schemas.get(config_type, {"required": [], "optional": []})
