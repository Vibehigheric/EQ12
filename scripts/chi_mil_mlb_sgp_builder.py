#!/usr/bin/env python3
"""
EQ12 CHI vs MIL MLB Same Game Parlay Builder
Target: 10x+ ROI on $8 stake (need +1000 odds or better)
Game: Chicago Cubs vs Milwaukee Brewers
"""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_chi_mil_mlb_sgp():
    """Create a MLB Same Game Parlay for CHI vs MIL targeting 10x+ ROI"""

    # Game analysis for CHI vs MIL (division rivals, potential playoff implications)
    game_info = {
        "matchup": "Chicago Cubs @ Milwaukee Brewers",
        "date": "2025-10-06",
        "game_type": "MLB Division Rival Game",
        "analysis": {
            "cubs_strength": "Young offense, improved pitching, divisional familiarity",
            "brewers_strength": "American Family Field advantage, strong bullpen, clutch hitting",
            "weather": "October in Milwaukee - cooler temps, potential wind factor",
            "key_factors": [
                "Division rivalry",
                "Home field advantage",
                "Late season implications",
                "Bullpen depth",
            ],
        },
    }

    # MLB SGP Strategy: Target division rival dynamics and home field patterns
    # Need +1000 odds for 10x ROI on $8 stake ($80 payout)

    sgp_legs = [
        {
            "leg": 1,
            "selection": "Milwaukee Brewers ML",
            "bet_type": "moneyline",
            "rationale": "Home field vs Cubs, strong in division matchups",
            "estimated_odds": "-125",
            "confidence": "MEDIUM-HIGH",
        },
        {
            "leg": 2,
            "selection": "Game Total Over 8.5 Runs",
            "bet_type": "total",
            "rationale": "Division rivals know each other, offensive explosion likely",
            "estimated_odds": "+110",
            "confidence": "MEDIUM",
        },
        {
            "leg": 3,
            "selection": "Christian Yelich Over 1.5 Total Bases",
            "bet_type": "player_prop",
            "rationale": "Home hero vs Cubs pitching, knows their tendencies",
            "estimated_odds": "+115",
            "confidence": "MEDIUM-HIGH",
        },
        {
            "leg": 4,
            "selection": "Cody Bellinger Over 1.5 Total Bases",
            "bet_type": "player_prop",
            "rationale": "Ex-Dodger performs in big spots, good vs Brewers pitching",
            "estimated_odds": "+125",
            "confidence": "MEDIUM",
        },
        {
            "leg": 5,
            "selection": "First 5 Innings Over 4.5 Runs",
            "bet_type": "first_5_total",
            "rationale": "Early offense, starters get hit hard in division games",
            "estimated_odds": "+105",
            "confidence": "MEDIUM",
        },
        {
            "leg": 6,
            "selection": "Both Teams to Score 4+ Runs",
            "bet_type": "team_total",
            "rationale": "High-scoring division affair, both offenses produce",
            "estimated_odds": "+170",
            "confidence": "MEDIUM",
        },
        {
            "leg": 7,
            "selection": "Game Decided by 1 Run",
            "bet_type": "special",
            "rationale": "Division rivals, tight games, late drama expected",
            "estimated_odds": "+220",
            "confidence": "LOW-MEDIUM",
        },
        {
            "leg": 8,
            "selection": "Milwaukee Wins & Over 8.5 Runs",
            "bet_type": "combo",
            "rationale": "Brewers win a shootout at home vs Cubs",
            "estimated_odds": "+185",
            "confidence": "MEDIUM",
        },
    ]

    # Calculate parlay odds (approximate)
    def american_to_decimal(odds_str):
        odds = int(odds_str.replace("+", "").replace("-", ""))
        if odds_str.startswith("-"):
            return 1 + (100 / odds)
        else:
            return 1 + (odds / 100)

    decimal_odds = 1.0
    for leg in sgp_legs:
        decimal_odds *= american_to_decimal(leg["estimated_odds"])

    american_odds = (int((decimal_odds - 1) * 100) if decimal_odds <
                     2 else int((decimal_odds - 1) * 100))

    sgp_analysis = {
        "strategy": "HIGH_SCORING_BREWERS_HOME_WIN",
        "target_odds": "+1000 or better",
        "estimated_combined_odds": f"+{american_odds}",
        "estimated_decimal_odds": round(decimal_odds, 2),
        "stake": 8,
        "potential_payout": round(8 * decimal_odds, 2),
        "roi_multiple": round(decimal_odds, 1),
        "correlation_analysis": {
            "positive_correlations": [
                "Brewers ML + Yelich performance (home field magic)",
                "Over totals + both player props (offensive explosion)",
                "F5 over + game over (consistent high scoring)",
                "1-run game + division rivalry (classic tight finish)",
                "Brewers win + over combo (home team shootout win)",
            ],
            "risk_factors": [
                "Weather turns - wind could kill offense",
                "Bullpen dominance shuts down late scoring",
                "Starting pitcher gem ruins over bets",
                "Cubs surprise road performance",
                "Key player sits for rest",
            ],
        },
        "division_factors": {
            "familiarity": "Teams know each other - could go either way",
            "motivation": "Late season positioning important for both",
            "home_field": "Brewers historically strong at American Family Field",
            "recent_meetings": "Check head-to-head record this season",
        },
    }

    # Enhanced betting slip for MLB division game
    betting_slip = {
        "parlay_id": f"chi_mil_mlb_sgp_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
        "game": game_info,
        "legs": sgp_legs,
        "analysis": sgp_analysis,
        "betting_instructions": {
            "shop_lines": "Compare MLB SGP odds across DraftKings, FanDuel, BetMGM, Caesars",
            "timing": "Place bet 1-2 hours before first pitch for optimal odds",
            "weather_check": "Monitor Milwaukee weather - wind affects American Family Field",
            "lineup_check": "Verify both lineups 90 minutes before game time",
            "bankroll_management": "Maximum 1-2% of bankroll on this aggressive 8-leg bet",
        },
        "mlb_specific_factors": {
            "starting_pitchers": "Confirm both SP status - late scratches kill SGPs",
            "bullpen_status": "Check recent usage for both bullpens",
            "weather_conditions": "Wind direction crucial at American Family Field",
            "division_history": "Cubs-Brewers always competitive, check recent H2H",
            "rest_factors": "Late season - check for rested/tired players",
        },
        "risk_assessment": {
            "probability_estimate": "3-6% chance of hitting all 8 legs",
            "ev_analysis": "Positive EV if getting +1500 or better",
            "max_acceptable_odds": "+1000 (minimum for 10x+ ROI)",
            "recommendation": "PROCEED if odds +1500 or better, CONSIDER if +1000-1499, PASS if worse than +1000",
        },
    }

    return betting_slip


