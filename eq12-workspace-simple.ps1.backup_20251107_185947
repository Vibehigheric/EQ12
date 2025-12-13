#!/usr/bin/env powershell
<#
.SYNOPSIS
    EQ12 Workspace Profile Manager
.DESCRIPTION
    Quick launcher for EQ12 VS Code profiles and workspace configurations
#>

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
    Write-Host "🚀 EQ12 Workspace Profile Manager" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\eq12-workspace.ps1 [ProfileName]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Profiles:" -ForegroundColor Cyan
    Write-Host "  dev     - Main development (Ruff + Copilot + Tests)"
    Write-Host "  data    - Jupyter & data analysis"
    Write-Host "  triage  - Fast debugging (minimal)"
    Write-Host "  ops     - Read-only inspection"
    Write-Host "  aiml    - Advanced ML development"
    Write-Host "  default - Workspace defaults"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\eq12-workspace.ps1 dev"
    Write-Host "  .\eq12-workspace.ps1 -ListProfiles"
    return
}

if ($ListProfiles) {
    Write-Host "📋 Available EQ12 Profiles:" -ForegroundColor Green
    foreach ($item in $ProfileMap.GetEnumerator()) {
        $key = $item.Key
        $value = $item.Value
        if ($value) {
            Write-Host "  $key -> $value" -ForegroundColor Cyan
        } else {
            Write-Host "  $key -> Workspace defaults" -ForegroundColor Yellow
        }
    }
    return
}

# Validate workspace exists
if (-not (Test-Path $EQ12Root)) {
    Write-Error "❌ EQ12 workspace not found at: $EQ12Root"
    return
}

# Build VS Code command
$codeArgs = @()

# Add profile if specified
$selectedProfile = $ProfileMap[$ProfileName]
if ($selectedProfile) {
    $codeArgs += "--profile", $selectedProfile
    Write-Host "🎯 Launching with profile: $selectedProfile" -ForegroundColor Green
} else {
    Write-Host "🔧 Launching with workspace defaults" -ForegroundColor Yellow
}

# Add workspace path
$codeArgs += "--new-window"
if (Test-Path $WorkspaceFile) {
    $codeArgs += $WorkspaceFile
    Write-Host "📂 Opening workspace: EQ12-GODSTACK-OPTIMAL.code-workspace" -ForegroundColor Cyan
} else {
    $codeArgs += $EQ12Root
    Write-Host "📂 Opening folder: $EQ12Root" -ForegroundColor Cyan
}

# Launch VS Code
Write-Host "🚀 Launching VS Code..." -ForegroundColor Green
try {
    Start-Process -FilePath "code" -ArgumentList $codeArgs -NoNewWindow
    Write-Host "✅ EQ12 workspace launched successfully!" -ForegroundColor Green
} catch {
    Write-Error "❌ Failed to launch VS Code: $_"
}
