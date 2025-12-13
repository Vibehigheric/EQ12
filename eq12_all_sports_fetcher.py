#!/usr/bin/env python3
"""
EQ12 Complete Sports Odds Fetcher - October 8, 2025
Pull ALL games: MLB, NHL, NCAAF, WNBA, and Preseason NBA
"""

import argparse
import json
import logging
import os
from datetime import datetime

import requests


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    return logging.getLogger(__name__)


def fetch_all_sports_odds(api_key=None):
    """Fetch odds for all available sports"""
    logger = setup_logging()

    if not api_key:
        api_key = os.getenv("ODDS_API_KEY")
        if not api_key:
            logger.error("No API key found. Set ODDS_API_KEY environment variable.")
            return None

    # Sports to fetch
    sports = {
        "baseball_mlb": "MLB",
        "icehockey_nhl": "NHL",
        "americanfootball_ncaaf": "NCAAF",
        "basketball_wnba": "WNBA",
        "basketball_nba": "NBA (including preseason)",
    }

    base_url = "https://api.the-odds-api.com/v4/sports"

    all_games = {}

    for sport_key, sport_name in sports.items():
        logger.info(f"Fetching {sport_name} odds...")

        params = {
            "api_key": api_key,
            "regions": "us",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american",
            "dateFormat": "iso",
        }

        url = f"{base_url}/{sport_key}/odds"

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data:
                all_games[sport_key] = {"sport_name": sport_name, "games": data, "count": len(data)}
                logger.info(f"✅ {sport_name}: {len(data)} games found")
            else:
                logger.warning(f"⚠️  {sport_name}: No games found")
                all_games[sport_key] = {"sport_name": sport_name, "games": [], "count": 0}

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching {sport_name}: {e}")
            all_games[sport_key] = {
                "sport_name": sport_name,
                "games": [],
                "count": 0,
                "error": str(e),
            }

    return all_games


def save_odds_data(all_games):
    """Save odds data to files"""
    logger = setup_logging()

    # Ensure logs directory exists
    os.makedirs("C:\\EQ12\\logs", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save combined data
    combined_file = f"C:\\EQ12\\logs\\all_sports_odds_{timestamp}.json"
    with open(combined_file, "w") as f:
        json.dump(all_games, f, indent=2)

    logger.info(f"📁 Combined odds saved to: {combined_file}")

    # Save individual sport files
    for sport_key, sport_data in all_games.items():
        if sport_data["games"]:
            sport_file = f"C:\\EQ12\\logs\\{sport_key}_odds_{timestamp}.json"
            with open(sport_file, "w") as f:
                json.dump(sport_data["games"], f, indent=2)
            logger.info(f"📁 {sport_data['sport_name']} odds saved to: {sport_file}")

    return combined_file


def display_summary(all_games):
    """Display summary of fetched games"""

    print("🎯 EQ12 ALL SPORTS ODDS FETCH COMPLETE")
    print("=" * 80)
    print(f"📅 {datetime.now().strftime('%A, %B %d, %Y - %I:%M %p ET')}")
    print()

    total_games = 0
    for _sport_key, sport_data in all_games.items():
        count = sport_data.get("count", 0)
        total_games += count

        if "error" in sport_data:
            print(f"❌ {sport_data['sport_name']}: Error - {sport_data['error']}")
        elif count > 0:
            print(f"✅ {sport_data['sport_name']}: {count} games")
        else:
            print(f"⚠️  {sport_data['sport_name']}: No games found")

    print(f"\n📊 TOTAL GAMES ACROSS ALL SPORTS: {total_games}")
    print()

    if total_games > 0:
        print("🎯 NEXT STEPS:")
        print("   1. ✅ All odds data saved to logs directory")
        print("   2. 🎲 Ready to create comprehensive parlays")
        print("   3. 🚀 Include preseason NBA games if available")
        print("   4. 💰 Build ultimate cross-sport combinations")
    else:
        print("⚠️  No games found across any sports!")
        print("   • Check API key validity")
        print("   • Verify sports are in season")
        print("   • Check network connectivity")


def main():
    parser = argparse.ArgumentParser(description="Fetch odds for all sports")
    parser.add_argument("--api-key", help="The Odds API key")
    parser.add_argument("--save-only", action="store_true", help="Only save data, no display")

    args = parser.parse_args()

    print("🎯 EQ12 ALL SPORTS ODDS FETCHER")
    print("=" * 50)
    print("Fetching: MLB, NHL, NCAAF, WNBA, NBA (preseason)")
    print()

    # Fetch all odds
    all_games = fetch_all_sports_odds(args.api_key)

    if all_games is None:
        print("❌ Failed to fetch odds data")
        return 1

    # Save the data
    save_odds_data(all_games)

    # Display summary unless save-only mode
    if not args.save_only:
        display_summary(all_games)

    return 0


if __name__ == "__main__":
    exit(main())
