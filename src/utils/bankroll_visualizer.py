#!/usr/bin/env python3
import argparse
import csv
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt


def plot_bankroll(bankroll_file: str, save: bool = False):
    path = Path(bankroll_file).resolve()
    if not path.exists():
        print(f"No bankroll file found at {path}")
        return
    timestamps, balances = [], []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bal = row.get("balance")
            if not bal:
                continue
            try:
                timestamps.append(datetime.fromisoformat(row["timestamp"]))
                balances.append(float(bal))
            except Exception:
                continue
    if not balances:
        print("No valid balance entries to plot.")
        return
    plt.figure(figsize=(10, 5))
    plt.plot(
        timestamps,
        balances,
        marker="o",
        linestyle="-",
        color="blue",
        label="Bankroll Balance",
    )
    plt.xlabel("Time")
    plt.ylabel("Balance ($)")
    plt.title("Bankroll Over Time")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    if save:
        out_file = path.parent / "bankroll_curve.png"
        plt.savefig(out_file)
        print(f"📈 Saved bankroll plot → {out_file}")
    else:
        plt.show()


def main():
    ap = argparse.ArgumentParser(description="Visualize bankroll CSV as line chart")
    ap.add_argument(
        "--file",
        default="../betting-bridge/data/bankroll.csv",
        help="Path to bankroll.csv",
    )
    ap.add_argument("--save", action="store_true", help="Save plot as PNG instead of displaying")
    args = ap.parse_args()
    plot_bankroll(args.file, save=args.save)


if __name__ == "__main__":
    main()
