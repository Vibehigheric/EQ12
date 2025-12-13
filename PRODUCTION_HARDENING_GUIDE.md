# EQ12 Production Hardening & Operations Guide

## Log Rotation Setup

### Python Log Rotation
Add to your Python logging configuration:

```python
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_production_logging():
    """Setup production-grade logging with rotation"""
    log_dir = "C:\\EQ12\\logs"
    os.makedirs(log_dir, exist_ok=True)

    # Main application log
    main_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "eq12_main.log"),
        maxBytes=10_000_000,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )

    # Error log (separate file for errors)
    error_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "eq12_errors.log"),
        maxBytes=5_000_000,   # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)

    # Configure formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    main_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(main_handler)
    logger.addHandler(error_handler)

    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
```

### Node.js Log Rotation (Winston)
Install winston and winston-daily-rotate-file:

```bash
npm install winston winston-daily-rotate-file
```

Add to your Node.js app:

```javascript
const winston = require('winston');
require('winston-daily-rotate-file');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    // Daily rotate file transport
    new winston.transports.DailyRotateFile({
      filename: 'logs/eq12-dashboard-%DATE%.log',
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '14d',
      zippedArchive: true
    }),

    // Error file
    new winston.transports.File({
      filename: 'logs/eq12-errors.log',
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    })
  ]
});

// Console transport for development
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

module.exports = logger;
```

## Windows Service Setup with NSSM

### Install NSSM
Download from: https://nssm.cc/download

### Dashboard Service Setup
```powershell
# Install dashboard as Windows service
nssm install eq12-dashboard "C:\Program Files\nodejs\node.exe"
nssm set eq12-dashboard Parameters "C:\EQ12\eq12_dashboard_server.js"
nssm set eq12-dashboard AppDirectory "C:\EQ12"
nssm set eq12-dashboard DisplayName "EQ12 Dashboard Server"
nssm set eq12-dashboard Description "EQ12 Automation Dashboard and API Server"

# Configure logging
nssm set eq12-dashboard AppStdout "C:\EQ12\logs\dashboard-stdout.log"
nssm set eq12-dashboard AppStderr "C:\EQ12\logs\dashboard-stderr.log"
nssm set eq12-dashboard AppRotateFiles 1
nssm set eq12-dashboard AppRotateOnline 1
nssm set eq12-dashboard AppRotateBytes 1048576

# Environment variables
nssm set eq12-dashboard AppEnvironmentExtra PORT=3000 NODE_ENV=production

# Service dependencies (optional)
nssm set eq12-dashboard DependOnService "Tcpip"

# Start the service
nssm start eq12-dashboard

# Check status
nssm status eq12-dashboard
```

### Python Service Setup
```powershell
# Install Python background service
nssm install eq12-python "C:\Python\python.exe"
nssm set eq12-python Parameters "C:\EQ12\eq12_background_service.py"
nssm set eq12-python AppDirectory "C:\EQ12"
nssm set eq12-python DisplayName "EQ12 Python Service"

# Configure logging and environment
nssm set eq12-python AppStdout "C:\EQ12\logs\python-stdout.log"
nssm set eq12-python AppStderr "C:\EQ12\logs\python-stderr.log"
nssm set eq12-python AppEnvironmentExtra PYTHONPATH=C:\EQ12

nssm start eq12-python
```

## Backup Strategy

