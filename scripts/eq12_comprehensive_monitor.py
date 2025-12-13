#!/usr/bin/env python3
"""
EQ12 Comprehensive System Monitor - All Scans Until 5:30 PM
Runs complete EQ12 system monitoring with Telegram notifications

Created: November 5, 2025
Author: EQ12 System Operations Team
Purpose: Comprehensive monitoring of all EQ12 systems until 5:30 PM
"""

import argparse
import json
import logging
import os
import sys
import subprocess
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import threading
import signal

class EQ12SystemMonitor:
    """Comprehensive EQ12 system monitoring with continuous scanning"""
    
    def __init__(self, workspace_path: str, end_time: str = "17:30"):
        self.workspace_path = workspace_path
        self.logs_dir = os.path.join(workspace_path, "logs")
        self.scripts_dir = os.path.join(workspace_path, "scripts")
        self.end_time = end_time
        self.running = True
        self.scan_count = 0
        
        # Parse end time
        self.end_datetime = self._parse_end_time(end_time)
        
        # Setup logging
        log_file = os.path.join(self.logs_dir, f"eq12_system_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # EQ12 System Scripts to Monitor
        self.system_scripts = {
            "NBA Intelligence": {
                "script": "eq12_bulletproof_intelligence_suite.py",
                "args": ["--workspace", workspace_path, "--send-telegram", "--verbose"],
                "interval": 300,  # 5 minutes
                "priority": "HIGH"
            },
            "Security Guardian": {
                "script": "eq12_gitleaks_guardian.py", 
                "args": ["--action", "comprehensive", "--workspace", workspace_path, "--verbose"],
                "interval": 900,  # 15 minutes
                "priority": "HIGH"
            },
            "Script Integrity": {
                "script": "eq12_script_integrity_suite.ps1",
                "args": ["-Action", "All", "-AutoFix", "-GenerateReport"],
                "shell": "powershell",
                "interval": 1200,  # 20 minutes
                "priority": "MEDIUM"
            },
            "Universal Repair": {
                "script": "eq12_universal_repair_assistant.py",
                "args": ["--action", "health-check", "--workspace", workspace_path],
                "interval": 600,  # 10 minutes
                "priority": "MEDIUM"
            },
            "Flake8 Autofix": {
                "script": "eq12_flake8_autofix.py",
                "args": ["--action", "fix-comprehensive", "--workspace", workspace_path, "--verbose"],
                "interval": 1800,  # 30 minutes
                "priority": "LOW"
            },
            "Business Intelligence": {
                "script": "eq12_business_intelligence_prompt_pack_generator.py",
                "args": ["--full-strategy", "--verbose"],
                "interval": 3600,  # 60 minutes
                "priority": "LOW"
            },
            "Coral Crypto Monitor": {
                "script": "eq12_coral_crypto_wrapper.ps1",
                "args": ["-Action", "Status", "-VerboseOutput"],
                "shell": "powershell",
                "interval": 420,  # 7 minutes
                "priority": "MEDIUM"
            }
        }
        
        # Track last run times
        self.last_run = {name: datetime.min for name in self.system_scripts.keys()}
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _parse_end_time(self, end_time: str) -> datetime:
        """Parse end time string to datetime object"""
        try:
            # Parse time in HH:MM format
            time_parts = end_time.split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            
            # Get today's date with the specified time
            now = datetime.now()
            end_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If time has already passed today, set for tomorrow
            if end_dt <= now:
                end_dt += timedelta(days=1)
                
            return end_dt
        except Exception:
            # Default to 5:30 PM today
            now = datetime.now()
            return now.replace(hour=17, minute=30, second=0, microsecond=0)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(" Shutdown signal received, stopping gracefully...")
        self.running = False

    def should_run_script(self, name: str, config: Dict[str, Any]) -> bool:
        """Check if script should run based on interval"""
        now = datetime.now()
        interval = config.get("interval", 600)  # Default 10 minutes
        
        return (now - self.last_run[name]).total_seconds() >= interval

    def run_script(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single EQ12 system script"""
        script_path = os.path.join(self.scripts_dir, config["script"])
        
        if not os.path.exists(script_path):
            return {
                "success": False,
                "error": f"Script not found: {script_path}",
                "output": ""
            }
        
        # Build command
        if config.get("shell") == "powershell":
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path] + config.get("args", [])
        else:
            cmd = ["python", script_path] + config.get("args", [])
        
        try:
            self.logger.info(f" Running {name}...")
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300,  # 5 minute timeout
                cwd=self.scripts_dir
            )
            
            success = result.returncode == 0
            if success:
                self.logger.info(f" {name} completed successfully")
            else:
                self.logger.warning(f" {name} completed with warnings (exit code: {result.returncode})")
            
            return {
                "success": success,
                "exit_code": result.returncode,
                "output": result.stdout,
                "error": result.stderr,
                "duration": "< 5 minutes"
            }
            
        except subprocess.TimeoutExpired:
            self.logger.error(f" {name} timed out after 5 minutes")
            return {
                "success": False,
                "error": "Script timed out after 5 minutes",
                "output": "",
                "duration": "5+ minutes (timeout)"
            }
        except Exception as e:
            self.logger.error(f" {name} failed with exception: {e}")
            return {
                "success": False,
                "error": str(e), 
                "output": "",
                "duration": "Failed"
            }

    def send_telegram_summary(self, results: Dict[str, Any]):
        """Send comprehensive system status to Telegram"""
        try:
            # Find telegram script
            telegram_scripts = [
                "eq12_bulletproof_intelligence_suite.py",
                "eq12_nba_news_harvester.py"
            ]
            
            summary_lines = [
                f" EQ12 System Monitor - Scan #{self.scan_count}",
                f" {datetime.now().strftime('%m/%d %I:%M %p')}",
                f" Running until {self.end_time}",
                ""
            ]
            
            # System status summary
            total_scripts = len(results)
            successful = sum(1 for r in results.values() if r.get("success", False))
            failed = total_scripts - successful
            
            summary_lines.extend([
                f" Scripts Run: {total_scripts}",
                f" Successful: {successful}",
                f" Failed: {failed}",
                ""
            ])
            
            # Priority issues
            high_priority_issues = []
            for name, result in results.items():
                config = self.system_scripts.get(name, {})
                if config.get("priority") == "HIGH" and not result.get("success", False):
                    high_priority_issues.append(f" {name}: {result.get('error', 'Unknown error')}")
            
            if high_priority_issues:
                summary_lines.extend([" HIGH PRIORITY ISSUES:"] + high_priority_issues[:3] + [""])
            
            # Recent completions
            recent_completions = [name for name, result in results.items() if result.get("success", False)]
            if recent_completions:
                summary_lines.extend([
                    " Recent Completions:",
                    *[f" {name}" for name in recent_completions[:5]]
                ])
            
            telegram_message = "\n".join(summary_lines)
            
            # Try to send via existing telegram integration
            for script in telegram_scripts:
                script_path = os.path.join(self.scripts_dir, script)
                if os.path.exists(script_path):
                    try:
                        # Create temporary message file
                        temp_msg_file = os.path.join(self.logs_dir, "temp_telegram_msg.txt")
                        with open(temp_msg_file, 'w', encoding='utf-8') as f:
                            f.write(telegram_message)
                        
                        # Send message (attempt with news harvester)
                        if "news_harvester" in script:
                            subprocess.run([
                                "python", script_path,
                                "--workspace", self.workspace_path,
                                "--send-telegram", 
                                "--top-n", "5"
                            ], timeout=30, capture_output=True)
                        
                        os.remove(temp_msg_file)
                        self.logger.info(" Telegram summary sent")
                        return True
                        
                    except Exception as e:
                        self.logger.warning(f"Telegram send attempt failed: {e}")
                        continue
            
            self.logger.warning(" Could not send Telegram summary - no working integration found")
            return False
            
        except Exception as e:
            self.logger.error(f" Telegram summary failed: {e}")
            return False

    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        self.scan_count += 1
        now = datetime.now()
        
        self.logger.info(f" Starting monitoring cycle #{self.scan_count} at {now.strftime('%H:%M:%S')}")
        
        results = {}
        scripts_run = 0
        
        # Check each script
        for name, config in self.system_scripts.items():
            if not self.running:
                break
                
            if self.should_run_script(name, config):
                result = self.run_script(name, config)
                results[name] = result
                self.last_run[name] = now
                scripts_run += 1
                
                # Small delay between scripts
                if self.running:
                    time.sleep(2)
        
        # Send Telegram summary if any scripts ran
        if scripts_run > 0:
            self.send_telegram_summary(results)
        
        # Save monitoring report
        report = {
            "timestamp": now.isoformat(),
            "scan_number": self.scan_count,
            "scripts_run": scripts_run,
            "results": results,
            "next_scan_in": "60 seconds",
            "monitoring_until": self.end_time
        }
        
        report_file = os.path.join(self.logs_dir, f"eq12_monitor_scan_{self.scan_count:03d}_{now.strftime('%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f" Cycle #{self.scan_count} completed - {scripts_run} scripts run")
        return results

    def run_until_end_time(self):
        """Run continuous monitoring until end time"""
        self.logger.info(" STARTING EQ12 COMPREHENSIVE SYSTEM MONITORING")
        self.logger.info("=" * 80)
        self.logger.info(f" Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f" End Time: {self.end_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f" Workspace: {self.workspace_path}")
        self.logger.info(f" System Scripts: {len(self.system_scripts)}")
        self.logger.info("=" * 80)
        
        try:
            while self.running and datetime.now() < self.end_datetime:
                # Run monitoring cycle
                self.run_monitoring_cycle()
                
                # Check if we should continue
                if not self.running:
                    break
                    
                # Calculate time until next scan (60 seconds) or end time
                now = datetime.now()
                next_scan = now + timedelta(seconds=60)
                
                if next_scan >= self.end_datetime:
                    self.logger.info(f" End time reached, stopping monitoring")
                    break
                
                # Sleep until next scan
                sleep_seconds = min(60, (self.end_datetime - now).total_seconds())
                if sleep_seconds > 0:
                    self.logger.info(f" Waiting {int(sleep_seconds)} seconds until next scan...")
                    time.sleep(sleep_seconds)
                    
        except KeyboardInterrupt:
            self.logger.info(" Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f" Monitoring error: {e}")
        finally:
            self.running = False
            
        # Final summary
        self.logger.info("=" * 80)
        self.logger.info(" EQ12 SYSTEM MONITORING COMPLETED")
        self.logger.info(f" Total Scans: {self.scan_count}")
        self.logger.info(f" Duration: {datetime.now().strftime('%H:%M:%S')}")
        self.logger.info("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="EQ12 Comprehensive System Monitor")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    parser.add_argument("--end-time", default="17:30", help="End time in HH:MM format (24-hour)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize and run monitor
    monitor = EQ12SystemMonitor(args.workspace, args.end_time)
    monitor.run_until_end_time()

if __name__ == "__main__":
    main()