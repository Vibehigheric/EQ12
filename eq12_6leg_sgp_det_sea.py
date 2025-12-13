#!/usr/bin/env python3
"""
EQ12 Enhanced 6-Leg SGP Builder - Detroit Tigers vs Seattle Mariners
Advanced Same Game Parlay with 6+ Legs and Correlation Optimization

Date: October 4, 2025
Game: Detroit Tigers @ Seattle Mariners
"""

import argparse
import json
import math
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SGPLeg:
    """Individual SGP leg with enhanced analytics"""

    market: str
    selection: str
    odds: int
    probability: float
    confidence: float
    correlation_group: str  # For correlation analysis


class Enhanced6LegSGP:
    """Advanced 6-leg SGP builder with correlation optimization"""

    def __init__(self):
        self.ballpark_factors = {
            "hr_factor": 0.92,  # T-Mobile Park HR suppression
            "runs_factor": 0.98,  # Slight pitcher advantage
            "hit_factor": 1.02,  # Good hitting conditions tonight
        }

    def calculate_player_hit_probability(
        self, avg: float, recent_form: float, vs_pitcher: float, line: float = 0.5
    ) -> float:
        """Enhanced hit probability calculation"""
        adjusted_avg = avg * recent_form * vs_pitcher * self.ballpark_factors["hit_factor"]
        expected_hits = adjusted_avg * 3.8  # Expected at-bats

        if line == 0.5:  # 1+ hits
            return 1 - math.exp(-expected_hits)
        if line == 1.5:  # 2+ hits
            prob_0 = math.exp(-expected_hits)
            prob_1 = expected_hits * math.exp(-expected_hits)
            return 1 - (prob_0 + prob_1)

        return 0.5

    def calculate_total_bases_probability(
        self, slg: float, recent_form: float, vs_pitcher: float, line: float = 1.5
    ) -> float:
        """Total bases probability with ballpark adjustment"""
        adjusted_slg = slg * recent_form * vs_pitcher
        adjusted_slg * 3.8

        if line == 1.5:  # 2+ total bases
            # Probability of extra base hit or multiple singles
            extra_base_rate = (adjusted_slg - 0.250) * 3.8
            return min(0.80, max(0.25, extra_base_rate * 0.65))
        if line == 2.5:  # 3+ total bases
            return min(0.65, max(0.15, extra_base_rate * 0.35))

        return 0.5

    def calculate_rbi_probability(self, ops: float, lineup_pos: int, recent_form: float) -> float:
        """RBI probability based on OPS and lineup position"""
        base_rate = (ops - 0.650) / 4.0 if ops > 0.650 else 0.12

        # Lineup position adjustment (3-6 hitters get RBI boost)
        position_factor = 1.3 if 3 <= lineup_pos <= 6 else 1.0

        adjusted_prob = base_rate * recent_form * position_factor
        return min(0.70, max(0.20, adjusted_prob))

    def calculate_team_runs_probability(self, expected_runs: float, line: float) -> float:
        """Team runs probability using Poisson distribution"""
        if line == 3.5:
            prob_under = sum(
                [
                    (expected_runs**k * math.exp(-expected_runs)) / math.factorial(k)
                    for k in range(4)
                ]
            )
            return 1 - prob_under
        if line == 4.5:
            prob_under = sum(
                [
                    (expected_runs**k * math.exp(-expected_runs)) / math.factorial(k)
                    for k in range(5)
                ]
            )
            return 1 - prob_under

        return 0.5

    def build_6_leg_sgp(self) -> dict:
        """Build optimized 6-leg SGP with correlation analysis"""

        # Enhanced player profiles
        players = {
            "riley_greene": {
                "avg": 0.278,
                "slg": 0.449,
                "ops": 0.798,
                "recent": 1.15,
                "vs_rhp": 1.08,
                "pos": 1,
            },
            "colt_keith": {
                "avg": 0.262,
                "slg": 0.417,
                "ops": 0.742,
                "recent": 0.95,
                "vs_rhp": 1.02,
                "pos": 2,
            },
            "julio_rodriguez": {
                "avg": 0.273,
                "slg": 0.456,
                "ops": 0.785,
                "recent": 1.18,
                "vs_lhp": 1.12,
                "pos": 2,
            },
            "cal_raleigh": {
                "avg": 0.224,
                "slg": 0.436,
                "ops": 0.751,
                "recent": 1.09,
                "vs_lhp": 1.15,
                "pos": 3,
            },
            "randy_arozarena": {
                "avg": 0.251,
                "slg": 0.417,
                "ops": 0.738,
                "recent": 0.97,
                "vs_lhp": 1.06,
                "pos": 4,
            },
            "luke_raley": {
                "avg": 0.242,
                "slg": 0.424,
                "ops": 0.712,
                "recent": 1.14,
                "vs_lhp": 1.08,
                "pos": 5,
            },
        }

        # Build 6-leg SGP with strategic correlation
        sgp_legs = []

        # LEG 1: Riley Greene 1+ Hits (-135) - Anchor leg
        greene = players["riley_greene"]
        greene_hit_prob = self.calculate_player_hit_probability(
            greene["avg"], greene["recent"], greene["vs_rhp"]
        )
        sgp_legs.append(
            SGPLeg(
                "Riley Greene 1+ Hits",
                "1+ Hits",
                -135,
                greene_hit_prob,
                0.85,
                "detroit_offense",
            )
        )

        # LEG 2: Julio Rodriguez 1+ Hits (-125) - Correlated with SEA offense
        julio = players["julio_rodriguez"]
        julio_hit_prob = self.calculate_player_hit_probability(
            julio["avg"], julio["recent"], julio["vs_lhp"]
        )
        sgp_legs.append(
            SGPLeg(
                "Julio Rodriguez 1+ Hits",
                "1+ Hits",
                -125,
                julio_hit_prob,
                0.82,
                "seattle_offense",
            )
        )

        # LEG 3: Julio Rodriguez 2+ Total Bases (-110) - Stacked with his hits
        julio_tb_prob = self.calculate_total_bases_probability(
            julio["slg"], julio["recent"], julio["vs_lhp"]
        )
        sgp_legs.append(
            SGPLeg(
                "Julio Rodriguez 2+ Total Bases",
                "2+ Total Bases",
                -110,
                julio_tb_prob,
                0.78,
                "seattle_offense",
            )
        )

        # LEG 4: Cal Raleigh 1+ RBIs (+105) - Power correlation
        raleigh = players["cal_raleigh"]
        raleigh_rbi_prob = self.calculate_rbi_probability(
            raleigh["ops"], raleigh["pos"], raleigh["recent"]
        )
        sgp_legs.append(
            SGPLeg(
                "Cal Raleigh 1+ RBIs",
                "1+ RBIs",
                105,
                raleigh_rbi_prob,
                0.71,
                "seattle_offense",
            )
        )

        # LEG 5: Game Total Over 7.5 Runs (-115) - Offensive correlation
        # Detroit expected: 4.2, Seattle expected: 4.8 = 9.0 total
        game_over_prob = self.calculate_team_runs_probability(9.0, 7.5)
        sgp_legs.append(
            SGPLeg(
                "Game Total Over 7.5",
                "Over 7.5 Runs",
                -115,
                game_over_prob,
                0.73,
                "offense_total",
            )
        )

        # LEG 6: Both Teams To Score 4+ Runs (+140) - High correlation
        # Probability both teams score 4+ (aggressive but correlated)
        det_4plus = self.calculate_team_runs_probability(4.2, 3.5) * 0.8  # Conservative adj
        sea_4plus = self.calculate_team_runs_probability(4.8, 3.5) * 0.9
        both_4plus_prob = det_4plus * sea_4plus * 1.2  # Positive correlation
        sgp_legs.append(
            SGPLeg(
                "Both Teams 4+ Runs",
                "Both Teams Score 4+",
                140,
                both_4plus_prob,
                0.68,
                "offense_total",
            )
        )

        # Calculate correlation-adjusted probability
        individual_probs = [leg.probability for leg in sgp_legs]
        raw_combined = 1.0
        for prob in individual_probs:
            raw_combined *= prob

        # Advanced correlation adjustment
        correlation_matrix = {
            "seattle_offense": 1.35,  # Strong positive correlation within SEA offense
            "offense_total": 1.25,  # Total runs correlate with individual performances
            "mixed": 1.15,  # Cross-team correlations
        }

        # Apply correlation bonuses
        seattle_legs = sum(1 for leg in sgp_legs if leg.correlation_group == "seattle_offense")
        total_legs = sum(1 for leg in sgp_legs if leg.correlation_group == "offense_total")

        correlation_factor = 1.0
        if seattle_legs >= 3:
            correlation_factor *= correlation_matrix["seattle_offense"] ** 0.6
        if total_legs >= 2:
            correlation_factor *= correlation_matrix["offense_total"] ** 0.4

        adjusted_prob = raw_combined * correlation_factor

        # Convert to American odds
        if adjusted_prob > 0.50:
            sgp_odds = int(-100 * adjusted_prob / (1 - adjusted_prob))
        else:
            sgp_odds = int(100 * (1 - adjusted_prob) / adjusted_prob)

        # Kelly criterion sizing
        implied_prob_at_market = 0.12  # Assume market offers around +730
        if adjusted_prob > implied_prob_at_market:
            kelly_pct = ((adjusted_prob * 8.3 - 1) / 7.3) * 100  # Kelly formula
            kelly_pct = max(0, min(kelly_pct, 4.0))  # Cap at 4%
        else:
            kelly_pct = 0.0

        return {
            "sgp_info": {
                "game": "Detroit Tigers @ Seattle Mariners",
                "date": "October 4, 2025",
                "time": "10:10 PM ET",
                "venue": "T-Mobile Park, Seattle",
            },
            "six_leg_sgp": [
                {
                    "leg": i + 1,
                    "market": leg.market,
                    "selection": leg.selection,
                    "odds": f"{leg.odds:+d}" if leg.odds > 0 else f"{leg.odds}",
                    "probability": f"{leg.probability:.3f}",
                    "confidence": f"{leg.confidence:.2f}",
                    "correlation_group": leg.correlation_group,
                }
                for i, leg in enumerate(sgp_legs)
            ],
            "sgp_analysis": {
                "individual_probabilities": [f"{p:.3f}" for p in individual_probs],
                "raw_combined_probability": f"{raw_combined:.6f}",
                "correlation_adjustment": f"{correlation_factor:.3f}",
                "final_probability": f"{adjusted_prob:.5f}",
                "fair_value_odds": sgp_odds,
                "estimated_market_odds": "+730 to +850",
                "overall_confidence": f"{statistics.mean([leg.confidence for leg in sgp_legs]):.2f}",
                "kelly_sizing": f"{kelly_pct:.1f}%",
            },
            "correlation_breakdown": {
                "seattle_offense_stack": f"{seattle_legs} legs with 1.35x correlation boost",
                "total_runs_correlation": f"{total_legs} legs benefit from offensive environment",
                "key_synergies": [
                    "Julio hits + total bases (same player stack)",
                    "Seattle offense + game total (offensive environment)",
                    "Both teams scoring + game total (high-scoring game script)",
                ],
            },
            "strategic_reasoning": [
                "LEG 1-2: Dual hit anchors provide stability (73%+ each)",
                "LEG 3: Julio total bases stacks with his hit probability",
                "LEG 4: Raleigh RBI correlates with Seattle offensive output",
                "LEG 5-6: Game totals benefit from offensive correlation",
                "Weather/Ballpark: Clear conditions favor hitting at T-Mobile Park",
            ],
            "risk_assessment": {
                "primary_risks": [
                    "Tarik Skubal dominance (elite recent form)",
                    "T-Mobile Park pitcher-friendly reputation",
                    "October offensive suppression historically",
                ],
                "risk_mitigation": [
                    "Avoided strikeout props (Skubal's strength)",
                    "Mixed team approach reduces single-team risk",
                    "Conservative probability estimates with correlation boost",
                ],
                "correlation_risk": "High - if offensive game script fails, multiple legs fail together",
            },
            "recommendation": {
                "action": "MODERATE PLAY" if kelly_pct > 1.5 else "PASS/SMALL PLAY",
                "reasoning": "6-leg structure creates correlation risk but offers lottery ticket upside",
                "optimal_unit_size": f"{kelly_pct:.1f}% Kelly sizing",
                "confidence_level": f"{statistics.mean([leg.confidence for leg in sgp_legs]):.1f}/10",
                "market_target": "Seek +750 or better odds for positive expected value",
            },
        }


