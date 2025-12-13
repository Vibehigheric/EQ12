import json
import os
from datetime import datetime

def load_odds(sport):
    path = os.path.join("logs", f"odds_{sport}.json")
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def display_bets(sport_name, data):
    print(f"\n🏈 {sport_name.upper()} UPCOMING GAMES & ODDS 🏀")
    print("=" * 60)
    
    # Sort by time
    data.sort(key=lambda x: x['commence_time'])
    
    for event in data[:5]: # Show top 5 upcoming
        home = event['home_team']
        away = event['away_team']
        start = event['commence_time']
        
        # Find best odds
        best_home_price = -1
        best_away_price = -1
        home_book = ""
        away_book = ""
        
        for book in event['bookmakers']:
            for market in book['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        if outcome['name'] == home:
                            if outcome['price'] > best_home_price:
                                best_home_price = outcome['price']
                                home_book = book['title']
                        elif outcome['name'] == away:
                            if outcome['price'] > best_away_price:
                                best_away_price = outcome['price']
                                away_book = book['title']
        
        # Convert decimal to american for display if needed, but decimal is standard for calc
        # Simple display
        print(f"⚔️  {away} vs {home}")
        print(f"   ⏰ {start}")
        print(f"   💵 {away}: {best_away_price} ({away_book})")
        print(f"   💵 {home}: {best_home_price} ({home_book}")
        print("-" * 40)

def main():
    nfl = load_odds("americanfootball_nfl")
    if nfl:
        display_bets("NFL", nfl)
    
    nba = load_odds("basketball_nba")
    if nba:
        display_bets("NBA", nba)

if __name__ == "__main__":
    main()
