# EQ12 Safe Startup Script
# Launches EQ12 Dynamic Launcher without special characters

param()

Set-Location "C:\EQ12"

Clear-Host
Write-Host ""
Write-Host "EQ12 GODSTACK STARTUP" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dynamic Automation Platform" -ForegroundColor Gray
Write-Host ""

Write-Host "[System Check]" -ForegroundColor Yellow

$status = @{
    "Python Available" = $null -ne (Get-Command python -ErrorAction SilentlyContinue)
    "EQ12 Directory" = Test-Path "C:\EQ12"
    "Scripts Directory" = Test-Path "C:\EQ12\scripts"
    "Basic Launcher" = Test-Path "C:\EQ12\EQ12_Basic_Launcher.ps1"
    "API Configuration" = Test-Path "C:\EQ12\EQ12_API_Config.ps1"
}

foreach ($check in $status.GetEnumerator()) {
    $icon = if ($check.Value) { "[OK]" } else { "[FAIL]" }
    $color = if ($check.Value) { "Green" } else { "Red" }
    Write-Host "  $icon $($check.Key)" -ForegroundColor $color
}

Write-Host ""

if (Test-Path "C:\EQ12\keys\openai_api_key.txt") {
    Write-Host "[API Status] CONFIGURED" -ForegroundColor Green
} else {
    Write-Host "[API Status] NEEDS SETUP" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[Launcher] Starting EQ12 System..." -ForegroundColor Green
Write-Host ""

Start-Sleep -Seconds 2

if (Test-Path "C:\EQ12\EQ12_Basic_Launcher.ps1") {
    & "C:\EQ12\EQ12_Basic_Launcher.ps1"
} else {
    Write-Host "[ERROR] Launcher not found!" -ForegroundColor Red
    Write-Host "Please ensure EQ12_Basic_Launcher.ps1 exists" -ForegroundColor Gray
}
