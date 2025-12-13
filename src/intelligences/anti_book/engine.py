import os
import sys
import logging
import random
from typing import List, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AntiBookEngine")

class AntiBookBehaviorEngine:
    """
    Intelligence #8: Anti-Book Behavior Engine
    Mimics 'Square' (recreational) betting behavior to avoid account limits.
    
    Logic:
    1. Analyze the 'Sharp' bet list.
    2. Inject 'Camouflage' bets (small -EV bets on popular teams/parlays).
    3. Round stake sizes to look natural (e.g., $55 instead of $53.21).
    4. Ensure betting timing isn't purely algorithmic (add jitter).
    """

    def __init__(self):
        self.camouflage_ratio = 0.1 # 1 camo bet for every 10 sharp bets
        self.popular_teams = ["Lakers", "Chiefs", "Yankees", "Cowboys", "Warriors"]

    def mask_activity(self, sharp_bets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes a list of sharp bets and returns a 'masked' list ready for execution.
        """
        logger.info(f"Masking activity for {len(sharp_bets)} sharp bets...")
        
        final_bets = []
        
        # 1. Round Stakes
        for bet in sharp_bets:
            stake = bet.get('recommended_stake', 0)
            if stake > 0:
                # Round to nearest 5 or whole number to look human
                if stake > 100:
                    bet['final_stake'] = round(stake / 5) * 5
                else:
                    bet['final_stake'] = round(stake)
                
                # Avoid weird numbers like $49.00 -> make it $50
                if 48 <= bet['final_stake'] <= 52:
                    bet['final_stake'] = 50
                    
                final_bets.append(bet)

        # 2. Inject Camouflage Bets
        num_camo = max(1, int(len(sharp_bets) * self.camouflage_ratio))
        camo_bets = self._generate_camo_bets(num_camo)
        
        final_bets.extend(camo_bets)
        
        # 3. Shuffle Execution Order (so we don't always bet sharpest first)
        random.shuffle(final_bets)
        
        logger.info(f"Final bet list prepared: {len(final_bets)} bets (including {len(camo_bets)} camo).")
        return final_bets

    def _generate_camo_bets(self, count: int) -> List[Dict[str, Any]]:
        camo = []
        for _ in range(count):
            team = random.choice(self.popular_teams)
            camo.append({
                "type": "CAMOUFLAGE",
                "selection": f"{team} Moneyline",
                "odds": 1.91,
                "edge": "-4.5%", # Intentionally bad/neutral
                "recommended_stake": 10.0, # Small stake
                "final_stake": 10,
                "reason": "Account Health / Camouflage",
                "timestamp": datetime.now().isoformat()
            })
        return camo

if __name__ == "__main__":
    # Mock Input
    mock_bets = [
        {"selection": "Sharp Play 1", "recommended_stake": 53.21},
        {"selection": "Sharp Play 2", "recommended_stake": 121.50},
        {"selection": "Sharp Play 3", "recommended_stake": 22.10}
    ]
    
    engine = AntiBookBehaviorEngine()
    results = engine.mask_activity(mock_bets)
    import json
    print(json.dumps(results, indent=2))
