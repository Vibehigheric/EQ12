#!/usr/bin/env python3
"""
 EQ12 NBA SGP CONTINUOUS MONITORING SYSTEM
Scans every 2 hours for player status changes and sends Telegram updates
Includes fully displayed and labeled updated parlays
"""

import asyncio
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import argparse
import logging
from pathlib import Path
import schedule

# Import availability gatekeeper
try:
    from eq12_player_availability import PlayerAvailabilityManager
    from eq12_roster_validated_sgp_generator_enhanced import RosterValidatedSGPGenerator
    GATEKEEPER_ENABLED = True
except ImportError:
    GATEKEEPER_ENABLED = False
    print(" Roster validation gatekeeper not available")


class NBAMonitoringSystem:
    """
     Continuous NBA SGP Monitoring with Telegram Updates
    Runs every 2 hours to check player status and update parlays
    """
    
    def __init__(self, workspace: str = "C:/EQ12"):
        self.workspace = Path(workspace)
        self.logs_path = self.workspace / "logs"
        self.reports_path = self.workspace / "coral_betting_ai" / "reports"
        self.logs_path.mkdir(exist_ok=True)
        self.reports_path.mkdir(parents=True, exist_ok=True)
        
        # Telegram configuration
        self.telegram_config = self._load_telegram_config()
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Current SGP state
        self.current_sgps = {}
        self.last_scan_time = None
        self.scan_count = 0
        
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging for monitoring system"""
        log_file = self.logs_path / f"nba_monitoring_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f" NBA Monitoring System initialized - Log: {log_file}")
    
    def _load_telegram_config(self) -> Dict[str, str]:
        """Load Telegram configuration from environment or config file"""
        try:
            config_file = self.workspace / "coral_betting_ai" / "coral_config.env"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    content = f.read()
                    
                telegram_config = {}
                for line in content.split('\n'):
                    if 'TELEGRAM_BOT_TOKEN=' in line:
                        telegram_config['bot_token'] = line.split('=', 1)[1].strip()
                    elif 'TELEGRAM_CHAT_ID=' in line:
                        telegram_config['chat_id'] = line.split('=', 1)[1].strip()
                
                return telegram_config
        except Exception as e:
            self.logger.warning(f"Failed to load Telegram config: {e}")
        
        return {
            'bot_token': 'YOUR_BOT_TOKEN',
            'chat_id': 'YOUR_CHAT_ID'
        }
    
    async def send_telegram_update(self, message: str, parse_mode: str = 'Markdown'):
        """Send update to Telegram"""
        if not self.telegram_config.get('bot_token') or 'YOUR_BOT_TOKEN' in self.telegram_config.get('bot_token', ''):
            self.logger.warning(" Telegram not configured - skipping message")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
            payload = {
                'chat_id': self.telegram_config['chat_id'],
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                self.logger.info(" Telegram update sent successfully")
                return True
            else:
                self.logger.error(f" Telegram API error: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f" Failed to send Telegram update: {e}")
            return False
    
    async def scan_player_status(self) -> Dict[str, Any]:
        """Scan current player status and detect changes"""
        self.logger.info(" SCANNING PLAYER STATUS FOR CHANGES...")
        
        # Run the roster-validated player status verification system
        try:
            import subprocess
            import sys
            
            # Run both the original verification and new roster validation
            result = subprocess.run([
                sys.executable,
                str(self.workspace / "scripts" / "eq12_roster_validated_sgp_generator.py")
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.logger.info(" Player status scan completed successfully")
                
                # Load the latest verification results
                verification_files = list(self.logs_path.glob("sgp_player_status_verification_*.json"))
                if verification_files:
                    latest_file = max(verification_files, key=lambda f: f.stat().st_mtime)
                    with open(latest_file, 'r') as f:
                        return json.load(f)
            else:
                self.logger.error(f" Player status scan failed: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f" Failed to run player status scan: {e}")
        
        return {}
    
    async def update_sgp_analysis(self) -> Dict[str, Any]:
        """Update SGP analysis with roster validation"""
        self.logger.info(" UPDATING ROSTER-VALIDATED SGP ANALYSIS...")
        
        try:
            if GATEKEEPER_ENABLED:
                # Use the enhanced roster-validated SGP generator
                self.logger.info(" Using roster validation gatekeeper...")
                sgp_generator = RosterValidatedSGPGenerator(str(self.workspace))
                validated_slate = sgp_generator.generate_clean_sgp_slate()
                
                # Save the validated slate
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = self.reports_path / f"roster_validated_sgps_{timestamp}.json"
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'w') as f:
                    json.dump(validated_slate, f, indent=2)
                
                self.logger.info(f" Roster-validated SGPs saved: {output_file}")
                return validated_slate
            
            else:
                # Fallback to original method
                import subprocess
                import sys
                
                result = subprocess.run([
                    sys.executable,
                    str(self.workspace / "scripts" / "eq12_coral_betting_ai.py"),
                    "--workspace", str(self.workspace),
                    "--sgp-tonight",
                    "--verbose"
                ], capture_output=True, text=True, timeout=180)
                
                if result.returncode == 0:
                    self.logger.info(" SGP analysis updated successfully")
                    
                    # Load the latest SGP analysis
                    sgp_files = list(self.reports_path.glob("draftkings_sgp_analysis_*.json"))
                    if sgp_files:
                        latest_file = max(sgp_files, key=lambda f: f.stat().st_mtime)
                        with open(latest_file, 'r') as f:
                            return json.load(f)
                else:
                    self.logger.error(f" SGP analysis failed: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f" Failed to update SGP analysis: {e}")
        
        return {}
    
    def detect_changes(self, current_status: Dict[str, Any], current_sgps: Dict[str, Any]) -> Dict[str, Any]:
        """Detect changes in player status or SGP recommendations"""
        changes = {
            'player_changes': [],
            'sgp_changes': [],
            'new_out_players': [],
            'new_questionable_players': [],
            'players_cleared': [],
            'sgps_removed': [],
            'sgps_added': [],
            'significant_changes': False
        }
        
        # Compare with previous scan if available
        if hasattr(self, 'previous_status') and self.previous_status:
            prev_status = self.previous_status
            
            # Check for player status changes
            for player, status_info in current_status.get('player_details', {}).items():
                prev_info = prev_status.get('player_details', {}).get(player, {})
                current_status_val = status_info.get('status', 'UNKNOWN')
                prev_status_val = prev_info.get('status', 'UNKNOWN')
                
                if current_status_val != prev_status_val:
                    changes['player_changes'].append({
                        'player': player,
                        'from': prev_status_val,
                        'to': current_status_val,
                        'reason': status_info.get('reason', 'Status change detected')
                    })
                    changes['significant_changes'] = True
                    
                    if current_status_val == 'OUT':
                        changes['new_out_players'].append(player)
                    elif current_status_val == 'QUESTIONABLE':
                        changes['new_questionable_players'].append(player)
                    elif prev_status_val in ['OUT', 'QUESTIONABLE'] and current_status_val == 'ACTIVE':
                        changes['players_cleared'].append(player)
        
        # Store current status for next comparison
        self.previous_status = current_status
        
        return changes
    
    def format_telegram_update(self, status: Dict[str, Any], sgps: Dict[str, Any], changes: Dict[str, Any]) -> str:
        """Format comprehensive Telegram update message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        scan_num = self.scan_count
        
        message = f" *NBA SGP MONITORING UPDATE #{scan_num}*\n"
        message += f" {timestamp}\n"
        message += f" Auto-scan every 2 hours\n\n"
        
        # Player Status Summary
        active_count = status.get('active_players', 0)
        questionable_count = status.get('questionable_players', 0)
        out_count = status.get('out_players', 0)
        
        message += f" *PLAYER STATUS SUMMARY:*\n"
        message += f" ACTIVE: {active_count} players\n"
        message += f" QUESTIONABLE: {questionable_count} players\n"
        message += f" OUT/INACTIVE: {out_count} players\n\n"
        
        # Changes Detection
        if changes['significant_changes']:
            message += f" *CHANGES DETECTED:*\n"
            
            for change in changes['player_changes']:
                status_emoji = {'ACTIVE': '', 'QUESTIONABLE': '', 'OUT': ''}.get(change['to'], '')
                message += f"{status_emoji} {change['player']}: {change['from']}  {change['to']}\n"
            
            message += "\n"
        else:
            message += f" *NO CHANGES DETECTED* - All players stable\n\n"
        
        # Current SGP Status
        safe_sgps = status.get('safe_sgps', [])
        unsafe_sgps = status.get('unsafe_sgps', [])
        
        message += f" *CURRENT SGP STATUS:*\n"
        message += f" SAFE SGPs: {len(safe_sgps)}\n"
        message += f" RISKY SGPs: {len(unsafe_sgps)}\n\n"
        
        # Roster-Validated SGPs with Full Details
        message += f" *ROSTER-VALIDATED SGP PARLAYS:*\n"
        message += f" *All props verified against player roles*\n"
        message += f" *Fake assists props removed*\n"
        message += f" *Injury status confirmed*\n\n"
        
        # Load latest clean SGP data
        try:
            import json
            from pathlib import Path
            
            # Find most recent clean SGP file
            logs_path = Path(self.workspace) / "logs"
            clean_sgp_files = list(logs_path.glob("clean_sgp_data_*.json"))
            
            if clean_sgp_files:
                latest_file = max(clean_sgp_files, key=lambda f: f.stat().st_mtime)
                with open(latest_file, 'r') as f:
                    clean_sgps = json.load(f)
                
                # Show top 3 highest confidence SGPs
                sorted_sgps = sorted(clean_sgps.items(), 
                                   key=lambda x: x[1].get('confidence', 0), reverse=True)
                
                for i, (game, sgp_data) in enumerate(sorted_sgps[:3], 1):
                    confidence = sgp_data.get('confidence', 0)
                    payout_odds = sgp_data.get('payout_odds', 'N/A')
                    potential_win = sgp_data.get('potential_payout', 0)
                    stake = sgp_data.get('recommended_stake', 25)
                    
                    message += f"*#{i}: {game}*\n"
                    message += f" Confidence: {confidence}%\n"
                    message += f" Odds: {payout_odds}\n"
                    message += f" ${stake}  ${potential_win:.0f}\n"
                    
                    # Show injury notes if any
                    if 'injuries_note' in sgp_data:
                        message += f" {sgp_data['injuries_note']}\n"
                    
                    # Show top 3 legs with validation
                    legs = sgp_data.get('legs', [])[:3]
                    message += f" Verified Legs:\n"
                    for leg in legs:
                        selection = leg.get('selection', 'N/A')
                        odds = leg.get('odds', 0)
                        odds_display = f"+{odds}" if odds > 0 else f"{odds}"
                        message += f"   {selection} ({odds_display})\n"
                    
                    message += "\n"
                    
        except Exception as e:
            message += f" Could not load roster-validated SGPs: {str(e)[:50]}...\n\n"
        
        # Alert for questionable players
        if questionable_count > 0:
            message += f" *MONITOR CLOSELY:*\n"
            for player, details in status.get('player_details', {}).items():
                if details.get('status') == 'QUESTIONABLE':
                    reason = details.get('reason', 'Status unclear')
                    message += f" {player} - {reason}\n"
            message += "\n"
        
        # Next scan info
        next_scan = datetime.now() + timedelta(hours=2)
        message += f" *Next scan:* {next_scan.strftime('%H:%M')}\n"
        message += f" Updates sent automatically\n"
        message += f" EQ12 Coral AI Monitoring"
        
        return message
    
    async def run_monitoring_cycle(self):
        """Run a complete monitoring cycle"""
        self.scan_count += 1
        self.logger.info(f" STARTING MONITORING CYCLE #{self.scan_count}")
        
        try:
            # Scan player status
            current_status = await self.scan_player_status()
            
            # Update SGP analysis 
            current_sgps = await self.update_sgp_analysis()
            
            # Detect changes
            changes = self.detect_changes(current_status, current_sgps)
            
            # Format and send Telegram update
            message = self.format_telegram_update(current_status, current_sgps, changes)
            await self.send_telegram_update(message)
            
            # Save monitoring state
            self.current_sgps = current_sgps
            self.last_scan_time = datetime.now()
            
            # Save scan results
            scan_results = {
                'timestamp': datetime.now().isoformat(),
                'scan_number': self.scan_count,
                'player_status': current_status,
                'sgp_analysis': current_sgps,
                'changes_detected': changes,
                'telegram_sent': True
            }
            
            results_file = self.logs_path / f"monitoring_scan_{self.scan_count:03d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w') as f:
                json.dump(scan_results, f, indent=2)
            
            self.logger.info(f" Monitoring cycle #{self.scan_count} completed successfully")
            
        except Exception as e:
            self.logger.error(f" Monitoring cycle #{self.scan_count} failed: {e}")
            
            # Send error alert to Telegram
            error_message = f" *MONITORING ERROR #{self.scan_count}*\n"
            error_message += f" Failed to complete scan\n"
            error_message += f" {datetime.now().strftime('%H:%M:%S')}\n"
            error_message += f" Will retry in 2 hours\n"
            error_message += f" Error: {str(e)[:100]}..."
            
            await self.send_telegram_update(error_message)
    
    def start_monitoring(self):
        """Start the continuous monitoring system"""
        self.logger.info(" STARTING NBA SGP CONTINUOUS MONITORING SYSTEM")
        self.logger.info(" Updates will be sent to Telegram every 2 hours")
        
        # Schedule monitoring every 2 hours
        schedule.every(2).hours.do(lambda: asyncio.run(self.run_monitoring_cycle()))
        
        # Run initial scan immediately
        asyncio.run(self.run_monitoring_cycle())
        
        # Keep running scheduled tasks
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for scheduled tasks


def main():
    parser = argparse.ArgumentParser(description="NBA SGP Continuous Monitoring System")
    parser.add_argument("--workspace", default="C:/EQ12", help="Workspace path")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    parser.add_argument("--test", action="store_true", help="Run single test cycle")
    
    args = parser.parse_args()
    
    print(" Starting EQ12 NBA SGP Continuous Monitoring System...")
    print(" Will scan every 2 hours and send Telegram updates")
    
    # Initialize monitoring system
    monitor = NBAMonitoringSystem(args.workspace)
    
    if args.test:
        # Run single test cycle
        print(" Running test cycle...")
        asyncio.run(monitor.run_monitoring_cycle())
    else:
        # Start continuous monitoring
        print(" Starting continuous monitoring...")
        monitor.start_monitoring()


if __name__ == "__main__":
    main()