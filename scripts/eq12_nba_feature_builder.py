#!/usr/bin/env python3
"""
EQ12 NBA Feature Engineering Pipeline
Transforms raw NBA data into optimized features for Coral TPU inference.
Handles player metrics, pace factors, rest analysis, and opponent ratings.
"""

import pandas as pd
import numpy as np
import sqlite3
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# EQ12 Cluster Configuration
EQ12_CONFIG = {
    "data_dir": "C:/EQ12/data",
    "logs_dir": "C:/EQ12/logs",
    "models_dir": "C:/EQ12/models",
    "cluster_mode": True
}

@dataclass
class PlayerFeatures:
    """NBA player feature vector optimized for TPU inference"""
    player_name: str
    team: str
    opponent: str
    game_date: str
    
    # Core performance features
    avg_points: float
    avg_rebounds: float
    avg_assists: float
    avg_threes: float
    avg_minutes: float
    
    # Advanced metrics
    usage_rate: float
    pace_factor: float
    offensive_rating: float
    defensive_rating: float
    rest_days: int
    back_to_back: bool
    
    # Opponent features
    opp_def_rating: float
    opp_pace: float
    opp_points_allowed: float
    
    # Situational features
    home_away: str  # 'H' or 'A'
    days_since_injury: int
    season_games_played: int
    
    # Line movement features
    opening_line: float
    current_line: float
    line_movement: float
    sharp_money: bool

