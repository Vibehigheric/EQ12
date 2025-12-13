# EQ12 Clean Startup Script
# Launches the EQ12 Dynamic Launcher System

param()

Set-Location "C:\EQ12"

Clear-Host
Write-Host ""
Write-Host "EQ12 GODSTACK STARTUP" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dynamic Automation Platform" -ForegroundColor Gray
Write-Host ""

Write-Host "🔍 System Check..." -ForegroundColor Yellow

$status = @{
    "Python Available" = (Get-Command python -ErrorAction SilentlyContinue) -ne $null
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
    Write-Host "🔑 API Keys: CONFIGURED" -ForegroundColor Green
} else {
    Write-Host "🔑 API Keys: NEEDS SETUP" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🚀 Starting EQ12 Launcher..." -ForegroundColor Green
Write-Host ""

Start-Sleep -Seconds 2

# Launch the basic launcher
if (Test-Path "C:\EQ12\EQ12_Basic_Launcher.ps1") {
    & "C:\EQ12\EQ12_Basic_Launcher.ps1"
} else {
    Write-Host "❌ Launcher not found!" -ForegroundColor Red
    Write-Host "Please ensure EQ12_Basic_Launcher.ps1 exists" -ForegroundColor Gray
}
