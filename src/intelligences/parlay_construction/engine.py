import os
import sys
import logging
import itertools
from typing import List, Dict, Any
from datetime import datetime
from src.core.dns_prefetcher import prefetch_dns

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ParlayEngine")

prefetch_dns()

class ParlayConstructionEngine:
    """
    Intelligence #6: Parlay Construction Engine
    Combines individual +EV bets into correlated parlays to maximize ROI.
    
    Logic:
    1. Accept a list of single bets (Props, ML, Spreads).
    2. Identify correlations (e.g., QB Passing Yards Over + WR Receiving Yards Over).
    3. Construct 2-leg and 3-leg parlays.
    4. Calculate 'True Probability' of the parlay vs 'Book Probability'.
    """

    def __init__(self):
        pass

    def run(self, single_bets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Main execution.
        single_bets: List of dicts with keys: 'event_id', 'selection', 'probability', 'odds', 'type', 'player', 'team'
        """
        logger.info(f"Constructing parlays from {len(single_bets)} single bets...")
        
        # QUANTUM EDGE OPTIMIZATION: Use generator to yield parlays instead of building a massive list
        parlays = []
        
        # Group bets by Event ID to find Same Game Parlays (SGP)
        bets_by_event = {}
        for bet in single_bets:
            eid = bet.get('event_id') or bet.get('event') # Fallback to event name if ID missing
            if eid not in bets_by_event:
                bets_by_event[eid] = []
            bets_by_event[eid].append(bet)
            
        # 1. Construct Same Game Parlays (SGPs)
        for eid, bets in bets_by_event.items():
            if len(bets) >= 2:
                # _build_sgps is now a generator
                for sgp in self._build_sgps(bets):
                    parlays.append(sgp)
                
        # 2. Construct Cross-Sport Parlays (uncorrelated, pure value)
        # Take top 3 highest edge bets from different events
        sorted_bets = sorted(single_bets, key=lambda x: float(x.get('edge', '0').strip('%')), reverse=True)
        if len(sorted_bets) >= 2:
            cross_sport = self._build_cross_sport_parlay(sorted_bets[:3])
            if cross_sport:
                parlays.append(cross_sport)

        logger.info(f"Constructed {len(parlays)} +EV Parlays.")
        return parlays

    def _is_valid_sgp(self, legs: List[str]) -> bool:
        """
        FIX #1: Validates SGP legs to remove impossible or illegal combinations.
        """
        # Remove identical duplicate legs
        if len(set(legs)) != len(legs):
            return False

        # Remove ML + Draw combos (not allowed in US books)
        # "Moneyline" vs "Draw"
        has_draw = any("Draw" in leg for leg in legs)
        has_ml_team = any("Moneyline" in leg and "Draw" not in leg for leg in legs)
        
        if has_draw and has_ml_team:
            return False

        return True

    def _build_sgps(self, bets: List[Dict[str, Any]]):
        """Builds correlated SGPs from a list of bets for the same event. Yields results."""
        seen_sgps = set() # Deduplication set

        # Generate all 2-leg combinations
        for leg1, leg2 in itertools.combinations(bets, 2):
            # Validate SGP before processing
            leg_names = [
                f"{leg1['selection']} ({leg1.get('market', 'Unknown')})",
                f"{leg2['selection']} ({leg2.get('market', 'Unknown')})"
            ]
            
            if not self._is_valid_sgp(leg_names):
                continue

            # Deduplication check
            sgp_hash = hash(tuple(sorted(leg_names)))
            if sgp_hash in seen_sgps:
                continue
            seen_sgps.add(sgp_hash)

            correlation = self._check_correlation(leg1, leg2)
            
            # If positively correlated or neutral with high individual edge
            if correlation >= 0:
                # Calculate combined odds (simplified)
                # In reality, books punish SGPs with worse odds, so we need a correlation bonus to make it worth it.
                
                combined_odds = leg1['odds'] * leg2['odds']
                
                # FIX #4: Sanity check for odds
                if combined_odds > 100: 
                     logging.warning(f"Discarding impossible odds value: {combined_odds}")
                     continue

                # Apply correlation factor to True Probability (boost it)
                # If correlated, the true prob of both hitting is HIGHER than P(A)*P(B)
                
                p1 = self._parse_prob(leg1.get('tensor_prob', leg1.get('implied_prob', '50%')))
                p2 = self._parse_prob(leg2.get('tensor_prob', leg2.get('implied_prob', '50%')))
                
                joint_prob = p1 * p2 * (1 + correlation) # Boost prob by correlation
                
                fair_odds = 1 / joint_prob if joint_prob > 0 else 999
                
                # If Book Odds > Fair Odds, it's a bet
                if combined_odds > fair_odds:
                    # FIX #2: Correct Edge Calculation
                    edge = ((combined_odds / fair_odds) - 1) * 100
                    
                    yield {
                        "type": "Correlated SGP",
                        "event": leg1.get('event'),
                        "legs": leg_names,
                        "odds": round(combined_odds, 2),
                        "fair_odds": round(fair_odds, 2),
                        "edge": f"{edge:.2f}%",
                        "correlation_factor": correlation,
                    }

    def _build_cross_sport_parlay(self, bets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Builds a 'Lotto' parlay from top value bets."""
        combined_odds = 1.0
        joint_prob = 1.0
        legs = []
        
        for bet in bets:
            combined_odds *= bet['odds']
            p = self._parse_prob(bet.get('tensor_prob', bet.get('implied_prob', '50%')))
            joint_prob *= p
            legs.append(f"{bet['selection']} ({bet.get('sport')})")
            
        fair_odds = 1 / joint_prob if joint_prob > 0 else 999
        edge = (combined_odds / fair_odds) - 1
        
        return {
            "type": "Cross-Sport Value Parlay",
            "legs": legs,
            "odds": round(combined_odds, 2),
            "fair_odds": round(fair_odds, 2),
            "edge": f"{edge*100:.1f}%",
            "timestamp": datetime.now().isoformat()
        }

    def _check_correlation(self, leg1: Dict[str, Any], leg2: Dict[str, Any]) -> float:
        """
        Returns a correlation coefficient (-1.0 to 1.0).
        Positive = Good for SGP. Negative = Bad.
        """
        # Example: QB Passing Yards Over + WR Receiving Yards Over = High Correlation
        m1 = leg1.get('market', '')
        m2 = leg2.get('market', '')
        s1 = leg1.get('selection', '')
        s2 = leg2.get('selection', '')
        
        # QB + WR Logic (Simplified)
        if "passing_yards" in m1 and "receiving_yards" in m2:
            # Assuming same team (checked by caller being same event)
            # Ideally check if WR is on QB's team
            return 0.4 # Strong positive correlation
            
        # Over + Over usually slightly correlated in high scoring games
        if "Over" in s1 and "Over" in s2:
            return 0.1
            
        return 0.0

    def _parse_prob(self, prob_str: str) -> float:
        try:
            return float(prob_str.strip('%')) / 100.0
        except:
            return 0.5

if __name__ == "__main__":
    # Mock Input
    mock_bets = [
        {"event_id": "1", "event": "KC @ BUF", "market": "player_passing_yards", "selection": "Josh Allen Over 250", "odds": 1.91, "tensor_prob": "60%"},
        {"event_id": "1", "event": "KC @ BUF", "market": "player_receiving_yards", "selection": "Stefon Diggs Over 70", "odds": 1.91, "tensor_prob": "58%"},
        {"event_id": "2", "event": "LAL @ GSW", "market": "h2h", "selection": "Lakers", "odds": 2.10, "tensor_prob": "52%", "sport": "nba"}
    ]
    
    engine = ParlayConstructionEngine()
    results = engine.run(mock_bets)
    import json
    print(json.dumps(results, indent=2))
