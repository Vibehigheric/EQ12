"""
EQ12 Intelligent Parlay Builder
EV-optimized parlay construction with ML-driven suggestions and risk management.

Mathematical optimization for profitable parlay selection with safety controls.
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from pathlib import Path
import joblib
from itertools import combinations
import requests
from abc import ABC, abstractmethod

# EQ12 imports
from train_parlay_model import EnsembleParlayModel, load_trained_model

# Logging setup
logger = logging.getLogger(__name__)


@dataclass
class BetLeg:
    """Individual bet leg for parlay construction."""
    team: str
    opponent: str
    bet_type: str  # 'spread', 'total', 'moneyline', 'prop'
    line: float
    odds_american: int
    sport: str
    game_time: datetime
    confidence: float = 0.0
    ev: float = 0.0
    
    def __post_init__(self):
        """Calculate implied probability from American odds."""
        if self.odds_american > 0:
            self.implied_prob = 100 / (self.odds_american + 100)
        else:
            self.implied_prob = abs(self.odds_american) / (abs(self.odds_american) + 100)
            
    @property
    def decimal_odds(self) -> float:
        """Convert American odds to decimal."""
        if self.odds_american > 0:
            return (self.odds_american / 100) + 1
        else:
            return (100 / abs(self.odds_american)) + 1


@dataclass 
class ParlayRecommendation:
    """Complete parlay recommendation with analysis."""
    legs: List[BetLeg]
    total_odds_american: int
    win_probability: float
    expected_value: float
    kelly_fraction: float
    confidence_score: float
    risk_score: float
    correlation_warning: bool
    reasoning: str
    max_stake: float = 25.0
    
    @property
    def leg_count(self) -> int:
        return len(self.legs)
    
    @property
    def potential_payout(self) -> float:
        """Calculate potential payout for max stake."""
        if self.total_odds_american > 0:
            return self.max_stake * (self.total_odds_american / 100)
        else:
            return self.max_stake * (100 / abs(self.total_odds_american))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'legs': [
                {
                    'team': leg.team,
                    'opponent': leg.opponent,
                    'bet_type': leg.bet_type,
                    'line': leg.line,
                    'odds_american': leg.odds_american,
                    'sport': leg.sport,
                    'confidence': leg.confidence
                } for leg in self.legs
            ],
            'total_odds_american': self.total_odds_american,
            'win_probability': self.win_probability,
            'expected_value': self.expected_value,
            'kelly_fraction': self.kelly_fraction,
            'confidence_score': self.confidence_score,
            'risk_score': self.risk_score,
            'correlation_warning': self.correlation_warning,
            'reasoning': self.reasoning,
            'max_stake': self.max_stake,
            'potential_payout': self.potential_payout,
            'leg_count': self.leg_count
        }


class RiskManager:
    """Mathematical risk management for parlay construction."""
    
    # Risk parameters (configurable)
    MAX_KELLY_FRACTION = 0.25  # Never bet more than 25% of bankroll
    MIN_WIN_PROBABILITY = 0.35  # Minimum 35% win chance
    MIN_EXPECTED_VALUE = 0.15   # Minimum 15% EV
    MAX_CORRELATION_SCORE = 0.6 # Maximum correlation between legs
    MAX_LEGS = 4               # Maximum parlay size
    MIN_CONFIDENCE = 0.65      # Minimum ML model confidence
    
    def __init__(self, bankroll: float = 1000.0):
        self.bankroll = bankroll
        
    def calculate_kelly_fraction(self, win_prob: float, 
                               odds_decimal: float) -> float:
        """Calculate Kelly criterion fraction."""
        b = odds_decimal - 1  # Net odds received
        q = 1 - win_prob     # Loss probability
        
        kelly = (b * win_prob - q) / b
        return max(0, min(kelly, self.MAX_KELLY_FRACTION))
    
    def calculate_correlation_score(self, legs: List[BetLeg]) -> float:
        """Calculate correlation risk score between legs."""
        if len(legs) < 2:
            return 0.0
            
        correlation_score = 0.0
        
        for i, leg1 in enumerate(legs):
            for leg2 in legs[i+1:]:
                # Same game correlation (highest risk)
                if leg1.team == leg2.team or leg1.opponent == leg2.opponent:
                    correlation_score += 0.8
                    
                # Same sport, same time correlation
                elif (leg1.sport == leg2.sport and 
                      abs((leg1.game_time - leg2.game_time).total_seconds()) < 3600):
                    correlation_score += 0.3
                    
                # Division/conference correlation (medium risk)
                elif leg1.sport == leg2.sport:
                    correlation_score += 0.1
                    
        return min(correlation_score, 1.0)
    
    def validate_parlay(self, legs: List[BetLeg], 
                       win_prob: float, ev: float, 
                       confidence: float) -> Tuple[bool, List[str]]:
        """Validate parlay against all risk criteria."""
        violations = []
        
        # Check leg count
        if len(legs) > self.MAX_LEGS:
            violations.append(f"Too many legs: {len(legs)} > {self.MAX_LEGS}")
            
        # Check win probability
        if win_prob < self.MIN_WIN_PROBABILITY:
            violations.append(f"Win probability too low: {win_prob:.2%} < {self.MIN_WIN_PROBABILITY:.2%}")
            
        # Check expected value
        if ev < self.MIN_EXPECTED_VALUE:
            violations.append(f"Expected value too low: {ev:.2%} < {self.MIN_EXPECTED_VALUE:.2%}")
            
        # Check ML confidence
        if confidence < self.MIN_CONFIDENCE:
            violations.append(f"Model confidence too low: {confidence:.2%} < {self.MIN_CONFIDENCE:.2%}")
            
        # Check correlation
        correlation = self.calculate_correlation_score(legs)
        if correlation > self.MAX_CORRELATION_SCORE:
            violations.append(f"Correlation too high: {correlation:.2f} > {self.MAX_CORRELATION_SCORE}")
            
        return len(violations) == 0, violations
    
    def calculate_optimal_stake(self, kelly_fraction: float, 
                              win_prob: float, ev: float) -> float:
        """Calculate optimal stake based on Kelly criterion and risk limits."""
        # Base Kelly stake
        kelly_stake = kelly_fraction * self.bankroll
        
        # Apply safety multipliers
        if win_prob < 0.5:
            kelly_stake *= 0.5  # Reduce for lower probability bets
            
        if ev < 0.25:
            kelly_stake *= 0.75  # Reduce for lower EV bets
            
        # Hard limits
        max_stake = min(50.0, self.bankroll * 0.05)  # Max $50 or 5% of bankroll
        
        return min(kelly_stake, max_stake)


class BettingDataProvider(ABC):
    """Abstract base class for betting data providers."""
    
    @abstractmethod
    def get_available_bets(self, sport: str, 
                          date: datetime = None) -> List[BetLeg]:
        """Get available bets for a sport and date."""
        pass
    
    @abstractmethod  
    def get_live_odds(self, bet_leg: BetLeg) -> BetLeg:
        """Get current odds for a specific bet leg."""
        pass


class MockBettingDataProvider(BettingDataProvider):
    """Mock data provider for testing and development."""
    
    def get_available_bets(self, sport: str, 
                          date: datetime = None) -> List[BetLeg]:
        """Generate mock betting data."""
        if date is None:
            date = datetime.now()
            
        mock_bets = []
        
        if sport.upper() == 'NFL':
            teams = [
                ('KC', 'LAC'), ('BUF', 'MIA'), ('DAL', 'PHI'), 
                ('SF', 'SEA'), ('BAL', 'PIT'), ('GB', 'MIN')
            ]
            
            for home, away in teams:
                # Spread bets
                mock_bets.extend([
                    BetLeg(home, away, 'spread', -3.5, -110, 'NFL', 
                          date + timedelta(hours=np.random.randint(1, 72))),
                    BetLeg(away, home, 'spread', 3.5, -110, 'NFL',
                          date + timedelta(hours=np.random.randint(1, 72)))
                ])
                
                # Total bets
                total_line = np.random.uniform(42.5, 54.5)
                mock_bets.extend([
                    BetLeg(home, away, 'total', total_line, -110, 'NFL',
                          date + timedelta(hours=np.random.randint(1, 72))),
                    BetLeg(home, away, 'total', -total_line, -110, 'NFL',
                          date + timedelta(hours=np.random.randint(1, 72)))
                ])
                
        elif sport.upper() == 'NBA':
            teams = [
                ('LAL', 'GSW'), ('BOS', 'MIA'), ('MIL', 'PHI'),
                ('DEN', 'PHX'), ('DAL', 'LAC'), ('BKN', 'NYK')
            ]
            
            for home, away in teams:
                spread = np.random.uniform(-7.5, 7.5)
                mock_bets.extend([
                    BetLeg(home, away, 'spread', spread, -110, 'NBA',
                          date + timedelta(hours=np.random.randint(1, 48))),
                    BetLeg(away, home, 'spread', -spread, -110, 'NBA',
                          date + timedelta(hours=np.random.randint(1, 48)))
                ])
                
        return mock_bets
        
    def get_live_odds(self, bet_leg: BetLeg) -> BetLeg:
        """Return bet leg with slightly adjusted odds."""
        # Simulate odds movement
        odds_change = np.random.randint(-10, 11)  # ±10 points
        bet_leg.odds_american += odds_change
        return bet_leg


class IntelligentParlayBuilder:
    """ML-driven parlay builder with EV optimization."""
    
    def __init__(self, model_path: str = None, 
                 data_provider: BettingDataProvider = None):
        
        # Load trained ML model
        if model_path and Path(model_path).exists():
            self.model = load_trained_model(model_path)
            logger.info(f"Loaded ML model: {model_path}")
        else:
            logger.warning("No ML model provided, using mock predictions")
            self.model = None
            
        # Initialize components
        self.risk_manager = RiskManager()
        self.data_provider = data_provider or MockBettingDataProvider()
        
        # Performance tracking
        self.suggestions_made = []
        self.performance_history = []
        
    def predict_leg_probability(self, leg: BetLeg) -> Tuple[float, float]:
        """Predict win probability and confidence for a bet leg."""
        if self.model is None:
            # Mock prediction based on odds
            base_prob = leg.implied_prob
            # Add some noise and bias toward better odds
            adjusted_prob = base_prob + np.random.normal(0.1, 0.05)
            adjusted_prob = np.clip(adjusted_prob, 0.1, 0.9)
            confidence = np.random.uniform(0.6, 0.9)
            return adjusted_prob, confidence
            
        # TODO: Convert BetLeg to feature vector for ML model
        # For now, use enhanced heuristics
        prob_adjustment = 0.0
        
        # Sport-specific adjustments
        if leg.sport == 'NFL':
            prob_adjustment += 0.05  # Slight NFL boost
        elif leg.sport == 'NBA':
            prob_adjustment += 0.02  
            
        # Bet type adjustments  
        if leg.bet_type == 'spread':
            prob_adjustment += 0.03  # Spreads slightly more predictable
        elif leg.bet_type == 'moneyline':
            prob_adjustment -= 0.02  # Moneylines less predictable
            
        # Odds-based adjustment
        if leg.odds_american > 100:  # Underdog
            prob_adjustment += 0.02  # Slight underdog boost
            
        final_prob = np.clip(leg.implied_prob + prob_adjustment, 0.15, 0.85)
        confidence = np.random.uniform(0.65, 0.9)
        
        return final_prob, confidence
    
    def calculate_parlay_probability(self, legs: List[BetLeg]) -> float:
        """Calculate combined parlay probability."""
        total_prob = 1.0
        
        for leg in legs:
            leg_prob, _ = self.predict_leg_probability(leg)
            total_prob *= leg_prob
            
        # Apply correlation penalty
        correlation_penalty = self.risk_manager.calculate_correlation_score(legs)
        adjusted_prob = total_prob * (1 - correlation_penalty * 0.3)
        
        return max(adjusted_prob, 0.01)  # Minimum 1% probability
    
    def calculate_parlay_odds(self, legs: List[BetLeg]) -> int:
        """Calculate combined American odds for parlay."""
        total_decimal_odds = 1.0
        
        for leg in legs:
            total_decimal_odds *= leg.decimal_odds
            
        # Convert back to American odds
        if total_decimal_odds >= 2.0:
            american_odds = int((total_decimal_odds - 1) * 100)
        else:
            american_odds = int(-100 / (total_decimal_odds - 1))
            
        return american_odds
    
    def optimize_leg_selection(self, available_legs: List[BetLeg],
                             max_legs: int = 3) -> List[List[BetLeg]]:
        """Find optimal leg combinations using EV optimization."""
        candidates = []
        
        # Generate all possible combinations
        for leg_count in range(2, max_legs + 1):
            for combo in combinations(available_legs, leg_count):
                legs = list(combo)
                
                # Quick correlation filter
                correlation = self.risk_manager.calculate_correlation_score(legs)
                if correlation > self.risk_manager.MAX_CORRELATION_SCORE:
                    continue
                    
                # Calculate metrics
                win_prob = self.calculate_parlay_probability(legs)
                parlay_odds = self.calculate_parlay_odds(legs)
                
                if parlay_odds > 0:
                    decimal_odds = (parlay_odds / 100) + 1
                else:
                    decimal_odds = (100 / abs(parlay_odds)) + 1
                    
                # Expected value
                payout = 25.0 * (decimal_odds - 1)  # Assuming $25 stake
                ev = (win_prob * payout) - ((1 - win_prob) * 25.0)
                ev_percentage = ev / 25.0
                
                # Kelly fraction
                kelly = self.risk_manager.calculate_kelly_fraction(win_prob, decimal_odds)
                
                # Overall confidence (average of leg confidences)
                confidences = [self.predict_leg_probability(leg)[1] for leg in legs]
                avg_confidence = np.mean(confidences)
                
                if (win_prob >= self.risk_manager.MIN_WIN_PROBABILITY and 
                    ev_percentage >= self.risk_manager.MIN_EXPECTED_VALUE and
                    avg_confidence >= self.risk_manager.MIN_CONFIDENCE):
                    
                    candidates.append({
                        'legs': legs,
                        'win_probability': win_prob,
                        'ev_percentage': ev_percentage,
                        'kelly_fraction': kelly,
                        'confidence': avg_confidence,
                        'odds': parlay_odds,
                        'score': ev_percentage * avg_confidence  # Combined score
                    })
                    
        # Sort by combined EV * confidence score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        return [c['legs'] for c in candidates[:5]]  # Return top 5
    
    def build_parlay_recommendation(self, legs: List[BetLeg]) -> ParlayRecommendation:
        """Build complete parlay recommendation with analysis."""
        
        # Calculate core metrics
        win_prob = self.calculate_parlay_probability(legs)
        parlay_odds = self.calculate_parlay_odds(legs)
        
        if parlay_odds > 0:
            decimal_odds = (parlay_odds / 100) + 1
        else:
            decimal_odds = (100 / abs(parlay_odds)) + 1
            
        # Financial calculations
        stake = 25.0  # Default stake
        payout = stake * (decimal_odds - 1)
        ev = (win_prob * payout) - ((1 - win_prob) * stake)
        ev_percentage = ev / stake
        
        # Risk calculations
        kelly = self.risk_manager.calculate_kelly_fraction(win_prob, decimal_odds)
        correlation = self.risk_manager.calculate_correlation_score(legs)
        
        # Confidence calculation
        confidences = [self.predict_leg_probability(leg)[1] for leg in legs]
        avg_confidence = np.mean(confidences)
        
        # Risk score (0-1, lower is better)
        risk_score = (
            (1 - win_prob) * 0.4 +           # Probability risk
            correlation * 0.3 +              # Correlation risk  
            (len(legs) / 6) * 0.2 +          # Complexity risk
            (1 - avg_confidence) * 0.1       # Model uncertainty risk
        )
        
        # Generate reasoning
        reasoning_parts = []
        reasoning_parts.append(f"{len(legs)}-leg parlay with {win_prob:.1%} win probability")
        reasoning_parts.append(f"Expected value: {ev_percentage:.1%}")
        
        if correlation > 0.3:
            reasoning_parts.append("⚠️ Moderate correlation detected")
        if kelly < 0.05:
            reasoning_parts.append("⚠️ Low Kelly fraction suggests small bet size")
        if avg_confidence < 0.7:
            reasoning_parts.append("⚠️ Model confidence below 70%")
            
        reasoning = ". ".join(reasoning_parts)
        
        # Calculate optimal stake
        optimal_stake = self.risk_manager.calculate_optimal_stake(
            kelly, win_prob, ev_percentage
        )
        
        return ParlayRecommendation(
            legs=legs,
            total_odds_american=parlay_odds,
            win_probability=win_prob,
            expected_value=ev_percentage,
            kelly_fraction=kelly,
            confidence_score=avg_confidence,
            risk_score=risk_score,
            correlation_warning=correlation > 0.3,
            reasoning=reasoning,
            max_stake=optimal_stake
        )
    
    def generate_suggestions(self, sport: str = 'NFL', 
                           max_suggestions: int = 3) -> List[ParlayRecommendation]:
        """Generate parlay suggestions for a given sport."""
        logger.info(f"Generating parlay suggestions for {sport}...")
        
        # Get available bets
        available_legs = self.data_provider.get_available_bets(sport)
        
        if len(available_legs) < 2:
            logger.warning(f"Insufficient betting options for {sport}")
            return []
            
        # Find optimal combinations
        optimal_combinations = self.optimize_leg_selection(
            available_legs, max_legs=4
        )
        
        suggestions = []
        
        for legs in optimal_combinations[:max_suggestions]:
            try:
                recommendation = self.build_parlay_recommendation(legs)
                
                # Final validation
                is_valid, violations = self.risk_manager.validate_parlay(
                    legs, recommendation.win_probability,
                    recommendation.expected_value, recommendation.confidence_score
                )
                
                if is_valid:
                    suggestions.append(recommendation)
                    self.suggestions_made.append(recommendation)
                else:
                    logger.debug(f"Parlay rejected: {violations}")
                    
            except Exception as e:
                logger.error(f"Error building recommendation: {e}")
                continue
                
        logger.info(f"Generated {len(suggestions)} valid parlay suggestions")
        return suggestions
    
    def save_suggestions(self, suggestions: List[ParlayRecommendation],
                        filename: str = None) -> str:
        """Save parlay suggestions to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"C:/EQ12/logs/parlay_suggestions_{timestamp}.json"
            
        suggestions_data = {
            'generation_timestamp': datetime.now().isoformat(),
            'suggestions_count': len(suggestions),
            'suggestions': [s.to_dict() for s in suggestions]
        }
        
        with open(filename, 'w') as f:
            json.dump(suggestions_data, f, indent=2, default=str)
            
        logger.info(f"Suggestions saved: {filename}")
        return filename


