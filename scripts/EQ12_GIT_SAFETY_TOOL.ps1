<#
.SYNOPSIS
    EQ12 Git Safety Tool - Safely maintains Git repository health
.DESCRIPTION
    Performs safe Git repository maintenance:
    - Clears read-only flags that block Git operations
    - Removes stale lock files (.git\index.lock, HEAD.lock, refs\*.lock)
    - NEVER deletes the .git directory itself
    - Logs all actions with UTC timestamps
.PARAMETER RepoPath
    Path to the Git repository. Defaults to C:\EQ12_BROKEN_20251122_210342
.PARAMETER DryRun
    Preview what would be done without making changes
.PARAMETER Force
    Skip confirmation prompts for lock file removal
.EXAMPLE
    .\EQ12_GIT_SAFETY_TOOL.ps1
    .\EQ12_GIT_SAFETY_TOOL.ps1 -DryRun
    .\EQ12_GIT_SAFETY_TOOL.ps1 -Force
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$RepoPath = "C:\EQ12_BROKEN_20251122_210342",

    [Parameter()]
    [switch]$DryRun,

    [Parameter()]
    [switch]$Force
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Initialize logging
$LogDir = Join-Path $RepoPath "logs"
if (-not (Test-Path $LogDir)) {
    New-Item -Path $LogDir -ItemType Directory -Force | Out-Null
}

$ScriptName = [System.IO.Path]::GetFileNameWithoutExtension($MyInvocation.MyCommand.Name)
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "${ScriptName}_LOG_${Timestamp}.txt"

function Write-Log {
    [CmdletBinding()]
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $LogEntry = "[{0:yyyy-MM-dd HH:mm:ss}] [{1}] {2}" -f (Get-Date).ToUniversalTime(), $Level, $Message
    
    switch ($Level) {
        "ERROR" { Write-Host $LogEntry -ForegroundColor Red }
        "WARN"  { Write-Host $LogEntry -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $LogEntry -ForegroundColor Green }
        default { Write-Host $LogEntry }
    }
    
    Add-Content -Path $LogFile -Value $LogEntry -ErrorAction SilentlyContinue
}

Write-Log "===== EQ12 GIT SAFETY TOOL STARTED ====="
Write-Log "Repository path: $RepoPath"
Write-Log "Dry run: $DryRun"

# Verify repo exists
if (-not (Test-Path $RepoPath)) {
    Write-Log "Repository path not found: $RepoPath" -Level "ERROR"
    throw "Repository path not found"
}

$GitDir = Join-Path $RepoPath ".git"
if (-not (Test-Path $GitDir)) {
    Write-Log "Not a Git repository (no .git directory found)" -Level "ERROR"
    throw "Not a Git repository"
}

Write-Log ".git directory confirmed at: $GitDir" -Level "SUCCESS"

# Results tracking
$Results = @{
    ReadOnlyFilesCleared = 0
    LockFilesRemoved = @()
    Errors = @()
}

# Task 1: Clear read-only flags
Write-Log ""
Write-Log "Task 1: Clearing read-only flags..."

try {
    $ReadOnlyFiles = Get-ChildItem -Path $RepoPath -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.IsReadOnly }
    
    Write-Log "Found $($ReadOnlyFiles.Count) read-only files"
    
    foreach ($File in $ReadOnlyFiles) {
        try {
            if (-not $DryRun) {
                $File.IsReadOnly = $false
                $Results.ReadOnlyFilesCleared++
                Write-Log "  Cleared: $($File.FullName)" -Level "SUCCESS"
            }
            else {
                Write-Log "  [DRY RUN] Would clear: $($File.FullName)"
            }
        }
        catch {
            $ErrorMsg = "Failed to clear read-only on $($File.FullName): $_"
            Write-Log "  $ErrorMsg" -Level "ERROR"
            $Results.Errors += $ErrorMsg
        }
    }
}
catch {
    $ErrorMsg = "Error scanning for read-only files: $_"
    Write-Log $ErrorMsg -Level "ERROR"
    $Results.Errors += $ErrorMsg
}

