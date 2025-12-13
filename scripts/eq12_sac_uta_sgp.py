#!/usr/bin/env python3
"""
EQ12 High-Odds SGP Builder - Sacramento Kings @ Utah Jazz
Custom moonshot parlay builder for SAC @ UTA tonight.
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

def american_to_decimal(american_odds: int) -> float:
    """Convert American odds to decimal."""
    if american_odds > 0:
        return (american_odds / 100.0) + 1.0
    else:
        return (100.0 / abs(american_odds)) + 1.0

def build_sac_uta_sgp():
    """Build high-odds SGPs for SAC @ UTA."""
    
    print("\n" + "="*80)
    print("🚀 EQ12 HIGH-ODDS SGP BUILDER")
    print("="*80)
    print(f"Game: Sacramento Kings @ Utah Jazz")
    print(f"Tonight: 9:40 PM ET / 6:40 PM PT (Same time as PHO/OKC)")
    print(f"Stake: $5.00")
    print(f"Target Payout: $500.00 - $1000.00")
    print("="*80)
    
    # Current odds (from API scan)
    print("\n📊 CURRENT ODDS:")
    print("   Moneyline: UTA -146 / SAC +124")
    print("   Spread: UTA -3.0 (-110) / SAC +3.0 (-114)")
    print("   Total: Over 242.5 (-110) / Under 242.5 (-110)")
    print("")
    print("📈 GAME ANALYSIS:")
    print("   - Utah slight favorite at home (-146)")
    print("   - Sacramento competitive underdog (+124)")
    print("   - Close spread (only 3 points)")
    print("   - High total (242.5 - both teams can score)")
    
    # Build SGP options
    sgps = []
    
    # OPTION 1: Sacramento upset (best odds)
    legs_1 = [
        {"pick": "SAC Moneyline", "odds": +124, "desc": "Kings win outright"},
        {"pick": "SAC +3.0", "odds": -114, "desc": "Kings cover spread"},
        {"pick": "Over 242.5", "odds": -110, "desc": "High scoring game"}
    ]
    decimal_1 = american_to_decimal(124) * american_to_decimal(-114) * american_to_decimal(-110)
    payout_1 = 5.0 * decimal_1
    
    sgps.append({
        "name": "🔥 MOONSHOT: Sacramento Upset Special",
        "strategy": "Aggressive underdog play - Kings win on the road",
        "legs": legs_1,
        "parlay_odds_decimal": round(decimal_1, 2),
        "parlay_odds_american": int((decimal_1 - 1) * 100),
        "stake": 5.0,
        "payout": round(payout_1, 2),
        "profit": round(payout_1 - 5.0, 2),
        "win_prob": round((1/decimal_1)*100, 2)
    })
    
    # OPTION 2: Utah dominates (safer)
    legs_2 = [
        {"pick": "UTA Moneyline", "odds": -146, "desc": "Jazz win at home"},
        {"pick": "UTA -3.0", "odds": -110, "desc": "Jazz win by 4+"},
        {"pick": "Under 242.5", "odds": -110, "desc": "Defense controls tempo"}
    ]
    decimal_2 = american_to_decimal(-146) * american_to_decimal(-110) * american_to_decimal(-110)
    payout_2 = 5.0 * decimal_2
    
    sgps.append({
        "name": "🛡️ SAFE: Utah Home Win",
        "strategy": "Conservative favorite play - Jazz defend home court",
        "legs": legs_2,
        "parlay_odds_decimal": round(decimal_2, 2),
        "parlay_odds_american": int((decimal_2 - 1) * 100) if decimal_2 >= 2 else int(-100/(decimal_2 - 1)),
        "stake": 5.0,
        "payout": round(payout_2, 2),
        "profit": round(payout_2 - 5.0, 2),
        "win_prob": round((1/decimal_2)*100, 2)
    })
    
    # OPTION 3: Kings cover but lose
    legs_3 = [
        {"pick": "UTA Moneyline", "odds": -146, "desc": "Jazz win"},
        {"pick": "SAC +3.0", "odds": -114, "desc": "Kings keep it close"},
        {"pick": "Over 242.5", "odds": -110, "desc": "Both teams score"}
    ]
    decimal_3 = american_to_decimal(-146) * american_to_decimal(-114) * american_to_decimal(-110)
    payout_3 = 5.0 * decimal_3
    
    sgps.append({
        "name": "⚖️ BALANCED: Close Utah Win",
        "strategy": "Moderate - Jazz win but Kings cover spread",
        "legs": legs_3,
        "parlay_odds_decimal": round(decimal_3, 2),
        "parlay_odds_american": int((decimal_3 - 1) * 100) if decimal_3 >= 2 else int(-100/(decimal_3 - 1)),
        "stake": 5.0,
        "payout": round(payout_3, 2),
        "profit": round(payout_3 - 5.0, 2),
        "win_prob": round((1/decimal_3)*100, 2)
    })
    
    # OPTION 4: High-scoring Sacramento win (HIGHEST ODDS)
    legs_4 = [
        {"pick": "SAC Moneyline", "odds": +124, "desc": "Kings win"},
        {"pick": "Over 242.5", "odds": -110, "desc": "High scoring"},
        {"pick": "SAC +3.0", "odds": -114, "desc": "Kings cover"},
        {"pick": "Over 242.5 (again)", "odds": -110, "desc": "Shootout game"}
    ]
    decimal_4 = american_to_decimal(124) * american_to_decimal(-110) * american_to_decimal(-114) * american_to_decimal(-110)
    payout_4 = 5.0 * decimal_4
    
    sgps.append({
        "name": "💎 JACKPOT: Sacramento Shootout Win (4-leg)",
        "strategy": "High-risk 4-leg parlay - Kings win high-scoring game",
        "legs": legs_4,
        "parlay_odds_decimal": round(decimal_4, 2),
        "parlay_odds_american": int((decimal_4 - 1) * 100),
        "stake": 5.0,
        "payout": round(payout_4, 2),
        "profit": round(payout_4 - 5.0, 2),
        "win_prob": round((1/decimal_4)*100, 2)
    })
    
    # OPTION 5: 5-leg MEGA parlay
    legs_5 = [
        {"pick": "SAC Moneyline", "odds": +124, "desc": "Kings win"},
        {"pick": "SAC +3.0", "odds": -114, "desc": "Kings cover"},
        {"pick": "Over 242.5", "odds": -110, "desc": "High scoring"},
        {"pick": "UTA -3.0", "odds": -110, "desc": "Jazz cover (if they win)"},
        {"pick": "Over 242.5 (again)", "odds": -110, "desc": "Shootout"}
    ]
    decimal_5 = american_to_decimal(124) * american_to_decimal(-114) * american_to_decimal(-110) * american_to_decimal(-110) * american_to_decimal(-110)
    payout_5 = 5.0 * decimal_5
    
    sgps.append({
        "name": "🌟 MEGA MOONSHOT: 5-Leg Extreme (HIGHEST PAYOUT)",
        "strategy": "EXTREME RISK - 5 legs for maximum payout",
        "legs": legs_5,
        "parlay_odds_decimal": round(decimal_5, 2),
        "parlay_odds_american": int((decimal_5 - 1) * 100),
        "stake": 5.0,
        "payout": round(payout_5, 2),
        "profit": round(payout_5 - 5.0, 2),
        "win_prob": round((1/decimal_5)*100, 2)
    })
    
    # Display
    print("\n" + "="*80)
    print("🎯 SGP OPTIONS (Sorted by Payout)")
    print("="*80)
    
    # Sort by payout
    sgps_sorted = sorted(sgps, key=lambda x: x['payout'], reverse=True)
    
    for sgp in sgps_sorted:
        print_sgp(sgp)
    
    print("\n" + "="*80)
    print("💡 COMPARISON: SAC/UTA vs PHO/OKC")
    print("="*80)
    print("✅ SAC/UTA is BETTER for moonshots:")
    print("   - Sacramento only +124 (vs Phoenix +700)")
    print("   - Closer spread (3 points vs 14.5)")
    print("   - More realistic upset potential")
    print("   - Higher total (242.5 vs 223.5)")
    print("")
    print("🎯 BEST OPTIONS FOR $500-1000 TARGET:")
    best = sgps_sorted[0]
    print(f"   1. {best['name']}")
    print(f"      Payout: ${best['payout']:.2f}")
    print(f"      Still needs ${500 - best['profit']:.2f} more to hit $500")
    print("")
    print("💡 STRATEGY TO HIT $500:")
    print("   Option A: Bet $5 on SAC upset → Win $14 → Reinvest in next game")
    print("   Option B: Split $5 across SAC/UTA + PHO/OKC underdogs")
    print("   Option C: Wait for bigger underdog (+300+) and parlay")
    print("="*80)
    
    print("\n⚠️  RISK WARNINGS:")
    print("   1. 5-leg parlays have <1% win probability")
    print("   2. Correlated bets may be rejected by sportsbooks")
    print("   3. $5 to $500-1000 requires 100:1+ odds (very rare)")
    print("   4. Responsible gambling: Only bet what you can lose")
    print("   5. This is analysis only - not financial advice")
    print("="*80)
    
    # Save report
    output = Path("../reports/sgp_sac_uta_high_odds.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output, 'w') as f:
        json.dump({
            'game': 'Sacramento Kings @ Utah Jazz',
            'stake': 5.0,
            'target_payout': 500.0,
            'required_odds': 100.0,
            'sgps': sgps_sorted,
            'comparison': {
                'vs_pho_okc': 'SAC/UTA better for moonshots - smaller underdog more likely to hit',
                'best_strategy': 'Sacramento upset or 4-5 leg parlay'
            },
            'generated_at': datetime.now(timezone.utc).isoformat()
        }, f, indent=2)
    
    print(f"\n✅ Full analysis saved: {output}")

def print_sgp(sgp):
    """Print formatted SGP."""
    print(f"\n{sgp['name']}")
    print(f"{'-'*80}")
    print(f"Strategy: {sgp['strategy']}")
    print(f"Odds: {sgp['parlay_odds_american']:+d} ({sgp['parlay_odds_decimal']:.2f}x)")
    print(f"Stake: ${sgp['stake']:.2f}")
    print(f"Payout: ${sgp['payout']:.2f}")
    print(f"Profit: ${sgp['profit']:.2f} 💰")
    print(f"Win Probability: ~{sgp['win_prob']:.1f}%")
    print(f"\nLegs ({len(sgp['legs'])}):")
    for i, leg in enumerate(sgp['legs'], 1):
        print(f"   {i}. {leg['pick']} ({leg['odds']:+d}) - {leg['desc']}")

if __name__ == '__main__':
    build_sac_uta_sgp()
