# ================================
# EQ12 SAFE MODE  NO MORE BREAKS
# ================================
Set-StrictMode -Version Latest
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
[System.Console]::InputEncoding = [System.Text.Encoding]::UTF8
[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Prevent accidental truncation or malformed scripts
$ErrorActionPreference = "Stop"

#region EQ12_SELF_HEALING_V5_WRAPPER_HARDENED
# EQ12 Self-Healing v5.0 PowerShell Wrapper - HARDENED BULLETPROOF VERSION
# Proper UTF-8 encoding for PowerShell  Python  JSON integration
# Buffalo NY 14215 Content Empire Protection
# VERSION: 2.0 - CORRUPTION-PROOF EDITION

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [ValidateSet("monitor", "heal", "test", "status")]
    [string]$Action = "monitor",

    [Parameter()]
    [ValidateScript({Test-Path $_ -PathType Container})]
    [string]$Workspace = "C:\EQ12",

    [Parameter()]
    [switch]$Continuous,

    [Parameter()]
    [switch]$EmergencyMode,

    [Parameter()]
    [string]$AlertsJson,

    [Parameter()]
    [switch]$Verbose,

    [Parameter()]
    [int]$Interval = 300  # 5 minutes default
)

function Initialize-UTF8Environment {
    [CmdletBinding()]
    param()

    # Force all encoding to UTF-8
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONUTF8 = "1"
    $env:LC_ALL = "C.UTF-8"
    $env:LANG = "C.UTF-8"

    # Additional PowerShell UTF-8 enforcement
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
    $PSDefaultParameterValues['*:Encoding'] = 'utf8'
    $PSDefaultParameterValues['ConvertTo-Json:Depth'] = 10
}

function Write-EQ12Header {
    [CmdletBinding()]
    param()

    Write-Host ""
    Write-Host " EQ12 SELF-HEALING v5.0 PowerShell Wrapper - HARDENED" -ForegroundColor Cyan
    Write-Host " Buffalo NY 14215 Content Empire Protection" -ForegroundColor Yellow
    Write-Host " CORRUPTION-PROOF BULLETPROOF EDITION" -ForegroundColor Green
    Write-Host ("=" * 60)
}

function Test-PythonScript {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ScriptPath
    )

    if (-not (Test-Path $ScriptPath -PathType Leaf)) {
        Write-Host " EQ12 Self-Healing v5.0 script not found: $ScriptPath" -ForegroundColor Red
        Write-Host " Expected path: $ScriptPath" -ForegroundColor Gray

        # Check alternative locations
        $AlternativeLocations = @(
            Join-Path $Workspace "eq12_self_healing_v5.py"
            "C:\EQ12\eq12_self_healing_v5.py"
            "C:\EQ12\scripts\eq12_self_healing_v5.py"
        )

        Write-Host " Checking alternative locations..." -ForegroundColor Yellow
        foreach ($AltPath in $AlternativeLocations) {
            if (Test-Path $AltPath -PathType Leaf) {
                Write-Host " Found at: $AltPath" -ForegroundColor Green
                return $AltPath
            } else {
                Write-Host " Not found: $AltPath" -ForegroundColor Red
            }
        }

        return $null
    }

    return $ScriptPath
}

function ConvertTo-SafeJsonString {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [object]$InputObject
    )

    try {
        # Convert to JSON with proper depth and compression
        $JsonString = $InputObject | ConvertTo-Json -Depth 10 -Compress

        # Escape for command line safety
        $SafeJson = $JsonString -replace '"', '\"'

        return $SafeJson
    }
    catch {
        Write-Host " JSON conversion error: $($_.Exception.Message)" -ForegroundColor Yellow
        return '[]'  # Return empty array as fallback
    }
}

function New-TestAlerts {
    [CmdletBinding()]
    param()

    $CurrentTime = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffK"

    return @(
        @{
            type = "cpu_overload"
            severity = "critical"
            message = "CPU usage critical: 95.2%"
            value = 95.2
            threshold = 90.0
            timestamp = $CurrentTime
            source = "PowerShell_Wrapper_Test"
        },
        @{
            type = "memory_overload"
            severity = "high"
            message = "Memory usage high: 87.5%"
            value = 87.5
            threshold = 85.0
            timestamp = $CurrentTime
            source = "PowerShell_Wrapper_Test"
        },
        @{
            type = "disk_space_low"
            severity = "warning"
            message = "Disk space running low: 78.3%"
            value = 78.3
            threshold = 80.0
            timestamp = $CurrentTime
            source = "PowerShell_Wrapper_Test"
        }
    )
}

