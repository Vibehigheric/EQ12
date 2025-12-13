#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    EQ12 GODSTACK - Chrome Governance Task Scheduler Management

.DESCRIPTION
    Manages Windows Task Scheduler tasks for Chrome governance automation.
    Provides installation, removal, status checking, and execution of scheduled tasks.

.PARAMETER Action
    The action to perform: Install, InstallXML, Remove, Status, Run, or Test

.PARAMETER TaskName
    Name of the scheduled task (default: EQ12ChromeGovernanceDailyUpdate)

.PARAMETER Schedule
    Schedule for the task: Daily, Weekly, or OnStartup (default: Daily)

.PARAMETER Time
    Time to run daily task in HH:MM format (default: 07:00)

.EXAMPLE
    .\manage_chrome_task.ps1 -Action Install

.EXAMPLE
    .\manage_chrome_task.ps1 -Action Status -Verbose

.EXAMPLE
    .\manage_chrome_task.ps1 -Action Run -TaskName "EQ12ChromeGovernanceDailyUpdate"

.NOTES
    Author: EQ12 GODSTACK Team
    Version: 1.0.0
    Requires: Administrator privileges, Windows Task Scheduler
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("Install", "InstallXML", "Remove", "Status", "Run", "Test")]
    [string]$Action = "Install",

    [Parameter(Mandatory = $false)]
    [string]$TaskName = "EQ12ChromeGovernanceDailyUpdate",

    [Parameter(Mandatory = $false)]
    [ValidateSet("Daily", "Weekly", "OnStartup")]
    [string]$Schedule = "Daily",

    [Parameter(Mandatory = $false)]
    [string]$Time = "07:00"
)

# Configuration
$EQ12Root = "C:\EQ12"
$PythonExecutable = "C:\Program Files\Python312\python.exe"
$ChromeScript = "$EQ12Root\chrome_governance_automation.py"
$TaskXmlFile = "$EQ12Root\chrome_governance_daily_task.xml"
$LogsDir = "$EQ12Root\logs"

# Ensure logs directory exists
if (!(Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}

# Setup logging
$LogFile = "$LogsDir\chrome_task_management_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
Start-Transcript -Path $LogFile -Append

function Write-EQ12Log {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $false)]
        [ValidateSet("Info", "Warning", "Error", "Success")]
        [string]$Level = "Info"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $colorMap = @{
        "Info"    = "White"
        "Warning" = "Yellow"
        "Error"   = "Red"
        "Success" = "Green"
    }

    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry -ForegroundColor $colorMap[$Level]

    # Also log to file
    Add-Content -Path $LogFile -Value $logEntry
}

function Test-Prerequisites {
    Write-EQ12Log "🔍 Checking prerequisites..." -Level "Info"

    $issues = @()

    # Check if running as administrator
    if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        $issues += "❌ Must run as Administrator"
    }

    # Check Python executable
    if (!(Test-Path $PythonExecutable)) {
        $issues += "❌ Python not found at: $PythonExecutable"
    }

    # Check Chrome automation script
    if (!(Test-Path $ChromeScript)) {
        $issues += "❌ Chrome script not found at: $ChromeScript"
    }

    # Check EQ12 root directory
    if (!(Test-Path $EQ12Root)) {
        $issues += "❌ EQ12 root directory not found: $EQ12Root"
    }

    if ($issues.Count -gt 0) {
        Write-EQ12Log "❌ Prerequisites check failed:" -Level "Error"
        $issues | ForEach-Object { Write-EQ12Log "   $_" -Level "Error" }
        return $false
    }

    Write-EQ12Log "✅ All prerequisites met" -Level "Success"
    return $true
}

function Install-ChromeGovernanceTaskFromXML {
    param(
        [Parameter(Mandatory = $true)]
        [string]$XmlFilePath,

        [Parameter(Mandatory = $true)]
        [string]$TaskName
    )

    Write-EQ12Log "🚀 Installing Chrome governance task from XML: $XmlFilePath" -Level "Info"

    try {
        if (!(Test-Path $XmlFilePath)) {
            Write-EQ12Log "❌ XML file not found: $XmlFilePath" -Level "Error"
            return $false
        }

        # Check if task already exists
        $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($existingTask) {
            Write-EQ12Log "⚠️ Task '$TaskName' already exists. Removing first..." -Level "Warning"
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        }

        # Import task from XML
        Register-ScheduledTask -Xml (Get-Content $XmlFilePath -Raw) -TaskName $TaskName

        Write-EQ12Log "✅ Successfully installed scheduled task from XML: $TaskName" -Level "Success"
        return $true

    } catch {
        Write-EQ12Log "❌ Failed to install task from XML: $($_.Exception.Message)" -Level "Error"
        return $false
    }
}

