#!/usr/bin/env python3
"""
EQ12 Bulletproof Intelligence Suite - Master Integration
Combines bulletproof parlay generation with real-time NBA news intelligence

Created: November 4, 2025
Author: EQ12 Intelligence Team
Purpose: Complete protection against player availability errors like Damian Lillard oversight
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
import subprocess

# Local imports
sys.path.append(os.path.dirname(__file__))

class BulletproofIntelligenceSuite:
    """Master intelligence suite combining bulletproof parlays with news intelligence"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.logs_dir = os.path.join(workspace_path, "logs")
        self.reports_dir = os.path.join(workspace_path, "reports")
        
        # Ensure directories exist
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Setup logging
        log_file = os.path.join(self.logs_dir, f"bulletproof_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Script paths
        self.bulletproof_script = os.path.join(workspace_path, "scripts", "eq12_bulletproof_standalone.py")
        self.news_harvester_script = os.path.join(workspace_path, "scripts", "eq12_nba_news_harvester.py")
        self.injury_corrector_script = os.path.join(workspace_path, "scripts", "eq12_injury_intelligence_corrector.py")

    def run_news_intelligence(self, send_telegram: bool = False) -> Dict[str, Any]:
        """Run NBA news intelligence harvester"""
        self.logger.info(" Running NBA news intelligence scan...")
        
        cmd = [
            "python", self.news_harvester_script,
            "--workspace", self.workspace_path,
            "--top-n", "30"
        ]
        
        if send_telegram:
            cmd.append("--send-telegram")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info(" News intelligence scan completed successfully")
                
                # Parse latest report
                import glob
                report_files = glob.glob(os.path.join(self.reports_dir, "nba_news_*.json"))
                if report_files:
                    latest_report = max(report_files, key=os.path.getctime)
                    with open(latest_report, 'r') as f:
                        news_data = json.load(f)
                    
                    return {
                        "success": True,
                        "report_file": latest_report,
                        "news_data": news_data,
                        "items_scanned": len(news_data.get("results", [])),
                        "players_tracked": news_data.get("players", []),
                        "teams_tracked": news_data.get("teams", [])
                    }
                else:
                    return {"success": True, "report_file": None, "news_data": {}}
            else:
                self.logger.error(f"News intelligence scan failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            self.logger.error(f"Exception during news intelligence scan: {e}")
            return {"success": False, "error": str(e)}

    def check_injury_alerts(self, news_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for critical injury alerts in news data"""
        alerts = []
        
        if not news_data.get("results"):
            return alerts
        
        for item in news_data["results"]:
            hits = item.get("hits", {})
            
            # Critical alert criteria
            if (hits.get("players") and hits.get("injury_terms") and 
                item.get("score", 0) >= 20):
                
                # Check for critical injury keywords
                critical_keywords = ["out", "ruled out", "season ending", "torn", "surgery"]
                injury_terms = [term.lower() for term in hits.get("injury_terms", [])]
                
                is_critical = any(keyword in " ".join(injury_terms) for keyword in critical_keywords)
                
                alert = {
                    "title": item.get("title", ""),
                    "players": hits.get("players", []),
                    "injury_terms": hits.get("injury_terms", []),
                    "score": item.get("score", 0),
                    "is_critical": is_critical,
                    "link": item.get("link", ""),
                    "published": item.get("published", "")
                }
                alerts.append(alert)
        
        return alerts

    def generate_bulletproof_parlay(self) -> Dict[str, Any]:
        """Generate bulletproof parlay with current blocked players"""
        self.logger.info(" Generating bulletproof parlay...")
        
        cmd = ["python", self.bulletproof_script, "--test-mode", "--verbose"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.logger.info(" Bulletproof parlay generated successfully")
                
                # Parse output for parlay data
                output_lines = result.stdout.split('\n')
                parlay_info = {}
                
                for line in output_lines:
                    if "Legs:" in line:
                        parlay_info["legs"] = line.split("Legs:")[1].strip()
                    elif "Total Odds:" in line:
                        parlay_info["odds"] = line.split("Total Odds:")[1].strip()
                    elif "Potential Payout:" in line:
                        parlay_info["payout"] = line.split("Potential Payout:")[1].strip()
                    elif "Generation Time:" in line:
                        parlay_info["time"] = line.split("Generation Time:")[1].strip()
                
                # Count blocked players from output
                blocked_count = result.stdout.count("BLOCKED")
                parlay_info["blocked_players_count"] = blocked_count
                
                return {
                    "success": True,
                    "parlay_info": parlay_info,
                    "output": result.stdout
                }
            else:
                self.logger.error(f"Bulletproof parlay generation failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            self.logger.error(f"Exception during parlay generation: {e}")
            return {"success": False, "error": str(e)}

    def run_comprehensive_intelligence(self, send_telegram: bool = False) -> Dict[str, Any]:
        """Run complete intelligence suite"""
        self.logger.info(" RUNNING COMPREHENSIVE BULLETPROOF INTELLIGENCE SUITE ")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "news_intelligence": {},
            "injury_alerts": [],
            "bulletproof_parlay": {},
            "summary": {}
        }
        
        # Step 1: Run news intelligence
        self.logger.info("Step 1: NBA News Intelligence Scan")
        news_result = self.run_news_intelligence(send_telegram)
        results["news_intelligence"] = news_result
        
        # Step 2: Check for injury alerts
        if news_result.get("success") and news_result.get("news_data"):
            self.logger.info("Step 2: Injury Alert Analysis")
            alerts = self.check_injury_alerts(news_result["news_data"])
            results["injury_alerts"] = alerts
            
            if alerts:
                self.logger.warning(f" Found {len(alerts)} injury alerts!")
                for alert in alerts:
                    if alert["is_critical"]:
                        self.logger.error(f" CRITICAL: {alert['title']}")
        
        # Step 3: Generate bulletproof parlay
        self.logger.info("Step 3: Bulletproof Parlay Generation")
        parlay_result = self.generate_bulletproof_parlay()
        results["bulletproof_parlay"] = parlay_result
        
        # Step 4: Generate summary
        results["summary"] = {
            "news_items_scanned": news_result.get("items_scanned", 0),
            "injury_alerts_found": len(results["injury_alerts"]),
            "critical_alerts": len([a for a in results["injury_alerts"] if a["is_critical"]]),
            "parlay_generated": parlay_result.get("success", False),
            "blocked_players": parlay_result.get("parlay_info", {}).get("blocked_players_count", 0)
        }
        
        # Save comprehensive report
        report_file = os.path.join(self.logs_dir, f"comprehensive_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f" Comprehensive report saved: {report_file}")
        
        return results

    def print_summary(self, results: Dict[str, Any]):
        """Print formatted summary of intelligence results"""
        print("\n" + "="*80)
        print(" BULLETPROOF INTELLIGENCE SUITE - SUMMARY REPORT")
        print("="*80)
        
        summary = results.get("summary", {})
        
        print(f" Timestamp: {results.get('timestamp', 'Unknown')}")
        print(f" News items scanned: {summary.get('news_items_scanned', 0)}")
        print(f" Injury alerts found: {summary.get('injury_alerts_found', 0)}")
        print(f" Critical alerts: {summary.get('critical_alerts', 0)}")
        print(f" Parlay generated: {'' if summary.get('parlay_generated') else ''}")
        print(f" Players blocked: {summary.get('blocked_players', 0)}")
        
        # Show critical alerts
        critical_alerts = [a for a in results.get("injury_alerts", []) if a.get("is_critical")]
        if critical_alerts:
            print(f"\n CRITICAL INJURY ALERTS:")
            for i, alert in enumerate(critical_alerts, 1):
                print(f"  {i}. {alert['title']}")
                print(f"     Players: {', '.join(alert['players'])}")
                print(f"     Injury Terms: {', '.join(alert['injury_terms'])}")
        
        # Show parlay info
        parlay_info = results.get("bulletproof_parlay", {}).get("parlay_info", {})
        if parlay_info:
            print(f"\n BULLETPROOF PARLAY:")
            print(f"  Legs: {parlay_info.get('legs', 'Unknown')}")
            print(f"  Odds: {parlay_info.get('odds', 'Unknown')}")
            print(f"  Payout: {parlay_info.get('payout', 'Unknown')}")
            print(f"  Generation Time: {parlay_info.get('time', 'Unknown')}")
        
        print("="*80)

def main():
    parser = argparse.ArgumentParser(description="EQ12 Bulletproof Intelligence Suite")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    parser.add_argument("--send-telegram", action="store_true", help="Send Telegram notifications")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize and run suite
    suite = BulletproofIntelligenceSuite(args.workspace)
    results = suite.run_comprehensive_intelligence(args.send_telegram)
    
    # Print summary
    suite.print_summary(results)
    
    # Exit with appropriate code
    if results.get("summary", {}).get("critical_alerts", 0) > 0:
        print("\n CRITICAL ALERTS DETECTED - REVIEW IMMEDIATELY!")
        sys.exit(2)  # Critical alerts
    elif not results.get("bulletproof_parlay", {}).get("success", False):
        print("\n PARLAY GENERATION FAILED")
        sys.exit(1)  # Generation failure
    else:
        print("\n ALL SYSTEMS OPERATIONAL")
        sys.exit(0)  # Success

if __name__ == "__main__":
    main()