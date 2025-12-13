# =====================================================================
# EQ12 ENVIRONMENT MONITOR
# =====================================================================
# Continuously monitors your EQ12 development environment for stability issues
# and warns you before problems escalate into crashes or corruption.
#
# What it monitors:
#   1. VS Code extension health (Copilot, Pylance, Python)
#   2. Python interpreter status
#   3. File watcher resource usage
#   4. Git repository health
#   5. WSL remote server status
#   6. Memory usage of VS Code processes
#   7. Dependency conflicts
#
# Usage:
#   # Run once for immediate health check:
#   .\EQ12_ENVIRONMENT_MONITOR.ps1
#
#   # Run continuously with monitoring interval:
#   .\EQ12_ENVIRONMENT_MONITOR.ps1 -Continuous -IntervalSeconds 300
#
#   # Export health report to JSON:
#   .\EQ12_ENVIRONMENT_MONITOR.ps1 -ExportReport
#
# =====================================================================

[CmdletBinding()]
param(
    [switch]$Continuous,
    [int]$IntervalSeconds = 300,
    [switch]$ExportReport,
    [string]$ReportPath = "C:\EQ12\logs\environment_health_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
)

$ErrorActionPreference = "Continue"

function Write-ColoredStatus {
    param(
        [string]$Message,
        [string]$Status  # "OK", "WARNING", "ERROR", "INFO"
    )
    
    $color = switch ($Status) {
        "OK"      { "Green" }
        "WARNING" { "Yellow" }
        "ERROR"   { "Red" }
        "INFO"    { "Cyan" }
        default   { "White" }
    }
    
    $symbol = switch ($Status) {
        "OK"      { "✔" }
        "WARNING" { "⚠️" }
        "ERROR"   { "❌" }
        "INFO"    { "ℹ️" }
        default   { "•" }
    }
    
    Write-Host "$symbol $Message" -ForegroundColor $color
}

