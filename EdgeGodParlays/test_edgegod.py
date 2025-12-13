#!/usr/bin/env python3
"""
EdgeGod Expert Engine Test Suite
Comprehensive testing for the advanced odds analysis system
"""

import os
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Import the engine components
from edgegod_expert_engine import (
    BankrollManager,
    EdgeGodExpertEngine,
    MLBExpertAnalyzer,
    ParlayConstructor,
    TelegramAlerter,
    app,
)

# Test configuration
TEST_BANKROLL = 1000.0
TEST_ODDS_API_KEY = "test_key"
TEST_TELEGRAM_TOKEN = "test_token"
TEST_CHAT_ID = "test_chat"


@pytest.fixture
def mock_env():
    """Mock environment variables for testing"""
    env_vars = {
        "BANKROLL_BASE": str(TEST_BANKROLL),
        "ODDS_API_KEY": TEST_ODDS_API_KEY,
        "TELEGRAM_BOT_TOKEN": TEST_TELEGRAM_TOKEN,
        "TELEGRAM_CHAT_ID": TEST_CHAT_ID,
        "MIN_EDGE_THRESHOLD": "0.02",
        "MAX_SINGLE_BET_PERCENTAGE": "0.05",
        "KELLY_FRACTION": "0.25",
    }

    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def bankroll_manager():
    """Create BankrollManager instance for testing"""
    return BankrollManager(
        base_bankroll=TEST_BANKROLL, max_bet_percentage=0.05, kelly_fraction=0.25
    )


@pytest.fixture
def mlb_analyzer():
    """Create MLBExpertAnalyzer instance for testing"""
    return MLBExpertAnalyzer(TEST_ODDS_API_KEY)


@pytest.fixture
def parlay_constructor():
    """Create ParlayConstructor instance for testing"""
    return ParlayConstructor()


@pytest.fixture
def telegram_alerter():
    """Create TelegramAlerter instance for testing"""
    return TelegramAlerter(TEST_TELEGRAM_TOKEN, TEST_CHAT_ID)


@pytest.fixture
def expert_engine(mock_env):
    """Create EdgeGodExpertEngine instance for testing"""
    return EdgeGodExpertEngine()


# Bankroll Manager Tests
class TestBankrollManager:

    def test_initialization(self, bankroll_manager):
        """Test bankroll manager initialization"""
        assert bankroll_manager.current_bankroll == TEST_BANKROLL
        assert bankroll_manager.max_bet_percentage == 0.05
        assert bankroll_manager.kelly_fraction == 0.25

    def test_kelly_sizing_positive_edge(self, bankroll_manager):
        """Test Kelly criterion with positive edge"""
        # Test with 5% edge, -110 odds
        probability = 0.55  # 55% chance
        decimal_odds = 1.909  # -110 in decimal

        sizing = bankroll_manager.calculate_kelly_sizing(probability, decimal_odds)

        assert sizing["edge"] > 0
        assert sizing["kelly_percentage"] > 0
        assert sizing["recommended_bet"] > 0
        assert sizing["recommended_bet"] <= TEST_BANKROLL * 0.05

    def test_kelly_sizing_negative_edge(self, bankroll_manager):
        """Test Kelly criterion with negative edge"""
        # Test with negative edge
        probability = 0.45  # 45% chance
        decimal_odds = 1.909  # -110 in decimal

        sizing = bankroll_manager.calculate_kelly_sizing(probability, decimal_odds)

        assert sizing["edge"] < 0
        assert sizing["kelly_percentage"] == 0
        assert sizing["recommended_bet"] == 0

    def test_bet_tracking(self, bankroll_manager):
        """Test bet placement and tracking"""
        bet_amount = 50.0
        outcome = "win"
        profit = 45.45  # Win $45.45 on -110 bet

        bankroll_manager.place_bet(bet_amount, outcome, profit)

        # Check bankroll updated correctly
        expected_bankroll = TEST_BANKROLL + profit
        assert bankroll_manager.current_bankroll == expected_bankroll

        # Check bet recorded
        assert len(bankroll_manager.bet_history) == 1
        bet_record = bankroll_manager.bet_history[0]
        assert bet_record["amount"] == bet_amount
        assert bet_record["outcome"] == outcome
        assert bet_record["profit"] == profit

    def test_bankroll_protection(self, bankroll_manager):
        """Test bankroll protection limits"""
        # Try to bet more than max percentage
        large_bet = TEST_BANKROLL * 0.10  # 10% of bankroll

        sizing = bankroll_manager.calculate_kelly_sizing(0.60, 2.0)  # High edge scenario

        # Should be capped at max percentage
        assert sizing["recommended_bet"] <= TEST_BANKROLL * 0.05


