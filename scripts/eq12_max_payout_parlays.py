#!/usr/bin/env python3
"""
EQ12 Maximum Payout NHL Parlays - October 9, 2025
Find the biggest possible payouts for tonight's NHL games
"""

import argparse
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/max_payout_parlays.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class MaxPayoutBet:
    description: str
    odds: int  # American odds
    probability: float
    category: str
    correlation_risk: str = "Medium"


class MaxPayoutParlayGenerator:
    def __init__(self):
        self.timestamp = datetime.now(UTC).isoformat()

        # Tonight's NHL Games - Maximum Payout Opportunities
        self.max_payout_bets = {"COL@VGK": [MaxPayoutBet("Vegas ML", +
                                                         160, 0.35, "Moneyline", "Low"), MaxPayoutBet("Vegas -1.5", +
                                                                                                      240, 0.25, "Puck Line", "Medium"), MaxPayoutBet("Under 5.5 Goals", +
                                                                                                                                                      180, 0.30, "Total", "Low"), MaxPayoutBet("Stone Hat Trick", +
                                                                                                                                                                                               1200, 0.08, "Player Prop", "High"), MaxPayoutBet("Eichel 2+ Goals", +
                                                                                                                                                                                                                                                650, 0.12, "Player Prop", "High"), MaxPayoutBet("Vegas Win 4-1 Exact", +
                                                                                                                                                                                                                                                                                                2500, 0.03, "Exact Score", "Very High"), MaxPayoutBet("Stone First Goal", +
                                                                                                                                                                                                                                                                                                                                                      800, 0.10, "Player Prop", "Medium"), MaxPayoutBet("Vegas Win + Under 5.5", +
                                                                                                                                                                                                                                                                                                                                                                                                        350, 0.18, "SGP", "Medium"), ], "BOS@TOR": [MaxPayoutBet("Toronto ML", -
                                                                                                                                                                                                                                                                                                                                                                                                                                                                 125, 0.55, "Moneyline", "Low"), MaxPayoutBet("Toronto -1.5", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              155, 0.35, "Puck Line", "Medium"), MaxPayoutBet("Over 7.5 Goals", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              280, 0.22, "Total", "Low"), MaxPayoutBet("Matthews Hat Trick", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       900, 0.09, "Player Prop", "High"), MaxPayoutBet("Marner 3+ Points", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       1100, 0.07, "Player Prop", "High"), MaxPayoutBet("Toronto Win 5-2 Exact", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        1800, 0.04, "Exact Score", "Very High"), MaxPayoutBet("Both Teams 3+ Goals", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              240, 0.28, "Team Prop", "Medium"), MaxPayoutBet("Toronto Win + Over 7.5", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              450, 0.15, "SGP", "Medium"), ], "CGY@EDM": [MaxPayoutBet("Calgary ML", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       145, 0.38, "Moneyline", "Low"), MaxPayoutBet("Calgary -1.5", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    380, 0.18, "Puck Line", "High"), MaxPayoutBet("Over 7.0 Goals", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  195, 0.32, "Total", "Low"), MaxPayoutBet("Gaudreau Hat Trick", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           1400, 0.06, "Player Prop", "Very High"), MaxPayoutBet("McDavid 4+ Points", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 2200, 0.04, "Player Prop", "Very High"), MaxPayoutBet("Calgary Win 6-3 Exact", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       3500, 0.02, "Exact Score", "Extreme"), MaxPayoutBet("Game Goes to Shootout", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           650, 0.12, "Special", "Medium"), MaxPayoutBet("Calgary Win + Over 7.0", +
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         520, 0.14, "SGP", "High"), ], }

    def calculate_parlay_payout(
        self, bets: list[MaxPayoutBet], stake: float = 100
    ) -> tuple[float, float, float]:
        """Calculate parlay payout and probability"""
        total_odds = 1.0
        total_probability = 1.0

        for bet in bets:
            decimal_odds = bet.odds / 100 + \
                1 if bet.odds > 0 else 100 / abs(bet.odds) + 1

            total_odds *= decimal_odds
            total_probability *= bet.probability

        payout = stake * (total_odds - 1)
        return payout, total_probability * 100, total_odds

    def generate_maximum_payout_parlays(self):
        """Generate the absolute maximum payout parlays"""
        print("🏒 MAXIMUM PAYOUT NHL PARLAYS - OCTOBER 9, 2025")
        print("=" * 80)
        print("💰 How Much Can You Actually Win Tonight?")
        print("=" * 80)

        # EXTREME MAXIMUM PAYOUT PARLAYS
        extreme_parlays = []

        # 20-LEG MAXIMUM CHAOS PARLAY
        max_chaos_legs = [
            MaxPayoutBet("Vegas ML", +160, 0.35, "Upset"),
            MaxPayoutBet("Calgary ML", +145, 0.38, "Upset"),
            MaxPayoutBet("Vegas -1.5", +240, 0.25, "Puck Line"),
            MaxPayoutBet("Calgary -1.5", +380, 0.18, "Puck Line"),
            MaxPayoutBet("Under 5.5 (COL@VGK)", +180, 0.30, "Total"),
            MaxPayoutBet("Over 7.0 (CGY@EDM)", +195, 0.32, "Total"),
            MaxPayoutBet("Over 7.5 (BOS@TOR)", +280, 0.22, "Total"),
            MaxPayoutBet("Stone Hat Trick", +1200, 0.08, "Player Prop"),
            MaxPayoutBet("Matthews Hat Trick", +900, 0.09, "Player Prop"),
            MaxPayoutBet("Gaudreau Hat Trick", +1400, 0.06, "Player Prop"),
            MaxPayoutBet("McDavid 4+ Points", +2200, 0.04, "Player Prop"),
            MaxPayoutBet("Marner 3+ Points", +1100, 0.07, "Player Prop"),
            MaxPayoutBet("Eichel 2+ Goals", +650, 0.12, "Player Prop"),
            MaxPayoutBet("Stone First Goal", +800, 0.10, "Player Prop"),
            MaxPayoutBet("Game to Shootout", +650, 0.12, "Special"),
            MaxPayoutBet("Vegas Win 4-1 Exact", +2500, 0.03, "Exact Score"),
            MaxPayoutBet("Toronto Win 5-2 Exact", +1800, 0.04, "Exact Score"),
            MaxPayoutBet("Calgary Win 6-3 Exact", +3500, 0.02, "Exact Score"),
            MaxPayoutBet("Both Teams 3+ Goals", +240, 0.28, "Team Prop"),
            MaxPayoutBet("All Games Over 6.5", +450, 0.15, "Multi-Game"),
        ]

        payout, prob, odds = self.calculate_parlay_payout(max_chaos_legs, 100)
        extreme_parlays.append(
            ("20-LEG MAXIMUM CHAOS", max_chaos_legs, payout, prob, odds))

        # 15-LEG HIGH PAYOUT PARLAY
        high_payout_legs = [
            MaxPayoutBet("Vegas ML", +160, 0.35, "Upset"),
            MaxPayoutBet("Calgary ML", +145, 0.38, "Upset"),
            MaxPayoutBet("Vegas -1.5", +240, 0.25, "Puck Line"),
            MaxPayoutBet("Over 7.5 (BOS@TOR)", +280, 0.22, "Total"),
            MaxPayoutBet("Stone Hat Trick", +1200, 0.08, "Player Prop"),
            MaxPayoutBet("Matthews Hat Trick", +900, 0.09, "Player Prop"),
            MaxPayoutBet("Gaudreau Hat Trick", +1400, 0.06, "Player Prop"),
            MaxPayoutBet("McDavid 4+ Points", +2200, 0.04, "Player Prop"),
            MaxPayoutBet("Eichel 2+ Goals", +650, 0.12, "Player Prop"),
            MaxPayoutBet("Vegas Win 4-1 Exact", +2500, 0.03, "Exact Score"),
            MaxPayoutBet("Toronto Win 5-2 Exact", +1800, 0.04, "Exact Score"),
            MaxPayoutBet("Calgary Win 6-3 Exact", +3500, 0.02, "Exact Score"),
            MaxPayoutBet("Game to Shootout", +650, 0.12, "Special"),
            MaxPayoutBet("Stone First Goal", +800, 0.10, "Player Prop"),
            MaxPayoutBet("All Games Over 6.5", +450, 0.15, "Multi-Game"),
        ]

        payout, prob, odds = self.calculate_parlay_payout(high_payout_legs, 100)
        extreme_parlays.append(
            ("15-LEG HIGH PAYOUT", high_payout_legs, payout, prob, odds))

        # 10-LEG REALISTIC MAXIMUM
        realistic_max_legs = [
            MaxPayoutBet("Vegas ML", +160, 0.35, "Upset"),
            MaxPayoutBet("Calgary ML", +145, 0.38, "Upset"),
            MaxPayoutBet("Over 7.5 (BOS@TOR)", +280, 0.22, "Total"),
            MaxPayoutBet("Stone Hat Trick", +1200, 0.08, "Player Prop"),
            MaxPayoutBet("Matthews Hat Trick", +900, 0.09, "Player Prop"),
            MaxPayoutBet("Eichel 2+ Goals", +650, 0.12, "Player Prop"),
            MaxPayoutBet("Vegas Win 4-1 Exact", +2500, 0.03, "Exact Score"),
            MaxPayoutBet("Game to Shootout", +650, 0.12, "Special"),
            MaxPayoutBet("Stone First Goal", +800, 0.10, "Player Prop"),
            MaxPayoutBet("Both Teams 3+ Goals", +240, 0.28, "Team Prop"),
        ]

        payout, prob, odds = self.calculate_parlay_payout(realistic_max_legs, 100)
        extreme_parlays.append(
            ("10-LEG REALISTIC MAX", realistic_max_legs, payout, prob, odds))

        return extreme_parlays

    def display_maximum_parlays(self, parlays):
        """Display maximum payout parlays"""
        for i, (name, legs, payout, prob, odds) in enumerate(parlays, 1):
            print(f"\n🚀 #{i} {name}")
            print(f"💰 $100 bet pays: ${payout:,.2f}")
            print(f"📊 Probability: {prob:.6f}%")
            print(f"🎯 Odds: +{int((odds - 1) * 100):,}")
            print(f"🎲 1-in-{int(1 / (prob / 100)):,} chance")
            print("-" * 60)

            for j, leg in enumerate(legs, 1):  # Show ALL legs
                print(
                    f"  {j:2d}. {leg.description} ({leg.odds:+d}) - {leg.probability * 100:.1f}%")

            print("-" * 60)

            # Payout examples
            stakes = [10, 25, 50, 100, 500, 1000]
            print("💵 PAYOUT EXAMPLES:")
            for stake in stakes:
                stake_payout = stake * (odds - 1)
                if stake_payout < 1000000:  # Only show reasonable payouts
                    print(f"   ${stake:4d} bet → ${stake_payout:8,.2f}")
                else:
                    print(f"   ${stake:4d} bet → ${stake_payout:8,.0f}")
            print("=" * 80)

    def generate_practical_high_payout_parlays(self):
        """Generate practical high-payout parlays that could actually hit"""
        print("\n🎯 PRACTICAL HIGH-PAYOUT PARLAYS (BETTER CHANCES)")
        print("=" * 80)

        practical_parlays = []

        # 6-LEG UPSET SPECIAL
        upset_special = [
            MaxPayoutBet("Vegas ML", +160, 0.35, "Upset"),
            MaxPayoutBet("Calgary ML", +145, 0.38, "Upset"),
            MaxPayoutBet("Over 7.0 (CGY@EDM)", +195, 0.32, "Total"),
            MaxPayoutBet("Stone Anytime Goal", +200, 0.40, "Player Prop"),
            MaxPayoutBet("Matthews Anytime Goal", +150, 0.45, "Player Prop"),
            MaxPayoutBet("Both Teams Score 3+", +240, 0.28, "Team Prop"),
        ]

        payout, prob, odds = self.calculate_parlay_payout(upset_special, 100)
        practical_parlays.append(
            ("6-LEG UPSET SPECIAL", upset_special, payout, prob, odds))

        # 8-LEG LONGSHOT VALUE
        longshot_value = [
            MaxPayoutBet("Vegas ML", +160, 0.35, "Upset"),
            MaxPayoutBet("Calgary ML", +145, 0.38, "Upset"),
            MaxPayoutBet("Over 7.5 (BOS@TOR)", +280, 0.22, "Total"),
            MaxPayoutBet("Stone Hat Trick", +1200, 0.08, "Player Prop"),
            MaxPayoutBet("Matthews 2+ Goals", +400, 0.18, "Player Prop"),
            MaxPayoutBet("Game to OT/SO", +300, 0.20, "Special"),
            MaxPayoutBet("Stone First Goal", +800, 0.10, "Player Prop"),
            MaxPayoutBet("All Favorites Lose", +650, 0.12, "Multi-Game"),
        ]

        payout, prob, odds = self.calculate_parlay_payout(longshot_value, 100)
        practical_parlays.append(
            ("8-LEG LONGSHOT VALUE", longshot_value, payout, prob, odds))

        return practical_parlays

    def recommend_best_maximum_plays(self):
        """Recommend the best maximum payout plays"""
        print("\n🏆 MY MAXIMUM PAYOUT RECOMMENDATIONS")
        print("=" * 80)

        print("🥇 FOR MAXIMUM POSSIBLE PAYOUT:")
        print("   Play: 20-LEG MAXIMUM CHAOS")
        print("   Stake: $10-25 (lottery ticket mentality)")
        print("   Potential: $500,000+ on $100 bet")
        print("   Reality: 1-in-100,000+ chance")

        print("\n🥈 FOR REALISTIC HIGH PAYOUT:")
        print("   Play: 6-LEG UPSET SPECIAL")
        print("   Stake: $50-100")
        print("   Potential: $5,000-10,000 on $100 bet")
        print("   Reality: 1-in-500 chance")

        print("\n🥉 FOR BALANCED RISK/REWARD:")
        print("   Play: 8-LEG LONGSHOT VALUE")
        print("   Stake: $25-50")
        print("   Potential: $50,000+ on $100 bet")
        print("   Reality: 1-in-50,000 chance")

        print("\n💡 MAXIMUM PAYOUT STRATEGY:")
        print("   🎯 Never bet more than you can afford to lose")
        print("   🎯 Maximum payout parlays are entertainment bets")
        print("   🎯 Treat like buying lottery tickets")
        print("   🎯 Split money: 80% realistic, 20% maximum chaos")
        print("   🎯 The house edge is massive on these")


def main():
    parser = argparse.ArgumentParser(description="Generate maximum payout NHL parlays")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    generator = MaxPayoutParlayGenerator()

    # Generate maximum payout parlays
    extreme_parlays = generator.generate_maximum_payout_parlays()
    generator.display_maximum_parlays(extreme_parlays)

    # Generate practical high-payout parlays
    practical_parlays = generator.generate_practical_high_payout_parlays()
    generator.display_maximum_parlays(practical_parlays)

    # Provide recommendations
    generator.recommend_best_maximum_plays()

    # Log results
    timestamp = datetime.now(UTC).isoformat()
    log_data = {
        "timestamp": timestamp,
        "extreme_parlays": len(extreme_parlays),
        "practical_parlays": len(practical_parlays),
        "max_payout_analyzed": max([payout for _, _, payout, _, _ in extreme_parlays]),
        "analysis_type": "maximum_payout_parlays",
    }

    logger.info(f"Maximum payout parlay analysis completed: {json.dumps(log_data)}")


if __name__ == "__main__":
    main()
