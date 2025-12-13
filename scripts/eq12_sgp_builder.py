#!/usr/bin/env python3
"""
EQ12 Same Game Parlay (SGP) Builder
Creates optimized SGP bets targeting specific payout ranges.

Author: EQ12 System
Created: 2025-11-28
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path
import requests
from typing import List, Dict, Tuple, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EQ12SGPBuilder:
    """Build Same Game Parlays with target payout analysis."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.the-odds-api.com/v4"
        
    def get_game_odds(self, sport: str, team1: str, team2: str) -> Optional[Dict]:
        """Get odds for a specific game."""
        url = f"{self.base_url}/sports/{sport}/odds"
        params = {
            'apiKey': self.api_key,
            'regions': 'us',
            'markets': 'h2h,spreads,totals',
            'oddsFormat': 'american'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            games = response.json()
            
            # Find the specific game
            for game in games:
                home = game.get('home_team', '').lower()
                away = game.get('away_team', '').lower()
                t1 = team1.lower()
                t2 = team2.lower()
                
                if (t1 in home or t1 in away) and (t2 in home or t2 in away):
                    logger.info(f"✅ Found game: {game['away_team']} @ {game['home_team']}")
                    logger.info(f"   Commence: {game['commence_time']}")
                    return game
                    
            logger.warning(f"Game not found: {team1} vs {team2}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching odds: {e}")
            return None
    
    def american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal."""
        if american_odds > 0:
            return (american_odds / 100.0) + 1.0
        else:
            return (100.0 / abs(american_odds)) + 1.0
    
    def decimal_to_american(self, decimal_odds: float) -> int:
        """Convert decimal odds to American."""
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1.0) * 100)
        else:
            return int(-100 / (decimal_odds - 1.0))
    
    def calculate_parlay_odds(self, legs: List[int]) -> Tuple[float, int, float]:
        """
        Calculate parlay odds from individual American odds legs.
        Returns: (decimal_odds, american_odds, probability)
        """
        decimal_product = 1.0
        for american_odds in legs:
            decimal_product *= self.american_to_decimal(american_odds)
        
        american_parlay = self.decimal_to_american(decimal_product)
        implied_prob = 1.0 / decimal_product
        
        return decimal_product, american_parlay, implied_prob
    
    def build_sgp_for_target(self, game: Dict, stake: float, 
                            target_min: float, target_max: float) -> List[Dict]:
        """
        Build SGP combinations targeting a payout range.
        """
        sgp_options = []
        
        # Extract available markets from best odds
        home_team = game['home_team']
        away_team = game['away_team']
        
        # Get best odds for each market
        best_odds = {}
        for bookmaker in game.get('bookmakers', []):
            book_name = bookmaker['title']
            
            for market in bookmaker.get('markets', []):
                market_key = market['key']
                
                for outcome in market.get('outcomes', []):
                    outcome_name = outcome['name']
                    odds = outcome['price']
                    point = outcome.get('point')
                    
                    # Create unique key
                    key = f"{market_key}_{outcome_name}"
                    if point:
                        key += f"_{point}"
                    
                    # Store best odds
                    if key not in best_odds or abs(odds) > abs(best_odds[key]['odds']):
                        best_odds[key] = {
                            'market': market_key,
                            'outcome': outcome_name,
                            'odds': odds,
                            'point': point,
                            'book': book_name
                        }
        
        logger.info(f"\n📊 Available markets: {len(best_odds)}")
        
        # Generate SGP combinations
        # Strategy: Mix high-probability and moderate-probability bets
        
        # Define betting strategies by number of legs
        strategies = {
            2: "High Risk - 2 Legs",
            3: "Moderate - 3 Legs", 
            4: "Balanced - 4 Legs",
            5: "Conservative - 5 Legs",
            6: "Very Conservative - 6 Legs"
        }
        
        for num_legs in range(2, 7):
            # Generate combinations
            self._generate_combinations(
                best_odds, home_team, away_team, 
                num_legs, stake, target_min, target_max, 
                sgp_options, strategies[num_legs]
            )
        
        # Sort by expected value (payout / implied_prob)
        sgp_options.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return sgp_options[:10]  # Return top 10
    
    def _generate_combinations(self, best_odds: Dict, home_team: str, 
                               away_team: str, num_legs: int, stake: float,
                               target_min: float, target_max: float,
                               sgp_options: List, strategy_name: str):
        """Generate SGP combinations with specific number of legs."""
        
        # Common winning SGP patterns for NBA
        patterns = []
        
        if num_legs == 2:
            # Aggressive 2-leg parlays
            patterns = [
                ['h2h', 'totals_over'],
                ['h2h', 'totals_under'],
                ['spreads_favorite', 'totals_over'],
                ['spreads_underdog', 'totals_under']
            ]
        
        elif num_legs == 3:
            # Moderate 3-leg parlays (targeting 100:1+ for $500-1000 on $5)
            patterns = [
                ['h2h', 'totals_over', 'spreads_favorite'],
                ['h2h', 'totals_under', 'spreads_underdog'],
                ['spreads_favorite', 'totals_over', 'h2h'],
                ['spreads_underdog', 'totals_under', 'h2h']
            ]
        
        elif num_legs == 4:
            # Balanced 4-leg parlays
            patterns = [
                ['h2h', 'spreads_favorite', 'totals_over', 'h2h'],
                ['h2h', 'spreads_underdog', 'totals_under', 'spreads_underdog']
            ]
        
        elif num_legs == 5:
            # Conservative 5-leg
            patterns = [
                ['h2h', 'spreads_favorite', 'totals_over', 'h2h', 'spreads_favorite']
            ]
        
        elif num_legs == 6:
            # Very conservative 6-leg
            patterns = [
                ['h2h', 'spreads_favorite', 'totals_over', 'h2h', 'spreads_favorite', 'totals_over']
            ]
        
        # Build SGPs from patterns
        for pattern in patterns:
            legs = []
            leg_details = []
            
            for bet_type in pattern:
                # Find matching bet
                matching_bet = self._find_matching_bet(best_odds, bet_type, home_team, away_team)
                if matching_bet:
                    legs.append(matching_bet['odds'])
                    leg_details.append({
                        'market': matching_bet['market'],
                        'outcome': matching_bet['outcome'],
                        'odds': matching_bet['odds'],
                        'point': matching_bet.get('point'),
                        'book': matching_bet['book']
                    })
            
            # Only create SGP if we have all legs
            if len(legs) == num_legs:
                decimal_odds, american_odds, implied_prob = self.calculate_parlay_odds(legs)
                payout = stake * decimal_odds
                profit = payout - stake
                
                # Check if payout is in target range
                if target_min <= profit <= target_max:
                    sgp_options.append({
                        'strategy': strategy_name,
                        'num_legs': num_legs,
                        'legs': leg_details,
                        'parlay_odds_american': american_odds,
                        'parlay_odds_decimal': round(decimal_odds, 2),
                        'stake': stake,
                        'payout': round(payout, 2),
                        'profit': round(profit, 2),
                        'implied_probability': round(implied_prob * 100, 2),
                        'expected_value': round(profit / implied_prob, 2)
                    })
    
    def _find_matching_bet(self, best_odds: Dict, bet_type: str, 
                          home_team: str, away_team: str) -> Optional[Dict]:
        """Find a bet matching the type."""
        
        # Map bet types to market patterns
        if bet_type == 'h2h':
            # Prefer home team (OKC is home, likely favorite)
            for key, bet in best_odds.items():
                if bet['market'] == 'h2h' and home_team in bet['outcome']:
                    return bet
            # Fallback to away
            for key, bet in best_odds.items():
                if bet['market'] == 'h2h' and away_team in bet['outcome']:
                    return bet
        
        elif bet_type == 'spreads_favorite':
            # Find negative spread (favorite)
            spreads = [(k, v) for k, v in best_odds.items() if v['market'] == 'spreads' and v['point'] and v['point'] < 0]
            if spreads:
                return spreads[0][1]
        
        elif bet_type == 'spreads_underdog':
            # Find positive spread (underdog)
            spreads = [(k, v) for k, v in best_odds.items() if v['market'] == 'spreads' and v['point'] and v['point'] > 0]
            if spreads:
                return spreads[0][1]
        
        elif bet_type == 'totals_over':
            for key, bet in best_odds.items():
                if bet['market'] == 'totals' and 'over' in bet['outcome'].lower():
                    return bet
        
        elif bet_type == 'totals_under':
            for key, bet in best_odds.items():
                if bet['market'] == 'totals' and 'under' in bet['outcome'].lower():
                    return bet
        
        return None
    
    def print_sgp_report(self, sgps: List[Dict], team1: str, team2: str):
        """Print formatted SGP report."""
        print("\n" + "="*80)
        print(f"🎯 EQ12 SAME GAME PARLAY BUILDER")
        print("="*80)
        print(f"Game: {team1} @ {team2}")
        print(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("="*80)
        
        for idx, sgp in enumerate(sgps, 1):
            print(f"\n{'='*80}")
            print(f"SGP OPTION #{idx}: {sgp['strategy']}")
            print(f"{'='*80}")
            print(f"Stake: ${sgp['stake']:.2f}")
            print(f"Odds: {sgp['parlay_odds_american']:+d} ({sgp['parlay_odds_decimal']:.2f}x)")
            print(f"Payout: ${sgp['payout']:.2f}")
            print(f"Profit: ${sgp['profit']:.2f}")
            print(f"Win Probability: {sgp['implied_probability']:.2f}%")
            print(f"Expected Value: ${sgp['expected_value']:.2f}")
            print(f"\n📋 LEGS ({sgp['num_legs']}):")
            
            for leg_idx, leg in enumerate(sgp['legs'], 1):
                point_str = f" ({leg['point']:+.1f})" if leg['point'] else ""
                print(f"   {leg_idx}. {leg['outcome']}{point_str} - {leg['odds']:+d} [{leg['book']}]")
        
        print("\n" + "="*80)
        print("⚠️  RISK WARNING:")
        print("   - Parlays are HIGH RISK bets")
        print("   - ALL legs must win for payout")
        print("   - Correlated outcomes may be rejected by sportsbooks")
        print("   - Odds may change before placement")
        print("="*80)


def main():
    parser = argparse.ArgumentParser(description='EQ12 Same Game Parlay Builder')
    parser.add_argument('--sport', default='basketball_nba', help='Sport key (default: basketball_nba)')
    parser.add_argument('--team1', required=True, help='First team (e.g., "Phoenix" or "PHO")')
    parser.add_argument('--team2', required=True, help='Second team (e.g., "Oklahoma" or "OKC")')
    parser.add_argument('--stake', type=float, required=True, help='Bet stake ($)')
    parser.add_argument('--target-min', type=float, required=True, help='Minimum target profit ($)')
    parser.add_argument('--target-max', type=float, required=True, help='Maximum target profit ($)')
    parser.add_argument('--output', help='Output JSON file path')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = os.getenv('ODDS_API_KEY')
    if not api_key:
        logger.error("❌ ODDS_API_KEY environment variable not set")
        sys.exit(1)
    
    # Build SGPs
    builder = EQ12SGPBuilder(api_key)
    
    logger.info(f"🔍 Searching for game: {args.team1} vs {args.team2}")
    game = builder.get_game_odds(args.sport, args.team1, args.team2)
    
    if not game:
        logger.error(f"❌ Game not found: {args.team1} vs {args.team2}")
        sys.exit(1)
    
    logger.info(f"\n🎲 Building SGPs:")
    logger.info(f"   Stake: ${args.stake:.2f}")
    logger.info(f"   Target profit: ${args.target_min:.2f} - ${args.target_max:.2f}")
    
    sgps = builder.build_sgp_for_target(
        game, args.stake, args.target_min, args.target_max
    )
    
    if not sgps:
        logger.warning("⚠️  No SGPs found in target range. Try adjusting targets.")
    else:
        logger.info(f"✅ Generated {len(sgps)} SGP options")
        builder.print_sgp_report(sgps, args.team1, args.team2)
        
        # Save to file
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump({
                    'game': {
                        'away_team': game['away_team'],
                        'home_team': game['home_team'],
                        'commence_time': game['commence_time']
                    },
                    'parameters': {
                        'stake': args.stake,
                        'target_min': args.target_min,
                        'target_max': args.target_max
                    },
                    'sgps': sgps,
                    'generated_at': datetime.now(timezone.utc).isoformat()
                }, f, indent=2)
            
            logger.info(f"✅ Report saved: {output_path}")


if __name__ == '__main__':
    main()
