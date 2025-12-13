<#
.SYNOPSIS
    EQ12 Reverse Engineer - Analyzes system scan results for common issues
.DESCRIPTION
    Takes a SCAN_RESULT_*.json file from EQ12_SYSTEM_SCAN.ps1 and analyzes
    it for patterns that indicate problems:
    - Broken/incomplete Copilot extensions
    - Corrupted dist/ JS files
    - Multiple conflicting VS Code configs
    - Missing/broken Python environments
    - Oversized cache/log directories
    
    Outputs both console report and JSON summary.
.PARAMETER ScanFile
    Path to the SCAN_RESULT_*.json file to analyze
.PARAMETER OutputDir
    Directory to write analysis reports. Defaults to C:\EQ12_BROKEN_20251122_210342\reports
.EXAMPLE
    .\EQ12_REVERSE_ENGINEER.ps1 -ScanFile "C:\EQ12_BROKEN_20251122_210342\reports\SCAN_RESULT_20251122_143000.json"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ScanFile,

    [Parameter()]
    [string]$OutputDir = "C:\EQ12_BROKEN_20251122_210342\reports"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Initialize
$ScriptName = [System.IO.Path]::GetFileNameWithoutExtension($MyInvocation.MyCommand.Name)
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $OutputDir "${ScriptName}_LOG_${Timestamp}.txt"

function Write-Log {
    [CmdletBinding()]
    param([string]$Message, [string]$Level = "INFO")
    
    $LogEntry = "[{0:yyyy-MM-dd HH:mm:ss}] [{1}] {2}" -f (Get-Date).ToUniversalTime(), $Level, $Message
    Write-Verbose $LogEntry
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -ErrorAction SilentlyContinue
}

# Ensure output directory exists
if (-not (Test-Path $OutputDir)) {
    New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null
}

# Load scan data
Write-Log "===== EQ12 REVERSE ENGINEER STARTED ====="
Write-Log "Loading scan file: $ScanFile"

if (-not (Test-Path $ScanFile)) {
    Write-Log "Scan file not found: $ScanFile" -Level "ERROR"
    throw "Scan file not found"
}

try {
    $ScanData = Get-Content -Path $ScanFile -Raw | ConvertFrom-Json
}
catch {
    Write-Log "Failed to parse scan file: $_" -Level "ERROR"
    throw
}

Write-Log "Scan file loaded. Total files: $($ScanData.TotalFiles)"

# Initialize analysis results
$AnalysisResults = @{
    AnalysisTimestamp = (Get-Date).ToUniversalTime().ToString("o")
    SourceScanFile = $ScanFile
    Issues = @()
    Warnings = @()
    Info = @()
}

# Helper function to add findings
function Add-Finding {
    param(
        [string]$Category,
        [string]$Severity,  # "Issue", "Warning", "Info"
        [string]$Title,
        [string]$Description,
        [array]$AffectedFiles = @()
    )
    
    $Finding = @{
        Category = $Category
        Title = $Title
        Description = $Description
        AffectedFiles = $AffectedFiles
    }
    
    switch ($Severity) {
        "Issue" { $AnalysisResults.Issues += $Finding }
        "Warning" { $AnalysisResults.Warnings += $Finding }
        "Info" { $AnalysisResults.Info += $Finding }
    }
}

Write-Log "Starting analysis..."

# Collect all files from scan
$AllFiles = @()
foreach ($PathResult in $ScanData.Paths) {
    $AllFiles += $PathResult.Files
}

Write-Log "Analyzing $($AllFiles.Count) files..."

# Analysis 1: Check for tiny or missing critical Copilot files
Write-Log "Checking for Copilot extension issues..."
$CopilotFiles = $AllFiles | Where-Object { $_.Path -match "copilot.*tikTokenizerWorker\.js" }
$SuspiciousCopilotFiles = $CopilotFiles | Where-Object { $_.SizeBytes -lt 1000 }

if ($SuspiciousCopilotFiles) {
    $FileList = $SuspiciousCopilotFiles | ForEach-Object { $_.Path }
    Add-Finding -Category "Copilot" -Severity "Issue" `
        -Title "Corrupted Copilot tokenizer files detected" `
        -Description "Found tikTokenizerWorker.js files smaller than 1KB, indicating corruption" `
        -AffectedFiles $FileList
    Write-Log "ISSUE: Found $($SuspiciousCopilotFiles.Count) suspicious Copilot files" -Level "WARN"
}

# Analysis 2: Check for multiple conflicting .vscode/settings.json
Write-Log "Checking for multiple VS Code settings files..."
$SettingsFiles = $AllFiles | Where-Object { $_.Path -match "\.vscode\\settings\.json$" }
if ($SettingsFiles.Count -gt 1) {
    $FileList = $SettingsFiles | ForEach-Object { $_.Path }
    Add-Finding -Category "VSCode Config" -Severity "Warning" `
        -Title "Multiple VS Code settings.json files found" `
        -Description "Found $($SettingsFiles.Count) settings.json files which may conflict" `
        -AffectedFiles $FileList
    Write-Log "WARNING: Found $($SettingsFiles.Count) settings.json files" -Level "WARN"
}

