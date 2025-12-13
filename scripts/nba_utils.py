"""
EQ12 NBA Analysis Utilities
============================

Shared helper functions for NBA data fetching, plotting, model evaluation,
logging, and alert systems. Designed for integration with JupyterLab notebooks.

Created: 2025-11-27
Repository: C:\EQ12_BROKEN_20251122_210342
"""

import os
import sys
import logging
import json
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Data Analysis
import pandas as pd
import numpy as np
from scipy import stats

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# NBA Stats (official API)
try:
    from nba_api.stats.endpoints import leaguegamefinder, teamgamelog, playergamelog
    from nba_api.stats.static import teams, players
    NBA_API_AVAILABLE = True
except ImportError:
    NBA_API_AVAILABLE = False
    logging.warning("nba_api not installed. Install with: pip install nba-api")

# Machine Learning
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score, roc_auc_score
)
from sklearn.model_selection import cross_val_score, train_test_split


# ============================================================================
# CONFIGURATION & ENVIRONMENT
# ============================================================================

def load_env_config() -> Dict[str, Optional[str]]:
    """Load environment variables for API keys and tokens."""
    from dotenv import load_dotenv
    
    env_path = Path("C:/EQ12/.env")
    if env_path.exists():
        load_dotenv(env_path)
    
    return {
        "odds_api_key": os.getenv("ODDS_API_KEY"),
        "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID"),
        "discord_webhook_url": os.getenv("DISCORD_WEBHOOK_URL"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
    }


def setup_logging(log_file: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Configure structured logging for NBA analysis.
    
    Args:
        log_file: Optional path to log file (default: C:/EQ12/logs/nba_analysis_YYYYMMDD_HHMMSS.log)
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    if log_file is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        log_dir = Path("C:/EQ12/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"nba_analysis_{timestamp}.log"
    
    logger = logging.getLogger("EQ12_NBA")
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(funcName)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    return logger


# ============================================================================
# DATA FETCHERS
# ============================================================================

def fetch_nba_odds(sport: str = "basketball_nba", api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch NBA odds from The Odds API.
    
    Args:
        sport: Sport key (default: basketball_nba)
        api_key: OddsAPI key (reads from env if None)
    
    Returns:
        JSON response with odds data
    """
    if api_key is None:
        config = load_env_config()
        api_key = config["odds_api_key"]
    
    if not api_key or api_key == "REPLACE_ME":
        raise ValueError("ODDS_API_KEY not configured in .env")
    
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": api_key,
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "american"
    }
    
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    
    return response.json()


def fetch_nba_teams() -> pd.DataFrame:
    """
    Fetch NBA team information.
    
    Returns:
        DataFrame with team details (id, abbreviation, city, name, etc.)
    """
    if not NBA_API_AVAILABLE:
        raise ImportError("nba_api not installed. Run: pip install nba-api")
    
    team_list = teams.get_teams()
    return pd.DataFrame(team_list)


def fetch_nba_games(team_abbr: str, season: str = "2024-25") -> pd.DataFrame:
    """
    Fetch game logs for a specific NBA team.
    
    Args:
        team_abbr: Team abbreviation (e.g., "LAL", "BOS")
        season: NBA season (e.g., "2024-25")
    
    Returns:
        DataFrame with game logs
    """
    if not NBA_API_AVAILABLE:
        raise ImportError("nba_api not installed. Run: pip install nba-api")
    
    team_info = teams.find_team_by_abbreviation(team_abbr)
    if not team_info:
        raise ValueError(f"Team not found: {team_abbr}")
    
    team_id = team_info["id"]
    game_log = teamgamelog.TeamGameLog(team_id=team_id, season=season)
    df = game_log.get_data_frames()[0]
    
    return df


def fetch_player_stats(player_name: str, season: str = "2024-25") -> pd.DataFrame:
    """
    Fetch game logs for a specific NBA player.
    
    Args:
        player_name: Player name (first last)
        season: NBA season (e.g., "2024-25")
    
    Returns:
        DataFrame with player game logs
    """
    if not NBA_API_AVAILABLE:
        raise ImportError("nba_api not installed. Run: pip install nba-api")
    
    player_info = players.find_players_by_full_name(player_name)
    if not player_info:
        raise ValueError(f"Player not found: {player_name}")
    
    player_id = player_info[0]["id"]
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    df = game_log.get_data_frames()[0]
    
    return df


# ============================================================================
# PLOTTING TEMPLATES
# ============================================================================

def plot_team_trend(df: pd.DataFrame, metric: str, team_name: str) -> go.Figure:
    """
    Create interactive line chart for team performance metric.
    
    Args:
        df: DataFrame with game logs (must have 'GAME_DATE' and metric column)
        metric: Column name to plot (e.g., 'PTS', 'FG_PCT', 'PLUS_MINUS')
        team_name: Team name for title
    
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['GAME_DATE'],
        y=df[metric],
        mode='lines+markers',
        name=metric,
        line=dict(width=2),
        marker=dict(size=6)
    ))
    
    # Add rolling average
    if len(df) >= 5:
        rolling_avg = df[metric].rolling(window=5).mean()
        fig.add_trace(go.Scatter(
            x=df['GAME_DATE'],
            y=rolling_avg,
            mode='lines',
            name='5-Game Avg',
            line=dict(dash='dash', width=2)
        ))
    
    fig.update_layout(
        title=f"{team_name} - {metric} Trend",
        xaxis_title="Game Date",
        yaxis_title=metric,
        hovermode='x unified',
        template='plotly_dark'
    )
    
    return fig


def plot_correlation_heatmap(df: pd.DataFrame, features: List[str]) -> go.Figure:
    """
    Create correlation heatmap for selected features.
    
    Args:
        df: DataFrame with feature columns
        features: List of column names to correlate
    
    Returns:
        Plotly figure object
    """
    corr_matrix = df[features].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Feature Correlation Matrix",
        template='plotly_dark',
        height=600
    )
    
    return fig


