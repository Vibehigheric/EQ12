# EQ12 Real-time Dashboard System Documentation

## Overview

This is a comprehensive real-time dashboard system with WebSockets, health monitoring, Ngrok tunnel diagnostics, and structured observability for the EQ12 betting analytics platform.

## 🎯 Features Implemented

### ✅ Real-time Dashboards & WebSockets
- **Real-time WebSocket Dashboard** (`eq12_realtime_dashboard_system.py`)
  - Live betting analytics updates
  - WebSocket connection management
  - Real-time event broadcasting
  - Health monitoring integration
  - Governance rule engine with alerts
  - Performance metrics tracking

### ✅ Health Checks & Status Pages
- **Comprehensive Health Monitoring**
  - System resource monitoring (CPU, Memory, Disk)
  - Database connectivity checks
  - External API health verification
  - WebSocket connection health
  - Overall system status calculation
  - Automated health reporting

### ✅ Ngrok Tunnel Diagnostics
- **Ngrok Tunnel Management** (`eq12_ngrok_tunnel_diagnostics.py`)
  - Automated tunnel monitoring
  - Health checks with latency testing
  - Tunnel failover and restart capabilities
  - Comprehensive status reporting
  - Configuration management
  - Recommendation engine

### ✅ Modern React/Tailwind UI
- **Modern Dashboard Interface** (`eq12_modern_react_dashboard.js`)
  - Beautiful responsive design with Tailwind CSS
  - Real-time data visualization
  - Interactive parlay builder
  - Health status cards
  - Event stream display
  - WebSocket connection status

### ✅ JSON Schema & Structured Responses
- **Structured Observability** (`eq12_structured_observability.py`)
  - JSON schema validation for betting events
  - Structured logging with metadata
  - Distributed tracing capabilities
  - Metrics collection and export
  - Comprehensive error handling
  - Standardized API responses

### ✅ Comprehensive Integration
- **Unified System** (`eq12_comprehensive_integration_system.py`)
  - FastAPI backend with all components
  - Integrated dashboard with system management
  - RESTful API for system control
  - Automated component orchestration
  - Graceful startup and shutdown

## 🚀 Quick Start

### Prerequisites
```powershell
# Required packages
pip install fastapi uvicorn aiohttp pydantic psutil

# Optional packages (enhanced features)
pip install jsonschema opentelemetry websockets aiofiles
```

### Launch System
```powershell
# Easy launch with PowerShell script
powershell -ExecutionPolicy Bypass -File ./EQ12_Integrated_Dashboard_Launcher.ps1

# Or with custom ports
powershell -ExecutionPolicy Bypass -File ./EQ12_Integrated_Dashboard_Launcher.ps1 -Port 3000 -ApiPort 8080

# Development mode with verbose logging
powershell -ExecutionPolicy Bypass -File ./EQ12_Integrated_Dashboard_Launcher.ps1 -Mode dev -Verbose
```

### Manual Launch
```python
# Direct Python execution
python eq12_comprehensive_integration_system.py
```

## 🌐 Access URLs

After successful launch, access these URLs:

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:3001 | Main real-time dashboard |
| **Integrated UI** | http://localhost:8082/api/dashboard | Comprehensive management interface |
| **WebSocket** | ws://localhost:3001/ws | Real-time event stream |
| **Health Check** | http://localhost:3001/health | System health status |
| **System Status** | http://localhost:8082/api/system/status | Detailed system metrics |
| **Tunnel Status** | http://localhost:8082/api/tunnels/status | Ngrok tunnel diagnostics |
| **Ngrok Dashboard** | http://localhost:4040 | Ngrok management interface |

## 📊 API Endpoints

### System Management
```http
GET  /api/system/status           # Comprehensive system status
POST /api/system/restart-component # Restart specific component
GET  /api/observability/health    # Observability system health
```

### Tunnel Management
```http
GET  /api/tunnels/status                # Detailed tunnel status
POST /api/tunnels/restart/{tunnel_name} # Restart specific tunnel
```

### Betting Operations
```http
POST /api/parlay  # Create parlay with validation
POST /api/bet     # Place bet with governance checks
```

### Health & Monitoring
```http
GET  /health      # Basic health check
GET  /status      # Comprehensive status page
GET  /metrics     # Prometheus-style metrics
```

## 🔌 WebSocket Events

Connect to `ws://localhost:3001/ws?user_id=your_user_id`

### Event Types
- `parlay_update` - Real-time parlay changes
- `odds_change` - Odds movement notifications
- `system_alert` - System alerts and warnings
- `health_status` - Health monitoring updates
- `governance_trigger` - Governance rule violations
- `performance_metric` - Performance threshold alerts

### Message Format
```json
{
  "event_id": "uuid",
  "event_type": "parlay_update",
  "timestamp": "2025-01-01T12:00:00Z",
  "alert_level": "info",
  "data": {
    "message": "Event details",
    "additional_data": "..."
  },
  "user_id": "user123",
  "trace_id": "trace_uuid"
}
```

## 🏥 Health Monitoring

### Health Status Levels
- **healthy** - All systems operational
- **degraded** - Some issues detected, system functional
- **critical** - Major issues, immediate attention required
- **unknown** - Status cannot be determined

### Monitored Components
- System Resources (CPU, Memory, Disk)
- Database Connectivity
- External API Health
- WebSocket Connections
- Ngrok Tunnels
- Observability Pipeline

## 📝 Structured Logging

### Log Levels
- `debug` - Detailed diagnostic information
- `info` - General information messages
- `warning` - Warning conditions
- `error` - Error conditions
- `critical` - Critical error conditions

