#!/usr/bin/env python3
"""
EQ12 OpenAI Status Dashboard
Web dashboard for monitoring OpenAI service status and EQ12 optimization workflows
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta

# FastAPI imports
try:
    import uvicorn
    from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
except ImportError:
    print("FastAPI not installed. Run: pip install fastapi uvicorn jinja2")
    sys.exit(1)

# Add EQ12 modules to path
sys.path.append(os.path.dirname(__file__))

try:
    from eq12_openai_status_monitor import EQ12OpenAIStatusMonitor
    from eq12_optimization_orchestrator import EQ12OptimizationOrchestrator
except ImportError as e:
    print(f"Failed to import EQ12 modules: {e}")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EQ12 OpenAI Status Dashboard",
    description="Monitor OpenAI service status and EQ12 optimization workflows",
    version="1.0.0",
)

# Global instances
status_monitor = EQ12OpenAIStatusMonitor()
orchestrator = EQ12OptimizationOrchestrator()

# Background monitoring state
monitoring_active = False
last_status_check = None
cached_status = None


@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Serve the main dashboard HTML"""

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EQ12 OpenAI Status Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header {
                border-bottom: 2px solid #e0e0e0;
                padding-bottom: 20px;
                margin-bottom: 20px;
            }
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .status-card {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 15px;
                background: #fafafa;
            }
            .status-operational { border-left: 4px solid #28a745; }
            .status-degraded { border-left: 4px solid #ffc107; }
            .status-outage { border-left: 4px solid #dc3545; }
            .health-score {
                font-size: 24px;
                font-weight: bold;
                margin: 10px 0;
            }
            .recommendations {
                margin-top: 20px;
            }
            .recommendation {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 4px;
                padding: 10px;
                margin: 10px 0;
            }
            .priority-critical { background: #f8d7da; border-color: #f5c6cb; }
            .priority-high { background: #fff3cd; border-color: #ffeaa7; }
            .refresh-btn {
                background: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                margin: 10px 0;
            }
            .refresh-btn:hover { background: #0056b3; }
            .timestamp {
                color: #666;
                font-size: 12px;
            }
            .loading {
                text-align: center;
                padding: 20px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 EQ12 OpenAI Status Dashboard</h1>
                <p>Real-time monitoring of OpenAI services and EQ12 optimization workflows</p>
                <button class="refresh-btn" onclick="refreshStatus()">🔄 Refresh Status</button>
                <span class="timestamp" id="lastUpdate">Last updated: Loading...</span>
            </div>

            <div id="statusContent" class="loading">
                Loading status information...
            </div>
        </div>

        <script>
            let statusData = null;

            async function fetchStatus() {
                try {
                    const response = await fetch('/api/status');
                    statusData = await response.json();
                    renderStatus();
                } catch (error) {
                    console.error('Failed to fetch status:', error);
                    document.getElementById('statusContent').innerHTML =
                        '<div class="status-card"><h3>❌ Error</h3><p>Failed to fetch status information</p></div>';
                }
            }

            function renderStatus() {
                if (!statusData) return;

                const content = document.getElementById('statusContent');
                const lastUpdate = document.getElementById('lastUpdate');

                lastUpdate.textContent = `Last updated: ${new Date(statusData.timestamp).toLocaleString()}`;

                let html = `
                    <div class="status-card">
                        <h3>🎯 Overall Health</h3>
                        <div class="health-score" style="color: ${getHealthColor(statusData.overall_health)}">
                            ${statusData.overall_health.toFixed(1)}%
                        </div>
                        <p>Status: <strong>${statusData.status}</strong></p>
                    </div>
                `;

                html += '<div class="status-grid">';

                statusData.services.forEach(service => {
                    const statusClass = getStatusClass(service.status);
                    html += `
                        <div class="status-card ${statusClass}">
                            <h4>${service.name}</h4>
                            <p><strong>${service.status.replace('_', ' ').toUpperCase()}</strong></p>
                            <p class="timestamp">${service.description}</p>
                            <p class="timestamp">Impact: ${service.impact_level}</p>
                        </div>
                    `;
                });

                html += '</div>';

                // EQ12 Impact Assessment
                if (statusData.eq12_impact_assessment) {
                    html += '<h3>🎮 EQ12 Workflow Impact</h3><div class="status-grid">';

                    Object.entries(statusData.eq12_impact_assessment).forEach(([workflow, status]) => {
                        const statusClass = getStatusClass(status);
                        html += `
                            <div class="status-card ${statusClass}">
                                <h4>${workflow.replace('_', ' ').toUpperCase()}</h4>
                                <p><strong>${status.toUpperCase()}</strong></p>
                            </div>
                        `;
                    });

                    html += '</div>';
                }

                // Recommendations
                if (statusData.active_recommendations && statusData.active_recommendations.length > 0) {
                    html += '<div class="recommendations"><h3>⚠️ Active Recommendations</h3>';

                    statusData.active_recommendations.forEach(rec => {
                        const priorityClass = `priority-${rec.priority}`;
                        const recData = rec.recommendation;
                        html += `
                            <div class="recommendation ${priorityClass}">
                                <strong>[${rec.priority.toUpperCase()}] ${recData.action.replace(/_/g, ' ').toUpperCase()}</strong>
                                <p>${recData.description}</p>
                                ${recData.affected_use_cases ? `<p><small>Affects: ${recData.affected_use_cases.join(', ')}</small></p>` : ''}
                            </div>
                        `;
                    });

                    html += '</div>';
                }

                content.innerHTML = html;
            }

            function getHealthColor(health) {
                if (health >= 90) return '#28a745';
                if (health >= 70) return '#ffc107';
                return '#dc3545';
            }

            function getStatusClass(status) {
                if (status === 'operational') return 'status-operational';
                if (status.includes('degraded')) return 'status-degraded';
                return 'status-outage';
            }

            function refreshStatus() {
                document.getElementById('statusContent').innerHTML = '<div class="loading">Refreshing...</div>';
                fetchStatus();
            }

            // Auto-refresh every 30 seconds
            setInterval(fetchStatus, 30000);

            // Initial load
            fetchStatus();
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


@app.get("/api/status")
async def get_status():
    """Get current OpenAI service status"""

    global cached_status, last_status_check

    # Use cached status if recent (within 2 minutes)
    if (
        cached_status
        and last_status_check
        and datetime.utcnow() - last_status_check < timedelta(minutes=2)
    ):
        return JSONResponse(content=cached_status)

    try:
        # Get current status
        status_summary = status_monitor.get_status_summary()

        # Cache the result
        cached_status = status_summary
        last_status_check = datetime.utcnow()

        return JSONResponse(content=status_summary)

    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {e!s}")


@app.get("/api/refresh")
async def refresh_status(background_tasks: BackgroundTasks):
    """Force refresh of OpenAI service status"""

    async def refresh_task():
        global cached_status, last_status_check
        try:
            # Force fresh status check
            statuses = await status_monitor.get_current_status()
            status_monitor.generate_eq12_recommendations(statuses)

            # Update cached status
            cached_status = status_monitor.get_status_summary()
            last_status_check = datetime.utcnow()

            logger.info("Status refreshed successfully")

        except Exception as e:
            logger.error(f"Failed to refresh status: {e}")

    background_tasks.add_task(refresh_task)

    return JSONResponse(
        content={
            "message": "Status refresh initiated",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.get("/api/model/{model_name}")
async def check_model_availability(model_name: str):
    """Check availability of specific OpenAI model"""

    try:
        model_status = await status_monitor.check_model_availability(model_name)
        return JSONResponse(content=model_status)

    except Exception as e:
        logger.error(f"Failed to check model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check model: {e!s}")


@app.get("/api/optimization/{use_case}")
async def get_optimization_status(use_case: str):
    """Get optimization status for specific EQ12 use case"""

    try:
        # Check if use case is valid
        if use_case not in orchestrator.eq12_use_cases:
            raise HTTPException(status_code=404, detail=f"Use case '{use_case}' not found")

        # Get current status and check if optimization can proceed
        statuses = await status_monitor.get_current_status()

        api_service = statuses.get("API")
        can_optimize = api_service and api_service.status in [
            "operational",
            "degraded_performance",
        ]

        fine_tuning_service = statuses.get("Fine-tuning")
        can_fine_tune = fine_tuning_service and fine_tuning_service.status == "operational"

        return JSONResponse(
            content={
                "use_case": use_case,
                "can_optimize": can_optimize,
                "can_fine_tune": can_fine_tune,
                "api_status": api_service.status if api_service else "unknown",
                "fine_tuning_status": (
                    fine_tuning_service.status if fine_tuning_service else "unknown"
                ),
                "recommendations": status_monitor.generate_eq12_recommendations(statuses),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get optimization status for {use_case}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get optimization status: {e!s}")


@app.post("/api/monitoring/start")
async def start_monitoring(background_tasks: BackgroundTasks):
    """Start continuous background monitoring"""

    global monitoring_active

    if monitoring_active:
        return JSONResponse(content={"message": "Monitoring already active", "status": "active"})

    async def monitoring_task():
        global monitoring_active, cached_status, last_status_check
        monitoring_active = True

        logger.info("Started continuous monitoring")

        try:
            while monitoring_active:
                # Update status every 5 minutes
                statuses = await status_monitor.get_current_status()
                status_monitor.generate_eq12_recommendations(statuses)

                # Update cached status
                cached_status = status_monitor.get_status_summary()
                last_status_check = datetime.utcnow()

                # Check for alerts
                if cached_status["overall_health"] < 80:
                    logger.warning(f"Health alert: {cached_status['overall_health']}%")

                # Wait 5 minutes
                await asyncio.sleep(300)

        except Exception as e:
            logger.error(f"Monitoring task error: {e}")
        finally:
            monitoring_active = False
            logger.info("Continuous monitoring stopped")

    background_tasks.add_task(monitoring_task)
    monitoring_active = True

    return JSONResponse(
        content={
            "message": "Continuous monitoring started",
            "status": "started",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.post("/api/monitoring/stop")
async def stop_monitoring():
    """Stop continuous background monitoring"""

    global monitoring_active
    monitoring_active = False

    return JSONResponse(
        content={
            "message": "Monitoring stop requested",
            "status": "stopping",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint for the dashboard itself"""

    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "monitoring_active": monitoring_active,
            "cached_status_age": (
                (datetime.utcnow() - last_status_check).total_seconds()
                if last_status_check
                else None
            ),
        }
    )


def main():
    """Main entry point for the dashboard server"""

    import argparse

    parser = argparse.ArgumentParser(description="EQ12 OpenAI Status Dashboard")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    args = parser.parse_args()

    print("🚀 Starting EQ12 OpenAI Status Dashboard")
    print(f"📊 Dashboard URL: http://{args.host}:{args.port}")
    print(f"🔌 API URL: http://{args.host}:{args.port}/api/status")

    uvicorn.run(
        "eq12_status_dashboard:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
