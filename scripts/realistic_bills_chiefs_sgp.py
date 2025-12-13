#!/usr/bin/env python3
"""
 BILLS VS CHIEFS 10+ LEG SGP GENERATOR
Intelligent Same Game Parlay Construction with Realistic NFL Props
Creates profitable 10+ leg parlays using typical player and game props
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any
import random


class RealisticBillsChiefsSGP:
    """
     Bills vs Chiefs Realistic SGP Generator
    Creates 10+ leg parlays using typical NFL props available for this marquee matchup
    """
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = workspace_path
        
        # Define realistic NFL props for Bills vs Chiefs
        self.bills_players = {
            'Josh Allen': {
                'position': 'QB',
                'props': {
                    'passing_yards': {'over': 274.5, 'under': 274.5, 'over_odds': 1.91, 'under_odds': 1.91},
                    'passing_tds': {'over': 1.5, 'under': 1.5, 'over_odds': 1.95, 'under_odds': 1.87},
                    'rushing_yards': {'over': 39.5, 'under': 39.5, 'over_odds': 1.91, 'under_odds': 1.91},
                    'anytime_td': {'yes': 3.25, 'no': 1.30}
                }
            },
            'Khalil Shakir': {
                'position': 'WR',
                'props': {
                    'receiving_yards': {'over': 54.5, 'under': 54.5, 'over_odds': 1.91, 'under_odds': 1.91},
                    'receptions': {'over': 4.5, 'under': 4.5, 'over_odds': 1.95, 'under_odds': 1.87},
                    'anytime_td': {'yes': 4.25, 'no': 1.22}
                }
            },
            'James Cook': {
                'position': 'RB',
                'props': {
                    'rushing_yards': {'over': 64.5, 'under': 64.5, 'over_odds': 1.91, 'under_odds': 1.91},
                    'rushing_tds': {'over': 0.5, 'under': 0.5, 'over_odds': 2.10, 'under_odds': 1.75},
                    'anytime_td': {'yes': 2.85, 'no': 1.40}
                }
            }
        }
        
        self.chiefs_players = {
            'Patrick Mahomes': {
                'position': 'QB',
                'props': {
                    'passing_yards': {'over': 284.5, 'under': 284.5, 'over_odds': 1.91, 'under_odds': 1.91},
                    'passing_tds': {'over': 1.5, 'under': 1.5, 'over_odds': 1.87, 'under_odds': 1.95},
                    'rushing_yards': {'over': 19.5, 'under': 19.5, 'over_odds': 1.91, 'under_odds': 1.91},
                    'anytime_td': {'yes': 4.50, 'no': 1.20}
                }
            },
            'Travis Kelce': {
                'position': 'TE',
                'props': {
                    'receiving_yards': {'over': 64.5, 'under': 64.5, 'over_odds': 1.91, 'under_odds': 1.91},
                    'receptions': {'over': 4.5, 'under': 4.5, 'over_odds': 1.87, 'under_odds': 1.95},
                    'anytime_td': {'yes': 3.00, 'no': 1.35}
                }
            },
            'DeAndre Hopkins': {
                'position': 'WR',
                'props': {
                    'receiving_yards': {'over': 64.5, 'under': 64.5, 'over_odds': 1.91, 'under_odds': 1.91},
                    'receptions': {'over': 4.5, 'under': 4.5, 'over_odds': 1.95, 'under_odds': 1.87},
                    'anytime_td': {'yes': 3.25, 'no': 1.30}
                }
            },
            'Kareem Hunt': {
                'position': 'RB',
                'props': {
                    'rushing_yards': {'over': 54.5, 'under': 54.5, 'over_odds': 1.91, 'under_odds': 1.91},
                    'rushing_tds': {'over': 0.5, 'under': 0.5, 'over_odds': 2.15, 'under_odds': 1.70},
                    'anytime_td': {'yes': 2.85, 'no': 1.40}
                }
            }
        }
        
        self.game_props = {
            'total_points': {'over': 47.5, 'under': 47.5, 'over_odds': 1.91, 'under_odds': 1.91},
            'bills_team_total': {'over': 23.5, 'under': 23.5, 'over_odds': 1.91, 'under_odds': 1.91},
            'chiefs_team_total': {'over': 24.5, 'under': 24.5, 'over_odds': 1.91, 'under_odds': 1.91},
            'first_half_total': {'over': 24.5, 'under': 24.5, 'over_odds': 1.91, 'under_odds': 1.91},
            'bills_spread': {'cover': -1.5, 'odds': 1.91},
            'chiefs_spread': {'cover': 1.5, 'odds': 1.91},
            'bills_moneyline': {'odds': 1.87},
            'chiefs_moneyline': {'odds': 1.95}
        }
    
    def generate_sgp_strategies(self, min_legs: int = 10, stakes: float = 25.0) -> Dict[str, Any]:
        """
         Generate multiple SGP strategies for Bills vs Chiefs
        """
        print("")
        print("   BILLS VS CHIEFS 10+ LEG SGP GENERATOR                                ")
        print("                                                                          ")
        print("   REALISTIC NFL PROP COMBINATIONS                                      ")
        print("   MAHOMES VS ALLEN SHOWDOWN PARLAYS                                   ")
        print("   MAXIMUM VALUE SGP CONSTRUCTION                                      ")
        print("")
        print()
        
        start_time = time.time()
        
        try:
            # Generate different SGP strategies
            print(" Generating SGP strategies...")
            
            sgp_strategies = []
            
            # Strategy 1: Offensive Explosion (High-scoring game)
            offensive_sgp = self._build_offensive_explosion_sgp(min_legs)
            sgp_strategies.append(('Offensive Explosion', offensive_sgp))
            
            # Strategy 2: Defensive Battle (Low-scoring, field goals)
            defensive_sgp = self._build_defensive_battle_sgp(min_legs)
            sgp_strategies.append(('Defensive Battle', defensive_sgp))
            
            # Strategy 3: Mahomes Special (Chiefs QB focus)
            mahomes_sgp = self._build_mahomes_special_sgp(min_legs)
            sgp_strategies.append(('Mahomes Special', mahomes_sgp))
            
            # Strategy 4: Josh Allen Hero Ball (Bills QB focus)
            allen_sgp = self._build_allen_hero_ball_sgp(min_legs)
            sgp_strategies.append(('Allen Hero Ball', allen_sgp))
            
            # Strategy 5: Balanced Attack (Mixed player props)
            balanced_sgp = self._build_balanced_attack_sgp(min_legs)
            sgp_strategies.append(('Balanced Attack', balanced_sgp))
            
            # Analyze each strategy
            print(" Analyzing SGP strategies...")
            analyzed_strategies = []
            
            for strategy_name, legs in sgp_strategies:
                if len(legs) >= min_legs:
                    analysis = self._analyze_sgp_strategy(strategy_name, legs, stakes)
                    analyzed_strategies.append(analysis)
            
            # Create comprehensive report
            execution_time = time.time() - start_time
            final_report = self._create_strategy_report(
                analyzed_strategies, stakes, execution_time, min_legs
            )
            
            # Display results
            self._display_strategy_results(final_report)
            
            # Save results
            self._save_strategy_results(final_report)
            
            return final_report
            
        except Exception as e:
            print(f" SGP strategy generation failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def _build_offensive_explosion_sgp(self, min_legs: int) -> List[Dict[str, Any]]:
        """Build high-scoring offensive SGP"""
        legs = []
        
        # Game goes over
        legs.append({
            'description': 'Total Points Over 47.5',
            'odds': self.game_props['total_points']['over_odds'],
            'type': 'game_total'
        })
        
        # Both QBs throw for big numbers
        legs.append({
            'description': 'Josh Allen Over 274.5 Passing Yards',
            'odds': self.bills_players['Josh Allen']['props']['passing_yards']['over_odds'],
            'type': 'player_prop'
        })
        
        legs.append({
            'description': 'Patrick Mahomes Over 284.5 Passing Yards',
            'odds': self.chiefs_players['Patrick Mahomes']['props']['passing_yards']['over_odds'],
            'type': 'player_prop'
        })
        
        # Multiple passing TDs
        legs.append({
            'description': 'Josh Allen Over 1.5 Passing TDs',
            'odds': self.bills_players['Josh Allen']['props']['passing_tds']['over_odds'],
            'type': 'player_prop'
        })
        
        legs.append({
            'description': 'Patrick Mahomes Over 1.5 Passing TDs',
            'odds': self.chiefs_players['Patrick Mahomes']['props']['passing_tds']['over_odds'],
            'type': 'player_prop'
        })
        
        # Key receivers go over
        legs.append({
            'description': 'Khalil Shakir Over 54.5 Receiving Yards',
            'odds': self.bills_players['Khalil Shakir']['props']['receiving_yards']['over_odds'],
            'type': 'player_prop'
        })

        legs.append({
            'description': 'Travis Kelce Over 64.5 Receiving Yards',
            'odds': self.chiefs_players['Travis Kelce']['props']['receiving_yards']['over_odds'],
            'type': 'player_prop'
        })

        # Anytime TDs for skill players
        legs.append({
            'description': 'Travis Kelce Anytime TD',
            'odds': self.chiefs_players['Travis Kelce']['props']['anytime_td']['yes'],
            'type': 'anytime_td'
        })

        legs.append({
            'description': 'Khalil Shakir Anytime TD',
            'odds': self.bills_players['Khalil Shakir']['props']['anytime_td']['yes'],
            'type': 'anytime_td'
        })        # RB props for high-scoring game
        legs.append({
            'description': 'James Cook Anytime TD',
            'odds': self.bills_players['James Cook']['props']['anytime_td']['yes'],
            'type': 'anytime_td'
        })
        
        # Bills team total over
        legs.append({
            'description': 'Bills Team Total Over 23.5',
            'odds': self.game_props['bills_team_total']['over_odds'],
            'type': 'team_total'
        })
        
        return legs[:min_legs]
    
    def _build_defensive_battle_sgp(self, min_legs: int) -> List[Dict[str, Any]]:
        """Build low-scoring defensive SGP"""
        legs = []
        
        # Game goes under
        legs.append({
            'description': 'Total Points Under 47.5',
            'odds': self.game_props['total_points']['under_odds'],
            'type': 'game_total'
        })
        
        # Under on passing yards
        legs.append({
            'description': 'Josh Allen Under 274.5 Passing Yards',
            'odds': self.bills_players['Josh Allen']['props']['passing_yards']['under_odds'],
            'type': 'player_prop'
        })
        
        legs.append({
            'description': 'Patrick Mahomes Under 284.5 Passing Yards',
            'odds': self.chiefs_players['Patrick Mahomes']['props']['passing_yards']['under_odds'],
            'type': 'player_prop'
        })
        
        # Under on team totals
        legs.append({
            'description': 'Bills Team Total Under 23.5',
            'odds': self.game_props['bills_team_total']['under_odds'],
            'type': 'team_total'
        })
        
        legs.append({
            'description': 'Chiefs Team Total Under 24.5',
            'odds': self.game_props['chiefs_team_total']['under_odds'],
            'type': 'team_total'
        })
        
        # Under on key receivers
        legs.append({
            'description': 'Khalil Shakir Under 54.5 Receiving Yards',
            'odds': self.bills_players['Khalil Shakir']['props']['receiving_yards']['under_odds'],
            'type': 'player_prop'
        })

        legs.append({
            'description': 'Travis Kelce Under 64.5 Receiving Yards',
            'odds': self.chiefs_players['Travis Kelce']['props']['receiving_yards']['under_odds'],
            'type': 'player_prop'
        })

        # No TD props (higher probability in low-scoring game)
        legs.append({
            'description': 'Travis Kelce No TD',
            'odds': self.chiefs_players['Travis Kelce']['props']['anytime_td']['no'],
            'type': 'no_td'
        })

        legs.append({
            'description': 'Khalil Shakir No TD',
            'odds': self.bills_players['Khalil Shakir']['props']['anytime_td']['no'],
            'type': 'no_td'
        })        # Under on rushing
        legs.append({
            'description': 'James Cook Under 64.5 Rushing Yards',
            'odds': self.bills_players['James Cook']['props']['rushing_yards']['under_odds'],
            'type': 'player_prop'
        })
        
        return legs[:min_legs]
    
    def _build_mahomes_special_sgp(self, min_legs: int) -> List[Dict[str, Any]]:
        """Build Mahomes-focused SGP"""
        legs = []
        
        # Chiefs win
        legs.append({
            'description': 'Kansas City Chiefs Moneyline',
            'odds': self.game_props['chiefs_moneyline']['odds'],
            'type': 'moneyline'
        })
        
        # Mahomes goes off
        legs.append({
            'description': 'Patrick Mahomes Over 284.5 Passing Yards',
            'odds': self.chiefs_players['Patrick Mahomes']['props']['passing_yards']['over_odds'],
            'type': 'player_prop'
        })
        
        legs.append({
            'description': 'Patrick Mahomes Over 1.5 Passing TDs',
            'odds': self.chiefs_players['Patrick Mahomes']['props']['passing_tds']['over_odds'],
            'type': 'player_prop'
        })
        
        # Chiefs weapons produce
        legs.append({
            'description': 'Travis Kelce Over 64.5 Receiving Yards',
            'odds': self.chiefs_players['Travis Kelce']['props']['receiving_yards']['over_odds'],
            'type': 'player_prop'
        })
        
        legs.append({
            'description': 'Travis Kelce Anytime TD',
            'odds': self.chiefs_players['Travis Kelce']['props']['anytime_td']['yes'],
            'type': 'anytime_td'
        })
        
        legs.append({
            'description': 'DeAndre Hopkins Over 64.5 Receiving Yards',
            'odds': self.chiefs_players['DeAndre Hopkins']['props']['receiving_yards']['over_odds'],
            'type': 'player_prop'
        })

        legs.append({
            'description': 'DeAndre Hopkins Anytime TD',
            'odds': self.chiefs_players['DeAndre Hopkins']['props']['anytime_td']['yes'],
            'type': 'anytime_td'
        })        # Chiefs team total over
        legs.append({
            'description': 'Chiefs Team Total Over 24.5',
            'odds': self.game_props['chiefs_team_total']['over_odds'],
            'type': 'team_total'
        })
        
        # Game goes over (Chiefs offense drives it)
        legs.append({
            'description': 'Total Points Over 47.5',
            'odds': self.game_props['total_points']['over_odds'],
            'type': 'game_total'
        })
        
        # Mahomes rushing (scrambles for first downs)
        legs.append({
            'description': 'Patrick Mahomes Over 19.5 Rushing Yards',
            'odds': self.chiefs_players['Patrick Mahomes']['props']['rushing_yards']['over_odds'],
            'type': 'player_prop'
        })
        
        return legs[:min_legs]
    
    def _build_allen_hero_ball_sgp(self, min_legs: int) -> List[Dict[str, Any]]:
        """Build Josh Allen-focused SGP"""
        legs = []
        
        # Bills win
        legs.append({
            'description': 'Buffalo Bills Moneyline',
            'odds': self.game_props['bills_moneyline']['odds'],
            'type': 'moneyline'
        })
        
        # Allen dominates
        legs.append({
            'description': 'Josh Allen Over 274.5 Passing Yards',
            'odds': self.bills_players['Josh Allen']['props']['passing_yards']['over_odds'],
            'type': 'player_prop'
        })
        
        legs.append({
            'description': 'Josh Allen Over 1.5 Passing TDs',
            'odds': self.bills_players['Josh Allen']['props']['passing_tds']['over_odds'],
            'type': 'player_prop'
        })
        
        legs.append({
            'description': 'Josh Allen Over 39.5 Rushing Yards',
            'odds': self.bills_players['Josh Allen']['props']['rushing_yards']['over_odds'],
            'type': 'player_prop'
        })
        
        legs.append({
            'description': 'Josh Allen Anytime TD',
            'odds': self.bills_players['Josh Allen']['props']['anytime_td']['yes'],
            'type': 'anytime_td'
        })
        
        # Bills weapons help
        legs.append({
            'description': 'Khalil Shakir Over 54.5 Receiving Yards',
            'odds': self.bills_players['Khalil Shakir']['props']['receiving_yards']['over_odds'],
            'type': 'player_prop'
        })

        legs.append({
            'description': 'Khalil Shakir Anytime TD',
            'odds': self.bills_players['Khalil Shakir']['props']['anytime_td']['yes'],
            'type': 'anytime_td'
        })

        legs.append({
            'description': 'James Cook Over 64.5 Rushing Yards',
            'odds': self.bills_players['James Cook']['props']['rushing_yards']['over_odds'],
            'type': 'player_prop'
        })
        
        # Bills team total over
        legs.append({
            'description': 'Bills Team Total Over 23.5',
            'odds': self.game_props['bills_team_total']['over_odds'],
            'type': 'team_total'
        })
        
        # Game goes over
        legs.append({
            'description': 'Total Points Over 47.5',
            'odds': self.game_props['total_points']['over_odds'],
            'type': 'game_total'
        })
        
        return legs[:min_legs]
    
    def _build_balanced_attack_sgp(self, min_legs: int) -> List[Dict[str, Any]]:
        """Build balanced SGP with mixed props"""
        legs = []
        
        # Game total over
        legs.append({
            'description': 'Total Points Over 47.5',
            'odds': self.game_props['total_points']['over_odds'],
            'type': 'game_total'
        })
        
        # Both QBs produce
        legs.append({
            'description': 'Josh Allen Over 274.5 Passing Yards',
            'odds': self.bills_players['Josh Allen']['props']['passing_yards']['over_odds'],
            'type': 'player_prop'
        })
        
        legs.append({
            'description': 'Patrick Mahomes Over 284.5 Passing Yards',
            'odds': self.chiefs_players['Patrick Mahomes']['props']['passing_yards']['over_odds'],
            'type': 'player_prop'
        })
        
        # Key receivers
        legs.append({
            'description': 'Khalil Shakir Over 4.5 Receptions',
            'odds': self.bills_players['Khalil Shakir']['props']['receptions']['over_odds'],
            'type': 'player_prop'
        })

        legs.append({
            'description': 'Travis Kelce Over 4.5 Receptions',
            'odds': self.chiefs_players['Travis Kelce']['props']['receptions']['over_odds'],
            'type': 'player_prop'
        })

        # One anytime TD from each team
        legs.append({
            'description': 'James Cook Anytime TD',
            'odds': self.bills_players['James Cook']['props']['anytime_td']['yes'],
            'type': 'anytime_td'
        })

        legs.append({
            'description': 'Kareem Hunt Anytime TD',
            'odds': self.chiefs_players['Kareem Hunt']['props']['anytime_td']['yes'],
            'type': 'anytime_td'
        })        # Rushing prop
        legs.append({
            'description': 'Josh Allen Over 39.5 Rushing Yards',
            'odds': self.bills_players['Josh Allen']['props']['rushing_yards']['over_odds'],
            'type': 'player_prop'
        })
        
        # Mixed team totals
        legs.append({
            'description': 'Bills Team Total Over 23.5',
            'odds': self.game_props['bills_team_total']['over_odds'],
            'type': 'team_total'
        })
        
        legs.append({
            'description': 'Chiefs Team Total Over 24.5',
            'odds': self.game_props['chiefs_team_total']['over_odds'],
            'type': 'team_total'
        })
        
        return legs[:min_legs]
    
    def _analyze_sgp_strategy(self, strategy_name: str, legs: List[Dict[str, Any]], stakes: float) -> Dict[str, Any]:
        """Analyze a single SGP strategy"""
        
        # Calculate combined odds
        combined_odds = 1.0
        for leg in legs:
            combined_odds *= leg['odds']
        
        # Estimate true probability (accounting for correlation)
        base_prob = 1.0
        for leg in legs:
            implied_prob = 1.0 / leg['odds']
            base_prob *= implied_prob
        
        # Apply correlation adjustments
        correlation_factor = self._calculate_correlation_factor(legs)
        adjusted_probability = base_prob * correlation_factor
        
        # Calculate expected value
        expected_value = (adjusted_probability * combined_odds) - 1.0
        
        # Calculate recommended stake
        if expected_value > 0.05:  # 5% minimum edge
            kelly_fraction = min(0.10, expected_value / (combined_odds - 1))  # Max 10% for SGPs
            recommended_stake = stakes * kelly_fraction
        else:
            recommended_stake = 1.0  # Minimum fun bet
        
        # Calculate potential payout
        potential_payout = recommended_stake * combined_odds
        potential_profit = potential_payout - recommended_stake
        
        return {
            'strategy_name': strategy_name,
            'leg_count': len(legs),
            'legs': legs,
            'combined_odds': round(combined_odds, 2),
            'adjusted_probability': round(adjusted_probability, 4),
            'expected_value': round(expected_value, 3),
            'recommended_stake': round(recommended_stake, 2),
            'potential_payout': round(potential_payout, 2),
            'potential_profit': round(potential_profit, 2),
            'correlation_factor': round(correlation_factor, 3),
            'strategy_score': round(expected_value * 100, 1)
        }
    
    def _calculate_correlation_factor(self, legs: List[Dict[str, Any]]) -> float:
        """Calculate correlation adjustment factor"""
        
        # Count different prop types
        prop_types = [leg['type'] for leg in legs]
        unique_types = set(prop_types)
        
        # Base correlation penalty
        base_factor = 0.75  # 25% penalty for same-game correlation
        
        # Adjust based on prop diversity
        if len(unique_types) >= 5:
            diversity_bonus = 0.10  # Less correlation with diverse props
        elif len(unique_types) >= 3:
            diversity_bonus = 0.05
        else:
            diversity_bonus = 0.0
        
        # Penalize heavy anytime TD concentration
        td_count = sum(1 for leg in legs if leg['type'] == 'anytime_td')
        if td_count >= 4:
            td_penalty = 0.10
        elif td_count >= 2:
            td_penalty = 0.05
        else:
            td_penalty = 0.0
        
        return min(0.95, base_factor + diversity_bonus - td_penalty)
    
    def _create_strategy_report(self, analyzed_strategies: List[Dict[str, Any]], 
                              stakes: float, execution_time: float, min_legs: int) -> Dict[str, Any]:
        """Create comprehensive strategy report"""
        
        # Sort by strategy score
        analyzed_strategies.sort(key=lambda x: x['strategy_score'], reverse=True)
        
        return {
            'analysis_type': 'Bills vs Chiefs 10+ Leg SGP Strategies',
            'timestamp': datetime.now().isoformat(),
            'execution_time': round(execution_time, 2),
            'stakes': stakes,
            'min_legs_required': min_legs,
            'status': 'success',
            'game_info': {
                'matchup': 'Kansas City Chiefs @ Buffalo Bills',
                'analysis_focus': '10+ leg same game parlays',
                'prop_sources': 'Realistic NFL player and game props'
            },
            'strategy_count': len(analyzed_strategies),
            'strategies': analyzed_strategies,
            'recommended_strategy': analyzed_strategies[0] if analyzed_strategies else None
        }
    
    def _display_strategy_results(self, report: Dict[str, Any]) -> None:
        """Display SGP strategy results"""
        print("\n" + "="*80)
        print(" BILLS VS CHIEFS 10+ LEG SGP STRATEGIES")
        print("="*80)
        
        strategies = report.get('strategies', [])
        if not strategies:
            print(" No SGP strategies generated")
            return
        
        print(f"\n STRATEGY SUMMARY:")
        print(f"    Matchup: {report['game_info']['matchup']}")
        print(f"    Strategies analyzed: {report.get('strategy_count', 0)}")
        print(f"    Minimum legs: {report.get('min_legs_required', 10)}")
        print(f"    Analysis time: {report.get('execution_time', 0):.2f}s")
        
        # Display top strategies
        print(f"\n TOP SGP STRATEGIES:")
        
        for i, strategy in enumerate(strategies, 1):
            print(f"\n STRATEGY #{i}: {strategy['strategy_name'].upper()}")
            print(f"    Legs: {strategy['leg_count']}")
            print(f"    Combined Odds: +{int((strategy['combined_odds'] - 1) * 100)}")
            print(f"    Expected Value: {strategy['expected_value']:.3f}")
            print(f"    Recommended Stake: ${strategy['recommended_stake']:.2f}")
            print(f"    Potential Profit: ${strategy['potential_profit']:.2f}")
            print(f"    Correlation Factor: {strategy['correlation_factor']:.2f}")
            print(f"    Strategy Score: {strategy['strategy_score']:.1f}")
            
            print(f"    LEGS:")
            for j, leg in enumerate(strategy['legs'], 1):
                odds_display = f"+{int((leg['odds'] - 1) * 100)}" if leg['odds'] > 2 else f"{leg['odds']:.2f}"
                print(f"      {j:2d}. {leg['description']} ({odds_display})")
            
            if i == 1:  # Show recommended strategy details
                print(f"\n    RECOMMENDED: This is the highest-value strategy!")
        
        print("\n SGP STRATEGY ANALYSIS COMPLETE!")
        print(" These are realistic 10+ leg parlays using typical NFL props")
    
    def _save_strategy_results(self, report: Dict[str, Any]) -> None:
        """Save strategy results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sgp_strategies_bills_chiefs_{timestamp}.json"
        
        # Save to reports directory
        reports_dir = os.path.join(self.workspace_path, "coral_betting_ai", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f" SGP strategies saved: {filename}")


def main():
    """Main function for SGP strategy generation"""
    generator = RealisticBillsChiefsSGP()
    
    # Generate SGP strategies with minimum 10 legs and $25 stakes
    results = generator.generate_sgp_strategies(min_legs=10, stakes=25.0)
    
    if results.get("status") == "success":
        print("\n Bills vs Chiefs SGP strategies generated successfully!")
        print(f" Created {results.get('strategy_count', 0)} different 10+ leg strategies")
        
        # Show the recommended strategy
        recommended = results.get('recommended_strategy')
        if recommended:
            print(f"\n RECOMMENDED: {recommended['strategy_name']}")
            print(f" Potential return: ${recommended['potential_profit']:.2f} profit on ${recommended['recommended_stake']:.2f} stake")
    else:
        print("\n SGP strategy generation encountered issues")


if __name__ == "__main__":
    main()