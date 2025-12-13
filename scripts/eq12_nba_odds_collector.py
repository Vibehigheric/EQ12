#!/usr/bin/env python3
"""
EQ12 NBA Odds Collection System
Collects real-time NBA odds, player props, and game data optimized for cluster processing.
Designed for EQ12 + Pi5 + Coral TPU distributed betting intelligence.
"""

import asyncio
import aiohttp
import sqlite3
import pandas as pd
import numpy as np
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
import time
from dataclasses import dataclass
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# EQ12 Cluster Configuration
EQ12_CONFIG = {
    "data_dir": "C:/EQ12/data",
    "logs_dir": "C:/EQ12/logs", 
    "pi_host": "192.168.100.2",
    "cluster_mode": True
}

@dataclass
class NBAGame:
    """NBA game data structure optimized for TPU inference"""
    game_id: str
    home_team: str
    away_team: str
    game_time: datetime
    home_spread: float
    away_spread: float
    total_over: float
    total_under: float
    home_ml: int
    away_ml: int
    updated: datetime

@dataclass
class PlayerProp:
    """Player prop betting data structure"""
    prop_id: str
    player_name: str
    team: str
    stat_type: str  # points, rebounds, assists, threes
    line: float
    over_odds: int
    under_odds: int
    game_id: str
    updated: datetime

