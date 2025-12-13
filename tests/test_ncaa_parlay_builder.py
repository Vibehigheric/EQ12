"""
EQ12 NCAA PARLAY BUILDER - PYTEST TESTS
========================================
Comprehensive Python tests for NCAA parlay generation system.
"""

import json
import os
import sqlite3

# Add EQ12 root to path for imports
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from eq12_ncaa_parlay_builder import EQ12NCAAParleyBuilder, Parlay, ParlayLeg


class TestEQ12NCAAParleyBuilder:
    """Test suite for NCAA parlay builder."""

    @pytest.fixture
    def builder(self):
        """Create a test builder instance."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "ODDS_API_KEY": "test-key"}):
            return EQ12NCAAParleyBuilder()

    @pytest.fixture
    def mock_games_data(self):
        """Mock NCAA games data."""
        return [
            {
                "id": "test_game_1",
                "eq12_sport": "NCAA-FB",
                "sport_title": "NCAA Football",
                "commence_time": "2024-01-15T19:00:00Z",
                "home_team": "Alabama",
                "away_team": "Georgia",
                "bookmakers": [
                    {
                        "key": "fanduel",
                        "title": "FanDuel",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Alabama", "price": -110},
                                    {"name": "Georgia", "price": -110},
                                ],
                            },
                            {
                                "key": "spreads",
                                "outcomes": [
                                    {"name": "Alabama", "price": -110, "point": -3.5},
                                    {"name": "Georgia", "price": -110, "point": 3.5},
                                ],
                            },
                        ],
                    }
                ],
            }
        ]

    def test_builder_initialization(self, builder):
        """Test that builder initializes correctly."""
        assert isinstance(builder, EQ12NCAAParleyBuilder)
        assert hasattr(builder, "config")
        assert hasattr(builder, "error_boundary")
        assert builder.min_confidence == 0.08
        assert builder.max_legs_high_conf == 10
        assert builder.max_legs_high_payout == 20

    def test_config_loading(self, builder):
        """Test configuration loading."""
        config = builder.config
        assert isinstance(config, dict)
        assert "bankroll" in config
        assert "max_risk_per_bet" in config
        assert config["bankroll"] > 0

    def test_database_setup(self, builder):
        """Test database initialization."""
        # Check if database path is set
        assert hasattr(builder, "db_path")

        # Check if database file exists after setup
        db_dir = os.path.dirname(builder.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        # Run setup
        builder._setup_database()

        # Verify tables exist
        with sqlite3.connect(builder.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            assert "ncaa_parlays" in tables
            assert "parlay_legs" in tables

    def test_mock_data_generation(self, builder):
        """Test mock NCAA data generation."""
        mock_data = builder._generate_mock_ncaa_data()

        assert isinstance(mock_data, list)
        assert len(mock_data) > 0

        # Check for required fields
        for game in mock_data:
            assert "id" in game
            assert "eq12_sport" in game
            assert "home_team" in game
            assert "away_team" in game
            assert "bookmakers" in game

        # Check for both sports
        sports = {game["eq12_sport"] for game in mock_data}
        assert "NCAA-FB" in sports
        assert "NCAA-BB" in sports

    def test_edge_calculation(self, builder):
        """Test betting edge calculation."""
        # Test positive edge scenario
        edge1 = builder.calculate_edge(-110, 0.55)  # 55% true prob, -110 odds
        assert edge1 > 0

        # Test negative edge scenario
        edge2 = builder.calculate_edge(-110, 0.45)  # 45% true prob, -110 odds
        assert edge2 < 0

        # Test zero edge scenario
        edge3 = builder.calculate_edge(100, 0.5)  # 50% true prob, +100 odds
        assert abs(edge3) < 0.01  # Should be close to zero

    def test_kelly_calculation(self, builder):
        """Test Kelly Criterion calculation."""
        # Test positive edge
        kelly1 = builder.calculate_kelly_percentage(0.1, 150)  # 10% edge, +150
        assert kelly1 > 0
        assert kelly1 < 0.1  # Should be less than raw edge due to multiplier

        # Test zero/negative edge
        kelly2 = builder.calculate_kelly_percentage(0.0, 100)
        assert kelly2 == 0.0

        kelly3 = builder.calculate_kelly_percentage(-0.05, -110)
        assert kelly3 == 0.0

    def test_weather_impact_evaluation(self, builder):
        """Test weather impact assessment."""
        # Test outdoor sport (football)
        fb_game = {"eq12_sport": "NCAA-FB"}
        weather, impact = builder.evaluate_weather_impact(fb_game)
        assert isinstance(weather, str)
        assert isinstance(impact, float)

        # Test indoor sport (basketball)
        bb_game = {"eq12_sport": "NCAA-BB"}
        weather, impact = builder.evaluate_weather_impact(bb_game)
        assert weather == "Indoor"
        assert impact == 0.0

    @pytest.mark.asyncio
    async def test_sentiment_analysis(self, builder):
        """Test sentiment analysis functionality."""
        test_game = {
            "away_team": "Duke",
            "home_team": "North Carolina",
            "eq12_sport": "NCAA-BB",
        }

        sentiment = await builder.analyze_game_sentiment(test_game)
        assert isinstance(sentiment, float)
        assert 0.0 <= sentiment <= 1.0

    @pytest.mark.asyncio
    async def test_parlay_leg_creation(self, builder, mock_games_data):
        """Test parlay leg creation from games data."""
        legs = await builder.create_parlay_legs(mock_games_data)

        assert isinstance(legs, list)

        # If legs were created, verify structure
        for leg in legs:
            assert isinstance(leg, ParlayLeg)
            assert hasattr(leg, "game_id")
            assert hasattr(leg, "sport")
            assert hasattr(leg, "odds")
            assert hasattr(leg, "confidence")
            assert hasattr(leg, "edge_percentage")

    def test_leg_selection(self, builder):
        """Test parlay leg selection algorithm."""
        # Create mock legs
        mock_legs = [
            ParlayLeg(
                game_id=f"game_{i}",
                sport="NCAA-FB",
                matchup=f"Team A @ Team B {i}",
                home_team=f"Home_{i}",
                away_team=f"Away_{i}",
                pick_type="ML",
                bet="Team A ML",
                odds=100 + i * 10,
                confidence=0.6 + i * 0.01,
                kelly_percentage=0.02 + i * 0.005,
                sentiment=0.7,
                weather="Clear",
                edge_percentage=8.0 + i,
                clv_variance=0.01,
                start_time="2024-01-15T19:00:00Z",
                market_data={},
            )
            for i in range(15)
        ]

        # Test high-confidence selection
        hc_legs = builder.select_parlay_legs(mock_legs, 10, "high-confidence")
        assert len(hc_legs) <= 10

        # Test high-payout selection
        hp_legs = builder.select_parlay_legs(mock_legs, 20, "high-payout")
        assert len(hp_legs) <= 20

        # Verify no duplicate games
        hc_game_ids = {leg.game_id for leg in hc_legs}
        assert len(hc_game_ids) == len(hc_legs)

    def test_parlay_metrics_calculation(self, builder):
        """Test parlay-level metrics calculation."""
        # Create test legs
        test_legs = [
            ParlayLeg(
                game_id="game_1",
                sport="NCAA-FB",
                matchup="Team A @ Team B",
                home_team="Team B",
                away_team="Team A",
                pick_type="ML",
                bet="Team A ML",
                odds=150,
                confidence=0.6,
                kelly_percentage=0.02,
                sentiment=0.7,
                weather="Clear",
                edge_percentage=8.0,
                clv_variance=0.01,
                start_time="2024-01-15T19:00:00Z",
                market_data={},
            ),
            ParlayLeg(
                game_id="game_2",
                sport="NCAA-BB",
                matchup="Team C @ Team D",
                home_team="Team D",
                away_team="Team C",
                pick_type="SPREADS",
                bet="Team C +5",
                odds=-110,
                confidence=0.65,
                kelly_percentage=0.025,
                sentiment=0.75,
                weather="Indoor",
                edge_percentage=9.0,
                clv_variance=0.02,
                start_time="2024-01-16T19:00:00Z",
                market_data={},
            ),
        ]

        combined_odds, win_prob, expected_roi, avg_clv = builder.calculate_parlay_metrics(test_legs)

        assert isinstance(combined_odds, float)
        assert isinstance(win_prob, float)
        assert isinstance(expected_roi, float)
        assert isinstance(avg_clv, float)

        assert win_prob > 0
        assert win_prob < 1
        assert avg_clv > 0

    def test_stake_calculation(self, builder):
        """Test recommended stake calculation."""
        # Create mock parlay
        mock_parlay = Parlay(
            parlay_id="test_parlay",
            parlay_type="high-confidence",
            legs=[],  # Empty for this test
            combined_odds=500,
            win_probability=0.3,
            expected_roi=50.0,
            clv_vs_open=0.02,
            recommended_stake=0.0,
            total_edge=20.0,
            risk_score=0.5,
            created_at=datetime.now().isoformat(),
        )

        # Add mock legs with Kelly percentages
        mock_parlay.legs = [
            MagicMock(kelly_percentage=0.02),
            MagicMock(kelly_percentage=0.015),
        ]

        stake = builder.calculate_recommended_stake(mock_parlay)

        assert isinstance(stake, float)
        assert stake >= 0
        assert stake <= builder.config["bankroll"] * builder.config["max_risk_per_bet"]

    @pytest.mark.asyncio
    async def test_full_parlay_generation(self, builder):
        """Test complete parlay generation workflow."""
        with patch.object(builder, "fetch_ncaa_odds") as mock_fetch:
            # Mock the odds fetching to return test data
            mock_fetch.return_value = builder._generate_mock_ncaa_data()

            high_conf, high_payout = await builder.generate_parlays()

            # Verify both parlays were created
            assert isinstance(high_conf, Parlay)
            assert isinstance(high_payout, Parlay)

            assert high_conf.parlay_type == "high-confidence"
            assert high_payout.parlay_type == "high-payout"

            # Verify parlay structure
            assert len(high_conf.legs) <= builder.max_legs_high_conf
            assert len(high_payout.legs) <= builder.max_legs_high_payout

    def test_database_operations(self, builder):
        """Test database save operations."""
        # Create test parlay
        test_parlay = Parlay(
            parlay_id="test_save_parlay",
            parlay_type="test",
            legs=[],
            combined_odds=200,
            win_probability=0.4,
            expected_roi=25.0,
            clv_vs_open=0.01,
            recommended_stake=20.0,
            total_edge=15.0,
            risk_score=0.3,
            created_at=datetime.now().isoformat(),
        )

        # Save to database
        builder.save_parlays_to_database([test_parlay])

        # Verify save
        with sqlite3.connect(builder.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM ncaa_parlays WHERE parlay_id = ?",
                (test_parlay.parlay_id,),
            )
            result = cursor.fetchone()

            assert result is not None
            assert result[1] == test_parlay.parlay_id  # parlay_id column

    def test_json_export(self, builder):
        """Test JSON export functionality."""
        # Create test parlay
        test_parlay = Parlay(
            parlay_id="test_export_parlay",
            parlay_type="test",
            legs=[],
            combined_odds=300,
            win_probability=0.35,
            expected_roi=30.0,
            clv_vs_open=0.015,
            recommended_stake=25.0,
            total_edge=18.0,
            risk_score=0.4,
            created_at=datetime.now().isoformat(),
        )

        filename = builder.export_to_json([test_parlay])

        assert filename is not None
        assert filename.endswith(".json")
        assert os.path.exists(filename)

        # Verify JSON content
        with open(filename) as f:
            data = json.load(f)

        assert "generated_at" in data
        assert "system" in data
        assert "parlays" in data
        assert "summary" in data

        assert data["system"] == "EQ12 NCAA Parlay Builder"
        assert len(data["parlays"]) == 1

        # Cleanup
        os.unlink(filename)

    def test_bet_description_formatting(self, builder):
        """Test bet description formatting."""
        # Test moneyline
        ml_desc = builder._format_bet_description("h2h", {"name": "Alabama"}, {})
        assert ml_desc == "Alabama ML"

        # Test spread
        spread_desc = builder._format_bet_description(
            "spreads", {"name": "Alabama", "point": -3.5}, {}
        )
        assert spread_desc == "Alabama -3.5"

        # Test totals
        total_desc = builder._format_bet_description("totals", {"name": "Over", "point": 47.5}, {})
        assert total_desc == "Over 47.5"


@pytest.mark.integration
class TestIntegration:
    """Integration tests for NCAA parlay system with EQ12 components."""

    def test_unicode_integration(self):
        """Test integration with EQ12 Unicode protection."""
        from eq12_ncaa_parlay_builder import EQ12NCAAParleyBuilder
        from eq12_unicode_simple import safe_print

        # This should not raise any exceptions
        safe_print("🏈 Testing NCAA parlay Unicode integration")

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            builder = EQ12NCAAParleyBuilder()
            assert isinstance(builder, EQ12NCAAParleyBuilder)

    def test_error_boundary_integration(self):
        """Test integration with GPT-5 Error Boundary."""
        from eq12_error_boundary import GPT5ErrorBoundary

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            builder = EQ12NCAAParleyBuilder()
            assert hasattr(builder, "error_boundary")
            assert isinstance(builder.error_boundary, GPT5ErrorBoundary)


# Test configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
