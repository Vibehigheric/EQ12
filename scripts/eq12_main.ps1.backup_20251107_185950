[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Status", "StartEdge", "Demo", "BuildParlay", "Help")]
    [string]$Action = "Status",
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose
)

<#
.SYNOPSIS
    EQ12 Production Stack PowerShell Wrapper

.DESCRIPTION
    PowerShell wrapper for the complete EQ12 production stack.
    Provides easy access to EdgeFinder service, parlay building, and monitoring.

.PARAMETER Action
    Action to perform:
    - Status: Show system status (default)
    - StartEdge: Start EdgeFinder service 
    - Demo: Run demo mode
    - BuildParlay: Interactive parlay builder
    - Help: Show detailed help

.PARAMETER Verbose
    Enable verbose output

.EXAMPLE
    .\eq12_main.ps1 -Action Status
    Shows current system status

.EXAMPLE
    .\eq12_main.ps1 -Action StartEdge -Verbose
    Starts EdgeFinder service with verbose logging

.EXAMPLE
    .\eq12_main.ps1 -Action Demo
    Runs demo mode with sample data
#>

# Ensure we're in the right directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# EQ12 Configuration
$EQ12Root = "C:\EQ12"
$PythonScript = Join-Path $ScriptDir "eq12_main.py"

function Write-EQ12Banner {
    Write-Host "🚀 EQ12 Production Stack" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Green
    Write-Host "PowerShell Wrapper for EdgeFinder & Parlay Builder" -ForegroundColor Yellow
    Write-Host ""
}

function Test-EQ12Environment {
    param([bool]$ShowDetails = $false)
    
    $Issues = @()
    
    # Check Python
    try {
        $PythonVersion = & python --version 2>$null
        if ($ShowDetails) {
            Write-Host "✅ Python: $PythonVersion" -ForegroundColor Green
        }
    }
    catch {
        $Issues += "Python not found in PATH"
    }
    
    # Check core files
    $RequiredFiles = @(
        "eq12_main.py",
        "eq12_edgefinder.py", 
        "eq12_parlay_builder.py",
        "eq12_math.py",
        "eq12_timezone.py",
        "eq12_responses_client.py"
    )
    
    foreach ($File in $RequiredFiles) {
        $FilePath = Join-Path $ScriptDir $File
        if (Test-Path $FilePath) {
            if ($ShowDetails) {
                $Size = [math]::Round((Get-Item $FilePath).Length / 1KB, 1)
                Write-Host "✅ $File ($Size KB)" -ForegroundColor Green
            }
        }
        else {
            $Issues += "Missing file: $File"
        }
    }
    
    # Check environment variables
    $RequiredEnvVars = @("ODDS_API_KEY", "OPENAI_API_KEY")
    $OptionalEnvVars = @("TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID")
    
    foreach ($Var in $RequiredEnvVars) {
        $Value = [Environment]::GetEnvironmentVariable($Var)
        if ($Value) {
            if ($ShowDetails) {
                $Length = $Value.Length
                Write-Host "✅ $Var (${Length} chars)" -ForegroundColor Green
            }
        }
        else {
            $Issues += "Missing environment variable: $Var"
        }
    }
    
    foreach ($Var in $OptionalEnvVars) {
        $Value = [Environment]::GetEnvironmentVariable($Var)
        if ($Value) {
            if ($ShowDetails) {
                $Length = $Value.Length
                Write-Host "💙 $Var (${Length} chars)" -ForegroundColor Blue
            }
        }
        elseif ($ShowDetails) {
            Write-Host "⚠️ $Var (optional)" -ForegroundColor Yellow
        }
    }
    
    if ($Issues.Count -gt 0) {
        Write-Host "❌ Environment Issues:" -ForegroundColor Red
        foreach ($Issue in $Issues) {
            Write-Host "  • $Issue" -ForegroundColor Red
        }
        return $false
    }
    
    return $true
}

function Invoke-EQ12Action {
    param(
        [string]$ActionName,
        [bool]$VerboseOutput = $false
    )
    
    # Map PowerShell actions to Python arguments
    $PythonArgs = switch ($ActionName) {
        "Status" { "--status" }
        "StartEdge" { "--start-edge" }
        "Demo" { "--demo" }
        "BuildParlay" { "--build-parlay" }
        default { "--status" }
    }
    
    if ($VerboseOutput) {
        Write-Host "🔧 Executing: python $PythonScript $PythonArgs" -ForegroundColor Cyan
        Write-Host ""
    }
    
    try {
        # Execute Python script
        & python $PythonScript $PythonArgs
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Action completed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️ Action completed with exit code: $LASTEXITCODE" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Error "❌ Failed to execute action: $_"
    }
}

function Show-EQ12Help {
    Write-Host @"
🔍 EQ12 Production Stack Help
================================

Available Actions:
  Status      Show system status and component health
  StartEdge   Start the EdgeFinder daemon service
  Demo        Run demo mode with sample parlay data
  BuildParlay Interactive parlay builder
  Help        Show this help message

Environment Setup:
  Required:
    ODDS_API_KEY     - The Odds API key for fetching odds
    OPENAI_API_KEY   - OpenAI API key for AI features
  
  Optional:
    TELEGRAM_TOKEN   - Telegram bot token for alerts
    TELEGRAM_CHAT_ID - Telegram chat ID for notifications

Examples:
  .\eq12_main.ps1 -Action Status
  .\eq12_main.ps1 -Action StartEdge -Verbose
  .\eq12_main.ps1 -Action Demo
  .\eq12_main.ps1 -Action BuildParlay

Components:
  • EdgeFinder: Automated odds monitoring and parlay discovery
  • ParlayBuilder: Multi-strategy parlay construction engine  
  • MathUtils: EV calculation and Kelly sizing
  • TimezoneUtils: UTC-aware datetime handling
  • ResponsesClient: AI-powered normalization and analysis

For more information, visit: https://github.com/your-org/EQ12
"@ -ForegroundColor White
}

# Main execution
try {
    Write-EQ12Banner
    
    # Handle Help action first
    if ($Action -eq "Help") {
        Show-EQ12Help
        exit 0
    }
    
    # Test environment
    Write-Host "🔧 Environment Check:" -ForegroundColor Cyan
    $EnvOK = Test-EQ12Environment -ShowDetails:$Verbose
    Write-Host ""
    
    if (-not $EnvOK) {
        Write-Host "❌ Environment check failed. Run with -Action Help for setup info." -ForegroundColor Red
        exit 1
    }
    
    # Execute requested action
    Write-Host "🎯 Executing Action: $Action" -ForegroundColor Magenta
    Write-Host ""
    
    Invoke-EQ12Action -ActionName $Action -VerboseOutput:$Verbose
}
catch {
    Write-Error "❌ Script failed: $_"
    exit 1
}
finally {
    Write-Host ""
    Write-Host "🎉 EQ12 PowerShell wrapper complete" -ForegroundColor Green
}