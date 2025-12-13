# EQ12 Global PowerShell Repair Engine v2.0
# Ultra-simple version without complex syntax

param(
    [string]$RootPath = "C:\EQ12"
)

Write-Host "EQ12 GLOBAL POWERSHELL REPAIR ENGINE v2.0" -ForegroundColor Cyan
Write-Host "Scanning: $RootPath" -ForegroundColor Yellow

$files = Get-ChildItem -Path $RootPath -Recurse -Filter *.ps1
$totalFixed = 0
$filesProcessed = 0

Write-Host "Found $($files.Count) PowerShell files to process" -ForegroundColor Green

foreach ($file in $files) {
    $filesProcessed++
    Write-Host "`nProcessing: $($file.Name)" -ForegroundColor White

    $raw = Get-Content -Raw $file.FullName
    $original = $raw

    # Step 1: Remove non-ASCII characters
    $clean = $raw -replace '[^\x20-\x7E\r\n\t]', ''

    # Step 2: Fix smart quotes and dashes
    $clean = $clean -replace '[""]', '"'
    $clean = $clean -replace '['']', "'"
    $clean = $clean -replace '[]', '-'

    # Step 3: Balance braces
    $openBraces = ($clean.ToCharArray() | Where-Object { $_ -eq '{' }).Count
    $closeBraces = ($clean.ToCharArray() | Where-Object { $_ -eq '}' }).Count

    if ($openBraces -gt $closeBraces) {
        $missing = $openBraces - $closeBraces
        $clean = $clean + ("`n" + "}" * $missing)
        Write-Host "  Added $missing missing closing braces" -ForegroundColor Yellow
    }

    # Only save if changes were made
    if ($raw -ne $clean) {
        $backupPath = $file.FullName + ".backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item $file.FullName $backupPath

        [System.IO.File]::WriteAllText($file.FullName, $clean, [System.Text.UTF8Encoding]($false))

        Write-Host "  REPAIRED and backed up" -ForegroundColor Green
        $totalFixed++
    } else {
        Write-Host "  Already clean" -ForegroundColor Gray
    }
}

Write-Host "`nREPAIR COMPLETE!" -ForegroundColor Cyan
Write-Host "Files processed: $filesProcessed" -ForegroundColor White
Write-Host "Files repaired: $totalFixed" -ForegroundColor Green

# Test critical scripts
$criticalScripts = @(
    "$RootPath\scripts\eq12_5usb_system_validator.ps1",
    "$RootPath\scripts\eq12_self_healing_v5_wrapper.ps1"
)

Write-Host "`nTesting critical scripts..." -ForegroundColor Cyan
foreach ($script in $criticalScripts) {
    if (Test-Path $script) {
        Write-Host "Found: $(Split-Path $script -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "Missing: $(Split-Path $script -Leaf)" -ForegroundColor Red
    }
}
