# 🔒 Security Policy – EQ12 GODSTACK

This repository is governed by a DevSecOps pipeline that enforces **secure coding, secret handling, supply chain security, and responsible disclosure**.

---

## 🚀 Supported Versions
Only the `main` branch is actively maintained and subject to security monitoring.

| Version | Supported |
|---------|-----------||
| main    | ✅ |
| other branches | ❌ (development use only) |

---

## 🧑‍💻 Secure Coding Practices
- All code must follow **PEP8 + repo governance rules**.  
- Prohibited:
  - Hardcoded secrets (API keys, tokens, passwords).  
  - Use of unsafe functions (`eval()`, `exec()`, `os.system()` without sanitization).  
- Required:
  - Store secrets in **environment variables**, never in source.  
  - Use **SQLite** as default DB for persistence.  
  - Always log through approved logger (no silent failures).  

---

## 🔑 Secret Handling
- **GitHub Secret Scanning** enabled by default.  
- **Gitleaks Action** scans PRs for secrets and blocks merges if detected.  
- **Secrets Gate workflow** (`check-secrets.yml`) validates required environment variables:
  - `TG_TOKEN`, `TG_CHAT_ID`  
  - `OPENAI_SERVICE_KEY`  
  - `BING_KEY`, `GOOGLE_KEY`, `GOOGLE_CSE_ID`  
  - `CODECOV_TOKEN`, `SONAR_TOKEN`

### Authentication Security Standards
- **Personal Access Tokens**: Use fine-grained tokens with minimal scopes
- **SSH Keys**: Ed25519 keys preferred, regular rotation required
- **Two-Factor Authentication**: Mandatory for all repository contributors
- **Commit Signing**: GPG signatures required for sensitive business stacks
- **Token Expiration**: Maximum 90-day expiration for all access tokens
- **Session Management**: Regular review and revocation of unused sessions

---

## 🛡️ Supply Chain Security
- **Dependabot** runs daily to check for outdated/vulnerable dependencies.  
- **Dependency Review Action** blocks PRs that introduce vulnerable packages.  
- All dependencies must be pinned in `requirements.txt` or `requirements_patch.txt`.  
- Docker images are built and pushed to **GitHub Packages** with provenance metadata.  

---

## 🔍 Code Scanning
- **CodeQL** runs on every PR and weekly on `main`.  
- Blocks merges if high/critical vulnerabilities are detected.  
- Custom CodeQL queries flag unsafe coding patterns (e.g., unsafe subprocess usage).  

---

## 📢 Security Advisories
If a vulnerability is found:
1. Report it privately via GitHub **Security Advisories**.  
2. Do not disclose publicly until a patch is released.  
3. Advisories will be linked to Dependabot alerts automatically if dependency-related.  

---

## 📨 Reporting a Vulnerability
- Open a private **Security Advisory** in this repo.  
- Alternatively, contact the maintainer privately.  
- Please include:
  - A description of the vulnerability.  
  - Steps to reproduce.  
  - Suggested fix (if available).  

---

## ✅ Enforcement
This repo enforces **multi-layer governance**:
- PR templates (general + sensitive).  
- Auto-labeler + CODEOWNERS for sensitive stacks.  
- Workflows: Secrets → Security → CI → Compliance.  
- Post-merge audits: Daily, Weekly, Monthly, Quarterly.  

All contributors must follow these rules.  
PRs or commits violating security policy will be rejected.

---

## 🏢 Business Stack Security

### Sensitive Stacks (Require Enhanced Security)
- **Betting Stack** (`betting/`, `odds_parser.py`, `parlay_builder.py`)
  - Must comply with responsible gaming regulations
  - API rate limiting enforced
  - No underage access logic permitted

- **Cannabis Stack** (`cannabis/`)
  - Must comply with METRC and state regulations
  - Seed-to-sale tracking required
  - Multi-state compliance validation

- **Credit Stack** (`credit/`)
  - PCI DSS compliance required
  - Financial data encryption enforced
  - Credit bureau API security standards

### CODEOWNERS Approval Required
All changes to sensitive stacks require explicit approval from `@Vibehigheric` via CODEOWNERS enforcement.

---

## 🔄 Security Workflow Integration

### PR-Level Security Gates:
1. **Secrets Gate** → `check-secrets.yml` validates environment variables
2. **Security Gate** → `security-scan.yml` runs CodeQL, Gitleaks, Dependency Review
3. **CI/Test Gate** → `ci-all-in-one.yml` ensures code quality and coverage
4. **Compliance Gate** → CODEOWNERS + PR templates enforce business rules

### Post-Merge Security Monitoring:
- **Daily**: Secret and vulnerability scanning
- **Weekly**: Automated dependency updates via Dependabot
- **Monthly**: Badge health monitoring with Telegram alerts
- **Quarterly**: Comprehensive compliance audit with governance validation

---

*This security policy is enforced automatically through GitHub Actions workflows and monitored via Grafana dashboards.*