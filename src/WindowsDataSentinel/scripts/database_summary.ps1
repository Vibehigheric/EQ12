<#
.SYNOPSIS
    Windows Data Sentinel - Database Summary Report

.DESCRIPTION
    Generates summary statistics from the SQLite database
    Shows item counts by category, source, and recent activity

.EXAMPLE
    .\database_summary.ps1
#>

[CmdletBinding()]
param()

$dbPath = "C:\EQ12\WindowsDataSentinel\data\eq12_sentinel.db"

if (-not (Test-Path $dbPath)) {
    Write-Error "Database not found: $dbPath"
    exit 1
}

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Windows Data Sentinel - Database Summary" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Database file info
$dbInfo = Get-Item $dbPath
Write-Host "Database File:" -ForegroundColor Yellow
Write-Host "  Path: $dbPath"
Write-Host "  Size: $([math]::Round($dbInfo.Length / 1KB, 2)) KB"
Write-Host "  Last Modified: $($dbInfo.LastWriteTime)"
Write-Host ""

# Total items
$totalItems = sqlite3 $dbPath "SELECT COUNT(*) FROM Items"
Write-Host "Total Items: " -NoNewline -ForegroundColor Yellow
Write-Host $totalItems -ForegroundColor Green
Write-Host ""

# Items by category
Write-Host "Items by Category:" -ForegroundColor Yellow
$categoryStats = sqlite3 $dbPath "SELECT Category, COUNT(*) FROM Items GROUP BY Category ORDER BY COUNT(*) DESC"
foreach ($line in $categoryStats) {
    $parts = $line.Split("|")
    $category = $parts[0].PadRight(15)
    $count = $parts[1].PadLeft(4)
    Write-Host "  $category : $count items" -ForegroundColor Cyan
}
Write-Host ""

# Items by source
Write-Host "Items by Source:" -ForegroundColor Yellow
$sourceStats = sqlite3 $dbPath "SELECT SourceName, COUNT(*) FROM Items GROUP BY SourceName ORDER BY COUNT(*) DESC LIMIT 10"
foreach ($line in $sourceStats) {
    $parts = $line.Split("|")
    $source = $parts[0].PadRight(30)
    $count = $parts[1].PadLeft(4)
    Write-Host "  $source : $count items" -ForegroundColor Cyan
}
Write-Host ""

# Recent items (last 5)
Write-Host "Recent Items:" -ForegroundColor Yellow
$recentItems = sqlite3 $dbPath "SELECT SourceName, Title, PublishedUtc FROM Items ORDER BY InsertedUtc DESC LIMIT 5"
foreach ($line in $recentItems) {
    $parts = $line.Split("|")
    if ($parts.Length -ge 2) {
        $source = $parts[0]
        $title = if ($parts[1].Length -gt 60) { $parts[1].Substring(0, 57) + "..." } else { $parts[1] }
        Write-Host "  [$source]" -ForegroundColor Yellow -NoNewline
        Write-Host " $title" -ForegroundColor White
    }
}
Write-Host ""

# Oldest and newest published dates
$dateRange = sqlite3 $dbPath "SELECT MIN(PublishedUtc) as oldest, MAX(PublishedUtc) as newest FROM Items WHERE PublishedUtc IS NOT NULL"
if ($dateRange) {
    $parts = $dateRange.Split("|")
    Write-Host "Date Range:" -ForegroundColor Yellow
    Write-Host "  Oldest: $($parts[0])" -ForegroundColor Cyan
    Write-Host "  Newest: $($parts[1])" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "=" * 70 -ForegroundColor Cyan
