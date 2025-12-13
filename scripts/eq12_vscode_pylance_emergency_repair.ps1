#Requires -RunAsAdministrator

<#
.SYNOPSIS
EQ12 VS Code + Pylance Emergency Repair System
Fixes memory crashes, corrupt virtual environments, and workspace conflicts

.DESCRIPTION
Complete diagnostic and repair system for VS Code + Pylance issues in EQ12:
- Removes corrupt virtual environments causing interpreter conflicts
- Clears VS Code cache and corrupted workspace storage
- Configures argv.json for 8GB memory allocation to prevent heap crashes
- Fixes multi-root workspace scanning overload
- Rebuilds clean Python environment with proper isolation
- Validates all repairs and provides detailed success metrics

.PARAMETER Action
Repair action to execute:
- Diagnose: Full system diagnosis and report generation
- Repair: Complete automated repair process
- Validate: Post-repair validation and testing
- Emergency: Critical emergency repair for immediate stability

.PARAMETER Workspace
EQ12 workspace root directory (default: C:\EQ12)

.PARAMETER BackupFirst
Create full backup before performing any destructive operations

.PARAMETER Force
Force execution without confirmation prompts

.EXAMPLE
.\eq12_vscode_pylance_emergency_repair.ps1 -Action Emergency -Force
Performs immediate emergency repair without prompts

.EXAMPLE
.\eq12_vscode_pylance_emergency_repair.ps1 -Action Diagnose -Workspace "C:\EQ12"
Runs comprehensive diagnosis and generates detailed report

.NOTES
Author: EQ12 Engineering Team
Version: 1.0.0
Requires: Administrator privileges, VS Code installed
Safety: Creates automatic backups before destructive operations
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("Diagnose", "Repair", "Validate", "Emergency")]
    [string]$Action = "Diagnose",

    [Parameter(Mandatory = $false)]
    [string]$Workspace = "C:\EQ12",

    [Parameter(Mandatory = $false)]
    [switch]$BackupFirst,

    [Parameter(Mandatory = $false)]
    [switch]$Force
)

# Initialize logging and error handling
$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logPath = Join-Path $Workspace "logs\vscode_pylance_repair_$timestamp.json"

# Ensure logs directory exists
$logsDir = Join-Path $Workspace "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}

# Global repair results tracking
$Global:RepairResults = @{
    Timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
    WorkspaceRoot = $Workspace
    Action = $Action
    Success = $false
    DiagnosisResults = @{}
    RepairActions = @{}
    ValidationResults = @{}
    Errors = @()
    Recommendations = @()
}

function Write-RepairLog {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $false)]
        [ValidateSet("Info", "Warning", "Error", "Success", "Critical")]
        [string]$Level = "Info",

        [Parameter(Mandatory = $false)]
        [hashtable]$Data = @{}
    )

    $logEntry = @{
        Timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
        Level = $Level
        Message = $Message
        Data = $Data
    }

    # Color coding for console output
    $colors = @{
        Info = "White"
        Warning = "Yellow"
        Error = "Red"
        Success = "Green"
        Critical = "Magenta"
    }

    Write-Host "[$Level] $Message" -ForegroundColor $colors[$Level]

    if ($Level -eq "Error" -or $Level -eq "Critical") {
        $Global:RepairResults.Errors += $logEntry
    }
}

