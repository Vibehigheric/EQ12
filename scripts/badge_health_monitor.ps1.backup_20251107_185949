# EQ12 GODSTACK Badge Health Monitor - PowerShell Wrapper
# Monthly automated monitoring of GitHub repository status badges

[CmdletBinding()]
param(
    [switch]$ForceAlert,
    [switch]$TestMode,
    [string]$LogLevel = "INFO"
)

# EQ12 standard error handling
$ErrorActionPreference = "Stop"
$LogPath = "C:\EQ12\logs\badge-health-monitor.log"

# Ensure logs directory exists
if (-not (Test-Path "C:\EQ12\logs")) {
    New-Item -Path "C:\EQ12\logs" -ItemType Directory -Force | Out-Null
}

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"
    $LogEntry = "[$Timestamp] [$Level] Badge Health Monitor: $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogPath -Value $LogEntry
}

function Test-Prerequisites {
    """Validate all required prerequisites for badge monitoring."""
    Write-EQ12Log "🔍 Validating badge health monitor prerequisites..."
    
    $issues = @()
    
    # Check Python availability
    try {
        $pythonVersion = python --version 2>&1
        Write-EQ12Log "✅ Python available: $pythonVersion"
    } catch {
        $issues += "Python not found in PATH"
    }
    
    # Check required environment variables
    $requiredEnvVars = @("GITHUB_TOKEN", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
    foreach ($envVar in $requiredEnvVars) {
        $envValue = [System.Environment]::GetEnvironmentVariable($envVar)
        if (-not $envValue) {
            $issues += "Missing environment variable: $envVar"
        } else {
            Write-EQ12Log "✅ Environment variable set: $envVar"
        }
    }
    
    # Check Python script exists
    $scriptPath = "C:\EQ12\scripts\badge_health_monitor.py"
    if (-not (Test-Path $scriptPath)) {
        $issues += "Badge health monitor script not found: $scriptPath"
    } else {
        Write-EQ12Log "✅ Badge health monitor script found"
    }
    
    # Check GitHub API access
    if ($env:GITHUB_TOKEN) {
        try {
            $headers = @{
                "Authorization" = "Bearer $env:GITHUB_TOKEN"
                "Accept" = "application/vnd.github+json"
            }
            $response = Invoke-RestMethod -Uri "https://api.github.com/user" -Headers $headers -Method GET
            Write-EQ12Log "✅ GitHub API access confirmed for user: $($response.login)"
        } catch {
            $issues += "GitHub API access failed: $($_.Exception.Message)"
        }
    }
    
    # Check Telegram API access
    if ($env:TELEGRAM_BOT_TOKEN -and $env:TELEGRAM_CHAT_ID) {
        try {
            $telegramUrl = "https://api.telegram.org/bot$env:TELEGRAM_BOT_TOKEN/getMe"
            $response = Invoke-RestMethod -Uri $telegramUrl -Method GET
            Write-EQ12Log "✅ Telegram bot access confirmed: $($response.result.username)"
        } catch {
            $issues += "Telegram API access failed: $($_.Exception.Message)"
        }
    }
    
    if ($issues.Count -gt 0) {
        Write-EQ12Log "❌ Prerequisites check failed:" -Level "ERROR"
        foreach ($issue in $issues) {
            Write-EQ12Log "   • $issue" -Level "ERROR"
        }
        return $false
    } else {
        Write-EQ12Log "✅ All prerequisites satisfied"
        return $true
    }
}

function Invoke-BadgeHealthCheck {
    """Execute the Python badge health monitor."""
    Write-EQ12Log "🚀 Starting EQ12 GODSTACK badge health check..."
    
    try {
        # Prepare arguments
        $arguments = @()
        if ($ForceAlert) { $arguments += "--force-alert" }
        
        # Set environment for Python script
        $env:PYTHONPATH = "C:\EQ12"
        
        # Execute Python script
        $scriptPath = "C:\EQ12\scripts\badge_health_monitor.py"
        
        Write-EQ12Log "🐍 Executing badge health monitor script..."
        
        if ($arguments.Count -gt 0) {
            & python $scriptPath $arguments
        } else {
            & python $scriptPath
        }
        
        $exitCode = $LASTEXITCODE
        
        # Interpret results
        switch ($exitCode) {
            0 { 
                Write-EQ12Log "✅ Badge health check completed - All systems green!"
                return @{ Success = $true; Status = "All Clear"; ExitCode = 0 }
            }
            1 { 
                Write-EQ12Log "🚨 CRITICAL ISSUES detected in badge health check!" -Level "ERROR"
                return @{ Success = $false; Status = "Critical Issues"; ExitCode = 1 }
            }
            2 { 
                Write-EQ12Log "⚠️ Warning issues detected in badge health check" -Level "WARN"
                return @{ Success = $true; Status = "Warnings"; ExitCode = 2 }
            }
            3 { 
                Write-EQ12Log "❌ Badge health check script error" -Level "ERROR"
                return @{ Success = $false; Status = "Script Error"; ExitCode = 3 }
            }
            default { 
                Write-EQ12Log "❓ Unknown exit code from badge health check: $exitCode" -Level "ERROR"
                return @{ Success = $false; Status = "Unknown Error"; ExitCode = $exitCode }
            }
        }
        
    } catch {
        Write-EQ12Log "❌ Failed to execute badge health monitor: $($_.Exception.Message)" -Level "ERROR"
        return @{ Success = $false; Status = "Execution Error"; ExitCode = -1 }
    }
}

function New-HealthCheckReport {
    """Generate PowerShell-specific health check report."""
    Write-EQ12Log "📊 Generating PowerShell badge health report..."
    
    $report = @{
        timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
        hostname = $env:COMPUTERNAME
        user = $env:USERNAME
        repository = "Vibehigheric/EQ12-GODSTACK"
        monitor_version = "1.0"
        powershell_version = $PSVersionTable.PSVersion.ToString()
        execution_policy = (Get-ExecutionPolicy).ToString()
    }
    
    # Check repository files
    $badgeFiles = @(
        "C:\EQ12\README.md",
        "C:\EQ12\DASHBOARD.md",
        "C:\EQ12\.github\workflows\github-advanced-security.yml",
        "C:\EQ12\.github\dependabot.yml",
        "C:\EQ12\.github\SECURITY.md"
    )
    
    $report.badge_infrastructure = @{}
    foreach ($file in $badgeFiles) {
        $fileName = Split-Path $file -Leaf
        $report.badge_infrastructure.$fileName = @{
            exists = (Test-Path $file)
            last_modified = if (Test-Path $file) { (Get-Item $file).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss") } else { "N/A" }
        }
    }
    
    # Save report
    $reportPath = "C:\EQ12\logs\badge-health-report-powershell-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $report | ConvertTo-Json -Depth 4 | Out-File -FilePath $reportPath -Encoding UTF8
    
    Write-EQ12Log "📊 PowerShell report saved: $reportPath"
    return $report
}

function Test-BadgeUrls {
    """Test badge URL accessibility."""
    Write-EQ12Log "🔗 Testing badge URL accessibility..."
    
    $badgeUrls = @{
        "CI Workflow" = "https://github.com/Vibehigheric/EQ12-GODSTACK/actions/workflows/github-advanced-security.yml"
        "Repository" = "https://github.com/Vibehigheric/EQ12-GODSTACK"
        "Security Tab" = "https://github.com/Vibehigheric/EQ12-GODSTACK/security"
        "Actions Tab" = "https://github.com/Vibehigheric/EQ12-GODSTACK/actions"
    }
    
    $results = @{}
    foreach ($name in $badgeUrls.Keys) {
        $url = $badgeUrls[$name]
        try {
            $response = Invoke-WebRequest -Uri $url -Method Head -TimeoutSec 10 -UseBasicParsing
            $results[$name] = @{
                status = "✅ Accessible"
                status_code = $response.StatusCode
            }
            Write-EQ12Log "✅ $name URL accessible"
        } catch {
            $results[$name] = @{
                status = "❌ Error"
                error = $_.Exception.Message
            }
            Write-EQ12Log "❌ $name URL error: $($_.Exception.Message)" -Level "WARN"
        }
    }
    
    return $results
}

function Main {
    """Main execution function for badge health monitoring."""
    Write-EQ12Log "🚀 EQ12 GODSTACK Badge Health Monitor Starting"
    Write-EQ12Log "Parameters: ForceAlert=$ForceAlert, TestMode=$TestMode, LogLevel=$LogLevel"
    
    try {
        # Test prerequisites
        if (-not (Test-Prerequisites)) {
            Write-EQ12Log "❌ Prerequisites check failed - cannot proceed" -Level "ERROR"
            return 1
        }
        
        # Test mode - validate setup only
        if ($TestMode) {
            Write-EQ12Log "🧪 Running in test mode - validating setup only"
            Test-BadgeUrls | Out-Null
            New-HealthCheckReport | Out-Null
            Write-EQ12Log "✅ Test mode completed successfully"
            return 0
        }
        
        # Execute badge health check
        $healthResult = Invoke-BadgeHealthCheck
        
        # Generate PowerShell report
        New-HealthCheckReport | Out-Null
        
        # Test badge URLs
        Test-BadgeUrls | Out-Null
        
        # Summary
        Write-EQ12Log ""
        Write-EQ12Log "📊 EQ12 GODSTACK Badge Health Monitor Summary:"
        Write-EQ12Log "   Status: $($healthResult.Status)"
        Write-EQ12Log "   Success: $($healthResult.Success)"
        Write-EQ12Log "   Exit Code: $($healthResult.ExitCode)"
        Write-EQ12Log "   Repository: Vibehigheric/EQ12-GODSTACK"
        Write-EQ12Log "   Monitor Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')"
        
        if ($healthResult.Success) {
            Write-EQ12Log "🎉 Badge health monitoring completed successfully!"
            
            if ($healthResult.Status -eq "All Clear") {
                Write-EQ12Log "🟢 All security badges are green - repository is healthy!"
            } elseif ($healthResult.Status -eq "Warnings") {
                Write-EQ12Log "🟡 Some warnings detected - review and address when convenient"
            }
            
        } else {
            Write-EQ12Log "❌ Badge health monitoring detected issues requiring attention" -Level "ERROR"
            
            if ($healthResult.Status -eq "Critical Issues") {
                Write-EQ12Log "🚨 CRITICAL security issues require immediate attention!" -Level "ERROR"
            }
        }
        
        return $healthResult.ExitCode
        
    } catch {
        Write-EQ12Log "❌ Unexpected error in badge health monitor: $($_.Exception.Message)" -Level "ERROR"
        return -1
    }
}

# Execute main function and exit with appropriate code
exit (Main)