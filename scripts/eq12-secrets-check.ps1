[CmdletBinding()]
param()

# Checks that required Codespaces/CI secrets are present and exits non-zero if missing
$required = @('ODDS_API_KEY','TELEGRAM_BOT_TOKEN','TELEGRAM_CHAT_ID')
$missing = @()
foreach ($name in $required) {
    if (-not ${env:$name}) {
        $missing += $name
    }
}
if ($missing.Count -gt 0) {
    Write-Error "Missing required secrets: $($missing -join ', ')"
    exit 1
}
Write-Output "All required secrets present."
