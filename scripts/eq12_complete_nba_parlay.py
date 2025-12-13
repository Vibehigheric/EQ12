#!/usr/bin/env python3
"""
EQ12 Complete Tonight NBA Parlay Builder
All games after 9 PM ET with $5 to hit $500+ target
"""

def american_to_decimal(american_odds: int) -> float:
    if american_odds > 0:
        return (american_odds / 100.0) + 1.0
    else:
        return (100.0 / abs(american_odds)) + 1.0

def calculate_parlay(legs_odds: list, stake=5.0) -> dict:
    """Calculate parlay with list of American odds."""
    decimal = 1.0
    for odds in legs_odds:
        decimal *= american_to_decimal(odds)
    
    american = int((decimal - 1) * 100) if decimal >= 2 else int(-100/(decimal - 1))
    payout = stake * decimal
    profit = payout - stake
    probability = (1.0 / decimal) * 100
    
    return {
        'decimal': round(decimal, 2),
        'american': american,
        'payout': round(payout, 2),
        'profit': round(profit, 2),
        'probability': round(probability, 2)
    }

print("\n" + "="*80)
print("🏀 COMPLETE NBA PARLAY BUILDER - ALL GAMES AFTER 9 PM ET")
print("="*80)
print("Goal: Turn $5 into $500+")
print("Strategy: Combine multiple underdogs across different games")
print("="*80)

# Available games (9 PM+ ET)
games = {
    'PHO @ OKC': {'underdog': 'Phoenix Suns', 'odds': +775, 'time': '9:40 PM'},
    'SAC @ UTA': {'underdog': 'Sacramento Kings', 'odds': +145, 'time': '9:41 PM'},
    'SAS @ DEN': {'underdog': 'San Antonio Spurs', 'odds': +235, 'time': '9:41 PM'},
    'DAL @ LAL': {'underdog': 'Dallas Mavericks', 'odds': +343, 'time': '10:10 PM'},
    'MEM @ LAC': {'underdog': 'Memphis Grizzlies', 'odds': +220, 'time': '10:10 PM'},
}

print("\n📊 TONIGHT'S UNDERDOGS (9 PM+ ET):")
print("-" * 80)
for game, info in games.items():
    print(f"{info['time']} - {game}")
    print(f"  Underdog: {info['underdog']} ({info['odds']:+d})")

print("\n" + "="*80)
print("💎 PARLAY OPTIONS TO HIT $500+")
print("="*80)

parlays = []

# OPTION 1: Top 2 biggest underdogs
print("\n✅ OPTION 1: TWO BIGGEST UNDERDOGS")
print("-" * 80)
legs = [775, 343]  # PHO, DAL
result = calculate_parlay(legs)
print(f"Leg 1: Phoenix Suns +775 @ OKC (9:40 PM)")
print(f"Leg 2: Dallas Mavericks +343 @ Lakers (10:10 PM)")
print(f"Combined Odds: {result['american']:+d} ({result['decimal']:.1f}:1)")
print(f"Payout: ${result['payout']:.2f}")
print(f"Profit: ${result['profit']:.2f}")
print(f"Win Probability: {result['probability']:.1f}%")
if result['profit'] >= 500:
    print("🎯 HITS $500 TARGET! ✅")
else:
    print(f"❌ Short by ${500 - result['profit']:.2f}")
parlays.append(('Option 1: PHO + DAL', result, legs))

# OPTION 2: Top 3 biggest
print("\n✅ OPTION 2: THREE BIGGEST UNDERDOGS")
print("-" * 80)
legs = [775, 343, 235]  # PHO, DAL, SAS
result = calculate_parlay(legs)
print(f"Leg 1: Phoenix Suns +775 @ OKC (9:40 PM)")
print(f"Leg 2: Dallas Mavericks +343 @ Lakers (10:10 PM)")
print(f"Leg 3: San Antonio Spurs +235 @ Nuggets (9:41 PM)")
print(f"Combined Odds: {result['american']:+d} ({result['decimal']:.1f}:1)")
print(f"Payout: ${result['payout']:.2f}")
print(f"Profit: ${result['profit']:.2f}")
print(f"Win Probability: {result['probability']:.1f}%")
if result['profit'] >= 500:
    print("🎯 HITS $500 TARGET! ✅")
