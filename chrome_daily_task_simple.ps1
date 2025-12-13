#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Simple Chrome Daily Task Scheduler Manager for EQ12 GODSTACK

.DESCRIPTION
    Simplified script to manage Windows Task Scheduler for Chrome governance daily automation

.PARAMETER Action
    Action to perform: Install, Remove, Status, Run

.EXAMPLE
    .\chrome_daily_task_simple.ps1 -Action Install
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("Install", "Remove", "Status", "Run")]
    [string]$Action = "Install"
)

$TaskName = "EQ12ChromeGovernanceDailyRefresh"
$EQ12Root = "C:\EQ12"
$XmlFilePath = "$EQ12Root\tasks\ChromeGovernanceDailyRefresh.xml"

function Write-Status {
    param(
        [string]$Message,
        [string]$Level = "Info"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $colors = @{
        "Info" = "White"
        "Success" = "Green"
        "Warning" = "Yellow"
        "Error" = "Red"
    }

    Write-Host "[$timestamp] $Message" -ForegroundColor $colors[$Level]
}

Write-Status "EQ12 Chrome Daily Task Manager - Action: $Action" "Info"

switch ($Action) {
    "Install" {
        Write-Status "Installing Chrome governance daily task..." "Info"

        try {
            if (!(Test-Path $XmlFilePath)) {
                Write-Status "ERROR: Task XML file not found: $XmlFilePath" "Error"
                exit 1
            }

            # Remove existing task if present
            $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            if ($existingTask) {
                Write-Status "Removing existing task..." "Warning"
                Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            }

            # Import task from XML
            $xmlContent = Get-Content $XmlFilePath -Raw
            Register-ScheduledTask -Xml $xmlContent -TaskName $TaskName

            Write-Status "SUCCESS: Chrome governance daily task installed" "Success"
            Write-Status "Task will run daily at 9:00 AM" "Info"

        } catch {
            Write-Status "ERROR: Failed to install task - $($_.Exception.Message)" "Error"
            exit 1
        }
    }

    "Remove" {
        Write-Status "Removing Chrome governance daily task..." "Info"

        try {
            $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            if ($task) {
                Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
                Write-Status "SUCCESS: Task removed successfully" "Success"
            } else {
                Write-Status "Task not found - nothing to remove" "Warning"
            }
        } catch {
            Write-Status "ERROR: Failed to remove task - $($_.Exception.Message)" "Error"
            exit 1
        }
    }

    "Status" {
        Write-Status "Checking Chrome governance task status..." "Info"

        try {
            $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            if ($task) {
                $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
                Write-Status "Task Status: $($task.State)" "Success"
                Write-Status "Last Run Time: $($taskInfo.LastRunTime)" "Info"
                Write-Status "Last Result: $($taskInfo.LastTaskResult)" "Info"
                Write-Status "Next Run Time: $($taskInfo.NextRunTime)" "Info"
            } else {
                Write-Status "Task not found" "Warning"
            }
        } catch {
            Write-Status "ERROR: Failed to get task status - $($_.Exception.Message)" "Error"
            exit 1
        }
    }

    "Run" {
        Write-Status "Running Chrome governance task now..." "Info"

        try {
            $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            if ($task) {
                Start-ScheduledTask -TaskName $TaskName
                Start-Sleep -Seconds 3

                $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
                if ($taskInfo.LastTaskResult -eq 0) {
                    Write-Status "SUCCESS: Task executed successfully" "Success"
                } else {
                    Write-Status "Task execution completed with code: $($taskInfo.LastTaskResult)" "Warning"
                }
            } else {
                Write-Status "ERROR: Task not found - install it first" "Error"
                exit 1
            }
        } catch {
            Write-Status "ERROR: Failed to run task - $($_.Exception.Message)" "Error"
            exit 1
        }
    }
}

Write-Status "Chrome daily task management completed" "Info"
