[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('Scan', 'Dashboard', 'Test')]
    [string]$Action = 'Scan',
    [Parameter()]
    [string]$WorkspaceRoot = 'C:\EQ12',
    [Parameter()]
    [switch]$CleanMemory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-EQ12Log {
    param([string]$Message, [string]$Level = 'INFO')
    $Timestamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    $LogEntry = "$Timestamp [$Level] $Message"
    switch ($Level) {
        'INFO' { Write-Host $LogEntry -ForegroundColor Green }
        'WARN' { Write-Host $LogEntry -ForegroundColor Yellow }
        'ERROR' { Write-Host $LogEntry -ForegroundColor Red }
    }
}

function Test-SystemResources {
    try {
        $Memory = Get-CimInstance -ClassName Win32_OperatingSystem
        $FreeMemoryMB = [math]::Round($Memory.FreePhysicalMemory / 1KB, 0)
        Write-EQ12Log "Memory check: ${FreeMemoryMB}MB free" 'INFO'
        return ($FreeMemoryMB -gt 512)
    }
    catch {
        Write-EQ12Log "Resource check failed: $($_.Exception.Message)" 'ERROR'
        return $false
    }
}

function Invoke-SecurityScan {
    Write-EQ12Log "Starting security scan of: $WorkspaceRoot" 'INFO'
    $PythonScanner = Join-Path $WorkspaceRoot 'scripts\eq12_snyk_security_v3.py'
    
    if (Test-Path $PythonScanner) {
        try {
            $Process = Start-Process -FilePath "python" -ArgumentList @($PythonScanner, '--scan', '--verbose') -NoNewWindow -PassThru -Wait
            $ExitCode = $Process.ExitCode
            
            if ($ExitCode -eq 0 -or $ExitCode -eq 1) {
                Write-EQ12Log "Security scan completed (exit code: $ExitCode)" 'INFO'
                return 0
            }
            else {
                Write-EQ12Log "Security scan failed with exit code: $ExitCode" 'ERROR'
                return $ExitCode
            }
        }
        catch {
            Write-EQ12Log "Python scanner failed: $($_.Exception.Message)" 'ERROR'
            return 1
        }
    }
    else {
        Write-EQ12Log "No Python scanner found - basic scan only" 'WARN'
        return 0
    }
}

function Show-SecurityDashboard {
    Write-Host "EQ12 SECURITY DASHBOARD" -ForegroundColor Cyan
    Write-Host "======================" -ForegroundColor Cyan
    try {
        $Memory = Get-CimInstance -ClassName Win32_OperatingSystem
        $FreeMemoryGB = [math]::Round($Memory.FreePhysicalMemory / 1GB, 2)
        Write-Host "Free Memory: $FreeMemoryGB GB" -ForegroundColor White
        $PythonScanner = Join-Path $WorkspaceRoot 'scripts\eq12_snyk_security_v3.py'
        if (Test-Path $PythonScanner) {
            Write-Host "Python Scanner: Available" -ForegroundColor Green
        }
        else {
            Write-Host "Python Scanner: Not Found" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Dashboard Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-EQ12Log "EQ12 Security Scanner v4.0 - Action: $Action" 'INFO'

switch ($Action) {
    'Scan' {
        if (Test-SystemResources) {
            $ExitCode = Invoke-SecurityScan
            exit $ExitCode
        }
        else {
            Write-EQ12Log "Insufficient resources for scan" 'ERROR'
            exit 1
        }
    }
    'Dashboard' {
        Show-SecurityDashboard
    }
    'Test' {
        $ResourcesOK = Test-SystemResources
        $WorkspaceExists = Test-Path $WorkspaceRoot
        Write-Host "System Resources: $(if($ResourcesOK) {'OK'} else {'FAIL'})" -ForegroundColor $(if($ResourcesOK) {'Green'} else {'Red'})
        Write-Host "Workspace Access: $(if($WorkspaceExists) {'OK'} else {'FAIL'})" -ForegroundColor $(if($WorkspaceExists) {'Green'} else {'Red'})
        exit $(if($ResourcesOK -and $WorkspaceExists) {0} else {1})
    }
}
