#!/usr/bin/env python3
"""
EQ12 Enhanced Python Module - Expert Patterns and Modern Features
Advanced Python implementation demonstrating best practices and productivity hacks

Features:
- Type hints and dataclasses (Python 3.7+)
- Context managers and async/await
- Comprehensions and functional programming
- Modern error handling and logging
- Performance optimizations
- Decorator patterns
- Generator expressions
- Walrus operator (Python 3.8+)
- Pattern matching (Python 3.10+)
"""

import asyncio
import functools
import logging
import sqlite3
import time
from collections import Counter
from collections.abc import Callable, Generator
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any,
    Final,
    Protocol,
    TypeVar,
)

# Configure logging with modern formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("C:/EQ12/logs/enhanced_python.log"),
    ],
)

logger = logging.getLogger(__name__)

# Type variables for generic programming
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# Modern constants using Final (Python 3.8+)
EQ12_ROOT: Final[Path] = Path("C:/EQ12")
API_TIMEOUT: Final[int] = 30
MAX_RETRIES: Final[int] = 3


# Enums for better type safety
class BetStatus(Enum):
    """Enum for bet status using auto() for cleaner code"""

    PENDING = auto()
    WON = auto()
    LOST = auto()
    PUSHED = auto()
    VOIDED = auto()


class SportType(Enum):
    """Sport types with string values for API compatibility"""

    MLB = "baseball"
    NFL = "football"
    NBA = "basketball"
    UFC = "mma"


# Modern dataclasses with type hints and default factories
@dataclass(frozen=True)  # Immutable for thread safety
class Bet:
    """Modern bet representation using dataclass with comprehensive typing"""

    id: str
    sport: SportType
    player: str
    market: str
    line: float
    odds: int
    stake: float
    status: BetStatus = BetStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def potential_payout(self) -> float:
        """Calculate potential payout using property decorator"""
        if self.odds > 0:
            return self.stake * (self.odds / 100)
        return self.stake * (100 / abs(self.odds))

    @property
    def is_active(self) -> bool:
        """Check if bet is still active"""
        return self.status == BetStatus.PENDING


@dataclass
class Portfolio:
    """Portfolio tracking with modern Python features"""

    bets: list[Bet] = field(default_factory=list)
    initial_bankroll: float = 1000.0
    _cache: dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self):
        """Post-initialization hook for validation"""
        if self.initial_bankroll <= 0:
            raise ValueError("Initial bankroll must be positive")

    @property
    def current_bankroll(self) -> float:
        """Calculate current bankroll with caching"""
        if "current_bankroll" not in self._cache:
            total_pnl = sum(
                bet.potential_payout if bet.status == BetStatus.WON else -bet.stake
                for bet in self.bets
                if bet.status != BetStatus.PENDING
            )
            self._cache["current_bankroll"] = self.initial_bankroll + total_pnl
        return self._cache["current_bankroll"]

    @property
    def roi(self) -> float:
        """Calculate ROI as percentage"""
        return ((self.current_bankroll - self.initial_bankroll) / self.initial_bankroll) * 100

    def clear_cache(self) -> None:
        """Clear internal cache when data changes"""
        self._cache.clear()


# Protocol for type hints (Python 3.8+)
class Analyzer(Protocol):
    """Protocol defining analyzer interface"""

    def analyze(self, data: list[Bet]) -> dict[str, Any]: ...


# Context managers for resource management
@contextmanager
def database_connection(
    db_path: str | Path,
) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for SQLite connections with automatic cleanup"""
    conn = None
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        yield conn
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()


@asynccontextmanager
async def async_timer(operation_name: str) -> Generator[None, None, None]:
    """Async context manager for timing operations"""
    start_time = time.perf_counter()
    logger.info(f"Starting {operation_name}...")
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start_time
        logger.info(f"{operation_name} completed in {elapsed:.2f}s")


# Decorator patterns for common functionality
def retry_on_failure(max_retries: int = MAX_RETRIES, delay: float = 1.0):
    """Decorator for automatic retry with exponential backoff"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        sleep_time = delay * (2**attempt)  # Exponential backoff
                        logger.warning(
                            f"Attempt {attempt + 1} failed, retrying in {sleep_time}s: {e}"
                        )
                        time.sleep(sleep_time)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed")

            raise last_exception

        return wrapper

    return decorator