class EQ12_NBA_Collector:
    """NBA Odds Collection Engine for EQ12 Cluster"""
    
    def __init__(self, config: Dict = None):
        self.config = config or EQ12_CONFIG
        self.setup_logging()
        self.setup_database()
        self.api_keys = self.load_api_keys()
        self.session = None
        
    def setup_logging(self):
        """Initialize logging for cluster operations"""
        log_file = f"{self.config['logs_dir']}/nba_collector_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_database(self):
        """Initialize SQLite database for NBA data storage"""
        db_path = f"{self.config['data_dir']}/nba_cluster.db"
        Path(self.config['data_dir']).mkdir(exist_ok=True)
        
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
        
    def create_tables(self):
        """Create optimized database schema for NBA betting data"""
        
        # Games table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS nba_games (
                game_id TEXT PRIMARY KEY,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                game_time TIMESTAMP,
                home_spread REAL,
                away_spread REAL,
                total_over REAL,
                total_under REAL,
                home_ml INTEGER,
                away_ml INTEGER,
                updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_game_time ON nba_games(game_time),
                INDEX idx_teams ON nba_games(home_team, away_team)
            )
        ''')
        
        # Player props table 
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS player_props (
                prop_id TEXT PRIMARY KEY,
                player_name TEXT NOT NULL,
                team TEXT NOT NULL,
                stat_type TEXT NOT NULL,
                line REAL NOT NULL,
                over_odds INTEGER,
                under_odds INTEGER,
                game_id TEXT,
                updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES nba_games(game_id),
                INDEX idx_player_stat ON player_props(player_name, stat_type),
                INDEX idx_game_props ON player_props(game_id)
            )
        ''')
        
        # Historical performance table (for TPU training)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS player_performance (
                performance_id TEXT PRIMARY KEY,
                player_name TEXT NOT NULL,
                team TEXT NOT NULL,
                opponent TEXT NOT NULL,
                game_date DATE,
                points INTEGER,
                rebounds INTEGER,
                assists INTEGER,
                threes INTEGER,
                minutes_played REAL,
                game_pace REAL,
                usage_rate REAL,
                rest_days INTEGER,
                updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_player_date ON player_performance(player_name, game_date),
                INDEX idx_team_date ON player_performance(team, game_date)
            )
        ''')
        
        # Odds movement tracking
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS odds_movement (
                movement_id TEXT PRIMARY KEY,
                game_id TEXT,
                prop_id TEXT,
                market_type TEXT,
                old_line REAL,
                new_line REAL,
                old_odds INTEGER,
                new_odds INTEGER,
                movement_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sharp_indicator BOOLEAN DEFAULT FALSE,
                INDEX idx_movement_time ON odds_movement(movement_time),
                INDEX idx_sharp_moves ON odds_movement(sharp_indicator, movement_time)
            )
        ''')
        
        self.conn.commit()
        self.logger.info(" NBA database tables initialized")
        
    def load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment variables"""
        keys = {
            'odds_api_key': os.getenv('ODDS_API_KEY'),
            'rapidapi_key': os.getenv('RAPIDAPI_KEY'),
            'sportsdata_key': os.getenv('SPORTSDATA_KEY')
        }
        
        missing_keys = [k for k, v in keys.items() if not v]
        if missing_keys:
            self.logger.warning(f" Missing API keys: {missing_keys}")
            
        return keys
    
    async def fetch_odds_api_data(self) -> List[NBAGame]:
        """Fetch NBA odds from The Odds API"""
        
        if not self.api_keys['odds_api_key']:
            self.logger.error(" ODDS_API_KEY not found")
            return []
            
        url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
        params = {
            'api_key': self.api_keys['odds_api_key'],
            'regions': 'us',
            'markets': 'h2h,spreads,totals',
            'oddsFormat': 'american',
            'dateFormat': 'iso'
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    self.logger.error(f" Odds API error: {response.status}")
                    return []
                    
                data = await response.json()
                games = []
                
                for game_data in data:
                    game = self.parse_odds_api_game(game_data)
                    if game:
                        games.append(game)
                        
                self.logger.info(f" Fetched {len(games)} NBA games from Odds API")
                return games
                
        except Exception as e:
            self.logger.error(f" Error fetching odds: {e}")
            return []
    
    def parse_odds_api_game(self, game_data: Dict) -> Optional[NBAGame]:
        """Parse game data from Odds API response"""
        try:
            game_id = game_data['id']
            home_team = game_data['home_team']
            away_team = game_data['away_team']
            game_time = datetime.fromisoformat(game_data['commence_time'].replace('Z', '+00:00'))
            
            # Extract betting lines from bookmakers
            spreads = {}
            totals = {}
            h2h = {}
            
            for bookmaker in game_data.get('bookmakers', []):
                if bookmaker['key'] in ['fanduel', 'betmgm', 'draftkings']:
                    for market in bookmaker['markets']:
                        if market['key'] == 'spreads':
                            for outcome in market['outcomes']:
                                if outcome['name'] == home_team:
                                    spreads['home'] = outcome['point']
                                elif outcome['name'] == away_team:
                                    spreads['away'] = outcome['point']
                                    
                        elif market['key'] == 'totals':
                            if market['outcomes']:
                                totals['over'] = market['outcomes'][0]['point']
                                totals['under'] = market['outcomes'][0]['point']
                                
                        elif market['key'] == 'h2h':
                            for outcome in market['outcomes']:
                                if outcome['name'] == home_team:
                                    h2h['home'] = outcome['price']
                                elif outcome['name'] == away_team:
                                    h2h['away'] = outcome['price']
            
            return NBAGame(
                game_id=game_id,
                home_team=home_team,
                away_team=away_team,
                game_time=game_time,
                home_spread=spreads.get('home', 0.0),
                away_spread=spreads.get('away', 0.0),
                total_over=totals.get('over', 0.0),
                total_under=totals.get('under', 0.0),
                home_ml=h2h.get('home', 0),
                away_ml=h2h.get('away', 0),
                updated=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.error(f" Error parsing game data: {e}")
            return None
    
    async def fetch_player_props(self) -> List[PlayerProp]:
        """Fetch NBA player props from multiple sources"""
        
        if not self.api_keys['rapidapi_key']:
            self.logger.warning(" RapidAPI key missing - skipping player props")
            return []
        
        # This would integrate with RapidAPI NBA endpoints
        # For demo purposes, returning sample data structure
        props = []
        
        # Sample prop data structure (replace with actual API calls)
        sample_props = [
            {
                'prop_id': 'lebron_points_20241108',
                'player_name': 'LeBron James',
                'team': 'LAL',
                'stat_type': 'points',
                'line': 25.5,
                'over_odds': -110,
                'under_odds': -110,
                'game_id': 'lal_vs_bos_20241108'
            }
        ]
        
        for prop_data in sample_props:
            prop = PlayerProp(
                prop_id=prop_data['prop_id'],
                player_name=prop_data['player_name'],
                team=prop_data['team'],
                stat_type=prop_data['stat_type'],
                line=prop_data['line'],
                over_odds=prop_data['over_odds'],
                under_odds=prop_data['under_odds'],
                game_id=prop_data['game_id'],
                updated=datetime.utcnow()
            )
            props.append(prop)
        
        self.logger.info(f" Fetched {len(props)} player props")
        return props
    
    def store_games(self, games: List[NBAGame]):
        """Store NBA games in database with upsert logic"""
        
        for game in games:
            self.conn.execute('''
                INSERT OR REPLACE INTO nba_games 
                (game_id, home_team, away_team, game_time, home_spread, away_spread, 
                 total_over, total_under, home_ml, away_ml, updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                game.game_id, game.home_team, game.away_team, game.game_time,
                game.home_spread, game.away_spread, game.total_over, game.total_under,
                game.home_ml, game.away_ml, game.updated
            ))
        
        self.conn.commit()
        self.logger.info(f" Stored {len(games)} NBA games")
    
    def store_props(self, props: List[PlayerProp]):
        """Store player props in database"""
        
        for prop in props:
            self.conn.execute('''
                INSERT OR REPLACE INTO player_props
                (prop_id, player_name, team, stat_type, line, over_odds, under_odds, game_id, updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prop.prop_id, prop.player_name, prop.team, prop.stat_type,
                prop.line, prop.over_odds, prop.under_odds, prop.game_id, prop.updated
            ))
        
        self.conn.commit()
        self.logger.info(f" Stored {len(props)} player props")
    
    def detect_line_movement(self):
        """Detect significant line movements for sharp betting indicators"""
        
        query = '''
            SELECT game_id, home_spread, away_spread, total_over, updated
            FROM nba_games 
            WHERE updated > datetime('now', '-1 hour')
            ORDER BY game_id, updated
        '''
        
        df = pd.read_sql_query(query, self.conn)
        movements = []
        
        for game_id in df['game_id'].unique():
            game_data = df[df['game_id'] == game_id].sort_values('updated')
            
            if len(game_data) > 1:
                # Check for spread movement > 1 point
                spread_diff = abs(game_data.iloc[-1]['home_spread'] - game_data.iloc[0]['home_spread'])
                if spread_diff >= 1.0:
                    movements.append({
                        'game_id': game_id,
                        'movement_type': 'spread',
                        'movement_size': spread_diff,
                        'sharp_indicator': spread_diff >= 2.0
                    })
        
        if movements:
            self.logger.info(f" Detected {len(movements)} significant line movements")
            
        return movements
    
    async def run_collection_cycle(self):
        """Execute one complete data collection cycle"""
        
        self.logger.info(" Starting NBA data collection cycle")
        
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # Collect odds and props in parallel
            tasks = [
                self.fetch_odds_api_data(),
                self.fetch_player_props()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            games = results[0] if not isinstance(results[0], Exception) else []
            props = results[1] if not isinstance(results[1], Exception) else []
            
            # Store data
            if games:
                self.store_games(games)
            if props:
                self.store_props(props)
            
            # Analyze movements
            movements = self.detect_line_movement()
            
            # Generate collection report
            report = {
                'timestamp': datetime.utcnow().isoformat(),
                'games_collected': len(games),
                'props_collected': len(props),
                'movements_detected': len(movements),
                'cluster_node': 'EQ12-Host'
            }
            
            # Save report for cluster coordination
            report_file = f"{self.config['logs_dir']}/nba_collection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f" Collection cycle complete: {report}")
    
    async def run_continuous_collection(self, interval_minutes: int = 15):
        """Run continuous data collection for live betting"""
        
        self.logger.info(f" Starting continuous NBA collection (every {interval_minutes}m)")
        
        while True:
            try:
                await self.run_collection_cycle()
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                self.logger.info(" Collection stopped by user")
                break
            except Exception as e:
                self.logger.error(f" Collection error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def get_today_games(self) -> pd.DataFrame:
        """Get today's NBA games for cluster processing"""
        
        query = '''
            SELECT * FROM nba_games 
            WHERE date(game_time) = date('now')
            ORDER BY game_time
        '''
        
        return pd.read_sql_query(query, self.conn)
    
    def get_player_props_by_game(self, game_id: str) -> pd.DataFrame:
        """Get player props for specific game"""
        
        query = '''
            SELECT * FROM player_props 
            WHERE game_id = ?
            ORDER BY player_name, stat_type
        '''
        
        return pd.read_sql_query(query, self.conn, params=[game_id])
    
    def export_for_tpu_processing(self) -> str:
        """Export data in format optimized for Coral TPU processing"""
        
        # Export today's data for TPU inference
        export_data = {
            'games': self.get_today_games().to_dict('records'),
            'props': pd.read_sql_query(
                "SELECT * FROM player_props WHERE date(updated) = date('now')", 
                self.conn
            ).to_dict('records'),
            'export_timestamp': datetime.utcnow().isoformat(),
            'cluster_ready': True
        }
        
        export_file = f"{self.config['data_dir']}/nba_tpu_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f" Data exported for TPU processing: {export_file}")
        return export_file

def main():
    parser = argparse.ArgumentParser(description="EQ12 NBA Odds Collection System")
    parser.add_argument('--mode', choices=['single', 'continuous'], default='single',
                       help='Collection mode: single cycle or continuous')
    parser.add_argument('--interval', type=int, default=15,
                       help='Collection interval in minutes (continuous mode)')
    parser.add_argument('--export-tpu', action='store_true',
                       help='Export data for TPU processing')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    collector = EQ12_NBA_Collector()
    
    try:
        if args.mode == 'continuous':
            asyncio.run(collector.run_continuous_collection(args.interval))
        else:
            asyncio.run(collector.run_collection_cycle())
            
        if args.export_tpu:
            export_file = collector.export_for_tpu_processing()
            print(f" TPU export ready: {export_file}")
            
    except KeyboardInterrupt:
        print("\n Collection stopped")
    except Exception as e:
        print(f" Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())