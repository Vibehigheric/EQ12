#!/usr/bin/env python3
"""
 EQ12 Enhanced NBA Monitoring with Comprehensive Player Gatekeeper
Real-time monitoring with multi-source player validation
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add scripts to path
sys.path.append('C:/EQ12/scripts')

try:
    from eq12_nba_continuous_monitoring import NBAMonitoringSystem
    from eq12_comprehensive_player_gatekeeper import ComprehensivePlayerGatekeeper
    ENHANCED_MONITORING_AVAILABLE = True
except ImportError as e:
    ENHANCED_MONITORING_AVAILABLE = False
    print(f" Enhanced monitoring components not available: {e}")


class EnhancedNBAMonitoring(NBAMonitoringSystem):
    """
     Enhanced NBA monitoring with comprehensive player gatekeeper
    Extends base monitoring with multi-source validation
    """
    
    def __init__(self, workspace: str = "C:/EQ12"):
        super().__init__(workspace)
        
        if ENHANCED_MONITORING_AVAILABLE:
            # Initialize comprehensive gatekeeper
            self.gatekeeper = ComprehensivePlayerGatekeeper(workspace)
            self.logger.info(" Enhanced monitoring with comprehensive gatekeeper")
        else:
            self.gatekeeper = None
            self.logger.warning(" Comprehensive gatekeeper not available")
    
    async def scan_for_updates_enhanced(self) -> dict:
        """Enhanced scan with comprehensive player validation"""
        if not self.gatekeeper:
            # Fallback to original method
            return await super().scan_for_updates()
        
        self.logger.info(" ENHANCED SCAN: Multi-source player validation")
        
        try:
            # Generate comprehensive SGP slate
            comprehensive_slate = self.gatekeeper.validate_sgp_slate_comprehensive()
            
            # Create validation summary for Telegram
            validation_summary = self._create_enhanced_summary(comprehensive_slate)
            
            self.logger.info(" Enhanced scan completed with comprehensive validation")
            return validation_summary
            
        except Exception as e:
            self.logger.error(f" Enhanced scan failed: {e}")
            # Fallback to original method
            return await super().scan_for_updates()
    
    def _create_enhanced_summary(self, comprehensive_slate: dict) -> dict:
        """Create enhanced summary for Telegram notifications"""
        base_slate = comprehensive_slate.get("base_slate", {})
        enhanced_validation = comprehensive_slate.get("enhanced_validation", {})
        
        # Count validation results
        available_players = []
        unavailable_players = []
        low_confidence_players = []
        
        for player, validation in enhanced_validation.items():
            decision = validation["final_decision"]
            if decision["available"]:
                available_players.append({
                    "name": player,
                    "confidence": decision["confidence"],
                    "consensus": decision["consensus"]
                })
            else:
                unavailable_players.append({
                    "name": player,
                    "confidence": decision["confidence"],
                    "reason": decision["reasoning"]
                })
            
            if decision["confidence"] < 80:
                low_confidence_players.append(player)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "validation_type": "COMPREHENSIVE_MULTI_SOURCE",
            "games": {
                "analyzed": base_slate.get("games_analyzed", 0),
                "approved": base_slate.get("games_approved", 0),
                "sgps": base_slate.get("sgps", {})
            },
            "player_validation": {
                "total_validated": len(enhanced_validation),
                "available": len(available_players),
                "unavailable": len(unavailable_players),
                "low_confidence": len(low_confidence_players),
                "available_players": available_players,
                "unavailable_players": unavailable_players
            },
            "alerts": self._generate_alerts(unavailable_players, low_confidence_players)
        }
    
    def _generate_alerts(self, unavailable_players: list, low_confidence_players: list) -> list:
        """Generate alert messages for significant changes"""
        alerts = []
        
        # Alert for unavailable players
        if unavailable_players:
            high_profile_out = [p for p in unavailable_players if "lebron" in p["name"].lower() or "davis" in p["name"].lower()]
            if high_profile_out:
                alerts.append({
                    "type": "HIGH_PROFILE_OUT",
                    "message": f" Star players OUT: {', '.join(p['name'] for p in high_profile_out)}",
                    "severity": "HIGH"
                })
        
        # Alert for low confidence validations
        if len(low_confidence_players) > 3:
            alerts.append({
                "type": "LOW_CONFIDENCE",
                "message": f" {len(low_confidence_players)} players with uncertain status",
                "severity": "MEDIUM"
            })
        
        return alerts
    
    def format_enhanced_telegram_update(self, enhanced_summary: dict) -> str:
        """Format enhanced summary for Telegram"""
        message = " *EQ12 ENHANCED NBA MONITORING UPDATE*\n\n"
        
        # Timestamp
        timestamp = datetime.fromisoformat(enhanced_summary["timestamp"])
        message += f" {timestamp.strftime('%m/%d/%Y %I:%M %p')}\n"
        message += f" Multi-source validation: {enhanced_summary['validation_type']}\n\n"
        
        # Games summary
        games = enhanced_summary["games"]
        message += f" *GAMES SUMMARY:*\n"
        message += f" Analyzed: {games['analyzed']} | Approved: {games['approved']}\n\n"
        
        # Player validation summary
        validation = enhanced_summary["player_validation"]
        message += f" *PLAYER VALIDATION:*\n"
        message += f" Available: {validation['available']}\n"
        message += f" Unavailable: {validation['unavailable']}\n"
        message += f" Low Confidence: {validation['low_confidence']}\n\n"
        
        # Unavailable players
        if validation["unavailable_players"]:
            message += f" *UNAVAILABLE PLAYERS:*\n"
            for player in validation["unavailable_players"][:5]:  # Top 5
                conf = player["confidence"]
                message += f"    {player['name']} ({conf:.0f}%)\n"
            if len(validation["unavailable_players"]) > 5:
                message += f"   ... and {len(validation['unavailable_players']) - 5} more\n"
            message += "\n"
        
        # Alerts
        alerts = enhanced_summary.get("alerts", [])
        if alerts:
            message += f" *ALERTS:*\n"
            for alert in alerts:
                message += f"   {alert['message']}\n"
            message += "\n"
        
        # SGP summary
        sgps = games.get("sgps", {})
        if sgps:
            message += f" *APPROVED SGPs ({len(sgps)}):*\n"
            for game, sgp_data in list(sgps.items())[:3]:  # Top 3 games
                legs = len(sgp_data.get("legs", []))
                odds = sgp_data.get("estimated_odds", "N/A")
                confidence = sgp_data.get("confidence", 0)
                message += f"    {game}: {legs} legs | {odds} | {confidence}%\n"
            
            if len(sgps) > 3:
                message += f"   ... and {len(sgps) - 3} more games\n"
        
        message += f"\n *All players roster-validated with multi-source checking*"
        
        return message


async def main():
    """Main enhanced monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced NBA Monitoring")
    parser.add_argument("--workspace", default="C:/EQ12", help="Workspace path")
    parser.add_argument("--test", action="store_true", help="Run single test scan")
    parser.add_argument("--schedule", action="store_true", help="Start scheduled monitoring")
    parser.add_argument("--interval", type=int, default=120, help="Scan interval in minutes")
    
    args = parser.parse_args()
    
    print(" EQ12 ENHANCED NBA MONITORING SYSTEM")
    print("=" * 60)
    print("Features: Multi-source player validation, comprehensive gatekeeper")
    
    if not ENHANCED_MONITORING_AVAILABLE:
        print(" Enhanced monitoring components not available")
        return
    
    # Initialize enhanced monitoring
    monitor = EnhancedNBAMonitoring(args.workspace)
    
    if args.test:
        print("\n Running enhanced test scan...")
        
        # Run enhanced scan
        results = await monitor.scan_for_updates_enhanced()
        
        # Display results
        print(f"\n ENHANCED SCAN RESULTS:")
        print(f"   Validation Type: {results.get('validation_type', 'N/A')}")
        print(f"   Games Approved: {results.get('games', {}).get('approved', 0)}")
        
        validation = results.get('player_validation', {})
        print(f"   Players Available: {validation.get('available', 0)}")
        print(f"   Players Unavailable: {validation.get('unavailable', 0)}")
        
        # Show alerts
        alerts = results.get('alerts', [])
        if alerts:
            print(f"\n ALERTS:")
            for alert in alerts:
                print(f"   {alert['message']}")
        
        # Generate Telegram message
        telegram_message = monitor.format_enhanced_telegram_update(results)
        print(f"\n TELEGRAM MESSAGE PREVIEW:")
        print(telegram_message)
        
        # Send actual Telegram message if configured
        if monitor.telegram_config.get('bot_token') and 'YOUR_BOT_TOKEN' not in monitor.telegram_config.get('bot_token', ''):
            print(f"\n Sending Telegram update...")
            success = monitor.send_telegram_update(telegram_message)
            if success:
                print(" Telegram message sent successfully")
            else:
                print(" Failed to send Telegram message")
    
    elif args.schedule:
        print(f"\n Starting scheduled monitoring (every {args.interval} minutes)...")
        print("   Enhanced validation with comprehensive gatekeeper")
        print("   Press Ctrl+C to stop")
        
        try:
            import schedule
            import time
            
            # Schedule enhanced scans
            schedule.every(args.interval).minutes.do(
                lambda: asyncio.run(monitor.scan_for_updates_enhanced())
            )
            
            print(f" Scheduled monitoring started")
            
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            print(f"\n Monitoring stopped by user")
        except Exception as e:
            print(f"\n Monitoring error: {e}")
    
    else:
        print("\n Use --test for single scan or --schedule for continuous monitoring")
        print("   Enhanced features: Multi-source validation, comprehensive alerts")


if __name__ == "__main__":
    asyncio.run(main())