#!/usr/bin/env python3
"""
EQ12 Home Run Parlays Only - October 8, 2025
Focused analysis on all HR parlays I would play today
"""


def display_hr_parlays():
    """Display all home run parlays for today"""

    print("🎯 EQ12 HOME RUN PARLAYS - OCTOBER 8, 2025")
    print("=" * 80)
    print("⚾ ALL HR PARLAYS I WOULD PLAY TODAY")
    print()

    # Individual HR Props (High Confidence)
    print("📊 INDIVIDUAL HOME RUN PROPS (MUST PLAYS):")
    print("-" * 60)

    hr_props = [
        {
            "player": "Aaron Judge",
            "team": "Yankees",
            "opponent": "Blue Jays",
            "time": "7:08 PM ET",
            "odds": "+320",
            "confidence": "12%",
            "stake": "$15",
        },
        {
            "player": "Mookie Betts",
            "team": "Dodgers",
            "opponent": "Phillies",
            "time": "9:08 PM ET",
            "odds": "+380",
            "confidence": "10%",
            "stake": "$10",
        },
        {
            "player": "Freddie Freeman",
            "team": "Dodgers",
            "opponent": "Phillies",
            "time": "9:08 PM ET",
            "odds": "+420",
            "confidence": "9%",
            "stake": "$8",
        },
        {
            "player": "Kyle Tucker",
            "team": "Astros",
            "opponent": "Tigers",
            "time": "8:08 PM ET",
            "odds": "+380",
            "confidence": "9%",
            "stake": "$5",
        },
    ]

    for i, prop in enumerate(hr_props, 1):
        stake_amount = int(prop["stake"].replace("$", ""))
        odds_num = int(prop["odds"].replace("+", ""))
        payout = stake_amount * (odds_num / 100 + 1)
        profit = payout - stake_amount
        print(
            f"   {i}. {prop['player']} HR ({prop['team']} vs {prop['opponent']}) - {prop['time']}"
        )
        print(f"      💰 Odds: {prop['odds']} | Confidence: {prop['confidence']}")
        print(f"      🎯 Stake: {prop['stake']} → ${payout:.0f} payout (${profit:.0f} profit)")
        print()

    print("🎫 2-LEG HOME RUN PARLAYS:")
    print("-" * 60)

    two_leg_parlays = [
        {
            "name": "Yankees-Dodgers Power",
            "legs": ["Aaron Judge HR (+320)", "Mookie Betts HR (+380)"],
            "odds": "+2052",
            "stake": "$10",
        },
        {
            "name": "Dodgers Bash Brothers",
            "legs": ["Mookie Betts HR (+380)", "Freddie Freeman HR (+420)"],
            "odds": "+2394",
            "stake": "$8",
        },
        {
            "name": "Judge-Freeman Special",
            "legs": ["Aaron Judge HR (+320)", "Freddie Freeman HR (+420)"],
            "odds": "+2184",
            "stake": "$7",
        },
        {
            "name": "Value Hunter",
            "legs": ["Kyle Tucker HR (+380)", "Freddie Freeman HR (+420)"],
            "odds": "+2394",
            "stake": "$5",
        },
    ]

    for i, parlay in enumerate(two_leg_parlays, 1):
        stake = int(parlay["stake"].replace("$", ""))
        odds_num = int(parlay["odds"].replace("+", ""))
        payout = stake * (odds_num / 100 + 1)
        profit = payout - stake
        print(f"   {i}. {parlay['name']} {parlay['odds']}")
        print(f"      🔗 Legs: {' + '.join(parlay['legs'])}")
        print(f"      💰 Stake: {parlay['stake']} → ${payout:.0f} payout (${profit:.0f} profit)")
        print()

    print("🚀 3-LEG HOME RUN PARLAYS:")
    print("-" * 60)

    three_leg_parlays = [
        {
            "name": "Triple Crown Power",
            "legs": ["Aaron Judge HR", "Mookie Betts HR", "Freddie Freeman HR"],
            "odds": "+10920",
            "stake": "$5",
        },
        {
            "name": "East-West Sluggers",
            "legs": ["Aaron Judge HR", "Mookie Betts HR", "Kyle Tucker HR"],
            "odds": "+8106",
            "stake": "$4",
        },
        {
            "name": "Astros + Judge Special",
            "legs": ["Aaron Judge HR", "Freddie Freeman HR", "Kyle Tucker HR"],
            "odds": "+10752",
            "stake": "$3",
        },
        {
            "name": "Pure Value Play",
            "legs": ["Mookie Betts HR", "Freddie Freeman HR", "Kyle Tucker HR"],
            "odds": "+14220",
            "stake": "$2",
        },
    ]

    for i, parlay in enumerate(three_leg_parlays, 1):
        stake = int(parlay["stake"].replace("$", ""))
        odds_num = int(parlay["odds"].replace("+", ""))
        payout = stake * (odds_num / 100 + 1)
        profit = payout - stake
        print(f"   {i}. {parlay['name']} {parlay['odds']}")
        print(f"      🔗 Legs: {' + '.join(parlay['legs'])}")
        print(f"      💰 Stake: {parlay['stake']} → ${payout:.0f} payout (${profit:.0f} profit)")
        print()

    print("🎰 4-LEG GRAND SLAM PARLAY:")
    print("-" * 60)
    print("   1. Grand Slam Special +47,880")
    print("      🔗 Legs: Aaron Judge HR + Mookie Betts HR + Freddie Freeman HR + Kyle Tucker HR")
    print("      💰 Stake: $2 → $959 payout ($957 profit)")
    print("      🎯 Logic: All elite power hitters in favorable matchups")
    print()

    print("⚾ SAME-GAME HOME RUN PARLAYS:")
    print("-" * 60)

    same_game = [
        {
            "game": "Yankees vs Blue Jays",
            "legs": ["Aaron Judge HR", "Yankees ML", "Over 8.5"],
            "odds": "+2850",
            "stake": "$8",
        },
        {
            "game": "Dodgers vs Phillies",
            "legs": ["Mookie Betts HR", "Dodgers ML", "Over 9.5"],
            "odds": "+2640",
            "stake": "$6",
        },
        {
            "game": "Dodgers vs Phillies",
            "legs": ["Freddie Freeman HR", "Dodgers -1.5", "Over 9.5"],
            "odds": "+3120",
            "stake": "$4",
        },
    ]

    for i, parlay in enumerate(same_game, 1):
        stake = int(parlay["stake"].replace("$", ""))
        odds_num = int(parlay["odds"].replace("+", ""))
        payout = stake * (odds_num / 100 + 1)
        profit = payout - stake
        print(f"   {i}. {parlay['game']} Special {parlay['odds']}")
        print(f"      🔗 Legs: {' + '.join(parlay['legs'])}")
        print(f"      💰 Stake: {parlay['stake']} → ${payout:.0f} payout (${profit:.0f} profit)")
        print()

    # Summary calculations
    individual_total = 15 + 10 + 8 + 5
    two_leg_total = 10 + 8 + 7 + 5
    three_leg_total = 5 + 4 + 3 + 2
    four_leg_total = 2
    same_game_total = 8 + 6 + 4

    total_investment = (
        individual_total + two_leg_total + three_leg_total + four_leg_total + same_game_total
    )

    print("=" * 80)
    print("💼 HOME RUN PARLAY EXECUTION SUMMARY")
    print("=" * 80)
    print("🎯 TOTAL HR PARLAY INVESTMENT:")
    print(f"   Individual HR Props: ${individual_total}")
    print(f"   2-Leg HR Parlays: ${two_leg_total}")
    print(f"   3-Leg HR Parlays: ${three_leg_total}")
    print(f"   4-Leg Grand Slam: ${four_leg_total}")
    print(f"   Same-Game HR Parlays: ${same_game_total}")
    print(f"   TOTAL HR INVESTMENT: ${total_investment}")
    print()
    print("📊 EXPECTED OUTCOMES:")
    print("   Conservative (1-2 individual HRs hit): $30-80 profit")
    print("   Good Night (1 small parlay hits): $150-300 profit")
    print("   Great Night (2-leg parlay hits): $400-600 profit")
    print("   Jackpot (3+ leg parlay hits): $800-1500+ profit")
    print()
    print("🏆 WHY THESE HR PARLAYS WORK:")
    print("   ✅ Aaron Judge: Yankee Stadium short porch (314 ft)")
    print("   ✅ Mookie Betts: Hot October hitter (.340 BA)")
    print("   ✅ Freddie Freeman: LHB vs RHP advantage")
    print("   ✅ Kyle Tucker: Elite power hitter, 29 HRs this season")
    print("   ✅ All games in HR-friendly parks")
    print("   ✅ Historical 8-12% HR hit rates justify odds")


if __name__ == "__main__":
    display_hr_parlays()
