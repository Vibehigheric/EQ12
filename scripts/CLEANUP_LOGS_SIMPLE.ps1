# EQ12 Simple Log Cleanup
# Archives old universal_repair logs, keeps most recent 50

$LogsDir = "C:\EQ12_BROKEN_20251122_210342\logs"
$ArchiveDir = Join-Path $LogsDir "archive"
$KeepRecent = 50

# Create archive directory
New-Item -Path $ArchiveDir -ItemType Directory -Force -ErrorAction SilentlyContinue | Out-Null

# Get all repair logs
$allLogs = Get-ChildItem -Path $LogsDir -Filter "universal_repair_*.log"

Write-Host "[INFO] Found $($allLogs.Count) universal_repair logs" -ForegroundColor Cyan

if ($allLogs.Count -le $KeepRecent) {
    Write-Host "[INFO] Only $($allLogs.Count) logs found, nothing to archive" -ForegroundColor Green
    exit 0
}

# Sort by date, keep most recent
$sortedLogs = $allLogs | Sort-Object LastWriteTime -Descending
$logsToKeep = $sortedLogs | Select-Object -First $KeepRecent
$logsToArchive = $sortedLogs | Select-Object -Skip $KeepRecent

Write-Host "[INFO] Archiving $($logsToArchive.Count) old logs..." -ForegroundColor Yellow

# Create zip archive
$archiveName = "universal_repair_archive_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
$archivePath = Join-Path $ArchiveDir $archiveName

try {
    Compress-Archive -Path $logsToArchive.FullName -DestinationPath $archivePath -CompressionLevel Optimal
    Write-Host "[OK] Created archive: $archivePath" -ForegroundColor Green
    
    # Delete original files
    $logsToArchive | Remove-Item -Force
    
    $totalSizeMB = [math]::Round(($logsToArchive | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
    Write-Host "[OK] Freed $totalSizeMB MB of disk space" -ForegroundColor Green
    Write-Host "[OK] Kept $KeepRecent most recent logs" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Archive failed: $_" -ForegroundColor Red
    exit 1
}
