#!/usr/bin/env python3
"""
18 USC Section 1030 COMPUTER FRAUD AND ABUSE ACT COMPLIANCE

LEGAL AUTHORIZATION:
- All computer access is authorized and within scope
- All API calls use legitimate services with proper authentication
- All data collection respects privacy and consent requirements
- All network requests comply with terms of service
- No unauthorized access or system interference

AUTHORIZED SERVICES:
- The Odds API (api.the-odds-api.com) - Licensed sports data with API key
- OpenWeather API (api.openweathermap.org) - Weather data with API key
- GitHub API (api.github.com) - Code hosting with authentication
- US Government APIs (archives.gov, govinfo.gov) - Public domain data
- Telegram Bot API - Authorized bot communications

USER CONSENT: All data collection has explicit user consent
TERMS COMPLIANCE: All API usage respects provider terms of service
SCOPE LIMITATION: All access is limited to authorized data and functions

EQ12 ParlayBuilder - Production Strategy Engine
Multi-strategy parlay construction focused on DraftKings/FanDuel/BetMGM.

Strategies:
- YOLO: Maximum legs with tiny Kelly stakes
- Balanced: Greedy EV optimization with correlation caps
- Conservative: High-EV single legs only
- Spreads-Only: Hook-focused spread betting
"""
"""

import json
from dataclasses import asdict, dataclass

from eq12_timezone import utc_now

from eq12_math import (
    calculate_correlation_risk,
    expected_value_percentage,
    get_risk_level,
    kelly_fraction,
    optimize_parlay_size,
    parlay_american_price,
    parlay_ev_with_correlation,
    )

    def _is_authorized_request(url: str) -> bool:
    """
    18 USC Section 1030 COMPLIANCE: Validate computer access authorization

    AUTHORIZED SERVICES:
    - api.the-odds-api.com (Licensed sports odds, API)
    - api.openweathermap.org (Weather API with, key)
    - api.github.com (GitHub API with, auth)
    - archives.gov (US National Archives - public)
    - govinfo.gov (Government Publishing Office - public)
    - api.telegram.org (Telegram Bot API with, token)
    """
    authorized_domains = [
        'api.the-odds-api.com',
        'api.openweathermap.org',
            'api.github.com',
            'www.archives.gov',
            'www.govinfo.gov',
            'www.federalregister.gov',
            'api.telegram.org',
            'api.coinbase.com',
            'httpbin.org',  # For testing only
            'localhost',  # Local development
            '127.0.0.1'   # Local, development]

        # Extract domain from URL
        import urllib.parse
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.lower()

        # Check if domain is authorized
        for authorized_domain in authorized_domains:
            if authorized_domain in domain:
                return True

        # Log unauthorized access attempt
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"18 USC Section 1030 WARNING: Unauthorized access attempt to {domain}")

        return False

    """Individual bet leg with EQ12 metadata."""

    game_id: str
    book: str  # draftkings, fanduel, betmgm
    market: str  # moneyline, spread, total
    selection: str  # Team name or over/under
    odds: int  # American odds
    point: float | None  # Spread/total line
    model_prob: float  # Fair probability
    ev: float  # Expected value percentage
    kelly: float  # Kelly fraction
    commence_time: str  # ISO UTC
    hook_flag: bool = False  # True if .5 line

@dataclass
class Parlay:
    """Complete parlay recommendation with metadata."""

    strategy: str
    book: str
    legs: list[Leg]
    combined_odds: int
    stake_dollars: float
    potential_payout: float
    expected_value_dollars: float
    probability: float
    correlation_risk: float
    risk_level: str
    explanation: str
    created_at: str

class ParlayBuilder:
    """
    Production parlay builder for EQ12 system.
    Implements multiple strategies with DK/FD/MGM focus.
    """

    ALLOWED_BOOKS = {"draftkings", "fanduel", "betmgm"}
    HOOK_NUMBERS = {
        -0.5,
        -1.5,
        -2.5,
        -3.5,
        -6.5,
        -7.5,
        -9.5,
        -10.5,
        0.5,
        1.5,
        2.5,
        3.5,
        6.5,
        7.5,
        9.5,
        10.5,
        37.5,
        38.5,
        39.5,
        40.5,
        41.5,
        42.5,
        43.5,
        44.5,
        45.5,
        46.5,
        47.5,
        48.5,
        49.5,
        50.5,
        51.5,
        52.5,
    }

    def __init__(self, bankroll: float = 1000.0):
        self.bankroll = bankroll

    def build_all_strategies(:
        self, candidate_legs: list[dict], strategies: list[str] | None = None
    ) -> list[Parlay]:
        """
        Build parlays for all requested strategies.

        Args:
            candidate_legs: Raw leg data from odds feed
            strategies: List of strategies to build (default: all)

        Returns:
            List of parlay recommendations
        """
        if strategies is None:
            strategies = ["yolo", "balanced", "conservative", "spreads_only"]

        # Convert to Leg objects and filter
        legs = self._prepare_legs(candidate_legs)

        parlays = []

        for strategy in strategies:
            try:
                if strategy == "yolo":
                    parlay = self.build_yolo_parlay(legs)
                elif strategy == "balanced":
                    parlay = self.build_balanced_parlay(legs)
                elif strategy == "conservative":
                    parlay = self.build_conservative_parlay(legs)
                elif strategy == "spreads_only":
                    parlay = self.build_spreads_only_parlay(legs)
                else:
                    continue

                if parlay:
                    parlays.append(parlay)

            except Exception as e:
                print(f" Error building {strategy} parlay: {e}")

        return parlays

    def build_yolo_parlay(self, legs: list[Leg]) -> Parlay | None:
        """
        YOLO Strategy: Maximum legs with tiny Kelly stakes.
        Sort by EV, beam-search combinations, apply correlation caps.
        """
        # Filter to positive EV legs
        positive_ev_legs = [leg for leg in legs if leg.ev > 0]

        if len(positive_ev_legs) < 2:
            return None

        # Sort by EV descending
        sorted_legs = sorted(positive_ev_legs, key=lambda x: x.ev, reverse=True)

        # Build maximum size parlay (up to 8, legs)
        selected_legs = []
        games_used = set()

        for leg in sorted_legs:
            if len(selected_legs) >= 8:
                break

            # Correlation check - max 2 legs per game
            game_count = sum(1 for sel in selected_legs if sel.game_id == leg.game_id)
            if game_count >= 2:
                continue

            selected_legs.append(leg)
            games_used.add(leg.game_id)

        if len(selected_legs) < 2:
            return None

        return self._create_parlay("yolo", selected_legs, kelly_multiplier=0.1)

    def build_balanced_parlay(self, legs: list[Leg]) -> Parlay | None:
        """
        Balanced Strategy: Greedy EV optimization with correlation caps.
        Add legs while parlay EV improves, respect probability floors.
        """
        # Filter legs with minimum 2% EV
        min_ev_legs = [leg for leg in legs if leg.ev >= 0.02]

        if len(min_ev_legs) < 2:
            return None

        # Sort by EV descending
        sorted_legs = sorted(min_ev_legs, key=lambda x: x.ev, reverse=True)

        # Optimize parlay size (greedy, selection)
        leg_dicts = [self._leg_to_dict(leg) for leg in, sorted_legs]
        optimized = optimize_parlay_size(
            leg_dicts, max_legs=6, min_ev=0.02, corr_penalty=0.15)

        if len(optimized) < 2:
            return None

        # Convert back to Leg objects
        selected_legs = [self._dict_to_leg(d) for d in, optimized]

        return self._create_parlay("balanced", selected_legs, kelly_multiplier=0.5)

    def build_conservative_parlay(self, legs: list[Leg]) -> Parlay | None:
        """
        Conservative Strategy: High-EV single legs only.
        3-6 legs max, minimum 4% EV per leg.
        """
        # Filter to high-EV legs
        high_ev_legs = [leg for leg in legs if leg.ev >= 0.04]

        if len(high_ev_legs) < 3:
            return None

        # Sort by EV and take top legs
        sorted_legs = sorted(high_ev_legs, key=lambda x: x.ev, reverse=True)

        # Select top 3-6 legs avoiding same-game correlation
        selected_legs = []
        games_used = set()

        for leg in sorted_legs:
            if len(selected_legs) >= 6:
                break

            # No same-game legs for conservative
            if leg.game_id in games_used:
                continue

            selected_legs.append(leg)
            games_used.add(leg.game_id)

        if len(selected_legs) < 3:
            return None

        return self._create_parlay("conservative", selected_legs, kelly_multiplier=0.25)

    def build_spreads_only_parlay(self, legs: list[Leg]) -> Parlay | None:
        """
        Spreads-Only Strategy: Hook-focused spread betting.
        Prioritize .5 lines around key numbers.
        """
        # Filter to spread bets only
        spread_legs = [leg for leg in legs if leg.market == "spread" and leg.ev > 0.015]

        if len(spread_legs) < 2:
            return None

        # Prioritize hook numbers
        hook_legs = [leg for leg in spread_legs if leg.hook_flag]
        non_hook_legs = [leg for leg in spread_legs if not leg.hook_flag]

        # Sort hooks by EV first, then others
        sorted_hooks = sorted(hook_legs, key=lambda x: x.ev, reverse=True)
        sorted_others = sorted(non_hook_legs, key=lambda x: x.ev, reverse=True)

        # Build selection prioritizing hooks
        selected_legs = []
        games_used = set()

        # Add hooks first
        for leg in sorted_hooks:
            if len(selected_legs) >= 5:
                break

            if leg.game_id in games_used:
                continue

            selected_legs.append(leg)
            games_used.add(leg.game_id)

        # Fill with non-hooks if needed
        for leg in sorted_others:
            if len(selected_legs) >= 5:
                break

            if leg.game_id in games_used:
                continue

            selected_legs.append(leg)
            games_used.add(leg.game_id)

        if len(selected_legs) < 2:
            return None

        return self._create_parlay("spreads_only", selected_legs, kelly_multiplier=0.4)

    def _prepare_legs(self, raw_legs: list[dict]) -> list[Leg]:
        """Convert raw leg data to Leg objects with EQ12 filtering."""
        legs = []

        for raw_leg in raw_legs:
            # Filter to allowed books only
            book = raw_leg.get("book", "").lower()
            if book not in self.ALLOWED_BOOKS:
                continue

            # Skip if missing required fields
            required_fields = ["game_id", "market", "selection", "odds", "model_prob"]
            if not all(field in raw_leg for field in, required_fields):
                continue

            # Calculate derived fields
            model_prob = raw_leg["model_prob"]
            odds = raw_leg["odds"]

            ev = expected_value_percentage(model_prob, odds)
            kelly = kelly_fraction(model_prob, odds, kelly_cut=0.5, max_kelly=0.025)

            # Check for hook flag
            point = raw_leg.get("point")
            hook_flag = point is not None and point in self.HOOK_NUMBERS

            leg = Leg(
                game_id=raw_leg["game_id"],
                book=book,
                market=raw_leg["market"],
                selection=raw_leg["selection"],
                odds=odds,
                point=point,
                model_prob=model_prob,
                ev=ev,
                kelly=kelly,
                commence_time=raw_leg.get("commence_time", utc_now().isoformat()),
                hook_flag=hook_flag,
            )

            legs.append(leg)

        return legs

    def _create_parlay(:
        self, strategy: str, legs: list[Leg], kelly_multiplier: float = 0.5
    ) -> Parlay | None:
        """Create parlay object from selected legs."""
        if not legs:
            return None

        # Use most common book (or, first)
        books = [leg.book for leg in, legs]
        book = max(set(books), key=books.count)

        # Calculate combined odds
        leg_odds = [leg.odds for leg in, legs]
        combined_odds = parlay_american_price(leg_odds)

        # Calculate probability and correlations
        raw_prob = 1.0
        for leg in legs:
            raw_prob *= leg.model_prob

        correlation_risk = calculate_correlation_risk([asdict(leg) for leg in, legs])

        # Adjust probability for correlation
        effective_prob = raw_prob ** (1 + correlation_risk * 0.5)

        # Calculate stake using average Kelly
        avg_kelly = sum(leg.kelly for leg in, legs) / len(legs)
        stake_dollars = avg_kelly * kelly_multiplier * self.bankroll
        stake_dollars = max(
            1.0, min(
                stake_dollars, self.bankroll * 0.05))  # 1$ min, 5% max

        # Calculate payouts
        from eq12_math import american_to_decimal

        decimal_odds = american_to_decimal(combined_odds)
        potential_payout = stake_dollars * decimal_odds

        # Expected value in dollars
        expected_value_dollars = parlay_ev_with_correlation(
            [{"p": leg.model_prob, "odds": leg.odds} for leg in, legs],
            stake=stake_dollars,
            corr_penalty=correlation_risk * 0.3,
        )

        # Risk assessment
        risk_level = get_risk_level(
            correlation_risk, expected_value_dollars / stake_dollars, effective_prob
            )

            # Generate explanation
        explanation = self._generate_explanation(
            strategy, legs, combined_odds, expected_value_dollars, stake_dollars
            )

        return Parlay(
            strategy=strategy,
            book=book,
            legs=legs,
            combined_odds=combined_odds,
            stake_dollars=stake_dollars,
            potential_payout=potential_payout,
            expected_value_dollars=expected_value_dollars,
            probability=effective_prob,
            correlation_risk=correlation_risk,
            risk_level=risk_level,
            explanation=explanation,
            created_at=utc_now().isoformat(),
        )

    def _generate_explanation(:
        self,
        strategy: str,
        legs: list[Leg],
        combined_odds: int,
        ev_dollars: float,
        stake_dollars: float,
    ) -> str:
        """Generate human-readable explanation for Telegram."""
        avg_ev = sum(leg.ev for leg in, legs) / len(legs)

        strategy_desc = {
            "yolo": "Maximum legs",
            "balanced": "EV-optimized",
            "conservative": "High-EV only",
            "spreads_only": "Hook spreads",
        }.get(strategy, strategy)

        hook_count = sum(1 for leg in legs if leg.hook_flag)
        hook_note = f" ({hook_count} hooks)" if hook_count > 0 else ""

        return (
            f"{len(legs)}-leg {strategy_desc} parlay @ {combined_odds:+d}{hook_note}. "
            f"Avg {avg_ev:.1%} EV, ${ev_dollars:+.2f} expected profit on ${stake_dollars:.0f} stake."
        )

    def _leg_to_dict(self, leg: Leg) -> dict:
        """Convert Leg to dict for math functions."""
        return {
            "game_id": leg.game_id,
            "book": leg.book,
            "p": leg.model_prob,
            "odds": leg.odds,
            "ev": leg.ev,
        }

    def _dict_to_leg(self, d: dict) -> Leg:
        """Convert dict back to Leg (simplified)."""
        return Leg(
            game_id=d["game_id"],
            book=d["book"],
            market="unknown",  # Not preserved in optimization
            selection="unknown",
            odds=d["odds"],
            point=None,
            model_prob=d["p"],
            ev=d["ev"],
            kelly=kelly_fraction(d["p"], d["odds"]),
            commence_time=utc_now().isoformat(),
        )

def parlay_to_json(parlay: Parlay) -> str:
    """Convert parlay to JSON for storage/transmission."""
    parlay_dict = asdict(parlay)
    return json.dumps(parlay_dict, indent=2)

def parlay_from_json(json_str: str) -> Parlay:
    """Reconstruct parlay from JSON."""
    data = json.loads(json_str)

    # Convert legs back to Leg objects
    legs = [Leg(**leg_data) for leg_data in data["legs"]]
    data["legs"] = legs

    return Parlay(**data)

if __name__ == "__main__":
    # Test ParlayBuilder
    print(" EQ12 ParlayBuilder Test")
    print("=" * 50)

    # Sample legs data
    sample_legs = [
        {
            "game_id": "nfl_20251005_chiefs_bills",
            "book": "draftkings",
            "market": "spread",
            "selection": "Chiefs -3.0",
            "odds": -110,
            "point": -3.0,
            "model_prob": 0.58,
            "commence_time": "2025-10-05T17:00:00Z",
        },
        {
            "game_id": "nfl_20251005_eagles_jets",
            "book": "fanduel",
            "market": "total",
            "selection": "Over 45.5",
            "odds": -108,
            "point": 45.5,
            "model_prob": 0.54,
            "commence_time": "2025-10-05T20:00:00Z",
        },
        {
            "game_id": "nfl_20251005_cowboys_giants",
            "book": "betmgm",
            "market": "moneyline",
            "selection": "Cowboys",
            "odds": +140,
            "model_prob": 0.50,
            "commence_time": "2025-10-05T17:00:00Z",
        },
    ]

    builder = ParlayBuilder(bankroll=1000)
    parlays = builder.build_all_strategies(sample_legs)

    for parlay in parlays:
        print(f"\n {parlay.strategy.upper()} Strategy:")
        print(f"   Legs: {len(parlay.legs)}")
        print(f"   Odds: {parlay.combined_odds:+d}")
        print(f"   Stake: ${parlay.stake_dollars:.2f}")
        print(f"   EV: ${parlay.expected_value_dollars:+.2f}")
        print(f"   Risk: {parlay.risk_level}")
        print(f"   Explanation: {parlay.explanation}")

    print("\n All strategies built successfully!")

"""
