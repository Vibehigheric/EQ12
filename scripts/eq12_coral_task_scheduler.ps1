[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

# EQ12 Coral Edge TPU Sports Betting AI - Windows Task Scheduler Setup
# Run this script as Administrator to create automated tasks

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Status,
    [string]$WorkspacePath = "C:\EQ12"
)

$TaskPrefix = "EQ12-Coral-"
$ScriptPath = Join-Path $WorkspacePath "scripts\eq12_coral_automation_wrapper.ps1"

$Tasks = @(
    @{
        Name = "$($TaskPrefix)LiveOddsCollector"
        Description = "Collects live sports betting odds every 30 seconds"
        Action = "CollectOdds"
        Schedule = "RepeatEvery30Seconds"
        Enabled = $true
    },
    @{
        Name = "$($TaskPrefix)CoralInference"
        Description = "Runs Coral Edge TPU inference every minute"
        Action = "RunInference"
        Schedule = "RepeatEveryMinute"
        Enabled = $true
    },
    @{
        Name = "$($TaskPrefix)ParlayOptimizer"
        Description = "Optimizes parlays every 5 minutes"
        Action = "OptimizeParlays"
        Schedule = "RepeatEvery5Minutes"
        Enabled = $true
    },
    @{
        Name = "$($TaskPrefix)AlertSystem"
        Description = "Checks and sends alerts every 2 minutes"
        Action = "SendAlerts"
        Schedule = "RepeatEvery2Minutes"
        Enabled = $true
    },
    @{
        Name = "$($TaskPrefix)DailyReporter"
        Description = "Generates daily reports at midnight"
        Action = "GenerateReports"
        Schedule = "DailyMidnight"
        Enabled = $true
    },
    @{
        Name = "$($TaskPrefix)FullPipeline"
        Description = "Runs complete pipeline every 10 minutes"
        Action = "FullPipeline"
        Schedule = "RepeatEvery10Minutes"
        Enabled = $false
    }
)

function Install-CoralTasks {
    Write-Host "Installing EQ12 Coral AI automation tasks..." -ForegroundColor Green
    
    foreach ($Task in $Tasks) {
        try {
            # Check if task already exists
            $ExistingTask = Get-ScheduledTask -TaskName $Task.Name -ErrorAction SilentlyContinue
            
            if ($ExistingTask) {
                Write-Host "Task $($Task.Name) already exists, updating..." -ForegroundColor Yellow
                Unregister-ScheduledTask -TaskName $Task.Name -Confirm:$false
            }
            
            # Create task action
            $TaskAction = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`" -Action $($Task.Action) -Workspace `"$WorkspacePath`" -Verbose"
            
            # Create task trigger based on schedule
            switch ($Task.Schedule) {
                "RepeatEvery30Seconds" {
                    $TaskTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Seconds 30) -RepetitionDuration (New-TimeSpan -Days 365)
                }
                "RepeatEveryMinute" {
                    $TaskTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration (New-TimeSpan -Days 365)
                }
                "RepeatEvery2Minutes" {
                    $TaskTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 2) -RepetitionDuration (New-TimeSpan -Days 365)
                }
                "RepeatEvery5Minutes" {
                    $TaskTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)
                }
                "RepeatEvery10Minutes" {
                    $TaskTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 10) -RepetitionDuration (New-TimeSpan -Days 365)
                }
                "DailyMidnight" {
                    $TaskTrigger = New-ScheduledTaskTrigger -Daily -At "00:00"
                }
                default {
                    $TaskTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1)
                }
            }
            
            # Create task settings
            $TaskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
            
            # Create task principal (run as current user)
            $TaskPrincipal = New-ScheduledTaskPrincipal -UserId ${env}USERNAME -LogonType Interactive -RunLevel Highest
            
            # Register the task
            $TaskDefinition = New-ScheduledTask -Action $TaskAction -Trigger $TaskTrigger -Settings $TaskSettings -Principal $TaskPrincipal -Description $Task.Description
            
            Register-ScheduledTask -TaskName $Task.Name -InputObject $TaskDefinition
            
            # Enable/disable based on configuration
            if ($Task.Enabled) {
                Enable-ScheduledTask -TaskName $Task.Name
                Write-Host " Created and enabled task: $($Task.Name)" -ForegroundColor Green
            } else {
                Disable-ScheduledTask -TaskName $Task.Name
                Write-Host " Created but disabled task: $($Task.Name)" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host " Failed to create task $($Task.Name): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Write-Host "`nEQ12 Coral AI automation tasks installed successfully!" -ForegroundColor Green
    Write-Host "Use "Get-ScheduledTask -TaskName `"$TaskPrefix*`"' to view all tasks" -ForegroundColor Cyan
}

