#!/usr/bin/env python3
"""
EQ12 Enhanced Parlay Builder - Extended Analysis
Additional parlay combinations including cross-sport stacks and complex SGPs.
"""

import json
from datetime import datetime

from eq12_live_parlay_analyzer import LiveSportsDataFetcher, ParlayBuilder


class ExtendedParlayBuilder(ParlayBuilder):
    """Extended parlay builder with more sophisticated combinations."""

    def build_cross_sport_stacks(self, games: list) -> list:
        """Build cross-sport correlated stacks."""
        stacks = []

        # Find NFL and NBA games for prime-time correlation
        nfl_games = [g for g in games if g["sport"] == "NFL"]
        nba_games = [g for g in games if g["sport"] == "NBA"]

        for nfl_game in nfl_games:
            for nba_game in nba_games:
                # Overs correlation in prime time
                stack_legs = [
                    {
                        "game": nfl_game,
                        "market_type": "total",
                        "selection": f"over {nfl_game['markets']['totals']['over_under']}",
                        "odds": nfl_game["markets"]["totals"]["over_odds"],
                    },
                    {
                        "game": nba_game,
                        "market_type": "total",
                        "selection": f"over {nba_game['markets']['totals']['over_under']}",
                        "odds": nba_game["markets"]["totals"]["over_odds"],
                    },
                ]

                stack = self._create_parlay(stack_legs, "Cross-Sport Overs Stack")
                if stack:
                    stack["correlation_boost"] = 0.18  # Prime time correlation
                    stacks.append(stack)

        return stacks

    def build_mega_parlays(self, games: list) -> list:
        """Build higher-leg parlays for bigger payouts (4-6 legs)."""
        mega_parlays = []

        if len(games) >= 4:
            # 4-leg cross-sport mega parlay
            legs = []
            for _i, game in enumerate(games[:4]):
                market = self._get_best_market(game)
                legs.append(market)

            mega = self._create_parlay(legs, "4-Leg Mega Parlay")
            if mega:
                mega_parlays.append(mega)

        return mega_parlays

    def build_prop_heavy_sgps(self, games: list) -> list:
        """Build SGPs focused heavily on player props."""
        prop_sgps = []

        for game in games:
            if not game.get("player_props") or len(game["player_props"]) < 3:
                continue

            # 3+ prop SGP
            prop_legs = []
            for prop in game["player_props"][:3]:
                prop_leg = {
                    "game": game,
                    "market_type": "player_prop",
                    "selection": f"{prop['player']} {prop['market']} Over {prop['line']}",
                    "odds": prop["over_odds"],
                }
                prop_legs.append(prop_leg)

            prop_sgp = self._create_parlay(
                prop_legs, f"3-Prop SGP: {game['away_team']} @ {game['home_team']}"
            )
            if prop_sgp:
                prop_sgp["correlation_boost"] = 0.25
                prop_sgps.append(prop_sgp)

        return prop_sgps


def generate_comprehensive_analysis():
    """Generate comprehensive parlay analysis with all types."""

    print("🎯 EQ12 COMPREHENSIVE PARLAY ANALYSIS")
    print("=" * 70)
    print(f"⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize components
    data_fetcher = LiveSportsDataFetcher()
    extended_builder = ExtendedParlayBuilder()

    # Get games starting after 4:45 PM
    cutoff_time = datetime.now().replace(hour=16, minute=45, second=0)
    games = data_fetcher.fetch_live_games(cutoff_time)

    if not games:
        print("❌ No games found")
        return

    print(f"\n📊 Analyzing {len(games)} games for optimal parlays...")

    # Generate all parlay types
    parlay_categories = {
        "Regular Cross-Sport": extended_builder.build_regular_parlays(games),
        "Same Game Parlays": extended_builder.build_same_game_parlays(games),
        "Stacked SGPs": extended_builder.build_stacked_sgps(games),
        "Cross-Sport Stacks": extended_builder.build_cross_sport_stacks(games),
        "Prop-Heavy SGPs": extended_builder.build_prop_heavy_sgps(games),
        "Mega Parlays": extended_builder.build_mega_parlays(games),
    }

    # Display results by category
    all_recommendations = []

    for category, parlays in parlay_categories.items():
        if not parlays:
            continue

        print(f"\n🔥 {category.upper()}")
        print("-" * 60)

        for i, parlay in enumerate(parlays[:3], 1):  # Top 3 per category
            print(f"\n   #{i} - {parlay.get('type', category)}")
            print(
                f"   🎯 Win Prob: {parlay['win_probability']:.1%} | EV: {parlay['expected_value_pct']:+.1%}"
            )
            print(
                f"   💰 Odds: {parlay['american_odds']:+d} | Kelly: {parlay['kelly_fraction']:.1%}"
            )
            print(f"   💵 Stake: ${parlay['recommended_stake']:.0f}")
            print(
                f"   📋 {' | '.join(parlay['legs'][:2])}{'...' if len(parlay['legs']) > 2 else ''}"
            )

            all_recommendations.append(parlay)

    # Overall top recommendations
    all_recommendations.sort(key=lambda x: x["expected_value_pct"], reverse=True)

    print("\n🏆 TOP 5 OVERALL RECOMMENDATIONS")
    print("=" * 70)

    for i, parlay in enumerate(all_recommendations[:5], 1):
        print(f"\n#{i} {parlay.get('type', 'Parlay')}")
        print(f"   🎯 {parlay['win_probability']:.1%} win probability")
        print(f"   💰 {parlay['american_odds']:+d} odds")
        print(f"   📈 {parlay['expected_value_pct']:+.1%} expected value")
        print(f"   🧮 {parlay['kelly_fraction']:.1%} Kelly fraction")
        print(f"   💵 ${parlay['recommended_stake']:.0f} recommended stake")
        print(f"   🛡️  {parlay['risk_level']} risk")
        print(f"   📋 {parlay['reasoning']}")

    # Statistical summary
    approved = [p for p in all_recommendations if p["risk_level"] in ["LOW", "MEDIUM"]]

    print("\n📊 STATISTICAL SUMMARY")
    print(f"   Total Parlays Generated: {len(all_recommendations)}")
    print(f"   Risk-Approved: {len(approved)}")
    print(f"   Average Win Rate: {sum(p['win_probability'] for p in approved) / len(approved):.1%}")
    print(
        f"   Average Expected Value: {sum(p['expected_value_pct'] for p in approved) / len(approved):+.1%}"
    )
    print(f"   Best Single EV: {max(p['expected_value_pct'] for p in approved):+.1%}")

    # Save comprehensive results
    results = {
        "timestamp": datetime.now().isoformat(),
        "games_analyzed": len(games),
        "parlay_categories": {cat: len(parlays) for cat, parlays in parlay_categories.items()},
        "top_recommendations": all_recommendations[:10],
        "statistical_summary": {
            "total_generated": len(all_recommendations),
            "risk_approved": len(approved),
            "avg_win_rate": (
                sum(p["win_probability"] for p in approved) / len(approved) if approved else 0
            ),
            "avg_expected_value": (
                sum(p["expected_value_pct"] for p in approved) / len(approved) if approved else 0
            ),
        },
    }

    from pathlib import Path

    logs_dir = Path("C:/EQ12/logs")
    results_file = logs_dir / f"comprehensive_parlays_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Full analysis saved to: {results_file}")
    print("🚀 Ready to place optimal bets!")

    return all_recommendations[:5]


if __name__ == "__main__":
    generate_comprehensive_analysis()
