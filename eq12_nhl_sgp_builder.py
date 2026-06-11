"""
EQ12 NHL SGP Builder - All Games Tonight
Build SGPs for every NHL game using EQ12 correlation analysis
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import requests


class EQ12NHLSGPBuilder:
    """Build SGPs for all NHL games tonight."""

    def __init__(self):
        """Initialize NHL SGP builder."""

        # EQ12 production API key
        self.api_key = "ODDS_API_KEY_PLACEHOLDER"
        self.base_url = "https://api.the-odds-api.com/v4"

        # NHL correlation matrix
        self.nhl_correlations = {
            ("ml_favorite", "puckline_favorite"): 0.60,  # Same team double-down
            ("puckline_home", "over"): 0.45,  # Home favorite scores more
            ("puckline_away", "under"): 0.50,  # Away favorite defensive
            ("ml_underdog", "under"): 0.35,  # Underdog + under
            ("ml_favorite", "over"): 0.30,  # Favorite + over
            ("puckline_home", "under"): -0.25,  # Negative correlation
            ("puckline_away", "over"): -0.20,  # Negative correlation
        }

        # Setup logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        self.logger.info("🏒 EQ12 NHL SGP Builder initialized")

    def fetch_nhl_games_tonight(self):
        """Fetch all NHL games for this week with comprehensive details."""

        try:
            url = f"{self.base_url}/sports/icehockey_nhl/odds"
            params = {
                "apiKey": self.api_key,
                "regions": "us",
                "markets": "h2h,spreads,totals",
                "oddsFormat": "american",
                "dateFormat": "iso",
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            games = response.json()

            self.logger.info(f"API returned {len(games)} total NHL games")

            # Process games and find the 3 target games
            today = datetime.now().date()
            tomorrow = datetime.fromordinal(today.toordinal() + 1).date()
            target_games = []

            for game in games:
                try:
                    game_time = datetime.fromisoformat(game["commence_time"].replace("Z", "+00:00"))
                    game_date = game_time.date()

                    # Add enhanced game info
                    game["local_time"] = game_time.strftime("%I:%M %p ET")
                    game["matchup"] = f"{game['away_team']} @ {game['home_team']}"
                    game["game_date"] = game_date

                    # Check for our 3 target games
                    is_target_game = False

                    # Today's game: Chicago @ Florida
                    if (
                        (
                            game_date == today
                            and "Chicago Blackhawks" in [game["away_team"], game["home_team"]]
                            and "Florida Panthers" in [game["away_team"], game["home_team"]]
                        )
                        or (
                            game_date == tomorrow
                            and "Pittsburgh Penguins" in [game["away_team"], game["home_team"]]
                            and "New York Rangers" in [game["away_team"], game["home_team"]]
                        )
                        or (
                            game_date == tomorrow
                            and "Colorado Avalanche" in [game["away_team"], game["home_team"]]
                            and "Los Angeles Kings" in [game["away_team"], game["home_team"]]
                        )
                    ):
                        is_target_game = True

                    if is_target_game:
                        target_games.append(game)
                        self.logger.info(f"🎯 TARGET: {game['matchup']} at {game['local_time']}")

                except Exception as e:
                    self.logger.error(f"Error processing game: {e}")
                    continue

            self.logger.info("=== TARGET GAMES FOR SGP ANALYSIS ===")
            self.logger.info(f"Found {len(target_games)} target games:")

            for game in target_games:
                game_date_str = "TODAY" if game["game_date"] == today else "LATE TONIGHT"
                self.logger.info(
                    f"  🏒 {game['matchup']} at {game['local_time']} ({game_date_str})"
                )

            self.logger.info("=== END TARGET GAMES ===")

            return target_games

        except Exception as e:
            self.logger.error(f"Failed to fetch NHL games: {e}")
            return []

    def calculate_nhl_probability(self, american_odds: int) -> float:
        """Calculate enhanced probability for NHL markets."""

        # Base implied probability
        if american_odds > 0:
            implied_prob = 100 / (american_odds + 100)
        else:
            implied_prob = abs(american_odds) / (abs(american_odds) + 100)

        # EQ12 NHL enhancement (11% boost)
        enhanced_prob = implied_prob + 0.11

        return max(0.05, min(enhanced_prob, 0.95))

    def build_game_sgps(self, game):
        """Build multiple SGP strategies for a single NHL game."""

        if not game.get("bookmakers"):
            return []

        bookmaker = game["bookmakers"][0]
        markets = {market["key"]: market for market in bookmaker["markets"]}

        home_team = game["home_team"]
        away_team = game["away_team"]
        game_time = datetime.fromisoformat(game["commence_time"].replace("Z", "+00:00"))

        sgps = []

        # Strategy 1: Favorite ML + Puckline + Over (high correlation)
        favorite_over_sgp = self._build_favorite_over_sgp(markets, home_team, away_team, game_time)
        if favorite_over_sgp:
            sgps.append(favorite_over_sgp)

        # Strategy 2: Underdog ML + Under (contrarian play)
        underdog_under_sgp = self._build_underdog_under_sgp(
            markets, home_team, away_team, game_time
        )
        if underdog_under_sgp:
            sgps.append(underdog_under_sgp)

        # Strategy 3: Home team + Over (home ice advantage)
        home_over_sgp = self._build_home_over_sgp(markets, home_team, away_team, game_time)
        if home_over_sgp:
            sgps.append(home_over_sgp)

        # Strategy 4: Road favorite + Under (defensive road play)
        road_under_sgp = self._build_road_under_sgp(markets, home_team, away_team, game_time)
        if road_under_sgp:
            sgps.append(road_under_sgp)

        return sgps

    def _build_favorite_over_sgp(self, markets, home_team, away_team, game_time):
        """Build favorite ML + puckline + over SGP."""

        if not all(k in markets for k in ["h2h", "spreads", "totals"]):
            return None

        # Find favorite
        home_ml = away_ml = None
        for outcome in markets["h2h"]["outcomes"]:
            if outcome["name"] == home_team:
                home_ml = outcome
            else:
                away_ml = outcome

        favorite = home_ml if home_ml["price"] < away_ml["price"] else away_ml

        # Find favorite puckline
        favorite_puckline = None
        for outcome in markets["spreads"]["outcomes"]:
            if outcome["name"] == favorite["name"]:
                favorite_puckline = outcome
                break

        # Find over
        over_total = None
        for outcome in markets["totals"]["outcomes"]:
            if outcome["name"] == "Over":
                over_total = outcome
                break

        if not all([favorite, favorite_puckline, over_total]):
            return None

        legs = [
            {
                "pick": f"{favorite['name']} ML",
                "odds": favorite["price"],
                "probability": self.calculate_nhl_probability(favorite["price"]),
            },
            {
                "pick": f"{favorite_puckline['name']} {favorite_puckline.get('point', 'puckline')}",
                "odds": favorite_puckline["price"],
                "probability": self.calculate_nhl_probability(favorite_puckline["price"]),
            },
            {
                "pick": f"Over {over_total.get('point', 'total')}",
                "odds": over_total["price"],
                "probability": self.calculate_nhl_probability(over_total["price"]),
            },
        ]

        return self._create_sgp(
            legs, f"{away_team} @ {home_team}", game_time, "Favorite + Over", 0.35
        )

    def _build_underdog_under_sgp(self, markets, home_team, away_team, game_time):
        """Build underdog ML + under SGP."""

        if not all(k in markets for k in ["h2h", "totals"]):
            return None

        # Find underdog
        home_ml = away_ml = None
        for outcome in markets["h2h"]["outcomes"]:
            if outcome["name"] == home_team:
                home_ml = outcome
            else:
                away_ml = outcome

        underdog = home_ml if home_ml["price"] > away_ml["price"] else away_ml

        # Find under
        under_total = None
        for outcome in markets["totals"]["outcomes"]:
            if outcome["name"] == "Under":
                under_total = outcome
                break

        if not all([underdog, under_total]):
            return None

        legs = [
            {
                "pick": f"{underdog['name']} ML",
                "odds": underdog["price"],
                "probability": self.calculate_nhl_probability(underdog["price"]),
            },
            {
                "pick": f"Under {under_total.get('point', 'total')}",
                "odds": under_total["price"],
                "probability": self.calculate_nhl_probability(under_total["price"]),
            },
        ]

        return self._create_sgp(
            legs, f"{away_team} @ {home_team}", game_time, "Underdog + Under", 0.25
        )

    def _build_home_over_sgp(self, markets, home_team, away_team, game_time):
        """Build home team ML + over SGP."""

        if not all(k in markets for k in ["h2h", "totals"]):
            return None

        # Find home ML
        home_ml = None
        for outcome in markets["h2h"]["outcomes"]:
            if outcome["name"] == home_team:
                home_ml = outcome
                break

        # Find over
        over_total = None
        for outcome in markets["totals"]["outcomes"]:
            if outcome["name"] == "Over":
                over_total = outcome
                break

        if not all([home_ml, over_total]):
            return None

        legs = [
            {
                "pick": f"{home_ml['name']} ML",
                "odds": home_ml["price"],
                "probability": self.calculate_nhl_probability(home_ml["price"]),
            },
            {
                "pick": f"Over {over_total.get('point', 'total')}",
                "odds": over_total["price"],
                "probability": self.calculate_nhl_probability(over_total["price"]),
            },
        ]

        return self._create_sgp(legs, f"{away_team} @ {home_team}", game_time, "Home + Over", 0.20)

    def _build_road_under_sgp(self, markets, home_team, away_team, game_time):
        """Build road team puckline + under SGP."""

        if not all(k in markets for k in ["spreads", "totals"]):
            return None

        # Find away puckline
        away_puckline = None
        for outcome in markets["spreads"]["outcomes"]:
            if outcome["name"] == away_team:
                away_puckline = outcome
                break

        # Find under
        under_total = None
        for outcome in markets["totals"]["outcomes"]:
            if outcome["name"] == "Under":
                under_total = outcome
                break

        if not all([away_puckline, under_total]):
            return None

        legs = [
            {
                "pick": f"{away_puckline['name']} {away_puckline.get('point', 'puckline')}",
                "odds": away_puckline["price"],
                "probability": self.calculate_nhl_probability(away_puckline["price"]),
            },
            {
                "pick": f"Under {under_total.get('point', 'total')}",
                "odds": under_total["price"],
                "probability": self.calculate_nhl_probability(under_total["price"]),
            },
        ]

        return self._create_sgp(legs, f"{away_team} @ {home_team}", game_time, "Road + Under", 0.30)

    def _create_sgp(self, legs, game_desc, game_time, strategy, correlation_boost):
        """Create SGP object from legs."""

        if not legs:
            return None

        # Calculate combined probability with correlation
        combined_prob = 1.0
        for leg in legs:
            combined_prob *= leg["probability"]

        # Apply correlation boost
        combined_prob *= 1 + correlation_boost
        combined_prob = max(0.001, min(combined_prob, 0.90))

        # Calculate combined odds
        combined_decimal = 1.0
        for leg in legs:
            decimal = leg["odds"] / 100 + 1 if leg["odds"] > 0 else 100 / abs(leg["odds"]) + 1
            combined_decimal *= decimal

        # Convert to American odds
        if combined_decimal >= 2:
            combined_odds = int((combined_decimal - 1) * 100)
        else:
            combined_odds = int(-100 / (combined_decimal - 1))

        # Calculate metrics for $45 bet
        stake = 45.0
        payout = stake * combined_decimal
        roi = payout / stake

        expected_return = combined_prob * payout
        ev_percentage = (expected_return - stake) / stake

        # Confidence assessment
        if combined_prob >= 0.25 and ev_percentage >= 0.15:
            confidence = "HIGH"
        elif combined_prob >= 0.15 and ev_percentage >= 0.05:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        return {
            "game": game_desc,
            "time": game_time.strftime("%I:%M %p ET"),
            "strategy": strategy,
            "legs": legs,
            "num_legs": len(legs),
            "combined_odds": combined_odds,
            "win_probability": combined_prob,
            "expected_value_pct": ev_percentage,
            "payout": payout,
            "roi": roi,
            "correlation_boost": correlation_boost,
            "confidence": confidence,
            "stake": stake,
        }


def main():
    """Generate SGPs for 3 target NHL games: CHI@FLA, PIT@NYR, COL@LAK."""

    print("🏒 EQ12 NHL SGP BUILDER - 3 TARGET GAMES")
    print("=" * 60)
    print("Building SGPs for CHI@FLA (9:20PM), PIT@NYR (12:10AM), COL@LAK (2:50AM)")

    try:
        builder = EQ12NHLSGPBuilder()

        # Fetch the 3 target games
        print("\n🔄 Fetching 3 target NHL games...")
        nhl_games = builder.fetch_nhl_games_tonight()

        if not nhl_games:
            print("❌ No NHL games found for tonight")
            return

        print(f"Found {len(nhl_games)} NHL games")

        # Build SGPs for each game
        all_sgps = []

        for game in nhl_games:
            print(f"\n🏒 Building SGPs for {game['away_team']} @ {game['home_team']}...")
            game_sgps = builder.build_game_sgps(game)

            if game_sgps:
                all_sgps.extend(game_sgps)
                print(f"   Generated {len(game_sgps)} SGP strategies")
            else:
                print("   No viable SGPs found")

        if not all_sgps:
            print("❌ No viable SGPs found for tonight's NHL games")
            return

        # Sort by ROI and display results
        all_sgps.sort(key=lambda x: x["roi"], reverse=True)

        print("\n🏆 TOP NHL SGP RECOMMENDATIONS")
        print("=" * 60)

        for i, sgp in enumerate(all_sgps[:10], 1):  # Show top 10
            print(f"\n#{i}. {sgp['game']} - {sgp['time']}")
            print(f"    Strategy: {sgp['strategy']}")
            print(f"    Legs: {sgp['num_legs']} | Odds: {sgp['combined_odds']:+d}")
            print(f"    Win Prob: {sgp['win_probability']:.1%} | ROI: {sgp['roi']:.1f}x")
            print(f"    Payout: ${sgp['payout']:.0f} | EV: {sgp['expected_value_pct']:+.1%}")
            print(f"    Confidence: {sgp['confidence']}")

            print("    Picks:")
            for j, leg in enumerate(sgp["legs"], 1):
                print(f"      {j}. {leg['pick']} ({leg['odds']:+d})")

        # Highlight best SGPs that meet criteria
        qualifying_sgps = [
            sgp for sgp in all_sgps if sgp["roi"] >= 5 and sgp["expected_value_pct"] >= 0.5
        ]

        if qualifying_sgps:
            print("\n🎯 RECOMMENDED PLAYS (5x+ ROI, 50%+ EV)")
            print("=" * 50)

            for sgp in qualifying_sgps[:3]:  # Top 3 recommendations
                print(f"\n🏒 {sgp['game']} ({sgp['time']})")
                print(f"Strategy: {sgp['strategy']}")
                print(f"Stake: ${sgp['stake']:.0f}")
                print(f"Payout: ${sgp['payout']:.0f}")
                print(f"ROI: {sgp['roi']:.1f}x")
                print(f"Win Probability: {sgp['win_probability']:.1%}")
                print(f"Expected Value: {sgp['expected_value_pct']:+.1%}")

                print("Legs:")
                for leg in sgp["legs"]:
                    print(f"  • {leg['pick']} ({leg['odds']:+d})")
        else:
            print("\n⚠️ No SGPs meet the 5x ROI + 50% EV criteria tonight")
            print("Top SGP recommendations shown above")

        # Save results
        logs_dir = Path("C:/EQ12/logs")
        logs_dir.mkdir(exist_ok=True)

        results = {
            "timestamp": datetime.now().isoformat(),
            "nhl_games_analyzed": len(nhl_games),
            "total_sgps_generated": len(all_sgps),
            "all_sgps": all_sgps,
            "top_recommendations": qualifying_sgps[:5] if qualifying_sgps else all_sgps[:5],
        }

        results_file = logs_dir / f"nhl_sgps_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n💾 NHL SGP analysis saved: {results_file}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
