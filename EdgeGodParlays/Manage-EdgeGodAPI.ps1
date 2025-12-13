# EdgeGod API Management PowerShell Wrapper
# Manages The Odds API rate limiting, quota tracking, and optimization

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [ValidateSet("configure", "monitor", "test", "optimize", "status", "help")]
    [string]$Action = "status",
    
    [string]$ApiKey = $env:ODDS_API_KEY,
    [int]$MonitorHours = 1,
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Initialize logging
$LogPath = $env:EQ12_LOGS
if (!$LogPath) {
    $LogPath = "C:\EQ12\logs"
}

if (!(Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
}

$LogFile = Join-Path $LogPath "edgegod_api_management_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
}

function Test-Prerequisites {
    Write-Log "Checking prerequisites for EdgeGod API management..."
    
    # Check Python
    try {
        $PythonVersion = & python --version 2>&1
        Write-Log "Found Python: $PythonVersion"
    }
    catch {
        Write-Log "Python not found in PATH" -Level "ERROR"
        return $false
    }
    
    # Check if we're in EdgeGodParlays directory
    $ApiManagerScript = Join-Path $PSScriptRoot "api_manager.py"
    $ConfigScript = Join-Path $PSScriptRoot "configure_api.py"
    
    if (!(Test-Path $ApiManagerScript) -or !(Test-Path $ConfigScript)) {
        Write-Log "EdgeGod API scripts not found in current directory" -Level "ERROR"
        Write-Log "Please run from C:\EQ12\EdgeGodParlays directory" -Level "ERROR"
        return $false
    }
    
    # Check API key
    if (!$ApiKey) {
        Write-Log "API key not provided. Set ODDS_API_KEY environment variable or use -ApiKey parameter" -Level "WARNING"
        return $false
    }
    else {
        Write-Log "API key found (${($ApiKey.Length)} characters)"
    }
    
    Write-Log "Prerequisites check passed"
    return $true
}

function Invoke-APIConfiguration {
    Write-Log "Starting EdgeGod API configuration..."
    
    try {
        Set-Location $PSScriptRoot
        $env:ODDS_API_KEY = $ApiKey
        
        & python configure_api.py
        
        Write-Log "API configuration completed successfully"
    }
    catch {
        Write-Log "API configuration failed: $_" -Level "ERROR"
        throw
    }
}

function Invoke-APIMonitoring {
    param([int]$Hours = 1)
    
    Write-Log "Starting EdgeGod API monitoring for $Hours hour(s)..."
    
    try {
        Set-Location $PSScriptRoot
        $env:ODDS_API_KEY = $ApiKey
        
        # Create monitoring script
        $MonitorScript = @"
import asyncio
from api_manager import EdgeGodAPIManager
import json
from datetime import datetime
from pathlib import Path
import os

async def monitor():
    api_manager = EdgeGodAPIManager('$ApiKey')
    
    try:
        print(f"Starting API monitoring for $Hours hour(s)...")
        monitoring_data = await api_manager.monitor_quota_usage($Hours)
        
        # Save results
        logs_dir = Path(os.environ.get('EQ12_LOGS', './logs'))
        logs_dir.mkdir(exist_ok=True)
        
        monitor_file = logs_dir / f'api_monitoring_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(monitor_file, 'w') as f:
            json.dump(monitoring_data, f, indent=2)
        
        print(f"Monitoring complete. Results saved to: {monitor_file}")
        
        # Print summary
        if monitoring_data['samples']:
            last_sample = monitoring_data['samples'][-1]
            print(f"Final quota usage: {last_sample['quota_used']}")
            print(f"Total requests: {last_sample['requests_made']}")
            print(f"Cache hits: {last_sample['cache_hits']}")
    
    finally:
        await api_manager.close()

asyncio.run(monitor())
"@
        
        $TempScript = Join-Path $env:TEMP "edgegod_monitor.py"
        Set-Content -Path $TempScript -Value $MonitorScript -Encoding UTF8
        
        & python $TempScript
        
        Remove-Item $TempScript -Force -ErrorAction SilentlyContinue
        Write-Log "API monitoring completed successfully"
    }
    catch {
        Write-Log "API monitoring failed: $_" -Level "ERROR"
        throw
    }
}

function Test-APIEndpoints {
    Write-Log "Testing EdgeGod API endpoints..."
    
    try {
        Set-Location $PSScriptRoot
        $env:ODDS_API_KEY = $ApiKey
        
        # Create test script
        $TestScript = @"
import asyncio
from api_manager import EdgeGodAPIManager
import json

async def test_endpoints():
    api_manager = EdgeGodAPIManager('$ApiKey')
    
    try:
        print("🧪 Testing API endpoints...")
        
        # Health check
        health = await api_manager.health_check()
        print(f"Health Status: {health['status']}")
        
        if health['status'] == 'healthy':
            print(f"Response Time: {health['response_time_ms']}ms")
            print(f"Sports Available: {health['sports_available']}")
            
        # Usage stats
        stats = api_manager.get_usage_stats()
        print(f"\n📊 Current Usage:")
        print(f"  Total Requests: {stats['requests']['total']}")
        print(f"  Success Rate: {stats['requests']['success_rate']:.1f}%")
        print(f"  Daily Quota: {stats['quota']['daily_used']}/{stats['quota']['daily_limit']}")
        print(f"  Cache Hit Rate: {stats['cache']['hit_rate']:.1f}%")
        
        return health['status'] == 'healthy'
    
    finally:
        await api_manager.close()

result = asyncio.run(test_endpoints())
exit(0 if result else 1)
"@
        
        $TempScript = Join-Path $env:TEMP "edgegod_test.py"
        Set-Content -Path $TempScript -Value $TestScript -Encoding UTF8
        
        & python $TempScript
        $TestResult = $LASTEXITCODE -eq 0
        
        Remove-Item $TempScript -Force -ErrorAction SilentlyContinue
        
        if ($TestResult) {
            Write-Log "API endpoint tests passed"
        }
        else {
            Write-Log "API endpoint tests failed" -Level "ERROR"
        }
        
        return $TestResult
    }
    catch {
        Write-Log "API endpoint testing failed: $_" -Level "ERROR"
        throw
    }
}

