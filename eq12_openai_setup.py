#!/usr/bin/env python3
"""
EQ12 OpenAI API Development Environment Setup
===========================================

Professional OpenAI Python SDK setup for EQ12 sports betting automation.
Includes client configuration, error handling, rate limiting, and usage examples.
"""

import asyncio
import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Import OpenAI v1.0+ SDK
try:
    from openai import AsyncOpenAI, OpenAI
    from openai.types.chat import ChatCompletion
    from openai.types.completion_usage import CompletionUsage
except ImportError:
    print("❌ OpenAI SDK not installed. Run: pip install openai>=1.0.0")
    exit(1)

# EQ12 imports
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for OpenAI usage tracking
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/openai_usage.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


class EQ12OpenAIClient:
    """
    Professional OpenAI client for EQ12 sports betting automation.

    Features:
    - Automatic fallback models
    - Usage tracking and logging
    - Rate limit handling
    - Error recovery
    - Async support
    - EQ12-specific configurations
    """

    def __init__(self, api_key: str | None = None):
        """Initialize EQ12 OpenAI client with professional configuration."""

        # API Key configuration
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key or len(self.api_key) < 20:
            raise ValueError(
                "❌ OPENAI_API_KEY not found or invalid. "
                "Please set it in your .env file or pass it to the constructor."
            )

        # Model configuration
        self.primary_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.fallback_models = os.getenv(
            "OPENAI_FALLBACK_MODELS", "gpt-4o-mini,gpt-4-turbo,gpt-4,gpt-3.5-turbo"
        ).split(",")

        # Generation parameters
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.top_p = float(os.getenv("OPENAI_TOP_P", "1.0"))

        # Initialize clients
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)

        # Usage tracking
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost_estimate": 0.0,
            "model_usage": {},
            "session_start": datetime.now(UTC).isoformat(),
        }

        logger.info(f"✅ EQ12 OpenAI Client initialized with model: {self.primary_model}")

    def _estimate_cost(self, model: str, usage: CompletionUsage) -> float:
        """Estimate API call cost based on model and usage."""
        # Approximate costs per 1K tokens (as of Oct 2024)
        cost_per_1k = {
            "gpt-4o": {"input": 0.0025, "output": 0.01},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        }

        if model not in cost_per_1k:
            return 0.0

        input_cost = (usage.prompt_tokens / 1000) * cost_per_1k[model]["input"]
        output_cost = (usage.completion_tokens / 1000) * cost_per_1k[model]["output"]
        return input_cost + output_cost

    def _log_usage(self, model: str, usage: CompletionUsage, cost: float):
        """Log usage statistics for tracking and optimization."""
        self.usage_stats["total_requests"] += 1
        self.usage_stats["total_tokens"] += usage.total_tokens
        self.usage_stats["total_cost_estimate"] += cost

        if model not in self.usage_stats["model_usage"]:
            self.usage_stats["model_usage"][model] = {
                "requests": 0,
                "tokens": 0,
                "cost": 0.0,
            }

        self.usage_stats["model_usage"][model]["requests"] += 1
        self.usage_stats["model_usage"][model]["tokens"] += usage.total_tokens
        self.usage_stats["model_usage"][model]["cost"] += cost

        logger.info(
            f"OpenAI Usage - Model: {model}, Tokens: {usage.total_tokens}, "
            f"Cost: ${cost:.4f}, "
            f"Total Session Cost: ${self.usage_stats['total_cost_estimate']:.4f}"
        )

    def chat_completion(
        self, messages: list[dict[str, str]], model: str | None = None, **kwargs
    ) -> ChatCompletion:
        """
        Execute chat completion with automatic fallback and error handling.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Override default model
            **kwargs: Additional OpenAI parameters

        Returns:
            ChatCompletion response
        """

        models_to_try = [model or self.primary_model, *self.fallback_models]

        for attempt, model_name in enumerate(models_to_try):
            try:
                logger.info(f"🤖 Attempting OpenAI request with model: {model_name}")

                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=kwargs.get("max_tokens", self.max_tokens),
                    temperature=kwargs.get("temperature", self.temperature),
                    top_p=kwargs.get("top_p", self.top_p),
                    **{
                        k: v
                        for k, v in kwargs.items()
                        if k not in ["max_tokens", "temperature", "top_p"]
                    },
                )

                # Log usage and costs
                cost = self._estimate_cost(model_name, response.usage)
                self._log_usage(model_name, response.usage, cost)

                logger.info(f"✅ OpenAI request successful with {model_name}")
                return response

            except Exception as e:
                logger.warning(f"❌ Model {model_name} failed: {e!s}")
                if attempt == len(models_to_try) - 1:
                    logger.error("❌ All models failed!")
                    raise
                continue

    async def async_chat_completion(
        self, messages: list[dict[str, str]], model: str | None = None, **kwargs
    ) -> ChatCompletion:
        """Async version of chat completion."""

        models_to_try = [model or self.primary_model, *self.fallback_models]

        for attempt, model_name in enumerate(models_to_try):
            try:
                logger.info(f"🤖 Async OpenAI request with model: {model_name}")

                response = await self.async_client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=kwargs.get("max_tokens", self.max_tokens),
                    temperature=kwargs.get("temperature", self.temperature),
                    top_p=kwargs.get("top_p", self.top_p),
                    **{
                        k: v
                        for k, v in kwargs.items()
                        if k not in ["max_tokens", "temperature", "top_p"]
                    },
                )

                # Log usage and costs
                cost = self._estimate_cost(model_name, response.usage)
                self._log_usage(model_name, response.usage, cost)

                logger.info(f"✅ Async OpenAI request successful with {model_name}")
                return response

            except Exception as e:
                logger.warning(f"❌ Async model {model_name} failed: {e!s}")
                if attempt == len(models_to_try) - 1:
                    logger.error("❌ All async models failed!")
                    raise
                continue

    def sports_betting_analysis(self, game_data: str, analysis_type: str = "general") -> str:
        """
        EQ12-specific sports betting analysis using OpenAI.

        Args:
            game_data: Game information, odds, statistics
            analysis_type: Type of analysis (general, sgp, value, etc.)

        Returns:
            AI-generated sports betting analysis
        """

        system_prompts = {
            "general": """You are an expert sports betting analyst for EQ12.
                         Analyze the provided game data and give strategic insights
                         focusing on value betting opportunities and risk management.""",
            "sgp": """You are an expert Same Game Parlay (SGP) analyst for EQ12.
                     Identify correlated betting opportunities within the game data
                     and suggest profitable SGP combinations with proper risk assessment.""",
            "value": """You are an expert value betting analyst for EQ12.
                       Calculate expected value, identify mispriced lines, and
                       recommend optimal betting strategies based on the data.""",
            "risk": """You are an expert risk management analyst for EQ12.
                      Assess betting risk, recommend position sizing, and
                      provide risk mitigation strategies for the betting opportunities.""",
        }

        messages = [
            {
                "role": "system",
                "content": system_prompts.get(analysis_type, system_prompts["general"]),
            },
            {
                "role": "user",
                "content": f"Analyze this sports betting data:\n\n{game_data}",
            },
        ]

        try:
            response = self.chat_completion(
                messages=messages,
                temperature=0.3,  # Lower temperature for more focused analysis
                max_tokens=2048,
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"❌ Sports betting analysis failed: {e}")
            return f"Analysis failed: {e!s}"

    def get_usage_report(self) -> dict[str, Any]:
        """Generate comprehensive usage report for monitoring."""
        return {
            **self.usage_stats,
            "session_duration": (
                datetime.now(UTC) - datetime.fromisoformat(self.usage_stats["session_start"])
            ).total_seconds(),
            "avg_tokens_per_request": (
                self.usage_stats["total_tokens"] / max(self.usage_stats["total_requests"], 1)
            ),
        }

    def save_usage_report(self, filepath: str | None = None):
        """Save usage report to file for tracking."""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"C:/EQ12/logs/openai_usage_report_{timestamp}.json"

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(self.get_usage_report(), f, indent=2, default=str)

        logger.info(f"📊 Usage report saved to: {filepath}")


