<#
setup_orchestrator_schedule.ps1
Registers a Windows Scheduled Task to run the eq12-orchestrator.ps1 script daily at 07:00 local time.
Run this script in an elevated PowerShell session if you run into permission errors.
#>
[CmdletBinding()]
param(
    [int]$Hour = 7,
    [int]$Minute = 0
)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$orchestratorWrapper = Join-Path $scriptDir 'eq12-orchestrator.ps1'
if (-not (Test-Path $orchestratorWrapper)) {
    Write-Host "Could not find $orchestratorWrapper"
    exit 1
}

$taskName = 'EQ12-Orchestrator-Daily'
$time = (Get-Date).Date.AddHours($Hour).AddMinutes($Minute)
$action = New-ScheduledTaskAction -Execute 'PowerShell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$orchestratorWrapper`""
$trigger = New-ScheduledTaskTrigger -Daily -At $time
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Description 'EQ12: daily orchestrator run' -Force
    Write-Host "Scheduled Task '$taskName' registered to run daily at ${Hour}:${Minute}."
} catch {
    Write-Host "Failed to register scheduled task: $($_.Exception.Message)"
    Write-Host "Try running this script as Administrator."
}
""