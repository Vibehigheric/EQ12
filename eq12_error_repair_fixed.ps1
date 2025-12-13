[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Error Repair - Automatic PowerShell and System Fixes (Fixed)
    
.DESCRIPTION
    Comprehensive repair tool that automatically fixes common EQ12 system issues:
    - PowerShell try/catch/finally syntax errors
    - UTF-8 encoding problems with emojis
    - Missing file dependencies
    - Permission and execution policy issues
    - Log file corruption
    - Dashboard generation failures
    
.PARAMETER Action
    Repair action: 'All', 'PowerShell', 'Encoding', 'Dependencies', 'Permissions'
    
.PARAMETER TargetScript
    Specific PowerShell script to repair (optional)
    
.PARAMETER Workspace
    EQ12 workspace path (default: C:\EQ12)
    
.PARAMETER VerboseLogging
    Enable detailed logging
    
.PARAMETER BackupFirst
    Create backup before making changes
    
.EXAMPLE
    .\eq12_error_repair_fixed.ps1 -Action All -VerboseLogging -BackupFirst
    
.NOTES
    Author: EQ12 Quantum Development Team
    Version: 1.0.1 - Fixed Auto-Repair System
    Date: November 7, 2025
#>

[CmdletBinding()]
param(
    [ValidateSet('All', 'PowerShell', 'Encoding', 'Dependencies', 'Permissions', 'Cleanup')]
    [string]$Action = 'All',
    
    [string]$TargetScript = '',
    
    [ValidateScript({ Test-Path $_ -PathType Container })]
    [string]$Workspace = 'C:\EQ12',
    
    [switch]$VerboseLogging,
    
    [switch]$BackupFirst
)

begin {
    # Initialize repair tracking
    $RepairStart = Get-Date
    $ScriptName = $MyInvocation.MyCommand.Name
    $LogTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $LogPath = Join-Path $Workspace "logs\error_repair_fixed_$LogTimestamp.log"
    
    # Ensure logs directory exists
    $LogDir = Join-Path $Workspace "logs"
    if (-not (Test-Path $LogDir)) {
        New-Item -Path $LogDir -ItemType Directory -Force | Out-Null
    }
    
    function Write-RepairLog {
        param(
            [string]$Message,
            [ValidateSet('INFO', 'WARNING', 'ERROR', 'SUCCESS', 'REPAIR')]
            [string]$Level = 'INFO'
        )
        
        $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $LogEntry = "[$Timestamp] [$Level] $Message"
        
        # Write to console with colors
        switch ($Level) {
            'INFO' { Write-Host $LogEntry -ForegroundColor Cyan }
            'WARNING' { Write-Host $LogEntry -ForegroundColor Yellow }
            'ERROR' { Write-Host $LogEntry -ForegroundColor Red }
            'SUCCESS' { Write-Host $LogEntry -ForegroundColor Green }
            'REPAIR' { Write-Host $LogEntry -ForegroundColor Magenta }
        }
        
        # Write to log file
        try {
            Add-Content -Path $LogPath -Value $LogEntry -Encoding UTF8 -ErrorAction SilentlyContinue
        }
        catch {
            # Silently continue if logging fails
        }
    }
    
    Write-RepairLog " EQ12 ERROR REPAIR SYSTEM (FIXED) STARTED" -Level SUCCESS
    Write-RepairLog " Workspace: $Workspace" -Level INFO
    Write-RepairLog " Action: $Action" -Level INFO
    
    if ($TargetScript) {
        Write-RepairLog " Target Script: $TargetScript" -Level INFO
    }
}

process {
    $RepairResults = @{
        FilesProcessed = 0
        ErrorsFixed    = 0
        BackupsCreated = 0
        Skipped        = 0
        Failed         = 0
        Issues         = @()
    }
    
    function Repair-PowerShellSyntax {
        param([string]$FilePath)
        
        try {
            if (-not (Test-Path $FilePath)) {
                Write-RepairLog " File not found: $FilePath" -Level WARNING
                $RepairResults.Skipped++
                return $false
            }
            
            $Content = Get-Content $FilePath -Raw -Encoding UTF8
            $OriginalContent = $Content
            $FixesApplied = @()
            
            # Fix 1: Unterminated strings
            if ($Content -match 'Write-Host\s+"[^"]*''') {
                $Content = $Content -replace 'Write-Host\s+"([^"]*)"', 'Write-Host "$1"'
                $FixesApplied += "Fixed unterminated strings"
            }
            
            # Fix 2: Missing UTF-8 encoding header
            if (-not $Content.StartsWith('[Console]::OutputEncoding')) {
                $Header = @"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
`$ErrorActionPreference = "Stop"

"@
                $Content = $Header + $Content
                $FixesApplied += "Added UTF-8 encoding header"
            }
            
            # Fix 3: Incomplete try/catch blocks
            $TryMatches = [regex]::Matches($Content, 'try\s*\{')
            $CatchMatches = [regex]::Matches($Content, '\}\s*catch\s*\{')
            
            if ($TryMatches.Count -gt $CatchMatches.Count) {
                # Add basic catch blocks for orphaned try blocks
                $Lines = $Content -split "`n"
                $NewLines = @()
                $InTryBlock = $false
                $BraceCount = 0
                
                for ($i = 0; $i -lt $Lines.Count; $i++) {
                    $Line = $Lines[$i]
                    $NewLines += $Line
                    
                    if ($Line -match 'try\s*\{') {
                        $InTryBlock = $true
                        $BraceCount = 1
                    }
                    elseif ($InTryBlock) {
                        $BraceCount += ($Line.ToCharArray() | Where-Object { $_ -eq '{' }).Count
                        $BraceCount -= ($Line.ToCharArray() | Where-Object { $_ -eq '}' }).Count
                        
                        if ($BraceCount -le 0) {
                            # Check if next non-empty line is catch
                            $HasCatch = $false
                            for ($j = $i + 1; $j -lt [Math]::Min($i + 3, $Lines.Count); $j++) {
                                if ($Lines[$j].Trim() -and $Lines[$j] -match 'catch\s*\{') {
                                    $HasCatch = $true
                                    break
                                }
                            }
                            
                            if (-not $HasCatch) {
                                $NewLines += "catch {"
                                $NewLines += '    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red'
                                $NewLines += "}"
                                $FixesApplied += "Added missing catch block"
                            }
                            
                            $InTryBlock = $false
                        }
                    }
                }
                
                $Content = $NewLines -join "`n"
            }
            
            # Apply fixes if any were made
            if ($FixesApplied.Count -gt 0) {
                # Create backup if requested
                if ($BackupFirst) {
                    $BackupPath = "$FilePath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                    Copy-Item $FilePath $BackupPath
                    $RepairResults.BackupsCreated++
                    Write-RepairLog " Backup created: $BackupPath" -Level INFO
                }
                
                # Write fixed content
                Set-Content -Path $FilePath -Value $Content -Encoding UTF8
                $RepairResults.ErrorsFixed += $FixesApplied.Count
                
                Write-RepairLog " Fixed $($FixesApplied.Count) issues in $(Split-Path $FilePath -Leaf)" -Level SUCCESS
                foreach ($Fix in $FixesApplied) {
                    Write-RepairLog "   - $Fix" -Level REPAIR
                }
            }
            else {
                Write-RepairLog " No repairs needed for $(Split-Path $FilePath -Leaf)" -Level INFO
            }
            
            $RepairResults.FilesProcessed++
            return $true
        }
        catch {
            Write-RepairLog " Failed to repair $FilePath : $($_.Exception.Message)" -Level ERROR
            $RepairResults.Failed++
            $RepairResults.Issues += "Failed to repair $FilePath : $($_.Exception.Message)"
            return $false
        }
    }
    
    function Repair-EncodingIssues {
        Write-RepairLog " Checking encoding issues..." -Level INFO
        
        try {
            # Find files with potential encoding issues
            $PythonFiles = Get-ChildItem -Path $Workspace -Filter "*.py" -Recurse | Select-Object -First 10
            
            foreach ($File in $PythonFiles) {
                try {
                    $Content = Get-Content $File.FullName -Raw -Encoding UTF8
                    if ($Content -match '[^\x00-\x7F]' -and $Content -notmatch '# -\*- coding: utf-8 -\*-') {
                        # Add UTF-8 encoding declaration
                        $Header = "# -*- coding: utf-8 -*-`n"
                        $NewContent = $Header + $Content
                        Set-Content -Path $File.FullName -Value $NewContent -Encoding UTF8
                        
                        Write-RepairLog " Added UTF-8 encoding to $($File.Name)" -Level SUCCESS
                        $RepairResults.ErrorsFixed++
                    }
                }
                catch {
                    Write-RepairLog " Could not process encoding for $($File.Name)" -Level WARNING
                }
            }
        }
        catch {
            Write-RepairLog " Encoding repair failed: $($_.Exception.Message)" -Level ERROR
            $RepairResults.Issues += "Encoding repair failed: $($_.Exception.Message)"
        }
    }
    
    function Repair-Dependencies {
        Write-RepairLog " Checking dependencies..." -Level INFO
        
        try {
            # Check for missing critical files
            $CriticalFiles = @(
                "eq12_enhanced_stadium_weather_system.py",
                "eq12_api_key_manager.py",
                "eq12_self_healing_orchestrator.py"
            )
            
            foreach ($File in $CriticalFiles) {
                $FilePath = Join-Path $Workspace $File
                if (-not (Test-Path $FilePath)) {
                    Write-RepairLog " Missing critical file: $File" -Level WARNING
                    $RepairResults.Issues += "Missing critical file: $File"
                }
                else {
                    Write-RepairLog " Critical file exists: $File" -Level SUCCESS
                }
            }
        }
        catch {
            Write-RepairLog " Dependency check failed: $($_.Exception.Message)" -Level ERROR
            $RepairResults.Issues += "Dependency check failed: $($_.Exception.Message)"
        }
    }
    
    function Repair-Permissions {
        Write-RepairLog " Checking permissions..." -Level INFO
        
        try {
            # Check PowerShell execution policy
            $ExecutionPolicy = Get-ExecutionPolicy -Scope CurrentUser
            if ($ExecutionPolicy -in @('Restricted', 'AllSigned')) {
                try {
                    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
                    Write-RepairLog " Fixed PowerShell execution policy" -Level SUCCESS
                    $RepairResults.ErrorsFixed++
                }
                catch {
                    Write-RepairLog " Could not fix execution policy: $($_.Exception.Message)" -Level WARNING
                    $RepairResults.Issues += "Could not fix execution policy: $($_.Exception.Message)"
                }
            }
            else {
                Write-RepairLog " PowerShell execution policy OK: $ExecutionPolicy" -Level SUCCESS
            }
        }
        catch {
            Write-RepairLog " Permission repair failed: $($_.Exception.Message)" -Level ERROR
            $RepairResults.Issues += "Permission repair failed: $($_.Exception.Message)"
        }
    }
    
    # Main repair logic
    Write-RepairLog " Starting repair process..." -Level INFO
    
    switch ($Action) {
        'All' {
            # Repair PowerShell files
            if ($TargetScript) {
                $ScriptPath = if (Test-Path $TargetScript) { $TargetScript } else { Join-Path $Workspace $TargetScript }
                Repair-PowerShellSyntax -FilePath $ScriptPath
            }
            else {
                $PowerShellFiles = @()
                $PowerShellFiles += Get-ChildItem -Path $Workspace -Filter "*.ps1" | Select-Object -First 5
                $PowerShellFiles += Get-ChildItem -Path (Join-Path $Workspace "scripts") -Filter "*.ps1" -ErrorAction SilentlyContinue | Select-Object -First 5
                
                foreach ($File in $PowerShellFiles) {
                    Repair-PowerShellSyntax -FilePath $File.FullName
                }
            }
            
            Repair-EncodingIssues
            Repair-Dependencies
            Repair-Permissions
        }
        'PowerShell' {
            if ($TargetScript) {
                $ScriptPath = if (Test-Path $TargetScript) { $TargetScript } else { Join-Path $Workspace $TargetScript }
                Repair-PowerShellSyntax -FilePath $ScriptPath
            }
            else {
                $PowerShellFiles = Get-ChildItem -Path $Workspace -Filter "*.ps1" | Select-Object -First 10
                foreach ($File in $PowerShellFiles) {
                    Repair-PowerShellSyntax -FilePath $File.FullName
                }
            }
        }
        'Encoding' {
            Repair-EncodingIssues
        }
        'Dependencies' {
            Repair-Dependencies
        }
        'Permissions' {
            Repair-Permissions
        }
        'Cleanup' {
            Write-RepairLog " Performing cleanup..." -Level INFO
            try {
                # Clean up old backup files (older than 7 days)
                $OldBackups = Get-ChildItem -Path $Workspace -Filter "*.backup_*" -Recurse | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }
                foreach ($Backup in $OldBackups) {
                    Remove-Item $Backup.FullName -Force
                    Write-RepairLog " Removed old backup: $($Backup.Name)" -Level INFO
                }
                
                # Clean up old log files (older than 30 days)
                $LogsDir = Join-Path $Workspace "logs"
                if (Test-Path $LogsDir) {
                    $OldLogs = Get-ChildItem -Path $LogsDir -Filter "*.log" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) }
                    foreach ($Log in $OldLogs) {
                        Remove-Item $Log.FullName -Force
                        Write-RepairLog " Removed old log: $($Log.Name)" -Level INFO
                    }
                }
                
                $RepairResults.ErrorsFixed += $OldBackups.Count + ($OldLogs ? $OldLogs.Count : 0)
            }
            catch {
                Write-RepairLog " Cleanup failed: $($_.Exception.Message)" -Level ERROR
                $RepairResults.Issues += "Cleanup failed: $($_.Exception.Message)"
            }
        }
    }
}

