#!/usr/bin/env python3
"""
EQ12 Parlay Optimizer with Coral Edge TPU Acceleration
Builds optimal multi-leg parlays using hardware-accelerated AI

Author: EQ12 Team
Date: November 2, 2025
"""

import argparse
import json
import logging
import itertools
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np


class ParlayOptimizer:
    """Hardware-accelerated parlay optimization using Coral Edge TPU"""
    
    def __init__(self, workspace_path: str, verbose: bool = False):
        self.workspace_path = Path(workspace_path)
        self.feeds_path = self.workspace_path / "coral_betting_ai" / "feeds"
        self.reports_path = self.workspace_path / "coral_betting_ai" / "reports"
        self.logs_path = self.workspace_path / "logs"
        
        self.verbose = verbose
        self.setup_logging()
        
        # Parlay optimization parameters
        self.min_legs = 3
        self.max_legs = 10
        self.min_total_odds = 3.0  # Minimum parlay odds
        self.max_total_odds = 100.0  # Maximum parlay odds
        self.correlation_threshold = 0.3  # Max correlation between legs
        
    def setup_logging(self):
        """Setup logging for parlay optimization"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.logs_path / f"parlay_optimizer_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.DEBUG if self.verbose else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_coral_predictions(self, predictions_file: str = None) -> List[Dict]:
        """Load Coral AI predictions for parlay building"""
        if predictions_file is None:
            # Use latest Coral results
            coral_files = list(self.reports_path.glob("coral_results_*.json"))
            if not coral_files:
                self.logger.error("No Coral AI results found")
                return []
            predictions_file = max(coral_files, key=lambda f: f.stat().st_mtime)
            
        try:
            with open(predictions_file, 'r') as f:
                data = json.load(f)
                
            predictions = data.get('bets', [])
            self.logger.info(f"Loaded {len(predictions)} Coral predictions from {predictions_file}")
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error loading predictions: {e}")
            return []
            
    def filter_high_confidence_bets(self, predictions: List[Dict], 
                                   min_ev: float = 0.1, min_confidence: float = 0.6) -> List[Dict]:
        """Filter bets by EV and confidence thresholds"""
        filtered = []
        
        for bet in predictions:
            ev_score = bet.get('coral_ev_score', 0.0)
            confidence = bet.get('coral_confidence', 0.0)
            
            if ev_score >= min_ev and confidence >= min_confidence:
                # Add parlay-specific metrics
                bet['parlay_weight'] = ev_score * confidence
                bet['risk_adjusted_ev'] = ev_score * (confidence ** 0.5)
                filtered.append(bet)
                
        self.logger.info(f"Filtered to {len(filtered)} high-confidence bets "
                        f"(EV>={min_ev}, Conf>={min_confidence})")
        return filtered
        
    def calculate_parlay_odds(self, bets: List[Dict]) -> float:
        """Calculate total parlay odds from individual bet odds"""
        total_odds = 1.0
        
        for bet in bets:
            # Extract odds from bet data
            odds = self.extract_bet_odds(bet)
            if odds:
                total_odds *= odds
                
        return total_odds
        
    def extract_bet_odds(self, bet: Dict) -> float:
        """Extract decimal odds from bet data"""
        # Try different odds fields
        odds_fields = ['decimal_odds', 'odds', 'price', 'home_odds', 'away_odds']
        
        for field in odds_fields:
            if field in bet and bet[field]:
                try:
                    return float(bet[field])
                except (ValueError, TypeError):
                    continue
                    
        # Default odds if not found
        return 2.0
        
    def calculate_correlation_penalty(self, bets: List[Dict]) -> float:
        """Calculate penalty for correlated bets in parlay"""
        if len(bets) < 2:
            return 0.0
            
        total_penalty = 0.0
        
        for i, bet1 in enumerate(bets):
            for bet2 in bets[i+1:]:
                correlation = self.estimate_bet_correlation(bet1, bet2)
                if correlation > self.correlation_threshold:
                    total_penalty += correlation * 0.5  # Penalty factor
                    
        return total_penalty
        
    def estimate_bet_correlation(self, bet1: Dict, bet2: Dict) -> float:
        """Estimate correlation between two bets"""
        correlation = 0.0
        
        # Same game correlation
        if (bet1.get('game_id') == bet2.get('game_id') and 
            bet1.get('game_id') is not None):
            correlation += 0.4
            
        # Same team correlation
        teams1 = set([bet1.get('home_team', ''), bet1.get('away_team', '')])
        teams2 = set([bet2.get('home_team', ''), bet2.get('away_team', '')])
        if teams1.intersection(teams2):
            correlation += 0.3
            
        # Same sport correlation (weaker)
        if bet1.get('sport') == bet2.get('sport'):
            correlation += 0.1
            
        # Same bet type correlation
        if bet1.get('bet_type') == bet2.get('bet_type'):
            correlation += 0.1
            
        return min(correlation, 1.0)
        
    def calculate_parlay_ev(self, bets: List[Dict]) -> Tuple[float, float]:
        """Calculate expected value and confidence for parlay"""
        if not bets:
            return 0.0, 0.0
            
        # Compound EV calculation
        combined_ev = 1.0
        combined_confidence = 1.0
        
        for bet in bets:
            ev_score = bet.get('coral_ev_score', 0.0)
            confidence = bet.get('coral_confidence', 0.5)
            
            # Convert EV to probability multipliers
            prob_multiplier = 1.0 + (ev_score * 0.1)  # Conservative conversion
            combined_ev *= prob_multiplier
            combined_confidence *= confidence
            
        # Apply correlation penalty
        correlation_penalty = self.calculate_correlation_penalty(bets)
        combined_ev *= (1.0 - correlation_penalty)
        
        # Convert back to EV score
        parlay_ev = combined_ev - 1.0
        parlay_confidence = combined_confidence ** (1.0 / len(bets))  # Geometric mean
        
        return parlay_ev, parlay_confidence
        
    def generate_parlay_combinations(self, bets: List[Dict], 
                                   target_legs: int = 5) -> List[Dict]:
        """Generate optimal parlay combinations"""
        if len(bets) < target_legs:
            self.logger.warning(f"Not enough bets ({len(bets)}) for {target_legs}-leg parlays")
            target_legs = min(len(bets), self.max_legs)
            
        parlays = []
        
        # Generate all combinations of target length
        for combo in itertools.combinations(bets, target_legs):
            parlay_bets = list(combo)
            
            # Calculate parlay metrics
            total_odds = self.calculate_parlay_odds(parlay_bets)
            parlay_ev, parlay_confidence = self.calculate_parlay_ev(parlay_bets)
            
            # Filter by odds range
            if not (self.min_total_odds <= total_odds <= self.max_total_odds):
                continue
                
            # Calculate risk-adjusted score
            risk_adjusted_score = parlay_ev * parlay_confidence * (total_odds ** 0.1)
            
            parlay = {
                'parlay_id': f"parlay_{len(parlays) + 1}",
                'legs': parlay_bets,
                'total_legs': len(parlay_bets),
                'total_odds': total_odds,
                'parlay_ev': parlay_ev,
                'parlay_confidence': parlay_confidence,
                'risk_adjusted_score': risk_adjusted_score,
                'correlation_penalty': self.calculate_correlation_penalty(parlay_bets),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
            parlays.append(parlay)
            
        # Sort by risk-adjusted score
        parlays.sort(key=lambda p: p['risk_adjusted_score'], reverse=True)
        
        self.logger.info(f"Generated {len(parlays)} {target_legs}-leg parlays")
        return parlays
        
    def optimize_multi_leg_parlays(self, predictions: List[Dict]) -> Dict:
        """Generate optimal parlays of different leg counts"""
        filtered_bets = self.filter_high_confidence_bets(predictions)
        
        if len(filtered_bets) < self.min_legs:
            return {
                'error': f'Not enough qualifying bets ({len(filtered_bets)}) for parlays',
                'min_required': self.min_legs
            }
            
        all_parlays = {}
        
        # Generate parlays for different leg counts
        for leg_count in range(self.min_legs, min(len(filtered_bets) + 1, self.max_legs + 1)):
            parlays = self.generate_parlay_combinations(filtered_bets, leg_count)
            
            # Keep top 10 parlays per leg count
            top_parlays = parlays[:10]
            all_parlays[f'{leg_count}_leg'] = top_parlays
            
        # Find overall best parlays
        all_parlay_list = []
        for leg_parlays in all_parlays.values():
            all_parlay_list.extend(leg_parlays)
            
        best_parlays = sorted(all_parlay_list, 
                            key=lambda p: p['risk_adjusted_score'], 
                            reverse=True)[:20]
        
        # Generate summary
        summary = {
            'optimization_summary': {
                'total_input_bets': len(predictions),
                'qualified_bets': len(filtered_bets),
                'parlay_combinations_generated': sum(len(parlays) for parlays in all_parlays.values()),
                'best_parlays_selected': len(best_parlays),
                'optimization_timestamp': datetime.now(timezone.utc).isoformat()
            },
            'parlay_by_legs': all_parlays,
            'top_20_parlays': best_parlays,
            'optimization_parameters': {
                'min_legs': self.min_legs,
                'max_legs': self.max_legs,
                'min_ev_threshold': 0.1,
                'min_confidence_threshold': 0.6,
                'correlation_threshold': self.correlation_threshold
            }
        }
        
        return summary
        
    def save_optimized_parlays(self, results: Dict) -> str:
        """Save optimized parlay results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"optimized_parlays_{timestamp}.json"
        filepath = self.reports_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
            
        # Also save as latest for easy access
        latest_file = self.reports_path / "optimized_parlays_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(results, f, indent=2)
            
        self.logger.info(f"Saved optimized parlays to {filepath}")
        return str(filepath)
        
    def generate_parlay_report(self) -> str:
        """Generate HTML report of optimized parlays"""
        # Load latest parlays
        latest_file = self.reports_path / "optimized_parlays_latest.json"
        
        if not latest_file.exists():
            return "No parlay data available"
            
        with open(latest_file, 'r') as f:
            data = json.load(f)
            
        html_content = self.create_parlay_html_report(data)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_file = self.reports_path / f"parlay_report_{timestamp}.html"
        
        with open(html_file, 'w') as f:
            f.write(html_content)
            
        return str(html_file)
        
    def create_parlay_html_report(self, data: Dict) -> str:
        """Create HTML report for parlay optimization results"""
        top_parlays = data.get('top_20_parlays', [])
        summary = data.get('optimization_summary', {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>EQ12 Coral Parlay Optimization Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #2c3e50; color: white; padding: 15px; }}
        .summary {{ background-color: #ecf0f1; padding: 15px; margin: 10px 0; }}
        .parlay {{ border: 1px solid #ddd; margin: 10px 0; padding: 10px; }}
        .parlay-header {{ background-color: #3498db; color: white; padding: 8px; }}
        .leg {{ margin: 5px 0; padding: 5px; background-color: #f8f9fa; }}
        .metrics {{ display: flex; justify-content: space-around; }}
        .metric {{ text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>EQ12 Coral Parlay Optimization Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    </div>
    
    <div class="summary">
        <h2>Optimization Summary</h2>
        <div class="metrics">
            <div class="metric">
                <h3>{summary.get('total_input_bets', 0)}</h3>
                <p>Input Bets</p>
            </div>
            <div class="metric">
                <h3>{summary.get('qualified_bets', 0)}</h3>
                <p>Qualified Bets</p>
            </div>
            <div class="metric">
                <h3>{summary.get('parlay_combinations_generated', 0)}</h3>
                <p>Combinations Generated</p>
            </div>
            <div class="metric">
                <h3>{len(top_parlays)}</h3>
                <p>Top Parlays</p>
            </div>
        </div>
    </div>
    
    <h2>Top 20 Optimized Parlays</h2>
"""
        
        for i, parlay in enumerate(top_parlays[:20], 1):
            html += f"""
    <div class="parlay">
        <div class="parlay-header">
            <h3>Parlay #{i} - {parlay.get('total_legs', 0)} Legs</h3>
            <div class="metrics">
                <span>Odds: {parlay.get('total_odds', 0):.2f}</span>
                <span>EV: {parlay.get('parlay_ev', 0):.3f}</span>
                <span>Confidence: {parlay.get('parlay_confidence', 0):.3f}</span>
                <span>Score: {parlay.get('risk_adjusted_score', 0):.3f}</span>
            </div>
        </div>
"""
            
            for j, leg in enumerate(parlay.get('legs', []), 1):
                description = leg.get('description', f"Bet {j}")
                ev_score = leg.get('coral_ev_score', 0)
                confidence = leg.get('coral_confidence', 0)
                
                html += f"""
        <div class="leg">
            <strong>Leg {j}:</strong> {description}<br>
            <small>EV: {ev_score:.3f} | Confidence: {confidence:.3f}</small>
        </div>
"""
            
            html += "    </div>\n"
            
        html += """
</body>
</html>
"""
        
        return html


def main():
    parser = argparse.ArgumentParser(description="EQ12 Parlay Optimizer")
    parser.add_argument("--workspace", default="c:/EQ12", help="Workspace path")
    parser.add_argument("--predictions", help="Coral predictions JSON file")
    parser.add_argument("--min-legs", type=int, default=3, help="Minimum parlay legs")
    parser.add_argument("--max-legs", type=int, default=10, help="Maximum parlay legs")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    parser.add_argument("--generate-report", action="store_true", help="Generate HTML report")
    
    args = parser.parse_args()
    
    optimizer = ParlayOptimizer(args.workspace, args.verbose)
    optimizer.min_legs = args.min_legs
    optimizer.max_legs = args.max_legs
    
    # Load predictions
    predictions = optimizer.load_coral_predictions(args.predictions)
    
    if not predictions:
        print("No predictions available for parlay optimization")
        return
        
    # Optimize parlays
    results = optimizer.optimize_multi_leg_parlays(predictions)
    
    if 'error' in results:
        print(f"Optimization error: {results['error']}")
        return
        
    # Save results
    filepath = optimizer.save_optimized_parlays(results)
    
    # Generate report if requested
    if args.generate_report:
        report_file = optimizer.generate_parlay_report()
        print(f"HTML report generated: {report_file}")
        
    # Show summary
    summary = results.get('optimization_summary', {})
    top_parlays = results.get('top_20_parlays', [])
    
    print(f"\nParlay Optimization Complete:")
    print(f"  Input bets: {summary.get('total_input_bets', 0)}")
    print(f"  Qualified bets: {summary.get('qualified_bets', 0)}")
    print(f"  Combinations generated: {summary.get('parlay_combinations_generated', 0)}")
    print(f"  Results saved to: {filepath}")
    
    if top_parlays:
        print(f"\nTop 5 Parlays:")
        for i, parlay in enumerate(top_parlays[:5], 1):
            print(f"  {i}. {parlay['total_legs']}-leg parlay - "
                  f"Odds: {parlay['total_odds']:.2f} - "
                  f"Score: {parlay['risk_adjusted_score']:.3f}")


if __name__ == "__main__":
    main()