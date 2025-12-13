# eq12_advanced_ai_ml_pipeline.py
"""
EQ12 Advanced AI/ML Pipeline
OpenAI v2.x integration, ensemble model predictions, automated feature engineering
Real-time model training and adaptive betting intelligence
"""

import asyncio
import json
import logging
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import lightgbm as lgb
import numpy as np

# ML/AI Imports
import xgboost as xgb
from sklearn.decomposition import PCA
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
)

# Feature Engineering
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.linear_model import Ridge
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import RobustScaler

from eq12_helpers import (
    build_json_payload,
    call_with_fallbacks,
    create_openai_client,
    setup_utf8_logging,
)

setup_utf8_logging()


@dataclass
class ModelPrediction:
    """Individual model prediction with confidence metrics"""

    model_name: str
    prediction: float
    confidence: float
    feature_importance: dict[str, float]
    timestamp: datetime
    version: str


@dataclass
class EnsemblePrediction:
    """Ensemble prediction combining multiple models"""

    final_prediction: float
    confidence_score: float
    model_predictions: list[ModelPrediction]
    feature_contributions: dict[str, float]
    uncertainty_bounds: tuple[float, float]
    explanation: str
    timestamp: datetime


@dataclass
class TrainingMetrics:
    """Model training and validation metrics"""

    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    rmse: float
    r2_score: float
    cross_val_score: float
    training_time: float
    feature_count: int


