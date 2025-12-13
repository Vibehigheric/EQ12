# EQ12 GODSTACK Status Check
# Comprehensive status monitoring for all EQ12 services

Write-Host "🚀 EQ12 GODSTACK Status Check" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host ""

# Python Environment Status
Write-Host "🐍 Python Environment:" -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python: Not available" -ForegroundColor Red
}

# Pip Status
try {
    $pipVersion = pip --version 2>&1
    Write-Host "  ✅ Pip: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Pip: Not available" -ForegroundColor Red
}

Write-Host ""

# Process Status
Write-Host "🔄 Active Processes:" -ForegroundColor Yellow
$processes = Get-Process | Where-Object {$_.ProcessName -match "(ngrok|python|flask|uvicorn|gunicorn|node)"} | Select-Object ProcessName, Id, StartTime
if ($processes) {
    foreach ($proc in $processes) {
        $uptime = if ($proc.StartTime) { 
            $elapsed = (Get-Date) - $proc.StartTime
            "$($elapsed.Hours)h $($elapsed.Minutes)m $($elapsed.Seconds)s"
        } else { "Unknown" }
        Write-Host "  ✅ $($proc.ProcessName) (PID: $($proc.Id)) - Uptime: $uptime" -ForegroundColor Green
    }
} else {
    Write-Host "  ⚠️  No EQ12-related processes found" -ForegroundColor Yellow
}

Write-Host ""

# Ngrok Tunnel Status
Write-Host "🌐 Ngrok Tunnel Status:" -ForegroundColor Yellow
try {
    $tunnelResponse = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction Stop
    if ($tunnelResponse.tunnels -and $tunnelResponse.tunnels.Count -gt 0) {
        foreach ($tunnel in $tunnelResponse.tunnels) {
            Write-Host "  ✅ $($tunnel.name): $($tunnel.public_url) -> $($tunnel.config.addr)" -ForegroundColor Green
        }
    } else {
        Write-Host "  ⚠️  No active tunnels found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ Ngrok API not accessible (tunnel may not be running)" -ForegroundColor Red
}

Write-Host ""

# File System Status
Write-Host "📁 EQ12 Directory Structure:" -ForegroundColor Yellow
$directories = @("C:\EQ12\scripts", "C:\EQ12\logs", "C:\EQ12\keys", "C:\EQ12\configs")
foreach ($dir in $directories) {
    if (Test-Path $dir) {
        $fileCount = (Get-ChildItem $dir -File -ErrorAction SilentlyContinue).Count
        Write-Host "  ✅ $dir ($fileCount files)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $dir (missing)" -ForegroundColor Red
    }
}

Write-Host ""

# Key Scripts Status
Write-Host "📜 Core Scripts:" -ForegroundColor Yellow
$scripts = @(
    "C:\EQ12\scripts\odds_parser.py",
    "C:\EQ12\scripts\parlay_builder.py",
    "C:\EQ12\eq12_simple_start.ps1",
    "C:\EQ12\eq12_master_launcher.ps1"
)
foreach ($script in $scripts) {
    if (Test-Path $script) {
        $size = [math]::Round((Get-Item $script).Length / 1KB, 2)
        Write-Host "  ✅ $(Split-Path $script -Leaf) ($size KB)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $(Split-Path $script -Leaf) (missing)" -ForegroundColor Red
    }
}

Write-Host ""

# Log Files Status
Write-Host "📝 Recent Logs:" -ForegroundColor Yellow
$logDir = "C:\EQ12\logs"
if (Test-Path $logDir) {
    $recentLogs = Get-ChildItem $logDir -File | Sort-Object LastWriteTime -Descending | Select-Object -First 5
    if ($recentLogs) {
        foreach ($log in $recentLogs) {
            $age = (Get-Date) - $log.LastWriteTime
            $ageStr = if ($age.TotalHours -lt 1) { "$([math]::Round($age.TotalMinutes))m ago" } else { "$([math]::Round($age.TotalHours))h ago" }
            Write-Host "  📄 $($log.Name) - $ageStr" -ForegroundColor Cyan
        }
    } else {
        Write-Host "  ⚠️  No log files found" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ❌ Logs directory not found" -ForegroundColor Red
}

Write-Host ""

# Network Status
Write-Host "🌐 Network Connectivity:" -ForegroundColor Yellow
try {
    $internetTest = Test-NetConnection -ComputerName "8.8.8.8" -Port 53 -InformationLevel Quiet -ErrorAction Stop
    if ($internetTest) {
        Write-Host "  ✅ Internet connectivity: Available" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Internet connectivity: Failed" -ForegroundColor Red
    }
} catch {
    Write-Host "  ⚠️  Internet connectivity: Test failed" -ForegroundColor Yellow
}

# Local port checks
$ports = @(4040, 8080, 5000, 3000)
foreach ($port in $ports) {
    try {
        $connection = Test-NetConnection -ComputerName "localhost" -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($connection) {
            Write-Host "  ✅ Port ${port}: Open" -ForegroundColor Green
        } else {
            Write-Host "  ⚪ Port ${port}: Closed" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  ⚪ Port ${port}: Unknown" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "🎯 EQ12 GODSTACK Status Check Complete!" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray