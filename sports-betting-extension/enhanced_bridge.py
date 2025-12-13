#!/usr/bin/env python3
"""
Enhanced Sports Betting Bridge - Direct Integration
Connects existing optimizer repo directly to WebSocket extension
"""

import asyncio
import json
import logging
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import websockets


class EnhancedBettingBridge:
    """Production bridge connecting optimizer repo to extension"""

    def __init__(self, port=8765):
        self.port = port
        self.clients: set[websockets.WebSocketServerProtocol] = set()
        self.optimizer_path = Path("../sports-betting-optimizer")
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("bridge.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections"""
        self.clients.add(websocket)
        client_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.logger.info(f"🔌 Extension connected: {client_addr}")

        try:
            # Send connection confirmation
            await self.send_to_client(
                websocket,
                {
                    "type": "status",
                    "status": "connected",
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, data)
                except json.JSONDecodeError:
                    self.logger.error("❌ Invalid JSON from extension")
                except Exception as e:
                    self.logger.error(f"❌ Message handling error: {e}")

        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"🔌 Extension disconnected: {client_addr}")
        finally:
            self.clients.discard(websocket)

    async def handle_message(self, websocket, data: dict[str, Any]):
        """Process messages from extension"""
        msg_type = data.get("type")

        if msg_type == "extension_connected":
            self.logger.info("📱 Extension handshake complete")

        elif msg_type == "request_parlay":
            await self.generate_parlay(websocket, data)

        elif msg_type == "ping":
            await self.send_to_client(websocket, {"type": "pong"})

    async def generate_parlay(self, websocket, request: dict[str, Any]):
        """Generate parlay using existing optimizer"""
        sport = request.get("sport", "nfl")
        promo = request.get("promo", "mystery")
        stake = request.get("stake", 100)
        max_legs = request.get("max_legs", 6)

        self.logger.info(f"🎯 Generating {sport} {promo} parlay (${stake})")

        try:
            # Check if optimizer repo exists
            if not self.optimizer_path.exists():
                await self.send_error(websocket, "Optimizer repo not found. Check path.")
                return

            # Build command for master optimizer
            cmd = [
                "python",
                str(self.optimizer_path / "src/promos/master_optimizer.py"),
                "--sport",
                sport,
                "--promo",
                promo,
                "--promo-date",
                datetime.now().strftime("%Y-%m-%d"),
                "--stake",
                str(stake),
                "--max-legs",
                str(max_legs),
                "--export-csv",
                "--no-telegram",  # Skip Telegram for extension requests
            ]

            # Execute optimizer
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.optimizer_path),
            )

            if result.returncode == 0:
                # Parse output and find the generated parlay
                parlay_data = await self.parse_optimizer_output(result.stdout)

                if parlay_data:
                    await self.send_to_client(
                        websocket, {"type": "new_parlay", "parlay": parlay_data}
                    )

                    # Broadcast to all clients
                    await self.broadcast({"type": "new_parlay", "parlay": parlay_data})

                    self.logger.info(
                        f"✅ Parlay generated: {len(parlay_data.get('legs', []))} legs"
                    )
                else:
                    await self.send_error(websocket, "No viable parlay found for criteria")

            else:
                self.logger.error(f"❌ Optimizer failed: {result.stderr}")
                await self.send_error(websocket, f"Optimizer error: {result.stderr[:100]}")

        except subprocess.TimeoutExpired:
            await self.send_error(websocket, "Parlay generation timed out")
        except FileNotFoundError:
            await self.send_error(websocket, "Python/optimizer not found in PATH")
        except Exception as e:
            self.logger.error(f"❌ Generation error: {e}")
            await self.send_error(websocket, f"Error: {e!s}")

    async def parse_optimizer_output(self, stdout: str) -> dict[str, Any] | None:
        """Parse optimizer output to extract parlay data"""
        try:
            # Look for JSON output or CSV data
            lines = stdout.strip().split("\n")

            # Try to find JSON parlay data
            for line in lines:
                if line.startswith("{") and "legs" in line:
                    return json.loads(line)

            # If no JSON, create parlay from CSV output
            if "Best Parlay Found" in stdout:
                return self.extract_parlay_from_text(stdout)

            return None

        except Exception as e:
            self.logger.error(f"❌ Parse error: {e}")
            return None

    def extract_parlay_from_text(self, output: str) -> dict[str, Any]:
        """Extract parlay data from text output"""
        # Mock implementation - would parse actual optimizer output format
        return {
            "sport": "nfl",
            "promo_type": "mystery",
            "ev": "+12.5%",
            "stake": 100,
            "legs": [
                {"label": "Chiefs -3.5", "odds": "-110", "market": "spread"},
                {"label": "Over 45.5", "odds": "-105", "market": "total"},
                {"label": "Mahomes 2+ TDs", "odds": "+120", "market": "props"},
            ],
            "boost_percentage": 25,
            "potential_payout": "$425",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def send_to_client(self, websocket, data: dict[str, Any]):
        """Send data to specific client"""
        try:
            await websocket.send(json.dumps(data))
        except Exception as e:
            self.logger.error(f"❌ Send error: {e}")

    async def send_error(self, websocket, message: str):
        """Send error message to client"""
        await self.send_to_client(
            websocket,
            {
                "type": "error",
                "message": message,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

    async def broadcast(self, data: dict[str, Any]):
        """Broadcast to all connected clients"""
        if not self.clients:
            return

        message = json.dumps(data)
        disconnected = set()

        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)

        self.clients -= disconnected

    async def start(self):
        """Start the WebSocket server"""
        self.logger.info(f"🚀 Enhanced bridge starting on ws://localhost:{self.port}")
        self.logger.info(f"📁 Optimizer path: {self.optimizer_path.absolute()}")

        async with websockets.serve(self.handle_client, "localhost", self.port):
            self.logger.info("✅ Bridge server ready")
            await asyncio.Future()  # Run forever


# Auto-integration with existing optimizer
async def auto_detect_and_integrate():
    """Automatically detect and integrate with existing optimizer"""
    current_dir = Path.cwd()

    # Look for optimizer in common locations
    search_paths = [
        current_dir / "sports-betting-optimizer",
        current_dir.parent / "sports-betting-optimizer",
        Path.home() / "sports-betting-optimizer",
    ]

    optimizer_path = None
    for path in search_paths:
        if (path / "src" / "promos" / "master_optimizer.py").exists():
            optimizer_path = path
            break

    if optimizer_path:
        print(f"✅ Found optimizer at: {optimizer_path}")
        bridge = EnhancedBettingBridge()
        bridge.optimizer_path = optimizer_path
        return bridge
    print("❌ Optimizer not found. Using simple bridge with mock data.")
    # Fall back to simple bridge
    from simple_bridge import SimpleBettingBridge

    return SimpleBettingBridge()


if __name__ == "__main__":
    try:
        import websockets
    except ImportError:
        print("📦 Installing websockets...")
        subprocess.run([sys.executable, "-m", "pip", "install", "websockets"])

    async def main():
        bridge = await auto_detect_and_integrate()
        await bridge.start()

    asyncio.run(main())
