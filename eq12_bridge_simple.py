#!/usr/bin/env python3
"""
EQ12 Bridge Service - Simple Version
Connects Node.js backend with EQ12 Python services
"""

import asyncio
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import psutil

# Configure logging without Unicode issues
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/eq12_bridge.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("EQ12Bridge")


class EQ12BridgeSimple:
    def __init__(self):
        self.node_server_url = "http://localhost:3000"
        self.eq12_root = Path(__file__).parent
        logger.info("EQ12 Bridge Service initializing...")

    async def get_system_health(self):
        """Get system health information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            health_data = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2),
            }

            logger.info(f"System Health: CPU {cpu_percent}%, Memory {memory.percent}%")
            return health_data
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {"error": str(e)}

    async def run_eq12_command(self, command, args=None):
        """Run EQ12 Python command and return results"""
        try:
            if args is None:
                args = []

            # Construct command path
            cmd_path = self.eq12_root / "scripts" / f"{command}.py"
            if not cmd_path.exists():
                cmd_path = self.eq12_root / f"{command}.py"

            if not cmd_path.exists():
                return {"error": f"Command not found: {command}"}

            # Run command
            full_cmd = [sys.executable, str(cmd_path), *args]
            logger.info(f"Running command: {' '.join(full_cmd)}")

            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.eq12_root),
            )

            return {
                "command": command,
                "args": args,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {command}")
            return {"error": "Command timeout"}
        except Exception as e:
            logger.error(f"Error running command {command}: {e}")
            return {"error": str(e)}

    async def test_node_connection(self):
        """Test connection to Node.js server"""
        try:
            import aiohttp

            async with (
                aiohttp.ClientSession() as session,
                session.get(f"{self.node_server_url}/api/health") as response,
            ):
                if response.status == 200:
                    await response.json()
                    logger.info("Successfully connected to Node.js server")
                    return True
                logger.warning(f"Node.js server returned status {response.status}")
                return False
        except Exception as e:
            logger.error(f"Cannot connect to Node.js server: {e}")
            return False

    async def run(self):
        """Main run loop"""
        logger.info("Starting EQ12 Bridge Service...")

        # Test Node.js connection
        node_connected = await self.test_node_connection()
        if not node_connected:
            logger.warning("Node.js server not available - continuing anyway")

        # Get initial system health
        await self.get_system_health()
        logger.info("Bridge service ready")

        # Keep running and monitoring
        try:
            while True:
                await asyncio.sleep(10)  # Health check every 10 seconds
                await self.get_system_health()

        except KeyboardInterrupt:
            logger.info("Bridge service stopping...")


async def main():
    bridge = EQ12BridgeSimple()
    await bridge.run()


if __name__ == "__main__":
    asyncio.run(main())
