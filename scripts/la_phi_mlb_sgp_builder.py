#!/usr/bin/env python3
"""
EQ12 LA vs PHI MLB Same Game Parlay Builder
Target: 10x+ ROI on $8 stake (need +1000 odds or better)
Game: Los Angeles (Angels/Dodgers) vs Philadelphia Phillies
"""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_la_phi_mlb_sgp():
    """Create a MLB Same Game Parlay for LA vs PHI targeting 10x+ ROI"""

    # Game analysis for LA vs PHI (assuming Dodgers vs Phillies playoff scenario)
    game_info = {
        "matchup": "Los Angeles Dodgers @ Philadelphia Phillies",
        "date": "2025-10-06",
        "game_type": "MLB Postseason",
        "analysis": {
            "dodgers_strength": "Elite rotation, Mookie/Freeman power, playoff experience",
            "phillies_strength": "Home field advantage, Harper clutch hitting, bullpen depth",
            "weather": "October baseball - cooler temps favor pitchers",
            "key_factors": [
                "Starting pitcher matchup",
                "Bullpen usage",
                "Home field advantage",
                "Playoff pressure",
            ],
        },
    }

    # MLB SGP Strategy: Target correlated outcomes with pitcher props and totals
    # Need +1000 odds for 10x ROI on $8 stake ($80 payout)

    sgp_legs = [
        {
            "leg": 1,
            "selection": "Philadelphia Phillies ML",
            "bet_type": "moneyline",
            "rationale": "Home field advantage in playoffs crucial, Phillies desperate",
            "estimated_odds": "+130",
            "confidence": "MEDIUM-HIGH",
        },
        {
            "leg": 2,
            "selection": "Game Total Under 7.5 Runs",
            "bet_type": "total",
            "rationale": "Playoff pitching, cooler weather, tight defense",
            "estimated_odds": "-115",
            "confidence": "HIGH",
        },
        {
            "leg": 3,
            "selection": "Bryce Harper Over 1.5 Total Bases",
            "bet_type": "player_prop",
            "rationale": "Home playoff hero, clutch performer vs Dodger pitching",
            "estimated_odds": "+105",
            "confidence": "MEDIUM-HIGH",
        },
        {
            "leg": 4,
            "selection": "Mookie Betts Under 1.5 Total Bases",
            "bet_type": "player_prop",
            "rationale": "Phillies pitching targets Betts, road playoff pressure",
            "estimated_odds": "+120",
            "confidence": "MEDIUM",
        },
        {
            "leg": 5,
            "selection": "First 5 Innings Under 4.5 Runs",
            "bet_type": "first_5_total",
            "rationale": "Strong starting pitching, teams feel each other out early",
            "estimated_odds": "-110",
            "confidence": "HIGH",
        },
        {
            "leg": 6,
            "selection": "Game Goes Extra Innings",
            "bet_type": "special",
            "rationale": "Tight playoff game, both bullpens strong, low-scoring affair",
            "estimated_odds": "+280",
            "confidence": "LOW-MEDIUM",
        },
        {
            "leg": 7,
            "selection": "Both Teams Score Under 3.5 Runs",
            "bet_type": "team_total",
            "rationale": "Pitcher's duel, playoff pressure, defensive focused",
            "estimated_odds": "+140",
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

    american_odds = (
        int((decimal_odds - 1) * 100) if decimal_odds < 2 else int((decimal_odds - 1) * 100)
    )

    sgp_analysis = {
        "strategy": "LOW_SCORING_PHILLIES_HOME_WIN",
        "target_odds": "+1000 or better",
        "estimated_combined_odds": f"+{american_odds}",
        "estimated_decimal_odds": round(decimal_odds, 2),
        "stake": 8,
        "potential_payout": round(8 * decimal_odds, 2),
        "roi_multiple": round(decimal_odds, 1),
        "correlation_analysis": {
            "positive_correlations": [
                "Phillies ML + Harper performance (home hero)",
                "Under totals + extra innings (pitcher's duel)",
                "F5 under + game under (consistent low scoring)",
                "Betts under + Phillies ML (Dodgers struggle)",
            ],
            "risk_factors": [
                "One big inning could kill multiple under bets",
                "Weather changes (wind helping hitters)",
                "Bullpen blowup in late innings",
                "Starting pitcher early exit",
            ],
        },
        "alternate_scenarios": {
            "high_confidence_5_leg": "Remove extra innings bet for safer odds",
            "conservative_4_leg": "Remove Betts under and extra innings",
            "aggressive_add": "Add specific pitcher strikeout props",
        },
    }

    # Enhanced betting slip for MLB
    betting_slip = {
        "parlay_id": f"la_phi_mlb_sgp_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
        "game": game_info,
        "legs": sgp_legs,
        "analysis": sgp_analysis,
        "betting_instructions": {
            "shop_lines": "Compare MLB SGP odds across DraftKings, FanDuel, BetMGM, Caesars",
            "timing": "Place bet 1-2 hours before first pitch for best odds",
            "weather_check": "Monitor wind conditions - affects totals significantly",
            "lineup_check": "Verify starting lineups 90 minutes before game",
            "bankroll_management": "Maximum 1-2% of total bankroll on this high-variance bet",
        },
        "mlb_specific_factors": {
            "starting_pitchers": "Verify SP status - changes everything",
            "bullpen_usage": "Check recent bullpen workload for both teams",
            "weather_impact": "Wind direction crucial for over/under bets",
            "playoff_pressure": "Home team historically performs better in elimination games",
            "umpire_factor": "Check home plate umpire's strike zone tendencies",
        },
        "risk_assessment": {
            "probability_estimate": "5-8% chance of hitting all 7 legs",
            "ev_analysis": "Positive EV if getting +1200 or better",
            "max_acceptable_odds": "+800 (still 10x+ ROI)",
            "recommendation": "PROCEED if odds +1000 or better, CONSIDER if +800-999, PASS if worse than +800",
        },
    }

    return betting_slip


def format_mlb_betting_slip(slip):
    """Format the MLB betting slip for easy reading"""

    output = []
    output.append("⚾ EQ12 LA vs PHI MLB SAME GAME PARLAY ⚾")
    output.append("=" * 55)
    output.append(f"Game: {slip['game']['matchup']}")
    output.append(f"Type: {slip['game']['game_type']}")
    output.append(f"Target: 10x+ ROI on ${slip['analysis']['stake']} stake")
    output.append(f"Est. Odds: {slip['analysis']['estimated_combined_odds']}")
    output.append(f"Potential Payout: ${slip['analysis']['potential_payout']}")
    output.append("")

    output.append("📋 PARLAY LEGS:")
    for i, leg in enumerate(slip["legs"], 1):
        output.append(f"{i}. {leg['selection']}")
        output.append(f"   Odds: {leg['estimated_odds']} | Confidence: {leg['confidence']}")
        output.append(f"   Logic: {leg['rationale']}")
        output.append("")

    output.append("🎯 STRATEGY ANALYSIS:")
    output.append(f"• Strategy: {slip['analysis']['strategy']}")
    output.append(f"• Est. Win Probability: {slip['risk_assessment']['probability_estimate']}")
    output.append(f"• Minimum Acceptable Odds: {slip['risk_assessment']['max_acceptable_odds']}")
    output.append("")

    output.append("⚾ KEY MLB CORRELATIONS:")
    for corr in slip["analysis"]["correlation_analysis"]["positive_correlations"]:
        output.append(f"• {corr}")
    output.append("")

    output.append("🚨 BASEBALL RISK FACTORS:")
    for risk in slip["analysis"]["correlation_analysis"]["risk_factors"]:
        output.append(f"• {risk}")
    output.append("")

    output.append("🔍 MLB-SPECIFIC CHECKS:")
    for factor, desc in slip["mlb_specific_factors"].items():
        output.append(f"• {factor.replace('_', ' ').title()}: {desc}")
    output.append("")

    output.append("💡 BETTING INSTRUCTIONS:")
    output.append(f"• {slip['betting_instructions']['shop_lines']}")
    output.append(f"• {slip['betting_instructions']['timing']}")
    output.append(f"• {slip['betting_instructions']['weather_check']}")
    output.append(f"• {slip['betting_instructions']['lineup_check']}")
    output.append("")

    output.append("🎯 ALTERNATE STRATEGIES:")
    for alt, desc in slip["analysis"]["alternate_scenarios"].items():
        output.append(f"• {alt.replace('_', ' ').title()}: {desc}")
    output.append("")

    output.append(f"⚾ FINAL RECOMMENDATION: {slip['risk_assessment']['recommendation']}")
    output.append("")
    output.append("Play ball! ⚾🍀")

    return "\n".join(output)


def main():
    """Generate the LA vs PHI MLB SGP"""

    logger.info("Generating LA vs PHI MLB Same Game Parlay targeting 10x+ ROI")

    # Create the SGP
    betting_slip = create_la_phi_mlb_sgp()

    # Save to logs
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    # Save JSON analysis
    json_file = logs_dir / f"la_phi_mlb_sgp_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(betting_slip, f, indent=2, ensure_ascii=False)

    # Save readable betting slip
    slip_file = logs_dir / f"la_phi_mlb_sgp_betting_slip_{timestamp}.txt"
    with open(slip_file, "w", encoding="utf-8") as f:
        f.write(format_mlb_betting_slip(betting_slip))

    # Print to console
    print(format_mlb_betting_slip(betting_slip))

    logger.info(f"MLB betting slip saved to: {slip_file}")
    logger.info(f"Analysis saved to: {json_file}")

    return betting_slip


if __name__ == "__main__":
    main()
