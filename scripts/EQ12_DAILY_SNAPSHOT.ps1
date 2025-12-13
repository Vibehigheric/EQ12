# ==================================================================
# EQ12 DAILY SNAPSHOT - Automated Backup System
# ==================================================================
# Creates daily ZIP backups of your EQ12 workspace
# Automatically rotates old backups (keeps last 7 days)
# Run via Task Scheduler for daily automation
# ==================================================================

[CmdletBinding()]
param(
    [string]$Source = "C:\EQ12",
    [string]$BackupRoot = "C:\EQ12\backups",
    [int]$RetentionDays = 7
)

Write-Host "`n=== EQ12 DAILY SNAPSHOT ===" -ForegroundColor Cyan
Write-Host "Creating backup of workspace..." -ForegroundColor Yellow
Write-Host ""

$Date = Get-Date -Format "yyyyMMdd_HHmmss"
$ZipPath = "$BackupRoot\EQ12_SNAPSHOT_$Date.zip"

# Ensure backup directory exists
if (-not (Test-Path $BackupRoot)) {
    New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
    Write-Host "Created backup directory: $BackupRoot" -ForegroundColor Green
}

# Check source exists
if (-not (Test-Path $Source)) {
    Write-Host "ERROR: Source directory not found: $Source" -ForegroundColor Red
    exit 1
}

# Create backup
try {
    Write-Host "Compressing workspace to: $ZipPath" -ForegroundColor White
    
    # Exclude large/unnecessary directories from backup
    $TempSource = "$env:TEMP\EQ12_BACKUP_TEMP"
    if (Test-Path $TempSource) {
        Remove-Item -Path $TempSource -Recurse -Force
    }
    
    # Copy source excluding problematic directories
    $ExcludeDirs = @('.git', 'node_modules', '.venv', '__pycache__', 'dist', 'build', '.pytest_cache', '.ruff_cache')
    
    Write-Host "  Copying files (excluding: $($ExcludeDirs -join ', '))..." -ForegroundColor DarkGray
    
    robocopy $Source $TempSource /E /XD $ExcludeDirs /NFL /NDL /NJH /NJS /NC /NS /NP | Out-Null
    
    # Create ZIP
    Compress-Archive -Path "$TempSource\*" -DestinationPath $ZipPath -CompressionLevel Optimal -Force
    
    # Cleanup temp
    Remove-Item -Path $TempSource -Recurse -Force -ErrorAction SilentlyContinue
    
    $sizeM B = [math]::Round((Get-Item $ZipPath).Length / 1MB, 2)
    Write-Host "  SUCCESS: Backup created ($sizeMB MB)" -ForegroundColor Green
    
} catch {
    Write-Host "ERROR: Backup failed - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Rotate old backups
Write-Host ""
Write-Host "Rotating old backups (keeping last $RetentionDays days)..." -ForegroundColor Yellow

$AllBackups = Get-ChildItem -Path $BackupRoot -Filter "EQ12_SNAPSHOT_*.zip" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending

if ($AllBackups.Count -gt $RetentionDays) {
    $ToRemove = $AllBackups | Select-Object -Skip $RetentionDays
    foreach ($oldBackup in $ToRemove) {
        Write-Host "  Removing old backup: $($oldBackup.Name)" -ForegroundColor DarkGray
        Remove-Item -Path $oldBackup.FullName -Force
    }
    Write-Host "  Removed $($ToRemove.Count) old backup(s)" -ForegroundColor Yellow
} else {
    Write-Host "  No old backups to remove (have $($AllBackups.Count) of $RetentionDays max)" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " SNAPSHOT COMPLETE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backup location: $ZipPath" -ForegroundColor Green
Write-Host "Backup size: $sizeMB MB" -ForegroundColor White
Write-Host "Total backups retained: $($AllBackups.Count)" -ForegroundColor White
Write-Host ""
Write-Host "To restore this backup, run:" -ForegroundColor Cyan
Write-Host "  .\EQ12_RESTORE_SNAPSHOT.ps1 -BackupZip '$ZipPath'" -ForegroundColor White
Write-Host ""

# Automation instructions
if (-not (Get-ScheduledTask -TaskName "EQ12 Daily Snapshot" -ErrorAction SilentlyContinue)) {
    Write-Host "=== AUTOMATION SETUP ===" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To run this backup daily automatically:" -ForegroundColor White
    Write-Host ""
    Write-Host "1. Open PowerShell as Administrator" -ForegroundColor Cyan
    Write-Host "2. Run the following command:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "schtasks /create /sc daily /tn `"EQ12 Daily Snapshot`" /tr `"powershell -ExecutionPolicy Bypass -File C:\EQ12\scripts\EQ12_DAILY_SNAPSHOT.ps1`" /st 09:00" -ForegroundColor White
    Write-Host ""
}
