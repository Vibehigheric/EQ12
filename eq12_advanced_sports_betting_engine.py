# eq12_advanced_sports_betting_engine.py
"""
EQ12 Advanced Sports Betting Analysis Engine with ML/AI Integration
Comprehensive upgrade with real-time odds streaming, circuit breakers, and ensemble modeling
"""

import asyncio
import json
import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import httpx
import numpy as np
import redis
import websocket
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from eq12_helpers import (
    env_get,
    setup_utf8_logging,
)

setup_utf8_logging()


@dataclass
class Player:
    name: str
    team: str
    position: str
    stats: dict[str, float]
    injury_status: str = "ACTIVE"
    weather_factor: float = 1.0
    matchup_rating: float = 0.5


@dataclass
class Game:
    home_team: str
    away_team: str
    game_time: datetime
    weather: dict[str, Any] | None = None
    ballpark_factors: dict[str, float] | None = None


@dataclass
class BettingLeg:
    player: str
    market: str
    line: float
    odds: int
    probability: float
    expected_value: float
    kelly_stake: float
    confidence: float
    risk_category: str


@dataclass
class ParlayRecommendation:
    legs: list[BettingLeg]
    total_odds: int
    expected_payout: float
    risk_score: float
    kelly_percentage: float
    confidence_score: float
    edge_percentage: float


