# EQ12_Integrated_Dashboard_Launcher.ps1
<#
.SYNOPSIS
    EQ12 Integrated Dashboard System Launcher

.DESCRIPTION
    Launches the complete EQ12 real-time dashboard system with WebSockets,
    health monitoring, Ngrok diagnostics, and structured observability.

.PARAMETER Mode
    Launch mode: 'dev' for development, 'prod' for production

.PARAMETER Port
    Custom port for dashboard (default: 3001)

.PARAMETER ApiPort
    Custom port for API (default: 8082)

.PARAMETER NoNgrok
    Skip Ngrok tunnel setup

.PARAMETER Verbose
    Enable verbose logging

.EXAMPLE
    .\EQ12_Integrated_Dashboard_Launcher.ps1 -Mode dev -Verbose

.EXAMPLE
    .\EQ12_Integrated_Dashboard_Launcher.ps1 -Mode prod -Port 3000 -ApiPort 8080
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('dev', 'prod')]
    [string]$Mode = 'dev',

    [Parameter()]
    [int]$Port = 3001,

    [Parameter()]
    [int]$ApiPort = 8082,

    [Parameter()]
    [switch]$NoNgrok,

    [Parameter()]
    [switch]$Verbose
)

# Set error handling
$ErrorActionPreference = "Stop"

# Setup logging
$LogFile = "C:\EQ12\logs\dashboard_launcher_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$null = New-Item -Path (Split-Path $LogFile) -ItemType Directory -Force -ErrorAction SilentlyContinue

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Write-Host $LogMessage -ForegroundColor $(if ($Level -eq "ERROR") { "Red" } elseif ($Level -eq "WARN") { "Yellow" } else { "White" })
    $LogMessage | Out-File -FilePath $LogFile -Append -Encoding UTF8
}

function Test-Prerequisites {
    Write-Log "🔍 Checking system prerequisites..."

    # Check Python
    try {
        $PythonVersion = python --version 2>&1
        Write-Log "✅ Python found: $PythonVersion"
    }
    catch {
        Write-Log "❌ Python not found - please install Python 3.8+" "ERROR"
        return $false
    }

    # Check Node.js
    try {
        $NodeVersion = node --version 2>&1
        Write-Log "✅ Node.js found: $NodeVersion"
    }
    catch {
        Write-Log "⚠️ Node.js not found - some features may be limited" "WARN"
    }

    # Check required Python packages
    $RequiredPackages = @('fastapi', 'uvicorn', 'aiohttp', 'pydantic', 'psutil', 'jsonschema')

    foreach ($Package in $RequiredPackages) {
        try {
            $null = python -c "import $Package" 2>&1
            Write-Log "✅ Python package found: $Package"
        }
        catch {
            Write-Log "❌ Missing Python package: $Package" "ERROR"
            Write-Log "Run: pip install $Package" "ERROR"
            return $false
        }
    }

    # Check Ngrok if required
    if (-not $NoNgrok) {
        try {
            $NgrokVersion = ngrok version 2>&1
            Write-Log "✅ Ngrok found: $NgrokVersion"
        }
        catch {
            Write-Log "⚠️ Ngrok not found - tunnel diagnostics will be limited" "WARN"
        }
    }

    return $true
}

function Initialize-Environment {
    Write-Log "🔧 Initializing environment..."

    # Set environment variables
    if ($Mode -eq 'dev') {
        $env:EQ12_LOG_LEVEL = "DEBUG"
        $env:EQ12_ENVIRONMENT = "development"
    }
    else {
        $env:EQ12_LOG_LEVEL = "INFO"
        $env:EQ12_ENVIRONMENT = "production"
    }

    $env:EQ12_DASHBOARD_PORT = $Port
    $env:EQ12_API_PORT = $ApiPort
    $env:EQ12_ENABLE_NGROK = if ($NoNgrok) { "false" } else { "true" }

    Write-Log "Environment configured for $Mode mode"
    Write-Log "Dashboard Port: $Port"
    Write-Log "API Port: $ApiPort"
    Write-Log "Ngrok Enabled: $(-not $NoNgrok)"
}

