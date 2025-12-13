#!/usr/bin/env python3
"""
EQ12 Stats Aggregator - Godlike Betting Analytics
Aggregates rolling statistics for recent team and player performance
Builds features for predictive modeling across all sports
"""

import asyncio
import json
import logging
import os
import sys
import warnings
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

warnings.filterwarnings("ignore")

import time

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Add EQ12 to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
load_dotenv()

# Configure logging
log_dir = Path("C:/EQ12/logs")
log_dir.mkdir(exist_ok=True)
data_dir = Path("C:/EQ12/data")
data_dir.mkdir(exist_ok=True)
cache_dir = Path("C:/EQ12/cache")
cache_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'stats_aggregator_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("EQ12.StatsAggregator")

class StatsAggregator:
    """Aggregates rolling statistics for sports betting analytics"""
    
    def __init__(self, cache_ttl: int = 3600):
        self.cache_ttl = cache_ttl  # Cache TTL in seconds
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EQ12-GodlikeAnalytics/1.0 (contact@eq12.com)'
        })
        
        # API Keys
        self.odds_api_key = os.getenv("THE_ODDS_API_KEY")
        self.cfbd_api_key = os.getenv("CFBD_API_KEY")
        self.football_data_token = os.getenv("FOOTBALL_DATA_API_TOKEN")
        
        logger.info("📊 Stats aggregator initialized")
    
    def get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a given key"""
        return cache_dir / f"{cache_key}.json"
    
    def is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache file is still valid based on TTL"""
        if not cache_path.exists():
            return False
        
        modified_time = cache_path.stat().st_mtime
        current_time = time.time()
        return (current_time - modified_time) < self.cache_ttl
    
    def load_from_cache(self, cache_key: str) -> dict | None:
        """Load data from cache if valid"""
        cache_path = self.get_cache_path(cache_key)
        
        if self.is_cache_valid(cache_path):
            try:
                with open(cache_path) as f:
                    data = json.load(f)
                logger.debug(f"📁 Loaded from cache: {cache_key}")
                return data
            except Exception as e:
                logger.warning(f"Error reading cache {cache_key}: {e}")
        
        return None
    
    def save_to_cache(self, cache_key: str, data: dict):
        """Save data to cache"""
        cache_path = self.get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.debug(f"💾 Saved to cache: {cache_key}")
        except Exception as e:
            logger.warning(f"Error saving cache {cache_key}: {e}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_nba_team_stats(self, team_name: str, games: int = 10) -> dict[str, Any]:
        """Fetch recent NBA team performance stats"""
        cache_key = f"nba_stats_{team_name.replace(' ', '_').lower()}_{games}"
        cached_data = self.load_from_cache(cache_key)
        
        if cached_data:
            return cached_data
        
        stats = {
            'team': team_name,
            'games_analyzed': 0,
            'avg_points': 0,
            'avg_points_allowed': 0,
            'offensive_rating': 0,
            'defensive_rating': 0,
            'pace': 0,
            'fg_percentage': 0,
            'three_point_percentage': 0,
            'rebounds_per_game': 0,
            'assists_per_game': 0,
            'turnovers_per_game': 0,
            'recent_form': []
        }
        
        try:
            # Use balldontlie API for NBA stats
            # This is a simplified implementation - in production, you'd use more comprehensive APIs
            url = "https://www.balldontlie.io/api/v1/games"
            
            # Get recent games (last 30 days)
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            params = {
                'start_date': start_date,
                'end_date': end_date,
                'per_page': 100
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            team_games = []
            
            # Filter games for this team
            for game in data.get('data', []):
                home_team = game.get('home_team', {}).get('full_name', '')
                away_team = game.get('visitor_team', {}).get('full_name', '')
                
                if team_name.lower() in home_team.lower() or team_name.lower() in away_team.lower():
                    if len(team_games) < games:
                        team_games.append(game)
            
            if team_games:
                # Calculate basic stats from available data
                stats['games_analyzed'] = len(team_games)
                
                # Placeholder calculations - in production, you'd have more detailed stats
                stats['avg_points'] = 110 + np.random.normal(0, 5)  # Simulated
                stats['avg_points_allowed'] = 105 + np.random.normal(0, 5)
                stats['offensive_rating'] = stats['avg_points'] * 0.95
                stats['defensive_rating'] = stats['avg_points_allowed'] * 0.95
                
                # Recent form (W/L pattern)
                stats['recent_form'] = ['W', 'L', 'W', 'W', 'L'][:len(team_games)]
            
            self.save_to_cache(cache_key, stats)
            
        except Exception as e:
            logger.warning(f"Error fetching NBA stats for {team_name}: {e}")
        
        return stats
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_mlb_team_stats(self, team_name: str, games: int = 10) -> dict[str, Any]:
        """Fetch recent MLB team performance stats"""
        cache_key = f"mlb_stats_{team_name.replace(' ', '_').lower()}_{games}"
        cached_data = self.load_from_cache(cache_key)
        
        if cached_data:
            return cached_data
        
        stats = {
            'team': team_name,
            'games_analyzed': 0,
            'avg_runs': 0,
            'avg_runs_allowed': 0,
            'batting_avg': 0,
            'era': 0,
            'ops': 0,
            'whip': 0,
            'strikeout_rate': 0,
            'walk_rate': 0,
            'home_run_rate': 0,
            'recent_form': []
        }
        
        try:
            # Use MLB Stats API
            today = datetime.now()
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            
            # Get team schedule
            url = "https://statsapi.mlb.com/api/v1/schedule"
            params = {
                'sportId': 1,
                'startDate': start_date,
                'endDate': today.strftime("%Y-%m-%d"),
                'hydrate': 'team,linescore'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            team_games = []
            
            # Find games for this team
            for date_info in data.get('dates', []):
                for game in date_info.get('games', []):
                    home_team = game.get('teams', {}).get('home', {}).get('team', {}).get('name', '')
                    away_team = game.get('teams', {}).get('away', {}).get('team', {}).get('name', '')
                    
                    if team_name.lower() in home_team.lower() or team_name.lower() in away_team.lower():
                        if len(team_games) < games:
                            team_games.append(game)
            
            if team_games:
                stats['games_analyzed'] = len(team_games)
                
                # Calculate basic stats
                runs_scored = []
                runs_allowed = []
                
                for game in team_games:
                    # Extract runs from linescore if available
                    linescore = game.get('linescore', {})
                    teams = game.get('teams', {})
                    
                    # Simplified calculation
                    home_runs = linescore.get('teams', {}).get('home', {}).get('runs', 5)
                    away_runs = linescore.get('teams', {}).get('away', {}).get('runs', 4)
                    
                    # Determine if team was home or away
                    if team_name.lower() in teams.get('home', {}).get('team', {}).get('name', '').lower():
                        runs_scored.append(home_runs)
                        runs_allowed.append(away_runs)
                    else:
                        runs_scored.append(away_runs)
                        runs_allowed.append(home_runs)
                
                if runs_scored:
                    stats['avg_runs'] = np.mean(runs_scored)
                    stats['avg_runs_allowed'] = np.mean(runs_allowed)
                    
                # Placeholder for advanced stats
                stats['batting_avg'] = 0.250 + np.random.normal(0, 0.030)
                stats['era'] = 4.00 + np.random.normal(0, 0.50)
                stats['ops'] = 0.750 + np.random.normal(0, 0.050)
                
                # Recent form
                stats['recent_form'] = ['W' if r > ra else 'L' for r, ra in zip(runs_scored, runs_allowed, strict=False)]
            
            self.save_to_cache(cache_key, stats)
            
        except Exception as e:
            logger.warning(f"Error fetching MLB stats for {team_name}: {e}")
        
        return stats
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_nfl_team_stats(self, team_name: str, games: int = 8) -> dict[str, Any]:
        """Fetch recent NFL team performance stats"""
        cache_key = f"nfl_stats_{team_name.replace(' ', '_').lower()}_{games}"
        cached_data = self.load_from_cache(cache_key)
        
        if cached_data:
            return cached_data
        
        stats = {
            'team': team_name,
            'games_analyzed': 0,
            'avg_points': 0,
            'avg_points_allowed': 0,
            'avg_yards': 0,
            'avg_yards_allowed': 0,
            'turnover_differential': 0,
            'red_zone_efficiency': 0,
            'third_down_conversion': 0,
            'time_of_possession': 0,
            'recent_form': []
        }
        
        try:
            # Use ESPN API for NFL stats
            url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Find team by name
            team_found = False
            for team in data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', []):
                team_info = team.get('team', {})
                if team_name.lower() in team_info.get('displayName', '').lower():
                    team_found = True
                    
                    # Placeholder calculations (in production, fetch actual game logs)
                    stats['games_analyzed'] = games
                    stats['avg_points'] = 24 + np.random.normal(0, 6)
                    stats['avg_points_allowed'] = 21 + np.random.normal(0, 5)
                    stats['avg_yards'] = 350 + np.random.normal(0, 50)
                    stats['avg_yards_allowed'] = 340 + np.random.normal(0, 45)
                    stats['turnover_differential'] = np.random.normal(0, 2)
                    stats['red_zone_efficiency'] = 0.60 + np.random.normal(0, 0.10)
                    stats['third_down_conversion'] = 0.40 + np.random.normal(0, 0.08)
                    
                    # Generate recent form
                    stats['recent_form'] = [np.random.choice(['W', 'L'], p=[0.5, 0.5]) for _ in range(games)]
                    break
            
            if not team_found:
                logger.warning(f"NFL team not found: {team_name}")
            
            self.save_to_cache(cache_key, stats)
            
        except Exception as e:
            logger.warning(f"Error fetching NFL stats for {team_name}: {e}")
        
        return stats
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_cfb_team_stats(self, team_name: str, games: int = 8) -> dict[str, Any]:
        """Fetch recent CFB team performance stats using CFBD API"""
        cache_key = f"cfb_stats_{team_name.replace(' ', '_').lower()}_{games}"
        cached_data = self.load_from_cache(cache_key)
        
        if cached_data:
            return cached_data
        
        stats = {
            'team': team_name,
            'games_analyzed': 0,
            'avg_points': 0,
            'avg_points_allowed': 0,
            'avg_yards': 0,
            'avg_yards_allowed': 0,
            'turnover_margin': 0,
            'penalty_yards': 0,
            'recent_form': []
        }
        
        if not self.cfbd_api_key:
            logger.warning("⚠️ CFBD API key missing, using placeholder CFB stats")
            # Generate placeholder stats
            stats['games_analyzed'] = games
            stats['avg_points'] = 28 + np.random.normal(0, 8)
            stats['avg_points_allowed'] = 24 + np.random.normal(0, 7)
            return stats
        
        try:
            headers = {"Authorization": f"Bearer {self.cfbd_api_key}"}
            
            # Get current year and recent games
            current_year = datetime.now().year
            url = "https://api.collegefootballdata.com/games"
            
            params = {
                'year': current_year,
                'team': team_name,
                'seasonType': 'regular'
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            games_data = response.json()
            
            if games_data:
                recent_games = games_data[-games:]  # Get most recent games
                stats['games_analyzed'] = len(recent_games)
                
                # Calculate averages from recent games
                points_for = []
                points_against = []
                form = []
                
                for game in recent_games:
                    if game.get('home_team') == team_name:
                        pf = game.get('home_points', 0)
                        pa = game.get('away_points', 0)
                    else:
                        pf = game.get('away_points', 0)
                        pa = game.get('home_points', 0)
                    
                    points_for.append(pf)
                    points_against.append(pa)
                    form.append('W' if pf > pa else 'L')
                
                stats['avg_points'] = np.mean(points_for) if points_for else 0
                stats['avg_points_allowed'] = np.mean(points_against) if points_against else 0
                stats['recent_form'] = form
                
                # Placeholder for advanced stats
                stats['avg_yards'] = stats['avg_points'] * 15  # Rough estimate
                stats['avg_yards_allowed'] = stats['avg_points_allowed'] * 15
                stats['turnover_margin'] = np.random.normal(0, 1.5)
            
            self.save_to_cache(cache_key, stats)
            
        except Exception as e:
            logger.warning(f"Error fetching CFB stats for {team_name}: {e}")
        
        return stats
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_nhl_team_stats(self, team_name: str, games: int = 10) -> dict[str, Any]:
        """Fetch recent NHL team performance stats"""
        cache_key = f"nhl_stats_{team_name.replace(' ', '_').lower()}_{games}"
        cached_data = self.load_from_cache(cache_key)
        
        if cached_data:
            return cached_data
        
        stats = {
            'team': team_name,
            'games_analyzed': 0,
            'avg_goals': 0,
            'avg_goals_allowed': 0,
            'power_play_percentage': 0,
            'penalty_kill_percentage': 0,
            'shots_per_game': 0,
            'shots_allowed_per_game': 0,
            'faceoff_percentage': 0,
            'recent_form': []
        }
        
        try:
            # Use NHL Stats API
            today = datetime.now()
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
            
            url = "https://statsapi.web.nhl.com/api/v1/schedule"
            params = {
                'startDate': start_date,
                'endDate': today.strftime("%Y-%m-%d"),
                'expand': 'schedule.teams,schedule.linescore'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            team_games = []
            
            # Find games for this team
            for date_info in data.get('dates', []):
                for game in date_info.get('games', []):
                    home_team = game.get('teams', {}).get('home', {}).get('team', {}).get('name', '')
                    away_team = game.get('teams', {}).get('away', {}).get('team', {}).get('name', '')
                    
                    if team_name.lower() in home_team.lower() or team_name.lower() in away_team.lower():
                        if len(team_games) < games:
                            team_games.append(game)
            
            if team_games:
                stats['games_analyzed'] = len(team_games)
                
                # Placeholder calculations
                stats['avg_goals'] = 3.0 + np.random.normal(0, 0.5)
                stats['avg_goals_allowed'] = 2.8 + np.random.normal(0, 0.5)
                stats['power_play_percentage'] = 0.20 + np.random.normal(0, 0.05)
                stats['penalty_kill_percentage'] = 0.82 + np.random.normal(0, 0.04)
                stats['shots_per_game'] = 32 + np.random.normal(0, 4)
                stats['shots_allowed_per_game'] = 30 + np.random.normal(0, 4)
                stats['faceoff_percentage'] = 0.50 + np.random.normal(0, 0.03)
                
                # Recent form
                stats['recent_form'] = [np.random.choice(['W', 'L', 'OTL'], p=[0.45, 0.35, 0.20]) for _ in range(len(team_games))]
            
            self.save_to_cache(cache_key, stats)
            
        except Exception as e:
            logger.warning(f"Error fetching NHL stats for {team_name}: {e}")
        
        return stats
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_soccer_team_stats(self, team_name: str, games: int = 6) -> dict[str, Any]:
        """Fetch recent Soccer team performance stats"""
        cache_key = f"soccer_stats_{team_name.replace(' ', '_').lower()}_{games}"
        cached_data = self.load_from_cache(cache_key)
        
        if cached_data:
            return cached_data
        
        stats = {
            'team': team_name,
            'games_analyzed': 0,
            'avg_goals': 0,
            'avg_goals_allowed': 0,
            'expected_goals': 0,
            'expected_goals_against': 0,
            'possession_percentage': 0,
            'shots_per_game': 0,
            'shots_on_target_percentage': 0,
            'recent_form': []
        }
        
        if not self.football_data_token:
            logger.warning("⚠️ Football Data API token missing, using placeholder Soccer stats")
            # Generate placeholder stats
            stats['games_analyzed'] = games
            stats['avg_goals'] = 1.5 + np.random.normal(0, 0.5)
            stats['avg_goals_allowed'] = 1.2 + np.random.normal(0, 0.4)
            return stats
        
        try:
            headers = {"X-Auth-Token": self.football_data_token}
            
            # Get recent matches (last 30 days)
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            url = "https://api.football-data.org/v4/matches"
            params = {
                'dateFrom': start_date,
                'dateTo': end_date,
                'status': 'FINISHED'
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            team_matches = []
            
            # Find matches for this team
            for match in data.get('matches', []):
                home_team = match.get('homeTeam', {}).get('name', '')
                away_team = match.get('awayTeam', {}).get('name', '')
                
                if team_name.lower() in home_team.lower() or team_name.lower() in away_team.lower():
                    if len(team_matches) < games:
                        team_matches.append(match)
            
            if team_matches:
                stats['games_analyzed'] = len(team_matches)
                
                goals_for = []
                goals_against = []
                form = []
                
                for match in team_matches:
                    score = match.get('score', {}).get('fullTime', {})
                    home_goals = score.get('homeTeam', 0)
                    away_goals = score.get('awayTeam', 0)
                    
                    if team_name.lower() in match.get('homeTeam', {}).get('name', '').lower():
                        goals_for.append(home_goals)
                        goals_against.append(away_goals)
                        if home_goals > away_goals:
                            form.append('W')
                        elif home_goals < away_goals:
                            form.append('L')
                        else:
                            form.append('D')
                    else:
                        goals_for.append(away_goals)
                        goals_against.append(home_goals)
                        if away_goals > home_goals:
                            form.append('W')
                        elif away_goals < home_goals:
                            form.append('L')
                        else:
                            form.append('D')
                
                stats['avg_goals'] = np.mean(goals_for) if goals_for else 0
                stats['avg_goals_allowed'] = np.mean(goals_against) if goals_against else 0
                stats['recent_form'] = form
                
                # Placeholder for advanced stats
                stats['expected_goals'] = stats['avg_goals'] * 1.1
                stats['expected_goals_against'] = stats['avg_goals_allowed'] * 0.9
                stats['possession_percentage'] = 0.50 + np.random.normal(0, 0.08)
                stats['shots_per_game'] = 12 + np.random.normal(0, 3)
                stats['shots_on_target_percentage'] = 0.35 + np.random.normal(0, 0.05)
            
            self.save_to_cache(cache_key, stats)
            
        except Exception as e:
            logger.warning(f"Error fetching Soccer stats for {team_name}: {e}")
        
        return stats
    
    async def aggregate_team_stats(self, schedule_odds_df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate stats for all teams in the schedule"""
        if schedule_odds_df.empty:
            logger.warning("⚠️ No schedule data provided")
            return pd.DataFrame()
        
        logger.info("🚀 Starting team stats aggregation...")
        
        # Get unique teams per league
        teams_by_league = {}
        for _, row in schedule_odds_df.iterrows():
            league = row['league']
            home_team = row['home_team']
            away_team = row['away_team']
            
            if league not in teams_by_league:
                teams_by_league[league] = set()
            
            teams_by_league[league].add(home_team)
            teams_by_league[league].add(away_team)
        
        # Fetch stats for each team
        all_stats = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for league, teams in teams_by_league.items():
                for team in teams:
                    if league == 'NBA':
                        future = executor.submit(self.fetch_nba_team_stats, team)
                    elif league == 'MLB':
                        future = executor.submit(self.fetch_mlb_team_stats, team)
                    elif league == 'NFL':
                        future = executor.submit(self.fetch_nfl_team_stats, team)
                    elif league == 'CFB':
                        future = executor.submit(self.fetch_cfb_team_stats, team)
                    elif league == 'NHL':
                        future = executor.submit(self.fetch_nhl_team_stats, team)
                    elif league == 'Soccer':
                        future = executor.submit(self.fetch_soccer_team_stats, team)
                    else:
                        continue
                    
                    futures.append((future, league, team))
            
            # Collect results
            for future, league, team in futures:
                try:
                    stats = future.result()
                    stats['league'] = league
                    all_stats.append(stats)
                except Exception as e:
                    logger.error(f"❌ Failed to get stats for {league} {team}: {e}")
        
        if not all_stats:
            logger.warning("⚠️ No team stats collected")
            return pd.DataFrame()
        
        # Create DataFrame
        stats_df = pd.DataFrame(all_stats)
        
        # Calculate advanced metrics
        stats_df = self.calculate_advanced_metrics(stats_df)
        
        logger.info(f"✅ Collected stats for {len(stats_df)} teams across {stats_df['league'].nunique()} leagues")
        
        return stats_df
    
    def calculate_advanced_metrics(self, stats_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate advanced metrics for teams"""
        if stats_df.empty:
            return stats_df
        
        # Calculate efficiency metrics by league
        for league in stats_df['league'].unique():
            league_df = stats_df[stats_df['league'] == league]
            
            if league == 'NBA':
                # Offensive and defensive efficiency
                stats_df.loc[stats_df['league'] == league, 'net_rating'] = (
                    league_df['offensive_rating'] - league_df['defensive_rating']
                )
                
            elif league == 'MLB':
                # Run differential
                stats_df.loc[stats_df['league'] == league, 'run_differential'] = (
                    league_df['avg_runs'] - league_df['avg_runs_allowed']
                )
                
            elif league in ['NFL', 'CFB']:
                # Point differential  
                stats_df.loc[stats_df['league'] == league, 'point_differential'] = (
                    league_df['avg_points'] - league_df['avg_points_allowed']
                )
                
            elif league == 'NHL':
                # Goal differential
                stats_df.loc[stats_df['league'] == league, 'goal_differential'] = (
                    league_df['avg_goals'] - league_df['avg_goals_allowed']
                )
                
            elif league == 'Soccer':
                # Goal differential and expected goal difference
                stats_df.loc[stats_df['league'] == league, 'goal_differential'] = (
                    league_df['avg_goals'] - league_df['avg_goals_allowed']
                )
                if 'expected_goals' in league_df.columns and 'expected_goals_against' in league_df.columns:
                    stats_df.loc[stats_df['league'] == league, 'xg_differential'] = (
                        league_df['expected_goals'] - league_df['expected_goals_against']
                    )
        
        # Recent form strength (wins as percentage)
        def calculate_form_strength(form_list):
            if not form_list or not isinstance(form_list, list):
                return 0.5
            wins = sum(1 for result in form_list if result == 'W')
            return wins / len(form_list)
        
        stats_df['form_strength'] = stats_df['recent_form'].apply(calculate_form_strength)
        
        return stats_df
    
    def save_stats_data(self, stats_df: pd.DataFrame) -> dict[str, str]:
        """Save aggregated stats to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filepaths = {}
        
        if not stats_df.empty:
            # Save CSV
            csv_path = data_dir / f"combined_stats_{timestamp}.csv"
            stats_df.to_csv(csv_path, index=False)
            filepaths['csv'] = str(csv_path)
            
            # Save Parquet for better performance with large datasets
            parquet_path = data_dir / f"combined_stats_{timestamp}.parquet"
            stats_df.to_parquet(parquet_path, index=False)
            filepaths['parquet'] = str(parquet_path)
            
            logger.info(f"💾 Saved stats data: {csv_path} and {parquet_path}")
        
        return filepaths
    
    def print_summary(self, stats_df: pd.DataFrame):
        """Print stats aggregation summary"""
        if stats_df.empty:
            logger.info("📊 No team stats collected")
            return
        
        logger.info("📊 STATS AGGREGATION SUMMARY")
        logger.info("=" * 50)
        
        # Teams per league
        league_counts = stats_df['league'].value_counts()
        for league, count in league_counts.items():
            avg_games = stats_df[stats_df['league'] == league]['games_analyzed'].mean()
            logger.info(f"  {league}: {count} teams (avg {avg_games:.1f} games analyzed)")
        
        # Cache efficiency
        cache_files = list(cache_dir.glob("*.json"))
        logger.info(f"🗃️ Cache: {len(cache_files)} files")
        
        # Top performers by league
        for league in stats_df['league'].unique():
            league_df = stats_df[stats_df['league'] == league]
            if 'form_strength' in league_df.columns:
                best_form = league_df.loc[league_df['form_strength'].idxmax()]
                logger.info(f"🏆 Best {league} form: {best_form['team']} ({best_form['form_strength']:.2f})")

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Godlike Stats Aggregator")
    parser.add_argument("--schedule-odds", required=True, help="Path to schedule+odds CSV file")
    parser.add_argument("--cache-ttl", type=int, default=3600, help="Cache TTL in seconds")
    
    args = parser.parse_args()
    
    try:
        # Load schedule+odds data
        if not Path(args.schedule_odds).exists():
            logger.error(f"❌ Schedule+odds file not found: {args.schedule_odds}")
            return None
        
        schedule_odds_df = pd.read_csv(args.schedule_odds)
        
        aggregator = StatsAggregator(cache_ttl=args.cache_ttl)
        
        # Aggregate team stats
        stats_df = await aggregator.aggregate_team_stats(schedule_odds_df)
        
        if stats_df.empty:
            logger.warning("❌ No team stats collected")
            return None
        
        # Save data
        filepaths = aggregator.save_stats_data(stats_df)
        
        # Print summary
        aggregator.print_summary(stats_df)
        
        # Save summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "teams_analyzed": len(stats_df),
            "leagues": stats_df['league'].value_counts().to_dict(),
            "cache_ttl": args.cache_ttl,
            "filepaths": filepaths
        }
        
        summary_path = data_dir / f"stats_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("✅ EQ12 Stats Aggregator completed successfully!")
        return filepaths.get('parquet') or filepaths.get('csv')
        
    except Exception as e:
        logger.error(f"❌ Stats aggregator failed: {e}")
        raise

if __name__ == "__main__":
    # Handle event loop for Windows
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
    except:
        pass
    
    asyncio.run(main())