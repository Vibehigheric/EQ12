from __future__ import annotations

"""Typed configuration helpers for the CLI package."""

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv as _load_dotenv
except ImportError:  # pragma: no cover - optional dependency

    def _load_dotenv(*_: Any, **__: Any) -> bool:
        return False


def _load_env_file() -> None:
    root = Path(__file__).resolve().parent.parent
    env_path = root / ".env"
    if env_path.exists():
        _load_dotenv(env_path)
    else:
        _load_dotenv()


def _coerce_str(value: str | None, default: str) -> str:
    return value if isinstance(value, str) and value else default


def _coerce_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class AppConfig:
    api_key: str
    api_url: str
    model: str
    log_level: str
    timeout: int
    retry_limit: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "OPENAI_API_KEY": self.api_key,
            "OPENAI_API_URL": self.api_url,
            "DEFAULT_MODEL": self.model,
            "LOG_LEVEL": self.log_level,
            "TIMEOUT": self.timeout,
            "RETRY_LIMIT": self.retry_limit,
        }


def load_config(env: Mapping[str, str | None] | None = None) -> AppConfig:
    _load_env_file()
    source: Mapping[str, str | None] = env if env is not None else os.environ
    return AppConfig(
        api_key=_coerce_str(source.get("OPENAI_API_KEY"), ""),
        api_url=_coerce_str(
            source.get("OPENAI_API_URL"),
            "https://api.openai.com/v1/chat/completions",
        ),
        model=_coerce_str(source.get("DEFAULT_MODEL"), "gpt-4o-mini"),
        log_level=_coerce_str(source.get("LOG_LEVEL"), "INFO"),
        timeout=_coerce_int(source.get("TIMEOUT"), 30),
        retry_limit=_coerce_int(source.get("RETRY_LIMIT"), 3),
    )


config: AppConfig = load_config()


def reload_config() -> AppConfig:
    global config
    config = load_config()
    return config


def as_dict() -> dict[str, Any]:
    return config.as_dict()


__all__ = ["AppConfig", "as_dict", "config", "load_config", "reload_config"]
