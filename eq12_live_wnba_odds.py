#!/usr/bin/env python3
"""
EQ12 Live WNBA Odds Fetcher - October 8, 2025
Pull actual WNBA games and odds from The Odds API
"""

import json
import os
from datetime import datetime

import requests


def fetch_wnba_odds():
    """Fetch live WNBA odds from The Odds API"""

    print("🏀 EQ12 LIVE WNBA ODDS FETCHER - OCTOBER 8, 2025")
    print("=" * 80)
    print("📡 Connecting to The Odds API for live WNBA data...")
    print()

    # Get API key from environment
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        print("⚠️ ERROR: ODDS_API_KEY environment variable not found!")
        print("🔧 Please set your API key: $env:ODDS_API_KEY = 'your_key_here'")
        return

    # The Odds API endpoint for WNBA
    base_url = "https://api.the-odds-api.com/v4/sports/basketball_wnba/odds"

    params = {
        "apiKey": api_key,
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "american",
        "dateFormat": "iso",
        "bookmakers": "draftkings,fanduel,betmgm",
    }

    try:
        print("🔍 Searching for WNBA games...")
        response = requests.get(base_url, params=params, timeout=10)

        if response.status_code == 200:
            games = response.json()
            print(f"✅ API Response: {len(games)} WNBA games found")
            print()

            if len(games) == 0:
                print("📊 WNBA GAMES STATUS:")
                print("-" * 60)
                print("⚠️  NO WNBA GAMES AVAILABLE ON OCTOBER 8, 2025")
                print()
                print("📅 WNBA Season Context:")
                print("   • WNBA regular season: May - September")
                print("   • WNBA playoffs: September - October")
                print("   • WNBA Finals: Usually mid-October")
                print("   • Off-season: November - April")
                print()
                print("🔍 Possible Reasons for No Games:")
                print("   1. Regular season ended in September")
                print("   2. Playoffs concluded")
                print("   3. Between playoff rounds")
                print("   4. Finals not yet started")
                print("   5. Off-season exhibitions only")
                print()
                print("🏀 ALTERNATIVE BETTING OPTIONS:")
                print("   • NBA (starting soon)")
                print("   • Women's College Basketball (November start)")
                print("   • International women's leagues")
                print("   • WNBA futures/awards betting")
                return

            print(f"🏀 LIVE WNBA GAMES FOUND: {len(games)}")
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

            # Create WNBA parlays if games exist
            if len(games) >= 2:
                print("🎫 SUGGESTED WNBA PARLAYS:")
                print("-" * 60)
                create_wnba_parlays(games)

        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")


def create_wnba_parlays(games):
    """Create WNBA parlays from available games"""

    if len(games) >= 2:
        print("1. WNBA Favorites Parlay")
        print("   🔗 Combine all favorite MLs")
        print("   💰 Conservative approach")
        print()

        print("2. WNBA Over/Under Parlay")
        print("   🔗 All game totals (mix of overs/unders)")
        print("   💰 Moderate risk")
        print()

        print("3. WNBA Mixed Parlay")
        print("   🔗 Best ML + spread + total picks")
        print("   💰 Balanced approach")
        print()

    if len(games) >= 3:
        print("4. WNBA Round Robin")
        print("   🔗 Multiple 2-team combinations")
        print("   💰 Higher hit rate strategy")
        print()

    print("💡 WNBA BETTING TIPS:")
    print("   • Lower scoring than NBA (avg 80-85 points)")
    print("   • Home court advantage significant")
    print("   • Star player props often have value")
    print("   • Playoff intensity increases variance")
    print("   • Check for rest/travel situations")


def save_wnba_data(games):
    """Save WNBA data to logs"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"C:\\EQ12\\logs\\wnba_odds_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(games, f, indent=2)

    print(f"💾 WNBA data saved to: {filename}")


if __name__ == "__main__":
    fetch_wnba_odds()
