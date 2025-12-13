#!/usr/bin/env python3
"""
EQ12 Enhanced DraftKings Friday CFB Mystery Boost Optimizer
===========================================================
Enhanced with CSV export and Telegram integration

Features:
- Smart credential management (prompts once, saves forever)
- CSV export for historical tracking
- Telegram bot notifications for instant betting alerts
- Complete DraftKings promo rule compliance
- EV-optimized parlay selection

Author: EQ12 Development Team
Version: 2.1.0
Updated: 2025-10-03
"""

import argparse
import csv
import itertools
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import requests

# --------------------------- Defaults ---------------------------

SPORT = "americanfootball_ncaaf"
REGION = "us"
MARKETS = "h2h,spreads,totals"  # moneyline, spread, total
DK_BOOKMAKER_KEYS = ["DraftKings", "Draft Kings", "DraftKings Sportsbook"]

MIN_LEGS = 3
MIN_COMBINED_AMERICAN = 300
MIN_COMBINED_DECIMAL = 1 + (MIN_COMBINED_AMERICAN / 100)  # 4.0
MAX_STAKE_RULE = 100.0

# Safety filters
MAX_LEGS_DEFAULT = 5
AVOID_WHOLE_NUM_LINES = True  # avoid spread/total with integer to reduce push risk
MIN_PER_LEG_DECIMAL = 1.2  # ignore ultra-juicy legs (optional filter)

# --------------------------- Credential Management ---------------------------


def get_credentials_path():
    """Get path to EQ12 credentials file"""
    script_dir = Path(__file__).parent
    eq12_root = script_dir if script_dir.name == "EQ12" else script_dir.parent
    creds_dir = eq12_root / "eq12_shared"
    creds_dir.mkdir(exist_ok=True)
    return creds_dir / "credentials.json"


def load_credentials():
    """Load existing credentials from file"""
    creds_path = get_credentials_path()
    if creds_path.exists():
        try:
            with open(creds_path) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}
    return {}


def save_credentials(credentials):
    """Save credentials to file (deep merge with existing)"""
    creds_path = get_credentials_path()
    existing = load_credentials()

    # Deep merge
    for key, value in credentials.items():
        if key in existing and isinstance(existing[key], dict) and isinstance(value, dict):
            existing[key].update(value)
        else:
            existing[key] = value

    with open(creds_path, "w") as f:
        json.dump(existing, f, indent=2)
    print(f"✅ Credentials saved to {creds_path}")


def get_api_key():
    """Get OddsAPI key from env, credentials file, or prompt user"""
    # Try environment first
    api_key = os.getenv("ODDSAPI_KEY") or os.getenv("ODDS_API_KEY")
    if api_key:
        return api_key

    # Try credentials file
    creds = load_credentials()
    if "oddsapi" in creds and "api_key" in creds["oddsapi"]:
        return creds["oddsapi"]["api_key"]

    # Prompt user
    print("\n🔑 OddsAPI Key Required")
    print("   Get your key at: https://the-odds-api.com/")
    api_key = input("Enter your OddsAPI Key: ").strip()

    if not api_key:
        raise SystemExit("❌ OddsAPI key is required")

    # Save for future use
    save_credentials({"oddsapi": {"api_key": api_key}})
    return api_key


def get_telegram_credentials():
    """Get Telegram bot credentials from env, file, or prompt user"""
    # Try environment first
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if bot_token and chat_id:
        return bot_token, chat_id

    # Try credentials file
    creds = load_credentials()
    if "telegram" in creds and "bot_token" in creds["telegram"] and "chat_id" in creds["telegram"]:
        return creds["telegram"]["bot_token"], creds["telegram"]["chat_id"]

    # Prompt user
    print("\n📱 Telegram Credentials Required")
    print("   1. Message @BotFather on Telegram")
    print("   2. Use /newbot to create a bot")
    print("   3. Get your chat ID from: https://api.telegram.org/bot<TOKEN>/getUpdates")
    print()

    bot_token = input("Enter Telegram Bot Token: ").strip()
    chat_id = input("Enter Telegram Chat ID: ").strip()

    if not bot_token or not chat_id:
        raise SystemExit("❌ Both Telegram bot token and chat ID are required")

    # Save for future use
    save_credentials({"telegram": {"bot_token": bot_token, "chat_id": chat_id}})

    return bot_token, chat_id


