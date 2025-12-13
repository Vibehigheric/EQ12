#!/usr/bin/env python3
"""
EQ12 GODSTACK - Parlay EV/Variance Explainer
For each leg: edge, sensitivity (ΔEV per 5% move), and "why it's here" text for ticket receipt

Core Features:
- Individual leg EV calculation and explanation
- Sensitivity analysis for probability changes
- Parlay-level variance and correlation impact
- Human-readable explanations for each selection
- Risk/reward breakdown for complex parlays
- Ticket receipt generation with reasoning
"""

import argparse
import json
import logging
import math
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/ev_explainer.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class LegAnalysis:
    """Detailed analysis of a single parlay leg"""

    leg_id: str
    description: str

    # Odds and probabilities
    offered_odds: int  # American format
    implied_probability: float
    true_probability: float
    edge_percentage: float

    # EV calculations
    leg_ev: float  # Expected value of this leg alone
    parlay_contribution: float  # How much this leg contributes to parlay EV

    # Sensitivity analysis
    ev_sensitivity_5pct: float  # Change in EV for 5% prob change
    breakeven_probability: float  # Probability needed to break even
    margin_of_safety: float  # How much probability can drop before EV turns negative

    # Risk metrics
    individual_variance: float
    correlation_impact: float  # How correlations affect this leg's value

    # Explanations
    selection_reasoning: str  # Why this leg was chosen
    risk_explanation: str  # What could go wrong
    confidence_factors: list[str]  # Factors supporting confidence
    concern_factors: list[str]  # Factors creating doubt

    # Context
    market_efficiency: str  # "efficient", "semi_efficient", "inefficient"
    value_grade: str  # "A+", "A", "B+", "B", "C+", "C", "D", "F"


@dataclass
class ParlayAnalysis:
    """Complete parlay analysis and explanation"""

    parlay_id: str
    parlay_description: str

    # Overall metrics
    total_odds: int
    total_implied_probability: float
    total_true_probability: float
    parlay_edge_percentage: float
    parlay_ev: float

    # Risk analysis
    parlay_variance: float
    standard_deviation: float
    correlation_adjustment: float

    # Probability scenarios
    breakeven_scenario: dict[str, float]  # What needs to happen to break even
    success_scenarios: list[dict[str, Any]]  # Different ways parlay can win
    failure_modes: list[dict[str, Any]]  # Ways parlay can lose

    # Individual leg analysis
    legs: list[LegAnalysis]

    # Explanations
    overall_thesis: str  # Main reason for this parlay
    key_correlations: list[str]  # Important correlations
    risk_summary: str  # Main risks
    recommendation: str  # Final recommendation

    # Grades and ratings
    overall_grade: str  # A+ to F
    confidence_rating: int  # 1-10
    complexity_score: int  # 1-10 (higher = more complex)

    # Metadata
    analysis_timestamp: datetime
    analyst_notes: str


