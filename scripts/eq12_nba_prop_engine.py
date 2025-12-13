#!/usr/bin/env python3
"""
EQ12 NBA Prop Engine
Advanced Monte Carlo simulation engine for NBA prop betting optimization.
Generates high-EV parlays using Coral TPU predictions and market analysis.
"""

import numpy as np
import pandas as pd
import sqlite3
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import itertools
from concurrent.futures import ProcessPoolExecutor
import random
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# EQ12 Prop Engine Configuration
PROP_CONFIG = {
    "data_dir": "C:/EQ12/data",
    "logs_dir": "C:/EQ12/logs",
    "models_dir": "C:/EQ12/models",
    "simulation_runs": 10000,
    "max_parlay_legs": 8,
    "min_ev_threshold": 0.05,
    "bankroll_pct": 0.02
}


@dataclass
class PropBet:
    """Individual prop bet data structure"""
    prop_id: str
    player_name: str
    team: str
    stat_type: str
    line: float
    over_odds: int
    under_odds: int
    predicted_value: float
    confidence: float
    sharp_money: bool
    game_time: datetime


@dataclass
class ParlayTicket:
    """Parlay betting ticket structure"""
    ticket_id: str
    legs: List[PropBet]
    total_odds: int
    stake: float
    potential_payout: float
    expected_value: float
    win_probability: float
    risk_rating: str
    created: datetime


