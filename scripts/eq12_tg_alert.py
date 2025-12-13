#!/usr/bin/env python3
"""
EQ12 Telegram Alert System for Coral Betting AI
Sends real-time betting alerts and reports via Telegram

Author: EQ12 Team
Date: November 2, 2025
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import requests


class TelegramAlerter:
    """Telegram bot for EQ12 Coral betting alerts"""
    
    def __init__(self, workspace_path: str, verbose: bool = False):
        self.workspace_path = Path(workspace_path)
        self.reports_path = self.workspace_path / "coral_betting_ai" / "reports"
        self.logs_path = self.workspace_path / "logs"
        
        self.verbose = verbose
        self.setup_logging()
        
        # Telegram configuration
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            self.logger.warning("Telegram credentials not configured")
            self.enabled = False
        else:
            self.enabled = True
            self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
            
        # Alert thresholds
        self.alert_thresholds = {
            'high_ev': 0.6,
            'medium_ev': 0.3,
            'high_confidence': 0.8,
            'medium_confidence': 0.6,
            'parlay_min_odds': 5.0,
            'parlay_max_legs': 8
        }
        
    def setup_logging(self):
        """Setup logging for Telegram alerts"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.logs_path / f"telegram_alerts_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.DEBUG if self.verbose else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Send message via Telegram bot"""
        if not self.enabled:
            self.logger.warning("Telegram not configured, message not sent")
            return False
            
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            self.logger.info("Telegram message sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            return False
            
    def format_bet_alert(self, bet: Dict) -> str:
        """Format individual bet alert message"""
        description = bet.get('description', 'Unknown bet')
        ev_score = bet.get('coral_ev_score', 0.0)
        confidence = bet.get('coral_confidence', 0.0)
        recommendation = bet.get('coral_recommendation', 'NO_BET')
        
        # Get odds
        odds = bet.get('decimal_odds', bet.get('odds', 'N/A'))
        
        # Format message
        if recommendation == 'STRONG_BET':
            emoji = ""
            priority = "HIGH"
        elif recommendation == 'MODERATE_BET':
            emoji = ""
            priority = "MED"
        else:
            emoji = ""
            priority = "LOW"
            
        message = f"""
{emoji} <b>{priority} PRIORITY BET</b>

<b>Bet:</b> {description}
<b>Coral EV Score:</b> {ev_score:.3f}
<b>Confidence:</b> {confidence:.3f}
<b>Odds:</b> {odds}
<b>Recommendation:</b> {recommendation}

<i>Coral AI Analysis at {datetime.now().strftime('%H:%M:%S UTC')}</i>
"""
        
        return message.strip()
        
    def format_parlay_alert(self, parlay: Dict) -> str:
        """Format parlay alert message"""
        legs = parlay.get('legs', [])
        total_odds = parlay.get('total_odds', 0.0)
        parlay_ev = parlay.get('parlay_ev', 0.0)
        confidence = parlay.get('parlay_confidence', 0.0)
        
        # Priority based on risk-adjusted score
        score = parlay.get('risk_adjusted_score', 0.0)
        if score > 0.5:
            emoji = ""
            priority = "PREMIUM"
        elif score > 0.3:
            emoji = ""
            priority = "HIGH"
        else:
            emoji = ""
            priority = "GOOD"
            
        message = f"""
{emoji} <b>{priority} PARLAY OPPORTUNITY</b>

<b>{len(legs)}-Leg Parlay</b>
<b>Total Odds:</b> {total_odds:.2f}
<b>Parlay EV:</b> {parlay_ev:.3f}
<b>Confidence:</b> {confidence:.3f}
<b>Risk Score:</b> {score:.3f}

