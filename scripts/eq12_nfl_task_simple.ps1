# EQ12 NFL Parlay Task Frequency Optimizer - Simple Version
param(
    [int]$IntervalMinutes = 120,
    [switch]$UpdateAll
)

Write-Host "EQ12 NFL Parlay Task Frequency Optimizer" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# Find NFL-related tasks
Write-Host "`nSearching for NFL/parlay related scheduled tasks..." -ForegroundColor Yellow

try {
    $Tasks = Get-ScheduledTask | Where-Object {
        $_.TaskName -like "*NFL*" -or 
        $_.TaskName -like "*parlay*" -or
        $_.TaskName -like "*EQ12*" -or
        $_.TaskName -like "*odds*"
    }
    
    Write-Host "Found $($Tasks.Count) NFL-related scheduled tasks" -ForegroundColor Green
    
    # List current tasks
    Write-Host "`nCurrent NFL/Parlay Tasks:" -ForegroundColor Cyan
    foreach ($Task in $Tasks) {
        Write-Host "  - $($Task.TaskName)" -ForegroundColor White
        Write-Host "    State: $($Task.State)" -ForegroundColor Gray
        
        if ($Task.Triggers) {
            foreach ($Trigger in $Task.Triggers) {
                if ($Trigger.Repetition -and $Trigger.Repetition.Interval) {
                    Write-Host "    Current Interval: $($Trigger.Repetition.Interval)" -ForegroundColor Cyan
                }
            }
        }
    }
    
    if ($UpdateAll) {
        Write-Host "`nUpdating task frequencies to $IntervalMinutes minutes..." -ForegroundColor Yellow
        
        $UpdatedCount = 0
        foreach ($Task in $Tasks) {
            try {
                $TaskName = $Task.TaskName
                Write-Host "  Updating: $TaskName" -ForegroundColor Gray
                
                # Create new trigger with specified interval
                $NewTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration ([TimeSpan]::MaxValue)
                
                # Update the task
                Set-ScheduledTask -TaskName $TaskName -Trigger $NewTrigger
                
                Write-Host "    ✅ Updated successfully" -ForegroundColor Green
                $UpdatedCount++
            }
            catch {
                Write-Host "    ❌ Failed to update: $_" -ForegroundColor Red
            }
        }
        
        Write-Host "`nUpdate Summary:" -ForegroundColor Cyan
        Write-Host "  Total tasks: $($Tasks.Count)" -ForegroundColor White
        Write-Host "  Successfully updated: $UpdatedCount" -ForegroundColor Green
        Write-Host "  New interval: $IntervalMinutes minutes" -ForegroundColor Cyan
        
        if ($UpdatedCount -eq $Tasks.Count) {
            Write-Host "`n🎉 All tasks updated successfully!" -ForegroundColor Green
        }
    } else {
        Write-Host "`nTo update all tasks to $IntervalMinutes minute intervals, run:" -ForegroundColor Yellow
        Write-Host "  .\eq12_nfl_task_simple.ps1 -UpdateAll -IntervalMinutes $IntervalMinutes" -ForegroundColor White
    }
}
catch {
    Write-Error "Error processing scheduled tasks: $_"
}