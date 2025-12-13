#!/usr/bin/env python3
"""
EQ12 GODSTACK - LLM Router with Intelligent Fallback
Provider routing with model downshift, cost optimization, and quality guarantees

Core Features:
- Multi-provider routing (OpenAI, Anthropic, Azure, Local models)
- Intelligent model downshifting based on task complexity
- Cost-aware routing with budget optimization
- Quality-based fallback chains with performance tracking
- Request classification for optimal model selection
- Comprehensive retry logic with exponential backoff
- Provider health monitoring and automatic failover
"""

import asyncio
import logging
import os
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

import openai
from anthropic import AsyncAnthropic

# Import our rate guard
from eq12_rate_guard import Priority, Provider, RateGuard, RequestContext

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/llm_router.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Task complexity levels for model selection"""

    SIMPLE = "simple"  # Classification, simple QA
    MEDIUM = "medium"  # Analysis, research synthesis
    COMPLEX = "complex"  # Complex reasoning, code generation
    EXPERT = "expert"  # Advanced analysis, critical decisions


class ResponseQuality(Enum):
    """Response quality levels"""

    EXCELLENT = "excellent"  # 9-10/10
    GOOD = "good"  # 7-8/10
    ACCEPTABLE = "acceptable"  # 5-6/10
    POOR = "poor"  # 1-4/10


@dataclass
class ModelCapability:
    """Model capability and performance profile"""

    model_name: str
    provider: Provider

    # Capability scores (0-1)
    reasoning_score: float
    creativity_score: float
    accuracy_score: float
    speed_score: float
    cost_efficiency_score: float

    # Task suitability
    suitable_complexities: list[TaskComplexity]
    preferred_tasks: list[str]  # "analysis", "generation", "classification", etc.

    # Performance metrics
    average_quality: float  # Historical quality score
    reliability: float  # Uptime/success rate
    avg_latency_ms: int

    # Cost metrics
    cost_per_quality_point: float  # Cost normalized by quality


@dataclass
class RoutingRequest:
    """Request for LLM routing"""

    request_id: str

    # Request content
    messages: list[dict[str, str]]
    system_prompt: str | None = None

    # Routing preferences
    preferred_provider: Provider | None = None
    preferred_model: str | None = None
    task_type: str = "general"
    complexity: TaskComplexity = TaskComplexity.MEDIUM

    # Quality requirements
    min_quality: ResponseQuality = ResponseQuality.ACCEPTABLE
    creativity_required: bool = False
    accuracy_critical: bool = False

    # Constraints
    max_cost_usd: float | None = None
    max_latency_ms: int | None = None
    timeout_seconds: int = 30

    # Retry policy
    max_retries: int = 3
    allow_downshift: bool = True

    # Context
    priority: Priority = Priority.NORMAL
    source_component: str = "unknown"


@dataclass
class RoutingResult:
    """Result from LLM routing"""

    request_id: str

    # Routing decision
    selected_model: str
    selected_provider: Provider
    routing_reason: str

    # Response
    response_content: str
    response_metadata: dict[str, Any]

    # Performance metrics
    latency_ms: int
    input_tokens: int
    output_tokens: int
    total_cost: float

    # Quality assessment
    estimated_quality: ResponseQuality
    quality_confidence: float

    # Routing history
    attempts: list[dict[str, Any]]
    fallback_used: bool
    downshift_applied: bool


class QualityAssessor:
    """Assess response quality"""

    def __init__(self):
        self.quality_patterns = self._load_quality_patterns()

    def _load_quality_patterns(self) -> dict[str, Any]:
        """Load quality assessment patterns"""

        return {
            "excellent_indicators": [
                r"comprehensive analysis",
                r"multiple perspectives",
                r"specific examples",
                r"quantified data",
                r"actionable insights",
            ],
            "poor_indicators": [
                r"I don't know",
                r"cannot provide",
                r"insufficient information",
                r"generic response",
                r"repetitive content",
            ],
            "accuracy_checks": [
                r"\d+\.\d+%",  # Percentages
                r"\$\d+",  # Dollar amounts
                r"\d{4}-\d{2}-\d{2}",  # Dates
            ],
        }

    def assess_quality(
        self, response: str, task_type: str, accuracy_critical: bool = False
    ) -> tuple[ResponseQuality, float]:
        """Assess response quality and return confidence"""

        # Simple heuristic-based quality assessment
        score = 5.0  # Start at middle
        confidence = 0.7

        # Length check
        if len(response) < 50:
            score -= 2.0
        elif len(response) > 500:
            score += 1.0

        # Content quality indicators
        excellent_matches = sum(
            1
            for pattern in self.quality_patterns["excellent_indicators"]
            if pattern.lower() in response.lower()
        )
        score += excellent_matches * 1.5

        poor_matches = sum(
            1
            for pattern in self.quality_patterns["poor_indicators"]
            if pattern.lower() in response.lower()
        )
        score -= poor_matches * 2.0

        # Accuracy checks for critical tasks
        if accuracy_critical:
            accuracy_elements = sum(
                1 for pattern in self.quality_patterns["accuracy_checks"] if pattern in response
            )
            if accuracy_elements > 0:
                score += 1.0
                confidence += 0.1
            else:
                confidence -= 0.1

        # Task-specific adjustments
        if (task_type == "analysis" and "analysis" in response.lower()) or (
            task_type == "research"
            and any(word in response.lower() for word in ["source", "study", "data"])
        ):
            score += 0.5

        # Convert to quality enum
        score = max(1, min(10, score))

        if score >= 8.5:
            quality = ResponseQuality.EXCELLENT
        elif score >= 6.5:
            quality = ResponseQuality.GOOD
        elif score >= 4.5:
            quality = ResponseQuality.ACCEPTABLE
        else:
            quality = ResponseQuality.POOR

        confidence = max(0.1, min(1.0, confidence))

        return quality, confidence


class ModelRegistry:
    """Registry of available models and their capabilities"""

    def __init__(self):
        self.models = self._initialize_models()
        self.performance_history = defaultdict(list)

    def _initialize_models(self) -> dict[str, ModelCapability]:
        """Initialize model registry"""

        models = {
            "gpt-4o": ModelCapability(
                model_name="gpt-4o",
                provider=Provider.OPENAI,
                reasoning_score=0.95,
                creativity_score=0.90,
                accuracy_score=0.93,
                speed_score=0.75,
                cost_efficiency_score=0.60,
                suitable_complexities=[TaskComplexity.COMPLEX, TaskComplexity.EXPERT],
                preferred_tasks=["analysis", "reasoning", "research", "generation"],
                average_quality=0.88,
                reliability=0.99,
                avg_latency_ms=2000,
                cost_per_quality_point=0.028,
            ),
            "gpt-4o-mini": ModelCapability(
                model_name="gpt-4o-mini",
                provider=Provider.OPENAI,
                reasoning_score=0.85,
                creativity_score=0.80,
                accuracy_score=0.88,
                speed_score=0.90,
                cost_efficiency_score=0.95,
                suitable_complexities=[TaskComplexity.SIMPLE, TaskComplexity.MEDIUM],
                preferred_tasks=["classification", "simple_analysis", "qa"],
                average_quality=0.78,
                reliability=0.98,
                avg_latency_ms=1500,
                cost_per_quality_point=0.004,
            ),
            "gpt-3.5-turbo": ModelCapability(
                model_name="gpt-3.5-turbo",
                provider=Provider.OPENAI,
                reasoning_score=0.70,
                creativity_score=0.75,
                accuracy_score=0.80,
                speed_score=0.95,
                cost_efficiency_score=0.98,
                suitable_complexities=[TaskComplexity.SIMPLE],
                preferred_tasks=["classification", "simple_qa", "formatting"],
                average_quality=0.68,
                reliability=0.97,
                avg_latency_ms=1000,
                cost_per_quality_point=0.002,
            ),
            "claude-3-5-sonnet-20241022": ModelCapability(
                model_name="claude-3-5-sonnet-20241022",
                provider=Provider.ANTHROPIC,
                reasoning_score=0.92,
                creativity_score=0.88,
                accuracy_score=0.90,
                speed_score=0.70,
                cost_efficiency_score=0.55,
                suitable_complexities=[TaskComplexity.COMPLEX, TaskComplexity.EXPERT],
                preferred_tasks=["analysis", "reasoning", "research", "writing"],
                average_quality=0.85,
                reliability=0.96,
                avg_latency_ms=2500,
                cost_per_quality_point=0.035,
            ),
            "claude-3-haiku-20240307": ModelCapability(
                model_name="claude-3-haiku-20240307",
                provider=Provider.ANTHROPIC,
                reasoning_score=0.78,
                creativity_score=0.70,
                accuracy_score=0.82,
                speed_score=0.85,
                cost_efficiency_score=0.90,
                suitable_complexities=[TaskComplexity.SIMPLE, TaskComplexity.MEDIUM],
                preferred_tasks=["classification", "simple_analysis", "summarization"],
                average_quality=0.72,
                reliability=0.95,
                avg_latency_ms=1800,
                cost_per_quality_point=0.008,
            ),
        }

        return models

    def get_suitable_models(
        self,
        complexity: TaskComplexity,
        task_type: str,
        quality_requirement: ResponseQuality,
    ) -> list[str]:
        """Get models suitable for the task"""

        suitable = []
        min_quality_score = {
            ResponseQuality.EXCELLENT: 0.85,
            ResponseQuality.GOOD: 0.75,
            ResponseQuality.ACCEPTABLE: 0.65,
            ResponseQuality.POOR: 0.0,
        }[quality_requirement]

        for model_name, capability in self.models.items():
            if (
                complexity in capability.suitable_complexities
                and capability.average_quality >= min_quality_score
                and (
                    not task_type
                    or task_type in capability.preferred_tasks
                    or "general" in capability.preferred_tasks
                    or len(capability.preferred_tasks) == 0
                )
            ):
                suitable.append(model_name)

        # Sort by suitability score
        def suitability_score(model_name: str) -> float:
            cap = self.models[model_name]
            complexity_match = 1.0 if complexity in cap.suitable_complexities else 0.5
            task_match = 1.0 if task_type in cap.preferred_tasks else 0.8
            quality_bonus = cap.average_quality

            return complexity_match * task_match * quality_bonus

        suitable.sort(key=suitability_score, reverse=True)

        return suitable

    def update_performance(
        self, model_name: str, quality: ResponseQuality, latency_ms: int, success: bool
    ):
        """Update model performance metrics"""

        if model_name in self.models:
            # Store performance data
            quality_score = {
                ResponseQuality.EXCELLENT: 1.0,
                ResponseQuality.GOOD: 0.8,
                ResponseQuality.ACCEPTABLE: 0.6,
                ResponseQuality.POOR: 0.2,
            }[quality]

            self.performance_history[model_name].append(
                {
                    "timestamp": datetime.now(UTC),
                    "quality": quality_score,
                    "latency_ms": latency_ms,
                    "success": success,
                }
            )

            # Keep only recent history
            cutoff = datetime.now(UTC) - timedelta(days=7)
            self.performance_history[model_name] = [
                record
                for record in self.performance_history[model_name]
                if record["timestamp"] > cutoff
            ]

            # Update model capability metrics
            recent_data = self.performance_history[model_name]
            if recent_data:
                avg_quality = sum(r["quality"] for r in recent_data) / len(recent_data)
                reliability = sum(1 for r in recent_data if r["success"]) / len(recent_data)
                avg_latency = sum(r["latency_ms"] for r in recent_data) / len(recent_data)

                capability = self.models[model_name]
                # Exponential moving average
                capability.average_quality = 0.9 * capability.average_quality + 0.1 * avg_quality
                capability.reliability = 0.9 * capability.reliability + 0.1 * reliability
                capability.avg_latency_ms = int(0.9 * capability.avg_latency_ms + 0.1 * avg_latency)


class ProviderClient:
    """Provider-specific client implementations"""

    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize provider clients"""

        # OpenAI client
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = openai.AsyncOpenAI(api_key=openai_key)

        # Anthropic client
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.anthropic_client = AsyncAnthropic(api_key=anthropic_key)

    async def call_openai(
        self, model: str, messages: list[dict[str, str]], **kwargs
    ) -> tuple[str, dict[str, Any]]:
        """Call OpenAI API"""

        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")

        start_time = time.time()

        response = await self.openai_client.chat.completions.create(
            model=model, messages=messages, **kwargs
        )

        latency_ms = int((time.time() - start_time) * 1000)

        content = response.choices[0].message.content
        metadata = {
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "latency_ms": latency_ms,
            "finish_reason": response.choices[0].finish_reason,
        }

        return content, metadata

    async def call_anthropic(
        self,
        model: str,
        messages: list[dict[str, str]],
        system: str | None = None,
        **kwargs,
    ) -> tuple[str, dict[str, Any]]:
        """Call Anthropic API"""

        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized")

        start_time = time.time()

        # Convert messages format for Anthropic
        anthropic_messages = []
        for msg in messages:
            if msg["role"] != "system":  # System handled separately
                anthropic_messages.append(msg)

        response = await self.anthropic_client.messages.create(
            model=model,
            messages=anthropic_messages,
            system=system,
            max_tokens=kwargs.get("max_tokens", 4000),
        )

        latency_ms = int((time.time() - start_time) * 1000)

        content = response.content[0].text
        metadata = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            "latency_ms": latency_ms,
            "finish_reason": response.stop_reason,
        }

        return content, metadata


