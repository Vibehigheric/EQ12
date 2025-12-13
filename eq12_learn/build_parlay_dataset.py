"""
EQ12 ML Parlay Dataset Builder
Extracts training features from 958+ analyzed parlays for ML model training.

Transforms historical parlay logs into ML-ready dataset with comprehensive feature engineering.
"""

import json
import logging
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re
from sklearn.preprocessing import LabelEncoder, StandardScaler
import argparse

# EQ12 Logging Setup
log_dir = Path("C:/EQ12/logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"parlay_dataset_builder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ParlayDatasetBuilder:
    """Extracts ML training features from historical parlay analysis logs."""
    
    def __init__(self, logs_dir: str = "C:/EQ12/logs"):
        self.logs_dir = Path(logs_dir)
        self.raw_data = []
        self.features_df = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        
    def load_parlay_logs(self) -> List[Dict]:
        """Load all parlay analysis JSON files from logs directory."""
        parlay_files = list(self.logs_dir.glob("parlay_analysis_*.json"))
        logger.info(f"Found {len(parlay_files)} parlay analysis files")
        
        all_parlays = []
        for file_path in parlay_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'parlays' in data:
                        all_parlays.extend(data['parlays'])
                        logger.info(f"Loaded {len(data['parlays'])} parlays from {file_path.name}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                
        logger.info(f"Total parlays loaded: {len(all_parlays)}")
        self.raw_data = all_parlays
        return all_parlays
    
    def extract_outcome_features(self, parlay: Dict) -> Dict:
        """Extract win/loss and financial outcome features."""
        features = {}
        
        # Target variable (win/loss)
        outcome = parlay.get('outcome', 'pending').lower()
        features['win_loss_label'] = 1 if outcome == 'win' else 0
        features['is_decided'] = 1 if outcome in ['win', 'loss'] else 0
        
        # Financial features
        features['stake_amount'] = float(parlay.get('stake', 0))
        features['potential_payout'] = float(parlay.get('potential_payout', 0))
        features['actual_payout'] = float(parlay.get('actual_payout', 0)) if outcome == 'win' else 0
        features['net_profit_loss'] = features['actual_payout'] - features['stake_amount']
        
        # ROI calculation
        if features['stake_amount'] > 0:
            features['roi'] = features['net_profit_loss'] / features['stake_amount']
        else:
            features['roi'] = 0
            
        return features
    
    def extract_temporal_features(self, parlay: Dict) -> Dict:
        """Extract time-based features from parlay timestamp."""
        features = {}
        
        try:
            # Parse timestamp
            timestamp_str = parlay.get('timestamp', '')
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                timestamp = datetime.now()
                
            features['day_of_week'] = timestamp.weekday()  # 0=Monday, 6=Sunday
            features['month'] = timestamp.month
            features['hour'] = timestamp.hour
            features['is_weekend'] = 1 if timestamp.weekday() >= 5 else 0
            
            # Season mapping
            month = timestamp.month
            if month in [9, 10, 11, 12, 1]:
                features['season'] = 'football'
            elif month in [4, 5, 6, 7, 8, 9]:
                features['season'] = 'baseball'
            elif month in [10, 11, 12, 1, 2, 3, 4]:
                features['season'] = 'basketball'
            else:
                features['season'] = 'other'
                
        except Exception as e:
            logger.warning(f"Error parsing timestamp: {e}")
            features.update({
                'day_of_week': 0, 'month': 1, 'hour': 12, 
                'is_weekend': 0, 'season': 'other'
            })
            
        return features
    
    def extract_sport_features(self, parlay: Dict) -> Dict:
        """Extract sport-specific features."""
        features = {}
        
        # Primary sport detection
        sport = parlay.get('sport', '').upper()
        if not sport:
            # Try to infer from legs
            legs = parlay.get('legs', [])
            sports_found = set()
            for leg in legs:
                leg_text = str(leg).upper()
                if any(term in leg_text for term in ['NFL', 'FOOTBALL']):
                    sports_found.add('NFL')
                elif any(term in leg_text for term in ['NBA', 'BASKETBALL']):
                    sports_found.add('NBA')  
                elif any(term in leg_text for term in ['MLB', 'BASEBALL']):
                    sports_found.add('MLB')
            sport = list(sports_found)[0] if sports_found else 'UNKNOWN'
            
        features['sport_primary'] = sport
        features['is_nfl'] = 1 if sport == 'NFL' else 0
        features['is_nba'] = 1 if sport == 'NBA' else 0
        features['is_mlb'] = 1 if sport == 'MLB' else 0
        features['is_mixed_sport'] = 1 if len(parlay.get('legs', [])) > 1 and 'mix' in str(parlay).lower() else 0
        
        return features
    
    def extract_parlay_structure_features(self, parlay: Dict) -> Dict:
        """Extract features about parlay structure and composition."""
        features = {}
        
        legs = parlay.get('legs', [])
        features['leg_count'] = len(legs)
        
        # Bet type analysis
        bet_types = []
        has_spread = has_total = has_moneyline = has_prop = 0
        
        for leg in legs:
            leg_text = str(leg).upper()
            if any(term in leg_text for term in ['+', '-', 'SPREAD']):
                has_spread = 1
                bet_types.append('spread')
            elif any(term in leg_text for term in ['OVER', 'UNDER', 'TOTAL']):
                has_total = 1
                bet_types.append('total')
            elif any(term in leg_text for term in ['ML', 'MONEYLINE', 'WIN']):
                has_moneyline = 1
                bet_types.append('moneyline')
            else:
                has_prop = 1
                bet_types.append('prop')
                
        features['has_spread'] = has_spread
        features['has_total'] = has_total
        features['has_moneyline'] = has_moneyline
        features['has_prop'] = has_prop
        features['bet_type_diversity'] = len(set(bet_types))
        
        # SGP (Same Game Parlay) detection
        features['is_sgp'] = 1 if parlay.get('type', '').upper() == 'SGP' or 'sgp' in str(parlay).lower() else 0
        
        # Odds and probability features
        odds_american = parlay.get('odds_american', 0)
        if odds_american:
            if odds_american > 0:
                implied_prob = 100 / (odds_american + 100)
            else:
                implied_prob = abs(odds_american) / (abs(odds_american) + 100)
        else:
            implied_prob = 0.5
            
        features['odds_american'] = odds_american
        features['implied_probability'] = implied_prob
        features['implied_fair_payout'] = 1 / implied_prob if implied_prob > 0 else 0
        
        return features
    
    def extract_team_features(self, parlay: Dict) -> Dict:
        """Extract team-specific features from parlay legs."""
        features = {}
        
        legs = parlay.get('legs', [])
        teams_mentioned = []
        
        # Common team abbreviations
        nfl_teams = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 
                    'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC', 'LV', 'LAC', 'LAR', 'MIA', 
                    'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS']
        
        for leg in legs:
            leg_text = str(leg).upper()
            for team in nfl_teams:
                if team in leg_text:
                    teams_mentioned.append(team)
                    
        features['unique_teams_count'] = len(set(teams_mentioned))
        features['has_divisional_matchup'] = 0  # TODO: Implement divisional detection
        features['has_primetime_team'] = 1 if any(team in ['DAL', 'GB', 'NE', 'PIT'] for team in teams_mentioned) else 0
        
        return features
    
    def calculate_correlation_score(self, parlay: Dict) -> float:
        """Calculate correlation risk score for parlay legs."""
        legs = parlay.get('legs', [])
        if len(legs) < 2:
            return 0.0
            
        correlation_score = 0.0
        
        # Same game correlation (highest risk)
        same_game_legs = 0
        for i, leg1 in enumerate(legs):
            for leg2 in legs[i+1:]:
                if self._legs_same_game(str(leg1), str(leg2)):
                    same_game_legs += 1
                    correlation_score += 0.8  # High correlation penalty
                    
        # Player prop correlation
        if parlay.get('type', '').upper() == 'SGP':
            correlation_score += 0.5
            
        return min(correlation_score, 1.0)  # Cap at 1.0
    
    def _legs_same_game(self, leg1: str, leg2: str) -> bool:
        """Check if two legs are from the same game."""
        # Simple team name matching - can be improved
        common_teams = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN']
        
        leg1_teams = [team for team in common_teams if team in leg1.upper()]
        leg2_teams = [team for team in common_teams if team in leg2.upper()]
        
        return bool(set(leg1_teams) & set(leg2_teams))
    
    def build_feature_matrix(self) -> pd.DataFrame:
        """Build complete feature matrix from loaded parlay data."""
        if not self.raw_data:
            logger.error("No parlay data loaded. Call load_parlay_logs() first.")
            return pd.DataFrame()
            
        logger.info(f"Building feature matrix from {len(self.raw_data)} parlays...")
        
        all_features = []
        
        for i, parlay in enumerate(self.raw_data):
            try:
                features = {}
                
                # Add unique identifier
                features['parlay_id'] = f"parlay_{i:06d}"
                
                # Extract all feature categories
                features.update(self.extract_outcome_features(parlay))
                features.update(self.extract_temporal_features(parlay))
                features.update(self.extract_sport_features(parlay))
                features.update(self.extract_parlay_structure_features(parlay))
                features.update(self.extract_team_features(parlay))
                
                # Add correlation risk score
                features['correlation_risk_score'] = self.calculate_correlation_score(parlay)
                
                # Store raw parlay for reference
                features['raw_parlay_json'] = json.dumps(parlay)
                
                all_features.append(features)
                
            except Exception as e:
                logger.error(f"Error processing parlay {i}: {e}")
                continue
                
        # Convert to DataFrame
        df = pd.DataFrame(all_features)
        
        # Handle categorical variables
        categorical_columns = ['sport_primary', 'season']
        for col in categorical_columns:
            if col in df.columns:
                le = LabelEncoder()
                df[f'{col}_encoded'] = le.fit_transform(df[col].fillna('unknown'))
                self.label_encoders[col] = le
                
        logger.info(f"Feature matrix built: {df.shape[0]} samples, {df.shape[1]} features")
        logger.info(f"Features: {list(df.columns)}")
        
        # Log feature statistics
        if 'win_loss_label' in df.columns:
            win_rate = df['win_loss_label'].mean()
            logger.info(f"Overall win rate in dataset: {win_rate:.2%}")
            
        self.features_df = df
        return df
    
    def save_dataset(self, output_path: str = None) -> str:
        """Save processed dataset to CSV and pickle files."""
        if self.features_df is None:
            raise ValueError("No dataset built. Call build_feature_matrix() first.")
            
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"C:/EQ12/eq12_learn/parlay_dataset_{timestamp}"
            
        # Save as CSV
        csv_path = f"{output_path}.csv"
        self.features_df.to_csv(csv_path, index=False)
        logger.info(f"Dataset saved to CSV: {csv_path}")
        
        # Save as pickle (preserves data types)
        pkl_path = f"{output_path}.pkl"
        self.features_df.to_pickle(pkl_path)
        logger.info(f"Dataset saved to pickle: {pkl_path}")
        
        # Save label encoders
        encoders_path = f"{output_path}_encoders.pkl"
        pd.to_pickle(self.label_encoders, encoders_path)
        logger.info(f"Label encoders saved: {encoders_path}")
        
        # Save feature summary report
        self._save_feature_report(f"{output_path}_report.json")
        
        return csv_path
    
    def _save_feature_report(self, report_path: str):
        """Save comprehensive feature analysis report."""
        if self.features_df is None:
            return
            
        report = {
            'dataset_info': {
                'total_samples': len(self.features_df),
                'total_features': len(self.features_df.columns),
                'generation_timestamp': datetime.now().isoformat(),
                'source_files_count': len(list(self.logs_dir.glob("parlay_analysis_*.json")))
            },
            'target_distribution': {},
            'feature_statistics': {},
            'data_quality': {}
        }
        
        # Target distribution
        if 'win_loss_label' in self.features_df.columns:
            wins = self.features_df['win_loss_label'].sum()
            total = len(self.features_df)
            report['target_distribution'] = {
                'wins': int(wins),
                'losses': int(total - wins),
                'win_rate': float(wins / total),
                'samples_decided': int(self.features_df['is_decided'].sum())
            }
            
        # Feature statistics for numeric columns
        numeric_cols = self.features_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col != 'win_loss_label':  # Skip target
                report['feature_statistics'][col] = {
                    'mean': float(self.features_df[col].mean()),
                    'std': float(self.features_df[col].std()),
                    'min': float(self.features_df[col].min()),
                    'max': float(self.features_df[col].max()),
                    'missing_count': int(self.features_df[col].isna().sum())
                }
                
        # Data quality metrics
        report['data_quality'] = {
            'total_missing_values': int(self.features_df.isna().sum().sum()),
            'samples_with_missing': int((self.features_df.isna().any(axis=1)).sum()),
            'duplicate_rows': int(self.features_df.duplicated().sum())
        }
        
        # Save report
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Feature report saved: {report_path}")


def main():
    """Main execution function for dataset building."""
    parser = argparse.ArgumentParser(description='Build ML dataset from EQ12 parlay logs')
    parser.add_argument('--logs-dir', default='C:/EQ12/logs', 
                       help='Directory containing parlay analysis logs')
    parser.add_argument('--output-dir', default='C:/EQ12/eq12_learn',
                       help='Output directory for dataset files')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    logger.info("🚀 EQ12 Parlay Dataset Builder Starting...")
    
    try:
        # Initialize builder
        builder = ParlayDatasetBuilder(logs_dir=args.logs_dir)
        
        # Load parlay data
        builder.load_parlay_logs()
        
        # Build feature matrix
        df = builder.build_feature_matrix()
        
        if df.empty:
            logger.error("❌ No features extracted. Check parlay logs.")
            return
            
        # Save dataset
        output_path = os.path.join(args.output_dir, 'parlay_dataset')
        final_path = builder.save_dataset(output_path)
        
        logger.info(f"✅ Dataset building completed successfully!")
        logger.info(f"📊 Final dataset: {df.shape[0]} samples, {df.shape[1]} features")
        logger.info(f"💾 Saved to: {final_path}")
        
        # Quick validation
        if 'win_loss_label' in df.columns:
            win_rate = df['win_loss_label'].mean()
            total_decided = df['is_decided'].sum()
            logger.info(f"🎯 Win rate: {win_rate:.2%} ({total_decided} decided parlays)")
            
    except Exception as e:
        logger.error(f"❌ Dataset building failed: {e}")
        raise


if __name__ == "__main__":
    main()