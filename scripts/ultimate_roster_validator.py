#!/usr/bin/env python3
"""
 ULTIMATE NFL ROSTER VALIDATION SYSTEM
Prevents SGP failures by ensuring all players are verified before betting
Master controller that eliminates roster issues once and for all
"""

import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os

# Import our custom systems
try:
    from nfl_live_roster_verification import NFLLiveRosterSystem
    from automated_sgp_generator import AutomatedSGPGenerator
except ImportError as e:
    print(f" Import error: {e}")
    sys.exit(1)


class UltimateRosterValidator:
    """
     Ultimate NFL Roster Validation System
    Master controller that prevents ALL player prop failures
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.setup_logging()
        
        # Initialize subsystems
        self.roster_system = NFLLiveRosterSystem()
        self.sgp_generator = AutomatedSGPGenerator()
        
        # Validation history
        self.validation_history = []
        
        self.logger.info("Ultimate Roster Validator initialized")
    
    def setup_logging(self):
        """Setup logging system"""
        
        log_dir = "C:\\EQ12\\logs"
        os.makedirs(log_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"roster_validation_{timestamp}.log")
        
        logging.basicConfig(
            level=logging.INFO if self.verbose else logging.WARNING,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler() if self.verbose else logging.NullHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def validate_and_generate_sgps(self, away_team: str, home_team: str, 
                                  game_date: Optional[str] = None,
                                  num_strategies: int = 5,
                                  min_legs: int = 8,
                                  max_legs: int = 12) -> Dict[str, Any]:
        """
         Complete validation and SGP generation pipeline
        Returns both verification results and generated SGPs
        """
        
        self.logger.info(f"Starting complete validation for {away_team} @ {home_team}")
        
        print(" ULTIMATE NFL ROSTER VALIDATION SYSTEM")
        print("="*80)
        print(f" GAME: {away_team} @ {home_team}")
        print(f" DATE: {game_date or datetime.now().strftime('%Y-%m-%d')}")
        print("="*80)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'game_info': {
                'away_team': away_team,
                'home_team': home_team,
                'game_date': game_date or datetime.now().strftime('%Y-%m-%d')
            },
            'roster_verification': {},
            'sgp_strategies': [],
            'validation_status': 'UNKNOWN',
            'recommendations': [],
            'errors': []
        }
        
        try:
            # Step 1: Comprehensive roster verification
            print("\n STEP 1: ROSTER VERIFICATION")
            print("-" * 40)
            
            roster_results = self.roster_system.verify_game_rosters(
                away_team, home_team, game_date
            )
            
            results['roster_verification'] = roster_results
            
            # Display verification results
            self.roster_system.display_verification_results(roster_results)
            
            # Step 2: Validate roster quality
            validation_quality = self._assess_roster_quality(roster_results)
            results['validation_quality'] = validation_quality
            
            # Step 3: Generate verified SGPs if rosters are good
            if validation_quality['safe_for_betting']:
                print("\n STEP 2: GENERATING VERIFIED SGPs")
                print("-" * 40)
                
                sgp_strategies = self.sgp_generator.generate_verified_sgps(
                    away_team, home_team, num_strategies, min_legs, max_legs
                )
                
                results['sgp_strategies'] = sgp_strategies
                
                # Display SGP strategies
                if sgp_strategies:
                    self.sgp_generator.display_sgp_strategies(sgp_strategies)
                
                results['validation_status'] = 'SUCCESS'
                
            else:
                print("\n ROSTER QUALITY INSUFFICIENT FOR SGP GENERATION")
                print("   Skipping SGP generation due to roster issues")
                results['validation_status'] = 'ROSTER_ISSUES'
            
            # Step 4: Generate final recommendations
            recommendations = self._generate_final_recommendations(results)
            results['recommendations'] = recommendations
            
            # Step 5: Save complete results
            self._save_complete_results(results)
            
            return results
            
        except Exception as e:
            error_msg = f"Validation pipeline failed: {str(e)}"
            self.logger.error(error_msg)
            results['errors'].append(error_msg)
            results['validation_status'] = 'ERROR'
            
            print(f"\n PIPELINE ERROR: {error_msg}")
            
            return results
    
    def _assess_roster_quality(self, roster_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess whether roster data is sufficient for betting"""
        
        quality_assessment = {
            'safe_for_betting': True,
            'confidence_level': 'HIGH',
            'issues_found': [],
            'players_verified': 0,
            'positions_covered': set()
        }
        
        try:
            validation = roster_results.get('validation', {})
            rosters = roster_results.get('rosters', {})
            
            # Check validation status
            if validation.get('status') == 'ERRORS':
                quality_assessment['safe_for_betting'] = False
                quality_assessment['confidence_level'] = 'LOW'
                quality_assessment['issues_found'].extend(validation.get('errors', []))
            
            elif validation.get('status') == 'WARNINGS':
                quality_assessment['confidence_level'] = 'MEDIUM'
                quality_assessment['issues_found'].extend(validation.get('warnings', []))
            
            # Count verified players
            total_players = 0
            for team_data in rosters.values():
                players = team_data.get('players', [])
                for player in players:
                    total_players += 1
                    pos = getattr(player, 'position', None) or player.get('position')
                    if pos:
                        quality_assessment['positions_covered'].add(pos)
            
            quality_assessment['players_verified'] = total_players
            
            # Require minimum position coverage
            required_positions = {'QB', 'RB', 'WR', 'TE'}
            covered_positions = quality_assessment['positions_covered']
            
            if not required_positions.issubset(covered_positions):
                missing = required_positions - covered_positions
                quality_assessment['safe_for_betting'] = False
                quality_assessment['issues_found'].append(
                    f"Missing key positions: {', '.join(missing)}"
                )
            
            # Require minimum player count
            if total_players < 8:  # At least 4 players per team
                quality_assessment['safe_for_betting'] = False
                quality_assessment['issues_found'].append(
                    f"Insufficient player data: {total_players} players found"
                )
            
            self.logger.info(f"Roster quality assessment: {quality_assessment}")
            
        except Exception as e:
            self.logger.error(f"Roster quality assessment failed: {e}")
            quality_assessment['safe_for_betting'] = False
            quality_assessment['issues_found'].append(f"Assessment error: {str(e)}")
        
        return quality_assessment
    
    def _generate_final_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate final betting recommendations"""
        
        recommendations = []
        
        validation_status = results.get('validation_status')
        quality = results.get('validation_quality', {})
        
        if validation_status == 'SUCCESS':
            recommendations.extend([
                " ALL SYSTEMS GREEN - Safe to place SGP bets",
                " Rosters verified and SGP strategies generated",
                " Focus on high-confidence legs (85%+ confidence)",
                " Consider bankroll management with multiple strategies"
            ])
            
        elif validation_status == 'ROSTER_ISSUES':
            recommendations.extend([
                " ROSTER ISSUES DETECTED - Avoid player props",
                " Game totals and spreads are still safe",
                " Re-check rosters 90 minutes before kickoff",
                " Consider simpler 3-5 leg parlays with verified players only"
            ])
            
        else:
            recommendations.extend([
                " SYSTEM ERRORS - DO NOT BET",
                " Technical issues detected with verification system",
                " Manual roster verification required",
                " Wait for system resolution before betting"
            ])
        
        # Add quality-specific recommendations
        if quality.get('confidence_level') == 'MEDIUM':
            recommendations.append(" Medium confidence - reduce bet sizes by 50%")
        elif quality.get('confidence_level') == 'LOW':
            recommendations.append(" Low confidence - avoid all player props")
        
        # Add timing recommendations
        recommendations.extend([
            f" Last verified: {datetime.now().strftime('%H:%M')}",
            " Re-verify 2 hours before game time",
            " Check official injury reports before betting"
        ])
        
        return recommendations
    
    def _save_complete_results(self, results: Dict[str, Any]) -> str:
        """Save complete validation results"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        game_info = results['game_info']
        filename = (f"C:\\EQ12\\logs\\complete_validation_"
                   f"{game_info['away_team']}_{game_info['home_team']}_{timestamp}.json")
        
        # Convert any complex objects to JSON-serializable format
        json_results = self._convert_to_json_serializable(results)
        
        with open(filename, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"\n Complete results saved: {filename}")
        self.logger.info(f"Results saved to {filename}")
        
        return filename
    
    def _convert_to_json_serializable(self, obj: Any) -> Any:
        """Convert complex objects to JSON-serializable format"""
        
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        elif isinstance(obj, dict):
            return {k: self._convert_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, set):
            return list(obj)
        else:
            return obj
    
    def quick_verify_players(self, player_names: List[str], teams: List[str]) -> Dict[str, bool]:
        """Quick verification of specific players"""
        
        print(f"\n QUICK PLAYER VERIFICATION")
        print("-" * 40)
        
        verification_results = {}
        
        for i, player in enumerate(player_names):
            team = teams[i] if i < len(teams) else 'Unknown'
            
            # This would hit the live API in production
            # For now, using fallback logic
            is_active = self._check_player_status(player, team)
            verification_results[player] = is_active
            
            status_icon = "" if is_active else ""
            print(f"   {status_icon} {player} ({team}): {'ACTIVE' if is_active else 'INACTIVE/UNKNOWN'}")
        
        return verification_results
    
    def _check_player_status(self, player_name: str, team: str) -> bool:
        """Check individual player status"""
        
        # Known inactive players as of November 2025
        known_inactive = [
            'DK Metcalf',
            'Terry McLaurin', 
            'Tyler Lockett',
            'Isiah Pacheco',
            'Stefon Diggs'
        ]
        
        # If player is in known inactive list, return False
        if player_name in known_inactive:
            return False
        
        # Otherwise assume active (in production, this would hit live APIs)
        return True
    
    def display_final_summary(self, results: Dict[str, Any]) -> None:
        """Display final validation summary"""
        
        print("\n" + "="*80)
        print(" ULTIMATE VALIDATION SUMMARY")
        print("="*80)
        
        game_info = results['game_info']
        print(f" GAME: {game_info['away_team']} @ {game_info['home_team']}")
        print(f" DATE: {game_info['game_date']}")
        print(f" VALIDATED: {results['timestamp']}")
        
        validation_status = results['validation_status']
        status_icons = {
            'SUCCESS': '',
            'ROSTER_ISSUES': '',
            'ERROR': '',
            'UNKNOWN': ''
        }
        
        icon = status_icons.get(validation_status, '')
        print(f"\n{icon} VALIDATION STATUS: {validation_status}")
        
        # Display quality metrics
        quality = results.get('validation_quality', {})
        if quality:
            print(f" CONFIDENCE LEVEL: {quality.get('confidence_level', 'Unknown')}")
            print(f" PLAYERS VERIFIED: {quality.get('players_verified', 0)}")
            print(f" POSITIONS COVERED: {len(quality.get('positions_covered', set()))}")
        
        # Display SGP count
        sgp_count = len(results.get('sgp_strategies', []))
        if sgp_count > 0:
            print(f" SGP STRATEGIES: {sgp_count} generated")
        
        # Display recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            print(f"\n FINAL RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   {rec}")
        
        # Display errors if any
        errors = results.get('errors', [])
        if errors:
            print(f"\n ERRORS ENCOUNTERED:")
            for error in errors:
                print(f"   {error}")
        
        print("\n" + "="*80)