function Get-APIStatus {
    Write-Log "Getting EdgeGod API status..."
    
    try {
        Set-Location $PSScriptRoot
        $env:ODDS_API_KEY = $ApiKey
        
        # Create status script
        $StatusScript = @"
import asyncio
from api_manager import EdgeGodAPIManager
from configure_api import EdgeGodAPIOptimizer
import json

async def get_status():
    api_manager = EdgeGodAPIManager('$ApiKey')
    optimizer = EdgeGodAPIOptimizer('$ApiKey')
    
    try:
        print("🎯 EdgeGod API Status Report")
        print("=" * 50)
        
        # Current usage analysis
        analysis = await optimizer.analyze_current_usage()
        
        print(f"API Status: {analysis['status'].upper()}")
        
        if 'efficiency_metrics' in analysis:
            metrics = analysis['efficiency_metrics']
            print(f"Cache Hit Rate: {metrics['cache_hit_rate']:.1f}%")
            print(f"Success Rate: {metrics['success_rate']:.1f}%")
            print(f"Quota Efficiency: {metrics['quota_efficiency']:.1f}%")
        
        # Current usage stats
        stats = api_manager.get_usage_stats()
        print(f"\n📊 Usage Statistics:")
        print(f"  Requests Today: {stats['requests']['total']}")
        print(f"  Daily Quota Used: {stats['quota']['daily_used']}/{stats['quota']['daily_limit']}")
        print(f"  Hourly Usage: {stats['quota']['hourly_used']}/50")
        print(f"  Cache Entries: {stats['cache']['entries']}")
        
        # Recommendations
        if analysis.get('recommendations'):
            print(f"\n💡 Recommendations:")
            for rec in analysis['recommendations']:
                priority_icon = {"critical": "🚨", "high": "⚠️", "medium": "ℹ️"}.get(rec['priority'], "💡")
                print(f"  {priority_icon} {rec['message']}")
        
        # Optimal schedule
        schedule_type = analysis.get('optimal_schedule', 'moderate')
        print(f"\n📅 Recommended Schedule: {schedule_type.upper()}")
        
        return analysis['status'] == 'healthy'
    
    finally:
        await api_manager.close()

result = asyncio.run(get_status())
exit(0 if result else 1)
"@
        
        $TempScript = Join-Path $env:TEMP "edgegod_status.py"
        Set-Content -Path $TempScript -Value $StatusScript -Encoding UTF8
        
        & python $TempScript
        $StatusResult = $LASTEXITCODE -eq 0
        
        Remove-Item $TempScript -Force -ErrorAction SilentlyContinue
        
        if ($StatusResult) {
            Write-Log "API status check completed successfully"
        }
        else {
            Write-Log "API status check indicated issues" -Level "WARNING"
        }
        
        return $StatusResult
    }
    catch {
        Write-Log "API status check failed: $_" -Level "ERROR"
        throw
    }
}

function Show-Usage {
    Write-Host @"
EdgeGod API Management PowerShell Wrapper

Usage: .\Manage-EdgeGodAPI.ps1 -Action <action> [options]

Actions:
  configure    Run full API configuration and optimization
  monitor      Monitor API quota usage over time
  test         Test API endpoints and connectivity
  optimize     Analyze and optimize API usage patterns
  status       Show current API status and recommendations
  help         Show this help message

Options:
  -ApiKey <key>        Specify API key (or set ODDS_API_KEY env var)
  -MonitorHours <n>    Hours to monitor (default: 1)
  -Verbose            Enable verbose logging
  -Force              Force operations even if warnings exist

Examples:
  .\Manage-EdgeGodAPI.ps1 -Action status
  .\Manage-EdgeGodAPI.ps1 -Action configure -ApiKey "your-api-key"
  .\Manage-EdgeGodAPI.ps1 -Action monitor -MonitorHours 4
  .\Manage-EdgeGodAPI.ps1 -Action test -Verbose

Environment Variables:
  ODDS_API_KEY         The Odds API key
  EQ12_LOGS           Log directory (default: C:\EQ12\logs)

For detailed API management, see:
  - api_manager.py: Core rate limiting and quota management
  - configure_api.py: Configuration and optimization utility
"@
}

# Main execution
try {
    Write-Log "EdgeGod API Management started with action: $Action"
    
    if ($Action -eq "help") {
        Show-Usage
        exit 0
    }
    
    if (!(Test-Prerequisites)) {
        exit 1
    }
    
    switch ($Action) {
        "configure" {
            Invoke-APIConfiguration
        }
        
        "monitor" {
            Invoke-APIMonitoring -Hours $MonitorHours
        }
        
        "test" {
            $TestResult = Test-APIEndpoints
            if (!$TestResult) {
                exit 1
            }
        }
        
        "optimize" {
            # Same as configure for now
            Invoke-APIConfiguration
        }
        
        "status" {
            $StatusResult = Get-APIStatus
            if (!$StatusResult) {
                exit 1
            }
        }
        
        default {
            Write-Log "Unknown action: $Action" -Level "ERROR"
            Show-Usage
            exit 1
        }
    }
    
    Write-Log "EdgeGod API management completed successfully"
}
catch {
    Write-Log "EdgeGod API management failed: $_" -Level "ERROR"
    exit 1
}
finally {
    Write-Log "Log saved to: $LogFile"
}