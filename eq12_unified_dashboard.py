#!/usr/bin/env python3
"""
EQ12 Unified Dashboard - God Mode Control Center
Real-time monitoring, controls, and analytics for all EQ12 modules

Features:
- One-click "God Mode" execution of all systems
- Real-time system status monitoring
- Live performance metrics and analytics
- Interactive controls for all EQ12 modules
- Legal compliance framework for betting activities
- Streaming AI assistance integration
- Cross-platform automation orchestration
"""

import asyncio
import logging
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil
from flask import Flask, jsonify, render_template_string
from flask_socketio import SocketIO, emit

# EQ12 system imports
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/dashboard.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EQ12SystemOrchestrator:
    """Core orchestrator for all EQ12 systems and processes"""

    def __init__(self, eq12_root: Path = Path("C:/EQ12")):
        self.eq12_root = eq12_root
        self.processes: dict[str, subprocess.Popen] = {}
        self.system_status: dict[str, Any] = {}
        self.performance_metrics: dict[str, list] = {
            "cpu_usage": [],
            "memory_usage": [],
            "active_processes": [],
            "system_health": [],
        }
        self.is_god_mode_active = False

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "god_mode_active": self.is_god_mode_active,
            "system_health": self._get_system_health(),
            "active_processes": self._get_active_processes(),
            "eq12_modules": self._get_eq12_module_status(),
            "performance": self._get_performance_metrics(),
            "disk_usage": self._get_disk_usage(),
            "network_status": self._get_network_status(),
        }
        return status

    def _get_system_health(self) -> dict[str, Any]:
        """Get system health metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("C:/")

            health_score = 100
            if cpu_percent > 80:
                health_score -= 20
            if memory.percent > 85:
                health_score -= 20
            if disk.percent > 90:
                health_score -= 30

            return {
                "score": max(0, health_score),
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent,
                "status": (
                    "healthy"
                    if health_score > 70
                    else "warning" if health_score > 40 else "critical"
                ),
            }
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {"score": 0, "status": "error", "error": str(e)}

    def _get_active_processes(self) -> list[dict[str, Any]]:
        """Get active EQ12-related processes"""
        eq12_processes = []
        try:
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
                if any(
                    keyword in proc.info["name"].lower()
                    for keyword in ["python", "eq12", "chrome", "firefox"]
                ):
                    eq12_processes.append(
                        {
                            "pid": proc.info["pid"],
                            "name": proc.info["name"],
                            "cpu_percent": proc.info["cpu_percent"],
                            "memory_mb": (
                                proc.info["memory_info"].rss / 1024 / 1024
                                if proc.info["memory_info"]
                                else 0
                            ),
                        }
                    )
        except Exception as e:
            logger.error(f"Error getting active processes: {e}")

        return eq12_processes[:10]  # Limit to top 10

    def _get_eq12_module_status(self) -> dict[str, Any]:
        """Get status of all EQ12 modules"""
        modules = {
            "backtester": self._check_module_status("eq12_backtester"),
            "chrome_automation": self._check_module_status("chrome_governance_automation.py"),
            "firefox_automation": self._check_module_status("firefox_governance_automation.py"),
            "ai_assistant": self._check_module_status("eq12_streaming_assistant.py"),
            "system_scanner": self._check_module_status("eq12_system_scanner.py"),
            "java_integration": self._check_java_integration(),
            "streaming_processor": self._check_module_status("eq12_stream_processor.py"),
        }
        return modules

    def _check_module_status(self, module_name: str) -> dict[str, Any]:
        """Check if a specific module is running and healthy"""
        try:
            # Check if module file exists
            module_path = self.eq12_root / module_name
            if not module_path.exists():
                # Try in scripts directory
                module_path = self.eq12_root / "scripts" / module_name

            status = {
                "exists": module_path.exists(),
                "running": False,
                "healthy": False,
                "last_modified": None,
                "size_kb": 0,
            }

            if module_path.exists():
                stat = module_path.stat()
                status["last_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                status["size_kb"] = stat.st_size / 1024

                # Check if process is running
                for proc in psutil.process_iter(["pid", "cmdline"]):
                    if proc.info["cmdline"] and any(
                        module_name in arg for arg in proc.info["cmdline"]
                    ):
                        status["running"] = True
                        status["healthy"] = True
                        break

            return status
        except Exception as e:
            return {"exists": False, "error": str(e)}

    def _check_java_integration(self) -> dict[str, Any]:
        """Check Java integration status"""
        java_dir = self.eq12_root / "eq12_java_integration"
        status = {
            "exists": java_dir.exists(),
            "maven_configured": False,
            "compiled": False,
            "running": False,
        }

        if java_dir.exists():
            pom_path = java_dir / "pom.xml"
            status["maven_configured"] = pom_path.exists()

            target_dir = java_dir / "target"
            status["compiled"] = target_dir.exists() and any(target_dir.glob("*.jar"))

            # Check for running Java processes
            for proc in psutil.process_iter(["pid", "name"]):
                if "java" in proc.info["name"].lower():
                    status["running"] = True
                    break

        return status

    def _get_performance_metrics(self) -> dict[str, Any]:
        """Get current performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()

            # Update rolling metrics
            self.performance_metrics["cpu_usage"].append(
                {"timestamp": datetime.now().isoformat(), "value": cpu_percent}
            )
            self.performance_metrics["memory_usage"].append(
                {"timestamp": datetime.now().isoformat(), "value": memory.percent}
            )

            # Keep only last 100 data points
            for metric in self.performance_metrics:
                if len(self.performance_metrics[metric]) > 100:
                    self.performance_metrics[metric] = self.performance_metrics[metric][-100:]

            return {
                "current_cpu": cpu_percent,
                "current_memory": memory.percent,
                "cpu_history": self.performance_metrics["cpu_usage"][-20:],
                "memory_history": self.performance_metrics["memory_usage"][-20:],
            }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}

    def _get_disk_usage(self) -> dict[str, Any]:
        """Get disk usage information"""
        try:
            disk = psutil.disk_usage("C:/")
            eq12_size = self._get_directory_size(self.eq12_root)

            return {
                "total_gb": disk.total / 1024**3,
                "used_gb": disk.used / 1024**3,
                "free_gb": disk.free / 1024**3,
                "percent_used": disk.percent,
                "eq12_size_mb": eq12_size / 1024**2,
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_directory_size(self, path: Path) -> int:
        """Get total size of directory in bytes"""
        try:
            total = 0
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    total += file_path.stat().st_size
            return total
        except Exception:
            return 0

    def _get_network_status(self) -> dict[str, Any]:
        """Get network connectivity status"""
        try:
            # Test internet connectivity
            import urllib.request

            try:
                urllib.request.urlopen("http://www.google.com", timeout=5)
                internet_connected = True
            except:
                internet_connected = False

            # Get network interfaces
            interfaces = []
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        interfaces.append({"name": interface, "ip": addr.address})

            return {
                "internet_connected": internet_connected,
                "interfaces": interfaces[:5],  # Limit to 5 interfaces
            }
        except Exception as e:
            return {"error": str(e)}

    async def activate_god_mode(self) -> dict[str, Any]:
        """Activate God Mode - launch all EQ12 systems"""
        logger.info("Activating EQ12 God Mode...")
        self.is_god_mode_active = True

        results = {
            "status": "success",
            "activated_systems": [],
            "failed_systems": [],
            "start_time": datetime.now().isoformat(),
        }

        # Define all systems to launch
        god_mode_systems = [
            {
                "name": "Chrome Governance Automation",
                "command": [
                    "python",
                    str(self.eq12_root / "chrome_governance_automation.py"),
                    "--refresh-daily",
                    "--launch-browser",
                ],
                "background": True,
            },
            {
                "name": "Firefox Governance Setup",
                "command": [
                    "python",
                    str(self.eq12_root / "scripts" / "firefox_governance_automation.py"),
                ],
                "background": True,
            },
            {
                "name": "AI Streaming Assistant",
                "command": [
                    "python",
                    str(self.eq12_root / "eq12_streaming_assistant.py"),
                    "--demo",
                ],
                "background": True,
            },
            {
                "name": "System Health Monitor",
                "command": ["python", str(self.eq12_root / "eq12_system_health.py")],
                "background": True,
            },
            {
                "name": "EQ12 Backtester",
                "command": [
                    "python",
                    str(self.eq12_root / "eq12_backtester" / "run.py"),
                    "--help",
                ],
                "background": False,
            },
        ]

        # Launch each system
        for system in god_mode_systems:
            try:
                logger.info(f"Launching {system['name']}...")

                if system["background"]:
                    proc = subprocess.Popen(
                        system["command"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=(
                            subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                        ),
                    )
                    self.processes[system["name"]] = proc
                else:
                    subprocess.run(system["command"], capture_output=True, text=True, timeout=10)

                results["activated_systems"].append(
                    {
                        "name": system["name"],
                        "status": "launched",
                        "pid": proc.pid if system["background"] else "completed",
                    }
                )

                # Small delay between launches
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Failed to launch {system['name']}: {e}")
                results["failed_systems"].append({"name": system["name"], "error": str(e)})

        results["completion_time"] = datetime.now().isoformat()
        logger.info(
            f"God Mode activation completed: {len(results['activated_systems'])} systems launched"
        )

        return results

    def deactivate_god_mode(self) -> dict[str, Any]:
        """Deactivate God Mode - stop all launched processes"""
        logger.info("Deactivating EQ12 God Mode...")
        self.is_god_mode_active = False

        results = {"status": "success", "stopped_processes": [], "failed_stops": []}

        for name, proc in self.processes.items():
            try:
                if proc.poll() is None:  # Process still running
                    proc.terminate()
                    proc.wait(timeout=5)
                    results["stopped_processes"].append(name)
                    logger.info(f"Stopped {name}")
            except Exception as e:
                logger.error(f"Failed to stop {name}: {e}")
                results["failed_stops"].append({"name": name, "error": str(e)})

        self.processes.clear()
        return results


class EQ12UnifiedDashboard:
    """Main dashboard web application"""

    def __init__(self, port: int = 8080):
        self.port = port
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = "eq12-dashboard-secret-key"
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.orchestrator = EQ12SystemOrchestrator()
        self.setup_routes()
        self.setup_socketio()

    def setup_routes(self):
        """Setup Flask routes"""

        @self.app.route("/")
        def dashboard():
            return render_template_string(DASHBOARD_HTML_TEMPLATE)

        @self.app.route("/api/status")
        def get_status():
            return jsonify(self.orchestrator.get_system_status())

        @self.app.route("/api/god-mode/activate", methods=["POST"])
        def activate_god_mode():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.orchestrator.activate_god_mode())
            return jsonify(result)

        @self.app.route("/api/god-mode/deactivate", methods=["POST"])
        def deactivate_god_mode():
            result = self.orchestrator.deactivate_god_mode()
            return jsonify(result)

        @self.app.route("/api/legal-compliance")
        def get_legal_compliance():
            return jsonify(self.get_legal_compliance_info())

    def setup_socketio(self):
        """Setup SocketIO events for real-time updates"""

        @self.socketio.on("connect")
        def handle_connect():
            emit("status_update", self.orchestrator.get_system_status())
            logger.info("Client connected to dashboard")

        @self.socketio.on("request_status")
        def handle_status_request():
            emit("status_update", self.orchestrator.get_system_status())

    def get_legal_compliance_info(self) -> dict[str, Any]:
        """Get legal compliance information for betting activities"""
        return {
            "disclaimer": "EQ12 is for educational and research purposes only. "
            "All betting activities must comply with local laws and regulations.",
            "age_verification": "Users must be 21+ years old to use betting features.",
            "responsible_gambling": {
                "resources": [
                    "National Council on Problem Gambling: ncpgambling.org",
                    "Gamblers Anonymous: gamblersanonymous.org",
                    "SAMHSA Helpline: 1-800-662-4357",
                ],
                "warning_signs": [
                    "Betting more than you can afford to lose",
                    "Chasing losses with bigger bets",
                    "Neglecting responsibilities to bet",
                    "Lying about betting activities",
                ],
            },
            "transparency": {
                "algorithm_disclosure": "EQ12 uses statistical models and machine learning for predictions",
                "no_guarantee": "Past performance does not guarantee future results",
                "risk_warning": "All betting involves risk of financial loss",
            },
            "last_updated": datetime.now().isoformat(),
        }

    def start_background_monitoring(self):
        """Start background thread for system monitoring"""

        def monitor_loop():
            while True:
                try:
                    status = self.orchestrator.get_system_status()
                    self.socketio.emit("status_update", status)
                    time.sleep(5)  # Update every 5 seconds
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(10)

        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()

    def run(self, debug: bool = False):
        """Run the dashboard"""
        logger.info(f"Starting EQ12 Unified Dashboard on port {self.port}")

        # Start background monitoring
        self.start_background_monitoring()

        # Open browser
        if not debug:
            threading.Timer(2.0, lambda: webbrowser.open(f"http://localhost:{self.port}")).start()

        # Run the dashboard
        self.socketio.run(self.app, host="0.0.0.0", port=self.port, debug=debug)


# HTML Template for the dashboard
DASHBOARD_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 Unified Dashboard - God Mode Control Center</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: white;
            min-height: 100vh;
        }

        .header {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #00ff88;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #00ff88, #00d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .god-mode-button {
            background: linear-gradient(45deg, #ff4757, #ff3838);
            border: none;
            color: white;
            padding: 15px 30px;
            font-size: 1.2rem;
            border-radius: 25px;
            cursor: pointer;
            margin: 20px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3);
        }

        .god-mode-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 71, 87, 0.5);
        }

        .god-mode-button.active {
            background: linear-gradient(45deg, #00ff88, #00d4ff);
            box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3);
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }

        .dashboard-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
        }

        .card-title {
            font-size: 1.4rem;
            margin-bottom: 15px;
            color: #00ff88;
            border-bottom: 2px solid #00ff88;
            padding-bottom: 5px;
        }

        .system-health {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }

        .health-indicator {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
        }

        .health-healthy { background: #00ff88; }
        .health-warning { background: #ffb347; }
        .health-critical { background: #ff4757; }
        .health-error { background: #ff3838; }

        .metric {
            margin: 10px 0;
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
        }

        .metric-label {
            font-weight: bold;
            color: #00d4ff;
        }

        .metric-value {
            font-size: 1.2rem;
            margin-left: 10px;
        }

        .process-list {
            max-height: 300px;
            overflow-y: auto;
        }

        .process-item {
            background: rgba(0, 0, 0, 0.2);
            margin: 5px 0;
            padding: 8px;
            border-radius: 5px;
            font-size: 0.9rem;
        }

        .legal-section {
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid #ffc107;
            margin-top: 20px;
        }

        .legal-warning {
            color: #ffc107;
            font-weight: bold;
            margin-bottom: 10px;
        }

        .chart-container {
            position: relative;
            height: 200px;
            margin-top: 15px;
        }

        .status-online {
            color: #00ff88;
        }

        .status-offline {
            color: #ff4757;
        }

        .timestamp {
            font-size: 0.8rem;
            color: #888;
            text-align: right;
            margin-top: 10px;
        }

        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
                padding: 10px;
            }

            .header h1 {
                font-size: 2rem;
            }

            .god-mode-button {
                padding: 12px 20px;
                font-size: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 EQ12 UNIFIED DASHBOARD</h1>
        <p>God Mode Control Center - Real-time System Monitoring & Control</p>
        <button id="godModeBtn" class="god-mode-button" onclick="toggleGodMode()">
            ACTIVATE GOD MODE
        </button>
        <div id="godModeStatus"></div>
    </div>

    <div class="dashboard-grid">
        <div class="dashboard-card">
            <div class="card-title">🎯 System Health</div>
            <div id="systemHealth">
                <div class="system-health">
                    <div class="health-indicator health-healthy"></div>
                    <span>System Status: Loading...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Health Score:</span>
                    <span class="metric-value" id="healthScore">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">CPU Usage:</span>
                    <span class="metric-value" id="cpuUsage">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Memory Usage:</span>
                    <span class="metric-value" id="memoryUsage">--</span>
                </div>
            </div>
        </div>

        <div class="dashboard-card">
            <div class="card-title">📊 Performance Metrics</div>
            <div class="chart-container">
                <canvas id="performanceChart"></canvas>
            </div>
        </div>

        <div class="dashboard-card">
            <div class="card-title">🔧 EQ12 Modules Status</div>
            <div id="modulesStatus">
                Loading module status...
            </div>
        </div>

        <div class="dashboard-card">
            <div class="card-title">⚡ Active Processes</div>
            <div class="process-list" id="processList">
                Loading processes...
            </div>
        </div>

        <div class="dashboard-card">
            <div class="card-title">💾 System Resources</div>
            <div id="systemResources">
                <div class="metric">
                    <span class="metric-label">Disk Usage:</span>
                    <span class="metric-value" id="diskUsage">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">EQ12 Size:</span>
                    <span class="metric-value" id="eq12Size">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Network:</span>
                    <span class="metric-value" id="networkStatus">--</span>
                </div>
            </div>
        </div>

        <div class="dashboard-card legal-section">
            <div class="card-title">⚖️ Legal Compliance</div>
            <div class="legal-warning">
                ⚠️ IMPORTANT: Betting Disclaimer & Legal Notice
            </div>
            <p><strong>Educational Use Only:</strong> EQ12 is for research and educational purposes.</p>
            <p><strong>Age Verification:</strong> Must be 21+ to use betting features.</p>
            <p><strong>Responsible Gaming:</strong> Only bet what you can afford to lose.</p>
            <p><strong>No Guarantees:</strong> Past performance does not guarantee future results.</p>
            <div style="margin-top: 10px; font-size: 0.9rem;">
                <strong>Resources:</strong><br>
                • Problem Gambling: ncpgambling.org<br>
                • Gamblers Anonymous: gamblersanonymous.org<br>
                • SAMHSA Helpline: 1-800-662-4357
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let godModeActive = false;
        let performanceChart = null;

        // Initialize performance chart
        function initPerformanceChart() {
            const ctx = document.getElementById('performanceChart').getContext('2d');
            performanceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU %',
                        data: [],
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Memory %',
                        data: [],
                        borderColor: '#00d4ff',
                        backgroundColor: 'rgba(0, 212, 255, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: 'white'
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: 'white'
                            }
                        },
                        y: {
                            ticks: {
                                color: 'white'
                            }
                        }
                    }
                }
            });
        }

        // Update dashboard with status data
        function updateDashboard(status) {
            // Update system health
            const health = status.system_health;
            document.getElementById('healthScore').textContent = health.score + '%';
            document.getElementById('cpuUsage').textContent = health.cpu_usage.toFixed(1) + '%';
            document.getElementById('memoryUsage').textContent = health.memory_usage.toFixed(1) + '%';

            // Update health indicator
            const healthIndicator = document.querySelector('.health-indicator');
            healthIndicator.className = 'health-indicator health-' + health.status;

            // Update performance chart
            if (performanceChart && status.performance) {
                const perf = status.performance;
                const now = new Date().toLocaleTimeString();

                performanceChart.data.labels.push(now);
                performanceChart.data.datasets[0].data.push(perf.current_cpu);
                performanceChart.data.datasets[1].data.push(perf.current_memory);

                // Keep only last 20 data points
                if (performanceChart.data.labels.length > 20) {
                    performanceChart.data.labels.shift();
                    performanceChart.data.datasets[0].data.shift();
                    performanceChart.data.datasets[1].data.shift();
                }

                performanceChart.update();
            }

            // Update modules status
            const modulesDiv = document.getElementById('modulesStatus');
            let modulesHtml = '';
            for (const [name, moduleStatus] of Object.entries(status.eq12_modules)) {
                const statusClass = moduleStatus.running ? 'status-online' : 'status-offline';
                const statusText = moduleStatus.running ? 'RUNNING' : moduleStatus.exists ? 'STOPPED' : 'MISSING';
                modulesHtml += `
                    <div class="metric">
                        <span class="metric-label">${name}:</span>
                        <span class="metric-value ${statusClass}">${statusText}</span>
                    </div>
                `;
            }
            modulesDiv.innerHTML = modulesHtml;

            // Update processes
            const processList = document.getElementById('processList');
            let processesHtml = '';
            status.active_processes.forEach(proc => {
                processesHtml += `
                    <div class="process-item">
                        <strong>${proc.name}</strong> (PID: ${proc.pid})<br>
                        CPU: ${proc.cpu_percent}% | Memory: ${proc.memory_mb.toFixed(1)} MB
                    </div>
                `;
            });
            processList.innerHTML = processesHtml;

            // Update system resources
            if (status.disk_usage) {
                document.getElementById('diskUsage').textContent =
                    status.disk_usage.percent_used.toFixed(1) + '% (' +
                    status.disk_usage.free_gb.toFixed(1) + ' GB free)';
                document.getElementById('eq12Size').textContent =
                    status.disk_usage.eq12_size_mb.toFixed(1) + ' MB';
            }

            if (status.network_status) {
                const netStatus = status.network_status.internet_connected ?
                    'Connected' : 'Disconnected';
                document.getElementById('networkStatus').textContent = netStatus;
            }

            // Update God Mode status
            godModeActive = status.god_mode_active;
            const godModeBtn = document.getElementById('godModeBtn');
            if (godModeActive) {
                godModeBtn.textContent = 'DEACTIVATE GOD MODE';
                godModeBtn.classList.add('active');
            } else {
                godModeBtn.textContent = 'ACTIVATE GOD MODE';
                godModeBtn.classList.remove('active');
            }

            // Add timestamp
            const timestamp = new Date(status.timestamp).toLocaleString();
            document.querySelectorAll('.timestamp').forEach(el => {
                el.textContent = 'Last updated: ' + timestamp;
            });
        }

        // Toggle God Mode
        async function toggleGodMode() {
            const btn = document.getElementById('godModeBtn');
            const statusDiv = document.getElementById('godModeStatus');

            btn.disabled = true;
            btn.textContent = godModeActive ? 'DEACTIVATING...' : 'ACTIVATING...';

            try {
                const endpoint = godModeActive ? '/api/god-mode/deactivate' : '/api/god-mode/activate';
                const response = await fetch(endpoint, { method: 'POST' });
                const result = await response.json();

                if (result.status === 'success') {
                    if (godModeActive) {
                        statusDiv.innerHTML = '<div style="color: #00ff88;">God Mode Deactivated</div>';
                    } else {
                        statusDiv.innerHTML = `
                            <div style="color: #00ff88;">
                                God Mode Activated!<br>
                                Launched: ${result.activated_systems.length} systems<br>
                                Failed: ${result.failed_systems.length} systems
                            </div>
                        `;
                    }
                } else {
                    statusDiv.innerHTML = '<div style="color: #ff4757;">Error: ' + result.error + '</div>';
                }
            } catch (error) {
                statusDiv.innerHTML = '<div style="color: #ff4757;">Network Error</div>';
            }

            btn.disabled = false;
            setTimeout(() => {
                statusDiv.innerHTML = '';
            }, 5000);
        }

        // Socket event handlers
        socket.on('connect', function() {
            console.log('Connected to EQ12 Dashboard');
        });

        socket.on('status_update', function(status) {
            updateDashboard(status);
        });

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initPerformanceChart();

            // Request initial status
            socket.emit('request_status');

            // Add timestamps to cards
            document.querySelectorAll('.dashboard-card').forEach(card => {
                if (!card.querySelector('.timestamp')) {
                    const timestamp = document.createElement('div');
                    timestamp.className = 'timestamp';
                    card.appendChild(timestamp);
                }
            });
        });

        // Auto-refresh status every 30 seconds
        setInterval(() => {
            socket.emit('request_status');
        }, 30000);
    </script>
</body>
</html>
"""


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Unified Dashboard")
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to run dashboard on (default: 8080)",
    )
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")

    args = parser.parse_args()

    try:
        dashboard = EQ12UnifiedDashboard(port=args.port)
        dashboard.run(debug=args.debug)
    except KeyboardInterrupt:
        logger.info("Dashboard shutdown requested")
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
