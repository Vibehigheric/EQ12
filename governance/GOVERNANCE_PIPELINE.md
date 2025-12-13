# ⚖️ EQ12 GODSTACK – Governance Pipeline

This document explains the **end-to-end governance pipeline** for EQ12 GODSTACK.
It connects **PR templates → auto-labels → workflows → Governance Board → audits** into one cohesive flow.

---

## 🔑 Step 1: Pull Request Templates

* **General PRs** → `.github/PULL_REQUEST_TEMPLATE.md`
* **Sensitive stacks (betting, cannabis, credit)** → `.github/PULL_REQUEST_TEMPLATE/sensitive_module.md`

✅ Ensures authors complete **security, compliance, and testing checklists**.

---

## 🏷️ Step 2: Auto-Labeler

* Config: `.github/labeler.yml` + `.github/workflows/auto-label.yml`
* Labels PRs automatically based on folder/file changes:

  * `⚠ Sensitive: Betting`, `⚠ Sensitive: Cannabis`, `⚠ Sensitive: Credit`
  * `Travel`, `Fleet`, `AliDropship`
  * `Governance`, `CI/CD`, `Docs`

✅ Sensitive PRs instantly flagged without manual labeling.

---

## 🛡️ Step 3: Workflow Gates

1. **Secrets Gate** → `check-secrets.yml`

   * Blocks PRs missing required secrets.

2. **Security Gate** → `security-scan.yml`

   * Runs CodeQL, Gitleaks, Dependency Review.

3. **CI/Test Gate** → `ci-all-in-one.yml`

   * Runs lint, tests, coverage, Codecov, SonarCloud.

4. **Compliance Gate** → CODEOWNERS + PR templates

   * Ensures sensitive stacks require your approval.

✅ No PR can merge without passing all gates.

---

## 📊 Step 4: Governance Board

* Config: `.github/projects/governance-board.yml`

* Columns:

  * 🚧 Needs Copilot Review
  * 🔍 In Governance Review
  * ✅ Ready for Merge
  * ⏳ Blocked

* **Sync workflow**: `.github/workflows/governance-board-sync.yml`

  * Moves PRs/issues between columns automatically based on labels & workflow results.

✅ Visual dashboard for governance tracking.

---

## 🤖 Step 5: Copilot Review

* Guide: `COPILOT_REVIEW.md`
* Issue template: `.github/ISSUE_TEMPLATE/pr-review-checklist.md`
* Reminder workflow: `.github/workflows/pr-review-reminder.yml`

✅ Copilot Chat reviews PRs against governance rules before merge.

---

## 📅 Step 6: Post-Merge Audits

* **Daily**: TrendingMonitor + NewsAggregator + enrichment → Telegram
* **Weekly**: Scheduled CI runs → health verification
* **Monthly**: `badge_check.py` → badge audit → Telegram
* **Quarterly**: `compliance_audit.py` → governance review + key rotation reminders

✅ Ensures ongoing repo health, not just PR-time checks.

---

## 🖼️ Visual Governance Flow

```mermaid
flowchart TD
    PR[Pull Request] --> T[PR Template (General/Sensitive)]
    T --> L[Auto-Labeler]
    L --> G1[Secrets Gate]
    L --> G2[Security Gate]
    L --> G3[CI/Test Gate]
    L --> G4[Compliance Gate]

    G1 --> B[Governance Board]
    G2 --> B
    G3 --> B
    G4 --> B

    B --> Copilot[Copilot Review + Issue Checklist]
    Copilot --> Merge[✅ Merge Allowed]

    Merge --> Daily[Daily Audits]
    Merge --> Weekly[Weekly CI]
    Merge --> Monthly[BadgeCheck]
    Merge --> Quarterly[Compliance Audit]

    style PR fill:#f6f8fa,stroke:#0366d6,stroke-width:2px
    style T fill:#fef6e7,stroke:#d97706,stroke-width:2px
    style L fill:#fee2e2,stroke:#dc2626,stroke-width:2px
    style G1 fill:#e0f2fe,stroke:#0284c7,stroke-width:2px
    style G2 fill:#e0f2fe,stroke:#0284c7,stroke-width:2px
    style G3 fill:#e0f2fe,stroke:#0284c7,stroke-width:2px
    style G4 fill:#e0f2fe,stroke:#0284c7,stroke-width:2px
    style B fill:#ede9fe,stroke:#7c3aed,stroke-width:2px
    style Copilot fill:#dcfce7,stroke:#16a34a,stroke-width:2px
    style Merge fill:#dcfce7,stroke:#16a34a,stroke-width:3px
```

---

## 📋 Governance Labels & Automation

### Auto-Applied Labels:
- `⚠ Sensitive: Betting` → PRs touching betting logic
- `⚠ Sensitive: Cannabis` → PRs touching cannabis compliance  
- `⚠ Sensitive: Credit` → PRs touching financial data
- `Governance` → PRs modifying governance files
- `CI/CD` → PRs modifying workflows or DevContainers
- `Docs` → Documentation-only changes

### Board Movement Rules:
- **New PR** → 🚧 Needs Copilot Review
- **Has `review-needed` label** → 🚧 Needs Copilot Review  
- **Sensitive + under review** → 🔍 In Governance Review
- **All checks pass** → ✅ Ready for Merge
- **CI/Security failures** → ⏳ Blocked
- **Merged/Closed** → Archived

---

## 🔄 Complete Workflow Example

1. **Developer opens PR** touching `betting/odds_parser.py`
2. **Auto-labeler** applies `⚠ Sensitive: Betting` label
3. **PR Review Reminder** creates governance checklist issue
4. **Governance Board Sync** moves PR to 🚧 Needs Copilot Review
5. **Security Gate** runs CodeQL + Gitleaks scan
6. **CODEOWNERS** requires your approval (sensitive stack)
7. **Copilot Review** validates compliance using prompts
8. **Board Sync** moves to ✅ Ready for Merge (all gates pass)
9. **Post-merge**: Monthly badge check + quarterly compliance audit

---

## ✅ Summary

* **PR Stage**: Templates + auto-labeler enforce governance from the start.
* **Workflow Gates**: Secrets, Security, CI, Compliance block unsafe merges.
* **Governance Board**: Tracks every PR/issue visually.
* **Copilot Review**: AI-assisted PR compliance auditing.
* **Post-Merge Audits**: Daily → Weekly → Monthly → Quarterly health checks.

With this pipeline, **no unsafe or non-compliant change can enter `main`**, and EQ12 GODSTACK stays healthy long-term.

---

## 🚀 Quick Setup Checklist

- [ ] Enable GitHub Projects (beta) in repository settings
- [ ] Configure repository secrets (TG_TOKEN, OPENAI_SERVICE_KEY, etc.)
- [ ] Set up CODEOWNERS file with sensitive stack approvals
- [ ] Test auto-labeling with a sample PR
- [ ] Verify Governance Board appears in Projects tab
- [ ] Run Copilot Chat with prompts from COPILOT_REVIEW.md

---

*This governance pipeline ensures enterprise-grade compliance for all EQ12 GODSTACK business stacks.*