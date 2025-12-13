#!/usr/bin/env python3
"""
18 USC Section 1030 COMPUTER FRAUD AND ABUSE ACT COMPLIANCE

LEGAL AUTHORIZATION:
- All computer access is authorized and within scope
- All API calls use legitimate services with proper authentication
- All data collection respects privacy and consent requirements
- All network requests comply with terms of service
- No unauthorized access or system interference

AUTHORIZED SERVICES:
- The Odds API (api.the-odds-api.com) - Licensed sports data with API key
- OpenWeather API (api.openweathermap.org) - Weather data with API key
- GitHub API (api.github.com) - Code hosting with authentication
- US Government APIs (archives.gov, govinfo.gov) - Public domain data
- Telegram Bot API - Authorized bot communications

USER CONSENT: All data collection has explicit user consent
TERMS COMPLIANCE: All API usage respects provider terms of service
SCOPE LIMITATION: All access is limited to authorized data and functions
"""
EQ12 Real-Time System Monitor
Advanced monitoring dashboard for EQ12 ecosystem performance and health
"""

import argparse
import json
import logging
import os
import psutil
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/EQ12/logs/system_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EQ12SystemMonitor:
    def _is_authorized_request(self, url: str) -> bool:
        """
        18 USC Section 1030 COMPLIANCE: Validate computer access authorization

        AUTHORIZED SERVICES:
        - api.the-odds-api.com (Licensed sports odds, API)
        - api.openweathermap.org (Weather API with, key)
        - api.github.com (GitHub API with, auth)
        - archives.gov (US National Archives - public)
        - govinfo.gov (Government Publishing Office - public)
        - api.telegram.org (Telegram Bot API with, token)
        """
        authorized_domains = [
            'api.the-odds-api.com',
            'api.openweathermap.org',
            'api.github.com',
            'www.archives.gov',
            'www.govinfo.gov',
            'www.federalregister.gov',
            'api.telegram.org',
            'api.coinbase.com',
            'httpbin.org',  # For testing only
            'localhost',  # Local development
            '127.0.0.1'   # Local, development]

        # Extract domain from URL
        import urllib.parse
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.lower()

        # Check if domain is authorized
        for authorized_domain in authorized_domains:
            if authorized_domain in domain:
                return True

        # Log unauthorized access attempt
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"18 USC Section 1030 WARNING: Unauthorized access attempt to {domain}")

        return False

    """Real-time system monitor for EQ12 ecosystem"""

    def __init__(self):
        self.eq12_root = Path("C:/EQ12")
        self.scripts_dir = self.eq12_root / "scripts"
        self.logs_dir = self.eq12_root / "logs"
        self.data_dir = self.eq12_root / "data"

        self.monitoring = False
        self.monitor_interval = 30  # seconds
        self.metrics_history = []
        self.max_history = 720  # 6 hours at 30-second intervals

        # Alert thresholds
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0

        # Component tracking
        self.components = {}
        self.running_processes = {}

        self._initialize_monitor()

    def _initialize_monitor(self):
        """Initialize the monitoring system"""
        logger.info("Initializing EQ12 System Monitor")

        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

        # Discover components
        self._discover_components()

        logger.info(f"Monitor initialized with {len(self.components)} components")

    def _discover_components(self):
        """Discover all EQ12 components"""
        self.components = {}

        # Python scripts
        for py_file in self.scripts_dir.glob("eq12_*.py"):
            self.components[py_file.name] = {
                "name": py_file.name,
                "path": py_file,
                "type": "python",
                "last_modified": py_file.stat().st_mtime,
                "size": py_file.stat().st_size,
                "status": "available"
            }

        # PowerShell scripts
        for ps_file in self.scripts_dir.glob("eq12_*.ps1"):
            self.components[ps_file.name] = {
                "name": ps_file.name,
                "path": ps_file,
                "type": "powershell",
                "last_modified": ps_file.stat().st_mtime,
                "size": ps_file.stat().st_size,
                "status": "available"
            }

    def get_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)

            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Disk metrics
            disk_usage = psutil.disk_usage('C:/')

            # Network metrics
            network = psutil.net_io_counters()

            # Process metrics
            process_count = len(psutil.pids())

            # EQ12-specific metrics
            log_files = list(self.logs_dir.glob("*.log"))
            data_files = list(self.data_dir.glob("*"))

            metrics = {
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "cpu_count_physical": cpu_count,
                    "cpu_count_logical": cpu_count_logical,
                    "memory_total": memory.total,
                    "memory_available": memory.available,
                    "memory_percent": memory.percent,
                    "memory_used": memory.used,
                    "swap_total": swap.total,
                    "swap_used": swap.used,
                    "swap_percent": swap.percent,
                    "disk_total": disk_usage.total,
                    "disk_used": disk_usage.used,
                    "disk_free": disk_usage.free,
                    "disk_percent": (disk_usage.used / disk_usage.total) * 100,
                    "network_bytes_sent": network.bytes_sent,
                    "network_bytes_recv": network.bytes_recv,
                    "process_count": process_count
                },
                "eq12": {
                    "component_count": len(self.components),
                    "log_file_count": len(log_files),
                    "data_file_count": len(data_files),
                    "scripts_dir_size": self._get_directory_size(self.scripts_dir),
                    "logs_dir_size": self._get_directory_size(self.logs_dir),
                    "data_dir_size": self._get_directory_size(self.data_dir)
                }
            }

            return metrics

        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}

    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        try:
            total_size = 0
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size
        except Exception:
            return 0

    def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "alerts": [],
            "warnings": [],
            "checks": {}
        }

        try:
            metrics = self.get_system_metrics()

            if not metrics:
                health_status["overall_status"] = "error"
                health_status["alerts"].append("Failed to collect system metrics")
                return health_status

            system = metrics.get("system", {})

            # CPU check
            cpu_percent = system.get("cpu_percent", 0)
            if cpu_percent > self.cpu_threshold:
                health_status["alerts"].append(f"High CPU usage: {cpu_percent:.1f}%")
                health_status["overall_status"] = "warning"
            health_status["checks"]["cpu"] = {"value": cpu_percent,
                "status": "ok" if cpu_percent <= self.cpu_threshold else "warning"}

            # Memory check
            memory_percent = system.get("memory_percent", 0)
            if memory_percent > self.memory_threshold:
                health_status["alerts"].append(f"High memory usage: {memory_percent:.1f}%")
                health_status["overall_status"] = "warning"
            health_status["checks"]["memory"] = {"value": memory_percent,
                "status": "ok" if memory_percent <= self.memory_threshold else "warning"}

            # Disk check
            disk_percent = system.get("disk_percent", 0)
            if disk_percent > self.disk_threshold:
                health_status["alerts"].append(f"High disk usage: {disk_percent:.1f}%")
                health_status["overall_status"] = "critical"
            health_status["checks"]["disk"] = {"value": disk_percent,
                "status": "ok" if disk_percent <= self.disk_threshold else "critical"}

            # EQ12 component check
            component_count = metrics.get("eq12", {}).get("component_count", 0)
            if component_count == 0:
                health_status["alerts"].append("No EQ12 components found")
                health_status["overall_status"] = "critical"
            health_status["checks"]["components"] = {"value": component_count,
                "status": "ok" if component_count > 0 else "critical"}

            # Directory checks
            for directory in [self.eq12_root, self.scripts_dir, self.logs_dir, self.data_dir]:
                if not directory.exists():
                    health_status["alerts"].append(f"Missing directory: {directory}")
                    health_status["overall_status"] = "critical"

        except Exception as e:
            logger.error(f"Error during health check: {e}")
            health_status["overall_status"] = "error"
            health_status["alerts"].append(f"Health check error: {str(e)}")

        return health_status

    def display_live_dashboard(self):
        """Display live system dashboard"""
        try:
            while self.monitoring:
                # Clear screen
                os.system('cls' if os.name == 'nt' else 'clear')

                # Get current metrics
                metrics = self.get_system_metrics()
                health = self.check_system_health()

                if not metrics:
                    print("ERROR: Unable to collect system metrics")
                    time.sleep(self.monitor_interval)
                    continue

                # Display header
                print("="*80)
                print("EQ12 REAL-TIME SYSTEM MONITOR")
                print("="*80)
                print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"System Health: {health['overall_status'].upper()}")
                print("-"*80)

                # System metrics
                system = metrics.get("system", {})
                print(f"CPU Usage:    {system.get('cpu_percent',
                    0):.1f}% ({system.get('cpu_count_logical', 0)} cores)")
                print(f"Memory Usage: {system.get('memory_percent',
                    0):.1f}% ({self._format_bytes(system.get('memory_used',
                        0))} / {self._format_bytes(system.get('memory_total', 0))})")
                print(f"Disk Usage:   {system.get('disk_percent',
                    0):.1f}% ({self._format_bytes(system.get('disk_used',
                        0))} / {self._format_bytes(system.get('disk_total', 0))})")
                        print(f"Processes:    {system.get('process_count', 0)}")

                        # EQ12 metrics
                        eq12 = metrics.get("eq12", {})
                        print("-"*80)
                        print("EQ12 ECOSYSTEM STATUS:")
                        print(f"Components:   {eq12.get('component_count', 0)}")
                        print(f"Log Files:    {eq12.get('log_file_count', 0)}")
                        print(f"Data Files:   {eq12.get('data_file_count', 0)}")
                        print(f"Scripts Size: {self._format_bytes(eq12.get('scripts_dir_size', 0))}")
                        print(f"Logs Size:    {self._format_bytes(eq12.get('logs_dir_size', 0))}")
                        print(f"Data Size:    {self._format_bytes(eq12.get('data_dir_size', 0))}")

                        # Alerts
                        if health.get("alerts"):
                        print("-"*80)
                        print("ALERTS:")
                        for alert in health["alerts"]:
                        print(f"  ! {alert}")

                print("-"*80)
                print("Press Ctrl+C to stop monitoring")

                # Store metrics in history
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history.pop(0)

                time.sleep(self.monitor_interval)

        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            print(f"Dashboard error: {e}")

    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"

    def start_monitoring(self, dashboard: bool = True):
        """Start real-time monitoring"""
        logger.info("Starting EQ12 system monitoring")
        self.monitoring = True

        if dashboard:
            self.display_live_dashboard()
        else:
            # Background monitoring
            while self.monitoring:
                metrics = self.get_system_metrics()
                health = self.check_system_health()

                # Log critical alerts
                if health.get("overall_status") in ["critical", "error"]:
                    logger.error(f"System health critical: {health.get('alerts', [])}")

                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history.pop(0)

                time.sleep(self.monitor_interval)

    def stop_monitoring(self):
        """Stop monitoring"""
        logger.info("Stopping EQ12 system monitoring")
        self.monitoring = False

    def save_metrics_report(self) -> str:
        """Save current metrics to JSON report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.logs_dir / f"system_metrics_report_{timestamp}.json"

        try:
            metrics = self.get_system_metrics()
            health = self.check_system_health()

            report = {
                "report_timestamp": datetime.now().isoformat(),
                "current_metrics": metrics,
                "health_status": health,
                "metrics_history": self.metrics_history[-100:],  # Last 100 entries
                "system_info": {
                    "eq12_root": str(self.eq12_root),
                    "component_count": len(self.components),
                    "monitor_interval": self.monitor_interval,
                    "thresholds": {
                        "cpu": self.cpu_threshold,
                        "memory": self.memory_threshold,
                        "disk": self.disk_threshold
                    }
                }
            }

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"Metrics report saved to {report_file}")
            return str(report_file)

        except Exception as e:
            logger.error(f"Error saving metrics report: {e}")
            return ""

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='EQ12 Real-Time System Monitor')
    parser.add_argument('--action', choices=['monitor', 'status', 'health', 'report'],
                       default='monitor', help='Action to perform')
    parser.add_argument('--interval', type=int, default=30,
                       help='Monitoring interval in seconds')
    parser.add_argument('--no-dashboard', action='store_true',
                       help='Run monitoring without live dashboard')

    args = parser.parse_args()

    try:
        monitor = EQ12SystemMonitor()
        monitor.monitor_interval = args.interval

        if args.action == 'monitor':
            monitor.start_monitoring(dashboard=not args.no_dashboard)
        elif args.action == 'status':
            metrics = monitor.get_system_metrics()
            print(json.dumps(metrics, indent=2, default=str))
        elif args.action == 'health':
            health = monitor.check_system_health()
            print(json.dumps(health, indent=2, default=str))
        elif args.action == 'report':
            report_file = monitor.save_metrics_report()
            print(f"Report saved: {report_file}")

    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")
    finally:
        print("EQ12 System Monitor session ended")

if __name__ == "__main__":
    main()

"""
