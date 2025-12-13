# EQ12 VPN Guard - Task Scheduler Setup Script
# Configures Windows Task Scheduler for automated VPN connection and betting pipeline management

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$TaskName = "EQ12_VPN_Guard",

    [Parameter(Mandatory = $false)]
    [string]$TaskXmlPath = "C:\EQ12\configs\EQ12_VPN_Guard_Task.xml",

    [Parameter(Mandatory = $false)]
    [string]$VpnConfig = "eq12-betting",

    [Parameter(Mandatory = $false)]
    [switch]$Force,

    [Parameter(Mandatory = $false)]
    [switch]$Remove,

    [Parameter(Mandatory = $false)]
    [switch]$Test
)

# Import required modules
Import-Module ScheduledTasks -ErrorAction SilentlyContinue

function Write-StatusMessage {
    param([string]$Message, [string]$Type = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    switch ($Type) {
        "INFO" { Write-Host "[$timestamp] [INFO]  $Message" -ForegroundColor Green }
        "WARN" { Write-Host "[$timestamp] [WARN]  $Message" -ForegroundColor Yellow }
        "ERROR" { Write-Host "[$timestamp] [ERROR] $Message" -ForegroundColor Red }
        "SUCCESS" { Write-Host "[$timestamp] [OK]    $Message" -ForegroundColor Cyan }
    }
}

function Test-Prerequisites {
    Write-StatusMessage "Checking prerequisites..."

    # Check if running as Administrator
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) {
        Write-StatusMessage "This script requires Administrator privileges" -Type "ERROR"
        return $false
    }

    # Check if WireGuard is installed
    $wgPath = "${env:ProgramFiles}\WireGuard\wireguard.exe"
    if (-not (Test-Path $wgPath)) {
        Write-StatusMessage "WireGuard not found at $wgPath" -Type "ERROR"
        Write-StatusMessage "Please install WireGuard from: https://www.wireguard.com/install/" -Type "INFO"
        return $false
    }

    # Check if VPN config exists
    $configPath = "C:\EQ12\wireguard\$VpnConfig.conf"
    if (-not (Test-Path $configPath)) {
        Write-StatusMessage "VPN config not found: $configPath" -Type "WARN"
        Write-StatusMessage "Please create VPN configuration file before proceeding" -Type "INFO"
    }

    # Check if EQ12 directories exist
    $requiredDirs = @("C:\EQ12", "C:\EQ12\logs", "C:\EQ12\configs")
    foreach ($dir in $requiredDirs) {
        if (-not (Test-Path $dir)) {
            Write-StatusMessage "Creating directory: $dir"
            New-Item -Path $dir -ItemType Directory -Force | Out-Null
        }
    }

    # Check if PowerShell script exists
    $vpnGuardScript = "C:\EQ12\eq12_vpn_guard.ps1"
    if (-not (Test-Path $vpnGuardScript)) {
        Write-StatusMessage "VPN Guard script not found: $vpnGuardScript" -Type "ERROR"
        return $false
    }

    Write-StatusMessage "Prerequisites check completed" -Type "SUCCESS"
    return $true
}

function Remove-EQ12Task {
    Write-StatusMessage "Removing existing EQ12 VPN Guard task..."

    try {
        $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($existingTask) {
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            Write-StatusMessage "Existing task removed successfully" -Type "SUCCESS"
        } else {
            Write-StatusMessage "No existing task found to remove" -Type "INFO"
        }
        return $true
    } catch {
        Write-StatusMessage "Failed to remove existing task: $_" -Type "ERROR"
        return $false
    }
}

function Install-EQ12Task {
    Write-StatusMessage "Installing EQ12 VPN Guard scheduled task..."

    try {
        # Check if task XML exists
        if (-not (Test-Path $TaskXmlPath)) {
            Write-StatusMessage "Task XML not found: $TaskXmlPath" -Type "ERROR"
            return $false
        }

        # Remove existing task if it exists
        $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($existingTask) {
            if ($Force) {
                Write-StatusMessage "Removing existing task (Force mode)"
                Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            } else {
                Write-StatusMessage "Task already exists. Use -Force to replace it." -Type "WARN"
                return $false
            }
        }

        # Register the new task
        Register-ScheduledTask -Xml (Get-Content $TaskXmlPath | Out-String) -TaskName $TaskName
        Write-StatusMessage "Task registered successfully" -Type "SUCCESS"

        # Verify task was created
        $newTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($newTask) {
            Write-StatusMessage "Task verification: OK" -Type "SUCCESS"
            Write-StatusMessage "Task State: $($newTask.State)"
            Write-StatusMessage "Next Run Time: $($newTask.NextRunTime)"
            return $true
        } else {
            Write-StatusMessage "Task verification failed" -Type "ERROR"
            return $false
        }
    } catch {
        Write-StatusMessage "Failed to install task: $_" -Type "ERROR"
        return $false
    }
}

