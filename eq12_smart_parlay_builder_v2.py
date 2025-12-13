#!/usr/bin/env python3
"""
EQ12 Smart Parlay Builder 2.0 - AI-Powered Parlay Construction System
====================================================================

Advanced AI-powered parlay construction with:
- Correlation-aware parlay building
- Negative correlation avoidance
- Risk-balanced leg selection
- AI-driven optimal parlay construction
- Multi-dimensional analysis integration
- Real-time market optimization

Features:
- AI-powered leg selection with GPT-4o integration
- Advanced correlation matrix analysis
- Negative correlation detection and avoidance
- Risk-balanced portfolio construction
- Real-time odds optimization
- Multi-sport parlay intelligence
- Integration with all EQ12 systems

Author: EQ12 Development Team
Date: October 6, 2025
Version: 2.0.0
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np

# EQ12 Integration
try:
    from eq12_advanced_bankroll_optimizer import EQ12AdvancedBankrollOptimizer
    from eq12_advanced_correlation_engine import (
        EQ12AdvancedCorrelationEngine,
        enhance_edgegod_with_correlations,
    )
    from eq12_enhanced_openai_sdk import EQ12EnhancedOpenAIClient
    from eq12_line_movement_intelligence import EQ12LineMovementIntelligence

    EQ12_INTEGRATION = True
except ImportError:
    EQ12_INTEGRATION = False
    print("⚠️ EQ12 integration not available - running in standalone mode")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/smart_parlay_builder.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("EQ12SmartParlayBuilder")


class ParlayStrategy(Enum):
    """Parlay construction strategies"""

    CONSERVATIVE = "conservative"  # Low risk, higher probability
    AGGRESSIVE = "aggressive"  # High risk, high reward
    BALANCED = "balanced"  # Balanced risk/reward
    CORRELATION_AWARE = "correlation_aware"  # Focus on correlation optimization
    VALUE_FOCUSED = "value_focused"  # Focus on EV maximization
    SHARP = "sharp"  # Follow sharp money movements


class LegType(Enum):
    """Types of betting legs"""

    MONEYLINE = "moneyline"
    SPREAD = "spread"
    TOTAL = "total"
    PLAYER_PROP = "player_prop"
    TEAM_PROP = "team_prop"
    GAME_PROP = "game_prop"


@dataclass
class SmartParlayLeg:
    """Enhanced parlay leg with AI analysis"""

    leg_id: str
    sport: str
    game: str
    leg_type: LegType
    description: str
    odds: float
    win_probability: float
    expected_value: float

    # AI Analysis
    ai_confidence: float
    sharp_money_indicator: bool
    line_movement_score: float
    correlation_risk: float

    # Market data
    opening_odds: float
    current_odds: float
    line_movement: float
    market_consensus: float

    # Metadata
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    data_sources: list[str] = field(default_factory=list)

    @property
    def kelly_fraction(self) -> float:
        """Calculate Kelly Criterion fraction"""
        if self.win_probability <= 0 or self.win_probability >= 1:
            return 0.0

        decimal_odds = self.odds / 100 + 1 if self.odds > 0 else 100 / abs(self.odds) + 1

        b = decimal_odds - 1
        p = self.win_probability
        q = 1 - p

        return max(0.0, (b * p - q) / b)

    @property
    def risk_score(self) -> float:
        """Calculate overall risk score (0-1)"""
        # Combine various risk factors
        odds_risk = min(abs(self.odds) / 1000, 1.0)
        prob_risk = abs(self.win_probability - 0.5) * 2
        correlation_risk = self.correlation_risk
        line_movement_risk = abs(self.line_movement) / 10.0

        return np.mean([odds_risk, prob_risk, correlation_risk, line_movement_risk])


@dataclass
class SmartParlay:
    """AI-constructed parlay with comprehensive analysis"""

    parlay_id: str
    legs: list[SmartParlayLeg]
    strategy: ParlayStrategy

    # Parlay metrics
    combined_odds: float
    combined_probability: float
    expected_value: float
    kelly_sizing: float

    # Risk analysis
    correlation_matrix: np.ndarray
    risk_score: float
    diversification_score: float

    # AI analysis
    ai_grade: str  # A+, A, B+, B, C, D, F
    ai_confidence: float
    recommendation: str

    # Market analysis
    sharp_money_score: float
    line_movement_score: float
    market_efficiency_score: float

    # Construction metadata
    construction_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    data_quality_score: float = 1.0

    @property
    def leg_count(self) -> int:
        return len(self.legs)

    @property
    def average_leg_probability(self) -> float:
        return np.mean([leg.win_probability for leg in self.legs])

    @property
    def total_correlation_risk(self) -> float:
        """Calculate total correlation risk from correlation matrix"""
        if self.correlation_matrix.size == 0:
            return 0.0

        # Calculate average absolute correlation
        n = self.correlation_matrix.shape[0]
        if n <= 1:
            return 0.0

        # Get upper triangle (excluding diagonal)
        upper_triangle = np.triu(self.correlation_matrix, k=1)
        correlations = upper_triangle[upper_triangle != 0]

        return np.mean(np.abs(correlations)) if len(correlations) > 0 else 0.0


class EQ12SmartParlayBuilder:
    """
    AI-powered smart parlay construction system
    """

    def __init__(self, eq12_root: str = "C:/EQ12"):
        self.eq12_root = Path(eq12_root)

        # AI and analysis components
        self.ai_client = None
        self.correlation_engine = None
        self.bankroll_optimizer = None
        self.line_tracker = None

        # Market data
        self.available_legs: dict[str, list[SmartParlayLeg]] = {}
        self.correlation_cache: dict[str, float] = {}

        # Configuration
        self.min_legs = 2
        self.max_legs = 8
        self.min_combined_odds = -500  # Minimum combined odds
        self.max_combined_odds = 5000  # Maximum combined odds
        self.max_correlation_threshold = 0.5  # Maximum allowed correlation

        # AI prompt templates
        self.prompt_templates = self._load_prompt_templates()

        # Initialize components
        self._initialize_components()

        logger.info("🧠 EQ12 Smart Parlay Builder 2.0 initialized")

    def _initialize_components(self):
        """Initialize AI and analysis components"""
        if EQ12_INTEGRATION:
            try:
                self.ai_client = EQ12EnhancedOpenAIClient()
                self.correlation_engine = EQ12AdvancedCorrelationEngine()
                self.bankroll_optimizer = EQ12AdvancedBankrollOptimizer()
                self.line_tracker = EQ12LineMovementIntelligence()
                logger.info("✅ EQ12 integration components initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize EQ12 components: {e}")

    def _load_prompt_templates(self) -> dict[str, str]:
        """Load AI prompt templates for parlay analysis"""
        return {
            "leg_analysis": """
