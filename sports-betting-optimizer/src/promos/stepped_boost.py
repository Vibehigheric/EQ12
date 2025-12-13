from dataclasses import dataclass

from ..core.ev_calc import (
    boosted_payout_from_decimal,
    decimal_to_american,
    product_decimal,
    product_prob,
)

MIN_LEGS = 4
MIN_PER_LEG_DECIMAL = 1.25  # -400
MAX_BOOST = 105.0


@dataclass
class Leg:
    label: str
    american: int
    decimal: float
    fair_prob: float
    game: str


def boost_pct_for_legs(n: int) -> float:
    return min(20 + (n - 4) * 10, MAX_BOOST)


def validate(legs: list[Leg], stake: float) -> tuple[bool, str]:
    if len(legs) < MIN_LEGS:
        return False, f"Need >= {MIN_LEGS} legs"
    for l in legs:
        if l.decimal < MIN_PER_LEG_DECIMAL:
            return False, "Each leg must be >= -400 (dec 1.25)"
    if stake > 100:
        return False, "Stake must be <= $100"
    return True, "OK"


def score(legs: list[Leg], stake: float):
    dec = product_decimal([l.decimal for l in legs])
    pwin = product_prob([l.fair_prob for l in legs])
    boost = boost_pct_for_legs(len(legs))
    payout = boosted_payout_from_decimal(stake, dec, boost)
    profit = payout - stake
    ev = pwin * profit - (1 - pwin) * stake
    return {
        "combined_decimal": dec,
        "combined_american": decimal_to_american(dec),
        "p_win": pwin,
        "boost_pct": boost,
        "boosted_payout": payout,
        "boosted_profit": profit,
        "ev": ev,
    }
