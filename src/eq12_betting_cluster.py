import json
import time
import logging
from datetime import datetime

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [EQ12 CLUSTER] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/betting_cluster.log"),
        logging.StreamHandler()
    ]
)

class EQ12BettingStrategy:
    def __init__(self):
        self.active_bets = []
        self.balance = 1000.0
        logging.info("Strategy Engine Initialized. Balance: $1000.00")

    def process_signal(self, signal_data):
        """
        Process a signal from an Edge Node (Coral TPU).
        """
        timestamp = signal_data.get("timestamp")
        betting_signal = signal_data.get("betting_signal")
        entities = signal_data.get("detected_entities", [])
        
        logging.info(f"Received Signal: {betting_signal} | Entities: {len(entities)}")

        if betting_signal == "LIVE_PLAY_ACTIVE":
            self.evaluate_live_bet(entities)
        elif betting_signal == "BREAK_OR_TIMEOUT":
            logging.info("Game is paused. No action.")

    def evaluate_live_bet(self, entities):
        # Example Logic: If confidence is high and we haven't bet recently
        # In a real app, this would check odds APIs, etc.
        
        # Calculate average confidence of detection
        scores = [e['score'] for e in entities]
        avg_confidence = sum(scores) / len(scores) if scores else 0
        
        if avg_confidence > 0.6:
            logging.info(f"High confidence ({avg_confidence:.2f}) detected. Placing micro-bet.")
            self.place_bet(amount=10, reason="High Activity Detected")
        else:
            logging.info(f"Confidence low ({avg_confidence:.2f}). Holding.")

    def place_bet(self, amount, reason):
        if self.balance >= amount:
            self.balance -= amount
            bet_id = f"BET-{int(time.time())}"
            self.active_bets.append(bet_id)
            logging.warning(f"$$$ PLACED BET {bet_id} for ${amount} | Reason: {reason} | New Balance: ${self.balance}")
        else:
            logging.error("Insufficient funds.")

if __name__ == "__main__":
    # Simulation Mode
    engine = EQ12BettingStrategy()
    
    print("--- EQ12 SPORTS BETTING CLUSTER LISTENER ---")
    print("Waiting for signals from Edge Nodes (Raspberry Pi)...")
    
    # Simulate receiving a payload (since we don't have a real network listener set up yet)
    mock_payload = {
        "timestamp": time.time(),
        "inference_ms": 12.5,
        "detected_entities": [
            {"id": 0, "label": "person", "score": 0.85, "bbox": [0,0,10,10]},
            {"id": 0, "label": "person", "score": 0.82, "bbox": [20,20,30,30]},
            {"id": 32, "label": "sports ball", "score": 0.75, "bbox": [15,15,18,18]}
        ],
        "betting_signal": "LIVE_PLAY_ACTIVE"
    }
    
    time.sleep(2)
    engine.process_signal(mock_payload)
    
    time.sleep(1)
    mock_payload_2 = {
        "timestamp": time.time(),
        "inference_ms": 11.2,
        "detected_entities": [],
        "betting_signal": "BREAK_OR_TIMEOUT"
    }
    engine.process_signal(mock_payload_2)
