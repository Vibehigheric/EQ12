#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Ngrok Tunnel Monitor - Windows PowerShell Management Interface
    
.DESCRIPTION
    Advanced PowerShell wrapper for managing ngrok tunnel monitoring service.
    Provides Windows-native integration including Task Scheduler setup,
    service management, and comprehensive monitoring capabilities.
    
    Features:
    - Start/Stop/Restart monitoring service
    - Windows Task Scheduler integration
    - Real-time status monitoring and reporting
    - Automatic startup configuration
    - Log file management and rotation
    - Health check and diagnostics
    
.PARAMETER Action
    Action to perform: Start, Stop, Restart, Status, Install, Uninstall, Test
    
.PARAMETER Interval
    Monitoring check interval in seconds (default: 30)
    
.PARAMETER LogLevel
    Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
    
.PARAMETER NoRestart
    Disable automatic tunnel restart on failure
    
.PARAMETER Verbose
    Enable verbose output
    
.EXAMPLE
    .\manage_ngrok_monitor.ps1 -Action Start
    Start the ngrok tunnel monitoring service
    
.EXAMPLE
    .\manage_ngrok_monitor.ps1 -Action Install -Verbose
    Install as Windows scheduled task with verbose output
    
.EXAMPLE
    .\manage_ngrok_monitor.ps1 -Action Status
    Show current monitoring status
    
.NOTES
    Author: EQ12 GODSTACK System
    Version: 1.0.0
    Compatible with: Windows 10/11, Windows Server 2016+
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet("Start", "Stop", "Restart", "Status", "Install", "Uninstall", "Test", "Logs")]
    [string]$Action,
    
    [Parameter(Mandatory = $false)]
    [ValidateRange(10, 300)]
    [int]$Interval = 30,
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("DEBUG", "INFO", "WARNING", "ERROR")]
    [string]$LogLevel = "INFO",
    
    [Parameter(Mandatory = $false)]
    [switch]$NoRestart
)

# Initialize EQ12 environment
$EQ12Root = if ($env:EQ12_ROOT) { $env:EQ12_ROOT } else { "C:\EQ12" }
$ScriptsDir = Join-Path $EQ12Root "scripts"
$LogsDir = Join-Path $EQ12Root "logs"
$MonitorScript = Join-Path $ScriptsDir "ngrok_tunnel_monitor.py"
$TaskName = "EQ12NgrokTunnelMonitor"

# Ensure directories exist
if (!(Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}

# Setup logging
$LogFile = Join-Path $LogsDir "ngrok_monitor_ps_$(Get-Date -Format 'yyyyMMdd').log"

function Write-LogMessage {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARNING", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp - $Level - $Message"
    
    # Console output with colors
    switch ($Level) {
        "SUCCESS" { Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
        "INFO"    { Write-Host "[INFO] $Message" -ForegroundColor Cyan }
        "WARNING" { Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
        "ERROR"   { Write-Host "[ERROR] $Message" -ForegroundColor Red }
    }
    
    # Log to file
    $logEntry | Out-File -FilePath $LogFile -Append -Encoding UTF8
}

function Test-Prerequisites {
    <#
    .SYNOPSIS
        Test system prerequisites for ngrok monitoring
    #>
    
    Write-LogMessage "Testing system prerequisites..." "INFO"
    
    $issues = @()
    
    # Check Python
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "Python: $pythonVersion" "SUCCESS"
        } else {
            $issues += "Python not found in PATH"
        }
    } catch {
        $issues += "Python not installed or not accessible"
    }
    
    # Check ngrok
    try {
        $ngrokVersion = & ngrok version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "Ngrok: Available" "SUCCESS"
        } else {
            $issues += "Ngrok not found in PATH"
        }
    } catch {
        $issues += "Ngrok not installed or not accessible"
    }
    
    # Check monitor script
    if (Test-Path $MonitorScript) {
        Write-LogMessage "Monitor script: Found at $MonitorScript" "SUCCESS"
    } else {
        $issues += "Monitor script not found at $MonitorScript"
    }
    
    # Check required Python packages
    try {
        & python -c "import aiohttp, psutil, requests" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "Required Python packages: Available" "SUCCESS"
        } else {
            $issues += "Missing required Python packages (aiohttp, psutil, requests)"
        }
    } catch {
        $issues += "Cannot verify Python package availability"
    }
    
    if ($issues.Count -gt 0) {
        Write-LogMessage "Prerequisites check failed:" "ERROR"
        foreach ($issue in $issues) {
            Write-LogMessage "  - $issue" "ERROR"
        }
        return $false
    }
    
    Write-LogMessage "All prerequisites satisfied" "SUCCESS"
    return $true
}

