#Requires -Version 5.1

<#
.SYNOPSIS
    EQ12 System Health Analyzer PowerShell Wrapper

.DESCRIPTION
    PowerShell wrapper for the EQ12 comprehensive system health analysis tool.
    Provides Windows-native interface for scanning logs, fixing issues, and monitoring system health.

.PARAMETER Action
    Action to perform: Analyze, Fix, Report, Monitor

.PARAMETER Verbose
    Enable verbose logging and output

.PARAMETER LogPath
    Custom log directory path (defaults to C:\EQ12\logs)

.PARAMETER AutoFix
    Automatically apply fixes for detected issues

.EXAMPLE
    .\eq12_system_health_analyzer.ps1 -Action Analyze
    Run comprehensive system health analysis

.EXAMPLE
    .\eq12_system_health_analyzer.ps1 -Action Fix -Verbose
    Run analysis and apply automatic fixes with verbose output

.EXAMPLE
    .\eq12_system_health_analyzer.ps1 -Action Monitor
    Start continuous health monitoring

.NOTES
    Author: EQ12 AI Agent
    Version: 1.0.0
    Requires Python 3.12+ and EQ12 system health analyzer
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("Analyze", "Fix", "Report", "Monitor", "Status")]
    [string]$Action = "Analyze",
    
    [Parameter(Mandatory = $false)]
    [switch]$Verbose,
    
    [Parameter(Mandatory = $false)]
    [string]$LogPath = "C:\EQ12\logs",
    
    [Parameter(Mandatory = $false)]
    [switch]$AutoFix,
    
    [Parameter(Mandatory = $false)]
    [switch]$ReportOnly
)

# EQ12 System Health Analyzer PowerShell Wrapper
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Define paths
$EQ12Root = "C:\EQ12"
$ScriptsPath = Join-Path $EQ12Root "scripts"
$LogsPath = Join-Path $EQ12Root "logs"
$AnalyzerScript = Join-Path $ScriptsPath "eq12_system_health_analyzer.py"

# Logging setup
$LogFile = Join-Path $LogsPath "health_analyzer_wrapper_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "$Timestamp - $Level - $Message"
    
    switch ($Level) {
        "ERROR" { Write-Host $LogEntry -ForegroundColor Red }
        "WARNING" { Write-Host $LogEntry -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $LogEntry -ForegroundColor Green }
        default { Write-Host $LogEntry -ForegroundColor Cyan }
    }
    
    # Also write to log file
    Add-Content -Path $LogFile -Value $LogEntry -ErrorAction SilentlyContinue
}

function Test-Prerequisites {
    <#
    .SYNOPSIS
        Test system prerequisites for health analysis
    #>
    
    Write-Log "🔍 Checking system prerequisites..."
    
    # Check if EQ12 root exists
    if (-not (Test-Path $EQ12Root)) {
        Write-Log "EQ12 root directory not found: $EQ12Root" "ERROR"
        return $false
    }
    
    # Check if logs directory exists
    if (-not (Test-Path $LogsPath)) {
        Write-Log "Creating logs directory: $LogsPath" "WARNING"
        New-Item -Path $LogsPath -ItemType Directory -Force | Out-Null
    }
    
    # Check if analyzer script exists
    if (-not (Test-Path $AnalyzerScript)) {
        Write-Log "System health analyzer script not found: $AnalyzerScript" "ERROR"
        return $false
    }
    
    # Check Python availability
    try {
        $PythonVersion = python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Python available: $PythonVersion"
        } else {
            Write-Log "Python not found or not accessible" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Error checking Python: $_" "ERROR"
        return $false
    }
    
    Write-Log "✅ All prerequisites satisfied"
    return $true
}

function Invoke-SystemHealthAnalysis {
    <#
    .SYNOPSIS
        Run comprehensive system health analysis
    #>
    
    Write-Log "🚀 Starting EQ12 comprehensive system health analysis..."
    
    # Build Python command arguments
    $PythonArgs = @()
    
    if ($Verbose) {
        $PythonArgs += "--verbose"
    }
    
    if ($AutoFix -or $Action -eq "Fix") {
        $PythonArgs += "--fix"
    }
    
    if ($ReportOnly -or $Action -eq "Report") {
        $PythonArgs += "--report-only"
    }
    
    try {
        # Run the Python analyzer
        Write-Log "Executing: python `"$AnalyzerScript`" $($PythonArgs -join ' ')"
        
        $ProcessStartInfo = New-Object System.Diagnostics.ProcessStartInfo
        $ProcessStartInfo.FileName = "python"
        $ProcessStartInfo.Arguments = "`"$AnalyzerScript`" $($PythonArgs -join ' ')"
        $ProcessStartInfo.UseShellExecute = $false
        $ProcessStartInfo.RedirectStandardOutput = $true
        $ProcessStartInfo.RedirectStandardError = $true
        $ProcessStartInfo.WorkingDirectory = $EQ12Root
        
        $Process = New-Object System.Diagnostics.Process
        $Process.StartInfo = $ProcessStartInfo
        $Process.Start() | Out-Null
        
        # Capture output
        $StdOut = $Process.StandardOutput.ReadToEnd()
        $StdErr = $Process.StandardError.ReadToEnd()
        $Process.WaitForExit()
        
        $ExitCode = $Process.ExitCode
        
        # Display output
        if ($StdOut) {
            Write-Host $StdOut
        }
        
        if ($StdErr) {
            Write-Log "Analysis stderr: $StdErr" "WARNING"
        }
        
        # Interpret exit code
        switch ($ExitCode) {
            0 { 
                Write-Log "✅ System health analysis completed successfully - Excellent health (75-100)" "SUCCESS"
                return @{ Success = $true; HealthCategory = "Excellent"; ExitCode = $ExitCode }
            }
            1 { 
                Write-Log "⚠️ System health analysis completed - Fair health (50-74), some issues found" "WARNING"
                return @{ Success = $true; HealthCategory = "Fair"; ExitCode = $ExitCode }
            }
            2 { 
                Write-Log "🚨 System health analysis completed - Poor health (<50), critical issues found" "ERROR"
                return @{ Success = $true; HealthCategory = "Poor"; ExitCode = $ExitCode }
            }
            130 { 
                Write-Log "🛑 System health analysis interrupted by user" "WARNING"
                return @{ Success = $false; HealthCategory = "Interrupted"; ExitCode = $ExitCode }
            }
            default { 
                Write-Log "💥 System health analysis failed with exit code: $ExitCode" "ERROR"
                return @{ Success = $false; HealthCategory = "Failed"; ExitCode = $ExitCode }
            }
        }
        
    } catch {
        Write-Log "Error running system health analysis: $_" "ERROR"
        return @{ Success = $false; Error = $_.Exception.Message }
    }
}

function Get-LatestHealthReport {
    <#
    .SYNOPSIS
        Get the latest system health report
    #>
    
    Write-Log "📊 Retrieving latest system health report..."
    
    try {
        # Find latest health report
        $HealthReports = Get-ChildItem -Path $LogsPath -Filter "system_health_report_*.json" -ErrorAction SilentlyContinue |
                        Sort-Object LastWriteTime -Descending
        
        if (-not $HealthReports) {
            Write-Log "No system health reports found" "WARNING"
            return $null
        }
        
        $LatestReport = $HealthReports[0]
        Write-Log "Latest health report: $($LatestReport.Name)"
        
        # Parse JSON report
        $ReportContent = Get-Content -Path $LatestReport.FullName -Raw | ConvertFrom-Json
        
        return @{
            ReportFile = $LatestReport.FullName
            Timestamp = $ReportContent.timestamp
            HealthScore = $ReportContent.health_score
            LogsScanned = $ReportContent.total_logs_scanned
            CriticalErrors = $ReportContent.critical_errors.Count
            PerformanceIssues = $ReportContent.performance_issues.Count
            FixesApplied = $ReportContent.fixes_applied.Count
            Recommendations = $ReportContent.system_recommendations
        }
        
    } catch {
        Write-Log "Error retrieving health report: $_" "ERROR"
        return $null
    }
}

