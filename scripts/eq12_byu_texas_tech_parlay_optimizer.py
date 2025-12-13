#!/usr/bin/env python3
"""
EQ12 BYU vs Texas Tech Parlay Optimizer
Create optimal parlay recommendations for the BYU vs Texas Tech game
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BYUTexasTechParlayOptimizer:
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        
        # Game data from analysis
        self.game_data = {
            'home_team': 'Texas Tech Red Raiders',
            'away_team': 'BYU Cougars',
            'start_time': '2025-11-08T17:08:25Z',
            'moneyline': {
                'BYU Cougars': +385,
                'Texas Tech Red Raiders': -500
            },
            'spreads': {
                'BYU Cougars': {'odds': -110, 'spread': +13.5},
                'Texas Tech Red Raiders': {'odds': -110, 'spread': -13.5}
            },
            'totals': {
                'Over': {'odds': -105, 'total': 50.5},
                'Under': {'odds': -115, 'total': 50.5}
            }
        }
    
    def check_game_status(self) -> str:
        """Check if game has started"""
        try:
            game_time = datetime.fromisoformat(self.game_data['start_time'].replace('Z', '+00:00'))
            current_time = datetime.now(timezone.utc)
            
            time_diff = (current_time - game_time).total_seconds() / 60  # minutes
            
            if time_diff < -30:
                return "PREGAME"
            elif time_diff < 0:
                return "STARTING_SOON"
            elif time_diff < 180:  # Within 3 hours (typical game length)
                return "LIVE"
            else:
                return "COMPLETED"
                
        except Exception as e:
            logger.warning(f"Could not determine game status: {e}")
            return "UNKNOWN"
    
    def calculate_implied_probability(self, odds: int) -> float:
        """Convert American odds to implied probability"""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    
    def calculate_decimal_odds(self, odds: int) -> float:
        """Convert American odds to decimal odds"""
        if odds > 0:
            return (odds / 100) + 1
        else:
            return (100 / abs(odds)) + 1
    
    def analyze_value_bets(self) -> List[Dict]:
        """Analyze value betting opportunities"""
        value_bets = []
        
        # Analyze spreads (most common for parlays)
        for team, data in self.game_data['spreads'].items():
            odds = data['odds']
            spread = data['spread']
            implied_prob = self.calculate_implied_probability(odds)
            
            # For spreads, fair probability is typically around 50%
            # But adjust based on spread size and game dynamics
            if abs(spread) > 10:  # Large spread
                if spread > 0:  # Underdog
                    fair_prob = 0.45  # Underdogs tend to cover large spreads more often
                else:  # Heavy favorite
                    fair_prob = 0.48  # Favorites sometimes don't cover large spreads
            else:
                fair_prob = 0.50
            
            edge = fair_prob - implied_prob
            
            if edge > 0.01:  # 1% edge minimum
                value_bets.append({
                    'bet_type': 'spread',
                    'team': team,
                    'bet': f"{team} {spread:+.1f}",
                    'odds': odds,
                    'implied_prob': implied_prob,
                    'fair_prob': fair_prob,
                    'edge': edge,
                    'decimal_odds': self.calculate_decimal_odds(odds)
                })
        
        # Analyze totals
        for bet_type, data in self.game_data['totals'].items():
            odds = data['odds']
            total = data['total']
            implied_prob = self.calculate_implied_probability(odds)
            
            # Analyze total based on game dynamics
            # Texas Tech heavily favored suggests they'll score a lot
            # BYU as big underdog might keep it lower scoring
            if bet_type == 'Under':
                # Under might have value if BYU struggles offensively
                fair_prob = 0.52  # Slight edge to under in blowout potential
            else:  # Over
                fair_prob = 0.48
            
            edge = fair_prob - implied_prob
            
            if edge > 0.005:  # 0.5% edge minimum for totals
                value_bets.append({
                    'bet_type': 'total',
                    'team': bet_type,
                    'bet': f"{bet_type} {total}",
                    'odds': odds,
                    'implied_prob': implied_prob,
                    'fair_prob': fair_prob,
                    'edge': edge,
                    'decimal_odds': self.calculate_decimal_odds(odds)
                })
        
        # Sort by edge
        value_bets.sort(key=lambda x: x['edge'], reverse=True)
        return value_bets
    
    def create_same_game_parlays(self, value_bets: List[Dict]) -> List[Dict]:
        """Create same-game parlay combinations"""
        parlays = []
        
        if len(value_bets) < 2:
            return parlays
        
        # 2-leg parlays
        for i, bet1 in enumerate(value_bets):
            for j, bet2 in enumerate(value_bets):
                if i != j and self.is_valid_combination(bet1, bet2):
                    parlay = self.calculate_parlay_odds([bet1, bet2])
                    if parlay:
                        parlays.append(parlay)
        
        # 3-leg parlays if we have enough valid bets
        if len(value_bets) >= 3:
            for i, bet1 in enumerate(value_bets):
                for j, bet2 in enumerate(value_bets):
                    for k, bet3 in enumerate(value_bets):
                        if i != j and j != k and i != k:
                            if (self.is_valid_combination(bet1, bet2) and 
                                self.is_valid_combination(bet1, bet3) and 
                                self.is_valid_combination(bet2, bet3)):
                                parlay = self.calculate_parlay_odds([bet1, bet2, bet3])
                                if parlay:
                                    parlays.append(parlay)
        
        # Sort by expected value
        parlays.sort(key=lambda x: x.get('expected_value', 0), reverse=True)
        return parlays[:5]  # Top 5 parlays
    
    def is_valid_combination(self, bet1: Dict, bet2: Dict) -> bool:
        """Check if two bets can be combined in a same-game parlay"""
        # Can't bet both teams on spread
        if (bet1['bet_type'] == 'spread' and bet2['bet_type'] == 'spread'):
            return False
        
        # Can't bet both over and under
        if (bet1['bet_type'] == 'total' and bet2['bet_type'] == 'total'):
            return False
        
        return True
    
    def calculate_parlay_odds(self, bets: List[Dict]) -> Optional[Dict]:
        """Calculate parlay odds and expected value"""
        try:
            total_decimal_odds = 1.0
            combined_prob = 1.0
            total_edge = 0
            
            legs = []
            for bet in bets:
                decimal_odds = bet['decimal_odds']
                fair_prob = bet['fair_prob']
                
                total_decimal_odds *= decimal_odds
                combined_prob *= fair_prob
                total_edge += bet['edge']
                
                legs.append({
                    'bet': bet['bet'],
                    'odds': bet['odds'],
                    'edge': bet['edge']
                })
            
            # Calculate expected value
            expected_value = (combined_prob * total_decimal_odds) - 1
            
            # Kelly criterion for stake sizing
            b = total_decimal_odds - 1
            kelly_fraction = (b * combined_prob - (1 - combined_prob)) / b if b > 0 else 0
            recommended_stake = max(0, min(0.03, kelly_fraction * 0.25))  # Max 3%, quarter Kelly
            
            return {
                'parlay_id': f"BYU_TTU_{datetime.now().strftime('%H%M%S')}_{len(legs)}LEG",
                'legs': legs,
                'total_decimal_odds': total_decimal_odds,
                'american_odds': self.decimal_to_american(total_decimal_odds),
                'win_probability': combined_prob,
                'expected_value': expected_value,
                'avg_edge': total_edge / len(legs),
                'recommended_stake_pct': recommended_stake * 100,
                'game': 'BYU @ Texas Tech'
            }
            
        except Exception as e:
            logger.error(f"Parlay calculation failed: {e}")
            return None
    
    def decimal_to_american(self, decimal_odds: float) -> int:
        """Convert decimal odds to American odds"""
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))
    
    def get_live_recommendations(self) -> Dict:
        """Get recommendations based on game status"""
        game_status = self.check_game_status()
        
        recommendations = {
            'game_status': game_status,
            'recommendations': []
        }
        
        if game_status == "LIVE":
            recommendations['recommendations'] = [
                " Game is currently LIVE - consider live betting opportunities",
                " Monitor in-game momentum shifts",
                " Look for live total adjustments based on scoring pace",
                " First half bets may still be available"
            ]
        elif game_status == "STARTING_SOON":
            recommendations['recommendations'] = [
                " Game starting soon - lock in pregame bets now",
                " Pregame lines offer best value before live adjustments",
                " Same-game parlays are available"
            ]
        elif game_status == "COMPLETED":
            recommendations['recommendations'] = [
                " Game has completed - no betting opportunities available"
            ]
        else:  # PREGAME
            recommendations['recommendations'] = [
                " Game is pregame - full betting menu available",
                " Same-game parlays offer best value",
                " Consider spread + total combinations"
            ]
        
        return recommendations

def format_parlay_report(parlays: List[Dict], value_bets: List[Dict], game_status: str) -> str:
    """Format comprehensive parlay analysis report"""
    
    report = f"""
 BYU vs TEXAS TECH PARLAY ANALYSIS 
{'='*60}

 GAME OVERVIEW:
 Matchup: BYU Cougars @ Texas Tech Red Raiders  
 Status: {game_status}
 Spread: Texas Tech -13.5 (-110) / BYU +13.5 (-110)
 Total: Over/Under 50.5 (-105/-115)  
 Moneyline: Texas Tech -500 / BYU +385

 VALUE BETTING OPPORTUNITIES:
{'='*60}
"""
    
    if value_bets:
        for i, bet in enumerate(value_bets[:3], 1):
            edge_pct = bet['edge'] * 100
            report += f"""
