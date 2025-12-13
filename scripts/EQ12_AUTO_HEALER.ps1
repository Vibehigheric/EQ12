<#
.SYNOPSIS
    EQ12_AUTO_HEALER.ps1 - PowerShell orchestrator for autonomous system diagnostics + auto-healing

.DESCRIPTION
    Wrapper for eq12_system_scan.py with structured logging, error handling, and Telegram alerts
    Contract: Runs Python diagnostic engine, captures output to logs/, auto-fixes safe issues

.PARAMETER Verbose
    Enable verbose logging

.PARAMETER AutoFix
    Automatically execute fixes for auto-fixable issues

.PARAMETER TelegramAlert
    Send Telegram alert if critical issues detected

.EXAMPLE
    .\EQ12_AUTO_HEALER.ps1 -Verbose
    .\EQ12_AUTO_HEALER.ps1 -AutoFix -TelegramAlert
#>

[CmdletBinding()]
param(
    [switch]$AutoFix,
    [switch]$TelegramAlert
)

$ErrorActionPreference = "Stop"

# Paths
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PythonScript = Join-Path $RepoRoot "scripts\eq12_system_scan.py"
$LogDir = Join-Path $RepoRoot "logs"

# Ensure logs directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Log file
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "auto_healer_$Timestamp.log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $LogLine = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] $Message"
    Write-Verbose $LogLine
    Add-Content -Path $LogFile -Value $LogLine
}

try {
    Write-Log "Starting EQ12 Auto-Healer (diagnostic + auto-fix)" "INFO"
    Write-Log "Repository root: $RepoRoot" "INFO"
    
    # Verify Python script exists
    if (-not (Test-Path $PythonScript)) {
        throw "Python scan script not found: $PythonScript"
    }
    
    # Run Python diagnostic engine
    Write-Log "Executing Python diagnostic engine..." "INFO"
    $VerboseFlag = if ($PSBoundParameters['Verbose']) { "--verbose" } else { "" }
    $PythonArgs = @($PythonScript, "--repo-root", $RepoRoot, $VerboseFlag)
    
    $PythonOutput = & python @PythonArgs 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Python scan failed with exit code $LASTEXITCODE" "ERROR"
        Write-Log "Output: $PythonOutput" "ERROR"
        throw "Python scan failed"
    }
    
    Write-Log "Python diagnostic engine completed successfully" "INFO"
    Write-Log "Output: $PythonOutput" "INFO"
    
    # Find most recent scan report
    $ScanReports = Get-ChildItem -Path $LogDir -Filter "system_scan_*.json" | Sort-Object LastWriteTime -Descending
    
    if ($ScanReports.Count -eq 0) {
        throw "No scan report generated"
    }
    
    $LatestReport = $ScanReports[0]
    Write-Log "Latest scan report: $($LatestReport.FullName)" "INFO"
    
    # Parse JSON report
    $Report = Get-Content $LatestReport.FullName | ConvertFrom-Json
    
    # Display summary
    Write-Host ""
    Write-Host "="*60 -ForegroundColor Cyan
    Write-Host "🏥 SYSTEM HEALTH SCORE: $($Report.health_score)/100" -ForegroundColor $(if ($Report.health_score -ge 80) { "Green" } elseif ($Report.health_score -ge 60) { "Yellow" } else { "Red" })
    Write-Host "="*60 -ForegroundColor Cyan
    Write-Host "Total Issues: $($Report.summary.total_issues)" -ForegroundColor White
    Write-Host "  - Critical: $($Report.summary.critical)" -ForegroundColor Red
    Write-Host "  - High: $($Report.summary.high)" -ForegroundColor Magenta
    Write-Host "  - Medium: $($Report.summary.medium)" -ForegroundColor Yellow
    Write-Host "  - Low: $($Report.summary.low)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Auto-Fixable: $($Report.summary.auto_fixable)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Recommendations:" -ForegroundColor Cyan
    foreach ($rec in $Report.recommendations) {
        Write-Host "  $rec" -ForegroundColor White
    }
    Write-Host ""
    
    # Auto-fix if requested
    if ($AutoFix) {
        Write-Log "Auto-fix mode enabled" "INFO"
        $FixableIssues = $Report.issues | Where-Object { $_.auto_fix_available -and $_.fix_command }
        
        if ($FixableIssues.Count -eq 0) {
            Write-Host "✅ No auto-fixable issues found" -ForegroundColor Green
        } else {
            Write-Host "🔧 Applying $($FixableIssues.Count) auto-fixes..." -ForegroundColor Yellow
            
            foreach ($issue in $FixableIssues) {
                Write-Host "  - Fixing: $($issue.title)" -ForegroundColor Cyan
                Write-Log "Executing fix: $($issue.fix_command)" "INFO"
                
                try {
                    # Safe fixes only (skip destructive commands)
                    if ($issue.fix_command -match "pip install|mkdir|dotnet add package") {
                        Invoke-Expression $issue.fix_command
                        Write-Host "    ✅ Fixed" -ForegroundColor Green
                    } else {
                        Write-Host "    ⚠️ Skipped (requires manual review)" -ForegroundColor Yellow
                        Write-Log "Skipped potentially unsafe fix: $($issue.fix_command)" "WARN"
                    }
                } catch {
                    Write-Host "    ❌ Failed: $_" -ForegroundColor Red
                    Write-Log "Fix failed: $_" "ERROR"
                }
            }
        }
    }
    
    # Send Telegram alert if critical issues detected
    if ($TelegramAlert -and $Report.summary.critical -gt 0) {
        Write-Log "Critical issues detected - sending Telegram alert" "WARN"
        
        $TelegramToken = $env:TELEGRAM_BOT_TOKEN
        $TelegramChatId = $env:TELEGRAM_CHAT_ID
        
        if ($TelegramToken -and $TelegramChatId) {
            $Message = "🚨 EQ12 CRITICAL ALERT`n`nHealth Score: $($Report.health_score)/100`nCritical Issues: $($Report.summary.critical)`n`nAction required!"
            $Uri = "https://api.telegram.org/bot$TelegramToken/sendMessage"
            $Body = @{
                chat_id = $TelegramChatId
                text = $Message
            } | ConvertTo-Json
            
            try {
                Invoke-RestMethod -Uri $Uri -Method Post -ContentType "application/json" -Body $Body | Out-Null
                Write-Log "Telegram alert sent" "INFO"
                Write-Host "📱 Telegram alert sent" -ForegroundColor Green
            } catch {
                Write-Log "Failed to send Telegram alert: $_" "ERROR"
                Write-Host "❌ Telegram alert failed: $_" -ForegroundColor Red
            }
        } else {
            Write-Log "Telegram credentials not configured (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)" "WARN"
            Write-Host "⚠️  Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables." -ForegroundColor Yellow
        }
    }
    
    Write-Log "Auto-Healer completed successfully" "INFO"
    Write-Host "✅ Scan complete. Full report: $($LatestReport.FullName)" -ForegroundColor Green
    
    # Return summary for pipeline usage
    return @{
        ReportFile = $LatestReport.FullName
        HealthScore = $Report.health_score
        TotalIssues = $Report.summary.total_issues
        CriticalIssues = $Report.summary.critical
        AutoFixable = $Report.summary.auto_fixable
    }
    
}
catch {
    Write-Log "Auto-Healer failed: $_" "ERROR"
    Write-Host "❌ Auto-Healer failed: $_" -ForegroundColor Red
    exit 1
}