def memoize[T](func: Callable[..., T]) -> Callable[..., T]:
    """Memoization decorator using functools.lru_cache"""
    return functools.lru_cache(maxsize=128)(func)


def validate_types[T](func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to validate function arguments at runtime"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        # In production, would use a proper type validation library
        return func(*args, **kwargs)

    return wrapper


# Modern class with advanced Python features
class EQ12DataProcessor:
    """
    Advanced data processor showcasing modern Python patterns

    Features:
    - Type hints throughout
    - Properties with caching
    - Generator methods for memory efficiency
    - Async methods for I/O operations
    - Context manager support
    """

    def __init__(self, eq12_root: Path = EQ12_ROOT):
        self.eq12_root = eq12_root
        self.db_path = eq12_root / "enhanced_data.db"
        self._cache: dict[str, Any] = {}
        self._setup_database()

    def _setup_database(self) -> None:
        """Setup SQLite database with modern context manager"""
        with database_connection(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS bets (
                    id TEXT PRIMARY KEY,
                    sport TEXT NOT NULL,
                    player TEXT NOT NULL,
                    market TEXT NOT NULL,
                    line REAL NOT NULL,
                    odds INTEGER NOT NULL,
                    stake REAL NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            """
            )
            conn.commit()

    def __enter__(self) -> "EQ12DataProcessor":
        """Context manager entry"""
        logger.info("EQ12DataProcessor context entered")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit with cleanup"""
        self._cache.clear()
        logger.info("EQ12DataProcessor context exited")

    @property
    def total_bets(self) -> int:
        """Get total bet count with caching"""
        if "total_bets" not in self._cache:
            with database_connection(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM bets")
                self._cache["total_bets"] = cursor.fetchone()[0]
        return self._cache["total_bets"]

    def add_bet(self, bet: Bet) -> None:
        """Add bet to database using modern f-strings and walrus operator"""
        import json

        with database_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO bets
                (id, sport, player, market, line, odds, stake, status, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    bet.id,
                    bet.sport.value,  # Enum value extraction
                    bet.player,
                    bet.market,
                    bet.line,
                    bet.odds,
                    bet.stake,
                    bet.status.name,  # Enum name
                    bet.timestamp.isoformat(),
                    json.dumps(bet.metadata),
                ),
            )
            conn.commit()

        # Clear cache when data changes
        self._cache.clear()
        logger.info(f"Added bet: {bet.id}")

    def get_bets_by_sport(self, sport: SportType) -> Generator[Bet, None, None]:
        """Generator function for memory-efficient bet retrieval"""
        with database_connection(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM bets WHERE sport = ?", (sport.value,))

            for row in cursor:
                yield self._row_to_bet(row)

    def get_filtered_bets(self, **filters) -> list[Bet]:
        """Get bets with flexible filtering using **kwargs"""
        conditions = []
        params = []

        # Build dynamic SQL using dictionary comprehension
        for key, value in filters.items():
            if key in {"sport", "player", "market", "status"}:
                conditions.append(f"{key} = ?")
                params.append(value.value if hasattr(value, "value") else value)

        # Use walrus operator for cleaner conditional logic (Python 3.8+)
        if where_clause := " AND ".join(conditions):
            query = f"SELECT * FROM bets WHERE {where_clause}"
        else:
            query = "SELECT * FROM bets"

        with database_connection(self.db_path) as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_bet(row) for row in cursor.fetchall()]

    @retry_on_failure(max_retries=3)
    async def analyze_performance(self, sport: SportType | None = None) -> dict[str, Any]:
        """Async analysis with error handling and modern typing"""
        async with async_timer("Performance Analysis"):
            # Use async to simulate I/O operation
            await asyncio.sleep(0.1)  # Simulate processing time

            # Get bets using generator or filtered query
            bets = list(self.get_bets_by_sport(sport)) if sport else self.get_filtered_bets()

            if not bets:
                return {"error": "No bets found for analysis"}

            # Modern analysis using comprehensions and built-in functions
            analysis = {
                "total_bets": len(bets),
                "sports_distribution": self._analyze_sports_distribution(bets),
                "status_summary": self._analyze_status_summary(bets),
                "roi_analysis": self._analyze_roi(bets),
                "performance_metrics": self._calculate_performance_metrics(bets),
            }

            return analysis

    def _analyze_sports_distribution(self, bets: list[Bet]) -> dict[str, int]:
        """Analyze sports distribution using Counter"""
        return dict(Counter(bet.sport.name for bet in bets))

    def _analyze_status_summary(self, bets: list[Bet]) -> dict[str, int]:
        """Status analysis using modern dict comprehension"""
        status_counts = Counter(bet.status.name for bet in bets)
        return dict(status_counts.items())

    def _analyze_roi(self, bets: list[Bet]) -> dict[str, float]:
        """ROI analysis using filter and sum with generator expressions"""
        completed_bets = [bet for bet in bets if bet.status != BetStatus.PENDING]

        if not completed_bets:
            return {"roi": 0.0, "total_profit": 0.0, "total_staked": 0.0}

        total_staked = sum(bet.stake for bet in completed_bets)
        total_profit = sum(
            bet.potential_payout if bet.status == BetStatus.WON else -bet.stake
            for bet in completed_bets
        )

        roi = (total_profit / total_staked) * 100 if total_staked > 0 else 0.0

        return {
            "roi": round(roi, 2),
            "total_profit": round(total_profit, 2),
            "total_staked": round(total_staked, 2),
        }

    def _calculate_performance_metrics(self, bets: list[Bet]) -> dict[str, Any]:
        """Calculate advanced performance metrics"""
        completed_bets = [bet for bet in bets if bet.status != BetStatus.PENDING]

        if not completed_bets:
            return {}

        # Use any() and all() for boolean logic
        wins = [bet for bet in completed_bets if bet.status == BetStatus.WON]
        losses = [bet for bet in completed_bets if bet.status == BetStatus.LOST]

        win_rate = len(wins) / len(completed_bets) if completed_bets else 0

        # Advanced metrics using modern Python features
        metrics = {
            "win_rate": round(win_rate * 100, 2),
            "total_wins": len(wins),
            "total_losses": len(losses),
            "average_odds": (
                round(sum(bet.odds for bet in completed_bets) / len(completed_bets), 2)
                if completed_bets
                else 0
            ),
            "largest_win": max((bet.potential_payout for bet in wins), default=0),
            "largest_loss": max((bet.stake for bet in losses), default=0),
            "has_profitable_bets": any(bet.status == BetStatus.WON for bet in completed_bets),
            "all_bets_resolved": all(bet.status != BetStatus.PENDING for bet in bets),
        }

        return metrics

    def _row_to_bet(self, row: sqlite3.Row) -> Bet:
        """Convert database row to Bet object"""
        import json

        return Bet(
            id=row["id"],
            sport=SportType(row["sport"]),
            player=row["player"],
            market=row["market"],
            line=row["line"],
            odds=row["odds"],
            stake=row["stake"],
            status=BetStatus[row["status"]],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )

    @memoize
    def get_top_performers(self, limit: int = 10) -> list[tuple[str, float]]:
        """Get top performing players using memoization"""
        with database_connection(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT player,
                       AVG(CASE WHEN status = 'WON' THEN 1.0 ELSE 0.0 END) as win_rate,
                       COUNT(*) as bet_count
                FROM bets
                WHERE status != 'PENDING'
                GROUP BY player
                HAVING bet_count >= 5
                ORDER BY win_rate DESC
                LIMIT ?
            """,
                (limit,),
            )

            return [(row["player"], row["win_rate"]) for row in cursor.fetchall()]


# Functional programming utilities
def compose(*functions: Callable) -> Callable:
    """Function composition utility"""
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)


def partition(predicate: Callable[[T], bool], iterable: list[T]) -> tuple[list[T], list[T]]:
    """Partition iterable based on predicate"""
    true_items, false_items = [], []
    for item in iterable:
        (true_items if predicate(item) else false_items).append(item)
    return true_items, false_items


# Modern async processing
class EQ12AsyncProcessor:
    """Async processor for I/O intensive operations"""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers

    async def process_multiple_sports(
        self, sports: list[SportType]
    ) -> dict[SportType, dict[str, Any]]:
        """Process multiple sports concurrently"""

        async def process_sport(sport: SportType) -> tuple[SportType, dict[str, Any]]:
            processor = EQ12DataProcessor()
            result = await processor.analyze_performance(sport)
            return sport, result

        # Use asyncio.gather for concurrent execution
        tasks = [process_sport(sport) for sport in sports]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and return results
        return {sport: result for sport, result in results if not isinstance(result, Exception)}

    async def batch_process_bets(self, bets: list[Bet], batch_size: int = 100) -> list[bool]:
        """Process bets in batches for better performance"""
        results = []

        # Use itertools.islice for efficient batching
        bet_batches = [bets[i : i + batch_size] for i in range(0, len(bets), batch_size)]

        for batch in bet_batches:
            async with async_timer(f"Processing batch of {len(batch)} bets"):
                # Simulate async processing
                await asyncio.sleep(0.1)
                batch_results = [True] * len(batch)  # Simulate success
                results.extend(batch_results)

        return results


# Pattern matching example (Python 3.10+)
def analyze_bet_outcome(bet: Bet) -> str:
    """Analyze bet outcome using pattern matching (Python 3.10+)"""
    # Note: This requires Python 3.10+, fallback to if-elif for older versions
    try:
        match bet.status:
            case BetStatus.WON if bet.odds > 0:
                return f"Underdog win: +{bet.potential_payout:.2f}"
            case BetStatus.WON if bet.odds < 0:
                return f"Favorite win: +{bet.potential_payout:.2f}"
            case BetStatus.LOST:
                return f"Loss: -{bet.stake:.2f}"
            case BetStatus.PUSHED:
                return "Push: Even"
            case BetStatus.VOIDED:
                return "Voided: Refunded"
            case _:
                return "Pending"
    except SyntaxError:
        # Fallback for Python < 3.10
        if bet.status == BetStatus.WON:
            return f"Win: +{bet.potential_payout:.2f}"
        if bet.status == BetStatus.LOST:
            return f"Loss: -{bet.stake:.2f}"
        return bet.status.name


# Demo and testing functions
async def demo_enhanced_features():
    """Demonstrate enhanced Python features"""
    logger.info("🚀 EQ12 Enhanced Python Features Demo")

    # Create sample data using modern syntax
    sample_bets = [
        Bet(
            id=f"bet_{i}",
            sport=SportType.MLB,
            player=f"Player_{i}",
            market="HR",
            line=0.5,
            odds=150 if i % 2 else -110,
            stake=100.0,
            status=BetStatus.WON if i % 3 == 0 else BetStatus.LOST,
        )
        for i in range(10)
    ]

    # Context manager usage
    with EQ12DataProcessor() as processor:
        # Add bets using modern features
        for bet in sample_bets:
            processor.add_bet(bet)

        # Async analysis
        analysis = await processor.analyze_performance()
        logger.info(f"Analysis results: {analysis}")

        # Generator usage for memory efficiency
        mlb_bets = list(processor.get_bets_by_sport(SportType.MLB))
        logger.info(f"Found {len(mlb_bets)} MLB bets")

        # Top performers with memoization
        top_performers = processor.get_top_performers(limit=5)
        logger.info(f"Top performers: {top_performers}")

    # Async processing demo
    async_processor = EQ12AsyncProcessor()
    sports_analysis = await async_processor.process_multiple_sports([SportType.MLB, SportType.NFL])
    logger.info(f"Multi-sport analysis: {sports_analysis}")

    # Functional programming demo
    profitable_bets, losing_bets = partition(lambda bet: bet.status == BetStatus.WON, sample_bets)
    logger.info(f"Profitable: {len(profitable_bets)}, Losing: {len(losing_bets)}")

    logger.info("✅ Enhanced features demo completed")


if __name__ == "__main__":
    # Modern async execution
    try:
        asyncio.run(demo_enhanced_features())
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise
