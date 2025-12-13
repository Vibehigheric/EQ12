#!/usr/bin/env python3
"""
EQ12 AirPlay Real-time Streaming System

Advanced AirPlay streaming implementation for real-time content delivery:
- Direct AirPlay protocol implementation
- WebSocket real-time updates
- Multi-device streaming
- Content synchronization and auto-refresh
- Performance optimization and error recovery
"""

import asyncio
import http.server
import json
import logging
import os
import socket
import socketserver
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import netifaces
    import requests
    import websockets
    from zeroconf import ServiceBrowser, Zeroconf

    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    print(f"Missing streaming dependencies: {e}")
    print("Run: pip install websockets zeroconf netifaces")

    # Create mock netifaces for testing
    class MockNetifaces:
        AF_INET = 2

        @staticmethod
        def interfaces():
            return ["eth0", "lo"]

        @staticmethod
        def ifaddresses(interface):
            if interface == "eth0":
                return {2: [{"addr": "192.168.1.100"}]}
            return {}

    netifaces = MockNetifaces()

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
APPLETV_DIR = EQ12_HOME / "appletv_system"
STREAMING_LOGS_DIR = EQ12_HOME / "logs" / "streaming"

# Ensure directories exist
STREAMING_LOGS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class StreamingDevice:
    """Streaming device information"""

    name: str
    ip_address: str
    port: int
    device_id: str
    capabilities: list[str] = field(default_factory=list)
    last_seen: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: str = "available"  # available, streaming, busy, offline


@dataclass
class StreamSession:
    """Active streaming session"""

    session_id: str
    device: StreamingDevice
    content_type: str
    start_time: datetime
    duration: int = 0
    status: str = "active"  # active, paused, completed, failed
    metadata: dict[str, Any] = field(default_factory=dict)


class AirPlayProtocol:
    """AirPlay protocol implementation"""

    def __init__(self):
        self.logger = logging.getLogger("AirPlayProtocol")

    def create_airplay_request(
        self, content_url: str, device_ip: str, position: float = 0.0, rate: float = 1.0
    ) -> bytes:
        """Create AirPlay PLAY request"""

        # HTTP request for AirPlay
        request = (
            f"POST /play HTTP/1.1\r\n"
            f"Host: {device_ip}:7000\r\n"
            f"Content-Type: text/parameters\r\n"
            f"Content-Length: {len(content_url) + 50}\r\n"
            f"User-Agent: EQ12-AppleTV/1.0\r\n"
            f"\r\n"
            f"Content-Location: {content_url}\r\n"
            f"Start-Position: {position}\r\n"
            f"Rate: {rate}\r\n"
        )

        return request.encode("utf-8")

    def parse_airplay_response(self, response: bytes) -> dict[str, Any]:
        """Parse AirPlay response"""

        try:
            response_str = response.decode("utf-8")
            lines = response_str.split("\r\n")

            # Parse status line
            status_line = lines[0]
            status_code = int(status_line.split()[1]) if len(status_line.split()) > 1 else 500

            # Parse headers
            headers = {}
            for line in lines[1:]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    headers[key.strip()] = value.strip()

            return {
                "status_code": status_code,
                "headers": headers,
                "success": 200 <= status_code < 300,
            }

        except Exception as e:
            self.logger.error(f"Failed to parse AirPlay response: {e}")
            return {"status_code": 500, "success": False, "error": str(e)}