function Test-EnvironmentHealth {
    $healthReport = @{
        Timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        Checks = @{}
        OverallStatus = "OK"
        Issues = @()
        Warnings = @()
    }
    
    Write-Host "`n=== EQ12 ENVIRONMENT HEALTH CHECK ===" -ForegroundColor Cyan
    Write-Host "Timestamp: $((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor DarkGray
    Write-Host ""
    
    # ----------------------------------------------------------------
    # CHECK 1: VS Code Process Health
    # ----------------------------------------------------------------
    Write-Host "[1/8] VS Code Process Health..." -ForegroundColor Yellow
    
    $vscodeProcesses = Get-Process -Name "Code" -ErrorAction SilentlyContinue
    if ($vscodeProcesses) {
        $totalMemoryMB = ($vscodeProcesses | Measure-Object -Property WorkingSet64 -Sum).Sum / 1MB
        $processCount = $vscodeProcesses.Count
        
        $healthReport.Checks.VSCodeProcess = @{
            Running = $true
            ProcessCount = $processCount
            TotalMemoryMB = [math]::Round($totalMemoryMB, 2)
        }
        
        if ($totalMemoryMB -gt 4096) {
            Write-ColoredStatus "VS Code memory usage HIGH: $([math]::Round($totalMemoryMB, 0)) MB" "WARNING"
            $healthReport.Warnings += "VS Code using excessive memory"
        } elseif ($totalMemoryMB -gt 8192) {
            Write-ColoredStatus "VS Code memory usage CRITICAL: $([math]::Round($totalMemoryMB, 0)) MB" "ERROR"
            $healthReport.Issues += "VS Code memory exhaustion risk"
            $healthReport.OverallStatus = "WARNING"
        } else {
            Write-ColoredStatus "VS Code memory usage OK: $([math]::Round($totalMemoryMB, 0)) MB" "OK"
        }
    } else {
        Write-ColoredStatus "VS Code not running" "INFO"
        $healthReport.Checks.VSCodeProcess = @{ Running = $false }
    }
    
    Write-Host ""
    
    # ----------------------------------------------------------------
    # CHECK 2: Extension Health
    # ----------------------------------------------------------------
    Write-Host "[2/8] Extension Health..." -ForegroundColor Yellow
    
    $extensionsPath = "$env:USERPROFILE\.vscode\extensions"
    $requiredExtensions = @{
        "ms-python.python" = "Python"
        "ms-python.vscode-pylance" = "Pylance"
        "github.copilot" = "GitHub Copilot"
        "github.copilot-chat" = "GitHub Copilot Chat"
    }
    
    $healthReport.Checks.Extensions = @{}
    $missingExtensions = @()
    
    if (Test-Path $extensionsPath) {
        $installedExtensions = Get-ChildItem -Path $extensionsPath -Directory
        
        foreach ($extId in $requiredExtensions.Keys) {
            $extName = $requiredExtensions[$extId]
            $found = $installedExtensions | Where-Object { $_.Name -like "$extId*" }
            
            if ($found) {
                $healthReport.Checks.Extensions[$extId] = @{
                    Installed = $true
                    Version = $found.Name -replace "^$extId-", ""
                }
                Write-ColoredStatus "$extName installed" "OK"
            } else {
                $healthReport.Checks.Extensions[$extId] = @{ Installed = $false }
                $missingExtensions += $extName
                Write-ColoredStatus "$extName NOT installed" "ERROR"
            }
        }
        
        # Check for corrupted tikTokenizerWorker.js
        $copilotChatDirs = $installedExtensions | Where-Object { $_.Name -like "github.copilot-chat*" }
        foreach ($dir in $copilotChatDirs) {
            $tikWorker = Get-ChildItem -Path $dir.FullName -Recurse -Filter "tikTokenizerWorker.js" -ErrorAction SilentlyContinue
            if ($tikWorker -and $tikWorker.Length -lt 1024) {
                Write-ColoredStatus "Corrupted tikTokenizerWorker.js in $($dir.Name)" "ERROR"
                $healthReport.Issues += "Copilot Chat corruption detected"
                $healthReport.OverallStatus = "ERROR"
            }
        }
    }
    
    if ($missingExtensions.Count -gt 0) {
        $healthReport.Issues += "Missing extensions: $($missingExtensions -join ', ')"
        $healthReport.OverallStatus = "ERROR"
    }
    
    Write-Host ""
    
    # ----------------------------------------------------------------
    # CHECK 3: Python Environment
    # ----------------------------------------------------------------
    Write-Host "[3/8] Python Environment..." -ForegroundColor Yellow
    
    $venvPython = "C:\EQ12\.venv\Scripts\python.exe"
    $healthReport.Checks.Python = @{}
    
    if (Test-Path $venvPython) {
        $pythonVersion = & $venvPython --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $healthReport.Checks.Python.VenvExists = $true
            $healthReport.Checks.Python.Version = $pythonVersion
            Write-ColoredStatus "Python venv working: $pythonVersion" "OK"
            
            # Check for dependency conflicts
            $pipCheck = & $venvPython -m pip check 2>&1
            if ($LASTEXITCODE -eq 0) {
                $healthReport.Checks.Python.DependenciesOK = $true
                Write-ColoredStatus "No dependency conflicts" "OK"
            } else {
                $healthReport.Checks.Python.DependenciesOK = $false
                $healthReport.Checks.Python.ConflictDetails = $pipCheck
                Write-ColoredStatus "Dependency conflicts detected" "WARNING"
                $healthReport.Warnings += "Python dependency conflicts"
            }
        } else {
            Write-ColoredStatus "Python venv exists but failed to execute" "ERROR"
            $healthReport.Issues += "Python venv corruption"
            $healthReport.OverallStatus = "ERROR"
        }
    } else {
        Write-ColoredStatus "Python venv not found" "ERROR"
        $healthReport.Issues += "Missing Python venv"
        $healthReport.OverallStatus = "ERROR"
    }
    
    Write-Host ""
    
    # ----------------------------------------------------------------
    # CHECK 4: Git Repository Health
    # ----------------------------------------------------------------
    Write-Host "[4/8] Git Repository Health..." -ForegroundColor Yellow
    
    $healthReport.Checks.Git = @{}
    
    if (Test-Path "C:\EQ12\.git") {
        # Check for lock files
        $lockFiles = Get-ChildItem -Path "C:\EQ12\.git" -Recurse -Filter "*.lock" -ErrorAction SilentlyContinue
        if ($lockFiles) {
            $healthReport.Checks.Git.LockFiles = $lockFiles.Count
            Write-ColoredStatus "Git lock files found: $($lockFiles.Count)" "WARNING"
            $healthReport.Warnings += "Git lock files present"
        } else {
            $healthReport.Checks.Git.LockFiles = 0
            Write-ColoredStatus "No Git lock files" "OK"
        }
        
        # Check Git status
        Set-Location "C:\EQ12" -ErrorAction SilentlyContinue
        $gitStatus = & git status --porcelain 2>&1
        if ($LASTEXITCODE -eq 0) {
            $changedFiles = ($gitStatus | Measure-Object).Count
            $healthReport.Checks.Git.ChangedFiles = $changedFiles
            Write-ColoredStatus "Git repository healthy ($changedFiles changed files)" "OK"
        } else {
            Write-ColoredStatus "Git status check failed" "WARNING"
            $healthReport.Warnings += "Git status errors"
        }
    } else {
        Write-ColoredStatus "Git repository not found" "ERROR"
        $healthReport.Issues += "Missing Git repository"
        $healthReport.OverallStatus = "ERROR"
    }
    
    Write-Host ""
    
    # ----------------------------------------------------------------
    # CHECK 5: File Watcher Configuration
    # ----------------------------------------------------------------
    Write-Host "[5/8] File Watcher Configuration..." -ForegroundColor Yellow
    
    $settingsPath = "C:\EQ12\.vscode\settings.json"
    $healthReport.Checks.FileWatchers = @{}
    
    if (Test-Path $settingsPath) {
        try {
            $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
            
            if ($settings.'files.watcherExclude') {
                $exclusionCount = ($settings.'files.watcherExclude' | Get-Member -MemberType NoteProperty).Count
                $healthReport.Checks.FileWatchers.ExclusionPatterns = $exclusionCount
                
                # Check for critical exclusions
                $criticalExclusions = @("**/.git/objects/**", "**/node_modules/**", "**/.venv/**")
                $missingCritical = @()
                foreach ($pattern in $criticalExclusions) {
                    if (-not $settings.'files.watcherExclude'.$pattern) {
                        $missingCritical += $pattern
                    }
                }
                
                if ($missingCritical.Count -eq 0) {
                    Write-ColoredStatus "File watcher exclusions configured ($exclusionCount patterns)" "OK"
                } else {
                    Write-ColoredStatus "Missing critical file watcher exclusions" "WARNING"
                    $healthReport.Warnings += "Incomplete file watcher exclusions"
                }
            } else {
                Write-ColoredStatus "No file watcher exclusions configured" "WARNING"
                $healthReport.Warnings += "File watcher exhaustion risk"
            }
        } catch {
            Write-ColoredStatus "Failed to parse settings.json" "ERROR"
            $healthReport.Issues += "Corrupted settings.json"
            $healthReport.OverallStatus = "ERROR"
        }
    } else {
        Write-ColoredStatus "Workspace settings.json not found" "WARNING"
        $healthReport.Warnings += "Missing workspace settings"
    }
    
    Write-Host ""
    
    # ----------------------------------------------------------------
    # CHECK 6: WSL Health
    # ----------------------------------------------------------------
    Write-Host "[6/8] WSL Health..." -ForegroundColor Yellow
    
    $healthReport.Checks.WSL = @{}
    $wslCmd = Get-Command wsl -ErrorAction SilentlyContinue
    
    if ($wslCmd) {
        $wslStatus = & wsl --status 2>&1
        if ($LASTEXITCODE -eq 0) {
            $healthReport.Checks.WSL.Available = $true
            $healthReport.Checks.WSL.Status = "Running"
            Write-ColoredStatus "WSL responding normally" "OK"
        } else {
            $healthReport.Checks.WSL.Available = $true
            $healthReport.Checks.WSL.Status = "Error"
            Write-ColoredStatus "WSL returned error" "WARNING"
            $healthReport.Warnings += "WSL status errors"
        }
    } else {
        $healthReport.Checks.WSL.Available = $false
        Write-ColoredStatus "WSL not installed (optional)" "INFO"
    }
    
    Write-Host ""
    
    # ----------------------------------------------------------------
    # CHECK 7: Disk Space
    # ----------------------------------------------------------------
    Write-Host "[7/8] Disk Space..." -ForegroundColor Yellow
    
    $drive = Get-PSDrive -Name C
    $freeSpaceGB = [math]::Round($drive.Free / 1GB, 2)
    $totalSpaceGB = [math]::Round(($drive.Free + $drive.Used) / 1GB, 2)
    $freePercent = [math]::Round(($drive.Free / ($drive.Free + $drive.Used)) * 100, 1)
    
    $healthReport.Checks.DiskSpace = @{
        FreeGB = $freeSpaceGB
        TotalGB = $totalSpaceGB
        FreePercent = $freePercent
    }
    
    if ($freeSpaceGB -lt 10) {
        Write-ColoredStatus "Disk space CRITICAL: $freeSpaceGB GB free ($freePercent%)" "ERROR"
        $healthReport.Issues += "Low disk space"
        $healthReport.OverallStatus = "ERROR"
    } elseif ($freeSpaceGB -lt 50) {
        Write-ColoredStatus "Disk space LOW: $freeSpaceGB GB free ($freePercent%)" "WARNING"
        $healthReport.Warnings += "Low disk space"
    } else {
        Write-ColoredStatus "Disk space OK: $freeSpaceGB GB free ($freePercent%)" "OK"
    }
    
    Write-Host ""
    
    # ----------------------------------------------------------------
    # CHECK 8: Recent Errors in Logs
    # ----------------------------------------------------------------
    Write-Host "[8/8] Recent Error Patterns..." -ForegroundColor Yellow
    
    $logsPath = "C:\EQ12\logs"
    $healthReport.Checks.RecentErrors = @{}
    
    if (Test-Path $logsPath) {
        $recentLogs = Get-ChildItem -Path $logsPath -Filter "*.log" -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-24) } |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 5
        
        if ($recentLogs) {
            $errorCount = 0
            foreach ($log in $recentLogs) {
                $errors = Select-String -Path $log.FullName -Pattern "ERROR|CRITICAL|FATAL" -ErrorAction SilentlyContinue
                $errorCount += $errors.Count
            }
            
            $healthReport.Checks.RecentErrors.Count = $errorCount
            
            if ($errorCount -gt 10) {
                Write-ColoredStatus "Recent error patterns detected: $errorCount errors in last 24h" "WARNING"
                $healthReport.Warnings += "High error rate in logs"
            } elseif ($errorCount -gt 0) {
                Write-ColoredStatus "Minor errors in logs: $errorCount errors in last 24h" "INFO"
            } else {
                Write-ColoredStatus "No recent errors in logs" "OK"
            }
        } else {
            Write-ColoredStatus "No recent log files" "INFO"
        }
    } else {
        Write-ColoredStatus "Logs directory not found" "INFO"
    }
    
    Write-Host ""
    
    # ----------------------------------------------------------------
    # SUMMARY
    # ----------------------------------------------------------------
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host " HEALTH CHECK SUMMARY" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    
    $statusColor = switch ($healthReport.OverallStatus) {
        "OK"      { "Green" }
        "WARNING" { "Yellow" }
        "ERROR"   { "Red" }
    }
    
    Write-Host "Overall Status: $($healthReport.OverallStatus)" -ForegroundColor $statusColor
    Write-Host "Issues: $($healthReport.Issues.Count)" -ForegroundColor $(if ($healthReport.Issues.Count -gt 0) { "Red" } else { "Green" })
    Write-Host "Warnings: $($healthReport.Warnings.Count)" -ForegroundColor $(if ($healthReport.Warnings.Count -gt 0) { "Yellow" } else { "Green" })
    Write-Host ""
    
    if ($healthReport.Issues.Count -gt 0) {
        Write-Host "Critical Issues:" -ForegroundColor Red
        foreach ($issue in $healthReport.Issues) {
            Write-Host "  • $issue" -ForegroundColor Red
        }
        Write-Host ""
    }
    
    if ($healthReport.Warnings.Count -gt 0) {
        Write-Host "Warnings:" -ForegroundColor Yellow
        foreach ($warning in $healthReport.Warnings) {
            Write-Host "  • $warning" -ForegroundColor Yellow
        }
        Write-Host ""
    }
    
    return $healthReport
}

# ----------------------------------------------------------------
# MAIN EXECUTION
# ----------------------------------------------------------------

do {
    $report = Test-EnvironmentHealth
    
    if ($ExportReport) {
        $reportDir = Split-Path -Path $ReportPath -Parent
        if (-not (Test-Path $reportDir)) {
            New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
        }
        
        $report | ConvertTo-Json -Depth 10 | Set-Content -Path $ReportPath -Encoding UTF8
        Write-Host "✔ Health report exported to: $ReportPath" -ForegroundColor Green
        Write-Host ""
    }
    
    if ($Continuous) {
        Write-Host "Next check in $IntervalSeconds seconds... (Ctrl+C to stop)" -ForegroundColor DarkGray
        Start-Sleep -Seconds $IntervalSeconds
    }
    
} while ($Continuous)
