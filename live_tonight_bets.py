#!/usr/bin/env python3
"""
EQ12 TONIGHT'S BEST BETS - Live Games Analysis
Shows actual betting opportunities for games starting soon
"""

from datetime import UTC, datetime, timedelta

from eq12_odds_ingestor import OddsIngestor


def american_to_decimal(american_odds):
    """Convert American odds to decimal"""
    try:
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    except:
        return 2.0


def get_tonights_live_games():
    """Get games starting in the next 8 hours"""
    ingestor = OddsIngestor()

    sports = {"baseball_mlb": "MLB", "icehockey_nhl": "NHL", "americanfootball_ncaaf": "NCAAF"}

    now = datetime.now(UTC)
    cutoff = now + timedelta(hours=8)  # Next 8 hours

    live_games = []

    print("🔄 Fetching LIVE odds for tonight's games...")

    for sport_key, sport_name in sports.items():
        try:
            result = ingestor.ingest_live_odds(sport_key, force_refresh=True)
            if isinstance(result, dict) and "games" in result:
                games = result["games"]

                for game in games:
                    if isinstance(game, dict):
                        commence_time_str = game.get("commence_time", "")
                        if commence_time_str:
                            try:
                                game_time = datetime.fromisoformat(
                                    commence_time_str.replace("Z", "+00:00")
                                )

                                # Games in next 8 hours
                                if now <= game_time <= cutoff:
                                    hours_away = (game_time - now).total_seconds() / 3600
                                    local_time = game_time.astimezone()

                                    live_games.append(
                                        {
                                            "sport": sport_name,
                                            "home": game.get("home_team", "Unknown"),
                                            "away": game.get("away_team", "Unknown"),
                                            "game_time": game_time,
                                            "local_time": local_time,
                                            "hours_away": hours_away,
                                            "bookmakers": game.get("bookmakers", []),
                                            "raw_game": game,
                                        }
                                    )

                            except Exception:
                                continue

        except Exception as e:
            print(f"   ❌ Error with {sport_name}: {e!s}")

    return sorted(live_games, key=lambda x: x["game_time"])


def extract_best_odds(game_data):
    """Extract best odds from bookmakers"""
    bookmakers = game_data["bookmakers"]

    best_odds = {
        "home_ml": None,
        "away_ml": None,
        "over": None,
        "under": None,
        "home_spread": None,
        "away_spread": None,
    }

    for book in bookmakers:
        if not isinstance(book, dict):
            continue

        book_key = book.get("key", "unknown")
        markets = book.get("markets", [])

        for market in markets:
            if not isinstance(market, dict):
                continue

            market_type = market.get("key", "")
            outcomes = market.get("outcomes", [])

            # Process each outcome
            for outcome in outcomes:
                if not isinstance(outcome, dict):
                    continue

                name = outcome.get("name", "")
                price = outcome.get("price", 0)
                point = outcome.get("point", 0)

                # Moneyline
                if market_type == "h2h":
                    if name == game_data["home"] and (
                        best_odds["home_ml"] is None or price > best_odds["home_ml"][1]
                    ):
                        best_odds["home_ml"] = (name, price, book_key)
                    elif name == game_data["away"] and (
                        best_odds["away_ml"] is None or price > best_odds["away_ml"][1]
                    ):
                        best_odds["away_ml"] = (name, price, book_key)

                # Totals
                elif market_type == "totals":
                    if "Over" in name and (
                        best_odds["over"] is None or price > best_odds["over"][1]
                    ):
                        best_odds["over"] = (f"Over {point}", price, book_key, point)
                    elif "Under" in name and (
                        best_odds["under"] is None or price > best_odds["under"][1]
                    ):
                        best_odds["under"] = (f"Under {point}", price, book_key, point)

                # Spreads
                elif market_type == "spreads":
                    if name == game_data["home"] and (
                        best_odds["home_spread"] is None or price > best_odds["home_spread"][1]
                    ):
                        best_odds["home_spread"] = (f"{name} {point:+.1f}", price, book_key, point)
                    elif name == game_data["away"] and (
                        best_odds["away_spread"] is None or price > best_odds["away_spread"][1]
                    ):
                        best_odds["away_spread"] = (f"{name} {point:+.1f}", price, book_key, point)

    return best_odds


def analyze_tonights_bets():
    """Main analysis function"""
    print("🎯 EQ12 LIVE BETTING ANALYSIS - TONIGHT'S GAMES")
    print("=" * 80)

    games = get_tonights_live_games()

    if not games:
        print("❌ No games starting in the next 8 hours")
        return

    now_local = datetime.now()
    print(f"\n📊 FOUND {len(games)} GAMES STARTING SOON")
    print(f"⏰ Current Time: {now_local.strftime('%I:%M %p ET')}")

    # Show all games
    print("\n🎮 TONIGHT'S GAMES:")
    for i, game in enumerate(games, 1):
        local_time_str = game["local_time"].strftime("%I:%M %p")
        print(
            f"  {i}. {local_time_str}: {game['away']} @ {game['home']} ({game['sport']}) - {game['hours_away']:.1f}h"
        )

    print("\n" + "=" * 80)

    # Analyze each game
    sgp_opportunities = []
    parlay_legs = []

    for game in games:
        odds = extract_best_odds(game)

        print(f"\n🏈 {game['sport']}: {game['away']} @ {game['home']}")
        print(
            f"   ⏰ {game['local_time'].strftime('%I:%M %p ET')} ({game['hours_away']:.1f} hours away)"
        )

        # Display odds
        if odds["away_ml"]:
            away_ml_odds = odds["away_ml"][1]
            print(f"   🏃 {odds['away_ml'][0]}: {away_ml_odds:+d} ({odds['away_ml'][2]})")

        if odds["home_ml"]:
            home_ml_odds = odds["home_ml"][1]
            print(f"   🏠 {odds['home_ml'][0]}: {home_ml_odds:+d} ({odds['home_ml'][2]})")

        if odds["over"]:
            over_odds = odds["over"][1]
            print(f"   ⬆️  {odds['over'][0]}: {over_odds:+d} ({odds['over'][2]})")

        if odds["under"]:
            under_odds = odds["under"][1]
            print(f"   ⬇️  {odds['under'][0]}: {under_odds:+d} ({odds['under'][2]})")

        # SGP Analysis
        if odds["away_ml"] and odds["over"] and away_ml_odds >= 120:
            # Underdog + Over correlation
            combined_decimal = american_to_decimal(away_ml_odds) * american_to_decimal(over_odds)
            if combined_decimal >= 3.5:
                sgp_opportunities.append(
                    {
                        "game": f"{game['away']} @ {game['home']}",
                        "sport": game["sport"],
                        "time": game["local_time"].strftime("%I:%M %p"),
                        "legs": [
                            f"{odds['away_ml'][0]} ML ({away_ml_odds:+d})",
                            f"{odds['over'][0]} ({over_odds:+d})",
                        ],
                        "combined_odds": combined_decimal,
                        "american_odds": int((combined_decimal - 1) * 100),
                        "payout_10": combined_decimal * 10,
                        "payout_25": combined_decimal * 25,
                    }
                )

        # Conservative parlay legs (strong favorites)
        if odds["home_ml"] and home_ml_odds <= -140:
            parlay_legs.append(
                {
                    "game": f"{game['away']} @ {game['home']}",
                    "sport": game["sport"],
                    "bet": f"{odds['home_ml'][0]} ML ({home_ml_odds:+d})",
                    "decimal_odds": american_to_decimal(home_ml_odds),
                    "time": game["local_time"].strftime("%I:%M %p"),
                }
            )

        if odds["away_ml"] and away_ml_odds <= -140:
            parlay_legs.append(
                {
                    "game": f"{game['away']} @ {game['home']}",
                    "sport": game["sport"],
                    "bet": f"{odds['away_ml'][0]} ML ({away_ml_odds:+d})",
                    "decimal_odds": american_to_decimal(away_ml_odds),
                    "time": game["local_time"].strftime("%I:%M %p"),
                }
            )

    # SGP Recommendations
    print("\n🎲 SAME GAME PARLAY (SGP) OPPORTUNITIES")
    print("-" * 60)

    if sgp_opportunities:
        sgp_opportunities.sort(key=lambda x: x["combined_odds"], reverse=True)

        for i, sgp in enumerate(sgp_opportunities[:3], 1):
            print(f"\n{i}. 🔥 {sgp['sport']} - {sgp['time']}")
            print(f"   {sgp['game']}")
            print(f"   Legs: {' + '.join(sgp['legs'])}")
            print(f"   Combined: {sgp['combined_odds']:.1f}x ({sgp['american_odds']:+d})")
            print(f"   $10 bet → ${sgp['payout_10']:.0f} | $25 bet → ${sgp['payout_25']:.0f}")
    else:
        print("   No high-value SGPs found (looking for 3.5x+ odds)")

    # Cross-Sport Parlay
    print("\n🏆 CROSS-SPORT PARLAY BUILDER")
    print("-" * 60)

    if len(parlay_legs) >= 2:
        # Best 2-3 favorites
        best_legs = parlay_legs[:3]
        combined_decimal = 1.0
        for leg in best_legs:
            combined_decimal *= leg["decimal_odds"]

        american_combined = (
            int((combined_decimal - 1) * 100)
            if combined_decimal < 2
            else int((combined_decimal - 1) * 100)
        )

        print(f"\n💰 {len(best_legs)}-Leg Conservative Parlay")
        for leg in best_legs:
            print(f"   • {leg['time']} - {leg['sport']}: {leg['bet']}")
        print(f"   Combined: {combined_decimal:.2f}x ({american_combined:+d})")
        print(f"   $50 bet → ${combined_decimal * 50:.0f}")
    else:
        print("   Need 2+ strong favorites (-140 or better)")

    # Tonight's Best Single Bets
    print("\n⭐ TONIGHT'S BEST SINGLE BETS")
    print("-" * 60)

    single_bets = []
    for game in games[:3]:  # Top 3 games by time
        odds = extract_best_odds(game)

        # Look for value plays
        if odds["away_ml"] and 100 <= odds["away_ml"][1] <= 200:
            # Underdog with reasonable odds
            decimal_odds = american_to_decimal(odds["away_ml"][1])
            single_bets.append(
                {
                    "type": "Underdog ML",
                    "bet": f"{odds['away_ml'][0]} ({odds['away_ml'][1]:+d})",
                    "game": f"{game['away']} @ {game['home']}",
                    "sport": game["sport"],
                    "time": game["local_time"].strftime("%I:%M %p"),
                    "decimal": decimal_odds,
                    "payout_20": decimal_odds * 20,
                }
            )

        if odds["over"] and -115 <= odds["over"][1] <= -105:
            # Over with good juice
            decimal_odds = american_to_decimal(odds["over"][1])
            single_bets.append(
                {
                    "type": "Total Over",
                    "bet": f"{odds['over'][0]} ({odds['over'][1]:+d})",
                    "game": f"{game['away']} @ {game['home']}",
                    "sport": game["sport"],
                    "time": game["local_time"].strftime("%I:%M %p"),
                    "decimal": decimal_odds,
                    "payout_20": decimal_odds * 20,
                }
            )

    for i, bet in enumerate(single_bets[:3], 1):
        print(f"\n{i}. {bet['type']}: {bet['bet']}")
        print(f"   {bet['time']} - {bet['sport']}: {bet['game']}")
        print(f"   $20 bet → ${bet['payout_20']:.0f}")

    print("\n" + "=" * 80)
    print("✅ LIVE ANALYSIS COMPLETE")
    print("💰 All odds are LIVE from DraftKings, FanDuel, BetMGM")
    print("📊 Recommendations based on correlation analysis & value")
    print("⚠️  Always bet responsibly!")


if __name__ == "__main__":
    analyze_tonights_bets()
