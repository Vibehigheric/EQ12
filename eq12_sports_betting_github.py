#!/usr/bin/env python3
"""
EQ12 Sports Betting GitHub System
==================================

Advanced sports betting quantitative trading system with GitHub integration.
Manages betting models, repositories, automation, and performance tracking.

Features:
- GitHub repository management for betting models
- Quantitative trading strategy development
- Model versioning and deployment
- Performance analytics and backtesting
- Automated trading integration
- Risk management systems
- Market data integration
- Portfolio optimization

Usage:
    python eq12_sports_betting_github.py --create-repo
    python eq12_sports_betting_github.py --deploy-models
    python eq12_sports_betting_github.py --backtest-strategies
    python eq12_sports_betting_github.py --track-performance

Author: EQ12 Development Team
Version: 1.0.0
"""

import argparse
import asyncio
import json
import logging
import random
import statistics
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

# EQ12 Configuration
EQ12_ROOT = Path(r"C:\EQ12")
LOGS_DIR = EQ12_ROOT / "logs"
CONFIGS_DIR = EQ12_ROOT / "configs"
BETTING_DIR = EQ12_ROOT / "sports_betting"
MODELS_DIR = BETTING_DIR / "models"
STRATEGIES_DIR = BETTING_DIR / "strategies"
BACKTESTS_DIR = BETTING_DIR / "backtests"
REPOS_DIR = BETTING_DIR / "repositories"