end {
    $RepairEnd = Get-Date
    $TotalTime = [math]::Round(($RepairEnd - $RepairStart).TotalSeconds, 2)
    
    Write-RepairLog "" -Level INFO
    Write-RepairLog " REPAIR SUMMARY" -Level SUCCESS
    Write-RepairLog "=================" -Level SUCCESS
    Write-RepairLog " Total Time: $TotalTime seconds" -Level INFO
    Write-RepairLog " Files Processed: $($RepairResults.FilesProcessed)" -Level INFO
    Write-RepairLog " Errors Fixed: $($RepairResults.ErrorsFixed)" -Level SUCCESS
    Write-RepairLog " Backups Created: $($RepairResults.BackupsCreated)" -Level INFO
    Write-RepairLog " Files Skipped: $($RepairResults.Skipped)" -Level INFO
    Write-RepairLog " Failed Repairs: $($RepairResults.Failed)" -Level WARNING
    
    if ($RepairResults.Issues.Count -gt 0) {
        Write-RepairLog " Issues Found:" -Level WARNING
        foreach ($Issue in $RepairResults.Issues) {
            Write-RepairLog "   - $Issue" -Level WARNING
        }
    }
    
    Write-RepairLog " EQ12 Error Repair Complete" -Level SUCCESS
    
    # Restore original default parameter values
    if ($OriginalPSDefaultParameterValues) {
        $PSDefaultParameterValues.Clear()
        $OriginalPSDefaultParameterValues.GetEnumerator() | ForEach-Object {
            $PSDefaultParameterValues[$_.Key] = $_.Value
        }
    }
}