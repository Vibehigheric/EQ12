#!/usr/bin/env python3
"""
EQ12 CFB Parlay Analyzer - Quick Demo
==============                # Pick the underdog (higher odds) for better parlay potential
                for game in combo:
                    dk_away = game['dk_away']
                    dk_home = game['dk_home']

                    # Skip games with missing odds
                    if dk_away is None or dk_home is None:
                        continue

                    # Pick the underdog (higher odds) for better parlay potential
                    if abs(dk_away) > abs(dk_home):
                        legs.append({
                            'team': game['away'],
                            'opponent': game['home'],
                            'odds': dk_away,
                            'game_id': game['id']
                        })
                    else:
                        legs.append({
                            'team': game['home'],
                            'opponent': game['away'],
                            'odds': dk_home,
                            'game_id': game['id']
                        })=====
Shows all available FBS games with DraftKings odds and builds best parlays.
"""

from eq12_cfb_optimizer import CFBMysteryBoostOptimizer
from itertools import combinations
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


def main():
    print("=== EQ12 NCAA CFB PARLAY ANALYZER ===")
    print()

    # Initialize optimizer
    optimizer = CFBMysteryBoostOptimizer(token_percent=33, max_bet=100.0)

    # Fetch games
    print("Fetching current NCAAF games...")
    games_data = optimizer.fetch_ncaaf_moneylines()
    print("Found {len(games_data)} total games")
    print()

    # Filter FBS games (all dates, not just Friday)
    fbs_games = []
    for game in games_data:
        try:
            home_fbs = optimizer._is_fbs_team(game["home_team"])
            away_fbs = optimizer._is_fbs_team(game["away_team"])

            if home_fbs and away_fbs:
                # Extract DraftKings odds directly
                dk_odds, _all_odds = optimizer._extract_dk_and_allbooks_prices(game)
                if dk_odds:
                    fbs_games.append(
                        {
                            "id": game["id"],
                            "home": game["home_team"],
                            "away": game["away_team"],
                            "time": game["commence_time"],
                            "dk_home": dk_odds.get("home_odds"),
                            "dk_away": dk_odds.get("away_odds"),
                            "game_data": game,  # Store full game data
                        }
                    )
        except Exception:
            game.get("id", "unknown")
            print("Warning: Error processing game {game_id}: {e}")

    print("Found {len(fbs_games)} FBS games with DraftKings odds:")
    print()

    # Show available games
    for _i, game in enumerate(fbs_games[:15]):  # Show first 15
        print('{i+1:2d}. {game["away"]} @ {game["home"]}')

        away_odds = game["dk_away"] if game["dk_away"] is not None else "N/A"
        home_odds = game["dk_home"] if game["dk_home"] is not None else "N/A"

        if isinstance(away_odds, int) and isinstance(home_odds, int):
            print("     DK Odds: Away {away_odds:+d} | Home {home_odds:+d}")
        else:
            print("     DK Odds: Away {away_odds} | Home {home_odds}")

        print('     Time: {game["time"][:16]}')
        print()

    if len(fbs_games) >= 3:
        print("✅ {len(fbs_games)} games available for 3-leg parlays!")
        print()
        print("Building optimal parlay recommendations...")
        print()

        # Build best parlays manually (since the optimizer is date-restricted)
        best_parlays = []

        # Check all 3-leg combinations
        for combo in combinations(
                fbs_games[:12], 3):  # Limit to first 12 games for speed
            try:
                # Build parlay legs
                legs = []
                for game in combo:
                    # Pick the underdog (higher odds) for better parlay potential
                    if abs(game["dk_away"]) > abs(game["dk_home"]):
                        legs.append(
                            {
                                "team": game["away"],
                                "opponent": game["home"],
                                "odds": game["dk_away"],
                                "game_id": game["id"],
                            }
                        )
                    else:
                        legs.append(
                            {
                                "team": game["home"],
                                "opponent": game["away"],
                                "odds": game["dk_home"],
                                "game_id": game["id"],
                            }
                        )

                # Only process if we have 3 complete legs
                if len(legs) != 3:
                    continue

                # Calculate parlay odds
                total_decimal = 1.0
                for leg in legs:
                    if leg["odds"] > 0:
                        decimal_odds = (leg["odds"] / 100) + 1
                    else:
                        decimal_odds = (100 / abs(leg["odds"])) + 1
                    total_decimal *= decimal_odds

                american_odds = ((total_decimal - 1) * 100 if total_decimal >=
                                 2 else -100 / (total_decimal - 1))

                # Check if meets +300 minimum
                if american_odds >= 300:
                    # Calculate boosted value (33% boost)
                    boosted_decimal = total_decimal * 1.33
                    boosted_american = (
                        (boosted_decimal - 1) * 100
                        if boosted_decimal >= 2
                        else -100 / (boosted_decimal - 1)
                    )

                    # Estimate EV (simplified - assumes 50% win rate per leg)
                    win_prob = 0.5**3  # 12.5% for 3 legs
                    ev = (win_prob * boosted_decimal * 100) - 100

                    best_parlays.append(
                        {
                            "legs": legs,
                            "odds": american_odds,
                            "boosted_odds": boosted_american,
                            "ev": ev,
                            "decimal": total_decimal,
                        }
                    )

            except Exception:
                print("Error building parlay: {e}")

        # Sort by EV and show top 3
        best_parlays.sort(key=lambda x: x["ev"], reverse=True)

        if best_parlays:
            print("🎯 TOP 3 RECOMMENDED PARLAYS (33% Mystery Boost):")
            print()

            for _i, parlay in enumerate(best_parlays[:3]):
                print('#{i+1} - Expected Value: ${parlay["ev"]:.2f}')
                print('   Original Odds: {parlay["odds"]:+.0f}')
                print('   Boosted Odds: {parlay["boosted_odds"]:+.0f}')
                print("   Legs:")
                for _j, leg in enumerate(parlay["legs"]):
                    print('      {j+1}. {leg["team"]} ({leg["odds"]:+d})')
                print()
        else:
            print("❌ No parlays found meeting +300 minimum odds requirement")

    else:
        print("⚠️  Only {len(fbs_games)} games available - need at least 3 for parlays")


if __name__ == "__main__":
    main()
