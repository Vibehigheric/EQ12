"""
EQ12 Parlay ML Model Training Pipeline
Trains calibrated ensemble model for profitable parlay prediction.

Mathematical framework with ensemble methods, calibration, and rigorous validation.
"""

import json
import logging
import os
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import joblib
import argparse

# ML imports
from sklearn.model_selection import TimeSeriesSplit, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (classification_report, roc_auc_score, 
                           brier_score_loss, log_loss, precision_recall_curve)
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from sklearn.linear_model import LogisticRegression

# EQ12 Logging Setup
log_dir = Path("C:/EQ12/logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(
            log_dir / f"model_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnsembleParlayModel:
    """Ensemble ML model for parlay win prediction with calibration."""
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        
        # Base models
        self.rf_model = RandomForestClassifier(
            n_estimators=500,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            class_weight='balanced_subsample',
            random_state=random_state,
            n_jobs=-1
        )
        
        self.xgb_model = xgb.XGBClassifier(
            learning_rate=0.05,
            max_depth=8,
            n_estimators=300,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=random_state,
            eval_metric='logloss'
        )
        
        self.lr_model = LogisticRegression(
            class_weight='balanced',
            random_state=random_state,
            max_iter=1000
        )
        
        # Calibrated ensemble
        self.calibrated_rf = None
        self.calibrated_xgb = None
        self.calibrated_lr = None
        
        # Meta-learner for ensemble
        self.meta_learner = LogisticRegression(random_state=random_state)
        
        # Preprocessor
        self.scaler = StandardScaler()
        
        # Feature importance and selection
        self.feature_names = []
        self.selected_features = []
        
        # Performance metrics
        self.training_metrics = {}
        
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target for training."""
        # Remove non-numeric and identifier columns
        exclude_cols = [
            'parlay_id', 'raw_parlay_json', 'win_loss_label', 
            'sport_primary', 'season'  # Use encoded versions
        ]
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Handle missing values
        X = df[feature_cols].fillna(0)
        
        # Get target
        y = df['win_loss_label'].values
        
        self.feature_names = feature_cols
        logger.info(f"Prepared {len(feature_cols)} features for training")
        
        return X.values, y
    
    def select_features(self, X: np.ndarray, y: np.ndarray, 
                       max_features: int = 50) -> np.ndarray:
        """Select top features using Random Forest importance."""
        # Fit RF for feature selection
        rf_selector = RandomForestClassifier(
            n_estimators=100, random_state=self.random_state, n_jobs=-1
        )
        rf_selector.fit(X, y)
        
        # Get feature importances
        importances = rf_selector.feature_importances_
        feature_importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        # Select top features
        top_features = feature_importance_df.head(max_features)['feature'].tolist()
        feature_indices = [self.feature_names.index(feat) for feat in top_features]
        
        self.selected_features = top_features
        logger.info(f"Selected top {len(top_features)} features")
        logger.info(f"Top 10 features: {top_features[:10]}")
        
        return X[:, feature_indices]
    
    def train_base_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Train individual base models with cross-validation."""
        logger.info("Training base models...")
        
        # Time series split for validation (respects temporal order)
        tscv = TimeSeriesSplit(n_splits=5)
        
        models = {
            'random_forest': self.rf_model,
            'xgboost': self.xgb_model,
            'logistic_regression': self.lr_model
        }
        
        cv_results = {}
        
        for name, model in models.items():
            logger.info(f"Training {name}...")
            
            # Cross-validation scores
            cv_scores = cross_val_score(
                model, X, y, cv=tscv, scoring='roc_auc', n_jobs=-1
            )
            
            # Fit on full dataset
            model.fit(X, y)
            
            cv_results[name] = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'cv_scores': cv_scores.tolist()
            }
            
            logger.info(f"{name} CV ROC-AUC: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
            
        return cv_results
    
    def calibrate_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Calibrate models for better probability estimates."""
        logger.info("Calibrating models...")
        
        # Calibrate each base model
        self.calibrated_rf = CalibratedClassifierCV(
            self.rf_model, method='sigmoid', cv=3
        )
        self.calibrated_xgb = CalibratedClassifierCV(
            self.xgb_model, method='sigmoid', cv=3
        )
        self.calibrated_lr = CalibratedClassifierCV(
            self.lr_model, method='sigmoid', cv=3
        )
        
        calibrated_models = {
            'rf': self.calibrated_rf,
            'xgb': self.calibrated_xgb,
            'lr': self.calibrated_lr
        }
        
        calibration_scores = {}
        
        for name, model in calibrated_models.items():
            model.fit(X, y)
            probs = model.predict_proba(X)[:, 1]
            
            # Brier score (lower is better)
            brier = brier_score_loss(y, probs)
            calibration_scores[f'{name}_brier'] = brier
            
            logger.info(f"{name} Brier Score: {brier:.4f}")
            
        return calibration_scores
    
    def train_ensemble(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Train ensemble meta-learner."""
        logger.info("Training ensemble meta-learner...")
        
        # Get predictions from calibrated models
        rf_probs = self.calibrated_rf.predict_proba(X)[:, 1]
        xgb_probs = self.calibrated_xgb.predict_proba(X)[:, 1]
        lr_probs = self.calibrated_lr.predict_proba(X)[:, 1]
        
        # Stack predictions
        stacked_features = np.column_stack([rf_probs, xgb_probs, lr_probs])
        
        # Train meta-learner
        self.meta_learner.fit(stacked_features, y)
        
        # Evaluate ensemble
        ensemble_probs = self.meta_learner.predict_proba(stacked_features)[:, 1]
        
        ensemble_metrics = {
            'ensemble_roc_auc': roc_auc_score(y, ensemble_probs),
            'ensemble_brier': brier_score_loss(y, ensemble_probs),
            'ensemble_log_loss': log_loss(y, ensemble_probs)
        }
        
        logger.info(f"Ensemble ROC-AUC: {ensemble_metrics['ensemble_roc_auc']:.3f}")
        logger.info(f"Ensemble Brier Score: {ensemble_metrics['ensemble_brier']:.4f}")
        
        return ensemble_metrics
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities using ensemble."""
        # Select features
        feature_indices = [self.feature_names.index(feat) 
                          for feat in self.selected_features]
        X_selected = X[:, feature_indices]
        
        # Scale features
        X_scaled = self.scaler.transform(X_selected)
        
        # Get predictions from calibrated models
        rf_probs = self.calibrated_rf.predict_proba(X_scaled)[:, 1]
        xgb_probs = self.calibrated_xgb.predict_proba(X_scaled)[:, 1]
        lr_probs = self.calibrated_lr.predict_proba(X_scaled)[:, 1]
        
        # Stack and predict with meta-learner
        stacked_features = np.column_stack([rf_probs, xgb_probs, lr_probs])
        ensemble_probs = self.meta_learner.predict_proba(stacked_features)
        
        return ensemble_probs
    
    def calculate_expected_value(self, win_prob: float, odds_american: int, 
                               stake: float = 25.0) -> Dict[str, float]:
        """Calculate expected value for a bet."""
        # Convert American odds to decimal
        if odds_american > 0:
            decimal_odds = (odds_american / 100) + 1
        else:
            decimal_odds = (100 / abs(odds_american)) + 1
            
        # Calculate EV
        payout = stake * (decimal_odds - 1)
        ev = (win_prob * payout) - ((1 - win_prob) * stake)
        ev_percentage = ev / stake
        
        # Kelly criterion
        b = decimal_odds - 1  # Net odds received
        kelly_fraction = (b * win_prob - (1 - win_prob)) / b
        
        return {
            'expected_value': ev,
            'ev_percentage': ev_percentage,
            'kelly_fraction': kelly_fraction,
            'decimal_odds': decimal_odds,
            'implied_prob': 1 / decimal_odds
        }


class ParlayModelTrainer:
    """Main trainer class for EQ12 parlay models."""
    
    def __init__(self, dataset_path: str, output_dir: str = "C:/EQ12/eq12_learn"):
        self.dataset_path = dataset_path
        self.output_dir = Path(output_dir)
        self.model = EnsembleParlayModel()
        
        # Performance tracking
        self.training_history = []
        
    def load_dataset(self) -> pd.DataFrame:
        """Load preprocessed dataset."""
        if self.dataset_path.endswith('.pkl'):
            df = pd.read_pickle(self.dataset_path)
        else:
            df = pd.read_csv(self.dataset_path)
            
        logger.info(f"Loaded dataset: {df.shape[0]} samples, {df.shape[1]} features")
        
        # Filter to decided parlays only for training
        if 'is_decided' in df.columns:
            decided_df = df[df['is_decided'] == 1].copy()
            logger.info(f"Filtered to {len(decided_df)} decided parlays for training")
            return decided_df
            
        return df
    
    def train_model(self) -> Dict[str, Any]:
        """Complete model training pipeline."""
        logger.info("🚀 Starting EQ12 parlay model training...")
        
        # Load dataset
        df = self.load_dataset()
        
        if len(df) < 10:
            raise ValueError(f"Insufficient training data: {len(df)} samples")
            
        # Prepare features
        X, y = self.model.prepare_features(df)
        
        # Feature selection
        X_selected = self.model.select_features(X, y, max_features=30)
        
        # Scale features
        X_scaled = self.model.scaler.fit_transform(X_selected)
        
        training_results = {}
        
        # Train base models
        cv_results = self.model.train_base_models(X_scaled, y)
        training_results['base_models'] = cv_results
        
        # Calibrate models
        calibration_scores = self.model.calibrate_models(X_scaled, y)
        training_results['calibration'] = calibration_scores
        
        # Train ensemble
        ensemble_metrics = self.model.train_ensemble(X_scaled, y)
        training_results['ensemble'] = ensemble_metrics
        
        # Calculate additional metrics
        ensemble_probs = self.model.predict_proba(X)[:, 1]
        
        # Precision-recall analysis
        precision, recall, thresholds = precision_recall_curve(y, ensemble_probs)
        
        # Find optimal threshold for 65% precision
        target_precision = 0.65
        valid_indices = precision >= target_precision
        if np.any(valid_indices):
            optimal_threshold = thresholds[np.where(valid_indices)[0][0]]
        else:
            optimal_threshold = 0.5
            
        training_results['optimal_threshold'] = optimal_threshold
        training_results['target_precision_achievable'] = np.any(valid_indices)
        
        # Performance summary
        win_rate_actual = y.mean()
        high_conf_mask = ensemble_probs >= optimal_threshold
        high_conf_accuracy = y[high_conf_mask].mean() if np.any(high_conf_mask) else 0
        
        training_results['performance_summary'] = {
            'baseline_win_rate': win_rate_actual,
            'high_confidence_accuracy': high_conf_accuracy,
            'high_confidence_samples': int(np.sum(high_conf_mask)),
            'model_selectivity': np.sum(high_conf_mask) / len(y)
        }
        
        self.training_history.append(training_results)
        
        logger.info("✅ Model training completed!")
        logger.info(f"📊 Baseline win rate: {win_rate_actual:.2%}")
        logger.info(f"🎯 High confidence accuracy: {high_conf_accuracy:.2%}")
        logger.info(f"🔍 Model selectivity: {training_results['performance_summary']['model_selectivity']:.2%}")
        
        return training_results
    
    def save_model(self, model_name: str = None) -> str:
        """Save trained model and metadata."""
        if model_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_name = f"parlay_ensemble_model_{timestamp}"
            
        model_path = self.output_dir / f"{model_name}.pkl"
        
        # Save complete model pipeline
        model_package = {
            'ensemble_model': self.model,
            'training_history': self.training_history,
            'feature_names': self.model.feature_names,
            'selected_features': self.model.selected_features,
            'scaler': self.model.scaler,
            'metadata': {
                'training_timestamp': datetime.now().isoformat(),
                'dataset_path': str(self.dataset_path),
                'model_version': '1.0.0'
            }
        }
        
        joblib.dump(model_package, model_path)
        logger.info(f"💾 Model saved: {model_path}")
        
        # Save training report
        report_path = self.output_dir / f"{model_name}_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.training_history[-1], f, indent=2, default=str)
        logger.info(f"📄 Training report saved: {report_path}")
        
        return str(model_path)


def load_trained_model(model_path: str) -> EnsembleParlayModel:
    """Load a trained model from disk."""
    model_package = joblib.load(model_path)
    return model_package['ensemble_model']


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description='Train EQ12 parlay prediction model')
    parser.add_argument('--dataset', required=True,
                       help='Path to processed parlay dataset')
    parser.add_argument('--output-dir', default='C:/EQ12/eq12_learn',
                       help='Output directory for trained model')
    parser.add_argument('--model-name', 
                       help='Custom model name (default: auto-generated)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    try:
        # Initialize trainer
        trainer = ParlayModelTrainer(
            dataset_path=args.dataset,
            output_dir=args.output_dir
        )
        
        # Train model
        results = trainer.train_model()
        
        # Save model
        model_path = trainer.save_model(args.model_name)
        
        logger.info(f"🎉 Training completed successfully!")
        logger.info(f"📈 Final ROC-AUC: {results['ensemble']['ensemble_roc_auc']:.3f}")
        logger.info(f"💾 Model saved: {model_path}")
        
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        raise


if __name__ == "__main__":
    main()