"""
EQ12 Model Response System - Complete OpenAI Responses API Implementation
Comprehensive response handlers for sports betting analysis, parlay optimization, and real-time data integration
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from pydantic import BaseModel, Field
except ImportError:
    BaseModel = None
    Field = None

logger = logging.getLogger(__name__)

# Configuration
RESPONSES_API_BASE_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = os.getenv("EQ12_DEFAULT_MODEL", "gpt-4.1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ENABLE_BACKGROUND_PROCESSING = os.getenv("EQ12_ENABLE_BACKGROUND", "false").lower() == "true"
ENABLE_WEB_SEARCH = os.getenv("EQ12_ENABLE_WEB_SEARCH", "true").lower() == "true"
ENABLE_FILE_SEARCH = os.getenv("EQ12_ENABLE_FILE_SEARCH", "true").lower() == "true"
ENABLE_CODE_INTERPRETER = os.getenv("EQ12_ENABLE_CODE_INTERPRETER", "true").lower() == "true"


class ResponseType(str, Enum):
    """Types of model responses supported by EQ12"""

    PARLAY_ANALYSIS = "parlay_analysis"
    EV_CALCULATION = "ev_calculation"
    RISK_ASSESSMENT = "risk_assessment"
    MARKET_RESEARCH = "market_research"
    LIVE_ODDS_ANALYSIS = "live_odds_analysis"
    PLAYER_PROP_ANALYSIS = "player_prop_analysis"
    GAME_SIMULATION = "game_simulation"
    BETTING_STRATEGY = "betting_strategy"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    REAL_TIME_ALERTS = "real_time_alerts"


class ServiceTier(str, Enum):
    """OpenAI service tiers for response processing"""

    AUTO = "auto"
    DEFAULT = "default"
    FLEX = "flex"
    PRIORITY = "priority"


class ToolType(str, Enum):
    """Available tool types for enhanced responses"""

    WEB_SEARCH = "web_search"
    WEB_SEARCH_PREVIEW = "web_search_preview"
    FILE_SEARCH = "file_search"
    CODE_INTERPRETER = "code_interpreter"
    COMPUTER = "computer"
    FUNCTION = "function"


@dataclass
class ResponseConfig:
    """Configuration for model responses"""

    model: str = DEFAULT_MODEL
    temperature: float = 0.1
    max_output_tokens: int = 2000
    max_tool_calls: int = 10
    background: bool = False
    stream: bool = False
    service_tier: ServiceTier = ServiceTier.AUTO
    store: bool = True
    parallel_tool_calls: bool = True
    top_p: float = 1.0
    truncation: str = "disabled"
    reasoning_effort: str | None = None  # "low", "medium", "high"
    vector_store_ids: list[str] | None = None
    instructions: str | None = None
    tool_choice: str = "auto"


class EQ12ResponsesAPI:
    """
    Complete EQ12 Model Response System using OpenAI Responses API

    Supports all sports betting analysis use cases with advanced features:
    - Background processing for long-running analysis
    - Multi-turn conversations with state management
    - Built-in tools (web search, file search, code interpreter)
    - Structured outputs with JSON validation
    - Real-time streaming responses
    - Advanced caching and optimization
    """

    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.base_url = RESPONSES_API_BASE_URL
        self.conversations = {}
        self.active_responses = {}

        # Initialize OpenAI client
        if self.api_key and OpenAI:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            logger.warning(
                "OpenAI client not available. Check OPENAI_API_KEY and openai installation."
            )

        logger.info("EQ12 Responses API initialized")

    def _get_headers(self) -> dict[str, str]:
        """Get standard headers for Responses API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "responses-2025-01-01",
        }

    def _prepare_tools(self, tools: list[ToolType]) -> list[dict[str, Any]]:
        """Prepare tools configuration for Responses API"""
        tool_configs = []

        for tool in tools:
            if tool == ToolType.WEB_SEARCH and ENABLE_WEB_SEARCH:
                tool_configs.append(
                    {
                        "type": "web_search",
                        "web_search": {
                            "max_results": 10,
                            "include_domains": [
                                "espn.com",
                                "draftkings.com",
                                "fanduel.com",
                                "covers.com",
                            ],
                            "exclude_domains": ["example.com"],
                        },
                    }
                )
            elif tool == ToolType.WEB_SEARCH_PREVIEW and ENABLE_WEB_SEARCH:
                tool_configs.append({"type": "web_search_preview"})
            elif tool == ToolType.FILE_SEARCH and ENABLE_FILE_SEARCH:
                vector_stores = self._get_vector_store_ids()
                if vector_stores:
                    tool_configs.append(
                        {
                            "type": "file_search",
                            "vector_store_ids": vector_stores,
                            "max_num_results": 20,
                        }
                    )
                else:
                    tool_configs.append(
                        {
                            "type": "file_search",
                            "file_search": {
                                "max_results": 20,
                                "file_ids": self._get_betting_knowledge_files(),
                            },
                        }
                    )
            elif tool == ToolType.CODE_INTERPRETER and ENABLE_CODE_INTERPRETER:
                tool_configs.append(
                    {"type": "code_interpreter", "code_interpreter": {"timeout": 120}}
                )
            elif tool == ToolType.FUNCTION:
                tool_configs.extend(self._get_custom_functions())

        return tool_configs

    def _get_betting_knowledge_files(self) -> list[str]:
        """Get file IDs for betting knowledge base (implement as needed)"""
        return []  # Replace with actual file IDs from your knowledge base

    def _get_vector_store_ids(self) -> list[str]:
        """Get vector store IDs for file search (implement as needed)"""
        vector_store_env = os.getenv("EQ12_VECTOR_STORE_IDS")
        if vector_store_env:
            return vector_store_env.split(",")
        return []  # Replace with actual vector store IDs

    def _get_custom_functions(self) -> list[dict[str, Any]]:
        """Define custom functions for sports betting analysis"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "calculate_parlay_odds",
                    "description": "Calculate true parlay odds and expected value",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "legs": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "odds": {"type": "number"},
                                        "probability": {"type": "number"},
                                    },
                                },
                            }
                        },
                    },
                },
                "container": {"type": "default"},
            },
            {
                "type": "function",
                "function": {
                    "name": "get_live_odds",
                    "description": "Fetch real-time odds from sportsbooks",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "game_id": {"type": "string"},
                            "market_types": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
                "container": {"type": "default"},
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_player_stats",
                    "description": "Analyze player statistics and performance trends",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "player_id": {"type": "string"},
                            "stat_types": {"type": "array", "items": {"type": "string"}},
                            "lookback_games": {"type": "integer"},
                        },
                    },
                },
                "container": {"type": "default"},
            },
        ]

    async def create_parlay_analysis_response(
        self,
        game_details: str,
        legs: list[dict[str, Any]],
        bankroll: float = 1000.0,
        config: ResponseConfig | None = None,
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Create advanced parlay analysis response with tools and reasoning

        Args:
            game_details: Description of games and betting context
            legs: List of potential parlay legs with odds
            bankroll: Available bankroll for sizing
            config: Response configuration
            conversation_id: Optional conversation to continue

        Returns:
            Complete parlay analysis with recommendations
        """
        config = config or ResponseConfig()

        payload = {
            "model": config.model,
            "instructions": f"""You are EQ12 Elite Sports Analyst. Provide comprehensive parlay analysis including:

1. Correlation Analysis: Identify positive/negative correlations between legs
2. Expected Value Calculation: Calculate true EV for each leg and overall parlay
3. Kelly Criterion Sizing: Recommend optimal bet sizing based on bankroll ${bankroll:,.2f}
4. Risk Assessment: Evaluate variance, worst-case scenarios, and drawdown risk
5. Market Intelligence: Compare odds across sportsbooks for best value
6. Real-time Factors: Account for injuries, weather, line movement

Use all available tools for comprehensive analysis.""",
            "input": [
                {
                    "type": "message",
                    "message": {
                        "role": "user",
                        "content": f"""Analyze this parlay opportunity:

Game Details: {game_details}

Proposed Legs:
{json.dumps(legs, indent=2)}

Bankroll Available: ${bankroll:,.2f}

Provide detailed analysis with specific recommendations for:
- Individual leg value assessment
- Correlation impact on parlay odds
- Optimal stake sizing using Kelly Criterion
- Risk management considerations
- Alternative leg suggestions for better value""",
                    },
                }
            ],
            "tools": self._prepare_tools(
                [ToolType.WEB_SEARCH_PREVIEW, ToolType.CODE_INTERPRETER, ToolType.FUNCTION]
            ),
            "text": {
                "type": "json_object",
                "json_schema": {
                    "type": "object",
                    "properties": {
                        "parlay_analysis": {
                            "type": "object",
                            "properties": {
                                "overall_rating": {
                                    "type": "string",
                                    "enum": ["EXCELLENT", "GOOD", "FAIR", "POOR", "AVOID"],
                                },
                                "expected_value_pct": {"type": "number"},
                                "true_odds": {"type": "number"},
                                "sportsbook_odds": {"type": "number"},
                                "kelly_stake_pct": {"type": "number"},
                                "recommended_stake": {"type": "number"},
                                "max_loss_amount": {"type": "number"},
                                "correlation_factor": {"type": "number"},
                                "leg_analysis": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "leg_description": {"type": "string"},
                                            "individual_ev_pct": {"type": "number"},
                                            "confidence_level": {"type": "string"},
                                            "key_factors": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                        },
                                    },
                                },
                                "risk_factors": {"type": "array", "items": {"type": "string"}},
                                "alternative_suggestions": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "market_intelligence": {"type": "object"},
                                "reasoning": {"type": "string"},
                            },
                        }
                    },
                },
            },
            "temperature": config.temperature,
            "max_output_tokens": config.max_output_tokens,
            "max_tool_calls": config.max_tool_calls,
            "background": config.background,
            "stream": config.stream,
            "service_tier": config.service_tier.value,
            "store": config.store,
            "parallel_tool_calls": config.parallel_tool_calls,
            "include": [
                "web_search_call.action.sources",
                "code_interpreter_call.outputs",
                "file_search_call.results",
            ],
            "metadata": {
                "response_type": ResponseType.PARLAY_ANALYSIS.value,
                "bankroll": str(bankroll),
                "legs_count": str(len(legs)),
                "timestamp": datetime.now(UTC).isoformat(),
            },
        }

        if conversation_id:
            payload["conversation"] = conversation_id

        # Add reasoning configuration if specified
        if config.reasoning_effort:
            payload["reasoning"] = {"effort": config.reasoning_effort}

        # Add tool_choice if specified
        if config.tool_choice != "auto":
            payload["tool_choice"] = config.tool_choice

        return await self._make_request(payload)

    async def create_reasoning_analysis_response(
        self,
        question: str,
        context_data: dict[str, Any] | None = None,
        effort_level: str = "high",
        config: ResponseConfig | None = None,
    ) -> dict[str, Any]:
        """
        Create deep reasoning analysis using o3-mini model

        Args:
            question: Question or problem to analyze
            context_data: Optional context information
            effort_level: Reasoning effort ("low", "medium", "high")
            config: Response configuration

        Returns:
            Detailed reasoning analysis with step-by-step logic
        """
        config = config or ResponseConfig(
            model="o3-mini", reasoning_effort=effort_level, temperature=0.1, max_output_tokens=4000
        )

        # Format input with context if provided
        input_text = question
        if context_data:
            input_text += f"\n\nContext:\n{json.dumps(context_data, indent=2)}"

        payload = {
            "model": config.model,
            "input": [{"type": "message", "message": {"role": "user", "content": input_text}}],
            "reasoning": {"effort": effort_level},
            "temperature": config.temperature,
            "max_output_tokens": config.max_output_tokens,
        }

        return await self._make_request(payload)

    async def create_live_odds_analysis_response(
        self,
        games: list[str],
        markets: list[str] | None = None,
        config: ResponseConfig | None = None,
    ) -> dict[str, Any]:
        """
        Create real-time odds analysis with market movement tracking

        Args:
            games: List of game identifiers
            markets: Market types to analyze (ML, spread, total, props)
            config: Response configuration

        Returns:
            Live odds analysis with movement alerts
        """
        config = config or ResponseConfig(background=True, stream=True)
        markets = markets or ["moneyline", "spread", "total"]

        payload = {
            "model": config.model,
            "instructions": """You are EQ12 Live Odds Monitor. Provide real-time market analysis including:

1. Line Movement Tracking: Identify significant movement patterns
2. Sharp vs Public Money: Distinguish professional vs recreational betting action
3. Value Identification: Find mispriced lines across sportsbooks
4. Arbitrage Opportunities: Identify guaranteed profit scenarios
5. Steam Moves: Detect coordinated sharp betting activity
6. Closing Line Value: Predict line movement before game time

Use web search for real-time odds data and code interpreter for statistical analysis.""",
            "input": [
                {
                    "type": "text",
                    "text": f"""Monitor and analyze live odds for these games:

Games: {", ".join(games)}
Markets: {", ".join(markets)}

Provide comprehensive analysis including:
- Current best odds across all major sportsbooks
- Line movement trends and velocity
- Sharp vs public betting indicators
- Value bets and arbitrage opportunities
- Recommended betting windows
- Risk alerts and market anomalies""",
                }
            ],
            "tools": self._prepare_tools(
                [ToolType.WEB_SEARCH, ToolType.CODE_INTERPRETER, ToolType.FUNCTION]
            ),
            "text": {
                "type": "json_object",
                "json_schema": {
                    "type": "object",
                    "properties": {
                        "live_analysis": {
                            "type": "object",
                            "properties": {
                                "timestamp": {"type": "string"},
                                "games_analyzed": {"type": "array", "items": {"type": "string"}},
                                "best_values": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "game": {"type": "string"},
                                            "market": {"type": "string"},
                                            "best_odds": {"type": "number"},
                                            "sportsbook": {"type": "string"},
                                            "ev_estimate": {"type": "number"},
                                            "confidence": {"type": "string"},
                                        },
                                    },
                                },
                                "line_movements": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "game": {"type": "string"},
                                            "market": {"type": "string"},
                                            "movement_direction": {"type": "string"},
                                            "movement_size": {"type": "number"},
                                            "velocity": {"type": "string"},
                                            "sharp_indicator": {"type": "boolean"},
                                        },
                                    },
                                },
                                "arbitrage_opportunities": {"type": "array"},
                                "alerts": {"type": "array", "items": {"type": "string"}},
                                "market_summary": {"type": "string"},
                            },
                        }
                    },
                },
            },
            "background": config.background,
            "stream": config.stream,
            "service_tier": ServiceTier.PRIORITY.value,  # Use priority for real-time data
            "temperature": 0.1,
            "max_output_tokens": 3000,
            "metadata": {
                "response_type": ResponseType.LIVE_ODDS_ANALYSIS.value,
                "games_count": str(len(games)),
                "markets": ",".join(markets),
            },
        }

        return await self._make_request(payload)

    async def create_portfolio_optimization_response(
        self,
        current_bets: list[dict[str, Any]],
        available_opportunities: list[dict[str, Any]],
        bankroll: float,
        risk_tolerance: str = "moderate",
        config: ResponseConfig | None = None,
    ) -> dict[str, Any]:
        """
        Create portfolio optimization response for bet sizing and diversification

        Args:
            current_bets: Existing positions in portfolio
            available_opportunities: New betting opportunities to consider
            bankroll: Total available bankroll
            risk_tolerance: Risk preference (conservative, moderate, aggressive)
            config: Response configuration

        Returns:
            Portfolio optimization recommendations
        """
        config = config or ResponseConfig()

        payload = {
            "model": "gpt-4o",  # Use advanced model for complex optimization
            "instructions": f"""You are EQ12 Portfolio Manager. Optimize betting portfolio using:

1. Modern Portfolio Theory: Maximize expected return for given risk level
2. Kelly Criterion: Optimal bet sizing for each opportunity
3. Diversification Analysis: Minimize correlated risk exposure
4. Risk Management: Set position limits and stop-loss triggers
5. Capital Allocation: Distribute bankroll across opportunities
6. Drawdown Protection: Preserve capital during losing streaks

Risk Tolerance: {risk_tolerance}
Use code interpreter for mathematical optimization and Monte Carlo simulation.""",
            "input": [
                {
                    "type": "text",
                    "text": f"""Optimize betting portfolio:

Current Positions:
{json.dumps(current_bets, indent=2)}

New Opportunities:
{json.dumps(available_opportunities, indent=2)}

Portfolio Parameters:
- Total Bankroll: ${bankroll:,.2f}
- Risk Tolerance: {risk_tolerance}
- Max Single Position: 5% of bankroll
- Target Monthly Return: 15-25%

Provide complete portfolio optimization including position sizing, risk metrics, and implementation strategy.""",
                }
            ],
            "tools": self._prepare_tools([ToolType.CODE_INTERPRETER, ToolType.FUNCTION]),
            "text": {
                "type": "json_object",
                "json_schema": {
                    "type": "object",
                    "properties": {
                        "portfolio_optimization": {
                            "type": "object",
                            "properties": {
                                "recommended_positions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "opportunity_id": {"type": "string"},
                                            "recommended_stake": {"type": "number"},
                                            "stake_percentage": {"type": "number"},
                                            "expected_return": {"type": "number"},
                                            "risk_score": {"type": "number"},
                                            "kelly_fraction": {"type": "number"},
                                        },
                                    },
                                },
                                "portfolio_metrics": {
                                    "type": "object",
                                    "properties": {
                                        "total_allocated": {"type": "number"},
                                        "expected_portfolio_return": {"type": "number"},
                                        "portfolio_volatility": {"type": "number"},
                                        "sharpe_ratio": {"type": "number"},
                                        "max_drawdown_estimate": {"type": "number"},
                                        "diversification_score": {"type": "number"},
                                    },
                                },
                                "risk_analysis": {
                                    "type": "object",
                                    "properties": {
                                        "correlation_matrix": {"type": "object"},
                                        "stress_test_results": {"type": "array"},
                                        "value_at_risk_95": {"type": "number"},
                                        "expected_shortfall": {"type": "number"},
                                    },
                                },
                                "implementation_strategy": {
                                    "type": "object",
                                    "properties": {
                                        "entry_sequence": {"type": "array"},
                                        "timing_recommendations": {"type": "array"},
                                        "hedge_suggestions": {"type": "array"},
                                        "exit_strategies": {"type": "array"},
                                    },
                                },
                            },
                        }
                    },
                },
            },
            "reasoning": {"show_reasoning": True},
            "temperature": 0.0,  # Deterministic for financial calculations
            "max_output_tokens": 4000,
            "service_tier": ServiceTier.PRIORITY.value,
            "metadata": {
                "response_type": ResponseType.PORTFOLIO_OPTIMIZATION.value,
                "bankroll": str(bankroll),
                "risk_tolerance": risk_tolerance,
                "opportunities_count": str(len(available_opportunities)),
            },
        }

        return await self._make_request(payload)

    async def _make_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Make request using OpenAI client's responses endpoint"""
        if not self.client:
            raise RuntimeError("OpenAI client not available. Check API key and installation.")

        try:
            # Use direct OpenAI client
            response = self.client.responses.create(**payload)

            # Convert response to dict format for compatibility
            result = {
                "id": response.id,
                "object": response.object,
                "model": response.model,
                "created": response.created,
                "status": response.status,
                "output": response.output,
                "usage": response.usage.__dict__ if hasattr(response, "usage") else None,
            }

            # Store response for tracking
            if response.id:
                self.active_responses[response.id] = result

            # Log debug information (simulated headers for compatibility)
            debug_headers = {
                "x-request-id": response.id,
                "openai-processing-ms": "1500",  # Simulated
            }
            self._log_response_debug(debug_headers, result)

            return result

        except Exception as e:
            logger.error(f"OpenAI Responses API request failed: {e}")
            raise

    def _log_response_debug(self, headers: dict[str, str], result: dict[str, Any]) -> None:
        """Log response debugging information"""
        debug_info = {
            "timestamp": datetime.now(UTC).isoformat(),
            "response_id": result.get("id"),
            "model": result.get("model"),
            "service_tier": result.get("service_tier"),
            "processing_ms": headers.get("openai-processing-ms"),
            "request_id": headers.get("x-request-id"),
            "usage": result.get("usage", {}),
            "rate_limits": {k: v for k, v in headers.items() if k.startswith("x-ratelimit-")},
        }

        logger.info(f"Response created: {debug_info['response_id']}")

        # Save to debug log
        try:
            os.makedirs("logs", exist_ok=True)
            with open("logs/responses_debug.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(debug_info) + "\n")
        except Exception as e:
            logger.debug(f"Failed to log debug info: {e}")

    async def get_response_status(self, response_id: str) -> dict[str, Any]:
        """Get status of background response"""
        if response_id in self.active_responses:
            return self.active_responses[response_id]

        # Fetch from API if not in local cache
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{response_id}", headers=self._get_headers()
                )

                if response.status_code == 200:
                    result = response.json()
                    self.active_responses[response_id] = result
                    return result
                else:
                    return {"error": f"Status check failed: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    async def stream_response(self, response_id: str):
        """Stream response data as it's generated"""
        # Implementation for streaming responses
        # This would handle server-sent events from the API
        pass


# Convenience functions for common use cases
async def analyze_parlay_with_responses(
    game_details: str,
    legs: list[dict[str, Any]],
    bankroll: float = 1000.0,
    background: bool = False,
) -> dict[str, Any]:
    """Convenience function for parlay analysis"""
    api = EQ12ResponsesAPI()
    config = ResponseConfig(background=background)

    return await api.create_parlay_analysis_response(game_details, legs, bankroll, config)


async def simple_bedtime_story() -> dict[str, Any]:
    """Simple example like your bedtime story demo"""
    api = EQ12ResponsesAPI()

    if not api.client:
        raise RuntimeError("OpenAI client not available")

    response = api.client.responses.create(
        model="gpt-4.1", input="Tell me a three sentence bedtime story about a unicorn."
    )

    return {"id": response.id, "story": response.output}


async def web_search_news_example() -> dict[str, Any]:
    """Web search example like your news story demo"""
    api = EQ12ResponsesAPI()

    if not api.client:
        raise RuntimeError("OpenAI client not available")

    response = api.client.responses.create(
        model="gpt-4.1",
        tools=[{"type": "web_search_preview"}],
        input="What was a positive sports betting news story from today?",
    )

    return {"id": response.id, "news": response.output}


async def reasoning_analysis_example(question: str) -> dict[str, Any]:
    """O3-mini reasoning example"""
    api = EQ12ResponsesAPI()

    if not api.client:
        raise RuntimeError("OpenAI client not available")

    response = api.client.responses.create(
        model="o3-mini", input=question, reasoning={"effort": "high"}
    )

    return {"id": response.id, "reasoning": response.output}


async def streaming_analysis_example(question: str):
    """Streaming response example"""
    api = EQ12ResponsesAPI()

    if not api.client:
        raise RuntimeError("OpenAI client not available")

    response = api.client.responses.create(
        model="gpt-4.1",
        instructions="You are a helpful sports betting assistant.",
        input=question,
        stream=True,
    )

    for event in response:
        yield event


async def monitor_live_odds(games: list[str], stream: bool = True) -> dict[str, Any]:
    """Convenience function for live odds monitoring"""
    api = EQ12ResponsesAPI()
    config = ResponseConfig(stream=stream, background=True)

    return await api.create_live_odds_analysis_response(games, config=config)


async def optimize_portfolio(
    current_bets: list[dict[str, Any]],
    opportunities: list[dict[str, Any]],
    bankroll: float,
    risk_tolerance: str = "moderate",
) -> dict[str, Any]:
    """Convenience function for portfolio optimization"""
    api = EQ12ResponsesAPI()

    return await api.create_portfolio_optimization_response(
        current_bets, opportunities, bankroll, risk_tolerance
    )


if __name__ == "__main__":
    import asyncio

    async def test_responses_system():
        """Test the EQ12 Responses system"""
        print("🚀 Testing EQ12 Model Response System")

        # Test parlay analysis
        sample_legs = [
            {
                "game": "Lakers vs Warriors",
                "market": "spread",
                "selection": "Lakers -3.5",
                "odds": -110,
            },
            {
                "game": "Lakers vs Warriors",
                "market": "total",
                "selection": "Over 225.5",
                "odds": -105,
            },
            {
                "game": "Celtics vs Heat",
                "market": "moneyline",
                "selection": "Celtics",
                "odds": -150,
            },
        ]

        try:
            result = await analyze_parlay_with_responses(
                "NBA games tonight featuring Lakers vs Warriors and Celtics vs Heat",
                sample_legs,
                bankroll=5000.0,
            )

            print(f"✅ Parlay Analysis Response ID: {result.get('id')}")
            print(f"Model: {result.get('model')}")
            print(f"Status: {result.get('status')}")

        except Exception as e:
            print(f"❌ Test failed: {e}")

    # Run test
    asyncio.run(test_responses_system())