#{i} {bet['bet']} ({bet['odds']:+d})
   Edge: {edge_pct:+.1f}% | Fair Prob: {bet['fair_prob']*100:.1f}%
"""
    else:
        report += "\n No significant value bets identified\n"
    
    if parlays and game_status != "COMPLETED":
        report += f"""

 RECOMMENDED SAME-GAME PARLAYS:
{'='*60}
"""
        
        for i, parlay in enumerate(parlays[:3], 1):
            win_prob_pct = parlay['win_probability'] * 100
            ev_pct = parlay['expected_value'] * 100
            stake_pct = parlay['recommended_stake_pct']
            
            report += f"""
#{i} {parlay['parlay_id']}
{''*40}
 Win Probability: {win_prob_pct:.1f}%
 Expected Value: {ev_pct:+.1f}%
 American Odds: {parlay['american_odds']:+d}
 Recommended Stake: {stake_pct:.1f}% of bankroll
 Average Edge: {parlay['avg_edge']*100:.1f}%

LEGS:
"""
            
            for j, leg in enumerate(parlay['legs'], 1):
                report += f"  {j}. {leg['bet']} ({leg['odds']:+d}) - {leg['edge']*100:.1f}% edge\n"
            
            report += "\n"
    
    if game_status == "LIVE":
        report += f"""
 LIVE GAME STRATEGIES:
{'='*60}
 Monitor scoring pace for live total adjustments
 Watch for momentum shifts affecting spread
 Consider live player props if available
 First half markets may still be open
