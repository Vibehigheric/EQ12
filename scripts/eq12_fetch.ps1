# EQ12 NFL Fetch Engine PowerShell Wrapper
# ASCII-safe wrapper for real-time NFL data fetching
# NO EMOJIS, NO UNICODE - PRODUCTION READY

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("NFL", "NBA", "MLB")]
    [string]$Sport = "NFL",

    [Parameter(Mandatory=$false)]
    [ValidateSet("TNF", "SNF", "MNF", "Regular")]
    [string]$Mode = "TNF",

    [Parameter(Mandatory=$false)]
    [string]$Workspace = "C:\EQ12",

    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput,

    [Parameter(Mandatory=$false)]
    [switch]$ValidateOnly
)

# Set error preference
$ErrorActionPreference = "Stop"

# Setup paths
$ScriptRoot = Split-Path -Parent $PSCommandPath
$PythonScript = Join-Path $ScriptRoot "eq12_fetch_nfl.py"
$ConfigFile = Join-Path $ScriptRoot "eq12_fetch_config.json"
$LogDir = Join-Path $Workspace "logs"
$DataDir = Join-Path $Workspace "data"

# Ensure directories exist
foreach ($Dir in @($LogDir, $DataDir)) {
    if (-not (Test-Path $Dir)) {
        New-Item -ItemType Directory -Path $Dir -Force | Out-Null
    }
}

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"

    if ($VerboseOutput) {
        Write-Host $LogMessage
    }

    $LogFile = Join-Path $LogDir "eq12_fetch_$(Get-Date -Format 'yyyyMMdd').log"
    Add-Content -Path $LogFile -Value $LogMessage
}

function Test-PythonEnvironment {
    try {
        $PythonVersion = & python --version 2>&1
        Write-EQ12Log "Python environment: $PythonVersion"
        return $true
    }
    catch {
        Write-EQ12Log "Python not found or not accessible" "ERROR"
        return $false
    }
}

