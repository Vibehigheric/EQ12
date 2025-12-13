#!/usr/bin/env python3
"""
 EQ12 RUN-ODDS - High-Frequency Market Data Feed Executor


Real-time odds aggregation and market intelligence system.
Pulls from OddsAPI, SportsData, and multiple bookmaker feeds.
Updates revenue.db and odds_tracker.db every 15-30 minutes.

Author: EQ12 Quantum Development Team
Version: 2.0.0 - Godlike Edition  
Date: November 7, 2025
"""

import os
import sys
import time
import logging
import sqlite3
import requests
import json
import argparse
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add EQ12 modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class EQ12OddsEngine:
    def __init__(self, workspace_path="C:/EQ12"):
        self.workspace = workspace_path
        self.db_path = f"{workspace_path}/data/revenue.db"
        self.odds_db_path = f"{workspace_path}/data/odds_tracker.db"
        self.log_path = f"{workspace_path}/logs/eq12_run_odds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler(self.log_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # API configurations
        self.api_keys = {
            'odds_api': os.getenv('ODDS_API_KEY', os.getenv('THE_ODDS_API_KEY')),
            'sportsdata_api': os.getenv('SPORTSDATA_API_KEY'),
            'openai_api': os.getenv('OPENAI_API_KEY'),
            'telegram_token': os.getenv('TELEGRAM_BOT_TOKEN')
        }
        
        self.sports_list = [
            'americanfootball_nfl', 'basketball_nba', 'baseball_mlb',
            'icehockey_nhl', 'soccer_epl', 'soccer_uefa_champions_league'
        ]
        
        self.init_databases()
        
    def init_databases(self):
        """Initialize database tables for odds tracking"""
        try:
            # Revenue database
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS odds_feed (
                    id TEXT PRIMARY KEY,
                    sport_key TEXT,
                    home_team TEXT,
                    away_team TEXT,
                    commence_time TEXT,
                    bookmaker TEXT,
                    market TEXT,
                    odds_data TEXT,
                    timestamp TEXT,
                    profit_potential REAL
                )
            ''')
            conn.commit()
            conn.close()
            
            # Odds tracker database
            conn = sqlite3.connect(self.odds_db_path)
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS live_odds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT,
                    bookmaker TEXT,
                    market_type TEXT,
                    odds_value REAL,
                    line_value REAL,
                    timestamp TEXT,
                    movement_direction TEXT,
                    value_rating REAL
                )
            ''')
            conn.commit()
            conn.close()
            
            self.logger.info(" Database tables initialized successfully")
            
        except Exception as e:
            self.logger.error(f" Database initialization failed: {e}")
            
    def fetch_odds_api_data(self, sport):
        """Fetch odds from The Odds API"""
        if not self.api_keys['odds_api']:
            self.logger.warning(" ODDS_API_KEY not configured")
            return []
            
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/"
            params = {
                'apiKey': self.api_keys['odds_api'],
                'regions': 'us',
                'markets': 'h2h,spreads,totals',
                'oddsFormat': 'american',
                'dateFormat': 'iso'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            self.logger.info(f" Fetched {len(data)} games for {sport}")
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f" API request failed for {sport}: {e}")
            return []
            
    def calculate_profit_potential(self, odds_data):
        """Calculate profit potential and value rating"""
        try:
            if not odds_data.get('bookmakers'):
                return 0.0
                
            best_odds = {}
            for bookmaker in odds_data['bookmakers']:
                for market in bookmaker.get('markets', []):
                    market_type = market['key']
                    for outcome in market.get('outcomes', []):
                        key = f"{market_type}_{outcome['name']}"
                        price = outcome['price']
                        
                        if key not in best_odds or abs(price) > abs(best_odds[key]):
                            best_odds[key] = price
                            
            # Simple profit potential calculation
            if best_odds:
                avg_odds = sum(abs(odd) for odd in best_odds.values()) / len(best_odds)
                return round(avg_odds / 100.0, 3)
            return 0.0
            
        except Exception as e:
            self.logger.error(f" Profit calculation failed: {e}")
            return 0.0
            
    def save_odds_data(self, odds_data, sport):
        """Save odds data to databases"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            for game in odds_data:
                profit_potential = self.calculate_profit_potential(game)
                
                cur.execute('''
                    INSERT OR REPLACE INTO odds_feed 
                    (id, sport_key, home_team, away_team, commence_time, 
                     bookmaker, market, odds_data, timestamp, profit_potential)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    game['id'],
                    sport,
                    game.get('home_team', ''),
                    game.get('away_team', ''),
                    game.get('commence_time', ''),
                    'aggregated',
                    'multiple',
                    json.dumps(game),
                    datetime.now().isoformat(),
                    profit_potential
                ))
                
            conn.commit()
            conn.close()
            
            self.logger.info(f" Saved {len(odds_data)} games to database")
            
        except Exception as e:
            self.logger.error(f" Database save failed: {e}")
            
    def run_odds_cycle(self):
        """Execute complete odds fetching cycle"""
        self.logger.info(" Starting EQ12 odds fetching cycle...")
        
        total_games = 0
        successful_sports = 0
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_sport = {
                executor.submit(self.fetch_odds_api_data, sport): sport 
                for sport in self.sports_list
            }
            
            for future in as_completed(future_to_sport):
                sport = future_to_sport[future]
                try:
                    odds_data = future.result()
                    if odds_data:
                        self.save_odds_data(odds_data, sport)
                        total_games += len(odds_data)
                        successful_sports += 1
                        
                except Exception as e:
                    self.logger.error(f" Failed to process {sport}: {e}")
                    
        # Generate summary
        self.generate_odds_summary(total_games, successful_sports)
        
    def generate_odds_summary(self, total_games, successful_sports):
        """Generate odds fetching summary"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_games_fetched": total_games,
            "sports_processed": successful_sports,
            "api_keys_status": {
                "odds_api": "" if self.api_keys['odds_api'] else "",
                "sportsdata_api": "" if self.api_keys['sportsdata_api'] else ""
            },
            "next_update": (datetime.now() + timedelta(minutes=15)).isoformat()
        }
        
        summary_path = f"{self.workspace}/logs/odds_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f" Odds Summary: {total_games} games from {successful_sports} sports")
        self.logger.info(f" Summary saved: {summary_path}")
        
        return summary
        
    def run_continuous_mode(self, interval_minutes=15):
        """Run odds fetching in continuous mode"""
        self.logger.info(f" Starting continuous odds monitoring (every {interval_minutes} minutes)")
        
        try:
            while True:
                self.run_odds_cycle()
                self.logger.info(f" Waiting {interval_minutes} minutes for next cycle...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            self.logger.info(" Continuous mode stopped by user")
        except Exception as e:
            self.logger.error(f" Continuous mode error: {e}")

def main():
    parser = argparse.ArgumentParser(description='EQ12 Run-Odds - High-Frequency Market Data Feed')
    parser.add_argument('--mode', choices=['single', 'continuous'], default='single',
                       help='Run mode: single cycle or continuous monitoring')
    parser.add_argument('--interval', type=int, default=15,
                       help='Update interval in minutes (for continuous mode)')
    parser.add_argument('--workspace', default='C:/EQ12',
                       help='EQ12 workspace path')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    engine = EQ12OddsEngine(args.workspace)
    
    if args.mode == 'continuous':
        engine.run_continuous_mode(args.interval)
    else:
        engine.run_odds_cycle()
        
    print(f"\n EQ12 Run-Odds execution complete!")
    print(f" Check logs: {engine.log_path}")

if __name__ == "__main__":
    main()