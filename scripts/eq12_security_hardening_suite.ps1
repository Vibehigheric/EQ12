# EQ12 Security Hardening PowerShell Wrapper
# Buffalo NY 14215 Content Empire
# Multi-Hat Security Analysis Suite

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('full', 'quick', 'critical-only')]
    [string]$Mode = 'full',

    [Parameter(Mandatory=$false)]
    [ValidateSet('json', 'text', 'both')]
    [string]$Output = 'both',

    [Parameter(Mandatory=$false)]
    [switch]$FixIssues,

    [Parameter(Mandatory=$false)]
    [switch]$GenerateReport,

    [Parameter(Mandatory=$false)]
    [switch]$AutoHarden
)

# Set strict error handling
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Initialize logging
$LogFile = "C:\EQ12\logs\eq12_security_hardening_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$ScriptName = $MyInvocation.MyCommand.Name

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "$Timestamp [$Level] $ScriptName`: $Message"
    Add-Content -Path $LogFile -Value $LogEntry -Encoding ASCII
    Write-Host $LogEntry -ForegroundColor $(
        switch($Level) {
            "ERROR" { "Red" }
            "WARN" { "Yellow" }
            "SUCCESS" { "Green" }
            default { "White" }
        }
    )
}

function Test-Prerequisites {
    Write-Log "Checking security hardening prerequisites..."

    # Check if Python is available
    try {
        $PythonVersion = python --version 2>&1
        Write-Log "Python available: $PythonVersion" "SUCCESS"
    } catch {
        Write-Log "Python not found. Install Python 3.12 or later." "ERROR"
        throw "Python prerequisite not met"
    }

    # Check if we can write to logs directory
    if (-not (Test-Path "C:\EQ12\logs")) {
        New-Item -Path "C:\EQ12\logs" -ItemType Directory -Force | Out-Null
        Write-Log "Created logs directory" "SUCCESS"
    }

    # Check current execution policy
    $ExecPolicy = Get-ExecutionPolicy
    if ($ExecPolicy -eq "Restricted") {
        Write-Log "PowerShell execution policy is Restricted. This may limit security testing capabilities." "WARN"
    } else {
        Write-Log "PowerShell execution policy: $ExecPolicy" "INFO"
    }

    # Check if running with appropriate privileges
    $CurrentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $Principal = New-Object Security.Principal.WindowsPrincipal($CurrentUser)
    $IsAdmin = $Principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

    if ($IsAdmin) {
        Write-Log "Running with administrative privileges" "SUCCESS"
    } else {
        Write-Log "Running with standard user privileges. Some security checks may be limited." "WARN"
    }
}

