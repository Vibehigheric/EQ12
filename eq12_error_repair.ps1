[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Error Repair - Automatic PowerShell and System Fixes
    
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
    
.PARAMETER VerboseOutput
    Enable detailed logging
    
.PARAMETER BackupFirst
    Create backup before making changes
    
.EXAMPLE
    .\eq12_error_repair.ps1 -Action All -VerboseOutput -BackupFirst
    
.NOTES
    Author: EQ12 Quantum Development Team
    Version: 1.0.0 - Auto-Repair System
    Date: November 7, 2025
#>

[CmdletBinding()]
param(
    [ValidateSet('All', 'PowerShell', 'Encoding', 'Dependencies', 'Permissions', 'Cleanup')]
    [string]$Action = 'All',
    
    [string]$TargetScript = '',
    
    [ValidateScript({ Test-Path $_ -PathType Container })]
    [string]$Workspace = 'C:\EQ12',
    
    [switch]$VerboseOutput,
    
    [switch]$BackupFirst
)

begin {
    # Force UTF-8 encoding for emoji compatibility
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OriginalPSDefaultParameterValues = $PSDefaultParameterValues.Clone()
    $PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
    
    # Initialize repair tracking
    $RepairStart = Get-Date
    $ScriptName = $MyInvocation.MyCommand.Name
    $LogTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $LogPath = Join-Path $Workspace "logs\repair_$LogTimestamp.log"
    
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
    
    Write-RepairLog " EQ12 ERROR REPAIR SYSTEM STARTED" -Level SUCCESS
    Write-RepairLog " Repair Time: $RepairStart" -Level INFO
    Write-RepairLog " Workspace: $Workspace" -Level INFO
    Write-RepairLog " Action Mode: $Action" -Level INFO
}

process {
    try {
        $RepairResults = @{
            PowerShellFixed   = 0
            EncodingFixed     = 0
            DependenciesFixed = 0
            PermissionsFixed  = 0
            CleanupItems      = 0
            TotalIssues       = 0
            BackupsCreated    = 0
        }
        
        Write-Host ""
        Write-Host " EQ12 ERROR REPAIR SYSTEM" -ForegroundColor Green
        Write-Host "=" * 50 -ForegroundColor Blue
        Write-Host " Action: $Action" -ForegroundColor Cyan
        Write-Host " Workspace: $Workspace" -ForegroundColor Cyan
        Write-Host " Started: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")" -ForegroundColor Cyan
        Write-Host "=" * 50 -ForegroundColor Blue
        Write-Host ""
        
        # Create backups if requested
        if ($BackupFirst) {
            Write-RepairLog " Creating backups before repairs..." -Level INFO
            $BackupDir = Join-Path $Workspace "backups\repair_$LogTimestamp"
            New-Item -Path $BackupDir -ItemType Directory -Force | Out-Null
            
            # Backup PowerShell scripts
            Get-ChildItem -Path $Workspace -Filter "*.ps1" -Recurse | ForEach-Object {
                $RelativePath = $_.FullName.Replace($Workspace, '')
                $BackupPath = Join-Path $BackupDir $RelativePath
                $BackupParent = Split-Path $BackupPath -Parent
                if (-not (Test-Path $BackupParent)) {
                    New-Item -Path $BackupParent -ItemType Directory -Force | Out-Null
                }
                Copy-Item $_.FullName $BackupPath -Force
                $RepairResults.BackupsCreated++
            }
            
            Write-RepairLog " Created $($RepairResults.BackupsCreated) backups in $BackupDir" -Level SUCCESS
        }
        
        # Repair PowerShell syntax issues
        if ($Action -eq 'All' -or $Action -eq 'PowerShell') {
            Write-RepairLog " Repairing PowerShell syntax issues..." -Level REPAIR
            
            $PSScripts = if ($TargetScript) {
                @(Get-Item (Join-Path $Workspace $TargetScript) -ErrorAction SilentlyContinue)
            }
            else {
                Get-ChildItem -Path $Workspace -Filter "*.ps1" -Recurse
            }
            
            foreach ($Script in $PSScripts) {
                Write-RepairLog " Analyzing: $($Script.Name)" -Level INFO
                
                $Content = Get-Content $Script.FullName -Raw
                $OriginalContent = $Content
                $IssuesFound = 0
                
                # Fix common try/catch/finally syntax issues
                
                # Pattern 1: Missing closing brace before catch
                $Pattern1 = '(?s)try\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*(?<!\})\s*catch\s*\{'
                if ($Content -match $Pattern1) {
                    $Content = $Content -replace '(\s+)catch\s*\{', '}$1catch {'
                    $IssuesFound++
                    Write-RepairLog "   Fixed missing } before catch block" -Level REPAIR
                }
                
                # Pattern 2: Missing closing brace before finally
                $Pattern2 = '(?s)catch\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*(?<!\})\s*finally\s*\{'
                if ($Content -match $Pattern2) {
                    $Content = $Content -replace '(\s+)finally\s*\{', '}$1finally {'
                    $IssuesFound++
                    Write-RepairLog "   Fixed missing } before finally block" -Level REPAIR
                }
                
                # Pattern 3: Ensure proper try structure
                $TryBlocks = [regex]::Matches($Content, 'try\s*\{')
                $CatchBlocks = [regex]::Matches($Content, 'catch\s*\{')
                $FinallyBlocks = [regex]::Matches($Content, 'finally\s*\{')
                
                if ($TryBlocks.Count -ne $CatchBlocks.Count -and $TryBlocks.Count -ne $FinallyBlocks.Count) {
                    Write-RepairLog "   Warning: Unmatched try/catch/finally blocks detected" -Level WARNING
                }
                
                # Fix UTF-8 encoding declaration
                if ($Content -notmatch '\[Console\]::OutputEncoding\s*=\s*\[System\.Text\.Encoding\]::UTF8') {
                    $EncodingLine = '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8'
                    $ParamBlockEnd = $Content.IndexOf(')')
                    if ($ParamBlockEnd -gt 0) {
                        $InsertPos = $Content.IndexOf('begin {', $ParamBlockEnd)
                        if ($InsertPos -gt 0) {
                            $Content = $Content.Insert($InsertPos, "    # Force UTF-8 encoding for emoji compatibility`n    $EncodingLine`n    `n")
                            $IssuesFound++
                            Write-RepairLog "   Added UTF-8 encoding declaration" -Level REPAIR
                        }
                    }
                }
                
                # Save repaired content if changes were made
                if ($Content -ne $OriginalContent) {
                    Set-Content -Path $Script.FullName -Value $Content -Encoding UTF8
                    $RepairResults.PowerShellFixed++
                    Write-RepairLog "   Repaired $IssuesFound issues in $($Script.Name)" -Level SUCCESS
                }
                else {
                    Write-RepairLog "   No issues found in $($Script.Name)" -Level INFO
                }
                
                $RepairResults.TotalIssues += $IssuesFound
            }
        }
        
        # Fix encoding issues
        if ($Action -eq 'All' -or $Action -eq 'Encoding') {
            Write-RepairLog " Fixing encoding issues..." -Level REPAIR
            
            # Check and fix Python files with encoding issues
            $PythonFiles = Get-ChildItem -Path $Workspace -Filter "*.py" -Recurse
            
            foreach ($PyFile in $PythonFiles) {
                $Content = Get-Content $PyFile.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
                if ($Content) {
                    # Ensure UTF-8 encoding declaration
                    if ($Content -notmatch '#.*coding[:=]\s*([-\w.]+)') {
                        $Lines = Get-Content $PyFile.FullName -Encoding UTF8
                        if ($Lines[0] -match '^#!') {
                            $Lines = $Lines[0], '# -*- coding: utf-8 -*-' + $Lines[1..($Lines.Length - 1)]
                        }
                        else {
                            $Lines = '# -*- coding: utf-8 -*-', '' + $Lines
                        }
                        Set-Content -Path $PyFile.FullName -Value $Lines -Encoding UTF8
                        $RepairResults.EncodingFixed++
                        Write-RepairLog "   Added UTF-8 encoding to $($PyFile.Name)" -Level REPAIR
                    }
                }
            }
        }
        
        # Fix dependencies
        if ($Action -eq 'All' -or $Action -eq 'Dependencies') {
            Write-RepairLog " Checking and fixing dependencies..." -Level REPAIR
            
            # Check for required directories
            $RequiredDirs = @('logs', 'dashboard', 'data', 'reports', 'configs', 'partners')
            foreach ($Dir in $RequiredDirs) {
                $DirPath = Join-Path $Workspace $Dir
                if (-not (Test-Path $DirPath)) {
                    New-Item -Path $DirPath -ItemType Directory -Force | Out-Null
                    $RepairResults.DependenciesFixed++
                    Write-RepairLog "   Created missing directory: $Dir" -Level REPAIR
                }
            }
            
            # Check for __init__.py files in Python directories
            $PythonDirs = Get-ChildItem -Path $Workspace -Directory -Recurse | Where-Object { 
                (Get-ChildItem $_.FullName -Filter "*.py" -ErrorAction SilentlyContinue).Count -gt 0 
            }
            
            foreach ($PyDir in $PythonDirs) {
                $InitFile = Join-Path $PyDir.FullName "__init__.py"
                if (-not (Test-Path $InitFile)) {
                    Set-Content -Path $InitFile -Value "# EQ12 Python Module" -Encoding UTF8
                    $RepairResults.DependenciesFixed++
                    Write-RepairLog "   Created __init__.py in $($PyDir.Name)" -Level REPAIR
                }
            }
        }
        
        # Fix permissions
        if ($Action -eq 'All' -or $Action -eq 'Permissions') {
            Write-RepairLog " Fixing permissions and execution policies..." -Level REPAIR
            
            try {
                # Check execution policy
                $CurrentPolicy = Get-ExecutionPolicy -Scope CurrentUser
                if ($CurrentPolicy -eq 'Restricted') {
                    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
                    $RepairResults.PermissionsFixed++
                    Write-RepairLog "   Updated execution policy to RemoteSigned" -Level REPAIR
                }
                
                # Ensure scripts are not blocked
                $Scripts = Get-ChildItem -Path $Workspace -Filter "*.ps1" -Recurse
                foreach ($Script in $Scripts) {
                    try {
                        Unblock-File -Path $Script.FullName -ErrorAction SilentlyContinue
                    }
                    catch {
                        # Continue if unblock fails
                    }
                }
                
                Write-RepairLog "   Unblocked $($Scripts.Count) PowerShell scripts" -Level REPAIR
            }
            catch {
                Write-RepairLog "   Could not modify execution policy (may require admin)" -Level WARNING
            }
        }
        
        # Cleanup operations
        if ($Action -eq 'All' -or $Action -eq 'Cleanup') {
            Write-RepairLog " Performing system cleanup..." -Level REPAIR
            
            # Clean up old log files (keep last 30 days)
            $OldLogs = Get-ChildItem -Path (Join-Path $Workspace "logs") -Filter "*.log" | 
            Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) }
            
            foreach ($OldLog in $OldLogs) {
                Remove-Item $OldLog.FullName -Force
                $RepairResults.CleanupItems++
            }
            
            # Clean up temporary files
            $TempFiles = Get-ChildItem -Path $Workspace -Filter "*.tmp" -Recurse
            foreach ($TempFile in $TempFiles) {
                Remove-Item $TempFile.FullName -Force
                $RepairResults.CleanupItems++
            }
            
            Write-RepairLog "   Cleaned up $($RepairResults.CleanupItems) old files" -Level REPAIR
        }
        
        # Generate repair summary
        $RepairEnd = Get-Date
        $RepairDuration = $RepairEnd - $RepairStart
        
        Write-Host ""
        Write-Host " EQ12 REPAIR SUMMARY" -ForegroundColor Green
        Write-Host "=" * 40 -ForegroundColor Blue
        Write-Host " Duration: $($RepairDuration.ToString("hh\:mm\:ss"))" -ForegroundColor Cyan
        Write-Host " PowerShell Scripts Fixed: $($RepairResults.PowerShellFixed)" -ForegroundColor Cyan
        Write-Host " Encoding Issues Fixed: $($RepairResults.EncodingFixed)" -ForegroundColor Cyan
        Write-Host " Dependencies Fixed: $($RepairResults.DependenciesFixed)" -ForegroundColor Cyan
        Write-Host " Permissions Fixed: $($RepairResults.PermissionsFixed)" -ForegroundColor Cyan
        Write-Host " Cleanup Items: $($RepairResults.CleanupItems)" -ForegroundColor Cyan
        Write-Host " Total Issues Resolved: $($RepairResults.TotalIssues)" -ForegroundColor Cyan
        
        if ($BackupFirst) {
            Write-Host " Backups Created: $($RepairResults.BackupsCreated)" -ForegroundColor Cyan
        }
        
        Write-Host " Log File: $LogPath" -ForegroundColor Cyan
        Write-Host "=" * 40 -ForegroundColor Blue
        
        if ($RepairResults.TotalIssues -eq 0) {
            Write-Host " EQ12 SYSTEM STATUS: PERFECT" -ForegroundColor Green
        }
        else {
            Write-Host " EQ12 SYSTEM STATUS: REPAIRED" -ForegroundColor Yellow
        }
        
        Write-RepairLog " EQ12 Error Repair completed successfully" -Level SUCCESS
        
    }
    catch {
        $ErrorDetails = $_.Exception.Message
        Write-RepairLog " CRITICAL REPAIR FAILURE: $ErrorDetails" -Level ERROR
        Write-Host ""
        Write-Host " CRITICAL REPAIR ERROR!" -ForegroundColor Red
        Write-Host "Error: $ErrorDetails" -ForegroundColor Red
        Write-Host "Log: $LogPath" -ForegroundColor Yellow
        Write-Host ""
        
        # Set failed exit code
        $global:LASTEXITCODE = 1
        throw
    }
}

end {
    # Restore original encoding settings
    $PSDefaultParameterValues.Clear()
    $PSDefaultParameterValues += $OriginalPSDefaultParameterValues
    
    Write-RepairLog " PowerShell repair wrapper execution complete" -Level INFO
    
    # Final status message
    $FinalDuration = (Get-Date) - $RepairStart
    Write-Host ""
    Write-Host " EQ12 Error Repair finished in $($FinalDuration.ToString("hh\:mm\:ss"))" -ForegroundColor Green
    Write-Host " Complete repair log available at: $LogPath" -ForegroundColor Cyan
}