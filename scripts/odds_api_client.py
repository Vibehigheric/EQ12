import os
import requests
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EQ12OddsAPIClient:
    """
    EQ12 Client for The Odds API (SportsGameOdds backup)
    Provides real-time odds data to feed into AI analysis.
    """
    
    BASE_URL = "https://api.the-odds-api.com/v4"

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ODDS_API_KEY")
        if not self.api_key:
            logger.warning("ODDS_API_KEY not found in environment variables.")
            self.available = False
        else:
            self.available = True
            logger.info("✅ EQ12 Odds API Client initialized")

    def get_sports(self) -> List[Dict]:
        """Get list of available sports"""
        if not self.available:
            return []
            
        try:
            response = requests.get(
                f"{self.BASE_URL}/sports",
                params={"apiKey": self.api_key}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching sports: {e}")
            return []

    def get_odds(self, sport_key: str, regions: str = "us", markets: str = "h2h") -> List[Dict]:
        """
        Get odds for a specific sport.
        
        Args:
            sport_key: Sport key (e.g., 'icehockey_nhl', 'basketball_nba')
            regions: Comma-separated regions (us, uk, eu, au)
            markets: Comma-separated markets (h2h, spreads, totals)
        """
        if not self.available:
            return []

        try:
            response = requests.get(
                f"{self.BASE_URL}/sports/{sport_key}/odds",
                params={
                    "apiKey": self.api_key,
                    "regions": regions,
                    "markets": markets,
                    "oddsFormat": "american"
                }
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Successfully fetched {len(data)} games for {sport_key}")
            return data
        except Exception as e:
            logger.error(f"Error fetching odds for {sport_key}: {e}")
            return []

    def get_remaining_requests(self) -> int:
        """Check remaining API requests"""
        if not self.available:
            return 0
            
        try:
            response = requests.get(
                f"{self.BASE_URL}/sports",
                params={"apiKey": self.api_key}
            )
            if "x-requests-remaining" in response.headers:
                return int(response.headers["x-requests-remaining"])
            return 0
        except:
            return 0

if __name__ == "__main__":
    # Simple test
    client = EQ12OddsAPIClient()
    if client.available:
        print(f"Remaining requests: {client.get_remaining_requests()}")
        sports = client.get_sports()
        print(f"Found {len(sports)} active sports")
        
        # Try to get NHL odds
        nhl_odds = client.get_odds("icehockey_nhl")
        if nhl_odds:
            print(f"Found {len(nhl_odds)} NHL games with odds")
            print(f"Sample game: {nhl_odds[0]['home_team']} vs {nhl_odds[0]['away_team']}")
