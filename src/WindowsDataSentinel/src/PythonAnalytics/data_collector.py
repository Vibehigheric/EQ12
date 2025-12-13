#!/usr/bin/env python3
"""
Windows Data Sentinel - Python Data Collector
Fallback collector for RSS feeds and JSON APIs
Writes to SQLite database for dashboard consumption
"""

import json
import sqlite3
import argparse
import logging
import feedparser
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DataCollector')


class WindowsDataCollector:
    """Collects data from RSS feeds and JSON APIs"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.db_path = self.config['databasePath']
        self._init_database()
    
    def _load_config(self) -> dict:
        """Load configuration from JSON"""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _init_database(self):
        """Initialize SQLite database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Items (
                Id INTEGER PRIMARY KEY AUTOINCREMENT,
                SourceName TEXT NOT NULL,
                Category TEXT NOT NULL,
                ItemId TEXT NOT NULL,
                Title TEXT,
                Url TEXT,
                PublishedUtc TEXT,
                RawJson TEXT,
                InsertedUtc TEXT NOT NULL,
                UNIQUE(SourceName, ItemId)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_category 
            ON Items(Category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_source 
            ON Items(SourceName)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_published 
            ON Items(PublishedUtc DESC)
        """)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized: {self.db_path}")
    
    def process_feed(self, feed_config: dict):
        """Process a single feed based on its type"""
        if not feed_config.get('enabled', False):
            logger.debug(f"Skipping disabled feed: {feed_config['name']}")
            return
        
        feed_type = feed_config['type']
        feed_name = feed_config['name']
        
        logger.info(f"Processing {feed_type}: {feed_name}")
        
        try:
            if feed_type == 'rss':
                self._process_rss(feed_config)
            elif feed_type == 'api-json':
                self._process_json_api(feed_config)
            else:
                logger.warning(f"Unknown feed type: {feed_type}")
        except Exception as e:
            logger.error(f"Error processing {feed_name}: {e}")
    
    def _process_rss(self, feed_config: dict):
        """Process RSS feed"""
        feed_url = feed_config['url']
        source_name = feed_config['name']
        category = feed_config['category']
        
        try:
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"RSS feed has parsing issues: {source_name}")
            
            items_added = 0
            for entry in feed.entries:
                item_id = entry.get('id') or entry.get('link') or hashlib.md5(
                    (entry.get('title', '') + entry.get('published', '')).encode()
                ).hexdigest()
                
                title = entry.get('title')
                url = entry.get('link')
                
                # Parse published date
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    from time import mktime
                    published = datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone.utc)
                
                if self._upsert_item(source_name, category, item_id, title, url, published, None):
                    items_added += 1
            
            logger.info(f"  → Added {items_added} new items from {source_name}")
            
        except Exception as e:
            logger.error(f"RSS parsing error ({source_name}): {e}")
    
    def _process_json_api(self, feed_config: dict):
        """Process JSON API"""
        api_url = feed_config['url']
        source_name = feed_config['name']
        category = feed_config['category']
        
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Try to find results array
            items = None
            if isinstance(data, dict):
                # Common patterns: "results", "data", "items", "hits"
                for key in ['results', 'data', 'items', 'hits', 'response']:
                    if key in data and isinstance(data[key], list):
                        items = data[key]
                        break
                
                # If no array found, treat whole object as single item
                if items is None:
                    items = [data]
            elif isinstance(data, list):
                items = data
            else:
                items = [data]
            
            items_added = 0
            for item in items:
                # Extract common fields (flexible)
                item_id = (
                    item.get('id') or 
                    item.get('citation') or 
                    item.get('guid') or
                    hashlib.md5(json.dumps(item, sort_keys=True).encode()).hexdigest()
                )
                
                title = (
                    item.get('case_name') or 
                    item.get('title') or 
                    item.get('name') or 
                    item.get('headline')
                )
                
                url = (
                    item.get('absolute_url') or 
                    item.get('url') or 
                    item.get('link') or
                    item.get('href')
                )
                
                # Parse date
                published = None
                for date_key in ['date_filed', 'date_created', 'published', 'created_at', 'timestamp']:
                    if date_key in item:
                        try:
                            from dateutil import parser
                            published = parser.parse(item[date_key])
                            if published.tzinfo is None:
                                published = published.replace(tzinfo=timezone.utc)
                            break
                        except:
                            pass
                
                raw_json = json.dumps(item)
                
                if self._upsert_item(source_name, category, str(item_id), title, url, published, raw_json):
                    items_added += 1
            
            logger.info(f"  → Added {items_added} new items from {source_name}")
            
        except Exception as e:
            logger.error(f"API error ({source_name}): {e}")
    
    def _upsert_item(
        self, 
        source_name: str, 
        category: str, 
        item_id: str, 
        title: Optional[str],
        url: Optional[str],
        published: Optional[datetime],
        raw_json: Optional[str]
    ) -> bool:
        """Insert item if it doesn't exist. Returns True if new item added."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO Items 
                (SourceName, Category, ItemId, Title, Url, PublishedUtc, RawJson, InsertedUtc)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source_name,
                category,
                item_id,
                title,
                url,
                published.isoformat() if published else None,
                raw_json,
                datetime.now(timezone.utc).isoformat()
            ))
            
            rows_affected = cursor.rowcount
            conn.commit()
            
            return rows_affected > 0
            
        finally:
            conn.close()
    
    def run(self):
        """Process all enabled feeds"""
        logger.info("="*60)
        logger.info("Windows Data Sentinel - Python Collector")
        logger.info("="*60)
        
        feeds = self.config.get('feeds', [])
        enabled_feeds = [f for f in feeds if f.get('enabled', False)]
        
        logger.info(f"Processing {len(enabled_feeds)} enabled feeds (out of {len(feeds)} total)")
        
        for feed in enabled_feeds:
            self.process_feed(feed)
        
        logger.info("="*60)
        logger.info("Collection complete")
        logger.info("="*60)


def main():
    parser = argparse.ArgumentParser(description="Windows Data Sentinel - Python Collector")
    parser.add_argument('--config', default='C:\\EQ12\\WindowsDataSentinel\\config\\feeds.json',
                       help='Path to feeds.json configuration file')
    args = parser.parse_args()
    
    try:
        collector = WindowsDataCollector(args.config)
        collector.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main()
