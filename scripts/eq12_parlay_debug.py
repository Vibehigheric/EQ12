#!/usr/bin/env python3
"""
EQ12 Professional Parlay Engine - Debug Version
Shows probability distributions and parlay generation details

Author: EQ12 GODSTACK
Date: November 8, 2025
"""

import json
import logging
from datetime import datetime
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

from eq12_professional_parlay_engine import ProfessionalParlayEngine
import random


class DebugParlayEngine(ProfessionalParlayEngine):
    """Debug version with detailed probability analysis"""
    
    def analyze_probability_distribution(self, legs):
        """Analyze the probability distribution of available legs"""
        print("\n" + "="*80)
        print(" PROBABILITY DISTRIBUTION ANALYSIS")
        print("="*80)
        
        # Group by probability ranges
        ranges = {
            'Very High (70%+)': [leg for leg in legs if leg.probability >= 0.7],
            'High (50-70%)': [leg for leg in legs if 0.5 <= leg.probability < 0.7],
            'Medium (30-50%)': [leg for leg in legs if 0.3 <= leg.probability < 0.5],
            'Low (15-30%)': [leg for leg in legs if 0.15 <= leg.probability < 0.3],
            'Very Low (<15%)': [leg for leg in legs if leg.probability < 0.15]
        }
        
        total_legs = len(legs)
        for range_name, range_legs in ranges.items():
            count = len(range_legs)
            pct = (count / total_legs * 100) if total_legs > 0 else 0
            print(f"{range_name:20} {count:4d} legs ({pct:5.1f}%)")
            
            # Show sample legs from each range
            if count > 0:
                sample_size = min(3, count)
                samples = random.sample(range_legs, sample_size)
                for leg in samples:
                    sport_icon = {'NHL': '', 'NCAAF': '', 'NCAAB': ''}.get(leg.sport, '')
                    odds_str = f"+{leg.odds}" if leg.odds > 0 else str(leg.odds)
                    print(f"    {sport_icon} {leg.team_or_side:30} ({odds_str:5}) - {leg.probability:.1%}")
                print()
                
        print(f" Total Legs Available: {total_legs}")
        
    def test_parlay_combinations(self, legs, strategy_name):
        """Test various parlay combinations to see what works"""
        strategy = self.strategies[strategy_name]
        print(f"\n{'='*80}")
        print(f" TESTING {strategy.name.upper()} COMBINATIONS")
        print("="*80)
        
        # Filter legs for strategy
        if strategy_name == 'bankroll_builder':
            suitable_legs = [leg for leg in legs if 0.3 <= leg.probability <= 0.7]
        elif strategy_name == 'optimal_growth':
            suitable_legs = [leg for leg in legs if 0.2 <= leg.probability <= 0.5]
        elif strategy_name == 'aggressive':
            suitable_legs = [leg for leg in legs if 0.1 <= leg.probability <= 0.4]
        else:
            suitable_legs = [leg for leg in legs if 0.05 <= leg.probability <= 0.3]
            
        print(f" Suitable legs for {strategy.name}: {len(suitable_legs)}")
        
        if len(suitable_legs) < strategy.legs_range[0]:
            print(f" Not enough suitable legs (need {strategy.legs_range[0]}, have {len(suitable_legs)})")
            return
            
        # Test different leg counts
        for num_legs in range(strategy.legs_range[0], min(strategy.legs_range[1] + 1, len(suitable_legs) + 1)):
            print(f"\n Testing {num_legs}-leg parlays:")
            
            # Try several combinations
            successful_parlays = 0
            for attempt in range(20):  # Try 20 combinations
                # Randomly select legs
                selected_legs = random.sample(suitable_legs, num_legs)
                
                # Calculate metrics
                win_prob = self.calculate_parlay_probability(selected_legs)
                payout = self.calculate_parlay_payout(selected_legs)
                ev = self.calculate_parlay_ev(selected_legs)
                
                # Check if it meets criteria
                meets_prob = strategy.target_win_prob_range[0] <= win_prob <= strategy.target_win_prob_range[1]
                meets_ev = ev >= strategy.ev_floor
                
                if meets_prob and meets_ev:
                    successful_parlays += 1
                    if successful_parlays <= 3:  # Show first 3 successful parlays
                        print(f"   Win Prob: {win_prob:.3%} | Payout: {payout:.1f} | EV: {ev:+.2%}")
                        
            success_rate = (successful_parlays / 20) * 100
            print(f"   Success Rate: {successful_parlays}/20 ({success_rate:.0f}%)")
            
            if successful_parlays > 0:
                print(f"   Found working combinations for {num_legs} legs!")
                break
                
    def run_debug_analysis(self):
        """Run complete debug analysis"""
        print("\n" + "="*100)
        print(" PROFESSIONAL PARLAY ENGINE - DEBUG MODE")
        print("="*100)
        
        # Load data
        games_data = self.load_current_games_data()
        if not games_data:
            print(" No games data available")
            return
            
        # Extract legs
        all_legs = self.extract_betting_legs(games_data)
        if not all_legs:
            print(" No betting legs extracted")
            return
            
        # Analyze probability distribution
        self.analyze_probability_distribution(all_legs)
        
        # Test each strategy
        for strategy_name in ['bankroll_builder', 'optimal_growth', 'aggressive']:
            self.test_parlay_combinations(all_legs, strategy_name)
            
        print("\n" + "="*100)
        print(" DEBUG ANALYSIS COMPLETE")
        print("="*100)


def main():
    debug_engine = DebugParlayEngine("C:\\EQ12")
    debug_engine.run_debug_analysis()


if __name__ == "__main__":
    main()