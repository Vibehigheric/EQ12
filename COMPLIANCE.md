# 📜 Compliance Policy – EQ12 GODSTACK

This repository enforces strict compliance rules for **sensitive modules** (Betting, Cannabis, Credit/Housing) and general governance.

---

## 🧩 Sensitive Stacks

The following stacks are considered **sensitive** and require additional review:

- 🏈 `betting/` – Sports betting logic & OddsAPI integrations  
- 🌿 `cannabis/` – Cannabis / CBD intelligence modules  
- 🏠 `credit/` – Credit & housing market analysis

---

## 🔒 Sensitive PR Requirements
- Must use the **Sensitive Module PR Template**:
  - `.github/PULL_REQUEST_TEMPLATE/sensitive_module.md`
- Must receive explicit approval from a **CODEOWNER**:
  - See `.github/CODEOWNERS` for reviewer assignments.
- Must pass all **governance gates**:
  - ✅ Secrets Gate (`check-secrets.yml`)  
  - ✅ Security Gate (`security-scan.yml`)  
  - ✅ CI/Test Gate (`ci-all-in-one.yml`)  
  - ✅ Compliance Gate (PR templates + CODEOWNERS)

---

## ⚙️ General Governance Rules
- **General PRs**: use `.github/PULL_REQUEST_TEMPLATE.md`.  
- **Auto-labeler** applies labels based on folder changes:
  - `⚠ Sensitive: Betting`  
  - `⚠ Sensitive: Cannabis`  
  - `⚠ Sensitive: Credit`  
- **Governance Board** tracks PR status:
  - 🚧 Needs Copilot Review  
  - 🔍 In Governance Review  
  - ✅ Ready for Merge  
  - ⏳ Blocked  

---

## 🛡️ Compliance Workflows
1. **Auto-labeler** → flags sensitive PRs.  
2. **Governance Board Sync** → moves cards automatically.  
3. **Copilot Review** → reviewers run prompts in `COPILOT_REVIEW.md`.  
4. **CI/CD + Security Workflows**:
   - `check-secrets.yml` → ensures required secrets present.  
   - `security-scan.yml` → CodeQL, Gitleaks, Dependency Review.  
   - `ci-all-in-one.yml` → lint, tests, coverage.  
   - `governance-board-sync.yml` → syncs PRs/issues with Governance Board.

### Workflow Security Requirements
- **SHA-pinned Actions**: All third-party actions must use SHA commits, not tags
- **CODEOWNERS Approval**: Required for all `.github/workflows/` modifications
- **Workflow Auditing**: All workflow changes logged and reviewed quarterly
- **Action Validation**: Only verified publishers and trusted actions allowed
- **Secrets Access**: Workflow secrets limited to minimum required scope
- **Branch Protection**: Workflow files protected by branch protection rules

---

## 📅 Post-Merge Compliance Audits
- **Daily**: Trending + News alerts with enrichment (Telegram).  
- **Weekly**: CI scheduled run.  
- **Monthly**: BadgeCheck → verifies all badges green.  
- **Quarterly**: Compliance Audit → validates CODEOWNERS, PR templates, secrets, and governance health.

---

## ✅ Enforcement
- Sensitive PRs cannot merge without CODEOWNERS approval.  
- All PRs blocked until governance gates pass.  
- Post-merge audits generate **Telegram alerts** for compliance failures.  

Failure to follow compliance rules will result in:
- ❌ PR rejection  
- ❌ Branch protection enforcement  
- ❌ Issue logged in Governance Board

---

## 📢 Contact
For compliance questions or escalations:  
📧 **compliance@eq12-godstack.local** (placeholder, replace with real contact)

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

*This compliance policy is enforced automatically through GitHub Actions workflows and monitored via Grafana dashboards.*