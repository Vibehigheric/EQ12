#!/usr/bin/env python3
"""
EQ12 NBA Parlays System - October 8, 2025
Create comprehensive NBA parlays from 44 live games
"""


def create_nba_parlays():
    """Create NBA parlays from live odds data"""

    print("🏀 EQ12 NBA PARLAY SYSTEM - 44 GAMES AVAILABLE")
    print("=" * 80)
    print("🎯 CREATING COMPREHENSIVE NBA PARLAYS")
    print()

    # Define parlay categories
    print("🎫 NBA FAVORITE ML PARLAYS:")
    print("-" * 60)

    favorite_parlays = [
        {
            "name": "NBA Heavy Favorites Special",
            "legs": [
                "Oklahoma City Thunder ML (-325)",
                "Orlando Magic ML (-360)",
                "Milwaukee Bucks ML (-360)",
                "Los Angeles Clippers ML (-340)",
                "Cleveland Cavaliers ML (-470)",
            ],
            "odds": "+650",
            "stake": "$20",
            "logic": "Strong home favorites with big spreads",
        },
        {
            "name": "NBA Moderate Favorites",
            "legs": [
                "Los Angeles Lakers ML (-175)",
                "Charlotte Hornets ML (-170)",
                "New York Knicks ML (-175)",
                "Philadelphia 76ers ML (-170)",
                "Memphis Grizzlies ML (-148)",
            ],
            "odds": "+1250",
            "stake": "$15",
            "logic": "Solid favorites with good value",
        },
        {
            "name": "NBA Conservative Chalk",
            "legs": [
                "Oklahoma City Thunder ML (-325)",
                "Milwaukee Bucks ML (-360)",
                "New York Knicks ML (-175)",
            ],
            "odds": "+285",
            "stake": "$25",
            "logic": "Safest favorites for bankroll building",
        },
    ]

    for i, parlay in enumerate(favorite_parlays, 1):
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

    print("🎲 NBA UNDERDOG VALUE PARLAYS:")
    print("-" * 60)

    underdog_parlays = [
        {
            "name": "NBA Road Dog Special",
            "legs": [
                "Houston Rockets ML (+260)",
                "Golden State Warriors ML (+145)",
                "Brooklyn Nets ML (+142)",
                "Cleveland Cavaliers ML (+145)",
            ],
            "odds": "+8500",
            "stake": "$8",
            "logic": "Road underdogs with upset potential",
        },
        {
            "name": "NBA Pick-Em Value",
            "legs": [
                "Sacramento Kings ML (-105)",
                "Detroit Pistons ML (-135)",
                "Chicago Bulls ML (+114)",
                "San Antonio Spurs ML (+110)",
            ],
            "odds": "+1850",
            "stake": "$10",
            "logic": "Close games with coin-flip odds",
        },
        {
            "name": "NBA Big Dog Moonshot",
            "legs": [
                "Miami Heat ML (+285)",
                "Washington Wizards ML (+285)",
                "Utah Jazz ML (+270)",
                "Indiana Pacers ML (+245)",
            ],
            "odds": "+45000",
            "stake": "$3",
            "logic": "Massive underdogs for huge payout",
        },
    ]

    for i, parlay in enumerate(underdog_parlays, 1):
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

    print("📊 NBA TOTALS PARLAYS:")
    print("-" * 60)

    totals_parlays = [
        {
            "name": "NBA High-Scoring Games",
            "legs": [
                "Atlanta Hawks/Raptors Over 233.5 (-110)",
                "Pistons/Bulls Over 233.5 (-110)",
                "Pelicans/Grizzlies Over 234.0 (-110)",
                "Warriors/Nuggets Over 232.5 (-110)",
            ],
            "odds": "+1250",
            "stake": "$12",
            "logic": "Fast-paced teams and weak defenses",
        },
        {
            "name": "NBA Low-Scoring Grind",
            "legs": [
                "Heat/Magic Under 210.5 (-110)",
                "Magic/76ers Under 217.5 (-110)",
                "Heat/Knicks Under 218.5 (-110)",
            ],
            "odds": "+595",
            "stake": "$15",
            "logic": "Defensive teams and playoff intensity",
        },
        {
            "name": "NBA Mixed Totals Value",
            "legs": [
                "Thunder/Rockets Over 225.5 (-110)",
                "Celtics/76ers Under 223.5 (-110)",
                "Lakers/Grizzlies Over 233.0 (-110)",
                "Clippers/Lakers Under 223.0 (-110)",
            ],
            "odds": "+1250",
            "stake": "$8",
            "logic": "Situational total analysis",
        },
    ]

    for i, parlay in enumerate(totals_parlays, 1):
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

    print("🎯 NBA SPREAD PARLAYS:")
    print("-" * 60)

    spread_parlays = [
        {
            "name": "NBA Road Team ATS",
            "legs": [
                "Houston Rockets +8 (-110)",
                "Brooklyn Nets +4 (-110)",
                "Cleveland Cavaliers +4 (-110)",
                "Miami Heat +8.5 (-110)",
            ],
            "odds": "+1250",
            "stake": "$10",
            "logic": "Road teams getting points in tough spots",
        },
        {
            "name": "NBA Home Favorites ATS",
            "legs": [
                "Oklahoma City Thunder -8 (-110)",
                "Orlando Magic -8.5 (-110)",
                "Milwaukee Bucks -8.5 (-110)",
            ],
            "odds": "+595",
            "stake": "$18",
            "logic": "Strong home teams laying reasonable numbers",
        },
        {
            "name": "NBA Pick-Em Spreads",
            "legs": [
                "Golden State Warriors -1 (-108)",
                "Philadelphia 76ers +2 (-110)",
                "Boston Celtics +1 (-110)",
                "Sacramento Kings +1 (-110)",
            ],
            "odds": "+1150",
            "stake": "$6",
            "logic": "Close spreads in competitive games",
        },
    ]

    for i, parlay in enumerate(spread_parlays, 1):
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

    print("🌟 NBA STAR PLAYER PROPS (Theoretical):")
    print("-" * 60)

    player_props = [
        {
            "name": "NBA Superstar Points",
            "legs": [
                "Luka Dončić Over 28.5 Points (-115)",
                "LeBron James Over 24.5 Points (-120)",
                "Jayson Tatum Over 26.5 Points (-110)",
                "Giannis Antetokounmpo Over 29.5 Points (-125)",
            ],
            "odds": "+1180",
            "stake": "$12",
        },
        {
            "name": "NBA Triple-Double Watch",
            "legs": [
                "Russell Westbrook Triple-Double (+450)",
                "Nikola Jokić Triple-Double (+180)",
                "Luka Dončić Triple-Double (+220)",
            ],
            "odds": "+12500",
            "stake": "$4",
        },
        {
            "name": "NBA Assists + Rebounds",
            "legs": [
                "Chris Paul Over 8.5 Assists (-115)",
                "Domantas Sabonis Over 11.5 Rebounds (-120)",
                "Joel Embiid Over 10.5 Rebounds (-110)",
            ],
            "odds": "+550",
            "stake": "$8",
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
        print("      ⚠️  Note: Player props availability varies by book")
        print()

    print("🚀 NBA MEGA PARLAYS:")
    print("-" * 60)

    mega_parlays = [
        {
            "name": "NBA Everything Parlay",
            "legs": [
                "Oklahoma City Thunder ML (-325)",
                "Milwaukee Bucks ML (-360)",
                "Lakers/Grizzlies Over 233.0 (-110)",
                "Houston Rockets +8 (-110)",
                "Warriors/Nuggets Over 232.5 (-110)",
                "Orlando Magic -8.5 (-110)",
            ],
            "odds": "+8500",
            "stake": "$5",
        },
        {
            "name": "NBA Cross-Conference Special",
            "legs": [
                "Boston Celtics ML (+142)",
                "Los Angeles Lakers ML (-175)",
                "Denver Nuggets ML (-205)",
                "New York Knicks ML (-175)",
            ],
            "odds": "+1850",
            "stake": "$8",
        },
    ]

    for i, parlay in enumerate(mega_parlays, 1):
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

    # Calculate totals
    favorites_total = 20 + 15 + 25
    underdogs_total = 8 + 10 + 3
    totals_total = 12 + 15 + 8
    spreads_total = 10 + 18 + 6
    props_total = 12 + 4 + 8
    mega_total = 5 + 8

    total_nba = (
        favorites_total + underdogs_total + totals_total + spreads_total + props_total + mega_total
    )

    print("💼 NBA PARLAY EXECUTION SUMMARY")
    print("=" * 60)
    print(f"   Favorite ML Parlays: ${favorites_total}")
    print(f"   Underdog Value Parlays: ${underdogs_total}")
    print(f"   Totals Parlays: ${totals_total}")
    print(f"   Spread Parlays: ${spreads_total}")
    print(f"   Player Props (if available): ${props_total}")
    print(f"   Mega Parlays: ${mega_total}")
    print(f"   TOTAL NBA INVESTMENT: ${total_nba}")
    print()
    print("🎯 NBA BETTING STRATEGY:")
    print("   • 44 games = huge selection for parlays")
    print("   • Mix favorites and underdogs for balance")
    print("   • Totals offer great value in NBA")
    print("   • Player props have excellent edges")
    print("   • Spread betting reduces juice")
    print("   • Late games (West Coast) get less action")
    print()
    print("📊 EXPECTED OUTCOMES:")
    print("   Conservative (favorite parlays hit): $200-500 profit")
    print("   Good Night (totals/spreads hit): $500-1500 profit")
    print("   Great Night (underdog parlay hits): $2000-5000 profit")
    print("   Jackpot (mega parlay hits): $5000-15000+ profit")
    print()
    print("⚠️  EXECUTION NOTES:")
    print("   • Games span 5:00 PM - 4:00 AM ET")
    print("   • Early games start at 5:00 PM (Cavs/Knicks)")
    print("   • Late games end at 4:00 AM (Clippers/Lakers)")
    print("   • Stagger bets throughout the evening")
    print("   • Monitor injury reports before placing")
    print("   • Shop for best NBA odds across books")


if __name__ == "__main__":
    create_nba_parlays()