function Uninstall-CoralTasks {
    Write-Host "Uninstalling EQ12 Coral AI automation tasks..." -ForegroundColor Yellow
    
    foreach ($Task in $Tasks) {
        try {
            $ExistingTask = Get-ScheduledTask -TaskName $Task.Name -ErrorAction SilentlyContinue
            
            if ($ExistingTask) {
                Unregister-ScheduledTask -TaskName $Task.Name -Confirm:$false
                Write-Host " Removed task: $($Task.Name)" -ForegroundColor Green
            } else {
                Write-Host "- Task not found: $($Task.Name)" -ForegroundColor Gray
            }
        }
        catch {
            Write-Host " Failed to remove task $($Task.Name): $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Write-Host "`nEQ12 Coral AI automation tasks uninstalled!" -ForegroundColor Green
}

function Show-TaskStatus {
    Write-Host "EQ12 Coral AI Automation Tasks Status" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    
    foreach ($Task in $Tasks) {
        try {
            $ExistingTask = Get-ScheduledTask -TaskName $Task.Name -ErrorAction SilentlyContinue
            
            if ($ExistingTask) {
                $Status = $ExistingTask.State
                $LastRun = (Get-ScheduledTaskInfo -TaskName $Task.Name).LastRunTime
                $NextRun = (Get-ScheduledTaskInfo -TaskName $Task.Name).NextRunTime
                
                $StatusColor = switch ($Status) {
                    "Ready" { "Green" }
                    "Running" { "Yellow" }
                    "Disabled" { "Gray" }
                    default { "Red" }
                }
                
                Write-Host ""
                Write-Host "Task: $($Task.Name)" -ForegroundColor White
                Write-Host "  Status: $Status" -ForegroundColor $StatusColor
                Write-Host "  Description: $($Task.Description)" -ForegroundColor Gray
                Write-Host "  Last Run: $LastRun" -ForegroundColor Gray
                Write-Host "  Next Run: $NextRun" -ForegroundColor Gray
            } else {
                Write-Host ""
                Write-Host "Task: $($Task.Name)" -ForegroundColor White
                Write-Host "  Status: Not Installed" -ForegroundColor Red
            }
        }
        catch {
            Write-Host ""
            Write-Host "Task: $($Task.Name)" -ForegroundColor White
            Write-Host "  Status: Error - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Write-Host ""
}

# Main execution
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires Administrator privileges. Please run as Administrator." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $ScriptPath)) {
    Write-Host "Coral automation script not found: $ScriptPath" -ForegroundColor Red
    Write-Host "Please ensure the EQ12 workspace is properly set up." -ForegroundColor Yellow
    exit 1
}

switch ($true) {
    $Install {
        Install-CoralTasks
    }
    $Uninstall {
        Uninstall-CoralTasks
    }
    $Status {
        Show-TaskStatus
    }
    default {
        Write-Host "EQ12 Coral Edge TPU Sports Betting AI - Task Scheduler Setup" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Usage:" -ForegroundColor Yellow
        Write-Host "  -Install    Install all automation tasks" -ForegroundColor White
        Write-Host "  -Uninstall  Remove all automation tasks" -ForegroundColor White
        Write-Host "  -Status     Show current task status" -ForegroundColor White
        Write-Host ""
        Write-Host "Example: .\eq12_coral_task_scheduler.ps1 -Install" -ForegroundColor Green
        Write-Host ""
        
        Show-TaskStatus
    }
}
