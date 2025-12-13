# eq12_comprehensive_llm_automation.py
"""
EQ12 Comprehensive LLM-Powered Sports Betting Automation System
Integrates OpenAI GPT-5 with advanced circuit breakers, fallback mechanisms,
parlay optimization using Kelly Criterion and Expected Value calculations
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from functools import wraps
from typing import Any

import aiohttp
import numpy as np
import redis.asyncio as redis
from openai import AsyncOpenAI

# Configure logging with UTF-8 support
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/llm_automation.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    OFFLINE = "offline"


class CircuitBreakerState(Enum):
    """Circuit breaker state enumeration"""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class BettingOdds:
    """Comprehensive betting odds structure"""

    sportsbook: str
    sport: str
    event_id: str
    market_type: str  # moneyline, spread, total, etc.
    selection: str
    american_odds: int
    decimal_odds: float
    implied_probability: float
    timestamp: datetime
    confidence: float = 0.95

    @classmethod
    def from_american_odds(cls, american_odds: int, **kwargs) -> "BettingOdds":
        """Create BettingOdds from American odds format"""
        decimal = cls.american_to_decimal(american_odds)
        implied = 1 / decimal

        return cls(
            american_odds=american_odds,
            decimal_odds=decimal,
            implied_probability=implied,
            **kwargs,
        )

    @staticmethod
    def american_to_decimal(american_odds: int) -> float:
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        return (100 / abs(american_odds)) + 1


@dataclass
class ParlayLeg:
    """Individual parlay leg"""

    selection: str
    odds: BettingOdds
    confidence: float
    expected_probability: float
    edge: float  # Expected edge over implied probability


@dataclass
class KellyCalculation:
    """Kelly Criterion calculation result"""

    kelly_fraction: float
    edge: float
    implied_probability: float
    true_probability: float
    recommended_bet: float
    max_bet_fraction: float = 0.25  # Maximum 25% of bankroll


@dataclass
class ExpectedValueAnalysis:
    """Expected Value analysis result"""

    ev_per_dollar: float
    ev_total: float
    true_probability: float
    payout_odds: float
    recommendation: str  # BET, PASS, REDUCE
    confidence: float


@dataclass
class ParlayOptimization:
    """Comprehensive parlay optimization result"""

    legs: list[ParlayLeg]
    combined_odds: float
    true_probability: float
    expected_value: ExpectedValueAnalysis
    kelly_sizing: KellyCalculation
    risk_assessment: dict[str, Any]
    correlation_factors: dict[str, float]
    recommendation: str
    confidence_score: float


class CircuitBreaker:
    """Advanced circuit breaker with exponential backoff"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                else:
                    raise Exception(f"Circuit breaker OPEN for {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e

        return wrapper

    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and time.time() - self.last_failure_time >= self.recovery_timeout
        )

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN


class RateLimiter:
    """Token bucket rate limiter for API calls"""

    def __init__(self, max_calls: int = 100, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = asyncio.Lock()

    async def acquire(self) -> bool:
        async with self.lock:
            now = time.time()
            # Remove calls outside the time window
            self.calls = [
                call_time for call_time in self.calls if now - call_time < self.time_window
            ]

            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True

            return False

    async def wait_if_needed(self):
        while not await self.acquire():
            await asyncio.sleep(1)


class OpenAILLMService:
    """Advanced OpenAI service with fallback and circuit breaker"""

    def __init__(self, api_key: str, redis_client=None):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key)
        self.redis = redis_client

        # Circuit breakers for different models
        self.gpt5_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=300)
        self.gpt4_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=180)

        # Rate limiters
        self.gpt5_limiter = RateLimiter(max_calls=50, time_window=60)
        self.gpt4_limiter = RateLimiter(max_calls=100, time_window=60)

        # Model fallback hierarchy
        self.model_hierarchy = [
            ("gpt-5-turbo", self.gpt5_breaker, self.gpt5_limiter),
            ("gpt-4-turbo", self.gpt4_breaker, self.gpt4_limiter),
            ("gpt-4", self.gpt4_breaker, self.gpt4_limiter),
        ]

    async def chat_completion(self, messages: list[dict], **kwargs) -> str | None:
        """Attempt chat completion with fallback models"""

        for model, breaker, limiter in self.model_hierarchy:
            try:
                await limiter.wait_if_needed()

                @breaker
                async def _make_request():
                    response = await self.client.chat.completions.create(
                        model=model, messages=messages, **kwargs
                    )
                    return response.choices[0].message.content

                result = await _make_request()
                logger.info(f"Successful completion with {model}")
                return result

            except Exception as e:
                logger.warning(f"Model {model} failed: {e}")
                continue

        logger.error("All OpenAI models failed, using fallback")
        return self._fallback_response(messages)

    def _fallback_response(self, messages: list[dict]) -> str:
        """Fallback response when all models fail"""
        return json.dumps(
            {
                "status": "fallback",
                "recommendation": "PASS",
                "confidence": 0.1,
                "message": "AI analysis unavailable, using conservative recommendation",
            }
        )


