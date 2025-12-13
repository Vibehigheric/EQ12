[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$LocalLogs = 'C:\EQ12\logs',
    [Parameter(Mandatory=$false)]
    [string]$CodespaceLogs = '/workspaces/EQ12/logs'
)

Write-Host "Initializing logs directories..."
if (-not (Test-Path $LocalLogs)) { New-Item -ItemType Directory -Path $LocalLogs -Force | Out-Null }
if (-not (Test-Path $CodespaceLogs)) {
    try {
        New-Item -ItemType Directory -Path $CodespaceLogs -Force | Out-Null
    } catch {
        Write-Host "Could not create $CodespaceLogs in this environment. This is expected on Windows." -ForegroundColor Yellow
    }
}

Write-Host "Logs initialized. Local: $LocalLogs, Codespaces: $CodespaceLogs"