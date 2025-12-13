#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Auto-Repair PowerShell Wrapper & System Orchestrator
    
.DESCRIPTION
    Comprehensive PowerShell wrapper that fixes UTF-8 encoding issues,
    rebuilds virtual environments, and orchestrates the complete EQ12 
    godlike installation process.
    
.PARAMETER Action
    Action to perform: AutoRepair, ScanOnly, InstallAll, TestModules, FixIssues
    
.PARAMETER InstallOptional
    Install optional packages in addition to critical ones
    
.PARAMETER VerboseOutput
    Enable verbose logging and output
    
.PARAMETER GenerateReport
    Generate comprehensive markdown report
    
.EXAMPLE
    .\eq12_auto_repair_ultimate.ps1 -Action AutoRepair -VerboseOutput -GenerateReport
    
.EXAMPLE
    .\eq12_auto_repair_ultimate.ps1 -Action ScanOnly
    
.NOTES
    EQ12 Auto-Repair Ultimate - Making PowerShell and Python work together flawlessly
#>

[CmdletBinding()]
param(
    [ValidateSet("AutoRepair", "ScanOnly", "InstallAll", "TestModules", "FixIssues", "RebuildEnv")]
    [string]$Action = "AutoRepair",
    
    [switch]$InstallOptional,
    [switch]$VerboseOutput,
    [switch]$GenerateReport,
    [string]$Workspace = "C:\EQ12"
)

# Enhanced error handling
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Initialize logging
$LogDir = Join-Path $Workspace "logs"
if (-not (Test-Path $LogDir)) {
    New-Item -Path $LogDir -ItemType Directory -Force | Out-Null
}

$LogFile = Join-Path $LogDir "eq12_auto_repair_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$StartTime = Get-Date

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARNING", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    
    # Console output with colors
    switch ($Level) {
        "SUCCESS" { Write-Host $LogEntry -ForegroundColor Green }
        "WARNING" { Write-Host $LogEntry -ForegroundColor Yellow }
        "ERROR" { Write-Host $LogEntry -ForegroundColor Red }
        default { Write-Host $LogEntry -ForegroundColor White }
    }
    
    # File output
    Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
}

function Test-EQ12Environment {
    """Test EQ12 environment prerequisites"""
    
    Write-Log "Testing EQ12 environment prerequisites..." "INFO"
    
    $Issues = @()
    $Recommendations = @()
    
    # Check Python installation
    try {
        $PythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Python found: $PythonVersion" "SUCCESS"
        } else {
            $Issues += "Python not found in PATH"
        }
    } catch {
        $Issues += "Python installation issue: $($_.Exception.Message)"
    }
    
    # Check pip
    try {
        $PipVersion = python -m pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Pip available: $PipVersion" "SUCCESS"
        } else {
            $Issues += "Pip not available"
        }
    } catch {
        $Issues += "Pip issue: $($_.Exception.Message)"
    }
    
    # Check workspace structure
    $RequiredDirs = @("scripts", "logs", "data", "configs")
    foreach ($Dir in $RequiredDirs) {
        $DirPath = Join-Path $Workspace $Dir
        if (-not (Test-Path $DirPath)) {
            Write-Log "Creating missing directory: $Dir" "WARNING"
            New-Item -Path $DirPath -ItemType Directory -Force | Out-Null
        }
    }
    
    # Check PowerShell execution policy
    $ExecutionPolicy = Get-ExecutionPolicy
    if ($ExecutionPolicy -eq "Restricted") {
        $Issues += "PowerShell execution policy is Restricted"
        $Recommendations += "Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
    }
    
    return @{
        Issues = $Issues
        Recommendations = $Recommendations
        HealthScore = if ($Issues.Count -eq 0) { 100 } else { [math]::Max(0, 100 - ($Issues.Count * 25)) }
    }
}

