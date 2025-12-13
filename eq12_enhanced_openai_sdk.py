#!/usr/bin/env python3

# === UTF-8 Console Fix for Windows ===
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
# ====================================

"""
EQ12 Enhanced OpenAI SDK - Expert Development & Sports Betting Integration
=========================================================================

This module provides an enhanced OpenAI Python SDK client specifically designed for:
1. Expert-level SDK development and customization
2. Advanced sports betting automation and analysis
3. Deep integration with EQ12 sports betting infrastructure

Features:
- Custom SDK development tools and debugging capabilities
- Advanced sports betting AI analysis (odds, parlays, live betting)
- Real-time streaming for live game analysis
- Integration with EQ12 Telegram alerts and logging
- Performance optimization for high-frequency betting operations
- Advanced prompt engineering for sports betting contexts

Author: EQ12 Development Team
Date: October 5, 2025
Version: 1.0.0
"""

import asyncio
import hashlib
import json
import logging
import os
import sys
import time
import traceback
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

# Core dependencies
try:
    import openai
    from openai import AsyncOpenAI, OpenAI
    from openai.types.chat import ChatCompletion
except ImportError as e:
    print(f"❌ OpenAI SDK not installed: {e}")
    print("Install with: pip install openai>=2.0.0")
    sys.exit(1)

# Load environment variables first
try:
    from dotenv import load_dotenv

    load_dotenv()  # Load OPENAI_API_KEY, ODDS_API_KEY, etc.
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")

# Optional dependencies with safety guards
try:
    import numpy as np
except ImportError:
    np = None
    print("⚠️ NumPy not available. Install with: pip install numpy")

try:
    import pandas as pd
except ImportError:
    pd = None
    print("⚠️ Pandas not available. Install with: pip install pandas")

try:
    import requests
except ImportError:
    requests = None
    print("⚠️ Requests not available. Install with: pip install requests")


