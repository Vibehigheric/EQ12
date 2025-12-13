#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EQ12 HARDENED REVENUE TRACKER
UTF-8 Safe, Emoji Sanitized, No Encoding Errors
Target: $750/day automated revenue generation
"""

import sys
import os
import json
import argparse
import logging
import re
from datetime import datetime
from pathlib import Path

# FORCE UTF-8 ENCODING
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Set UTF-8 environment
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LC_ALL"] = "en_US.UTF-8"
os.environ["LANG"] = "en_US.UTF-8"

class HardenedRevenueTracker:
    def __init__(self):
        self.target_daily = 750
        self.target_annual = 273750
        self.log_path = Path("C:/EQ12/logs")
        self.log_path.mkdir(exist_ok=True)
        
        # Setup UTF-8 safe logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8',
            handlers=[
                logging.FileHandler(self.log_path / "revenue_tracker.log", encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def sanitize_text(self, text):
        """Remove problematic characters that break JSON/logging"""
        if not isinstance(text, str):
            text = str(text)
        
        # Remove smart quotes and problematic Unicode
        text = re.sub(r'[\u2018\u2019\u201C\u201D\u2013\u2014]', "'", text)
        # Keep only safe ASCII + basic Unicode
        text = re.sub(r'[^\w\s\-\.\,\:\;\!\?\(\)\[\]\{\}]', '_', text)
        return text.strip()
    
    def safe_filename(self, name):
        """Generate safe filename without problematic characters"""
        name = self.sanitize_text(name)
        name = re.sub(r'[^A-Za-z0-9._-]', '_', name)
        return name[:100]  # Limit length
    
    def safe_json_dump(self, data, path):
        """UTF-8 safe JSON writing with no BOM"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def safe_json_load(self, path):
        """UTF-8 safe JSON reading"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def track_revenue(self, platform, amount, content_type):
        """Track revenue with UTF-8 safety"""
        # Sanitize all inputs
        platform = self.sanitize_text(platform)
        content_type = self.sanitize_text(content_type)
        amount = float(amount)
        
        timestamp = datetime.now().isoformat()
        
        revenue_data = {
            "timestamp": timestamp,
            "platform": platform,
            "amount": amount,
            "content_type": content_type,
            "daily_target": self.target_daily,
            "annual_target": self.target_annual,
            "progress_daily": round((amount / self.target_daily) * 100, 2),
            "empire_mode": os.getenv("CONTENT_EMPIRE_MODE", "INACTIVE"),
            "encoding": "UTF-8"
        }
        
        # Safe filename with date
        date_str = datetime.now().strftime('%Y%m%d')
        safe_date = self.safe_filename(date_str)
        log_file = self.log_path / f"revenue_{safe_date}.json"
        
        try:
            # Read existing data
            entries = []
            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            for line in content.split('\n'):
                                if line.strip():
                                    entries.append(json.loads(line))
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    self.logger.warning(f"Corrupted log file, starting fresh: {e}")
                    entries = []
            
            # Add new entry
            entries.append(revenue_data)
            
            # Write all entries as JSON lines
            with open(log_file, 'w', encoding='utf-8') as f:
                for entry in entries:
                    json.dump(entry, f, ensure_ascii=False, separators=(',', ':'))
                    f.write('\n')
            
            self.logger.info(f"Revenue tracked: {platform} +${amount} ({content_type})")
            print(f"Revenue logged: {platform} +${amount}")
            
            # Calculate and display progress
            daily_total = self.get_daily_total()
            progress_pct = (daily_total / self.target_daily) * 100
            
            print(f"Daily Progress: ${daily_total:.2f} / ${self.target_daily} ({progress_pct:.1f}%)")
            
            if daily_total >= self.target_daily:
                print("DAILY TARGET ACHIEVED! Content Empire at full capacity!")
                
        except Exception as e:
            self.logger.error(f"Revenue tracking error: {e}")
            print(f"Error tracking revenue: {e}")
    
    def get_daily_total(self):
        """Calculate total revenue for today"""
        today = datetime.now().strftime('%Y%m%d')
        log_file = self.log_path / f"revenue_{today}.json"
        
        total = 0.0
        try:
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        for line in content.split('\n'):
                            if line.strip():
                                try:
                                    data = json.loads(line)
                                    total += data.get('amount', 0)
                                except json.JSONDecodeError:
                                    continue  # Skip corrupted lines
        except Exception as e:
            self.logger.error(f"Error calculating daily total: {e}")
            
        return total
    
    def generate_report(self):
        """Generate hardened revenue performance report"""
        daily_total = self.get_daily_total()
        daily_progress = (daily_total / self.target_daily) * 100
        
        report = {
            "content_empire_status": "ACTIVE",
            "revenue_today": daily_total,
            "daily_target": self.target_daily,
            "daily_progress_pct": round(daily_progress, 2),
            "annual_target": self.target_annual,
            "projected_annual": daily_total * 365,
            "empire_efficiency": round((daily_total / self.target_daily) * 100, 1),
            "timestamp": datetime.now().isoformat(),
            "encoding": "UTF-8",
            "system_hardened": True
        }
        
        # Safe report filename
        date_str = datetime.now().strftime('%Y%m%d')
        report_file = self.log_path / f"empire_performance_{date_str}.json"
        
        try:
            self.safe_json_dump(report, report_file)
            
            print("\n=== Content Empire Performance Report ===")
            print(f"Revenue Today: ${daily_total:.2f}")
            print(f"Daily Target: ${self.target_daily}")
            print(f"Progress: {daily_progress:.1f}%")
            print(f"Empire Efficiency: {report['empire_efficiency']}%")
            print(f"Projected Annual: ${report['projected_annual']:,.0f}")
            print(f"Report saved: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Report generation error: {e}")
            print(f"Error generating report: {e}")
        
        return report

def main():
    parser = argparse.ArgumentParser(description='EQ12 Hardened Revenue Tracker')
    parser.add_argument('--platform', help='Revenue platform (sanitized automatically)')
    parser.add_argument('--amount', type=float, help='Revenue amount in USD')
    parser.add_argument('--content-type', help='Content type (sanitized automatically)')
    parser.add_argument('--report', action='store_true', help='Generate performance report')
    
    args = parser.parse_args()
    
    tracker = HardenedRevenueTracker()
    
    if args.report:
        tracker.generate_report()
    elif args.platform and args.amount is not None and args.content_type:
        tracker.track_revenue(args.platform, args.amount, args.content_type)
    else:
        print("Error: Either --report or all tracking arguments required")
        parser.print_help()

if __name__ == "__main__":
    main()