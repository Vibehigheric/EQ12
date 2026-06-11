#!/usr/bin/env python3
"""
EQ12 Ultimate NFL Mixed Parlay Analyzer
Combines Moneyline + Spread + Over/Under for maximum value parlays
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import UTC, datetime

import requests


class EQ12UltimateMixedAnalyzer:
    def __init__(self):
        self.api_key = "ODDS_API_KEY_PLACEHOLDER"
        self.bankroll = 1000.0

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Ultimate NFL Mixed Parlay Analyzer initialized")

    def get_comprehensive_nfl_data(self) -> dict:
        """Fetch NFL odds for ML + Spreads + Totals"""
        try:
            url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
            params = {
                "apiKey": self.api_key,
                "regions": "us",
                "markets": "h2h,spreads,totals",  # All three markets
                "oddsFormat": "american",
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            games = response.json()

            self.logger.info(f"Fetched {len(games)} NFL games with ML+Spreads+Totals")
            return {"success": True, "games": games}

        except Exception as e:
            self.logger.error(f"Failed to fetch NFL data: {e}")
            return {"success": False, "error": str(e)}

    def analyze_game_status(self, games: list) -> dict:
        """Determine which games are live, upcoming, or finished"""
        current_time = datetime.now(UTC)

        live_games = []
        upcoming_games = []
        finished_games = []

        for game in games:
            try:
                game_time = datetime.fromisoformat(game["commence_time"].replace("Z", "+00:00"))
                local_time = game_time.astimezone()
                today = datetime.now().date()
                game_date = local_time.date()

                # Calculate elapsed time
                time_diff = current_time - game_time
                elapsed_hours = time_diff.total_seconds() / 3600

                game_info = {
                    **game,
                    "game_time_local": local_time.strftime("%m/%d %I:%M %p"),
                    "elapsed_hours": elapsed_hours,
                    "start_time_utc": game_time.isoformat(),
                }

                if game_time <= current_time:
                    if elapsed_hours < 4:  # NFL games ~3.5 hours
                        game_info["status"] = "LIVE"
                        live_games.append(game_info)
                        self.logger.info(
                            f"LIVE: {game['away_team']} @ {game['home_team']} ({elapsed_hours:.1f}h)"
                        )
                    else:
                        game_info["status"] = "FINISHED"
                        finished_games.append(game_info)
                elif game_date == today:
                    # Only include today's upcoming games
                    game_info["status"] = "UPCOMING"
                    upcoming_games.append(game_info)
                    self.logger.info(
                        f"UPCOMING: {game['away_team']} @ {game['home_team']} at {local_time.strftime('%I:%M %p')}"
                    )

            except Exception as e:
                self.logger.warning(f"Could not parse game: {e}")

        return {
            "live": live_games,
            "upcoming": upcoming_games,
            "finished": finished_games,
        }

    def extract_all_opportunities(self, games: list) -> dict:
        """Extract ML, Spread, and Totals opportunities"""
        ml_ops = []
        spread_ops = []
        totals_ops = []

        for game in games:
            try:
                for bookmaker in game.get("bookmakers", []):
                    for market in bookmaker.get("markets", []):
                        # Moneyline opportunities
                        if market["key"] == "h2h":
                            for outcome in market["outcomes"]:
                                team = outcome["name"]
                                odds = outcome["price"]

                                model_prob = self.calculate_ml_model_prob(
                                    team, game["home_team"], game["away_team"]
                                )
                                ev_percent = self.calculate_ev(odds, model_prob)

                                if ev_percent > 1:
                                    ml_ops.append(
                                        {
                                            "game_id": f"{game['away_team']}_at_{game['home_team']}",
                                            "teams": f"{game['away_team']} @ {game['home_team']}",
                                            "selection": team,
                                            "odds": odds,
                                            "sportsbook": bookmaker["title"],
                                            "expected_value": ev_percent,
                                            "status": game.get("status", "UNKNOWN"),
                                            "game_time": game.get("game_time_local", "Unknown"),
                                            "elapsed_hours": game.get("elapsed_hours", 0),
                                            "market": "Moneyline",
                                            "value_grade": self.grade_value(ev_percent),
                                        }
                                    )

                        # Spread opportunities
                        elif market["key"] == "spreads":
                            for outcome in market["outcomes"]:
                                team = outcome["name"]
                                spread = outcome["point"]
                                odds = outcome["price"]

                                is_hook = abs(spread) % 1 == 0.5
                                model_prob = 0.52 + (0.03 if is_hook else 0)
                                ev_percent = self.calculate_ev(odds, model_prob)

                                if ev_percent > 1:
                                    spread_ops.append(
                                        {
                                            "game_id": f"{game['away_team']}_at_{game['home_team']}",
                                            "teams": f"{game['away_team']} @ {game['home_team']}",
                                            "selection": f"{team} {spread:+}",
                                            "spread": spread,
                                            "odds": odds,
                                            "sportsbook": bookmaker["title"],
                                            "expected_value": ev_percent,
                                            "is_hook": is_hook,
                                            "status": game.get("status", "UNKNOWN"),
                                            "game_time": game.get("game_time_local", "Unknown"),
                                            "elapsed_hours": game.get("elapsed_hours", 0),
                                            "market": "Spread",
                                            "value_grade": self.grade_value(ev_percent),
                                        }
                                    )

                        # Totals opportunities
                        elif market["key"] == "totals":
                            for outcome in market["outcomes"]:
                                bet_type = outcome["name"]  # "Over" or "Under"
                                total = outcome["point"]
                                odds = outcome["price"]

                                model_prob = self.calculate_totals_model_prob(
                                    total,
                                    bet_type,
                                    game["home_team"],
                                    game["away_team"],
                                )
                                ev_percent = self.calculate_ev(odds, model_prob)

                                if ev_percent > 1:
                                    totals_ops.append(
                                        {
                                            "game_id": f"{game['away_team']}_at_{game['home_team']}",
                                            "teams": f"{game['away_team']} @ {game['home_team']}",
                                            "selection": f"{bet_type} {total}",
                                            "bet_type": bet_type,
                                            "total": total,
                                            "odds": odds,
                                            "sportsbook": bookmaker["title"],
                                            "expected_value": ev_percent,
                                            "status": game.get("status", "UNKNOWN"),
                                            "game_time": game.get("game_time_local", "Unknown"),
                                            "elapsed_hours": game.get("elapsed_hours", 0),
                                            "market": "Totals",
                                            "value_grade": self.grade_value(ev_percent),
                                            "total_category": self.categorize_total(total),
                                        }
                                    )

            except Exception as e:
                self.logger.warning(f"Error processing game: {e}")

        # Dedupe opportunities to prevent exact duplicates
        ml_ops_deduped = self.remove_duplicate_picks(ml_ops)
        spread_ops_deduped = self.remove_duplicate_picks(spread_ops)
        totals_ops_deduped = self.remove_duplicate_picks(totals_ops)

        # Sort all by EV
        ml_ops_deduped.sort(key=lambda x: x["expected_value"], reverse=True)
        spread_ops_deduped.sort(key=lambda x: x["expected_value"], reverse=True)
        totals_ops_deduped.sort(key=lambda x: x["expected_value"], reverse=True)

        self.logger.info(
            f"Found {len(ml_ops_deduped)} ML + {len(spread_ops_deduped)} Spread + {len(totals_ops_deduped)} Totals opportunities (after dedup)"
        )

        return {
            "moneyline": ml_ops_deduped,
            "spreads": spread_ops_deduped,
            "totals": totals_ops_deduped,
        }

    def calculate_ml_model_prob(self, team: str, home_team: str, away_team: str) -> float:
        """Calculate moneyline model probability"""
        is_home = team == home_team
        base_prob = 0.5

        # Home field advantage
        if is_home:
            base_prob += 0.07

        # Team strength (simplified)
        strong_teams = [
            "Kansas City Chiefs",
            "Buffalo Bills",
            "Baltimore Ravens",
            "Philadelphia Eagles",
            "Detroit Lions",
            "Dallas Cowboys",
        ]
        weak_teams = ["Carolina Panthers", "Arizona Cardinals", "New England Patriots"]

        if team in strong_teams:
            base_prob += 0.1
        elif team in weak_teams:
            base_prob -= 0.1

        return max(0.1, min(0.9, base_prob))

    def calculate_totals_model_prob(
        self, total: float, bet_type: str, home_team: str, away_team: str
    ) -> float:
        """Calculate totals model probability"""
        base_prob = 0.5

        # High-scoring teams
        high_offense = [
            "Buffalo Bills",
            "Miami Dolphins",
            "Dallas Cowboys",
            "Kansas City Chiefs",
        ]
        # Strong defenses
        strong_defense = [
            "Pittsburgh Steelers",
            "Baltimore Ravens",
            "New England Patriots",
        ]

        # Adjust based on teams
        offensive_factor = 0
        defensive_factor = 0

        if home_team in high_offense or away_team in high_offense:
            offensive_factor += 0.03
        if home_team in strong_defense or away_team in strong_defense:
            defensive_factor += 0.03

        # Adjust based on total range
        total_factor = (0.02 if bet_type == "Under" else -0.02) if total < 42 or total > 50 else 0

        # Apply adjustments
        if bet_type == "Over":
            base_prob += offensive_factor - defensive_factor + total_factor
        else:  # Under
            base_prob += defensive_factor - offensive_factor + total_factor

        return max(0.1, min(0.9, base_prob))

    def calculate_ev(self, odds: int, model_prob: float) -> float:
        """Calculate expected value percentage"""
        if odds > 0:
            ev = (model_prob * odds - (1 - model_prob) * 100) / 100
        else:
            ev = (model_prob * 100 - (1 - model_prob) * abs(odds)) / abs(odds)
        return ev * 100

    def categorize_total(self, total: float) -> str:
        """Categorize total into ranges"""
        if total < 42:
            return "LOW"
        if total <= 48:
            return "AVERAGE"
        return "HIGH"

    def grade_value(self, ev: float) -> str:
        """Grade expected value"""
        if ev >= 15:
            return "🟢 ELITE"
        if ev >= 8:
            return "🟢 STRONG"
        if ev >= 4:
            return "🟡 SOLID"
        return "🟠 FAIR"

    def is_after_405pm(self, game_time: str) -> bool:
        """Check if game starts after 4:05 PM"""
        if not game_time or game_time == "Unknown":
            return False
        try:
            # Parse times like "10/05 04:26 PM" or "04:26 PM"
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

    def extract_team_from_selection(self, selection: str, teams: str) -> str:
        """Extract team name from selection string"""
        # Parse teams string like "Houston Texans @ Baltimore Ravens"
        away_team, home_team = teams.split(" @ ")

        # For ML bets, selection is just the team name
        if selection in (away_team, home_team):
            return selection

        # For spread bets, selection is like "Ravens +6.5" or "Texans -3"
        # Extract team name from spread selection
        for team in [away_team, home_team]:
            if team.split()[-1] in selection:  # Match last word (team name)
                return team

        return selection  # Fallback

    def has_team_conflict(self, legs: list) -> bool:
        """Check if parlay has ML and Spread bets on same team"""
        ml_teams = set()
        spread_teams = set()

        for leg in legs:
            team = self.extract_team_from_selection(leg["selection"], leg["teams"])

            if leg["market"] == "Moneyline":
                ml_teams.add(team)
            elif leg["market"] == "Spread":
                spread_teams.add(team)

        # Check for conflicts
        conflicts = ml_teams.intersection(spread_teams)
        return len(conflicts) > 0

    def has_same_game_spread_conflict(self, legs: list) -> bool:
        """Check if parlay has spread bets on both teams in same game"""
        spread_games = {}

        for leg in legs:
            if leg["market"] == "Spread":
                game_id = leg["game_id"]
                team = self.extract_team_from_selection(leg["selection"], leg["teams"])

                if game_id not in spread_games:
                    spread_games[game_id] = set()
                spread_games[game_id].add(team)

        # Check if any game has both teams with spread bets
        return any(len(teams) > 1 for game_id, teams in spread_games.items())

    def remove_same_game_spread_conflicts(self, legs: list) -> list:
        """Remove conflicting spread bets on both teams in same game"""
        spread_games = {}
        non_spread_legs = []

        # Separate spread bets by game and collect non-spread legs
        for leg in legs:
            if leg["market"] == "Spread":
                game_id = leg["game_id"]
                if game_id not in spread_games:
                    spread_games[game_id] = []
                spread_games[game_id].append(leg)
            else:
                non_spread_legs.append(leg)

        # For each game, keep only the highest EV spread bet
        filtered_spreads = []
        for game_id, game_spreads in spread_games.items():
            if len(game_spreads) > 1:
                # Multiple spread bets in same game - keep highest EV
                best_spread = max(game_spreads, key=lambda x: x["expected_value"])
                filtered_spreads.append(best_spread)
                removed_spreads = [s for s in game_spreads if s != best_spread]
                for removed in removed_spreads:
                    team = self.extract_team_from_selection(removed["selection"], removed["teams"])
                    self.logger.info(
                        f"Same-game conflict: Removed {team} spread ({removed['expected_value']:.1f}% EV)"
                    )
            else:
                # Only one spread bet in this game
                filtered_spreads.extend(game_spreads)

        return non_spread_legs + filtered_spreads

    def remove_duplicate_picks(self, legs: list) -> list:
        """Remove exact duplicate picks using comprehensive key matching"""
        unique_picks = {}
        duplicate_count = 0

        for leg in legs:
            # Create comprehensive key for ALL markets including totals - use more specific key
            pick_key = f"{leg['market']}|{leg['selection']}|{leg['game_id']}|{leg.get('odds', 'N/A')}|{leg.get('sportsbook', 'N/A')}"

            # Also check for identical selections regardless of odds/book (catch same bets)
            selection_key = f"{leg['market']}|{leg['selection']}|{leg['game_id']}"

            # Check if we already have this exact pick or same selection
            existing_key = None
            for existing in unique_picks:
                if existing == pick_key or existing.startswith(selection_key + "|"):
                    existing_key = existing
                    break

            if existing_key is None:
                unique_picks[pick_key] = leg
            else:
                # Duplicate found - keep the one with higher EV
                existing_ev = unique_picks[existing_key]["expected_value"]
                current_ev = leg["expected_value"]
                duplicate_count += 1

                if current_ev > existing_ev:
                    self.logger.info(
                        f"Duplicate #{duplicate_count}: Replaced {leg['selection']} ({existing_ev:.1f}% EV) with higher EV version ({current_ev:.1f}% EV)"
                    )
                    del unique_picks[existing_key]  # Remove old version
                    unique_picks[pick_key] = leg  # Add new version
                else:
                    self.logger.info(
                        f"Duplicate #{duplicate_count}: Kept existing {leg['selection']} ({existing_ev:.1f}% EV) over duplicate ({current_ev:.1f}% EV)"
                    )

        if duplicate_count > 0:
            self.logger.info(f"Removed {duplicate_count} total duplicates")

        return list(unique_picks.values())

    def remove_team_conflicts(self, legs: list) -> list:
        """Remove conflicting ML/Spread bets for same teams, keeping higher EV"""
        # First, dedupe exact same selections
        unique_selections = {}
        for leg in legs:
            selection_key = f"{leg['selection']}_{leg['game_id']}"
            if (
                selection_key not in unique_selections
                or leg["expected_value"] > unique_selections[selection_key]["expected_value"]
            ):
                unique_selections[selection_key] = leg

        deduped_legs = list(unique_selections.values())

        # Then handle team conflicts between ML and Spread
        team_bets = {}

        # Group bets by team and market
        for leg in deduped_legs:
            team = self.extract_team_from_selection(leg["selection"], leg["teams"])

            if team not in team_bets:
                team_bets[team] = {}

            market = leg["market"]
            if (
                market not in team_bets[team]
                or leg["expected_value"] > team_bets[team][market]["expected_value"]
            ):
                team_bets[team][market] = leg

        # Build conflict-free legs
        conflict_free_legs = []

        for team, markets in team_bets.items():
            # If team has both ML and Spread, keep only the higher EV one
            if "Moneyline" in markets and "Spread" in markets:
                ml_ev = markets["Moneyline"]["expected_value"]
                spread_ev = markets["Spread"]["expected_value"]

                if ml_ev >= spread_ev:
                    conflict_free_legs.append(markets["Moneyline"])
                    self.logger.info(
                        f"Conflict: Kept {team} ML ({ml_ev:.1f}% EV) over Spread ({spread_ev:.1f}% EV)"
                    )
                else:
                    conflict_free_legs.append(markets["Spread"])
                    self.logger.info(
                        f"Conflict: Kept {team} Spread ({spread_ev:.1f}% EV) over ML ({ml_ev:.1f}% EV)"
                    )
            else:
                # No conflict, add all available markets
                for market_leg in markets.values():
                    conflict_free_legs.append(market_leg)

            # Always add totals (no conflict with ML/Spread)
            if "Totals" in markets:
                conflict_free_legs.append(markets["Totals"])

        return conflict_free_legs

    def dedupe_games_mixed(self, opportunities: dict) -> dict:
        """Dedupe to one pick per game across all markets"""
        seen_games = {}
        deduped = {"moneyline": [], "spreads": [], "totals": []}

        # Process all opportunities together to find best pick per game
        all_ops = []

        # Add market type to each opportunity
        for ml_op in opportunities["moneyline"]:
            all_ops.append({**ml_op, "market_type": "moneyline"})
        for spread_op in opportunities["spreads"]:
            all_ops.append({**spread_op, "market_type": "spreads"})
        for totals_op in opportunities["totals"]:
            all_ops.append({**totals_op, "market_type": "totals"})

        # Sort by EV and dedupe
        all_ops.sort(key=lambda x: x["expected_value"], reverse=True)

        for op in all_ops:
            game_id = op["game_id"]
            if game_id not in seen_games:
                seen_games[game_id] = op
                deduped[op["market_type"]].append(op)

        return deduped

    def build_ultimate_mixed_parlays(self, opportunities: dict) -> list:
        """Build ultimate mixed parlays combining ML + Spread + Totals"""
        parlays = []

        # Get deduped opportunities (one bet per game)
        deduped = self.dedupe_games_mixed(opportunities)

        # Strategy 1: Late Games Special (After 4:05 PM) - COMPREHENSIVE ML+SPREAD+O/U
        # Step 1: Get DEDUPED opportunities first
        deduped_ops = self.dedupe_games_mixed(opportunities)

        # Step 2: Filter for games starting after 4:05 PM
        late_games_ml = []
        late_games_spreads = []
        late_games_totals = []

        self.logger.info("Checking for late games (after 4:05 PM)...")

        for op in deduped_ops["moneyline"]:
            game_time = op.get("game_time", "")
            is_late = self.is_after_405pm(game_time)
            if is_late:
                late_games_ml.append(op)
                self.logger.info(f"Late ML: {op['selection']} at {game_time}")

        for op in deduped_ops["spreads"]:
            game_time = op.get("game_time", "")
            is_late = self.is_after_405pm(game_time)
            if is_late:
                late_games_spreads.append(op)

        for op in deduped_ops["totals"]:
            game_time = op.get("game_time", "")
            is_late = self.is_after_405pm(game_time)
            if is_late:
                late_games_totals.append(op)

        self.logger.info(
            f"Found {len(late_games_ml)} ML + {len(late_games_spreads)} Spread + {len(late_games_totals)} Totals for late games"
        )

        # Step 3: Build comprehensive late games parlay (ML+Spread+O/U up to 20 legs)
        late_mixed = (
            late_games_ml[:6] + late_games_spreads[:8] + late_games_totals[:6]
        )  # Max 20 legs

        # Step 4: Strict uniqueness validation
        unique_late_mixed = []
        seen_bets = set()

        for bet in late_mixed:
            bet_key = f"{bet['market']}__{bet['selection']}__{bet['game_id']}"
            if bet_key not in seen_bets:
                unique_late_mixed.append(bet)
                seen_bets.add(bet_key)

        # Step 5: Final deduplication and conflict resolution
        late_mixed_clean = self.remove_duplicate_picks(unique_late_mixed)
        late_mixed_clean = self.remove_team_conflicts(late_mixed_clean)
        late_mixed_clean = self.remove_same_game_spread_conflicts(late_mixed_clean)

        if len(late_mixed_clean) >= 4:
            parlays.append(
                {
                    "strategy": "Late Games Special",
                    "description": "ML + Spread + O/U for games after 4:05 PM (No conflicts)",
                    "legs": late_mixed_clean,
                    "stake_pct": 0.08,  # 8% of bankroll
                    "risk_level": "HIGH",
                    "mix_type": "Evening Action",
                }
            )

        # Strategy 2: Elite Mixed Trinity (Best from each market)
        elite_ml = [op for op in deduped["moneyline"] if "ELITE" in op["value_grade"]][:3]
        elite_spreads = [op for op in deduped["spreads"] if "ELITE" in op["value_grade"]][:3]
        elite_totals = [op for op in deduped["totals"] if "ELITE" in op["value_grade"]][:3]
        elite_mixed = elite_ml + elite_spreads + elite_totals

        # Remove team conflicts (ML + Spread on same team)
        elite_mixed_clean = self.remove_team_conflicts(elite_mixed)

        if len(elite_mixed_clean) >= 4:
            parlays.append(
                {
                    "strategy": "Elite Mixed Trinity",
                    "description": "Premium ML + Spread + O/U combinations (No conflicts)",
                    "legs": elite_mixed_clean,
                    "stake_pct": 0.1,  # 10% of bankroll
                    "risk_level": "MEDIUM",
                    "mix_type": "Elite Value",
                }
            )

        # Strategy 3: Late Games Comprehensive (All markets for games after 4:05 PM)
        # Focus on comprehensive coverage of late starting games with balanced distribution
        late_game_comprehensive = []
        game_coverage = {}

        # Get all late game opportunities by game
        for market_type in ["moneyline", "spreads", "totals"]:
            market_ops = deduped_ops.get(market_type, [])
            for op in market_ops:
                if self.is_after_405pm(op.get("game_time", "")):
                    game_id = op["game_id"]
                    if game_id not in game_coverage:
                        game_coverage[game_id] = {}

                    # Keep best opportunity from each market for each late game
                    if (
                        market_type not in game_coverage[game_id]
                        or op["expected_value"]
                        > game_coverage[game_id][market_type]["expected_value"]
                    ):
                        game_coverage[game_id][market_type] = op

        # Build comprehensive late game parlay (one bet per market per late game)
        for game_id, markets in game_coverage.items():
            if len(late_game_comprehensive) >= 15:  # Limit to 15 legs
                break

            # Add best bet from each available market for this late game
            for market_type in ["moneyline", "spreads", "totals"]:
                if market_type in markets and len(late_game_comprehensive) < 15:
                    if (
                        markets[market_type]["expected_value"] >= 2
                    ):  # Lower threshold for late games
                        late_game_comprehensive.append(markets[market_type])

        # Final cleanup
        late_comprehensive_clean = self.remove_duplicate_picks(late_game_comprehensive)
        late_comprehensive_clean = self.remove_team_conflicts(late_comprehensive_clean)
        late_comprehensive_clean = self.remove_same_game_spread_conflicts(late_comprehensive_clean)

        if len(late_comprehensive_clean) >= 6:
            parlays.append(
                {
                    "strategy": "Late Games Comprehensive",
                    "description": "All markets coverage for games after 4:05 PM",
                    "legs": late_comprehensive_clean,
                    "stake_pct": 0.12,  # 12% of bankroll
                    "risk_level": "MEDIUM",
                    "mix_type": "Evening Coverage",
                }
            )

        # Strategy 4: Conservative Mixed (High-confidence picks only)
        conservative_mixed = []
        for market_type in ["moneyline", "spreads", "totals"]:
            high_confidence = [
                op for op in opportunities[market_type] if op["expected_value"] >= 8
            ][:3]
            conservative_mixed.extend(high_confidence)

        # Remove team conflicts first, then dedupe by game
        conservative_clean = self.remove_team_conflicts(conservative_mixed)

        # Dedupe conservative picks by game
        conservative_deduped = []
        seen_conservative = set()
        for op in conservative_clean:
            if op["game_id"] not in seen_conservative:
                conservative_deduped.append(op)
                seen_conservative.add(op["game_id"])

        if len(conservative_deduped) >= 4:
            parlays.append(
                {
                    "strategy": "Conservative Mixed",
                    "description": "High-confidence ML + Spread + O/U (No conflicts)",
                    "legs": conservative_deduped[:6],
                    "stake_pct": 0.12,  # 12% of bankroll
                    "risk_level": "LOW",
                    "mix_type": "Safe Value",
                }
            )

        # Final validation: Remove team conflicts and same-game spread conflicts
        validated_parlays = []
        for parlay in parlays:
            needs_fixing = self.has_team_conflict(
                parlay["legs"]
            ) or self.has_same_game_spread_conflict(parlay["legs"])

            if not needs_fixing:
                validated_parlays.append(parlay)
            else:
                # Fix conflicts in this parlay
                clean_legs = self.remove_duplicate_picks(parlay["legs"])
                clean_legs = self.remove_team_conflicts(clean_legs)
                clean_legs = self.remove_same_game_spread_conflicts(clean_legs)

                if len(clean_legs) >= 3:  # Minimum legs for mixed parlay
                    parlay["legs"] = clean_legs
                    parlay["description"] += " (All conflicts resolved)"
                    validated_parlays.append(parlay)
                    self.logger.info(f"Fixed all conflicts in {parlay['strategy']}")

        return validated_parlays

    def calculate_parlay_odds(self, legs: list) -> tuple:
        """Calculate parlay odds and multiplier"""
        total_prob = 1.0

        for leg in legs:
            prob = self.implied_probability(leg["odds"])
            total_prob *= prob

        if total_prob > 0:
            multiplier = 1 / total_prob
            american_odds = self.decimal_to_american(multiplier)
            return american_odds, multiplier

        return 0, 1

    def implied_probability(self, odds: int) -> float:
        """Convert American odds to implied probability"""
        if odds > 0:
            return 100 / (odds + 100)
        return abs(odds) / (abs(odds) + 100)

    def decimal_to_american(self, decimal_odds: float) -> float:
        """Convert decimal odds to American format"""
        if decimal_odds >= 2:
            return (decimal_odds - 1) * 100
        return -100 / (decimal_odds - 1)

    def format_ultimate_output(self, parlays: list, opportunities: dict, game_status: dict) -> str:
        """Format comprehensive mixed parlay output"""

        total_ops = (
            len(opportunities["moneyline"])
            + len(opportunities["spreads"])
            + len(opportunities["totals"])
        )

        output = f"""