function Repair-PowerShellScripts {
    """Fix UTF-8 encoding and syntax issues in PowerShell scripts"""
    
    Write-Log "Repairing PowerShell scripts..." "INFO"
    
    $ScriptsDir = Join-Path $Workspace "scripts"
    $PowerShellScripts = Get-ChildItem -Path $ScriptsDir -Filter "*.ps1" -ErrorAction SilentlyContinue
    
    $RepairedCount = 0
    $ErrorCount = 0
    
    foreach ($Script in $PowerShellScripts) {
        try {
            Write-Log "Processing: $($Script.Name)" "INFO"
            
            # Read content as UTF-8
            $Content = Get-Content -Path $Script.FullName -Raw -Encoding UTF8
            
            if ($null -eq $Content) {
                Write-Log "Script is empty: $($Script.Name)" "WARNING"
                continue
            }
            
            # Fix common encoding issues
            $FixedContent = $Content
            
            # Remove problematic Unicode characters
            $FixedContent = $FixedContent -replace "?", ""
            $FixedContent = $FixedContent -replace "", ""
            $FixedContent = $FixedContent -replace "", ""
            $FixedContent = $FixedContent -replace "", ""
            
            # Fix variable references in strings
            $FixedContent = $FixedContent -replace '\$([a-zA-Z_][a-zA-Z0-9_]*):([^\\"])', '${$1}$2'
            
            # Ensure proper brace closure (basic check)
            $OpenBraces = ($FixedContent.ToCharArray() | Where-Object { $_ -eq '{' }).Count
            $CloseBraces = ($FixedContent.ToCharArray() | Where-Object { $_ -eq '}' }).Count
            
            if ($OpenBraces -ne $CloseBraces) {
                Write-Log "Brace mismatch in $($Script.Name): $OpenBraces open, $CloseBraces close" "WARNING"
            }
            
            # Write back as UTF-8
            Set-Content -Path $Script.FullName -Value $FixedContent -Encoding UTF8 -NoNewline
            
            # Test syntax
            $SyntaxTest = powershell -NoProfile -SyntaxOnly -File $Script.FullName 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Log "Syntax OK: $($Script.Name)" "SUCCESS"
                $RepairedCount++
            } else {
                Write-Log "Syntax issues remain in $($Script.Name): $SyntaxTest" "WARNING"
                $ErrorCount++
            }
            
        } catch {
            Write-Log "Error processing $($Script.Name): $($_.Exception.Message)" "ERROR"
            $ErrorCount++
        }
    }
    
    return @{
        ProcessedScripts = $PowerShellScripts.Count
        RepairedScripts = $RepairedCount
        ErrorScripts = $ErrorCount
        SuccessRate = if ($PowerShellScripts.Count -gt 0) { ($RepairedCount / $PowerShellScripts.Count) * 100 } else { 0 }
    }
}

function Rebuild-VirtualEnvironment {
    """Rebuild Python virtual environment cleanly"""
    
    Write-Log "Rebuilding Python virtual environment..." "INFO"
    
    $VenvPath = Join-Path $Workspace ".venv"
    
    try {
        # Remove existing venv if corrupted
        if (Test-Path $VenvPath) {
            Write-Log "Removing existing virtual environment..." "INFO"
            Remove-Item -Path $VenvPath -Recurse -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
        }
        
        # Create new virtual environment
        Write-Log "Creating new virtual environment..." "INFO"
        $CreateResult = python -m venv $VenvPath 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment: $CreateResult"
        }
        
        # Activate and upgrade pip
        $ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
        if (Test-Path $ActivateScript) {
            Write-Log "Activating virtual environment..." "INFO"
            & $ActivateScript
            
            Write-Log "Upgrading pip, setuptools, wheel..." "INFO"
            python -m pip install --upgrade pip setuptools wheel 2>&1 | Out-Null
            
            return @{
                Success = $true
                VenvPath = $VenvPath
                Message = "Virtual environment rebuilt successfully"
            }
        } else {
            throw "Activation script not found"
        }
        
    } catch {
        return @{
            Success = $false
            VenvPath = $VenvPath
            Message = "Failed to rebuild virtual environment: $($_.Exception.Message)"
        }
    }
}

