#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path


def bankroll_report(bankroll_file: str, last: int = 10):
    path = Path(bankroll_file).resolve()
    if not path.exists():
        print(f"No bankroll file found at {path}")
        return
    with open(path, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        print("Empty bankroll file")
        return
    header, data = rows[0], rows[1:]
    if not data:
        print("No entries yet")
        return
    last_rows = data[-last:]
    print("=== Current Balance ===")
    try:
        balance = float(last_rows[-1][6])
    except Exception:
        balance = "N/A"
    print(balance)
    print("=== Last Entries ===")
    print(",".join(header))
    for row in last_rows:
        print(",".join(row))


def main():
    ap = argparse.ArgumentParser(description="Bankroll report utility")
    ap.add_argument(
        "--file",
        default="../betting-bridge/data/bankroll.csv",
        help="Path to bankroll.csv",
    )
    ap.add_argument("--last", type=int, default=10, help="Show last N entries")
    args = ap.parse_args()
    bankroll_report(args.file, args.last)


if __name__ == "__main__":
    main()
