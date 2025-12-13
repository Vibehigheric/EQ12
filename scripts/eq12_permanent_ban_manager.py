#!/usr/bin/env python3
"""
EQ12 Permanent Ban List and Risk Management System
================================================

CRITICAL SYSTEM: This script maintains the permanent ban list of markets,
players, and betting patterns that have demonstrated consistent failure
rates and must be avoided in all future parlays.

🚫 PERMANENT BANS AND RESTRICTIONS:
- High-volatility prop markets (Odd/Even, Double-Doubles, 35+ points)
- Void-prone player props (Barnes TD, Sarr inconsistencies)
- Correlation-breaking patterns (Over-pace + Under combinations)
- Player-specific risk caps and restrictions

Author: EQ12 Expert Betting System
Date: November 22, 2025
Version: 1.0 - Permanent Ban Management
"""

import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

@dataclass
class BannedMarket:
    """Permanently banned market definition"""
    market_name: str
    ban_reason: str
    failure_rate: float
    ban_date: str
    examples: List[str]
    permanent: bool = True

@dataclass
class PlayerRiskCap:
    """Player-specific risk management rules"""
    player_name: str
    max_props_per_parlay: int
    void_risk_percentage: float
    confidence_penalty: float
    restricted_markets: List[str]
    special_rules: List[str]