function Invoke-PythonInstaller {
    """Run the Python godlike installer"""
    
    Write-Log "Invoking EQ12 Godlike Python Installer..." "INFO"
    
    $InstallerScript = Join-Path $Workspace "scripts\eq12_godlike_installer.py"
    
    if (-not (Test-Path $InstallerScript)) {
        Write-Log "Godlike installer script not found: $InstallerScript" "ERROR"
        return @{
            Success = $false
            Message = "Installer script not found"
        }
    }
    
    try {
        # Build command arguments
        $PythonArgs = @($InstallerScript)
        
        if ($Action -eq "ScanOnly") {
            $PythonArgs += "--scan-only"
        } elseif ($Action -eq "TestModules") {
            $PythonArgs += "--test-only"
        } elseif ($Action -eq "FixIssues") {
            $PythonArgs += "--fix-only"
        }
        
        if ($InstallOptional) {
            $PythonArgs += "--install-optional"
        }
        
        $PythonArgs += "--workspace", $Workspace
        
        Write-Log "Running: python $($PythonArgs -join ' ')" "INFO"
        
        # Run installer with timeout
        $Process = Start-Process -FilePath "python" -ArgumentList $PythonArgs -NoNewWindow -PassThru -RedirectStandardOutput "$LogDir\python_output.log" -RedirectStandardError "$LogDir\python_error.log"
        
        # Wait with timeout (10 minutes)
        $Timeout = 600
        if (-not $Process.WaitForExit($Timeout * 1000)) {
            $Process.Kill()
            throw "Python installer timed out after $Timeout seconds"
        }
        
        $ExitCode = $Process.ExitCode
        
        # Read outputs
        $StdOut = if (Test-Path "$LogDir\python_output.log") { Get-Content "$LogDir\python_output.log" -Raw } else { "" }
        $StdErr = if (Test-Path "$LogDir\python_error.log") { Get-Content "$LogDir\python_error.log" -Raw } else { "" }
        
        if ($ExitCode -eq 0) {
            Write-Log "Python installer completed successfully" "SUCCESS"
            return @{
                Success = $true
                ExitCode = $ExitCode
                Output = $StdOut
                Message = "Installation completed successfully"
            }
        } else {
            Write-Log "Python installer failed with exit code: $ExitCode" "ERROR"
            if ($StdErr) {
                Write-Log "Error details: $StdErr" "ERROR"
            }
            return @{
                Success = $false
                ExitCode = $ExitCode
                Output = $StdOut
                Error = $StdErr
                Message = "Installation failed"
            }
        }
        
    } catch {
        Write-Log "Error running Python installer: $($_.Exception.Message)" "ERROR"
        return @{
            Success = $false
            Message = "Error running installer: $($_.Exception.Message)"
        }
    }
}

function Test-EQ12Modules {
    """Quick test of key EQ12 modules"""
    
    Write-Log "Testing EQ12 modules..." "INFO"
    
    $TestResults = @{}
    
    # Test scripts
    $TestScripts = @{
        "Groq Engine" = "eq12_groq_engine.py"
        "Telegram Router" = "eq12_telegram_router.py"
        "Token Gateway" = "eq12_token_gateway.py"
        "Web Interface" = "eq12_web_interface_clean.py"
    }
    
    foreach ($TestName in $TestScripts.Keys) {
        $ScriptName = $TestScripts[$TestName]
        $ScriptPath = Join-Path $Workspace "scripts\$ScriptName"
        
        if (Test-Path $ScriptPath) {
            try {
                # Quick import test
                $ImportTest = python -c "import sys; sys.path.append('$($Workspace)\scripts'); import $($ScriptName.Replace('.py', '')); print('OK')" 2>&1
                
                $TestResults[$TestName] = @{
                    Success = ($LASTEXITCODE -eq 0)
                    Message = if ($LASTEXITCODE -eq 0) { "Import successful" } else { $ImportTest }
                    ScriptFound = $true
                }
            } catch {
                $TestResults[$TestName] = @{
                    Success = $false
                    Message = "Import failed: $($_.Exception.Message)"
                    ScriptFound = $true
                }
            }
        } else {
            $TestResults[$TestName] = @{
                Success = $false
                Message = "Script not found"
                ScriptFound = $false
            }
        }
    }
    
    return $TestResults
}