function New-DefaultTestAlert {
    [CmdletBinding()]
    param()

    $CurrentTime = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffK"

    return @(
        @{
            type = "system_check"
            severity = "info"
            message = "PowerShell wrapper connection test"
            timestamp = $CurrentTime
            source = "eq12_self_healing_v5_wrapper"
            version = "2.0-hardened"
        }
    )
}

function Build-PythonArguments {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Action,

        [Parameter(Mandatory)]
        [string]$Workspace,

        [Parameter()]
        [string]$AlertsJson,

        [Parameter()]
        [bool]$Continuous,

        [Parameter()]
        [bool]$EmergencyMode,

        [Parameter()]
        [bool]$VerboseMode,

        [Parameter()]
        [int]$IntervalSeconds
    )

    $PythonArgs = @()

    switch ($Action.ToLower()) {
        "monitor" {
            $PythonArgs += "monitor"
            $PythonArgs += "--workspace"
            $PythonArgs += $Workspace

            if ($Continuous) {
                $PythonArgs += "--continuous"
                $PythonArgs += "--interval"
                $PythonArgs += $IntervalSeconds.ToString()
            }

            Write-Host " Starting resource monitoring..." -ForegroundColor Green
        }

        "heal" {
            $PythonArgs += "heal"
            $PythonArgs += "--workspace"
            $PythonArgs += $Workspace

            if ([string]::IsNullOrWhiteSpace($AlertsJson)) {
                $DefaultAlert = New-DefaultTestAlert
                $AlertsJson = ConvertTo-SafeJsonString -InputObject $DefaultAlert
            }

            $PythonArgs += "--alerts"
            $PythonArgs += $AlertsJson

            if ($EmergencyMode) {
                $PythonArgs += "--emergency-mode"
            }

            Write-Host " Starting emergency healing..." -ForegroundColor Yellow
        }

        "test" {
            $PythonArgs += "heal"
            $PythonArgs += "--workspace"
            $PythonArgs += $Workspace

            $TestAlerts = New-TestAlerts
            $TestAlertsJson = ConvertTo-SafeJsonString -InputObject $TestAlerts

            $PythonArgs += "--alerts"
            $PythonArgs += $TestAlertsJson
            $PythonArgs += "--emergency-mode"

            Write-Host " Running test healing scenario..." -ForegroundColor Magenta
        }

        "status" {
            $PythonArgs += "status"
            $PythonArgs += "--workspace"
            $PythonArgs += $Workspace

            Write-Host " Checking system status..." -ForegroundColor Blue
        }

        default {
            throw "Invalid action: $Action. Valid actions: monitor, heal, test, status"
        }
    }

    # Add verbose flag if requested
    if ($VerboseMode) {
        $PythonArgs += "--verbose"
    }

    return $PythonArgs
}

