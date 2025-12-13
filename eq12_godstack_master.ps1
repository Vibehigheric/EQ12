# EQ12 GODSTACK Master Launch Script
# This PowerShell script provides a comprehensive interface to launch and manage the entire EQ12 system

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("launch", "status", "restart", "shutdown", "test", "install", "update")]
    [string]$Action = "launch",

    [Parameter(Mandatory=$false)]
    [switch]$AutoLaunch,

    [Parameter(Mandatory=$false)]
    [switch]$Headless,

    [Parameter(Mandatory=$false)]
    [switch]$Force,

    [Parameter(Mandatory=$false)]
    [switch]$Verbose
)

# Enhanced error handling and logging
$ErrorActionPreference = "Stop"
$VerbosePreference = if ($Verbose) { "Continue" } else { "SilentlyContinue" }

# System paths and constants
$EQ12_ROOT = "C:\EQ12"
$LOGS_PATH = "$EQ12_ROOT\logs"
$SCRIPTS_PATH = "$EQ12_ROOT\scripts"
$ORCHESTRATOR_SCRIPT = "$EQ12_ROOT\eq12_godstack_orchestrator.py"
$COLD_RESTART_SCRIPT = "$EQ12_ROOT\eq12_cold_restart_manager.py"
$ADVANCED_WRAPPER = "$EQ12_ROOT\eq12_sports_betting_advanced.ps1"

# Ensure logs directory exists
if (-not (Test-Path $LOGS_PATH)) {
    New-Item -Path $LOGS_PATH -ItemType Directory -Force | Out-Null
}

# Logging function with structured output
function Write-EQ12Log {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,

        [Parameter(Mandatory=$false)]
        [ValidateSet("INFO", "WARNING", "ERROR", "SUCCESS")]
        [string]$Level = "INFO",

        [Parameter(Mandatory=$false)]
        [string]$Component = "MasterLauncher"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] [$Component] $Message"

    # Console output with colors
    switch ($Level) {
        "INFO"    { Write-Host $logEntry -ForegroundColor Cyan }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "ERROR"   { Write-Host $logEntry -ForegroundColor Red }
    }

    # File output
    $logFile = "$LOGS_PATH\master_launcher.log"
    $logEntry | Add-Content -Path $logFile -Encoding UTF8
}

# Banner display
function Show-EQ12Banner {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║                    🎯 EQ12 GODSTACK MASTER LAUNCHER                ║" -ForegroundColor Blue
    Write-Host "║                     Advanced System Orchestration                 ║" -ForegroundColor Blue
    Write-Host "╠════════════════════════════════════════════════════════════════════╣" -ForegroundColor Blue
    Write-Host "║  🚀 Launch System    🔍 System Status    🔄 Cold Restart         ║" -ForegroundColor White
    Write-Host "║  🛑 Shutdown System  🧪 Run Tests       📦 Install/Update        ║" -ForegroundColor White
    Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
    Write-Host ""
}