<b>Legs:</b>
"""
        
        for i, leg in enumerate(legs[:5], 1):  # Show max 5 legs in alert
            leg_desc = leg.get('description', f'Leg {i}')
            leg_ev = leg.get('coral_ev_score', 0.0)
            message += f"{i}. {leg_desc} (EV: {leg_ev:.3f})\n"
            
        if len(legs) > 5:
            message += f"... and {len(legs) - 5} more legs\n"
            
        message += f"\n<i>Generated at {datetime.now().strftime('%H:%M:%S UTC')}</i>"
        
        return message.strip()
        
    def check_and_send_bet_alerts(self, coral_results_file: str = None) -> int:
        """Check Coral results and send alerts for qualifying bets"""
        if coral_results_file is None:
            # Use latest Coral results
            coral_files = list(self.reports_path.glob("coral_results_*.json"))
            if not coral_files:
                self.logger.warning("No Coral results found")
                return 0
            coral_results_file = max(coral_files, key=lambda f: f.stat().st_mtime)
            
        try:
            with open(coral_results_file, 'r') as f:
                data = json.load(f)
                
            bets = data.get('bets', [])
            alerts_sent = 0
            
            for bet in bets:
                if self.should_alert_bet(bet):
                    message = self.format_bet_alert(bet)
                    if self.send_message(message):
                        alerts_sent += 1
                        time.sleep(1)  # Rate limiting
                        
            self.logger.info(f"Sent {alerts_sent} bet alerts")
            return alerts_sent
            
        except Exception as e:
            self.logger.error(f"Error sending bet alerts: {e}")
            return 0
            
    def should_alert_bet(self, bet: Dict) -> bool:
        """Determine if bet qualifies for alert"""
        ev_score = bet.get('coral_ev_score', 0.0)
        confidence = bet.get('coral_confidence', 0.0)
        recommendation = bet.get('coral_recommendation', 'NO_BET')
        
        # High priority alerts
        if (ev_score >= self.alert_thresholds['high_ev'] and 
            confidence >= self.alert_thresholds['high_confidence']):
            return True
            
        # Medium priority alerts
        if (ev_score >= self.alert_thresholds['medium_ev'] and 
            confidence >= self.alert_thresholds['medium_confidence']):
            return True
            
        # Strong recommendation alerts
        if recommendation == 'STRONG_BET':
            return True
            
        return False
        
    def check_and_send_parlay_alerts(self, parlay_results_file: str = None) -> int:
        """Check parlay results and send alerts"""
        if parlay_results_file is None:
            latest_file = self.reports_path / "optimized_parlays_latest.json"
            if not latest_file.exists():
                self.logger.warning("No parlay results found")
                return 0
            parlay_results_file = latest_file
            
        try:
            with open(parlay_results_file, 'r') as f:
                data = json.load(f)
                
            top_parlays = data.get('top_20_parlays', [])
            alerts_sent = 0
            
            # Send alerts for top 3 parlays
            for parlay in top_parlays[:3]:
                if self.should_alert_parlay(parlay):
                    message = self.format_parlay_alert(parlay)
                    if self.send_message(message):
                        alerts_sent += 1
                        time.sleep(2)  # Longer delay for parlays
                        
            self.logger.info(f"Sent {alerts_sent} parlay alerts")
            return alerts_sent
            
        except Exception as e:
            self.logger.error(f"Error sending parlay alerts: {e}")
            return 0
            
    def should_alert_parlay(self, parlay: Dict) -> bool:
        """Determine if parlay qualifies for alert"""
        total_odds = parlay.get('total_odds', 0.0)
        parlay_ev = parlay.get('parlay_ev', 0.0)
        score = parlay.get('risk_adjusted_score', 0.0)
        legs = parlay.get('total_legs', 0)
        
        # High value parlay
        if (total_odds >= self.alert_thresholds['parlay_min_odds'] and 
            parlay_ev > 0.2 and 
            score > 0.3 and
            legs <= self.alert_thresholds['parlay_max_legs']):
            return True
            
        return False
        
    def send_daily_summary(self) -> bool:
        """Send daily betting summary"""
        try:
            # Collect data from latest files
            summary_data = self.collect_daily_summary_data()
            
            if not summary_data:
                return False
                
            message = self.format_daily_summary(summary_data)
            return self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending daily summary: {e}")
            return False
            
    def collect_daily_summary_data(self) -> Dict:
        """Collect data for daily summary"""
        summary = {}
        
        # Latest Coral results
        coral_files = list(self.reports_path.glob("coral_results_*.json"))
        if coral_files:
            latest_coral = max(coral_files, key=lambda f: f.stat().st_mtime)
            try:
                with open(latest_coral, 'r') as f:
                    coral_data = json.load(f)
                    
                bets = coral_data.get('bets', [])
                summary['total_bets_analyzed'] = len(bets)
                summary['strong_bets'] = len([b for b in bets 
                                           if b.get('coral_recommendation') == 'STRONG_BET'])
                summary['moderate_bets'] = len([b for b in bets 
                                             if b.get('coral_recommendation') == 'MODERATE_BET'])
                                             
                # Performance metrics
                performance = coral_data.get('coral_performance', {})
                summary['avg_inference_time'] = performance.get('avg_inference_time_ms', 0)
                summary['total_predictions'] = performance.get('total_predictions', 0)
                
            except Exception as e:
                self.logger.error(f"Error reading Coral data: {e}")
                
        # Latest parlay results
        parlay_file = self.reports_path / "optimized_parlays_latest.json"
        if parlay_file.exists():
            try:
                with open(parlay_file, 'r') as f:
                    parlay_data = json.load(f)
                    
                parlay_summary = parlay_data.get('optimization_summary', {})
                summary['parlays_generated'] = parlay_summary.get('parlay_combinations_generated', 0)
                summary['top_parlay_score'] = 0
                
                top_parlays = parlay_data.get('top_20_parlays', [])
                if top_parlays:
                    summary['top_parlay_score'] = top_parlays[0].get('risk_adjusted_score', 0)
                    
            except Exception as e:
                self.logger.error(f"Error reading parlay data: {e}")
                
        return summary
        
    def format_daily_summary(self, data: Dict) -> str:
        """Format daily summary message"""
        message = f"""
 <b>EQ12 Coral AI Daily Summary</b>
 {datetime.now().strftime('%Y-%m-%d')}

 <b>Betting Analysis:</b>
 Total bets analyzed: {data.get('total_bets_analyzed', 0)}
 Strong recommendations: {data.get('strong_bets', 0)}
 Moderate recommendations: {data.get('moderate_bets', 0)}

 <b>Parlay Optimization:</b>
 Combinations generated: {data.get('parlays_generated', 0)}
 Top parlay score: {data.get('top_parlay_score', 0):.3f}

 <b>Coral TPU Performance:</b>
 Total predictions: {data.get('total_predictions', 0)}
 Avg inference time: {data.get('avg_inference_time', 0):.1f}ms

