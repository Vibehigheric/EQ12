# EQ12 Windows Task Scheduler Automation Script
# Creates scheduled tasks for odds ingestion, AI optimization, and monitoring

param(
    [switch]$Install,
    [switch]$Remove,
    [switch]$Status,
    [switch]$RunNow
)

function Write-Status {
    param([string]$Message, [string]$Type = "Info")

    $color = switch ($Type) {
        "Success" { "Green" }
        "Warning" { "Yellow" }
        "Error" { "Red" }
        default { "White" }
    }
    Write-Host $Message -ForegroundColor $color
}

function Install-Tasks {
    Write-Status "Installing EQ12 scheduled tasks..." "Info"

    $pythonExe = "C:\EQ12\.venv\Scripts\python.exe"
    $workingDir = "C:\EQ12"

    # Task 1: Odds Ingestion (Every 5 minutes)
    $task1Name = "EQ12_OddsIngestion"
    $task1Action = New-ScheduledTaskAction -Execute $pythonExe -Argument "eq12_odds_api_client.py --league americanfootball_nfl --save mysql" -WorkingDirectory $workingDir
    $task1Trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 5) -At (Get-Date) -Once
    $task1Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $task1Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Limited

    try {
        Register-ScheduledTask -TaskName $task1Name -Action $task1Action -Trigger $task1Trigger -Settings $task1Settings -Principal $task1Principal -Force | Out-Null
        Write-Status "Odds ingestion task installed" "Success"
    }
    catch {
        Write-Status "Failed to install odds ingestion task: $_" "Error"
    }

    # Task 2: AI Optimization (Every 10 minutes)
    $task2Name = "EQ12_AIOptimization"
    $task2Action = New-ScheduledTaskAction -Execute $pythonExe -Argument "eq12_nfl_parlay_optimizer.py --bankroll 1000 --max-legs 12 --min-ev 2" -WorkingDirectory $workingDir
    $task2Trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 10) -At (Get-Date) -Once
    $task2Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $task2Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Limited

    try {
        Register-ScheduledTask -TaskName $task2Name -Action $task2Action -Trigger $task2Trigger -Settings $task2Settings -Principal $task2Principal -Force | Out-Null
        Write-Status "AI optimization task installed" "Success"
    }
    catch {
        Write-Status "Failed to install AI optimization task: $_" "Error"
    }

    # Task 3: Health Monitor (Every hour)
    $task3Name = "EQ12_HealthMonitor"
    $task3Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File eq12_xampp_security_simple.ps1 -Verify" -WorkingDirectory $workingDir
    $task3Trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Hours 1) -At (Get-Date) -Once
    $task3Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $task3Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Limited

    try {
        Register-ScheduledTask -TaskName $task3Name -Action $task3Action -Trigger $task3Trigger -Settings $task3Settings -Principal $task3Principal -Force | Out-Null
        Write-Status "Health monitor task installed" "Success"
    }
    catch {
        Write-Status "Failed to install health monitor task: $_" "Error"
    }

    # Task 4: Log Cleanup (Daily at 2 AM)
    $task4Name = "EQ12_LogCleanup"
    $task4Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-Command ""Get-ChildItem 'C:\EQ12\logs\*.log' | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item -Force""" -WorkingDirectory $workingDir
    $task4Trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
    $task4Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $task4Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Limited

    try {
        Register-ScheduledTask -TaskName $task4Name -Action $task4Action -Trigger $task4Trigger -Settings $task4Settings -Principal $task4Principal -Force | Out-Null
        Write-Status "Log cleanup task installed" "Success"
    }
    catch {
        Write-Status "Failed to install log cleanup task: $_" "Error"
    }

    Write-Status "All EQ12 tasks installed successfully!" "Success"
}

function Remove-Tasks {
    Write-Status "Removing EQ12 scheduled tasks..." "Warning"

    $taskNames = @("EQ12_OddsIngestion", "EQ12_AIOptimization", "EQ12_HealthMonitor", "EQ12_LogCleanup")

    foreach ($taskName in $taskNames) {
        try {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
            Write-Status "Removed task: $taskName" "Success"
        }
        catch {
            Write-Status "Failed to remove task: $taskName" "Warning"
        }
    }
}

function Show-Status {
    Write-Status "EQ12 Scheduled Tasks Status:" "Info"
    Write-Status "=" * 40 "Info"

    $taskNames = @("EQ12_OddsIngestion", "EQ12_AIOptimization", "EQ12_HealthMonitor", "EQ12_LogCleanup")

    foreach ($taskName in $taskNames) {
        try {
            $task = Get-ScheduledTask -TaskName $taskName -ErrorAction Stop
            $taskInfo = Get-ScheduledTaskInfo -TaskName $taskName

            $status = switch ($task.State) {
                "Ready" { "READY" }
                "Running" { "RUNNING" }
                "Disabled" { "DISABLED" }
                default { $task.State }
            }

            $lastRun = if ($taskInfo.LastRunTime) { $taskInfo.LastRunTime.ToString("yyyy-MM-dd HH:mm:ss") } else { "Never" }
            $nextRun = if ($taskInfo.NextRunTime) { $taskInfo.NextRunTime.ToString("yyyy-MM-dd HH:mm:ss") } else { "Not scheduled" }

            Write-Status "Task: $taskName" "Info"
            Write-Status "  Status: $status" "Success"
            Write-Status "  Last Run: $lastRun" "Info"
            Write-Status "  Next Run: $nextRun" "Info"
            Write-Status "" "Info"

        }
        catch {
            Write-Status "Task: $taskName - NOT INSTALLED" "Error"
        }
    }
}

function Run-TaskNow {
    param([string]$TaskName)

    Write-Status "Running task: $TaskName" "Info"

    try {
        Start-ScheduledTask -TaskName $TaskName
        Write-Status "Task $TaskName started successfully" "Success"

        # Wait a moment and check status
        Start-Sleep 3
        $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
        Write-Status "Task result: $($taskInfo.LastTaskResult)" "Info"

    }
    catch {
        Write-Status "Failed to run task $TaskName" "Error"
    }
}

# Main execution
switch ($true) {
    $Install {
        Install-Tasks
        Show-Status
    }

    $Remove {
        Remove-Tasks
    }

    $Status {
        Show-Status
    }

    $RunNow {
        Write-Status "Available tasks to run:" "Info"
        Write-Status "1. EQ12_OddsIngestion" "Info"
        Write-Status "2. EQ12_AIOptimization" "Info"
        Write-Status "3. EQ12_HealthMonitor" "Info"

        $choice = Read-Host "Enter task number (1-3)"

        switch ($choice) {
            "1" { Run-TaskNow "EQ12_OddsIngestion" }
            "2" { Run-TaskNow "EQ12_AIOptimization" }
            "3" { Run-TaskNow "EQ12_HealthMonitor" }
            default { Write-Status "Invalid choice" "Error" }
        }
    }

    default {
        Write-Status "EQ12 Windows Task Scheduler Manager" "Info"
        Write-Status "Usage:" "Info"
        Write-Status "  -Install   Install all EQ12 scheduled tasks" "Info"
        Write-Status "  -Remove    Remove all EQ12 scheduled tasks" "Info"
        Write-Status "  -Status    Show current task status" "Info"
        Write-Status "  -RunNow    Run a task immediately" "Info"
        Write-Status "" "Info"
        Write-Status "Example: .\eq12_task_scheduler.ps1 -Install" "Info"
    }
}
