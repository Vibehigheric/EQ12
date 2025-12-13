$sourceDirs = @(
    "C:\EQ12",
    "C:\EQ12_BACKUP_20251127_110157",
    "C:\EQ12_BROKEN_20251122_210342",
    "C:\EQ12_v2"
)

$destDir = "C:\EQ12_BROKEN_20251122_210342\betting_engine_v1\data\legacy_import"
$reportFile = "C:\EQ12_BROKEN_20251122_210342\betting_engine_v1\docs\LEGACY_IMPORT_REPORT.md"

# Create destination directory
New-Item -ItemType Directory -Force -Path $destDir | Out-Null

# Keywords to search for
$keywords = @("bet", "odds", "parlay", "ev", "sport", "nba", "nfl", "mlb", "nhl", "sgp")

$foundFiles = @()

"Scanning for betting engines..."
foreach ($dir in $sourceDirs) {
    if (Test-Path $dir) {
        Write-Host "Scanning $dir..."
        
        # Get all files recursively
        $files = Get-ChildItem -Path $dir -Recurse -File -ErrorAction SilentlyContinue
        
        foreach ($file in $files) {
            $match = $false
            foreach ($kw in $keywords) {
                if ($file.Name -match $kw) {
                    $match = $true
                    break
                }
            }
            
            if ($match) {
                # Avoid copying files from the destination itself or the .git folder
                if ($file.FullName -notlike "*$destDir*" -and $file.FullName -notlike "*.git*") {
                    $foundFiles += $file
                    
                    # Copy to legacy import folder with a prefix to avoid collisions
                    $prefix = $dir.Split("\")[-1]
                    $newFileName = "${prefix}_" + $file.Name
                    $destPath = Join-Path $destDir $newFileName
                    
                    Copy-Item -Path $file.FullName -Destination $destPath -Force
                    Write-Host "  Found: $($file.Name)"
                }
            }
        }
    }
    else {
        Write-Host "Directory not found: $dir"
    }
}

# Generate Report
$reportContent = "# Legacy Betting Engine Import Report`n`n"
$reportContent += "Date: $(Get-Date)`n"
$reportContent += "Total Files Found: $($foundFiles.Count)`n`n"
$reportContent += "| Original Location | File Name | Size (KB) | Last Modified |`n"
$reportContent += "|---|---|---|---|`n"

foreach ($file in $foundFiles) {
    $sizeKB = [math]::Round($file.Length / 1KB, 2)
    $reportContent += "| $($file.DirectoryName) | $($file.Name) | $sizeKB | $($file.LastWriteTime) |`n"
}

Set-Content -Path $reportFile -Value $reportContent
Write-Host "Import complete. Report saved to $reportFile"