function Test-EQ12Task {
    Write-StatusMessage "Testing EQ12 VPN Guard task..."

    try {
        # Check if task exists
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if (-not $task) {
            Write-StatusMessage "Task not found: $TaskName" -Type "ERROR"
            return $false
        }

        Write-StatusMessage "Task found: $TaskName"
        Write-StatusMessage "Task State: $($task.State)"
        Write-StatusMessage "Last Run Time: $($task.LastRunTime)"
        Write-StatusMessage "Last Task Result: $($task.LastTaskResult)"
        Write-StatusMessage "Next Run Time: $($task.NextRunTime)"

        # Test run the task
        Write-StatusMessage "Starting test run..."
        Start-ScheduledTask -TaskName $TaskName

        Start-Sleep -Seconds 5

        # Check if task is running
        $taskInfo = Get-ScheduledTask -TaskName $TaskName
        Write-StatusMessage "Task State after start: $($taskInfo.State)"

        # Check for log output
        $logFile = "C:\EQ12\logs\vpn_guard.log"
        if (Test-Path $logFile) {
            Write-StatusMessage "Log file found: $logFile"
            $recentLogs = Get-Content $logFile -Tail 5
            Write-StatusMessage "Recent log entries:"
            foreach ($log in $recentLogs) {
                Write-Host "  $log" -ForegroundColor Gray
            }
        }

        return $true
    } catch {
        Write-StatusMessage "Task test failed: $_" -Type "ERROR"
        return $false
    }
}

function Show-TaskStatus {
    Write-StatusMessage "EQ12 VPN Guard Task Status Report"
    Write-Host "=" * 60

    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Write-Host "Task Name:        $($task.TaskName)" -ForegroundColor Cyan
            Write-Host "State:            $($task.State)" -ForegroundColor Cyan
            Write-Host "Last Run:         $($task.LastRunTime)" -ForegroundColor Cyan
            Write-Host "Last Result:      $($task.LastTaskResult)" -ForegroundColor Cyan
            Write-Host "Next Run:         $($task.NextRunTime)" -ForegroundColor Cyan
            Write-Host "Author:           $($task.Author)" -ForegroundColor Cyan
            Write-Host "Description:      $($task.Description)" -ForegroundColor Cyan

            # Show triggers
            $triggers = Get-ScheduledTask -TaskName $TaskName | Select-Object -ExpandProperty Triggers
            Write-Host "`nTriggers:" -ForegroundColor Yellow
            foreach ($trigger in $triggers) {
                Write-Host "  - $($trigger.GetType().Name): $trigger" -ForegroundColor Gray
            }

            # Show actions
            $actions = Get-ScheduledTask -TaskName $TaskName | Select-Object -ExpandProperty Actions
            Write-Host "`nActions:" -ForegroundColor Yellow
            foreach ($action in $actions) {
                Write-Host "  - Execute: $($action.Execute)" -ForegroundColor Gray
                Write-Host "    Arguments: $($action.Arguments)" -ForegroundColor Gray
            }
        } else {
            Write-Host "Task not found: $TaskName" -ForegroundColor Red
        }
    } catch {
        Write-StatusMessage "Failed to get task status: $_" -Type "ERROR"
    }
}

# Main execution
function Main {
    Write-StatusMessage "EQ12 VPN Guard - Task Scheduler Setup"
    Write-Host "=" * 60

    if ($Remove) {
        if (Remove-EQ12Task) {
            Write-StatusMessage "Task removal completed successfully" -Type "SUCCESS"
        }
        return
    }

    if ($Test) {
        Test-EQ12Task
        Show-TaskStatus
        return
    }

    # Normal installation process
    if (-not (Test-Prerequisites)) {
        Write-StatusMessage "Prerequisites check failed - aborting" -Type "ERROR"
        exit 1
    }

    if (Install-EQ12Task) {
        Write-StatusMessage "EQ12 VPN Guard task installed successfully!" -Type "SUCCESS"
        Write-StatusMessage "The task will automatically start VPN and betting pipeline at system boot" -Type "INFO"
        Write-StatusMessage "Use 'Get-ScheduledTask -TaskName $TaskName' to monitor the task" -Type "INFO"

        # Show final status
        Show-TaskStatus
    } else {
        Write-StatusMessage "Task installation failed" -Type "ERROR"
        exit 1
    }
}

# Execute main function
Main
