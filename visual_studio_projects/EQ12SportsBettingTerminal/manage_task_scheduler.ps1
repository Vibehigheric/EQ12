# EQ12 Task Scheduler Management Script
# Final Form Implementation for Windows Task Scheduler Integration
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Install", "Uninstall", "Start", "Stop", "Status", "Logs", "Test")]
    [string]$Action,

    [Parameter()]
    [string]$TaskName = "EQ12SportsBettingDailyOps",

    [Parameter()]
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Configuration
$TASK_XML_PATH = Join-Path $PSScriptRoot "EQ12_Daily_Operations.xml"
$LOG_PATH = "C:\EQ12\logs\task_scheduler_$(Get-Date -Format 'yyyyMMdd').log"

function Write-TaskLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    Write-Host $logEntry -ForegroundColor $(switch ($Level) {
            "ERROR" { "Red" }
            "WARN" { "Yellow" }
            "SUCCESS" { "Green" }
            default { "Cyan" }
        })

    # Ensure log directory exists
    $logDir = Split-Path $LOG_PATH -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -Path $logDir -ItemType Directory -Force | Out-Null
    }

    Add-Content -Path $LOG_PATH -Value $logEntry
}

function Test-AdminPrivileges {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

    if (-not $isAdmin) {
        throw "This script requires Administrator privileges. Please run as Administrator."
    }
}

