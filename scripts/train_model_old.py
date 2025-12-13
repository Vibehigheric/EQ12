#!/usr/bin/env python3
"""
Advanced Predictive Model Training for EQ12 Betting Optimizer
Supports XGBoost, LightGBM, and ensemble methods
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Any

try:
    import xgboost as xgb
    import lightgbm as lgb
    from sklearn.model_selection import TimeSeriesSplit, cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import log_loss, brier_score_loss, roc_auc_score
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call(["pip", "install", "xgboost", "lightgbm", "scikit-learn"])

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/train_model.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ModelTrainer')

class EQ12ModelTrainer:
    """Advanced model training pipeline for sports betting predictions"""
    
    def __init__(self, config_path: str = ".azureml/dev.json"):
        self.config = self._load_config(config_path)
        self.models = {}
        self.metrics = {}
        
    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load training configuration"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config not found at {path}, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default training configuration"""
        return {
            "test_size": 0.2,
            "cv_folds": 5,
            "random_state": 42,
            "xgboost_params": {
                "n_estimators": 500,
                "max_depth": 8,
                "learning_rate": 0.05,
                "subsample": 0.8,
                "colsample_bytree": 0.8
            },
            "lightgbm_params": {
                "num_leaves": 31,
                "max_depth": 8,
                "learning_rate": 0.05,
                "n_estimators": 500
            }
        }
    
    def load_training_data(self, csv_path: str) -> Tuple[pd.DataFrame, np.ndarray]:
        """Load and prepare training data"""
        logger.info(f"Loading data from {csv_path}")
        df = pd.read_csv(csv_path)
        
        # Separate features and target
        if 'outcome' in df.columns:
            X = df.drop(['outcome', 'match_id'], axis=1, errors='ignore')
            y = df['outcome'].values
        else:
            raise ValueError("'outcome' column not found in data")
        
        logger.info(f"Data shape: {X.shape}, Target distribution: {np.unique(y, return_counts=True)}")
        return X, y
    
    def train_xgboost(self, X: pd.DataFrame, y: np.ndarray) -> xgb.Booster:
        """Train XGBoost model"""
        logger.info("Training XGBoost model...")
        
        params = self.config['xgboost_params'].copy()
        params['objective'] = 'binary:logistic'
        params['eval_metric'] = 'logloss'
        
        dtrain = xgb.DMatrix(X, label=y)
        
        # Train with early stopping
        evals = [(dtrain, 'train')]
        model = xgb.train(
            params,
            dtrain,
            num_boost_round=params.pop('n_estimators'),
            evals=evals,
            early_stopping_rounds=20,
            verbose_eval=50
        )
        
        logger.info("XGBoost training complete")
        return model
    
    def train_lightgbm(self, X: pd.DataFrame, y: np.ndarray) -> lgb.Booster:
        """Train LightGBM model"""
        logger.info("Training LightGBM model...")
        
        params = self.config['lightgbm_params'].copy()
        params['objective'] = 'binary'
        params['metric'] = 'binary_logloss'
        params['verbose'] = -1
        
        train_data = lgb.Dataset(X, label=y)
        model = lgb.train(
            params,
            train_data,
            num_boost_round=params.pop('n_estimators'),
            callbacks=[lgb.early_stopping(20), lgb.log_evaluation(50)]
        )
        
        logger.info("LightGBM training complete")
        return model
    
    def evaluate_model(self, model, X_test: pd.DataFrame, y_test: np.ndarray, 
                      model_type: str = 'xgboost') -> Dict[str, float]:
        """Evaluate model performance"""
        logger.info(f"Evaluating {model_type} model...")
        
        # Get predictions
        if model_type == 'xgboost':
            dtest = xgb.DMatrix(X_test)
            y_pred = model.predict(dtest)
        else:  # lightgbm
            y_pred = model.predict(X_test)
        
        # Clip predictions to [0, 1]
        y_pred = np.clip(y_pred, 0.001, 0.999)
        
        # Calculate metrics
        metrics = {
            'logloss': log_loss(y_test, y_pred),
            'brier_score': brier_score_loss(y_test, y_pred),
            'auc_roc': roc_auc_score(y_test, y_pred),
            'accuracy': np.mean((y_pred > 0.5).astype(int) == y_test),
            'model_type': model_type
        }
        
        logger.info(f"Metrics: {json.dumps(metrics, indent=2)}")
        return metrics
    
    def train_all_models(self, csv_path: str) -> Dict[str, Any]:
        """Train all models and compare"""
        # Load data
        X, y = self.load_training_data(csv_path)
        
        # Train/test split
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config['test_size'], 
            random_state=self.config['random_state']
        )
        
        results = {}
        
        # Train XGBoost
        try:
            xgb_model = self.train_xgboost(X_train, y_train)
            xgb_metrics = self.evaluate_model(xgb_model, X_test, y_test, 'xgboost')
            results['xgboost'] = {
                'model': xgb_model,
                'metrics': xgb_metrics
            }
        except Exception as e:
            logger.error(f"XGBoost training failed: {e}")
        
        # Train LightGBM
        try:
            lgb_model = self.train_lightgbm(X_train, y_train)
            lgb_metrics = self.evaluate_model(lgb_model, X_test, y_test, 'lightgbm')
            results['lightgbm'] = {
                'model': lgb_model,
                'metrics': lgb_metrics
            }
        except Exception as e:
            logger.error(f"LightGBM training failed: {e}")
        
        # Save results
        self._save_training_results(results)
        return results
    
    def _save_training_results(self, results: Dict[str, Any]):
        """Save training results to disk"""
        timestamp = datetime.now().isoformat()
        Path('models').mkdir(exist_ok=True)
        
        for model_name, data in results.items():
            metrics = data['metrics']
            logger.info(f"Saving {model_name} results...")
            
            # Save metrics
            metrics_file = f"models/{model_name}_metrics_{timestamp}.json"
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Train EQ12 predictive models")
    parser.add_argument('--data', type=str, default='data/training_data.csv',
                       help='Path to training data')
    parser.add_argument('--config', type=str, default='.azureml/dev.json',
                       help='Path to config file')
    parser.add_argument('--output', type=str, default='models/eq12_optimizer',
                       help='Output path for trained model')
    
    args = parser.parse_args()
    
    trainer = EQ12ModelTrainer(args.config)
    results = trainer.train_all_models(args.data)
    
    # Print summary
    print("\n" + "="*60)
    print("🎯 MODEL TRAINING SUMMARY")
    print("="*60)
    for model_name, data in results.items():
        metrics = data['metrics']
        print(f"\n📊 {model_name.upper()}")
        print(f"  Logloss:     {metrics['logloss']:.4f}")
        print(f"  Brier Score: {metrics['brier_score']:.4f}")
        print(f"  AUC-ROC:     {metrics['auc_roc']:.4f}")
        print(f"  Accuracy:    {metrics['accuracy']:.4f}")

if __name__ == "__main__":
    main()
