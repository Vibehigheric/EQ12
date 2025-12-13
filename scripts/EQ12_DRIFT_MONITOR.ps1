# ==================================================================
# EQ12 DRIFT MONITOR - Prevent Environment Corruption
# ==================================================================
# Monitors workspace for signs of drift, corruption, or runaway growth
# Run daily or before major changes to catch problems early
# ==================================================================

[CmdletBinding()]
param(
    [switch]$Continuous,
    [int]$IntervalMinutes = 60,
    [switch]$ExportReport
)

Write-Host "`n=== EQ12 DRIFT MONITOR ===" -ForegroundColor Cyan
Write-Host "Protecting workspace from corruption and runaway growth..." -ForegroundColor Yellow
Write-Host ""

$Root = "C:\EQ12"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Warnings = @()
$Errors = @()

function Test-DriftCondition {
    param(
        [string]$Name,
        [scriptblock]$Condition,
        [string]$Level = "WARNING"
    )
    
    $result = & $Condition
    if ($result.Failed) {
        $message = "$Name - $($result.Message)"
        if ($Level -eq "ERROR") {
            $script:Errors += $message
            Write-Host "  ERROR: $message" -ForegroundColor Red
        } else {
            $script:Warnings += $message
            Write-Host "  WARNING: $message" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  OK: $Name" -ForegroundColor Green
    }
}

do {
    $Warnings = @()
    $Errors = @()
    
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Running drift checks..." -ForegroundColor Cyan
    Write-Host ""
    
    # ==============================================================
    # CHECK 1: Multiple .venv folders
    # ==============================================================
    Test-DriftCondition -Name "Virtual environment count" -Condition {
        $venvFolders = @(Get-ChildItem -Path $Root -Directory -Filter ".venv*" -ErrorAction SilentlyContinue)
        if ($venvFolders.Count -gt 1) {
            return @{ Failed = $true; Message = "Found $($venvFolders.Count) .venv folders (should have only 1)" }
        }
        return @{ Failed = $false }
    }
    
    # ==============================================================
    # CHECK 2: Logs folder size
    # ==============================================================
    Test-DriftCondition -Name "Logs folder size" -Condition {
        $logsPath = "$Root\logs"
        if (Test-Path $logsPath) {
            $sizeMB = [math]::Round((Get-ChildItem -Path $logsPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
            if ($sizeMB -gt 250) {
                return @{ Failed = $true; Message = "Logs folder is $sizeMB MB (should be < 250 MB)" }
            }
        }
        return @{ Failed = $false }
    }
    
    # ==============================================================
    # CHECK 3: node_modules size
    # ==============================================================
    Test-DriftCondition -Name "node_modules size" -Condition {
        $nodeModulesPath = "$Root\node_modules"
        if (Test-Path $nodeModulesPath) {
            $sizeMB = [math]::Round((Get-ChildItem -Path $nodeModulesPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
            if ($sizeMB -gt 500) {
                return @{ Failed = $true; Message = "node_modules is $sizeMB MB (should be < 500 MB)" }
            }
        }
        return @{ Failed = $false }
    }
    
    # ==============================================================
    # CHECK 4: Git repository health
    # ==============================================================
    Test-DriftCondition -Name "Git lock files" -Condition {
        $lockFiles = @(Get-ChildItem -Path "$Root\.git" -Recurse -Filter "*.lock" -ErrorAction SilentlyContinue)
        if ($lockFiles.Count -gt 0) {
            return @{ Failed = $true; Message = "Found $($lockFiles.Count) Git lock file(s)" }
        }
        return @{ Failed = $false }
    } -Level "ERROR"
    
    # ==============================================================
    # CHECK 5: Disk space
    # ==============================================================
    Test-DriftCondition -Name "Disk space" -Condition {
        $drive = Get-PSDrive -Name C
        $freeGB = [math]::Round($drive.Free / 1GB, 2)
        if ($freeGB -lt 20) {
            return @{ Failed = $true; Message = "Only $freeGB GB free (should have > 20 GB)" }
        }
        return @{ Failed = $false }
    } -Level "ERROR"
    
    # ==============================================================
    # CHECK 6: VS Code workspace settings integrity
    # ==============================================================
    Test-DriftCondition -Name "VS Code settings" -Condition {
        $settingsPath = "$Root\.vscode\settings.json"
        if (-not (Test-Path $settingsPath)) {
            return @{ Failed = $true; Message = "Workspace settings.json missing" }
        }
        
        try {
            $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
            if (-not $settings.'files.watcherExclude') {
                return @{ Failed = $true; Message = "File watcher exclusions not configured" }
            }
        } catch {
            return @{ Failed = $true; Message = "settings.json is corrupted (invalid JSON)" }
        }
        
        return @{ Failed = $false }
    }
    
    # ==============================================================
    # CHECK 7: Python environment integrity
    # ==============================================================
    Test-DriftCondition -Name "Python venv integrity" -Condition {
        $venvPython = "$Root\.venv\Scripts\python.exe"
        if (-not (Test-Path $venvPython)) {
            return @{ Failed = $true; Message = "Python venv not found or corrupted" }
        }
        
        $testResult = & $venvPython --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            return @{ Failed = $true; Message = "Python interpreter failed to execute" }
        }
        
        return @{ Failed = $false }
    }
    
    # ==============================================================
    # CHECK 8: Backup staleness
    # ==============================================================
    Test-DriftCondition -Name "Backup age" -Condition {
        $backupRoot = "C:\EQ12\backups"
        if (Test-Path $backupRoot) {
            $latestBackup = Get-ChildItem -Path $backupRoot -Directory -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($latestBackup) {
                $age = (Get-Date) - $latestBackup.LastWriteTime
                if ($age.TotalDays -gt 7) {
                    return @{ Failed = $true; Message = "Latest backup is $([math]::Round($age.TotalDays, 1)) days old (should backup weekly)" }
                }
            } else {
                return @{ Failed = $true; Message = "No backups found in $backupRoot" }
            }
        } else {
            return @{ Failed = $true; Message = "Backup directory does not exist" }
        }
        return @{ Failed = $false }
    }
    
    # ==============================================================
    # SUMMARY
    # ==============================================================
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host " DRIFT MONITOR SUMMARY" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    
    if ($Errors.Count -eq 0 -and $Warnings.Count -eq 0) {
        Write-Host "STATUS: HEALTHY" -ForegroundColor Green
        Write-Host "No drift or corruption detected." -ForegroundColor Green
    } else {
        if ($Errors.Count -gt 0) {
            Write-Host "STATUS: CRITICAL" -ForegroundColor Red
            Write-Host "Errors: $($Errors.Count)" -ForegroundColor Red
            foreach ($error in $Errors) {
                Write-Host "  - $error" -ForegroundColor Red
            }
        }
        
        if ($Warnings.Count -gt 0) {
            Write-Host "Warnings: $($Warnings.Count)" -ForegroundColor Yellow
            foreach ($warning in $Warnings) {
                Write-Host "  - $warning" -ForegroundColor Yellow
            }
        }
    }
    
    Write-Host ""
    
    # Export report if requested
    if ($ExportReport) {
        $reportPath = "$Root\logs\drift_monitor_$Timestamp.json"
        $reportDir = Split-Path -Path $reportPath -Parent
        if (-not (Test-Path $reportDir)) {
            New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
        }
        
        $report = @{
            Timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
            ErrorCount = $Errors.Count
            WarningCount = $Warnings.Count
            Errors = $Errors
            Warnings = $Warnings
            Status = if ($Errors.Count -gt 0) { "CRITICAL" } elseif ($Warnings.Count -gt 0) { "WARNING" } else { "HEALTHY" }
        }
        
        $report | ConvertTo-Json -Depth 5 | Set-Content -Path $reportPath -Encoding UTF8
        Write-Host "Report exported to: $reportPath" -ForegroundColor Cyan
        Write-Host ""
    }
    
    # Sleep if in continuous mode
    if ($Continuous) {
        Write-Host "Next check in $IntervalMinutes minutes... (Ctrl+C to stop)" -ForegroundColor DarkGray
        Write-Host ""
        Start-Sleep -Seconds ($IntervalMinutes * 60)
    }
    
} while ($Continuous)

Write-Host "Drift monitoring complete." -ForegroundColor Green
Write-Host ""