function Install-EQ12Task {
    Write-TaskLog "🔧 Installing EQ12 Task Scheduler..." "INFO"

    try {
        # Check if task already exists
        $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

        if ($existingTask -and -not $Force) {
            Write-TaskLog "Task '$TaskName' already exists. Use -Force to overwrite." "WARN"
            return
        }

        if ($existingTask -and $Force) {
            Write-TaskLog "Removing existing task '$TaskName'..." "INFO"
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        }

        # Validate XML file exists
        if (-not (Test-Path $TASK_XML_PATH)) {
            throw "Task XML file not found: $TASK_XML_PATH"
        }

        # Read and update XML with current user SID
        $xmlContent = Get-Content $TASK_XML_PATH -Raw
        $currentSid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
        $xmlContent = $xmlContent -replace "S-1-5-21-0-0-0-1000", $currentSid

        # Create temporary XML file with updated SID
        $tempXmlPath = [System.IO.Path]::GetTempFileName() + ".xml"
        Set-Content -Path $tempXmlPath -Value $xmlContent

        try {
            # Register the task
            Register-ScheduledTask -Xml (Get-Content $tempXmlPath -Raw) -TaskName $TaskName | Out-Null

            Write-TaskLog "✅ Task '$TaskName' installed successfully" "SUCCESS"

            # Verify installation
            $task = Get-ScheduledTask -TaskName $TaskName
            Write-TaskLog "Task Status: $($task.State)" "INFO"

            # Show next run times
            $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
            if ($taskInfo.NextRunTime) {
                Write-TaskLog "Next Run: $($taskInfo.NextRunTime)" "INFO"
            }

        }
        finally {
            # Clean up temporary file
            if (Test-Path $tempXmlPath) {
                Remove-Item $tempXmlPath -Force
            }
        }

    }
    catch {
        Write-TaskLog "❌ Failed to install task: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Uninstall-EQ12Task {
    Write-TaskLog "🗑️ Uninstalling EQ12 Task Scheduler..." "INFO"

    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

        if (-not $task) {
            Write-TaskLog "Task '$TaskName' not found" "WARN"
            return
        }

        # Stop task if running
        if ($task.State -eq "Running") {
            Write-TaskLog "Stopping running task..." "INFO"
            Stop-ScheduledTask -TaskName $TaskName
            Start-Sleep -Seconds 2
        }

        # Unregister task
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false

        Write-TaskLog "✅ Task '$TaskName' uninstalled successfully" "SUCCESS"

    }
    catch {
        Write-TaskLog "❌ Failed to uninstall task: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Start-EQ12Task {
    Write-TaskLog "▶️ Starting EQ12 Task..." "INFO"

    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

        if (-not $task) {
            throw "Task '$TaskName' not found. Install it first."
        }

        Start-ScheduledTask -TaskName $TaskName

        Write-TaskLog "✅ Task '$TaskName' started successfully" "SUCCESS"

        # Wait a moment and check status
        Start-Sleep -Seconds 2
        $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
        Write-TaskLog "Current Status: $($taskInfo.TaskState)" "INFO"

    }
    catch {
        Write-TaskLog "❌ Failed to start task: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Stop-EQ12Task {
    Write-TaskLog "⏹️ Stopping EQ12 Task..." "INFO"

    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

        if (-not $task) {
            throw "Task '$TaskName' not found"
        }

        if ($task.State -ne "Running") {
            Write-TaskLog "Task is not currently running" "INFO"
            return
        }

        Stop-ScheduledTask -TaskName $TaskName

        Write-TaskLog "✅ Task '$TaskName' stopped successfully" "SUCCESS"

    }
    catch {
        Write-TaskLog "❌ Failed to stop task: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Get-EQ12TaskStatus {
    Write-TaskLog "📊 Checking EQ12 Task Status..." "INFO"

    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

        if (-not $task) {
            Write-TaskLog "❌ Task '$TaskName' not found" "ERROR"
            return
        }

        $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName

        Write-TaskLog "=== EQ12 Task Status ===" "SUCCESS"
        Write-TaskLog "Task Name: $($task.TaskName)" "INFO"
        Write-TaskLog "State: $($task.State)" "INFO"
        Write-TaskLog "Current Status: $($taskInfo.TaskState)" "INFO"
        Write-TaskLog "Last Run Time: $($taskInfo.LastRunTime)" "INFO"
        Write-TaskLog "Next Run Time: $($taskInfo.NextRunTime)" "INFO"
        Write-TaskLog "Last Result: $($taskInfo.LastTaskResult)" "INFO"
        Write-TaskLog "Number of Missed Runs: $($taskInfo.NumberOfMissedRuns)" "INFO"

        # Show triggers
        Write-TaskLog "=== Scheduled Triggers ===" "SUCCESS"
        $triggers = $task.Triggers
        foreach ($trigger in $triggers) {
            if ($trigger.CimClass.CimClassName -eq "MSFT_TaskDailyTrigger") {
                Write-TaskLog "Daily at: $($trigger.StartBoundary)" "INFO"
            }
        }

        # Show recent history
        Write-TaskLog "=== Recent Execution History ===" "SUCCESS"
        try {
            $events = Get-WinEvent -FilterHashtable @{LogName = 'Microsoft-Windows-TaskScheduler/Operational'; ID = 200, 201 } -MaxEvents 10 |
            Where-Object { $_.Message -like "*$TaskName*" } |
            Select-Object TimeCreated, Id, LevelDisplayName, Message

            foreach ($event in $events) {
                $status = if ($event.Id -eq 200) { "Started" } else { "Completed" }
                Write-TaskLog "$($event.TimeCreated): $status" "INFO"
            }
        }
        catch {
            Write-TaskLog "Could not retrieve execution history" "WARN"
        }

    }
    catch {
        Write-TaskLog "❌ Failed to get task status: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Get-EQ12TaskLogs {
    Write-TaskLog "📋 Retrieving EQ12 Task Logs..." "INFO"

    try {
        # Show recent PowerShell logs
        $logPattern = "C:\EQ12\logs\daily_operations_*.log"
        $logFiles = Get-ChildItem -Path $logPattern -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending

        if ($logFiles) {
            Write-TaskLog "=== Recent Log Files ===" "SUCCESS"
            foreach ($logFile in $logFiles | Select-Object -First 5) {
                Write-TaskLog "$($logFile.Name) (Size: $([math]::Round($logFile.Length/1KB, 1)) KB)" "INFO"
            }

            # Show last 20 lines of most recent log
            $latestLog = $logFiles | Select-Object -First 1
            if ($latestLog) {
                Write-TaskLog "=== Latest Log Content (Last 20 Lines) ===" "SUCCESS"
                $content = Get-Content -Path $latestLog.FullName -Tail 20
                foreach ($line in $content) {
                    Write-Host $line
                }
            }
        }
        else {
            Write-TaskLog "No log files found matching pattern: $logPattern" "WARN"
        }

        # Show Windows Event Log entries
        Write-TaskLog "=== Windows Task Scheduler Events ===" "SUCCESS"
        try {
            $events = Get-WinEvent -FilterHashtable @{LogName = 'Microsoft-Windows-TaskScheduler/Operational' } -MaxEvents 50 |
            Where-Object { $_.Message -like "*$TaskName*" } |
            Select-Object TimeCreated, Id, LevelDisplayName, Message -First 10

            foreach ($event in $events) {
                Write-TaskLog "$($event.TimeCreated) [$($event.Id)] $($event.LevelDisplayName): $($event.Message)" "INFO"
            }
        }
        catch {
            Write-TaskLog "Could not retrieve Windows Event Log entries" "WARN"
        }

    }
    catch {
        Write-TaskLog "❌ Failed to retrieve logs: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Test-EQ12Task {
    Write-TaskLog "🧪 Testing EQ12 Task Configuration..." "INFO"

    try {
        # Test prerequisites
        Write-TaskLog "Checking prerequisites..." "INFO"

        # Check CLI executable
        $cliPath = "C:\EQ12\visual_studio_projects\EQ12SportsBettingTerminal\bin\Debug\Eq12Cli.exe"
        if (-not (Test-Path $cliPath)) {
            Write-TaskLog "❌ EQ12 CLI not found at: $cliPath" "ERROR"
        }
        else {
            Write-TaskLog "✅ EQ12 CLI found" "SUCCESS"
        }

        # Check config file
        $configPath = "C:\EQ12\visual_studio_projects\EQ12SportsBettingTerminal\Config\config.json"
        if (-not (Test-Path $configPath)) {
            Write-TaskLog "❌ Config file not found at: $configPath" "ERROR"
        }
        else {
            Write-TaskLog "✅ Config file found" "SUCCESS"
        }

        # Test PowerShell script
        $scriptPath = Join-Path $PSScriptRoot "daily_operations.ps1"
        if (-not (Test-Path $scriptPath)) {
            Write-TaskLog "❌ Daily operations script not found at: $scriptPath" "ERROR"
        }
        else {
            Write-TaskLog "✅ Daily operations script found" "SUCCESS"
        }

        # Check XML file
        if (-not (Test-Path $TASK_XML_PATH)) {
            Write-TaskLog "❌ Task XML not found at: $TASK_XML_PATH" "ERROR"
        }
        else {
            Write-TaskLog "✅ Task XML found" "SUCCESS"
        }

        # Test network connectivity
        try {
            $response = Invoke-WebRequest -Uri "https://api.telegram.org" -UseBasicParsing -TimeoutSec 10
            Write-TaskLog "✅ Network connectivity (Telegram API): OK" "SUCCESS"
        }
        catch {
            Write-TaskLog "❌ Network connectivity test failed: $($_.Exception.Message)" "ERROR"
        }

        # Run a quick health check via CLI
        Write-TaskLog "Running CLI health check..." "INFO"
        try {
            $result = & $cliPath "health" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-TaskLog "✅ CLI health check: PASSED" "SUCCESS"
            }
            else {
                Write-TaskLog "❌ CLI health check: FAILED - $result" "ERROR"
            }
        }
        catch {
            Write-TaskLog "❌ CLI health check error: $($_.Exception.Message)" "ERROR"
        }

        Write-TaskLog "✅ Test completed" "SUCCESS"

    }
    catch {
        Write-TaskLog "❌ Test failed: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Show-Usage {
    Write-Host @"
🎯 EQ12 Task Scheduler Management Script

Usage: .\manage_task_scheduler.ps1 -Action [Action] [Parameters]

Actions:
  Install   - Install the EQ12 scheduled task
  Uninstall - Remove the EQ12 scheduled task
  Start     - Start the task immediately
  Stop      - Stop the running task
  Status    - Show detailed task status and history
  Logs      - Display recent log files and events
  Test      - Test task configuration and prerequisites

Parameters:
  -TaskName [Name]  - Custom task name (default: EQ12SportsBettingDailyOps)
  -Force           - Force overwrite existing task during install

Examples:
  .\manage_task_scheduler.ps1 -Action Install
  .\manage_task_scheduler.ps1 -Action Install -Force
  .\manage_task_scheduler.ps1 -Action Status
  .\manage_task_scheduler.ps1 -Action Start
  .\manage_task_scheduler.ps1 -Action Test

Notes:
  - Requires Administrator privileges
  - Task runs daily at 9:00 AM, 2:00 PM, and 9:00 PM
  - Logs are stored in C:\EQ12\logs\
  - Automatic restart on failure (3 attempts, 15min intervals)

"@
}

# Main execution
Write-TaskLog "🚀 EQ12 Task Scheduler Management - Action: $Action" "SUCCESS"

try {
    # Check admin privileges for most actions
    if ($Action -in @("Install", "Uninstall", "Start", "Stop")) {
        Test-AdminPrivileges
    }

    switch ($Action) {
        "Install" { Install-EQ12Task }
        "Uninstall" { Uninstall-EQ12Task }
        "Start" { Start-EQ12Task }
        "Stop" { Stop-EQ12Task }
        "Status" { Get-EQ12TaskStatus }
        "Logs" { Get-EQ12TaskLogs }
        "Test" { Test-EQ12Task }
        default { Show-Usage }
    }

}
catch {
    Write-TaskLog "❌ Operation failed: $($_.Exception.Message)" "ERROR"
    exit 1
}

Write-TaskLog "✅ Action '$Action' completed successfully" "SUCCESS"
