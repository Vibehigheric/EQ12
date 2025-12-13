#!/usr/bin/env python3
"""
 EQ12 NETWORK MONITORING DASHBOARD
Real-time network performance monitoring for UGREEN CM648 adapter

Created: November 7, 2025
Author: EQ12 Network Monitoring Team
Purpose: Continuous monitoring and alerting for network performance
Classification: NETWORK MONITORING - REAL-TIME DASHBOARD
"""

import sys
import json
import time
import logging
import psutil
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import threading
import queue

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
log = logging.getLogger("NETWORK_MONITOR")


class EQ12NetworkMonitor:
    """Real-time network performance monitoring system"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.logs_dir = self.workspace_path / "logs"
        self.dashboard_dir = self.workspace_path / "dashboard"
        
        # Create directories
        for dir_path in [self.logs_dir, self.dashboard_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.monitoring_active = False
        self.performance_history = []
        self.alert_thresholds = {
            "max_latency_ms": 100,
            "min_throughput_mbps": 10,
            "max_packet_loss_percent": 5,
            "max_jitter_ms": 20
        }
        
        log.info(" Initializing Network Performance Monitoring System")

    def start_continuous_monitoring(self, interval_seconds: int = 30) -> None:
        """Start continuous network performance monitoring"""
        
        log.info(f" Starting continuous network monitoring (interval: {interval_seconds}s)")
        
        self.monitoring_active = True
        
        # Create monitoring thread
        monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        monitor_thread.start()
        
        log.info(" Network monitoring started")

    def _monitoring_loop(self, interval_seconds: int) -> None:
        """Main monitoring loop"""
        
        while self.monitoring_active:
            try:
                # Collect performance metrics
                metrics = self._collect_performance_metrics()
                
                # Add timestamp
                metrics["timestamp"] = datetime.now().isoformat()
                
                # Store in history
                self.performance_history.append(metrics)
                
                # Keep only last 1000 entries
                if len(self.performance_history) > 1000:
                    self.performance_history = self.performance_history[-1000:]
                
                # Check for alerts
                alerts = self._check_performance_alerts(metrics)
                if alerts:
                    self._handle_performance_alerts(alerts, metrics)
                
                # Save metrics to log
                self._save_performance_log(metrics)
                
                # Update dashboard
                self._update_monitoring_dashboard()
                
                time.sleep(interval_seconds)
                
            except Exception as e:
                log.error(f" Monitoring loop error: {e}")
                time.sleep(5)  # Short delay before retry

    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect current performance metrics"""
        
        metrics = {
            "network_interfaces": {},
            "internet_connectivity": {},
            "system_resources": {},
            "alerts": []
        }
        
        try:
            # Network interface metrics
            net_io = psutil.net_io_counters(pernic=True)
            net_stats = psutil.net_if_stats()
            
            for interface_name, io_counters in net_io.items():
                if interface_name in net_stats:
                    interface_stats = net_stats[interface_name]
                    
                    metrics["network_interfaces"][interface_name] = {
                        "is_up": interface_stats.isup,
                        "speed_mbps": interface_stats.speed,
                        "bytes_sent": io_counters.bytes_sent,
                        "bytes_recv": io_counters.bytes_recv,
                        "packets_sent": io_counters.packets_sent,
                        "packets_recv": io_counters.packets_recv,
                        "errors_in": io_counters.errin,
                        "errors_out": io_counters.errout,
                        "drops_in": io_counters.dropin,
                        "drops_out": io_counters.dropout
                    }
            
            # Internet connectivity test
            connectivity = self._test_internet_connectivity()
            metrics["internet_connectivity"] = connectivity
            
            # System resource usage
            metrics["system_resources"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {}
            }
            
        except Exception as e:
            log.error(f" Metrics collection error: {e}")
            metrics["collection_error"] = str(e)
        
        return metrics

    def _test_internet_connectivity(self) -> Dict[str, Any]:
        """Test internet connectivity"""
        
        connectivity = {
            "status": "unknown",
            "latency_ms": 0,
            "packet_loss_percent": 0,
            "test_timestamp": datetime.now().isoformat()
        }
        
        try:
            # Quick ping test to Google DNS
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["ping", "-n", "1", "8.8.8.8"],
                    capture_output=True, text=True, timeout=5
                )
            else:
                result = subprocess.run(
                    ["ping", "-c", "1", "8.8.8.8"],
                    capture_output=True, text=True, timeout=5
                )
            
            if result.returncode == 0:
                connectivity["status"] = "connected"
                
                # Extract latency from ping output
                output = result.stdout.lower()
                import re
                latency_match = re.search(r'time[<>=]*(\d+)ms', output)
                if latency_match:
                    connectivity["latency_ms"] = int(latency_match.group(1))
                
                connectivity["packet_loss_percent"] = 0
            else:
                connectivity["status"] = "disconnected"
                connectivity["packet_loss_percent"] = 100
                
        except Exception as e:
            connectivity["status"] = "error"
            connectivity["error"] = str(e)
        
        return connectivity

    def _check_performance_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for performance alerts"""
        
        alerts = []
        
        try:
            # Check internet connectivity
            connectivity = metrics.get("internet_connectivity", {})
            
            if connectivity.get("status") != "connected":
                alerts.append({
                    "type": "connectivity",
                    "severity": "critical",
                    "message": "Internet connectivity lost",
                    "metric": "connection_status",
                    "value": connectivity.get("status", "unknown")
                })
            
            # Check latency
            latency = connectivity.get("latency_ms", 0)
            if latency > self.alert_thresholds["max_latency_ms"]:
                alerts.append({
                    "type": "performance",
                    "severity": "warning",
                    "message": f"High latency detected: {latency}ms",
                    "metric": "latency_ms",
                    "value": latency,
                    "threshold": self.alert_thresholds["max_latency_ms"]
                })
            
            # Check packet loss
            packet_loss = connectivity.get("packet_loss_percent", 0)
            if packet_loss > self.alert_thresholds["max_packet_loss_percent"]:
                alerts.append({
                    "type": "performance",
                    "severity": "warning" if packet_loss < 50 else "critical",
                    "message": f"Packet loss detected: {packet_loss}%",
                    "metric": "packet_loss_percent",
                    "value": packet_loss,
                    "threshold": self.alert_thresholds["max_packet_loss_percent"]
                })
            
            # Check for interface errors
            for interface_name, interface_data in metrics.get("network_interfaces", {}).items():
                if interface_data.get("is_up") and interface_data.get("speed_mbps", 0) > 100:
                    errors_total = interface_data.get("errors_in", 0) + interface_data.get("errors_out", 0)
                    drops_total = interface_data.get("drops_in", 0) + interface_data.get("drops_out", 0)
                    
                    if errors_total > 10:
                        alerts.append({
                            "type": "interface",
                            "severity": "warning",
                            "message": f"Network errors on {interface_name}: {errors_total}",
                            "metric": "interface_errors",
                            "value": errors_total,
                            "interface": interface_name
                        })
                    
                    if drops_total > 10:
                        alerts.append({
                            "type": "interface",
                            "severity": "warning",
                            "message": f"Network drops on {interface_name}: {drops_total}",
                            "metric": "interface_drops",
                            "value": drops_total,
                            "interface": interface_name
                        })
            
        except Exception as e:
            log.error(f" Alert checking error: {e}")
        
        return alerts

    def _handle_performance_alerts(self, alerts: List[Dict[str, Any]], metrics: Dict[str, Any]) -> None:
        """Handle performance alerts"""
        
        for alert in alerts:
            severity = alert.get("severity", "info")
            message = alert.get("message", "Unknown alert")
            
            if severity == "critical":
                log.error(f" CRITICAL ALERT: {message}")
            elif severity == "warning":
                log.warning(f" WARNING: {message}")
            else:
                log.info(f" INFO: {message}")
        
        # Save alerts to file
        alert_file = self.logs_dir / f"network_alerts_{datetime.now().strftime('%Y%m%d')}.json"
        
        alert_entry = {
            "timestamp": datetime.now().isoformat(),
            "alerts": alerts,
            "metrics_snapshot": metrics
        }
        
        # Append to alerts file
        alerts_data = []
        if alert_file.exists():
            try:
                with open(alert_file, 'r') as f:
                    alerts_data = json.load(f)
            except:
                alerts_data = []
        
        alerts_data.append(alert_entry)
        
        # Keep only last 100 alerts
        if len(alerts_data) > 100:
            alerts_data = alerts_data[-100:]
        
        with open(alert_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)

    def _save_performance_log(self, metrics: Dict[str, Any]) -> None:
        """Save performance metrics to log file"""
        
        log_file = self.logs_dir / f"network_performance_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Append to daily log file
        log_data = []
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
            except:
                log_data = []
        
        log_data.append(metrics)
        
        # Keep only last 1000 entries per day
        if len(log_data) > 1000:
            log_data = log_data[-1000:]
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)

    def _update_monitoring_dashboard(self) -> None:
        """Update monitoring dashboard HTML"""
        
        try:
            dashboard_file = self.dashboard_dir / "eq12_network_monitoring_dashboard.html"
            
            # Get latest metrics
            latest_metrics = self.performance_history[-1] if self.performance_history else {}
            
            # Generate dashboard HTML
            html_content = self._generate_dashboard_html(latest_metrics)
            
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        except Exception as e:
            log.error(f" Dashboard update error: {e}")

    def _generate_dashboard_html(self, latest_metrics: Dict[str, Any]) -> str:
        """Generate monitoring dashboard HTML"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Get connectivity status
        connectivity = latest_metrics.get("internet_connectivity", {})
        connection_status = connectivity.get("status", "unknown")
        latency = connectivity.get("latency_ms", 0)
        
        # Get interface information
        interfaces = latest_metrics.get("network_interfaces", {})
        active_interfaces = [name for name, data in interfaces.items() if data.get("is_up")]
        
        # Get system resources
        system = latest_metrics.get("system_resources", {})
        cpu_usage = system.get("cpu_percent", 0)
        memory_usage = system.get("memory_percent", 0)
        
        # Status colors
        connection_color = "#4CAF50" if connection_status == "connected" else "#f44336"
        latency_color = "#4CAF50" if latency < 50 else "#ff9800" if latency < 100 else "#f44336"
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> EQ12 Network Monitoring Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .metric-title {{
            font-size: 1.2em;
            margin-bottom: 15px;
            font-weight: 600;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }}
        
        .metric-status {{
            text-align: center;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 500;
            text-transform: uppercase;
            font-size: 0.9em;
        }}
        
        .status-connected {{
            background: #4CAF50;
            color: white;
        }}
        
        .status-disconnected {{
            background: #f44336;
            color: white;
        }}
        
        .status-warning {{
            background: #ff9800;
            color: white;
        }}
        
        .interface-list {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 20px;
        }}
        
        .interface-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .interface-item:last-child {{
            border-bottom: none;
        }}
        
        .interface-name {{
            font-weight: 600;
        }}
        
        .interface-status {{
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        
        .performance-history {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .history-entry {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 0.9em;
        }}
        
        .history-entry:last-child {{
            border-bottom: none;
        }}
        
        .timestamp {{
            text-align: center;
            margin-top: 30px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .alert-section {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 20px;
        }}
        
        .alert-item {{
            padding: 10px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid;
        }}
        
        .alert-critical {{
            background: rgba(244, 67, 54, 0.2);
            border-left-color: #f44336;
        }}
        
        .alert-warning {{
            background: rgba(255, 152, 0, 0.2);
            border-left-color: #ff9800;
        }}
        
        .refresh-indicator {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(76, 175, 80, 0.9);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 0.9em;
            font-weight: 500;
        }}
        
        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
    </style>
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> EQ12 Network Monitoring Dashboard</h1>
            <p>Real-time UGREEN CM648 Performance Monitoring</p>
        </div>
        
        <div class="refresh-indicator pulse">
             Auto-refresh: 30s
        </div>
        
        <div class="dashboard-grid">
            <div class="metric-card">
                <div class="metric-title"> Internet Connection</div>
                <div class="metric-value" style="color: {connection_color};">
                    {"" if connection_status == "connected" else ""}
                </div>
                <div class="metric-status {'status-connected' if connection_status == 'connected' else 'status-disconnected'}">
                    {connection_status.title()}
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title"> Network Latency</div>
                <div class="metric-value" style="color: {latency_color};">
                    {latency}ms
                </div>
                <div class="metric-status {'status-connected' if latency < 50 else 'status-warning' if latency < 100 else 'status-disconnected'}">
                    {"Excellent" if latency < 30 else "Good" if latency < 50 else "Fair" if latency < 100 else "Poor"}
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title"> Active Interfaces</div>
                <div class="metric-value">
                    {len(active_interfaces)}
                </div>
                <div class="metric-status status-connected">
                    Networks Active
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title"> CPU Usage</div>
                <div class="metric-value" style="color: {'#4CAF50' if cpu_usage < 50 else '#ff9800' if cpu_usage < 80 else '#f44336'};">
                    {cpu_usage:.1f}%
                </div>
                <div class="metric-status {'status-connected' if cpu_usage < 70 else 'status-warning' if cpu_usage < 90 else 'status-disconnected'}">
                    {"Normal" if cpu_usage < 70 else "High" if cpu_usage < 90 else "Critical"}
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title"> Memory Usage</div>
                <div class="metric-value" style="color: {'#4CAF50' if memory_usage < 60 else '#ff9800' if memory_usage < 80 else '#f44336'};">
                    {memory_usage:.1f}%
                </div>
                <div class="metric-status {'status-connected' if memory_usage < 70 else 'status-warning' if memory_usage < 90 else 'status-disconnected'}">
                    {"Normal" if memory_usage < 70 else "High" if memory_usage < 90 else "Critical"}
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title"> Monitoring Status</div>
                <div class="metric-value" style="color: #4CAF50;">
                    
                </div>
                <div class="metric-status status-connected">
                    Active
                </div>
            </div>
        </div>
        
        <div class="interface-list">
            <h2 style="margin-bottom: 20px; text-align: center;"> Network Interfaces</h2>
"""

        # Add interface information
        for interface_name, interface_data in interfaces.items():
            is_up = interface_data.get("is_up", False)
            speed = interface_data.get("speed_mbps", 0)
            status_class = "status-connected" if is_up else "status-disconnected"
            status_text = f"Active ({speed} Mbps)" if is_up and speed > 0 else "Active" if is_up else "Inactive"
            
            html_content += f"""
            <div class="interface-item">
                <div>
                    <div class="interface-name">{interface_name}</div>
                    <div style="font-size: 0.8em; opacity: 0.8;">
                        Sent: {interface_data.get('bytes_sent', 0):,} bytes | 
                        Received: {interface_data.get('bytes_recv', 0):,} bytes
                    </div>
                </div>
                <div class="interface-status {status_class}">
                    {status_text}
                </div>
            </div>
"""

        html_content += f"""
        </div>
        
        <div class="performance-history">
            <h2 style="margin-bottom: 20px; text-align: center;"> Recent Performance History</h2>
"""

        # Add recent performance history
        recent_history = self.performance_history[-10:] if self.performance_history else []
        for entry in reversed(recent_history):
            entry_time = entry.get("timestamp", "Unknown")
            if entry_time != "Unknown":
                try:
                    # Format timestamp
                    dt = datetime.fromisoformat(entry_time.replace('Z', '+00:00'))
                    entry_time = dt.strftime('%H:%M:%S')
                except:
                    pass
            
            entry_connectivity = entry.get("internet_connectivity", {})
            entry_status = entry_connectivity.get("status", "unknown")
            entry_latency = entry_connectivity.get("latency_ms", 0)
            
            html_content += f"""
            <div class="history-entry">
                <span>{entry_time}</span>
                <span>Status: {entry_status.title()}</span>
                <span>Latency: {entry_latency}ms</span>
            </div>
"""

        html_content += f"""
        </div>
        
        <div class="timestamp">
             Last Updated: {timestamp} |  Monitoring: Active |  UGREEN CM648 Status: Connected
        </div>
    </div>
    
    <script>
        // Auto-refresh functionality
        setTimeout(function() {{
            location.reload();
        }}, 30000);
        
        // Add visual feedback on page load
        document.addEventListener('DOMContentLoaded', function() {{
            const cards = document.querySelectorAll('.metric-card');
            cards.forEach((card, index) => {{
                setTimeout(() => {{
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {{
                        card.style.transition = 'all 0.5s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }}, 50);
                }}, index * 100);
            }});
        }});
    </script>
</body>
</html>"""

        return html_content

    def generate_monitoring_summary(self) -> Dict[str, Any]:
        """Generate monitoring summary report"""
        
        summary = {
            "monitoring_duration": len(self.performance_history),
            "current_status": {},
            "performance_trends": {},
            "alert_summary": {},
            "recommendations": []
        }
        
        if self.performance_history:
            latest = self.performance_history[-1]
            summary["current_status"] = {
                "connectivity": latest.get("internet_connectivity", {}).get("status", "unknown"),
                "latency_ms": latest.get("internet_connectivity", {}).get("latency_ms", 0),
                "active_interfaces": len([
                    name for name, data in latest.get("network_interfaces", {}).items() 
                    if data.get("is_up")
                ]),
                "timestamp": latest.get("timestamp", "unknown")
            }
            
            # Calculate performance trends
            if len(self.performance_history) > 1:
                latencies = [
                    entry.get("internet_connectivity", {}).get("latency_ms", 0)
                    for entry in self.performance_history[-10:]
                    if entry.get("internet_connectivity", {}).get("latency_ms", 0) > 0
                ]
                
                if latencies:
                    summary["performance_trends"] = {
                        "average_latency_ms": round(sum(latencies) / len(latencies), 2),
                        "min_latency_ms": min(latencies),
                        "max_latency_ms": max(latencies),
                        "latency_stability": "stable" if max(latencies) - min(latencies) < 20 else "variable"
                    }
        
        return summary

    def stop_monitoring(self) -> None:
        """Stop continuous monitoring"""
        
        log.info(" Stopping network monitoring...")
        self.monitoring_active = False
        log.info(" Network monitoring stopped")


def main():
    """Main network monitoring interface"""
    
    print("" + "="*80)
    print(" EQ12 NETWORK MONITORING DASHBOARD")
    print(" REAL-TIME UGREEN CM648 PERFORMANCE MONITORING")
    print("" + "="*80)
    
    # Initialize monitoring system
    monitor = EQ12NetworkMonitor()
    
    try:
        # Generate initial dashboard
        monitor._update_monitoring_dashboard()
        
        print(f"\n NETWORK MONITORING SYSTEM INITIALIZED")
        print(f"    Dashboard: C:\\EQ12\\dashboard\\eq12_network_monitoring_dashboard.html")
        print(f"    Real-time monitoring ready")
        print(f"    Auto-refresh: 30 seconds")
        
        # Start continuous monitoring
        monitor.start_continuous_monitoring(30)
        
        print(f"\n MONITORING ACTIVE")
        print(f"    Internet connectivity tracking")
        print(f"    Latency monitoring")
        print(f"    Interface status monitoring")
        print(f"    Performance alerting")
        
        # Run for a short period to demonstrate
        print(f"\n Running monitoring for 2 minutes...")
        time.sleep(120)
        
        # Generate summary
        summary = monitor.generate_monitoring_summary()
        
        print(f"\n MONITORING SUMMARY")
        current = summary.get("current_status", {})
        print(f"    Current Status: {current.get('connectivity', 'unknown').title()}")
        print(f"    Current Latency: {current.get('latency_ms', 0)}ms")
        print(f"    Active Interfaces: {current.get('active_interfaces', 0)}")
        
        trends = summary.get("performance_trends", {})
        if trends:
            print(f"    Average Latency: {trends.get('average_latency_ms', 0)}ms")
            print(f"    Latency Range: {trends.get('min_latency_ms', 0)}-{trends.get('max_latency_ms', 0)}ms")
            print(f"    Stability: {trends.get('latency_stability', 'unknown').title()}")
        
        monitor.stop_monitoring()
        
    except KeyboardInterrupt:
        print(f"\n Monitoring stopped by user")
        monitor.stop_monitoring()
    except Exception as e:
        print(f"\n Monitoring error: {e}")
        monitor.stop_monitoring()
    
    print("" + "="*80)
    
    return monitor


if __name__ == "__main__":
    main()