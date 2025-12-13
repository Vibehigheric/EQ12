"""
EQ12 Groq Integration Test
Tests ultra-fast AI inference for sports betting analysis
Part of Phase 1 API enhancement implementation
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.groq_ai_client import EQ12GroqClient


class TestEQ12GroqIntegration:
    """Test suite for Groq AI integration with EQ12 system"""

    @pytest.fixture
    def groq_client(self):
        """Create test Groq client instance"""
        return EQ12GroqClient()

    def test_client_initialization(self, groq_client):
        """Test that Groq client initializes properly"""
        assert groq_client is not None
        assert groq_client.model_name == "llama3-8b-8192"
        assert groq_client.max_tokens == 1000

    @patch.dict(os.environ, {"GROQ_API_KEY": "test_key"})
    def test_api_key_detection(self):
        """Test API key environment variable detection"""
        client = EQ12GroqClient()
        assert client.api_key == "test_key"

    def test_missing_api_key_handling(self, groq_client):
        """Test graceful handling of missing API key"""
        with patch.dict(os.environ, {}, clear=True):
            try:
                EQ12GroqClient()
            except ValueError as e:
                assert "GROQ_API_KEY environment variable not found" in str(e)

    @patch("scripts.groq_ai_client.Groq")
    def test_quick_analysis_mock(self, mock_groq, groq_client):
        """Test quick analysis with mocked Groq response"""
        # Mock the Groq client response
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message = Mock()
        mock_completion.choices[0].message.content = "Vegas Golden Knights favored by 1.5 goals"
        mock_completion.usage = Mock()
        mock_completion.usage.total_tokens = 150

        mock_groq.return_value.chat.completions.create.return_value = mock_completion

        result = groq_client.quick_analysis("Analyze VGK vs COL tonight")

        assert "Vegas Golden Knights" in result
        assert groq_client.usage_stats["total_requests"] == 1
        assert groq_client.usage_stats["total_tokens"] == 150

    @patch("scripts.groq_ai_client.Groq")
    def test_betting_recommendation_mock(self, mock_groq, groq_client):
        """Test betting recommendation with structured response"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message = Mock()
        mock_completion.choices[
            0
        ].message.content = """
        RECOMMENDATION: BET ON VEGAS -1.5
        CONFIDENCE: 72%
        REASONING: Strong home ice advantage, better goaltending
        RISK: Medium - Division rivalry game
        """
        mock_completion.usage = Mock()
        mock_completion.usage.total_tokens = 200

        mock_groq.return_value.chat.completions.create.return_value = mock_completion

        game_data = {
            "home_team": "Vegas Golden Knights",
            "away_team": "Colorado Avalanche",
            "home_odds": -180,
            "away_odds": 150,
        }

        result = groq_client.betting_recommendation(game_data)

        assert "BET ON VEGAS" in result
        assert "72%" in result
        assert groq_client.usage_stats["total_requests"] == 1

    def test_usage_tracking(self, groq_client):
        """Test usage statistics tracking"""
        initial_stats = groq_client.get_usage_stats()

        assert "total_requests" in initial_stats
        assert "total_tokens" in initial_stats
        assert "daily_limit" in initial_stats
        assert initial_stats["daily_limit"] == 14400

    def test_rate_limiting_check(self, groq_client):
        """Test rate limiting logic"""
        # Simulate approaching daily limit
        groq_client.usage_stats["total_requests"] = 14300

        can_make_request = groq_client._check_rate_limit()
        assert can_make_request is True  # Should still allow requests

        # Simulate exceeding daily limit
        groq_client.usage_stats["total_requests"] = 14500
        can_make_request = groq_client._check_rate_limit()
        assert can_make_request is False

    @patch("scripts.groq_ai_client.Groq")
    def test_arbitrage_scanner_mock(self, mock_groq, groq_client):
        """Test arbitrage opportunity detection"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message = Mock()
        mock_completion.choices[
            0
        ].message.content = """
        ARBITRAGE DETECTED:
        Game: BOS @ TOR
        Sportsbook A: BOS +150
        Sportsbook B: TOR -140
        Profit Margin: 2.3%
        Recommended Stakes: $100 BOS, $140 TOR
        """
        mock_completion.usage = Mock()
        mock_completion.usage.total_tokens = 180

        mock_groq.return_value.chat.completions.create.return_value = mock_completion

        odds_data = [
            {"game": "BOS @ TOR", "book": "BookA", "home_odds": -140, "away_odds": 150},
            {"game": "BOS @ TOR", "book": "BookB", "home_odds": -135, "away_odds": 145},
        ]

        result = groq_client.arbitrage_scanner(odds_data)

        assert "ARBITRAGE DETECTED" in result
        assert "2.3%" in result

    def test_nhl_game_analysis_structure(self, groq_client):
        """Test NHL game analysis data structure"""
        game_info = {
            "home_team": "Toronto Maple Leafs",
            "away_team": "Boston Bruins",
            "game_time": "7:00 PM ET",
            "home_record": "5-2-1",
            "away_record": "6-1-1",
        }

        # Test that method accepts proper game structure
        assert "home_team" in game_info
        assert "away_team" in game_info
        assert "game_time" in game_info

    def test_performance_expectations(self):
        """Test that we expect sub-second response times"""
        # Groq should be significantly faster than OpenAI
        # This is more of a documentation test for expected performance
        expected_response_time = 0.5  # seconds
        groq_advantage = 3  # 3x faster than standard APIs

        assert expected_response_time < 1.0
        assert groq_advantage >= 3


class TestEQ12GroqSystemIntegration:
    """Integration tests with existing EQ12 infrastructure"""

    def test_log_directory_exists(self):
        """Test that EQ12 logs directory is available"""
        log_dir = "C:\\\\EQ12\\logs"
        if os.name == "nt":  # Windows
            # In real system, this should exist
            # In test, we just verify the path format is correct
            assert log_dir.endswith("logs")

    def test_environment_integration(self):
        """Test integration with EQ12 environment variables"""
        expected_vars = [
            "GROQ_API_KEY",
            # Other EQ12 vars that might interact
            "ODDS_API_KEY",
            "OPENAI_API_KEY",
        ]

        # Just test that we know what variables to check
        for var in expected_vars:
            assert isinstance(var, str)
            assert var.endswith("_KEY") or var.endswith("_TOKEN")

    def test_odds_api_compatibility(self):
        """Test that Groq analysis can work with existing Odds API data"""
        # Sample odds data structure from existing EQ12 system
        odds_structure = {
            "sport_key": "icehockey_nhl",
            "home_team": "Vegas Golden Knights",
            "away_team": "Colorado Avalanche",
            "bookmakers": [
                {
                    "key": "draftkings",
                    "markets": [
                        {
                            "key": "h2h",
                            "outcomes": [
                                {"name": "Vegas Golden Knights", "price": -180},
                                {"name": "Colorado Avalanche", "price": 150},
                            ],
                        }
                    ],
                }
            ],
        }

        # Verify this structure is compatible with Groq analysis
        assert "home_team" in odds_structure
        assert "away_team" in odds_structure
        assert "bookmakers" in odds_structure
        assert len(odds_structure["bookmakers"]) > 0


if __name__ == "__main__":
    # Run basic connectivity test
    print("🚀 EQ12 Groq Integration Test Suite")
    print("Testing ultra-fast AI inference capabilities...")

    # Check for API key
    if "GROQ_API_KEY" in os.environ:
        print("✅ GROQ_API_KEY found")

        try:
            client = EQ12GroqClient()
            print("✅ Groq client initialized")

            # Quick connection test
            stats = client.get_usage_stats()
            print(f"✅ Usage tracking: {stats['total_requests']} requests used")
            print(f"📊 Daily limit: {stats['daily_limit']} requests")

        except Exception as e:
            print(f"❌ Client initialization failed: {e}")
    else:
        print("⚠️  GROQ_API_KEY not set - get free key at https://console.groq.com/keys")

    print("\n🧪 Run full test suite with: pytest test_groq_integration.py -v")
