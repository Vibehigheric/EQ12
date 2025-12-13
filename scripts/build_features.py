#!/usr/bin/env python3
"""
EQ12 Feature Engineering Pipeline
Domain-specific sports betting features with versioning and reproducibility
"""

import argparse
import json
import logging
import numpy as np
import pandas as pd
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EQ12FeatureBuilder:
    """Production-grade feature engineering for sports betting models"""
    
    def __init__(self, config_path: str):
        """Initialize with YAML config"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.feature_version = self.config['model']['version']
        self.random_state = self.config['reproducibility']['random_seed']
        
        # Set seeds for reproducibility
        np.random.seed(self.random_state)
        
    def load_raw_data(self, data_path: str) -> pd.DataFrame:
        """Load raw game/event data"""
        logger.info(f"Loading data from {data_path}")
        
        if not Path(data_path).exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(df)} records")
        
        # Ensure datetime column
        if 'game_date' in df.columns:
            df['game_date'] = pd.to_datetime(df['game_date'])
        
        return df
    
    def build_rolling_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rolling averages for team stats"""
        logger.info("Building rolling statistics features")
        
        windows = self.config['features']['rolling_windows']
        
        # Sort by team and date for proper rolling
        df = df.sort_values(['team_id', 'game_date'])
        
        # Example rolling features (customize per your data)
        stat_cols = [col for col in df.columns if any(
            stat in col.lower() for stat in ['pts', 'reb', 'ast', 'fg', 'score']
        )]
        
        for window in windows:
            for col in stat_cols:
                if col in df.columns:
                    # Rolling mean
                    df[f'{col}_roll_{window}'] = (
                        df.groupby('team_id')[col]
                        .transform(lambda x: x.rolling(window, min_periods=1).mean())
                    )
                    
                    # Rolling std (volatility)
                    df[f'{col}_roll_{window}_std'] = (
                        df.groupby('team_id')[col]
                        .transform(lambda x: x.rolling(window, min_periods=1).std())
                    )
        
        logger.info(f"Created rolling features for {len(stat_cols)} stats")
        return df
    
    def build_opponent_adjusted_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Strength-of-schedule adjusted metrics"""
        logger.info("Building opponent-adjusted features")
        
        if not self.config['features']['opponent_adjustment']:
            return df
        
        # Calculate opponent strength (average of points allowed, etc.)
        if 'opponent_id' in df.columns and 'pts_allowed' in df.columns:
            opp_strength = df.groupby('opponent_id')['pts_allowed'].mean()
            df['opponent_defensive_strength'] = df['opponent_id'].map(opp_strength)
            
            # Adjust offensive stats by opponent strength
            if 'pts_roll_10' in df.columns:
                df['pts_roll_10_opp_adj'] = (
                    df['pts_roll_10'] / (df['opponent_defensive_strength'] + 1e-6)
                )
        
        return df
    
    def build_market_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Market movement and line features"""
        logger.info("Building market movement features")
        
        if not self.config['features']['market_features']:
            return df
        
        # Line movement (opening to closing)
        if 'opening_line' in df.columns and 'closing_line' in df.columns:
            df['line_movement'] = df['closing_line'] - df['opening_line']
            df['line_movement_pct'] = (
                df['line_movement'] / (abs(df['opening_line']) + 1e-6)
            )
            
            # Steam move detection (large rapid movement)
            df['steam_move'] = (abs(df['line_movement']) > 2.0).astype(int)
        
        # Implied probability from odds
        if 'closing_odds' in df.columns:
            df['market_implied_prob'] = self._odds_to_probability(df['closing_odds'])
        
        return df
    
    def build_contextual_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rest days, travel, home/away, etc."""
        logger.info("Building contextual features")
        
        # Rest days between games
        if 'game_date' in df.columns:
            df = df.sort_values(['team_id', 'game_date'])
            df['days_rest'] = (
                df.groupby('team_id')['game_date']
                .diff()
                .dt.total_seconds() / 86400
            )
            df['days_rest'] = df['days_rest'].fillna(7)  # Default for first game
            
            # Back-to-back games
            df['is_back_to_back'] = (df['days_rest'] <= 1).astype(int)
        
        # Home advantage
        if 'is_home' in df.columns:
            df['home_advantage'] = df['is_home'].astype(int)
        
        # Day of week effects
        if 'game_date' in df.columns:
            df['day_of_week'] = df['game_date'].dt.dayofweek
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        return df
    
    def build_injury_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Injury list impact features"""
        logger.info("Building injury impact features")
        
        if not self.config['features']['injury_weighted']:
            return df
        
        # Placeholder - integrate with your injury tracking
        if 'injured_players_count' in df.columns:
            df['injury_impact'] = df['injured_players_count']
            
            # Weight by player importance (if available)
            if 'injured_star_players' in df.columns:
                df['injury_impact_weighted'] = (
                    df['injured_players_count'] + 
                    df['injured_star_players'] * 2  # Stars count more
                )
        
        return df
    
    def build_weather_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Weather impact (outdoor sports)"""
        logger.info("Building weather features")
        
        if not self.config['features']['weather_enabled']:
            return df
        
        # Temperature, wind, precipitation effects
        weather_cols = ['temperature', 'wind_speed', 'precipitation']
        for col in weather_cols:
            if col in df.columns:
                df[f'{col}_z'] = (
                    (df[col] - df[col].mean()) / (df[col].std() + 1e-6)
                )
        
        # Extreme weather flags
        if 'wind_speed' in df.columns:
            df['high_wind'] = (df['wind_speed'] > 15).astype(int)
        
        if 'precipitation' in df.columns:
            df['rainy'] = (df['precipitation'] > 0.1).astype(int)
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing data per config"""
        logger.info("Handling missing values")
        
        strategy = self.config['data']['missing_strategy']
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if strategy == "indicator":
            # Add missing indicator columns
            for col in numeric_cols:
                if df[col].isna().any():
                    df[f'{col}_missing'] = df[col].isna().astype(int)
        
        # Impute numeric
        impute_method = self.config['data']['impute_numeric']
        if impute_method == "median":
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        elif impute_method == "mean":
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        elif impute_method == "zero":
            df[numeric_cols] = df[numeric_cols].fillna(0)
        
        return df
    
    def remove_leakage_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove features that contain future information"""
        logger.info("Removing leakage features")
        
        exclude_patterns = self.config['data']['exclude_features']
        cols_to_drop = []
        
        for pattern in exclude_patterns:
            if '*' in pattern:
                # Wildcard pattern
                prefix = pattern.replace('*', '')
                matching = [col for col in df.columns if col.startswith(prefix)]
                cols_to_drop.extend(matching)
            elif pattern in df.columns:
                cols_to_drop.append(pattern)
        
        if cols_to_drop:
            logger.warning(f"Dropping {len(cols_to_drop)} leakage features: {cols_to_drop}")
            df = df.drop(columns=cols_to_drop, errors='ignore')
        
        return df
    
    def build_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Execute full feature pipeline"""
        logger.info(f"Building features v{self.feature_version}")
        
        original_cols = len(df.columns)
        
        # Execute feature groups in order
        feature_groups = self.config['data']['feature_groups']
        
        if 'team_stats_rolling' in feature_groups:
            df = self.build_rolling_stats(df)
        
        if 'opponent_adjusted' in feature_groups:
            df = self.build_opponent_adjusted_features(df)
        
        if 'market_movement' in feature_groups:
            df = self.build_market_features(df)
        
        if 'contextual' in feature_groups:
            df = self.build_contextual_features(df)
        
        if 'injury_impact' in feature_groups:
            df = self.build_injury_features(df)
        
        if 'weather' in feature_groups:
            df = self.build_weather_features(df)
        
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Remove leakage
        df = self.remove_leakage_features(df)
        
        new_cols = len(df.columns)
        logger.info(f"Feature engineering complete: {original_cols} → {new_cols} columns")
        
        return df
    
    def save_features(self, df: pd.DataFrame, output_path: str):
        """Save engineered features with metadata"""
        logger.info(f"Saving features to {output_path}")
        
        # Save CSV
        df.to_csv(output_path, index=False)
        
        # Save metadata
        metadata = {
            'feature_version': self.feature_version,
            'created_at': datetime.utcnow().isoformat(),
            'num_records': len(df),
            'num_features': len(df.columns),
            'feature_columns': list(df.columns),
            'config': self.config
        }
        
        metadata_path = Path(output_path).with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved {len(df)} records with {len(df.columns)} features")
    
    @staticmethod
    def _odds_to_probability(odds: pd.Series) -> pd.Series:
        """Convert American odds to implied probability"""
        prob = np.where(
            odds > 0,
            100 / (odds + 100),
            -odds / (-odds + 100)
        )
        return pd.Series(prob, index=odds.index)


def main():
    parser = argparse.ArgumentParser(description="EQ12 Feature Engineering Pipeline")
    parser.add_argument(
        '--config',
        required=True,
        help='Path to model config YAML'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input CSV file with raw data'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output CSV file for engineered features'
    )
    
    args = parser.parse_args()
    
    # Build features
    builder = EQ12FeatureBuilder(args.config)
    df = builder.load_raw_data(args.input)
    df_features = builder.build_all_features(df)
    builder.save_features(df_features, args.output)
    
    print(f"✅ Feature engineering complete: {args.output}")


if __name__ == "__main__":
    main()
