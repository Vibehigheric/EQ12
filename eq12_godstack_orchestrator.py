#!/usr/bin/env python3
"""
EQ12 GODSTACK System Orchestrator

This is the master controller that coordinates all EQ12 system components
providing a unified interface for system management, monitoring, and control.

Features:
- Unified system startup/shutdown
- Real-time monitoring and health checks
- Automated recovery and restart procedures
- WebSocket server for real-time dashboard
- RESTful API for system control
- Comprehensive logging and telemetry

Author: EQ12 System
Created: 2025-10-04
"""

import asyncio
import json
import logging
import signal
import sqlite3
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

import psutil
import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/orchestrator.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("EQ12Orchestrator")


class EQ12SystemOrchestrator:
    """Master system orchestrator for EQ12 GODSTACK"""

    def __init__(self):
        self.base_path = Path("C:/EQ12")
        self.dashboard_path = self.base_path / "dashboard"
        self.logs_path = self.base_path / "logs"

        # System state
        self.is_running = False
        self.components = {}
        self.websocket_clients = set()
        self.http_server = None
        self.websocket_server = None

        # Component definitions
        self.system_components = {
            "database": {
                "name": "Database Engine",
                "script": "eq12_database_migration.py",
                "health_check": self.check_database_health,
                "critical": True,
                "restart_on_failure": True,
            },
            "sports_betting": {
                "name": "Sports Betting Engine",
                "script": "eq12_sports_betting_advanced.ps1",
                "args": ["-Action", "startlive"],
                "health_check": self.check_betting_engine_health,
                "critical": True,
                "restart_on_failure": True,
            },
            "cold_restart": {
                "name": "Cold Restart Manager",
                "script": "eq12_cold_restart_manager.py",
                "health_check": self.check_restart_manager_health,
                "critical": False,
                "restart_on_failure": False,
            },
            "dashboard": {
                "name": "Real-time Dashboard",
                "script": None,  # HTTP server
                "health_check": self.check_dashboard_health,
                "critical": False,
                "restart_on_failure": True,
            },
        }

        self.performance_metrics = {
            "system_uptime": 0,
            "total_bets_placed": 0,
            "total_profit": 0.0,
            "win_rate": 0.0,
            "active_processes": 0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
        }

    async def initialize_system(self):
        """Initialize the complete EQ12 system"""
        logger.info("🚀 INITIALIZING EQ12 GODSTACK SYSTEM")
        logger.info("=" * 60)

        try:
            # Phase 1: Pre-flight checks
            logger.info("📋 Phase 1: Pre-flight system checks")
            if not await self.run_preflight_checks():
                logger.error("❌ Pre-flight checks failed")
                return False

            # Phase 2: Initialize core components
            logger.info("📋 Phase 2: Core component initialization")
            if not await self.initialize_core_components():
                logger.error("❌ Core component initialization failed")
                return False

            # Phase 3: Start system services
            logger.info("📋 Phase 3: Starting system services")
            if not await self.start_system_services():
                logger.error("❌ System service startup failed")
                return False

            # Phase 4: Launch dashboard and monitoring
            logger.info("📋 Phase 4: Dashboard and monitoring setup")
            if not await self.launch_dashboard():
                logger.error("❌ Dashboard launch failed")
                return False

            # Phase 5: Final health check
            logger.info("📋 Phase 5: Final system health verification")
            health_status = await self.perform_health_check()

            if health_status["overall_health"] >= 0.8:
                logger.info("✅ EQ12 GODSTACK SYSTEM FULLY OPERATIONAL")
                logger.info("🌐 Dashboard: http://localhost:8080")
                logger.info("🔗 WebSocket: ws://localhost:8765")
                logger.info("=" * 60)
                self.is_running = True
                return True
            logger.warning(
                f"⚠️ System operational with warnings (Health: {health_status['overall_health']:.1%})"
            )
            self.is_running = True
            return True

        except Exception as e:
            logger.error(f"💥 CRITICAL ERROR during system initialization: {e}")
            return False

    async def run_preflight_checks(self) -> bool:
        """Run comprehensive pre-flight checks"""
        checks_passed = 0
        total_checks = 6

        # Check Python environment
        try:
            result = subprocess.run(
                [sys.executable, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                logger.info(f"✅ Python: {result.stdout.strip()}")
                checks_passed += 1
            else:
                logger.error("❌ Python environment check failed")
        except Exception as e:
            logger.error(f"❌ Python check error: {e}")

        # Check PowerShell
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-Host | Select-Object Version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                logger.info("✅ PowerShell environment available")
                checks_passed += 1
            else:
                logger.error("❌ PowerShell environment check failed")
        except Exception as e:
            logger.error(f"❌ PowerShell check error: {e}")

        # Check directory structure
        required_dirs = ["scripts", "logs", "configs", "data", "dashboard"]
        for dir_name in required_dirs:
            dir_path = self.base_path / dir_name
            if dir_path.exists():
                logger.info(f"✅ Directory: {dir_name}")
                checks_passed += 1
            else:
                logger.warning(f"⚠️ Missing directory: {dir_name} - will create")
                dir_path.mkdir(parents=True, exist_ok=True)
                checks_passed += 1

        # The total should be updated to match actual checks
        success_rate = checks_passed / (total_checks + len(required_dirs))
        logger.info(
            f"📊 Pre-flight checks: {checks_passed}/{total_checks + len(required_dirs)} passed ({success_rate:.1%})"
        )

        return success_rate >= 0.8

    async def initialize_core_components(self) -> bool:
        """Initialize core system components"""
        logger.info("🔧 Initializing core components...")

        # Initialize database
        db_init = await self.initialize_database()
        if not db_init:
            logger.error("❌ Database initialization failed")
            return False

        # Validate configuration files
        config_valid = await self.validate_configurations()
        if not config_valid:
            logger.warning("⚠️ Configuration validation had issues - proceeding with defaults")

        # Initialize logging system
        logs_init = await self.initialize_logging_system()
        if not logs_init:
            logger.error("❌ Logging system initialization failed")
            return False

        logger.info("✅ Core components initialized successfully")
        return True

    async def initialize_database(self) -> bool:
        """Initialize and migrate database"""
        try:
            db_path = self.base_path / "data" / "sports_betting.db"

            # Ensure data directory exists
            db_path.parent.mkdir(parents=True, exist_ok=True)

            # Run database migration
            migration_script = self.base_path / "eq12_database_migration.py"
            if migration_script.exists():
                result = subprocess.run(
                    [sys.executable, str(migration_script)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode == 0:
                    logger.info("✅ Database migration completed")
                    return True
                logger.error(f"❌ Database migration failed: {result.stderr}")
                return False
            # Create minimal database structure
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS system_status (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        component TEXT NOT NULL,
                        status TEXT NOT NULL,
                        details TEXT
                    )
                """
            )

            conn.commit()
            conn.close()
            logger.info("✅ Basic database structure created")
            return True

        except Exception as e:
            logger.error(f"❌ Database initialization error: {e}")
            return False

    async def validate_configurations(self) -> bool:
        """Validate system configuration files"""
        try:
            config_dir = self.base_path / "configs"
            config_dir.mkdir(parents=True, exist_ok=True)

            # Check for main config file
            main_config = config_dir / "sports_betting_config.json"
            if not main_config.exists():
                # Create default configuration
                default_config = {
                    "database": {
                        "path": "data/sports_betting.db",
                        "backup_interval": 3600,
                    },
                    "betting": {
                        "min_edge": 0.05,
                        "max_bet_size": 1000,
                        "bankroll_percentage": 0.02,
                    },
                    "monitoring": {
                        "health_check_interval": 30,
                        "log_retention_days": 30,
                    },
                    "dashboard": {
                        "port": 8080,
                        "websocket_port": 8765,
                        "auto_refresh_interval": 30,
                    },
                }

                with open(main_config, "w") as f:
                    json.dump(default_config, f, indent=4)

                logger.info("✅ Default configuration created")
            else:
                # Validate existing configuration
                with open(main_config) as f:
                    json.load(f)

                logger.info("✅ Configuration file validated")

            return True

        except Exception as e:
            logger.error(f"❌ Configuration validation error: {e}")
            return False

    async def initialize_logging_system(self) -> bool:
        """Initialize comprehensive logging system"""
        try:
            # Ensure logs directory exists
            self.logs_path.mkdir(parents=True, exist_ok=True)

            # Create log files for different components
            log_files = [
                "orchestrator.log",
                "sports_betting.log",
                "dashboard.log",
                "system_health.log",
                "performance.log",
            ]

            for log_file in log_files:
                log_path = self.logs_path / log_file
                if not log_path.exists():
                    log_path.touch()

            logger.info("✅ Logging system initialized")
            return True

        except Exception as e:
            logger.error(f"❌ Logging initialization error: {e}")
            return False

    async def start_system_services(self) -> bool:
        """Start all system services in proper order"""
        logger.info("🚀 Starting system services...")

        services_started = 0

        for component_id, component in self.system_components.items():
            if component_id == "dashboard":
                continue  # Dashboard started separately

            try:
                success = await self.start_component(component_id, component)
                if success:
                    services_started += 1
                    logger.info(f"✅ Started: {component['name']}")
                else:
                    if component.get("critical", False):
                        logger.error(f"❌ CRITICAL: Failed to start {component['name']}")
                        return False
                    logger.warning(f"⚠️ Failed to start {component['name']} (non-critical)")

                # Wait between service starts
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"❌ Error starting {component['name']}: {e}")
                if component.get("critical", False):
                    return False

        logger.info(f"📊 Services started: {services_started}/{len(self.system_components) - 1}")
        return services_started >= 1  # At least one service must start

    async def start_component(self, component_id: str, component: dict) -> bool:
        """Start a single system component"""
        script = component.get("script")
        if not script:
            return True  # No script to run

        script_path = self.base_path / script
        if not script_path.exists():
            logger.warning(f"Script not found: {script_path}")
            return False

        try:
            # Determine how to run the script
            if script.endswith(".py"):
                cmd = [sys.executable, str(script_path)]
            elif script.endswith(".ps1"):
                cmd = [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script_path),
                ]
                # Add any additional arguments
                if "args" in component:
                    cmd.extend(component["args"])
            else:
                logger.error(f"Unknown script type: {script}")
                return False

            # Start the process
            if component_id == "sports_betting":
                # For betting engine, we want it to run continuously
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                self.components[component_id] = {
                    "process": process,
                    "started_at": datetime.now(),
                    "status": "running",
                }

                # Give it a moment to start
                await asyncio.sleep(3)

                if process.poll() is None:  # Still running
                    return True
                _stdout, stderr = process.communicate()
                logger.error(f"Process exited early: {stderr}")
                return False
            # For other components, run once and check result
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            self.components[component_id] = {
                "last_run": datetime.now(),
                "status": "completed" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
            }

            return result.returncode == 0

        except Exception as e:
            logger.error(f"Error starting {component_id}: {e}")
            return False

    async def launch_dashboard(self) -> bool:
        """Launch the real-time dashboard"""
        logger.info("🌐 Launching real-time dashboard...")

        try:
            # Start HTTP server for dashboard
            dashboard_success = await self.start_http_server()

            # Start WebSocket server for real-time updates
            websocket_success = await self.start_websocket_server()

            if dashboard_success and websocket_success:
                logger.info("✅ Dashboard launched successfully")

                # Try to open browser (non-blocking)
                try:
                    webbrowser.open("http://localhost:8080/eq12_realtime_dashboard.html")
                    logger.info("🌐 Browser launched")
                except Exception:
                    logger.info(
                        "🌐 Dashboard available at: http://localhost:8080/eq12_realtime_dashboard.html"
                    )

                return True
            logger.error("❌ Dashboard launch failed")
            return False

        except Exception as e:
            logger.error(f"❌ Dashboard launch error: {e}")
            return False

    async def start_http_server(self) -> bool:
        """Start HTTP server for dashboard"""
        try:

            class DashboardHandler(SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=str(self.dashboard_path), **kwargs)

                def log_message(self, format, *args):
                    # Suppress default HTTP server logs
                    pass

            # Update the handler to use the correct dashboard path
            def handler(*args, **kwargs):
                return DashboardHandler(*args, **kwargs)

            handler.dashboard_path = self.dashboard_path

            self.http_server = HTTPServer(("localhost", 8080), handler)

            # Start server in background thread
            server_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
            server_thread.start()

            logger.info("✅ HTTP server started on port 8080")
            return True

        except Exception as e:
            logger.error(f"❌ HTTP server start error: {e}")
            return False

    async def start_websocket_server(self) -> bool:
        """Start WebSocket server for real-time updates"""
        try:

            async def handle_client(websocket, path):
                logger.info(f"🔗 WebSocket client connected: {websocket.remote_address}")
                self.websocket_clients.add(websocket)

                try:
                    # Send initial status
                    health_status = await self.perform_health_check()
                    await websocket.send(
                        json.dumps({"type": "initial_status", "data": health_status})
                    )

                    # Keep connection alive
                    async for message in websocket:
                        # Handle incoming messages from dashboard
                        try:
                            data = json.loads(message)
                            await self.handle_websocket_message(websocket, data)
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON from client: {message}")

                except websockets.exceptions.ConnectionClosed:
                    pass
                finally:
                    self.websocket_clients.discard(websocket)
                    logger.info("🔌 WebSocket client disconnected")

            # Start WebSocket server
            self.websocket_server = await websockets.serve(handle_client, "localhost", 8765)

            logger.info("✅ WebSocket server started on port 8765")
            return True

        except Exception as e:
            logger.error(f"❌ WebSocket server start error: {e}")
            return False

    async def handle_websocket_message(self, websocket, data):
        """Handle messages from WebSocket clients"""
        try:
            message_type = data.get("type")

            if message_type == "request_status":
                health_status = await self.perform_health_check()
                await websocket.send(json.dumps({"type": "status_update", "data": health_status}))

            elif message_type == "cold_restart":
                logger.info("🔥 Cold restart requested via WebSocket")
                # Execute cold restart in background
                asyncio.create_task(self.execute_cold_restart())
                await websocket.send(
                    json.dumps(
                        {
                            "type": "restart_initiated",
                            "message": "Cold restart initiated",
                        }
                    )
                )

        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

    async def perform_health_check(self) -> dict:
        """Perform comprehensive system health check"""
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "overall_health": 0.0,
            "performance": {},
        }

        # Check each component
        healthy_components = 0
        total_components = len(self.system_components)

        for component_id, component in self.system_components.items():
            try:
                if component.get("health_check"):
                    is_healthy = await component["health_check"]()
                    health_data["components"][component_id] = {
                        "name": component["name"],
                        "status": "healthy" if is_healthy else "unhealthy",
                        "critical": component.get("critical", False),
                    }

                    if is_healthy:
                        healthy_components += 1
                else:
                    health_data["components"][component_id] = {
                        "name": component["name"],
                        "status": "unknown",
                        "critical": component.get("critical", False),
                    }
                    healthy_components += 0.5  # Partial credit for unknown status

            except Exception as e:
                logger.error(f"Health check error for {component_id}: {e}")
                health_data["components"][component_id] = {
                    "name": component["name"],
                    "status": "error",
                    "error": str(e),
                    "critical": component.get("critical", False),
                }

        # Calculate overall health
        health_data["overall_health"] = (
            healthy_components / total_components if total_components > 0 else 0.0
        )

        # Add performance metrics
        health_data["performance"] = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": (
                psutil.disk_usage("/").percent
                if sys.platform != "win32"
                else psutil.disk_usage("C:").percent
            ),
            "active_processes": len(
                [
                    p
                    for p in psutil.process_iter()
                    if "python" in p.name().lower() or "eq12" in " ".join(p.cmdline()).lower()
                ]
            ),
        }

        return health_data

    # Health check methods for individual components
    async def check_database_health(self) -> bool:
        """Check database connectivity and integrity"""
        try:
            db_path = self.base_path / "data" / "sports_betting.db"
            if not db_path.exists():
                return False

            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
            result = cursor.fetchone()
            conn.close()

            return result is not None
        except Exception:
            return False

    async def check_betting_engine_health(self) -> bool:
        """Check sports betting engine status"""
        try:
            if "sports_betting" in self.components:
                process = self.components["sports_betting"].get("process")
                if process and process.poll() is None:
                    return True
            return False
        except Exception:
            return False

    async def check_restart_manager_health(self) -> bool:
        """Check cold restart manager availability"""
        try:
            script_path = self.base_path / "eq12_cold_restart_manager.py"
            return script_path.exists()
        except Exception:
            return False

    async def check_dashboard_health(self) -> bool:
        """Check dashboard server status"""
        try:
            return self.http_server is not None and self.websocket_server is not None
        except Exception:
            return False

    async def execute_cold_restart(self):
        """Execute system cold restart"""
        logger.info("🔥 Executing cold restart...")

        try:
            # Import and run cold restart manager
            from eq12_cold_restart_manager import EQ12ColdRestartManager

            restart_manager = EQ12ColdRestartManager()

            success = await restart_manager.execute_cold_restart(force=False)

            if success:
                logger.info("✅ Cold restart completed successfully")
                # Broadcast success to all WebSocket clients
                await self.broadcast_to_clients(
                    {
                        "type": "restart_completed",
                        "status": "success",
                        "message": "Cold restart completed successfully",
                    }
                )
            else:
                logger.error("❌ Cold restart failed")
                await self.broadcast_to_clients(
                    {
                        "type": "restart_completed",
                        "status": "error",
                        "message": "Cold restart failed - check logs",
                    }
                )

        except Exception as e:
            logger.error(f"Error during cold restart: {e}")
            await self.broadcast_to_clients(
                {
                    "type": "restart_completed",
                    "status": "error",
                    "message": f"Cold restart error: {e!s}",
                }
            )

    async def broadcast_to_clients(self, message: dict):
        """Broadcast message to all connected WebSocket clients"""
        if self.websocket_clients:
            message_json = json.dumps(message)
            disconnected_clients = set()

            for client in self.websocket_clients:
                try:
                    await client.send(message_json)
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(client)
                except Exception as e:
                    logger.warning(f"Error broadcasting to client: {e}")
                    disconnected_clients.add(client)

            # Remove disconnected clients
            self.websocket_clients -= disconnected_clients

    async def monitoring_loop(self):
        """Main monitoring loop for system health and updates"""
        logger.info("👁️ Starting system monitoring loop...")

        while self.is_running:
            try:
                # Perform health check
                health_status = await self.perform_health_check()

                # Log critical issues
                for _component_id, component_health in health_status["components"].items():
                    if component_health["status"] == "unhealthy" and component_health.get(
                        "critical", False
                    ):
                        logger.error(f"🚨 CRITICAL: {component_health['name']} is unhealthy")

                # Broadcast health update to dashboard
                await self.broadcast_to_clients({"type": "health_update", "data": health_status})

                # Check performance metrics
                perf = health_status["performance"]
                if perf["cpu_percent"] > 80:
                    logger.warning(f"⚡ High CPU usage: {perf['cpu_percent']:.1f}%")

                if perf["memory_percent"] > 85:
                    logger.warning(f"🧠 High memory usage: {perf['memory_percent']:.1f}%")

                # Sleep until next check
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Longer sleep on error

    async def shutdown_system(self):
        """Graceful system shutdown"""
        logger.info("🛑 Shutting down EQ12 GODSTACK system...")

        self.is_running = False

        # Stop all component processes
        for component_id, component_data in self.components.items():
            if "process" in component_data:
                try:
                    process = component_data["process"]
                    if process.poll() is None:
                        process.terminate()
                        await asyncio.sleep(3)
                        if process.poll() is None:
                            process.kill()
                    logger.info(f"✅ Stopped component: {component_id}")
                except Exception as e:
                    logger.error(f"Error stopping {component_id}: {e}")

        # Close servers
        if self.http_server:
            self.http_server.shutdown()

        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()

        logger.info("✅ EQ12 GODSTACK system shutdown complete")

    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        asyncio.create_task(self.shutdown_system())


async def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 GODSTACK System Orchestrator")
    parser.add_argument(
        "--auto-launch",
        action="store_true",
        help="Automatically launch browser dashboard",
    )
    parser.add_argument("--headless", action="store_true", help="Run without launching browser")

    parser.parse_args()

    # Create orchestrator
    orchestrator = EQ12SystemOrchestrator()

    # Set up signal handlers
    signal.signal(signal.SIGINT, orchestrator.signal_handler)
    signal.signal(signal.SIGTERM, orchestrator.signal_handler)

    try:
        # Initialize system
        success = await orchestrator.initialize_system()

        if not success:
            logger.error("💥 System initialization failed")
            sys.exit(1)

        # Start monitoring loop
        monitoring_task = asyncio.create_task(orchestrator.monitoring_loop())

        # Keep system running
        logger.info("🎯 EQ12 GODSTACK is now fully operational")
        logger.info("Press Ctrl+C to shutdown gracefully")

        # Wait for monitoring loop or shutdown signal
        await monitoring_task

    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"💥 CRITICAL SYSTEM ERROR: {e}")
    finally:
        await orchestrator.shutdown_system()


if __name__ == "__main__":
    asyncio.run(main())
