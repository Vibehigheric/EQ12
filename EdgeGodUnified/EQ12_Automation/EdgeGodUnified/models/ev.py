from math import isfinite


def american_to_prob(odds) -> None:
    if odds is None:
        return None
    o = float(odds)
    if o > 0:
        return 100.0 / (o + 100.0)
    return -o / (-o + 100.0)


def prob_to_american(p) -> None:
    if p <= 0 or p >= 1:
        return None
    if p >= 0.5:
        return int(round(-(p / (1 - p)) * 100))
    return int(round(((1 - p) / p) * 100))


def edge_ev(true_p, book_odds) -> None:
    o = float(book_odds)
    payout = o / 100.0 if o > 0 else 100.0 / abs(o)
    ev = true_p * payout - (1 - true_p)
    return ev * 100.0


def clamp_prob(p) -> None:
    p = float(p)
    if not isfinite(p):
        return 0.0
    return max(1e-6, min(1 - 1e-6, p))
