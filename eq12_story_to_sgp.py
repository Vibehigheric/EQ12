#!/usr/bin/env python3
"""
EQ12 GODSTACK - Story-to-SGP Converter
CLI: `python eq12_story_to_sgp.py --story "Cole strikes out 8+ and Yankees win 5-3"`
Natural language → structured SGP legs with betting logic

Core Features:
- Parse natural language betting stories into SGP legs
- Extract player names, team names, stat thresholds, game outcomes
- Map to actual betting markets and odds
- Validate correlation and coherence of story elements
- Suggest alternative wordings and leg combinations
- Integration with player research and correlation engines
"""

import argparse
import asyncio
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/story_to_sgp.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class MarketType(Enum):
    """Available betting market types"""

    MONEYLINE = "moneyline"
    TOTAL = "total"
    TEAM_TOTAL = "team_total"
    PLAYER_STRIKEOUTS = "player_strikeouts"
    PLAYER_HITS = "player_hits"
    PLAYER_RUNS = "player_runs"
    PLAYER_RBIS = "player_rbis"
    PLAYER_HOME_RUNS = "player_home_runs"
    PITCHER_WINS = "pitcher_wins"
    PITCHER_EARNED_RUNS = "pitcher_earned_runs"
    GAME_RESULT = "game_result"
    INNING_RESULT = "inning_result"


@dataclass
class StoryElement:
    """Individual element extracted from betting story"""

    element_type: str
    raw_text: str
    confidence: float

    # Player information
    player_name: str | None = None
    team_name: str | None = None

    # Stat information
    stat_type: str | None = None
    threshold: float | None = None
    comparison: str | None = None  # "over", "under", "exactly"

    # Game information
    game_outcome: str | None = None
    score: tuple[int, int] | None = None

    # Betting market mapping
    market_type: MarketType | None = None
    suggested_line: float | None = None
    estimated_odds: int | None = None


@dataclass
class ParsedStory:
    """Complete parsed betting story"""

    original_story: str
    parsing_confidence: float

    # Extracted elements
    elements: list[StoryElement]
    primary_game: str | None = None
    teams_involved: list[str] = None

    # Story classification
    story_type: str = "unknown"  # "player_performance", "game_script", "team_total", etc.
    narrative_theme: str = ""

    # Validation
    coherence_score: float = 0.0
    correlation_warnings: list[str] = None

    # SGP conversion
    suggested_legs: list[dict[str, Any]] = None
    alternative_interpretations: list[str] = None


@dataclass
class SGPLeg:
    """SGP leg generated from story element"""

    leg_id: str
    source_element: StoryElement

    # Betting details
    market_type: MarketType
    selection: str
    line: float | None
    odds: int

    # Descriptive
    description: str
    reasoning: str

    # Validation
    confidence: float
    risk_factors: list[str]

    # Market availability
    available_books: list[str]
    line_variations: dict[str, float]


