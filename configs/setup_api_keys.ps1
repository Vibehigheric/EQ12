# EQ12 API Key Setup Script
# Run this script to set up your API keys as environment variables

Write-Host " EQ12 API Key Environment Setup" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# CRITICAL APIs (Required for core functionality)
Write-Host " Setting up CRITICAL APIs..." -ForegroundColor Yellow


# SportsData.io - Comprehensive sports statistics
# Get your key from: https://sportsdata.io/
# Example format: sd_1a2b3c4d5e6f7g8h9i0j1k2l3m4n
$env:SPORTSDATA_API_KEY = "YOUR_API_KEY_HERE"
[Environment]::SetEnvironmentVariable("SPORTSDATA_API_KEY", $env:SPORTSDATA_API_KEY, "User")
Write-Host " SPORTSDATA_API_KEY configured" -ForegroundColor Green

# Twitter API v2 - Social intelligence monitoring
# Get your key from: https://developer.twitter.com/
# Example format: AAAAAAAAAAAAAAAAAAAAAA%2FAA...
$env:TWITTER_API_KEY = "YOUR_API_KEY_HERE"
[Environment]::SetEnvironmentVariable("TWITTER_API_KEY", $env:TWITTER_API_KEY, "User")
Write-Host " TWITTER_API_KEY configured" -ForegroundColor Green

# IMPORTANT APIs (Enhanced functionality)
Write-Host " Setting up IMPORTANT APIs..." -ForegroundColor Yellow

# OpenWeatherMap - Weather data for sports analysis
# Get your key from: https://openweathermap.org/api
$env:OPENWEATHER_API_KEY = "YOUR_API_KEY_HERE"
[Environment]::SetEnvironmentVariable("OPENWEATHER_API_KEY", $env:OPENWEATHER_API_KEY, "User")
Write-Host " OPENWEATHER_API_KEY configured" -ForegroundColor Green

# OPTIONAL APIs (Additional features)
Write-Host " Setting up OPTIONAL APIs..." -ForegroundColor Yellow

# ESPN API - Real-time sports data
# Get your key from: https://site.api.espn.com/
$env:ESPN_API_KEY = "YOUR_API_KEY_HERE"
[Environment]::SetEnvironmentVariable("ESPN_API_KEY", $env:ESPN_API_KEY, "User")
Write-Host " ESPN_API_KEY configured" -ForegroundColor Green

Write-Host ""
Write-Host " API Key setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host " NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Replace 'YOUR_API_KEY_HERE' with your actual API keys" -ForegroundColor White
Write-Host "2. Run this script in PowerShell" -ForegroundColor White
Write-Host "3. Restart VS Code/PowerShell to load new variables" -ForegroundColor White
Write-Host "4. Test with: python eq12_api_key_manager.py --test-all" -ForegroundColor White
Write-Host ""
Write-Host " SECURITY NOTE:" -ForegroundColor Red
Write-Host "Keep your API keys secure and never commit them to version control!" -ForegroundColor Yellow
