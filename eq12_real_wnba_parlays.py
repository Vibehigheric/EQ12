#!/usr/bin/env python3
"""
EQ12 WNBA Parlays - October 8, 2025
Real WNBA game: Las Vegas Aces @ Phoenix Mercury
"""


def display_real_wnba_parlays():
    """Display WNBA parlays for the actual game available"""

    print("🏀 EQ12 LIVE WNBA PARLAYS - OCTOBER 8, 2025")
    print("=" * 80)
    print("🎯 REAL WNBA GAME AVAILABLE!")
    print()

    print("📊 GAME DETAILS:")
    print("-" * 60)
    print("🏀 Las Vegas Aces @ Phoenix Mercury")
    print("🕐 Time: 12:00 AM ET (Late Night)")
    print("📍 Venue: Phoenix (Mercury home)")
    print("📊 DraftKings Odds:")
    print("   • Las Vegas Aces ML: +150")
    print("   • Phoenix Mercury ML: -180")
    print("   • Las Vegas Aces +4.5: -112")
    print("   • Phoenix Mercury -4.5: -108")
    print("   • Over 163.5: -110")
    print("   • Under 163.5: -110")
    print()

    print("🎫 WNBA SINGLE GAME PARLAYS:")
    print("-" * 60)

    wnba_parlays = [
        {
            "name": "Mercury Home Victory Special",
            "legs": [
                "Phoenix Mercury ML (-180)",
                "Phoenix Mercury -4.5 (-108)",
                "Under 163.5 (-110)",
            ],
            "odds": "+550",
            "stake": "$15",
            "logic": "Home team covers, defensive game",
        },
        {
            "name": "Aces Road Upset Value",
            "legs": ["Las Vegas Aces ML (+150)", "Over 163.5 (-110)"],
            "odds": "+380",
            "stake": "$10",
            "logic": "Aces steal road win in high-scoring affair",
        },
        {
            "name": "High-Scoring Mercury Win",
            "legs": ["Phoenix Mercury ML (-180)", "Over 163.5 (-110)"],
            "odds": "+220",
            "stake": "$20",
            "logic": "Home team wins, both offenses clicking",
        },
        {
            "name": "Aces Cover + Under",
            "legs": ["Las Vegas Aces +4.5 (-112)", "Under 163.5 (-110)"],
            "odds": "+190",
            "stake": "$15",
            "logic": "Competitive game, defensive battle",
        },
    ]

    for i, parlay in enumerate(wnba_parlays, 1):
        stake = int(parlay["stake"].replace("$", ""))
        odds_num = int(parlay["odds"].replace("+", ""))
        payout = stake * (odds_num / 100 + 1)
        profit = payout - stake
        print(f"   {i}. {parlay['name']} {parlay['odds']}")
        print(f"      🔗 Legs ({len(parlay['legs'])}):")
        for leg in parlay["legs"]:
            print(f"         • {leg}")
        print(f"      💰 Stake: {parlay['stake']} → ${payout:.0f} payout (${profit:.0f} profit)")
        print(f"      🧠 Logic: {parlay['logic']}")
        print()

    print("🌟 WNBA PLAYER PROPS (Theoretical - Check Availability):")
    print("-" * 60)

    player_props = [
        {
            "name": "A'ja Wilson Dominance",
            "legs": [
                "A'ja Wilson Over 22.5 Points (-115)",
                "A'ja Wilson Over 9.5 Rebounds (-120)",
                "Las Vegas Aces +4.5 (-112)",
            ],
            "odds": "+650",
            "stake": "$8",
        },
        {
            "name": "Diana Taurasi Veteran Magic",
            "legs": ["Diana Taurasi Over 15.5 Points (-125)", "Phoenix Mercury ML (-180)"],
            "odds": "+280",
            "stake": "$12",
        },
        {
            "name": "Dual Star Performance",
            "legs": [
                "A'ja Wilson Over 20.5 Points (-110)",
                "Diana Taurasi Over 12.5 Points (-115)",
                "Over 163.5 (-110)",
            ],
            "odds": "+550",
            "stake": "$6",
        },
    ]

    for i, parlay in enumerate(player_props, 1):
        stake = int(parlay["stake"].replace("$", ""))
        odds_num = int(parlay["odds"].replace("+", ""))
        payout = stake * (odds_num / 100 + 1)
        profit = payout - stake
        print(f"   {i}. {parlay['name']} {parlay['odds']}")
        print(f"      🔗 Legs ({len(parlay['legs'])}):")
        for leg in parlay["legs"]:
            print(f"         • {leg}")
        print(f"      💰 Stake: {parlay['stake']} → ${payout:.0f} payout (${profit:.0f} profit)")
        print()

    print("🎯 WNBA BETTING STRATEGY ANALYSIS:")
    print("-" * 60)
    print("📈 KEY FACTORS:")
    print("   • Mercury (-180 ML) = 64% implied probability")
    print("   • Aces (+150 ML) = 40% implied probability")
    print("   • 4.5 point spread suggests competitive game")
    print("   • 163.5 total is typical WNBA range")
    print("   • Late night game (12 AM) - check if playoffs")
    print()
    print("🏆 RECOMMENDED PLAYS:")
    print("   1. Mercury ML + Over (most likely scenario)")
    print("   2. Aces +4.5 + Under (value hedge)")
    print("   3. Player props if A'ja Wilson available")
    print("   4. Conservative Mercury -4.5 straight bet")
    print()

    # Calculate totals
    game_total = 15 + 10 + 20 + 15
    props_total = 8 + 12 + 6
    total_wnba = game_total + props_total

    print("💼 WNBA BETTING ALLOCATION:")
    print("-" * 60)
    print(f"   Single Game Parlays: ${game_total}")
    print(f"   Player Props (if available): ${props_total}")
    print(f"   TOTAL WNBA INVESTMENT: ${total_wnba}")
    print()
    print("⚠️  EXECUTION NOTES:")
    print("   • Verify game time and availability")
    print("   • Check if this is playoffs or exhibition")
    print("   • Player props may not be available")
    print("   • Late night game - less public betting")
    print("   • Single game limits parlay options")
    print("   • Focus on best 1-2 plays rather than all")


if __name__ == "__main__":
    display_real_wnba_parlays()
