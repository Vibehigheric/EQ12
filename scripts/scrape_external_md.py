import requests
from bs4 import BeautifulSoup
import html2text
import os
import time
import re
import argparse

# Configuration
OUTPUT_DIR = r"c:\EQ12_BROKEN_20251122_210342\knowledge\external_sources"

def clean_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)[:100]

def scrape_github_markdown(url):
    """
    Scrapes a raw markdown file or a rendered markdown page from GitHub.
    """
    print(f"Scraping GitHub: {url}")
    try:
        # If it's a blob URL, try to get the raw version
        if "github.com" in url and "/blob/" in url:
            raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            print(f"  -> Fetching raw: {raw_url}")
            response = requests.get(raw_url)
            response.raise_for_status()
            content = response.text
            # Use repo name + filename to avoid collisions
            # Standard GitHub URL: https://github.com/owner/repo/blob/branch/filename
            parts = url.split("/")
            if "github.com" in url and len(parts) >= 5:
                # owner is parts[3], repo is parts[4]
                repo_name = parts[4]
                filename = parts[-1]
                title = f"{repo_name}_{filename}"
            else:
                title = url.split("/")[-1]
        else:
            # Standard webpage scrape
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try to find the main markdown body (GitHub specific)
            article = soup.find("article", class_="markdown-body")
            if article:
                h = html2text.HTML2Text()
                h.ignore_links = False
                content = h.handle(str(article))
            else:
                # Fallback to generic body
                h = html2text.HTML2Text()
                content = h.handle(response.text)
            
            title = soup.title.string if soup.title else "scraped_doc"

        # Save
        filename = os.path.join(OUTPUT_DIR, f"{clean_filename(title)}.md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\nSource: {url}\n\n---\n\n{content}")
        print(f"  -> Saved to {filename}")
        return filename

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Scrape markdown knowledge from URLs")
    parser.add_argument("urls", nargs="+", help="List of URLs to scrape")
    args = parser.parse_args()

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for url in args.urls:
        scrape_github_markdown(url)

if __name__ == "__main__":
    main()
