<#
Simple local wrapper to run Codex CLI commands in the repo.
It prefers a CODEX_API_KEY env var; otherwise prompts the user.
#>
[CmdletBinding()]
param(
    [string]$Command = 'run pytest -q',
    [switch]$InstallIfMissing
)

function Get-CodexExecutable {
    $codex = (Get-Command codex -ErrorAction SilentlyContinue).Source
    if (-not $codex -and $InstallIfMissing) {
        Write-Host "Attempting to install codex CLI via npm..."
        npm i -g @openai/codex 2>&1 | Write-Host
        $codex = (Get-Command codex -ErrorAction SilentlyContinue).Source
    }
    return $codex
}

$codex = Get-CodexExecutable
if (-not $codex) {
    Write-Warning 'codex CLI not available. Install with: npm i -g @openai/codex'
    exit 0
}

if (-not $env:CODEX_API_KEY) {
    $env:CODEX_API_KEY = Read-Host -Prompt 'Enter CODEX_API_KEY (or set CODEX_API_KEY env var)'
}

# Run codex in dry-run mode if supported
& $codex --dry-run $Command | Tee-Object -FilePath codex-output.txt
Write-Host 'Codex run complete; output saved to codex-output.txt'