def demo_openai_setup():
    """Demonstrate EQ12 OpenAI setup and capabilities."""

    print("🚀 EQ12 OpenAI SDK Setup Demo")
    print("=" * 40)

    try:
        # Initialize client
        client = EQ12OpenAIClient()
        print("✅ Client initialized successfully")
        print(f"   Primary model: {client.primary_model}")
        print(f"   Fallback models: {', '.join(client.fallback_models)}")
        print()

        # Test basic chat completion
        print("🧪 Testing basic chat completion...")
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant for EQ12 sports betting.",
            },
            {
                "role": "user",
                "content": "Explain expected value in sports betting in 2 sentences.",
            },
        ]

        response = client.chat_completion(messages)
        print(f"✅ Response: {response.choices[0].message.content}")
        print()

        # Test sports betting analysis
        print("🏈 Testing sports betting analysis...")
        game_data = """
        NFL Game: Kansas City Chiefs vs Buffalo Bills
        Spread: KC -3.5 (-110), BUF +3.5 (-110)
        Total: Over 54.5 (-110), Under 54.5 (-110)
        Moneyline: KC -175, BUF +145
        Weather: Clear, 72°F, Wind 5mph
        """

        analysis = client.sports_betting_analysis(game_data, "general")
        print(f"✅ Analysis: {analysis[:200]}...")
        print()

        # Show usage statistics
        print("📊 Usage Statistics:")
        report = client.get_usage_report()
        print(f"   Total requests: {report['total_requests']}")
        print(f"   Total tokens: {report['total_tokens']}")
        print(f"   Estimated cost: ${report['total_cost_estimate']:.4f}")
        print()

        # Save usage report
        client.save_usage_report()
        print("✅ Usage report saved")

        print("🎉 EQ12 OpenAI setup test completed successfully!")

    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

    return True