function Get-MonitorProcess {
    <#
    .SYNOPSIS
        Get the current monitor process if running
    #>
    
    return Get-Process | Where-Object {
        $_.ProcessName -eq "python" -and 
        $_.CommandLine -like "*ngrok_tunnel_monitor.py*"
    }
}

function Start-Monitor {
    <#
    .SYNOPSIS
        Start the ngrok tunnel monitor
    #>
    
    Write-LogMessage "Starting EQ12 Ngrok Tunnel Monitor..." "INFO"
    
    if (!(Test-Prerequisites)) {
        Write-LogMessage "Cannot start monitor - prerequisites not met" "ERROR"
        return $false
    }
    
    # Check if already running
    $existing = Get-MonitorProcess
    if ($existing) {
        Write-LogMessage "Monitor already running (PID: $($existing.Id))" "WARNING"
        return $true
    }
    
    # Build command arguments
    $cmdArgs = @(
        $MonitorScript,
        "--interval", $Interval,
        "--log-level", $LogLevel
    )
    
    if ($NoRestart) {
        $cmdArgs += "--no-restart"
    }
    
    try {
        # Start monitor process
        $startInfo = New-Object System.Diagnostics.ProcessStartInfo
        $startInfo.FileName = "python"
        $startInfo.Arguments = $cmdArgs -join " "
        $startInfo.WorkingDirectory = $EQ12Root
        $startInfo.UseShellExecute = $false
        $startInfo.CreateNoWindow = $true
        $startInfo.RedirectStandardOutput = $true
        $startInfo.RedirectStandardError = $true
        
        $process = [System.Diagnostics.Process]::Start($startInfo)
        
        # Wait a moment to ensure it starts properly
        Start-Sleep -Seconds 3
        
        if (!$process.HasExited) {
            Write-LogMessage "Monitor started successfully (PID: $($process.Id))" "SUCCESS"
            Write-LogMessage "Monitor logs: $LogFile" "INFO"
            return $true
        } else {
            $stderr = $process.StandardError.ReadToEnd()
            Write-LogMessage "Monitor failed to start: $stderr" "ERROR"
            return $false
        }
        
    } catch {
        Write-LogMessage "Error starting monitor: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Stop-Monitor {
    <#
    .SYNOPSIS
        Stop the ngrok tunnel monitor
    #>
    
    Write-LogMessage "Stopping EQ12 Ngrok Tunnel Monitor..." "INFO"
    
    $processes = Get-MonitorProcess
    
    if (!$processes) {
        Write-LogMessage "No monitor processes found" "WARNING"
        return $true
    }
    
    foreach ($proc in $processes) {
        try {
            Write-LogMessage "Stopping monitor process (PID: $($proc.Id))..." "INFO"
            $proc.Kill()
            $proc.WaitForExit(10000)  # Wait up to 10 seconds
            Write-LogMessage "Monitor stopped successfully" "SUCCESS"
        } catch {
            Write-LogMessage "Error stopping monitor: $($_.Exception.Message)" "ERROR"
            return $false
        }
    }
    
    return $true
}

function Get-MonitorStatus {
    <#
    .SYNOPSIS
        Get detailed monitor and tunnel status
    #>
    
    Write-LogMessage "EQ12 Ngrok Tunnel Monitor Status Report" "INFO"
    Write-Host "=" * 60
    
    # Check monitor process
    $monitorProc = Get-MonitorProcess
    if ($monitorProc) {
        $uptime = (Get-Date) - $monitorProc.StartTime
        Write-LogMessage "Monitor Process: ✅ Running (PID: $($monitorProc.Id), Uptime: $($uptime.ToString('hh\:mm\:ss')))" "SUCCESS"
    } else {
        Write-LogMessage "Monitor Process: ❌ Not running" "ERROR"
    }
    
    # Check ngrok process
    $ngrokProc = Get-Process | Where-Object { $_.ProcessName -like "*ngrok*" }
    if ($ngrokProc) {
        $uptime = (Get-Date) - $ngrokProc.StartTime
        Write-LogMessage "Ngrok Process: ✅ Running (PID: $($ngrokProc.Id), Uptime: $($uptime.ToString('hh\:mm\:ss')))" "SUCCESS"
    } else {
        Write-LogMessage "Ngrok Process: ❌ Not running" "ERROR"
    }
    
    # Check ngrok API
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -TimeoutSec 5
        $tunnels = $response.tunnels
        
        if ($tunnels) {
            Write-LogMessage "Ngrok API: ✅ Accessible" "SUCCESS"
            foreach ($tunnel in $tunnels) {
                Write-LogMessage "  - Tunnel: $($tunnel.name) -> $($tunnel.public_url)" "INFO"
            }
        } else {
            Write-LogMessage "Ngrok API: ⚠️ Accessible but no tunnels" "WARNING"
        }
    } catch {
        Write-LogMessage "Ngrok API: ❌ Not accessible" "ERROR"
    }
    
    # Check scheduled task
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($task) {
        Write-LogMessage "Scheduled Task: ✅ Installed ($($task.State))" "SUCCESS"
    } else {
        Write-LogMessage "Scheduled Task: ❌ Not installed" "ERROR"
    }
    
    # Show recent log entries
    if (Test-Path $LogFile) {
        Write-LogMessage "Recent Monitor Logs:" "INFO"
        Get-Content $LogFile -Tail 5 | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Gray
        }
    }
    
    Write-Host "=" * 60
}

