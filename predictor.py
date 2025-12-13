#!/usr/bin/env python3
"""
EQ12 Predictor - Godlike Betting ML Engine
Machine learning predictor with edge detection and Kelly criterion stake calculations
Builds models for value betting across all sports with proper bankroll management
"""

import asyncio
import json
import logging
import pickle
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import xgboost as xgb
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

# Add EQ12 to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
load_dotenv()

# Configure logging
log_dir = Path("C:/EQ12/logs")
log_dir.mkdir(exist_ok=True)
data_dir = Path("C:/EQ12/data")
data_dir.mkdir(exist_ok=True)
reports_dir = Path("C:/EQ12/reports")
reports_dir.mkdir(exist_ok=True)
models_dir = Path("C:/EQ12/models")
models_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'predictor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("EQ12.Predictor")

class EQ12Predictor:
    """ML predictor with edge detection and Kelly criterion betting"""
    
    def __init__(self, model_type: str = "logistic", bankroll: float = 1000.0):
        self.model_type = model_type
        self.bankroll = bankroll
        self.models = {}
        self.scalers = {}
        self.feature_cols = {}
        
        # Model parameters
        self.model_params = {
            'logistic': {'random_state': 42, 'max_iter': 1000},
            'rf': {'n_estimators': 100, 'random_state': 42, 'max_depth': 10},
            'xgboost': {'objective': 'binary:logistic', 'random_state': 42, 'max_depth': 6}
        }
        
        logger.info(f"🎯 Predictor initialized - Model: {model_type}, Bankroll: ${bankroll:,.0f}")
    
    def american_to_decimal(self, american_odds: float) -> float:
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def american_to_probability(self, american_odds: float) -> float:
        """Convert American odds to implied probability"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    def calculate_kelly_fraction(self, win_prob: float, odds: float, max_fraction: float = 0.10) -> float:
        """Calculate Kelly criterion fraction with max bet limit"""
        if pd.isna(win_prob) or pd.isna(odds):
            return 0.0
        
        decimal_odds = self.american_to_decimal(odds)
        
        # Kelly formula: f = (bp - q) / b
        # where b = decimal odds - 1, p = win probability, q = 1 - p
        b = decimal_odds - 1
        p = win_prob
        q = 1 - p
        
        if b <= 0 or p <= 0:
            return 0.0
        
        kelly_fraction = (b * p - q) / b
        
        # Cap at maximum fraction to avoid over-betting
        kelly_fraction = max(0, min(kelly_fraction, max_fraction))
        
        return kelly_fraction
    
    def calculate_expected_value(self, win_prob: float, odds: float) -> float:
        """Calculate expected value of a bet"""
        if pd.isna(win_prob) or pd.isna(odds):
            return 0.0
        
        decimal_odds = self.american_to_decimal(odds)
        implied_prob = self.american_to_probability(odds)
        
        # EV = (win_prob * payout) - (lose_prob * stake)
        # For $1 bet: EV = (win_prob * decimal_odds) - 1
        expected_value = (win_prob * decimal_odds) - 1
        
        return expected_value
    
    def calculate_edge(self, win_prob: float, odds: float) -> float:
        """Calculate betting edge as percentage"""
        if pd.isna(win_prob) or pd.isna(odds):
            return 0.0
        
        implied_prob = self.american_to_probability(odds)
        edge = (win_prob - implied_prob) / implied_prob * 100
        
        return edge
    
    def build_features(self, schedule_df: pd.DataFrame, stats_df: pd.DataFrame) -> pd.DataFrame:
        """Build ML features from schedule and stats data"""
        logger.info("🔧 Building ML features...")
        
        if schedule_df.empty or stats_df.empty:
            logger.warning("⚠️ Empty input data for feature building")
            return pd.DataFrame()
        
        # Merge schedule with team stats
        # Home team stats
        home_stats = stats_df.copy()
        home_stats.columns = ['home_' + col if col not in ['team', 'league'] else col for col in home_stats.columns]
        home_stats = home_stats.rename(columns={'team': 'home_team'})
        
        # Away team stats  
        away_stats = stats_df.copy()
        away_stats.columns = ['away_' + col if col not in ['team', 'league'] else col for col in away_stats.columns]
        away_stats = away_stats.rename(columns={'team': 'away_team'})
        
        # Merge with schedule
        features_df = schedule_df.merge(home_stats, on=['league', 'home_team'], how='left')
        features_df = features_df.merge(away_stats[away_stats.columns[away_stats.columns != 'league']], 
                                      on='away_team', how='left')
        
        # Create differential features by league
        for league in features_df['league'].unique():
            league_mask = features_df['league'] == league
            
            if league == 'NBA':
                features_df.loc[league_mask, 'home_offensive_advantage'] = (
                    features_df.loc[league_mask, 'home_offensive_rating'] - 
                    features_df.loc[league_mask, 'away_defensive_rating']
                )
                features_df.loc[league_mask, 'away_offensive_advantage'] = (
                    features_df.loc[league_mask, 'away_offensive_rating'] - 
                    features_df.loc[league_mask, 'home_defensive_rating']
                )
                
            elif league == 'MLB':
                features_df.loc[league_mask, 'home_run_advantage'] = (
                    features_df.loc[league_mask, 'home_avg_runs'] - 
                    features_df.loc[league_mask, 'away_avg_runs_allowed']
                )
                features_df.loc[league_mask, 'away_run_advantage'] = (
                    features_df.loc[league_mask, 'away_avg_runs'] - 
                    features_df.loc[league_mask, 'home_avg_runs_allowed']
                )
                
            elif league in ['NFL', 'CFB']:
                features_df.loc[league_mask, 'home_point_advantage'] = (
                    features_df.loc[league_mask, 'home_avg_points'] - 
                    features_df.loc[league_mask, 'away_avg_points_allowed']
                )
                features_df.loc[league_mask, 'away_point_advantage'] = (
                    features_df.loc[league_mask, 'away_avg_points'] - 
                    features_df.loc[league_mask, 'home_avg_points_allowed']
                )
                
            elif league == 'NHL':
                features_df.loc[league_mask, 'home_goal_advantage'] = (
                    features_df.loc[league_mask, 'home_avg_goals'] - 
                    features_df.loc[league_mask, 'away_avg_goals_allowed']
                )
                features_df.loc[league_mask, 'away_goal_advantage'] = (
                    features_df.loc[league_mask, 'away_avg_goals'] - 
                    features_df.loc[league_mask, 'home_avg_goals_allowed']
                )
        
        # Form strength differential
        if 'home_form_strength' in features_df.columns and 'away_form_strength' in features_df.columns:
            features_df['form_differential'] = (
                features_df['home_form_strength'] - features_df['away_form_strength']
            )
        
        # Home field advantage (generic boost)
        features_df['home_field_advantage'] = 0.55  # Slight home advantage across sports
        
        # Rest days (if available in schedule data)
        if 'start_time' in features_df.columns:
            features_df['start_time_dt'] = pd.to_datetime(features_df['start_time'])
            features_df['days_until_game'] = (
                features_df['start_time_dt'] - datetime.now()
            ).dt.total_seconds() / (24 * 3600)
        
        logger.info(f"✅ Built {len(features_df)} feature rows with {len(features_df.columns)} columns")
        
        return features_df
    
    def prepare_training_data(self, features_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
        """Prepare training data with synthetic outcomes for demonstration"""
        logger.info("🎲 Preparing training data...")
        
        if features_df.empty:
            return pd.DataFrame(), pd.Series()
        
        # For demonstration, create synthetic historical outcomes
        # In production, this would use real historical game results
        np.random.seed(42)
        
        synthetic_outcomes = []
        for _, row in features_df.iterrows():
            # Create realistic win probabilities based on features
            base_prob = 0.5  # Start with 50/50
            
            # Adjust for home advantage
            if 'home_field_advantage' in row:
                base_prob += 0.05  # Home teams win ~55% of the time
            
            # Adjust for form differential
            if 'form_differential' in row and pd.notna(row['form_differential']):
                base_prob += row['form_differential'] * 0.1
            
            # Adjust for league-specific advantages
            league = row.get('league', '')
            if league == 'NBA' and 'home_offensive_advantage' in row:
                if pd.notna(row['home_offensive_advantage']):
                    base_prob += np.tanh(row['home_offensive_advantage'] / 10) * 0.1
            elif league == 'MLB' and 'home_run_advantage' in row:
                if pd.notna(row['home_run_advantage']):
                    base_prob += np.tanh(row['home_run_advantage'] / 2) * 0.1
            elif league in ['NFL', 'CFB'] and 'home_point_advantage' in row:
                if pd.notna(row['home_point_advantage']):
                    base_prob += np.tanh(row['home_point_advantage'] / 7) * 0.1
            elif league == 'NHL' and 'home_goal_advantage' in row:
                if pd.notna(row['home_goal_advantage']):
                    base_prob += np.tanh(row['home_goal_advantage'] / 1) * 0.1
            
            # Clamp probability between 0.1 and 0.9
            base_prob = max(0.1, min(0.9, base_prob))
            
            # Generate outcome based on probability
            outcome = 1 if np.random.random() < base_prob else 0
            synthetic_outcomes.append(outcome)
        
        # Create expanded training set by duplicating with noise
        training_size = min(1000, len(features_df) * 5)  # Target 1000 samples or 5x current
        expanded_features = []
        expanded_outcomes = []
        
        for i in range(training_size):
            base_idx = i % len(features_df)
            row = features_df.iloc[base_idx].copy()
            outcome = synthetic_outcomes[base_idx]
            
            # Add small amount of noise to numerical features
            for col in row.index:
                if pd.api.types.is_numeric_dtype(type(row[col])) and pd.notna(row[col]):
                    if col not in ['league', 'home_team', 'away_team', 'game_id']:
                        noise = np.random.normal(0, abs(row[col]) * 0.05)  # 5% noise
                        row[col] += noise
            
            expanded_features.append(row)
            expanded_outcomes.append(outcome)
        
        training_df = pd.DataFrame(expanded_features)
        training_outcomes = pd.Series(expanded_outcomes)
        
        logger.info(f"✅ Created training set: {len(training_df)} samples")
        
        return training_df, training_outcomes
    
    def select_features(self, df: pd.DataFrame, league: str) -> list[str]:
        """Select relevant features for a specific league"""
        base_features = [
            'home_field_advantage', 'form_differential', 'days_until_game'
        ]
        
        league_features = {
            'NBA': [
                'home_offensive_advantage', 'away_offensive_advantage',
                'home_avg_points', 'away_avg_points',
                'home_form_strength', 'away_form_strength'
            ],
            'MLB': [
                'home_run_advantage', 'away_run_advantage',
                'home_avg_runs', 'away_avg_runs',
                'home_batting_avg', 'away_batting_avg',
                'home_era', 'away_era'
            ],
            'NFL': [
                'home_point_advantage', 'away_point_advantage',
                'home_avg_points', 'away_avg_points',
                'home_turnover_differential', 'away_turnover_differential'
            ],
            'CFB': [
                'home_point_advantage', 'away_point_advantage',
                'home_avg_points', 'away_avg_points'
            ],
            'NHL': [
                'home_goal_advantage', 'away_goal_advantage',
                'home_avg_goals', 'away_avg_goals',
                'home_power_play_percentage', 'away_power_play_percentage'
            ],
            'Soccer': [
                'home_avg_goals', 'away_avg_goals',
                'home_expected_goals', 'away_expected_goals',
                'home_possession_percentage', 'away_possession_percentage'
            ]
        }
        
        # Combine base features with league-specific features
        features = base_features + league_features.get(league, [])
        
        # Filter to only include features that exist in the DataFrame
        available_features = [f for f in features if f in df.columns]
        
        return available_features
    
    def train_model(self, features_df: pd.DataFrame, save_model: bool = True) -> dict[str, Any]:
        """Train ML models for each league"""
        logger.info(f"🚀 Training {self.model_type} models...")
        
        # Prepare training data
        training_df, outcomes = self.prepare_training_data(features_df)
        
        if training_df.empty:
            logger.error("❌ No training data available")
            return {}
        
        results = {}
        
        # Train separate models for each league
        for league in training_df['league'].unique():
            logger.info(f"Training model for {league}...")
            
            league_data = training_df[training_df['league'] == league]
            league_outcomes = outcomes[training_df['league'] == league]
            
            if len(league_data) < 20:
                logger.warning(f"⚠️ Insufficient data for {league} ({len(league_data)} samples)")
                continue
            
            # Select features for this league
            feature_cols = self.select_features(league_data, league)
            
            if not feature_cols:
                logger.warning(f"⚠️ No features available for {league}")
                continue
            
            # Prepare feature matrix
            X = league_data[feature_cols].fillna(0)
            y = league_outcomes
            
            # Split train/validation
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_val_scaled = scaler.transform(X_val)
            
            # Train model
            if self.model_type == 'logistic':
                model = LogisticRegression(**self.model_params['logistic'])
            elif self.model_type == 'rf':
                model = RandomForestClassifier(**self.model_params['rf'])
            elif self.model_type == 'xgboost':
                model = xgb.XGBClassifier(**self.model_params['xgboost'])
            else:
                model = LogisticRegression(**self.model_params['logistic'])
            
            model.fit(X_train_scaled, y_train)
            
            # Validate model
            train_pred = model.predict(X_train_scaled)
            val_pred = model.predict(X_val_scaled)
            train_proba = model.predict_proba(X_train_scaled)[:, 1]
            val_proba = model.predict_proba(X_val_scaled)[:, 1]
            
            # Calculate metrics
            train_accuracy = accuracy_score(y_train, train_pred)
            val_accuracy = accuracy_score(y_val, val_pred)
            val_logloss = log_loss(y_val, val_proba)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='accuracy')
            
            # Store model and results
            self.models[league] = model
            self.scalers[league] = scaler
            self.feature_cols[league] = feature_cols
            
            results[league] = {
                'train_accuracy': train_accuracy,
                'val_accuracy': val_accuracy,
                'val_logloss': val_logloss,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'feature_count': len(feature_cols),
                'training_samples': len(X_train)
            }
            
            logger.info(f"✅ {league} model - Val Accuracy: {val_accuracy:.3f}, CV: {cv_scores.mean():.3f}±{cv_scores.std():.3f}")
        
        # Save models
        if save_model and self.models:
            self.save_models()
        
        return results
    
    def predict(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """Make predictions on new data"""
        logger.info("🔮 Making predictions...")
        
        if features_df.empty:
            logger.warning("⚠️ No data to predict on")
            return pd.DataFrame()
        
        predictions = []
        
        for league in features_df['league'].unique():
            if league not in self.models:
                logger.warning(f"⚠️ No model available for {league}")
                continue
            
            league_data = features_df[features_df['league'] == league]
            feature_cols = self.feature_cols[league]
            
            # Prepare features
            X = league_data[feature_cols].fillna(0)
            X_scaled = self.scalers[league].transform(X)
            
            # Make predictions
            probabilities = self.models[league].predict_proba(X_scaled)[:, 1]
            
            # Add predictions to league data
            league_predictions = league_data.copy()
            league_predictions['home_win_prob'] = probabilities
            league_predictions['away_win_prob'] = 1 - probabilities
            
            predictions.append(league_predictions)
        
        if not predictions:
            logger.warning("⚠️ No predictions generated")
            return pd.DataFrame()
        
        predictions_df = pd.concat(predictions, ignore_index=True)
        
        logger.info(f"✅ Generated predictions for {len(predictions_df)} games")
        
        return predictions_df
    
    def calculate_betting_metrics(self, predictions_df: pd.DataFrame, odds_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate betting metrics including edge and Kelly sizing"""
        logger.info("💰 Calculating betting metrics...")
        
        if predictions_df.empty or odds_df.empty:
            logger.warning("⚠️ Empty predictions or odds data")
            return pd.DataFrame()
        
        # Merge predictions with odds (moneyline only for now)
        moneyline_odds = odds_df[odds_df['market'] == 'moneyline'].copy()
        
        if moneyline_odds.empty:
            logger.warning("⚠️ No moneyline odds found")
            return pd.DataFrame()
        
        # Create betting opportunities
        betting_opportunities = []
        
        for _, pred_row in predictions_df.iterrows():
            game_id = pred_row.get('game_id')
            home_team = pred_row.get('home_team')
            away_team = pred_row.get('away_team')
            home_win_prob = pred_row.get('home_win_prob', 0)
            away_win_prob = pred_row.get('away_win_prob', 0)
            
            # Find odds for this game
            game_odds = moneyline_odds[
                (moneyline_odds['home_team'].str.lower() == home_team.lower()) &
                (moneyline_odds['away_team'].str.lower() == away_team.lower())
            ]
            
            if game_odds.empty:
                continue
            
            # Process each bookmaker's odds
            for _, odds_row in game_odds.iterrows():
                team = odds_row.get('team', '')
                odds = odds_row.get('odds', 0)
                bookmaker = odds_row.get('bookmaker', '')
                
                if pd.isna(odds) or odds == 0:
                    continue
                
                # Determine which team and probability to use
                if team.lower() == home_team.lower():
                    win_prob = home_win_prob
                    bet_team = 'home'
                    bet_team_name = home_team
                elif team.lower() == away_team.lower():
                    win_prob = away_win_prob
                    bet_team = 'away'
                    bet_team_name = away_team
                else:
                    continue
                
                # Calculate betting metrics
                expected_value = self.calculate_expected_value(win_prob, odds)
                edge = self.calculate_edge(win_prob, odds)
                kelly_fraction = self.calculate_kelly_fraction(win_prob, odds)
                kelly_stake = kelly_fraction * self.bankroll
                
                betting_opportunities.append({
                    'game_id': game_id,
                    'league': pred_row.get('league'),
                    'home_team': home_team,
                    'away_team': away_team,
                    'start_time': pred_row.get('start_time'),
                    'bookmaker': bookmaker,
                    'bet_team': bet_team,
                    'bet_team_name': bet_team_name,
                    'odds': odds,
                    'model_prob': win_prob,
                    'implied_prob': self.american_to_probability(odds),
                    'expected_value': expected_value,
                    'edge_percent': edge,
                    'kelly_fraction': kelly_fraction,
                    'kelly_stake': kelly_stake,
                    'profit_potential': kelly_stake * (self.american_to_decimal(odds) - 1)
                })
        
        if not betting_opportunities:
            logger.warning("⚠️ No betting opportunities found")
            return pd.DataFrame()
        
        betting_df = pd.DataFrame(betting_opportunities)
        
        # Filter for positive edge bets
        positive_edge = betting_df[betting_df['edge_percent'] > 0]
        
        logger.info(f"✅ Found {len(positive_edge)} positive edge opportunities out of {len(betting_df)} total bets")
        
        return betting_df
    
    def find_value_bets(self, betting_df: pd.DataFrame, min_edge: float = 5.0, min_stake: float = 10.0) -> pd.DataFrame:
        """Filter for value bets based on edge and minimum stake"""
        if betting_df.empty:
            return pd.DataFrame()
        
        value_bets = betting_df[
            (betting_df['edge_percent'] >= min_edge) &
            (betting_df['kelly_stake'] >= min_stake)
        ].copy()
        
        # Sort by edge percentage descending
        value_bets = value_bets.sort_values('edge_percent', ascending=False)
        
        logger.info(f"🎯 Found {len(value_bets)} value bets with edge >= {min_edge}% and stake >= ${min_stake}")
        
        return value_bets
    
    def save_models(self):
        """Save trained models to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        for league, model in self.models.items():
            model_path = models_dir / f"{league.lower()}_{self.model_type}_model_{timestamp}.pkl"
            scaler_path = models_dir / f"{league.lower()}_{self.model_type}_scaler_{timestamp}.pkl"
            
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scalers[league], f)
        
        # Save feature columns and metadata
        metadata = {
            'model_type': self.model_type,
            'feature_cols': self.feature_cols,
            'bankroll': self.bankroll,
            'timestamp': datetime.now().isoformat()
        }
        
        metadata_path = models_dir / f"model_metadata_{timestamp}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"💾 Saved {len(self.models)} models to {models_dir}")
    
    def load_models(self, model_timestamp: str):
        """Load models from disk"""
        # Load metadata first
        metadata_path = models_dir / f"model_metadata_{model_timestamp}.json"
        
        if not metadata_path.exists():
            logger.error(f"❌ Model metadata not found: {metadata_path}")
            return False
        
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        self.feature_cols = metadata['feature_cols']
        self.bankroll = metadata.get('bankroll', self.bankroll)
        
        # Load models and scalers
        for league in self.feature_cols.keys():
            model_path = models_dir / f"{league.lower()}_{self.model_type}_model_{model_timestamp}.pkl"
            scaler_path = models_dir / f"{league.lower()}_{self.model_type}_scaler_{model_timestamp}.pkl"
            
            if model_path.exists() and scaler_path.exists():
                with open(model_path, 'rb') as f:
                    self.models[league] = pickle.load(f)
                
                with open(scaler_path, 'rb') as f:
                    self.scalers[league] = pickle.load(f)
            else:
                logger.warning(f"⚠️ Model files not found for {league}")
        
        logger.info(f"📁 Loaded {len(self.models)} models from {model_timestamp}")
        return True

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Godlike Predictor")
    parser.add_argument("--schedule-odds", help="Path to schedule+odds CSV file")
    parser.add_argument("--stats", help="Path to stats CSV/parquet file")
    parser.add_argument("--model", choices=['logistic', 'rf', 'xgboost'], default='logistic', help="Model type")
    parser.add_argument("--bankroll", type=float, default=1000.0, help="Bankroll amount")
    parser.add_argument("--train", action="store_true", help="Train new models")
    parser.add_argument("--save-model", action="store_true", help="Save trained models")
    parser.add_argument("--load-model", help="Load models from timestamp")
    parser.add_argument("--min-edge", type=float, default=5.0, help="Minimum edge percentage")
    parser.add_argument("--simulate", action="store_true", help="Dry run without saving")
    
    args = parser.parse_args()
    
    try:
        predictor = EQ12Predictor(model_type=args.model, bankroll=args.bankroll)
        
        # Load existing models if specified
        if args.load_model and not args.train:
            if not predictor.load_models(args.load_model):
                logger.error("❌ Failed to load models")
                return None
        
        # Load input data
        if not args.schedule_odds or not args.stats:
            logger.error("❌ Must provide --schedule-odds and --stats files")
            return None
        
        schedule_odds_df = pd.read_csv(args.schedule_odds)
        
        if args.stats.endswith('.parquet'):
            stats_df = pd.read_parquet(args.stats)
        else:
            stats_df = pd.read_csv(args.stats)
        
        # Build features
        features_df = predictor.build_features(schedule_odds_df, stats_df)
        
        if features_df.empty:
            logger.error("❌ Failed to build features")
            return None
        
        # Train models if requested
        training_results = {}
        if args.train:
            training_results = predictor.train_model(features_df, save_model=args.save_model)
        
        # Make predictions
        predictions_df = predictor.predict(features_df)
        
        if predictions_df.empty:
            logger.error("❌ No predictions generated")
            return None
        
        # Calculate betting metrics
        betting_df = predictor.calculate_betting_metrics(predictions_df, schedule_odds_df)
        
        # Find value bets
        value_bets_df = predictor.find_value_bets(betting_df, min_edge=args.min_edge)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        if not args.simulate:
            predictions_path = reports_dir / f"predictions_{timestamp}.csv"
            predictions_df.to_csv(predictions_path, index=False)
            
            if not betting_df.empty:
                betting_path = reports_dir / f"betting_opportunities_{timestamp}.csv"
                betting_df.to_csv(betting_path, index=False)
            
            if not value_bets_df.empty:
                value_path = reports_dir / f"value_bets_{timestamp}.csv"
                value_bets_df.to_csv(value_path, index=False)
        
        # Print summary
        logger.info("📊 PREDICTION SUMMARY")
        logger.info("=" * 50)
        
        if training_results:
            for league, metrics in training_results.items():
                logger.info(f"{league}: Accuracy {metrics['val_accuracy']:.3f}, Features {metrics['feature_count']}")
        
        logger.info(f"🎯 Predictions: {len(predictions_df)} games")
        logger.info(f"💰 Betting opportunities: {len(betting_df)}")
        logger.info(f"🔥 Value bets (edge >= {args.min_edge}%): {len(value_bets_df)}")
        
        if not value_bets_df.empty:
            total_stake = value_bets_df['kelly_stake'].sum()
            total_profit_potential = value_bets_df['profit_potential'].sum()
            avg_edge = value_bets_df['edge_percent'].mean()
            
            logger.info(f"💵 Total recommended stake: ${total_stake:.0f}")
            logger.info(f"🎯 Potential profit: ${total_profit_potential:.0f}")
            logger.info(f"📈 Average edge: {avg_edge:.1f}%")
            
            logger.info("\n🏆 TOP VALUE BETS:")
            for _, bet in value_bets_df.head(5).iterrows():
                logger.info(f"  {bet['league']}: {bet['bet_team_name']} ({bet['odds']:+d}) - Edge: {bet['edge_percent']:.1f}%, Stake: ${bet['kelly_stake']:.0f}")
        
        logger.info("✅ EQ12 Predictor completed successfully!")
        return predictions_path if not args.simulate else None
        
    except Exception as e:
        logger.error(f"❌ Predictor failed: {e}")
        raise

if __name__ == "__main__":
    # Handle event loop for Windows
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
    except:
        pass
    
    asyncio.run(main())