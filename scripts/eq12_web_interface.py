#!/usr/bin/env python3
"""
EQ12 Web Interface Backend - AI Enterprise Control Center
========================================================
FastAPI backend for the complete EQ12 AI enterprise web dashboard
"""

from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import json
import logging
import subprocess
import psutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import sqlite3


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state tracking
system_state = {
    "active_processes": {},
    "system_health": {},
    "ai_models": {},
    "revenue_metrics": {},
    "betting_results": {},
    "connected_clients": set()
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown operations"""
    # Startup operations
    logger.info(" EQ12 Web Interface starting up...")
    init_database()
    logger.info(" EQ12 Web Interface started")
    
    yield
    
    # Shutdown operations
    logger.info(" EQ12 Web Interface shutting down...")
    # Close any open connections, cleanup resources
    system_state["connected_clients"].clear()
    logger.info(" EQ12 Web Interface shutdown complete")


# Initialize FastAPI with lifespan
app = FastAPI(
    title="EQ12 AI Enterprise Control Center", 
    version="1.0.0",
    lifespan=lifespan
)

class CommandRequest(BaseModel):
    command: str
    params: Optional[Dict[str, Any]] = {}

class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_usage: Dict[str, float]
    active_processes: int
    uptime: str

class AIModelStatus(BaseModel):
    name: str
    status: str
    accuracy: Optional[float] = None
    last_updated: str

class BettingPrediction(BaseModel):
    prediction: str
    confidence: float
    recommendation: str
    timestamp: str

# Initialize database
def init_database():
    """Initialize SQLite database for logs and metrics"""
    db_path = Path("C:/EQ12/data/eq12_web.db")
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            level TEXT,
            module TEXT,
            message TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            command TEXT,
            status TEXT,
            duration_ms INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS revenue_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source TEXT,
            amount REAL,
            currency TEXT
        )
    """)
    
    conn.commit()
    conn.close()


# Model classes
class CommandRequest(BaseModel):
    command: str
    params: Optional[Dict[str, Any]] = {}


class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    disk_usage: Dict[str, float]
    active_processes: int
    uptime: str


class AIModelStatus(BaseModel):
    name: str
    status: str
    accuracy: Optional[float] = None
    last_updated: str


class BettingPrediction(BaseModel):
    prediction: str
    confidence: float
    recommendation: str
    timestamp: str


# System Monitoring Endpoints
@app.get("/api/system/health")
async def get_system_health():
    """Get real-time system health metrics"""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('C:/')
        
        # Calculate health score
        health_score = (
            (100 - cpu_percent) * 0.3 +
            (100 - memory.percent) * 0.4 +
            (disk.free / disk.total * 100) * 0.3
        ) / 100
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_free_gb": disk.free / (1024**3),
            "disk_total_gb": disk.total / (1024**3),
            "health_score": health_score,
            "status": "healthy" if health_score > 0.7 else "warning" if health_score > 0.5 else "critical"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/processes")
async def get_active_processes():
    """Get EQ12-related active processes"""
    eq12_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
        try:
            if any('eq12' in str(item).lower() for item in proc.info['cmdline'] or []):
                eq12_processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cpu_percent": proc.info['cpu_percent'],
                    "memory_mb": proc.info['memory_info'].rss / (1024*1024) if proc.info['memory_info'] else 0,
                    "cmdline": ' '.join(proc.info['cmdline'] or [])
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return {"processes": eq12_processes, "count": len(eq12_processes)}