<i>Automated report from EQ12 Coral AI system</i>
"""
        
        return message.strip()
        
    def send_system_status(self) -> bool:
        """Send system status alert"""
        try:
            # Check system health
            status_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
                'telegram_enabled': self.enabled,
                'coral_files_count': len(list(self.reports_path.glob("coral_results_*.json"))),
                'parlay_files_count': len(list(self.reports_path.glob("optimized_parlays_*.json"))),
                'alerts_sent_today': 0  # Would track in production
            }
            
            message = f"""
 <b>EQ12 Coral AI System Status</b>

 <b>System Health:</b>
 Telegram alerts: {'Enabled' if status_data['telegram_enabled'] else 'Disabled'}
 Coral result files: {status_data['coral_files_count']}
 Parlay result files: {status_data['parlay_files_count']}

 <b>Last Update:</b> {status_data['timestamp']}

<i>Automated status check</i>
"""
            
            return self.send_message(message.strip())
            
        except Exception as e:
            self.logger.error(f"Error sending system status: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="EQ12 Telegram Alert System")
    parser.add_argument("--workspace", default="c:/EQ12", help="Workspace path")
    parser.add_argument("--trigger", help="Alert trigger condition")
    parser.add_argument("--check-bets", action="store_true", 
                       help="Check and send bet alerts")
    parser.add_argument("--check-parlays", action="store_true", 
                       help="Check and send parlay alerts")
    parser.add_argument("--daily-summary", action="store_true", 
                       help="Send daily summary")
    parser.add_argument("--system-status", action="store_true", 
                       help="Send system status")
    parser.add_argument("--message", help="Send custom message")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    alerter = TelegramAlerter(args.workspace, args.verbose)
    
    if not alerter.enabled:
        print("Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        return
        
    if args.message:
        success = alerter.send_message(args.message)
        print(f"Message sent: {success}")
        
    elif args.check_bets:
        count = alerter.check_and_send_bet_alerts()
        print(f"Sent {count} bet alerts")
        
    elif args.check_parlays:
        count = alerter.check_and_send_parlay_alerts()
        print(f"Sent {count} parlay alerts")
        
    elif args.daily_summary:
        success = alerter.send_daily_summary()
        print(f"Daily summary sent: {success}")
        
    elif args.system_status:
        success = alerter.send_system_status()
        print(f"System status sent: {success}")
        
    elif args.trigger:
        # Parse trigger condition (simplified)
        print(f"Trigger monitoring not implemented: {args.trigger}")
        
    else:
        print("EQ12 Telegram Alert System ready")
        print("Use --check-bets, --check-parlays, --daily-summary, or --system-status")


if __name__ == "__main__":
    main()