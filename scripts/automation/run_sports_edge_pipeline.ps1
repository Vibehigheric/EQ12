param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..' '..')).Path,
    [string]$Timezone = 'US/Eastern'
)

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error 'Python is required to run the sports edge pipeline.'
    exit 1
}

$script = Join-Path $RepoRoot 'scripts/sports/eq12_sports_command_center.py'
if (-not (Test-Path $script)) {
    Write-Error "Sports command center script not found at $script"
    exit 1
}

$env:EQ12_REPO_ROOT = $RepoRoot
$env:EQ12_LOG_ROOT = Join-Path $RepoRoot 'logs'
$env:EQ12_DATA_ROOT = Join-Path $RepoRoot 'data'
$env:EQ12_CONFIG_ROOT = Join-Path $RepoRoot 'configs'

& $python.Source $script --timezone $Timezone --dump
