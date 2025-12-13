import random

from .ev import clamp_prob


def simulate_parlay_win_prob(legs, sims=20000):
    probs = [clamp_prob(p) for p in legs if p is not None]
    if not probs:
        return 0.0
    wins = 0
    for _ in range(int(sims)):
        ok = True
        for p in probs:
            if random.random() > p:
                ok = False
                break
        if ok:
            wins += 1
    return wins / float(sims)
