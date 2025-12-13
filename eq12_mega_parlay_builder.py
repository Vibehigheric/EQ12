#!/usr/bin/env python3
"""
EQ12 MEGA PARLAY BUILDER - October 4, 2025
Pulls all games starting after 3PM and builds optimized parlays up to 20 legs
ENHANCED WITH LIVE NBA DATA INTEGRATION AND RATE LIMITING
"""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

# Import EQ12 rate limiting system
try:
    from eq12_rate_limit import get_limiter_stats, get_with_limit, sync_limiter

    RATE_LIMITING_AVAILABLE = True
    print("EQ12 Rate limiting enabled")
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    print("Rate limiting not available - using basic requests")

# Import today-only guard system
from eq12_date_filters import filter_after_time, filter_events_today

# Import NBA data integration
try:
    from eq12_nba_data_integration import NBADataIntegration

    NBA_INTEGRATION_AVAILABLE = True
except ImportError:
    NBA_INTEGRATION_AVAILABLE = False
    print("NBA Integration not available - using static data")

# Global date filtering settings
TARGET_DATE = None  # None = today (America/New_York); override with --date
AFTER = "15:00"  # Default: after 3 PM


class BetType(Enum):
    MONEYLINE = "ML"
    SPREAD = "SPREAD"
    OVER_UNDER = "O/U"
    PROP = "PROP"


class Sport(Enum):
    NCAA_FOOTBALL = "NCAA Football"
    NFL = "NFL"
    NBA = "NBA"
    NHL = "NHL"
    MLB = "MLB"
    SOCCER = "Soccer"
    TENNIS = "Tennis"


@dataclass
class GameInfo:
    """Individual game information"""

    home_team: str
    away_team: str
    sport: Sport
    game_time: str
    spread_line: float | None = None
    total_line: float | None = None
    home_ml_odds: float | None = None
    away_ml_odds: float | None = None
    props: dict[str, float] | None = None


@dataclass
class ParlayLeg:
    """Individual parlay leg with complete details"""

    game: GameInfo
    bet_type: BetType
    selection: str
    odds: float
    confidence: float
    reasoning: str
    game_id: str | None = None  # For same-game conflict detection


@dataclass
class MegaParlay:
    """Complete parlay with up to 20 legs"""

    legs: list[ParlayLeg]
    total_odds: float
    stake: float
    expected_payout: float
    confidence_score: float
    risk_level: str
    category: str


