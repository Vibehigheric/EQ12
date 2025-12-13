#!/usr/bin/env python3
"""
EQ12 Professional Parlay Engine with Tiered Strategy Framework
Implements quant-based win-probability targets and Kelly criterion staking

Author: EQ12 GODSTACK
Date: November 8, 2025
"""

import json
import logging
import argparse
import math
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import random


@dataclass
class ParlayLeg:
    """Individual bet leg in a parlay"""
    game: str
    sport: str
    bet_type: str  # 'spread', 'moneyline', 'total'
    team_or_side: str
    line: float
    odds: int
    probability: float
    edge: float
    
    
@dataclass
class ParlayStrategy:
    """Strategy tier configuration"""
    name: str
    legs_range: Tuple[int, int]
    target_win_prob_range: Tuple[float, float]
    payout_range: Tuple[int, int]
    description: str
    kelly_fraction: float
    ev_floor: float


class ProfessionalParlayEngine:
    """
    Professional-grade parlay engine with tiered strategy framework
    Based on quant betting principles and Kelly criterion optimization
    """
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.logs_dir = self.workspace_path / "logs"
        self.data_dir = self.workspace_path / "data"
        
        # Setup logging
        self.setup_logging()
        
        # Define strategy tiers per professional recommendation
        self.strategies = {
            'bankroll_builder': ParlayStrategy(
                name="Bankroll Builder (Low Risk)",
                legs_range=(3, 4),
                target_win_prob_range=(0.08, 0.15),  # 8-15%
                payout_range=(6, 12),
                description="Consistent daily plays, small variance",
                kelly_fraction=0.15,  # Conservative Kelly
                ev_floor=0.03
            ),
            'optimal_growth': ParlayStrategy(
                name="Optimal Growth (Moderate Risk)",
                legs_range=(6, 8),
                target_win_prob_range=(0.008, 0.015),  # 0.8-1.5%
                payout_range=(100, 300),
                description="Best balance between hit rate and profit curve",
                kelly_fraction=0.25,  # Quarter-Kelly for stability
                ev_floor=0.05
            ),
            'aggressive': ParlayStrategy(
                name="Aggressive (High Risk)",
                legs_range=(9, 12),
                target_win_prob_range=(0.0005, 0.005),  # 0.05-0.5%
                payout_range=(500, 2000),
                description="Big-payout moonshots, limit to 1-2 tickets/day",
                kelly_fraction=0.10,  # Reduced Kelly for high variance
                ev_floor=0.08
            ),
            'simulation': ParlayStrategy(
                name="Simulation / Showcase (Extreme)",
                legs_range=(15, 20),
                target_win_prob_range=(0.0001, 0.0001),  # <0.01%
                payout_range=(10000, 50000),
                description="Data testing only; not sustainable live play",
                kelly_fraction=0.05,  # Minimal Kelly
                ev_floor=0.15
            )
        }
        
        # Professional default target (recommended sweet spot)
        self.default_strategy = 'optimal_growth'
        
        self.logger.info(" Professional Parlay Engine initialized with tiered strategy framework")
        
    def setup_logging(self):
        """Setup comprehensive logging system"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"professional_parlay_engine_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def american_to_decimal(self, odds: int) -> float:
        """Convert American odds to decimal odds"""
        if odds > 0:
            return (odds / 100) + 1
        else:
            return (100 / abs(odds)) + 1
            
    def calculate_implied_probability(self, odds: int) -> float:
        """Calculate implied probability from American odds"""
        decimal_odds = self.american_to_decimal(odds)
        return 1 / decimal_odds
        
    def calculate_true_probability(self, odds: int, edge: float) -> float:
        """Calculate true probability accounting for edge"""
        implied_prob = self.calculate_implied_probability(odds)
        # If we have positive edge, true probability is higher than implied
        return implied_prob * (1 + edge)
        
    def calculate_parlay_probability(self, legs: List[ParlayLeg]) -> float:
        """Calculate total parlay win probability"""
        total_prob = 1.0
        for leg in legs:
            total_prob *= leg.probability
        return total_prob
        
    def calculate_parlay_payout(self, legs: List[ParlayLeg]) -> float:
        """Calculate parlay payout multiplier"""
        total_odds = 1.0
        for leg in legs:
            decimal_odds = self.american_to_decimal(leg.odds)
            total_odds *= decimal_odds
        return total_odds
        
    def calculate_parlay_ev(self, legs: List[ParlayLeg]) -> float:
        """Calculate expected value of parlay"""
        win_prob = self.calculate_parlay_probability(legs)
        payout = self.calculate_parlay_payout(legs)
        ev = (win_prob * payout) - 1
        return ev
        
    def kelly_stake_size(self, legs: List[ParlayLeg], bankroll: float, strategy: ParlayStrategy) -> float:
        """Calculate optimal stake using Kelly criterion"""
        ev = self.calculate_parlay_ev(legs)
        if ev <= 0:
            return 0
            
        win_prob = self.calculate_parlay_probability(legs)
        payout = self.calculate_parlay_payout(legs)
        
        # Kelly formula: f = (bp - q) / b
        # where b = odds-1, p = win prob, q = lose prob
        b = payout - 1
        p = win_prob
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        
        # Apply strategy-specific Kelly fraction multiplier for safety
        adjusted_kelly = kelly_fraction * strategy.kelly_fraction
        
        # Cap at reasonable percentage of bankroll
        max_stake_pct = 0.05  # Never risk more than 5% on single parlay
        final_stake_pct = min(adjusted_kelly, max_stake_pct)
        
        return max(0, final_stake_pct * bankroll)
        
    def load_current_games_data(self) -> List[Dict]:
        """Load current games data from latest file"""
        data_files = list(self.data_dir.glob("real_games_data_*.json"))
        if not data_files:
            # Fallback to logs directory
            data_files = list(self.logs_dir.glob("real_games_data_*.json"))
            
        if not data_files:
            self.logger.error(" No games data files found")
            return []
            
        # Get most recent file
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        
        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            # Handle different data formats
            if isinstance(data, dict) and 'games' in data:
                games_data = data['games']
            elif isinstance(data, list):
                games_data = data
            else:
                self.logger.error(" Unexpected data format")
                return []
                
            self.logger.info(f" Loaded {len(games_data)} games from {latest_file.name}")
            return games_data
        except Exception as e:
            self.logger.error(f" Error loading games data: {e}")
            return []
            
    def extract_betting_legs(self, games_data: List[Dict]) -> List[ParlayLeg]:
        """Extract all available betting legs from games data"""
        legs = []
        
        for game in games_data:
            try:
                sport = game.get('sport', 'Unknown')
                # Map sport codes to readable names
                sport_map = {
                    'icehockey_nhl': 'NHL',
                    'americanfootball_ncaaf': 'NCAAF', 
                    'basketball_ncaab': 'NCAAB'
                }
                sport_display = sport_map.get(sport, sport)
                
                game_title = f"{game.get('away_team', 'Away')} @ {game.get('home_team', 'Home')}"
                
                # Process markets from the new data structure
                markets = game.get('markets', [])
                
                for market in markets:
                    market_key = market.get('key', '')
                    outcomes = market.get('outcomes', [])
                    
                    if market_key == 'spreads' and len(outcomes) >= 2:
                        for outcome in outcomes:
                            price = outcome.get('price', 0)
                            point = outcome.get('point', 0)
                            team = outcome.get('name', '')
                            
                            if price != 0:
                                # Calculate edge (simplified - real system would use more sophisticated edge detection)
                                implied_prob = self.calculate_implied_probability(price)
                                edge = 0.05 if price > 0 else 0.02
                                true_prob = min(implied_prob * (1 + edge), 0.95)  # Cap at 95%
                                
                                leg = ParlayLeg(
                                    game=game_title,
                                    sport=sport_display,
                                    bet_type='spread',
                                    team_or_side=f"{team} {point:+.1f}",
                                    line=point,
                                    odds=price,
                                    probability=true_prob,
                                    edge=edge
                                )
                                legs.append(leg)
                    
                    elif market_key == 'totals' and len(outcomes) >= 2:
                        for outcome in outcomes:
                            price = outcome.get('price', 0)
                            point = outcome.get('point', 0)
                            side = outcome.get('name', '')  # 'Over' or 'Under'
                            
                            if price != 0:
                                implied_prob = self.calculate_implied_probability(price)
                                edge = 0.03 if price > 0 else 0.01
                                true_prob = min(implied_prob * (1 + edge), 0.95)
                                
                                leg = ParlayLeg(
                                    game=game_title,
                                    sport=sport_display,
                                    bet_type='total',
                                    team_or_side=f"{side} {point}",
                                    line=point,
                                    odds=price,
                                    probability=true_prob,
                                    edge=edge
                                )
                                legs.append(leg)
                                
                    elif market_key == 'h2h' and len(outcomes) >= 2:
                        for outcome in outcomes:
                            price = outcome.get('price', 0)
                            team = outcome.get('name', '')
                            
                            if price != 0:
                                implied_prob = self.calculate_implied_probability(price)
                                edge = 0.04 if price > 0 else 0.01
                                true_prob = min(implied_prob * (1 + edge), 0.95)
                                
                                leg = ParlayLeg(
                                    game=game_title,
                                    sport=sport_display,
                                    bet_type='moneyline',
                                    team_or_side=team,
                                    line=0,
                                    odds=price,
                                    probability=true_prob,
                                    edge=edge
                                )
                                legs.append(leg)
                        
            except Exception as e:
                self.logger.warning(f" Error processing game: {e}")
                continue
                
        self.logger.info(f" Extracted {len(legs)} betting legs from {len(games_data)} games")
        return legs
        
    def generate_strategy_parlays(self, legs: List[ParlayLeg], strategy_name: str, 
                                count: int = 5) -> List[Dict]:
        """Generate parlays for specific strategy tier"""
        strategy = self.strategies[strategy_name]
        parlays = []
        
        # Filter legs by probability range suitable for strategy
        if strategy_name == 'bankroll_builder':
            # Want higher probability legs (favorites, lower odds)
            suitable_legs = [leg for leg in legs if 0.3 <= leg.probability <= 0.7]
        elif strategy_name == 'optimal_growth':
            # Want moderate probability legs (solid underdogs, plus money)
            suitable_legs = [leg for leg in legs if 0.2 <= leg.probability <= 0.5]
        elif strategy_name == 'aggressive':
            # Want lower probability legs (big underdogs, high odds)
            suitable_legs = [leg for leg in legs if 0.1 <= leg.probability <= 0.4]
        else:  # simulation
            # Want very low probability legs (extreme underdogs)
            suitable_legs = [leg for leg in legs if 0.05 <= leg.probability <= 0.3]
            
        if len(suitable_legs) < strategy.legs_range[0]:
            self.logger.warning(f" Not enough suitable legs for {strategy.name}")
            return []
            
        # Generate parlays with more attempts for harder strategies
        attempts = 100 if strategy_name in ['bankroll_builder'] else 500
        
        for i in range(attempts):
            # Random number of legs within strategy range
            num_legs = random.randint(strategy.legs_range[0], strategy.legs_range[1])
            
            # Randomly select legs (ensuring no duplicate games)
            selected_legs = []
            used_games = set()
            leg_attempts = 0
            
            while len(selected_legs) < num_legs and leg_attempts < 200:
                leg = random.choice(suitable_legs)
                if leg.game not in used_games:
                    selected_legs.append(leg)
                    used_games.add(leg.game)
                leg_attempts += 1
                
            if len(selected_legs) < num_legs:
                continue
                
            # Calculate parlay metrics
            win_prob = self.calculate_parlay_probability(selected_legs)
            payout = self.calculate_parlay_payout(selected_legs)
            ev = self.calculate_parlay_ev(selected_legs)
            
            # Check if parlay meets strategy criteria
            if (strategy.target_win_prob_range[0] <= win_prob <= strategy.target_win_prob_range[1] and
                ev >= strategy.ev_floor):
                
                parlay = {
                    'strategy': strategy.name,
                    'legs': selected_legs,
                    'win_probability': win_prob,
                    'payout_multiplier': payout,
                    'expected_value': ev,
                    'kelly_fraction': strategy.kelly_fraction,
                    'legs_count': len(selected_legs)
                }
                parlays.append(parlay)
                
                # Stop once we have enough parlays
                if len(parlays) >= count:
                    break
                
        self.logger.info(f" Generated {len(parlays)} {strategy.name} parlays")
        return parlays
        
    def format_parlay_display(self, parlay: Dict, bankroll: float = 1000) -> str:
        """Format parlay for display with professional metrics"""
        strategy = next(s for s in self.strategies.values() if s.name == parlay['strategy'])
        stake = self.kelly_stake_size(parlay['legs'], bankroll, strategy)
        
        output = []
        output.append(f"\n{'='*80}")
        output.append(f" {parlay['strategy'].upper()}")
        output.append(f"{'='*80}")
        output.append(f" Win Probability: {parlay['win_probability']:.3%}")
        output.append(f" Payout: {parlay['payout_multiplier']:.1f}")
        output.append(f" Expected Value: {parlay['expected_value']:+.2%}")
        output.append(f" Legs: {parlay['legs_count']}")
        output.append(f" Recommended Stake: ${stake:.2f} ({stake/bankroll:.2%} of bankroll)")
        output.append(f" Potential Win: ${stake * parlay['payout_multiplier']:.2f}")
        output.append("")
        
        # Show individual legs
        for i, leg in enumerate(parlay['legs'], 1):
            sport_icon = {'NHL': '', 'NCAAF': '', 'NCAAB': ''}.get(leg.sport, '')
            odds_str = f"+{leg.odds}" if leg.odds > 0 else str(leg.odds)
            output.append(f"  {i}. {sport_icon} {leg.team_or_side} ({odds_str}) - {leg.probability:.1%} | {leg.game}")
            
        output.append("")
        return "\n".join(output)
        
    def run_professional_analysis(self, strategy_targets: List[str] = None) -> Dict:
        """Run complete professional parlay analysis"""
        if strategy_targets is None:
            strategy_targets = ['bankroll_builder', 'optimal_growth', 'aggressive']
            
        self.logger.info(" Starting Professional Parlay Engine Analysis")
        
        # Load current games data
        games_data = self.load_current_games_data()
        if not games_data:
            return {}
            
        # Extract betting legs
        all_legs = self.extract_betting_legs(games_data)
        if not all_legs:
            self.logger.error(" No betting legs extracted")
            return {}
            
        # Generate parlays for each strategy
        results = {}
        for strategy_name in strategy_targets:
            if strategy_name in self.strategies:
                parlays = self.generate_strategy_parlays(all_legs, strategy_name, count=3)
                results[strategy_name] = parlays
                
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.logs_dir / f"professional_parlays_{timestamp}.json"
        
        # Convert results for JSON serialization
        json_results = {}
        for strategy, parlays in results.items():
            json_results[strategy] = []
            for parlay in parlays:
                json_parlay = {
                    'strategy': parlay['strategy'],
                    'win_probability': parlay['win_probability'],
                    'payout_multiplier': parlay['payout_multiplier'],
                    'expected_value': parlay['expected_value'],
                    'legs_count': parlay['legs_count'],
                    'legs': [
                        {
                            'game': leg.game,
                            'sport': leg.sport,
                            'bet_type': leg.bet_type,
                            'team_or_side': leg.team_or_side,
                            'odds': leg.odds,
                            'probability': leg.probability,
                            'edge': leg.edge
                        }
                        for leg in parlay['legs']
                    ]
                }
                json_results[strategy].append(json_parlay)
                
        with open(results_file, 'w') as f:
            json.dump(json_results, f, indent=2)
            
        self.logger.info(f" Results saved to {results_file}")
        return results
        
    def display_strategy_summary(self):
        """Display strategy tier summary"""
        print("\n" + "="*100)
        print(" PROFESSIONAL PARLAY ENGINE - STRATEGY TIERS")
        print("="*100)
        
        for key, strategy in self.strategies.items():
            print(f"\n {strategy.name}")
            print("-" * 60)
            print(f" Legs: {strategy.legs_range[0]}-{strategy.legs_range[1]}")
            print(f" Win Probability: {strategy.target_win_prob_range[0]:.2%} - {strategy.target_win_prob_range[1]:.2%}")
            print(f" Payout Range: {strategy.payout_range[0]} - {strategy.payout_range[1]}")
            print(f" Kelly Fraction: {strategy.kelly_fraction:.2%}")
            print(f" EV Floor: {strategy.ev_floor:.2%}")
            print(f" {strategy.description}")
            
        print(f"\n RECOMMENDED DEFAULT: {self.strategies[self.default_strategy].name}")
        print("="*100)


def main():
    parser = argparse.ArgumentParser(description="EQ12 Professional Parlay Engine")
    parser.add_argument('--strategy', choices=['bankroll_builder', 'optimal_growth', 'aggressive', 'simulation', 'all'],
                       default='optimal_growth', help='Strategy tier to run')
    parser.add_argument('--count', type=int, default=3, help='Number of parlays to generate per strategy')
    parser.add_argument('--bankroll', type=float, default=1000, help='Bankroll size for Kelly calculations')
    parser.add_argument('--show-summary', action='store_true', help='Show strategy tier summary')
    parser.add_argument('--workspace', default="C:\\EQ12", help='Workspace path')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize engine
    engine = ProfessionalParlayEngine(args.workspace)
    
    if args.show_summary:
        engine.display_strategy_summary()
        return
        
    # Determine strategies to run
    if args.strategy == 'all':
        strategies = ['bankroll_builder', 'optimal_growth', 'aggressive']
    else:
        strategies = [args.strategy]
        
    # Run analysis
    results = engine.run_professional_analysis(strategies)
    
    if not results:
        print(" No results generated")
        return
        
    # Display results
    print("\n" + "="*100)
    print(" PROFESSIONAL PARLAY RECOMMENDATIONS")
    print("="*100)
    
    for strategy_name, parlays in results.items():
        if parlays:
            print(f"\n {strategy_name.upper().replace('_', ' ')} STRATEGY")
            print("="*80)
            
            for i, parlay in enumerate(parlays, 1):
                print(f"\n Option #{i}:")
                print(engine.format_parlay_display(parlay, args.bankroll))
                
    print("\n" + "="*100)
    print(" PROFESSIONAL ANALYSIS COMPLETE")
    print("="*100)


if __name__ == "__main__":
    main()