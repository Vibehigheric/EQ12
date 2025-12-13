#!/usr/bin/env powershell
<#
.SYNOPSIS
    Bootstrap script for EQ12 OpsBot - creates complete production setup

.DESCRIPTION
    This script sets up the EQ12 OpsBot environment including:
    - Python virtual environment with dependencies
    - Configuration files and directories
    - VS Code integration and tasks
    - Windows service registration (optional)
    - First-run initialization

.PARAMETER SetupService
    Register OpsBot as Windows service using NSSM

.PARAMETER SkipVenv
    Skip virtual environment creation (use existing)

.PARAMETER ConfigOnly
    Only create configuration files, skip installation

.EXAMPLE
    .\bootstrap_opsbot.ps1
    .\bootstrap_opsbot.ps1 -SetupService
    .\bootstrap_opsbot.ps1 -ConfigOnly

.NOTES
    Author: EQ12 GODSTACK
    Requires: PowerShell 5.1+, Python 3.12+
#>

[CmdletBinding()]
param(
    [switch]$SetupService,
    [switch]$SkipVenv,
    [switch]$ConfigOnly
)

# EQ12 standard error handling
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# ANSI colors for output
$Colors = @{
    Reset   = "`e[0m"
    Red     = "`e[31m"
    Green   = "`e[32m"
    Yellow  = "`e[33m"
    Blue    = "`e[34m"
    Magenta = "`e[35m"
    Cyan    = "`e[36m"
    Bold    = "`e[1m"
}

function Write-ColorOutput {
    param(
        [Parameter(Mandatory)]
        [string]$Message,
        [string]$Color = "Reset"
    )

    if ($Colors.ContainsKey($Color)) {
        Write-Host "$($Colors[$Color])$Message$($Colors.Reset)"
    }
    else {
        Write-Host $Message
    }
}

function Test-Prerequisites {
    Write-ColorOutput "🔍 Checking prerequisites..." -Color "Blue"

    # Check Python 3.12+
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]

            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 12)) {
                throw "Python 3.12+ required, found: $pythonVersion"
            }
            Write-ColorOutput "✅ $pythonVersion" -Color "Green"
        }
    }
    catch {
        Write-ColorOutput "❌ Python 3.12+ not found or not in PATH" -Color "Red"
        throw "Python 3.12+ is required for EQ12 OpsBot"
    }

    # Check Git (for signed commits)
    try {
        $gitVersion = git --version 2>$null
        Write-ColorOutput "✅ $gitVersion" -Color "Green"
    }
    catch {
        Write-ColorOutput "⚠️  Git not found - signed commits disabled" -Color "Yellow"
    }

    # Check PowerShell version
    $psVersion = $PSVersionTable.PSVersion
    if ($psVersion.Major -lt 5) {
        Write-ColorOutput "⚠️  PowerShell 5.1+ recommended, found: $psVersion" -Color "Yellow"
    }
    else {
        Write-ColorOutput "✅ PowerShell $psVersion" -Color "Green"
    }
}

function Initialize-Directories {
    Write-ColorOutput "📁 Creating directory structure..." -Color "Blue"

    $directories = @(
        "C:\EQ12\logs",
        "C:\EQ12\logs\webhooks",
        "C:\EQ12\configs",
        "C:\EQ12\eq12_opsbot",
        "C:\EQ12\.vscode"
    )

    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-ColorOutput "  Created: $dir" -Color "Green"
        }
        else {
            Write-ColorOutput "  Exists: $dir" -Color "Yellow"
        }
    }
}

