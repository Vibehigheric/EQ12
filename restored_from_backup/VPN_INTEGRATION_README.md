# EQ12 VPN Integration - Complete Setup Guide
# Comprehensive VPN security and automation for EQ12 betting system

## 🔐 **Complete VPN Security Stack Delivered**

Your EQ12 system now has enterprise-grade VPN integration with:

### **📦 Delivered Components**

1. **PowerShell VPN Guard** (`eq12_vpn_guard.ps1`)
   - ✅ WireGuard connection management
   - ✅ Automatic reconnection on drops
   - ✅ Pipeline kill-switch protection
   - ✅ Comprehensive audit logging
   - ✅ Multi-IP verification system

2. **Python Pipeline Controller** (`vpn_pipeline_controller.py`)
   - ✅ VPN-dependent betting operations
   - ✅ Graceful shutdown on VPN failure
   - ✅ Multi-module pipeline management
   - ✅ Real-time monitoring integration

3. **Advanced Health Monitor** (`vpn_health_monitor.py`)
   - ✅ Continuous security validation
   - ✅ IP/DNS leak detection
   - ✅ Performance monitoring
   - ✅ Automated threat response
   - ✅ Comprehensive reporting

4. **Database Schema** (`database/vpn_audit_schema.sql`)
   - ✅ Complete audit trail
   - ✅ Performance metrics tracking
   - ✅ Security event logging
   - ✅ Compliance reporting views

5. **Task Scheduler Integration**
   - ✅ XML configuration (`EQ12_VPN_Guard_Task.xml`)
   - ✅ Setup script (`setup_vpn_task.ps1`)
   - ✅ Automatic startup configuration
   - ✅ System-level integration

---

## 🚀 **Quick Setup (5 Minutes)**

### **Step 1: Install WireGuard**
```powershell
# Download and install WireGuard
winget install WireGuard.WireGuard
```

### **Step 2: Configure VPN**
```powershell
# Create VPN config directory
New-Item -Path "C:\EQ12\wireguard" -ItemType Directory -Force

# Copy your VPN config to: C:\EQ12\wireguard\eq12-betting.conf
# Example config format:
[Interface]
PrivateKey = YOUR_PRIVATE_KEY
Address = 10.0.0.2/24
DNS = 1.1.1.1

[Peer]
PublicKey = SERVER_PUBLIC_KEY
Endpoint = vpn.yourprovider.com:51820
AllowedIPs = 0.0.0.0/0
```

### **Step 3: Setup Database**
```powershell
# Install SQLite (if not installed)
winget install SQLite.SQLite

# Initialize VPN audit database
sqlite3 C:\EQ12\eq12_bets.db < C:\EQ12\database\vpn_audit_schema.sql
```

### **Step 4: Configure Task Scheduler**
```powershell
# Run as Administrator
Set-ExecutionPolicy Bypass -Scope CurrentUser
.\setup_vpn_task.ps1 -Force
```

### **Step 5: Test Everything**
```powershell
# Test VPN Guard manually
.\eq12_vpn_guard.ps1 -VpnConfig "eq12-betting" -RunPipeline

# Test Task Scheduler
.\setup_vpn_task.ps1 -Test
```

---

## 🛡️ **Security Features**

### **Multi-Layer Protection**
- **Kill Switch**: Instantly stops betting on VPN failure
- **IP Leak Detection**: Validates real IP is hidden
- **DNS Leak Protection**: Ensures queries are secure
- **Automatic Reconnection**: Up to 5 attempts with exponential backoff
- **Audit Trail**: Complete logging for compliance

### **Performance Monitoring**
- **Latency Tracking**: Real-time connection quality
- **Bandwidth Monitoring**: Performance optimization
- **Uptime Calculation**: Reliability metrics
- **Security Scoring**: 0-100 security assessment

### **Automated Responses**
- **Threat Detection**: IP/DNS leaks, performance issues
- **Auto-Remediation**: Reconnect VPN, stop processes
- **Alert System**: Telegram/email notifications (configurable)

---

## 📊 **Usage Examples**

