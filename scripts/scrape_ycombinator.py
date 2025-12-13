import requests
from bs4 import BeautifulSoup
import html2text
import os
import time
import re

BASE_URL = "https://paulgraham.com/"
ARTICLES_URL = "https://paulgraham.com/articles.html"
OUTPUT_DIR = r"c:\EQ12_BROKEN_20251122_210342\knowledge\ycombinator\essays"

def get_article_links():
    print(f"Fetching articles from {ARTICLES_URL}...")
    try:
        response = requests.get(ARTICLES_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        links = []
        # PG's site is old school tables.
        # Look for links in the main table.
        for a in soup.find_all('a'):
            href = a.get('href')
            if href and href.endswith('.html') and 'index.html' not in href and 'rss.html' not in href:
                full_url = BASE_URL + href if not href.startswith('http') else href
                title = a.text.strip()
                if title and len(title) > 2: # Filter out tiny links
                    links.append({'title': title, 'url': full_url})
        
        # Remove duplicates
        unique_links = []
        seen = set()
        for l in links:
            if l['url'] not in seen:
                unique_links.append(l)
                seen.add(l['url'])
                
        return unique_links
    except Exception as e:
        print(f"Error fetching article list: {e}")
        return []

def save_article(article):
    title = article['title']
    url = article['url']
    
    # Clean title for filename
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
    filename = os.path.join(OUTPUT_DIR, f"{safe_title}.md")
    
    if os.path.exists(filename):
        print(f"Skipping {title} (already exists)")
        return

    print(f"Downloading: {title}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Convert to Markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.body_width = 0 # No wrapping
        
        markdown_content = h.handle(response.text)
        
        # Add metadata
        full_content = f"# {title}\n\nSource: {url}\n\n---\n\n{markdown_content}"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_content)
            
        time.sleep(0.5) # Be nice to the server
        
    except Exception as e:
        print(f"Failed to download {title}: {e}")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    articles = get_article_links()
    print(f"Found {len(articles)} articles.")
    
    # Download top 50 to avoid overwhelming
    for i, article in enumerate(articles[:50]):
        save_article(article)
        
    print("Done!")

if __name__ == "__main__":
    main()
