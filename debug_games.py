#!/usr/bin/env python3
"""
Debug script to see what games are actually available
"""

from datetime import UTC, datetime

from eq12_odds_ingestor import OddsIngestor


def debug_games():
    """Debug what games we're getting"""
    ingestor = OddsIngestor()

    sports = {"baseball_mlb": "MLB", "icehockey_nhl": "NHL", "americanfootball_ncaaf": "NCAAF"}

    now = datetime.now(UTC)
    print(f"Current time (UTC): {now}")
    print(f"Current time (ET): {now.astimezone()}")

    for sport_key, sport_name in sports.items():
        print(f"\n{'=' * 50}")
        print(f"🏈 {sport_name} GAMES")
        print(f"{'=' * 50}")

        try:
            result = ingestor.ingest_live_odds(sport_key, force_refresh=True)
            if isinstance(result, dict) and "games" in result:
                games = result["games"]
                print(f"Total {sport_name} games: {len(games)}")

                for i, game in enumerate(games[:5]):  # Show first 5 games
                    if isinstance(game, dict):
                        home = game.get("home_team", "Unknown")
                        away = game.get("away_team", "Unknown")
                        commence_time = game.get("commence_time", "No time")

                        try:
                            if commence_time != "No time":
                                game_time = datetime.fromisoformat(
                                    commence_time.replace("Z", "+00:00")
                                )
                                local_time = game_time.astimezone()
                                hours_from_now = (game_time - now).total_seconds() / 3600

                                print(f"  {i + 1}. {away} @ {home}")
                                print(f"      UTC: {game_time}")
                                print(f"      Local: {local_time}")
                                print(f"      Hours from now: {hours_from_now:.1f}")

                                # Check if it has bookmakers
                                bookmakers = game.get("bookmakers", [])
                                print(f"      Bookmakers: {len(bookmakers)}")

                                if bookmakers and len(bookmakers) > 0:
                                    first_book = bookmakers[0]
                                    if isinstance(first_book, dict):
                                        book_name = first_book.get("key", "unknown")
                                        markets = first_book.get("markets", [])
                                        print(
                                            f"      Sample book: {book_name} with {len(markets)} markets"
                                        )

                                        for market in markets[:2]:  # First 2 markets
                                            if isinstance(market, dict):
                                                market_key = market.get("key", "")
                                                outcomes = market.get("outcomes", [])
                                                print(
                                                    f"        Market: {market_key} ({len(outcomes)} outcomes)"
                                                )
                        except Exception as e:
                            print(f"  {i + 1}. {away} @ {home} - Error parsing time: {e}")

            else:
                print(f"No games data for {sport_name}")

        except Exception as e:
            print(f"Error fetching {sport_name}: {e}")


if __name__ == "__main__":
    debug_games()
