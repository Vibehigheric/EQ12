#!/usr/bin/env python3
"""
EQ12 Model Drift Detection System
Expert-level monitoring using PSI (Population Stability Index)
Triggers alerts when feature distributions or prediction calibration degrades
"""

import argparse
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EQ12.DriftMonitor')


class PopulationStabilityIndex:
    """Calculate PSI for feature drift detection"""
    
    @staticmethod
    def calculate_psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
        """
        Calculate PSI between two distributions
        PSI < 0.10: No significant change
        0.10 <= PSI < 0.25: Moderate shift (investigate)
        PSI >= 0.25: Significant shift (retrain required)
        """
        # Create bins from expected distribution
        breakpoints = np.percentile(expected, np.linspace(0, 100, bins + 1))
        breakpoints = np.unique(breakpoints)  # Remove duplicates
        
        if len(breakpoints) < 2:
            logger.warning("Not enough unique values for PSI calculation")
            return 0.0
        
        # Bin both distributions
        expected_counts = np.histogram(expected, bins=breakpoints)[0]
        actual_counts = np.histogram(actual, bins=breakpoints)[0]
        
        # Convert to percentages
        expected_pct = expected_counts / len(expected)
        actual_pct = actual_counts / len(actual)
        
        # Avoid division by zero
        expected_pct = np.where(expected_pct == 0, 0.0001, expected_pct)
        actual_pct = np.where(actual_pct == 0, 0.0001, actual_pct)
        
        # Calculate PSI
        psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
        
        return psi