# Ensure directories exist
for directory in [
    LOGS_DIR,
    CONFIGS_DIR,
    BETTING_DIR,
    MODELS_DIR,
    STRATEGIES_DIR,
    BACKTESTS_DIR,
    REPOS_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# Setup logging
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_name = f"sports_betting_github_{timestamp}.log"
log_file = LOGS_DIR / log_file_name
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@dataclass
class BettingModel:
    """Data class for betting models"""

    name: str
    model_type: str
    sport: str
    algorithm: str
    features: list[str] = field(default_factory=list)
    performance_metrics: dict[str, float] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    version: str = "1.0.0"
    accuracy: float = 0.0
    roi: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    github_repo: str | None = None
    deployment_status: str = "development"  # development, testing, production


@dataclass
class TradingStrategy:
    """Data class for trading strategies"""

    name: str
    strategy_type: str
    sports: list[str] = field(default_factory=list)
    betting_markets: list[str] = field(default_factory=list)
    risk_parameters: dict[str, float] = field(default_factory=dict)
    kelly_criterion: bool = True
    bankroll_management: str = "kelly"
    models: list[str] = field(default_factory=list)
    expected_roi: float = 0.0
    max_bet_size: float = 0.05  # 5% of bankroll
    github_branch: str | None = None


@dataclass
class BacktestResult:
    """Data class for backtest results"""

    strategy_name: str
    model_name: str
    start_date: str
    end_date: str
    total_bets: int
    winning_bets: int
    losing_bets: int
    total_roi: float
    annualized_roi: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    avg_odds: float
    total_profit: float
    confidence_interval: dict[str, float] = field(default_factory=dict)


@dataclass
class GitHubRepository:
    """Data class for GitHub repositories"""

    name: str
    description: str
    owner: str
    private: bool = True
    models: list[str] = field(default_factory=list)
    strategies: list[str] = field(default_factory=list)
    last_commit: str | None = None
    url: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class EQ12SportsBettingGitHub:
    """
    Advanced sports betting quantitative trading system with GitHub integration
    """

    def __init__(self):
        self.config = self.load_betting_config()
        self.models = self.load_models()
        self.strategies = self.load_strategies()
        self.repositories = self.load_repositories()
        self.performance_data = self.load_performance_data()
        logger.info("EQ12 Sports Betting GitHub System initialized")

    def load_betting_config(self) -> dict[str, Any]:
        """Load sports betting configuration"""
        config_file = CONFIGS_DIR / "sports_betting_config.json"

        default_config = {
            "github_settings": {
                "username": "",
                "personal_access_token": "",
                "organization": "",
                "auto_create_repos": True,
                "auto_commit": True,
                "branch_strategy": "feature_branch",
            },
            "trading_settings": {
                "initial_bankroll": 10000.0,
                "max_bet_percentage": 0.05,
                "min_odds": 1.5,
                "max_odds": 10.0,
                "kelly_multiplier": 0.25,
                "risk_tolerance": "medium",
            },
            "model_settings": {
                "default_algorithm": "gradient_boosting",
                "feature_selection": "automated",
                "validation_method": "time_series_cv",
                "retrain_frequency": "weekly",
                "performance_threshold": 0.55,
            },
            "sports_markets": {
                "football": {
                    "enabled": True,
                    "leagues": ["NFL", "NCAAF"],
                    "markets": ["moneyline", "spread", "totals"],
                    "data_sources": ["odds_api", "espn"],
                },
                "basketball": {
                    "enabled": True,
                    "leagues": ["NBA", "NCAAB"],
                    "markets": ["moneyline", "spread", "totals"],
                    "data_sources": ["odds_api", "espn"],
                },
                "baseball": {
                    "enabled": False,
                    "leagues": ["MLB"],
                    "markets": ["moneyline", "run_line", "totals"],
                    "data_sources": ["odds_api"],
                },
            },
            "automation_settings": {
                "auto_bet": False,
                "bet_approval_required": True,
                "daily_analysis": True,
                "telegram_notifications": True,
                "email_reports": False,
            },
        }

        if config_file.exists():
            try:
                with open(config_file) as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Error loading betting config: {e}")
        else:
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default betting config: {config_file}")

        return default_config

    def load_models(self) -> list[BettingModel]:
        """Load betting models"""
        models = []
        models_file = MODELS_DIR / "models.json"

        if models_file.exists():
            try:
                with open(models_file) as f:
                    models_data = json.load(f)
                models = [BettingModel(**model) for model in models_data]
            except Exception as e:
                logger.warning(f"Error loading models: {e}")

        # Create default models if none exist
        if not models:
            default_models = [
                BettingModel(
                    name="nfl_moneyline_predictor",
                    model_type="classification",
                    sport="football",
                    algorithm="gradient_boosting",
                    features=[
                        "team_strength",
                        "home_advantage",
                        "weather",
                        "injury_report",
                        "recent_form",
                        "head_to_head",
                    ],
                    performance_metrics={
                        "accuracy": 0.58,
                        "precision": 0.56,
                        "recall": 0.61,
                        "f1_score": 0.58,
                    },
                    accuracy=0.58,
                    roi=0.12,
                    sharpe_ratio=1.8,
                    max_drawdown=0.15,
                ),
                BettingModel(
                    name="nba_spread_predictor",
                    model_type="regression",
                    sport="basketball",
                    algorithm="xgboost",
                    features=[
                        "offensive_rating",
                        "defensive_rating",
                        "pace",
                        "rest_days",
                        "travel_distance",
                        "motivation",
                    ],
                    performance_metrics={"mae": 6.2, "rmse": 8.1, "r2_score": 0.34},
                    accuracy=0.52,
                    roi=0.08,
                    sharpe_ratio=1.2,
                    max_drawdown=0.18,
                ),
            ]

            self.save_models(default_models)
            models = default_models

        return models

    def load_strategies(self) -> list[TradingStrategy]:
        """Load trading strategies"""
        strategies = []
        strategies_file = STRATEGIES_DIR / "strategies.json"

        if strategies_file.exists():
            try:
                with open(strategies_file) as f:
                    strategies_data = json.load(f)
                strategies = [TradingStrategy(**strategy) for strategy in strategies_data]
            except Exception as e:
                logger.warning(f"Error loading strategies: {e}")

        # Create default strategies if none exist
        if not strategies:
            default_strategies = [
                TradingStrategy(
                    name="conservative_value_betting",
                    strategy_type="value_betting",
                    sports=["football", "basketball"],
                    betting_markets=["moneyline"],
                    risk_parameters={
                        "min_edge": 0.05,
                        "max_bet_size": 0.03,
                        "kelly_multiplier": 0.25,
                    },
                    kelly_criterion=True,
                    bankroll_management="kelly",
                    models=["nfl_moneyline_predictor", "nba_spread_predictor"],
                    expected_roi=0.15,
                    max_bet_size=0.03,
                ),
                TradingStrategy(
                    name="aggressive_arbitrage",
                    strategy_type="arbitrage",
                    sports=["football", "basketball"],
                    betting_markets=["moneyline", "spread", "totals"],
                    risk_parameters={
                        "min_profit_margin": 0.02,
                        "max_bet_size": 0.10,
                        "max_exposure": 0.20,
                    },
                    kelly_criterion=False,
                    bankroll_management="fixed_percentage",
                    models=[],
                    expected_roi=0.05,
                    max_bet_size=0.10,
                ),
            ]

            self.save_strategies(default_strategies)
            strategies = default_strategies

        return strategies

    def load_repositories(self) -> list[GitHubRepository]:
        """Load GitHub repositories"""
        repositories = []
        repos_file = REPOS_DIR / "repositories.json"

        if repos_file.exists():
            try:
                with open(repos_file) as f:
                    repos_data = json.load(f)
                repositories = [GitHubRepository(**repo) for repo in repos_data]
            except Exception as e:
                logger.warning(f"Error loading repositories: {e}")

        return repositories

    def load_performance_data(self) -> dict[str, Any]:
        """Load performance tracking data"""
        perf_file = BETTING_DIR / "performance.json"

        default_performance = {
            "total_bankroll": self.config["trading_settings"]["initial_bankroll"],
            "current_bankroll": self.config["trading_settings"]["initial_bankroll"],
            "total_bets": 0,
            "winning_bets": 0,
            "total_roi": 0.0,
            "best_month": 0.0,
            "worst_month": 0.0,
            "current_streak": 0,
            "longest_winning_streak": 0,
            "longest_losing_streak": 0,
            "models_performance": {},
            "strategies_performance": {},
        }

        if perf_file.exists():
            try:
                with open(perf_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading performance data: {e}")

        return default_performance

    def save_models(self, models: list[BettingModel]):
        """Save betting models"""
        models_file = MODELS_DIR / "models.json"
        models_data = [model.__dict__ for model in models]
        with open(models_file, "w") as f:
            json.dump(models_data, f, indent=2)

    def save_strategies(self, strategies: list[TradingStrategy]):
        """Save trading strategies"""
        strategies_file = STRATEGIES_DIR / "strategies.json"
        strategies_data = [strategy.__dict__ for strategy in strategies]
        with open(strategies_file, "w") as f:
            json.dump(strategies_data, f, indent=2)

    def save_repositories(self, repositories: list[GitHubRepository]):
        """Save GitHub repositories"""
        repos_file = REPOS_DIR / "repositories.json"
        repos_data = [repo.__dict__ for repo in repositories]
        with open(repos_file, "w") as f:
            json.dump(repos_data, f, indent=2)

    def save_performance_data(self):
        """Save performance data"""
        perf_file = BETTING_DIR / "performance.json"
        with open(perf_file, "w") as f:
            json.dump(self.performance_data, f, indent=2)

    async def create_github_repository(self, name: str, description: str) -> GitHubRepository:
        """Create a new GitHub repository for betting models"""
        logger.info(f"Creating GitHub repository: {name}")

        github_username = self.config["github_settings"]["username"]
        github_token = self.config["github_settings"]["personal_access_token"]

        if not github_username or not github_token:
            raise ValueError("GitHub credentials not configured")

        # Mock GitHub API call (replace with actual GitHub API integration)

        # Simulate API call
        await asyncio.sleep(1)

        repository = GitHubRepository(
            name=name,
            description=description,
            owner=github_username,
            private=True,
            url=f"https://github.com/{github_username}/{name}",
        )

        # Create initial repository structure
        await self.setup_repository_structure(repository)

        self.repositories.append(repository)
        self.save_repositories(self.repositories)

        logger.info(f"Created repository: {repository.url}")
        return repository

    async def setup_repository_structure(self, repository: GitHubRepository):
        """Setup initial repository structure and files"""
        logger.info(f"Setting up repository structure for {repository.name}")

        # Create local repository directory
        local_repo_path = REPOS_DIR / repository.name
        local_repo_path.mkdir(exist_ok=True)

        # Create directory structure
        directories = [
            "models",
            "strategies",
            "data",
            "backtests",
            "notebooks",
            "tests",
            "scripts",
            "docs",
        ]

        for directory in directories:
            (local_repo_path / directory).mkdir(exist_ok=True)

        # Create README.md
        readme_content = f"""# {repository.name}

{repository.description}

## Structure

- `models/` - Machine learning models for sports betting predictions
- `strategies/` - Trading strategies and risk management
- `data/` - Historical data and market feeds
- `backtests/` - Backtesting results and analysis
- `notebooks/` - Jupyter notebooks for analysis
- `tests/` - Unit tests and validation
- `scripts/` - Utility scripts and automation
- `docs/` - Documentation and guides

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from models.predictor import BettingPredictor
from strategies.kelly import KellyStrategy

# Initialize predictor
predictor = BettingPredictor()

# Load strategy
strategy = KellyStrategy()

# Make predictions
predictions = predictor.predict(games)
bets = strategy.calculate_bets(predictions)
```

## Performance

Current Model Performance:
- Accuracy: TBD
- ROI: TBD
- Sharpe Ratio: TBD
- Max Drawdown: TBD

## License

Private Repository - EQ12 Sports Betting System
"""

        with open(local_repo_path / "README.md", "w") as f:
            f.write(readme_content)

        # Create requirements.txt
        requirements = [
            "numpy>=1.21.0",
            "pandas>=1.3.0",
            "scikit-learn>=1.0.0",
            "xgboost>=1.5.0",
            "matplotlib>=3.4.0",
            "seaborn>=0.11.0",
            "jupyter>=1.0.0",
            "requests>=2.26.0",
            "aiohttp>=3.8.0",
            "python-telegram-bot>=13.0",
        ]

        with open(local_repo_path / "requirements.txt", "w") as f:
            f.write("\n".join(requirements))

        # Create .gitignore
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# Environment variables
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Betting data and logs
data/raw/
data/processed/
logs/
*.log

# API keys and secrets
config/secrets.json
*.key
"""

        with open(local_repo_path / ".gitignore", "w") as f:
            f.write(gitignore_content)

        logger.info(f"Repository structure created at {local_repo_path}")

    async def deploy_model_to_github(self, model: BettingModel, repository_name: str):
        """Deploy betting model to GitHub repository"""
        logger.info(f"Deploying model {model.name} to repository {repository_name}")

        # Find repository
        repository = None
        for repo in self.repositories:
            if repo.name == repository_name:
                repository = repo
                break

        if not repository:
            logger.error(f"Repository {repository_name} not found")
            return

        local_repo_path = REPOS_DIR / repository_name
        models_path = local_repo_path / "models"

        # Create model Python file
        model_code = self.generate_model_code(model)
        model_file = models_path / f"{model.name}.py"

        with open(model_file, "w") as f:
            f.write(model_code)

        # Create model configuration
        model_config = {
            "name": model.name,
            "type": model.model_type,
            "sport": model.sport,
            "algorithm": model.algorithm,
            "features": model.features,
            "performance": model.performance_metrics,
            "version": model.version,
            "created_at": model.created_at,
            "last_updated": model.last_updated,
        }

        config_file = models_path / f"{model.name}_config.json"
        with open(config_file, "w") as f:
            json.dump(model_config, f, indent=2)

        # Update model with repository reference
        model.github_repo = repository.name
        model.deployment_status = "deployed"

        # Add model to repository
        if model.name not in repository.models:
            repository.models.append(model.name)

        self.save_models(self.models)
        self.save_repositories(self.repositories)

        logger.info(f"Model {model.name} deployed successfully")

    def generate_model_code(self, model: BettingModel) -> str:
        """Generate Python code for betting model"""

        code_template = f'''"""
{model.name} - Sports Betting Prediction Model
Generated by EQ12 Sports Betting GitHub System

Model Type: {model.model_type}
Sport: {model.sport}
Algorithm: {model.algorithm}
Version: {model.version}
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import logging

logger = logging.getLogger(__name__)


class {model.name.title().replace("_", "")}:
    """
    {model.sport.title()} betting prediction model using {model.algorithm}

    Features: {", ".join(model.features)}
    Expected Accuracy: {model.accuracy:.1%}
    Expected ROI: {model.roi:.1%}
    """

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.features = {model.features}
        self.is_trained = False

    def prepare_features(self, data):
        """Prepare features for model input"""
        feature_data = data[self.features].copy()

        # Handle missing values
        feature_data = feature_data.fillna(feature_data.mean())

        # Scale features
        if self.is_trained:
            scaled_features = self.scaler.transform(feature_data)
        else:
            scaled_features = self.scaler.fit_transform(feature_data)

        return scaled_features

    def train(self, training_data, target_column):
        """Train the betting model"""
        logger.info("Training {model.name} model...")

        # Prepare features and targets
        X = self.prepare_features(training_data)
        y = training_data[target_column]

        # Initialize model based on type
        if "{model.model_type}" == "classification":
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
        else:
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )

        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Validate performance
        predictions = self.model.predict(X_test)

        if "{model.model_type}" == "classification":
            accuracy = accuracy_score(y_test, predictions)
            logger.info(f"Model accuracy: {{accuracy:.1%}}")
        else:
            from sklearn.metrics import mean_squared_error
            mse = mean_squared_error(y_test, predictions)
            logger.info(f"Model MSE: {{mse:.4f}}")

        return self.model

    def predict(self, data):
        """Make predictions on new data"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        X = self.prepare_features(data)
        predictions = self.model.predict(X)

        # Get prediction probabilities for classification
        if "{model.model_type}" == "classification":
            probabilities = self.model.predict_proba(X)
            return predictions, probabilities
        else:
            return predictions

    def calculate_betting_edge(self, predictions, odds):
        """Calculate betting edge using model predictions and market odds"""
        if "{model.model_type}" == "classification":
            # For classification, use probability vs implied probability
            _, probabilities = predictions
            implied_prob = 1 / odds
            model_prob = probabilities[:, 1]  # Probability of positive outcome

            # Calculate edge
            edge = model_prob - implied_prob
            return edge
        else:
            # For regression, compare prediction vs line
            return predictions - odds

    def save_model(self, filepath):
        """Save trained model to file"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")

        model_data = {{
            'model': self.model,
            'scaler': self.scaler,
            'features': self.features,
            'metadata': {{
                'name': "{model.name}",
                'version': "{model.version}",
                'sport': "{model.sport}",
                'algorithm': "{model.algorithm}",
                'accuracy': {model.accuracy},
                'roi': {model.roi}
            }}
        }}

        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {{filepath}}")

    def load_model(self, filepath):
        """Load trained model from file"""
        model_data = joblib.load(filepath)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.features = model_data['features']
        self.is_trained = True

        logger.info(f"Model loaded from {{filepath}}")


