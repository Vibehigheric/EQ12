#!/usr/bin/env python3
"""
EQ12 GODSTACK - SGP Correlation Engine
Convert run distributions + player rates into correlations between legs

Core Features:
- Correlation matrix generation for all SGP leg combinations
- Mathematical coherence scoring for proposed SGPs
- DraftKings-style correlation rules enforcement
- Dynamic correlation calculation based on game context
- Pitcher vs team performance correlation modeling
- Weather and park factor correlation adjustments

Output:
- ρ-matrix (correlation coefficients between all legs)
- Coherence score for proposed SGP combinations
- Correlation strength indicators (weak/medium/strong)
- Allowed/restricted leg combinations per DK rules
"""

import argparse
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/sgp_correlation.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CorrelationType(Enum):
    """Types of correlation between SGP legs"""

    POSITIVE_STRONG = "positive_strong"  # ρ > 0.4
    POSITIVE_MODERATE = "positive_moderate"  # 0.2 < ρ <= 0.4
    POSITIVE_WEAK = "positive_weak"  # 0.05 < ρ <= 0.2
    INDEPENDENT = "independent"  # -0.05 <= ρ <= 0.05
    NEGATIVE_WEAK = "negative_weak"  # -0.2 <= ρ < -0.05
    NEGATIVE_MODERATE = "negative_moderate"  # -0.4 <= ρ < -0.2
    NEGATIVE_STRONG = "negative_strong"  # ρ < -0.4


class DraftKingsCorrelationRule(Enum):
    """DraftKings SGP correlation rules"""

    ALLOWED = "allowed"  # Can be combined freely
    USUALLY_ALLOWED = "usually_allowed"  # Allowed with slight juice penalty
    RESTRICTED = "restricted"  # Higher juice penalty
    MUTUALLY_EXCLUSIVE = "mutually_exclusive"  # Cannot combine


@dataclass
class SGPLeg:
    """Individual SGP leg with correlation properties"""

    leg_id: str
    leg_type: str  # "moneyline", "total", "team_total", "player_prop"
    selection: str  # "over", "under", "home", "away"
    line: float | None  # betting line (e.g., 8.5 for total)

    # Leg metadata
    team: str | None  # team affected
    player: str | None  # player affected (for props)
    game_component: str  # "offense", "pitching", "defense", "team_performance"

    # Probability and value
    true_probability: float  # model probability
    offered_odds: int  # sportsbook odds (American format)
    expected_value: float  # EV of this leg

    # Correlation metadata
    correlation_category: str  # for grouping similar legs


@dataclass
class CorrelationPair:
    """Correlation between two SGP legs"""

    leg1_id: str
    leg2_id: str
    correlation_coefficient: float  # Pearson correlation (-1 to 1)
    correlation_type: CorrelationType
    draftkings_rule: DraftKingsCorrelationRule

    # Explanation
    reasoning: str  # why these legs correlate
    strength_description: str  # human-readable strength

    # Context factors
    game_situation: str  # "pitcher_duel", "slugfest", "balanced"
    weather_impact: float  # weather correlation modifier
    park_impact: float  # park factor correlation modifier


@dataclass
class SGPCoherenceScore:
    """Overall coherence assessment for an SGP combination"""

    sgp_id: str
    legs: list[SGPLeg]

    # Correlation matrix
    correlation_matrix: list[list[float]]  # NxN matrix

    # Coherence metrics
    overall_coherence: float  # 0-1 scale (1 = perfectly coherent)
    narrative_strength: float  # how well legs tell a story
    mathematical_consistency: float  # statistical coherence
    draftkings_buildability: float  # can it be built on DK

    # Risk metrics
    correlation_risk: float  # risk from high correlations
    variance_inflation: float  # how correlations affect variance

    # Recommendations
    coherence_grade: str  # "A+", "A", "B+", "B", "C+", "C", "D", "F"
    improvement_suggestions: list[str]

    # Metadata
    calculation_timestamp: datetime
    confidence_level: float