function Show-HealthStatus {
    <#
    .SYNOPSIS
        Display current system health status
    #>
    
    Write-Host "`n" + "="*70 -ForegroundColor Cyan
    Write-Host "🏥 EQ12 SYSTEM HEALTH STATUS" -ForegroundColor Cyan
    Write-Host "="*70 -ForegroundColor Cyan
    
    $HealthReport = Get-LatestHealthReport
    
    if ($HealthReport) {
        Write-Host "`n📊 Health Score: $($HealthReport.HealthScore)/100" -ForegroundColor White
        
        if ($HealthReport.HealthScore -ge 90) {
            Write-Host "🎉 EXCELLENT: System health is outstanding!" -ForegroundColor Green
        } elseif ($HealthReport.HealthScore -ge 75) {
            Write-Host "✅ GOOD: System health is acceptable with minor issues" -ForegroundColor Green
        } elseif ($HealthReport.HealthScore -ge 50) {
            Write-Host "⚠️ FAIR: System has moderate issues requiring attention" -ForegroundColor Yellow
        } else {
            Write-Host "🚨 POOR: System has critical issues requiring immediate action" -ForegroundColor Red
        }
        
        Write-Host "`n📈 System Metrics:" -ForegroundColor White
        Write-Host "   📁 Logs Scanned: $($HealthReport.LogsScanned)" -ForegroundColor Gray
        Write-Host "   🚨 Critical Errors: $($HealthReport.CriticalErrors)" -ForegroundColor Gray
        Write-Host "   ⚡ Performance Issues: $($HealthReport.PerformanceIssues)" -ForegroundColor Gray
        Write-Host "   🛠️ Fixes Applied: $($HealthReport.FixesApplied)" -ForegroundColor Gray
        Write-Host "   📅 Last Analysis: $($HealthReport.Timestamp)" -ForegroundColor Gray
        
        if ($HealthReport.Recommendations -and $HealthReport.Recommendations.Count -gt 0) {
            Write-Host "`n💡 Top Recommendations:" -ForegroundColor White
            for ($i = 0; $i -lt [Math]::Min(5, $HealthReport.Recommendations.Count); $i++) {
                Write-Host "   $($i + 1). $($HealthReport.Recommendations[$i])" -ForegroundColor Gray
            }
        }
        
        Write-Host "`n📝 Full report: $($HealthReport.ReportFile)" -ForegroundColor Gray
        
    } else {
        Write-Host "`n❓ No system health reports available" -ForegroundColor Yellow
        Write-Host "Run: .\eq12_system_health_analyzer.ps1 -Action Analyze" -ForegroundColor Gray
    }
    
    Write-Host ""
}

function Start-HealthMonitoring {
    <#
    .SYNOPSIS
        Start continuous health monitoring
    #>
    
    Write-Log "🔄 Starting continuous health monitoring..."
    Write-Log "Press Ctrl+C to stop monitoring"
    
    try {
        while ($true) {
            Write-Log "Running scheduled health check..."
            
            $Result = Invoke-SystemHealthAnalysis
            
            if ($Result.Success) {
                Write-Log "Health check completed - Status: $($Result.HealthCategory)"
            } else {
                Write-Log "Health check failed: $($Result.Error)" "ERROR"
            }
            
            # Wait 30 minutes before next check
            Write-Log "Next health check in 30 minutes..."
            Start-Sleep -Seconds 1800
        }
    } catch [System.Management.Automation.BreakException] {
        Write-Log "Health monitoring stopped by user"
    } catch {
        Write-Log "Error in health monitoring: $_" "ERROR"
    }
}

# Main execution
function Main {
    Write-Log "🏥 EQ12 System Health Analyzer Wrapper v1.0.0"
    Write-Log "Action: $Action"
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        Write-Log "Prerequisites not met. Exiting." "ERROR"
        exit 1
    }
    
    try {
        switch ($Action) {
            "Analyze" {
                $Result = Invoke-SystemHealthAnalysis
                if ($Result.Success) {
                    Show-HealthStatus
                }
            }
            
            "Fix" {
                Write-Log "Running analysis with automatic fixes enabled..."
                $Result = Invoke-SystemHealthAnalysis
                if ($Result.Success) {
                    Show-HealthStatus
                }
            }
            
            "Report" {
                Write-Log "Generating health report only..."
                $Result = Invoke-SystemHealthAnalysis
                if ($Result.Success) {
                    Show-HealthStatus
                }
            }
            
            "Status" {
                Show-HealthStatus
            }
            
            "Monitor" {
                Start-HealthMonitoring
            }
            
            default {
                Write-Log "Unknown action: $Action" "ERROR"
                exit 1
            }
        }
        
        Write-Log "✅ System health analyzer completed successfully" "SUCCESS"
        
    } catch {
        Write-Log "System health analyzer failed: $_" "ERROR"
        exit 1
    }
}

# Execute main function
Main