#!/usr/bin/env python3
"""
EQ12 All Sports Game Date Filter - October 8, 2025
Check which games are actually happening TODAY across all sports
"""

import json


def check_all_game_dates():
    """Check which games from all sports are actually TODAY (October 8, 2025)"""

    print("🎯 EQ12 ALL SPORTS DATE FILTER - OCTOBER 8, 2025")
    print("=" * 80)

    # Load the combined sports data
    try:
        with open(r"C:\EQ12\logs\all_sports_odds_20251008_185037.json") as f:
            all_sports_data = json.load(f)

        today_games = {}
        future_games = {}
        total_today = 0

        for sport_key, sport_info in all_sports_data.items():
            sport_name = sport_info.get("sport_name", sport_key)
            games = sport_info.get("games", [])

            today_games[sport_key] = []
            future_games[sport_key] = []

            for game in games:
                commence_time = game.get("commence_time", "")
                game_date = commence_time.split("T")[0] if "T" in commence_time else ""

                home_team = game.get("home_team", "")
                away_team = game.get("away_team", "")

                game_info = {
                    "home": home_team,
                    "away": away_team,
                    "time": commence_time,
                    "date": game_date,
                }

                if game_date == "2025-10-08":
                    today_games[sport_key].append(game_info)
                    total_today += 1
                else:
                    future_games[sport_key].append(game_info)

            # Display results for this sport
            today_count = len(today_games[sport_key])
            future_count = len(future_games[sport_key])

            print(f"📊 {sport_name.upper()}:")
            print(f"   📅 TODAY (Oct 8): {today_count} games")

            if today_count > 0:
                for i, game in enumerate(today_games[sport_key][:5], 1):  # Show first 5
                    time_only = game["time"].split("T")[1][:5] if "T" in game["time"] else "TBD"
                    print(f"      {i}. {game['away']} @ {game['home']} - {time_only} UTC")
                if today_count > 5:
                    print(f"      ... and {today_count - 5} more games")

            print(f"   📅 FUTURE: {future_count} games")
            if future_count > 0:
                # Show next game date
                next_dates = list({g["date"] for g in future_games[sport_key] if g["date"]})
                if next_dates:
                    print(f"      Next games: {min(next_dates)}")
            print()

        print("🎯 TODAY'S GAMES SUMMARY:")
        print("=" * 60)
        for sport_key, games in today_games.items():
            sport_name = all_sports_data[sport_key]["sport_name"]
            count = len(games)
            if count > 0:
                print(f"   ✅ {sport_name}: {count} games TODAY")
            else:
                print(f"   ❌ {sport_name}: No games today")

        print(f"\n📊 TOTAL GAMES TODAY: {total_today}")

        if total_today > 0:
            print("\n🎲 PARLAY OPPORTUNITIES:")
            print(f"   • {total_today} total games for parlay combinations")
            print("   • Multiple sports = cross-sport parlays possible")
            print("   • All games finish by midnight ET")
            print("   • Perfect for today's betting action!")
        else:
            print("\n⚠️  NO GAMES TODAY ACROSS ANY SPORTS!")
            print("   • All games appear to be scheduled for future dates")
            print("   • Check individual sport schedules")
            print("   • May need to wait for scheduled game days")

        return today_games, total_today

    except FileNotFoundError:
        print("❌ Could not find combined sports odds file")
        print("   Run eq12_all_sports_fetcher.py first")
        return None, 0
    except Exception as e:
        print(f"❌ Error reading sports data: {e}")
        return None, 0


if __name__ == "__main__":
    check_all_game_dates()
