#!/usr/bin/env python3
"""
EQ12 NBA Telegram Bot
Automated NBA betting recommendations via Telegram
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse
import logging
from pathlib import Path
import asyncio
import aiohttp


class NBATelegramBot:
    """NBA betting recommendations Telegram bot"""
    
    def __init__(self, workspace_dir: str = "C:/EQ12"):
        self.workspace_dir = Path(workspace_dir)
        self.data_dir = self.workspace_dir / "data"
        self.logs_dir = self.workspace_dir / "logs"
        
        # Ensure directories exist
        for directory in [self.data_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Telegram configuration from environment
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.bot_token or not self.chat_id:
            self.logger.warning("Telegram credentials not configured in environment")
        
        # Database connections
        self.predictions_db = self.data_dir / "nba_predictions.db"
        self.parlays_db = self.data_dir / "nba_parlays.db"
        
    def setup_logging(self):
        """Configure logging"""
        log_file = self.logs_dir / f"telegram_bot_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_daily_summary(self) -> Dict[str, Any]:
        """Get daily summary statistics"""
        summary = {
            "games_count": 0,
            "predictions_count": 0,
            "high_value_props": 0,
            "top_parlays": 0,
            "avg_confidence": 0,
            "max_ev": 0
        }
        
        try:
            if self.predictions_db.exists():
                with sqlite3.connect(self.predictions_db) as conn:
                    cursor = conn.cursor()
                    
                    # Count today's predictions
                    cursor.execute("""
                        SELECT COUNT(*), AVG(confidence), MAX(expected_value)
                        FROM predictions 
                        WHERE date(prediction_time) = date('now')
                        AND expected_value > 0
                    """)
                    
                    row = cursor.fetchone()
                    if row and row[0]:
                        summary["predictions_count"] = row[0]
                        summary["avg_confidence"] = row[1] or 0
                        summary["max_ev"] = row[2] or 0
                    
                    # Count high-value props (EV > 5%)
                    cursor.execute("""
                        SELECT COUNT(*)
                        FROM predictions 
                        WHERE date(prediction_time) = date('now')
                        AND expected_value > 0.05
                    """)
                    
                    summary["high_value_props"] = cursor.fetchone()[0]
                    
                    # Count unique games
                    cursor.execute("""
                        SELECT COUNT(DISTINCT game_id)
                        FROM predictions 
                        WHERE date(prediction_time) = date('now')
                    """)
                    
                    summary["games_count"] = cursor.fetchone()[0]
            
            # Check for parlays
            parlay_file = self.data_dir / f"parlays_{datetime.now().strftime('%Y%m%d')}.json"
            if parlay_file.exists():
                with open(parlay_file, 'r') as f:
                    parlay_data = json.load(f)
                summary["top_parlays"] = len(parlay_data.get("parlays", []))
        
        except Exception as e:
            self.logger.error(f"Error getting daily summary: {e}")
        
        return summary
    
    def get_top_picks(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top picks by expected value"""
        picks = []
        
        try:
            if self.predictions_db.exists():
                with sqlite3.connect(self.predictions_db) as conn:
                    cursor = conn.cursor()
                    
                    query = """
                    SELECT 
                        player_name,
                        prop_type,
                        line,
                        predicted_value,
                        confidence,
                        expected_value,
                        bookmaker,
                        odds,
                        game_info
                    FROM predictions 
                    WHERE date(prediction_time) = date('now')
                        AND expected_value > 0.03
                        AND confidence > 0.65
                    ORDER BY expected_value DESC
                    LIMIT ?
                    """
                    
                    cursor.execute(query, (limit,))
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        picks.append({
                            "player": row[0],
                            "prop_type": row[1],
                            "line": row[2],
                            "predicted": row[3],
                            "confidence": row[4],
                            "expected_value": row[5],
                            "bookmaker": row[6],
                            "odds": row[7],
                            "game": row[8] if row[8] else "Unknown"
                        })
        
        except Exception as e:
            self.logger.error(f"Error getting top picks: {e}")
        
        return picks
    
    def get_best_parlays(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Get best parlays by expected value"""
        parlays = []
        
        try:
            parlay_file = self.data_dir / f"parlays_{datetime.now().strftime('%Y%m%d')}.json"
            
            if parlay_file.exists():
                with open(parlay_file, 'r') as f:
                    parlay_data = json.load(f)
                
                # Filter and sort parlays
                good_parlays = [
                    p for p in parlay_data.get("parlays", [])
                    if p.get("expected_value", 0) > 0.02 and
                       p.get("avg_confidence", 0) > 0.6 and
                       len(p.get("legs", [])) <= 4
                ]
                
                sorted_parlays = sorted(good_parlays, 
                                      key=lambda x: x.get("expected_value", 0), 
                                      reverse=True)
                
                parlays = sorted_parlays[:limit]
        
        except Exception as e:
            self.logger.error(f"Error getting best parlays: {e}")
        
        return parlays
    
    def format_telegram_message(self) -> str:
        """Format comprehensive Telegram message"""
        
        try:
            summary = self.get_daily_summary()
            top_picks = self.get_top_picks(5)
            best_parlays = self.get_best_parlays(3)
            
            # Header
            message = " *EQ12 NBA BETTING INTELLIGENCE*\n"
            message += f" {datetime.now().strftime('%A, %B %d, %Y')}\n"
            message += "=" * 35 + "\n\n"
            
            # Daily summary
            message += " *DAILY SUMMARY*\n"
            message += f" Games Analyzed: *{summary['games_count']}*\n"
            message += f" Predictions Generated: *{summary['predictions_count']}*\n"
            message += f" High-Value Props: *{summary['high_value_props']}*\n"
            message += f" Best Expected Value: *+{summary['max_ev']:.1%}*\n"
            message += f" Parlays Created: *{summary['top_parlays']}*\n"
            message += f" Avg Confidence: *{summary['avg_confidence']:.1%}*\n\n"
            
            # Top picks section
            if top_picks:
                message += " *TOP PICKS (Expected Value)*\n"
                message += "" * 35 + "\n"
                
                for i, pick in enumerate(top_picks, 1):
                    confidence_emoji = "" if pick['confidence'] > 0.8 else "" if pick['confidence'] > 0.7 else ""
                    
                    message += f"*{i}. {pick['player']}*\n"
                    message += f"   {pick['prop_type']} {pick['line']}\n"
                    message += f"   {confidence_emoji} Predicted: *{pick['predicted']:.1f}*\n"
                    message += f"    EV: *+{pick['expected_value']:.1%}* | Conf: *{pick['confidence']:.1%}*\n"
                    message += f"    {pick['bookmaker']} | {pick['odds']}\n"
                    message += f"    {pick['game']}\n\n"
            else:
                message += " *TOP PICKS*\n"
                message += "No qualified picks found today.\n"
                message += "Minimum criteria: EV > 3%, Confidence > 65%\n\n"
            
            # Best parlays section
            if best_parlays:
                message += " *OPTIMIZED PARLAYS*\n"
                message += "" * 35 + "\n"
                
                for i, parlay in enumerate(best_parlays, 1):
                    legs = parlay.get('legs', [])
                    total_odds = parlay.get('total_odds', 0)
                    expected_value = parlay.get('expected_value', 0)
                    avg_confidence = parlay.get('avg_confidence', 0)
                    
                    message += f"*{i}. {len(legs)}-Leg Parlay*\n"
                    message += f"    Odds: *+{total_odds:.0f}* | EV: *+{expected_value:.1%}*\n"
                    message += f"    Avg Confidence: *{avg_confidence:.1%}*\n"
                    
                    for j, leg in enumerate(legs[:3], 1):  # Show first 3 legs
                        message += f"   {j}. {leg.get('player', 'Unknown')} {leg.get('prop_type', '')}\n"
                    
                    if len(legs) > 3:
                        message += f"   ... +{len(legs) - 3} more legs\n"
                    
                    message += "\n"
            else:
                message += " *OPTIMIZED PARLAYS*\n"
                message += "No qualified parlays found today.\n\n"
            
            # Cluster status
            cluster_file = self.logs_dir / f"cluster_status_{datetime.now().strftime('%Y%m%d')}.json"
            if cluster_file.exists():
                try:
                    with open(cluster_file, 'r') as f:
                        cluster_data = json.load(f)
                    
                    message += " *CLUSTER STATUS*\n"
                    eq12_status = "" if cluster_data.get('eq12_online', False) else ""
                    pi_status = "" if cluster_data.get('pi_online', False) else ""
                    tpu_status = "" if cluster_data.get('tpu_available', False) else ""
                    
                    message += f"{eq12_status} EQ12 Host | {pi_status} Pi5 Node | {tpu_status} Coral TPU\n"
                    message += f" Inference Queue: {cluster_data.get('inference_queue', 0)} jobs\n\n"
                
                except Exception:
                    pass
            
            # Footer
            message += " *POWERED BY*\n"
            message += "EQ12 + Raspberry Pi 5 + Coral TPU\n"
            message += "TensorFlow Lite + Monte Carlo Simulation\n\n"
            
            message += " *DISCLAIMER*\n"
            message += "_Predictions are AI-generated estimates._\n"
            message += "_Always gamble responsibly._\n"
            message += "_Past performance  future results._\n\n"
            
            message += f" Generated: {datetime.now().strftime('%H:%M:%S UTC')}\n"
            message += " EQ12 NBA Intelligence v2.0"
            
            return message
        
        except Exception as e:
            self.logger.error(f"Error formatting Telegram message: {e}")
            return f" Error generating NBA report: {e}"
    
    async def send_telegram_message(self, message: str) -> bool:
        """Send message to Telegram"""
        
        if not self.bot_token or not self.chat_id:
            self.logger.error("Telegram credentials not configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, timeout=30) as response:
                    if response.status == 200:
                        self.logger.info("Telegram message sent successfully")
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Telegram API error {response.status}: {error_text}")
                        return False
        
        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {e}")
            return False
    
    async def send_daily_report(self) -> bool:
        """Send daily NBA betting report"""
        self.logger.info("Generating daily NBA betting report...")
        
        try:
            message = self.format_telegram_message()
            
            # Save message to file
            message_file = self.logs_dir / f"telegram_message_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(message_file, 'w', encoding='utf-8') as f:
                f.write(message)
            
            self.logger.info(f"Message saved to: {message_file}")
            
            # Send to Telegram if configured
            if self.bot_token and self.chat_id:
                success = await self.send_telegram_message(message)
                if success:
                    self.logger.info("Daily report sent to Telegram successfully")
                else:
                    self.logger.error("Failed to send daily report to Telegram")
                return success
            else:
                self.logger.info("Telegram not configured, message saved to file only")
                print("\n" + "="*60)
                print("TELEGRAM MESSAGE READY:")
                print("="*60)
                print(message)
                print("="*60)
                return True
        
        except Exception as e:
            self.logger.error(f"Error sending daily report: {e}")
            return False
    
    def generate_text_report(self) -> str:
        """Generate simple text report for console output"""
        summary = self.get_daily_summary()
        top_picks = self.get_top_picks(3)
        
        report = f"""
 EQ12 NBA DAILY REPORT - {datetime.now().strftime('%Y-%m-%d')}
{'='*60}

 SUMMARY:
  Games: {summary['games_count']} | Predictions: {summary['predictions_count']}
  High-Value Props: {summary['high_value_props']} | Max EV: +{summary['max_ev']:.1%}

 TOP 3 PICKS:
"""
        
        if top_picks:
            for i, pick in enumerate(top_picks, 1):
                report += f"""
  {i}. {pick['player']} - {pick['prop_type']} {pick['line']}
     Predicted: {pick['predicted']:.1f} | EV: +{pick['expected_value']:.1%}
     Confidence: {pick['confidence']:.1%} | {pick['bookmaker']}
"""
        else:
            report += "\n  No qualifying picks found today.\n"
        
        report += f"\n Generated: {datetime.now().strftime('%H:%M:%S')}"
        
        return report


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EQ12 NBA Telegram Bot")
    parser.add_argument("--workspace", type=str, default="C:/EQ12",
                       help="EQ12 workspace directory")
    parser.add_argument("--action", type=str, default="report",
                       choices=["report", "test", "daily"],
                       help="Action to perform")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        bot = NBATelegramBot(args.workspace)
        
        if args.action == "test":
            # Test message
            test_message = " EQ12 NBA Bot Test\n\nBot is working correctly! "
            
            async def test_send():
                return await bot.send_telegram_message(test_message)
            
            success = asyncio.run(test_send())
            if success:
                print(" Test message sent successfully!")
            else:
                print(" Test message failed")
            return 0 if success else 1
        
        elif args.action == "daily":
            # Send daily report
            success = asyncio.run(bot.send_daily_report())
            return 0 if success else 1
        
        else:
            # Generate and display report
            report = bot.generate_text_report()
            print(report)
            return 0
    
    except Exception as e:
        print(f" Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())