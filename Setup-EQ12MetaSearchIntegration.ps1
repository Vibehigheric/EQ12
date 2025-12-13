#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Meta-Search Integration Setup - Combines existing meta-search with Bing intelligence suite

.DESCRIPTION
    This script sets up the complete EQ12 meta-search integration system that combines:
    - Existing C:\EQ12\eq12_meta_search system (Bing + Google search)
    - New Bing intelligence suite (stack-specific AI modules)
    - Unified search controller with intelligent query routing
    - Integration with existing EQ12 automation systems

.AUTHOR
    EQ12 AI Assistant

.DATE
    2025-01-27
#>

[CmdletBinding()]
param(
    [Parameter(HelpMessage = "Skip dependency installation")]
    [switch]$SkipDependencies,
    
    [Parameter(HelpMessage = "Skip Task Scheduler setup")]
    [switch]$SkipScheduler,
    
    [Parameter(HelpMessage = "Test mode - setup without running")]
    [switch]$TestMode,
    
    [Parameter(HelpMessage = "Force reinstall even if components exist")]
    [switch]$Force,
    
    [Parameter(HelpMessage = "Enable verbose logging")]
    [switch]$Verbose
)

# EQ12 standard error handling
$ErrorActionPreference = "Stop"
Set-StrictMode -Version 3.0

# EQ12 paths
$EQ12Root = "C:\EQ12"
$LogsDir = "$EQ12Root\logs"
$KeysDir = "$EQ12Root\keys"
$MetaSearchDir = "$EQ12Root\eq12_meta_search"
$BingIntelDir = "$EQ12Root\bing_intelligence"

# Ensure directories exist
@($LogsDir, $KeysDir, $MetaSearchDir, $BingIntelDir) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -Path $_ -ItemType Directory -Force | Out-Null
    }
}

# Setup logging
$LogFile = "$LogsDir\eq12_metasearch_setup_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-EQ12Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Console output with colors
    switch ($Level) {
        "INFO"    { Write-Host $logEntry -ForegroundColor White }
        "WARN"    { Write-Host $logEntry -ForegroundColor Yellow }
        "ERROR"   { Write-Host $logEntry -ForegroundColor Red }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
    }
    
    # File output
    Add-Content -Path $LogFile -Value $logEntry
}

