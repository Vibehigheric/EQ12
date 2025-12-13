# EQ12 Environment Scanner & Upgrader - PowerShell Wrapper
# ======================================================
# Easy-to-use PowerShell interface for .env scanning and upgrading

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$Workspace = "C:\EQ12",
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("scan", "upgrade", "report", "backup", "test")]
    [string]$Action = "scan",
    
    [switch]$VerboseOutput,
    [switch]$TestAPIKeys,
    [switch]$CreateBackup,
    [switch]$GenerateReport
)

# Set error handling
$ErrorActionPreference = "Stop"
Set-Location $Workspace

function Write-ScanLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp | $Level | ENV-SCANNER | $Message"
    Add-Content -Path "$Workspace\logs\env_scanner_wrapper.log" -Value $logEntry -Encoding UTF8
    
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "Cyan" }
    }
    Write-Host $logEntry -ForegroundColor $color
}

function Test-Prerequisites {
    Write-ScanLog " Checking prerequisites..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-ScanLog " Python found: $pythonVersion" "SUCCESS"
    }
    catch {
        Write-ScanLog " Python not found or not in PATH" "ERROR"
        throw "Python is required but not found"
    }
    
    # Check requests module
    try {
        python -c "import requests" 2>$null
        Write-ScanLog " Python requests module available" "SUCCESS"
    }
    catch {
        Write-ScanLog " Installing requests module..." "WARNING"
        pip install requests
    }
    
    # Create logs directory
    if (-not (Test-Path "$Workspace\logs")) {
        New-Item -Path "$Workspace\logs" -ItemType Directory -Force | Out-Null
        Write-ScanLog " Created logs directory" "SUCCESS"
    }
}

