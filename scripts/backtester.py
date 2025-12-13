#!/usr/bin/env python3
"""
Advanced Backtester for EQ12 Betting Optimizer
Simulates historical performance with realistic constraints
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Backtester')

class EQ12Backtester:
    """Advanced historical simulation engine"""
    
    def __init__(self, initial_bankroll: float = 10000.0):
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.trades = []
        self.daily_equity = []
        
    def load_historical_slips(self, csv_path: str) -> pd.DataFrame:
        """Load historical betting slips"""
        logger.info(f"Loading slips from {csv_path}")
        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date')
    
    def backtest(self, slips: pd.DataFrame, kelly_fraction: float = 0.25) -> Dict[str, Any]:
        """Run backtest simulation"""
        logger.info(f"Running backtest with {len(slips)} slips")
        
        daily_pnl = {}
        winning_trades = 0
        losing_trades = 0
        
        for idx, slip in slips.iterrows():
            # Extract bet info
            date = slip['date'].date()
            stake = slip['stake']
            odds = slip['odds']
            outcome = slip['outcome']  # 1 for win, 0 for loss
            
            # Calculate P&L
            if outcome == 1:
                pnl = stake * (odds - 1)
                winning_trades += 1
            else:
                pnl = -stake
                losing_trades += 1
            
            # Update bankroll
            self.current_bankroll += pnl
            
            # Track daily
            if date not in daily_pnl:
                daily_pnl[date] = 0
            daily_pnl[date] += pnl
            
            # Log trade
            self.trades.append({
                'date': date,
                'stake': stake,
                'odds': odds,
                'outcome': outcome,
                'pnl': pnl,
                'bankroll': self.current_bankroll
            })
        
        # Calculate equity curve
        self.daily_equity = self._calculate_equity_curve()
        
        # Calculate metrics
        return self._calculate_metrics(winning_trades, losing_trades)
    
    def _calculate_equity_curve(self) -> List[float]:
        """Calculate bankroll over time"""
        equity = [self.initial_bankroll]
        for trade in self.trades:
            equity.append(trade['bankroll'])
        return equity
    
    def _calculate_metrics(self, wins: int, losses: int) -> Dict[str, float]:
        """Calculate performance metrics"""
        total_trades = wins + losses
        win_rate = wins / total_trades if total_trades > 0 else 0
        
        # Calculate ROI
        total_profit = self.current_bankroll - self.initial_bankroll
        roi = total_profit / self.initial_bankroll
        
        # Calculate Sharpe ratio
        equity_array = np.array(self.daily_equity)
        daily_returns = np.diff(equity_array) / equity_array[:-1]
        sharpe = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if len(daily_returns) > 1 else 0
        
        # Calculate max drawdown
        peak = equity_array[0]
        max_dd = 0
        for equity in equity_array:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak
            if drawdown > max_dd:
                max_dd = drawdown
        
        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 4),
            'initial_bankroll': self.initial_bankroll,
            'final_bankroll': round(self.current_bankroll, 2),
            'profit': round(total_profit, 2),
            'roi': round(roi, 4),
            'sharpe_ratio': round(sharpe, 4),
            'max_drawdown': round(max_dd, 4),
            'avg_trade_size': round(sum(t['stake'] for t in self.trades) / total_trades, 2),
            'avg_winning_trade': round(np.mean([t['pnl'] for t in self.trades if t['pnl'] > 0]), 2) if any(t['pnl'] > 0 for t in self.trades) else 0,
            'avg_losing_trade': round(np.mean([t['pnl'] for t in self.trades if t['pnl'] < 0]), 2) if any(t['pnl'] < 0 for t in self.trades) else 0,
        }
    
    def save_results(self, output_path: str):
        """Save backtest results"""
        Path('reports').mkdir(exist_ok=True)
        
        # Save trades
        trades_df = pd.DataFrame(self.trades)
        trades_path = f"{output_path}_trades.csv"
        trades_df.to_csv(trades_path, index=False)
        logger.info(f"Saved trades to {trades_path}")
        
        # Save equity curve
        equity_path = f"{output_path}_equity.json"
        with open(equity_path, 'w') as f:
            json.dump(self.daily_equity, f)
        logger.info(f"Saved equity curve to {equity_path}")

def main():
    parser = argparse.ArgumentParser(description="Backtest EQ12 betting system")
    parser.add_argument('--slips', type=str, default='data/historical_slips.csv',
                       help='Path to historical slips CSV')
    parser.add_argument('--bankroll', type=float, default=10000.0,
                       help='Initial bankroll')
    parser.add_argument('--output', type=str, default='reports/backtest',
                       help='Output path for results')
    parser.add_argument('--days', type=int, help='Number of days to backtest')
    
    args = parser.parse_args()
    
    # Run backtest
    backtester = EQ12Backtester(args.bankroll)
    slips = backtester.load_historical_slips(args.slips)
    
    if args.days:
        cutoff = datetime.now() - timedelta(days=args.days)
        slips = slips[slips['date'] >= cutoff]
        logger.info(f"Backtesting {args.days} days: {len(slips)} slips")
    
    metrics = backtester.backtest(slips)
    backtester.save_results(args.output)
    
    # Print results
    print("\n" + "="*60)
    print("📊 BACKTEST RESULTS")
    print("="*60)
    print(f"Trades:         {metrics['total_trades']} ({metrics['wins']} wins, {metrics['losses']} losses)")
    print(f"Win Rate:       {metrics['win_rate']*100:.1f}%")
    print(f"Initial:        ${metrics['initial_bankroll']:,.2f}")
    print(f"Final:          ${metrics['final_bankroll']:,.2f}")
    print(f"Profit:         ${metrics['profit']:,.2f}")
    print(f"ROI:            {metrics['roi']*100:.1f}%")
    print(f"Sharpe Ratio:   {metrics['sharpe_ratio']:.4f}")
    print(f"Max Drawdown:   {metrics['max_drawdown']*100:.1f}%")
    print("="*60)

if __name__ == "__main__":
    main()
