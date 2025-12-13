#!/usr/bin/env python3
"""
EQ12 Live NBA Odds Fetcher - October 8, 2025
Pull actual NBA games and odds from The Odds API
"""

import json
import os
from datetime import datetime

import requests


def fetch_nba_odds():
    """Fetch live NBA odds from The Odds API"""

    print("🏀 EQ12 LIVE NBA ODDS FETCHER - OCTOBER 8, 2025")
    print("=" * 80)
    print("📡 Connecting to The Odds API for live NBA data...")
    print()

    # Get API key from environment
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        print("⚠️ ERROR: ODDS_API_KEY environment variable not found!")
        print("🔧 Please set your API key: $env:ODDS_API_KEY = 'your_key_here'")
        return []

    # The Odds API endpoint for NBA
    base_url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"

    params = {
        "apiKey": api_key,
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "american",
        "dateFormat": "iso",
        "bookmakers": "draftkings,fanduel,betmgm",
    }

    try:
        print("🔍 Searching for NBA games...")
        response = requests.get(base_url, params=params, timeout=10)

        if response.status_code == 200:
            games = response.json()
            print(f"✅ API Response: {len(games)} NBA games found")
            print()

            if len(games) == 0:
                print("📊 NBA GAMES STATUS:")
                print("-" * 60)
                print("⚠️  NO NBA GAMES AVAILABLE ON OCTOBER 8, 2025")
                print()
                print("📅 NBA Season Context:")
                print("   • NBA preseason: September - October")
                print("   • NBA regular season: October - April")
                print("   • NBA playoffs: April - June")
                print("   • Off-season: July - September")
                print()
                print("🔍 Possible Reasons for No Games:")
                print("   1. Early preseason schedule")
                print("   2. Between preseason and regular season")
                print("   3. Rest day in schedule")
                print("   4. International games not covered")
                print()
                return []

            print(f"🏀 LIVE NBA GAMES FOUND: {len(games)}")
            print("=" * 60)

            for i, game in enumerate(games, 1):
                home_team = game["home_team"]
                away_team = game["away_team"]
                commence_time = game["commence_time"]

                # Parse game time
                game_time = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
                formatted_time = game_time.strftime("%I:%M %p ET")

                print(f"{i}. {away_team} @ {home_team}")
                print(f"   🕐 Time: {formatted_time}")

                # Process bookmaker odds
                if game["bookmakers"]:
                    bookmaker = game["bookmakers"][0]  # Use first bookmaker
                    print(f"   📊 Odds ({bookmaker['title']}):")

                    for market in bookmaker["markets"]:
                        if market["key"] == "h2h":
                            # Moneyline odds
                            for outcome in market["outcomes"]:
                                team = outcome["name"]
                                odds = outcome["price"]
                                odds_str = f"+{odds}" if odds > 0 else str(odds)
                                print(f"      💰 {team} ML: {odds_str}")

                        elif market["key"] == "spreads":
                            # Spread odds
                            for outcome in market["outcomes"]:
                                team = outcome["name"]
                                point = outcome["point"]
                                odds = outcome["price"]
                                odds_str = f"+{odds}" if odds > 0 else str(odds)
                                print(f"      📈 {team} {point:+g}: {odds_str}")

                        elif market["key"] == "totals":
                            # Total odds
                            for outcome in market["outcomes"]:
                                over_under = outcome["name"]
                                total = outcome["point"]
                                odds = outcome["price"]
                                odds_str = f"+{odds}" if odds > 0 else str(odds)
                                print(f"      📊 {over_under} {total}: {odds_str}")

                print()

            # Save data for parlay creation
            save_nba_data(games)
            return games

        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return []


def save_nba_data(games):
    """Save NBA data to logs"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"C:\\EQ12\\logs\\nba_odds_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(games, f, indent=2)

    print(f"💾 NBA data saved to: {filename}")


if __name__ == "__main__":
    nba_games = fetch_nba_odds()
    if nba_games:
        print(f"🎯 Found {len(nba_games)} NBA games ready for parlay creation!")
    else:
        print("⚠️ No NBA games available for parlays today.")
