#!/usr/bin/env python3
"""
EQ12 NBA Production Data Collector with AI Enhancement
Real-time NBA odds, props, and AI-powered analysis
November 8, 2025 - Production Ready
"""

import asyncio
import aiohttp
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import argparse
import logging
from pathlib import Path
import openai
import anthropic
from groq import Groq
import requests
from concurrent.futures import ThreadPoolExecutor
import hashlib
import pickle

# NBA Data Sources Integration
try:
    from nba_api.stats.endpoints import leaguegamefinder, scoreboardv2, teamgamelog
    from nba_api.stats.static import teams, players
    NBA_API_AVAILABLE = True
except ImportError:
    NBA_API_AVAILABLE = False
    print(" nba_api not available. Install with: pip install nba_api")


class NBAProductionCollector:
    """Production NBA data collector with AI enhancement"""
    
    def __init__(self, workspace_dir: str = "C:/EQ12", use_ai: bool = True):
        self.workspace_dir = Path(workspace_dir)
        self.data_dir = self.workspace_dir / "data"
        self.logs_dir = self.workspace_dir / "logs"
        self.models_dir = self.workspace_dir / "models"
        
        # Ensure directories exist
        for directory in [self.data_dir, self.logs_dir, self.models_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Load environment variables
        self.load_environment()
        
        # Setup logging
        self.setup_logging()
        
        # Initialize AI clients
        self.use_ai = use_ai
        if self.use_ai:
            self.setup_ai_clients()
        
        # Database setup
        self.setup_databases()
        
        # Rate limiting
        self.api_calls_minute = {}
        self.last_reset_time = time.time()
        
        # Performance tracking
        self.performance_stats = {
            "api_calls": 0,
            "successful_collections": 0,
            "ai_enhancements": 0,
            "errors": 0,
            "start_time": datetime.now()
        }
    
    def load_environment(self):
        """Load production environment variables"""
        env_file = self.workspace_dir / ".env.production"
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key] = value
        
        # Core API keys
        self.odds_api_key = os.getenv("ODDS_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.claude_api_key = os.getenv("CLAUDE_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.google_ai_key = os.getenv("GOOGLE_AI_API_KEY")
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY")
        
        # Configuration
        self.min_ev = float(os.getenv("MIN_EXPECTED_VALUE", "0.03"))
        self.min_confidence = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", "0.65"))
        self.focus_teams = os.getenv("FOCUS_TEAMS", "").split(",")
        self.prop_types = os.getenv("PROP_TYPES", "points,assists,rebounds").split(",")
        
        # Rate limits
        self.odds_api_limit = int(os.getenv("ODDS_API_REQUESTS_PER_MINUTE", "120"))
        self.openai_limit = int(os.getenv("OPENAI_REQUESTS_PER_MINUTE", "60"))
        self.claude_limit = int(os.getenv("CLAUDE_REQUESTS_PER_MINUTE", "30"))
    
    def setup_logging(self):
        """Configure production logging"""
        log_file = self.logs_dir / f"nba_production_{datetime.now().strftime('%Y%m%d')}.log"
        
        log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO"))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Performance log
        self.perf_log = self.logs_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.json"
    
    def setup_ai_clients(self):
        """Initialize AI service clients"""
        try:
            if self.openai_api_key:
                openai.api_key = self.openai_api_key
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                self.logger.info("OpenAI client initialized")
            
            if self.claude_api_key:
                self.claude_client = anthropic.Anthropic(api_key=self.claude_api_key)
                self.logger.info("Claude client initialized")
            
            if self.groq_api_key:
                self.groq_client = Groq(api_key=self.groq_api_key)
                self.logger.info("Groq client initialized")
        
        except Exception as e:
            self.logger.error(f"Error initializing AI clients: {e}")
            self.use_ai = False
    
    def setup_databases(self):
        """Initialize production databases"""
        # Main databases
        self.odds_db = self.data_dir / "nba_odds.db"
        self.props_db = self.data_dir / "nba_props.db"
        self.predictions_db = self.data_dir / "nba_predictions.db"
        self.ai_insights_db = self.data_dir / "nba_ai_insights.db"
        
        self.create_tables()
    
    def create_tables(self):
        """Create all required database tables"""
        try:
            # Odds table
            with sqlite3.connect(self.odds_db) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS odds (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id TEXT NOT NULL,
                        home_team TEXT NOT NULL,
                        away_team TEXT NOT NULL,
                        commence_time TIMESTAMP NOT NULL,
                        home_odds REAL,
                        away_odds REAL,
                        home_spread REAL,
                        away_spread REAL,
                        total_over REAL,
                        total_under REAL,
                        total_points REAL,
                        bookmaker TEXT NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        collection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(game_id, bookmaker, collection_time)
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_odds_game_time ON odds(game_id, collection_time)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_odds_commence ON odds(commence_time)")
            
            # Player props table  
            with sqlite3.connect(self.props_db) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS player_props (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id TEXT NOT NULL,
                        player_name TEXT NOT NULL,
                        player_id TEXT,
                        team TEXT NOT NULL,
                        prop_type TEXT NOT NULL,
                        line REAL NOT NULL,
                        over_odds REAL,
                        under_odds REAL,
                        bookmaker TEXT NOT NULL,
                        game_date DATE NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        collection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(game_id, player_name, prop_type, bookmaker, collection_time)
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_props_player_date ON player_props(player_name, game_date)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_props_game ON player_props(game_id)")
            
            # AI insights table
            with sqlite3.connect(self.ai_insights_db) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS ai_insights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id TEXT NOT NULL,
                        player_name TEXT,
                        insight_type TEXT NOT NULL,
                        ai_model TEXT NOT NULL,
                        insight_text TEXT NOT NULL,
                        confidence_score REAL,
                        impact_score REAL,
                        created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_relevant BOOLEAN DEFAULT 1
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_insights_game ON ai_insights(game_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_insights_player ON ai_insights(player_name)")
            
            self.logger.info("Database tables created successfully")
        
        except Exception as e:
            self.logger.error(f"Error creating database tables: {e}")
            raise
    
    def check_rate_limit(self, api_name: str, limit: int) -> bool:
        """Check if API call is within rate limit"""
        current_time = time.time()
        
        # Reset counters every minute
        if current_time - self.last_reset_time > 60:
            self.api_calls_minute = {}
            self.last_reset_time = current_time
        
        # Check current count
        current_count = self.api_calls_minute.get(api_name, 0)
        if current_count >= limit:
            return False
        
        # Increment counter
        self.api_calls_minute[api_name] = current_count + 1
        return True
    
    async def check_api_health(self, session: aiohttp.ClientSession) -> Dict[str, Dict[str, Any]]:
        """Check health status of all free NBA APIs"""
        health_status = {}
        
        # Check NBA API
        try:
            from nba_api.stats.endpoints import scoreboardv2
            scoreboard = scoreboardv2.ScoreboardV2()
            if scoreboard.get_data_frames():
                health_status["nba_api"] = {"status": "healthy", "response_time": 0.5, "error": None}
            else:
                health_status["nba_api"] = {"status": "degraded", "response_time": 0, "error": "No data returned"}
        except Exception as e:
            health_status["nba_api"] = {"status": "failed", "response_time": 0, "error": str(e)}
        
        # Check ESPN API
        try:
            start_time = time.time()
            async with session.get("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard", timeout=10) as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    health_status["espn"] = {"status": "healthy", "response_time": response_time, "error": None}
                else:
                    health_status["espn"] = {"status": "failed", "response_time": response_time, "error": f"HTTP {response.status}"}
        except Exception as e:
            health_status["espn"] = {"status": "failed", "response_time": 0, "error": str(e)}
        
        # Check Ball Don't Lie API
        try:
            start_time = time.time()
            async with session.get("https://api.balldontlie.io/v1/games", 
                                 headers={"Authorization": f"Bearer {os.getenv('BALLDONTLIE_API_KEY', '')}"}, 
                                 timeout=10) as response:
                response_time = time.time() - start_time
                if response.status == 200:
                    health_status["balldontlie"] = {"status": "healthy", "response_time": response_time, "error": None}
                else:
                    health_status["balldontlie"] = {"status": "failed", "response_time": response_time, "error": f"HTTP {response.status}"}
        except Exception as e:
            health_status["balldontlie"] = {"status": "failed", "response_time": 0, "error": str(e)}
        
        return health_status
    
    def get_api_priority_order(self, health_status: Dict[str, Dict[str, Any]]) -> List[tuple]:
        """Get API collection order based on health and performance"""
        api_configs = [
            ("nba_api", self.collect_nba_api_data, [], health_status.get("nba_api", {})),
            ("espn", self.collect_espn_data, [], health_status.get("espn", {})),
            ("balldontlie", self.collect_balldontlie_data, [], health_status.get("balldontlie", {}))
        ]
        
        # Sort by health status and response time
        def api_score(api_config):
            name, func, args, health = api_config
            status = health.get("status", "failed")
            response_time = health.get("response_time", 999)
            
            # Scoring: healthy=100, degraded=50, failed=0, plus bonus for speed
            base_score = {"healthy": 100, "degraded": 50, "failed": 0}.get(status, 0)
            speed_bonus = max(0, 10 - response_time)  # Faster APIs get higher priority
            
            return base_score + speed_bonus
        
        sorted_apis = sorted(api_configs, key=api_score, reverse=True)
        
        # Return as (name, func, args) tuples
        return [(name, func, args) for name, func, args, health in sorted_apis]
    
    async def collect_nba_odds(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Collect live NBA odds from The Odds API"""
        if not self.check_rate_limit("odds_api", self.odds_api_limit):
            self.logger.warning("Odds API rate limit reached")
            return []
        
        try:
            url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
            params = {
                "apiKey": self.odds_api_key,
                "regions": "us",
                "markets": "h2h,spreads,totals",
                "oddsFormat": "american",
                "dateFormat": "iso"
            }
            
            self.logger.info("Collecting NBA odds...")
            self.performance_stats["api_calls"] += 1
            
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    odds_collected = []
                    for game in data:
                        if not self.is_game_relevant(game):
                            continue
                        
                        game_odds = self.parse_odds_data(game)
                        if game_odds:
                            odds_collected.extend(game_odds)
                    
                    self.logger.info(f"Collected odds for {len(odds_collected)} bookmaker entries")
                    self.performance_stats["successful_collections"] += 1
                    return odds_collected
                
                else:
                    self.logger.error(f"Odds API error: {response.status}")
                    self.performance_stats["errors"] += 1
                    return []
        
        except Exception as e:
            self.logger.error(f"Error collecting NBA odds: {e}")
            self.performance_stats["errors"] += 1
            return []
    
    async def collect_player_props(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Collect NBA player props"""
        if not self.check_rate_limit("odds_api", self.odds_api_limit):
            self.logger.warning("Odds API rate limit reached for props")
            return []
        
        try:
            # Player points props
            props_collected = []
            
            for prop_type in ["player_points", "player_assists", "player_rebounds"]:
                url = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds"
                params = {
                    "apiKey": self.odds_api_key,
                    "regions": "us",
                    "markets": prop_type,
                    "oddsFormat": "american",
                    "dateFormat": "iso"
                }
                
                self.performance_stats["api_calls"] += 1
                
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for game in data:
                            if not self.is_game_relevant(game):
                                continue
                            
                            game_props = self.parse_props_data(game, prop_type)
                            if game_props:
                                props_collected.extend(game_props)
                    
                    await asyncio.sleep(0.5)  # Rate limiting
            
            self.logger.info(f"Collected {len(props_collected)} player props")
            return props_collected
        
        except Exception as e:
            self.logger.error(f"Error collecting player props: {e}")
            self.performance_stats["errors"] += 1
            return []
    
    def is_game_relevant(self, game: Dict[str, Any]) -> bool:
        """Check if game is relevant for analysis"""
        try:
            # Check if teams are in focus list
            home_team = game.get("home_team", "")
            away_team = game.get("away_team", "")
            
            if self.focus_teams:
                team_codes = [self.get_team_code(home_team), self.get_team_code(away_team)]
                if not any(code in self.focus_teams for code in team_codes):
                    return False
            
            # Check game time (focus on evening games)
            commence_time = game.get("commence_time")
            if commence_time:
                game_time = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
                game_hour = game_time.hour
                
                # Focus on evening games (7 PM - 10 PM EST)
                if game_hour < 19 or game_hour > 22:
                    return False
            
            return True
        
        except Exception as e:
            self.logger.warning(f"Error checking game relevance: {e}")
            return True  # Default to including game
    
    def get_team_code(self, team_name: str) -> str:
        """Convert team name to 3-letter code"""
        team_mapping = {
            "Los Angeles Lakers": "LAL",
            "Golden State Warriors": "GSW", 
            "Boston Celtics": "BOS",
            "Miami Heat": "MIA",
            "Denver Nuggets": "DEN",
            "Phoenix Suns": "PHX",
            "Milwaukee Bucks": "MIL",
            "Philadelphia 76ers": "PHI",
            "Dallas Mavericks": "DAL",
            "New York Knicks": "NYK"
        }
        return team_mapping.get(team_name, team_name[:3].upper())
    
    def parse_odds_data(self, game: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse odds data from API response"""
        try:
            game_id = f"{game['home_team']}_vs_{game['away_team']}_{game['commence_time']}"
            home_team = game["home_team"]
            away_team = game["away_team"]
            commence_time = game["commence_time"]
            
            odds_data = []
            
            for bookmaker in game.get("bookmakers", []):
                bookmaker_name = bookmaker["title"]
                
                odds_entry = {
                    "game_id": game_id,
                    "home_team": home_team,
                    "away_team": away_team,
                    "commence_time": commence_time,
                    "bookmaker": bookmaker_name,
                    "home_odds": None,
                    "away_odds": None,
                    "home_spread": None,
                    "away_spread": None,
                    "total_over": None,
                    "total_under": None,
                    "total_points": None
                }
                
                for market in bookmaker.get("markets", []):
                    market_key = market["key"]
                    
                    if market_key == "h2h":
                        # Money line odds
                        for outcome in market["outcomes"]:
                            if outcome["name"] == home_team:
                                odds_entry["home_odds"] = outcome["price"]
                            elif outcome["name"] == away_team:
                                odds_entry["away_odds"] = outcome["price"]
                    
                    elif market_key == "spreads":
                        # Spread odds
                        for outcome in market["outcomes"]:
                            if outcome["name"] == home_team:
                                odds_entry["home_spread"] = outcome["point"]
                            elif outcome["name"] == away_team:
                                odds_entry["away_spread"] = outcome["point"]
                    
                    elif market_key == "totals":
                        # Over/Under
                        for outcome in market["outcomes"]:
                            if outcome["name"] == "Over":
                                odds_entry["total_over"] = outcome["price"]
                                odds_entry["total_points"] = outcome["point"]
                            elif outcome["name"] == "Under":
                                odds_entry["total_under"] = outcome["price"]
                
                odds_data.append(odds_entry)
            
            return odds_data
        
        except Exception as e:
            self.logger.error(f"Error parsing odds data: {e}")
            return []
    
    def parse_props_data(self, game: Dict[str, Any], prop_type: str) -> List[Dict[str, Any]]:
        """Parse player props data"""
        try:
            game_id = f"{game['home_team']}_vs_{game['away_team']}_{game['commence_time']}"
            game_date = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00')).date()
            
            props_data = []
            
            for bookmaker in game.get("bookmakers", []):
                bookmaker_name = bookmaker["title"]
                
                for market in bookmaker.get("markets", []):
                    if market["key"] != prop_type:
                        continue
                    
                    # Group outcomes by player
                    player_props = {}
                    for outcome in market["outcomes"]:
                        player_name = outcome["description"]
                        outcome_type = outcome["name"]  # Over/Under
                        
                        if player_name not in player_props:
                            player_props[player_name] = {
                                "player_name": player_name,
                                "line": outcome["point"],
                                "over_odds": None,
                                "under_odds": None
                            }
                        
                        if outcome_type == "Over":
                            player_props[player_name]["over_odds"] = outcome["price"]
                        elif outcome_type == "Under":
                            player_props[player_name]["under_odds"] = outcome["price"]
                    
                    # Create prop entries
                    for player_name, prop_data in player_props.items():
                        if prop_data["over_odds"] and prop_data["under_odds"]:
                            props_data.append({
                                "game_id": game_id,
                                "player_name": player_name,
                                "team": self.get_player_team(player_name, game),
                                "prop_type": prop_type.replace("player_", ""),
                                "line": prop_data["line"],
                                "over_odds": prop_data["over_odds"],
                                "under_odds": prop_data["under_odds"],
                                "bookmaker": bookmaker_name,
                                "game_date": game_date.isoformat()
                            })
            
            return props_data
        
        except Exception as e:
            self.logger.error(f"Error parsing props data: {e}")
            return []
    
    def get_player_team(self, player_name: str, game: Dict[str, Any]) -> str:
        """Determine player's team (simplified)"""
        # This would need a more sophisticated player-team mapping
        # For now, return home team as default
        return game.get("home_team", "Unknown")
    
    async def enhance_with_ai_insights(self, session: aiohttp.ClientSession, 
                                     game_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use AI to generate insights about games and players"""
        if not self.use_ai:
            return []
        
        insights = []
        
        try:
            # Generate injury analysis
            if hasattr(self, 'openai_client') and self.check_rate_limit("openai", self.openai_limit):
                injury_insights = await self.get_injury_analysis(game_data)
                insights.extend(injury_insights)
            
            # Generate lineup predictions
            if hasattr(self, 'claude_client') and self.check_rate_limit("claude", self.claude_limit):
                lineup_insights = await self.get_lineup_predictions(game_data)
                insights.extend(lineup_insights)
            
            self.performance_stats["ai_enhancements"] += len(insights)
            
        except Exception as e:
            self.logger.error(f"Error generating AI insights: {e}")
        
        return insights
    
    async def get_injury_analysis(self, game_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use OpenAI to analyze injury impact"""
        try:
            prompt = f"""
            Analyze the injury impact for NBA game: {game_data.get('home_team')} vs {game_data.get('away_team')}
            
            Consider:
            1. Key player injuries and their impact on team performance
            2. Rest advantages (back-to-back games, travel)
            3. Lineup changes and their effect on prop betting lines
            4. Historical performance with similar circumstances
            
            Provide a concise analysis focusing on prop betting implications.
            Format as JSON with confidence score (0-1) and impact score (0-1).
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            insight_text = response.choices[0].message.content
            
            return [{
                "game_id": game_data.get("game_id", ""),
                "insight_type": "injury_analysis",
                "ai_model": "gpt-3.5-turbo",
                "insight_text": insight_text,
                "confidence_score": 0.8,  # Default for GPT analysis
                "impact_score": 0.7
            }]
        
        except Exception as e:
            self.logger.error(f"Error in injury analysis: {e}")
            return []
    
    async def get_lineup_predictions(self, game_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use Claude to predict optimal lineups"""
        try:
            prompt = f"""
            Predict starting lineups and rotation changes for:
            {game_data.get('home_team')} vs {game_data.get('away_team')}
            
            Focus on:
            1. Likely starters and their minutes projections
            2. Bench rotation impact
            3. Matchup advantages/disadvantages
            4. Coaching tendencies in similar situations
            
            Highlight players with prop betting value opportunities.
            """
            
            message = self.claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )
            
            insight_text = message.content[0].text
            
            return [{
                "game_id": game_data.get("game_id", ""),
                "insight_type": "lineup_prediction",
                "ai_model": "claude-3-haiku",
                "insight_text": insight_text,
                "confidence_score": 0.75,
                "impact_score": 0.8
            }]
        
        except Exception as e:
            self.logger.error(f"Error in lineup prediction: {e}")
            return []
    
    # NEW NBA API COLLECTION METHODS
    async def collect_nba_api_data(self) -> List[Dict[str, Any]]:
        """Collect data from official NBA API"""
        if not NBA_API_AVAILABLE:
            self.logger.warning("NBA API not available")
            return []
        
        try:
            data_collected = []
            
            # Get today's games
            scoreboard = scoreboardv2.ScoreboardV2()
            games_data = scoreboard.get_data_frames()[0]
            
            if not games_data.empty:
                for _, game in games_data.head(10).iterrows():
                    game_data = {
                        "source": "nba_api",
                        "game_id": f"nba_api_{game.get('GAME_ID', '')}",
                        "home_team": game.get("HOME_TEAM_NAME", ""),
                        "away_team": game.get("VISITOR_TEAM_NAME", ""),
                        "home_score": game.get("HOME_TEAM_PTS", 0),
                        "away_score": game.get("PTS_AWAY", 0),
                        "game_status": game.get("GAME_STATUS_TEXT", ""),
                        "game_time": game.get("GAME_DATE_EST", ""),
                        "collection_time": datetime.now().isoformat()
                    }
                    data_collected.append(game_data)
            
            self.logger.info(f"NBA API: Collected {len(data_collected)} games")
            return data_collected
            
        except Exception as e:
            self.logger.error(f"Error collecting NBA API data: {e}")
            return []
    
    async def collect_balldontlie_data(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Collect data from Ball Don't Lie API"""
        try:
            url = "https://www.balldontlie.io/api/v1/games"
            params = {
                'seasons[]': 2024,
                'per_page': 25,
                'start_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            async with session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    games = data.get('data', [])
                    
                    data_collected = []
                    for game in games:
                        game_data = {
                            "source": "balldontlie",
                            "game_id": f"bdl_{game.get('id', '')}",
                            "home_team": game.get("home_team", {}).get("full_name", ""),
                            "away_team": game.get("visitor_team", {}).get("full_name", ""),
                            "home_score": game.get("home_team_score", 0),
                            "away_score": game.get("visitor_team_score", 0),
                            "status": game.get("status", ""),
                            "date": game.get("date", ""),
                            "collection_time": datetime.now().isoformat()
                        }
                        data_collected.append(game_data)
                    
                    self.logger.info(f"Ball Don't Lie: Collected {len(data_collected)} games")
                    return data_collected
                else:
                    self.logger.warning(f"Ball Don't Lie API returned status {response.status}")
                    return []
        
        except Exception as e:
            self.logger.error(f"Error collecting Ball Don't Lie data: {e}")
            return []
    
    async def collect_espn_data(self, session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
        """Collect data from ESPN unofficial API"""
        try:
            url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
            
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    events = data.get('events', [])
                    
                    data_collected = []
                    for event in events:
                        competitors = event.get('competitions', [{}])[0].get('competitors', [])
                        
                        home_team = ""
                        away_team = ""
                        home_score = 0
                        away_score = 0
                        
                        for competitor in competitors:
                            team_name = competitor.get('team', {}).get('displayName', '')
                            score = competitor.get('score', 0)
                            
                            if competitor.get('homeAway') == 'home':
                                home_team = team_name
                                home_score = score
                            else:
                                away_team = team_name
                                away_score = score
                        
                        game_data = {
                            "source": "espn",
                            "game_id": f"espn_{event.get('id', '')}",
                            "home_team": home_team,
                            "away_team": away_team,
                            "home_score": home_score,
                            "away_score": away_score,
                            "status": event.get('status', {}).get('type', {}).get('name', ''),
                            "date": event.get('date', ''),
                            "collection_time": datetime.now().isoformat()
                        }
                        data_collected.append(game_data)
                    
                    self.logger.info(f"ESPN: Collected {len(data_collected)} games")
                    return data_collected
                else:
                    self.logger.warning(f"ESPN API returned status {response.status}")
                    return []
        
        except Exception as e:
            self.logger.error(f"Error collecting ESPN data: {e}")
            return []
    
    async def collect_all_free_sources(self, session: aiohttp.ClientSession) -> Dict[str, List[Dict[str, Any]]]:
        """Collect data from all free NBA sources with intelligent failover"""
        self.logger.info("Collecting from all free NBA data sources...")
        
        # First, check API health to prioritize working APIs
        health_status = await self.check_api_health(session)
        
        # Get APIs in priority order (healthiest first)
        api_sources = self.get_api_priority_order(health_status)
        
        results = {}
        working_apis = []
        failed_apis = []
        target_records = 8  # Minimum records needed
        
        self.logger.info("API Health Status:")
        for api_name, health in health_status.items():
            status_emoji = {"healthy": "", "degraded": "", "failed": ""}.get(health.get("status"), "")
            self.logger.info(f"  {status_emoji} {api_name}: {health.get('status', 'unknown')} ({health.get('response_time', 0):.2f}s)")
        
        # Try each API in priority order
        for source_name, collect_func, args in api_sources:
            try:
                self.logger.info(f"Attempting collection from {source_name} (priority API)...")
                
                # Skip if health check showed this API as failed
                if health_status.get(source_name, {}).get("status") == "failed":
                    self.logger.warning(f" Skipping {source_name} - health check failed")
                    failed_apis.append(source_name)
                    results[source_name] = []
                    continue
                
                # Add session parameter if needed
                if source_name in ["espn", "balldontlie"]:
                    data = await collect_func(session)
                else:
                    data = await collect_func()
                
                if data and len(data) > 0:
                    results[source_name] = data
                    working_apis.append(source_name)
                    self.logger.info(f" {source_name}: {len(data)} records collected")
                    
                    # If we have enough data from prioritized APIs, we can stop early
                    total_so_far = sum(len(results[api]) for api in working_apis)
                    if total_so_far >= target_records:
                        self.logger.info(f" Target records ({target_records}) achieved, stopping early collection")
                        # Still initialize remaining APIs with empty results
                        for remaining_name, _, _ in api_sources:
                            if remaining_name not in results:
                                results[remaining_name] = []
                        break
                else:
                    failed_apis.append(source_name)
                    results[source_name] = []
                    self.logger.warning(f" {source_name}: No data returned")
                    
            except Exception as e:
                failed_apis.append(source_name)
                results[source_name] = []
                self.logger.error(f" {source_name} failed: {e}")
        
        # Failover logic: if we still don't have enough data, try degraded APIs
        total_collected = sum(len(data) for data in results.values())
        
        if total_collected < target_records:
            self.logger.warning(f"Only {total_collected}/{target_records} records collected, trying degraded APIs...")
            
            # Try degraded APIs that we might have skipped
            for api_name, health in health_status.items():
                if health.get("status") == "degraded" and api_name not in working_apis:
                    try:
                        self.logger.info(f" Attempting degraded API: {api_name}")
                        
                        if api_name == "nba_api":
                            backup_data = await self.collect_nba_api_data()
                        elif api_name == "espn":
                            backup_data = await self.collect_espn_data(session)
                        elif api_name == "balldontlie":
                            backup_data = await self.collect_balldontlie_data(session)
                        else:
                            continue
                        
                        if backup_data:
                            results[api_name] = backup_data
                            working_apis.append(api_name)
                            self.logger.info(f" {api_name} degraded recovery: {len(backup_data)} records")
                            
                    except Exception as e:
                        self.logger.warning(f"Degraded API {api_name} also failed: {e}")
        
        # Log final status with intelligent summary
        total_collected = sum(len(data) for data in results.values())
        working_count = len(working_apis)
        total_apis = len(health_status)
        
        self.logger.info(f" Free sources collection complete:")
        self.logger.info(f"   Total records: {total_collected}")
        self.logger.info(f"   Working APIs: {working_count}/{total_apis} ({', '.join(working_apis)})")
        
        if failed_apis:
            self.logger.warning(f"   Failed APIs: {', '.join(failed_apis)}")
        
        # Success rate assessment
        if total_collected >= target_records:
            self.logger.info(f" Collection successful: {total_collected}/{target_records} records")
        else:
            self.logger.error(f" Collection below target: {total_collected}/{target_records} records")
        
        return results

    async def save_free_sources_data(self, free_sources_data: Dict[str, List[Dict[str, Any]]]):
        """Save free sources data to enrichment database"""
        try:
            enrichment_db = self.data_dir / "nba_enrichment.db"
            
            with sqlite3.connect(enrichment_db) as conn:
                # Create table if not exists
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS free_sources_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source TEXT,
                        game_id TEXT,
                        home_team TEXT,
                        away_team TEXT,
                        home_score INTEGER,
                        away_score INTEGER,
                        status TEXT,
                        game_time TEXT,
                        collection_time TEXT,
                        raw_data TEXT
                    )
                """)
                
                # Save data from each source
                for source_name, games_data in free_sources_data.items():
                    for game_data in games_data:
                        conn.execute("""
                            INSERT INTO free_sources_data
                            (source, game_id, home_team, away_team, home_score,
                             away_score, status, game_time, collection_time, raw_data)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            game_data.get("source", source_name),
                            game_data.get("game_id", ""),
                            game_data.get("home_team", ""),
                            game_data.get("away_team", ""),
                            game_data.get("home_score", 0),
                            game_data.get("away_score", 0),
                            game_data.get("status", ""),
                            game_data.get("game_time", ""),
                            game_data.get("collection_time", ""),
                            json.dumps(game_data)
                        ))
                
                conn.commit()
                
            total_saved = sum(len(data) for data in free_sources_data.values())
            self.logger.info(f"Saved {total_saved} records from free NBA sources")
        
        except Exception as e:
            self.logger.error(f"Error saving free sources data: {e}")

    def save_data_to_databases(self, odds_data: List[Dict], props_data: List[Dict], 
                              insights_data: List[Dict]):
        """Save collected data to databases"""
        try:
            # Save odds
            if odds_data:
                with sqlite3.connect(self.odds_db) as conn:
                    for odds in odds_data:
                        conn.execute("""
                            INSERT OR IGNORE INTO odds 
                            (game_id, home_team, away_team, commence_time, home_odds, away_odds,
                             home_spread, away_spread, total_over, total_under, total_points, bookmaker)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            odds["game_id"], odds["home_team"], odds["away_team"],
                            odds["commence_time"], odds["home_odds"], odds["away_odds"],
                            odds["home_spread"], odds["away_spread"], odds["total_over"],
                            odds["total_under"], odds["total_points"], odds["bookmaker"]
                        ))
                    conn.commit()
                self.logger.info(f"Saved {len(odds_data)} odds records")
            
            # Save props
            if props_data:
                with sqlite3.connect(self.props_db) as conn:
                    for prop in props_data:
                        conn.execute("""
                            INSERT OR IGNORE INTO player_props
                            (game_id, player_name, team, prop_type, line, over_odds, 
                             under_odds, bookmaker, game_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            prop["game_id"], prop["player_name"], prop["team"],
                            prop["prop_type"], prop["line"], prop["over_odds"],
                            prop["under_odds"], prop["bookmaker"], prop["game_date"]
                        ))
                    conn.commit()
                self.logger.info(f"Saved {len(props_data)} props records")
            
            # Save AI insights
            if insights_data:
                with sqlite3.connect(self.ai_insights_db) as conn:
                    for insight in insights_data:
                        conn.execute("""
                            INSERT INTO ai_insights
                            (game_id, player_name, insight_type, ai_model, insight_text,
                             confidence_score, impact_score)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            insight["game_id"], insight.get("player_name"),
                            insight["insight_type"], insight["ai_model"],
                            insight["insight_text"], insight["confidence_score"],
                            insight["impact_score"]
                        ))
                    conn.commit()
                self.logger.info(f"Saved {len(insights_data)} AI insights")
        
        except Exception as e:
            self.logger.error(f"Error saving data to databases: {e}")
            raise
    
    async def run_production_collection(self) -> Dict[str, Any]:
        """Run complete production data collection with enhanced free APIs"""
        self.logger.info("Starting NBA production data collection...")
        start_time = datetime.now()
        
        all_odds = []
        all_props = []
        all_insights = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Collect from original Odds API
                odds_data = await self.collect_nba_odds(session)
                all_odds.extend(odds_data)
                
                # Collect props
                props_data = await self.collect_player_props(session)
                all_props.extend(props_data)
                
                # NEW: Collect from free NBA data sources
                free_sources_data = await self.collect_all_free_sources(session)
                
                # Save free sources data to a new table for enrichment
                await self.save_free_sources_data(free_sources_data)
                
                # Generate AI insights for each game
                if self.use_ai and odds_data:
                    game_ids = list(set(odds['game_id'] for odds in odds_data))
                    
                    for game_id in game_ids[:5]:  # Limit to first 5 games for AI analysis
                        game_data = next(odds for odds in odds_data if odds['game_id'] == game_id)
                        insights = await self.enhance_with_ai_insights(session, game_data)
                        all_insights.extend(insights)
            
            # Save all data
            self.save_data_to_databases(all_odds, all_props, all_insights)
            
            # Export for TPU processing
            self.export_for_tpu_processing(all_odds, all_props)
            
            # Update performance stats
            end_time = datetime.now()
            collection_duration = (end_time - start_time).total_seconds()
            
            self.performance_stats.update({
                "collection_duration": collection_duration,
                "odds_collected": len(all_odds),
                "props_collected": len(all_props),
                "insights_generated": len(all_insights),
                "end_time": end_time
            })
            
            # Save performance stats
            self.save_performance_stats()
            
            summary = {
                "success": True,
                "odds_collected": len(all_odds),
                "props_collected": len(all_props),
                "ai_insights": len(all_insights),
                "duration_seconds": collection_duration,
                "api_calls_made": self.performance_stats["api_calls"],
                "errors": self.performance_stats["errors"]
            }
            
            self.logger.info(f"Production collection completed: {summary}")
            return summary
        
        except Exception as e:
            self.logger.error(f"Error in production collection: {e}")
            self.performance_stats["errors"] += 1
            return {
                "success": False,
                "error": str(e),
                "partial_data": {
                    "odds": len(all_odds),
                    "props": len(all_props),
                    "insights": len(all_insights)
                }
            }
    
    def export_for_tpu_processing(self, odds_data: List[Dict], props_data: List[Dict]):
        """Export data in format optimized for TPU processing"""
        try:
            export_data = {
                "collection_time": datetime.now().isoformat(),
                "odds": odds_data,
                "props": props_data,
                "metadata": {
                    "total_games": len(set(odds['game_id'] for odds in odds_data)),
                    "total_props": len(props_data),
                    "focus_teams": self.focus_teams,
                    "prop_types": self.prop_types
                }
            }
            
            # Save as JSON for TPU processing
            export_file = self.data_dir / f"tpu_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            # Create symlink for latest export
            latest_link = self.data_dir / "latest_tpu_export.json"
            if latest_link.exists():
                latest_link.unlink()
            
            try:
                latest_link.symlink_to(export_file.name)
            except OSError:
                # Symlink failed, copy instead
                import shutil
                shutil.copy2(export_file, latest_link)
            
            self.logger.info(f"TPU export saved: {export_file}")
        
        except Exception as e:
            self.logger.error(f"Error exporting for TPU: {e}")
    
    def save_performance_stats(self):
        """Save performance statistics"""
        try:
            with open(self.perf_log, 'w') as f:
                json.dump(self.performance_stats, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving performance stats: {e}")


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EQ12 NBA Production Data Collector")
    parser.add_argument("--workspace", type=str, default="C:/EQ12",
                       help="EQ12 workspace directory")
    parser.add_argument("--no-ai", action="store_true",
                       help="Disable AI enhancement features")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--test-mode", action="store_true",
                       help="Run in test mode (limited API calls)")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        collector = NBAProductionCollector(
            workspace_dir=args.workspace,
            use_ai=not args.no_ai
        )
        
        if args.test_mode:
            collector.odds_api_limit = 5  # Limit for testing
            collector.openai_limit = 2
            collector.claude_limit = 1
        
        result = await collector.run_production_collection()
        
        if result["success"]:
            print(f" NBA data collection completed successfully!")
            print(f" Odds collected: {result['odds_collected']}")
            print(f" Props collected: {result['props_collected']}")
            print(f" AI insights: {result['ai_insights']}")
            print(f" Duration: {result['duration_seconds']:.1f} seconds")
            return 0
        else:
            print(f" Collection failed: {result['error']}")
            return 1
    
    except Exception as e:
        print(f" Fatal error: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))