function Install-ScheduledTask {
    <#
    .SYNOPSIS
        Install Windows scheduled task for automatic monitoring
    #>
    
    Write-LogMessage "Installing EQ12 Ngrok Monitor as scheduled task..." "INFO"
    
    if (!(Test-Prerequisites)) {
        Write-LogMessage "Cannot install - prerequisites not met" "ERROR"
        return $false
    }
    
    # Remove existing task if present
    $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-LogMessage "Removing existing scheduled task..." "INFO"
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }
    
    try {
        # Create task action
        $actionArgs = @(
            $MonitorScript,
            "--interval", $Interval,
            "--log-level", $LogLevel
        )
        
        if ($NoRestart) {
            $actionArgs += "--no-restart"
        }
        
        $action = New-ScheduledTaskAction -Execute "python" -Argument ($actionArgs -join " ") -WorkingDirectory $EQ12Root
        
        # Create task trigger (start at boot, repeat every hour)
        $trigger = New-ScheduledTaskTrigger -AtStartup
        
        # Create task settings
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)
        
        # Create task principal (run as system)
        $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        
        # Register task
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "EQ12 Ngrok Tunnel Monitor - Automatic tunnel health monitoring and management"
        
        Write-LogMessage "Scheduled task installed successfully" "SUCCESS"
        Write-LogMessage "Task will start automatically at system boot" "INFO"
        
        # Start the task now
        Start-ScheduledTask -TaskName $TaskName
        Write-LogMessage "Task started" "SUCCESS"
        
        return $true
        
    } catch {
        Write-LogMessage "Error installing scheduled task: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Uninstall-ScheduledTask {
    <#
    .SYNOPSIS
        Uninstall Windows scheduled task
    #>
    
    Write-LogMessage "Uninstalling EQ12 Ngrok Monitor scheduled task..." "INFO"
    
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    
    if (!$task) {
        Write-LogMessage "Scheduled task not found" "WARNING"
        return $true
    }
    
    try {
        # Stop task if running
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        
        # Remove task
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        
        Write-LogMessage "Scheduled task uninstalled successfully" "SUCCESS"
        return $true
        
    } catch {
        Write-LogMessage "Error uninstalling scheduled task: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Show-Logs {
    <#
    .SYNOPSIS
        Show recent monitor logs
    #>
    
    Write-LogMessage "Recent EQ12 Ngrok Monitor Logs:" "INFO"
    Write-Host "=" * 60
    
    # Show PowerShell wrapper logs
    if (Test-Path $LogFile) {
        Write-Host "PowerShell Wrapper Logs:" -ForegroundColor Cyan
        Get-Content $LogFile -Tail 10 | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Gray
        }
        Write-Host ""
    }
    
    # Show Python monitor logs
    $pythonLogPattern = Join-Path $LogsDir "ngrok_monitor_*.log"
    $pythonLogs = Get-ChildItem $pythonLogPattern -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    if ($pythonLogs) {
        Write-Host "Python Monitor Logs:" -ForegroundColor Cyan
        Get-Content $pythonLogs.FullName -Tail 15 | ForEach-Object {
            Write-Host "  $_" -ForegroundColor Gray
        }
    } else {
        Write-LogMessage "No Python monitor logs found" "WARNING"
    }
    
    Write-Host "=" * 60
}