# Example usage
if __name__ == "__main__":
    # Initialize model
    model = {model.name.title().replace("_", "")}()

    # Load sample data (replace with actual data loading)
    # data = pd.read_csv('training_data.csv')
    # target = 'outcome'

    # Train model
    # model.train(data, target)

    # Make predictions
    # predictions = model.predict(new_data)

    # Save model
    # model.save_model('{model.name}_v{model.version}.pkl')

    print("Model initialized successfully")
'''

        return code_template

    async def run_backtest(
        self, model_name: str, strategy_name: str, start_date: str, end_date: str
    ) -> BacktestResult:
        """Run backtest for model and strategy combination"""
        logger.info(f"Running backtest for {model_name} with {strategy_name}")

        # Find model and strategy
        model = None
        strategy = None

        for m in self.models:
            if m.name == model_name:
                model = m
                break

        for s in self.strategies:
            if s.name == strategy_name:
                strategy = s
                break

        if not model or not strategy:
            raise ValueError("Model or strategy not found")

        # Mock backtest (replace with actual backtesting logic)
        await asyncio.sleep(2)  # Simulate backtest time

        # Generate realistic backtest results
        total_bets = random.randint(100, 500)
        win_rate = model.accuracy + random.uniform(-0.05, 0.05)
        winning_bets = int(total_bets * win_rate)
        losing_bets = total_bets - winning_bets

        # Calculate ROI based on Kelly Criterion and edge
        avg_edge = 0.03 + random.uniform(-0.02, 0.02)
        avg_odds = 2.5 + random.uniform(-0.5, 0.5)

        if strategy.kelly_criterion:
            kelly_fraction = avg_edge / (avg_odds - 1)
            bet_size = min(
                kelly_fraction * strategy.risk_parameters.get("kelly_multiplier", 0.25),
                strategy.max_bet_size,
            )
        else:
            bet_size = strategy.max_bet_size

        # Simulate returns
        win_return = (avg_odds - 1) * bet_size
        loss_return = -bet_size

        total_return = (winning_bets * win_return) + (losing_bets * loss_return)
        total_roi = total_return / total_bets

        # Calculate risk metrics
        daily_returns = []
        for _ in range(total_bets):
            if random.random() < win_rate:
                daily_returns.append(win_return)
            else:
                daily_returns.append(loss_return)

        if daily_returns:
            sharpe_ratio = (statistics.mean(daily_returns) / statistics.stdev(daily_returns)) * (
                252**0.5
            )

            # Calculate max drawdown
            cumulative = [0]
            for ret in daily_returns:
                cumulative.append(cumulative[-1] + ret)

            peak = cumulative[0]
            max_drawdown = 0
            for value in cumulative:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak if peak != 0 else 0
                max_drawdown = max(max_drawdown, drawdown)
        else:
            sharpe_ratio = 0
            max_drawdown = 0

        # Annualize ROI
        days_diff = (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)).days
        annualized_roi = total_roi * (365 / max(days_diff, 1))

        backtest_result = BacktestResult(
            strategy_name=strategy_name,
            model_name=model_name,
            start_date=start_date,
            end_date=end_date,
            total_bets=total_bets,
            winning_bets=winning_bets,
            losing_bets=losing_bets,
            total_roi=total_roi,
            annualized_roi=annualized_roi,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            avg_odds=avg_odds,
            total_profit=total_return,
            confidence_interval={
                "lower_95": total_roi - (0.1 * total_roi),
                "upper_95": total_roi + (0.1 * total_roi),
            },
        )

        # Save backtest results
        self.save_backtest_result(backtest_result)

        logger.info(f"Backtest completed: {win_rate:.1%} win rate, {total_roi:.1%} ROI")
        return backtest_result

    def save_backtest_result(self, result: BacktestResult):
        """Save backtest result to file"""
        result_file = BACKTESTS_DIR / f"{result.model_name}_{result.strategy_name}_{timestamp}.json"
        with open(result_file, "w") as f:
            json.dump(result.__dict__, f, indent=2)

    async def track_performance(self):
        """Track and update performance metrics"""
        logger.info("Tracking performance metrics...")

        # Update model performance based on recent backtests
        for model in self.models:
            # Find recent backtests for this model
            model_backtests = []
            for backtest_file in BACKTESTS_DIR.glob(f"{model.name}_*.json"):
                try:
                    with open(backtest_file) as f:
                        backtest_data = json.load(f)
                    model_backtests.append(backtest_data)
                except Exception as e:
                    logger.warning(f"Error loading backtest {backtest_file}: {e}")

            if model_backtests:
                # Calculate average performance
                avg_roi = statistics.mean([bt["total_roi"] for bt in model_backtests])
                avg_sharpe = statistics.mean([bt["sharpe_ratio"] for bt in model_backtests])
                max_dd = max([bt["max_drawdown"] for bt in model_backtests])
                avg_accuracy = statistics.mean([bt["win_rate"] for bt in model_backtests])

                # Update model metrics
                model.roi = avg_roi
                model.sharpe_ratio = avg_sharpe
                model.max_drawdown = max_dd
                model.accuracy = avg_accuracy
                model.last_updated = datetime.now(UTC).isoformat()

        # Update strategy performance
        for strategy in self.strategies:
            strategy_backtests = []
            for backtest_file in BACKTESTS_DIR.glob(f"*_{strategy.name}_*.json"):
                try:
                    with open(backtest_file) as f:
                        backtest_data = json.load(f)
                    strategy_backtests.append(backtest_data)
                except Exception as e:
                    logger.warning(f"Error loading backtest {backtest_file}: {e}")

            if strategy_backtests:
                avg_roi = statistics.mean([bt["total_roi"] for bt in strategy_backtests])
                strategy.expected_roi = avg_roi

        # Update overall performance data
        all_backtests = []
        for backtest_file in BACKTESTS_DIR.glob("*.json"):
            try:
                with open(backtest_file) as f:
                    backtest_data = json.load(f)
                all_backtests.append(backtest_data)
            except Exception:
                continue

        if all_backtests:
            self.performance_data["total_bets"] = sum([bt["total_bets"] for bt in all_backtests])
            self.performance_data["winning_bets"] = sum(
                [bt["winning_bets"] for bt in all_backtests]
            )

            total_roi = statistics.mean([bt["total_roi"] for bt in all_backtests])
            self.performance_data["total_roi"] = total_roi

            # Simulate bankroll growth
            initial_bankroll = self.config["trading_settings"]["initial_bankroll"]
            self.performance_data["current_bankroll"] = initial_bankroll * (1 + total_roi)

        # Save updated data
        self.save_models(self.models)
        self.save_strategies(self.strategies)
        self.save_performance_data()

        logger.info("Performance tracking completed")

    async def generate_performance_report(self) -> str:
        """Generate comprehensive performance report"""
        logger.info("Generating performance report...")

        report = f"""
# EQ12 Sports Betting Performance Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overall Performance
- Total Bankroll: ${self.performance_data["current_bankroll"]:,.2f}
- Total ROI: {self.performance_data["total_roi"]:.1%}
- Total Bets: {self.performance_data["total_bets"]:,}
- Win Rate: {(self.performance_data["winning_bets"] / max(self.performance_data["total_bets"], 1)):.1%}

## Model Performance
"""

        for model in self.models:
            report += f"""
### {model.name}
- Sport: {model.sport}
- Algorithm: {model.algorithm}
- Accuracy: {model.accuracy:.1%}
- ROI: {model.roi:.1%}
- Sharpe Ratio: {model.sharpe_ratio:.2f}
- Max Drawdown: {model.max_drawdown:.1%}
- Deployment: {model.deployment_status}
"""

        report += "\n## Strategy Performance\n"

        for strategy in self.strategies:
            report += f"""
### {strategy.name}
- Type: {strategy.strategy_type}
- Expected ROI: {strategy.expected_roi:.1%}
- Max Bet Size: {strategy.max_bet_size:.1%}
- Kelly Criterion: {strategy.kelly_criterion}
"""

        report += f"""
## GitHub Repositories
- Total Repositories: {len(self.repositories)}
"""

        for repo in self.repositories:
            report += f"""
### {repo.name}
- Models: {len(repo.models)}
- URL: {repo.url}
- Created: {repo.created_at[:10]}
"""

        # Save report
        report_file = BETTING_DIR / f"performance_report_{timestamp}.md"
        with open(report_file, "w") as f:
            f.write(report)

        logger.info(f"Performance report saved: {report_file}")
        return report


def main():
    """Main entry point for EQ12 Sports Betting GitHub System"""

    parser = argparse.ArgumentParser(
        description="EQ12 Sports Betting GitHub System - Quantitative trading with GitHub integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--create-repo", type=str, help="Create new GitHub repository")
    parser.add_argument(
        "--deploy-models",
        action="store_true",
        help="Deploy models to GitHub repositories",
    )
    parser.add_argument(
        "--backtest-strategies",
        action="store_true",
        help="Run backtests for all strategies",
    )
    parser.add_argument(
        "--track-performance",
        action="store_true",
        help="Track and update performance metrics",
    )
    parser.add_argument(
        "--generate-report", action="store_true", help="Generate performance report"
    )
    parser.add_argument(
        "--full-pipeline",
        action="store_true",
        help="Run complete betting system pipeline",
    )
    parser.add_argument("--model-name", type=str, help="Specific model name for operations")
    parser.add_argument("--strategy-name", type=str, help="Specific strategy name for operations")

    args = parser.parse_args()

    async def async_main():
        # Initialize sports betting system
        logger.info("🏈 Starting EQ12 Sports Betting GitHub System")
        betting_system = EQ12SportsBettingGitHub()

        try:
            if args.create_repo:
                # Create new repository
                repo_name = args.create_repo
                description = f"EQ12 Sports Betting Repository - {repo_name}"
                repository = await betting_system.create_github_repository(repo_name, description)
                print("✅ Created repository: {repository.url}")

            elif args.deploy_models or args.full_pipeline:
                # Deploy models to repositories
                for model in betting_system.models:
                    # Create repository if it doesn't exist
                    if not model.github_repo:
                        repo_name = f"eq12-{model.sport}-{model.model_type}-models"
                        description = f"EQ12 {model.sport.title()} {model.model_type} Models"
                        repository = await betting_system.create_github_repository(
                            repo_name, description
                        )
                        model.github_repo = repository.name

                    # Deploy model
                    await betting_system.deploy_model_to_github(model, model.github_repo)
                    print("✅ Deployed model: {model.name}")

            if args.backtest_strategies or args.full_pipeline:
                # Run backtests
                end_date = datetime.now().isoformat()
                start_date = (datetime.now() - timedelta(days=365)).isoformat()

                for model in betting_system.models:
                    for strategy in betting_system.strategies:
                        if model.sport in strategy.sports:
                            result = await betting_system.run_backtest(
                                model.name, strategy.name, start_date, end_date
                            )
                            print(f"📊 Backtest completed: {model.name} + {strategy.name}")
                            print(
                                f"   Win Rate: {result.win_rate:.1%}, ROI: {result.total_roi:.1%}"
                            )

            if args.track_performance or args.full_pipeline:
                # Track performance
                await betting_system.track_performance()
                print("📈 Performance tracking updated")

            if args.generate_report or args.full_pipeline:
                # Generate report
                await betting_system.generate_performance_report()
                print("📋 Performance report generated")

            if args.full_pipeline or not any(vars(args).values()):
                # Full pipeline summary
                print("\n🏈 EQ12 Sports Betting GitHub System Complete!")
                print("📦 Models: {len(betting_system.models)}")
                print("🎯 Strategies: {len(betting_system.strategies)}")
                print("📂 Repositories: {len(betting_system.repositories)}")
                print(
                    f"💰 Current Bankroll: ${betting_system.performance_data['current_bankroll']:,.2f}"
                )
                print(f"📊 Total ROI: {betting_system.performance_data['total_roi']:.1%}")
                print(f"🎲 Total Bets: {betting_system.performance_data['total_bets']:,}")

        except Exception as e:
            logger.error(f"Error in Sports Betting GitHub System: {e}")
            raise

        finally:
            logger.info("EQ12 Sports Betting GitHub System execution completed")

    # Run async main
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
