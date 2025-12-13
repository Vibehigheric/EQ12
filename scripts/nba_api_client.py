import requests
import logging
import time
import random
import json
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NBA_API_Client")

class NBAStatsClient:
    """
    Client for stats.nba.com
    Handles headers, rate limiting, and specific endpoint parsing.
    """
    
    BASE_URL = "https://stats.nba.com/stats"
    
    # Headers are CRITICAL for stats.nba.com
    HEADERS = {
        "Host": "stats.nba.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://www.nba.com",
        "Referer": "https://www.nba.com/",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _request(self, endpoint, params=None):
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Add random delay to avoid rate limits
        time.sleep(random.uniform(0.5, 1.5))
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {endpoint}: {e}")
            return None

    def get_active_players(self):
        """
        Fetches 'CommonAllPlayers' to get the roster list.
        Note: This gives the roster, but not necessarily 'Active for tonight'.
        """
        endpoint = "commonallplayers"
        params = {
            "LeagueID": "00",
            "Season": "2024-25", # Update season dynamically in real prod
            "IsOnlyCurrentSeason": "1"
        }
        
        data = self._request(endpoint, params)
        if not data:
            return []
            
        # Parse ResultSets
        headers = data['resultSets'][0]['headers']
        rows = data['resultSets'][0]['rowSet']
        
        players = []
        for row in rows:
            player = dict(zip(headers, row))
            if player['ROSTERSTATUS'] == 1: # 1 = Active on roster
                players.append(player)
                
        return players

    def get_player_info(self, player_id):
        """
        Get detailed info for a specific player.
        """
        endpoint = "commonplayerinfo"
        params = {"PlayerID": player_id}
        return self._request(endpoint, params)

    def get_daily_lineups(self):
        """
        Attempts to fetch daily lineups/rotations if available via scoreboard or similar.
        Stats.nba.com doesn't have a direct 'daily injury' endpoint that is public/reliable.
        We often use 'scoreboardv2' to see who is active in live games.
        """
        # For pre-game, we might need to rely on the scraper approach mentioned in the prompt.
        # But we can check 'scoreboardv2' for game status.
        endpoint = "scoreboardv2"
        params = {
            "GameDate": datetime.now().strftime("%Y-%m-%d"),
            "LeagueID": "00",
            "DayOffset": "0"
        }
        return self._request(endpoint, params)

if __name__ == "__main__":
    client = NBAStatsClient()
    print("Fetching active roster sample...")
    players = client.get_active_players()
    print(f"Found {len(players)} active players on rosters.")
    if players:
        print(f"Sample: {players[0]['DISPLAY_FIRST_LAST']} (ID: {players[0]['PERSON_ID']})")
