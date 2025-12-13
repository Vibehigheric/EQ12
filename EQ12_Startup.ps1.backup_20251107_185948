# EQ12 Auto-Startup Script
# This script runs the Dynamic Interactive Launcher on first system start

[CmdletBinding()]
param()

# Set working directory to EQ12 root
Set-Location "C:\EQ12"

# Display startup banner
Clear-Host
Write-Host ""
Write-Host "███████╗ ██████╗  ██╗██████╗ " -ForegroundColor Cyan
Write-Host "██╔════╝██╔═══██╗███║██╔══██╗" -ForegroundColor Cyan
Write-Host "█████╗  ██║   ██║╚██║██████╔╝" -ForegroundColor Cyan
Write-Host "██╔══╝  ██║▄▄ ██║ ██║██╔══██╗" -ForegroundColor Cyan
Write-Host "███████╗╚██████╔╝ ██║██║  ██║" -ForegroundColor Cyan
Write-Host "╚══════╝ ╚══▀▀═╝  ╚═╝╚═╝  ╚═╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "          GODSTACK SYSTEM" -ForegroundColor Yellow
Write-Host "     Dynamic AI-Powered Platform" -ForegroundColor Gray
Write-Host ""
Write-Host "Initializing..." -ForegroundColor Green

# Brief startup check
Start-Sleep 2

# Check for critical components
$status = @{
    "Python" = (Get-Command python -ErrorAction SilentlyContinue) -ne $null
    "Node.js" = (Get-Command node -ErrorAction SilentlyContinue) -ne $null
    "Keys Directory" = Test-Path "C:\EQ12\keys"
    "Launcher" = Test-Path "C:\EQ12\EQ12_Dynamic_Launcher.ps1"
}

Write-Host "System Status:" -ForegroundColor Yellow
foreach ($check in $status.GetEnumerator()) {
    $icon = if ($check.Value) { "✅" } else { "❌" }
    Write-Host "  $icon $($check.Key)" -ForegroundColor White
}

Write-Host ""

if (-not $status["Launcher"]) {
    Write-Host "❌ Dynamic Launcher not found! Please run setup first." -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

Write-Host "🚀 Starting Dynamic Interactive Launcher..." -ForegroundColor Green
Start-Sleep 1

# Launch the basic launcher (working version)
& ".\EQ12_Basic_Launcher.ps1"
