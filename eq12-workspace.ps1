#!/usr/bin/env powershell
<#
.SYNOPSIS
    EQ12 Workspace Profile Manager
.DESCRIPTION
    Quick launcher for EQ12 VS Code profiles and workspace configurations
.PARAMETER Profile
    Profile to launch: dev, data, triage, ops, aiml
.PARAMETER Task
    Task to run after launch: bootstrap, test, validate, pipeline
.EXAMPLE
    .\eq12-workspace.ps1 -ProfileName dev
    .\eq12-workspace.ps1 -ProfileName data -Task bootstrap
#>

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [ValidateSet('dev', 'data', 'triage', 'ops', 'aiml', 'default')]
    [string]$ProfileName = 'dev',

    [Parameter(Position=1)]
    [ValidateSet('bootstrap', 'test', 'validate', 'pipeline', 'none')]
    [string]$Task = 'none',

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

# Task mapping
$TaskMap = @{
    'bootstrap' = 'EQ12: Bootstrap Environment'
    'test'      = 'EQ12: Run Tests (Fast)'
    'validate'  = 'EQ12: System Validation'
    'pipeline'  = 'EQ12: CI/CD Pipeline'
    'none'      = $null
}

if ($Help) {
    Write-Host "🚀 EQ12 Workspace Profile Manager" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\eq12-workspace.ps1 [Profile] [Task]"
    Write-Host ""
    Write-Host "Profiles:" -ForegroundColor Cyan
    Write-Host "  dev     - EQ12 Dev (Professional) - Main development"
    Write-Host "  data    - EQ12 Data (Heavy) - Jupyter & analysis"
    Write-Host "  triage  - EQ12 Triage (Minimal) - Fast debugging"
    Write-Host "  ops     - EQ12 Ops (Read-Only) - Safe inspection"
    Write-Host "  aiml    - EQ12 AI/ML (Specialized) - Advanced ML"
    Write-Host "  default - No profile (use workspace defaults)"
    Write-Host ""
    Write-Host "Tasks:" -ForegroundColor Magenta
    Write-Host "  bootstrap - Set up environment"
    Write-Host "  test      - Run quick tests"
    Write-Host "  validate  - System validation"
    Write-Host "  pipeline  - Full CI/CD pipeline"
    Write-Host "  none      - No task (default)"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Green
    Write-Host "  .\eq12-workspace.ps1 dev bootstrap"
    Write-Host "  .\eq12-workspace.ps1 data"
    Write-Host "  .\eq12-workspace.ps1 -ListProfiles"
    return
}

if ($ListProfiles) {
    Write-Host "📋 Available EQ12 Profiles:" -ForegroundColor Green
    $ProfileMap.GetEnumerator() | ForEach-Object {
        $key = $_.Key
        $value = $_.Value
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
    return 1
}

# Build VS Code command
$codeArgs = @()

# Add profile if specified
$selectedProfile = $ProfileMap[$ProfileName]
if ($selectedProfile) {
    $codeArgs += "--profile"
    $codeArgs += $selectedProfile
    Write-Host "🎯 Launching with profile: $selectedProfile" -ForegroundColor Green
} else {
    Write-Host "🔧 Launching with workspace defaults" -ForegroundColor Yellow
}

# Add new window flag
$codeArgs += "--new-window"

# Add workspace path
if (Test-Path $WorkspaceFile) {
    $codeArgs += $WorkspaceFile
    Write-Host "📂 Opening workspace: EQ12-GODSTACK-OPTIMAL.code-workspace" -ForegroundColor Cyan
} else {
    $codeArgs += $EQ12Root
    Write-Host "📂 Opening folder: $EQ12Root" -ForegroundColor Cyan
}

try {
    # Launch VS Code
    Write-Host "🚀 Launching VS Code..." -ForegroundColor Green
    Start-Process -FilePath "code" -ArgumentList $codeArgs -NoNewWindow

    # Wait for VS Code to start, then run task if specified
    if ($Task -ne 'none') {
        $selectedTask = $TaskMap[$Task]
        Write-Host "⏳ Waiting for VS Code to start..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3

        Write-Host "🔧 Running task: $selectedTask" -ForegroundColor Magenta

        # Use VS Code CLI to run task
        $taskArgs = @(
            "--command", "workbench.action.tasks.runTask"
            "--args", $selectedTask
        )
        Start-Process -FilePath "code" -ArgumentList $taskArgs -NoNewWindow
    }

    Write-Host "✅ EQ12 workspace launched successfully!" -ForegroundColor Green

} catch {
    Write-Error "❌ Failed to launch VS Code: $($_.Exception.Message)"
    return 1
}
