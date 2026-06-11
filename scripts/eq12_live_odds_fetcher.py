#!/usr/bin/env python3
"""
EQ12 Live Odds Fetcher - Real-time sports betting data collection
Fetches live odds from The Odds API for Coral Betting AI processing

Author: EQ12 Team
Date: November 3, 2025
Version: 1.0 - Live Data Ready
"""

import argparse
import json
import logging
import requests
import time
from datetime import datetime, timezone
from pathlib import Path
# Removed unused typing imports

# Configure API key from EQ12 environment
ODDS_API_KEY = "ODDS_API_KEY_PLACEHOLDER"

# The Odds API endpoints
BASE_URL = "https://api.the-odds-api.com/v4"

# Available sports for live betting
AVAILABLE_SPORTS = {
    "americanfootball_nfl": "NFL",
    "americanfootball_ncaaf": "NCAA Football",
    "basketball_nba": "NBA",
    "basketball_ncaab": "NCAA Basketball",
    "baseball_mlb": "MLB",
    "icehockey_nhl": "NHL",
    "soccer_epl": "English Premier League",
    "soccer_uefa_champs_league": "UEFA Champions League"
}

# Markets to fetch
MARKETS = ["h2h", "spreads", "totals"]
REGIONS = ["us", "uk", "au", "eu"]


