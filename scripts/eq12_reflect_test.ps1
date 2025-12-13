<#
.SYNOPSIS
Use Macrium viBoot to stage the latest backup and run EQ12 stack checks inside the VM.

.DESCRIPTION
This script wraps `eq12_viboot_stage.ps1` where available. It will stage a VM (via viBoot), run the provided test commands inside the VM, collect results, and write a JSON log to C:\EQ12\logs\viboot_test.log.

Safety: Default is dry-run when called with -Verify.
#>
[CmdletBinding()]
param(
    [switch]$Verify,
    [string]$ConfigPath
)

function Write-Log($status, $msg, $extra) {
    $entry = @{ ts = (Get-Date).ToString('o'); status = $status; msg = $msg }
    if ($extra) { $entry.extra = $extra }
    $json = $entry | ConvertTo-Json -Depth 5
    $logDir = 'C:\EQ12\logs'
    if (-not (Test-Path $logDir)) { New-Item -Path $logDir -ItemType Directory -Force | Out-Null }
    $logFile = Join-Path $logDir 'viboot_test.log'
    Add-Content -Path $logFile -Value $json
}

function Send-Telegram($text) {
    if (Get-Command -Name 'eq12-tg' -ErrorAction SilentlyContinue) {
    try { & eq12-tg $text } catch { Write-Log 'warning' ("eq12-tg failed: {0}" -f $_.Exception.Message) $null }
        return
    }
    $token = $env:TELEGRAM_BOT_TOKEN
    $chat = $env:TELEGRAM_CHAT_ID
    if (-not $token -or -not $chat) { Write-Log 'warning' 'No Telegram notifier configured' $null; return }
    try {
        $uri = "https://api.telegram.org/bot$token/sendMessage"
        $body = @{ chat_id = $chat; text = $text }
        Invoke-RestMethod -Uri $uri -Method Post -Body $body -ErrorAction Stop | Out-Null
    } catch {
    Write-Log 'warning' ("Telegram HTTP send failed: {0}" -f $_.Exception.Message) $null
    }
}

if ($Verify) { Write-Log 'info' 'Verify mode: dry-run' $null; return }

# prefer local staging helper if present
$stageScript = 'C:\EQ12\scripts\eq12_viboot_stage.ps1'
if (-not (Test-Path $stageScript)) {
    Write-Log 'error' "Staging helper not found: $stageScript" $null
    return
}

# Prepare a temporary config for eq12_viboot_stage (or use provided ConfigPath)
if (-not $ConfigPath) {
    $tempCfg = [PSCustomObject]@{
        backup_directory = 'D:\Backups'
        vm = @{ BootTimeoutSec = 300 }
        tests = @{ test_commands = @('eq12-elite-run --dry-run', 'eq12-build-dashboard --check'); vm_logs_path = 'C:\EQ12\logs' }
    }
    $tempCfgPath = Join-Path (Split-Path -Parent $stageScript) 'viboot_temp_config.json'
    $tempCfg | ConvertTo-Json -Depth 5 | Set-Content -Path $tempCfgPath -Encoding UTF8
} else {
    $tempCfgPath = $ConfigPath
}

# Invoke the staging script and capture output
try {
    Write-Log 'info' 'Starting viBoot staging and tests' @{ cfg = $tempCfgPath }
    $out = & $stageScript -ConfigPath $tempCfgPath
    Write-Log 'ok' 'viBoot helper completed' @{ out = $out }
} catch {
    Write-Log 'error' 'viBoot test failed' @{ err = $_.Exception.Message }
    Send-Telegram ("⚠️ viBoot test failed: {0}" -f $_.Exception.Message)
}

# cleanup temp config
if (Test-Path $tempCfgPath) { Remove-Item $tempCfgPath -Force -ErrorAction SilentlyContinue }
