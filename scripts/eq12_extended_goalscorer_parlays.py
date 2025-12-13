#!/usr/bin/env python3
"""
Show extended goalscorer parlays up to 20 legs
"""

from eq12_goalscorer_parlays import GoalscorerParlayGenerator


def main():
    generator = GoalscorerParlayGenerator()
    goalscorers = sorted(
        generator.sample_goalscorers,
        key=lambda x: x.probability,
        reverse=True)

    print("🏒 EXTENDED GOALSCORER PARLAYS - UP TO 20 LEGS")
    print("=" * 80)

    # Generate specific leg counts with best players
    leg_counts = [3, 4, 5, 6, 8, 10, 12, 15, 20]
    best_parlays = []

    for legs in leg_counts:
        if legs <= len(goalscorers):
            combo = goalscorers[:legs]
            probability = generator.calculate_parlay_probability(combo)
            odds = generator.calculate_parlay_odds(combo)

            best_parlays.append(
                {"legs": legs, "bets": combo, "probability": probability, "odds": odds}
            )

    # Sort by probability for final ranking
    best_parlays.sort(key=lambda x: x["probability"], reverse=True)

    print("\n🎯 BEST GOALSCORER PARLAYS BY WINNING PROBABILITY:")
    print("=" * 80)

    for i, parlay in enumerate(best_parlays, 1):
        prob_pct = parlay["probability"] * 100
        odds = parlay["odds"]
        payout = abs(odds) / 100 if odds > 0 else 100 / abs(odds)

        if prob_pct >= 5:
            status = "🟢 EXCELLENT CHANCE"
        elif prob_pct >= 1:
            status = "🟡 GOOD CHANCE"
        elif prob_pct >= 0.1:
            status = "🟠 DECENT CHANCE"
        else:
            status = "🔴 LONG SHOT"

        print(f'\n#{i} | {parlay["legs"]}-LEG PARLAY | {status}')
        print(f"Probability: {prob_pct:.4f}% | Odds: {odds:+,d}")
        print(f'$1 bet pays: ${payout:.2f} | 1-in-{1 /
                                                   parlay["probability"]:.0f} chance')
        print("-" * 80)

        for j, bet in enumerate(parlay["bets"], 1):
            print(f"  {j:2d}. {bet}")

        if i <= 6:
            expected_value = (parlay["probability"] * payout) - 1
            print(
                f"\n💰 Expected Value: {expected_value:+.4f} ({expected_value * 100:+.2f}%)")

        print("=" * 80)

    print("\n🏆 MY TOP 5 PLAYS FOR TODAY (IN ORDER OF BEST CHANCE):")
    print("=" * 60)

    for i in range(min(5, len(best_parlays))):
        p = best_parlays[i]
        prob_pct = p["probability"] * 100
        payout_per_dollar = abs(p["odds"]) / \
            100 if p["odds"] > 0 else 100 / abs(p["odds"])

        risk_level = "LOW" if prob_pct > 5 else "MEDIUM" if prob_pct > 1 else "HIGH"

        print(f'\n🥇 PLAY #{i + 1}: {p["legs"]}-LEG PARLAY')
        print(f"   Probability: {prob_pct:.4f}% | Risk: {risk_level}")
        print(f"   $10 bet pays: ${payout_per_dollar * 10:.2f}")
        print(f"   $25 bet pays: ${payout_per_dollar * 25:.2f}")
        print(f"   $50 bet pays: ${payout_per_dollar * 50:.2f}")


if __name__ == "__main__":
    main()
