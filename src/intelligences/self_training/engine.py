import os
import sys
import logging
import json
import random
from typing import List, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SelfTrainingEngine")

class SelfTrainingLoop:
    """
    Intelligence #9: Self-Training Loop
    Closes the feedback loop by analyzing past bet results and updating model weights.
    
    Logic:
    1. Read 'Bet History' (simulated log for now).
    2. Calculate ROI per Intelligence Module (e.g., Prop Engine vs Arb Engine).
    3. Adjust 'Confidence Weights' for future predictions.
    4. Output updated configuration.
    """

    def __init__(self, history_file: str = "logs/bet_history.json"):
        self.history_file = history_file
        self.weights_file = "config/intelligence_weights.json"
        
        # Default weights
        self.weights = {
            "line_discrepancy": 1.0,
            "arbitrage": 1.0,
            "prop_tensor": 1.0,
            "ml_line_correction": 1.0
        }

    def run_training_cycle(self):
        """Analyzes history and updates weights."""
        logger.info("Starting Self-Training Cycle...")
        
        history = self._load_history()
        if not history:
            logger.warning("No bet history found. Skipping training.")
            return
            
        performance = self._analyze_performance(history)
        self._update_weights(performance)
        self._save_weights()
        
        logger.info("Training complete. Weights updated.")
        return self.weights

    def _load_history(self) -> List[Dict[str, Any]]:
        # In a real system, this reads from DB/File.
        # We'll simulate some history here if file doesn't exist.
        if not os.path.exists(self.history_file):
            return self._generate_mock_history()
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except:
            return []

    def _generate_mock_history(self):
        """Simulates a history of wins/losses."""
        history = []
        sources = ["line_discrepancy", "arbitrage", "prop_tensor", "ml_line_correction"]
        for _ in range(50):
            source = random.choice(sources)
            # Simulate Prop Tensor being hot (70% win)
            win_prob = 0.7 if source == "prop_tensor" else 0.5
            won = random.random() < win_prob
            history.append({
                "source": source,
                "stake": 50,
                "profit": 45 if won else -50,
                "result": "WIN" if won else "LOSS"
            })
        return history

    def _analyze_performance(self, history: List[Dict[str, Any]]) -> Dict[str, float]:
        stats = {}
        for bet in history:
            src = bet.get('source', 'unknown')
            if src not in stats:
                stats[src] = {"profit": 0, "bets": 0}
            stats[src]["profit"] += bet["profit"]
            stats[src]["bets"] += 1
            
        logger.info("Performance Analysis:")
        for src, data in stats.items():
            logger.info(f"  {src}: ${data['profit']} ({data['bets']} bets)")
            
        return stats

    def _update_weights(self, performance: Dict[str, Any]):
        """Boosts weights for profitable engines, penalizes losers."""
        for src, data in performance.items():
            if src in self.weights:
                if data["profit"] > 0:
                    self.weights[src] *= 1.05 # 5% boost
                else:
                    self.weights[src] *= 0.95 # 5% penalty
                
                # Clamp
                self.weights[src] = max(0.1, min(2.0, self.weights[src]))

    def _save_weights(self):
        os.makedirs(os.path.dirname(self.weights_file), exist_ok=True)
        with open(self.weights_file, 'w') as f:
            json.dump(self.weights, f, indent=2)
        logger.info(f"Saved updated weights to {self.weights_file}")

if __name__ == "__main__":
    engine = SelfTrainingLoop()
    results = engine.run_training_cycle()
    print(json.dumps(results, indent=2))
