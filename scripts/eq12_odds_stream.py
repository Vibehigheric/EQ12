#!/usr/bin/env python3
"""
EQ12 Live Odds Stream Collector
Collects and processes live sports betting odds from multiple APIs

Author: EQ12 Team
Date: November 2, 2025
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import requests
import feedparser


class LiveOddsCollector:
    """Collects live odds from multiple sports betting APIs"""
    
    def __init__(self, workspace_path: str, verbose: bool = False):
        self.workspace_path = Path(workspace_path)
        self.feeds_path = self.workspace_path / "coral_betting_ai" / "feeds"
        self.logs_path = self.workspace_path / "logs"
        
        # Ensure directories exist
        for path in [self.feeds_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)
            
        self.verbose = verbose
        self.setup_logging()
        
        # API configurations
        self.apis = {
            'odds_api': {
                'key': os.getenv('ODDS_API_KEY'),
                'base_url': 'https://api.the-odds-api.com/v4',
                'enabled': bool(os.getenv('ODDS_API_KEY'))
            },
            'sportsdata': {
                'key': os.getenv('SPORTSDATA_API_KEY'),
                'base_url': 'https://api.sportsdata.io',
                'enabled': bool(os.getenv('SPORTSDATA_API_KEY'))
            }
        }
        
        self.session = requests.Session()
        self.collected_feeds = []
        
    def setup_logging(self):
        """Setup logging for odds collection"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.logs_path / f"odds_collector_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.DEBUG if self.verbose else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def collect_odds_api_data(self, sport: str = 'americanfootball_nfl') -> List[Dict]:
        """Collect odds from The Odds API"""
        if not self.apis['odds_api']['enabled']:
            self.logger.warning("Odds API key not configured")
            return []
            
        try:
            api_key = self.apis['odds_api']['key']
            base_url = self.apis['odds_api']['base_url']
            
            # Get upcoming games
            url = f"{base_url}/sports/{sport}/odds"
            params = {
                'apiKey': api_key,
                'regions': 'us',
                'markets': 'h2h,spreads,totals',
                'oddsFormat': 'decimal',
                'dateFormat': 'iso'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            odds_data = []
            
            for game in data:
                # Process each game's odds
                game_odds = {
                    'game_id': game.get('id'),
                    'sport': sport,
                    'commence_time': game.get('commence_time'),
                    'home_team': game.get('home_team'),
                    'away_team': game.get('away_team'),
                    'bookmakers': [],
                    'collected_at': datetime.now(timezone.utc).isoformat()
                }
                
                for bookmaker in game.get('bookmakers', []):
                    bm_data = {
                        'name': bookmaker.get('title'),
                        'markets': {}
                    }
                    
                    for market in bookmaker.get('markets', []):
                        market_key = market.get('key')
                        outcomes = []
                        
                        for outcome in market.get('outcomes', []):
                            outcomes.append({
                                'name': outcome.get('name'),
                                'price': outcome.get('price'),
                                'point': outcome.get('point')
                            })
                            
                        bm_data['markets'][market_key] = outcomes
                        
                    game_odds['bookmakers'].append(bm_data)
                    
                odds_data.append(game_odds)
                
            self.logger.info(f"Collected {len(odds_data)} games from Odds API")
            return odds_data
            
        except Exception as e:
            self.logger.error(f"Error collecting from Odds API: {e}")
            return []
            
    def collect_rss_feeds(self, feed_urls: List[str]) -> List[Dict]:
        """Collect data from RSS feeds"""
        rss_data = []
        
        for url in feed_urls:
            try:
                self.logger.info(f"Fetching RSS feed: {url}")
                feed = feedparser.parse(url)
                
                for entry in feed.entries:
                    feed_item = {
                        'title': entry.get('title', ''),
                        'link': entry.get('link', ''),
                        'description': entry.get('description', ''),
                        'published': entry.get('published', ''),
                        'source_url': url,
                        'collected_at': datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Try to extract odds information from description
                    feed_item.update(self.extract_odds_from_text(entry.get('description', '')))
                    
                    rss_data.append(feed_item)
                    
                self.logger.info(f"Collected {len(feed.entries)} items from {url}")
                
            except Exception as e:
                self.logger.error(f"Error collecting RSS from {url}: {e}")
                
        return rss_data
        
    def extract_odds_from_text(self, text: str) -> Dict:
        """Extract odds information from text using pattern matching"""
        odds_info = {}
        
        # Simple pattern matching for common odds formats
        import re
        
        # Decimal odds pattern (e.g., "1.85")
        decimal_odds = re.findall(r'\b\d+\.\d{2}\b', text)
        if decimal_odds:
            odds_info['decimal_odds_found'] = decimal_odds
            
        # American odds pattern (e.g., "+150", "-200")
        american_odds = re.findall(r'[+-]\d{3,}', text)
        if american_odds:
            odds_info['american_odds_found'] = american_odds
            
        # Over/Under pattern
        ou_pattern = re.findall(r'(?:over|under)\s+(\d+\.?\d*)', text.lower())
        if ou_pattern:
            odds_info['over_under_totals'] = ou_pattern
            
        # Spread pattern
        spread_pattern = re.findall(r'[+-]\d+\.?\d*\s*(?:points?|pts?)', text.lower())
        if spread_pattern:
            odds_info['spreads_found'] = spread_pattern
            
        return odds_info
        
    def save_collected_data(self, data: List[Dict], data_type: str):
        """Save collected odds data to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{data_type}_odds_{timestamp}.json"
        filepath = self.feeds_path / filename
        
        output_data = {
            'collection_timestamp': datetime.now(timezone.utc).isoformat(),
            'data_type': data_type,
            'total_items': len(data),
            'bets': data
        }
        
        with open(filepath, 'w') as f:
            json.dump(output_data, f, indent=2)
            
        self.logger.info(f"Saved {len(data)} items to {filepath}")
        return str(filepath)
        
    def collect_live_feeds(self, sports: List[str] = None, rss_urls: List[str] = None) -> str:
        """Main method to collect all live feeds"""
        if sports is None:
            sports = ['americanfootball_nfl', 'basketball_nba', 'baseball_mlb']
            
        if rss_urls is None:
            rss_urls = [
                'https://www.actionnetwork.com/rss',
                'https://www.vegasinsider.com/rss/news.xml'
            ]
            
        all_data = []
        
        # Collect from APIs
        for sport in sports:
            odds_data = self.collect_odds_api_data(sport)
            all_data.extend(odds_data)
            time.sleep(1)  # Rate limiting
            
        # Collect from RSS feeds
        rss_data = self.collect_rss_feeds(rss_urls)
        
        # Combine and enhance data
        combined_data = {
            'api_odds': all_data,
            'rss_feeds': rss_data,
            'collection_summary': {
                'total_api_games': len(all_data),
                'total_rss_items': len(rss_data),
                'collection_time': datetime.now(timezone.utc).isoformat(),
                'next_collection': (datetime.now(timezone.utc)).isoformat()
            }
        }
        
        # Save to master feed file
        filepath = self.save_master_feed(combined_data)
        
        self.logger.info(f"Collection complete. Total items: {len(all_data) + len(rss_data)}")
        return filepath
        
    def save_master_feed(self, data: Dict) -> str:
        """Save master feed file for Coral AI processing"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        master_file = self.feeds_path / f"live_odds_master_{timestamp}.json"
        
        with open(master_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        # Also save as 'latest' for automated processing
        latest_file = self.feeds_path / "live_odds_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(data, f, indent=2)
            
        return str(master_file)
        
    def generate_feed_report(self) -> Dict:
        """Generate report on feed collection performance"""
        feed_files = list(self.feeds_path.glob("live_odds_master_*.json"))
        
        if not feed_files:
            return {"error": "No feed data available"}
            
        # Get latest feed file
        latest_feed = max(feed_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_feed, 'r') as f:
                data = json.load(f)
                
            report = {
                'feed_collection_report': {
                    'last_collection': data.get('collection_summary', {}).get('collection_time'),
                    'api_games_collected': data.get('collection_summary', {}).get('total_api_games', 0),
                    'rss_items_collected': data.get('collection_summary', {}).get('total_rss_items', 0),
                    'total_feed_files': len(feed_files),
                    'latest_file': str(latest_feed),
                    'apis_configured': [name for name, config in self.apis.items() if config['enabled']],
                    'generated_at': datetime.now(timezone.utc).isoformat()
                }
            }
            
            return report
            
        except Exception as e:
            return {"error": f"Failed to generate report: {e}"}


def main():
    parser = argparse.ArgumentParser(description="EQ12 Live Odds Stream Collector")
    parser.add_argument("--workspace", default="c:/EQ12", help="Workspace path")
    parser.add_argument("--sports", nargs="+", 
                       default=['americanfootball_nfl', 'basketball_nba'],
                       help="Sports to collect odds for")
    parser.add_argument("--rss-urls", nargs="+", help="RSS feed URLs to collect")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    parser.add_argument("--report", action="store_true", help="Generate collection report")
    parser.add_argument("--continuous", action="store_true", 
                       help="Run continuous collection (every 30 seconds)")
    
    args = parser.parse_args()
    
    collector = LiveOddsCollector(args.workspace, args.verbose)
    
    if args.report:
        report = collector.generate_feed_report()
        print(json.dumps(report, indent=2))
        return
        
    if args.continuous:
        print("Starting continuous odds collection (Ctrl+C to stop)")
        try:
            while True:
                filepath = collector.collect_live_feeds(args.sports, args.rss_urls)
                print(f"Collection complete: {filepath}")
                time.sleep(30)  # Collect every 30 seconds
        except KeyboardInterrupt:
            print("\nStopping continuous collection")
    else:
        filepath = collector.collect_live_feeds(args.sports, args.rss_urls)
        print(f"Live odds collected and saved to: {filepath}")


if __name__ == "__main__":
    main()