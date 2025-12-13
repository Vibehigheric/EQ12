#!/usr/bin/env python3
"""
EQ12 API Test Suite - Quick Validation
=====================================

SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2025 EQ12 Project Contributors

Quick test to validate all 9 API endpoints work correctly.
"""

from fastapi.testclient import TestClient

from eq12_api import app

client = TestClient(app)

# Test API key
API_KEY = "development-key-change-in-production"
headers = {"X-API-Key": API_KEY}


def test_health_endpoint():
    """Test health check endpoint (no auth required)"""
    response = client.get("/health")
    print(f"🏥 Health Check: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Status: {data['status']}")
        print(f"   Database: {data['database_connected']}")
        return True
    return False


def test_ev_endpoint():
    """Test expected value calculation"""
    payload = {"true_probability": 0.55, "american_odds": -110}
    response = client.post("/ev", json=payload, headers=headers)
    print(f"📊 EV Calculation: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Expected Value: {data['expected_value']:.4f}")
        print(f"   Recommendation: {data['recommended_action']}")
        return True
    return False


def test_kelly_endpoint():
    """Test Kelly criterion calculation"""
    payload = {
        "true_probability": 0.55,
        "american_odds": -110,
        "bankroll": 1000.0,
        "max_kelly_fraction": 0.25,
    }
    response = client.post("/kelly", json=payload, headers=headers)
    print(f"🎯 Kelly Criterion: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Full Kelly: {data['full_kelly']:.4f}")
        print(f"   Bet Size: ${data['bet_size_dollars']:.2f}")
        return True
    return False


def test_parlay_validate_endpoint():
    """Test parlay validation"""
    payload = {
        "legs": [
            {"market_type": "moneyline", "american_odds": -110, "true_probability": 0.55},
            {"market_type": "spread", "american_odds": -110, "true_probability": 0.52},
        ],
        "correlation_threshold": 0.25,
    }
    response = client.post("/parlay/validate", json=payload, headers=headers)
    print(f"🔍 Parlay Validation: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Valid: {data['is_valid']}")
        print(f"   Max Correlation: {data['max_correlation']:.4f}")
        return True
    return False


def test_parlay_price_endpoint():
    """Test parlay pricing"""
    payload = {
        "legs": [
            {"market_type": "moneyline", "american_odds": -110, "true_probability": 0.55},
            {"market_type": "total", "american_odds": -105, "true_probability": 0.53},
        ]
    }
    response = client.post("/parlay/price", json=payload, headers=headers)
    print(f"💰 Parlay Pricing: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Combined Odds: {data['combined_odds']:.4f}")
        print(f"   Expected Value: {data['expected_value']:.4f}")
        return True
    return False


def test_elo_update_endpoint():
    """Test Elo rating update"""
    payload = {
        "home_rating": 1650.0,
        "away_rating": 1580.0,
        "home_score": 28,
        "away_score": 21,
        "k_factor": 32.0,
    }
    response = client.post("/elo/update", json=payload, headers=headers)
    print(f"⚡ Elo Update: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Home Rating Change: {data['rating_change_home']:+.1f}")
        print(f"   Away Rating Change: {data['rating_change_away']:+.1f}")
        return True
    return False


def test_portfolio_sim_endpoint():
    """Test portfolio simulation"""
    payload = {
        "initial_bankroll": 1000.0,
        "bets": [
            {"probability": 0.55, "odds": 1.91, "stake_fraction": 0.02},
            {"probability": 0.52, "odds": 1.96, "stake_fraction": 0.015},
        ],
        "num_simulations": 100,
        "random_seed": 42,
    }
    response = client.post("/sim/portfolio", json=payload, headers=headers)
    print(f"🎲 Portfolio Simulation: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Mean Final: ${data['mean_final_bankroll']:.2f}")
        print(f"   Profit Probability: {data['probability_of_profit']:.2%}")
        return True
    return False


def test_clv_log_endpoint():
    """Test CLV logging"""
    payload = {
        "market_id": "TEST_BUF_NE_SPREAD",
        "opening_odds": 1.91,
        "closing_odds": 1.85,
        "bet_amount": 100.0,
    }
    response = client.post("/clv/log", json=payload, headers=headers)
    print(f"📈 CLV Logging: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   CLV Percentage: {data['clv_percentage']:.2f}%")
        print(f"   Theoretical Profit: ${data['theoretical_profit']:.2f}")
        return True
    return False


def test_clv_summary_endpoint():
    """Test CLV summary"""
    response = client.get("/clv/summary", headers=headers)
    print(f"📋 CLV Summary: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Total Bets: {data['total_bets']}")
        print(f"   Average CLV: {data['average_clv']:.2f}%")
        return True
    return False


def run_all_api_tests():
    """Run all API endpoint tests"""
    print("🚀 EQ12 API Test Suite")
    print("=" * 60)

    tests = [
        ("Health Check", test_health_endpoint),
        ("Expected Value", test_ev_endpoint),
        ("Kelly Criterion", test_kelly_endpoint),
        ("Parlay Validation", test_parlay_validate_endpoint),
        ("Parlay Pricing", test_parlay_price_endpoint),
        ("Elo Update", test_elo_update_endpoint),
        ("Portfolio Simulation", test_portfolio_sim_endpoint),
        ("CLV Logging", test_clv_log_endpoint),
        ("CLV Summary", test_clv_summary_endpoint),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"   ❌ {test_name} failed")
                failed += 1
        except Exception as e:
            print(f"   ❌ {test_name} error: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"📊 API Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("✅ ALL API ENDPOINTS WORKING - Ready for production!")
        return True
    else:
        print("❌ Some endpoints failed - check errors above")
        return False


if __name__ == "__main__":
    success = run_all_api_tests()
    exit(0 if success else 1)