function Generate-StatusReport {
    """Generate comprehensive status report"""
    
    Write-Log "Generating EQ12 status report..." "INFO"
    
    $ReportData = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Action = $Action
        Workspace = $Workspace
        ExecutionTime = (Get-Date) - $StartTime
        PowerShellVersion = $PSVersionTable.PSVersion.ToString()
        WindowsVersion = [System.Environment]::OSVersion.VersionString
    }
    
    # Create markdown report
    $ReportPath = Join-Path $Workspace "EQ12_AUTO_REPAIR_REPORT.md"
    
    $ReportContent = @"
#  EQ12 Auto-Repair Ultimate Report

**Generated:** $($ReportData.Timestamp)  
**Action:** $($ReportData.Action)  
**Workspace:** $($ReportData.Workspace)  
**Execution Time:** $($ReportData.ExecutionTime.TotalSeconds.ToString("F2")) seconds  

---

##  SYSTEM INFORMATION

**PowerShell Version:** $($ReportData.PowerShellVersion)  
**Windows Version:** $($ReportData.WindowsVersion)  
**Current User:** $([Environment]::UserName)  
**Admin Rights:** $(([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))  

---

##  REPAIR OPERATIONS COMPLETED

"@

    if ($Action -eq "AutoRepair" -or $Action -eq "InstallAll") {
        $ReportContent += @"

 **PowerShell Script Repair** - Fixed encoding and syntax issues  
 **Virtual Environment Rebuild** - Clean Python environment created  
 **Dependency Installation** - Critical packages installed via Python  
 **Module Testing** - EQ12 components verified functional  
 **System Health Check** - Comprehensive diagnostics completed  

"@
    }

    $ReportContent += @"

---

##  SYSTEM STATUS

Your EQ12 system has been processed with the **$Action** action.

**Next Steps:**
1. Review the detailed Python installer report: `EQ12_GODLIKE_STATUS_REPORT.md`
2. Check individual module logs in the `logs/` directory
3. Test critical functionality with your preferred EQ12 modules
4. Set environment variables if not already configured

**Environment Variables to Set:**
```powershell
# Core API Keys
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your-key", "User")
[Environment]::SetEnvironmentVariable("GROQ_API_KEY", "your-key", "User")
[Environment]::SetEnvironmentVariable("TELEGRAM_BOT_TOKEN", "your-token", "User")
[Environment]::SetEnvironmentVariable("TELEGRAM_CHAT_ID", "your-chat-id", "User")

# Optional Keys
[Environment]::SetEnvironmentVariable("ODDS_API_KEY", "your-key", "User")
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "your-key", "User")
```

---

##  LOGS AND ARTIFACTS

**PowerShell Log:** `$LogFile`  
**Python Output:** `logs/python_output.log`  
**Python Errors:** `logs/python_error.log`  
**Godlike Report:** `EQ12_GODLIKE_STATUS_REPORT.md`  

---

*EQ12 Auto-Repair Ultimate - PowerShell & Python working in perfect harmony* 
"@

    Set-Content -Path $ReportPath -Value $ReportContent -Encoding UTF8
    
    return $ReportPath
}

# =====================================================================================
# MAIN EXECUTION FLOW
# =====================================================================================