### Daily Backup Script
```powershell
# EQ12_Daily_Backup.ps1
param(
    [string]$BackupRoot = "C:\EQ12\backup",
    [int]$RetainDays = 30
)

$Date = Get-Date -Format "yyyy-MM-dd"
$BackupDir = Join-Path $BackupRoot $Date

# Create backup directory
New-Item -ItemType Directory -Path $BackupDir -Force

# Backup configurations
Copy-Item "C:\EQ12\configs\*" -Destination "$BackupDir\configs\" -Recurse -Force

# Backup logs (last 7 days)
$RecentLogs = Get-ChildItem "C:\EQ12\logs\" | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-7) }
$LogBackupDir = Join-Path $BackupDir "logs"
New-Item -ItemType Directory -Path $LogBackupDir -Force
$RecentLogs | Copy-Item -Destination $LogBackupDir -Force

# Backup critical scripts
$CriticalFiles = @(
    "eq12_dashboard_server.js",
    "eq12_openai_client_enhanced.py",
    "Manage-DashboardServer.ps1",
    "requirements.txt"
)

foreach ($file in $CriticalFiles) {
    if (Test-Path "C:\EQ12\$file") {
        Copy-Item "C:\EQ12\$file" -Destination $BackupDir -Force
    }
}

# Compress backup
$ZipPath = "$BackupDir.zip"
Compress-Archive -Path "$BackupDir\*" -DestinationPath $ZipPath -Force
Remove-Item $BackupDir -Recurse -Force

# Cleanup old backups
Get-ChildItem $BackupRoot -Filter "*.zip" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RetainDays) } |
    Remove-Item -Force

Write-Host "Backup completed: $ZipPath"
```

### Schedule Daily Backup
```powershell
# Create scheduled task for daily backup
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\EQ12\EQ12_Daily_Backup.ps1"
$Trigger = New-ScheduledTaskTrigger -Daily -At "02:00AM"
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask -TaskName "EQ12 Daily Backup" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings
```

## Performance Monitoring

### Health Check Service
```python
# eq12_health_monitor.py
import psutil
import requests
import time
import logging
from datetime import datetime
import json

class EQ12HealthMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.endpoints = [
            "http://localhost:3000/health",
            "http://localhost:3000/api/health"
        ]

    def check_system_resources(self):
        """Monitor system resources"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('C:')

        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_free_gb': disk.free / (1024**3),
            'disk_percent': (disk.used / disk.total) * 100
        }

    def check_endpoints(self):
        """Check all HTTP endpoints"""
        results = {}
        for endpoint in self.endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                results[endpoint] = {
                    'status': 'ok',
                    'status_code': response.status_code,
                    'response_time_ms': response.elapsed.total_seconds() * 1000
                }
            except Exception as e:
                results[endpoint] = {
                    'status': 'error',
                    'error': str(e)
                }
        return results

    def check_processes(self):
        """Check critical processes"""
        processes = ['node.exe', 'python.exe']
        results = {}

        for proc_name in processes:
            count = len([p for p in psutil.process_iter(['name']) if p.info['name'] == proc_name])
            results[proc_name] = {
                'running': count > 0,
                'count': count
            }

        return results

    def generate_report(self):
        """Generate comprehensive health report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system': self.check_system_resources(),
            'endpoints': self.check_endpoints(),
            'processes': self.check_processes()
        }

        # Log critical issues
        if report['system']['cpu_percent'] > 80:
            self.logger.warning(f"High CPU usage: {report['system']['cpu_percent']}%")

        if report['system']['memory_percent'] > 85:
            self.logger.warning(f"High memory usage: {report['system']['memory_percent']}%")

        for endpoint, status in report['endpoints'].items():
            if status['status'] != 'ok':
                self.logger.error(f"Endpoint {endpoint} failed: {status}")

        return report

    def run_monitoring_loop(self, interval_seconds=300):
        """Run continuous monitoring"""
        self.logger.info(f"Starting health monitoring (interval: {interval_seconds}s)")

        while True:
            try:
                report = self.generate_report()

                # Save report
                report_file = f"logs/health_report_{datetime.now().strftime('%Y%m%d')}.json"
                with open(report_file, 'a') as f:
                    f.write(json.dumps(report) + '\n')

                time.sleep(interval_seconds)

            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor = EQ12HealthMonitor()
    monitor.run_monitoring_loop()
```

## Rollback Procedures

