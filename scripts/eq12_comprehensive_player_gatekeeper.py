#!/usr/bin/env python3
"""
 EQ12 Comprehensive Player Gatekeeper - Integrated Multi-Source Validation
Complete solution combining all 3 levels with enhanced status checking
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add scripts to path
sys.path.append('C:/EQ12/scripts')

try:
    from eq12_player_status_checker import PlayerStatusChecker
    from eq12_player_availability import PlayerAvailabilityManager
    from eq12_roster_validated_sgp_generator_enhanced import RosterValidatedSGPGenerator
    ALL_COMPONENTS_AVAILABLE = True
except ImportError as e:
    ALL_COMPONENTS_AVAILABLE = False
    print(f" Some gatekeeper components not available: {e}")


class ComprehensivePlayerGatekeeper:
    """
     Master player gatekeeper integrating all validation levels
    Combines enhanced status checking with existing 3-level system
    """
    
    def __init__(self, workspace: str = "C:/EQ12"):
        self.workspace = Path(workspace)
        self.logs_path = self.workspace / "logs"
        self.logs_path.mkdir(exist_ok=True)
        
        self.setup_logging()
        
        if ALL_COMPONENTS_AVAILABLE:
            # Initialize all gatekeeper components
            self.status_checker = PlayerStatusChecker(workspace)
            self.availability_manager = PlayerAvailabilityManager(workspace)
            self.sgp_generator = RosterValidatedSGPGenerator(workspace)
            
            self.logger.info(" All gatekeeper components initialized")
        else:
            self.logger.error(" Missing gatekeeper components")
    
    def setup_logging(self):
        """Configure logging"""
        log_file = self.logs_path / f"comprehensive_gatekeeper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def validate_player_comprehensive(self, player_name: str, team: str = "") -> Dict[str, Any]:
        """
         Comprehensive multi-level player validation
        Combines all gatekeeper systems for definitive result
        """
        if not ALL_COMPONENTS_AVAILABLE:
            return {"error": "Components not available"}
        
        validation_result = {
            "player_name": player_name,
            "team": team,
            "timestamp": datetime.now().isoformat(),
            "validation_levels": {},
            "final_decision": None,
            "confidence": 0
        }
        
        # Level 1: Enhanced Status Checker (Multi-source)
        try:
            enhanced_status = self.status_checker.get_player_status_detailed(player_name, team)
            validation_result["validation_levels"]["level_1_enhanced"] = {
                "status": enhanced_status["status"],
                "playing": enhanced_status["playing"],
                "source": enhanced_status["source"],
                "reason": enhanced_status["reason"],
                "confidence": 95 if enhanced_status["source"] != "not_found" else 60
            }
        except Exception as e:
            self.logger.warning(f" Level 1 Enhanced failed: {e}")
            validation_result["validation_levels"]["level_1_enhanced"] = {
                "error": str(e),
                "confidence": 0
            }
        
        # Level 2: Original Availability Manager
        try:
            availability_status = self.availability_manager.get_player_status(player_name, team)
            is_available = self.availability_manager.is_player_available(player_name, team)
            validation_result["validation_levels"]["level_2_availability"] = {
                "status": availability_status["status"],
                "available": is_available,
                "source": availability_status["source"],
                "confidence": 85
            }
        except Exception as e:
            self.logger.warning(f" Level 2 Availability failed: {e}")
            validation_result["validation_levels"]["level_2_availability"] = {
                "error": str(e),
                "confidence": 0
            }
        
        # Level 3: SGP Generator Validation
        try:
            sgp_availability = self.sgp_generator.validate_player_availability(player_name, team)
            validation_result["validation_levels"]["level_3_sgp"] = {
                "available": sgp_availability["available"],
                "status": sgp_availability["status"],
                "reason": sgp_availability["reason"],
                "source": sgp_availability["source"],
                "confidence": 80
            }
        except Exception as e:
            self.logger.warning(f" Level 3 SGP failed: {e}")
            validation_result["validation_levels"]["level_3_sgp"] = {
                "error": str(e),
                "confidence": 0
            }
        
        # Aggregate results for final decision
        final_decision = self._aggregate_validation_results(validation_result["validation_levels"])
        validation_result["final_decision"] = final_decision
        
        return validation_result
    
    def _aggregate_validation_results(self, levels: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate validation results from all levels"""
        decisions = []
        total_confidence = 0
        
        for level_name, level_data in levels.items():
            if "error" in level_data:
                continue
            
            confidence = level_data.get("confidence", 0)
            
            if level_name == "level_1_enhanced":
                available = level_data.get("playing", True)
            elif level_name == "level_2_availability":
                available = level_data.get("available", True)
            elif level_name == "level_3_sgp":
                available = level_data.get("available", True)
            else:
                available = True
            
            decisions.append({
                "level": level_name,
                "available": available,
                "confidence": confidence
            })
            total_confidence += confidence
        
        if not decisions:
            return {
                "available": True,
                "confidence": 0,
                "consensus": "no_data",
                "reasoning": "No validation data available - defaulting to available"
            }
        
        # Calculate weighted decision
        weighted_available = sum(d["available"] * d["confidence"] for d in decisions)
        weighted_total = sum(d["confidence"] for d in decisions)
        
        if weighted_total == 0:
            final_available = True
            confidence = 0
        else:
            final_available = (weighted_available / weighted_total) > 0.5
            confidence = min(100, total_confidence / len(decisions))
        
        # Determine consensus
        available_count = sum(1 for d in decisions if d["available"])
        total_count = len(decisions)
        
        if available_count == total_count:
            consensus = "unanimous_available"
        elif available_count == 0:
            consensus = "unanimous_unavailable"
        elif available_count > total_count / 2:
            consensus = "majority_available"
        else:
            consensus = "majority_unavailable"
        
        return {
            "available": final_available,
            "confidence": confidence,
            "consensus": consensus,
            "reasoning": f"{available_count}/{total_count} systems indicate available",
            "weighted_score": weighted_available / weighted_total if weighted_total > 0 else 0.5
        }
    
    def validate_sgp_slate_comprehensive(self, games: List[str] = None) -> Dict[str, Any]:
        """Generate comprehensive validated SGP slate"""
        if not ALL_COMPONENTS_AVAILABLE:
            return {"error": "Components not available"}
        
        self.logger.info(" Generating comprehensive validated SGP slate...")
        
        # Get the base SGP slate
        sgp_slate = self.sgp_generator.generate_clean_sgp_slate()
        
        # Add comprehensive validation to each player
        comprehensive_slate = {
            "timestamp": datetime.now().isoformat(),
            "validation_type": "COMPREHENSIVE_MULTI_SOURCE",
            "base_slate": sgp_slate,
            "enhanced_validation": {}
        }
        
        # Extract all players from SGPs and validate comprehensively
        all_players = set()
        for game, sgp_data in sgp_slate.get("sgps", {}).items():
            for leg in sgp_data.get("legs", []):
                if leg.get("player_name"):
                    all_players.add(leg["player_name"])
        
        # Comprehensive validation for each player
        for player in all_players:
            validation = self.validate_player_comprehensive(player)
            comprehensive_slate["enhanced_validation"][player] = validation
            
            # Log results
            final_decision = validation["final_decision"]
            confidence = final_decision["confidence"]
            available = final_decision["available"]
            
            self.logger.info(f" {player}: {' AVAILABLE' if available else ' UNAVAILABLE'} (confidence: {confidence:.1f}%)")
        
        return comprehensive_slate
    
    def create_validation_report(self, players: List[str] = None) -> Dict[str, Any]:
        """Create comprehensive validation report for specified players"""
        if not players:
            # Use default set of key players
            players = [
                "LeBron James", "Anthony Davis", "Nikola Jokic", 
                "Jayson Tatum", "Damian Lillard", "De'Aaron Fox",
                "Keegan Murray", "Walker Kessler"
            ]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "validation_type": "COMPREHENSIVE_MULTI_SOURCE",
            "players_validated": len(players),
            "validations": {},
            "summary": {
                "available": 0,
                "unavailable": 0,
                "high_confidence": 0,
                "low_confidence": 0
            }
        }
        
        for player in players:
            validation = self.validate_player_comprehensive(player)
            report["validations"][player] = validation
            
            # Update summary
            if validation["final_decision"]["available"]:
                report["summary"]["available"] += 1
            else:
                report["summary"]["unavailable"] += 1
            
            if validation["final_decision"]["confidence"] >= 80:
                report["summary"]["high_confidence"] += 1
            else:
                report["summary"]["low_confidence"] += 1
        
        return report


