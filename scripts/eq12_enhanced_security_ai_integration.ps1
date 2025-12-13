#!/usr/bin/env pwsh
<#
.SYNOPSIS
    EQ12 Enhanced Security & AI Integration System - PowerShell Wrapper
    
.DESCRIPTION
    PowerShell wrapper for the enhanced security analysis system that combines
    Snyk Open Source vulnerability detection with OpenAI Cookbook patterns.
    Provides comprehensive analysis of the EQ12 betting platform with
    automated dashboard generation including hardcoded URLs.

.PARAMETER Analyze
    Run comprehensive security and AI integration analysis

.PARAMETER GenerateDashboard
    Generate enhanced dashboard with hardcoded links

.PARAMETER SnykOnly
    Run Snyk analysis only

.PARAMETER AIPatternsOnly
    Analyze AI patterns only

.PARAMETER Verbose
    Enable verbose logging

.EXAMPLE
    .\eq12_enhanced_security_ai_integration.ps1 -Analyze -Verbose
    
.EXAMPLE
    .\eq12_enhanced_security_ai_integration.ps1 -GenerateDashboard

.NOTES
    Author: EQ12 Development Team
    Created: 2025-10-09
    Version: 2.0.0
    
    This wrapper ensures proper PowerShell integration while maintaining
    all Python functionality for comprehensive security analysis.
#>

[CmdletBinding()]
param(
    [Parameter(HelpMessage="Run comprehensive security and AI integration analysis")]
    [switch]$Analyze,
    
    [Parameter(HelpMessage="Generate enhanced dashboard with hardcoded links")]
    [switch]$GenerateDashboard,
    
    [Parameter(HelpMessage="Run Snyk analysis only")]
    [switch]$SnykOnly,
    
    [Parameter(HelpMessage="Analyze AI patterns only")]
    [switch]$AIPatternsOnly,
    
    [Parameter(HelpMessage="Enable verbose logging")]
    [switch]$Verbose
)

# Enhanced error handling and logging
$ErrorActionPreference = "Stop"
$VerbosePreference = if ($Verbose) { "Continue" } else { "SilentlyContinue" }

try {
    # Initialize EQ12 environment
    Write-Host "[SECURE] EQ12 Enhanced Security & AI Integration System" -ForegroundColor Cyan
    Write-Host "=========================================================" -ForegroundColor Gray
    
    # Validate Python environment
    $pythonPath = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonPath) {
        throw "Python is not installed or not in PATH. Please install Python 3.8+ and ensure it's in your PATH."
    }
    
    # Get script directory and repo root
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $repoRoot = Split-Path -Parent $scriptDir
    $pythonScript = Join-Path $scriptDir "eq12_enhanced_security_ai_integration.py"
    
    # Validate Python script exists
    if (-not (Test-Path $pythonScript)) {
        throw "Python script not found: $pythonScript"
    }
    
    # Set working directory
    Push-Location $repoRoot
    
    try {
        # Build command arguments
        $arguments = @()
        
        if ($Analyze -or (-not ($SnykOnly -or $AIPatternsOnly -or $GenerateDashboard))) {
            $arguments += "--analyze"
            Write-Verbose "Running comprehensive analysis"
        }
        
        if ($GenerateDashboard) {
            $arguments += "--generate-dashboard"
            Write-Verbose "Generating enhanced dashboard"
        }
        
        if ($SnykOnly) {
            $arguments += "--snyk-only"
            Write-Verbose "Running Snyk analysis only"
        }
        
        if ($AIPatternsOnly) {
            $arguments += "--ai-patterns-only"
            Write-Verbose "Analyzing AI patterns only"
        }
        
        if ($Verbose) {
            $arguments += "--verbose"
        }
        
        # Execute Python script
        Write-Host "[START] Executing enhanced security analysis..." -ForegroundColor Green
        Write-Verbose "Command: python $pythonScript $($arguments -join ' ')"
        
        $process = Start-Process -FilePath "python" -ArgumentList @($pythonScript) + $arguments -NoNewWindow -Wait -PassThru
        
        if ($process.ExitCode -eq 0) {
            Write-Host "[OK] Enhanced security & AI integration analysis completed successfully" -ForegroundColor Green
            
            # Check for generated dashboards
            $dashboardDir = Join-Path $repoRoot "generated_dashboards"
            if (Test-Path $dashboardDir) {
                $dashboards = Get-ChildItem $dashboardDir -Filter "enhanced_security_ai_dashboard_*.html" | Sort-Object LastWriteTime -Descending | Select-Object -First 3
                
                if ($dashboards.Count -gt 0) {
                    Write-Host "`n[REPORT] Generated Dashboards:" -ForegroundColor Yellow
                    foreach ($dashboard in $dashboards) {
                        $url = "https://eq12.local/dashboards/$($dashboard.Name)"
                        Write-Host "  [LINK] $url" -ForegroundColor Cyan
                    }
                }
            }
            
            # Check for generated reports
            $logsDir = Join-Path $repoRoot "logs"
            if (Test-Path $logsDir) {
                $reports = Get-ChildItem $logsDir -Filter "enhanced_security_ai_report_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
                
                if ($reports.Count -gt 0) {
                    Write-Host "`n[METRIC] Latest Report: $($reports[0].Name)" -ForegroundColor Magenta
                }
            }
            
        } else {
            Write-Error "Enhanced security analysis failed with exit code: $($process.ExitCode)"
            exit $process.ExitCode
        }
        
    } finally {
        Pop-Location
    }
    
} catch {
    Write-Error "EQ12 Enhanced Security & AI Integration failed: $($_.Exception.Message)"
    Write-Verbose "Full error: $($_.Exception.ToString())"
    exit 1
}

# Success summary
Write-Host "`n=========================================================" -ForegroundColor Gray
Write-Host "[SECURE] EQ12 Enhanced Security & AI Integration Complete" -ForegroundColor Green
Write-Host "For detailed logs, check: C:\EQ12\logs\enhanced_security_ai.log" -ForegroundColor Gray
Write-Host "=========================================================" -ForegroundColor Gray