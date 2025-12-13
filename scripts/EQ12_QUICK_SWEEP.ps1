<#
.SYNOPSIS
    EQ12 Quick Sweep - One-command system health check
.DESCRIPTION
    Convenience wrapper that runs system scan + analysis in sequence.
    Perfect for quick health checks without remembering multiple commands.
.PARAMETER IncludeVSCode
    Include VS Code user extensions and settings in the scan
.PARAMETER DryRun
    Preview what would be scanned without writing reports
.EXAMPLE
    .\EQ12_QUICK_SWEEP.ps1
    .\EQ12_QUICK_SWEEP.ps1 -IncludeVSCode
#>

[CmdletBinding()]
param(
    [Parameter()]
    [switch]$IncludeVSCode,

    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [int]$MaxFiles = 10000
)

$ErrorActionPreference = "Continue"
Set-StrictMode -Version Latest

# Determine script location
$ScriptRoot = $PSScriptRoot
if (-not $ScriptRoot) {
    $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   EQ12 QUICK SWEEP - System Health" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verify we're in the right place
$RepoRoot = Split-Path -Parent $ScriptRoot
$ExpectedPath = "C:\EQ12_BROKEN_20251122_210342"

if ($RepoRoot -ne $ExpectedPath) {
    Write-Host "WARNING: Running from unexpected location" -ForegroundColor Yellow
    Write-Host "  Expected: $ExpectedPath" -ForegroundColor Yellow
    Write-Host "  Actual:   $RepoRoot" -ForegroundColor Yellow
    Write-Host ""
    $Response = Read-Host "Continue anyway? [Y/N]"
    if ($Response -ne "Y" -and $Response -ne "y") {
        Write-Host "Aborted." -ForegroundColor Red
        exit 1
    }
}

# Step 1: Run system scan
Write-Host "[1/2] Running System Scan..." -ForegroundColor Green
Write-Host "  Limiting to $MaxFiles files to prevent crashes" -ForegroundColor Gray
Write-Host ""

$ScanArgs = @{
    Verbose = $true
    MaxFiles = $MaxFiles
}

if ($IncludeVSCode) {
    $ScanArgs['IncludeVSCode'] = $true
    Write-Host "Including VS Code paths in scan" -ForegroundColor Cyan
}

try {
    $ScanResult = & (Join-Path $ScriptRoot "EQ12_SYSTEM_SCAN.ps1") @ScanArgs
    
    if (-not $ScanResult) {
        Write-Host "System scan failed or returned no results" -ForegroundColor Red
        Write-Host "Try running with fewer files: .\EQ12_QUICK_SWEEP.ps1 -MaxFiles 5000" -ForegroundColor Yellow
        exit 1
    }

    Write-Host ""
    Write-Host "✓ Scan complete!" -ForegroundColor Green
    Write-Host "  Files scanned: $($ScanResult.TotalFiles)" -ForegroundColor Gray
    Write-Host "  Total size: $($ScanResult.TotalSizeMB) MB" -ForegroundColor Gray
    Write-Host "  Duration: $($ScanResult.ScanDuration) seconds" -ForegroundColor Gray
    Write-Host "  Output: $($ScanResult.OutputFile)" -ForegroundColor Gray
    Write-Host ""
}
catch {
    Write-Host "System scan failed: $_" -ForegroundColor Red
    exit 1
}

if ($DryRun) {
    Write-Host "Dry run mode - skipping analysis" -ForegroundColor Yellow
    exit 0
}

# Step 2: Run reverse engineering analysis
Write-Host "[2/2] Analyzing Results..." -ForegroundColor Green
Write-Host ""

try {
    $AnalysisResult = & (Join-Path $ScriptRoot "EQ12_REVERSE_ENGINEER.ps1") -ScanFile $ScanResult.OutputFile -Verbose
    
    Write-Host ""
    Write-Host "✓ Analysis complete!" -ForegroundColor Green
    Write-Host "  Issues: $($AnalysisResult.IssuesCount)" -ForegroundColor $(if ($AnalysisResult.IssuesCount -gt 0) { "Red" } else { "Gray" })
    Write-Host "  Warnings: $($AnalysisResult.WarningsCount)" -ForegroundColor $(if ($AnalysisResult.WarningsCount -gt 0) { "Yellow" } else { "Gray" })
    Write-Host "  Info items: $($AnalysisResult.InfoCount)" -ForegroundColor Gray
    Write-Host "  Report: $($AnalysisResult.OutputFile)" -ForegroundColor Gray
    Write-Host ""
}
catch {
    Write-Host "Analysis failed: $_" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   SWEEP COMPLETE" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

if ($AnalysisResult.IssuesCount -gt 0) {
    Write-Host "⚠️  $($AnalysisResult.IssuesCount) issue(s) detected - review the report" -ForegroundColor Red
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Open: $($AnalysisResult.OutputFile)" -ForegroundColor Gray
    Write-Host "  2. Review the 'Issues' section" -ForegroundColor Gray
    Write-Host "  3. Consult EQ12_COPILOT_HEALTHCHECK.md for repair procedures" -ForegroundColor Gray
}
elseif ($AnalysisResult.WarningsCount -gt 0) {
    Write-Host "✓ No critical issues, but $($AnalysisResult.WarningsCount) warning(s) found" -ForegroundColor Yellow
    Write-Host "  Review: $($AnalysisResult.OutputFile)" -ForegroundColor Gray
}
else {
    Write-Host "✓ All clear! No issues detected." -ForegroundColor Green
}

Write-Host ""
Write-Host "Full reports available in: $(Join-Path $RepoRoot 'reports')" -ForegroundColor Cyan
Write-Host ""

# Return results for pipeline usage
return @{
    ScanResult = $ScanResult
    AnalysisResult = $AnalysisResult
    OverallStatus = if ($AnalysisResult.IssuesCount -gt 0) { "Issues" } 
                    elseif ($AnalysisResult.WarningsCount -gt 0) { "Warnings" } 
                    else { "Healthy" }
}
