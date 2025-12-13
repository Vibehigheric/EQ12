#!/usr/bin/env python3
"""
⚡ EQ12 Auto-Trade Executor
Lightning-fast automated bet execution with millisecond CLV tracking
Integrates with X-Factor Pipeline for sentiment-driven trade execution
"""

import asyncio
import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

import aiohttp

# Setup logging with UTF-8 encoding fix
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/eq12_auto_trade.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class TradeOpportunity:
    """Represents a betting opportunity with edge calculation"""

    game_id: str
    sport: str
    market_type: str
    selection: str
    bookmaker: str
    odds: Decimal
    true_probability: Decimal
    kelly_fraction: Decimal
    recommended_stake: Decimal
    expected_value: Decimal
    confidence_score: Decimal
    xfactor_signal: float | None = None
    detected_at: datetime = None

    def __post_init__(self):
        if self.detected_at is None:
            self.detected_at = datetime.now(UTC)


@dataclass
class TradeExecution:
    """Represents an executed trade with performance metrics"""

    execution_id: str
    opportunity: TradeOpportunity
    execution_timestamp: datetime
    odds_at_detection: Decimal
    odds_at_execution: Decimal
    clv_milliseconds: int
    clv_value: Decimal
    stake_amount: Decimal
    status: str  # 'pending', 'placed', 'confirmed', 'failed'
    bookmaker_confirmation: str | None = None
    error_message: str | None = None


@dataclass
class CLVTracker:
    """Tracks Closing Line Value performance"""

    execution_id: str
    detection_time: float
    execution_time: float
    detection_odds: Decimal
    execution_odds: Decimal
    closing_odds: Decimal | None = None
    clv_percentage: float | None = None


class AutoTradeDatabase:
    """Database for storing trade executions and CLV tracking"""

    def __init__(self, db_path: str = "data/auto_trade.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Trade executions table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS trade_executions (
            execution_id TEXT PRIMARY KEY,
            game_id TEXT,
            sport TEXT,
            market_type TEXT,
            selection TEXT,
            bookmaker TEXT,
            odds_detected REAL,
            odds_executed REAL,
            kelly_fraction REAL,
            stake_amount REAL,
            expected_value REAL,
            xfactor_signal REAL,
            confidence_score REAL,
            clv_milliseconds INTEGER,
            clv_value REAL,
            execution_timestamp TEXT,
            status TEXT,
            bookmaker_confirmation TEXT,
            error_message TEXT
        )
        """
        )

        # CLV tracking table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS clv_tracking (
            execution_id TEXT PRIMARY KEY,
            detection_time REAL,
            execution_time REAL,
            detection_odds REAL,
            execution_odds REAL,
            closing_odds REAL,
            clv_percentage REAL,
            FOREIGN KEY (execution_id) REFERENCES trade_executions (execution_id)
        )
        """
        )

        # Performance metrics table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS performance_metrics (
            date TEXT,
            total_trades INTEGER,
            successful_trades INTEGER,
            average_clv REAL,
            total_volume REAL,
            net_profit REAL,
            roi_percentage REAL,
            PRIMARY KEY (date)
        )
        """
        )

        conn.commit()
        conn.close()

    def store_trade_execution(self, execution: TradeExecution):
        """Store trade execution in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        INSERT OR REPLACE INTO trade_executions VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                execution.execution_id,
                execution.opportunity.game_id,
                execution.opportunity.sport,
                execution.opportunity.market_type,
                execution.opportunity.selection,
                execution.opportunity.bookmaker,
                float(execution.odds_at_detection),
                float(execution.odds_at_execution),
                float(execution.opportunity.kelly_fraction),
                float(execution.stake_amount),
                float(execution.opportunity.expected_value),
                execution.opportunity.xfactor_signal,
                float(execution.opportunity.confidence_score),
                execution.clv_milliseconds,
                float(execution.clv_value),
                execution.execution_timestamp.isoformat(),
                execution.status,
                execution.bookmaker_confirmation,
                execution.error_message,
            ),
        )

        conn.commit()
        conn.close()


