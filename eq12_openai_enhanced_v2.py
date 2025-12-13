#!/usr/bin/env python3
"""
EQ12 Enhanced OpenAI Integration v2.0
Modern OpenAI API integration with structured outputs, function calling,
advanced prompt engineering, and intelligent model selection.

Features:
- OpenAI API v1.50+ with structured outputs and response schemas
- Advanced prompt templates with role-based instructions
- Dynamic model selection (GPT-4o, GPT-4o-mini, o1-preview, o1-mini)
- Function calling and tool integration
- Token optimization and cost tracking
- Intelligent error handling and retries

Author: EQ12 GODSTACK Team
Version: 2.0.0
License: MIT
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import tiktoken
from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel, Field


class ModelTier(Enum):
    """Model performance and cost tiers"""

    REASONING = "reasoning"  # o1-preview, o1-mini for complex reasoning
    FLAGSHIP = "flagship"  # GPT-4o for high-quality general tasks
    EFFICIENT = "efficient"  # GPT-4o-mini for quick, cost-effective tasks
    LEGACY = "legacy"  # GPT-3.5-turbo for fallback


class TaskComplexity(Enum):
    """Task complexity levels for model selection"""

    SIMPLE = "simple"  # Basic text processing, simple Q&A
    MODERATE = "moderate"  # Analysis, summarization, classification
    COMPLEX = "complex"  # Multi-step reasoning, code generation
    EXPERT = "expert"  # Advanced analysis, research, strategic planning


class MessageRole(Enum):
    """OpenAI message roles"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ModelConfig:
    """Model configuration with capabilities and limits"""

    name: str
    tier: ModelTier
    max_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    supports_functions: bool
    supports_vision: bool
    context_window: int
    reasoning_capability: float  # 0.0 to 1.0


@dataclass
class TokenUsage:
    """Token usage tracking"""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float


@dataclass
class PromptTemplate:
    """Structured prompt template"""

    name: str
    system_message: str
    user_template: str
    variables: list[str]
    complexity: TaskComplexity
    model_preferences: list[str]
    response_schema: dict | None = None
    functions: list[dict] | None = None


class ResponseSchema(BaseModel):
    """Structured response schema for OpenAI outputs"""

    success: bool = Field(description="Whether the operation was successful")
    data: Any = Field(description="The main response data")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")
    reasoning: str | None = Field(description="Step-by-step reasoning process")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BettingAnalysisResponse(BaseModel):
    """Sports betting analysis response schema"""

    recommendation: str = Field(description="BET, PASS, or STRONG_BET")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in recommendation")
    expected_value: float = Field(description="Expected value percentage")
    kelly_fraction: float = Field(ge=0.0, le=1.0, description="Optimal Kelly bet size")
    risk_assessment: str = Field(description="Risk level: LOW, MEDIUM, HIGH")
    reasoning: str = Field(description="Detailed analysis reasoning")
    factors: list[str] = Field(description="Key decision factors")


