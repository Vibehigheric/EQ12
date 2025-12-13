# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 EQ12 Project Contributors

<#
.SYNOPSIS
    EQ12 Security Tools Setup Script
    
.DESCRIPTION
    Installs and configures security tools for the EQ12 repository:
    - pre-commit hooks
    - gitleaks secret scanning
    - detect-secrets baseline
    - Windows Credential Manager helpers
    
.EXAMPLE
    .\eq12_setup_security.ps1
    
.NOTES
    Run this script once per development environment setup.
    Requires Python 3.8+ and Git.
#>

[CmdletBinding()]
param(
    [switch]$SkipPreCommit,
    [switch]$SkipCredentials,
    [switch]$Force
)

Write-Host "🔐 EQ12 Security Tools Setup" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Check prerequisites
Write-Host "🔍 Checking prerequisites..."

# Check Python
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "❌ Python 3.8+ required. Install from https://python.org"
    exit 1
}

# Check Git
try {
    $gitVersion = git --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Git not found"
    }
    Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
} catch {
    Write-Error "❌ Git required. Install from https://git-scm.com"
    exit 1
}

# Install pre-commit if not skipped
if (-not $SkipPreCommit) {
    Write-Host "`n📦 Installing pre-commit..."
    
    try {
        # Check if pre-commit is installed
        $precommitVersion = pre-commit --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ pre-commit already installed: $precommitVersion" -ForegroundColor Green
        } else {
            # Install pre-commit
            Write-Host "Installing pre-commit via pip..."
            pip install pre-commit
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to install pre-commit"
            }
            Write-Host "✅ pre-commit installed successfully" -ForegroundColor Green
        }
        
        # Install hooks
        Write-Host "🔗 Installing pre-commit hooks..."
        pre-commit install
        pre-commit install --hook-type commit-msg
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Pre-commit hooks installed" -ForegroundColor Green
        } else {
            Write-Warning "⚠️ Some hooks may have failed to install"
        }
        
    } catch {
        Write-Error "❌ Failed to setup pre-commit: $_"
        if (-not $Force) { exit 1 }
    }
}

# Install gitleaks
Write-Host "`n🔒 Installing gitleaks..."

try {
    # Check if gitleaks is installed
    $gitleaksVersion = gitleaks version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ gitleaks already installed: $gitleaksVersion" -ForegroundColor Green
    } else {
        # Install gitleaks (Windows)
        if ($env:OS -eq "Windows_NT") {
            Write-Host "Installing gitleaks via winget..."
            winget install gitleaks.gitleaks
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Trying chocolatey..."
                choco install gitleaks -y
                
                if ($LASTEXITCODE -ne 0) {
                    Write-Warning "⚠️ Failed to install gitleaks automatically"
                    Write-Host "Please install manually from: https://github.com/gitleaks/gitleaks/releases"
                }
            }
        }
    }
} catch {
    Write-Warning "⚠️ gitleaks installation failed: $_"
}

# Install detect-secrets
Write-Host "`n🔍 Installing detect-secrets..."

try {
    pip install detect-secrets
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ detect-secrets installed" -ForegroundColor Green
        
        # Create baseline if it doesn't exist
        if (-not (Test-Path ".secrets.baseline")) {
            Write-Host "Creating secrets baseline..."
            detect-secrets scan --baseline .secrets.baseline
            Write-Host "✅ Secrets baseline created" -ForegroundColor Green
        }
    } else {
        throw "Failed to install detect-secrets"
    }
} catch {
    Write-Error "❌ Failed to install detect-secrets: $_"
    if (-not $Force) { exit 1 }
}

# Setup Windows Credential Manager helpers
if (-not $SkipCredentials) {
    Write-Host "`n🗝️ Setting up credential helpers..."
    
    try {
        # Install keyring for Python
        pip install keyring
        
        # Create credential helper script
        $credentialHelper = @'
# EQ12 Credential Helper Functions
# Source: . .\scripts\eq12_credentials.ps1

function Set-EQ12ApiKey {
    param(
        [Parameter(Mandatory=$true)]
        [string]$KeyName,
        
        [Parameter(Mandatory=$true)]
        [string]$KeyValue
    )
    
    $target = "EQ12_$KeyName"
    cmdkey /generic:$target /user:"eq12-dev" /pass:$KeyValue
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Stored $KeyName securely" -ForegroundColor Green
    } else {
        Write-Error "❌ Failed to store $KeyName"
    }
}

function Get-EQ12ApiKey {
    param(
        [Parameter(Mandatory=$true)]
        [string]$KeyName
    )
    
    $target = "EQ12_$KeyName"
    try {
        $cred = Get-StoredCredential -Target $target -ErrorAction Stop
        return $cred.GetNetworkCredential().Password
    } catch {
        Write-Warning "⚠️ Key $KeyName not found in credential store"
        return $null
    }
}

function Remove-EQ12ApiKey {
    param(
        [Parameter(Mandatory=$true)]
        [string]$KeyName
    )
    
    $target = "EQ12_$KeyName"
    cmdkey /delete:$target
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Removed $KeyName from credential store" -ForegroundColor Green
    } else {
        Write-Warning "⚠️ Failed to remove $KeyName"
    }
}

