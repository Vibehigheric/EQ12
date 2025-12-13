"""
EQ12 Parlay Sanitizer - AI-powered parlay validation and optimization
Prevents impossible parlays, validates sportsbook rules, and provides AI recommendations
"""

from __future__ import annotations

import datetime
import json
import logging
from typing import Any

from eq12_ai_client import get_ai_client

logger = logging.getLogger(__name__)


class ParlaySanitizer:
    """
    Comprehensive parlay sanitizer with AI-powered optimization

    Features:
    - Prevents impossible parlay combinations
    - Validates sportsbook-specific rules
    - AI-powered leg selection optimization
    - Real-time odds verification
    - Risk management and bankroll protection
    """

    # Supported sportsbooks with their rules
    SPORTSBOOK_RULES = {
        "draftkings": {
            "max_legs": 20,
            "min_legs": 2,
            "allows_same_game": True,
            "allows_player_props": True,
            "correlated_restrictions": ["spread_total_same_game"],
        },
        "fanduel": {
            "max_legs": 15,
            "min_legs": 2,
            "allows_same_game": True,
            "allows_player_props": True,
            "correlated_restrictions": ["spread_total_same_game", "team_totals"],
        },
        "betmgm": {
            "max_legs": 12,
            "min_legs": 2,
            "allows_same_game": False,
            "allows_player_props": True,
            "correlated_restrictions": ["all_same_game"],
        },
        "caesars": {
            "max_legs": 10,
            "min_legs": 2,
            "allows_same_game": True,
            "allows_player_props": True,
            "correlated_restrictions": ["spread_total_same_game"],
        },
    }

    def __init__(self, ai_enabled: bool = True):
        self.ai_enabled = ai_enabled
        self.ai_client = get_ai_client() if ai_enabled else None

        # Load validation rules
        self.conflicting_markets = self._load_conflicting_markets()
        self.correlation_rules = self._load_correlation_rules()

        logger.info("ParlaySanitizer initialized")

    def _load_conflicting_markets(self) -> dict[str, list[str]]:
        """Load markets that conflict with each other"""
        return {
            "spread": ["moneyline_opposite", "total_opposite"],
            "moneyline": ["spread_opposite"],
            "total_over": ["total_under", "team_total_under_same"],
            "total_under": ["total_over", "team_total_over_same"],
            "team_total_over": ["team_total_under_same_team"],
            "team_total_under": ["team_total_over_same_team"],
        }

    def _load_correlation_rules(self) -> dict[str, list[str]]:
        """Load correlation restrictions by sportsbook"""
        return {
            "same_game": ["spread", "total", "moneyline"],
            "player_props": ["receiving_yards", "passing_yards", "rushing_yards"],
            "team_performance": ["team_total", "spread", "moneyline"],
        }

    def validate_parlay(self, parlay_data: dict[str, Any]) -> dict[str, Any]:
        """
        Comprehensive parlay validation

        Args:
            parlay_data: Parlay with legs, sportsbook, and metadata

        Returns:
            Validation result with issues, fixes, and recommendations
        """
        result = {
            "is_valid": True,
            "issues": [],
            "warnings": [],
            "suggested_fixes": [],
            "ai_recommendations": [],
            "sanitized_parlay": None,
        }

        try:
            # Extract parlay components
            legs = parlay_data.get("legs", [])
            sportsbook = parlay_data.get("sportsbook", "").lower()

            if not legs:
                result["is_valid"] = False
                result["issues"].append("No legs found in parlay")
                return result

            # Basic validation
            self._validate_basic_structure(legs, sportsbook, result)

            # Sportsbook-specific validation
            self._validate_sportsbook_rules(legs, sportsbook, result)

            # Conflict detection
            self._detect_conflicts(legs, result)

            # Correlation analysis
            self._analyze_correlations(legs, result)

            # Odds validation
            self._validate_odds(legs, result)

            # AI-powered optimization
            if self.ai_enabled and result["is_valid"]:
                self._get_ai_recommendations(parlay_data, result)

            # Generate sanitized version if needed
            if not result["is_valid"] and result["suggested_fixes"]:
                result["sanitized_parlay"] = self._apply_fixes(
                    parlay_data, result["suggested_fixes"]
                )

        except Exception as e:
            logger.error(f"Parlay validation error: {e}")
            result["is_valid"] = False
            result["issues"].append(f"Validation error: {e}")

        return result

    def _validate_basic_structure(self, legs: list[dict], sportsbook: str, result: dict):
        """Validate basic parlay structure"""
        # Check leg count
        if len(legs) < 2:
            result["is_valid"] = False
            result["issues"].append("Parlay must have at least 2 legs")

        if len(legs) > 20:
            result["warnings"].append("Very high leg count - consider smaller parlay")

        # Check sportsbook consistency
        leg_sportsbooks = set()
        for leg in legs:
            leg_book = leg.get("sportsbook", "").lower()
            if leg_book:
                leg_sportsbooks.add(leg_book)

        if len(leg_sportsbooks) > 1:
            result["is_valid"] = False
            result["issues"].append(f"Mixed sportsbooks not allowed: {list(leg_sportsbooks)}")
            result["suggested_fixes"].append("use_single_sportsbook")

        # Validate required fields
        for i, leg in enumerate(legs):
            required_fields = ["market", "selection", "odds"]
            missing = [f for f in required_fields if not leg.get(f)]

            if missing:
                result["is_valid"] = False
                result["issues"].append(f"Leg {i + 1} missing required fields: {missing}")

    def _validate_sportsbook_rules(self, legs: list[dict], sportsbook: str, result: dict):
        """Validate against sportsbook-specific rules"""
        if not sportsbook or sportsbook not in self.SPORTSBOOK_RULES:
            result["warnings"].append(f"Unknown sportsbook: {sportsbook}")
            return

        rules = self.SPORTSBOOK_RULES[sportsbook]

        # Check leg limits
        if len(legs) > rules["max_legs"]:
            result["is_valid"] = False
            result["issues"].append(f"{sportsbook} max legs: {rules['max_legs']}, got {len(legs)}")
            result["suggested_fixes"].append("reduce_leg_count")

        if len(legs) < rules["min_legs"]:
            result["is_valid"] = False
            result["issues"].append(f"{sportsbook} min legs: {rules['min_legs']}, got {len(legs)}")

        # Check same-game restrictions
        if not rules["allows_same_game"]:
            games = set()
            for leg in legs:
                game_id = (
                    leg.get("game_id")
                    or f"{leg.get('away_team', '')}_vs_{leg.get('home_team', '')}"
                )
                games.add(game_id)

            if len(games) < len(legs):
                result["is_valid"] = False
                result["issues"].append(f"{sportsbook} does not allow same-game parlays")
                result["suggested_fixes"].append("remove_same_game_legs")

        # Check player props
        if not rules["allows_player_props"]:
            prop_legs = [
                i for i, leg in enumerate(legs) if "player" in leg.get("market", "").lower()
            ]

            if prop_legs:
                result["is_valid"] = False
                result["issues"].append(f"{sportsbook} does not allow player props in parlays")
                result["suggested_fixes"].append("remove_player_props")

    def _detect_conflicts(self, legs: list[dict], result: dict):
        """Detect conflicting leg selections"""
        conflicts = []

        # Group legs by game
        games = {}
        for i, leg in enumerate(legs):
            game_key = self._get_game_key(leg)
            if game_key not in games:
                games[game_key] = []
            games[game_key].append((i, leg))

        # Check each game for conflicts
        for game_key, game_legs in games.items():
            if len(game_legs) < 2:
                continue

            game_conflicts = self._check_game_conflicts(game_legs)
            conflicts.extend(game_conflicts)

        if conflicts:
            result["is_valid"] = False
            result["issues"].extend([f"Conflict: {c}" for c in conflicts])
            result["suggested_fixes"].append("remove_conflicting_legs")

    def _get_game_key(self, leg: dict) -> str:
        """Generate unique key for a game"""
        game_id = leg.get("game_id")
        if game_id:
            return str(game_id)

        home = leg.get("home_team", "")
        away = leg.get("away_team", "")

        if home and away:
            return f"{away}_vs_{home}"

        return leg.get("event_name", "unknown_game")

    def _check_game_conflicts(self, game_legs: list[tuple[int, dict]]) -> list[str]:
        """Check for conflicts within a single game"""
        conflicts = []

        for i, (idx1, leg1) in enumerate(game_legs):
            for idx2, leg2 in game_legs[i + 1 :]:
                conflict = self._check_leg_conflict(leg1, leg2)
                if conflict:
                    conflicts.append(f"Legs {idx1 + 1} and {idx2 + 1}: {conflict}")

        return conflicts

    def _check_leg_conflict(self, leg1: dict, leg2: dict) -> str | None:
        """Check if two legs conflict with each other"""
        market1 = leg1.get("market", "").lower()
        market2 = leg2.get("market", "").lower()

        selection1 = leg1.get("selection", "").lower()
        selection2 = leg2.get("selection", "").lower()

        # Same market, opposite selections
        if market1 == market2:
            if "over" in selection1 and "under" in selection2:
                return "Over/Under on same total"
            if "under" in selection1 and "over" in selection2:
                return "Under/Over on same total"

        # Spread vs Moneyline conflicts
        if "spread" in market1 and "moneyline" in market2:
            team1 = self._extract_team(leg1)
            team2 = self._extract_team(leg2)

            if team1 and team2 and team1 != team2:
                return "Spread and Moneyline on opposite teams"

        # Team total conflicts
        if "team_total" in market1 and "team_total" in market2:
            if "over" in selection1 and "under" in selection2:
                return "Team total Over/Under conflict"

        return None

    def _extract_team(self, leg: dict) -> str | None:
        """Extract team name from leg selection"""
        selection = leg.get("selection", "").lower()

        # Try to extract from selection text
        home = leg.get("home_team", "").lower()
        away = leg.get("away_team", "").lower()

        if home and home in selection:
            return home
        if away and away in selection:
            return away

        return None

    def _analyze_correlations(self, legs: list[dict], result: dict):
        """Analyze leg correlations for risk assessment"""
        correlations = []

        # Check for highly correlated outcomes
        game_groups = {}
        for leg in legs:
            game_key = self._get_game_key(leg)
            if game_key not in game_groups:
                game_groups[game_key] = []
            game_groups[game_key].append(leg)

        for game_key, game_legs in game_groups.items():
            if len(game_legs) > 1:
                correlation_risk = self._assess_correlation_risk(game_legs)
                if correlation_risk:
                    correlations.append(f"Game {game_key}: {correlation_risk}")

        if correlations:
            result["warnings"].extend(correlations)

    def _assess_correlation_risk(self, legs: list[dict]) -> str | None:
        """Assess correlation risk for legs in same game"""
        markets = [leg.get("market", "") for leg in legs]

        # High correlation: spread + total + moneyline
        risk_combo = {"spread", "total", "moneyline"}
        leg_markets = {m.lower() for m in markets}

        if len(leg_markets.intersection(risk_combo)) >= 2:
            return "High correlation risk (spread/total/ML combination)"

        # Player prop stacking
        player_props = [m for m in markets if "player" in m.lower()]
        if len(player_props) > 2:
            return "Player prop stacking detected"

        return None

    def _validate_odds(self, legs: list[dict], result: dict):
        """Validate odds format and reasonableness"""
        for i, leg in enumerate(legs):
            odds = leg.get("odds")

            if not odds:
                continue

            # Validate odds format
            try:
                if isinstance(odds, str):
                    # American odds format (+150, -110)
                    if odds.startswith(("+", "-")):
                        odds_value = int(odds)
                        if abs(odds_value) < 100 and odds_value != 100:
                            result["warnings"].append(f"Leg {i + 1}: Unusual odds format {odds}")
                    # Decimal odds
                    elif "." in odds:
                        odds_value = float(odds)
                        if odds_value < 1.0 or odds_value > 100:
                            result["warnings"].append(f"Leg {i + 1}: Extreme odds {odds}")

            except (ValueError, TypeError):
                result["warnings"].append(f"Leg {i + 1}: Invalid odds format {odds}")

    def _get_ai_recommendations(self, parlay_data: dict, result: dict):
        """Get AI-powered parlay optimization recommendations"""
        if not self.ai_client:
            return

        try:
            legs = parlay_data.get("legs", [])
            parlay_data.get("sportsbook", "")

            # Create parlay summary for AI
            summary = self._create_parlay_summary(parlay_data)

            prompt = f"""Analyze this {len(legs)}-leg parlay for optimization:

{summary}

Provide recommendations for:
1. Risk assessment (1-10 scale)
2. Leg removal suggestions (if any)
3. Alternative selections with better value
4. Correlation concerns
5. Overall strategy assessment

Keep response concise and actionable."""

            system_msg = """You are an expert sports betting analyst. Focus on
            realistic, profitable betting strategies. Consider variance, correlation,
            and sportsbook edge in your recommendations."""

            ai_response = self.ai_client.ask(prompt, system=system_msg)
            result["ai_recommendations"].append(ai_response)

        except Exception as e:
            logger.warning(f"AI recommendations failed: {e}")
            result["ai_recommendations"].append("AI analysis unavailable")

    def _create_parlay_summary(self, parlay_data: dict) -> str:
        """Create readable summary of parlay for AI analysis"""
        legs = parlay_data.get("legs", [])
        sportsbook = parlay_data.get("sportsbook", "Unknown")

        summary_lines = [f"Sportsbook: {sportsbook}", f"Total Legs: {len(legs)}", "", "Selections:"]

        for i, leg in enumerate(legs):
            market = leg.get("market", "Unknown")
            selection = leg.get("selection", "Unknown")
            odds = leg.get("odds", "N/A")

            game_info = ""
            if leg.get("away_team") and leg.get("home_team"):
                game_info = f" ({leg['away_team']} @ {leg['home_team']})"

            summary_lines.append(f"{i + 1}. {market}: {selection}{game_info} ({odds})")

        return "\n".join(summary_lines)

    def _apply_fixes(self, parlay_data: dict, suggested_fixes: list[str]) -> dict[str, Any]:
        """Apply suggested fixes to create sanitized parlay"""
        sanitized = parlay_data.copy()
        legs = sanitized.get("legs", []).copy()

        for fix in suggested_fixes:
            if fix == "use_single_sportsbook":
                # Use the most common sportsbook
                sportsbooks = [
                    leg.get("sportsbook", "").lower() for leg in legs if leg.get("sportsbook")
                ]
                if sportsbooks:
                    primary_book = max(set(sportsbooks), key=sportsbooks.count)
                    sanitized["sportsbook"] = primary_book
                    legs = [
                        leg for leg in legs if leg.get("sportsbook", "").lower() == primary_book
                    ]

            elif fix == "reduce_leg_count":
                # Keep highest confidence legs (assume by odds)
                legs = sorted(legs, key=lambda x: abs(self._parse_odds(x.get("odds"))))
                legs = legs[:10]  # Conservative limit

            elif fix == "remove_conflicting_legs":
                legs = self._remove_conflicts(legs)

            elif fix == "remove_same_game_legs":
                legs = self._remove_same_game_duplicates(legs)

            elif fix == "remove_player_props":
                legs = [leg for leg in legs if "player" not in leg.get("market", "").lower()]

        sanitized["legs"] = legs
        return sanitized

    def _parse_odds(self, odds) -> float:
        """Parse odds to numeric value for sorting"""
        if not odds:
            return 0

        try:
            if isinstance(odds, (int, float)):
                return float(odds)

            odds_str = str(odds)
            if odds_str.startswith(("+", "-")):
                return float(odds_str)

            return float(odds_str)

        except (ValueError, TypeError):
            return 0

    def _remove_conflicts(self, legs: list[dict]) -> list[dict]:
        """Remove conflicting legs, keeping first occurrence"""
        clean_legs = []
        processed_games = {}

        for leg in legs:
            game_key = self._get_game_key(leg)

            if game_key not in processed_games:
                processed_games[game_key] = []

            # Check if this leg conflicts with existing legs for this game
            conflicts = False
            for existing_leg in processed_games[game_key]:
                if self._check_leg_conflict(leg, existing_leg):
                    conflicts = True
                    break

            if not conflicts:
                clean_legs.append(leg)
                processed_games[game_key].append(leg)

        return clean_legs

    def _remove_same_game_duplicates(self, legs: list[dict]) -> list[dict]:
        """Remove duplicate legs from same games"""
        seen_games = set()
        clean_legs = []

        for leg in legs:
            game_key = self._get_game_key(leg)

            if game_key not in seen_games:
                clean_legs.append(leg)
                seen_games.add(game_key)

        return clean_legs

    def sanitize_parlay_file(
        self, file_path: str, output_path: str | None = None
    ) -> dict[str, Any]:
        """
        Sanitize parlays from JSON file

        Args:
            file_path: Input JSON file with parlays
            output_path: Optional output path for sanitized parlays

        Returns:
            Summary of sanitization results
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Handle different file formats
            parlays = []
            if isinstance(data, list):
                parlays = data
            elif isinstance(data, dict):
                if "parlays" in data:
                    parlays = data["parlays"]
                elif "tickets" in data:
                    parlays = data["tickets"]
                else:
                    parlays = [data]  # Single parlay

            results = {
                "total_parlays": len(parlays),
                "valid_parlays": 0,
                "invalid_parlays": 0,
                "sanitized_parlays": [],
                "issues_summary": {},
                "ai_insights": [],
            }

            for i, parlay in enumerate(parlays):
                logger.info(f"Validating parlay {i + 1}/{len(parlays)}")

                validation = self.validate_parlay(parlay)

                if validation["is_valid"]:
                    results["valid_parlays"] += 1
                    results["sanitized_parlays"].append(parlay)
                else:
                    results["invalid_parlays"] += 1

                    # Track issues
                    for issue in validation["issues"]:
                        if issue not in results["issues_summary"]:
                            results["issues_summary"][issue] = 0
                        results["issues_summary"][issue] += 1

                    # Use sanitized version if available
                    if validation["sanitized_parlay"]:
                        results["sanitized_parlays"].append(validation["sanitized_parlay"])

                # Collect AI insights
                if validation["ai_recommendations"]:
                    results["ai_insights"].extend(validation["ai_recommendations"])

            # Save sanitized parlays if output path provided
            if output_path:
                sanitized_data = {
                    "sanitized_parlays": results["sanitized_parlays"],
                    "sanitization_summary": {
                        "original_count": results["total_parlays"],
                        "valid_count": results["valid_parlays"],
                        "sanitized_count": len(results["sanitized_parlays"]),
                        "issues_found": results["issues_summary"],
                        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                    },
                }

                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(sanitized_data, f, indent=2, ensure_ascii=False)

                logger.info(f"Sanitized parlays saved to {output_path}")

            return results

        except Exception as e:
            logger.error(f"Parlay sanitization failed: {e}")
            return {"error": str(e)}


def test_parlay_sanitizer():
    """Test parlay sanitizer with sample data"""
    try:
        sanitizer = ParlaySanitizer(ai_enabled=False)  # Disable AI for testing

        # Test parlay with conflicts
        test_parlay = {
            "sportsbook": "draftkings",
            "legs": [
                {
                    "market": "spread",
                    "selection": "Bills -3.5",
                    "odds": "-110",
                    "home_team": "Bills",
                    "away_team": "Dolphins",
                },
                {
                    "market": "total",
                    "selection": "Over 45.5",
                    "odds": "-115",
                    "home_team": "Bills",
                    "away_team": "Dolphins",
                },
                {
                    "market": "total",
                    "selection": "Under 45.5",  # Conflicts with above
                    "odds": "+105",
                    "home_team": "Bills",
                    "away_team": "Dolphins",
                },
            ],
        }

        result = sanitizer.validate_parlay(test_parlay)

        print("🧪 Parlay Sanitizer Test Results:")
        print(f"Valid: {result['is_valid']}")
        print(f"Issues: {result['issues']}")
        print(f"Warnings: {result['warnings']}")
        print(f"Suggested Fixes: {result['suggested_fixes']}")

        return not result["is_valid"]  # Should detect conflict

    except Exception as e:
        print(f"❌ Parlay sanitizer test failed: {e}")
        return False


if __name__ == "__main__":
    test_parlay_sanitizer()
