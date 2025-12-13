# eq12_sports_betting_analytics_platform.py
"""
EQ12 Sports Betting Analytics Platform
Advanced parlay analytics with Kelly criterion, expected value calculation,
OpenAI GPT-5 integration, and comprehensive sportsbook API management
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import aioredis
import backoff
import httpx
from openai import AsyncOpenAI
from pydantic import BaseModel, ConfigDict, Field

from eq12_helpers import setup_utf8_logging
from eq12_structured_observability import ObservabilityManager, tracked_operation

setup_utf8_logging()


class BetType(Enum):
    """Types of sports bets"""

    MONEYLINE = "moneyline"
    SPREAD = "spread"
    TOTAL = "total"
    PROP = "prop"
    FUTURES = "futures"


class SportType(Enum):
    """Sports categories"""

    NFL = "nfl"
    NBA = "nba"
    MLB = "mlb"
    NHL = "nhl"
    NCAAF = "ncaaf"
    NCAAB = "ncaab"
    SOCCER = "soccer"
    TENNIS = "tennis"


@dataclass
class OddsData:
    """Standardized odds data structure"""

    sportsbook: str
    sport: SportType
    event_id: str
    market_type: BetType
    selection: str
    odds: float  # American odds
    decimal_odds: float
    implied_probability: float
    timestamp: str
    confidence: float = 1.0
    volume: int | None = None
    line_movement: float | None = None


@dataclass
class KellyCalculation:
    """Kelly criterion calculation results"""

    bet_id: str
    selection: str
    sportsbook_odds: float
    true_probability: float
    implied_probability: float
    edge: float  # Betting edge percentage
    kelly_fraction: float  # Optimal bet size
    recommended_bet: float  # Dollar amount
    bankroll_percentage: float  # Percentage of bankroll
    confidence_interval: tuple[float, float]  # CI for edge
    risk_rating: str  # LOW/MEDIUM/HIGH
    expected_value: float  # Expected value in dollars


class ParlayLeg(BaseModel):
    """Individual leg of a parlay bet"""

    selection: str = Field(..., description="Team or player selection")
    odds: float = Field(..., description="American odds")
    market_type: BetType = Field(..., description="Type of bet")
    sport: SportType = Field(..., description="Sport category")
    event_id: str = Field(..., description="Event identifier")
    sportsbook: str = Field(..., description="Sportsbook source")
    confidence: float = Field(default=1.0, ge=0, le=1, description="Confidence in odds accuracy")

    model_config = ConfigDict(use_enum_values=True)


class ParlayAnalysis(BaseModel):
    """Comprehensive parlay analysis results"""

    parlay_id: str = Field(..., description="Unique parlay identifier")
    legs: list[ParlayLeg] = Field(..., min_items=2, max_items=20)
    stake: float = Field(..., gt=0, description="Bet amount in dollars")

    # Odds calculations
    combined_american_odds: float = Field(..., description="Combined American odds")
    combined_decimal_odds: float = Field(..., description="Combined decimal odds")
    total_implied_probability: float = Field(..., description="Total implied probability")

    # Kelly criterion analysis
    kelly_calculation: KellyCalculation | None = None
    expected_value: float = Field(..., description="Expected value in dollars")
    win_probability: float = Field(..., ge=0, le=1, description="True win probability")
    edge: float = Field(..., description="Betting edge percentage")

    # Risk assessment
    risk_rating: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|EXTREME)$")
    correlation_risk: float = Field(default=0.0, description="Correlation between legs")
    bankroll_impact: float = Field(..., description="Impact on total bankroll")

    # Recommendations
    recommended_action: str = Field(..., pattern="^(BET|PASS|REDUCE_STAKE|SPLIT)$")
    optimal_stake: float | None = Field(None, description="Kelly-optimal stake")
    confidence_score: float = Field(..., ge=0, le=1, description="Overall confidence")

    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    analysis_version: str = Field(default="2.1.0", description="Analysis engine version")


class SportsBookAPI:
    """Unified sportsbook API interface with circuit breaker"""

    def __init__(self, observability: ObservabilityManager, redis_client: aioredis.Redis):
        self.observability = observability
        self.redis = redis_client
        self.client = httpx.AsyncClient(timeout=30.0)

        # Circuit breaker state
        self.circuit_breaker = {
            "failures": 0,
            "last_failure": None,
            "is_open": False,
            "failure_threshold": 5,
            "recovery_timeout": 300,  # 5 minutes
        }

        # API configurations
        self.api_configs = {
            "draftkings": {
                "base_url": "https://sportsbook-us-ny.draftkings.com",
                "rate_limit": 100,  # requests per minute
                "headers": {"User-Agent": "EQ12-Analytics/2.1.0"},
            },
            "fanduel": {
                "base_url": "https://pa.betfair.com/sport",
                "rate_limit": 60,
                "headers": {"Accept": "application/json"},
            },
            "caesars": {
                "base_url": "https://www.caesars.com/sportsbook-and-casino",
                "rate_limit": 80,
                "headers": {"Accept": "application/json"},
            },
        }

    @backoff.on_exception(
        backoff.expo,
        (httpx.RequestError, httpx.HTTPStatusError),
        max_tries=3,
        max_time=60,
    )
    async def fetch_odds(
        self, sportsbook: str, sport: SportType, event_id: str | None = None
    ) -> list[OddsData]:
        """Fetch odds with circuit breaker and retry logic"""

        async with tracked_operation(
            self.observability,
            "fetch_sportsbook_odds",
            sportsbook=sportsbook,
            sport=sport.value,
        ) as ctx:
            # Check circuit breaker
            if self._is_circuit_open():
                raise Exception(f"Circuit breaker open for {sportsbook}")

            try:
                config = self.api_configs.get(sportsbook)
                if not config:
                    raise ValueError(f"Unknown sportsbook: {sportsbook}")

                # Rate limiting check
                await self._check_rate_limit(sportsbook)

                # Fetch odds data
                odds_data = await self._fetch_odds_impl(sportsbook, sport, event_id, config)

                # Reset circuit breaker on success
                self._reset_circuit_breaker()

                # Cache results
                cache_key = f"odds:{sportsbook}:{sport.value}:{event_id or 'all'}"
                await self.redis.setex(
                    cache_key,
                    300,  # 5 minute cache
                    json.dumps([self._serialize_odds(odds) for odds in odds_data]),
                )

                await self.observability.metrics.counter(
                    "sportsbook_odds_fetched",
                    labels={"sportsbook": sportsbook, "sport": sport.value},
                )

                return odds_data

            except Exception as e:
                self._record_failure()
                await self.observability.logger.error(
                    f"Failed to fetch odds from {sportsbook}",
                    error=str(e),
                    sportsbook=sportsbook,
                    sport=sport.value,
                    request_id=ctx["request_id"],
                )
                raise

    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is open"""
        if not self.circuit_breaker["is_open"]:
            return False

        if self.circuit_breaker["last_failure"]:
            time_since_failure = time.time() - self.circuit_breaker["last_failure"]
            if time_since_failure > self.circuit_breaker["recovery_timeout"]:
                self.circuit_breaker["is_open"] = False
                self.circuit_breaker["failures"] = 0
                return False

        return True

    def _record_failure(self):
        """Record API failure for circuit breaker"""
        self.circuit_breaker["failures"] += 1
        self.circuit_breaker["last_failure"] = time.time()

        if self.circuit_breaker["failures"] >= self.circuit_breaker["failure_threshold"]:
            self.circuit_breaker["is_open"] = True
            logging.warning("Circuit breaker opened due to repeated failures")

    def _reset_circuit_breaker(self):
        """Reset circuit breaker on successful request"""
        self.circuit_breaker["failures"] = 0
        self.circuit_breaker["is_open"] = False

    async def _check_rate_limit(self, sportsbook: str):
        """Check and enforce rate limiting"""
        rate_key = f"rate_limit:{sportsbook}"
        current_requests = await self.redis.get(rate_key)

        config = self.api_configs[sportsbook]
        if current_requests and int(current_requests) >= config["rate_limit"]:
            raise Exception(f"Rate limit exceeded for {sportsbook}")

        # Increment request count
        pipeline = self.redis.pipeline()
        pipeline.incr(rate_key)
        pipeline.expire(rate_key, 60)  # Reset every minute
        await pipeline.execute()

    async def _fetch_odds_impl(
        self, sportsbook: str, sport: SportType, event_id: str | None, config: dict
    ) -> list[OddsData]:
        """Implementation-specific odds fetching"""

        # This would contain sportsbook-specific API calls
        # For demo purposes, returning mock data

        mock_odds = [
            OddsData(
                sportsbook=sportsbook,
                sport=sport,
                event_id=event_id or f"event_{uuid.uuid4().hex[:8]}",
                market_type=BetType.MONEYLINE,
                selection="Team A",
                odds=150,
                decimal_odds=2.5,
                implied_probability=0.4,
                timestamp=datetime.now(UTC).isoformat(),
                confidence=0.95,
                volume=1000,
            ),
            OddsData(
                sportsbook=sportsbook,
                sport=sport,
                event_id=event_id or f"event_{uuid.uuid4().hex[:8]}",
                market_type=BetType.MONEYLINE,
                selection="Team B",
                odds=-170,
                decimal_odds=1.588,
                implied_probability=0.63,
                timestamp=datetime.now(UTC).isoformat(),
                confidence=0.93,
                volume=1500,
            ),
        ]

        return mock_odds

    def _serialize_odds(self, odds: OddsData) -> dict:
        """Serialize odds data for caching"""
        return {
            "sportsbook": odds.sportsbook,
            "sport": odds.sport.value,
            "event_id": odds.event_id,
            "market_type": odds.market_type.value,
            "selection": odds.selection,
            "odds": odds.odds,
            "decimal_odds": odds.decimal_odds,
            "implied_probability": odds.implied_probability,
            "timestamp": odds.timestamp,
            "confidence": odds.confidence,
            "volume": odds.volume,
            "line_movement": odds.line_movement,
        }


