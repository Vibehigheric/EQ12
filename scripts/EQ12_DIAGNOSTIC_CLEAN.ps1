<#
.SYNOPSIS
    EQ12 System Diagnostic and Cleanup Tool - Clean ASCII Version

.DESCRIPTION
    Comprehensive diagnostic tool for the EQ12 system runaway repair loop issue.
    Analyzes universal_repair logs, identifies root causes, and provides cleanup.
    
    ASCII-ONLY VERSION - No Unicode, no emojis, no corruption.

.PARAMETER Action
    scan     - Analyze the problem without making changes
    cleanup  - Archive old logs and clean up
    kill     - Stop any running repair processes
    full     - Complete diagnostic + cleanup + prevention

.PARAMETER KeepRecentLogs
    Number of recent logs to keep (default: 50)

.PARAMETER Force
    Skip confirmation prompts

.EXAMPLE
    .\EQ12_DIAGNOSTIC_CLEAN.ps1 -Action scan
    .\EQ12_DIAGNOSTIC_CLEAN.ps1 -Action full -Force

.NOTES
    Author: EQ12 Copilot Workspace Architect
    Date: 2025-11-27
    Purpose: Fix runaway repair loop that created 8K+ log files
    Encoding: ASCII-ONLY (UTF-8 without BOM)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("scan", "cleanup", "kill", "full")]
    [string]$Action = "scan",

    [Parameter(Mandatory = $false)]
    [int]$KeepRecentLogs = 50,

    [Parameter(Mandatory = $false)]
    [switch]$Force
)

# ==================== CONFIGURATION ====================
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSDefaultParameterValues['Out-File:Encoding'] = 'ASCII'

$script:RepoRoot = "C:\EQ12_BROKEN_20251122_210342"
$script:LogsDir = Join-Path $RepoRoot "logs"
$script:ReportsDir = Join-Path $RepoRoot "reports"
$script:ArchiveDir = Join-Path $LogsDir "archive"

$script:DiagnosticReport = @{
    Timestamp          = (Get-Date).ToUniversalTime().ToString("o")
    TotalRepairLogs    = 0
    OldestLog          = $null
    NewestLog          = $null
    TotalSizeGB        = 0
    RunningProcesses   = @()
    ScheduledTasks     = @()
    SuspiciousScripts  = @()
    RootCauseAnalysis  = @()
    RecommendedActions = @()
}

# ==================== LOGGING ====================
function Write-DiagLog {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )

    $colors = @{
        INFO    = "Cyan"
        WARN    = "Yellow"
        ERROR   = "Red"
        SUCCESS = "Green"
    }

    $timestamp = Get-Date -Format "HH:mm:ss"
    $line = "[{0}] [{1}] {2}" -f $timestamp, $Level, $Message
    Write-Host $line -ForegroundColor $colors[$Level]
}