# Analysis 3: Check for broken Python environments
Write-Log "Checking for Python environment issues..."
$VenvDirs = $AllFiles | Where-Object { $_.Path -match "\.venv\\Scripts\\python\.exe$" }
$PythonExes = $AllFiles | Where-Object { $_.Name -eq "python.exe" -and $_.Path -match "\.venv" }

foreach ($PyExe in $PythonExes) {
    if ($PyExe.SizeBytes -lt 10000) {
        Add-Finding -Category "Python Environment" -Severity "Issue" `
            -Title "Suspiciously small python.exe detected" `
            -Description "Found python.exe smaller than 10KB at $($PyExe.Path)" `
            -AffectedFiles @($PyExe.Path)
        Write-Log "ISSUE: Suspicious python.exe at $($PyExe.Path)" -Level "WARN"
    }
}

# Analysis 4: Large cache/temp directories
Write-Log "Checking for oversized cache directories..."
$CacheDirs = @("__pycache__", ".ruff_cache", ".pytest_cache", "dist", "build", "node_modules")
foreach ($CacheDir in $CacheDirs) {
    $CacheFiles = $AllFiles | Where-Object { $_.Path -match "\\$CacheDir\\" }
    if ($CacheFiles) {
        $TotalSize = ($CacheFiles | Measure-Object -Property SizeBytes -Sum).Sum
        $TotalSizeMB = [math]::Round($TotalSize / 1MB, 2)
        
        if ($TotalSizeMB -gt 100) {
            Add-Finding -Category "Workspace Performance" -Severity "Warning" `
                -Title "Large cache directory: $CacheDir" `
                -Description "$CacheDir contains $($CacheFiles.Count) files ($TotalSizeMB MB)" `
                -AffectedFiles @()
            Write-Log "WARNING: $CacheDir is $TotalSizeMB MB with $($CacheFiles.Count) files" -Level "WARN"
        }
        elseif ($TotalSizeMB -gt 10) {
            Add-Finding -Category "Workspace Performance" -Severity "Info" `
                -Title "Cache directory: $CacheDir" `
                -Description "$CacheDir contains $($CacheFiles.Count) files ($TotalSizeMB MB)" `
                -AffectedFiles @()
        }
    }
}

# Analysis 5: Missing critical files
Write-Log "Checking for missing critical configuration files..."
$RepoRoot = "C:\EQ12_BROKEN_20251122_210342"
$CriticalFiles = @(
    ".vscode\settings.json",
    "pyproject.toml",
    ".gitignore"
)

foreach ($CriticalFile in $CriticalFiles) {
    $FullPath = Join-Path $RepoRoot $CriticalFile
    $Found = $AllFiles | Where-Object { $_.Path -eq $FullPath }
    
    if (-not $Found) {
        Add-Finding -Category "Configuration" -Severity "Warning" `
            -Title "Missing critical file: $CriticalFile" `
            -Description "Expected file not found at $FullPath" `
            -AffectedFiles @($FullPath)
        Write-Log "WARNING: Missing critical file: $CriticalFile" -Level "WARN"
    }
}

# Analysis 6: Identify duplicate files (same name, different paths)
Write-Log "Checking for duplicate file names..."
$FileGroups = $AllFiles | Group-Object -Property Name | Where-Object { $_.Count -gt 3 -and $_.Name -ne "" }
foreach ($Group in $FileGroups) {
    if ($Group.Name -match "\.(py|ps1|json|md)$") {
        $Paths = $Group.Group | ForEach-Object { $_.Path }
        Add-Finding -Category "Duplication" -Severity "Info" `
            -Title "Multiple instances of $($Group.Name)" `
            -Description "Found $($Group.Count) files named $($Group.Name)" `
            -AffectedFiles $Paths
    }
}

# Generate summary report
Write-Log ""
Write-Log "===== ANALYSIS SUMMARY ====="
Write-Log "Issues found: $($AnalysisResults.Issues.Count)"
Write-Log "Warnings: $($AnalysisResults.Warnings.Count)"
Write-Log "Informational items: $($AnalysisResults.Info.Count)"

if ($AnalysisResults.Issues.Count -gt 0) {
    Write-Log ""
    Write-Log "ISSUES:" -Level "WARN"
    foreach ($Issue in $AnalysisResults.Issues) {
        Write-Log "  [$($Issue.Category)] $($Issue.Title)" -Level "WARN"
        Write-Log "    $($Issue.Description)" -Level "WARN"
    }
}

if ($AnalysisResults.Warnings.Count -gt 0) {
    Write-Log ""
    Write-Log "WARNINGS:"
    foreach ($Warning in $AnalysisResults.Warnings) {
        Write-Log "  [$($Warning.Category)] $($Warning.Title)"
        Write-Log "    $($Warning.Description)"
    }
}

# Write JSON report
$OutputFile = Join-Path $OutputDir "REVERSE_REPORT_${Timestamp}.json"
try {
    $AnalysisResults | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputFile -Encoding UTF8
    Write-Log "Analysis report written to: $OutputFile"
}
catch {
    Write-Log "Failed to write output file: $_" -Level "ERROR"
    throw
}

Write-Log "===== EQ12 REVERSE ENGINEER COMPLETED ====="

# Return results
return @{
    OutputFile = $OutputFile
    IssuesCount = $AnalysisResults.Issues.Count
    WarningsCount = $AnalysisResults.Warnings.Count
    InfoCount = $AnalysisResults.Info.Count
}
