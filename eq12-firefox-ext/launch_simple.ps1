# EQ12 Firefox Extension Simple Launcher

Write-Host "EQ12 Firefox Extension Launcher" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Start the backend API server
Write-Host "Starting EQ12 backend API..." -ForegroundColor Yellow

# Check if backend is already running
$existingJobs = Get-Job | Where-Object { $_.Name -like "*EQ12-API*" -and $_.State -eq "Running" }
if ($existingJobs) {
    Write-Host "Backend already running (Job: $($existingJobs[0].Name))" -ForegroundColor Yellow
} else {
    # Start backend as background job
    $job = Start-Job -ScriptBlock {
        Set-Location "C:\EQ12\scripts"
        python eq12_extension_backend.py
    } -Name "EQ12-API-Extension"

    Write-Host "Backend started (Job ID: $($job.Id))" -ForegroundColor Green

    # Wait for server to start
    Write-Host "Waiting for server startup..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5

    # Test API connectivity
    try {
        $ping = Invoke-RestMethod -Uri "http://localhost:8000/api/ping" -TimeoutSec 10
        Write-Host "API is responding!" -ForegroundColor Green
        Write-Host "Server: $($ping.server)" -ForegroundColor Cyan
    } catch {
        Write-Host "API not responding yet - give it a moment..." -ForegroundColor Yellow
    }
}

Write-Host "`nFIREFOX EXTENSION READY!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "1. Open Firefox" -ForegroundColor White
Write-Host "2. Go to about:debugging#/runtime/this-firefox" -ForegroundColor White
Write-Host "3. Click 'Load Temporary Add-on'" -ForegroundColor White
Write-Host "4. Navigate to: C:\EQ12\eq12-firefox-ext\" -ForegroundColor Yellow
Write-Host "5. Select: manifest.json" -ForegroundColor Yellow

Write-Host "`nExtension Features:" -ForegroundColor Cyan
Write-Host "* Generate 5-leg and 10-leg parlays" -ForegroundColor White
Write-Host "* View audit reports and analytics" -ForegroundColor White
Write-Host "* System health monitoring" -ForegroundColor White
Write-Host "* EV highlighting on sportsbook pages" -ForegroundColor White

Write-Host "`nAPI Endpoints:" -ForegroundColor Cyan
Write-Host "* Ping: http://localhost:8000/api/ping" -ForegroundColor White
Write-Host "* Health: http://localhost:8000/api/health" -ForegroundColor White
Write-Host "* Parlay: http://localhost:8000/api/parlay?size=5" -ForegroundColor White
Write-Host "* Audit: http://localhost:8000/api/audit" -ForegroundColor White

Write-Host "`nEQ12 Extension System Ready!" -ForegroundColor Green