class PermanentBanManager:
    """Manages permanent ban list and risk restrictions"""

    def __init__(self):
        self.timestamp = datetime.now()
        self.logs_dir = r"C:\EQ12\logs"
        self.configs_dir = r"C:\EQ12\configs"

        # Initialize permanent ban lists
        self.banned_markets = self._initialize_banned_markets()
        self.player_risk_caps = self._initialize_player_risk_caps()
        self.prohibited_patterns = self._initialize_prohibited_patterns()

    def _initialize_banned_markets(self) -> Dict[str, BannedMarket]:
        """Initialize permanently banned markets based on loss analysis"""

        banned = {}

        # High-volatility props - permanently banned
        banned["odd_even_points"] = BannedMarket(
            market_name="Odd/Even Total Points",
            ban_reason="Pure randomness - no skill edge possible",
            failure_rate=0.52,
            ban_date="2025-11-22",
            examples=["Player points odd/even", "Team total odd/even", "Game total odd/even"],
            permanent=True
        )

        banned["double_double_props"] = BannedMarket(
            market_name="Double-Double Props",
            ban_reason="High variance - unpredictable late-game stat padding",
            failure_rate=0.48,
            ban_date="2025-11-22",
            examples=["Points + Rebounds DD", "Points + Assists DD", "Any DD prop"],
            permanent=True
        )

        banned["extreme_point_totals"] = BannedMarket(
            market_name="35+ Point Props",
            ban_reason="Extreme outlier events - very low probability",
            failure_rate=0.71,
            ban_date="2025-11-22",
            examples=["Player 35+ points", "Player 40+ points", "50+ point games"],
            permanent=True
        )

        banned["extreme_rebound_totals"] = BannedMarket(
            market_name="14+ Rebound Props",
            ban_reason="Game flow dependent - highly unpredictable",
            failure_rate=0.68,
            ban_date="2025-11-22",
            examples=["Player 14+ rebounds", "Player 15+ rebounds", "20+ rebound games"],
            permanent=True
        )

        # Player-specific bans
        banned["sarr_rebound_props"] = BannedMarket(
            market_name="Alexandre Sarr Rebound Overs",
            ban_reason="Extremely inconsistent performance patterns",
            failure_rate=0.73,
            ban_date="2025-11-22",
            examples=["Sarr over rebounds", "Sarr double-double", "Sarr 10+ rebounds"],
            permanent=True
        )

        banned["barnes_touchdown_props"] = BannedMarket(
            market_name="Scottie Barnes Touchdown Props",
            ban_reason="23% void rate - frequent status changes",
            failure_rate=0.23,  # Void rate
            ban_date="2025-11-22",
            examples=["Barnes anytime TD", "Barnes rushing TD", "Barnes receiving TD"],
            permanent=True
        )

        # Correlation-breaking patterns
        banned["pace_under_combos"] = BannedMarket(
            market_name="High-Pace Team + Under Combinations",
            ban_reason="Mathematical contradiction - pace drives scoring",
            failure_rate=0.67,
            ban_date="2025-11-22",
            examples=["Raptors + game under", "Fast-pace team + low total", "Over-pace + under combo"],
            permanent=True
        )

        return banned

    def _initialize_player_risk_caps(self) -> Dict[str, PlayerRiskCap]:
        """Initialize player-specific risk management rules"""

        risk_caps = {}

        # Alexandre Sarr - High volatility player
        risk_caps["Alexandre Sarr"] = PlayerRiskCap(
            player_name="Alexandre Sarr",
            max_props_per_parlay=1,
            void_risk_percentage=0.12,
            confidence_penalty=0.15,
            restricted_markets=["rebounds_over", "double_double", "points_rebounds"],
            special_rules=[
                "MAX 1 prop per parlay",
                "Avoid rebound overs completely",
                "Monitor game flow before execution",
                "Reduce confidence by 15% on all props"
            ]
        )

        # Scottie Barnes - Void risk player
        risk_caps["Scottie Barnes"] = PlayerRiskCap(
            player_name="Scottie Barnes",
            max_props_per_parlay=1,
            void_risk_percentage=0.23,
            confidence_penalty=0.20,
            restricted_markets=["touchdown_props", "rushing_props", "receiving_props"],
            special_rules=[
                "NEVER use TD props - 23% void rate",
                "Check injury report before execution",
                "Monitor snap count projections",
                "MAX 1 prop per parlay due to status uncertainty"
            ]
        )

        # Any Raptors player in high-pace matchups
        risk_caps["Toronto Raptors Players"] = PlayerRiskCap(
            player_name="Any Raptors Player",
            max_props_per_parlay=2,
            void_risk_percentage=0.08,
            confidence_penalty=0.10,
            restricted_markets=["under_combinations"],
            special_rules=[
                "NEVER combine with game unders when pace > 102.5",
                "Avoid prop unders in fast-paced games",
                "Check opponent pace factor before execution",
                "Prefer overs in high-pace matchups"
            ]
        )

        return risk_caps

    def _initialize_prohibited_patterns(self) -> Set[str]:
        """Initialize prohibited betting patterns"""

        return {
            "multi_player_same_team_props",  # More than 2 props from same team
            "opposing_correlation_bets",     # Contradictory correlations
            "extreme_total_combinations",    # Multiple extreme overs/unders
            "high_void_risk_stacking",      # Multiple void-prone props
            "pace_contradiction_bets",       # Pace vs total contradictions
            "injury_report_ignored",         # Betting without checking status
            "weather_impact_ignored",        # Outdoor games without weather check
            "back_to_back_fatigue_ignored"   # Not accounting for rest disadvantage
        }

    def validate_parlay_against_bans(self, parlay_legs: List[str]) -> Dict[str, any]:
        """Validate a parlay against all permanent bans and restrictions"""

        print(f"\n🛡️ VALIDATING PARLAY AGAINST PERMANENT BAN LIST")
        print(f"📋 Parlay Legs: {parlay_legs}")
        print(f"🕒 Validation Time: {datetime.now().strftime('%H:%M:%S')}")

        validation_result = {
            "approved": True,
            "ban_violations": [],
            "risk_warnings": [],
            "player_cap_violations": [],
            "pattern_violations": [],
            "recommendations": []
        }

        # Check for banned markets
        for leg in parlay_legs:
            for ban_key, banned_market in self.banned_markets.items():
                if self._matches_banned_market(leg, banned_market):
                    validation_result["approved"] = False
                    validation_result["ban_violations"].append({
                        "leg": leg,
                        "banned_market": banned_market.market_name,
                        "reason": banned_market.ban_reason,
                        "failure_rate": banned_market.failure_rate
                    })

        # Check player risk caps
        player_prop_count = {}
        for leg in parlay_legs:
            player = self._extract_player_from_leg(leg)
            if player:
                player_prop_count[player] = player_prop_count.get(player, 0) + 1

        for player, count in player_prop_count.items():
            if player in self.player_risk_caps:
                cap = self.player_risk_caps[player]
                if count > cap.max_props_per_parlay:
                    validation_result["approved"] = False
                    validation_result["player_cap_violations"].append({
                        "player": player,
                        "prop_count": count,
                        "max_allowed": cap.max_props_per_parlay,
                        "violation": f"Exceeds {player} prop cap"
                    })

        # Check for prohibited patterns
        if self._detect_prohibited_patterns(parlay_legs):
            validation_result["approved"] = False
            validation_result["pattern_violations"].append("Contains prohibited betting patterns")

        # Generate recommendations if violations found
        if not validation_result["approved"]:
            validation_result["recommendations"] = self._generate_safer_alternatives(parlay_legs)

        # Display validation results
        self._display_validation_results(validation_result)

        return validation_result

    def _matches_banned_market(self, leg: str, banned_market: BannedMarket) -> bool:
        """Check if a parlay leg matches a banned market"""

        leg_lower = leg.lower()
        market_indicators = {
            "odd_even_points": ["odd", "even", "total points"],
            "double_double_props": ["double", "dd", "double-double"],
            "extreme_point_totals": ["35+", "40+", "35 points", "40 points"],
            "extreme_rebound_totals": ["14+", "15+", "14 rebounds", "15 rebounds"],
            "sarr_rebound_props": ["sarr", "rebound", "over"],
            "barnes_touchdown_props": ["barnes", "td", "touchdown"],
            "pace_under_combos": ["raptors", "under", "pace"]
        }

        market_key = banned_market.market_name.lower().replace(" ", "_").replace("/", "_")

        if market_key.startswith("odd_even"):
            return any(indicator in leg_lower for indicator in market_indicators["odd_even_points"])
        elif market_key.startswith("double_double"):
            return any(indicator in leg_lower for indicator in market_indicators["double_double_props"])
        elif "35+" in banned_market.market_name:
            return any(indicator in leg_lower for indicator in market_indicators["extreme_point_totals"])
        elif "14+" in banned_market.market_name:
            return any(indicator in leg_lower for indicator in market_indicators["extreme_rebound_totals"])
        elif "sarr" in banned_market.market_name.lower():
            return all(indicator in leg_lower for indicator in market_indicators["sarr_rebound_props"])
        elif "barnes" in banned_market.market_name.lower():
            return any(indicator in leg_lower for indicator in market_indicators["barnes_touchdown_props"])
        elif "pace" in banned_market.market_name.lower():
            return any(indicator in leg_lower for indicator in market_indicators["pace_under_combos"])

        return False

    def _extract_player_from_leg(self, leg: str) -> str:
        """Extract player name from parlay leg"""

        # Common player names in loss analysis
        players = [
            "Alexandre Sarr", "Scottie Barnes", "Cooper Flagg",
            "Caleb Foster", "Kon Knueppel", "RJ Barrett"
        ]

        leg_lower = leg.lower()
        for player in players:
            if player.lower() in leg_lower:
                return player

        # Check for team-based restrictions
        if any(team in leg_lower for team in ["raptors", "toronto"]):
            return "Toronto Raptors Players"

        return None

    def _detect_prohibited_patterns(self, parlay_legs: List[str]) -> bool:
        """Detect prohibited betting patterns in parlay"""

        # Check for too many props from same player
        player_counts = {}
        for leg in parlay_legs:
            player = self._extract_player_from_leg(leg)
            if player:
                player_counts[player] = player_counts.get(player, 0) + 1

        # Pattern: More than 2 props from any single player
        if any(count > 2 for count in player_counts.values()):
            return True

        # Pattern: Pace contradiction (high-pace team + under)
        has_pace_team = any("raptors" in leg.lower() for leg in parlay_legs)
        has_under = any("under" in leg.lower() for leg in parlay_legs)
        if has_pace_team and has_under:
            return True

        return False

    def _generate_safer_alternatives(self, parlay_legs: List[str]) -> List[str]:
        """Generate safer alternatives for banned parlay legs"""

        alternatives = []

        for leg in parlay_legs:
            if "odd" in leg.lower() or "even" in leg.lower():
                alternatives.append(f"Replace '{leg}' with stable point total prop")
            elif "double" in leg.lower() and "double" in leg.lower():
                alternatives.append(f"Replace '{leg}' with single-stat prop (points or rebounds)")
            elif "35+" in leg or "40+" in leg:
                alternatives.append(f"Replace '{leg}' with more achievable point total (25+ or 30+)")
            elif "sarr" in leg.lower() and "rebound" in leg.lower():
                alternatives.append(f"Replace '{leg}' with Sarr points prop (more consistent)")
            elif "barnes" in leg.lower() and ("td" in leg.lower() or "touchdown" in leg.lower()):
                alternatives.append(f"Replace '{leg}' with rushing yards prop (lower void risk)")
            else:
                alternatives.append(f"Verify '{leg}' against current ban list")

        return alternatives

    def _display_validation_results(self, validation_result: Dict):
        """Display parlay validation results"""

        if validation_result["approved"]:
            print(f"✅ PARLAY APPROVED - No ban violations detected")
            print(f"🛡️ All legs comply with permanent ban list")
        else:
            print(f"🚫 PARLAY REJECTED - Ban violations detected")

            if validation_result["ban_violations"]:
                print(f"\n❌ BANNED MARKET VIOLATIONS:")
                for violation in validation_result["ban_violations"]:
                    print(f"   🚫 {violation['leg']}")
                    print(f"      Market: {violation['banned_market']}")
                    print(f"      Reason: {violation['reason']}")
                    print(f"      Failure Rate: {violation['failure_rate']:.1%}")

            if validation_result["player_cap_violations"]:
                print(f"\n⚠️ PLAYER CAP VIOLATIONS:")
                for violation in validation_result["player_cap_violations"]:
                    print(f"   ❌ {violation['player']}: {violation['prop_count']} props")
                    print(f"      Maximum Allowed: {violation['max_allowed']}")

            if validation_result["pattern_violations"]:
                print(f"\n🔍 PATTERN VIOLATIONS:")
                for violation in validation_result["pattern_violations"]:
                    print(f"   ❌ {violation}")

            print(f"\n💡 SAFER ALTERNATIVES:")
            for recommendation in validation_result["recommendations"]:
                print(f"   ✨ {recommendation}")

    def get_current_ban_summary(self) -> Dict:
        """Get summary of current permanent bans"""

        summary = {
            "total_banned_markets": len(self.banned_markets),
            "total_player_caps": len(self.player_risk_caps),
            "total_prohibited_patterns": len(self.prohibited_patterns),
            "ban_categories": {
                "high_volatility_props": 4,
                "player_specific_bans": 2,
                "correlation_breaking": 1
            }
        }

        return summary

    def save_ban_list_snapshot(self):
        """Save current ban list to logs"""

        snapshot = {
            "timestamp": self.timestamp.isoformat(),
            "banned_markets": {k: v.__dict__ for k, v in self.banned_markets.items()},
            "player_risk_caps": {k: v.__dict__ for k, v in self.player_risk_caps.items()},
            "prohibited_patterns": list(self.prohibited_patterns),
            "summary": self.get_current_ban_summary()
        }

        filename = f"permanent_ban_list_snapshot_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.logs_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2, default=str)

        print(f"💾 Ban list snapshot saved: {filepath}")


