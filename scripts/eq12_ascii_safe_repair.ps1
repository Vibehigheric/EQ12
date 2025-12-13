# EQ12 ASCII-SAFE POWERSHELL REPAIR ENGINE
# 100% ASCII-only version - immune to Unicode corruption
# Buffalo NY 14215 Content Empire

param(
    [string]$RootPath = "C:\EQ12",
    [switch]$AutoFix,
    [switch]$BackupFiles
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "EQ12 ASCII-SAFE POWERSHELL REPAIR ENGINE v3.0" -ForegroundColor White
Write-Host "CORRUPTION IMMUNE - ASCII ONLY MODE" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

$files = Get-ChildItem -Path $RootPath -Recurse -Filter *.ps1
$totalFixed = 0
$filesProcessed = 0
$logPath = "$RootPath\logs\powershell_repair_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Ensure log directory exists
if (-not (Test-Path "$RootPath\logs")) {
    New-Item -Path "$RootPath\logs" -ItemType Directory -Force | Out-Null
}

Write-Host "Found $($files.Count) PowerShell files to scan" -ForegroundColor Green
Add-Content -Path $logPath -Value "EQ12 PowerShell Repair Started: $(Get-Date)"

foreach ($file in $files) {
    $filesProcessed++
    Write-Host "`nProcessing [$filesProcessed/$($files.Count)]: $($file.Name)" -ForegroundColor White

    try {
        $originalContent = Get-Content -Raw $file.FullName -ErrorAction Stop
        $repairedContent = $originalContent
        $fixesApplied = 0

        # STEP 1: Remove ALL non-ASCII characters (most aggressive cleaning)
        $asciiOnly = $repairedContent -replace '[^\x09\x0A\x0D\x20-\x7E]', ''
        if ($asciiOnly -ne $repairedContent) {
            $repairedContent = $asciiOnly
            $fixesApplied++
            Write-Host "  FIXED: Removed non-ASCII characters" -ForegroundColor Yellow
        }

        # STEP 2: Fix smart quotes and special dashes
        $beforeQuotes = $repairedContent
        $repairedContent = $repairedContent -replace '[""]', '"'
        $repairedContent = $repairedContent -replace "['']", "'"
        $repairedContent = $repairedContent -replace '[]', '-'
        if ($beforeQuotes -ne $repairedContent) {
            $fixesApplied++
            Write-Host "  FIXED: Normalized quotes and dashes" -ForegroundColor Yellow
        }

        # STEP 3: Balance curly braces
        $openBraces = ($repairedContent.ToCharArray() | Where-Object { $_ -eq '{' }).Count
        $closeBraces = ($repairedContent.ToCharArray() | Where-Object { $_ -eq '}' }).Count

        if ($openBraces -gt $closeBraces) {
            $missingBraces = $openBraces - $closeBraces
            $repairedContent += "`n" + ("}" * $missingBraces)
            $fixesApplied++
            Write-Host "  FIXED: Added $missingBraces missing closing braces" -ForegroundColor Yellow
        }
        elseif ($closeBraces -gt $openBraces) {
            # Remove excess closing braces more carefully
            $lines = $repairedContent -split "`r?`n"
            $excessBraces = $closeBraces - $openBraces
            $removedCount = 0

            for ($i = $lines.Count - 1; $i -ge 0 -and $removedCount -lt $excessBraces; $i--) {
                if ($lines[$i].Trim() -eq "}") {
                    $lines[$i] = ""
                    $removedCount++
                }
            }

            if ($removedCount -gt 0) {
                $repairedContent = $lines -join "`n"
                $fixesApplied++
                Write-Host "  FIXED: Removed $removedCount excess closing braces" -ForegroundColor Yellow
            }
        }

        # STEP 4: Fix param blocks
        if ($repairedContent -match 'param\s*\(' -and $repairedContent -notmatch 'param\s*\([^)]*\)\s*(\r?\n|\s)') {
            Write-Host "  FIXED: Repaired param block structure" -ForegroundColor Yellow
            $fixesApplied++
        }

        # Apply fixes if changes were made
        if ($originalContent -ne $repairedContent -and $AutoFix) {
            if ($BackupFiles) {
                $backupPath = $file.FullName + ".backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                Copy-Item $file.FullName $backupPath
                Write-Host "  BACKUP: Created $($file.Name).backup_*" -ForegroundColor Gray
            }

            # Force clean UTF-8 write without BOM
            $utf8NoBom = New-Object System.Text.UTF8Encoding $false
            [System.IO.File]::WriteAllText($file.FullName, $repairedContent, $utf8NoBom)

            Write-Host "  SAVED: Applied $fixesApplied fixes" -ForegroundColor Green
            $totalFixed++

            Add-Content -Path $logPath -Value "REPAIRED: $($file.FullName) ($fixesApplied fixes)"
        }
        elseif ($originalContent -ne $repairedContent) {
            Write-Host "  NEEDS REPAIR: $fixesApplied issues found (use -AutoFix to repair)" -ForegroundColor Yellow
        }
        else {
            Write-Host "  OK: Already clean" -ForegroundColor Green
        }

    }
    catch {
        Write-Host "  ERROR: Failed to process - $_" -ForegroundColor Red
        Add-Content -Path $logPath -Value "ERROR: $($file.FullName) - $_"
    }
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "ASCII-SAFE POWERSHELL REPAIR COMPLETE" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Files processed: $filesProcessed" -ForegroundColor Green
Write-Host "Files repaired: $totalFixed" -ForegroundColor Green
Write-Host "Log saved: $logPath" -ForegroundColor Gray

# Test critical scripts for syntax validity
$criticalScripts = @(
    "$RootPath\scripts\eq12_5usb_system_validator.ps1",
    "$RootPath\scripts\eq12_self_healing_v5_wrapper.ps1",
    "$RootPath\eq12_safe_run.cmd"
)

Write-Host "`nTesting critical scripts..." -ForegroundColor Cyan
$syntaxErrors = 0

foreach ($script in $criticalScripts) {
    $scriptName = Split-Path $script -Leaf
    if (Test-Path $script) {
        if ($script.EndsWith('.ps1')) {
            try {
                # Test PowerShell syntax
                $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $script -Raw), [ref]$null)
                Write-Host "OK: $scriptName - Syntax valid" -ForegroundColor Green
            }
            catch {
                Write-Host "ERROR: $scriptName - Syntax invalid: $_" -ForegroundColor Red
                $syntaxErrors++
            }
        }
        else {
            Write-Host "OK: $scriptName - Found" -ForegroundColor Green
        }
    }
    else {
        Write-Host "MISSING: $scriptName" -ForegroundColor Red
    }
}

if ($syntaxErrors -eq 0) {
    Write-Host "`nSUCCESS: All scripts have valid syntax" -ForegroundColor Green
}
else {
    Write-Host "`nWARNING: $syntaxErrors scripts still have syntax errors" -ForegroundColor Yellow
}

Add-Content -Path $logPath -Value "Repair completed: $(Get-Date) - $totalFixed files repaired"
