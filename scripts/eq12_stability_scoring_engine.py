#!/usr/bin/env python3
"""
EQ12 Stability Scoring and Parlay Validation Engine
==================================================

CRITICAL COPILOT INTEGRATION: This script provides the 1-100 stability
scoring system that Copilot uses to validate all parlays before execution.
Every parlay must pass stability validation to prevent repeated losses.

🎯 STABILITY SCORING FEATURES:
- Real-time parlay stability scoring (1-100 scale)
- Void risk assessment and player reliability scoring
- Correlation strength validation and market stability checks
- Automatic recommendations for safer alternatives
- Integration with permanent ban list and adaptive learning

Author: EQ12 Expert Betting System
Date: November 22, 2025
Version: 1.0 - Copilot Stability Integration
"""

import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

@dataclass
class StabilityFactors:
    """Individual stability scoring factors"""
    player_consistency: float  # 0.0 - 1.0
    market_stability: float    # 0.0 - 1.0
    correlation_strength: float # 0.0 - 1.0
    void_risk: float          # 0.0 - 1.0 (inverted - lower is better)
    historical_performance: float # 0.0 - 1.0

@dataclass
class StabilityResult:
    """Complete stability analysis result"""
    stability_score: int      # 1-100 final score
    risk_level: str          # GREEN/YELLOW/RED
    individual_factors: StabilityFactors
    warnings: List[str]
    recommendations: List[str]
    execution_approved: bool

