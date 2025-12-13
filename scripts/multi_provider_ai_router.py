"""
EQ12 Multi-Provider AI Router
The Ultimate Phase 2 Enhancement - Intelligent AI Provider Selection

Routes tasks to optimal AI provider based on:
- Task complexity and type
- Speed requirements
- Cost considerations
- Provider availability and rate limits
- Historical performance data

Supported Providers:
✅ Groq (Ultra-fast, FREE 14,400/day)
✅ Google AI Studio (Gemini, FREE 1M tokens/min)
✅ GitHub Models (GPT-4, Claude, Llama via Pro)
✅ OpenAI (Existing integration)
✅ Fallback chains for reliability
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Import our AI clients
try:
    from groq_ai_client import EQ12GroqClient

    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from google_ai_client import EQ12GoogleAIClient

    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

try:
    from github_models_client import EQ12GitHubModelsClient

    GITHUB_MODELS_AVAILABLE = True
except ImportError:
    GITHUB_MODELS_AVAILABLE = False

try:
    from odds_api_client import EQ12OddsAPIClient
    ODDS_API_AVAILABLE = True
except ImportError:
    ODDS_API_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of analysis tasks for intelligent routing"""

    QUICK_ANALYSIS = "quick_analysis"
    NHL_GAME_ANALYSIS = "nhl_analysis"
    ARBITRAGE_DETECTION = "arbitrage"
    BETTING_RECOMMENDATION = "betting_rec"
    RISK_ASSESSMENT = "risk_assessment"
    PROP_ANALYSIS = "prop_analysis"
    MULTI_GAME_ANALYSIS = "multi_game"
    COMPLEX_REASONING = "complex_reasoning"


class SpeedTier(Enum):
    """Speed requirements for task routing"""

    ULTRA_FAST = "ultra_fast"  # <1s - Real-time decisions
    FAST = "fast"  # 1-3s - Quick analysis
    STANDARD = "standard"  # 3-10s - Normal analysis
    DEEP = "deep"  # 10s+ - Complex reasoning


@dataclass
class ProviderConfig:
    """Configuration for each AI provider"""

    name: str
    client_class: type
    available: bool
    speed_tier: SpeedTier
    cost_tier: str  # "free", "low", "medium", "high"
    strengths: list[str]
    rate_limits: dict[str, int]
    reliability_score: float = 0.95


@dataclass
class TaskResult:
    """Result from AI analysis with metadata"""

    content: str
    provider: str
    model: str
    response_time: float
    confidence: float = 0.8
    cost_estimate: float = 0.0
    tokens_used: int = 0


