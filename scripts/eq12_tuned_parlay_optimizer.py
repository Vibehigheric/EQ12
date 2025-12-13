#!/usr/bin/env python3
"""
EQ12 Parlay Optimizer - Trained Model Version
Optimized for real Coral Edge TPU model outputs
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import itertools

class TunedParlayOptimizer:
    """Parlay optimizer tuned for trained Coral model outputs"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.reports_path = self.workspace_path / "coral_betting_ai" / "reports"
        
        # Adjusted thresholds for trained models
        self.min_ev_threshold = 1e-10  # Very low threshold for trained models
        self.min_confidence_threshold = 1e-10  # Very low threshold
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def load_latest_predictions(self) -> List[Dict]:
        """Load the most recent Coral predictions"""
        coral_files = list(self.reports_path.glob("coral_results_*.json"))
        if not coral_files:
            self.logger.error("No Coral results found")
            return []
            
        latest_file = max(coral_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_file) as f:
                data = json.load(f)
            bets = data.get('bets', [])
            self.logger.info(f"Loaded {len(bets)} predictions from {latest_file}")
            return bets
        except Exception as e:
            self.logger.error(f"Error loading predictions: {e}")
            return []
            
    def select_top_bets(self, bets: List[Dict], max_bets: int = 20) -> List[Dict]:
        """Select top bets by EV score"""
        # Sort by EV score descending
        sorted_bets = sorted(bets, 
                           key=lambda x: x.get('coral_ev_score', 0), 
                           reverse=True)
        
        top_bets = sorted_bets[:max_bets]
        self.logger.info(f"Selected top {len(top_bets)} bets for parlays")
        
        for i, bet in enumerate(top_bets[:5], 1):
            self.logger.info(f"  {i}. {bet.get('description', 'Unknown')} - "
                           f"EV: {bet.get('coral_ev_score', 0):.8f}")
        
        return top_bets
        
    def create_simple_parlays(self, bets: List[Dict]) -> List[Dict]:
        """Create 2-leg and 3-leg parlays from top bets"""
        parlays = []
        
        # 2-leg parlays
        for combo in itertools.combinations(bets[:10], 2):
            parlay_odds = combo[0].get('odds', 2.0) * combo[1].get('odds', 2.0)
            avg_ev = (combo[0].get('coral_ev_score', 0) + combo[1].get('coral_ev_score', 0)) / 2
            
            parlays.append({
                'legs': list(combo),
                'leg_count': 2,
                'total_odds': parlay_odds,
                'avg_ev': avg_ev,
                'description': f"{combo[0].get('team', 'Team1')} + {combo[1].get('team', 'Team2')}"
            })
            
        # 3-leg parlays  
        for combo in itertools.combinations(bets[:8], 3):
            parlay_odds = combo[0].get('odds', 2.0) * combo[1].get('odds', 2.0) * combo[2].get('odds', 2.0)
            avg_ev = sum(leg.get('coral_ev_score', 0) for leg in combo) / 3
            
            parlays.append({
                'legs': list(combo),
                'leg_count': 3,
                'total_odds': parlay_odds,
                'avg_ev': avg_ev,
                'description': f"{combo[0].get('team', 'T1')} + {combo[1].get('team', 'T2')} + {combo[2].get('team', 'T3')}"
            })
            
        # Sort by average EV
        parlays.sort(key=lambda x: x.get('avg_ev', 0), reverse=True)
        
        self.logger.info(f"Generated {len(parlays)} parlay combinations")
        return parlays[:10]  # Top 10
        
    def save_results(self, parlays: List[Dict]) -> str:
        """Save parlay results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.reports_path / f"tuned_parlays_{timestamp}.json"
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_parlays': len(parlays),
            'parlays': parlays
        }
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        self.logger.info(f"Results saved to {output_file}")
        return str(output_file)


def main():
    optimizer = TunedParlayOptimizer("C:/EQ12")
    
    # Load predictions
    bets = optimizer.load_latest_predictions()
    if not bets:
        print("No predictions available")
        return
        
    # Select top bets
    top_bets = optimizer.select_top_bets(bets)
    
    # Create parlays
    parlays = optimizer.create_simple_parlays(top_bets)
    
    # Save results
    output_file = optimizer.save_results(parlays)
    
    # Display results
    print(f"\n Tuned Parlay Optimization Complete!")
    print(f" Processed {len(bets)} total bets")
    print(f" Selected {len(top_bets)} top bets")
    print(f" Generated {len(parlays)} optimal parlays")
    print(f" Results: {output_file}")
    
    print(f"\n Top 5 Recommended Parlays:")
    for i, parlay in enumerate(parlays[:5], 1):
        print(f"  {i}. {parlay['description']}")
        print(f"     Odds: {parlay['total_odds']:.2f}x | Avg EV: {parlay['avg_ev']:.8f}")


if __name__ == "__main__":
    main()