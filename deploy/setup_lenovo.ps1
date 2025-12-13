# EQ12 Setup Script for Lenovo M70q
Write-Host "🚀 Starting EQ12 Cluster Setup..." -ForegroundColor Cyan

# 1. Check Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Error "❌ Python not found! Please install Python 3.10+ and add to PATH."
    exit 1
}

# 2. Create Virtual Environment
if (-not (Test-Path ".venv")) {
    Write-Host "📦 Creating Python Virtual Environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
}
else {
    Write-Host "✅ Virtual Environment already exists." -ForegroundColor Green
}

# 3. Activate Venv and Install Requirements
Write-Host "⬇️ Installing Dependencies..." -ForegroundColor Yellow
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed successfully." -ForegroundColor Green
}
else {
    Write-Error "❌ Failed to install dependencies."
    exit 1
}

# 4. Setup Environment Variables
if (-not (Test-Path ".env")) {
    Write-Host "🔑 Creating .env file..." -ForegroundColor Yellow
    $envContent = @"
OPENAI_API_KEY=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
ODDS_API_KEY=c32c9644050b2240081428b43e7016ce
EQ12_ENV=PRODUCTION
"@
    Set-Content -Path ".env" -Value $envContent
    Write-Host "✅ .env file created. Please verify keys." -ForegroundColor Green
}

# 5. Create Directories
$dirs = @("logs", "reports", "workspace", "n8n\generated")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "📁 Created directory: $dir" -ForegroundColor Gray
    }
}

# 6. Setup Local LLMs (Ollama)
Write-Host "`n🦙 Setting up Local LLMs..." -ForegroundColor Cyan
if (Test-Path "scripts\download_ollama_models.ps1") {
    & "scripts\download_ollama_models.ps1"
} else {
    Write-Warning "⚠️ scripts\download_ollama_models.ps1 not found. Skipping local LLM setup."
}

Write-Host "`n🎉 EQ12 Cluster Setup Complete!" -ForegroundColor Cyan
Write-Host "To activate the environment, run: .\.venv\Scripts\Activate.ps1"
Write-Host "To run the betting engine: python src\gpt_analyzer.py"
