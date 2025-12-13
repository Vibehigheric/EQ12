[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("start", "stop", "restart", "status")]
    [string]$Action = "start",

    [Parameter(Mandatory = $false)]
    [int]$Port = 9000,

    [Parameter(Mandatory = $false)]
    [switch]$Debug,

    [Parameter(Mandatory = $false)]
    [switch]$ForceKill
)

<#
.SYNOPSIS
EQ12 Unified Dashboard Manager - PowerShell Control Script

.DESCRIPTION
Manages the EQ12 Unified Dashboard backend server and frontend integration.
Provides start/stop/restart functionality with health checks and logging.

.EXAMPLE
.\eq12_unified_dashboard_manager.ps1 -Action start
.\eq12_unified_dashboard_manager.ps1 -Action stop -ForceKill
.\eq12_unified_dashboard_manager.ps1 -Action restart -Port 9001 -Debug

.NOTES
Author: EQ12 System
Requires: Python 3.12+, FastAPI, uvicorn
#>

# Initialize logging
$LogDir = "C:\EQ12\logs"
$LogFile = Join-Path $LogDir "dashboard_manager.log"

if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp | $Level | DashboardManager | $Message"
    Add-Content -Path $LogFile -Value $logEntry

    switch ($Level) {
        "ERROR" { Write-Host $Message -ForegroundColor Red }
        "WARN" { Write-Host $Message -ForegroundColor Yellow }
        "INFO" { Write-Host $Message -ForegroundColor Green }
        default { Write-Host $Message }
    }
}

function Test-PythonEnvironment {
    <#
    .SYNOPSIS
    Verify Python environment and required packages
    #>

    Write-Log "Checking Python environment..."

    try {
        # Check Python version
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Python not found in PATH" "ERROR"
            return $false
        }

        Write-Log "Found Python: $pythonVersion"

        # Check required packages
        $requiredPackages = @("fastapi", "uvicorn", "pydantic", "requests")
        foreach ($package in $requiredPackages) {
            $result = & python -c "import $package" 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-Log "Missing required package: $package" "ERROR"
                Write-Log "Run: pip install $package" "ERROR"
                return $false
            }
        }

        Write-Log "All required packages found"
        return $true

    } catch {
        Write-Log "Error checking Python environment: $_" "ERROR"
        return $false
    }
}

function Get-DashboardProcess {
    <#
    .SYNOPSIS
    Find running dashboard processes
    #>

    $processes = Get-Process | Where-Object {
        $_.ProcessName -eq "python" -and
        $_.CommandLine -like "*eq12_unified_dashboard_backend*"
    }

    return $processes
}

function Start-Dashboard {
    <#
    .SYNOPSIS
    Start the unified dashboard backend
    #>

    Write-Log "Starting EQ12 Unified Dashboard..."

    # Check if already running
    $existingProcesses = Get-DashboardProcess
    if ($existingProcesses.Count -gt 0) {
        Write-Log "Dashboard already running (PID: $($existingProcesses[0].Id))" "WARN"
        return $true
    }

    # Verify Python environment
    if (!(Test-PythonEnvironment)) {
        Write-Log "Python environment check failed" "ERROR"
        return $false
    }

    # Check if port is available
    $portInUse = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($portInUse) {
        Write-Log "Port $Port is already in use" "ERROR"
        return $false
    }

    try {
        # Set environment variables
        $env:EQ12_DASHBOARD_PORT = $Port
        $env:EQ12_LOG_LEVEL = if ($Debug) { "DEBUG" } else { "INFO" }

        # Navigate to EQ12 directory
        Push-Location "C:\EQ12"

        # Start the dashboard backend
        $processArgs = @{
            FilePath     = "python"
            ArgumentList = @(
                "eq12_unified_dashboard_backend.py"
                "--host", "0.0.0.0"
                "--port", $Port.ToString()
                "--log-level", $env:EQ12_LOG_LEVEL.ToLower()
            )
            WindowStyle  = if ($Debug) { "Normal" } else { "Hidden" }
            PassThru     = $true
        }

        if (!$Debug) {
            $processArgs.RedirectStandardOutput = Join-Path $LogDir "dashboard_output.log"
            $processArgs.RedirectStandardError = Join-Path $LogDir "dashboard_error.log"
        }

        $process = Start-Process @processArgs

        Pop-Location

        # Wait a moment for startup
        Start-Sleep -Seconds 3

        # Verify it started successfully
        if (Test-DashboardHealth) {
            Write-Log "Dashboard started successfully (PID: $($process.Id), Port: $Port)"

            # Save process info
            $processInfo = @{
                PID       = $process.Id
                Port      = $Port
                StartTime = Get-Date
                LogFile   = $LogFile
            }
            $processInfo | ConvertTo-Json | Set-Content "C:\EQ12\dashboard_process.json"

            return $true
        } else {
            Write-Log "Dashboard failed to start properly" "ERROR"
            Stop-Dashboard -ForceKill
            return $false
        }

    } catch {
        Write-Log "Error starting dashboard: $_" "ERROR"
        Pop-Location
        return $false
    }
}

