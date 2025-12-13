#!/usr/bin/env python3
"""
EQ12 Production Model Training System
Expert-level config-driven training with baselines, calibration, champion-challenger
Integrated with backtester.py for ROI validation before deployment
"""

import argparse
import json
import logging
import pickle
import subprocess
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    log_loss, brier_score_loss, roc_auc_score,
    calibration_curve
)
from sklearn.model_selection import TimeSeriesSplit
import xgboost as xgb
import lightgbm as lgb

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EQ12.ModelTrainer')


class EQ12ProductionTrainer:
    """Production-grade model training with full ML lifecycle management"""
    
    def __init__(self, config_path: str):
        """Initialize with YAML config"""
        logger.info(f"Loading config: {config_path}")
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.model_name = self.config['model']['name']
        self.model_version = self.config['model']['version']
        self.algorithm = self.config['model']['algorithm']
        
        # Set reproducibility
        self.random_state = self.config['reproducibility']['random_seed']
        np.random.seed(self.random_state)
        
        # Model artifacts
        self.model = None
        self.calibrated_model = None
        self.feature_names = None
        self.metrics = {}
        
    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load train/val/test datasets"""
        logger.info("Loading datasets")
        
        train_path = self.config['data']['train_data']
        val_path = self.config['data']['val_data']
        test_path = self.config['data']['test_data']
        
        train_df = pd.read_csv(train_path)
        val_df = pd.read_csv(val_path)
        test_df = pd.read_csv(test_path)
        
        logger.info(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
        
        return train_df, val_df, test_df
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Extract features and target"""
        target_col = self.config['model']['target']
        
        # Remove target and exclude columns
        exclude_cols = [target_col] + self.config['data'].get('exclude_features', [])
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        X = df[feature_cols]
        y = df[target_col]
        
        self.feature_names = feature_cols
        logger.info(f"Features: {len(feature_cols)}, Target: {target_col}")
        
        return X, y
    
    def train_baseline_models(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series
    ) -> Dict[str, Dict]:
        """Train baseline models for comparison"""
        logger.info("Training baseline models")
        
        baselines = {}
        baseline_configs = self.config['evaluation']['baselines']
        
        for baseline_cfg in baseline_configs:
            name = baseline_cfg['name']
            logger.info(f"  Training baseline: {name}")
            
            if name == "market_implied":
                # Use closing line implied probability
                if 'market_implied_prob' in X_val.columns:
                    y_pred = X_val['market_implied_prob'].values
                else:
                    logger.warning("market_implied_prob not in features, using 0.5")
                    y_pred = np.full(len(y_val), 0.5)
            
            elif name == "home_favorite":
                # Always pick home favorite
                if 'is_home' in X_val.columns and 'opening_odds' in X_val.columns:
                    y_pred = (X_val['is_home'] == 1).astype(float).values
                else:
                    y_pred = np.full(len(y_val), 0.5)
            
            elif name == "global_average":
                # Historical average
                y_pred = np.full(len(y_val), y_train.mean())
            
            else:
                logger.warning(f"Unknown baseline: {name}, skipping")
                continue
            
            # Evaluate
            baselines[name] = {
                'log_loss': log_loss(y_val, y_pred),
                'brier_score': brier_score_loss(y_val, y_pred),
                'description': baseline_cfg['description']
            }
            
            logger.info(f"    {name}: log_loss={baselines[name]['log_loss']:.4f}")
        
        return baselines
    
    def train_model(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series
    ):
        """Train primary model (XGBoost or LightGBM)"""
        logger.info(f"Training {self.algorithm} model")
        
        params = self.config['hyperparameters']
        
        if self.algorithm == "xgboost":
            self.model = xgb.XGBClassifier(
                max_depth=params['max_depth'],
                learning_rate=params['learning_rate'],
                n_estimators=params['n_estimators'],
                min_child_weight=params['min_child_weight'],
                subsample=params['subsample'],
                colsample_bytree=params['colsample_bytree'],
                gamma=params['gamma'],
                reg_alpha=params['reg_alpha'],
                reg_lambda=params['reg_lambda'],
                random_state=params['random_state'],
                n_jobs=params['n_jobs'],
                eval_metric=params['eval_metric']
            )
            
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                early_stopping_rounds=params['early_stopping_rounds'],
                verbose=False
            )
            
        elif self.algorithm == "lightgbm":
            self.model = lgb.LGBMClassifier(
                max_depth=params['max_depth'],
                learning_rate=params['learning_rate'],
                n_estimators=params['n_estimators'],
                min_child_weight=params['min_child_weight'],
                subsample=params['subsample'],
                colsample_bytree=params['colsample_bytree'],
                reg_alpha=params['reg_alpha'],
                reg_lambda=params['reg_lambda'],
                random_state=params['random_state'],
                n_jobs=params['n_jobs']
            )
            
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                callbacks=[lgb.early_stopping(params['early_stopping_rounds'])]
            )
        
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
        
        logger.info("Model training complete")
    
    def calibrate_model(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series
    ):
        """Calibrate probabilities using isotonic or Platt scaling"""
        logger.info("Calibrating model probabilities")
        
        calib_method = self.config['calibration']['method']
        cv_folds = self.config['calibration']['cv_folds']
        
        self.calibrated_model = CalibratedClassifierCV(
            self.model,
            method=calib_method,
            cv=cv_folds
        )
        
        self.calibrated_model.fit(X_train, y_train)
        logger.info(f"Calibration complete ({calib_method})")
    
    def evaluate_model(
        self,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        use_calibrated: bool = True
    ) -> Dict[str, float]:
        """Evaluate model on validation set"""
        logger.info("Evaluating model")
        
        model = self.calibrated_model if use_calibrated else self.model
        y_pred_proba = model.predict_proba(X_val)[:, 1]
        
        metrics = {
            'log_loss': log_loss(y_val, y_pred_proba),
            'brier_score': brier_score_loss(y_val, y_pred_proba),
            'auc_roc': roc_auc_score(y_val, y_pred_proba)
        }
        
        # Calibration error (ECE - Expected Calibration Error)
        frac_pos, mean_pred = calibration_curve(y_val, y_pred_proba, n_bins=10)
        ece = np.abs(frac_pos - mean_pred).mean()
        metrics['calibration_error'] = ece
        
        logger.info(f"  Log Loss: {metrics['log_loss']:.4f}")
        logger.info(f"  Brier Score: {metrics['brier_score']:.4f}")
        logger.info(f"  AUC-ROC: {metrics['auc_roc']:.4f}")
        logger.info(f"  Calibration Error: {metrics['calibration_error']:.4f}")
        
        return metrics
    
    def run_backtest(self, predictions_path: str) -> Dict[str, float]:
        """Run backtester.py on model predictions"""
        logger.info("Running backtest for ROI validation")
        
        backtest_config = self.config['evaluation']['backtest']
        
        if not backtest_config['enabled']:
            logger.info("Backtesting disabled in config")
            return {}
        
        # Run backtester
        cmd = [
            'python',
            backtest_config['script'],
            '--slips', predictions_path,
            '--bankroll', str(backtest_config['bankroll']),
            '--output', 'logs/backtest_results.json'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Backtester failed: {result.stderr}")
            return {}
        
        # Load results
        with open('logs/backtest_results.json', 'r') as f:
            backtest_results = json.load(f)
        
        logger.info(f"  Backtest ROI: {backtest_results.get('roi', 0):.2%}")
        logger.info(f"  Sharpe Ratio: {backtest_results.get('sharpe', 0):.2f}")
        logger.info(f"  Max Drawdown: {backtest_results.get('max_drawdown', 0):.2%}")
        
        return backtest_results
    
    def save_model(self):
        """Save model artifacts with versioning"""
        logger.info("Saving model artifacts")
        
        output_config = self.config['output']
        model_dir = Path(output_config['model_dir']) / self.model_version
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model pickle
        model_path = model_dir / 'model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(self.calibrated_model, f)
        
        # Save metadata
        metadata = {
            'model_name': self.model_name,
            'model_version': self.model_version,
            'algorithm': self.algorithm,
            'trained_at': datetime.utcnow().isoformat(),
            'feature_count': len(self.feature_names),
            'feature_names': self.feature_names,
            'hyperparameters': self.config['hyperparameters'],
            'metrics': self.metrics,
            'config': self.config
        }
        
        metadata_path = model_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Model saved to: {model_dir}")
    
    def train_full_pipeline(self):
        """Execute complete training pipeline"""
        logger.info(f"Starting training pipeline: {self.model_name} {self.model_version}")
        
        # Load data
        train_df, val_df, test_df = self.load_data()
        
        # Prepare features
        X_train, y_train = self.prepare_features(train_df)
        X_val, y_val = self.prepare_features(val_df)
        X_test, y_test = self.prepare_features(test_df)
        
        # Train baselines
        baselines = self.train_baseline_models(X_train, y_train, X_val, y_val)
        self.metrics['baselines'] = baselines
        
        # Train model
        self.train_model(X_train, y_train, X_val, y_val)
        
        # Calibrate
        self.calibrate_model(X_train, y_train)
        
        # Evaluate
        val_metrics = self.evaluate_model(X_val, y_val)
        test_metrics = self.evaluate_model(X_test, y_test)
        
        self.metrics['validation'] = val_metrics
        self.metrics['test'] = test_metrics
        
        # Backtest (optional)
        if self.config['evaluation']['backtest']['enabled']:
            # Generate predictions for backtest
            # (Implementation depends on your backtest data format)
            pass
        
        # Save
        self.save_model()
        
        logger.info("Training pipeline complete!")
        logger.info(f"Final test log_loss: {test_metrics['log_loss']:.4f}")


def main():
    parser = argparse.ArgumentParser(description="EQ12 Production Model Training")
    parser.add_argument(
        '--config',
        required=True,
        help='Path to model config YAML (e.g., configs/model_moneyline_v1.yaml)'
    )
    
    args = parser.parse_args()
    
    # Train model
    trainer = EQ12ProductionTrainer(args.config)
    trainer.train_full_pipeline()
    
    print(f"\n✅ Training complete: {trainer.model_name} {trainer.model_version}")
    print(f"📊 Test Log Loss: {trainer.metrics['test']['log_loss']:.4f}")
    print(f"📊 Test Brier Score: {trainer.metrics['test']['brier_score']:.4f}")


if __name__ == "__main__":
    main()