class SGPCorrelationEngine:
    """Main correlation calculation and analysis engine"""

    def __init__(self):
        self.correlation_rules = self._initialize_correlation_rules()
        self.narrative_templates = self._load_narrative_templates()
        self.baseline_correlations = self._load_baseline_correlations()

        logger.info("SGPCorrelationEngine initialized")

    def _initialize_correlation_rules(self) -> dict[str, dict]:
        """Initialize DraftKings-style correlation rules"""

        rules = {
            # Team performance correlations
            "moneyline_team_total": {
                "same_team": {
                    "rule": DraftKingsCorrelationRule.ALLOWED,
                    "base_correlation": 0.35,
                },
                "opponent_team": {
                    "rule": DraftKingsCorrelationRule.ALLOWED,
                    "base_correlation": -0.25,
                },
            },
            # Pitching correlations
            "pitcher_strikeouts_game_total": {
                "under_correlation": {
                    "rule": DraftKingsCorrelationRule.USUALLY_ALLOWED,
                    "base_correlation": 0.28,
                },
                "over_correlation": {
                    "rule": DraftKingsCorrelationRule.ALLOWED,
                    "base_correlation": -0.15,
                },
            },
            "pitcher_strikeouts_team_total": {
                "opposing_team_under": {
                    "rule": DraftKingsCorrelationRule.USUALLY_ALLOWED,
                    "base_correlation": 0.32,
                },
                "own_team_total": {
                    "rule": DraftKingsCorrelationRule.ALLOWED,
                    "base_correlation": 0.12,
                },
            },
            # Player prop correlations
            "hitter_performance_team_success": {
                "hits_team_total": {
                    "rule": DraftKingsCorrelationRule.ALLOWED,
                    "base_correlation": 0.22,
                },
                "total_bases_team_total": {
                    "rule": DraftKingsCorrelationRule.ALLOWED,
                    "base_correlation": 0.28,
                },
                "home_runs_team_total": {
                    "rule": DraftKingsCorrelationRule.ALLOWED,
                    "base_correlation": 0.35,
                },
            },
            # Same player multiple props
            "same_player_props": {
                "hits_total_bases": {
                    "rule": DraftKingsCorrelationRule.RESTRICTED,
                    "base_correlation": 0.65,
                },
                "home_runs_total_bases": {
                    "rule": DraftKingsCorrelationRule.RESTRICTED,
                    "base_correlation": 0.45,
                },
                "rbis_team_total": {
                    "rule": DraftKingsCorrelationRule.ALLOWED,
                    "base_correlation": 0.40,
                },
            },
            # Opposing relationships
            "opposing_pitchers": {
                "both_strikeout_props": {
                    "rule": DraftKingsCorrelationRule.ALLOWED,
                    "base_correlation": 0.05,
                },
                "strikeouts_game_under": {
                    "rule": DraftKingsCorrelationRule.USUALLY_ALLOWED,
                    "base_correlation": 0.25,
                },
            },
            # Mutually exclusive combinations
            "mutually_exclusive": {
                "same_market_different_lines": {
                    "rule": DraftKingsCorrelationRule.MUTUALLY_EXCLUSIVE
                },
                "contradictory_outcomes": {"rule": DraftKingsCorrelationRule.MUTUALLY_EXCLUSIVE},
            },
        }

        return rules

    def _load_narrative_templates(self) -> dict[str, dict]:
        """Load narrative coherence templates"""

        templates = {
            "pitcher_duel": {
                "core_legs": [
                    "game_total_under",
                    "pitcher_strikeouts_over",
                    "opposing_pitcher_strikeouts_over",
                ],
                "supporting_legs": ["team_total_under", "hit_props_under"],
                "base_coherence": 0.85,
                "narrative": "Both starters dominate with strikeouts in low-scoring game",
            },
            "team_stack": {
                "core_legs": [
                    "team_moneyline",
                    "team_total_over",
                    "key_hitter_props_over",
                ],
                "supporting_legs": ["game_total_over", "opposing_pitcher_props_under"],
                "base_coherence": 0.80,
                "narrative": "Team performs well across multiple categories",
            },
            "power_surge": {
                "core_legs": [
                    "home_run_props_over",
                    "total_bases_over",
                    "team_total_over",
                ],
                "supporting_legs": ["game_total_over", "runs_scored_props_over"],
                "base_coherence": 0.75,
                "narrative": "Power hitting drives offensive success",
            },
            "defensive_battle": {
                "core_legs": [
                    "game_total_under",
                    "both_team_totals_under",
                    "error_props_over",
                ],
                "supporting_legs": ["pitcher_props_over", "hit_props_under"],
                "base_coherence": 0.70,
                "narrative": "Strong defense and pitching limit scoring",
            },
            "road_warrior": {
                "core_legs": [
                    "away_team_moneyline",
                    "away_team_total_over",
                    "away_hitter_props_over",
                ],
                "supporting_legs": ["home_pitcher_props_under"],
                "base_coherence": 0.65,
                "narrative": "Road team overcomes home field disadvantage",
            },
        }

        return templates

    def _load_baseline_correlations(self) -> dict[tuple[str, str], float]:
        """Load empirically-derived baseline correlations"""

        # These would typically come from historical data analysis
        baseline = {
            # Team performance
            ("moneyline_home", "home_team_total_over"): 0.35,
            ("moneyline_away", "away_team_total_over"): 0.35,
            ("moneyline_home", "away_team_total_under"): 0.20,
            # Game totals
            ("game_total_over", "home_team_total_over"): 0.45,
            ("game_total_over", "away_team_total_over"): 0.45,
            ("game_total_under", "home_team_total_under"): 0.40,
            ("game_total_under", "away_team_total_under"): 0.40,
            # Pitcher performance
            ("pitcher_strikeouts_over", "opposing_team_total_under"): 0.32,
            ("pitcher_strikeouts_over", "game_total_under"): 0.25,
            ("pitcher_walks_under", "opposing_team_total_under"): 0.18,
            # Hitter performance
            ("hitter_hits_over", "team_total_over"): 0.22,
            ("hitter_total_bases_over", "team_total_over"): 0.28,
            ("hitter_home_runs_over", "game_total_over"): 0.35,
            ("hitter_rbis_over", "team_total_over"): 0.40,
            # Weather correlations
            ("wind_out_conditions", "game_total_over"): 0.15,
            ("wind_out_conditions", "home_run_props_over"): 0.20,
            ("cold_weather", "game_total_under"): 0.12,
            # Park factors
            ("hitter_friendly_park", "game_total_over"): 0.18,
            ("pitcher_friendly_park", "game_total_under"): 0.15,
            # Same player props (these get restricted juice)
            ("hitter_hits_over", "hitter_total_bases_over"): 0.65,
            ("hitter_home_runs_over", "hitter_total_bases_over"): 0.45,
            ("hitter_home_runs_over", "hitter_rbis_over"): 0.38,
            # Opposing outcomes (negative correlation)
            ("home_team_total_over", "away_team_total_under"): -0.05,
            ("pitcher_era_good", "opposing_hitters_props_over"): -0.25,
        }

        return baseline

    def calculate_leg_correlation(
        self, leg1: SGPLeg, leg2: SGPLeg, game_context: dict[str, Any] | None = None
    ) -> CorrelationPair:
        """Calculate correlation between two SGP legs"""

        game_context = game_context or {}

        # Generate correlation key
        self._generate_correlation_key(leg1, leg2)

        # Base correlation from lookup table
        base_correlation = self._get_base_correlation(leg1, leg2)

        # Apply context adjustments
        adjusted_correlation = self._apply_context_adjustments(
            base_correlation, leg1, leg2, game_context
        )

        # Determine correlation type
        correlation_type = self._classify_correlation_strength(adjusted_correlation)

        # Get DraftKings rule
        dk_rule = self._get_draftkings_rule(leg1, leg2)

        # Generate reasoning
        reasoning = self._generate_correlation_reasoning(leg1, leg2, adjusted_correlation)

        return CorrelationPair(
            leg1_id=leg1.leg_id,
            leg2_id=leg2.leg_id,
            correlation_coefficient=adjusted_correlation,
            correlation_type=correlation_type,
            draftkings_rule=dk_rule,
            reasoning=reasoning,
            strength_description=correlation_type.value.replace("_", " ").title(),
            game_situation=game_context.get("game_situation", "unknown"),
            weather_impact=game_context.get("weather_impact", 0.0),
            park_impact=game_context.get("park_impact", 0.0),
        )

    def _generate_correlation_key(self, leg1: SGPLeg, leg2: SGPLeg) -> tuple[str, str]:
        """Generate standardized key for correlation lookup"""

        # Standardize leg descriptions
        leg1_key = f"{leg1.leg_type}_{leg1.selection}_{leg1.team or 'any'}"
        leg2_key = f"{leg2.leg_type}_{leg2.selection}_{leg2.team or 'any'}"

        # Always put in alphabetical order for consistency
        if leg1_key <= leg2_key:
            return (leg1_key, leg2_key)
        return (leg2_key, leg1_key)

    def _get_base_correlation(self, leg1: SGPLeg, leg2: SGPLeg) -> float:
        """Look up base correlation between leg types"""

        # Check for exact matches in baseline correlations
        correlation_key = self._generate_correlation_key(leg1, leg2)

        if correlation_key in self.baseline_correlations:
            return self.baseline_correlations[correlation_key]

        # Rule-based correlation calculation
        correlation = 0.0

        # Same team positive correlation
        if leg1.team == leg2.team and leg1.team is not None:
            if leg1.leg_type in ["moneyline", "team_total"] and leg2.leg_type in [
                "moneyline",
                "team_total",
            ]:
                correlation += 0.35
            elif leg1.leg_type == "player_prop" and leg2.leg_type in [
                "moneyline",
                "team_total",
            ]:
                correlation += 0.25

        # Opposing outcomes negative correlation
        if leg1.team != leg2.team and leg1.team and leg2.team:
            if leg1.selection == "over" and leg2.selection == "under":
                correlation -= 0.15
            elif leg1.selection == leg2.selection:
                correlation += 0.05

        # Pitcher props correlation with game totals
        if "pitcher" in leg1.correlation_category and "total" in leg2.leg_type:
            if leg1.selection == "over" and leg2.selection == "under":
                correlation += 0.28
            elif leg1.selection == "under" and leg2.selection == "over":
                correlation -= 0.20

        # Same player multiple props (high correlation but restricted)
        if leg1.player == leg2.player and leg1.player is not None:
            if leg1.leg_type == "player_prop" and leg2.leg_type == "player_prop":
                correlation += 0.55  # High correlation, but DK restricts these

        return max(-1.0, min(1.0, correlation))  # Clamp to valid range

    def _apply_context_adjustments(
        self,
        base_correlation: float,
        leg1: SGPLeg,
        leg2: SGPLeg,
        context: dict[str, Any],
    ) -> float:
        """Apply game context adjustments to base correlation"""

        adjusted = base_correlation

        # Weather adjustments
        weather = context.get("weather", {})
        if weather:
            # Wind helps home runs and totals
            if weather.get("wind_direction") == "out":
                if "total" in leg1.leg_type and "total" in leg2.leg_type:
                    if leg1.selection == "over" and leg2.selection == "over":
                        adjusted += 0.05

            # Cold weather reduces offense
            temp = weather.get("temperature", 72)
            if temp < 60 and "total" in leg1.leg_type and leg1.selection == "under":
                if "total" in leg2.leg_type and leg2.selection == "under":
                    adjusted += 0.03

        # Park factor adjustments
        park = context.get("park", {})
        if park:
            runs_factor = park.get("runs_factor", 1.0)
            if runs_factor > 1.05:  # Hitter-friendly
                if "total" in leg1.leg_type and "total" in leg2.leg_type:
                    if leg1.selection == "over" and leg2.selection == "over":
                        adjusted += 0.04

        # Game situation adjustments
        situation = context.get("game_situation", "")
        if situation == "pitcher_duel":
            if "strikeouts" in leg1.correlation_category and "total" in leg2.leg_type:
                if leg1.selection == "over" and leg2.selection == "under":
                    adjusted += 0.08

        elif situation == "slugfest":
            if "total" in leg1.leg_type and "total" in leg2.leg_type:
                if leg1.selection == "over" and leg2.selection == "over":
                    adjusted += 0.06

        return max(-1.0, min(1.0, adjusted))  # Clamp to valid range

    def _classify_correlation_strength(self, correlation: float) -> CorrelationType:
        """Classify correlation strength"""

        abs_corr = abs(correlation)

        if abs_corr > 0.4:
            return (
                CorrelationType.POSITIVE_STRONG
                if correlation > 0
                else CorrelationType.NEGATIVE_STRONG
            )
        if abs_corr > 0.2:
            return (
                CorrelationType.POSITIVE_MODERATE
                if correlation > 0
                else CorrelationType.NEGATIVE_MODERATE
            )
        if abs_corr > 0.05:
            return (
                CorrelationType.POSITIVE_WEAK if correlation > 0 else CorrelationType.NEGATIVE_WEAK
            )
        return CorrelationType.INDEPENDENT

    def _get_draftkings_rule(self, leg1: SGPLeg, leg2: SGPLeg) -> DraftKingsCorrelationRule:
        """Determine DraftKings correlation rule for leg combination"""

        # Same player multiple props = restricted
        if leg1.player == leg2.player and leg1.player is not None:
            if leg1.leg_type == "player_prop" and leg2.leg_type == "player_prop":
                return DraftKingsCorrelationRule.RESTRICTED

        # Mutually exclusive outcomes
        if leg1.leg_type == leg2.leg_type and leg1.line == leg2.line:
            if leg1.selection != leg2.selection:
                return DraftKingsCorrelationRule.MUTUALLY_EXCLUSIVE

        # High correlation pitcher/total combinations
        if ("pitcher" in leg1.correlation_category and "total" in leg2.leg_type) or (
            "pitcher" in leg2.correlation_category and "total" in leg1.leg_type
        ):
            return DraftKingsCorrelationRule.USUALLY_ALLOWED

        # Default is allowed
        return DraftKingsCorrelationRule.ALLOWED

    def _generate_correlation_reasoning(
        self, leg1: SGPLeg, leg2: SGPLeg, correlation: float
    ) -> str:
        """Generate human-readable correlation reasoning"""

        if abs(correlation) < 0.05:
            return f"{leg1.leg_type} and {leg2.leg_type} outcomes are largely independent"

        if correlation > 0:
            if leg1.team == leg2.team and leg1.team:
                return f"Both legs benefit from {leg1.team} performing well"
            if "pitcher" in leg1.correlation_category and "total" in leg2.leg_type:
                return "Strong pitching performance supports lower scoring"
            return "These outcomes tend to occur together"
        return "These outcomes tend to be mutually exclusive"

    def calculate_sgp_coherence(
        self, legs: list[SGPLeg], game_context: dict[str, Any] | None = None
    ) -> SGPCoherenceScore:
        """Calculate overall coherence score for an SGP combination"""

        game_context = game_context or {}

        # Calculate all pairwise correlations
        n_legs = len(legs)
        correlation_matrix = [[0.0 for _ in range(n_legs)] for _ in range(n_legs)]
        correlations = []

        for i in range(n_legs):
            for j in range(n_legs):
                if i == j:
                    correlation_matrix[i][j] = 1.0
                elif i < j:  # Only calculate upper triangle
                    corr_pair = self.calculate_leg_correlation(legs[i], legs[j], game_context)
                    correlation_matrix[i][j] = corr_pair.correlation_coefficient
                    correlation_matrix[j][i] = corr_pair.correlation_coefficient  # Symmetric
                    correlations.append(corr_pair)

        # Calculate coherence metrics
        overall_coherence = self._calculate_overall_coherence(correlations, legs)
        narrative_strength = self._calculate_narrative_strength(legs, correlations)
        mathematical_consistency = self._calculate_mathematical_consistency(correlation_matrix)
        draftkings_buildability = self._calculate_draftkings_buildability(correlations)

        # Risk metrics
        correlation_risk = self._calculate_correlation_risk(correlations)
        variance_inflation = self._calculate_variance_inflation(correlation_matrix)

        # Overall grade
        coherence_grade = self._assign_coherence_grade(
            overall_coherence,
            narrative_strength,
            mathematical_consistency,
            draftkings_buildability,
        )

        # Improvement suggestions
        suggestions = self._generate_improvement_suggestions(legs, correlations, coherence_grade)

        return SGPCoherenceScore(
            sgp_id=f"sgp_{hash(tuple(leg.leg_id for leg in legs)) % 10000}",
            legs=legs,
            correlation_matrix=correlation_matrix,
            overall_coherence=overall_coherence,
            narrative_strength=narrative_strength,
            mathematical_consistency=mathematical_consistency,
            draftkings_buildability=draftkings_buildability,
            correlation_risk=correlation_risk,
            variance_inflation=variance_inflation,
            coherence_grade=coherence_grade,
            improvement_suggestions=suggestions,
            calculation_timestamp=datetime.now(UTC),
            confidence_level=0.85,
        )

    def _calculate_overall_coherence(
        self, correlations: list[CorrelationPair], legs: list[SGPLeg]
    ) -> float:
        """Calculate overall coherence score"""

        if not correlations:
            return 1.0

        # Average absolute correlation (how much legs relate to each other)
        avg_abs_correlation = sum(abs(c.correlation_coefficient) for c in correlations) / len(
            correlations
        )

        # Penalty for mutually exclusive combinations
        mutex_penalty = (
            sum(
                1
                for c in correlations
                if c.draftkings_rule == DraftKingsCorrelationRule.MUTUALLY_EXCLUSIVE
            )
            * 0.5
        )

        # Bonus for positive correlations (coherent narrative)
        positive_bonus = (
            sum(max(0, c.correlation_coefficient) for c in correlations) / len(correlations) * 0.3
        )

        coherence = (avg_abs_correlation + positive_bonus) * (1 - mutex_penalty)
        return max(0.0, min(1.0, coherence))

    def _calculate_narrative_strength(
        self, legs: list[SGPLeg], correlations: list[CorrelationPair]
    ) -> float:
        """Calculate how well the SGP tells a coherent story"""

        # Check against narrative templates
        max_template_score = 0.0

        for _template_name, template in self.narrative_templates.items():
            template_score = self._score_against_template(legs, template)
            max_template_score = max(max_template_score, template_score)

        # Bonus for consistent team focus
        teams_involved = {leg.team for leg in legs if leg.team}
        team_focus_bonus = 0.2 if len(teams_involved) <= 2 else -0.1

        return max(0.0, min(1.0, max_template_score + team_focus_bonus))

    def _score_against_template(self, legs: list[SGPLeg], template: dict) -> float:
        """Score SGP against a narrative template"""

        leg_types = [leg.leg_type for leg in legs]
        core_matches = sum(
            1 for core in template["core_legs"] if any(core in lt for lt in leg_types)
        )

        if core_matches == 0:
            return 0.0

        # Score based on template match
        core_score = core_matches / len(template["core_legs"])
        base_coherence = template["base_coherence"]

        return core_score * base_coherence

    def _calculate_mathematical_consistency(self, correlation_matrix: list[list[float]]) -> float:
        """Check mathematical consistency of correlation matrix"""

        # For now, simple check that correlations are reasonable
        # In full implementation, would check positive semi-definiteness

        n = len(correlation_matrix)
        if n < 2:
            return 1.0

        # Check for extreme correlations that might be unrealistic
        extreme_count = 0
        total_correlations = 0

        for i in range(n):
            for j in range(i + 1, n):
                corr = abs(correlation_matrix[i][j])
                if corr > 0.8:  # Very high correlation
                    extreme_count += 1
                total_correlations += 1

        if total_correlations == 0:
            return 1.0

        extreme_ratio = extreme_count / total_correlations
        return max(0.0, 1.0 - extreme_ratio * 0.5)  # Penalize too many extreme correlations

    def _calculate_draftkings_buildability(self, correlations: list[CorrelationPair]) -> float:
        """Calculate how likely DraftKings is to allow this SGP"""

        if not correlations:
            return 1.0

        rule_scores = {
            DraftKingsCorrelationRule.ALLOWED: 1.0,
            DraftKingsCorrelationRule.USUALLY_ALLOWED: 0.85,
            DraftKingsCorrelationRule.RESTRICTED: 0.6,
            DraftKingsCorrelationRule.MUTUALLY_EXCLUSIVE: 0.0,
        }

        total_score = sum(rule_scores[c.draftkings_rule] for c in correlations)
        return total_score / len(correlations)

    def _calculate_correlation_risk(self, correlations: list[CorrelationPair]) -> float:
        """Calculate risk from high correlations"""

        if not correlations:
            return 0.0

        high_corr_count = sum(1 for c in correlations if abs(c.correlation_coefficient) > 0.4)
        return high_corr_count / len(correlations)

    def _calculate_variance_inflation(self, correlation_matrix: list[list[float]]) -> float:
        """Calculate how correlations inflate variance"""

        # Simplified VIF calculation
        n = len(correlation_matrix)
        if n < 2:
            return 1.0

        avg_correlation = 0.0
        count = 0

        for i in range(n):
            for j in range(i + 1, n):
                avg_correlation += abs(correlation_matrix[i][j])
                count += 1

        if count > 0:
            avg_correlation /= count

        # Higher correlations increase variance
        return 1.0 + avg_correlation * 2.0

    def _assign_coherence_grade(
        self, overall: float, narrative: float, mathematical: float, buildability: float
    ) -> str:
        """Assign letter grade based on coherence metrics"""

        avg_score = (overall + narrative + mathematical + buildability) / 4.0

        if avg_score >= 0.95:
            return "A+"
        if avg_score >= 0.90:
            return "A"
        if avg_score >= 0.85:
            return "B+"
        if avg_score >= 0.80:
            return "B"
        if avg_score >= 0.75:
            return "C+"
        if avg_score >= 0.70:
            return "C"
        if avg_score >= 0.60:
            return "D"
        return "F"

    def _generate_improvement_suggestions(
        self, legs: list[SGPLeg], correlations: list[CorrelationPair], grade: str
    ) -> list[str]:
        """Generate suggestions for improving SGP coherence"""

        suggestions = []

        # Check for mutually exclusive legs
        mutex_correlations = [
            c
            for c in correlations
            if c.draftkings_rule == DraftKingsCorrelationRule.MUTUALLY_EXCLUSIVE
        ]
        if mutex_correlations:
            suggestions.append(f"Remove mutually exclusive legs: {mutex_correlations[0].reasoning}")

        # Check for weak correlations
        weak_correlations = [
            c for c in correlations if c.correlation_type == CorrelationType.INDEPENDENT
        ]
        if len(weak_correlations) > len(correlations) / 2:
            suggestions.append(
                "Consider legs with stronger correlations for better narrative coherence"
            )

        # Team focus suggestion
        teams = {leg.team for leg in legs if leg.team}
        if len(teams) > 2:
            suggestions.append("Consider focusing on fewer teams for stronger narrative")

        # Grade-specific suggestions
        if grade in ["D", "F"]:
            suggestions.append("Consider rebuilding SGP with legs that tell a clearer story")
        elif grade in ["C+", "C"]:
            suggestions.append("Add legs that strengthen the central narrative theme")
        elif grade in ["B+", "B"]:
            suggestions.append("Fine-tune leg selection for optimal correlation balance")

        return suggestions


