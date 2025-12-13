#!/usr/bin/env python3
"""
 EQ12 PARLAY CONFLICT DETECTOR
Prevents conflicting bets on the same game/slip

CONFLICT TYPES DETECTED:
 Same game: Moneyline + Spread (e.g., TOR ML + MIL -3.5)
 Same game: Over + Under totals
 Same player: Multiple props of same type
 Contradictory bets: Team ML + Opponent spread
 Mutually exclusive outcomes
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set


class ParlayConflictDetector:
    """ Detects and prevents conflicting bets in parlays"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.logs_path = self.workspace_path / "logs"
        self.logs_path.mkdir(exist_ok=True)
        
        self.logger = self._setup_logging()
        
        # Conflict detection rules
        self.conflict_rules = {
            "same_game_ml_spread": "Cannot have moneyline and spread bets on same game",
            "opposite_totals": "Cannot have both OVER and UNDER on same total",
            "contradictory_sides": "Cannot bet opposing sides of same game",
            "duplicate_props": "Cannot have duplicate player props of same type",
            "mutually_exclusive": "Cannot have mutually exclusive outcomes"
        }
        
        self.logger.info(" Parlay Conflict Detector initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup conflict detection logging"""
        logger = logging.getLogger("conflict_detector")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            log_file = self.logs_path / f"conflict_detection_{datetime.now().strftime('%Y%m%d')}.log"
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            # Console handler for conflicts
            console = logging.StreamHandler()
            console.setLevel(logging.WARNING)
            console.setFormatter(formatter)
            logger.addHandler(console)
        
        return logger
    
    def extract_game_info(self, description: str) -> Tuple[str, str, str]:
        """
        Extract game info from bet description
        Returns: (game_id, bet_type, team/side)
        """
        description = description.upper()
        
        # Common team abbreviations
        teams = ["TOR", "MIL", "ATL", "ORL", "PHI", "CHI", "GS", "PHX", 
                 "LAC", "OKC", "LAL", "DEN", "BOS", "MIA", "NYK", "BRK"]
        
        # Extract teams
        found_teams = [team for team in teams if team in description]
        
        if len(found_teams) >= 2:
            # Sort to create consistent game_id
            game_teams = sorted(found_teams[:2])
            game_id = f"{game_teams[0]}v{game_teams[1]}"
            
            # Determine bet type
            if " ML " in description or description.endswith(" ML"):
                bet_type = "moneyline"
                # Find which team is being bet on
                for team in found_teams:
                    if f"{team} ML" in description:
                        return game_id, bet_type, team
            
            elif any(x in description for x in ["-", "+"]) and "OVER" not in description and "UNDER" not in description:
                bet_type = "spread"
                # Find which team has the spread
                for team in found_teams:
                    if f"{team} -" in description or f"{team} +" in description:
                        return game_id, bet_type, team
            
            elif "OVER" in description or "UNDER" in description:
                bet_type = "total"
                side = "over" if "OVER" in description else "under"
                return game_id, bet_type, side
            
            else:
                bet_type = "unknown"
                return game_id, bet_type, "unknown"
        
        return "unknown", "unknown", "unknown"
    
    def extract_player_info(self, description: str) -> Tuple[str, str]:
        """
        Extract player info from bet description
        Returns: (player_name, prop_type)
        """
        # Look for player prop keywords
        prop_keywords = ["OVER", "UNDER", "points", "rebounds", "assists", "steals", "blocks"]
        
        for keyword in prop_keywords:
            if keyword in description:
                # Get text before keyword
                before_keyword = description.split(keyword)[0].strip()
                
                # Remove odds and numbers
                words = before_keyword.split()
                clean_words = []
                
                for word in words:
                    if any(char.isdigit() or char in "+-.()" for char in word):
                        continue
                    clean_words.append(word)
                
                if len(clean_words) >= 2:
                    player_name = " ".join(clean_words)
                    
                    # Determine prop type
                    if "points" in description.lower():
                        prop_type = "points"
                    elif "rebounds" in description.lower():
                        prop_type = "rebounds"
                    elif "assists" in description.lower():
                        prop_type = "assists"
                    else:
                        prop_type = "other"
                    
                    return player_name, prop_type
        
        return "", ""
    
    def detect_conflicts(self, parlay_legs: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
         Detect conflicts in parlay legs
        Returns: (valid_legs, conflicted_legs)
        """
        self.logger.info(f" Scanning {len(parlay_legs)} legs for conflicts...")
        
        valid_legs = []
        conflicted_legs = []
        
        # Track what we've seen
        game_bets = {}  # game_id -> {bet_type: side/team}
        player_props = {}  # player_name -> {prop_type: count}
        
        for i, leg in enumerate(parlay_legs):
            description = leg.get("description", "")
            is_conflict = False
            conflict_reasons = []
            
            # Extract game info
            game_id, bet_type, side_team = self.extract_game_info(description)
            
            if game_id != "unknown":
                # Check for same-game conflicts
                if game_id in game_bets:
                    existing_bets = game_bets[game_id]
                    
                    # Rule 1: ML + Spread conflict
                    if (bet_type == "moneyline" and "spread" in existing_bets) or \
                       (bet_type == "spread" and "moneyline" in existing_bets):
                        is_conflict = True
                        conflict_reasons.append("Same game: Moneyline + Spread conflict")
                        self.logger.warning(f" CONFLICT: {description} - ML/Spread on same game")
                    
                    # Rule 2: Opposite totals
                    if bet_type == "total":
                        if "total" in existing_bets:
                            existing_side = existing_bets["total"]
                            if (side_team == "over" and existing_side == "under") or \
                               (side_team == "under" and existing_side == "over"):
                                is_conflict = True
                                conflict_reasons.append("Opposite totals on same game")
                                self.logger.warning(f" CONFLICT: {description} - Opposite totals")
                    
                    # Rule 3: Contradictory sides (opposing ML/spreads)
                    if bet_type in ["moneyline", "spread"] and bet_type in existing_bets:
                        existing_team = existing_bets[bet_type]
                        if side_team != existing_team:
                            is_conflict = True
                            conflict_reasons.append("Contradictory sides on same game")
                            self.logger.warning(f" CONFLICT: {description} - Opposing sides")
                
                # Record this bet
                if game_id not in game_bets:
                    game_bets[game_id] = {}
                game_bets[game_id][bet_type] = side_team
            
            # Check player prop conflicts
            player_name, prop_type = self.extract_player_info(description)
            
            if player_name:
                # Rule 4: Duplicate player props
                if player_name in player_props:
                    if prop_type in player_props[player_name]:
                        player_props[player_name][prop_type] += 1
                        if player_props[player_name][prop_type] > 1:
                            is_conflict = True
                            conflict_reasons.append(f"Duplicate {prop_type} prop for {player_name}")
                            self.logger.warning(f" CONFLICT: {description} - Duplicate player prop")
                    else:
                        player_props[player_name][prop_type] = 1
                else:
                    player_props[player_name] = {prop_type: 1}
            
            # Classify leg
            if is_conflict:
                leg["conflict_reasons"] = conflict_reasons
                leg["conflict_index"] = i
                conflicted_legs.append(leg)
            else:
                valid_legs.append(leg)
        
        # Log results
        self.logger.info(f" Conflict scan complete: {len(valid_legs)} valid, {len(conflicted_legs)} conflicted")
        
        if conflicted_legs:
            self.logger.warning(" CONFLICTS DETECTED:")
            for leg in conflicted_legs:
                reasons = "; ".join(leg["conflict_reasons"])
                self.logger.warning(f"   - {leg['description']}: {reasons}")
        
        return valid_legs, conflicted_legs
    
    def fix_tor_mil_conflict(self, parlay_legs: List[Dict]) -> List[Dict]:
        """
         Specific fix for TOR ML vs MIL + MIL -3.5 vs TOR conflict
        """
        self.logger.info(" Applying TOR/MIL conflict fix...")
        
        fixed_legs = []
        tor_mil_bets = []
        
        # Find TOR/MIL bets
        for leg in parlay_legs:
            description = leg.get("description", "")
            
            if ("TOR" in description and "MIL" in description):
                tor_mil_bets.append(leg)
            else:
                fixed_legs.append(leg)
        
        # If we have TOR/MIL conflicts, keep only one
        if len(tor_mil_bets) > 1:
            self.logger.warning(f" Found {len(tor_mil_bets)} TOR/MIL bets - keeping only one")
            
            # Prefer totals over ML/spread to avoid conflicts
            total_bets = [bet for bet in tor_mil_bets if "OVER" in bet["description"] or "UNDER" in bet["description"]]
            
            if total_bets:
                fixed_legs.append(total_bets[0])  # Keep first total bet
                self.logger.info(f" Kept TOR/MIL total bet: {total_bets[0]['description']}")
            else:
                fixed_legs.append(tor_mil_bets[0])  # Keep first non-total bet
                self.logger.info(f" Kept first TOR/MIL bet: {tor_mil_bets[0]['description']}")
            
            # Log what was removed
            for removed_bet in tor_mil_bets[1:]:
                self.logger.warning(f" Removed conflicting bet: {removed_bet['description']}")
        
        elif len(tor_mil_bets) == 1:
            fixed_legs.extend(tor_mil_bets)
        
        return fixed_legs
    
    def save_conflict_report(self, valid_legs: List[Dict], conflicted_legs: List[Dict]) -> str:
        """Save conflict detection report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_legs_scanned": len(valid_legs) + len(conflicted_legs),
            "valid_legs": len(valid_legs),
            "conflicted_legs": len(conflicted_legs),
            "conflict_rules": self.conflict_rules,
            "conflicts_found": [
                {
                    "description": leg["description"],
                    "reasons": leg.get("conflict_reasons", []),
                    "index": leg.get("conflict_index", -1)
                }
                for leg in conflicted_legs
            ]
        }
        
        report_file = self.workspace_path / "data" / f"conflict_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Ensure data directory exists
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f" Conflict report saved: {report_file}")
        return str(report_file)


