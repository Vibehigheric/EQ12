# ==================================================================
# EQ12 RESTORE SNAPSHOT - Restore from Backup
# ==================================================================
# Restores your EQ12 workspace from a snapshot ZIP file
# DESTRUCTIVE: Deletes current C:\EQ12 and replaces with backup
# ==================================================================

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$BackupZip,
    
    [string]$RestoreLocation = "C:\EQ12",
    
    [switch]$Force
)

Write-Host "`n=== EQ12 RESTORE SNAPSHOT ===" -ForegroundColor Cyan
Write-Host ""

# Validate backup exists
if (-not (Test-Path $BackupZip)) {
    Write-Host "ERROR: Backup file not found: $BackupZip" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available backups:" -ForegroundColor Cyan
    $backups = Get-ChildItem -Path "C:\EQ12\backups" -Filter "*.zip" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    if ($backups) {
        $backups | ForEach-Object {
            $age = (Get-Date) - $_.LastWriteTime
            Write-Host "  - $($_.Name) ($($ ([math]::Round($age.TotalDays, 1)) days old)" -ForegroundColor White
        }
    } else {
        Write-Host "  No backups found" -ForegroundColor DarkGray
    }
    exit 1
}

# Show backup info
$backupInfo = Get-Item $BackupZip
$sizeMB = [math]::Round($backupInfo.Length / 1MB, 2)
Write-Host "Backup file: $($backupInfo.Name)" -ForegroundColor White
Write-Host "Size: $sizeMB MB" -ForegroundColor White
Write-Host "Created: $($backupInfo.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor White
Write-Host ""

# Safety check
if (-not $Force) {
    Write-Host "WARNING: This will DELETE the current workspace and restore from backup!" -ForegroundColor Red
    Write-Host "Current location: $RestoreLocation" -ForegroundColor Yellow
    Write-Host ""
    $confirm = Read-Host "Type 'YES' to confirm restore"
    
    if ($confirm -ne 'YES') {
        Write-Host "Restore cancelled." -ForegroundColor Yellow
        exit 0
    }
}

# Delete current workspace
Write-Host ""
Write-Host "Deleting current workspace: $RestoreLocation" -ForegroundColor Yellow

if (Test-Path $RestoreLocation) {
    try {
        # Remove read-only attributes
        & attrib -r "$RestoreLocation\*" /S /D 2>$null
        
        # Remove directory
        Remove-Item -Path $RestoreLocation -Recurse -Force -ErrorAction Stop
        Write-Host "  Workspace deleted" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to delete workspace - $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  Try closing VS Code and running again" -ForegroundColor Cyan
        exit 1
    }
} else {
    Write-Host "  Workspace does not exist (will create fresh)" -ForegroundColor DarkGray
}

# Restore backup
Write-Host ""
Write-Host "Restoring backup..." -ForegroundColor Yellow

try {
    # Create restore location
    New-Item -ItemType Directory -Path $RestoreLocation -Force | Out-Null
    
    # Extract ZIP
    Expand-Archive -Path $BackupZip -DestinationPath $RestoreLocation -Force
    
    Write-Host "  Backup restored successfully" -ForegroundColor Green
    
} catch {
    Write-Host "ERROR: Restore failed - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Verify restoration
Write-Host ""
Write-Host "Verifying restoration..." -ForegroundColor Yellow

$criticalPaths = @(
    "$RestoreLocation\.vscode\settings.json",
    "$RestoreLocation\scripts",
    "$RestoreLocation\.github"
)

$allGood = $true
foreach ($path in $criticalPaths) {
    if (Test-Path $path) {
        Write-Host "  OK: $path" -ForegroundColor Green
    } else {
        Write-Host "  MISSING: $path" -ForegroundColor Red
        $allGood = $false
    }
}

# Summary
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " RESTORE COMPLETE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if ($allGood) {
    Write-Host "STATUS: SUCCESS" -ForegroundColor Green
    Write-Host "Workspace restored to: $RestoreLocation" -ForegroundColor White
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Rebuild Python venv:" -ForegroundColor White
    Write-Host "   cd $RestoreLocation" -ForegroundColor Cyan
    Write-Host "   python -m venv .venv" -ForegroundColor Cyan
    Write-Host "   .\.venv\Scripts\activate" -ForegroundColor Cyan
    Write-Host "   pip install -r requirements.txt" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Restart VS Code" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Run post-restore checklist:" -ForegroundColor White
    Write-Host "   .\scripts\EQ12_POST_RESET_CHECKLIST.ps1" -ForegroundColor Cyan
} else {
    Write-Host "STATUS: INCOMPLETE" -ForegroundColor Red
    Write-Host "Some critical files are missing. Backup may be corrupted." -ForegroundColor Red
}

Write-Host ""
