#!/usr/bin/env python3
"""
 EQ12 REAL SPORTS API FETCHER 
Fetches actual sports data for November 8, 2025 using real APIs

This replaces fake game generation with legitimate API calls to:
- The Odds API (for current games and odds)
- Real sports schedules for accurate game data

Author: EQ12 AI Assistant
Date: November 8, 2025
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RealGameEvent:
    """Real sports game event from API data"""
    id: str
    sport: str
    league: str
    home_team: str
    away_team: str
    start_time: str
    bookmakers: List[Dict[str, Any]]
    markets: List[Dict[str, Any]]

class EQ12RealSportsAPIFetcher:
    """
     Real Sports Data Fetcher using legitimate APIs
    
    Fetches actual games for November 8, 2025 from:
    - The Odds API (NBA, NHL, NFL, NCAAB, NCAAF)
    - Real schedules and odds data
    """
    
    def __init__(self):
        self.odds_api_key = os.getenv('THE_ODDS_API_KEY') or os.getenv('ODDS_API_KEY')
        if not self.odds_api_key:
            logger.error(" No Odds API key found! Set THE_ODDS_API_KEY or ODDS_API_KEY environment variable")
            sys.exit(1)
        
        self.base_url = "https://api.the-odds-api.com/v4"
        self.sports_mapping = {
            'NBA': 'basketball_nba',
            'NHL': 'icehockey_nhl', 
            'NFL': 'americanfootball_nfl',
            'NCAAB': 'basketball_ncaab',  # College Basketball
            'NCAAF': 'americanfootball_ncaaf'  # College Football
        }
        
        # Rate limiting
        self.last_request_time = 0
        self.request_delay = 1.0  # 1 second between requests
        
        logger.info(f" EQ12 Real Sports API Fetcher initialized")
        logger.info(f" Using Odds API Key: {self.odds_api_key[:20]}...")
    
    def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make rate-limited API request"""
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        
        params['apiKey'] = self.odds_api_key
        
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params, timeout=30)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.error(f" API Authentication failed - check your API key")
                return None
            elif response.status_code == 429:
                logger.warning(f" Rate limit hit - waiting 60 seconds")
                time.sleep(60)
                return self._make_api_request(endpoint, params)
            else:
                logger.error(f" API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f" Network error: {e}")
            return None
    
    def fetch_real_games_for_today(self) -> List[RealGameEvent]:
        """
        Fetch actual games scheduled for November 8, 2025
        """
        logger.info(" Fetching real games for November 8, 2025...")
        
        all_games = []
        
        for league, sport_key in self.sports_mapping.items():
            logger.info(f" Fetching {league} games...")
            
            params = {
                'sport': sport_key,
                'regions': 'us',
                'markets': 'h2h,spreads,totals',  # Moneyline, spreads, over/under
                'oddsFormat': 'american',
                'dateFormat': 'iso'
            }
            
            data = self._make_api_request('sports/{}/odds'.format(sport_key), params)
            
            if data:
                today_games = []
                target_date = "2025-11-08"
                
                for game in data:
                    game_date = game.get('commence_time', '')[:10]  # Get YYYY-MM-DD part
                    
                    if game_date == target_date:
                        real_game = RealGameEvent(
                            id=game.get('id', ''),
                            sport=sport_key,
                            league=league,
                            home_team=game.get('home_team', ''),
                            away_team=game.get('away_team', ''),
                            start_time=game.get('commence_time', ''),
                            bookmakers=game.get('bookmakers', []),
                            markets=[]
                        )
                        
                        # Extract markets from bookmakers
                        for bookmaker in real_game.bookmakers:
                            for market in bookmaker.get('markets', []):
                                real_game.markets.append({
                                    'key': market.get('key'),
                                    'outcomes': market.get('outcomes', []),
                                    'bookmaker': bookmaker.get('title', '')
                                })
                        
                        today_games.append(real_game)
                        all_games.append(real_game)
                
                logger.info(f" Found {len(today_games)} real {league} games for November 8, 2025")
            else:
                logger.warning(f" No data returned for {league}")
            
            # Small delay between different sports
            time.sleep(0.5)
        
        logger.info(f" Total real games found: {len(all_games)}")
        return all_games
    
    def get_available_sports(self) -> List[Dict[str, Any]]:
        """Get list of available sports from the API"""
        data = self._make_api_request('sports', {})
        if data:
            return data
        return []
    
    def save_real_games_data(self, games: List[RealGameEvent], filename: str = None) -> str:
        """Save real games data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"real_games_data_{timestamp}.json"
        
        filepath = os.path.join("C:\\EQ12\\logs", filename)
        
        games_data = {
            "timestamp": datetime.now().isoformat(),
            "date": "2025-11-08",
            "total_games": len(games),
            "games": []
        }
        
        for game in games:
            games_data["games"].append({
                "id": game.id,
                "sport": game.sport,
                "league": game.league,
                "home_team": game.home_team,
                "away_team": game.away_team,
                "start_time": game.start_time,
                "bookmakers_count": len(game.bookmakers),
                "markets_count": len(game.markets),
                "markets": game.markets[:3]  # Include first 3 markets as sample
            })
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(games_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f" Real games data saved to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f" Failed to save games data: {e}")
            return ""

def main():
    """Test the real sports API fetcher"""
    logger.info(" EQ12 Real Sports API Fetcher - Test Run")
    
    fetcher = EQ12RealSportsAPIFetcher()
    
    # First, check available sports
    logger.info(" Checking available sports...")
    sports = fetcher.get_available_sports()
    if sports:
        logger.info(f" Available sports: {len(sports)}")
        for sport in sports[:5]:  # Show first 5
            logger.info(f"   - {sport.get('title', 'Unknown')}: {sport.get('key', '')}")
    
    # Fetch real games for today
    real_games = fetcher.fetch_real_games_for_today()
    
    if real_games:
        logger.info(" REAL GAMES SUMMARY:")
        leagues = {}
        for game in real_games:
            if game.league not in leagues:
                leagues[game.league] = []
            leagues[game.league].append(f"{game.away_team} @ {game.home_team}")
        
        for league, games in leagues.items():
            logger.info(f" {league}: {len(games)} games")
            for game in games[:3]:  # Show first 3 games per league
                logger.info(f"   - {game}")
        
        # Save the data
        saved_file = fetcher.save_real_games_data(real_games)
        logger.info(f" Real sports data ready for parlay simulation!")
        
    else:
        logger.warning(" No real games found for November 8, 2025")
        logger.info("This could mean:")
        logger.info("1. No games scheduled for this date")
        logger.info("2. API key issues")
        logger.info("3. Date might be outside API coverage")

if __name__ == "__main__":
    main()