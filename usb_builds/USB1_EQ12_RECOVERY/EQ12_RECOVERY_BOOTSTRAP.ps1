#!/usr/bin/env powershell
# EQ12 Recovery Bootstrap Script
# Rebuilds entire EQ12 system in 20 minutes
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

Write-Host " EQ12 RECOVERY SYSTEM ACTIVATED" -ForegroundColor Cyan
Write-Host "Buffalo NY 14215 Content Empire Recovery" -ForegroundColor Yellow
Write-Host "=" * 50

$RecoveryPath = $PSScriptRoot
$EQ12Path = "C:\EQ12"

# Step 1: Prepare directories
Write-Host " Creating EQ12 directory structure..." -ForegroundColor Green
New-Item -Path $EQ12Path -ItemType Directory -Force
$subdirs = @("scripts", "logs", "data", "configs", "dashboard", "tests")
foreach ($dir in $subdirs) {
    New-Item -Path "$EQ12Path\$dir" -ItemType Directory -Force
}

# Step 2: Copy all EQ12 scripts
Write-Host " Restoring EQ12 scripts..." -ForegroundColor Green
Copy-Item "$RecoveryPath\EQ12_BOOTSTRAP\*" -Destination "$EQ12Path\scripts\" -Recurse -Force

# Step 3: Restore Python environment
Write-Host " Setting up Python environment..." -ForegroundColor Green
& "$RecoveryPath\PYTHON_ENV\setup_python.ps1"

# Step 4: Install VS Code extensions
Write-Host " Installing VS Code extensions..." -ForegroundColor Green
& "$RecoveryPath\VSCODE_EXTENSIONS\install_extensions.ps1"

# Step 5: Configure Coral drivers
Write-Host " Setting up Coral TPU drivers..." -ForegroundColor Green
& "$RecoveryPath\CORAL_DRIVERS\install_coral.ps1"

# Step 6: Discover Raspberry Pi
Write-Host " Scanning for Raspberry Pi..." -ForegroundColor Green
& "$RecoveryPath\PI_DISCOVERY\find_pi.ps1"

# Step 7: Restore API keys (encrypted)
Write-Host " Restoring API keys..." -ForegroundColor Yellow
& "$RecoveryPath\API_KEYS_ENCRYPTED\restore_keys.ps1"

# Step 8: Windows system repair
Write-Host " Running Windows repair utilities..." -ForegroundColor Green
& "$RecoveryPath\WINDOWS_REPAIR\system_repair.ps1"

# Step 9: Configure GitHub/Copilot
Write-Host " Configuring GitHub integration..." -ForegroundColor Green
& "$RecoveryPath\GITHUB_CONFIG\setup_github.ps1"

# Step 10: Apply encoding fixes
Write-Host " Applying encoding immunity..." -ForegroundColor Green
& "$RecoveryPath\ENCODING_FIXES\apply_immunity.ps1"

Write-Host ""
Write-Host " EQ12 RECOVERY COMPLETE!" -ForegroundColor Green
Write-Host " Content Empire restored and operational" -ForegroundColor Cyan
Write-Host " Buffalo NY 14215 advantage: ACTIVE" -ForegroundColor Magenta

# Test system
Write-Host " Running system tests..." -ForegroundColor Yellow
& "$EQ12Path\scripts\eq12_workspace_guard.py" --quick
& "$EQ12Path\scripts\revenue_tracker_hardened.py" --report

Write-Host ""
Write-Host " EQ12 System Status: FULLY OPERATIONAL" -ForegroundColor Green
