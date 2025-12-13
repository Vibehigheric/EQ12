"""
EQ12 Professional Bankroll Management System

Comprehensive bankroll tracking, Kelly Criterion optimization, risk management,
and portfolio analytics for sports betting operations.

Author: EQ12 System
Created: 2025-11-28
"""

import json
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EQ12_Bankroll_Manager")

class EQ12KellyBankrollManager:
    """
    Manages bankroll and calculates stake sizes using Kelly Criterion.
    """

    def __init__(self, total_bankroll=1000.0, kelly_multiplier=0.25, max_stake_percent=5.0):
        """
        :param total_bankroll: Total funds available.
        :param kelly_multiplier: Fractional Kelly to reduce variance (e.g., 0.25 for Quarter Kelly).
        :param max_stake_percent: Maximum percentage of bankroll to wager on a single bet.
        """
        self.bankroll = float(total_bankroll)
        self.kelly_multiplier = kelly_multiplier
        self.max_stake_percent = max_stake_percent
        logger.info(f"💰 Bankroll Manager Initialized: ${self.bankroll:.2f} | Kelly: {self.kelly_multiplier}x")

    def calculate_stake(self, ev_percent, american_odds, model_probability_percent):
        """
        Calculate optimal stake amount.
        :param ev_percent: Expected Value percentage.
        :param american_odds: Market odds.
        :param model_probability_percent: Model's win probability.
        :return: Stake amount in dollars.
        """
        if ev_percent <= 0:
            logger.info("Skipping bet: Negative or Zero EV")
            return 0.0

        decimal_odds = self._american_to_decimal(american_odds)
        if decimal_odds <= 1:
            return 0.0

        # Kelly Criterion Formula: f* = (bp - q) / b
        # b = net odds received on the wager (decimal odds - 1)
        # p = probability of winning
        # q = probability of losing (1 - p)
        
        b = decimal_odds - 1
        p = model_probability_percent / 100.0
        q = 1.0 - p

        f_star = (b * p - q) / b
        
        # Apply Fractional Kelly
        adjusted_f = f_star * self.kelly_multiplier

        # Calculate raw stake
        stake = self.bankroll * adjusted_f

        # Apply Max Stake Limit
        max_stake = self.bankroll * (self.max_stake_percent / 100.0)
        
        final_stake = max(0.0, min(stake, max_stake))
        
        logger.info(f"Stake Calc: EV {ev_percent:.1f}% | Kelly {f_star:.4f} -> Adj {adjusted_f:.4f} | Stake: ${final_stake:.2f}")
        return round(final_stake, 2)

    def _american_to_decimal(self, american_odds):
        try:
            odds = float(american_odds)
            if odds > 0:
                return 1 + (odds / 100)
            else:
                return 1 + (100 / abs(odds))
        except:
            return 0.0

    def update_bankroll(self, amount_won_or_lost):
        """Update bankroll after a bet settles."""
        self.bankroll += amount_won_or_lost
        logger.info(f"Bankroll Updated: ${self.bankroll:.2f} ({amount_won_or_lost:+.2f})")

if __name__ == "__main__":
    mgr = EQ12BankrollManager(total_bankroll=10000)
    
    # Scenario: High confidence edge
    # 55% win rate at -110 odds (EV ~5%)
    stake = mgr.calculate_stake(ev_percent=4.9, american_odds=-110, model_probability_percent=55)
    print(f"Recommended Stake: ${stake}")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BetStatus(Enum):
    """Bet lifecycle statuses"""
    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    PUSHED = "pushed"
    CANCELLED = "cancelled"


class BetType(Enum):
    """Types of bets"""
    MONEYLINE = "moneyline"
    SPREAD = "spread"
    TOTAL = "total"
    PROP = "prop"
    PARLAY = "parlay"
    ARBITRAGE = "arbitrage"