### **Basic VPN Protection**
```powershell
# Start VPN with betting pipeline
.\eq12_vpn_guard.ps1 -VpnConfig "eq12-betting" -RunPipeline -KillOnVpnDrop
```

### **Monitoring Only**
```powershell
# Monitor existing VPN without managing connection
.\eq12_vpn_guard.ps1 -MonitorOnly -MonitorIntervalSeconds 15
```

### **Python Integration**
```python
# Start Python pipeline with VPN dependency
from vpn_pipeline_controller import VpnPipelineController

controller = VpnPipelineController()
controller.run()  # Won't start betting unless VPN active
```

### **Health Monitoring**
```python
# Continuous security monitoring
from vpn_health_monitor import VpnHealthMonitor

monitor = VpnHealthMonitor()
monitor.start_monitoring()  # IP/DNS leak detection, performance tracking
```

---

## 📈 **Monitoring & Reporting**

### **Real-Time Status**
```powershell
# Check current VPN status
Get-ScheduledTask -TaskName "EQ12_VPN_Guard"

# View recent logs
Get-Content C:\EQ12\logs\vpn_guard.log -Tail 20
```

### **Database Queries**
```sql
-- Current VPN status
SELECT * FROM v_current_vpn_status;

-- Daily uptime report
SELECT * FROM v_vpn_uptime_report;

-- Recent security events
SELECT * FROM vpn_security_events
WHERE timestamp > strftime('%s', 'now', '-1 day')
ORDER BY timestamp DESC;
```

### **Health Report**
```python
# Generate comprehensive health report
monitor = VpnHealthMonitor()
report = monitor.get_health_report()
print(json.dumps(report, indent=2))
```

---

## 🔧 **Configuration Files**

### **VPN Pipeline Config** (`configs/vpn_pipeline_config.json`)
```json
{
    "vpn": {
        "config_name": "eq12-betting",
        "required_regions": ["US", "UK", "CA"],
        "reconnect_attempts": 5,
        "health_check_interval": 30
    },
    "security": {
        "kill_on_ip_leak": true,
        "dns_leak_protection": true,
        "auto_remediation": true
    },
    "pipeline": {
        "modules": ["odds_scraper", "parlay_builder", "telegram_bot"],
        "restart_on_vpn_recovery": true
    }
}
```

### **Health Monitor Config** (`configs/vpn_health_config.json`)
```json
{
    "monitoring": {
        "check_interval_seconds": 30,
        "alert_thresholds": {
            "latency_warning_ms": 200,
            "uptime_warning_percent": 95
        }
    },
    "security": {
        "check_ip_leaks": true,
        "check_dns_leaks": true,
        "auto_remediation": true
    }
}
```

---

## 🎯 **Integration with EQ12 Master Profile**

Add these functions to your EQ12 PowerShell profile:

```powershell
function Start-EQ12VPN {
    & "C:\EQ12\eq12_vpn_guard.ps1" -VpnConfig "eq12-betting" -RunPipeline
}

function Get-EQ12VPNStatus {
    $task = Get-ScheduledTask -TaskName "EQ12_VPN_Guard" -ErrorAction SilentlyContinue
    if ($task) {
        Write-Host "VPN Task Status: $($task.State)" -ForegroundColor Green
        Get-Content "C:\EQ12\logs\vpn_guard.log" -Tail 5
    }
}

function Stop-EQ12VPN {
    Stop-ScheduledTask -TaskName "EQ12_VPN_Guard"
    Write-Host "EQ12 VPN Guard stopped" -ForegroundColor Yellow
}
```

---

## 🎉 **Benefits Delivered**

✅ **Security**: End-to-end VPN protection with leak detection
✅ **Automation**: Zero-touch startup and monitoring
✅ **Reliability**: Automatic reconnection and health checks
✅ **Compliance**: Complete audit trail and reporting
✅ **Performance**: Real-time monitoring and optimization
✅ **Integration**: Seamless EQ12 ecosystem integration

**Status**: 🔐 **PRODUCTION READY** - Enterprise-grade VPN security stack delivered!

Your EQ12 betting operations are now protected with military-grade VPN integration.
