# 🤖 EQ12 GODSTACK – Copilot PR Review Guide

This guide contains ready-to-use prompts for GitHub Copilot Chat to review **pull requests** in this repo according to our **governance rules**.

---

## 🔒 General Governance Review
Prompt Copilot with:

```
Review this PR for EQ12 GODSTACK.
Check against governance gates:

* Secrets Gate (check-secrets.yml)
* Security Gate (security-scan.yml → CodeQL, Gitleaks, Dep Review)
* CI/Test Gate (ci-all-in-one.yml → lint, tests, coverage)
* Compliance Gate (PR templates + CODEOWNERS)

List:
✅ Pass or ❌ Fail for each gate, with reasons.
```

---

## 🧩 Sensitive Module Review
For PRs in `betting/`, `cannabis/`, or `credit/` folders:

```
Review this PR as a sensitive stack change.
Checklist:

* Did the author use the sensitive_module PR template?
* Are CODEOWNERS approvals required and present?
* Are there any secrets (API keys, tokens) accidentally committed?
* Do changes respect compliance (e.g., no underage gambling logic, no illegal cannabis flows)?
* Are enrichment + Telegram alerts handled properly?

Respond with a Pass/Fail for compliance, and suggest fixes if ❌.
```

---

## 🧪 Test & Coverage Review
For any code changes:

```
Check this PR for test coverage.

* Are new functions covered by pytest tests?
* Does coverage likely remain ≥70%?
* Suggest missing test cases if any.
```

---

## 🛡️ Security Review
```
Scan this PR for:

* Hardcoded secrets or credentials
* Use of unsafe functions (eval, exec, subprocess without sanitization)
* Dependency changes that may introduce vulnerabilities
* Compliance with security workflows (CodeQL, Gitleaks, Dependency Review)
```

---

## 📊 Governance Report Prompt
After a PR review:

```
Summarize governance compliance for this PR.

* Secrets Gate: ✅/❌
* Security Gate: ✅/❌
* CI/Test Gate: ✅/❌
* Compliance Gate: ✅/❌
  Overall Recommendation: Merge / Needs Fix
```

---

# ✅ Usage Tips
- Run these prompts in **Copilot Chat (PR view)** → Copilot will analyze diff & context.  
- Pair with **PR Templates**: Copilot can cross-check PR description vs template requirements.  
- For **sensitive stacks**, always run the "Sensitive Module Review" prompt.  

---

# 📅 Workflow Integration
- Use this guide with:
  - **Secrets Gate** (`check-secrets.yml`)  
  - **Security Gate** (`security-scan.yml`)  
  - **CI/Test Gate** (`ci-all-in-one.yml`)  
  - **Compliance Gate** (PR templates + CODEOWNERS)  

Together, Copilot Chat + automated workflows give you **human + AI double coverage** on every PR.