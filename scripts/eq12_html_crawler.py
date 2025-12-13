#!/usr/bin/env python3
"""
EQ12 Expert HTML Crawler - Professional Web Content Extraction System
Professional Engineering Grade HTML Knowledge Acquisition

Author: EQ12 Engineering Team
Version: 2.1.0
Date: 2025-11-22
Python: 3.12+

This script provides professional-grade HTML content crawling and knowledge extraction:
- Respects robots.txt and rate limiting
- Intelligent content extraction and text processing
- Knowledge indexing with keyword frequency analysis
- Safe file handling with ASCII-compatible storage
- Comprehensive error handling and recovery
- EQ12 system integration with logging and reporting

Usage Examples:
  python eq12_html_crawler.py --url https://html.com --max-pages 100
  python eq12_html_crawler.py --url https://html.com --deep-crawl --extract-knowledge
  python eq12_html_crawler.py --batch-urls urls.txt --parallel 5

Teaching Notes (30-Day Python Curriculum Integration):
- Web scraping (Day 24): Professional crawling with respect for robots.txt
- Data processing (Day 23): Text extraction and knowledge indexing
- File I/O operations (Day 12): Safe storage with ASCII compatibility
- Error handling (Day 19): Comprehensive exception management
- Performance optimization (Day 27): Parallel processing and rate limiting
"""

import os
import re
import sys
import time
import json
import queue
import hashlib
import logging
import argparse
import threading
from datetime import datetime, timedelta
from typing import Dict, Set, List, Tuple, Optional, Union
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser
from pathlib import Path
import concurrent.futures

import requests
from bs4 import BeautifulSoup, Comment

