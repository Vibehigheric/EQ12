import csv
import os
import re
from pathlib import Path

# Try pandas if available (best experience), else fallback to basic CSV passthrough
try:
    import pandas as pd  # requires: pandas, openpyxl, xlrd
except Exception:
    pd = None

SCHEMA_HEADERS = [
    "game_id",
    "market",
    "side",
    "player",
    "display_name",
    "odds",
    "true_prob",
    "proj_over_2_prob",
]

SHEET_MARKET_HINTS = {
    "mlb-ml": "ML",
    "mlb_ml": "ML",
    "mlb ml": "ML",
    "mlb-spread": "Spread",
    "mlb_spread": "Spread",
    "mlb spread": "Spread",
    "mlb-o/u": "OU",
    "mlb_ou": "OU",
    "mlb ou": "OU",
    "tb": "TB",
    "hits": "Hits",
    "hr": "HR",
}


def guess_market_from_sheet(sheet_name: str) -> str:
    key = re.sub(r"[^a-z0-9/]+", " ", sheet_name.strip().lower())
    key = key.replace("o / u", "o/u").replace("o/u", "o/u").replace(" / ", "/")
    for hint, market in SHEET_MARKET_HINTS.items():
        if hint in key:
            return market
    # fallback: look for substrings
    if "spread" in key:
        return "Spread"
    if "ou" in key or "o/u" in key or "total" in key:
        return "OU"
    if "ml" in key:
        return "ML"
    return ""


def coerce_float(x) -> bool:
    try:
        if x is None or x == "":
            return None
        return float(str(x).replace("%", "").strip())
    except Exception:
        return None


def coerce_int(x) -> bool:
    try:
        if x is None or x == "":
            return None
        return int(str(x).strip())
    except Exception:
        # try float to int
        try:
            return int(float(x))
        except Exception:
            return None


def compose_display_name(row) -> bool:
    # Prefer explicit display_name; else build from player/market/side/value
    dn = (row.get("display_name") or "").strip()
    if dn:
        return dn
    player = (row.get("player") or "").strip()
    market = (row.get("market") or "").strip()
    side = (row.get("side") or "").strip()
    val = (row.get("value") or row.get("line") or "").strip()
    parts = []
    if player:
        parts.append(player)
    if market:
        parts.append(market)
    if side:
        parts.append(side)
    if val:
        parts.append(val)
    built = " ".join([p for p in parts if p])
    return built if built else None


def normalize_dataframe(df, inferred_market="") -> bool:
    # Flexible column mapping
    cols = {c.strip().lower(): c for c in df.columns if isinstance(c, str)}

    def pick(*names) -> bool:
        for n in names:
            key = n.lower()
            if key in cols:
                return cols[key]
        # fuzzy picks
        for c in cols:
            for n in names:
                if n.lower() in c:
                    return cols[c]
        return None

    out_rows = []
    for _, r in df.iterrows():
        entry = {}
        entry["game_id"] = str(
            r.get(pick("game_id", "game", "matchup", "fixture", "event_id")) or ""
        ).strip()
        entry["market"] = (
            str(r.get(pick("market", "bet_type", "type"))) or ""
        ).strip() or inferred_market
        entry["side"] = (
            str(r.get(pick("side", "selection", "pick", "team", "over_under"))) or ""
        ).strip()
        entry["player"] = (str(r.get(pick("player", "name", "athlete", "batter"))) or "").strip()
        entry["display_name"] = (
            compose_display_name(
                {
                    "display_name": r.get(pick("display_name", "desc", "description")),
                    "player": entry["player"],
                    "market": entry["market"],
                    "side": entry["side"],
                    "value": r.get(pick("value", "line", "points")),
                }
            )
            or ""
        )
        entry["odds"] = coerce_int(r.get(pick("odds", "price", "american_odds", "american")))
        # true_prob might be provided or derived; we take provided numeric 0..1 or %
        tp = r.get(pick("true_prob", "truep", "prob", "win_prob", "implied_prob"))
        tp = coerce_float(tp)
        if tp is not None and tp > 1.0:
            tp = tp / 100.0
        entry["true_prob"] = tp
        p2 = r.get(pick("proj_over_2_prob", "p2plus", "two_plus_prob", "over_2_prob"))
        p2 = coerce_float(p2)
        if p2 is not None and p2 > 1.0:
            p2 = p2 / 100.0
        entry["proj_over_2_prob"] = p2

        # Clean market names to match runner expectations
        if entry["market"]:
            m = entry["market"].strip().upper()
            mapping = {
                "MONEYLINE": "ML",
                "MONEY LINE": "ML",
                "RUN LINE": "SPREAD",
                "RL": "SPREAD",
                "TOTAL": "OU",
                "O/U": "OU",
                "OVER/UNDER": "OU",
            }
            entry["market"] = mapping.get(m, entry["market"])

        # Only include rows with at least odds and true_prob or market+side
        if not entry["display_name"]:
            entry["display_name"] = f"{entry['market']} {entry['side']}".strip()

        out_rows.append(entry)

    return out_rows


def write_csv(path, rows) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA_HEADERS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in SCHEMA_HEADERS})


def normalize_input_folder(input_dir, output_csv) -> bool:
    input_dir = Path(input_dir)
    files = (
        list(input_dir.glob("*.xlsx"))
        + list(input_dir.glob("*.xls"))
        + list(input_dir.glob("*.csv"))
    )
    all_rows = []

    if not files:
        return False, "No input files found."

    if pd is None:
        # Fallback: if CSV exists, pass through best-effort (must match schema)
        for csv_path in [p for p in files if p.suffix.lower() == ".csv"]:
            try:
                with open(csv_path, newline="", encoding="utf-8") as f:
                    r = csv.DictReader(f)
                    for row in r:
                        all_rows.append({k: row.get(k, "") for k in SCHEMA_HEADERS})
            except Exception:
                continue
        if all_rows:
            write_csv(Path(output_csv), all_rows)
            return (
                True,
                f"Wrote {len(all_rows)} rows (CSV passthrough). Install pandas+openpyxl for Excel parsing.",
            )
        return False, "Pandas not available and no CSV schema-matching files found."
    for fp in files:
        try:
            if fp.suffix.lower() == ".csv":
                df = pd.read_csv(fp)
                inferred = ""
                rows = normalize_dataframe(df, inferred_market=inferred)
                all_rows.extend(rows)
            else:
                # Excel: iterate all sheets
                xl = pd.ExcelFile(fp)
                for sheet in xl.sheet_names:
                    df = xl.parse(sheet)
                    inferred = guess_market_from_sheet(sheet)
                    rows = normalize_dataframe(df, inferred_market=inferred)
                    all_rows.extend(rows)
        except Exception:
            continue
    if not all_rows:
        return False, "No usable rows parsed. Check input format."
    write_csv(Path(output_csv), all_rows)
    return True, f"Wrote {len(all_rows)} rows from {len(files)} file(s)."


if __name__ == "__main__":
    ok, msg = normalize_input_folder(
        os.path.join("data", "input"), os.path.join("data", "sample_lines.csv")
    )
    print("[normalizer]", "OK" if ok else "FAIL", "-", msg)