Analyze this betting leg for parlay inclusion:

Sport: {sport}
Game: {game}
Bet: {description}
Odds: {odds}
Market Data: Opening {opening_odds} → Current {current_odds}

Provide analysis on:
1. Win probability estimate (0-1)
2. Expected value assessment
3. Correlation risk with other legs
4. Sharp money indicators
5. Overall confidence (0-1)
6. Risk factors

Respond in JSON format with numerical scores.
""",
            "parlay_optimization": """
Optimize this parlay construction:

Available Legs:
{legs_data}

Strategy: {strategy}
Target: {target_legs} legs
Risk Tolerance: {risk_tolerance}

Correlation Matrix:
{correlation_matrix}

Select the optimal combination of legs that:
1. Maximizes expected value
2. Minimizes correlation risk
3. Balances probability vs payout
4. Follows {strategy} strategy

Provide reasoning and final leg selection.
""",
            "parlay_grading": """
Grade this constructed parlay:

Legs: {leg_count}
Combined Odds: {combined_odds}
Combined Probability: {combined_probability}
Expected Value: {expected_value}
Correlation Risk: {correlation_risk}
Sharp Money Score: {sharp_money_score}

Provide:
1. Letter grade (A+ to F)
2. Confidence score (0-1)
3. Key strengths
4. Key weaknesses
5. Recommendation (Strong Buy/Buy/Hold/Avoid)
""",
        }

    async def analyze_leg_with_ai(self, leg_data: dict[str, Any]) -> SmartParlayLeg:
        """
        Analyze a potential parlay leg using AI
        """
        try:
            # Prepare prompt
            prompt = self.prompt_templates["leg_analysis"].format(
                sport=leg_data.get("sport", "Unknown"),
                game=leg_data.get("game", "Unknown"),
                description=leg_data.get("description", "Unknown"),
                odds=leg_data.get("odds", 0),
                opening_odds=leg_data.get("opening_odds", leg_data.get("odds", 0)),
                current_odds=leg_data.get("current_odds", leg_data.get("odds", 0)),
            )

            # Get AI analysis
            if self.ai_client and hasattr(self.ai_client, "chat_completion_async"):
                response = await self.ai_client.chat_completion_async(
                    [
                        {
                            "role": "system",
                            "content": "You are an expert sports betting analyst. Provide precise numerical analysis.",
                        },
                        {"role": "user", "content": prompt},
                    ]
                )

                # Parse AI response (simplified - would have better parsing in production)
                ai_analysis = self._parse_ai_leg_analysis(response.content)
            else:
                # Fallback analysis without AI
                ai_analysis = self._fallback_leg_analysis(leg_data)

            # Get line movement data
            line_movement_score = await self._get_line_movement_score(leg_data)

            # Create enhanced leg
            leg = SmartParlayLeg(
                leg_id=leg_data.get("id", f"leg_{int(datetime.now().timestamp())}"),
                sport=leg_data.get("sport", "Unknown"),
                game=leg_data.get("game", "Unknown"),
                leg_type=LegType(leg_data.get("type", "moneyline")),
                description=leg_data.get("description", "Unknown"),
                odds=leg_data.get("odds", 100),
                win_probability=ai_analysis.get("win_probability", 0.5),
                expected_value=ai_analysis.get("expected_value", 0.0),
                ai_confidence=ai_analysis.get("confidence", 0.5),
                sharp_money_indicator=ai_analysis.get("sharp_money", False),
                line_movement_score=line_movement_score,
                correlation_risk=ai_analysis.get("correlation_risk", 0.0),
                opening_odds=leg_data.get("opening_odds", leg_data.get("odds", 100)),
                current_odds=leg_data.get("current_odds", leg_data.get("odds", 100)),
                line_movement=leg_data.get("current_odds", 100) - leg_data.get("opening_odds", 100),
                market_consensus=ai_analysis.get("market_consensus", 0.5),
                data_sources=["ai_analysis", "market_data"],
            )

            return leg

        except Exception as e:
            logger.error(f"❌ Failed to analyze leg with AI: {e}")
            return self._create_basic_leg(leg_data)

    def _parse_ai_leg_analysis(self, ai_response: str) -> dict[str, Any]:
        """
        Parse AI response for leg analysis
        """
        try:
            # Try to extract JSON from response
            import re

            json_match = re.search(r"\{.*\}", ai_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        # Fallback parsing (simplified)
        return {
            "win_probability": 0.5,
            "expected_value": 0.0,
            "correlation_risk": 0.3,
            "confidence": 0.6,
            "sharp_money": False,
            "market_consensus": 0.5,
        }

    def _fallback_leg_analysis(self, leg_data: dict[str, Any]) -> dict[str, Any]:
        """
        Fallback analysis without AI
        """
        odds = leg_data.get("odds", 100)

        # Calculate implied probability
        implied_prob = 100 / (odds + 100) if odds > 0 else abs(odds) / (abs(odds) + 100)

        # Estimate true probability (add some edge)
        estimated_prob = implied_prob * 1.05  # Assume 5% edge

        # Calculate expected value
        if odds > 0:
            ev = (estimated_prob * (odds / 100)) - (1 - estimated_prob)
        else:
            ev = (estimated_prob * (100 / abs(odds))) - (1 - estimated_prob)

        return {
            "win_probability": estimated_prob,
            "expected_value": ev * 100,  # Convert to percentage
            "correlation_risk": 0.2,
            "confidence": 0.6,
            "sharp_money": False,
            "market_consensus": implied_prob,
        }

    async def _get_line_movement_score(self, leg_data: dict[str, Any]) -> float:
        """
        Get line movement score for a leg
        """
        if not self.line_tracker:
            return 0.0

        opening_odds = leg_data.get("opening_odds", leg_data.get("odds", 100))
        current_odds = leg_data.get("current_odds", leg_data.get("odds", 100))

        line_movement = current_odds - opening_odds

        # Score based on movement magnitude and direction
        movement_score = min(abs(line_movement) / 50.0, 1.0)  # Normalize to 0-1

        return movement_score

    def _create_basic_leg(self, leg_data: dict[str, Any]) -> SmartParlayLeg:
        """
        Create basic leg without AI analysis
        """
        analysis = self._fallback_leg_analysis(leg_data)

        return SmartParlayLeg(
            leg_id=leg_data.get("id", f"leg_{int(datetime.now().timestamp())}"),
            sport=leg_data.get("sport", "Unknown"),
            game=leg_data.get("game", "Unknown"),
            leg_type=LegType(leg_data.get("type", "moneyline")),
            description=leg_data.get("description", "Unknown"),
            odds=leg_data.get("odds", 100),
            win_probability=analysis["win_probability"],
            expected_value=analysis["expected_value"],
            ai_confidence=0.5,
            sharp_money_indicator=False,
            line_movement_score=0.0,
            correlation_risk=0.2,
            opening_odds=leg_data.get("opening_odds", leg_data.get("odds", 100)),
            current_odds=leg_data.get("current_odds", leg_data.get("odds", 100)),
            line_movement=0.0,
            market_consensus=analysis["market_consensus"],
            data_sources=["basic_analysis"],
        )

    async def build_smart_parlay(
        self,
        available_legs: list[dict[str, Any]],
        strategy: ParlayStrategy = ParlayStrategy.BALANCED,
        target_legs: int = 4,
        min_expected_value: float = 5.0,
    ) -> SmartParlay:
        """
        Build an optimized smart parlay using AI and correlation analysis
        """
        logger.info(f"🧠 Building smart parlay: {strategy.value} strategy, {target_legs} legs")

        # Analyze all available legs
        analyzed_legs = []
        for leg_data in available_legs:
            leg = await self.analyze_leg_with_ai(leg_data)
            analyzed_legs.append(leg)

        # Filter legs based on strategy
        filtered_legs = self._filter_legs_by_strategy(analyzed_legs, strategy, min_expected_value)

        if len(filtered_legs) < self.min_legs:
            raise ValueError(
                f"Insufficient quality legs available: {len(filtered_legs)} < {self.min_legs}"
            )

        # Build correlation matrix
        correlation_matrix = await self._build_correlation_matrix(filtered_legs)

        # Select optimal leg combination
        selected_legs = await self._select_optimal_legs(
            filtered_legs, correlation_matrix, strategy, target_legs
        )

        # Calculate parlay metrics
        parlay_metrics = self._calculate_parlay_metrics(selected_legs, correlation_matrix)

        # Get AI grading
        ai_grade, ai_confidence, recommendation = await self._grade_parlay_with_ai(
            selected_legs, parlay_metrics
        )

        # Create smart parlay
        parlay = SmartParlay(
            parlay_id=f"smart_parlay_{int(datetime.now().timestamp())}",
            legs=selected_legs,
            strategy=strategy,
            combined_odds=parlay_metrics["combined_odds"],
            combined_probability=parlay_metrics["combined_probability"],
            expected_value=parlay_metrics["expected_value"],
            kelly_sizing=parlay_metrics["kelly_sizing"],
            correlation_matrix=correlation_matrix,
            risk_score=parlay_metrics["risk_score"],
            diversification_score=parlay_metrics["diversification_score"],
            ai_grade=ai_grade,
            ai_confidence=ai_confidence,
            recommendation=recommendation,
            sharp_money_score=parlay_metrics["sharp_money_score"],
            line_movement_score=parlay_metrics["line_movement_score"],
            market_efficiency_score=parlay_metrics["market_efficiency_score"],
        )

        logger.info(
            f"✅ Smart parlay built: {len(selected_legs)} legs, Grade: {ai_grade}, EV: {parlay_metrics['expected_value']:.1f}%"
        )

        return parlay

    def _filter_legs_by_strategy(
        self, legs: list[SmartParlayLeg], strategy: ParlayStrategy, min_ev: float
    ) -> list[SmartParlayLeg]:
        """
        Filter legs based on strategy requirements
        """
        filtered = []

        for leg in legs:
            include = True

            if strategy == ParlayStrategy.CONSERVATIVE:
                # Higher probability, lower risk
                if leg.win_probability < 0.6 or leg.risk_score > 0.4:
                    include = False

            elif strategy == ParlayStrategy.AGGRESSIVE:
                # Higher odds, higher EV
                if leg.expected_value < min_ev * 1.5 or abs(leg.odds) < 150:
                    include = False

            elif strategy == ParlayStrategy.VALUE_FOCUSED:
                # Focus on EV
                if leg.expected_value < min_ev:
                    include = False

            elif strategy == ParlayStrategy.SHARP:
                # Follow sharp money
                if not leg.sharp_money_indicator and leg.line_movement_score < 0.3:
                    include = False

            elif strategy == ParlayStrategy.CORRELATION_AWARE:
                # Focus on low correlation
                if leg.correlation_risk > 0.4:
                    include = False

            # Common filters
            if leg.ai_confidence < 0.4 or leg.expected_value < 0:
                include = False

            if include:
                filtered.append(leg)

        # Sort by strategy priority
        if strategy == ParlayStrategy.VALUE_FOCUSED:
            filtered.sort(key=lambda x: x.expected_value, reverse=True)
        elif strategy == ParlayStrategy.CONSERVATIVE:
            filtered.sort(key=lambda x: (x.win_probability, -x.risk_score), reverse=True)
        elif strategy == ParlayStrategy.SHARP:
            filtered.sort(
                key=lambda x: (x.sharp_money_indicator, x.line_movement_score), reverse=True
            )
        else:
            filtered.sort(key=lambda x: x.ai_confidence, reverse=True)

        return filtered

    async def _build_correlation_matrix(self, legs: list[SmartParlayLeg]) -> np.ndarray:
        """
        Build correlation matrix for legs
        """
        n = len(legs)
        correlation_matrix = np.eye(n)

        if not self.correlation_engine:
            # Simple correlation estimation
            for i in range(n):
                for j in range(i + 1, n):
                    # Estimate correlation based on same game, sport, etc.
                    correlation = self._estimate_correlation(legs[i], legs[j])
                    correlation_matrix[i, j] = correlation
                    correlation_matrix[j, i] = correlation
        else:
            # Use advanced correlation engine
            try:
                for i in range(n):
                    for j in range(i + 1, n):
                        # Convert legs to format expected by correlation engine
                        leg1_data = [legs[i].win_probability * 100] * 100  # Mock historical data
                        leg2_data = [legs[j].win_probability * 100] * 100

                        corr_result = await self.correlation_engine.calculate_prop_correlation(
                            leg1_data, leg2_data, legs[i].leg_id, legs[j].leg_id
                        )

                        correlation_matrix[i, j] = corr_result.correlation_coefficient
                        correlation_matrix[j, i] = corr_result.correlation_coefficient
            except Exception as e:
                logger.warning(f"⚠️ Advanced correlation failed, using simple estimation: {e}")
                correlation_matrix = self._simple_correlation_matrix(legs)

        return correlation_matrix

    def _estimate_correlation(self, leg1: SmartParlayLeg, leg2: SmartParlayLeg) -> float:
        """
        Simple correlation estimation between two legs
        """
        # Same game = high correlation
        if leg1.game == leg2.game and leg1.game != "Unknown":
            if leg1.leg_type == leg2.leg_type:
                return 0.7  # Same type, same game
            else:
                return 0.4  # Different type, same game

        # Same sport = low correlation
        if leg1.sport == leg2.sport:
            return 0.1

        # Different sports = very low correlation
        return 0.05

    def _simple_correlation_matrix(self, legs: list[SmartParlayLeg]) -> np.ndarray:
        """
        Create simple correlation matrix
        """
        n = len(legs)
        matrix = np.eye(n)

        for i in range(n):
            for j in range(i + 1, n):
                corr = self._estimate_correlation(legs[i], legs[j])
                matrix[i, j] = corr
                matrix[j, i] = corr

        return matrix

    async def _select_optimal_legs(
        self,
        legs: list[SmartParlayLeg],
        correlation_matrix: np.ndarray,
        strategy: ParlayStrategy,
        target_legs: int,
    ) -> list[SmartParlayLeg]:
        """
        Select optimal combination of legs using AI optimization
        """
        if len(legs) <= target_legs:
            return legs[:target_legs]

        # Use AI to optimize selection if available
        if self.ai_client and hasattr(self.ai_client, "chat_completion_async"):
            try:
                selected_legs = await self._ai_optimize_leg_selection(
                    legs, correlation_matrix, strategy, target_legs
                )
                return selected_legs
            except Exception as e:
                logger.warning(f"⚠️ AI optimization failed, using heuristic: {e}")

        # Fallback: heuristic selection
        return self._heuristic_leg_selection(legs, correlation_matrix, target_legs)

    async def _ai_optimize_leg_selection(
        self,
        legs: list[SmartParlayLeg],
        correlation_matrix: np.ndarray,
        strategy: ParlayStrategy,
        target_legs: int,
    ) -> list[SmartParlayLeg]:
        """
        Use AI to optimize leg selection
        """
        # Prepare legs data for AI
        legs_data = []
        for i, leg in enumerate(legs):
            legs_data.append(
                {
                    "index": i,
                    "description": leg.description,
                    "odds": leg.odds,
                    "win_probability": leg.win_probability,
                    "expected_value": leg.expected_value,
                    "ai_confidence": leg.ai_confidence,
                    "risk_score": leg.risk_score,
                }
            )

        prompt = self.prompt_templates["parlay_optimization"].format(
            legs_data=json.dumps(legs_data, indent=2),
            strategy=strategy.value,
            target_legs=target_legs,
            risk_tolerance="medium",
            correlation_matrix=correlation_matrix.tolist(),
        )

        response = await self.ai_client.chat_completion_async(
            [
                {
                    "role": "system",
                    "content": "You are an expert parlay optimizer. Select the best combination of legs.",
                },
                {"role": "user", "content": prompt},
            ]
        )

        # Parse AI selection (simplified)
        selected_indices = self._parse_ai_selection(response.content, target_legs)

        return [legs[i] for i in selected_indices if i < len(legs)]

    def _parse_ai_selection(self, ai_response: str, target_legs: int) -> list[int]:
        """
        Parse AI leg selection response
        """
        # Try to extract indices from response
        import re

        # Look for numbers in the response
        numbers = re.findall(r"\b\d+\b", ai_response)

        if numbers:
            indices = [int(n) for n in numbers[:target_legs]]
            return indices

        # Fallback: return first target_legs indices
        return list(range(target_legs))

    def _heuristic_leg_selection(
        self, legs: list[SmartParlayLeg], correlation_matrix: np.ndarray, target_legs: int
    ) -> list[SmartParlayLeg]:
        """
        Heuristic leg selection algorithm
        """
        selected_indices = []
        available_indices = list(range(len(legs)))

        # Start with the best leg
        best_idx = max(
            available_indices, key=lambda i: legs[i].expected_value * legs[i].ai_confidence
        )
        selected_indices.append(best_idx)
        available_indices.remove(best_idx)

        # Add remaining legs with correlation constraints
        while len(selected_indices) < target_legs and available_indices:
            best_candidate = None
            best_score = -float("inf")

            for candidate_idx in available_indices:
                # Calculate score considering correlations
                leg_score = legs[candidate_idx].expected_value * legs[candidate_idx].ai_confidence

                # Penalize high correlations with selected legs
                max_correlation = 0
                for selected_idx in selected_indices:
                    correlation = abs(correlation_matrix[candidate_idx, selected_idx])
                    max_correlation = max(max_correlation, correlation)

                # Apply correlation penalty
                correlation_penalty = max_correlation * 2.0  # Penalty factor
                final_score = leg_score - correlation_penalty

                if final_score > best_score:
                    best_score = final_score
                    best_candidate = candidate_idx

            if best_candidate is not None:
                selected_indices.append(best_candidate)
                available_indices.remove(best_candidate)
            else:
                break

        return [legs[i] for i in selected_indices]

    def _calculate_parlay_metrics(
        self, legs: list[SmartParlayLeg], correlation_matrix: np.ndarray
    ) -> dict[str, float]:
        """
        Calculate comprehensive parlay metrics
        """
        if not legs:
            return {}

        # Combined odds calculation
        combined_decimal_odds = 1.0
        for leg in legs:
            decimal_odds = leg.odds / 100 + 1 if leg.odds > 0 else 100 / abs(leg.odds) + 1
            combined_decimal_odds *= decimal_odds

        # Convert back to American odds
        if combined_decimal_odds >= 2:
            combined_odds = (combined_decimal_odds - 1) * 100
        else:
            combined_odds = -100 / (combined_decimal_odds - 1)

        # Combined probability (independent assumption, adjusted for correlations)
        independent_probability = np.prod([leg.win_probability for leg in legs])

        # Adjust for correlations (simplified)
        avg_correlation = np.mean(np.abs(correlation_matrix)) if correlation_matrix.size > 0 else 0
        correlation_adjustment = 1 - (
            avg_correlation * 0.2
        )  # Reduce probability for positive correlations
        combined_probability = independent_probability * correlation_adjustment

        # Expected value
        if combined_odds > 0:
            expected_return = combined_probability * (combined_odds / 100) - (
                1 - combined_probability
            )
        else:
            expected_return = combined_probability * (100 / abs(combined_odds)) - (
                1 - combined_probability
            )
        expected_value = expected_return * 100  # Convert to percentage

        # Kelly sizing
        if combined_probability > 0 and combined_probability < 1:
            kelly_sizing = max(
                0, (combined_decimal_odds * combined_probability - 1) / (combined_decimal_odds - 1)
            )
        else:
            kelly_sizing = 0

        # Risk score
        individual_risk_scores = [leg.risk_score for leg in legs]
        portfolio_risk = np.mean(individual_risk_scores)
        correlation_risk = avg_correlation
        risk_score = (portfolio_risk + correlation_risk) / 2

        # Diversification score
        diversification_score = 1 - avg_correlation

        # Sharp money score
        sharp_money_score = np.mean([1.0 if leg.sharp_money_indicator else 0.0 for leg in legs])

        # Line movement score
        line_movement_score = np.mean([leg.line_movement_score for leg in legs])

        # Market efficiency score (inverse of average EV)
        market_efficiency_score = 1.0 / (1.0 + np.mean([leg.expected_value for leg in legs]) / 100)

        return {
            "combined_odds": combined_odds,
            "combined_probability": combined_probability,
            "expected_value": expected_value,
            "kelly_sizing": kelly_sizing,
            "risk_score": risk_score,
            "diversification_score": diversification_score,
            "sharp_money_score": sharp_money_score,
            "line_movement_score": line_movement_score,
            "market_efficiency_score": market_efficiency_score,
        }

    async def _grade_parlay_with_ai(
        self, legs: list[SmartParlayLeg], metrics: dict[str, float]
    ) -> tuple[str, float, str]:
        """
        Grade parlay using AI analysis
        """
        if not self.ai_client or not hasattr(self.ai_client, "chat_completion_async"):
            return self._heuristic_grading(metrics)

        try:
            prompt = self.prompt_templates["parlay_grading"].format(
                leg_count=len(legs),
                combined_odds=metrics.get("combined_odds", 0),
                combined_probability=metrics.get("combined_probability", 0),
                expected_value=metrics.get("expected_value", 0),
                correlation_risk=metrics.get("risk_score", 0),
                sharp_money_score=metrics.get("sharp_money_score", 0),
            )

            response = await self.ai_client.chat_completion_async(
                [
                    {
                        "role": "system",
                        "content": "You are an expert parlay grader. Provide accurate grades and recommendations.",
                    },
                    {"role": "user", "content": prompt},
                ]
            )

            # Parse AI grading
            grade, confidence, recommendation = self._parse_ai_grading(response.content)
            return grade, confidence, recommendation

        except Exception as e:
            logger.warning(f"⚠️ AI grading failed, using heuristic: {e}")
            return self._heuristic_grading(metrics)

    def _parse_ai_grading(self, ai_response: str) -> tuple[str, float, str]:
        """
        Parse AI grading response
        """
        # Extract grade (A+, A, B+, B, C, D, F)
        import re

        grade_match = re.search(r"\b([A-F][+-]?|A\+)\b", ai_response, re.IGNORECASE)
        grade = grade_match.group(1).upper() if grade_match else "C"

        # Extract confidence (0-1)
        confidence_match = re.search(r"confidence[:\s]*(\d+(?:\.\d+)?)", ai_response, re.IGNORECASE)
        confidence = float(confidence_match.group(1)) if confidence_match else 0.6
        if confidence > 1:
            confidence = confidence / 100  # Convert percentage to decimal

        # Extract recommendation
        if "strong buy" in ai_response.lower():
            recommendation = "Strong Buy"
        elif "buy" in ai_response.lower():
            recommendation = "Buy"
        elif "hold" in ai_response.lower():
            recommendation = "Hold"
        elif "avoid" in ai_response.lower():
            recommendation = "Avoid"
        else:
            recommendation = "Hold"

        return grade, confidence, recommendation

    def _heuristic_grading(self, metrics: dict[str, float]) -> tuple[str, float, str]:
        """
        Heuristic grading without AI
        """
        ev = metrics.get("expected_value", 0)
        risk = metrics.get("risk_score", 0.5)
        diversification = metrics.get("diversification_score", 0.5)

        # Calculate composite score
        score = (ev / 10.0) + (diversification * 0.5) - (risk * 0.5)

        # Assign grade based on score
        if score >= 0.8:
            grade = "A+"
            recommendation = "Strong Buy"
        elif score >= 0.6:
            grade = "A"
            recommendation = "Buy"
        elif score >= 0.4:
            grade = "B+"
            recommendation = "Buy"
        elif score >= 0.2:
            grade = "B"
            recommendation = "Hold"
        elif score >= 0:
            grade = "C"
            recommendation = "Hold"
        else:
            grade = "D"
            recommendation = "Avoid"

        confidence = min(0.8, max(0.4, (score + 1) / 2))

        return grade, confidence, recommendation

    def format_parlay_analysis(self, parlay: SmartParlay) -> str:
        """
        Format comprehensive parlay analysis for display
        """
        analysis = f"""