function Start-SecurityAudit {
    param([string]$AuditMode, [string]$OutputFormat, [bool]$AutoFix)

    Write-Log "Starting EQ12 Multi-Hat Security Audit - Mode: $AuditMode" "INFO"

    # Construct Python command
    $PythonScript = "C:\EQ12\scripts\eq12_security_hardening_suite.py"
    $PythonArgs = @(
        "--mode", $AuditMode,
        "--output", $OutputFormat
    )

    if ($AutoFix) {
        $PythonArgs += "--fix-issues"
    }

    try {
        # Execute Python security suite
        Write-Log "Executing Python security suite..."
        $Result = & python $PythonScript @PythonArgs

        if ($LASTEXITCODE -eq 0) {
            Write-Log "Security audit completed successfully" "SUCCESS"
        } elseif ($LASTEXITCODE -eq 1) {
            Write-Log "Security audit completed with CRITICAL vulnerabilities found" "ERROR"
        } else {
            Write-Log "Security audit failed with exit code: $LASTEXITCODE" "ERROR"
        }

        return $Result
    } catch {
        Write-Log "Failed to execute security audit: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Invoke-PowerShellSecurityHardening {
    Write-Log "Applying PowerShell-specific security hardening..."

    try {
        # 1. Check and recommend execution policy
        $CurrentPolicy = Get-ExecutionPolicy -Scope CurrentUser
        if ($CurrentPolicy -in @("Unrestricted", "Bypass")) {
            Write-Log "SECURITY RISK: PowerShell execution policy is $CurrentPolicy" "ERROR"

            if ($AutoHarden) {
                Write-Log "Auto-hardening: Setting execution policy to RemoteSigned..."
                Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
                Write-Log "Execution policy updated to RemoteSigned" "SUCCESS"
            } else {
                Write-Log "RECOMMENDATION: Run 'Set-ExecutionPolicy RemoteSigned -Scope CurrentUser'" "WARN"
            }
        } else {
            Write-Log "PowerShell execution policy is secure: $CurrentPolicy" "SUCCESS"
        }

        # 2. Check for dangerous PowerShell patterns in EQ12 scripts
        Write-Log "Scanning PowerShell scripts for security risks..."
        $PowerShellFiles = Get-ChildItem -Path "C:\EQ12" -Filter "*.ps1" -Recurse

        $RiskyPatterns = @{
            "Invoke-Expression" = "Code injection risk"
            "IEX" = "Code injection risk"
            "DownloadString" = "Remote code execution risk"
            "EncodedCommand" = "Obfuscated command execution"
            "Bypass" = "Execution policy bypass"
            "-WindowStyle Hidden" = "Hidden execution"
            "Start-Process.*-Verb RunAs" = "Privilege escalation"
        }

        $SecurityIssues = @()

        foreach ($File in $PowerShellFiles) {
            try {
                $Content = Get-Content -Path $File.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue

                foreach ($Pattern in $RiskyPatterns.Keys) {
                    if ($Content -match $Pattern) {
                        $SecurityIssues += [PSCustomObject]@{
                            File = $File.FullName
                            Pattern = $Pattern
                            Risk = $RiskyPatterns[$Pattern]
                            Line = ($Content -split "`n" | Select-String $Pattern | Select-Object -First 1).LineNumber
                        }
                    }
                }
            } catch {
                Write-Log "Could not scan file: $($File.FullName)" "WARN"
            }
        }

        if ($SecurityIssues.Count -gt 0) {
            Write-Log "Found $($SecurityIssues.Count) PowerShell security issues:" "ERROR"
            foreach ($Issue in $SecurityIssues) {
                Write-Log "  - $($Issue.File):$($Issue.Line) - $($Issue.Pattern) ($($Issue.Risk))" "ERROR"
            }
        } else {
            Write-Log "No PowerShell security risks detected" "SUCCESS"
        }

        # 3. Verify script integrity
        Write-Log "Checking script integrity..."
        $CriticalScripts = @(
            "C:\EQ12\eq12_no_pycache.py",
            "C:\EQ12\scripts\eq12_pycache_cleanup.ps1",
            "C:\EQ12\.copilot\copilot.yml"
        )

        foreach ($Script in $CriticalScripts) {
            if (Test-Path $Script) {
                $Hash = Get-FileHash -Path $Script -Algorithm SHA256
                $HashFile = "$Script.sha256"

                if (Test-Path $HashFile) {
                    $StoredHash = Get-Content $HashFile -Raw
                    if ($Hash.Hash -ne $StoredHash.Trim()) {
                        Write-Log "INTEGRITY VIOLATION: $Script has been modified" "ERROR"
                    } else {
                        Write-Log "Integrity verified: $Script" "SUCCESS"
                    }
                } else {
                    # Store initial hash
                    $Hash.Hash | Out-File $HashFile -Encoding ASCII -NoNewline
                    Write-Log "Created integrity hash for: $Script" "INFO"
                }
            }
        }

    } catch {
        Write-Log "PowerShell security hardening failed: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Test-EnvironmentSecurity {
    Write-Log "Testing environment security configuration..."

    # Check required environment variables
    $RequiredEnvVars = @(
        "PYTHONDONTWRITEBYTECODE",
        "EQ12_ASCII_MODE"
    )

    $SensitiveEnvVars = @(
        "ODDS_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
        "OPENAI_API_KEY",
        "GITHUB_TOKEN"
    )

    # Check required variables
    foreach ($Var in $RequiredEnvVars) {
        $Value = [Environment]::GetEnvironmentVariable($Var, [EnvironmentVariableTarget]::User)
        if (-not $Value) {
            Write-Log "Missing required environment variable: $Var" "ERROR"
        } else {
            Write-Log "Required environment variable set: $Var" "SUCCESS"
        }
    }

    # Check sensitive variables (should be set but not logged)
    foreach ($Var in $SensitiveEnvVars) {
        $Value = [Environment]::GetEnvironmentVariable($Var, [EnvironmentVariableTarget]::User)
        if ($Value) {
            Write-Log "Sensitive environment variable configured: $Var" "SUCCESS"
        } else {
            Write-Log "Sensitive environment variable not set: $Var" "WARN"
        }
    }

    # Check for environment variable leakage in code
    Write-Log "Checking for hardcoded secrets in code..."
    $CodeFiles = Get-ChildItem -Path "C:\EQ12" -Include @("*.py", "*.ps1", "*.json", "*.yml") -Recurse

    $HardcodedSecrets = @()
    foreach ($File in $CodeFiles) {
        try {
            $Content = Get-Content -Path $File.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue

            # Look for potential hardcoded API keys/tokens
            $SecretPatterns = @(
                '(?i)(api[_-]?key|apikey)\s*[=:]\s*["\''']?([a-zA-Z0-9_-]{20,})["\''']?',
                '(?i)(token|auth[_-]?token)\s*[=:]\s*["\''']?([a-zA-Z0-9_-]{30,})["\''']?',
                '(?i)(password|passwd)\s*[=:]\s*["\''']?([^"\'''\s]{8,})["\''']?',
                '(?i)(secret|secret[_-]?key)\s*[=:]\s*["\''']?([a-zA-Z0-9_-]{16,})["\''']?'
            )

            foreach ($Pattern in $SecretPatterns) {
                if ($Content -match $Pattern) {
                    # Exclude obvious test/example values
                    $Match = [regex]::Match($Content, $Pattern)
                    $Value = $Match.Groups[2].Value

                    if ($Value -notmatch '(?i)(test|example|dummy|placeholder|xxx|123)') {
                        $HardcodedSecrets += [PSCustomObject]@{
                            File = $File.FullName
                            Type = $Match.Groups[1].Value
                            Value = $Value.Substring(0, [Math]::Min($Value.Length, 10)) + "..."
                        }
                    }
                }
            }
        } catch {
            # Skip files that can't be read
        }
    }

    if ($HardcodedSecrets.Count -gt 0) {
        Write-Log "Found $($HardcodedSecrets.Count) potential hardcoded secrets:" "ERROR"
        foreach ($Secret in $HardcodedSecrets) {
            Write-Log "  - $($Secret.File): $($Secret.Type) = $($Secret.Value)" "ERROR"
        }
    } else {
        Write-Log "No hardcoded secrets detected" "SUCCESS"
    }
}

function Test-FileSystemSecurity {
    Write-Log "Testing file system security..."

    # Check permissions on critical directories
    $CriticalDirs = @(
        "C:\EQ12\scripts",
        "C:\EQ12\configs",
        "C:\EQ12\.github",
        "C:\EQ12\logs"
    )

    foreach ($Dir in $CriticalDirs) {
        if (Test-Path $Dir) {
            try {
                # Check if directory is writable by current user
                $TestFile = Join-Path $Dir "security_test_$(Get-Date -Format 'yyyyMMddHHmmss').tmp"
                "test" | Out-File $TestFile -Encoding ASCII
                Remove-Item $TestFile -Force
                Write-Log "Directory permissions verified: $Dir" "SUCCESS"
            } catch {
                Write-Log "Cannot write to directory: $Dir" "ERROR"
            }
        } else {
            Write-Log "Critical directory missing: $Dir" "ERROR"
        }
    }

    # Check for suspicious executables
    $SuspiciousExes = Get-ChildItem -Path "C:\EQ12" -Filter "*.exe" -Recurse
    if ($SuspiciousExes.Count -gt 0) {
        Write-Log "Found $($SuspiciousExes.Count) executable files:" "WARN"
        foreach ($Exe in $SuspiciousExes) {
            Write-Log "  - $($Exe.FullName)" "WARN"
        }
    }
}

function Invoke-NetworkSecurityCheck {
    Write-Log "Checking network security configuration..."

    try {
        # Check Windows Firewall status
        $FirewallProfiles = Get-NetFirewallProfile
        foreach ($Profile in $FirewallProfiles) {
            if ($Profile.Enabled) {
                Write-Log "Firewall profile '$($Profile.Name)' is enabled" "SUCCESS"
            } else {
                Write-Log "Firewall profile '$($Profile.Name)' is DISABLED" "ERROR"
                if ($AutoHarden) {
                    Set-NetFirewallProfile -Profile $Profile.Name -Enabled True
                    Write-Log "Auto-hardening: Enabled firewall profile '$($Profile.Name)'" "SUCCESS"
                }
            }
        }

        # Check for active network connections to external hosts
        $ExternalConnections = Get-NetTCPConnection | Where-Object {
            $_.State -eq "Established" -and
            $_.RemoteAddress -notmatch '^(127\.|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)' -and
            $_.RemoteAddress -ne "::" -and
            $_.RemoteAddress -ne "0.0.0.0"
        }

        if ($ExternalConnections.Count -gt 0) {
            Write-Log "Found $($ExternalConnections.Count) external network connections:" "INFO"
            foreach ($Conn in $ExternalConnections | Select-Object -First 10) {
                Write-Log "  - $($Conn.LocalAddress):$($Conn.LocalPort) -> $($Conn.RemoteAddress):$($Conn.RemotePort)" "INFO"
            }
        }

    } catch {
        Write-Log "Network security check failed: $($_.Exception.Message)" "ERROR"
    }
}

function Start-ContinuousMonitoring {
    Write-Log "Setting up continuous security monitoring..."

    $MonitoringScript = @"
# EQ12 Continuous Security Monitor
# Auto-generated by Security Hardening Suite

param()

`$LogFile = "C:\EQ12\logs\security_monitor_`$(Get-Date -Format 'yyyyMMdd').log"
`$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Function to log events
function Write-SecurityLog {
    param([string]`$Message)
    "`$Timestamp - `$Message" | Add-Content `$LogFile -Encoding ASCII
}

try {
    # Monitor PowerShell activity
    `$PSEvents = Get-WinEvent -FilterHashtable @{LogName='Windows PowerShell'; StartTime=(Get-Date).AddMinutes(-15)} -ErrorAction SilentlyContinue
    `$SuspiciousPSEvents = `$PSEvents | Where-Object {`$_.Message -match 'Invoke-Expression|DownloadString|EncodedCommand|IEX'}

    if (`$SuspiciousPSEvents) {
        Write-SecurityLog "ALERT: `$(`$SuspiciousPSEvents.Count) suspicious PowerShell events detected"
    }

    # Monitor file integrity of critical files
    `$CriticalFiles = @(
        "C:\EQ12\eq12_no_pycache.py",
        "C:\EQ12\.copilot\copilot.yml"
    )

    foreach (`$File in `$CriticalFiles) {
        if (Test-Path `$File) {
            `$CurrentHash = (Get-FileHash `$File -Algorithm SHA256).Hash
            `$HashFile = "`$File.sha256"

            if (Test-Path `$HashFile) {
                `$StoredHash = Get-Content `$HashFile -Raw
                if (`$CurrentHash -ne `$StoredHash.Trim()) {
                    Write-SecurityLog "ALERT: File integrity violation detected: `$File"
                }
            }
        }
    }

    # Monitor network connections
    `$ExternalConns = Get-NetTCPConnection | Where-Object {
        `$_.State -eq "Established" -and
        `$_.RemoteAddress -notmatch '^(127\.|10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)' -and
        `$_.RemoteAddress -ne "::" -and `$_.RemoteAddress -ne "0.0.0.0"
    }

    if (`$ExternalConns.Count -gt 20) {
        Write-SecurityLog "INFO: High number of external connections (`$(`$ExternalConns.Count))"
    }

    Write-SecurityLog "Security monitoring sweep completed successfully"

} catch {
    Write-SecurityLog "ERROR: Security monitoring failed: `$(`$_.Exception.Message)"
}
"@

    $MonitoringPath = "C:\EQ12\scripts\eq12_security_monitor.ps1"
    $MonitoringScript | Out-File -FilePath $MonitoringPath -Encoding ASCII -Force

    Write-Log "Security monitoring script created: $MonitoringPath" "SUCCESS"
    Write-Log "To enable continuous monitoring, schedule this script to run every 15 minutes:" "INFO"
    Write-Log "schtasks /create /tn 'EQ12 Security Monitor' /tr 'powershell -ExecutionPolicy Bypass -File $MonitoringPath' /sc minute /mo 15" "INFO"
}

