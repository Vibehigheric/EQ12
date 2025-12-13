#!/usr/bin/env python3
from ..core.bankroll_tracker import update_bankroll
from ..core.slip_export import export_slip


def run_optimizer(best, args):
    best_slip = {
        "id": f"{args.promo_date}-{args.sport}-{args.promo}",
        "sport": args.sport,
        "ev": float(best["ev"]),
        "stake": args.stake,
        "legs": [
            {"label": leg.label, "american": leg.american, "game": leg.game} for leg in best["legs"]
        ],
    }
    latest, csvfile = export_slip(best_slip, bridge_dir="../betting-bridge/data/parlays")
    print("📤 Slip exported:")
    print("  JSON:", latest)
    print("  CSV :", csvfile)
    bankroll_file = update_bankroll(best_slip)
    print("💰 Bankroll updated:", bankroll_file)
