[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

[CmdletBinding()]
param(
    [Parameter(HelpMessage="Run comprehensive security scan")]
    [switch]$Scan,
    
    [Parameter(HelpMessage="Clean memory before scan")]
    [switch]$CleanMemory,
    
    [Parameter(HelpMessage="Show security dashboard")]
    [switch]$Dashboard,
    
    [Parameter(HelpMessage="Enable verbose logging")]
    [switch]$Verbose
)

# EQ12 Security Scanner v3.0 PowerShell Wrapper
# Clean, stable, memory-safe wrapper for Python security scanner

Write-Host " EQ12 Security Scanner v3.0" -ForegroundColor Cyan
Write-Host "Memory-safe security scanning with resource limits" -ForegroundColor Gray

# Configuration
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptRoot
$PythonScript = Join-Path $ScriptRoot "eq12_snyk_security_v3.py"
$LogsDir = Join-Path $ProjectRoot "logs"

# Ensure directories exist
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}

# Lock file management
$LockFile = Join-Path $LogsDir "eq12_security_wrapper.lock"

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    
    $LogFile = Join-Path $LogsDir "security_wrapper.log"
    Add-Content -Path $LogFile -Value $LogEntry -ErrorAction SilentlyContinue
    
    switch ($Level) {
        "ERROR" { Write-Error $Message }
        "WARN" { Write-Warning $Message }
        "INFO" { Write-Host $Message -ForegroundColor Green }
        "DEBUG" { if ($Verbose) { Write-Host $Message -ForegroundColor Gray } }
    }
}

function Test-SystemResources {
    """Check if system has sufficient resources"""
    try {
        # Check available RAM
        $Memory = Get-CimInstance -ClassName Win32_OperatingSystem
        $FreeMemoryGB = [math]::Round($Memory.FreePhysicalMemory / 1GB, 2)
        
        if ($FreeMemoryGB -lt 2) {
            Write-EQ12Log "Low memory warning: ${FreeMemoryGB}GB free" "WARN"
            return $false
        }
        
        # Check CPU load (simplified)
        $CPU = Get-CimInstance -ClassName Win32_Processor | 
               Measure-Object -Property LoadPercentage -Average
        
        if ($CPU.Average -gt 80) {
            Write-EQ12Log "High CPU load warning: $($CPU.Average)%" "WARN"
        }
        
        Write-EQ12Log "System resources OK: ${FreeMemoryGB}GB RAM, $($CPU.Average)% CPU" "INFO"
        return $true
    }
    catch {
        Write-EQ12Log "Resource check failed: $_" "WARN"
        return $true  # Proceed anyway
    }
}

function Stop-MemoryHogs {
    """Terminate processes consuming excessive memory"""
    try {
        Write-EQ12Log "Cleaning memory hogs..." "INFO"
        
        $HeavyProcesses = Get-Process | Where-Object {
            $_.WorkingSet -gt 2GB -and 
            $_.ProcessName -like "*docker*" -or 
            $_.ProcessName -like "*wsl*"
        }
        
        foreach ($proc in $HeavyProcesses) {
            $MemoryGB = [math]::Round($proc.WorkingSet / 1GB, 2)
            Write-EQ12Log "Stopping heavy process: $($proc.ProcessName) (${MemoryGB}GB)" "WARN"
            try {
                $proc.Kill()
                Start-Sleep -Seconds 2
            }
            catch {
                Write-EQ12Log "Failed to stop $($proc.ProcessName): $_" "WARN"
            }
        }
    }
    catch {
        Write-EQ12Log "Memory cleanup failed: $_" "ERROR"
    }
}

function Test-PythonEnvironment {
    """Verify Python and required packages"""
    try {
        # Test Python availability
        $PythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-EQ12Log "Python not found in PATH" "ERROR"
            return $false
        }
        
        Write-EQ12Log "Python available: $PythonVersion" "DEBUG"
        
        # Test required packages
        $RequiredPackages = @("psutil")
        foreach ($package in $RequiredPackages) {
            python -c "import $package" 2>$null
            if ($LASTEXITCODE -ne 0) {
                Write-EQ12Log "Installing required package: $package" "INFO"
                pip install $package --quiet
                if ($LASTEXITCODE -ne 0) {
                    Write-EQ12Log "Failed to install $package" "ERROR"
                    return $false
                }
            }
        }
        
        return $true
    }
    catch {
        Write-EQ12Log "Python environment check failed: $_" "ERROR"
        return $false
    }
}