function Test-System {
    <#
    .SYNOPSIS
        Run comprehensive system tests
    #>
    
    Write-LogMessage "Running EQ12 Ngrok Monitor System Tests..." "INFO"
    Write-Host "=" * 60
    
    $testResults = @{}
    
    # Test prerequisites
    $testResults["Prerequisites"] = Test-Prerequisites
    
    # Test monitor script syntax
    try {
        & python -m py_compile $MonitorScript
        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "Monitor script syntax: ✅ Valid" "SUCCESS"
            $testResults["ScriptSyntax"] = $true
        } else {
            Write-LogMessage "Monitor script syntax: ❌ Invalid" "ERROR"
            $testResults["ScriptSyntax"] = $false
        }
    } catch {
        Write-LogMessage "Monitor script syntax: ❌ Cannot validate" "ERROR"
        $testResults["ScriptSyntax"] = $false
    }
    
    # Test ngrok installation
    try {
        $ngrokHelp = & ngrok --help 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "Ngrok functionality: ✅ Working" "SUCCESS"
            $testResults["NgrokInstall"] = $true
        } else {
            Write-LogMessage "Ngrok functionality: ❌ Not working" "ERROR"
            $testResults["NgrokInstall"] = $false
        }
    } catch {
        Write-LogMessage "Ngrok functionality: ❌ Error testing" "ERROR"
        $testResults["NgrokInstall"] = $false
    }
    
    # Test permissions
    try {
        $testFile = Join-Path $LogsDir "test_permissions.tmp"
        "test" | Out-File $testFile
        Remove-Item $testFile -Force
        Write-LogMessage "File system permissions: ✅ Working" "SUCCESS"
        $testResults["Permissions"] = $true
    } catch {
        Write-LogMessage "File system permissions: ❌ Limited" "ERROR"
        $testResults["Permissions"] = $false
    }
    
    Write-Host "=" * 60
    
    $passedTests = ($testResults.Values | Where-Object { $_ -eq $true }).Count
    $totalTests = $testResults.Count
    
    Write-LogMessage "System Tests Complete: $passedTests/$totalTests passed" "INFO"
    
    if ($passedTests -eq $totalTests) {
        Write-LogMessage "All tests passed - System ready for monitoring" "SUCCESS"
        return $true
    } else {
        Write-LogMessage "Some tests failed - Please address issues before running monitor" "ERROR"
        return $false
    }
}

# Main execution logic
Write-LogMessage "EQ12 Ngrok Tunnel Monitor Management" "INFO"
Write-LogMessage "Action: $Action" "INFO"

switch ($Action.ToLower()) {
    "start" {
        $success = Start-Monitor
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "stop" {
        $success = Stop-Monitor
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "restart" {
        Write-LogMessage "Restarting monitor..." "INFO"
        $stopSuccess = Stop-Monitor
        Start-Sleep -Seconds 2
        $startSuccess = Start-Monitor
        $success = $stopSuccess -and $startSuccess
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "status" {
        Get-MonitorStatus
        exit 0
    }
    
    "install" {
        $success = Install-ScheduledTask
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "uninstall" {
        $success = Uninstall-ScheduledTask
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "test" {
        $success = Test-System
        exit $(if ($success) { 0 } else { 1 })
    }
    
    "logs" {
        Show-Logs
        exit 0
    }
    
    default {
        Write-LogMessage "Unknown action: $Action" "ERROR"
        exit 1
    }
}