# MLB Analyzer Tests
class TestMLBExpertAnalyzer:

    @pytest.mark.asyncio
    async def test_injury_analysis(self, mlb_analyzer):
        """Test injury list analysis"""
        # Mock injury data
        mock_injuries = [{"player": "Test Player", "team": "TEST", "status": "10-day IL"}]

        with patch.object(mlb_analyzer, "_fetch_injury_list", return_value=mock_injuries):
            injuries = await mlb_analyzer.analyze_injuries("TEST")

            assert len(injuries) == 1
            assert injuries[0]["player"] == "Test Player"

    @pytest.mark.asyncio
    async def test_game_analysis(self, mlb_analyzer):
        """Test comprehensive game analysis"""
        # Mock game data
        mock_game = {
            "id": "test_game_123",
            "home_team": "NYY",
            "away_team": "BOS",
            "commence_time": "2024-01-15T19:00:00Z",
        }

        mock_odds = {"h2h": [{"name": "NYY", "price": -110}, {"name": "BOS", "price": +100}]}

        with (
            patch.object(mlb_analyzer, "_fetch_game_odds", return_value=mock_odds),
            patch.object(mlb_analyzer, "analyze_injuries", return_value=[]),
        ):

            analysis = await mlb_analyzer.analyze_game(mock_game)

            assert analysis["game_id"] == "test_game_123"
            assert "value_bets" in analysis
            assert "injury_impact" in analysis


# Parlay Constructor Tests
class TestParlayConstructor:

    def test_correlation_detection(self, parlay_constructor):
        """Test correlation detection between bets"""
        # Test same game correlation (should be high)
        bet1 = {"game_id": "game_1", "bet_type": "moneyline", "team": "home"}
        bet2 = {"game_id": "game_1", "bet_type": "total", "selection": "over"}

        correlation = parlay_constructor.calculate_correlation(bet1, bet2)
        assert abs(correlation) > 0  # Should have some correlation

        # Test different game correlation (should be lower)
        bet3 = {"game_id": "game_2", "bet_type": "moneyline", "team": "away"}
        correlation = parlay_constructor.calculate_correlation(bet1, bet3)
        assert abs(correlation) < 0.5  # Should have low correlation

    def test_parlay_construction(self, parlay_constructor):
        """Test parlay construction with correlation limits"""
        # Mock value bets
        value_bets = [
            {
                "game_id": "game_1",
                "bet_type": "moneyline",
                "team": "NYY",
                "odds": -110,
                "probability": 0.55,
                "edge": 0.03,
            },
            {
                "game_id": "game_2",
                "bet_type": "moneyline",
                "team": "BOS",
                "odds": +100,
                "probability": 0.52,
                "edge": 0.04,
            },
            {
                "game_id": "game_1",  # Same game - should be filtered
                "bet_type": "total",
                "selection": "over",
                "odds": -105,
                "probability": 0.53,
                "edge": 0.025,
            },
        ]

        parlay = parlay_constructor.construct_optimal_parlay(
            value_bets, max_legs=3, min_edge=0.02, max_correlation=0.3
        )

        # Should filter out highly correlated same-game bets
        assert len(parlay["legs"]) <= 2
        assert parlay["expected_value"] > 0


# Telegram Alerter Tests
class TestTelegramAlerter:

    @pytest.mark.asyncio
    async def test_alert_sending(self, telegram_alerter):
        """Test Telegram alert functionality"""
        mock_response = Mock()
        mock_response.json = AsyncMock(return_value={"ok": True, "result": {}})

        with patch("aiohttp.ClientSession.post", return_value=mock_response):
            success = await telegram_alerter.send_alert("Test message", "INFO")
            assert success

    def test_alert_formatting(self, telegram_alerter):
        """Test alert message formatting"""
        bet_data = {"team": "NYY", "odds": -110, "edge": 0.05, "recommended_bet": 25.0}

        message = telegram_alerter.format_bet_alert(bet_data)

        assert "NYY" in message
        assert "-110" in message
        assert "5.0%" in message  # Edge percentage
        assert "$25.00" in message


