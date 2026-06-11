# EQ12 API Keys Secure Setup - Complete Con# Test API Key Status
Write-Host "`n🔍 API Keys Status Check:" -ForegroundColor Yellow
if ($env:GROQ_API_KEY) { Write-Host "GROQ_API_KEY: SET ✅" -ForegroundColor Green } else { Write-Host "GROQ_API_KEY: NOT SET ❌" -ForegroundColor Red }
if ($env:OPENAI_API_KEY) { Write-Host "OPENAI_API_KEY: SET ✅" -ForegroundColor Green } else { Write-Host "OPENAI_API_KEY: NOT SET ❌" -ForegroundColor Red }
if ($env:THE_ODDS_API_KEY) { Write-Host "THE_ODDS_API_KEY: SET ✅" -ForegroundColor Green } else { Write-Host "THE_ODDS_API_KEY: NOT SET ❌" -ForegroundColor Red }
if ($env:TELEGRAM_BOT_TOKEN) { Write-Host "TELEGRAM_BOT_TOKEN: SET ✅" -ForegroundColor Green } else { Write-Host "TELEGRAM_BOT_TOKEN: NOT SET ❌" -ForegroundColor Red }
if ($env:GITHUB_TOKEN) { Write-Host "GITHUB_TOKEN: SET ✅" -ForegroundColor Green } else { Write-Host "GITHUB_TOKEN: NOT SET ❌" -ForegroundColor Red }
if ($env:GITLENS_KEY) { Write-Host "GITLENS_KEY: SET ✅" -ForegroundColor Green } else { Write-Host "GITLENS_KEY: NOT SET ❌" -ForegroundColor Red }ion
# ==================================================

[CmdletBinding()]
param()

Write-Host "🔑 EQ12 API Keys Setup - Secure Configuration" -ForegroundColor Green
Write-Host "Setting up environment variables for EQ12 betting automation..." -ForegroundColor Cyan

# Set environment variables securely
Write-Host "📝 Configuring environment variables..." -ForegroundColor Yellow

# AI Services
$env:GROQ_API_KEY = "GROQ_API_KEY_PLACEHOLDER"
[Environment]::SetEnvironmentVariable("GROQ_API_KEY", $env:GROQ_API_KEY, "User")

$env:OPENAI_API_KEY = "OPENAI_API_KEY_PLACEHOLDER"
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $env:OPENAI_API_KEY, "User")

# Sports Data
$env:THE_ODDS_API_KEY = "ODDS_API_KEY_PLACEHOLDER"
[Environment]::SetEnvironmentVariable("THE_ODDS_API_KEY", $env:THE_ODDS_API_KEY, "User")

# Communication
$env:TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN_PLACEHOLDER"
$env:TELEGRAM_CHAT_ID = "5475370304"
[Environment]::SetEnvironmentVariable("TELEGRAM_BOT_TOKEN", $env:TELEGRAM_BOT_TOKEN, "User")
[Environment]::SetEnvironmentVariable("TELEGRAM_CHAT_ID", $env:TELEGRAM_CHAT_ID, "User")

# GitHub Integration
$env:GITHUB_TOKEN = "GITHUB_PAT_PLACEHOLDER"
[Environment]::SetEnvironmentVariable("GITHUB_TOKEN", $env:GITHUB_TOKEN, "User")

# Development Tools
$env:GITLENS_KEY = "GITLENS_KEY_PLACEHOLDER"
[Environment]::SetEnvironmentVariable("GITLENS_KEY", $env:GITLENS_KEY, "User")

# EQ12 Configuration
$env:EQ12_ENVIRONMENT = "development"
[Environment]::SetEnvironmentVariable("EQ12_ENVIRONMENT", $env:EQ12_ENVIRONMENT, "User")

Write-Host "✅ All API keys configured successfully!" -ForegroundColor Green

# Test API Key Status
Write-Host "`n� API Keys Status Check:" -ForegroundColor Yellow
Write-Host "GROQ_API_KEY: $(if($env:GROQ_API_KEY) { 'SET ✅' } else { 'NOT SET ❌' })" -ForegroundColor $(if($env:GROQ_API_KEY) { 'Green' } else { 'Red' })
Write-Host "OPENAI_API_KEY: $(if($env:OPENAI_API_KEY) { 'SET ✅' } else { 'NOT SET ❌' })" -ForegroundColor $(if($env:OPENAI_API_KEY) { 'Green' } else { 'Red' })
Write-Host "THE_ODDS_API_KEY: $(if($env:THE_ODDS_API_KEY) { 'SET ✅' } else { 'NOT SET ❌' })" -ForegroundColor $(if($env:THE_ODDS_API_KEY) { 'Green' } else { 'Red' })
Write-Host "TELEGRAM_BOT_TOKEN: $(if($env:TELEGRAM_BOT_TOKEN) { 'SET ✅' } else { 'NOT SET ❌' })" -ForegroundColor $(if($env:TELEGRAM_BOT_TOKEN) { 'Green' } else { 'Red' })
Write-Host "GITHUB_TOKEN: $(if($env:GITHUB_TOKEN) { 'SET ✅' } else { 'NOT SET ❌' })" -ForegroundColor $(if($env:GITHUB_TOKEN) { 'Green' } else { 'Red' })

Write-Host "`n🎉 SETUP COMPLETE!" -ForegroundColor Green
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Restart your terminal to reload environment variables" -ForegroundColor White
Write-Host "2. Run: python smoke_test.py" -ForegroundColor White
Write-Host "3. Test Telegram notifications with any EQ12 script" -ForegroundColor White
Write-Host "4. Add these keys to GitHub Secrets for CI/CD automation" -ForegroundColor White
Write-Host "`n⚠️  SECURITY REMINDER:" -ForegroundColor Red
Write-Host "- .env file is gitignored (safe from commits)" -ForegroundColor Yellow
Write-Host "- Never commit API keys to version control" -ForegroundColor Yellow
Write-Host "- Use GitHub repository secrets for CI/CD pipelines" -ForegroundColor Yellow
Write-Host "4. Run live scanner: python eq12_live_parlay_scanner.py --once"
