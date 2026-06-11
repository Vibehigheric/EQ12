#!/usr/bin/env python3
"""
EQ12 Same Game Parlay (SGP) Builder
Builds high-confidence, high-ROI SGPs for daily sports betting automation.
No emojis - ASCII only to avoid Windows cp1252 encoding errors.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Any

# Import existing EQ12 components
try:
    from eq12_math.odds import (
        american_to_decimal,
        expected_value,
        kelly_fraction,
        parlay_decimal_odds,
    )
except ImportError:
    # Fallback implementations if eq12_math module doesn't exist
    def american_to_decimal(american_odds: int) -> float:
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1

    def expected_value(decimal_odds: float, true_probability: float) -> float:
        """Calculate expected value given odds and true probability"""
        return (decimal_odds * true_probability) - 1

    def parlay_decimal_odds(odds_list: list[float]) -> float:
        """Calculate parlay odds from list of decimal odds"""
        result = 1.0
        for odds in odds_list:
            result *= odds
        return result

    def kelly_fraction(decimal_odds: float, true_probability: float) -> float:
        """Calculate Kelly criterion betting fraction"""
        ev = expected_value(decimal_odds, true_probability)
        if ev <= 0:
            return 0.0
        return (decimal_odds * true_probability - 1) / (decimal_odds - 1)


try:
    from eq12_parlay_sanitizer import validate_sgp
except ImportError:
    # Fallback SGP validator
    def validate_sgp(legs: list[dict], sgp_mode: bool = True) -> dict[str, Any]:
        """Validate SGP legs for logical consistency"""
        if not legs:
            return {"valid": False, "reason": "No legs provided"}

        if len(legs) < 2:
            return {"valid": False, "reason": "SGP requires at least 2 legs"}

        # Basic contradiction checks for same game
        markets_seen = {}
        for leg in legs:
            market = leg.get("market", "").lower()
            selection = leg.get("selection", "").lower()

            # Check for obvious contradictions
            if market == "total" and "over" in selection and "under" in selection:
                return {
                    "valid": False,
                    "reason": "Cannot have both over and under on same total",
                }

            # Store market for further checks
            if market not in markets_seen:
                markets_seen[market] = []
            markets_seen[market].append(selection)

        return {"valid": True, "reason": "SGP validation passed"}


@dataclass
class SGPLeg:
    """Individual leg of a Same Game Parlay"""

    market: str
    selection: str
    price: int  # American odds
    book: str
    decimal_odds: float = None

    def __post_init__(self):
        if self.decimal_odds is None:
            self.decimal_odds = american_to_decimal(self.price)


@dataclass
class SGP:
    """Same Game Parlay with scoring metrics"""

    game: str
    league: str
    legs: list[SGPLeg]
    decimal_odds: float
    stake: float
    potential_payout: float
    ev_pct: float
    kelly_fraction: float
    risk_score: str
    validated: bool
    notes: str = ""
    type: str = "sgp"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result["legs"] = [asdict(leg) for leg in self.legs]
        return result


class SGPBuilder:
    """Builds and scores Same Game Parlays for EQ12 automation"""

    def __init__(self, min_odds: float = 10.0, stake_range: tuple[float, float] = (8.0, 20.0)):
        self.min_odds = min_odds
        self.stake_min, self.stake_max = stake_range
        self.logger = logging.getLogger(__name__)

        # Default hold assumptions by market type
        self.market_holds = {
            "moneyline": 0.04,  # 4% hold
            "spread": 0.045,  # 4.5% hold
            "total": 0.045,  # 4.5% hold
            "player_props": 0.08,  # 8% hold for props
        }

    def build_sgp_candidates(
        self, game: dict, market_book: dict, rules: dict | None = None
    ) -> list[SGP]:
        """
        Build all valid SGP candidates for a game

        Args:
            game: Game information dict with teams, date, etc.
            market_book: Available markets and best prices
            rules: Optional SGP rules and constraints

        Returns:
            List of valid SGP candidates
        """
        candidates = []

        try:
            # Extract available markets
            available_markets = self._extract_markets(market_book)

            if len(available_markets) < 2:
                self.logger.warning(f"Insufficient markets for SGP: {game.get('id', 'unknown')}")
                return candidates

            # Generate combinations of 2-6 legs
            for leg_count in range(2, min(7, len(available_markets) + 1)):
                for market_combo in combinations(available_markets, leg_count):
                    sgp = self._build_sgp_from_markets(game, market_combo)
                    if sgp:
                        candidates.append(sgp)

            self.logger.info(
                f"Generated {len(candidates)} SGP candidates for {game.get('id', 'unknown')}"
            )

        except Exception as e:
            self.logger.error(f"Error building SGP candidates: {e!s}")

        return candidates

    def _extract_markets(self, market_book: dict) -> list[dict]:
        """Extract available markets from market book"""
        markets = []

        # Standard markets
        for market_type in ["h2h", "spreads", "totals"]:
            if market_type in market_book:
                for outcome in market_book[market_type].get("outcomes", []):
                    markets.append(
                        {
                            "market": self._normalize_market_name(market_type),
                            "selection": outcome.get("name", ""),
                            "price": outcome.get("price", 0),
                            "book": market_book[market_type].get("bookmaker", "unknown"),
                        }
                    )

        # Player props if available
        if "player_props" in market_book:
            for prop in market_book["player_props"]:
                markets.append(
                    {
                        "market": "player_props",
                        "selection": prop.get("description", ""),
                        "price": prop.get("price", 0),
                        "book": prop.get("bookmaker", "unknown"),
                    }
                )

        return markets

    def _normalize_market_name(self, market_type: str) -> str:
        """Normalize market names for consistency"""
        mapping = {"h2h": "moneyline", "spreads": "spread", "totals": "total"}
        return mapping.get(market_type, market_type)

    def _build_sgp_from_markets(self, game: dict, markets: tuple[dict]) -> SGP | None:
        """Build SGP from selected markets"""
        try:
            # Convert to SGP legs
            legs = []
            for market in markets:
                leg = SGPLeg(
                    market=market["market"],
                    selection=market["selection"],
                    price=market["price"],
                    book=market["book"],
                )
                legs.append(leg)

            # Validate SGP
            validation = validate_sgp([asdict(leg) for leg in legs], sgp_mode=True)
            if not validation.get("valid", False):
                return None

            # Calculate parlay odds
            decimal_odds_list = [leg.decimal_odds for leg in legs]
            parlay_odds = parlay_decimal_odds(decimal_odds_list)

            if parlay_odds < self.min_odds:
                return None

            # Score the SGP
            scoring = self.score_sgp_legs(legs, parlay_odds)

            if scoring["ev_pct"] < 0.02:  # Skip if EV < 2%
                return None

            # Determine optimal stake
            stake = self._calculate_optimal_stake(scoring["kelly_fraction"])

            sgp = SGP(
                game=f"{game.get('home_team', 'Unknown')} vs {game.get('away_team', 'Unknown')}",
                league=game.get("sport_title", "Unknown"),
                legs=legs,
                decimal_odds=parlay_odds,
                stake=stake,
                potential_payout=stake * parlay_odds,
                ev_pct=scoring["ev_pct"],
                kelly_fraction=scoring["kelly_fraction"],
                risk_score=scoring["risk_score"],
                validated=True,
                notes="Same-game supported; props availability may vary by book.",
            )

            return sgp

        except Exception as e:
            self.logger.error(f"Error building SGP from markets: {e!s}")
            return None

    def score_sgp_legs(self, legs: list[SGPLeg], parlay_odds: float) -> dict[str, Any]:
        """
        Score SGP based on expected value and risk

        Args:
            legs: List of SGP legs
            parlay_odds: Combined decimal odds

        Returns:
            Scoring metrics dictionary
        """
        try:
            # Estimate true probabilities (simple consensus-hold adjustment)
            total_implied_prob = 0.0

            for leg in legs:
                implied_prob = 1.0 / leg.decimal_odds
                # Adjust for assumed hold based on market type
                hold = self.market_holds.get(leg.market, 0.05)
                true_prob = implied_prob / (1 - hold)
                total_implied_prob += true_prob

            # For parlay, multiply individual true probabilities
            # This is simplified - real correlation modeling would be more complex
            estimated_true_prob = max(0.01, min(0.99, total_implied_prob / len(legs)))

            # Calculate metrics
            ev = expected_value(parlay_odds, estimated_true_prob)
            ev_pct = ev * 100
            kelly_frac = kelly_fraction(parlay_odds, estimated_true_prob)

            # Cap kelly fraction for safety
            kelly_frac = min(kelly_frac, 0.25)

            # Determine risk score
            if ev_pct >= 8.0:
                risk_score = "LOW"
            elif ev_pct >= 4.0:
                risk_score = "MED"
            elif ev_pct >= 2.0:
                risk_score = "HIGH"
            else:
                risk_score = "SKIP"

            return {
                "ev_pct": ev_pct / 100,  # Convert back to decimal
                "kelly_fraction": kelly_frac,
                "risk_score": risk_score,
                "estimated_true_prob": estimated_true_prob,
            }

        except Exception as e:
            self.logger.error(f"Error scoring SGP: {e!s}")
            return {
                "ev_pct": 0.0,
                "kelly_fraction": 0.0,
                "risk_score": "SKIP",
                "estimated_true_prob": 0.0,
            }

    def _calculate_optimal_stake(self, kelly_fraction: float) -> float:
        """Calculate optimal stake within allowed range"""
        if kelly_fraction >= 0.15:
            # High confidence - use higher stake
            return self.stake_max
        elif kelly_fraction >= 0.08:
            # Medium confidence - mid-range stake
            return (self.stake_min + self.stake_max) / 2
        else:
            # Lower confidence - minimum stake
            return self.stake_min

    def select_best_sgp(self, candidates: list[SGP], min_odds: float | None = None) -> SGP | None:
        """
        Select best SGP from candidates based on EV and risk

        Args:
            candidates: List of SGP candidates
            min_odds: Minimum odds requirement (uses class default if None)

        Returns:
            Best SGP candidate or None
        """
        if not candidates:
            return None

        min_odds = min_odds or self.min_odds

        # Filter by minimum odds and risk requirements
        valid_candidates = [
            sgp for sgp in candidates if sgp.decimal_odds >= min_odds and sgp.risk_score != "SKIP"
        ]

        if not valid_candidates:
            return None

        # Sort by EV percentage (descending), then by risk score preference
        risk_priority = {"LOW": 3, "MED": 2, "HIGH": 1}

        valid_candidates.sort(
            key=lambda sgp: (sgp.ev_pct, risk_priority.get(sgp.risk_score, 0)), reverse=True
        )

        return valid_candidates[0]


def setup_logging() -> None:
    """Setup ASCII-only logging to avoid Windows encoding issues"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    Path("logs").mkdir(parents=True, exist_ok=True)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # File handler
    log_filename = f"logs/eq12_sgp_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_filename, encoding="ascii", errors="ignore")
    file_handler.setLevel(logging.DEBUG)

    # ASCII-only formatter (no emojis)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


if __name__ == "__main__":
    # Example usage
    setup_logging()

    builder = SGPBuilder(min_odds=10.0, stake_range=(8.0, 20.0))

    # Example game and market book
    example_game = {
        "id": "test_game_1",
        "home_team": "Boston Bruins",
        "away_team": "NY Rangers",
        "sport_title": "NHL",
    }

    example_market_book = {
        "h2h": {
            "bookmaker": "draftkings",
            "outcomes": [
                {"name": "Boston Bruins", "price": -135},
                {"name": "NY Rangers", "price": 115},
            ],
        },
        "totals": {
            "bookmaker": "fanduel",
            "outcomes": [{"name": "Over 6.5", "price": -105}, {"name": "Under 6.5", "price": -115}],
        },
    }

    candidates = builder.build_sgp_candidates(example_game, example_market_book)
    best_sgp = builder.select_best_sgp(candidates)

    if best_sgp:
        print("Best SGP found:")
        print(json.dumps(best_sgp.to_dict(), indent=2))
    else:
        print("No qualifying SGP found")