class KellyCriterionCalculator:
    """Advanced Kelly Criterion calculator for optimal bet sizing"""

    def __init__(self, bankroll: float, max_fraction: float = 0.25):
        self.bankroll = bankroll
        self.max_fraction = max_fraction

    def calculate_kelly(self, odds: BettingOdds, true_probability: float) -> KellyCalculation:
        """Calculate optimal Kelly fraction"""

        # Convert to decimal odds
        decimal_odds = odds.decimal_odds
        implied_prob = odds.implied_probability

        # Calculate edge
        edge = true_probability - implied_prob

        # Kelly formula: f = (bp - q) / b
        # where b = odds-1, p = true probability, q = 1-p
        b = decimal_odds - 1  # Net odds
        p = true_probability
        q = 1 - p

        if edge <= 0:
            # No edge, don't bet
            kelly_fraction = 0
        else:
            kelly_fraction = (b * p - q) / b

        # Apply maximum fraction limit
        kelly_fraction = min(kelly_fraction, self.max_fraction)
        kelly_fraction = max(kelly_fraction, 0)  # Never negative

        recommended_bet = kelly_fraction * self.bankroll

        return KellyCalculation(
            kelly_fraction=kelly_fraction,
            edge=edge * 100,  # Convert to percentage
            implied_probability=implied_prob,
            true_probability=true_probability,
            recommended_bet=recommended_bet,
            max_bet_fraction=self.max_fraction,
        )


class ExpectedValueCalculator:
    """Calculate Expected Value for betting opportunities"""

    @staticmethod
    def calculate_ev(
        odds: BettingOdds, true_probability: float, stake: float = 1.0
    ) -> ExpectedValueAnalysis:
        """Calculate expected value of a bet"""

        decimal_odds = odds.decimal_odds
        payout = decimal_odds * stake  # Total return including stake
        profit = payout - stake  # Net profit

        # EV = (probability of win * profit) - (probability of loss * stake)
        prob_win = true_probability
        prob_loss = 1 - prob_win

        ev_total = (prob_win * profit) - (prob_loss * stake)
        ev_per_dollar = ev_total / stake

        # Generate recommendation
        if ev_per_dollar > 0.05:  # 5% positive EV
            recommendation = "BET"
            confidence = min(0.95, 0.5 + (ev_per_dollar * 5))
        elif ev_per_dollar > 0.02:  # Small positive EV
            recommendation = "SMALL_BET"
            confidence = 0.6
        elif ev_per_dollar > -0.02:  # Close to neutral
            recommendation = "PASS"
            confidence = 0.7
        else:  # Negative EV
            recommendation = "AVOID"
            confidence = 0.9

        return ExpectedValueAnalysis(
            ev_per_dollar=ev_per_dollar,
            ev_total=ev_total,
            true_probability=true_probability,
            payout_odds=decimal_odds,
            recommendation=recommendation,
            confidence=confidence,
        )


