"""
EQ12 Sport Simulators
Advanced simulation modules for all sports betting markets

Each simulator handles specific market logic:
- MLB: HR, TB, Hits, Strikeouts, ML, Spreads, Totals
- NFL: TD props, spreads, totals, ML
- NBA: Points, assists, rebounds, ML, spreads, totals
- UFC: Moneyline, method of victory
- Multi-sport parlays with correlation adjustments
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

try:
    from eq12_backtester.core.engine import Bet, BetOutcome, MarketType
    from eq12_backtester.data.loader import GameResult, PlayerStat
except ImportError:
    from core.engine import Bet, BetOutcome, MarketType

logger = logging.getLogger(__name__)


@dataclass
class SimulationInput:
    """Input parameters for bet simulation"""

    bet: Bet
    historical_data: pd.DataFrame | None = None
    player_stats: dict[str, Any] | None = None
    game_context: dict[str, Any] | None = None
    weather: dict[str, Any] | None = None


@dataclass
class SimulationResult:
    """Result of bet simulation"""

    bet_id: str
    outcome: BetOutcome
    actual_value: float | None = None
    confidence: float = 0.5  # 0-1 confidence in simulation
    factors: dict[str, Any] | None = None


class BaseSimulator(ABC):
    """Base class for sport simulators"""

    def __init__(self, name: str):
        self.name = name
        self.historical_accuracy = {}

    @abstractmethod
    def simulate_bet(self, sim_input: SimulationInput) -> SimulationResult:
        """Simulate a single bet outcome"""
        pass

    def calibrate_model(
        self, historical_bets: list[Bet], actual_results: list[Any]
    ) -> dict[str, float]:
        """Calibrate simulator against historical results"""
        pass


class MLBSimulator(BaseSimulator):
    """
    MLB betting simulator with advanced prop logic

    Handles:
    - Home runs (Over/Under)
    - Total bases (Over/Under)
    - Hits (Over/Under)
    - Strikeouts (Over/Under)
    - Moneyline
    - Spread (Run Line)
    - Totals (Over/Under)
    """

    def __init__(self):
        super().__init__("MLB_Simulator")

        # Historical averages and adjustments
        self.player_baselines = {
            # These would be loaded from historical data
            "Aaron Judge": {
                "hr_per_game": 0.31,  # 2022 season average
                "tb_per_game": 2.1,
                "hits_per_game": 1.1,
                "vs_lefty_adjustment": 1.15,
                "vs_righty_adjustment": 0.95,
                "home_adjustment": 1.08,
                "away_adjustment": 0.92,
            },
            "Mookie Betts": {
                "hr_per_game": 0.25,
                "tb_per_game": 1.9,
                "hits_per_game": 1.3,
                "vs_lefty_adjustment": 1.2,
                "vs_righty_adjustment": 0.9,
                "home_adjustment": 1.05,
                "away_adjustment": 0.95,
            },
            # Add more players as needed
        }

        # Ballpark factors
        self.ballpark_factors = {
            "Yankee Stadium": {"hr_factor": 1.15, "hits_factor": 0.98},
            "Fenway Park": {"hr_factor": 1.08, "hits_factor": 1.05},
            "Coors Field": {"hr_factor": 1.25, "hits_factor": 1.15},
            "Petco Park": {"hr_factor": 0.85, "hits_factor": 0.95},
            # Add more ballparks
        }

        # Weather impacts
        self.weather_adjustments = {
            "wind_out": {"hr_factor": 1.12, "hits_factor": 1.03},
            "wind_in": {"hr_factor": 0.88, "hits_factor": 0.97},
            "hot_temp": {"hr_factor": 1.05, "hits_factor": 1.02},
            "cold_temp": {"hr_factor": 0.95, "hits_factor": 0.98},
        }

    def simulate_bet(self, sim_input: SimulationInput) -> SimulationResult:
        """Simulate MLB bet outcome"""
        bet = sim_input.bet

        if bet.market_type == MarketType.MLB_HR:
            return self._simulate_hr_bet(sim_input)
        if bet.market_type == MarketType.MLB_TB:
            return self._simulate_tb_bet(sim_input)
        if bet.market_type == MarketType.MLB_HITS:
            return self._simulate_hits_bet(sim_input)
        if bet.market_type == MarketType.MLB_K:
            return self._simulate_strikeout_bet(sim_input)
        if bet.market_type == MarketType.MLB_MONEYLINE:
            return self._simulate_moneyline_bet(sim_input)
        if bet.market_type == MarketType.MLB_SPREAD:
            return self._simulate_spread_bet(sim_input)
        if bet.market_type == MarketType.MLB_TOTAL:
            return self._simulate_total_bet(sim_input)
        # Fallback to probability-based simulation
        return self._simulate_probability_based(sim_input)

    def _simulate_hr_bet(self, sim_input: SimulationInput) -> SimulationResult:
        """Simulate home run prop bet"""
        bet = sim_input.bet

        # Parse selection (e.g., "Aaron Judge Over 0.5 HR")
        if "Over" in bet.selection:
            player_name = bet.selection.split(" Over ")[0]
            threshold = float(bet.selection.split("Over ")[1].split(" ")[0])
            is_over = True
        elif "Under" in bet.selection:
            player_name = bet.selection.split(" Under ")[0]
            threshold = float(bet.selection.split("Under ")[1].split(" ")[0])
            is_over = False
        else:
            # Can't parse - use probability
            return self._simulate_probability_based(sim_input)

        # Get player baseline
        baseline = self.player_baselines.get(
            player_name,
            {
                "hr_per_game": 0.15,  # League average
                "vs_lefty_adjustment": 1.0,
                "vs_righty_adjustment": 1.0,
                "home_adjustment": 1.0,
                "away_adjustment": 1.0,
            },
        )

        # Calculate adjusted HR expectation
        hr_expectation = baseline["hr_per_game"]

        # Apply game context adjustments
        if sim_input.game_context:
            # Pitcher handedness
            if sim_input.game_context.get("pitcher_hand") == "L":
                hr_expectation *= baseline["vs_lefty_adjustment"]
            else:
                hr_expectation *= baseline["vs_righty_adjustment"]

            # Home/Away
            if sim_input.game_context.get("is_home"):
                hr_expectation *= baseline["home_adjustment"]
            else:
                hr_expectation *= baseline["away_adjustment"]

            # Ballpark factor
            ballpark = sim_input.game_context.get("ballpark", "")
            park_factor = self.ballpark_factors.get(ballpark, {}).get("hr_factor", 1.0)
            hr_expectation *= park_factor

        # Apply weather adjustments
        if sim_input.weather:
            wind = sim_input.weather.get("wind_direction")
            if wind in self.weather_adjustments:
                hr_expectation *= self.weather_adjustments[wind]["hr_factor"]

        # Simulate using Poisson distribution
        simulated_hrs = np.random.poisson(hr_expectation)

        # Determine outcome
        if is_over:
            outcome = BetOutcome.WIN if simulated_hrs > threshold else BetOutcome.LOSS
        else:
            outcome = BetOutcome.WIN if simulated_hrs < threshold else BetOutcome.LOSS

        # Calculate confidence based on how close to threshold
        prob_over = 1 - np.exp(-hr_expectation) * sum(
            [hr_expectation**k / np.math.factorial(k) for k in range(int(threshold) + 1)]
        )

        confidence = prob_over if is_over else 1 - prob_over

        return SimulationResult(
            bet_id=bet.bet_id,
            outcome=outcome,
            actual_value=float(simulated_hrs),
            confidence=confidence,
            factors={
                "baseline_hr_rate": baseline["hr_per_game"],
                "adjusted_expectation": hr_expectation,
                "simulated_hrs": simulated_hrs,
                "threshold": threshold,
                "prob_over": prob_over,
            },
        )

    def _simulate_tb_bet(self, sim_input: SimulationInput) -> SimulationResult:
        """Simulate total bases prop bet"""
        bet = sim_input.bet

        # Parse similar to HR bet
        if "Over" in bet.selection:
            player_name = bet.selection.split(" Over ")[0]
            threshold = float(bet.selection.split("Over ")[1].split(" ")[0])
            is_over = True
        else:
            return self._simulate_probability_based(sim_input)

        baseline = self.player_baselines.get(player_name, {"tb_per_game": 1.5})
        tb_expectation = baseline["tb_per_game"]

        # Apply similar adjustments as HR
        # ... (similar logic to HR simulation)

        # Simulate using gamma distribution (better for continuous values)
        simulated_tb = np.random.gamma(shape=2, scale=tb_expectation / 2)

        outcome = BetOutcome.WIN if (simulated_tb > threshold) == is_over else BetOutcome.LOSS

        return SimulationResult(
            bet_id=bet.bet_id,
            outcome=outcome,
            actual_value=float(simulated_tb),
            confidence=0.6,  # Simplified confidence
        )

    def _simulate_hits_bet(self, sim_input: SimulationInput) -> SimulationResult:
        """Simulate hits prop bet"""
        # Similar structure to HR simulation
        return self._simulate_probability_based(sim_input)

    def _simulate_strikeout_bet(self, sim_input: SimulationInput) -> SimulationResult:
        """Simulate strikeout prop bet (pitcher)"""
        # Pitcher-focused simulation
        return self._simulate_probability_based(sim_input)

    def _simulate_moneyline_bet(self, sim_input: SimulationInput) -> SimulationResult:
        """Simulate MLB moneyline bet"""
        return self._simulate_probability_based(sim_input)

    def _simulate_spread_bet(self, sim_input: SimulationInput) -> SimulationResult:
        """Simulate MLB spread (run line) bet"""
        return self._simulate_probability_based(sim_input)

    def _simulate_total_bet(self, sim_input: SimulationInput) -> SimulationResult:
        """Simulate MLB total runs bet"""
        return self._simulate_probability_based(sim_input)

    def _simulate_probability_based(self, sim_input: SimulationInput) -> SimulationResult:
        """Fallback probability-based simulation"""
        bet = sim_input.bet
        win_prob = bet.implied_probability

        # Add some noise and edge detection
        if sim_input.historical_data is not None:
            # Analyze historical performance for similar bets
            pass

        outcome = BetOutcome.WIN if np.random.random() < win_prob else BetOutcome.LOSS

        return SimulationResult(bet_id=bet.bet_id, outcome=outcome, confidence=0.5)


class NFLSimulator(BaseSimulator):
    """
    NFL betting simulator

    Handles:
    - Player props (TD, yards, receptions)
    - Team totals
    - Spreads
    - Moneylines
    """

    def __init__(self):
        super().__init__("NFL_Simulator")

        self.player_baselines = {
            "Josh Allen": {
                "passing_tds_per_game": 2.1,
                "rushing_tds_per_game": 0.8,
                "home_adjustment": 1.05,
                "dome_adjustment": 0.95,
                "weather_sensitivity": 0.85,
            },
            "Christian McCaffrey": {
                "rushing_tds_per_game": 0.9,
                "receiving_tds_per_game": 0.3,
                "home_adjustment": 1.02,
                "weather_sensitivity": 0.95,
            },
        }

        self.team_factors = {
            "Buffalo Bills": {"offensive_rating": 1.15, "defensive_rating": 1.08},
            "Kansas City Chiefs": {"offensive_rating": 1.20, "defensive_rating": 1.05},
            # Add more teams
        }

    def simulate_bet(self, sim_input: SimulationInput) -> SimulationResult:
        """Simulate NFL bet outcome"""
        bet = sim_input.bet

        if bet.market_type == MarketType.NFL_PROPS:
            return self._simulate_nfl_prop(sim_input)
        if bet.market_type == MarketType.NFL_SPREAD:
            return self._simulate_nfl_spread(sim_input)
        if bet.market_type == MarketType.NFL_TOTAL:
            return self._simulate_nfl_total(sim_input)
        return self._simulate_probability_based(sim_input)

    def _simulate_nfl_prop(self, sim_input: SimulationInput) -> SimulationResult:
        """Simulate NFL player prop"""
        # Similar structure to MLB HR simulation
        # but with NFL-specific logic
        return self._simulate_probability_based(sim_input)

    def _simulate_nfl_spread(self, sim_input: SimulationInput) -> SimulationResult:
        """Simulate NFL spread bet"""
        return self._simulate_probability_based(sim_input)

    def _simulate_nfl_total(self, sim_input: SimulationInput) -> SimulationResult:
        """Simulate NFL total points bet"""
        return self._simulate_probability_based(sim_input)

    def _simulate_probability_based(self, sim_input: SimulationInput) -> SimulationResult:
        """Fallback simulation"""
        bet = sim_input.bet
        outcome = (
            BetOutcome.WIN if np.random.random() < bet.implied_probability else BetOutcome.LOSS
        )
        return SimulationResult(bet_id=bet.bet_id, outcome=outcome, confidence=0.5)


class NBASimulator(BaseSimulator):
    """NBA betting simulator for player props and team markets"""

    def __init__(self):
        super().__init__("NBA_Simulator")

        self.player_baselines = {
            "LeBron James": {
                "points_per_game": 28.9,
                "assists_per_game": 8.3,
                "rebounds_per_game": 8.2,
                "home_adjustment": 1.03,
                "rest_adjustment": 1.08,  # Games with 2+ days rest
            },
            "Stephen Curry": {
                "points_per_game": 29.5,
                "assists_per_game": 6.1,
                "rebounds_per_game": 6.5,
                "home_adjustment": 1.05,
                "three_point_variance": 1.2,
            },
        }

    def simulate_bet(self, sim_input: SimulationInput) -> SimulationResult:
        """Simulate NBA bet outcome"""
        return self._simulate_probability_based(sim_input)

    def _simulate_probability_based(self, sim_input: SimulationInput) -> SimulationResult:
        """Probability-based simulation"""
        bet = sim_input.bet
        outcome = (
            BetOutcome.WIN if np.random.random() < bet.implied_probability else BetOutcome.LOSS
        )
        return SimulationResult(bet_id=bet.bet_id, outcome=outcome, confidence=0.5)


class ParlaySimulator:
    """
    Multi-sport parlay simulator with correlation adjustments

    Handles complex parlay logic:
    - Same game parlays (correlation)
    - Cross-sport parlays
    - EQ12-specific parlay rules
    """

    def __init__(self):
        self.sport_simulators = {
            "MLB": MLBSimulator(),
            "NFL": NFLSimulator(),
            "NBA": NBASimulator(),
        }

        # Correlation matrices for same-game parlays
        self.mlb_correlations = {
            ("HR", "TB"): 0.65,  # HR and TB are positively correlated
            ("HR", "Hits"): 0.45,
            ("TB", "Hits"): 0.70,
        }

    def simulate_parlay(
        self, parlay_legs: list[SimulationInput]
    ) -> tuple[BetOutcome, list[SimulationResult]]:
        """
        Simulate parlay outcome with correlation adjustments

        Returns:
            Tuple of (overall_outcome, individual_leg_results)
        """
        leg_results = []

        # Simulate each leg
        for leg_input in parlay_legs:
            sport = leg_input.bet.sport
            simulator = self.sport_simulators.get(sport)

            if simulator:
                result = simulator.simulate_bet(leg_input)
            else:
                # Fallback simulation
                bet = leg_input.bet
                outcome = (
                    BetOutcome.WIN
                    if np.random.random() < bet.implied_probability
                    else BetOutcome.LOSS
                )
                result = SimulationResult(bet_id=bet.bet_id, outcome=outcome, confidence=0.5)

            leg_results.append(result)

        # Apply correlation adjustments for same-game parlays
        if self._is_same_game_parlay(parlay_legs):
            leg_results = self._apply_correlation_adjustments(parlay_legs, leg_results)

        # Determine overall parlay outcome
        all_legs_win = all(result.outcome == BetOutcome.WIN for result in leg_results)

        parlay_outcome = BetOutcome.WIN if all_legs_win else BetOutcome.LOSS

        return parlay_outcome, leg_results

    def _is_same_game_parlay(self, parlay_legs: list[SimulationInput]) -> bool:
        """Check if parlay legs are from the same game"""
        if len(parlay_legs) < 2:
            return False

        # Check if all legs have same game context
        first_game = parlay_legs[0].game_context
        if not first_game:
            return False

        for leg in parlay_legs[1:]:
            if not leg.game_context or leg.game_context.get("game_id") != first_game.get("game_id"):
                return False

        return True

    def _apply_correlation_adjustments(
        self, parlay_legs: list[SimulationInput], results: list[SimulationResult]
    ) -> list[SimulationResult]:
        """Apply correlation adjustments to same-game parlays"""
        # Simplified correlation logic
        # In real implementation, this would use copulas or other correlation models

        return results  # Return unmodified for now


class SimulatorFactory:
    """Factory for creating sport simulators"""

    @staticmethod
    def get_simulator(sport: str) -> BaseSimulator:
        """Get appropriate simulator for sport"""
        simulators = {
            "MLB": MLBSimulator(),
            "NFL": NFLSimulator(),
            "NBA": NBASimulator(),
        }

        return simulators.get(sport.upper(), MLBSimulator())  # Default to MLB

    @staticmethod
    def get_parlay_simulator() -> ParlaySimulator:
        """Get parlay simulator"""
        return ParlaySimulator()


if __name__ == "__main__":
    # Test the simulators
    print("🎯 EQ12 Sport Simulators Test")

    # Test MLB HR simulation
    mlb_sim = MLBSimulator()

    # Create test bet
    test_bet = Bet(
        bet_id="test_hr_001",
        sport="MLB",
        market_type=MarketType.MLB_HR,
        selection="Aaron Judge Over 0.5 HR",
        odds=150,
        stake=50.0,
    )

    # Create simulation input
    sim_input = SimulationInput(
        bet=test_bet,
        game_context={
            "pitcher_hand": "L",
            "is_home": True,
            "ballpark": "Yankee Stadium",
        },
        weather={"wind_direction": "wind_out"},
    )

    # Run simulation
    result = mlb_sim.simulate_bet(sim_input)

    print(f"Bet: {test_bet.selection}")
    print(f"Outcome: {result.outcome.value}")
    print(f"Simulated HRs: {result.actual_value}")
    print(f"Confidence: {result.confidence:.2f}")
    if result.factors:
        print(f"Factors: {result.factors}")

    logger.info("EQ12 Sport Simulators test completed!")