function Setup-VirtualEnvironment {
    if ($SkipVenv) {
        Write-ColorOutput "⏭️  Skipping virtual environment setup" -Color "Yellow"
        return
    }

    Write-ColorOutput "🐍 Setting up Python virtual environment..." -Color "Blue"

    $venvPath = "C:\EQ12\.venv"

    if (!(Test-Path $venvPath)) {
        python -m venv $venvPath
        Write-ColorOutput "✅ Virtual environment created" -Color "Green"
    }
    else {
        Write-ColorOutput "⚠️  Virtual environment exists, updating..." -Color "Yellow"
    }

    # Activate and install dependencies
    $activateScript = "$venvPath\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript

        # Upgrade pip
        python -m pip install --upgrade pip

        # Install OpsBot requirements
        if (Test-Path "C:\EQ12\requirements_opsbot.txt") {
            pip install -r "C:\EQ12\requirements_opsbot.txt"
            Write-ColorOutput "✅ Dependencies installed" -Color "Green"
        }
        else {
            Write-ColorOutput "⚠️  requirements_opsbot.txt not found" -Color "Yellow"
        }
    }
}

function Create-Configuration {
    Write-ColorOutput "⚙️  Creating configuration files..." -Color "Blue"

    # Create .env.example
    $envExample = @"
# EQ12 OpsBot Configuration
# Copy this to .env and fill in your values

# Core Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
OPENAI_WEBHOOK_SECRET=your-webhook-secret-from-openai-dashboard

# Budget Limits (USD)
EQ12_BUDGET_DAILY=5.00
EQ12_BUDGET_MONTHLY=120.00

# Service Configuration
EQ12_OPSBOT_HOST=127.0.0.1
EQ12_OPSBOT_PORT=8088
LOG_LEVEL=INFO

# Notifications (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
TEAMS_WEBHOOK_URL=https://your-org.webhook.office.com/YOUR/TEAMS/WEBHOOK
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id

# GitHub Integration (Optional)
GITHUB_TOKEN=ghp_your-github-personal-access-token
GITHUB_REPO=your-username/eq12-issues

# Production Settings
EQ12_ENVIRONMENT=production
EQ12_ENABLE_NOTIFICATIONS=true
EQ12_ENABLE_GITHUB_ISSUES=true
"@

    $envPath = "C:\EQ12\.env.example"
    if (!(Test-Path $envPath)) {
        Set-Content -Path $envPath -Value $envExample -Encoding UTF8
        Write-ColorOutput "✅ Created .env.example" -Color "Green"
    }

    # Create default model policy
    $modelPolicy = @"
# EQ12 OpsBot Model Policy Configuration
# Controls which models are allowed/denied

allowed_models:
  # GPT-4 models
  - gpt-4o
  - gpt-4o-mini
  - gpt-4o-2024-08-06
  - gpt-4-turbo
  - gpt-4-turbo-preview

  # GPT-3.5 models
  - gpt-3.5-turbo
  - gpt-3.5-turbo-16k

# Deny patterns (regex)
denied_patterns:
  # Block all preview models
  - ".*-preview${'$'}"

  # Block o1 models (expensive)
  - "^o1-.*"

  # Block deprecated models
  - "^text-.*"
  - "^code-.*"

# Alternative suggestions for blocked models
alternatives:
  "gpt-4-preview": "gpt-4o"
  "o1-preview": "gpt-4o"
  "o1-mini": "gpt-4o-mini"
  "text-davinci-003": "gpt-3.5-turbo"

# Policy enforcement settings
enforcement:
  block_unknown_models: true
  warn_on_expensive_models: true
  log_policy_violations: true
"@

    $policyPath = "C:\EQ12\configs\models_allowlist.yaml"
    if (!(Test-Path $policyPath)) {
        Set-Content -Path $policyPath -Value $modelPolicy -Encoding UTF8
        Write-ColorOutput "✅ Created model policy" -Color "Green"
    }

    # Create rate limits config
    $rateLimits = @"
# EQ12 OpsBot Rate Limits Configuration
# Tokens per minute (TPM) and Requests per minute (RPM) by model

production:
  gpt-4o:
    tpm: 30000
    rpm: 500

  gpt-4o-mini:
    tpm: 200000
    rpm: 1000

  gpt-4-turbo:
    tpm: 10000
    rpm: 500

  gpt-3.5-turbo:
    tpm: 90000
    rpm: 1000

development:
  # Lower limits for development
  gpt-4o:
    tpm: 3000
    rpm: 50

  gpt-4o-mini:
    tpm: 20000
    rpm: 100

# Rate limit enforcement
enforcement:
  apply_jitter: true
  max_wait_time: 300  # seconds
  backoff_multiplier: 1.5
"@

    $limitsPath = "C:\EQ12\configs\rate_limits.yaml"
    if (!(Test-Path $limitsPath)) {
        Set-Content -Path $limitsPath -Value $rateLimits -Encoding UTF8
        Write-ColorOutput "✅ Created rate limits config" -Color "Green"
    }
}

