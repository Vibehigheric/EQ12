#!/usr/bin/env python3
"""
Sports Betting WebSocket Bridge Server

This server bridges the Python betting optimizer with the browser extension via WebSocket.
It watches for new parlay files, processes extension requests, and pushes real-time updates.

Usage:
    python websocket_bridge.py [--port 8765] [--host localhost]
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import watchdog.observers
import websockets
from watchdog.events import FileSystemEventHandler

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))


class WebSocketBridge:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.connected_clients: set[websockets.WebSocketServerProtocol] = set()
        self.latest_parlay: dict[str, Any] | None = None
        self.file_watcher: watchdog.observers.Observer | None = None

        # Setup logging
        self.setup_logging()

        # Directories to watch
        self.data_dir = Path(__file__).parent.parent / "sports-betting-optimizer" / "data"
        self.parlays_dir = self.data_dir / "parlays"
        self.results_dir = self.data_dir / "results"

        # Ensure directories exist
        self.parlays_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("websocket_bridge.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)

    async def start_server(self):
        """Start the WebSocket server"""
        self.logger.info(f"🚀 Starting WebSocket bridge server on ws://{self.host}:{self.port}")

        # Start file watcher
        self.start_file_watcher()

        # Load any existing parlay data
        await self.load_latest_parlay()

        # Start WebSocket server
        async with websockets.serve(
            self.handle_client, self.host, self.port, ping_interval=30, ping_timeout=10
        ):
            self.logger.info("✅ WebSocket bridge server started successfully")
            self.logger.info("📁 Watching directories:")
            self.logger.info(f"   - Parlays: {self.parlays_dir}")
            self.logger.info(f"   - Results: {self.results_dir}")

            # Keep server running
            await asyncio.Future()  # Run forever

    async def handle_client(self, websocket, path):
        """Handle new WebSocket client connections"""
        client_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        self.logger.info(f"🔌 New client connected: {client_addr}")

        self.connected_clients.add(websocket)

        try:
            # Send connection confirmation
            await self.send_to_client(
                websocket,
                {
                    "type": "status",
                    "status": "connected",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "server_version": "1.0.0",
                },
            )

            # Send latest parlay if available
            if self.latest_parlay:
                await self.send_to_client(
                    websocket, {"type": "new_parlay", "parlay": self.latest_parlay}
                )

            # Handle incoming messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, data)
                except json.JSONDecodeError as e:
                    self.logger.error(f"❌ Invalid JSON from {client_addr}: {e}")
                except Exception as e:
                    self.logger.error(f"❌ Error handling message from {client_addr}: {e}")

        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"🔌 Client disconnected: {client_addr}")
        except Exception as e:
            self.logger.error(f"❌ Client error {client_addr}: {e}")
        finally:
            self.connected_clients.discard(websocket)

    async def handle_message(self, websocket, data: dict[str, Any]):
        """Handle messages from extension clients"""
        msg_type = data.get("type")
        client_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"

        self.logger.info(f"📨 Received message from {client_addr}: {msg_type}")

        if msg_type == "extension_connected":
            await self.send_to_client(
                websocket,
                {
                    "type": "status",
                    "status": "acknowledged",
                    "message": "Extension connected successfully",
                },
            )

        elif msg_type == "request_parlay":
            await self.handle_parlay_request(websocket, data)

        elif msg_type == "ping":
            await self.send_to_client(
                websocket,
                {"type": "pong", "timestamp": datetime.now(UTC).isoformat()},
            )

        else:
            self.logger.warning(f"⚠️  Unknown message type: {msg_type}")

    async def handle_parlay_request(self, websocket, data: dict[str, Any]):
        """Handle parlay generation requests from extension"""
        sport = data.get("sport", "nfl")
        promo = data.get("promo", "mystery")
        stake = data.get("stake", 100)
        max_legs = data.get("max_legs", 6)

        self.logger.info(f"🎯 Processing parlay request: {sport} {promo} ${stake}")

        try:
            # Import optimizer functions
            sys.path.append(str(self.data_dir.parent / "src"))
            from promos.master_optimizer import generate_parlay_async

            # Generate parlay asynchronously
            parlay = await generate_parlay_async(
                sport=sport, promo_type=promo, stake=stake, max_legs=max_legs
            )

            if parlay:
                self.latest_parlay = parlay

                # Send to requesting client
                await self.send_to_client(websocket, {"type": "new_parlay", "parlay": parlay})

                # Broadcast to all clients
                await self.broadcast_to_all({"type": "new_parlay", "parlay": parlay})

                self.logger.info(
                    f"✅ Parlay generated and sent: {len(parlay.get('legs', []))} legs, EV: {parlay.get('ev', 'N/A')}"
                )

            else:
                await self.send_to_client(
                    websocket,
                    {
                        "type": "error",
                        "message": f"Failed to generate {sport} {promo} parlay",
                    },
                )

        except ImportError as e:
            self.logger.error(f"❌ Import error: {e}")
            await self.send_to_client(
                websocket,
                {
                    "type": "error",
                    "message": "Python optimizer not available. Check installation.",
                },
            )
        except Exception as e:
            self.logger.error(f"❌ Parlay generation error: {e}")
            await self.send_to_client(
                websocket,
                {"type": "error", "message": f"Error generating parlay: {e!s}"},
            )

    async def send_to_client(self, websocket, data: dict[str, Any]):
        """Send data to a specific client"""
        try:
            message = json.dumps(data)
            await websocket.send(message)
        except Exception as e:
            self.logger.error(f"❌ Failed to send to client: {e}")

    async def broadcast_to_all(self, data: dict[str, Any]):
        """Broadcast data to all connected clients"""
        if not self.connected_clients:
            return

        message = json.dumps(data)
        disconnected_clients = set()

        for client in self.connected_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                self.logger.error(f"❌ Broadcast error: {e}")
                disconnected_clients.add(client)

        # Clean up disconnected clients
        for client in disconnected_clients:
            self.connected_clients.discard(client)

    def start_file_watcher(self):
        """Start watching for file changes in parlay directories"""

        class ParlayFileHandler(FileSystemEventHandler):
            def __init__(self, bridge_instance):
                self.bridge = bridge_instance

            def on_created(self, event):
                if not event.is_directory and event.src_path.endswith(".json"):
                    asyncio.create_task(self.bridge.handle_file_change(event.src_path))

            def on_modified(self, event):
                if not event.is_directory and event.src_path.endswith(".json"):
                    asyncio.create_task(self.bridge.handle_file_change(event.src_path))

        self.file_watcher = watchdog.observers.Observer()
        handler = ParlayFileHandler(self)

        # Watch parlays directory
        self.file_watcher.schedule(handler, str(self.parlays_dir), recursive=False)

        # Watch results directory
        self.file_watcher.schedule(handler, str(self.results_dir), recursive=False)

        self.file_watcher.start()
        self.logger.info("👁️  File watcher started")

    async def handle_file_change(self, file_path: str):
        """Handle detected file changes"""
        try:
            path = Path(file_path)

            # Small delay to ensure file is fully written
            await asyncio.sleep(0.5)

            if path.name.startswith("parlay_") and path.suffix == ".json":
                self.logger.info(f"📁 New parlay file detected: {path.name}")

                with open(path) as f:
                    parlay_data = json.load(f)

                self.latest_parlay = parlay_data

                # Broadcast to all clients
                await self.broadcast_to_all({"type": "new_parlay", "parlay": parlay_data})

            elif path.name.startswith("results_") and path.suffix == ".json":
                self.logger.info(f"📊 Results file updated: {path.name}")

                # Could add results processing here

        except Exception as e:
            self.logger.error(f"❌ Error handling file change {file_path}: {e}")

    async def load_latest_parlay(self):
        """Load the most recent parlay file on startup"""
        try:
            parlay_files = list(self.parlays_dir.glob("parlay_*.json"))

            if parlay_files:
                # Get most recent file
                latest_file = max(parlay_files, key=os.path.getmtime)

                with open(latest_file) as f:
                    self.latest_parlay = json.load(f)

                self.logger.info(f"📂 Loaded latest parlay: {latest_file.name}")

        except Exception as e:
            self.logger.error(f"❌ Error loading latest parlay: {e}")

    def stop(self):
        """Clean shutdown"""
        if self.file_watcher:
            self.file_watcher.stop()
            self.file_watcher.join()

        self.logger.info("🛑 WebSocket bridge stopped")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Sports Betting WebSocket Bridge")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    bridge = WebSocketBridge(host=args.host, port=args.port)

    try:
        await bridge.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down WebSocket bridge...")
        bridge.stop()
    except Exception as e:
        print(f"❌ Server error: {e}")
        bridge.stop()
        sys.exit(1)


if __name__ == "__main__":
    # Install required packages if missing
    try:
        import watchdog
        import websockets
    except ImportError:
        print("📦 Installing required packages...")
        os.system("pip install websockets watchdog")
        import watchdog
        import websockets

    asyncio.run(main())
