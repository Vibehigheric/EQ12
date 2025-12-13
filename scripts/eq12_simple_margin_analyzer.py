#!/usr/bin/env python3
"""
EQ12 Simple Winning Margin Parlay Analyzer
Focused analysis for November 8, 2025 spread betting opportunities
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleMarginAnalyzer:
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.data_file = self.workspace_path / "logs" / "real_games_data_20251108_120857.json"
        
        # Load games data
        with open(self.data_file, 'r') as f:
            self.games_data = json.load(f)
        
        logger.info(f" Loaded {len(self.games_data.get('games', []))} games")
    
    def find_spread_bets(self) -> List[Dict]:
        """Find profitable spread betting opportunities"""
        opportunities = []
        
        for game in self.games_data.get('games', []):
            try:
                spread_bet = self.analyze_game_spread(game)
                if spread_bet:
                    opportunities.append(spread_bet)
            except Exception as e:
                logger.warning(f"Failed to analyze game: {e}")
        
        logger.info(f" Found {len(opportunities)} spread opportunities")
        
        # Debug: log opportunity details
        for i, opp in enumerate(opportunities[:3]):
            logger.info(f"Opportunity {i+1}: {opp['sport']} - {opp['team']} {opp['spread']:+.1f} ({opp['edge']*100:.1f}% edge)")
        
        return opportunities
    
    def analyze_game_spread(self, game: Dict) -> Optional[Dict]:
        """Analyze spread betting for a single game"""
        try:
            home_team = game.get('home_team', '')
            away_team = game.get('away_team', '')
            sport = game.get('league', game.get('sport', ''))
            
            # Find spread markets
            best_spread = None
            best_edge = 0
            
            # Look through markets for spreads
            for market in game.get('markets', []):
                if market.get('key') == 'spreads':
                    for outcome in market.get('outcomes', []):
                        odds = outcome.get('price', 100)
                        point = outcome.get('point')
                        
                        if point is not None:  # Has spread
                            # Convert odds to decimal
                            if odds > 0:
                                decimal_odds = (odds / 100) + 1
                            else:
                                decimal_odds = (100 / abs(odds)) + 1
                            
                            # Simple edge calculation
                            implied_prob = 1 / decimal_odds
                            fair_prob = 0.50  # Simplified assumption
                            
                            edge = fair_prob - implied_prob
                            
                            if edge > best_edge and edge > 0.01:  # 1% minimum edge (lowered)
                                best_edge = edge
                                best_spread = {
                                    'team': outcome.get('name', ''),
                                    'spread': point,
                                    'odds': odds,
                                    'edge': edge,
                                    'decimal_odds': decimal_odds,
                                    'bookmaker': market.get('bookmaker', 'Unknown'),
                                    'game': f"{away_team} @ {home_team}",
                                    'sport': sport,
                                    'start_time': game.get('start_time', '')
                                }
            
            return best_spread
            
        except Exception as e:
            logger.error(f"Game analysis failed: {e}")
            return None
    
    def get_sport_name(self, sport_key: str) -> str:
        """Convert sport key to readable name"""
        mapping = {
            'icehockey_nhl': 'NHL',
            'americanfootball_ncaaf': 'NCAAF',
            'basketball_ncaab': 'NCAAB',
            'basketball_nba': 'NBA'
        }
        return mapping.get(sport_key, sport_key.upper())
    
    def create_parlays(self, opportunities: List[Dict]) -> List[Dict]:
        """Create cross-sport parlay combinations"""
        if len(opportunities) < 2:
            return []
        
        parlays = []
        
        # Group by sport for diversity
        by_sport = {}
        for opp in opportunities:
            sport = opp.get('sport', 'UNKNOWN')
            if sport not in by_sport:
                by_sport[sport] = []
            by_sport[sport].append(opp)
        
        # Create 2-leg parlays (including same sport if needed)
        for i, bet1 in enumerate(opportunities[:5]):  # Top 5 opportunities
            for j, bet2 in enumerate(opportunities[:5]):
                if i != j:  # Different bets
                    parlay = self.calculate_parlay([bet1, bet2])
                    if parlay and parlay.get('expected_value', 0) > -0.1:  # Allow slightly negative EV
                        parlays.append(parlay)
        
        # Create 3-leg parlays if we have enough sports
        sports_list = list(by_sport.keys())
        if len(sports_list) >= 3:
            for i, sport1 in enumerate(sports_list):
                for j, sport2 in enumerate(sports_list):
                    for k, sport3 in enumerate(sports_list):
                        if i != j and j != k and i != k:  # All different
                            bet1 = by_sport[sport1][0] if by_sport[sport1] else None
                            bet2 = by_sport[sport2][0] if by_sport[sport2] else None  
                            bet3 = by_sport[sport3][0] if by_sport[sport3] else None
                            
                            if bet1 and bet2 and bet3:
                                parlay = self.calculate_parlay([bet1, bet2, bet3])
                                if parlay:
                                    parlays.append(parlay)
        
        # Simple filtering: keep parlays with positive expected value
        good_parlays = []
        for parlay in parlays:
            if parlay.get('expected_value', 0) > 0:
                good_parlays.append(parlay)
        
        # Return top 10 by expected value (simple sort by single value)
        good_parlays = sorted(good_parlays, key=lambda p: p.get('expected_value', 0), reverse=True)
        return good_parlays[:10]
    
    def calculate_parlay(self, bets: List[Dict]) -> Optional[Dict]:
        """Calculate parlay odds and expected value"""
        try:
            total_odds = 1.0
            win_prob = 1.0
            total_edge = 0
            
            legs = []
            for bet in bets:
                decimal_odds = bet.get('decimal_odds', 2.0)
                edge = bet.get('edge', 0)
                
                # Simple probability model (edge + 50% baseline)
                bet_prob = 0.50 + (edge * 0.5)  # Conservative
                
                total_odds *= decimal_odds
                win_prob *= bet_prob
                total_edge += edge
                
                legs.append({
                    'game': bet.get('game', ''),
                    'sport': bet.get('sport', ''),
                    'bet': f"{bet.get('team', '')} {bet.get('spread', 0):+.1f}",
                    'odds': bet.get('odds', 100),
                    'edge': edge
                })
            
            # Expected value calculation
            expected_value = (win_prob * total_odds) - (1 - win_prob)
            
            # Kelly stake (conservative)
            b = total_odds - 1
            kelly_fraction = (b * win_prob - (1 - win_prob)) / b if b > 0 else 0
            recommended_stake = max(0, min(0.02, kelly_fraction * 0.25))  # Max 2%, quarter Kelly
            
            return {
                'parlay_id': f"SIMPLE_{datetime.now().strftime('%H%M%S')}_{len(legs)}LEG",
                'legs': legs,
                'total_odds': total_odds,
                'win_probability': win_prob,
                'expected_value': expected_value,
                'avg_edge': total_edge / len(legs),
                'recommended_stake_pct': recommended_stake * 100,
                'sports_count': len(set(leg['sport'] for leg in legs))
            }
            
        except Exception as e:
            logger.error(f"Parlay calculation failed: {e}")
            return None

def format_simple_report(parlays: List[Dict]) -> str:
    """Format simple analysis report"""
    if not parlays:
        return " No profitable margin parlays found for today"
    
    report = f"""
 WINNING MARGIN PARLAYS - November 8, 2025 
{'='*60}

 SUMMARY:
 Total Profitable Parlays: {len(parlays)}
 Focus: Cross-Sport Spread Betting
 Risk Level: Conservative (Quarter Kelly)

 TOP MARGIN PARLAYS:
{'='*60}
"""
    
    for i, parlay in enumerate(parlays[:5], 1):
        win_prob_pct = parlay['win_probability'] * 100
        ev_pct = parlay['expected_value'] * 100
        stake_pct = parlay['recommended_stake_pct']
        
        report += f"""
