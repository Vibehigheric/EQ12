#!/usr/bin/env python3
"""
 EQ12 BULLETPROOF PARLAY TEST SUITE
Tests to verify Giannis and other OUT players are properly blocked

This test suite demonstrates:
1. Giannis Antetokounmpo is blocked (OUT - Load Management)
2. LeBron James is blocked (OUT - Load Management)
3. Kawhi Leonard is blocked (OUT - Knee Management)
4. Safe players are allowed through
5. Error prevention works correctly
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from eq12_bulletproof_standalone import BulletproofParlayEngine
    from eq12_parlay_filter_engine import ParlayFilterEngine
    IMPORTS_OK = True
except ImportError as e:
    print(f" Import error: {e}")
    IMPORTS_OK = False


def test_bulletproof_blocking():
    """Test that blocked players are properly filtered"""
    if not IMPORTS_OK:
        print(" Cannot run tests - imports failed")
        return False
    
    print(" TESTING BULLETPROOF PLAYER BLOCKING")
    print("="*50)
    
    engine = BulletproofParlayEngine()
    
    # Test cases: (player_name, expected_blocked, description)
    test_cases = [
        ("Giannis Antetokounmpo", True, "Should be blocked - OUT (Load Management)"),
        ("LeBron James", True, "Should be blocked - OUT (Load Management)"),
        ("Kawhi Leonard", True, "Should be blocked - OUT (Knee Management)"),
        ("Paul George", True, "Should be blocked - QUESTIONABLE (Knee Soreness)"),
        ("Zion Williamson", True, "Should be blocked - OUT (Hamstring Strain)"),
        ("Stephen Curry", False, "Should be allowed - Active player"),
        ("Jayson Tatum", False, "Should be allowed - Active player"),
        ("Nikola Jokic", False, "Should be allowed - Active player")
    ]
    
    all_passed = True
    
    for player_name, expected_blocked, description in test_cases:
        is_blocked, reason = engine.is_player_blocked(player_name)
        
        if is_blocked == expected_blocked:
            status = " PASS"
        else:
            status = " FAIL"
            all_passed = False
        
        print(f"{status} {player_name}")
        print(f"   Expected: {'BLOCKED' if expected_blocked else 'ALLOWED'}")
        print(f"   Actual: {'BLOCKED' if is_blocked else 'ALLOWED'}")
        if is_blocked:
            print(f"   Reason: {reason}")
        print(f"   Test: {description}")
        print()
    
    return all_passed


def test_parlay_leg_extraction():
    """Test player name extraction from parlay leg descriptions"""
    if not IMPORTS_OK:
        print(" Cannot run extraction tests - imports failed")
        return False
    
    print(" TESTING PLAYER NAME EXTRACTION")
    print("="*40)
    
    engine = BulletproofParlayEngine()
    
    # Test cases: (description, expected_player)
    test_cases = [
        ("Giannis Antetokounmpo OVER 31.5 points", "Giannis Antetokounmpo"),
        ("LeBron James OVER 25.5 points (-110)", "LeBron James"),
        ("Stephen Curry UNDER 28.5 points", "Stephen Curry"),
        ("Lakers ML vs Warriors", None),  # Team bet, no player
        ("OVER 225.5 total points", None),  # Total bet, no player
        ("Jayson Tatum OVER 8.5 rebounds", "Jayson Tatum")
    ]
    
    all_passed = True
    
    for description, expected_player in test_cases:
        extracted_player = engine.extract_player_from_description(description)
        
        if extracted_player == expected_player:
            status = " PASS"
        else:
            status = " FAIL"
            all_passed = False
        
        print(f"{status} '{description}'")
        print(f"   Expected: {expected_player}")
        print(f"   Extracted: {extracted_player}")
        print()
    
    return all_passed


def test_full_parlay_filtering():
    """Test complete parlay filtering with mixed legs"""
    if not IMPORTS_OK:
        print(" Cannot run parlay filtering tests - imports failed")
        return False
    
    print(" TESTING FULL PARLAY FILTERING")
    print("="*35)
    
    engine = BulletproofParlayEngine()
    
    # Create test parlay with mix of safe and blocked players
    test_parlay_legs = [
        {"description": "Giannis Antetokounmpo OVER 31.5 points", "odds": -110},
        {"description": "Stephen Curry OVER 28.5 points", "odds": -115},
        {"description": "LeBron James OVER 25.5 points", "odds": -105},
        {"description": "Lakers ML vs Warriors", "odds": -120},  # Team bet
        {"description": "Kawhi Leonard OVER 24.5 points", "odds": -108},
        {"description": "Jayson Tatum OVER 28.5 points", "odds": -115},
        {"description": "OVER 225.5 total points", "odds": -110}  # Total bet
    ]
    
    print(f"Input: {len(test_parlay_legs)} legs")
    
    # Process legs to identify blocked vs safe
    safe_legs = []
    blocked_legs = []
    
    for leg in test_parlay_legs:
        description = leg["description"]
        player_name = engine.extract_player_from_description(description)
        
        if player_name:
            is_blocked, reason = engine.is_player_blocked(player_name)
            
            if is_blocked:
                leg["blocked_reason"] = reason
                leg["blocked_player"] = player_name
                blocked_legs.append(leg)
            else:
                safe_legs.append(leg)
        else:
            # Non-player legs are safe
            safe_legs.append(leg)
    
    print(f"Result: {len(safe_legs)} safe legs, {len(blocked_legs)} blocked legs")
    
    if blocked_legs:
        print(f"\n BLOCKED LEGS:")
        for leg in blocked_legs:
            player = leg.get("blocked_player", "Unknown")
            reason = leg.get("blocked_reason", "Unknown")
            print(f"   - {leg['description']}")
            print(f"     Player: {player}")
            print(f"     Reason: {reason}")
    
    if safe_legs:
        print(f"\n SAFE LEGS:")
        for leg in safe_legs:
            print(f"   - {leg['description']}")
    
    # Verify specific expectations
    expected_blocked = ["Giannis Antetokounmpo", "LeBron James", "Kawhi Leonard"]
    expected_safe = ["Stephen Curry", "Jayson Tatum"]
    
    blocked_players = [leg.get("blocked_player") for leg in blocked_legs if "blocked_player" in leg]
    
    success = True
    
    # Check that all expected blocked players are blocked
    for player in expected_blocked:
        if player not in blocked_players:
            print(f" FAIL: {player} should have been blocked but wasn't")
            success = False
    
    # Check that team/total bets are preserved
    team_bets = [leg for leg in safe_legs if "ML" in leg["description"] or "total" in leg["description"]]
    if len(team_bets) < 2:
        print(f" FAIL: Team/total bets should be preserved")
        success = False
    
    if success:
        print(f"\n PARLAY FILTERING TEST PASSED")
    else:
        print(f"\n PARLAY FILTERING TEST FAILED")
    
    return success


def run_all_tests():
    """Run complete test suite"""
    print(" EQ12 BULLETPROOF PARLAY TEST SUITE")
    print("="*60)
    print("Testing prevention of Giannis-type errors")
    print("="*60)
    
    tests = [
        ("Player Blocking", test_bulletproof_blocking),
        ("Name Extraction", test_parlay_leg_extraction),
        ("Parlay Filtering", test_full_parlay_filtering)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n Running {test_name} tests...")
        if test_func():
            print(f" {test_name} tests PASSED")
            passed += 1
        else:
            print(f" {test_name} tests FAILED")
    
    print(f"\n" + "="*60)
    print(f" TEST RESULTS: {passed}/{total} test suites passed")
    
    if passed == total:
        print(" ALL TESTS PASSED - Bulletproof system working correctly!")
        print(" Giannis and other OUT players will be blocked automatically!")
    else:
        print(" SOME TESTS FAILED - System may not be bulletproof!")
    
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)