function Test-EQ12Prerequisites {
    [CmdletBinding()]
    param()
    
    Write-EQ12Log "Checking EQ12 meta-search integration prerequisites..." "INFO"
    
    $checks = @()
    
    # Python availability
    try {
        $pythonVersion = & python --version 2>&1
        if ($pythonVersion -match "Python 3\.([8-9]|1[0-9])") {
            $checks += @{ Name = "Python 3.8+"; Status = "✅"; Details = $pythonVersion }
        } else {
            $checks += @{ Name = "Python 3.8+"; Status = "❌"; Details = "Python 3.8+ required, found: $pythonVersion" }
        }
    } catch {
        $checks += @{ Name = "Python 3.8+"; Status = "❌"; Details = "Python not found in PATH" }
    }
    
    # Existing meta-search system
    if (Test-Path "$MetaSearchDir\meta_search.py") {
        $checks += @{ Name = "Existing Meta-Search"; Status = "✅"; Details = "Found at $MetaSearchDir" }
    } else {
        $checks += @{ Name = "Existing Meta-Search"; Status = "❌"; Details = "Missing meta_search.py" }
    }
    
    # Bing intelligence suite
    if (Test-Path "$BingIntelDir\core\bing_web_search.py") {
        $checks += @{ Name = "Bing Intelligence Suite"; Status = "✅"; Details = "Found at $BingIntelDir" }
    } else {
        $checks += @{ Name = "Bing Intelligence Suite"; Status = "❌"; Details = "Missing Bing intelligence modules" }
    }
    
    # Required API keys
    $requiredKeys = @("BING_KEY", "GOOGLE_KEY", "GOOGLE_CSE_ID")
    foreach ($key in $requiredKeys) {
        if ([System.Environment]::GetEnvironmentVariable($key) -or (Test-Path "$KeysDir\$key.txt")) {
            $checks += @{ Name = "$key"; Status = "✅"; Details = "Available" }
        } else {
            $checks += @{ Name = "$key"; Status = "⚠️"; Details = "Missing (optional)" }
        }
    }
    
    # Telegram keys (optional)
    $telegramKeys = @("TG_TOKEN", "TG_CHAT_ID", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
    $telegramAvailable = $false
    foreach ($key in $telegramKeys) {
        if ([System.Environment]::GetEnvironmentVariable($key) -or (Test-Path "$KeysDir\$key.txt")) {
            $telegramAvailable = $true
            break
        }
    }
    
    if ($telegramAvailable) {
        $checks += @{ Name = "Telegram Integration"; Status = "✅"; Details = "Keys available" }
    } else {
        $checks += @{ Name = "Telegram Integration"; Status = "⚠️"; Details = "No Telegram keys (optional)" }
    }
    
    # Display results
    Write-Host "`n📋 Prerequisites Check:" -ForegroundColor Cyan
    foreach ($check in $checks) {
        Write-Host "  $($check.Status) $($check.Name): $($check.Details)"
    }
    
    $failedChecks = $checks | Where-Object { $_.Status -eq "❌" }
    if ($failedChecks.Count -gt 0) {
        Write-EQ12Log "Failed prerequisite checks: $($failedChecks.Count)" "ERROR"
        return $false
    }
    
    Write-EQ12Log "All critical prerequisites met" "SUCCESS"
    return $true
}

function Install-EQ12MetaSearchDependencies {
    [CmdletBinding()]
    param()
    
    Write-EQ12Log "Installing EQ12 meta-search integration dependencies..." "INFO"
    
    try {
        # Check if virtual environment exists
        $venvPath = "$MetaSearchDir\.venv"
        if (-not (Test-Path $venvPath) -or $Force) {
            Write-EQ12Log "Creating Python virtual environment..." "INFO"
            Push-Location $MetaSearchDir
            
            & python -m venv .venv
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to create virtual environment"
            }
            
            Pop-Location
        }
        
        # Install requirements
        $activateScript = "$venvPath\Scripts\Activate.ps1"
        if (Test-Path $activateScript) {
            Write-EQ12Log "Installing Python packages..." "INFO"
            
            & $activateScript
            
            # Install basic meta-search requirements
            $basicRequirements = @(
                "requests>=2.28.0",
                "python-telegram-bot>=20.0",
                "sqlite3"  # Built into Python but ensure it's available
            )
            
            foreach ($package in $basicRequirements) {
                Write-EQ12Log "Installing $package..." "INFO"
                & python -m pip install $package --quiet
            }
            
            # Install enhanced requirements if Bing intelligence is available
            if (Test-Path "$BingIntelDir\requirements.txt") {
                Write-EQ12Log "Installing Bing intelligence requirements..." "INFO"
                & python -m pip install -r "$BingIntelDir\requirements.txt" --quiet
            }
            
            Write-EQ12Log "Python dependencies installed successfully" "SUCCESS"
        } else {
            throw "Virtual environment activation script not found"
        }
        
    } catch {
        Write-EQ12Log "Failed to install dependencies: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Initialize-EQ12MetaSearchDatabase {
    [CmdletBinding()]
    param()
    
    Write-EQ12Log "Initializing enhanced meta-search database..." "INFO"
    
    try {
        $pythonScript = @"
import sys
sys.path.insert(0, r'$EQ12Root\eq12_meta_search')
from enhanced_db import init_enhanced_db, migrate_from_legacy
print('Initializing enhanced database...')
init_enhanced_db()
print('Migrating legacy data...')
migrate_from_legacy()
print('Database initialization completed successfully')
"@
        
        $scriptFile = "$env:TEMP\eq12_init_db.py"
        Set-Content -Path $scriptFile -Value $pythonScript -Encoding UTF8
        
        Push-Location $MetaSearchDir
        & .\.venv\Scripts\python.exe $scriptFile
        Pop-Location
        
        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "Database initialized successfully" "SUCCESS"
        } else {
            throw "Database initialization failed with exit code $LASTEXITCODE"
        }
        
    } catch {
        Write-EQ12Log "Database initialization failed: $($_.Exception.Message)" "ERROR"
        throw
    } finally {
        if (Test-Path $scriptFile) {
            Remove-Item $scriptFile -Force
        }
    }
}

