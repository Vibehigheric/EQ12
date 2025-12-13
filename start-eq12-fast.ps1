[CmdletBinding()]
param(
    [int]$Port = 3000,
    [switch]$Quick = $false
)

$ErrorActionPreference = "Stop"
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

Write-Host "EQ12 FAST STARTUP" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan

# Prerequisites check
Write-Host "`nChecking prerequisites..." -ForegroundColor Yellow

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Error "Python not found in PATH"
}

$venvPath = ".\venv\Scripts\activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "[OK] Python environment ready" -ForegroundColor Green
}
else {
    Write-Warning "Virtual environment not found. Run eq12_bootstrap.ps1 first."
}

# Circuit breaker service
Write-Host "`nInitializing circuit breaker..." -ForegroundColor Yellow

try {
    python .\scripts\circuit_breaker_service.py --status 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Circuit breaker ready" -ForegroundColor Green
    }
}
catch {
    Write-Warning "Circuit breaker initialization skipped: $($_.Exception.Message)"
}

# Dashboard startup
Write-Host "`nStarting dashboard..." -ForegroundColor Yellow

if ($Quick -eq $false) {
    try {
        Start-Process python -ArgumentList ".\dashboard\app.py", "--port", $Port -WindowStyle Hidden
        Write-Host "[OK] Dashboard server started" -ForegroundColor Green
    }
    catch {
        Write-Warning "Dashboard startup failed: $_"
    }
}

# Core services
$services = @(
    "health_monitor.py",
    "betting_intelligence_orchestrator.py"
)

Write-Host "`nStarting core services..." -ForegroundColor Yellow

foreach ($service in $services) {
    $servicePath = ".\scripts\$service"
    if (Test-Path $servicePath) {
        try {
            $proc = Start-Process python -ArgumentList $servicePath, "--daemon" -WindowStyle Hidden -PassThru
            if ($proc.Id) {
                Write-Host "[OK] $service started" -ForegroundColor Green
            }
        }
        catch {
            Write-Warning "Failed to start ${service}: $($_.Exception.Message)"
        }
    }
    else {
        Write-Warning "$service not found"
    }
}

# Betting intelligence test
if ($Quick -eq $false) {
    Write-Host "`n[TEST] BETTING INTELLIGENCE" -ForegroundColor Yellow

    try {
        python .\scripts\betting_intelligence_orchestrator.py --test-mode 2>$null
        Write-Host "[OK] Betting intelligence test complete" -ForegroundColor Green
    }
    catch {
        Write-Warning "Betting intelligence test failed: $_"
    }
}

$stopwatch.Stop()
$elapsed = $stopwatch.Elapsed

Write-Host "`n[SUCCESS] EQ12 STARTUP COMPLETE!" -ForegroundColor Green
Write-Host "Elapsed: $($elapsed.TotalSeconds.ToString('F1'))s" -ForegroundColor Gray
Write-Host "Dashboard: http://localhost:$Port" -ForegroundColor Cyan
Write-Host "`nReady for betting intelligence and Visual Studio debugging!" -ForegroundColor Magenta

Write-Host "`nStartup summary complete." -ForegroundColor Gray