else:
    print(f"❌ Short by ${500 - result['profit']:.2f}")
parlays.append(('Option 2: PHO + DAL + SAS', result, legs))

# OPTION 3: Top 4 underdogs
print("\n✅ OPTION 3: FOUR BIGGEST UNDERDOGS")
print("-" * 80)
legs = [775, 343, 235, 220]  # PHO, DAL, SAS, MEM
result = calculate_parlay(legs)
print(f"Leg 1: Phoenix Suns +775 @ OKC (9:40 PM)")
print(f"Leg 2: Dallas Mavericks +343 @ Lakers (10:10 PM)")
print(f"Leg 3: San Antonio Spurs +235 @ Nuggets (9:41 PM)")
print(f"Leg 4: Memphis Grizzlies +220 @ Clippers (10:10 PM)")
print(f"Combined Odds: {result['american']:+d} ({result['decimal']:.1f}:1)")
print(f"Payout: ${result['payout']:.2f}")
print(f"Profit: ${result['profit']:.2f}")
print(f"Win Probability: {result['probability']:.1f}%")
if result['profit'] >= 500:
    print("🎯 HITS $500 TARGET! ✅")
else:
    print(f"❌ Short by ${500 - result['profit']:.2f}")
parlays.append(('Option 3: PHO + DAL + SAS + MEM', result, legs))

# OPTION 4: All 5 underdogs
print("\n✅ OPTION 4: ALL FIVE UNDERDOGS (MEGA PARLAY)")
print("-" * 80)
legs = [775, 343, 235, 220, 145]  # PHO, DAL, SAS, MEM, SAC
result = calculate_parlay(legs)
print(f"Leg 1: Phoenix Suns +775 @ OKC (9:40 PM)")
print(f"Leg 2: Dallas Mavericks +343 @ Lakers (10:10 PM)")
print(f"Leg 3: San Antonio Spurs +235 @ Nuggets (9:41 PM)")
print(f"Leg 4: Memphis Grizzlies +220 @ Clippers (10:10 PM)")
print(f"Leg 5: Sacramento Kings +145 @ Jazz (9:41 PM)")
print(f"Combined Odds: {result['american']:+d} ({result['decimal']:.1f}:1)")
print(f"Payout: ${result['payout']:.2f}")
print(f"Profit: ${result['profit']:.2f}")
print(f"Win Probability: {result['probability']:.2f}%")
if result['profit'] >= 500:
    print("🎯 HITS $500 TARGET! ✅")
else:
    print(f"❌ Short by ${500 - result['profit']:.2f}")
parlays.append(('Option 4: ALL 5 UNDERDOGS', result, legs))

# OPTION 5: More realistic combo (skip biggest longshot PHO +775)
print("\n✅ OPTION 5: REALISTIC MIX (Skip PHO +775 longshot)")
print("-" * 80)
legs = [343, 235, 220, 145]  # DAL, SAS, MEM, SAC
result = calculate_parlay(legs)
print(f"Leg 1: Dallas Mavericks +343 @ Lakers (10:10 PM)")
print(f"Leg 2: San Antonio Spurs +235 @ Nuggets (9:41 PM)")
print(f"Leg 3: Memphis Grizzlies +220 @ Clippers (10:10 PM)")
print(f"Leg 4: Sacramento Kings +145 @ Jazz (9:41 PM)")
print(f"Combined Odds: {result['american']:+d} ({result['decimal']:.1f}:1)")
print(f"Payout: ${result['payout']:.2f}")
print(f"Profit: ${result['profit']:.2f}")
print(f"Win Probability: {result['probability']:.2f}%")
if result['profit'] >= 500:
    print("🎯 HITS $500 TARGET! ✅")
else:
    print(f"❌ Short by ${500 - result['profit']:.2f}")
parlays.append(('Option 5: DAL + SAS + MEM + SAC', result, legs))