function Test-ConfigFile {
    if (-not (Test-Path $ConfigFile)) {
        Write-EQ12Log "Config file not found: $ConfigFile" "ERROR"
        return $false
    }

    try {
        $Config = Get-Content $ConfigFile | ConvertFrom-Json
        Write-EQ12Log "Config file validated successfully"
        return $true
    }
    catch {
        Write-EQ12Log "Config file validation failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Invoke-NFLFetcher {
    Write-EQ12Log "Starting EQ12 NFL Fetch Engine"
    Write-EQ12Log "Sport: $Sport, Mode: $Mode"

    # Pre-flight checks
    if (-not (Test-PythonEnvironment)) {
        throw "Python environment check failed"
    }

    if (-not (Test-ConfigFile)) {
        throw "Config file validation failed"
    }

    if (-not (Test-Path $PythonScript)) {
        throw "Python script not found: $PythonScript"
    }

    # Execute the fetcher
    try {
        Write-EQ12Log "Executing Python fetcher..."
        $StartTime = Get-Date

        $Output = & python $PythonScript 2>&1
        $ExitCode = $LASTEXITCODE

        $Duration = (Get-Date) - $StartTime
        Write-EQ12Log "Python execution completed in $($Duration.TotalSeconds) seconds"

        if ($ExitCode -eq 0) {
            Write-EQ12Log "Fetch operation SUCCESS"

            # Display output
            if ($Output) {
                Write-Host ""
                Write-Host "=== EQ12 NFL FETCH ENGINE OUTPUT ===" -ForegroundColor Green
                $Output | ForEach-Object { Write-Host $_ }
                Write-Host "=== END OUTPUT ===" -ForegroundColor Green
                Write-Host ""
            }

            # Find the most recent output file
            $DataFiles = Get-ChildItem -Path $DataDir -Filter "tnf_real_data_*.json" | Sort-Object LastWriteTime -Descending
            if ($DataFiles) {
                $LatestFile = $DataFiles[0]
                Write-EQ12Log "Latest data file: $($LatestFile.Name)"

                # Validate JSON structure
                try {
                    $Data = Get-Content $LatestFile.FullName | ConvertFrom-Json
                    Write-EQ12Log "Data validation: SUCCESS"

                    # Quick integrity check
                    if ($Data.game -like "*Bills*" -and $Data.game -like "*Texans*") {
                        Write-EQ12Log "Game validation: Bills @ Texans confirmed"
                    }
                    else {
                        Write-EQ12Log "Game validation: WARNING - unexpected game data" "WARN"
                    }

                    # Check for simulation markers
                    $DataString = $Data | ConvertTo-Json -Depth 10
                    $SimulationMarkers = @("simulation", "simulated", "Bears", "Lions", "fake")

                    foreach ($Marker in $SimulationMarkers) {
                        if ($DataString -like "*$Marker*") {
                            Write-EQ12Log "INTEGRITY VIOLATION: Simulation marker detected: $Marker" "ERROR"
                            throw "Data integrity check failed - simulation data detected"
                        }
                    }

                    Write-EQ12Log "Integrity check: PASSED - Real data confirmed"

                }
                catch {
                    Write-EQ12Log "Data validation failed: $($_.Exception.Message)" "ERROR"
                    throw
                }
            }

            return $true
        }
        else {
            Write-EQ12Log "Python script failed with exit code: $ExitCode" "ERROR"
            if ($Output) {
                Write-EQ12Log "Python output: $Output" "ERROR"
            }
            throw "Python fetch script failed"
        }
    }
    catch {
        Write-EQ12Log "Fetch operation failed: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Show-Usage {
    Write-Host ""
    Write-Host "EQ12 NFL Fetch Engine - PowerShell Wrapper" -ForegroundColor Cyan
    Write-Host "=========================================="
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\eq12_fetch.ps1 -Sport NFL -Mode TNF"
    Write-Host "  .\eq12_fetch.ps1 -Sport NFL -Mode TNF -VerboseOutput"
    Write-Host "  .\eq12_fetch.ps1 -ValidateOnly"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -Sport      : NFL, NBA, MLB (default: NFL)"
    Write-Host "  -Mode       : TNF, SNF, MNF, Regular (default: TNF)"
    Write-Host "  -Workspace  : EQ12 workspace path (default: C:\EQ12)"
    Write-Host "  -VerboseOutput : Show detailed logging"
    Write-Host "  -ValidateOnly : Just validate environment, don't fetch"
    Write-Host ""
}

# Main execution
try {
    Write-EQ12Log "EQ12 Fetch Engine started with PID: $PID"

    if ($ValidateOnly) {
        Write-Host "Running validation checks only..." -ForegroundColor Yellow

        $PythonOK = Test-PythonEnvironment
        $ConfigOK = Test-ConfigFile
        $ScriptOK = Test-Path $PythonScript

        Write-Host ""
        Write-Host "Validation Results:" -ForegroundColor Cyan
        Write-Host "Python Environment: $(if($PythonOK){'OK'}else{'FAIL'})"
        Write-Host "Config File: $(if($ConfigOK){'OK'}else{'FAIL'})"
        Write-Host "Python Script: $(if($ScriptOK){'OK'}else{'FAIL'})"
        Write-Host ""

        if ($PythonOK -and $ConfigOK -and $ScriptOK) {
            Write-Host "All validation checks PASSED" -ForegroundColor Green
            exit 0
        }
        else {
            Write-Host "Validation checks FAILED" -ForegroundColor Red
            exit 1
        }
    }

    # Run the fetcher
    $Result = Invoke-NFLFetcher

    if ($Result) {
        Write-Host ""
        Write-Host "EQ12 NFL FETCH ENGINE - SUCCESS" -ForegroundColor Green
        Write-Host "Real TNF data available for analysis" -ForegroundColor Green
        Write-EQ12Log "Fetch engine completed successfully"
        exit 0
    }
}
catch {
    Write-Host ""
    Write-Host "EQ12 NFL FETCH ENGINE - FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-EQ12Log "Fetch engine failed: $($_.Exception.Message)" "ERROR"

    Write-Host ""
    Write-Host "Troubleshooting:"
    Write-Host "1. Check Python installation"
    Write-Host "2. Verify network connectivity"
    Write-Host "3. Check workspace permissions"
    Write-Host "4. Run with -ValidateOnly to diagnose"

    exit 1
}
