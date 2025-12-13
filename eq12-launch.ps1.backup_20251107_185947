#!/usr/bin/env powershell
# EQ12 Workspace Profile Manager

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [ValidateSet('dev', 'data', 'triage', 'ops', 'aiml', 'default')]
    [string]$ProfileName = 'dev',

    [switch]$ListProfiles,
    [switch]$Help
)

$EQ12Root = "C:\EQ12"
$WorkspaceFile = "$EQ12Root\EQ12-GODSTACK-OPTIMAL.code-workspace"

# Profile mapping
$ProfileMap = @{
    'dev'     = 'EQ12 Dev (Professional)'
    'data'    = 'EQ12 Data (Heavy)'
    'triage'  = 'EQ12 Triage (Minimal)'
    'ops'     = 'EQ12 Ops (Read-Only)'
    'aiml'    = 'EQ12 AI/ML (Specialized)'
    'default' = $null
}

if ($Help) {
    Write-Host "EQ12 Workspace Profile Manager" -ForegroundColor Green
    Write-Host "Usage: .\eq12-launch.ps1 [ProfileName]" -ForegroundColor Yellow
    Write-Host "Profiles: dev, data, triage, ops, aiml, default" -ForegroundColor Cyan
    return
}

if ($ListProfiles) {
    Write-Host "Available EQ12 Profiles:" -ForegroundColor Green
    foreach ($item in $ProfileMap.GetEnumerator()) {
        Write-Host "  $($item.Key) -> $($item.Value)" -ForegroundColor Cyan
    }
    return
}

# Build VS Code command
$codeArgs = @()
$selectedProfile = $ProfileMap[$ProfileName]
if ($selectedProfile) {
    $codeArgs += "--profile", $selectedProfile
    Write-Host "Launching with profile: $selectedProfile" -ForegroundColor Green
}

$codeArgs += "--new-window"
if (Test-Path $WorkspaceFile) {
    $codeArgs += $WorkspaceFile
} else {
    $codeArgs += $EQ12Root
}

Write-Host "Launching VS Code..." -ForegroundColor Green
Start-Process -FilePath "code" -ArgumentList $codeArgs -NoNewWindow
Write-Host "Done!" -ForegroundColor Green