class EQ12MultiProviderAIRouter:
    """
    Intelligent AI Provider Router for EQ12 System
    Optimizes provider selection based on task requirements and constraints
    """

    def __init__(self):
        # Initialize provider configurations
        self.providers = {
            "groq": ProviderConfig(
                name="Groq",
                client_class=EQ12GroqClient if GROQ_AVAILABLE else None,
                available=GROQ_AVAILABLE and bool(os.getenv("GROQ_API_KEY")),
                speed_tier=SpeedTier.ULTRA_FAST,
                cost_tier="free",
                strengths=["speed", "real_time", "quick_analysis"],
                rate_limits={"daily": 14400, "per_minute": 240},
                reliability_score=0.92,
            ),
            "google_ai": ProviderConfig(
                name="Google AI Studio",
                client_class=EQ12GoogleAIClient if GOOGLE_AI_AVAILABLE else None,
                available=GOOGLE_AI_AVAILABLE and bool(os.getenv("GOOGLE_AI_API_KEY")),
                speed_tier=SpeedTier.FAST,
                cost_tier="free",
                strengths=["reasoning", "multi_modal", "large_context"],
                rate_limits={"tokens_per_minute": 1000000, "requests_per_minute": 1000},
                reliability_score=0.96,
            ),
            "github_models": ProviderConfig(
                name="GitHub Models",
                client_class=(EQ12GitHubModelsClient if GITHUB_MODELS_AVAILABLE else None),
                available=GITHUB_MODELS_AVAILABLE and bool(os.getenv("GITHUB_TOKEN")),
                speed_tier=SpeedTier.STANDARD,
                cost_tier="free",  # With Pro subscription
                strengths=["gpt4", "claude", "llama", "diversity"],
                rate_limits={"per_minute": 100},  # Conservative estimate
                reliability_score=0.94,
            ),
            "openai": ProviderConfig(
                name="OpenAI",
                client_class=None,  # Use existing EQ12 integration
                available=bool(os.getenv("OPENAI_API_KEY")),
                speed_tier=SpeedTier.STANDARD,
                cost_tier="medium",
                strengths=["reasoning", "reliability", "established"],
                rate_limits={"per_minute": 60, "tokens_per_minute": 90000},
                reliability_score=0.98,
            ),
        }

        # Initialize available clients
        self.clients = {}
        self._initialize_clients()

        # Initialize Odds API Client (Data Provider)
        self.odds_client = EQ12OddsAPIClient() if ODDS_API_AVAILABLE else None
        if self.odds_client and self.odds_client.available:
            logger.info("✅ Odds API Client initialized")
        else:
            logger.warning("⚠️ Odds API Client unavailable")

        # Task routing rules
        self.routing_rules = self._build_routing_rules()

        # Performance tracking
        self.performance_history = {}
        self.usage_stats = {
            "total_requests": 0,
            "provider_usage": {},
            "avg_response_times": {},
            "success_rates": {},
            "cost_savings": 0.0,
        }

        logger.info("🚀 EQ12 Multi-Provider AI Router initialized")
        logger.info(f"📊 Available providers: {list(self.get_available_providers())}")

    def _initialize_clients(self):
        """Initialize available AI provider clients"""
        for provider_key, config in self.providers.items():
            if config.available and config.client_class:
                try:
                    self.clients[provider_key] = config.client_class()
                    logger.info(f"✅ {config.name} client initialized")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to initialize {config.name}: {e}")
                    self.providers[provider_key].available = False

    def _build_routing_rules(self) -> dict[TaskType, list[str]]:
        """Build task-to-provider routing rules"""
        return {
            TaskType.QUICK_ANALYSIS: ["groq", "google_ai", "github_models", "openai"],
            TaskType.NHL_GAME_ANALYSIS: [
                "github_models",
                "google_ai",
                "groq",
                "openai",
            ],
            TaskType.ARBITRAGE_DETECTION: [
                "groq",
                "github_models",
                "google_ai",
                "openai",
            ],
            TaskType.BETTING_RECOMMENDATION: [
                "github_models",
                "google_ai",
                "groq",
                "openai",
            ],
            TaskType.RISK_ASSESSMENT: ["github_models", "google_ai", "openai", "groq"],
            TaskType.PROP_ANALYSIS: ["google_ai", "github_models", "groq", "openai"],
            TaskType.MULTI_GAME_ANALYSIS: [
                "google_ai",
                "github_models",
                "openai",
                "groq",
            ],
            TaskType.COMPLEX_REASONING: [
                "github_models",
                "google_ai",
                "openai",
                "groq",
            ],
        }

    def select_optimal_provider(
        self,
        task_type: TaskType,
        speed_requirement: SpeedTier = SpeedTier.FAST,
        prefer_free: bool = True,
    ) -> str | None:
        """
        Select optimal provider based on task requirements
        """
        available_providers = [
            provider
            for provider in self.routing_rules.get(task_type, [])
            if self.providers[provider].available
        ]

        if not available_providers:
            logger.warning("No available providers for task type")
            return None

        # Apply filters and scoring
        scored_providers = []

        for provider in available_providers:
            config = self.providers[provider]
            score = 0.0

            # Speed score (higher is better for faster requirements)
            if speed_requirement == SpeedTier.ULTRA_FAST:
                if config.speed_tier == SpeedTier.ULTRA_FAST:
                    score += 40
                elif config.speed_tier == SpeedTier.FAST:
                    score += 20
            elif speed_requirement == SpeedTier.FAST:
                if config.speed_tier in [SpeedTier.ULTRA_FAST, SpeedTier.FAST]:
                    score += 30
                elif config.speed_tier == SpeedTier.STANDARD:
                    score += 15
            else:
                score += 20  # All providers acceptable for standard/deep

            # Cost preference
            if prefer_free and config.cost_tier == "free":
                score += 25
            elif not prefer_free and config.cost_tier == "medium":
                score += 15

            # Reliability score
            score += config.reliability_score * 20

            # Task-specific strengths
            task_keywords = {
                TaskType.QUICK_ANALYSIS: ["speed", "real_time"],
                TaskType.ARBITRAGE_DETECTION: ["speed", "reasoning"],
                TaskType.COMPLEX_REASONING: ["reasoning", "gpt4", "claude"],
                TaskType.NHL_GAME_ANALYSIS: ["reasoning", "sports_analysis"],
            }

            if task_type in task_keywords:
                for keyword in task_keywords[task_type]:
                    if keyword in config.strengths:
                        score += 10

            scored_providers.append((provider, score))

        # Sort by score and return best option
        scored_providers.sort(key=lambda x: x[1], reverse=True)
        selected = scored_providers[0][0]

        logger.info(f"🎯 Task: {task_type.value} → Provider: {self.providers[selected].name}")
        return selected

    async def analyze(
        self,
        prompt: str,
        task_type: TaskType = TaskType.QUICK_ANALYSIS,
        speed_requirement: SpeedTier = SpeedTier.FAST,
        prefer_free: bool = True,
        fallback: bool = True,
    ) -> TaskResult:
        """
        Main analysis method with intelligent provider selection and fallback
        """
        start_time = time.time()

        # Select optimal provider
        provider = self.select_optimal_provider(task_type, speed_requirement, prefer_free)

        if not provider:
            return TaskResult(
                content="No available providers",
                provider="none",
                model="none",
                response_time=0.0,
                confidence=0.0,
            )

        # Attempt analysis with selected provider
        try:
            result = await self._execute_analysis(provider, prompt, task_type)
            self._update_performance_stats(provider, result.response_time, True)
            return result

        except Exception as e:
            logger.warning(f"❌ {self.providers[provider].name} failed: {e}")
            self._update_performance_stats(provider, time.time() - start_time, False)

            if fallback:
                # Try fallback providers
                fallback_providers = [
                    p
                    for p in self.routing_rules.get(task_type, [])
                    if p != provider and self.providers[p].available
                ]

                for fallback_provider in fallback_providers[:2]:  # Try up to 2 fallbacks
                    try:
                        logger.info(f"🔄 Falling back to {self.providers[fallback_provider].name}")
                        result = await self._execute_analysis(fallback_provider, prompt, task_type)
                        result.content = f"[Fallback: {result.provider}] {result.content}"
                        return result
                    except Exception as fallback_error:
                        logger.warning(f"❌ Fallback {fallback_provider} failed: {fallback_error}")
                        continue

            # All providers failed
            return TaskResult(
                content=f"Analysis failed: All providers unavailable. Last error: {e!s}",
                provider="failed",
                model="none",
                response_time=time.time() - start_time,
                confidence=0.0,
            )

    async def _execute_analysis(
        self, provider: str, prompt: str, task_type: TaskType
    ) -> TaskResult:
        """Execute analysis with specific provider"""
        start_time = time.time()
        client = self.clients[provider]

        # Route to appropriate method based on task type
        if task_type == TaskType.NHL_GAME_ANALYSIS:
            # Fetch real odds if available
            odds_context = ""
            if self.odds_client and self.odds_client.available:
                try:
                    odds = self.odds_client.get_odds("icehockey_nhl")
                    if odds:
                        odds_context = f"\n\nREAL-TIME ODDS DATA:\n{json.dumps(odds[:5], indent=2)}\n\n"
                except Exception as e:
                    logger.warning(f"Failed to fetch odds: {e}")

            game_info = {"away_team": "Team A", "home_team": "Team B"}
            if hasattr(client, "nhl_game_analysis"):
                # Some clients might not accept extra context in this method signature
                # For now, we append it to the prompt if we fall back to quick_analysis
                content = client.nhl_game_analysis(game_info)
            else:
                content = client.quick_analysis(f"NHL Analysis: {prompt}{odds_context}")

        elif task_type == TaskType.ARBITRAGE_DETECTION:
            if hasattr(client, "arbitrage_scanner"):
                sample_odds = [{"game": "Sample", "book": "BookA", "odds": 1.5}]
                content = client.arbitrage_scanner(sample_odds)
            else:
                content = client.quick_analysis(f"Arbitrage Analysis: {prompt}")

        elif task_type == TaskType.BETTING_RECOMMENDATION:
            if hasattr(client, "betting_recommendation"):
                game_data = {"home_team": "Team A", "away_team": "Team B"}
                content = client.betting_recommendation(game_data)
            else:
                content = client.quick_analysis(f"Betting Recommendation: {prompt}")
        else:
            # Default to quick_analysis
            content = client.quick_analysis(prompt)

        response_time = time.time() - start_time

        return TaskResult(
            content=content,
            provider=self.providers[provider].name,
            model=getattr(client, "current_model", "unknown"),
            response_time=response_time,
            confidence=0.85,  # Base confidence, could be improved with actual confidence scoring
            tokens_used=len(content.split()) * 1.3,  # Rough estimate
        )

    def multi_provider_consensus(
        self,
        prompt: str,
        task_type: TaskType = TaskType.QUICK_ANALYSIS,
        num_providers: int = 3,
    ) -> dict[str, TaskResult]:
        """
        Get consensus analysis from multiple providers
        Perfect for high-stakes betting decisions
        """
        available_providers = [
            p
            for p in self.routing_rules.get(task_type, [])[:num_providers]
            if self.providers[p].available
        ]

        results = {}
        for provider in available_providers:
            try:
                result = asyncio.run(self._execute_analysis(provider, prompt, task_type))
                results[provider] = result
                time.sleep(0.5)  # Rate limiting courtesy
            except Exception as e:
                logger.warning(f"Consensus provider {provider} failed: {e}")

        return results

    def _update_performance_stats(self, provider: str, response_time: float, success: bool):
        """Update performance tracking"""
        if provider not in self.performance_history:
            self.performance_history[provider] = {
                "total_requests": 0,
                "successful_requests": 0,
                "total_response_time": 0.0,
                "avg_response_time": 0.0,
                "success_rate": 0.0,
            }

        stats = self.performance_history[provider]
        stats["total_requests"] += 1

        if success:
            stats["successful_requests"] += 1
            stats["total_response_time"] += response_time

        stats["avg_response_time"] = (
            stats["total_response_time"] / stats["successful_requests"]
            if stats["successful_requests"] > 0
            else 0.0
        )
        stats["success_rate"] = stats["successful_requests"] / stats["total_requests"]

        # Update provider reliability score based on recent performance
        recent_success_rate = stats["success_rate"]
        self.providers[provider].reliability_score = (
            self.providers[provider].reliability_score * 0.9 + recent_success_rate * 0.1
        )

    def get_available_providers(self) -> list[str]:
        """Get list of currently available providers"""
        return [name for name, config in self.providers.items() if config.available]

    def get_performance_report(self) -> dict[str, Any]:
        """Get comprehensive performance report"""
        return {
            "available_providers": self.get_available_providers(),
            "performance_history": self.performance_history,
            "usage_stats": self.usage_stats,
            "provider_configs": {
                name: {
                    "speed_tier": config.speed_tier.value,
                    "cost_tier": config.cost_tier,
                    "reliability_score": config.reliability_score,
                    "strengths": config.strengths,
                }
                for name, config in self.providers.items()
                if config.available
            },
        }

    def health_check(self) -> dict[str, bool]:
        """Comprehensive health check of all providers"""
        results = {}

        for provider_name, client in self.clients.items():
            try:
                if hasattr(client, "health_check"):
                    results[provider_name] = client.health_check()
                else:
                    # Basic test
                    test_result = client.quick_analysis("Test")
                    results[provider_name] = len(test_result) > 0
            except Exception as e:
                logger.warning(f"Health check failed for {provider_name}: {e}")
                results[provider_name] = False

        # Check Odds API
        if self.odds_client:
            # Odds API is a data provider, not an inference provider
            # Health check passes if we can connect and have requests remaining
            is_healthy = self.odds_client.available and self.odds_client.get_remaining_requests() > 0
            results["odds_api"] = is_healthy
            if not is_healthy:
                logger.warning("Odds API health check failed (unavailable or no requests)")

        return results


