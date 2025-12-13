#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Copilot Management Dashboard Server
.DESCRIPTION
    Starts the Flask API server for EQ12 Copilot Management Dashboard
.PARAMETER Port
    Port to run the server on (default: 5012)
.PARAMETER TestMode
    Run in test mode without starting background services
.PARAMETER AutoStart
    Automatically start background monitoring
.EXAMPLE
    .\eq12_copilot_server.ps1
    Start the dashboard server on default port 5012
.EXAMPLE
    .\eq12_copilot_server.ps1 -Port 8080 -AutoStart
    Start the server on port 8080 with auto-start monitoring
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [int]$Port = 5012,

    [Parameter(Mandatory = $false)]
    [switch]$TestMode,

    [Parameter(Mandatory = $false)]
    [switch]$AutoStart
)

# Set up logging
$LogPath = "C:\EQ12\logs"
if (-not (Test-Path $LogPath)) {
    New-Item -Path $LogPath -ItemType Directory -Force | Out-Null
}

$LogFile = Join-Path $LogPath "copilot_server.log"

function Write-Log {
    param($Message, $Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Level: $Message"
    Write-Output $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Test-Prerequisites {
    Write-Log "Checking prerequisites..."

    $Issues = @()

    # Check Python
    try {
        $PythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Python found: $PythonVersion"
        } else {
            $Issues += "Python not found in PATH"
        }
    } catch {
        $Issues += "Python not available"
    }

    # Check required Python packages
    $RequiredPackages = @("flask", "requests")
    foreach ($Package in $RequiredPackages) {
        try {
            python -c "import $Package" 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Log "Package $Package is available"
            } else {
                $Issues += "Python package '$Package' not installed"
            }
        } catch {
            $Issues += "Cannot verify package '$Package'"
        }
    }

    # Check EQ12 directory structure
    $RequiredPaths = @(
        "C:\EQ12\scripts\eq12_copilot_api.py",
        "C:\EQ12\dashboard\copilot_management.html",
        "C:\EQ12\logs"
    )

    foreach ($Path in $RequiredPaths) {
        if (-not (Test-Path $Path)) {
            $Issues += "Required path missing: $Path"
        }
    }

    return $Issues
}

function Install-MissingPackages {
    Write-Log "Installing missing Python packages..."

    $Packages = @("flask", "requests", "psutil")

    foreach ($Package in $Packages) {
        try {
            Write-Log "Installing $Package..."
            python -m pip install $Package --quiet
            if ($LASTEXITCODE -eq 0) {
                Write-Log "Successfully installed $Package"
            } else {
                Write-Log "Failed to install $Package" "ERROR"
            }
        } catch {
            Write-Log "Exception installing $Package: $($_.Exception.Message)" "ERROR"
        }
    }
}

function Start-CopilotServer {
    param($Port, $TestMode)

    Write-Log "Starting EQ12 Copilot API Server on port $Port..."

    # Change to scripts directory
    $ScriptsPath = "C:\EQ12\scripts"
    if (-not (Test-Path $ScriptsPath)) {
        Write-Log "Scripts directory not found: $ScriptsPath" "ERROR"
        return $false
    }

    Set-Location $ScriptsPath

    # Set environment variables
    $env:FLASK_ENV = if ($TestMode) { "development" } else { "production" }
    $env:FLASK_PORT = $Port

    try {
        # Start the Flask server
        if ($TestMode) {
            Write-Log "Starting in test mode..."
            python eq12_copilot_api.py --test
        } else {
            Write-Log "Starting production server..."
            python eq12_copilot_api.py
        }
    } catch {
        Write-Log "Failed to start server: $($_.Exception.Message)" "ERROR"
        return $false
    }

    return $true
}

function Test-ServerHealth {
    param($Port)

    $MaxAttempts = 10
    $AttemptDelay = 2

    Write-Log "Testing server health on port $Port..."

    for ($i = 1; $i -le $MaxAttempts; $i++) {
        try {
            $Response = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/copilot/status" -TimeoutSec 5
            if ($Response) {
                Write-Log "Server is healthy and responding"
                return $true
            }
        } catch {
            Write-Log "Health check attempt $i failed, retrying in $AttemptDelay seconds..."
            Start-Sleep $AttemptDelay
        }
    }

    Write-Log "Server health check failed after $MaxAttempts attempts" "ERROR"
    return $false
}

function Open-Dashboard {
    param($Port)

    $DashboardUrl = "http://127.0.0.1:$Port/"

    try {
        Write-Log "Opening dashboard at $DashboardUrl"
        Start-Process $DashboardUrl
    } catch {
        Write-Log "Could not open dashboard automatically. Please navigate to: $DashboardUrl" "WARN"
    }
}

function Start-BackgroundMonitoring {
    Write-Log "Starting background Copilot monitoring..."

    $MonitorScript = "C:\EQ12\scripts\eq12_copilot_enhanced.ps1"
    if (Test-Path $MonitorScript) {
        try {
            # Start monitoring in background job
            $Job = Start-Job -ScriptBlock {
                param($ScriptPath)
                & powershell -ExecutionPolicy Bypass -File $ScriptPath -BackgroundMonitor
            } -ArgumentList $MonitorScript

            Write-Log "Background monitoring started (Job ID: $($Job.Id))"
        } catch {
            Write-Log "Failed to start background monitoring: $($_.Exception.Message)" "ERROR"
        }
    } else {
        Write-Log "Background monitoring script not found: $MonitorScript" "WARN"
    }
}

# Main execution
try {
    Write-Log "=== EQ12 Copilot Dashboard Server Starting ==="
    Write-Log "Port: $Port"
    Write-Log "Test Mode: $TestMode"
    Write-Log "Auto Start: $AutoStart"

    # Check prerequisites
    $Issues = Test-Prerequisites

    if ($Issues.Count -gt 0) {
        Write-Log "Prerequisites check failed:" "ERROR"
        foreach ($Issue in $Issues) {
            Write-Log "  - $Issue" "ERROR"
        }

        # Try to fix missing packages
        if ($Issues -match "package") {
            Write-Log "Attempting to install missing packages..."
            Install-MissingPackages

            # Re-check
            $RemainingIssues = Test-Prerequisites
            if ($RemainingIssues.Count -gt 0) {
                Write-Log "Some issues remain after auto-fix attempt:" "WARN"
                foreach ($Issue in $RemainingIssues) {
                    Write-Log "  - $Issue" "WARN"
                }
            }
        }
    }

    # Start background monitoring if requested
    if ($AutoStart -and -not $TestMode) {
        Start-BackgroundMonitoring
    }

    # Show startup information
    Write-Log "Dashboard URL: http://127.0.0.1:$Port/"
    Write-Log "Copilot Management: http://127.0.0.1:$Port/dashboard/copilot_management.html"
    Write-Log "API Endpoint: http://127.0.0.1:$Port/api/copilot/status"

    Write-Log "Press Ctrl+C to stop the server"

    # Start the server
    if (-not (Start-CopilotServer -Port $Port -TestMode $TestMode)) {
        throw "Failed to start Copilot server"
    }

} catch {
    Write-Log "Fatal error: $($_.Exception.Message)" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    exit 1
} finally {
    Write-Log "=== Server Shutdown ==="
}
