# =====================================================================
# EQ12 BACKUP SNAPSHOT ROUTINE
# =====================================================================
# Creates point-in-time snapshots of your working EQ12 configuration
# before making risky changes like enabling DevContainers, Docker, or
# installing new extensions.
#
# What it backs up:
#   1. .vscode/ directory (settings, tasks, launch configs)
#   2. Python venv state (requirements.txt + pip freeze)
#   3. Git repository state (branch, uncommitted changes)
#   4. VS Code extension list
#   5. Environment variables
#   6. Key configuration files
#
# Snapshots are stored in C:\EQ12\backups\ with timestamps
# and can be restored if something breaks.
#
# Usage:
#   # Create a snapshot before risky changes:
#   .\EQ12_BACKUP_SNAPSHOT.ps1 -Label "before_docker_enable"
#
#   # Create automatic snapshot:
#   .\EQ12_BACKUP_SNAPSHOT.ps1
#
#   # List all available snapshots:
#   .\EQ12_BACKUP_SNAPSHOT.ps1 -ListSnapshots
#
#   # Restore a specific snapshot:
#   .\EQ12_BACKUP_SNAPSHOT.ps1 -Restore -SnapshotId "20251122_143000_before_docker"
#
# =====================================================================

[CmdletBinding()]
param(
    [string]$Label = "auto",
    [switch]$ListSnapshots,
    [switch]$Restore,
    [string]$SnapshotId,
    [string]$BackupRoot = "C:\EQ12\backups"
)

$ErrorActionPreference = "Continue"

function Write-SnapshotLog {
    param([string]$Message, [string]$Level = "INFO")
    
    $color = switch ($Level) {
        "INFO"    { "Cyan" }
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR"   { "Red" }
        default   { "White" }
    }
    
    $symbol = switch ($Level) {
        "INFO"    { "ℹ️" }
        "SUCCESS" { "✔" }
        "WARNING" { "⚠️" }
        "ERROR"   { "❌" }
        default   { "•" }
    }
    
    Write-Host "$symbol $Message" -ForegroundColor $color
}

