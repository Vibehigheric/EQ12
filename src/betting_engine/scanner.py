import requests
import os
import json
from datetime import datetime

# Placeholder for The-Odds-API Key (Should be in env vars)
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "YOUR_API_KEY_HERE")
BASE_URL = "https://api.the-odds-api.com/v4/sports"

def fetch_odds(sport_key="upcoming", regions="us", markets="h2h"):
    """
    Fetches odds from The-Odds-API.
    """
    if ODDS_API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️ ODDS_API_KEY not set. Using mock data.")
        return get_mock_data()

    url = f"{BASE_URL}/{sport_key}/odds"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": regions,
        "markets": markets,
        "oddsFormat": "decimal"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching odds: {e}")
        return []

def get_mock_data():
    """Returns mock data for testing without API key."""
    return [
        {
            "sport_key": "basketball_nba",
            "sport_title": "NBA",
            "commence_time": "2025-12-12T00:00:00Z",
            "home_team": "Los Angeles Lakers",
            "away_team": "Golden State Warriors",
            "bookmakers": [
                {
                    "key": "draftkings",
                    "title": "DraftKings",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Los Angeles Lakers", "price": 1.95},
                                {"name": "Golden State Warriors", "price": 1.90}
                            ]
                        }
                    ]
                },
                {
                    "key": "fanduel",
                    "title": "FanDuel",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Los Angeles Lakers", "price": 2.05}, # Arbitrage opportunity?
                                {"name": "Golden State Warriors", "price": 1.80}
                            ]
                        }
                    ]
                }
            ]
        }
    ]

def scan_for_arbitrage(odds_data):
    """
    Scans for arbitrage opportunities across bookmakers.
    """
    opportunities = []
    
    for event in odds_data:
        home_team = event['home_team']
        away_team = event['away_team']
        
        best_home_odds = 0
        best_home_book = ""
        best_away_odds = 0
        best_away_book = ""
        
        for book in event['bookmakers']:
            for market in book['markets']:
                if market['key'] == 'h2h':
                    for outcome in market['outcomes']:
                        if outcome['name'] == home_team:
                            if outcome['price'] > best_home_odds:
                                best_home_odds = outcome['price']
                                best_home_book = book['title']
                        elif outcome['name'] == away_team:
                            if outcome['price'] > best_away_odds:
                                best_away_odds = outcome['price']
                                best_away_book = book['title']
        
        if best_home_odds > 0 and best_away_odds > 0:
            # Calculate Arbitrage Percentage
            # Arb % = (1/HomeOdds) + (1/AwayOdds)
            arb_percent = (1 / best_home_odds) + (1 / best_away_odds)
            
            if arb_percent < 1.0:
                profit_margin = (1 - arb_percent) * 100
                opportunities.append({
                    "event": f"{away_team} @ {home_team}",
                    "profit_margin": profit_margin,
                    "bet_home": {"book": best_home_book, "odds": best_home_odds, "team": home_team},
                    "bet_away": {"book": best_away_book, "odds": best_away_odds, "team": away_team}
                })
                
    return opportunities

if __name__ == "__main__":
    print("🔍 Scanning for Opportunities...")
    data = fetch_odds()
    arbs = scan_for_arbitrage(data)
    
    if arbs:
        print(f"✅ Found {len(arbs)} Arbitrage Opportunities!")
        for arb in arbs:
            print(f"\n💰 {arb['event']} | Profit: {arb['profit_margin']:.2f}%")
            print(f"   Bet Home: {arb['bet_home']['team']} @ {arb['bet_home']['odds']} ({arb['bet_home']['book']})")
            print(f"   Bet Away: {arb['bet_away']['team']} @ {arb['bet_away']['odds']} ({arb['bet_away']['book']})")
    else:
        print("No arbitrage opportunities found.")
