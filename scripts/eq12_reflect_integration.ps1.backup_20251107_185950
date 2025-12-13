<#
Lightweight integration snippet to call Reflect backup/test from your daily maintenance script.
Drop a single line into `run_daily_maintenance_now.ps1` to invoke this file.
This wrapper is conservative: it will call the backup script; optionally call the viBoot test when on Sunday or when forced.
#>
param(
    [switch]$Verify
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backupScript = Join-Path $scriptDir 'eq12_reflect_backup.ps1'
$testScript = Join-Path $scriptDir 'eq12_reflect_test.ps1'

if (Test-Path $backupScript) {
    if ($Verify) { Write-Output 'Would invoke: ' $backupScript }
    else { & $backupScript }
} else { Write-Output "Reflect backup script not found at $backupScript" }

# Run viBoot test on Sunday (or use -Verify and force manually by calling this wrapper with -Verify:0 and setting RunViBootTest in your daily script)
if ((Get-Date).DayOfWeek -eq 'Sunday') {
    if (Test-Path $testScript) {
        if ($Verify) { Write-Output 'Would invoke viBoot test: ' $testScript }
        else { & $testScript }
    } else { Write-Output "viBoot test script not found at $testScript" }
}
