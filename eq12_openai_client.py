# eq12_openai_client.py
"""
EQ12 Unified OpenAI Client with Azure Compatibility and Responses API
Enhanced client with circuit breaker integration, modern API patterns, and Azure OpenAI support
"""

import asyncio
import io
import logging
import os

# UTF-8 safe stdout/stderr (avoid emoji encode crashes)
import sys
from dataclasses import dataclass
from typing import Any

# Load environment variables early
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not available, using system environment only")

from eq12_llm_offline import LLMOffline

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

try:
    from openai import APIStatusError, AsyncOpenAI, OpenAI
except ImportError:
    AsyncOpenAI = OpenAI = APIStatusError = None

# Try Azure OpenAI import
try:
    from azure.ai.openai import AzureOpenAI
except ImportError:
    AzureOpenAI = None

logger = logging.getLogger(__name__)


@dataclass
class OpenAIResponse:
    """Standardized OpenAI response wrapper"""

    content: str
    model: str
    usage: dict[str, Any] | None = None
    finish_reason: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class OpenAIConfig:
    """OpenAI configuration with latest models"""

    api_key: str
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    max_retries: int = 0  # Disabled for circuit breaker
    timeout: float = 30.0


class EQ12OpenAIClient:
    """
    Unified OpenAI client with GPT-4o support and circuit breaker integration
    """

    # Latest OpenAI models (as of 2025)
    MODELS = {
        "gpt-4o": "gpt-4o",  # Latest GPT-4 Omni
        "gpt-4o-mini": "gpt-4o-mini",  # Cost-effective GPT-4 Omni
        "o1-preview": "o1-preview",  # Reasoning model
        "o1-mini": "o1-mini",  # Smaller reasoning model
        "gpt-4-turbo": "gpt-4-turbo",  # Legacy GPT-4 Turbo
        "gpt-4": "gpt-4",  # Legacy GPT-4
        "gpt-3.5-turbo": "gpt-3.5-turbo",  # Legacy fallback
    }

    FALLBACK_CHAIN = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4"]

    def __init__(self, config: OpenAIConfig | None = None):
        """Initialize with configuration"""
        if not config:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable required")
            config = OpenAIConfig(api_key=api_key)

        self.config = config
        self.sync_client = None
        self.async_client = None

        if OpenAI:
            self.sync_client = OpenAI(
                api_key=config.api_key,
                max_retries=config.max_retries,
                timeout=config.timeout,
            )
            self.async_client = AsyncOpenAI(
                api_key=config.api_key,
                max_retries=config.max_retries,
                timeout=config.timeout,
            )
        else:
            logger.warning("OpenAI library not available")

    def is_available(self) -> bool:
        """Check if OpenAI client is available and not offline"""
        return (
            self.sync_client is not None
            and not LLMOffline.is_offline()
            and bool(int(os.getenv("EQ12_USE_LLM", "1")))
        )

    async def chat_completion_async(
        self, messages: list[dict[str, str]], model: str | None = None, **kwargs
    ) -> OpenAIResponse:
        """Async chat completion with circuit breaker"""
        if not self.is_available():
            return OpenAIResponse(
                content="🛡️ OpenAI offline - using local fallback",
                model="offline",
                finish_reason="circuit_breaker",
            )

        model = model or self.config.model

        try:
            response = await self.async_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                top_p=kwargs.get("top_p", self.config.top_p),
                frequency_penalty=kwargs.get("frequency_penalty", self.config.frequency_penalty),
                presence_penalty=kwargs.get("presence_penalty", self.config.presence_penalty),
            )

            return OpenAIResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage=response.usage.dict() if response.usage else None,
                finish_reason=response.choices[0].finish_reason,
            )

        except Exception as e:
            error_str = str(e).lower()

            # Trip circuit breaker on quota exhaustion
            if "insufficient_quota" in error_str or "billing" in error_str:
                LLMOffline.trip(reason="quota_exhausted")
                logger.error(f"OpenAI quota exhausted, circuit breaker tripped: {e}")
                return OpenAIResponse(
                    content="🛡️ OpenAI quota exhausted - circuit breaker activated",
                    model=model,
                    finish_reason="quota_exhausted",
                )

            # Try fallback models for other errors
            if model in self.FALLBACK_CHAIN:
                current_idx = self.FALLBACK_CHAIN.index(model)
                if current_idx < len(self.FALLBACK_CHAIN) - 1:
                    fallback_model = self.FALLBACK_CHAIN[current_idx + 1]
                    logger.warning(f"Retrying with fallback model: {fallback_model}")
                    return await self.chat_completion_async(messages, fallback_model, **kwargs)

            logger.error(f"OpenAI API error: {e}")
            return OpenAIResponse(
                content=f"🛡️ OpenAI API error: {str(e)[:100]}...",
                model=model,
                finish_reason="error",
            )

    def chat_completion_sync(
        self, messages: list[dict[str, str]], model: str | None = None, **kwargs
    ) -> OpenAIResponse:
        """Sync chat completion wrapper"""
        return asyncio.run(self.chat_completion_async(messages, model, **kwargs))

    async def simple_completion(self, prompt: str, **kwargs) -> str:
        """Simple text completion interface"""
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion_async(messages, **kwargs)
        return response.content

    def get_available_models(self) -> list[str]:
        """Get list of available models"""
        if not self.is_available():
            return []

        try:
            models = self.sync_client.models.list()
            return [model.id for model in models.data if model.id in self.MODELS.values()]
        except Exception as e:
            logger.warning(f"Failed to fetch models: {e}")
            return list(self.MODELS.values())

    def validate_model(self, model: str) -> bool:
        """Validate if model is supported"""
        return model in self.MODELS.values()

    def get_best_model_for_task(self, task_type: str = "general") -> str:
        """Get recommended model for task type"""
        model_recommendations = {
            "reasoning": "o1-preview",
            "coding": "gpt-4o",
            "analysis": "gpt-4o",
            "chat": "gpt-4o-mini",
            "cost_effective": "gpt-4o-mini",
            "general": "gpt-4o",
        }
        return model_recommendations.get(task_type, "gpt-4o")


# Global client instance
_global_client = None


def get_openai_client() -> EQ12OpenAIClient:
    """Get global OpenAI client instance"""
    global _global_client
    if _global_client is None:
        _global_client = EQ12OpenAIClient()
    return _global_client


# Convenience functions
async def ask_gpt(prompt: str, model: str = "gpt-4o", **kwargs) -> str:
    """Simple GPT query function"""
    client = get_openai_client()
    return await client.simple_completion(prompt, model=model, **kwargs)


def ask_gpt_sync(prompt: str, model: str = "gpt-4o", **kwargs) -> str:
    """Simple synchronous GPT query"""
    return asyncio.run(ask_gpt(prompt, model, **kwargs))


# Legacy wrapper for ChatGPT integration commands
def query_openai(
    prompt: str,
    model: str = "gpt-4o",
    temperature: float = 0.5,
    max_tokens: int = 1000,
    system_message: str | None = None
) -> str:
    """
    Synchronous OpenAI query wrapper for ChatGPT integration commands
    Compatible with EQ12_CHATGPT_COMMANDS.ps1
    """
    try:
        client = get_openai_client()
        
        # Build messages
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        # Make synchronous call
        response = client.sync_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ OpenAI API Error: {str(e)}"
