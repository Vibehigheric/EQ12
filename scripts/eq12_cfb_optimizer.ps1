[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, HelpMessage = "Mystery Profit Boost token percentage (25, 33, or 50)")]
    [ValidateSet(25, 33, 50)]
    [int]$TokenPercent = 25,

    [Parameter(Mandatory = $false, HelpMessage = "Maximum bet amount (up to 100 for DK promos)")]
    [ValidateRange(1, 100)]
    [decimal]$Stake = 100.00,

    [Parameter(Mandatory = $false, HelpMessage = "Promo date in YYYY-MM-DD format")]
    [ValidatePattern('^\d{4}-\d{2}-\d{2}$')]
    [string]$PromoDate = "2025-10-03",

    [Parameter(Mandatory = $false, HelpMessage = "Disable EQ12 backend integration")]
    [switch]$NoEQ12Integration,

    [Parameter(Mandatory = $false, HelpMessage = "Show detailed verbose output")]
    [switch]$Verbose,

    [Parameter(Mandatory = $false, HelpMessage = "Show help information")]
    [switch]$Help
)

<#
.SYNOPSIS
    EQ12 NCAA College Football DraftKings Mystery Profit Boost Optimizer Wrapper

.DESCRIPTION
    PowerShell wrapper for the EQ12 CFB optimizer that finds the optimal
    DraftKings-eligible Friday CFB (FBS-only) parlay for Mystery Profit Boost promotions.

    Features:
    - OddsAPI integration with real-time CFB moneylines
    - Advanced de-vigging using multiple sportsbooks
    - EV optimization with configurable boost percentages
    - FBS-only filtering and Friday game targeting
    - DraftKings promo rule compliance validation
    - EQ12 backend integration for analytics and logging

.PARAMETER TokenPercent
    Mystery Profit Boost token percentage. Valid values: 25, 33, 50. Default: 25

.PARAMETER Stake
    Maximum bet amount in USD. Range: $1-$100 for DK promos. Default: $100

.PARAMETER PromoDate
    Promo date in YYYY-MM-DD format. Must be a Friday. Default: "2025-10-03"

.PARAMETER NoEQ12Integration
    Disable EQ12 backend integration (database storage, analytics)

.PARAMETER Verbose
    Show detailed verbose output from the Python optimizer

.PARAMETER Help
    Show this help information

.EXAMPLE
    .\eq12_cfb_optimizer.ps1
    Run optimization with default settings (25% boost, $100 stake, 2025-10-03)

.EXAMPLE
    .\eq12_cfb_optimizer.ps1 -TokenPercent 50 -Stake 50 -PromoDate "2025-10-10"
    Run optimization with 50% boost, $50 stake on different Friday

.EXAMPLE
    .\eq12_cfb_optimizer.ps1 -NoEQ12Integration -Verbose
    Run without EQ12 backend integration and show detailed output

.NOTES
    Author: EQ12 Development Team
    Version: 2.0.0
    Updated: 2025-10-03

    Requirements:
    - Python 3.12+ with required packages (requests, etc.)
    - ODDSAPI_KEY environment variable set
    - EQ12 backend system (optional with -NoEQ12Integration)
    - DraftKings account with Mystery Profit Boost token

    Promo Rules Enforced:
    - 3+ legs required
    - +300 minimum combined odds
    - $100 maximum stake
    - Cash/DK Dollars only
    - FBS teams only
    - Friday games only on promo date
#>

# Show help if requested
if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Full
    exit 0
}

# EQ12 standard error handling
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# EQ12 paths and configuration
$ScriptRoot = $PSScriptRoot
$PythonScript = Join-Path $ScriptRoot "eq12_cfb_optimizer.py"
$EQ12LogsDir = "C:\EQ12\logs"
$LogFile = Join-Path $EQ12LogsDir "cfb_optimizer_wrapper_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Ensure logs directory exists
if (-not (Test-Path $EQ12LogsDir)) {
    New-Item -ItemType Directory -Path $EQ12LogsDir -Force | Out-Null
}

# Logging function
function Write-EQ12Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )

    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"
    $LogEntry = "[$Timestamp] [$Level] $Message"

    # Write to console with color
    switch ($Level) {
        "ERROR" { Write-Error $Message }
        "WARN" { Write-Warning $Message }
        "INFO" { Write-Host $Message -ForegroundColor Green }
        "DEBUG" { if ($Verbose) { Write-Host $Message -ForegroundColor Cyan } }
        default { Write-Host $Message }
    }

    # Write to log file
    Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
}

