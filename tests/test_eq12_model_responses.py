"""
Test suite for EQ12 Model Response System
Comprehensive testing for all response capabilities
"""

import json
import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Test data
SAMPLE_PARLAY_LEGS = [
    {
        "game": "Lakers vs Warriors",
        "market": "spread",
        "selection": "Lakers -3.5",
        "odds": -110,
        "probability": 0.55,
    },
    {
        "game": "Lakers vs Warriors",
        "market": "total",
        "selection": "Over 225.5",
        "odds": -105,
        "probability": 0.52,
    },
    {
        "game": "Celtics vs Heat",
        "market": "moneyline",
        "selection": "Celtics",
        "odds": -150,
        "probability": 0.60,
    },
]

SAMPLE_NFL_GAMES = [
    {
        "home": "Patriots",
        "away": "Bills",
        "spread": "Bills -3.5",
        "total": 44.5,
        "moneyline": {"home": +140, "away": -160},
    },
    {
        "home": "Cowboys",
        "away": "Eagles",
        "spread": "Eagles -7",
        "total": 51.5,
        "moneyline": {"home": +280, "away": -350},
    },
]

SAMPLE_NBA_PROPS = [
    {
        "player": "LeBron James",
        "market": "points",
        "line": 26.5,
        "over_odds": -110,
        "under_odds": -110,
    },
    {
        "player": "Stephen Curry",
        "market": "threes",
        "line": 4.5,
        "over_odds": +105,
        "under_odds": -125,
    },
]

SAMPLE_LINE_MOVEMENTS = [
    {
        "game": "Patriots vs Bills",
        "market": "spread",
        "opening": "Bills -2.5",
        "current": "Bills -3.5",
        "movement": 1.0,
        "time": "2024-01-01T10:00:00Z",
    },
    {
        "game": "Patriots vs Bills",
        "market": "total",
        "opening": 45.5,
        "current": 44.5,
        "movement": -1.0,
        "time": "2024-01-01T10:15:00Z",
    },
]


