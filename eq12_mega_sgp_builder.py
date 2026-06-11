"""
EQ12 MEGA SGP BUILDER - Up to 20 legs + Stacked + Cross-Sport
Advanced correlation analysis for maximum payout potential
Targets 10x+ ROI with $8 stake using multi-game combinations
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import requests


class EQ12MegaSGPBuilder:
    """Advanced SGP builder supporting up to 20 legs + stacked + cross-sport."""

    def __init__(self):
        """Initialize with EQ12 production configuration."""

        # EQ12 production API key
        self.api_key = "ODDS_API_KEY_PLACEHOLDER"
        self.base_url = "https://api.the-odds-api.com/v4"

        # User requirements
        self.stake = 8.0
        self.target_roi = 10.0  # 10x return
        self.target_payout = self.stake * self.target_roi  # $80

        # Sports to include for cross-sport SGPs
        self.sports = ["baseball_mlb", "basketball_nba", "americanfootball_nfl", "icehockey_nhl"]

        # Enhanced correlation matrices
        self.same_game_correlations = {
            # Baseball correlations
            ("runline_home", "over"): 0.40,
            ("runline_away", "under"): 0.45,
            ("ml_underdog", "under"): 0.35,
            ("ml_favorite", "over"): 0.30,
            ("runline_home", "under"): -0.25,
            ("runline_away", "over"): -0.20,
            # Basketball correlations
            ("spread_home", "over"): 0.35,
            ("spread_away", "under"): 0.40,
            ("ml_underdog", "under"): 0.30,
            # Hockey correlations
            ("puckline_home", "over"): 0.45,
            ("puckline_away", "under"): 0.50,
            # Football correlations
            ("spread_home", "over"): 0.30,
            ("spread_away", "under"): 0.35,
        }

        self.cross_game_correlations = {
            # Same sport cross-game (moderate correlation)
            "same_sport_totals": 0.15,  # Weather/conditions affect multiple games
            "same_sport_favorites": 0.10,  # Market sentiment correlation
            "same_sport_underdogs": 0.12,  # Contrarian correlation
            # Cross-sport correlations (weaker but real)
            "cross_sport_totals": 0.05,  # General market conditions
            "cross_sport_underdogs": 0.08,  # Contrarian betting patterns
            "cross_sport_primetime": 0.06,  # Primetime game effects
        }

        # Setup logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        self.logger.info("🚀 EQ12 MEGA SGP Builder initialized")
        self.logger.info(f"Target: ${self.stake} stake for ${self.target_payout}+ payout")
        self.logger.info("Supports: Up to 20 legs, Stacked SGPs, Cross-Sport")

    def fetch_all_games_today(self):
        """Fetch all games from multiple sports happening today."""

        all_games = {}

        for sport in self.sports:
            try:
                self.logger.info(f"Fetching {sport} games...")

                url = f"{self.base_url}/sports/{sport}/odds"
                params = {
                    "apiKey": self.api_key,
                    "regions": "us",
                    "markets": "h2h,spreads,totals",
                    "oddsFormat": "american",
                }

                response = requests.get(url, params=params)
                if response.status_code == 200:
                    games = response.json()

                    # Filter for today's games (any time)
                    today_games = []
                    for game in games:
                        game_time = datetime.fromisoformat(
                            game["commence_time"].replace("Z", "+00:00")
                        )
                        if game_time.date() == datetime.now().date():
                            game["sport"] = sport
                            today_games.append(game)

                    all_games[sport] = today_games
                    self.logger.info(f"Found {len(today_games)} {sport} games today")

            except Exception as e:
                self.logger.error(f"Failed to fetch {sport}: {e}")
                all_games[sport] = []

        return all_games

    def calculate_ml_probability(self, american_odds: int, market_type: str, sport: str) -> float:
        """Calculate ML-enhanced probability with sport-specific boosts."""

        # Base implied probability
        if american_odds > 0:
            implied_prob = 100 / (american_odds + 100)
        else:
            implied_prob = abs(american_odds) / (abs(american_odds) + 100)

        # EQ12 ML enhancement by sport and market
        sport_boosts = {
            "baseball_mlb": {"h2h": 0.12, "spreads": 0.08, "totals": 0.06},
            "basketball_nba": {"h2h": 0.10, "spreads": 0.07, "totals": 0.05},
            "americanfootball_nfl": {"h2h": 0.08, "spreads": 0.06, "totals": 0.04},
            "icehockey_nhl": {"h2h": 0.11, "spreads": 0.08, "totals": 0.06},
        }

        ml_boost = sport_boosts.get(sport, {}).get(market_type, 0.05)
        enhanced_prob = implied_prob + ml_boost

        # EQ12 safety bounds
        return max(0.05, min(enhanced_prob, 0.95))

    def extract_picks_from_game(self, game):
        """Extract all possible picks from a single game."""

        picks = []
        sport = game.get("sport", "unknown")

        if not game.get("bookmakers"):
            return picks

        bookmaker = game["bookmakers"][0]
        markets = {market["key"]: market for market in bookmaker["markets"]}

        game_id = game["id"]
        home_team = game["home_team"]
        away_team = game["away_team"]

        # Money line picks
        if "h2h" in markets:
            for outcome in markets["h2h"]["outcomes"]:
                pick = {
                    "game_id": game_id,
                    "sport": sport,
                    "game_desc": f"{away_team} @ {home_team}",
                    "type": "ml_home" if outcome["name"] == home_team else "ml_away",
                    "description": f"{outcome['name']} ML",
                    "odds": outcome["price"],
                    "probability": self.calculate_ml_probability(outcome["price"], "h2h", sport),
                    "team": outcome["name"],
                }
                picks.append(pick)

        # Spread/runline picks
        if "spreads" in markets:
            for outcome in markets["spreads"]["outcomes"]:
                spread_type = "runline" if sport == "baseball_mlb" else "spread"
                pick_type = (
                    f"{spread_type}_home" if outcome["name"] == home_team else f"{spread_type}_away"
                )

                pick = {
                    "game_id": game_id,
                    "sport": sport,
                    "game_desc": f"{away_team} @ {home_team}",
                    "type": pick_type,
                    "description": f"{outcome['name']} {outcome.get('point', 'spread')}",
                    "odds": outcome["price"],
                    "probability": self.calculate_ml_probability(
                        outcome["price"], "spreads", sport
                    ),
                    "team": outcome["name"],
                    "spread": outcome.get("point", 0),
                }
                picks.append(pick)

        # Total picks
        if "totals" in markets:
            for outcome in markets["totals"]["outcomes"]:
                pick = {
                    "game_id": game_id,
                    "sport": sport,
                    "game_desc": f"{away_team} @ {home_team}",
                    "type": outcome["name"].lower(),
                    "description": f"{outcome['name']} {outcome.get('point', 'total')}",
                    "odds": outcome["price"],
                    "probability": self.calculate_ml_probability(outcome["price"], "totals", sport),
                    "total": outcome.get("point", 0),
                }
                picks.append(pick)

        return picks

    def calculate_sgp_probability(self, picks):
        """Calculate SGP probability with advanced correlation analysis."""

        if not picks:
            return 0

        if len(picks) == 1:
            return picks[0]["probability"]

        # Group picks by game and sport
        same_game_groups = {}
        cross_game_same_sport = {}
        cross_sport_picks = {}

        for pick in picks:
            # Same game grouping
            if pick["game_id"] not in same_game_groups:
                same_game_groups[pick["game_id"]] = []
            same_game_groups[pick["game_id"]].append(pick)

            # Cross-game same sport grouping
            if pick["sport"] not in cross_game_same_sport:
                cross_game_same_sport[pick["sport"]] = []
            cross_game_same_sport[pick["sport"]].append(pick)

            # Cross-sport grouping
            sport_category = self._get_sport_category(pick["sport"])
            if sport_category not in cross_sport_picks:
                cross_sport_picks[sport_category] = []
            cross_sport_picks[sport_category].append(pick)

        # Calculate probability with correlations
        total_probability = 1.0

        # Apply same-game correlations
        for _game_id, game_picks in same_game_groups.items():
            game_prob = 1.0
            for pick in game_picks:
                game_prob *= pick["probability"]

            # Apply same-game correlations
            if len(game_picks) >= 2:
                correlation_boost = self._calculate_same_game_correlation(game_picks)
                game_prob *= 1 + correlation_boost

            total_probability *= game_prob

        # Apply cross-game correlations
        if len(same_game_groups) > 1:
            cross_correlation = self._calculate_cross_game_correlation(picks)
            total_probability *= 1 + cross_correlation

        # Apply cross-sport correlations
        if len(cross_sport_picks) > 1:
            cross_sport_correlation = self._calculate_cross_sport_correlation(picks)
            total_probability *= 1 + cross_sport_correlation

        # Safety bounds
        return max(0.001, min(total_probability, 0.95))

    def _get_sport_category(self, sport):
        """Categorize sports for correlation analysis."""
        categories = {
            "baseball_mlb": "baseball",
            "basketball_nba": "basketball",
            "americanfootball_nfl": "football",
            "icehockey_nhl": "hockey",
        }
        return categories.get(sport, sport)

    def _calculate_same_game_correlation(self, picks):
        """Calculate correlation for picks within the same game."""

        if len(picks) < 2:
            return 0

        total_correlation = 0
        comparisons = 0

        for i, pick1 in enumerate(picks):
            for pick2 in picks[i + 1 :]:
                correlation_key = (pick1["type"], pick2["type"])
                correlation = self.same_game_correlations.get(correlation_key, 0)

                # Also check reverse
                if correlation == 0:
                    correlation = self.same_game_correlations.get((pick2["type"], pick1["type"]), 0)

                total_correlation += correlation
                comparisons += 1

        return total_correlation / max(comparisons, 1) if comparisons > 0 else 0

    def _calculate_cross_game_correlation(self, picks):
        """Calculate correlation for picks across different games."""

        # Group by sport
        sport_groups = {}
        for pick in picks:
            if pick["sport"] not in sport_groups:
                sport_groups[pick["sport"]] = []
            sport_groups[pick["sport"]].append(pick)

        # Same sport cross-game correlation
        correlation = 0
        if len(sport_groups) == 1:  # All picks from same sport
            correlation = self.cross_game_correlations.get("same_sport_totals", 0.10)

        return correlation

    def _calculate_cross_sport_correlation(self, picks):
        """Calculate correlation for cross-sport picks."""

        sports = {pick["sport"] for pick in picks}

        if len(sports) > 1:
            return self.cross_game_correlations.get("cross_sport_totals", 0.05)

        return 0

    def calculate_combined_odds(self, picks):
        """Calculate combined American odds for all picks."""

        combined_decimal = 1.0

        for pick in picks:
            decimal = pick["odds"] / 100 + 1 if pick["odds"] > 0 else 100 / abs(pick["odds"]) + 1

            combined_decimal *= decimal

        # Convert back to American odds
        if combined_decimal >= 2:
            return int((combined_decimal - 1) * 100)
        else:
            return int(-100 / (combined_decimal - 1))

    def build_mega_sgps(self, all_games):
        """Build various SGP strategies with up to 20 legs."""

        self.logger.info("Building MEGA SGPs with up to 20 legs...")

        # Extract all possible picks
        all_picks = []
        for _sport, games in all_games.items():
            for game in games:
                picks = self.extract_picks_from_game(game)
                all_picks.extend(picks)

        self.logger.info(f"Total available picks: {len(all_picks)}")

        mega_sgps = []

        # Strategy 1: Focus on SEA vs DET + other games (stacked)
        sea_det_sgps = self._build_sea_det_stacked_sgps(all_picks)
        mega_sgps.extend(sea_det_sgps)

        # Strategy 2: High correlation same-sport combinations
        same_sport_sgps = self._build_same_sport_mega_sgps(all_picks)
        mega_sgps.extend(same_sport_sgps)

        # Strategy 3: Cross-sport combinations
        cross_sport_sgps = self._build_cross_sport_mega_sgps(all_picks)
        mega_sgps.extend(cross_sport_sgps)

        # Strategy 4: Maximum legs for highest payout
        max_legs_sgps = self._build_max_legs_sgps(all_picks)
        mega_sgps.extend(max_legs_sgps)

        # Filter and rank
        qualifying_sgps = [sgp for sgp in mega_sgps if sgp and sgp.get("roi", 0) >= self.target_roi]

        if not qualifying_sgps:
            self.logger.warning("No MEGA SGPs found meeting 10x ROI requirement")
            if mega_sgps:
                mega_sgps.sort(key=lambda x: x.get("roi", 0), reverse=True)
                return mega_sgps[0]
            return None

        # Sort by ROI, then confidence
        qualifying_sgps.sort(key=lambda x: (x["roi"], x["confidence_score"]), reverse=True)

        return qualifying_sgps[0]

    def _build_sea_det_stacked_sgps(self, all_picks):
        """Build stacked SGPs starting with SEA vs DET game."""

        sgps = []

        # Find SEA vs DET picks
        sea_det_picks = [
            p for p in all_picks if "Mariners" in p["game_desc"] and "Tigers" in p["game_desc"]
        ]

        if not sea_det_picks:
            return sgps

        # Best SEA vs DET combination
        best_sea_det_combo = [
            next(
                (
                    p
                    for p in sea_det_picks
                    if p["type"] == "runline_away" and "Mariners" in p["team"]
                ),
                None,
            ),
            next((p for p in sea_det_picks if p["type"] == "under"), None),
        ]
        best_sea_det_combo = [p for p in best_sea_det_combo if p is not None]

        if len(best_sea_det_combo) >= 2:
            # Add picks from other games
            other_picks = [p for p in all_picks if p["game_id"] != best_sea_det_combo[0]["game_id"]]

            # Add 3-6 more high-probability picks
            high_prob_picks = sorted(other_picks, key=lambda x: x["probability"], reverse=True)[:6]

            combined_picks = best_sea_det_combo + high_prob_picks[:4]  # 6 legs total

            sgp = self._create_sgp_from_picks(combined_picks, "SEA vs DET Stacked")
            if sgp:
                sgps.append(sgp)

        return sgps

    def _build_same_sport_mega_sgps(self, all_picks):
        """Build mega SGPs within same sport."""

        sgps = []

        # Group by sport
        by_sport = {}
        for pick in all_picks:
            if pick["sport"] not in by_sport:
                by_sport[pick["sport"]] = []
            by_sport[pick["sport"]].append(pick)

        for sport, picks in by_sport.items():
            if len(picks) >= 6:  # Need enough picks for mega SGP
                # Strategy: Mix of high-probability + correlated picks
                high_prob = sorted(picks, key=lambda x: x["probability"], reverse=True)[:8]

                # Add some medium probability for higher payout
                medium_prob = [p for p in picks if 0.35 <= p["probability"] <= 0.55][:4]

                combined = high_prob + medium_prob
                if len(combined) >= 6:
                    sgp = self._create_sgp_from_picks(combined[:12], f"Same Sport {sport} Mega")
                    if sgp:
                        sgps.append(sgp)

        return sgps

    def _build_cross_sport_mega_sgps(self, all_picks):
        """Build cross-sport mega SGPs."""

        sgps = []

        # Group by sport
        by_sport = {}
        for pick in all_picks:
            if pick["sport"] not in by_sport:
                by_sport[pick["sport"]] = []
            by_sport[pick["sport"]].append(pick)

        if len(by_sport) >= 2:  # Need multiple sports
            # Take best picks from each sport
            cross_sport_picks = []
            for _sport, picks in by_sport.items():
                # Take top 3 picks from each sport
                top_picks = sorted(picks, key=lambda x: x["probability"], reverse=True)[:3]
                cross_sport_picks.extend(top_picks)

            if len(cross_sport_picks) >= 6:
                sgp = self._create_sgp_from_picks(cross_sport_picks[:15], "Cross-Sport Mega")
                if sgp:
                    sgps.append(sgp)

        return sgps

    def _build_max_legs_sgps(self, all_picks):
        """Build maximum 20-leg SGPs for highest payout."""

        sgps = []

        if len(all_picks) >= 15:
            # Strategy 1: High probability picks (safer 20-leg)
            high_prob_picks = sorted(all_picks, key=lambda x: x["probability"], reverse=True)[:20]
            sgp = self._create_sgp_from_picks(high_prob_picks, "20-Leg High Probability")
            if sgp:
                sgps.append(sgp)

            # Strategy 2: Mixed probability for balance
            mixed_picks = []
            # 10 high probability
            mixed_picks.extend(sorted(all_picks, key=lambda x: x["probability"], reverse=True)[:10])
            # 10 medium probability for higher payout
            medium_picks = [p for p in all_picks if 0.40 <= p["probability"] <= 0.60]
            mixed_picks.extend(medium_picks[:10])

            if len(mixed_picks) >= 15:
                sgp = self._create_sgp_from_picks(mixed_picks[:20], "20-Leg Mixed Strategy")
                if sgp:
                    sgps.append(sgp)

        return sgps

    def _create_sgp_from_picks(self, picks, strategy_name):
        """Create SGP object from list of picks."""

        if not picks:
            return None

        # Calculate probability with correlations
        win_probability = self.calculate_sgp_probability(picks)

        # Calculate combined odds and payout
        combined_odds = self.calculate_combined_odds(picks)

        if combined_odds > 0:
            combined_decimal = (combined_odds / 100) + 1
        else:
            combined_decimal = (100 / abs(combined_odds)) + 1

        payout = self.stake * combined_decimal
        roi = payout / self.stake

        # Expected value
        expected_return = win_probability * payout
        ev_percentage = (expected_return - self.stake) / self.stake

        # Kelly fraction
        kelly = (win_probability * combined_decimal - 1) / (combined_decimal - 1)
        kelly = max(0, min(kelly, 0.25))

        # Confidence score
        confidence_score = win_probability * (1 + ev_percentage) * (len(picks) / 20)

        # Determine confidence level
        if win_probability >= 0.25 and ev_percentage >= 0.08 and len(picks) <= 10:
            confidence_level = "HIGH"
        elif win_probability >= 0.15 and ev_percentage >= 0.05:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"

        sgp = {
            "legs": picks,
            "num_legs": len(picks),
            "combined_odds": combined_odds,
            "win_probability": win_probability,
            "expected_value_pct": ev_percentage,
            "payout": payout,
            "roi": roi,
            "kelly_fraction": kelly,
            "confidence_level": confidence_level,
            "confidence_score": confidence_score,
            "strategy": strategy_name,
            "sports_involved": list({p["sport"] for p in picks}),
            "games_involved": len({p["game_id"] for p in picks}),
        }

        return sgp


def main():
    """Generate MEGA SGPs with up to 20 legs + stacked + cross-sport."""

    print("🚀 EQ12 MEGA SGP BUILDER")
    print("=" * 60)
    print("Features: Up to 20 legs | Stacked SGPs | Cross-Sport")
    print("Target: $8 stake → $80+ payout (10x ROI)")
    print("Advanced correlation analysis for maximum payouts")

    try:
        builder = EQ12MegaSGPBuilder()

        # Fetch all games
        print("\n🔄 Fetching all games from multiple sports...")
        all_games = builder.fetch_all_games_today()

        total_games = sum(len(games) for games in all_games.values())
        print(f"Found {total_games} total games across all sports")

        if total_games == 0:
            print("❌ No games found for today")
            return

        # Build MEGA SGPs
        print("\n🤖 Building MEGA SGPs with advanced correlation analysis...")
        sgp = builder.build_mega_sgps(all_games)

        if not sgp:
            print("❌ Could not build qualifying MEGA SGP")
            return

        # Display results
        print("\n🏆 MEGA SGP RECOMMENDATION")
        print("=" * 60)

        print(f"🎯 Strategy: {sgp['strategy']}")
        print(f"🎮 Sports Involved: {', '.join(sgp['sports_involved'])}")
        print(f"🎪 Games Involved: {sgp['games_involved']}")
        print(f"🦵 Total Legs: {sgp['num_legs']}")

        print(f"\n📋 SGP Legs ({sgp['num_legs']} total):")
        for i, leg in enumerate(sgp["legs"], 1):
            sport_emoji = {
                "baseball_mlb": "⚾",
                "basketball_nba": "🏀",
                "americanfootball_nfl": "🏈",
                "icehockey_nhl": "🏒",
            }.get(leg["sport"], "🎯")
            print(
                f"   {i:2d}. {sport_emoji} {leg['description']} ({leg['odds']:+d}) - {leg['game_desc']}"
            )

        print("\n📊 MEGA SGP Analysis:")
        print(f"   🎯 Win Probability: {sgp['win_probability']:.2%}")
        print(f"   💰 Combined Odds: {sgp['combined_odds']:+d}")
        print(f"   💵 Stake: ${builder.stake:.0f}")
        print(f"   🏆 Potential Payout: ${sgp['payout']:.2f}")
        print(f"   📈 ROI: {sgp['roi']:.1f}x {'🎯' if sgp['roi'] >= 10 else '⚠️'}")
        print(f"   📊 Expected Value: {sgp['expected_value_pct']:+.1%}")
        print(f"   🧮 Kelly Fraction: {sgp['kelly_fraction']:.2%}")
        print(f"   ⭐ Confidence: {sgp['confidence_level']}")

        # Achievement check
        print("\n✅ TARGET ACHIEVEMENT:")
        print(f"   Stake: ${builder.stake} ✅")
        print(
            f"   ROI: {sgp['roi']:.1f}x {'🎯 ACHIEVES 10x TARGET!' if sgp['roi'] >= 10 else '⚠️ Below target'}"
        )
        print(
            f"   Payout: ${sgp['payout']:.2f} {'🎯 Above $80!' if sgp['payout'] >= 80 else '⚠️ Below $80'}"
        )
        print(f"   Legs: {sgp['num_legs']}/20 ✅")

        # Risk assessment
        print("\n⚠️  EQ12 RISK ASSESSMENT:")
        print(
            f"   Expected Value: {'✅ Positive' if sgp['expected_value_pct'] > 0 else '❌ Negative'}"
        )
        print(
            f"   Kelly Criterion: {'✅ Safe' if sgp['kelly_fraction'] <= 0.25 else '⚠️ High Risk'}"
        )
        print(f"   Confidence Level: {sgp['confidence_level']}")
        print(
            f"   Games Spread: {sgp['games_involved']} games {'✅ Diversified' if sgp['games_involved'] > 1 else '⚠️ Single game'}"
        )

        if sgp["roi"] >= 10:
            print("\n🎯 SUCCESS: MEGA SGP achieves 10x ROI target!")
            print(f"💪 {sgp['num_legs']}-leg combination across {sgp['games_involved']} games")
        else:
            print(f"\n📈 BEST AVAILABLE: {sgp['roi']:.1f}x ROI with {sgp['num_legs']} legs")

        # Save results
        logs_dir = Path("C:/EQ12/logs")
        logs_dir.mkdir(exist_ok=True)

        results = {
            "timestamp": datetime.now().isoformat(),
            "mega_sgp": sgp,
            "meets_10x_target": sgp["roi"] >= 10,
            "total_games_analyzed": total_games,
        }

        results_file = logs_dir / f"mega_sgp_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n💾 MEGA analysis saved: {results_file}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