# ==================== DIAGNOSTIC FUNCTIONS ====================
function Get-RepairLogStats {
    Write-DiagLog "Analyzing universal_repair logs..." "INFO"

    $repairLogs = Get-ChildItem -Path $script:LogsDir -Filter "universal_repair_*.log" -ErrorAction SilentlyContinue

    if (-not $repairLogs) {
        Write-DiagLog "No universal_repair logs found" "WARN"
        return $null
    }

    $script:DiagnosticReport.TotalRepairLogs = $repairLogs.Count
    $script:DiagnosticReport.OldestLog = ($repairLogs | Sort-Object LastWriteTime | Select-Object -First 1).LastWriteTime
    $script:DiagnosticReport.NewestLog = ($repairLogs | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
    $script:DiagnosticReport.TotalSizeGB = [math]::Round(($repairLogs | Measure-Object -Property Length -Sum).Sum / 1GB, 3)

    $timespan = $script:DiagnosticReport.NewestLog - $script:DiagnosticReport.OldestLog
    $avgLogsPerHour = if ($timespan.TotalHours -gt 0) {
        [math]::Round($script:DiagnosticReport.TotalRepairLogs / $timespan.TotalHours, 2)
    }
    else { 0 }

    Write-DiagLog "Found $($script:DiagnosticReport.TotalRepairLogs) repair logs" "WARN"
    Write-DiagLog "Date range: $($script:DiagnosticReport.OldestLog) to $($script:DiagnosticReport.NewestLog)" "INFO"
    Write-DiagLog "Total size: $($script:DiagnosticReport.TotalSizeGB) GB" "INFO"
    Write-DiagLog "Average rate: $avgLogsPerHour logs/hour" "WARN"

    # Sample recent logs to check for patterns
    $recentLogs = $repairLogs | Sort-Object LastWriteTime -Descending | Select-Object -First 10
    $emptySamples = ($recentLogs | Where-Object { $_.Length -lt 100 }).Count

    if ($emptySamples -gt 5) {
        $script:DiagnosticReport.RootCauseAnalysis += "FINDING: $emptySamples/10 recent logs are near-empty (<100 bytes) - Script initializing but not executing"
    }

    return $repairLogs
}

function Get-RunningRepairProcesses {
    Write-DiagLog "Checking for running repair processes..." "INFO"

    $processes = Get-Process | Where-Object {
        $_.Name -like "*python*" -or
        $_.ProcessName -like "*eq12*" -or
        $_.ProcessName -like "*repair*"
    }

    foreach ($proc in $processes) {
        $runtime = (Get-Date) - $proc.StartTime
        $procInfo = @{
            Name      = $proc.Name
            PID       = $proc.Id
            Runtime   = $runtime.ToString("hh\:mm\:ss")
            MemoryMB  = [math]::Round($proc.WS / 1MB, 2)
            CPUTime   = $proc.CPU
            StartTime = $proc.StartTime
        }

        $script:DiagnosticReport.RunningProcesses += $procInfo

        if ($runtime.TotalMinutes -gt 5) {
            Write-DiagLog "SUSPICIOUS: Process $($proc.Name) (PID $($proc.Id)) running for $($runtime.TotalMinutes.ToString('F1')) minutes" "WARN"
            $script:DiagnosticReport.RootCauseAnalysis += "FINDING: Process $($proc.Name) hung for $($runtime.TotalMinutes.ToString('F1')) minutes - likely I/O deadlock"
        }
    }

    return $processes
}

function Get-SuspiciousScheduledTasks {
    Write-DiagLog "Checking scheduled tasks..." "INFO"

    $allTasks = Get-ScheduledTask | Where-Object {
        $_.TaskName -like "*EQ12*" -or
        $_.TaskName -like "*repair*" -or
        $_.TaskName -like "*universal*"
    }

    foreach ($task in $allTasks) {
        $info = Get-ScheduledTaskInfo $task
        $taskDetail = @{
            Name     = $task.TaskName
            State    = $task.State
            LastRun  = $info.LastRunTime
            NextRun  = $info.NextRunTime
            Result   = $info.LastTaskResult
            Triggers = ($task.Triggers | Measure-Object).Count
        }

        $script:DiagnosticReport.ScheduledTasks += $taskDetail

        # Check for frequent triggers
        foreach ($trigger in $task.Triggers) {
            try {
                if ($trigger.Repetition -and $trigger.Repetition.Interval) {
                    $interval = [System.Xml.XmlConvert]::ToTimeSpan($trigger.Repetition.Interval)
                    if ($interval.TotalMinutes -lt 5) {
                        Write-DiagLog "SUSPICIOUS: Task '$($task.TaskName)' repeats every $($interval.TotalMinutes) minutes" "WARN"
                        $script:DiagnosticReport.RootCauseAnalysis += "FINDING: Scheduled task '$($task.TaskName)' has sub-5-minute trigger interval"
                    }
                }
            }
            catch {
                # Interval format invalid or property doesn't exist, skip
            }
        }
    }

    return $allTasks
}

function Get-InfiniteLoopScripts {
    Write-DiagLog "Scanning for infinite loop patterns in scripts..." "INFO"

    $scriptPatterns = @(
        "*.ps1",
        "*.py",
        "*.bat"
    )

    $suspiciousFiles = @()

    foreach ($pattern in $scriptPatterns) {
        $files = Get-ChildItem -Path $script:RepoRoot -Filter $pattern -Recurse -ErrorAction SilentlyContinue | Where-Object {
            $_.FullName -notlike "*\node_modules\*" -and
            $_.FullName -notlike "*\venv\*" -and
            $_.FullName -notlike "*\.venv\*"
        }

        foreach ($file in $files) {
            $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue

            $infinitePatterns = @(
                'while\s*\(\s*\$true\s*\)',
                'while\s*\(\s*True\s*\)',
                'while\s*true\s*;',
                'for\s*\(\s*;\s*;\s*\)',
                'while\s*\(\s*1\s*\)'
            )

            foreach ($pattern in $infinitePatterns) {
                if ($content -match $pattern) {
                    $suspiciousFiles += @{
                        File    = $file.FullName
                        Pattern = $pattern
                        Type    = $file.Extension
                    }

                    Write-DiagLog "Found infinite loop pattern in: $($file.Name)" "WARN"
                    break
                }
            }
        }
    }

    $script:DiagnosticReport.SuspiciousScripts = $suspiciousFiles
    return $suspiciousFiles
}

function Stop-RepairProcesses {
    param([array]$Processes)

    Write-DiagLog "Stopping repair processes..." "WARN"

    foreach ($proc in $Processes) {
        try {
            Stop-Process -Id $proc.Id -Force -ErrorAction Stop
            Write-DiagLog "[OK] Killed process $($proc.Name) (PID $($proc.Id))" "SUCCESS"
        }
        catch {
            Write-DiagLog "Failed to kill PID $($proc.Id): $_" "ERROR"
        }
    }
}

function Invoke-LogCleanup {
    param(
        [Parameter(Mandatory = $true)]
        [array]$RepairLogs,

        [Parameter(Mandatory = $false)]
        [int]$KeepRecent = 50
    )

    Write-DiagLog "Starting log cleanup (keeping $KeepRecent most recent)..." "INFO"

    # Create archive directory
    if (-not (Test-Path $script:ArchiveDir)) {
        New-Item -Path $script:ArchiveDir -ItemType Directory -Force | Out-Null
    }

    # Sort logs by date (oldest first)
    $sortedLogs = $RepairLogs | Sort-Object LastWriteTime

    # Keep the most recent N logs
    $logsToArchive = $sortedLogs | Select-Object -First ($sortedLogs.Count - $KeepRecent)

    if ($logsToArchive.Count -eq 0) {
        Write-DiagLog "No logs to archive" "INFO"
        return
    }

    Write-DiagLog "Archiving $($logsToArchive.Count) old logs..." "INFO"

    $archiveZip = Join-Path $script:ArchiveDir "universal_repair_archive_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"

    try {
        Compress-Archive -Path $logsToArchive.FullName -DestinationPath $archiveZip -CompressionLevel Optimal
        $logsToArchive | Remove-Item -Force

        Write-DiagLog "[OK] Archived $($logsToArchive.Count) logs to: $archiveZip" "SUCCESS"

        $totalSizeMB = [math]::Round(($logsToArchive | Measure-Object -Property Length -Sum).Sum / 1MB, 2)
        Write-DiagLog "Freed up approximately $totalSizeMB MB" "SUCCESS"
    }
    catch {
        Write-DiagLog "Failed to archive logs: $_" "ERROR"
    }
}

function New-PreventionMechanisms {
    Write-DiagLog "Creating prevention mechanisms..." "INFO"

    $cooldownFile = Join-Path $script:LogsDir "repair_cooldown.json"
    $cooldownConfig = @{
        LastRun                = (Get-Date).ToUniversalTime().ToString("o")
        MinimumIntervalMinutes = 60
        Note                   = "EQ12 repair scripts should check this file and enforce minimum 1-hour cooldown"
    } | ConvertTo-Json

    $cooldownConfig | Set-Content $cooldownFile -Force -Encoding ASCII

    Write-DiagLog "Created cooldown tracker: $cooldownFile" "SUCCESS"
    $script:DiagnosticReport.RecommendedActions += "Added cooldown mechanism to prevent rapid re-execution"
}

function Export-DiagnosticReport {
    Write-DiagLog "Generating diagnostic report..." "INFO"

    if (-not (Test-Path $script:ReportsDir)) {
        New-Item -Path $script:ReportsDir -ItemType Directory -Force | Out-Null
    }

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $jsonReport = Join-Path $script:ReportsDir "runaway_repair_diagnostic_$timestamp.json"
    $mdReport = Join-Path $script:ReportsDir "runaway_repair_diagnostic_$timestamp.md"

    # Export JSON
    $script:DiagnosticReport | ConvertTo-Json -Depth 10 | Set-Content $jsonReport -Force -Encoding ASCII

    # Generate simple Markdown report
    $mdContent = @"
# EQ12 Runaway Repair Loop Diagnostic Report

Generated: $($script:DiagnosticReport.Timestamp)

## Summary

- Total Logs: $($script:DiagnosticReport.TotalRepairLogs)
- Total Size: $($script:DiagnosticReport.TotalSizeGB) GB
- Date Range: $($script:DiagnosticReport.OldestLog) to $($script:DiagnosticReport.NewestLog)
- Running Processes: $($script:DiagnosticReport.RunningProcesses.Count)
- Scheduled Tasks: $($script:DiagnosticReport.ScheduledTasks.Count)
- Suspicious Scripts: $($script:DiagnosticReport.SuspiciousScripts.Count)

## Root Cause Analysis

$($script:DiagnosticReport.RootCauseAnalysis -join "`n")

## Recommended Actions

$($script:DiagnosticReport.RecommendedActions -join "`n")

## Report Files

- JSON: $jsonReport
- Markdown: $mdReport
"@

    $mdContent | Set-Content $mdReport -Force -Encoding ASCII

    Write-DiagLog "[OK] Diagnostic reports generated" "SUCCESS"
    Write-DiagLog "   JSON: $jsonReport" "INFO"
    Write-DiagLog "   Markdown: $mdReport" "INFO"
}

# ==================== MAIN EXECUTION ====================
function Invoke-MainDiagnostic {
    Write-DiagLog "EQ12 Runaway Repair Loop Diagnostic Tool" "INFO"
    Write-DiagLog "Action: $Action" "INFO"
    Write-DiagLog "" "INFO"

    # Step 1: Analyze repair logs
    $repairLogs = Get-RepairLogStats

    # Step 2: Check running processes
    $runningProcs = Get-RunningRepairProcesses

    # Step 3: Check scheduled tasks
    $scheduledTasks = Get-SuspiciousScheduledTasks

    # Step 4: Scan for infinite loop scripts
    $suspiciousScripts = Get-InfiniteLoopScripts

    # Execute action-specific operations
    switch ($Action) {
        "scan" {
            Write-DiagLog "Scan complete - no changes made" "INFO"
        }

        "kill" {
            if ($runningProcs.Count -gt 0) {
                if ($Force -or (Read-Host "Kill $($runningProcs.Count) processes? (y/n)") -eq 'y') {
                    Stop-RepairProcesses -Processes $runningProcs
                    $script:DiagnosticReport.RecommendedActions += "Killed $($runningProcs.Count) hung processes"
                }
            }
            else {
                Write-DiagLog "No processes to kill" "INFO"
            }
        }

        "cleanup" {
            if ($repairLogs -and $repairLogs.Count -gt $KeepRecentLogs) {
                if ($Force -or (Read-Host "Archive $($repairLogs.Count - $KeepRecentLogs) logs? (y/n)") -eq 'y') {
                    Invoke-LogCleanup -RepairLogs $repairLogs -KeepRecent $KeepRecentLogs
                    $script:DiagnosticReport.RecommendedActions += "Archived old logs, kept $KeepRecentLogs most recent"
                }
            }
            else {
                Write-DiagLog "No cleanup needed" "INFO"
            }
        }

        "full" {
            if ($runningProcs.Count -gt 0) {
                if ($Force -or (Read-Host "Kill $($runningProcs.Count) processes? (y/n)") -eq 'y') {
                    Stop-RepairProcesses -Processes $runningProcs
                }
            }

            if ($repairLogs -and $repairLogs.Count -gt $KeepRecentLogs) {
                if ($Force -or (Read-Host "Archive $($repairLogs.Count - $KeepRecentLogs) logs? (y/n)") -eq 'y') {
                    Invoke-LogCleanup -RepairLogs $repairLogs -KeepRecent $KeepRecentLogs
                }
            }

            New-PreventionMechanisms
        }
    }

    # Always generate report
    Export-DiagnosticReport

    Write-DiagLog "" "INFO"
    Write-DiagLog "[OK] Diagnostic complete" "SUCCESS"
}

# Run main diagnostic
Invoke-MainDiagnostic
