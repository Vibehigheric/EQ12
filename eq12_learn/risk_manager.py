"""
EQ12 Advanced Risk Management System
Comprehensive risk controls for parlay betting with mathematical safeguards.

Implements Kelly criterion, correlation analysis, and cost controls.
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
from enum import Enum

# Logging setup
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classifications."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class RiskMetrics:
    """Comprehensive risk assessment metrics."""
    kelly_fraction: float
    correlation_score: float
    volatility_score: float
    liquidity_risk: float
    concentration_risk: float
    model_confidence: float
    overall_risk_score: float
    risk_level: RiskLevel
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class BankrollState:
    """Current bankroll and position tracking."""
    total_bankroll: float
    available_balance: float
    outstanding_bets: float
    daily_exposure: float
    weekly_exposure: float
    max_loss_streak: int
    current_loss_streak: int
    last_update: datetime = field(default_factory=datetime.now)


@dataclass
class PositionLimit:
    """Position sizing limits and constraints."""
    max_single_bet: float
    max_daily_exposure: float
    max_weekly_exposure: float
    max_correlation_exposure: float
    max_sport_concentration: float
    kelly_multiplier: float = 0.25  # Conservative Kelly fraction


class AdvancedRiskManager:
    """Advanced risk management with mathematical controls."""
    
    # Risk parameters (configurable)
    DEFAULT_BANKROLL = 1000.0
    MAX_KELLY_FRACTION = 0.25
    MIN_WIN_PROBABILITY = 0.35
    MIN_EXPECTED_VALUE = 0.15
    MAX_CORRELATION_SCORE = 0.6
    MAX_LEGS = 4
    MIN_CONFIDENCE = 0.65
    
    # Position limits
    MAX_SINGLE_BET_PCT = 0.05  # 5% of bankroll
    MAX_DAILY_EXPOSURE_PCT = 0.15  # 15% of bankroll
    MAX_WEEKLY_EXPOSURE_PCT = 0.35  # 35% of bankroll
    MAX_SPORT_CONCENTRATION_PCT = 0.25  # 25% in single sport
    
    # Loss limits
    MAX_DAILY_LOSS_PCT = 0.10  # 10% daily loss limit
    MAX_WEEKLY_LOSS_PCT = 0.20  # 20% weekly loss limit
    STOP_LOSS_STREAK = 5  # Stop after 5 consecutive losses
    
    def __init__(self, bankroll: float = None, config_file: str = None):
        self.bankroll = bankroll or self.DEFAULT_BANKROLL
        
        # Load configuration
        if config_file and Path(config_file).exists():
            self._load_config(config_file)
        
        # Initialize tracking
        self.bankroll_state = BankrollState(
            total_bankroll=self.bankroll,
            available_balance=self.bankroll,
            outstanding_bets=0.0,
            daily_exposure=0.0,
            weekly_exposure=0.0,
            max_loss_streak=0,
            current_loss_streak=0
        )
        
        # Position limits
        self.position_limits = PositionLimit(
            max_single_bet=self.bankroll * self.MAX_SINGLE_BET_PCT,
            max_daily_exposure=self.bankroll * self.MAX_DAILY_EXPOSURE_PCT,
            max_weekly_exposure=self.bankroll * self.MAX_WEEKLY_EXPOSURE_PCT,
            max_correlation_exposure=self.bankroll * 0.1,  # 10% correlated exposure
            max_sport_concentration=self.bankroll * self.MAX_SPORT_CONCENTRATION_PCT
        )
        
        # Risk tracking
        self.risk_history: List[RiskMetrics] = []
        self.active_positions: Dict[str, Dict] = {}
        self.loss_history: List[Dict] = []
        
    def _load_config(self, config_file: str):
        """Load risk management configuration."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            # Override defaults with config values
            self.MAX_KELLY_FRACTION = config.get('max_kelly_fraction', self.MAX_KELLY_FRACTION)
            self.MIN_WIN_PROBABILITY = config.get('min_win_probability', self.MIN_WIN_PROBABILITY)
            self.MIN_EXPECTED_VALUE = config.get('min_expected_value', self.MIN_EXPECTED_VALUE)
            
            logger.info(f"Loaded risk config from {config_file}")
            
        except Exception as e:
            logger.warning(f"Failed to load config {config_file}: {e}")
    
    def calculate_kelly_fraction(self, win_prob: float, 
                               decimal_odds: float, 
                               confidence: float = 1.0) -> float:
        """Calculate Kelly criterion with confidence adjustment."""
        b = decimal_odds - 1  # Net odds received
        q = 1 - win_prob     # Loss probability
        
        # Basic Kelly calculation
        kelly = (b * win_prob - q) / b
        
        # Confidence adjustment (reduce bet size for lower confidence)
        confidence_adjusted_kelly = kelly * confidence
        
        # Apply maximum Kelly fraction limit
        safe_kelly = max(0, min(confidence_adjusted_kelly, self.MAX_KELLY_FRACTION))
        
        return safe_kelly
    
    def calculate_correlation_matrix(self, legs: List[Dict]) -> np.ndarray:
        """Calculate correlation matrix between parlay legs."""
        n_legs = len(legs)
        correlation_matrix = np.eye(n_legs)  # Start with identity matrix
        
        for i in range(n_legs):
            for j in range(i + 1, n_legs):
                correlation = self._calculate_pairwise_correlation(legs[i], legs[j])
                correlation_matrix[i, j] = correlation
                correlation_matrix[j, i] = correlation  # Symmetric matrix
                
        return correlation_matrix
    
    def _calculate_pairwise_correlation(self, leg1: Dict, leg2: Dict) -> float:
        """Calculate correlation between two bet legs."""
        correlation = 0.0
        
        # Same game correlation (highest)
        if (leg1.get('team') == leg2.get('team') or 
            leg1.get('opponent') == leg2.get('opponent')):
            correlation += 0.8
            
        # Same sport, same day correlation
        elif (leg1.get('sport') == leg2.get('sport') and
              self._same_day(leg1.get('game_time'), leg2.get('game_time'))):
            correlation += 0.3
            
        # Same sport correlation
        elif leg1.get('sport') == leg2.get('sport'):
            correlation += 0.1
            
        # Player prop correlations
        if (leg1.get('bet_type') == 'prop' and leg2.get('bet_type') == 'prop' and
            leg1.get('player') == leg2.get('player')):
            correlation += 0.9  # Same player props highly correlated
            
        # Weather/venue correlations
        if (leg1.get('venue') == leg2.get('venue') and 
            leg1.get('sport') in ['NFL', 'MLB']):  # Outdoor sports
            correlation += 0.2
            
        return min(correlation, 1.0)  # Cap at 1.0
    
    def _same_day(self, time1: Optional[datetime], time2: Optional[datetime]) -> bool:
        """Check if two times are on the same day."""
        if not time1 or not time2:
            return False
        return time1.date() == time2.date()
    
    def calculate_portfolio_volatility(self, positions: List[Dict]) -> float:
        """Calculate portfolio volatility using correlation adjustments."""
        if not positions:
            return 0.0
            
        # Extract individual position volatilities
        volatilities = []
        weights = []
        
        for pos in positions:
            # Estimate volatility from odds and stake
            odds = pos.get('decimal_odds', 2.0)
            stake = pos.get('stake', 0.0)
            
            # Higher odds = higher volatility
            individual_vol = min(1.0, (odds - 1) / 10.0)
            volatilities.append(individual_vol)
            weights.append(stake / self.bankroll)
            
        if len(volatilities) < 2:
            return volatilities[0] if volatilities else 0.0
            
        # Portfolio volatility with correlation
        weights = np.array(weights)
        volatilities = np.array(volatilities)
        
        # Simplified correlation matrix (assume 0.3 correlation between positions)
        correlation_matrix = np.full((len(positions), len(positions)), 0.3)
        np.fill_diagonal(correlation_matrix, 1.0)
        
        # Portfolio variance
        portfolio_var = np.dot(weights, np.dot(correlation_matrix * np.outer(volatilities, volatilities), weights))
        
        return np.sqrt(portfolio_var)
    
    def calculate_liquidity_risk(self, legs: List[Dict]) -> float:
        """Calculate liquidity risk based on bet types and markets."""
        risk_score = 0.0
        
        for leg in legs:
            bet_type = leg.get('bet_type', '').lower()
            sport = leg.get('sport', '').upper()
            
            # Bet type risk
            if bet_type == 'prop':
                risk_score += 0.4  # Player props less liquid
            elif bet_type in ['alt_spread', 'alt_total']:
                risk_score += 0.3  # Alternative lines less liquid
            elif bet_type in ['spread', 'total']:
                risk_score += 0.1  # Standard bets most liquid
                
            # Sport risk
            if sport in ['NFL', 'NBA', 'MLB']:
                risk_score += 0.0  # Major sports most liquid
            elif sport in ['NHL', 'NCAAF', 'NCAAB']:
                risk_score += 0.1  # Moderate liquidity
            else:
                risk_score += 0.3  # Minor sports less liquid
                
        return min(risk_score / len(legs), 1.0) if legs else 0.0
    
    def calculate_concentration_risk(self, current_positions: List[Dict], 
                                  new_position: Dict) -> float:
        """Calculate concentration risk across portfolio."""
        sport_exposure = {}
        team_exposure = {}
        bet_type_exposure = {}
        
        # Include existing positions
        for pos in current_positions:
            sport = pos.get('sport', 'UNKNOWN')
            team = pos.get('team', 'UNKNOWN')
            bet_type = pos.get('bet_type', 'UNKNOWN')
            stake = pos.get('stake', 0.0)
            
            sport_exposure[sport] = sport_exposure.get(sport, 0) + stake
            team_exposure[team] = team_exposure.get(team, 0) + stake
            bet_type_exposure[bet_type] = bet_type_exposure.get(bet_type, 0) + stake
            
        # Add new position
        new_sport = new_position.get('sport', 'UNKNOWN')
        new_team = new_position.get('team', 'UNKNOWN')
        new_bet_type = new_position.get('bet_type', 'UNKNOWN')
        new_stake = new_position.get('stake', 0.0)
        
        sport_exposure[new_sport] = sport_exposure.get(new_sport, 0) + new_stake
        team_exposure[new_team] = team_exposure.get(new_team, 0) + new_stake
        bet_type_exposure[new_bet_type] = bet_type_exposure.get(new_bet_type, 0) + new_stake
        
        # Calculate concentration scores
        max_sport_pct = max(sport_exposure.values()) / self.bankroll if sport_exposure else 0
        max_team_pct = max(team_exposure.values()) / self.bankroll if team_exposure else 0
        max_bet_type_pct = max(bet_type_exposure.values()) / self.bankroll if bet_type_exposure else 0
        
        # Combined concentration risk
        concentration_risk = (
            max(0, (max_sport_pct - self.MAX_SPORT_CONCENTRATION_PCT) * 2) +
            max(0, (max_team_pct - 0.15) * 3) +  # 15% team limit
            max(0, (max_bet_type_pct - 0.4) * 1)   # 40% bet type limit
        )
        
        return min(concentration_risk, 1.0)
    
    def assess_comprehensive_risk(self, parlay_legs: List[Dict],
                                stake: float, win_prob: float,
                                decimal_odds: float, confidence: float) -> RiskMetrics:
        """Perform comprehensive risk assessment."""
        
        # Kelly fraction
        kelly = self.calculate_kelly_fraction(win_prob, decimal_odds, confidence)
        
        # Correlation analysis
        correlation_matrix = self.calculate_correlation_matrix(parlay_legs)
        max_correlation = np.max(correlation_matrix - np.eye(len(parlay_legs)))
        
        # Portfolio metrics
        current_positions = list(self.active_positions.values())
        volatility = self.calculate_portfolio_volatility(current_positions + [{'decimal_odds': decimal_odds, 'stake': stake}])
        liquidity_risk = self.calculate_liquidity_risk(parlay_legs)
        concentration_risk = self.calculate_concentration_risk(current_positions, {'sport': parlay_legs[0].get('sport'), 'stake': stake})
        
        # Overall risk score (0-1, higher is riskier)
        overall_risk = (
            (1 - win_prob) * 0.3 +           # Probability risk
            max_correlation * 0.25 +         # Correlation risk
            volatility * 0.2 +               # Volatility risk
            liquidity_risk * 0.15 +          # Liquidity risk
            concentration_risk * 0.1         # Concentration risk
        )
        
        # Risk level classification
        if overall_risk < 0.3:
            risk_level = RiskLevel.LOW
        elif overall_risk < 0.5:
            risk_level = RiskLevel.MEDIUM
        elif overall_risk < 0.7:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.EXTREME
            
        # Generate warnings and recommendations
        warnings = []
        recommendations = []
        
        if kelly < 0.01:
            warnings.append("Kelly fraction very low - consider skipping this bet")
        if max_correlation > self.MAX_CORRELATION_SCORE:
            warnings.append(f"High correlation detected: {max_correlation:.2f}")
        if volatility > 0.8:
            warnings.append("High portfolio volatility")
        if concentration_risk > 0.5:
            warnings.append("High concentration risk")
            
        if win_prob < 0.4:
            recommendations.append("Consider higher probability bets")
        if stake > self.position_limits.max_single_bet:
            recommendations.append(f"Reduce stake to max ${self.position_limits.max_single_bet:.0f}")
        if liquidity_risk > 0.6:
            recommendations.append("Avoid illiquid markets")
            
        return RiskMetrics(
            kelly_fraction=kelly,
            correlation_score=max_correlation,
            volatility_score=volatility,
            liquidity_risk=liquidity_risk,
            concentration_risk=concentration_risk,
            model_confidence=confidence,
            overall_risk_score=overall_risk,
            risk_level=risk_level,
            warnings=warnings,
            recommendations=recommendations
        )
    
    def validate_bet(self, parlay_legs: List[Dict], stake: float,
                   win_prob: float, expected_value: float,
                   confidence: float, decimal_odds: float) -> Tuple[bool, List[str], RiskMetrics]:
        """Comprehensive bet validation with risk assessment."""
        
        violations = []
        
        # Basic parameter checks
        if len(parlay_legs) > self.MAX_LEGS:
            violations.append(f"Too many legs: {len(parlay_legs)} > {self.MAX_LEGS}")
            
        if win_prob < self.MIN_WIN_PROBABILITY:
            violations.append(f"Win probability too low: {win_prob:.2%} < {self.MIN_WIN_PROBABILITY:.2%}")
            
        if expected_value < self.MIN_EXPECTED_VALUE:
            violations.append(f"Expected value too low: {expected_value:.2%} < {self.MIN_EXPECTED_VALUE:.2%}")
            
        if confidence < self.MIN_CONFIDENCE:
            violations.append(f"Model confidence too low: {confidence:.2%} < {self.MIN_CONFIDENCE:.2%}")
            
        # Position sizing checks
        if stake > self.position_limits.max_single_bet:
            violations.append(f"Stake too large: ${stake:.0f} > ${self.position_limits.max_single_bet:.0f}")
            
        if (self.bankroll_state.daily_exposure + stake) > self.position_limits.max_daily_exposure:
            violations.append(f"Daily exposure limit exceeded")
            
        if (self.bankroll_state.weekly_exposure + stake) > self.position_limits.max_weekly_exposure:
            violations.append(f"Weekly exposure limit exceeded")
            
        # Loss streak protection
        if self.bankroll_state.current_loss_streak >= self.STOP_LOSS_STREAK:
            violations.append(f"Loss streak protection: {self.bankroll_state.current_loss_streak} consecutive losses")
            
        # Comprehensive risk assessment
        risk_metrics = self.assess_comprehensive_risk(
            parlay_legs, stake, win_prob, decimal_odds, confidence
        )
        
        # Risk level checks
        if risk_metrics.risk_level == RiskLevel.EXTREME:
            violations.append("Extreme risk level - bet rejected")
        elif risk_metrics.risk_level == RiskLevel.HIGH and confidence < 0.8:
            violations.append("High risk with low confidence - bet rejected")
            
        # Correlation checks
        if risk_metrics.correlation_score > self.MAX_CORRELATION_SCORE:
            violations.append(f"Correlation too high: {risk_metrics.correlation_score:.2f} > {self.MAX_CORRELATION_SCORE}")
            
        is_valid = len(violations) == 0
        
        return is_valid, violations, risk_metrics
    
    def calculate_optimal_stake(self, kelly_fraction: float, win_prob: float,
                              expected_value: float, risk_metrics: RiskMetrics) -> float:
        """Calculate optimal stake with risk adjustments."""
        
        # Base Kelly stake
        base_stake = kelly_fraction * self.bankroll
        
        # Risk adjustments
        risk_multiplier = 1.0
        
        # Reduce for high risk
        if risk_metrics.risk_level == RiskLevel.HIGH:
            risk_multiplier *= 0.5
        elif risk_metrics.risk_level == RiskLevel.MEDIUM:
            risk_multiplier *= 0.75
            
        # Reduce for low confidence
        if risk_metrics.model_confidence < 0.7:
            risk_multiplier *= 0.6
            
        # Reduce for high correlation
        if risk_metrics.correlation_score > 0.4:
            risk_multiplier *= (1 - risk_metrics.correlation_score * 0.5)
            
        # Reduce for high volatility
        if risk_metrics.volatility_score > 0.6:
            risk_multiplier *= 0.7
            
        # Apply adjustments
        adjusted_stake = base_stake * risk_multiplier
        
        # Hard limits
        max_stake = min(
            self.position_limits.max_single_bet,
            self.position_limits.max_daily_exposure - self.bankroll_state.daily_exposure,
            50.0  # Absolute maximum
        )
        
        return max(0, min(adjusted_stake, max_stake))
    
    def update_position(self, position_id: str, outcome: str, 
                       payout: float = 0.0, stake: float = 0.0):
        """Update position with outcome and adjust bankroll."""
        
        if position_id in self.active_positions:
            position = self.active_positions[position_id]
            
            # Update bankroll
            if outcome == 'win':
                self.bankroll_state.total_bankroll += (payout - stake)
                self.bankroll_state.available_balance += payout
                self.bankroll_state.current_loss_streak = 0
                
            elif outcome == 'loss':
                self.bankroll_state.total_bankroll -= stake
                self.bankroll_state.current_loss_streak += 1
                self.bankroll_state.max_loss_streak = max(
                    self.bankroll_state.max_loss_streak,
                    self.bankroll_state.current_loss_streak
                )
                
                # Record loss for analysis
                self.loss_history.append({
                    'timestamp': datetime.now(),
                    'amount': stake,
                    'position_id': position_id,
                    'streak': self.bankroll_state.current_loss_streak
                })
                
            # Remove from active positions
            del self.active_positions[position_id]
            
            # Update exposure tracking
            self.bankroll_state.outstanding_bets -= stake
            
        self._update_position_limits()
    
    def _update_position_limits(self):
        """Update position limits based on current bankroll."""
        self.position_limits.max_single_bet = self.bankroll_state.total_bankroll * self.MAX_SINGLE_BET_PCT
        self.position_limits.max_daily_exposure = self.bankroll_state.total_bankroll * self.MAX_DAILY_EXPOSURE_PCT
        self.position_limits.max_weekly_exposure = self.bankroll_state.total_bankroll * self.MAX_WEEKLY_EXPOSURE_PCT
    
    def get_risk_dashboard(self) -> Dict:
        """Get comprehensive risk dashboard data."""
        
        # Calculate current metrics
        available_pct = self.bankroll_state.available_balance / self.bankroll_state.total_bankroll
        exposure_pct = self.bankroll_state.outstanding_bets / self.bankroll_state.total_bankroll
        
        # Recent performance
        recent_losses = [loss for loss in self.loss_history 
                        if loss['timestamp'] > datetime.now() - timedelta(days=7)]
        weekly_loss_amount = sum(loss['amount'] for loss in recent_losses)
        
        return {
            'bankroll_status': {
                'total_bankroll': self.bankroll_state.total_bankroll,
                'available_balance': self.bankroll_state.available_balance,
                'available_percentage': available_pct,
                'outstanding_bets': self.bankroll_state.outstanding_bets,
                'exposure_percentage': exposure_pct
            },
            'position_limits': {
                'max_single_bet': self.position_limits.max_single_bet,
                'max_daily_exposure': self.position_limits.max_daily_exposure,
                'max_weekly_exposure': self.position_limits.max_weekly_exposure,
                'daily_exposure_used': self.bankroll_state.daily_exposure,
                'weekly_exposure_used': self.bankroll_state.weekly_exposure
            },
            'risk_metrics': {
                'current_loss_streak': self.bankroll_state.current_loss_streak,
                'max_loss_streak': self.bankroll_state.max_loss_streak,
                'weekly_loss_amount': weekly_loss_amount,
                'weekly_loss_percentage': weekly_loss_amount / self.bankroll_state.total_bankroll,
                'stop_loss_active': self.bankroll_state.current_loss_streak >= self.STOP_LOSS_STREAK
            },
            'active_positions': {
                'count': len(self.active_positions),
                'total_exposure': sum(pos.get('stake', 0) for pos in self.active_positions.values()),
                'positions': list(self.active_positions.values())
            },
            'configuration': {
                'max_kelly_fraction': self.MAX_KELLY_FRACTION,
                'min_win_probability': self.MIN_WIN_PROBABILITY,
                'min_expected_value': self.MIN_EXPECTED_VALUE,
                'stop_loss_streak': self.STOP_LOSS_STREAK
            }
        }
    
    def save_risk_state(self, filename: str = None) -> str:
        """Save current risk state to file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"C:/EQ12/logs/risk_state_{timestamp}.json"
            
        risk_state = {
            'timestamp': datetime.now().isoformat(),
            'bankroll_state': {
                'total_bankroll': self.bankroll_state.total_bankroll,
                'available_balance': self.bankroll_state.available_balance,
                'outstanding_bets': self.bankroll_state.outstanding_bets,
                'daily_exposure': self.bankroll_state.daily_exposure,
                'weekly_exposure': self.bankroll_state.weekly_exposure,
                'current_loss_streak': self.bankroll_state.current_loss_streak,
                'max_loss_streak': self.bankroll_state.max_loss_streak
            },
            'active_positions': self.active_positions,
            'recent_risk_history': [
                {
                    'overall_risk_score': rm.overall_risk_score,
                    'risk_level': rm.risk_level.value,
                    'kelly_fraction': rm.kelly_fraction,
                    'correlation_score': rm.correlation_score
                } for rm in self.risk_history[-10:]  # Last 10 assessments
            ],
            'loss_history': self.loss_history[-20:]  # Last 20 losses
        }
        
        with open(filename, 'w') as f:
            json.dump(risk_state, f, indent=2, default=str)
            
        logger.info(f"Risk state saved: {filename}")
        return filename


def main():
    """Demo of risk management system."""
    
    # Initialize risk manager
    risk_manager = AdvancedRiskManager(bankroll=1000.0)
    
    print("🛡️ EQ12 Advanced Risk Management System")
    print("=" * 50)
    
    # Sample parlay for risk assessment
    sample_legs = [
        {
            'team': 'KC',
            'opponent': 'LAC',
            'bet_type': 'spread',
            'sport': 'NFL',
            'game_time': datetime.now() + timedelta(hours=24)
        },
        {
            'team': 'DAL',
            'opponent': 'PHI',
            'bet_type': 'total',
            'sport': 'NFL', 
            'game_time': datetime.now() + timedelta(hours=48)
        }
    ]
    
    # Risk assessment
    win_prob = 0.45
    expected_value = 0.20
    confidence = 0.75
    decimal_odds = 3.5
    stake = 25.0
    
    print(f"\n📊 Risk Assessment:")
    print(f"Win Probability: {win_prob:.1%}")
    print(f"Expected Value: {expected_value:.1%}")
    print(f"Confidence: {confidence:.1%}")
    print(f"Stake: ${stake:.0f}")
    
    # Validate bet
    is_valid, violations, risk_metrics = risk_manager.validate_bet(
        sample_legs, stake, win_prob, expected_value, confidence, decimal_odds
    )
    
    print(f"\n✅ Bet Validation: {'APPROVED' if is_valid else 'REJECTED'}")
    
    if violations:
        print("❌ Violations:")
        for violation in violations:
            print(f"  - {violation}")
    
    print(f"\n🎯 Risk Metrics:")
    print(f"Kelly Fraction: {risk_metrics.kelly_fraction:.2%}")
    print(f"Correlation Score: {risk_metrics.correlation_score:.2f}")
    print(f"Volatility: {risk_metrics.volatility_score:.2f}")
    print(f"Liquidity Risk: {risk_metrics.liquidity_risk:.2f}")
    print(f"Concentration Risk: {risk_metrics.concentration_risk:.2f}")
    print(f"Overall Risk: {risk_metrics.overall_risk_score:.2f} ({risk_metrics.risk_level.value})")
    
    if risk_metrics.warnings:
        print("\n⚠️ Warnings:")
        for warning in risk_metrics.warnings:
            print(f"  - {warning}")
    
    if risk_metrics.recommendations:
        print("\n💡 Recommendations:")
        for rec in risk_metrics.recommendations:
            print(f"  - {rec}")
    
    # Calculate optimal stake
    optimal_stake = risk_manager.calculate_optimal_stake(
        risk_metrics.kelly_fraction, win_prob, expected_value, risk_metrics
    )
    
    print(f"\n💰 Optimal Stake: ${optimal_stake:.0f}")
    
    # Risk dashboard
    dashboard = risk_manager.get_risk_dashboard()
    
    print(f"\n📈 Risk Dashboard:")
    print(f"Available Balance: ${dashboard['bankroll_status']['available_balance']:.0f} "
          f"({dashboard['bankroll_status']['available_percentage']:.1%})")
    print(f"Current Exposure: ${dashboard['bankroll_status']['outstanding_bets']:.0f} "
          f"({dashboard['bankroll_status']['exposure_percentage']:.1%})")
    print(f"Loss Streak: {dashboard['risk_metrics']['current_loss_streak']}")
    print(f"Active Positions: {dashboard['active_positions']['count']}")
    
    # Save risk state
    filename = risk_manager.save_risk_state()
    print(f"\n💾 Risk state saved: {filename}")


if __name__ == "__main__":
    main()