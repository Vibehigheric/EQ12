$ErrorActionPreference = "Stop"

$TargetIP = "192.168.100.3"
$User = "ricoj100"
$ScriptPath = "$PSScriptRoot/m70q_bootstrap.sh"

Write-Host "=== Bootstrapping M70q at $TargetIP ===" -ForegroundColor Cyan

# Check if script exists
if (-not (Test-Path $ScriptPath)) {
    Write-Error "Bootstrap script not found at $ScriptPath"
}

# Convert line endings to LF just in case
(Get-Content $ScriptPath -Raw) -replace "`r`n", "`n" | Set-Content $ScriptPath -NoNewline

Write-Host "Connecting to $TargetIP... You may be prompted for your password." -ForegroundColor Yellow

# Execute remote script
# Use scp to copy the file first, then execute it with ssh -t to allow sudo prompts
Write-Host "Copying script to $TargetIP..." -ForegroundColor Cyan
scp $ScriptPath "${User}@${TargetIP}:/tmp/m70q_bootstrap.sh"

Write-Host "Executing script..." -ForegroundColor Cyan
ssh -t "${User}@${TargetIP}" "chmod +x /tmp/m70q_bootstrap.sh && sudo /tmp/m70q_bootstrap.sh"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Bootstrap initiated successfully. Node is rebooting." -ForegroundColor Green
}
else {
    Write-Host "Bootstrap failed or connection dropped (expected during reboot)." -ForegroundColor Yellow
}