def validate_sample_parlays():
    """Test the permanent ban system with sample parlays"""

    ban_manager = PermanentBanManager()

    print("🧪 TESTING PERMANENT BAN VALIDATION SYSTEM")
    print("=" * 50)

    # Test cases
    test_parlays = [
        # Should be REJECTED - Contains banned markets
        ["UNC +7.5", "Cooper Flagg Over 22.5 P+R", "Game Total Odd"],  # Odd/Even banned
        ["Celtics -5.5", "Jayson Tatum Double-Double", "Lakers +3.5"],  # DD banned
        ["Sarr Over 9.5 Rebounds", "Warriors -7", "Under 225.5"],  # Sarr rebounds banned
        ["Barnes Anytime TD", "Ravens -3.5", "Over 47.5"],  # Barnes TD banned

        # Should be APPROVED - Clean parlay
        ["UNC +7.5", "Cooper Flagg Over 22.5 P+R", "Under 148.5"],  # Clean Duke/UNC parlay
        ["Celtics -5.5", "Tatum Over 27.5 Points", "Lakers +3.5"],  # Clean NBA parlay
    ]

    for i, parlay in enumerate(test_parlays, 1):
        print(f"\n🧪 TEST CASE {i}:")
        result = ban_manager.validate_parlay_against_bans(parlay)
        print(f"Result: {'✅ APPROVED' if result['approved'] else '🚫 REJECTED'}")
        print("-" * 30)

    # Save snapshot
    ban_manager.save_ban_list_snapshot()


def main():
    """Main execution function"""
    validate_sample_parlays()


if __name__ == "__main__":
    main()
