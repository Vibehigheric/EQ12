"""
EQ12 VB.NET Interface - Flask API Bridge
Enables VB.NET Control Center to communicate with Python backend
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time
import psutil
from datetime import datetime
from typing import Dict, Any
import sys
import os

# Add scripts directory to path
sys.path.append(os.path.dirname(__file__))

# Import existing EQ12 modules
from eq12_resource_monitor import ResourceMonitor, get_safe_worker_count
from eq12_live_sports_scanner_1hour import LiveSportsScanner

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests

# Global state
resource_monitor = ResourceMonitor()
scanner_instance = None
scanner_thread = None
scanner_running = False

# System state
system_state = {
    "cpu_percent": 0.0,
    "memory_percent": 0.0,
    "memory_used_gb": 0.0,
    "memory_available_gb": 0.0,
    "disk_percent": 0.0,
    "disk_free_gb": 0.0,
    "active_workers": 0,
    "scanner_workers": 0,
    "validator_workers": 0,
    "bankroll_workers": 0,
    "scanner_status": "idle",
    "validator_status": "idle",
    "bankroll_status": "idle",
    "total_opportunities": 0,
    "latest_opportunities": []
}

def update_system_state():
    """Background thread to update system state every 5 seconds"""
    global system_state
    
    while True:
        try:
            # Capture metrics
            metrics = resource_monitor.capture_metrics(
                active_workers=system_state['active_workers']
            )
            
            # Update state
            system_state.update({
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "memory_used_gb": metrics.memory_used_gb,
                "memory_available_gb": metrics.memory_available_gb,
                "disk_free_gb": psutil.disk_usage('C:\\').free / (1024**3),
                "disk_percent": psutil.disk_usage('C:\\').percent
            })
            
            # Get scanner status if running
            if scanner_instance:
                system_state["scanner_status"] = "running"
                system_state["total_opportunities"] = scanner_instance.results.get("total_opportunities", 0)
                
                # Get latest opportunities
                latest = []
                for opp in scanner_instance.results.get("arbitrage", [])[:10]:
                    latest.append({
                        "sport": opp.get("sport", "Unknown"),
                        "game": opp.get("game", "Unknown"),
                        "market_type": opp.get("market", "Unknown"),
                        "profit_margin": opp.get("profit_margin", 0.0),
                        "expected_value": opp.get("ev", 0.0),
                        "timestamp": datetime.now().isoformat()
                    })
                
                system_state["latest_opportunities"] = latest
            else:
                system_state["scanner_status"] = "idle"
            
        except Exception as e:
            print(f"Error updating system state: {e}")
        
        time.sleep(5)

# Start background update thread
update_thread = threading.Thread(target=update_system_state, daemon=True)
update_thread.start()

# API Endpoints

@app.route('/status', methods=['GET'])
def get_status():
    """VB.NET polls this for dashboard updates"""
    return jsonify(system_state)

@app.route('/scanner/start', methods=['POST'])
def start_scanner():
    """Start sports scanner"""
    global scanner_instance, scanner_thread, scanner_running
    
    try:
        data = request.json or {}
        workers = data.get('workers', get_safe_worker_count())
        duration = data.get('duration', 60)
        
        if scanner_running:
            return jsonify({"error": "Scanner already running"}), 400
        
        # Get API key
        api_key = os.getenv("ODDS_API_KEY")
        if not api_key:
            return jsonify({"error": "ODDS_API_KEY not set"}), 500
        
        # Create scanner instance
        scanner_instance = LiveSportsScanner(api_key=api_key, max_workers=workers)
        
        # Run in background thread
        def run_scanner():
            global scanner_running
            scanner_running = True
            system_state["scanner_workers"] = workers
            system_state["active_workers"] = workers
            
            try:
                # Run scanner (simplified - actual implementation may vary)
                print(f"Starting scanner with {workers} workers for {duration} minutes")
                # scanner_instance.run_scan()  # Actual scan method
                
            except Exception as e:
                print(f"Scanner error: {e}")
            finally:
                scanner_running = False
                system_state["scanner_workers"] = 0
                system_state["active_workers"] = 0
                system_state["scanner_status"] = "idle"
        
        scanner_thread = threading.Thread(target=run_scanner, daemon=True)
        scanner_thread.start()
        
        return jsonify({
            "status": "started",
            "workers": workers,
            "duration": duration
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scanner/stop', methods=['POST'])
def stop_scanner():
    """Stop sports scanner"""
    global scanner_running
    
    if not scanner_running:
        return jsonify({"error": "Scanner not running"}), 400
    
    scanner_running = False
    system_state["scanner_status"] = "stopping"
    
    return jsonify({"status": "stopping"})

@app.route('/validator/start', methods=['POST'])
def start_validator():
    """Start parlay validator"""
    try:
        system_state["validator_status"] = "running"
        system_state["validator_workers"] = 5
        system_state["active_workers"] += 5
        
        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/validator/stop', methods=['POST'])
def stop_validator():
    """Stop parlay validator"""
    system_state["validator_status"] = "idle"
    system_state["validator_workers"] = 0
    system_state["active_workers"] = max(0, system_state["active_workers"] - 5)
    
    return jsonify({"status": "stopped"})

@app.route('/bankroll/status', methods=['GET'])
def get_bankroll_status():
    """Get bankroll status"""
    # TODO: Integrate with actual bankroll manager
    return jsonify({
        "balance": 10000.0,
        "profit_loss": 0.0,
        "total_bets": 0,
        "win_rate": 0.0
    })

@app.route('/opportunities/latest', methods=['GET'])
def get_latest_opportunities():
    """Get latest opportunities"""
    return jsonify(system_state["latest_opportunities"])

@app.route('/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify({
        "default_workers": get_safe_worker_count(),
        "max_workers": 10,
        "min_workers": 2,
        "memory_total_gb": psutil.virtual_memory().total / (1024**3),
        "cpu_count": psutil.cpu_count()
    })

@app.route('/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        data = request.json
        # TODO: Save configuration to file
        return jsonify({"status": "updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

if __name__ == '__main__':
    print("="*60)
    print("EQ12 VB.NET API Bridge Starting...")
    print("="*60)
    print(f"Listening on: http://localhost:5000")
    print(f"Safe worker count: {get_safe_worker_count()}")
    print(f"System RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    print(f"CPU threads: {psutil.cpu_count()}")
    print("="*60)
    print("\nEndpoints:")
    print("  GET  /status - System status")
    print("  POST /scanner/start - Start scanner")
    print("  POST /scanner/stop - Stop scanner")
    print("  POST /validator/start - Start validator")
    print("  POST /validator/stop - Stop validator")
    print("  GET  /bankroll/status - Bankroll status")
    print("  GET  /opportunities/latest - Latest opportunities")
    print("  GET  /config - Get configuration")
    print("  POST /config - Update configuration")
    print("  GET  /health - Health check")
    print("="*60)
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='localhost', port=5000, debug=False)
