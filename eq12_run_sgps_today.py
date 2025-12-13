#!/usr/bin/env python3
"""
EQ12 SGP Orchestrator - Daily Same Game Parlay Builder
Builds high-confidence SGPs for today's games across multiple sports.
ASCII only logging to avoid Windows cp1252 encoding errors.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Import real odds ingestor - NO MOCK DATA
from eq12_odds_ingestor import OddsIngestor

# Import EQ12 components
from eq12_sgp_builder import SGP, SGPBuilder, setup_logging
from eq12_time import now_utc, parse_ts

try:
    from eq12_cost_guards import get_cost_guards
except ImportError:

    def get_cost_guards() -> dict:
        """Fallback cost guards"""
        return {"api_calls_remaining": 1000, "budget_ok": True}


class SGPOrchestrator:
    """Orchestrates daily SGP generation across multiple sports"""

    def __init__(self, args):
        self.args = args
        self.logger = logging.getLogger(__name__)
        self.sgp_builder = SGPBuilder(
            min_odds=args.min_odds, stake_range=(args.stake_min, args.stake_max)
        )
        self.odds_ingestor = OddsIngestor()

        # Target games (force include these matchups)
        self.target_matchups = [("Missouri State", "Middle Tennessee"), ("Liberty", "UTEP")]

        # Sports configuration
        self.sports_config = {
            "baseball_mlb": {"title": "MLB", "enabled": True},
            "icehockey_nhl": {"title": "NHL", "enabled": True},
            "basketball_nba": {"title": "NBA", "enabled": True},
            "americanfootball_ncaaf": {"title": "NCAAF", "enabled": True},
        }

    def run(self) -> None:
        """Main orchestration logic"""
        try:
            self.logger.info("Starting EQ12 SGP generation for today's games")

            # Check cost guards
            cost_guards = get_cost_guards()
            if hasattr(cost_guards, "budget_ok"):
                if not cost_guards.budget_ok:
                    self.logger.error("Cost guards failed - budget exceeded")
                    return
            elif isinstance(cost_guards, dict):
                if not cost_guards.get("budget_ok", False):
                    self.logger.error("Cost guards failed - budget exceeded")
                    return

            # Determine date range for today
            local_date = self._parse_date(self.args.date)
            date_range = self._get_utc_window(local_date)

            self.logger.info(f"Processing games for {local_date.strftime('%Y-%m-%d')}")

            # Process each sport
            all_sgps = []
            stacked_slips = []

            for sport_key, config in self.sports_config.items():
                if not config["enabled"]:
                    continue

                try:
                    sport_sgps = self._process_sport(sport_key, config, date_range)
                    all_sgps.extend(sport_sgps)

                except Exception as e:
                    self.logger.error(f"Error processing {sport_key}: {e!s}")

            # Generate stacked day slips if needed
            if len(all_sgps) > 1:
                stacked_slips = self._generate_stacked_slips(all_sgps)

            # Save results
            self._save_results(all_sgps, stacked_slips, local_date)

            # Send notifications if configured
            self._send_notifications(all_sgps, stacked_slips)

            self.logger.info(
                f"SGP generation complete. Found {len(all_sgps)} SGPs "
                f"and {len(stacked_slips)} stacked slips"
            )

        except Exception as e:
            self.logger.error(f"Critical error in SGP orchestration: {e!s}")
            raise

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string or use today"""
        if date_str:
            try:
                # Parse as UTC
                return parse_ts(date_str + "T00:00:00Z")
            except Exception:
                self.logger.warning(f"Invalid date format: {date_str}, using today")
        return now_utc()

    def _get_utc_window(self, local_date: datetime) -> tuple:
        """Get UTC window for local date"""
        start = local_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return (start, end)

    def _process_sport(self, sport_key: str, config: dict, date_range: tuple) -> list[SGP]:
        """Process SGPs for a single sport"""
        sport_sgps = []

        try:
            self.logger.info(f"Processing {config['title']} games")

            # Fetch games for sport using real API
            odds_result = self.odds_ingestor.ingest_live_odds(
                sport=sport_key, markets=["h2h", "spreads", "totals"], force_refresh=True
            )

            # Extract games list from API response
            games = []
            if isinstance(odds_result, dict):
                if "games" in odds_result:
                    games = odds_result["games"]
                    self.logger.info(f"Extracted {len(games)} games from API response")
                elif "error" in odds_result:
                    self.logger.error(f"API error for {sport_key}: {odds_result.get('error')}")
                    games = []
                else:
                    # Debug: show what keys are available
                    available_keys = list(odds_result.keys())
                    self.logger.warning(
                        f"Unexpected API response format for {sport_key}. Available keys: {available_keys}"
                    )

                    # Try common alternative keys
                    if "processed_games" in odds_result:
                        games = odds_result["processed_games"]
                    elif "data" in odds_result:
                        games = odds_result["data"]
                    else:
                        games = []

            # Filter to today's games + force include targets
            todays_games = self._filter_todays_games(games, date_range)
            target_games = self._find_target_games(games, sport_key)

            all_games = todays_games + target_games

            if not all_games:
                self.logger.info(f"No games found for {config['title']}")
                return sport_sgps

            self.logger.info(f"Found {len(all_games)} games for {config['title']}")

            # Generate SGPs for each game
            for i, game in enumerate(all_games):
                try:
                    # Debug: log game structure
                    self.logger.debug(
                        f"Processing game {i}: type={type(game)}, content={str(game)[:100]}"
                    )

                    # Skip if game is not a dict
                    if not isinstance(game, dict):
                        self.logger.warning(f"Skipping game {i}: expected dict, got {type(game)}")
                        continue

                    game_sgps = self._process_game(game, config)
                    sport_sgps.extend(game_sgps)

                except Exception as e:
                    self.logger.error(f"Error processing game {i}: {e!s}")

            if not sport_sgps:
                self.logger.info(f"No safe {self.args.min_odds}x SGPs found for {config['title']}")

        except Exception as e:
            self.logger.error(f"Error in sport processing for {sport_key}: {e!s}")

        return sport_sgps

    def _filter_todays_games(self, games: list[dict], date_range: tuple) -> list[dict]:
        """Filter games to today's date range"""
        filtered_games = []
        start_time, end_time = date_range

        for game in games:
            try:
                commence_time = parse_ts(game.get("commence_time", ""))
                if start_time <= commence_time < end_time:
                    filtered_games.append(game)
            except Exception:
                self.logger.warning(f"Invalid game time format: {game.get('commence_time')}")
        return filtered_games

    def _find_target_games(self, games: list[dict], sport_key: str) -> list[dict]:
        """Find target matchups (force include)"""
        if sport_key != "americanfootball_ncaaf":
            return []

        target_games = []

        for game in games:
            home_team = game.get("home_team", "").lower()
            away_team = game.get("away_team", "").lower()

            for target_home, target_away in self.target_matchups:
                if self._team_match(home_team, target_home.lower()) and self._team_match(
                    away_team, target_away.lower()
                ):
                    target_games.append(game)
                    self.logger.info(
                        f"Found target game: {game.get('home_team')} vs {game.get('away_team')}"
                    )

        return target_games

    def _team_match(self, team_name: str, target_name: str) -> bool:
        """Fuzzy match team names"""
        # Simple token matching - could use fuzzywuzzy for better matching
        team_tokens = set(team_name.split())
        target_tokens = set(target_name.split())

        # Check if significant overlap
        intersection = team_tokens.intersection(target_tokens)
        return len(intersection) >= max(1, min(len(team_tokens), len(target_tokens)) // 2)

    def _process_game(self, game: dict, config: dict) -> list[SGP]:
        """Process SGPs for a single game"""
        try:
            # Build market book from bookmakers
            market_book = self._build_market_book(game)

            if not market_book:
                return []

            # Generate SGP candidates
            candidates = self.sgp_builder.build_sgp_candidates(game, market_book)

            if not candidates:
                return []

            # Select best SGP
            best_sgp = self.sgp_builder.select_best_sgp(candidates, self.args.min_odds)

            if best_sgp:
                return [best_sgp]

        except Exception as e:
            self.logger.error(f"Error processing game: {e!s}")

        return []

    def _build_market_book(self, game: dict) -> dict:
        """Build market book with best available prices"""
        market_book = {}

        bookmakers = game.get("bookmakers", [])
        if not bookmakers:
            return market_book

        # Aggregate markets across bookmakers
        for bookmaker in bookmakers:
            book_name = bookmaker.get("key", "unknown")
            markets = bookmaker.get("markets", [])

            for market in markets:
                market_key = market.get("key")
                if not market_key:
                    continue

                if market_key not in market_book:
                    market_book[market_key] = {
                        "bookmaker": book_name,
                        "outcomes": market.get("outcomes", []),
                    }
                else:
                    # Could implement best price logic here
                    # For now, just use first available
                    pass

        return market_book

    def _generate_stacked_slips(self, sgps: list[SGP]) -> list[dict]:
        """Generate stacked day slips from multiple SGPs"""
        stacked_slips = []

        if len(sgps) < 2:
            return stacked_slips

        try:
            # Sort SGPs by EV and select top ones with low correlation
            sorted_sgps = sorted(sgps, key=lambda x: x.ev_pct, reverse=True)

            # Simple stacking - take top 2-4 SGPs
            for combo_size in range(2, min(5, len(sorted_sgps) + 1)):
                combo_sgps = sorted_sgps[:combo_size]

                # Calculate combined odds
                combined_odds = 1.0
                for sgp in combo_sgps:
                    combined_odds *= sgp.decimal_odds

                # Check if meets payout requirements
                for stake in [
                    self.args.stake_min,
                    (self.args.stake_min + self.args.stake_max) / 2,
                    self.args.stake_max,
                ]:
                    potential_payout = stake * combined_odds

                    if potential_payout >= self.args.payout_min:
                        stacked_slip = {
                            "type": "stacked_day",
                            "sgps": [sgp.to_dict() for sgp in combo_sgps],
                            "combined_odds": combined_odds,
                            "stake": stake,
                            "potential_payout": potential_payout,
                            "notes": "books may not allow SGP x SGP, treat as conceptual or multi-book",
                        }
                        stacked_slips.append(stacked_slip)
                        break

        except Exception as e:
            self.logger.error(f"Error generating stacked slips: {e!s}")

        return stacked_slips

    def _save_results(self, sgps: list[SGP], stacked_slips: list[dict], date: datetime) -> None:
        """Save results to files"""
        date_str = date.strftime("%Y%m%d")

        # Ensure logs directory exists
        Path("logs").mkdir(exist_ok=True)

        try:
            # JSON output (full detail)
            json_data = {
                "date": date_str,
                "generated_at": now_utc().isoformat(),
                "sgps": [sgp.to_dict() for sgp in sgps],
                "stacked_slips": stacked_slips,
                "summary": {
                    "total_sgps": len(sgps),
                    "total_stacked": len(stacked_slips),
                    "leagues": list({sgp.league for sgp in sgps}),
                },
            }

            json_path = Path(f"logs/sgp_{date_str}.json")
            with json_path.open("w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            # Text output (human readable)
            txt_path = Path(f"logs/sgp_{date_str}.txt")
            with txt_path.open("w", encoding="utf-8") as f:
                f.write(f"EQ12 SGPs for {date_str}\n")
                f.write("=" * 60 + "\n\n")
                for idx, sgp in enumerate(sgps, 1):
                    f.write(f"{idx}. {sgp.title} [{sgp.decimal_odds:.2f}x]\n")
                    for leg in sgp.legs:
                        f.write(f"   - {leg.market}: {leg.selection} @ {leg.price}\n")
                    f.write(f"   EV: {sgp.ev_pct * 100:.1f}% | Risk: {sgp.risk_score}\n")
                    f.write("\n")

            self.logger.info(f"Saved SGP results to {json_path} and {txt_path}")
        except Exception as e:
            self.logger.error(f"Failed to save results: {e!s}")

    def _send_notifications(self, sgps: list[SGP], stacked_slips: list[dict]) -> None:
        """Send Telegram notifications if configured"""
        try:
            telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
            telegram_chat = os.getenv("TELEGRAM_CHAT_ID")

            if not (telegram_token and telegram_chat):
                self.logger.info("Telegram not configured - skipping notifications")
                return

            # Prepare message (ASCII only)
            message_lines = [
                f"EQ12 SGP Report - {datetime.now().strftime('%Y-%m-%d')}",
                f"Found {len(sgps)} SGPs, {len(stacked_slips)} stacked slips",
                "",
            ]

            # Top 5 SGPs by EV
            if sgps:
                message_lines.append("TOP SGPs:")
                sorted_sgps = sorted(sgps, key=lambda x: x.ev_pct, reverse=True)[:5]

                for i, sgp in enumerate(sorted_sgps, 1):
                    message_lines.append(
                        f"{i}. {sgp.game} - {sgp.decimal_odds:.1f}x "
                        f"(EV: {sgp.ev_pct * 100:.1f}%, Risk: {sgp.risk_score})"
                    )

            message = "\n".join(message_lines)

            # Send via telegram (would need actual implementation)
            self.logger.info("Would send Telegram notification (not implemented in fallback)")
            self.logger.info(f"Message: {message}")

        except Exception as e:
            self.logger.error(f"Error sending notifications: {e!s}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="EQ12 Daily SGP Generator")
    parser.add_argument("--date", help="Date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--stake-min", type=float, default=8.0, help="Minimum stake")
    parser.add_argument("--stake-max", type=float, default=20.0, help="Maximum stake")
    parser.add_argument("--min-odds", type=float, default=10.0, help="Minimum odds for SGPs")
    parser.add_argument(
        "--payout-min", type=float, default=1000.0, help="Minimum payout for stacked slips"
    )

    args = parser.parse_args()

    # Setup ASCII-only logging
    setup_logging()

    try:
        orchestrator = SGPOrchestrator(args)
        orchestrator.run()

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Fatal error: {e!s}")
        sys.exit(1)


if __name__ == "__main__":
    main()