class KellyCriterionCalculator:
    """Advanced Kelly criterion calculator with risk management"""

    def __init__(self, bankroll: float, max_kelly_fraction: float = 0.25):
        self.bankroll = bankroll
        self.max_kelly_fraction = max_kelly_fraction  # Risk management cap

    def calculate_kelly(
        self,
        odds: float,
        true_probability: float,
        confidence_interval: tuple[float, float] | None = None,
    ) -> KellyCalculation:
        """Calculate optimal Kelly bet sizing"""

        # Convert American odds to decimal
        decimal_odds = odds / 100 + 1 if odds > 0 else 100 / abs(odds) + 1

        # Calculate implied probability from odds
        implied_probability = 1 / decimal_odds

        # Calculate edge
        edge = true_probability - implied_probability

        # Kelly formula: f = (bp - q) / b
        # where b = decimal odds - 1, p = true probability, q = 1 - p
        b = decimal_odds - 1
        p = true_probability
        q = 1 - p

        kelly_fraction = (b * p - q) / b

        # Apply risk management cap
        capped_kelly = min(kelly_fraction, self.max_kelly_fraction)
        if capped_kelly < 0:
            capped_kelly = 0  # Never bet negative Kelly

        # Calculate recommended bet amount
        recommended_bet = self.bankroll * capped_kelly
        bankroll_percentage = capped_kelly * 100

        # Calculate expected value
        expected_value = recommended_bet * edge

        # Risk assessment
        risk_rating = self._assess_risk(capped_kelly, edge, confidence_interval)

        return KellyCalculation(
            bet_id=str(uuid.uuid4()),
            selection="",  # To be filled by caller
            sportsbook_odds=odds,
            true_probability=true_probability,
            implied_probability=implied_probability,
            edge=edge * 100,  # Convert to percentage
            kelly_fraction=capped_kelly,
            recommended_bet=recommended_bet,
            bankroll_percentage=bankroll_percentage,
            confidence_interval=confidence_interval or (edge - 0.05, edge + 0.05),
            risk_rating=risk_rating,
            expected_value=expected_value,
        )

    def _assess_risk(
        self,
        kelly_fraction: float,
        edge: float,
        confidence_interval: tuple[float, float] | None,
    ) -> str:
        """Assess risk level of the bet"""

        if kelly_fraction <= 0.01:  # 1% or less
            return "LOW"
        if kelly_fraction <= 0.05:  # 5% or less
            return "MEDIUM"
        if kelly_fraction <= 0.15:  # 15% or less
            return "HIGH"
        return "EXTREME"


