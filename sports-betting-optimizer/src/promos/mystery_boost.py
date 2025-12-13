from dataclasses import dataclass

from ..core.ev_calc import (
    boosted_payout_from_decimal,
    decimal_to_american,
    product_decimal,
    product_prob,
)

MIN_LEGS = 3
MIN_COMBINED_DECIMAL = 4.0
VALID_TOKENS = {25, 33, 50}


@dataclass
class Leg:
    label: str
    american: int
    decimal: float
    fair_prob: float
    game: str


def validate(legs: list[Leg], stake: float, token: int) -> tuple[bool, str]:
    if token not in VALID_TOKENS:
        return False, "Token must be 25, 33, or 50%"
    if len(legs) < MIN_LEGS:
        return False, f"Need >= {MIN_LEGS} legs"
    dec = product_decimal([l.decimal for l in legs])
    if dec < MIN_COMBINED_DECIMAL:
        return False, "Combined odds must be >= +300 (dec 4.0)"
    if stake > 100:
        return False, "Stake must be <= $100"
    return True, "OK"


def score(legs: list[Leg], stake: float, token: int):
    dec = product_decimal([l.decimal for l in legs])
    pwin = product_prob([l.fair_prob for l in legs])
    payout = boosted_payout_from_decimal(stake, dec, token)
    profit = payout - stake
    ev = pwin * profit - (1 - pwin) * stake
    return {
        "combined_decimal": dec,
        "combined_american": decimal_to_american(dec),
        "p_win": pwin,
        "boosted_payout": payout,
        "boosted_profit": profit,
        "ev": ev,
    }