function Setup-VSCodeIntegration {
    Write-ColorOutput "🔧 Setting up VS Code integration..." -Color "Blue"

    # Create tasks.json for OpsBot
    $tasksJson = @"
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "EQ12: Start OpsBot Server",
            "type": "shell",
            "command": "python",
            "args": ["-m", "eq12_opsbot.main", "run"],
            "group": "build",
            "options": {
                "cwd": "${'${workspaceFolder}'}",
                "env": {
                    "PYTHONUNBUFFERED": "1"
                }
            },
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "EQ12: OpsBot Doctor",
            "type": "shell",
            "command": "python",
            "args": ["-m", "eq12_opsbot.main", "doctor"],
            "group": "test",
            "options": {
                "cwd": "${'${workspaceFolder}'}"
            }
        },
        {
            "label": "EQ12: Sync Rate Limits",
            "type": "shell",
            "command": "python",
            "args": ["-m", "eq12_opsbot.main", "limits", "--sync", "--show"],
            "group": "build"
        },
        {
            "label": "EQ12: Enforce Model Policy",
            "type": "shell",
            "command": "python",
            "args": ["-m", "eq12_opsbot.main", "model-policy", "--enforce", "--show"],
            "group": "test"
        },
        {
            "label": "EQ12: Run OpsBot Tests",
            "type": "shell",
            "command": "python",
            "args": ["-m", "pytest", "tests/opsbot/", "-v"],
            "group": "test"
        }
    ]
}
"@

    $tasksPath = "C:\EQ12\.vscode\tasks.json"
    if (!(Test-Path $tasksPath)) {
        Set-Content -Path $tasksPath -Value $tasksJson -Encoding UTF8
        Write-ColorOutput "✅ Created VS Code tasks" -Color "Green"
    }

    # Create launch.json for debugging
    $launchJson = @"
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug OpsBot Server",
            "type": "python",
            "request": "launch",
            "module": "eq12_opsbot.main",
            "args": ["run", "--host", "127.0.0.1", "--port", "8088"],
            "console": "integratedTerminal",
            "envFile": "${'${workspaceFolder}'}/.env",
            "cwd": "${'${workspaceFolder}'}"
        },
        {
            "name": "Debug OpsBot CLI",
            "type": "python",
            "request": "launch",
            "module": "eq12_opsbot.main",
            "args": ["doctor"],
            "console": "integratedTerminal",
            "envFile": "${'${workspaceFolder}'}/.env"
        }
    ]
}
"@

    $launchPath = "C:\EQ12\.vscode\launch.json"
    if (!(Test-Path $launchPath)) {
        Set-Content -Path $launchPath -Value $launchJson -Encoding UTF8
        Write-ColorOutput "✅ Created VS Code debug config" -Color "Green"
    }
}

function Register-WindowsService {
    if (!$SetupService) {
        return
    }

    Write-ColorOutput "🔧 Setting up Windows service..." -Color "Blue"

    # Check if NSSM is available
    try {
        $null = Get-Command nssm -ErrorAction Stop
    }
    catch {
        Write-ColorOutput "❌ NSSM not found. Install with: winget install nssm" -Color "Red"
        return
    }

    $serviceName = "EQ12OpsBot"
    $pythonPath = (Get-Command python).Source
    $scriptPath = "C:\EQ12\eq12_opsbot\main.py"

    # Check if service already exists
    $existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if ($existingService) {
        Write-ColorOutput "⚠️  Service '$serviceName' already exists" -Color "Yellow"
        return
    }

    # Install service
    & nssm install $serviceName $pythonPath "-m eq12_opsbot.main run"
    & nssm set $serviceName AppDirectory "C:\EQ12"
    & nssm set $serviceName DisplayName "EQ12 OpsBot Webhook Server"
    & nssm set $serviceName Description "EQ12 automation bot for webhooks, budget control, and model policy"
    & nssm set $serviceName Start SERVICE_AUTO_START

    Write-ColorOutput "✅ Windows service registered: $serviceName" -Color "Green"
    Write-ColorOutput "   Start with: net start $serviceName" -Color "Cyan"
}