class ParlayOptimizer:
    """Advanced parlay optimization using EV and Kelly Criterion"""

    def __init__(self, bankroll: float, llm_service: OpenAILLMService):
        self.bankroll = bankroll
        self.llm_service = llm_service
        self.kelly_calc = KellyCriterionCalculator(bankroll)
        self.ev_calc = ExpectedValueCalculator()

    async def optimize_parlay(self, potential_legs: list[dict]) -> ParlayOptimization:
        """Optimize a parlay combination"""

        # Convert to ParlayLeg objects
        legs = []
        for leg_data in potential_legs:
            odds = BettingOdds.from_american_odds(**leg_data["odds"])

            # Use LLM to analyze true probability
            true_prob = await self._analyze_leg_probability(leg_data)
            edge = true_prob - odds.implied_probability

            leg = ParlayLeg(
                selection=leg_data["selection"],
                odds=odds,
                confidence=leg_data.get("confidence", 0.8),
                expected_probability=true_prob,
                edge=edge,
            )
            legs.append(leg)

        # Calculate combined odds and probabilities
        combined_decimal_odds = np.prod([leg.odds.decimal_odds for leg in legs])
        combined_true_prob = np.prod([leg.expected_probability for leg in legs])

        # Account for correlation (negative correlation reduces true probability)
        correlation_adjustment = await self._assess_correlations(legs)
        adjusted_true_prob = combined_true_prob * correlation_adjustment

        # Create combined odds object for calculations
        combined_odds = BettingOdds(
            sportsbook="combined",
            sport="parlay",
            event_id="parlay_" + str(int(time.time())),
            market_type="parlay",
            selection=f"{len(legs)}_leg_parlay",
            american_odds=int((combined_decimal_odds - 1) * 100),
            decimal_odds=combined_decimal_odds,
            implied_probability=1 / combined_decimal_odds,
            timestamp=datetime.now(UTC),
        )

        # Calculate EV and Kelly sizing
        ev_analysis = self.ev_calc.calculate_ev(combined_odds, adjusted_true_prob)
        kelly_sizing = self.kelly_calc.calculate_kelly(combined_odds, adjusted_true_prob)

        # Risk assessment
        risk_factors = await self._assess_risk_factors(legs, ev_analysis, kelly_sizing)

        # Generate final recommendation
        recommendation = self._generate_recommendation(ev_analysis, kelly_sizing, risk_factors)

        return ParlayOptimization(
            legs=legs,
            combined_odds=combined_decimal_odds,
            true_probability=adjusted_true_prob,
            expected_value=ev_analysis,
            kelly_sizing=kelly_sizing,
            risk_assessment=risk_factors,
            correlation_factors={"adjustment": correlation_adjustment},
            recommendation=recommendation,
            confidence_score=min([leg.confidence for leg in legs]),
        )

    async def _analyze_leg_probability(self, leg_data: dict) -> float:
        """Use LLM to analyze true probability of a leg"""

        prompt = f"""
        Analyze this sports betting opportunity and estimate the true probability:

        Selection: {leg_data["selection"]}
        Sport: {leg_data.get("sport", "Unknown")}
        Market: {leg_data.get("market_type", "Unknown")}
        Current Odds: {leg_data["odds"].get("american_odds")}

        Consider:
        1. Team/player form and statistics
        2. Injuries and lineup changes
        3. Weather conditions (if applicable)
        4. Historical matchup data
        5. Market sentiment and line movement

        Return ONLY a decimal probability between 0.01 and 0.99.
        """

        messages = [
            {
                "role": "system",
                "content": "You are an expert sports analyst. Provide only numerical probability estimates.",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            response = await self.llm_service.chat_completion(messages, max_tokens=50)
            # Extract probability from response
            prob_str = response.strip().replace("%", "")
            probability = float(prob_str)

            # Ensure valid range
            if probability > 1:
                probability = probability / 100  # Convert percentage

            return max(0.01, min(0.99, probability))

        except Exception as e:
            logger.warning(f"LLM probability analysis failed: {e}")
            # Fallback to implied probability with small adjustment
            implied = leg_data["odds"].get("implied_probability", 0.5)
            return max(0.01, min(0.99, implied * 0.95))  # Conservative adjustment

    async def _assess_correlations(self, legs: list[ParlayLeg]) -> float:
        """Assess correlation between parlay legs"""

        # Use LLM to analyze correlations
        leg_descriptions = [f"{leg.selection} ({leg.odds.sport})" for leg in legs]

        prompt = f"""
        Analyze the correlation between these betting selections:
        {chr(10).join(f"{i + 1}. {desc}" for i, desc in enumerate(leg_descriptions))}

        Consider:
        1. Same game correlations (positive or negative)
        2. Same team multiple bets
        3. Weather impact on multiple games
        4. League-wide trends

        Return a correlation adjustment factor between 0.7 and 1.0:
        - 1.0 = No correlation (independent events)
        - 0.9 = Slight negative correlation
        - 0.8 = Moderate negative correlation
        - 0.7 = Strong negative correlation

        Return ONLY the decimal number.
        """

        messages = [
            {
                "role": "system",
                "content": "You are a sports betting correlation expert.",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            response = await self.llm_service.chat_completion(messages, max_tokens=30)
            adjustment = float(response.strip())
            return max(0.7, min(1.0, adjustment))
        except Exception:
            return 0.85  # Conservative default

    async def _assess_risk_factors(
        self,
        legs: list[ParlayLeg],
        ev_analysis: ExpectedValueAnalysis,
        kelly_sizing: KellyCalculation,
    ) -> dict[str, Any]:
        """Comprehensive risk assessment"""

        risk_factors = {
            "leg_count": len(legs),
            "lowest_confidence": min([leg.confidence for leg in legs]),
            "negative_edges": sum(1 for leg in legs if leg.edge <= 0),
            "kelly_fraction": kelly_sizing.kelly_fraction,
            "expected_value": ev_analysis.ev_per_dollar,
            "risk_level": "LOW",
        }

        # Determine risk level
        if (
            len(legs) > 6
            or risk_factors["lowest_confidence"] < 0.6
            or risk_factors["negative_edges"] > 1
            or ev_analysis.ev_per_dollar < 0
        ):
            risk_factors["risk_level"] = "HIGH"
        elif (
            len(legs) > 4
            or risk_factors["lowest_confidence"] < 0.75
            or kelly_sizing.kelly_fraction < 0.02
        ):
            risk_factors["risk_level"] = "MEDIUM"

        return risk_factors

    def _generate_recommendation(
        self,
        ev_analysis: ExpectedValueAnalysis,
        kelly_sizing: KellyCalculation,
        risk_factors: dict[str, Any],
    ) -> str:
        """Generate final betting recommendation"""

        if risk_factors["risk_level"] == "HIGH":
            return "AVOID"
        if ev_analysis.ev_per_dollar < 0 or kelly_sizing.kelly_fraction < 0.01:
            return "PASS"
        if ev_analysis.ev_per_dollar > 0.1 and risk_factors["risk_level"] == "LOW":
            return "STRONG_BET"
        if ev_analysis.ev_per_dollar > 0.05:
            return "BET"
        return "SMALL_BET"


class OddsIngestionPipeline:
    """Rate-limit-safe odds ingestion from multiple sportsbooks"""

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.session = None

        # Rate limiters for different sportsbooks
        self.rate_limiters = {
            "draftkings": RateLimiter(max_calls=60, time_window=60),
            "fanduel": RateLimiter(max_calls=50, time_window=60),
            "betmgm": RateLimiter(max_calls=40, time_window=60),
            "caesars": RateLimiter(max_calls=45, time_window=60),
        }

        # Circuit breakers
        self.circuit_breakers = {
            sportsbook: CircuitBreaker(failure_threshold=5, recovery_timeout=300)
            for sportsbook in self.rate_limiters
        }

    async def start(self):
        """Initialize the ingestion pipeline"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "EQ12-Odds-Ingestion/1.0"},
        )
        logger.info("Odds ingestion pipeline started")

    async def stop(self):
        """Clean shutdown of the pipeline"""
        if self.session:
            await self.session.close()
        logger.info("Odds ingestion pipeline stopped")

    async def ingest_odds(self, sportsbook: str, sport: str = "NFL") -> list[BettingOdds]:
        """Ingest odds from a specific sportsbook with rate limiting"""

        if sportsbook not in self.rate_limiters:
            raise ValueError(f"Unsupported sportsbook: {sportsbook}")

        rate_limiter = self.rate_limiters[sportsbook]
        circuit_breaker = self.circuit_breakers[sportsbook]

        await rate_limiter.wait_if_needed()

        @circuit_breaker
        async def _fetch_odds():
            # In production, this would call actual sportsbook APIs
            # For now, return mock data
            return self._generate_mock_odds(sportsbook, sport)

        try:
            odds_data = await _fetch_odds()

            # Cache in Redis if available
            if self.redis:
                cache_key = f"odds:{sportsbook}:{sport}:{int(time.time())}"
                await self.redis.setex(
                    cache_key,
                    300,  # 5 minute TTL
                    json.dumps([asdict(odds) for odds in odds_data], default=str),
                )

            logger.info(f"Successfully ingested {len(odds_data)} odds from {sportsbook}")
            return odds_data

        except Exception as e:
            logger.error(f"Failed to ingest odds from {sportsbook}: {e}")
            return []

    def _generate_mock_odds(self, sportsbook: str, sport: str) -> list[BettingOdds]:
        """Generate mock odds data for testing"""

        mock_games = [
            {"home": "Chiefs", "away": "Broncos", "spread": -7.5},
            {"home": "Bills", "away": "Dolphins", "spread": -3.5},
            {"home": "49ers", "away": "Cowboys", "spread": -2.5},
        ]

        odds_list = []

        for game in mock_games:
            event_id = f"{sport.lower()}_{game['away']}_{game['home']}"

            # Moneylines
            home_ml = int(game["spread"] * -15)  # Rough conversion
            away_ml = int(abs(game["spread"]) * 12)

            odds_list.extend(
                [
                    BettingOdds.from_american_odds(
                        american_odds=home_ml,
                        sportsbook=sportsbook,
                        sport=sport,
                        event_id=event_id,
                        market_type="moneyline",
                        selection=f"{game['home']} ML",
                        timestamp=datetime.now(UTC),
                    ),
                    BettingOdds.from_american_odds(
                        american_odds=away_ml,
                        sportsbook=sportsbook,
                        sport=sport,
                        event_id=event_id,
                        market_type="moneyline",
                        selection=f"{game['away']} ML",
                        timestamp=datetime.now(UTC),
                    ),
                ]
            )

        return odds_list


class EQ12LLMAutomationEngine:
    """Main automation engine coordinating all services"""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.redis = None
        self.llm_service = None
        self.odds_pipeline = None
        self.parlay_optimizer = None

        # Service status tracking
        self.service_status = {
            "llm": ServiceStatus.OFFLINE,
            "redis": ServiceStatus.OFFLINE,
            "odds_ingestion": ServiceStatus.OFFLINE,
            "parlay_optimizer": ServiceStatus.OFFLINE,
        }

    async def initialize(self):
        """Initialize all services"""
        try:
            # Initialize Redis
            if self.config.get("redis_url"):
                self.redis = redis.from_url(self.config["redis_url"])
                await self.redis.ping()
                self.service_status["redis"] = ServiceStatus.HEALTHY
                logger.info("Redis connection established")

            # Initialize LLM service
            if self.config.get("openai_api_key"):
                self.llm_service = OpenAILLMService(self.config["openai_api_key"], self.redis)
                self.service_status["llm"] = ServiceStatus.HEALTHY
                logger.info("OpenAI LLM service initialized")

            # Initialize odds ingestion
            self.odds_pipeline = OddsIngestionPipeline(self.redis)
            await self.odds_pipeline.start()
            self.service_status["odds_ingestion"] = ServiceStatus.HEALTHY

            # Initialize parlay optimizer
            if self.llm_service:
                bankroll = self.config.get("bankroll", 10000.0)
                self.parlay_optimizer = ParlayOptimizer(bankroll, self.llm_service)
                self.service_status["parlay_optimizer"] = ServiceStatus.HEALTHY

            logger.info("EQ12 LLM Automation Engine fully initialized")

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    async def shutdown(self):
        """Graceful shutdown"""
        if self.odds_pipeline:
            await self.odds_pipeline.stop()

        if self.redis:
            await self.redis.close()

        logger.info("EQ12 LLM Automation Engine shutdown complete")

    async def analyze_betting_opportunity(self, legs_data: list[dict]) -> dict[str, Any]:
        """Comprehensive betting opportunity analysis"""

        if not self.parlay_optimizer:
            return {"error": "Parlay optimizer not available", "status": "offline"}

        try:
            # Optimize parlay
            optimization = await self.parlay_optimizer.optimize_parlay(legs_data)

            # Generate comprehensive report
            report = {
                "timestamp": datetime.now(UTC).isoformat(),
                "analysis": {
                    "legs_count": len(optimization.legs),
                    "combined_odds": optimization.combined_odds,
                    "true_probability": optimization.true_probability,
                    "expected_value": asdict(optimization.expected_value),
                    "kelly_sizing": asdict(optimization.kelly_sizing),
                    "risk_assessment": optimization.risk_assessment,
                    "correlation_factors": optimization.correlation_factors,
                },
                "recommendation": {
                    "action": optimization.recommendation,
                    "confidence": optimization.confidence_score,
                    "suggested_stake": optimization.kelly_sizing.recommended_bet,
                    "max_stake": optimization.kelly_sizing.recommended_bet * 2,  # Upper limit
                },
                "service_status": dict(self.service_status),
            }

            # Cache result
            if self.redis:
                cache_key = f"analysis:{hashlib.md5(str(legs_data).encode()).hexdigest()}"
                await self.redis.setex(
                    cache_key,
                    1800,
                    json.dumps(report, default=str),  # 30 minute TTL
                )

            logger.info(f"Analysis complete: {optimization.recommendation}")
            return report

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def get_live_odds(
        self, sportsbooks: list[str] | None = None, sport: str = "NFL"
    ) -> dict[str, list[dict]]:
        """Get live odds from multiple sportsbooks"""

        if not sportsbooks:
            sportsbooks = ["draftkings", "fanduel", "betmgm"]

        results = {}

        for sportsbook in sportsbooks:
            try:
                odds = await self.odds_pipeline.ingest_odds(sportsbook, sport)
                results[sportsbook] = [asdict(odd) for odd in odds]
            except Exception as e:
                logger.error(f"Failed to get odds from {sportsbook}: {e}")
                results[sportsbook] = {"error": str(e)}

        return results

    def get_service_status(self) -> dict[str, Any]:
        """Get comprehensive service status"""
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "services": dict(self.service_status),
            "overall_health": self._calculate_overall_health(),
        }

    def _calculate_overall_health(self) -> str:
        """Calculate overall system health"""
        healthy_count = sum(
            1 for status in self.service_status.values() if status == ServiceStatus.HEALTHY
        )
        total_services = len(self.service_status)

        if healthy_count == total_services:
            return "HEALTHY"
        if healthy_count >= total_services * 0.75:
            return "DEGRADED"
        return "FAILING"


# Example usage and testing
async def main():
    """Example usage of the LLM automation system"""

    config = {
        "openai_api_key": "your_openai_key_here",
        "redis_url": "redis://localhost:6379/0",
        "bankroll": 10000.0,
    }

    # Initialize engine
    engine = EQ12LLMAutomationEngine(config)

    try:
        await engine.initialize()

        # Example parlay analysis
        parlay_legs = [
            {
                "selection": "Chiefs ML",
                "sport": "NFL",
                "market_type": "moneyline",
                "odds": {"american_odds": -150},
                "confidence": 0.85,
            },
            {
                "selection": "Over 47.5",
                "sport": "NFL",
                "market_type": "total",
                "odds": {"american_odds": -110},
                "confidence": 0.80,
            },
        ]

        # Analyze the opportunity
        analysis = await engine.analyze_betting_opportunity(parlay_legs)
        print(json.dumps(analysis, indent=2, default=str))

        # Get live odds
        live_odds = await engine.get_live_odds(["draftkings", "fanduel"])
        print(json.dumps(live_odds, indent=2, default=str))

        # Check service status
        status = engine.get_service_status()
        print(json.dumps(status, indent=2))

    finally:
        await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
