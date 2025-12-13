#!/usr/bin/env python3
"""
Check NBA game dates to filter for today's games only
"""

import json


def check_nba_dates():
    """Check which NBA games are actually today (October 8, 2025)"""

    print("🏀 NBA GAME DATE FILTER - OCTOBER 8, 2025")
    print("=" * 60)

    try:
        with open(r"C:\EQ12\logs\nba_odds_20251008_183225.json") as f:
            nba_data = json.load(f)

        today_games = []
        future_games = []

        for game in nba_data:
            commence_time = game.get("commence_time", "")
            game_date = commence_time.split("T")[0] if "T" in commence_time else ""

            home_team = game.get("home_team", "")
            away_team = game.get("away_team", "")

            if game_date == "2025-10-08":
                today_games.append({"home": home_team, "away": away_team, "time": commence_time})
            else:
                future_games.append(
                    {"home": home_team, "away": away_team, "date": game_date, "time": commence_time}
                )

        print(f"📅 GAMES TODAY (October 8, 2025): {len(today_games)}")
        if today_games:
            for i, game in enumerate(today_games, 1):
                print(f"   {i}. {game['away']} @ {game['home']}")
                print(f"      Time: {game['time']}")
        else:
            print("   ❌ NO NBA GAMES TODAY!")

        print(f"\n📅 FUTURE GAMES: {len(future_games)}")

        # Group by date
        dates = {}
        for game in future_games:
            date = game["date"]
            if date not in dates:
                dates[date] = []
            dates[date].append(game)

        for date in sorted(dates.keys())[:5]:  # Show next 5 dates
            games = dates[date]
            print(f"   📆 {date}: {len(games)} games")
            if len(games) <= 3:  # Show games if not too many
                for game in games:
                    print(f"      • {game['away']} @ {game['home']}")

        print("\n🎯 RECOMMENDATION:")
        if today_games:
            print(f"   ✅ Use {len(today_games)} NBA games for today's parlays")
        else:
            print("   ❌ NO NBA GAMES TODAY - REMOVE NBA FROM SYSTEM")
            print(
                "   📅 Next games appear to be on:", min(dates.keys()) if dates else "unknown date"
            )
            print("   🔄 Focus on MLB, NHL, NCAAF, WNBA only for today")

    except Exception as e:
        print(f"❌ Error reading NBA data: {e}")
        print("📄 Check if file exists: C:\\EQ12\\logs\\nba_odds_20251008_183225.json")


if __name__ == "__main__":
    check_nba_dates()