# Task 2: Remove stale lock files
Write-Log ""
Write-Log "Task 2: Checking for stale Git lock files..."

$LockFilePaths = @(
    (Join-Path $GitDir "index.lock"),
    (Join-Path $GitDir "HEAD.lock"),
    (Join-Path $GitDir "config.lock"),
    (Join-Path $GitDir "COMMIT_EDITMSG.lock"),
    (Join-Path $GitDir "refs\heads\*.lock"),
    (Join-Path $GitDir "refs\remotes\*.lock")
)

$StaleLockFiles = @()
foreach ($LockPath in $LockFilePaths) {
    $Found = Get-ChildItem -Path $LockPath -ErrorAction SilentlyContinue
    if ($Found) {
        $StaleLockFiles += $Found
    }
}

if ($StaleLockFiles.Count -eq 0) {
    Write-Log "No stale lock files found" -Level "SUCCESS"
}
else {
    Write-Log "Found $($StaleLockFiles.Count) stale lock files:" -Level "WARN"
    
    foreach ($LockFile in $StaleLockFiles) {
        Write-Log "  $($LockFile.FullName)" -Level "WARN"
    }
    
    $Proceed = $Force
    if (-not $Force -and -not $DryRun) {
        $Response = Read-Host "Remove these lock files? [Y/N]"
        $Proceed = $Response -eq "Y" -or $Response -eq "y"
    }
    
    if ($Proceed -or $DryRun) {
        foreach ($LockFile in $StaleLockFiles) {
            try {
                if (-not $DryRun) {
                    Remove-Item -Path $LockFile.FullName -Force
                    $Results.LockFilesRemoved += $LockFile.FullName
                    Write-Log "  Removed: $($LockFile.FullName)" -Level "SUCCESS"
                }
                else {
                    Write-Log "  [DRY RUN] Would remove: $($LockFile.FullName)"
                }
            }
            catch {
                $ErrorMsg = "Failed to remove $($LockFile.FullName): $_"
                Write-Log "  $ErrorMsg" -Level "ERROR"
                $Results.Errors += $ErrorMsg
            }
        }
    }
    else {
        Write-Log "Lock file removal skipped by user"
    }
}

# Task 3: Verify .git directory integrity (read-only, never delete)
Write-Log ""
Write-Log "Task 3: Verifying .git directory integrity..."

$CriticalGitFiles = @(
    (Join-Path $GitDir "config"),
    (Join-Path $GitDir "HEAD"),
    (Join-Path $GitDir "refs")
)

$AllPresent = $true
foreach ($CriticalPath in $CriticalGitFiles) {
    if (Test-Path $CriticalPath) {
        Write-Log "  ✓ $CriticalPath" -Level "SUCCESS"
    }
    else {
        Write-Log "  ✗ MISSING: $CriticalPath" -Level "ERROR"
        $Results.Errors += "Missing critical Git file: $CriticalPath"
        $AllPresent = $false
    }
}

if ($AllPresent) {
    Write-Log ".git directory integrity verified" -Level "SUCCESS"
}

# Summary
Write-Log ""
Write-Log "===== SUMMARY ====="
Write-Log "Read-only files cleared: $($Results.ReadOnlyFilesCleared)"
Write-Log "Lock files removed: $($Results.LockFilesRemoved.Count)"
Write-Log "Errors encountered: $($Results.Errors.Count)"

if ($Results.Errors.Count -gt 0) {
    Write-Log ""
    Write-Log "ERRORS:" -Level "ERROR"
    foreach ($Error in $Results.Errors) {
        Write-Log "  - $Error" -Level "ERROR"
    }
}

Write-Log "Log written to: $LogFile"
Write-Log "===== EQ12 GIT SAFETY TOOL COMPLETED ====="

# Return results
return @{
    LogFile = $LogFile
    ReadOnlyFilesCleared = $Results.ReadOnlyFilesCleared
    LockFilesRemoved = $Results.LockFilesRemoved
    ErrorCount = $Results.Errors.Count
}