function Install-ChromeGovernanceTask {
    Write-EQ12Log "🚀 Installing Chrome governance scheduled task..." -Level "Info"

    try {
        # Check if task already exists
        $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($existingTask) {
            Write-EQ12Log "⚠️ Task '$TaskName' already exists. Removing first..." -Level "Warning"
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        }

        # Create task action with daily refresh support
        if ($TaskName -eq "EQ12ChromeGovernanceDailyRefresh" -or $TaskName -eq "EQ12ChromeGovernanceDailyUpdate") {
            # Daily refresh mode with updated bookmarks and timestamps
            $action = New-ScheduledTaskAction -Execute $PythonExecutable -Argument "$ChromeScript --refresh-daily --launch-browser --verbose" -WorkingDirectory $EQ12Root
            Write-EQ12Log "📝 Configured for daily refresh mode with updated bookmarks" -Level "Info"
        } else {
            # Standard setup mode
            $action = New-ScheduledTaskAction -Execute $PythonExecutable -Argument "$ChromeScript --setup-profile --create-bookmarks --verbose" -WorkingDirectory $EQ12Root
            Write-EQ12Log "📝 Configured for standard profile setup mode" -Level "Info"
        }

        # Create task trigger based on schedule
        if ($Schedule -eq "Daily") {
            $trigger = New-ScheduledTaskTrigger -Daily -At $Time
            Write-EQ12Log "📅 Scheduled for daily execution at $Time" -Level "Info"
        } elseif ($Schedule -eq "Weekly") {
            $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At $Time
            Write-EQ12Log "📅 Scheduled for weekly execution (Mondays) at $Time" -Level "Info"
        } elseif ($Schedule -eq "OnStartup") {
            $trigger = New-ScheduledTaskTrigger -AtStartup
            Write-EQ12Log "📅 Scheduled for system startup execution" -Level "Info"
        }

        # Create task settings
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

        # Create task principal (run with highest privileges)
        $principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

        # Register the scheduled task
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "EQ12 Chrome Governance - Daily automation for profile management, bookmark updates, and extension compliance"

        Write-EQ12Log "✅ Successfully installed scheduled task: $TaskName" -Level "Success"

        # Test the task
        Write-EQ12Log "🧪 Testing task execution..." -Level "Info"
        Start-ScheduledTask -TaskName $TaskName

        # Wait a moment and check status
        Start-Sleep -Seconds 5
        $taskInfo = Get-ScheduledTask -TaskName $TaskName
        $lastResult = (Get-ScheduledTaskInfo -TaskName $TaskName).LastTaskResult

        if ($lastResult -eq 0) {
            Write-EQ12Log "✅ Task test execution successful" -Level "Success"
        } else {
            Write-EQ12Log "⚠️ Task test execution returned code: $lastResult" -Level "Warning"
        }

        return $true

    } catch {
        Write-EQ12Log "❌ Failed to install scheduled task: $($_.Exception.Message)" -Level "Error"
        return $false
    }
}

function Remove-ChromeGovernanceTask {
    Write-EQ12Log "🗑️ Removing Chrome governance scheduled task..." -Level "Info"

    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            Write-EQ12Log "✅ Successfully removed scheduled task: $TaskName" -Level "Success"
            return $true
        } else {
            Write-EQ12Log "⚠️ Task '$TaskName' not found" -Level "Warning"
            return $false
        }
    } catch {
        Write-EQ12Log "❌ Failed to remove scheduled task: $($_.Exception.Message)" -Level "Error"
        return $false
    }
}

function Get-ChromeGovernanceTaskStatus {
    Write-EQ12Log "📊 Checking Chrome governance task status..." -Level "Info"

    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName

            Write-EQ12Log "✅ Task Status Information:" -Level "Success"
            Write-EQ12Log "   Task Name: $($task.TaskName)" -Level "Info"
            Write-EQ12Log "   State: $($task.State)" -Level "Info"
            Write-EQ12Log "   Last Run Time: $($taskInfo.LastRunTime)" -Level "Info"
            Write-EQ12Log "   Next Run Time: $($taskInfo.NextRunTime)" -Level "Info"
            Write-EQ12Log "   Last Result: $($taskInfo.LastTaskResult)" -Level "Info"
            Write-EQ12Log "   Number of Missed Runs: $($taskInfo.NumberOfMissedRuns)" -Level "Info"

            # Show triggers
            Write-EQ12Log "📅 Task Triggers:" -Level "Info"
            $task.Triggers | ForEach-Object {
                Write-EQ12Log "   Type: $($_.CimClass.CimClassName)" -Level "Info"
                if ($_.StartBoundary) {
                    Write-EQ12Log "   Start Time: $($_.StartBoundary)" -Level "Info"
                }
                Write-EQ12Log "   Enabled: $($_.Enabled)" -Level "Info"
            }

            # Show actions
            Write-EQ12Log "⚙️ Task Actions:" -Level "Info"
            $task.Actions | ForEach-Object {
                Write-EQ12Log "   Execute: $($_.Execute)" -Level "Info"
                Write-EQ12Log "   Arguments: $($_.Arguments)" -Level "Info"
                Write-EQ12Log "   Working Directory: $($_.WorkingDirectory)" -Level "Info"
            }

            return $true
        } else {
            Write-EQ12Log "❌ Task '$TaskName' not found" -Level "Error"
            return $false
        }
    } catch {
        Write-EQ12Log "❌ Failed to get task status: $($_.Exception.Message)" -Level "Error"
        return $false
    }
}

