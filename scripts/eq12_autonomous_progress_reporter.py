#!/usr/bin/env python3
"""
EQ12 Autonomous Development Progress Reporter
Sends hourly Telegram updates during development sprints
"""

import os
import sys
import time
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_telegram_message(message, parse_mode='HTML'):
    """Send message to Telegram chat"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error(" Telegram credentials not configured")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': parse_mode,
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        logger.info(" Telegram message sent successfully")
        return True
    except Exception as e:
        logger.error(f" Failed to send Telegram message: {e}")
        return False

def format_progress_message(hour, completed_tasks, current_task, stats):
    """Format hourly progress update message"""
    
    emoji_progress = "" * completed_tasks + "" + "" * (10 - completed_tasks - 1)
    
    message = f"""
 <b>EQ12 AUTONOMOUS SPRINT - HOUR {hour}</b>

 <b>Progress</b>: {emoji_progress}
 <b>Completed</b>: {completed_tasks}/10 tasks
 <b>Current</b>: {current_task}

 <b>Hour {hour} Stats</b>:
{stats}

 <b>Sprint Time</b>: {hour}/10 hours
 <b>Next Update</b>: {(datetime.now() + timedelta(hours=1)).strftime('%H:%M')}

 <i>Building your NBA analytics empire autonomously...</i>
    """
    
    return message.strip()

def send_initial_sprint_notification():
    """Send initial sprint start notification"""
    message = f"""
 <b>EQ12 AUTONOMOUS DEVELOPMENT SPRINT INITIATED</b>

 <b>Duration</b>: 10 hours
 <b>Started</b>: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 <b>Target</b>: Complete NBA analytics ecosystem

 <b>Sprint Objectives</b>:
 28+ NBA analysis notebooks
 Complete test suite (80%+ coverage)
 Optimized trading algorithms
 Enhanced database architecture
 ML prediction models
 Real-time dashboards
 Automation framework
 Production-ready code

 <b>Updates</b>: Every hour for 10 hours
 <b>Next Update</b>: {(datetime.now() + timedelta(hours=1)).strftime('%H:%M')}

<i>Let's build something epic! </i>
    """
    
    return send_telegram_message(message)

if __name__ == "__main__":
    # Send initial notification
    send_initial_sprint_notification()
    
    # Example usage for testing
    test_stats = """
  Created: 5 NBA notebooks
  Tests: 15 new test cases
  Optimized: 3 algorithms
  Lines: 2,847 code written
"""
    
    test_message = format_progress_message(
        hour=1, 
        completed_tasks=1, 
        current_task="Building Comprehensive Test Suite",
        stats=test_stats
    )
    
    print("Test message preview:")
    print(test_message)