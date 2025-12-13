#!/usr/bin/env python3
"""
Enhanced EQ12 OpenAI Client with Async/Sync Compatibility and Model Fallbacks
Fixes asyncio.run() issues and provides comprehensive error handling
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from typing import Any

# UTF-8 safety for Windows
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from eq12_async_compat import run_coro_blocking
from eq12_llm_offline import LLMOffline

logger = logging.getLogger(__name__)


@dataclass
class OpenAIResponse:
    """Enhanced OpenAI response wrapper with metadata"""

    content: str
    model: str
    usage: dict[str, Any] | None = None
    finish_reason: str | None = None
    metadata: dict[str, Any] | None = None
    success: bool = True
    error: str | None = None


def _load_api_key() -> str | None:
    """Load API key from multiple sources"""
    # 1) Environment variable
    key = os.getenv("OPENAI_API_KEY") or os.getenv("CHATGPT_API_KEY")
    if key and key.startswith("sk-"):
        return key

    # 2) Credentials files
    for path in ["keys/credentials.json", "configs/credentials.json", ".env.json"]:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            candidates = [
                data.get("OPENAI_API_KEY"),
                data.get("openai_api_key"),
                data.get("openai", {}).get("api_key"),
                data.get("openai", {}).get("key"),
            ]

            for candidate in candidates:
                if candidate and candidate.startswith("sk-"):
                    return candidate

        except (FileNotFoundError, json.JSONDecodeError):
            continue

    return None


def _get_fallback_models() -> list[str]:
    """Get fallback model list from environment"""
    fallbacks = os.getenv("OPENAI_FALLBACK_MODELS", "")
    if not fallbacks:
        return ["gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]

    return [model.strip() for model in fallbacks.split(",") if model.strip()]


class EQ12OpenAIClient:
    """
    Production-ready OpenAI client with:
    - Async/sync compatibility
    - Model fallbacks
    - Circuit breaker integration
    - Quota management
    - UTF-8 safety
    """

    def __init__(self, primary_model: str | None = None):
        self.primary_model = primary_model or os.getenv("OPENAI_MODEL", "gpt-4o")
        self.fallback_models = _get_fallback_models()
        self.api_key = _load_api_key()
        self.client = None
        self.async_client = None
        self.mode = "offline"
        self._init_clients()

    def _init_clients(self):
        """Initialize OpenAI clients if conditions are met"""
        # Check if we should be offline
        if LLMOffline.is_offline():
            logger.info("LLM offline mode active - using local fallbacks")
            return

        if os.getenv("EQ12_USE_LLM", "1") == "0":
            logger.info("EQ12_USE_LLM=0 - staying offline")
            return

        if not self.api_key:
            logger.warning("No OpenAI API key found - staying offline")
            return

        try:
            from openai import AsyncOpenAI, OpenAI

            # Disable auto-retries (we handle retries)
            self.client = OpenAI(api_key=self.api_key, max_retries=0, timeout=30.0)

            self.async_client = AsyncOpenAI(api_key=self.api_key, max_retries=0, timeout=30.0)

            self.mode = "online"
            logger.info(f"OpenAI client initialized - primary: {self.primary_model}")

        except ImportError:
            logger.error("OpenAI library not installed")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")

    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        return self.mode == "online" and not LLMOffline.is_offline()

    async def chat_async(self, messages: list[dict[str, Any]], **kwargs) -> OpenAIResponse:
        """Async chat completion with model fallbacks"""
        if not self.is_available():
            return OpenAIResponse(
                content="🛡️ OpenAI offline - using local heuristics",
                model="offline",
                success=False,
                error="offline_mode",
            )

        # Try primary model first, then fallbacks
        models_to_try = [self.primary_model, *self.fallback_models]

        for model in models_to_try:
            try:
                response = await self.async_client.chat.completions.create(
                    model=model, messages=messages, **kwargs
                )

                return OpenAIResponse(
                    content=response.choices[0].message.content or "",
                    model=response.model,
                    usage=response.usage.dict() if response.usage else None,
                    finish_reason=response.choices[0].finish_reason,
                    success=True,
                )

            except Exception as e:
                error_msg = str(e).lower()

                # Trip circuit breaker on quota issues
                if "insufficient_quota" in error_msg or "billing" in error_msg:
                    LLMOffline.trip(reason="quota_exhausted")
                    logger.error("Quota exhausted - circuit breaker activated")
                    break

                # Try next model on rate limits or temporary issues
                if any(term in error_msg for term in ["429", "rate limit", "timeout", "temporary"]):
                    logger.warning(f"Model {model} unavailable, trying fallback")
                    continue

                # Other errors - try next model
                logger.warning(f"Model {model} error: {e}")
                continue

        return OpenAIResponse(
            content="🛡️ All models unavailable - using local heuristics",
            model="fallback",
            success=False,
            error="all_models_failed",
        )

    def chat_sync(
        self, messages: list[dict[str, Any]], timeout: float = 30, **kwargs
    ) -> OpenAIResponse:
        """Synchronous chat completion - works in any context"""
        try:
            return run_coro_blocking(self.chat_async(messages, **kwargs), timeout=timeout)
        except Exception as e:
            return OpenAIResponse(
                content=f"🛡️ Chat error: {e}", model="error", success=False, error=str(e)
            )

    def chat(self, messages: list[dict[str, Any]], **kwargs) -> OpenAIResponse:
        """Smart chat method - detects async context automatically"""
        try:
            # Check if we're in an async context
            asyncio.get_running_loop()
            # We're in an async context but this is sync call
            # Use thread-based approach
            return self.chat_sync(messages, **kwargs)
        except RuntimeError:
            # No running loop - safe to use asyncio.run
            return asyncio.run(self.chat_async(messages, **kwargs))


# Global client instance
_global_client: EQ12OpenAIClient | None = None


def get_openai_client(primary_model: str | None = None) -> EQ12OpenAIClient:
    """Get or create global OpenAI client instance"""
    global _global_client
    if _global_client is None:
        _global_client = EQ12OpenAIClient(primary_model)
    return _global_client


def reset_client():
    """Reset global client (useful for testing or config changes)"""
    global _global_client
    _global_client = None


# Convenience functions for common usage patterns
async def ask_gpt_async(prompt: str, model: str | None = None, **kwargs) -> str:
    """Simple async GPT query"""
    client = get_openai_client(model)
    messages = [{"role": "user", "content": prompt}]
    response = await client.chat_async(messages, **kwargs)
    return response.content


def ask_gpt_sync(prompt: str, model: str | None = None, **kwargs) -> str:
    """Simple sync GPT query"""
    client = get_openai_client(model)
    messages = [{"role": "user", "content": prompt}]
    response = client.chat_sync(messages, **kwargs)
    return response.content


def ask_gpt(prompt: str, model: str | None = None, **kwargs) -> str:
    """Smart GPT query - auto-detects sync/async context"""
    client = get_openai_client(model)
    messages = [{"role": "user", "content": prompt}]
    response = client.chat(messages, **kwargs)
    return response.content