function Test-EQ12MetaSearchIntegration {
    [CmdletBinding()]
    param()
    
    Write-EQ12Log "Testing EQ12 meta-search integration components..." "INFO"
    
    $testResults = @()
    
    try {
        # Test unified search controller
        Write-EQ12Log "Testing unified search controller..." "INFO"
        $testScript = @"
import sys
sys.path.insert(0, r'$EQ12Root')
from eq12_unified_search import EQ12UnifiedSearch
searcher = EQ12UnifiedSearch()
result = searcher.search_unified('test query sports betting', count=3, use_intelligence=False)
print(f'Unified search test: {len(result.get("meta_search_results", [])) + len(result.get("google_results", []))} results')
"@
        
        $result = Invoke-EQ12PythonTest -Script $testScript -TestName "Unified Search"
        $testResults += $result
        
        # Test intelligent router
        Write-EQ12Log "Testing intelligent query router..." "INFO"
        $routerScript = @"
import sys
sys.path.insert(0, r'$EQ12Root')
from eq12_intelligent_router import EQ12QueryRouter
router = EQ12QueryRouter()
matches = router.analyze_query('Buffalo Bills injury report tonight')
print(f'Router test: Detected {matches[0].stack if matches else "none"} with {matches[0].confidence:.3f} confidence')
"@
        
        $result = Invoke-EQ12PythonTest -Script $routerScript -TestName "Query Router"
        $testResults += $result
        
        # Test automation bridge
        Write-EQ12Log "Testing automation bridge..." "INFO"
        $bridgeScript = @"
import sys
sys.path.insert(0, r'$EQ12Root')
from eq12_automation_bridge import EQ12AutomationBridge
bridge = EQ12AutomationBridge(enable_intelligence=False)
status = bridge.get_system_status()
print(f'Bridge test: {sum(status["components"].values())} of {len(status["components"])} components ready')
"@
        
        $result = Invoke-EQ12PythonTest -Script $bridgeScript -TestName "Automation Bridge"
        $testResults += $result
        
    } catch {
        Write-EQ12Log "Integration testing failed: $($_.Exception.Message)" "ERROR"
        throw
    }
    
    # Display results
    Write-Host "`n🧪 Integration Test Results:" -ForegroundColor Cyan
    foreach ($test in $testResults) {
        $status = if ($test.Success) { "✅" } else { "❌" }
        Write-Host "  $status $($test.Name): $($test.Details)"
    }
    
    $failedTests = $testResults | Where-Object { -not $_.Success }
    if ($failedTests.Count -gt 0) {
        Write-EQ12Log "Failed integration tests: $($failedTests.Count)" "ERROR"
        return $false
    }
    
    Write-EQ12Log "All integration tests passed" "SUCCESS"
    return $true
}

function Invoke-EQ12PythonTest {
    param(
        [string]$Script,
        [string]$TestName
    )
    
    try {
        $scriptFile = "$env:TEMP\eq12_test_$([System.Guid]::NewGuid().ToString('N')[0..7] -join '').py"
        Set-Content -Path $scriptFile -Value $Script -Encoding UTF8
        
        Push-Location $MetaSearchDir
        $output = & .\.venv\Scripts\python.exe $scriptFile 2>&1
        Pop-Location
        
        if ($LASTEXITCODE -eq 0) {
            return @{ Name = $TestName; Success = $true; Details = $output -join '; ' }
        } else {
            return @{ Name = $TestName; Success = $false; Details = "Exit code: $LASTEXITCODE, Output: $($output -join '; ')" }
        }
        
    } catch {
        return @{ Name = $TestName; Success = $false; Details = $_.Exception.Message }
    } finally {
        if (Test-Path $scriptFile) {
            Remove-Item $scriptFile -Force -ErrorAction SilentlyContinue
        }
    }
}

