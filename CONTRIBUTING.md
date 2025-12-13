# 🤝 Contributing to EQ12 GODSTACK

Thank you for contributing!
This project enforces strict **DevSecOps governance** to protect sensitive modules and ensure code quality.
Please follow the rules below when making contributions.

---

## 🌱 Branching Strategy
- Always create feature branches from `main`.
  Example:
  ```bash
  git checkout main
  git pull origin main
  git checkout -b feature/my-new-module
  ```
- Branch names should be descriptive:
  - `feature/...`
  - `bugfix/...`
  - `security/...`
  - `compliance/...`

---

## 📌 Pull Requests
1. **PR Templates**:
   - General PRs → `.github/PULL_REQUEST_TEMPLATE.md`
   - Sensitive modules (betting, cannabis, credit) → `.github/PULL_REQUEST_TEMPLATE/sensitive_module.md`

2. **Labels**:
   - Auto-labeler applies labels based on folder changes:
     - `⚠ Sensitive: Betting`, `⚠ Sensitive: Cannabis`, `⚠ Sensitive: Credit`
   - You do not need to label manually.

3. **Governance Gates**:
   All PRs must pass before merge:
   - ✅ Secrets Gate (`check-secrets.yml`)
   - ✅ Security Gate (`security-scan.yml`)
   - ✅ CI/Test Gate (`ci-all-in-one.yml`)
   - ✅ Compliance Gate (PR templates + CODEOWNERS)

---

## 🤖 Copilot Review
- Use [COPILOT_REVIEW.md](COPILOT_REVIEW.md) to run GitHub Copilot Chat prompts.
- Copilot checks:
  - Secrets & security risks
  - Test coverage
  - Sensitive module compliance
  - Governance gate pass/fail summary
- Run the **Governance Report Prompt** at the end to summarize compliance.

---

## 🔑 Secrets & Authentication
- Never commit `.env` or secrets to the repo.
- Required environment variables (for local dev / Codespaces):
  - `TG_TOKEN`, `TG_CHAT_ID`
  - `OPENAI_SERVICE_KEY`
  - `BING_KEY`, `GOOGLE_KEY`, `GOOGLE_CSE_ID`
  - `CODECOV_TOKEN`, `SONAR_TOKEN`
- Secrets are injected automatically in **Codespaces** and GitHub Actions.

### Authentication Requirements
- **Two-Factor Authentication**: Required for all contributors
- **SSH Keys**: Use Ed25519 keys with passphrases
- **Commit Signing**: GPG signatures required for sensitive stack changes
- **Token Security**: Personal access tokens expire within 90 days
- **Session Management**: Regular review of active sessions required

---

## 🛡 Sensitive Modules
- Folders: `betting/`, `cannabis/`, `credit/`
- Require:
  - Sensitive PR template
  - CODEOWNERS approval
  - Compliance checklist completion
- These PRs cannot merge without extra scrutiny.

---

## 🧪 Testing
- All new code must include **pytest tests**.
- Run locally:
  ```bash
  pytest --maxfail=1 --disable-warnings -q
  ```
- CI enforces coverage ≥ 70%.
- Coverage reports uploaded to Codecov.

---

## 📅 Post-Merge
Once merged to `main`, automated jobs run:
- **Daily** → Trending + NewsAggregator + enrichment → Telegram
- **Weekly** → Scheduled CI run
- **Monthly** → BadgeCheck (status report)
- **Quarterly** → Compliance Audit (secrets, CODEOWNERS, governance rules)

---

## 📝 Commit Messages
Follow [Conventional Commits specification](https://www.conventionalcommits.org/):
- `feat:` → new feature
- `fix:` → bug fix
- `chore:` → non-code (docs, CI config)
- `docs:` → documentation updates
- `security:` → security patches
- `compliance:` → governance changes

Example:
```bash
feat(betting): add MLB odds fetcher with OddsAPI
```

---

## 📢 Reporting Issues
- Use GitHub Issues for bug reports and feature requests.
- For **security vulnerabilities**, follow the process in [SECURITY.md](SECURITY.md).
- For **compliance questions**, see [COMPLIANCE.md](COMPLIANCE.md).

---

## ✅ Summary
Contributors must:
- Branch from `main`.
- Use correct PR template.
- Pass all governance gates.
- Run Copilot review prompts.
- Add tests for new code.
- Never commit secrets.

Following this ensures EQ12 GODSTACK remains **secure, compliant, and audit-ready**.

---

## 🔧 Development Environment Setup

### Option 1: GitHub Codespaces (Recommended)
```bash
# 1. Open in Codespaces (secrets auto-injected)
# 2. Activate Python environment
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements_patch.txt

# 4. Run tests
pytest
```

### Option 2: Local Development
```bash
# 1. Clone repository
git clone https://github.com/Vibehigheric/edgegod-parlay.git
cd edgegod-parlay

# 2. Set up Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements_patch.txt

# 4. Copy environment template
cp .env.example .env
# Edit .env with your actual secrets

# 5. Run tests
pytest
```

### Option 3: Docker Development
```bash
# 1. Build development container
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 2. Access container
docker-compose exec godstack bash

# 3. Run development commands
pytest
python dashboard.py
```

---

## 🚀 Quick Commands

### Run Tests
```bash
# All tests
pytest

# Fast tests only
pytest -m "not slow"

# With coverage
pytest --cov=. --cov-report=html
```

### Start Services
```bash
# Start full stack
docker-compose up -d

# Start development mode
uvicorn dashboard:app --reload --host 0.0.0.0 --port 8000
```

### Governance Commands
```bash
# Check PR status
gh pr list

# Run governance check
python governance/alert_manager.py

# Start metrics exporter
python governance/alert_manager.py --metrics
```

---

*Thank you for contributing to EQ12 GODSTACK! Your adherence to these guidelines helps maintain the security, compliance, and quality of our automation platform.*
