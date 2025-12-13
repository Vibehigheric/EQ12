#!/usr/bin/env python3
"""
EQ12 GODSTACK - Trending Repo Monitor
Scrapes GitHub Trending daily and feeds into enrichment pipeline for integration suggestions.

Author: EQ12-GODSTACK
Created: 2025-09-27
"""

import argparse
import json
import logging
import random
import sqlite3
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Add the project directory to the path
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from telegram_utils import send_telegram_message

# Constants
TRENDING_URL = "https://github.com/trending"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# Database setup
DB_PATH = PROJECT_DIR / "meta_search.sqlite3"


def setup_logging():
    """Setup logging for the trending monitor."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("C:/EQ12/logs/trending_monitor.log"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


def init_trending_db():
    """Initialize the trending_repos table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trending_repos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                description TEXT,
                language TEXT,
                stars_today INTEGER DEFAULT 0,
                stars_total INTEGER DEFAULT 0,
                scraped_date TEXT NOT NULL,
                enrichment_status TEXT DEFAULT 'pending'
            )
        """
        )
        conn.commit()


def respectful_delay():
    """Implement respectful delay between requests for GitHub ToS compliance."""
    delay = random.uniform(2.0, 5.0)  # 2-5 second random delay
    time.sleep(delay)
    logging.info(f"Respectful delay: {delay:.1f} seconds")


def scrape_github_trending(language: str | None = None) -> list[dict]:
    """
    Scrape GitHub Trending page for hot repositories.
    Complies with GitHub Terms of Service - public data only.

    Args:
        language: Optional language filter (e.g., 'python', 'javascript')

    Returns:
        List of trending repo dictionaries
    """
    logger = logging.getLogger(__name__)

    url = TRENDING_URL
    if language:
        url += f"/{language}"

    logger.info(f"Scraping GitHub Trending (ToS compliant): {url}")

    # Implement respectful delay for GitHub ToS compliance
    respectful_delay()

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        repos = []

        # Find all trending repo articles
        repo_articles = soup.find_all("article", class_="Box-row")

        for article in repo_articles:
            try:
                # Extract repo name and URL
                h2_tag = article.find("h2", class_="h3")
                if not h2_tag:
                    continue

                link = h2_tag.find("a")
                if not link:
                    continue

                repo_name = link.get_text().strip().replace("\n", "").replace(" ", "")
                repo_url = f"https://github.com{link.get('href')}"

                # Extract description
                desc_p = article.find("p", class_="col-9")
                description = desc_p.get_text().strip() if desc_p else "No description available"

                # Extract language
                lang_span = article.find("span", {"itemprop": "programmingLanguage"})
                language_detected = lang_span.get_text().strip() if lang_span else "Unknown"

                # Extract stars (today and total)
                stars_today = 0
                stars_total = 0

                # Look for star counts
                star_links = article.find_all("a", href=lambda x: x and "/stargazers" in x)
                for star_link in star_links:
                    star_text = star_link.get_text().strip()
                    if star_text.replace(",", "").isdigit():
                        stars_total = int(star_text.replace(",", ""))
                        break

                # Look for "X stars today" pattern
                spans = article.find_all("span", class_="d-inline-block")
                for span in spans:
                    text = span.get_text().strip()
                    if "stars today" in text or "star today" in text:
                        try:
                            stars_today = int(text.split()[0].replace(",", ""))
                        except (ValueError, IndexError):
                            stars_today = 0
                        break

                repo_data = {
                    "name": repo_name,
                    "url": repo_url,
                    "description": description,
                    "language": language_detected,
                    "stars_today": stars_today,
                    "stars_total": stars_total,
                    "scraped_date": datetime.now(UTC).isoformat(),
                }

                repos.append(repo_data)
                logger.info(f"Found trending repo: {repo_name} ({stars_today} stars today)")

            except Exception as e:
                logger.warning(f"Error parsing repo article: {e}")
                continue

        logger.info(f"Successfully scraped {len(repos)} trending repositories")
        return repos

    except Exception as e:
        logger.error(f"Error scraping GitHub Trending: {e}")
        return []


def save_trending_repos(repos: list[dict]) -> int:
    """
    Save trending repos to database.

    Args:
        repos: List of repo dictionaries

    Returns:
        Number of new repos saved
    """
    logger = logging.getLogger(__name__)
    new_repos = 0

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        for repo in repos:
            try:
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO trending_repos
                    (name, url, description, language, stars_today, stars_total, scraped_date, enrichment_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        repo["name"],
                        repo["url"],
                        repo["description"],
                        repo["language"],
                        repo["stars_today"],
                        repo["stars_total"],
                        repo["scraped_date"],
                        "pending",
                    ),
                )

                if cursor.rowcount > 0:
                    new_repos += 1

            except Exception as e:
                logger.warning(f"Error saving repo {repo['name']}: {e}")

        conn.commit()

    logger.info(f"Saved {new_repos} new trending repositories")
    return new_repos


def generate_telegram_summary(repos: list[dict]) -> str:
    """Generate Telegram message summary of trending repos."""
    if not repos:
        return "🔍 **GitHub Trending Monitor** - No new repos found today"

    message = f"🔥 **GitHub Trending - {len(repos)} Hot Repos**\n\n"

    # Sort by stars today for better ranking
    sorted_repos = sorted(repos, key=lambda x: x["stars_today"], reverse=True)

    for i, repo in enumerate(sorted_repos[:10], 1):  # Top 10 only
        stars_today = repo["stars_today"]
        stars_total = f"{repo['stars_total']:,}" if repo["stars_total"] else "N/A"
        language = repo["language"] if repo["language"] != "Unknown" else ""

        message += f"**{i}. {repo['name']}** {language}\n"
        message += f"⭐ {stars_today} stars today ({stars_total} total)\n"
        message += (
            f"📝 {repo['description'][:100]}{'...' if len(repo['description']) > 100 else ''}\n"
        )
        message += f"🔗 {repo['url']}\n\n"

    message += "🤖 **Enrichment Analysis Coming Next...**\n"
    message += "GPT will analyze integration potential for EQ12 stacks"

    return message


def run_trending_monitor(language: str | None = None, telegram: bool = False) -> dict:
    """
    Main function to run the trending repo monitor.

    Args:
        language: Optional language filter
        telegram: Whether to send Telegram notifications

    Returns:
        Results dictionary with stats
    """
    logger = setup_logging()
    logger.info("Starting GitHub Trending Monitor")

    # Initialize database
    init_trending_db()

    # Scrape trending repos
    repos = scrape_github_trending(language)

    if not repos:
        logger.warning("No trending repos found")
        if telegram:
            send_telegram_message(
                "⚠️ **GitHub Trending Monitor** - No repos found (possible scraping issue)"
            )
        return {"repos_found": 0, "new_repos": 0}

    # Save to database
    new_repos = save_trending_repos(repos)

    # Send Telegram summary
    if telegram:
        summary = generate_telegram_summary(repos)
        send_telegram_message(summary)

    # Save snapshot
    snapshot = {
        "timestamp": datetime.now(UTC).isoformat(),
        "repos_found": len(repos),
        "new_repos": new_repos,
        "trending_repos": repos,
    }

    snapshot_path = (
        Path("C:/EQ12/logs") / f"trending_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    logger.info(f"Trending monitor completed - {len(repos)} repos found, {new_repos} new")

    return {
        "repos_found": len(repos),
        "new_repos": new_repos,
        "snapshot_path": str(snapshot_path),
    }


def main():
    """
    Main CLI entry point.
    GitHub ToS compliant trending repo monitor.
    """
    parser = argparse.ArgumentParser(description="EQ12 GitHub Trending Repo Monitor")
    parser.add_argument(
        "--language", help="Filter by programming language (e.g., python, javascript)"
    )
    parser.add_argument("--telegram", action="store_true", help="Send results to Telegram")
    parser.add_argument("--quiet", action="store_true", help="Suppress console output")

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    try:
        results = run_trending_monitor(language=args.language, telegram=args.telegram)

        if not args.quiet:
            print(
                f"✅ Trending Monitor Complete: {results['repos_found']} repos found, {results['new_repos']} new"
            )

    except Exception as e:
        logging.error(f"Trending monitor failed: {e}")
        if args.telegram:
            send_telegram_message(f"❌ **Trending Monitor Error**: {e!s}")
        sys.exit(1)


if __name__ == "__main__":
    main()