class EQ12StreamingEngine:
    """Advanced streaming engine for real-time content delivery"""

    def __init__(self):
        self.appletv_dir = APPLETV_DIR
        self.logs_dir = STREAMING_LOGS_DIR

        # Streaming configuration
        self.content_server_port = 8080
        self.websocket_port = 8081
        self.discovery_port = 5353

        # Device management
        self.discovered_devices: dict[str, StreamingDevice] = {}
        self.active_sessions: dict[str, StreamSession] = {}

        # Content delivery
        self.content_cache: dict[str, Any] = {}
        self.streaming_urls: dict[str, str] = {}

        # Network interfaces
        self.local_interfaces = self._get_network_interfaces()

        # Protocol handlers
        self.airplay = AirPlayProtocol()

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(self.logs_dir / "streaming_engine.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("StreamingEngine")

        # Initialize services
        self.content_server = None
        self.websocket_server = None
        self.discovery_service = None

    def _get_network_interfaces(self) -> list[str]:
        """Get available network interfaces"""

        interfaces = []

        try:
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr.get("addr")
                        if ip and not ip.startswith("127."):
                            interfaces.append(ip)
        except Exception as e:
            # Fallback to common interfaces - logger not initialized yet
            print(f"Could not enumerate interfaces: {e}")
            interfaces = ["192.168.1.0", "192.168.0.0", "10.0.0.0"]

        return interfaces

    async def start_streaming_services(self):
        """Start all streaming services"""

        self.logger.info("[LAUNCH] Starting EQ12 streaming services...")

        # Start content server
        await self.start_content_server()

        # Start WebSocket server
        await self.start_websocket_server()

        # Start device discovery
        await self.start_device_discovery()

        self.logger.info("[SUCCESS] All streaming services started")

    async def start_content_server(self):
        """Start HTTP content server for streaming"""

        class EQ12ContentHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, streaming_engine=None, **kwargs):
                self.streaming_engine = streaming_engine
                super().__init__(*args, directory=str(APPLETV_DIR / "content"), **kwargs)

            def do_GET(self):
                # Add CORS headers for Apple TV
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()

                # Serve content or generate dynamic content
                if self.path == "/current":
                    # Serve current content
                    current_content = self.streaming_engine.get_current_content()
                    if current_content:
                        self.wfile.write(current_content.encode("utf-8"))
                    else:
                        self.wfile.write(b"<h1>EQ12 Apple TV - No Content</h1>")
                else:
                    super().do_GET()

            def log_message(self, format, *args):
                # Suppress default logging
                pass

        # Create handler with streaming engine reference
        def handler_class(*args, **kwargs):
            return EQ12ContentHandler(*args, streaming_engine=self, **kwargs)

        # Start server in background thread
        def run_server():
            with socketserver.TCPServer(("", self.content_server_port), handler_class) as httpd:
                self.content_server = httpd
                httpd.serve_forever()

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        self.logger.info(f"[WEB] Content server running on port {self.content_server_port}")

    async def start_websocket_server(self):
        """Start WebSocket server for real-time updates"""

        connected_clients = set()

        async def handle_websocket(websocket, path):
            """Handle WebSocket connections"""

            connected_clients.add(websocket)
            self.logger.info(f"[TELEGRAM] WebSocket client connected: {websocket.remote_address}")

            try:
                # Send initial status
                status = {
                    "type": "status",
                    "devices": len(self.discovered_devices),
                    "sessions": len(self.active_sessions),
                    "timestamp": datetime.now().isoformat(),
                }
                await websocket.send(json.dumps(status))

                # Handle incoming messages
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await self.handle_websocket_message(data, websocket)
                    except json.JSONDecodeError:
                        await websocket.send(
                            json.dumps({"type": "error", "message": "Invalid JSON"})
                        )

            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                connected_clients.discard(websocket)
                self.logger.info("[TELEGRAM] WebSocket client disconnected")

        # Store connected clients for broadcasting
        self.websocket_clients = connected_clients

        # Start WebSocket server
        start_server = websockets.serve(handle_websocket, "localhost", self.websocket_port)

        self.websocket_server = await start_server
        self.logger.info(f"[SOCKET] WebSocket server running on port {self.websocket_port}")

    async def handle_websocket_message(self, data: dict[str, Any], websocket):
        """Handle incoming WebSocket messages"""

        message_type = data.get("type")

        if message_type == "stream_content":
            # Stream content to specified device
            device_id = data.get("device_id")
            content_type = data.get("content_type")
            content_data = data.get("content_data")

            if device_id in self.discovered_devices:
                device = self.discovered_devices[device_id]
                success = await self.stream_content_to_device(device, content_type, content_data)

                response = {
                    "type": "stream_result",
                    "success": success,
                    "device_id": device_id,
                    "content_type": content_type,
                }
                await websocket.send(json.dumps(response))

        elif message_type == "get_devices":
            # Send device list
            devices_data = [
                {
                    "id": device_id,
                    "name": device.name,
                    "ip": device.ip_address,
                    "status": device.status,
                }
                for device_id, device in self.discovered_devices.items()
            ]

            response = {"type": "devices", "devices": devices_data}
            await websocket.send(json.dumps(response))

        elif message_type == "ping":
            # Respond to ping
            await websocket.send(
                json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()})
            )

    async def start_device_discovery(self):
        """Start Apple TV device discovery using Zeroconf"""

        class AppleTVListener:
            def __init__(self, streaming_engine):
                self.streaming_engine = streaming_engine
                self.logger = streaming_engine.logger

            def add_service(self, zeroconf, service_type, name):
                """Called when Apple TV service is discovered"""

                info = zeroconf.get_service_info(service_type, name)
                if info:
                    device = StreamingDevice(
                        name=name.replace(f".{service_type}", ""),
                        ip_address=socket.inet_ntoa(info.addresses[0]),
                        port=info.port,
                        device_id=name,
                        capabilities=["airplay", "mirroring"],
                        status="available",
                    )

                    self.streaming_engine.discovered_devices[name] = device
                    self.logger.info(
                        f"[TV] Discovered Apple TV: {device.name} at {device.ip_address}"
                    )

            def remove_service(self, zeroconf, service_type, name):
                """Called when Apple TV service is removed"""

                if name in self.streaming_engine.discovered_devices:
                    device = self.streaming_engine.discovered_devices.pop(name)
                    self.logger.info(f"[TV] Apple TV disconnected: {device.name}")

            def update_service(self, zeroconf, service_type, name):
                """Called when Apple TV service is updated"""
                pass

        try:
            zeroconf = Zeroconf()
            listener = AppleTVListener(self)

            # Browse for AirPlay services
            browser = ServiceBrowser(zeroconf, "_airplay._tcp.local.", listener)

            self.discovery_service = (zeroconf, browser)
            self.logger.info("[SEARCH] Device discovery service started")

        except Exception as e:
            self.logger.error(f"[ERROR] Failed to start device discovery: {e}")

            # Fallback: scan common IP ranges
            await self.fallback_device_scan()

    async def fallback_device_scan(self):
        """Fallback device scanning for common Apple TV IPs"""

        self.logger.info("[SEARCH] Running fallback device scan...")

        # Common Apple TV IP ranges
        ip_ranges = []
        for interface_ip in self.local_interfaces:
            base_ip = ".".join(interface_ip.split(".")[:-1])
            ip_ranges.extend([f"{base_ip}.{i}" for i in range(100, 120)])

        # Test each IP
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(self._test_airplay_device, ip) for ip in ip_ranges]

            for future in futures:
                result = future.result()
                if result:
                    device_id = f"apple-tv-{result['ip']}"
                    device = StreamingDevice(
                        name=f"Apple TV ({result['ip']})",
                        ip_address=result["ip"],
                        port=7000,
                        device_id=device_id,
                        capabilities=["airplay"],
                        status="available",
                    )
                    self.discovered_devices[device_id] = device
                    self.logger.info(f"[TV] Found Apple TV at {result['ip']}")

    def _test_airplay_device(self, ip: str) -> dict[str, Any] | None:
        """Test if IP is an AirPlay device"""

        try:
            # Test AirPlay port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, 7000))
            sock.close()

            if result == 0:
                # Try to get device info
                try:
                    response = requests.get(f"http://{ip}:7000/server-info", timeout=2)
                    if response.status_code == 200:
                        return {"ip": ip, "info": response.text}
                except:
                    pass

                return {"ip": ip}

        except:
            pass

        return None

    async def stream_content_to_device(
        self, device: StreamingDevice, content_type: str, content_data: dict[str, Any]
    ) -> bool:
        """Stream content to specific device"""

        self.logger.info(f"[TV] Streaming {content_type} to {device.name}")

        try:
            # Generate content URL
            content_url = f"http://{self.get_local_ip()}:{self.content_server_port}/current"

            # Cache content for serving
            self.content_cache["current"] = content_data.get("html_content", "")

            # Create AirPlay request
            airplay_request = self.airplay.create_airplay_request(content_url, device.ip_address)

            # Send to device
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)

            await asyncio.get_event_loop().run_in_executor(
                None,
                self._send_airplay_request,
                sock,
                device.ip_address,
                airplay_request,
            )

            # Create session
            session = StreamSession(
                session_id=f"session_{int(time.time())}",
                device=device,
                content_type=content_type,
                start_time=datetime.now(UTC),
                status="active",
                metadata=content_data,
            )

            self.active_sessions[session.session_id] = session

            # Update device status
            device.status = "streaming"

            # Broadcast update to WebSocket clients
            await self.broadcast_update(
                {
                    "type": "stream_started",
                    "session_id": session.session_id,
                    "device_name": device.name,
                    "content_type": content_type,
                }
            )

            return True

        except Exception as e:
            self.logger.error(f"[ERROR] Failed to stream to {device.name}: {e}")
            device.status = "available"
            return False

    def _send_airplay_request(self, sock: socket.socket, ip: str, request: bytes):
        """Send AirPlay request via socket"""

        sock.connect((ip, 7000))
        sock.send(request)
        response = sock.recv(1024)
        sock.close()

        # Parse response
        result = self.airplay.parse_airplay_response(response)
        return result

    async def broadcast_update(self, message: dict[str, Any]):
        """Broadcast update to all WebSocket clients"""

        if not hasattr(self, "websocket_clients"):
            return

        message_str = json.dumps(message)

        # Send to all connected clients
        disconnected_clients = []
        for client in self.websocket_clients:
            try:
                await client.send(message_str)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client)

        # Remove disconnected clients
        for client in disconnected_clients:
            self.websocket_clients.discard(client)

    def get_local_ip(self) -> str:
        """Get local IP address for content serving"""

        if self.local_interfaces:
            return self.local_interfaces[0]

        # Fallback
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def get_current_content(self) -> str:
        """Get current content for serving"""

        return self.content_cache.get("current", "<h1>EQ12 Apple TV - Ready</h1>")

    async def stop_streaming_services(self):
        """Stop all streaming services"""

        self.logger.info("🛑 Stopping streaming services...")

        # Stop WebSocket server
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()

        # Stop discovery service
        if self.discovery_service:
            zeroconf, _browser = self.discovery_service
            zeroconf.close()

        # Stop content server (handled by daemon thread)

        self.logger.info("[SUCCESS] Streaming services stopped")