def main():
    """CLI interface for comprehensive gatekeeper"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive Player Gatekeeper")
    parser.add_argument("--workspace", default="C:/EQ12", help="Workspace path")
    parser.add_argument("--player", help="Validate specific player")
    parser.add_argument("--players", nargs="+", help="Validate multiple players")
    parser.add_argument("--sgp-slate", action="store_true", help="Generate comprehensive SGP slate")
    parser.add_argument("--report", action="store_true", help="Generate validation report")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    print(" EQ12 COMPREHENSIVE PLAYER GATEKEEPER")
    print("=" * 60)
    
    if not ALL_COMPONENTS_AVAILABLE:
        print(" Not all gatekeeper components available")
        return
    
    gatekeeper = ComprehensivePlayerGatekeeper(args.workspace)
    
    if args.player:
        # Validate single player
        validation = gatekeeper.validate_player_comprehensive(args.player)
        
        print(f"\n COMPREHENSIVE VALIDATION: {args.player}")
        print(f"   Final Decision: {' AVAILABLE' if validation['final_decision']['available'] else ' UNAVAILABLE'}")
        print(f"   Confidence: {validation['final_decision']['confidence']:.1f}%")
        print(f"   Consensus: {validation['final_decision']['consensus']}")
        print(f"   Reasoning: {validation['final_decision']['reasoning']}")
        
        print(f"\n VALIDATION LEVELS:")
        for level_name, level_data in validation["validation_levels"].items():
            if "error" not in level_data:
                status = " PASS" if level_data.get("available", level_data.get("playing", True)) else " FAIL"
                confidence = level_data.get("confidence", 0)
                print(f"   {level_name}: {status} (confidence: {confidence}%)")
    
    elif args.players:
        # Validate multiple players
        report = gatekeeper.create_validation_report(args.players)
        
        print(f"\n VALIDATION REPORT ({len(args.players)} players)")
        print(f"   Available: {report['summary']['available']}")
        print(f"   Unavailable: {report['summary']['unavailable']}")
        print(f"   High Confidence: {report['summary']['high_confidence']}")
        
        print(f"\n PLAYER RESULTS:")
        for player, validation in report["validations"].items():
            decision = validation["final_decision"]
            status = " AVAILABLE" if decision["available"] else " UNAVAILABLE"
            confidence = decision["confidence"]
            print(f"   {player}: {status} ({confidence:.1f}%)")
    
    elif args.sgp_slate:
        # Generate comprehensive SGP slate
        comprehensive_slate = gatekeeper.validate_sgp_slate_comprehensive()
        
        base_slate = comprehensive_slate["base_slate"]
        print(f"\n COMPREHENSIVE SGP SLATE")
        print(f"   Games Approved: {base_slate.get('games_approved', 0)}")
        print(f"   Validation Type: {comprehensive_slate['validation_type']}")
        
        print(f"\n ENHANCED PLAYER VALIDATION:")
        for player, validation in comprehensive_slate["enhanced_validation"].items():
            decision = validation["final_decision"]
            status = "" if decision["available"] else ""
            confidence = decision["confidence"]
            print(f"   {status} {player} ({confidence:.1f}%)")
    
    elif args.report:
        # Generate default validation report
        report = gatekeeper.create_validation_report()
        
        print(f"\n COMPREHENSIVE VALIDATION REPORT")
        print(f"   Players Validated: {report['players_validated']}")
        print(f"   Available: {report['summary']['available']}")
        print(f"   Unavailable: {report['summary']['unavailable']}")
        print(f"   High Confidence (80%): {report['summary']['high_confidence']}")
        print(f"   Low Confidence (<80%): {report['summary']['low_confidence']}")
        
        print(f"\n KEY PLAYER STATUS:")
        for player, validation in report["validations"].items():
            decision = validation["final_decision"]
            status = " AVAILABLE" if decision["available"] else " UNAVAILABLE"  
            confidence = decision["confidence"]
            consensus = decision["consensus"]
            print(f"   {player}: {status} ({confidence:.1f}%, {consensus})")
    
    # Save output if requested
    if args.output:
        output_data = None
        if args.player:
            output_data = validation
        elif args.players:
            output_data = report
        elif args.sgp_slate:
            output_data = comprehensive_slate
        elif args.report:
            output_data = report
        
        if output_data:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"\n Results saved to: {output_path}")


if __name__ == "__main__":
    main()