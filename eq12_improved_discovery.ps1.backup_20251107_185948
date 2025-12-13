# EQ12 Improved Discovery Script
# Fixes for pipe element errors and UTF-8 encoding

[CmdletBinding()]
param()

Write-Host "EQ12 IMPROVED PROGRAM DISCOVERY" -ForegroundColor Cyan
Write-Host ("=" * 40) -ForegroundColor Gray

# Configure UTF-8 encoding
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    chcp 65001 | Out-Null
} catch {
    Write-Warning "Could not configure UTF-8 encoding"
}

# Safe file discovery avoiding pipe element errors
$pythonFiles = @()
$powershellFiles = @()
$totalSize = 0

try {
    Write-Host "Scanning EQ12 directory structure..." -ForegroundColor Yellow
    
    # Use Get-ChildItem with proper error handling
    $allFiles = Get-ChildItem -Path "C:\EQ12" -Recurse -File -ErrorAction SilentlyContinue
    
    foreach ($file in $allFiles) {
        $totalSize += $file.Length
        
        switch ($file.Extension.ToLower()) {
            ".py" { $pythonFiles += $file }
            ".ps1" { $powershellFiles += $file }
        }
    }
    
    # Display results with safe encoding
    Write-Host ""
    Write-Host "DISCOVERY RESULTS:" -ForegroundColor Green
    Write-Host "Python files found: $($pythonFiles.Count)" -ForegroundColor Cyan
    Write-Host "PowerShell files found: $($powershellFiles.Count)" -ForegroundColor Blue
    Write-Host "Total files scanned: $($allFiles.Count)" -ForegroundColor White
    Write-Host "Total size: $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor Yellow
    
    # Show top Python files
    if ($pythonFiles.Count -gt 0) {
        Write-Host ""
        Write-Host "Top Python Scripts:" -ForegroundColor Cyan
        $pythonFiles | Sort-Object Name | Select-Object -First 10 | ForEach-Object {
            Write-Host "  - $($_.Name)" -ForegroundColor Gray
        }
    }
    
    # Show top PowerShell files  
    if ($powershellFiles.Count -gt 0) {
        Write-Host ""
        Write-Host "Top PowerShell Scripts:" -ForegroundColor Blue
        $powershellFiles | Sort-Object Name | Select-Object -First 10 | ForEach-Object {
            Write-Host "  - $($_.Name)" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    Write-Host "Discovery completed successfully!" -ForegroundColor Green
    
} catch {
    Write-Error "Discovery failed: $_"
    exit 1
}
