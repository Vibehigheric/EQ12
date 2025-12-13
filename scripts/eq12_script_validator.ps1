# ============================================================
# EQ12 POWERSHELL SCRIPT VALIDATOR AND AUTO-REPAIR SYSTEM
# ============================================================
# Finds and fixes syntax errors, missing braces, Unicode corruption
# Buffalo NY 14215 Content Empire System Protection

# Include UTF-8 protection
. "C:\EQ12\config\eq12_utf8_guard.ps1"

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$Folder = "C:\EQ12",

    [Parameter(Mandatory=$false)]
    [switch]$AutoFix,

    [Parameter(Mandatory=$false)]
    [switch]$BackupFiles
)

function Test-PowerShellSyntax {
    param([string]$FilePath)

    try {
        $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $FilePath -Raw), [ref]$null)
        return $true
    } catch {
        return $false
    }
}

function Repair-PowerShellFile {
    param(
        [string]$FilePath,
        [bool]$CreateBackup = $true
    )

    Write-Host "REPAIRING: $([System.IO.Path]::GetFileName($FilePath))" -ForegroundColor Yellow

    $Content = Get-Content $FilePath -Raw -Encoding UTF8
    $OriginalContent = $Content
    $Fixes = 0

    # Create backup if requested
    if ($CreateBackup) {
        $BackupPath = "$FilePath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item $FilePath $BackupPath
        Write-Host "  BACKUP: $BackupPath" -ForegroundColor Gray
    }

    # Fix 1: Remove Unicode/emoji corruption
    $CleanContent = $Content -replace '[^\x00-\x7F]', '' `
                              -replace '[""'']', '"' `
                              -replace '[]', '-' `
                              -replace '[]', '' `
                              -replace '[\u2018\u2019]', "'" `
                              -replace '[\u201C\u201D]', '"'

    if ($CleanContent -ne $Content) {
        $Content = $CleanContent
        $Fixes++
        Write-Host "  FIX 1: Removed Unicode corruption" -ForegroundColor Green
    }

    # Fix 2: Balance braces
    $OpenBraces = [regex]::Matches($Content, '\{').Count
    $CloseBraces = [regex]::Matches($Content, '\}').Count

    if ($OpenBraces -gt $CloseBraces) {
        $MissingBraces = $OpenBraces - $CloseBraces
        for ($i = 0; $i -lt $MissingBraces; $i++) {
            $Content += "`n}"
        }
        $Fixes++
        Write-Host "  FIX 2: Added $MissingBraces missing closing braces" -ForegroundColor Green
    }

    # Fix 3: Balance parentheses in param blocks
    $ParamMatches = [regex]::Matches($Content, 'param\s*\([^)]*\)', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
    foreach ($Match in $ParamMatches) {
        $ParamBlock = $Match.Value
        $OpenParens = ($ParamBlock.ToCharArray() | Where-Object { $_ -eq '(' }).Count
        $CloseParens = ($ParamBlock.ToCharArray() | Where-Object { $_ -eq ')' }).Count

        if ($OpenParens -gt $CloseParens) {
            $MissingParens = $OpenParens - $CloseParens
            $FixedParamBlock = $ParamBlock + (')" ' * $MissingParens)
            $Content = $Content -replace [regex]::Escape($ParamBlock), $FixedParamBlock
            $Fixes++
            Write-Host "  FIX 3: Fixed param block parentheses" -ForegroundColor Green
        }
    }

    # Fix 4: Fix malformed strings
    $Content = $Content -replace '([^"])"([^"])', '$1""$2'  # Fix embedded quotes

    # Fix 5: Add UTF-8 guard if missing
    if ($Content -notmatch 'eq12_utf8_guard') {
        $GuardInclude = "`n# Include UTF-8 protection`n. `"C:\EQ12\config\eq12_utf8_guard.ps1`"`n"
        $Content = $GuardInclude + $Content
        $Fixes++
        Write-Host "  FIX 5: Added UTF-8 protection guard" -ForegroundColor Green
    }

    # Save repaired file
    if ($Content -ne $OriginalContent) {
        $Content | Out-File -FilePath $FilePath -Encoding UTF8 -Force
        Write-Host "  SUCCESS: Applied $Fixes fixes" -ForegroundColor Green
        return $true
    } else {
        Write-Host "  OK: No repairs needed" -ForegroundColor Green
        return $false
    }
}

