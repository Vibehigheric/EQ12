<#
PowerShell remediation script to run after 10pm: safe actions
- Back up .env to logs/.env.backup.YYYYMMDD_HHMMSS
- Run Python scrub_secrets.py (report only)
- Replace sensitive values in `.env` with `REDACTED_BY_OPERATOR` placeholders (non-reversible)
- Save a post-run report to logs/post_10pm_report_TIMESTAMP.json

NOTE: This script attempts to be safe; it will backup .env before any changes.
#>

[CmdletBinding()]
param()

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
$logs = Join-Path $root "..\logs" | Resolve-Path -ErrorAction SilentlyContinue
if (-not $logs) { New-Item -Path (Join-Path $root "..\logs") -ItemType Directory | Out-Null }
$logs = (Join-Path $root "..\logs")

$timestamp = (Get-Date).ToString('yyyyMMdd_HHmmss')
$envPath = Join-Path $root "..\.env"
$backupPath = Join-Path $logs ".env.backup.$timestamp"

Write-Host "Backing up .env -> $backupPath"
if (Test-Path $envPath) {
    Copy-Item $envPath $backupPath -Force
}
else {
    Write-Host ".env not found at $envPath; creating empty .env" -ForegroundColor Yellow
    "# EQ12 .env created by EQ12_POST_10PM" | Out-File -FilePath $envPath -Encoding utf8
    Copy-Item $envPath $backupPath -Force
}

# Run non-destructive secret scanner (Python)
Write-Host "Running scrub_secrets.py to generate findings report"
$python = "python"
$scanner = Join-Path $root "scrub_secrets.py"
if (Test-Path $scanner) {
    & $python $scanner
}
else {
    Write-Host "scrub_secrets.py not found at $scanner" -ForegroundColor Red
}

# Redact sensitive keys in .env (simple, targeted replacements)
Write-Host "Redacting sensitive keys in .env (placeholders)"
$envText = Get-Content $envPath -Raw -ErrorAction Stop
$keys = @("OPENAI_API_KEY", "GROQ_API_KEY", "GOOGLE_AI_API_KEY", "OPENROUTER_API_KEY", "ODDS_API_KEY", "OPENWEATHER_API_KEY", "GITHUB_TOKEN", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "AZURE_OPENAI_API_KEY", "CLAUDE_API_KEY", "CHATGPT_API_KEY", "API_KEY")
foreach ($k in $keys) {
    $pattern = "^\s*($k)\s*=.*$"
    if ($envText -match $pattern) {
        $envText = [regex]::Replace($envText, $pattern, "$1=REDACTED_BY_OPERATOR", 'IgnoreCase', [System.TimeSpan]::FromSeconds(1))
    }
    else {
        # add placeholder if missing
        $envText += "`n$k=REDACTED_BY_OPERATOR"
    }
}

Set-Content -Path $envPath -Value $envText -Encoding UTF8

# Generate post-run JSON report summarizing actions
$postReport = @{ 
    timestamp           = (Get-Date).ToString('o')
    env_backup          = $backupPath
    scrub_report_prefix = "scrub_secrets_report_"
    env_path            = $envPath
    note                = "Sensitive keys in .env were replaced with REDACTED_BY_OPERATOR. Backup stored. Review scrub_secrets report for occurrences."
}
$postJson = $postReport | ConvertTo-Json -Depth 5
$postFile = Join-Path $logs "post_10pm_report_$timestamp.json"
$postJson | Out-File -FilePath $postFile -Encoding utf8

Write-Host "Post-10pm remediation script completed. Report: $postFile"