function Test-EQ12Credentials {
    $keys = @("OPENAI_API_KEY", "ODDS_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
    
    Write-Host "🔍 Checking stored credentials..." -ForegroundColor Cyan
    
    foreach ($key in $keys) {
        $value = Get-EQ12ApiKey -KeyName $key
        if ($value) {
            $masked = $value.Substring(0, [Math]::Min(8, $value.Length)) + "***"
            Write-Host "✅ $key : $masked" -ForegroundColor Green
        } else {
            Write-Host "❌ $key : Not found" -ForegroundColor Red
        }
    }
}

# Example usage:
# Set-EQ12ApiKey -KeyName "OPENAI_API_KEY" -KeyValue "sk-your-key-here"
# $key = Get-EQ12ApiKey -KeyName "OPENAI_API_KEY"
# Test-EQ12Credentials
'@
        
        $credentialHelper | Out-File -FilePath "scripts\eq12_credentials.ps1" -Encoding UTF8 -Force
        Write-Host "✅ Credential helper created: scripts\eq12_credentials.ps1" -ForegroundColor Green
        
    } catch {
        Write-Warning "⚠️ Failed to setup credential helpers: $_"
    }
}

# Create .env.template if it doesn't exist
if (-not (Test-Path ".env.template")) {
    Write-Host "`n📝 Creating .env.template..."
    
    $envTemplate = @'
# EQ12 Environment Variables Template
# Copy this to .env.local and fill in your actual values
# NEVER commit .env.local to version control

# OpenAI API Configuration
OPENAI_API_KEY=sk-PLACEHOLDER_OPENAI_KEY_HERE
OPENAI_ORG_ID=org-PLACEHOLDER_ORG_ID_HERE

# Sports Betting APIs
ODDS_API_KEY=PLACEHOLDER_ODDS_API_KEY_HERE
ODDS_API_BASE_URL=https://api.the-odds-api.com

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=PLACEHOLDER_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=PLACEHOLDER_CHAT_ID_HERE

# Database Configuration
DATABASE_URL=sqlite:///data/eq12.db
DATABASE_POOL_SIZE=5

# Security & Authentication
JWT_SECRET_KEY=PLACEHOLDER_JWT_SECRET_HERE
API_RATE_LIMIT=100
API_BURST_LIMIT=200

# Logging & Monitoring
LOG_LEVEL=INFO
LOG_FORMAT=json
METRICS_ENABLED=true

# Feature Flags
ENABLE_LIVE_BETTING=false
ENABLE_PARLAY_ALERTS=true
ENABLE_CLV_TRACKING=true
'@
    
    $envTemplate | Out-File -FilePath ".env.template" -Encoding UTF8 -Force
    Write-Host "✅ .env.template created" -ForegroundColor Green
}

# Run security scan
Write-Host "`n🔒 Running security scan..."

try {
    if (Test-Path ".gitleaks.toml") {
        Write-Host "Running gitleaks scan..."
        gitleaks detect --config .gitleaks.toml --no-banner --quiet
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ No secrets detected" -ForegroundColor Green
        } else {
            Write-Warning "⚠️ Potential secrets detected - review output above"
        }
    }
} catch {
    Write-Warning "⚠️ Could not run gitleaks scan: $_"
}

# Summary
Write-Host "`n✅ Security Setup Complete!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

Write-Host "`n📋 Next Steps:"
Write-Host "1. Review and configure .env.local with your API keys"
Write-Host "2. Run: . .\scripts\eq12_credentials.ps1"
Write-Host "3. Store credentials: Set-EQ12ApiKey -KeyName 'OPENAI_API_KEY' -KeyValue 'your-key'"
Write-Host "4. Test setup: python scripts\eq12_telegram_alerts.py --test"
Write-Host "5. Run pre-commit: pre-commit run --all-files"

Write-Host "`n🔐 Security Features Enabled:"
Write-Host "• Pre-commit hooks with secret scanning"
Write-Host "• GitLeaks configuration for comprehensive detection"  
Write-Host "• Windows Credential Manager integration"
Write-Host "• Baseline secrets scanning"
Write-Host "• Conventional commit formatting"

Write-Host "`n⚠️ Remember: Never commit real API keys to version control!"