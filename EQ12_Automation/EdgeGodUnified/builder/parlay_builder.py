import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any

from models.ev import edge_ev
from models.monte_carlo import simulate_parlay_win_prob


def _is_il_excluded(player: str, il_list: list[str]) -> bool:
    if not player:
        return False
    return any(player.strip().lower() == il.strip().lower() for il in il_list)


def _same_game_conflict(legs: list[dict[str, Any]]) -> bool:
    by_game = {}
    for leg in legs:
        game = leg.get("game_id")
        market = leg.get("market")
        if game not in by_game:
            by_game[game] = set()
        by_game[game].add(market)
    for markets in by_game.values():
        if "ML" in markets and "Spread" in markets:
            return True
    return False


def _apply_star_for_tb_hits(leg: dict[str, Any], star_threshold: float) -> dict[str, Any]:
    if leg.get("market") in ("TB", "Hits") and leg.get("side", "").lower() == "over":
        prob_over_2 = leg.get("proj_over_2_prob", 0.0)
        if prob_over_2 and prob_over_2 >= star_threshold:
            leg["starred"] = True
            leg["display_name"] = "**" + leg.get("display_name", "")
    return leg


def _filter_and_normalize_legs(
    rows: list[dict[str, Any]], cfg: dict[str, Any]
) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        market = (r.get("market") or "").strip()
        side = (r.get("side") or "").strip()
        player = r.get("player") or ""
        game_id = r.get("game_id") or ""

        if market == "HR":
            if cfg["hr_rules"].get("require_player_name", True) and not player:
                continue
            if not cfg["hr_rules"].get("allow_under", False) and side.lower() == "under":
                continue

        if player and _is_il_excluded(player, cfg.get("il_exclusions", [])):
            continue

        try:
            obj = {
                "display_name": r.get("display_name") or f"{market} {side}",
                "market": market,
                "side": side,
                "player": player,
                "game_id": game_id,
                "odds": int(r.get("odds")) if r.get("odds") is not None else None,
                "true_prob": (
                    float(r.get("true_prob")) if r.get("true_prob") is not None else None
                ),
                "proj_over_2_prob": (
                    float(r.get("proj_over_2_prob"))
                    if r.get("proj_over_2_prob") is not None
                    else 0.0
                ),
            }
        except Exception:
            continue
        obj = _apply_star_for_tb_hits(obj, cfg.get("star_threshold_tb_hits_prob_over_2_tb", 0.5))
        out.append(obj)
    return out


def _cap_by_market(legs: list[dict[str, Any]], caps: dict[str, int]) -> list[dict[str, Any]]:
    counts = {"MLB-ML": 0, "MLB-Spread": 0, "MLB-OU": 0, "TB": 0, "Hits": 0, "HR": 0}
    kept = []
    for leg in legs:
        m = leg["market"]
        key = m
        if m == "ML":
            key = "MLB-ML"
        if m == "Spread":
            key = "MLB-Spread"
        if m == "OU":
            key = "MLB-OU"
        if key not in counts:
            kept.append(leg)
            continue
        mapping = {
            "MLB-ML": "mlb_ml",
            "MLB-Spread": "mlb_spread",
            "MLB-OU": "mlb_ou",
            "TB": "tb",
            "Hits": "hits",
            "HR": "hr",
        }
        limit = caps.get(mapping.get(key, key), 999)
        if counts[key] < limit:
            kept.append(leg)
            counts[key] += 1
    return kept


def build_parlays(rows: list[dict[str, Any]], cfg: dict[str, Any]) -> dict[str, Any]:
    legs = _filter_and_normalize_legs(rows, cfg)
    legs = _cap_by_market(legs, cfg.get("caps", {}))

    scored = []
    for leg in legs:
        tp = leg.get("true_prob")
        odds = leg.get("odds")
        if tp is None or odds is None:
            continue
        ev = edge_ev(tp, odds)
        leg["ev_percent"] = ev
        scored.append(leg)
    scored.sort(key=lambda x: x["ev_percent"], reverse=True)

    tickets = {}

    five = []
    for leg in scored:
        if len(five) >= 5:
            break
        trial = five + [leg]
        if cfg.get("no_same_game_ml_and_spread", True) and _same_game_conflict(trial):
            continue
        if leg["ev_percent"] >= cfg.get("min_ev_percent", 5.0):
            five.append(leg)
    tickets["five_leg_mixed"] = five

    ten = []
    for leg in scored:
        if len(ten) >= 10:
            break
        trial = ten + [leg]
        if cfg.get("no_same_game_ml_and_spread", True) and _same_game_conflict(trial):
            continue
        ten.append(leg)
    tickets["ten_leg_mixed"] = ten

    hr_legs = [l for l in scored if l["market"] == "HR"][: cfg["caps"]["hr"]]
    tickets["hr_three_leg"] = hr_legs[:3]

    def parlay_prob(ls) -> bool:
        probs = [x["true_prob"] for x in ls if x.get("true_prob") is not None]
        if not probs:
            return 0.0
        return simulate_parlay_win_prob(probs, cfg.get("simulations", 20000))

    for key in list(tickets.keys()):
        tickets[key + "_true_win_prob"] = parlay_prob(tickets[key])

    return tickets