function Run-FirstTimeSetup {
    Write-ColorOutput "🚀 Running first-time setup..." -Color "Blue"

    # Activate virtual environment if it exists
    $venvActivate = "C:\EQ12\.venv\Scripts\Activate.ps1"
    if (Test-Path $venvActivate) {
        & $venvActivate
    }

    # Run OpsBot first-run initialization
    try {
        python -c "
from eq12_opsbot.first_run import FirstRunSetup
setup = FirstRunSetup()
setup.run_first_time_setup()
print('✅ First-run setup completed')
"
        Write-ColorOutput "✅ OpsBot initialized successfully" -Color "Green"
    }
    catch {
        Write-ColorOutput "⚠️  First-run setup encountered issues: $($_.Exception.Message)" -Color "Yellow"
    }
}

function Show-PostInstallInstructions {
    Write-ColorOutput "`n🎉 EQ12 OpsBot Bootstrap Complete!" -Color "Green"
    Write-ColorOutput "═══════════════════════════════════════════════════════════" -Color "Magenta"

    Write-ColorOutput "`n📋 Next Steps:" -Color "Bold"
    Write-ColorOutput "1. Copy .env.example to .env and configure your API keys" -Color "Cyan"
    Write-ColorOutput "2. Start OpsBot: python -m eq12_opsbot.main run" -Color "Cyan"
    Write-ColorOutput "3. Visit http://127.0.0.1:8088/healthz for status" -Color "Cyan"
    Write-ColorOutput "4. Configure OpenAI webhooks to point to your server" -Color "Cyan"

    Write-ColorOutput "`n🔧 Available Commands:" -Color "Bold"
    Write-ColorOutput "  python -m eq12_opsbot.main run      # Start webhook server" -Color "White"
    Write-ColorOutput "  python -m eq12_opsbot.main doctor   # Health diagnostics" -Color "White"
    Write-ColorOutput "  python -m eq12_opsbot.main --help   # Full command reference" -Color "White"

    if ($SetupService) {
        Write-ColorOutput "`n🔧 Windows Service:" -Color "Bold"
        Write-ColorOutput "  net start EQ12OpsBot    # Start service" -Color "White"
        Write-ColorOutput "  net stop EQ12OpsBot     # Stop service" -Color "White"
    }

    Write-ColorOutput "`n📖 Documentation:" -Color "Bold"
    Write-ColorOutput "  README_EQ12_OPSBOT.md - Complete usage guide" -Color "White"
    Write-ColorOutput "  configs/ - Configuration files and examples" -Color "White"
    Write-ColorOutput "  logs/ - Runtime logs and webhook events" -Color "White"

    Write-ColorOutput "`n═══════════════════════════════════════════════════════════" -Color "Magenta"
    Write-ColorOutput "Ready to run: python -m eq12_opsbot.main run 🚀" -Color "Green"
}

# Main execution
try {
    Write-ColorOutput "🎯 EQ12 OpsBot Bootstrap" -Color "Bold"
    Write-ColorOutput "Production webhook automation setup`n" -Color "Magenta"

    Test-Prerequisites
    Initialize-Directories
    Create-Configuration

    if (!$ConfigOnly) {
        Setup-VirtualEnvironment
        Setup-VSCodeIntegration
        Register-WindowsService
        Run-FirstTimeSetup
    }

    Show-PostInstallInstructions

}
catch {
    Write-ColorOutput "`n❌ Bootstrap failed: $($_.Exception.Message)" -Color "Red"
    Write-ColorOutput "Stack trace: $($_.ScriptStackTrace)" -Color "Red"
    exit 1
}
