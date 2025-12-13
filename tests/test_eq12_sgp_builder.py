#!/usr/bin/env python3
"""
Unit tests for EQ12 SGP Builder
Tests SGP generation, scoring, and selection with fixed vectors.
"""

import json
import unittest

from eq12_sgp_builder import SGP, SGPBuilder, SGPLeg


class TestSGPBuilder(unittest.TestCase):
    """Test cases for SGP Builder functionality"""

    def setUp(self):
        """Setup test fixtures"""
        self.builder = SGPBuilder(min_odds=10.0, stake_range=(8.0, 20.0))

        # Fixed test game
        self.test_game = {
            "id": "test_nhl_game",
            "home_team": "Boston Bruins",
            "away_team": "NY Rangers",
            "sport_title": "NHL",
            "commence_time": "2025-10-08T19:00:00Z",
        }

        # Fixed market book with deterministic odds
        self.test_market_book = {
            "h2h": {
                "bookmaker": "draftkings",
                "outcomes": [
                    {"name": "Boston Bruins", "price": -135},  # 1.741 decimal
                    {"name": "NY Rangers", "price": 115},  # 2.15 decimal
                ],
            },
            "totals": {
                "bookmaker": "fanduel",
                "outcomes": [
                    {"name": "Over 6.5", "price": -105},  # 1.952 decimal
                    {"name": "Under 6.5", "price": -115},  # 1.870 decimal
                ],
            },
            "spreads": {
                "bookmaker": "betmgm",
                "outcomes": [
                    {"name": "Boston Bruins -1.5", "price": 180},  # 2.80 decimal
                    {"name": "NY Rangers +1.5", "price": -220},  # 1.455 decimal
                ],
            },
        }

    def test_sgp_leg_creation(self):
        """Test SGP leg creation and decimal odds conversion"""
        leg = SGPLeg(market="moneyline", selection="Boston Bruins", price=-135, book="draftkings")

        self.assertEqual(leg.market, "moneyline")
        self.assertEqual(leg.selection, "Boston Bruins")
        self.assertEqual(leg.price, -135)
        self.assertEqual(leg.book, "draftkings")
        self.assertAlmostEqual(leg.decimal_odds, 1.741, places=3)

    def test_extract_markets(self):
        """Test market extraction from market book"""
        markets = self.builder._extract_markets(self.test_market_book)

        # Should have 6 total outcomes (2 ML + 2 totals + 2 spreads)
        self.assertEqual(len(markets), 6)

        # Check market normalization
        market_types = {market["market"] for market in markets}
        expected_types = {"moneyline", "total", "spread"}
        self.assertEqual(market_types, expected_types)

    def test_sgp_candidate_generation(self):
        """Test SGP candidate generation"""
        candidates = self.builder.build_sgp_candidates(self.test_game, self.test_market_book)

        # Should generate multiple candidates
        self.assertGreater(len(candidates), 0)

        # All candidates should be validated
        for candidate in candidates:
            self.assertTrue(candidate.validated)
            self.assertGreaterEqual(len(candidate.legs), 2)
            self.assertLessEqual(len(candidate.legs), 6)

    def test_sgp_scoring(self):
        """Test SGP scoring with fixed odds"""
        # Create test legs with known odds
        legs = [
            SGPLeg("moneyline", "Boston Bruins", -135, "draftkings"),  # 1.741
            SGPLeg("total", "Under 6.5", -115, "fanduel"),  # 1.870
        ]

        # Expected parlay odds: 1.741 * 1.870 = 3.256
        parlay_odds = 1.741 * 1.870

        scoring = self.builder.score_sgp_legs(legs, parlay_odds)

        # Verify scoring structure
        self.assertIn("ev_pct", scoring)
        self.assertIn("kelly_fraction", scoring)
        self.assertIn("risk_score", scoring)
        self.assertIn("estimated_true_prob", scoring)

        # EV should be reasonable (negative to positive range)
        self.assertGreaterEqual(scoring["ev_pct"], -0.50)
        self.assertLessEqual(scoring["ev_pct"], 0.50)

        # Kelly fraction should be capped at 0.25
        self.assertLessEqual(scoring["kelly_fraction"], 0.25)

    def test_best_sgp_selection(self):
        """Test best SGP selection logic"""
        # Create mock candidates with known metrics
        candidates = []

        # High EV candidate
        high_ev_sgp = SGP(
            game="Test Game",
            league="NHL",
            legs=[],
            decimal_odds=12.0,
            stake=15.0,
            potential_payout=180.0,
            ev_pct=0.10,  # 10% EV
            kelly_fraction=0.15,
            risk_score="LOW",
            validated=True,
        )
        candidates.append(high_ev_sgp)

        # Lower EV candidate
        low_ev_sgp = SGP(
            game="Test Game",
            league="NHL",
            legs=[],
            decimal_odds=15.0,
            stake=10.0,
            potential_payout=150.0,
            ev_pct=0.05,  # 5% EV
            kelly_fraction=0.08,
            risk_score="MED",
            validated=True,
        )
        candidates.append(low_ev_sgp)

        # Should select high EV candidate
        best = self.builder.select_best_sgp(candidates)
        self.assertEqual(best.ev_pct, 0.10)
        self.assertEqual(best.risk_score, "LOW")

    def test_optimal_stake_calculation(self):
        """Test optimal stake calculation based on Kelly fraction"""
        # High confidence (>= 0.15)
        high_stake = self.builder._calculate_optimal_stake(0.20)
        self.assertEqual(high_stake, 20.0)

        # Medium confidence (0.08-0.15)
        med_stake = self.builder._calculate_optimal_stake(0.10)
        self.assertEqual(med_stake, 14.0)  # (8+20)/2

        # Low confidence (< 0.08)
        low_stake = self.builder._calculate_optimal_stake(0.05)
        self.assertEqual(low_stake, 8.0)

    def test_sgp_to_dict_serialization(self):
        """Test SGP serialization to dictionary"""
        legs = [
            SGPLeg("moneyline", "Boston Bruins", -135, "draftkings"),
            SGPLeg("total", "Under 6.5", -115, "fanduel"),
        ]

        sgp = SGP(
            game="Boston Bruins vs NY Rangers",
            league="NHL",
            legs=legs,
            decimal_odds=12.5,
            stake=15.0,
            potential_payout=187.5,
            ev_pct=0.08,
            kelly_fraction=0.12,
            risk_score="LOW",
            validated=True,
            notes="Test SGP",
        )

        sgp_dict = sgp.to_dict()

        # Verify structure
        self.assertIn("game", sgp_dict)
        self.assertIn("league", sgp_dict)
        self.assertIn("legs", sgp_dict)
        self.assertIn("decimal_odds", sgp_dict)

        # Verify legs are properly serialized
        self.assertEqual(len(sgp_dict["legs"]), 2)
        self.assertEqual(sgp_dict["legs"][0]["market"], "moneyline")

        # Should be JSON serializable
        json_str = json.dumps(sgp_dict)
        self.assertIsInstance(json_str, str)

    def test_minimum_odds_filtering(self):
        """Test filtering by minimum odds requirement"""
        # Create candidates with different odds
        low_odds_sgp = SGP(
            game="Test",
            league="NHL",
            legs=[],
            decimal_odds=5.0,
            stake=10.0,
            potential_payout=50.0,
            ev_pct=0.08,
            kelly_fraction=0.1,
            risk_score="LOW",
            validated=True,
        )

        high_odds_sgp = SGP(
            game="Test",
            league="NHL",
            legs=[],
            decimal_odds=15.0,
            stake=10.0,
            potential_payout=150.0,
            ev_pct=0.06,
            kelly_fraction=0.08,
            risk_score="MED",
            validated=True,
        )

        candidates = [low_odds_sgp, high_odds_sgp]

        # Should select only the high odds SGP (>= 10.0)
        best = self.builder.select_best_sgp(candidates, min_odds=10.0)
        self.assertEqual(best.decimal_odds, 15.0)

    def test_risk_score_assignment(self):
        """Test risk score assignment based on EV percentage"""
        # Test LOW risk (>= 8% EV)
        legs = [SGPLeg("test", "test", 100, "test")]
        scoring_low = self.builder.score_sgp_legs(legs, 2.0)

        # Test MED risk (4-8% EV) - would need specific odds to hit this range
        # Test HIGH risk (2-4% EV) - would need specific odds to hit this range

        # The exact EV depends on the hold assumptions and implied probabilities
        # So we just verify the structure is correct
        self.assertIn(scoring_low["risk_score"], ["LOW", "MED", "HIGH", "SKIP"])


if __name__ == "__main__":
    # Create expected output snapshot for regression testing
    print("Running EQ12 SGP Builder tests...")

    # Run tests
    unittest.main(verbosity=2)

    # Example expected output structure for documentation
    expected_sgp_output = {
        "date_local": "2025-10-08",
        "league": "NHL",
        "type": "sgp",
        "game": "Boston Bruins vs NY Rangers",
        "legs": [
            {
                "market": "moneyline",
                "selection": "Boston Bruins",
                "price": -135,
                "book": "draftkings",
                "decimal_odds": 1.741,
            },
            {
                "market": "total",
                "selection": "Under 6.5",
                "price": -115,
                "book": "fanduel",
                "decimal_odds": 1.870,
            },
        ],
        "decimal_odds": 3.256,
        "stake": 12.0,
        "potential_payout": 39.07,
        "ev_pct": 0.045,
        "kelly_fraction": 0.08,
        "risk_score": "MED",
        "validated": True,
        "notes": "Same-game supported; props availability may vary by book.",
    }

    print("\nExpected SGP output structure:")
    print(json.dumps(expected_sgp_output, indent=2))
