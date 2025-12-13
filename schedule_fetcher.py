#!/usr/bin/env python3
"""
EQ12 Schedule Fetcher - Godlike Data Automation
Fetches schedules for MLB, NBA, NFL, CFB, NHL, Soccer with timezone-aware filtering
Filters for games starting at or after 12:00 PM (noon) local timezone
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import warnings
from datetime import datetime
from pathlib import Path

warnings.filterwarnings("ignore")

import pandas as pd
import pytz
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'schedule_fetcher_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("EQ12.ScheduleFetcher")

class ScheduleFetcher:
    """Fetches and normalizes sports schedules across multiple leagues"""
    
    def __init__(self, target_time: str = "12:00", after: bool = True, timezone: str = "US/Eastern"):
        self.target_time = target_time
        self.after = after
        self.timezone = pytz.timezone(timezone)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EQ12-GodlikeBetting/1.0 (contact@eq12.com)'
        })
        
        # API Keys
        self.odds_api_key = os.getenv("THE_ODDS_API_KEY")
        self.cfbd_api_key = os.getenv("CFBD_API_KEY") 
        self.football_data_token = os.getenv("FOOTBALL_DATA_API_TOKEN")
        
        logger.info(f"🎯 Schedule fetcher initialized - Target: {target_time}, After: {after}, TZ: {timezone}")
        
    def parse_target_time(self) -> datetime:
        """Parse target time into timezone-aware datetime for today"""
        today = datetime.now(self.timezone).date()
        time_parts = self.target_time.split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        target_dt = self.timezone.localize(datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute)))
        logger.info(f"🕐 Target time: {target_dt}")
        return target_dt
        
    def should_include_game(self, game_time: datetime) -> bool:
        """Check if game should be included based on time filter"""
        target_dt = self.parse_target_time()
        
        if self.after:
            # Include games at or after target time
            return game_time >= target_dt
        else:
            # Include games within ±15 minutes of target time
            time_diff = abs((game_time - target_dt).total_seconds() / 60)
            return time_diff <= 15
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def fetch_nba_schedule(self) -> list[dict]:
        """Fetch NBA schedule using free NBA API"""
        games = []
        try:
            # Use balldontlie API (free tier)
            url = "https://www.balldontlie.io/api/v1/games"
            today = datetime.now().strftime("%Y-%m-%d")
            
            params = {
                'dates[]': today,
                'per_page': 100
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            for game in data.get('data', []):
                try:
                    # Parse game time
                    game_time_str = game.get('status')  # This might need adjustment based on API response
                    if game_time_str and game_time_str != 'Final':
                        # Convert to timezone-aware datetime
                        game_time = datetime.now(self.timezone)  # Placeholder - adjust based on actual API
                        
                        if self.should_include_game(game_time):
                            games.append({
                                'league': 'NBA',
                                'home_team': game.get('home_team', {}).get('full_name', ''),
                                'away_team': game.get('visitor_team', {}).get('full_name', ''),
                                'start_time': game_time.isoformat(),
                                'venue': game.get('home_team', {}).get('city', ''),
                                'game_id': f"nba_{game.get('id')}",
                                'api_source': 'balldontlie'
                            })
                except Exception as e:
                    logger.warning(f"Error parsing NBA game: {e}")
                    
            logger.info(f"✅ Fetched {len(games)} NBA games")
            
        except Exception as e:
            logger.error(f"❌ NBA API error: {e}")
            
        return games
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def fetch_mlb_schedule(self) -> list[dict]:
        """Fetch MLB schedule using MLB Stats API"""
        games = []
        try:
            # Use MLB Stats API (free)
            today = datetime.now().strftime("%Y-%m-%d")
            url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}&hydrate=team,linescore"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            for date_info in data.get('dates', []):
                for game in date_info.get('games', []):
                    try:
                        # Parse game time
                        game_time_str = game.get('gameDate')
                        if game_time_str:
                            game_time = datetime.fromisoformat(game_time_str.replace('Z', '+00:00'))
                            game_time = game_time.astimezone(self.timezone)
                            
                            if self.should_include_game(game_time):
                                games.append({
                                    'league': 'MLB',
                                    'home_team': game.get('teams', {}).get('home', {}).get('team', {}).get('name', ''),
                                    'away_team': game.get('teams', {}).get('away', {}).get('team', {}).get('name', ''),
                                    'start_time': game_time.isoformat(),
                                    'venue': game.get('venue', {}).get('name', ''),
                                    'game_id': f"mlb_{game.get('gamePk')}",
                                    'api_source': 'mlb_statsapi'
                                })
                    except Exception as e:
                        logger.warning(f"Error parsing MLB game: {e}")
                        
            logger.info(f"✅ Fetched {len(games)} MLB games")
            
        except Exception as e:
            logger.error(f"❌ MLB API error: {e}")
            
        return games
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def fetch_nfl_schedule(self) -> list[dict]:
        """Fetch NFL schedule using ESPN API"""
        games = []
        try:
            # Use ESPN API (free)
            url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            for event in data.get('events', []):
                try:
                    # Parse game time
                    game_time_str = event.get('date')
                    if game_time_str:
                        game_time = datetime.fromisoformat(game_time_str.replace('Z', '+00:00'))
                        game_time = game_time.astimezone(self.timezone)
                        
                        if self.should_include_game(game_time):
                            competitions = event.get('competitions', [{}])
                            if competitions:
                                competitors = competitions[0].get('competitors', [])
                                home_team = next((c for c in competitors if c.get('homeAway') == 'home'), {})
                                away_team = next((c for c in competitors if c.get('homeAway') == 'away'), {})
                                
                                games.append({
                                    'league': 'NFL',
                                    'home_team': home_team.get('team', {}).get('displayName', ''),
                                    'away_team': away_team.get('team', {}).get('displayName', ''),
                                    'start_time': game_time.isoformat(),
                                    'venue': competitions[0].get('venue', {}).get('fullName', ''),
                                    'game_id': f"nfl_{event.get('id')}",
                                    'api_source': 'espn'
                                })
                except Exception as e:
                    logger.warning(f"Error parsing NFL game: {e}")
                    
            logger.info(f"✅ Fetched {len(games)} NFL games")
            
        except Exception as e:
            logger.error(f"❌ NFL API error: {e}")
            
        return games
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def fetch_cfb_schedule(self) -> list[dict]:
        """Fetch CFB schedule using CFBD API"""
        games = []
        if not self.cfbd_api_key:
            logger.warning("⚠️ CFBD API key missing, skipping CFB")
            return games
            
        try:
            url = "https://api.collegefootballdata.com/games"
            today = datetime.now().strftime("%Y-%m-%d")
            
            headers = {"Authorization": f"Bearer {self.cfbd_api_key}"}
            params = {
                'year': datetime.now().year,
                'week': self.get_cfb_week(),
                'division': 'fbs'
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            for game in data:
                try:
                    # Parse game time
                    game_time_str = game.get('start_date')
                    if game_time_str:
                        game_time = datetime.fromisoformat(game_time_str.replace('Z', '+00:00'))
                        game_time = game_time.astimezone(self.timezone)
                        
                        if self.should_include_game(game_time):
                            games.append({
                                'league': 'CFB',
                                'home_team': game.get('home_team', ''),
                                'away_team': game.get('away_team', ''),
                                'start_time': game_time.isoformat(),
                                'venue': game.get('venue', ''),
                                'game_id': f"cfb_{game.get('id')}",
                                'api_source': 'cfbd'
                            })
                except Exception as e:
                    logger.warning(f"Error parsing CFB game: {e}")
                    
            logger.info(f"✅ Fetched {len(games)} CFB games")
            
        except Exception as e:
            logger.error(f"❌ CFB API error: {e}")
            
        return games
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def fetch_nhl_schedule(self) -> list[dict]:
        """Fetch NHL schedule using NHL API"""
        games = []
        try:
            # Use NHL API (free)
            today = datetime.now().strftime("%Y-%m-%d")
            url = f"https://statsapi.web.nhl.com/api/v1/schedule?date={today}&expand=schedule.teams,schedule.linescore"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            for date_info in data.get('dates', []):
                for game in date_info.get('games', []):
                    try:
                        # Parse game time
                        game_time_str = game.get('gameDate')
                        if game_time_str:
                            game_time = datetime.fromisoformat(game_time_str.replace('Z', '+00:00'))
                            game_time = game_time.astimezone(self.timezone)
                            
                            if self.should_include_game(game_time):
                                games.append({
                                    'league': 'NHL',
                                    'home_team': game.get('teams', {}).get('home', {}).get('team', {}).get('name', ''),
                                    'away_team': game.get('teams', {}).get('away', {}).get('team', {}).get('name', ''),
                                    'start_time': game_time.isoformat(),
                                    'venue': game.get('venue', {}).get('name', ''),
                                    'game_id': f"nhl_{game.get('gamePk')}",
                                    'api_source': 'nhl_statsapi'
                                })
                    except Exception as e:
                        logger.warning(f"Error parsing NHL game: {e}")
                        
            logger.info(f"✅ Fetched {len(games)} NHL games")
            
        except Exception as e:
            logger.error(f"❌ NHL API error: {e}")
            
        return games
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def fetch_soccer_schedule(self) -> list[dict]:
        """Fetch Soccer schedule using football-data.org API"""
        games = []
        if not self.football_data_token:
            logger.warning("⚠️ Football Data API token missing, skipping Soccer")
            return games
            
        try:
            # Use football-data.org API
            url = "https://api.football-data.org/v4/matches"
            today = datetime.now().strftime("%Y-%m-%d")
            
            headers = {"X-Auth-Token": self.football_data_token}
            params = {
                'dateFrom': today,
                'dateTo': today,
                'status': 'SCHEDULED'
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            for match in data.get('matches', []):
                try:
                    # Parse game time
                    game_time_str = match.get('utcDate')
                    if game_time_str:
                        game_time = datetime.fromisoformat(game_time_str.replace('Z', '+00:00'))
                        game_time = game_time.astimezone(self.timezone)
                        
                        if self.should_include_game(game_time):
                            games.append({
                                'league': 'Soccer',
                                'home_team': match.get('homeTeam', {}).get('name', ''),
                                'away_team': match.get('awayTeam', {}).get('name', ''),
                                'start_time': game_time.isoformat(),
                                'venue': match.get('venue', ''),
                                'game_id': f"soccer_{match.get('id')}",
                                'api_source': 'football_data'
                            })
                except Exception as e:
                    logger.warning(f"Error parsing Soccer game: {e}")
                    
            logger.info(f"✅ Fetched {len(games)} Soccer games")
            
        except Exception as e:
            logger.error(f"❌ Soccer API error: {e}")
            
        return games
    
    def get_cfb_week(self) -> int:
        """Calculate current CFB week"""
        # Simple approximation - adjust based on actual CFB calendar
        week = datetime.now().isocalendar()[1] - 34  # Approximate CFB season start
        return max(1, min(week, 17))
    
    async def fetch_all_schedules(self) -> pd.DataFrame:
        """Fetch schedules from all leagues concurrently"""
        logger.info("🚀 Starting concurrent schedule fetch...")
        
        # Run all API calls concurrently
        results = await asyncio.gather(
            self.fetch_nba_schedule(),
            self.fetch_mlb_schedule(), 
            self.fetch_nfl_schedule(),
            self.fetch_cfb_schedule(),
            self.fetch_nhl_schedule(),
            self.fetch_soccer_schedule(),
            return_exceptions=True
        )
        
        # Combine all games
        all_games = []
        for result in results:
            if isinstance(result, list):
                all_games.extend(result)
            else:
                logger.error(f"API fetch error: {result}")
        
        if not all_games:
            logger.warning("⚠️ No games found matching criteria")
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(all_games)
        
        # Sort by start time
        df['start_time_dt'] = pd.to_datetime(df['start_time'])
        df = df.sort_values('start_time_dt').drop('start_time_dt', axis=1)
        
        return df
    
    def save_schedule(self, df: pd.DataFrame) -> str:
        """Save schedule to CSV file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filter_type = "after" if self.after else "exact"
        filename = f"schedules_{timestamp}_{filter_type}.csv"
        filepath = data_dir / filename
        
        df.to_csv(filepath, index=False)
        logger.info(f"💾 Saved schedule to: {filepath}")
        
        return str(filepath)
    
    def print_summary(self, df: pd.DataFrame):
        """Print schedule summary"""
        if df.empty:
            logger.info("📊 No games found matching criteria")
            return
        
        # Games per league
        league_counts = df['league'].value_counts()
        logger.info("📊 SCHEDULE SUMMARY")
        logger.info("=" * 50)
        
        for league, count in league_counts.items():
            logger.info(f"  {league}: {count} games")
        
        # Time range
        earliest = df['start_time'].min()
        latest = df['start_time'].max()
        
        logger.info(f"⏰ Time Range: {earliest} to {latest}")
        logger.info(f"🎯 Total Games: {len(df)}")
        
        # Sample games
        logger.info("\n🎮 SAMPLE GAMES:")
        for _, game in df.head(5).iterrows():
            logger.info(f"  {game['league']}: {game['away_team']} @ {game['home_team']} - {game['start_time'][:16]}")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="EQ12 Godlike Schedule Fetcher")
    parser.add_argument("--time", default="12:00", help="Target time (default: 12:00)")
    parser.add_argument("--after", action="store_true", default=True, help="Include games at or after time (default: True)")
    parser.add_argument("--exact", action="store_true", help="Include games within ±15min of time")
    parser.add_argument("--tz", default="US/Eastern", help="Timezone (default: US/Eastern)")
    
    args = parser.parse_args()
    
    # Handle exact flag
    after_flag = not args.exact if args.exact else args.after
    
    try:
        fetcher = ScheduleFetcher(
            target_time=args.time,
            after=after_flag,
            timezone=args.tz
        )
        
        df = await fetcher.fetch_all_schedules()
        
        if not df.empty:
            filepath = fetcher.save_schedule(df)
            fetcher.print_summary(df)
            
            # Save JSON summary
            summary = {
                "timestamp": datetime.now().isoformat(),
                "filter": {
                    "time": args.time,
                    "after": after_flag,
                    "timezone": args.tz
                },
                "games_found": len(df),
                "leagues": df['league'].value_counts().to_dict(),
                "filepath": filepath
            }
            
            summary_path = data_dir / f"schedule_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
                
            logger.info("✅ EQ12 Schedule Fetcher completed successfully!")
            return filepath
        else:
            logger.warning("❌ No games found for specified criteria")
            return None
            
    except Exception as e:
        logger.error(f"❌ Schedule fetcher failed: {e}")
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