class OpenAIAnalyticsEngine:
    """OpenAI GPT-5 integration for betting analytics with fallback routing"""

    def __init__(self, api_key: str, observability: ObservabilityManager):
        self.observability = observability
        self.client = AsyncOpenAI(api_key=api_key)

        # Model configuration with fallbacks
        self.model_config = {
            "primary": "gpt-5-turbo",
            "fallbacks": ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
            "max_tokens": 2000,
            "temperature": 0.1,  # Low temperature for analytical tasks
            "timeout": 30,
        }

        # Rate limiting
        self.rate_limits = {
            "requests_per_minute": 100,
            "tokens_per_minute": 50000,
            "current_requests": 0,
            "current_tokens": 0,
            "reset_time": time.time() + 60,
        }

    async def analyze_parlay_with_llm(
        self, parlay_legs: list[ParlayLeg], odds_data: dict[str, list[OddsData]]
    ) -> dict[str, Any]:
        """Use LLM to analyze parlay correlations and provide insights"""

        async with tracked_operation(
            self.observability,
            "llm_parlay_analysis",
            model=self.model_config["primary"],
            leg_count=len(parlay_legs),
        ) as ctx:
            try:
                # Check rate limits
                await self._check_rate_limits()

                # Prepare structured prompt
                analysis_prompt = self._build_analysis_prompt(parlay_legs, odds_data)

                # Try primary model first, then fallbacks
                for model in [self.model_config["primary"]] + self.model_config["fallbacks"]:
                    try:
                        response = await self._call_openai_api(model, analysis_prompt)

                        # Parse structured response
                        analysis_result = self._parse_llm_response(response)

                        await self.observability.metrics.counter(
                            "llm_analysis_success",
                            labels={"model": model, "request_type": "parlay_analysis"},
                        )

                        return analysis_result

                    except Exception as e:
                        await self.observability.logger.warning(
                            f"Model {model} failed, trying fallback",
                            error=str(e),
                            model=model,
                            request_id=ctx["request_id"],
                        )
                        continue

                raise Exception("All LLM models failed")

            except Exception as e:
                await self.observability.logger.error(
                    "LLM parlay analysis failed",
                    error=str(e),
                    request_id=ctx["request_id"],
                )

                # Return fallback analysis
                return self._fallback_analysis(parlay_legs)

    def _build_analysis_prompt(
        self, parlay_legs: list[ParlayLeg], odds_data: dict[str, list[OddsData]]
    ) -> str:
        """Build structured prompt for LLM analysis"""

        prompt = """
        Analyze this sports betting parlay for correlations, value, and risk factors.

        PARLAY LEGS:
        """

        for i, leg in enumerate(parlay_legs, 1):
            prompt += f"""
        {i}. {leg.selection} ({leg.sport.value.upper()})
           - Market: {leg.market_type.value}
           - Odds: {leg.odds:+d}
           - Sportsbook: {leg.sportsbook}
           - Confidence: {leg.confidence:.2f}
        """

        prompt += """

        ANALYSIS REQUIREMENTS:
        1. Correlation Risk (0-1 scale): How correlated are these outcomes?
        2. Value Assessment: Are any legs offering good value?
        3. Risk Factors: What could cause this parlay to lose?
        4. Win Probability: Estimated true probability of all legs hitting
        5. Recommendation: BET, PASS, REDUCE_STAKE, or SPLIT

        Respond in JSON format:
        {
          "correlation_risk": 0.0-1.0,
          "win_probability": 0.0-1.0,
          "value_legs": ["leg descriptions with value"],
          "risk_factors": ["key risk factors"],
          "recommendation": "BET|PASS|REDUCE_STAKE|SPLIT",
          "confidence_score": 0.0-1.0,
          "reasoning": "brief explanation"
        }
        """

        return prompt

    async def _call_openai_api(self, model: str, prompt: str) -> str:
        """Call OpenAI API with error handling"""

        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert sports betting analyst specializing in expected value and risk assessment.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=self.model_config["max_tokens"],
            temperature=self.model_config["temperature"],
            timeout=self.model_config["timeout"],
        )

        # Update token usage
        self.rate_limits["current_tokens"] += response.usage.total_tokens

        return response.choices[0].message.content

    def _parse_llm_response(self, response: str) -> dict[str, Any]:
        """Parse and validate LLM JSON response"""

        try:
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[json_start:json_end]
            analysis = json.loads(json_str)

            # Validate required fields
            required_fields = [
                "correlation_risk",
                "win_probability",
                "recommendation",
                "confidence_score",
            ]
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field: {field}")

            return analysis

        except Exception as e:
            logging.error(f"Failed to parse LLM response: {e}")
            raise

    def _fallback_analysis(self, parlay_legs: list[ParlayLeg]) -> dict[str, Any]:
        """Provide fallback analysis when LLM fails"""

        # Simple heuristic-based analysis
        correlation_risk = min(0.8, len(parlay_legs) * 0.15)  # Higher correlation with more legs
        win_probability = 0.5 ** len(parlay_legs)  # Assume 50% per leg for fallback

        return {
            "correlation_risk": correlation_risk,
            "win_probability": win_probability,
            "value_legs": [],
            "risk_factors": ["LLM analysis unavailable - using heuristics"],
            "recommendation": "PASS",  # Conservative fallback
            "confidence_score": 0.3,  # Low confidence without LLM
            "reasoning": "Fallback analysis due to LLM unavailability",
        }

    async def _check_rate_limits(self):
        """Check and enforce rate limits"""

        current_time = time.time()

        # Reset counters if minute has passed
        if current_time > self.rate_limits["reset_time"]:
            self.rate_limits["current_requests"] = 0
            self.rate_limits["current_tokens"] = 0
            self.rate_limits["reset_time"] = current_time + 60

        # Check limits
        if self.rate_limits["current_requests"] >= self.rate_limits["requests_per_minute"]:
            raise Exception("Request rate limit exceeded")

        if self.rate_limits["current_tokens"] >= self.rate_limits["tokens_per_minute"]:
            raise Exception("Token rate limit exceeded")

        # Increment request count
        self.rate_limits["current_requests"] += 1


