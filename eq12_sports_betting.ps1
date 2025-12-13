[CmdletBinding()]
param(
    [Parameter(HelpMessage = "Operation to perform")]
    [ValidateSet("analyze", "start", "stop", "status", "dashboard", "report")]
    [string]$Action = "analyze"
)

# EQ12 Professional Sports Betting PowerShell Wrapper

$ErrorActionPreference = "Stop"

# Configuration
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $ScriptRoot) {
    $ScriptRoot = "C:\EQ12"
}

$PythonScript = Join-Path $ScriptRoot "eq12_pro_sports_betting.py"
$DashboardPath = Join-Path $ScriptRoot "dashboard\sports_betting_dashboard.html"
$LogsDir = Join-Path $ScriptRoot "logs"

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        "INFO" { Write-Host $logEntry -ForegroundColor Cyan }
        default { Write-Host $logEntry }
    }
}

function Test-PythonEnvironment {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            return $false
        }

        Write-EQ12Log "Python environment: $pythonVersion" "SUCCESS"
        return $true
    }
    catch {
        Write-EQ12Log "Python environment check failed: $_" "ERROR"
        return $false
    }
}

function Start-SportsBettingEngine {
    if (-not (Test-Path $PythonScript)) {
        throw "Sports betting script not found: $PythonScript"
    }

    try {
        Write-EQ12Log "Starting sports betting analysis..." "INFO"
        & python $PythonScript

        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "Operation completed successfully" "SUCCESS"
        }
        else {
            Write-EQ12Log "Operation failed with exit code: $LASTEXITCODE" "ERROR"
        }
    }
    catch {
        Write-EQ12Log "Execution error: $_" "ERROR"
        throw
    }
}

function Open-SportsDashboard {
    if (-not (Test-Path $DashboardPath)) {
        Write-EQ12Log "Dashboard not found: $DashboardPath" "ERROR"
        return
    }

    try {
        Write-EQ12Log "Opening sports betting dashboard..." "INFO"
        Start-Process $DashboardPath
        Write-EQ12Log "Dashboard opened in default browser" "SUCCESS"
    }
    catch {
        Write-EQ12Log "Failed to open dashboard: $_" "ERROR"
    }
}

function Get-SystemStatus {
    Write-EQ12Log "Checking EQ12 Sports Betting System Status..." "INFO"

    # Check Python environment
    $pythonOK = Test-PythonEnvironment

    # Check script files
    $scriptOK = Test-Path $PythonScript
    Write-EQ12Log "Main script exists: $scriptOK" $(if ($scriptOK) { "SUCCESS" } else { "ERROR" })

    # Check dashboard
    $dashboardOK = Test-Path $DashboardPath
    Write-EQ12Log "Dashboard exists: $dashboardOK" $(if ($dashboardOK) { "SUCCESS" } else { "ERROR" })

    # Check configuration
    $configPath = Join-Path $ScriptRoot "configs\sports_betting_config.json"
    $configOK = Test-Path $configPath
    Write-EQ12Log "Configuration exists: $configOK" $(if ($configOK) { "SUCCESS" } else { "ERROR" })

    # Overall system health
    $overallHealth = $pythonOK -and $scriptOK -and $dashboardOK -and $configOK
    $healthStatus = if ($overallHealth) { "HEALTHY" } else { "ISSUES DETECTED" }

    Write-EQ12Log "Overall System Health: $healthStatus" $(if ($overallHealth) { "SUCCESS" } else { "WARNING" })

    return $overallHealth
}

function Show-Help {
    Write-Host ""
    Write-Host "EQ12 Professional Sports Betting System" -ForegroundColor Green
    Write-Host "=======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "ACTIONS:" -ForegroundColor Yellow
    Write-Host "  analyze     - Run sports analysis (default)" -ForegroundColor White
    Write-Host "  status      - Check system status" -ForegroundColor White
    Write-Host "  dashboard   - Open web dashboard" -ForegroundColor White
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  .\eq12_sports_betting.ps1" -ForegroundColor Gray
    Write-Host "  .\eq12_sports_betting.ps1 -Action status" -ForegroundColor Gray
    Write-Host "  .\eq12_sports_betting.ps1 -Action dashboard" -ForegroundColor Gray
    Write-Host ""
}

# Main execution
try {
    Write-Host ""
    Write-Host "EQ12 Professional Sports Betting System" -ForegroundColor Green
    Write-Host "=======================================" -ForegroundColor Green
    Write-Host ""

    switch ($Action.ToLower()) {
        "status" {
            $systemOK = Get-SystemStatus
            exit $(if ($systemOK) { 0 } else { 1 })
        }

        "dashboard" {
            Open-SportsDashboard
            exit 0
        }

        "analyze" {
            if (-not (Test-PythonEnvironment)) {
                throw "Python environment check failed"
            }
            Start-SportsBettingEngine
        }

        default {
            Write-EQ12Log "Unknown action: $Action" "ERROR"
            Show-Help
            exit 1
        }
    }

    Write-EQ12Log "EQ12 Sports Betting operation completed!" "SUCCESS"

}
catch {
    Write-EQ12Log "FATAL ERROR: $_" "ERROR"
    exit 1
}
