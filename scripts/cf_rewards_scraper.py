"""CouponFollow Rewards scraper scaffold for EQ12.

This is a lightweight, watchlist-driven scraper that finds coupon deals per store.
Replace `scrape_store` with a Playwright-based stealth implementation for production.
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("cf_rewards")
logging.basicConfig(level=logging.INFO)


def load_watchlist(path: str) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        logger.warning("Coupon watchlist not found: %s", path)
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def scrape_store(store: str, min_discount: float = 0.0) -> list[dict[str, Any]]:
    """Placeholder scraping logic. Return simulated coupon entries."""
    time.sleep(0.2)
    return [
        {
            "store": store,
            "coupon": "SAVE10",
            "discount_pct": 12,
            "url": f"https://rewards.couponfollow.com/store/{store.lower()}",
            "expiry": "2025-12-31",
        }
    ]


def process_watchlist(watchlist: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for entry in watchlist:
        store = entry.get("store")
        min_disc = entry.get("min_discount", 0)
        try:
            items = scrape_store(store, min_disc)
            filtered = [i for i in items if i.get("discount_pct", 0) >= min_disc]
            results.extend(filtered)
        except Exception as e:
            logger.exception("Error scraping %s: %s", store, e)
    return results


def save_results(results: list[dict[str, Any]], out: str, dry_run: bool = True):
    p = Path(out)
    p.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        logger.info("Dry-run: would write %d coupon entries to %s", len(results), out)
    else:
        p.write_text(json.dumps(results, indent=2), encoding="utf-8")
        logger.info("Wrote %d coupon entries to %s", len(results), out)


def build_parser():
    p = argparse.ArgumentParser()
    p.add_argument("--watchlist", default="configs/coupon_watchlist.json")
    p.add_argument("--out", default="C:/EQ12/logs/couponfollow_rewards.json")
    p.add_argument("--dry-run", action="store_true", dest="dry_run", default=True)
    p.add_argument("--no-dry-run", action="store_false", dest="dry_run")
    return p


def main(argv=None) -> None:
    p = build_parser()
    args = p.parse_args(argv)
    wl = load_watchlist(args.watchlist)
    results = process_watchlist(wl)
    save_results(results, args.out, args.dry_run)


if __name__ == "__main__":
    main()