class ParlayAnalyzer:
    """Main parlay analysis engine combining all components"""

    def __init__(
        self,
        bankroll: float,
        openai_api_key: str,
        redis_url: str = "redis://localhost:6379",
    ):
        self.observability = ObservabilityManager("parlay_analyzer")
        self.redis = None  # Will be initialized in setup
        self.sportsbook_api = None
        self.kelly_calculator = KellyCriterionCalculator(bankroll)
        self.llm_engine = OpenAIAnalyticsEngine(openai_api_key, self.observability)

        # Analysis configuration
        self.config = {
            "min_edge_threshold": 0.02,  # 2% minimum edge
            "max_correlation_risk": 0.7,  # Maximum acceptable correlation
            "confidence_threshold": 0.7,  # Minimum confidence for recommendations
            "responsible_gaming": {
                "max_daily_bets": 10,
                "max_daily_risk": 0.2,  # 20% of bankroll per day
                "cooling_period_hours": 4,
            },
        }

    async def setup(self, redis_url: str = "redis://localhost:6379"):
        """Initialize async components"""

        try:
            self.redis = await aioredis.from_url(redis_url)
            self.sportsbook_api = SportsBookAPI(self.observability, self.redis)

            await self.observability.logger.info("Parlay analyzer initialized successfully")

        except Exception as e:
            await self.observability.logger.error(f"Failed to initialize parlay analyzer: {e}")
            raise

    async def analyze_parlay(self, parlay_legs: list[ParlayLeg], stake: float) -> ParlayAnalysis:
        """Comprehensive parlay analysis with Kelly criterion and LLM insights"""

        async with tracked_operation(
            self.observability,
            "analyze_parlay",
            leg_count=len(parlay_legs),
            stake=stake,
        ) as ctx:
            parlay_id = str(uuid.uuid4())

            # Step 1: Fetch current odds from multiple sportsbooks
            odds_data = await self._fetch_odds_for_legs(parlay_legs)

            # Step 2: Calculate combined odds and probabilities
            combined_odds, combined_probability = self._calculate_combined_odds(parlay_legs)

            # Step 3: Get LLM analysis for correlations and insights
            llm_analysis = await self.llm_engine.analyze_parlay_with_llm(parlay_legs, odds_data)

            # Step 4: Apply Kelly criterion
            kelly_calc = self.kelly_calculator.calculate_kelly(
                combined_odds, llm_analysis["win_probability"]
            )
            kelly_calc.bet_id = parlay_id
            kelly_calc.selection = f"Parlay ({len(parlay_legs)} legs)"

            # Step 5: Risk assessment
            risk_rating = self._assess_overall_risk(
                kelly_calc.risk_rating,
                llm_analysis["correlation_risk"],
                len(parlay_legs),
            )

            # Step 6: Generate recommendation
            recommendation = self._generate_recommendation(
                kelly_calc, llm_analysis, stake, risk_rating
            )

            # Step 7: Responsible gaming checks
            await self._responsible_gaming_check(stake, risk_rating)

            # Create comprehensive analysis
            analysis = ParlayAnalysis(
                parlay_id=parlay_id,
                legs=parlay_legs,
                stake=stake,
                combined_american_odds=combined_odds,
                combined_decimal_odds=self._american_to_decimal(combined_odds),
                total_implied_probability=combined_probability,
                kelly_calculation=kelly_calc,
                expected_value=kelly_calc.expected_value,
                win_probability=llm_analysis["win_probability"],
                edge=kelly_calc.edge,
                risk_rating=risk_rating,
                correlation_risk=llm_analysis["correlation_risk"],
                bankroll_impact=stake / self.kelly_calculator.bankroll * 100,
                recommended_action=recommendation,
                optimal_stake=(kelly_calc.recommended_bet if recommendation == "BET" else None),
                confidence_score=llm_analysis["confidence_score"],
            )

            # Log analysis for audit trail
            await self._log_analysis_audit(analysis, llm_analysis, ctx["request_id"])

            return analysis

    async def _fetch_odds_for_legs(self, parlay_legs: list[ParlayLeg]) -> dict[str, list[OddsData]]:
        """Fetch odds from multiple sportsbooks for all parlay legs"""

        odds_data = {}

        # Group legs by sport for efficient fetching
        legs_by_sport = {}
        for leg in parlay_legs:
            if leg.sport not in legs_by_sport:
                legs_by_sport[leg.sport] = []
            legs_by_sport[leg.sport].append(leg)

        # Fetch odds for each sport from multiple sportsbooks
        sportsbooks = ["draftkings", "fanduel", "caesars"]

        for sport, _legs in legs_by_sport.items():
            odds_data[sport.value] = []

            for sportsbook in sportsbooks:
                try:
                    odds = await self.sportsbook_api.fetch_odds(sportsbook, sport)
                    odds_data[sport.value].extend(odds)
                except Exception as e:
                    await self.observability.logger.warning(
                        f"Failed to fetch odds from {sportsbook} for {sport.value}",
                        error=str(e),
                    )

        return odds_data

    def _calculate_combined_odds(self, parlay_legs: list[ParlayLeg]) -> tuple[float, float]:
        """Calculate combined American odds and implied probability"""

        total_decimal_odds = 1.0

        for leg in parlay_legs:
            decimal_odds = self._american_to_decimal(leg.odds)
            total_decimal_odds *= decimal_odds

        # Convert back to American odds
        if total_decimal_odds >= 2.0:
            american_odds = (total_decimal_odds - 1) * 100
        else:
            american_odds = -100 / (total_decimal_odds - 1)

        # Calculate implied probability
        implied_probability = 1 / total_decimal_odds

        return american_odds, implied_probability

    def _american_to_decimal(self, american_odds: float) -> float:
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        return (100 / abs(american_odds)) + 1

    def _assess_overall_risk(self, kelly_risk: str, correlation_risk: float, leg_count: int) -> str:
        """Assess overall risk combining multiple factors"""

        # Risk factors scoring
        kelly_scores = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "EXTREME": 4}
        kelly_score = kelly_scores.get(kelly_risk, 4)

        # Correlation risk (0-1 scale to 1-4 scale)
        correlation_score = min(4, max(1, correlation_risk * 4))

        # Leg count risk (more legs = higher risk)
        leg_score = min(4, max(1, leg_count / 3))

        # Combined score
        total_score = (kelly_score + correlation_score + leg_score) / 3

        if total_score <= 1.5:
            return "LOW"
        if total_score <= 2.5:
            return "MEDIUM"
        if total_score <= 3.5:
            return "HIGH"
        return "EXTREME"

    def _generate_recommendation(
        self,
        kelly_calc: KellyCalculation,
        llm_analysis: dict[str, Any],
        stake: float,
        risk_rating: str,
    ) -> str:
        """Generate betting recommendation"""

        # No edge = no bet
        if kelly_calc.edge <= self.config["min_edge_threshold"] * 100:
            return "PASS"

        # High correlation risk
        if llm_analysis["correlation_risk"] > self.config["max_correlation_risk"]:
            return "PASS"

        # Low confidence
        if llm_analysis["confidence_score"] < self.config["confidence_threshold"]:
            return "PASS"

        # Extreme risk
        if risk_rating == "EXTREME":
            return "PASS"

        # Stake too high compared to Kelly recommendation
        if stake > kelly_calc.recommended_bet * 2:
            return "REDUCE_STAKE"

        # Multiple correlated legs might be better as singles
        if len(kelly_calc.selection) > 4 and llm_analysis["correlation_risk"] > 0.5:
            return "SPLIT"

        return "BET"

    async def _responsible_gaming_check(self, stake: float, risk_rating: str):
        """Enforce responsible gaming limits"""

        # Check daily bet count
        daily_bets_key = f"daily_bets:{datetime.now().strftime('%Y-%m-%d')}"
        daily_bet_count = await self.redis.get(daily_bets_key) or 0

        if int(daily_bet_count) >= self.config["responsible_gaming"]["max_daily_bets"]:
            raise Exception("Daily bet limit exceeded - responsible gaming protection")

        # Check daily risk exposure
        daily_risk_key = f"daily_risk:{datetime.now().strftime('%Y-%m-%d')}"
        daily_risk = await self.redis.get(daily_risk_key) or 0

        max_daily_risk = (
            self.kelly_calculator.bankroll * self.config["responsible_gaming"]["max_daily_risk"]
        )

        if float(daily_risk) + stake > max_daily_risk:
            raise Exception("Daily risk limit exceeded - responsible gaming protection")

        # Update counters
        pipeline = self.redis.pipeline()
        pipeline.incr(daily_bets_key)
        pipeline.expire(daily_bets_key, 86400)  # 24 hours
        pipeline.incrbyfloat(daily_risk_key, stake)
        pipeline.expire(daily_risk_key, 86400)
        await pipeline.execute()

    async def _log_analysis_audit(
        self, analysis: ParlayAnalysis, llm_analysis: dict[str, Any], request_id: str
    ):
        """Log comprehensive audit trail"""

        audit_data = {
            "request_id": request_id,
            "parlay_id": analysis.parlay_id,
            "timestamp": analysis.created_at,
            "legs": [leg.dict() for leg in analysis.legs],
            "stake": analysis.stake,
            "analysis_results": {
                "expected_value": analysis.expected_value,
                "win_probability": analysis.win_probability,
                "edge": analysis.edge,
                "kelly_fraction": (
                    analysis.kelly_calculation.kelly_fraction
                    if analysis.kelly_calculation
                    else None
                ),
                "risk_rating": analysis.risk_rating,
                "recommendation": analysis.recommended_action,
                "confidence_score": analysis.confidence_score,
            },
            "llm_analysis": llm_analysis,
            "responsible_gaming": {
                "bankroll_impact": analysis.bankroll_impact,
                "daily_limits_checked": True,
            },
        }

        # Store in structured logs
        await self.observability.logger.info(
            "Parlay analysis completed",
            event_type="parlay_analysis",
            audit_data=audit_data,
            request_id=request_id,
        )

        # Store in Redis for retrieval
        audit_key = f"audit:parlay:{analysis.parlay_id}"
        await self.redis.setex(audit_key, 86400 * 30, json.dumps(audit_data))  # 30-day retention