function Stop-Dashboard {
    <#
    .SYNOPSIS
    Stop the unified dashboard backend
    #>

    Write-Log "Stopping EQ12 Unified Dashboard..."

    $processes = Get-DashboardProcess

    if ($processes.Count -eq 0) {
        Write-Log "No dashboard processes found" "WARN"
        return $true
    }

    foreach ($process in $processes) {
        try {
            if ($ForceKill) {
                Write-Log "Force killing dashboard process (PID: $($process.Id))"
                Stop-Process -Id $process.Id -Force
            } else {
                Write-Log "Gracefully stopping dashboard process (PID: $($process.Id))"
                Stop-Process -Id $process.Id

                # Wait up to 10 seconds for graceful shutdown
                $timeout = 10
                while ($timeout -gt 0 -and (Get-Process -Id $process.Id -ErrorAction SilentlyContinue)) {
                    Start-Sleep -Seconds 1
                    $timeout--
                }

                # Force kill if still running
                if (Get-Process -Id $process.Id -ErrorAction SilentlyContinue) {
                    Write-Log "Graceful shutdown failed, force killing process" "WARN"
                    Stop-Process -Id $process.Id -Force
                }
            }

            Write-Log "Dashboard process stopped successfully"

        } catch {
            Write-Log "Error stopping dashboard process: $_" "ERROR"
        }
    }

    # Clean up process info file
    $processFile = "C:\EQ12\dashboard_process.json"
    if (Test-Path $processFile) {
        Remove-Item $processFile -Force
    }

    return $true
}

function Test-DashboardHealth {
    <#
    .SYNOPSIS
    Check if dashboard is healthy and responsive
    #>

    try {
        $healthUrl = "http://localhost:$Port/api/health"
        $response = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 10 -ErrorAction Stop

        if ($response.status -eq "healthy") {
            Write-Log "Dashboard health check passed"
            return $true
        } else {
            Write-Log "Dashboard health check failed: $($response.status)" "ERROR"
            return $false
        }

    } catch {
        Write-Log "Dashboard health check failed: $_" "ERROR"
        return $false
    }
}

function Get-DashboardStatus {
    <#
    .SYNOPSIS
    Get detailed dashboard status information
    #>

    Write-Log "Getting dashboard status..."

    $processes = Get-DashboardProcess
    $isHealthy = Test-DashboardHealth

    $status = @{
        IsRunning    = $processes.Count -gt 0
        IsHealthy    = $isHealthy
        Port         = $Port
        ProcessCount = $processes.Count
        Processes    = @()
    }

    if ($processes.Count -gt 0) {
        foreach ($process in $processes) {
            $processInfo = @{
                PID        = $process.Id
                StartTime  = $process.StartTime
                CPU        = $process.CPU
                WorkingSet = [math]::Round($process.WorkingSet64 / 1MB, 2)
            }
            $status.Processes += $processInfo
        }
    }

    # Try to get additional status from API
    if ($isHealthy) {
        try {
            $apiStatus = Invoke-RestMethod -Uri "http://localhost:$Port/api/system/status" -TimeoutSec 5
            $status.APIResponse = $apiStatus
        } catch {
            Write-Log "Could not retrieve API status: $_" "WARN"
        }
    }

    # Display status
    Write-Log "=== Dashboard Status ==="
    Write-Log "Running: $($status.IsRunning)"
    Write-Log "Healthy: $($status.IsHealthy)"
    Write-Log "Port: $($status.Port)"
    Write-Log "Process Count: $($status.ProcessCount)"

    if ($status.Processes.Count -gt 0) {
        foreach ($proc in $status.Processes) {
            Write-Log "  PID $($proc.PID): Started $($proc.StartTime), Memory: $($proc.WorkingSet) MB"
        }
    }

    if ($status.APIResponse) {
        Write-Log "API Uptime: $($status.APIResponse.uptime)"
        Write-Log "Service Count: $($status.APIResponse.services.Count)"
    }

    return $status
}

function Restart-Dashboard {
    <#
    .SYNOPSIS
    Restart the dashboard (stop + start)
    #>

    Write-Log "Restarting EQ12 Unified Dashboard..."

    if (Stop-Dashboard) {
        Start-Sleep -Seconds 2
        return Start-Dashboard
    } else {
        Write-Log "Failed to stop dashboard, cannot restart" "ERROR"
        return $false
    }
}

function Show-DashboardURL {
    <#
    .SYNOPSIS
    Display dashboard access URLs
    #>

    Write-Log "=== Dashboard Access URLs ==="
    Write-Log "Main Dashboard: http://localhost:$Port/"
    Write-Log "API Health: http://localhost:$Port/api/health"
    Write-Log "System Status: http://localhost:$Port/api/system/status"
    Write-Log "Betting Data: http://localhost:$Port/api/betting/parlays"
    Write-Log "Finance Data: http://localhost:$Port/api/finance/portfolio"
    Write-Log "WebSocket: ws://localhost:$Port/ws"
    Write-Log "========================="
}

# Main execution logic
try {
    Write-Log "EQ12 Dashboard Manager started with action: $Action"

    $success = switch ($Action.ToLower()) {
        "start" {
            $result = Start-Dashboard
            if ($result) { Show-DashboardURL }
            $result
        }
        "stop" {
            Stop-Dashboard
        }
        "restart" {
            $result = Restart-Dashboard
            if ($result) { Show-DashboardURL }
            $result
        }
        "status" {
            Get-DashboardStatus
            $true
        }
        default {
            Write-Log "Invalid action: $Action. Use start, stop, restart, or status" "ERROR"
            $false
        }
    }

    if ($success) {
        Write-Log "Dashboard manager completed successfully"
        exit 0
    } else {
        Write-Log "Dashboard manager failed" "ERROR"
        exit 1
    }

} catch {
    Write-Log "Unexpected error in dashboard manager: $_" "ERROR"
    exit 1
}