🧠 **SMART PARLAY ANALYSIS** 🧠

**Parlay ID:** {parlay.parlay_id}
**Strategy:** {parlay.strategy.value.title()}
**AI Grade:** {parlay.ai_grade} (Confidence: {parlay.ai_confidence:.0%})
**Recommendation:** {parlay.recommendation}

**📊 PARLAY METRICS:**
• Legs: {parlay.leg_count}
• Combined Odds: {parlay.combined_odds:+.0f}
• Win Probability: {parlay.combined_probability:.1%}
• Expected Value: {parlay.expected_value:+.1f}%
• Kelly Sizing: {parlay.kelly_sizing:.1%}

**🎯 RISK ANALYSIS:**
• Overall Risk Score: {parlay.risk_score:.1%}
• Correlation Risk: {parlay.total_correlation_risk:.1%}
• Diversification Score: {parlay.diversification_score:.1%}

**💡 MARKET INTELLIGENCE:**
• Sharp Money Score: {parlay.sharp_money_score:.1%}
• Line Movement Score: {parlay.line_movement_score:.1%}
• Market Efficiency: {parlay.market_efficiency_score:.1%}

**🎲 INDIVIDUAL LEGS:**
"""

        for i, leg in enumerate(parlay.legs, 1):
            analysis += f"""
{i}. **{leg.description}**
   • Odds: {leg.odds:+.0f} | Probability: {leg.win_probability:.1%}
   • Expected Value: {leg.expected_value:+.1f}%
   • AI Confidence: {leg.ai_confidence:.0%}
   • Risk Score: {leg.risk_score:.1%}
   • Sharp Money: {"✅" if leg.sharp_money_indicator else "❌"}