@dataclass
class BankrollSnapshot:
    """Point-in-time bankroll state"""
    timestamp: str
    total_bankroll: float
    available_bankroll: float
    pending_amount: float
    total_bets: int
    won_bets: int
    lost_bets: int
    win_rate: float
    roi: float
    profit_loss: float
    largest_bet: float
    average_bet: float
    sharpe_ratio: float
    max_drawdown: float
    notes: str = ""


@dataclass
class Bet:
    """Individual bet record"""
    bet_id: str
    timestamp: str
    sport: str
    game: str
    market: str
    outcome: str
    odds: float  # American odds
    decimal_odds: float
    stake: float
    recommended_stake: float
    kelly_fraction: float
    edge_percent: float
    confidence_score: float
    bet_type: str
    sportsbook: str
    status: str
    result_timestamp: Optional[str] = None
    profit_loss: Optional[float] = None
    actual_odds: Optional[float] = None  # Final settled odds
    notes: str = ""
    sharp_money: bool = False
    steam_move: bool = False
    correlation_group: Optional[str] = None


@dataclass
class RiskMetrics:
    """Portfolio risk analytics"""
    total_exposure: float
    exposure_percent: float
    max_single_bet_percent: float
    kelly_compliance: float  # % of bets following Kelly
    correlation_risk: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    current_drawdown: float
    win_rate: float
    avg_winning_bet: float
    avg_losing_bet: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    risk_of_ruin: float


