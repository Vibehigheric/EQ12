[CmdletBinding()]
param()

Write-Host "🚀 EQ12 GITHUB PRO CODESPACES SETUP" -ForegroundColor Green
Write-Host "Installing requirements, Playwright browsers, and GitHub Pro optimizations" -ForegroundColor Cyan
$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

# Create logs directory
$LogsDir = '/workspaces/EQ12/logs'
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
    Write-Host "Created logs directory: $LogsDir" -ForegroundColor Cyan
}

if (Test-Path requirements.txt) {
    Write-Host "Installing Python requirements..." -ForegroundColor Yellow
    try {
        python -m pip install --upgrade pip --quiet
        python -m pip install -r requirements.txt --quiet
        Write-Host "✅ Python requirements installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Error installing Python requirements: $($_.Exception.Message)" -ForegroundColor Red
    }
}
else {
    Write-Host "ℹ️  No requirements.txt found, skipping Python package installation" -ForegroundColor Cyan
}

# Install Playwright browsers if playwright is in requirements
try {
    Write-Host "Checking for Playwright installation..." -ForegroundColor Yellow
    python -c "import playwright" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Installing Playwright browsers..." -ForegroundColor Yellow
        python -m playwright install --with-deps
        Write-Host "✅ Playwright browsers installed successfully" -ForegroundColor Green
    }
    else {
        Write-Host "ℹ️  Playwright not found, skipping browser installation" -ForegroundColor Cyan
    }
}
catch {
    Write-Host "⚠️  Playwright browser installation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Optional: configure ngrok if NGROK_AUTHTOKEN provided
if ($env:NGROK_AUTHTOKEN) {
    Write-Host "Configuring ngrok authtoken..." -ForegroundColor Yellow
    if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
        Write-Host "⚠️  ngrok not found in container; installing..." -ForegroundColor Yellow
        try {
            curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
            echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
            sudo apt update && sudo apt install ngrok -y
            Write-Host "✅ ngrok installed successfully" -ForegroundColor Green
        }
        catch {
            Write-Host "⚠️  ngrok installation failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    if (Get-Command ngrok -ErrorAction SilentlyContinue) {
        try {
            ngrok config add-authtoken $env:NGROK_AUTHTOKEN
            Write-Host "✅ ngrok authtoken configured successfully" -ForegroundColor Green
        }
        catch {
            Write-Host "⚠️  ngrok configuration failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}
else {
    Write-Host "ℹ️  NGROK_AUTHTOKEN not provided, skipping ngrok setup" -ForegroundColor Cyan
}

# Configure Git if GPG keys are available
if (Test-Path '/workspaces/EQ12/keys') {
    Write-Host "Importing GPG keys..." -ForegroundColor Yellow
    try {
        Get-ChildItem '/workspaces/EQ12/keys/*.asc' -ErrorAction SilentlyContinue | ForEach-Object {
            gpg --import $_.FullName
            Write-Host "Imported GPG key: $($_.Name)" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "⚠️  GPG key import failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Set up development environment
Write-Host "Setting up development environment..." -ForegroundColor Yellow
try {
    # Create common directories
    @('/workspaces/EQ12/logs', '/workspaces/EQ12/data', '/workspaces/EQ12/temp') | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
            Write-Host "Created directory: $_" -ForegroundColor Cyan
        }
    }
    
    # Set permissions
    sudo chown -R vscode:vscode /workspaces/EQ12
    Write-Host "✅ Development environment configured" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Development environment setup failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 EQ12 devcontainer post-create setup complete!" -ForegroundColor Green
Write-Host "📝 Logs directory: /workspaces/EQ12/logs" -ForegroundColor Cyan
Write-Host "🐍 Python version: $(python --version)" -ForegroundColor Cyan
Write-Host "💻 PowerShell version: $($PSVersionTable.PSVersion)" -ForegroundColor Cyan
