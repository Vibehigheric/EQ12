# EQ12 GitHub Models Environment Setup
# Generated: 2025-10-07T04:27:12.655957+00:00
# Token expires: 2025-11-06
# MCP deadline: 2025-11-10

Write-Host "🔐 Setting up GitHub Models environment for EQ12..." -ForegroundColor Green

# Set GitHub Models token (if not already set)
if (-not $env:GITHUB_MODELS_TOKEN) {
    Write-Host "⚠️  GITHUB_MODELS_TOKEN not found in environment" -ForegroundColor Yellow
    Write-Host "📋 To set the token, run:" -ForegroundColor Yellow
    Write-Host '   $env:GITHUB_MODELS_TOKEN = "your_token_here"' -ForegroundColor Cyan
    Write-Host "🔒 Or store securely using: python C:\EQ12\scripts\github_models_integration.py" -ForegroundColor Cyan
} else {
    Write-Host "✅ GITHUB_MODELS_TOKEN found in environment" -ForegroundColor Green
}

# Validate token expiration
$tokenExpires = [datetime]::Parse("2025-11-06")
$daysLeft = ($tokenExpires - (Get-Date)).Days

if ($daysLeft -le 7) {
    Write-Host "🚨 URGENT: GitHub Models token expires in $daysLeft days!" -ForegroundColor Red
    Write-Host "🔄 Renew token at: https://github.com/settings/tokens" -ForegroundColor Red
} elseif ($daysLeft -le 30) {
    Write-Host "⚠️  GitHub Models token expires in $daysLeft days" -ForegroundColor Yellow
} else {
    Write-Host "📅 GitHub Models token expires in $daysLeft days" -ForegroundColor Green
}

# MCP migration deadline warning
$mcpDeadline = [datetime]::Parse("2025-11-10")
$mcpDaysLeft = ($mcpDeadline - (Get-Date)).Days

Write-Host "🔄 MCP migration deadline in $mcpDaysLeft days (2025-11-10)" -ForegroundColor $(if ($mcpDaysLeft -le 7) {"Red"} else {"Yellow"})

# Test GitHub Models connection
Write-Host "🧪 Testing GitHub Models connection..." -ForegroundColor Blue
python -c "
import sys
sys.path.append('C:\\EQ12\\scripts')
from github_models_integration import GitHubModelsManager
import asyncio

async def test():
    manager = GitHubModelsManager()
    result = await manager.test_github_models_connection()
    if result['success']:
        print('✅ GitHub Models connection successful')
        print(f'📊 Models available: {result.get("models_available", "unknown")}')
    else:
        print(f'❌ Connection failed: {result.get("error", "unknown error")}')

asyncio.run(test())
"

Write-Host "🚀 GitHub Models environment setup complete!" -ForegroundColor Green
Write-Host "📚 Next: Run Install-EQ12MCP.ps1 to complete MCP migration setup" -ForegroundColor Cyan