function Start-BackgroundServices {
    Write-Log "🚀 Starting background services..."

    # Kill existing processes on ports
    @($Port, $ApiPort) | ForEach-Object {
        $ProcessId = (netstat -ano | findstr ":$_" | Where-Object { $_ -match "LISTENING" } | ForEach-Object { ($_ -split '\s+')[-1] }) | Select-Object -First 1

        if ($ProcessId) {
            Write-Log "Stopping existing process on port $_"
            Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
        }
    }

    # Start Ngrok if enabled
    if (-not $NoNgrok) {
        Write-Log "Starting Ngrok tunnels..."

        $NgrokConfig = "C:\EQ12\configs\ngrok.yml"
        if (Test-Path $NgrokConfig) {
            Start-Process -FilePath "ngrok" -ArgumentList "start", "--all", "--config", $NgrokConfig -WindowStyle Hidden
            Start-Sleep -Seconds 3
            Write-Log "✅ Ngrok tunnels started"
        }
        else {
            Write-Log "⚠️ Ngrok config not found at $NgrokConfig" "WARN"
        }
    }
}

function Start-DashboardSystem {
    Write-Log "🚀 Starting EQ12 Integrated Dashboard System..."

    # Change to EQ12 directory
    Set-Location -Path "C:\EQ12"

    # Create startup script content
    $StartupScript = @"
import asyncio
import sys
import os
import signal
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.getcwd())

from eq12_comprehensive_integration_system import EQ12IntegratedSystem
from eq12_helpers import setup_utf8_logging

async def main():
    setup_utf8_logging()

    # Configuration from environment
    config = {
        'dashboard_port': int(os.getenv('EQ12_DASHBOARD_PORT', '$Port')),
        'api_port': int(os.getenv('EQ12_API_PORT', '$ApiPort')),
        'enable_ngrok': os.getenv('EQ12_ENABLE_NGROK', 'true').lower() == 'true',
        'enable_observability': True,
        'health_check_interval': 30,
        'log_level': os.getenv('EQ12_LOG_LEVEL', 'INFO')
    }

    print("🚀 EQ12 INTEGRATED DASHBOARD SYSTEM")
    print("=" * 50)
    print(f"   📊 Dashboard: http://localhost:{config['dashboard_port']}")
    print(f"   🌐 API: http://localhost:{config['api_port']}")
    print(f"   🎛️ Integrated UI: http://localhost:{config['api_port']}/api/dashboard")
    print(f"   🔌 WebSocket: ws://localhost:{config['dashboard_port']}/ws")
    print("=" * 50)

    # Initialize system
    integrated_system = EQ12IntegratedSystem(config)

    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Shutdown signal received")
        asyncio.create_task(integrated_system.stop_system())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await integrated_system.start_system()

        print("\n✅ System started successfully!")
        print("Press Ctrl+C to stop the system")

        # Keep running
        while integrated_system.running:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal")
    except Exception as e:
        print(f"\n❌ System error: {e}")
        logging.exception("System startup failed")
    finally:
        await integrated_system.stop_system()
        print("✅ System shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
"@

    # Write startup script
    $StartupFile = "C:\EQ12\temp_dashboard_startup.py"
    $StartupScript | Out-File -FilePath $StartupFile -Encoding UTF8

    Write-Log "Starting Python dashboard system..."

    # Start the system
    try {
        if ($Verbose) {
            python $StartupFile
        }
        else {
            python $StartupFile 2>&1 | Tee-Object -FilePath $LogFile -Append
        }
    }
    catch {
        Write-Log "❌ Failed to start dashboard system: $($_.Exception.Message)" "ERROR"
        return $false
    }
    finally {
        # Clean up temp file
        Remove-Item -Path $StartupFile -ErrorAction SilentlyContinue
    }

    return $true
}

