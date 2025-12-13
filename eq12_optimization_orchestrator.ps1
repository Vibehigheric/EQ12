#Requires -Version 5.1

<#
.SYNOPSIS
    EQ12 Model Optimization Orchestrator PowerShell Wrapper

.DESCRIPTION
    Provides PowerShell interface for EQ12 model optimization workflows.
    Integrates with the Python-based optimization orchestrator for comprehensive model evaluation and improvement.

.PARAMETER UseCase
    The EQ12 use case to optimize:
    - betting_analysis: Analyze betting odds and generate insights
    - cannabis_compliance: Generate compliance reports for cannabis operations
    - credit_assessment: Assess credit risks and generate reports
    - governance_automation: Automate governance and security workflows
    - code_generation: Generate and review code for EQ12 systems

.PARAMETER Action
    The optimization action to perform:
    - evaluate: Run comprehensive evaluation only
    - optimize: Full optimization pipeline with recommendations
    - report: Generate optimization report from existing results

.PARAMETER OutputPath
    Optional path for saving the optimization report

.PARAMETER LogLevel
    Logging level (DEBUG, INFO, WARNING, ERROR)

.EXAMPLE
    .\eq12_optimization_orchestrator.ps1 -UseCase betting_analysis -Action optimize

.EXAMPLE
    .\eq12_optimization_orchestrator.ps1 -UseCase cannabis_compliance -Action evaluate -OutputPath "C:\EQ12\logs\cannabis_eval_report.txt"

.NOTES
    Author: EQ12 System
    Requires: Python 3.12+, OpenAI API key configured
    Dependencies: eq12_advanced_optimizer.py, eq12_openai_optimizer.py
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet("betting_analysis", "cannabis_compliance", "credit_assessment", "governance_automation", "code_generation")]
    [string]$UseCase,

    [ValidateSet("evaluate", "optimize", "report")]
    [string]$Action = "optimize",

    [string]$OutputPath,

    [ValidateSet("DEBUG", "INFO", "WARNING", "ERROR")]
    [string]$LogLevel = "INFO"
)

# Script configuration
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogFile = Join-Path $ScriptDir "logs" "eq12_optimization_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Ensure logs directory exists
$LogDir = Split-Path -Parent $LogFile
if (-not (Test-Path $LogDir)) {
    New-Item -Path $LogDir -ItemType Directory -Force | Out-Null
}

function Write-LogMessage {
    param(
        [Parameter(Mandatory)]
        [string]$Message,

        [ValidateSet("INFO", "WARNING", "ERROR", "DEBUG")]
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    # Write to console with appropriate color
    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "DEBUG" { if ($LogLevel -eq "DEBUG") { Write-Host $logEntry -ForegroundColor Gray } }
        default { Write-Host $logEntry -ForegroundColor White }
    }

    # Write to log file
    Add-Content -Path $LogFile -Value $logEntry -Encoding UTF8
}

function Test-Prerequisites {
    """Verify all prerequisites are met for optimization"""

    Write-LogMessage "Checking prerequisites..." -Level INFO

    # Check Python installation
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found in PATH"
        }
        Write-LogMessage "Python version: $pythonVersion" -Level INFO
    } catch {
        Write-LogMessage "Python 3.12+ is required but not found: $_" -Level ERROR
        return $false
    }

    # Check required Python modules
    $requiredModules = @("openai", "sqlite3", "asyncio")
    foreach ($module in $requiredModules) {
        try {
            $null = & python -c "import $module; print('OK')" 2>&1
            if ($LASTEXITCODE -ne 0) {
                throw "Module $module not available"
            }
            Write-LogMessage "Python module '$module' available" -Level DEBUG
        } catch {
            Write-LogMessage "Required Python module '$module' not found: $_" -Level ERROR
            return $false
        }
    }

    # Check OpenAI API key
    if (-not $env:OPENAI_API_KEY) {
        Write-LogMessage "OPENAI_API_KEY environment variable not set" -Level ERROR
        return $false
    }

    # Check required EQ12 Python files
    $requiredFiles = @(
        "eq12_optimization_orchestrator.py",
        "eq12_advanced_optimizer.py",
        "eq12_openai_optimizer.py"
    )

    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $ScriptDir $file
        if (-not (Test-Path $filePath)) {
            Write-LogMessage "Required file not found: $filePath" -Level ERROR
            return $false
        }
    }

    Write-LogMessage "All prerequisites satisfied" -Level INFO
    return $true
}