### Log Format
```json
{
  "timestamp": "2025-01-01T12:00:00Z",
  "level": "info",
  "message": "Operation completed",
  "component": "eq12_system",
  "event_type": "system_event",
  "user_id": "user123",
  "trace_id": "trace_uuid",
  "duration_ms": 45.2,
  "metadata": {}
}
```

## 🔍 JSON Schemas

### Parlay Schema
```json
{
  "parlay_id": "string",
  "user_id": "string",
  "legs": [
    {
      "selection": "string",
      "odds": "number",
      "market": "string"
    }
  ],
  "stake": "number",
  "total_odds": "number",
  "potential_payout": "number",
  "status": "pending|active|won|lost|void"
}
```

### Health Check Schema
```json
{
  "component": "string",
  "status": "healthy|degraded|critical|unknown",
  "timestamp": "string",
  "response_time_ms": "number",
  "details": {},
  "checks": [
    {
      "name": "string",
      "status": "boolean",
      "message": "string"
    }
  ]
}
```

## 🛡️ Governance Rules

### Built-in Rules
- **Daily Loss Limit** - Suspend betting after $500 daily loss
- **Single Bet Limit** - Require confirmation for bets > $100
- **Rapid Betting** - Cooling period after 10 bets in 5 minutes
- **Loss Streak** - Suggest break after 5 consecutive losses

### Rule Actions
- `suspend_betting` - Temporarily disable betting
- `require_confirmation` - Request user confirmation
- `cooling_period` - Enforced waiting period
- `suggest_break` - Recommend user take break

## 🔧 Configuration

### Environment Variables
```bash
EQ12_LOG_LEVEL=INFO|DEBUG
EQ12_ENVIRONMENT=development|production
EQ12_DASHBOARD_PORT=3001
EQ12_API_PORT=8082
EQ12_ENABLE_NGROK=true|false
```

### Config Files
- `C:/EQ12/configs/ngrok.yml` - Ngrok tunnel configuration
- `C:/EQ12/configs/observability_config.json` - Observability settings

## 📁 File Structure

```
C:/EQ12/
├── eq12_realtime_dashboard_system.py      # Real-time WebSocket dashboard
├── eq12_ngrok_tunnel_diagnostics.py       # Tunnel monitoring & failover
├── eq12_structured_observability.py       # Logging, metrics, tracing
├── eq12_modern_react_dashboard.js         # React/Tailwind frontend
├── eq12_comprehensive_integration_system.py # Unified system integration
├── EQ12_Integrated_Dashboard_Launcher.ps1 # PowerShell launcher script
├── test_integrated_dashboard.py           # System test suite
├── configs/
│   ├── ngrok.yml                          # Ngrok configuration
│   └── observability_config.json         # Observability settings
└── logs/
    ├── structured_logs.jsonl             # Structured log entries
    ├── metrics.jsonl                      # Metrics data
    ├── traces.jsonl                       # Distributed traces
    └── ngrok_diagnostics_YYYYMMDD.json   # Tunnel diagnostics
```

## 🧪 Testing

### Run Test Suite
```python
python test_integrated_dashboard.py
```

### Manual Testing
```powershell
# Health check
curl http://localhost:3001/health

# System status
curl http://localhost:8082/api/system/status

# WebSocket test (with websockets package)
python -c "
import asyncio
import websockets
import json

async def test_ws():
    async with websockets.connect('ws://localhost:3001/ws?user_id=test') as ws:
        await ws.send(json.dumps({'type': 'ping'}))
        response = await ws.recv()
        print('WebSocket response:', response)

asyncio.run(test_ws())
"
```

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**
   ```powershell
   # Kill processes on ports
   netstat -ano | findstr ":3001"
   taskkill /F /PID <process_id>
   ```

2. **Missing dependencies**
   ```powershell
   pip install fastapi uvicorn aiohttp pydantic psutil
   ```

3. **Ngrok not found**
   ```powershell
   # Download and install Ngrok
   # Add to PATH or place in C:/EQ12/
   ```

4. **WebSocket connection fails**
   - Check firewall settings
   - Verify ports are not blocked
   - Check dashboard is running

### Log Locations
- System logs: `C:/EQ12/logs/`
- Launcher logs: `C:/EQ12/logs/dashboard_launcher_*.log`
- Error logs: Check PowerShell output

## 🔄 System Management

### Restart Components
```http
POST http://localhost:8082/api/system/restart-component
Content-Type: application/json

{"component": "dashboard|ngrok|all"}
```

### Monitor System Health
```javascript
// Real-time health monitoring via WebSocket
const ws = new WebSocket('ws://localhost:3001/ws?user_id=admin');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.event_type === 'health_status') {
    console.log('Health Update:', data.data);
  }
};
```

## 🎯 Performance Metrics

### Key Metrics Tracked
- API response times
- WebSocket connection count
- System resource usage
- Tunnel latency and uptime
- Error rates and patterns
- User action frequencies

### Metrics Export
- Prometheus format: `GET /metrics`
- Structured logs: `C:/EQ12/logs/metrics.jsonl`
- Real-time via WebSocket events

## 🔮 Future Enhancements

### Planned Features
- [ ] Redis integration for session management
- [ ] Advanced analytics dashboard
- [ ] Mobile-responsive design improvements
- [ ] Machine learning betting insights
- [ ] Advanced governance rule builder
- [ ] Multi-tenant user management
- [ ] Enhanced security features
- [ ] Cloud deployment configurations

---

## 📞 Support

For issues or questions:
1. Check logs in `C:/EQ12/logs/`
2. Run test suite: `python test_integrated_dashboard.py`
3. Verify all URLs are accessible
4. Check system resources and ports

---

**EQ12 Real-time Dashboard System v2.1.0**
*Complete betting analytics platform with modern UI and comprehensive monitoring*
