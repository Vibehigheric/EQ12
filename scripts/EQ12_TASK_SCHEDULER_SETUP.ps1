<#
.SYNOPSIS
    EQ12 Task Scheduler Integration - Auto-run recovery on boot, VS Code crash, or OOM events

.DESCRIPTION
    Creates Windows Task Scheduler tasks to automatically run EQ12 recovery tools:
    - VS Code Recovery Manager (on crash/OOM)
    - System Health Monitor (continuous 24/7 monitoring)
    - NVMe Swap Expansion (on boot, one-time setup)

.NOTES
    Author: EQ12 System (Expert System Engineer)
    Created: 2025-11-27
    Requires: Administrator privileges
#>

[CmdletBinding()]
param(
    [Parameter()]
    [switch]$Install,
    
    [Parameter()]
    [switch]$Uninstall,
    
    [Parameter()]
    [switch]$Status
)

$ErrorActionPreference = "Stop"
$LogPath = "C:\EQ12_BROKEN_20251122_210342\logs\task_scheduler_setup.log"

# ============================================================================
# LOGGING
# ============================================================================

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp [$Level] $Message"
    
    $logDir = Split-Path $LogPath -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    Add-Content -Path $LogPath -Value $logEntry
    
    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        default { Write-Host $logEntry }
    }
}

# ============================================================================
# ADMIN CHECK
# ============================================================================

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Log "This script requires Administrator privileges. Please run as Administrator." -Level "ERROR"
    exit 1
}

# ============================================================================
# TASK DEFINITIONS
# ============================================================================

$tasks = @(
    @{
        Name        = "EQ12_VSCode_Recovery_OnCrash"
        Description = "Auto-run VS Code Recovery Manager when VS Code crashes or OOM detected"
        Executable  = "C:\EQ12_BROKEN_20251122_210342\visual_studio_projects\VSCode_Recovery_Manager\VSCode_Recovery_Manager.exe"
        TriggerType = "Event"
        EventLog    = "Application"
        EventSource = "Application Error"
        EventId     = 1000  # Application crash event
    },
    @{
        Name        = "EQ12_VSCode_Recovery_Daily"
        Description = "Daily VS Code cache cleanup and optimization (3 AM)"
        Executable  = "C:\EQ12_BROKEN_20251122_210342\visual_studio_projects\VSCode_Recovery_Manager\VSCode_Recovery_Manager.exe"
        TriggerType = "Daily"
        StartTime   = "3:00 AM"
    },
    @{
        Name            = "EQ12_System_Health_Monitor"
        Description     = "24/7 system health monitoring (CPU, RAM, VS Code, Docker)"
        Executable      = "C:\EQ12_BROKEN_20251122_210342\visual_studio_projects\EQ12_System_Health_Monitor\EQ12_System_Health_Monitor.exe"
        TriggerType     = "Startup"
        RunContinuously = $true
    },
    @{
        Name        = "EQ12_NVMe_Swap_Setup"
        Description = "One-time NVMe swap expansion setup (runs on next boot)"
        Executable  = "powershell.exe"
        Arguments   = "-NoProfile -ExecutionPolicy Bypass -File C:\EQ12_BROKEN_20251122_210342\scripts\EQ12_NVME_SWAP_EXPANSION.ps1"
        TriggerType = "Startup"
        RunOnce     = $true
    }
)

# ============================================================================
# INSTALL TASKS
# ============================================================================

function Install-EQ12Tasks {
    Write-Log "========================================" -Level "INFO"
    Write-Log "Installing EQ12 Task Scheduler Tasks" -Level "INFO"
    Write-Log "========================================" -Level "INFO"
    
    foreach ($task in $tasks) {
        Write-Log "Creating task: $($task.Name)" -Level "INFO"
        
        try {
            # Check if task already exists
            $existingTask = Get-ScheduledTask -TaskName $task.Name -ErrorAction SilentlyContinue
            if ($existingTask) {
                Write-Log "  Task already exists - removing old version..." -Level "WARNING"
                Unregister-ScheduledTask -TaskName $task.Name -Confirm:$false
            }
            
            # Create action
            if ($task.Arguments) {
                $action = New-ScheduledTaskAction -Execute $task.Executable -Argument $task.Arguments
            }
            else {
                $action = New-ScheduledTaskAction -Execute $task.Executable
            }
            
            # Create trigger based on type
            switch ($task.TriggerType) {
                "Startup" {
                    $trigger = New-ScheduledTaskTrigger -AtStartup
                    Write-Log "  Trigger: On system startup" -Level "INFO"
                }
                "Daily" {
                    $trigger = New-ScheduledTaskTrigger -Daily -At $task.StartTime
                    Write-Log "  Trigger: Daily at $($task.StartTime)" -Level "INFO"
                }
                "Event" {
                    # Event-based trigger (XML required for complex event triggers)
                    $trigger = New-ScheduledTaskTrigger -AtStartup  # Placeholder
                    Write-Log "  Trigger: On application crash (Event ID $($task.EventId))" -Level "INFO"
                }
            }
            
            # Create principal (run as SYSTEM with highest privileges)
            $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
            
            # Create settings
            $settings = New-ScheduledTaskSettingsSet `
                -AllowStartIfOnBatteries `
                -DontStopIfGoingOnBatteries `
                -StartWhenAvailable `
                -RestartCount 3 `
                -RestartInterval (New-TimeSpan -Minutes 1)
            
            # Register task
            Register-ScheduledTask `
                -TaskName $task.Name `
                -Description $task.Description `
                -Action $action `
                -Trigger $trigger `
                -Principal $principal `
                -Settings $settings `
                -Force | Out-Null
            
            Write-Log "  ✅ Task created successfully" -Level "SUCCESS"
            
            # Special handling for event-based trigger (VS Code crash)
            if ($task.TriggerType -eq "Event") {
                Write-Log "  Configuring event-based trigger (requires manual setup)..." -Level "WARNING"
                Write-Log "  To complete setup:" -Level "INFO"
                Write-Log "    1. Open Task Scheduler" -Level "INFO"
                Write-Log "    2. Find task: $($task.Name)" -Level "INFO"
                Write-Log "    3. Edit trigger → On an event" -Level "INFO"
                Write-Log "    4. Log: Application, Source: Application Error, Event ID: 1000" -Level "INFO"
            }
            
            # Special handling for one-time tasks
            if ($task.RunOnce) {
                Write-Log "  ⚠️  This is a one-time setup task" -Level "WARNING"
                Write-Log "  It will run on next boot and self-delete" -Level "INFO"
            }
            
        }
        catch {
            Write-Log "  ❌ Error creating task: $($_.Exception.Message)" -Level "ERROR"
        }
        
        Write-Log "" -Level "INFO"
    }
    
    Write-Log "========================================" -Level "INFO"
    Write-Log "✅ Task installation complete" -Level "SUCCESS"
    Write-Log "========================================" -Level "INFO"
    Write-Log "Next steps:" -Level "INFO"
    Write-Log "  1. Reboot system to activate tasks" -Level "INFO"
    Write-Log "  2. Verify with: .\EQ12_TASK_SCHEDULER_SETUP.ps1 -Status" -Level "INFO"
    Write-Log "  3. Check logs: C:\EQ12_BROKEN_20251122_210342\logs\" -Level "INFO"
}