def create_sample_legs() -> list[SGPLeg]:
    """Create sample SGP legs for testing"""

    legs = [
        SGPLeg(
            leg_id="leg_1",
            leg_type="total",
            selection="under",
            line=8.0,
            team=None,
            player=None,
            game_component="team_performance",
            true_probability=0.55,
            offered_odds=110,
            expected_value=0.05,
            correlation_category="game_total",
        ),
        SGPLeg(
            leg_id="leg_2",
            leg_type="player_prop",
            selection="over",
            line=6.5,
            team="NYY",
            player="Gerrit Cole",
            game_component="pitching",
            true_probability=0.60,
            offered_odds=-115,
            expected_value=0.08,
            correlation_category="pitcher_strikeouts",
        ),
        SGPLeg(
            leg_id="leg_3",
            leg_type="player_prop",
            selection="over",
            line=6.5,
            team="TOR",
            player="Chris Bassitt",
            game_component="pitching",
            true_probability=0.58,
            offered_odds=-120,
            expected_value=0.06,
            correlation_category="pitcher_strikeouts",
        ),
    ]

    return legs


async def main():
    """Main CLI interface"""

    parser = argparse.ArgumentParser(description="EQ12 SGP Correlation Engine")
    parser.add_argument("--demo", action="store_true", help="Run demo analysis")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize engine
    engine = SGPCorrelationEngine()

    if args.demo:
        print("🧠 RUNNING SGP CORRELATION ANALYSIS DEMO")

        # Create sample legs
        legs = create_sample_legs()

        # Game context
        game_context = {
            "game_situation": "pitcher_duel",
            "weather": {"temperature": 68, "wind_direction": "calm", "wind_speed": 5},
            "park": {"runs_factor": 0.96, "hr_factor": 0.91},
        }

        # Calculate coherence
        coherence = engine.calculate_sgp_coherence(legs, game_context)

        # Display results
        print("\n🎯 SGP COHERENCE ANALYSIS:")
        print(f"   SGP ID: {coherence.sgp_id}")
        print(f"   Overall Coherence: {coherence.overall_coherence:.3f}")
        print(f"   Narrative Strength: {coherence.narrative_strength:.3f}")
        print(f"   Mathematical Consistency: {coherence.mathematical_consistency:.3f}")
        print(f"   DraftKings Buildability: {coherence.draftkings_buildability:.3f}")
        print(f"   Grade: {coherence.coherence_grade}")

        print("\n🔗 CORRELATION MATRIX:")
        for i, leg in enumerate(legs):
            row_str = f"   {leg.leg_id}: "
            for j in range(len(legs)):
                corr_val = coherence.correlation_matrix[i][j]
                row_str += f"{corr_val:6.3f} "
            print(row_str)

        print("\n📊 INDIVIDUAL CORRELATIONS:")

        # Show pairwise correlations
        for i in range(len(legs)):
            for j in range(i + 1, len(legs)):
                corr_pair = engine.calculate_leg_correlation(legs[i], legs[j], game_context)
                print(
                    f"   {legs[i].leg_id} ↔ {legs[j].leg_id}: {corr_pair.correlation_coefficient:.3f} ({corr_pair.correlation_type.value})"
                )
                print(f"      DK Rule: {corr_pair.draftkings_rule.value}")
                print(f"      Reasoning: {corr_pair.reasoning}")

        print("\n🚨 RISK METRICS:")
        print(f"   Correlation Risk: {coherence.correlation_risk:.3f}")
        print(f"   Variance Inflation: {coherence.variance_inflation:.2f}x")

        if coherence.improvement_suggestions:
            print("\n💡 IMPROVEMENT SUGGESTIONS:")
            for i, suggestion in enumerate(coherence.improvement_suggestions, 1):
                print(f"   {i}. {suggestion}")

        print(f"\n✅ Analysis complete! Grade: {coherence.coherence_grade}")

    else:
        print("❌ Use --demo to run correlation analysis demo")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