class DriftMonitor:
    """Monitor model drift across features and predictions"""
    
    def __init__(self, model_dir: str, threshold_psi: float = 0.15):
        self.model_dir = Path(model_dir)
        self.threshold_psi = threshold_psi
        self.psi_calculator = PopulationStabilityIndex()
        self.drift_results = {}
        
    def load_reference_data(self) -> pd.DataFrame:
        """Load training data as reference distribution"""
        metadata_path = self.model_dir / 'metadata.json'
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        train_data_path = metadata['config']['data']['train_data']
        logger.info(f"Loading reference data: {train_data_path}")
        
        return pd.read_csv(train_data_path)
    
    def load_production_data(self, days: int = 7) -> pd.DataFrame:
        """Load recent production data"""
        # Query last N days from prediction log
        db_path = 'data/eq12_predictions.db'
        
        if not Path(db_path).exists():
            logger.warning("No production predictions database found")
            return pd.DataFrame()
        
        conn = sqlite3.connect(db_path)
        
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        query = f"""
            SELECT * FROM predictions
            WHERE prediction_time > '{cutoff}'
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        logger.info(f"Loaded {len(df)} production predictions from last {days} days")
        
        return df
    
    def calculate_feature_drift(
        self,
        reference_df: pd.DataFrame,
        production_df: pd.DataFrame,
        feature_names: List[str]
    ) -> Dict[str, float]:
        """Calculate PSI for each feature"""
        logger.info("Calculating feature drift (PSI)")
        
        feature_psi = {}
        
        for feature in feature_names:
            if feature not in reference_df.columns or feature not in production_df.columns:
                logger.warning(f"Feature {feature} not in both datasets, skipping")
                continue
            
            # Handle missing values
            ref_values = reference_df[feature].dropna().values
            prod_values = production_df[feature].dropna().values
            
            if len(ref_values) < 10 or len(prod_values) < 10:
                logger.warning(f"Insufficient data for {feature}")
                continue
            
            psi = self.psi_calculator.calculate_psi(ref_values, prod_values)
            feature_psi[feature] = psi
            
            if psi >= self.threshold_psi:
                logger.warning(f"  ⚠️  {feature}: PSI={psi:.4f} (DRIFT DETECTED)")
            else:
                logger.info(f"  ✓  {feature}: PSI={psi:.4f}")
        
        return feature_psi
    
    def calculate_prediction_drift(
        self,
        reference_df: pd.DataFrame,
        production_df: pd.DataFrame
    ) -> Dict[str, float]:
        """Check if prediction distribution has shifted"""
        logger.info("Calculating prediction drift")
        
        if 'predicted_prob' not in production_df.columns:
            logger.warning("No predicted_prob in production data")
            return {}
        
        ref_preds = reference_df.get('predicted_prob', np.full(len(reference_df), 0.5))
        prod_preds = production_df['predicted_prob'].values
        
        psi = self.psi_calculator.calculate_psi(ref_preds, prod_preds)
        
        # KS test for distribution difference
        ks_stat, ks_pval = stats.ks_2samp(ref_preds, prod_preds)
        
        results = {
            'prediction_psi': psi,
            'ks_statistic': ks_stat,
            'ks_pvalue': ks_pval
        }
        
        logger.info(f"  Prediction PSI: {psi:.4f}")
        logger.info(f"  KS Test: stat={ks_stat:.4f}, p={ks_pval:.4f}")
        
        return results
    
    def calculate_performance_drift(
        self,
        production_df: pd.DataFrame
    ) -> Dict[str, float]:
        """Check if model performance is degrading"""
        logger.info("Calculating performance drift")
        
        if 'actual_outcome' not in production_df.columns:
            logger.warning("No actual outcomes available yet")
            return {}
        
        # Filter to records with outcomes
        scored = production_df.dropna(subset=['actual_outcome'])
        
        if len(scored) < 50:
            logger.warning("Insufficient scored predictions for performance check")
            return {}
        
        y_true = scored['actual_outcome'].values
        y_pred = scored['predicted_prob'].values
        
        # Calculate log loss over time windows
        from sklearn.metrics import log_loss, brier_score_loss
        
        recent_logloss = log_loss(y_true[-100:], y_pred[-100:])
        overall_logloss = log_loss(y_true, y_pred)
        
        recent_brier = brier_score_loss(y_true[-100:], y_pred[-100:])
        overall_brier = brier_score_loss(y_true, y_pred)
        
        results = {
            'recent_log_loss': recent_logloss,
            'overall_log_loss': overall_logloss,
            'log_loss_degradation': recent_logloss - overall_logloss,
            'recent_brier': recent_brier,
            'overall_brier': overall_brier
        }
        
        logger.info(f"  Recent Log Loss: {recent_logloss:.4f}")
        logger.info(f"  Overall Log Loss: {overall_logloss:.4f}")
        
        return results
    
    def save_drift_report(self):
        """Save drift analysis to database + JSON"""
        logger.info("Saving drift report")
        
        # Save to logs
        report_path = f"logs/drift_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        Path('logs').mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.drift_results, f, indent=2)
        
        # Save to memory database for BI-Core
        db_path = 'data/eq12_memory.db'
        conn = sqlite3.connect(db_path)
        
        # Create table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS drift_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checked_at_utc TEXT NOT NULL,
                model_version TEXT NOT NULL,
                max_feature_psi REAL,
                prediction_psi REAL,
                performance_degradation REAL,
                drift_detected INTEGER,
                full_report TEXT
            )
        """)
        
        max_psi = max(self.drift_results.get('feature_psi', {}).values(), default=0)
        drift_detected = 1 if max_psi >= self.threshold_psi else 0
        
        conn.execute("""
            INSERT INTO drift_snapshots 
            (checked_at_utc, model_version, max_feature_psi, prediction_psi, 
             performance_degradation, drift_detected, full_report)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            str(self.model_dir.name),
            max_psi,
            self.drift_results.get('prediction_drift', {}).get('prediction_psi', 0),
            self.drift_results.get('performance_drift', {}).get('log_loss_degradation', 0),
            drift_detected,
            json.dumps(self.drift_results)
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Drift report saved: {report_path}")
    
    def run_drift_check(self, production_days: int = 7) -> bool:
        """Execute complete drift monitoring pipeline"""
        logger.info(f"Running drift check for model: {self.model_dir.name}")
        
        # Load data
        reference_df = self.load_reference_data()
        production_df = self.load_production_data(days=production_days)
        
        if production_df.empty:
            logger.warning("No production data available, skipping drift check")
            return False
        
        # Load feature names
        metadata_path = self.model_dir / 'metadata.json'
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        feature_names = metadata['feature_names']
        
        # Calculate drift metrics
        self.drift_results['feature_psi'] = self.calculate_feature_drift(
            reference_df, production_df, feature_names
        )
        
        self.drift_results['prediction_drift'] = self.calculate_prediction_drift(
            reference_df, production_df
        )
        
        self.drift_results['performance_drift'] = self.calculate_performance_drift(
            production_df
        )
        
        # Save report
        self.save_drift_report()
        
        # Determine if retrain needed
        max_psi = max(self.drift_results['feature_psi'].values(), default=0)
        
        if max_psi >= 0.25:
            logger.error(f"❌ CRITICAL DRIFT DETECTED (PSI={max_psi:.4f}) - RETRAIN REQUIRED")
            return True
        elif max_psi >= self.threshold_psi:
            logger.warning(f"⚠️  MODERATE DRIFT DETECTED (PSI={max_psi:.4f}) - INVESTIGATE")
            return True
        else:
            logger.info(f"✅ No significant drift detected (max PSI={max_psi:.4f})")
            return False


def main():
    parser = argparse.ArgumentParser(description="EQ12 Model Drift Detection")
    parser.add_argument(
        '--model-dir',
        required=True,
        help='Path to model directory (e.g., models/v1)'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.15,
        help='PSI threshold for drift alert (default: 0.15)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Days of production data to check (default: 7)'
    )
    
    args = parser.parse_args()
    
    monitor = DriftMonitor(args.model_dir, threshold_psi=args.threshold)
    drift_detected = monitor.run_drift_check(production_days=args.days)
    
    if drift_detected:
        print(f"\n⚠️  DRIFT DETECTED - Consider retraining model")
        exit(1)
    else:
        print(f"\n✅ Model stable - No drift detected")
        exit(0)


if __name__ == "__main__":
    main()
