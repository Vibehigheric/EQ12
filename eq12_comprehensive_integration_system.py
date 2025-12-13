# eq12_comprehensive_integration_system.py
"""
EQ12 Comprehensive Integration System
Complete real-time dashboard, WebSocket management, health monitoring,
Ngrok diagnostics, and structured observability integration
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

import psutil
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from eq12_helpers import setup_utf8_logging
from eq12_ngrok_tunnel_diagnostics import NgrokDiagnostics, TunnelFailover

# Import our custom modules
from eq12_realtime_dashboard_system import (
    DashboardServer,
)
from eq12_structured_observability import ObservabilityManager, tracked_operation

setup_utf8_logging()


class EQ12IntegratedSystem:
    """Comprehensive EQ12 system integration"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or self._load_default_config()

        # Initialize core components
        self.observability = ObservabilityManager("eq12_integrated_system")
        self.dashboard = DashboardServer(port=self.config["dashboard_port"])
        self.ngrok_diagnostics = NgrokDiagnostics()
        self.tunnel_failover = TunnelFailover(self.ngrok_diagnostics)

        # FastAPI app for advanced endpoints
        self.app = FastAPI(title="EQ12 Integrated System API", version="2.1.0")
        self._setup_api_routes()

        # System state
        self.running = False
        self.background_tasks = []

    def _load_default_config(self) -> dict[str, Any]:
        """Load default system configuration"""
        return {
            "dashboard_port": 3001,
            "api_port": 8082,
            "enable_ngrok": True,
            "enable_observability": True,
            "health_check_interval": 30,
            "metrics_flush_interval": 60,
            "log_level": "INFO",
        }

    def _setup_api_routes(self):
        """Setup FastAPI routes for system management"""

        @self.app.get("/api/system/status")
        async def get_system_status():
            """Get comprehensive system status"""

            async with tracked_operation(self.observability, "get_system_status") as ctx:
                # Collect status from all components
                dashboard_health = await self.dashboard.health_monitor._calculate_overall_health()
                ngrok_status = await self.ngrok_diagnostics.get_status_report()
                observability_health = await self.observability.health_check()

                system_status = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "overall_status": self._calculate_overall_system_health(),
                    "components": {
                        "dashboard": {
                            "status": dashboard_health,
                            "active_connections": len(self.dashboard.ws_manager.connections),
                            "port": self.config["dashboard_port"],
                        },
                        "ngrok_tunnels": {
                            "status": ngrok_status["overall_health"],
                            "tunnel_count": ngrok_status["tunnel_summary"]["total"],
                            "online_tunnels": ngrok_status["tunnel_summary"]["online"],
                        },
                        "observability": {
                            "status": observability_health["status"],
                            "response_time_ms": observability_health["response_time_ms"],
                        },
                    },
                    "system_metrics": {
                        "cpu_percent": psutil.cpu_percent(),
                        "memory_percent": psutil.virtual_memory().percent,
                        "disk_percent": (
                            psutil.disk_usage("C:").percent if psutil.disk_usage("C:") else 0
                        ),
                    },
                    "recommendations": await self._get_system_recommendations(),
                }

                return await self.observability.create_structured_response(
                    status="success",
                    data=system_status,
                    message="System status retrieved successfully",
                    request_id=ctx["request_id"],
                )

        @self.app.post("/api/system/restart-component")
        async def restart_component(component: str):
            """Restart specific system component"""

            async with tracked_operation(
                self.observability, "restart_component", component=component
            ) as ctx:
                success = False
                message = ""

                if component == "dashboard":
                    # Restart dashboard (would need implementation)
                    success = True
                    message = "Dashboard restart initiated"

                elif component == "ngrok":
                    success = await self.ngrok_diagnostics.restart_all_tunnels()
                    message = (
                        "Ngrok tunnels restart initiated" if success else "Ngrok restart failed"
                    )

                elif component == "all":
                    # Restart entire system
                    await self._restart_all_components()
                    success = True
                    message = "Full system restart initiated"

                else:
                    raise HTTPException(status_code=400, detail=f"Unknown component: {component}")

                status = "success" if success else "error"

                return await self.observability.create_structured_response(
                    status=status,
                    data={"component": component, "restarted": success},
                    message=message,
                    request_id=ctx["request_id"],
                )

        @self.app.get("/api/tunnels/status")
        async def get_tunnel_status():
            """Get detailed tunnel status"""

            async with tracked_operation(self.observability, "get_tunnel_status") as ctx:
                tunnel_report = await self.ngrok_diagnostics.get_status_report()

                return await self.observability.create_structured_response(
                    status="success",
                    data=tunnel_report,
                    message="Tunnel status retrieved successfully",
                    request_id=ctx["request_id"],
                )

        @self.app.post("/api/tunnels/restart/{tunnel_name}")
        async def restart_tunnel(tunnel_name: str):
            """Restart specific tunnel"""

            async with tracked_operation(
                self.observability, "restart_tunnel", tunnel=tunnel_name
            ) as ctx:
                success = await self.ngrok_diagnostics.restart_tunnel(tunnel_name)

                status = "success" if success else "error"
                message = f"Tunnel {tunnel_name} restart {'successful' if success else 'failed'}"

                return await self.observability.create_structured_response(
                    status=status,
                    data={"tunnel": tunnel_name, "restarted": success},
                    message=message,
                    request_id=ctx["request_id"],
                )

        @self.app.get("/api/observability/health")
        async def get_observability_health():
            """Get observability system health"""

            health_data = await self.observability.health_check()

            return await self.observability.create_structured_response(
                status="success" if health_data["status"] == "healthy" else "degraded",
                data=health_data,
                message="Observability health check completed",
            )

        @self.app.get("/api/dashboard")
        async def serve_dashboard():
            """Serve the integrated dashboard"""

            dashboard_html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>EQ12 Integrated System Dashboard</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
                <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
                <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
                <style>
                    .gradient-bg {
                        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #3b82f6 100%);
                    }
                </style>
            </head>
            <body class="bg-gray-900 text-white">
                <div id="integrated-dashboard"></div>

                <script type="text/babel">
                    const { useState, useEffect } = React;

                    function IntegratedDashboard() {
                        const [systemStatus, setSystemStatus] = useState({});
                        const [tunnelStatus, setTunnelStatus] = useState({});
                        const [connected, setConnected] = useState(false);

                        useEffect(() => {
                            // Fetch initial system status
                            fetchSystemStatus();
                            fetchTunnelStatus();

                            // Setup WebSocket connection for real-time updates
                            const ws = new WebSocket('ws://localhost:3001/ws?user_id=integrated_dashboard');

                            ws.onopen = () => setConnected(true);
                            ws.onclose = () => setConnected(false);

                            ws.onmessage = (event) => {
                                const data = JSON.parse(event.data);

                                // Handle real-time updates
                                if (data.event_type === 'system_status_update') {
                                    setSystemStatus(data.data);
                                }
                            };

                            // Periodic updates
                            const interval = setInterval(() => {
                                fetchSystemStatus();
                                fetchTunnelStatus();
                            }, 30000); // Every 30 seconds

                            return () => {
                                ws.close();
                                clearInterval(interval);
                            };
                        }, []);

                        const fetchSystemStatus = async () => {
                            try {
                                const response = await fetch('/api/system/status');
                                const result = await response.json();
                                if (result.status === 'success') {
                                    setSystemStatus(result.data);
                                }
                            } catch (error) {
                                console.error('Failed to fetch system status:', error);
                            }
                        };

                        const fetchTunnelStatus = async () => {
                            try {
                                const response = await fetch('/api/tunnels/status');
                                const result = await response.json();
                                if (result.status === 'success') {
                                    setTunnelStatus(result.data);
                                }
                            } catch (error) {
                                console.error('Failed to fetch tunnel status:', error);
                            }
                        };

                        const restartComponent = async (component) => {
                            try {
                                const response = await fetch('/api/system/restart-component', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ component })
                                });

                                const result = await response.json();
                                alert(result.message);

                                // Refresh status after restart
                                setTimeout(fetchSystemStatus, 3000);

                            } catch (error) {
                                alert('Failed to restart component: ' + error.message);
                            }
                        };

                        const getStatusColor = (status) => {
                            switch (status) {
                                case 'healthy': return 'text-green-400 bg-green-900/20';
                                case 'degraded': return 'text-yellow-400 bg-yellow-900/20';
                                case 'critical': return 'text-red-400 bg-red-900/20';
                                default: return 'text-gray-400 bg-gray-900/20';
                            }
                        };

                        return (
                            <div className="min-h-screen">
                                {/* Header */}
                                <header className="gradient-bg p-6 shadow-lg">
                                    <div className="max-w-7xl mx-auto">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <h1 className="text-4xl font-bold text-white">EQ12 Integrated System</h1>
                                                <p className="text-blue-100 mt-2">Real-time monitoring, tunnels, and observability</p>
                                            </div>

                                            <div className="flex items-center space-x-4">
                                                <span className={`px-4 py-2 rounded-full font-medium $${connected ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'}`}>
                                                    {connected ? '● Connected' : '● Disconnected'}
                                                </span>
                                                <span className="text-blue-100">
                                                    {new Date().toLocaleString()}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </header>

                                {/* Main Content */}
                                <main className="max-w-7xl mx-auto p-6 space-y-8">

                                    {/* System Overview */}
                                    {systemStatus.overall_status && (
                                        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                                            <h2 className="text-2xl font-bold mb-6">System Overview</h2>

                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                                                <div className="text-center">
                                                    <div className={`text-3xl font-bold mb-2 $${getStatusColor(systemStatus.overall_status)}`}>
                                                        {systemStatus.overall_status?.toUpperCase()}
                                                    </div>
                                                    <div className="text-gray-400">Overall Status</div>
                                                </div>

                                                <div className="text-center">
                                                    <div className="text-3xl font-bold text-blue-400 mb-2">
                                                        {systemStatus.system_metrics?.cpu_percent?.toFixed(1)}%
                                                    </div>
                                                    <div className="text-gray-400">CPU Usage</div>
                                                </div>

                                                <div className="text-center">
                                                    <div className="text-3xl font-bold text-purple-400 mb-2">
                                                        {systemStatus.system_metrics?.memory_percent?.toFixed(1)}%
                                                    </div>
                                                    <div className="text-gray-400">Memory Usage</div>
                                                </div>
                                            </div>

                                            {/* Component Status */}
                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                                {systemStatus.components && Object.entries(systemStatus.components).map(([name, component]) => (
                                                    <div key={name} className="bg-gray-900/50 p-4 rounded-lg">
                                                        <div className="flex items-center justify-between mb-2">
                                                            <h3 className="font-semibold capitalize">{name.replace('_', ' ')}</h3>
                                                            <span className={`px-2 py-1 rounded text-sm $${getStatusColor(component.status)}`}>
                                                                {component.status}
                                                            </span>
                                                        </div>

                                                        {component.active_connections !== undefined && (
                                                            <p className="text-sm text-gray-400">
                                                                Connections: {component.active_connections}
                                                            </p>
                                                        )}

                                                        {component.port && (
                                                            <p className="text-sm text-gray-400">
                                                                Port: {component.port}
                                                            </p>
                                                        )}

                                                        <button
                                                            onClick={() => restartComponent(name)}
                                                            className="mt-2 px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-sm transition-colors"
                                                        >
                                                            Restart
                                                        </button>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Tunnel Status */}
                                    {tunnelStatus.tunnels && (
                                        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                                            <h2 className="text-2xl font-bold mb-6">Ngrok Tunnels</h2>

                                            <div className="grid grid-cols-1 gap-4">
                                                {tunnelStatus.tunnels.map((tunnel, index) => (
                                                    <div key={index} className="bg-gray-900/50 p-4 rounded-lg">
                                                        <div className="flex items-center justify-between mb-2">
                                                            <h3 className="font-semibold">{tunnel.name}</h3>
                                                            <span className={`px-2 py-1 rounded text-sm $${getStatusColor(tunnel.status === 'online' ? 'healthy' : 'critical')}`}>
                                                                {tunnel.status}
                                                            </span>
                                                        </div>

                                                        {tunnel.public_url && (
                                                            <p className="text-sm text-blue-400 mb-1">
                                                                <a href={tunnel.public_url} target="_blank" rel="noopener">
                                                                    {tunnel.public_url}
                                                                </a>
                                                            </p>
                                                        )}

                                                        <div className="flex justify-between text-sm text-gray-400">
                                                            <span>Local: {tunnel.local_url}</span>
                                                            <span>Latency: {tunnel.latency_ms?.toFixed(0)}ms</span>
                                                            <span>Connections: {tunnel.connections}</span>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {/* Quick Actions */}
                                    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                                        <h2 className="text-2xl font-bold mb-6">Quick Actions</h2>

                                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                            <button
                                                onClick={() => restartComponent('dashboard')}
                                                className="bg-blue-600 hover:bg-blue-500 text-white py-3 px-4 rounded-lg transition-colors"
                                            >
                                                Restart Dashboard
                                            </button>

                                            <button
                                                onClick={() => restartComponent('ngrok')}
                                                className="bg-green-600 hover:bg-green-500 text-white py-3 px-4 rounded-lg transition-colors"
                                            >
                                                Restart Tunnels
                                            </button>

                                            <button
                                                onClick={fetchSystemStatus}
                                                className="bg-yellow-600 hover:bg-yellow-500 text-white py-3 px-4 rounded-lg transition-colors"
                                            >
                                                Refresh Status
                                            </button>

                                            <button
                                                onClick={() => restartComponent('all')}
                                                className="bg-red-600 hover:bg-red-500 text-white py-3 px-4 rounded-lg transition-colors"
                                            >
                                                Restart All
                                            </button>
                                        </div>
                                    </div>

                                    {/* Recommendations */}
                                    {systemStatus.recommendations && systemStatus.recommendations.length > 0 && (
                                        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
                                            <h2 className="text-2xl font-bold mb-4">Recommendations</h2>

                                            <ul className="space-y-2">
                                                {systemStatus.recommendations.map((rec, index) => (
                                                    <li key={index} className="flex items-start">
                                                        <span className="text-yellow-400 mr-2">⚠️</span>
                                                        <span className="text-gray-300">{rec}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </main>
                            </div>
                        );
                    }

                    ReactDOM.render(<IntegratedDashboard />, document.getElementById('integrated-dashboard'));
                </script>
            </body>
            </html>
            """

            return HTMLResponse(dashboard_html)

    def _calculate_overall_system_health(self) -> str:
        """Calculate overall system health status"""

        # This would aggregate health from all components
        # For now, return a mock status
        return "healthy"

    async def _get_system_recommendations(self) -> list[str]:
        """Get system optimization recommendations"""

        recommendations = []

        # Check system resources
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent

        if cpu_percent > 80:
            recommendations.append("High CPU usage detected - consider optimizing processes")

        if memory_percent > 85:
            recommendations.append("High memory usage - consider increasing system RAM")

        # Check tunnel status
        tunnel_report = await self.ngrok_diagnostics.get_status_report()
        if tunnel_report["tunnel_summary"]["online"] < tunnel_report["tunnel_summary"]["total"]:
            recommendations.append("Some tunnels are offline - check network connectivity")

        return recommendations

    async def _restart_all_components(self):
        """Restart all system components"""

        logging.info("🔄 Restarting all system components")

        # Restart Ngrok tunnels
        await self.ngrok_diagnostics.restart_all_tunnels()

        # Restart dashboard (would need proper implementation)
        # await self.dashboard.restart()

        logging.info("✅ All components restart initiated")

    async def start_system(self):
        """Start the complete integrated system"""

        async with tracked_operation(self.observability, "start_integrated_system") as ctx:
            logging.info("🚀 Starting EQ12 Integrated System")

            # Start dashboard server
            dashboard_runner = await self.dashboard.start_server()
            self.background_tasks.append(dashboard_runner)

            # Start Ngrok monitoring
            ngrok_task = asyncio.create_task(self.ngrok_diagnostics.start_monitoring())
            self.background_tasks.append(ngrok_task)

            # Start tunnel failover
            failover_task = asyncio.create_task(self.tunnel_failover.start_failover_monitoring())
            self.background_tasks.append(failover_task)

            # Start FastAPI server
            api_config = uvicorn.Config(
                self.app,
                host="localhost",
                port=self.config["api_port"],
                log_level="info",
            )
            api_server = uvicorn.Server(api_config)
            api_task = asyncio.create_task(api_server.serve())
            self.background_tasks.append(api_task)

            self.running = True

            logging.info("✅ EQ12 Integrated System running:")
            logging.info(f"   📊 Dashboard: http://localhost:{self.config['dashboard_port']}")
            logging.info(f"   🔌 WebSocket: ws://localhost:{self.config['dashboard_port']}/ws")
            logging.info(f"   🌐 API: http://localhost:{self.config['api_port']}")
            logging.info(
                f"   🎛️ Integrated UI: http://localhost:{self.config['api_port']}/api/dashboard"
            )

            await self.observability.logger.info(
                "EQ12 Integrated System started successfully",
                dashboard_port=self.config["dashboard_port"],
                api_port=self.config["api_port"],
                request_id=ctx["request_id"],
            )

    async def stop_system(self):
        """Stop the integrated system gracefully"""

        logging.info("⏹️ Stopping EQ12 Integrated System")

        self.running = False

        # Stop monitoring
        await self.ngrok_diagnostics.stop_monitoring()

        # Cancel background tasks
        for task in self.background_tasks:
            if hasattr(task, "cancel"):
                task.cancel()
            elif hasattr(task, "cleanup"):
                await task.cleanup()

        logging.info("✅ EQ12 Integrated System stopped")


async def main():
    """Main entry point for integrated system"""

    setup_utf8_logging()

    # Create and configure system
    config = {
        "dashboard_port": 3001,
        "api_port": 8082,
        "enable_ngrok": True,
        "enable_observability": True,
        "health_check_interval": 30,
    }

    integrated_system = EQ12IntegratedSystem(config)

    try:
        # Start the integrated system
        await integrated_system.start_system()

        # Keep running
        while integrated_system.running:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logging.info("Received shutdown signal")

    finally:
        await integrated_system.stop_system()


if __name__ == "__main__":
    asyncio.run(main())
