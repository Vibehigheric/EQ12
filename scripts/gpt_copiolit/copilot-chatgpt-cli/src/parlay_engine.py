"""
Simple parlay calculation helpers.

Functions:
- fractional_to_decimal(frac: str) -> float
- calculate_parlay_payout_decimal(odds, stake) -> float

Odds may be:
 - decimal odds as float/int (e.g. 1.5, 2.25)
 - decimal odds as string (e.g. "1.5")
 - fractional odds as string (e.g. "1/2", "3/1")
"""

from collections.abc import Iterable
from typing import Union

OddsType = Union[float, int, str]


def fractional_to_decimal(frac: str) -> float:
    """Convert fractional odds like "3/1" to decimal odds (4.0)."""
    parts = frac.strip().split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid fractional odds: {frac!r}")
    try:
        num = float(parts[0])
        den = float(parts[1])
    except ValueError:
        raise ValueError(f"Invalid numbers in fractional odds: {frac!r}")
    if den == 0:
        raise ValueError("Denominator in fractional odds cannot be zero")
    return 1.0 + (num / den)


def _parse_single_odd(o: OddsType) -> float:
    """Normalize a single odd to decimal form (float)."""
    if isinstance(o, (int, float)):
        return float(o)
    s = o.strip()
    if "/" in s:
        return fractional_to_decimal(s)
    try:
        return float(s)
    except ValueError:
        raise ValueError(f"Unrecognized odds format: {o!r}")
    raise TypeError(f"Unsupported odds type: {type(o).__name__}")


def calculate_parlay_payout_decimal(odds: Iterable[OddsType], stake: float) -> float:
    """
    Calculate total payout for a parlay expressed in decimal odds.

    - odds: iterable of odds (decimal floats/ints or strings, or fractional strings)
    - stake: amount staked (must be >= 0)

    Returns the total return (stake * product of decimal odds).
    Raises ValueError for empty odds or invalid values.
    """
    if stake < 0:
        raise ValueError("stake must be >= 0")
    odds_list: list[float] = [_parse_single_odd(o) for o in odds]
    if len(odds_list) == 0:
        raise ValueError("No odds provided")
    product = 1.0
    for d in odds_list:
        product *= d
    return stake * product


__all__ = [
    "calculate_parlay_payout_decimal",
    "fractional_to_decimal",
]
