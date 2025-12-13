#!/usr/bin/env python3
"""
EQ12 MLB Enhanced Value Analysis - Aggressive Mode
Shows all betting opportunities including marginal edges for educational purposes

This version uses lower thresholds to identify marginal betting opportunities
and provides detailed market analysis for informed decision making.
"""

import json
from datetime import datetime
from pathlib import Path


def analyze_detailed_opportunities():
    """Analyze games with detailed breakdown of all betting opportunities"""

    # Find most recent games file
    logs_dir = Path("C:/EQ12/logs")
    games_files = list(logs_dir.glob("mlb_games_today_*.json"))
    if not games_files:
        print("❌ No games file found")
        return

    games_file = max(games_files, key=lambda x: x.stat().st_mtime)

    with open(games_file, encoding="utf-8") as f:
        data = json.load(f)

    games = data.get("games", [])

    print("🎯 ENHANCED MLB VALUE ANALYSIS - AGGRESSIVE MODE")
    print("=" * 80)
    print(f"📅 Date: {data.get('date', 'Unknown')}")
    print(f"📊 Games: {len(games)}")
    print("⚠️ Showing ALL opportunities including marginal edges")
    print()

    for i, game in enumerate(games, 1):
        matchup = f"{game.get('away_team')} @ {game.get('home_team')}"
        odds = game.get("odds", {})

        print(f"🎯 GAME {i}: {matchup}")
        print("=" * 60)

        # Game details
        start_time = game.get("start_time", "")
        if start_time:
            dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            print(f"⏰ Start: {dt.strftime('%I:%M %p %Z')}")

        venue = game.get("venue", "Unknown")
        print(f"🏟️ Venue: {venue}")

        # Weather analysis
        weather = game.get("weather", {})
        if weather:
            temp = weather.get("temperature", "Unknown")
            conditions = weather.get("conditions", "Unknown")
            wind_speed = weather.get("wind_speed", 0)
            wind_dir = weather.get("wind_direction", "")

            print(f"🌤️ Weather: {temp}°F, {conditions}")
            if wind_speed and wind_dir:
                print(f"   💨 Wind: {wind_speed} mph {wind_dir}")

        # Pitcher analysis
        home_pitcher = game.get("home_pitcher", {})
        away_pitcher = game.get("away_pitcher", {})

        if home_pitcher and away_pitcher:
            print("⚾ PITCHING MATCHUP:")
            home_era = home_pitcher.get("era", "N/A")
            away_era = away_pitcher.get("era", "N/A")
            home_hand = home_pitcher.get("hand", "N/A")
            away_hand = away_pitcher.get("hand", "N/A")

            print(
                f"   {game.get('away_team')}: {away_pitcher.get('name', 'Unknown')} ({away_hand}HP, {away_era} ERA)"
            )
            print(
                f"   {game.get('home_team')}: {home_pitcher.get('name', 'Unknown')} ({home_hand}HP, {home_era} ERA)"
            )

            if isinstance(home_era, (int, float)) and isinstance(away_era, (int, float)):
                era_diff = abs(home_era - away_era)
                if era_diff > 0.5:
                    better_pitcher = "Home" if home_era < away_era else "Away"
                    print(
                        f"   🎯 Pitching Advantage: {better_pitcher} ({era_diff:.2f} ERA difference)"
                    )

        # Odds analysis
        if odds:
            print("\n💰 BETTING ANALYSIS:")

            # Moneyline analysis
            home_ml = odds.get("moneyline_home")
            away_ml = odds.get("moneyline_away")

            if home_ml and away_ml:
                # Calculate implied probabilities
                def american_to_prob(odds):
                    if odds > 0:
                        return 100 / (odds + 100)
                    return abs(odds) / (abs(odds) + 100)

                home_prob = american_to_prob(home_ml)
                away_prob = american_to_prob(away_ml)
                total_prob = home_prob + away_prob
                vig = total_prob - 1.0

                # True market probabilities (vig removed)
                home_true = home_prob / total_prob
                away_true = away_prob / total_prob

                home_odds_str = f"+{home_ml}" if home_ml > 0 else str(home_ml)
                away_odds_str = f"+{away_ml}" if away_ml > 0 else str(away_ml)

                print("   🎲 Moneyline:")
                print(
                    f"      {game.get('away_team')}: {away_odds_str} (Implied: {away_prob:.1%}, True: {away_true:.1%})"
                )
                print(
                    f"      {game.get('home_team')}: {home_odds_str} (Implied: {home_prob:.1%}, True: {home_true:.1%})"
                )
                print(f"      📊 Market Vig: {vig:.2%}")

                # Basic value assessment
                if vig < 0.04:
                    print("      ✅ Low vig market - good for line shopping")
                elif vig > 0.06:
                    print("      ⚠️ High vig market - avoid unless strong edge")

            # Spread analysis
            spread_home = odds.get("spread_home")
            spread_away = odds.get("spread_away")
            spread_price_home = odds.get("spread_price_home")
            spread_price_away = odds.get("spread_price_away")

            if all([spread_home, spread_away, spread_price_home, spread_price_away]):
                home_spread_prob = american_to_prob(spread_price_home)
                away_spread_prob = american_to_prob(spread_price_away)
                spread_vig = (home_spread_prob + away_spread_prob) - 1.0

                home_spread_str = f"{spread_home:+.1f}" if spread_home > 0 else f"{spread_home:.1f}"
                away_spread_str = f"{spread_away:+.1f}" if spread_away > 0 else f"{spread_away:.1f}"
                home_price_str = (
                    f"+{spread_price_home}" if spread_price_home > 0 else str(spread_price_home)
                )
                away_price_str = (
                    f"+{spread_price_away}" if spread_price_away > 0 else str(spread_price_away)
                )

                print("   🎯 Run Line:")
                print(f"      {game.get('away_team')} {away_spread_str}: {away_price_str}")
                print(f"      {game.get('home_team')} {home_spread_str}: {home_price_str}")
                print(f"      📊 Run Line Vig: {spread_vig:.2%}")

            # Total analysis
            total_runs = odds.get("total_runs")
            total_over_price = odds.get("total_over_price")
            total_under_price = odds.get("total_under_price")

            if all([total_runs, total_over_price, total_under_price]):
                over_prob = american_to_prob(total_over_price)
                under_prob = american_to_prob(total_under_price)
                total_vig = (over_prob + under_prob) - 1.0

                over_price_str = (
                    f"+{total_over_price}" if total_over_price > 0 else str(total_over_price)
                )
                under_price_str = (
                    f"+{total_under_price}" if total_under_price > 0 else str(total_under_price)
                )

                print(f"   🎯 Total Runs ({total_runs}):")
                print(f"      Over: {over_price_str} (Implied: {over_prob:.1%})")
                print(f"      Under: {under_price_str} (Implied: {under_prob:.1%})")
                print(f"      📊 Total Vig: {total_vig:.2%}")

                # Weather impact on totals
                if weather:
                    wind_speed = weather.get("wind_speed", 0)
                    wind_dir = weather.get("wind_direction", "").lower()
                    temp = weather.get("temperature", 72)

                    total_impacts = []

                    if wind_speed > 10:
                        if "out" in wind_dir:
                            total_impacts.append(f"Strong wind OUT ({wind_speed} mph) favors OVER")
                        elif "in" in wind_dir:
                            total_impacts.append(f"Strong wind IN ({wind_speed} mph) favors UNDER")

                    if temp > 80:
                        total_impacts.append(f"Hot weather ({temp}°F) favors OVER")
                    elif temp < 60:
                        total_impacts.append(f"Cold weather ({temp}°F) favors UNDER")

                    if total_impacts:
                        print(f"      🌤️ Weather Impact: {', '.join(total_impacts)}")

        # Market efficiency summary
        print("\n📋 MARKET SUMMARY:")
        if odds:
            avg_vig = (
                (vig + spread_vig + total_vig) / 3 if all([vig, spread_vig, total_vig]) else vig
            )

            if avg_vig < 0.035:
                efficiency = "VERY EFFICIENT"
                color = "🟢"
            elif avg_vig < 0.05:
                efficiency = "EFFICIENT"
                color = "🟡"
            elif avg_vig < 0.07:
                efficiency = "INEFFICIENT"
                color = "🟠"
            else:
                efficiency = "VERY INEFFICIENT"
                color = "🔴"

            print(f"   {color} Market Efficiency: {efficiency} (Avg Vig: {avg_vig:.2%})")

            # Betting recommendations
            print("   💡 Recommendations:")
            if avg_vig < 0.04:
                print("      • Excellent market for line shopping")
                print("      • Consider smaller edges (1-2%)")
            elif avg_vig < 0.06:
                print("      • Standard market - look for 3%+ edges")
            else:
                print("      • High vig - need 5%+ edges to overcome")

            print("      • Best value likely in market with lowest vig")

            # Sharp vs public indicators
            if home_ml and away_ml:
                if abs(home_ml) < abs(away_ml):
                    favorite = game.get("home_team")
                    dog = game.get("away_team")
                else:
                    favorite = game.get("away_team")
                    dog = game.get("home_team")

                print(f"      • Favorite: {favorite} | Underdog: {dog}")
                print("      • Consider contrarian approach if public heavily on favorite")

        print("\n" + "-" * 60 + "\n")

    print("🎯 PORTFOLIO RECOMMENDATIONS:")
    print("=" * 50)
    print("• Focus on games with lowest vig (under 4%)")
    print("• Look for pitcher/weather advantages not reflected in odds")
    print("• Consider small unit sizes (0.5-1% of bankroll) on marginal edges")
    print("• Shop lines across multiple sportsbooks")
    print("• Weather can create value in totals markets")
    print("• Late money movement may indicate sharp action")
    print()
    print("⚠️ Remember: Even marginal edges require proper bankroll management!")


if __name__ == "__main__":
    analyze_detailed_opportunities()