# System prerequisite checks
function Test-SystemPrerequisites {
    Write-EQ12Log "🔍 Checking system prerequisites..." "INFO"

    $checks = @{
        "Python" = $false
        "PowerShell" = $false
        "DirectoryStructure" = $false
        "DiskSpace" = $false
        "NetworkConnectivity" = $false
    }

    # Check Python
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $checks["Python"] = $true
            Write-EQ12Log "✅ Python detected: $pythonVersion" "SUCCESS"
        } else {
            Write-EQ12Log "❌ Python not found or not working" "ERROR"
        }
    } catch {
        Write-EQ12Log "❌ Python check failed: $($_.Exception.Message)" "ERROR"
    }

    # Check PowerShell version
    try {
        $psVersion = $PSVersionTable.PSVersion
        if ($psVersion.Major -ge 5) {
            $checks["PowerShell"] = $true
            Write-EQ12Log "✅ PowerShell $($psVersion.ToString()) detected" "SUCCESS"
        } else {
            Write-EQ12Log "⚠️ PowerShell version $($psVersion.ToString()) may have compatibility issues" "WARNING"
            $checks["PowerShell"] = $true  # Allow to continue
        }
    } catch {
        Write-EQ12Log "❌ PowerShell version check failed" "ERROR"
    }

    # Check directory structure
    $requiredDirs = @("scripts", "logs", "configs", "data", "dashboard", "tests")
    $missingDirs = @()

    foreach ($dir in $requiredDirs) {
        $dirPath = Join-Path $EQ12_ROOT $dir
        if (-not (Test-Path $dirPath)) {
            $missingDirs += $dir
            try {
                New-Item -Path $dirPath -ItemType Directory -Force | Out-Null
                Write-EQ12Log "📁 Created directory: $dir" "INFO"
            } catch {
                Write-EQ12Log "❌ Failed to create directory: $dir" "ERROR"
            }
        }
    }

    if ($missingDirs.Count -eq 0) {
        $checks["DirectoryStructure"] = $true
        Write-EQ12Log "✅ Directory structure validated" "SUCCESS"
    } else {
        Write-EQ12Log "⚠️ Created missing directories: $($missingDirs -join ', ')" "WARNING"
        $checks["DirectoryStructure"] = $true
    }

    # Check disk space (require at least 1GB free)
    try {
        $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
        $freeSpaceGB = [math]::Round($disk.FreeSpace / 1GB, 2)

        if ($freeSpaceGB -gt 1) {
            $checks["DiskSpace"] = $true
            Write-EQ12Log "✅ Disk space: $freeSpaceGB GB available" "SUCCESS"
        } else {
            Write-EQ12Log "⚠️ Low disk space: $freeSpaceGB GB available" "WARNING"
            $checks["DiskSpace"] = $true  # Allow to continue with warning
        }
    } catch {
        Write-EQ12Log "⚠️ Could not check disk space" "WARNING"
        $checks["DiskSpace"] = $true
    }

    # Check network connectivity
    try {
        $testConnection = Test-NetConnection -ComputerName "google.com" -Port 80 -WarningAction SilentlyContinue
        if ($testConnection.TcpTestSucceeded) {
            $checks["NetworkConnectivity"] = $true
            Write-EQ12Log "✅ Network connectivity confirmed" "SUCCESS"
        } else {
            Write-EQ12Log "⚠️ Network connectivity issues detected" "WARNING"
            $checks["NetworkConnectivity"] = $false
        }
    } catch {
        Write-EQ12Log "⚠️ Network connectivity check failed" "WARNING"
        $checks["NetworkConnectivity"] = $false
    }

    # Calculate overall health
    $passedChecks = ($checks.Values | Where-Object { $_ }).Count
    $totalChecks = $checks.Count
    $healthPercentage = [math]::Round(($passedChecks / $totalChecks) * 100, 1)

    Write-EQ12Log "📊 System Health: $passedChecks/$totalChecks checks passed ($healthPercentage%)" "INFO"

    return @{
        "Checks" = $checks
        "HealthPercentage" = $healthPercentage
        "IsHealthy" = ($healthPercentage -ge 80)
    }
}

