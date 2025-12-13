#!/usr/bin/env python3
"""
Simple CFB Parlay Recommendations
=================================
Direct analysis of available games and manual parlay suggestions.
"""

from eq12_cfb_optimizer import CFBMysteryBoostOptimizer
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


def show_game_details(game_data, optimizer):
    """Show detailed game information"""
    print(f"\nGame: {game_data['away_team']} @ {game_data['home_team']}")
    print(f"Time: {game_data['commence_time']}")

    # Check bookmakers
    bookmakers = game_data.get("bookmakers", [])
    dk_found = False

    for book in bookmakers:
        if any(keyword in book.get("title", "")
               for keyword in ["DraftKings", "Draft Kings"]):
            dk_found = True
            markets = book.get("markets", [])
            for market in markets:
                if market.get("key") == "h2h":  # moneyline
                    outcomes = market.get("outcomes", [])
                    for outcome in outcomes:
                        team = outcome.get("name", "")
                        price = outcome.get("price", 0)
                        if team == game_data["home_team"]:
                            print(f"  DK Home ({team}): {price:+d}")
                        elif team == game_data["away_team"]:
                            print(f"  DK Away ({team}): {price:+d}")

    if not dk_found:
        print("  No DraftKings odds found")
        # Show other books
        for book in bookmakers[:2]:  # Show first 2 other books
            print(f"  {book.get('title', 'Unknown Book')}: Available")

    return dk_found


def main():
    print("🏈 EQ12 NCAA FOOTBALL PARLAY FINDER")
    print("=" * 50)

    # Initialize optimizer
    optimizer = CFBMysteryBoostOptimizer(token_percent=33, max_bet=100.0)

    # Fetch games
    print("\n📡 Fetching live NCAA Football games...")
    try:
        games_data = optimizer.fetch_ncaaf_moneylines()
        print(f"✅ Found {len(games_data)} total games")
    except Exception as e:
        print(f"❌ Error fetching games: {e}")
        return

    # Analyze games
    good_games = []
    fbs_games = []

    print("\n🔍 Analyzing games for FBS status and DraftKings availability...")

    for i, game in enumerate(games_data):
        try:
            home_team = game["home_team"]
            away_team = game["away_team"]

            # Check if both teams are FBS
            home_fbs = optimizer._is_fbs_team(home_team)
            away_fbs = optimizer._is_fbs_team(away_team)

            if home_fbs and away_fbs:
                fbs_games.append(game)

                # Check for DraftKings odds
                bookmakers = game.get("bookmakers", [])
                has_dk = any(
                    "DraftKings" in book.get(
                        "title", "") or "Draft Kings" in book.get(
                        "title", "") for book in bookmakers)

                if has_dk:
                    good_games.append(game)

        except Exception as e:
            print(f"Warning: Error analyzing game {i + 1}: {e}")

    print("\n📊 RESULTS:")
    print(f"   • Total games: {len(games_data)}")
    print(f"   • FBS vs FBS: {len(fbs_games)}")
    print(f"   • With DraftKings odds: {len(good_games)}")

    if len(good_games) >= 3:
        print("\n🎯 GAMES AVAILABLE FOR PARLAYS:")
        print("=" * 40)

        # Show up to 10 games with DK odds
        for i, game in enumerate(good_games[:10]):
            print(f"\n{i + 1}. {game['away_team']} @ {game['home_team']}")
            print(f"   Time: {game['commence_time'][:16]}")

            # Show DraftKings odds if available
            dk_odds, _ = optimizer._extract_dk_and_allbooks_prices(game)
            if dk_odds:
                home_odds = dk_odds.get("home_odds")
                away_odds = dk_odds.get("away_odds")
                if home_odds and away_odds:
                    print(
                        f"   DK: {game['away_team']} ({away_odds:+d}) | {game['home_team']} ({home_odds:+d})"
                    )

        print("\n🏆 MANUAL PARLAY RECOMMENDATIONS:")
        print("=" * 40)
        print("Based on the available games, here are some strategic approaches:")
        print()
        print("1. 🎲 UNDERDOG STRATEGY (Higher Risk/Reward)")
        print("   • Look for teams with odds around +150 to +300")
        print("   • Combine 3 underdogs for natural +300+ parlay")
        print("   • Best for 33% Mystery Boost token")
        print()
        print("2. 🏛️ FAVORITE HEAVY STRATEGY (Lower Risk)")
        print("   • Pick 3-4 heavy favorites (-200 or better)")
        print("   • Safer but requires more legs for +300 minimum")
        print("   • Good for 50% boost if available")
        print()
        print("3. 🎯 MIXED STRATEGY (Balanced)")
        print("   • 1 heavy favorite + 2 mild underdogs")
        print("   • Target total odds around +400-600")
        print("   • Maximizes EV with boost")
        print()

        if len(good_games) >= 3:
            # Pick 3 games for sample parlay
            sample_games = good_games[:3]
            print("🎪 SAMPLE 3-LEG PARLAY:")
            print("-" * 25)
            total_american_odds = 1.0

            for i, game in enumerate(sample_games):
                dk_odds, _ = optimizer._extract_dk_and_allbooks_prices(game)
                if dk_odds:
                    away_odds = dk_odds.get("away_odds") or 100
                    home_odds = dk_odds.get("home_odds") or -110

                    # Pick the better value (underdog if reasonable)
                    if away_odds > 0 and away_odds <= 300:  # Reasonable underdog
                        pick_team = game["away_team"]
                        pick_odds = away_odds
                    else:
                        pick_team = game["home_team"]
                        pick_odds = home_odds

                    print(f"{i + 1}. {pick_team} ({pick_odds:+d})")

                    # Convert to decimal for calculation
                    decimal = pick_odds / 100 + \
                        1 if pick_odds > 0 else 100 / abs(pick_odds) + 1
                    total_american_odds *= decimal

            # Calculate parlay odds
            if total_american_odds >= 2:
                parlay_american = (total_american_odds - 1) * 100
            else:
                parlay_american = -100 / (total_american_odds - 1)

            # Apply 33% boost
            boosted_decimal = total_american_odds * 1.33
            if boosted_decimal >= 2:
                boosted_american = (boosted_decimal - 1) * 100
            else:
                boosted_american = -100 / (boosted_decimal - 1)

            print(f"\nParlay Odds: {parlay_american:+.0f}")
            print(f"With 33% Boost: {boosted_american:+.0f}")

            if parlay_american >= 300:
                print("✅ Meets DK +300 minimum requirement!")

                # Calculate potential payout
                payout_normal = 100 * total_american_odds
                payout_boosted = 100 * boosted_decimal
                profit_boost = payout_boosted - payout_normal

                print("\n💰 $100 Bet Results:")
                print(f"   Normal Payout: ${payout_normal:.2f}")
                print(f"   Boosted Payout: ${payout_boosted:.2f}")
                print(f"   Mystery Boost Profit: ${profit_boost:.2f}")
            else:
                print("❌ Does not meet +300 minimum requirement")
                print("   Try adding another leg or picking bigger underdogs")

    else:
        print("\n❌ INSUFFICIENT DATA")
        print(f"Only found {len(good_games)} games with DraftKings odds.")
        print("Need at least 3 games for a valid parlay.")
        print("\nThis could be because:")
        print("• DraftKings doesn't offer all college games")
        print("• Games are too far in the future")
        print("• API is missing some data")
        print("\nTry checking DraftKings app directly for available CFB games.")


if __name__ == "__main__":
    main()