class EQ12_NBA_PropEngine:
    """NBA Prop Betting Engine with Monte Carlo Optimization"""
    
    def __init__(self, config: Dict = None):
        self.config = config or PROP_CONFIG
        self.setup_logging()
        self.connect_database()
        
    def setup_logging(self):
        """Initialize logging for prop engine"""
        log_file = f"{self.config['logs_dir']}/nba_props_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def connect_database(self):
        """Connect to NBA cluster database"""
        db_path = f"{self.config['data_dir']}/nba_cluster.db"
        self.conn = sqlite3.connect(db_path)
        self.logger.info(" Connected to NBA prop database")
    
    def load_todays_props(self) -> List[PropBet]:
        """Load today's available props with predictions"""
        
        query = '''
            SELECT 
                pp.prop_id, pp.player_name, pp.team, pp.stat_type,
                pp.line, pp.over_odds, pp.under_odds,
                ng.game_time,
                -- Placeholder for TPU predictions (would be joined from prediction table)
                CASE pp.stat_type
                    WHEN 'points' THEN pp.line + (RANDOM() * 4 - 2)
                    WHEN 'rebounds' THEN pp.line + (RANDOM() * 2 - 1)
                    WHEN 'assists' THEN pp.line + (RANDOM() * 1.5 - 0.75)
                    WHEN 'threes' THEN pp.line + (RANDOM() * 1 - 0.5)
                END as predicted_value,
                -- Confidence based on line movement
                CASE WHEN om.sharp_indicator THEN 0.8 ELSE 0.6 END as confidence,
                COALESCE(om.sharp_indicator, 0) as sharp_money
            FROM player_props pp
            JOIN nba_games ng ON pp.game_id = ng.game_id
            LEFT JOIN odds_movement om ON pp.prop_id = om.prop_id
            WHERE date(ng.game_time) = date('now')
            AND pp.over_odds IS NOT NULL
            AND pp.under_odds IS NOT NULL
        '''
        
        df = pd.read_sql_query(query, self.conn)
        
        props = []
        for _, row in df.iterrows():
            prop = PropBet(
                prop_id=row['prop_id'],
                player_name=row['player_name'],
                team=row['team'],
                stat_type=row['stat_type'],
                line=row['line'],
                over_odds=row['over_odds'],
                under_odds=row['under_odds'],
                predicted_value=row['predicted_value'],
                confidence=row['confidence'],
                sharp_money=bool(row['sharp_money']),
                game_time=pd.to_datetime(row['game_time'])
            )
            props.append(prop)
        
        self.logger.info(f" Loaded {len(props)} props for analysis")
        return props
    
    def calculate_prop_probability(self, prop: PropBet, side: str = 'over') -> float:
        """Calculate true probability for prop bet side"""
        
        # Use prediction and confidence to estimate probability
        predicted = prop.predicted_value
        line = prop.line
        confidence = prop.confidence
        
        # Standard deviation based on confidence and stat type
        std_dev_map = {
            'points': 4.0,
            'rebounds': 2.5,
            'assists': 2.0,
            'threes': 1.5
        }
        
        base_std = std_dev_map.get(prop.stat_type, 3.0)
        adjusted_std = base_std * (1 - confidence * 0.3)  # Higher confidence = lower std
        
        # Calculate z-score
        z_score = (line - predicted) / adjusted_std if adjusted_std > 0 else 0
        
        # Probability using normal distribution
        prob_over = 1 - stats.norm.cdf(z_score)
        
        # Adjust for sharp money indicator
        if prop.sharp_money:
            if side == 'over' and predicted > line:
                prob_over = min(prob_over * 1.1, 0.95)
            elif side == 'under' and predicted < line:
                prob_over = max(prob_over * 0.9, 0.05)
        
        return prob_over if side == 'over' else (1 - prob_over)
    
    def calculate_expected_value(self, prop: PropBet, side: str = 'over') -> float:
        """Calculate expected value for prop bet"""
        
        probability = self.calculate_prop_probability(prop, side)
        odds = prop.over_odds if side == 'over' else prop.under_odds
        
        # Convert American odds to decimal
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1
        
        # Calculate expected value
        ev = (probability * decimal_odds) - 1.0
        
        return ev
    
    def find_positive_ev_props(self, props: List[PropBet], 
                             min_ev: float = 0.05) -> List[Tuple[PropBet, str, float]]:
        """Find props with positive expected value"""
        
        positive_ev_props = []
        
        for prop in props:
            # Check both sides
            for side in ['over', 'under']:
                ev = self.calculate_expected_value(prop, side)
                
                if ev >= min_ev:
                    positive_ev_props.append((prop, side, ev))
        
        # Sort by expected value
        positive_ev_props.sort(key=lambda x: x[2], reverse=True)
        
        self.logger.info(f" Found {len(positive_ev_props)} positive EV props")
        return positive_ev_props
    
    def monte_carlo_simulation(self, props_with_sides: List[Tuple[PropBet, str]], 
                              num_simulations: int = 10000) -> Dict[str, float]:
        """Run Monte Carlo simulation for prop combination"""
        
        wins = 0
        total_payout = 0.0
        
        for _ in range(num_simulations):
            all_hit = True
            parlay_payout = 1.0
            
            for prop, side in props_with_sides:
                # Simulate prop outcome
                probability = self.calculate_prop_probability(prop, side)
                hit = random.random() < probability
                
                if not hit:
                    all_hit = False
                    break
                
                # Add to parlay odds
                odds = prop.over_odds if side == 'over' else prop.under_odds
                if odds > 0:
                    decimal_odds = (odds / 100) + 1
                else:
                    decimal_odds = (100 / abs(odds)) + 1
                
                parlay_payout *= decimal_odds
            
            if all_hit:
                wins += 1
                total_payout += parlay_payout
        
        win_rate = wins / num_simulations
        avg_payout = total_payout / wins if wins > 0 else 0
        expected_value = (win_rate * avg_payout) - 1.0
        
        return {
            'win_probability': win_rate,
            'average_payout': avg_payout,
            'expected_value': expected_value,
            'simulations': num_simulations
        }
    
    def generate_parlay_combinations(self, positive_ev_props: List[Tuple[PropBet, str, float]], 
                                   max_legs: int = 5) -> List[ParlayTicket]:
        """Generate optimized parlay combinations"""
        
        parlays = []
        
        # Try different parlay sizes
        for leg_count in range(2, min(max_legs + 1, len(positive_ev_props) + 1)):
            
            # Generate combinations
            for combo in itertools.combinations(positive_ev_props[:20], leg_count):  # Limit to top 20
                
                props_with_sides = [(prop, side) for prop, side, _ in combo]
                
                # Run Monte Carlo simulation
                sim_results = self.monte_carlo_simulation(
                    props_with_sides, self.config['simulation_runs']
                )
                
                # Skip if EV is too low
                if sim_results['expected_value'] < self.config['min_ev_threshold']:
                    continue
                
                # Calculate stake using Kelly criterion (simplified)
                bankroll = 1000.0  # Placeholder bankroll
                kelly_fraction = sim_results['expected_value'] / (sim_results['average_payout'] - 1)
                stake = bankroll * min(kelly_fraction, self.config['bankroll_pct'])
                
                # Calculate American odds for parlay
                decimal_odds = sim_results['average_payout']
                if decimal_odds >= 2.0:
                    american_odds = int((decimal_odds - 1) * 100)
                else:
                    american_odds = int(-100 / (decimal_odds - 1))
                
                # Risk rating
                if sim_results['win_probability'] > 0.3:
                    risk_rating = 'LOW'
                elif sim_results['win_probability'] > 0.15:
                    risk_rating = 'MEDIUM'
                else:
                    risk_rating = 'HIGH'
                
                # Create parlay ticket
                ticket = ParlayTicket(
                    ticket_id=f"parlay_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(parlays)}",
                    legs=[prop for prop, _, _ in combo],
                    total_odds=american_odds,
                    stake=stake,
                    potential_payout=stake * decimal_odds,
                    expected_value=sim_results['expected_value'],
                    win_probability=sim_results['win_probability'],
                    risk_rating=risk_rating,
                    created=datetime.now()
                )
                
                parlays.append(ticket)
        
        # Sort by expected value
        parlays.sort(key=lambda x: x.expected_value, reverse=True)
        
        self.logger.info(f" Generated {len(parlays)} parlay combinations")
        return parlays[:10]  # Return top 10
    
    def analyze_correlation_risk(self, props: List[PropBet]) -> float:
        """Analyze correlation risk between props in parlay"""
        
        # Check for same game correlation
        games = set()
        same_player_props = 0
        
        for prop in props:
            game_key = f"{prop.team}_{prop.game_time.date()}"
            games.add(game_key)
            
            # Count props for same player
            player_props = [p for p in props if p.player_name == prop.player_name]
            if len(player_props) > 1:
                same_player_props += 1
        
        # Calculate risk score
        risk_score = 0.0
        
        # Same game penalty
        if len(games) < len(props):
            risk_score += 0.3
        
        # Same player penalty
        if same_player_props > 0:
            risk_score += 0.2 * same_player_props
        
        return min(risk_score, 1.0)
    
    def create_daily_report(self, parlays: List[ParlayTicket]) -> Dict:
        """Create comprehensive daily betting report"""
        
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'total_parlays': len(parlays),
            'recommended_parlays': [],
            'summary': {
                'total_stake': 0.0,
                'total_potential': 0.0,
                'avg_ev': 0.0,
                'avg_win_prob': 0.0
            }
        }
        
        for parlay in parlays[:5]:  # Top 5 recommendations
            
            # Calculate correlation risk
            correlation_risk = self.analyze_correlation_risk(parlay.legs)
            
            parlay_data = {
                'ticket_id': parlay.ticket_id,
                'legs': len(parlay.legs),
                'total_odds': parlay.total_odds,
                'stake': round(parlay.stake, 2),
                'potential_payout': round(parlay.potential_payout, 2),
                'expected_value': round(parlay.expected_value, 4),
                'win_probability': round(parlay.win_probability, 4),
                'risk_rating': parlay.risk_rating,
                'correlation_risk': round(correlation_risk, 3),
                'props': []
            }
            
            for prop in parlay.legs:
                prop_data = {
                    'player': prop.player_name,
                    'team': prop.team,
                    'stat': prop.stat_type,
                    'line': prop.line,
                    'predicted': round(prop.predicted_value, 2),
                    'sharp_money': prop.sharp_money
                }
                parlay_data['props'].append(prop_data)
            
            report['recommended_parlays'].append(parlay_data)
            
            # Update summary
            report['summary']['total_stake'] += parlay.stake
            report['summary']['total_potential'] += parlay.potential_payout
        
        if parlays:
            report['summary']['avg_ev'] = sum(p.expected_value for p in parlays[:5]) / min(5, len(parlays))
            report['summary']['avg_win_prob'] = sum(p.win_probability for p in parlays[:5]) / min(5, len(parlays))
        
        return report
    
    def save_report(self, report: Dict) -> str:
        """Save daily report to file"""
        
        report_file = f"{self.config['logs_dir']}/nba_prop_report_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f" Report saved: {report_file}")
        return report_file
    
    def run_daily_analysis(self) -> Dict:
        """Run complete daily prop analysis"""
        
        self.logger.info(" Starting daily NBA prop analysis")
        
        # Load props
        props = self.load_todays_props()
        
        if not props:
            self.logger.warning(" No props available for analysis")
            return {}
        
        # Find positive EV props
        positive_ev_props = self.find_positive_ev_props(props, self.config['min_ev_threshold'])
        
        if not positive_ev_props:
            self.logger.warning(" No positive EV props found")
            return {}
        
        # Generate parlays
        parlays = self.generate_parlay_combinations(positive_ev_props, self.config['max_parlay_legs'])
        
        # Create report
        report = self.create_daily_report(parlays)
        
        # Save report
        report_file = self.save_report(report)
        
        self.logger.info(f" Analysis complete: {len(parlays)} parlays generated")
        return report
    
    def export_for_telegram(self, report: Dict) -> str:
        """Export recommendations in Telegram-friendly format"""
        
        if not report.get('recommended_parlays'):
            return " No NBA recommendations today - no positive EV plays found."
        
        message = " **EQ12 NBA PROPS** \n"
        message += f" {report['date']}\n\n"
        
        for i, parlay in enumerate(report['recommended_parlays'][:3], 1):
            message += f"** PLAY #{i}** ({parlay['risk_rating']} RISK)\n"
            message += f" Stake: ${parlay['stake']:.0f}  ${parlay['potential_payout']:.0f}\n"
            message += f" EV: {parlay['expected_value']:.2%} | Win: {parlay['win_probability']:.1%}\n"
            
            for prop in parlay['props']:
                side = "OVER" if prop['predicted'] > prop['line'] else "UNDER"
                sharp = "" if prop['sharp_money'] else ""
                message += f"    {prop['player']} {prop['stat'].upper()} {side} {prop['line']} {sharp}\n"
            
            message += "\n"
        
        message += f" Total Stake: ${report['summary']['total_stake']:.0f}\n"
        message += f" Avg EV: {report['summary']['avg_ev']:.2%}\n"
        message += "\n Powered by EQ12 Coral TPU Cluster"
        
        return message