function Invoke-EnvironmentScan {
    Write-ScanLog " Starting environment scan..."
    
    $pythonArgs = @(
        "$Workspace\scripts\eq12_env_scanner_upgrader.py"
        "--workspace", $Workspace
        "--scan-only"
    )
    
    if ($VerboseOutput) {
        $pythonArgs += "--verbose"
    }
    
    if ($TestAPIKeys) {
        $pythonArgs += "--test-keys", "10"
    }
    
    try {
        & python @pythonArgs
        Write-ScanLog " Environment scan completed successfully" "SUCCESS"
    }
    catch {
        Write-ScanLog " Environment scan failed: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Invoke-EnvironmentUpgrade {
    Write-ScanLog " Starting environment upgrade..."
    
    # Create backup first if requested
    if ($CreateBackup) {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupDir = "$Workspace\backups\env_manual_backup_$timestamp"
        New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
        
        Get-ChildItem -Path $Workspace -Filter "*.env*" | ForEach-Object {
            Copy-Item $_.FullName -Destination $backupDir -Force
        }
        
        Write-ScanLog " Manual backup created: $backupDir" "SUCCESS"
    }
    
    $pythonArgs = @(
        "$Workspace\scripts\eq12_env_scanner_upgrader.py"
        "--workspace", $Workspace
    )
    
    if ($VerboseOutput) {
        $pythonArgs += "--verbose"
    }
    
    if (-not $CreateBackup) {
        $pythonArgs += "--no-backup"
    }
    
    try {
        & python @pythonArgs
        Write-ScanLog " Environment upgrade completed successfully" "SUCCESS"
    }
    catch {
        Write-ScanLog " Environment upgrade failed: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Show-SecurityReport {
    Write-ScanLog " Generating security report..."
    
    # Find the latest report
    $reportFiles = Get-ChildItem -Path "$Workspace\logs" -Filter "env_upgrade_report_*.json" | Sort-Object LastWriteTime -Descending
    
    if ($reportFiles.Count -eq 0) {
        Write-ScanLog " No report files found. Run a scan first." "WARNING"
        return
    }
    
    $latestReport = $reportFiles[0]
    $reportData = Get-Content $latestReport.FullName | ConvertFrom-Json
    
    Write-Host "`n EQ12 ENVIRONMENT SECURITY REPORT" -ForegroundColor Green
    Write-Host "===================================" -ForegroundColor Green
    Write-Host "Generated: $($reportData.timestamp)" -ForegroundColor Cyan
    Write-Host "Security Score: $($reportData.security_score)/100" -ForegroundColor $(if ($reportData.security_score -ge 80) { "Green" } elseif ($reportData.security_score -ge 60) { "Yellow" } else { "Red" })
    
    Write-Host "`n ISSUES SUMMARY:" -ForegroundColor Yellow
    $criticalIssues = $reportData.issues_found | Where-Object { $_.severity -eq "critical" }
    $warningIssues = $reportData.issues_found | Where-Object { $_.severity -eq "warning" }
    $infoIssues = $reportData.issues_found | Where-Object { $_.severity -eq "info" }
    
    Write-Host "   Critical: $($criticalIssues.Count)" -ForegroundColor Red
    Write-Host "   Warning: $($warningIssues.Count)" -ForegroundColor Yellow
    Write-Host "   Info: $($infoIssues.Count)" -ForegroundColor Cyan
    
    Write-Host "`n API KEYS ANALYSIS:" -ForegroundColor Yellow
    $totalKeys = $reportData.api_keys.Count
    $placeholderKeys = ($reportData.api_keys | Where-Object { $_.is_placeholder }).Count
    $validKeys = $totalKeys - $placeholderKeys
    
    Write-Host "  Total API Keys: $totalKeys" -ForegroundColor Cyan
    Write-Host "  Valid Keys: $validKeys" -ForegroundColor Green
    Write-Host "  Placeholder Keys: $placeholderKeys" -ForegroundColor $(if ($placeholderKeys -eq 0) { "Green" } else { "Red" })
    
    if ($reportData.recommendations.Count -gt 0) {
        Write-Host "`n TOP RECOMMENDATIONS:" -ForegroundColor Yellow
        $reportData.recommendations[0..4] | ForEach-Object {
            Write-Host "   $_" -ForegroundColor Cyan
        }
    }
    
    Write-ScanLog " Security report displayed" "SUCCESS"
}

function Test-APIKeysQuick {
    Write-ScanLog " Quick API key validation..."
    
    $pythonArgs = @(
        "$Workspace\scripts\eq12_env_scanner_upgrader.py"
        "--workspace", $Workspace
        "--scan-only"
        "--test-keys", "5"
    )
    
    if ($VerboseOutput) {
        $pythonArgs += "--verbose"
    }
    
    try {
        & python @pythonArgs
        Write-ScanLog " API key testing completed" "SUCCESS"
    }
    catch {
        Write-ScanLog " API key testing failed: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Show-EnvironmentFiles {
    Write-ScanLog " Discovering environment files..."
    
    $envPatterns = @("*.env*", "*environment*", "config\*env*")
    $foundFiles = @()
    
    foreach ($pattern in $envPatterns) {
        $files = Get-ChildItem -Path $Workspace -Filter $pattern -Recurse -File | Where-Object { 
            $_.Extension -notmatch '\.(md|txt|log)$' 
        }
        $foundFiles += $files
    }
    
    $uniqueFiles = $foundFiles | Sort-Object FullName -Unique
    
    Write-Host "`n DISCOVERED ENVIRONMENT FILES:" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    
    foreach ($file in $uniqueFiles) {
        $relativePath = $file.FullName.Replace($Workspace, ".")
        $size = [math]::Round($file.Length / 1KB, 2)
        $lastModified = $file.LastWriteTime.ToString("yyyy-MM-dd HH:mm")
        
        Write-Host "   $relativePath" -ForegroundColor Cyan
        Write-Host "     Size: ${size}KB | Modified: $lastModified" -ForegroundColor Gray
    }
    
    Write-Host "`n Summary: $($uniqueFiles.Count) environment files found" -ForegroundColor Yellow
    Write-ScanLog " Environment file discovery completed" "SUCCESS"
}

# Main execution logic
Write-ScanLog " EQ12 Environment Scanner & Upgrader starting..."

try {
    # Check prerequisites
    Test-Prerequisites
    
    switch ($Action.ToLower()) {
        "scan" {
            Show-EnvironmentFiles
            Invoke-EnvironmentScan
            if ($GenerateReport) {
                Show-SecurityReport
            }
        }
        "upgrade" {
            Invoke-EnvironmentUpgrade
            Show-SecurityReport
        }
        "report" {
            Show-SecurityReport
        }
        "backup" {
            $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $backupDir = "$Workspace\backups\env_manual_backup_$timestamp"
            New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
            
            Get-ChildItem -Path $Workspace -Filter "*.env*" | ForEach-Object {
                Copy-Item $_.FullName -Destination $backupDir -Force
            }
            
            Write-ScanLog " Environment backup created: $backupDir" "SUCCESS"
        }
        "test" {
            Test-APIKeysQuick
        }
        default {
            Write-ScanLog " Unknown action: $Action" "ERROR"
            Write-Host "Available actions: scan, upgrade, report, backup, test" -ForegroundColor Yellow
        }
    }
    
    Write-ScanLog " Environment scanner completed successfully" "SUCCESS"
    
}
catch {
    Write-ScanLog " Environment scanner failed: $($_.Exception.Message)" "ERROR"
    Write-Host "`nFor help, run: Get-Help .\eq12_env_scanner_wrapper.ps1 -Full" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n EQ12 Environment Scanner & Upgrader completed!" -ForegroundColor Green