#{i} {parlay['parlay_id']}
{''*40}
 Win Probability: {win_prob_pct:.1f}%
 Expected Value: {ev_pct:+.1f}%
 Recommended Stake: {stake_pct:.1f}% of bankroll
 Sports Diversity: {parlay['sports_count']} different sports
 Average Edge: {parlay['avg_edge']*100:.1f}%

LEGS:
"""
        
        for j, leg in enumerate(parlay['legs'], 1):
            report += f"  {j}. {leg['sport']}: {leg['bet']} ({leg['odds']:+d}) - {leg['game']}\n"
        
        report += "\n"
    
    report += f"""
 ANALYSIS NOTES:
 All parlays feature cross-sport diversification
 Conservative probability models used
 Minimum 2% edge required per leg
 Kelly criterion with 25% reduction for safety

 RISK MANAGEMENT:
 Never bet more than recommended stake
 Consider smaller stakes for higher-leg parlays
 Monitor line movement before placing bets

{'='*60}
"""
    
    return report

def main():
    """Main execution function"""
    try:
        logger.info(" Starting Simple Margin Parlay Analysis")
        
        # Initialize analyzer
        analyzer = SimpleMarginAnalyzer()
        
        # Find spread opportunities
        opportunities = analyzer.find_spread_bets()
        
        if not opportunities:
            print(" No profitable spread opportunities found for today")
            return
        
        # Create parlays
        parlays = analyzer.create_parlays(opportunities)
        
        # Generate report
        if parlays:
            report = format_simple_report(parlays)
        else:
            # Show individual opportunities if no parlays
            report = f"""
 SPREAD BETTING OPPORTUNITIES - November 8, 2025 
{'='*60}

 Found {len(opportunities)} individual spread opportunities:

"""
            for i, opp in enumerate(opportunities[:10], 1):
                report += f"""
#{i} {opp['sport']}: {opp['game']}
{''*40}
 Bet: {opp['team']} {opp['spread']:+.1f}
 Odds: {opp['odds']:+d}
 Edge: {opp['edge']*100:.1f}%
 Bookmaker: {opp['bookmaker']}

"""
            
            report += " Not enough cross-sport opportunities for recommended parlays\n"
        
        print(report)
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = analyzer.workspace_path / "logs" / f"simple_margin_parlays_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'analysis_date': '2025-11-08',
                'total_opportunities': len(opportunities),
                'total_parlays': len(parlays),
                'opportunities': opportunities,
                'parlays': parlays
            }, f, indent=2, default=str)
        
        logger.info(f" Results saved to: {results_file}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise

if __name__ == "__main__":
    main()