class EQ12_NBA_FeatureBuilder:
    """NBA Feature Engineering Engine for EQ12 Cluster"""
    
    def __init__(self, config: Dict = None):
        self.config = config or EQ12_CONFIG
        self.setup_logging()
        self.connect_database()
        
    def setup_logging(self):
        """Initialize logging for feature engineering"""
        log_file = f"{self.config['logs_dir']}/nba_features_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def connect_database(self):
        """Connect to NBA cluster database"""
        db_path = f"{self.config['data_dir']}/nba_cluster.db"
        self.conn = sqlite3.connect(db_path)
        self.logger.info(" Connected to NBA cluster database")
    
    def calculate_player_averages(self, player_name: str, team: str, lookback_days: int = 30) -> Dict[str, float]:
        """Calculate rolling averages for player performance"""
        
        cutoff_date = datetime.now() - timedelta(days=lookback_days)
        
        query = '''
            SELECT points, rebounds, assists, threes, minutes_played, usage_rate
            FROM player_performance 
            WHERE player_name = ? AND team = ? AND game_date >= ?
            ORDER BY game_date DESC
        '''
        
        df = pd.read_sql_query(query, self.conn, params=[player_name, team, cutoff_date.date()])
        
        if df.empty:
            self.logger.warning(f" No recent data for {player_name}")
            return self.get_default_averages()
        
        # Calculate weighted averages (recent games weighted more heavily)
        weights = np.exp(np.linspace(-1, 0, len(df)))
        weights = weights / weights.sum()
        
        averages = {
            'avg_points': np.average(df['points'], weights=weights),
            'avg_rebounds': np.average(df['rebounds'], weights=weights),
            'avg_assists': np.average(df['assists'], weights=weights),
            'avg_threes': np.average(df['threes'], weights=weights),
            'avg_minutes': np.average(df['minutes_played'], weights=weights),
            'usage_rate': np.average(df['usage_rate'], weights=weights)
        }
        
        return averages
    
    def get_default_averages(self) -> Dict[str, float]:
        """Return default averages for new/unknown players"""
        return {
            'avg_points': 10.0,
            'avg_rebounds': 4.0,
            'avg_assists': 3.0,
            'avg_threes': 1.0,
            'avg_minutes': 25.0,
            'usage_rate': 20.0
        }
    
    def calculate_pace_factor(self, team: str, opponent: str) -> float:
        """Calculate expected game pace for team matchup"""
        
        # Get team pace averages
        query = '''
            SELECT AVG(game_pace) as team_pace
            FROM player_performance 
            WHERE team = ? AND game_date >= date('now', '-30 days')
        '''
        
        team_pace = pd.read_sql_query(query, self.conn, params=[team])
        opp_pace = pd.read_sql_query(query, self.conn, params=[opponent])
        
        team_pace_val = team_pace.iloc[0]['team_pace'] if not team_pace.empty else 100.0
        opp_pace_val = opp_pace.iloc[0]['team_pace'] if not opp_pace.empty else 100.0
        
        # Combined pace factor (average of both teams)
        combined_pace = (team_pace_val + opp_pace_val) / 2
        
        return combined_pace
    
    def calculate_rest_days(self, player_name: str, team: str, target_date: str) -> Tuple[int, bool]:
        """Calculate rest days and back-to-back status"""
        
        query = '''
            SELECT game_date
            FROM player_performance 
            WHERE player_name = ? AND team = ? AND game_date < ?
            ORDER BY game_date DESC
            LIMIT 1
        '''
        
        df = pd.read_sql_query(query, self.conn, params=[player_name, team, target_date])
        
        if df.empty:
            return 3, False  # Default: 3 days rest, not back-to-back
        
        last_game = pd.to_datetime(df.iloc[0]['game_date'])
        target = pd.to_datetime(target_date)
        
        rest_days = (target - last_game).days
        back_to_back = rest_days == 1
        
        return rest_days, back_to_back
    
    def get_opponent_ratings(self, opponent: str) -> Dict[str, float]:
        """Get opponent defensive ratings and pace"""
        
        query = '''
            SELECT 
                AVG(points) as points_allowed,
                AVG(game_pace) as pace
            FROM player_performance 
            WHERE opponent = ? AND game_date >= date('now', '-20 days')
        '''
        
        df = pd.read_sql_query(query, self.conn, params=[opponent])
        
        if df.empty:
            return {
                'opp_def_rating': 110.0,  # Average defensive rating
                'opp_pace': 100.0,
                'opp_points_allowed': 115.0
            }
        
        return {
            'opp_def_rating': 110.0 - (df.iloc[0]['points_allowed'] - 115) * 0.5,
            'opp_pace': df.iloc[0]['pace'],
            'opp_points_allowed': df.iloc[0]['points_allowed']
        }
    
    def get_line_movement_features(self, prop_id: str) -> Dict[str, float]:
        """Calculate line movement and sharp money indicators"""
        
        query = '''
            SELECT old_line, new_line, sharp_indicator
            FROM odds_movement 
            WHERE prop_id = ?
            ORDER BY movement_time DESC
            LIMIT 1
        '''
        
        df = pd.read_sql_query(query, self.conn, params=[prop_id])
        
        if df.empty:
            return {
                'opening_line': 0.0,
                'current_line': 0.0,
                'line_movement': 0.0,
                'sharp_money': False
            }
        
        movement = df.iloc[0]
        return {
            'opening_line': movement['old_line'],
            'current_line': movement['new_line'],
            'line_movement': movement['new_line'] - movement['old_line'],
            'sharp_money': bool(movement['sharp_indicator'])
        }
    
    def calculate_situational_factors(self, team: str, opponent: str, game_date: str) -> Dict[str, any]:
        """Calculate situational factors for the game"""
        
        # Determine home/away status
        query = '''
            SELECT home_team, away_team
            FROM nba_games 
            WHERE (home_team = ? OR away_team = ?) AND date(game_time) = ?
        '''
        
        df = pd.read_sql_query(query, self.conn, params=[team, team, game_date])
        
        if df.empty:
            home_away = 'H'  # Default to home
        else:
            home_away = 'H' if df.iloc[0]['home_team'] == team else 'A'
        
        return {
            'home_away': home_away,
            'days_since_injury': 0,  # Placeholder - would integrate injury data
            'season_games_played': self.get_season_games_played(team, game_date)
        }
    
    def get_season_games_played(self, team: str, game_date: str) -> int:
        """Count season games played by team"""
        
        # Assume season starts October 1
        season_start = f"{datetime.now().year}-10-01"
        
        query = '''
            SELECT COUNT(*) as games_played
            FROM player_performance 
            WHERE team = ? AND game_date >= ? AND game_date < ?
        '''
        
        df = pd.read_sql_query(query, self.conn, params=[team, season_start, game_date])
        
        return df.iloc[0]['games_played'] if not df.empty else 0
    
    def build_player_features(self, player_name: str, team: str, opponent: str, 
                            game_date: str, prop_id: str = None) -> PlayerFeatures:
        """Build complete feature vector for a player"""
        
        self.logger.info(f" Building features for {player_name} ({team} vs {opponent})")
        
        # Get player performance averages
        averages = self.calculate_player_averages(player_name, team)
        
        # Calculate rest and conditioning
        rest_days, back_to_back = self.calculate_rest_days(player_name, team, game_date)
        
        # Get opponent factors
        opp_ratings = self.get_opponent_ratings(opponent)
        
        # Calculate pace factor
        pace_factor = self.calculate_pace_factor(team, opponent)
        
        # Get situational factors
        situational = self.calculate_situational_factors(team, opponent, game_date)
        
        # Get line movement (if prop_id provided)
        line_features = self.get_line_movement_features(prop_id) if prop_id else {
            'opening_line': 0.0, 'current_line': 0.0, 'line_movement': 0.0, 'sharp_money': False
        }
        
        # Build feature object
        features = PlayerFeatures(
            player_name=player_name,
            team=team,
            opponent=opponent,
            game_date=game_date,
            
            # Performance averages
            avg_points=averages['avg_points'],
            avg_rebounds=averages['avg_rebounds'],
            avg_assists=averages['avg_assists'],
            avg_threes=averages['avg_threes'],
            avg_minutes=averages['avg_minutes'],
            
            # Advanced metrics
            usage_rate=averages['usage_rate'],
            pace_factor=pace_factor,
            offensive_rating=110.0,  # Placeholder
            defensive_rating=105.0,  # Placeholder
            rest_days=rest_days,
            back_to_back=back_to_back,
            
            # Opponent factors
            opp_def_rating=opp_ratings['opp_def_rating'],
            opp_pace=opp_ratings['opp_pace'],
            opp_points_allowed=opp_ratings['opp_points_allowed'],
            
            # Situational
            home_away=situational['home_away'],
            days_since_injury=situational['days_since_injury'],
            season_games_played=situational['season_games_played'],
            
            # Line movement
            opening_line=line_features['opening_line'],
            current_line=line_features['current_line'],
            line_movement=line_features['line_movement'],
            sharp_money=line_features['sharp_money']
        )
        
        return features
    
    def features_to_tensor(self, features: PlayerFeatures) -> np.ndarray:
        """Convert PlayerFeatures to numpy array for TPU inference"""
        
        # Normalize categorical variables
        home_away_numeric = 1.0 if features.home_away == 'H' else 0.0
        back_to_back_numeric = 1.0 if features.back_to_back else 0.0
        sharp_money_numeric = 1.0 if features.sharp_money else 0.0
        
        # Create feature vector (order matters for TPU model)
        tensor = np.array([
            # Core performance (normalized)
            features.avg_points / 30.0,
            features.avg_rebounds / 15.0,
            features.avg_assists / 12.0,
            features.avg_threes / 5.0,
            features.avg_minutes / 48.0,
            
            # Advanced metrics (normalized)
            features.usage_rate / 35.0,
            features.pace_factor / 120.0,
            features.offensive_rating / 130.0,
            features.defensive_rating / 120.0,
            min(features.rest_days, 5) / 5.0,
            back_to_back_numeric,
            
            # Opponent factors (normalized)
            features.opp_def_rating / 120.0,
            features.opp_pace / 120.0,
            features.opp_points_allowed / 130.0,
            
            # Situational factors
            home_away_numeric,
            min(features.days_since_injury, 30) / 30.0,
            min(features.season_games_played, 82) / 82.0,
            
            # Line movement features
            np.tanh(features.line_movement),  # Bounded between -1 and 1
            sharp_money_numeric
        ], dtype=np.float32)
        
        return tensor
    
    def build_game_features_batch(self, game_date: str) -> List[Tuple[PlayerFeatures, np.ndarray]]:
        """Build features for all props on a given date"""
        
        query = '''
            SELECT DISTINCT player_name, team, prop_id
            FROM player_props pp
            JOIN nba_games ng ON pp.game_id = ng.game_id
            WHERE date(ng.game_time) = ?
        '''
        
        df = pd.read_sql_query(query, self.conn, params=[game_date])
        
        if df.empty:
            self.logger.warning(f" No props found for {game_date}")
            return []
        
        features_batch = []
        
        for _, row in df.iterrows():
            # Get opponent for this game
            opponent_query = '''
                SELECT CASE 
                    WHEN ng.home_team = ? THEN ng.away_team
                    ELSE ng.home_team
                END as opponent
                FROM player_props pp
                JOIN nba_games ng ON pp.game_id = ng.game_id
                WHERE pp.prop_id = ?
            '''
            
            opp_df = pd.read_sql_query(opponent_query, self.conn, 
                                     params=[row['team'], row['prop_id']])
            
            if opp_df.empty:
                continue
                
            opponent = opp_df.iloc[0]['opponent']
            
            # Build features
            features = self.build_player_features(
                row['player_name'], row['team'], opponent, 
                game_date, row['prop_id']
            )
            
            # Convert to tensor
            tensor = self.features_to_tensor(features)
            
            features_batch.append((features, tensor))
        
        self.logger.info(f" Built {len(features_batch)} feature sets for {game_date}")
        return features_batch
    
    def export_features_for_tpu(self, game_date: str) -> str:
        """Export features in TPU-optimized format"""
        
        features_batch = self.build_game_features_batch(game_date)
        
        if not features_batch:
            self.logger.warning(f" No features to export for {game_date}")
            return ""
        
        # Prepare export data
        export_data = {
            'game_date': game_date,
            'feature_count': len(features_batch),
            'feature_vectors': [],
            'player_metadata': [],
            'tensor_shape': [len(features_batch), 19],  # 19 features per player
            'export_timestamp': datetime.utcnow().isoformat()
        }
        
        # Convert to arrays for TPU processing
        feature_matrix = np.zeros((len(features_batch), 19), dtype=np.float32)
        
        for i, (features, tensor) in enumerate(features_batch):
            feature_matrix[i] = tensor
            
            export_data['player_metadata'].append({
                'index': i,
                'player_name': features.player_name,
                'team': features.team,
                'opponent': features.opponent,
                'prop_line': features.current_line,
                'sharp_money': features.sharp_money
            })
        
        # Save feature matrix for TPU
        feature_file = f"{self.config['data_dir']}/nba_features_{game_date.replace('-', '')}.npy"
        np.save(feature_file, feature_matrix)
        
        # Save metadata
        metadata_file = f"{self.config['data_dir']}/nba_features_meta_{game_date.replace('-', '')}.json"
        with open(metadata_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f" Features exported for TPU: {feature_file}")
        self.logger.info(f" Metadata saved: {metadata_file}")
        
        return feature_file
    
    def validate_features(self, features: PlayerFeatures) -> bool:
        """Validate feature vector for quality"""
        
        # Check for reasonable ranges
        if not (0 <= features.avg_points <= 50):
            return False
        if not (0 <= features.avg_rebounds <= 20):
            return False
        if not (0 <= features.avg_assists <= 15):
            return False
        if not (0 <= features.usage_rate <= 40):
            return False
        if not (80 <= features.pace_factor <= 120):
            return False
        
        return True
    
    def feature_importance_analysis(self, game_date: str) -> Dict[str, float]:
        """Analyze feature importance for given date"""
        
        features_batch = self.build_game_features_batch(game_date)
        
        if len(features_batch) < 10:
            self.logger.warning(" Insufficient data for feature importance analysis")
            return {}
        
        # Extract feature matrix
        feature_matrix = np.array([tensor for _, tensor in features_batch])
        
        # Calculate feature statistics
        feature_names = [
            'avg_points', 'avg_rebounds', 'avg_assists', 'avg_threes', 'avg_minutes',
            'usage_rate', 'pace_factor', 'offensive_rating', 'defensive_rating', 
            'rest_days', 'back_to_back', 'opp_def_rating', 'opp_pace', 
            'opp_points_allowed', 'home_away', 'days_since_injury', 
            'season_games_played', 'line_movement', 'sharp_money'
        ]
        
        importance = {}
        for i, name in enumerate(feature_names):
            importance[name] = {
                'mean': float(np.mean(feature_matrix[:, i])),
                'std': float(np.std(feature_matrix[:, i])),
                'variance': float(np.var(feature_matrix[:, i]))
            }
        
        return importance

