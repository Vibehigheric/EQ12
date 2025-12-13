#!/usr/bin/env python3
"""
Test suite for EQ12 Professional Sports Betting Engine
Comprehensive testing of all betting system components

Author: EQ12 Expert System
Version: 1.0
"""

import asyncio
import json
import sqlite3
import sys
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from eq12_pro_sports_betting import (
        BettingEdge,
        BetType,
        EQ12SportsBettingEngine,
        GameContext,
        GameInfo,
        OddsSnapshot,
        Sport,
        TeamRating,
        WeatherCondition,
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure eq12_pro_sports_betting.py is in the same directory")
    sys.exit(1)


class TestEQ12SportsBetting(unittest.TestCase):
    """Comprehensive test suite for sports betting engine"""

    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_dir = Path(tempfile.mkdtemp(prefix="eq12_test_"))
        cls.config_dir = cls.test_dir / "configs"
        cls.logs_dir = cls.test_dir / "logs"

        # Create directories
        cls.config_dir.mkdir(parents=True, exist_ok=True)
        cls.logs_dir.mkdir(parents=True, exist_ok=True)

        # Create test config
        cls.test_config = {
            "starting_bankroll": 1000,
            "max_bet_percentage": 0.05,
            "min_edge": 0.02,
            "min_odds": 1.5,
            "max_daily_loss": 0.1,
            "kelly_fraction": 0.25,
            "supported_sports": ["NFL", "NBA", "MLB"],
            "bookmakers": ["fanduel", "draftkings", "betmgm"],
            "auto_bet_enabled": False,
        }

        config_file = cls.config_dir / "sports_betting_config.json"
        with open(config_file, "w") as f:
            json.dump(cls.test_config, f, indent=2)

    def setUp(self):
        """Set up each test"""
        # Mock the base directory to use our test directory
        with patch("eq12_pro_sports_betting.Path") as mock_path:
            mock_path.return_value = self.test_dir
            self.engine = EQ12SportsBettingEngine(
                config_path=self.config_dir / "sports_betting_config.json"
            )

    def test_engine_initialization(self):
        """Test engine initialization"""
        self.assertIsInstance(self.engine, EQ12SportsBettingEngine)
        self.assertEqual(self.engine.config["starting_bankroll"], 1000)
        self.assertEqual(len(self.engine.config["supported_sports"]), 3)

        # Test database initialization
        self.assertTrue(self.engine.db_path.exists())

        # Test database schema
        conn = sqlite3.connect(str(self.engine.db_path))
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        conn.close()

        expected_tables = {
            "games",
            "odds_snapshots",
            "team_ratings",
            "betting_edges",
            "bets",
            "injury_reports",
            "twitter_sentiment",
            "bankroll_history",
            "performance_metrics",
        }

        table_names = {table[0] for table in tables}
        self.assertTrue(expected_tables.issubset(table_names))

    def test_seasonal_context(self):
        """Test seasonal context detection"""
        # Test NFL regular season
        nfl_date = datetime(2024, 10, 15)  # October
        context = self.engine.get_seasonal_context(Sport.NFL, nfl_date)

        self.assertEqual(context["phase"], "regular")
        self.assertEqual(context["context"], GameContext.REGULAR)
        self.assertIn("week", context)

        # Test NBA season
        nba_date = datetime(2024, 11, 15)  # November
        nba_context = self.engine.get_seasonal_context(Sport.NBA, nba_date)

        self.assertEqual(nba_context["phase"], "regular")

    def test_odds_snapshot_creation(self):
        """Test odds snapshot data structure"""
        snapshot = OddsSnapshot(
            game_id="test_game_1",
            bookmaker="fanduel",
            bet_type=BetType.MONEYLINE,
            selection="Kansas City Chiefs",
            odds=1.91,
            point=None,
        )

        self.assertEqual(snapshot.game_id, "test_game_1")
        self.assertEqual(snapshot.bookmaker, "fanduel")
        self.assertEqual(snapshot.bet_type, BetType.MONEYLINE)
        self.assertEqual(snapshot.odds, 1.91)
        self.assertIsInstance(snapshot.timestamp, datetime)

    def test_demo_odds_generation(self):
        """Test demo odds generation"""
        demo_odds = self.engine._generate_demo_odds(Sport.NFL)

        self.assertGreater(len(demo_odds), 0)

        # Check odds structure
        for odds in demo_odds[:5]:  # Check first 5
            self.assertIsInstance(odds, OddsSnapshot)
            self.assertTrue(odds.game_id.startswith("demo_"))
            self.assertIn(odds.bookmaker, self.engine.config["bookmakers"])
            self.assertGreater(odds.odds, 1.0)
            self.assertLess(odds.odds, 10.0)  # Reasonable odds range

    def test_kelly_calculation(self):
        """Test Kelly Criterion stake calculation"""
        # Test profitable bet
        odds = 2.0  # Even money
        true_prob = 0.6  # 60% chance to win

        kelly_stake = self.engine.calculate_kelly_stake(odds, true_prob)

        self.assertGreater(kelly_stake, 0)
        self.assertLessEqual(kelly_stake, float(self.engine.bankroll) * 0.25)  # Max quarter Kelly

        # Test unprofitable bet
        unprofitable_kelly = self.engine.calculate_kelly_stake(2.0, 0.4)
        self.assertEqual(unprofitable_kelly, 0)

        # Test edge case: zero probability
        zero_kelly = self.engine.calculate_kelly_stake(2.0, 0.0)
        self.assertEqual(zero_kelly, 0)

    def test_fair_value_calculation(self):
        """Test fair value calculation"""
        # Create test game
        game_info = GameInfo(
            game_id="test_fair_value",
            sport=Sport.NFL,
            home_team="Kansas City Chiefs",
            away_team="Buffalo Bills",
            commence_time=datetime.now(UTC) + timedelta(hours=24),
        )

        # Insert test game into database
        conn = sqlite3.connect(str(self.engine.db_path))
        conn.execute(
            """
        INSERT INTO games (
            game_id, sport, home_team, away_team, commence_time
        ) VALUES (?, ?, ?, ?, ?)
        """,
            (
                game_info.game_id,
                game_info.sport.value,
                game_info.home_team,
                game_info.away_team,
                game_info.commence_time.isoformat(),
            ),
        )
        conn.commit()
        conn.close()

        # Test fair value calculation
        fair_value, reasoning = self.engine.calculate_fair_value(
            game_info.game_id, BetType.MONEYLINE, game_info.home_team
        )

        self.assertGreater(fair_value, 0)
        self.assertIsInstance(reasoning, str)
        self.assertGreater(len(reasoning), 10)

    def test_edge_detection(self):
        """Test betting edge detection"""
        # Generate demo odds
        demo_odds = self.engine._generate_demo_odds(Sport.NFL)

        # Create games in database for edge detection
        conn = sqlite3.connect(str(self.engine.db_path))
        for i in range(3):
            conn.execute(
                """
            INSERT OR IGNORE INTO games (
                game_id, sport, home_team, away_team, commence_time
            ) VALUES (?, ?, ?, ?, ?)
            """,
                (
                    f"demo_americanfootball_nfl_{i}",
                    "americanfootball_nfl",
                    "Team Home",
                    "Team Away",
                    datetime.now(UTC).isoformat(),
                ),
            )
        conn.commit()
        conn.close()

        # Detect edges
        edges = self.engine.detect_betting_edges(demo_odds)

        # Validate edges
        for edge in edges:
            self.assertIsInstance(edge, BettingEdge)
            self.assertGreater(edge.odds, 1.0)
            self.assertGreater(edge.fair_value, 0)
            self.assertGreaterEqual(edge.confidence, 0)
            self.assertLessEqual(edge.confidence, 1)
            self.assertIsInstance(edge.reasoning, str)

    def test_team_rating_structure(self):
        """Test team rating data structure"""
        rating = TeamRating(
            team="Kansas City Chiefs",
            sport=Sport.NFL,
            overall_rating=1650.0,
            offensive_rating=1700.0,
            defensive_rating=1600.0,
            home_advantage=120.0,
            recent_form=0.7,
            injury_impact=-0.1,
            fatigue_factor=0.0,
            motivation_factor=0.1,
        )

        self.assertEqual(rating.team, "Kansas City Chiefs")
        self.assertEqual(rating.sport, Sport.NFL)
        self.assertGreater(rating.overall_rating, 0)
        self.assertGreaterEqual(rating.recent_form, 0)
        self.assertLessEqual(rating.recent_form, 1)

    def test_odds_storage(self):
        """Test odds snapshot storage"""
        # Create test odds
        test_odds = [
            OddsSnapshot(
                game_id="test_storage",
                bookmaker="fanduel",
                bet_type=BetType.MONEYLINE,
                selection="Test Team",
                odds=1.95,
            )
        ]

        # Store odds
        self.engine._save_odds_snapshots(test_odds)

        # Verify storage
        conn = sqlite3.connect(str(self.engine.db_path))
        stored_odds = conn.execute(
            "SELECT * FROM odds_snapshots WHERE game_id = ?", ("test_storage",)
        ).fetchall()
        conn.close()

        self.assertEqual(len(stored_odds), 1)
        self.assertEqual(stored_odds[0][1], "test_storage")  # game_id
        self.assertEqual(stored_odds[0][2], "fanduel")  # bookmaker

    def test_betting_edge_storage(self):
        """Test betting edge storage"""
        # Create test edge
        test_edge = BettingEdge(
            game_id="test_edge_storage",
            selection="Test Selection",
            bookmaker="draftkings",
            bet_type=BetType.SPREAD,
            odds=1.91,
            fair_value=2.10,
            edge_percentage=0.05,
            kelly_stake=25.0,
            confidence=0.75,
            reasoning="Test reasoning",
            expiry=datetime.now(UTC) + timedelta(hours=2),
        )

        # Store edge
        self.engine.save_betting_edges([test_edge])

        # Verify storage
        conn = sqlite3.connect(str(self.engine.db_path))
        stored_edges = conn.execute(
            "SELECT * FROM betting_edges WHERE game_id = ?", ("test_edge_storage",)
        ).fetchall()
        conn.close()

        self.assertEqual(len(stored_edges), 1)
        self.assertEqual(stored_edges[0][1], "test_edge_storage")  # game_id
        self.assertEqual(stored_edges[0][4], BetType.SPREAD.value)  # bet_type

    @patch("requests.get")
    async def test_live_odds_fetch(self, mock_get):
        """Test live odds fetching with mocked API"""
        # Mock API response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {
                "id": "test_api_game",
                "bookmakers": [
                    {
                        "key": "fanduel",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Team A", "price": 1.90},
                                    {"name": "Team B", "price": 1.95},
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
        mock_get.return_value = mock_response

        # Set API key to trigger real API call logic
        self.engine.odds_api_key = "test_key"

        # Fetch odds
        odds = await self.engine.fetch_live_odds(Sport.NFL)

        # Verify results
        self.assertGreater(len(odds), 0)
        for odds_item in odds:
            self.assertIsInstance(odds_item, OddsSnapshot)
            self.assertEqual(odds_item.game_id, "test_api_game")

    async def test_full_analysis_cycle(self):
        """Test complete analysis cycle"""
        # Run analysis
        results = await self.engine.run_full_analysis_cycle([Sport.NFL])

        # Verify results structure
        self.assertIn("timestamp", results)
        self.assertIn("sports_analyzed", results)
        self.assertIn("total_edges", results)
        self.assertIn("recommended_bets", results)
        self.assertIn("alerts", results)

        # Verify data types
        self.assertIsInstance(results["sports_analyzed"], int)
        self.assertIsInstance(results["total_edges"], int)
        self.assertIsInstance(results["recommended_bets"], list)
        self.assertIsInstance(results["alerts"], list)

    async def test_injury_report_fetch(self):
        """Test injury report fetching"""
        injuries = await self.engine.fetch_injury_reports(Sport.NFL)

        self.assertIsInstance(injuries, list)
        if injuries:  # If demo data is returned
            for injury in injuries:
                self.assertIn("team", injury)
                self.assertIn("player_name", injury)
                self.assertIn("impact_rating", injury)

    async def test_weather_data_fetch(self):
        """Test weather data fetching"""
        weather = await self.engine.fetch_weather_data("Arrowhead Stadium", datetime.now())

        self.assertIsInstance(weather, dict)
        self.assertIn("temperature", weather)
        self.assertIn("condition", weather)

    async def test_twitter_sentiment_analysis(self):
        """Test Twitter sentiment analysis"""
        sentiment = await self.engine.analyze_twitter_sentiment("test_game", ["Team A", "Team B"])

        self.assertIsInstance(sentiment, dict)
        self.assertIn("sentiment_score", sentiment)
        self.assertIn("tweet_volume", sentiment)

    def test_performance_summary(self):
        """Test performance summary generation"""
        # Add some test betting data
        conn = sqlite3.connect(str(self.engine.db_path))

        # Insert test edge
        conn.execute(
            """
        INSERT INTO betting_edges (
            game_id, selection, bookmaker, bet_type, odds, fair_value,
            edge_percentage, kelly_stake, confidence, reasoning, expiry
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "test_perf",
                "Test Selection",
                "fanduel",
                "h2h",
                1.95,
                2.10,
                0.05,
                50.0,
                0.8,
                "Test",
                datetime.now(UTC).isoformat(),
            ),
        )

        edge_id = conn.lastrowid

        # Insert test bet
        conn.execute(
            """
        INSERT INTO bets (
            game_id, selection, bookmaker, bet_type, odds, stake,
            potential_return, edge_id, bet_time, result, profit_loss
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "test_perf",
                "Test Selection",
                "fanduel",
                "h2h",
                1.95,
                50.0,
                97.5,
                edge_id,
                datetime.now(UTC).isoformat(),
                "win",
                47.5,
            ),
        )

        conn.commit()
        conn.close()

        # Get performance summary
        performance = self.engine.get_performance_summary(30)

        self.assertIn("total_bets", performance)
        self.assertIn("win_rate", performance)
        self.assertIn("total_profit", performance)
        self.assertEqual(performance["total_bets"], 1)

    async def test_daily_report_generation(self):
        """Test daily report generation"""
        report = await self.engine.generate_daily_report()

        self.assertIsInstance(report, str)
        self.assertIn("EQ12 Daily Sports Betting Report", report)
        self.assertIn("Performance", report)
        self.assertIn("Opportunities", report)

    def test_config_loading(self):
        """Test configuration loading and validation"""
        # Test with existing config
        self.assertEqual(self.engine.config["starting_bankroll"], 1000)
        self.assertEqual(len(self.engine.config["bookmakers"]), 3)

        # Test config validation
        required_keys = [
            "starting_bankroll",
            "max_bet_percentage",
            "min_edge",
            "supported_sports",
            "bookmakers",
        ]

        for key in required_keys:
            self.assertIn(key, self.engine.config)

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        import shutil

        try:
            shutil.rmtree(str(cls.test_dir))
        except:
            pass  # Ignore cleanup errors


class TestSportEnums(unittest.TestCase):
    """Test sport-related enumerations"""

    def test_sport_enum(self):
        """Test Sport enumeration"""
        self.assertEqual(Sport.NFL.value, "americanfootball_nfl")
        self.assertEqual(Sport.NBA.value, "basketball_nba")
        self.assertEqual(Sport.MLB.value, "baseball_mlb")

        # Test enum membership
        sports = [Sport.NFL, Sport.NBA, Sport.MLB, Sport.NHL, Sport.EPL]
        self.assertEqual(len(sports), 5)

    def test_bet_type_enum(self):
        """Test BetType enumeration"""
        self.assertEqual(BetType.MONEYLINE.value, "h2h")
        self.assertEqual(BetType.SPREAD.value, "spreads")
        self.assertEqual(BetType.TOTALS.value, "totals")

    def test_weather_condition_enum(self):
        """Test WeatherCondition enumeration"""
        conditions = list(WeatherCondition)
        self.assertIn(WeatherCondition.CLEAR, conditions)
        self.assertIn(WeatherCondition.RAIN, conditions)
        self.assertIn(WeatherCondition.SNOW, conditions)

    def test_game_context_enum(self):
        """Test GameContext enumeration"""
        contexts = list(GameContext)
        self.assertIn(GameContext.REGULAR, contexts)
        self.assertIn(GameContext.PLAYOFFS, contexts)
        self.assertIn(GameContext.RIVALRY, contexts)


def run_async_test(coro):
    """Helper to run async tests"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def run_tests():
    """Run all tests with detailed output"""
    print("🏆 EQ12 Sports Betting Engine Test Suite")
    print("=" * 50)

    # Create test suite
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTest(unittest.makeSuite(TestEQ12SportsBetting))
    suite.addTest(unittest.makeSuite(TestSportEnums))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2, stream=sys.stdout, descriptions=True, failfast=False
    )

    print("\n🔍 Running comprehensive test suite...")
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"✅ Tests Run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"🚨 Errors: {len(result.errors)}")
    print(f"⏭️  Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")

    success_rate = (
        ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
        if result.testsRun > 0
        else 0
    )
    print(f"📈 Success Rate: {success_rate:.1f}%")

    # Show failures if any
    if result.failures:
        print(f"\n💥 Failures ({len(result.failures)}):")
        for i, (test, _traceback) in enumerate(result.failures, 1):
            print(f"  {i}. {test}")

    if result.errors:
        print(f"\n🚨 Errors ({len(result.errors)}):")
        for i, (test, _traceback) in enumerate(result.errors, 1):
            print(f"  {i}. {test}")

    print("\n🎉 Test suite execution complete!")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
