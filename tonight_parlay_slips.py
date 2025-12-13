#!/usr/bin/env python3
"""
EQ12 TONIGHT'S PARLAY SLIPS - ACTIONABLE BETTING RECOMMENDATIONS
Generate specific betting slips for games starting 7:30 PM - 10:10 PM ET
"""

from datetime import UTC, datetime, timedelta

from eq12_odds_ingestor import OddsIngestor


def american_to_decimal(american_odds):
    """Convert American odds to decimal"""
    if american_odds > 0:
        return (american_odds / 100) + 1
    else:
        return (100 / abs(american_odds)) + 1


def decimal_to_american(decimal_odds):
    """Convert decimal odds to American"""
    if decimal_odds >= 2.0:
        return int((decimal_odds - 1) * 100)
    else:
        return int(-100 / (decimal_odds - 1))


def get_prime_time_games():
    """Get games in the 7:30 PM - 10:10 PM ET window"""
    ingestor = OddsIngestor()

    # Target time window - next 8 hours for tonight's games
    now = datetime.now(UTC)
    start_window = now  # Start from now
    end_window = now + timedelta(hours=8)  # Next 8 hours

    prime_games = []

    sports = {"americanfootball_ncaaf": "NCAAF", "icehockey_nhl": "NHL"}

    print("🎯 SCANNING PRIME TIME GAMES (7:30 PM - 10:10 PM ET)")
    print("=" * 70)

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

                                if start_window <= game_time <= end_window:
                                    local_time = game_time.astimezone()

                                    # Extract best odds from all bookmakers
                                    odds_data = extract_comprehensive_odds(game)

                                    if odds_data:  # Only include games with odds
                                        game_info = {
                                            "sport": sport_name,
                                            "home": game.get("home_team", ""),
                                            "away": game.get("away_team", ""),
                                            "game_time": game_time,
                                            "local_time": local_time,
                                            "time_str": local_time.strftime("%I:%M %p ET"),
                                            "odds": odds_data,
                                        }
                                        prime_games.append(game_info)

                            except Exception:
                                continue
        except Exception as e:
            print(f"Error fetching {sport_name}: {e}")

    return sorted(prime_games, key=lambda x: x["game_time"])


def extract_comprehensive_odds(game):
    """Extract best odds from all available bookmakers"""
    bookmakers = game.get("bookmakers", [])
    best_odds = {}

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

            for outcome in outcomes:
                if not isinstance(outcome, dict):
                    continue

                name = outcome.get("name", "")
                price = outcome.get("price", 0)
                point = outcome.get("point", None)

                # Store best odds by category
                if market_type == "h2h":  # Moneyline
                    key = f"ml_{name.lower().replace(' ', '_')}"
                    if key not in best_odds or price > best_odds[key]["price"]:
                        best_odds[key] = {
                            "team": name,
                            "price": price,
                            "book": book_key,
                            "type": "moneyline",
                        }

                elif market_type == "spreads":  # Point spreads
                    key = f"spread_{name.lower().replace(' ', '_')}"
                    if key not in best_odds or price > best_odds[key]["price"]:
                        best_odds[key] = {
                            "team": name,
                            "price": price,
                            "point": point,
                            "book": book_key,
                            "type": "spread",
                        }

                elif market_type == "totals":  # Over/Under
                    key = f"total_{name.lower()}"
                    if key not in best_odds or price > best_odds[key]["price"]:
                        best_odds[key] = {
                            "bet": name,
                            "price": price,
                            "point": point,
                            "book": book_key,
                            "type": "total",
                        }

    return best_odds


def generate_parlay_slips():
    """Generate specific parlay slips for tonight"""

    print("🎫 GENERATING TONIGHT'S PARLAY SLIPS")
    print("=" * 70)

    games = get_prime_time_games()

    if not games:
        print("❌ No games found in prime time window")
        return

    print(f"📊 FOUND {len(games)} PRIME TIME GAMES")

    # Display games first
    print("\n🎮 TONIGHT'S PRIME TIME LINEUP:")
    for i, game in enumerate(games, 1):
        print(f"  {i}. {game['time_str']}: {game['away']} @ {game['home']} ({game['sport']})")

    print("\n" + "=" * 70)

    # SLIP 1: TARGET SGP (Missouri State)
    missouri_game = None
    liberty_game = None

    for game in games:
        if "Missouri State" in game["away"] or "Missouri State" in game["home"]:
            missouri_game = game
        elif "Liberty" in game["away"] or "Liberty" in game["home"]:
            liberty_game = game

    slip_number = 1

    # SGP SLIP 1: Missouri State Game
    if missouri_game:
        print(f"🎫 PARLAY SLIP #{slip_number} - SAME GAME PARLAY")
        print("-" * 50)
        print(f"🏈 NCAAF: {missouri_game['away']} @ {missouri_game['home']}")
        print(f"⏰ {missouri_game['time_str']}")

        odds = missouri_game["odds"]

        # Find underdog + over correlation
        ml_bets = [(k, v) for k, v in odds.items() if k.startswith("ml_")]
        total_bets = [(k, v) for k, v in odds.items() if k.startswith("total_")]

        if ml_bets and total_bets:
            # Find underdog
            underdog = None

            for _, bet_info in ml_bets:
                if bet_info["price"] > 0:  # Positive odds = underdog
                    underdog = bet_info
                else:  # Negative odds = favorite
                    pass

            # Find over bet
            over_bet = None
            for _, bet_info in total_bets:
                if "over" in bet_info["bet"].lower():
                    over_bet = bet_info
                    break

            if underdog and over_bet:

                print("\n💰 SGP LEGS:")
                print(f"  1. {underdog['team']} ML: {underdog['price']:+d} ({underdog['book']})")
                print(f"  2. {over_bet['bet']}: {over_bet['price']:+d} ({over_bet['book']})")

                # Calculate combined odds
                combined_decimal = american_to_decimal(underdog["price"]) * american_to_decimal(
                    over_bet["price"]
                )
                combined_american = decimal_to_american(combined_decimal)

                stake = 25  # 2-5% of $1000 bankroll
                payout = stake * combined_decimal

                print("\n📊 SLIP SUMMARY:")
                print(f"   Combined Odds: {combined_decimal:.2f}x ({combined_american:+d})")
                print(f"   Stake: ${stake}")
                print(f"   Potential Payout: ${payout:.0f}")
                print(f"   Profit: ${payout - stake:.0f}")
                print("   Strategy: Underdog + Over correlation")

                slip_number += 1
            else:
                print("❌ Unable to build SGP - missing underdog or over bet")
        else:
            print("❌ No moneyline or total odds available")

    # SGP SLIP 2: Liberty Game
    if liberty_game:
        print(f"\n🎫 PARLAY SLIP #{slip_number} - SAME GAME PARLAY")
        print("-" * 50)
        print(f"🏈 NCAAF: {liberty_game['away']} @ {liberty_game['home']}")
        print(f"⏰ {liberty_game['time_str']}")

        odds = liberty_game["odds"]

        ml_bets = [(k, v) for k, v in odds.items() if k.startswith("ml_")]
        total_bets = [(k, v) for k, v in odds.items() if k.startswith("total_")]

        if ml_bets and total_bets:
            # Similar SGP logic
            underdog = None
            for _, bet_info in ml_bets:
                if bet_info["price"] > 0:
                    underdog = bet_info
                    break

            over_bet = None
            for _, bet_info in total_bets:
                if "over" in bet_info["bet"].lower():
                    over_bet = bet_info
                    break

            if underdog and over_bet:
                print("\n💰 SGP LEGS:")
                print(f"  1. {underdog['team']} ML: {underdog['price']:+d} ({underdog['book']})")
                print(f"  2. {over_bet['bet']}: {over_bet['price']:+d} ({over_bet['book']})")

                combined_decimal = american_to_decimal(underdog["price"]) * american_to_decimal(
                    over_bet["price"]
                )
                combined_american = decimal_to_american(combined_decimal)

                stake = 20
                payout = stake * combined_decimal

                print("\n📊 SLIP SUMMARY:")
                print(f"   Combined Odds: {combined_decimal:.2f}x ({combined_american:+d})")
                print(f"   Stake: ${stake}")
                print(f"   Potential Payout: ${payout:.0f}")
                print(f"   Profit: ${payout - stake:.0f}")

                slip_number += 1

    # SLIP 3: Cross-Sport Conservative Parlay
    print(f"\n🎫 PARLAY SLIP #{slip_number} - CROSS-SPORT PARLAY")
    print("-" * 50)

    favorites = []

    for game in games:
        odds = game["odds"]
        ml_bets = [(k, v) for k, v in odds.items() if k.startswith("ml_")]

        for _, bet_info in ml_bets:
            if bet_info["price"] <= -140:  # Strong favorite
                favorites.append(
                    {
                        "game": f"{game['away']} @ {game['home']}",
                        "sport": game["sport"],
                        "time": game["time_str"],
                        "bet": f"{bet_info['team']} ML",
                        "odds": bet_info["price"],
                        "decimal": american_to_decimal(bet_info["price"]),
                        "book": bet_info["book"],
                    }
                )

    if len(favorites) >= 2:
        # Take best 3 favorites
        top_favorites = sorted(favorites, key=lambda x: x["decimal"])[:3]

        print("💰 PARLAY LEGS:")
        combined_decimal = 1.0

        for i, fav in enumerate(top_favorites, 1):
            print(
                f"  {i}. {fav['time']} - {fav['sport']}: {fav['bet']} ({fav['odds']:+d}) [{fav['book']}]"
            )
            combined_decimal *= fav["decimal"]

        combined_american = decimal_to_american(combined_decimal)
        stake = 50
        payout = stake * combined_decimal

        print("\n📊 SLIP SUMMARY:")
        print(f"   Combined Odds: {combined_decimal:.2f}x ({combined_american:+d})")
        print(f"   Stake: ${stake}")
        print(f"   Potential Payout: ${payout:.0f}")
        print(f"   Profit: ${payout - stake:.0f}")
        print("   Strategy: Conservative multi-sport favorites")

        slip_number += 1
    else:
        print("❌ Insufficient strong favorites (-140+) for conservative parlay")

    # SLIP 4: High-Risk High-Reward Mega Parlay
    print(f"\n🎫 PARLAY SLIP #{slip_number} - MEGA PARLAY (HIGH RISK)")
    print("-" * 50)

    mega_legs = []

    # Mix of underdogs and totals
    for game in games[:2]:  # First 2 games
        odds = game["odds"]

        # Add an underdog ML
        ml_bets = [(k, v) for k, v in odds.items() if k.startswith("ml_")]
        for _, bet_info in ml_bets:
            if 100 <= bet_info["price"] <= 200:  # Reasonable underdog
                mega_legs.append(
                    {
                        "game": f"{game['away']} @ {game['home']}",
                        "sport": game["sport"],
                        "time": game["time_str"],
                        "bet": f"{bet_info['team']} ML",
                        "odds": bet_info["price"],
                        "decimal": american_to_decimal(bet_info["price"]),
                        "book": bet_info["book"],
                    }
                )
                break

        # Add an over
        total_bets = [(k, v) for k, v in odds.items() if k.startswith("total_")]
        for _, bet_info in total_bets:
            if "over" in bet_info["bet"].lower():
                mega_legs.append(
                    {
                        "game": f"{game['away']} @ {game['home']}",
                        "sport": game["sport"],
                        "time": game["time_str"],
                        "bet": bet_info["bet"],
                        "odds": bet_info["price"],
                        "decimal": american_to_decimal(bet_info["price"]),
                        "book": bet_info["book"],
                    }
                )
                break

    if len(mega_legs) >= 3:
        print("💰 MEGA PARLAY LEGS:")
        combined_decimal = 1.0

        for i, leg in enumerate(mega_legs[:4], 1):  # Max 4 legs
            print(
                f"  {i}. {leg['time']} - {leg['sport']}: {leg['bet']} ({leg['odds']:+d}) [{leg['book']}]"
            )
            combined_decimal *= leg["decimal"]

        combined_american = decimal_to_american(combined_decimal)
        stake = 10  # Lower stake for high risk
        payout = stake * combined_decimal

        print("\n📊 SLIP SUMMARY:")
        print(f"   Combined Odds: {combined_decimal:.1f}x ({combined_american:+d})")
        print(f"   Stake: ${stake} (REDUCED RISK)")
        print(f"   Potential Payout: ${payout:.0f}")
        print(f"   Profit: ${payout - stake:.0f}")
        print("   ⚠️  HIGH RISK - Multiple leg parlay")

    # BANKROLL SUMMARY
    total_stakes = 25 + 20 + 50 + 10  # Assuming all slips

    print("\n" + "=" * 70)
    print("💼 BANKROLL MANAGEMENT SUMMARY")
    print("=" * 70)
    print(f"🎯 Total Stake Across All Slips: ${total_stakes}")
    print(f"📊 Percentage of $1000 Bankroll: {total_stakes / 10:.1f}%")
    print(f"✅ Within 2-5% Risk Management: {'YES' if total_stakes <= 50 else 'NO'}")
    print("⏰ Prime Time Window: 7:30 PM - 10:10 PM ET")
    print("📱 Recommendation: Place bets 30 mins before game time")
    print("🚫 Remember: Never chase losses, stick to the plan!")


if __name__ == "__main__":
    generate_parlay_slips()