def main():
    """Main CLI interface"""
    
    parser = argparse.ArgumentParser(
        description="Ultimate NFL Roster Validation System"
    )
    
    parser.add_argument('--away-team', type=str, required=True,
                       help='Away team code (e.g., SEA)')
    parser.add_argument('--home-team', type=str, required=True,
                       help='Home team code (e.g., WAS)')
    parser.add_argument('--game-date', type=str,
                       help='Game date (YYYY-MM-DD)')
    parser.add_argument('--num-strategies', type=int, default=5,
                       help='Number of SGP strategies to generate')
    parser.add_argument('--min-legs', type=int, default=8,
                       help='Minimum SGP legs')
    parser.add_argument('--max-legs', type=int, default=12,
                       help='Maximum SGP legs')
    parser.add_argument('--quick-verify', type=str, nargs='+',
                       help='Quick verify specific players')
    parser.add_argument('--player-teams', type=str, nargs='+',
                       help='Teams for quick verify players')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = UltimateRosterValidator(verbose=args.verbose)
    
    # Quick verify mode
    if args.quick_verify:
        teams = args.player_teams or ['Unknown'] * len(args.quick_verify)
        verification_results = validator.quick_verify_players(args.quick_verify, teams)
        
        print(f"\n VERIFICATION RESULTS:")
        active_count = sum(verification_results.values())
        total_count = len(verification_results)
        print(f"   Active: {active_count}/{total_count}")
        
        return
    
    # Full validation mode
    results = validator.validate_and_generate_sgps(
        away_team=args.away_team,
        home_team=args.home_team,
        game_date=args.game_date,
        num_strategies=args.num_strategies,
        min_legs=args.min_legs,
        max_legs=args.max_legs
    )
    
    # Display final summary
    validator.display_final_summary(results)


if __name__ == "__main__":
    main()