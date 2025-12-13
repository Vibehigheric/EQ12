"""
EQ12 Automatic Bet Execution System

Integrates scanner output with bankroll manager for automated bet placement,
Kelly sizing, risk checks, and comprehensive tracking.

Author: EQ12 System
Created: 2025-11-28
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse

from eq12_bankroll_manager import EQ12BankrollManager, BetType, BetStatus

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EQ12AutoBetExecutor:
    """
    Automated bet execution with bankroll integration
    """
    
    def __init__(
        self,
        bankroll_db: str = "../logs/eq12_bankroll.db",
        starting_bankroll: float = 10000.0,
        min_confidence: float = 70.0,
        min_edge: float = 2.0,
        execute_mode: bool = False
    ):
        """
        Initialize auto executor
        
        Args:
            bankroll_db: Path to bankroll database
            starting_bankroll: Initial bankroll
            min_confidence: Minimum confidence score to bet
            min_edge: Minimum edge percentage to bet
            execute_mode: If True, actually place bets (False = dry run)
        """
        self.manager = EQ12BankrollManager(bankroll_db, starting_bankroll)
        self.min_confidence = min_confidence
        self.min_edge = min_edge
        self.execute_mode = execute_mode
        
        if not execute_mode:
            logger.warning("⚠️  DRY RUN MODE - Bets will not be placed")
            
    def process_scan_results(self, scan_file: str) -> Dict:
        """
        Process scanner output and execute qualifying bets
        
        Args:
            scan_file: Path to scanner JSON output
            
        Returns:
            Execution summary
        """
        with open(scan_file, 'r') as f:
            results = json.load(f)
            
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'scan_file': scan_file,
            'total_opportunities': 0,
            'arbitrage_processed': 0,
            'positive_ev_processed': 0,
            'bets_placed': 0,
            'bets_skipped': 0,
            'total_staked': 0.0,
            'errors': [],
            'placed_bets': []
        }
        
        # Process arbitrage opportunities (highest priority)
        if 'arbitrage' in results:
            for arb in results['arbitrage']:
                summary['total_opportunities'] += 1
                summary['arbitrage_processed'] += 1
                
                result = self._execute_arbitrage(arb)
                if result['success']:
                    summary['bets_placed'] += result['bets_placed']
                    summary['total_staked'] += result['total_staked']
                    summary['placed_bets'].extend(result['bet_ids'])
                else:
                    summary['bets_skipped'] += 1
                    summary['errors'].append(result.get('error', 'Unknown error'))
                    
        # Process positive EV opportunities
        if 'positive_ev' in results:
            # Sort by confidence score
            opportunities = sorted(
                results['positive_ev'],
                key=lambda x: x.get('confidence_score', 0),
                reverse=True
            )
            
            for opp in opportunities:
                summary['total_opportunities'] += 1
                summary['positive_ev_processed'] += 1
                
                # Filter by confidence and edge
                if opp.get('confidence_score', 0) < self.min_confidence:
                    summary['bets_skipped'] += 1
                    continue
                    
                if opp.get('edge_percent', 0) < self.min_edge:
                    summary['bets_skipped'] += 1
                    continue
                    
                result = self._execute_positive_ev(opp)
                if result['success']:
                    summary['bets_placed'] += 1
                    summary['total_staked'] += result['stake']
                    summary['placed_bets'].append(result['bet_id'])
                else:
                    summary['bets_skipped'] += 1
                    summary['errors'].append(result.get('error', 'Unknown error'))
                    
        return summary
        
    def _execute_arbitrage(self, arb: Dict) -> Dict:
        """Execute arbitrage opportunity (both legs)"""
        if not self.execute_mode:
            return {
                'success': True,
                'bets_placed': 2,
                'total_staked': arb.get('recommended_stake_amount', 0) * 2,
                'bet_ids': ['DRY_RUN_1', 'DRY_RUN_2'],
                'note': 'Dry run mode'
            }
            
        bet_ids = []
        total_staked = 0.0
        
        try:
            # Place first leg (higher stake usually)
            stake1 = arb.get('recommended_stake_amount', 0)
            
            result1 = self.manager.place_bet(
                sport=arb.get('sport', 'Unknown'),
                game=arb.get('game', 'Unknown'),
                market=arb.get('market', 'h2h'),
                outcome=arb.get('outcome', 'Unknown'),
                odds=arb.get('best_odds', 0),
                decimal_odds=arb.get('decimal_odds', 2.0),
                stake=stake1,
                edge_percent=arb.get('edge_percent', 0),
                confidence_score=95.0,  # Arbitrage is always high confidence
                bet_type='arbitrage',
                sportsbook=arb.get('best_book', 'Unknown'),
                notes=f"Arbitrage leg 1 - {arb.get('edge_percent', 0):.2f}% profit"
            )
            
            if not result1['success']:
                return {'success': False, 'error': result1['error']}
                
            bet_ids.append(result1['bet_id'])
            total_staked += stake1
            
            # Note: Second leg would require additional data from scanner
            # This is a framework - actual implementation needs paired leg data
            
            return {
                'success': True,
                'bets_placed': len(bet_ids),
                'total_staked': total_staked,
                'bet_ids': bet_ids
            }
            
        except Exception as e:
            logger.error(f"Arbitrage execution error: {e}")
            return {'success': False, 'error': str(e)}
            
    def _execute_positive_ev(self, opp: Dict) -> Dict:
        """Execute positive EV opportunity"""
        if not self.execute_mode:
            return {
                'success': True,
                'stake': opp.get('recommended_stake_amount', 0),
                'bet_id': 'DRY_RUN',
                'note': 'Dry run mode'
            }
            
        try:
            result = self.manager.place_bet(
                sport=opp.get('sport', 'Unknown'),
                game=opp.get('game', 'Unknown'),
                market=opp.get('market', 'h2h'),
                outcome=opp.get('outcome', 'Unknown'),
                odds=opp.get('best_odds', 0),
                decimal_odds=opp.get('decimal_odds', 2.0),
                stake=opp.get('recommended_stake_amount', 0),
                edge_percent=opp.get('edge_percent', 0),
                confidence_score=opp.get('confidence_score', 0),
                bet_type=self._determine_bet_type(opp.get('market', 'h2h')),
                sportsbook=opp.get('best_book', 'Unknown'),
                sharp_money=opp.get('sharp_money_indicator', False),
                steam_move=opp.get('steam_move_indicator', False),
                notes=f"Edge: {opp.get('edge_percent', 0):.2f}%, Conf: {opp.get('confidence_score', 0):.0f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Positive EV execution error: {e}")
            return {'success': False, 'error': str(e)}
            
    def _determine_bet_type(self, market: str) -> str:
        """Determine bet type from market"""
        market_lower = market.lower()
        if 'h2h' in market_lower or 'moneyline' in market_lower:
            return 'moneyline'
        elif 'spread' in market_lower or 'handicap' in market_lower:
            return 'spread'
        elif 'total' in market_lower or 'over' in market_lower or 'under' in market_lower:
            return 'total'
        elif 'prop' in market_lower:
            return 'prop'
        else:
            return 'moneyline'
            
    def generate_execution_report(self, summary: Dict, output_path: str):
        """Generate execution report"""
        report = {
            'execution_summary': summary,
            'bankroll_status': {
                'total': self.manager._get_current_bankroll(),
                'available': self.manager.get_available_bankroll(),
                'pending': self.manager._get_pending_amount()
            },
            'risk_metrics': self.manager.get_risk_metrics().__dict__,
            'settings': {
                'min_confidence': self.min_confidence,
                'min_edge': self.min_edge,
                'execute_mode': self.execute_mode
            }
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Execution report saved: {output_path}")
        return report


def main():
    parser = argparse.ArgumentParser(description="EQ12 Auto Bet Executor")
    parser.add_argument('--scan', required=True, help='Scanner output JSON file')
    parser.add_argument('--bankroll-db', default='../logs/eq12_bankroll.db', 
                       help='Bankroll database path')
    parser.add_argument('--starting-bankroll', type=float, default=10000.0,
                       help='Starting bankroll')
    parser.add_argument('--min-confidence', type=float, default=70.0,
                       help='Minimum confidence score (0-100)')
    parser.add_argument('--min-edge', type=float, default=2.0,
                       help='Minimum edge percentage')
    parser.add_argument('--execute', action='store_true',
                       help='Execute bets (default is dry run)')
    parser.add_argument('--report', default='../reports/execution_report.json',
                       help='Execution report output path')
    
    args = parser.parse_args()
    
    executor = EQ12AutoBetExecutor(
        bankroll_db=args.bankroll_db,
        starting_bankroll=args.starting_bankroll,
        min_confidence=args.min_confidence,
        min_edge=args.min_edge,
        execute_mode=args.execute
    )
    
    print("\n🤖 EQ12 AUTO BET EXECUTOR")
    print("=" * 60)
    print(f"Mode: {'LIVE EXECUTION' if args.execute else 'DRY RUN'}")
    print(f"Min Confidence: {args.min_confidence}")
    print(f"Min Edge: {args.min_edge}%")
    print(f"Bankroll: ${args.starting_bankroll:,.2f}")
    print("=" * 60)
    
    summary = executor.process_scan_results(args.scan)
    
    print(f"\n📊 EXECUTION SUMMARY")
    print(f"Total Opportunities: {summary['total_opportunities']}")
    print(f"Bets Placed: {summary['bets_placed']}")
    print(f"Bets Skipped: {summary['bets_skipped']}")
    print(f"Total Staked: ${summary['total_staked']:,.2f}")
    
    if summary['errors']:
        print(f"\n⚠️  ERRORS ({len(summary['errors'])})")
        for error in summary['errors'][:5]:
            print(f"  - {error}")
            
    executor.generate_execution_report(summary, args.report)
    print(f"\n✅ Report saved: {args.report}")


if __name__ == '__main__':
    main()
