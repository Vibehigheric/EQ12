#!/usr/bin/env python3
"""
EQ12 NBA Coral TPU Model
TensorFlow Lite model optimized for Coral TPU NBA player prediction inference.
Predicts points, rebounds, assists, and prop outcomes for betting analysis.
"""

import tensorflow as tf
import numpy as np
import pandas as pd
import sqlite3
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from pathlib import Path
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

# EQ12 TPU Configuration
TPU_CONFIG = {
    "model_dir": "C:/EQ12/models",
    "data_dir": "C:/EQ12/data", 
    "logs_dir": "C:/EQ12/logs",
    "tpu_delegate": True,
    "quantization": "int8"
}

class EQ12_NBA_TPUModel:
    """NBA Player Performance Prediction Model for Coral TPU"""
    
    def __init__(self, config: Dict = None):
        self.config = config or TPU_CONFIG
        self.setup_logging()
        self.model = None
        self.scaler = None
        self.interpreter = None
        
    def setup_logging(self):
        """Initialize logging for TPU model operations"""
        log_file = f"{self.config['logs_dir']}/nba_tpu_model_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_training_data(self, days_back: int = 90) -> Tuple[np.ndarray, np.ndarray]:
        """Load historical NBA data for model training"""
        
        db_path = f"{self.config['data_dir']}/nba_cluster.db"
        conn = sqlite3.connect(db_path)
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Query historical player performance with features
        query = '''
            SELECT 
                pp.points, pp.rebounds, pp.assists, pp.threes,
                pp.minutes_played, pp.usage_rate, pp.game_pace,
                pp.rest_days,
                -- Opponent features (simplified)
                CASE WHEN pp.team = ng.home_team THEN 1 ELSE 0 END as home_game,
                -- Season context
                julianday(pp.game_date) - julianday('2024-10-01') as season_day
            FROM player_performance pp
            JOIN nba_games ng ON (pp.team = ng.home_team OR pp.team = ng.away_team)
            WHERE pp.game_date >= ? AND pp.points IS NOT NULL
            ORDER BY pp.game_date
        '''
        
        df = pd.read_sql_query(query, conn, params=[cutoff_date.date()])
        conn.close()
        
        if df.empty:
            raise ValueError("No training data available")
            
        self.logger.info(f" Loaded {len(df)} training samples")
        
        # Prepare features (X) and targets (y)
        feature_columns = [
            'minutes_played', 'usage_rate', 'game_pace', 'rest_days',
            'home_game', 'season_day'
        ]
        
        target_columns = ['points', 'rebounds', 'assists', 'threes']
        
        X = df[feature_columns].values.astype(np.float32)
        y = df[target_columns].values.astype(np.float32)
        
        # Handle missing values
        X = np.nan_to_num(X, nan=0.0)
        y = np.nan_to_num(y, nan=0.0)
        
        return X, y
    
    def build_tpu_model(self, input_shape: int, output_shape: int) -> tf.keras.Model:
        """Build neural network optimized for Coral TPU"""
        
        model = tf.keras.Sequential([
            # Input layer
            tf.keras.layers.Input(shape=(input_shape,)),
            
            # Dense layers optimized for TPU quantization
            tf.keras.layers.Dense(64, activation='relu', name='dense_1'),
            tf.keras.layers.Dropout(0.2),
            
            tf.keras.layers.Dense(32, activation='relu', name='dense_2'),
            tf.keras.layers.Dropout(0.2),
            
            tf.keras.layers.Dense(16, activation='relu', name='dense_3'),
            
            # Output layer for multi-target regression
            tf.keras.layers.Dense(output_shape, activation='linear', name='output')
        ])
        
        # Compile with optimizer suitable for TPU
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        self.logger.info(f" Built TPU model: {input_shape}  {output_shape}")
        return model
    
    def train_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Train the NBA prediction model"""
        
        # Normalize features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Build model
        self.model = self.build_tpu_model(X.shape[1], y.shape[1])
        
        # Training callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss', patience=10, restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss', factor=0.5, patience=5
            )
        ]
        
        # Train model
        self.logger.info(" Starting model training...")
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=100,
            batch_size=32,
            callbacks=callbacks,
            verbose=1
        )
        
        # Evaluate model
        test_loss, test_mae = self.model.evaluate(X_test, y_test, verbose=0)
        
        # Calculate per-target metrics
        y_pred = self.model.predict(X_test)
        target_names = ['points', 'rebounds', 'assists', 'threes']
        
        metrics = {
            'overall_loss': test_loss,
            'overall_mae': test_mae
        }
        
        for i, target in enumerate(target_names):
            mae = mean_absolute_error(y_test[:, i], y_pred[:, i])
            rmse = np.sqrt(mean_squared_error(y_test[:, i], y_pred[:, i]))
            metrics[f'{target}_mae'] = mae
            metrics[f'{target}_rmse'] = rmse
        
        self.logger.info(f" Training complete. Test MAE: {test_mae:.3f}")
        return metrics
    
    def convert_to_tflite(self, quantize: bool = True) -> str:
        """Convert trained model to TensorFlow Lite for Coral TPU"""
        
        if self.model is None:
            raise ValueError("No trained model available")
        
        # Create TensorFlow Lite converter
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
        
        if quantize:
            # Enable quantization for TPU optimization
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            
            # Representative dataset for quantization
            def representative_dataset():
                # Use a subset of training data for calibration
                db_path = f"{self.config['data_dir']}/nba_cluster.db"
                conn = sqlite3.connect(db_path)
                
                query = '''
                    SELECT minutes_played, usage_rate, game_pace, rest_days,
                           CASE WHEN team = (SELECT home_team FROM nba_games ng 
                                           WHERE ng.home_team = player_performance.team 
                                           OR ng.away_team = player_performance.team LIMIT 1) 
                                THEN 1 ELSE 0 END as home_game,
                           julianday(game_date) - julianday('2024-10-01') as season_day
                    FROM player_performance 
                    WHERE game_date >= date('now', '-30 days')
                    LIMIT 100
                '''
                
                df = pd.read_sql_query(query, conn)
                conn.close()
                
                if not df.empty:
                    features = df.values.astype(np.float32)
                    features = np.nan_to_num(features, nan=0.0)
                    
                    if self.scaler:
                        features = self.scaler.transform(features)
                    
                    for sample in features:
                        yield [sample.reshape(1, -1)]
            
            converter.representative_dataset = representative_dataset
            converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
            converter.inference_input_type = tf.int8
            converter.inference_output_type = tf.int8
        
        # Convert model
        self.logger.info(" Converting to TensorFlow Lite...")
        tflite_model = converter.convert()
        
        # Save TFLite model
        model_path = f"{self.config['model_dir']}/nba_player_model.tflite"
        Path(self.config['model_dir']).mkdir(exist_ok=True)
        
        with open(model_path, 'wb') as f:
            f.write(tflite_model)
        
        # Save scaler
        scaler_path = f"{self.config['model_dir']}/nba_scaler.joblib"
        if self.scaler:
            joblib.dump(self.scaler, scaler_path)
        
        self.logger.info(f" TFLite model saved: {model_path}")
        return model_path
    
    def load_tflite_model(self, model_path: str = None):
        """Load TensorFlow Lite model for inference"""
        
        if model_path is None:
            model_path = f"{self.config['model_dir']}/nba_player_model.tflite"
        
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Load TFLite interpreter
        if self.config.get('tpu_delegate', False):
            # Try to use Coral TPU delegate (would require Coral runtime)
            try:
                from pycoral.utils import edgetpu
                self.interpreter = tf.lite.Interpreter(
                    model_path=model_path,
                    experimental_delegates=[edgetpu.make_interpreter()]
                )
                self.logger.info(" Loaded model with Coral TPU delegate")
            except ImportError:
                self.logger.warning(" Coral TPU delegate not available, using CPU")
                self.interpreter = tf.lite.Interpreter(model_path=model_path)
        else:
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
        
        self.interpreter.allocate_tensors()
        
        # Load scaler
        scaler_path = f"{self.config['model_dir']}/nba_scaler.joblib"
        if Path(scaler_path).exists():
            self.scaler = joblib.load(scaler_path)
        
        self.logger.info(f" TFLite model loaded: {model_path}")
    
    def predict_player_stats(self, features: np.ndarray) -> Dict[str, float]:
        """Predict player stats using TFLite model"""
        
        if self.interpreter is None:
            raise ValueError("No model loaded for inference")
        
        # Prepare input
        if self.scaler:
            features_scaled = self.scaler.transform(features.reshape(1, -1))
        else:
            features_scaled = features.reshape(1, -1)
        
        features_scaled = features_scaled.astype(np.float32)
        
        # Get input/output details
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()
        
        # Set input tensor
        self.interpreter.set_tensor(input_details[0]['index'], features_scaled)
        
        # Run inference
        self.interpreter.invoke()
        
        # Get output
        predictions = self.interpreter.get_tensor(output_details[0]['index'])
        predictions = predictions[0]  # Remove batch dimension
        
        # Map to readable format
        target_names = ['points', 'rebounds', 'assists', 'threes']
        results = {}
        
        for i, target in enumerate(target_names):
            results[target] = float(predictions[i])
        
        return results
    
    def batch_predict(self, features_batch: np.ndarray) -> List[Dict[str, float]]:
        """Predict stats for batch of players"""
        
        predictions = []
        
        for i in range(features_batch.shape[0]):
            features = features_batch[i]
            pred = self.predict_player_stats(features)
            predictions.append(pred)
        
        return predictions
    
    def evaluate_prop_bet(self, predicted_stats: Dict[str, float], 
                         prop_line: float, prop_type: str) -> Dict[str, float]:
        """Evaluate prop bet based on predictions"""
        
        if prop_type not in predicted_stats:
            return {'probability': 0.5, 'expected_value': 0.0}
        
        predicted_value = predicted_stats[prop_type]
        
        # Simple probability estimation (would be enhanced with confidence intervals)
        # Assuming normal distribution with std = 15% of prediction
        std_dev = predicted_value * 0.15
        z_score = (prop_line - predicted_value) / std_dev if std_dev > 0 else 0
        
        # Probability of OVER
        from scipy.stats import norm
        prob_over = 1 - norm.cdf(z_score)
        
        # Calculate expected value (simplified)
        # Assume -110 odds for both sides
        if prob_over > 0.52:  # Account for juice
            expected_value = (prob_over * 0.91) - ((1 - prob_over) * 1.0)
        else:
            expected_value = ((1 - prob_over) * 0.91) - (prob_over * 1.0)
        
        return {
            'predicted_value': predicted_value,
            'prop_line': prop_line,
            'probability_over': prob_over,
            'probability_under': 1 - prob_over,
            'expected_value': expected_value,
            'recommendation': 'OVER' if prob_over > 0.55 else 'UNDER' if prob_over < 0.45 else 'PASS'
        }
    
    def model_performance_report(self) -> Dict:
        """Generate model performance report"""
        
        # Load test data
        X, y = self.load_training_data(days_back=30)
        
        if self.scaler:
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X
        
        # Batch predictions
        predictions = []
        for i in range(X_scaled.shape[0]):
            pred = self.predict_player_stats(X_scaled[i])
            predictions.append([pred['points'], pred['rebounds'], pred['assists'], pred['threes']])
        
        predictions = np.array(predictions)
        
        # Calculate accuracy metrics
        target_names = ['points', 'rebounds', 'assists', 'threes']
        report = {
            'evaluation_date': datetime.now().isoformat(),
            'sample_size': len(y),
            'metrics': {}
        }
        
        for i, target in enumerate(target_names):
            mae = mean_absolute_error(y[:, i], predictions[:, i])
            rmse = np.sqrt(mean_squared_error(y[:, i], predictions[:, i]))
            
            # Calculate percentage accuracy (within 10% of actual)
            actual_values = y[:, i]
            predicted_values = predictions[:, i]
            pct_accuracy = np.mean(np.abs(predicted_values - actual_values) / actual_values <= 0.1) * 100
            
            report['metrics'][target] = {
                'mae': mae,
                'rmse': rmse,
                'accuracy_10pct': pct_accuracy
            }
        
        return report

def main():
    parser = argparse.ArgumentParser(description="EQ12 NBA Coral TPU Model")
    parser.add_argument('--action', choices=['train', 'convert', 'predict', 'evaluate'], 
                       default='train', help='Action to perform')
    parser.add_argument('--model-path', type=str, help='Path to TFLite model')
    parser.add_argument('--features', type=str, help='Feature file for prediction')
    parser.add_argument('--days-back', type=int, default=90, 
                       help='Days of historical data for training')
    parser.add_argument('--quantize', action='store_true', default=True,
                       help='Enable quantization for TPU')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    model = EQ12_NBA_TPUModel()
    
    try:
        if args.action == 'train':
            # Train new model
            X, y = model.load_training_data(args.days_back)
            metrics = model.train_model(X, y)
            
            print(" Training Results:")
            for metric, value in metrics.items():
                print(f"   {metric}: {value:.3f}")
        
        elif args.action == 'convert':
            # Convert to TFLite
            if model.model is None:
                print(" No trained model available. Train first.")
                return 1
                
            tflite_path = model.convert_to_tflite(args.quantize)
            print(f" TFLite model created: {tflite_path}")
        
        elif args.action == 'predict':
            # Load model and predict
            model.load_tflite_model(args.model_path)
            
            if args.features:
                # Load features from file
                features = np.load(args.features)
                predictions = model.batch_predict(features)
                
                print(f" Predictions for {len(predictions)} players:")
                for i, pred in enumerate(predictions[:5]):  # Show first 5
                    print(f"   Player {i+1}: {pred}")
            else:
                print(" No features file provided")
        
        elif args.action == 'evaluate':
            # Evaluate model performance
            model.load_tflite_model(args.model_path)
            report = model.model_performance_report()
            
            print(" Model Performance Report:")
            print(f"   Sample size: {report['sample_size']}")
            for target, metrics in report['metrics'].items():
                print(f"   {target:10s}: MAE={metrics['mae']:.2f}, "
                      f"RMSE={metrics['rmse']:.2f}, "
                      f"Acc@10%={metrics['accuracy_10pct']:.1f}%")
    
    except Exception as e:
        print(f" Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())