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
logger = logging.getLogger("ArbitrageEngine")

class ArbitrageEngine:
    """
    Intelligence #2: Arbitrage + Hedging Engine
    Identifies risk-free profit opportunities (Arbs) and low-risk hedges (Middles).
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
        self.markets = "h2h" # Focus on Moneyline for simple arbs first

    def fetch_odds(self, sport: str) -> List[Dict[str, Any]]:
        """Fetches odds for a specific sport from the Odds API."""
        if self.mock_mode:
            return [] # Mock mode not implemented for Arb yet

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

    def find_arbitrage(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scans for arbitrage opportunities.
        Logic: For each event, find the best odds for each outcome across all bookmakers.
        If the sum of the inverse of best odds < 1.0, an arb exists.
        """
        opportunities = []

        for event in events:
            event_name = f"{event['away_team']} @ {event['home_team']}"
            sport_key = event['sport_key']
            
            # 1. Collect all odds for this event
            # Structure: { "Team A": [ {book: "DraftKings", price: 2.1}, ... ], "Team B": ... }
            outcomes_map = {}

            for bookmaker in event.get("bookmakers", []):
                for market in bookmaker.get("markets", []):
                    if market["key"] == "h2h":
                        for outcome in market["outcomes"]:
                            team = outcome["name"]
                            price = outcome["price"]
                            if team not in outcomes_map:
                                outcomes_map[team] = []
                            outcomes_map[team].append({
                                "book": bookmaker["title"],
                                "price": price
                            })

            # 2. Find best odds for each team
            best_odds = {}
            for team, odds_list in outcomes_map.items():
                if not odds_list:
                    continue
                # Sort by price descending (highest odds are best)
                best_price = sorted(odds_list, key=lambda x: x["price"], reverse=True)[0]
                best_odds[team] = best_price

            # 3. Check for Arb (assuming 2-way market for simplicity, e.g., NBA/NFL moneyline)
            # Note: This logic needs refinement for 3-way markets (Soccer)
            if len(best_odds) == 2:
                teams = list(best_odds.keys())
                team_a = teams[0]
                team_b = teams[1]
                
                odd_a = best_odds[team_a]["price"]
                odd_b = best_odds[team_b]["price"]
                
                implied_prob = (1/odd_a) + (1/odd_b)
                
                if implied_prob < 1.0:
                    profit_margin = (1 - implied_prob) / implied_prob
                    opportunities.append({
                        "type": "Arbitrage",
                        "sport": sport_key,
                        "event": event_name,
                        "profit_margin": f"{round(profit_margin * 100, 2)}%",
                        "implied_probability": round(implied_prob, 4),
                        "bet_1": {
                            "team": team_a,
                            "book": best_odds[team_a]["book"],
                            "price": odd_a,
                            "stake_ratio": round((1/odd_a)/implied_prob, 4)
                        },
                        "bet_2": {
                            "team": team_b,
                            "book": best_odds[team_b]["book"],
                            "price": odd_b,
                            "stake_ratio": round((1/odd_b)/implied_prob, 4)
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    })

        return opportunities

    def run(self):
        """Main execution loop."""
        logger.info("Starting Arbitrage Scan...")
        all_arbs = []

        for sport in self.sports:
            odds_data = self.fetch_odds(sport)
            if odds_data:
                arbs = self.find_arbitrage(odds_data)
                if arbs:
                    logger.info(f"FOUND ARBITRAGE in {sport}!")
                    all_arbs.extend(arbs)

        logger.info(f"Scan complete. Found {len(all_arbs)} arbitrage opportunities.")
        return all_arbs

if __name__ == "__main__":
    engine = ArbitrageEngine()
    results = engine.run()
    import json
    print(json.dumps(results, indent=2))
