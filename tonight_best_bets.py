#!/usr/bin/env python3
"""
EQ12 Best Parlays & SGPs for Tonight's Games (After 5:00 PM)
Real-time analysis for optimal betting opportunities
"""

import logging
from datetime import UTC, datetime

from eq12_odds_ingestor import OddsIngestor

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def american_to_decimal(american_odds):
    """Convert American odds to decimal"""
    if american_odds > 0:
        return (american_odds / 100) + 1
    else:
        return (100 / abs(american_odds)) + 1


def calculate_parlay_odds(*decimal_odds):
    """Calculate combined parlay odds"""
    combined = 1.0
    for odds in decimal_odds:
        combined *= odds
    return combined


def get_games_after_5pm():
    """Get all games starting after 5:00 PM today"""
    ingestor = OddsIngestor()

    sports = {
        "baseball_mlb": "MLB",
        "icehockey_nhl": "NHL",
        "basketball_nba": "NBA",
        "americanfootball_ncaaf": "NCAAF",
    }

    all_games = []
    cutoff_time = datetime.now(UTC).replace(hour=22, minute=0, second=0)  # 5 PM ET = 22:00 UTC

    for sport_key, sport_name in sports.items():
        try:
            result = ingestor.ingest_live_odds(sport_key, force_refresh=True)
            if isinstance(result, dict) and "games" in result:
                for game in result["games"]:
                    if isinstance(game, dict):
                        game_time_str = game.get("commence_time", "")
                        if game_time_str:
                            try:
                                game_time = datetime.fromisoformat(
                                    game_time_str.replace("Z", "+00:00")
                                )
                                if game_time >= cutoff_time:
                                    game["sport_name"] = sport_name
                                    game["sport_key"] = sport_key
                                    all_games.append(game)
                            except:
                                continue
        except Exception as e:
            logger.error(f"Error fetching {sport_name}: {e}")

    return sorted(all_games, key=lambda x: x.get("commence_time", ""))


def analyze_game_markets(game):
    """Analyze a game's betting markets and find best opportunities"""

    game.get("home_team", "Unknown")
    game.get("away_team", "Unknown")
    game.get("sport_name", "Unknown")

    # Find best odds across bookmakers for each market
    best_odds = {}

    for bookmaker in game.get("bookmakers", []):
        book_name = bookmaker.get("key", "unknown")

        for market in bookmaker.get("markets", []):
            market_key = market.get("key")

            for outcome in market.get("outcomes", []):
                name = outcome.get("name", "")
                price = outcome.get("price", 0)
                point = outcome.get("point")

                # Create unique key for this bet
                bet_key = f"{market_key}_{name}"
                if point is not None:
                    bet_key += f"_{point}"

                # Track best odds
                if bet_key not in best_odds or price > best_odds[bet_key]["price"]:
                    best_odds[bet_key] = {
                        "market": market_key,
                        "name": name,
                        "price": price,
                        "point": point,
                        "book": book_name,
                        "decimal": american_to_decimal(price),
                    }

    return best_odds


