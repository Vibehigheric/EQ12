import os
import sys
import logging
import time
import random
from datetime import datetime
from typing import List, Dict, Any

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from src.shared.key_manager import KeyManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("LiveMicroSignalEngine")

class LiveMicroSignalEngine:
    """
    Intelligence #5: Live Micro-Signal Engine
    Monitors live game data for rapid line movements and game-state changes.
    Designed for IN-GAME betting.
    
    Logic:
    1. Poll live odds frequently (e.g., every 30s).
    2. Detect 'Steam Moves' (rapid line changes across multiple books).
    3. Detect 'Game State Mismatches' (e.g., Favorite down by 10 early -> Live Line overreaction).
    4. Output 'Micro-Signals' for immediate execution.
    """

    def __init__(self):
        self.key_manager = KeyManager()
        self.base_url = "https://api.the-odds-api.com/v4/sports"
        self.sports = ["basketball_nba", "americanfootball_nfl", "icehockey_nhl"]
        self.markets = "h2h,spreads" # Live markets
        self.poll_interval = 5 # Seconds (simulated for demo, real would be 30s+)
        self.history = {} # Store previous odds to detect movement

    def run_live_monitor(self, duration_seconds: int = 15):
        """Runs the live monitor for a set duration."""
        logger.info(f"Starting Live Micro-Signal Monitor for {duration_seconds} seconds...")
        start_time = time.time()
        
        while (time.time() - start_time) < duration_seconds:
            self._poll_cycle()
            time.sleep(self.poll_interval)
            
        logger.info("Live Monitor session complete.")

    def _poll_cycle(self):
        """One polling cycle across active sports."""
        for sport in self.sports:
            try:
                odds_data = self.fetch_live_odds(sport)
                if not odds_data:
                    continue
                
                signals = self.detect_micro_signals(odds_data, sport)
                if signals:
                    self._broadcast_signals(signals)
                    
            except Exception as e:
                logger.error(f"Error polling {sport}: {e}")

    def fetch_live_odds(self, sport: str) -> List[Dict[str, Any]]:
        """Fetches LIVE odds (simulated if no live games, or real if available)."""
        # In a real scenario, we'd use the 'live' parameter or specific live endpoints.
        # The Odds API 'odds' endpoint returns current lines, which update frequently.
        
        api_key = self.key_manager.get_key("ODDS_API")
        if not api_key:
            return self._generate_mock_live_data(sport)

        try:
            url = f"{self.base_url}/{sport}/odds"
            params = {
                "apiKey": api_key,
                "regions": "us",
                "markets": self.markets,
                "oddsFormat": "decimal",
                "commenceTimeFrom": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") # Only future/live
            }
            # Note: The Odds API free tier doesn't always have low-latency live data.
            # We will simulate "movement" on top of real data or use mock data for the "Micro-Signal" demo.
            
            resp = requests.get(url, params=params)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 401:
                self.key_manager.report_failure("ODDS_API", api_key)
                return self._generate_mock_live_data(sport)
            else:
                return self._generate_mock_live_data(sport)

        except Exception:
            return self._generate_mock_live_data(sport)

    def detect_micro_signals(self, odds_data: List[Dict[str, Any]], sport: str) -> List[Dict[str, Any]]:
        signals = []
        
        for event in odds_data:
            event_id = event["id"]
            event_name = f"{event['away_team']} @ {event['home_team']}"
            
            # Get current best lines
            current_lines = self._get_best_lines(event)
            
            # Compare with history
            if event_id in self.history:
                prev_lines = self.history[event_id]
                
                # Check for movement
                for team, price in current_lines.items():
                    prev_price = prev_lines.get(team)
                    if prev_price:
                        # Detect Steam (Price dropping rapidly = Heavy betting)
                        # e.g., 2.00 -> 1.80 in one cycle
                        if price < (prev_price * 0.95): 
                            signals.append({
                                "type": "STEAM MOVE",
                                "sport": sport,
                                "event": event_name,
                                "selection": team,
                                "old_price": prev_price,
                                "new_price": price,
                                "change": f"{((price - prev_price)/prev_price)*100:.1f}%",
                                "timestamp": datetime.now().isoformat()
                            })
                        
                        # Detect Drift (Price rising rapidly = Fade)
                        if price > (prev_price * 1.05):
                             signals.append({
                                "type": "DRIFT ALERT",
                                "sport": sport,
                                "event": event_name,
                                "selection": team,
                                "old_price": prev_price,
                                "new_price": price,
                                "change": f"+{((price - prev_price)/prev_price)*100:.1f}%",
                                "timestamp": datetime.now().isoformat()
                            })

            # Update history
            self.history[event_id] = current_lines
            
        return signals

    def _get_best_lines(self, event: Dict[str, Any]) -> Dict[str, float]:
        """Extracts best available price for each team."""
        best_lines = {}
        for book in event.get("bookmakers", []):
            for market in book.get("markets", []):
                if market["key"] == "h2h":
                    for outcome in market["outcomes"]:
                        name = outcome["name"]
                        price = outcome["price"]
                        if name not in best_lines or price > best_lines[name]:
                            best_lines[name] = price
        return best_lines

    def _broadcast_signals(self, signals: List[Dict[str, Any]]):
        """Simulates broadcasting signals to the Swarm/Telegram."""
        for sig in signals:
            logger.info(f"⚡ MICRO-SIGNAL: {sig['type']} | {sig['event']} | {sig['selection']} | {sig['old_price']} -> {sig['new_price']}")
            # In real system: TelegramBot.send_message(sig)

    def _generate_mock_live_data(self, sport: str) -> List[Dict[str, Any]]:
        """Generates mock data that changes over time to simulate live action."""
        # We simulate a game where the favorite is losing, causing lines to shift
        base_price_home = 1.50
        base_price_away = 2.60
        
        # Add random volatility
        volatility = random.uniform(-0.1, 0.1)
        
        return [{
            "id": "live_mock_game_1",
            "sport_key": sport,
            "home_team": "Lakers",
            "away_team": "Warriors",
            "bookmakers": [{
                "key": "mock_live_book",
                "markets": [{
                    "key": "h2h",
                    "outcomes": [
                        {"name": "Lakers", "price": round(base_price_home + volatility, 2)},
                        {"name": "Warriors", "price": round(base_price_away - volatility, 2)}
                    ]
                }]
            }]
        }]

if __name__ == "__main__":
    import requests
    engine = LiveMicroSignalEngine()
    engine.run_live_monitor(duration_seconds=10)