class LiveOddsFetcher:
    """Live odds data fetcher for Coral Betting AI"""
    
    def __init__(self, workspace_path: str, verbose: bool = False):
        self.workspace_path = Path(workspace_path)
        self.data_path = self.workspace_path / "coral_betting_ai" / "data"
        self.logs_path = self.workspace_path / "logs"
        
        # Create directories
        for path in [self.data_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)
            
        self.verbose = verbose
        self.setup_logging()
        
        # API configuration
        self.api_key = ODDS_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EQ12-Coral-Betting-AI/1.0'
        })
        
        self.logger.info("Live Odds Fetcher initialized")
        self.logger.info(f"API Key: {' Configured' if self.api_key else ' Missing'}")
        
    def setup_logging(self):
        """Setup logging for odds fetcher"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.logs_path / f"live_odds_fetcher_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.DEBUG if self.verbose else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def get_sports_list(self):
        """Get list of available sports from The Odds API"""
        url = f"{BASE_URL}/sports"
        params = {"apiKey": self.api_key}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            sports = response.json()
            self.logger.info(f"Retrieved {len(sports)} available sports")
            return sports
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching sports list: {e}")
            return []
            
    def fetch_odds_for_sport(self, sport: str, bookmakers=None):
        """Fetch live odds for a specific sport"""
        url = f"{BASE_URL}/sports/{sport}/odds"
        
        params = {
            "apiKey": self.api_key,
            "regions": ",".join(REGIONS),
            "markets": ",".join(MARKETS),
            "oddsFormat": "decimal",
            "dateFormat": "iso"
        }
        
        if bookmakers:
            params["bookmakers"] = ",".join(bookmakers)
            
        try:
            self.logger.info(f"Fetching odds for {sport}...")
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            odds_data = response.json()
            
            # Check API usage
            requests_used = response.headers.get('x-requests-used', 'Unknown')
            requests_remaining = response.headers.get('x-requests-remaining', 'Unknown')
            
            self.logger.info(f" Fetched {len(odds_data)} games for {sport}")
            self.logger.info(f"API Usage: {requests_used} used, {requests_remaining} remaining")
            
            return {
                'sport': sport,
                'sport_title': AVAILABLE_SPORTS.get(sport, sport),
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'games_count': len(odds_data),
                'api_usage': {
                    'requests_used': requests_used,
                    'requests_remaining': requests_remaining
                },
                'games': odds_data
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching odds for {sport}: {e}")
            return {
                'sport': sport,
                'error': str(e),
                'games': []
            }
            
    def fetch_live_odds(self, sports=None, save_file=True):
        """Fetch live odds for multiple sports"""
        if not sports:
            sports = list(AVAILABLE_SPORTS.keys())[:4]  # Limit to 4 sports to save API calls
            
        self.logger.info(f" Starting live odds fetch for {len(sports)} sports")
        
        all_odds = {
            'fetch_timestamp': datetime.now(timezone.utc).isoformat(),
            'sports_requested': sports,
            'api_odds': [],
            'summary': {
                'total_sports': len(sports),
                'total_games': 0,
                'successful_fetches': 0,
                'failed_fetches': 0
            }
        }
        
        for sport in sports:
            sport_odds = self.fetch_odds_for_sport(sport)
            
            if sport_odds.get('games'):
                all_odds['summary']['successful_fetches'] += 1
                all_odds['summary']['total_games'] += len(sport_odds['games'])
                
                # Add sport info to each game
                for game in sport_odds['games']:
                    game['sport'] = sport
                    game['sport_title'] = AVAILABLE_SPORTS.get(sport, sport)
                    game['game_id'] = f"{sport}_{game.get('id', 'unknown')}"
                    all_odds['api_odds'].append(game)
                    
            else:
                all_odds['summary']['failed_fetches'] += 1
                
            # Rate limiting - wait between requests
            time.sleep(1)
            
        if save_file:
            self.save_odds_data(all_odds)
            
        self.logger.info(f" Live odds fetch complete!")
        self.logger.info(f" Summary: {all_odds['summary']['total_games']} games from {all_odds['summary']['successful_fetches']} sports")
        
        return all_odds
        
    def save_odds_data(self, odds_data):
        """Save fetched odds data to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"live_odds_{timestamp}.json"
        filepath = self.data_path / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(odds_data, f, indent=2, default=str)
                
            self.logger.info(f" Odds data saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error saving odds data: {e}")
            return ""
            
    def get_usage_info(self):
        """Get API usage information"""
        url = f"{BASE_URL}/sports"
        params = {"apiKey": self.api_key}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            return {
                'requests_used': response.headers.get('x-requests-used', 'Unknown'),
                'requests_remaining': response.headers.get('x-requests-remaining', 'Unknown'),
                'status': 'active'
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Error checking API usage: {e}")
            return {
                'error': str(e),
                'status': 'error'
            }


def main():
    parser = argparse.ArgumentParser(description="EQ12 Live Odds Fetcher")
    parser.add_argument("--workspace", default="C:/EQ12", help="Workspace path")
    parser.add_argument("--sports", nargs="+", choices=list(AVAILABLE_SPORTS.keys()), 
                       help="Sports to fetch (default: NFL, NBA, NCAA Football, NCAA Basketball)")
    parser.add_argument("--output", help="Output file path (auto-generated if not specified)")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    parser.add_argument("--usage-info", action="store_true", help="Show API usage info only")
    
    args = parser.parse_args()
    
    # Initialize fetcher
    fetcher = LiveOddsFetcher(args.workspace, args.verbose)
    
    print(f" EQ12 Live Odds Fetcher")
    print(f"   API Status: {' Ready' if fetcher.api_key else ' No API Key'}")
    print(f"   Available Sports: {len(AVAILABLE_SPORTS)}")
    
    if args.usage_info:
        usage = fetcher.get_usage_info()
        print(f"\n API Usage Information:")
        print(f"   Requests Used: {usage.get('requests_used', 'Unknown')}")
        print(f"   Requests Remaining: {usage.get('requests_remaining', 'Unknown')}")
        print(f"   Status: {usage.get('status', 'Unknown')}")
        return
        
    # Determine sports to fetch
    sports_to_fetch = args.sports or ["americanfootball_nfl", "basketball_nba", "americanfootball_ncaaf", "basketball_ncaab"]
    
    print(f"\n Fetching live odds for:")
    for sport in sports_to_fetch:
        print(f"    {AVAILABLE_SPORTS.get(sport, sport)}")
    
    # Fetch live odds
    odds_data = fetcher.fetch_live_odds(sports_to_fetch)
    
    # Display results
    print(f"\n Live Odds Fetch Complete!")
    print(f"   Total Games: {odds_data['summary']['total_games']}")
    print(f"   Successful Sports: {odds_data['summary']['successful_fetches']}")
    print(f"   Failed Sports: {odds_data['summary']['failed_fetches']}")
    
    # Show sample games
    if odds_data['api_odds']:
        print(f"\n Sample Games Fetched:")
        for i, game in enumerate(odds_data['api_odds'][:5], 1):
            home_team = game.get('home_team', 'Unknown')
            away_team = game.get('away_team', 'Unknown')
            sport_title = game.get('sport_title', 'Unknown')
            bookmaker_count = len(game.get('bookmakers', []))
            
            print(f"   {i}. {away_team} @ {home_team} ({sport_title}) - {bookmaker_count} bookmakers")
            
        if len(odds_data['api_odds']) > 5:
            print(f"   ... and {len(odds_data['api_odds']) - 5} more games")
    
    # Output file info
    if odds_data.get('api_odds'):
        print(f"\n Data saved to: {fetcher.data_path}")
        
        # Show most recent file
        recent_files = list(fetcher.data_path.glob("live_odds_*.json"))
        if recent_files:
            latest_file = max(recent_files, key=lambda f: f.stat().st_mtime)
            print(f"   Latest file: {latest_file.name}")
            print(f"\n Ready for Coral Betting AI processing!")
            print(f"   Run: python eq12_coral_betting_ai.py --input \"{latest_file}\"")


if __name__ == "__main__":
    main()