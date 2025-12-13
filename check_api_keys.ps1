#!/usr/bin/env powershell
<#
EQ12 API Keys Setup and Verification
===================================
#>

Write-Host "API Keys Status Check" -ForegroundColor Green
Write-Host "===================="

# Check OpenAI API Key
if ($env:OPENAI_API_KEY) {
    Write-Host "OPENAI_API_KEY: SET (for AI explanations)" -ForegroundColor Green
} else {
    Write-Host "OPENAI_API_KEY: NOT SET" -ForegroundColor Red
}

# Check Odds API Key
if ($env:ODDS_API_KEY) {
    Write-Host "ODDS_API_KEY: SET (for live betting data)" -ForegroundColor Green
} else {
    Write-Host "ODDS_API_KEY: NOT SET - NEEDED for live data" -ForegroundColor Yellow
}

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "1. Get sports odds API key from: https://theoddsapi.com"
Write-Host "2. Sign up for free account (500 requests/month)"
Write-Host "3. Copy your API key from dashboard"
Write-Host "4. Run: setx ODDS_API_KEY `"paste_your_key_here`""
Write-Host "5. Restart terminal and test with: python eq12_real_odds_connector.py"

Write-Host "`nSecurity Note:" -ForegroundColor Red
Write-Host "- The key you provided is OpenAI (for AI), not sports odds"
Write-Host "- You need a separate API key for sports betting data"
Write-Host "- Never share API keys in messages or commits"

Write-Host "`nReady to test?" -ForegroundColor Green
Write-Host "python eq12_live_parlay_scanner.py --once --stake 8 --roi 10"
