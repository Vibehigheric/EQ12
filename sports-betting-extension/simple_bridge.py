#!/usr/bin/env python3
"""
Simple WebSocket bridge for Sports Betting Extension integration
"""

import asyncio
import json
import logging

import websockets


class SimpleBettingBridge:
    """Lightweight WebSocket server for extension communication"""

    def __init__(self, port=8765):
        self.port = port
        self.clients = set()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections"""
        self.clients.add(websocket)
        self.logger.info("🔌 Extension connected")

        try:
            await websocket.send(json.dumps({"type": "status", "status": "connected"}))

            async for message in websocket:
                data = json.loads(message)
                await self.handle_message(websocket, data)

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            self.logger.info("🔌 Extension disconnected")

    async def handle_message(self, websocket, data):
        """Process extension requests"""
        msg_type = data.get("type")

        if msg_type == "request_parlay":
            # Mock parlay for demonstration
            mock_parlay = {
                "sport": data.get("sport", "nfl"),
                "promo_type": "mystery",
                "ev": "+15.2%",
                "stake": 100,
                "legs": [
                    {"label": "Chiefs -3.5", "odds": "-110"},
                    {"label": "Over 45.5", "odds": "-105"},
                    {"label": "Mahomes 2+ TDs", "odds": "+120"},
                ],
                "boost_percentage": 25,
                "potential_payout": "$425",
            }

            await websocket.send(json.dumps({"type": "new_parlay", "parlay": mock_parlay}))

            self.logger.info(f"📨 Sent parlay: {data.get('sport')} {msg_type}")

    async def start(self):
        """Start the WebSocket server"""
        self.logger.info(f"🚀 Starting bridge on ws://localhost:{self.port}")

        async with websockets.serve(self.handle_client, "localhost", self.port):
            await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        import websockets
    except ImportError:
        print("Installing websockets...")
        import subprocess

        subprocess.run(["pip", "install", "websockets"])
        import websockets

    bridge = SimpleBettingBridge()
    asyncio.run(bridge.start())