# OPTION 6: Just SAC + moderate underdogs
print("\n✅ OPTION 6: BALANCED APPROACH (Most Realistic)")
print("-" * 80)
legs = [235, 220, 145]  # SAS, MEM, SAC
result = calculate_parlay(legs)
print(f"Leg 1: San Antonio Spurs +235 @ Nuggets (9:41 PM)")
print(f"Leg 2: Memphis Grizzlies +220 @ Clippers (10:10 PM)")
print(f"Leg 3: Sacramento Kings +145 @ Jazz (9:41 PM)")
print(f"Combined Odds: {result['american']:+d} ({result['decimal']:.1f}:1)")
print(f"Payout: ${result['payout']:.2f}")
print(f"Profit: ${result['profit']:.2f}")
print(f"Win Probability: {result['probability']:.1f}%")
if result['profit'] >= 500:
    print("🎯 HITS $500 TARGET! ✅")
else:
    print(f"❌ Short by ${500 - result['profit']:.2f}")
parlays.append(('Option 6: SAS + MEM + SAC', result, legs))

print("\n" + "="*80)
print("📊 SUMMARY: WHICH PARLAYS HIT $500 TARGET?")
print("="*80)
print(f"\n{'Option':<40} {'Payout':<12} {'Profit':<12} {'Prob':<8} {'Hits $500?'}")
print("-" * 80)

for name, result, _ in parlays:
    hits = "✅ YES" if result['profit'] >= 500 else "❌ NO"
    print(f"{name:<40} ${result['payout']:<11.2f} ${result['profit']:<11.2f} {result['probability']:<7.2f}% {hits}")

print("\n" + "="*80)
print("🎯 RECOMMENDATION")
print("="*80)

# Find best option that hits $500
hits_500 = [p for p in parlays if p[1]['profit'] >= 500]

if hits_500:
    # Sort by probability (highest first)
    hits_500.sort(key=lambda x: x[1]['probability'], reverse=True)
    best = hits_500[0]
    
    print(f"\n🥇 BEST OPTION: {best[0]}")
    print(f"   Payout: ${best[1]['payout']:.2f}")
    print(f"   Profit: ${best[1]['profit']:.2f}")
    print(f"   Probability: {best[1]['probability']:.2f}%")
    print(f"\n   Why: Highest probability parlay that hits $500+ target")
else:
    print("\n⚠️  NO PARLAY HITS $500 TARGET")
    print("\n   Closest option:")
    closest = max(parlays, key=lambda x: x[1]['profit'])
    print(f"   {closest[0]}")
    print(f"   Profit: ${closest[1]['profit']:.2f}")
    print(f"   Short by: ${500 - closest[1]['profit']:.2f}")

print("\n" + "="*80)
print("💡 TEAM ANALYSIS")
print("="*80)
print("\n🏀 Sacramento Kings (+145) @ Utah Jazz")
print("   ✅ SAC is 13-13, competitive")
print("   ✅ Utah struggling at 5-20")
print("   ✅ Most likely upset")
print("")
print("🏀 Memphis Grizzlies (+220) @ LA Clippers")
print("   ✅ MEM is 16-9, elite")
print("   ⚠️  Clippers at home, but beatable")
print("   ✅ Ja Morant playing well")
print("")
print("🏀 San Antonio Spurs (+235) @ Denver Nuggets")
print("   ✅ Wembanyama can dominate any game")
print("   ⚠️  Nuggets at altitude advantage")
print("   ⚖️  50/50 upset potential")
print("")
print("🏀 Dallas Mavericks (+343) @ LA Lakers")
print("   ✅ Luka Doncic can carry team")
print("   ⚠️  Lakers at home with LeBron/AD")
print("   ⚖️  Possible but tough")
print("")
print("🏀 Phoenix Suns (+775) @ OKC Thunder")
print("   ⚠️  OKC is 20-5, elite at home")
print("   ⚠️  Phoenix struggling 10-15")
print("   ❌ Least likely upset")

print("\n" + "="*80)
print("⚠️  FINAL WARNINGS")
print("="*80)
print("• ALL legs must win for payout")
print("• Parlays with 3+ legs have <5% win probability")
print("• This is high-risk gambling")
print("• Only bet what you can afford to lose")
print("• Expected outcome: Lose $5")
print("="*80)
