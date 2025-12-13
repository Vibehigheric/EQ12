# EQ12 Virtual Environment Setup Guide

## Version Isolation Strategy

### 1. Core EQ12 Environment (OpenAI 2.x)
```powershell
# Create core venv
python -m venv .venv-eq12-core
.\.venv-eq12-core\Scripts\Activate.ps1

# Install core requirements
pip install openai==2.1.0 aiohttp flask flask-socketio psutil requests beautifulsoup4 selenium pytest black

# Lock versions
pip freeze > requirements-core.lock
```

### 2. Legacy Llama-Stack Environment (OpenAI 1.x) - If Needed
```powershell
# Create legacy venv
python -m venv .venv-llama-stack
.\.venv-llama-stack\Scripts\Activate.ps1

# Install with older OpenAI
pip install "openai<1.100.0" llama-stack==0.2.20

# Lock versions
pip freeze > requirements-legacy.lock
```

## Current Status
- **Active Environment**: Default system Python with OpenAI 2.1.0
- **Conflict Resolution**: llama-stack removed from core environment
- **Recommendation**: Use separate venvs if llama-stack features are needed

## Environment Activation Commands
```powershell
# Activate core EQ12 environment
.\.venv-eq12-core\Scripts\Activate.ps1

# Activate legacy environment (if created)
.\.venv-llama-stack\Scripts\Activate.ps1

# Deactivate any environment
deactivate
```

## Package Version Conflicts Resolved
- ✅ openai 2.1.0 (core EQ12 apps)
- ❌ llama-stack 0.2.20 (requires openai < 1.100.0)
- ✅ Solution: Separate environments or removal of llama-stack

## Lock File Management
- `requirements.lock` - Current system state (all packages)
- `requirements-core.lock` - Core EQ12 minimal requirements
- `requirements-legacy.lock` - Llama-stack compatible versions (if created)

## Node.js Package Management
```powershell
# Ensure package-lock.json is committed
git add package-lock.json
git commit -m "Lock Node.js dependencies"

# Use npm ci in CI/production
npm ci --production
```
