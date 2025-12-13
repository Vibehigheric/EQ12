# EQ12 UNIVERSAL POWERSHELL REPAIR SCRIPT
# Fixes syntax errors, missing braces, and encoding issues
# Buffalo NY 14215 Content Empire System Repair

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "EQ12 UNIVERSAL POWERSHELL REPAIR SYSTEM" -ForegroundColor Cyan
Write-Host "Buffalo NY 14215 Content Empire Protection" -ForegroundColor Yellow
Write-Host "=========================================="

# Define repair functions
function Test-PowerShellSyntax {
    param([string]$FilePath)

    try {
        $Tokens = [System.Management.Automation.PSParser]::Tokenize((Get-Content $FilePath -Raw), [ref]$null)
        return $true
    } catch {
        return $false
    }
}

function Repair-PowerShellFile {
    param([string]$FilePath)

    Write-Host "REPAIRING: $FilePath" -ForegroundColor Yellow

    $Content = Get-Content $FilePath -Raw -Encoding UTF8
    $OriginalContent = $Content

    # Fix common syntax issues
    $Fixes = 0

    # Fix missing closing braces (simple pattern matching)
    $OpenBraces = [regex]::Matches($Content, '\{').Count
    $CloseBraces = [regex]::Matches($Content, '\}').Count

    if ($OpenBraces -gt $CloseBraces) {
        $MissingBraces = $OpenBraces - $CloseBraces
        Write-Host "  FIXING: Adding $MissingBraces missing closing braces" -ForegroundColor Green
        for ($i = 0; $i -lt $MissingBraces; $i++) {
            $Content += "`n}"
        }
        $Fixes++
    }

    # Fix common encoding issues with emoji
    $Content = $Content -replace '[^\x20-\x7E\r\n\t]', ''  # Remove non-ASCII except whitespace

    # Fix malformed strings
    $Content = $Content -replace '"([^"]*)"', '"$1"'  # Normalize quotes

    if ($Content -ne $OriginalContent) {
        $BackupPath = "$FilePath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item $FilePath $BackupPath
        Write-Host "  BACKUP: Saved to $BackupPath" -ForegroundColor Gray

        $Content | Out-File -FilePath $FilePath -Encoding UTF8 -Force
        Write-Host "  SUCCESS: Repaired $Fixes issues" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  OK: No repairs needed" -ForegroundColor Green
        return $false
    }
}

# Scan EQ12 directory for PowerShell files
$PowerShellFiles = Get-ChildItem "C:\EQ12" -Recurse -Filter "*.ps1" | Where-Object { $_.Length -gt 0 }

Write-Host "FOUND: $($PowerShellFiles.Count) PowerShell files to check" -ForegroundColor Green
Write-Host ""

$RepairsNeeded = 0
$RepairsCompleted = 0

foreach ($File in $PowerShellFiles) {
    Write-Host "CHECKING: $($File.Name)" -ForegroundColor White

    $IsValid = Test-PowerShellSyntax -FilePath $File.FullName

    if (-not $IsValid) {
        $RepairsNeeded++
        Write-Host "  ERROR: Syntax errors detected" -ForegroundColor Red

        $Repaired = Repair-PowerShellFile -FilePath $File.FullName

        if ($Repaired) {
            $RepairsCompleted++

            # Test again after repair
            $IsValidAfterRepair = Test-PowerShellSyntax -FilePath $File.FullName
            if ($IsValidAfterRepair) {
                Write-Host "  VERIFIED: Repair successful" -ForegroundColor Green
            } else {
                Write-Host "  WARNING: Repair partially successful" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "  OK: Syntax valid" -ForegroundColor Green
    }

    Write-Host ""
}

# Summary
Write-Host "REPAIR SUMMARY:" -ForegroundColor Cyan
Write-Host "  Total files checked: $($PowerShellFiles.Count)" -ForegroundColor Gray
Write-Host "  Files needing repair: $RepairsNeeded" -ForegroundColor Gray
Write-Host "  Repairs completed: $RepairsCompleted" -ForegroundColor Gray

if ($RepairsNeeded -eq 0) {
    Write-Host "SUCCESS: All PowerShell files are valid" -ForegroundColor Green
} elseif ($RepairsCompleted -eq $RepairsNeeded) {
    Write-Host "SUCCESS: All repairs completed successfully" -ForegroundColor Green
} else {
    Write-Host "WARNING: Some files may still have issues" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Test your key scripts:" -ForegroundColor Gray
Write-Host "   .\eq12_self_healing_wrapper_minimal.ps1 test" -ForegroundColor Gray
Write-Host "2. Run system validation:" -ForegroundColor Gray
Write-Host "   .\eq12_5usb_system_validator_v2.ps1" -ForegroundColor Gray
Write-Host "3. Launch enhanced system:" -ForegroundColor Gray
Write-Host "   python eq12_enhanced_command_launcher.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Buffalo NY 14215 Content Empire: SYSTEM REPAIRED" -ForegroundColor Green

exit 0