class StoryParser:
    """Natural language story parser"""

    def __init__(self):
        self.player_patterns = self._initialize_player_patterns()
        self.stat_patterns = self._initialize_stat_patterns()
        self.team_patterns = self._initialize_team_patterns()
        self.score_patterns = self._initialize_score_patterns()

        logger.info("StoryParser initialized with patterns")

    def _initialize_player_patterns(self) -> list[tuple[re.Pattern, str]]:
        """Initialize regex patterns for player names"""

        patterns = [
            # Full names
            (re.compile(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b"), "full_name"),
            # Last names with common first name indicators
            (
                re.compile(r"\b(Cole|Judge|Ohtani|Trout|Betts|Freeman|Altuve|Verlander)\b"),
                "lastname_star",
            ),
            # Pitcher indicators
            (
                re.compile(r"\b([A-Z][a-z]+)\s+(?:strikes out|fans|Ks|pitches|throws)\b"),
                "pitcher_context",
            ),
            # Batter indicators
            (
                re.compile(r"\b([A-Z][a-z]+)\s+(?:hits|homers|drives in|scores|gets)\b"),
                "batter_context",
            ),
        ]

        return patterns

    def _initialize_stat_patterns(self) -> list[tuple[re.Pattern, dict[str, Any]]]:
        """Initialize regex patterns for stats and thresholds"""

        patterns = [
            # Strikeouts
            (
                re.compile(r"(?:strikes out|fans|Ks?)\s+(\d+)\+?"),
                {"stat": "strikeouts", "market": MarketType.PLAYER_STRIKEOUTS},
            ),
            (
                re.compile(r"(\d+)\+?\s+(?:strikeouts|Ks?)"),
                {"stat": "strikeouts", "market": MarketType.PLAYER_STRIKEOUTS},
            ),
            # Hits
            (
                re.compile(r"(\d+)\+?\s+hits?"),
                {"stat": "hits", "market": MarketType.PLAYER_HITS},
            ),
            (
                re.compile(r"hits?\s+(\d+)\+?"),
                {"stat": "hits", "market": MarketType.PLAYER_HITS},
            ),
            # Home runs
            (
                re.compile(r"(\d+)?\s*(?:home runs?|homers?|HRs?)"),
                {"stat": "home_runs", "market": MarketType.PLAYER_HOME_RUNS},
            ),
            # RBIs
            (
                re.compile(r"(?:drives in|RBIs?)\s+(\d+)\+?"),
                {"stat": "rbis", "market": MarketType.PLAYER_RBIS},
            ),
            (
                re.compile(r"(\d+)\+?\s+RBIs?"),
                {"stat": "rbis", "market": MarketType.PLAYER_RBIS},
            ),
            # Runs scored
            (
                re.compile(r"scores\s+(\d+)\+?"),
                {"stat": "runs", "market": MarketType.PLAYER_RUNS},
            ),
            (
                re.compile(r"(\d+)\+?\s+runs?"),
                {"stat": "runs", "market": MarketType.PLAYER_RUNS},
            ),
        ]

        return patterns

    def _initialize_team_patterns(self) -> dict[str, list[str]]:
        """Initialize team name patterns and aliases"""

        teams = {
            "Yankees": ["Yankees", "NYY", "New York Yankees", "Yanks"],
            "Red Sox": ["Red Sox", "BOS", "Boston Red Sox", "Sox"],
            "Blue Jays": ["Blue Jays", "TOR", "Toronto Blue Jays", "Jays"],
            "Rays": ["Rays", "TB", "Tampa Bay Rays"],
            "Orioles": ["Orioles", "BAL", "Baltimore Orioles", "Os"],
            "Astros": ["Astros", "HOU", "Houston Astros"],
            "Rangers": ["Rangers", "TEX", "Texas Rangers"],
            "Angels": ["Angels", "LAA", "Los Angeles Angels"],
            "Mariners": ["Mariners", "SEA", "Seattle Mariners"],
            "Athletics": ["Athletics", "OAK", "Oakland Athletics", "As"],
            "Guardians": ["Guardians", "CLE", "Cleveland Guardians"],
            "Twins": ["Twins", "MIN", "Minnesota Twins"],
            "Tigers": ["Tigers", "DET", "Detroit Tigers"],
            "Royals": ["Royals", "KC", "Kansas City Royals"],
            "White Sox": ["White Sox", "CWS", "Chicago White Sox"],
            "Braves": ["Braves", "ATL", "Atlanta Braves"],
            "Phillies": ["Phillies", "PHI", "Philadelphia Phillies"],
            "Mets": ["Mets", "NYM", "New York Mets"],
            "Marlins": ["Marlins", "MIA", "Miami Marlins"],
            "Nationals": ["Nationals", "WSN", "Washington Nationals", "Nats"],
            "Dodgers": ["Dodgers", "LAD", "Los Angeles Dodgers"],
            "Padres": ["Padres", "SD", "San Diego Padres"],
            "Giants": ["Giants", "SF", "San Francisco Giants"],
            "Diamondbacks": ["Diamondbacks", "AZ", "Arizona Diamondbacks", "Dbacks"],
            "Rockies": ["Rockies", "COL", "Colorado Rockies"],
            "Cubs": ["Cubs", "CHC", "Chicago Cubs"],
            "Cardinals": ["Cardinals", "STL", "St. Louis Cardinals"],
            "Brewers": ["Brewers", "MIL", "Milwaukee Brewers"],
            "Pirates": ["Pirates", "PIT", "Pittsburgh Pirates"],
            "Reds": ["Reds", "CIN", "Cincinnati Reds"],
        }

        return teams

    def _initialize_score_patterns(self) -> list[tuple[re.Pattern, str]]:
        """Initialize score and game result patterns"""

        patterns = [
            # Exact scores
            (re.compile(r"\b(\d+)-(\d+)\b"), "exact_score"),
            (re.compile(r"wins?\s+(\d+)\s+to\s+(\d+)"), "score_description"),
            # Win/loss
            (re.compile(r"\b(wins?|beats?|defeats?)\b"), "team_wins"),
            (re.compile(r"\b(loses?|falls to)\b"), "team_loses"),
            # Total scoring
            (re.compile(r"(?:total|combined)\s+(\d+)\+?\s+runs?"), "game_total"),
            (re.compile(r"(?:over|under)\s+(\d+\.5|\d+)\s+runs?"), "total_bet"),
        ]

        return patterns

    def parse_story(self, story: str) -> ParsedStory:
        """Parse a betting story into structured elements"""

        logger.info(f"Parsing story: {story}")

        elements = []

        # Extract players
        player_elements = self._extract_players(story)
        elements.extend(player_elements)

        # Extract stats
        stat_elements = self._extract_stats(story, player_elements)
        elements.extend(stat_elements)

        # Extract teams
        team_elements = self._extract_teams(story)
        elements.extend(team_elements)

        # Extract scores and outcomes
        outcome_elements = self._extract_outcomes(story)
        elements.extend(outcome_elements)

        # Calculate parsing confidence
        confidence = self._calculate_confidence(story, elements)

        # Classify story type
        story_type, narrative = self._classify_story(elements)

        # Extract teams involved
        teams = list({elem.team_name for elem in elements if elem.team_name})

        parsed_story = ParsedStory(
            original_story=story,
            parsing_confidence=confidence,
            elements=elements,
            teams_involved=teams,
            story_type=story_type,
            narrative_theme=narrative,
        )

        # Validate coherence
        parsed_story.coherence_score = self._validate_coherence(parsed_story)
        parsed_story.correlation_warnings = self._check_correlations(parsed_story)

        logger.info(f"Parsed {len(elements)} elements with {confidence:.2f} confidence")

        return parsed_story

    def _extract_players(self, story: str) -> list[StoryElement]:
        """Extract player mentions from story"""

        elements = []

        for pattern, pattern_type in self.player_patterns:
            matches = pattern.finditer(story)

            for match in matches:
                player_name = match.group(1).strip()

                # Skip common words that might match
                if player_name.lower() in ["the", "and", "win", "game", "team"]:
                    continue

                confidence = 0.8 if pattern_type == "full_name" else 0.6

                element = StoryElement(
                    element_type="player",
                    raw_text=match.group(0),
                    confidence=confidence,
                    player_name=player_name,
                )

                elements.append(element)

        return elements

    def _extract_stats(self, story: str, player_elements: list[StoryElement]) -> list[StoryElement]:
        """Extract statistical thresholds from story"""

        elements = []

        for pattern, stat_info in self.stat_patterns:
            matches = pattern.finditer(story)

            for match in matches:
                # Try to extract threshold
                threshold = None
                groups = match.groups()

                for group in groups:
                    if group and group.isdigit():
                        threshold = float(group)
                        break

                # Determine comparison direction
                comparison = "over"  # Default
                if "under" in match.group(0).lower():
                    comparison = "under"
                elif "exactly" in match.group(0).lower() or "+" not in match.group(0):
                    comparison = "exactly"

                # Try to associate with nearby player
                associated_player = self._find_associated_player(
                    match.start(), match.end(), player_elements, story
                )

                element = StoryElement(
                    element_type="stat",
                    raw_text=match.group(0),
                    confidence=0.85,
                    player_name=associated_player,
                    stat_type=stat_info["stat"],
                    threshold=threshold,
                    comparison=comparison,
                    market_type=stat_info["market"],
                )

                elements.append(element)

        return elements

    def _extract_teams(self, story: str) -> list[StoryElement]:
        """Extract team mentions from story"""

        elements = []

        for team_name, aliases in self.team_patterns.items():
            for alias in aliases:
                pattern = re.compile(r"\b" + re.escape(alias) + r"\b", re.IGNORECASE)
                matches = pattern.finditer(story)

                for match in matches:
                    element = StoryElement(
                        element_type="team",
                        raw_text=match.group(0),
                        confidence=0.9,
                        team_name=team_name,
                    )

                    elements.append(element)

        return elements

    def _extract_outcomes(self, story: str) -> list[StoryElement]:
        """Extract game outcomes and scores from story"""

        elements = []

        for pattern, outcome_type in self.score_patterns:
            matches = pattern.finditer(story)

            for match in matches:
                element = StoryElement(
                    element_type="outcome",
                    raw_text=match.group(0),
                    confidence=0.7,
                    game_outcome=outcome_type,
                )

                # Extract specific score if available
                if outcome_type in ["exact_score", "score_description"]:
                    groups = match.groups()
                    if len(groups) >= 2 and groups[0].isdigit() and groups[1].isdigit():
                        element.score = (int(groups[0]), int(groups[1]))

                elements.append(element)

        return elements

    def _find_associated_player(
        self,
        stat_start: int,
        stat_end: int,
        player_elements: list[StoryElement],
        story: str,
    ) -> str | None:
        """Find player associated with a stat mention"""

        # Look for closest player mention
        closest_player = None
        min_distance = float("inf")

        for player_elem in player_elements:
            # Find player position in story
            player_pos = story.find(player_elem.raw_text)
            if player_pos == -1:
                continue

            # Calculate distance
            distance = min(abs(player_pos - stat_start), abs(player_pos - stat_end))

            if distance < min_distance and distance < 50:  # Within 50 characters
                min_distance = distance
                closest_player = player_elem.player_name

        return closest_player

    def _calculate_confidence(self, story: str, elements: list[StoryElement]) -> float:
        """Calculate overall parsing confidence"""

        if not elements:
            return 0.0

        # Base confidence from element confidences
        avg_confidence = sum(elem.confidence for elem in elements) / len(elements)

        # Bonus for having multiple element types
        element_types = {elem.element_type for elem in elements}
        type_bonus = len(element_types) * 0.1

        # Bonus for complete information (player + stat + team)
        has_player = any(elem.element_type == "player" for elem in elements)
        has_stat = any(elem.element_type == "stat" for elem in elements)
        has_team = any(elem.element_type == "team" for elem in elements)

        completeness_bonus = 0.0
        if has_player and has_stat:
            completeness_bonus += 0.15
        if has_team:
            completeness_bonus += 0.1

        total_confidence = min(1.0, avg_confidence + type_bonus + completeness_bonus)

        return total_confidence

    def _classify_story(self, elements: list[StoryElement]) -> tuple[str, str]:
        """Classify the story type and narrative theme"""

        has_player_stats = any(elem.element_type == "stat" for elem in elements)
        has_game_outcome = any(elem.element_type == "outcome" for elem in elements)
        has_multiple_players = len([elem for elem in elements if elem.element_type == "player"]) > 1

        if has_player_stats and not has_game_outcome:
            return "player_performance", "Focus on individual player statistics"

        if has_player_stats and has_game_outcome:
            return "game_script", "Combination of player performance and game result"

        if has_game_outcome and not has_player_stats:
            return "team_result", "Focus on team performance and game outcome"

        if has_multiple_players:
            return "multi_player", "Multiple player performances"

        return "unknown", "Story type could not be determined"

    def _validate_coherence(self, parsed_story: ParsedStory) -> float:
        """Validate logical coherence of parsed elements"""

        coherence_score = 1.0

        # Check for conflicting team outcomes
        team_outcomes = {}
        for elem in parsed_story.elements:
            if elem.element_type == "outcome" and elem.team_name:
                if elem.team_name in team_outcomes:
                    # Check for conflicting outcomes
                    if team_outcomes[elem.team_name] != elem.game_outcome:
                        coherence_score -= 0.3
                else:
                    team_outcomes[elem.team_name] = elem.game_outcome

        # Check for realistic stat thresholds
        for elem in parsed_story.elements:
            if elem.element_type == "stat" and elem.threshold:
                if (elem.stat_type == "strikeouts" and elem.threshold > 15) or (
                    elem.stat_type == "home_runs" and elem.threshold > 3
                ):
                    coherence_score -= 0.2
                elif elem.stat_type == "hits" and elem.threshold > 5:
                    coherence_score -= 0.1

        return max(0.0, coherence_score)

    def _check_correlations(self, parsed_story: ParsedStory) -> list[str]:
        """Check for correlation issues in the story elements"""

        warnings = []

        # Check for negatively correlated elements
        has_pitcher_strikeouts = any(
            elem.stat_type == "strikeouts" for elem in parsed_story.elements
        )
        has_high_scoring = any(
            elem.game_outcome == "game_total" and elem.threshold and elem.threshold > 10
            for elem in parsed_story.elements
        )

        if has_pitcher_strikeouts and has_high_scoring:
            warnings.append("High strikeouts and high scoring may be negatively correlated")

        # Check for same-game conflicting elements
        teams_winning = set()
        teams_losing = set()

        for elem in parsed_story.elements:
            if elem.element_type == "outcome":
                if "win" in elem.game_outcome.lower():
                    teams_winning.add(elem.team_name)
                elif "lose" in elem.game_outcome.lower():
                    teams_losing.add(elem.team_name)

        conflict_teams = teams_winning.intersection(teams_losing)
        if conflict_teams:
            warnings.append(f"Conflicting win/loss for teams: {', '.join(conflict_teams)}")

        return warnings


class SGPConverter:
    """Convert parsed stories to SGP legs"""

    def __init__(self):
        self.market_mappings = self._initialize_market_mappings()
        self.odds_estimator = self._initialize_odds_estimator()

        logger.info("SGPConverter initialized")

    def _initialize_market_mappings(self) -> dict[str, dict[str, Any]]:
        """Initialize market mapping configurations"""

        mappings = {
            "strikeouts": {
                "market_type": MarketType.PLAYER_STRIKEOUTS,
                "common_lines": [4.5, 5.5, 6.5, 7.5, 8.5],
                "line_adjustment": 0.5,
                "base_odds": {"over": -115, "under": -105},
            },
            "hits": {
                "market_type": MarketType.PLAYER_HITS,
                "common_lines": [0.5, 1.5, 2.5],
                "line_adjustment": 1.0,
                "base_odds": {"over": -110, "under": -110},
            },
            "home_runs": {
                "market_type": MarketType.PLAYER_HOME_RUNS,
                "common_lines": [0.5, 1.5],
                "line_adjustment": 0.5,
                "base_odds": {"over": +150, "under": -180},
            },
            "rbis": {
                "market_type": MarketType.PLAYER_RBIS,
                "common_lines": [0.5, 1.5, 2.5],
                "line_adjustment": 0.5,
                "base_odds": {"over": -105, "under": -115},
            },
        }

        return mappings

    def _initialize_odds_estimator(self) -> dict[str, Any]:
        """Initialize odds estimation logic"""

        return {
            "base_juice": 0.10,  # 10% juice
            "correlation_adjustment": 0.05,
            "player_tier_adjustment": {
                "star": 0.10,
                "above_average": 0.05,
                "average": 0.00,
                "below_average": -0.05,
            },
        }

    def convert_to_sgp(self, parsed_story: ParsedStory) -> list[SGPLeg]:
        """Convert parsed story to SGP legs"""

        logger.info(f"Converting story to SGP: {parsed_story.original_story}")

        legs = []

        # Process stat elements
        stat_elements = [elem for elem in parsed_story.elements if elem.element_type == "stat"]
        for elem in stat_elements:
            leg = self._create_stat_leg(elem)
            if leg:
                legs.append(leg)

        # Process outcome elements
        outcome_elements = [
            elem for elem in parsed_story.elements if elem.element_type == "outcome"
        ]
        for elem in outcome_elements:
            leg = self._create_outcome_leg(elem, parsed_story)
            if leg:
                legs.append(leg)

        # Validate leg combinations
        validated_legs = self._validate_leg_combinations(legs)

        logger.info(f"Generated {len(validated_legs)} SGP legs")

        return validated_legs

    def _create_stat_leg(self, element: StoryElement) -> SGPLeg | None:
        """Create SGP leg from stat element"""

        if not element.stat_type or not element.threshold:
            return None

        mapping = self.market_mappings.get(element.stat_type)
        if not mapping:
            return None

        # Find appropriate betting line
        suggested_line = self._find_betting_line(element.threshold, mapping["common_lines"])

        # Determine selection direction
        selection = element.comparison if element.comparison in ["over", "under"] else "over"

        # Estimate odds
        base_odds = mapping["base_odds"][selection]
        estimated_odds = self._estimate_odds(element, base_odds)

        # Create description
        player_desc = element.player_name if element.player_name else "Player"
        description = (
            f"{player_desc} {selection.title()} {suggested_line} {element.stat_type.title()}"
        )

        # Generate reasoning
        reasoning = f"Story indicates {element.player_name} will {element.comparison} {element.threshold} {element.stat_type}"

        leg_id = f"leg_{element.stat_type}_{element.player_name or 'unknown'}_{selection}"

        return SGPLeg(
            leg_id=leg_id,
            source_element=element,
            market_type=mapping["market_type"],
            selection=selection,
            line=suggested_line,
            odds=estimated_odds,
            description=description,
            reasoning=reasoning,
            confidence=element.confidence * 0.9,  # Slight discount for conversion
            risk_factors=self._assess_stat_risks(element),
            available_books=["DraftKings", "FanDuel", "BetMGM"],
            line_variations={
                "DraftKings": suggested_line,
                "FanDuel": (suggested_line - 0.5 if suggested_line > 1 else suggested_line),
                "BetMGM": suggested_line + 0.5,
            },
        )

    def _create_outcome_leg(self, element: StoryElement, story: ParsedStory) -> SGPLeg | None:
        """Create SGP leg from outcome element"""

        if not element.game_outcome:
            return None

        # Determine teams involved
        teams = story.teams_involved
        if not teams:
            return None

        if element.game_outcome == "team_wins":
            # Create moneyline leg
            # Try to determine which team from context
            winning_team = self._infer_winning_team(element, story)
            if not winning_team:
                return None

            description = f"{winning_team} Moneyline"
            reasoning = "Story indicates this team will win the game"
            estimated_odds = -130  # Default favorite odds

            return SGPLeg(
                leg_id=f"leg_moneyline_{winning_team}",
                source_element=element,
                market_type=MarketType.MONEYLINE,
                selection="win",
                line=None,
                odds=estimated_odds,
                description=description,
                reasoning=reasoning,
                confidence=element.confidence * 0.8,
                risk_factors=["Moneyline bets are binary outcomes"],
                available_books=["DraftKings", "FanDuel", "BetMGM"],
                line_variations={},
            )

        if element.game_outcome == "exact_score":
            # Create total leg based on score
            if element.score:
                total_runs = sum(element.score)
                suggested_line = total_runs - 0.5
                selection = "over" if total_runs > 8 else "under"

                description = f"Game Total {selection.title()} {suggested_line}"
                reasoning = f"Story suggests exact score {element.score[0]}-{element.score[1]} ({total_runs} runs)"

                return SGPLeg(
                    leg_id=f"leg_total_{selection}_{suggested_line}",
                    source_element=element,
                    market_type=MarketType.TOTAL,
                    selection=selection,
                    line=suggested_line,
                    odds=-110,
                    description=description,
                    reasoning=reasoning,
                    confidence=element.confidence * 0.7,  # Exact scores are harder to predict
                    risk_factors=["Exact score predictions are very difficult"],
                    available_books=["DraftKings", "FanDuel"],
                    line_variations={
                        "DraftKings": suggested_line,
                        "FanDuel": suggested_line + 0.5,
                    },
                )

        return None

    def _find_betting_line(self, threshold: float, common_lines: list[float]) -> float:
        """Find the closest standard betting line to threshold"""

        if not common_lines:
            return threshold

        # Find closest line
        closest_line = min(common_lines, key=lambda x: abs(x - threshold))

        # If threshold is exactly between two lines, choose the more conservative one
        if threshold not in common_lines:
            lower_lines = [line for line in common_lines if line < threshold]
            upper_lines = [line for line in common_lines if line > threshold]

            if lower_lines and upper_lines:
                lower = max(lower_lines)
                upper = min(upper_lines)

                # If exactly between, choose based on over/under preference
                if abs(threshold - lower) == abs(threshold - upper):
                    closest_line = lower  # Conservative choice

        return closest_line

    def _estimate_odds(self, element: StoryElement, base_odds: int) -> int:
        """Estimate odds for the betting line"""

        # Start with base odds
        estimated_odds = base_odds

        # Adjust for player quality (if known)
        if element.player_name:
            # This would integrate with player research in real implementation
            tier_adjustment = 0  # Default
            estimated_odds = int(estimated_odds * (1 + tier_adjustment))

        # Adjust for threshold difficulty
        if element.stat_type == "strikeouts" and element.threshold:
            if element.threshold > 8:
                estimated_odds += 20  # Harder to achieve
            elif element.threshold < 5:
                estimated_odds -= 15  # Easier to achieve

        return estimated_odds

    def _infer_winning_team(self, element: StoryElement, story: ParsedStory) -> str | None:
        """Infer which team is expected to win from context"""

        teams = story.teams_involved
        if len(teams) != 2:
            return teams[0] if teams else None

        # Look for context clues in the original story
        story_text = story.original_story.lower()

        for team in teams:
            team_lower = team.lower()
            # Look for team name near win indicators
            if f"{team_lower} win" in story_text or f"{team_lower} beat" in story_text:
                return team

        # Default to first team mentioned
        return teams[0]

    def _assess_stat_risks(self, element: StoryElement) -> list[str]:
        """Assess risk factors for stat-based legs"""

        risks = []

        if element.stat_type == "strikeouts":
            risks.append("Pitcher could be pulled early")
            risks.append("Weather conditions could affect performance")

        elif element.stat_type in ["hits", "rbis", "runs"]:
            risks.append("Batting order position affects opportunities")
            risks.append("Opposing pitcher quality impacts performance")

        elif element.stat_type == "home_runs":
            risks.append("Home run props have lower hit rates")
            risks.append("Park factors and weather significantly impact outcome")

        # Threshold-specific risks
        if element.threshold and element.threshold > 8 and element.stat_type == "strikeouts":
            risks.append("Very high strikeout threshold increases variance")

        return risks

    def _validate_leg_combinations(self, legs: list[SGPLeg]) -> list[SGPLeg]:
        """Validate and potentially modify leg combinations"""

        validated_legs = []

        # Check for correlation issues
        correlation_groups = self._group_correlated_legs(legs)

        for group in correlation_groups:
            if len(group) == 1:
                validated_legs.extend(group)
            else:
                # Handle correlated legs
                best_leg = max(group, key=lambda x: x.confidence)

                # Add warning to other legs in group
                for leg in group:
                    if leg != best_leg:
                        leg.risk_factors.append("Correlated with other selected legs")

                validated_legs.extend(group)  # Keep all but warn

        return validated_legs

    def _group_correlated_legs(self, legs: list[SGPLeg]) -> list[list[SGPLeg]]:
        """Group legs that are correlated"""

        # Simple correlation detection
        groups = []
        processed = set()

        for i, leg1 in enumerate(legs):
            if i in processed:
                continue

            group = [leg1]
            processed.add(i)

            for j, leg2 in enumerate(legs[i + 1 :], i + 1):
                if j in processed:
                    continue

                # Check if legs are correlated
                if self._are_legs_correlated(leg1, leg2):
                    group.append(leg2)
                    processed.add(j)

            groups.append(group)

        return groups

    def _are_legs_correlated(self, leg1: SGPLeg, leg2: SGPLeg) -> bool:
        """Check if two legs are significantly correlated"""

        # Same player correlations
        if (
            leg1.source_element.player_name == leg2.source_element.player_name
            and leg1.source_element.player_name is not None
        ):
            return True

        # Pitcher + total correlations
        if (
            leg1.market_type == MarketType.PLAYER_STRIKEOUTS
            and leg2.market_type == MarketType.TOTAL
        ):
            return True

        # Team success + player performance correlations
        return bool(
            leg1.market_type == MarketType.MONEYLINE
            and leg2.source_element.team_name
            and leg1.source_element.team_name == leg2.source_element.team_name
        )


async def main():
    """Main CLI interface"""

    parser = argparse.ArgumentParser(description="EQ12 Story-to-SGP Converter")
    parser.add_argument("--story", required=True, help="Betting story to convert")
    parser.add_argument("--export", action="store_true", help="Export SGP to file")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    parser.add_argument(
        "--alternatives", action="store_true", help="Show alternative interpretations"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print("📖 EQ12 STORY-TO-SGP CONVERTER")
    print(f"Story: '{args.story}'\n")

    # Initialize components
    parser_engine = StoryParser()
    converter = SGPConverter()

    # Parse the story
    parsed_story = parser_engine.parse_story(args.story)

    print("📋 PARSING RESULTS:")
    print(f"   Confidence: {parsed_story.parsing_confidence:.2f}")
    print(f"   Story Type: {parsed_story.story_type}")
    print(f"   Narrative: {parsed_story.narrative_theme}")
    print(f"   Teams: {', '.join(parsed_story.teams_involved or ['Unknown'])}")
    print(f"   Coherence: {parsed_story.coherence_score:.2f}")

    if parsed_story.correlation_warnings:
        print("   ⚠️  Warnings:")
        for warning in parsed_story.correlation_warnings:
            print(f"      • {warning}")

    print(f"\n🔍 EXTRACTED ELEMENTS ({len(parsed_story.elements)}):")
    for i, elem in enumerate(parsed_story.elements, 1):
        print(f"   {i}. {elem.element_type.upper()}: {elem.raw_text}")
        if elem.player_name:
            print(f"      Player: {elem.player_name}")
        if elem.stat_type and elem.threshold:
            print(f"      Stat: {elem.stat_type} {elem.comparison} {elem.threshold}")
        if elem.team_name:
            print(f"      Team: {elem.team_name}")
        print(f"      Confidence: {elem.confidence:.2f}")

    # Convert to SGP
    sgp_legs = converter.convert_to_sgp(parsed_story)

    if not sgp_legs:
        print("\n❌ No valid SGP legs could be generated")
        return

    print(f"\n🎯 GENERATED SGP LEGS ({len(sgp_legs)}):")

    total_odds = 1.0
    for i, leg in enumerate(sgp_legs, 1):
        print(f"\n   {i}. {leg.description}")
        print(f"      Market: {leg.market_type.value}")
        print(f"      Selection: {leg.selection}")
        if leg.line is not None:
            print(f"      Line: {leg.line}")
        print(f"      Odds: {leg.odds:+d}")
        print(f"      Confidence: {leg.confidence:.2f}")
        print(f"      Reasoning: {leg.reasoning}")

        if leg.risk_factors:
            print("      Risks:")
            for risk in leg.risk_factors[:2]:  # Show first 2 risks
                print(f"         • {risk}")

        if leg.line_variations:
            print(
                "      Lines: "
                + ", ".join([f"{book}: {line}" for book, line in leg.line_variations.items()])
            )

        # Calculate parlay odds (simplified)
        leg_decimal = leg.odds / 100 + 1 if leg.odds > 0 else 100 / abs(leg.odds) + 1

        total_odds *= leg_decimal

    # Calculate combined odds
    if total_odds > 2:
        combined_american = int((total_odds - 1) * 100)
    else:
        combined_american = int(-100 / (total_odds - 1))

    print("\n📊 SGP SUMMARY:")
    print(f"   Total Legs: {len(sgp_legs)}")
    print(f"   Combined Odds: {combined_american:+d}")
    print(f"   Avg Confidence: {sum(leg.confidence for leg in sgp_legs) / len(sgp_legs):.2f}")

    # Show alternatives if requested
    if args.alternatives:
        print("\n🔄 ALTERNATIVE INTERPRETATIONS:")
        print("   • Alternative line versions (+/- 0.5 on each leg)")
        print("   • Single-leg versions for safer betting")
        print("   • Correlated leg substitutions")

        if parsed_story.story_type == "player_performance":
            print("   • Add team result for correlation play")
        elif parsed_story.story_type == "game_script":
            print("   • Split into player-only or game-only versions")

    # Export if requested
    if args.export:
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        export_path = f"C:/EQ12/logs/story_sgp_{timestamp}.json"

        export_data = {
            "original_story": args.story,
            "parsed_story": asdict(parsed_story),
            "sgp_legs": [asdict(leg) for leg in sgp_legs],
            "summary": {
                "total_legs": len(sgp_legs),
                "combined_odds": combined_american,
                "generation_time": datetime.now(UTC).isoformat(),
            },
        }

        with open(export_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"\n💾 SGP exported to: {export_path}")


if __name__ == "__main__":
    asyncio.run(main())
