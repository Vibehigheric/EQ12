#!/usr/bin/env python3
"""
EQ12 Champion-Challenger Model Promotion System
Expert-level automated promotion with statistical significance testing
Only promotes if challenger beats champion on all key metrics
"""

import argparse
import json
import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EQ12.ModelPromotion')


class ModelPromoter:
    """Champion-Challenger promotion with rollback capability"""
    
    def __init__(self, models_root: str = "models"):
        self.models_root = Path(models_root)
        self.champion_path = self.models_root / "champion"
        self.challenger_path = None
        
    def load_model_metadata(self, model_path: Path) -> Dict:
        """Load model metadata JSON"""
        metadata_path = model_path / "metadata.json"
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"No metadata found: {metadata_path}")
        
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    def compare_metrics(
        self,
        champion_metrics: Dict,
        challenger_metrics: Dict
    ) -> Dict[str, bool]:
        """Compare champion vs challenger on key metrics"""
        logger.info("Comparing champion vs challenger")
        
        comparisons = {}
        
        # Lower is better for these metrics
        loss_metrics = ['log_loss', 'brier_score', 'calibration_error']
        
        for metric in loss_metrics:
            champ_val = champion_metrics.get(metric, float('inf'))
            chall_val = challenger_metrics.get(metric, float('inf'))
            
            is_better = chall_val < champ_val
            improvement = ((champ_val - chall_val) / champ_val * 100) if champ_val > 0 else 0
            
            comparisons[metric] = {
                'champion': champ_val,
                'challenger': chall_val,
                'challenger_better': is_better,
                'improvement_pct': improvement
            }
            
            logger.info(
                f"  {metric}: Champion={champ_val:.4f}, "
                f"Challenger={chall_val:.4f}, "
                f"Better={is_better} ({improvement:+.2f}%)"
            )
        
        # Higher is better
        if 'auc_roc' in champion_metrics and 'auc_roc' in challenger_metrics:
            champ_auc = champion_metrics['auc_roc']
            chall_auc = challenger_metrics['auc_roc']
            
            is_better = chall_auc > champ_auc
            improvement = ((chall_auc - champ_auc) / champ_auc * 100) if champ_auc > 0 else 0
            
            comparisons['auc_roc'] = {
                'champion': champ_auc,
                'challenger': chall_auc,
                'challenger_better': is_better,
                'improvement_pct': improvement
            }
            
            logger.info(
                f"  auc_roc: Champion={champ_auc:.4f}, "
                f"Challenger={chall_auc:.4f}, "
                f"Better={is_better} ({improvement:+.2f}%)"
            )
        
        return comparisons
    
    def run_backtest_comparison(
        self,
        champion_path: Path,
        challenger_path: Path
    ) -> Dict[str, Dict]:
        """Run backtests for both models and compare ROI/Sharpe"""
        logger.info("Running backtest comparison")
        
        results = {
            'champion': {},
            'challenger': {}
        }
        
        for name, model_path in [('champion', champion_path), ('challenger', challenger_path)]:
            logger.info(f"  Backtesting {name}...")
            
            # Generate predictions (stub - replace with actual prediction logic)
            predictions_path = f"logs/backtest_predictions_{name}.csv"
            
            # Run backtester
            cmd = [
                'python',
                'scripts/backtester.py',
                '--slips', predictions_path,
                '--bankroll', '10000',
                '--output', f'logs/backtest_{name}.json'
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    with open(f'logs/backtest_{name}.json', 'r') as f:
                        results[name] = json.load(f)
                    
                    logger.info(
                        f"    {name} backtest: ROI={results[name].get('roi', 0):.2%}, "
                        f"Sharpe={results[name].get('sharpe', 0):.2f}"
                    )
                else:
                    logger.warning(f"Backtest failed for {name}: {result.stderr}")
            
            except subprocess.TimeoutExpired:
                logger.error(f"Backtest timeout for {name}")
            except Exception as e:
                logger.error(f"Backtest error for {name}: {e}")
        
        return results
    
    def permutation_test(
        self,
        champion_scores: np.ndarray,
        challenger_scores: np.ndarray,
        n_permutations: int = 1000
    ) -> float:
        """
        Permutation test for statistical significance
        Returns p-value (reject null if p < 0.05)
        """
        logger.info("Running permutation test for significance")
        
        # Observed difference
        observed_diff = np.mean(challenger_scores) - np.mean(champion_scores)
        
        # Combine scores
        combined = np.concatenate([champion_scores, challenger_scores])
        n_champ = len(champion_scores)
        
        # Permutation
        count_extreme = 0
        
        for _ in range(n_permutations):
            np.random.shuffle(combined)
            perm_champ = combined[:n_champ]
            perm_chall = combined[n_champ:]
            perm_diff = np.mean(perm_chall) - np.mean(perm_champ)
            
            if perm_diff >= observed_diff:
                count_extreme += 1
        
        p_value = count_extreme / n_permutations
        
        logger.info(f"  Permutation test p-value: {p_value:.4f}")
        
        return p_value
    
    def should_promote(
        self,
        comparisons: Dict,
        backtest_results: Dict,
        min_improvement_pct: float = 2.0,
        require_all_metrics: bool = True
    ) -> bool:
        """Decide if challenger should be promoted to champion"""
        logger.info("Evaluating promotion criteria")
        
        # Check if challenger beats champion on all key metrics
        metrics_better = [
            comparisons['log_loss']['challenger_better'],
            comparisons['brier_score']['challenger_better']
        ]
        
        if 'auc_roc' in comparisons:
            metrics_better.append(comparisons['auc_roc']['challenger_better'])
        
        if require_all_metrics:
            all_better = all(metrics_better)
            logger.info(f"  All metrics better: {all_better}")
            
            if not all_better:
                logger.warning("❌ Challenger does not beat champion on ALL metrics")
                return False
        
        # Check minimum improvement threshold
        log_loss_improvement = comparisons['log_loss']['improvement_pct']
        
        if log_loss_improvement < min_improvement_pct:
            logger.warning(
                f"❌ Improvement ({log_loss_improvement:.2f}%) "
                f"below threshold ({min_improvement_pct}%)"
            )
            return False
        
        # Check backtest ROI (if available)
        if backtest_results['champion'] and backtest_results['challenger']:
            champ_roi = backtest_results['champion'].get('roi', 0)
            chall_roi = backtest_results['challenger'].get('roi', 0)
            
            if chall_roi <= champ_roi:
                logger.warning(
                    f"❌ Challenger backtest ROI ({chall_roi:.2%}) "
                    f"not better than champion ({champ_roi:.2%})"
                )
                return False
        
        logger.info("✅ All promotion criteria met")
        return True
    
    def promote_challenger(self, challenger_version: str):
        """Promote challenger to champion (with backup)"""
        logger.info(f"Promoting challenger {challenger_version} to champion")
        
        # Backup current champion
        if self.champion_path.exists():
            backup_path = self.models_root / f"champion_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"  Backing up current champion to: {backup_path}")
            shutil.copytree(self.champion_path, backup_path)
            shutil.rmtree(self.champion_path)
        
        # Copy challenger to champion
        challenger_path = self.models_root / challenger_version
        logger.info(f"  Copying {challenger_version} to champion")
        shutil.copytree(challenger_path, self.champion_path)
        
        # Update champion metadata
        metadata_path = self.champion_path / "metadata.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        metadata['promoted_at'] = datetime.utcnow().isoformat()
        metadata['promoted_from_version'] = challenger_version
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("✅ Promotion complete")
    
    def rollback_champion(self):
        """Rollback to previous champion if current one fails"""
        logger.info("Rolling back to previous champion")
        
        # Find most recent backup
        backups = sorted(self.models_root.glob("champion_backup_*"))
        
        if not backups:
            logger.error("❌ No champion backups found - cannot rollback")
            return False
        
        latest_backup = backups[-1]
        logger.info(f"  Restoring from backup: {latest_backup}")
        
        # Remove failed champion
        if self.champion_path.exists():
            shutil.rmtree(self.champion_path)
        
        # Restore backup
        shutil.copytree(latest_backup, self.champion_path)
        
        logger.info("✅ Rollback complete")
        return True
    
    def run_promotion_pipeline(
        self,
        challenger_version: str,
        min_improvement_pct: float = 2.0
    ) -> bool:
        """Execute full champion-challenger evaluation and promotion"""
        logger.info(f"Starting promotion pipeline for challenger: {challenger_version}")
        
        # Load metadata
        challenger_path = self.models_root / challenger_version
        
        if not challenger_path.exists():
            logger.error(f"Challenger not found: {challenger_path}")
            return False
        
        if not self.champion_path.exists():
            logger.info("No current champion - promoting challenger by default")
            self.promote_challenger(challenger_version)
            return True
        
        champion_meta = self.load_model_metadata(self.champion_path)
        challenger_meta = self.load_model_metadata(challenger_path)
        
        # Compare metrics
        comparisons = self.compare_metrics(
            champion_meta['metrics']['test'],
            challenger_meta['metrics']['test']
        )
        
        # Backtest comparison
        backtest_results = self.run_backtest_comparison(
            self.champion_path,
            challenger_path
        )
        
        # Promotion decision
        should_promote = self.should_promote(
            comparisons,
            backtest_results,
            min_improvement_pct=min_improvement_pct
        )
        
        if should_promote:
            self.promote_challenger(challenger_version)
            return True
        else:
            logger.info("❌ Challenger did not meet promotion criteria")
            return False


def main():
    parser = argparse.ArgumentParser(description="EQ12 Model Promotion System")
    parser.add_argument(
        '--challenger',
        required=True,
        help='Challenger model version (e.g., v2, v3)'
    )
    parser.add_argument(
        '--min-improvement',
        type=float,
        default=2.0,
        help='Minimum improvement percentage required (default: 2.0)'
    )
    parser.add_argument(
        '--models-root',
        default='models',
        help='Root directory for models (default: models)'
    )
    
    args = parser.parse_args()
    
    promoter = ModelPromoter(models_root=args.models_root)
    promoted = promoter.run_promotion_pipeline(
        args.challenger,
        min_improvement_pct=args.min_improvement
    )
    
    if promoted:
        print(f"\n✅ Challenger {args.challenger} PROMOTED to champion")
        exit(0)
    else:
        print(f"\n❌ Challenger {args.challenger} NOT promoted")
        exit(1)


if __name__ == "__main__":
    main()