# CLI Interface for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Multi-Provider AI Router")
    parser.add_argument("--analyze", help="Quick analysis prompt")
    parser.add_argument("--task-type", default="quick_analysis", help="Task type for routing")
    parser.add_argument(
        "--speed", default="fast", choices=["ultra_fast", "fast", "standard", "deep"]
    )
    parser.add_argument("--consensus", help="Multi-provider consensus analysis")
    parser.add_argument("--health-check", action="store_true", help="Run health check")
    parser.add_argument("--performance-report", action="store_true", help="Show performance report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    async def main():
        try:
            print("🚀 EQ12 Multi-Provider AI Router Demo")
            print("====================================")

            router = EQ12MultiProviderAIRouter()

            if args.health_check:
                print("\n🔄 Running health check...")
                health = router.health_check()
                for provider, status in health.items():
                    status_icon = "✅" if status else "❌"
                    print(f"  {status_icon} {provider}")

            elif args.performance_report:
                print("\n📊 Performance Report:")
                report = router.get_performance_report()
                print(json.dumps(report, indent=2, default=str))

            elif args.analyze:
                task_type = TaskType(args.task_type)
                speed_req = SpeedTier(args.speed)

                print(f"\n🎯 Analysis (Task: {task_type.value}, Speed: {speed_req.value}):")
                result = await router.analyze(args.analyze, task_type, speed_req)

                print(f"Provider: {result.provider}")
                print(f"Model: {result.model}")
                print(f"Response Time: {result.response_time:.2f}s")
                print(f"Confidence: {result.confidence:.2f}")
                print(f"Result: {result.content[:300]}...")

            elif args.consensus:
                print("\n🎯 Multi-Provider Consensus:")
                task_type = TaskType(args.task_type)
                results = router.multi_provider_consensus(args.consensus, task_type)

                for provider, result in results.items():
                    print(f"\n{provider.upper()}:")
                    print(f"  Time: {result.response_time:.2f}s")
                    print(f"  Result: {result.content[:150]}...")

            else:
                print("\n📋 Available Commands:")
                print("  --analyze 'prompt' --task-type quick_analysis")
                print("  --consensus 'prompt' --task-type nhl_analysis")
                print("  --health-check")
                print("  --performance-report")

        except Exception as e:
            print(f"❌ Error: {e}")

    # Run async main
    asyncio.run(main())