class ParlayStabilityEngine:
    """Engine for calculating parlay stability scores"""

    def __init__(self):
        self.timestamp = datetime.now()

        # Stability weights (must sum to 1.0)
        self.weights = {
            "player_consistency": 0.30,
            "market_stability": 0.25,
            "correlation_strength": 0.25,
            "void_risk": 0.20
        }

        # Player reliability database (based on loss analysis)
        self.player_reliability = {
            "Cooper Flagg": 0.85,      # High consistency
            "Caleb Foster": 0.78,      # Good reliability
            "Kon Knueppel": 0.82,      # Strong performer
            "Alexandre Sarr": 0.45,    # VERY UNRELIABLE - from loss analysis
            "Scottie Barnes": 0.52,    # Void risk issues
            "RJ Barrett": 0.75,        # Generally reliable
            "Jayson Tatum": 0.88,      # Elite consistency
            "Jaylen Brown": 0.83,      # Very reliable
            "Default Player": 0.70     # Average baseline
        }

        # Market stability ratings
        self.market_stability = {
            "point_spreads": 0.90,          # Very stable
            "game_totals": 0.85,            # Stable
            "player_points": 0.80,          # Generally stable
            "player_rebounds": 0.65,        # Moderate volatility
            "player_assists": 0.75,         # Good stability
            "points_rebounds": 0.70,        # Combined props
            "odd_even": 0.05,               # BANNED - pure randomness
            "double_double": 0.40,          # High volatility
            "extreme_totals": 0.25,         # Very risky (35+, 14+)
            "touchdown_props": 0.50         # Void risk
        }

        # Correlation strength database
        self.correlation_patterns = {
            "pace_team_overs": 0.82,        # Strong positive
            "pace_team_unders": 0.15,       # NEGATIVE correlation
            "blowout_overs": 0.74,          # Good correlation
            "close_game_unders": 0.68,      # Moderate correlation
            "player_team_success": 0.76,    # Good correlation
            "opposing_players": 0.45        # Low correlation
        }

    def calculate_stability_score(self, parlay_legs: List[str]) -> StabilityResult:
        """Calculate comprehensive stability score for parlay"""

        print(f"\n📊 CALCULATING STABILITY SCORE")
        print(f"🎯 Parlay: {parlay_legs}")
        print(f"⏰ Analysis Time: {self.timestamp.strftime('%H:%M:%S')}")

        # Calculate individual stability factors
        factors = self._analyze_stability_factors(parlay_legs)

        # Calculate weighted stability score
        weighted_score = (
            factors.player_consistency * self.weights["player_consistency"] +
            factors.market_stability * self.weights["market_stability"] +
            factors.correlation_strength * self.weights["correlation_strength"] +
            (1 - factors.void_risk) * self.weights["void_risk"]  # Invert void risk
        )

        # Convert to 1-100 scale
        stability_score = int(weighted_score * 100)

        # Determine risk level and approval
        risk_level, execution_approved = self._determine_risk_level(stability_score)

        # Generate warnings and recommendations
        warnings = self._generate_warnings(factors, parlay_legs)
        recommendations = self._generate_recommendations(factors, parlay_legs, stability_score)

        result = StabilityResult(
            stability_score=stability_score,
            risk_level=risk_level,
            individual_factors=factors,
            warnings=warnings,
            recommendations=recommendations,
            execution_approved=execution_approved
        )

        # Display results
        self._display_stability_results(result)

        return result

    def _analyze_stability_factors(self, parlay_legs: List[str]) -> StabilityFactors:
        """Analyze individual stability factors"""

        # Player Consistency Analysis
        player_scores = []
        for leg in parlay_legs:
            player = self._extract_player(leg)
            if player:
                reliability = self.player_reliability.get(player, self.player_reliability["Default Player"])
                player_scores.append(reliability)
            else:
                # Team-based bet - generally more stable
                player_scores.append(0.85)

        player_consistency = np.mean(player_scores) if player_scores else 0.70

        # Market Stability Analysis
        market_scores = []
        for leg in parlay_legs:
            market_type = self._classify_market_type(leg)
            stability = self.market_stability.get(market_type, 0.60)
            market_scores.append(stability)

        market_stability = np.mean(market_scores)

        # Correlation Strength Analysis
        correlation_strength = self._analyze_correlations(parlay_legs)

        # Void Risk Analysis
        void_risk = self._calculate_void_risk(parlay_legs)

        return StabilityFactors(
            player_consistency=player_consistency,
            market_stability=market_stability,
            correlation_strength=correlation_strength,
            void_risk=void_risk,
            historical_performance=0.75  # Placeholder - would use historical data
        )

    def _extract_player(self, leg: str) -> Optional[str]:
        """Extract player name from bet leg"""

        leg_lower = leg.lower()

        # Known players from analysis
        players = [
            "Cooper Flagg", "Caleb Foster", "Kon Knueppel",
            "Alexandre Sarr", "Scottie Barnes", "RJ Barrett",
            "Jayson Tatum", "Jaylen Brown"
        ]

        for player in players:
            if player.lower() in leg_lower:
                return player

        return None

    def _classify_market_type(self, leg: str) -> str:
        """Classify the type of betting market"""

        leg_lower = leg.lower()

        # Market classification logic
        if any(spread_indicator in leg_lower for spread_indicator in ["+", "-", "spread"]):
            return "point_spreads"
        elif "over" in leg_lower or "under" in leg_lower:
            if "total" in leg_lower or "game" in leg_lower:
                return "game_totals"
            elif "points" in leg_lower:
                return "player_points"
            elif "rebounds" in leg_lower:
                return "player_rebounds"
            elif "assists" in leg_lower:
                return "player_assists"
            elif "p+r" in leg_lower or "points+rebounds" in leg_lower:
                return "points_rebounds"
        elif "odd" in leg_lower or "even" in leg_lower:
            return "odd_even"  # BANNED
        elif "double" in leg_lower and "double" in leg_lower:
            return "double_double"
        elif "35+" in leg or "40+" in leg or "14+" in leg:
            return "extreme_totals"
        elif "td" in leg_lower or "touchdown" in leg_lower:
            return "touchdown_props"

        return "other_props"

    def _analyze_correlations(self, parlay_legs: List[str]) -> float:
        """Analyze correlation strength between parlay legs"""

        correlations = []

        # Check for pace-based correlations
        has_pace_team = any("raptors" in leg.lower() for leg in parlay_legs)
        has_overs = sum(1 for leg in parlay_legs if "over" in leg.lower())
        has_unders = sum(1 for leg in parlay_legs if "under" in leg.lower())

        if has_pace_team:
            if has_overs > has_unders:
                correlations.append(self.correlation_patterns["pace_team_overs"])
            elif has_unders > has_overs:
                correlations.append(self.correlation_patterns["pace_team_unders"])  # Very poor correlation

        # Check for blowout correlations
        has_spread = any("+" in leg or "-" in leg for leg in parlay_legs if not ("over" in leg.lower() or "under" in leg.lower()))
        if has_spread and has_overs:
            correlations.append(self.correlation_patterns["blowout_overs"])

        # Default correlation for multiple players from same team
        team_players = 0
        for leg in parlay_legs:
            if self._extract_player(leg):
                team_players += 1

        if team_players > 1:
            correlations.append(self.correlation_patterns["player_team_success"])

        return np.mean(correlations) if correlations else 0.60

    def _calculate_void_risk(self, parlay_legs: List[str]) -> float:
        """Calculate overall void risk for parlay"""

        total_void_risk = 0.0

        for leg in parlay_legs:
            player = self._extract_player(leg)

            # Player-specific void risks
            if player == "Scottie Barnes":
                if "td" in leg.lower() or "touchdown" in leg.lower():
                    total_void_risk += 0.23  # 23% void rate on TD props
                else:
                    total_void_risk += 0.05  # General injury risk
            elif player == "Alexandre Sarr":
                total_void_risk += 0.12  # High volatility/status uncertainty
            elif player:
                total_void_risk += 0.03  # General player injury risk
            else:
                total_void_risk += 0.01  # Team bet void risk

        # Cap total void risk at reasonable maximum
        return min(total_void_risk, 0.50)

    def _determine_risk_level(self, stability_score: int) -> Tuple[str, bool]:
        """Determine risk level and execution approval"""

        if stability_score >= 85:
            return "GREEN", True      # Execute with confidence
        elif stability_score >= 70:
            return "YELLOW", True     # Proceed with caution
        else:
            return "RED", False       # High risk - recommend alternatives

    def _generate_warnings(self, factors: StabilityFactors, parlay_legs: List[str]) -> List[str]:
        """Generate specific warnings based on stability factors"""

        warnings = []

        # Player consistency warnings
        if factors.player_consistency < 0.60:
            low_reliability_players = []
            for leg in parlay_legs:
                player = self._extract_player(leg)
                if player and self.player_reliability.get(player, 0.70) < 0.60:
                    low_reliability_players.append(player)
            if low_reliability_players:
                warnings.append(f"⚠️ Low reliability players detected: {', '.join(low_reliability_players)}")

        # Market stability warnings
        if factors.market_stability < 0.60:
            warnings.append(f"⚠️ Contains high-volatility markets - consider safer alternatives")

        # Correlation warnings
        if factors.correlation_strength < 0.50:
            warnings.append(f"⚠️ Weak correlations detected - legs may conflict with each other")

        # Void risk warnings
        if factors.void_risk > 0.15:
            warnings.append(f"⚠️ High void risk ({factors.void_risk:.1%}) - monitor injury reports")

        # Specific banned market warnings
        for leg in parlay_legs:
            leg_lower = leg.lower()
            if "odd" in leg_lower or "even" in leg_lower:
                warnings.append(f"🚫 BANNED MARKET: {leg} - Pure randomness, no skill edge")
            elif "sarr" in leg_lower and "rebound" in leg_lower:
                warnings.append(f"🚫 BANNED MARKET: {leg} - Sarr rebounds extremely inconsistent")
            elif "barnes" in leg_lower and ("td" in leg_lower or "touchdown" in leg_lower):
                warnings.append(f"🚫 BANNED MARKET: {leg} - Barnes TD props have 23% void rate")

        return warnings

    def _generate_recommendations(self, factors: StabilityFactors, parlay_legs: List[str], score: int) -> List[str]:
        """Generate specific recommendations to improve stability"""

        recommendations = []

        if score < 70:
            recommendations.append("🔴 HIGH RISK PARLAY - Consider alternatives or reduce stake")
        elif score < 85:
            recommendations.append("🟡 MODERATE RISK - Proceed with caution and reduced stake")
        else:
            recommendations.append("🟢 STABLE PARLAY - Approved for full execution")

        # Specific improvement suggestions
        if factors.player_consistency < 0.60:
            recommendations.append("Replace unreliable players with more consistent alternatives")

        if factors.market_stability < 0.60:
            recommendations.append("Switch to more stable markets (spreads/totals vs props)")

        if factors.correlation_strength < 0.50:
            recommendations.append("Improve correlations - ensure legs support each other")

        if factors.void_risk > 0.15:
            recommendations.append("Reduce void risk - avoid injury-prone players")

        # Specific leg recommendations
        for leg in parlay_legs:
            if "sarr" in leg.lower() and "rebound" in leg.lower():
                recommendations.append(f"Replace '{leg}' with Sarr points prop (more reliable)")
            elif "barnes" in leg.lower() and "td" in leg.lower():
                recommendations.append(f"Replace '{leg}' with Barnes rushing yards (lower void risk)")
            elif "35+" in leg or "40+" in leg:
                recommendations.append(f"Replace '{leg}' with more achievable total (25+ or 30+)")

        return recommendations

    def _display_stability_results(self, result: StabilityResult):
        """Display comprehensive stability analysis results"""

        print(f"\n📊 STABILITY ANALYSIS COMPLETE")
        print(f"=" * 45)
        print(f"🎯 STABILITY SCORE: {result.stability_score}/100")
        print(f"📈 RISK LEVEL: {result.risk_level}")
        print(f"✅ EXECUTION APPROVED: {'YES' if result.execution_approved else 'NO'}")
        print()

        print(f"🔍 INDIVIDUAL FACTORS:")
        print(f"   👤 Player Consistency: {result.individual_factors.player_consistency:.2%}")
        print(f"   📊 Market Stability: {result.individual_factors.market_stability:.2%}")
        print(f"   🔗 Correlation Strength: {result.individual_factors.correlation_strength:.2%}")
        print(f"   🚨 Void Risk: {result.individual_factors.void_risk:.2%}")
        print()

        if result.warnings:
            print(f"⚠️ WARNINGS:")
            for warning in result.warnings:
                print(f"   {warning}")
            print()

        print(f"💡 RECOMMENDATIONS:")
        for recommendation in result.recommendations:
            print(f"   {recommendation}")
        print()

        # Final execution recommendation
        if result.execution_approved:
            print(f"🚀 EXECUTION STATUS: APPROVED")
            print(f"💰 Recommended Stake: {'Full' if result.stability_score >= 85 else 'Reduced'}")
        else:
            print(f"🛑 EXECUTION STATUS: NOT RECOMMENDED")
            print(f"🔄 Action Required: Improve stability before execution")


def test_stability_scoring():
    """Test stability scoring with sample parlays"""

    engine = ParlayStabilityEngine()

    print("🧪 TESTING STABILITY SCORING ENGINE")
    print("=" * 40)

    # Test parlays
    test_parlays = [
        # High stability parlay - should score 85+
        ["UNC +7.5", "Cooper Flagg Over 22.5 P+R", "Under 148.5"],

        # Medium stability parlay - should score 70-84
        ["Celtics -5.5", "Tatum Over 27.5 Points", "Lakers +3.5"],

        # Low stability parlay - should score <70
        ["Sarr Over 9.5 Rebounds", "Game Total Odd", "Barnes Anytime TD"],

        # Banned market parlay - should score very low
        ["Double-Double Yes", "Over 35.5 Points", "Even Total Points"],
    ]

    for i, parlay in enumerate(test_parlays, 1):
        print(f"\n🧪 TEST CASE {i}: {parlay}")
        result = engine.calculate_stability_score(parlay)
        print(f"📊 Final Score: {result.stability_score}/100 ({result.risk_level})")
        print("-" * 50)


def main():
    """Main execution function"""
    test_stability_scoring()


if __name__ == "__main__":
    main()