class EQ12OpenAIEnhanced:
    """Enhanced OpenAI client with modern API features"""

    def __init__(self, api_key: str | None = None, eq12_root: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.sync_client = OpenAI(api_key=self.api_key)

        self.eq12_root = Path(eq12_root or os.getenv("EQ12_ROOT", "C:/EQ12"))
        self.logs_dir = self.eq12_root / "logs"
        self.prompts_dir = self.eq12_root / "prompts"

        # Create directories
        self.logs_dir.mkdir(exist_ok=True)
        self.prompts_dir.mkdir(exist_ok=True)

        self.logger = self._setup_logging()

        # Model configurations
        self.models = self._initialize_models()

        # Token counters for different models
        self.encoders = {}

        # Usage tracking
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.request_count = 0

        # Prompt templates
        self.prompt_templates: dict[str, PromptTemplate] = {}
        self._load_prompt_templates()

    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        log_file = self.logs_dir / f"eq12_openai_enhanced_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        return logging.getLogger(f"{__name__}.EQ12OpenAIEnhanced")

    def _initialize_models(self) -> dict[str, ModelConfig]:
        """Initialize model configurations"""
        return {
            "o1-preview": ModelConfig(
                name="o1-preview",
                tier=ModelTier.REASONING,
                max_tokens=32768,
                cost_per_1k_input=15.0,
                cost_per_1k_output=60.0,
                supports_functions=False,
                supports_vision=False,
                context_window=128000,
                reasoning_capability=1.0,
            ),
            "o1-mini": ModelConfig(
                name="o1-mini",
                tier=ModelTier.REASONING,
                max_tokens=65536,
                cost_per_1k_input=3.0,
                cost_per_1k_output=12.0,
                supports_functions=False,
                supports_vision=False,
                context_window=128000,
                reasoning_capability=0.9,
            ),
            "gpt-4o": ModelConfig(
                name="gpt-4o",
                tier=ModelTier.FLAGSHIP,
                max_tokens=16384,
                cost_per_1k_input=2.5,
                cost_per_1k_output=10.0,
                supports_functions=True,
                supports_vision=True,
                context_window=128000,
                reasoning_capability=0.8,
            ),
            "gpt-4o-mini": ModelConfig(
                name="gpt-4o-mini",
                tier=ModelTier.EFFICIENT,
                max_tokens=16384,
                cost_per_1k_input=0.15,
                cost_per_1k_output=0.6,
                supports_functions=True,
                supports_vision=True,
                context_window=128000,
                reasoning_capability=0.7,
            ),
            "gpt-3.5-turbo": ModelConfig(
                name="gpt-3.5-turbo",
                tier=ModelTier.LEGACY,
                max_tokens=4096,
                cost_per_1k_input=0.5,
                cost_per_1k_output=1.5,
                supports_functions=True,
                supports_vision=False,
                context_window=16385,
                reasoning_capability=0.6,
            ),
        }

    def _load_prompt_templates(self):
        """Load prompt templates from files"""
        # Sports betting analysis template
        self.prompt_templates["sports_betting_analysis"] = PromptTemplate(
            name="sports_betting_analysis",
            system_message="""You are an expert sports betting analyst with deep knowledge of
            statistical modeling, bankroll management, and Expected Value calculations.

            Your role is to:
            1. Analyze betting opportunities using statistical methods
            2. Calculate Expected Value and Kelly Criterion recommendations
            3. Assess risk levels and provide clear recommendations
            4. Explain reasoning in a clear, actionable manner

            Always respond with structured analysis including confidence levels,
            risk assessments, and specific betting recommendations.""",
            user_template="""Analyze this betting opportunity:

            Game: {game_info}
            Bet Type: {bet_type}
            Odds: {odds}
            Your Probability Estimate: {estimated_probability}%
            Bankroll: ${bankroll}

            Additional Context: {context}

            Provide a comprehensive analysis with recommendation.""",
            variables=[
                "game_info",
                "bet_type",
                "odds",
                "estimated_probability",
                "bankroll",
                "context",
            ],
            complexity=TaskComplexity.COMPLEX,
            model_preferences=["gpt-4o", "o1-mini", "gpt-4o-mini"],
            response_schema=BettingAnalysisResponse.model_json_schema(),
        )

        # Code review template
        self.prompt_templates["code_review"] = PromptTemplate(
            name="code_review",
            system_message="""You are a senior software engineer performing code reviews.
            Focus on security, performance, maintainability, and best practices.

            Provide specific, actionable feedback with examples and suggestions.""",
            user_template="""Review this code:

            File: {file_path}
            Language: {language}

            ```{language}
            {code}
            ```

            Context: {context}""",
            variables=["file_path", "language", "code", "context"],
            complexity=TaskComplexity.MODERATE,
            model_preferences=["gpt-4o", "gpt-4o-mini"],
        )

    def select_optimal_model(
        self,
        complexity: TaskComplexity,
        requires_functions: bool = False,
        requires_vision: bool = False,
        max_cost_per_1k: float | None = None,
    ) -> str:
        """Select optimal model based on requirements"""

        # Filter models by requirements
        suitable_models = []

        for name, config in self.models.items():
            if requires_functions and not config.supports_functions:
                continue
            if requires_vision and not config.supports_vision:
                continue
            if max_cost_per_1k and config.cost_per_1k_output > max_cost_per_1k:
                continue

            suitable_models.append((name, config))

        if not suitable_models:
            self.logger.warning("No models meet requirements, using fallback")
            return "gpt-4o-mini"

        # Select based on complexity and performance
        if complexity == TaskComplexity.EXPERT:
            # Use reasoning models for expert tasks
            for name, config in suitable_models:
                if config.tier == ModelTier.REASONING:
                    return name

        elif complexity == TaskComplexity.COMPLEX:
            # Use flagship models for complex tasks
            for name, config in suitable_models:
                if config.tier == ModelTier.FLAGSHIP:
                    return name

        elif complexity == TaskComplexity.SIMPLE:
            # Use efficient models for simple tasks
            for name, config in suitable_models:
                if config.tier == ModelTier.EFFICIENT:
                    return name

        # Default to best available model
        suitable_models.sort(key=lambda x: x[1].reasoning_capability, reverse=True)
        return suitable_models[0][0]

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens for text using appropriate encoder"""
        if model not in self.encoders:
            try:
                self.encoders[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fallback to cl100k_base for newer models
                self.encoders[model] = tiktoken.get_encoding("cl100k_base")

        return len(self.encoders[model].encode(text))

    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate API call cost"""
        config = self.models.get(model)
        if not config:
            return 0.0

        input_cost = (input_tokens / 1000) * config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * config.cost_per_1k_output

        return input_cost + output_cost

    async def create_structured_completion(
        self,
        messages: list[dict[str, str]],
        response_format: type | None = None,
        model: str | None = None,
        temperature: float = 0.1,
        max_tokens: int | None = None,
        functions: list[dict] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Create completion with structured output"""

        # Auto-select model if not specified
        if not model:
            complexity = kwargs.get("complexity", TaskComplexity.MODERATE)
            model = self.select_optimal_model(
                complexity=complexity, requires_functions=functions is not None
            )

        config = self.models[model]

        # Count input tokens
        input_text = "\n".join(msg.get("content", "") for msg in messages)
        input_tokens = self.count_tokens(input_text, model)

        # Prepare request parameters
        request_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens or config.max_tokens,
            **kwargs,
        }

        # Add structured output format if specified
        if response_format and hasattr(response_format, "model_json_schema"):
            request_params["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": response_format.__name__,
                    "schema": response_format.model_json_schema(),
                    "strict": True,
                },
            }

        # Add function calling if specified
        if functions:
            request_params["tools"] = [{"type": "function", "function": func} for func in functions]

        try:
            start_time = time.time()
            response = await self.client.chat.completions.create(**request_params)
            end_time = time.time()

            # Extract response data
            message = response.choices[0].message
            usage = response.usage

            # Calculate costs
            output_tokens = usage.completion_tokens if usage else 0
            cost = self.estimate_cost(input_tokens, output_tokens, model)

            # Update tracking
            self.total_tokens_used += usage.total_tokens if usage else 0
            self.total_cost += cost
            self.request_count += 1

            # Log usage
            self.logger.info(
                f"API call: {model}, {usage.total_tokens if usage else 0} tokens, ${cost:.4f}, {end_time - start_time:.2f}s"
            )

            # Parse structured response if expected
            content = message.content
            if response_format and content:
                try:
                    parsed_data = json.loads(content)
                    content = response_format.model_validate(parsed_data)
                except (json.JSONDecodeError, ValueError) as e:
                    self.logger.warning(f"Failed to parse structured response: {e}")

            return {
                "content": content,
                "model": model,
                "usage": TokenUsage(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=usage.total_tokens if usage else 0,
                    estimated_cost=cost,
                ),
                "response_time": end_time - start_time,
                "tool_calls": getattr(message, "tool_calls", None),
            }

        except Exception as e:
            self.logger.error(f"API call failed with {model}: {e}")
            raise

    async def analyze_sports_bet(
        self,
        game_info: str,
        bet_type: str,
        odds: str,
        estimated_probability: float,
        bankroll: float,
        context: str = "",
    ) -> BettingAnalysisResponse:
        """Analyze sports betting opportunity with structured output"""

        template = self.prompt_templates["sports_betting_analysis"]

        # Format messages
        messages = [
            {"role": "system", "content": template.system_message},
            {
                "role": "user",
                "content": template.user_template.format(
                    game_info=game_info,
                    bet_type=bet_type,
                    odds=odds,
                    estimated_probability=estimated_probability,
                    bankroll=bankroll,
                    context=context,
                ),
            },
        ]

        # Get structured response
        result = await self.create_structured_completion(
            messages=messages,
            response_format=BettingAnalysisResponse,
            complexity=template.complexity,
            model=self.select_optimal_model(template.complexity),
        )

        return result["content"]

    async def review_code(
        self, file_path: str, language: str, code: str, context: str = ""
    ) -> dict[str, Any]:
        """Perform code review with AI analysis"""

        template = self.prompt_templates["code_review"]

        messages = [
            {"role": "system", "content": template.system_message},
            {
                "role": "user",
                "content": template.user_template.format(
                    file_path=file_path, language=language, code=code, context=context
                ),
            },
        ]

        result = await self.create_structured_completion(
            messages=messages,
            response_format=ResponseSchema,
            complexity=template.complexity,
        )

        return result

    def get_usage_stats(self) -> dict[str, Any]:
        """Get usage statistics"""
        return {
            "total_requests": self.request_count,
            "total_tokens": self.total_tokens_used,
            "total_cost": self.total_cost,
            "average_cost_per_request": self.total_cost / max(1, self.request_count),
            "available_models": list(self.models.keys()),
            "prompt_templates": list(self.prompt_templates.keys()),
        }

    async def test_models(self) -> dict[str, Any]:
        """Test all available models with a simple prompt"""
        test_prompt = [{"role": "user", "content": "Explain the Kelly Criterion in one sentence."}]
        results = {}

        for model_name in self.models:
            try:
                result = await self.create_structured_completion(
                    messages=test_prompt, model=model_name, max_tokens=100
                )
                results[model_name] = {
                    "status": "success",
                    "response_time": result["response_time"],
                    "cost": result["usage"].estimated_cost,
                    "content_length": len(result["content"]),
                }
            except Exception as e:
                results[model_name] = {"status": "error", "error": str(e)}

        return results


# Example usage functions
async def main():
    """Example usage of enhanced OpenAI integration"""

    # Initialize client
    client = EQ12OpenAIEnhanced()

    print("🤖 EQ12 Enhanced OpenAI Integration v2.0")
    print("=" * 50)

    # Test model connectivity
    print("\n📊 Testing model connectivity...")
    test_results = await client.test_models()

    for model, result in test_results.items():
        status = "✅" if result["status"] == "success" else "❌"
        print(f"{status} {model}: {result['status']}")

    # Example sports betting analysis
    print("\n🎯 Example: Sports Betting Analysis")
    try:
        analysis = await client.analyze_sports_bet(
            game_info="Chiefs vs Bills, NFL Week 8",
            bet_type="Moneyline",
            odds="-150 (Chiefs)",
            estimated_probability=65.0,
            bankroll=1000.0,
            context="Chiefs coming off bye week, Bills missing key receiver",
        )

        print(f"Recommendation: {analysis.recommendation}")
        print(f"Confidence: {analysis.confidence:.1%}")
        print(f"Expected Value: {analysis.expected_value:.1f}%")
        print(f"Kelly Fraction: {analysis.kelly_fraction:.2%}")
        print(f"Reasoning: {analysis.reasoning}")

    except Exception as e:
        print(f"❌ Betting analysis failed: {e}")

    # Usage statistics
    print("\n📈 Usage Statistics:")
    stats = client.get_usage_stats()
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Total Tokens: {stats['total_tokens']:,}")
    print(f"Total Cost: ${stats['total_cost']:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
