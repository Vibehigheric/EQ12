#!/usr/bin/env python3
"""
 HARDCODED TRIGGER CHECKER
Reads configuration and tells you EXACTLY when to use roster prevention
No guesswork - simple YES/NO decisions based on hardcoded rules
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any


class HardcodedTriggerChecker:
    """
     Simple checker that tells you exactly when to use roster prevention
    Based on hardcoded configuration - no thinking required
    """
    
    def __init__(self):
        self.script_path = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(os.path.dirname(self.script_path), "configs")
        self.config_file = os.path.join(self.config_path, "hardcoded_automation_triggers.json")
        
        # Load hardcoded configuration
        self.config = self._load_hardcoded_config()
        
        print(" Hardcoded Trigger Checker initialized")
    
    def _load_hardcoded_config(self) -> Dict[str, Any]:
        """Load hardcoded trigger configuration"""
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f" Config file not found: {self.config_file}")
            return self._get_fallback_config()
        except json.JSONDecodeError:
            print(f" Invalid JSON in config file")
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Fallback configuration if file not found"""
        
        return {
            "hardcoded_automation_config": {
                "mandatory_triggers": {
                    "triggers": {
                        "before_sgp_creation": {"enabled": True, "action": "run_full_prevention"},
                        "before_player_props": {"enabled": True, "action": "run_quick_check"}
                    }
                },
                "problem_player_database": {
                    "players": {
                        "DK Metcalf": {"status": "INACTIVE", "confidence": 100},
                        "Terry McLaurin": {"status": "INACTIVE", "confidence": 100},
                        "Tyler Lockett": {"status": "INACTIVE", "confidence": 100}
                    }
                }
            }
        }
    
    def check_should_use_prevention(self, context: str = "general") -> Tuple[bool, str, str]:
        """
         MAIN FUNCTION: Check if you should use roster prevention right now
        
        Args:
            context: What you're about to do (sgp_creation, player_props, general_check)
            
        Returns:
            (should_use, reason, action_type)
        """
        
        config = self.config["hardcoded_automation_config"]
        
        # Check mandatory triggers first
        mandatory_result = self._check_mandatory_triggers(context, config)
        if mandatory_result[0]:
            return mandatory_result
        
        # Check time-based triggers
        time_result = self._check_time_triggers(config)
        if time_result[0]:
            return time_result
        
        # Check game-specific triggers
        game_result = self._check_game_triggers(config)
        if game_result[0]:
            return game_result
        
        # Check problem player triggers
        problem_result = self._check_problem_player_triggers(config)
        if problem_result[0]:
            return problem_result
        
        # Default: No trigger
        return False, "No hardcoded triggers activated", "none"
    
    def _check_mandatory_triggers(self, context: str, config: Dict) -> Tuple[bool, str, str]:
        """Check mandatory triggers that ALWAYS activate"""
        
        mandatory = config.get("mandatory_triggers", {}).get("triggers", {})
        
        # SGP Creation - ALWAYS trigger
        if context in ["sgp_creation", "creating_sgp", "sgp"]:
            if mandatory.get("before_sgp_creation", {}).get("enabled", False):
                return True, " MANDATORY: SGP creation requires roster verification", "run_full_prevention"
        
        # Player Props - ALWAYS trigger
        if context in ["player_props", "props", "betting_props"]:
            if mandatory.get("before_player_props", {}).get("enabled", False):
                return True, " MANDATORY: Player props require status verification", "run_quick_check"
        
        # Problem Players - ALWAYS trigger if mentioned
        problem_players = ["DK Metcalf", "Terry McLaurin", "Tyler Lockett", "Isiah Pacheco", "Stefon Diggs"]
        if any(player.lower() in context.lower() for player in problem_players):
            return True, " MANDATORY: Problem player detected in context", "run_quick_check"
        
        return False, "", ""
    
    def _check_time_triggers(self, config: Dict) -> Tuple[bool, str, str]:
        """Check time-based triggers"""
        
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        time_triggers = config.get("time_based_triggers", {}).get("triggers", {})
        
        # Daily morning check
        morning_trigger = time_triggers.get("daily_morning_check", {})
        if morning_trigger.get("enabled", False):
            trigger_time = morning_trigger.get("time", "09:00")
            if current_time == trigger_time:
                return True, " SCHEDULED: Daily morning roster check", "run_full_prevention"
        
        # Check if we're within game windows (simplified - assumes games today)
        # In production, this would check actual game schedule
        current_hour = now.hour
        
        # Pre-game window (2 hours before typical game times)
        if current_hour in [14, 17, 20]:  # 2 hours before 4pm, 7pm, 10pm games
            return True, " SCHEDULED: Pre-game verification window", "run_full_prevention"
        
        # Final check window (90 minutes before)
        if current_hour in [14, 18, 21]:  # 90 minutes before games
            return True, " SCHEDULED: Final verification window", "run_quick_check"
        
        return False, "", ""
    
    def _check_game_triggers(self, config: Dict) -> Tuple[bool, str, str]:
        """Check game-specific triggers"""
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        games = config.get("game_specific_triggers", {}).get("games", {})
        
        # Check if there are games today
        for game_id, game_info in games.items():
            if current_date in game_id and game_info.get("enabled", False):
                priority = game_info.get("priority", "NORMAL")
                
                if priority in ["HIGH", "MAXIMUM"]:
                    return True, f" GAME DAY: {game_id} requires verification", "run_full_prevention"
        
        return False, "", ""
    
    def _check_problem_player_triggers(self, config: Dict) -> Tuple[bool, str, str]:
        """Check if any problem players require attention"""
        
        problem_players = config.get("problem_player_database", {}).get("players", {})
        
        # Count high-confidence inactive players
        inactive_count = 0
        for player, info in problem_players.items():
            if info.get("status") == "INACTIVE" and info.get("confidence", 0) >= 95:
                inactive_count += 1
        
        if inactive_count > 0:
            return True, f" DETECTED: {inactive_count} high-confidence inactive players", "run_quick_check"
        
        return False, "", ""
    
    def get_current_recommendations(self) -> List[str]:
        """Get current recommendations based on hardcoded rules"""
        
        should_use, reason, action = self.check_should_use_prevention()
        
        recommendations = []
        
        if should_use:
            recommendations.append(f" YES - Use roster prevention: {reason}")
            recommendations.append(f" Recommended action: {action}")
            
            if action == "run_full_prevention":
                recommendations.append(" Run: python nfl_roster_prevention_system.py")
                recommendations.append(" Or: .\\nfl_roster_prevention_simple.ps1 -Action Prevent")
            elif action == "run_quick_check":
                recommendations.append(" Run: .\\nfl_roster_prevention_simple.ps1 -Action QuickCheck")
        else:
            recommendations.append(f" NO - No triggers active: {reason}")
            recommendations.append(" System will automatically check for triggers")
        
        # Add problem player warnings
        config = self.config["hardcoded_automation_config"]
        problem_players = config.get("problem_player_database", {}).get("players", {})
        
        inactive_players = [
            player for player, info in problem_players.items()
            if info.get("status") == "INACTIVE"
        ]
        
        if inactive_players:
            recommendations.append(f" ALWAYS AVOID: {', '.join(inactive_players)}")
        
        return recommendations
    
    def display_hardcoded_status(self) -> None:
        """Display current hardcoded trigger status"""
        
        print("\n HARDCODED TRIGGER STATUS CHECK")
        print("="*60)
        
        now = datetime.now()
        print(f" Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check current status
        should_use, reason, action = self.check_should_use_prevention()
        
        print(f"\n TRIGGER CHECK RESULT:")
        print(f"   Status: {' ACTIVATE' if should_use else ' STANDBY'}")
        print(f"   Reason: {reason}")
        print(f"   Action: {action}")
        
        # Show recommendations
        recommendations = self.get_current_recommendations()
        print(f"\n CURRENT RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"   {rec}")
        
        # Show problem players
        config = self.config["hardcoded_automation_config"]
        problem_players = config.get("problem_player_database", {}).get("players", {})
        
        print(f"\n PROBLEM PLAYERS MONITOR:")
        for player, info in problem_players.items():
            status = info.get("status", "UNKNOWN")
            confidence = info.get("confidence", 0)
            team = info.get("team", "")
            
            status_icon = "" if status == "INACTIVE" else "" if status == "QUESTIONABLE" else ""
            print(f"   {status_icon} {player} ({team}): {status} - {confidence}% confidence")
    
    def quick_context_check(self, what_youre_doing: str) -> None:
        """Quick check for specific context"""
        
        print(f"\n QUICK CHECK: {what_youre_doing.upper()}")
        print("-" * 50)
        
        should_use, reason, action = self.check_should_use_prevention(what_youre_doing.lower())
        
        if should_use:
            print(f" YES - {reason}")
            print(f" Action: {action}")
            
            if action == "run_full_prevention":
                print(f" Command: python nfl_roster_prevention_system.py")
            elif action == "run_quick_check":
                print(f" Command: .\\nfl_roster_prevention_simple.ps1 -Action QuickCheck")
        else:
            print(f" NO - {reason}")
            print(" Continue without prevention system")


def main():
    """Main demonstration"""
    
    print(" Starting Hardcoded Trigger Checker...")
    
    checker = HardcodedTriggerChecker()
    
    # Show current status
    checker.display_hardcoded_status()
    
    # Test specific scenarios
    test_scenarios = [
        "sgp_creation",
        "player_props", 
        "general_check",
        "DK Metcalf prop bet",
        "random betting"
    ]
    
    print(f"\n TESTING SCENARIOS:")
    print("="*60)
    
    for scenario in test_scenarios:
        checker.quick_context_check(scenario)
        print()


if __name__ == "__main__":
    main()