🏈 ULTIMATE NFL MIXED PARLAY ANALYZER 🏈
⏰ Generated: {datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")}
💰 Bankroll: ${self.bankroll:,.2f}
🎯 Analysis: MONEYLINE + SPREAD + TOTALS COMBINED
============================================================

📊 GAME STATUS:
🔴 Live Games: {len(game_status["live"])}
🕐 Upcoming Games: {len(game_status["upcoming"])}
⚫ Finished Games: {len(game_status["finished"])}

💰 OPPORTUNITIES FOUND:
📈 Moneyline: {len(opportunities["moneyline"])} picks
📊 Spreads: {len(opportunities["spreads"])} picks
🎲 Totals: {len(opportunities["totals"])} picks
🎯 Total: {total_ops} opportunities
📋 Mixed Parlays: {len(parlays)}

============================================================

"""

        for i, parlay in enumerate(parlays, 1):
            odds, multiplier = self.calculate_parlay_odds(parlay["legs"])
            stake = self.bankroll * parlay["stake_pct"]
            payout = stake * multiplier

            # Count bet types in parlay
            ml_count = len([leg for leg in parlay["legs"] if leg["market"] == "Moneyline"])
            spread_count = len([leg for leg in parlay["legs"] if leg["market"] == "Spread"])
            totals_count = len([leg for leg in parlay["legs"] if leg["market"] == "Totals"])

            output += f"""🎯 MIXED PARLAY #{i}: {parlay["strategy"]}
📖 {parlay["description"]}
🎪 Mix: {ml_count} ML + {spread_count} Spread + {totals_count} O/U | {parlay["mix_type"]}
📊 Legs: {len(parlay["legs"])} | Odds: {odds:+.0f} | Stake: ${stake:.0f} | Risk: {parlay["risk_level"]}
💸 Payout: ${payout:,.2f} | Net: +${payout - stake:,.2f}
----------------------------------------
"""

            for j, leg in enumerate(parlay["legs"], 1):
                status_icon = (
                    "🔴"
                    if leg["status"] == "LIVE"
                    else "🕐" if leg["status"] == "UPCOMING" else "⚫"
                )

                # Format market-specific info
                market_info = leg["market"]
                if leg["market"] == "Spread":
                    market_info += f" ({leg['spread']:+})"
                elif leg["market"] == "Totals":
                    market_info += f" ({leg['bet_type']} {leg['total']})"

                output += f"""   {j}. {leg["selection"]} - {market_info}
      📈 {leg["odds"]:+} | EV: {leg["expected_value"]:+.1f}% | {leg["value_grade"]}
      {status_icon} {leg["status"]} | 🕐 {leg["game_time"]} | 📱 {leg["sportsbook"]}
      🏟️ {leg["teams"]}
"""

            output += "\n"

        # Live games detail
        if game_status["live"]:
            output += "\n🔴 LIVE MIXED BETTING ANALYSIS:\n"
            for game in game_status["live"]:
                output += f"   {game['away_team']} @ {game['home_team']} - {game['elapsed_hours']:.1f}h elapsed\n"
            output += "\n"

        # Market breakdown
        elite_ml = len([op for op in opportunities["moneyline"] if "ELITE" in op["value_grade"]])
        elite_spreads = len([op for op in opportunities["spreads"] if "ELITE" in op["value_grade"]])
        elite_totals = len([op for op in opportunities["totals"] if "ELITE" in op["value_grade"]])

        output += f"""📊 MIXED MARKET BREAKDOWN:
🎯 ELITE Opportunities:
   • Moneyline: {elite_ml} elite picks
   • Spreads: {elite_spreads} elite picks
   • Totals: {elite_totals} elite picks

🔥 TOP CROSS-MARKET OPPORTUNITIES:
"""

        # Show top 3 from each market
        for market_name, ops in opportunities.items():
            if ops:
                top_pick = ops[0]
                output += f"   • {market_name.title()}: {top_pick['selection']} ({top_pick['expected_value']:.1f}% EV)\n"

        output += """
🎪 MIXED PARLAY ADVANTAGES:
✅ Diversification across bet types
✅ Reduced correlation risk
✅ Maximum market coverage
✅ Live + upcoming game mix
✅ Elite value combinations

📊 VALUE LEGEND:
🟢 ELITE = 15%+ EV  |  🟢 STRONG = 8%+ EV  |  🟡 SOLID = 4%+ EV
🟠 FAIR = 1%+ EV  |  🔴 AVOID = <1% EV

🚀 Ready to place these ULTIMATE MIXED parlays? LFG! 🚀
"""

        return output

    async def run_ultimate_analysis(self) -> dict:
        """Main ultimate mixed analysis execution"""
        try:
            self.logger.info("Starting Ultimate NFL Mixed Parlay Analysis")

            # Fetch comprehensive data
            data = self.get_comprehensive_nfl_data()
            if not data["success"]:
                return {"success": False, "message": data["error"]}

            # Analyze game status
            game_status = self.analyze_game_status(data["games"])

            # Extract all opportunities
            all_games = game_status["live"] + game_status["upcoming"]
            opportunities = self.extract_all_opportunities(all_games)

            # Build ultimate mixed parlays
            parlays = self.build_ultimate_mixed_parlays(opportunities)

            # Generate output
            output = self.format_ultimate_output(parlays, opportunities, game_status)
            print(output)

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results = {
                "timestamp": datetime.now().isoformat(),
                "bankroll": self.bankroll,
                "game_status": game_status,
                "opportunities": opportunities,
                "parlays": parlays,
                "summary": {
                    "total_ml_ops": len(opportunities["moneyline"]),
                    "total_spread_ops": len(opportunities["spreads"]),
                    "total_totals_ops": len(opportunities["totals"]),
                    "total_parlays": len(parlays),
                    "live_games": len(game_status["live"]),
                    "upcoming_games": len(game_status["upcoming"]),
                },
            }

            filename = f"C:/EQ12/logs/nfl_ultimate_mixed_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(results, f, indent=2, default=str)

            return {
                "success": True,
                "message": f"Generated {len(parlays)} ultimate mixed parlay strategies",
                "results_file": filename,
            }

        except Exception as e:
            self.logger.error(f"Ultimate analysis failed: {e}")
            return {"success": False, "message": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Ultimate NFL Mixed Parlay Analyzer")
    parser.add_argument("--bankroll", type=float, default=1000.0, help="Bankroll amount")

    args = parser.parse_args()

    analyzer = EQ12UltimateMixedAnalyzer()
    analyzer.bankroll = args.bankroll

    try:
        result = asyncio.run(analyzer.run_ultimate_analysis())
        if result["success"]:
            print(f"\n✅ {result['message']}")
            if "results_file" in result:
                print(f"📁 Results: {result['results_file']}")
        else:
            print(f"\n❌ {result['message']}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Ultimate analysis stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Ultimate analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