def plot_betting_performance(df: pd.DataFrame, bet_type: str = "spread") -> go.Figure:
    """
    Visualize betting performance over time.
    
    Args:
        df: DataFrame with columns: date, profit_loss, cumulative_profit
        bet_type: Type of bet (for title)
    
    Returns:
        Plotly figure object
    """
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Daily Profit/Loss", "Cumulative Profit"),
        vertical_spacing=0.15
    )
    
    # Daily P/L
    colors = ['green' if x > 0 else 'red' for x in df['profit_loss']]
    fig.add_trace(
        go.Bar(x=df['date'], y=df['profit_loss'], marker_color=colors, name="Daily P/L"),
        row=1, col=1
    )
    
    # Cumulative Profit
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['cumulative_profit'], mode='lines+markers',
                   name="Cumulative Profit", line=dict(width=3)),
        row=2, col=1
    )
    
    fig.update_layout(
        title_text=f"Betting Performance - {bet_type.upper()}",
        showlegend=False,
        template='plotly_dark',
        height=700
    )
    
    return fig


# ============================================================================
# MODEL EVALUATION
# ============================================================================

def evaluate_classification_model(y_true: np.ndarray, y_pred: np.ndarray,
                                   y_prob: Optional[np.ndarray] = None) -> Dict[str, float]:
    """
    Comprehensive classification model evaluation.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_prob: Predicted probabilities (for AUC)
    
    Returns:
        Dictionary with accuracy, precision, recall, F1, and optionally AUC
    """
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average='weighted', zero_division=0),
        "recall": recall_score(y_true, y_pred, average='weighted', zero_division=0),
        "f1_score": f1_score(y_true, y_pred, average='weighted', zero_division=0)
    }
    
    if y_prob is not None:
        try:
            metrics["roc_auc"] = roc_auc_score(y_true, y_prob, multi_class='ovr')
        except ValueError:
            metrics["roc_auc"] = None
    
    return metrics


