# EQ12 Key Policy & Secret Management
# SPDX-License-Identifier: MIT

## Overview

This document outlines EQ12's secret management policy to ensure API keys, tokens, and credentials are handled securely throughout the development lifecycle.

## 🔐 Secret Storage Locations

### Development Environment

**✅ APPROVED:**
- `.env.local` (in `.gitignore`, for local development only)
- Windows Credential Manager (`cmdkey`)
- macOS Keychain (`security`)
- Linux Secret Service (`secret-tool`)

**❌ NEVER:**
- Hardcoded in source code
- Committed to version control
- Stored in plain text files
- Shared via email/chat

### Production Environment

**✅ APPROVED:**
- Azure Key Vault
- AWS Secrets Manager
- GitHub Secrets (for Actions)
- HashiCorp Vault
- Docker Secrets

**❌ NEVER:**
- Environment variables in containers (unless encrypted)
- Config files in repositories
- Shared filesystems

## 🔑 Key Types & Rotation

### API Keys
- **OpenAI:** Rotate every 90 days
- **The Odds API:** Rotate every 30 days  
- **Telegram Bot:** Rotate every 180 days
- **GitHub Personal Access Tokens:** Rotate every 30 days

### Database Credentials
- **SQLite:** File permissions `600` (owner read/write only)
- **Production DB:** Rotate every 30 days
- **Connection strings:** Always use environment variables

### Signing Keys
- **Code signing:** Hardware security module (HSM) preferred
- **Git commit signing:** GPG keys, rotate yearly
- **API authentication:** JWT with 24-hour expiration

## 💻 Windows Development Setup

### Using Windows Credential Manager

```powershell
# Store API keys securely
cmdkey /generic:"EQ12_OPENAI_API_KEY" /user:"eq12-dev" /pass:"sk-YOUR_OPENAI_KEY_HERE"
cmdkey /generic:"EQ12_ODDS_API_KEY" /user:"eq12-dev" /pass:"YOUR_ODDS_API_KEY_HERE"
cmdkey /generic:"EQ12_TELEGRAM_BOT_TOKEN" /user:"eq12-dev" /pass:"YOUR_BOT_TOKEN_HERE"
cmdkey /generic:"EQ12_TELEGRAM_CHAT_ID" /user:"eq12-dev" /pass:"YOUR_CHAT_ID_HERE"

# Retrieve in PowerShell
$credential = Get-StoredCredential -Target "EQ12_OPENAI_API_KEY"
$env:OPENAI_API_KEY = $credential.GetNetworkCredential().Password

# Retrieve in Python
import keyring
api_key = keyring.get_password("EQ12_OPENAI_API_KEY", "eq12-dev")
```

### Using .env.local (Alternative)

Create `.env.local` (never commit this file):

```bash
# EQ12 Development Environment Variables
# NEVER commit this file - it's in .gitignore

OPENAI_API_KEY=sk-YOUR_OPENAI_KEY_HERE
ODDS_API_KEY=YOUR_ODDS_API_KEY_HERE
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE
```

Load in Python:
```python
from dotenv import load_dotenv
import os

load_dotenv('.env.local')
openai_key = os.getenv('OPENAI_API_KEY')
```

## 🚨 Incident Response

### If Secret is Leaked

1. **IMMEDIATE:** Revoke the compromised credential
2. **Generate** new credential with different format/scope
3. **Update** all systems using the old credential  
4. **Audit** logs for potential unauthorized usage
5. **Document** incident in `security_incidents.log`

### Prevention

- Run `pre-commit` hooks before every commit
- Use `gitleaks` to scan repository history
- Enable branch protection with required status checks
- Configure secret scanning in CI/CD pipeline

## 📋 Compliance Checklist

- [ ] All secrets in approved storage locations
- [ ] No hardcoded credentials in source code
- [ ] `.env.template` contains placeholder examples only
- [ ] Pre-commit hooks configured and active
- [ ] Secret scanning enabled in CI/CD
- [ ] Key rotation schedule documented and followed
- [ ] Incident response procedure tested

## 🔄 Rotation Commands

### OpenAI API Key Rotation
```powershell
# 1. Generate new key at https://platform.openai.com/api-keys
# 2. Test new key
$newKey = "sk-NEW_KEY_HERE"
$env:OPENAI_API_KEY = $newKey
python -c "import openai; print('✅ New key works')"

# 3. Update credential store
cmdkey /delete:"EQ12_OPENAI_API_KEY"
cmdkey /generic:"EQ12_OPENAI_API_KEY" /user:"eq12-dev" /pass:"$newKey"

# 4. Revoke old key in OpenAI dashboard
```

### Telegram Bot Token Rotation
```powershell
# 1. Contact @BotFather on Telegram
# 2. Use /token command to get new token
# 3. Update credential store
$newToken = "NEW_BOT_TOKEN_HERE"
cmdkey /delete:"EQ12_TELEGRAM_BOT_TOKEN"
cmdkey /generic:"EQ12_TELEGRAM_BOT_TOKEN" /user:"eq12-dev" /pass:"$newToken"

# 4. Test new token
python scripts/eq12_telegram_alerts.py --test
```

## 📝 Audit Log Format

Keep rotation logs in `logs/key_rotation.log`:

```
2025-10-06T22:00:00Z [INFO] OpenAI API key rotated successfully
2025-10-06T22:00:30Z [INFO] Old key revoked, new key activated  
2025-10-06T22:01:00Z [TEST] Telegram integration test passed
```

## 🏢 Production Deployment

For production deployments, use infrastructure-as-code:

```yaml
# Azure Key Vault (example)
apiVersion: v1
kind: Secret
metadata:
  name: eq12-secrets
type: Opaque
data:
  openai-api-key: <base64-encoded-from-key-vault>
  odds-api-key: <base64-encoded-from-key-vault>
```

Never store production secrets in development environments.