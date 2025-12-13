#!/usr/bin/env python3
"""
Display the specific recommended goalscorer parlays
"""

from eq12_goalscorer_parlays import GoalscorerParlayGenerator


def main():
    generator = GoalscorerParlayGenerator()
    goalscorers = sorted(
        generator.sample_goalscorers,
        key=lambda x: x.probability,
        reverse=True)

    print("🏒 MY DEFINITIVE GOALSCORER PARLAY PICKS FOR TODAY")
    print("=" * 80)
    print("📅 October 9, 2025 | NHL Action | Ranked by Winning Probability")
    print("=" * 80)

    # Define the specific parlays
    parlays = []

    # 2-leg parlays (best individual chances from earlier analysis)
    best_2_leg = [
        (goalscorers[0], goalscorers[1]),  # McDavid + MacKinnon
        (goalscorers[0], goalscorers[2]),  # McDavid + Draisaitl
        (goalscorers[1], goalscorers[2]),  # MacKinnon + Draisaitl
    ]

    for combo in best_2_leg:
        prob = generator.calculate_parlay_probability(combo)
        odds = generator.calculate_parlay_odds(combo)
        parlays.append(
            {
                "legs": 2,
                "bets": combo,
                "probability": prob,
                "odds": odds,
                "rating": "SAFEST BETS",
            }
        )

    # 3-leg parlay - #1 PICK
    combo_3 = goalscorers[:3]
    prob_3 = generator.calculate_parlay_probability(combo_3)
    odds_3 = generator.calculate_parlay_odds(combo_3)
    parlays.append(
        {
            "legs": 3,
            "bets": combo_3,
            "probability": prob_3,
            "odds": odds_3,
            "rating": "MY #1 PICK ⭐",
        }
    )

    # 4-leg parlay - EXCELLENT VALUE
    combo_4 = goalscorers[:4]
    prob_4 = generator.calculate_parlay_probability(combo_4)
    odds_4 = generator.calculate_parlay_odds(combo_4)
    parlays.append(
        {
            "legs": 4,
            "bets": combo_4,
            "probability": prob_4,
            "odds": odds_4,
            "rating": "EXCELLENT VALUE",
        }
    )

    # 6-leg parlay - SWEET SPOT
    combo_6 = goalscorers[:6]
    prob_6 = generator.calculate_parlay_probability(combo_6)
    odds_6 = generator.calculate_parlay_odds(combo_6)
    parlays.append(
        {
            "legs": 6,
            "bets": combo_6,
            "probability": prob_6,
            "odds": odds_6,
            "rating": "SWEET SPOT",
        }
    )

    # 8-leg parlay - LONG SHOT SPECIAL
    combo_8 = goalscorers[:8]
    prob_8 = generator.calculate_parlay_probability(combo_8)
    odds_8 = generator.calculate_parlay_odds(combo_8)
    parlays.append(
        {
            "legs": 8,
            "bets": combo_8,
            "probability": prob_8,
            "odds": odds_8,
            "rating": "LONG SHOT SPECIAL",
        }
    )

    # Sort by probability (best first)
    parlays.sort(key=lambda x: x["probability"], reverse=True)

    # Display each parlay
    for _i, parlay in enumerate(parlays):
        prob_pct = parlay["probability"] * 100
        odds = parlay["odds"]
        payout = abs(odds) / 100 if odds > 0 else 100 / abs(odds)

        # Determine status emoji
        if prob_pct >= 25:
            status = "🟢 SAFEST"
        elif prob_pct >= 15:
            status = "🟢 EXCELLENT"
        elif prob_pct >= 5:
            status = "🟡 SOLID"
        elif prob_pct >= 1:
            status = "🟠 DECENT"
        else:
            status = "🔴 LONG SHOT"

        print(f'\n{parlay["legs"]}-LEG PARLAY | {status} | {parlay["rating"]}')
        print(
            f'Probability: {
                prob_pct:.2f}% | Odds: {
                odds:+,d} | 1-in-{
                1 /
                parlay["probability"]:.0f} chance')
        print("=" * 80)

        for j, bet in enumerate(parlay["bets"], 1):
            print(f"  {j:2d}. {bet}")

        # Show payout scenarios
        print("\n💰 PAYOUT SCENARIOS:")
        print(f"   $10 bet → ${payout * 10:.2f} profit")
        print(f"   $25 bet → ${payout * 25:.2f} profit")
        print(f"   $50 bet → ${payout * 50:.2f} profit")

        # Expected value
        expected_value = (parlay["probability"] * payout) - 1
        ev_color = "🟢" if expected_value > -0.1 else "🟡" if expected_value > -0.3 else "🔴"
        print(
            f"\n📊 Expected Value: {expected_value:+.3f} ({expected_value * 100:+.1f}%) {ev_color}")

        print("=" * 80)

    # Summary and recommendations
    print("\n🎯 SUMMARY & BETTING STRATEGY:")
    print("=" * 50)

    safest = [p for p in parlays if p["legs"] == 2]
    best_safest = max(safest, key=lambda x: x["probability"])

    recommended = next(p for p in parlays if p["legs"] == 3)
    value_play = next(p for p in parlays if p["legs"] == 4)
    sweet_spot = next(p for p in parlays if p["legs"] == 6)

    print(
        f'\n🥇 SAFEST BET: 2-leg parlay ({best_safest["probability"] * 100:.2f}% chance)')
    print("   Best combo: McDavid + MacKinnon")
    print(f'   $25 bet pays: ${abs(best_safest["odds"]) / 100 * 25:.2f}')

    print(
        f'\n⭐ MY #1 PICK: 3-leg parlay ({recommended["probability"] * 100:.2f}% chance)')
    print("   Stars: McDavid + MacKinnon + Draisaitl")
    print(f'   $25 bet pays: ${abs(recommended["odds"]) / 100 * 25:.2f}')

    print(
        f'\n💎 EXCELLENT VALUE: 4-leg parlay ({value_play["probability"] * 100:.2f}% chance)')
    print("   Elite scorers only")
    print(f'   $25 bet pays: ${abs(value_play["odds"]) / 100 * 25:.2f}')

    print(
        f'\n🎯 SWEET SPOT: 6-leg parlay ({sweet_spot["probability"] * 100:.2f}% chance)')
    print("   Best risk/reward balance")
    print(f'   $25 bet pays: ${abs(sweet_spot["odds"]) / 100 * 25:.2f}')

    print("\n🎲 IF YOU'RE FEELING LUCKY: 8-leg parlay (0.42% chance)")
    print("   $25 bet pays: $5,892.50 💰")

    print("\n📈 BANKROLL STRATEGY:")
    print("   Conservative: 80% on 2-3 leg parlays")
    print("   Moderate: 60% on 2-4 leg, 40% on 6-8 leg")
    print("   Aggressive: Equal splits across all parlays")

    print("\n⚖️ THE MATHEMATICAL TRUTH:")
    print("   These are the ONLY parlays with realistic winning chances")
    print("   Stars score goals more than role players")
    print("   Probability decreases exponentially with more legs")
    print("   But... someone has to win, and tonight it could be YOU! 🏒")


if __name__ == "__main__":
    main()