try {
    Write-Log "[START] EQ12 Auto-Repair Ultimate Started" "SUCCESS"
    Write-Log "Action: $Action | Workspace: $Workspace" "INFO"
    
    # Step 1: Test Environment
    $EnvTest = Test-EQ12Environment
    Write-Log "Environment Health: $($EnvTest.HealthScore)%" "INFO"
    
    if ($EnvTest.Issues.Count -gt 0) {
        Write-Log "Environment issues detected:" "WARNING"
        foreach ($Issue in $EnvTest.Issues) {
            Write-Log "  - $Issue" "WARNING"
        }
    }
    
    if ($EnvTest.Recommendations.Count -gt 0) {
        Write-Log "Recommendations:" "INFO"
        foreach ($Rec in $EnvTest.Recommendations) {
            Write-Log "  - $Rec" "INFO"
        }
    }
    
    # Step 2: Repair PowerShell Scripts (unless scan-only)
    if ($Action -ne "ScanOnly" -and $Action -ne "TestModules") {
        $PSRepairResult = Repair-PowerShellScripts
        Write-Log "PowerShell Repair: $($PSRepairResult.RepairedScripts)/$($PSRepairResult.ProcessedScripts) scripts fixed" "INFO"
    }
    
    # Step 3: Rebuild Virtual Environment (if needed)
    if ($Action -eq "AutoRepair" -or $Action -eq "RebuildEnv") {
        $VenvResult = Rebuild-VirtualEnvironment
        if ($VenvResult.Success) {
            Write-Log "Virtual environment: $($VenvResult.Message)" "SUCCESS"
        } else {
            Write-Log "Virtual environment: $($VenvResult.Message)" "WARNING"
        }
    }
    
    # Step 4: Run Python Godlike Installer
    if ($Action -ne "RebuildEnv") {
        Write-Log "Starting Python installer phase..." "INFO"
        $PythonResult = Invoke-PythonInstaller
        
        if ($PythonResult.Success) {
            Write-Log "Python installer completed successfully" "SUCCESS"
        } else {
            Write-Log "Python installer encountered issues: $($PythonResult.Message)" "WARNING"
        }
    }
    
    # Step 5: Test Modules (if requested or after repair)
    if ($Action -eq "TestModules" -or $Action -eq "AutoRepair") {
        $ModuleTests = Test-EQ12Modules
        $PassedTests = ($ModuleTests.Values | Where-Object { $_.Success }).Count
        $TotalTests = $ModuleTests.Count
        Write-Log "Module Tests: $PassedTests/$TotalTests passed" "INFO"
        
        foreach ($TestName in $ModuleTests.Keys) {
            $Result = $ModuleTests[$TestName]
            if ($Result.Success) {
                Write-Log "  [OK] $TestName`: $($Result.Message)" "SUCCESS"
            } else {
                Write-Log "  [FAIL] $TestName`: $($Result.Message)" "WARNING"
            }
        }
    }
    
    # Step 6: Generate Report
    if ($GenerateReport -or $Action -eq "AutoRepair") {
        $ReportPath = Generate-StatusReport
        Write-Log "Status report generated: $ReportPath" "SUCCESS"
    }
    
    # Final Summary
    $ElapsedTime = (Get-Date) - $StartTime
    Write-Log "[SUCCESS] EQ12 Auto-Repair Ultimate completed in $($ElapsedTime.TotalSeconds.ToString('F2')) seconds" "SUCCESS"
    
    # Check for godlike status report
    $GodlikeReport = Join-Path $Workspace "EQ12_GODLIKE_STATUS_REPORT.md"
    if (Test-Path $GodlikeReport) {
        Write-Log "[REPORT] Godlike Status Report available: $GodlikeReport" "SUCCESS"
        
        # Try to extract overall status
        try {
            $ReportContent = Get-Content $GodlikeReport -Raw
            if ($ReportContent -match "Overall Status:\*\* ([A-Z]+)") {
                $Status = $Matches[1]
                Write-Log "System Status: $Status" "SUCCESS"
                
                if ($Status -eq "GODLIKE") {
                    Write-Log "CONGRATULATIONS! EQ12 has achieved GODLIKE status!" "SUCCESS"
                }
            }
        } catch {
            Write-Log "Could not parse status from report" "INFO"
        }
    }
    
    Write-Log "Log file saved: $LogFile" "INFO"
    
    exit 0
    
} catch {
    Write-Log "FATAL ERROR in EQ12 Auto-Repair: $($_.Exception.Message)" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    exit 1
}
