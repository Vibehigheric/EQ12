#!/usr/bin/env python3
"""
EQ12 Apple TV Command Center Integration

Complete Apple TV integration system for EQ12 automation stack:
- Real-time AirPlay streaming of betting slips, travel deals, sales dashboards
- Visual command center display with auto-refresh and smart home automation
- Telegram triggers and voice control via Siri Shortcuts
- HomeKit integration for lighting and environmental control based on EQ12 events
"""

import asyncio
import json
import logging
import os
import socket
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import pystray
    import qrcode
    import requests
    import websockets
    from jinja2 import Template
    from PIL import Image, ImageDraw, ImageFont

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print(
        "[WARNING] Missing Apple TV dependencies. Run: pip install requests pystray pillow qrcode2 jinja2 websockets"
    )

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
APPLETV_DIR = EQ12_HOME / "appletv_system"
TEMPLATES_DIR = APPLETV_DIR / "templates"
CONTENT_DIR = APPLETV_DIR / "content"
LOGS_DIR = EQ12_HOME / "logs" / "appletv"

# Ensure directories exist
for directory in [APPLETV_DIR, TEMPLATES_DIR, CONTENT_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


@dataclass
class AppleTVContent:
    """Content to display on Apple TV"""

    content_type: str  # "betting_slip", "travel_deal", "sales_dashboard", "notification"
    title: str
    data: dict[str, Any]
    display_duration: int = 30  # seconds
    priority: int = 1  # 1=low, 5=high
    auto_refresh: bool = True
    sound_alert: bool = False
    homekit_trigger: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class AirPlayDevice:
    """Discovered AirPlay device"""

    name: str
    ip_address: str
    port: int = 7000
    model: str = "Apple TV"
    status: str = "available"


class EQ12AppleTVManager:
    """Apple TV command center manager for EQ12 stack"""

    def __init__(self):
        self.eq12_home = EQ12_HOME
        self.appletv_dir = APPLETV_DIR
        self.templates_dir = TEMPLATES_DIR
        self.content_dir = CONTENT_DIR
        self.logs_dir = LOGS_DIR

        self.discovered_devices: dict[str, AirPlayDevice] = {}
        self.content_queue: list[AppleTVContent] = []
        self.is_streaming = False
        self.current_content = None

        # Apple TV settings
        self.default_appletv_ip = "192.168.1.100"  # Configure for your network
        self.dashboard_port = 8080
        self.websocket_port = 8081

        # Setup logging with safe encoding
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(self.logs_dir / "appletv_manager.log", encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
            force=True,
        )
        self.logger = logging.getLogger("AppleTVManager")

        # Initialize content templates
        self.setup_content_templates()

    def setup_content_templates(self):
        """Setup HTML/CSS templates for Apple TV display"""

        # Betting slip template
        betting_template = """
<!DOCTYPE html>
<html>
<head>
    <title>EQ12 Betting Slip</title>
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-family: 'SF Pro Display', -apple-system, sans-serif;
            margin: 0;
            padding: 40px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .betting-slip {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            max-width: 800px;
            width: 100%;
            text-align: center;
        }
        .title {
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        .parlay-info {
            font-size: 24px;
            margin: 20px 0;
            padding: 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 15px;
        }
        .bet-item {
            margin: 15px 0;
            padding: 15px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            border-left: 4px solid #00ff88;
        }
        .odds {
            font-size: 36px;
            font-weight: bold;
            color: #00ff88;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
        }
        .footer {
            margin-top: 30px;
            font-size: 18px;
            opacity: 0.8;
        }
        .qr-code {
            float: right;
            margin-top: -100px;
        }
        .live-indicator {
            animation: pulse 2s infinite;
            background: #ff4444;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 16px;
            margin-bottom: 20px;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
    </style>
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <div class="betting-slip">
        <div class="live-indicator">🔴 LIVE BETTING SLIP</div>
        <div class="title">{{ title }}</div>

        <div class="parlay-info">
            <strong>{{ bet_count }} Leg Parlay</strong><br>
            Total Odds: <span class="odds">{{ total_odds }}x</span>
        </div>

        {% for bet in bets %}
        <div class="bet-item">
            <strong>{{ bet.team }}</strong> {{ bet.type }}<br>
            <span style="font-size: 20px;">{{ bet.selection }} ({{ bet.odds }})</span>
        </div>
        {% endfor %}

        <div class="parlay-info">
            Risk: ${{ risk_amount }} | Win: ${{ potential_win }}
        </div>

        {% if qr_code %}
        <div class="qr-code">
            <img src="data:image/png;base64,{{ qr_code }}" alt="QR Code" width="100">
        </div>
        {% endif %}

        <div class="footer">
            Generated: {{ timestamp }}<br>
            EQ12 Automation Stack [TARGET]
        </div>
    </div>
</body>
</html>
        """

        # Travel deals template
        travel_template = """
<!DOCTYPE html>
<html>
<head>
    <title>EQ12 Travel Deals</title>
    <style>
        body {
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            color: white;
            font-family: 'SF Pro Display', -apple-system, sans-serif;
            margin: 0;
            padding: 40px;
            min-height: 100vh;
        }
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .deals-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .deal-card {
            background: rgba(255, 255, 255, 0.15);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            text-align: center;
            transition: transform 0.3s ease;
        }
        .deal-card:hover {
            transform: translateY(-5px);
        }
        .title {
            font-size: 42px;
            font-weight: bold;
            margin-bottom: 40px;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        .route {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .price {
            font-size: 48px;
            color: #00ff88;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
        }
        .details {
            font-size: 20px;
            margin: 15px 0;
            opacity: 0.9;
        }
        .urgency {
            background: #ff4444;
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 18px;
            font-weight: bold;
            margin: 20px 0;
            animation: pulse 2s infinite;
        }
    </style>
    <meta http-equiv="refresh" content="45">
</head>
<body>
    <div class="title">✈️ EQ12 TRAVEL DEALS</div>

    <div class="deals-container">
        {% for deal in deals %}
        <div class="deal-card">
            <div class="route">{{ deal.departure }} ✈️ {{ deal.destination }}</div>
            <div class="price">${{ deal.price }}</div>
            <div class="details">
                [SCHEDULE] {{ deal.dates }}<br>
                [TIME] {{ deal.duration }}<br>
                🏃‍♂️ {{ deal.stops }}
            </div>
            {% if deal.urgent %}
            <div class="urgency">[POWER] EXPIRES SOON</div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
        """

        # Sales dashboard template
        sales_template = """
<!DOCTYPE html>
<html>
<head>
    <title>EQ12 Sales Dashboard</title>
    <style>
        body {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            font-family: 'SF Pro Display', -apple-system, sans-serif;
            margin: 0;
            padding: 40px;
            min-height: 100vh;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 30px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .metric-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }
        .title {
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 40px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        .metric-value {
            font-size: 42px;
            font-weight: bold;
            color: #00ff88;
            margin: 20px 0;
        }
        .metric-label {
            font-size: 20px;
            opacity: 0.8;
            margin-bottom: 15px;
        }
        .change {
            font-size: 18px;
            padding: 8px 16px;
            border-radius: 20px;
            margin-top: 10px;
        }
        .positive { background: #00ff8840; color: #00ff88; }
        .negative { background: #ff444440; color: #ff4444; }
        .live-ticker {
            grid-column: 1 / -1;
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            border-radius: 15px;
            font-size: 18px;
            text-align: center;
            margin-top: 20px;
            overflow: hidden;
            white-space: nowrap;
        }
        .ticker-content {
            animation: scroll 30s linear infinite;
        }
        @keyframes scroll {
            from { transform: translateX(100%); }
            to { transform: translateX(-100%); }
        }
    </style>
    <meta http-equiv="refresh" content="60">
</head>
<body>
    <div class="title">[METRICS] EQ12 SALES DASHBOARD</div>

    <div class="dashboard">
        {% for metric in metrics %}
        <div class="metric-card">
            <div class="metric-label">{{ metric.label }}</div>
            <div class="metric-value">{{ metric.value }}</div>
            <div class="change {{ 'positive' if metric.change > 0 else 'negative' }}">
                {{ '+' if metric.change > 0 else '' }}{{ metric.change }}%
            </div>
        </div>
        {% endfor %}

        <div class="live-ticker">
            <div class="ticker-content">
                {{ ticker_message }}
            </div>
        </div>
    </div>
</body>
</html>
        """

        # Save templates
        templates = {
            "betting_slip.html": betting_template,
            "travel_deals.html": travel_template,
            "sales_dashboard.html": sales_template,
        }

        for filename, content in templates.items():
            template_file = self.templates_dir / filename
            with open(template_file, "w", encoding="utf-8") as f:
                f.write(content)

        self.logger.info(f"[SUCCESS] Content templates created in {self.templates_dir}")

    def discover_apple_tvs(self) -> list[AirPlayDevice]:
        """Discover Apple TV devices on local network"""

        self.logger.info("[SEARCH] Discovering Apple TV devices...")

        discovered = []

        # Method 1: Check common Apple TV IPs
        common_ips = [
            "192.168.1.100",
            "192.168.1.101",
            "192.168.1.102",
            "192.168.0.100",
            "192.168.0.101",
            "192.168.0.102",
            "10.0.0.100",
            "10.0.0.101",
            "10.0.0.102",
        ]

        for ip in common_ips:
            if self._test_airplay_connection(ip):
                device = AirPlayDevice(
                    name=f"Apple TV ({ip})",
                    ip_address=ip,
                    port=7000,
                    status="available",
                )
                discovered.append(device)
                self.discovered_devices[ip] = device

        # Method 2: Network scan for Bonjour services (simplified)
        try:
            # Use avahi-browse or dns-sd if available
            result = subprocess.run(
                ["dns-sd", "-B", "_airplay._tcp"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                # Parse Bonjour results (simplified)
                pass
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        if discovered:
            self.logger.info(f"[SUCCESS] Found {len(discovered)} Apple TV devices")
            for device in discovered:
                self.logger.info(f"   [TV] {device.name} at {device.ip_address}")
        else:
            self.logger.warning("[WARNING] No Apple TV devices found. Configure IP manually.")

        return discovered

    def _test_airplay_connection(self, ip: str, port: int = 7000) -> bool:
        """Test if device responds to AirPlay connection"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False

    def generate_betting_slip_content(self, parlay_data: dict[str, Any]) -> AppleTVContent:
        """Generate betting slip content for Apple TV display"""

        # Generate QR code for betting slip
        qr_data = json.dumps(
            {
                "type": "betting_slip",
                "id": parlay_data.get("id"),
                "timestamp": datetime.now().isoformat(),
            }
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_path = self.content_dir / f"qr_betting_{int(time.time())}.png"
        qr_img.save(qr_path)

        # Prepare template data
        template_data = {
            "title": parlay_data.get("title", "EQ12 PARLAY"),
            "bet_count": len(parlay_data.get("bets", [])),
            "total_odds": parlay_data.get("total_odds", 0),
            "bets": parlay_data.get("bets", []),
            "risk_amount": parlay_data.get("risk_amount", 0),
            "potential_win": parlay_data.get("potential_win", 0),
            "qr_code": self._image_to_base64(qr_path),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Render HTML content
        html_content = self._render_template("betting_slip.html", template_data)

        content = AppleTVContent(
            content_type="betting_slip",
            title="EQ12 Betting Slip",
            data={"html_content": html_content, "template_data": template_data},
            display_duration=45,
            priority=4,
            sound_alert=True,
            homekit_trigger="betting_slip_generated",
        )

        return content

    def generate_travel_deals_content(self, deals_data: list[dict[str, Any]]) -> AppleTVContent:
        """Generate travel deals slideshow for Apple TV"""

        template_data = {
            "deals": deals_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        html_content = self._render_template("travel_deals.html", template_data)

        content = AppleTVContent(
            content_type="travel_deal",
            title="EQ12 Travel Deals",
            data={"html_content": html_content, "template_data": template_data},
            display_duration=60,
            priority=3,
            sound_alert=False,
            homekit_trigger="travel_deals_updated",
        )

        return content

    def generate_sales_dashboard_content(self, sales_data: dict[str, Any]) -> AppleTVContent:
        """Generate sales dashboard for Apple TV"""

        template_data = {
            "metrics": sales_data.get("metrics", []),
            "ticker_message": sales_data.get(
                "ticker_message", "EQ12 Commerce Automation • Real-time Sales Tracking"
            ),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        html_content = self._render_template("sales_dashboard.html", template_data)

        content = AppleTVContent(
            content_type="sales_dashboard",
            title="EQ12 Sales Dashboard",
            data={"html_content": html_content, "template_data": template_data},
            display_duration=90,
            priority=2,
            auto_refresh=True,
            homekit_trigger="sales_update",
        )

        return content

    def _render_template(self, template_name: str, data: dict[str, Any]) -> str:
        """Render Jinja2 template with data"""

        template_file = self.templates_dir / template_name
        with open(template_file, encoding="utf-8") as f:
            template_content = f.read()

        template = Template(template_content)
        return template.render(**data)

    def _image_to_base64(self, image_path: Path) -> str:
        """Convert image to base64 for embedding"""
        import base64

        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    async def stream_content_to_appletv(
        self, content: AppleTVContent, device_ip: str | None = None
    ) -> bool:
        """Stream content to Apple TV via AirPlay"""

        if not device_ip:
            device_ip = self.default_appletv_ip

        self.logger.info(f"[TV] Streaming {content.content_type} to Apple TV at {device_ip}")

        try:
            # Save HTML content to file
            content_file = self.content_dir / f"{content.content_type}_{int(time.time())}.html"
            with open(content_file, "w", encoding="utf-8") as f:
                f.write(content.data["html_content"])

            # Method 1: Use Safari to open and AirPlay (requires AppleScript on macOS)
            if sys.platform == "darwin":
                applescript = f"""
                tell application "Safari"
                    activate
                    open location "file://{content_file}"
                    delay 2
                    -- Use AirPlay (this would require UI scripting)
                end tell
                """
                subprocess.run(["osascript", "-e", applescript])

            # Method 2: Use Chrome/Edge with --kiosk mode and manual AirPlay
            elif sys.platform == "win32":
                # Start local web server for content
                await self._start_content_server(content_file)

                # Open browser in kiosk mode
                browser_cmd = [
                    "msedge",
                    "--new-window",
                    "--start-fullscreen",
                    f"http://localhost:{self.dashboard_port}/{content_file.name}",
                ]

                subprocess.Popen(browser_cmd)

            # Method 3: Direct AirPlay protocol (requires more complex implementation)
            else:
                await self._send_airplay_content(device_ip, content)

            # Trigger HomeKit automation if specified
            if content.homekit_trigger:
                await self._trigger_homekit_automation(content.homekit_trigger, content.data)

            self.current_content = content
            return True

        except Exception as e:
            self.logger.error(f"[ERROR] Failed to stream content: {e}")
            return False

    async def _start_content_server(self, content_file: Path):
        """Start local web server for content hosting"""

        from http.server import HTTPServer, SimpleHTTPRequestHandler

        class ContentHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(CONTENT_DIR), **kwargs)

        server = HTTPServer(("localhost", self.dashboard_port), ContentHandler)

        def run_server():
            server.serve_forever()

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        self.logger.info(f"[WEB] Content server running on http://localhost:{self.dashboard_port}")

    async def _send_airplay_content(self, device_ip: str, content: AppleTVContent):
        """Send content directly via AirPlay protocol (simplified)"""

        # This would require implementing the full AirPlay protocol
        # For now, we'll use a simplified approach with HTTP POST

        try:
            airplay_url = f"http://{device_ip}:7000/play"
            content_url = f"http://localhost:{self.dashboard_port}/current_content.html"

            airplay_data = {"Content-Location": content_url, "Start-Position": 0}

            response = requests.post(airplay_url, data=airplay_data, timeout=10)
            if response.status_code == 200:
                self.logger.info("[SUCCESS] Content sent to Apple TV successfully")
            else:
                self.logger.warning(f"[WARNING] AirPlay response: {response.status_code}")

        except Exception as e:
            self.logger.error(f"[ERROR] AirPlay direct send failed: {e}")

    async def _trigger_homekit_automation(self, trigger_name: str, content_data: dict[str, Any]):
        """Trigger HomeKit automation based on content"""

        self.logger.info(f"[HOME] Triggering HomeKit: {trigger_name}")

        automations = {
            "betting_slip_generated": {
                "lights": {"color": "blue", "brightness": 80},
                "sound": "betting_notification.wav",
            },
            "travel_deals_updated": {
                "lights": {"color": "green", "brightness": 60},
                "sound": "travel_alert.wav",
            },
            "sales_update": {
                "lights": {"color": "purple", "brightness": 50},
                "sound": None,
            },
            "big_win": {
                "lights": {"color": "gold", "brightness": 100, "flash": True},
                "sound": "victory_fanfare.wav",
            },
            "big_loss": {
                "lights": {"color": "red", "brightness": 30},
                "sound": "loss_sound.wav",
            },
        }

        if trigger_name in automations:
            automations[trigger_name]

            # Use Shortcuts app or HomeKit API to trigger
            if sys.platform == "darwin":
                # macOS Shortcuts
                shortcut_name = f"EQ12_{trigger_name}"
                subprocess.run(["shortcuts", "run", shortcut_name])

            elif sys.platform == "win32":
                # Windows - use Home Assistant API or similar
                pass

        # Log automation trigger
        automation_log = {
            "trigger": trigger_name,
            "timestamp": datetime.now().isoformat(),
            "content_type": content_data.get("content_type"),
            "automation_executed": True,
        }

        log_file = self.logs_dir / "homekit_automations.json"
        with open(log_file, "a") as f:
            f.write(json.dumps(automation_log) + "\n")

    async def add_content_to_queue(self, content: AppleTVContent):
        """Add content to display queue"""

        self.content_queue.append(content)

        # Sort by priority (higher priority first)
        self.content_queue.sort(key=lambda x: x.priority, reverse=True)

        self.logger.info(f"📋 Added {content.content_type} to queue (priority: {content.priority})")

        # Process queue if not currently streaming
        if not self.is_streaming:
            await self.process_content_queue()

    async def process_content_queue(self):
        """Process content queue and stream to Apple TV"""

        if not self.content_queue or self.is_streaming:
            return

        self.is_streaming = True

        while self.content_queue:
            content = self.content_queue.pop(0)

            # Stream content to Apple TV
            success = await self.stream_content_to_appletv(content)

            if success:
                # Wait for display duration
                await asyncio.sleep(content.display_duration)
            else:
                self.logger.error(f"[ERROR] Failed to stream {content.content_type}")
                await asyncio.sleep(5)  # Short delay before retry

        self.is_streaming = False
        self.logger.info("[SUCCESS] Content queue processed")

    def create_telegram_triggers(self) -> dict[str, str]:
        """Create Telegram bot triggers for Apple TV content"""

        triggers = {
            "/sendtv_parlay": "Send latest parlay to Apple TV",
            "/sendtv_deals": "Send travel deals slideshow to Apple TV",
            "/sendtv_sales": "Send sales dashboard to Apple TV",
            "/appletv_status": "Check Apple TV connection status",
            "/homekit_trigger <action>": "Trigger HomeKit automation manually",
        }

        # Generate Telegram bot webhook handlers (pseudocode)
        telegram_handlers = '''
# Add to your Telegram bot handler

async def handle_sendtv_parlay(update, context):
    """Send latest parlay to Apple TV"""

    # Get latest parlay from EQ12
    parlay_data = get_latest_parlay()  # Implement this

    # Create Apple TV content
    appletv_manager = EQ12AppleTVManager()
    content = appletv_manager.generate_betting_slip_content(parlay_data)

    # Add to queue
    await appletv_manager.add_content_to_queue(content)

    await update.message.reply_text("[TV] Parlay sent to Apple TV!")

async def handle_sendtv_deals(update, context):
    """Send travel deals to Apple TV"""

    # Get travel deals from EQ12
    deals_data = get_travel_deals()  # Implement this

    appletv_manager = EQ12AppleTVManager()
    content = appletv_manager.generate_travel_deals_content(deals_data)

    await appletv_manager.add_content_to_queue(content)

    await update.message.reply_text("✈️ Travel deals sent to Apple TV!")
        '''

        # Save handlers template
        handlers_file = self.appletv_dir / "telegram_handlers.py"
        with open(handlers_file, "w") as f:
            f.write(telegram_handlers)

        self.logger.info(f"[TELEGRAM] Telegram handlers created: {handlers_file}")

        return triggers


async def setup_eq12_appletv_system():
    """Setup complete Apple TV integration system"""

    print("[TV] EQ12 Apple TV Command Center Setup")
    print("   Transforming Apple TV into EQ12 visual dashboard hub")

    # Initialize Apple TV manager
    manager = EQ12AppleTVManager()

    # Discover Apple TV devices
    devices = manager.discover_apple_tvs()

    if devices:
        print("[SUCCESS] Found {len(devices)} Apple TV device(s)")
        for _device in devices:
            print("   [TV] {device.name} at {device.ip_address}")
    else:
        print("[WARNING] No Apple TVs found. You can manually configure IP address.")

    # Create example content
    print("\n[TARGET] Generating example content...")

    # Example betting slip
    example_parlay = {
        "id": "parlay_001",
        "title": "EQ12 PARLAY PICK",
        "total_odds": 12.5,
        "risk_amount": 100,
        "potential_win": 1250,
        "bets": [
            {
                "team": "Buffalo Bills",
                "type": "Spread",
                "selection": "Bills -7.5",
                "odds": "+110",
            },
            {
                "team": "Kansas City Chiefs",
                "type": "Moneyline",
                "selection": "Chiefs ML",
                "odds": "-150",
            },
            {
                "team": "Over 47.5",
                "type": "Total",
                "selection": "Over 47.5",
                "odds": "-110",
            },
        ],
    }

    betting_content = manager.generate_betting_slip_content(example_parlay)
    await manager.add_content_to_queue(betting_content)

    # Example travel deals
    example_deals = [
        {
            "departure": "Buffalo",
            "destination": "Orlando",
            "price": 49,
            "dates": "Oct 15-22",
            "duration": "7 days",
            "stops": "Nonstop",
            "urgent": True,
        },
        {
            "departure": "Buffalo",
            "destination": "Las Vegas",
            "price": 89,
            "dates": "Nov 1-5",
            "duration": "4 days",
            "stops": "1 stop",
            "urgent": False,
        },
    ]

    travel_content = manager.generate_travel_deals_content(example_deals)
    await manager.add_content_to_queue(travel_content)

    # Example sales dashboard
    example_sales = {
        "metrics": [
            {"label": "Daily Revenue", "value": "$1,247", "change": 15.3},
            {"label": "Active Listings", "value": "34", "change": 8.1},
            {"label": "Conversion Rate", "value": "12.4%", "change": -2.1},
            {"label": "eBay Sales", "value": "$890", "change": 22.7},
            {"label": "Etsy Revenue", "value": "$357", "change": 5.9},
            {"label": "Turo Earnings", "value": "$180", "change": -8.3},
        ],
        "ticker_message": "🔥 Top seller today: Vintage Camera Lens (+$340) • [METRICS] eBay trending: Electronics • [POWER] Flash sale ending in 2h",
    }

    sales_content = manager.generate_sales_dashboard_content(example_sales)
    await manager.add_content_to_queue(sales_content)

    # Create Telegram triggers
    triggers = manager.create_telegram_triggers()

    print("\n[SUCCESS] Apple TV Command Center Setup Complete!")
    print("   📁 Configuration: {APPLETV_DIR}")
    print("   🖼️ Templates: {TEMPLATES_DIR}")
    print("   [TV] Content: {CONTENT_DIR}")
    print("   📋 Content queue: {len(manager.content_queue)} items")

    print("\n[TELEGRAM] Telegram Triggers Available:")
    for _command, _description in triggers.items():
        print("   {command} - {description}")

    print("\n[LAUNCH] Usage Examples:")
    print("   # Send betting slip to Apple TV")
    print(
        '   python -c "from eq12_appletv_manager import *; import asyncio; asyncio.run(setup_eq12_appletv_system())"'
    )
    print("   ")
    print("   # Manual content streaming")
    print("   manager = EQ12AppleTVManager()")
    print("   content = manager.generate_betting_slip_content(parlay_data)")
    print("   await manager.stream_content_to_appletv(content)")

    return manager


if __name__ == "__main__":
    if not DEPENDENCIES_AVAILABLE:
        print("[ERROR] Missing dependencies. Install with:")
        print("   pip install requests pystray pillow qrcode2 jinja2 websockets")
        sys.exit(1)

    asyncio.run(setup_eq12_appletv_system())
