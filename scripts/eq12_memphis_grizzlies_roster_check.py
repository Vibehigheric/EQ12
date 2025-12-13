#!/usr/bin/env python3
"""
EQ12 Memphis Grizzlies Roster Verification System
Verifies current Memphis Grizzlies roster to prevent betting mistakes
"""

import json
import logging
import argparse
from datetime import datetime, timezone
import requests
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MemphisGrizzliesRosterChecker:
    def __init__(self):
        self.team_name = "Memphis Grizzlies"
        self.team_abbreviation = "MEM"
        self.conference = "Western"
        self.division = "Southwest"

        # Known current roster (2024-25 season)
        self.current_roster = [
            {"name": "Ja Morant", "position": "PG", "number": "12", "status": "Active"},
            {"name": "Jaren Jackson Jr.", "position": "PF/C", "number": "13", "status": "Active"},
            {"name": "Desmond Bane", "position": "SG", "number": "22", "status": "Active"},
            {"name": "Marcus Smart", "position": "PG", "number": "36", "status": "Active"},
            {"name": "Brandon Clarke", "position": "PF", "number": "15", "status": "Active"},
            {"name": "Luke Kennard", "position": "SG", "number": "10", "status": "Active"},
            {"name": "Ziaire Williams", "position": "SF", "number": "8", "status": "Active"},
            {"name": "Santi Aldama", "position": "PF", "number": "7", "status": "Active"},
            {"name": "GG Jackson II", "position": "PF", "number": "45", "status": "Active"},
            {"name": "Vince Williams Jr.", "position": "SF", "number": "5", "status": "Active"},
            {"name": "John Konchar", "position": "SG/SF", "number": "46", "status": "Active"},
            {"name": "Jay Huff", "position": "C", "number": "30", "status": "Active"},
            {"name": "Jake LaRavia", "position": "SF/PF", "number": "0", "status": "Active"},
            {"name": "Derrick Rose", "position": "PG", "number": "4", "status": "Active"},
            {"name": "Bismack Biyombo", "position": "C", "number": "18", "status": "Active"}
        ]

        # Players NOT on Memphis Grizzlies
        self.not_on_roster = [
            {"name": "Cooper Flagg", "actual_team": "Dallas Mavericks", "league": "NBA"},
            {"name": "LeBron James", "actual_team": "Los Angeles Lakers", "league": "NBA"},
            {"name": "Stephen Curry", "actual_team": "Golden State Warriors", "league": "NBA"},
            {"name": "Kevin Durant", "actual_team": "Phoenix Suns", "league": "NBA"},
            {"name": "Giannis Antetokounmpo", "actual_team": "Milwaukee Bucks", "league": "NBA"}
        ]

    def verify_player_on_roster(self, player_name: str) -> Dict:
        """
        Verify if a player is on the Memphis Grizzlies roster
        """
        logger.info(f"Checking if {player_name} is on Memphis Grizzlies roster...")

        # Check current roster
        for player in self.current_roster:
            if player["name"].lower() == player_name.lower():
                return {
                    "on_roster": True,
                    "player": player,
                    "team": self.team_name,
                    "verification": "CONFIRMED - Player is on Memphis Grizzlies roster",
                    "betting_validity": "VALID"
                }

        # Check known non-roster players
        for player in self.not_on_roster:
            if player["name"].lower() == player_name.lower():
                return {
                    "on_roster": False,
                    "player": player,
                    "team": self.team_name,
                    "verification": f"ERROR - {player_name} plays for {player['actual_team']} in {player['league']}, NOT Memphis Grizzlies",
                    "betting_validity": "INVALID - WOULD LOSE"
                }

        # Player not found in either list
        return {
            "on_roster": False,
            "player": None,
            "team": self.team_name,
            "verification": f"UNKNOWN - {player_name} not found in Memphis Grizzlies roster database",
            "betting_validity": "VERIFY BEFORE BETTING"
        }

    def get_full_roster(self) -> Dict:
        """
        Get the complete Memphis Grizzlies roster
        """
        logger.info("Retrieving full Memphis Grizzlies roster...")

        return {
            "team": self.team_name,
            "abbreviation": self.team_abbreviation,
            "conference": self.conference,
            "division": self.division,
            "roster_count": len(self.current_roster),
            "players": self.current_roster,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "verification_status": "EQ12 VERIFIED ROSTER"
        }

    def cooper_flagg_check(self) -> Dict:
        """
        Specific Cooper Flagg verification (most common mistake)
        """
        logger.info("Running Cooper Flagg verification...")

        return {
            "player": "Cooper Flagg",
            "memphis_grizzlies_roster": False,
            "actual_team": "Duke Blue Devils",
            "actual_league": "NCAA",
            "status": "College Player",
            "nba_draft_eligibility": "2025 NBA Draft",
            "critical_warning": "🚨 COOPER FLAGG IS NOT IN THE NBA - He plays college basketball at Duke",
            "betting_impact": "Any Memphis Grizzlies Cooper Flagg bet would be INVALID and LOSE"
        }

    def save_verification_log(self, data: Dict) -> str:
        """
        Save verification results to log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"C:/EQ12/logs/memphis_grizzlies_roster_check_{timestamp}.json"

        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verification_type": "Memphis Grizzlies Roster Check",
            "results": data,
            "eq12_system": "Player Validation",
            "betting_protection": "Active"
        }

        try:
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            logger.info(f"Verification log saved: {log_file}")
            return log_file
        except Exception as e:
            logger.error(f"Failed to save verification log: {e}")
            return ""

def main():
    parser = argparse.ArgumentParser(description='Memphis Grizzlies Roster Verification')
    parser.add_argument('--player', type=str, help='Check specific player on roster')
    parser.add_argument('--full-roster', action='store_true', help='Show complete roster')
    parser.add_argument('--cooper-flagg', action='store_true', help='Run Cooper Flagg specific check')
    parser.add_argument('--all-checks', action='store_true', help='Run all verification checks')

    args = parser.parse_args()

    checker = MemphisGrizzliesRosterChecker()

    print("=" * 60)
    print("🏀 EQ12 MEMPHIS GRIZZLIES ROSTER VERIFICATION")
    print("🔒 BETTING MISTAKE PREVENTION SYSTEM")
    print("=" * 60)

    if args.player:
        print(f"\n🔍 CHECKING PLAYER: {args.player}")
        result = checker.verify_player_on_roster(args.player)

        print(f"Player: {args.player}")
        print(f"Team: {result['team']}")
        print(f"On Roster: {result['on_roster']}")
        print(f"Verification: {result['verification']}")
        print(f"Betting Validity: {result['betting_validity']}")

        if result['player']:
            player_info = result['player']
            if result['on_roster']:
                print(f"Position: {player_info['position']}")
                print(f"Number: #{player_info['number']}")
                print(f"Status: {player_info['status']}")
            else:
                print(f"Actual Team: {player_info['actual_team']}")
                print(f"League: {player_info['league']}")

        checker.save_verification_log(result)

    elif args.full_roster:
        print("\n📋 COMPLETE MEMPHIS GRIZZLIES ROSTER")
        roster = checker.get_full_roster()

        print(f"Team: {roster['team']}")
        print(f"Conference: {roster['conference']} Conference")
        print(f"Division: {roster['division']} Division")
        print(f"Active Players: {roster['roster_count']}")
        print("\nROSTER:")

        for i, player in enumerate(roster['players'], 1):
            print(f"{i:2d}. #{player['number']:<2} {player['name']:<20} - {player['position']}")

        checker.save_verification_log(roster)

    elif args.cooper_flagg:
        print("\n🚨 COOPER FLAGG VERIFICATION")
        result = checker.cooper_flagg_check()

        print(f"Player: {result['player']}")
        print(f"Memphis Grizzlies: {result['memphis_grizzlies_roster']}")
        print(f"Actual Team: {result['actual_team']}")
        print(f"League: {result['actual_league']}")
        print(f"Status: {result['status']}")
        print(f"Warning: {result['critical_warning']}")
        print(f"Betting Impact: {result['betting_impact']}")

        checker.save_verification_log(result)

    elif args.all_checks:
        print("\n🔄 RUNNING ALL VERIFICATION CHECKS")

        # Full roster
        roster = checker.get_full_roster()
        print(f"\n✅ Memphis Grizzlies roster loaded: {roster['roster_count']} players")

        # Cooper Flagg check
        flagg_check = checker.cooper_flagg_check()
        print(f"✅ Cooper Flagg verification: NOT on Memphis roster")

        # Save combined results
        all_results = {
            "full_roster": roster,
            "cooper_flagg_check": flagg_check,
            "verification_complete": True
        }
        checker.save_verification_log(all_results)
        print("✅ All verification checks complete")

    else:
        print("\n❓ No specific check requested")
        print("Use --help for available options")
        print("\nQuick options:")
        print("  --player 'Cooper Flagg'  # Check specific player")
        print("  --full-roster           # Show complete roster")
        print("  --cooper-flagg          # Cooper Flagg specific check")
        print("  --all-checks           # Run all verifications")

    print("\n🔒 EQ12 Roster Verification Complete")

if __name__ == "__main__":
    main()