# EQ12 Command Execution
@app.post("/api/commands/execute")
async def execute_command(command_request: CommandRequest, background_tasks: BackgroundTasks):
    """Execute EQ12 commands via web interface"""
    command = command_request.command
    params = command_request.params
    
    # Command mapping
    command_map = {
        "run-odds": "python C:/EQ12/scripts/eq12_run_odds.py",
        "run-parlay": "python C:/EQ12/scripts/eq12_run_parlay.py",
        "betting-suite": "python C:/EQ12/eq12_betting_suite.py",
        "health-check": "python C:/EQ12/eq12_final_system_validation.py",
        "ai-train": "python C:/EQ12/scripts/eq12_ai_trainer.py --model all",
        "ai-inference": "python C:/EQ12/scripts/eq12_ai_inference_engine.py --auto",
        "free-mode": "powershell -ExecutionPolicy Bypass -File C:/EQ12/eq12_free_mode_switcher.ps1 -Service all",
        "system-repair": "python C:/EQ12/eq12_hardcoded_repair_emergency_protocol.py --workspace C:/EQ12"
    }
    
    if command not in command_map:
        raise HTTPException(status_code=400, detail=f"Unknown command: {command}")
    
    start_time = datetime.now()
    
    try:
        # Execute command
        cmd_line = command_map[command]
        if params.get("verbose"):
            cmd_line += " --verbose"
        
        result = subprocess.run(
            cmd_line.split(), 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log command execution
        background_tasks.add_task(log_command_execution, command, "success" if result.returncode == 0 else "failed", duration)
        
        return {
            "command": command,
            "status": "success" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration_ms": duration,
            "timestamp": start_time.isoformat()
        }
        
    except subprocess.TimeoutExpired:
        return {
            "command": command,
            "status": "timeout",
            "error": "Command timed out after 300 seconds",
            "timestamp": start_time.isoformat()
        }
    except Exception as e:
        return {
            "command": command,
            "status": "error",
            "error": str(e),
            "timestamp": start_time.isoformat()
        }

# AI Model Management
@app.get("/api/ai/models/status")
async def get_ai_models_status():
    """Get status of all AI models"""
    models_dir = Path("C:/EQ12/ai_models")
    models = []
    
    if models_dir.exists():
        for metadata_file in models_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                model_name = metadata_file.stem.replace("_metadata", "")
                models.append({
                    "name": model_name,
                    "type": metadata.get("model_type", "unknown"),
                    "accuracy": metadata.get("test_accuracy", metadata.get("test_r2", 0)),
                    "trained_at": metadata.get("trained_at", ""),
                    "status": "trained"
                })
            except Exception as e:
                logger.error(f"Error reading model metadata: {e}")
    
    return {"models": models, "count": len(models)}

@app.post("/api/ai/inference/betting")
async def run_betting_inference():
    """Run AI betting inference"""
    try:
        result = subprocess.run([
            "python", "C:/EQ12/scripts/eq12_ai_inference_engine.py", 
            "--betting", "--confidence-threshold", "0.75"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # Parse JSON output
            try:
                inference_result = json.loads(result.stdout)
                return inference_result
            except json.JSONDecodeError:
                return {"error": "Failed to parse inference result", "raw_output": result.stdout}
        else:
            return {"error": result.stderr}
            
    except Exception as e:
        return {"error": str(e)}

# Revenue and Analytics
@app.get("/api/revenue/summary")
async def get_revenue_summary():
    """Get revenue summary and metrics"""
    try:
        # Read from betting suite logs
        logs_dir = Path("C:/EQ12/logs")
        revenue_data = {
            "total_revenue": 0,
            "monthly_savings": 375,  # From cost optimization
            "betting_profit": 0,
            "api_costs": 0,
            "net_profit": 0
        }
        
        # Try to find latest revenue data
        for log_file in logs_dir.glob("*revenue*.json"):
            try:
                with open(log_file, 'r') as f:
                    data = json.load(f)
                    if "revenue" in data:
                        revenue_data["total_revenue"] += data.get("revenue", 0)
            except:
                continue
        
        revenue_data["net_profit"] = revenue_data["total_revenue"] + revenue_data["monthly_savings"] - revenue_data["api_costs"]
        
        return revenue_data
        
    except Exception as e:
        return {"error": str(e)}

# GitHub Integration
@app.get("/api/github/repos")
async def get_github_repos():
    """Get GitHub repository information"""
    # Mock data - in real implementation, use GitHub API
    return {
        "repos": [
            {
                "name": "EQ12-AI-Enterprise",
                "description": "AI-powered betting and automation suite",
                "stars": 42,
                "forks": 8,
                "language": "Python",
                "updated_at": "2025-11-07T20:00:00Z",
                "sponsor_url": "https://github.com/sponsors/yourusername"
            }
        ]
    }

# WebSocket for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    system_state["connected_clients"].add(websocket)
    
    try:
        while True:
            # Send periodic system updates
            health_data = await get_system_health()
            await websocket.send_json({
                "type": "system_health",
                "data": health_data
            })
            
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        system_state["connected_clients"].discard(websocket)

# Utility functions
async def log_command_execution(command: str, status: str, duration: float):
    """Log command execution to database"""
    try:
        conn = sqlite3.connect("C:/EQ12/data/eq12_web.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO command_history (timestamp, command, status, duration_ms)
            VALUES (?, ?, ?, ?)
        """, (datetime.now().isoformat(), command, status, duration))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log command: {e}")

# Static file serving (for frontend)
@app.get("/")
async def serve_dashboard():
    """Serve the main dashboard"""
    return HTMLResponse(content=get_dashboard_html(), status_code=200)

def get_dashboard_html():
    """Generate the main dashboard HTML"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 AI Enterprise Control Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/chart.js"></script>
    <style>
        .bg-gradient-eq12 { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { @apply bg-white rounded-lg shadow-lg p-6 m-4; }
        .btn-primary { @apply bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded; }
        .btn-danger { @apply bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded; }
        .status-indicator { @apply inline-block w-3 h-3 rounded-full mr-2; }
        .status-healthy { @apply bg-green-500; }
        .status-warning { @apply bg-yellow-500; }
        .status-critical { @apply bg-red-500; }
    </style>
</head>
<body class="bg-gray-100">
    <header class="bg-gradient-eq12 text-white p-6">
        <div class="container mx-auto">
            <h1 class="text-3xl font-bold"> EQ12 AI Enterprise Control Center</h1>
            <p class="text-blue-100 mt-2">Autonomous Betting & AI Management System</p>
        </div>
    </header>

    <div class="container mx-auto px-4 py-8">
        <!-- System Status Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="card">
                <h3 class="text-lg font-semibold mb-2">System Health</h3>
                <div id="health-status" class="flex items-center">
                    <span class="status-indicator status-healthy"></span>
                    <span id="health-score">Loading...</span>
                </div>
                <div class="mt-2 text-sm text-gray-600">
                    <div>CPU: <span id="cpu-usage">--%</span></div>
                    <div>RAM: <span id="ram-usage">--%</span></div>
                </div>
            </div>

            <div class="card">
                <h3 class="text-lg font-semibold mb-2">AI Models</h3>
                <div id="ai-models-status">
                    <div class="text-2xl font-bold text-green-600" id="models-count">0</div>
                    <div class="text-sm text-gray-600">Models Trained</div>
                </div>
            </div>

            <div class="card">
                <h3 class="text-lg font-semibold mb-2">Revenue</h3>
                <div id="revenue-status">
                    <div class="text-2xl font-bold text-green-600">$<span id="total-revenue">0</span></div>
                    <div class="text-sm text-gray-600">Net Profit</div>
                </div>
            </div>

            <div class="card">
                <h3 class="text-lg font-semibold mb-2">Betting Suite</h3>
                <div id="betting-status">
                    <div class="text-2xl font-bold text-blue-600" id="betting-success">100%</div>
                    <div class="text-sm text-gray-600">Success Rate</div>
                </div>
            </div>
        </div>

        <!-- Command Center -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="card">
                <h3 class="text-xl font-semibold mb-4"> Command Center</h3>
                <div class="grid grid-cols-2 gap-3">
                    <button class="btn-primary" onclick="executeCommand('betting-suite')">
                         Run Betting Suite
                    </button>
                    <button class="btn-primary" onclick="executeCommand('ai-inference')">
                         AI Inference
                    </button>
                    <button class="btn-primary" onclick="executeCommand('health-check')">
                         System Health Check
                    </button>
                    <button class="btn-primary" onclick="executeCommand('free-mode')">
                         Activate Free Mode
                    </button>
                    <button class="btn-primary" onclick="executeCommand('ai-train')">
                         Train AI Models
                    </button>
                    <button class="btn-danger" onclick="executeCommand('system-repair')">
                         Emergency Repair
                    </button>
                </div>
                <div id="command-output" class="mt-4 p-3 bg-gray-900 text-green-400 font-mono text-sm rounded max-h-48 overflow-y-auto hidden"></div>
            </div>

            <div class="card">
                <h3 class="text-xl font-semibold mb-4"> Live System Metrics</h3>
                <canvas id="systemChart" width="400" height="200"></canvas>
            </div>
        </div>

        <!-- AI Inference Results -->
        <div class="card mt-8">
            <h3 class="text-xl font-semibold mb-4"> Latest AI Predictions</h3>
            <div id="ai-predictions" class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="p-4 bg-blue-50 rounded">
                    <h4 class="font-semibold">Betting Prediction</h4>
                    <div id="betting-prediction">Click "AI Inference" to run</div>
                </div>
                <div class="p-4 bg-green-50 rounded">
                    <h4 class="font-semibold">System Anomaly</h4>
                    <div id="anomaly-status">Normal Operation</div>
                </div>
                <div class="p-4 bg-purple-50 rounded">
                    <h4 class="font-semibold">Revenue Optimization</h4>
                    <div id="revenue-optimization">Optimized</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // WebSocket connection for real-time updates
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.type === 'system_health') {
                updateSystemHealth(data.data);
            }
        };

        // API functions
        async function executeCommand(command) {
            const outputDiv = document.getElementById('command-output');
            outputDiv.classList.remove('hidden');
            outputDiv.innerHTML = `Executing ${command}...`;

            try {
                const response = await fetch('/api/commands/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: command})
                });
                
                const result = await response.json();
                outputDiv.innerHTML = `
                    <div class="mb-2"><strong>${command}</strong> - Status: ${result.status}</div>
                    <div class="text-xs">${result.stdout || result.error || 'No output'}</div>
                `;
                
                // Refresh data after command execution
                await refreshDashboard();
                
            } catch (error) {
                outputDiv.innerHTML = `Error executing ${command}: ${error.message}`;
            }
        }

        async function refreshDashboard() {
            try {
                // Update AI models status
                const modelsResponse = await fetch('/api/ai/models/status');
                const modelsData = await modelsResponse.json();
                document.getElementById('models-count').textContent = modelsData.count;

                // Update revenue data
                const revenueResponse = await fetch('/api/revenue/summary');
                const revenueData = await revenueResponse.json();
                document.getElementById('total-revenue').textContent = revenueData.net_profit.toFixed(0);

            } catch (error) {
                console.error('Error refreshing dashboard:', error);
            }
        }

        function updateSystemHealth(healthData) {
            document.getElementById('health-score').textContent = `${(healthData.health_score * 100).toFixed(1)}%`;
            document.getElementById('cpu-usage').textContent = `${healthData.cpu_percent.toFixed(1)}%`;
            document.getElementById('ram-usage').textContent = `${healthData.memory_percent.toFixed(1)}%`;
            
            // Update status indicator
            const indicator = document.querySelector('.status-indicator');
            indicator.className = `status-indicator status-${healthData.status === 'healthy' ? 'healthy' : healthData.status === 'warning' ? 'warning' : 'critical'}`;
        }

        // Initialize dashboard
        refreshDashboard();
        
        // Setup chart
        const ctx = document.getElementById('systemChart').getContext('2d');
        const systemChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU %',
                    data: [],
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)'
                }, {
                    label: 'RAM %',
                    data: [],
                    borderColor: 'rgb(16, 185, 129)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });

        // Update chart with WebSocket data
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.type === 'system_health') {
                updateSystemHealth(data.data);
                
                // Update chart
                const now = new Date().toLocaleTimeString();
                systemChart.data.labels.push(now);
                systemChart.data.datasets[0].data.push(data.data.cpu_percent);
                systemChart.data.datasets[1].data.push(data.data.memory_percent);
                
                // Keep only last 20 data points
                if (systemChart.data.labels.length > 20) {
                    systemChart.data.labels.shift();
                    systemChart.data.datasets[0].data.shift();
                    systemChart.data.datasets[1].data.shift();
                }
                
                systemChart.update();
            }
        };
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")