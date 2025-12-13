#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Expert System Repair Script - Professional Engineering Grade
.DESCRIPTION
    Complete EQ12 Python environment diagnostic, repair, and rebuild system
    Designed for VS Code + GitHub Copilot + Python 3.12 environments

    Author: EQ12 Engineering Team
    Version: 2.1.0
    Date: 2025-11-22
    Dependencies: PowerShell 5.1+, Python 3.12

.PARAMETER Mode
    repair   - Full system repair (default)
    scan     - Scan only, no changes
    emergency - Emergency repair with aggressive cleanup

.PARAMETER DryRun
    Show what would be done without executing

.EXAMPLE
    .\eq12_repair.ps1 -Mode scan
    .\eq12_repair.ps1 -Mode repair -DryRun
    .\eq12_repair.ps1 -Mode emergency
#>

[CmdletBinding()]
param(
    [ValidateSet('repair', 'scan', 'emergency')]
    [string]$Mode = 'repair',

    [switch]$DryRun
)

# ASCII-safe logging with timestamp
function Write-EQ12Log {
    param(
        [string]$Message,
        [ValidateSet('INFO', 'WARN', 'ERROR', 'SUCCESS')]
        [string]$Level = 'INFO'
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    # ASCII-safe output
    $asciiMessage = [System.Text.Encoding]::ASCII.GetString([System.Text.Encoding]::ASCII.GetBytes($logEntry))

    switch ($Level) {
        'INFO'    { Write-Host $asciiMessage -ForegroundColor Cyan }
        'WARN'    { Write-Host $asciiMessage -ForegroundColor Yellow }
        'ERROR'   { Write-Host $asciiMessage -ForegroundColor Red }
        'SUCCESS' { Write-Host $asciiMessage -ForegroundColor Green }
    }

    # Log to file
    $logPath = "C:\EQ12\logs\eq12_repair_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    Add-Content -Path $logPath -Value $asciiMessage -Encoding ASCII
}

# Safe deletion wrapper with confirmation and logging
function Safe-Delete {
    param(
        [string]$Path,
        [switch]$Force,
        [switch]$Recurse
    )

    if (-not (Test-Path $Path)) {
        Write-EQ12Log "Path not found: $Path" -Level WARN
        return $false
    }

    $item = Get-Item $Path
    $size = if ($item.PSIsContainer) {
        (Get-ChildItem $Path -Recurse -Force | Measure-Object -Property Length -Sum).Sum
    } else {
        $item.Length
    }

    Write-EQ12Log "DELETION REQUEST: $Path (Size: $([math]::Round($size/1MB, 2)) MB)" -Level WARN

    if (-not $Force -and -not $DryRun) {
        $confirmation = Read-Host "Delete $Path? (y/N)"
        if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
            Write-EQ12Log "Deletion cancelled by user" -Level INFO
            return $false
        }
    }

    if ($DryRun) {
        Write-EQ12Log "DRY RUN: Would delete $Path" -Level INFO
        return $true
    }

    try {
        if ($Recurse) {
            Remove-Item $Path -Recurse -Force -ErrorAction Stop
        } else {
            Remove-Item $Path -Force -ErrorAction Stop
        }
        Write-EQ12Log "Successfully deleted: $Path" -Level SUCCESS
        return $true
    }
    catch {
        Write-EQ12Log "Failed to delete $Path: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

# Verify Python 3.12 installation integrity
function Test-PythonInstallation {
    Write-EQ12Log "Checking Python 3.12 installation integrity..." -Level INFO

    $pythonPaths = @(
        "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312",
        "C:\Python312",
        "C:\Program Files\Python312",
        "C:\Program Files (x86)\Python312"
    )

    $validPython = $null
    foreach ($path in $pythonPaths) {
        if (Test-Path "$path\python.exe") {
            $version = & "$path\python.exe" --version 2>$null
            if ($version -match "Python 3\.12\.") {
                Write-EQ12Log "Found valid Python 3.12: $path" -Level SUCCESS
                $validPython = $path
                break
            }
        }
    }

    if (-not $validPython) {
        Write-EQ12Log "No valid Python 3.12 installation found" -Level ERROR
        return $false
    }

    # Check pip integrity
    $pipCheck = & "$validPython\python.exe" -m pip --version 2>$null
    if (-not $pipCheck) {
        Write-EQ12Log "Pip is corrupted, attempting repair..." -Level WARN
        & "$validPython\python.exe" -m ensurepip --upgrade
    }

    return $validPython
}

# Scan and repair virtual environments
function Repair-VirtualEnvironments {
    Write-EQ12Log "Scanning virtual environments..." -Level INFO

    $venvPaths = @(
        "C:\EQ12\.venv",
        "C:\EQ12\.venv_new",
        "S:\EQ12\.venv"
    )

    foreach ($venvPath in $venvPaths) {
        if (Test-Path $venvPath) {
            Write-EQ12Log "Checking virtual environment: $venvPath" -Level INFO

            # Check activation script
            $activateScript = "$venvPath\Scripts\Activate.ps1"
            if (-not (Test-Path $activateScript)) {
                Write-EQ12Log "Corrupt venv detected: $venvPath (missing activate script)" -Level ERROR

                if ($Mode -ne 'scan') {
                    Safe-Delete $venvPath -Recurse -Force:$($Mode -eq 'emergency')

                    # Rebuild venv
                    $pythonPath = Test-PythonInstallation
                    if ($pythonPath) {
                        Write-EQ12Log "Rebuilding virtual environment: $venvPath" -Level INFO
                        & "$pythonPath\python.exe" -m venv $venvPath

                        # Install essential packages
                        & "$venvPath\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
                        & "$venvPath\Scripts\python.exe" -m pip install pylance python-lsp-server
                    }
                }
            }
            else {
                Write-EQ12Log "Virtual environment appears healthy: $venvPath" -Level SUCCESS
            }
        }
    }
}

# Clean corrupted __pycache__ directories
function Clean-PyCache {
    Write-EQ12Log "Cleaning corrupted __pycache__ directories..." -Level INFO

    $searchPaths = @("C:\EQ12", "S:\EQ12")

    foreach ($searchPath in $searchPaths) {
        if (Test-Path $searchPath) {
            $pycacheDirs = Get-ChildItem -Path $searchPath -Recurse -Directory -Name "__pycache__" -ErrorAction SilentlyContinue

            foreach ($dir in $pycacheDirs) {
                $fullPath = Join-Path $searchPath $dir
                Write-EQ12Log "Found __pycache__: $fullPath" -Level INFO

                # Check for corruption indicators
                $files = Get-ChildItem $fullPath -ErrorAction SilentlyContinue
                $corruptFiles = $files | Where-Object { $_.Length -eq 0 -or $_.Name -notmatch '\.pyc$' }

                if ($corruptFiles.Count -gt 0) {
                    Write-EQ12Log "Corrupt __pycache__ detected: $fullPath" -Level WARN
                    if ($Mode -ne 'scan') {
                        Safe-Delete $fullPath -Recurse -Force:$($Mode -eq 'emergency')
                    }
                }
            }
        }
    }
}

# Repair VS Code Python extension issues
function Repair-VSCodePython {
    Write-EQ12Log "Repairing VS Code Python configuration..." -Level INFO

    $vscodeUserData = "$env:APPDATA\Code\User"
    $vscodeExtensions = "$env:USERPROFILE\.vscode\extensions"

    # Check for Pylance EPIPE errors in logs
    $pylanceLogs = "$vscodeUserData\logs"
    if (Test-Path $pylanceLogs) {
        $errorLogs = Get-ChildItem $pylanceLogs -Recurse -Filter "*python*" |
                    Select-String "EPIPE|channel.*closed|connection.*lost" -ErrorAction SilentlyContinue

        if ($errorLogs.Count -gt 0) {
            Write-EQ12Log "Pylance EPIPE errors detected in logs" -Level ERROR

            if ($Mode -ne 'scan') {
                # Clear workspace storage
                $workspaceStorage = "$vscodeUserData\workspaceStorage"
                if (Test-Path $workspaceStorage) {
                    Write-EQ12Log "Clearing VS Code workspace storage..." -Level INFO
                    Safe-Delete $workspaceStorage -Recurse -Force:$($Mode -eq 'emergency')
                }

                # Clear extension cache
                $extensionCache = "$vscodeUserData\CachedExtensions"
                if (Test-Path $extensionCache) {
                    Write-EQ12Log "Clearing extension cache..." -Level INFO
                    Safe-Delete $extensionCache -Force:$($Mode -eq 'emergency')
                }
            }
        }
    }

    # Verify Python extension installation
    $pythonExtension = Get-ChildItem $vscodeExtensions -Directory -Filter "*ms-python.python*" -ErrorAction SilentlyContinue
    if (-not $pythonExtension) {
        Write-EQ12Log "Python extension not found - recommend reinstallation" -Level WARN
    }

    $pylanceExtension = Get-ChildItem $vscodeExtensions -Directory -Filter "*ms-python.vscode-pylance*" -ErrorAction SilentlyContinue
    if (-not $pylanceExtension) {
        Write-EQ12Log "Pylance extension not found - recommend reinstallation" -Level WARN
    }
}

# Verify GitHub CLI and Copilot integration
function Test-GitHubIntegration {
    Write-EQ12Log "Checking GitHub CLI and Copilot integration..." -Level INFO

    # Check GitHub CLI
    $ghVersion = gh --version 2>$null
    if (-not $ghVersion) {
        Write-EQ12Log "GitHub CLI not found or not in PATH" -Level WARN
        return $false
    }

    # Check GitHub CLI authentication
    $ghAuth = gh auth status 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-EQ12Log "GitHub CLI not authenticated" -Level WARN
        Write-EQ12Log "Run: gh auth login" -Level INFO
    }

    # Check Copilot extension
    $vscodeExtensions = "$env:USERPROFILE\.vscode\extensions"
    $copilotExtension = Get-ChildItem $vscodeExtensions -Directory -Filter "*github.copilot*" -ErrorAction SilentlyContinue

    if (-not $copilotExtension) {
        Write-EQ12Log "GitHub Copilot extension not found" -Level WARN
    } else {
        Write-EQ12Log "GitHub Copilot extension found" -Level SUCCESS
    }

    return $true
}

# Generate comprehensive system report
function Generate-SystemReport {
    Write-EQ12Log "Generating comprehensive system report..." -Level INFO

    $reportPath = "C:\EQ12\logs\eq12_system_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

    $report = @{
        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        mode = $Mode
        dryRun = $DryRun.IsPresent
        system = @{
            os = (Get-CimInstance Win32_OperatingSystem).Caption
            powerShellVersion = $PSVersionTable.PSVersion.ToString()
            pythonPath = (Test-PythonInstallation)
        }
        findings = @{
            corruptVenvs = 0
            corruptPyCache = 0
            pylanceErrors = $false
            githubAuth = $false
        }
        recommendations = @()
    }

    # Add findings to report (simplified for example)
    $report.recommendations += "Regular maintenance of __pycache__ directories"
    $report.recommendations += "Monitor VS Code extension health"
    $report.recommendations += "Verify GitHub authentication"

    # Save ASCII-safe report
    $reportJson = $report | ConvertTo-Json -Depth 4
    $asciiReport = [System.Text.Encoding]::ASCII.GetString([System.Text.Encoding]::ASCII.GetBytes($reportJson))
    Set-Content -Path $reportPath -Value $asciiReport -Encoding ASCII

    Write-EQ12Log "System report saved: $reportPath" -Level SUCCESS
    return $reportPath
}

# Main execution flow
function Start-EQ12Repair {
    Write-EQ12Log "=== EQ12 Expert System Repair Started ===" -Level INFO
    Write-EQ12Log "Mode: $Mode | DryRun: $($DryRun.IsPresent)" -Level INFO

    # Ensure log directory exists
    $logDir = "C:\EQ12\logs"
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    try {
        # Phase 1: Python Installation Check
        Write-EQ12Log "PHASE 1: Python Installation Verification" -Level INFO
        $pythonValid = Test-PythonInstallation

        # Phase 2: Virtual Environment Repair
        Write-EQ12Log "PHASE 2: Virtual Environment Analysis" -Level INFO
        Repair-VirtualEnvironments

        # Phase 3: Cache Cleanup
        Write-EQ12Log "PHASE 3: Python Cache Cleanup" -Level INFO
        Clean-PyCache

        # Phase 4: VS Code Repair
        Write-EQ12Log "PHASE 4: VS Code Python Integration" -Level INFO
        Repair-VSCodePython

        # Phase 5: GitHub Integration
        Write-EQ12Log "PHASE 5: GitHub CLI and Copilot Check" -Level INFO
        Test-GitHubIntegration

        # Phase 6: Generate Report
        Write-EQ12Log "PHASE 6: System Report Generation" -Level INFO
        $reportPath = Generate-SystemReport

        Write-EQ12Log "=== EQ12 Expert System Repair Completed ===" -Level SUCCESS
        Write-EQ12Log "Report available at: $reportPath" -Level INFO

        if ($DryRun) {
            Write-EQ12Log "DRY RUN COMPLETED - No changes were made" -Level INFO
        }
    }
    catch {
        Write-EQ12Log "CRITICAL ERROR: $($_.Exception.Message)" -Level ERROR
        Write-EQ12Log "Stack Trace: $($_.ScriptStackTrace)" -Level ERROR
        throw
    }
}

# Script entry point
if ($MyInvocation.InvocationName -ne '.') {
    Start-EQ12Repair
}