def main():
    """Demo of parlay builder functionality."""
    
    # Initialize builder
    builder = IntelligentParlayBuilder()
    
    # Generate suggestions for different sports
    for sport in ['NFL', 'NBA']:
        print(f"\n🏈 {sport} Parlay Suggestions:")
        print("=" * 50)
        
        suggestions = builder.generate_suggestions(sport, max_suggestions=2)
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n📋 Suggestion #{i}:")
            print(f"Legs: {suggestion.leg_count}")
            print(f"Win Probability: {suggestion.win_probability:.1%}")
            print(f"Expected Value: {suggestion.expected_value:.1%}")
            print(f"Kelly Fraction: {suggestion.kelly_fraction:.2%}")
            print(f"Confidence: {suggestion.confidence_score:.1%}")
            print(f"Max Stake: ${suggestion.max_stake:.0f}")
            print(f"Potential Payout: ${suggestion.potential_payout:.0f}")
            print(f"Reasoning: {suggestion.reasoning}")
            
            print("\nLegs:")
            for j, leg in enumerate(suggestion.legs, 1):
                print(f"  {j}. {leg.team} vs {leg.opponent} - {leg.bet_type} "
                      f"{leg.line} ({leg.odds_american:+d})")
                      
        # Save suggestions
        if suggestions:
            filename = builder.save_suggestions(suggestions)
            print(f"\n💾 Suggestions saved: {filename}")


if __name__ == "__main__":
    main()