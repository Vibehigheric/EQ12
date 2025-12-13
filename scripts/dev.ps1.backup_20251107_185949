# Quick development script
# Usage: pwsh -File scripts/dev.ps1

param(
    [switch]$SkipBootstrap,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
Write-Host "🚀 EQ12 Development Environment Setup" -ForegroundColor Green

# 1) Bootstrap environment
if (-not $SkipBootstrap) {
    Write-Host "📦 Running bootstrap..." -ForegroundColor Yellow
    & pwsh -File scripts/bootstrap.ps1
}

# 2) Code quality checks
Write-Host "🔧 Running code quality checks..." -ForegroundColor Yellow

# Activate venv for remaining commands
$venv = ".venv\Scripts\Activate.ps1"
if (Test-Path $venv) {
    . $venv
}

# Lint and format
Write-Host "   - Running ruff check..." -ForegroundColor Cyan
uv run ruff check --fix .

Write-Host "   - Running ruff format..." -ForegroundColor Cyan  
uv run ruff format .

# 3) Import audit
Write-Host "📋 Auditing imports..." -ForegroundColor Yellow
python scripts/audit_imports.py

# 4) Run tests
if (-not $SkipTests) {
    Write-Host "🧪 Running tests..." -ForegroundColor Yellow
    
    if (Test-Path "tests") {
        uv run pytest -q tests/ || Write-Host "⚠️ Some tests failed" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️ No tests directory found" -ForegroundColor Yellow
    }
}

Write-Host "✅ Development setup complete!" -ForegroundColor Green
Write-Host "💡 Ready for EQ12 sports betting automation development" -ForegroundColor Cyan