<#
EQ12 patch
Run scraper template and build dashboard; intended to be run from PowerShell (Windows) or pwsh in Codespaces.
#>
[CmdletBinding()]
param(
    [string]$OutJson = "$env:EQ12_LOGS\scraper_output.json",
    [switch]$Quiet
)

Begin {
    $logs = $env:EQ12_LOGS -or 'C:\EQ12\logs'
    if (-not (Test-Path $logs)) { New-Item -ItemType Directory -Path $logs -Force | Out-Null }
}

Process {
    $scriptPath = Join-Path $PSScriptRoot 'scripts\templates\python_scraper_template.py'
    if (-not (Test-Path $scriptPath)) { $scriptPath = 'C:\EQ12\scripts\templates\python_scraper_template.py' }
    if (-not (Test-Path $scriptPath)) { throw "Scraper template not found at $scriptPath" }

    Write-Host "Running scraper template -> $OutJson"
    & python $scriptPath --out-json $OutJson

    # TODO: add pytest test for schema

    # Build dashboard HTML from the latest snapshot
    $dashboardJson = $OutJson
    $dashboardOut = Join-Path $logs 'dashboard.html'
    Write-Host "Building dashboard HTML -> $dashboardOut"
    & powershell -NoProfile -ExecutionPolicy Bypass -File "C:\EQ12\scripts\build_dashboard.ps1" -JsonPath $dashboardJson -OutHtml $dashboardOut

    Write-Host "eq12-elite-run complete"
}
