#!/usr/bin/env python3
import argparse
import itertools
from dataclasses import dataclass

import requests

from ..core.ev_calc import american_to_decimal, devig_two_way
from ..core.odds_fetcher import fetch_odds
from ..core.utils import resolve_telegram
from . import mystery_boost as mystery
from . import stepped_boost as stepped

# Extension Integration - Auto-export slips to browser extension
try:
    from ..core.slip_export import export_optimizer_result

    EXTENSION_EXPORT = True
except ImportError:
    EXTENSION_EXPORT = False

    def export_optimizer_result(args, result, bridge_dir=None):
        pass


DK_NAMES = ["DraftKings", "Draft Kings", "DraftKings Sportsbook"]


@dataclass
class Leg:
    label: str
    american: int
    decimal: float
    fair_prob: float
    game: str


def is_half_point(x: float) -> bool:
    return abs(x - round(x)) >= 0.25 and abs((x * 2) - round(x * 2)) < 1e-9


def extract_pairs(game, market_key):
    pairs = []
    dk_map = {}
    for bm in game.get("bookmakers", []):
        title = bm.get("title", "")
        m = next((mm for mm in bm.get("markets", []) if mm.get("key") == market_key), None)
        if not m:
            continue
        oc = m.get("outcomes", [])
        if len(oc) != 2:
            continue
        a, b = oc[0], oc[1]
        pairs.append(
            (
                a["name"],
                int(a["price"]),
                a.get("point"),
                b["name"],
                int(b["price"]),
                b.get("point"),
            )
        )
        if any(k.lower() in title.lower() for k in DK_NAMES):
            dk_map[a["name"]] = (int(a["price"]), a.get("point"))
            dk_map[b["name"]] = (int(b["price"]), b.get("point"))
    return dk_map, pairs


def fair_probs(pairs):
    agg, cnt = {}, {}
    for a, a_price, _a_pt, b, b_price, _b_pt in pairs:
        pa, pb = devig_two_way(a_price, b_price)
        if pa is None:
            continue
        agg[a] = agg.get(a, 0.0) + pa
        cnt[a] = cnt.get(a, 0) + 1
        agg[b] = agg.get(b, 0.0) + pb
        cnt[b] = cnt.get(b, 0) + 1
    return {k: agg[k] / cnt[k] for k in agg}


def build_candidates(game, allow_whole_lines=False, min_per_leg_decimal=1.2):
    legs: list[Leg] = []
    for market in ["h2h", "spreads", "totals"]:
        dk_map, pairs = extract_pairs(game, market)
        if not pairs or not dk_map:
            continue
        fair = fair_probs(pairs)
        home = game.get("home_team", "")
        away = game.get("away_team", "")
        for sel, (price, point) in dk_map.items():
            label = sel if market != "h2h" else f"{sel} ML"
            if market in ("spreads", "totals") and point is not None and not allow_whole_lines:
                try:
                    if not is_half_point(float(point)):
                        continue
                except Exception:
                    pass
            key = label if label in fair else sel
            if key not in fair:
                continue
            dec = american_to_decimal(price)
            if dec < min_per_leg_decimal:
                continue
            legs.append(
                Leg(
                    label=label,
                    american=int(price),
                    decimal=dec,
                    fair_prob=float(fair[key]),
                    game=f"{away} @ {home}",
                )
            )
    return legs


def filter_games_for_date(games, date_str):
    return [g for g in games if g.get("commence_time", "").startswith(date_str[:10])]


