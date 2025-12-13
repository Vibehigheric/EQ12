#!/usr/bin/env python3
"""
 BILLS VS CHIEFS SGP ANALYZER
Same Game Parlay Intelligence for Buffalo Bills vs Kansas City Chiefs
Minimum 10-leg parlay construction with advanced prop analysis
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any
import random
import itertools


class BillsChiefsSGPAnalyzer:
    """
     Bills vs Chiefs Same Game Parlay Analyzer
    Constructs profitable 10+ leg parlays for maximum value
    """
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = workspace_path
        
    def analyze_sgp_opportunities(self, min_legs: int = 10, stakes: float = 25.0) -> Dict[str, Any]:
        """
         Analyze Bills vs Chiefs for SGP opportunities with minimum leg count
        """
        print("")
        print("   BILLS VS CHIEFS SAME GAME PARLAY ANALYZER                         ")
        print("                                                                          ")
        print("   10+ LEG SGP CONSTRUCTION INTELLIGENCE                                ")
        print("   BUFFALO BILLS VS KANSAS CITY CHIEFS PROP ANALYSIS                   ")
        print("   MAXIMUM VALUE SGP OPPORTUNITIES                                     ")
        print("")
        print()
        
        start_time = time.time()
        
        try:
            # Load odds and find Bills vs Chiefs game
            print(" Loading live odds and prop data...")
            odds_data = self._load_latest_odds()
            
            print(" Searching for Bills vs Chiefs game...")
            bills_chiefs_game = self._find_bills_chiefs_game(odds_data)
            
            if not bills_chiefs_game:
                print(" No Bills vs Chiefs game found")
                return self._create_no_game_report(stakes, time.time() - start_time)
            
            # Extract all available props
            print(" Extracting all available props and markets...")
            all_props = self._extract_all_props(bills_chiefs_game)
            
            print(f" Found {len(all_props)} total props across all markets")
            
            # Build SGP combinations
            print(f" Building SGP combinations with minimum {min_legs} legs...")
            sgp_combinations = self._build_sgp_combinations(all_props, min_legs)
            
            # Analyze and rank SGPs
            print(" Analyzing and ranking SGP opportunities...")
            analyzed_sgps = self._analyze_sgp_combinations(sgp_combinations, stakes)
            
            # Create comprehensive report
            execution_time = time.time() - start_time
            final_report = self._create_sgp_report(
                analyzed_sgps, bills_chiefs_game, stakes, execution_time, min_legs
            )
            
            # Display results
            self._display_sgp_results(final_report)
            
            # Save results
            self._save_sgp_results(final_report)
            
            return final_report
            
        except Exception as e:
            print(f" SGP analysis failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    def _load_latest_odds(self) -> Dict[str, Any]:
        """Load the latest odds data"""
        feeds_dir = os.path.join(self.workspace_path, "coral_betting_ai", "feeds")
        
        # Find the latest odds file
        odds_files = []
        for filename in os.listdir(feeds_dir):
            if "odds" in filename and filename.endswith(".json"):
                filepath = os.path.join(feeds_dir, filename)
                odds_files.append((filepath, os.path.getmtime(filepath)))
        
        if not odds_files:
            raise FileNotFoundError("No odds files found")
        
        # Get the most recent file
        latest_file = max(odds_files, key=lambda x: x[1])[0]
        print(f" Using: {os.path.basename(latest_file)}")
        
        with open(latest_file, 'r') as f:
            return json.load(f)
    
    def _find_bills_chiefs_game(self, odds_data: Dict[str, Any]) -> Dict[str, Any]:
        """Find the Bills vs Chiefs game"""
        games = odds_data.get('api_odds', [])
        
        for game in games:
            home_team = str(game.get('home_team', '')).lower()
            away_team = str(game.get('away_team', '')).lower()
            
            # Bills identifiers
            bills_identifiers = ['buffalo', 'bills']
            # Chiefs identifiers  
            chiefs_identifiers = ['kansas city', 'chiefs', 'kc']
            
            # Check if this is the Bills vs Chiefs game
            is_bills_game = any(identifier in home_team or identifier in away_team 
                              for identifier in bills_identifiers)
            is_chiefs_game = any(identifier in home_team or identifier in away_team 
                               for identifier in chiefs_identifiers)
            
            if is_bills_game and is_chiefs_game:
                print(f" Found: {game.get('away_team', 'Unknown')} @ {game.get('home_team', 'Unknown')}")
                return game
        
        return None
    
    def _extract_all_props(self, game: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all available props from the game"""
        all_props = []
        
        bookmakers = game.get('bookmakers', [])
        
        for bookmaker in bookmakers:
            bookmaker_name = bookmaker.get('name', 'Unknown')
            markets = bookmaker.get('markets', {})
            
            # Process each market type
            for market_key, outcomes in markets.items():
                if isinstance(outcomes, list):
                    for outcome in outcomes:
                        prop = {
                            'bookmaker': bookmaker_name,
                            'market': market_key,
                            'outcome_name': outcome.get('name', 'Unknown'),
                            'odds': outcome.get('price', 1.0),
                            'point': outcome.get('point'),
                            'prop_id': f"{bookmaker_name}_{market_key}_{outcome.get('name', 'unknown')}",
                            'game_teams': f"{game.get('away_team', 'Unknown')} @ {game.get('home_team', 'Unknown')}"
                        }
                        
                        # Add market classification
                        prop['market_type'] = self._classify_market(market_key, outcome.get('name', ''))
                        
                        # Calculate implied probability
                        prop['implied_probability'] = 1.0 / prop['odds'] if prop['odds'] > 0 else 0.5
                        
                        all_props.append(prop)
        
        return all_props
    
    def _classify_market(self, market_key: str, outcome_name: str) -> str:
        """Classify market type for SGP construction"""
        market_key = market_key.lower()
        outcome_name = outcome_name.lower()
        
        if market_key == 'h2h':
            return 'moneyline'
        elif market_key == 'spreads':
            return 'spread'
        elif market_key == 'totals':
            return 'total'
        elif 'touchdown' in outcome_name or 'td' in outcome_name:
            return 'touchdown'
        elif 'yard' in outcome_name or 'rushing' in outcome_name or 'passing' in outcome_name:
            return 'yardage'
        elif 'reception' in outcome_name or 'catch' in outcome_name:
            return 'reception'
        elif 'interception' in outcome_name or 'int' in outcome_name:
            return 'interception'
        elif 'sack' in outcome_name:
            return 'sack'
        else:
            return 'other'
    
    def _build_sgp_combinations(self, all_props: List[Dict[str, Any]], min_legs: int) -> List[List[Dict[str, Any]]]:
        """Build SGP combinations with minimum leg requirements"""
        
        # Filter out props that might conflict in SGPs
        compatible_props = self._filter_compatible_props(all_props)
        
        print(f" {len(compatible_props)} compatible props available for SGP construction")
        
        # Group props by market type for balanced SGPs
        market_groups = {}
        for prop in compatible_props:
            market_type = prop['market_type']
            if market_type not in market_groups:
                market_groups[market_type] = []
            market_groups[market_type].append(prop)
        
        print(f" Market types available: {list(market_groups.keys())}")
        
        # Build balanced SGP combinations
        sgp_combinations = []
        
        # Strategy 1: Build 10-leg SGPs with diverse markets
        if len(compatible_props) >= min_legs:
            # Create multiple 10+ leg combinations
            for _ in range(10):  # Generate 10 different SGP combinations
                combination = self._create_balanced_sgp(market_groups, min_legs)
                if len(combination) >= min_legs:
                    sgp_combinations.append(combination)
        
        # Strategy 2: Build focused SGPs (player props + game props)
        player_focused = self._build_player_focused_sgps(market_groups, min_legs)
        sgp_combinations.extend(player_focused)
        
        # Strategy 3: Build conservative SGPs (higher probability outcomes)
        conservative_sgps = self._build_conservative_sgps(compatible_props, min_legs)
        sgp_combinations.extend(conservative_sgps)
        
        print(f" Created {len(sgp_combinations)} SGP combinations")
        return sgp_combinations
    
    def _filter_compatible_props(self, all_props: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter props that are compatible for SGP combinations"""
        compatible = []
        
        for prop in all_props:
            # Skip props with very low odds (too risky for SGP)
            if prop['odds'] < 1.1:
                continue
            
            # Skip props with extremely high odds (too risky)
            if prop['odds'] > 10.0:
                continue
            
            # Only include props from major bookmakers for SGP
            major_books = ['DraftKings', 'FanDuel', 'Caesars', 'BetMGM', 'PointsBet']
            if any(book in prop['bookmaker'] for book in major_books):
                compatible.append(prop)
            else:
                # Include other books but with preference scoring
                prop['preference_score'] = 0.5
                compatible.append(prop)
        
        return compatible
    
    def _create_balanced_sgp(self, market_groups: Dict[str, List[Dict[str, Any]]], min_legs: int) -> List[Dict[str, Any]]:
        """Create a balanced SGP with diverse market types"""
        combination = []
        
        # Prioritize market types for balanced SGP
        priority_markets = ['moneyline', 'total', 'spread', 'touchdown', 'yardage', 'reception']
        
        # Add one prop from each priority market
        for market_type in priority_markets:
            if market_type in market_groups and market_groups[market_type]:
                # Choose a random prop from this market type
                prop = random.choice(market_groups[market_type])
                combination.append(prop)
        
        # Fill remaining legs with other props
        remaining_props = []
        for market_type, props in market_groups.items():
            if market_type not in priority_markets:
                remaining_props.extend(props)
        
        # Add random props to reach minimum legs
        while len(combination) < min_legs and remaining_props:
            prop = random.choice(remaining_props)
            if prop not in combination:  # Avoid duplicates
                combination.append(prop)
                remaining_props.remove(prop)
        
        return combination
    
    def _build_player_focused_sgps(self, market_groups: Dict[str, List[Dict[str, Any]]], min_legs: int) -> List[List[Dict[str, Any]]]:
        """Build SGPs focused on player performances"""
        player_sgps = []
        
        # Focus on touchdown and yardage props
        player_markets = ['touchdown', 'yardage', 'reception']
        
        for _ in range(3):  # Create 3 player-focused SGPs
            combination = []
            
            # Add multiple player props
            for market_type in player_markets:
                if market_type in market_groups:
                    available_props = market_groups[market_type][:3]  # Top 3 from each category
                    combination.extend(available_props)
            
            # Fill with game props
            game_markets = ['moneyline', 'total', 'spread']
            for market_type in game_markets:
                if market_type in market_groups and len(combination) < min_legs:
                    combination.extend(market_groups[market_type][:2])
            
            if len(combination) >= min_legs:
                player_sgps.append(combination[:min_legs])
        
        return player_sgps
    
    def _build_conservative_sgps(self, all_props: List[Dict[str, Any]], min_legs: int) -> List[List[Dict[str, Any]]]:
        """Build conservative SGPs with higher probability outcomes"""
        conservative_sgps = []
        
        # Sort by implied probability (higher probability = more conservative)
        sorted_props = sorted(all_props, key=lambda x: x['implied_probability'], reverse=True)
        
        # Take top probability props
        high_prob_props = [p for p in sorted_props if p['implied_probability'] > 0.4]  # 40%+ probability
        
        if len(high_prob_props) >= min_legs:
            # Create 2 conservative SGPs
            for i in range(2):
                start_idx = i * min_legs
                end_idx = start_idx + min_legs
                if end_idx <= len(high_prob_props):
                    conservative_sgps.append(high_prob_props[start_idx:end_idx])
        
        return conservative_sgps
    
    def _analyze_sgp_combinations(self, sgp_combinations: List[List[Dict[str, Any]]], stakes: float) -> List[Dict[str, Any]]:
        """Analyze and score SGP combinations"""
        analyzed_sgps = []
        
        for i, combination in enumerate(sgp_combinations, 1):
            if len(combination) < 10:  # Skip combinations with less than 10 legs
                continue
            
            sgp_analysis = self._analyze_single_sgp(combination, stakes, i)
            analyzed_sgps.append(sgp_analysis)
        
        # Sort by expected value
        analyzed_sgps.sort(key=lambda x: x['expected_value'], reverse=True)
        
        return analyzed_sgps
    
    def _analyze_single_sgp(self, combination: List[Dict[str, Any]], stakes: float, sgp_id: int) -> Dict[str, Any]:
        """Analyze a single SGP combination"""
        
        # Calculate combined odds
        combined_odds = 1.0
        total_implied_prob = 1.0
        
        for prop in combination:
            combined_odds *= prop['odds']
            # Adjust for correlation (SGPs typically have reduced payouts)
            total_implied_prob *= prop['implied_probability']
        
        # Apply SGP correlation penalty (typically 15-30% reduction in true odds)
        correlation_penalty = 0.80  # 20% penalty for correlation
        adjusted_probability = total_implied_prob * correlation_penalty
        
        # Calculate expected value
        expected_value = (adjusted_probability * combined_odds) - 1.0
        
        # Calculate recommended stake using modified Kelly
        if expected_value > 0.05:  # 5% minimum edge
            kelly_fraction = min(0.15, expected_value / (combined_odds - 1))  # Max 15% for SGPs
            recommended_stake = stakes * kelly_fraction
        else:
            recommended_stake = 0.0
        
        # Calculate potential payout
        potential_payout = recommended_stake * combined_odds if recommended_stake > 0 else 0
        potential_profit = potential_payout - recommended_stake if potential_payout > 0 else 0
        
        return {
            'sgp_id': sgp_id,
            'leg_count': len(combination),
            'legs': combination,
            'combined_odds': round(combined_odds, 2),
            'adjusted_probability': round(adjusted_probability, 4),
            'expected_value': round(expected_value, 3),
            'recommended_stake': round(recommended_stake, 2),
            'potential_payout': round(potential_payout, 2),
            'potential_profit': round(potential_profit, 2),
            'sgp_score': round(expected_value * 100, 1),  # For ranking
            'risk_level': self._calculate_risk_level(combination),
            'market_diversity': len(set(prop['market_type'] for prop in combination))
        }
    
    def _calculate_risk_level(self, combination: List[Dict[str, Any]]) -> str:
        """Calculate risk level of SGP combination"""
        avg_prob = sum(prop['implied_probability'] for prop in combination) / len(combination)
        
        if avg_prob > 0.6:
            return 'Conservative'
        elif avg_prob > 0.4:
            return 'Moderate' 
        else:
            return 'Aggressive'
    
    def _create_sgp_report(self, analyzed_sgps: List[Dict[str, Any]], game: Dict[str, Any], 
                          stakes: float, execution_time: float, min_legs: int) -> Dict[str, Any]:
        """Create comprehensive SGP report"""
        
        return {
            'analysis_type': 'Bills vs Chiefs SGP Analysis',
            'timestamp': datetime.now().isoformat(),
            'execution_time': round(execution_time, 2),
            'stakes': stakes,
            'min_legs_required': min_legs,
            'status': 'success',
            'game_info': {
                'home_team': game.get('home_team', 'Unknown'),
                'away_team': game.get('away_team', 'Unknown'),
                'commence_time': game.get('commence_time', 'Unknown')
            },
            'sgp_count': len(analyzed_sgps),
            'top_sgps': analyzed_sgps[:5],  # Top 5 SGPs
            'all_sgps': analyzed_sgps,
            'system_info': {
                'processor': 'SGP Intelligence Engine',
                'analysis_mode': 'Multi-leg SGP Construction',
                'correlation_adjustment': 'Applied'
            }
        }
    
    def _create_no_game_report(self, stakes: float, execution_time: float) -> Dict[str, Any]:
        """Create report when no game found"""
        return {
            'analysis_type': 'Bills vs Chiefs SGP Analysis',
            'timestamp': datetime.now().isoformat(),
            'execution_time': round(execution_time, 2),
            'stakes': stakes,
            'status': 'no_game_found',
            'message': 'No Bills vs Chiefs game found for SGP analysis'
        }
    
    def _display_sgp_results(self, report: Dict[str, Any]) -> None:
        """Display SGP analysis results"""
        print("\n" + "="*80)
        print(" BILLS VS CHIEFS SGP ANALYSIS RESULTS")
        print("="*80)
        
        if report.get('status') != 'success':
            print(" SGP analysis incomplete")
            return
        
        # Summary
        print(f"\n SGP ANALYSIS SUMMARY:")
        print(f"    Game: {report['game_info']['away_team']} @ {report['game_info']['home_team']}")
        print(f"    SGP combinations analyzed: {report.get('sgp_count', 0)}")
        print(f"    Minimum legs required: {report.get('min_legs_required', 10)}")
        print(f"    Analysis time: {report.get('execution_time', 0):.2f}s")
        
        # Top SGPs
        top_sgps = report.get('top_sgps', [])
        if top_sgps:
            print(f"\n TOP SGP OPPORTUNITIES:")
            
            for i, sgp in enumerate(top_sgps, 1):
                print(f"\n SGP #{i} - {sgp['leg_count']} LEGS ({sgp['risk_level']} Risk)")
                print(f"    Combined Odds: {sgp['combined_odds']:,.2f}")
                print(f"    Expected Value: {sgp['expected_value']:.3f}")
                print(f"    Recommended Stake: ${sgp['recommended_stake']:.2f}")
                print(f"    Potential Profit: ${sgp['potential_profit']:.2f}")
                print(f"    SGP Score: {sgp['sgp_score']:.1f}")
                print(f"    Market Diversity: {sgp['market_diversity']} different market types")
                
                print(f"    LEGS:")
                for j, leg in enumerate(sgp['legs'][:10], 1):  # Show first 10 legs
                    print(f"      {j:2d}. {leg['outcome_name']} @ {leg['odds']:.2f} ({leg['market']})")
                
                if len(sgp['legs']) > 10:
                    print(f"      ... and {len(sgp['legs']) - 10} more legs")
        
        print("\n SGP ANALYSIS COMPLETE!")
        print(" These SGPs are optimized for 10+ leg parlays with correlation adjustments")
    
    def _save_sgp_results(self, report: Dict[str, Any]) -> None:
        """Save SGP analysis results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sgp_bills_chiefs_{timestamp}.json"
        
        # Save to reports directory
        reports_dir = os.path.join(self.workspace_path, "coral_betting_ai", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f" SGP results saved: {filename}")


def main():
    """Main function for SGP analysis"""
    analyzer = BillsChiefsSGPAnalyzer()
    
    # Run SGP analysis with minimum 10 legs and $25 stakes
    results = analyzer.analyze_sgp_opportunities(min_legs=10, stakes=25.0)
    
    if results.get("status") == "success":
        print("\n Bills vs Chiefs SGP analysis successful!")
        print(f" Found {results.get('sgp_count', 0)} SGP opportunities with 10+ legs")
    else:
        print("\n SGP analysis encountered issues")


if __name__ == "__main__":
    main()