class AdvancedOddsEngine:
    """Real-time odds streaming with circuit breaker protection"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.redis_client = None
        self.websocket_url = env_get("SPORTSBOOK_WS_URL", "")
        self.api_key = env_get("ODDS_API_KEY", required=True)
        self.logger = logging.getLogger(__name__)

        # Initialize Redis if available
        try:
            self.redis_client = redis.Redis(
                host=env_get("REDIS_HOST", "localhost"),
                port=int(env_get("REDIS_PORT", "6379")),
                decode_responses=True,
            )
            self.redis_client.ping()
            self.logger.info("Redis connection established")
        except Exception as e:
            self.logger.warning(f"Redis not available: {e}")

    async def get_live_odds(self, sport: str = "baseball_mlb") -> dict[str, Any]:
        """Fetch live odds with caching and circuit breaker protection"""
        cache_key = f"odds:{sport}:{int(time.time() // 60)}"

        # Try Redis cache first
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    self.logger.debug(f"Cache hit for {cache_key}")
                    return json.loads(cached)
            except Exception as e:
                self.logger.warning(f"Redis cache error: {e}")

        # Fetch from API
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
            params = {
                "apiKey": self.api_key,
                "regions": "us",
                "markets": "h2h,spreads,totals,player_props",
                "oddsFormat": "american",
                "dateFormat": "iso",
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Cache for 1 minute
            if self.redis_client:
                try:
                    self.redis_client.setex(cache_key, 60, json.dumps(data))
                except Exception as e:
                    self.logger.warning(f"Redis cache set error: {e}")

            return data

        except Exception as e:
            self.logger.error(f"Failed to fetch odds: {e}")
            # Return cached data if available
            if self.redis_client:
                try:
                    fallback = self.redis_client.get(f"odds:{sport}:fallback")
                    if fallback:
                        return json.loads(fallback)
                except Exception:
                    pass
            raise

    async def stream_odds_updates(self, callback):
        """WebSocket streaming for real-time odds updates"""
        if not self.websocket_url:
            self.logger.warning("No WebSocket URL configured")
            return

        def on_message(ws, message):
            try:
                data = json.loads(message)
                asyncio.create_task(callback(data))
            except Exception as e:
                self.logger.error(f"WebSocket message error: {e}")

        def on_error(ws, error):
            self.logger.error(f"WebSocket error: {error}")

        ws = websocket.WebSocketApp(self.websocket_url, on_message=on_message, on_error=on_error)

        # Run in separate thread
        threading.Thread(target=ws.run_forever, daemon=True).start()


class MLPredictionEngine:
    """Ensemble machine learning models for probability prediction"""

    def __init__(self):
        self.models = {
            "rf": RandomForestClassifier(n_estimators=100, random_state=42),
            "gbm": GradientBoostingClassifier(n_estimators=100, random_state=42),
        }
        self.scaler = StandardScaler()
        self.is_trained = False
        self.logger = logging.getLogger(__name__)

    def prepare_features(self, player: Player, game: Game) -> np.ndarray:
        """Extract ML features from player and game data"""
        features = []

        # Player stats
        stats = player.stats
        features.extend(
            [
                stats.get("batting_avg", 0.250),
                stats.get("home_runs", 0),
                stats.get("rbi", 0),
                stats.get("ops", 0.750),
                stats.get("recent_form", 0.5),
                stats.get("vs_pitcher_type", 0.5),
            ]
        )

        # Weather factors
        if game.weather:
            features.extend(
                [
                    game.weather.get("temperature", 70),
                    game.weather.get("wind_speed", 5),
                    game.weather.get("humidity", 50),
                    1.0 if game.weather.get("wind_direction") == "out" else 0.0,
                ]
            )
        else:
            features.extend([70, 5, 50, 0.0])

        # Ballpark factors
        if game.ballpark_factors:
            features.append(game.ballpark_factors.get("hr_factor", 1.0))
        else:
            features.append(1.0)

        # Injury and matchup
        features.extend(
            [
                0.0 if player.injury_status == "INJURED" else 1.0,
                player.weather_factor,
                player.matchup_rating,
            ]
        )

        return np.array(features).reshape(1, -1)

    def train_models(self, training_data: list[dict]) -> None:
        """Train ensemble models on historical data"""
        if not training_data:
            self.logger.warning("No training data provided")
            return

        X, y = [], []

        for record in training_data:
            player = Player(**record["player"])
            game = Game(**record["game"])
            features = self.prepare_features(player, game).flatten()
            X.append(features)
            y.append(record["outcome"])  # 1 if prop hit, 0 if not

        X = np.array(X)
        y = np.array(y)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train each model
        for name, model in self.models.items():
            model.fit(X_scaled, y)
            self.logger.info(f"Trained {name} model on {len(X)} samples")

        self.is_trained = True

    def predict_probability(self, player: Player, game: Game) -> tuple[float, float]:
        """Predict probability using ensemble models"""
        if not self.is_trained:
            self.logger.warning("Models not trained, using baseline probability")
            return 0.5, 0.1  # probability, confidence

        features = self.prepare_features(player, game)
        features_scaled = self.scaler.transform(features)

        # Get predictions from all models
        predictions = []
        for _name, model in self.models.items():
            prob = model.predict_proba(features_scaled)[0][1]
            predictions.append(prob)

        # Ensemble average
        ensemble_prob = np.mean(predictions)
        confidence = 1.0 - np.std(predictions)  # Lower std = higher confidence

        return float(ensemble_prob), float(confidence)


class KellyCriterionCalculator:
    """Advanced Kelly Criterion with fractional Kelly and risk management"""

    @staticmethod
    def calculate_kelly(
        probability: float, odds: int, bankroll: float, fractional: float = 0.25
    ) -> float:
        """
        Calculate Kelly stake with fractional Kelly for risk management

        Args:
            probability: Model probability (0-1)
            odds: American odds
            bankroll: Total bankroll
            fractional: Fraction of Kelly to bet (default 25% Kelly)
        """
        decimal_odds = odds / 100 + 1 if odds > 0 else 100 / abs(odds) + 1

        # Kelly formula: f = (bp - q) / b
        # where b = decimal_odds - 1, p = probability, q = 1 - probability
        b = decimal_odds - 1
        q = 1 - probability

        kelly_fraction = (b * probability - q) / b

        # Apply fractional Kelly and ensure positive
        stake = max(0, kelly_fraction * fractional * bankroll)

        # Cap at 5% of bankroll for risk management
        return min(stake, bankroll * 0.05)

    @staticmethod
    def calculate_expected_value(probability: float, odds: int) -> float:
        """Calculate expected value percentage"""
        if odds > 0:
            100 / (odds + 100)
            payout_multiplier = odds / 100
        else:
            abs(odds) / (abs(odds) + 100)
            payout_multiplier = 100 / abs(odds)

        expected_return = probability * payout_multiplier - (1 - probability)
        ev_percentage = (expected_return / 1) * 100

        return ev_percentage


class AdvancedSportsAnalyzer:
    """Main analyzer combining all components"""

    def __init__(self):
        self.odds_engine = AdvancedOddsEngine()
        self.ml_engine = MLPredictionEngine()
        self.logger = logging.getLogger(__name__)

        # Load historical data for ML training
        self._load_training_data()

    def _load_training_data(self):
        """Load and prepare historical training data"""
        try:
            # This would load from your historical database
            # For now, using mock data structure
            training_data = self._generate_mock_training_data()
            self.ml_engine.train_models(training_data)
        except Exception as e:
            self.logger.warning(f"Could not load training data: {e}")

    def _generate_mock_training_data(self) -> list[dict]:
        """Generate mock training data for demonstration"""
        np.random.seed(42)
        data = []

        for _ in range(1000):
            # Mock historical records
            player_stats = {
                "batting_avg": np.random.normal(0.250, 0.050),
                "home_runs": np.random.poisson(25),
                "rbi": np.random.poisson(80),
                "ops": np.random.normal(0.750, 0.100),
                "recent_form": np.random.uniform(0.2, 0.8),
                "vs_pitcher_type": np.random.uniform(0.3, 0.7),
            }

            player = {
                "name": "Mock Player",
                "team": "LAD",
                "position": "1B",
                "stats": player_stats,
                "injury_status": "ACTIVE",
                "weather_factor": np.random.uniform(0.8, 1.2),
                "matchup_rating": np.random.uniform(0.3, 0.7),
            }

            game = {
                "home_team": "LAD",
                "away_team": "PHI",
                "game_time": datetime.now(),
                "weather": {
                    "temperature": np.random.normal(75, 10),
                    "wind_speed": np.random.normal(8, 3),
                    "humidity": np.random.normal(60, 15),
                    "wind_direction": "out" if np.random.random() > 0.5 else "in",
                },
                "ballpark_factors": {"hr_factor": np.random.normal(1.0, 0.1)},
            }

            # Simulate outcome based on features
            outcome = 1 if np.random.random() < 0.45 else 0  # ~45% hit rate

            data.append({"player": player, "game": game, "outcome": outcome})

        return data

    async def analyze_player_prop(
        self,
        player: Player,
        game: Game,
        market: str,
        line: float,
        odds: int,
        bankroll: float = 10000,
    ) -> BettingLeg:
        """Analyze a single player prop bet"""

        # Get ML probability prediction
        probability, confidence = self.ml_engine.predict_probability(player, game)

        # Calculate expected value
        expected_value = KellyCriterionCalculator.calculate_expected_value(probability, odds)

        # Calculate Kelly stake
        kelly_stake = KellyCriterionCalculator.calculate_kelly(probability, odds, bankroll)

        # Determine risk category
        if expected_value >= 15:
            risk_category = "HIGH_VALUE"
        elif expected_value >= 8:
            risk_category = "MODERATE_VALUE"
        elif expected_value >= 3:
            risk_category = "LOW_VALUE"
        else:
            risk_category = "NO_VALUE"

        return BettingLeg(
            player=player.name,
            market=market,
            line=line,
            odds=odds,
            probability=probability,
            expected_value=expected_value,
            kelly_stake=kelly_stake,
            confidence=confidence,
            risk_category=risk_category,
        )

    async def build_optimal_parlay(
        self,
        game: Game,
        players: list[Player],
        bankroll: float = 10000,
        min_ev: float = 8.0,
        max_legs: int = 4,
    ) -> ParlayRecommendation | None:
        """Build optimal parlay using ML predictions and Kelly criterion"""

        # Get live odds
        try:
            await self.odds_engine.get_live_odds()
        except Exception as e:
            self.logger.error(f"Could not fetch odds: {e}")
            return None

        # Analyze all potential legs
        potential_legs = []

        for player in players:
            # Mock different prop markets (normally from odds_data)
            markets = [
                ("Home Runs", 0.5, 150),
                ("RBIs", 1.5, 120),
                ("Hits", 1.5, -110),
                ("Total Bases", 1.5, 130),
            ]

            for market, line, odds in markets:
                leg = await self.analyze_player_prop(player, game, market, line, odds, bankroll)
                if leg.expected_value >= min_ev:
                    potential_legs.append(leg)

        if len(potential_legs) < 2:
            self.logger.warning("Not enough positive EV legs found")
            return None

        # Select best combination (simplified greedy approach)
        # In production, use more sophisticated optimization
        potential_legs.sort(key=lambda x: x.expected_value, reverse=True)
        selected_legs = potential_legs[:max_legs]

        # Calculate parlay metrics
        total_probability = 1.0
        total_odds_multiplier = 1.0

        for leg in selected_legs:
            total_probability *= leg.probability
            if leg.odds > 0:
                total_odds_multiplier *= leg.odds / 100 + 1
            else:
                total_odds_multiplier *= 100 / abs(leg.odds) + 1

        # Convert to American odds
        if total_odds_multiplier >= 2:
            parlay_odds = int((total_odds_multiplier - 1) * 100)
        else:
            parlay_odds = int(-100 / (total_odds_multiplier - 1))

        # Risk and confidence scoring
        confidence_score = np.mean([leg.confidence for leg in selected_legs])
        risk_score = 1.0 - total_probability  # Higher probability = lower risk
        edge_percentage = np.mean([leg.expected_value for leg in selected_legs])

        # Kelly percentage for parlay
        kelly_percentage = (
            KellyCriterionCalculator.calculate_kelly(total_probability, parlay_odds, bankroll)
            / bankroll
            * 100
        )

        expected_payout = (bankroll * kelly_percentage / 100) * total_odds_multiplier

        return ParlayRecommendation(
            legs=selected_legs,
            total_odds=parlay_odds,
            expected_payout=expected_payout,
            risk_score=risk_score,
            kelly_percentage=kelly_percentage,
            confidence_score=confidence_score,
            edge_percentage=edge_percentage,
        )


async def main():
    """Demonstration of the advanced sports betting engine"""
    setup_utf8_logging()
    analyzer = AdvancedSportsAnalyzer()

    # Mock game data
    game = Game(
        home_team="LAD",
        away_team="PHI",
        game_time=datetime.now() + timedelta(hours=2),
        weather={
            "temperature": 78,
            "wind_speed": 6,
            "humidity": 45,
            "wind_direction": "out",
        },
        ballpark_factors={"hr_factor": 1.15},
    )

    # Mock players
    players = [
        Player(
            name="Mookie Betts",
            team="LAD",
            position="RF",
            stats={
                "batting_avg": 0.289,
                "home_runs": 28,
                "rbi": 85,
                "ops": 0.892,
                "recent_form": 0.75,
                "vs_pitcher_type": 0.68,
            },
            matchup_rating=0.72,
        ),
        Player(
            name="Bryce Harper",
            team="PHI",
            position="1B",
            stats={
                "batting_avg": 0.293,
                "home_runs": 26,
                "rbi": 82,
                "ops": 0.931,
                "recent_form": 0.68,
                "vs_pitcher_type": 0.71,
            },
            matchup_rating=0.69,
        ),
    ]

    # Build optimal parlay
    parlay = await analyzer.build_optimal_parlay(game, players, bankroll=10000)

    if parlay:
        print("\n🎯 OPTIMAL PARLAY RECOMMENDATION")
        print("=" * 50)
        print(f"Total Odds: {parlay.total_odds:+d}")
        print(f"Kelly Stake: {parlay.kelly_percentage:.1f}% (${parlay.expected_payout:.2f})")
        print(f"Edge: {parlay.edge_percentage:.1f}%")
        print(f"Confidence: {parlay.confidence_score:.1f}")
        print(f"Risk Score: {parlay.risk_score:.2f}")
        print("\nLegs:")
        for i, leg in enumerate(parlay.legs, 1):
            print(f"{i}. {leg.player} {leg.market} @ {leg.odds:+d}")
            print(
                f"   EV: {leg.expected_value:.1f}% | Confidence: {leg.confidence:.2f} | {leg.risk_category}"
            )
    else:
        print("❌ No profitable parlay found with current criteria")


if __name__ == "__main__":
    asyncio.run(main())
