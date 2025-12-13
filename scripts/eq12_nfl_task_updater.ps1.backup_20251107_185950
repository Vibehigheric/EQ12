[CmdletBinding()]
param(
    [int]$IntervalMinutes = 120,
    [switch]$ListTasks,
    [switch]$UpdateAll,
    [string]$TaskName
)

# EQ12 NFL Parlay Task Frequency Updater
Write-Verbose "Starting NFL parlay task frequency updates..."

function Get-NFLRelatedTasks {
    try {
        $Tasks = Get-ScheduledTask | Where-Object {
            $_.TaskName -like "*NFL*" -or 
            $_.TaskName -like "*parlay*" -or
            $_.TaskName -like "*EQ12*" -or
            $_.Actions.Execute -like "*nfl*" -or
            $_.Actions.Arguments -like "*nfl*" -or
            $_.Actions.Arguments -like "*parlay*"
        }
        
        Write-Verbose "Found $($Tasks.Count) NFL-related scheduled tasks"
        return $Tasks
    }
    catch {
        Write-Error "Error getting NFL tasks: $_"
        return @()
    }
}

function Update-TaskFrequency {
    param(
        [string]$TaskName,
        [int]$IntervalMinutes
    )
    
    try {
        Write-Verbose "Updating task: $TaskName to $IntervalMinutes minute intervals"
        
        $Task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
        $TriggerSettings = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration ([TimeSpan]::MaxValue)
        Set-ScheduledTask -TaskName $TaskName -Trigger $TriggerSettings -ErrorAction Stop
        
        Write-Host "✅ Successfully updated $TaskName to $IntervalMinutes minute intervals" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Warning "❌ Failed to update $TaskName : $_"
        return $false
    }
}

function Show-TaskFrequencies {
    $Tasks = Get-NFLRelatedTasks
    
    Write-Host "`nCURRENT NFL PARLAY TASK FREQUENCIES:" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    
    foreach ($Task in $Tasks) {
        try {
            $TaskInfo = Get-ScheduledTaskInfo -TaskName $Task.TaskName
            $Triggers = $Task.Triggers
            
            Write-Host "`nTask: " -NoNewline -ForegroundColor Yellow
            Write-Host $Task.TaskName -ForegroundColor White
            Write-Host "State: " -NoNewline -ForegroundColor Gray
            Write-Host $Task.State -ForegroundColor $(if ($Task.State -eq "Ready") { "Green" } else { "Red" })
            
            if ($Triggers) {
                foreach ($Trigger in $Triggers) {
                    if ($Trigger.Repetition -and $Trigger.Repetition.Interval) {
                        $Interval = $Trigger.Repetition.Interval
                        Write-Host "Interval: " -NoNewline -ForegroundColor Gray
                        Write-Host $Interval -ForegroundColor Cyan
                    }
                }
            }
            
            if ($TaskInfo.LastRunTime) {
                Write-Host "Last Run: " -NoNewline -ForegroundColor Gray  
                Write-Host $TaskInfo.LastRunTime -ForegroundColor White
            }
        }
        catch {
            Write-Warning "Could not get info for task: $($Task.TaskName)"
        }
    }
}

# Main execution logic
if ($ListTasks) {
    Show-TaskFrequencies
    exit 0
}

if ($TaskName) {
    # Update specific task
    $Success = Update-TaskFrequency -TaskName $TaskName -IntervalMinutes $IntervalMinutes
    if ($Success) {
        Write-Host "`n✅ Task update completed successfully" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Task update failed" -ForegroundColor Red
        exit 1
    }
}
elseif ($UpdateAll) {
    # Update all NFL-related tasks
    $Tasks = Get-NFLRelatedTasks
    $UpdatedCount = 0
    $TotalTasks = $Tasks.Count
    
    Write-Host "`n🔄 Updating $TotalTasks NFL parlay tasks to $IntervalMinutes minute intervals..." -ForegroundColor Yellow
    
    foreach ($Task in $Tasks) {
        if (Update-TaskFrequency -TaskName $Task.TaskName -IntervalMinutes $IntervalMinutes) {
            $UpdatedCount++
        }
    }
    
    Write-Host "`n📊 SUMMARY:" -ForegroundColor Cyan
    Write-Host "Total Tasks Found: $TotalTasks" -ForegroundColor White
    Write-Host "Successfully Updated: $UpdatedCount" -ForegroundColor Green
    Write-Host "Failed Updates: $($TotalTasks - $UpdatedCount)" -ForegroundColor Red
    Write-Host "New Interval: $IntervalMinutes minutes" -ForegroundColor Cyan
    
    if ($UpdatedCount -eq $TotalTasks) {
        Write-Host "`n🎉 All NFL parlay tasks updated successfully!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "`n⚠️  Some tasks failed to update" -ForegroundColor Yellow
        exit 1
    }
}
else {
    # Show help
    Write-Host "`nEQ12 NFL Parlay Task Frequency Updater" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host "`nUsage Examples:" -ForegroundColor Yellow
    Write-Host "  .\eq12_nfl_task_updater.ps1 -ListTasks" -ForegroundColor White
    Write-Host "  .\eq12_nfl_task_updater.ps1 -UpdateAll -IntervalMinutes 120" -ForegroundColor White  
    Write-Host "  .\eq12_nfl_task_updater.ps1 -TaskName 'EQ12_OddsIngestion' -IntervalMinutes 60" -ForegroundColor White
    Write-Host "`nParameters:" -ForegroundColor Yellow
    Write-Host "  -ListTasks          Show current task frequencies" -ForegroundColor Gray
    Write-Host "  -UpdateAll          Update all NFL-related tasks" -ForegroundColor Gray
    Write-Host "  -TaskName           Update specific task" -ForegroundColor Gray
    Write-Host "  -IntervalMinutes    Frequency interval (default: 120 minutes)" -ForegroundColor Gray
    Write-Host "  -Verbose            Show detailed output" -ForegroundColor Gray
}
}