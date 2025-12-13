[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [switch]$SkipInstall,

    [Parameter(Mandatory = $false)]
    [switch]$OpenBrowser,

    [Parameter(Mandatory = $false)]
    [int]$Port = 9000
)

<#
.SYNOPSIS
EQ12 Unified Dashboard Setup and Launch Script

.DESCRIPTION
Sets up Python environment, installs dependencies, and launches the unified dashboard.
This is the main entry point for getting the dashboard running.

.EXAMPLE
.\eq12_dashboard_setup.ps1
.\eq12_dashboard_setup.ps1 -SkipInstall -OpenBrowser
.\eq12_dashboard_setup.ps1 -Port 9001

.NOTES
Author: EQ12 System
Version: 2.0.0
#>

# Script configuration
$ScriptName = "EQ12DashboardSetup"
$LogDir = "C:\EQ12\logs"
$LogFile = Join-Path $LogDir "dashboard_setup.log"

# Ensure logs directory exists
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp | $Level | $ScriptName | $Message"
    Add-Content -Path $LogFile -Value $logEntry

    switch ($Level) {
        "ERROR" { Write-Host "❌ $Message" -ForegroundColor Red }
        "WARN" { Write-Host "⚠️  $Message" -ForegroundColor Yellow }
        "SUCCESS" { Write-Host "✅ $Message" -ForegroundColor Green }
        default { Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
    }
}

function Test-Prerequisites {
    <#
    .SYNOPSIS
    Check system prerequisites
    #>

    Write-Log "Checking system prerequisites..."

    # Check Python
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Python is not installed or not in PATH" "ERROR"
            Write-Log "Please install Python 3.12+ and add to PATH" "ERROR"
            return $false
        }

        # Parse version
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]

            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
                Write-Log "Python version $pythonVersion is too old. Need Python 3.8+" "ERROR"
                return $false
            }
        }

        Write-Log "Found compatible Python version: $pythonVersion" "SUCCESS"

    } catch {
        Write-Log "Error checking Python: $_" "ERROR"
        return $false
    }

    # Check pip
    try {
        $pipVersion = & python -m pip --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Log "pip is not available" "ERROR"
            return $false
        }
        Write-Log "Found pip: $pipVersion" "SUCCESS"

    } catch {
        Write-Log "Error checking pip: $_" "ERROR"
        return $false
    }

    # Check required files
    $requiredFiles = @(
        "C:\EQ12\eq12_unified_dashboard_backend.py",
        "C:\EQ12\unified_main_dashboard.html",
        "C:\EQ12\requirements_dashboard.txt"
    )

    foreach ($file in $requiredFiles) {
        if (!(Test-Path $file)) {
            Write-Log "Required file missing: $file" "ERROR"
            return $false
        }
    }

    Write-Log "All required files found" "SUCCESS"
    return $true
}

function Install-Dependencies {
    <#
    .SYNOPSIS
    Install Python dependencies for the dashboard
    #>

    Write-Log "Installing dashboard dependencies..."

    try {
        # Upgrade pip first
        Write-Log "Upgrading pip..."
        & python -m pip install --upgrade pip

        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to upgrade pip" "WARN"
        } else {
            Write-Log "pip upgraded successfully" "SUCCESS"
        }

        # Install requirements
        $requirementsFile = "C:\EQ12\requirements_dashboard.txt"
        Write-Log "Installing packages from $requirementsFile..."

        & python -m pip install -r $requirementsFile --upgrade

        if ($LASTEXITCODE -ne 0) {
            Write-Log "Failed to install some dependencies" "ERROR"
            Write-Log "Check the log and try installing manually:" "ERROR"
            Write-Log "python -m pip install -r requirements_dashboard.txt" "ERROR"
            return $false
        }

        Write-Log "Dependencies installed successfully" "SUCCESS"
        return $true

    } catch {
        Write-Log "Error during dependency installation: $_" "ERROR"
        return $false
    }
}

