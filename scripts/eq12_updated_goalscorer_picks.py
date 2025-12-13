#!/usr/bin/env python3
"""
Updated goalscorer parlays without McDavid, Draisaitl, and Matthews
"""

from eq12_goalscorer_parlays import GoalscorerParlayGenerator


def main():
    generator = GoalscorerParlayGenerator()

    # Remove unavailable players: McDavid, Draisaitl, Matthews
    unavailable = ["Connor McDavid", "Leon Draisaitl", "Auston Matthews"]
    available_goalscorers = [
        g for g in generator.sample_goalscorers if g.player_name not in unavailable
    ]

    # Sort by probability (best first)
    available_sorted = sorted(
        available_goalscorers,
        key=lambda x: x.probability,
        reverse=True)

    print("🏒 UPDATED GOALSCORER PARLAYS - AVAILABLE PLAYERS ONLY")
    print("=" * 80)
    print("❌ NOT AVAILABLE: Connor McDavid, Leon Draisaitl, Auston Matthews")
    print("=" * 80)

    print("\n📋 TOP AVAILABLE GOALSCORERS:")
    for i, player in enumerate(available_sorted[:12], 1):
        print(
            f"{
                i:2d}. {
                player.player_name} ({
                player.team}) vs {
                    player.opponent} | {
                        player.odds:+d} ({
                            player.probability:.1%})")

    # Generate new parlays with available players
    parlays = []

    # 2-leg parlays (safest bets)
    best_2_legs = []
    for i in range(4):
        for j in range(i + 1, min(7, len(available_sorted))):
            combo = (available_sorted[i], available_sorted[j])
            prob = generator.calculate_parlay_probability(combo)
            odds = generator.calculate_parlay_odds(combo)
            best_2_legs.append(
                {"legs": 2, "bets": combo, "probability": prob, "odds": odds})

    # Take top 3 2-leg parlays
    best_2_legs.sort(key=lambda x: x["probability"], reverse=True)
    parlays.extend(best_2_legs[:3])

    # 3-leg (new #1 pick)
    combo_3 = available_sorted[:3]
    prob_3 = generator.calculate_parlay_probability(combo_3)
    odds_3 = generator.calculate_parlay_odds(combo_3)
    parlays.append({"legs": 3, "bets": combo_3, "probability": prob_3, "odds": odds_3})

    # 4-leg (excellent value)
    combo_4 = available_sorted[:4]
    prob_4 = generator.calculate_parlay_probability(combo_4)
    odds_4 = generator.calculate_parlay_odds(combo_4)
    parlays.append({"legs": 4, "bets": combo_4, "probability": prob_4, "odds": odds_4})

    # 5-leg (solid value)
    combo_5 = available_sorted[:5]
    prob_5 = generator.calculate_parlay_probability(combo_5)
    odds_5 = generator.calculate_parlay_odds(combo_5)
    parlays.append({"legs": 5, "bets": combo_5, "probability": prob_5, "odds": odds_5})

    # 6-leg (sweet spot)
    combo_6 = available_sorted[:6]
    prob_6 = generator.calculate_parlay_probability(combo_6)
    odds_6 = generator.calculate_parlay_odds(combo_6)
    parlays.append({"legs": 6, "bets": combo_6, "probability": prob_6, "odds": odds_6})

    # 8-leg (long shot)
    combo_8 = available_sorted[:8]
    prob_8 = generator.calculate_parlay_probability(combo_8)
    odds_8 = generator.calculate_parlay_odds(combo_8)
    parlays.append({"legs": 8, "bets": combo_8, "probability": prob_8, "odds": odds_8})

    # Sort by probability
    parlays.sort(key=lambda x: x["probability"], reverse=True)

    print("\n🎯 UPDATED BEST PARLAYS (RANKED BY WINNING PROBABILITY):")
    print("=" * 80)

    for i, parlay in enumerate(parlays, 1):
        prob_pct = parlay["probability"] * 100
        odds = parlay["odds"]
        payout = abs(odds) / 100 if odds > 0 else 100 / abs(odds)

        if prob_pct >= 15:
            status = "🟢 EXCELLENT CHANCE"
        elif prob_pct >= 8:
            status = "🟡 VERY GOOD CHANCE"
        elif prob_pct >= 3:
            status = "🟠 GOOD CHANCE"
        elif prob_pct >= 1:
            status = "🟠 DECENT CHANCE"
        else:
            status = "🔴 LONG SHOT"

        # Assign ratings
        if parlay["legs"] == 2:
            rating = "SAFEST BETS"
        elif parlay["legs"] == 3:
            rating = "NEW #1 PICK ⭐"
        elif parlay["legs"] == 4:
            rating = "EXCELLENT VALUE"
        elif parlay["legs"] == 5:
            rating = "SOLID VALUE"
        elif parlay["legs"] == 6:
            rating = "SWEET SPOT"
        else:
            rating = "LONG SHOT SPECIAL"

        print(f'\n#{i} | {parlay["legs"]}-LEG PARLAY | {status} | {rating}')
        print(
            f'Probability: {
                prob_pct:.2f}% | Odds: {
                odds:+,d} | 1-in-{
                1 /
                parlay["probability"]:.0f} chance')
        print("-" * 80)

        for j, bet in enumerate(parlay["bets"], 1):
            print(
                f"  {
                    j:2d}. {
                    bet.player_name} ({
                    bet.team}) vs {
                    bet.opponent} | {
                        bet.odds:+d} ({
                            bet.probability:.1%})")

        print("\n💰 PAYOUT SCENARIOS:")
        print(f"   $10 bet → ${payout * 10:.2f} profit")
        print(f"   $25 bet → ${payout * 25:.2f} profit")
        print(f"   $50 bet → ${payout * 50:.2f} profit")

        expected_value = (parlay["probability"] * payout) - 1
        ev_color = "🟢" if expected_value > -0.1 else "🟡" if expected_value > -0.3 else "🔴"
        print(
            f"\n📊 Expected Value: {expected_value:+.3f} ({expected_value * 100:+.1f}%) {ev_color}")
        print("=" * 80)

    print("\n🏆 MY TOP 5 UPDATED RECOMMENDATIONS:")
    print("=" * 60)

    best_5 = parlays[:5]
    for i, p in enumerate(best_5, 1):
        prob_pct = p["probability"] * 100
        payout = abs(p["odds"]) / 100 if p["odds"] > 0 else 100 / abs(p["odds"])
        risk = "LOW" if prob_pct > 10 else "MEDIUM" if prob_pct > 3 else "HIGH"

        print(f'\n🥇 RECOMMENDATION #{i}: {p["legs"]}-LEG PARLAY')
        print(f"   Probability: {prob_pct:.2f}% | Risk: {risk}")
        print(f"   $25 bet pays: ${payout * 25:.2f}")

    print("\n⚡ KEY CHANGES WITHOUT McDavid/Draisaitl/Matthews:")
    print("✅ Nathan MacKinnon becomes the #1 scorer (53.5% chance)")
    print("✅ David Pastrnak moves to #2 (51.2% chance)")
    print("✅ Mikko Rantanen becomes key value pick (48.8% chance)")
    print("✅ Probabilities drop but still very reasonable for stars!")

    print("\n🎯 UPDATED STRATEGY:")
    print("📈 Focus on MacKinnon + Pastrnak as foundation")
    print("💎 Rantanen + Gaudreau offer great value additions")
    print("🏒 Still targeting elite scorers with realistic chances")


if __name__ == "__main__":
    main()
