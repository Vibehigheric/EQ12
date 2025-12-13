import requests
import json
from datetime import datetime, timezone, timedelta

API_KEY = "c32c9644050b2240081428b43e7016ce"

r = requests.get(
    'https://api.the-odds-api.com/v4/sports/basketball_nba/odds',
    params={
        'apiKey': API_KEY,
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'american'
    }
)

games = r.json()

print("\n" + "="*80)
print("🏀 ALL NBA GAMES TONIGHT (Nov 28/29, 2025)")
print("="*80)

tonight_games = []
for g in games:
    commence_time = datetime.fromisoformat(g['commence_time'].replace('Z', '+00:00'))
    
    # Convert to ET
    et_time = commence_time - timedelta(hours=5)
    
    # Get best odds
    best_away_odds = None
    best_home_odds = None
    
    for bookmaker in g.get('bookmakers', []):
        for market in bookmaker.get('markets', []):
            if market['key'] == 'h2h':
                for outcome in market['outcomes']:
                    if outcome['name'] == g['away_team']:
                        if best_away_odds is None or abs(outcome['price']) > abs(best_away_odds):
                            best_away_odds = outcome['price']
                    elif outcome['name'] == g['home_team']:
                        if best_home_odds is None or abs(outcome['price']) > abs(best_home_odds):
                            best_home_odds = outcome['price']
    
    game_info = {
        'commence_utc': commence_time,
        'commence_et': et_time,
        'away_team': g['away_team'],
        'home_team': g['home_team'],
        'away_odds': best_away_odds,
        'home_odds': best_home_odds
    }
    
    tonight_games.append(game_info)

# Sort by time
tonight_games.sort(key=lambda x: x['commence_et'])

# Filter for games after 9 PM ET
after_9pm = [g for g in tonight_games if g['commence_et'].hour >= 21]

print(f"\nTotal games tonight: {len(tonight_games)}")
print(f"Games starting at or after 9 PM ET: {len(after_9pm)}")

print("\n" + "="*80)
print("⏰ GAMES AFTER 9 PM ET")
print("="*80)

for g in after_9pm:
    time_str = g['commence_et'].strftime('%I:%M %p ET')
    print(f"\n{time_str}")
    print(f"  {g['away_team']} @ {g['home_team']}")
    if g['away_odds'] and g['home_odds']:
        print(f"  Odds: {g['away_team']} {g['away_odds']:+d} / {g['home_team']} {g['home_odds']:+d}")
        
        # Identify underdog
        if g['away_odds'] > 0:
            print(f"  ⭐ Underdog: {g['away_team']} ({g['away_odds']:+d})")
        elif g['home_odds'] > 0:
            print(f"  ⭐ Underdog: {g['home_team']} ({g['home_odds']:+d})")

print("\n" + "="*80)
print("💡 BEST UNDERDOGS FOR PARLAY")
print("="*80)

underdogs = []
for g in after_9pm:
    if g['away_odds'] and g['away_odds'] > 0:
        underdogs.append({
            'team': g['away_team'],
            'opponent': g['home_team'],
            'odds': g['away_odds'],
            'time': g['commence_et'].strftime('%I:%M %p ET')
        })
    if g['home_odds'] and g['home_odds'] > 0:
        underdogs.append({
            'team': g['home_team'],
            'opponent': g['away_team'],
            'odds': g['home_odds'],
            'time': g['commence_et'].strftime('%I:%M %p ET')
        })

underdogs.sort(key=lambda x: x['odds'], reverse=True)

for i, dog in enumerate(underdogs[:5], 1):
    print(f"{i}. {dog['team']} ({dog['odds']:+d}) vs {dog['opponent']} - {dog['time']}")

# Save to file
with open("../reports/tonight_all_nba_games.json", "w") as f:
    json.dump({
        'total_games': len(tonight_games),
        'after_9pm': len(after_9pm),
        'games': [
            {
                'time_et': g['commence_et'].strftime('%I:%M %p ET'),
                'away_team': g['away_team'],
                'home_team': g['home_team'],
                'away_odds': g['away_odds'],
                'home_odds': g['home_odds']
            }
            for g in after_9pm
        ],
        'underdogs': underdogs
    }, f, indent=2)

print(f"\n✅ Full data saved: reports/tonight_all_nba_games.json")
