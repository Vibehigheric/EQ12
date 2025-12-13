#!/usr/bin/env python3
"""
EQ12 GODSTACK - Slate Generator
CLI: `python eq12_slate_generator.py --league MLB --after 15:00 --max-legs 6`
Emits 3 presets: 'Pitching Duel', 'Power Stack', 'Balanced Script'

Core Features:
- One-command slate generation for daily betting
- Pre-built SGP templates (Pitching Duel, Power Stack, Balanced)
- Time-based filtering for games after specified time
- Customizable leg limits and risk parameters
- Integration with existing odds and correlation engines
- Alternative line suggestions for each primary SGP
"""

import argparse
import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/slate_generator.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class SlateTemplate(Enum):
    """Pre-built SGP template types"""

    PITCHING_DUEL = "pitching_duel"
    POWER_STACK = "power_stack"
    BALANCED_SCRIPT = "balanced_script"
    CONTRARIAN_PLAY = "contrarian_play"
    WEATHER_NARRATIVE = "weather_narrative"


@dataclass
class SlateGame:
    """Individual game in the slate"""

    game_id: str
    home_team: str
    away_team: str
    start_time: datetime

    # Pitchers
    home_pitcher: str
    away_pitcher: str
    home_pitcher_stats: dict[str, Any]
    away_pitcher_stats: dict[str, Any]

    # Game conditions
    park_factors: dict[str, float]
    weather_conditions: dict[str, Any]

    # Betting markets
    moneyline_odds: dict[str, int]  # "home", "away"
    total_line: float
    total_odds: dict[str, int]  # "over", "under"

    # Template suitability scores
    template_scores: dict[SlateTemplate, float]


@dataclass
class SGPTemplate:
    """Template for generating SGPs"""

    template_name: str
    template_type: SlateTemplate

    # Core narrative
    narrative_description: str
    target_scenarios: list[str]

    # Leg requirements
    required_leg_types: list[str]
    optional_leg_types: list[str]
    max_legs: int
    min_confidence: float

    # Risk parameters
    max_correlation_risk: float
    target_odds_range: Tuple[int, int]  # Min, Max American odds

    # Selection criteria
    pitcher_requirements: dict[str, Any]
    team_requirements: dict[str, Any]
    game_requirements: dict[str, Any]


@dataclass
class GeneratedSGP:
    """Complete generated SGP with alternatives"""

    sgp_id: str
    template_used: SlateTemplate
    primary_game: SlateGame

    # SGP details
    description: str
    narrative: str
    legs: list[dict[str, Any]]

    # Odds and value
    combined_odds: int
    expected_value: float
    confidence_score: float

    # Alternative versions
    alternate_versions: list[dict[str, Any]]

    # Risk assessment
    risk_factors: list[str]
    correlation_summary: str

    # Metadata
    generation_timestamp: datetime
    expires_at: datetime


