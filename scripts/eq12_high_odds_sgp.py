#!/usr/bin/env python3
"""
EQ12 High-Odds SGP Builder - Build extreme parlays for moonshot bets
Targets 100x+ odds for turning small stakes into large payouts.
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import requests

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class HighOddsSGPBuilder:
    """Build high-risk, high-reward SGPs."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.the-odds-api.com/v4"
    
    def american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal."""
        if american_odds > 0:
            return (american_odds / 100.0) + 1.0
        else:
            return (100.0 / abs(american_odds)) + 1.0
    
    def build_aggressive_sgp(self, stake: float, target_payout: float):
        """Build aggressive SGP for PHO @ OKC."""
        
        print("\n" + "="*80)
        print("🚀 EQ12 HIGH-ODDS SGP BUILDER")
        print("="*80)
        print(f"Game: Phoenix Suns @ Oklahoma City Thunder")
        print(f"Tonight: 9:40 PM ET / 6:40 PM PT")
        print(f"Stake: ${stake:.2f}")
        print(f"Target Payout: ${target_payout:.2f}")
        print(f"Required Odds: {int(target_payout/stake)}:1 ({int((target_payout/stake)*100):+d})")
        print("="*80)
        
        # OKC is heavy favorite at home (-1100 moneyline, -14.5 spread)
        # PHO is massive underdog (+700 moneyline, +14.5 spread)
        
        print("\n📊 CURRENT ODDS (Approximate):")
        print("   Moneyline: OKC -1100 / PHO +700")
        print("   Spread: OKC -14.5 (-110) / PHO +14.5 (-110)")
        print("   Total: Over 223.5 (-110) / Under 223.5 (-110)")
        
        # Build SGP options
        sgps = []
        
        # OPTION 1: Underdog parlay (highest odds)
        legs_1 = [
            {"pick": "PHO Moneyline", "odds": +700, "desc": "Phoenix wins outright"},
            {"pick": "PHO +14.5", "odds": -110, "desc": "Phoenix covers spread"},
            {"pick": "Over 223.5", "odds": -110, "desc": "High scoring game"}
        ]
        decimal_1 = self.american_to_decimal(700) * self.american_to_decimal(-110) * self.american_to_decimal(-110)
        payout_1 = stake * decimal_1
        
        sgps.append({
            "name": "🔥 MOONSHOT: Phoenix Upset Special",
            "strategy": "Aggressive underdog play - Phoenix wins",
            "legs": legs_1,
            "parlay_odds_decimal": round(decimal_1, 2),
            "parlay_odds_american": int((decimal_1 - 1) * 100),
            "stake": stake,
            "payout": round(payout_1, 2),
            "profit": round(payout_1 - stake, 2),
            "win_prob": round((1/decimal_1)*100, 2)
        })
        
        # OPTION 2: OKC blowout
        legs_2 = [
            {"pick": "OKC Moneyline", "odds": -1100, "desc": "OKC wins (heavy favorite)"},
            {"pick": "OKC -14.5", "odds": -115, "desc": "OKC wins by 15+"},
            {"pick": "Under 223.5", "odds": -110, "desc": "Defense dominates"}
        ]
        decimal_2 = self.american_to_decimal(-1100) * self.american_to_decimal(-115) * self.american_to_decimal(-110)
        payout_2 = stake * decimal_2
        
        sgps.append({
            "name": "🛡️ SAFE: OKC Blowout",
            "strategy": "Conservative favorite play - OKC dominates",
            "legs": legs_2,
            "parlay_odds_decimal": round(decimal_2, 2),
            "parlay_odds_american": int((decimal_2 - 1) * 100) if decimal_2 >= 2 else int(-100/(decimal_2 - 1)),
            "stake": stake,
            "payout": round(payout_2, 2),
            "profit": round(payout_2 - stake, 2),
            "win_prob": round((1/decimal_2)*100, 2)
        })
        
        # OPTION 3: Mixed - PHO covers but loses
        legs_3 = [
            {"pick": "OKC Moneyline", "odds": -1100, "desc": "OKC wins"},
            {"pick": "PHO +14.5", "odds": -110, "desc": "Phoenix keeps it close"},
            {"pick": "Over 223.5", "odds": -110, "desc": "Both teams score"}
        ]
        decimal_3 = self.american_to_decimal(-1100) * self.american_to_decimal(-110) * self.american_to_decimal(-110)
        payout_3 = stake * decimal_3
        
        sgps.append({
            "name": "⚖️ BALANCED: OKC Wins Close",
            "strategy": "Moderate - OKC wins but Phoenix covers",
            "legs": legs_3,
            "parlay_odds_decimal": round(decimal_3, 2),
            "parlay_odds_american": int((decimal_3 - 1) * 100) if decimal_3 >= 2 else int(-100/(decimal_3 - 1)),
            "stake": stake,
            "payout": round(payout_3, 2),
            "profit": round(payout_3 - stake, 2),
            "win_prob": round((1/decimal_3)*100, 2)
        })
        
        # Display
        print("\n" + "="*80)
        print("🎯 SGP OPTIONS")
        print("="*80)
        
        for sgp in sgps:
            self._print_sgp(sgp)
        
        print("\n" + "="*80)
        print("💡 REALITY CHECK:")
        print("="*80)
        print(f"To turn ${stake:.2f} into ${target_payout:.2f}, you need {int(target_payout/stake)}:1 odds.")
        print(f"That's {int((target_payout/stake - 1)*100):+d} in American odds.")
        print("")
        print("📉 TRUTH: This requires either:")
        print(f"   1. VERY long parlay (8-10+ legs) with moderate odds")
        print(f"   2. Extreme underdog bets (PHO +700 is your best shot)")
        print(f"   3. Player props parlays (not available in basic API)")
        print("")
        print("🎲 RECOMMENDATION:")
        print(f"   - Option #1 (PHO upset) gives ${payout_1:.2f} profit")
        print(f"   - Still short of ${target_payout:.2f} target")
        print(f"   - Consider multiple ${stake:.2f} bets across games")
        print(f"   - OR wait for higher underdog opportunities (+1000+)")
        print("="*80)
        
        print("\n⚠️  CRITICAL WARNINGS:")
        print("   1. Parlays are EXTREMELY risky (ALL legs must win)")
        print("   2. Bookmakers often limit parlay sizes/correlations")
        print("   3. $5 to $500-1000 requires unrealistic odds")
        print("   4. Responsible gambling: Never bet money you can't lose")
        print("   5. This is for entertainment analysis only")
        print("="*80)
        
        # Save report
        output = Path("../reports/sgp_high_odds_analysis.json")
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w') as f:
            json.dump({
                'game': 'Phoenix Suns @ Oklahoma City Thunder',
                'stake': stake,
                'target_payout': target_payout,
                'required_odds': target_payout / stake,
                'sgps': sgps,
                'analysis': {
                    'realistic': False,
                    'reason': 'Target payout requires odds not available in this game',
                    'recommendation': 'Lower target or increase stake'
                },
                'generated_at': datetime.now(timezone.utc).isoformat()
            }, f, indent=2)
        
        print(f"\n✅ Full analysis saved: {output}")
    
    def _print_sgp(self, sgp):
        """Print formatted SGP."""
        print(f"\n{sgp['name']}")
        print(f"{'-'*80}")
        print(f"Strategy: {sgp['strategy']}")
        print(f"Odds: {sgp['parlay_odds_american']:+d} ({sgp['parlay_odds_decimal']:.2f}x)")
        print(f"Stake: ${sgp['stake']:.2f}")
        print(f"Payout: ${sgp['payout']:.2f}")
        print(f"Profit: ${sgp['profit']:.2f} 💰")
        print(f"Win Probability: ~{sgp['win_prob']:.1f}%")
        print(f"\nLegs:")
        for i, leg in enumerate(sgp['legs'], 1):
            print(f"   {i}. {leg['pick']} ({leg['odds']:+d}) - {leg['desc']}")


def main():
    # Check API key
    api_key = os.getenv('ODDS_API_KEY')
    if not api_key:
        print("❌ ODDS_API_KEY not set")
        sys.exit(1)
    
    builder = HighOddsSGPBuilder(api_key)
    builder.build_aggressive_sgp(stake=5.0, target_payout=500.0)


if __name__ == '__main__':
    main()