# Validate environment
function Test-EQ12Environment {
    Write-EQ12Log "Validating EQ12 environment..."

    # Check Python script exists
    if (-not (Test-Path $PythonScript)) {
        throw "CFB optimizer script not found: $PythonScript"
    }

    # Check OddsAPI key
    $OddsAPIKey = $env:ODDSAPI_KEY
    if ([string]::IsNullOrEmpty($OddsAPIKey) -or $OddsAPIKey -eq "YOUR_ODDSAPI_KEY_HERE") {
        throw "ODDSAPI_KEY environment variable not set. Get your key from: https://the-odds-api.com/"
    }

    # Check Python availability
    try {
        $PythonVersion = & python --version 2>&1
        Write-EQ12Log "Python version: $PythonVersion" "DEBUG"
    } catch {
        throw "Python not available in PATH. Ensure Python 3.12+ is installed."
    }

    # Validate promo date is Friday
    try {
        $PromoDateTime = [DateTime]::ParseExact($PromoDate, "yyyy-MM-dd", $null)
        if ($PromoDateTime.DayOfWeek -ne [DayOfWeek]::Friday) {
            Write-EQ12Log "Warning: $PromoDate is not a Friday. DK Mystery Boost promos typically run on Fridays." "WARN"
        }
    } catch {
        throw "Invalid promo date format. Use YYYY-MM-DD (e.g., 2025-10-03)"
    }

    Write-EQ12Log "Environment validation passed"
}

# Run CFB optimization
function Invoke-CFBOptimization {
    Write-EQ12Log "Starting NCAA CFB Mystery Profit Boost optimization..."
    Write-EQ12Log "Parameters: ${TokenPercent}% boost, $${Stake} stake, ${PromoDate}"

    # Set environment variables for Python script
    $env:CFB_TOKEN_PERCENT = $TokenPercent.ToString()
    $env:CFB_STAKE = $Stake.ToString()
    $env:CFB_PROMO_DATE = $PromoDate

    if ($NoEQ12Integration) {
        $env:CFB_NO_EQ12_INTEGRATION = "true"
    } else {
        $env:CFB_NO_EQ12_INTEGRATION = "false"
    }

    try {
        # Execute Python optimizer
        Write-EQ12Log "Executing CFB optimizer..." "DEBUG"

        if ($Verbose) {
            & python $PythonScript
        } else {
            $Output = & python $PythonScript 2>&1
            Write-Host $Output
        }

        if ($LASTEXITCODE -ne 0) {
            throw "CFB optimizer failed with exit code: $LASTEXITCODE"
        }

        Write-EQ12Log "CFB optimization completed successfully"

        # Show quick analytics if EQ12 integration enabled
        if (-not $NoEQ12Integration) {
            Write-EQ12Log "📊 View detailed analytics at: http://localhost:8000/api/cfb/analytics"
            Write-EQ12Log "💾 Results stored in: C:\EQ12\eq12_bets.db"
        }

    } catch {
        Write-EQ12Log "CFB optimization failed: $($_.Exception.Message)" "ERROR"
        throw
    } finally {
        # Clean up environment variables
        Remove-Item Env:CFB_TOKEN_PERCENT -ErrorAction SilentlyContinue
        Remove-Item Env:CFB_STAKE -ErrorAction SilentlyContinue
        Remove-Item Env:CFB_PROMO_DATE -ErrorAction SilentlyContinue
        Remove-Item Env:CFB_NO_EQ12_INTEGRATION -ErrorAction SilentlyContinue
    }
}

# Generate execution summary
function Write-ExecutionSummary {
    $Summary = @{
        "script"      = "eq12_cfb_optimizer.ps1"
        "version"     = "2.0.0"
        "timestamp"   = (Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
        "parameters"  = @{
            "token_percent"    = $TokenPercent
            "stake"            = $Stake
            "promo_date"       = $PromoDate
            "eq12_integration" = (-not $NoEQ12Integration)
        }
        "environment" = @{
            "python_script"  = $PythonScript
            "logs_directory" = $EQ12LogsDir
            "log_file"       = $LogFile
        }
    }

    $SummaryFile = Join-Path $EQ12LogsDir "cfb_optimization_summary_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    $Summary | ConvertTo-Json -Depth 3 | Out-File $SummaryFile -Encoding UTF8

    Write-EQ12Log "Execution summary saved: $SummaryFile" "DEBUG"
}

# Main execution block
try {
    Write-EQ12Log "=== EQ12 NCAA CFB Mystery Profit Boost Optimizer ==="
    Write-EQ12Log "Starting execution at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')"

    # Validate environment
    Test-EQ12Environment

    # Run optimization
    Invoke-CFBOptimization

    # Generate summary
    Write-ExecutionSummary

    Write-EQ12Log "✅ CFB optimization completed successfully"
    Write-EQ12Log "📋 Full execution log: $LogFile"

    exit 0
} catch {
    Write-EQ12Log "❌ CFB optimization failed: $($_.Exception.Message)" "ERROR"
    Write-EQ12Log "🔍 Check log file for details: $LogFile"

    # Generate error summary
    $ErrorSummary = @{
        "script"      = "eq12_cfb_optimizer.ps1"
        "timestamp"   = (Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
        "error"       = $_.Exception.Message
        "stack_trace" = $_.ScriptStackTrace
        "parameters"  = @{
            "token_percent" = $TokenPercent
            "stake"         = $Stake
            "promo_date"    = $PromoDate
        }
    }

    $ErrorFile = Join-Path $EQ12LogsDir "cfb_optimization_error_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    $ErrorSummary | ConvertTo-Json -Depth 3 | Out-File $ErrorFile -Encoding UTF8

    exit 1
}
