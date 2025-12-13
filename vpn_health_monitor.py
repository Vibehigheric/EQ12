#!/usr/bin/env python3
"""
EQ12 VPN Health Monitor & Security Checker
Comprehensive monitoring system for VPN connectivity, security validation, and automated threat response.
Integrates with EQ12 betting system to ensure secure operations.
"""

import json
import logging
import platform
import sqlite3
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import requests

# Add project root to path
PROJECT_ROOT = Path("C:/EQ12")
sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(PROJECT_ROOT / "logs" / "vpn_health_monitor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("EQ12_VPN_Health")


@dataclass
class VpnHealthMetrics:
    """VPN health metrics data class"""

    timestamp: float
    is_connected: bool
    ip_address: str
    region: str
    latency_ms: float
    bandwidth_mbps: float
    dns_leak_detected: bool
    ip_leak_detected: bool
    security_score: int
    uptime_percent: float
    reconnect_count: int


@dataclass
class SecurityThreat:
    """Security threat detection data class"""

    threat_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    detected_at: float
    source_ip: str
    action_required: bool
    auto_remediation: bool


class VpnHealthMonitor:
    """
    Comprehensive VPN health monitoring and security validation system.
    Provides continuous monitoring, threat detection, and automated responses.
    """

    def __init__(self, config_path: str | None = None):
        self.project_root = PROJECT_ROOT
        self.config_path = config_path or self.project_root / "configs" / "vpn_health_config.json"
        self.db_path = self.project_root / "eq12_bets.db"

        # Load configuration
        self.config = self._load_config()

        # Monitoring state
        self.is_monitoring = False
        self.baseline_ip = None
        self.baseline_dns = []
        self.health_history = []
        self.threat_log = []

        # Performance tracking
        self.performance_metrics = {
            "latency_samples": [],
            "bandwidth_samples": [],
            "uptime_windows": [],
            "connection_events": [],
        }

        # Security validation
        self.security_checks = {
            "ip_leak": True,
            "dns_leak": True,
            "webrtc_leak": True,
            "timezone_leak": True,
            "fingerprint_protection": True,
        }

    def _load_config(self) -> dict:
        """Load VPN health monitoring configuration"""
        default_config = {
            "monitoring": {
                "check_interval_seconds": 30,
                "health_history_limit": 1000,
                "performance_window_minutes": 60,
                "alert_thresholds": {
                    "latency_warning_ms": 200,
                    "latency_critical_ms": 1000,
                    "bandwidth_warning_mbps": 5,
                    "uptime_warning_percent": 95,
                    "uptime_critical_percent": 90,
                },
            },
            "security": {
                "check_ip_leaks": True,
                "check_dns_leaks": True,
                "check_webrtc_leaks": True,
                "allowed_ip_ranges": [],
                "blocked_regions": ["CN", "RU", "KP"],
                "security_scan_interval": 300,  # 5 minutes
                "auto_remediation": True,
            },
            "notifications": {
                "telegram_alerts": False,
                "email_alerts": False,
                "webhook_url": None,
                "alert_cooldown_minutes": 15,
            },
            "remediation": {
                "auto_reconnect": True,
                "kill_switch_enabled": True,
                "max_reconnect_attempts": 3,
                "quarantine_suspicious_traffic": True,
            },
        }

        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    self._deep_update(default_config, loaded_config)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

        return default_config

    def _deep_update(self, base_dict, update_dict):
        """Deep update dictionary"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def _execute_sql(self, query: str, params: tuple = ()) -> list:
        """Execute SQL query with error handling"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                conn.commit()
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Database error: {e}")
            return []

    def _log_health_metric(self, metrics: VpnHealthMetrics):
        """Log health metrics to database"""
        query = """
        INSERT INTO vpn_health_metrics
        (timestamp, vpn_config, metric_type, metric_value, metric_unit, status, details)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        # Log multiple metrics
        metrics_data = [
            (
                metrics.timestamp,
                "eq12-betting",
                "LATENCY",
                metrics.latency_ms,
                "ms",
                self._assess_latency_status(metrics.latency_ms),
                json.dumps({"ip": metrics.ip_address}),
            ),
            (
                metrics.timestamp,
                "eq12-betting",
                "BANDWIDTH",
                metrics.bandwidth_mbps,
                "mbps",
                self._assess_bandwidth_status(metrics.bandwidth_mbps),
                json.dumps({"region": metrics.region}),
            ),
            (
                metrics.timestamp,
                "eq12-betting",
                "UPTIME",
                metrics.uptime_percent,
                "percent",
                self._assess_uptime_status(metrics.uptime_percent),
                json.dumps({"reconnects": metrics.reconnect_count}),
            ),
            (
                metrics.timestamp,
                "eq12-betting",
                "SECURITY",
                metrics.security_score,
                "score",
                self._assess_security_status(metrics.security_score),
                json.dumps(
                    {
                        "dns_leak": metrics.dns_leak_detected,
                        "ip_leak": metrics.ip_leak_detected,
                    }
                ),
            ),
        ]

        for metric_data in metrics_data:
            self._execute_sql(query, metric_data)

    def _assess_latency_status(self, latency_ms: float) -> str:
        """Assess latency status"""
        thresholds = self.config["monitoring"]["alert_thresholds"]
        if latency_ms > thresholds["latency_critical_ms"]:
            return "CRITICAL"
        if latency_ms > thresholds["latency_warning_ms"]:
            return "WARNING"
        return "GOOD"

    def _assess_bandwidth_status(self, bandwidth_mbps: float) -> str:
        """Assess bandwidth status"""
        threshold = self.config["monitoring"]["alert_thresholds"]["bandwidth_warning_mbps"]
        return "WARNING" if bandwidth_mbps < threshold else "GOOD"

    def _assess_uptime_status(self, uptime_percent: float) -> str:
        """Assess uptime status"""
        thresholds = self.config["monitoring"]["alert_thresholds"]
        if uptime_percent < thresholds["uptime_critical_percent"]:
            return "CRITICAL"
        if uptime_percent < thresholds["uptime_warning_percent"]:
            return "WARNING"
        return "GOOD"

    def _assess_security_status(self, security_score: int) -> str:
        """Assess security status"""
        if security_score < 60:
            return "CRITICAL"
        if security_score < 80:
            return "WARNING"
        return "GOOD"

    def check_ip_leak(self) -> tuple[bool, str]:
        """Check for IP leaks by comparing with baseline"""
        try:
            # Get current IP from multiple sources
            ip_services = [
                "https://ifconfig.me/ip",
                "https://ipinfo.io/ip",
                "https://api.ipify.org",
            ]

            current_ips = []
            for service in ip_services:
                try:
                    response = requests.get(service, timeout=10)
                    ip = response.text.strip()
                    if self._is_valid_ip(ip):
                        current_ips.append(ip)
                except:
                    continue

            if not current_ips:
                return True, "Unable to determine IP address"

            # Check if all IPs are the same (good)
            if len(set(current_ips)) == 1:
                current_ip = current_ips[0]

                # Check against baseline if available
                if self.baseline_ip and current_ip == self.baseline_ip:
                    return True, "IP leak detected - matches baseline IP"

                return False, current_ip
            return True, f"Inconsistent IP addresses detected: {current_ips}"

        except Exception as e:
            logger.error(f"IP leak check failed: {e}")
            return True, f"IP leak check error: {e!s}"

    def check_dns_leak(self) -> tuple[bool, list[str]]:
        """Check for DNS leaks"""
        try:
            # Query DNS servers using different methods
            dns_servers = []

            # Method 1: Use nslookup to check current DNS
            try:
                result = subprocess.run(
                    ["nslookup", "google.com"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                # Parse DNS server from output
                for line in result.stdout.split("\n"):
                    if "Server:" in line:
                        dns_ip = line.split(":")[-1].strip()
                        if self._is_valid_ip(dns_ip):
                            dns_servers.append(dns_ip)
            except:
                pass

            # Method 2: Check system DNS configuration
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(
                        [
                            "powershell",
                            "-Command",
                            "Get-DnsClientServerAddress | Select-Object -ExpandProperty ServerAddresses",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    for line in result.stdout.split("\n"):
                        ip = line.strip()
                        if self._is_valid_ip(ip):
                            dns_servers.append(ip)
            except:
                pass

            # Check if DNS servers are in expected ranges (VPN provider's DNS)
            if not dns_servers:
                return True, ["No DNS servers found"]

            # Check against known ISP DNS servers that indicate leaks
            isp_dns_servers = [
                "8.8.8.8",
                "8.8.4.4",  # Google
                "1.1.1.1",
                "1.0.0.1",  # Cloudflare
                "208.67.222.222",
                "208.67.220.220",  # OpenDNS
            ]

            leaked_dns = [dns for dns in dns_servers if dns in isp_dns_servers]
            if leaked_dns:
                return True, leaked_dns

            return False, dns_servers

        except Exception as e:
            logger.error(f"DNS leak check failed: {e}")
            return True, [f"DNS check error: {e!s}"]

    def measure_latency(self) -> float:
        """Measure VPN latency"""
        try:
            # Ping Google DNS
            start_time = time.time()

            if platform.system() == "Windows":
                result = subprocess.run(
                    ["ping", "-n", "3", "8.8.8.8"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )

                # Parse ping results
                latencies = []
                for line in result.stdout.split("\n"):
                    if "time=" in line.lower() or "time<" in line.lower():
                        try:
                            # Extract time value
                            time_part = line.split("time")[1].split("ms")[0]
                            if "<" in time_part:
                                latency = 1.0  # Sub-millisecond
                            else:
                                latency = float(time_part.replace("=", "").replace("<", "").strip())
                            latencies.append(latency)
                        except:
                            continue

                if latencies:
                    return statistics.mean(latencies)

            # Fallback: simple connection time
            end_time = time.time()
            return (end_time - start_time) * 1000  # Convert to ms

        except Exception as e:
            logger.error(f"Latency measurement failed: {e}")
            return 9999.0  # Return high latency on error

    def measure_bandwidth(self) -> float:
        """Estimate bandwidth (simplified test)"""
        try:
            # Download a small test file and measure speed
            test_url = "https://httpbin.org/bytes/1048576"  # 1MB
            start_time = time.time()

            response = requests.get(test_url, timeout=30, stream=True)
            total_size = 0

            for chunk in response.iter_content(chunk_size=8192):
                total_size += len(chunk)

            end_time = time.time()
            duration = end_time - start_time

            # Calculate Mbps
            mbps = (total_size * 8) / (duration * 1000000)
            return mbps

        except Exception as e:
            logger.error(f"Bandwidth measurement failed: {e}")
            return 0.0

    def calculate_uptime(self) -> float:
        """Calculate VPN uptime percentage"""
        try:
            # Look at connection events in last 24 hours
            query = """
            SELECT event_type, timestamp FROM vpn_logs
            WHERE timestamp > ? AND event_type IN ('VPN_CONNECTED', 'VPN_CONNECTION_LOST', 'VPN_DISCONNECTED')
            ORDER BY timestamp
            """

            yesterday = time.time() - 86400  # 24 hours ago
            events = self._execute_sql(query, (yesterday,))

            if not events:
                return 100.0  # Assume 100% if no data

            # Calculate connected time
            connected_time = 0
            last_connect_time = None

            for event in events:
                if event["event_type"] == "VPN_CONNECTED":
                    last_connect_time = event["timestamp"]
                elif (
                    event["event_type"] in ["VPN_CONNECTION_LOST", "VPN_DISCONNECTED"]
                    and last_connect_time
                ):
                    connected_time += event["timestamp"] - last_connect_time
                    last_connect_time = None

            # If still connected, add time until now
            if last_connect_time:
                connected_time += time.time() - last_connect_time

            # Calculate percentage
            total_time = 86400  # 24 hours in seconds
            uptime_percent = (connected_time / total_time) * 100
            return min(uptime_percent, 100.0)

        except Exception as e:
            logger.error(f"Uptime calculation failed: {e}")
            return 0.0

    def calculate_security_score(self, ip_leak: bool, dns_leak: bool) -> int:
        """Calculate overall security score (0-100)"""
        score = 100

        # Deduct points for security issues
        if ip_leak:
            score -= 40  # Major security issue

        if dns_leak:
            score -= 30  # Significant privacy issue

        # Check other security factors
        try:
            # Check if using HTTPS
            response = requests.get("https://httpbin.org/ip", timeout=10)
            if response.status_code != 200:
                score -= 10
        except:
            score -= 15

        # Check WebRTC (simplified)
        # In a real implementation, you'd use browser automation

        return max(score, 0)

    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IP address format"""
        try:
            parts = ip.split(".")
            return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
        except:
            return False

    def collect_health_metrics(self) -> VpnHealthMetrics:
        """Collect comprehensive health metrics"""
        logger.debug("Collecting VPN health metrics...")

        # Basic connectivity
        ip_leak, current_ip = self.check_ip_leak()
        dns_leak, _dns_servers = self.check_dns_leak()

        # Performance metrics
        latency = self.measure_latency()
        bandwidth = self.measure_bandwidth()
        uptime = self.calculate_uptime()

        # Security assessment
        security_score = self.calculate_security_score(ip_leak, dns_leak)

        # Get region info
        region = "Unknown"
        if current_ip and current_ip != "Unknown":
            try:
                response = requests.get(f"http://ipinfo.io/{current_ip}/json", timeout=10)
                data = response.json()
                region = (
                    f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country', '')}"
                )
            except:
                pass

        # Get reconnect count from recent logs
        reconnect_query = """
        SELECT COUNT(*) as count FROM vpn_logs
        WHERE timestamp > ? AND event_type = 'VPN_RECONNECTED'
        """
        yesterday = time.time() - 86400
        reconnect_result = self._execute_sql(reconnect_query, (yesterday,))
        reconnect_count = reconnect_result[0]["count"] if reconnect_result else 0

        metrics = VpnHealthMetrics(
            timestamp=time.time(),
            is_connected=not ip_leak,
            ip_address=current_ip if current_ip != "Unknown" else "",
            region=region,
            latency_ms=latency,
            bandwidth_mbps=bandwidth,
            dns_leak_detected=dns_leak,
            ip_leak_detected=ip_leak,
            security_score=security_score,
            uptime_percent=uptime,
            reconnect_count=reconnect_count,
        )

        return metrics

    def detect_security_threats(self, metrics: VpnHealthMetrics) -> list[SecurityThreat]:
        """Detect security threats based on metrics"""
        threats = []

        # IP leak detection
        if metrics.ip_leak_detected:
            threats.append(
                SecurityThreat(
                    threat_type="IP_LEAK",
                    severity="CRITICAL",
                    description="IP address leak detected - real IP exposed",
                    detected_at=metrics.timestamp,
                    source_ip=metrics.ip_address,
                    action_required=True,
                    auto_remediation=True,
                )
            )

        # DNS leak detection
        if metrics.dns_leak_detected:
            threats.append(
                SecurityThreat(
                    threat_type="DNS_LEAK",
                    severity="HIGH",
                    description="DNS leak detected - queries may expose browsing history",
                    detected_at=metrics.timestamp,
                    source_ip=metrics.ip_address,
                    action_required=True,
                    auto_remediation=True,
                )
            )

        # Performance-based threats
        if metrics.latency_ms > 2000:  # Very high latency
            threats.append(
                SecurityThreat(
                    threat_type="PERFORMANCE_DEGRADATION",
                    severity="MEDIUM",
                    description=f"Extremely high latency: {metrics.latency_ms}ms - possible MITM attack",
                    detected_at=metrics.timestamp,
                    source_ip=metrics.ip_address,
                    action_required=False,
                    auto_remediation=False,
                )
            )

        # Security score threats
        if metrics.security_score < 50:
            threats.append(
                SecurityThreat(
                    threat_type="LOW_SECURITY_SCORE",
                    severity="HIGH",
                    description=f"Security score critically low: {metrics.security_score}/100",
                    detected_at=metrics.timestamp,
                    source_ip=metrics.ip_address,
                    action_required=True,
                    auto_remediation=True,
                )
            )

        return threats

    def handle_security_threats(self, threats: list[SecurityThreat]):
        """Handle detected security threats with automated remediation"""
        for threat in threats:
            logger.warning(f"Security threat detected: {threat.threat_type} - {threat.description}")

            # Log threat to database
            self._log_security_threat(threat)

            # Auto-remediation
            if threat.auto_remediation and self.config["remediation"]["auto_reconnect"]:
                if threat.threat_type in ["IP_LEAK", "DNS_LEAK"]:
                    logger.info("Initiating automatic VPN reconnection due to security threat")
                    self._trigger_vpn_reconnection()

                if (
                    threat.threat_type == "LOW_SECURITY_SCORE"
                    and self.config["remediation"]["kill_switch_enabled"]
                ):
                    logger.warning("Activating kill switch due to low security score")
                    self._activate_kill_switch()

    def _log_security_threat(self, threat: SecurityThreat):
        """Log security threat to database"""
        query = """
        INSERT INTO vpn_security_events
        (timestamp, event_type, severity, source_ip, description, action_taken)
        VALUES (?, ?, ?, ?, ?, ?)
        """

        action_taken = "AUTO_REMEDIATION" if threat.auto_remediation else "LOGGED_ONLY"

        self._execute_sql(
            query,
            (
                threat.detected_at,
                threat.threat_type,
                threat.severity,
                threat.source_ip,
                threat.description,
                action_taken,
            ),
        )

    def _trigger_vpn_reconnection(self):
        """Trigger VPN reconnection via PowerShell script"""
        try:
            subprocess.Popen(
                [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    "Restart-Service WireGuardTunnel$eq12-betting",
                ]
            )
            logger.info("VPN reconnection triggered")
        except Exception as e:
            logger.error(f"Failed to trigger VPN reconnection: {e}")

    def _activate_kill_switch(self):
        """Activate network kill switch"""
        try:
            # Stop all betting processes
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-Process | Where-Object {$_.ProcessName -like '*python*' -and $_.CommandLine -like '*eq12*'} | Stop-Process -Force",
                ]
            )
            logger.info("Kill switch activated - betting processes stopped")
        except Exception as e:
            logger.error(f"Failed to activate kill switch: {e}")

    def start_monitoring(self):
        """Start continuous VPN health monitoring"""
        logger.info("Starting VPN health monitoring...")
        self.is_monitoring = True

        while self.is_monitoring:
            try:
                # Collect health metrics
                metrics = self.collect_health_metrics()

                # Store metrics
                self._log_health_metric(metrics)
                self.health_history.append(metrics)

                # Limit history size
                max_history = self.config["monitoring"]["health_history_limit"]
                if len(self.health_history) > max_history:
                    self.health_history = self.health_history[-max_history:]

                # Detect threats
                threats = self.detect_security_threats(metrics)
                if threats:
                    self.handle_security_threats(threats)
                    self.threat_log.extend(threats)

                # Log status
                logger.info(
                    f"Health check: IP={metrics.ip_address}, Latency={metrics.latency_ms}ms, "
                    f"Security={metrics.security_score}/100, Uptime={metrics.uptime_percent:.1f}%"
                )

                # Wait for next check
                time.sleep(self.config["monitoring"]["check_interval_seconds"])

            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(30)  # Back off on errors

    def stop_monitoring(self):
        """Stop health monitoring"""
        logger.info("Stopping VPN health monitoring...")
        self.is_monitoring = False

    def get_health_report(self) -> dict:
        """Generate comprehensive health report"""
        if not self.health_history:
            return {"status": "No health data available"}

        recent_metrics = self.health_history[-10:]  # Last 10 checks

        # Calculate averages
        avg_latency = statistics.mean([m.latency_ms for m in recent_metrics])
        avg_bandwidth = statistics.mean([m.bandwidth_mbps for m in recent_metrics])
        avg_security = statistics.mean([m.security_score for m in recent_metrics])
        avg_uptime = statistics.mean([m.uptime_percent for m in recent_metrics])

        # Count recent issues
        recent_threats = [
            t for t in self.threat_log if time.time() - t.detected_at < 3600
        ]  # Last hour

        return {
            "timestamp": datetime.now().isoformat(),
            "status": ("HEALTHY" if avg_security > 80 and avg_uptime > 95 else "ISSUES_DETECTED"),
            "metrics": {
                "average_latency_ms": round(avg_latency, 2),
                "average_bandwidth_mbps": round(avg_bandwidth, 2),
                "average_security_score": round(avg_security, 1),
                "average_uptime_percent": round(avg_uptime, 1),
            },
            "recent_threats": len(recent_threats),
            "threat_types": list({t.threat_type for t in recent_threats}),
            "monitoring_duration_hours": (
                round((time.time() - self.health_history[0].timestamp) / 3600, 1)
                if self.health_history
                else 0
            ),
            "total_checks": len(self.health_history),
        }


def main():
    """Main entry point"""
    monitor = VpnHealthMonitor()

    try:
        # Start monitoring
        monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        monitor.stop_monitoring()

        # Generate final report
        report = monitor.get_health_report()
        logger.info(f"Final health report: {json.dumps(report, indent=2)}")


if __name__ == "__main__":
    main()