# Expert Engine Integration Tests
class TestEdgeGodExpertEngine:

    @pytest.mark.asyncio
    async def test_engine_initialization(self, expert_engine):
        """Test engine initialization"""
        assert expert_engine.bankroll_manager is not None
        assert expert_engine.mlb_analyzer is not None
        assert expert_engine.parlay_constructor is not None
        assert expert_engine.telegram_alerter is not None

    @pytest.mark.asyncio
    async def test_full_slate_analysis(self, expert_engine):
        """Test complete slate analysis workflow"""
        # Mock API responses
        mock_games = [
            {
                "id": "game_1",
                "sport_key": "baseball_mlb",
                "home_team": "NYY",
                "away_team": "BOS",
                "commence_time": "2024-01-15T19:00:00Z",
            }
        ]

        with (
            patch.object(expert_engine.mlb_analyzer, "_fetch_games", return_value=mock_games),
            patch.object(expert_engine.mlb_analyzer, "analyze_game") as mock_analyze,
        ):

            mock_analyze.return_value = {
                "game_id": "game_1",
                "value_bets": [
                    {
                        "bet_type": "moneyline",
                        "team": "NYY",
                        "odds": -110,
                        "probability": 0.55,
                        "edge": 0.03,
                    }
                ],
                "injury_impact": [],
            }

            results = await expert_engine.analyze_full_slate("2024-01-15")

            assert "summary" in results
            assert "games" in results
            assert results["summary"]["total_games"] == 1


# API Endpoint Tests
class TestAPIEndpoints:

    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app"""
        from fastapi.testclient import TestClient

        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_analyze_slate_endpoint(self, client):
        """Test slate analysis endpoint"""
        with patch("edgegod_expert_engine.expert_engine") as mock_engine:
            mock_engine.analyze_full_slate = AsyncMock(
                return_value={
                    "summary": {"total_games": 5, "value_bets_found": 2},
                    "games": [],
                }
            )

            response = client.post("/analyze/slate/today")
            assert response.status_code == 200

            data = response.json()
            assert data["summary"]["total_games"] == 5


# Performance Tests
class TestPerformance:

    @pytest.mark.asyncio
    async def test_analysis_speed(self, expert_engine):
        """Test analysis performance requirements"""
        start_time = datetime.now()

        # Mock fast responses
        with (
            patch.object(expert_engine.mlb_analyzer, "_fetch_games", return_value=[]),
            patch.object(expert_engine.mlb_analyzer, "analyze_game", return_value={}),
        ):

            await expert_engine.analyze_full_slate("2024-01-15")

        elapsed = (datetime.now() - start_time).total_seconds()

        # Analysis should complete within reasonable time
        assert elapsed < 10.0  # 10 seconds max


# Data Validation Tests
class TestDataValidation:

    def test_odds_validation(self, mlb_analyzer):
        """Test odds data validation"""
        # Test valid American odds
        assert mlb_analyzer._validate_odds(-110) == True
        assert mlb_analyzer._validate_odds(+150) == True

        # Test invalid odds
        assert mlb_analyzer._validate_odds(0) == False
        assert mlb_analyzer._validate_odds(None) == False

    def test_probability_validation(self, bankroll_manager):
        """Test probability validation"""
        # Valid probabilities
        assert 0 < 0.55 < 1
        assert 0 < 0.45 < 1

        # Invalid probabilities
        invalid_probs = [-0.1, 0, 1.0, 1.5]
        for prob in invalid_probs:
            with pytest.raises((ValueError, AssertionError)):
                bankroll_manager.calculate_kelly_sizing(prob, 2.0)


# Configuration Tests
class TestConfiguration:

    def test_environment_loading(self, mock_env):
        """Test environment variable loading"""
        engine = EdgeGodExpertEngine()

        assert engine.bankroll_manager.current_bankroll == TEST_BANKROLL
        assert engine.mlb_analyzer.api_key == TEST_ODDS_API_KEY

    def test_missing_config_handling(self):
        """Test graceful handling of missing configuration"""
        # Clear environment
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises((ValueError, KeyError)):
                EdgeGodExpertEngine()


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=edgegod_expert_engine",
            "--cov-report=html",
            "--cov-report=term",
        ]
    )