class LLMRouter:
    """Main LLM routing engine"""

    def __init__(self, rate_guard: RateGuard | None = None):
        self.rate_guard = rate_guard or RateGuard()
        self.model_registry = ModelRegistry()
        self.quality_assessor = QualityAssessor()
        self.provider_client = ProviderClient()

        self.routing_history = []
        self.fallback_chains = self._build_fallback_chains()

        logger.info("LLMRouter initialized with intelligent routing and fallback")

    def _build_fallback_chains(self) -> dict[TaskComplexity, list[str]]:
        """Build fallback chains for each complexity level"""

        chains = {
            TaskComplexity.SIMPLE: [
                "gpt-4o-mini",
                "gpt-3.5-turbo",
                "claude-3-haiku-20240307",
            ],
            TaskComplexity.MEDIUM: [
                "gpt-4o-mini",
                "gpt-4o",
                "claude-3-haiku-20240307",
                "gpt-3.5-turbo",
            ],
            TaskComplexity.COMPLEX: [
                "gpt-4o",
                "claude-3-5-sonnet-20241022",
                "gpt-4o-mini",
            ],
            TaskComplexity.EXPERT: ["gpt-4o", "claude-3-5-sonnet-20241022"],
        }

        return chains

    async def route_request(self, request: RoutingRequest) -> RoutingResult:
        """Route request to optimal model with fallback"""

        logger.info(
            f"Routing request {request.request_id} - {request.task_type} ({request.complexity.value})"
        )

        attempts = []
        start_time = time.time()

        # Get candidate models
        candidates = self._select_candidates(request)

        if not candidates:
            raise ValueError("No suitable models available for request")

        # Try each candidate
        for attempt_num, model_name in enumerate(candidates):
            try:
                result = await self._attempt_request(request, model_name, attempt_num)

                # Record successful routing
                total_latency = int((time.time() - start_time) * 1000)

                return RoutingResult(
                    request_id=request.request_id,
                    selected_model=model_name,
                    selected_provider=self.model_registry.models[model_name].provider,
                    routing_reason=f"Selected {model_name} (attempt {attempt_num + 1})",
                    response_content=result["content"],
                    response_metadata=result["metadata"],
                    latency_ms=total_latency,
                    input_tokens=result["metadata"]["input_tokens"],
                    output_tokens=result["metadata"]["output_tokens"],
                    total_cost=result["cost"],
                    estimated_quality=result["quality"],
                    quality_confidence=result["quality_confidence"],
                    attempts=[*attempts, result["attempt"]],
                    fallback_used=attempt_num > 0,
                    downshift_applied=self._is_downshift(candidates[0], model_name),
                )

            except Exception as e:
                attempt = {
                    "model": model_name,
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                attempts.append(attempt)

                logger.warning(f"Attempt {attempt_num + 1} failed for {model_name}: {e}")

                # Update model registry with failure
                self.model_registry.update_performance(model_name, ResponseQuality.POOR, 0, False)

                # Continue to next candidate
                continue

        # All attempts failed
        raise Exception(f"All routing attempts failed for request {request.request_id}")

    def _select_candidates(self, request: RoutingRequest) -> list[str]:
        """Select candidate models in priority order"""

        candidates = []

        # Start with preferred model if specified
        if request.preferred_model and request.preferred_model in self.model_registry.models:
            candidates.append(request.preferred_model)

        # Add models suitable for complexity and task
        suitable = self.model_registry.get_suitable_models(
            request.complexity, request.task_type, request.min_quality
        )

        for model in suitable:
            if model not in candidates:
                candidates.append(model)

        # Add fallback chain if downshift allowed
        if request.allow_downshift:
            fallback_chain = self.fallback_chains.get(request.complexity, [])
            for model in fallback_chain:
                if model not in candidates and model in self.model_registry.models:
                    candidates.append(model)

        # Filter by cost constraints
        if request.max_cost_usd:
            candidates = [
                model
                for model in candidates
                if self._estimate_cost(model, request) <= request.max_cost_usd
            ]

        # Filter by latency constraints
        if request.max_latency_ms:
            candidates = [
                model
                for model in candidates
                if self.model_registry.models[model].avg_latency_ms <= request.max_latency_ms
            ]

        # Sort by routing score
        candidates.sort(key=lambda m: self._calculate_routing_score(m, request), reverse=True)

        return candidates[:5]  # Limit to top 5 candidates

    def _calculate_routing_score(self, model_name: str, request: RoutingRequest) -> float:
        """Calculate routing score for model selection"""

        capability = self.model_registry.models[model_name]

        # Base score from capability metrics
        base_score = (
            capability.reasoning_score * 0.3
            + capability.accuracy_score * 0.3
            + capability.reliability * 0.2
            + capability.average_quality * 0.2
        )

        # Task-specific adjustments
        if request.task_type in capability.preferred_tasks:
            base_score += 0.1

        if request.complexity in capability.suitable_complexities:
            base_score += 0.1

        # Cost sensitivity
        if request.max_cost_usd:
            estimated_cost = self._estimate_cost(model_name, request)
            cost_ratio = estimated_cost / request.max_cost_usd
            if cost_ratio > 1:
                base_score -= 0.5  # Penalize over-budget
            else:
                base_score += (1 - cost_ratio) * 0.1  # Bonus for under-budget

        # Speed bonus for urgent requests
        if request.priority == Priority.CRITICAL:
            base_score += capability.speed_score * 0.2

        # Creativity bonus
        if request.creativity_required:
            base_score += capability.creativity_score * 0.1

        return base_score

    async def _attempt_request(
        self, request: RoutingRequest, model_name: str, attempt_num: int
    ) -> dict[str, Any]:
        """Attempt request with specific model"""

        # Check rate limits
        rate_context = RequestContext(
            request_id=request.request_id,
            priority=request.priority,
            estimated_input_tokens=self._estimate_input_tokens(request.messages),
            estimated_output_tokens=1000,  # Default estimate
            model_preference=model_name,
            provider_preference=self.model_registry.models[model_name].provider,
            timeout_seconds=request.timeout_seconds,
            retry_budget=request.max_retries,
            source_component=request.source_component,
            request_type=request.task_type,
        )

        rate_status = await self.rate_guard.check_rate_limit(rate_context)

        if not rate_status.allowed:
            raise Exception(f"Rate limit exceeded: {rate_status.reason}")

        # Reserve request
        tracking_id = await self.rate_guard.reserve_request(rate_context)

        start_time = time.time()

        try:
            # Make API call
            provider = self.model_registry.models[model_name].provider

            if provider == Provider.OPENAI:
                content, metadata = await self.provider_client.call_openai(
                    model=model_name,
                    messages=request.messages,
                    max_tokens=4000,
                    temperature=0.7 if request.creativity_required else 0.3,
                )
            elif provider == Provider.ANTHROPIC:
                # Extract system message
                system = None
                messages = request.messages.copy()
                if messages and messages[0]["role"] == "system":
                    system = messages[0]["content"]
                    messages = messages[1:]

                content, metadata = await self.provider_client.call_anthropic(
                    model=model_name, messages=messages, system=system, max_tokens=4000
                )
            else:
                raise ValueError(f"Provider {provider} not implemented")

            # Assess quality
            quality, quality_confidence = self.quality_assessor.assess_quality(
                content, request.task_type, request.accuracy_critical
            )

            # Check quality requirements
            quality_scores = {
                ResponseQuality.POOR: 1,
                ResponseQuality.ACCEPTABLE: 2,
                ResponseQuality.GOOD: 3,
                ResponseQuality.EXCELLENT: 4,
            }

            if quality_scores[quality] < quality_scores[request.min_quality]:
                raise Exception(
                    f"Quality {quality.value} below required {request.min_quality.value}"
                )

            # Calculate cost
            cost = self._calculate_actual_cost(
                model_name, metadata["input_tokens"], metadata["output_tokens"]
            )

            # Record usage
            await self.rate_guard.record_usage(
                tracking_id,
                model_name,
                metadata["input_tokens"],
                metadata["output_tokens"],
                True,
                metadata["latency_ms"],
            )

            # Update model performance
            self.model_registry.update_performance(
                model_name, quality, metadata["latency_ms"], True
            )

            return {
                "content": content,
                "metadata": metadata,
                "quality": quality,
                "quality_confidence": quality_confidence,
                "cost": cost,
                "attempt": {
                    "model": model_name,
                    "provider": provider.value,
                    "success": True,
                    "latency_ms": metadata["latency_ms"],
                    "tokens": metadata["total_tokens"],
                    "quality": quality.value,
                },
            }

        except Exception as e:
            # Record failure
            latency_ms = int((time.time() - start_time) * 1000)
            await self.rate_guard.record_usage(tracking_id, model_name, 0, 0, False, latency_ms)

            raise e

    def _estimate_input_tokens(self, messages: list[dict[str, str]]) -> int:
        """Estimate input token count"""

        total_chars = sum(len(msg["content"]) for msg in messages)
        # Rough approximation: 1 token ≈ 4 characters
        return total_chars // 4

    def _estimate_cost(self, model_name: str, request: RoutingRequest) -> float:
        """Estimate request cost"""

        self.model_registry.models[model_name]

        # Get cost from rate guard configuration
        if hasattr(self.rate_guard, "models") and model_name in self.rate_guard.models:
            limits = self.rate_guard.models[model_name]
            input_tokens = self._estimate_input_tokens(request.messages)
            output_tokens = 1000  # Estimate

            input_cost = (input_tokens / 1000) * limits.cost_per_1k_input
            output_cost = (output_tokens / 1000) * limits.cost_per_1k_output

            return input_cost + output_cost

        return 0.01  # Fallback estimate

    def _calculate_actual_cost(
        self, model_name: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculate actual cost"""

        if hasattr(self.rate_guard, "models") and model_name in self.rate_guard.models:
            limits = self.rate_guard.models[model_name]

            input_cost = (input_tokens / 1000) * limits.cost_per_1k_input
            output_cost = (output_tokens / 1000) * limits.cost_per_1k_output

            return input_cost + output_cost

        return 0.0

    def _is_downshift(self, preferred_model: str, selected_model: str) -> bool:
        """Check if model selection represents a downshift"""

        if preferred_model == selected_model:
            return False

        preferred_capability = self.model_registry.models.get(preferred_model)
        selected_capability = self.model_registry.models.get(selected_model)

        if not preferred_capability or not selected_capability:
            return False

        return selected_capability.average_quality < preferred_capability.average_quality

    def get_routing_stats(self) -> dict[str, Any]:
        """Get routing statistics"""

        return {
            "total_requests": len(self.routing_history),
            "model_usage": defaultdict(int),
            "fallback_rate": 0.0,
            "downshift_rate": 0.0,
            "average_latency": 0.0,
            "average_cost": 0.0,
            "quality_distribution": defaultdict(int),
            "model_performance": {
                model_name: {
                    "average_quality": capability.average_quality,
                    "reliability": capability.reliability,
                    "avg_latency_ms": capability.avg_latency_ms,
                }
                for model_name, capability in self.model_registry.models.items()
            },
        }


async def main():
    """CLI interface for LLM router testing"""

    import argparse

    parser = argparse.ArgumentParser(description="EQ12 LLM Router")
    parser.add_argument("--test", help="Test message to route")
    parser.add_argument(
        "--complexity",
        choices=["simple", "medium", "complex", "expert"],
        default="medium",
        help="Task complexity",
    )
    parser.add_argument("--task-type", default="general", help="Task type")
    parser.add_argument("--preferred-model", help="Preferred model")
    parser.add_argument("--stats", action="store_true", help="Show routing statistics")

    args = parser.parse_args()

    # Initialize router
    router = LLMRouter()

    if args.stats:
        print("📊 LLM ROUTER STATISTICS")
        print("=" * 50)

        stats = router.get_routing_stats()

        print("Model Performance:")
        for model, perf in stats["model_performance"].items():
            print(f"  {model}:")
            print(f"    Quality: {perf['average_quality']:.2f}")
            print(f"    Reliability: {perf['reliability']:.2%}")
            print(f"    Avg Latency: {perf['avg_latency_ms']}ms")

        return

    if args.test:
        print("🤖 Testing LLM Router")
        print(f"Message: {args.test}")
        print(f"Complexity: {args.complexity}")
        print(f"Task Type: {args.task_type}")

        # Create routing request
        request = RoutingRequest(
            request_id=f"test_{int(time.time())}",
            messages=[{"role": "user", "content": args.test}],
            task_type=args.task_type,
            complexity=TaskComplexity(args.complexity),
            preferred_model=args.preferred_model,
            priority=Priority.NORMAL,
        )

        try:
            result = await router.route_request(request)

            print("\n✅ Routing Result:")
            print(f"   Selected Model: {result.selected_model}")
            print(f"   Provider: {result.selected_provider.value}")
            print(f"   Latency: {result.latency_ms}ms")
            print(f"   Tokens: {result.input_tokens} + {result.output_tokens}")
            print(f"   Cost: ${result.total_cost:.4f}")
            print(f"   Quality: {result.estimated_quality.value}")
            print(f"   Fallback Used: {result.fallback_used}")
            print(f"   Downshift Applied: {result.downshift_applied}")

            print("\n📝 Response:")
            print(result.response_content)

        except Exception as e:
            print(f"❌ Routing failed: {e}")

    else:
        print("🤖 EQ12 LLM Router - Use --help for options")


if __name__ == "__main__":
    asyncio.run(main())