def main():
    parser = argparse.ArgumentParser(description="Enhanced 6-Leg SGP Builder")
    parser.add_argument("--format", choices=["detailed", "summary", "json"], default="detailed")
    parser.add_argument("--save", action="store_true", help="Save to file")

    args = parser.parse_args()

    try:
        builder = Enhanced6LegSGP()
        analysis = builder.build_6_leg_sgp()

        if args.format == "json":
            print(json.dumps(analysis, indent=2))

        elif args.format == "summary":
            print("\n6-LEG SGP - {analysis['sgp_info']['game']}")
            print("=" * 60)
            for leg in analysis["six_leg_sgp"]:
                print("{leg['leg']}. {leg['selection']} ({leg['odds']})")

            anal = analysis["sgp_analysis"]
            print("\nEstimated Odds: {anal['estimated_market_odds']}")
            print("True Probability: {anal['final_probability']}")
            print("Kelly Sizing: {anal['kelly_sizing']}")
            print("Confidence: {anal['overall_confidence']}")
            print("\nRecommendation: {analysis['recommendation']['action']}")

        else:  # detailed
            print("\n" + "=" * 75)
            print("🎯 ENHANCED 6-LEG SGP - DETROIT @ SEATTLE")
            print("=" * 75)

            # Game info
            analysis["sgp_info"]
            print("\n📊 GAME INFORMATION:")
            print("  Matchup: {game['game']}")
            print("  Date/Time: {game['date']} at {game['time']}")
            print("  Venue: {game['venue']}")

            # 6-leg construction
            print("\n🎯 6-LEG SGP CONSTRUCTION:")
            for leg in analysis["six_leg_sgp"]:
                print("  {leg['leg']}. {leg['selection']} ({leg['odds']})")
                print(f"     Probability: {leg['probability']} | Confidence: {leg['confidence']}")
                print("     Correlation Group: {leg['correlation_group']}")
                print()

            # Statistical analysis
            print("📈 STATISTICAL ANALYSIS:")
            anal = analysis["sgp_analysis"]
            print(f"  Individual Probabilities: {', '.join(anal['individual_probabilities'])}")
            print("  Raw Combined: {anal['raw_combined_probability']}")
            print("  Correlation Factor: {anal['correlation_adjustment']}")
            print("  Final Probability: {anal['final_probability']}")
            print("  Fair Value Odds: {anal['fair_value_odds']}")
            print("  Market Estimate: {anal['estimated_market_odds']}")
            print("  Kelly Sizing: {anal['kelly_sizing']}")

            # Correlation breakdown
            print("\n🔗 CORRELATION ANALYSIS:")
            corr = analysis["correlation_breakdown"]
            print("  Seattle Stack: {corr['seattle_offense_stack']}")
            print("  Total Runs Boost: {corr['total_runs_correlation']}")
            print("  Key Synergies:")
            for _synergy in corr["key_synergies"]:
                print("    • {synergy}")

            # Strategy
            print("\n🎯 STRATEGIC REASONING:")
            for _reason in analysis["strategic_reasoning"]:
                print("  • {reason}")

            # Risk assessment
            print("\n⚠️ RISK ASSESSMENT:")
            risk = analysis["risk_assessment"]
            print("  Primary Risks:")
            for _r in risk["primary_risks"]:
                print("    • {r}")
            print("  Mitigation:")
            for _m in risk["risk_mitigation"]:
                print("    • {m}")
            print("  Correlation Risk: {risk['correlation_risk']}")

            # Recommendation
            print("\n🏆 RECOMMENDATION:")
            analysis["recommendation"]
            print("  Action: {rec['action']}")
            print("  Reasoning: {rec['reasoning']}")
            print("  Unit Size: {rec['optimal_unit_size']}")
            print("  Confidence: {rec['confidence_level']}")
            print("  Market Target: {rec['market_target']}")

            print("=" * 75)

        if args.save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"C:/EQ12/logs/6leg_sgp_det_sea_{timestamp}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2)
            print("\n6-Leg SGP analysis saved to: {filename}")

    except Exception:
        print("Error building 6-leg SGP: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
