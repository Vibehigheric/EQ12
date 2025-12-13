# EQ12 Performance Optimized - 2025-10-11T06:54:20.714903
# Startup optimization applied by Master System Fixer

# EQ12 GODSTACK Status Check
# Comprehensive status monitoring for all EQ12 services

Write-Host "EQ12 GODSTACK Status Check" -ForegroundColor Cyan
Write-Host "=================================================="
Write-Host ""

# Python Environment Status
Write-Host "Python Environment:" -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  [OK] Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Python: Not available" -ForegroundColor Red
}

# Pip Status
try {
    $pipVersion = pip --version 2>&1 | Select-Object -First 1
    Write-Host "  [OK] Pip: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "  [FAIL] Pip: Not available" -ForegroundColor Red
}

Write-Host ""

# Process Status
Write-Host "Active Processes:" -ForegroundColor Yellow
$processes = Get-Process | Where-Object {$_.ProcessName -match "(ngrok|python|flask|uvicorn|gunicorn|node)"} | Select-Object ProcessName, Id, StartTime
if ($processes) {
    foreach ($proc in $processes) {
        $uptime = if ($proc.StartTime) { 
            $elapsed = (Get-Date) - $proc.StartTime
            "$($elapsed.Hours)h $($elapsed.Minutes)m $($elapsed.Seconds)s"
        } else { "Unknown" }
        Write-Host "  [OK] $($proc.ProcessName) (PID: $($proc.Id)) - Uptime: $uptime" -ForegroundColor Green
    }
} else {
    Write-Host "  [WARN] No EQ12-related processes found" -ForegroundColor Yellow
}

Write-Host ""

# Ngrok Tunnel Status
Write-Host "Ngrok Tunnel Status:" -ForegroundColor Yellow
try {
    $tunnelResponse = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction Stop
    if ($tunnelResponse.tunnels -and $tunnelResponse.tunnels.Count -gt 0) {
        foreach ($tunnel in $tunnelResponse.tunnels) {
            Write-Host "  [OK] $($tunnel.name): $($tunnel.public_url) -> $($tunnel.config.addr)" -ForegroundColor Green
        }
    } else {
        Write-Host "  [WARN] No active tunnels found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [FAIL] Ngrok API not accessible (tunnel may not be running)" -ForegroundColor Red
}

Write-Host ""

# File System Status
Write-Host "EQ12 Directory Structure:" -ForegroundColor Yellow
$directories = @("C:\EQ12\scripts", "C:\EQ12\logs", "C:\EQ12\keys", "C:\EQ12\configs")
foreach ($dir in $directories) {
    if (Test-Path $dir) {
        $fileCount = (Get-ChildItem $dir -File -ErrorAction SilentlyContinue).Count
        Write-Host "  [OK] $dir ($fileCount files)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $dir (missing)" -ForegroundColor Red
    }
}

Write-Host ""

# Key Scripts Status
Write-Host "Core Scripts:" -ForegroundColor Yellow
$scripts = @(
    "C:\EQ12\scripts\odds_parser.py",
    "C:\EQ12\scripts\parlay_builder.py",
    "C:\EQ12\eq12_simple_start.ps1",
    "C:\EQ12\eq12_master_launcher.ps1"
)
foreach ($script in $scripts) {
    if (Test-Path $script) {
        $size = [math]::Round((Get-Item $script).Length / 1KB, 2)
        Write-Host "  [OK] $(Split-Path $script -Leaf) ($size KB)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $(Split-Path $script -Leaf) (missing)" -ForegroundColor Red
    }
}

Write-Host ""

# Network Status
Write-Host "Network Connectivity:" -ForegroundColor Yellow
try {
    $internetTest = Test-NetConnection -ComputerName "8.8.8.8" -Port 53 -InformationLevel Quiet -ErrorAction Stop
    if ($internetTest) {
        Write-Host "  [OK] Internet connectivity: Available" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] Internet connectivity: Failed" -ForegroundColor Red
    }
} catch {
    Write-Host "  [WARN] Internet connectivity: Test failed" -ForegroundColor Yellow
}

# Local port checks
$ports = @(4040, 8080, 5000, 3000)
foreach ($port in $ports) {
    try {
        $connection = Test-NetConnection -ComputerName "localhost" -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($connection) {
            Write-Host "  [OK] Port ${port}: Open" -ForegroundColor Green
        } else {
            Write-Host "  [INFO] Port ${port}: Closed" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  [INFO] Port ${port}: Unknown" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "EQ12 GODSTACK Status Check Complete!" -ForegroundColor Cyan
Write-Host "=================================================="