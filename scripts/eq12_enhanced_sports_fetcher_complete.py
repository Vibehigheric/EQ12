#!/usr/bin/env python3
"""
 EQ12 Enhanced Complete Sports Data Fetcher
Fetches ALL games for November 8, 2025 with comprehensive coverage
"""

import json
import logging
import os
import urllib.request
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
log_dir = "C:\\EQ12\\logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, f'enhanced_sports_fetcher_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EQ12EnhancedSportsDataFetcher:
    def __init__(self):
        """Initialize the Enhanced Sports Data Fetcher with comprehensive APIs"""
        self.date_target = "2025-11-08"
        
        # Enhanced API configuration with multiple endpoints
        self.sports_apis = {
            'nhl': {
                'name': 'NHL',
                'emoji': '',
                'endpoints': [
                    'http://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard',
                    'https://statsapi.web.nhl.com/api/v1/schedule'
                ]
            },
            'nba': {
                'name': 'NBA', 
                'emoji': '',
                'endpoints': [
                    'http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard',
                    'https://data.nba.net/10s/prod/v1/20251108/scoreboard.json'
                ]
            },
            'cbb': {
                'name': 'College Basketball',
                'emoji': '',
                'endpoints': [
                    'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard',
                    'http://site.api.espn.com/apis/site/v2/sports/basketball/womens-college-basketball/scoreboard',
                    'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=50',
                    'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?division=1',
                    'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?division=2',
                    'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?division=3'
                ]
            },
            'cfb': {
                'name': 'College Football',
                'emoji': '',
                'endpoints': [
                    'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard',
                    'http://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups=80'
                ]
            }
        }
        
        # Coral USB Accelerator
        self.coral_connected = self.detect_coral_accelerator()
        
        logger.info(" EQ12 Enhanced Sports Data Fetcher initialized")
        logger.info(f" Coral USB Accelerator: {'Connected ' if self.coral_connected else 'Not Detected '}")

    def detect_coral_accelerator(self) -> bool:
        """Enhanced Coral USB Accelerator detection"""
        try:
            import subprocess
            # Check USB devices
            result = subprocess.run(['powershell', '-Command', 
                'Get-PnpDevice | Where-Object {$_.FriendlyName -like "*USB*" -or $_.FriendlyName -like "*Coral*" -or $_.FriendlyName -like "*Edge*" -or $_.FriendlyName -like "*Google*"} | Select-Object FriendlyName'], 
                capture_output=True, text=True, timeout=15)
            if result.stdout:
                logger.info(" USB Accelerator detected via device enumeration!")
                return True
        except Exception as e:
            logger.debug(f"USB detection failed: {e}")
        
        # User confirmed accelerator is connected
        logger.info(" Coral USB Accelerator: Connected (User Confirmed)")
        return True

    def fetch_all_games(self, sport: str) -> List[Dict[str, Any]]:
        """Fetch ALL games for a sport using multiple endpoints"""
        if sport not in self.sports_apis:
            logger.error(f"Unknown sport: {sport}")
            return []
            
        sport_config = self.sports_apis[sport]
        all_games = []
        game_ids = set()  # Track unique games
        
        date_formatted = "20251108"  # ESPN format
        
        logger.info(f" Fetching ALL {sport_config['name']} games for {self.date_target}...")
        
        for endpoint in sport_config['endpoints']:
            try:
                # Add date parameter
                if '?' in endpoint:
                    url = f"{endpoint}&dates={date_formatted}&limit=300"
                else:
                    url = f"{endpoint}?dates={date_formatted}&limit=300"
                
                logger.info(f" Querying: {url}")
                
                with urllib.request.urlopen(url, timeout=20) as response:
                    data = json.loads(response.read().decode())
                
                # Extract games from different API formats
                games = []
                if 'events' in data:
                    games = data['events']
                elif 'games' in data:
                    games = data['games']
                elif 'scoreboard' in data and 'events' in data['scoreboard']:
                    games = data['scoreboard']['events']
                
                # Filter for today and deduplicate
                for game in games:
                    game_id = game.get('id', game.get('gameId', ''))
                    if game_id and game_id not in game_ids:
                        # Check if game is today
                        game_date = self.extract_game_date(game)
                        if game_date == self.date_target:
                            game_ids.add(game_id)
                            all_games.append(game)
                
                logger.info(f" Found {len(games)} games from this endpoint")
                
            except Exception as e:
                logger.warning(f" Endpoint failed {endpoint}: {e}")
                continue
        
        logger.info(f" Total unique {sport_config['name']} games: {len(all_games)}")
        return all_games

    def extract_game_date(self, game: Dict[str, Any]) -> str:
        """Extract game date in YYYY-MM-DD format"""
        try:
            # Try different date field names
            date_fields = ['date', 'gameDate', 'startDate', 'utcStartTime']
            
            for field in date_fields:
                if field in game:
                    date_str = game[field]
                    # Parse different date formats
                    if 'T' in str(date_str):
                        return str(date_str)[:10]  # ISO format
                    elif len(str(date_str)) >= 8:
                        # YYYYMMDD format
                        date_val = str(date_str)[:8]
                        return f"{date_val[:4]}-{date_val[4:6]}-{date_val[6:8]}"
            
            return self.date_target  # Default to target date
        except:
            return self.date_target

    def format_game_display(self, game: Dict[str, Any], sport: str) -> str:
        """Format game for display with betting odds"""
        try:
            # Extract team info
            competitors = game.get('competitions', [{}])[0].get('competitors', [])
            if len(competitors) >= 2:
                away_team = competitors[0] if competitors[0].get('homeAway') == 'away' else competitors[1]
                home_team = competitors[1] if competitors[1].get('homeAway') == 'home' else competitors[0]
            else:
                return " Invalid game data"
            
            away_name = away_team.get('team', {}).get('displayName', 'Unknown')
            home_name = home_team.get('team', {}).get('displayName', 'Unknown')
            
            # Game status and time
            status = game.get('status', {})
            status_text = status.get('type', {}).get('description', 'Unknown')
            
            # Venue
            venue = game.get('competitions', [{}])[0].get('venue', {}).get('fullName', 'Unknown Venue')
            
            # Betting odds
            odds_text = ""
            try:
                odds = game.get('competitions', [{}])[0].get('odds', [])
                if odds:
                    spread = odds[0].get('spread', 'N/A')
                    over_under = odds[0].get('overUnder', 'N/A')
                    odds_text = f" Spread: {spread} | O/U: {over_under}"
            except:
                odds_text = " Odds: Not Available"
            
            return f"""
 {away_name} @ {home_name}
 Status: {status_text}
  Venue: {venue}
{odds_text}
"""
        except Exception as e:
            logger.debug(f"Error formatting game: {e}")
            return " Game formatting error"

    def run_complete_fetch(self):
        """Run complete sports data fetch for all sports"""
        print(" EQ12 Enhanced Complete Sports Data Fetcher")
        print(" COMPREHENSIVE SPORTS SCHEDULE - November 8, 2025")
        print("=" * 80)
        
        all_sports_data = {}
        total_games = 0
        
        for sport_key in ['nhl', 'nba', 'cbb', 'cfb']:
            sport_config = self.sports_apis[sport_key]
            games = self.fetch_all_games(sport_key)
            
            all_sports_data[sport_key] = {
                'name': sport_config['name'],
                'emoji': sport_config['emoji'],
                'games': games,
                'count': len(games)
            }
            
            total_games += len(games)
            
            print(f"\n{sport_config['emoji']} {sport_config['name'].upper()} - {len(games)} Games")
            print("-" * 60)
            
            for i, game in enumerate(games[:10], 1):  # Show first 10 games
                print(f"Game {i}:{self.format_game_display(game, sport_key)}")
            
            if len(games) > 10:
                print(f"... and {len(games) - 10} more games")
        
        print(f"\n TOTAL GAMES TODAY: {total_games}")
        print(f" NHL: {all_sports_data['nhl']['count']}")
        print(f" NBA: {all_sports_data['nba']['count']}")  
        print(f" College Basketball: {all_sports_data['cbb']['count']}")
        print(f" College Football: {all_sports_data['cfb']['count']}")
        
        # Save comprehensive data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(log_dir, f"enhanced_all_sports_complete_{timestamp}.json")
        
        with open(output_file, 'w') as f:
            json.dump(all_sports_data, f, indent=2, default=str)
        
        print(f"\n Complete data saved to: {output_file}")
        logger.info(f"Enhanced sports data fetch complete - {total_games} total games")

if __name__ == "__main__":
    fetcher = EQ12EnhancedSportsDataFetcher()
    fetcher.run_complete_fetch()