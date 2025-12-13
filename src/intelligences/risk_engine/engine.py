import os
import sys
import logging
from typing import List, Dict, Any
from datetime import datetime

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from src.core.dns_prefetcher import prefetch_dns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RiskEngine")

prefetch_dns()

class RiskEngine:
    """
    Intelligence #7: Capital Allocation / Risk Engine
    Calculates optimal stake sizes using Kelly Criterion and Bankroll Management rules.
    
    Logic:
    1. Input: Total Bankroll, List of Bets (with Edge and Odds).
    2. Apply Fractional Kelly (e.g., Quarter Kelly) to reduce variance.
    3. Apply Max Stake Limits (e.g., never bet > 5% of bankroll).
    4. Output: Recommended Stake ($) for each bet.
    """

    def __init__(self, total_bankroll: float = 1000.0, kelly_fraction: float = 0.25):
        self.bankroll = total_bankroll
        self.kelly_fraction = kelly_fraction
        self.max_stake_pct = 0.05 # Max 5% per bet

    def allocate_capital(self, bets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Augments the bet list with 'recommended_stake'.
        """
        logger.info(f"Allocating capital for {len(bets)} bets. Bankroll: ${self.bankroll}")
        
        allocated_bets = []
        
        for bet in bets:
            # Parse Odds and Edge
            try:
                odds = float(bet.get('odds', 2.0))
                # Edge might be string "5.5%" or float 0.055
                edge_raw = bet.get('edge', '0')
                if isinstance(edge_raw, str):
                    edge = float(edge_raw.strip('%')) / 100.0
                else:
                    edge = float(edge_raw)
                
                # FIX #3: Correct Kelly Formula using Fair Odds if available
                fair_odds = bet.get('fair_odds')
                if fair_odds:
                    p = 1.0 / float(fair_odds)
                else:
                    # Fallback: Derive p from Edge
                    # Edge = (p * odds) - 1  =>  p = (Edge + 1) / odds
                    p = (edge + 1) / odds
                
                q = 1 - p
                b = odds - 1 # Net odds (decimal - 1)
                
                # Kelly Formula: f* = (bp - q) / b
                if b > 0:
                    kelly_full = (b * p - q) / b
                else:
                    kelly_full = 0
                
                # Apply Fractional Kelly
                kelly_stake_pct = max(0, kelly_full * self.kelly_fraction)
                
                # Apply Max Limit
                final_stake_pct = min(kelly_stake_pct, self.max_stake_pct)
                
                stake_amount = self.bankroll * final_stake_pct
                
                # FIX #6: Final Stake Must Always Round DOWN to int
                final_stake = int(stake_amount)
                
                bet['recommended_stake'] = final_stake # Renamed for consistency, but keeping key
                bet['final_stake'] = final_stake       # Explicit key
                bet['kelly_pct'] = f"{kelly_stake_pct*100:.2f}%"
                bet['risk_analysis'] = "Safe" if final_stake_pct < 0.01 else "Aggressive"
                
                allocated_bets.append(bet)
                
            except Exception as e:
                logger.error(f"Error calculating stake for bet {bet}: {e}")
                bet['recommended_stake'] = 0.0
                allocated_bets.append(bet)
                
        return allocated_bets

if __name__ == "__main__":
    # Mock Input
    mock_bets = [
        {"selection": "Team A", "odds": 2.0, "edge": "5.0%"}, # 5% edge at even money
        {"selection": "Team B", "odds": 1.91, "edge": "2.0%"},
        {"selection": "Longshot", "odds": 10.0, "edge": "20.0%"}
    ]
    
    engine = RiskEngine(total_bankroll=5000)
    results = engine.allocate_capital(mock_bets)
    import json
    print(json.dumps(results, indent=2))
