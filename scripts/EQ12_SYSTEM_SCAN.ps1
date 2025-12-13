<#
.SYNOPSIS
    EQ12 System Scanner - Comprehensive workspace inventory tool
.DESCRIPTION
    Scans relevant paths for the EQ12 workspace, collecting file metadata
    (path, size, last write time) and outputting a timestamped JSON report.
    READ-ONLY operation - never modifies or deletes files.
.PARAMETER OutputDir
    Directory to write the scan report JSON. Defaults to C:\EQ12_BROKEN_20251122_210342\reports
.PARAMETER IncludeVSCode
    Include VS Code user settings and extensions in the scan
.EXAMPLE
    .\EQ12_SYSTEM_SCAN.ps1
    .\EQ12_SYSTEM_SCAN.ps1 -OutputDir "C:\custom\path" -IncludeVSCode
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$OutputDir = "C:\EQ12_BROKEN_20251122_210342\reports",

    [Parameter()]
    [switch]$IncludeVSCode,

    [Parameter()]
    [int]$MaxFiles = 50000,

    [Parameter()]
    [switch]$QuickScan
)

$ErrorActionPreference = "Continue"
Set-StrictMode -Version Latest

# Critical directories to ALWAYS exclude (prevent crashes)
$ExcludePatterns = @(
    '*\node_modules\*',
    '*\.git\*',
    '*\.venv\*',
    '*\__pycache__\*',
    '*\.pytest_cache\*',
    '*\.ruff_cache\*',
    '*\venv\*',
    '*\dist\*',
    '*\build\*',
    '*\.vscode-server\*',
    '*\AppData\Local\Temp\*',
    '*\Windows\*',
    '*\$Recycle.Bin\*'
)

# Initialize logging
$ScriptName = [System.IO.Path]::GetFileNameWithoutExtension($MyInvocation.MyCommand.Name)
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $OutputDir "${ScriptName}_LOG_${Timestamp}.txt"

function Write-Log {
    [CmdletBinding()]
    param([string]$Message, [string]$Level = "INFO")
    
    $LogEntry = "[{0:yyyy-MM-dd HH:mm:ss}] [{1}] {2}" -f (Get-Date).ToUniversalTime(), $Level, $Message
    Write-Verbose $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -ErrorAction SilentlyContinue
}

# Ensure output directory exists
if (-not (Test-Path $OutputDir)) {
    New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null
    Write-Log "Created output directory: $OutputDir"
}

Write-Log "===== EQ12 SYSTEM SCAN STARTED ====="
Write-Log "Output directory: $OutputDir"

# Define safe scan paths
$ScanPaths = @(
    @{
        Path = "C:\EQ12_BROKEN_20251122_210342"
        Description = "EQ12 Main Repository"
        Recursive = $true
    }
)

# Optionally include VS Code paths
if ($IncludeVSCode) {
    $UserProfile = $env:USERPROFILE
    $ScanPaths += @(
        @{
            Path = Join-Path $UserProfile ".vscode"
            Description = "VS Code User Extensions"
            Recursive = $true
        },
        @{
            Path = Join-Path $UserProfile "AppData\Roaming\Code"
            Description = "VS Code Roaming Data"
            Recursive = $false
        }
    )
    Write-Log "Including VS Code paths in scan"
}

# Scan results collection
$ScanResults = @{
    ScanTimestamp = (Get-Date).ToUniversalTime().ToString("o")
    ScanDuration = $null
    TotalFiles = 0
    TotalSize = 0
    Paths = @()
}

$StartTime = Get-Date

foreach ($ScanDef in $ScanPaths) {
    $TargetPath = $ScanDef.Path
    
    if (-not (Test-Path $TargetPath)) {
        Write-Log "Path not found, skipping: $TargetPath" -Level "WARN"
        continue
    }

    Write-Log "Scanning: $TargetPath ($($ScanDef.Description))"
    
    try {
        # Use filtered scan with exclusions
        $Files = if ($ScanDef.Recursive) {
            Get-ChildItem -Path $TargetPath -File -Recurse -ErrorAction SilentlyContinue |
                Where-Object { 
                    $filePath = $_.FullName
                    -not ($ExcludePatterns | Where-Object { $filePath -like $_ })
                }
        } else {
            Get-ChildItem -Path $TargetPath -File -ErrorAction SilentlyContinue
        }

        $PathResults = @()
        $PathSize = 0
        $FileCount = 0

        foreach ($File in $Files) {
            # Stop if we hit the file limit
            if ($ScanResults.TotalFiles -ge $MaxFiles) {
                Write-Log "Reached maximum file limit ($MaxFiles). Stopping scan." -Level "WARN"
                break
            }

            # Progress indicator every 1000 files
            if ($FileCount % 1000 -eq 0 -and $FileCount -gt 0) {
                Write-Host "." -NoNewline
            }

            $FileInfo = @{
                Path = $File.FullName
                SizeBytes = $File.Length
                LastWriteTimeUtc = $File.LastWriteTimeUtc.ToString("o")
                Extension = $File.Extension
                Name = $File.Name
            }
            
            $PathResults += $FileInfo
            $PathSize += $File.Length
            $ScanResults.TotalFiles++
            $ScanResults.TotalSize += $File.Length
            $FileCount++
        }

        Write-Host "" # New line after progress dots

        $ScanResults.Paths += @{
            Path = $TargetPath
            Description = $ScanDef.Description
            FileCount = $PathResults.Count
            TotalSizeBytes = $PathSize
            TotalSizeMB = [math]::Round($PathSize / 1MB, 2)
            Files = $PathResults
        }

        Write-Log "Found $($PathResults.Count) files ($([math]::Round($PathSize / 1MB, 2)) MB) in $TargetPath"
    }
    catch {
        Write-Log "Error scanning $TargetPath : $_" -Level "ERROR"
    }
}

$EndTime = Get-Date
$ScanResults.ScanDuration = ($EndTime - $StartTime).TotalSeconds

# Generate output file
$OutputFile = Join-Path $OutputDir "SCAN_RESULT_${Timestamp}.json"

try {
    # Use -Compress to reduce memory usage for large scans
    $ScanResults | ConvertTo-Json -Depth 10 -Compress | Set-Content -Path $OutputFile -Encoding UTF8
    Write-Log "Scan complete. Results written to: $OutputFile"
    Write-Log "Total files scanned: $($ScanResults.TotalFiles)"
    Write-Log "Total size: $([math]::Round($ScanResults.TotalSize / 1MB, 2)) MB"
    Write-Log "Scan duration: $([math]::Round($ScanResults.ScanDuration, 2)) seconds"
    
    if ($ScanResults.TotalFiles -ge $MaxFiles) {
        Write-Log "WARNING: File limit reached. Scan incomplete." -Level "WARN"
        Write-Host "⚠️  File limit reached ($MaxFiles). Consider scanning specific directories." -ForegroundColor Yellow
    }
}
catch {
    Write-Log "Failed to write output file: $_" -Level "ERROR"
    throw
}

Write-Log "===== EQ12 SYSTEM SCAN COMPLETED ====="

# Return output file path for pipeline usage
return @{
    OutputFile = $OutputFile
    TotalFiles = $ScanResults.TotalFiles
    TotalSizeMB = [math]::Round($ScanResults.TotalSize / 1MB, 2)
    ScanDuration = [math]::Round($ScanResults.ScanDuration, 2)
}