class EVExplainer:
    """Main EV and variance explanation engine"""

    def __init__(self):
        # Standard explanations for different scenarios
        self.standard_explanations = self._load_standard_explanations()

        # Risk factor templates
        self.risk_templates = self._load_risk_templates()

        # Confidence factor templates
        self.confidence_templates = self._load_confidence_templates()

        logger.info("EV Explainer initialized")

    def _load_standard_explanations(self) -> dict[str, dict[str, str]]:
        """Load standard explanation templates"""

        return {
            "pitcher_strikeouts": {
                "selection_reasoning": "Pitcher has favorable matchup and strong strikeout rate",
                "risk_explanation": "Could struggle if opposing hitters make contact or pitcher gets pulled early",
                "market_type": "Player prop with moderate market efficiency",
            },
            "game_total": {
                "selection_reasoning": "Expected game flow supports this total based on pitching matchup and offensive capabilities",
                "risk_explanation": "Weather, lineup changes, or bullpen usage could affect scoring",
                "market_type": "Highly efficient market with sharp money influence",
            },
            "team_total": {
                "selection_reasoning": "Team's offensive profile matches well against opposing pitcher",
                "risk_explanation": "Early deficit could change approach, or key hitters might sit",
                "market_type": "Moderately efficient with some edge available",
            },
            "moneyline": {
                "selection_reasoning": "Starting pitcher advantage and recent form support this selection",
                "risk_explanation": "Baseball variance high - any team can win on any day",
                "market_type": "Very efficient market, edges typically small",
            },
            "player_hits": {
                "selection_reasoning": "Hitter has favorable splits against opposing pitcher handedness",
                "risk_explanation": "Could face different pitcher in relief or get pitched around",
                "market_type": "Semi-efficient market with exploitable edges",
            },
        }

    def _load_risk_templates(self) -> dict[str, list[str]]:
        """Load risk factor templates"""

        return {
            "pitcher_dependent": [
                "Starting pitcher could be pulled early",
                "Bullpen quality affects game flow",
                "Weather conditions impact pitcher performance",
                "Opposing lineup adjustments",
            ],
            "hitter_dependent": [
                "Batting order changes possible",
                "Late-game pinch hitting scenarios",
                "Pitcher matchup changes in relief",
                "Day/night performance splits",
            ],
            "game_flow": [
                "Blowout could change strategy",
                "Late-inning management decisions",
                "Extra innings possibility",
                "Weather delays or postponement",
            ],
            "correlation_risks": [
                "High correlation increases variance",
                "Correlated failure modes possible",
                "Juice penalties from sportsbook",
                "Reduced overall edge from correlation",
            ],
        }

    def _load_confidence_templates(self) -> dict[str, list[str]]:
        """Load confidence factor templates"""

        return {
            "statistical_edges": [
                "Strong historical performance in similar matchups",
                "Significant statistical advantage in key metrics",
                "Market appears to undervalue this outcome",
                "Multiple data sources confirm edge",
            ],
            "situational_advantages": [
                "Home field advantage in key spots",
                "Rest advantage over opponent",
                "Motivation factors (playoff implications)",
                "Weather conditions favor selection",
            ],
            "market_inefficiency": [
                "Public betting creating line value",
                "Recency bias in market pricing",
                "Injury news not fully reflected",
                "Late breaking information edge",
            ],
            "model_confidence": [
                "High model confidence score",
                "Multiple models agree on direction",
                "Large sample size for projections",
                "Recent data validates model",
            ],
        }

    def calculate_leg_ev(
        self, true_prob: float, offered_odds: int
    ) -> tuple[float, dict[str, float]]:
        """Calculate expected value and related metrics for a single leg"""

        # Convert American odds to decimal
        if offered_odds > 0:
            decimal_odds = (offered_odds / 100) + 1
            payout_multiple = offered_odds / 100
        else:
            decimal_odds = (100 / abs(offered_odds)) + 1
            payout_multiple = 100 / abs(offered_odds)

        # Implied probability
        implied_prob = 1 / decimal_odds

        # EV calculation: (true_prob * payout) - (1 - true_prob) * stake
        # For $1 bet: (true_prob * payout_multiple) - (1 - true_prob)
        ev = (true_prob * payout_multiple) - (1 - true_prob)

        # Edge as percentage
        edge_pct = (true_prob - implied_prob) / implied_prob * 100

        # Breakeven probability
        breakeven_prob = 1 / decimal_odds

        # Margin of safety
        margin_of_safety = (true_prob - breakeven_prob) / breakeven_prob * 100

        # Variance calculation
        win_outcome = payout_multiple
        lose_outcome = -1
        expected_outcome = ev

        variance = (
            true_prob * (win_outcome - expected_outcome) ** 2
            + (1 - true_prob) * (lose_outcome - expected_outcome) ** 2
        )

        metrics = {
            "decimal_odds": decimal_odds,
            "implied_probability": implied_prob,
            "edge_percentage": edge_pct,
            "expected_value": ev,
            "breakeven_probability": breakeven_prob,
            "margin_of_safety": margin_of_safety,
            "variance": variance,
            "standard_deviation": math.sqrt(variance),
        }

        return ev, metrics

    def calculate_sensitivity(
        self, true_prob: float, offered_odds: int, prob_change: float = 0.05
    ) -> dict[str, float]:
        """Calculate sensitivity of EV to probability changes"""

        # Base EV
        base_ev, _ = self.calculate_leg_ev(true_prob, offered_odds)

        # EV with probability increase
        higher_ev, _ = self.calculate_leg_ev(true_prob + prob_change, offered_odds)

        # EV with probability decrease
        lower_ev, _ = self.calculate_leg_ev(true_prob - prob_change, offered_odds)

        # Sensitivity (change in EV per change in probability)
        upside_sensitivity = higher_ev - base_ev
        downside_sensitivity = base_ev - lower_ev

        return {
            "base_ev": base_ev,
            "upside_sensitivity": upside_sensitivity,
            "downside_sensitivity": downside_sensitivity,
            "sensitivity_per_1pct": upside_sensitivity / (prob_change * 100),
            "probability_change_tested": prob_change,
        }

    def analyze_leg(self, leg_data: dict[str, Any]) -> LegAnalysis:
        """Perform complete analysis of a single parlay leg"""

        # Extract leg data
        true_prob = leg_data.get("true_probability", 0.5)
        offered_odds = leg_data.get("offered_odds", 100)
        description = leg_data.get("description", "Unknown leg")
        market_type = leg_data.get("market_type", "unknown")

        # Calculate EV and metrics
        leg_ev, metrics = self.calculate_leg_ev(true_prob, offered_odds)

        # Calculate sensitivity
        sensitivity = self.calculate_sensitivity(true_prob, offered_odds)

        # Generate explanations
        explanations = self._generate_leg_explanations(leg_data, metrics)

        # Assign grades
        value_grade = self._assign_value_grade(
            metrics["edge_percentage"], metrics["margin_of_safety"]
        )
        market_efficiency = self._assess_market_efficiency(market_type, metrics["edge_percentage"])

        return LegAnalysis(
            leg_id=leg_data.get("leg_id", f"leg_{hash(description) % 1000}"),
            description=description,
            offered_odds=offered_odds,
            implied_probability=metrics["implied_probability"],
            true_probability=true_prob,
            edge_percentage=metrics["edge_percentage"],
            leg_ev=leg_ev,
            parlay_contribution=0.0,  # Will be calculated at parlay level
            ev_sensitivity_5pct=sensitivity["upside_sensitivity"],
            breakeven_probability=metrics["breakeven_probability"],
            margin_of_safety=metrics["margin_of_safety"],
            individual_variance=metrics["variance"],
            correlation_impact=leg_data.get("correlation_impact", 0.0),
            selection_reasoning=explanations["selection_reasoning"],
            risk_explanation=explanations["risk_explanation"],
            confidence_factors=explanations["confidence_factors"],
            concern_factors=explanations["concern_factors"],
            market_efficiency=market_efficiency,
            value_grade=value_grade,
        )

    def _generate_leg_explanations(
        self, leg_data: dict[str, Any], metrics: dict[str, float]
    ) -> dict[str, Any]:
        """Generate human-readable explanations for a leg"""

        market_type = leg_data.get("market_type", "unknown")

        # Base explanations from templates
        if market_type in self.standard_explanations:
            base_explanations = self.standard_explanations[market_type]
        else:
            base_explanations = {
                "selection_reasoning": "Statistical edge identified in this market",
                "risk_explanation": "Various factors could impact outcome",
            }

        # Confidence factors based on edge size and data
        confidence_factors = []
        if metrics["edge_percentage"] > 5:
            confidence_factors.append("Significant statistical edge identified")
        if metrics["margin_of_safety"] > 10:
            confidence_factors.append("Large margin of safety vs breakeven")
        if leg_data.get("confidence_score", 0.5) > 0.8:
            confidence_factors.append("High model confidence in projection")

        # Add context-specific confidence factors
        context = leg_data.get("context", {})
        if context.get("home_field_advantage"):
            confidence_factors.append("Home field advantage supports selection")
        if context.get("weather_favorable"):
            confidence_factors.append("Weather conditions favor this outcome")
        if context.get("recent_form_strong"):
            confidence_factors.append("Strong recent form trend")

        # Concern factors
        concern_factors = []
        if metrics["edge_percentage"] < 2:
            concern_factors.append("Edge is relatively small")
        if metrics["variance"] > 2:
            concern_factors.append("High variance outcome")
        if leg_data.get("correlation_impact", 0) > 0.3:
            concern_factors.append("Significant correlation with other legs increases risk")

        # Add context-specific concerns
        if context.get("injury_risk"):
            concern_factors.append("Player injury risk")
        if context.get("weather_concerns"):
            concern_factors.append("Weather could impact game")
        if context.get("lineup_uncertainty"):
            concern_factors.append("Lineup changes possible")

        return {
            "selection_reasoning": base_explanations["selection_reasoning"],
            "risk_explanation": base_explanations["risk_explanation"],
            "confidence_factors": confidence_factors,
            "concern_factors": concern_factors,
        }

    def _assign_value_grade(self, edge_pct: float, margin_of_safety: float) -> str:
        """Assign letter grade based on edge and margin of safety"""

        # Composite score based on edge and safety
        if edge_pct >= 8 and margin_of_safety >= 15:
            return "A+"
        if edge_pct >= 6 and margin_of_safety >= 12:
            return "A"
        if edge_pct >= 4 and margin_of_safety >= 8:
            return "B+"
        if edge_pct >= 2 and margin_of_safety >= 5:
            return "B"
        if edge_pct >= 1 and margin_of_safety >= 2:
            return "C+"
        if edge_pct >= 0 and margin_of_safety >= 0:
            return "C"
        if edge_pct >= -2:
            return "D"
        return "F"

    def _assess_market_efficiency(self, market_type: str, edge_pct: float) -> str:
        """Assess market efficiency based on market type and observed edge"""

        # Market efficiency classifications
        efficient_markets = ["moneyline", "game_total", "spread"]
        inefficient_markets = ["player_props", "novelty", "long_term"]

        base_efficiency = "semi_efficient"
        if market_type in efficient_markets:
            base_efficiency = "efficient"
        elif market_type in inefficient_markets:
            base_efficiency = "inefficient"

        # Adjust based on observed edge
        if abs(edge_pct) > 10:
            return "inefficient"  # Large edges suggest inefficiency
        if abs(edge_pct) < 1:
            return "efficient"  # Small edges suggest efficiency
        return base_efficiency

    def analyze_parlay(self, parlay_data: dict[str, Any]) -> ParlayAnalysis:
        """Perform complete analysis of a parlay"""

        legs_data = parlay_data.get("legs", [])
        correlations = parlay_data.get("correlations", [])

        # Analyze each leg
        leg_analyses = []
        for leg_data in legs_data:
            leg_analysis = self.analyze_leg(leg_data)
            leg_analyses.append(leg_analysis)

        # Calculate parlay-level metrics
        parlay_metrics = self._calculate_parlay_metrics(leg_analyses, correlations)

        # Generate parlay explanations
        explanations = self._generate_parlay_explanations(
            leg_analyses, parlay_metrics, correlations
        )

        # Calculate leg contributions to parlay EV
        self._calculate_leg_contributions(leg_analyses, parlay_metrics["parlay_ev"])

        return ParlayAnalysis(
            parlay_id=parlay_data.get("parlay_id", f"parlay_{hash(str(legs_data)) % 10000}"),
            parlay_description=parlay_data.get("description", "Multi-leg parlay"),
            total_odds=parlay_metrics["total_odds"],
            total_implied_probability=parlay_metrics["implied_probability"],
            total_true_probability=parlay_metrics["true_probability"],
            parlay_edge_percentage=parlay_metrics["edge_percentage"],
            parlay_ev=parlay_metrics["parlay_ev"],
            parlay_variance=parlay_metrics["variance"],
            standard_deviation=parlay_metrics["standard_deviation"],
            correlation_adjustment=parlay_metrics["correlation_adjustment"],
            breakeven_scenario=explanations["breakeven_scenario"],
            success_scenarios=explanations["success_scenarios"],
            failure_modes=explanations["failure_modes"],
            legs=leg_analyses,
            overall_thesis=explanations["overall_thesis"],
            key_correlations=explanations["key_correlations"],
            risk_summary=explanations["risk_summary"],
            recommendation=explanations["recommendation"],
            overall_grade=self._assign_parlay_grade(parlay_metrics),
            confidence_rating=self._calculate_confidence_rating(leg_analyses),
            complexity_score=self._calculate_complexity_score(leg_analyses, correlations),
            analysis_timestamp=datetime.now(UTC),
            analyst_notes=parlay_data.get("analyst_notes", ""),
        )

    def _calculate_parlay_metrics(
        self, legs: list[LegAnalysis], correlations: list[dict[str, Any]]
    ) -> dict[str, float]:
        """Calculate parlay-level metrics"""

        # Combined probability (assuming independence first)
        combined_true_prob = 1.0
        combined_implied_prob = 1.0

        for leg in legs:
            combined_true_prob *= leg.true_probability
            combined_implied_prob *= leg.implied_probability

        # Convert to American odds
        if combined_implied_prob > 0.5:
            total_odds = int(-100 / (1 / combined_implied_prob - 1))
        else:
            total_odds = int(100 * (1 / combined_implied_prob - 1))

        # Calculate parlay EV
        payout_multiple = total_odds / 100 if total_odds > 0 else 100 / abs(total_odds)

        parlay_ev = (combined_true_prob * payout_multiple) - (1 - combined_true_prob)

        # Edge percentage
        edge_pct = (combined_true_prob - combined_implied_prob) / combined_implied_prob * 100

        # Variance calculation (simplified)
        parlay_variance = (
            combined_true_prob * (payout_multiple - parlay_ev) ** 2
            + (1 - combined_true_prob) * (-1 - parlay_ev) ** 2
        )

        # Correlation adjustment (simplified)
        correlation_adjustment = 0.0
        if correlations:
            avg_correlation = sum(
                corr.get("correlation_coefficient", 0) for corr in correlations
            ) / len(correlations)
            correlation_adjustment = avg_correlation * 0.1  # Simplified adjustment

        return {
            "total_odds": total_odds,
            "implied_probability": combined_implied_prob,
            "true_probability": combined_true_prob,
            "edge_percentage": edge_pct,
            "parlay_ev": parlay_ev,
            "variance": parlay_variance,
            "standard_deviation": math.sqrt(parlay_variance),
            "correlation_adjustment": correlation_adjustment,
        }

    def _generate_parlay_explanations(
        self,
        legs: list[LegAnalysis],
        metrics: dict[str, float],
        correlations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate comprehensive parlay explanations"""

        # Overall thesis based on leg types and correlations
        thesis_elements = []
        for leg in legs:
            if "pitcher" in leg.description.lower():
                thesis_elements.append("pitching performance")
            elif "total" in leg.description.lower():
                thesis_elements.append("scoring environment")
            elif "team" in leg.description.lower():
                thesis_elements.append("team success")

        overall_thesis = (
            f"Parlay built around {', '.join(set(thesis_elements))} with supporting correlations"
        )

        # Key correlations
        key_correlations = []
        for corr in correlations:
            if abs(corr.get("correlation_coefficient", 0)) > 0.2:
                key_correlations.append(
                    corr.get("reasoning", "Significant correlation between legs")
                )

        # Success scenarios
        success_scenarios = [
            {
                "scenario": "All legs hit as projected",
                "probability": metrics["true_probability"],
                "description": "Base case where all projections are accurate",
            }
        ]

        # Failure modes
        failure_modes = [
            {
                "mode": "Single leg failure",
                "impact": "Total loss",
                "probability": 1 - metrics["true_probability"],
                "description": "Any single leg failing kills entire parlay",
            }
        ]

        # Risk summary
        risk_factors = []
        if metrics["variance"] > 3:
            risk_factors.append("High variance outcome")
        if len(legs) > 4:
            risk_factors.append("Multiple legs increase failure risk")
        if metrics["correlation_adjustment"] > 0.1:
            risk_factors.append("Correlations increase overall risk")

        risk_summary = (
            "Main risks: " + ", ".join(risk_factors) if risk_factors else "Moderate risk profile"
        )

        # Recommendation
        if metrics["edge_percentage"] > 5 and metrics["parlay_ev"] > 0.1:
            recommendation = "STRONG BET - Significant edge with reasonable risk"
        elif metrics["edge_percentage"] > 2 and metrics["parlay_ev"] > 0:
            recommendation = "MODERATE BET - Positive EV with acceptable risk"
        elif metrics["parlay_ev"] > 0:
            recommendation = "SMALL BET - Slight edge, consider for entertainment"
        else:
            recommendation = "AVOID - Negative expected value"

        # Breakeven scenario
        breakeven_scenario = {
            "required_probability": (
                1 / (abs(metrics["total_odds"]) / 100 + 1)
                if metrics["total_odds"] > 0
                else 100 / (abs(metrics["total_odds"]) + 100)
            ),
            "current_probability": metrics["true_probability"],
            "margin": (
                metrics["true_probability"]
                - (
                    1 / (abs(metrics["total_odds"]) / 100 + 1)
                    if metrics["total_odds"] > 0
                    else 100 / (abs(metrics["total_odds"]) + 100)
                )
            )
            * 100,
        }

        return {
            "overall_thesis": overall_thesis,
            "key_correlations": key_correlations,
            "success_scenarios": success_scenarios,
            "failure_modes": failure_modes,
            "risk_summary": risk_summary,
            "recommendation": recommendation,
            "breakeven_scenario": breakeven_scenario,
        }

    def _calculate_leg_contributions(self, legs: list[LegAnalysis], parlay_ev: float):
        """Calculate how much each leg contributes to parlay EV"""

        total_leg_ev = sum(leg.leg_ev for leg in legs)

        for leg in legs:
            if total_leg_ev != 0:
                leg.parlay_contribution = (leg.leg_ev / total_leg_ev) * parlay_ev
            else:
                leg.parlay_contribution = parlay_ev / len(legs)

    def _assign_parlay_grade(self, metrics: dict[str, float]) -> str:
        """Assign overall grade to parlay"""

        ev = metrics["parlay_ev"]
        edge_pct = metrics["edge_percentage"]

        if ev > 0.15 and edge_pct > 8:
            return "A+"
        if ev > 0.10 and edge_pct > 5:
            return "A"
        if ev > 0.05 and edge_pct > 3:
            return "B+"
        if ev > 0.02 and edge_pct > 1:
            return "B"
        if ev > 0 and edge_pct > 0:
            return "C+"
        if ev > -0.05:
            return "C"
        if ev > -0.10:
            return "D"
        return "F"

    def _calculate_confidence_rating(self, legs: list[LegAnalysis]) -> int:
        """Calculate 1-10 confidence rating"""

        avg_edge = sum(leg.edge_percentage for leg in legs) / len(legs) if legs else 0
        avg_margin = sum(leg.margin_of_safety for leg in legs) / len(legs) if legs else 0

        # Base confidence from edges and margins
        confidence = 5  # Neutral starting point

        if avg_edge > 5:
            confidence += 2
        elif avg_edge > 2:
            confidence += 1
        elif avg_edge < 0:
            confidence -= 2

        if avg_margin > 10:
            confidence += 1
        elif avg_margin < 0:
            confidence -= 1

        # Adjust for number of legs (more legs = less confidence)
        if len(legs) > 5:
            confidence -= 2
        elif len(legs) > 3:
            confidence -= 1

        return max(1, min(10, confidence))

    def _calculate_complexity_score(
        self, legs: list[LegAnalysis], correlations: list[dict[str, Any]]
    ) -> int:
        """Calculate 1-10 complexity score"""

        complexity = len(legs)  # Base complexity from number of legs

        # Add complexity for correlations
        complexity += len(correlations)

        # Add complexity for different market types
        market_types = {leg.description.split()[0].lower() for leg in legs}
        complexity += len(market_types)

        return max(1, min(10, complexity))

    def generate_ticket_receipt(self, analysis: ParlayAnalysis) -> str:
        """Generate human-readable ticket receipt with explanations"""

        receipt = f"""
🎫 PARLAY TICKET RECEIPT & ANALYSIS
═══════════════════════════════════════

PARLAY ID: {analysis.parlay_id}
DESCRIPTION: {analysis.parlay_description}
TOTAL ODDS: {analysis.total_odds:+d}
GRADE: {analysis.overall_grade} | CONFIDENCE: {analysis.confidence_rating}/10

💭 OVERALL THESIS:
{analysis.overall_thesis}

🎯 EXPECTED VALUE BREAKDOWN:
• Parlay EV: {analysis.parlay_ev:+.4f} ({analysis.parlay_edge_percentage:+.2f}% edge)
• True Probability: {analysis.total_true_probability:.3f} ({analysis.total_true_probability * 100:.1f}%)
• Breakeven Needed: {analysis.breakeven_scenario["required_probability"]:.3f} ({analysis.breakeven_scenario["required_probability"] * 100:.1f}%)
• Margin of Safety: {analysis.breakeven_scenario["margin"]:+.1f}%

📋 LEG-BY-LEG ANALYSIS:
"""

        for i, leg in enumerate(analysis.legs, 1):
            receipt += f"""
{i}. {leg.description} ({leg.offered_odds:+d})
   💡 WHY: {leg.selection_reasoning}
   📊 EDGE: {leg.edge_percentage:+.2f}% | EV: {leg.leg_ev:+.4f} | GRADE: {leg.value_grade}
   ⚠️  RISK: {leg.risk_explanation}
   ✅ CONFIDENCE: {", ".join(leg.confidence_factors[:2]) if leg.confidence_factors else "Standard projection"}
   ❌ CONCERNS: {", ".join(leg.concern_factors[:2]) if leg.concern_factors else "None significant"}
"""

        receipt += f"""
🔗 KEY CORRELATIONS:
{chr(10).join(f"• {corr}" for corr in analysis.key_correlations[:3]) if analysis.key_correlations else "• Legs largely independent"}

⚡ SENSITIVITY ANALYSIS:
"""

        for leg in analysis.legs:
            receipt += (
                f"• {leg.description}: ΔEV = {leg.ev_sensitivity_5pct:+.4f} per 5% prob change\n"
            )

        receipt += f"""
🎲 SUCCESS/FAILURE SCENARIOS:
{analysis.risk_summary}

🏆 RECOMMENDATION:
{analysis.recommendation}

📈 RISK METRICS:
• Variance: {analysis.parlay_variance:.4f}
• Standard Deviation: {analysis.standard_deviation:.4f}
• Complexity Score: {analysis.complexity_score}/10

⏰ Generated: {analysis.analysis_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")}

════════════════════════════════════════
This analysis is for informational purposes only.
Past performance does not guarantee future results.
Bet responsibly.
════════════════════════════════════════
"""

        return receipt


def create_sample_parlay_data():
    """Create sample parlay data for testing"""

    return {
        "parlay_id": "sample_001",
        "description": "Yankees/Blue Jays Pitcher's Duel Stack",
        "legs": [
            {
                "leg_id": "leg_1",
                "description": "Game Total Under 8.0",
                "true_probability": 0.55,
                "offered_odds": -110,
                "market_type": "game_total",
                "confidence_score": 0.82,
                "context": {"weather_favorable": True, "recent_form_strong": True},
            },
            {
                "leg_id": "leg_2",
                "description": "Gerrit Cole Over 6.5 Strikeouts",
                "true_probability": 0.60,
                "offered_odds": -115,
                "market_type": "pitcher_strikeouts",
                "confidence_score": 0.85,
                "context": {"home_field_advantage": False, "recent_form_strong": True},
            },
            {
                "leg_id": "leg_3",
                "description": "Chris Bassitt Over 6.5 Strikeouts",
                "true_probability": 0.58,
                "offered_odds": -120,
                "market_type": "pitcher_strikeouts",
                "confidence_score": 0.80,
                "context": {"home_field_advantage": True, "lineup_uncertainty": True},
            },
        ],
        "correlations": [
            {
                "leg1_id": "leg_1",
                "leg2_id": "leg_2",
                "correlation_coefficient": 0.28,
                "reasoning": "Pitcher strikeouts support game under",
            },
            {
                "leg1_id": "leg_1",
                "leg2_id": "leg_3",
                "correlation_coefficient": 0.25,
                "reasoning": "Both pitchers performing well supports low total",
            },
        ],
        "analyst_notes": "High-confidence pitcher's duel setup with strong correlations",
    }


async def main():
    """Main CLI interface"""

    parser = argparse.ArgumentParser(description="EQ12 EV/Variance Explainer")
    parser.add_argument("--demo", action="store_true", help="Run demo analysis")
    parser.add_argument("--ticket", action="store_true", help="Generate ticket receipt")
    parser.add_argument("--export", action="store_true", help="Export analysis to file")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize explainer
    explainer = EVExplainer()

    if args.demo:
        print("📊 EV/VARIANCE EXPLAINER DEMO")

        # Create sample parlay
        parlay_data = create_sample_parlay_data()

        # Analyze parlay
        analysis = explainer.analyze_parlay(parlay_data)

        # Display results
        print(f"\n🎯 PARLAY ANALYSIS: {analysis.parlay_description}")
        print(f"   Total Odds: {analysis.total_odds:+d}")
        print(
            f"   Expected Value: {analysis.parlay_ev:+.4f} ({analysis.parlay_edge_percentage:+.2f}% edge)"
        )
        print(f"   Grade: {analysis.overall_grade} | Confidence: {analysis.confidence_rating}/10")

        print("\n📋 LEG BREAKDOWN:")
        for i, leg in enumerate(analysis.legs, 1):
            print(f"   {i}. {leg.description}")
            print(
                f"      Edge: {leg.edge_percentage:+.2f}% | EV: {leg.leg_ev:+.4f} | Grade: {leg.value_grade}"
            )
            print(f"      5% Sensitivity: {leg.ev_sensitivity_5pct:+.4f}")
            print(f"      Reasoning: {leg.selection_reasoning}")

        print("\n🔗 CORRELATIONS:")
        for corr in analysis.key_correlations:
            print(f"   • {corr}")

        print("\n💡 RECOMMENDATION:")
        print(f"   {analysis.recommendation}")

        if args.ticket:
            print("\n" + "=" * 60)
            print(explainer.generate_ticket_receipt(analysis))

        if args.export:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            output_path = f"C:/EQ12/logs/ev_analysis_{timestamp}.json"

            with open(output_path, "w") as f:
                json.dump(asdict(analysis), f, indent=2, default=str)

            print(f"\n💾 Analysis exported to: {output_path}")

    else:
        print("❌ Use --demo to run EV analysis demo")
        print("   Use --ticket to generate formatted ticket receipt")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
