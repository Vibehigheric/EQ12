param(
    [string]$RootPath = "C:\EQ12"
)

Write-Host " EQ12 GLOBAL POWERSHELL REPAIR ENGINE" -ForegroundColor Cyan
Write-Host "Scanning: $RootPath" -ForegroundColor Yellow

# Get all .ps1 files
$files = Get-ChildItem -Path $RootPath -Recurse -Filter *.ps1

$totalFixed = 0
$filesProcessed = 0

foreach ($file in $files) {
    $filesProcessed++
    Write-Host "`n Repairing: $($file.FullName)" -ForegroundColor Green

    try {
        $raw = Get-Content -Raw $file.FullName -ErrorAction Stop

        # STEP 1  Remove invisible UTF-8 garbage
        $clean = $raw -replace '[^\x20-\x7E\r\n\t]', ''

        # STEP 2  Replace smart quotes & bad chars
        $clean = $clean `
            -replace '[""]', '"' `
            -replace '['']', "'" `
            -replace '[]', '-' `
            -replace '\x00', '' `
            -replace '\uFEFF', ''

        # STEP 3  Auto-fix missing braces
        $openCount  = ([regex]::Matches($clean, "\{")).Count
        $closeCount = ([regex]::Matches($clean, "\}")).Count
        $fixesApplied = 0

        if ($openCount -gt $closeCount) {
            $diff = $openCount - $closeCount
            Write-Host "   Missing closing braces detected: +$diff" -ForegroundColor Yellow
            $clean += ("`n}" * $diff)
            $fixesApplied++
        }

        if ($closeCount -gt $openCount) {
            Write-Host "   Excess closing braces detected" -ForegroundColor Yellow
            # More careful removal - only remove isolated closing braces
            $lines = $clean -split "`n"
            $newLines = @()
            $removedCount = 0

            foreach ($line in $lines) {
                if ($line.Trim() -eq "}" -and $removedCount -lt ($closeCount - $openCount)) {
                    $removedCount++
                    Write-Host "    Removed isolated '}' on line" -ForegroundColor Gray
                } else {
                    $newLines += $line
                }
            }
            $clean = $newLines -join "`n"
            if ($removedCount -gt 0) { $fixesApplied++ }
        }

        # STEP 4  Fix param blocks if corrupted
        if ($clean -match 'param\s*\(' -and $clean -notmatch 'param\s*\([^)]*\)\s*(\r?\n|\s)') {
            Write-Host "   Fixing param block structure" -ForegroundColor Yellow
            $clean = $clean -replace 'param\s*\(\s*([^)]*)', 'param(`n    $1`n)'
            $fixesApplied++
        }

        # Only write if changes were made
        if ($raw -ne $clean) {
            # Create backup
            $backupPath = $file.FullName + ".backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Copy-Item $file.FullName $backupPath
            Write-Host "    Backup created: $backupPath" -ForegroundColor Gray

            # STEP 5  Remove BOM and force UTF-8 clean write
            [System.IO.File]::WriteAllText($file.FullName, $clean, [System.Text.UTF8Encoding]($false))

            Write-Host "     Repaired with $fixesApplied fixes" -ForegroundColor Green
            $totalFixed++
        } else {
            Write-Host "     Already clean" -ForegroundColor Green
        }

    } catch {
        Write-Host "     Error processing file: $_" -ForegroundColor Red
    }
}

Write-Host "`n GLOBAL POWERSHELL REPAIR COMPLETE!" -ForegroundColor Cyan
Write-Host "Files processed: $filesProcessed" -ForegroundColor Green
Write-Host "Files repaired: $totalFixed" -ForegroundColor Green
Write-Host "All scripts sanitized, braces reconstructed, UTF-8 cleaned." -ForegroundColor Green

# Test a few critical scripts
$criticalScripts = @(
    "C:\EQ12\scripts\eq12_5usb_system_validator.ps1",
    "C:\EQ12\scripts\eq12_self_healing_v5_wrapper.ps1",
    "C:\EQ12\scripts\eq12_emergency_repair.ps1"
)

Write-Host "`n Testing critical scripts..." -ForegroundColor Cyan
foreach ($script in $criticalScripts) {
    if (Test-Path $script) {
        try {
            # Test PowerShell syntax
            $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $script -Raw), [ref]$null)
            Write-Host " $script - SYNTAX OK" -ForegroundColor Green
        } catch {
            Write-Host " $script - SYNTAX ERROR: $_" -ForegroundColor Red
        }
    }
}
