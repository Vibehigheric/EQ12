"""CLI runner for OmniScraper"""

import argparse
import logging
import sys
from pathlib import Path

from omni_scraper.omni_scraper import OmniScraper, ScraperConfig

ROOT = Path(__file__).resolve().parents[1]
shared_path = ROOT / "openai-python-project"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

from eq12_shared import CredentialError, CredentialManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("omni_run")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--api-key", help="API key for the odds API")
    p.add_argument("--db", help="Path to sqlite DB to persist results")
    p.add_argument("--out", help="Path to write JSON output", default="all_in_season_games.json")
    p.add_argument("--dry-run", action="store_true", default=False)
    args = p.parse_args()

    manager = CredentialManager()
    try:
        api_key = args.api_key or manager.ensure_env(
            "odds_api.api_key",
            "ODDS_API_KEY",
            prompt="Enter The Odds API key: ",
            mask_input=True,
        )
    except CredentialError as err:
        raise SystemExit(f"Credential error: {err}")

    cfg = ScraperConfig(api_key=api_key, db_path=args.db, dry_run=args.dry_run)
    scraper = OmniScraper(cfg)
    scraper.output_path = args.out

    # simple event handler
    scraper.on(
        "games_fetched",
        lambda sport, games: logger.info("Fetched %d games for %s", len(games), sport),
    )
    scraper.run()


if __name__ == "__main__":
    main()