function New-EQ12MetaSearchScheduledTasks {
    [CmdletBinding()]
    param()
    
    Write-EQ12Log "Setting up EQ12 meta-search scheduled tasks..." "INFO"
    
    try {
        # Daily maintenance task
        $maintenanceTaskName = "EQ12_MetaSearch_Daily_Maintenance"
        $maintenanceCmd = "$MetaSearchDir\.venv\Scripts\python.exe"
        $maintenanceArgs = "`"$EQ12Root\eq12_automation_bridge.py`" maintenance"
        
        # Check if task already exists
        $existingTask = Get-ScheduledTask -TaskName $maintenanceTaskName -ErrorAction SilentlyContinue
        if ($existingTask -and -not $Force) {
            Write-EQ12Log "Maintenance task already exists, skipping..." "WARN"
        } else {
            if ($existingTask) {
                Unregister-ScheduledTask -TaskName $maintenanceTaskName -Confirm:$false
            }
            
            $action = New-ScheduledTaskAction -Execute $maintenanceCmd -Argument $maintenanceArgs -WorkingDirectory $EQ12Root
            $trigger = New-ScheduledTaskTrigger -Daily -At "06:00"
            $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
            $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
            
            Register-ScheduledTask -TaskName $maintenanceTaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "EQ12 Meta-Search daily maintenance and analytics"
            
            Write-EQ12Log "Daily maintenance task created: $maintenanceTaskName" "SUCCESS"
        }
        
        # Hourly integration test task
        $testTaskName = "EQ12_MetaSearch_Hourly_HealthCheck"
        $testCmd = "$MetaSearchDir\.venv\Scripts\python.exe"
        $testArgs = "`"$EQ12Root\eq12_automation_bridge.py`" status"
        
        $existingTestTask = Get-ScheduledTask -TaskName $testTaskName -ErrorAction SilentlyContinue
        if ($existingTestTask -and -not $Force) {
            Write-EQ12Log "Health check task already exists, skipping..." "WARN"
        } else {
            if ($existingTestTask) {
                Unregister-ScheduledTask -TaskName $testTaskName -Confirm:$false
            }
            
            $testAction = New-ScheduledTaskAction -Execute $testCmd -Argument $testArgs -WorkingDirectory $EQ12Root
            $testTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)
            $testPrincipal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
            $testSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
            
            Register-ScheduledTask -TaskName $testTaskName -Action $testAction -Trigger $testTrigger -Principal $testPrincipal -Settings $testSettings -Description "EQ12 Meta-Search hourly health check"
            
            Write-EQ12Log "Hourly health check task created: $testTaskName" "SUCCESS"
        }
        
        Write-EQ12Log "Scheduled tasks setup completed" "SUCCESS"
        
    } catch {
        Write-EQ12Log "Failed to create scheduled tasks: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Show-EQ12MetaSearchUsage {
    [CmdletBinding()]
    param()
    
    Write-Host @"

🔍 EQ12 Meta-Search Integration - Usage Guide
=============================================

The integrated system combines existing meta-search with Bing intelligence:

Basic Usage:
------------
# Unified search (combines meta-search + intelligence)
python eq12_unified_search.py --query "Buffalo Bills injury report"

# Force specific stack
python eq12_unified_search.py --query "stock market analysis" --stack finance

# Intelligence-only search
python eq12_unified_search.py --query "cannabis dispensary buffalo" --stack-only --stack cannabis

# Send Telegram alerts
python eq12_unified_search.py --query "flight deals buffalo to lax" --telegram

Automation Integration:
----------------------
# Godmode Runner integration
python eq12_automation_bridge.py test-godmode "team injury updates" sports

# Elite Runner integration  
python eq12_automation_bridge.py test-elite stocks

# System status check
python eq12_automation_bridge.py status

Query Routing:
-------------
# Test intelligent routing
python eq12_intelligent_router.py "Buffalo dispensary near me" --explain

Advanced Usage:
--------------
# Batch queries from file
python eq12_unified_search.py --query-file queries.txt --telegram

# JSON output for automation
python eq12_unified_search.py --query "crypto market" --json-output

# History only (no new search)
python eq12_unified_search.py --query "previous search" --history-only

Key Integration Points:
----------------------
✅ Backward compatible with existing meta-search
✅ Intelligent stack detection and routing
✅ Enhanced database with analytics
✅ Automation system integration
✅ Scheduled maintenance and health checks
✅ Telegram alert integration

Configuration:
-------------
Set environment variables or place in C:\EQ12\keys\:
- BING_KEY: Azure Bing Search API key
- GOOGLE_KEY: Google Custom Search API key  
- GOOGLE_CSE_ID: Google Custom Search Engine ID
- TG_TOKEN / TELEGRAM_BOT_TOKEN: Telegram bot token
- TG_CHAT_ID / TELEGRAM_CHAT_ID: Telegram chat ID

Logs and Data:
-------------
- Logs: C:\EQ12\logs\
- Database: C:\EQ12\eq12_meta_search\meta_search_enhanced.sqlite3
- Snapshots: C:\EQ12\logs\eq12_search_snapshots_*.jsonl

"@ -ForegroundColor Green
}

# Main execution
function Main {
    Write-Host @"
🔍 EQ12 Meta-Search Integration Setup
=====================================
Combining existing meta-search with Bing intelligence suite
"@ -ForegroundColor Cyan
    
    Write-EQ12Log "Starting EQ12 meta-search integration setup..." "INFO"
    
    try {
        # Prerequisites check
        if (-not (Test-EQ12Prerequisites)) {
            throw "Prerequisites check failed - please resolve issues above"
        }
        
        # Install dependencies
        if (-not $SkipDependencies) {
            Install-EQ12MetaSearchDependencies
        } else {
            Write-EQ12Log "Skipping dependency installation" "WARN"
        }
        
        # Initialize database
        Initialize-EQ12MetaSearchDatabase
        
        # Test integration
        if (-not $TestMode) {
            Test-EQ12MetaSearchIntegration
        } else {
            Write-EQ12Log "Test mode - skipping integration tests" "WARN"
        }
        
        # Setup scheduled tasks
        if (-not $SkipScheduler -and -not $TestMode) {
            New-EQ12MetaSearchScheduledTasks
        } else {
            Write-EQ12Log "Skipping Task Scheduler setup" "WARN"
        }
        
        Write-EQ12Log "EQ12 meta-search integration setup completed successfully!" "SUCCESS"
        
        # Show usage information
        Show-EQ12MetaSearchUsage
        
        return 0
        
    } catch {
        Write-EQ12Log "Setup failed: $($_.Exception.Message)" "ERROR"
        Write-Host "`nFor detailed logs, check: $LogFile" -ForegroundColor Yellow
        return 1
    }
}

# Execute main function
exit (Main)