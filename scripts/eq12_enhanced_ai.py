#!/usr/bin/env python3
"""
EQ12 Enhanced AI Integration with GPT-5 Support
Advanced AI-powered content classification and analysis using latest OpenAI models

Author: EQ12 AI System
Version: 2.0.0 - GPT-5 Enhanced
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

try:
    from openai import AsyncOpenAI, OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not available. Install with: pip install openai>=1.40.0")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AIAnalysisResult:
    """Enhanced AI analysis result with GPT-5 insights"""

    category: str
    confidence: float
    reasoning: str
    key_features: list[str]
    suggested_actions: list[str]
    eq12_relevance: float
    model_used: str
    processing_time: float


class EQ12EnhancedAI:
    """Enhanced AI system with GPT-5 and latest model support"""

    def __init__(self, config_path: str = "C:/EQ12/configs/ai_enhanced_config.json"):
        self.config_path = config_path
        self.config = self._load_config()

        # Initialize OpenAI clients
        self.sync_client = None
        self.async_client = None
        self._init_clients()

        # Model configuration
        self.available_models = self._detect_available_models()
        self.current_model = self._select_best_model()

        logger.info(f"EQ12 Enhanced AI initialized with model: {self.current_model}")

    def _load_config(self) -> dict[str, Any]:
        """Load AI configuration from JSON file"""
        try:
            with open(self.config_path) as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            return self._default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return self._default_config()

    def _default_config(self) -> dict[str, Any]:
        """Default configuration if file not found"""
        return {
            "ai_configuration": {
                "openai_settings": {
                    "preferred_model": "gpt-5",
                    "fallback_models": [
                        "o1-preview",
                        "gpt-4-turbo-preview",
                        "gpt-4",
                        "gpt-3.5-turbo",
                    ],
                }
            }
        }

    def _init_clients(self):
        """Initialize OpenAI clients with API key"""
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI library not available")
            return

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set, AI features will be limited")
            return

        try:
            self.sync_client = OpenAI(api_key=api_key, max_retries=0, timeout=30.0)
            self.async_client = AsyncOpenAI(api_key=api_key)
            logger.info("OpenAI clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI clients: {e}")

    def _detect_available_models(self) -> list[str]:
        """Detect which models are available for the current API key"""
        if not self.sync_client:
            return []

        try:
            models = self.sync_client.models.list()
            available = [model.id for model in models.data]

            # Filter for GPT models we care about
            gpt_models = [
                model
                for model in available
                if any(gpt in model for gpt in ["gpt-5", "gpt-4", "gpt-3.5", "o1"])
            ]

            logger.info(f"Available GPT models: {gpt_models}")
            return gpt_models

        except Exception as e:
            logger.warning(f"Could not detect available models: {e}")
            return ["gpt-3.5-turbo"]  # Safe fallback

    def _select_best_model(self) -> str:
        """Select the best available model based on preference and availability"""
        # Check environment override
        env_model = os.getenv("EQ12_OPENAI_MODEL")
        if env_model and env_model in self.available_models:
            return env_model

        # Use preference order from config
        preferred_models = (
            self.config.get("ai_configuration", {})
            .get("openai_settings", {})
            .get("fallback_models", [])
        )
        preferred_model = (
            self.config.get("ai_configuration", {})
            .get("openai_settings", {})
            .get("preferred_model", "gpt-5")
        )

        # Check preferred model first
        if preferred_model in self.available_models:
            return preferred_model

        # Try fallback models
        for model in preferred_models:
            if model in self.available_models:
                return model

        # Final fallback
        return "gpt-3.5-turbo"

    async def enhanced_classify_content(
        self, content: str, url: str = "", context: str = ""
    ) -> AIAnalysisResult:
        """
        Enhanced content classification using GPT-5 with reasoning and insights
        """
        if not self.async_client:
            raise ValueError("OpenAI client not available")

        start_time = datetime.now()

        # Build enhanced prompt for GPT-5
        system_prompt = """You are an expert AI analyst for the EQ12 automation system.