class EQ12MegaParlayBuilder:
    """Enhanced parlay builder for maximum profit opportunities with NBA integration"""

    def __init__(self):
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.current_time = datetime.now()
        self.cutoff_time = self.current_time.replace(hour=15, minute=0, second=0)
        self.bankroll = 1000.00
        self.base_directory = Path("C:/EQ12")
        self.logs_dir = self.base_directory / "logs"

        # Initialize NBA data integration
        self._initialize_nba_integration()

    @staticmethod
    def clean_label(s: str) -> str:
        """Clean up duplicate labels and formatting issues"""
        if not s:
            return s
        s = " ".join(s.split())  # collapse whitespace

        # Fix duplicate Over/Under labels
        s = s.replace("Over Over", "Over").replace("Under Under", "Under")

        # Fix "Under Over" patterns (e.g., "First Dunk Under Over 5.5" -> "First Dunk Under 5.5")
        s = s.replace("Under Over", "Under").replace("Over Under", "Over")

        # Fix duplicate pipe separators
        s = s.replace(" |  | ", " | ")

        # Fix duplicate timestamps (e.g., "07:30 PM | 07:30 PM |")
        import re

        # Match duplicate time patterns like "HH:MM AM/PM | HH:MM AM/PM |"
        time_pattern = r"(\d{1,2}:\d{2}\s+[AP]M)\s+\|\s+\1\s+\|"
        s = re.sub(time_pattern, r"\1 |", s)

        return s

    @staticmethod
    def uniq_time_str(dt_str: str) -> str:
        """Create unique time string from datetime string"""
        try:
            # Parse the datetime string and format consistently
            if isinstance(dt_str, str):
                dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            else:
                dt = dt_str
            return dt.strftime("%I:%M %p").lstrip("0")
        except Exception:
            return str(dt_str)  # fallback

    def _initialize_nba_integration(self):
        """Initialize NBA data integration if available"""
        if NBA_INTEGRATION_AVAILABLE:
            self.nba_integration = NBADataIntegration()
            print("✅ NBA Data Integration enabled")
        else:
            self.nba_integration = None
            print("⚠️ Using static NBA data")

    def _get_live_nba_games(self) -> list[GameInfo]:
        """Get live NBA games from NBA.com integration"""
        if not self.nba_integration:
            return []

        try:
            # Get today's NBA games after the cutoff time
            nba_games_live = self.nba_integration.get_todays_games(AFTER)
            converted_games = []

            for nba_game in nba_games_live:
                # Enrich with betting data
                enriched_game = self.nba_integration.enrich_game_with_betting_data(nba_game)

                # Get dunk score betting insights for this game
                dunk_props = self._get_dunk_score_props(enriched_game)

                # Convert to EQ12 GameInfo format
                game_info = GameInfo(
                    home_team=enriched_game.home_team,
                    away_team=enriched_game.away_team,
                    sport=Sport.NBA,
                    game_time=enriched_game.game_time.strftime("%Y-%m-%d %H:%M"),
                    spread_line=enriched_game.spread_line,
                    total_line=enriched_game.total_line,
                    home_ml_odds=enriched_game.home_ml_odds,
                    away_ml_odds=enriched_game.away_ml_odds,
                    props=dunk_props,  # Enhanced with dunk score props
                )
                converted_games.append(game_info)

            print("🏀 Found {len(converted_games)} live NBA games")
            return converted_games

        except Exception:
            print("⚠️ Error fetching live NBA data: {e}")
            return []

    def _get_dunk_score_props(self, nba_game) -> dict[str, float]:
        """Generate dunk score based prop bets for NBA games"""
        if not self.nba_integration:
            return {}

        props = {}

        try:
            # Get dunk score insights for betting
            insights = self.nba_integration.get_dunk_score_betting_insights([nba_game])

            # Add standard NBA props
            game_key = f"{nba_game.away_team}_{nba_game.home_team}".lower().replace(" ", "_")

            # Base props for all NBA games
            props.update(
                {
                    "total_dunks_over": 4.5,
                    "first_dunk_under": 5.5,  # minutes into game
                    "poster_dunk_yes": 1.5,  # special dunk score market
                }
            )

            # Enhanced props based on dunk score data
            if insights.get("high_dunk_probability"):
                for player_insight in insights["high_dunk_probability"][:3]:
                    player_name = player_insight["player"].lower().replace(" ", "_")

                    # Player-specific dunk props
                    props[f"{player_name}_dunks_over"] = 0.5
                    props[f"{player_name}_dunk_score_over"] = 85.0

                    # If high-confidence dunker, adjust team totals
                    if player_insight["confidence"] == "High":
                        props["total_dunks_over"] = 6.5
                        props[f"{player_name}_poster_dunk"] = 2.0  # Yes/No market

            # Team-specific adjustments
            high_energy_teams = ["denver_nuggets", "dallas_mavericks", "utah_jazz"]
            if any(team in game_key for team in high_energy_teams):
                props["total_dunks_over"] = props.get("total_dunks_over", 4.5) + 1.0
                props["highlight_dunk_over"] = 100.0  # Dunk score threshold

        except Exception:
            print("⚠️ Error generating dunk props: {e}")
            # Fallback to basic props
            props = {
                "total_dunks_over": 4.5,
                "poster_dunk_yes": 1.5,
            }

        return props

    def get_all_games_after_3pm(self) -> list[GameInfo]:
        """Get comprehensive list of all games with today-only filtering"""

        # NCAA FOOTBALL - Saturday Night Action
        ncaa_games = [
            GameInfo(
                home_team="Louisiana Tech",
                away_team="UTEP",
                sport=Sport.NCAA_FOOTBALL,
                game_time="2025-10-04 19:30",
                spread_line=-7.5,
                total_line=58.5,
                home_ml_odds=-280,
                away_ml_odds=+230,
                props={"rushing_yards_over": 150.5, "passing_yards_over": 275.5},
            ),
            GameInfo(
                home_team="Toledo",
                away_team="Buffalo",
                sport=Sport.NCAA_FOOTBALL,
                game_time="2025-10-04 20:00",
                spread_line=-10.5,
                total_line=52.5,
                home_ml_odds=-450,
                away_ml_odds=+350,
                props={"total_touchdowns_over": 6.5, "field_goals_over": 2.5},
            ),
            GameInfo(
                home_team="Nevada",
                away_team="Air Force",
                sport=Sport.NCAA_FOOTBALL,
                game_time="2025-10-04 22:30",
                spread_line=+3.5,
                total_line=45.5,
                home_ml_odds=+150,
                away_ml_odds=-170,
                props={"rushing_attempts_over": 42.5, "time_of_possession": 32.5},
            ),
            GameInfo(
                home_team="San Diego State",
                away_team="Fresno State",
                sport=Sport.NCAA_FOOTBALL,
                game_time="2025-10-04 22:00",
                spread_line=-3.0,
                total_line=48.5,
                home_ml_odds=-140,
                away_ml_odds=+120,
            ),
            GameInfo(
                home_team="Boise State",
                away_team="Hawaii",
                sport=Sport.NCAA_FOOTBALL,
                game_time="2025-10-04 23:30",
                spread_line=-14.5,
                total_line=55.5,
                home_ml_odds=-650,
                away_ml_odds=+475,
            ),
        ]

        # NHL - Saturday Night Hockey
        nhl_games = [
            GameInfo(
                home_team="Pittsburgh Penguins",
                away_team="New York Rangers",
                sport=Sport.NHL,
                game_time="2025-10-04 19:00",
                spread_line=-1.5,
                total_line=6.5,
                home_ml_odds=+120,
                away_ml_odds=-140,
                props={"shots_on_goal_over": 28.5, "power_plays_over": 3.5},
            ),
            GameInfo(
                home_team="Detroit Red Wings",
                away_team="Nashville Predators",
                sport=Sport.NHL,
                game_time="2025-10-04 19:30",
                spread_line=+1.5,
                total_line=6.0,
                home_ml_odds=+180,
                away_ml_odds=-200,
            ),
            GameInfo(
                home_team="Chicago Blackhawks",
                away_team="St. Louis Blues",
                sport=Sport.NHL,
                game_time="2025-10-04 20:00",
                spread_line=+1.5,
                total_line=6.5,
                home_ml_odds=+165,
                away_ml_odds=-185,
            ),
            GameInfo(
                home_team="Colorado Avalanche",
                away_team="Seattle Kraken",
                sport=Sport.NHL,
                game_time="2025-10-04 21:00",
                spread_line=-1.5,
                total_line=6.0,
                home_ml_odds=-175,
                away_ml_odds=+155,
            ),
            GameInfo(
                home_team="Vegas Golden Knights",
                away_team="Anaheim Ducks",
                sport=Sport.NHL,
                game_time="2025-10-04 22:00",
                spread_line=-1.5,
                total_line=6.5,
                home_ml_odds=-190,
                away_ml_odds=+170,
            ),
        ]

        # NBA GAMES - Live Integration or Static Fallback
        nba_games = self._get_live_nba_games()

        # Fallback to static data if live integration fails
        if not nba_games:
            print("🔄 Using static NBA data as fallback")
            nba_games = [
                GameInfo(
                    home_team="Philadelphia 76ers",
                    away_team="New York Knicks",
                    sport=Sport.NBA,
                    game_time="2025-10-04 19:00",
                    spread_line=-3.5,
                    total_line=218.5,
                    home_ml_odds=-120,
                    away_ml_odds=+100,
                    props={"knicks_points_over": 110.5, "total_3pt_made_over": 24.5},
                ),
                GameInfo(
                    home_team="Miami Heat",
                    away_team="Orlando Magic",
                    sport=Sport.NBA,
                    game_time="2025-10-04 20:00",
                    spread_line=-4.5,
                    total_line=216.0,
                    home_ml_odds=-165,
                    away_ml_odds=+145,
                    props={"heat_points_over": 109.5, "magic_assists_over": 23.5},
                ),
                GameInfo(
                    home_team="Denver Nuggets",
                    away_team="Minnesota Timberwolves",
                    sport=Sport.NBA,
                    game_time="2025-10-04 21:00",
                    spread_line=-3.5,
                    total_line=219.5,
                    home_ml_odds=-125,
                    away_ml_odds=+105,
                    props={"jokic_points_over": 22.5, "edwards_points_over": 26.5},
                ),
                GameInfo(
                    home_team="New Orleans Pelicans",
                    away_team="Melbourne Phoenix",
                    sport=Sport.NBA,
                    game_time="2025-10-04 23:00",
                    spread_line=-12.5,
                    total_line=212.0,
                    home_ml_odds=-180,
                    away_ml_odds=+150,
                    props={"pelicans_points_over": 115.5, "total_rebounds_over": 95.5},
                ),
                GameInfo(
                    home_team="Brooklyn Nets",
                    away_team="Hapoel Jerusalem",
                    sport=Sport.NBA,
                    game_time="2025-10-04 20:00",
                    spread_line=-8.5,
                    total_line=208.0,
                    home_ml_odds=-275,
                    away_ml_odds=+225,
                    props={"nets_points_over": 108.5, "total_turnovers_over": 28.5},
                ),
            ]

        # SOCCER - WEB VERIFIED GAMES
        soccer_games = [
            GameInfo(
                home_team="Villarreal",
                away_team="Real Madrid",
                sport=Sport.SOCCER,
                game_time="2025-10-04 15:00",
                spread_line=+0.5,
                total_line=2.5,
                home_ml_odds=+240,
                away_ml_odds=-240,
                props={"goals_over": 2.5, "cards_over": 4.5},
            ),
            GameInfo(
                home_team="Como",
                away_team="Atalanta",
                sport=Sport.SOCCER,
                game_time="2025-10-04 14:45",
                spread_line=+1.5,
                total_line=2.5,
                home_ml_odds=+350,
                away_ml_odds=+115,
                props={"atalanta_goals_over": 1.5, "total_corners_over": 9.5},
            ),
            GameInfo(
                home_team="Lens",
                away_team="AJ Auxerre",
                sport=Sport.SOCCER,
                game_time="2025-10-04 15:05",
                spread_line=-0.5,
                total_line=2.5,
                home_ml_odds=+100,
                away_ml_odds=+280,
                props={"goals_over": 2.5, "both_teams_score": "Yes"},
            ),
            GameInfo(
                home_team="Santa Clara",
                away_team="Vitoria Guimaraes",
                sport=Sport.SOCCER,
                game_time="2025-10-04 15:30",
                spread_line=+0.5,
                total_line=2.5,
                home_ml_odds=+200,
                away_ml_odds=+160,
                props={"goals_over": 2.5, "corners_over": 8.5},
            ),
            GameInfo(
                home_team="LA Galaxy",
                away_team="FC Dallas",
                sport=Sport.SOCCER,
                game_time="2025-10-04 16:30",
                spread_line=-0.5,
                total_line=3.5,
                home_ml_odds=-155,
                away_ml_odds=+450,
                props={"goals_over": 3.5, "mls_action": "Yes"},
            ),
            GameInfo(
                home_team="Columbus Crew",
                away_team="Orlando City SC",
                sport=Sport.SOCCER,
                game_time="2025-10-04 19:30",
                spread_line=-0.5,
                total_line=3.5,
                home_ml_odds=-110,
                away_ml_odds=+280,
                props={"goals_over": 3.5, "both_teams_score": "Yes"},
            ),
        ]

        # Collect all games into a single list as dictionaries for filtering
        all_games_data = []

        for game in ncaa_games + nhl_games + nba_games + soccer_games:
            game_dict = {
                "home_team": game.home_team,
                "away_team": game.away_team,
                "sport": game.sport.value,
                "commence_time": game.game_time + ":00Z",  # Convert to UTC format
                "spread_line": game.spread_line,
                "total_line": game.total_line,
                "home_ml_odds": game.home_ml_odds,
                "away_ml_odds": game.away_ml_odds,
                "props": game.props or {},
            }
            all_games_data.append(game_dict)

        # Apply today-only filtering first
        filtered_games_data = filter_events_today(
            all_games_data,
            get_commence=lambda e: e.get("commence_time"),
            target_date=TARGET_DATE,
        )

        # Apply after-time filtering
        if AFTER:
            filtered_games_data = filter_after_time(
                filtered_games_data,
                get_commence=lambda e: e.get("commence_time"),
                hhmm=AFTER,
                target_date=TARGET_DATE,
            )

        # Convert back to GameInfo objects
        filtered_games = []
        for game_data in filtered_games_data:
            game_info = GameInfo(
                home_team=game_data["home_team"],
                away_team=game_data["away_team"],
                sport=Sport(game_data["sport"]),
                game_time=game_data["commence_time"].replace(":00Z", ""),
                spread_line=game_data["spread_line"],
                total_line=game_data["total_line"],
                home_ml_odds=game_data["home_ml_odds"],
                away_ml_odds=game_data["away_ml_odds"],
                props=game_data["props"],
            )
            filtered_games.append(game_info)

        return filtered_games

    def create_parlay_legs(self, games: list[GameInfo]) -> list[ParlayLeg]:
        """Create all possible parlay legs with conflict prevention"""
        legs = []

        for game in games:
            game_id = f"{game.away_team}@{game.home_team}_{game.game_time}"

            # Moneyline legs - Only add stronger option to prevent same-game conflicts
            if game.home_ml_odds and game.away_ml_odds:
                home_conf = self._calculate_ml_confidence(game.home_ml_odds)
                away_conf = self._calculate_ml_confidence(game.away_ml_odds)

                # Add only the stronger ML option per game
                if home_conf >= away_conf:
                    legs.append(
                        ParlayLeg(
                            game=game,
                            bet_type=BetType.MONEYLINE,
                            selection=f"{game.home_team} ML",
                            odds=game.home_ml_odds,
                            confidence=home_conf,
                            reasoning=f"Stronger ML pick: {game.home_team}",
                            game_id=game_id,
                        )
                    )
                else:
                    legs.append(
                        ParlayLeg(
                            game=game,
                            bet_type=BetType.MONEYLINE,
                            selection=f"{game.away_team} ML",
                            odds=game.away_ml_odds,
                            confidence=away_conf,
                            reasoning=f"Stronger ML pick: {game.away_team}",
                            game_id=game_id,
                        )
                    )
            elif game.home_ml_odds:
                legs.append(
                    ParlayLeg(
                        game=game,
                        bet_type=BetType.MONEYLINE,
                        selection=f"{game.home_team} ML",
                        odds=game.home_ml_odds,
                        confidence=self._calculate_ml_confidence(game.home_ml_odds),
                        reasoning=f"Home advantage for {game.home_team}",
                        game_id=game_id,
                    )
                )
            elif game.away_ml_odds:
                legs.append(
                    ParlayLeg(
                        game=game,
                        bet_type=BetType.MONEYLINE,
                        selection=f"{game.away_team} ML",
                        odds=game.away_ml_odds,
                        confidence=self._calculate_ml_confidence(game.away_ml_odds),
                        reasoning=f"Road value with {game.away_team}",
                        game_id=game_id,
                    )
                )

            # Spread legs
            if game.spread_line is not None:
                if game.spread_line < 0:
                    favorite = game.home_team
                    underdog = game.away_team
                else:
                    favorite = game.away_team
                    underdog = game.home_team
                spread_val = abs(game.spread_line)

                legs.append(
                    ParlayLeg(
                        game=game,
                        bet_type=BetType.SPREAD,
                        selection=f"{favorite} -{spread_val}",
                        odds=-110,
                        confidence=0.75 if spread_val < 7 else 0.65,
                        reasoning=f"Favorite -{spread_val} reasonable",
                    )
                )

                legs.append(
                    ParlayLeg(
                        game=game,
                        bet_type=BetType.SPREAD,
                        selection=f"{underdog} +{spread_val}",
                        odds=-110,
                        confidence=0.70 if spread_val > 7 else 0.60,
                        reasoning=f"Underdog +{spread_val} value",
                    )
                )

            # Total legs
            if game.total_line is not None:
                legs.append(
                    ParlayLeg(
                        game=game,
                        bet_type=BetType.OVER_UNDER,
                        selection=f"Over {game.total_line}",
                        odds=-110,
                        confidence=0.68,
                        reasoning=f"Over {game.total_line} - offensive game",
                    )
                )

                legs.append(
                    ParlayLeg(
                        game=game,
                        bet_type=BetType.OVER_UNDER,
                        selection=f"Under {game.total_line}",
                        odds=-110,
                        confidence=0.65,
                        reasoning=f"Under {game.total_line} - defensive game",
                    )
                )

            # Prop legs with specific game/team context
            if game.props:
                game_time = datetime.strptime(game.game_time, "%Y-%m-%d %H:%M").strftime("%I:%M %p")
                for prop_name, prop_line in game.props.items():
                    # Smart prop display formatting to avoid "Over Over" issues
                    if "under" in prop_name.lower():
                        # For "under" props, use "Under" instead of "Over"
                        base_display = prop_name.replace("_", " ").title().replace("Under", "")
                        prop_display = f"{base_display.strip()} Under"
                    elif "over" in prop_name.lower():
                        # For "over" props, remove redundant "over" from name
                        base_display = prop_name.replace("_", " ").title().replace("Over", "")
                        prop_display = f"{base_display.strip()} Over"
                    else:
                        # Default formatting with Over appended
                        prop_display = prop_name.replace("_", " ").title()

                    # Add specific context to avoid vague descriptions
                    if "rushing" in prop_name or "passing" in prop_name or "yards" in prop_name:
                        if "under" in prop_name.lower():
                            selection = f"{game_time} | {game.away_team} @ {game.home_team} {prop_display} {prop_line}"
                        else:
                            selection = f"{game_time} | {game.away_team} @ {game.home_team} {prop_display} {prop_line}"
                    elif "touchdowns" in prop_name or "field_goals" in prop_name:
                        if "under" in prop_name.lower():
                            selection = f"{game_time} | {game.away_team} @ {game.home_team} Game {prop_display} {prop_line}"
                        else:
                            selection = f"{game_time} | {game.away_team} @ {game.home_team} Game {prop_display} {prop_line}"
                    else:
                        if "under" in prop_name.lower():
                            selection = f"{game_time} | {prop_display} {prop_line} ({game.away_team} @ {game.home_team})"
                        else:
                            selection = f"{game_time} | {prop_display} {prop_line} ({game.away_team} @ {game.home_team})"

                    # Clean the selection to prevent duplicate labels
                    selection = EQ12MegaParlayBuilder.clean_label(selection)

                    legs.append(
                        ParlayLeg(
                            game=game,
                            bet_type=BetType.PROP,
                            selection=selection,
                            odds=-115,
                            confidence=0.72,
                            reasoning=f"Prop value: {prop_name} in {game.away_team} @ {game.home_team}",
                            game_id=game_id,
                        )
                    )

        return legs

    def _calculate_ml_confidence(self, odds: float) -> float:
        """Calculate confidence based on moneyline odds"""
        implied_prob = abs(odds) / (abs(odds) + 100) if odds < 0 else 100 / (odds + 100)

        # Adjust for juice and add our edge
        return min(implied_prob * 1.05, 0.85)

    def calculate_parlay_odds(self, legs: list[ParlayLeg]) -> float:
        """Calculate total parlay odds"""
        total_odds = 1.0

        for leg in legs:
            decimal_odds = 1 + 100 / abs(leg.odds) if leg.odds < 0 else 1 + leg.odds / 100
            total_odds *= decimal_odds

        # Convert back to American odds
        if total_odds >= 2.0:
            return (total_odds - 1) * 100
        return -100 / (total_odds - 1)

    def calculate_true_expected_value(self, legs: list[ParlayLeg]) -> float:
        """
        Calculate true expected value (probability-weighted return).

        Note: This fixes the confusion between expected_roi (payout multiplier)
        and true expected value (probability-weighted expected return).
        """
        # Calculate probability of all legs hitting
        win_probability = 1.0
        for leg in legs:
            win_probability *= leg.confidence

        # Get payout multiplier from odds
        parlay_odds = self.calculate_parlay_odds(legs)
        if parlay_odds >= 0:
            payout_multiplier = 1 + (parlay_odds / 100)
        else:
            payout_multiplier = 1 + (100 / abs(parlay_odds))

        # True EV = (win_prob * gross_return) - initial_bet
        # For $1 bet: EV = (win_prob * payout_multiplier) - 1
        expected_value = (win_probability * payout_multiplier) - 1

        return expected_value

    def build_mega_parlays(self, max_legs: int = 20) -> list[MegaParlay]:
        """Build optimized parlays with different leg counts and strategies"""
        games = self.get_all_games_after_3pm()
        all_legs = self.create_parlay_legs(games)

        mega_parlays = []

        # High Confidence Parlays (8-12 legs)
        high_conf_legs = [leg for leg in all_legs if leg.confidence >= 0.70]
        for leg_count in range(8, 13):
            if len(high_conf_legs) >= leg_count:
                best_combo = self._select_best_combination(high_conf_legs, leg_count, "confidence")
                if best_combo:
                    parlay = self._create_mega_parlay(best_combo, "High Confidence")
                    mega_parlays.append(parlay)

        # Value Parlays (12-16 legs)
        value_legs = [leg for leg in all_legs if leg.confidence >= 0.65]
        for leg_count in range(12, 17):
            if len(value_legs) >= leg_count:
                best_combo = self._select_best_combination(value_legs, leg_count, "balanced")
                if best_combo:
                    parlay = self._create_mega_parlay(best_combo, "Value Play")
                    mega_parlays.append(parlay)

        # Moonshot Parlays (16-20 legs)
        all_legs_sorted = sorted(
            all_legs,
            key=lambda x: x.confidence * (1 + abs(x.odds / 1000)),
            reverse=True,
        )
        for leg_count in range(16, 21):
            if len(all_legs_sorted) >= leg_count:
                best_combo = self._select_best_combination(all_legs_sorted, leg_count, "moonshot")
                if best_combo:
                    parlay = self._create_mega_parlay(best_combo, "Moonshot")
                    mega_parlays.append(parlay)

        # Sport-Specific Parlays
        for sport in [Sport.NCAA_FOOTBALL, Sport.NHL, Sport.NBA]:
            sport_legs = [leg for leg in all_legs if leg.game.sport == sport]
            if len(sport_legs) >= 8:
                best_combo = self._select_best_combination(
                    sport_legs, min(12, len(sport_legs)), "balanced"
                )
                if best_combo:
                    parlay = self._create_mega_parlay(best_combo, f"{sport.value} Special")
                    mega_parlays.append(parlay)

        return sorted(mega_parlays, key=lambda x: x.expected_payout, reverse=True)

    def _select_best_combination(
        self, legs: list[ParlayLeg], count: int, strategy: str
    ) -> list[ParlayLeg]:
        """Select best combination with correlation risk management"""
        # First apply strategy-based sorting
        if strategy == "confidence":
            sorted_legs = sorted(legs, key=lambda x: x.confidence, reverse=True)
        elif strategy == "balanced":
            scored_legs = []
            for leg in legs:
                odds_factor = (
                    1 + (abs(leg.odds) / 1000) if leg.odds > 0 else 1 + (100 / abs(leg.odds))
                )
                score = leg.confidence * odds_factor
                scored_legs.append((score, leg))
            sorted_legs = [leg for _, leg in sorted(scored_legs, key=lambda x: x[0], reverse=True)]
        elif strategy == "moonshot":
            sorted_legs = sorted(legs, key=lambda x: abs(x.odds) * x.confidence, reverse=True)
        else:
            sorted_legs = legs

        # Now apply correlation risk management
        selected = []
        same_game_tracker = {}

        for leg in sorted_legs:
            if len(selected) >= count:
                break

            # Track legs per game for correlation management
            if leg.game_id not in same_game_tracker:
                same_game_tracker[leg.game_id] = []

            current_game_legs = same_game_tracker[leg.game_id]

            # Skip if would create risky correlation
            correlation_risk = False
            for existing_leg in current_game_legs:
                # Avoid spread favorite + over total (high correlation)
                if leg.bet_type == BetType.SPREAD and existing_leg.bet_type == BetType.OVER_UNDER:
                    if "+" not in leg.selection and "Over" in existing_leg.selection:
                        correlation_risk = True
                        break
                elif leg.bet_type == BetType.OVER_UNDER and existing_leg.bet_type == BetType.SPREAD:
                    if "Over" in leg.selection and "+" not in existing_leg.selection:
                        correlation_risk = True
                        break

            if not correlation_risk and len(current_game_legs) < 2:
                selected.append(leg)
                same_game_tracker[leg.game_id].append(leg)

        return selected

    def _create_mega_parlay(self, legs: list[ParlayLeg], category: str) -> MegaParlay:
        """Create complete mega parlay from selected legs"""
        total_odds = self.calculate_parlay_odds(legs)
        avg_confidence = sum(leg.confidence for leg in legs) / len(legs)

        # Kelly Criterion sizing
        edge = avg_confidence - (
            1 / (abs(total_odds) / 100 + 1)
            if total_odds > 0
            else abs(total_odds) / (abs(total_odds) + 100)
        )
        kelly_fraction = max(edge / 5, 0.005)  # Conservative Kelly
        stake = min(self.bankroll * kelly_fraction, self.bankroll * 0.05)  # Max 5% bankroll

        if total_odds > 0:
            expected_payout = stake * (total_odds / 100)
        else:
            expected_payout = stake * (100 / abs(total_odds))

        # Risk level
        if len(legs) <= 10 and avg_confidence >= 0.72:
            risk_level = "Conservative"
        elif len(legs) <= 15 and avg_confidence >= 0.65:
            risk_level = "Moderate"
        else:
            risk_level = "Aggressive"

        # Calculate true expected value for accurate assessment
        self.calculate_true_expected_value(legs)

        return MegaParlay(
            legs=legs,
            total_odds=total_odds,
            stake=stake,
            expected_payout=expected_payout,
            confidence_score=avg_confidence,
            risk_level=risk_level,
            category=category,
        )

    def display_mega_parlays(self):
        """Display all mega parlays with complete analysis"""
        print("🚀 **EQ12 MEGA PARLAY BUILDER - {self.current_date}**")
        print("=" * 100)
        print("📅 Date: {datetime.now().strftime('%A, %B %d, %Y')}")
        print("🕒 Analysis Time: {datetime.now().strftime('%H:%M:%S')}")
        print("⏰ Games After 3PM Only")
        print("💰 Bankroll: ${self.bankroll:,.2f}")

        games = self.get_all_games_after_3pm()
        print("\n🎯 **{len(games)} GAMES AVAILABLE AFTER 3PM**")
        print("=" * 100)

        for game in games:
            game_time = datetime.strptime(game.game_time, "%Y-%m-%d %H:%M").strftime("%I:%M %p")
            print(f"{game_time} | {game.away_team} @ {game.home_team} ({game.sport.value})")
            if game.spread_line and game.total_line:
                spread_team = game.home_team if game.spread_line < 0 else game.away_team
                spread_val = abs(game.spread_line)
                print(f"   Spread: {spread_team} -{spread_val} | Total: {game.total_line}")
            if game.home_ml_odds and game.away_ml_odds:
                print(
                    f"   ML: {game.home_team} {game.home_ml_odds:+d} | {game.away_team} {game.away_ml_odds:+d}"
                )
            print()

        mega_parlays = self.build_mega_parlays(20)

        print("\n💎 **TOP {len(mega_parlays)} MEGA PARLAYS (UP TO 20 LEGS)**")
        print("=" * 100)

        total_stakes = 0
        total_potential = 0

        for i, parlay in enumerate(mega_parlays[:10], 1):
            total_stakes += parlay.stake
            total_potential += parlay.expected_payout

            print(f"\n🎯 **MEGA PARLAY #{i}: {parlay.category.upper()} ({len(parlay.legs)} LEGS)**")
            print(
                f"   Odds: {parlay.total_odds:+.0f} | Stake: ${parlay.stake:.2f} | Payout: ${parlay.expected_payout:,.2f}"
            )
            print(f"   Confidence: {parlay.confidence_score:.1%} | Risk: {parlay.risk_level}")
            print("   Legs:")

            for j, leg in enumerate(parlay.legs, 1):
                # Clean up selection to remove any formatting issues
                clean_selection = self.clean_label(leg.selection)
                print(f"   {j:2d}. {clean_selection} ({leg.odds:+d}) - {leg.game.sport.value}")

            print(
                f"   Strategy: {parlay.category} approach focusing on {parlay.risk_level.lower()} risk profile"
            )

        print("\n💼 **PORTFOLIO SUMMARY**")
        print("=" * 100)
        print("💰 Total Stakes: ${total_stakes:.2f}")
        print("🎯 Total Potential Payout: ${total_potential:,.2f}")
        print("📊 Bankroll Utilization: {(total_stakes/self.bankroll)*100:.1f}%")
        print(
            f"🚀 Maximum Possible ROI: {((total_potential - total_stakes) / total_stakes) * 100:,.0f}%"
        )

        # Save to logs
        self._save_analysis(mega_parlays)

        print("\n✅ **MEGA PARLAY ANALYSIS COMPLETE**")
        print("🎉 Ready to dominate with up to 20-leg mega parlays!")

    def _save_analysis(self, parlays: list[MegaParlay]):
        """Save analysis to logs directory"""
        self.logs_dir.mkdir(exist_ok=True)

        analysis_data = {
            "date": self.current_date,
            "analysis_time": datetime.now().isoformat(),
            "total_parlays": len(parlays),
            "parlays": [],
        }

        for parlay in parlays:
            parlay_data = {
                "category": parlay.category,
                "legs_count": len(parlay.legs),
                "total_odds": parlay.total_odds,
                "stake": parlay.stake,
                "expected_payout": parlay.expected_payout,
                "confidence_score": parlay.confidence_score,
                "risk_level": parlay.risk_level,
                "legs": [
                    {
                        "selection": leg.selection,
                        "odds": leg.odds,
                        "confidence": leg.confidence,
                        "game": f"{leg.game.away_team} @ {leg.game.home_team}",
                        "sport": leg.game.sport.value,
                        "game_time": leg.game.game_time,
                    }
                    for leg in parlay.legs
                ],
            }
            analysis_data["parlays"].append(parlay_data)

        filename = f"mega_parlay_analysis_{self.current_date}.json"
        filepath = self.logs_dir / filename

        with open(filepath, "w") as f:
            json.dump(analysis_data, f, indent=2)

        print("📝 Analysis saved to: {filepath}")


def main():
    """Main execution function with CLI argument support"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Mega Parlay Builder")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD (default: today America/New_York)")
    parser.add_argument(
        "--after",
        default="15:00",
        help="HH:MM 24h cutoff (default: 15:00 for after 3 PM)",
    )
    parser.add_argument("--preview-only", action="store_true", help="Preview mode only")

    args = parser.parse_args()

    # Set global date filtering
    global TARGET_DATE, AFTER
    TARGET_DATE = args.date or None
    AFTER = args.after or "15:00"

    builder = EQ12MegaParlayBuilder()
    builder.display_mega_parlays()


if __name__ == "__main__":
    main()