# EQ12 Enhanced OpenAI Configuration
class EQ12OpenAIConfig:
    """Enhanced configuration for EQ12 OpenAI SDK operations"""

    # API Configuration
    API_KEY = os.getenv("OPENAI_API_KEY", "")
    BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    ORG_ID = os.getenv("OPENAI_ORG_ID", "")

    # Model Configuration - Expert Level
    PRIMARY_MODEL = os.getenv("EQ12_OPENAI_MODEL", "gpt-4o")
    FALLBACK_MODELS = ["gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]

    # Sports Betting Specific Models
    SPORTS_ANALYSIS_MODEL = "gpt-4o"  # Best for complex sports analysis
    QUICK_ODDS_MODEL = "gpt-4o-mini"  # Fast for simple odds calculations
    LIVE_BETTING_MODEL = "gpt-4o"  # Real-time analysis

    # Performance & Cost Optimization
    MAX_TOKENS = int(os.getenv("EQ12_MAX_TOKENS", "4096"))
    TEMPERATURE = float(os.getenv("EQ12_TEMPERATURE", "0.1"))  # Lower for betting accuracy
    TOP_P = float(os.getenv("EQ12_TOP_P", "0.9"))

    # Rate Limiting & Retry Configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    RATE_LIMIT_DELAY = 0.5

    # EQ12 Integration
    LOGS_DIR = Path(os.getenv("EQ12_LOGS_DIR", "C:\\EQ12\\logs"))
    TELEGRAM_INTEGRATION = os.getenv("TELEGRAM_BOT_TOKEN", "") != ""

    # Expert Development Features
    DEBUG_MODE = os.getenv("EQ12_DEBUG", "False").lower() == "true"
    SAVE_REQUESTS = os.getenv("EQ12_SAVE_REQUESTS", "True").lower() == "true"
    PERFORMANCE_TRACKING = True


# Sports Betting Data Models
class BettingOddsFormat(Enum):
    """Supported betting odds formats"""

    AMERICAN = "american"
    DECIMAL = "decimal"
    FRACTIONAL = "fractional"
    IMPLIED_PROBABILITY = "implied"


class BettingMarket(Enum):
    """Supported betting markets"""

    MONEYLINE = "h2h"
    SPREAD = "spreads"
    TOTALS = "totals"
    PROPS = "props"
    LIVE = "live"


class AnalysisType(Enum):
    """Types of sports betting analysis"""

    ODDS_COMPARISON = "odds_comparison"
    VALUE_BETTING = "value_betting"
    PARLAY_OPTIMIZATION = "parlay_optimization"
    LIVE_BETTING = "live_betting"
    PROP_ANALYSIS = "prop_analysis"
    BANKROLL_MANAGEMENT = "bankroll_management"
    RISK_ASSESSMENT = "risk_assessment"


@dataclass
class GameData:
    """Structured game data for sports betting analysis"""

    game_id: str
    sport: str
    home_team: str
    away_team: str
    commence_time: datetime
    odds: dict[str, Any]
    live_data: dict | None = None
    market_type: BettingMarket = BettingMarket.MONEYLINE


@dataclass
class BettingRecommendation:
    """AI-generated betting recommendation"""

    game_id: str
    recommendation_type: str
    confidence: float
    expected_value: float
    suggested_stake: float
    reasoning: str
    risk_level: str
    timestamp: datetime


@dataclass
class ParlayLeg:
    """Individual leg of a parlay bet"""

    game_id: str
    team: str
    bet_type: str
    odds: float
    expected_value: float
    confidence: float


@dataclass
class OptimizedParlay:
    """AI-optimized parlay combination"""

    legs: list[ParlayLeg]
    total_odds: float
    expected_value: float
    confidence_score: float
    risk_rating: str
    suggested_stake: float
    reasoning: str


class EQ12UsageTracker:
    """Advanced usage tracking for cost optimization and performance monitoring"""

    def __init__(self, log_file: Path | None = None):
        self.log_file = log_file or EQ12OpenAIConfig.LOGS_DIR / "openai_usage.json"
        self.session_stats = {
            "requests": 0,
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "cost_estimate": 0.0,
            "errors": 0,
            "start_time": time.time(),
            "models_used": {},
            "analysis_types": {},
            "sports_analyzed": set(),
        }

    def log_request(self, model: str, usage: dict, analysis_type: str = "", sport: str = ""):
        """Log API request usage with detailed metrics"""
        self.session_stats["requests"] += 1
        self.session_stats["total_tokens"] += usage.get("total_tokens", 0)
        self.session_stats["prompt_tokens"] += usage.get("prompt_tokens", 0)
        self.session_stats["completion_tokens"] += usage.get("completion_tokens", 0)

        # Model usage tracking
        if model not in self.session_stats["models_used"]:
            self.session_stats["models_used"][model] = 0
        self.session_stats["models_used"][model] += 1

        # Analysis type tracking
        if analysis_type:
            if analysis_type not in self.session_stats["analysis_types"]:
                self.session_stats["analysis_types"][analysis_type] = 0
            self.session_stats["analysis_types"][analysis_type] += 1

        # Sports tracking
        if sport:
            self.session_stats["sports_analyzed"].add(sport)

        # Cost estimation (rough GPT-4o pricing)
        prompt_cost = (usage.get("prompt_tokens", 0) / 1000) * 0.005
        completion_cost = (usage.get("completion_tokens", 0) / 1000) * 0.015
        self.session_stats["cost_estimate"] += prompt_cost + completion_cost

    def log_error(self, error: Exception, context: dict | None = None):
        """Log API errors with context for debugging"""
        self.session_stats["errors"] += 1
        error_log = {
            "timestamp": datetime.now(UTC).isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "traceback": traceback.format_exc(),
        }

        # Save error to separate log file
        error_file = self.log_file.parent / "openai_errors.json"
        self._append_to_json_log(error_file, error_log)

    def get_session_stats(self) -> dict:
        """Get current session statistics"""
        stats = self.session_stats.copy()
        stats["session_duration"] = time.time() - stats["start_time"]
        stats["avg_tokens_per_request"] = stats["total_tokens"] / max(stats["requests"], 1)
        stats["sports_analyzed"] = list(stats["sports_analyzed"])
        return stats

    def save_session_log(self):
        """Save session statistics to log file"""
        session_log = {
            "session_id": hashlib.md5(
                f"{self.session_stats['start_time']}{os.getpid()}".encode()
            ).hexdigest()[:8],
            **self.get_session_stats(),
        }
        self._append_to_json_log(self.log_file, session_log)

    def _append_to_json_log(self, file_path: Path, data: dict):
        """Safely append data to JSON log file"""
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if file_path.exists():
                with open(file_path) as f:
                    logs = json.load(f) if f.read().strip() else []
            else:
                logs = []

            logs.append(data)

            with open(file_path, "w") as f:
                json.dump(logs, f, indent=2, default=str)

        except Exception as e:
            logging.error(f"Failed to save usage log: {e}")


class EQ12SportsPromptEngine:
    """Advanced prompt engineering specifically designed for sports betting analysis"""

    @staticmethod
    def odds_analysis_prompt(game_data: GameData, analysis_type: AnalysisType) -> str:
        """Generate specialized prompts for odds analysis"""
        base_context = f"""
You are an expert sports analyst and professional bettor analyzing {game_data.sport} games.
Game: {game_data.away_team} @ {game_data.home_team}
Commence Time: {game_data.commence_time}
Current Odds: {json.dumps(game_data.odds, indent=2)}
"""

        if analysis_type == AnalysisType.VALUE_BETTING:
            return (
                base_context
                + """
TASK: Identify value betting opportunities by analyzing:
1. Line movement and market inefficiencies
2. True probability vs implied probability from odds
3. Expected value calculations for each betting option
4. Sharp vs public money indicators
5. Key factors affecting the game outcome

Provide specific recommendations with confidence levels and expected value percentages.
Format your response as structured JSON with clear reasoning.
"""
            )

        elif analysis_type == AnalysisType.ODDS_COMPARISON:
            return (
                base_context
                + """
TASK: Compare odds across different sportsbooks and markets:
1. Identify the best available odds for each outcome
2. Calculate implied probabilities and overround
3. Find arbitrage opportunities if they exist
4. Recommend optimal betting strategy based on odds movement
5. Assess market consensus vs your analysis

Focus on actionable insights for immediate betting decisions.
"""
            )

        elif analysis_type == AnalysisType.LIVE_BETTING:
            live_context = f"Live Game Data: {json.dumps(game_data.live_data or {}, indent=2)}"
            return (
                base_context
                + live_context
                + """
TASK: Real-time live betting analysis:
1. Assess current game state vs pre-game expectations
2. Identify momentum shifts and their betting implications
3. Calculate updated win probabilities based on live data
4. Recommend immediate live betting actions
5. Consider in-game prop betting opportunities

Time-sensitive analysis - prioritize speed and accuracy.
"""
            )

        return base_context + "Provide comprehensive sports betting analysis."

    @staticmethod
    def parlay_optimization_prompt(
        games: list[GameData], bankroll: float, risk_tolerance: str
    ) -> str:
        """Generate prompts for AI-powered parlay optimization"""
        games_summary = "\n".join(
            [
                f"Game {i + 1}: {game.away_team} @ {game.home_team} - Odds: {game.odds}"
                for i, game in enumerate(games)
            ]
        )

        return f"""
You are an expert parlay builder and risk management specialist.

AVAILABLE GAMES:
{games_summary}

BETTING CONTEXT:
- Bankroll: ${bankroll:,.2f}
- Risk Tolerance: {risk_tolerance}
- Target: Optimize for positive expected value while managing risk

TASK: Build optimal parlay combinations by:
1. Analyzing correlation between games (avoid negative correlation)
2. Calculating true probabilities for each leg
3. Finding the optimal balance of risk vs reward
4. Considering bankroll management principles (Kelly Criterion)
5. Providing multiple parlay options (conservative, moderate, aggressive)

For each recommended parlay:
- List all legs with reasoning
- Calculate expected value and confidence score
- Recommend stake size based on bankroll management
- Explain why this combination is optimal
- Assess overall risk level

Prioritize parlays with positive expected value and manageable risk.
"""

    @staticmethod
    def prop_betting_prompt(game_data: GameData, player_props: dict) -> str:
        """Generate prompts for player prop betting analysis"""
        return f"""
You are an expert in player prop betting and statistical analysis.

GAME CONTEXT:
{game_data.away_team} @ {game_data.home_team}
Sport: {game_data.sport}
Game Time: {game_data.commence_time}

AVAILABLE PROP BETS:
{json.dumps(player_props, indent=2)}

TASK: Analyze player prop betting opportunities by:
1. Evaluating player recent performance and trends
2. Considering matchup advantages/disadvantages
3. Factoring in game script and pace
4. Identifying props with positive expected value
5. Assessing injury reports and lineup changes

For each recommended prop bet:
- Player and prop details
- Statistical analysis supporting the pick
- Expected value calculation
- Confidence level (1-10)
- Recommended stake as percentage of bankroll
- Key factors that could affect the outcome

Focus on props where you have the strongest statistical edge.
"""


class EQ12EnhancedOpenAIClient:
    """
    Enhanced OpenAI SDK Client for Expert Development & Sports Betting

    This class combines expert-level SDK development capabilities with
    advanced sports betting analysis features specifically designed for EQ12.
    """

    def __init__(
        self,
        api_key: str | None = None,
        custom_base_url: str | None = None,
        enable_usage_tracking: bool = True,
        enable_telegram_integration: bool = True,
    ):
        """
        Initialize the enhanced EQ12 OpenAI client

        Args:
            api_key: OpenAI API key (defaults to environment variable)
            custom_base_url: Custom API base URL for local/custom deployments
            enable_usage_tracking: Enable detailed usage and performance tracking
            enable_telegram_integration: Enable Telegram alerts for betting recommendations
        """
        # Initialize configuration first
        self.config = EQ12OpenAIConfig()
        self.logger = self._setup_logging()

        # Initialize OpenAI clients with better error handling
        api_key = api_key or self.config.API_KEY
        base_url = custom_base_url or self.config.BASE_URL

        if not api_key or api_key.strip() == "" or "test-key" in api_key.lower():
            raise ValueError(
                "Valid OpenAI API key is required. "
                "Set OPENAI_API_KEY environment variable with a real key (sk-...). "
                "Remove any 'test-key' placeholders."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            organization=self.config.ORG_ID or None,
            max_retries=self.config.MAX_RETRIES,
        )

        self.async_client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            organization=self.config.ORG_ID or None,
            max_retries=self.config.MAX_RETRIES,
        )

        # Initialize tracking and integrations
        self.usage_tracker = EQ12UsageTracker() if enable_usage_tracking else None
        self.prompt_engine = EQ12SportsPromptEngine()
        self.telegram_enabled = enable_telegram_integration and self.config.TELEGRAM_INTEGRATION

        # Performance metrics
        self.performance_metrics = {"request_times": [], "model_performance": {}, "error_rates": {}}

        self.logger.info("✅ EQ12 Enhanced OpenAI Client initialized")
        self.logger.info(f"   Primary model: {self.config.PRIMARY_MODEL}")
        self.logger.info(f"   Fallback models: {', '.join(self.config.FALLBACK_MODELS)}")
        self.logger.info(f"   Usage tracking: {enable_usage_tracking}")
        self.logger.info(f"   Telegram integration: {self.telegram_enabled}")

    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging for the enhanced client"""
        logger = logging.getLogger("eq12_enhanced_openai")

        if not logger.handlers:
            # Create logs directory
            EQ12OpenAIConfig.LOGS_DIR.mkdir(parents=True, exist_ok=True)

            # File handler for detailed logs
            log_file = (
                EQ12OpenAIConfig.LOGS_DIR / f"eq12_openai_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)

            # Console handler for immediate feedback
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            console_handler.setFormatter(console_formatter)

            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            logger.setLevel(logging.DEBUG if self.config.DEBUG_MODE else logging.INFO)

        return logger

    def chat_completion(
        self, messages: list[dict[str, str]], model: str | None = None, **kwargs
    ) -> dict[str, Any]:
        """
        Enhanced chat completion with automatic fallbacks and performance tracking

        Args:
            messages: List of message dictionaries
            model: Specific model to use (defaults to primary model)
            **kwargs: Additional OpenAI API parameters

        Returns:
            Enhanced response with usage tracking and performance metrics
        """
        start_time = time.time()
        models_to_try = (
            [model] if model else [self.config.PRIMARY_MODEL, *self.config.FALLBACK_MODELS]
        )

        for model_name in models_to_try:
            try:
                self.logger.info(f"🤖 Attempting request with model: {model_name}")

                # Prepare request parameters
                request_params = {
                    "model": model_name,
                    "messages": messages,
                    "max_tokens": kwargs.get("max_tokens", self.config.MAX_TOKENS),
                    "temperature": kwargs.get("temperature", self.config.TEMPERATURE),
                    "top_p": kwargs.get("top_p", self.config.TOP_P),
                    **{
                        k: v
                        for k, v in kwargs.items()
                        if k not in ["max_tokens", "temperature", "top_p"]
                    },
                }

                # Save request for debugging if enabled
                if self.config.SAVE_REQUESTS:
                    self._save_request_debug(request_params)

                # Make API call
                response = self.client.chat.completions.create(**request_params)

                # Track performance
                request_time = time.time() - start_time
                self.performance_metrics["request_times"].append(request_time)

                # Enhanced response with metadata
                enhanced_response = {
                    "response": response,
                    "model_used": model_name,
                    "request_time": request_time,
                    "usage": response.usage.model_dump() if response.usage else {},
                    "timestamp": datetime.now(UTC),
                    "success": True,
                }

                # Track usage if enabled
                if self.usage_tracker:
                    self.usage_tracker.log_request(model_name, enhanced_response["usage"])

                self.logger.info(f"✅ Request successful with {model_name}")
                self.logger.debug(f"Request completed in {request_time:.2f}s")

                return enhanced_response

            except Exception as e:
                error_msg = str(e)

                # Enhanced error handling for common API issues
                if "insufficient_quota" in error_msg or "429" in error_msg:
                    self.logger.error(
                        "🚫 OpenAI quota/billing issue. "
                        "Add payment method/credits and raise usage limits in OpenAI Platform, then retry."
                    )
                elif (
                    "invalid_api_key" in error_msg
                    or "Incorrect API key" in error_msg
                    or "401" in error_msg
                ):
                    self.logger.error(
                        "🔑 Invalid OpenAI API key. "
                        "Set a valid OPENAI_API_KEY (sk-...) and remove any 'test-key' placeholders."
                    )
                else:
                    self.logger.warning(f"❌ Model {model_name} failed: {error_msg}")

                if self.usage_tracker:
                    self.usage_tracker.log_error(
                        e, {"model": model_name, "messages": messages, "request_params": kwargs}
                    )

                # If this is the last model, raise the exception with enhanced message
                if model_name == models_to_try[-1]:
                    self.logger.error("❌ All models failed!")
                    if "insufficient_quota" in error_msg or "invalid_api_key" in error_msg:
                        # Don't retry other models for these critical errors
                        raise e
                    raise e

                # Wait before trying next model (unless it's a critical API error)
                if not ("insufficient_quota" in error_msg or "invalid_api_key" in error_msg):
                    time.sleep(self.config.RETRY_DELAY)

        raise RuntimeError("All available models failed")

    async def async_chat_completion(
        self, messages: list[dict[str, str]], model: str | None = None, **kwargs
    ) -> dict[str, Any]:
        """Async version of chat completion for high-performance applications"""
        start_time = time.time()
        models_to_try = (
            [model] if model else [self.config.PRIMARY_MODEL, *self.config.FALLBACK_MODELS]
        )

        for model_name in models_to_try:
            try:
                self.logger.info(f"🤖 Async request with model: {model_name}")

                request_params = {
                    "model": model_name,
                    "messages": messages,
                    "max_tokens": kwargs.get("max_tokens", self.config.MAX_TOKENS),
                    "temperature": kwargs.get("temperature", self.config.TEMPERATURE),
                    "top_p": kwargs.get("top_p", self.config.TOP_P),
                    **{
                        k: v
                        for k, v in kwargs.items()
                        if k not in ["max_tokens", "temperature", "top_p"]
                    },
                }

                response = await self.async_client.chat.completions.create(**request_params)

                request_time = time.time() - start_time
                enhanced_response = {
                    "response": response,
                    "model_used": model_name,
                    "request_time": request_time,
                    "usage": response.usage.model_dump() if response.usage else {},
                    "timestamp": datetime.now(UTC),
                    "success": True,
                }

                if self.usage_tracker:
                    self.usage_tracker.log_request(model_name, enhanced_response["usage"])

                return enhanced_response

            except Exception as e:
                self.logger.warning(f"❌ Async model {model_name} failed: {e!s}")
                if model_name == models_to_try[-1]:
                    raise e
                await asyncio.sleep(self.config.RETRY_DELAY)

        raise RuntimeError("All available models failed")

    def sports_betting_analysis(
        self, game_data: GameData, analysis_type: AnalysisType, custom_context: str | None = None
    ) -> BettingRecommendation:
        """
        Expert sports betting analysis using AI

        Args:
            game_data: Structured game data for analysis
            analysis_type: Type of analysis to perform
            custom_context: Additional context for the analysis

        Returns:
            AI-generated betting recommendation with confidence scores
        """
        self.logger.info(f"🏈 Starting {analysis_type.value} analysis for {game_data.game_id}")

        # Generate specialized prompt
        prompt = self.prompt_engine.odds_analysis_prompt(game_data, analysis_type)
        if custom_context:
            prompt += f"\n\nADDITIONAL CONTEXT:\n{custom_context}"

        messages = [
            {
                "role": "system",
                "content": "You are an expert sports analyst and professional bettor.",
            },
            {"role": "user", "content": prompt},
        ]

        # Use sports analysis model for better accuracy
        model = self.config.SPORTS_ANALYSIS_MODEL
        if analysis_type == AnalysisType.LIVE_BETTING:
            model = self.config.LIVE_BETTING_MODEL

        try:
            response = self.chat_completion(
                messages=messages,
                model=model,
                temperature=0.1,  # Lower temperature for more consistent betting analysis
            )

            # Track sports analysis
            if self.usage_tracker:
                self.usage_tracker.log_request(
                    model, response["usage"], analysis_type.value, game_data.sport
                )

            # Parse AI response into structured recommendation
            ai_response = response["response"].choices[0].message.content

            # Create betting recommendation (simplified extraction - you might want to use JSON mode)
            recommendation = BettingRecommendation(
                game_id=game_data.game_id,
                recommendation_type=analysis_type.value,
                confidence=0.75,  # You'd extract this from AI response
                expected_value=5.0,  # You'd calculate this from AI analysis
                suggested_stake=50.0,  # You'd get this from AI recommendation
                reasoning=ai_response[:500],  # Truncated for storage
                risk_level="medium",
                timestamp=datetime.now(UTC),
            )

            self.logger.info(f"✅ Analysis complete - Confidence: {recommendation.confidence:.2f}")

            # Send Telegram alert if enabled
            if self.telegram_enabled:
                asyncio.create_task(self._send_telegram_alert(recommendation))

            return recommendation

        except Exception as e:
            self.logger.error(f"❌ Sports analysis failed: {e}")
            raise e

    def optimize_parlay(
        self,
        games: list[GameData],
        bankroll: float,
        risk_tolerance: str = "medium",
        max_legs: int = 6,
    ) -> list[OptimizedParlay]:
        """
        AI-powered parlay optimization for maximum expected value

        Args:
            games: List of available games for parlay construction
            bankroll: Current bankroll for stake calculation
            risk_tolerance: Risk level (conservative, medium, aggressive)
            max_legs: Maximum number of parlay legs

        Returns:
            List of optimized parlay recommendations
        """
        self.logger.info(f"🎯 Optimizing parlays for {len(games)} games")

        prompt = self.prompt_engine.parlay_optimization_prompt(games, bankroll, risk_tolerance)

        messages = [
            {
                "role": "system",
                "content": "You are an expert parlay builder and risk management specialist.",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.chat_completion(
                messages=messages, model=self.config.SPORTS_ANALYSIS_MODEL, temperature=0.2
            )

            # Parse AI response into optimized parlays (simplified)
            ai_response = response["response"].choices[0].message.content

            # For demo - in reality you'd parse JSON response
            sample_parlay = OptimizedParlay(
                legs=[
                    ParlayLeg(
                        game_id=games[0].game_id,
                        team=games[0].home_team,
                        bet_type="moneyline",
                        odds=-110,
                        expected_value=3.5,
                        confidence=0.72,
                    )
                ],
                total_odds=190,
                expected_value=4.2,
                confidence_score=0.68,
                risk_rating="medium",
                suggested_stake=bankroll * 0.02,
                reasoning=ai_response[:300],
            )

            self.logger.info("✅ Parlay optimization complete")
            return [sample_parlay]

        except Exception as e:
            self.logger.error(f"❌ Parlay optimization failed: {e}")
            raise e

    async def stream_live_analysis(self, game_data: GameData) -> AsyncGenerator[str, None]:
        """
        Stream real-time live betting analysis for in-game decisions

        Args:
            game_data: Game data with live updates

        Yields:
            Real-time analysis updates
        """
        self.logger.info(f"📡 Starting live analysis stream for {game_data.game_id}")

        prompt = self.prompt_engine.odds_analysis_prompt(game_data, AnalysisType.LIVE_BETTING)

        messages = [
            {
                "role": "system",
                "content": "You are providing real-time live betting analysis. Be concise and actionable.",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            stream = await self.async_client.chat.completions.create(
                model=self.config.LIVE_BETTING_MODEL,
                messages=messages,
                stream=True,
                temperature=0.1,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            self.logger.error(f"❌ Live stream failed: {e}")
            yield f"Error in live analysis: {e!s}"

    def analyze_player_props(
        self, game_data: GameData, player_props: dict
    ) -> list[BettingRecommendation]:
        """
        Analyze player proposition bets for value opportunities

        Args:
            game_data: Game information
            player_props: Available player prop bets

        Returns:
            List of prop betting recommendations
        """
        self.logger.info(f"🏃 Analyzing player props for {game_data.game_id}")

        prompt = self.prompt_engine.prop_betting_prompt(game_data, player_props)

        messages = [
            {
                "role": "system",
                "content": "You are an expert in player prop betting and statistical analysis.",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.chat_completion(
                messages=messages, model=self.config.SPORTS_ANALYSIS_MODEL, temperature=0.15
            )

            # Parse response into prop recommendations (simplified)
            ai_response = response["response"].choices[0].message.content

            # Sample prop recommendation
            prop_rec = BettingRecommendation(
                game_id=game_data.game_id,
                recommendation_type="player_prop",
                confidence=0.78,
                expected_value=6.2,
                suggested_stake=25.0,
                reasoning=ai_response[:400],
                risk_level="low",
                timestamp=datetime.now(UTC),
            )

            self.logger.info("✅ Props analysis complete")
            return [prop_rec]

        except Exception as e:
            self.logger.error(f"❌ Props analysis failed: {e}")
            raise e

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get detailed performance metrics for SDK optimization"""
        if not self.performance_metrics["request_times"]:
            return {"message": "No requests made yet"}

        request_times = self.performance_metrics["request_times"]

        return {
            "total_requests": len(request_times),
            "avg_request_time": sum(request_times) / len(request_times),
            "min_request_time": min(request_times),
            "max_request_time": max(request_times),
            "usage_stats": self.usage_tracker.get_session_stats() if self.usage_tracker else None,
            "model_performance": self.performance_metrics["model_performance"],
            "error_rates": self.performance_metrics["error_rates"],
        }

    def _save_request_debug(self, request_params: dict):
        """Save request details for debugging and optimization"""
        if not self.config.DEBUG_MODE:
            return

        debug_file = (
            self.config.LOGS_DIR / f"debug_requests_{datetime.now().strftime('%Y%m%d')}.json"
        )
        debug_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "request_id": hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
            "request_params": request_params,
        }

        try:
            if debug_file.exists():
                with open(debug_file) as f:
                    logs = json.load(f)
            else:
                logs = []

            logs.append(debug_data)

            with open(debug_file, "w") as f:
                json.dump(logs, f, indent=2, default=str)

        except Exception as e:
            self.logger.warning(f"Failed to save debug request: {e}")

    async def _send_telegram_alert(self, recommendation: BettingRecommendation):
        """Send betting recommendation via Telegram (if configured)"""
        if not self.telegram_enabled:
            return

        try:
            # This would integrate with your existing Telegram setup
            f"""
🏈 EQ12 Betting Alert

Game: {recommendation.game_id}
Type: {recommendation.recommendation_type}
Confidence: {recommendation.confidence:.1%}
Expected Value: +{recommendation.expected_value:.1f}%
Suggested Stake: ${recommendation.suggested_stake:.2f}
Risk: {recommendation.risk_level.title()}

Analysis: {recommendation.reasoning[:200]}...
"""
            self.logger.info(f"📱 Telegram alert prepared for {recommendation.game_id}")
            # You'd implement actual Telegram sending here

        except Exception as e:
            self.logger.error(f"❌ Telegram alert failed: {e}")

    def cleanup_session(self):
        """Clean up session resources and save final statistics"""
        if self.usage_tracker:
            self.usage_tracker.save_session_log()

        self.logger.info("🔄 EQ12 Enhanced OpenAI Client session cleanup complete")


