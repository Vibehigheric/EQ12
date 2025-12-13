<#
.SYNOPSIS
    EQ12 Safe Scan - Crash-resistant workspace scanner
.DESCRIPTION
    Ultra-lightweight scanner designed to prevent VS Code crashes.
    Only scans essential directories and limits resource usage.
.PARAMETER OutputDir
    Directory to write the scan report. Defaults to C:\EQ12_BROKEN_20251122_210342\reports
.EXAMPLE
    .\EQ12_SAFE_SCAN.ps1
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$OutputDir = "C:\EQ12_BROKEN_20251122_210342\reports"
)

$ErrorActionPreference = "Continue"
Set-StrictMode -Version Latest

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   EQ12 SAFE SCAN - Crash Protection" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Ensure output directory exists
if (-not (Test-Path $OutputDir)) {
    New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null
}

# Only scan CRITICAL directories (not recursive)
$SafePaths = @(
    "C:\EQ12_BROKEN_20251122_210342\.vscode",
    "C:\EQ12_BROKEN_20251122_210342\.github",
    "C:\EQ12_BROKEN_20251122_210342\scripts",
    "C:\EQ12_BROKEN_20251122_210342\tests"
)

$Results = @{
    ScanTimestamp = (Get-Date).ToUniversalTime().ToString("o")
    Mode = "SAFE_SCAN"
    TotalFiles = 0
    Directories = @()
}

Write-Host "Scanning critical directories only..." -ForegroundColor Yellow
Write-Host ""

foreach ($Path in $SafePaths) {
    if (-not (Test-Path $Path)) {
        Write-Host "  [SKIP] $Path (not found)" -ForegroundColor Gray
        continue
    }

    try {
        Write-Host "  [SCAN] $Path" -ForegroundColor Green
        
        # Non-recursive scan only
        $Files = Get-ChildItem -Path $Path -File -ErrorAction SilentlyContinue
        $Subdirs = Get-ChildItem -Path $Path -Directory -ErrorAction SilentlyContinue
        
        $DirInfo = @{
            Path = $Path
            Files = @()
            Subdirectories = @($Subdirs | ForEach-Object { $_.Name })
        }
        
        foreach ($File in $Files) {
            $DirInfo.Files += @{
                Name = $File.Name
                SizeKB = [math]::Round($File.Length / 1KB, 2)
                Extension = $File.Extension
            }
            $Results.TotalFiles++
        }
        
        $Results.Directories += $DirInfo
        Write-Host "    Found: $($Files.Count) files, $($Subdirs.Count) subdirectories" -ForegroundColor Gray
    }
    catch {
        Write-Host "    ERROR: $_" -ForegroundColor Red
    }
}

Write-Host ""

# Check for common crash-causing issues
Write-Host "Checking for crash-causing patterns..." -ForegroundColor Yellow

$Issues = @()

# Check 1: Large node_modules
$NodeModules = "C:\EQ12_BROKEN_20251122_210342\node_modules"
if (Test-Path $NodeModules) {
    try {
        $NodeSize = (Get-ChildItem $NodeModules -Recurse -File -ErrorAction SilentlyContinue | 
            Measure-Object -Property Length -Sum).Sum / 1MB
        if ($NodeSize -gt 500) {
            $Issues += "Large node_modules ($([math]::Round($NodeSize, 0)) MB) - exclude from search"
        }
    } catch {}
}

# Check 2: .git size
$GitDir = "C:\EQ12_BROKEN_20251122_210342\.git"
if (Test-Path $GitDir) {
    try {
        $GitSize = (Get-ChildItem $GitDir -Recurse -File -ErrorAction SilentlyContinue | 
            Measure-Object -Property Length -Sum).Sum / 1MB
        if ($GitSize -gt 100) {
            $Issues += ".git directory is large ($([math]::Round($GitSize, 0)) MB)"
        }
    } catch {}
}

# Check 3: VS Code settings
$VSCodeSettings = "C:\EQ12_BROKEN_20251122_210342\.vscode\settings.json"
if (Test-Path $VSCodeSettings) {
    try {
        $SettingsSize = (Get-Item $VSCodeSettings).Length
        if ($SettingsSize -gt 100KB) {
            $Issues += "settings.json is very large ($([math]::Round($SettingsSize / 1KB, 0)) KB)"
        }
    } catch {}
}

# Check 4: Multiple Python environments
$VenvDirs = @(Get-ChildItem -Path "C:\EQ12_BROKEN_20251122_210342" -Directory -Filter ".venv*" -ErrorAction SilentlyContinue)
if ($VenvDirs.Count -gt 1) {
    $Issues += "Multiple Python virtual environments detected ($($VenvDirs.Count))"
}

$Results.Issues = $Issues

# Write output
$OutputFile = Join-Path $OutputDir "SAFE_SCAN_${Timestamp}.json"
$Results | ConvertTo-Json -Depth 5 -Compress | Set-Content -Path $OutputFile -Encoding UTF8

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   SCAN COMPLETE" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files scanned: $($Results.TotalFiles)" -ForegroundColor Green
Write-Host "Issues found: $($Issues.Count)" -ForegroundColor $(if ($Issues.Count -gt 0) { "Yellow" } else { "Green" })
Write-Host ""

if ($Issues.Count -gt 0) {
    Write-Host "Potential crash causes:" -ForegroundColor Yellow
    foreach ($Issue in $Issues) {
        Write-Host "  ⚠️  $Issue" -ForegroundColor Yellow
    }
    Write-Host ""
}

Write-Host "Report: $OutputFile" -ForegroundColor Cyan
Write-Host ""

# VS Code crash mitigation suggestions
Write-Host "To prevent VS Code crashes:" -ForegroundColor Cyan
Write-Host "  1. Add to .vscode/settings.json:" -ForegroundColor Gray
Write-Host '     "files.watcherExclude": {' -ForegroundColor Gray
Write-Host '       "**/.git/objects/**": true,' -ForegroundColor Gray
Write-Host '       "**/node_modules/**": true,' -ForegroundColor Gray
Write-Host '       "**/.venv/**": true' -ForegroundColor Gray
Write-Host '     }' -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Restart VS Code after adding exclusions" -ForegroundColor Gray
Write-Host "  3. Use limited scan: .\EQ12_QUICK_SWEEP.ps1 -MaxFiles 5000" -ForegroundColor Gray
Write-Host ""

return @{
    OutputFile = $OutputFile
    TotalFiles = $Results.TotalFiles
    IssuesCount = $Issues.Count
}
