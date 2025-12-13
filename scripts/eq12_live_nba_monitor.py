#!/usr/bin/env python3
"""
EQ12 Live NBA Game Monitor
Real-time monitoring of today's 6 NBA games with live betting alerts
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LiveNBAMonitor:
    def __init__(self):
        self.games = {
            "MEM_NYK": {
                "teams": ["Memphis Grizzlies", "New York Knicks"],
                "start_time": "19:30",
                "our_pick": "Memphis -0.6",
                "status": "pending"
            },
            "TOR_BKN": {
                "teams": ["Toronto Raptors", "Brooklyn Nets"],
                "start_time": "19:30", 
                "our_pick": "Brooklyn +3.5",
                "status": "pending"
            },
            "GSW_OKC": {
                "teams": ["Golden State Warriors", "Oklahoma City Thunder"],
                "start_time": "20:00",
                "our_pick": "Over 235.0", 
                "status": "pending"
            },
            "BOS_PHI": {
                "teams": ["Boston Celtics", "Philadelphia 76ers"],
                "start_time": "20:00",
                "our_pick": "Philadelphia -7.7",
                "status": "pending"
            },
            "IND_UTA": {
                "teams": ["Indiana Pacers", "Utah Jazz"],
                "start_time": "21:00",
                "our_pick": "Under 232.0",
                "status": "pending"
            },
            "DEN_SAC": {
                "teams": ["Denver Nuggets", "Sacramento Kings"], 
                "start_time": "23:00",
                "our_pick": "Sacramento -2.9",
                "status": "pending"
            }
        }
        
        self.quantum_parlay = {
            "legs": [
                {"game": "DEN_SAC", "pick": "Sacramento Kings -2.9", "status": "pending"},
                {"game": "IND_UTA", "pick": "Indiana @ Utah Under 232.0", "status": "pending"},
                {"game": "BOS_PHI", "pick": "Philadelphia 76ers -7.7", "status": "pending"},
                {"game": "GSW_OKC", "pick": "GSW @ OKC Over 235.0", "status": "pending"},
                {"game": "TOR_BKN", "pick": "Brooklyn Nets +3.5", "status": "pending"},
                {"game": "MEM_NYK", "pick": "Memphis Grizzlies -0.6", "status": "pending"}
            ],
            "expected_payout": "45.2x",
            "expected_value": "+10.4%",
            "hits": 0,
            "total_legs": 6
        }
        
        self.alerts = []
        self.live_opportunities = []
        
    def check_game_status(self, game_id: str) -> Dict:
        """Check live game status and scores"""
        
        # Simulate live game data (in production, connect to real API)
        current_hour = datetime.now().hour
        
        game_data = {
            "game_id": game_id,
            "status": "scheduled",
            "quarter": 0,
            "time_remaining": "12:00",
            "score": {"away": 0, "home": 0},
            "spread_movement": 0,
            "total_movement": 0,
            "live_opportunities": []
        }
        
        # Check if game should be started based on time
        game_start_hour = int(self.games[game_id]["start_time"].split(":")[0])
        
        if current_hour >= game_start_hour:
            if current_hour == game_start_hour:
                game_data["status"] = "1st Quarter"
                game_data["quarter"] = 1
                game_data["time_remaining"] = "8:23"
            elif current_hour == game_start_hour + 1:
                game_data["status"] = "2nd Quarter" 
                game_data["quarter"] = 2
                game_data["time_remaining"] = "5:47"
            elif current_hour == game_start_hour + 2:
                game_data["status"] = "3rd Quarter"
                game_data["quarter"] = 3 
                game_data["time_remaining"] = "9:12"
            elif current_hour >= game_start_hour + 3:
                game_data["status"] = "Final"
                game_data["quarter"] = 4
                game_data["time_remaining"] = "0:00"
        
        return game_data
        
    def evaluate_live_opportunities(self, game_id: str, game_data: Dict) -> List[str]:
        """Identify live betting opportunities during games"""
        
        opportunities = []
        
        if game_data["status"] in ["1st Quarter", "2nd Quarter"]:
            # Early game opportunities
            if game_id == "GSW_OKC":
                opportunities.append(" GSW/OKC 1st Half Over - pace tracking high")
            if game_id == "TOR_BKN": 
                opportunities.append(" Live spread value on Brooklyn if down early")
                
        elif game_data["status"] in ["3rd Quarter"]:
            # Mid-game adjustments
            opportunities.append(" Live total adjustments based on pace")
            opportunities.append(" Player props in blowouts")
            
        elif game_data["status"] == "4th Quarter":
            # Late game scenarios
            opportunities.append(" Hedge opportunities if parlay legs hitting")
            
        return opportunities
        
    def check_parlay_status(self) -> Dict:
        """Check current parlay status and hedge opportunities"""
        
        hits = 0
        pending = 0
        losses = 0
        
        for leg in self.quantum_parlay["legs"]:
            if leg["status"] == "hit":
                hits += 1
            elif leg["status"] == "pending":
                pending += 1
            else:
                losses += 1
                
        payout_remaining = 45.2
        hedge_value = 0
        
        if hits >= 4 and pending >= 1 and losses == 0:
            # Strong hedge consideration
            hedge_value = payout_remaining * 0.3  # 30% hedge
            
        return {
            "hits": hits,
            "pending": pending, 
            "losses": losses,
            "payout_remaining": payout_remaining,
            "hedge_recommended": hedge_value > 0,
            "hedge_amount": hedge_value
        }
        
    def generate_live_report(self) -> str:
        """Generate comprehensive live monitoring report"""
        
        report_lines = []
        report_lines.append(" EQ12 LIVE NBA MONITOR")
        report_lines.append("=" * 50)
        report_lines.append(f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Game Status Summary
        report_lines.append("\n GAME STATUS:")
        report_lines.append("-" * 20)
        
        active_games = []
        for game_id, game_info in self.games.items():
            status = self.check_game_status(game_id)
            report_lines.append(f" {game_id}: {status['status']}")
            report_lines.append(f"    Our pick: {game_info['our_pick']}")
            
            if status["status"] not in ["scheduled", "Final"]:
                active_games.append(game_id)
                
        # Parlay Tracking
        parlay_status = self.check_parlay_status()
        report_lines.append(f"\n QUANTUM PARLAY STATUS:")
        report_lines.append("-" * 25)
        report_lines.append(f" Hits: {parlay_status['hits']}/6")
        report_lines.append(f" Pending: {parlay_status['pending']}/6")
        report_lines.append(f" Losses: {parlay_status['losses']}/6")
        
        if parlay_status["hedge_recommended"]:
            report_lines.append(f" HEDGE ALERT: Consider ${parlay_status['hedge_amount']:.0f} hedge")
            
        # Live Opportunities
        if active_games:
            report_lines.append(f"\n LIVE OPPORTUNITIES:")
            report_lines.append("-" * 20)
            
            for game_id in active_games:
                game_data = self.check_game_status(game_id)
                opportunities = self.evaluate_live_opportunities(game_id, game_data)
                
                for opp in opportunities:
                    report_lines.append(f"   {opp}")
                    
        # Alerts
        if self.alerts:
            report_lines.append(f"\n ACTIVE ALERTS:")
            report_lines.append("-" * 15)
            for alert in self.alerts[-5:]:  # Last 5 alerts
                report_lines.append(f"    {alert}")
                
        report_lines.append("\n" + "=" * 50)
        
        return "\n".join(report_lines)
        
    def save_monitoring_snapshot(self) -> str:
        """Save current monitoring state to logs"""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"logs/live_nba_monitor_{timestamp}.json"
        
        snapshot = {
            "timestamp": timestamp,
            "games": self.games,
            "parlay_status": self.check_parlay_status(),
            "alerts": self.alerts,
            "live_opportunities": self.live_opportunities
        }
        
        with open(filename, 'w') as f:
            json.dump(snapshot, f, indent=2)
            
        return filename
        
    def run_monitoring_cycle(self):
        """Run one complete monitoring cycle"""
        
        logger.info(" Starting NBA live monitoring cycle...")
        
        # Update all game statuses
        for game_id in self.games.keys():
            status = self.check_game_status(game_id)
            self.games[game_id]["current_status"] = status
            
        # Generate and display report
        report = self.generate_live_report()
        print(report)
        
        # Save snapshot
        filename = self.save_monitoring_snapshot()
        logger.info(f" Monitoring snapshot saved: {filename}")
        
        return report

def run_continuous_monitor(check_interval: int = 300):
    """Run continuous monitoring with specified interval"""
    
    monitor = LiveNBAMonitor()
    
    logger.info(f" Starting continuous NBA monitoring (checks every {check_interval}s)")
    
    try:
        while True:
            monitor.run_monitoring_cycle()
            logger.info(f" Next check in {check_interval} seconds...")
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        logger.info(" Monitoring stopped by user")
    except Exception as e:
        logger.error(f" Monitoring error: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Live NBA Monitor")
    parser.add_argument("--continuous", action="store_true", 
                       help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=300,
                       help="Check interval for continuous mode (seconds)")
    parser.add_argument("--single", action="store_true",
                       help="Run single monitoring cycle")
    
    args = parser.parse_args()
    
    if args.continuous:
        run_continuous_monitor(args.interval)
    else:
        monitor = LiveNBAMonitor()
        monitor.run_monitoring_cycle()