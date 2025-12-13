<#
Wrapper to safely call existing run_daily_maintenance_now.ps1 (if present) then call Reflect integration.
Creates a backup of the original file before editing.
#>
[CmdletBinding()]
param(
    [switch]$Verify
)

$main = 'C:\EQ12\scripts\run_daily_maintenance_now.ps1'
$integration = 'C:\EQ12\scripts\eq12_reflect_integration.ps1'

if (Test-Path $main) {
    Write-Output "Found main maintenance script: $main"
    $bak = "$main.bak.$((Get-Date).ToString('yyyyMMddHHmmss'))"
    Copy-Item -Path $main -Destination $bak -Force
    Write-Output "Backed up to $bak"
    Write-Output "Invoking main maintenance (verify=$Verify)"
    if ($Verify) { Write-Output "Would run: & '$main' -Verify" } else { & $main }
} else {
    Write-Output "No existing main maintenance script at $main"
}

# Call Reflect integration wrapper
if (Test-Path $integration) {
    Write-Output "Invoking Reflect integration (verify=$Verify)"
    if ($Verify) { Write-Output "Would run: & '$integration' -Verify" } else { & $integration -Verify:$Verify }
} else {
    Write-Output "Reflect integration wrapper not found: $integration"
}
