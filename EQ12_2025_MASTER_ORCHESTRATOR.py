#!/usr/bin/env python3
"""
EQ12 2025 Master Revenue Orchestrator
Unified control system for all 5 revenue streams
Revenue Target: $8.5M/year baseline → $12M/year with optimization
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import subprocess
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure master logging
LOG_DIR = Path("C:/EQ12/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f"master_orchestrator_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EQ12_MASTER")


@dataclass
class RevenueStream:
    """Revenue stream configuration"""
    name: str
    enabled: bool
    script_path: str
    priority: int  # 1=critical, 2=high, 3=medium
    revenue_target_monthly: float
    actual_revenue_monthly: float = 0.0
    last_run: Optional[str] = None
    status: str = "idle"
    error_count: int = 0


class EQ12MasterOrchestrator:
    """Master control system for EQ12 2025 revenue automation"""
    
    def __init__(self, config_path: str = "config/master_config.json"):
        self.config_path = config_path
        self.start_time = datetime.now()
        self.revenue_streams = self._initialize_revenue_streams()
        self.performance_metrics = {
            "total_revenue_ytd": 0.0,
            "target_revenue_ytd": 8_500_000.0,
            "revenue_today": 0.0,
            "uptime_hours": 0.0,
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0
        }
        self.load_config()
        
    def _initialize_revenue_streams(self) -> Dict[str, RevenueStream]:
        """Initialize all 5 revenue streams"""
        return {
            "betting_intelligence": RevenueStream(
                name="AI Betting Intelligence Suite",
                enabled=True,
                script_path="scripts/eq12_live_sports_scanner_1hour.py",
                priority=1,
                revenue_target_monthly=300_000.0  # $300K/month from betting automation
            ),
            "prompt_monetization": RevenueStream(
                name="AI Prompt Monetization Engine",
                enabled=True,
                script_path="scripts/eq12_prompt_executor.py",
                priority=1,
                revenue_target_monthly=150_000.0  # $150K/month from 20K prompt library
            ),
            "pacer_legal": RevenueStream(
                name="PACER Legal Intelligence",
                enabled=True,
                script_path="scripts/eq12_pacer_scraper.py",
                priority=2,
                revenue_target_monthly=12_500.0  # $150K/year documented
            ),
            "travel_automation": RevenueStream(
                name="Travel Deal Automation",
                enabled=True,
                script_path="scripts/eq12_american_airlines_flight_hunter.py",
                priority=3,
                revenue_target_monthly=25_000.0  # $25K/month from travel affiliate
            ),
            "content_empire": RevenueStream(
                name="Content Empire Builder",
                enabled=True,
                script_path="scripts/eq12_master_copywriting_empire.py",
                priority=2,
                revenue_target_monthly=75_000.0  # $75K/month from Gumroad, eBay, TikTok
            )
        }
    
    def load_config(self):
        """Load configuration from JSON"""
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Update revenue streams from config
                for stream_id, stream_data in config.get("revenue_streams", {}).items():
                    if stream_id in self.revenue_streams:
                        self.revenue_streams[stream_id].enabled = stream_data.get("enabled", True)
                        self.revenue_streams[stream_id].actual_revenue_monthly = stream_data.get("revenue", 0.0)
                logger.info(f"Loaded configuration from {config_file}")
        else:
            logger.warning(f"Config file not found: {config_file}. Using defaults.")
            self.save_config()
    
    def save_config(self):
        """Save current configuration to JSON"""
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            "last_updated": datetime.now().isoformat(),
            "revenue_streams": {
                stream_id: {
                    "enabled": stream.enabled,
                    "revenue": stream.actual_revenue_monthly,
                    "last_run": stream.last_run,
                    "status": stream.status,
                    "error_count": stream.error_count
                }
                for stream_id, stream in self.revenue_streams.items()
            },
            "performance_metrics": self.performance_metrics
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Configuration saved to {config_file}")
    
    def execute_revenue_stream(self, stream_id: str) -> bool:
        """Execute a single revenue stream"""
        stream = self.revenue_streams.get(stream_id)
        if not stream or not stream.enabled:
            logger.warning(f"Stream {stream_id} is disabled or not found")
            return False
        
        logger.info(f"🚀 Executing: {stream.name}")
        stream.status = "running"
        
        try:
            script_path = Path(stream.script_path)
            if not script_path.exists():
                logger.error(f"Script not found: {script_path}")
                stream.error_count += 1
                stream.status = "error"
                return False
            
            # Execute Python script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {stream.name} completed successfully")
                stream.status = "completed"
                stream.last_run = datetime.now().isoformat()
                stream.error_count = 0
                self.performance_metrics["successful_executions"] += 1
                return True
            else:
                logger.error(f"❌ {stream.name} failed with code {result.returncode}")
                logger.error(f"Error: {result.stderr[:500]}")
                stream.status = "failed"
                stream.error_count += 1
                self.performance_metrics["failed_executions"] += 1
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏱️ {stream.name} timed out after 1 hour")
            stream.status = "timeout"
            stream.error_count += 1
            self.performance_metrics["failed_executions"] += 1
            return False
        except Exception as e:
            logger.error(f"💥 {stream.name} crashed: {str(e)}")
            stream.status = "crashed"
            stream.error_count += 1
            self.performance_metrics["failed_executions"] += 1
            return False
        finally:
            self.performance_metrics["total_executions"] += 1
            self.save_config()
    
    def execute_all_streams(self, parallel: bool = False):
        """Execute all enabled revenue streams"""
        logger.info("=" * 80)
        logger.info("🎯 EQ12 2025 MASTER ORCHESTRATOR - FULL EXECUTION")
        logger.info("=" * 80)
        
        enabled_streams = [
            (stream_id, stream) for stream_id, stream in self.revenue_streams.items()
            if stream.enabled
        ]
        
        # Sort by priority
        enabled_streams.sort(key=lambda x: x[1].priority)
        
        logger.info(f"📊 Executing {len(enabled_streams)} revenue streams")
        logger.info(f"💰 Monthly Target: ${sum(s.revenue_target_monthly for _, s in enabled_streams):,.0f}")
        
        if parallel:
            # Parallel execution for speed
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(self.execute_revenue_stream, stream_id): stream_id
                    for stream_id, _ in enabled_streams
                }
                
                for future in as_completed(futures):
                    stream_id = futures[future]
                    try:
                        success = future.result()
                        if success:
                            logger.info(f"✅ {stream_id} completed")
                        else:
                            logger.warning(f"⚠️ {stream_id} had issues")
                    except Exception as e:
                        logger.error(f"❌ {stream_id} failed: {str(e)}")
        else:
            # Sequential execution for reliability
            for stream_id, stream in enabled_streams:
                logger.info(f"\n{'='*60}")
                logger.info(f"Priority {stream.priority}: {stream.name}")
                logger.info(f"Target: ${stream.revenue_target_monthly:,.0f}/month")
                logger.info(f"{'='*60}\n")
                
                success = self.execute_revenue_stream(stream_id)
                
                if not success and stream.priority == 1:
                    logger.error(f"🛑 CRITICAL STREAM FAILED: {stream.name}")
                    logger.error("Stopping execution due to critical failure")
                    break
                
                # Small delay between streams
                time.sleep(2)
        
        self.print_summary()
    
    def print_summary(self):
        """Print execution summary"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 EXECUTION SUMMARY")
        logger.info("=" * 80)
        
        total_target = sum(s.revenue_target_monthly for s in self.revenue_streams.values() if s.enabled)
        total_actual = sum(s.actual_revenue_monthly for s in self.revenue_streams.values() if s.enabled)
        
        logger.info(f"\n💰 REVENUE METRICS:")
        logger.info(f"  Monthly Target: ${total_target:,.0f}")
        logger.info(f"  Monthly Actual: ${total_actual:,.0f}")
        logger.info(f"  Achievement:    {(total_actual/total_target*100) if total_target > 0 else 0:.1f}%")
        
        logger.info(f"\n⚡ PERFORMANCE METRICS:")
        logger.info(f"  Total Executions:      {self.performance_metrics['total_executions']}")
        logger.info(f"  Successful:            {self.performance_metrics['successful_executions']}")
        logger.info(f"  Failed:                {self.performance_metrics['failed_executions']}")
        success_rate = (self.performance_metrics['successful_executions'] / 
                       self.performance_metrics['total_executions'] * 100) if self.performance_metrics['total_executions'] > 0 else 0
        logger.info(f"  Success Rate:          {success_rate:.1f}%")
        
        logger.info(f"\n📈 STREAM STATUS:")
        for stream_id, stream in sorted(self.revenue_streams.items(), key=lambda x: x[1].priority):
            if stream.enabled:
                status_emoji = {
                    "completed": "✅",
                    "running": "🔄",
                    "failed": "❌",
                    "error": "⚠️",
                    "idle": "⏸️"
                }.get(stream.status, "❓")
                
                logger.info(f"  {status_emoji} {stream.name}")
                logger.info(f"     Status: {stream.status} | Errors: {stream.error_count} | " +
                          f"Target: ${stream.revenue_target_monthly:,.0f}/mo")
        
        runtime = (datetime.now() - self.start_time).total_seconds() / 60
        logger.info(f"\n⏱️  Total Runtime: {runtime:.1f} minutes")
        logger.info("=" * 80 + "\n")
    
    def run_health_check(self):
        """Check health of all revenue streams"""
        logger.info("🏥 Running EQ12 Health Check...")
        
        issues = []
        for stream_id, stream in self.revenue_streams.items():
            script_path = Path(stream.script_path)
            if not script_path.exists():
                issues.append(f"❌ {stream.name}: Script missing at {script_path}")
            elif stream.error_count > 5:
                issues.append(f"⚠️ {stream.name}: High error count ({stream.error_count})")
            elif stream.enabled and not stream.last_run:
                issues.append(f"⏸️ {stream.name}: Never executed")
        
        if issues:
            logger.warning(f"Found {len(issues)} health issues:")
            for issue in issues:
                logger.warning(f"  {issue}")
        else:
            logger.info("✅ All systems healthy!")
        
        return len(issues) == 0


def main():
    parser = argparse.ArgumentParser(description="EQ12 2025 Master Revenue Orchestrator")
    parser.add_argument("--mode", choices=["all", "single", "health"], default="all",
                       help="Execution mode")
    parser.add_argument("--stream", help="Specific stream ID for single mode")
    parser.add_argument("--parallel", action="store_true",
                       help="Run streams in parallel (faster but riskier)")
    parser.add_argument("--config", default="config/master_config.json",
                       help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = EQ12MasterOrchestrator(config_path=args.config)
    
    try:
        if args.mode == "health":
            orchestrator.run_health_check()
        elif args.mode == "single":
            if not args.stream:
                logger.error("--stream required for single mode")
                sys.exit(1)
            orchestrator.execute_revenue_stream(args.stream)
        else:  # all
            orchestrator.execute_all_streams(parallel=args.parallel)
        
        logger.info("🎉 Orchestrator execution completed")
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Execution interrupted by user")
        orchestrator.save_config()
        sys.exit(130)
    except Exception as e:
        logger.error(f"💥 Fatal error: {str(e)}", exc_info=True)
        orchestrator.save_config()
        sys.exit(1)


if __name__ == "__main__":
    main()
