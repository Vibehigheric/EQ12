# EQ12 Enhanced OpenWeatherMap Integration - PowerShell Wrapper
[CmdletBinding()]
param(
    [Parameter()]
    [string]$Action = "test-premium",
    
    [Parameter()]
    [string]$Team,
    
    [Parameter()]
    [string[]]$Teams,
    
    [Parameter()]
    [string]$ApiKey,
    
    [Parameter()]
    [switch]$AirQuality,
    
    [Parameter()]
    [switch]$WeatherAlerts,
    
    [Parameter()]
    [switch]$Verbose
)

# EQ12 Enhanced OpenWeatherMap Integration wrapper script
# Provides comprehensive weather intelligence with premium features

$ErrorActionPreference = 'Stop'

function Write-LogMessage {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    switch ($Level) {
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "WARNING" { Write-Host $logMessage -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logMessage -ForegroundColor Green }
        default { Write-Host $logMessage -ForegroundColor White }
    }
    
    # Log to file
    $logFile = "C:\EQ12\logs\premium_openweather_wrapper.log"
    Add-Content -Path $logFile -Value $logMessage -Encoding UTF8
}

function Test-PythonEnvironment {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found in PATH"
        }
        
        Write-LogMessage "Python environment detected: $pythonVersion"
        return $true
    }
    catch {
        Write-LogMessage "Python environment check failed: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Invoke-PremiumWeatherScript {
    param(
        [string[]]$Arguments
    )
    
    $scriptPath = "C:\EQ12\scripts\eq12_premium_openweather_integration.py"
    
    if (-not (Test-Path $scriptPath)) {
        Write-LogMessage "Premium OpenWeather script not found: $scriptPath" -Level "ERROR"
        return $false
    }
    
    try {
        Write-LogMessage "Executing premium weather analysis..."
        
        # Add API key if provided
        if ($ApiKey) {
            $Arguments += "--api-key", $ApiKey
        }
        
        # Execute Python script
        $result = python $scriptPath @Arguments 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "Premium weather analysis completed successfully" -Level "SUCCESS"
            Write-Output $result
            return $true
        }
        else {
            Write-LogMessage "Premium weather analysis failed with exit code: $LASTEXITCODE" -Level "ERROR"
            Write-Output $result
            return $false
        }
    }
    catch {
        Write-LogMessage "Exception during premium weather analysis: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

# Main execution
Write-LogMessage "EQ12 Enhanced OpenWeatherMap Integration started"
Write-Host ""
Write-Host "🌤️ EQ12 ENHANCED OPENWEATHERMAP INTEGRATION" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Validate Python environment
if (-not (Test-PythonEnvironment)) {
    Write-LogMessage "Python environment validation failed" -Level "ERROR"
    exit 1
}

# Prepare arguments based on action
$scriptArgs = @()

switch ($Action.ToLower()) {
    "test-premium" {
        Write-Host "🔍 Testing Premium API Access..." -ForegroundColor Yellow
        $scriptArgs = @("--test-premium")
    }
    
    "team-analysis" {
        if (-not $Team) {
            Write-LogMessage "Team parameter required for team analysis" -Level "ERROR"
            exit 1
        }
        
        Write-Host "🏈 Premium Team Weather Analysis: $Team" -ForegroundColor Green
        $scriptArgs = @("--team-premium", $Team)
    }
    
    "parlay-analysis" {
        if (-not $Teams -or $Teams.Count -eq 0) {
            Write-LogMessage "Teams parameter required for parlay analysis" -Level "ERROR"
            exit 1
        }
        
        Write-Host "🎯 Premium Parlay Weather Analysis: $($Teams -join ', ')" -ForegroundColor Green
        $scriptArgs = @("--parlay-premium") + $Teams
    }
    
    "air-quality" {
        if (-not $Team) {
            Write-LogMessage "Team parameter required for air quality analysis" -Level "ERROR"
            exit 1
        }
        
        Write-Host "🌫️ Air Quality Analysis: $Team" -ForegroundColor Magenta
        $scriptArgs = @("--air-quality", $Team)
    }
    
    "weather-alerts" {
        Write-Host "🚨 Checking Weather Alerts..." -ForegroundColor Red
        $scriptArgs = @("--weather-alerts")
    }
    
    "comprehensive" {
        Write-Host "🚀 Comprehensive Premium System Test..." -ForegroundColor Cyan
        $scriptArgs = @()  # Default behavior runs comprehensive test
    }
    
    default {
        Write-LogMessage "Unknown action: $Action" -Level "ERROR"
        Write-Host ""
        Write-Host "Available Actions:" -ForegroundColor Yellow
        Write-Host "  test-premium     - Test premium API access"
        Write-Host "  team-analysis    - Premium weather analysis for single team"
        Write-Host "  parlay-analysis  - Premium weather analysis for multiple teams"
        Write-Host "  air-quality      - Air quality analysis for team venue"
        Write-Host "  weather-alerts   - Check active weather alerts"
        Write-Host "  comprehensive    - Full system capability test"
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Cyan
        Write-Host "  eq12_premium_openweather_wrapper.ps1 -Action test-premium"
        Write-Host "  eq12_premium_openweather_wrapper.ps1 -Action team-analysis -Team 'Green Bay Packers'"
        Write-Host "  eq12_premium_openweather_wrapper.ps1 -Action parlay-analysis -Teams 'Green Bay Packers','Kansas City Chiefs'"
        Write-Host "  eq12_premium_openweather_wrapper.ps1 -Action air-quality -Team 'Buffalo Bills'"
        exit 1
    }
}

# Execute premium weather analysis
$success = Invoke-PremiumWeatherScript -Arguments $scriptArgs

if ($success) {
    Write-Host ""
    Write-LogMessage "Premium OpenWeatherMap integration completed successfully" -Level "SUCCESS"
    Write-Host "✅ Enhanced weather intelligence available!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Premium Features Active:" -ForegroundColor Cyan
    Write-Host "   • One Call API 3.0: Minute/hourly/daily forecasts + alerts" -ForegroundColor White
    Write-Host "   • Air Pollution API: Air quality impact analysis" -ForegroundColor White
    Write-Host "   • Global Weather Alerts: Severe weather monitoring" -ForegroundColor White
    Write-Host "   • Advanced Betting Intelligence: Multi-factor analysis" -ForegroundColor White
    Write-Host "   • Premium Stadium Database: 30+ NFL venues" -ForegroundColor White
    Write-Host ""
}
else {
    Write-LogMessage "Premium OpenWeatherMap integration failed" -Level "ERROR"
    Write-Host "❌ Integration failed. Check logs for details." -ForegroundColor Red
    exit 1
}

Write-Host "🎯 EQ12 Enhanced Weather Intelligence Ready!" -ForegroundColor Green