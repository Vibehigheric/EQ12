<#
.SYNOPSIS
    Schedule EQ12 Daily Loop to run at 3:00 AM UTC every day

.DESCRIPTION
    Creates Windows Task Scheduler job to execute DailyLoopOrchestrator
    Handles timezone conversion, logging, error handling

.EXAMPLE
    .\Schedule-DailyLoop.ps1 -Install
    .\Schedule-DailyLoop.ps1 -Remove
    .\Schedule-DailyLoop.ps1 -RunNow
#>

[CmdletBinding()]
param(
    [Parameter()]
    [switch]$Install,
    
    [Parameter()]
    [switch]$Remove,
    
    [Parameter()]
    [switch]$RunNow,
    
    [Parameter()]
    [string]$DataRoot = "C:\EQ12_BROKEN_20251122_210342"
)

$TaskName = "EQ12_Daily_Loop"
$ScriptPath = Join-Path $DataRoot "src\EQ12.Phase33\DailyLoopOrchestrator.vb"

function Install-DailyLoopSchedule {
    Write-Host "📅 Installing EQ12 Daily Loop schedule..." -ForegroundColor Cyan
    
    # Convert 3 AM UTC to local time
    $utcTime = [DateTime]::UtcNow.Date.AddHours(3)
    $localTime = [System.TimeZoneInfo]::ConvertTimeFromUtc($utcTime, [System.TimeZoneInfo]::Local)
    
    Write-Host "   UTC Time: 03:00 UTC" -ForegroundColor Gray
    Write-Host "   Local Time: $($localTime.ToString('HH:mm')) $([System.TimeZoneInfo]::Local.DisplayName)" -ForegroundColor Gray
    
    # Create action to run VB.NET executable
    # In production, this would call the compiled .exe
    # For now, we'll use a PowerShell wrapper
    
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$DataRoot\scripts\Run-DailyLoop.ps1`""
    
    # Create trigger for daily 3 AM UTC
    $trigger = New-ScheduledTaskTrigger -Daily -At $localTime
    
    # Create principal (run with highest privileges)
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
    
    # Create settings
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RunOnlyIfNetworkAvailable `
        -ExecutionTimeLimit (New-TimeSpan -Hours 1)
    
    # Register task
    try {
        Register-ScheduledTask -TaskName $TaskName `
            -Action $action `
            -Trigger $trigger `
            -Principal $principal `
            -Settings $settings `
            -Force | Out-Null
        
        Write-Host "✅ Task '$TaskName' installed successfully" -ForegroundColor Green
        Write-Host "   Next run: $((Get-ScheduledTask -TaskName $TaskName).NextRunTime)" -ForegroundColor Green
    }
    catch {
        Write-Error "❌ Failed to install task: $_"
        exit 1
    }
}

function Remove-DailyLoopSchedule {
    Write-Host "🗑️  Removing EQ12 Daily Loop schedule..." -ForegroundColor Cyan
    
    try {
        if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            Write-Host "✅ Task '$TaskName' removed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️  Task '$TaskName' not found" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Error "❌ Failed to remove task: $_"
        exit 1
    }
}

function Start-DailyLoopNow {
    Write-Host "▶️  Running Daily Loop NOW..." -ForegroundColor Cyan
    
    # Check if task exists
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "✅ Daily Loop started" -ForegroundColor Green
        
        # Monitor for completion
        Start-Sleep -Seconds 2
        $task = Get-ScheduledTask -TaskName $TaskName
        Write-Host "   Status: $($task.State)" -ForegroundColor Gray
    }
    else {
        Write-Host "⚠️  Task not installed. Run with -Install first." -ForegroundColor Yellow
        Write-Host "   Or run directly:" -ForegroundColor Gray
        Write-Host "   & `"$DataRoot\scripts\Run-DailyLoop.ps1`"" -ForegroundColor Gray
    }
}

# Main execution
if ($Install) {
    Install-DailyLoopSchedule
}
elseif ($Remove) {
    Remove-DailyLoopSchedule
}
elseif ($RunNow) {
    Start-DailyLoopNow
}
else {
    Write-Host "EQ12 Daily Loop Scheduler" -ForegroundColor Cyan
    Write-Host "Usage:" -ForegroundColor Gray
    Write-Host "  -Install    Install daily schedule (3 AM UTC)" -ForegroundColor Gray
    Write-Host "  -Remove     Remove schedule" -ForegroundColor Gray
    Write-Host "  -RunNow     Execute loop immediately" -ForegroundColor Gray
    Write-Host ""
    
    # Show current status
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
        $task = Get-ScheduledTask -TaskName $TaskName
        Write-Host "✅ Task installed" -ForegroundColor Green
        Write-Host "   State: $($task.State)" -ForegroundColor Gray
        Write-Host "   Next run: $($task.NextRunTime)" -ForegroundColor Gray
    }
    else {
        Write-Host "⚠️  Task not installed" -ForegroundColor Yellow
    }
}