class SlateGenerator:
    """Main slate generation engine"""

    def __init__(self):
        self.templates = self._initialize_templates()
        self.current_slate = []

        logger.info("SlateGenerator initialized with templates")

    def _initialize_templates(self) -> dict[SlateTemplate, SGPTemplate]:
        """Initialize SGP templates"""

        templates = {
            SlateTemplate.PITCHING_DUEL: SGPTemplate(
                template_name="Pitcher's Duel Stack",
                template_type=SlateTemplate.PITCHING_DUEL,
                narrative_description="Both starters dominate with strikeouts in low-scoring game",
                target_scenarios=[
                    "Both pitchers record 7+ strikeouts",
                    "Game stays under total",
                    "Quality start for both pitchers",
                ],
                required_leg_types=["game_total_under", "pitcher_strikeouts_over"],
                optional_leg_types=[
                    "team_total_under",
                    "opposing_pitcher_strikeouts_over",
                ],
                max_legs=4,
                min_confidence=0.75,
                max_correlation_risk=0.4,
                target_odds_range=(200, 800),
                pitcher_requirements={
                    "min_k_per_9": 8.0,
                    "max_era": 4.00,
                    "min_innings_season": 100,
                },
                team_requirements={"max_runs_per_game": 5.5},
                game_requirements={"max_total_line": 9.0, "weather_wind_max": 15},
            ),
            SlateTemplate.POWER_STACK: SGPTemplate(
                template_name="Power Surge Stack",
                template_type=SlateTemplate.POWER_STACK,
                narrative_description="Offensive explosion with home runs and high scoring",
                target_scenarios=[
                    "Multiple home runs hit",
                    "Game goes over total",
                    "High-powered offense dominates",
                ],
                required_leg_types=["game_total_over", "home_run_props_over"],
                optional_leg_types=[
                    "team_total_over",
                    "hit_props_over",
                    "runs_scored_over",
                ],
                max_legs=5,
                min_confidence=0.70,
                max_correlation_risk=0.5,
                target_odds_range=(150, 600),
                pitcher_requirements={
                    "max_k_per_9": 10.0,  # Avoid strikeout pitchers
                    "min_hr_per_9": 1.0,  # Target homer-prone pitchers
                },
                team_requirements={
                    "min_runs_per_game": 4.5,
                    "min_home_runs_per_game": 1.0,
                },
                game_requirements={"min_total_line": 8.0, "hitter_friendly_park": True},
            ),
            SlateTemplate.BALANCED_SCRIPT: SGPTemplate(
                template_name="Balanced Game Script",
                template_type=SlateTemplate.BALANCED_SCRIPT,
                narrative_description="Mixed approach with team success and moderate scoring",
                target_scenarios=[
                    "Favorite covers with moderate scoring",
                    "Key players produce in team win",
                    "Reasonable scoring environment",
                ],
                required_leg_types=["moneyline", "team_performance"],
                optional_leg_types=["player_props", "game_total", "team_total"],
                max_legs=4,
                min_confidence=0.65,
                max_correlation_risk=0.6,
                target_odds_range=(120, 400),
                pitcher_requirements={},  # More flexible
                team_requirements={"min_win_percentage": 0.45},
                game_requirements={"total_line_range": (7.0, 10.5)},
            ),
            SlateTemplate.CONTRARIAN_PLAY: SGPTemplate(
                template_name="Contrarian Value Play",
                template_type=SlateTemplate.CONTRARIAN_PLAY,
                narrative_description="Fade the public with underdog or contrarian angle",
                target_scenarios=[
                    "Road underdog covers or wins",
                    "Public overvalues favorite",
                    "Market inefficiency exploitation",
                ],
                required_leg_types=["underdog_value"],
                optional_leg_types=["road_team_props", "under_plays", "fade_public"],
                max_legs=3,
                min_confidence=0.60,
                max_correlation_risk=0.3,
                target_odds_range=(180, 1000),
                pitcher_requirements={"undervalued_starter": True},
                team_requirements={"public_fade_candidate": True},
                game_requirements={"line_movement_favorable": True},
            ),
        }

        return templates

    async def fetch_available_games(
        self, league: str = "MLB", after_time: datetime | None = None
    ) -> list[SlateGame]:
        """Fetch available games for slate generation"""

        logger.info(f"Fetching {league} games after {after_time}")

        # In real implementation, this would integrate with eq12_odds_ingest.py
        # For demo, create sample games

        sample_games = [
            SlateGame(
                game_id="game_001",
                home_team="TOR",
                away_team="NYY",
                start_time=datetime.now(UTC) + timedelta(hours=2),
                home_pitcher="Chris Bassitt",
                away_pitcher="Gerrit Cole",
                home_pitcher_stats={
                    "era": 3.45,
                    "k_per_9": 8.8,
                    "whip": 1.18,
                    "innings_pitched": 165,
                    "hr_per_9": 1.1,
                },
                away_pitcher_stats={
                    "era": 2.75,
                    "k_per_9": 11.2,
                    "whip": 1.05,
                    "innings_pitched": 180,
                    "hr_per_9": 0.8,
                },
                park_factors={"runs_factor": 0.98, "hr_factor": 0.95},
                weather_conditions={
                    "temperature": 72,
                    "wind_speed": 6,
                    "wind_direction": "calm",
                },
                moneyline_odds={"home": +115, "away": -135},
                total_line=8.0,
                total_odds={"over": -110, "under": -110},
                template_scores={},
            ),
            SlateGame(
                game_id="game_002",
                home_team="SEA",
                away_team="DET",
                start_time=datetime.now(UTC) + timedelta(hours=5),
                home_pitcher="Logan Gilbert",
                away_pitcher="Tarik Skubal",
                home_pitcher_stats={
                    "era": 3.21,
                    "k_per_9": 9.5,
                    "whip": 1.12,
                    "innings_pitched": 170,
                    "hr_per_9": 1.0,
                },
                away_pitcher_stats={
                    "era": 2.39,
                    "k_per_9": 11.8,
                    "whip": 0.98,
                    "innings_pitched": 192,
                    "hr_per_9": 0.7,
                },
                park_factors={"runs_factor": 0.94, "hr_factor": 0.88},
                weather_conditions={
                    "temperature": 68,
                    "wind_speed": 8,
                    "wind_direction": "in",
                },
                moneyline_odds={"home": +108, "away": -118},
                total_line=6.5,
                total_odds={"over": +105, "under": -125},
                template_scores={},
            ),
        ]

        # Filter by time if specified
        if after_time:
            sample_games = [game for game in sample_games if game.start_time > after_time]

        # Score games for each template
        for game in sample_games:
            game.template_scores = self._score_game_for_templates(game)

        return sample_games

    def _score_game_for_templates(self, game: SlateGame) -> dict[SlateTemplate, float]:
        """Score how well a game fits each template"""

        scores = {}

        # Pitching Duel scoring
        pitcher_duel_score = 0.0

        # High strikeout rates boost score
        avg_k_rate = (
            game.home_pitcher_stats.get("k_per_9", 8) + game.away_pitcher_stats.get("k_per_9", 8)
        ) / 2
        if avg_k_rate > 9.5:
            pitcher_duel_score += 0.3
        elif avg_k_rate > 8.5:
            pitcher_duel_score += 0.2

        # Low total supports duel
        if game.total_line <= 7.5:
            pitcher_duel_score += 0.3
        elif game.total_line <= 8.5:
            pitcher_duel_score += 0.2

        # Good ERAs support duel
        avg_era = (
            game.home_pitcher_stats.get("era", 4.5) + game.away_pitcher_stats.get("era", 4.5)
        ) / 2
        if avg_era < 3.5:
            pitcher_duel_score += 0.2

        # Pitcher friendly park
        runs_factor = game.park_factors.get("runs_factor", 1.0)
        if runs_factor < 0.98:
            pitcher_duel_score += 0.1

        # Calm weather helps pitchers
        wind_speed = game.weather_conditions.get("wind_speed", 10)
        if wind_speed < 8:
            pitcher_duel_score += 0.1

        scores[SlateTemplate.PITCHING_DUEL] = min(1.0, pitcher_duel_score)

        # Power Stack scoring
        power_stack_score = 0.0

        # High total supports power
        if game.total_line >= 9.0:
            power_stack_score += 0.3
        elif game.total_line >= 8.0:
            power_stack_score += 0.2

        # Hitter-friendly park
        hr_factor = game.park_factors.get("hr_factor", 1.0)
        if hr_factor > 1.05:
            power_stack_score += 0.3
        elif hr_factor > 1.02:
            power_stack_score += 0.2

        # Wind helping offense
        wind_direction = game.weather_conditions.get("wind_direction", "calm")
        if wind_direction == "out":
            power_stack_score += 0.2

        # Moderate pitcher quality (not too dominant)
        if 3.5 < avg_era < 4.5:
            power_stack_score += 0.2

        scores[SlateTemplate.POWER_STACK] = min(1.0, power_stack_score)

        # Balanced Script scoring (always moderate fit)
        balanced_score = 0.6

        # Reasonable total range
        if 7.5 <= game.total_line <= 9.0:
            balanced_score += 0.2

        # Competitive game (close moneyline)
        ml_home = abs(game.moneyline_odds["home"])
        ml_away = abs(game.moneyline_odds["away"])
        if max(ml_home, ml_away) < 150:
            balanced_score += 0.2

        scores[SlateTemplate.BALANCED_SCRIPT] = min(1.0, balanced_score)

        # Contrarian Play scoring
        contrarian_score = 0.0

        # Road underdog gets points
        if game.moneyline_odds["away"] > 0:
            contrarian_score += 0.4

        # Big favorite to fade
        if ml_home < -150 or ml_away < -150:
            contrarian_score += 0.3

        # Under in high total game (contrarian)
        if game.total_line > 8.5 and game.total_odds["under"] > 0:
            contrarian_score += 0.3

        scores[SlateTemplate.CONTRARIAN_PLAY] = min(1.0, contrarian_score)

        return scores

    def generate_sgp_from_template(
        self, game: SlateGame, template: SGPTemplate
    ) -> GeneratedSGP | None:
        """Generate an SGP from a game and template"""

        logger.info(f"Generating {template.template_name} for {game.away_team}@{game.home_team}")

        # Check if game meets template requirements
        template_score = game.template_scores.get(template.template_type, 0.0)
        if template_score < 0.4:
            logger.info(f"Game score {template_score:.2f} too low for {template.template_name}")
            return None

        # Generate legs based on template
        legs = []

        if template.template_type == SlateTemplate.PITCHING_DUEL:
            legs = self._generate_pitching_duel_legs(game, template)
        elif template.template_type == SlateTemplate.POWER_STACK:
            legs = self._generate_power_stack_legs(game, template)
        elif template.template_type == SlateTemplate.BALANCED_SCRIPT:
            legs = self._generate_balanced_legs(game, template)
        elif template.template_type == SlateTemplate.CONTRARIAN_PLAY:
            legs = self._generate_contrarian_legs(game, template)

        if not legs:
            return None

        # Calculate combined odds (simplified)
        combined_prob = 1.0
        for leg in legs:
            combined_prob *= leg.get("true_probability", 0.5)

        if combined_prob > 0.5:
            combined_odds = int(-100 / (1 / combined_prob - 1))
        else:
            combined_odds = int(100 * (1 / combined_prob - 1))

        # Check if odds are in target range
        min_odds, max_odds = template.target_odds_range
        if not (min_odds <= abs(combined_odds) <= max_odds):
            logger.info(f"Odds {combined_odds} outside target range {min_odds}-{max_odds}")
            return None

        # Calculate EV (simplified)
        payout_multiple = combined_odds / 100 if combined_odds > 0 else 100 / abs(combined_odds)

        expected_value = (combined_prob * payout_multiple) - (1 - combined_prob)

        # Generate alternatives
        alternatives = self._generate_alternatives(legs, game, template)

        # Risk assessment
        risk_factors = self._assess_risk_factors(legs, game, template)

        sgp_id = f"sgp_{template.template_type.value}_{game.game_id}"

        return GeneratedSGP(
            sgp_id=sgp_id,
            template_used=template.template_type,
            primary_game=game,
            description=f"{template.template_name}: {game.away_team} @ {game.home_team}",
            narrative=template.narrative_description,
            legs=legs,
            combined_odds=combined_odds,
            expected_value=expected_value,
            confidence_score=template_score * 0.8,  # Slight discount from game score
            alternate_versions=alternatives,
            risk_factors=risk_factors,
            correlation_summary=self._generate_correlation_summary(legs),
            generation_timestamp=datetime.now(UTC),
            expires_at=game.start_time - timedelta(minutes=30),
        )

    def _generate_pitching_duel_legs(
        self, game: SlateGame, template: SGPTemplate
    ) -> list[dict[str, Any]]:
        """Generate legs for pitching duel template"""

        legs = [
            {
                "leg_type": "total",
                "selection": "under",
                "line": game.total_line,
                "odds": game.total_odds["under"],
                "description": f"Game Total Under {game.total_line}",
                "true_probability": 0.55,
                "reasoning": "Both quality starters support low-scoring game",
            },
            {
                "leg_type": "player_prop",
                "selection": "over",
                "line": 6.5,
                "odds": -115,
                "player": game.away_pitcher,
                "team": game.away_team,
                "description": f"{game.away_pitcher} Over 6.5 Strikeouts",
                "true_probability": 0.60,
                "reasoning": "High strikeout rate pitcher in favorable matchup",
            },
        ]

        # Add home pitcher if both have good K rates
        home_k_rate = game.home_pitcher_stats.get("k_per_9", 8)
        if home_k_rate > 8.5:
            legs.append(
                {
                    "leg_type": "player_prop",
                    "selection": "over",
                    "line": 6.5,
                    "odds": -120,
                    "player": game.home_pitcher,
                    "team": game.home_team,
                    "description": f"{game.home_pitcher} Over 6.5 Strikeouts",
                    "true_probability": 0.58,
                    "reasoning": "Home pitcher also projects for strikeouts",
                }
            )

        return legs

    def _generate_power_stack_legs(
        self, game: SlateGame, template: SGPTemplate
    ) -> list[dict[str, Any]]:
        """Generate legs for power stack template"""

        legs = [
            {
                "leg_type": "total",
                "selection": "over",
                "line": game.total_line,
                "odds": game.total_odds["over"],
                "description": f"Game Total Over {game.total_line}",
                "true_probability": 0.52,
                "reasoning": "Offensive environment supports higher scoring",
            },
            {
                "leg_type": "player_prop",
                "selection": "over",
                "line": 0.5,
                "odds": +185,
                "player": "Team Home Run",
                "description": "Any Player Home Run",
                "true_probability": 0.65,
                "reasoning": "Hitter-friendly conditions increase HR probability",
            },
        ]

        return legs

    def _generate_balanced_legs(
        self, game: SlateGame, template: SGPTemplate
    ) -> list[dict[str, Any]]:
        """Generate legs for balanced template"""

        # Pick the moderate favorite
        if game.moneyline_odds["home"] < 0:
            favorite_team = game.home_team
            favorite_odds = game.moneyline_odds["home"]
        else:
            favorite_team = game.away_team
            favorite_odds = game.moneyline_odds["away"]

        legs = [
            {
                "leg_type": "moneyline",
                "selection": "win",
                "team": favorite_team,
                "odds": favorite_odds,
                "description": f"{favorite_team} Moneyline",
                "true_probability": 0.58,
                "reasoning": "Slight favorite in competitive matchup",
            }
        ]

        # Add a moderate total play
        if game.total_line > 8.0:
            legs.append(
                {
                    "leg_type": "total",
                    "selection": "under",
                    "line": game.total_line,
                    "odds": game.total_odds["under"],
                    "description": f"Game Total Under {game.total_line}",
                    "true_probability": 0.53,
                    "reasoning": "Moderate scoring expectation",
                }
            )

        return legs

    def _generate_contrarian_legs(
        self, game: SlateGame, template: SGPTemplate
    ) -> list[dict[str, Any]]:
        """Generate legs for contrarian template"""

        legs = []

        # Road underdog if available
        if game.moneyline_odds["away"] > 0:
            legs.append(
                {
                    "leg_type": "moneyline",
                    "selection": "win",
                    "team": game.away_team,
                    "odds": game.moneyline_odds["away"],
                    "description": f"{game.away_team} ML (Road Dog)",
                    "true_probability": 0.42,
                    "reasoning": "Road underdog with value against public favorite",
                }
            )

        # Contrarian total play
        if game.total_line > 8.5:
            legs.append(
                {
                    "leg_type": "total",
                    "selection": "under",
                    "line": game.total_line,
                    "odds": game.total_odds["under"],
                    "description": f"Game Total Under {game.total_line}",
                    "true_probability": 0.48,
                    "reasoning": "Fade public over betting in high total game",
                }
            )

        return legs

    def _generate_alternatives(
        self, base_legs: list[dict[str, Any]], game: SlateGame, template: SGPTemplate
    ) -> list[dict[str, Any]]:
        """Generate alternative versions of the SGP"""

        alternatives = []

        # Alternative line versions
        for leg in base_legs:
            if leg["leg_type"] == "total" and "line" in leg:
                # Alternative total lines
                base_line = leg["line"]
                alt_lines = [base_line - 0.5, base_line + 0.5]

                for alt_line in alt_lines:
                    if alt_line > 0:
                        alternatives.append(
                            {
                                "type": "alternative_line",
                                "description": f"Alt: Game Total {leg['selection']} {alt_line}",
                                "change": f"Line {base_line} → {alt_line}",
                                "odds_impact": "+15 to +25",
                            }
                        )

            elif (
                leg["leg_type"] == "player_prop"
                and "strikeouts" in leg.get("description", "").lower()
            ):
                # Alternative K lines
                base_line = leg.get("line", 6.5)
                alt_k_lines = [base_line - 0.5, base_line + 0.5]

                for alt_line in alt_k_lines:
                    if alt_line > 0:
                        alternatives.append(
                            {
                                "type": "alternative_player_line",
                                "description": f"Alt: {leg.get('player', 'Player')} {leg['selection']} {alt_line} Ks",
                                "change": f"Line {base_line} → {alt_line}",
                                "odds_impact": "+10 to +30",
                            }
                        )

        # Template-specific alternatives
        if template.template_type == SlateTemplate.PITCHING_DUEL:
            alternatives.append(
                {
                    "type": "template_variation",
                    "description": "Add team totals under for both teams",
                    "change": "More legs, higher payout",
                    "odds_impact": "+150 to +300",
                }
            )

        return alternatives[:3]  # Limit to 3 alternatives

    def _assess_risk_factors(
        self, legs: list[dict[str, Any]], game: SlateGame, template: SGPTemplate
    ) -> list[str]:
        """Assess risk factors for the SGP"""

        risk_factors = []

        # Weather risks
        wind_speed = game.weather_conditions.get("wind_speed", 0)
        if wind_speed > 15:
            risk_factors.append("High wind conditions could affect play")

        # Pitcher risks
        for leg in legs:
            if (
                leg.get("leg_type") == "player_prop"
                and "strikeouts" in leg.get("description", "").lower()
            ):
                risk_factors.append("Pitcher could be pulled early or struggle with command")

        # Correlation risks
        if len(legs) > 3:
            risk_factors.append("Multiple correlated legs increase overall risk")

        # Template-specific risks
        if template.template_type == SlateTemplate.PITCHING_DUEL:
            risk_factors.append("Offense could break out despite pitching matchup")
        elif template.template_type == SlateTemplate.POWER_STACK:
            risk_factors.append("Pitchers could dominate despite offensive expectations")

        return risk_factors

    def _generate_correlation_summary(self, legs: list[dict[str, Any]]) -> str:
        """Generate correlation summary for legs"""

        correlation_types = []

        # Check for pitcher + total correlations
        has_pitcher_props = any("strikeouts" in leg.get("description", "").lower() for leg in legs)
        has_total_under = any(
            leg.get("selection") == "under" and leg.get("leg_type") == "total" for leg in legs
        )

        if has_pitcher_props and has_total_under:
            correlation_types.append("Pitcher strikeouts correlate positively with game under")

        # Check for team performance correlations
        has_moneyline = any(leg.get("leg_type") == "moneyline" for leg in legs)
        has_team_props = any("team" in leg.get("description", "").lower() for leg in legs)

        if has_moneyline and has_team_props:
            correlation_types.append("Team success correlates with individual performance")

        if not correlation_types:
            return "Legs are largely independent with minimal correlation"

        return "; ".join(correlation_types)

    async def generate_daily_slate(
        self, league: str = "MLB", after_time: str | None = None, max_legs: int = 6
    ) -> list[GeneratedSGP]:
        """Generate complete daily slate with all templates"""

        logger.info(f"Generating daily slate for {league}")

        # Parse after_time if provided
        if after_time:
            try:
                # Parse time like "15:00" or "3:00 PM"
                if ":" in after_time:
                    if "PM" in after_time.upper() or "AM" in after_time.upper():
                        time_obj = datetime.strptime(after_time.upper(), "%I:%M %p").time()
                    else:
                        time_obj = datetime.strptime(after_time, "%H:%M").time()

                    # Combine with today's date
                    today = datetime.now(UTC).date()
                    after_datetime = datetime.combine(today, time_obj, UTC)
                else:
                    after_datetime = None
            except ValueError:
                logger.warning(f"Could not parse time: {after_time}")
                after_datetime = None
        else:
            after_datetime = None

        # Fetch available games
        games = await self.fetch_available_games(league, after_datetime)

        if not games:
            logger.warning("No games found for slate generation")
            return []

        logger.info(f"Found {len(games)} games for slate generation")

        # Generate SGPs for each template and game combination
        generated_sgps = []

        for template_type, template in self.templates.items():
            logger.info(f"Generating {template.template_name} SGPs")

            # Find best game for this template
            best_game = None
            best_score = 0.0

            for game in games:
                score = game.template_scores.get(template_type, 0.0)
                if score > best_score:
                    best_score = score
                    best_game = game

            # Generate SGP for best game
            if best_game and best_score > 0.4:
                sgp = self.generate_sgp_from_template(best_game, template)
                if sgp:
                    generated_sgps.append(sgp)
                    logger.info(f"Generated {template.template_name}: {sgp.combined_odds:+d} odds")

        # Sort by confidence score
        generated_sgps.sort(key=lambda x: x.confidence_score, reverse=True)

        logger.info(f"Generated {len(generated_sgps)} SGPs for daily slate")
        return generated_sgps

    def export_slate(self, sgps: list[GeneratedSGP], output_path: str | None = None) -> str:
        """Export slate to JSON file"""

        if not output_path:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            output_path = f"C:/EQ12/logs/daily_slate_{timestamp}.json"

        slate_data = {
            "slate_metadata": {
                "generation_time": datetime.now(UTC).isoformat(),
                "total_sgps": len(sgps),
                "league": "MLB",
            },
            "sgps": [asdict(sgp) for sgp in sgps],
        }

        with open(output_path, "w") as f:
            json.dump(slate_data, f, indent=2, default=str)

        logger.info(f"Slate exported to {output_path}")
        return output_path