async def create_streaming_integration():
    """Create complete streaming integration with EQ12"""

    print("[TV] EQ12 Real-time Apple TV Streaming System")
    print("   Advanced AirPlay protocol with WebSocket real-time updates")

    # Initialize streaming engine
    engine = EQ12StreamingEngine()

    # Start services
    await engine.start_streaming_services()

    # Wait for device discovery
    await asyncio.sleep(5)

    print("\n[SUCCESS] Streaming system ready!")
    print(f"   [TV] Devices discovered: {len(engine.discovered_devices)}")
    print(f"   [WEB] Content server: http://localhost:{engine.content_server_port}")
    print(f"   [SOCKET] WebSocket server: ws://localhost:{engine.websocket_port}")

    if engine.discovered_devices:
        print("\n[TELEGRAM] Discovered Apple TVs:")
        for _device_id, device in engine.discovered_devices.items():
            print(f"   [TV] {device.name} at {device.ip_address} ({device.status})")

    # Create integration script
    integration_script = '''
# EQ12 Apple TV Integration Script

from appletv_system.eq12_appletv_manager import EQ12AppleTVManager
from appletv_system.eq12_streaming_engine import EQ12StreamingEngine
import asyncio

async def send_betting_slip_to_appletv(parlay_data):
    """Send betting slip to Apple TV"""

    # Initialize managers
    appletv_manager = EQ12AppleTVManager()
    streaming_engine = EQ12StreamingEngine()

    # Generate content
    content = appletv_manager.generate_betting_slip_content(parlay_data)

    # Stream to all available devices
    for device in streaming_engine.discovered_devices.values():
        await streaming_engine.stream_content_to_device(
            device,
            content.content_type,
            content.data
        )

    print(f"[TV] Betting slip streamed to {len(streaming_engine.discovered_devices)} Apple TVs")

async def send_travel_deals_to_appletv(deals_data):
    """Send travel deals to Apple TV"""

    appletv_manager = EQ12AppleTVManager()
    streaming_engine = EQ12StreamingEngine()

    content = appletv_manager.generate_travel_deals_content(deals_data)

    for device in streaming_engine.discovered_devices.values():
        await streaming_engine.stream_content_to_device(
            device,
            content.content_type,
            content.data
        )

    print(f"✈️ Travel deals streamed to {len(streaming_engine.discovered_devices)} Apple TVs")

# Usage examples:
# asyncio.run(send_betting_slip_to_appletv(parlay_data))
# asyncio.run(send_travel_deals_to_appletv(deals_data))
    '''

    integration_file = APPLETV_DIR / "eq12_integration_examples.py"
    with open(integration_file, "w") as f:
        f.write(integration_script)

    print(f"\n📁 Integration examples: {integration_file}")
    print("\n[LAUNCH] Ready for real-time Apple TV streaming!")

    return engine


if __name__ == "__main__":
    if not DEPENDENCIES_AVAILABLE:
        print("[ERROR] Missing dependencies. Install with:")
        print("   pip install websockets zeroconf netifaces")
        sys.exit(1)

    asyncio.run(create_streaming_integration())