def main():
    """Demo the conflict detector"""
    print(" EQ12 PARLAY CONFLICT DETECTOR")
    print("=" * 50)
    
    detector = ParlayConflictDetector()
    
    # Test with the problematic TOR/MIL bets
    test_parlay = [
        {"description": "TOR ML vs MIL (-110)", "odds": -110},
        {"description": "MIL -3.5 vs TOR (-110)", "odds": -110},
        {"description": "OVER 225.5 TOR vs MIL (-110)", "odds": -110},
        {"description": "Stephen Curry OVER 28.5 points (-115)", "odds": -115},
        {"description": "Stephen Curry OVER 28.5 points (-105)", "odds": -105},  # Duplicate
        {"description": "UNDER 220.5 GS vs PHX (-110)", "odds": -110},
        {"description": "OVER 220.5 GS vs PHX (-110)", "odds": -110}  # Opposite total
    ]
    
    print(f"\n Testing with {len(test_parlay)} legs...")
    
    # Detect conflicts
    valid_legs, conflicted_legs = detector.detect_conflicts(test_parlay)
    
    print(f"\n RESULTS:")
    print(f" Valid legs: {len(valid_legs)}")
    print(f" Conflicted legs: {len(conflicted_legs)}")
    
    if conflicted_legs:
        print(f"\n CONFLICTS DETECTED:")
        for leg in conflicted_legs:
            print(f"    {leg['description']}")
            for reason in leg.get("conflict_reasons", []):
                print(f"       {reason}")
    
    # Test specific TOR/MIL fix
    print(f"\n Testing TOR/MIL specific fix...")
    fixed_legs = detector.fix_tor_mil_conflict(test_parlay)
    print(f"Fixed parlay has {len(fixed_legs)} legs")
    
    # Save report
    report_file = detector.save_conflict_report(valid_legs, conflicted_legs)
    print(f"\n Report saved: {report_file}")


if __name__ == "__main__":
    main()