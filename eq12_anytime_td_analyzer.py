#!/usr/bin/env python3
"""
EQ12 Ultimate NFL Anytime TD Scorer Analyzer
Advanced touchdown scorer parlay generator with time filtering and comprehensive analysis.
"""

import argparse
import json
import logging
import os
from datetime import UTC, datetime

import requests


class UltimateAnytimeTDAnalyzer:
    def __init__(self, api_key: str | None = None, bankroll: float = 1000.0):
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        self.bankroll = bankroll
        self.logger = self._setup_logging()

        if not self.api_key:
            self.logger.error("❌ No API key provided. Set ODDS_API_KEY environment variable.")
            raise ValueError("API key required")

        self.logger.info("Ultimate NFL Anytime TD Analyzer initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def fetch_player_props(self) -> list[dict]:
        """Fetch NFL player props focusing on TD scorers"""
        try:
            url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
            params = {
                "apiKey": self.api_key,
                "regions": "us",
                "markets": "player_touchdowns_anytime,player_touchdowns_first,player_touchdowns_last",
                "oddsFormat": "american",
                "dateFormat": "iso",
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            games = response.json()

            self.logger.info(f"Fetched {len(games)} NFL games with TD props")
            return games

        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch TD props: {e}")
            return []

    def extract_td_opportunities(self, games: list[dict]) -> dict[str, list[dict]]:
        """Extract and categorize TD scorer opportunities"""
        opportunities = {"anytime_td": [], "first_td": [], "last_td": []}

        for game in games:
            home_team = game.get("home_team", "Unknown")
            away_team = game.get("away_team", "Unknown")
            game_time = game.get("commence_time", "Unknown")
            game_id = f"{away_team}_vs_{home_team}"

            # Format game time for display
            formatted_time = self._format_game_time(game_time)

            # Log game info
            if "live" in game.get("id", "").lower():
                self.logger.info(f"LIVE: {away_team} @ {home_team}")
            else:
                self.logger.info(f"UPCOMING: {away_team} @ {home_team} at {formatted_time}")

            for bookmaker in game.get("bookmakers", []):
                book_name = bookmaker.get("title", "Unknown")

                for market in bookmaker.get("markets", []):
                    market_key = market.get("key", "")

                    if market_key == "player_touchdowns_anytime":
                        self._process_td_market(
                            market,
                            opportunities["anytime_td"],
                            game_id,
                            game_time,
                            formatted_time,
                            book_name,
                            "Anytime TD",
                        )
                    elif market_key == "player_touchdowns_first":
                        self._process_td_market(
                            market,
                            opportunities["first_td"],
                            game_id,
                            game_time,
                            formatted_time,
                            book_name,
                            "First TD",
                        )
                    elif market_key == "player_touchdowns_last":
                        self._process_td_market(
                            market,
                            opportunities["last_td"],
                            game_id,
                            game_time,
                            formatted_time,
                            book_name,
                            "Last TD",
                        )

        return opportunities

    def _process_td_market(
        self,
        market: dict,
        opportunities: list[dict],
        game_id: str,
        game_time: str,
        formatted_time: str,
        book_name: str,
        market_type: str,
    ):
        """Process individual TD market and extract opportunities"""
        for outcome in market.get("outcomes", []):
            player_name = outcome.get("name", "Unknown Player")
            odds = outcome.get("price")

            if odds and odds > 0:  # Only positive odds for TD props
                # Calculate model probability and EV
                model_prob = self._estimate_td_probability(player_name, market_type)
                implied_prob = self._calculate_implied_probability(odds)
                expected_value = ((model_prob - implied_prob) / implied_prob) * 100

                # Only include opportunities with positive EV
                if expected_value > 0:
                    opportunity = {
                        "player": player_name,
                        "market": market_type,
                        "selection": f"{player_name} - {market_type}",
                        "odds": f"+{odds}",
                        "decimal_odds": odds,
                        "sportsbook": book_name,
                        "game_id": game_id,
                        "game_time": game_time,
                        "formatted_time": formatted_time,
                        "model_probability": model_prob,
                        "implied_probability": implied_prob,
                        "expected_value": expected_value,
                        "teams": game_id.replace("_vs_", " @ "),
                    }
                    opportunities.append(opportunity)

    def _estimate_td_probability(self, player_name: str, market_type: str) -> float:
        """Estimate TD probability based on player and market type"""
        # Simplified model - in production, this would use advanced analytics
        base_prob = {
            "Anytime TD": 0.35,  # RB/WR baseline
            "First TD": 0.08,  # Lower probability for first TD
            "Last TD": 0.08,  # Lower probability for last TD
        }

        # Adjust based on player position heuristics
        if any(keyword in player_name.lower() for keyword in ["rb", "running", "cook", "henry"]):
            multiplier = 1.3  # RBs more likely
        elif any(keyword in player_name.lower() for keyword in ["wr", "wide", "receiver"]):
            multiplier = 1.1  # WRs solid chance
        elif any(keyword in player_name.lower() for keyword in ["te", "tight"]):
            multiplier = 0.9  # TEs slightly lower
        else:
            multiplier = 1.0

        return min(base_prob.get(market_type, 0.25) * multiplier, 0.85)

    def _calculate_implied_probability(self, american_odds: int) -> float:
        """Calculate implied probability from American odds"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        return abs(american_odds) / (abs(american_odds) + 100)

    def _format_game_time(self, iso_time: str) -> str:
        """Format ISO timestamp to readable time"""
        if iso_time == "Unknown":
            return "Unknown"
        try:
            dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
            local_dt = dt.replace(tzinfo=UTC).astimezone()
            return local_dt.strftime("%m/%d %I:%M %p")
        except:
            return iso_time

    def is_after_405pm(self, game_time: str) -> bool:
        """Check if game starts after 4:05 PM"""
        if not game_time or game_time == "Unknown":
            return False
        try:
            # Parse times like "10/05 04:26 PM"
            if "PM" in game_time:
                # Extract just the time part
                if " " in game_time:
                    parts = game_time.split()
                    # Find the time part (contains colon)
                    time_part = None
                    for part in parts:
                        if ":" in part:
                            time_part = part
                            break

                    if not time_part:
                        return False
                else:
                    time_part = game_time.replace(" PM", "")

                hours, minutes = map(int, time_part.split(":"))

                # For PM times, 12:00-12:59 PM stays as 12, others get +12
                if hours == 12:
                    # 12 PM = noon, so 12:05 PM is still before 4:05 PM
                    return False
                # Convert 1-11 PM to 13-23 in 24-hour format
                hours += 12

                # Check if after 4:05 PM (16:05 in 24-hour)
                result = hours > 16 or (hours == 16 and minutes > 5)
                return result
            return False
        except Exception as e:
            self.logger.warning(f"Time parse error for '{game_time}': {e}")
            return False

    def remove_duplicates(self, opportunities: list[dict]) -> list[dict]:
        """Remove duplicate TD opportunities, keeping highest EV"""
        seen = {}
        duplicates_removed = 0

        for opp in opportunities:
            # Create unique key for player + market + game
            key = f"{opp['player']}|{opp['market']}|{opp['game_id']}"

            if key in seen:
                duplicates_removed += 1
                # Keep the one with higher EV
                if opp["expected_value"] > seen[key]["expected_value"]:
                    self.logger.info(
                        f"Duplicate #{duplicates_removed}: Replaced {opp['player']} "
                        f"({seen[key]['expected_value']:.1f}% EV) with higher EV version "
                        f"({opp['expected_value']:.1f}% EV)"
                    )
                    seen[key] = opp
                else:
                    self.logger.info(
                        f"Duplicate #{duplicates_removed}: Kept existing {opp['player']} "
                        f"({seen[key]['expected_value']:.1f}% EV) over duplicate "
                        f"({opp['expected_value']:.1f}% EV)"
                    )
            else:
                seen[key] = opp

        if duplicates_removed > 0:
            self.logger.info(f"Removed {duplicates_removed} total duplicates")

        return list(seen.values())

    def build_td_parlays(self, opportunities: dict[str, list[dict]]) -> list[dict]:
        """Build comprehensive TD scorer parlays"""
        parlays = []

        # Remove duplicates from each market
        deduped_ops = {}
        for market, ops in opportunities.items():
            deduped_ops[market] = self.remove_duplicates(ops)

        # Filter for late games (after 4:05 PM)
        late_games_anytime = []
        late_games_first = []
        late_games_last = []

        self.logger.info("Checking for late games (after 4:05 PM)...")

        for op in deduped_ops["anytime_td"]:
            if self.is_after_405pm(op.get("formatted_time", "")):
                late_games_anytime.append(op)
                self.logger.info(f"Late Anytime TD: {op['player']} at {op['formatted_time']}")

        for op in deduped_ops["first_td"]:
            if self.is_after_405pm(op.get("formatted_time", "")):
                late_games_first.append(op)

        for op in deduped_ops["last_td"]:
            if self.is_after_405pm(op.get("formatted_time", "")):
                late_games_last.append(op)

        self.logger.info(
            f"Found {len(late_games_anytime)} Anytime + {len(late_games_first)} First + {len(late_games_last)} Last TD for late games"
        )

        # Strategy 1: Late Games TD Special
        if late_games_anytime:
            late_mixed = late_games_anytime[:6] + late_games_first[:2] + late_games_last[:2]
            if late_mixed:
                parlay = self._create_parlay(
                    legs=late_mixed[:8],  # Max 8 legs for TD parlays
                    strategy_name="Late Games TD Special",
                    description="Anytime + First + Last TD for games after 4:05 PM",
                    stake_percentage=0.08,  # 8% of bankroll
                    risk_level="HIGH",
                )
                if parlay:
                    parlays.append(parlay)

        # Strategy 2: Conservative Anytime TD
        all_anytime = sorted(
            deduped_ops["anytime_td"], key=lambda x: x["expected_value"], reverse=True
        )
        high_ev_anytime = [op for op in all_anytime if op["expected_value"] >= 15.0]

        if len(high_ev_anytime) >= 4:
            parlay = self._create_parlay(
                legs=high_ev_anytime[:6],
                strategy_name="Conservative Anytime TD",
                description="High-confidence anytime TD scorers (15%+ EV)",
                stake_percentage=0.12,  # 12% of bankroll
                risk_level="MEDIUM",
            )
            if parlay:
                parlays.append(parlay)

        # Strategy 3: Premium Multi-Market TD
        combined_high_ev = []
        for market, ops in deduped_ops.items():
            market_high_ev = [op for op in ops if op["expected_value"] >= 10.0]
            combined_high_ev.extend(market_high_ev)

        # Sort by EV and remove conflicts (same player different markets)
        combined_high_ev = sorted(combined_high_ev, key=lambda x: x["expected_value"], reverse=True)
        combined_filtered = self._remove_player_conflicts(combined_high_ev)

        if len(combined_filtered) >= 5:
            parlay = self._create_parlay(
                legs=combined_filtered[:8],
                strategy_name="Premium Multi-Market TD",
                description="Mix of Anytime + First + Last TD (No player conflicts)",
                stake_percentage=0.15,  # 15% of bankroll
                risk_level="HIGH",
            )
            if parlay:
                parlays.append(parlay)

        return parlays

    def _remove_player_conflicts(self, opportunities: list[dict]) -> list[dict]:
        """Remove conflicts where same player has multiple TD market bets"""
        seen_players = set()
        filtered = []
        conflicts_removed = 0

        for op in opportunities:
            player = op["player"]
            if player not in seen_players:
                seen_players.add(player)
                filtered.append(op)
            else:
                conflicts_removed += 1
                self.logger.info(
                    f"Player conflict: Removed {player} {op['market']} "
                    f"({op['expected_value']:.1f}% EV) - already have this player"
                )

        if conflicts_removed > 0:
            self.logger.info(f"Removed {conflicts_removed} player conflicts")

        return filtered

    def _create_parlay(
        self,
        legs: list[dict],
        strategy_name: str,
        description: str,
        stake_percentage: float,
        risk_level: str,
    ) -> dict:
        """Create a parlay from selected legs"""
        if not legs:
            return None

        # Calculate combined odds
        combined_odds = 1.0
        for leg in legs:
            decimal_odds = (leg["decimal_odds"] / 100) + 1
            combined_odds *= decimal_odds

        # Calculate stake and payout
        stake = self.bankroll * stake_percentage
        payout = stake * combined_odds
        american_odds = int((combined_odds - 1) * 100) if combined_odds >= 2 else -100

        return {
            "strategy": strategy_name,
            "description": description,
            "legs": legs,
            "num_legs": len(legs),
            "stake": stake,
            "combined_odds": combined_odds,
            "american_odds": american_odds,
            "payout": payout,
            "profit": payout - stake,
            "risk_level": risk_level,
            "mix": self._get_market_mix(legs),
        }

    def _get_market_mix(self, legs: list[dict]) -> str:
        """Get mix description of markets in parlay"""
        anytime_count = sum(1 for leg in legs if leg["market"] == "Anytime TD")
        first_count = sum(1 for leg in legs if leg["market"] == "First TD")
        last_count = sum(1 for leg in legs if leg["market"] == "Last TD")

        return f"{anytime_count} Anytime + {first_count} First + {last_count} Last TD"

    def format_output(self, opportunities: dict[str, list[dict]], parlays: list[dict]) -> str:
        """Format comprehensive analysis output"""

        total_opportunities = sum(len(ops) for ops in opportunities.values())

        output = []
        output.append("🏈 ULTIMATE NFL ANYTIME TD SCORER ANALYZER 🏈")
        output.append(f"⏰ Generated: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
        output.append(f"💰 Bankroll: ${self.bankroll:,.2f}")
        output.append("🎯 Analysis: ANYTIME + FIRST + LAST TD SCORERS")
        output.append("=" * 60)
        output.append("")

        # Opportunities summary
        output.append("💰 TD OPPORTUNITIES FOUND:")
        output.append(f"🎯 Anytime TD: {len(opportunities.get('anytime_td', []))} picks")
        output.append(f"🥇 First TD: {len(opportunities.get('first_td', []))} picks")
        output.append(f"🏁 Last TD: {len(opportunities.get('last_td', []))} picks")
        output.append(f"📊 Total: {total_opportunities} opportunities")
        output.append(f"📋 TD Parlays: {len(parlays)}")
        output.append("")
        output.append("=" * 60)
        output.append("")

        # Display each parlay
        for i, parlay in enumerate(parlays, 1):
            output.append(f"🎯 TD PARLAY #{i}: {parlay['strategy']}")
            output.append(f"📖 {parlay['description']}")
            output.append(f"🎪 Mix: {parlay['mix']} | TD Action")
            output.append(
                f"📊 Legs: {parlay['num_legs']} | Odds: +{parlay['american_odds']} | "
                f"Stake: ${parlay['stake']:.0f} | Risk: {parlay['risk_level']}"
            )
            output.append(f"💸 Payout: ${parlay['payout']:,.2f} | Net: +${parlay['profit']:,.2f}")
            output.append("-" * 40)

            for j, leg in enumerate(parlay["legs"], 1):
                output.append(f"   {j}. {leg['player']} - {leg['market']}")
                output.append(
                    f"      📈 {leg['odds']} | EV: +{leg['expected_value']:.1f}% | "
                    f"{self._get_ev_badge(leg['expected_value'])}"
                )
                output.append(f"      🕐 {leg['formatted_time']} | 📱 {leg['sportsbook']}")
                output.append(f"      🏟️ {leg['teams']}")
                output.append("")

        # TD Scorer advantages
        output.append("🎪 TD PARLAY ADVANTAGES:")
        output.append("✅ Player prop specialization")
        output.append("✅ Multiple TD market coverage")
        output.append("✅ Late game filtering available")
        output.append("✅ Player conflict prevention")
        output.append("✅ Elite value combinations")
        output.append("")

        # Legend
        output.append("📊 VALUE LEGEND:")
        output.append("🟢 ELITE = 15%+ EV  |  🟢 STRONG = 8%+ EV  |  🟡 SOLID = 4%+ EV")
        output.append("🟠 FAIR = 1%+ EV  |  🔴 AVOID = <1% EV")
        output.append("")
        output.append("🚀 Ready to place these TD SCORER parlays? LFG! 🚀")
        output.append("")
        output.append("")
        output.append(f"✅ Generated {len(parlays)} ultimate TD scorer parlay strategies")

        return "\n".join(output)

    def _get_ev_badge(self, ev: float) -> str:
        """Get EV quality badge"""
        if ev >= 15:
            return "🟢 ELITE"
        if ev >= 8:
            return "🟢 STRONG"
        if ev >= 4:
            return "🟡 SOLID"
        if ev >= 1:
            return "🟠 FAIR"
        return "🔴 AVOID"

    def save_results(self, opportunities: dict[str, list[dict]], parlays: list[dict]) -> str:
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:/EQ12/logs/nfl_td_scorer_{timestamp}.json"

        results = {
            "timestamp": datetime.now().isoformat(),
            "bankroll": self.bankroll,
            "opportunities": opportunities,
            "parlays": parlays,
            "summary": {
                "total_opportunities": sum(len(ops) for ops in opportunities.values()),
                "total_parlays": len(parlays),
                "anytime_td_count": len(opportunities.get("anytime_td", [])),
                "first_td_count": len(opportunities.get("first_td", [])),
                "last_td_count": len(opportunities.get("last_td", [])),
            },
        }

        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                json.dump(results, f, indent=2)
            return filename
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
            return ""

    def analyze(self) -> str:
        """Run complete TD scorer analysis"""
        self.logger.info("Starting Ultimate NFL Anytime TD Scorer Analysis")

        # Fetch player props
        games = self.fetch_player_props()
        if not games:
            return "❌ No TD scorer data available"

        # Extract opportunities
        opportunities = self.extract_td_opportunities(games)
        total_ops = sum(len(ops) for ops in opportunities.values())

        if total_ops == 0:
            return "❌ No TD scoring opportunities found"

        self.logger.info(
            f"Found {opportunities.get('anytime_td', [])} Anytime + "
            f"{len(opportunities.get('first_td', []))} First + "
            f"{len(opportunities.get('last_td', []))} Last TD opportunities"
        )

        # Build parlays
        parlays = self.build_td_parlays(opportunities)

        # Format output
        output = self.format_output(opportunities, parlays)

        # Save results
        results_file = self.save_results(opportunities, parlays)
        if results_file:
            output += f"\n📁 Results: {results_file}"

        return output


def main():
    parser = argparse.ArgumentParser(description="Ultimate NFL Anytime TD Scorer Analyzer")
    parser.add_argument(
        "--bankroll", type=float, default=1000.0, help="Bankroll amount (default: 1000)"
    )
    parser.add_argument(
        "--api-key", type=str, help="The Odds API key (or set ODDS_API_KEY env var)"
    )

    args = parser.parse_args()

    try:
        analyzer = UltimateAnytimeTDAnalyzer(api_key=args.api_key, bankroll=args.bankroll)

        result = analyzer.analyze()
        print(result)

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