def run():
    ap = argparse.ArgumentParser(description="Master DK promo optimizer")
    ap.add_argument(
        "--sport",
        required=True,
        choices=["cfb", "nfl", "nba", "mlb", "nhl", "soccer", "ufc", "tennis"],
    )
    ap.add_argument("--promo", required=True, choices=["mystery", "stepped"])
    ap.add_argument("--promo-date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--stake", type=float, default=100.0)
    ap.add_argument(
        "--token",
        type=int,
        choices=[25, 33, 50],
        help="Mystery token % (required for mystery)",
    )
    ap.add_argument("--max-legs", type=int, default=5)
    ap.add_argument("--min-per-leg-decimal", type=float, default=1.2)
    ap.add_argument("--allow-whole-lines", action="store_true")
    ap.add_argument("--export-csv", action="store_true")
    ap.add_argument("--csv-file", default=None)
    ap.add_argument("--telegram", action="store_true")
    args = ap.parse_args()
    data = fetch_odds(args.sport, markets="h2h,spreads,totals", region="us")
    games = filter_games_for_date(data, args.promo_date)
    if len(games) < 3:
        raise SystemExit("Not enough games for parlays on this date.")
    per_game = []
    for g in games:
        legs = build_candidates(
            g,
            allow_whole_lines=args.allow_whole_lines,
            min_per_leg_decimal=args.min_per_leg_decimal,
        )
        if legs:
            per_game.append(legs)
    if len(per_game) < 3:
        raise SystemExit("Insufficient candidate legs across games.")
    best = None
    board = []
    for L in range(3, min(args.max_legs, len(per_game)) + 1):
        for subset in itertools.combinations(range(len(per_game)), L):
            pools = [per_game[i] for i in subset]
            for combo in itertools.product(*pools):
                legs = list(combo)
                if args.promo == "mystery":
                    if args.token is None:
                        raise SystemExit("--token required for mystery promo")
                    ok, msg = mystery.validate(legs, args.stake, args.token)
                    if not ok:
                        continue
                    row = mystery.score(legs, args.stake, args.token)
                else:
                    ok, _msg = stepped.validate(legs, args.stake)
                    if not ok:
                        continue
                    row = stepped.score(legs, args.stake)
                row["legs"] = legs
                row["legs_count"] = L
                if (best is None) or (row["ev"] > best["ev"]):
                    best = row
                board.append(row)
    board.sort(key=lambda x: x["ev"], reverse=True)
    if best is None:
        raise SystemExit("No valid combo met promo constraints.")

    print(f"✅ Best {args.sport.upper()} parlay for {args.promo} on {args.promo_date}")
    extra = (
        f"| Boost {best.get('boost_pct', '')}"
        if args.promo == "stepped"
        else f"| Token {args.token}%"
    )
    print(
        f"Legs: {best['legs_count']} | Odds {best['combined_american']:+d} (dec {best['combined_decimal']:.3f}) {extra}"
    )
    print(
        f"P(win): {best['p_win'] * 100:.2f}% | EV: ${best['ev']:.2f} | Boosted payout: ${best['boosted_payout']:.2f}"
    )
    for i, l in enumerate(best["legs"], 1):
        print(f"  {i}. {l.label} ({l.american:+d}) | {l.game}")

    # 📱🎮💰 Export to extension bridge + bankroll + Discord
    if EXTENSION_EXPORT:
        try:
            # Get Discord webhook from environment
            import os

            discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")

            # Export with full integration (bridge + bankroll + Discord)
            export_optimizer_result(args, best, discord_webhook=discord_webhook)

        except Exception as e:
            print(f"⚠️ Extension/bankroll export failed: {e}")

    if args.export_csv:
        import csv
        import os

        fname = args.csv_file or f"{args.sport}_{args.promo}_{args.promo_date}.csv"
        with open(fname, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "sport",
                    "promo",
                    "date",
                    "legs",
                    "odds_american",
                    "odds_decimal",
                    "p_win",
                    "boosted_payout",
                    "ev",
                    "legs_detail",
                ]
            )
            legs_detail = "; ".join(
                [
                    f"{i + 1}. {l.label} ({l.american:+d}) | {l.game}"
                    for i, l in enumerate(best["legs"])
                ]
            )
            w.writerow(
                [
                    args.sport,
                    args.promo,
                    args.promo_date,
                    best["legs_count"],
                    best["combined_american"],
                    f"{best['combined_decimal']:.4f}",
                    f"{best['p_win'] * 100:.2f}%",
                    f"{best['boosted_payout']:.2f}",
                    f"{best['ev']:.2f}",
                    legs_detail,
                ]
            )
        print(f"📁 Saved CSV: {os.path.abspath(fname)}")
    if args.telegram:
        tok, chat = resolve_telegram(interactive=True)
        if tok and chat:
            text = (
                f"✅ {args.sport.upper()} {args.promo} {args.promo_date}\nLegs {best['legs_count']} | {best['combined_american']:+d} (dec {best['combined_decimal']:.2f})\nP(win) {best['p_win'] * 100:.2f}% | EV ${best['ev']:.2f}\nBoosted payout ${best['boosted_payout']:.2f}\n"
                + "\n".join(
                    [
                        f"{i + 1}. {l.label} ({l.american:+d}) | {l.game}"
                        for i, l in enumerate(best["legs"])
                    ]
                )
            )
            try:
                requests.post(
                    f"https://api.telegram.org/bot{tok}/sendMessage",
                    json={"chat_id": chat, "text": text},
                    timeout=20,
                )
                print("📨 Telegram sent.")
            except Exception as e:
                print("⚠️ Telegram failed:", e)
        else:
            print("⚠️ Telegram credentials missing.")


if __name__ == "__main__":
    run()