def format_chi_mil_betting_slip(slip):
    """Format the CHI vs MIL betting slip for easy reading"""

    output = []
    output.append("⚾ EQ12 CHI vs MIL MLB SAME GAME PARLAY ⚾")
    output.append("=" * 58)
    output.append(f"Game: {slip['game']['matchup']}")
    output.append(f"Type: {slip['game']['game_type']}")
    output.append(f"Target: 10x+ ROI on ${slip['analysis']['stake']} stake")
    output.append(f"Est. Odds: {slip['analysis']['estimated_combined_odds']}")
    output.append(f"Potential Payout: ${slip['analysis']['potential_payout']}")
    output.append("")

    output.append("📋 PARLAY LEGS (8-LEG AGGRESSIVE):")
    for i, leg in enumerate(slip["legs"], 1):
        output.append(f"{i}. {leg['selection']}")
        output.append(
            f"   Odds: {
                leg['estimated_odds']} | Confidence: {
                leg['confidence']}")
        output.append(f"   Logic: {leg['rationale']}")
        output.append("")

    output.append("🎯 STRATEGY ANALYSIS:")
    output.append(f"• Strategy: {slip['analysis']['strategy']}")
    output.append(
        f"• Est. Win Probability: {
            slip['risk_assessment']['probability_estimate']}")
    output.append(
        f"• Minimum Acceptable Odds: {
            slip['risk_assessment']['max_acceptable_odds']}")
    output.append("")

    output.append("⚾ DIVISION RIVALRY CORRELATIONS:")
    for corr in slip["analysis"]["correlation_analysis"]["positive_correlations"]:
        output.append(f"• {corr}")
    output.append("")

    output.append("🚨 DIVISION GAME RISKS:")
    for risk in slip["analysis"]["correlation_analysis"]["risk_factors"]:
        output.append(f"• {risk}")
    output.append("")

    output.append("🏟️ AMERICAN FAMILY FIELD FACTORS:")
    for factor, desc in slip["analysis"]["division_factors"].items():
        output.append(f"• {factor.replace('_', ' ').title()}: {desc}")
    output.append("")

    output.append("🔍 CRITICAL MLB CHECKS:")
    for factor, desc in slip["mlb_specific_factors"].items():
        output.append(f"• {factor.replace('_', ' ').title()}: {desc}")
    output.append("")

    output.append("💡 BETTING INSTRUCTIONS:")
    output.append(f"• {slip['betting_instructions']['shop_lines']}")
    output.append(f"• {slip['betting_instructions']['timing']}")
    output.append(f"• {slip['betting_instructions']['weather_check']}")
    output.append(f"• {slip['betting_instructions']['lineup_check']}")
    output.append("")

    output.append("⚠️ RISK WARNING:")
    output.append("This is an 8-leg parlay with 3-6% win probability")
    output.append("Only bet money you can afford to completely lose")
    output.append("Consider smaller 4-5 leg versions for better odds")
    output.append("")

    output.append(
        f"⚾ FINAL RECOMMENDATION: {
            slip['risk_assessment']['recommendation']}")
    output.append("")
    output.append("Cubs vs Brewers - Division rivalry magic! ⚾🧀🐻")

    return "\n".join(output)


def main():
    """Generate the CHI vs MIL MLB SGP"""

    logger.info("Generating CHI vs MIL MLB Same Game Parlay targeting 10x+ ROI")

    # Create the SGP
    betting_slip = create_chi_mil_mlb_sgp()

    # Save to logs
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    # Save JSON analysis
    json_file = logs_dir / f"chi_mil_mlb_sgp_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(betting_slip, f, indent=2, ensure_ascii=False)

    # Save readable betting slip
    slip_file = logs_dir / f"chi_mil_mlb_sgp_betting_slip_{timestamp}.txt"
    with open(slip_file, "w", encoding="utf-8") as f:
        f.write(format_chi_mil_betting_slip(betting_slip))

    # Print to console
    print(format_chi_mil_betting_slip(betting_slip))

    logger.info(f"MLB betting slip saved to: {slip_file}")
    logger.info(f"Analysis saved to: {json_file}")

    return betting_slip


if __name__ == "__main__":
    main()