def reset_credentials():
    """Reset saved credentials"""
    creds_path = get_credentials_path()
    if creds_path.exists():
        creds_path.unlink()
        print(f"✅ Credentials cleared from {creds_path}")
    else:
        print("ℹ️  No credentials file found")


# --------------------------- CSV Export ---------------------------


def export_to_csv(
    best_parlay: dict,
    alternatives: list,
    filename: str,
    promo_date: str = "N/A",
    token_percent: int = 0,
    stake: float = 0.0,
) -> str:
    """Export parlay results to CSV file"""
    if not filename.endswith(".csv"):
        filename += ".csv"

    filepath = Path(filename).resolve()

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "rank",
            "promo_date",
            "token_percent",
            "stake",
            "legs_count",
            "combined_american",
            "combined_decimal",
            "fair_win_prob_pct",
            "boosted_payout",
            "boosted_profit",
            "ev",
            "leg1_market",
            "leg1_selection",
            "leg1_odds",
            "leg1_game",
            "leg2_market",
            "leg2_selection",
            "leg2_odds",
            "leg2_game",
            "leg3_market",
            "leg3_selection",
            "leg3_odds",
            "leg3_game",
            "leg4_market",
            "leg4_selection",
            "leg4_odds",
            "leg4_game",
            "leg5_market",
            "leg5_selection",
            "leg5_odds",
            "leg5_game",
            "timestamp",
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Write best parlay (rank 1)
        row = {
            "rank": 1,
            "promo_date": promo_date,
            "token_percent": token_percent,
            "stake": stake,
            "legs_count": best_parlay["legs_count"],
            "combined_american": best_parlay["combined_american"],
            "combined_decimal": f"{best_parlay['combined_decimal']:.3f}",
            "fair_win_prob_pct": f"{best_parlay['p_win'] * 100:.2f}",
            "boosted_payout": f"{best_parlay['boosted_payout']:.2f}",
            "boosted_profit": f"{best_parlay['boosted_profit']:.2f}",
            "ev": f"{best_parlay['ev']:.2f}",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Add leg details (up to 5)
        legs = best_parlay["legs"]
        for i in range(5):
            if i < len(legs):
                leg = legs[i]
                row[f"leg{i + 1}_market"] = leg.market
                row[f"leg{i + 1}_selection"] = leg.selection_label
                row[f"leg{i + 1}_odds"] = leg.dk_american
                row[f"leg{i + 1}_game"] = leg.display_game
            else:
                row[f"leg{i + 1}_market"] = ""
                row[f"leg{i + 1}_selection"] = ""
                row[f"leg{i + 1}_odds"] = ""
                row[f"leg{i + 1}_game"] = ""

        writer.writerow(row)

        # Write alternatives
        for rank, alt in enumerate(alternatives[:10], 2):
            alt_row = {
                "rank": rank,
                "promo_date": promo_date,
                "token_percent": token_percent,
                "stake": stake,
                "legs_count": alt["legs_count"],
                "combined_american": alt["combined_american"],
                "combined_decimal": f"{alt['combined_decimal']:.3f}",
                "fair_win_prob_pct": f"{alt['p_win'] * 100:.2f}",
                "boosted_payout": f"{alt['boosted_payout']:.2f}",
                "boosted_profit": f"{alt['boosted_profit']:.2f}",
                "ev": f"{alt['ev']:.2f}",
                "timestamp": datetime.now(UTC).isoformat(),
            }

            # Add leg details for alternatives
            alt_legs = alt["legs"]
            for i in range(5):
                if i < len(alt_legs):
                    leg = alt_legs[i]
                    alt_row[f"leg{i + 1}_market"] = leg.market
                    alt_row[f"leg{i + 1}_selection"] = leg.selection_label
                    alt_row[f"leg{i + 1}_odds"] = leg.dk_american
                    alt_row[f"leg{i + 1}_game"] = leg.display_game
                else:
                    alt_row[f"leg{i + 1}_market"] = ""
                    alt_row[f"leg{i + 1}_selection"] = ""
                    alt_row[f"leg{i + 1}_odds"] = ""
                    alt_row[f"leg{i + 1}_game"] = ""

            writer.writerow(alt_row)

    return str(filepath)


# --------------------------- Telegram Integration ---------------------------


def send_telegram_message(message: str, bot_token: str, chat_id: str) -> bool:
    """Send message to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            return True
        print(f"❌ Telegram API error: {response.status_code} - {response.text}")
        return False

    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False


def format_telegram_message(
    best_parlay: dict, alternatives: list, promo_date: str, token: int, stake: float
) -> str:
    """Format parlay results as Telegram message"""
    message = f"""✅ *Best DK-Eligible Friday CFB Parlay*

📅 *Promo Date:* {promo_date}
🎯 *Token:* {token}% | 💰 *Stake:* ${stake:.2f}
🎲 *Legs:* {best_parlay["legs_count"]} | 📊 *Odds:* {best_parlay["combined_american"]:+d}
🧮 *Fair Win Prob:* {best_parlay["p_win"] * 100:.2f}% | 📈 *EV:* ${best_parlay["ev"]:.2f}
💸 *Boosted Payout:* ${best_parlay["boosted_payout"]:.2f}

*🎪 BETTING SLIP:*
"""

    for i, leg in enumerate(best_parlay["legs"], 1):
        message += f"{i}. `{leg.selection_label}` ({leg.dk_american:+d})\n"
        message += f"   📍 _{leg.display_game}_\n"

    if alternatives:
        message += "\n*— Top Alternatives (by EV) —*\n"
        for i, alt in enumerate(alternatives[:5], 2):
            message += f"{i}. {alt['legs_count']} legs | {alt['combined_american']:+d} | EV ${alt['ev']:.2f}\n"

    message += "\n⚠️ *IMPORTANT:*\n"
    message += f"• Apply {token}% Mystery Boost token BEFORE placing\n"
    message += "• Use Cash or DK Dollars only (no bonus funds)\n"
    message += f"• Verify all games are FBS and on {promo_date}\n"
    message += "• Max stake $100, minimum +300 odds\n"
    message += "• No other boosts, cash-outs, or progressive parlays\n"
    message += "\n🚀 _Generated by EQ12 CFB Optimizer_"

    return message


# --------------------------- Original CFB Optimizer Code ---------------------------


def american_to_decimal(american: int) -> float:
    return 1 + (100 / abs(american)) if american < 0 else 1 + (american / 100)


def decimal_to_american(decimal_odds: float) -> int:
    if decimal_odds >= 2.0:
        return round((decimal_odds - 1.0) * 100)
    return round(-100 / (decimal_odds - 1.0))


def american_to_implied_prob(american: int) -> float:
    return (abs(american) / (abs(american) + 100)) if american < 0 else (100 / (american + 100))


def devig_two_way_pair(a_price: int, b_price: int) -> tuple[float | None, float | None]:
    pa_raw = american_to_implied_prob(a_price)
    pb_raw = american_to_implied_prob(b_price)
    s = pa_raw + pb_raw
    if s <= 0:
        return None, None
    return pa_raw / s, pb_raw / s


def is_friday_game_on_promo_date(game: dict, promo_date: str) -> bool:
    ct = game.get("commence_time", "")
    return ct.startswith(promo_date)


def is_fbs_matchup(game: dict) -> bool:
    home = game.get("home_team", "") or ""
    away = game.get("away_team", "") or ""
    flags = ["FCS", "(FCS)"]
    return not any(flag in home or flag in away for flag in flags)


def is_half_point(x: float) -> bool:
    return abs(x - round(x)) >= 0.25 and abs((x * 2) - round(x * 2)) < 1e-9  # .5 multiples


@dataclass
class Leg:
    market: str  # 'h2h' | 'spreads' | 'totals'
    game_id: str
    home_team: str
    away_team: str
    selection_label: str  # e.g., 'Alabama ML' or 'Alabama -3.5' or 'Over 51.5'
    dk_american: int
    dk_decimal: float
    fair_prob: float
    display_game: str


def fetch_odds(api_key: str) -> dict:
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/"
    params = {
        "apiKey": api_key,
        "regions": REGION,
        "markets": MARKETS,
        "oddsFormat": "american",
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise SystemExit(f"[Unverified] OddsAPI error: {response.status_code}")

    return response.json()


def parse_dk_leg(game: dict, market_key: str, outcome: dict) -> tuple[str, int, float | None]:
    """Parse a single DK outcome into a leg candidate"""

    price = int(outcome.get("price"))
    name = outcome.get("name")

    if market_key == "h2h":
        # Moneyline
        if name == game["home_team"] or name == game["away_team"]:
            return f"{name} ML", price, None
        return None, price, None

    if market_key == "spreads":
        # Point spread
        point = outcome.get("point")
        if name == game["home_team"] or name == game["away_team"]:
            return f"{name} {point:+g}", price, point
        return None, price, None

    if market_key == "totals":
        # Over/Under
        point = outcome.get("point")
        if name == "Over":
            return f"Over {point}", price, point
        if name == "Under":
            return f"Under {point}", price, point
        return None, price, None

    return label, price, line


def average_fair_probs_from_pairs(pairs: list[tuple]) -> dict[str, float]:
    """Aggregate de-vigged probabilities from all books"""
    sums = {}
    counts = {}

    for label_a, price_a, label_b, price_b in pairs:
        pa_devig, pb_devig = devig_two_way_pair(price_a, price_b)

        if pa_devig is not None and pb_devig is not None:
            sums[label_a] = sums.get(label_a, 0) + pa_devig
            counts[label_a] = counts.get(label_a, 0) + 1

            sums[label_b] = sums.get(label_b, 0) + pb_devig
            counts[label_b] = counts.get(label_b, 0) + 1

    return {label: sums[label] / counts[label] for label in sums if counts[label] > 0}


def build_game_candidates(game: dict) -> list[Leg]:
    """Build leg candidates from a single game"""
    dk_outcomes = {}  # market -> {label -> price}
    all_pairs = []  # for de-vigging

    for bookmaker in game.get("bookmakers", []):
        title = bookmaker.get("title", "")
        is_dk = any(dk_key in title for dk_key in DK_BOOKMAKER_KEYS)

        for market in bookmaker.get("markets", []):
            market_key = market.get("key")
            if market_key not in ["h2h", "spreads", "totals"]:
                continue

            outcomes = market.get("outcomes", [])
            if len(outcomes) != 2:
                continue

            # Parse legs for this market
            legs_here = []
            for outcome in outcomes:
                label, price, line = parse_dk_leg(game, market_key, outcome)
                if label:
                    legs_here.append((label, price, line))

            if len(legs_here) == 2:
                # Store DK prices if this is DraftKings
                if is_dk:
                    if market_key not in dk_outcomes:
                        dk_outcomes[market_key] = {}
                    for label, price, line in legs_here:
                        dk_outcomes[market_key][label] = price

                # Add to de-vigging pairs (all books)
                (label_a, price_a, _), (label_b, price_b, _) = legs_here
                all_pairs.append((label_a, price_a, label_b, price_b))

    # Get fair probabilities from de-vigging
    fair_probs = average_fair_probs_from_pairs(all_pairs)

    # Build candidate Legs using DK prices and fair probs
    candidates = []
    display_game = f"{game.get('away_team', '')} @ {game.get('home_team', '')}"

    for market_key, dk_market in dk_outcomes.items():
        for label, dk_price in dk_market.items():
            if label in fair_probs:
                # Filter criteria
                dk_decimal = american_to_decimal(dk_price)

                if dk_decimal < MIN_PER_LEG_DECIMAL:
                    continue

                # For spreads/totals, optionally filter whole numbers
                if market_key in ["spreads", "totals"] and AVOID_WHOLE_NUM_LINES:
                    # Extract line value from label
                    if market_key == "spreads":
                        # e.g., "Alabama +3.5" -> check if 3.5 is half-point
                        parts = label.split()
                        if len(parts) >= 2:
                            try:
                                line_val = float(parts[-1].replace("+", ""))
                                if not is_half_point(line_val):
                                    continue
                            except ValueError:
                                continue
                    elif market_key == "totals":
                        # e.g., "Over 51.5" -> check if 51.5 is half-point
                        parts = label.split()
                        if len(parts) >= 2:
                            try:
                                line_val = float(parts[-1])
                                if not is_half_point(line_val):
                                    continue
                            except ValueError:
                                continue

                candidates.append(
                    Leg(
                        market=market_key,
                        game_id=game["id"],
                        home_team=game.get("home_team", ""),
                        away_team=game.get("away_team", ""),
                        selection_label=label,
                        dk_american=dk_price,
                        dk_decimal=dk_decimal,
                        fair_prob=fair_probs[label],
                        display_game=display_game,
                    )
                )

    return candidates


def combine_decimal(legs: list[Leg]) -> float:
    product = 1.0
    for leg in legs:
        product *= leg.dk_decimal
    return product


def product_prob(legs: list[Leg]) -> float:
    product = 1.0
    for leg in legs:
        product *= leg.fair_prob
    return product


class PromoValidator:
    def __init__(self, token_percent: int, promo_date: str, max_bet: float):
        self.token_percent = token_percent
        self.promo_date = promo_date
        self.max_bet = max_bet

    def boosted_payout_from_decimal(self, stake: float, decimal_odds: float) -> float:
        normal_payout = stake * decimal_odds
        boost_multiplier = 1 + (self.token_percent / 100)
        return normal_payout * boost_multiplier

    def validate(
        self, legs: list[Leg], combined_decimal: float, stake: float, use_cash: bool
    ) -> tuple[bool, str]:
        if len(legs) < MIN_LEGS:
            return False, f"Minimum {MIN_LEGS} legs required"

        if combined_decimal < MIN_COMBINED_DECIMAL:
            return False, f"Combined odds must be >= +{MIN_COMBINED_AMERICAN}"

        if stake > self.max_bet:
            return False, f"Stake must be <= ${self.max_bet}"

        if not use_cash:
            return False, "Must use cash/DK Dollars for Mystery Boost"

        # Check same game (no SGP)
        game_ids = {leg.game_id for leg in legs}
        if len(game_ids) != len(legs):
            return False, "Cannot combine legs from the same game"

        return True, "Valid"


def optimize_parlay(
    candidate_pools: list[list[Leg]],
    stake: float,
    validator: PromoValidator,
    max_legs: int,
    shortlist_k: int = 10,
):
    """Search for optimal parlay by EV"""
    best = None
    board = []

    for L in range(MIN_LEGS, min(max_legs, len(candidate_pools)) + 1):
        for game_indices in itertools.combinations(range(len(candidate_pools)), L):
            pools = [candidate_pools[i] for i in game_indices]

            for legs in itertools.product(*pools):
                legs = list(legs)
                dec = combine_decimal(legs)

                if dec < MIN_COMBINED_DECIMAL:
                    continue

                pwin = product_prob(legs)
                boosted_payout = validator.boosted_payout_from_decimal(stake, dec)
                boosted_profit = boosted_payout - stake
                ev = pwin * boosted_profit - (1 - pwin) * stake

                row = {
                    "legs": legs,
                    "legs_count": L,
                    "combined_decimal": dec,
                    "combined_american": decimal_to_american(dec),
                    "p_win": pwin,
                    "boosted_payout": boosted_payout,
                    "boosted_profit": boosted_profit,
                    "ev": ev,
                }
                if (best is None) or (ev > best["ev"]):
                    best = row
                board.append(row)

    board.sort(key=lambda x: x["ev"], reverse=True)
    return best, board[:shortlist_k]


def main():
    global MIN_PER_LEG_DECIMAL, AVOID_WHOLE_NUM_LINES

    parser = argparse.ArgumentParser(description="EQ12 Enhanced CFB DK Mystery Boost Optimizer")
    parser.add_argument("--promo-date", required=True, help="YYYY-MM-DD (Friday)")
    parser.add_argument(
        "--token",
        type=int,
        choices=[25, 33, 50],
        required=True,
        help="Profit boost percent",
    )
    parser.add_argument("--stake", type=float, default=MAX_STAKE_RULE, help="Stake (<= $100)")
    parser.add_argument(
        "--max-legs",
        type=int,
        default=MAX_LEGS_DEFAULT,
        help="Max legs to consider (>=3)",
    )
    parser.add_argument(
        "--min-per-leg-decimal",
        type=float,
        default=MIN_PER_LEG_DECIMAL,
        help="Filter ultra-juicy legs",
    )
    parser.add_argument(
        "--allow-whole-lines",
        action="store_true",
        help="Allow integer spreads/totals (push risk)",
    )
    parser.add_argument("--export-csv", action="store_true", help="Export results to CSV file")
    parser.add_argument("--csv-filename", type=str, help="Custom CSV filename")
    parser.add_argument("--telegram", action="store_true", help="Send results to Telegram bot")
    parser.add_argument("--reset-creds", action="store_true", help="Reset saved credentials")
    args = parser.parse_args()

    # Handle credential reset
    if args.reset_creds:
        reset_credentials()
        return

    # Get API key with credential management
    try:
        api_key = get_api_key()
    except SystemExit as e:
        print(e)
        return

    # Get Telegram credentials if needed
    if args.telegram:
        try:
            bot_token, chat_id = get_telegram_credentials()
        except SystemExit as e:
            print(e)
            return

    if args.stake > MAX_STAKE_RULE + 1e-9:
        raise SystemExit(f"Stake must be <= ${MAX_STAKE_RULE:.2f}")

    MIN_PER_LEG_DECIMAL = args.min_per_leg_decimal
    AVOID_WHOLE_NUM_LINES = not args.allow_whole_lines

    # Fetch markets
    data = fetch_odds(api_key)

    # Filter to Friday FBS games
    friday_games = [g for g in data if is_friday_game_on_promo_date(g, args.promo_date)]
    friday_fbs_games = [g for g in friday_games if is_fbs_matchup(g)]

    if len(friday_fbs_games) < MIN_LEGS:
        raise SystemExit("[Unverified] Not enough FBS Friday games found to build a 3+ leg parlay.")

    print(f"Found {len(friday_fbs_games)} FBS Friday games on {args.promo_date}")

    # Build candidate legs
    pools = []
    for game in friday_fbs_games:
        legs = build_game_candidates(game)
        if legs:
            pools.append(legs)

    if len(pools) < MIN_LEGS:
        raise SystemExit(
            "[Unverified] Insufficient DK-priced candidate legs across distinct games."
        )

    promo = PromoValidator(
        token_percent=args.token, promo_date=args.promo_date, max_bet=MAX_STAKE_RULE
    )

    best, top = optimize_parlay(
        pools, stake=args.stake, validator=promo, max_legs=max(args.max_legs, MIN_LEGS)
    )

    if not best:
        raise SystemExit("No valid combo reached +300 minimum after filtering.")

    ok, msg = promo.validate(best["legs"], best["combined_decimal"], args.stake, use_cash=True)
    if not ok:
        raise SystemExit("❌ " + msg)

    # -------- Output --------
    print("\n✅ Best DK‑Eligible Friday CFB Parlay (EV‑optimized, boost applied in EV math)")
    print(f"Promo Date: {args.promo_date} | Token: {args.token}% | Stake: ${args.stake:.2f}")
    print(
        f"Legs: {best['legs_count']} | Combined Odds: {best['combined_american']:+d} (decimal {best['combined_decimal']:.3f})"
    )
    print(f"Fair Win Prob: {best['p_win'] * 100:.2f}%")
    print(
        f"Boosted Payout: ${best['boosted_payout']:.2f} | Boosted Profit: ${best['boosted_profit']:.2f}"
    )
    print(f"EV (Boosted): ${best['ev']:.2f}")
    print(
        "\nPlace on DraftKings (cash/DK Dollars only). Do NOT stack other boosts/cash-out. Avoid progressive parlays."
    )
    for i, leg in enumerate(best["legs"], 1):
        print(
            f"  {i}. {leg.selection_label:>20}  ({leg.dk_american:+d})  | Game: {leg.display_game}"
        )

    print("\n— Top Alternatives (by EV) —")
    for i, c in enumerate(top, 1):
        print(
            f"{i}. {c['legs_count']} legs | {c['combined_american']:+d} (dec {c['combined_decimal']:.2f}) | "
            f"P(win) {c['p_win'] * 100:.2f}% | EV ${c['ev']:.2f}"
        )

    # -------- Export to CSV --------
    if args.export_csv:
        try:
            csv_filename = args.csv_filename or f"parlays_{args.promo_date}.csv"

            csv_path = export_to_csv(
                best, top, csv_filename, args.promo_date, args.token, args.stake
            )
            print(f"\n📊 CSV Export: {csv_path}")
        except Exception as e:
            print(f"\n❌ CSV Export failed: {e}")

    # -------- Send to Telegram --------
    if args.telegram:
        try:
            telegram_message = format_telegram_message(
                best, top, args.promo_date, args.token, args.stake
            )
            success = send_telegram_message(telegram_message, bot_token, chat_id)
            if success:
                print("\n📱 Telegram notification sent successfully!")
            else:
                print("\n❌ Failed to send Telegram notification")
        except Exception as e:
            print(f"\n❌ Telegram export failed: {e}")


if __name__ == "__main__":
    main()
