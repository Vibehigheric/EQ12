#!/usr/bin/env python3
"""
 EQ12 RESOURCE MONITOR WRAPPER - System Health Intelligence
============================================================

Comprehensive resource monitoring wrapper that orchestrates multiple
monitoring systems for complete EQ12 infrastructure health tracking.

Features:
- Real-time CPU, Memory, Disk monitoring
- Process health tracking
- Network connectivity checks
- Database performance monitoring
- Service availability checks
- Auto-healing trigger integration
- Performance trend analysis
- Resource usage forecasting

Author: EQ12 Quantum Development Team
Version: 1.0.0 - Resource Intelligence
Date: November 7, 2025
"""

import asyncio
import json
import logging
import os
import psutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import aiohttp
import sqlite3


class EQ12ResourceMonitorWrapper:
    """Comprehensive resource monitoring orchestrator."""

    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.logs_path = self.workspace_path / "logs"
        self.data_path = self.workspace_path / "data"

        # Ensure directories exist
        self.logs_path.mkdir(exist_ok=True)
        self.data_path.mkdir(exist_ok=True)

        # Setup logging
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.log_file = self.logs_path / f"resource_monitor_{self.timestamp}.json"

        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        # Initialize monitoring components
        self.monitoring_active = False
        self.alert_thresholds = {
            "cpu_percent": 85.0,
            "memory_percent": 90.0,
            "disk_percent": 95.0,
            "process_count": 300,
            "response_time_ms": 5000,
        }

        # Critical EQ12 processes to monitor
        self.critical_processes = [
            "python.exe",
            "powershell.exe",
            "httpd.exe",
            "mysqld.exe",
            "node.exe",
            "ngrok.exe",
        ]

        # Critical services to monitor
        self.critical_services = [
            "http://localhost:3000/health",
            "http://localhost:8000/health",
            "http://localhost:8080/health",
            "http://localhost:4040/api/tunnels",
        ]

    async def start_monitoring(self, interval_seconds: int = 60) -> None:
        """Start comprehensive resource monitoring."""
        self.logger.info(" Starting EQ12 Resource Monitor")
        self.monitoring_active = True

        # Initialize database
        await self._initialize_monitoring_db()

        # Start monitoring loop
        while self.monitoring_active:
            try:
                monitoring_data = await self._collect_comprehensive_metrics()
                await self._process_monitoring_data(monitoring_data)
                await self._check_alert_conditions(monitoring_data)

                # Save metrics to database
                await self._save_metrics_to_db(monitoring_data)

                self.logger.info(
                    f" Monitoring cycle completed - {monitoring_data['overall_health_score']}% health"
                )

                # Wait for next cycle
                await asyncio.sleep(interval_seconds)

            except Exception as e:
                self.logger.error(f" Monitoring cycle failed: {e}")
                await asyncio.sleep(30)  # Shorter retry interval on error

    async def _collect_comprehensive_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics."""
        timestamp = datetime.now(timezone.utc)

        # System resource metrics
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": dict(psutil.virtual_memory()._asdict()),
            "disk": dict(psutil.disk_usage(str(self.workspace_path))._asdict()),
            "network": dict(psutil.net_io_counters()._asdict()),
            "boot_time": psutil.boot_time(),
        }

        # Process monitoring
        process_metrics = await self._monitor_critical_processes()

        # Service health checks
        service_metrics = await self._check_service_health()

        # Database performance
        db_metrics = await self._check_database_performance()

        # EQ12-specific metrics
        eq12_metrics = await self._check_eq12_specific_health()

        # Calculate overall health score
        health_score = self._calculate_health_score(
            system_metrics, process_metrics, service_metrics, db_metrics, eq12_metrics
        )

        return {
            "timestamp": timestamp.isoformat(),
            "system": system_metrics,
            "processes": process_metrics,
            "services": service_metrics,
            "databases": db_metrics,
            "eq12_specific": eq12_metrics,
            "overall_health_score": health_score,
            "alerts": [],
        }

    async def _process_monitoring_data(self, monitoring_data: Dict[str, Any]) -> None:
        """Process and enrich monitoring data with additional analysis."""
        try:
            # Log current status
            health_score = monitoring_data["overall_health_score"]
            self.logger.debug(f" Processing monitoring data - Health: {health_score:.1f}%")

            # Add performance trends if we have historical data
            monitoring_data["trends"] = await self._calculate_performance_trends()

            # Add resource predictions
            monitoring_data["predictions"] = self._predict_resource_usage(monitoring_data)

            # Create performance snapshot
            snapshot = {
                "timestamp": monitoring_data["timestamp"],
                "health_score": health_score,
                "cpu_percent": monitoring_data["system"]["cpu_percent"],
                "memory_percent": monitoring_data["system"]["memory"]["percent"],
                "active_processes": len(monitoring_data["processes"]),
                "alert_count": len(monitoring_data["alerts"]),
            }

            # Save snapshot to performance history
            await self._save_performance_snapshot(snapshot)

        except Exception as e:
            self.logger.warning(f" Error processing monitoring data: {e}")

    async def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate performance trends from historical data."""
        try:
            db_path = self.data_path / "resource_monitoring.db"
            if not db_path.exists():
                return {"trend": "no_data", "change_rate": 0}

            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT health_score, timestamp 
                    FROM monitoring_metrics 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                """
                )
                recent_scores = cursor.fetchall()

            if len(recent_scores) < 2:
                return {"trend": "insufficient_data", "change_rate": 0}

            # Calculate trend
            scores = [score[0] for score in recent_scores]
            avg_recent = sum(scores[:3]) / 3 if len(scores) >= 3 else scores[0]
            avg_older = sum(scores[3:]) / len(scores[3:]) if len(scores) > 3 else scores[-1]

            change_rate = avg_recent - avg_older

            if change_rate > 5:
                trend = "improving"
            elif change_rate < -5:
                trend = "declining"
            else:
                trend = "stable"

            return {
                "trend": trend,
                "change_rate": round(change_rate, 2),
                "data_points": len(recent_scores),
            }

        except Exception as e:
            self.logger.warning(f" Error calculating trends: {e}")
            return {"trend": "error", "change_rate": 0}

    def _predict_resource_usage(self, monitoring_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict future resource usage based on current trends."""
        try:
            current_cpu = monitoring_data["system"]["cpu_percent"]
            current_memory = monitoring_data["system"]["memory"]["percent"]

            # Simple prediction based on current usage
            predictions = {
                "cpu_1h": min(current_cpu * 1.1, 100),  # Assume 10% increase
                "memory_1h": min(current_memory * 1.05, 100),  # Assume 5% increase
                "risk_level": "low",
            }

            # Adjust risk level
            if current_cpu > 80 or current_memory > 85:
                predictions["risk_level"] = "high"
            elif current_cpu > 60 or current_memory > 70:
                predictions["risk_level"] = "medium"

            return predictions

        except Exception as e:
            self.logger.warning(f" Error predicting resource usage: {e}")
            return {"risk_level": "unknown"}

    async def _save_performance_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Save performance snapshot for trend analysis."""
        try:
            snapshot_file = (
                self.logs_path
                / f"performance_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(snapshot_file, "w") as f:
                json.dump(snapshot, f, indent=2)

        except Exception as e:
            self.logger.warning(f" Error saving performance snapshot: {e}")

    async def _monitor_critical_processes(self) -> Dict[str, Any]:
        """Monitor critical EQ12 processes."""
        processes = {}

        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "status"]):
            try:
                if proc.info["name"] in self.critical_processes:
                    proc_name = proc.info["name"]
                    if proc_name not in processes:
                        processes[proc_name] = []

                    processes[proc_name].append(
                        {
                            "pid": proc.info["pid"],
                            "cpu_percent": proc.info["cpu_percent"],
                            "memory_mb": proc.info["memory_info"].rss / 1024 / 1024,
                            "status": proc.info["status"],
                        }
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {
            "critical_processes": processes,
            "total_process_count": len(list(psutil.process_iter())),
            "python_processes": len(processes.get("python.exe", [])),
            "powershell_processes": len(processes.get("powershell.exe", [])),
        }

    async def _check_service_health(self) -> Dict[str, Any]:
        """Check health of critical services."""
        service_health = {}

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for service_url in self.critical_services:
                try:
                    start_time = time.time()
                    async with session.get(service_url) as response:
                        response_time = (time.time() - start_time) * 1000

                        service_health[service_url] = {
                            "status": "healthy" if response.status == 200 else "unhealthy",
                            "status_code": response.status,
                            "response_time_ms": response_time,
                            "content_length": (
                                len(await response.text()) if response.status == 200 else 0
                            ),
                        }

                except Exception as e:
                    service_health[service_url] = {
                        "status": "down",
                        "error": str(e),
                        "response_time_ms": 0,
                        "content_length": 0,
                    }

        return service_health

    async def _check_database_performance(self) -> Dict[str, Any]:
        """Check database performance metrics."""
        db_metrics = {}

        # Check SQLite databases
        db_files = [
            self.data_path / "eq12_enterprise.db",
            self.data_path / "eq12_control.db",
            self.data_path / "eq12_security.db",
        ]

        for db_file in db_files:
            if db_file.exists():
                try:
                    start_time = time.time()
                    with sqlite3.connect(str(db_file)) as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                        table_count = cursor.fetchone()[0]

                        # Get database size
                        db_size = db_file.stat().st_size / 1024 / 1024  # MB

                        query_time = (time.time() - start_time) * 1000

                        db_metrics[db_file.name] = {
                            "status": "healthy",
                            "size_mb": db_size,
                            "table_count": table_count,
                            "query_time_ms": query_time,
                        }

                except Exception as e:
                    db_metrics[db_file.name] = {
                        "status": "error",
                        "error": str(e),
                        "size_mb": 0,
                        "table_count": 0,
                        "query_time_ms": 0,
                    }

        return db_metrics

    async def _check_eq12_specific_health(self) -> Dict[str, Any]:
        """Check EQ12-specific health indicators."""
        eq12_health = {}

        # Check log file health
        recent_logs = list(self.logs_path.glob("*.log"))
        recent_logs.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        eq12_health["log_files"] = {
            "total_count": len(recent_logs),
            "recent_count": len(
                [log for log in recent_logs if (time.time() - log.stat().st_mtime) < 3600]
            ),  # Last hour
            "total_size_mb": sum(log.stat().st_size for log in recent_logs) / 1024 / 1024,
        }

        # Check script integrity
        scripts_path = self.workspace_path / "scripts"
        if scripts_path.exists():
            python_scripts = list(scripts_path.glob("*.py"))
            powershell_scripts = list(scripts_path.glob("*.ps1"))

            eq12_health["scripts"] = {
                "python_count": len(python_scripts),
                "powershell_count": len(powershell_scripts),
                "last_modified": max(
                    (script.stat().st_mtime for script in python_scripts + powershell_scripts),
                    default=0,
                ),
            }

        # Check configuration health
        config_path = self.workspace_path / "configs"
        if config_path.exists():
            config_files = list(config_path.glob("*.json"))
            eq12_health["configs"] = {
                "count": len(config_files),
                "total_size_kb": sum(cfg.stat().st_size for cfg in config_files) / 1024,
            }

        return eq12_health

    def _calculate_health_score(
        self, system: Dict, processes: Dict, services: Dict, databases: Dict, eq12: Dict
    ) -> float:
        """Calculate overall system health score (0-100)."""
        score = 100.0

        # System metrics impact (40% weight)
        if system["cpu_percent"] > self.alert_thresholds["cpu_percent"]:
            score -= 15
        if system["memory"]["percent"] > self.alert_thresholds["memory_percent"]:
            score -= 20
        if (system["disk"]["used"] / system["disk"]["total"] * 100) > self.alert_thresholds[
            "disk_percent"
        ]:
            score -= 15

        # Process health impact (20% weight)
        if processes["total_process_count"] > self.alert_thresholds["process_count"]:
            score -= 10
        if processes["python_processes"] == 0:
            score -= 10  # No Python processes running

        # Service health impact (25% weight)
        unhealthy_services = sum(1 for svc in services.values() if svc["status"] != "healthy")
        score -= unhealthy_services * 5

        # Database health impact (10% weight)
        unhealthy_dbs = sum(1 for db in databases.values() if db["status"] != "healthy")
        score -= unhealthy_dbs * 5

        # EQ12-specific health impact (5% weight)
        if eq12["log_files"]["recent_count"] == 0:
            score -= 5  # No recent log activity

        return max(0.0, min(100.0, score))

    async def _check_alert_conditions(self, monitoring_data: Dict[str, Any]) -> None:
        """Check for alert conditions and trigger auto-healing if needed."""
        alerts = []

        # CPU alerts
        cpu_percent = monitoring_data["system"]["cpu_percent"]
        if cpu_percent > self.alert_thresholds["cpu_percent"]:
            alerts.append(
                {
                    "level": "critical" if cpu_percent > 95 else "warning",
                    "component": "cpu",
                    "message": f"High CPU usage: {cpu_percent:.1f}%",
                    "auto_heal": True if cpu_percent > 95 else False,
                }
            )

        # Memory alerts
        memory_percent = monitoring_data["system"]["memory"]["percent"]
        if memory_percent > self.alert_thresholds["memory_percent"]:
            alerts.append(
                {
                    "level": "critical" if memory_percent > 95 else "warning",
                    "component": "memory",
                    "message": f"High memory usage: {memory_percent:.1f}%",
                    "auto_heal": True if memory_percent > 95 else False,
                }
            )

        # Service alerts
        for service_url, service_data in monitoring_data["services"].items():
            if service_data["status"] != "healthy":
                alerts.append(
                    {
                        "level": "critical",
                        "component": "service",
                        "message": f"Service down: {service_url}",
                        "auto_heal": True,
                    }
                )

        monitoring_data["alerts"] = alerts

        # Trigger auto-healing for critical alerts
        critical_alerts = [
            alert for alert in alerts if alert["level"] == "critical" and alert.get("auto_heal")
        ]
        if critical_alerts:
            await self._trigger_auto_healing(critical_alerts)

    async def _trigger_auto_healing(self, alerts: List[Dict]) -> None:
        """Trigger auto-healing mechanisms for critical issues."""
        self.logger.warning(f" Triggering auto-healing for {len(alerts)} critical alerts")

        try:
            # Call the self-healing orchestrator
            heal_script = self.workspace_path / "eq12_self_healing_orchestrator.py"
            if heal_script.exists():
                cmd = [
                    sys.executable,
                    str(heal_script),
                    "--emergency-mode",
                    "--workspace",
                    str(self.workspace_path),
                    "--alerts",
                    json.dumps(alerts),
                ]

                result = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )

                stdout, stderr = await result.communicate()

                if result.returncode == 0:
                    self.logger.info(" Auto-healing triggered successfully")
                else:
                    self.logger.error(f" Auto-healing failed: {stderr.decode()}")

            # Also trigger universal repair assistant
            repair_script = self.workspace_path / "scripts" / "eq12_universal_repair_assistant.py"
            if repair_script.exists():
                cmd = [
                    sys.executable,
                    str(repair_script),
                    "--action",
                    "emergency-repair",
                    "--workspace",
                    str(self.workspace_path),
                    "--verbose",
                ]

                await asyncio.create_subprocess_exec(*cmd)
                self.logger.info(" Universal repair assistant triggered")

        except Exception as e:
            self.logger.error(f" Failed to trigger auto-healing: {e}")

    async def _initialize_monitoring_db(self) -> None:
        """Initialize monitoring database."""
        db_path = self.data_path / "resource_monitoring.db"

        with sqlite3.connect(str(db_path)) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS monitoring_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    process_count INTEGER,
                    health_score REAL,
                    alerts_count INTEGER,
                    raw_data TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp ON monitoring_metrics(timestamp)
            """
            )

    async def _save_metrics_to_db(self, metrics: Dict[str, Any]) -> None:
        """Save metrics to database."""
        db_path = self.data_path / "resource_monitoring.db"

        with sqlite3.connect(str(db_path)) as conn:
            conn.execute(
                """
                INSERT INTO monitoring_metrics (
                    timestamp, cpu_percent, memory_percent, disk_percent,
                    process_count, health_score, alerts_count, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    metrics["timestamp"],
                    metrics["system"]["cpu_percent"],
                    metrics["system"]["memory"]["percent"],
                    (metrics["system"]["disk"]["used"] / metrics["system"]["disk"]["total"] * 100),
                    metrics["processes"]["total_process_count"],
                    metrics["overall_health_score"],
                    len(metrics["alerts"]),
                    json.dumps(metrics),
                ),
            )

    async def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report."""
        self.logger.info(" Generating comprehensive health report")

        # Collect current metrics
        current_metrics = await self._collect_comprehensive_metrics()

        # Get historical data
        db_path = self.data_path / "resource_monitoring.db"
        historical_data = []

        if db_path.exists():
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT timestamp, health_score, alerts_count
                    FROM monitoring_metrics
                    ORDER BY timestamp DESC
                    LIMIT 24
                """
                )
                historical_data = cursor.fetchall()

        # Generate report
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "current_health": current_metrics,
            "historical_trends": {
                "avg_health_score_24h": (
                    sum(row[1] for row in historical_data) / len(historical_data)
                    if historical_data
                    else 0
                ),
                "total_alerts_24h": sum(row[2] for row in historical_data),
                "data_points": len(historical_data),
            },
            "recommendations": self._generate_recommendations(current_metrics),
        }

        # Save report
        report_file = self.logs_path / f"health_report_{self.timestamp}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f" Health report saved: {report_file}")
        return report

    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on metrics."""
        recommendations = []

        if metrics["system"]["cpu_percent"] > 80:
            recommendations.append("Consider identifying and optimizing high-CPU processes")

        if metrics["system"]["memory"]["percent"] > 85:
            recommendations.append("Monitor memory usage and consider increasing available RAM")

        if len(metrics["alerts"]) > 0:
            recommendations.append("Address critical alerts to improve system stability")

        unhealthy_services = sum(
            1 for svc in metrics["services"].values() if svc["status"] != "healthy"
        )
        if unhealthy_services > 0:
            recommendations.append(f"Restart {unhealthy_services} unhealthy service(s)")

        if metrics["overall_health_score"] < 80:
            recommendations.append("Run comprehensive system diagnostics")

        return recommendations

    def stop_monitoring(self) -> None:
        """Stop monitoring gracefully."""
        self.logger.info(" Stopping resource monitoring")
        self.monitoring_active = False


async def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Resource Monitor Wrapper")
    parser.add_argument(
        "--action",
        choices=["monitor", "report", "status"],
        default="monitor",
        help="Action to perform",
    )
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    parser.add_argument("--interval", type=int, default=60, help="Monitoring interval in seconds")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    monitor = EQ12ResourceMonitorWrapper(args.workspace)

    try:
        if args.action == "monitor":
            await monitor.start_monitoring(args.interval)
        elif args.action == "report":
            report = await monitor.generate_health_report()
            print(f" Health Report Generated")
            print(f"Current Health Score: {report['current_health']['overall_health_score']:.1f}%")
            print(f"Active Alerts: {len(report['current_health']['alerts'])}")
        elif args.action == "status":
            metrics = await monitor._collect_comprehensive_metrics()
            print(f" EQ12 Resource Status")
            print(f"Health Score: {metrics['overall_health_score']:.1f}%")
            print(f"CPU: {metrics['system']['cpu_percent']:.1f}%")
            print(f"Memory: {metrics['system']['memory']['percent']:.1f}%")
            print(f"Alerts: {len(metrics['alerts'])}")

    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("\n Resource monitoring stopped")


if __name__ == "__main__":
    asyncio.run(main())