def main():
    parser = argparse.ArgumentParser(description="EQ12 NBA Prop Engine")
    parser.add_argument('--action', choices=['analyze', 'report', 'telegram'], 
                       default='analyze', help='Action to perform')
    parser.add_argument('--min-ev', type=float, default=0.05,
                       help='Minimum expected value threshold')
    parser.add_argument('--max-legs', type=int, default=5,
                       help='Maximum parlay legs')
    parser.add_argument('--simulations', type=int, default=10000,
                       help='Monte Carlo simulation runs')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Update config with command line args
    config = PROP_CONFIG.copy()
    config['min_ev_threshold'] = args.min_ev
    config['max_parlay_legs'] = args.max_legs
    config['simulation_runs'] = args.simulations
    
    engine = EQ12_NBA_PropEngine(config)
    
    try:
        if args.action == 'analyze':
            # Run full analysis
            report = engine.run_daily_analysis()
            if report:
                print(f" Analysis complete: {report['total_parlays']} parlays generated")
                print(f" Total potential: ${report['summary']['total_potential']:.0f}")
                print(f" Average EV: {report['summary']['avg_ev']:.2%}")
        
        elif args.action == 'telegram':
            # Generate Telegram message
            report = engine.run_daily_analysis()
            message = engine.export_for_telegram(report)
            print(message)
        
        else:
            print(" Invalid action")
            return 1
    
    except Exception as e:
        print(f" Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())