function Generate-SecurityReport {
    Write-Log "Generating comprehensive security report..."

    $ReportPath = "C:\EQ12\logs\eq12_security_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').html"

    $HtmlReport = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 Security Audit Report</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .critical { background-color: #ffebee; border-left: 5px solid #f44336; }
        .warning { background-color: #fff3e0; border-left: 5px solid #ff9800; }
        .success { background-color: #e8f5e8; border-left: 5px solid #4caf50; }
        .info { background-color: #e3f2fd; border-left: 5px solid #2196f3; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f5f5f5; }
        .badge { padding: 2px 8px; border-radius: 3px; font-size: 0.8em; }
        .badge-critical { background-color: #f44336; color: white; }
        .badge-warning { background-color: #ff9800; color: white; }
        .badge-success { background-color: #4caf50; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <h1>EQ12 Security Audit Report</h1>
        <p>Buffalo NY 14215 Content Empire - Multi-Hat Security Assessment</p>
        <p>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
    </div>

    <div class="section info">
        <h2>Executive Summary</h2>
        <p>This report presents the results of a comprehensive security audit performed on the EQ12 automation system using Red Hat, Black Hat, White Hat, and Blue Hat methodologies.</p>
    </div>

    <div class="section">
        <h2>Audit Results</h2>
        <p>For detailed technical findings, please refer to the JSON report generated by the Python security suite.</p>

        <h3>PowerShell Security Status</h3>
        <p>Execution Policy: $(Get-ExecutionPolicy)</p>
        <p>Administrative Privileges: $($IsAdmin)</p>

        <h3>Environment Security</h3>
        <p>Environment variables and secret management assessment completed.</p>

        <h3>Network Security</h3>
        <p>Windows Firewall and network connection analysis performed.</p>
    </div>

    <div class="section success">
        <h2>Implemented Security Measures</h2>
        <ul>
            <li>Comprehensive vulnerability scanning</li>
            <li>PowerShell security hardening</li>
            <li>Environment variable security assessment</li>
            <li>File system permission validation</li>
            <li>Network security configuration review</li>
            <li>Continuous monitoring script deployment</li>
        </ul>
    </div>

    <div class="section info">
        <h2>Next Steps</h2>
        <ol>
            <li>Review and address any CRITICAL vulnerabilities immediately</li>
            <li>Implement recommended security controls</li>
            <li>Enable continuous security monitoring</li>
            <li>Schedule regular security audits</li>
            <li>Update security documentation</li>
        </ol>
    </div>

    <div class="section">
        <h2>Contact Information</h2>
        <p>For security concerns or questions about this report, contact the EQ12 security team.</p>
        <p>Report generated by EQ12 Security Hardening Suite</p>
    </div>
</body>
</html>
"@

    $HtmlReport | Out-File -FilePath $ReportPath -Encoding UTF8 -Force
    Write-Log "Security report generated: $ReportPath" "SUCCESS"

    return $ReportPath
}

# Main execution
try {
    Write-Log "=== EQ12 SECURITY HARDENING SUITE STARTED ===" "INFO"
    Write-Log "Mode: $Mode | Output: $Output | Fix Issues: $FixIssues | Auto Harden: $AutoHarden" "INFO"

    # Run prerequisites check
    Test-Prerequisites

    # Run Python security audit
    $AuditResults = Start-SecurityAudit -AuditMode $Mode -OutputFormat $Output -AutoFix $FixIssues

    # Run PowerShell-specific hardening
    Invoke-PowerShellSecurityHardening

    # Test environment security
    Test-EnvironmentSecurity

    # Test file system security
    Test-FileSystemSecurity

    # Check network security
    Invoke-NetworkSecurityCheck

    # Setup continuous monitoring
    Start-ContinuousMonitoring

    # Generate comprehensive report
    if ($GenerateReport) {
        $ReportPath = Generate-SecurityReport
        Write-Log "Open security report: $ReportPath" "INFO"
    }

    Write-Log "=== EQ12 SECURITY HARDENING SUITE COMPLETED ===" "SUCCESS"

    # Display summary
    Write-Host "`n" -NoNewline
    Write-Host "🛡️  EQ12 SECURITY HARDENING COMPLETE" -ForegroundColor Green -BackgroundColor Black
    Write-Host "📊 Audit Mode: $Mode" -ForegroundColor White
    Write-Host "📋 Log File: $LogFile" -ForegroundColor White
    Write-Host "🔍 Check logs for detailed results and recommendations" -ForegroundColor Yellow

    if ($GenerateReport) {
        Write-Host "📄 Security Report: $ReportPath" -ForegroundColor Cyan
    }

} catch {
    Write-Log "FATAL ERROR: $($_.Exception.Message)" "ERROR"
    Write-Log "Stack Trace: $($_.ScriptStackTrace)" "ERROR"
    Write-Host "❌ Security hardening failed. Check log: $LogFile" -ForegroundColor Red
    exit 1
}