function Start-ChromeGovernanceTask {
    Write-EQ12Log "▶️ Running Chrome governance task..." -Level "Info"

    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Start-ScheduledTask -TaskName $TaskName
            Write-EQ12Log "✅ Task started successfully" -Level "Success"

            # Monitor execution for a short time
            Write-EQ12Log "⏱️ Monitoring task execution..." -Level "Info"
            for ($i = 1; $i -le 10; $i++) {
                Start-Sleep -Seconds 3
                $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
                $state = (Get-ScheduledTask -TaskName $TaskName).State

                Write-EQ12Log "   Status check $i/10: $state" -Level "Info"

                if ($state -eq "Ready") {
                    $lastResult = $taskInfo.LastTaskResult
                    if ($lastResult -eq 0) {
                        Write-EQ12Log "✅ Task completed successfully" -Level "Success"
                    } else {
                        Write-EQ12Log "⚠️ Task completed with exit code: $lastResult" -Level "Warning"
                    }
                    break
                }
            }

            return $true
        } else {
            Write-EQ12Log "❌ Task '$TaskName' not found" -Level "Error"
            return $false
        }
    } catch {
        Write-EQ12Log "❌ Failed to run task: $($_.Exception.Message)" -Level "Error"
        return $false
    }
}

function Test-ChromeGovernanceTask {
    Write-EQ12Log "🧪 Testing Chrome governance automation..." -Level "Info"

    try {
        # Test Python script directly
        Write-EQ12Log "🐍 Testing Python script execution..." -Level "Info"
        $result = & $PythonExecutable $ChromeScript --validate-profile --verbose
        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            Write-EQ12Log "✅ Python script test successful" -Level "Success"
        } else {
            Write-EQ12Log "❌ Python script test failed with exit code: $exitCode" -Level "Error"
        }

        # Check Chrome executable
        $chromeExe = "C:\Program Files\Google\Chrome\Application\chrome.exe"
        if (Test-Path $chromeExe) {
            Write-EQ12Log "✅ Chrome executable found" -Level "Success"
        } else {
            Write-EQ12Log "⚠️ Chrome executable not found at: $chromeExe" -Level "Warning"
        }

        # Test network connectivity
        Write-EQ12Log "🌐 Testing network connectivity..." -Level "Info"
        $testUrls = @("github.com", "google.com", "localhost")
        foreach ($url in $testUrls) {
            try {
                $response = Test-NetConnection -ComputerName $url -Port 80 -InformationLevel Quiet -WarningAction SilentlyContinue
                if ($response) {
                    Write-EQ12Log "Network connectivity to $url OK" -Level "Success"
                } else {
                    Write-EQ12Log "Network connectivity to $url Failed" -Level "Warning"
                }
            } catch {
                Write-EQ12Log "Network test to $url failed: $($_.Exception.Message)" -Level "Warning"
            }
        }

        return ($exitCode -eq 0)

    } catch {
        Write-EQ12Log "❌ Test failed: $($_.Exception.Message)" -Level "Error"
        return $false
    }
}

# Main execution
Write-EQ12Log "🚀 EQ12 Chrome Governance Task Management" -Level "Info"
Write-EQ12Log "Action: $Action | Task: $TaskName | Schedule: $Schedule" -Level "Info"

# Check prerequisites
if (!(Test-Prerequisites)) {
    Write-EQ12Log "❌ Prerequisites check failed. Exiting." -Level "Error"
    Stop-Transcript
    exit 1
}

# Execute requested action
$success = $false

if ($Action -eq "Install") {
    $success = Install-ChromeGovernanceTask
} elseif ($Action -eq "InstallXML") {
    $XmlTaskFile = "$EQ12Root\tasks\ChromeGovernanceDailyRefresh.xml"
    $success = Install-ChromeGovernanceTaskFromXML -XmlFilePath $XmlTaskFile -TaskName "EQ12ChromeGovernanceDailyRefresh"
} elseif ($Action -eq "Remove") {
    $success = Remove-ChromeGovernanceTask
} elseif ($Action -eq "Status") {
    $success = Get-ChromeGovernanceTaskStatus
} elseif ($Action -eq "Run") {
    $success = Start-ChromeGovernanceTask
} elseif ($Action -eq "Test") {
    $success = Test-ChromeGovernanceTask
}

# Final status
if ($success) {
    Write-EQ12Log "🎉 Chrome governance task management completed successfully!" -Level "Success"
    Write-EQ12Log "📊 Log file: $LogFile" -Level "Info"
} else {
    Write-EQ12Log "❌ Chrome governance task management encountered issues." -Level "Error"
    Write-EQ12Log "📊 Check log file for details: $LogFile" -Level "Info"
}

Stop-Transcript

if ($success) {
    exit 0
} else {
    exit 1
}
