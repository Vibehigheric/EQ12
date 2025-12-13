## 📋 Pull Request Information

**Type of Change** (select all that apply):
- [ ] � Security-related change
- [ ] ⚙️ Infrastructure/DevOps change
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] � Documentation update
- [ ] 🎨 Code style/formatting change
- [ ] ♻️ Refactoring (no functional changes)

## 🎯 Business Stack Impact

**Which business stacks does this PR affect?** (Critical for compliance review):
- [ ] 🎰 **Betting Stack** (Gambling regulations - requires compliance review)
- [ ] 🌿 **Cannabis Stack** (METRC/State compliance - requires compliance review)
- [ ] 💳 **Credit Stack** (PCI DSS/Financial - requires compliance review)
- [ ] 🏪 E-commerce Stack
- [ ] � AI/Automation Stack
- [ ] 📊 Analytics/Scraping Stack
- [ ] 🔧 Infrastructure/DevOps
- [ ] 📱 Mobile Applications
- [ ] None specifically

## 📖 Description

**Summary of Changes:**
<!-- Provide a clear and concise description of what this PR does -->

**Related Issue(s):**
<!-- Link to related issues using #issue_number -->
- Fixes #
- Relates to #

**Motivation and Context:**
<!-- Why is this change required? What problem does it solve? -->

## 🧪 Testing

**How has this been tested?**
- [ ] Unit tests added/updated (`pytest -q`)
- [ ] Pester tests pass (`Invoke-Pester`)
- [ ] Integration tests added/updated
- [ ] Manual testing performed
- [ ] Regression testing completed
- [ ] Performance testing completed
- [ ] Security testing performed (for security-related changes)

**Test Coverage:**
<!-- Describe the test coverage and any testing limitations -->

## ✅ Pre-merge Checklist

**Code Quality:**
- [ ] Code follows EQ12 coding standards
- [ ] Self-review of code completed
- [ ] Code has been reviewed by peers
- [ ] Comments added to hard-to-understand areas
- [ ] No debugging code or console logs left in

**Security & Compliance:**
- [ ] No secrets, API keys, or sensitive data in code
- [ ] Security implications reviewed
- [ ] Compliance requirements checked (especially for sensitive stacks)
- [ ] Dependencies are up-to-date and secure
- [ ] Appropriate error handling implemented

**Documentation:**
- [ ] Documentation updated (if applicable)
- [ ] README updated (if applicable)
- [ ] API documentation updated (if applicable)
- [ ] Changelog updated (if applicable)

**Deployment:**
- [ ] Changes are backward compatible
- [ ] Database migrations included (if applicable)
- [ ] Environment variables documented (if applicable)
- [ ] Deployment instructions provided (if applicable)

**GitLens Review:**
- [ ] Used GitLens to review blame/authorship for all touched lines
- [ ] Verified no secrets in diff (keys, tokens)
- [ ] Lint passed locally (ruff)
- [ ] Security scans passed (bandit, pip-audit)
- [ ] Tests added/updated where applicable
- [ ] Linked related issue(s)

## 🚨 Breaking Changes

<!-- If this PR introduces breaking changes, describe them here -->

**Migration Guide:**
<!-- Provide instructions for users to migrate from the old version -->

## � Additional Notes

<!-- Any additional information that reviewers should know -->

**Deployment Notes:**
<!-- Special deployment considerations, rollback plans, etc. -->

**Performance Impact:**
<!-- Expected performance implications -->

**Risk Assessment:**
<!-- Assess the risk level of these changes -->

---

## 🔍 For Reviewers

**Focus Areas for Review:**
<!-- Guide reviewers on what to focus on -->

**Testing Instructions:**
<!-- How reviewers can test these changes -->

**Questions for Reviewers:**
<!-- Specific questions you want reviewers to consider -->

---

**📋 Governance Reminder:** This PR will go through automated governance gates including secret scanning, security analysis, and compliance checks. Sensitive business stack changes require additional approvals as defined in CODEOWNERS.
