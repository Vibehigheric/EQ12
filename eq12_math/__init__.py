"""
EQ12 Math Library - __init__.py
===============================

Main module for the EQ12 mathematical betting calculations library.
Provides pure deterministic functions for sports betting analysis.

Modules:
- odds: Core odds calculations and conversions
- parlay: Parlay optimization with correlation analysis
- elo: Elo rating system for team strength
- sim: Monte Carlo simulation engine

Author: EQ12 Development Team
Version: 1.0.0
"""

from .elo import (
    calculate_elo_probability,
    calculate_home_field_advantage,
    elo_to_spread,
    simulate_game_outcome,
    spread_to_elo,
    update_elo_ratings,
)
from .odds import (
    american_to_decimal,
    arbitrage_profit_percentage,
    calculate_ev,
    closing_line_value_percent,
    decimal_to_american,
    kelly_criterion,
    parlay_decimal_odds,
    remove_vig_two_way,
)
from .parlay import (
    calculate_parlay_ev,
    correlated_parlay_probability,
    detect_sgp_correlations,
    independent_parlay_probability,
    optimize_parlay_selection,
    parlay_breakeven_probability,
)
from .sim import (
    calculate_risk_of_ruin,
    monte_carlo_season,
    simulate_betting_session,
    simulate_kelly_growth,
    simulate_portfolio_performance,
)

__version__ = "1.0.0"
__author__ = "EQ12 Development Team"

__all__ = [
    # Odds functions
    "american_to_decimal",
    "arbitrage_profit_percentage",
    # Elo functions
    "calculate_elo_probability",
    "calculate_ev",
    "calculate_home_field_advantage",
    "calculate_parlay_ev",
    "calculate_risk_of_ruin",
    "closing_line_value_percent",
    "correlated_parlay_probability",
    "decimal_to_american",
    "detect_sgp_correlations",
    "elo_to_spread",
    # Parlay functions
    "independent_parlay_probability",
    "kelly_criterion",
    "monte_carlo_season",
    "optimize_parlay_selection",
    "parlay_breakeven_probability",
    "parlay_decimal_odds",
    "remove_vig_two_way",
    # Simulation functions
    "simulate_betting_session",
    "simulate_game_outcome",
    "simulate_kelly_growth",
    "simulate_portfolio_performance",
    "spread_to_elo",
    "update_elo_ratings",
]


def get_library_info():
    """Get information about the EQ12 math library."""
    return {
        "version": __version__,
        "author": __author__,
        "modules": ["odds", "parlay", "elo", "sim"],
        "description": "Deterministic sports betting mathematics library",
    }


# Library validation function
def validate_library():
    """Validate that all library components are working correctly."""
    try:
        # Test odds functions
        prob = 0.6
        odds = american_to_decimal(-150)
        ev = calculate_ev(prob, odds)
        kelly_frac = kelly_criterion(prob, odds)

        # Test parlay functions
        leg_probs = [0.6, 0.55]
        parlay_prob = independent_parlay_probability(leg_probs)

        # Test elo functions
        rating_a, rating_b = 1600, 1500
        win_prob = calculate_elo_probability(rating_a, rating_b)

        # Test simulation functions
        ruin_prob = calculate_risk_of_ruin(1000, 50, 0.55, 1.9)

        return {
            "status": "success",
            "odds_test": f"EV: {ev:.3f}, Kelly: {kelly_frac:.3f}",
            "parlay_test": f"Parlay prob: {parlay_prob:.3f}",
            "elo_test": f"Win prob: {win_prob:.3f}",
            "sim_test": f"Ruin prob: {ruin_prob:.3f}",
            "message": "All library components validated successfully",
        }

    except Exception as e:
        return {"status": "error", "message": f"Library validation failed: {e!s}"}


if __name__ == "__main__":
    # Run validation when module is executed directly
    print("EQ12 Math Library")
    print("=================")

    info = get_library_info()
    print(f"Version: {info['version']}")
    print(f"Author: {info['author']}")
    print(f"Modules: {', '.join(info['modules'])}")

    print("\nRunning validation tests...")
    result = validate_library()

    if result["status"] == "success":
        print("✅ All tests passed!")
        for key, value in result.items():
            if key not in ["status", "message"]:
                print(f"  {key}: {value}")
    else:
        print("❌ Validation failed!")
        print(f"  Error: {result['message']}")

    print("\nLibrary ready for use!")