function Get-AllSnapshots {
    if (-not (Test-Path $BackupRoot)) {
        return @()
    }
    
    Get-ChildItem -Path $BackupRoot -Directory |
        Where-Object { $_.Name -match '^\d{8}_\d{6}_' } |
        Sort-Object Name -Descending |
        ForEach-Object {
            $manifestPath = Join-Path $_.FullName "manifest.json"
            if (Test-Path $manifestPath) {
                $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
                [PSCustomObject]@{
                    SnapshotId = $_.Name
                    Timestamp = $manifest.Timestamp
                    Label = $manifest.Label
                    SizeMB = [math]::Round((Get-ChildItem $_.FullName -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
                    Path = $_.FullName
                }
            }
        }
}

function Show-SnapshotList {
    Write-Host "`n=== EQ12 BACKUP SNAPSHOTS ===" -ForegroundColor Cyan
    Write-Host ""
    
    $snapshots = Get-AllSnapshots
    
    if ($snapshots.Count -eq 0) {
        Write-SnapshotLog "No snapshots found in $BackupRoot" "INFO"
        return
    }
    
    Write-Host "Found $($snapshots.Count) snapshot(s):" -ForegroundColor White
    Write-Host ""
    
    $snapshots | Format-Table -Property @{
        Label = "Snapshot ID"
        Expression = { $_.SnapshotId }
    }, @{
        Label = "Label"
        Expression = { $_.Label }
    }, @{
        Label = "Timestamp"
        Expression = { $_.Timestamp }
    }, @{
        Label = "Size (MB)"
        Expression = { $_.SizeMB }
    } -AutoSize
    
    Write-Host ""
    Write-SnapshotLog "To restore a snapshot, run:" "INFO"
    Write-Host "  .\EQ12_BACKUP_SNAPSHOT.ps1 -Restore -SnapshotId '<id>'" -ForegroundColor DarkGray
    Write-Host ""
}

function New-Snapshot {
    param([string]$Label)
    
    Write-Host "`n=== EQ12 BACKUP SNAPSHOT ===" -ForegroundColor Cyan
    Write-Host "Creating snapshot with label: $Label" -ForegroundColor Yellow
    Write-Host ""
    
    # Create snapshot directory
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $snapshotId = "${timestamp}_${Label}"
    $snapshotDir = Join-Path $BackupRoot $snapshotId
    
    if (-not (Test-Path $BackupRoot)) {
        New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
    }
    
    New-Item -ItemType Directory -Path $snapshotDir -Force | Out-Null
    Write-SnapshotLog "Created snapshot directory: $snapshotId" "INFO"
    
    $manifest = @{
        SnapshotId = $snapshotId
        Timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        Label = $Label
        BackupItems = @()
    }
    
    # ----------------------------------------------------------------
    # 1. Backup .vscode directory
    # ----------------------------------------------------------------
    Write-Host "[1/7] Backing up .vscode configuration..." -ForegroundColor Yellow
    
    $vscodeSource = "C:\EQ12\.vscode"
    if (Test-Path $vscodeSource) {
        $vscodeBackup = Join-Path $snapshotDir "vscode"
        Copy-Item -Path $vscodeSource -Destination $vscodeBackup -Recurse -Force
        $manifest.BackupItems += "vscode"
        Write-SnapshotLog ".vscode directory backed up" "SUCCESS"
    } else {
        Write-SnapshotLog ".vscode directory not found (skipping)" "WARNING"
    }
    
    # ----------------------------------------------------------------
    # 2. Backup Python venv state
    # ----------------------------------------------------------------
    Write-Host "`n[2/7] Backing up Python environment state..." -ForegroundColor Yellow
    
    $venvPython = "C:\EQ12\.venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        $pythonBackupDir = Join-Path $snapshotDir "python"
        New-Item -ItemType Directory -Path $pythonBackupDir -Force | Out-Null
        
        # Export pip freeze
        $pipFreeze = & $venvPython -m pip freeze 2>&1
        $pipFreeze | Set-Content -Path (Join-Path $pythonBackupDir "pip_freeze.txt") -Encoding UTF8
        
        # Copy requirements.txt if exists
        if (Test-Path "C:\EQ12\requirements.txt") {
            Copy-Item -Path "C:\EQ12\requirements.txt" -Destination (Join-Path $pythonBackupDir "requirements.txt") -Force
        }
        
        # Get Python version
        $pythonVersion = & $venvPython --version 2>&1
        $pythonVersion | Set-Content -Path (Join-Path $pythonBackupDir "python_version.txt") -Encoding UTF8
        
        $manifest.BackupItems += "python"
        Write-SnapshotLog "Python environment state backed up" "SUCCESS"
    } else {
        Write-SnapshotLog "Python venv not found (skipping)" "WARNING"
    }
    
    # ----------------------------------------------------------------
    # 3. Backup Git repository state
    # ----------------------------------------------------------------
    Write-Host "`n[3/7] Backing up Git repository state..." -ForegroundColor Yellow
    
    if (Test-Path "C:\EQ12\.git") {
        $gitBackupDir = Join-Path $snapshotDir "git"
        New-Item -ItemType Directory -Path $gitBackupDir -Force | Out-Null
        
        Set-Location "C:\EQ12" -ErrorAction SilentlyContinue
        
        # Current branch
        $currentBranch = & git branch --show-current 2>&1
        $currentBranch | Set-Content -Path (Join-Path $gitBackupDir "current_branch.txt") -Encoding UTF8
        
        # Git status
        $gitStatus = & git status --porcelain 2>&1
        $gitStatus | Set-Content -Path (Join-Path $gitBackupDir "git_status.txt") -Encoding UTF8
        
        # Uncommitted changes diff
        $gitDiff = & git diff 2>&1
        $gitDiff | Set-Content -Path (Join-Path $gitBackupDir "uncommitted_diff.txt") -Encoding UTF8
        
        # Last 10 commits
        $gitLog = & git log --oneline -10 2>&1
        $gitLog | Set-Content -Path (Join-Path $gitBackupDir "recent_commits.txt") -Encoding UTF8
        
        $manifest.BackupItems += "git"
        Write-SnapshotLog "Git repository state backed up" "SUCCESS"
    } else {
        Write-SnapshotLog "Git repository not found (skipping)" "WARNING"
    }
    
    # ----------------------------------------------------------------
    # 4. Backup VS Code extension list
    # ----------------------------------------------------------------
    Write-Host "`n[4/7] Backing up VS Code extensions list..." -ForegroundColor Yellow
    
    $extensionsBackupDir = Join-Path $snapshotDir "extensions"
    New-Item -ItemType Directory -Path $extensionsBackupDir -Force | Out-Null
    
    $extensionsPath = "$env:USERPROFILE\.vscode\extensions"
    if (Test-Path $extensionsPath) {
        $extensionList = Get-ChildItem -Path $extensionsPath -Directory |
            Select-Object Name, LastWriteTime |
            ConvertTo-Json -Depth 3
        
        $extensionList | Set-Content -Path (Join-Path $extensionsBackupDir "installed_extensions.json") -Encoding UTF8
        
        $manifest.BackupItems += "extensions"
        Write-SnapshotLog "VS Code extensions list backed up" "SUCCESS"
    } else {
        Write-SnapshotLog "VS Code extensions directory not found (skipping)" "WARNING"
    }
    
    # ----------------------------------------------------------------
    # 5. Backup environment variables
    # ----------------------------------------------------------------
    Write-Host "`n[5/7] Backing up environment variables..." -ForegroundColor Yellow
    
    $envBackupDir = Join-Path $snapshotDir "environment"
    New-Item -ItemType Directory -Path $envBackupDir -Force | Out-Null
    
    # Capture relevant environment variables
    $envVars = @{
        PYTHONPATH = $env:PYTHONPATH
        PATH = $env:PATH
        VIRTUAL_ENV = $env:VIRTUAL_ENV
        CODEX_API_KEY = if ($env:CODEX_API_KEY) { "***REDACTED***" } else { $null }
        OPENAI_API_KEY = if ($env:OPENAI_API_KEY) { "***REDACTED***" } else { $null }
        ODDS_API_KEY = if ($env:ODDS_API_KEY) { "***REDACTED***" } else { $null }
    }
    
    $envVars | ConvertTo-Json -Depth 3 | Set-Content -Path (Join-Path $envBackupDir "environment_variables.json") -Encoding UTF8
    
    $manifest.BackupItems += "environment"
    Write-SnapshotLog "Environment variables backed up (secrets redacted)" "SUCCESS"
    
    # ----------------------------------------------------------------
    # 6. Backup key configuration files
    # ----------------------------------------------------------------
    Write-Host "`n[6/7] Backing up configuration files..." -ForegroundColor Yellow
    
    $configBackupDir = Join-Path $snapshotDir "configs"
    New-Item -ItemType Directory -Path $configBackupDir -Force | Out-Null
    
    $configFiles = @(
        "C:\EQ12\pyproject.toml",
        "C:\EQ12\setup.py",
        "C:\EQ12\.gitignore",
        "C:\EQ12\.env.example",
        "C:\EQ12\docker-compose.yml",
        "C:\EQ12\.devcontainer\devcontainer.json"
    )
    
    foreach ($configFile in $configFiles) {
        if (Test-Path $configFile) {
            $fileName = Split-Path $configFile -Leaf
            Copy-Item -Path $configFile -Destination (Join-Path $configBackupDir $fileName) -Force
        }
    }
    
    $manifest.BackupItems += "configs"
    Write-SnapshotLog "Configuration files backed up" "SUCCESS"
    
    # ----------------------------------------------------------------
    # 7. Save manifest
    # ----------------------------------------------------------------
    Write-Host "`n[7/7] Saving snapshot manifest..." -ForegroundColor Yellow
    
    $manifestPath = Join-Path $snapshotDir "manifest.json"
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8
    
    Write-SnapshotLog "Snapshot manifest saved" "SUCCESS"
    
    # ----------------------------------------------------------------
    # Summary
    # ----------------------------------------------------------------
    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host " SNAPSHOT CREATED SUCCESSFULLY" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Snapshot ID: $snapshotId" -ForegroundColor Green
    Write-Host "Location: $snapshotDir" -ForegroundColor White
    Write-Host "Backed up: $($manifest.BackupItems -join ', ')" -ForegroundColor White
    
    $snapshotSizeMB = [math]::Round((Get-ChildItem $snapshotDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
    Write-Host "Size: $snapshotSizeMB MB" -ForegroundColor White
    Write-Host ""
    Write-Host "To restore this snapshot later, run:" -ForegroundColor Cyan
    Write-Host "  .\EQ12_BACKUP_SNAPSHOT.ps1 -Restore -SnapshotId '$snapshotId'" -ForegroundColor White
    Write-Host ""
}

function Restore-Snapshot {
    param([string]$SnapshotId)
    
    Write-Host "`n=== EQ12 SNAPSHOT RESTORE ===" -ForegroundColor Cyan
    Write-Host "Restoring snapshot: $SnapshotId" -ForegroundColor Yellow
    Write-Host ""
    
    $snapshotDir = Join-Path $BackupRoot $SnapshotId
    
    if (-not (Test-Path $snapshotDir)) {
        Write-SnapshotLog "Snapshot not found: $SnapshotId" "ERROR"
        Write-Host ""
        Write-Host "Available snapshots:" -ForegroundColor Cyan
        Show-SnapshotList
        return
    }
    
    # Load manifest
    $manifestPath = Join-Path $snapshotDir "manifest.json"
    if (-not (Test-Path $manifestPath)) {
        Write-SnapshotLog "Snapshot manifest missing. Snapshot may be corrupted." "ERROR"
        return
    }
    
    $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
    
    Write-Host "Snapshot Details:" -ForegroundColor White
    Write-Host "  Label: $($manifest.Label)" -ForegroundColor DarkGray
    Write-Host "  Timestamp: $($manifest.Timestamp)" -ForegroundColor DarkGray
    Write-Host "  Items: $($manifest.BackupItems -join ', ')" -ForegroundColor DarkGray
    Write-Host ""
    
    Write-Host "⚠️ WARNING: This will overwrite current configuration!" -ForegroundColor Red
    Write-Host ""
    $confirm = Read-Host "Type 'YES' to confirm restore"
    
    if ($confirm -ne "YES") {
        Write-SnapshotLog "Restore cancelled by user" "WARNING"
        return
    }
    
    # ----------------------------------------------------------------
    # Restore .vscode
    # ----------------------------------------------------------------
    if ("vscode" -in $manifest.BackupItems) {
        Write-Host "`n[1/4] Restoring .vscode configuration..." -ForegroundColor Yellow
        
        $vscodeBackup = Join-Path $snapshotDir "vscode"
        if (Test-Path $vscodeBackup) {
            $vscodeTarget = "C:\EQ12\.vscode"
            
            # Backup current before overwriting
            if (Test-Path $vscodeTarget) {
                $tempBackup = "C:\EQ12\.vscode.before_restore_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                Move-Item -Path $vscodeTarget -Destination $tempBackup -Force
                Write-SnapshotLog "Current .vscode backed up to: $tempBackup" "INFO"
            }
            
            Copy-Item -Path $vscodeBackup -Destination $vscodeTarget -Recurse -Force
            Write-SnapshotLog ".vscode configuration restored" "SUCCESS"
        }
    }
    
    # ----------------------------------------------------------------
    # Restore Python environment (info only, requires manual rebuild)
    # ----------------------------------------------------------------
    if ("python" -in $manifest.BackupItems) {
        Write-Host "`n[2/4] Python environment information..." -ForegroundColor Yellow
        
        $pythonBackup = Join-Path $snapshotDir "python"
        if (Test-Path "$pythonBackup\pip_freeze.txt") {
            Write-SnapshotLog "Python dependencies snapshot available" "INFO"
            Write-Host "  To restore Python environment, run:" -ForegroundColor Cyan
            Write-Host "    .\.venv\Scripts\activate" -ForegroundColor White
            Write-Host "    pip install -r `"$pythonBackup\requirements.txt`"" -ForegroundColor White
        }
    }
    
    # ----------------------------------------------------------------
    # Restore Git state (info only)
    # ----------------------------------------------------------------
    if ("git" -in $manifest.BackupItems) {
        Write-Host "`n[3/4] Git repository information..." -ForegroundColor Yellow
        
        $gitBackup = Join-Path $snapshotDir "git"
        if (Test-Path "$gitBackup\current_branch.txt") {
            $originalBranch = Get-Content "$gitBackup\current_branch.txt" -Raw
            Write-SnapshotLog "Original branch: $originalBranch" "INFO"
            Write-Host "  Git state information available in: $gitBackup" -ForegroundColor Cyan
        }
    }
    
    # ----------------------------------------------------------------
    # Restore configuration files
    # ----------------------------------------------------------------
    if ("configs" -in $manifest.BackupItems) {
        Write-Host "`n[4/4] Restoring configuration files..." -ForegroundColor Yellow
        
        $configBackup = Join-Path $snapshotDir "configs"
        if (Test-Path $configBackup) {
            $configFiles = Get-ChildItem -Path $configBackup -File
            foreach ($configFile in $configFiles) {
                $targetPath = "C:\EQ12\$($configFile.Name)"
                Copy-Item -Path $configFile.FullName -Destination $targetPath -Force
                Write-SnapshotLog "Restored: $($configFile.Name)" "SUCCESS"
            }
        }
    }
    
    # ----------------------------------------------------------------
    # Summary
    # ----------------------------------------------------------------
    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host " SNAPSHOT RESTORE COMPLETE" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✔ Configuration files restored from snapshot: $SnapshotId" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️ NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "  1. Restart VS Code to apply restored settings" -ForegroundColor White
    Write-Host "  2. Rebuild Python venv if needed (see instructions above)" -ForegroundColor White
    Write-Host "  3. Verify Git branch and uncommitted changes" -ForegroundColor White
    Write-Host "  4. Run: .\EQ12_POST_RESET_CHECKLIST.ps1 to verify health" -ForegroundColor White
    Write-Host ""
}

# ----------------------------------------------------------------
# MAIN EXECUTION
# ----------------------------------------------------------------

if ($ListSnapshots) {
    Show-SnapshotList
}
elseif ($Restore) {
    if (-not $SnapshotId) {
        Write-Host "❌ -SnapshotId required for restore operation" -ForegroundColor Red
        Write-Host ""
        Show-SnapshotList
    } else {
        Restore-Snapshot -SnapshotId $SnapshotId
    }
}
else {
    New-Snapshot -Label $Label
}