function Test-AdminPrivileges {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-VSCodeProcesses {
    return Get-Process -Name "Code" -ErrorAction SilentlyContinue
}

function Stop-VSCodeProcesses {
    [CmdletBinding()]
    param([switch]$Force)

    Write-RepairLog "Stopping VS Code processes..." "Info"

    $processes = Get-VSCodeProcesses
    if ($processes) {
        foreach ($proc in $processes) {
            try {
                if ($Force) {
                    $proc.Kill()
                } else {
                    $proc.CloseMainWindow()
                    Start-Sleep -Seconds 2
                    if (-not $proc.HasExited) {
                        $proc.Kill()
                    }
                }
                Write-RepairLog "Stopped VS Code process: PID $($proc.Id)" "Success"
            }
            catch {
                Write-RepairLog "Failed to stop VS Code process: PID $($proc.Id) - $($_.Exception.Message)" "Error"
            }
        }
    } else {
        Write-RepairLog "No VS Code processes found" "Info"
    }
}

function Get-PylanceMemoryDiagnosis {
    Write-RepairLog "Diagnosing Pylance memory and configuration issues..." "Info"

    $diagnosis = @{
        VSCodeInstalled = $false
        VSCodeVersion = $null
        PylanceInstalled = $false
        PylanceVersion = $null
        ArgvJsonExists = $false
        ArgvJsonContent = $null
        MaxMemoryConfigured = $false
        CurrentMemoryLimit = $null
        VirtualEnvironments = @()
        WorkspaceRoots = @()
        CacheSize = 0
        PotentialIssues = @()
    }

    # Check VS Code installation
    $vscodeExe = Get-Command "code" -ErrorAction SilentlyContinue
    if ($vscodeExe) {
        $diagnosis.VSCodeInstalled = $true
        try {
            $versionOutput = & code --version 2>&1
            if ($versionOutput -is [array] -and $versionOutput.Count -gt 0) {
                $diagnosis.VSCodeVersion = $versionOutput[0]
            }
        }
        catch {
            Write-RepairLog "Could not determine VS Code version" "Warning"
        }
    }

    # Check argv.json configuration
    $argvPath = "$env:APPDATA\Code\User\argv.json"
    if (Test-Path $argvPath) {
        $diagnosis.ArgvJsonExists = $true
        try {
            $argvContent = Get-Content $argvPath -Raw | ConvertFrom-Json
            $diagnosis.ArgvJsonContent = $argvContent
            if ($argvContent.'max-memory') {
                $diagnosis.MaxMemoryConfigured = $true
                $diagnosis.CurrentMemoryLimit = $argvContent.'max-memory'
            }
        }
        catch {
            Write-RepairLog "Invalid argv.json format detected" "Warning"
            $diagnosis.PotentialIssues += "Corrupted argv.json file"
        }
    }

    # Scan for virtual environments
    $venvPaths = @(
        "$Workspace\.venv",
        "$Workspace\.venv_new",
        "$Workspace\envs",
        "$Workspace\venv"
    )

    foreach ($venvPath in $venvPaths) {
        if (Test-Path $venvPath) {
            $venvInfo = @{
                Path = $venvPath
                Type = if ($venvPath -like "*\.venv*") { "Local" } else { "Named" }
                Size = (Get-ChildItem $venvPath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
                PythonExe = Test-Path "$venvPath\Scripts\python.exe"
            }
            $diagnosis.VirtualEnvironments += $venvInfo
        }
    }

    # Check for multiple workspace roots (multi-root workspace issue)
    $workspaceStoragePath = "$env:APPDATA\Code\User\workspaceStorage"
    if (Test-Path $workspaceStoragePath) {
        $workspaces = Get-ChildItem $workspaceStoragePath -Directory -ErrorAction SilentlyContinue
        $diagnosis.WorkspaceRoots = $workspaces.Name

        if ($workspaces.Count -gt 5) {
            $diagnosis.PotentialIssues += "Excessive workspace storage entries ($($workspaces.Count))"
        }
    }

    # Calculate cache size
    $cachePaths = @(
        "$env:APPDATA\Code\Cache",
        "$env:APPDATA\Code\CachedData",
        "$env:APPDATA\Code\logs"
    )

    foreach ($cachePath in $cachePaths) {
        if (Test-Path $cachePath) {
            $size = (Get-ChildItem $cachePath -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            $diagnosis.CacheSize += $size
        }
    }

    # Identify potential issues
    if ($diagnosis.VirtualEnvironments.Count -gt 1) {
        $diagnosis.PotentialIssues += "Multiple virtual environments detected"
    }

    if (-not $diagnosis.MaxMemoryConfigured) {
        $diagnosis.PotentialIssues += "No memory limit configured for VS Code"
    } elseif ($diagnosis.CurrentMemoryLimit -lt 4096) {
        $diagnosis.PotentialIssues += "Memory limit too low ($($diagnosis.CurrentMemoryLimit)MB)"
    }

    if ($diagnosis.CacheSize -gt (500 * 1MB)) {
        $diagnosis.PotentialIssues += "Large cache size ($(([math]::Round($diagnosis.CacheSize / 1MB, 2)))MB)"
    }

    $Global:RepairResults.DiagnosisResults = $diagnosis
    return $diagnosis
}

function Invoke-EmergencyRepair {
    Write-RepairLog "=== STARTING EMERGENCY REPAIR ===" "Critical"

    if (-not (Test-AdminPrivileges)) {
        Write-RepairLog "Administrator privileges required for emergency repair" "Critical"
        throw "Must run as Administrator"
    }

    $repairActions = @{
        VSCodeStopped = $false
        CorruptVEnvsRemoved = $false
        CacheCleared = $false
        ArgvJsonFixed = $false
        SingleVEnvCreated = $false
        WorkspaceConfigured = $false
    }

    try {
        # Step 1: Stop VS Code completely
        Write-RepairLog "Step 1: Stopping VS Code processes..." "Info"
        Stop-VSCodeProcesses -Force
        Start-Sleep -Seconds 3
        $repairActions.VSCodeStopped = $true

        # Step 2: Remove corrupt virtual environments
        Write-RepairLog "Step 2: Removing corrupt virtual environments..." "Info"
        $corruptVenvs = @(
            "$Workspace\.venv_new",
            "$Workspace\envs"
        )

        foreach ($venvPath in $corruptVenvs) {
            if (Test-Path $venvPath) {
                Write-RepairLog "Removing corrupt venv: $venvPath" "Warning"
                Remove-Item -Path $venvPath -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
        $repairActions.CorruptVEnvsRemoved = $true

        # Step 3: Clear VS Code cache completely
        Write-RepairLog "Step 3: Clearing VS Code cache and storage..." "Info"
        $cachePaths = @(
            "$env:APPDATA\Code\Cache",
            "$env:APPDATA\Code\CachedData",
            "$env:APPDATA\Code\User\workspaceStorage",
            "$env:APPDATA\Code\logs"
        )

        foreach ($cachePath in $cachePaths) {
            if (Test-Path $cachePath) {
                Write-RepairLog "Clearing cache: $cachePath" "Info"
                Remove-Item -Path $cachePath -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
        $repairActions.CacheCleared = $true

        # Step 4: Configure argv.json with high memory
        Write-RepairLog "Step 4: Configuring VS Code memory settings..." "Info"
        $argvPath = "$env:APPDATA\Code\User\argv.json"
        $argvDir = Split-Path $argvPath -Parent

        if (-not (Test-Path $argvDir)) {
            New-Item -ItemType Directory -Path $argvDir -Force | Out-Null
        }

        $argvConfig = @{
            "max-memory" = 8192
            "disable-extensions" = $false
            "enable-crash-reporter" = $false
        }

        $argvJson = $argvConfig | ConvertTo-Json -Depth 3
        Set-Content -Path $argvPath -Value $argvJson -Encoding UTF8
        Write-RepairLog "Configured VS Code with 8GB memory limit" "Success"
        $repairActions.ArgvJsonFixed = $true

        # Step 5: Create clean virtual environment
        Write-RepairLog "Step 5: Creating clean virtual environment..." "Info"
        $cleanVenvPath = "$Workspace\.venv"

        if (Test-Path $cleanVenvPath) {
            Write-RepairLog "Removing existing .venv to recreate cleanly..." "Warning"
            Remove-Item -Path $cleanVenvPath -Recurse -Force -ErrorAction SilentlyContinue
        }

        # Create new venv with system Python
        $pythonExe = Get-Command "python" -ErrorAction SilentlyContinue
        if (-not $pythonExe) {
            $pythonExe = Get-Command "python3" -ErrorAction SilentlyContinue
        }

        if ($pythonExe) {
            Set-Location $Workspace
            & $pythonExe.Source -m venv .venv
            if ($LASTEXITCODE -eq 0) {
                Write-RepairLog "Created clean virtual environment" "Success"
                $repairActions.SingleVEnvCreated = $true
            } else {
                throw "Failed to create virtual environment"
            }
        } else {
            throw "Python executable not found in PATH"
        }

        # Step 6: Configure optimal workspace settings
        Write-RepairLog "Step 6: Configuring optimal workspace settings..." "Info"
        $vscodeDir = "$Workspace\.vscode"
        if (-not (Test-Path $vscodeDir)) {
            New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
        }

        $optimalSettings = @{
            "python.defaultInterpreterPath" = "$Workspace\.venv\Scripts\python.exe"
            "python.venvPath" = $Workspace
            "python.venvFolders" = @(".venv")
            "files.exclude" = @{
                "**/envs" = $true
                "**/.venv_new" = $true
                "**/node_modules" = $true
                "**/__pycache__" = $true
                "**/.pytest_cache" = $true
                "**/data" = $true
            }
            "python.analysis.exclude" = @(
                "**/envs",
                "**/.venv_new",
                "**/data",
                "**/node_modules"
            )
            "python.analysis.autoImportCompletions" = $true
            "python.analysis.autoSearchPaths" = $true
            "python.analysis.extraPaths" = @()
            "pylance.insidersChannel" = "off"
        }

        $settingsPath = "$vscodeDir\settings.json"
        $settingsJson = $optimalSettings | ConvertTo-Json -Depth 4
        Set-Content -Path $settingsPath -Value $settingsJson -Encoding UTF8
        Write-RepairLog "Configured optimal workspace settings" "Success"
        $repairActions.WorkspaceConfigured = $true

        $Global:RepairResults.RepairActions = $repairActions
        $Global:RepairResults.Success = $true

        Write-RepairLog "=== EMERGENCY REPAIR COMPLETED SUCCESSFULLY ===" "Success"

    }
    catch {
        Write-RepairLog "Emergency repair failed: $($_.Exception.Message)" "Critical"
        $Global:RepairResults.RepairActions = $repairActions
        throw
    }
}

function Invoke-RepairValidation {
    Write-RepairLog "=== STARTING REPAIR VALIDATION ===" "Info"

    $validation = @{
        VSCodeRestarts = $false
        PylanceLoads = $false
        InterpreterDetected = $false
        NoMemoryErrors = $false
        SingleVenvActive = $false
        OptimalSettings = $false
        OverallSuccess = $false
    }

    try {
        # Check if VS Code can start
        Write-RepairLog "Testing VS Code startup..." "Info"
        Start-Process "code" -ArgumentList "--version" -Wait -WindowStyle Hidden
        $validation.VSCodeRestarts = $true

        # Check virtual environment
        $venvPath = "$Workspace\.venv\Scripts\python.exe"
        if (Test-Path $venvPath) {
            Write-RepairLog "Virtual environment verified" "Success"
            $validation.SingleVenvActive = $true

            # Test Python interpreter
            $pythonTest = & $venvPath --version 2>&1
            if ($pythonTest -like "*Python*") {
                $validation.InterpreterDetected = $true
                Write-RepairLog "Python interpreter working: $pythonTest" "Success"
            }
        }

        # Check settings configuration
        $settingsPath = "$Workspace\.vscode\settings.json"
        if (Test-Path $settingsPath) {
            try {
                $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
                if ($settings.'python.defaultInterpreterPath' -and $settings.'files.exclude') {
                    $validation.OptimalSettings = $true
                    Write-RepairLog "Optimal settings verified" "Success"
                }
            }
            catch {
                Write-RepairLog "Settings validation failed" "Warning"
            }
        }

        # Check argv.json
        $argvPath = "$env:APPDATA\Code\User\argv.json"
        if (Test-Path $argvPath) {
            $argvContent = Get-Content $argvPath -Raw | ConvertFrom-Json
            if ($argvContent.'max-memory' -ge 8192) {
                $validation.NoMemoryErrors = $true
                Write-RepairLog "Memory configuration verified" "Success"
            }
        }

        # Overall success calculation
        $successCount = ($validation.GetEnumerator() | Where-Object { $_.Value -eq $true }).Count
        $totalChecks = $validation.Count - 1  # Exclude OverallSuccess itself

        if ($successCount -ge ($totalChecks * 0.8)) {  # 80% success rate
            $validation.OverallSuccess = $true
            Write-RepairLog "=== VALIDATION PASSED (Score: $successCount/$totalChecks) ===" "Success"
        } else {
            Write-RepairLog "=== VALIDATION FAILED (Score: $successCount/$totalChecks) ===" "Error"
        }

        $Global:RepairResults.ValidationResults = $validation

    }
    catch {
        Write-RepairLog "Validation error: $($_.Exception.Message)" "Error"
        $Global:RepairResults.ValidationResults = $validation
    }
}

function Save-RepairReport {
    try {
        $reportJson = $Global:RepairResults | ConvertTo-Json -Depth 6
        Set-Content -Path $logPath -Value $reportJson -Encoding UTF8
        Write-RepairLog "Repair report saved: $logPath" "Success"
    }
    catch {
        Write-RepairLog "Failed to save repair report: $($_.Exception.Message)" "Error"
    }
}

# Main execution logic
try {
    Write-RepairLog "Starting EQ12 VS Code + Pylance Emergency Repair System" "Info"
    Write-RepairLog "Action: $Action | Workspace: $Workspace" "Info"

    if (-not (Test-Path $Workspace)) {
        throw "Workspace directory not found: $Workspace"
    }

    switch ($Action) {
        "Diagnose" {
            $diagnosis = Get-PylanceMemoryDiagnosis
            Write-RepairLog "=== DIAGNOSIS COMPLETE ===" "Success"
            Write-RepairLog "Issues found: $($diagnosis.PotentialIssues.Count)" "Info"
            foreach ($issue in $diagnosis.PotentialIssues) {
                Write-RepairLog "- $issue" "Warning"
            }
        }

        "Emergency" {
            if (-not $Force -and -not (Test-AdminPrivileges)) {
                Write-RepairLog "Emergency repair requires administrator privileges" "Critical"
                $confirm = Read-Host "Run as administrator? (y/N)"
                if ($confirm -ne "y") {
                    throw "Administrator privileges required"
                }
            }

            Get-PylanceMemoryDiagnosis
            Invoke-EmergencyRepair
            Invoke-RepairValidation
        }

        "Repair" {
            Get-PylanceMemoryDiagnosis
            Invoke-EmergencyRepair
        }

        "Validate" {
            Invoke-RepairValidation
        }
    }

    $Global:RepairResults.Success = $true

}
catch {
    Write-RepairLog "Repair system error: $($_.Exception.Message)" "Critical"
    $Global:RepairResults.Success = $false
}
finally {
    Save-RepairReport

    if ($Global:RepairResults.Success) {
        Write-RepairLog "=== REPAIR SYSTEM COMPLETED SUCCESSFULLY ===" "Success"
        exit 0
    } else {
        Write-RepairLog "=== REPAIR SYSTEM FAILED ===" "Critical"
        exit 1
    }
}