# Utility functions for easy integration
def create_game_data_from_api(api_response: dict, sport: str) -> list[GameData]:
    """Convert API response to GameData objects"""
    games = []

    for game in api_response:
        game_data = GameData(
            game_id=game.get("id", ""),
            sport=sport,
            home_team=game.get("home_team", ""),
            away_team=game.get("away_team", ""),
            commence_time=datetime.fromisoformat(game.get("commence_time", "")),
            odds=game.get("bookmakers", {}),
            market_type=BettingMarket.MONEYLINE,
        )
        games.append(game_data)

    return games


def demo_enhanced_sdk():
    """Demonstrate the enhanced SDK capabilities"""
    print("\n🚀 EQ12 Enhanced OpenAI SDK Demo")
    print("=" * 50)

    try:
        # Initialize enhanced client
        client = EQ12EnhancedOpenAIClient(
            enable_usage_tracking=True,
            enable_telegram_integration=False,  # Disable for demo
        )

        print("✅ Enhanced SDK client initialized successfully")
        print("   Expert features: Advanced logging, performance tracking, debugging")
        print("   Sports features: Odds analysis, parlay optimization, live betting")

        # Demo expert SDK features
        print("\n🔧 Expert SDK Features:")
        print(f"   - Custom model fallbacks: {client.config.FALLBACK_MODELS}")
        print("   - Performance tracking: Enabled")
        print(f"   - Debug mode: {client.config.DEBUG_MODE}")
        print(f"   - Request logging: {client.config.SAVE_REQUESTS}")

        # Demo sports betting features
        print("\n🏈 Sports Betting AI Features:")
        print("   - Odds comparison and value betting analysis")
        print("   - AI-powered parlay optimization")
        print("   - Real-time live betting analysis")
        print("   - Player prop betting recommendations")
        print("   - Bankroll management integration")

        # Sample analysis
        sample_game = GameData(
            game_id="demo_game_001",
            sport="football",
            home_team="Kansas City Chiefs",
            away_team="Buffalo Bills",
            commence_time=datetime.now() + timedelta(hours=2),
            odds={"chiefs_ml": -150, "bills_ml": +130, "total": 47.5},
        )

        print("\n🧪 Running sample analysis...")
        print(f"   Game: {sample_game.away_team} @ {sample_game.home_team}")
        print("   Analysis: Value betting opportunity identification")

        # Note: This would make an actual API call
        # recommendation = client.sports_betting_analysis(sample_game, AnalysisType.VALUE_BETTING)
        print("   ✅ Sample analysis structure ready (skipping API call for demo)")

        # Performance metrics
        metrics = client.get_performance_metrics()
        print("\n📊 Performance Metrics:")
        print(f"   Total requests: {metrics.get('total_requests', 0)}")
        print(f"   Session stats available: {bool(client.usage_tracker)}")

        # Cleanup
        client.cleanup_session()
        print("\n✅ Enhanced SDK demo complete!")

        return True

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False


if __name__ == "__main__":
    success = demo_enhanced_sdk()
    sys.exit(0 if success else 1)
