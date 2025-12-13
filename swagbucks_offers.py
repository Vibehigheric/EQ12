#!/usr/bin/env python
import argparse
import sys

from playwright.sync_api import sync_playwright

from alert_pipe import send_offers
from db import init_db, upsert_offers

CATEGORIES = [
    ("https://www.swagbucks.com/g/shop", "shopping"),
    ("https://www.swagbucks.com/g/best-offers", "best"),
]


def scrape_offers(url: str, category: str, limit: int = 20) -> list[dict]:
    offers: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        # Allow for dynamic load
        page.wait_for_timeout(4000)
        # The CSS classes can change; we attempt a few selectors
        selectors = [".offer-card", ".MerchantCard", "[data-testid='offer-card']"]
        cards = []
        for sel in selectors:
            cards = page.query_selector_all(sel)
            if cards:
                break
        for c in cards[:limit]:
            title = ""
            reward = ""
            link = ""
            try:
                title_el = (
                    c.query_selector(".offer-title")
                    or c.query_selector(".merchant-name")
                    or c.query_selector("h3, h4")
                )
                if title_el:
                    title = title_el.inner_text().strip()
                reward_el = c.query_selector(".offer-reward, .cashback, .points, .reward")
                if reward_el:
                    reward = reward_el.inner_text().strip()
                link_el = c.query_selector("a")
                if link_el:
                    link = link_el.get_attribute("href") or ""
            except Exception:
                pass
            if title and link:
                offers.append(
                    {
                        "source": "swagbucks",
                        "title": title,
                        "url": link,
                        "reward": reward,
                        "category": category,
                    }
                )
        browser.close()
    return offers


def main():
    p = argparse.ArgumentParser(description="EQ12 Swagbucks Offers Scraper")
    p.add_argument("--category-url", help="Override a single category URL to scrape")
    p.add_argument("--category-name", help="Category name for the custom URL")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--telegram", action="store_true")
    args = p.parse_args()

    init_db()
    rows: list[dict] = []

    if args.category_url:
        rows += scrape_offers(args.category_url, args.category_name or "custom", limit=args.limit)
    else:
        for url, cat in CATEGORIES:
            try:
                rows += scrape_offers(url, cat, limit=args.limit)
            except Exception as e:
                print(f"[warn] {url} failed: {e}", file=sys.stderr)

    saved = upsert_offers(rows)
    print(f"[ok] scraped {len(rows)} offers; saved up to {saved}")
    if args.telegram and rows:
        err = send_offers(rows[:20], header="Swagbucks Offers")
        if err:
            print(f"[note] Telegram not sent: {err}")


if __name__ == "__main__":
    main()