def find_best_sgps(games):
    """Find best Same Game Parlays"""
    sgp_opportunities = []

    for game in games:
        home_team = game.get("home_team", "Unknown")
        away_team = game.get("away_team", "Unknown")
        sport = game.get("sport_name", "Unknown")
        game_time = game.get("commence_time", "")[:16]

        best_odds = analyze_game_markets(game)

        # Look for high-value SGP combinations
        sgp_legs = []

        # Common SGP strategies by sport
        if sport == "MLB":
            # MLB SGP: Home team + Over total
            home_ml = None
            over_total = None

            for _bet_key, bet in best_odds.items():
                if bet["market"] == "h2h" and bet["name"] == home_team:
                    home_ml = bet
                elif bet["market"] == "totals" and "Over" in bet["name"]:
                    over_total = bet

            if home_ml and over_total and home_ml["price"] > 120:  # Underdog home team
                combined_odds = calculate_parlay_odds(home_ml["decimal"], over_total["decimal"])
                if combined_odds >= 4.0:  # 4.0+ odds (300+ American)
                    sgp_legs = [
                        f"{home_team} ML ({home_ml['price']:+d})",
                        f"Over {over_total.get('point', 'Total')} ({over_total['price']:+d})",
                    ]

        elif sport == "NHL":
            # NHL SGP: Underdog + Over total
            away_ml = None
            over_total = None

            for _bet_key, bet in best_odds.items():
                if bet["market"] == "h2h" and bet["name"] == away_team and bet["price"] > 150:
                    away_ml = bet
                elif bet["market"] == "totals" and "Over" in bet["name"]:
                    over_total = bet

            if away_ml and over_total:
                combined_odds = calculate_parlay_odds(away_ml["decimal"], over_total["decimal"])
                if combined_odds >= 5.0:
                    sgp_legs = [
                        f"{away_team} ML ({away_ml['price']:+d})",
                        f"Over {over_total.get('point', 'Total')} ({over_total['price']:+d})",
                    ]

        elif sport == "NCAAF":
            # NCAAF SGP: Spread + Total (correlated)
            spread_bet = None
            total_bet = None

            for _bet_key, bet in best_odds.items():
                if bet["market"] == "spreads" and bet["point"] and bet["price"] >= -120:
                    spread_bet = bet
                elif bet["market"] == "totals" and bet["price"] >= -120:
                    total_bet = bet

            if spread_bet and total_bet:
                combined_odds = calculate_parlay_odds(spread_bet["decimal"], total_bet["decimal"])
                if combined_odds >= 3.5:
                    point_str = f"{spread_bet['point']:+.1f}" if spread_bet["point"] else ""
                    total_str = f"{total_bet.get('point', 'Total')}"
                    sgp_legs = [
                        f"{spread_bet['name']} {point_str} ({spread_bet['price']:+d})",
                        f"{total_bet['name']} {total_str} ({total_bet['price']:+d})",
                    ]

        if sgp_legs:
            combined_odds = calculate_parlay_odds(
                *[
                    bet["decimal"]
                    for bet in [home_ml or away_ml or spread_bet, over_total or total_bet]
                ]
            )
            american_odds = (
                int((combined_odds - 1) * 100)
                if combined_odds < 2
                else int((combined_odds - 1) * 100)
            )

            sgp_opportunities.append(
                {
                    "game": f"{away_team} @ {home_team}",
                    "sport": sport,
                    "time": game_time,
                    "legs": sgp_legs,
                    "combined_odds": combined_odds,
                    "american_odds": american_odds,
                    "recommended_stake": min(50, max(15, 200 // combined_odds)),
                }
            )

    return sorted(sgp_opportunities, key=lambda x: x["combined_odds"], reverse=True)


def find_best_cross_sport_parlays(games):
    """Find best cross-sport parlays"""
    parlay_legs = []

    # Look for strong favorites and good value underdogs
    for game in games:
        best_odds = analyze_game_markets(game)
        home_team = game.get("home_team", "Unknown")
        away_team = game.get("away_team", "Unknown")
        sport = game.get("sport_name", "Unknown")

        # Find moneylines
        for _bet_key, bet in best_odds.items():
            if bet["market"] == "h2h":
                # Strong favorites (-200 or better)
                if bet["price"] <= -180:
                    parlay_legs.append(
                        {
                            "game": f"{away_team} @ {home_team}",
                            "sport": sport,
                            "bet": f"{bet['name']} ML",
                            "odds": bet["price"],
                            "decimal": bet["decimal"],
                            "confidence": "HIGH",
                            "type": "favorite",
                        }
                    )
                # Value underdogs (+200 to +400)
                elif 200 <= bet["price"] <= 400:
                    parlay_legs.append(
                        {
                            "game": f"{away_team} @ {home_team}",
                            "sport": sport,
                            "bet": f"{bet['name']} ML",
                            "odds": bet["price"],
                            "decimal": bet["decimal"],
                            "confidence": "MEDIUM",
                            "type": "underdog",
                        }
                    )

    # Create balanced parlays
    parlays = []

    # Conservative parlay: 3-4 strong favorites
    favorites = [leg for leg in parlay_legs if leg["type"] == "favorite"][:4]
    if len(favorites) >= 3:
        combined_odds = calculate_parlay_odds(*[leg["decimal"] for leg in favorites])
        parlays.append(
            {
                "name": "Conservative Favorites Parlay",
                "legs": favorites,
                "combined_odds": combined_odds,
                "american_odds": int((combined_odds - 1) * 100),
                "recommended_stake": 50,
                "risk_level": "LOW",
            }
        )

    # Value parlay: 2 favorites + 1 underdog
    if len(favorites) >= 2:
        underdogs = [leg for leg in parlay_legs if leg["type"] == "underdog"][:1]
        if underdogs:
            value_legs = favorites[:2] + underdogs
            combined_odds = calculate_parlay_odds(*[leg["decimal"] for leg in value_legs])
            parlays.append(
                {
                    "name": "Value Mixed Parlay",
                    "legs": value_legs,
                    "combined_odds": combined_odds,
                    "american_odds": int((combined_odds - 1) * 100),
                    "recommended_stake": 30,
                    "risk_level": "MEDIUM",
                }
            )

    return parlays


def main():
    """Main analysis function"""
    print("🎯 EQ12 BEST BETS - TONIGHT'S GAMES (AFTER 5:00 PM)")
    print("=" * 80)

    # Get games
    games = get_games_after_5pm()

    if not games:
        print("❌ No games found starting after 5:00 PM today")
        return

    print(f"📊 ANALYZING {len(games)} GAMES STARTING AFTER 5:00 PM")
    print("\n🕐 TONIGHT'S SCHEDULE:")
    for game in games:
        sport = game.get("sport_name", "Unknown")
        home = game.get("home_team", "Unknown")
        away = game.get("away_team", "Unknown")
        time = game.get("commence_time", "")[:16]
        print(f"  • {sport}: {away} @ {home} - {time}")

    print("\n" + "=" * 80)

    # Find best SGPs
    sgps = find_best_sgps(games)

    if sgps:
        print("\n🎲 BEST SAME GAME PARLAYS (SGPs)")
        print("-" * 50)

        for i, sgp in enumerate(sgps[:5], 1):  # Top 5 SGPs
            print(f"\n{i}. {sgp['sport']}: {sgp['game']}")
            print(f"   Time: {sgp['time']}")
            print(f"   Legs: {' + '.join(sgp['legs'])}")
            print(f"   Odds: {sgp['combined_odds']:.2f}x ({sgp['american_odds']:+d})")
            print(f"   Recommended Stake: ${sgp['recommended_stake']}")
            print(f"   Potential Payout: ${sgp['recommended_stake'] * sgp['combined_odds']:.0f}")
    else:
        print("\n❌ No qualifying SGPs found for tonight's games")

    # Find cross-sport parlays
    parlays = find_best_cross_sport_parlays(games)

    if parlays:
        print("\n🏆 BEST CROSS-SPORT PARLAYS")
        print("-" * 50)

        for i, parlay in enumerate(parlays, 1):
            print(f"\n{i}. {parlay['name']} ({parlay['risk_level']} Risk)")
            print("   Legs:")
            for leg in parlay["legs"]:
                print(f"     • {leg['sport']}: {leg['bet']} ({leg['odds']:+d})")
            print(
                f"   Combined Odds: {parlay['combined_odds']:.2f}x ({parlay['american_odds']:+d})"
            )
            print(f"   Recommended Stake: ${parlay['recommended_stake']}")
            print(
                f"   Potential Payout: ${parlay['recommended_stake'] * parlay['combined_odds']:.0f}"
            )
    else:
        print("\n❌ No qualifying cross-sport parlays found")

    # Stacked SGPs
    if len(sgps) >= 2:
        print("\n🔥 STACKED SGP COMBINATIONS")
        print("-" * 50)

        # Take top 2-3 SGPs and combine them
        stack_combinations = [
            sgps[:2],  # Top 2
            sgps[:3] if len(sgps) >= 3 else None,  # Top 3
        ]

        for i, stack in enumerate([combo for combo in stack_combinations if combo], 1):
            combined_odds = calculate_parlay_odds(*[sgp["combined_odds"] for sgp in stack])
            stake = 20  # Conservative stake for stacked bets

            print(f"\n{i}. Stacked SGP Combo ({len(stack)} games)")
            for sgp in stack:
                print(f"     • {sgp['sport']}: {sgp['game']}")
                print(f"       Legs: {' + '.join(sgp['legs'])}")
            print(f"   Combined Odds: {combined_odds:.1f}x")
            print(f"   Recommended Stake: ${stake}")
            print(f"   Potential Payout: ${stake * combined_odds:.0f}")
            print("   ⚠️  Note: May require multiple sportsbooks")

    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE - All recommendations use LIVE odds data")
    print("💰 Remember to bet responsibly and within your limits!")


if __name__ == "__main__":
    main()