async def main():
    """Main CLI interface"""

    parser = argparse.ArgumentParser(description="EQ12 Slate Generator")
    parser.add_argument("--league", default="MLB", help="League to generate slate for")
    parser.add_argument(
        "--after", help="Generate for games after this time (e.g., '15:00', '3:00 PM')"
    )
    parser.add_argument("--max-legs", type=int, default=6, help="Maximum legs per SGP")
    parser.add_argument("--export", action="store_true", help="Export slate to file")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize slate generator
    generator = SlateGenerator()

    print(f"🎯 EQ12 SLATE GENERATOR - {args.league.upper()}")

    # Generate daily slate
    sgps = await generator.generate_daily_slate(
        league=args.league, after_time=args.after, max_legs=args.max_legs
    )

    if not sgps:
        print("❌ No SGPs generated for today's slate")
        return

    print(f"\n🏆 DAILY SLATE GENERATED: {len(sgps)} SGPs")

    for i, sgp in enumerate(sgps, 1):
        print(f"\n{i}. {sgp.description}")
        print(f"   Template: {sgp.template_used.value.replace('_', ' ').title()}")
        print(f"   Odds: {sgp.combined_odds:+d} | EV: {sgp.expected_value:+.4f}")
        print(f"   Confidence: {sgp.confidence_score:.2f}")
        print(f"   Narrative: {sgp.narrative}")

        print("   Legs:")
        for leg in sgp.legs:
            odds_str = f"{leg['odds']:+d}" if leg["odds"] >= 0 else str(leg["odds"])
            print(f"      • {leg['description']} ({odds_str})")

        if sgp.alternate_versions:
            print("   Alternatives:")
            for alt in sgp.alternate_versions[:2]:
                print(f"      • {alt['description']} ({alt['odds_impact']})")

        print(f"   Expires: {sgp.expires_at.strftime('%H:%M UTC')}")

    # Export if requested
    if args.export:
        export_path = generator.export_slate(sgps)
        print(f"\n💾 Slate exported to: {export_path}")

    print("\n📋 SLATE SUMMARY:")
    print(f"   Total SGPs: {len(sgps)}")
    print(f"   Average Confidence: {sum(sgp.confidence_score for sgp in sgps) / len(sgps):.2f}")
    print(f"   Templates Used: {len({sgp.template_used for sgp in sgps})}")


if __name__ == "__main__":
    asyncio.run(main())
