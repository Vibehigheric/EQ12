<#
EQ12 patch
PowerShell wrapper to build dashboard HTML from the latest snapshot.
#>
[CmdletBinding()]
param(
    [string]$JsonPath = "$env:EQ12_LOGS\dashboard_snapshot.json",
    [string]$OutHtml = "$env:EQ12_LOGS\dashboard.html"
)

if (-not (Test-Path $JsonPath)) { throw "JSON snapshot not found: $JsonPath" }

# TODO: add Pester test

Write-Host "Building dashboard HTML from $JsonPath to $OutHtml"
& powershell -NoProfile -ExecutionPolicy Bypass -File "C:\EQ12\scripts\build_dashboard.ps1" -JsonPath $JsonPath -OutHtml $OutHtml

Write-Host "Dashboard build complete"