function Invoke-PythonScript {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ScriptPath,

        [Parameter(Mandatory)]
        [array]$Arguments
    )

    Write-Host " Executing Python command with UTF-8 encoding..." -ForegroundColor Green
    Write-Host "Script: $ScriptPath" -ForegroundColor Gray
    Write-Host "Arguments: $($Arguments -join ' ')" -ForegroundColor Gray

    try {
        # Use Start-Process for better control and UTF-8 handling
        $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
        $ProcessInfo.FileName = "python"
        $ProcessInfo.Arguments = "`"$ScriptPath`" " + ($Arguments -join ' ')
        $ProcessInfo.UseShellExecute = $false
        $ProcessInfo.RedirectStandardOutput = $true
        $ProcessInfo.RedirectStandardError = $true
        $ProcessInfo.StandardOutputEncoding = [System.Text.Encoding]::UTF8
        $ProcessInfo.StandardErrorEncoding = [System.Text.Encoding]::UTF8
        $ProcessInfo.CreateNoWindow = $false

        # Set environment variables for UTF-8
        $ProcessInfo.EnvironmentVariables["PYTHONIOENCODING"] = "utf-8"
        $ProcessInfo.EnvironmentVariables["PYTHONUTF8"] = "1"
        $ProcessInfo.EnvironmentVariables["LC_ALL"] = "C.UTF-8"
        $ProcessInfo.EnvironmentVariables["LANG"] = "C.UTF-8"

        $Process = [System.Diagnostics.Process]::Start($ProcessInfo)

        # Read output
        $StandardOutput = $Process.StandardOutput.ReadToEnd()
        $StandardError = $Process.StandardError.ReadToEnd()

        $Process.WaitForExit()
        $ExitCode = $Process.ExitCode

        # Display output
        if (-not [string]::IsNullOrWhiteSpace($StandardOutput)) {
            Write-Host $StandardOutput
        }

        if (-not [string]::IsNullOrWhiteSpace($StandardError)) {
            Write-Host $StandardError -ForegroundColor Yellow
        }

        Write-Host ""

        if ($ExitCode -eq 0) {
            Write-Host " EQ12 Self-Healing v5.0 completed successfully" -ForegroundColor Green
        } elseif ($ExitCode -eq 2) {
            Write-Host " EQ12 Self-Healing v5.0 completed with warnings" -ForegroundColor Yellow
        } else {
            Write-Host " EQ12 Self-Healing v5.0 failed" -ForegroundColor Red
        }

        Write-Host " Exit code: $ExitCode" -ForegroundColor Gray

        return $ExitCode
    }
    catch {
        Write-Host ""
        Write-Host " EQ12 Self-Healing v5.0 execution failed" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Stack: $($_.ScriptStackTrace)" -ForegroundColor Gray
        return 1
    }
}

function Show-UsageInformation {
    [CmdletBinding()]
    param()

    Write-Host ""
    Write-Host " EQ12 Self-Healing v5.0 Wrapper Usage:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Monitor mode:" -ForegroundColor White
    Write-Host "  .\eq12_self_healing_v5_wrapper_v2.ps1 -Action monitor" -ForegroundColor Gray
    Write-Host "  .\eq12_self_healing_v5_wrapper_v2.ps1 -Action monitor -Continuous" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Healing mode:" -ForegroundColor White
    Write-Host "  .\eq12_self_healing_v5_wrapper_v2.ps1 -Action heal" -ForegroundColor Gray
    Write-Host "  .\eq12_self_healing_v5_wrapper_v2.ps1 -Action heal -EmergencyMode" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Test mode:" -ForegroundColor White
    Write-Host "  .\eq12_self_healing_v5_wrapper_v2.ps1 -Action test" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Status check:" -ForegroundColor White
    Write-Host "  .\eq12_self_healing_v5_wrapper_v2.ps1 -Action status" -ForegroundColor Gray
    Write-Host ""
    Write-Host " Buffalo NY 14215 Content Empire: PROTECTED" -ForegroundColor Green
}

function Save-ExecutionLog {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Action,

        [Parameter(Mandatory)]
        [int]$ExitCode,

        [Parameter(Mandatory)]
        [array]$Arguments
    )

    try {
        $LogEntry = [PSCustomObject]@{
            timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffK"
            wrapper_version = "2.0-hardened"
            action = $Action
            exit_code = $ExitCode
            arguments = $Arguments
            workspace = $Workspace
            success = ($ExitCode -eq 0)
            buffalo_ny_14215 = $true
        }

        # Ensure logs directory exists
        $LogsDir = Join-Path $Workspace "logs"
        if (-not (Test-Path $LogsDir)) {
            New-Item -Path $LogsDir -ItemType Directory -Force | Out-Null
        }

        $LogPath = Join-Path $LogsDir "self_healing_wrapper_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

        $LogEntry | ConvertTo-Json -Depth 10 |
            Out-File -FilePath $LogPath -Encoding UTF8 -Force

        Write-Host " Execution log saved: $LogPath" -ForegroundColor Gray
    }
    catch {
        Write-Host " Could not save execution log: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Main execution logic
try {
    # Initialize environment
    Initialize-UTF8Environment

    # Display header
    Write-EQ12Header

    # Validate Python script exists
    $PythonScript = Join-Path $Workspace "scripts\eq12_self_healing_v5.py"
    $ValidatedScript = Test-PythonScript -ScriptPath $PythonScript

    if ($null -eq $ValidatedScript) {
        Write-Host ""
        Write-Host " Cannot continue: Python script not found" -ForegroundColor Red
        Show-UsageInformation
        exit 1
    }

    Write-Host " Python script validated: $ValidatedScript" -ForegroundColor Green

    # Build Python arguments
    $PythonArgs = Build-PythonArguments -Action $Action -Workspace $Workspace -AlertsJson $AlertsJson -Continuous $Continuous.IsPresent -EmergencyMode $EmergencyMode.IsPresent -VerboseMode $Verbose.IsPresent -IntervalSeconds $Interval

    # Execute Python script
    $ExitCode = Invoke-PythonScript -ScriptPath $ValidatedScript -Arguments $PythonArgs

    # Save execution log
    Save-ExecutionLog -Action $Action -ExitCode $ExitCode -Arguments $PythonArgs

    # Show usage information
    Show-UsageInformation

    # Exit with the same code as Python script
    exit $ExitCode
}
catch {
    Write-Host ""
    Write-Host " CRITICAL ERROR IN WRAPPER:" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack: $($_.ScriptStackTrace)" -ForegroundColor Gray

    Show-UsageInformation

    exit 1
}

#endregion EQ12_SELF_HEALING_V5_WRAPPER_HARDENED