function Test-SystemHealth {
    Write-Log "🏥 Testing system health..."

    Start-Sleep -Seconds 5  # Allow system to start

    # Test dashboard endpoint
    try {
        $DashboardResponse = Invoke-WebRequest -Uri "http://localhost:$Port/health" -TimeoutSec 10
        if ($DashboardResponse.StatusCode -eq 200) {
            Write-Log "✅ Dashboard health check passed"
        }
    }
    catch {
        Write-Log "⚠️ Dashboard health check failed: $($_.Exception.Message)" "WARN"
    }

    # Test API endpoint
    try {
        $ApiResponse = Invoke-WebRequest -Uri "http://localhost:$ApiPort/api/system/status" -TimeoutSec 10
        if ($ApiResponse.StatusCode -eq 200) {
            Write-Log "✅ API health check passed"
        }
    }
    catch {
        Write-Log "⚠️ API health check failed: $($_.Exception.Message)" "WARN"
    }

    # Test Ngrok tunnels if enabled
    if (-not $NoNgrok) {
        try {
            $NgrokApi = Invoke-WebRequest -Uri "http://localhost:4040/api/tunnels" -TimeoutSec 5
            if ($NgrokApi.StatusCode -eq 200) {
                $TunnelData = $NgrokApi.Content | ConvertFrom-Json
                $TunnelCount = $TunnelData.tunnels.Count
                Write-Log "✅ Ngrok health check passed - $TunnelCount tunnels active"

                # Display tunnel URLs
                foreach ($Tunnel in $TunnelData.tunnels) {
                    Write-Log "   🌐 $($Tunnel.name): $($Tunnel.public_url)"
                }
            }
        }
        catch {
            Write-Log "⚠️ Ngrok health check failed: $($_.Exception.Message)" "WARN"
        }
    }
}

function Show-SystemInfo {
    Write-Host ""
    Write-Host "🚀 EQ12 INTEGRATED DASHBOARD SYSTEM" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host "   📊 Dashboard:     http://localhost:$Port" -ForegroundColor Green
    Write-Host "   🌐 API:           http://localhost:$ApiPort" -ForegroundColor Green
    Write-Host "   🎛️ Integrated UI: http://localhost:$ApiPort/api/dashboard" -ForegroundColor Green
    Write-Host "   🔌 WebSocket:     ws://localhost:$Port/ws" -ForegroundColor Green
    Write-Host "   📁 Log File:      $LogFile" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host ""

    if (-not $NoNgrok) {
        Write-Host "🌐 NGROK TUNNELS:" -ForegroundColor Cyan
        Write-Host "   Management UI: http://localhost:4040" -ForegroundColor Green
        Write-Host "   (Tunnel URLs will be displayed after startup)" -ForegroundColor Yellow
        Write-Host ""
    }

    Write-Host "📝 QUICK COMMANDS:" -ForegroundColor Cyan
    Write-Host "   Health Check:  curl http://localhost:$Port/health" -ForegroundColor Green
    Write-Host "   System Status: curl http://localhost:$ApiPort/api/system/status" -ForegroundColor Green
    Write-Host "   Stop System:   Press Ctrl+C" -ForegroundColor Yellow
    Write-Host ""
}

# Main execution
try {
    Write-Log "🚀 EQ12 Integrated Dashboard Launcher Started"
    Write-Log "Mode: $Mode, Port: $Port, API Port: $ApiPort"

    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Log "❌ Prerequisites check failed" "ERROR"
        exit 1
    }

    # Initialize environment
    Initialize-Environment

    # Show system information
    Show-SystemInfo

    # Start background services
    Start-BackgroundServices

    Write-Log "🎯 Starting dashboard system (this may take a moment)..."

    # Start dashboard system
    if (Start-DashboardSystem) {
        Write-Log "✅ Dashboard system started successfully"

        # Test system health
        Test-SystemHealth

        Write-Log "🎉 EQ12 Integrated Dashboard System is ready!"
        Write-Host ""
        Write-Host "✅ SYSTEM READY!" -ForegroundColor Green
        Write-Host "Access the dashboard at: http://localhost:$Port" -ForegroundColor Cyan
        Write-Host "Access the integrated UI at: http://localhost:$ApiPort/api/dashboard" -ForegroundColor Cyan

    }
    else {
        Write-Log "❌ Failed to start dashboard system" "ERROR"
        exit 1
    }

}
catch {
    Write-Log "❌ Launcher failed: $($_.Exception.Message)" "ERROR"
    Write-Host ""
    Write-Host "❌ SYSTEM STARTUP FAILED" -ForegroundColor Red
    Write-Host "Check log file: $LogFile" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