function Invoke-OptimizationOrchestrator {
    param(
        [string]$UseCase,
        [string]$Action,
        [string]$OutputPath
    )

    Write-LogMessage "Starting EQ12 optimization orchestrator..." -Level INFO
    Write-LogMessage "Use Case: $UseCase" -Level INFO
    Write-LogMessage "Action: $Action" -Level INFO

    # Build Python command
    $pythonScript = Join-Path $ScriptDir "eq12_optimization_orchestrator.py"
    $arguments = @($UseCase, "--action", $Action)

    if ($OutputPath) {
        $arguments += @("--output", $OutputPath)
    }

    # Set environment variables for Python logging
    $env:PYTHONPATH = $ScriptDir
    $env:EQ12_LOG_LEVEL = $LogLevel

    try {
        Write-LogMessage "Executing: python `"$pythonScript`" $($arguments -join ' ')" -Level DEBUG

        # Run the Python orchestrator
        $result = & python $pythonScript @arguments 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "Optimization orchestrator completed successfully" -Level INFO

            # Display results
            foreach ($line in $result) {
                Write-LogMessage $line -Level INFO
            }

            return $true
        } else {
            Write-LogMessage "Optimization orchestrator failed with exit code: $LASTEXITCODE" -Level ERROR
            foreach ($line in $result) {
                Write-LogMessage $line -Level ERROR
            }
            return $false
        }
    } catch {
        Write-LogMessage "Failed to execute optimization orchestrator: $_" -Level ERROR
        return $false
    }
}

function Export-OptimizationSummary {
    """Export optimization summary for EQ12 dashboard integration"""

    $summaryPath = Join-Path $ScriptDir "logs" "eq12_optimization_summary.json"

    $summary = @{
        timestamp      = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        use_case       = $UseCase
        action         = $Action
        log_file       = $LogFile
        output_path    = $OutputPath
        status         = if ($script:OptimizationSuccess) { "SUCCESS" } else { "FAILED" }
        script_version = "1.0.0"
    }

    $summary | ConvertTo-Json -Depth 3 | Set-Content -Path $summaryPath -Encoding UTF8
    Write-LogMessage "Optimization summary exported to: $summaryPath" -Level INFO
}

# Main execution
try {
    Write-LogMessage "=== EQ12 Model Optimization Orchestrator ===" -Level INFO
    Write-LogMessage "Starting optimization workflow for use case: $UseCase" -Level INFO

    # Verify prerequisites
    if (-not (Test-Prerequisites)) {
        throw "Prerequisites check failed"
    }

    # Run optimization
    $script:OptimizationSuccess = Invoke-OptimizationOrchestrator -UseCase $UseCase -Action $Action -OutputPath $OutputPath

    if ($script:OptimizationSuccess) {
        Write-LogMessage "=== Optimization completed successfully ===" -Level INFO

        # Display log file location
        Write-LogMessage "Detailed logs saved to: $LogFile" -Level INFO

        # Check for generated result files
        $resultPattern = Join-Path $ScriptDir "eq12_optimization_${UseCase}_*.json"
        $resultFiles = Get-ChildItem -Path $resultPattern -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending

        if ($resultFiles) {
            Write-LogMessage "Latest optimization results: $($resultFiles[0].FullName)" -Level INFO
        }
    } else {
        Write-LogMessage "=== Optimization failed ===" -Level ERROR
        exit 1
    }
} catch {
    Write-LogMessage "Critical error in optimization orchestrator: $_" -Level ERROR
    $script:OptimizationSuccess = $false
    exit 1
} finally {
    # Always export summary for monitoring
    Export-OptimizationSummary

    Write-LogMessage "Optimization orchestrator finished" -Level INFO
    Write-LogMessage "Session log: $LogFile" -Level INFO
}
