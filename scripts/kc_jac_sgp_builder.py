#!/usr/bin/env python3
"""
EQ12 KC vs JAC Same Game Parlay Builder
Target: 10x+ ROI on $8 stake (need +1000 odds or better)
Game: Kansas City Chiefs vs Jacksonville Jaguars
"""

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_kc_jac_sgp():
    """Create a Same Game Parlay for KC vs JAC targeting 10x+ ROI"""

    # Game analysis for KC vs JAC
    game_info = {
        "matchup": "Kansas City Chiefs @ Jacksonville Jaguars",
        "date": "2025-10-06",
        "analysis": {
            "chiefs_strength": "Elite offense, Mahomes magic, strong defense",
            "jaguars_weakness": "Inconsistent offense, road struggles",
            "weather": "Dome game (favorable for passing)",
            "key_factors": [
                "Mahomes vs JAC secondary",
                "KC defense vs Lawrence",
                "Home field advantage",
            ],
        },
    }

    # SGP Strategy: Target correlated outcomes favoring Chiefs dominance
    # Need +1000 odds for 10x ROI on $8 stake ($80 payout)

    sgp_legs = [
        {
            "leg": 1,
            "selection": "Kansas City Chiefs -7.5",
            "bet_type": "spread",
            "rationale": "Chiefs should dominate at home, JAC struggles on road",
            "estimated_odds": "-110",
            "confidence": "HIGH",
        },
        {
            "leg": 2,
            "selection": "Patrick Mahomes Over 2.5 Passing TDs",
            "bet_type": "player_prop",
            "rationale": "Mahomes excels vs weak secondaries, dome conditions",
            "estimated_odds": "+120",
            "confidence": "HIGH",
        },
        {
            "leg": 3,
            "selection": "Travis Kelce Over 65.5 Receiving Yards",
            "bet_type": "player_prop",
            "rationale": "JAC struggles covering TEs, Mahomes security blanket",
            "estimated_odds": "-115",
            "confidence": "MEDIUM-HIGH",
        },
        {
            "leg": 4,
            "selection": "Game Total Under 48.5",
            "bet_type": "total",
            "rationale": "KC controls clock, JAC offensive struggles limit scoring",
            "estimated_odds": "-110",
            "confidence": "MEDIUM",
        },
        {
            "leg": 5,
            "selection": "Trevor Lawrence Under 1.5 Passing TDs",
            "bet_type": "player_prop",
            "rationale": "KC defense at home, JAC road offensive struggles",
            "estimated_odds": "+130",
            "confidence": "MEDIUM",
        },
        {
            "leg": 6,
            "selection": "Kansas City 1st Half -4.5",
            "bet_type": "first_half_spread",
            "rationale": "Chiefs start fast at home, JAC slow starts on road",
            "estimated_odds": "-105",
            "confidence": "MEDIUM-HIGH",
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
        "strategy": "CORRELATED_CHIEFS_DOMINANCE",
        "target_odds": "+1000 or better",
        "estimated_combined_odds": f"+{american_odds}",
        "estimated_decimal_odds": round(decimal_odds, 2),
        "stake": 8,
        "potential_payout": round(8 * decimal_odds, 2),
        "roi_multiple": round(decimal_odds, 1),
        "correlation_analysis": {
            "positive_correlations": [
                "Chiefs spread + Mahomes TDs (blowout scenario)",
                "Chiefs 1H spread + game spread (early lead)",
                "Under total + Lawrence under TDs (defensive game)",
            ],
            "risk_factors": [
                "JAC garbage time TDs could hurt under bets",
                "Weather changes (though dome game)",
                "Key injury updates before game",
            ],
        },
        "hedge_opportunities": {
            "live_hedge": "If Chiefs up big early, hedge JAC comeback",
            "pre_game_hedge": "Consider Chiefs TT over as insurance",
        },
    }

    # Enhanced betting slip
    betting_slip = {
        "parlay_id": f"kc_jac_sgp_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
        "game": game_info,
        "legs": sgp_legs,
        "analysis": sgp_analysis,
        "betting_instructions": {
            "shop_lines": "Compare SGP odds across DraftKings, FanDuel, BetMGM",
            "timing": "Place bet 2-3 hours before kickoff for best odds",
            "bankroll_management": "This is 1-2% of bankroll max",
            "success_criteria": "Need +1000 or better to meet 10x target",
        },
        "risk_assessment": {
            "probability_estimate": "8-12% chance of hitting all legs",
            "ev_analysis": "Positive EV if getting +1100 or better",
            "max_acceptable_odds": "+900 (still 9x+ ROI)",
            "recommendation": "PROCEED if odds +1000 or better, PASS if worse than +900",
        },
    }

    return betting_slip


def format_betting_slip(slip):
    """Format the betting slip for easy reading"""

    output = []
    output.append("🏈 EQ12 KC vs JAC SAME GAME PARLAY 🏈")
    output.append("=" * 50)
    output.append(f"Game: {slip['game']['matchup']}")
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

    output.append("⚠️ KEY CORRELATIONS:")
    for corr in slip["analysis"]["correlation_analysis"]["positive_correlations"]:
        output.append(f"• {corr}")
    output.append("")

    output.append("🚨 RISK FACTORS:")
    for risk in slip["analysis"]["correlation_analysis"]["risk_factors"]:
        output.append(f"• {risk}")
    output.append("")

    output.append("💡 BETTING INSTRUCTIONS:")
    output.append(f"• {slip['betting_instructions']['shop_lines']}")
    output.append(f"• {slip['betting_instructions']['timing']}")
    output.append(f"• {slip['betting_instructions']['bankroll_management']}")
    output.append("")

    output.append(f"🎲 FINAL RECOMMENDATION: {slip['risk_assessment']['recommendation']}")
    output.append("")
    output.append("Good luck! 🍀")

    return "\n".join(output)


def main():
    """Generate the KC vs JAC SGP"""

    logger.info("Generating KC vs JAC Same Game Parlay targeting 10x+ ROI")

    # Create the SGP
    betting_slip = create_kc_jac_sgp()

    # Save to logs
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    # Save JSON analysis
    json_file = logs_dir / f"kc_jac_sgp_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(betting_slip, f, indent=2, ensure_ascii=False)

    # Save readable betting slip
    slip_file = logs_dir / f"kc_jac_sgp_betting_slip_{timestamp}.txt"
    with open(slip_file, "w", encoding="utf-8") as f:
        f.write(format_betting_slip(betting_slip))

    # Print to console
    print(format_betting_slip(betting_slip))

    logger.info(f"Betting slip saved to: {slip_file}")
    logger.info(f"Analysis saved to: {json_file}")

    return betting_slip


if __name__ == "__main__":
    main()
