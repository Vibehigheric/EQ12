[CmdletBinding()]
param()

Write-Host "[DISCOVERY] EQ12 PROGRAM DISCOVERY" -ForegroundColor Green
Write-Host "=" * 40 -ForegroundColor Green

# Option 7: Program Discovery with proper error handling
try {
    $pyFiles = Get-ChildItem -Path "C:\EQ12" -Recurse -Filter "*.py" -ErrorAction SilentlyContinue | Select-Object -First 10 -ExpandProperty Name
    $ps1Files = Get-ChildItem -Path "C:\EQ12" -Recurse -Filter "*.ps1" -ErrorAction SilentlyContinue | Select-Object -First 10 -ExpandProperty Name

    Write-Host "`nPython Scripts (Top 10):" -ForegroundColor Cyan
    if ($pyFiles) {
        $pyFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }
    } else {
        Write-Host "  No Python files found" -ForegroundColor Gray
    }

    Write-Host "`nPowerShell Scripts (Top 10):" -ForegroundColor Yellow
    if ($ps1Files) {
        $ps1Files | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }
    } else {
        Write-Host "  No PowerShell files found" -ForegroundColor Gray
    }
} catch {
    Write-Host "Error during program discovery: $($_.Exception.Message)" -ForegroundColor Red
}

# Option 8: System Statistics with proper variable handling
try {
    Write-Host "`n[STATISTICS] EQ12 SYSTEM STATISTICS" -ForegroundColor Green
    Write-Host "=" * 40 -ForegroundColor Green

    $allFiles = Get-ChildItem -Path "C:\EQ12" -Recurse -File -ErrorAction SilentlyContinue
    $allDirs = Get-ChildItem -Path "C:\EQ12" -Recurse -Directory -ErrorAction SilentlyContinue

    $totalFiles = ($allFiles | Measure-Object).Count
    $totalDirs = ($allDirs | Measure-Object).Count
    $totalSize = ($allFiles | Measure-Object -Property Length -Sum).Sum

    Write-Host "Total Files: $totalFiles" -ForegroundColor White
    Write-Host "Total Directories: $totalDirs" -ForegroundColor White
    Write-Host "Total Size: $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor White
    Write-Host "Scan Time: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
} catch {
    Write-Host "Error during statistics collection: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n[COMPLETE] Discovery and statistics scan finished!" -ForegroundColor Green