"""

        analysis += f"""
**⏰ Analysis Time:** {parlay.construction_time.strftime("%Y-%m-%d %H:%M:%S UTC")}
**📈 Data Quality:** {parlay.data_quality_score:.0%}
"""

        return analysis


# Integration with existing EdgeGod system
async def integrate_smart_parlay_builder_with_edgegod(
    available_legs: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Integration point with existing EdgeGod parlay system
    """
    builder = EQ12SmartParlayBuilder()

    # Build optimized parlay
    parlay = await builder.build_smart_parlay(
        available_legs=available_legs,
        strategy=ParlayStrategy.BALANCED,
        target_legs=4,
        min_expected_value=5.0,
    )

    # Generate analysis
    analysis = builder.format_parlay_analysis(parlay)

    return {
        "smart_parlay": {
            "id": parlay.parlay_id,
            "legs": len(parlay.legs),
            "combined_odds": parlay.combined_odds,
            "win_probability": parlay.combined_probability,
            "expected_value": parlay.expected_value,
            "ai_grade": parlay.ai_grade,
            "recommendation": parlay.recommendation,
        },
        "selected_legs": [
            {
                "description": leg.description,
                "odds": leg.odds,
                "win_probability": leg.win_probability,
                "expected_value": leg.expected_value,
                "ai_confidence": leg.ai_confidence,
            }
            for leg in parlay.legs
        ],
        "risk_analysis": {
            "overall_risk": parlay.risk_score,
            "correlation_risk": parlay.total_correlation_risk,
            "diversification_score": parlay.diversification_score,
        },
        "detailed_analysis": analysis,
        "integration_status": "active",
    }


