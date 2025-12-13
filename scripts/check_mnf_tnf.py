import json
import os
from datetime import datetime

def find_mnf_tnf():
    path = os.path.join("logs", "odds_americanfootball_nfl.json")
    if not os.path.exists(path):
        print("No NFL odds data found.")
        return

    with open(path, "r") as f:
        data = json.load(f)

    # Monday Night Football (Dec 8th US time -> Dec 9th UTC usually, or late Dec 8th)
    # Thursday Night Football (Dec 11th US time -> Dec 12th UTC usually)
    
    mnf_games = []
    tnf_games = []
    
    print(f"Scanning {len(data)} NFL games...")

    for event in data:
        start_time = event['commence_time']
        # Simple string check for dates
        if "2025-12-09" in start_time: # MNF is usually Tuesday morning UTC
            mnf_games.append(event)
        elif "2025-12-12" in start_time: # TNF is usually Friday morning UTC
            tnf_games.append(event)
            
    print(f"\n🏈 MONDAY NIGHT FOOTBALL (Dec 8)")
    if mnf_games:
        for game in mnf_games:
            print_game_odds(game)
    else:
        print("No games found for Monday night.")

    print(f"\n🏈 THURSDAY NIGHT FOOTBALL (Dec 11)")
    if tnf_games:
        for game in tnf_games:
            print_game_odds(game)
    else:
        print("No games found for Thursday night.")

def print_game_odds(event):
    home = event['home_team']
    away = event['away_team']
    print(f"⚔️  {away} vs {home}")
    
    best_home = -1
    best_away = -1
    home_book = ""
    away_book = ""
    
    for book in event['bookmakers']:
        for market in book['markets']:
            if market['key'] == 'h2h':
                for outcome in market['outcomes']:
                    if outcome['name'] == home:
                        if outcome['price'] > best_home:
                            best_home = outcome['price']
                            home_book = book['title']
                    elif outcome['name'] == away:
                        if outcome['price'] > best_away:
                            best_away = outcome['price']
                            away_book = book['title']
                            
    print(f"   💵 {away}: {best_away} ({away_book})")
    print(f"   💵 {home}: {best_home} ({home_book})")
    print("-" * 40)

if __name__ == "__main__":
    find_mnf_tnf()
