[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [switch]$SkipInstall,

    [Parameter(Mandatory = $false)]
    [switch]$OpenBrowser,

    [Parameter(Mandatory = $false)]
    [int]$Port = 9000
)

# EQ12 Unified Dashboard Setup Script
$LogDir = "C:\EQ12\logs"
$LogFile = Join-Path $LogDir "dashboard_setup.log"

# Ensure logs directory exists
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-DashboardLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp | $Level | DashboardSetup | $Message"
    Add-Content -Path $LogFile -Value $logEntry

    $color = switch ($Level) {
        "ERROR" { "Red"; break }
        "WARN" { "Yellow"; break }
        "SUCCESS" { "Green"; break }
        default { "Cyan"; break }
    }

    Write-Host $Message -ForegroundColor $color
}

Write-DashboardLog "Starting EQ12 Unified Dashboard Setup..." "SUCCESS"
Write-DashboardLog "Port: $Port"

# Check Python
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-DashboardLog "Python not found. Please install Python 3.8+" "ERROR"
        exit 1
    }
    Write-DashboardLog "Found Python: $pythonVersion" "SUCCESS"
} catch {
    Write-DashboardLog "Error checking Python: $_" "ERROR"
    exit 1
}

# Install dependencies unless skipped
if (!$SkipInstall) {
    Write-DashboardLog "Installing dashboard dependencies..."

    try {
        # Install required packages
        python -m pip install fastapi uvicorn pydantic requests websockets aiofiles --upgrade

        if ($LASTEXITCODE -eq 0) {
            Write-DashboardLog "Dependencies installed successfully" "SUCCESS"
        } else {
            Write-DashboardLog "Some dependencies failed to install" "WARN"
        }
    } catch {
        Write-DashboardLog "Error installing dependencies: $_" "ERROR"
    }
} else {
    Write-DashboardLog "Skipping dependency installation"
}

# Create directories
$dirs = @("C:\EQ12\logs", "C:\EQ12\data")
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-DashboardLog "Created directory: $dir"
    }
}

# Start the dashboard
Write-DashboardLog "Starting EQ12 Unified Dashboard..."

try {
    # Check if already running
    $existingProcess = Get-Process | Where-Object {
        $_.ProcessName -eq "python" -and $_.CommandLine -like "*eq12_unified_dashboard_backend*"
    }

    if ($existingProcess) {
        Write-DashboardLog "Dashboard already running (PID: $($existingProcess.Id))" "WARN"
        Write-DashboardLog "Stopping existing process..."
        Stop-Process -Id $existingProcess.Id -Force
        Start-Sleep 2
    }

    # Start new process
    $processArgs = @{
        FilePath         = "python"
        ArgumentList     = @("eq12_unified_dashboard_backend.py")
        WindowStyle      = "Hidden"
        PassThru         = $true
        WorkingDirectory = "C:\EQ12"
    }

    $process = Start-Process @processArgs
    Write-DashboardLog "Dashboard started (PID: $($process.Id))" "SUCCESS"

    # Wait for startup
    Start-Sleep 5

    # Test health
    try {
        $healthUrl = "http://localhost:$Port/api/health"
        $response = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 10

        if ($response.status -eq "healthy") {
            Write-DashboardLog "Dashboard is healthy and responding" "SUCCESS"
        }
    } catch {
        Write-DashboardLog "Dashboard may still be starting up..." "WARN"
    }

    # Show access info
    Write-DashboardLog ""
    Write-DashboardLog "=== EQ12 UNIFIED DASHBOARD READY ===" "SUCCESS"
    Write-DashboardLog "Main Dashboard: http://localhost:$Port/" "SUCCESS"
    Write-DashboardLog "API Health: http://localhost:$Port/api/health" "SUCCESS"
    Write-DashboardLog "System Status: http://localhost:$Port/api/system/status" "SUCCESS"
    Write-DashboardLog ""
    Write-DashboardLog "Features Available:" "SUCCESS"
    Write-DashboardLog "- Betting Hub (Parlays, Live Odds, Analytics)" "SUCCESS"
    Write-DashboardLog "- System Status (Services, VPN, Logs)" "SUCCESS"
    Write-DashboardLog "- Finance Dashboard (Portfolio, Stocks, Crypto)" "SUCCESS"
    Write-DashboardLog "- Automation Center (Scrapers, Bots, Apple TV)" "SUCCESS"
    Write-DashboardLog "- AI Control Panel (GPT-5, Cookbook, Sora)" "SUCCESS"
    Write-DashboardLog ""
    Write-DashboardLog "Control Commands:" "SUCCESS"
    Write-DashboardLog "  Status: powershell -File .\scripts\eq12_unified_dashboard_manager.ps1 -Action status"
    Write-DashboardLog "  Stop:   powershell -File .\scripts\eq12_unified_dashboard_manager.ps1 -Action stop"
    Write-DashboardLog ""

    # Open browser if requested
    if ($OpenBrowser) {
        Write-DashboardLog "Opening dashboard in browser..."
        Start-Process "http://localhost:$Port/"
    }

    Write-DashboardLog "Setup completed successfully!" "SUCCESS"

} catch {
    Write-DashboardLog "Error starting dashboard: $_" "ERROR"
    exit 1
}
