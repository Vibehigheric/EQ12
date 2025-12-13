# EQ12 NCAA Week 7 Parlay Builder
# Generates conference-aware parlays (5, 10, 20 legs) and a Top 25 master ticket.
# [Unverified] Generated orchestration code wired to EQ12 conventions.
import json
import os
import random
from datetime import datetime
from typing import Any

os.makedirs("logs/parlays", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Resilience & Unicode
from eq12_unicode_guard import *

# ---- Configuration ----
DEFAULT_CONF = {
    "edge_min": 0.08,
    "sentiment_min": 0.6,
    "max_wind_mph": 15,
    "week": 7,
    "bankroll": 1000.0,
    "kelly_fraction": 0.25,
    "simulate_if_missing": True,
}

CONFERENCES = [
    "SEC",
    "Big Ten",
    "ACC",
    "Big 12",
    "American",
    "Mountain West",
    "MAC",
    "Sun Belt",
    "Pac-12",
    "Independent",
]


# ---- Stubs to integrate with real EQ12 when present ----
def _load_eq12_config() -> dict[str, Any]:
    try:
        with open("sports_betting_config.json", encoding="utf-8") as f:
            cfg = json.load(f)
        xcfg = cfg.get("EQ12_PARLAY", {})
        return {**DEFAULT_CONF, **xcfg}
    except Exception:
        return DEFAULT_CONF.copy()


def _engine_fetch_games(conference: str, week: int) -> list[dict[str, Any]]:
    """
    Expected to call eq12_pro_sports_betting.fetch_odds_data(...).
    Fallback to simulated fixtures if engine not available.
    """
    try:
        import eq12_pro_sports_betting as engine  # real integration

        return engine.fetch_odds_data(sport="NCAA", conference=conference, week=week)
    except Exception:
        # Simulated games (for offline use)
        random.seed(hash(conference) % 2**32)
        teams = [f"{conference} Team {i}" for i in range(1, 40)]
        games = []
        for i in range(0, len(teams), 2):
            if i + 1 >= len(teams):
                break
            edge = round(max(0, random.gauss(0.1, 0.05)), 3)
            odds = random.choice([-110, -105, +100, +110, +125, +135])
            sentiment = round(min(1.0, max(0.0, random.gauss(0.65, 0.15))), 2)
            wind = max(0, int(random.gauss(9, 6)))
            games.append(
                {
                    "home": teams[i],
                    "away": teams[i + 1],
                    "market": random.choice(["ML", "Spread", "Total"]),
                    "bet": random.choice(["Home", "Away", "Over", "Under"]),
                    "odds": odds,
                    "edge": edge,
                    "sentiment": sentiment,
                    "wind_mph": wind,
                    "injury_flag": random.random() < 0.05,
                    "is_top25": random.random() < 0.25,
                }
            )
        return games


def _clv_positive(_g) -> bool:
    # Placeholder: integrate with stored CLV when available
    return True


def _kelly_percent(true_edge: float) -> float:
    # Simplified: map edge to implied kelly %, bounded
    return round(min(3.0, max(0.1, true_edge * 10.0)), 2)


def _score_leg(g: dict[str, Any]) -> float:
    # Combine edge and sentiment (basic composite)
    return g["edge"] * (0.5 + 0.5 * g["sentiment"])


# ---- Parlay Builder ----
def _filter_and_rank(games: list[dict[str, Any]], cfg: dict[str, Any]) -> list[dict[str, Any]]:
    filtered = []
    for g in games:
        if g.get("injury_flag"):
            continue
        if g["edge"] < cfg["edge_min"]:
            continue
        if g["sentiment"] < cfg["sentiment_min"]:
            continue
        if g.get("wind_mph", 0) > cfg["max_wind_mph"] and g["market"] in (
            "Total",
            "ML",
        ):
            continue
        if not _clv_positive(g):
            continue
        g = dict(g)
        g["score"] = _score_leg(g)
        filtered.append(g)
    filtered.sort(key=lambda x: x["score"], reverse=True)
    return filtered


def _compose_ticket(legs: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    return legs[: min(count, len(legs))]


def _combined_odds(legs: list[dict[str, Any]]) -> float:
    # Approximate American odds multiplication using decimal conversion
    if not legs:
        return 0.0
    dec = 1.0
    for l in legs:
        a = l["odds"]
        if a >= 0:
            dec *= 1 + a / 100.0
        else:
            dec *= 1 + 100.0 / abs(a)
    # convert back to American (approx)
    if dec >= 2.0:
        return round((dec - 1.0) * 100.0, 0)
    return round(-100.0 / (dec - 1.0), 0)


def _est_win_prob(legs: list[dict[str, Any]]) -> float:
    # Multiply individual win probs roughly from edge (toy model)
    p = 1.0
    for l in legs:
        base = 0.55  # baseline for filtered picks
        p *= min(0.99, base + l["edge"] * 0.5)
    return round(p, 4)


def _ticket_table(legs: list[dict[str, Any]]) -> str:
    lines = [
        "| # | Matchup | Pick Type | Bet | Odds | Conf | Kelly% | Sent | Wind | Edge% |",
        "|---|---------|-----------|-----|------|------|--------|------|------|-------|",
    ]
    for i, l in enumerate(legs, 1):
        matchup = f"{l['away']} @ {l['home']}"
        conf = f"{round((0.55 + l['edge'] * 0.5) * 100, 1)}%"
        kelly = f"{_kelly_percent(l['edge'])}%"
        edgep = f"{round(l['edge'] * 100, 1)}%"
        lines.append(
            f"| {i} | {sanitize_text(matchup)} | {l['market']} | {l['bet']} | {l['odds']} | {conf} | {kelly} | {l['sentiment']} | {l.get('wind_mph', 0)} | {edgep} |"
        )
    return "\n".join(lines)


def _save_outputs(name: str, legs: list[dict[str, Any]], meta: dict[str, Any]):
    stamp = datetime.utcnow().isoformat()
    log_path = os.path.join("logs", "parlays", f"{name}.log")
    json_path = os.path.join("outputs", f"{name}.json")
    with open(log_path, "a", encoding="utf-8", errors="replace") as f:
        f.write(f"[{stamp}] {name}\n")
        f.write(_ticket_table(legs) + "\n")
        f.write(json.dumps(meta, indent=2) + "\n\n")
    with open(json_path, "w", encoding="utf-8", errors="replace") as f:
        json.dump({"name": name, "legs": legs, "meta": meta}, f, indent=2, ensure_ascii=False)


def build_for_conference(conf: str, cfg: dict[str, Any]):
    games = _engine_fetch_games(conf, cfg["week"])
    ranked = _filter_and_rank(games, cfg)
    tickets = {
        "lock5": _compose_ticket(ranked, 5),
        "balanced10": _compose_ticket(ranked, 10),
        "highpay20": _compose_ticket(ranked, 20),
    }
    results = {}
    for key, legs in tickets.items():
        meta = {
            "conference": conf,
            "week": cfg["week"],
            "legs": len(legs),
            "combined_american_odds": _combined_odds(legs),
            "est_win_prob": _est_win_prob(legs),
            "bankroll": cfg["bankroll"],
            "kelly_fraction": cfg["kelly_fraction"],
            "generated_utc": datetime.utcnow().isoformat(),
        }
        name = f"{conf.lower().replace(' ', '')}_week{cfg['week']}_{key}"
        _save_outputs(name, legs, meta)
        results[key] = {"legs": legs, "meta": meta}
    return results


def build_top25(cfg: dict[str, Any]) -> dict[str, Any]:
    # Collate from all conferences and filter is_top25
    pool = []
    for conf in CONFERENCES:
        games = _engine_fetch_games(conf, cfg["week"])
        ranked = _filter_and_rank([g for g in games if g.get("is_top25")], cfg)
        pool.extend(ranked[:5])  # take the best few from each
    pool.sort(key=lambda x: x["score"], reverse=True)
    top20 = _compose_ticket(pool, 20)
    meta = {
        "conference": "Top25",
        "week": cfg["week"],
        "legs": len(top20),
        "combined_american_odds": _combined_odds(top20),
        "est_win_prob": _est_win_prob(top20),
        "bankroll": cfg["bankroll"],
        "generated_utc": datetime.utcnow().isoformat(),
    }
    name = f"top25_week{cfg['week']}_elite20"
    _save_outputs(name, top20, meta)
    return {"legs": top20, "meta": meta}


def main():
    cfg = _load_eq12_config()
    summary = {}
    for conf in CONFERENCES:
        res = build_for_conference(conf, cfg)
        summary[conf] = res
        print(f"[Build] {conf}: 5/10/20 tickets generated.")
    t25 = build_top25(cfg)
    summary["Top25"] = t25
    with open(
        os.path.join("outputs", f"ncaa_week{cfg['week']}_summary.json"),
        "w",
        encoding="utf-8",
        errors="replace",
    ) as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print("[Done] Outputs written to ./logs/parlays and ./outputs")


if __name__ == "__main__":
    main()