async def demo_async_openai():
    """Demonstrate async OpenAI capabilities."""

    print("🚀 Testing Async OpenAI...")

    try:
        client = EQ12OpenAIClient()

        messages = [
            {"role": "system", "content": "You are a sports betting expert."},
            {
                "role": "user",
                "content": "What are the key factors in NFL point spread betting?",
            },
        ]

        response = await client.async_chat_completion(messages)
        print(f"✅ Async response: {response.choices[0].message.content[:100]}...")

    except Exception as e:
        print(f"❌ Async test failed: {e}")


if __name__ == "__main__":
    # Run synchronous demo
    print("🔧 EQ12 OpenAI Development Environment Setup")
    print("=" * 50)

    # Check environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment!")
        print("💡 Add it to your C:/EQ12/.env file:")
        print("   OPENAI_API_KEY=sk-your-key-here")
        exit(1)

    if len(api_key) < 20:
        print("❌ OPENAI_API_KEY appears to be invalid (too short)")
        exit(1)

    print(f"✅ OpenAI API key configured (length: {len(api_key)})")

    # Run demos
    success = demo_openai_setup()

    if success:
        # Run async demo
        print("\n" + "=" * 50)
        asyncio.run(demo_async_openai())

        print("\n🎉 EQ12 OpenAI SDK setup complete!")
        print("\n📚 Next steps:")
        print("   1. Import: from eq12_openai_setup import EQ12OpenAIClient")
        print("   2. Use: client = EQ12OpenAIClient()")
        print("   3. Call: client.sports_betting_analysis(game_data)")
        print("   4. Monitor usage with: client.get_usage_report()")