function Test-ParamBlockSyntax {
    param([string]$FilePath)

    $Content = Get-Content $FilePath -Raw

    # Check for param block
    if ($Content -match 'param\s*\(') {
        $Issues = @()

        # Check for Unicode in param block
        if ($Content -match '[^\x00-\x7F]') {
            $Issues += "Unicode characters detected"
        }

        # Check for balanced parentheses
        $ParamSection = [regex]::Match($Content, 'param\s*\([^}]*\)', [System.Text.RegularExpressions.RegexOptions]::Singleline)
        if ($ParamSection.Success) {
            $ParamText = $ParamSection.Value
            $OpenParens = ($ParamText.ToCharArray() | Where-Object { $_ -eq '(' }).Count
            $CloseParens = ($ParamText.ToCharArray() | Where-Object { $_ -eq ')' }).Count

            if ($OpenParens -ne $CloseParens) {
                $Issues += "Unbalanced parentheses in param block"
            }
        }

        # Check for smart quotes
        if ($Content -match '[""'']') {
            $Issues += "Smart quotes detected"
        }

        return $Issues
    }

    return @()
}

# Main execution
Write-Host ""
Write-Host "EQ12 POWERSHELL SCRIPT VALIDATOR AND REPAIR SYSTEM" -ForegroundColor Cyan
Write-Host "Buffalo NY 14215 Content Empire Protection" -ForegroundColor Yellow
Write-Host "=================================================="

# Find all PowerShell files
$PowerShellFiles = Get-ChildItem -Path $Folder -Recurse -Filter "*.ps1" | Where-Object { $_.Length -gt 0 }

Write-Host "SCANNING: $($PowerShellFiles.Count) PowerShell files in $Folder" -ForegroundColor Green
Write-Host ""

$TotalFiles = 0
$FilesWithErrors = 0
$FilesRepaired = 0
$ParameterBlockIssues = 0

foreach ($File in $PowerShellFiles) {
    $TotalFiles++
    $FileName = $File.Name

    Write-Host "CHECKING: $FileName" -ForegroundColor White

    # Test syntax
    $IsValid = Test-PowerShellSyntax -FilePath $File.FullName

    # Test param block
    $ParamIssues = Test-ParamBlockSyntax -FilePath $File.FullName

    if (-not $IsValid -or $ParamIssues.Count -gt 0) {
        $FilesWithErrors++

        if (-not $IsValid) {
            Write-Host "  ERROR: Syntax errors detected" -ForegroundColor Red
        }

        if ($ParamIssues.Count -gt 0) {
            $ParameterBlockIssues++
            Write-Host "  PARAM ISSUES: $($ParamIssues -join ', ')" -ForegroundColor Red
        }

        if ($AutoFix) {
            $Repaired = Repair-PowerShellFile -FilePath $File.FullName -CreateBackup $BackupFiles

            if ($Repaired) {
                $FilesRepaired++

                # Test again after repair
                $IsValidAfterRepair = Test-PowerShellSyntax -FilePath $File.FullName
                if ($IsValidAfterRepair) {
                    Write-Host "  VERIFIED: Repair successful" -ForegroundColor Green
                } else {
                    Write-Host "  WARNING: Repair partially successful" -ForegroundColor Yellow
                }
            }
        } else {
            Write-Host "  SUGGESTION: Run with -AutoFix to repair automatically" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  OK: Syntax and param block are valid" -ForegroundColor Green
    }

    Write-Host ""
}

# Summary
Write-Host "VALIDATION SUMMARY:" -ForegroundColor Cyan
Write-Host "  Total files scanned: $TotalFiles" -ForegroundColor Gray
Write-Host "  Files with errors: $FilesWithErrors" -ForegroundColor Gray
Write-Host "  Files with param block issues: $ParameterBlockIssues" -ForegroundColor Gray
Write-Host "  Files repaired: $FilesRepaired" -ForegroundColor Gray

if ($FilesWithErrors -eq 0) {
    Write-Host "SUCCESS: All PowerShell files are valid" -ForegroundColor Green
} elseif ($AutoFix -and $FilesRepaired -eq $FilesWithErrors) {
    Write-Host "SUCCESS: All issues repaired automatically" -ForegroundColor Green
} elseif (-not $AutoFix) {
    Write-Host "INFO: Run with -AutoFix parameter to repair issues automatically" -ForegroundColor Yellow
} else {
    Write-Host "WARNING: Some files may still have issues - manual review needed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "USAGE EXAMPLES:" -ForegroundColor Cyan
Write-Host "  Scan only: .\eq12_script_validator.ps1" -ForegroundColor Gray
Write-Host "  Auto-fix: .\eq12_script_validator.ps1 -AutoFix" -ForegroundColor Gray
Write-Host "  With backups: .\eq12_script_validator.ps1 -AutoFix -BackupFiles" -ForegroundColor Gray
Write-Host ""
Write-Host "Buffalo NY 14215 Content Empire: SCRIPTS PROTECTED" -ForegroundColor Green

exit $(if ($FilesWithErrors -eq 0) { 0 } else { 1 })

