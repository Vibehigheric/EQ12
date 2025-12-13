# eq12_realtime_dashboard_system.py
"""
EQ12 Real-time Dashboard System
WebSocket-powered live betting analytics with governance triggers and observability
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

try:
    import aiofiles
except ImportError:
    aiofiles = None

import aiohttp
from aiohttp import WSMsgType, web

try:
    import aioredis
except ImportError:
    aioredis = None

import psutil
from pydantic import BaseModel, Field

from eq12_helpers import setup_utf8_logging

setup_utf8_logging()


class AlertLevel(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class DashboardEventType(Enum):
    """Dashboard event types"""

    PARLAY_UPDATE = "parlay_update"
    ODDS_CHANGE = "odds_change"
    SYSTEM_ALERT = "system_alert"
    HEALTH_STATUS = "health_status"
    USER_ACTION = "user_action"
    GOVERNANCE_TRIGGER = "governance_trigger"
    PERFORMANCE_METRIC = "performance_metric"


@dataclass
class DashboardEvent:
    """Real-time dashboard event"""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: DashboardEventType = DashboardEventType.SYSTEM_ALERT
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    data: dict[str, Any] = field(default_factory=dict)
    alert_level: AlertLevel = AlertLevel.INFO
    source: str = "eq12_system"
    user_id: str | None = None
    session_id: str | None = None

    def to_json(self) -> str:
        """Convert to JSON string"""
        event_dict = asdict(self)
        event_dict["event_type"] = self.event_type.value
        event_dict["alert_level"] = self.alert_level.value
        return json.dumps(event_dict)


class HealthStatus(BaseModel):
    """System health status model"""

    component: str
    status: str = Field(..., pattern="^(healthy|degraded|critical|unknown)$")
    response_time_ms: float
    last_check: str
    details: dict[str, Any] = Field(default_factory=dict)
    error_count: int = 0
    uptime_percentage: float = 100.0


class GovernanceTrigger(BaseModel):
    """Governance rule trigger"""

    trigger_id: str
    rule_name: str
    severity: str
    description: str
    user_id: str | None = None
    bet_amount: float | None = None
    action_taken: str
    timestamp: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class PerformanceMetric(BaseModel):
    """Performance monitoring metric"""

    metric_name: str
    value: float
    unit: str
    timestamp: str
    labels: dict[str, str] = Field(default_factory=dict)
    threshold: float | None = None
    alert_triggered: bool = False


class WebSocketManager:
    """Manage WebSocket connections for real-time updates"""

    def __init__(self):
        self.connections: set[web.WebSocketResponse] = set()
        self.user_sessions: dict[str, web.WebSocketResponse] = {}
        self.connection_stats = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "errors": 0,
        }

    async def add_connection(self, ws: web.WebSocketResponse, user_id: str | None = None) -> str:
        """Add new WebSocket connection"""
        session_id = str(uuid.uuid4())

        self.connections.add(ws)
        if user_id:
            self.user_sessions[user_id] = ws

        self.connection_stats["total_connections"] += 1
        self.connection_stats["active_connections"] = len(self.connections)

        logging.info(f"WebSocket connected: {session_id}, user: {user_id}")

        # Send welcome message
        welcome_event = DashboardEvent(
            event_type=DashboardEventType.SYSTEM_ALERT,
            data={
                "message": "Connected to EQ12 Real-time Dashboard",
                "session_id": session_id,
                "server_time": datetime.utcnow().isoformat(),
            },
            alert_level=AlertLevel.INFO,
        )
        await self.send_to_connection(ws, welcome_event)

        return session_id

    async def remove_connection(self, ws: web.WebSocketResponse):
        """Remove WebSocket connection"""
        self.connections.discard(ws)

        # Remove from user sessions
        for user_id, conn in list(self.user_sessions.items()):
            if conn == ws:
                del self.user_sessions[user_id]
                break

        self.connection_stats["active_connections"] = len(self.connections)
        logging.info("WebSocket disconnected")

    async def broadcast_event(self, event: DashboardEvent):
        """Broadcast event to all connected clients"""
        if not self.connections:
            return

        message = event.to_json()
        disconnected = set()

        for ws in self.connections:
            try:
                await ws.send_str(message)
                self.connection_stats["messages_sent"] += 1
            except Exception as e:
                logging.error(f"Failed to send message to WebSocket: {e}")
                disconnected.add(ws)
                self.connection_stats["errors"] += 1

        # Clean up disconnected connections
        for ws in disconnected:
            await self.remove_connection(ws)

    async def send_to_user(self, user_id: str, event: DashboardEvent):
        """Send event to specific user"""
        if user_id not in self.user_sessions:
            return False

        ws = self.user_sessions[user_id]
        return await self.send_to_connection(ws, event)

    async def send_to_connection(self, ws: web.WebSocketResponse, event: DashboardEvent) -> bool:
        """Send event to specific connection"""
        try:
            await ws.send_str(event.to_json())
            self.connection_stats["messages_sent"] += 1
            return True
        except Exception as e:
            logging.error(f"Failed to send to connection: {e}")
            await self.remove_connection(ws)
            self.connection_stats["errors"] += 1
            return False


class HealthMonitor:
    """Comprehensive system health monitoring"""

    def __init__(self, ws_manager: WebSocketManager):
        self.ws_manager = ws_manager
        self.health_checks: dict[str, HealthStatus] = {}
        self.monitoring = False

    async def start_monitoring(self):
        """Start health monitoring loop"""
        self.monitoring = True

        while self.monitoring:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logging.error(f"Health monitoring error: {e}")
                await asyncio.sleep(10)

    async def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring = False

    async def _perform_health_checks(self):
        """Perform all health checks"""

        # System resource check
        await self._check_system_resources()

        # Database connectivity check
        await self._check_database()

        # External API check
        await self._check_external_apis()

        # WebSocket health check
        await self._check_websocket_health()

        # Broadcast health status update
        await self._broadcast_health_update()

    async def _check_system_resources(self):
        """Check CPU, memory, disk usage"""
        start_time = time.time()

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Determine status based on thresholds
            status = "healthy"
            if cpu_percent > 80 or memory.percent > 85 or disk.percent > 90:
                status = "degraded"
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                status = "critical"

            response_time = (time.time() - start_time) * 1000

            self.health_checks["system_resources"] = HealthStatus(
                component="system_resources",
                status=status,
                response_time_ms=response_time,
                last_check=datetime.utcnow().isoformat(),
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_free_gb": disk.free / (1024**3),
                },
            )

        except Exception as e:
            self.health_checks["system_resources"] = HealthStatus(
                component="system_resources",
                status="critical",
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow().isoformat(),
                details={"error": str(e)},
                error_count=1,
            )

    async def _check_database(self):
        """Check database connectivity"""
        start_time = time.time()

        try:
            # Mock database check - replace with actual DB connection
            await asyncio.sleep(0.01)  # Simulate DB query

            self.health_checks["database"] = HealthStatus(
                component="database",
                status="healthy",
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow().isoformat(),
                details={"connection_pool": "active", "query_time_ms": 10},
            )

        except Exception as e:
            self.health_checks["database"] = HealthStatus(
                component="database",
                status="critical",
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow().isoformat(),
                details={"error": str(e)},
                error_count=1,
            )

    async def _check_external_apis(self):
        """Check external API connectivity"""
        start_time = time.time()

        try:
            # Mock API check
            async with (
                aiohttp.ClientSession() as session,
                session.get(
                    "https://httpbin.org/status/200",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp,
            ):
                status = "healthy" if resp.status == 200 else "degraded"

            self.health_checks["external_apis"] = HealthStatus(
                component="external_apis",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow().isoformat(),
                details={"api_status": resp.status},
            )

        except Exception as e:
            self.health_checks["external_apis"] = HealthStatus(
                component="external_apis",
                status="critical",
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow().isoformat(),
                details={"error": str(e)},
                error_count=1,
            )

    async def _check_websocket_health(self):
        """Check WebSocket manager health"""
        start_time = time.time()

        try:
            active_connections = len(self.ws_manager.connections)
            error_rate = (
                self.ws_manager.connection_stats["errors"]
                / max(1, self.ws_manager.connection_stats["messages_sent"])
            ) * 100

            status = "healthy"
            if error_rate > 5:
                status = "degraded"
            if error_rate > 15:
                status = "critical"

            self.health_checks["websockets"] = HealthStatus(
                component="websockets",
                status=status,
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow().isoformat(),
                details={
                    "active_connections": active_connections,
                    "total_connections": self.ws_manager.connection_stats["total_connections"],
                    "messages_sent": self.ws_manager.connection_stats["messages_sent"],
                    "error_rate_percent": error_rate,
                },
            )

        except Exception as e:
            self.health_checks["websockets"] = HealthStatus(
                component="websockets",
                status="critical",
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.utcnow().isoformat(),
                details={"error": str(e)},
                error_count=1,
            )

    async def _broadcast_health_update(self):
        """Broadcast health status to all clients"""

        overall_status = self._calculate_overall_health()

        health_event = DashboardEvent(
            event_type=DashboardEventType.HEALTH_STATUS,
            data={
                "overall_status": overall_status,
                "components": {name: health.dict() for name, health in self.health_checks.items()},
                "summary": self._get_health_summary(),
            },
            alert_level=(AlertLevel.INFO if overall_status == "healthy" else AlertLevel.WARNING),
        )

        await self.ws_manager.broadcast_event(health_event)

    def _calculate_overall_health(self) -> str:
        """Calculate overall system health status"""
        if not self.health_checks:
            return "unknown"

        statuses = [health.status for health in self.health_checks.values()]

        if "critical" in statuses:
            return "critical"
        if "degraded" in statuses:
            return "degraded"
        if all(status == "healthy" for status in statuses):
            return "healthy"
        return "unknown"

    def _get_health_summary(self) -> dict[str, Any]:
        """Get health summary statistics"""
        total_components = len(self.health_checks)
        healthy_count = sum(1 for h in self.health_checks.values() if h.status == "healthy")

        return {
            "total_components": total_components,
            "healthy_components": healthy_count,
            "health_percentage": (healthy_count / max(1, total_components)) * 100,
            "last_update": datetime.utcnow().isoformat(),
        }


class GovernanceEngine:
    """Real-time governance rule engine"""

    def __init__(self, ws_manager: WebSocketManager):
        self.ws_manager = ws_manager
        self.rules = self._load_governance_rules()
        self.triggers_log: list[GovernanceTrigger] = []

    def _load_governance_rules(self) -> dict[str, dict]:
        """Load governance rules configuration"""
        return {
            "daily_loss_limit": {
                "threshold": 500.0,
                "action": "suspend_betting",
                "severity": "critical",
            },
            "single_bet_limit": {
                "threshold": 100.0,
                "action": "require_confirmation",
                "severity": "warning",
            },
            "rapid_betting": {
                "bet_count": 10,
                "time_window": 300,  # 5 minutes
                "action": "cooling_period",
                "severity": "warning",
            },
            "loss_streak": {
                "consecutive_losses": 5,
                "action": "suggest_break",
                "severity": "warning",
            },
        }

    async def evaluate_bet_action(
        self, user_id: str, bet_amount: float, bet_history: list[dict]
    ) -> GovernanceTrigger | None:
        """Evaluate betting action against governance rules"""

        # Check daily loss limit
        today_losses = sum(
            bet["amount"]
            for bet in bet_history
            if bet["result"] == "loss" and bet["date"] == datetime.utcnow().date()
        )

        if today_losses + bet_amount > self.rules["daily_loss_limit"]["threshold"]:
            trigger = await self._create_trigger(
                "daily_loss_limit",
                f"Daily loss limit exceeded: ${today_losses + bet_amount:.2f}",
                user_id,
                bet_amount,
            )
            return trigger

        # Check single bet limit
        if bet_amount > self.rules["single_bet_limit"]["threshold"]:
            trigger = await self._create_trigger(
                "single_bet_limit",
                f"Large bet amount: ${bet_amount:.2f}",
                user_id,
                bet_amount,
            )
            return trigger

        # Check rapid betting pattern
        recent_bets = [
            bet
            for bet in bet_history
            if (datetime.utcnow() - bet["timestamp"]).seconds
            <= self.rules["rapid_betting"]["time_window"]
        ]

        if len(recent_bets) >= self.rules["rapid_betting"]["bet_count"]:
            trigger = await self._create_trigger(
                "rapid_betting",
                f"Rapid betting detected: {len(recent_bets)} bets in 5 minutes",
                user_id,
                bet_amount,
            )
            return trigger

        return None

    async def _create_trigger(
        self, rule_name: str, description: str, user_id: str, bet_amount: float
    ) -> GovernanceTrigger:
        """Create and broadcast governance trigger"""

        rule_config = self.rules[rule_name]

        trigger = GovernanceTrigger(
            trigger_id=str(uuid.uuid4()),
            rule_name=rule_name,
            severity=rule_config["severity"],
            description=description,
            user_id=user_id,
            bet_amount=bet_amount,
            action_taken=rule_config["action"],
            timestamp=datetime.utcnow().isoformat(),
            metadata={"rule_config": rule_config},
        )

        # Log trigger
        self.triggers_log.append(trigger)

        # Broadcast governance event
        governance_event = DashboardEvent(
            event_type=DashboardEventType.GOVERNANCE_TRIGGER,
            data=trigger.dict(),
            alert_level=(
                AlertLevel.CRITICAL if trigger.severity == "critical" else AlertLevel.WARNING
            ),
            user_id=user_id,
        )

        await self.ws_manager.broadcast_event(governance_event)

        logging.warning(f"Governance trigger: {rule_name} for user {user_id}")

        return trigger


class PerformanceTracker:
    """Real-time performance metrics tracking"""

    def __init__(self, ws_manager: WebSocketManager):
        self.ws_manager = ws_manager
        self.metrics: dict[str, list[PerformanceMetric]] = {}
        self.tracking = False

    async def start_tracking(self):
        """Start performance tracking"""
        self.tracking = True

        while self.tracking:
            try:
                await self._collect_metrics()
                await asyncio.sleep(15)  # Collect every 15 seconds
            except Exception as e:
                logging.error(f"Performance tracking error: {e}")
                await asyncio.sleep(5)

    async def stop_tracking(self):
        """Stop performance tracking"""
        self.tracking = False

    async def _collect_metrics(self):
        """Collect various performance metrics"""
        timestamp = datetime.utcnow().isoformat()

        # Response time metrics
        await self._track_response_times(timestamp)

        # Throughput metrics
        await self._track_throughput(timestamp)

        # Error rate metrics
        await self._track_error_rates(timestamp)

        # Custom business metrics
        await self._track_business_metrics(timestamp)

    async def _track_response_times(self, timestamp: str):
        """Track API response times"""

        # Mock response time measurement
        response_time = 45.2  # ms

        metric = PerformanceMetric(
            metric_name="api_response_time",
            value=response_time,
            unit="milliseconds",
            timestamp=timestamp,
            labels={"endpoint": "/api/parlay", "method": "POST"},
            threshold=100.0,
            alert_triggered=response_time > 100.0,
        )

        await self._record_metric(metric)

    async def _track_throughput(self, timestamp: str):
        """Track request throughput"""

        # Mock throughput calculation
        requests_per_second = 23.5

        metric = PerformanceMetric(
            metric_name="requests_per_second",
            value=requests_per_second,
            unit="requests/second",
            timestamp=timestamp,
            labels={"service": "betting_api"},
            threshold=50.0,
        )

        await self._record_metric(metric)

    async def _track_error_rates(self, timestamp: str):
        """Track error rates"""

        # Mock error rate calculation
        error_rate = 0.8  # percent

        metric = PerformanceMetric(
            metric_name="error_rate",
            value=error_rate,
            unit="percent",
            timestamp=timestamp,
            labels={"service": "odds_service"},
            threshold=2.0,
            alert_triggered=error_rate > 2.0,
        )

        await self._record_metric(metric)

    async def _track_business_metrics(self, timestamp: str):
        """Track business-specific metrics"""

        # Mock business metrics
        active_parlays = 145
        total_bets_today = 1247

        metrics = [
            PerformanceMetric(
                metric_name="active_parlays",
                value=active_parlays,
                unit="count",
                timestamp=timestamp,
                labels={"type": "live_betting"},
            ),
            PerformanceMetric(
                metric_name="daily_bet_count",
                value=total_bets_today,
                unit="count",
                timestamp=timestamp,
                labels={"date": datetime.utcnow().date().isoformat()},
            ),
        ]

        for metric in metrics:
            await self._record_metric(metric)

    async def _record_metric(self, metric: PerformanceMetric):
        """Record and broadcast metric"""

        # Store metric
        if metric.metric_name not in self.metrics:
            self.metrics[metric.metric_name] = []

        self.metrics[metric.metric_name].append(metric)

        # Keep only last 100 measurements per metric
        if len(self.metrics[metric.metric_name]) > 100:
            self.metrics[metric.metric_name] = self.metrics[metric.metric_name][-100:]

        # Broadcast if alert triggered
        if metric.alert_triggered:
            performance_event = DashboardEvent(
                event_type=DashboardEventType.PERFORMANCE_METRIC,
                data={
                    "metric": metric.dict(),
                    "alert": f"{metric.metric_name} exceeded threshold: {metric.value} {metric.unit}",
                },
                alert_level=AlertLevel.WARNING,
            )

            await self.ws_manager.broadcast_event(performance_event)


class DashboardServer:
    """Main dashboard server with WebSocket support"""

    def __init__(self, port: int = 3001):
        self.port = port
        self.app = web.Application()
        self.ws_manager = WebSocketManager()
        self.health_monitor = HealthMonitor(self.ws_manager)
        self.governance_engine = GovernanceEngine(self.ws_manager)
        self.performance_tracker = PerformanceTracker(self.ws_manager)

        self._setup_routes()

    def _setup_routes(self):
        """Setup HTTP routes"""

        # WebSocket endpoint
        self.app.router.add_get("/ws", self.websocket_handler)

        # Health check endpoint
        self.app.router.add_get("/health", self.health_handler)

        # Status page endpoint
        self.app.router.add_get("/status", self.status_handler)

        # Metrics endpoint
        self.app.router.add_get("/metrics", self.metrics_handler)

        # Dashboard HTML (served statically)
        self.app.router.add_get("/", self.dashboard_handler)

        # API endpoints
        self.app.router.add_post("/api/parlay", self.parlay_handler)
        self.app.router.add_post("/api/bet", self.bet_handler)

        # Enable CORS
        self.app.middlewares.append(self._cors_middleware)

    async def _cors_middleware(self, request, handler):
        """CORS middleware"""
        response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    async def websocket_handler(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        user_id = request.query.get("user_id")
        session_id = await self.ws_manager.add_connection(ws, user_id)

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._handle_ws_message(ws, data, session_id)
                    except json.JSONDecodeError:
                        logging.error(f"Invalid JSON from WebSocket: {msg.data}")
                elif msg.type == WSMsgType.ERROR:
                    logging.error(f"WebSocket error: {ws.exception()}")
                    break
        except Exception as e:
            logging.error(f"WebSocket handler error: {e}")
        finally:
            await self.ws_manager.remove_connection(ws)

        return ws

    async def _handle_ws_message(self, ws: web.WebSocketResponse, data: dict, session_id: str):
        """Handle incoming WebSocket messages"""

        message_type = data.get("type", "unknown")

        if message_type == "ping":
            # Respond to ping
            await ws.send_str(
                json.dumps(
                    {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                        "session_id": session_id,
                    }
                )
            )

        elif message_type == "subscribe":
            # Handle event subscriptions
            events = data.get("events", [])
            # Implementation would track user subscriptions
            await ws.send_str(
                json.dumps({"type": "subscribed", "events": events, "session_id": session_id})
            )

        elif message_type == "user_action":
            # Handle user actions
            action_event = DashboardEvent(
                event_type=DashboardEventType.USER_ACTION,
                data=data.get("action", {}),
                session_id=session_id,
                user_id=data.get("user_id"),
            )
            await self.ws_manager.broadcast_event(action_event)

    async def health_handler(self, request):
        """Health check endpoint"""

        overall_status = self.health_monitor._calculate_overall_health()

        health_data = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                name: {
                    "status": health.status,
                    "response_time_ms": health.response_time_ms,
                    "last_check": health.last_check,
                }
                for name, health in self.health_monitor.health_checks.items()
            },
            "summary": self.health_monitor._get_health_summary(),
        }

        status_code = 200 if overall_status == "healthy" else 503

        return web.json_response(health_data, status=status_code)

    async def status_handler(self, request):
        """Comprehensive status page"""

        status_data = {
            "system": {
                "uptime": time.time(),  # Would be actual uptime
                "version": "2.1.0",
                "environment": "production",
            },
            "health": dict(self.health_monitor.health_checks),
            "websockets": {
                "active_connections": len(self.ws_manager.connections),
                "stats": self.ws_manager.connection_stats,
            },
            "governance": {
                "rules_count": len(self.governance_engine.rules),
                "triggers_today": len(
                    [
                        t
                        for t in self.governance_engine.triggers_log
                        if t.timestamp.startswith(datetime.utcnow().date().isoformat())
                    ]
                ),
                "recent_triggers": self.governance_engine.triggers_log[-5:],
            },
            "performance": {
                "metrics_tracked": len(self.performance_tracker.metrics),
                "latest_metrics": {
                    name: metrics[-1].dict() if metrics else None
                    for name, metrics in self.performance_tracker.metrics.items()
                },
            },
        }

        return web.json_response(status_data)

    async def metrics_handler(self, request):
        """Prometheus-style metrics endpoint"""

        metrics_output = []

        for metric_name, metric_list in self.performance_tracker.metrics.items():
            if metric_list:
                latest = metric_list[-1]
                labels = ",".join([f'{k}="{v}"' for k, v in latest.labels.items()])
                labels_str = f"{{{labels}}}" if labels else ""
                metrics_output.append(f"{metric_name}{labels_str} {latest.value}")

        return web.Response(text="\n".join(metrics_output), content_type="text/plain")

    async def dashboard_handler(self, request):
        """Serve dashboard HTML"""

        dashboard_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EQ12 Real-time Dashboard</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
            <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
            <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
        </head>
        <body class="bg-gray-900 text-white">
            <div id="dashboard"></div>

            <script type="text/babel">
                const { useState, useEffect } = React;

                function Dashboard() {
                    const [connected, setConnected] = useState(false);
                    const [events, setEvents] = useState([]);
                    const [health, setHealth] = useState({});
                    const [ws, setWs] = useState(null);

                    useEffect(() => {
                        const websocket = new WebSocket(`ws://localhost:3001/ws?user_id=demo_user`);

                        websocket.onopen = () => {
                            setConnected(true);
                            setWs(websocket);
                        };

                        websocket.onmessage = (event) => {
                            const data = JSON.parse(event.data);

                            if (data.event_type === 'health_status') {
                                setHealth(data.data);
                            }

                            setEvents(prev => [data, ...prev.slice(0, 49)]); // Keep last 50 events
                        };

                        websocket.onclose = () => {
                            setConnected(false);
                        };

                        return () => websocket.close();
                    }, []);

                    const getAlertColor = (level) => {
                        switch (level) {
                            case 'critical': return 'text-red-400 bg-red-900/20';
                            case 'warning': return 'text-yellow-400 bg-yellow-900/20';
                            case 'emergency': return 'text-purple-400 bg-purple-900/20';
                            default: return 'text-green-400 bg-green-900/20';
                        }
                    };

                    return (
                        <div className="min-h-screen p-6">
                            <div className="max-w-7xl mx-auto">
                                {/* Header */}
                                <div className="mb-8">
                                    <h1 className="text-4xl font-bold text-white mb-2">EQ12 Real-time Dashboard</h1>
                                    <div className="flex items-center gap-4">
                                        <span className={`px-3 py-1 rounded-full text-sm ${connected ? 'bg-green-900/20 text-green-400' : 'bg-red-900/20 text-red-400'}`}>
                                            {connected ? '● Connected' : '● Disconnected'}
                                        </span>
                                        <span className="text-gray-400">
                                            {new Date().toLocaleString()}
                                        </span>
                                    </div>
                                </div>

                                {/* Health Status Grid */}
                                {health.components && (
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                                        {Object.entries(health.components).map(([name, component]) => (
                                            <div key={name} className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                                                <h3 className="text-lg font-semibold mb-2 capitalize">{name.replace('_', ' ')}</h3>
                                                <div className={`px-3 py-1 rounded-full text-sm inline-block mb-2 ${
                                                    component.status === 'healthy' ? 'bg-green-900/20 text-green-400' :
                                                    component.status === 'degraded' ? 'bg-yellow-900/20 text-yellow-400' :
                                                    'bg-red-900/20 text-red-400'
                                                }`}>
                                                    {component.status}
                                                </div>
                                                <p className="text-gray-400 text-sm">
                                                    Response: {component.response_time_ms?.toFixed(1)}ms
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {/* Real-time Events */}
                                <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                                    <h2 className="text-2xl font-bold mb-4">Real-time Events</h2>
                                    <div className="space-y-3 max-h-96 overflow-y-auto">
                                        {events.map((event, index) => (
                                            <div key={event.event_id || index} className={`p-4 rounded-lg border ${getAlertColor(event.alert_level)}`}>
                                                <div className="flex justify-between items-start mb-2">
                                                    <span className="font-semibold capitalize">
                                                        {event.event_type?.replace('_', ' ')}
                                                    </span>
                                                    <span className="text-sm text-gray-400">
                                                        {new Date(event.timestamp).toLocaleTimeString()}
                                                    </span>
                                                </div>
                                                <div className="text-sm">
                                                    {event.data?.message || JSON.stringify(event.data, null, 2)}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                }

                ReactDOM.render(<Dashboard />, document.getElementById('dashboard'));
            </script>
        </body>
        </html>
        """

        return web.Response(text=dashboard_html, content_type="text/html")

    async def parlay_handler(self, request):
        """Handle parlay API requests"""
        try:
            data = await request.json()

            # Mock parlay processing
            parlay_result = {
                "parlay_id": str(uuid.uuid4()),
                "legs": data.get("legs", []),
                "total_odds": 350,
                "potential_payout": data.get("stake", 10) * 3.5,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Broadcast parlay update
            parlay_event = DashboardEvent(
                event_type=DashboardEventType.PARLAY_UPDATE,
                data=parlay_result,
                user_id=data.get("user_id"),
            )
            await self.ws_manager.broadcast_event(parlay_event)

            return web.json_response(parlay_result)

        except Exception as e:
            logging.error(f"Parlay handler error: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def bet_handler(self, request):
        """Handle betting requests with governance checks"""
        try:
            data = await request.json()
            user_id = data.get("user_id", "anonymous")
            bet_amount = data.get("amount", 0)

            # Mock bet history for governance check
            bet_history = []  # Would fetch from database

            # Check governance rules
            trigger = await self.governance_engine.evaluate_bet_action(
                user_id, bet_amount, bet_history
            )

            if trigger and trigger.severity == "critical":
                return web.json_response(
                    {
                        "error": "Bet blocked by governance rules",
                        "reason": trigger.description,
                        "action_required": trigger.action_taken,
                    },
                    status=403,
                )

            # Process bet
            bet_result = {
                "bet_id": str(uuid.uuid4()),
                "amount": bet_amount,
                "user_id": user_id,
                "status": "accepted",
                "timestamp": datetime.utcnow().isoformat(),
                "governance_trigger": trigger.dict() if trigger else None,
            }

            return web.json_response(bet_result)

        except Exception as e:
            logging.error(f"Bet handler error: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def start_server(self):
        """Start the dashboard server"""

        # Start background monitoring tasks
        asyncio.create_task(self.health_monitor.start_monitoring())
        asyncio.create_task(self.performance_tracker.start_tracking())

        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, "localhost", self.port)
        await site.start()

        logging.info(f"🚀 EQ12 Dashboard Server started on http://localhost:{self.port}")
        logging.info(f"📊 Dashboard: http://localhost:{self.port}")
        logging.info(f"🔌 WebSocket: ws://localhost:{self.port}/ws")
        logging.info(f"❤️ Health: http://localhost:{self.port}/health")

        return runner

    async def stop_server(self, runner):
        """Stop the dashboard server"""
        await self.health_monitor.stop_monitoring()
        await self.performance_tracker.stop_tracking()
        await runner.cleanup()


async def main():
    """Main entry point"""

    setup_utf8_logging()
    logging.info("🚀 Starting EQ12 Real-time Dashboard System")

    # Create and start dashboard server
    dashboard = DashboardServer(port=3001)
    runner = await dashboard.start_server()

    try:
        # Keep server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutting down dashboard server...")
        await dashboard.stop_server(runner)


if __name__ == "__main__":
    asyncio.run(main())
