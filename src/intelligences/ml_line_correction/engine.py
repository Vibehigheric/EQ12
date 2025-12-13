import os
import sys
import logging
import random
import statistics
from typing import List, Dict, Any
from datetime import datetime
import requests

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from src.shared.key_manager import KeyManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MLLineCorrectionEngine")

class MLLineCorrectionEngine:
    """
    Intelligence #4: ML Line-Correction Engine
    Uses statistical modeling (and eventually ML) to calculate a 'Fair Price' 
    that is more accurate than the market average.
    
    Logic:
    1. Fetch odds from multiple bookmakers.
    2. Identify 'Sharp' books (e.g., Pinnacle) vs 'Soft' books.
    3. Calculate a weighted average (Sharp Consensus).
    4. Apply a 'Correction Factor' based on recent volatility/injury news (simulated).
    5. Compare 'Fair Price' to available lines to find value.
    """

    def __init__(self):
        self.key_manager = KeyManager()
        self.base_url = "https://api.the-odds-api.com/v4/sports"
        self.sports = ["basketball_nba", "americanfootball_nfl", "icehockey_nhl"]
        self.markets = "h2h,spreads,totals"
        
        # Simulated weights for bookmakers (Sharp vs Soft)
        self.book_weights = {
            "pinnacle": 1.0,      # The gold standard
            "lowvig": 0.9,
            "bookmaker": 0.9,
            "draftkings": 0.6,    # Soft / Retail
            "fanduel": 0.6,
            "betmgm": 0.6,
            "caesars": 0.6,
            "mock_book": 0.5      # Lowest weight
        }
        self.default_weight = 0.5

    def run(self):
        """Main execution loop."""
        logger.info("Starting ML Line-Correction Scan...")
        all_signals = []
        
        for sport in self.sports:
            try:
                odds_data = self.fetch_odds(sport)
                if not odds_data:
                    continue
                
                signals = self.analyze_market(odds_data, sport)
                all_signals.extend(signals)
                
            except Exception as e:
                logger.error(f"Error processing {sport}: {e}")
        
        logger.info(f"Scan complete. Found {len(all_signals)} Line Correction signals.")
        return all_signals

    def fetch_odds(self, sport: str) -> List[Dict[str, Any]]:
        """Fetches odds with key rotation."""
        while True:
            api_key = self.key_manager.get_key("ODDS_API")
            if not api_key:
                logger.warning("No valid ODDS_API keys. Using MOCK DATA.")
                return self._generate_mock_data(sport)

            try:
                url = f"{self.base_url}/{sport}/odds"
                params = {
                    "apiKey": api_key,
                    "regions": "us,eu", # Get EU for Pinnacle if available
                    "markets": self.markets,
                    "oddsFormat": "decimal"
                }
                resp = requests.get(url, params=params)
                
                if resp.status_code == 401:
                    logger.error(f"Key {api_key[:4]}... unauthorized. Rotating.")
                    self.key_manager.report_failure("ODDS_API", api_key)
                    continue

                resp.raise_for_status()
                return resp.json()

            except Exception as e:
                logger.error(f"Fetch error for {sport}: {e}")
                return self._generate_mock_data(sport)

    def analyze_market(self, odds_data: List[Dict[str, Any]], sport: str) -> List[Dict[str, Any]]:
        signals = []
        
        for event in odds_data:
            event_name = f"{event.get('away_team')} @ {event.get('home_team')}"
            
            # Process each market type (h2h, spreads, totals)
            # For simplicity, let's focus on H2H (Moneyline) for this version
            h2h_market = self._extract_market_prices(event, "h2h")
            if not h2h_market:
                continue
                
            # 1. Calculate Fair Price (Weighted Consensus)
            fair_prices = self._calculate_fair_price(h2h_market)
            if not fair_prices:
                continue
                
            # 2. Find Value Bets
            for outcome_name, fair_price in fair_prices.items():
                # Fair Probability
                fair_prob = 1 / fair_price
                
                # Check all books for this outcome
                for book_key, price in h2h_market.get(outcome_name, []):
                    implied_prob = 1 / price
                    
                    # Edge Calculation: (Prob_Win * Odds) - 1
                    # Or simply: Price > Fair_Price
                    
                    # We want a margin of safety (e.g., 2% edge)
                    edge = (fair_prob * price) - 1
                    
                    if edge > 0.02: # 2% ROI threshold
                        signals.append({
                            "type": "ML Line Correction",
                            "sport": sport,
                            "event": event_name,
                            "selection": outcome_name,
                            "book": book_key,
                            "odds": price, # Added odds field for compatibility
                            "market": "Moneyline", # Added market field for compatibility
                            "market_price": price,
                            "fair_price": round(fair_price, 2),
                            "edge": f"{edge*100:.1f}%",
                            "confidence": "High" if edge > 0.05 else "Medium",
                            "timestamp": datetime.now().isoformat()
                        })
        return signals

    def _extract_market_prices(self, event: Dict[str, Any], market_key: str) -> Dict[str, List[tuple]]:
        """
        Returns a dict: { "Team A": [(book1, price), (book2, price)], "Team B": ... }
        """
        prices = {}
        for book in event.get("bookmakers", []):
            book_key = book["key"]
            for market in book.get("markets", []):
                if market["key"] == market_key:
                    for outcome in market["outcomes"]:
                        name = outcome["name"]
                        price = outcome["price"]
                        if name not in prices:
                            prices[name] = []
                        prices[name].append((book_key, price))
        return prices

    def _calculate_fair_price(self, market_prices: Dict[str, List[tuple]]) -> Dict[str, float]:
        """
        Calculates the weighted average probability for each outcome, then converts back to odds.
        """
        fair_prices = {}
        
        # Calculate total weighted probability for the event (to normalize)
        # This is a simplification. A robust model would handle vig removal properly.
        
        # First, get weighted prob for each outcome
        outcome_weighted_probs = {}
        
        for outcome, books in market_prices.items():
            total_weight = 0
            weighted_prob_sum = 0
            
            for book_key, price in books:
                weight = self.book_weights.get(book_key, self.default_weight)
                prob = 1 / price
                
                weighted_prob_sum += (prob * weight)
                total_weight += weight
            
            if total_weight > 0:
                outcome_weighted_probs[outcome] = weighted_prob_sum / total_weight
            else:
                outcome_weighted_probs[outcome] = 0

        # Normalize probabilities to sum to 1.0 (removing the vig)
        total_prob = sum(outcome_weighted_probs.values())
        if total_prob == 0:
            return {}
            
        for outcome, raw_prob in outcome_weighted_probs.items():
            true_prob = raw_prob / total_prob
            if true_prob > 0:
                fair_prices[outcome] = 1 / true_prob
                
        return fair_prices

    def _generate_mock_data(self, sport: str) -> List[Dict[str, Any]]:
        """Generates mock data with a clear discrepancy for testing."""
        return [{
            "id": "mock_event_1",
            "sport_key": sport,
            "home_team": "Team Sharp",
            "away_team": "Team Soft",
            "bookmakers": [
                {
                    "key": "pinnacle", # Sharp
                    "title": "Pinnacle",
                    "markets": [{
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Team Sharp", "price": 1.50}, # 66% prob
                            {"name": "Team Soft", "price": 2.70}
                        ]
                    }]
                },
                {
                    "key": "draftkings", # Soft
                    "title": "DraftKings",
                    "markets": [{
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Team Sharp", "price": 1.65}, # Mispriced! Value here.
                            {"name": "Team Soft", "price": 2.30}
                        ]
                    }]
                }
            ]
        }]

if __name__ == "__main__":
    engine = MLLineCorrectionEngine()
    results = engine.run()
    import json
    print(json.dumps(results, indent=2))