"""
    elif game_status == "COMPLETED":
        report += f"""
 GAME COMPLETED:
{'='*60}
 No betting opportunities available
 Results will be used for model calibration
"""
    
    report += f"""
 STRATEGIC NOTES:
{'='*60}
 Texas Tech heavily favored (-13.5) suggests blowout potential
 BYU as +385 moneyline underdog offers high payout but low probability
 Under 50.5 might have value in potential blowout scenario
 Same-game parlays reduce correlation risk vs separate games

 RISK MANAGEMENT:
{'='*60}
 Limit total exposure to 2-3% of bankroll
 Consider smaller stakes for 3+ leg parlays
 Monitor line movement if game is live
 Set stop-loss limits for live betting

{'='*60}
"""
    
    return report

def main():
    """Main execution function"""
    logger.info(" Starting BYU vs Texas Tech Parlay Analysis")
    
    optimizer = BYUTexasTechParlayOptimizer()
    
    # Check game status
    game_status = optimizer.check_game_status()
    logger.info(f" Game Status: {game_status}")
    
    # Analyze value bets
    value_bets = optimizer.analyze_value_bets()
    logger.info(f" Found {len(value_bets)} value betting opportunities")
    
    # Create parlays
    parlays = optimizer.create_same_game_parlays(value_bets)
    logger.info(f" Generated {len(parlays)} parlay combinations")
    
    # Generate report
    report = format_parlay_report(parlays, value_bets, game_status)
    print(report)
    
    # Save analysis
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results = {
        'timestamp': timestamp,
        'game_status': game_status,
        'value_bets': value_bets,
        'parlays': parlays,
        'game_data': optimizer.game_data
    }
    
    results_file = optimizer.workspace_path / "logs" / f"byu_texas_tech_parlays_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f" Analysis saved to: {results_file}")

if __name__ == "__main__":
    main()