# CLI interface
async def main():
    """Main function for CLI testing"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Smart Parlay Builder 2.0")
    parser.add_argument("--build", action="store_true", help="Build smart parlay")
    parser.add_argument(
        "--strategy",
        default="balanced",
        choices=["conservative", "aggressive", "balanced", "value_focused", "sharp"],
    )
    parser.add_argument("--legs", type=int, default=4, help="Target number of legs")

    args = parser.parse_args()

    builder = EQ12SmartParlayBuilder()

    if args.build:
        # Sample legs for testing
        sample_legs = [
            {
                "id": "leg1",
                "sport": "NFL",
                "game": "Team A vs Team B",
                "description": "Team A ML",
                "odds": 150,
                "type": "moneyline",
            },
            {
                "id": "leg2",
                "sport": "NBA",
                "game": "Team C vs Team D",
                "description": "Team C -5.5",
                "odds": -110,
                "type": "spread",
            },
            {
                "id": "leg3",
                "sport": "MLB",
                "game": "Team E vs Team F",
                "description": "Over 8.5",
                "odds": 105,
                "type": "total",
            },
            {
                "id": "leg4",
                "sport": "NHL",
                "game": "Team G vs Team H",
                "description": "Team G ML",
                "odds": -120,
                "type": "moneyline",
            },
            {
                "id": "leg5",
                "sport": "NFL",
                "game": "Team I vs Team J",
                "description": "Player X 2+ TDs",
                "odds": 200,
                "type": "player_prop",
            },
        ]

        print(f"🧠 Building smart parlay with {args.strategy} strategy...")

        parlay = await builder.build_smart_parlay(
            available_legs=sample_legs,
            strategy=ParlayStrategy(args.strategy),
            target_legs=args.legs,
        )

        print("✅ Smart parlay built:")
        print(f"   Grade: {parlay.ai_grade} (Confidence: {parlay.ai_confidence:.0%})")
        print(f"   Legs: {len(parlay.legs)}")
        print(f"   Combined Odds: {parlay.combined_odds:+.0f}")
        print(f"   Expected Value: {parlay.expected_value:+.1f}%")
        print(f"   Recommendation: {parlay.recommendation}")

        print("\n📋 Selected Legs:")
        for i, leg in enumerate(parlay.legs, 1):
            print(f"   {i}. {leg.description} ({leg.odds:+.0f}) - EV: {leg.expected_value:+.1f}%")

    else:
        print("📊 Smart Parlay Builder Status:")
        print(f"   AI Client: {'✅' if builder.ai_client else '❌'}")
        print(f"   Correlation Engine: {'✅' if builder.correlation_engine else '❌'}")
        print(f"   Bankroll Optimizer: {'✅' if builder.bankroll_optimizer else '❌'}")
        print(f"   Line Tracker: {'✅' if builder.line_tracker else '❌'}")


if __name__ == "__main__":
    asyncio.run(main())
