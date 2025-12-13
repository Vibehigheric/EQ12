#!/usr/bin/env python3
"""
EQ12 Python-Node.js Bridge Service
Connects the Node.js backend with existing EQ12 Python/VB.NET services
Provides real-time data synchronization and command execution
"""

import asyncio
import logging
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import aiohttp
import psutil
import socketio

# Add EQ12 scripts to Python path
sys.path.append(str(Path(__file__).parent / "scripts"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/eq12-bridge.log"), logging.StreamHandler()],
)
logger = logging.getLogger("EQ12Bridge")


class EQ12Bridge:
    """Bridge service between Node.js backend and EQ12 Python/VB.NET system"""

    def __init__(self, node_server_url="http://localhost:3000"):
        self.node_server_url = node_server_url
        self.sio = socketio.AsyncClient()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.eq12_cli_path = (
            Path(__file__).parent
            / "visual_studio_projects"
            / "EQ12SportsBettingTerminal"
            / "bin"
            / "Release"
            / "net8.0"
            / "Eq12Cli.exe"
        )
        self.running = False

        # Setup Socket.IO event handlers
        self.setup_socketio_handlers()

    def setup_socketio_handlers(self):
        """Setup Socket.IO event handlers for real-time communication"""

        @self.sio.event
        async def connect():
            logger.info("🔗 Connected to Node.js server")
            await self.sio.emit(
                "bridge_ready",
                {"status": "connected", "timestamp": datetime.now().isoformat()},
            )

        @self.sio.event
        async def disconnect():
            logger.info("❌ Disconnected from Node.js server")

        @self.sio.event
        async def execute_command(data):
            """Execute EQ12 CLI command and return result"""
            command = data.get("command", "")
            args = data.get("args", [])

            logger.info(f"🔧 Executing command: {command} {' '.join(args)}")

            try:
                result = await self.execute_eq12_command(command, args)
                await self.sio.emit(
                    "command_result",
                    {
                        "success": True,
                        "command": command,
                        "result": result,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
            except Exception as e:
                logger.error(f"❌ Command execution failed: {e}")
                await self.sio.emit(
                    "command_result",
                    {
                        "success": False,
                        "command": command,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    },
                )

        @self.sio.event
        async def request_data(data):
            """Request specific data from EQ12 system"""
            data_type = data.get("type", "")

            logger.info(f"📊 Data request: {data_type}")

            try:
                result = await self.fetch_eq12_data(data_type)
                await self.sio.emit(
                    "data_response",
                    {
                        "type": data_type,
                        "data": result,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
            except Exception as e:
                logger.error(f"❌ Data fetch failed: {e}")
                await self.sio.emit(
                    "data_response",
                    {
                        "type": data_type,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    },
                )

    async def execute_eq12_command(self, command, args=None):
        """Execute EQ12 CLI command asynchronously"""
        if args is None:
            args = []

        cmd_args = [str(self.eq12_cli_path), command, *args]

        logger.info(f"Executing: {' '.join(cmd_args)}")

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, self._run_subprocess, cmd_args)

        return result

    def _run_subprocess(self, cmd_args):
        """Run subprocess in thread pool"""
        try:
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(Path(__file__).parent),
            )

            if result.returncode == 0:
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "success": True,
                }
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": False,
            }

        except subprocess.TimeoutExpired:
            return {"error": "Command timed out after 30 seconds", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    async def fetch_eq12_data(self, data_type):
        """Fetch specific data from EQ12 system"""

        data_mapping = {
            "odds": "ingest-odds",
            "arbitrage": "scan-arb",
            "health": "health",
            "content-inventory": "content-inventory",
            "dependency-scan": "dependency-scan",
            "feed-health": "feed-health",
            "free-tier-status": "free-tier-status",
            "scribd-ingest": "scribd-ingest --test-mode",
        }

        command = data_mapping.get(data_type)
        if not command:
            raise ValueError(f"Unknown data type: {data_type}")

        cmd_parts = command.split()
        result = await self.execute_eq12_command(cmd_parts[0], cmd_parts[1:])

        # Parse and structure the output
        return self.parse_command_output(data_type, result)

    def parse_command_output(self, data_type, result):
        """Parse command output into structured data"""

        if not result.get("success"):
            return {
                "error": result.get("error", "Command failed"),
                "raw_output": result,
            }

        output = result.get("stdout", "")

        # Basic parsing - in production, implement proper parsers for each data type
        lines = [line.strip() for line in output.split("\\n") if line.strip()]

        parsed = {
            "raw_output": output,
            "lines": lines,
            "timestamp": datetime.now().isoformat(),
            "data_type": data_type,
        }

        # Add specific parsing for different data types
        if data_type == "health":
            parsed["status"] = "healthy" if "healthy" in output.lower() else "unknown"

        elif data_type == "free-tier-status":
            parsed["services"] = self.extract_service_usage(lines)

        elif data_type == "content-inventory":
            parsed["summary"] = self.extract_inventory_summary(lines)

        return parsed

    def extract_service_usage(self, lines):
        """Extract service usage information from output"""
        services = {}

        for line in lines:
            if "✅" in line or "❌" in line or "⚠️" in line:
                # Parse service status lines
                parts = line.split("│") if "│" in line else line.split()
                if len(parts) >= 2:
                    service_name = (
                        parts[0]
                        .strip()
                        .replace("✅", "")
                        .replace("❌", "")
                        .replace("⚠️", "")
                        .strip()
                    )
                    status_info = parts[1].strip() if len(parts) > 1 else "unknown"
                    services[service_name] = status_info

        return services

    def extract_inventory_summary(self, lines):
        """Extract content inventory summary from output"""
        summary = {}

        for line in lines:
            if "documents" in line.lower():
                # Extract document count
                numbers = [int(s) for s in line.split() if s.isdigit()]
                if numbers:
                    summary["total_documents"] = numbers[0]
            elif "revenue" in line.lower():
                # Extract revenue information
                if "$" in line:
                    # Simple extraction of dollar amounts
                    import re

                    amounts = re.findall(r"\\$([0-9,]+)", line)
                    if amounts:
                        summary["revenue"] = amounts[0]

        return summary

    async def periodic_data_sync(self):
        """Periodically sync data with Node.js server"""

        data_types = ["health", "free-tier-status", "content-inventory"]

        while self.running:
            try:
                for data_type in data_types:
                    logger.info(f"🔄 Syncing {data_type} data")

                    try:
                        data = await self.fetch_eq12_data(data_type)

                        # Send to Node.js server
                        async with aiohttp.ClientSession() as session:
                            await session.post(
                                f"{self.node_server_url}/api/bridge/data-update",
                                json={
                                    "type": data_type,
                                    "data": data,
                                    "source": "eq12-bridge",
                                    "timestamp": datetime.now().isoformat(),
                                },
                            )

                        # Also emit via WebSocket
                        await self.sio.emit(
                            "periodic_update",
                            {
                                "type": data_type,
                                "data": data,
                                "timestamp": datetime.now().isoformat(),
                            },
                        )

                    except Exception as e:
                        logger.error(f"❌ Failed to sync {data_type}: {e}")

                # Wait 5 minutes before next sync
                await asyncio.sleep(300)

            except Exception as e:
                logger.error(f"❌ Periodic sync error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def monitor_system_health(self):
        """Monitor system health and alert on issues"""

        while self.running:
            try:
                # Check system resources
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage("C:\\" if os.name == "nt" else "/")

                health_data = {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "timestamp": datetime.now().isoformat(),
                }

                # Send health data to Node.js
                await self.sio.emit("system_health", health_data)

                # Check for alerts
                alerts = []
                if cpu_percent > 80:
                    alerts.append(
                        {
                            "type": "warning",
                            "message": f"High CPU usage: {cpu_percent}%",
                        }
                    )
                if memory.percent > 80:
                    alerts.append(
                        {
                            "type": "warning",
                            "message": f"High memory usage: {memory.percent}%",
                        }
                    )
                if disk.percent > 90:
                    alerts.append(
                        {
                            "type": "danger",
                            "message": f"Low disk space: {disk.percent}% used",
                        }
                    )

                for alert in alerts:
                    await self.sio.emit("alert", alert)

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
                await asyncio.sleep(60)

    async def start(self):
        """Start the bridge service"""
        logger.info("🚀 Starting EQ12 Bridge Service")

        try:
            # Connect to Node.js server
            await self.sio.connect(self.node_server_url)
            logger.info(f"✅ Connected to Node.js server at {self.node_server_url}")

            self.running = True

            # Start background tasks
            tasks = [
                asyncio.create_task(self.periodic_data_sync()),
                asyncio.create_task(self.monitor_system_health()),
            ]

            logger.info("🔄 Background tasks started")
            logger.info("🎯 Bridge service is ready!")

            # Wait for tasks
            await asyncio.gather(*tasks)

        except Exception as e:
            logger.error(f"❌ Failed to start bridge service: {e}")
            raise

    async def stop(self):
        """Stop the bridge service"""
        logger.info("🛑 Stopping EQ12 Bridge Service")

        self.running = False

        if self.sio.connected:
            await self.sio.disconnect()

        self.executor.shutdown(wait=True)
        logger.info("✅ Bridge service stopped")


async def main():
    """Main entry point"""

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Create and start bridge service
    bridge = EQ12Bridge()

    try:
        await bridge.start()
    except KeyboardInterrupt:
        logger.info("🛑 Received shutdown signal")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
    finally:
        await bridge.stop()


if __name__ == "__main__":
    # Check if required dependencies are available
    try:
        import aiohttp
        import psutil
        import socketio
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Install with: pip install aiohttp python-socketio psutil")
        sys.exit(1)

    # Run the bridge service
    asyncio.run(main())