function Invoke-SecurityScan {
    """Execute the Python security scanner"""
    param([string[]]$Arguments)
    
    try {
        Write-EQ12Log "Starting Python security scanner..." "INFO"
        
        # Build Python command
        $PythonArgs = @($PythonScript) + $Arguments
        
        if ($Verbose) {
            $PythonArgs += "--verbose"
        }
        
        Write-EQ12Log "Executing: python $($PythonArgs -join ' ')" "DEBUG"
        
        # Execute with timeout
        $Process = Start-Process -FilePath "python" -ArgumentList $PythonArgs `
                                -NoNewWindow -PassThru -Wait
        
        $ExitCode = $Process.ExitCode
        Write-EQ12Log "Scanner completed with exit code: $ExitCode" "INFO"
        
        return $ExitCode
    }
    catch {
        Write-EQ12Log "Scanner execution failed: $_" "ERROR"
        return 1
    }
}

function Show-SecurityDashboard {
    """Display security status dashboard"""
    Write-Host "`n" + "="*70 -ForegroundColor Cyan
    Write-Host " EQ12 SECURITY DASHBOARD v3.0" -ForegroundColor Cyan
    Write-Host "="*70 -ForegroundColor Cyan
    
    # System status
    Write-Host "`n  SYSTEM STATUS:" -ForegroundColor Yellow
    $Memory = Get-CimInstance -ClassName Win32_OperatingSystem
    $FreeMemoryGB = [math]::Round($Memory.FreePhysicalMemory / 1GB, 2)
    $TotalMemoryGB = [math]::Round($Memory.TotalVisibleMemorySize / 1GB, 2)
    
    Write-Host "   Memory: ${FreeMemoryGB}GB free / ${TotalMemoryGB}GB total" -ForegroundColor Gray
    
    if (Test-Path $LockFile) {
        Write-Host "   Scanner Status: Running" -ForegroundColor Yellow
    } else {
        Write-Host "   Scanner Status: Idle" -ForegroundColor Green
    }
    
    # Recent reports
    Write-Host "`n RECENT SCAN RESULTS:" -ForegroundColor Yellow
    $RecentReports = Get-ChildItem -Path $LogsDir -Filter "security_report_*.json" -ErrorAction SilentlyContinue |
                    Sort-Object LastWriteTime -Descending | Select-Object -First 3
    
    if ($RecentReports) {
        foreach ($Report in $RecentReports) {
            $ReportTime = $Report.LastWriteTime.ToString("yyyy-MM-dd HH:mm")
            Write-Host "    $ReportTime - $($Report.Name)" -ForegroundColor Gray
        }
    } else {
        Write-Host "   No recent scan reports found" -ForegroundColor Gray
    }
    
    # Memory hogs
    Write-Host "`n HIGH MEMORY PROCESSES:" -ForegroundColor Yellow
    $MemoryHogs = Get-Process | Where-Object { $_.WorkingSet -gt 500MB } |
                 Sort-Object WorkingSet -Descending | Select-Object -First 5
    
    foreach ($proc in $MemoryHogs) {
        $MemoryMB = [math]::Round($proc.WorkingSet / 1MB, 0)
        Write-Host "   $($proc.ProcessName): ${MemoryMB}MB" -ForegroundColor Gray
    }
    
    Write-Host "`n" + "="*70 -ForegroundColor Cyan
}

# Main execution
try {
    Write-EQ12Log "EQ12 Security Scanner v3.0 started" "INFO"
    
    # Check for existing lock
    if (Test-Path $LockFile) {
        $LockContent = Get-Content $LockFile -ErrorAction SilentlyContinue
        Write-EQ12Log "Another scanner may be running (lock found)" "WARN"
        Write-Host "Use -Dashboard to check status or remove lock file manually" -ForegroundColor Yellow
        exit 1
    }
    
    # Create lock
    $PID | Out-File -FilePath $LockFile -Force
    
    try {
        if ($Dashboard) {
            Show-SecurityDashboard
            exit 0
        }
        
        # System resource check
        if (-not (Test-SystemResources)) {
            Write-Host "  System resources may be insufficient" -ForegroundColor Yellow
        }
        
        # Clean memory if requested
        if ($CleanMemory) {
            Stop-MemoryHogs
            Start-Sleep -Seconds 5  # Let system stabilize
        }
        
        # Check Python environment
        if (-not (Test-PythonEnvironment)) {
            Write-Host " Python environment not ready" -ForegroundColor Red
            exit 1
        }
        
        if ($Scan) {
            Write-Host " Starting comprehensive security scan..." -ForegroundColor Cyan
            
            $ScanArgs = @("--scan")
            if ($CleanMemory) {
                $ScanArgs += "--clean-memory"
            }
            
            $ExitCode = Invoke-SecurityScan -Arguments $ScanArgs
            
            if ($ExitCode -eq 0) {
                Write-Host " Security scan completed successfully" -ForegroundColor Green
            } elseif ($ExitCode -eq 1) {
                Write-Host "  Security scan completed with warnings" -ForegroundColor Yellow
            } elseif ($ExitCode -eq 2) {
                Write-Host " Critical security issues found" -ForegroundColor Red
            } else {
                Write-Host " Security scan failed" -ForegroundColor Red
            }
            
            exit $ExitCode
        }
        
        # Default: show help
        Write-Host "`nEQ12 Security Scanner v3.0 - Available Options:" -ForegroundColor Yellow
        Write-Host "  -Scan              Run comprehensive security scan" -ForegroundColor Gray
        Write-Host "  -CleanMemory       Clean memory before scan" -ForegroundColor Gray
        Write-Host "  -Dashboard         Show security status dashboard" -ForegroundColor Gray
        Write-Host "  -Verbose           Enable verbose logging" -ForegroundColor Gray
        Write-Host "`nExample: .\eq12_snyk_security_v3.ps1 -Scan -CleanMemory -Verbose" -ForegroundColor Cyan
        
        exit 0
    }
    finally {
        # Always remove lock
        if (Test-Path $LockFile) {
            Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
        }
    }
}
catch {
    Write-EQ12Log "Critical error: $_" "ERROR"
    Write-Host " Security scanner failed: $_" -ForegroundColor Red
    
    # Cleanup
    if (Test-Path $LockFile) {
        Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
    }
    
    exit 1
}
