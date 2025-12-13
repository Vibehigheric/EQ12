# Register Windows Data Sentinel as a Scheduled Task
# Run this script AS ADMINISTRATOR once to set up automatic polling

param(
    [string]$TaskName = "EQ12_WindowsDataSentinel",
    [int]$IntervalMinutes = 15,
    [switch]$Unregister
)

if ($Unregister) {
    Write-Host "Unregistering task: $TaskName" -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Task unregistered (if it existed)" -ForegroundColor Green
    exit 0
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Windows Data Sentinel Task Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$psPath = (Get-Command powershell.exe).Source
$scriptPath = "C:\EQ12\WindowsDataSentinel\scripts\run_all.ps1"

if (-not (Test-Path $scriptPath)) {
    Write-Host "ERROR: run_all.ps1 not found at: $scriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "PowerShell Path: $psPath" -ForegroundColor Gray
Write-Host "Script Path: $scriptPath" -ForegroundColor Gray
Write-Host "Interval: Every $IntervalMinutes minutes" -ForegroundColor Gray
Write-Host ""

# Unregister existing task if it exists
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Create task action
$action = New-ScheduledTaskAction `
    -Execute $psPath `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`" -Verbose"

# Create trigger (every X minutes, forever)
$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date).AddMinutes(2) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) `
    -RepetitionDuration ([TimeSpan]::MaxValue)

# Create principal (run as current user, highest privileges)
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Highest

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Description "EQ12 Windows Data Sentinel - Automated data collection from RSS feeds and APIs" `
        -ErrorAction Stop
    
    Write-Host "✅ SUCCESS: Task registered successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $TaskName" -ForegroundColor White
    Write-Host "  Schedule: Every $IntervalMinutes minutes" -ForegroundColor White
    Write-Host "  First Run: In 2 minutes" -ForegroundColor White
    Write-Host ""
    Write-Host "To view task status:" -ForegroundColor Yellow
    Write-Host "  Get-ScheduledTask -TaskName $TaskName" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To unregister task:" -ForegroundColor Yellow
    Write-Host "  .\register_scheduled_task.ps1 -Unregister" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "❌ ERROR: Failed to register task" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