def evaluate_regression_model(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Comprehensive regression model evaluation.
    
    Args:
        y_true: True values
        y_pred: Predicted values
    
    Returns:
        Dictionary with MSE, RMSE, MAE, and R²
    """
    mse = mean_squared_error(y_true, y_pred)
    
    return {
        "mse": mse,
        "rmse": np.sqrt(mse),
        "mae": mean_absolute_error(y_true, y_pred),
        "r2": r2_score(y_true, y_pred)
    }


def calculate_betting_roi(wins: int, losses: int, unit_size: float = 100,
                          avg_odds: float = -110) -> Dict[str, float]:
    """
    Calculate betting ROI and related metrics.
    
    Args:
        wins: Number of winning bets
        losses: Number of losing bets
        unit_size: Bet amount per unit (default: $100)
        avg_odds: Average American odds (default: -110)
    
    Returns:
        Dictionary with total_bets, win_rate, total_profit, roi
    """
    total_bets = wins + losses
    if total_bets == 0:
        return {"total_bets": 0, "win_rate": 0.0, "total_profit": 0.0, "roi": 0.0}
    
    # Convert American odds to decimal multiplier
    if avg_odds > 0:
        multiplier = (avg_odds / 100)
    else:
        multiplier = (100 / abs(avg_odds))
    
    total_wagered = total_bets * unit_size
    total_winnings = wins * unit_size * multiplier
    total_losses_amount = losses * unit_size
    total_profit = total_winnings - total_losses_amount
    
    return {
        "total_bets": total_bets,
        "win_rate": wins / total_bets,
        "total_profit": total_profit,
        "roi": (total_profit / total_wagered) * 100
    }


# ============================================================================
# ALERT SYSTEMS
# ============================================================================

def send_telegram_alert(message: str, bot_token: Optional[str] = None,
                        chat_id: Optional[str] = None) -> bool:
    """
    Send alert to Telegram.
    
    Args:
        message: Message text
        bot_token: Telegram bot token (reads from env if None)
        chat_id: Telegram chat ID (reads from env if None)
    
    Returns:
        True if successful, False otherwise
    """
    if bot_token is None or chat_id is None:
        config = load_env_config()
        bot_token = bot_token or config["telegram_bot_token"]
        chat_id = chat_id or config["telegram_chat_id"]
    
    if not bot_token or not chat_id:
        logging.warning("Telegram credentials not configured")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        logging.error(f"Telegram alert failed: {e}")
        return False


def send_discord_alert(message: str, webhook_url: Optional[str] = None) -> bool:
    """
    Send alert to Discord.
    
    Args:
        message: Message text
        webhook_url: Discord webhook URL (reads from env if None)
    
    Returns:
        True if successful, False otherwise
    """
    if webhook_url is None:
        config = load_env_config()
        webhook_url = config["discord_webhook_url"]
    
    if not webhook_url:
        logging.warning("Discord webhook not configured")
        return False
    
    payload = {"content": message}
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        logging.error(f"Discord alert failed: {e}")
        return False


# ============================================================================
# DATA CACHING
# ============================================================================

def cache_data(data: Any, cache_key: str, cache_dir: str = "C:/EQ12/cache/nba") -> None:
    """
    Cache data to JSON file with UTC timestamp.
    
    Args:
        data: Data to cache (must be JSON-serializable)
        cache_key: Unique cache identifier
        cache_dir: Cache directory path
    """
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    cache_file = cache_path / f"{cache_key}_{timestamp}.json"
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    logging.info(f"Cached data to {cache_file}")


def load_cached_data(cache_key: str, max_age_hours: int = 24,
                     cache_dir: str = "C:/EQ12/cache/nba") -> Optional[Any]:
    """
    Load most recent cached data if within age limit.
    
    Args:
        cache_key: Cache identifier
        max_age_hours: Maximum cache age in hours
        cache_dir: Cache directory path
    
    Returns:
        Cached data or None if not found/expired
    """
    cache_path = Path(cache_dir)
    if not cache_path.exists():
        return None
    
    # Find most recent cache file
    cache_files = list(cache_path.glob(f"{cache_key}_*.json"))
    if not cache_files:
        return None
    
    most_recent = max(cache_files, key=lambda p: p.stat().st_mtime)
    
    # Check age
    file_age = datetime.now(timezone.utc) - datetime.fromtimestamp(
        most_recent.stat().st_mtime, tz=timezone.utc
    )
    
    if file_age > timedelta(hours=max_age_hours):
        logging.info(f"Cache expired: {most_recent}")
        return None
    
    with open(most_recent, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logging.info(f"Loaded cached data from {most_recent}")
    return data


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def save_snapshot(df: pd.DataFrame, snapshot_name: str, output_dir: str = "C:/EQ12/logs") -> str:
    """
    Save DataFrame snapshot with UTC timestamp.
    
    Args:
        df: DataFrame to save
        snapshot_name: Base name for snapshot
        output_dir: Output directory
    
    Returns:
        Path to saved snapshot
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    snapshot_file = output_path / f"{snapshot_name}_{timestamp}.csv"
    
    df.to_csv(snapshot_file, index=False)
    logging.info(f"Saved snapshot to {snapshot_file}")
    
    return str(snapshot_file)


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string."""
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage string."""
    return f"{value * 100:.{decimals}f}%"


# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

# Set default plotting styles
sns.set_style("darkgrid")
plt.style.use('dark_background')

# Configure pandas display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', '{:.2f}'.format)

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Print module load confirmation
print("✅ EQ12 NBA Utils loaded successfully")
print(f"   NBA API Available: {NBA_API_AVAILABLE}")
print(f"   Logging configured: C:/EQ12/logs/")
print(f"   Cache directory: C:/EQ12/cache/nba/")