class AdvancedFeatureEngineering:
    """Automated feature engineering for sports betting predictions"""

    def __init__(self):
        self.feature_cache = {}
        self.scaler = RobustScaler()
        self.feature_selector = SelectKBest(score_func=f_regression, k=50)
        self.pca = PCA(n_components=0.95)  # Keep 95% of variance

    def engineer_player_features(self, player_data: dict, game_context: dict) -> np.ndarray:
        """Generate comprehensive player features"""

        features = {}

        # Basic stats
        stats = player_data.get("stats", {})
        features.update(
            {
                "batting_avg": stats.get("batting_avg", 0.250),
                "on_base_pct": stats.get("on_base_pct", 0.320),
                "slugging_pct": stats.get("slugging_pct", 0.400),
                "ops": stats.get("ops", 0.720),
                "home_runs": stats.get("home_runs", 0),
                "rbi": stats.get("rbi", 0),
                "hits": stats.get("hits", 0),
                "at_bats": stats.get("at_bats", 100),
                "walks": stats.get("walks", 0),
                "strikeouts": stats.get("strikeouts", 0),
            }
        )

        # Advanced metrics
        features.update(
            {
                "babip": self.calculate_babip(stats),
                "iso_power": features["slugging_pct"] - features["batting_avg"],
                "walk_rate": features["walks"] / max(features["at_bats"], 1),
                "strikeout_rate": features["strikeouts"] / max(features["at_bats"], 1),
                "contact_rate": 1 - features["strikeout_rate"],
            }
        )

        # Situational features
        features.update(self.generate_situational_features(player_data, game_context))

        # Time-based features
        features.update(self.generate_temporal_features(player_data))

        # Streak and momentum features
        features.update(self.generate_momentum_features(player_data))

        # Matchup-specific features
        features.update(self.generate_matchup_features(player_data, game_context))

        # Weather impact features
        features.update(self.generate_weather_features(game_context))

        return np.array(list(features.values()))

    def calculate_babip(self, stats: dict) -> float:
        """Calculate Batting Average on Balls In Play"""
        hits = stats.get("hits", 0)
        home_runs = stats.get("home_runs", 0)
        at_bats = stats.get("at_bats", 1)
        strikeouts = stats.get("strikeouts", 0)

        balls_in_play = at_bats - strikeouts - home_runs
        return (hits - home_runs) / max(balls_in_play, 1)

    def generate_situational_features(self, player_data: dict, game_context: dict) -> dict:
        """Generate situational performance features"""
        return {
            "home_performance": player_data.get("home_ops", 0.750),
            "away_performance": player_data.get("away_ops", 0.700),
            "vs_lefty": player_data.get("vs_left_ops", 0.720),
            "vs_righty": player_data.get("vs_right_ops", 0.730),
            "day_game": player_data.get("day_ops", 0.740),
            "night_game": player_data.get("night_ops", 0.720),
            "divisional_game": 1.0 if game_context.get("divisional", False) else 0.0,
            "playoff_game": 1.0 if game_context.get("playoff", False) else 0.0,
        }

    def generate_temporal_features(self, player_data: dict) -> dict:
        """Generate time-based performance features"""
        return {
            "days_rest": player_data.get("days_rest", 1),
            "games_played": player_data.get("games_played", 50),
            "season_progress": player_data.get("season_progress", 0.5),
            "monthly_trend": player_data.get("monthly_ops_trend", 0.0),
            "weekly_trend": player_data.get("weekly_ops_trend", 0.0),
        }

    def generate_momentum_features(self, player_data: dict) -> dict:
        """Generate momentum and streak features"""
        return {
            "current_streak": player_data.get("hitting_streak", 0),
            "last_5_avg": player_data.get("last_5_avg", 0.250),
            "last_10_ops": player_data.get("last_10_ops", 0.750),
            "last_15_hr": player_data.get("last_15_hr", 0),
            "hot_streak": 1.0 if player_data.get("last_10_avg", 0) > 0.350 else 0.0,
            "cold_streak": 1.0 if player_data.get("last_10_avg", 1) < 0.200 else 0.0,
        }

    def generate_matchup_features(self, player_data: dict, game_context: dict) -> dict:
        """Generate pitcher-batter matchup features"""
        pitcher_data = game_context.get("pitcher", {})

        return {
            "pitcher_era": pitcher_data.get("era", 4.50),
            "pitcher_whip": pitcher_data.get("whip", 1.30),
            "pitcher_k_per_9": pitcher_data.get("k_per_9", 8.0),
            "pitcher_hr_per_9": pitcher_data.get("hr_per_9", 1.2),
            "historical_vs_pitcher": player_data.get("vs_pitcher_ops", 0.750),
            "pitcher_handedness_advantage": self.calculate_handedness_advantage(
                player_data.get("bats"), pitcher_data.get("throws")
            ),
            "pitcher_fatigue": pitcher_data.get("pitch_count", 0) / 100.0,
            "bullpen_quality": game_context.get("bullpen_era", 4.00),
        }

    def calculate_handedness_advantage(self, batter_side: str, pitcher_side: str) -> float:
        """Calculate advantage based on handedness matchup"""
        if not batter_side or not pitcher_side:
            return 0.0

        # Same-handed matchup typically favors pitcher
        if batter_side == pitcher_side:
            return -0.1
        # Opposite-handed matchup typically favors batter
        return 0.1

    def generate_weather_features(self, game_context: dict) -> dict:
        """Generate weather impact features"""
        weather = game_context.get("weather", {})

        return {
            "temperature": weather.get("temperature", 75) / 100.0,
            "wind_speed": weather.get("wind_speed", 8) / 30.0,
            "humidity": weather.get("humidity", 50) / 100.0,
            "wind_direction_out": (1.0 if weather.get("wind_direction") == "out" else 0.0),
            "wind_direction_in": 1.0 if weather.get("wind_direction") == "in" else 0.0,
            "precipitation": 1.0 if weather.get("precipitation", False) else 0.0,
            "dome_game": 1.0 if game_context.get("dome", False) else 0.0,
        }

    def select_features(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Select most important features"""
        return self.feature_selector.fit_transform(X, y)

    def scale_features(self, X: np.ndarray, fit: bool = False) -> np.ndarray:
        """Scale features for model training"""
        if fit:
            return self.scaler.fit_transform(X)
        return self.scaler.transform(X)


class EnsembleModelManager:
    """Manages ensemble of ML models for betting predictions"""

    def __init__(self):
        self.models = {}
        self.model_weights = {}
        self.model_performance = {}
        self.feature_engineering = AdvancedFeatureEngineering()
        self.openai_client = create_openai_client()

        # Initialize models
        self.initialize_models()

    def initialize_models(self):
        """Initialize ensemble of ML models"""

        # Tree-based models
        self.models["random_forest"] = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )

        self.models["gradient_boosting"] = GradientBoostingRegressor(
            n_estimators=150, learning_rate=0.1, max_depth=10, random_state=42
        )

        self.models["xgboost"] = xgb.XGBRegressor(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=8,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
        )

        self.models["lightgbm"] = lgb.LGBMRegressor(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=10,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            verbose=-1,
        )

        # Linear models
        self.models["ridge"] = Ridge(alpha=1.0)

        # Initialize equal weights
        self.model_weights = dict.fromkeys(self.models.keys(), 1.0)

    async def train_ensemble(self, training_data: list[dict]) -> dict[str, TrainingMetrics]:
        """Train all models in the ensemble"""

        if not training_data:
            raise ValueError("No training data provided")

        # Prepare features and targets
        X, y = self.prepare_training_data(training_data)

        if len(X) == 0:
            raise ValueError("No valid training samples")

        metrics = {}

        for model_name, model in self.models.items():
            logging.info(f"Training {model_name}...")

            start_time = time.time()

            try:
                # Train model
                model.fit(X, y)

                # Calculate metrics
                y_pred = model.predict(X)

                # Cross-validation score
                cv_scores = cross_val_score(
                    model,
                    X,
                    y,
                    cv=TimeSeriesSplit(n_splits=5),
                    scoring="neg_mean_squared_error",
                )

                training_time = time.time() - start_time

                metrics[model_name] = TrainingMetrics(
                    model_name=model_name,
                    accuracy=r2_score(y, y_pred),
                    precision=0.0,  # Will calculate for classification tasks
                    recall=0.0,  # Will calculate for classification tasks
                    f1_score=0.0,  # Will calculate for classification tasks
                    rmse=np.sqrt(mean_squared_error(y, y_pred)),
                    r2_score=r2_score(y, y_pred),
                    cross_val_score=np.mean(-cv_scores),
                    training_time=training_time,
                    feature_count=X.shape[1],
                )

                # Update model performance tracking
                self.model_performance[model_name] = metrics[model_name]

                logging.info(f"{model_name} trained - R²: {metrics[model_name].r2_score:.3f}")

            except Exception as e:
                logging.error(f"Failed to train {model_name}: {e}")
                continue

        # Update model weights based on performance
        self.update_model_weights()

        return metrics

    def prepare_training_data(self, training_data: list[dict]) -> tuple[np.ndarray, np.ndarray]:
        """Prepare training data for model fitting"""

        X_list = []
        y_list = []

        for record in training_data:
            try:
                # Extract features
                features = self.feature_engineering.engineer_player_features(
                    record["player_data"], record["game_context"]
                )

                # Extract target
                target = record["outcome"]  # 1 if prop hit, 0 if not

                X_list.append(features)
                y_list.append(target)

            except Exception as e:
                logging.warning(f"Skipping invalid training record: {e}")
                continue

        if not X_list:
            return np.array([]), np.array([])

        X = np.array(X_list)
        y = np.array(y_list)

        # Feature selection and scaling
        X = self.feature_engineering.select_features(X, y)
        X = self.feature_engineering.scale_features(X, fit=True)

        return X, y

    def update_model_weights(self):
        """Update ensemble weights based on recent performance"""

        if not self.model_performance:
            return

        # Weight based on R² score and inverse of RMSE
        total_weight = 0
        for name, metrics in self.model_performance.items():
            weight = metrics.r2_score / (1 + metrics.rmse)
            self.model_weights[name] = max(0.1, weight)  # Minimum weight of 0.1
            total_weight += self.model_weights[name]

        # Normalize weights
        for name in self.model_weights:
            self.model_weights[name] /= total_weight

        logging.info(f"Updated model weights: {self.model_weights}")

    async def predict_ensemble(self, player_data: dict, game_context: dict) -> EnsemblePrediction:
        """Generate ensemble prediction for a player/game scenario"""

        # Engineer features
        features = self.feature_engineering.engineer_player_features(player_data, game_context)
        features = features.reshape(1, -1)

        # Scale features
        features_scaled = self.feature_engineering.scale_features(features)

        # Get predictions from all models
        model_predictions = []

        for model_name, model in self.models.items():
            try:
                prediction = model.predict(features_scaled)[0]

                # Calculate confidence (simplified - could use prediction intervals)
                confidence = min(
                    0.95,
                    self.model_performance.get(
                        model_name,
                        TrainingMetrics(
                            model_name=model_name,
                            accuracy=0.5,
                            precision=0,
                            recall=0,
                            f1_score=0,
                            rmse=1.0,
                            r2_score=0.5,
                            cross_val_score=0.5,
                            training_time=0,
                            feature_count=0,
                        ),
                    ).r2_score,
                )

                # Feature importance (for tree-based models)
                feature_importance = {}
                if hasattr(model, "feature_importances_"):
                    feature_importance = {
                        f"feature_{i}": importance
                        for i, importance in enumerate(model.feature_importances_)
                    }

                model_predictions.append(
                    ModelPrediction(
                        model_name=model_name,
                        prediction=prediction,
                        confidence=confidence,
                        feature_importance=feature_importance,
                        timestamp=datetime.now(),
                        version="1.0",
                    )
                )

            except Exception as e:
                logging.warning(f"Model {model_name} prediction failed: {e}")
                continue

        if not model_predictions:
            raise ValueError("No models available for prediction")

        # Calculate weighted ensemble prediction
        weighted_sum = sum(
            pred.prediction * self.model_weights.get(pred.model_name, 0.2)
            for pred in model_predictions
        )

        weight_sum = sum(self.model_weights.get(pred.model_name, 0.2) for pred in model_predictions)

        final_prediction = weighted_sum / weight_sum

        # Calculate ensemble confidence
        confidence_score = np.mean([pred.confidence for pred in model_predictions])

        # Calculate prediction uncertainty bounds
        predictions = [pred.prediction for pred in model_predictions]
        std_dev = np.std(predictions)
        uncertainty_bounds = (
            final_prediction - 1.96 * std_dev,
            final_prediction + 1.96 * std_dev,
        )

        # Generate AI explanation
        explanation = await self.generate_ai_explanation(
            player_data, game_context, model_predictions, final_prediction
        )

        return EnsemblePrediction(
            final_prediction=final_prediction,
            confidence_score=confidence_score,
            model_predictions=model_predictions,
            feature_contributions=self.calculate_feature_contributions(model_predictions),
            uncertainty_bounds=uncertainty_bounds,
            explanation=explanation,
            timestamp=datetime.now(),
        )

    def calculate_feature_contributions(
        self, model_predictions: list[ModelPrediction]
    ) -> dict[str, float]:
        """Calculate aggregated feature contributions"""

        feature_contributions = {}

        for pred in model_predictions:
            weight = self.model_weights.get(pred.model_name, 0.2)

            for feature, importance in pred.feature_importance.items():
                if feature not in feature_contributions:
                    feature_contributions[feature] = 0
                feature_contributions[feature] += importance * weight

        return feature_contributions

    async def generate_ai_explanation(
        self,
        player_data: dict,
        game_context: dict,
        model_predictions: list[ModelPrediction],
        final_prediction: float,
    ) -> str:
        """Generate AI-powered explanation of the prediction"""

        try:
            # Prepare context for OpenAI
            context = {
                "player": player_data.get("name", "Unknown Player"),
                "market": game_context.get("market", "Unknown Market"),
                "prediction": final_prediction,
                "confidence": np.mean([p.confidence for p in model_predictions]),
                "key_factors": self.identify_key_factors(player_data, game_context),
                "model_agreement": self.calculate_model_agreement(model_predictions),
            }

            messages = [
                {
                    "role": "system",
                    "content": """You are an expert sports betting analyst. Explain predictions in a clear,
                    concise manner focusing on key factors and reasoning. Keep explanations under 100 words.""",
                },
                {
                    "role": "user",
                    "content": f"""
                    Analyze this betting prediction:

                    Player: {context["player"]}
                    Market: {context["market"]}
                    Prediction: {context["prediction"]:.3f}
                    Confidence: {context["confidence"]:.1%}

                    Key Factors: {context["key_factors"]}
                    Model Agreement: {context["model_agreement"]:.1%}

                    Provide a brief explanation of why this prediction makes sense.
                    """,
                },
            ]

            response = await call_with_fallbacks(
                lambda: self.openai_client,
                lambda model: build_json_payload(model, messages, max_tokens=150),
                "prediction_explanation",
            )

            content = response.choices[0].message.content

            # Parse JSON response
            try:
                result = json.loads(content)
                return result.get("explanation", content)
            except json.JSONDecodeError:
                return content

        except Exception as e:
            logging.warning(f"AI explanation generation failed: {e}")
            return (
                f"Prediction: {final_prediction:.1%} probability based on ensemble model analysis."
            )

    def identify_key_factors(self, player_data: dict, game_context: dict) -> str:
        """Identify key factors influencing the prediction"""

        factors = []

        # Player form
        recent_avg = player_data.get("stats", {}).get("last_10_avg", 0)
        if recent_avg > 0.350:
            factors.append("hot batting streak")
        elif recent_avg < 0.200:
            factors.append("cold batting streak")

        # Weather
        weather = game_context.get("weather", {})
        if weather.get("wind_direction") == "out" and weather.get("wind_speed", 0) > 10:
            factors.append("favorable wind conditions")

        # Matchup
        if player_data.get("vs_pitcher_ops", 0.750) > 0.900:
            factors.append("strong historical matchup vs pitcher")

        return ", ".join(factors) if factors else "standard statistical indicators"

    def calculate_model_agreement(self, model_predictions: list[ModelPrediction]) -> float:
        """Calculate how much models agree on the prediction"""

        if len(model_predictions) < 2:
            return 1.0

        predictions = [p.prediction for p in model_predictions]
        std_dev = np.std(predictions)
        mean_pred = np.mean(predictions)

        # Agreement is inverse of coefficient of variation
        cv = std_dev / (mean_pred + 0.001)  # Avoid division by zero
        agreement = 1.0 / (1.0 + cv)

        return min(1.0, agreement)


class AdaptiveLearningSystem:
    """Continuously adapt and improve models based on new data"""

    def __init__(self, model_manager: EnsembleModelManager):
        self.model_manager = model_manager
        self.performance_history = []
        self.adaptation_threshold = 0.1  # Retrain if performance drops by 10%

    async def monitor_performance(
        self, predictions: list[EnsemblePrediction], actual_outcomes: list[float]
    ) -> dict[str, Any]:
        """Monitor model performance and trigger retraining if needed"""

        if len(predictions) != len(actual_outcomes):
            raise ValueError("Prediction and outcome counts must match")

        # Calculate current performance metrics
        pred_values = [p.final_prediction for p in predictions]

        accuracy = accuracy_score(
            [1 if x > 0.5 else 0 for x in actual_outcomes],
            [1 if x > 0.5 else 0 for x in pred_values],
        )

        rmse = np.sqrt(mean_squared_error(actual_outcomes, pred_values))

        performance_metrics = {
            "timestamp": datetime.now(),
            "accuracy": accuracy,
            "rmse": rmse,
            "sample_count": len(predictions),
            "mean_confidence": np.mean([p.confidence_score for p in predictions]),
        }

        self.performance_history.append(performance_metrics)

        # Check if retraining is needed
        if self.should_retrain():
            logging.info("Performance degradation detected - triggering model retraining")
            await self.trigger_adaptive_retraining()

        return performance_metrics

    def should_retrain(self) -> bool:
        """Determine if models should be retrained"""

        if len(self.performance_history) < 10:
            return False

        # Compare recent performance to historical baseline
        recent_accuracy = np.mean([p["accuracy"] for p in self.performance_history[-5:]])
        baseline_accuracy = np.mean([p["accuracy"] for p in self.performance_history[-20:-5]])

        performance_drop = baseline_accuracy - recent_accuracy

        return performance_drop > self.adaptation_threshold

    async def trigger_adaptive_retraining(self):
        """Trigger adaptive retraining with latest data"""

        # This would fetch latest training data and retrain models
        # Implementation depends on data storage and pipeline setup
        logging.info("Adaptive retraining triggered")

        # Placeholder for retraining logic
        # In production, this would:
        # 1. Fetch recent historical data
        # 2. Prepare training dataset
        # 3. Retrain models with new data
        # 4. Validate performance improvements
        # 5. Deploy updated models

        pass


class AIMLPipelineOrchestrator:
    """Main orchestrator for the AI/ML pipeline"""

    def __init__(self):
        self.model_manager = EnsembleModelManager()
        self.adaptive_system = AdaptiveLearningSystem(self.model_manager)
        self.feature_store_path = Path("C:/EQ12/data/feature_store.db")
        self.model_store_path = Path("C:/EQ12/models")

        # Ensure directories exist
        self.model_store_path.mkdir(exist_ok=True, parents=True)

        # Initialize feature store
        self.init_feature_store()

    def init_feature_store(self):
        """Initialize SQLite feature store"""

        conn = sqlite3.connect(self.feature_store_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                player_name TEXT,
                market TEXT,
                prediction REAL,
                confidence REAL,
                actual_outcome REAL,
                features TEXT,
                model_versions TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                model_name TEXT,
                accuracy REAL,
                rmse REAL,
                r2_score REAL,
                training_samples INTEGER
            )
        """
        )

        conn.commit()
        conn.close()

    async def generate_prediction(
        self, player_data: dict, game_context: dict
    ) -> EnsemblePrediction:
        """Generate a comprehensive prediction using the full AI/ML pipeline"""

        # Generate ensemble prediction
        prediction = await self.model_manager.predict_ensemble(player_data, game_context)

        # Store prediction in feature store
        self.store_prediction(prediction, player_data, game_context)

        return prediction

    def store_prediction(
        self, prediction: EnsemblePrediction, player_data: dict, game_context: dict
    ):
        """Store prediction in feature store for future learning"""

        conn = sqlite3.connect(self.feature_store_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO predictions
            (timestamp, player_name, market, prediction, confidence, features, model_versions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                prediction.timestamp.isoformat(),
                player_data.get("name", "Unknown"),
                game_context.get("market", "Unknown"),
                prediction.final_prediction,
                prediction.confidence_score,
                json.dumps(prediction.feature_contributions),
                json.dumps([p.model_name for p in prediction.model_predictions]),
            ),
        )

        conn.commit()
        conn.close()

    async def batch_train_models(self, training_data_path: str) -> dict[str, TrainingMetrics]:
        """Train models on historical data"""

        # Load training data
        training_data = self.load_training_data(training_data_path)

        # Train ensemble
        metrics = await self.model_manager.train_ensemble(training_data)

        # Save trained models
        self.save_models()

        # Store performance metrics
        self.store_training_metrics(metrics)

        return metrics

    def load_training_data(self, data_path: str) -> list[dict]:
        """Load training data from various sources"""

        # This would load from your historical database
        # For now, return mock data
        return self.generate_mock_training_data(1000)

    def generate_mock_training_data(self, count: int) -> list[dict]:
        """Generate mock training data for testing"""

        np.random.seed(42)
        data = []

        for _ in range(count):
            player_data = {
                "name": f"Player_{np.random.randint(1, 100)}",
                "stats": {
                    "batting_avg": np.random.normal(0.250, 0.050),
                    "home_runs": np.random.poisson(20),
                    "rbi": np.random.poisson(60),
                    "ops": np.random.normal(0.750, 0.100),
                    "last_10_avg": np.random.normal(0.260, 0.080),
                },
            }

            game_context = {
                "market": "Home Runs",
                "weather": {
                    "temperature": np.random.normal(75, 10),
                    "wind_speed": np.random.normal(8, 4),
                    "wind_direction": np.random.choice(["in", "out"]),
                },
                "pitcher": {
                    "era": np.random.normal(4.20, 1.00),
                    "whip": np.random.normal(1.30, 0.20),
                },
            }

            # Simulate outcome based on player strength
            base_prob = 0.15 + (player_data["stats"]["ops"] - 0.600) * 0.3
            base_prob = max(0.05, min(0.80, base_prob))

            outcome = 1 if np.random.random() < base_prob else 0

            data.append(
                {
                    "player_data": player_data,
                    "game_context": game_context,
                    "outcome": outcome,
                }
            )

        return data

    def save_models(self):
        """Save trained models to disk"""

        for name, model in self.model_manager.models.items():
            model_path = self.model_store_path / f"{name}_model.joblib"
            joblib.dump(model, model_path)

        # Save feature engineering components
        joblib.dump(
            self.model_manager.feature_engineering.scaler,
            self.model_store_path / "scaler.joblib",
        )
        joblib.dump(
            self.model_manager.feature_engineering.feature_selector,
            self.model_store_path / "feature_selector.joblib",
        )

        # Save model weights
        with open(self.model_store_path / "model_weights.json", "w") as f:
            json.dump(self.model_manager.model_weights, f)

    def load_models(self):
        """Load trained models from disk"""

        for name in self.model_manager.models:
            model_path = self.model_store_path / f"{name}_model.joblib"
            if model_path.exists():
                self.model_manager.models[name] = joblib.load(model_path)

        # Load feature engineering components
        scaler_path = self.model_store_path / "scaler.joblib"
        if scaler_path.exists():
            self.model_manager.feature_engineering.scaler = joblib.load(scaler_path)

        selector_path = self.model_store_path / "feature_selector.joblib"
        if selector_path.exists():
            self.model_manager.feature_engineering.feature_selector = joblib.load(selector_path)

        # Load model weights
        weights_path = self.model_store_path / "model_weights.json"
        if weights_path.exists():
            with open(weights_path) as f:
                self.model_manager.model_weights = json.load(f)

    def store_training_metrics(self, metrics: dict[str, TrainingMetrics]):
        """Store training metrics in database"""

        conn = sqlite3.connect(self.feature_store_path)
        cursor = conn.cursor()

        for model_name, metric in metrics.items():
            cursor.execute(
                """
                INSERT INTO model_performance
                (timestamp, model_name, accuracy, rmse, r2_score, training_samples)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    datetime.now().isoformat(),
                    model_name,
                    metric.accuracy,
                    metric.rmse,
                    metric.r2_score,
                    0,  # Training samples would be passed separately
                ),
            )

        conn.commit()
        conn.close()


async def main():
    """Demonstrate the advanced AI/ML pipeline"""

    setup_utf8_logging()
    logging.info("🤖 Starting EQ12 Advanced AI/ML Pipeline")

    # Initialize pipeline
    pipeline = AIMLPipelineOrchestrator()

    # Train models on mock data
    logging.info("Training ensemble models...")
    training_metrics = await pipeline.batch_train_models("mock_data")

    # Display training results
    print("\n🎯 MODEL TRAINING RESULTS")
    print("=" * 50)
    for model_name, metrics in training_metrics.items():
        print(f"{model_name}:")
        print(f"  R² Score: {metrics.r2_score:.3f}")
        print(f"  RMSE: {metrics.rmse:.3f}")
        print(f"  Training Time: {metrics.training_time:.1f}s")
        print(f"  Features: {metrics.feature_count}")

    # Generate sample prediction
    print("\n🔮 SAMPLE PREDICTION")
    print("=" * 50)

    sample_player = {
        "name": "Mike Trout",
        "stats": {
            "batting_avg": 0.283,
            "home_runs": 35,
            "rbi": 95,
            "ops": 0.987,
            "last_10_avg": 0.350,
        },
    }

    sample_game = {
        "market": "Home Runs",
        "weather": {"temperature": 78, "wind_speed": 12, "wind_direction": "out"},
        "pitcher": {"era": 4.85, "whip": 1.45},
    }

    prediction = await pipeline.generate_prediction(sample_player, sample_game)

    print(f"Player: {sample_player['name']}")
    print(f"Market: {sample_game['market']}")
    print(f"Prediction: {prediction.final_prediction:.1%}")
    print(f"Confidence: {prediction.confidence_score:.1%}")
    print(
        f"Uncertainty: [{prediction.uncertainty_bounds[0]:.1%}, {prediction.uncertainty_bounds[1]:.1%}]"
    )
    print(f"Explanation: {prediction.explanation}")

    print("\n✅ AI/ML Pipeline demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main())
