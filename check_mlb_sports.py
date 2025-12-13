#!/usr/bin/env python3
"""
Quick script to check available MLB sports from The-Odds-API
"""

import os

import requests

api_key = os.getenv("ODDS_API_KEY")
if not api_key:
    print("❌ No ODDS_API_KEY found")
    exit(1)

print("🔍 Checking available sports from The-Odds-API...")

url = "https://api.the-odds-api.com/v4/sports"
params = {"apiKey": api_key}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    sports = response.json()

    # Filter for MLB/Baseball sports
    mlb_sports = [
        s
        for s in sports
        if "baseball" in s.get("key", "").lower() or "mlb" in s.get("key", "").lower()
    ]

    print("\n⚾ MLB/Baseball sports available:")
    for sport in mlb_sports:
        status = "✅ Active" if sport["active"] else "❌ Inactive"
        print(f"  📋 {sport['key']}: {sport['title']} - {status}")

    print(f"\n📊 Total sports found: {len(sports)}")
    print(f"📊 Baseball sports found: {len(mlb_sports)}")

    # Try to fetch games for each baseball sport
    print("\n🔍 Checking games for each baseball sport...")
    for sport in mlb_sports:
        if sport["active"]:
            games_url = f"https://api.the-odds-api.com/v4/sports/{sport['key']}/odds"
            games_params = {
                "apiKey": api_key,
                "regions": "us",
                "markets": "h2h",
                "oddsFormat": "american",
            }

            try:
                games_response = requests.get(games_url, params=games_params)
                games_response.raise_for_status()
                games = games_response.json()

                print(f"  🎯 {sport['key']}: {len(games)} games found")

                # Show first few games with dates
                for i, game in enumerate(games[:3]):
                    away = game.get("away_team", "Unknown")
                    home = game.get("home_team", "Unknown")
                    start_time = game.get("commence_time", "Unknown")
                    print(f"    {i + 1}. {away} @ {home} - {start_time}")

                if len(games) > 3:
                    print(f"    ... and {len(games) - 3} more games")

            except Exception as e:
                print(f"  ❌ {sport['key']}: Error fetching games - {e}")

except Exception as e:
    print(f"❌ Error: {e}")
