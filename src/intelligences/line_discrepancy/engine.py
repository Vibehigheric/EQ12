import os
import requests
import logging
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LineDiscrepancyEngine")

class LineDiscrepancyEngine:
    """
    Intelligence #1: Line Discrepancy Engine
    Detects when a specific sportsbook's line deviates significantly from the market consensus.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        if not self.api_key:
            logger.warning("ODDS_API_KEY not found. Engine will run in MOCK mode.")
            self.mock_mode = True
        else:
            self.mock_mode = False
        
        self.base_url = "https://api.the-odds-api.com/v4/sports"
        self.sports = ["basketball_nba", "americanfootball_nfl", "icehockey_nhl"]
        self.regions = "us"
        self.markets = "h2h,spreads,totals"

    def fetch_odds(self, sport: str) -> List[Dict[str, Any]]:
        """Fetches odds for a specific sport from the Odds API."""
        if self.mock_mode:
            return self._get_mock_data(sport)

        url = f"{self.base_url}/{sport}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": self.regions,
            "markets": self.markets,
            "oddsFormat": "decimal"
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Fetched {len(data)} events for {sport}")
            return data
        except Exception as e:
            logger.error(f"Error fetching odds for {sport}: {e}")
            return []

    def analyze_discrepancies(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyzes odds to find discrepancies.
        Logic: Calculate average odds (consensus) and flag books that deviate by > X%.
        """
        discrepancies = []
        threshold_percent = 0.05  # 5% deviation

        for event in events:
            event_id = event.get("id")
            sport_key = event.get("sport_key")
            home_team = event.get("home_team")
            away_team = event.get("away_team")

            # Process H2H (Moneyline)
            h2h_odds = []
            for bookmaker in event.get("bookmakers", []):
                for market in bookmaker.get("markets", []):
                    if market["key"] == "h2h":
                        for outcome in market["outcomes"]:
                            h2h_odds.append({
                                "book": bookmaker["title"],
                                "team": outcome["name"],
                                "price": outcome["price"]
                            })

            # Calculate Consensus per team
            teams = set(o["team"] for o in h2h_odds)
            for team in teams:
                team_odds = [o["price"] for o in h2h_odds if o["team"] == team]
                if not team_odds:
                    continue
                
                avg_price = sum(team_odds) / len(team_odds)
                
                for odd in h2h_odds:
                    if odd["team"] == team:
                        deviation = (odd["price"] - avg_price) / avg_price
                        if abs(deviation) >= threshold_percent:
                            discrepancies.append({
                                "type": "Line Discrepancy",
                                "sport": sport_key,
                                "event": f"{away_team} @ {home_team}",
                                "market": "Moneyline",
                                "team": team,
                                "book": odd["book"],
                                "price": odd["price"],
                                "consensus": round(avg_price, 2),
                                "deviation": f"{round(deviation * 100, 2)}%",
                                "timestamp": datetime.utcnow().isoformat()
                            })

        return discrepancies

    def run(self):
        """Main execution loop for this intelligence."""
        logger.info("Starting Line Discrepancy Scan...")
        all_discrepancies = []

        for sport in self.sports:
            odds_data = self.fetch_odds(sport)
            if odds_data:
                discrepancies = self.analyze_discrepancies(odds_data)
                all_discrepancies.extend(discrepancies)

        logger.info(f"Scan complete. Found {len(all_discrepancies)} discrepancies.")
        return all_discrepancies

    def _get_mock_data(self, sport: str) -> List[Dict[str, Any]]:
        """Returns mock data for testing without API credits."""
        return [
            {
                "id": "mock_event_1",
                "sport_key": sport,
                "home_team": "Lakers",
                "away_team": "Warriors",
                "bookmakers": [
                    {
                        "title": "DraftKings",
                        "markets": [{"key": "h2h", "outcomes": [{"name": "Lakers", "price": 1.90}, {"name": "Warriors", "price": 1.90}]}]
                    },
                    {
                        "title": "FanDuel",
                        "markets": [{"key": "h2h", "outcomes": [{"name": "Lakers", "price": 1.85}, {"name": "Warriors", "price": 1.95}]}]
                    },
                    {
                        "title": "Bovada", # The outlier
                        "markets": [{"key": "h2h", "outcomes": [{"name": "Lakers", "price": 2.10}, {"name": "Warriors", "price": 1.75}]}]
                    }
                ]
            }
        ]

if __name__ == "__main__":
    engine = LineDiscrepancyEngine()
    results = engine.run()
    import json
    print(json.dumps(results, indent=2))