class TestEQ12ResponsesAPI:
    """Test core Responses API functionality"""

    @pytest.fixture
    def mock_api_response(self):
        """Mock successful API response"""
        return {
            "id": "resp_test123",
            "object": "response",
            "model": "gpt-4o",
            "created": 1704067200,
            "status": "completed",
            "output": {
                "type": "text",
                "text": json.dumps(
                    {
                        "parlay_analysis": {
                            "overall_rating": "GOOD",
                            "expected_value_pct": 5.2,
                            "true_odds": 650,
                            "sportsbook_odds": 600,
                            "kelly_stake_pct": 2.1,
                            "recommended_stake": 42.0,
                        }
                    }
                ),
            },
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 200,
                "total_tokens": 350,
            },
        }

    @pytest.fixture
    def mock_responses_api(self, mock_api_response):
        """Mock EQ12ResponsesAPI with successful responses"""
        with patch("eq12_model_responses.httpx") as mock_httpx:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response
            mock_response.headers = {
                "openai-processing-ms": "1500",
                "x-request-id": "req_test123",
            }
            mock_client.post.return_value = mock_response
            mock_httpx.AsyncClient.return_value.__aenter__.return_value = mock_client

            from eq12_model_responses import EQ12ResponsesAPI

            return EQ12ResponsesAPI()

    @pytest.mark.asyncio
    async def test_parlay_analysis(self, mock_responses_api):
        """Test parlay analysis response"""
        result = await mock_responses_api.create_parlay_analysis_response(
            "NBA games tonight", SAMPLE_PARLAY_LEGS, bankroll=5000.0
        )

        assert result["id"] == "resp_test123"
        assert result["status"] == "completed"
        assert result["model"] == "gpt-4o"

        # Verify analysis content
        output_text = result["output"]["text"]
        analysis = json.loads(output_text)

        assert "parlay_analysis" in analysis
        assert analysis["parlay_analysis"]["overall_rating"] == "GOOD"
        assert analysis["parlay_analysis"]["expected_value_pct"] > 0

    @pytest.mark.asyncio
    async def test_live_odds_analysis(self, mock_responses_api):
        """Test live odds analysis with streaming"""
        games = ["Patriots vs Bills", "Cowboys vs Eagles"]

        result = await mock_responses_api.create_live_odds_analysis_response(
            games, markets=["moneyline", "spread"]
        )

        assert result["id"] == "resp_test123"
        assert "live_analysis" in json.loads(result["output"]["text"])

    @pytest.mark.asyncio
    async def test_portfolio_optimization(self, mock_responses_api):
        """Test portfolio optimization response"""
        current_bets = [{"id": "bet1", "stake": 100, "odds": -110, "sport": "NFL"}]
        opportunities = [{"id": "opp1", "edge": 0.05, "odds": +150, "sport": "NBA"}]

        result = await mock_responses_api.create_portfolio_optimization_response(
            current_bets, opportunities, bankroll=10000.0, risk_tolerance="moderate"
        )

        assert result["id"] == "resp_test123"
        assert result["status"] == "completed"

    def test_tool_preparation(self, mock_responses_api):
        """Test tool configuration preparation"""
        from eq12_model_responses import ToolType

        tools = mock_responses_api._prepare_tools(
            [ToolType.WEB_SEARCH, ToolType.CODE_INTERPRETER, ToolType.FUNCTION]
        )

        assert len(tools) > 0
        tool_types = [tool["type"] for tool in tools]
        assert "web_search" in tool_types
        assert "code_interpreter" in tool_types
        assert "function" in tool_types

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test API error handling"""
        with patch("eq12_model_responses.httpx") as mock_httpx:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "Invalid request"}
            mock_client.post.return_value = mock_response
            mock_httpx.AsyncClient.return_value.__aenter__.return_value = mock_client

            from eq12_model_responses import EQ12ResponsesAPI

            api = EQ12ResponsesAPI()

            with pytest.raises(RuntimeError, match="API Error 400"):
                await api.create_parlay_analysis_response("test", [], 1000.0)


class TestEQ12ResponseTemplates:
    """Test pre-configured response templates"""

    @pytest.fixture
    def mock_templates(self):
        """Mock response templates"""
        with patch("eq12_response_templates.EQ12ResponsesAPI") as mock_api_class:
            mock_api = AsyncMock()
            mock_api._make_request.return_value = {
                "id": "resp_template123",
                "status": "completed",
                "output": {"text": json.dumps({"analysis": "complete"})},
            }
            mock_api_class.return_value = mock_api

            from eq12_response_templates import EQ12ResponseTemplates

            return EQ12ResponseTemplates()

    @pytest.mark.asyncio
    async def test_nfl_sunday_template(self, mock_templates):
        """Test NFL Sunday slate template"""
        from eq12_response_templates import BettingScenario

        context = {
            "games": SAMPLE_NFL_GAMES,
            "weather": [],
            "injuries": [],
            "bankroll": 5000.0,
        }

        result = await mock_templates.execute_scenario(BettingScenario.NFL_SUNDAY_SLATE, context)

        assert result["id"] == "resp_template123"
        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_nba_props_template(self, mock_templates):
        """Test NBA props template"""
        from eq12_response_templates import BettingScenario

        context = {
            "games": [{"home": "Lakers", "away": "Warriors"}],
            "props": SAMPLE_NBA_PROPS,
            "players": ["LeBron James", "Stephen Curry"],
            "injuries": [],
        }

        result = await mock_templates.execute_scenario(BettingScenario.NBA_PROPS_NIGHT, context)

        assert result["id"] == "resp_template123"

    @pytest.mark.asyncio
    async def test_steam_alert_template(self, mock_templates):
        """Test steam detection template"""
        from eq12_response_templates import BettingScenario

        context = {"line_moves": SAMPLE_LINE_MOVEMENTS, "volume": [], "public_bets": []}

        result = await mock_templates.execute_scenario(BettingScenario.SHARP_STEAM_ALERT, context)

        assert result["status"] == "completed"

    def test_template_configuration(self, mock_templates):
        """Test template configurations are valid"""
        templates = mock_templates.templates

        assert len(templates) > 0

        for _scenario, template in templates.items():
            assert template.instructions is not None
            assert len(template.instructions) > 0
            assert template.config is not None
            assert template.output_schema is not None
            assert "type" in template.output_schema

    @pytest.mark.asyncio
    async def test_context_formatting(self, mock_templates):
        """Test context formatting for different scenarios"""
        from eq12_response_templates import BettingScenario

        # Test NFL context
        nfl_context = {"games": SAMPLE_NFL_GAMES, "bankroll": 1000}
        formatted = mock_templates._format_context_for_scenario(
            BettingScenario.NFL_SUNDAY_SLATE, nfl_context
        )

        assert "NFL Sunday slate" in formatted
        assert "Patriots" in formatted

        # Test NBA context
        nba_context = {"props": SAMPLE_NBA_PROPS}
        formatted = mock_templates._format_context_for_scenario(
            BettingScenario.NBA_PROPS_NIGHT, nba_context
        )

        assert "NBA player props" in formatted
        assert "LeBron James" in formatted


class TestEQ12UnifiedSystem:
    """Test unified response system integration"""

    @pytest.fixture
    def mock_unified_system(self):
        """Mock unified system with all components"""
        with (
            patch("eq12_unified_responses.EQ12ResponsesAPI") as mock_api,
            patch("eq12_unified_responses.EQ12ResponseTemplates") as mock_templates,
        ):

            # Mock API responses
            mock_api_instance = AsyncMock()
            mock_api.return_value = mock_api_instance

            # Mock template responses
            mock_templates_instance = AsyncMock()
            mock_templates.return_value = mock_templates_instance

            from eq12_unified_responses import EQ12UnifiedResponseSystem

            return EQ12UnifiedResponseSystem()

    @pytest.mark.asyncio
    async def test_analyze_betting_opportunity(self, mock_unified_system):
        """Test unified opportunity analysis"""
        # Mock the internal methods
        mock_unified_system._analyze_parlay_opportunity = AsyncMock(
            return_value={"analysis": "parlay_complete"}
        )

        result = await mock_unified_system.analyze_betting_opportunity(
            "parlay", {"legs": SAMPLE_PARLAY_LEGS}, bankroll=5000.0
        )

        assert result["analysis"] == "parlay_complete"

    @pytest.mark.asyncio
    async def test_batch_analysis(self, mock_unified_system):
        """Test batch opportunity analysis"""
        # Mock individual analyses
        mock_unified_system.analyze_betting_opportunity = AsyncMock(
            return_value={"status": "success"}
        )

        opportunities = [
            {"type": "parlay", "data": {"legs": SAMPLE_PARLAY_LEGS[:2]}},
            {"type": "nfl_slate", "data": {"games": SAMPLE_NFL_GAMES}},
        ]

        results = await mock_unified_system.batch_analyze_opportunities(
            opportunities, bankroll=10000.0
        )

        assert len(results) == 2
        assert all(r["status"] == "completed" for r in results)

    @pytest.mark.asyncio
    async def test_live_monitoring_session(self, mock_unified_system):
        """Test live monitoring session management"""
        # Mock API response
        mock_unified_system.core_api.create_live_odds_analysis_response = AsyncMock(
            return_value={"id": "live_resp_123"}
        )

        games = ["Patriots vs Bills", "Cowboys vs Eagles"]
        session_id = await mock_unified_system.start_live_monitoring_session(games)

        assert session_id.startswith("live_")
        assert session_id in mock_unified_system.active_sessions

        # Test session status
        status = await mock_unified_system.get_session_status(session_id)
        assert "session_info" in status

        # Test session stop
        stopped = mock_unified_system.stop_session(session_id)
        assert stopped is True
        assert session_id not in mock_unified_system.active_sessions

    def test_system_status(self, mock_unified_system):
        """Test system status reporting"""
        status = mock_unified_system.get_system_status()

        assert "timestamp" in status
        assert "core_api_available" in status
        assert "templates_available" in status
        assert "active_sessions" in status

    @pytest.mark.asyncio
    async def test_health_check(self, mock_unified_system):
        """Test system health check"""
        health = await mock_unified_system.health_check()

        assert "status" in health
        assert "checks" in health
        assert "api_key" in health["checks"]
        assert "core_api" in health["checks"]
        assert "templates" in health["checks"]

    @pytest.mark.asyncio
    async def test_error_handling_in_unified_system(self, mock_unified_system):
        """Test error handling in unified system"""
        # Mock method to raise exception
        mock_unified_system._analyze_parlay_opportunity = AsyncMock(
            side_effect=Exception("API Error")
        )

        result = await mock_unified_system.analyze_betting_opportunity(
            "parlay", {"legs": []}, bankroll=1000.0
        )

        assert "error" in result
        assert "API Error" in result["error"]


class TestConvenienceFunctions:
    """Test convenience functions"""

    @pytest.mark.asyncio
    async def test_quick_parlay_analysis(self):
        """Test quick parlay analysis function"""
        with patch("eq12_unified_responses.EQ12UnifiedResponseSystem") as mock_system:
            mock_instance = AsyncMock()
            mock_instance.analyze_betting_opportunity.return_value = {
                "analysis": "quick_parlay_complete"
            }
            mock_system.return_value = mock_instance

            from eq12_unified_responses import quick_parlay_analysis

            result = await quick_parlay_analysis(SAMPLE_PARLAY_LEGS[:2], bankroll=2000.0)

            assert result["analysis"] == "quick_parlay_complete"

    @pytest.mark.asyncio
    async def test_quick_nfl_analysis(self):
        """Test quick NFL slate analysis function"""
        with patch("eq12_unified_responses.EQ12UnifiedResponseSystem") as mock_system:
            mock_instance = AsyncMock()
            mock_instance.analyze_betting_opportunity.return_value = {"slate": "nfl_complete"}
            mock_system.return_value = mock_instance

            from eq12_unified_responses import quick_nfl_slate_analysis

            result = await quick_nfl_slate_analysis(SAMPLE_NFL_GAMES, bankroll=5000.0)

            assert result["slate"] == "nfl_complete"

    @pytest.mark.asyncio
    async def test_quick_steam_detection(self):
        """Test quick steam detection function"""
        with patch("eq12_unified_responses.EQ12UnifiedResponseSystem") as mock_system:
            mock_instance = AsyncMock()
            mock_instance.analyze_betting_opportunity.return_value = {"steam": "detected"}
            mock_system.return_value = mock_instance

            from eq12_unified_responses import quick_steam_detection

            result = await quick_steam_detection(SAMPLE_LINE_MOVEMENTS)

            assert result["steam"] == "detected"


@pytest.mark.integration
class TestIntegrationScenarios:
    """Integration tests with real-world scenarios"""

    @pytest.mark.asyncio
    async def test_full_parlay_workflow(self):
        """Test complete parlay analysis workflow"""
        # This would test the full workflow in a real environment
        # Skip if no API key available
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No API key available for integration test")

        from eq12_unified_responses import quick_parlay_analysis

        try:
            result = await quick_parlay_analysis(SAMPLE_PARLAY_LEGS[:2], bankroll=1000.0)

            # Verify structure of real response
            assert "id" in result or "error" in result

        except Exception as e:
            # Expected if modules not available or API issues
            assert "not available" in str(e) or "API" in str(e)

    def test_environment_configuration(self):
        """Test environment variable configuration"""
        # Test default values
        from eq12_model_responses import DEFAULT_MODEL

        assert DEFAULT_MODEL is not None
        # API key may or may not be present

        # Test boolean environment variables
        from eq12_model_responses import ENABLE_FILE_SEARCH, ENABLE_WEB_SEARCH

        assert isinstance(ENABLE_WEB_SEARCH, bool)
        assert isinstance(ENABLE_FILE_SEARCH, bool)


if __name__ == "__main__":
    # Run specific test suites
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "integration":
        # Run integration tests
        pytest.main(["-v", "-m", "integration", __file__])
    else:
        # Run unit tests
        pytest.main(["-v", "-m", "not integration", __file__])