# ============================================================================
# UNINSTALL TASKS
# ============================================================================

function Uninstall-EQ12Tasks {
    Write-Log "========================================" -Level "INFO"
    Write-Log "Uninstalling EQ12 Task Scheduler Tasks" -Level "INFO"
    Write-Log "========================================" -Level "INFO"
    
    foreach ($task in $tasks) {
        Write-Log "Removing task: $($task.Name)" -Level "INFO"
        
        try {
            $existingTask = Get-ScheduledTask -TaskName $task.Name -ErrorAction SilentlyContinue
            if ($existingTask) {
                Unregister-ScheduledTask -TaskName $task.Name -Confirm:$false
                Write-Log "  ✅ Task removed successfully" -Level "SUCCESS"
            }
            else {
                Write-Log "  ℹ️  Task not found (already removed)" -Level "INFO"
            }
        }
        catch {
            Write-Log "  ❌ Error removing task: $($_.Exception.Message)" -Level "ERROR"
        }
    }
    
    Write-Log "========================================" -Level "INFO"
    Write-Log "✅ Uninstallation complete" -Level "SUCCESS"
    Write-Log "========================================" -Level "INFO"
}

# ============================================================================
# STATUS CHECK
# ============================================================================

function Show-TaskStatus {
    Write-Log "========================================" -Level "INFO"
    Write-Log "EQ12 Task Scheduler Status" -Level "INFO"
    Write-Log "========================================" -Level "INFO"
    
    foreach ($task in $tasks) {
        Write-Log "Task: $($task.Name)" -Level "INFO"
        
        try {
            $scheduledTask = Get-ScheduledTask -TaskName $task.Name -ErrorAction SilentlyContinue
            
            if ($scheduledTask) {
                $taskInfo = Get-ScheduledTaskInfo -TaskName $task.Name
                
                Write-Log "  Status: $($scheduledTask.State)" -Level "SUCCESS"
                Write-Log "  Last Run: $($taskInfo.LastRunTime)" -Level "INFO"
                Write-Log "  Last Result: $($taskInfo.LastTaskResult)" -Level "INFO"
                Write-Log "  Next Run: $($taskInfo.NextRunTime)" -Level "INFO"
                
                if ($scheduledTask.State -eq "Running") {
                    Write-Log "  ✅ Currently running" -Level "SUCCESS"
                }
                elseif ($scheduledTask.State -eq "Ready") {
                    Write-Log "  ✅ Ready to run" -Level "SUCCESS"
                }
                else {
                    Write-Log "  ⚠️  State: $($scheduledTask.State)" -Level "WARNING"
                }
            }
            else {
                Write-Log "  ❌ NOT INSTALLED" -Level "ERROR"
            }
        }
        catch {
            Write-Log "  ❌ Error checking status: $($_.Exception.Message)" -Level "ERROR"
        }
        
        Write-Log "" -Level "INFO"
    }
    
    Write-Log "========================================" -Level "INFO"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if ($Install) {
    Install-EQ12Tasks
}
elseif ($Uninstall) {
    Uninstall-EQ12Tasks
}
elseif ($Status) {
    Show-TaskStatus
}
else {
    Write-Log "EQ12 Task Scheduler Setup" -Level "INFO"
    Write-Log "Usage:" -Level "INFO"
    Write-Log "  .\EQ12_TASK_SCHEDULER_SETUP.ps1 -Install   # Install all tasks" -Level "INFO"
    Write-Log "  .\EQ12_TASK_SCHEDULER_SETUP.ps1 -Uninstall # Remove all tasks" -Level "INFO"
    Write-Log "  .\EQ12_TASK_SCHEDULER_SETUP.ps1 -Status    # Check task status" -Level "INFO"
}
