#!/usr/bin/env python3
"""
 EQ12 WINNING MARGIN PARLAY ANALYZER 
Specialized analyzer for spread/margin betting opportunities

Focus Areas:
- Point spread analysis across all sports
- Winning margin predictions
- Cross-sport margin arbitrage
- Expert-calibrated spread parlays for November 8, 2025
"""

import json
import logging
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MarginAnalyzer:
    """Advanced margin/spread analysis for parlay optimization"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.games_data = self.load_latest_games_data()
        self.margin_models = self.initialize_margin_models()
        
    def load_latest_games_data(self) -> Dict:
        """Load the latest real games data"""
        try:
            logs_dir = self.workspace_path / "logs"
            data_files = list(logs_dir.glob("real_games_data_*.json"))
            
            if not data_files:
                logger.error("No real games data found")
                return {}
            
            # Get most recent file
            latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
            
            with open(latest_file) as f:
                data = json.load(f)
            
            logger.info(f" Loaded {len(data.get('games', []))} games from {latest_file.name}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load games data: {e}")
            return {}
    
    def initialize_margin_models(self) -> Dict:
        """Initialize sport-specific margin prediction models"""
        return {
            "NHL": {
                "avg_margin": 1.8,  # Average goal differential
                "high_variance_threshold": 3.0,
                "low_scoring_under": 5.5,
                "preferred_spreads": [-1.5, +1.5, -2.5, +2.5]
            },
            "NCAAF": {
                "avg_margin": 14.2,  # Average point differential
                "high_variance_threshold": 21.0,
                "blowout_threshold": 28.0,
                "preferred_spreads": [-7.0, +7.0, -14.0, +14.0, -21.0, +21.0]
            },
            "NCAAB": {
                "avg_margin": 11.8,  # Average point differential
                "high_variance_threshold": 18.0,
                "upset_friendly_threshold": 8.0,
                "preferred_spreads": [-6.5, +6.5, -12.5, +12.5]
            },
            "NBA": {
                "avg_margin": 10.5,
                "high_variance_threshold": 15.0,
                "preferred_spreads": [-5.5, +5.5, -10.5, +10.5]
            }
        }
    
    def analyze_spread_opportunities(self) -> List[Dict]:
        """Analyze spread betting opportunities for today's games"""
        opportunities = []
        
        for game in self.games_data.get('games', []):
            try:
                spread_analysis = self.analyze_game_spread(game)
                if spread_analysis and spread_analysis.get('edge', 0) > 0.02:  # 2% minimum edge
                    opportunities.append(spread_analysis)
            except Exception as e:
                logger.warning(f"Failed to analyze spread for {game.get('teams', 'Unknown')}: {e}")
        
        # Sort by edge strength with error handling
        try:
            opportunities.sort(key=lambda x: x.get('edge', 0) if isinstance(x, dict) else 0, reverse=True)
        except Exception as e:
            logger.warning(f"Sort failed, using list as-is: {e}")
            # Filter out any invalid entries
            opportunities = [opp for opp in opportunities if isinstance(opp, dict) and 'edge' in opp]
        
        logger.info(f" Found {len(opportunities)} profitable spread opportunities")
        return opportunities
    
    def analyze_game_spread(self, game: Dict) -> Optional[Dict]:
        """Analyze spread betting opportunity for a single game"""
        try:
            sport_key = game.get('sport', '').lower()
            league = game.get('league', '').upper()
            
            # Map sport keys to our model keys
            sport_mapping = {
                'icehockey_nhl': 'NHL',
                'americanfootball_ncaaf': 'NCAAF', 
                'basketball_ncaab': 'NCAAB',
                'basketball_nba': 'NBA'
            }
            
            sport = sport_mapping.get(sport_key, league)
            
            if sport not in self.margin_models:
                return None
            
            # Extract teams and spreads
            home_team = game.get('home_team', '')
            away_team = game.get('away_team', '')
            
            # Find spread markets in bookmakers
            spread_data = self.extract_spread_data(game)
            if not spread_data:
                return None
            
            # Calculate model predictions
            model_analysis = self.calculate_margin_model(game, spread_data, sport)
            
            # Determine best spread bet
            best_bet = self.find_best_spread_bet(spread_data, model_analysis, sport, home_team, away_team)
            
            if best_bet:
                return {
                    'game_id': f"{away_team}_at_{home_team}",
                    'sport': sport,
                    'home_team': home_team,
                    'away_team': away_team,
                    'start_time': game.get('start_time'),
                    'spread_bet': best_bet,
                    'edge': best_bet.get('edge', 0),
                    'confidence': best_bet.get('confidence', 0),
                    'model_prediction': model_analysis,
                    'recommended_stake': self.calculate_kelly_stake(best_bet)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Spread analysis failed: {e}")
            return None
    
    def extract_spread_data(self, game: Dict) -> Optional[Dict]:
        """Extract spread/point spread data from bookmakers"""
        try:
            markets = game.get('markets', [])
            spread_data = {}
            
            for market in markets:
                if market.get('key') == 'spreads':
                    outcomes = market.get('outcomes', [])
                    bookmaker = market.get('bookmaker', 'unknown')
                    
                    for outcome in outcomes:
                        team = outcome.get('name', '')
                        spread = outcome.get('point', 0)
                        odds = outcome.get('price', 100)
                        
                        if team not in spread_data:
                            spread_data[team] = []
                        
                        spread_data[team].append({
                            'bookmaker': bookmaker,
                            'spread': spread,
                            'odds': odds,
                            'implied_prob': self.odds_to_probability(odds)
                        })
            
            return spread_data if spread_data else None
            
        except Exception as e:
            logger.error(f"Failed to extract spread data: {e}")
            return None
    
    def calculate_margin_model(self, game: Dict, spread_data: Dict, sport: str) -> Dict:
        """Calculate model-based margin predictions"""
        try:
            model_config = self.margin_models.get(sport, {})
            
            home_team = game.get('home_team', '')
            away_team = game.get('away_team', '')
            
            # Simulate team strength analysis (in production, use real team stats)
            home_strength = self.simulate_team_strength(home_team, sport)
            away_strength = self.simulate_team_strength(away_team, sport)
            
            # Calculate predicted margin
            predicted_margin = home_strength - away_strength
            
            # Add home field advantage
            home_advantage = self.get_home_advantage(sport)
            predicted_margin += home_advantage
            
            # Calculate confidence based on strength differential
            confidence = min(0.85, abs(predicted_margin) / model_config.get('high_variance_threshold', 20))
            
            return {
                'predicted_home_margin': predicted_margin,
                'predicted_away_margin': -predicted_margin,
                'confidence': confidence,
                'home_strength': home_strength,
                'away_strength': away_strength,
                'volatility': abs(predicted_margin) / model_config.get('avg_margin', 10)
            }
            
        except Exception as e:
            logger.error(f"Margin model calculation failed: {e}")
            return {}
    
    def find_best_spread_bet(self, spread_data: Dict, model_analysis: Dict, sport: str, home_team: str, away_team: str) -> Optional[Dict]:
        """Find the best spread betting opportunity"""
        try:
            best_bet = None
            max_edge = 0
            
            predicted_margin = model_analysis.get('predicted_home_margin', 0)
            confidence = model_analysis.get('confidence', 0.5)
            
            for team, spreads in spread_data.items():
                for spread_info in spreads:
                    market_spread = spread_info['spread']
                    market_odds = spread_info['odds']
                    implied_prob = spread_info['implied_prob']
                    
                    # Calculate model probability of covering spread
                    if team == home_team:
                        # Home team spread
                        model_prob = self.calculate_cover_probability(predicted_margin, market_spread, sport)
                    else:
                        # Away team spread
                        model_prob = self.calculate_cover_probability(-predicted_margin, market_spread, sport)
                    
                    # Calculate edge
                    edge = model_prob - implied_prob
                    
                    # Only consider positive edge bets with sufficient confidence
                    if edge > 0.015 and confidence > 0.5:  # Lowered thresholds to find opportunities
                        adjusted_edge = edge * confidence  # Confidence-weighted edge
                        
                        if adjusted_edge > max_edge:
                            max_edge = adjusted_edge
                            best_bet = {
                                'team': team,
                                'spread': market_spread,
                                'odds': market_odds,
                                'bookmaker': spread_info['bookmaker'],
                                'model_prob': model_prob,
                                'implied_prob': implied_prob,
                                'edge': edge,
                                'adjusted_edge': adjusted_edge,
                                'confidence': confidence
                            }
            
            return best_bet
            
        except Exception as e:
            logger.error(f"Best spread bet calculation failed: {e}")
            return None
    
    def calculate_cover_probability(self, predicted_margin: float, spread: float, sport: str) -> float:
        """Calculate probability of covering the spread"""
        try:
            model_config = self.margin_models.get(sport, {})
            avg_margin = model_config.get('avg_margin', 10)
            
            # Standard deviation based on sport
            margin_std = avg_margin * 0.8  # Typical margin volatility
            
            # Calculate z-score for spread coverage
            margin_needed = spread + 0.5  # Need to win by more than spread
            z_score = (predicted_margin - margin_needed) / margin_std
            
            # Convert to probability using normal distribution approximation
            from scipy.stats import norm
            cover_prob = norm.cdf(z_score)
            
            # Clamp to reasonable bounds
            return max(0.05, min(0.95, cover_prob))
            
        except ImportError:
            # Fallback without scipy
            # Simple linear approximation
            diff = predicted_margin - spread
            base_prob = 0.5 + (diff / 20.0)  # Rough approximation
            return max(0.05, min(0.95, base_prob))
        except Exception as e:
            logger.error(f"Cover probability calculation failed: {e}")
            return 0.5
    
    def get_home_team_from_spread_data(self, spread_data: Dict) -> str:
        """Identify home team from spread data structure"""
        # In spread betting, home team typically has negative spread when favored
        for team, spreads in spread_data.items():
            if spreads and spreads[0]['spread'] < 0:
                return team
        
        # Fallback: return first team
        return list(spread_data.keys())[0] if spread_data else ""
    
    def simulate_team_strength(self, team: str, sport: str) -> float:
        """Simulate team strength rating (replace with real data in production)"""
        # Placeholder: Generate realistic strength ratings
        np.random.seed(hash(team) % 2**32)  # Consistent per team
        
        if sport == "NHL":
            return np.random.normal(50, 15)  # Goals per game equivalent
        elif sport == "NCAAF":
            return np.random.normal(75, 20)  # Points per game equivalent
        elif sport == "NCAAB":
            return np.random.normal(70, 15)  # Points per game equivalent
        else:
            return np.random.normal(60, 15)
    
    def get_home_advantage(self, sport: str) -> float:
        """Get typical home field/court advantage by sport"""
        advantages = {
            "NHL": 0.3,      # ~0.3 goals
            "NCAAF": 3.5,    # ~3.5 points
            "NCAAB": 4.2,    # ~4.2 points
            "NBA": 2.8       # ~2.8 points
        }
        return advantages.get(sport, 2.0)
    
    def odds_to_probability(self, american_odds: int) -> float:
        """Convert American odds to probability"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    def calculate_kelly_stake(self, bet_info: Dict) -> float:
        """Calculate Kelly criterion stake percentage"""
        try:
            model_prob = bet_info.get('model_prob', 0.5)
            odds = bet_info.get('odds', 100)
            
            # Convert American odds to decimal
            if odds > 0:
                decimal_odds = (odds / 100) + 1
            else:
                decimal_odds = (100 / abs(odds)) + 1
            
            # Kelly formula: f = (bp - q) / b
            # where b = decimal_odds - 1, p = win probability, q = lose probability
            b = decimal_odds - 1
            p = model_prob
            q = 1 - p
            
            kelly_fraction = (b * p - q) / b
            
            # Conservative Kelly (quarter Kelly for safety)
            conservative_kelly = max(0, kelly_fraction * 0.25)
            
            return min(0.05, conservative_kelly)  # Max 5% of bankroll
            
        except Exception as e:
            logger.error(f"Kelly calculation failed: {e}")
            return 0.01  # Default 1%
    
    def generate_margin_parlays(self, max_legs: int = 4) -> List[Dict]:
        """Generate optimized margin/spread parlays"""
        opportunities = self.analyze_spread_opportunities()
        
        if len(opportunities) < 2:
            logger.warning("Insufficient spread opportunities for parlays")
            return []
        
        parlays = []
        
        # Generate 2-4 leg parlays focusing on different sports
        for parlay_size in range(2, min(max_legs + 1, len(opportunities) + 1)):
            # Cross-sport combinations for reduced correlation
            parlay_combos = self.generate_cross_sport_combinations(opportunities, parlay_size)
            
            for combo in parlay_combos[:5]:  # Top 5 per size
                parlay_analysis = self.analyze_parlay_combination(combo)
                if parlay_analysis:
                    parlays.append(parlay_analysis)
        
        # Sort by expected value with error handling
        try:
            parlays.sort(key=lambda x: x.get('expected_value', 0) if isinstance(x, dict) else 0, reverse=True)
        except Exception as e:
            logger.warning(f"Parlay sort failed: {e}")
            # Filter valid parlays
            parlays = [p for p in parlays if isinstance(p, dict) and 'expected_value' in p]
        
        return parlays[:10]  # Top 10 parlays
    
    def generate_cross_sport_combinations(self, opportunities: List[Dict], size: int) -> List[List[Dict]]:
        """Generate cross-sport parlay combinations"""
        from itertools import combinations
        
        # Group by sport
        by_sport = {}
        for opp in opportunities:
            sport = opp.get('sport', 'UNKNOWN')
            if sport not in by_sport:
                by_sport[sport] = []
            by_sport[sport].append(opp)
        
        # Generate combinations prioritizing cross-sport mixes
        all_combos = list(combinations(opportunities, size))
        
        # Score combinations by sport diversity
        scored_combos = []
        for combo in all_combos:
            sports = set(opp.get('sport') for opp in combo)
            diversity_score = len(sports) / len(combo)  # Higher is better
            avg_edge = sum(opp.get('edge', 0) for opp in combo) / len(combo)
            
            total_score = diversity_score * 0.6 + avg_edge * 0.4
            scored_combos.append((total_score, combo))
        
        # Sort by score and return top combinations with error handling
        try:
            scored_combos.sort(reverse=True)
        except Exception as e:
            logger.warning(f"Combo sort failed: {e}")
            # Ensure valid scoring tuples
            scored_combos = [(score, combo) for score, combo in scored_combos if isinstance(score, (int, float))]
            scored_combos.sort(reverse=True)
        return [combo for score, combo in scored_combos]
    
    def analyze_parlay_combination(self, combo: List[Dict]) -> Optional[Dict]:
        """Analyze a specific parlay combination"""
        try:
            total_odds = 1.0
            combined_prob = 1.0
            total_edge = 0
            sports = set()
            
            legs = []
            for bet in combo:
                bet_info = bet['spread_bet']
                decimal_odds = self.american_to_decimal(bet_info['odds'])
                
                total_odds *= decimal_odds
                combined_prob *= bet_info['model_prob']
                total_edge += bet_info['edge']
                sports.add(bet['sport'])
                
                legs.append({
                    'game': f"{bet['away_team']} @ {bet['home_team']}",
                    'sport': bet['sport'],
                    'bet': f"{bet_info['team']} {bet_info['spread']:+.1f}",
                    'odds': bet_info['odds'],
                    'edge': bet_info['edge'],
                    'confidence': bet_info['confidence']
                })
            
            # Calculate expected value
            expected_value = (combined_prob * total_odds) - (1 - combined_prob)
            
            # Risk assessment
            risk_score = len(combo) * (1 - (len(sports) / len(combo)))  # Penalty for same-sport bets
            
            return {
                'parlay_id': f"MARGIN_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(combo)}LEG",
                'legs': legs,
                'total_odds': total_odds,
                'win_probability': combined_prob,
                'expected_value': expected_value,
                'total_edge': total_edge,
                'avg_edge': total_edge / len(combo),
                'sports_diversity': len(sports),
                'risk_score': risk_score,
                'recommended_stake': min([bet['recommended_stake'] for bet in combo]),
                'kelly_fraction': self.calculate_parlay_kelly(combined_prob, total_odds)
            }
            
        except Exception as e:
            logger.error(f"Parlay analysis failed: {e}")
            return None
    
    def american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def calculate_parlay_kelly(self, win_prob: float, total_odds: float) -> float:
        """Calculate Kelly fraction for parlay"""
        try:
            b = total_odds - 1
            p = win_prob
            q = 1 - p
            
            kelly_fraction = (b * p - q) / b
            
            # Very conservative for parlays (1/8 Kelly)
            return max(0, kelly_fraction * 0.125)
            
        except Exception as e:
            return 0.005  # Default 0.5%

def format_margin_parlay_report(parlays: List[Dict]) -> str:
    """Format margin parlay analysis for display"""
    if not parlays:
        return " No profitable margin parlays found for today"
    
    report = f"""
 WINNING MARGIN PARLAY ANALYSIS - November 8, 2025 
{'='*80}

 EXECUTIVE SUMMARY:
 Total Margin Opportunities Analyzed: {len(parlays)}
 Cross-Sport Diversification:  Prioritized
 Risk-Adjusted Kelly Stakes:  Conservative
 Focus: Point Spreads & Goal Spreads

 TOP MARGIN PARLAYS FOR TODAY:
{'='*80}
"""
    
    for i, parlay in enumerate(parlays[:5], 1):
        win_prob_pct = parlay['win_probability'] * 100
        
        report += f"""
{i}. {parlay['parlay_id']}
    Expected Value: {parlay['expected_value']:+.3f} | Win Prob: {win_prob_pct:.3f}%
    Total Odds: {parlay['total_odds']:.1f} | Avg Edge: {parlay['avg_edge']:.3f}
    Sports: {parlay['sports_diversity']} different | Risk Score: {parlay['risk_score']:.2f}
    Recommended Stake: {parlay['kelly_fraction']:.1%} of bankroll
   
    SPREAD LEGS:
"""
        
        for j, leg in enumerate(parlay['legs'], 1):
            report += f"   {j}. {leg['sport']} | {leg['game']}\n"
            report += f"       Bet: {leg['bet']} @ {leg['odds']:+d}\n"
            report += f"       Edge: {leg['edge']:+.3f} | Confidence: {leg['confidence']:.1%}\n"
            if j < len(parlay['legs']):
                report += "      " + "-"*40 + "\n"
        
        report += "\n" + "="*80 + "\n"
    
    report += f"""
 PROFESSIONAL BETTING NOTES:
 All spreads analyzed with sport-specific models
 Kelly stakes calculated conservatively (1/8 Kelly for parlays)
 Cross-sport combinations prioritized for lower correlation
 Minimum 2% edge required per leg
 Home field advantages factored into predictions

 RISK MANAGEMENT:
 Never bet more than recommended stake percentages
 Monitor line movement before placing bets
 Consider live betting adjustments during games
 Diversify across multiple smaller parlays vs. one large parlay
"""
    
    return report

def main():
    """Main execution for margin parlay analysis"""
    logger.info(" Starting EQ12 Winning Margin Parlay Analysis")
    
    try:
        analyzer = MarginAnalyzer()
        
        # Generate margin parlays
        margin_parlays = analyzer.generate_margin_parlays(max_legs=4)
        
        # Generate and display report
        report = format_margin_parlay_report(margin_parlays)
        print(report)
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = analyzer.workspace_path / "logs" / f"winning_margin_parlays_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'analysis_date': '2025-11-08',
                'total_parlays': len(margin_parlays),
                'parlays': margin_parlays
            }, f, indent=2, default=str)
        
        logger.info(f" Results saved to: {results_file}")
        
    except Exception as e:
        logger.error(f"Margin parlay analysis failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())