def main():
    parser = argparse.ArgumentParser(description="EQ12 NBA Feature Engineering Pipeline")
    parser.add_argument('--date', type=str, default=datetime.now().strftime('%Y-%m-%d'),
                       help='Game date to process (YYYY-MM-DD)')
    parser.add_argument('--player', type=str, help='Specific player to analyze')
    parser.add_argument('--team', type=str, help='Team for player analysis')
    parser.add_argument('--opponent', type=str, help='Opponent for analysis')
    parser.add_argument('--export-tpu', action='store_true',
                       help='Export features for TPU processing')
    parser.add_argument('--importance', action='store_true',
                       help='Run feature importance analysis')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    builder = EQ12_NBA_FeatureBuilder()
    
    try:
        if args.player and args.team and args.opponent:
            # Single player analysis
            features = builder.build_player_features(args.player, args.team, args.opponent, args.date)
            tensor = builder.features_to_tensor(features)
            
            print(f" Features for {args.player}:")
            print(f"   Points avg: {features.avg_points:.1f}")
            print(f"   Usage rate: {features.usage_rate:.1f}%")
            print(f"   Rest days: {features.rest_days}")
            print(f"   Pace factor: {features.pace_factor:.1f}")
            print(f"   Feature tensor shape: {tensor.shape}")
            
        elif args.export_tpu:
            # Export for TPU processing
            feature_file = builder.export_features_for_tpu(args.date)
            if feature_file:
                print(f" TPU features exported: {feature_file}")
            
        elif args.importance:
            # Feature importance analysis
            importance = builder.feature_importance_analysis(args.date)
            print(f" Feature importance analysis for {args.date}:")
            for feature, stats in importance.items():
                print(f"   {feature:20s}: mean={stats['mean']:.3f}, std={stats['std']:.3f}")
        
        else:
            # Batch processing for date
            features_batch = builder.build_game_features_batch(args.date)
            print(f" Processed {len(features_batch)} player features for {args.date}")
            
    except Exception as e:
        print(f" Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())