async def main():
    """Demonstration of the sports betting analytics platform"""

    setup_utf8_logging()
    logging.info("🎯 Starting EQ12 Sports Betting Analytics Platform")

    # Configuration
    bankroll = 10000.0  # $10,000 bankroll
    openai_api_key = "your-openai-api-key-here"

    # Initialize analyzer
    analyzer = ParlayAnalyzer(bankroll, openai_api_key)
    await analyzer.setup()

    # Example parlay
    parlay_legs = [
        ParlayLeg(
            selection="Kansas City Chiefs ML",
            odds=-150,
            market_type=BetType.MONEYLINE,
            sport=SportType.NFL,
            event_id="nfl_kc_vs_den_20251005",
            sportsbook="draftkings",
            confidence=0.95,
        ),
        ParlayLeg(
            selection="Over 47.5 points",
            odds=-110,
            market_type=BetType.TOTAL,
            sport=SportType.NFL,
            event_id="nfl_kc_vs_den_20251005",
            sportsbook="fanduel",
            confidence=0.88,
        ),
        ParlayLeg(
            selection="Travis Kelce Over 5.5 receptions",
            odds=120,
            market_type=BetType.PROP,
            sport=SportType.NFL,
            event_id="nfl_kc_vs_den_20251005",
            sportsbook="caesars",
            confidence=0.82,
        ),
    ]

    # Analyze parlay
    try:
        analysis = await analyzer.analyze_parlay(parlay_legs, stake=250.0)

        print("\n🏈 EQ12 PARLAY ANALYSIS RESULTS")
        print("=" * 50)
        print(f"Parlay ID: {analysis.parlay_id}")
        print(f"Legs: {len(analysis.legs)}")
        print(f"Stake: ${analysis.stake:.2f}")
        print(f"Combined Odds: {analysis.combined_american_odds:+.0f}")
        print(f"Win Probability: {analysis.win_probability:.1%}")
        print(f"Expected Value: ${analysis.expected_value:.2f}")
        print(f"Edge: {analysis.edge:.2f}%")
        print(f"Risk Rating: {analysis.risk_rating}")
        print(f"Correlation Risk: {analysis.correlation_risk:.1%}")
        print(f"Recommendation: {analysis.recommended_action}")
        print(f"Confidence: {analysis.confidence_score:.1%}")

        if analysis.kelly_calculation:
            kelly = analysis.kelly_calculation
            print("\n📊 KELLY CRITERION ANALYSIS")
            print(f"Optimal Fraction: {kelly.kelly_fraction:.3f}")
            print(f"Recommended Bet: ${kelly.recommended_bet:.2f}")
            print(f"Bankroll %: {kelly.bankroll_percentage:.2f}%")

        if analysis.optimal_stake:
            print(f"\n💡 OPTIMAL STAKE: ${analysis.optimal_stake:.2f}")

        print("\n✅ Analysis complete - check logs for full audit trail")

    except Exception as e:
        logging.error(f"Analysis failed: {e}")

    finally:
        # Cleanup
        if analyzer.redis:
            await analyzer.redis.close()


if __name__ == "__main__":
    asyncio.run(main())