# Launch the main orchestrator system
function Start-EQ12System {
    param(
        [switch]$AutoLaunch,
        [switch]$Headless
    )

    Write-EQ12Log "🚀 Initiating EQ12 GODSTACK system launch..." "INFO"

    # Verify orchestrator script exists
    if (-not (Test-Path $ORCHESTRATOR_SCRIPT)) {
        Write-EQ12Log "❌ Orchestrator script not found: $ORCHESTRATOR_SCRIPT" "ERROR"
        return $false
    }

    # Build command arguments
    $pythonArgs = @($ORCHESTRATOR_SCRIPT)

    if ($AutoLaunch -or (-not $Headless)) {
        $pythonArgs += "--auto-launch"
    }

    if ($Headless) {
        $pythonArgs += "--headless"
    }

    try {
        Write-EQ12Log "🔥 Executing: python $($pythonArgs -join ' ')" "INFO"

        # Start the orchestrator
        $process = Start-Process -FilePath "python" -ArgumentList $pythonArgs -NoNewWindow -PassThru

        if ($process) {
            Write-EQ12Log "✅ EQ12 GODSTACK orchestrator started (PID: $($process.Id))" "SUCCESS"
            Write-EQ12Log "🌐 Dashboard will be available at: http://localhost:8080/eq12_realtime_dashboard.html" "INFO"
            Write-EQ12Log "🔗 WebSocket server will be available at: ws://localhost:8765" "INFO"

            # Monitor the process for a few seconds
            Start-Sleep -Seconds 5

            if (-not $process.HasExited) {
                Write-EQ12Log "🎯 System appears to be starting successfully" "SUCCESS"

                if (-not $Headless) {
                    Write-EQ12Log "⌚ Waiting for system initialization (30 seconds)..." "INFO"
                    Start-Sleep -Seconds 25  # Give system time to start

                    # Try to open the dashboard
                    try {
                        Start-Process "http://localhost:8080/eq12_realtime_dashboard.html"
                        Write-EQ12Log "🌐 Dashboard launched in browser" "SUCCESS"
                    } catch {
                        Write-EQ12Log "⚠️ Could not auto-launch browser - navigate manually to http://localhost:8080/eq12_realtime_dashboard.html" "WARNING"
                    }
                }

                return $true
            } else {
                $exitCode = $process.ExitCode
                Write-EQ12Log "❌ Orchestrator process exited prematurely (Exit Code: $exitCode)" "ERROR"
                return $false
            }
        } else {
            Write-EQ12Log "❌ Failed to start orchestrator process" "ERROR"
            return $false
        }
    } catch {
        Write-EQ12Log "❌ Error starting system: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Get comprehensive system status
function Get-EQ12SystemStatus {
    Write-EQ12Log "📊 Gathering comprehensive system status..." "INFO"

    # Check if orchestrator is running
    $orchestratorRunning = $false
    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue
    foreach ($proc in $processes) {
        try {
            $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
            if ($cmdLine -like "*eq12_godstack_orchestrator.py*") {
                $orchestratorRunning = $true
                Write-EQ12Log "✅ Orchestrator is running (PID: $($proc.Id))" "SUCCESS"
                break
            }
        } catch {
            # Ignore errors getting command line
        }
    }

    if (-not $orchestratorRunning) {
        Write-EQ12Log "❌ Orchestrator is not running" "ERROR"
    }

    # Check dashboard accessibility
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        Write-EQ12Log "✅ Dashboard HTTP server is accessible" "SUCCESS"
    } catch {
        Write-EQ12Log "❌ Dashboard HTTP server is not accessible" "ERROR"
    }

    # Check WebSocket server
    try {
        $tcpConnection = Test-NetConnection -ComputerName "localhost" -Port 8765 -WarningAction SilentlyContinue
        if ($tcpConnection.TcpTestSucceeded) {
            Write-EQ12Log "✅ WebSocket server is listening" "SUCCESS"
        } else {
            Write-EQ12Log "❌ WebSocket server is not accessible" "ERROR"
        }
    } catch {
        Write-EQ12Log "❌ WebSocket server check failed" "ERROR"
    }

    # Check database
    $dbPath = "$EQ12_ROOT\data\sports_betting.db"
    if (Test-Path $dbPath) {
        $dbSize = [math]::Round((Get-Item $dbPath).Length / 1MB, 2)
        Write-EQ12Log "✅ Database exists ($dbSize MB)" "SUCCESS"
    } else {
        Write-EQ12Log "❌ Database file not found" "ERROR"
    }

    # Check recent log activity
    $logFiles = Get-ChildItem -Path $LOGS_PATH -Filter "*.log" -ErrorAction SilentlyContinue
    $recentActivity = $false

    foreach ($logFile in $logFiles) {
        if ($logFile.LastWriteTime -gt (Get-Date).AddMinutes(-5)) {
            $recentActivity = $true
            break
        }
    }

    if ($recentActivity) {
        Write-EQ12Log "✅ Recent system activity detected" "SUCCESS"
    } else {
        Write-EQ12Log "⚠️ No recent system activity in logs" "WARNING"
    }

    return @{
        "OrchestratorRunning" = $orchestratorRunning
        "DatabaseExists" = (Test-Path $dbPath)
        "RecentActivity" = $recentActivity
    }
}

# Execute cold restart
function Invoke-EQ12ColdRestart {
    param(
        [switch]$Force
    )

    Write-EQ12Log "🔥 Initiating EQ12 GODSTACK cold restart..." "WARNING"

    if (-not (Test-Path $COLD_RESTART_SCRIPT)) {
        Write-EQ12Log "❌ Cold restart script not found: $COLD_RESTART_SCRIPT" "ERROR"
        return $false
    }

    $restartArgs = @($COLD_RESTART_SCRIPT, "--action", "restart")

    if ($Force) {
        $restartArgs += "--force"
    }

    try {
        Write-EQ12Log "🔄 Executing cold restart process..." "INFO"

        $result = & python @restartArgs
        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            Write-EQ12Log "✅ Cold restart completed successfully" "SUCCESS"
            return $true
        } else {
            Write-EQ12Log "❌ Cold restart failed (Exit Code: $exitCode)" "ERROR"
            return $false
        }
    } catch {
        Write-EQ12Log "❌ Cold restart error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Graceful system shutdown
function Stop-EQ12System {
    Write-EQ12Log "🛑 Initiating graceful system shutdown..." "INFO"

    # Find and terminate orchestrator processes
    $stopped = $false
    $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue

    foreach ($proc in $processes) {
        try {
            $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
            if ($cmdLine -like "*eq12_godstack_orchestrator.py*") {
                Write-EQ12Log "🔄 Stopping orchestrator process (PID: $($proc.Id))" "INFO"

                # Send graceful termination signal (Ctrl+C equivalent)
                $proc.CloseMainWindow()
                Start-Sleep -Seconds 5

                if (-not $proc.HasExited) {
                    Write-EQ12Log "⚡ Force terminating process..." "WARNING"
                    $proc.Kill()
                }

                $stopped = $true
                Write-EQ12Log "✅ Orchestrator process stopped" "SUCCESS"
                break
            }
        } catch {
            Write-EQ12Log "⚠️ Error checking process: $($_.Exception.Message)" "WARNING"
        }
    }

    if (-not $stopped) {
        Write-EQ12Log "ℹ️ No orchestrator processes found running" "INFO"
    }

    # Stop any other EQ12 related processes
    $eq12Processes = Get-Process | Where-Object {
        $_.ProcessName -like "*eq12*" -or
        ($_.MainWindowTitle -like "*EQ12*")
    }

    foreach ($proc in $eq12Processes) {
        try {
            Write-EQ12Log "🔄 Stopping EQ12 process: $($proc.ProcessName) (PID: $($proc.Id))" "INFO"
            $proc.CloseMainWindow()
            Start-Sleep -Seconds 2

            if (-not $proc.HasExited) {
                $proc.Kill()
            }
        } catch {
            Write-EQ12Log "⚠️ Could not stop process $($proc.ProcessName): $($_.Exception.Message)" "WARNING"
        }
    }

    Write-EQ12Log "✅ System shutdown complete" "SUCCESS"
    return $true
}

# Run comprehensive system tests
function Invoke-EQ12SystemTests {
    Write-EQ12Log "🧪 Running comprehensive system tests..." "INFO"

    # Check if optimized test runner exists
    $testRunner = "$EQ12_ROOT\Run-EQ12TestsOptimized.ps1"
    if (Test-Path $testRunner) {
        try {
            Write-EQ12Log "🚀 Executing optimized Pester test suite..." "INFO"

            $testResult = & powershell -ExecutionPolicy Bypass -File $testRunner -TargetScript $ADVANCED_WRAPPER
            $exitCode = $LASTEXITCODE

            if ($exitCode -eq 0) {
                Write-EQ12Log "✅ All tests passed successfully" "SUCCESS"
                return $true
            } else {
                Write-EQ12Log "❌ Some tests failed (Exit Code: $exitCode)" "ERROR"
                return $false
            }
        } catch {
            Write-EQ12Log "❌ Test execution error: $($_.Exception.Message)" "ERROR"
            return $false
        }
    } else {
        Write-EQ12Log "⚠️ Optimized test runner not found, running basic tests..." "WARNING"

        # Run basic system checks
        $healthCheck = Test-SystemPrerequisites
        return $healthCheck.IsHealthy
    }
}

# Install or update system components
function Install-EQ12System {
    Write-EQ12Log "📦 Installing/updating EQ12 system components..." "INFO"

    # Check for Python packages
    try {
        Write-EQ12Log "📋 Checking Python dependencies..." "INFO"

        $requiredPackages = @(
            "asyncio",
            "sqlite3",
            "psutil",
            "websockets",
            "playwright"
        )

        foreach ($package in $requiredPackages) {
            try {
                $result = & python -c "import $package; print('✅ $package')" 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-EQ12Log "✅ Python package available: $package" "SUCCESS"
                } else {
                    Write-EQ12Log "⚠️ Python package may need installation: $package" "WARNING"
                }
            } catch {
                Write-EQ12Log "⚠️ Could not check package: $package" "WARNING"
            }
        }
    } catch {
        Write-EQ12Log "⚠️ Python package check failed" "WARNING"
    }

    # Check PowerShell modules
    try {
        $requiredModules = @("Pester")

        foreach ($module in $requiredModules) {
            $moduleInfo = Get-Module -Name $module -ListAvailable
            if ($moduleInfo) {
                Write-EQ12Log "✅ PowerShell module available: $module" "SUCCESS"
            } else {
                Write-EQ12Log "⚠️ PowerShell module may need installation: $module" "WARNING"
            }
        }
    } catch {
        Write-EQ12Log "⚠️ PowerShell module check failed" "WARNING"
    }

    Write-EQ12Log "✅ System component check complete" "SUCCESS"
    return $true
}

# Main execution logic
function Main {
    Show-EQ12Banner

    Write-EQ12Log "🎯 EQ12 GODSTACK Master Launcher started with action: $Action" "INFO"

    # Run prerequisite checks for most actions
    if ($Action -ne "shutdown") {
        $healthCheck = Test-SystemPrerequisites

        if (-not $healthCheck.IsHealthy -and -not $Force) {
            Write-EQ12Log "⚠️ System health check failed ($($healthCheck.HealthPercentage)% healthy)" "WARNING"
            Write-EQ12Log "Use -Force to proceed anyway, or resolve the issues above" "WARNING"
            exit 1
        }
    }

    # Execute requested action
    switch ($Action) {
        "launch" {
            $success = Start-EQ12System -AutoLaunch:$AutoLaunch -Headless:$Headless
            if ($success) {
                Write-EQ12Log "🎉 EQ12 GODSTACK launched successfully!" "SUCCESS"
                Write-EQ12Log "💡 Use 'eq12_godstack_master.ps1 -Action status' to check system health" "INFO"
                Write-EQ12Log "💡 Use 'eq12_godstack_master.ps1 -Action shutdown' for graceful shutdown" "INFO"
            } else {
                Write-EQ12Log "💥 Failed to launch EQ12 GODSTACK" "ERROR"
                exit 1
            }
        }

        "status" {
            $status = Get-EQ12SystemStatus
            Write-EQ12Log "📊 System status check complete" "INFO"
        }

        "restart" {
            $success = Invoke-EQ12ColdRestart -Force:$Force
            if (-not $success) {
                exit 1
            }
        }

        "shutdown" {
            $success = Stop-EQ12System
            if (-not $success) {
                exit 1
            }
        }

        "test" {
            $success = Invoke-EQ12SystemTests
            if (-not $success) {
                exit 1
            }
        }

        "install" {
            $success = Install-EQ12System
            if (-not $success) {
                exit 1
            }
        }

        "update" {
            Write-EQ12Log "🔄 Update action - running install checks..." "INFO"
            $success = Install-EQ12System
            if (-not $success) {
                exit 1
            }
        }

        default {
            Write-EQ12Log "❌ Unknown action: $Action" "ERROR"
            Write-EQ12Log "Valid actions: launch, status, restart, shutdown, test, install, update" "INFO"
            exit 1
        }
    }

    Write-EQ12Log "✅ Action '$Action' completed successfully" "SUCCESS"
}

# Execute main function with error handling
try {
    Main
} catch {
    Write-EQ12Log "💥 CRITICAL ERROR: $($_.Exception.Message)" "ERROR"
    Write-EQ12Log "Stack Trace: $($_.Exception.StackTrace)" "ERROR"
    exit 1
}
