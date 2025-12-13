#!/usr/bin/env python3
"""
Best SGP Combination Slip Generator
Combines the best SGPs from different games on one slip
"""

import itertools

from eq12_sgp_generator import SGPGenerator


def main():
    SGPGenerator()

    print("🏒 BEST SGP COMBINATION SLIPS - OCTOBER 9, 2025")
    print("=" * 80)
    print("🎯 Combining Best SGPs from Different Games on One Slip")
    print("=" * 80)

    # Define the best individual SGPs from each game
    best_sgps = {
        "COL @ VGK": [
            {
                "name": "Colorado ML + Colorado +1.5",
                "legs": 2,
                "probability": 0.36051,
                "odds": 177,
                "description": "Colorado ML (-110) + Colorado +1.5 (-220)",
            },
            {
                "name": "Colorado ML + Over 6.5",
                "legs": 2,
                "probability": 0.28034,
                "odds": 256,
                "description": "Colorado ML (-110) + Over 6.5 Goals (-115)",
            },
            {
                "name": "Colorado ML + MacKinnon Goal",
                "legs": 2,
                "probability": 0.28034,  # 52.4% * 53.5%
                "odds": 256,
                "description": "Colorado ML (-110) + MacKinnon Anytime Goal (-115)",
            },
        ],
        "BOS @ TOR": [
            {
                "name": "Boston ML + Boston +1.5",
                "legs": 2,
                "probability": 0.34453,
                "odds": 190,
                "description": "Boston ML (+105) + Boston +1.5 (-240)",
            },
            {
                "name": "Boston ML + Over 6.0",
                "legs": 2,
                "probability": 0.25571,
                "odds": 291,
                "description": "Boston ML (+105) + Over 6.0 Goals (-110)",
            },
            {
                "name": "Boston ML + Pastrnak Goal",
                "legs": 2,
                "probability": 0.24986,  # 48.8% * 51.2%
                "odds": 300,
                "description": "Boston ML (+105) + Pastrnak Anytime Goal (-105)",
            },
        ],
        "CGY @ EDM": [
            {
                "name": "Calgary ML + Edmonton +1.5",
                "legs": 2,
                "probability": 0.32640,
                "odds": 206,
                "description": "Calgary ML (+145) + Edmonton +1.5 (-400)",
            },
            {
                "name": "Calgary ML + Over 6.5",
                "legs": 2,
                "probability": 0.20890,
                "odds": 378,
                "description": "Calgary ML (+145) + Over 6.5 Goals (-105)",
            },
            {
                "name": "Edmonton ML + Over 6.5",
                "legs": 2,
                "probability": 0.32563,  # 63.6% * 51.2%
                "odds": 207,
                "description": "Edmonton ML (-175) + Over 6.5 Goals (-105)",
            },
        ],
    }

    # Calculate combination probabilities
    combinations = []

    # 2-game combinations (pick 1 SGP from 2 different games)
    games = list(best_sgps.keys())
    for game1, game2 in itertools.combinations(games, 2):
        for sgp1 in best_sgps[game1]:
            for sgp2 in best_sgps[game2]:
                combo_prob = sgp1["probability"] * sgp2["probability"]
                combo_odds = int((1 / combo_prob) - 1) * \
                    100 if combo_prob > 0 else 999999

                combinations.append(
                    {
                        "type": "2-Game Combo",
                        "games": [game1, game2],
                        "sgps": [sgp1, sgp2],
                        "total_legs": sgp1["legs"] + sgp2["legs"],
                        "probability": combo_prob,
                        "odds": combo_odds,
                        "description": f"{sgp1['name']} + {sgp2['name']}",
                    }
                )

    # 3-game combinations (pick 1 SGP from all 3 games)
    for sgp1 in best_sgps["COL @ VGK"]:
        for sgp2 in best_sgps["BOS @ TOR"]:
            for sgp3 in best_sgps["CGY @ EDM"]:
                combo_prob = sgp1["probability"] * \
                    sgp2["probability"] * sgp3["probability"]
                combo_odds = int((1 / combo_prob) - 1) * \
                    100 if combo_prob > 0 else 999999

                combinations.append(
                    {
                        "type": "3-Game Combo",
                        "games": ["COL @ VGK", "BOS @ TOR", "CGY @ EDM"],
                        "sgps": [sgp1, sgp2, sgp3],
                        "total_legs": sgp1["legs"] + sgp2["legs"] + sgp3["legs"],
                        "probability": combo_prob,
                        "odds": combo_odds,
                        "description": f"{sgp1['name']} + {sgp2['name']} + {sgp3['name']}",
                    }
                )

    # Sort by probability (best first)
    combinations.sort(key=lambda x: x["probability"], reverse=True)

    # Display best combinations
    print("\n🏆 TOP 15 SGP COMBINATION SLIPS (BEST PROBABILITY):")
    print("=" * 80)

    for i, combo in enumerate(combinations[:15], 1):
        prob_pct = combo["probability"] * 100
        payout = abs(combo["odds"]) / \
            100 if combo["odds"] > 0 else 100 / abs(combo["odds"])

        # Status based on probability
        if prob_pct >= 8:
            status = "🟢 EXCELLENT"
        elif prob_pct >= 3:
            status = "🟡 VERY GOOD"
        elif prob_pct >= 1:
            status = "🟠 GOOD"
        else:
            status = "🔴 LONG SHOT"

        print(f"\n#{i} | {combo['type']} | {combo['total_legs']}-LEG TOTAL | {status}")
        print(
            f"Probability: {prob_pct:.3f}% | Odds: +{combo['odds']:,} | 1-in-{1 / combo['probability']:.0f}"
        )
        print(f"$25 bet pays: ${payout * 25:.2f} | $50 bet pays: ${payout * 50:.2f}")
        print("-" * 70)

        for j, sgp in enumerate(combo["sgps"], 1):
            print(f"  {j}. {sgp['description']} ({sgp['probability']:.1%})")

        # Expected value calculation
        expected_value = (combo["probability"] * payout) - 1
        ev_color = "🟢" if expected_value > -0.2 else "🟡" if expected_value > -0.5 else "🔴"
        print(
            f"\n📊 Expected Value: {expected_value:+.3f} ({expected_value * 100:+.1f}%) {ev_color}")
        print("=" * 80)

    # My top recommendations
    print("\n🎯 MY TOP 5 SGP COMBINATION RECOMMENDATIONS:")
    print("=" * 60)

    top_5 = combinations[:5]
    for i, combo in enumerate(top_5, 1):
        prob_pct = combo["probability"] * 100
        payout = abs(combo["odds"]) / 100

        risk_level = "LOW" if prob_pct > 5 else "MEDIUM" if prob_pct > 2 else "HIGH"

        print(f"\n🥇 RECOMMENDATION #{i}: {combo['type']}")
        print(f"   Description: {combo['description']}")
        print(f"   Probability: {prob_pct:.3f}% | Risk: {risk_level}")
        print(f"   $25 → ${payout * 25:.2f} | $50 → ${payout * 50:.2f}")

    # Strategy recommendations
    print("\n💡 COMBINATION SGP STRATEGY:")
    print("=" * 50)

    best_2_game = next(c for c in combinations if c["type"] == "2-Game Combo")
    best_3_game = next(c for c in combinations if c["type"] == "3-Game Combo")

    print("\n🎯 CONSERVATIVE PLAY:")
    print(f"   Best 2-Game Combo: {best_2_game['probability'] * 100:.3f}% chance")
    print(f"   Payout: ${abs(best_2_game['odds']) / 100 * 50:.2f} on $50 bet")
    print("   Strategy: Pick safest SGP from 2 different games")

    print("\n🎲 MODERATE PLAY:")
    print(f"   Best 3-Game Combo: {best_3_game['probability'] * 100:.3f}% chance")
    print(f"   Payout: ${abs(best_3_game['odds']) / 100 * 25:.2f} on $25 bet")
    print("   Strategy: Include all 3 games for bigger payout")

    print("\n🚀 AGGRESSIVE PLAY:")
    print("   Lower probability combos (1-2% range)")
    print("   Higher payouts ($1,000+ on $25 bets)")
    print("   Strategy: Target 4-6 leg combinations")

    # Bankroll allocation suggestions
    print("\n💰 SUGGESTED BANKROLL ALLOCATION ($100 total):")
    print(f"   $40: Best 2-game combo ({best_2_game['probability'] * 100:.1f}% chance)")
    print("   $30: Second-best 2-game combo")
    print(f"   $20: Best 3-game combo ({best_3_game['probability'] * 100:.1f}% chance)")
    print("   $10: Long shot combo (swing for the fences)")

    # Final analysis
    total_combos = len(combinations)
    avg_prob = sum(c["probability"] for c in combinations) / total_combos * 100

    print("\n📈 COMBINATION ANALYSIS:")
    print(f"   Total combinations analyzed: {total_combos}")
    print(f"   Average probability: {avg_prob:.3f}%")
    print(f"   Best combination: {combinations[0]['probability'] * 100:.3f}%")
    print(f"   Longest shot: {combinations[-1]['probability'] * 100:.6f}%")

    print("\n🏒 KEY INSIGHTS:")
    print("   ✅ 2-game combos offer best balance of probability vs payout")
    print("   ✅ Safest individual SGPs from each game = best foundations")
    print("   ✅ 3-game combos still reasonable (2-4% range)")
    print("   ✅ Combining moneylines + totals provides good correlation")
    print("   ✅ Stars scoring + team winning = logical combinations")


if __name__ == "__main__":
    main()
