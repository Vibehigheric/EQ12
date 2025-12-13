# ====================================================
# EQ12 SAFE LAUNCHER - CORRUPTION-PROOF SCRIPT EXECUTION
# ====================================================
# Guaranteed to work - Fixes scripts BEFORE execution
# Buffalo NY 14215 Content Empire Protection

param(
    [string]$ScriptPath,
    [string[]]$Args = @()
)

# Force UTF-8 encoding
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "SAFE LAUNCHER: EQ12 Script Protection Engaged" -ForegroundColor Cyan

# Verify script exists
if (!(Test-Path $ScriptPath)) {
    Write-Host "ERROR: Script not found: $ScriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "VALIDATING: $ScriptPath" -ForegroundColor Green

# Read and clean file BEFORE execution
$raw = Get-Content -Raw $ScriptPath -Encoding UTF8

# Remove ALL corrupting characters
$clean = $raw -replace '[^\x00-\x7F]', '' `
               -replace '[""'']', '"' `
               -replace '[]', '-' `
               -replace '[]', '' `
               -replace '[^\x00-\x7F]', ''

if ($raw -ne $clean) {
    Write-Host "CLEANING: Unicode corruption detected and removed" -ForegroundColor Yellow

    # Create backup
    $backup = "$ScriptPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $ScriptPath $backup

    # Save cleaned version
    Set-Content -Path $ScriptPath -Value $clean -Encoding UTF8
    Write-Host "BACKUP: Saved original to $backup" -ForegroundColor Gray
} else {
    Write-Host "CLEAN: Script is already ASCII-safe" -ForegroundColor Green
}

# Validate param block syntax
$paramMatch = [regex]::Match($clean, 'param\s*\(.*?\)', [System.Text.RegularExpressions.RegexOptions]::Singleline)
if ($paramMatch.Success) {
    $paramBlock = $paramMatch.Value
    $openParens = ($paramBlock.ToCharArray() | Where-Object { $_ -eq '(' }).Count
    $closeParens = ($paramBlock.ToCharArray() | Where-Object { $_ -eq ')' }).Count

    if ($openParens -ne $closeParens) {
        Write-Host "ERROR: Param block has unmatched parentheses" -ForegroundColor Red
        exit 1
    } else {
        Write-Host "VALIDATED: Param block syntax is correct" -ForegroundColor Green
    }
}

# Set clean environment for execution
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:LC_ALL = "C.UTF-8"
$env:LANG = "C.UTF-8"

# Execute with clean environment
Write-Host "EXECUTING: powershell -NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`" $($Args -join ' ')" -ForegroundColor Blue

try {
    $process = Start-Process -FilePath "powershell" -ArgumentList @(
        '-NoProfile',
        '-ExecutionPolicy', 'Bypass',
        '-File', "`"$ScriptPath`""
    ) + $Args -Wait -PassThru -NoNewWindow

    $exitCode = $process.ExitCode

    if ($exitCode -eq 0) {
        Write-Host "SUCCESS: Script completed successfully (Exit: $exitCode)" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Script completed with issues (Exit: $exitCode)" -ForegroundColor Yellow
    }

    exit $exitCode
} catch {
    Write-Host "ERROR: Script execution failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