class BookmakerAPI:
    """Simulated bookmaker API for bet placement"""

    def __init__(self, config: dict):
        self.config = config
        self.session = None

    async def initialize(self):
        """Initialize HTTP session for API calls"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=5),
            headers={"User-Agent": "EQ12-AutoTrader/1.0"},
        )

    async def place_bet(
        self, opportunity: TradeOpportunity, stake: Decimal
    ) -> tuple[bool, str, str | None]:
        """
        Place bet with bookmaker API (simulated for demo)
        Returns: (success, message, confirmation_id)
        """
        try:
            # Simulate API call delay
            await asyncio.sleep(0.1)  # 100ms simulated latency

            # Simulate different success rates by bookmaker
            success_rates = {
                "draftkings": 0.95,
                "fanduel": 0.93,
                "betmgm": 0.90,
                "caesars": 0.88,
                "bovada": 0.85,
            }

            bookmaker = opportunity.bookmaker.lower()
            success_rate = success_rates.get(bookmaker, 0.80)

            # Random success/failure for demo
            import random

            if random.random() < success_rate:
                confirmation_id = f"CONF_{bookmaker.upper()}_{int(time.time() * 1000)}"
                return True, "Bet placed successfully", confirmation_id
            error_messages = [
                "Odds changed",
                "Insufficient balance",
                "Market suspended",
                "Bet limit exceeded",
                "Technical error",
            ]
            error = random.choice(error_messages)
            return False, error, None

        except Exception as e:
            return False, f"API error: {e!s}", None

    async def get_current_odds(self, game_id: str, market: str) -> Decimal | None:
        """Get current odds for CLV comparison (simulated)"""
        try:
            # Simulate slight odds movement
            import random

            base_odds = Decimal("2.0")
            movement = Decimal(str(random.uniform(-0.1, 0.1)))
            return base_odds + movement
        except:
            return None

    async def cleanup(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()


class AutoTradeExecutor:
    """Main auto-trade execution engine"""

    def __init__(self, config_path: str = "sports_betting_config.json"):
        self.config = self._load_config(config_path)
        self.auto_trade_config = self.config.get("AUTO_TRADE_EXECUTOR", {})
        self.database = AutoTradeDatabase()
        self.bookmaker_api = BookmakerAPI(self.auto_trade_config)
        self.running = False

        # Performance tracking
        self.stats = {
            "total_opportunities": 0,
            "trades_executed": 0,
            "successful_trades": 0,
            "failed_trades": 0,
            "total_volume": Decimal("0.00"),
            "average_clv_ms": 0,
            "start_time": None,
        }

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"⚠️ Config file not found: {config_path}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> dict:
        """Default configuration for auto-trade executor"""
        return {
            "AUTO_TRADE_EXECUTOR": {
                "ENABLE_AUTO_EXECUTION": True,
                "MIN_CONFIDENCE_FOR_X_TRADE": 0.08,  # 8% Kelly minimum
                "TRADE_EXECUTION_TIMEOUT_MS": 500,
                "MAX_STAKE_PER_TRADE": 1000.00,
                "MIN_STAKE_PER_TRADE": 10.00,
                "BANKROLL": 10000.00,
                "MAX_DAILY_VOLUME": 5000.00,
                "RISK_LIMITS": {
                    "MAX_TRADES_PER_HOUR": 10,
                    "MAX_LOSS_PER_DAY": 500.00,
                    "MIN_ODDS": 1.50,
                    "MAX_ODDS": 10.00,
                },
            }
        }

    async def initialize(self):
        """Initialize the auto-trade executor"""
        try:
            await self.bookmaker_api.initialize()
            self.stats["start_time"] = time.time()
            logger.info("✅ Auto-Trade Executor initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Auto-Trade Executor: {e}")
            raise

    def generate_execution_id(self) -> str:
        """Generate unique execution ID"""
        timestamp = str(int(time.time() * 1000000))
        random_data = os.urandom(8).hex()
        return f"EXEC_{timestamp}_{random_data[:8]}"

    def validate_opportunity(self, opportunity: TradeOpportunity) -> tuple[bool, str]:
        """Validate trade opportunity against risk limits"""
        config = self.auto_trade_config

        # Check if auto-execution is enabled
        if not config.get("ENABLE_AUTO_EXECUTION", False):
            return False, "Auto-execution disabled"

        # Check Kelly fraction threshold
        min_kelly = config.get("MIN_CONFIDENCE_FOR_X_TRADE", 0.08)
        if float(opportunity.kelly_fraction) < min_kelly:
            return (
                False,
                f"Kelly {opportunity.kelly_fraction} below threshold {min_kelly}",
            )

        # Check odds limits
        odds_value = float(opportunity.odds)
        min_odds = config.get("RISK_LIMITS", {}).get("MIN_ODDS", 1.50)
        max_odds = config.get("RISK_LIMITS", {}).get("MAX_ODDS", 10.00)

        if odds_value < min_odds or odds_value > max_odds:
            return False, f"Odds {odds_value} outside limits ({min_odds}-{max_odds})"

        # Check stake limits
        stake_value = float(opportunity.recommended_stake)
        min_stake = config.get("MIN_STAKE_PER_TRADE", 10.00)
        max_stake = config.get("MAX_STAKE_PER_TRADE", 1000.00)

        if stake_value < min_stake or stake_value > max_stake:
            return (
                False,
                f"Stake ${stake_value} outside limits (${min_stake}-${max_stake})",
            )

        return True, "Validated"

    async def execute_trade(self, opportunity: TradeOpportunity) -> TradeExecution:
        """Execute a trade opportunity with CLV tracking"""
        time.time()
        execution_id = self.generate_execution_id()

        # Validate opportunity
        is_valid, validation_message = self.validate_opportunity(opportunity)
        if not is_valid:
            logger.warning(f"🚫 Trade rejected: {validation_message}")
            return self._create_failed_execution(execution_id, opportunity, validation_message)

        try:
            # Record detection time and odds
            detection_time = time.time()
            detection_odds = opportunity.odds

            logger.info(
                f"⚡ Executing trade: {opportunity.selection} @ {opportunity.odds} | Kelly: {opportunity.kelly_fraction}"
            )

            # Place bet with bookmaker
            success, message, confirmation = await self.bookmaker_api.place_bet(
                opportunity, opportunity.recommended_stake
            )

            execution_time = time.time()
            clv_milliseconds = int((execution_time - detection_time) * 1000)

            # Get current odds for CLV calculation
            current_odds = await self.bookmaker_api.get_current_odds(
                opportunity.game_id, opportunity.market_type
            )

            execution_odds = current_odds if current_odds else opportunity.odds
            clv_value = self._calculate_clv(detection_odds, execution_odds)

            # Create execution record
            execution = TradeExecution(
                execution_id=execution_id,
                opportunity=opportunity,
                execution_timestamp=datetime.now(UTC),
                odds_at_detection=detection_odds,
                odds_at_execution=execution_odds,
                clv_milliseconds=clv_milliseconds,
                clv_value=clv_value,
                stake_amount=opportunity.recommended_stake,
                status="confirmed" if success else "failed",
                bookmaker_confirmation=confirmation,
                error_message=None if success else message,
            )

            # Store in database
            self.database.store_trade_execution(execution)

            # Update statistics
            self._update_stats(execution, success)

            # Log result
            if success:
                logger.info(
                    f"✅ Trade executed: {confirmation} | CLV: {clv_milliseconds}ms | Value: {clv_value:.4f}"
                )
            else:
                logger.error(f"❌ Trade failed: {message}")

            return execution

        except Exception as e:
            logger.error(f"❌ Execution error: {e}")
            return self._create_failed_execution(execution_id, opportunity, str(e))

    def _create_failed_execution(
        self, execution_id: str, opportunity: TradeOpportunity, error: str
    ) -> TradeExecution:
        """Create a failed execution record"""
        return TradeExecution(
            execution_id=execution_id,
            opportunity=opportunity,
            execution_timestamp=datetime.now(UTC),
            odds_at_detection=opportunity.odds,
            odds_at_execution=opportunity.odds,
            clv_milliseconds=0,
            clv_value=Decimal("0.0"),
            stake_amount=Decimal("0.0"),
            status="failed",
            error_message=error,
        )

    def _calculate_clv(self, detection_odds: Decimal, execution_odds: Decimal) -> Decimal:
        """Calculate Closing Line Value"""
        try:
            # CLV = (execution_odds - detection_odds) / detection_odds
            clv = (execution_odds - detection_odds) / detection_odds
            return clv.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        except:
            return Decimal("0.0")

    def _update_stats(self, execution: TradeExecution, success: bool):
        """Update performance statistics"""
        self.stats["trades_executed"] += 1

        if success:
            self.stats["successful_trades"] += 1
            self.stats["total_volume"] += execution.stake_amount
        else:
            self.stats["failed_trades"] += 1

        # Update average CLV
        if self.stats["trades_executed"] > 0:
            total_clv_ms = (
                self.stats["average_clv_ms"] * (self.stats["trades_executed"] - 1)
                + execution.clv_milliseconds
            )
            self.stats["average_clv_ms"] = total_clv_ms / self.stats["trades_executed"]

    async def process_xfactor_signal(self, xfactor_event, betting_edge):
        """Process X-Factor signal and execute trade if conditions met"""
        try:
            # Create trade opportunity from X-Factor signal and betting edge
            opportunity = TradeOpportunity(
                game_id=f"xfactor_{xfactor_event.tweet_id}",
                sport="nfl",  # Example sport
                market_type="moneyline",
                selection="Team A",  # Would be extracted from X-Factor event
                bookmaker="draftkings",
                odds=Decimal("2.10"),
                true_probability=Decimal("0.52"),
                kelly_fraction=Decimal("0.095"),  # 9.5% Kelly
                recommended_stake=Decimal("95.00"),
                expected_value=Decimal("0.052"),
                confidence_score=Decimal(str(xfactor_event.confidence_score)),
                xfactor_signal=xfactor_event.weighted_sentiment,
            )

            # Execute trade
            execution = await self.execute_trade(opportunity)
            return execution

        except Exception as e:
            logger.error(f"❌ Failed to process X-Factor signal: {e}")
            return None

    async def run_demo_mode(self):
        """Run auto-trade executor in demo mode"""
        logger.info("🎭 Starting Auto-Trade Executor in Demo Mode...")

        await self.initialize()

        # Create demo opportunities
        demo_opportunities = [
            TradeOpportunity(
                game_id="demo_game_001",
                sport="nfl",
                market_type="moneyline",
                selection="Kansas City Chiefs",
                bookmaker="draftkings",
                odds=Decimal("1.95"),
                true_probability=Decimal("0.55"),
                kelly_fraction=Decimal("0.105"),  # 10.5% Kelly
                recommended_stake=Decimal("105.00"),
                expected_value=Decimal("0.0725"),
                confidence_score=Decimal("0.89"),
                xfactor_signal=0.75,
            ),
            TradeOpportunity(
                game_id="demo_game_002",
                sport="nba",
                market_type="spread",
                selection="Lakers +3.5",
                bookmaker="fanduel",
                odds=Decimal("2.05"),
                true_probability=Decimal("0.52"),
                kelly_fraction=Decimal("0.085"),  # 8.5% Kelly
                recommended_stake=Decimal("85.00"),
                expected_value=Decimal("0.056"),
                confidence_score=Decimal("0.82"),
                xfactor_signal=0.45,
            ),
        ]

        # Execute demo trades
        for opportunity in demo_opportunities:
            execution = await self.execute_trade(opportunity)
            print(f"📊 Execution: {execution.status} | CLV: {execution.clv_milliseconds}ms")
            await asyncio.sleep(2)  # Delay between trades for demo

        # Print statistics
        self._print_statistics()

        await self.bookmaker_api.cleanup()
        logger.info("✅ Auto-Trade Executor demo completed")

    def _print_statistics(self):
        """Print execution statistics"""
        print("\n" + "=" * 60)
        print("⚡ AUTO-TRADE EXECUTOR STATISTICS")
        print("=" * 60)
        print(f"🎯 Total Trades: {self.stats['trades_executed']}")
        print(f"✅ Successful: {self.stats['successful_trades']}")
        print(f"❌ Failed: {self.stats['failed_trades']}")
        success_rate = (
            self.stats["successful_trades"] / max(1, self.stats["trades_executed"])
        ) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"💰 Total Volume: ${self.stats['total_volume']:.2f}")
        print(f"⚡ Average CLV: {self.stats['average_clv_ms']:.0f}ms")
        print("=" * 60)


async def main():
    """Main entry point for Auto-Trade Executor"""
    executor = AutoTradeExecutor()
    await executor.run_demo_mode()


if __name__ == "__main__":
    asyncio.run(main())