Your task is to analyze web content and provide detailed classification with reasoning.

EQ12 Categories:
- betting: Sports betting, odds APIs, parlay systems, gambling automation
- automation: Web scraping, browser bots, API integration, workflow automation
- finance: Trading platforms, crypto, portfolio management, financial APIs
- ai: Machine learning, AI models, GPT systems, NLP tools, training data
- dashboard: Analytics dashboards, monitoring, visualization, reporting
- config: Configuration management, environment setup, API keys, settings
- data: Data processing, databases, ETL, analysis tools, storage

Respond with JSON containing:
{
  "category": "most_appropriate_category",
  "confidence": 0.0-1.0,
  "reasoning": "detailed explanation of classification",
  "key_features": ["feature1", "feature2", "feature3"],
  "suggested_actions": ["action1", "action2"],
  "eq12_relevance": 0.0-1.0
}"""

        user_prompt = """
        Analyze this content for the EQ12 system:

        URL: {url}
        Context: {context}

        Content:
        {content[:3000]}  # Increased limit for GPT-5

        Provide detailed analysis with reasoning and actionable insights.
        """

        try:
            # Use the selected model with optimal parameters
            model_params = self._get_model_parameters(self.current_model)

            response = await self.async_client.chat.completions.create(
                model=self.current_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                **model_params,
            )

            # Parse JSON response
            result_text = response.choices[0].message.content.strip()

            # Handle potential JSON parsing issues
            try:
                result_data = json.loads(result_text)
            except json.JSONDecodeError:
                # Fallback parsing for non-JSON responses
                result_data = self._parse_fallback_response(result_text)

            processing_time = (datetime.now() - start_time).total_seconds()

            return AIAnalysisResult(
                category=result_data.get("category", "data"),
                confidence=result_data.get("confidence", 0.5),
                reasoning=result_data.get("reasoning", "Analysis completed"),
                key_features=result_data.get("key_features", []),
                suggested_actions=result_data.get("suggested_actions", []),
                eq12_relevance=result_data.get("eq12_relevance", 0.5),
                model_used=self.current_model,
                processing_time=processing_time,
            )

        except Exception as e:
            logger.error(f"GPT-5 analysis failed: {e}")
            # Fallback to simple classification
            return await self._fallback_classification(content, url, context)

    def _get_model_parameters(self, model: str) -> dict[str, Any]:
        """Get optimal parameters for the specified model"""
        model_params = (
            self.config.get("ai_configuration", {})
            .get("openai_settings", {})
            .get("model_parameters", {})
        )

        if model in model_params:
            return model_params[model]

        # Default parameters for unknown models
        return {"temperature": 0.2, "max_tokens": 300, "top_p": 0.9}

    def _parse_fallback_response(self, response_text: str) -> dict[str, Any]:
        """Parse non-JSON responses as fallback"""
        lines = response_text.split("\n")

        # Simple parsing for category and confidence
        category = "data"
        confidence = 0.5

        for line in lines:
            if "category" in line.lower():
                # Extract category from line
                for cat in [
                    "betting",
                    "automation",
                    "finance",
                    "ai",
                    "dashboard",
                    "config",
                    "data",
                ]:
                    if cat in line.lower():
                        category = cat
                        break

            if "confidence" in line.lower():
                # Extract confidence number
                import re

                numbers = re.findall(r"0\.\d+|\d+\.\d+", line)
                if numbers:
                    try:
                        confidence = float(numbers[0])
                        if confidence > 1.0:
                            confidence = confidence / 100.0  # Convert percentage
                    except ValueError:
                        pass

        return {
            "category": category,
            "confidence": confidence,
            "reasoning": "Fallback parsing applied",
            "key_features": [],
            "suggested_actions": [],
            "eq12_relevance": 0.5,
        }

    async def _fallback_classification(
        self, content: str, url: str, context: str
    ) -> AIAnalysisResult:
        """Fallback classification using simple keyword matching"""
        categories = {
            "betting": ["bet", "odds", "sportsbook", "parlay", "gambling", "wager"],
            "automation": ["automation", "script", "bot", "scraper", "api", "workflow"],
            "finance": [
                "stock",
                "crypto",
                "trading",
                "investment",
                "portfolio",
                "market",
            ],
            "ai": ["ai", "machine learning", "gpt", "model", "neural", "nlp"],
            "dashboard": [
                "dashboard",
                "analytics",
                "monitoring",
                "visualization",
                "chart",
            ],
            "config": ["config", "settings", "environment", "api key", "setup"],
            "data": ["data", "database", "analysis", "export", "import", "storage"],
        }

        content_lower = content.lower()
        scores = {}

        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            scores[category] = score

        best_category = max(scores, key=scores.get) if scores else "data"
        confidence = min(0.8, scores[best_category] *
                         0.2) if scores[best_category] > 0 else 0.3

        return AIAnalysisResult(
            category=best_category,
            confidence=confidence,
            reasoning="Fallback keyword-based classification",
            key_features=[],
            suggested_actions=[],
            eq12_relevance=0.5,
            model_used="fallback",
            processing_time=0.1,
        )

    def test_gpt5_connection(self) -> dict[str, Any]:
        """Test connection to GPT-5 and other models"""
        results = {
            "openai_available": OPENAI_AVAILABLE,
            "client_initialized": bool(self.sync_client),
            "api_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "available_models": self.available_models,
            "selected_model": self.current_model,
            "gpt5_available": "gpt-5" in self.available_models,
            "o1_available": any("o1" in model for model in self.available_models),
            "config_loaded": bool(self.config),
        }

        # Test simple API call if possible
        if self.sync_client:
            try:
                test_response = self.sync_client.chat.completions.create(
                    model=self.current_model,
                    messages=[
                        {
                            "role": "user",
                            "content": "Test connection - respond with 'OK'",
                        }
                    ],
                    max_tokens=5,
                    temperature=0,
                )
                results["api_test"] = "success"
                results["test_response"] = test_response.choices[0].message.content
            except Exception as e:
                results["api_test"] = f"failed: {e}"

        return results


async def main():
    """Test the enhanced AI system"""
    print("🧠 EQ12 Enhanced AI System - GPT-5 Integration Test")
    print("=" * 60)

    ai_system = EQ12EnhancedAI()

    # Test connection
    connection_test = ai_system.test_gpt5_connection()
    print("\n📊 Connection Test Results:")
    for key, value in connection_test.items():
        print(f"  {key}: {value}")

    if not connection_test.get("client_initialized"):
        print("\n❌ OpenAI client not initialized. Check your API key.")
        return

    # Test content classification
    test_content = """
    FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+.
    It's built on standard Python type hints and provides automatic API documentation.
    Great for building automation tools and integrating with machine learning models.
    """

    print("\n🔍 Testing GPT-5 Enhanced Classification:")
    print(f"Model: {ai_system.current_model}")
    print(f"Content: {test_content[:100]}...")

    try:
        result = await ai_system.enhanced_classify_content(
            content=test_content,
            url="https://fastapi.tiangolo.com",
            context="Testing URL learning system",
        )

        print("\n✅ Classification Results:")
        print(f"  Category: {result.category}")
        print(f"  Confidence: {result.confidence:.2%}")
        print(f"  Model Used: {result.model_used}")
        print(f"  Processing Time: {result.processing_time:.2f}s")
        print(f"  Reasoning: {result.reasoning}")
        print(f"  Key Features: {', '.join(result.key_features)}")
        print(f"  EQ12 Relevance: {result.eq12_relevance:.2%}")

        if result.suggested_actions:
            print("  Suggested Actions:")
            for action in result.suggested_actions:
                print(f"    - {action}")

    except Exception as e:
        print(f"\n❌ Classification failed: {e}")

    print("\n🎉 GPT-5 Enhanced AI System Ready!")
    print("💡 Set EQ12_OPENAI_MODEL environment variable to override model selection")


if __name__ == "__main__":
    asyncio.run(main())
