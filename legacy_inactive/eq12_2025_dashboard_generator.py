#!/usr/bin/env python3
"""
EQ12 2025 Revenue Dashboard Generator
Creates real-time HTML dashboard for monitoring all 5 revenue streams
"""

import json
import os
from datetime import datetime
from pathlib import Path

CONFIG_PATH = "config/master_config.json"
OUTPUT_PATH = "reports/revenue_dashboard.html"

def load_config():
    """Load master configuration"""
    config_file = Path(CONFIG_PATH)
    if not config_file.exists():
        return create_default_config()
    
    with open(config_file, 'r') as f:
        return json.load(f)

def create_default_config():
    """Create default configuration structure"""
    return {
        "revenue_streams": {
            "betting_intelligence": {"enabled": True, "revenue": 0, "status": "idle", "error_count": 0, "last_run": None},
            "prompt_monetization": {"enabled": True, "revenue": 0, "status": "idle", "error_count": 0, "last_run": None},
            "pacer_legal": {"enabled": True, "revenue": 0, "status": "idle", "error_count": 0, "last_run": None},
            "travel_automation": {"enabled": True, "revenue": 0, "status": "idle", "error_count": 0, "last_run": None},
            "content_empire": {"enabled": True, "revenue": 0, "status": "idle", "error_count": 0, "last_run": None}
        },
        "performance_metrics": {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0
        }
    }

def generate_dashboard(config):
    """Generate HTML dashboard"""
    
    # Calculate metrics
    stream_targets = {
        "betting_intelligence": {"target": 300000, "priority": 1, "name": "AI Betting Intelligence Suite"},
        "prompt_monetization": {"target": 150000, "priority": 1, "name": "AI Prompt Monetization Engine"},
        "pacer_legal": {"target": 12500, "priority": 2, "name": "PACER Legal Intelligence"},
        "travel_automation": {"target": 25000, "priority": 3, "name": "Travel Deal Automation"},
        "content_empire": {"target": 75000, "priority": 2, "name": "Content Empire Builder"}
    }
    
    total_target = sum(info["target"] for info in stream_targets.values())
    total_actual = sum(config["revenue_streams"][sid]["revenue"] for sid in stream_targets.keys())
    achievement_pct = (total_actual / total_target * 100) if total_target > 0 else 0
    
    total_exec = config["performance_metrics"]["total_executions"]
    success_exec = config["performance_metrics"]["successful_executions"]
    success_rate = (success_exec / total_exec * 100) if total_exec > 0 else 0
    
    streams_enabled = sum(1 for s in config["revenue_streams"].values() if s["enabled"])
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="300">
    <title>EQ12 2025 Revenue Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 3px solid rgba(255,255,255,0.2);
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{ font-size: 1.2em; opacity: 0.9; }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s;
        }}
        .metric-card:hover {{ transform: translateY(-5px); }}
        .metric-card h3 {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .metric-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .metric-card .label {{ font-size: 0.9em; opacity: 0.7; }}
        .streams-section {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .streams-section h2 {{
            font-size: 2em;
            margin-bottom: 20px;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 10px;
        }}
        .stream {{
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 5px solid;
        }}
        .stream.priority-1 {{ border-left-color: #ff6b6b; }}
        .stream.priority-2 {{ border-left-color: #ffd93d; }}
        .stream.priority-3 {{ border-left-color: #6bcf7f; }}
        .stream-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .stream-name {{
            font-size: 1.3em;
            font-weight: bold;
        }}
        .stream-status {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .status-completed {{ background: #4caf50; }}
        .status-running {{ background: #2196f3; }}
        .status-failed {{ background: #f44336; }}
        .status-idle {{ background: #9e9e9e; }}
        .stream-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .stream-detail {{
            background: rgba(255,255,255,0.05);
            padding: 10px;
            border-radius: 5px;
        }}
        .stream-detail label {{
            display: block;
            font-size: 0.8em;
            opacity: 0.7;
            margin-bottom: 5px;
        }}
        .stream-detail .value {{ font-size: 1.1em; font-weight: bold; }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.2);
            opacity: 0.7;
        }}
        .progress-bar {{
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            height: 30px;
            overflow: hidden;
            margin-top: 10px;
        }}
        .progress-fill {{
            background: linear-gradient(90deg, #4caf50, #8bc34a);
            height: 100%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 EQ12 2025 Revenue Dashboard</h1>
            <p>Real-Time Monitoring | 5 Revenue Streams | $12M Annual Target</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Last Updated: {datetime.now().strftime('%B %d, %Y %H:%M:%S')}</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <h3>💰 Monthly Revenue</h3>
                <div class="value">${total_actual:,.0f}</div>
                <div class="label">of ${total_target:,.0f} target</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {achievement_pct:.0f}%">
                        {achievement_pct:.1f}%
                    </div>
                </div>
            </div>

            <div class="metric-card">
                <h3>📊 Success Rate</h3>
                <div class="value">{success_rate:.1f}%</div>
                <div class="label">{success_exec} of {total_exec} executions</div>
            </div>

            <div class="metric-card">
                <h3>🎯 Active Streams</h3>
                <div class="value">{streams_enabled}</div>
                <div class="label">of 5 revenue streams</div>
            </div>

            <div class="metric-card">
                <h3>⚡ Status</h3>
                <div class="value">{'✅' if success_rate >= 90 else '⚠️' if success_rate >= 70 else '❌'}</div>
                <div class="label">{'Excellent' if success_rate >= 90 else 'Good' if success_rate >= 70 else 'Needs Attention'}</div>
            </div>
        </div>

        <div class="streams-section">
            <h2>💼 Revenue Streams</h2>
"""
    
    # Add each stream
    for stream_id, stream_info in stream_targets.items():
        stream_data = config["revenue_streams"][stream_id]
        status_class = f"status-{stream_data['status']}"
        last_run = datetime.fromisoformat(stream_data['last_run']).strftime('%m/%d %H:%M') if stream_data['last_run'] else 'Never'
        
        html += f"""
            <div class="stream priority-{stream_info['priority']}">
                <div class="stream-header">
                    <div class="stream-name">{stream_info['name']}</div>
                    <div class="stream-status {status_class}">{stream_data['status'].upper()}</div>
                </div>
                <div class="stream-details">
                    <div class="stream-detail">
                        <label>💰 Monthly Target</label>
                        <div class="value">${stream_info['target']:,.0f}</div>
                    </div>
                    <div class="stream-detail">
                        <label>📈 Actual Revenue</label>
                        <div class="value">${stream_data['revenue']:,.0f}</div>
                    </div>
                    <div class="stream-detail">
                        <label>⚠️ Error Count</label>
                        <div class="value">{stream_data['error_count']}</div>
                    </div>
                    <div class="stream-detail">
                        <label>🕒 Last Run</label>
                        <div class="value">{last_run}</div>
                    </div>
                </div>
            </div>
"""
    
    html += """
        </div>

        <div class="footer">
            <p>Auto-refreshes every 5 minutes</p>
            <p>EQ12 2025 Master Orchestrator | Built with Python</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    print("📊 Generating EQ12 2025 Revenue Dashboard...")
    
    # Load config
    config = load_config()
    
    # Generate HTML
    html = generate_dashboard(config)
    
    # Save dashboard
    output_file = Path(OUTPUT_PATH)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Dashboard generated: {output_file.absolute()}")
    
    # Try to open in browser
    try:
        import webbrowser
        webbrowser.open(str(output_file.absolute()))
        print("🌐 Opening dashboard in browser...")
    except:
        print(f"💡 Open manually: {output_file.absolute()}")

if __name__ == "__main__":
    main()
