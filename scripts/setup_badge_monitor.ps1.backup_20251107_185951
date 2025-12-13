# EQ12 Badge Health Monitor Deployment Script
# Automated setup of monthly GitHub badge monitoring with Telegram alerts

[CmdletBinding()]
param(
    [string]$GitHubToken = $env:GITHUB_TOKEN,
    [string]$TelegramBotToken = $env:TELEGRAM_BOT_TOKEN,
    [string]$TelegramChatId = $env:TELEGRAM_CHAT_ID,
    [switch]$TestOnly,
    [switch]$SetupEnvironment
)

$ErrorActionPreference = "Stop"
$LogPath = "C:\EQ12\logs\badge-monitor-setup.log"

function Write-SetupLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    if (Test-Path (Split-Path $LogPath)) {
        Add-Content -Path $LogPath -Value $LogEntry
    }
}

function Install-BadgeHealthMonitor {
    """Install and configure the EQ12 Badge Health Monitor."""
    Write-SetupLog "🚀 Installing EQ12 Badge Health Monitor..."
    
    try {
        # Validate required files exist
        $requiredFiles = @(
            "C:\EQ12\scripts\badge_health_monitor.py",
            "C:\EQ12\scripts\badge_health_monitor.ps1", 
            "C:\EQ12\eq12_badge_health_monitor.xml"
        )
        
        foreach ($file in $requiredFiles) {
            if (-not (Test-Path $file)) {
                throw "Required file not found: $file"
            }
        }
        Write-SetupLog "✅ All required files present"
        
        # Set up environment variables if requested
        if ($SetupEnvironment) {
            Write-SetupLog "🔧 Setting up environment variables..."
            
            if ($GitHubToken) {
                [Environment]::SetEnvironmentVariable("GITHUB_TOKEN", $GitHubToken, "User")
                Write-SetupLog "✅ GITHUB_TOKEN configured"
            }
            
            if ($TelegramBotToken) {
                [Environment]::SetEnvironmentVariable("TELEGRAM_BOT_TOKEN", $TelegramBotToken, "User")
                Write-SetupLog "✅ TELEGRAM_BOT_TOKEN configured"
            }
            
            if ($TelegramChatId) {
                [Environment]::SetEnvironmentVariable("TELEGRAM_CHAT_ID", $TelegramChatId, "User")
                Write-SetupLog "✅ TELEGRAM_CHAT_ID configured"
            }
        }
        
        # Install Task Scheduler job
        Write-SetupLog "📅 Installing Task Scheduler job..."
        $taskXmlPath = "C:\EQ12\eq12_badge_health_monitor.xml"
        $taskName = "EQ12\Badge Health Monitor"
        
        # Remove existing task if present
        try {
            schtasks /Delete /TN "$taskName" /F 2>$null
            Write-SetupLog "🗑️ Removed existing task"
        } catch {
            # Task didn't exist, that's fine
        }
        
        # Create new task
        $result = schtasks /Create /TN "$taskName" /XML "$taskXmlPath" /F
        if ($LASTEXITCODE -eq 0) {
            Write-SetupLog "✅ Task Scheduler job installed successfully"
        } else {
            throw "Failed to install Task Scheduler job: $result"
        }
        
        # Test execution if not test-only
        if (-not $TestOnly) {
            Write-SetupLog "🧪 Testing badge health monitor execution..."
            
            # Test PowerShell script
            & "C:\EQ12\scripts\badge_health_monitor.ps1" -TestMode
            if ($LASTEXITCODE -eq 0) {
                Write-SetupLog "✅ PowerShell script test passed"
            } else {
                Write-SetupLog "⚠️ PowerShell script test returned exit code: $LASTEXITCODE" -Level "WARN"
            }
            
            # Test task execution
            Write-SetupLog "🎯 Testing Task Scheduler execution..."
            schtasks /Run /TN "$taskName"
            Start-Sleep -Seconds 10  # Give task time to start
            
            $taskInfo = schtasks /Query /TN "$taskName" /FO CSV | ConvertFrom-Csv
            Write-SetupLog "📊 Task Status: $($taskInfo.'Last Result')"
        }
        
        Write-SetupLog "🎉 Badge Health Monitor installation completed successfully!"
        return $true
        
    } catch {
        Write-SetupLog "❌ Installation failed: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Show-SetupSummary {
    """Display setup summary and next steps."""
    Write-SetupLog ""
    Write-SetupLog "📊 EQ12 Badge Health Monitor Setup Summary"
    Write-SetupLog "=" * 50
    
    # Check task installation
    try {
        $taskInfo = schtasks /Query /TN "EQ12\Badge Health Monitor" /FO CSV 2>$null | ConvertFrom-Csv
        Write-SetupLog "📅 Task Scheduler: ✅ Installed"
        Write-SetupLog "   Next Run: $($taskInfo.'Next Run Time')"
        Write-SetupLog "   Status: $($taskInfo.Status)"
    } catch {
        Write-SetupLog "📅 Task Scheduler: ❌ Not installed"
    }
    
    # Check environment variables
    Write-SetupLog "🔧 Environment Variables:"
    $envVars = @("GITHUB_TOKEN", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
    foreach ($var in $envVars) {
        $value = [Environment]::GetEnvironmentVariable($var, "User")
        if ($value) {
            Write-SetupLog "   ✅ ${var}: Configured"
        } else {
            Write-SetupLog "   ❌ ${var}: Not configured"
        }
    }
    
    # Check files
    Write-SetupLog "📁 Required Files:"
    $files = @(
        "C:\EQ12\scripts\badge_health_monitor.py",
        "C:\EQ12\scripts\badge_health_monitor.ps1",
        "C:\EQ12\eq12_badge_health_monitor.xml",
        "C:\EQ12\README.md",
        "C:\EQ12\DASHBOARD.md"
    )
    
    foreach ($file in $files) {
        if (Test-Path $file) {
            Write-SetupLog "   ✅ $(Split-Path $file -Leaf)"
        } else {
            Write-SetupLog "   ❌ $(Split-Path $file -Leaf): Missing"
        }
    }
    
    Write-SetupLog ""
    Write-SetupLog "🚀 Next Steps:"
    Write-SetupLog "   1. Verify environment variables are set correctly"
    Write-SetupLog "   2. Test manual execution: C:\EQ12\scripts\badge_health_monitor.ps1 -TestMode"
    Write-SetupLog "   3. Force test alert: C:\EQ12\scripts\badge_health_monitor.ps1 -ForceAlert"
    Write-SetupLog "   4. Check logs: C:\EQ12\logs\badge-health-monitor.log"
    Write-SetupLog "   5. Monitor monthly execution on 1st of each month"
    Write-SetupLog ""
    Write-SetupLog "📱 Telegram Alerts:"
    Write-SetupLog "   • Monthly health reports (1st of each month)"
    Write-SetupLog "   • Immediate alerts for critical security issues"
    Write-SetupLog "   • Weekly status checks (every Sunday)"
    Write-SetupLog ""
    Write-SetupLog "🔒 Security Monitoring:"
    Write-SetupLog "   • GitHub Advanced Security workflow status"
    Write-SetupLog "   • CodeQL security analysis results"
    Write-SetupLog "   • Secret scanning and vulnerability alerts"
    Write-SetupLog "   • Repository security configuration"
    Write-SetupLog "   • EQ12 business stack compliance validation"
    Write-SetupLog ""
}

function Main {
    Write-SetupLog "🚀 EQ12 Badge Health Monitor Setup Starting"
    
    # Ensure logs directory
    $logsDir = "C:\EQ12\logs"
    if (-not (Test-Path $logsDir)) {
        New-Item -Path $logsDir -ItemType Directory -Force | Out-Null
        Write-SetupLog "📁 Created logs directory"
    }
    
    # Validate parameters
    if (-not $SetupEnvironment -and (-not $GitHubToken -or -not $TelegramBotToken -or -not $TelegramChatId)) {
        Write-SetupLog "⚠️ Environment variables not provided and -SetupEnvironment not specified" -Level "WARN"
        Write-SetupLog "   Run with -SetupEnvironment to configure, or set environment variables manually"
    }
    
    # Install badge health monitor
    $success = Install-BadgeHealthMonitor
    
    # Show summary
    Show-SetupSummary
    
    if ($success) {
        Write-SetupLog "✅ EQ12 Badge Health Monitor setup completed successfully!"
        return 0
    } else {
        Write-SetupLog "❌ Setup failed - check logs for details" -Level "ERROR"
        return 1
    }
}

# Execute main function
exit (Main)