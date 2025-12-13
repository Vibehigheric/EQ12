#!/usr/bin/env python3
"""
EQ12 MCP Integration Layer

Integrates Model Context Protocol (MCP) servers with EQ12 automation system.
Enables natural language Docker management, desktop automation, and enhanced debugging.

Author: EQ12 AI Agent
Version: 1.0.0
"""

import argparse
import contextlib
import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/mcp_integration.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class MCPIntegration:
    """EQ12 MCP Integration Manager"""

    def __init__(self):
        self.eq12_root = Path("C:/EQ12")
        self.mcp_servers = {
            "docker": self.eq12_root / "docker_mcp_server",
            "advanced_docker": self.eq12_root / "advanced_docker_mcp",
            "desktop_commander": self.eq12_root / "desktop_commander_mcp",
            "main_servers": self.eq12_root / "mcp_servers",
        }
        self.active_servers = {}
        self.log_dir = self.eq12_root / "logs"

    def log_system_snapshot(self, event: str, data: dict[str, Any]):
        """Log structured JSON snapshot for EQ12 system events"""
        timestamp = datetime.utcnow().isoformat() + "Z"
        snapshot = {
            "timestamp": timestamp,
            "event": event,
            "system": "EQ12_MCP_Integration",
            "data": data,
            "active_servers": list(self.active_servers.keys()),
        }

        log_file = self.log_dir / \
            f"mcp_integration_{datetime.now().strftime('%Y%m%d')}.json"
        with open(log_file, "a") as f:
            f.write(json.dumps(snapshot) + "\n")

    def check_mcp_server_health(self, server_name: str) -> dict[str, Any]:
        """Check health status of MCP server"""
        server_path = self.mcp_servers.get(server_name)
        if not server_path or not server_path.exists():
            return {"status": "missing", "path": str(server_path)}

        # Check for package.json and node_modules
        package_json = server_path / "package.json"
        node_modules = server_path / "node_modules"
        dist_folder = server_path / "dist"

        health = {
            "status": "healthy",
            "path": str(server_path),
            "has_package_json": package_json.exists(),
            "has_dependencies": node_modules.exists(),
            "has_build": (
                dist_folder.exists() if server_name == "desktop_commander" else True),
            "last_modified": (
                server_path.stat().st_mtime if server_path.exists() else None),
        }

        if not all([health["has_package_json"], health["has_dependencies"]]):
            health["status"] = "unhealthy"

        return health

    def start_mcp_server(self, server_name: str, port: int | None = None) -> bool:
        """Start an MCP server process"""
        try:
            server_path = self.mcp_servers.get(server_name)
            if not server_path:
                logger.error(f"Unknown MCP server: {server_name}")
                return False

            health = self.check_mcp_server_health(server_name)
            if health["status"] != "healthy":
                logger.error(f"MCP server {server_name} is not healthy: {health}")
                return False

            # Start server based on type
            if server_name in ["docker", "advanced_docker"]:
                cmd = ["npm", "start"]
            elif server_name == "desktop_commander":
                cmd = ["node", "dist/index.js"]
            else:
                logger.warning(f"Unknown startup method for {server_name}")
                return False

            logger.info(f"Starting MCP server: {server_name}")
            process = subprocess.Popen(
                cmd,
                cwd=str(server_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.active_servers[server_name] = {
                "process": process,
                "pid": process.pid,
                "port": port,
                "started_at": datetime.utcnow().isoformat(),
                "cmd": cmd,
            }

            self.log_system_snapshot(
                "mcp_server_started",
                {"server_name": server_name, "pid": process.pid, "cmd": cmd},
            )

            return True

        except Exception as e:
            logger.error(f"Failed to start MCP server {server_name}: {e}")
            return False

    def stop_mcp_server(self, server_name: str) -> bool:
        """Stop an MCP server process"""
        try:
            if server_name not in self.active_servers:
                logger.warning(f"MCP server {server_name} is not active")
                return False

            server_info = self.active_servers[server_name]
            process = server_info["process"]

            logger.info(f"Stopping MCP server: {server_name} (PID: {process.pid})")
            process.terminate()

            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing MCP server {server_name}")
                process.kill()
                process.wait()

            del self.active_servers[server_name]

            self.log_system_snapshot(
                "mcp_server_stopped",
                {"server_name": server_name, "pid": server_info["pid"]},
            )

            return True

        except Exception as e:
            logger.error(f"Failed to stop MCP server {server_name}: {e}")
            return False

    def get_server_status(self) -> dict[str, Any]:
        """Get status of all MCP servers"""
        status = {"timestamp": datetime.utcnow().isoformat(), "servers": {}}

        for server_name in self.mcp_servers:
            health = self.check_mcp_server_health(server_name)
            is_active = server_name in self.active_servers

            status["servers"][server_name] = {
                "health": health,
                "active": is_active,
                "process_info": self.active_servers.get(server_name, {}).copy(),
            }

            # Remove process object for JSON serialization
            if "process" in status["servers"][server_name]["process_info"]:
                del status["servers"][server_name]["process_info"]["process"]

        return status

    def test_docker_mcp(self) -> dict[str, Any]:
        """Test Docker MCP functionality"""
        logger.info("Testing Docker MCP integration...")

        results = {
            "docker_version": None,
            "docker_status": "unknown",
            "containers": [],
            "mcp_server_health": None,
        }

        try:
            # Check Docker installation
            docker_result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=10
            )

            if docker_result.returncode == 0:
                results["docker_version"] = docker_result.stdout.strip()
                results["docker_status"] = "available"

                # List containers
                ps_result = subprocess.run(
                    ["docker", "ps", "-a", "--format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if ps_result.returncode == 0:
                    for line in ps_result.stdout.strip().split("\n"):
                        if line:
                            with contextlib.suppress(json.JSONDecodeError):
                                results["containers"].append(json.loads(line))

            else:
                results["docker_status"] = "unavailable"

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            results["docker_status"] = "error"
            results["error"] = str(e)

        # Check MCP server health
        results["mcp_server_health"] = {
            "docker": self.check_mcp_server_health("docker"),
            "advanced_docker": self.check_mcp_server_health("advanced_docker"),
        }

        return results

    def run_eq12_debug_with_mcp(self) -> dict[str, Any]:
        """Run EQ12 debug session with MCP enhancement"""
        logger.info("Starting EQ12 debug session with MCP integration...")

        debug_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "mcp_status": self.get_server_status(),
            "docker_test": self.test_docker_mcp(),
            "eq12_components": {},
            "integration_status": "starting",
        }

        try:
            # Check EQ12 core components
            eq12_scripts = self.eq12_root / "scripts"
            eq12_tests = self.eq12_root / "tests"

            debug_results["eq12_components"] = {
                "scripts_available": eq12_scripts.exists(),
                "tests_available": eq12_tests.exists(),
                "script_count": (
                    len(list(eq12_scripts.glob("*.py"))) if eq12_scripts.exists() else 0
                ),
                "test_count": (len(list(eq12_tests.glob("*.py"))) if eq12_tests.exists() else 0),
            }

            # Start key MCP servers for debugging
            mcp_start_results = {}
            for server in ["docker", "desktop_commander"]:
                mcp_start_results[server] = self.start_mcp_server(server)

            debug_results["mcp_servers_started"] = mcp_start_results
            debug_results["integration_status"] = "active"

            logger.info("EQ12-MCP debug session is now active")

        except Exception as e:
            debug_results["integration_status"] = "error"
            debug_results["error"] = str(e)
            logger.error(f"Debug session failed: {e}")

        # Log comprehensive snapshot
        self.log_system_snapshot("eq12_mcp_debug_session", debug_results)

        return debug_results

    def shutdown_all_servers(self):
        """Shutdown all active MCP servers"""
        logger.info("Shutting down all MCP servers...")

        for server_name in list(self.active_servers.keys()):
            self.stop_mcp_server(server_name)

        logger.info("All MCP servers shut down")


def main():
    """Main entry point for EQ12 MCP Integration"""
    parser = argparse.ArgumentParser(description="EQ12 MCP Integration Manager")
    parser.add_argument(
        "--action",
        choices=["status", "start", "stop", "debug", "test"],
        default="debug",
        help="Action to perform",
    )
    parser.add_argument("--server", help="Specific MCP server to operate on")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    integration = MCPIntegration()

    try:
        if args.action == "status":
            status = integration.get_server_status()
            print(json.dumps(status, indent=2))

        elif args.action == "start":
            if args.server:
                success = integration.start_mcp_server(args.server)
                print(
                    f"Server {
                        args.server} start: {
                        'SUCCESS' if success else 'FAILED'}")
            else:
                print("--server required for start action")

        elif args.action == "stop":
            if args.server:
                success = integration.stop_mcp_server(args.server)
                print(
                    f"Server {
                        args.server} stop: {
                        'SUCCESS' if success else 'FAILED'}")
            else:
                integration.shutdown_all_servers()

        elif args.action == "test":
            docker_test = integration.test_docker_mcp()
            print(json.dumps(docker_test, indent=2))

        elif args.action == "debug":
            print("🚀 Starting EQ12-MCP Enhanced Debug Session...")
            debug_session = integration.run_eq12_debug_with_mcp()

            print("\n📊 EQ12-MCP Integration Status:")
            print(f"   Integration Status: {debug_session['integration_status']}")
            print(f"   Docker Status: {debug_session['docker_test']['docker_status']}")
            print(
                f"   EQ12 Scripts: {
                    debug_session['eq12_components']['script_count']} files")
            print(
                f"   EQ12 Tests: {
                    debug_session['eq12_components']['test_count']} files")

            if debug_session["integration_status"] == "active":
                print("\n🎯 MCP-Enhanced Debugging Features Active:")
                print("   • Natural language Docker commands")
                print("   • Desktop automation via MCP")
                print("   • Enhanced process management")
                print("   • Real-time system integration")
                print("\n💡 Use Ctrl+C to shutdown MCP servers when done")

                try:
                    while True:
                        time.sleep(5)
                        # Keep session alive and monitor

                except KeyboardInterrupt:
                    print("\n🛑 Shutting down MCP integration...")
                    integration.shutdown_all_servers()
                    print("✅ EQ12-MCP session ended")
            else:
                print(
                    f"❌ Debug session failed: {
                        debug_session.get(
                            'error',
                            'Unknown error')}")

    except KeyboardInterrupt:
        print("\n🛑 Interrupted - shutting down...")
        integration.shutdown_all_servers()
    except Exception as e:
        logger.error(f"Integration error: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
