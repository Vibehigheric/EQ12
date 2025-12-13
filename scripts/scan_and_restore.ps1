
param(
    [string]$BackupPath = "C:\EQ12_BACKUP_20251127_110157",
    [string]$RestorePath = "C:\EQ12_BROKEN_20251122_210342\restored_from_backup"
)

$patterns = @(
    "*parlay*",
    "*bet*",
    "*nba*",
    "*inventory*",
    "*monitor*",
    "*orchestrator*",
    "*dashboard*",
    "*intelligence*",
    "*scraper*",
    "*vpn*"
)

Write-Host "Scanning $BackupPath for useful files..."

$foundFiles = Get-ChildItem -Path $BackupPath -Recurse | Where-Object {
    $file = $_
    $patterns | Where-Object { $file.Name -like $_ }
}

$report = @()

foreach ($file in $foundFiles) {
    # Try to determine original name by removing the timestamp and .backup extension
    # Format seems to be: original_name.ext_YYYYMMDD_HHMMSS.backup
    # Or: original_name_YYYYMMDD_HHMMSS.backup
    
    $originalName = $file.Name -replace '_\d{8}_\d{6}\.backup$', ''
    $originalName = $originalName -replace '\.backup$', '' # Fallback
    
    $destPath = Join-Path $RestorePath $originalName
    
    if (-not (Test-Path $destPath)) {
        Copy-Item -Path $file.FullName -Destination $destPath
        $report += [PSCustomObject]@{
            OriginalFile = $file.Name
            RestoredAs   = $originalName
            Status       = "Restored"
        }
        Write-Host "Restored: $($file.Name) -> $originalName"
    }
    else {
        $report += [PSCustomObject]@{
            OriginalFile = $file.Name
            RestoredAs   = $originalName
            Status       = "Skipped (Exists)"
        }
        Write-Host "Skipped: $originalName (already exists)"
    }
}

$report | Format-Table -AutoSize
