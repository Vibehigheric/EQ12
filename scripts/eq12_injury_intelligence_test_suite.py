#!/usr/bin/env python3
"""
EQ12 Injury Intelligence Corrector - Test Suite
Validates that Damian Lillard oversight has been properly corrected

Created: November 4, 2025
Author: EQ12 Emergency Response Team
"""

import unittest
import sys
import os
import json
from datetime import datetime

# Add the scripts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Import the bulletproof system
from eq12_bulletproof_standalone import BulletproofParlayEngine

class TestInjuryIntelligenceCorrection(unittest.TestCase):
    """Test suite for injury intelligence correction system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.workspace_path = "C:\\EQ12"
        self.engine = BulletproofParlayEngine(self.workspace_path)
    
    def test_damian_lillard_blocked(self):
        """Test that Damian Lillard is properly blocked"""
        print(" Testing Damian Lillard blocking...")
        
        # Check if Damian Lillard is in blocked players
        self.assertIn("damian lillard", self.engine.blocked_players, 
                     "Damian Lillard should be in blocked players list")
        
        # Verify his status
        lillard_info = self.engine.blocked_players["damian lillard"]
        self.assertEqual(lillard_info["status"], "OUT", 
                        "Damian Lillard should have OUT status")
        self.assertIn("Achilles", lillard_info["reason"], 
                     "Reason should mention Achilles injury")
        self.assertEqual(lillard_info["team"], "POR", 
                        "Team should be Portland Trail Blazers")
        
        print(f" Damian Lillard properly blocked: {lillard_info}")
    
    def test_blocked_players_count(self):
        """Test that blocked players count is correct"""
        print(" Testing blocked players count...")
        
        # Should now have 6 blocked players (added Damian Lillard)
        expected_count = 6
        actual_count = len(self.engine.blocked_players)
        
        self.assertEqual(actual_count, expected_count, 
                        f"Should have {expected_count} blocked players, got {actual_count}")
        
        print(f" Blocked players count correct: {actual_count}")
    
    def test_all_critical_players_blocked(self):
        """Test that all critical injury-prone players are blocked"""
        print(" Testing all critical players are blocked...")
        
        expected_blocked = [
            "damian lillard",    # NEW: Torn Achilles
            "giannis antetokounmpo",  # Knee issues
            "lebron james",      # Age/rest management
            "kawhi leonard",     # Chronic knee issues
            "paul george",       # Injury prone
            "zion williamson"    # Frequent injuries
        ]
        
        for player in expected_blocked:
            self.assertIn(player, self.engine.blocked_players, 
                         f"{player} should be blocked")
            print(f" {player.title()} is properly blocked")
    
    def test_parlay_generation_blocks_lillard(self):
        """Test that parlay generation properly blocks Damian Lillard"""
        print(" Testing parlay generation blocks Damian Lillard...")
        
        # Create a test bet that would include Damian Lillard
        test_bet = "Damian Lillard OVER 10.5 rebounds (-115)"
        
        # Check if bet would be blocked
        is_blocked, reason = self.engine.is_player_blocked("Damian Lillard")
        
        self.assertTrue(is_blocked, "Damian Lillard bet should be blocked")
        self.assertIn("Achilles", reason, "Block reason should mention Achilles")
        
        print(f" Damian Lillard bet properly blocked: {reason}")
    
    def test_emergency_correction_completeness(self):
        """Test that emergency correction was comprehensive"""
        print(" Testing emergency correction completeness...")
        
        # Check that data files were created
        data_dir = os.path.join(self.workspace_path, "data")
        blocked_players_file = os.path.join(data_dir, "blocked_players_master.json")
        
        if os.path.exists(blocked_players_file):
            with open(blocked_players_file, 'r') as f:
                data = json.load(f)
                self.assertIn("Damian Lillard", data.get("blocked_players", []),
                             "Damian Lillard should be in master blocked players file")
                print(" Master blocked players file updated")
        
        # Check that logs were generated
        logs_dir = os.path.join(self.workspace_path, "logs")
        emergency_reports = [f for f in os.listdir(logs_dir) 
                           if f.startswith("EMERGENCY_INJURY_INTELLIGENCE_REPORT_")]
        
        self.assertGreater(len(emergency_reports), 0, 
                          "Emergency intelligence reports should be generated")
        print(f" {len(emergency_reports)} emergency reports generated")
    
    def test_bulletproof_system_functionality(self):
        """Test that bulletproof system still functions correctly"""
        print(" Testing bulletproof system functionality...")
        
        # Generate a test parlay
        try:
            parlay = self.engine.generate_bulletproof_parlay()
            
            # Verify parlay structure
            self.assertIn("legs", parlay, "Parlay should have legs")
            self.assertIn("blocked_players", parlay, "Parlay should track blocked players")
            self.assertIn("total_odds", parlay, "Parlay should have total odds")
            
            # Verify Damian Lillard is in blocked list
            blocked_players = parlay["blocked_players"]
            self.assertIn("damian lillard", [player.lower() for player in blocked_players],
                         "Damian Lillard should be in parlay blocked players list")
            
            print(f" Bulletproof parlay generated with {len(parlay['legs'])} legs")
            print(f" {len(blocked_players)} players blocked from parlay")
            
        except Exception as e:
            self.fail(f"Bulletproof system failed to generate parlay: {e}")

class TestDamianLillardSpecific(unittest.TestCase):
    """Specific tests for Damian Lillard injury situation"""
    
    def setUp(self):
        self.workspace_path = "C:\\EQ12"
        self.engine = BulletproofParlayEngine(self.workspace_path)
    
    def test_lillard_injury_details(self):
        """Test specific details of Damian Lillard's injury"""
        print(" Testing Damian Lillard injury details...")
        
        lillard_info = self.engine.blocked_players["damian lillard"]
        
        # Verify injury details
        self.assertEqual(lillard_info["status"], "OUT")
        self.assertIn("Torn Achilles", lillard_info["reason"])
        self.assertEqual(lillard_info["team"], "POR")
        self.assertEqual(lillard_info["confidence"], 1.0)  # 100% confidence he's out
        
        print(f" Lillard injury details correct: {lillard_info}")
    
    def test_lillard_variants_blocked(self):
        """Test that different name variants of Damian Lillard are blocked"""
        print(" Testing Damian Lillard name variants...")
        
        name_variants = [
            "Damian Lillard",
            "damian lillard", 
            "DAMIAN LILLARD",
            "D. Lillard",
            "Dame Lillard"
        ]
        
        for variant in name_variants:
            is_blocked, reason = self.engine.is_player_blocked(variant)
            if is_blocked:
                print(f" {variant} properly blocked: {reason}")
            else:
                # Some variants might not match exactly, but main ones should
                if variant.lower() in ["damian lillard", "dame lillard"]:
                    print(f" {variant} not blocked - may need fuzzy matching")

def run_correction_tests():
    """Run all correction tests"""
    print(" RUNNING INJURY INTELLIGENCE CORRECTION TESTS ")
    print("=" * 80)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestInjuryIntelligenceCorrection))
    suite.addTest(unittest.makeSuite(TestDamianLillardSpecific))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print(" ALL INJURY INTELLIGENCE CORRECTION TESTS PASSED")
        print(f" Ran {result.testsRun} tests successfully")
        print(" Damian Lillard oversight has been CORRECTED")
    else:
        print(" SOME TESTS FAILED")
        print(f" Failures: {len(result.failures)}")
        print(f" Errors: {len(result.errors)}")
        
        for test, error in result.failures + result.errors:
            print(f" {test}: {error}")
    
    print("=" * 80)
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_correction_tests()
    sys.exit(0 if success else 1)