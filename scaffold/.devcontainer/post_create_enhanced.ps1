[CmdletBinding()]
param()

Write-Host "🏗️ EQ12 scaffold post-create: installing requirements and enabling profile" -ForegroundColor Green
$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

# Ensure logs folder exists
$eq12Logs = $env:EQ12_LOGS -or '/workspaces/EQ12/logs'
if (-not (Test-Path $eq12Logs)) { 
    New-Item -ItemType Directory -Path $eq12Logs -Force | Out-Null 
    Write-Host "📁 Created logs directory: $eq12Logs" -ForegroundColor Cyan
}

# Install Python requirements if present
$req = Join-Path $PSScriptRoot '..\..\..\requirements.txt'
if (Test-Path $req) {
    Write-Host "📦 Installing requirements from $req" -ForegroundColor Yellow
    try {
        python -m pip install --upgrade pip --quiet
        pip install -r $req --quiet
        Write-Host "✅ Python requirements installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Error installing requirements: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Install Playwright browsers if playwright available
try {
    Write-Host "🎭 Checking for Playwright installation..." -ForegroundColor Yellow
    pip show playwright > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "🎭 Installing Playwright browsers..." -ForegroundColor Yellow
        python -m playwright install --with-deps
        Write-Host "✅ Playwright browsers installed successfully" -ForegroundColor Green
    } else {
        Write-Host "🎭 Installing Playwright and browsers..." -ForegroundColor Yellow
        pip install playwright --quiet
        python -m playwright install --with-deps
        Write-Host "✅ Playwright and browsers installed successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Playwright installation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Try to install stealth libs quietly
try {
    Write-Host "🥷 Installing stealth automation libraries..." -ForegroundColor Yellow
    pip install undetected-chromedriver playwright-stealth fake-useragent --quiet
    Write-Host "✅ Stealth libraries installed successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Could not install stealth libs automatically: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Please install manually if required: pip install undetected-chromedriver playwright-stealth fake-useragent" -ForegroundColor Cyan
}

# Auto-install dotfiles if DOTFILES_REPO provided (Codespaces convenience)
if ($env:DOTFILES_REPO) {
    $dotdir = "$HOME/.dotfiles"
    if (-not (Test-Path $dotdir)) {
        Write-Host "🔧 Installing dotfiles from $env:DOTFILES_REPO..." -ForegroundColor Yellow
        try {
            git clone $env:DOTFILES_REPO $dotdir
            if (Test-Path "$dotdir/install.sh") {
                bash "$dotdir/install.sh"
                Write-Host "✅ Dotfiles installed successfully" -ForegroundColor Green
            }
        } catch {
            Write-Host "⚠️ Dotfiles installation failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "ℹ️ Dotfiles already present at $dotdir" -ForegroundColor Cyan
    }
} else {
    Write-Host "ℹ️ DOTFILES_REPO not provided, skipping dotfiles setup" -ForegroundColor Cyan
}

# Configure Git if GPG keys are available
if (Test-Path '/workspaces/EQ12/keys') {
    Write-Host "🔐 Importing GPG keys..." -ForegroundColor Yellow
    try {
        Get-ChildItem '/workspaces/EQ12/keys/*.asc' -ErrorAction SilentlyContinue | ForEach-Object {
            gpg --import $_.FullName
            Write-Host "🔑 Imported GPG key: $($_.Name)" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️ GPG key import failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Set up scaffold-specific directories
Write-Host "🏗️ Setting up scaffold directories..." -ForegroundColor Yellow
try {
    @(
        '/workspaces/EQ12/scaffold/templates',
        '/workspaces/EQ12/scaffold/output', 
        '/workspaces/EQ12/scaffold/temp'
    ) | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
            Write-Host "📁 Created directory: $_" -ForegroundColor Cyan
        }
    }
    
    # Set permissions
    sudo chown -R vscode:vscode /workspaces/EQ12/scaffold
    Write-Host "✅ Scaffold environment configured" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Scaffold setup failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 EQ12 scaffold devcontainer post-create setup complete!" -ForegroundColor Green
Write-Host "📂 Scaffold directory: /workspaces/EQ12/scaffold" -ForegroundColor Cyan
Write-Host "📝 Logs directory: /workspaces/EQ12/logs" -ForegroundColor Cyan
Write-Host "🐍 Python version: $(python --version)" -ForegroundColor Cyan
Write-Host "💻 PowerShell version: $($PSVersionTable.PSVersion)" -ForegroundColor Cyan