class EQ12HTMLCrawler:
    """
    Professional HTML crawler with EQ12 system integration

    Teaching note (Day 20 - Classes): Enterprise-grade crawler class
    with comprehensive configuration and monitoring capabilities.
    """

    def __init__(self, base_url: str, config: Optional[Dict] = None):
        """Initialize the EQ12 HTML Crawler"""
        self.base_url = self.normalize_url(base_url)
        self.base_domain = urlparse(self.base_url).netloc

        # Default configuration
        self.config = {
            'user_agent': 'EQ12-HTMLCrawler/2.1 (+https://eq12.com/contact)',
            'request_timeout': 15,
            'request_delay': 1.5,  # Respectful crawling
            'max_pages': 1000,
            'max_depth': 10,
            'max_workers': 3,  # Conservative parallel crawling
            'data_dir': Path('C:/EQ12/data/html_crawler'),
            'logs_dir': Path('C:/EQ12/logs'),
            'respect_robots': True,
            'extract_knowledge': True,
            'save_html': True,
            'save_text': True,
            'create_index': True
        }

        # Update with user config
        if config:
            self.config.update(config)

        # Initialize directories
        self.setup_directories()

        # Setup logging
        self.setup_logging()

        # Initialize session
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.config['user_agent']})

        # Load robots.txt
        self.robots_parser = self.load_robots_parser() if self.config['respect_robots'] else None

        # Crawling state
        self.visited_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.url_queue: queue.Queue = queue.Queue()
        self.crawl_stats = {
            'pages_crawled': 0,
            'pages_failed': 0,
            'total_size_bytes': 0,
            'start_time': None,
            'end_time': None
        }

        # Knowledge index
        self.knowledge_index: Dict[str, Dict] = {}

        # Thread safety
        self.lock = threading.Lock()

        self.logger.info("EQ12 HTML Crawler initialized for domain: %s", self.base_domain)
        self.logger.info("Configuration: %s", {k: v for k, v in self.config.items() if 'dir' not in k})

    def setup_directories(self):
        """Create necessary directories"""
        dirs_to_create = [
            self.config['data_dir'],
            self.config['data_dir'] / 'html',
            self.config['data_dir'] / 'text',
            self.config['data_dir'] / 'index',
            self.config['logs_dir']
        ]

        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)

    def setup_logging(self):
        """Setup comprehensive logging system"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.config['logs_dir'] / f"eq12_html_crawler_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(log_file, encoding='ascii', errors='replace'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger('eq12_html_crawler')
        self.logger.info(f"Logging initialized: {log_file}")

    def normalize_url(self, url: str) -> str:
        """
        Normalize URLs for consistency

        Teaching note (Day 14 - String processing): URL normalization
        is critical for avoiding duplicate crawling and maintaining state.
        """
        # Remove fragment
        url, _fragment = urldefrag(url)

        # Parse URL
        parsed = urlparse(url)

        # Ensure scheme
        if not parsed.scheme:
            parsed = parsed._replace(scheme='https')

        # Normalize domain
        if not parsed.netloc:
            base_netloc = urlparse(self.base_url).netloc if hasattr(self, 'base_url') else 'html.com'
            parsed = parsed._replace(netloc=base_netloc)

        # Clean up domain
        netloc = parsed.netloc.lower()
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        parsed = parsed._replace(netloc=netloc)

        # Normalize path
        path = parsed.path or '/'
        if path != '/' and path.endswith('/'):
            path = path[:-1]
        parsed = parsed._replace(path=path)

        return parsed.geturl()

    def load_robots_parser(self) -> Optional[RobotFileParser]:
        """Load and parse robots.txt"""
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()

            self.logger.info("Successfully loaded robots.txt from %s", robots_url)
            return rp

        except Exception as e:
            self.logger.warning("Could not load robots.txt: %s", str(e))
            return None

    def is_crawl_allowed(self, url: str) -> bool:
        """Check if crawling is allowed by robots.txt"""
        if not self.robots_parser:
            return True

        try:
            return self.robots_parser.can_fetch(self.config['user_agent'], url)
        except Exception as e:
            self.logger.warning("Error checking robots.txt for %s: %s", url, str(e))
            return False

    def is_internal_url(self, url: str) -> bool:
        """Check if URL belongs to the target domain"""
        parsed = urlparse(url)
        return parsed.netloc.endswith(self.base_domain.replace('www.', ''))

    def generate_filename(self, url: str, extension: str) -> str:
        """
        Generate safe filename from URL

        Teaching note (Day 12 - File operations): Safe filename generation
        prevents filesystem issues and ensures cross-platform compatibility.
        """
        # Create hash of URL for unique filename
        url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()

        # Extract meaningful part from URL path
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]

        if path_parts:
            # Use last path component, cleaned for filesystem
            meaningful_part = re.sub(r'[^\w\-.]', '_', path_parts[-1])[:50]
            filename = f"{meaningful_part}_{url_hash[:8]}.{extension}"
        else:
            filename = f"index_{url_hash[:8]}.{extension}"

        return filename

    def extract_text_content(self, html: str) -> Dict[str, Union[str, List[str]]]:
        """
        Extract and analyze text content from HTML

        Teaching note (Day 23 - Data processing): Professional text extraction
        with content analysis and metadata generation.
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Remove unwanted elements
        unwanted_tags = ['script', 'style', 'noscript', 'iframe', 'object', 'embed']
        for tag in soup(unwanted_tags):
            tag.decompose()

        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Extract metadata
        title = soup.find('title')
        title_text = title.get_text().strip() if title else 'No Title'

        meta_description = soup.find('meta', attrs={'name': 'description'})
        description = meta_description.get('content', '').strip() if meta_description else ''

        # Extract headings
        headings = []
        for h_tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                'level': h_tag.name,
                'text': h_tag.get_text().strip()
            })

        # Extract main content
        main_content = soup.get_text(separator=' ')

        # Clean up whitespace
        clean_text = re.sub(r'\s+', ' ', main_content).strip()

        # Extract links
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            link_text = a_tag.get_text().strip()
            if href and link_text:
                links.append({'url': href, 'text': link_text})

        return {
            'title': title_text,
            'description': description,
            'content': clean_text,
            'headings': headings,
            'links': links,
            'word_count': len(clean_text.split()),
            'char_count': len(clean_text)
        }

    def create_knowledge_index(self, url: str, content_data: Dict) -> Dict:
        """
        Create knowledge index entry for the content

        Teaching note (Day 26 - Data structures): Creating searchable
        indexes from unstructured content for later analysis.
        """
        text = content_data['content'].lower()

        # Simple tokenization
        tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text)

        # Word frequency analysis
        word_freq = {}
        for token in tokens:
            word_freq[token] = word_freq.get(token, 0) + 1

        # Get top words
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:25]

        # Extract key phrases (simple bigrams)
        bigrams = []
        for i in range(len(tokens) - 1):
            bigram = f"{tokens[i]} {tokens[i+1]}"
            bigrams.append(bigram)

        bigram_freq = {}
        for bigram in bigrams:
            bigram_freq[bigram] = bigram_freq.get(bigram, 0) + 1

        top_phrases = sorted(bigram_freq.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'url': url,
            'title': content_data['title'],
            'description': content_data['description'],
            'word_count': content_data['word_count'],
            'char_count': content_data['char_count'],
            'top_words': top_words,
            'top_phrases': top_phrases,
            'headings': content_data['headings'],
            'crawled_at': datetime.now().isoformat(),
            'links_count': len(content_data['links'])
        }

    def save_content(self, url: str, html: str, content_data: Dict) -> bool:
        """
        Save content to filesystem with EQ12 ASCII compatibility

        Teaching note (Day 12 - File operations): Professional file handling
        with proper encoding and error management.
        """
        try:
            # Save HTML if requested
            if self.config['save_html']:
                html_filename = self.generate_filename(url, 'html')
                html_path = self.config['data_dir'] / 'html' / html_filename

                with open(html_path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(html)

                self.logger.debug("Saved HTML: %s", html_path)

            # Save text content if requested
            if self.config['save_text']:
                text_filename = self.generate_filename(url, 'txt')
                text_path = self.config['data_dir'] / 'text' / text_filename

                # Create ASCII-compatible content
                ascii_content = f"""URL: {url}
Title: {content_data['title']}
Description: {content_data['description']}
Word Count: {content_data['word_count']}
Crawled: {datetime.now().isoformat()}

Content:
{content_data['content']}

Headings:
"""
                for heading in content_data['headings']:
                    ascii_content += f"{heading['level'].upper()}: {heading['text']}\n"

                # Ensure ASCII compatibility
                ascii_safe_content = ascii_content.encode('ascii', errors='replace').decode('ascii')

                with open(text_path, 'w', encoding='ascii', errors='replace') as f:
                    f.write(ascii_safe_content)

                self.logger.debug("Saved text: %s", text_path)

            return True

        except Exception as e:
            self.logger.error("Error saving content for %s: %s", url, str(e))
            return False

    def fetch_page(self, url: str) -> Optional[Tuple[str, Dict]]:
        """
        Fetch and process a single page

        Teaching note (Day 19 - Error handling): Robust page fetching
        with comprehensive error handling and timeout management.
        """
        if not self.is_crawl_allowed(url):
            self.logger.info("Crawling not allowed by robots.txt: %s", url)
            return None

        try:
            self.logger.info("Fetching: %s", url)

            response = self.session.get(
                url,
                timeout=self.config['request_timeout'],
                allow_redirects=True
            )

            # Rate limiting
            time.sleep(self.config['request_delay'])

            # Check response
            if response.status_code != 200:
                self.logger.warning("Non-200 status %d for %s", response.status_code, url)
                return None

            # Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                self.logger.info("Skipping non-HTML content: %s", url)
                return None

            # Extract content
            html = response.text
            content_data = self.extract_text_content(html)

            # Update statistics
            with self.lock:
                self.crawl_stats['total_size_bytes'] += len(html)

            return html, content_data

        except requests.exceptions.Timeout:
            self.logger.warning("Timeout fetching %s", url)
            return None

        except requests.exceptions.RequestException as e:
            self.logger.warning("Request error for %s: %s", url, str(e))
            return None

        except Exception as e:
            self.logger.error("Unexpected error fetching %s: %s", url, str(e))
            return None

    def extract_links(self, url: str, content_data: Dict) -> List[str]:
        """Extract and normalize internal links"""
        links = []

        for link_data in content_data['links']:
            href = link_data['url']

            # Skip non-HTTP links
            if href.startswith(('mailto:', 'tel:', 'ftp:', 'javascript:')):
                continue

            # Convert relative to absolute
            abs_url = urljoin(url, href)
            normalized_url = self.normalize_url(abs_url)

            # Only include internal links
            if self.is_internal_url(normalized_url):
                links.append(normalized_url)

        return links

    def crawl_single_page(self, url: str, depth: int = 0) -> Optional[Dict]:
        """Crawl a single page and return results"""
        if url in self.visited_urls or url in self.failed_urls:
            return None

        if depth > self.config['max_depth']:
            self.logger.debug("Max depth reached for %s", url)
            return None

        # Fetch page
        result = self.fetch_page(url)
        if not result:
            with self.lock:
                self.failed_urls.add(url)
                self.crawl_stats['pages_failed'] += 1
            return None

        html, content_data = result

        # Mark as visited
        with self.lock:
            self.visited_urls.add(url)
            self.crawl_stats['pages_crawled'] += 1

        # Save content
        if not self.save_content(url, html, content_data):
            self.logger.warning("Failed to save content for %s", url)

        # Create knowledge index entry
        if self.config['create_index']:
            index_entry = self.create_knowledge_index(url, content_data)
            with self.lock:
                self.knowledge_index[url] = index_entry

        # Extract new links for crawling
        new_links = self.extract_links(url, content_data)

        # Add new links to queue
        for link in new_links:
            if link not in self.visited_urls and link not in self.failed_urls:
                self.url_queue.put((link, depth + 1))

        self.logger.info("Crawled %s - Found %d new links", url, len(new_links))

        return {
            'url': url,
            'status': 'success',
            'new_links': len(new_links),
            'content_size': len(html)
        }

    def crawl_parallel(self, max_workers: Optional[int] = None) -> Dict:
        """
        Execute parallel crawling with thread pool

        Teaching note (Day 25 - Concurrency): Professional parallel processing
        with proper thread management and resource control.
        """
        max_workers = max_workers or self.config['max_workers']

        self.crawl_stats['start_time'] = datetime.now()
        self.logger.info("Starting parallel crawl with %d workers", max_workers)

        # Add initial URL
        self.url_queue.put((self.base_url, 0))

        crawl_results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []

            while (not self.url_queue.empty() and
                   self.crawl_stats['pages_crawled'] < self.config['max_pages']):

                # Submit available URLs to thread pool
                while (len(futures) < max_workers and
                       not self.url_queue.empty() and
                       self.crawl_stats['pages_crawled'] < self.config['max_pages']):

                    try:
                        url, depth = self.url_queue.get_nowait()
                        future = executor.submit(self.crawl_single_page, url, depth)
                        futures.append(future)
                    except queue.Empty:
                        break

                # Process completed futures
                if futures:
                    completed_futures = []
                    for future in futures:
                        if future.done():
                            try:
                                result = future.result(timeout=1)
                                if result:
                                    crawl_results.append(result)
                            except Exception as e:
                                self.logger.error("Error processing future: %s", str(e))
                            completed_futures.append(future)

                    # Remove completed futures
                    for future in completed_futures:
                        futures.remove(future)

                # Small delay to prevent busy waiting
                time.sleep(0.1)

            # Wait for remaining futures
            for future in futures:
                try:
                    result = future.result(timeout=30)
                    if result:
                        crawl_results.append(result)
                except Exception as e:
                    self.logger.error("Error waiting for future: %s", str(e))

        self.crawl_stats['end_time'] = datetime.now()

        return {
            'crawl_results': crawl_results,
            'stats': self.crawl_stats,
            'total_urls_visited': len(self.visited_urls),
            'total_urls_failed': len(self.failed_urls)
        }

    def save_knowledge_index(self) -> Path:
        """Save the knowledge index to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        index_filename = f"knowledge_index_{timestamp}.json"
        index_path = self.config['data_dir'] / 'index' / index_filename

        # Create comprehensive index
        full_index = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'base_url': self.base_url,
                'total_pages': len(self.knowledge_index),
                'crawl_stats': self.crawl_stats
            },
            'pages': self.knowledge_index
        }

        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(full_index, f, indent=2, ensure_ascii=False)

            self.logger.info("Knowledge index saved: %s", index_path)
            return index_path

        except Exception as e:
            self.logger.error("Error saving knowledge index: %s", str(e))
            raise

    def generate_crawl_report(self, crawl_results: Dict) -> Path:
        """Generate comprehensive crawl report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"crawl_report_{timestamp}.json"
        report_path = self.config['logs_dir'] / report_filename

        # Calculate metrics
        total_time = (self.crawl_stats['end_time'] - self.crawl_stats['start_time']).total_seconds()
        pages_per_minute = (self.crawl_stats['pages_crawled'] / total_time * 60) if total_time > 0 else 0

        report = {
            'crawl_session': {
                'base_url': self.base_url,
                'start_time': self.crawl_stats['start_time'].isoformat(),
                'end_time': self.crawl_stats['end_time'].isoformat(),
                'duration_seconds': total_time,
                'configuration': self.config
            },
            'statistics': {
                'pages_crawled': self.crawl_stats['pages_crawled'],
                'pages_failed': self.crawl_stats['pages_failed'],
                'success_rate': (self.crawl_stats['pages_crawled'] /
                               (self.crawl_stats['pages_crawled'] + self.crawl_stats['pages_failed']))
                               if (self.crawl_stats['pages_crawled'] + self.crawl_stats['pages_failed']) > 0 else 0,
                'total_size_mb': self.crawl_stats['total_size_bytes'] / (1024 * 1024),
                'pages_per_minute': pages_per_minute,
                'avg_page_size_kb': (self.crawl_stats['total_size_bytes'] / self.crawl_stats['pages_crawled'] / 1024)
                                   if self.crawl_stats['pages_crawled'] > 0 else 0
            },
            'crawl_results': crawl_results['crawl_results']
        }

        try:
            with open(report_path, 'w', encoding='ascii', errors='replace') as f:
                json.dump(report, f, indent=2, ensure_ascii=True, default=str)

            self.logger.info("Crawl report saved: %s", report_path)
            return report_path

        except Exception as e:
            self.logger.error("Error saving crawl report: %s", str(e))
            raise

def main():
    """
    Main entry point for EQ12 HTML Crawler

    Teaching note (Day 11 - Functions): Professional CLI with comprehensive
    argument parsing and configuration management.
    """
    parser = argparse.ArgumentParser(
        description='EQ12 Expert HTML Crawler - Professional Web Content Extraction',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --url https://html.com --max-pages 100
  %(prog)s --url https://html.com --deep-crawl --parallel 5
  %(prog)s --url https://html.com --extract-knowledge --save-index
  %(prog)s --config crawler_config.json
        """
    )

    # URL configuration
    parser.add_argument('--url', required=True, help='Base URL to start crawling')
    parser.add_argument('--max-pages', type=int, default=1000, help='Maximum pages to crawl')
    parser.add_argument('--max-depth', type=int, default=10, help='Maximum crawl depth')

    # Crawling behavior
    parser.add_argument('--parallel', type=int, default=3, help='Number of parallel workers')
    parser.add_argument('--delay', type=float, default=1.5, help='Delay between requests (seconds)')
    parser.add_argument('--timeout', type=int, default=15, help='Request timeout (seconds)')

    # Features
    parser.add_argument('--deep-crawl', action='store_true', help='Enable deep crawling')
    parser.add_argument('--extract-knowledge', action='store_true', help='Create knowledge index')
    parser.add_argument('--save-index', action='store_true', help='Save searchable index')
    parser.add_argument('--no-robots', action='store_true', help='Ignore robots.txt')

    # Output options
    parser.add_argument('--output-dir', help='Output directory for data')
    parser.add_argument('--config', help='JSON config file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    try:
        # Load configuration
        config = {}
        if args.config and Path(args.config).exists():
            with open(args.config, 'r') as f:
                config = json.load(f)

        # Override with command line arguments
        config.update({
            'max_pages': args.max_pages,
            'max_depth': args.max_depth if args.deep_crawl else 3,
            'max_workers': args.parallel,
            'request_delay': args.delay,
            'request_timeout': args.timeout,
            'respect_robots': not args.no_robots,
            'extract_knowledge': args.extract_knowledge,
            'create_index': args.save_index or args.extract_knowledge
        })

        if args.output_dir:
            config['data_dir'] = Path(args.output_dir)

        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Initialize crawler
        print("🕷️ EQ12 Expert HTML Crawler")
        print("Professional Web Content Extraction System")
        print("=" * 60)

        crawler = EQ12HTMLCrawler(args.url, config)

        # Execute crawl
        print(f"🚀 Starting crawl of {args.url}")
        print(f"📊 Max pages: {args.max_pages}, Max depth: {config['max_depth']}")
        print(f"🔧 Workers: {args.parallel}, Delay: {args.delay}s")
        print("=" * 60)

        crawl_results = crawler.crawl_parallel()

        # Save results
        if crawler.config['create_index']:
            index_path = crawler.save_knowledge_index()
            print(f"📚 Knowledge index saved: {index_path}")

        report_path = crawler.generate_crawl_report(crawl_results)
        print(f"📋 Crawl report saved: {report_path}")

        # Print summary
        stats = crawl_results['stats']
        print("\n" + "=" * 60)
        print("🎯 CRAWL SUMMARY")
        print("=" * 60)
        print(f"✅ Pages crawled: {stats['pages_crawled']}")
        print(f"❌ Pages failed: {stats['pages_failed']}")
        print(f"📊 Success rate: {(stats['pages_crawled'] / (stats['pages_crawled'] + stats['pages_failed']) * 100):.1f}%")
        print(f"💾 Total size: {stats['total_size_bytes'] / (1024*1024):.2f} MB")

        duration = (stats['end_time'] - stats['start_time']).total_seconds()
        print(f"⏱️ Duration: {duration:.1f} seconds")
        print(f"🚀 Speed: {stats['pages_crawled'] / duration * 60:.1f} pages/min")

        print("\n🎉 Crawl completed successfully!")
        return 0

    except KeyboardInterrupt:
        print("\n🛑 Crawl cancelled by user")
        return 130

    except Exception as e:
        print(f"\n💥 Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