### Quick Rollback Commands
```powershell
# Create rollback directory structure
New-Item -ItemType Directory -Path "C:\EQ12\rollback" -Force

# Save current state before changes
pip freeze > rollback\requirements-before-upgrade.lock
Copy-Item package-lock.json rollback\ -ErrorAction SilentlyContinue
Copy-Item configs\*.json rollback\configs\ -Recurse -Force -ErrorAction SilentlyContinue

# Python rollback
pip install -r rollback\requirements-before-upgrade.lock --force-reinstall

# Node.js rollback
git checkout HEAD~1 -- package-lock.json
npm ci

# Config rollback
git checkout HEAD~1 -- configs/
```

### Service Management Commands
```powershell
# Stop all services
nssm stop eq12-dashboard
nssm stop eq12-python

# Restart services
nssm start eq12-dashboard
nssm start eq12-python

# Check service status
nssm status eq12-dashboard
nssm status eq12-python

# Remove services (if needed)
nssm remove eq12-dashboard confirm
nssm remove eq12-python confirm
```

## Security Hardening

### File Permissions
```powershell
# Secure configuration directory
icacls "C:\EQ12\configs" /grant:r "Administrators:(OI)(CI)F" /grant:r "SYSTEM:(OI)(CI)F" /remove "Users" /inheritance:r

# Secure logs directory
icacls "C:\EQ12\logs" /grant:r "Administrators:(OI)(CI)F" /grant:r "SYSTEM:(OI)(CI)F" /grant:r "Users:(OI)(CI)RX"

# Secure service executables
icacls "C:\EQ12\*.js" /grant:r "Administrators:(OI)(CI)F" /grant:r "SYSTEM:(OI)(CI)F" /grant:r "Users:(OI)(CI)RX"
```

### Firewall Rules
```powershell
# Allow inbound on port 3000 for dashboard
New-NetFirewallRule -DisplayName "EQ12 Dashboard" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow

# Block external access (optional - only localhost)
New-NetFirewallRule -DisplayName "EQ12 Dashboard Localhost Only" -Direction Inbound -Protocol TCP -LocalPort 3000 -RemoteAddress "127.0.0.1" -Action Allow
```

## Monitoring Dashboard

### PowerShell Status Dashboard
```powershell
# EQ12_Status_Dashboard.ps1
while ($true) {
    Clear-Host
    Write-Host "=== EQ12 System Status Dashboard ===" -ForegroundColor Green
    Write-Host "Last Updated: $(Get-Date)" -ForegroundColor Gray

    # Service Status
    $services = @("eq12-dashboard", "eq12-python")
    Write-Host "`nServices:" -ForegroundColor Yellow
    foreach ($svc in $services) {
        try {
            $status = & nssm status $svc 2>$null
            $color = if ($status -eq "SERVICE_RUNNING") { "Green" } else { "Red" }
            Write-Host "  $svc`: $status" -ForegroundColor $color
        } catch {
            Write-Host "  $svc`: NOT INSTALLED" -ForegroundColor Gray
        }
    }

    # Endpoint Status
    Write-Host "`nEndpoints:" -ForegroundColor Yellow
    $endpoints = @("http://localhost:3000/health", "http://localhost:3000/api/health")
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest $endpoint -TimeoutSec 2 -UseBasicParsing
            Write-Host "  $endpoint`: HTTP $($response.StatusCode)" -ForegroundColor Green
        } catch {
            Write-Host "  $endpoint`: FAILED" -ForegroundColor Red
        }
    }

    # System Resources
    Write-Host "`nSystem Resources:" -ForegroundColor Yellow
    $cpu = Get-Counter "\Processor(_Total)\% Processor Time" | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue
    $memory = Get-Counter "\Memory\Available MBytes" | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue
    Write-Host "  CPU: $([math]::Round($cpu,1))%" -ForegroundColor $(if($cpu -gt 80){"Red"}else{"Green"})
    Write-Host "  Available Memory: $([math]::Round($memory,0)) MB" -ForegroundColor $(if($memory -lt 1000){"Red"}else{"Green"})

    Write-Host "`nPress Ctrl+C to exit" -ForegroundColor Gray
    Start-Sleep -Seconds 10
}
```

This comprehensive hardening guide provides production-ready operations setup for EQ12!