function Initialize-Dashboard {
    <#
    .SYNOPSIS
    Initialize dashboard database and configuration
    #>

    Write-Log "Initializing dashboard..."

    try {
        # Create necessary directories
        $dirs = @(
            "C:\EQ12\logs",
            "C:\EQ12\data"
        )

        foreach ($dir in $dirs) {
            if (!(Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
                Write-Log "Created directory: $dir"
            }
        }

        # Initialize database (will be created by Python script on first run)
        Write-Log "Database will be initialized on first startup"

        Write-Log "Dashboard initialization complete" "SUCCESS"
        return $true

    } catch {
        Write-Log "Error during dashboard initialization: $_" "ERROR"
        return $false
    }
}

function Start-DashboardService {
    <#
    .SYNOPSIS
    Start the dashboard service
    #>

    Write-Log "Starting dashboard service..."

    try {
        # Use the dashboard manager script
        $managerScript = "C:\EQ12\scripts\eq12_unified_dashboard_manager.ps1"

        if (!(Test-Path $managerScript)) {
            Write-Log "Dashboard manager script not found: $managerScript" "ERROR"
            return $false
        }

        # Start the dashboard
        $result = & powershell -ExecutionPolicy Bypass -File $managerScript -Action start -Port $Port

        if ($LASTEXITCODE -eq 0) {
            Write-Log "Dashboard service started successfully" "SUCCESS"
            return $true
        } else {
            Write-Log "Failed to start dashboard service" "ERROR"
            return $false
        }

    } catch {
        Write-Log "Error starting dashboard service: $_" "ERROR"
        return $false
    }
}

function Test-DashboardAccess {
    <#
    .SYNOPSIS
    Test dashboard accessibility
    #>

    Write-Log "Testing dashboard access..."

    try {
        # Wait a moment for startup
        Start-Sleep -Seconds 5

        # Test health endpoint
        $healthUrl = "http://localhost:$Port/api/health"
        $response = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 10

        if ($response.status -eq "healthy") {
            Write-Log "Dashboard is responding correctly" "SUCCESS"
            return $true
        } else {
            Write-Log "Dashboard health check failed" "ERROR"
            return $false
        }

    } catch {
        Write-Log "Cannot access dashboard: $_" "ERROR"
        Write-Log "Dashboard may still be starting up..." "WARN"
        return $false
    }
}

function Show-DashboardInfo {
    <#
    .SYNOPSIS
    Display dashboard access information
    #>

    Write-Log ""
    Write-Log "╔═══════════════════════════════════════╗" "SUCCESS"
    Write-Log "║       EQ12 UNIFIED DASHBOARD          ║" "SUCCESS"
    Write-Log "╠═══════════════════════════════════════╣" "SUCCESS"
    Write-Log "║                                       ║" "SUCCESS"
    Write-Log "║  🌐 Main Dashboard:                   ║" "SUCCESS"
    Write-Log "║     http://localhost:$Port/               ║" "SUCCESS"
    Write-Log "║                                       ║" "SUCCESS"
    Write-Log "║  🔧 API Health:                       ║" "SUCCESS"
    Write-Log "║     http://localhost:$Port/api/health     ║" "SUCCESS"
    Write-Log "║                                       ║" "SUCCESS"
    Write-Log "║  📊 System Status:                    ║" "SUCCESS"
    Write-Log "║     http://localhost:$Port/api/system/status ║" "SUCCESS"
    Write-Log "║                                       ║" "SUCCESS"
    Write-Log "║  🎯 Betting Hub:                      ║" "SUCCESS"
    Write-Log "║     - Active Parlays                  ║" "SUCCESS"
    Write-Log "║     - Live Odds                       ║" "SUCCESS"
    Write-Log "║     - Performance Analytics           ║" "SUCCESS"
    Write-Log "║                                       ║" "SUCCESS"
    Write-Log "║  💰 Finance Dashboard:                ║" "SUCCESS"
    Write-Log "║     - Portfolio Overview              ║" "SUCCESS"
    Write-Log "║     - Stock/Crypto Data               ║" "SUCCESS"
    Write-Log "║                                       ║" "SUCCESS"
    Write-Log "║  🤖 Automation Center:                ║" "SUCCESS"
    Write-Log "║     - Scrapers & Bots                 ║" "SUCCESS"
    Write-Log "║     - Apple TV Integration            ║" "SUCCESS"
    Write-Log "║                                       ║" "SUCCESS"
    Write-Log "║  🧠 AI Control Panel:                 ║" "SUCCESS"
    Write-Log "║     - GPT-5 Betting Analysis          ║" "SUCCESS"
    Write-Log "║     - Cookbook Search                 ║" "SUCCESS"
    Write-Log "║     - Sora Video Generation           ║" "SUCCESS"
    Write-Log "║                                       ║" "SUCCESS"
    Write-Log "╚═══════════════════════════════════════╝" "SUCCESS"
    Write-Log ""

    Write-Log "💡 Control Commands:"
    Write-Log "   Status:  .\scripts\eq12_unified_dashboard_manager.ps1 -Action status"
    Write-Log "   Stop:    .\scripts\eq12_unified_dashboard_manager.ps1 -Action stop"
    Write-Log "   Restart: .\scripts\eq12_unified_dashboard_manager.ps1 -Action restart"
    Write-Log ""
}

function Open-DashboardBrowser {
    <#
    .SYNOPSIS
    Open dashboard in default browser
    #>

    if ($OpenBrowser) {
        Write-Log "Opening dashboard in browser..."
        try {
            Start-Process "http://localhost:$Port/"
            Write-Log "Browser opened" "SUCCESS"
        } catch {
            Write-Log "Could not open browser: $_" "WARN"
        }
    }
}

# Main execution
try {
    Write-Log "Starting EQ12 Unified Dashboard Setup..." "SUCCESS"
    Write-Log "Port: $Port"
    Write-Log "Skip Install: $SkipInstall"
    Write-Log "Open Browser: $OpenBrowser"
    Write-Log ""

    # Step 1: Check prerequisites
    if (!(Test-Prerequisites)) {
        Write-Log "Prerequisites check failed. Setup cannot continue." "ERROR"
        exit 1
    }

    # Step 2: Install dependencies (unless skipped)
    if (!$SkipInstall) {
        if (!(Install-Dependencies)) {
            Write-Log "Dependency installation failed. Setup cannot continue." "ERROR"
            exit 1
        }
    } else {
        Write-Log "Skipping dependency installation as requested"
    }

    # Step 3: Initialize dashboard
    if (!(Initialize-Dashboard)) {
        Write-Log "Dashboard initialization failed. Setup cannot continue." "ERROR"
        exit 1
    }

    # Step 4: Start dashboard service
    if (!(Start-DashboardService)) {
        Write-Log "Failed to start dashboard service. Setup cannot continue." "ERROR"
        exit 1
    }

    # Step 5: Test access
    Test-DashboardAccess | Out-Null

    # Step 6: Show info and open browser
    Show-DashboardInfo
    Open-DashboardBrowser

    Write-Log "EQ12 Unified Dashboard setup completed successfully! 🎉" "SUCCESS"
    exit 0

} catch {
    Write-Log "Unexpected error during setup: $_" "ERROR"
    Write-Log "Check the log file: $LogFile" "ERROR"
    exit 1
}