class EQ12BankrollManager:
    """
    Professional bankroll management system with Kelly Criterion,
    risk analytics, and comprehensive bet tracking.
    """
    
    def __init__(self, db_path: str = "../logs/eq12_bankroll.db", starting_bankroll: float = 10000.0):
        """
        Initialize bankroll manager
        
        Args:
            db_path: Path to SQLite database
            starting_bankroll: Initial bankroll amount
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.starting_bankroll = starting_bankroll
        
        # Risk parameters
        self.kelly_fraction = 0.25  # Quarter Kelly (conservative)
        self.max_single_bet = 0.05  # 5% max per bet
        self.max_total_exposure = 0.30  # 30% max pending
        self.min_bankroll_percent = 0.50  # Stop at 50% loss
        
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Bets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                bet_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                sport TEXT NOT NULL,
                game TEXT NOT NULL,
                market TEXT NOT NULL,
                outcome TEXT NOT NULL,
                odds REAL NOT NULL,
                decimal_odds REAL NOT NULL,
                stake REAL NOT NULL,
                recommended_stake REAL NOT NULL,
                kelly_fraction REAL NOT NULL,
                edge_percent REAL NOT NULL,
                confidence_score REAL NOT NULL,
                bet_type TEXT NOT NULL,
                sportsbook TEXT NOT NULL,
                status TEXT NOT NULL,
                result_timestamp TEXT,
                profit_loss REAL,
                actual_odds REAL,
                notes TEXT,
                sharp_money INTEGER DEFAULT 0,
                steam_move INTEGER DEFAULT 0,
                correlation_group TEXT
            )
        """)
        
        # Bankroll snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_bankroll REAL NOT NULL,
                available_bankroll REAL NOT NULL,
                pending_amount REAL NOT NULL,
                total_bets INTEGER NOT NULL,
                won_bets INTEGER NOT NULL,
                lost_bets INTEGER NOT NULL,
                win_rate REAL NOT NULL,
                roi REAL NOT NULL,
                profit_loss REAL NOT NULL,
                largest_bet REAL NOT NULL,
                average_bet REAL NOT NULL,
                sharpe_ratio REAL NOT NULL,
                max_drawdown REAL NOT NULL,
                notes TEXT
            )
        """)
        
        # Deposits/Withdrawals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                bankroll_before REAL NOT NULL,
                bankroll_after REAL NOT NULL,
                notes TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Create initial snapshot if database is new
        if self._get_current_bankroll() is None:
            self._record_deposit(self.starting_bankroll, "Initial deposit")
            
    def _get_current_bankroll(self) -> Optional[float]:
        """Get current total bankroll"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT total_bankroll FROM snapshots 
            ORDER BY timestamp DESC LIMIT 1
        """)
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
        
    def get_available_bankroll(self) -> float:
        """Get available bankroll (total - pending bets)"""
        current = self._get_current_bankroll() or self.starting_bankroll
        pending = self._get_pending_amount()
        return current - pending
        
    def _get_pending_amount(self) -> float:
        """Get total amount in pending bets"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(stake) FROM bets WHERE status = 'pending'
        """)
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] else 0.0
        
    def calculate_kelly_stake(
        self, 
        decimal_odds: float, 
        win_probability: float,
        bankroll: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Calculate Kelly Criterion stake
        
        Args:
            decimal_odds: Decimal odds (e.g., 2.5)
            win_probability: True probability of winning (0-1)
            bankroll: Override current bankroll
            
        Returns:
            Dict with kelly_fraction, stake, and max_stake
        """
        if bankroll is None:
            bankroll = self.get_available_bankroll()
            
        b = decimal_odds - 1.0  # Net odds received
        p = win_probability
        q = 1.0 - win_probability
        
        # Full Kelly
        kelly_full = ((b * p) - q) / b
        
        if kelly_full <= 0:
            return {
                'kelly_fraction': 0.0,
                'stake': 0.0,
                'max_stake': bankroll * self.max_single_bet,
                'recommendation': 'NO BET - Negative expectation'
            }
            
        # Apply conservative fraction
        kelly_conservative = kelly_full * self.kelly_fraction
        
        # Apply max bet limit
        kelly_limited = min(kelly_conservative, self.max_single_bet)
        
        stake = bankroll * kelly_limited
        max_stake = bankroll * self.max_single_bet
        
        return {
            'kelly_fraction': kelly_limited,
            'kelly_full': kelly_full,
            'kelly_conservative': kelly_conservative,
            'stake': round(stake, 2),
            'max_stake': round(max_stake, 2),
            'bankroll_used': bankroll,
            'recommendation': 'BET' if stake > 0 else 'NO BET'
        }
        
    def place_bet(
        self,
        sport: str,
        game: str,
        market: str,
        outcome: str,
        odds: float,
        decimal_odds: float,
        stake: float,
        edge_percent: float,
        confidence_score: float,
        bet_type: str,
        sportsbook: str,
        **kwargs
    ) -> Dict[str, any]:
        """
        Record a new bet
        
        Args:
            sport: Sport name
            game: Game description
            market: Market type
            outcome: Bet outcome
            odds: American odds
            decimal_odds: Decimal odds
            stake: Bet amount
            edge_percent: Calculated edge
            confidence_score: Confidence (0-100)
            bet_type: Type of bet
            sportsbook: Sportsbook name
            **kwargs: Additional fields (sharp_money, steam_move, etc.)
            
        Returns:
            Dict with bet_id and validation status
        """
        # Validate bankroll
        available = self.get_available_bankroll()
        if stake > available:
            return {
                'success': False,
                'error': f'Insufficient bankroll. Available: ${available:.2f}, Requested: ${stake:.2f}'
            }
            
        # Validate max bet size
        current_bankroll = self._get_current_bankroll()
        max_allowed = current_bankroll * self.max_single_bet
        if stake > max_allowed:
            return {
                'success': False,
                'error': f'Stake exceeds max bet limit. Max: ${max_allowed:.2f}, Requested: ${stake:.2f}'
            }
            
        # Check total exposure
        pending = self._get_pending_amount()
        new_exposure = (pending + stake) / current_bankroll
        if new_exposure > self.max_total_exposure:
            return {
                'success': False,
                'error': f'Total exposure would be {new_exposure*100:.1f}% (max: {self.max_total_exposure*100:.1f}%)'
            }
            
        # Generate bet ID
        timestamp = datetime.utcnow()
        bet_id = f"BET_{timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Calculate Kelly recommendation
        win_prob = 1.0 / decimal_odds + (edge_percent / 100)
        kelly_calc = self.calculate_kelly_stake(decimal_odds, win_prob, current_bankroll)
        
        # Create bet record
        bet = Bet(
            bet_id=bet_id,
            timestamp=timestamp.isoformat(),
            sport=sport,
            game=game,
            market=market,
            outcome=outcome,
            odds=odds,
            decimal_odds=decimal_odds,
            stake=stake,
            recommended_stake=kelly_calc['stake'],
            kelly_fraction=kelly_calc['kelly_fraction'],
            edge_percent=edge_percent,
            confidence_score=confidence_score,
            bet_type=bet_type,
            sportsbook=sportsbook,
            status=BetStatus.PENDING.value,
            sharp_money=kwargs.get('sharp_money', False),
            steam_move=kwargs.get('steam_move', False),
            correlation_group=kwargs.get('correlation_group'),
            notes=kwargs.get('notes', '')
        )
        
        # Save to database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO bets VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            bet.bet_id, bet.timestamp, bet.sport, bet.game, bet.market,
            bet.outcome, bet.odds, bet.decimal_odds, bet.stake,
            bet.recommended_stake, bet.kelly_fraction, bet.edge_percent,
            bet.confidence_score, bet.bet_type, bet.sportsbook, bet.status,
            bet.result_timestamp, bet.profit_loss, bet.actual_odds, bet.notes,
            int(bet.sharp_money), int(bet.steam_move), bet.correlation_group
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Placed bet {bet_id}: {outcome} @ {odds} for ${stake:.2f}")
        
        return {
            'success': True,
            'bet_id': bet_id,
            'stake': stake,
            'recommended_stake': kelly_calc['stake'],
            'kelly_compliance': abs(stake - kelly_calc['stake']) < 1.0,
            'available_after': available - stake,
            'exposure_percent': ((pending + stake) / current_bankroll) * 100
        }
        
    def settle_bet(
        self,
        bet_id: str,
        status: BetStatus,
        actual_odds: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Settle a bet and update bankroll
        
        Args:
            bet_id: Bet identifier
            status: Final status (WON, LOST, PUSHED, CANCELLED)
            actual_odds: Actual settled odds (if different from original)
            
        Returns:
            Dict with settlement details
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get bet details
        cursor.execute("SELECT * FROM bets WHERE bet_id = ?", (bet_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return {'success': False, 'error': f'Bet {bet_id} not found'}
            
        # Parse bet data
        stake = result[8]
        decimal_odds = result[7]
        current_status = result[15]
        
        if current_status != BetStatus.PENDING.value:
            conn.close()
            return {'success': False, 'error': f'Bet already settled as {current_status}'}
            
        # Use actual odds if provided, otherwise use original
        odds_used = actual_odds if actual_odds else decimal_odds
        
        # Calculate profit/loss
        if status == BetStatus.WON:
            profit_loss = stake * (odds_used - 1.0)
        elif status == BetStatus.LOST:
            profit_loss = -stake
        elif status in [BetStatus.PUSHED, BetStatus.CANCELLED]:
            profit_loss = 0.0
        else:
            conn.close()
            return {'success': False, 'error': f'Invalid status: {status}'}
            
        # Update bet
        result_timestamp = datetime.utcnow().isoformat()
        cursor.execute("""
            UPDATE bets SET 
                status = ?,
                result_timestamp = ?,
                profit_loss = ?,
                actual_odds = ?
            WHERE bet_id = ?
        """, (status.value, result_timestamp, profit_loss, odds_used, bet_id))
        
        conn.commit()
        conn.close()
        
        # Update bankroll snapshot
        self._create_snapshot(f"Settled bet {bet_id}: {status.value}")
        
        logger.info(f"Settled bet {bet_id}: {status.value}, P/L: ${profit_loss:.2f}")
        
        return {
            'success': True,
            'bet_id': bet_id,
            'status': status.value,
            'profit_loss': profit_loss,
            'new_bankroll': self._get_current_bankroll()
        }
        
    def _create_snapshot(self, notes: str = ""):
        """Create bankroll snapshot"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get all bets
        cursor.execute("SELECT * FROM bets")
        all_bets = cursor.fetchall()
        
        # Calculate metrics
        total_bets = len(all_bets)
        won_bets = sum(1 for b in all_bets if b[15] == BetStatus.WON.value)
        lost_bets = sum(1 for b in all_bets if b[15] == BetStatus.LOST.value)
        pending_bets = [b for b in all_bets if b[15] == BetStatus.PENDING.value]
        settled_bets = [b for b in all_bets if b[17] is not None]
        
        win_rate = won_bets / max(won_bets + lost_bets, 1)
        total_profit_loss = sum(b[17] for b in settled_bets if b[17])
        pending_amount = sum(b[8] for b in pending_bets)
        
        # Get starting bankroll
        cursor.execute("SELECT amount FROM transactions WHERE type = 'deposit' ORDER BY timestamp ASC LIMIT 1")
        starting = cursor.fetchone()
        starting_bankroll = starting[0] if starting else self.starting_bankroll
        
        total_bankroll = starting_bankroll + total_profit_loss
        available_bankroll = total_bankroll - pending_amount
        
        roi = (total_profit_loss / starting_bankroll) * 100 if starting_bankroll > 0 else 0
        
        # Calculate additional metrics
        stakes = [b[8] for b in all_bets if b[8]]
        largest_bet = max(stakes) if stakes else 0
        average_bet = sum(stakes) / len(stakes) if stakes else 0
        
        # Simplified Sharpe and drawdown (would need more sophisticated calculation)
        sharpe_ratio = roi / max(abs(roi), 1) if settled_bets else 0
        max_drawdown = 0  # Would track historically
        
        # Create snapshot
        snapshot = BankrollSnapshot(
            timestamp=datetime.utcnow().isoformat(),
            total_bankroll=total_bankroll,
            available_bankroll=available_bankroll,
            pending_amount=pending_amount,
            total_bets=total_bets,
            won_bets=won_bets,
            lost_bets=lost_bets,
            win_rate=win_rate,
            roi=roi,
            profit_loss=total_profit_loss,
            largest_bet=largest_bet,
            average_bet=average_bet,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            notes=notes
        )
        
        cursor.execute("""
            INSERT INTO snapshots VALUES (
                NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            snapshot.timestamp, snapshot.total_bankroll, snapshot.available_bankroll,
            snapshot.pending_amount, snapshot.total_bets, snapshot.won_bets,
            snapshot.lost_bets, snapshot.win_rate, snapshot.roi,
            snapshot.profit_loss, snapshot.largest_bet, snapshot.average_bet,
            snapshot.sharpe_ratio, snapshot.max_drawdown, snapshot.notes
        ))
        
        conn.commit()
        conn.close()
        
    def _record_deposit(self, amount: float, notes: str = ""):
        """Record a deposit"""
        current = self._get_current_bankroll() or 0
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO transactions VALUES (
                NULL, ?, 'deposit', ?, ?, ?, ?
            )
        """, (
            datetime.utcnow().isoformat(),
            amount,
            current,
            current + amount,
            notes
        ))
        
        conn.commit()
        conn.close()
        
        self._create_snapshot(f"Deposit: ${amount:.2f}")
        
    def deposit(self, amount: float, notes: str = "") -> Dict[str, any]:
        """Add funds to bankroll"""
        if amount <= 0:
            return {'success': False, 'error': 'Amount must be positive'}
            
        self._record_deposit(amount, notes)
        new_bankroll = self._get_current_bankroll()
        
        logger.info(f"Deposited ${amount:.2f}. New bankroll: ${new_bankroll:.2f}")
        
        return {
            'success': True,
            'amount': amount,
            'new_bankroll': new_bankroll
        }
        
    def withdraw(self, amount: float, notes: str = "") -> Dict[str, any]:
        """Withdraw funds from bankroll"""
        available = self.get_available_bankroll()
        
        if amount <= 0:
            return {'success': False, 'error': 'Amount must be positive'}
            
        if amount > available:
            return {
                'success': False,
                'error': f'Insufficient funds. Available: ${available:.2f}'
            }
            
        current = self._get_current_bankroll()
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO transactions VALUES (
                NULL, ?, 'withdrawal', ?, ?, ?, ?
            )
        """, (
            datetime.utcnow().isoformat(),
            -amount,
            current,
            current - amount,
            notes
        ))
        
        conn.commit()
        conn.close()
        
        self._create_snapshot(f"Withdrawal: ${amount:.2f}")
        new_bankroll = self._get_current_bankroll()
        
        logger.info(f"Withdrew ${amount:.2f}. New bankroll: ${new_bankroll:.2f}")
        
        return {
            'success': True,
            'amount': amount,
            'new_bankroll': new_bankroll
        }
        
    def get_risk_metrics(self) -> RiskMetrics:
        """Calculate comprehensive risk metrics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM bets")
        all_bets = cursor.fetchall()
        
        conn.close()
        
        if not all_bets:
            return RiskMetrics(
                total_exposure=0, exposure_percent=0, max_single_bet_percent=0,
                kelly_compliance=0, correlation_risk=0, sharpe_ratio=0,
                sortino_ratio=0, max_drawdown=0, current_drawdown=0,
                win_rate=0, avg_winning_bet=0, avg_losing_bet=0,
                largest_win=0, largest_loss=0, consecutive_wins=0,
                consecutive_losses=0, risk_of_ruin=0
            )
            
        # Basic calculations
        pending = [b for b in all_bets if b[15] == BetStatus.PENDING.value]
        won = [b for b in all_bets if b[15] == BetStatus.WON.value]
        lost = [b for b in all_bets if b[15] == BetStatus.LOST.value]
        settled = won + lost
        
        total_exposure = sum(b[8] for b in pending)
        current_bankroll = self._get_current_bankroll()
        exposure_percent = (total_exposure / current_bankroll) * 100 if current_bankroll > 0 else 0
        
        stakes = [b[8] for b in all_bets]
        max_single = max(stakes) if stakes else 0
        max_single_percent = (max_single / current_bankroll) * 100 if current_bankroll > 0 else 0
        
        # Kelly compliance
        kelly_compliant = sum(1 for b in all_bets if abs(b[8] - b[9]) < 1.0)
        kelly_compliance = (kelly_compliant / len(all_bets)) * 100 if all_bets else 0
        
        # Win metrics
        win_rate = len(won) / len(settled) * 100 if settled else 0
        avg_winning = sum(b[17] for b in won) / len(won) if won else 0
        avg_losing = sum(abs(b[17]) for b in lost) / len(lost) if lost else 0
        largest_win = max((b[17] for b in won), default=0)
        largest_loss = min((b[17] for b in lost), default=0)
        
        # Streak tracking (simplified)
        consecutive_wins = 0
        consecutive_losses = 0
        current_streak = 0
        for bet in reversed(settled):
            if bet[15] == BetStatus.WON.value:
                current_streak += 1
                consecutive_wins = max(consecutive_wins, current_streak)
            else:
                current_streak = 0
                
        # Risk of ruin (simplified)
        risk_of_ruin = max(0, min(100, (1 - win_rate/100) * 50))
        
        return RiskMetrics(
            total_exposure=total_exposure,
            exposure_percent=exposure_percent,
            max_single_bet_percent=max_single_percent,
            kelly_compliance=kelly_compliance,
            correlation_risk=0,  # Would need correlation analysis
            sharpe_ratio=0,  # Would need return variance
            sortino_ratio=0,  # Would need downside deviation
            max_drawdown=0,  # Would need historical tracking
            current_drawdown=0,
            win_rate=win_rate,
            avg_winning_bet=avg_winning,
            avg_losing_bet=avg_losing,
            largest_win=largest_win,
            largest_loss=largest_loss,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses,
            risk_of_ruin=risk_of_ruin
        )
        
    def generate_report(self, output_path: Optional[str] = None) -> Dict:
        """Generate comprehensive bankroll report"""
        snapshot = self._get_latest_snapshot()
        risk = self.get_risk_metrics()
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'bankroll': {
                'total': self._get_current_bankroll(),
                'available': self.get_available_bankroll(),
                'pending': self._get_pending_amount(),
                'starting': self.starting_bankroll
            },
            'performance': {
                'total_bets': snapshot.total_bets if snapshot else 0,
                'won': snapshot.won_bets if snapshot else 0,
                'lost': snapshot.lost_bets if snapshot else 0,
                'win_rate': snapshot.win_rate * 100 if snapshot else 0,
                'roi': snapshot.roi if snapshot else 0,
                'profit_loss': snapshot.profit_loss if snapshot else 0
            },
            'risk_metrics': asdict(risk),
            'parameters': {
                'kelly_fraction': self.kelly_fraction,
                'max_single_bet': self.max_single_bet * 100,
                'max_exposure': self.max_total_exposure * 100,
                'min_bankroll': self.min_bankroll_percent * 100
            }
        }
        
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {output_path}")
            
        return report
        
    def _get_latest_snapshot(self) -> Optional[BankrollSnapshot]:
        """Get most recent snapshot"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM snapshots ORDER BY timestamp DESC LIMIT 1
        """)
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
            
        return BankrollSnapshot(
            timestamp=result[1],
            total_bankroll=result[2],
            available_bankroll=result[3],
            pending_amount=result[4],
            total_bets=result[5],
            won_bets=result[6],
            lost_bets=result[7],
            win_rate=result[8],
            roi=result[9],
            profit_loss=result[10],
            largest_bet=result[11],
            average_bet=result[12],
            sharpe_ratio=result[13],
            max_drawdown=result[14],
            notes=result[15]
        )


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(description="EQ12 Bankroll Manager")
    parser.add_argument('--db', default='../logs/eq12_bankroll.db', help='Database path')
    parser.add_argument('--bankroll', type=float, default=10000.0, help='Starting bankroll')
    parser.add_argument('--action', choices=['status', 'deposit', 'withdraw', 'report'], 
                       default='status', help='Action to perform')
    parser.add_argument('--amount', type=float, help='Amount for deposit/withdrawal')
    parser.add_argument('--output', help='Report output path')
    
    args = parser.parse_args()
    
    manager = EQ12BankrollManager(args.db, args.bankroll)
    
    if args.action == 'status':
        print(f"\n💰 EQ12 BANKROLL STATUS")
        print(f"=" * 50)
        print(f"Total Bankroll: ${manager._get_current_bankroll():,.2f}")
        print(f"Available: ${manager.get_available_bankroll():,.2f}")
        print(f"Pending: ${manager._get_pending_amount():,.2f}")
        
        snapshot = manager._get_latest_snapshot()
        if snapshot:
            print(f"\n📊 PERFORMANCE")
            print(f"Total Bets: {snapshot.total_bets}")
            print(f"Win Rate: {snapshot.win_rate*100:.1f}%")
            print(f"ROI: {snapshot.roi:.2f}%")
            print(f"P/L: ${snapshot.profit_loss:,.2f}")
            
    elif args.action == 'deposit':
        if not args.amount:
            print("Error: --amount required for deposit")
            return
        result = manager.deposit(args.amount)
        print(f"✅ Deposited ${args.amount:,.2f}")
        print(f"New Bankroll: ${result['new_bankroll']:,.2f}")
        
    elif args.action == 'withdraw':
        if not args.amount:
            print("Error: --amount required for withdrawal")
            return
        result = manager.withdraw(args.amount)
        if result['success']:
            print(f"✅ Withdrew ${args.amount:,.2f}")
            print(f"New Bankroll: ${result['new_bankroll']:,.2f}")
        else:
            print(f"❌ {result['error']}")
            
    elif args.action == 'report':
        output = args.output or '../reports/bankroll_report.json'
        report = manager.generate_report(output)
        print(f"✅ Report generated: {output}")
        print(f"\nROI: {report['performance']['roi']:.2f}%")
        print(f"Win Rate: {report['performance']['win_rate']:.1f}%")
        

if __name__ == '__main__':
    main()
