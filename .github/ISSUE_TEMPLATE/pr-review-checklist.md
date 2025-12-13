---
name: "PR Review Checklist (Copilot)"
about: "Use this issue to ensure each PR is reviewed with Copilot against EQ12 GODSTACK governance rules."
title: "PR Review Checklist for #<PR_NUMBER>"
labels: ["governance", "review-needed"]
assignees: ["Vibehigheric"]
---

# ✅ EQ12 GODSTACK PR Review Checklist

This issue is automatically linked to PR **#<PR_NUMBER>**.  
Before merge, run GitHub Copilot Chat with the prompts in [COPILOT_REVIEW.md](../COPILOT_REVIEW.md).

---

## 🔒 Gates
- [ ] Secrets Gate – `check-secrets.yml`
- [ ] Security Gate – `security-scan.yml`
- [ ] CI/Test Gate – `ci-all-in-one.yml`
- [ ] Compliance Gate – PR templates + CODEOWNERS

---

## 🧩 Sensitive Modules
If PR touches:
- `betting/`
- `cannabis/`
- `credit/`

Run Copilot with **Sensitive Module Review** prompts.

---

## 📊 Copilot Review Prompts
Use Copilot Chat:
- **General Governance Review**
- **Sensitive Module Review** (if applicable)
- **Test & Coverage Review**
- **Security Review**
- **Governance Report Prompt**

---

## 👀 Reviewer Action
- [ ] Copilot review completed
- [ ] All governance gates green ✅
- [ ] Sensitive module compliance confirmed (if applicable)

---

🔗 PR: #<PR_NUMBER>