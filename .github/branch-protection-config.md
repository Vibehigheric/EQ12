# GitHub Branch Protection Configuration for EQ12
# ==============================================
# This file documents the branch protection settings that should be configured
# in the GitHub repository settings to ensure comprehensive security and quality control.

# ⚠️  IMPORTANT: This file serves as documentation for manual GitHub configuration
# Branch protection rules must be configured manually in GitHub repository settings:
# Settings → Branches → Add branch protection rule

# 🔐 Main Branch Protection Rules
# ==============================

main_branch_protection:
  branch_name: "main"
  protection_rules:
    # 🛡️ Basic Protection
    restrict_pushes: true
    allow_force_pushes: false
    allow_deletions: false

    # 👥 Pull Request Requirements
    require_pull_requests: true
    required_reviewers: 2
    dismiss_stale_reviews: true
    require_code_owner_reviews: true
    restrict_review_dismissals: true

    # 🧪 Status Check Requirements
    require_status_checks: true
    require_branches_up_to_date: true
    required_status_checks:
      - "CodeQL Analysis"
      - "Dependency Review"
      - "Security Scan"
      - "Safety Check"
      - "Bandit Security Scan"
      - "Pre-commit Hooks"
      - "Python Tests"
      - "Type Check (mypy)"
      - "Lint Check (ruff)"
      - "Format Check (black)"

    # 👑 Admin Enforcement
    enforce_admins: true
    include_administrators: true

    # 🔄 Linear History
    require_linear_history: true

    # 💬 Conversation Resolution
    require_conversation_resolution: true

    # 🔒 Signed Commits
    require_signed_commits: true

# 🚀 Development Branch Protection Rules
# =====================================

development_branch_protection:
  branch_name: "develop"
  protection_rules:
    # 🛡️ Basic Protection
    restrict_pushes: false  # Allow direct pushes for development
    allow_force_pushes: true  # Allow force pushes for rebasing
    allow_deletions: false

    # 👥 Pull Request Requirements
    require_pull_requests: true
    required_reviewers: 1
    dismiss_stale_reviews: false
    require_code_owner_reviews: false

    # 🧪 Status Check Requirements
    require_status_checks: true
    require_branches_up_to_date: false  # Less strict for development
    required_status_checks:
      - "Pre-commit Hooks"
      - "Python Tests"
      - "Security Scan"

    # 👑 Admin Enforcement
    enforce_admins: false  # Allow admins to bypass for hotfixes

    # 🔒 Signed Commits
    require_signed_commits: false  # Optional for development

# 🔥 Hotfix Branch Protection Rules
# =================================

hotfix_branch_protection:
  branch_pattern: "hotfix/*"
  protection_rules:
    # 🛡️ Basic Protection
    restrict_pushes: false
    allow_force_pushes: true
    allow_deletions: true

    # 👥 Pull Request Requirements
    require_pull_requests: true
    required_reviewers: 1  # Fast-track for critical fixes
    dismiss_stale_reviews: false

    # 🧪 Status Check Requirements
    require_status_checks: true
    required_status_checks:
      - "Security Scan"  # Minimal checks for hotfixes
      - "Python Tests"

    # 👑 Admin Enforcement
    enforce_admins: false

# 🌟 Feature Branch Protection Rules
# ==================================

feature_branch_protection:
  branch_pattern: "feature/*"
  protection_rules:
    # 🛡️ Basic Protection
    restrict_pushes: false
    allow_force_pushes: true
    allow_deletions: true

    # 👥 Pull Request Requirements
    require_pull_requests: false  # Allow direct development

    # 🧪 Status Check Requirements
    require_status_checks: false  # No requirements for feature branches

    # 👑 Admin Enforcement
    enforce_admins: false

# 🔧 Configuration Steps for GitHub UI
# ===================================

github_configuration_steps: |
  1. Navigate to Repository Settings
     - Go to https://github.com/[username]/EQ12/settings

  2. Access Branch Protection Rules
     - Click "Branches" in the left sidebar
     - Click "Add branch protection rule"

  3. Configure Main Branch Protection
     - Branch name pattern: "main"
     - ✅ Restrict pushes that create files larger than 100 MB
     - ✅ Require a pull request before merging
       - ✅ Require approvals: 2
       - ✅ Dismiss stale pull request approvals when new commits are pushed
       - ✅ Require review from code owners
       - ✅ Restrict pushes that create files larger than 100 MB
     - ✅ Require status checks to pass before merging
       - ✅ Require branches to be up to date before merging
       - Add required status checks (see list above)
     - ✅ Require conversation resolution before merging
     - ✅ Require signed commits
     - ✅ Require linear history
     - ✅ Include administrators

  4. Configure Additional Branches
     - Repeat process for develop, hotfix/*, feature/* patterns
     - Adjust settings according to rules defined above

  5. Verify Configuration
     - Test with a test branch and pull request
     - Ensure all status checks are properly configured
     - Verify CODEOWNERS file is being respected

# 🔍 Status Check Configuration
# ============================

required_github_actions: |
  The following GitHub Actions must be configured to provide required status checks:

  1. .github/workflows/security.yml (Already created)
     - Provides: CodeQL Analysis, Dependency Review, Security Scan

  2. .github/workflows/python-ci.yml (To be created)
     - Provides: Python Tests, Type Check, Lint Check, Format Check

  3. .github/workflows/pre-commit.yml (To be created)
     - Provides: Pre-commit Hooks validation

# 🚨 Security Enforcement Levels
# ==============================

security_enforcement:
  critical_files:
    - "**/*secret*"
    - "**/*key*"
    - "**/*credential*"
    - "**/config*.json"
    - "**/*.env*"
    enforcement: "BLOCK - No exceptions, admin override required"

  betting_data:
    - "data/**/*"
    - "**/betting*"
    - "**/odds*"
    - "**/bankroll*"
    enforcement: "REVIEW - Require data steward approval"

  core_algorithms:
    - "**/eq12_*.py"
    - "**/edge_god*"
    - "**/parlay*"
    - "scripts/**/*"
    enforcement: "REVIEW - Require algorithm expert approval"

  infrastructure:
    - ".github/**/*"
    - "docker*"
    - "*.yml"
    - "*.yaml"
    enforcement: "REVIEW - Require DevOps approval"

# 📋 Compliance Requirements
# =========================

compliance_checklist: |
  Before enabling branch protection, ensure:

  ✅ CODEOWNERS file is properly configured
  ✅ Required GitHub Actions workflows are active
  ✅ Team members have appropriate repository permissions
  ✅ GPG signing is configured for required contributors
  ✅ All status checks are passing on existing branches
  ✅ Emergency bypass procedures are documented
  ✅ Compliance team has reviewed gambling-related restrictions

# 🆘 Emergency Procedures
# =======================

emergency_bypass: |
  In case of critical production issues requiring immediate bypass:

  1. Document the emergency in GitHub issue
  2. Tag @admin team for approval
  3. Use admin override with justification comment
  4. Create follow-up issue for post-incident review
  5. Restore branch protection immediately after fix

  NEVER bypass security scans even in emergencies.
  If security scan fails, contact security team immediately.

# 📊 Monitoring and Alerts
# ========================

monitoring_setup: |
  Configure GitHub repository alerts for:

  1. Branch protection rule changes
  2. Failed required status checks
  3. Admin override usage
  4. Security scan failures
  5. Large file commits
  6. Unsigned commits on protected branches

  Integrate alerts with:
  - Slack channel: #eq12-security-alerts
  - Email notifications to security team
  - PagerDuty for critical security failures

# 📈 Success Metrics
# ==================

success_metrics: |
  Track these metrics to measure branch protection effectiveness:

  - % of commits requiring review (target: 100% on main)
  - Average time to review and merge (target: <24 hours)
  - Number of security scan failures caught (higher is better)
  - Compliance violation prevention rate (target: 100%)
  - Emergency bypass frequency (target: <1 per month)

# 🔄 Regular Review Process
# =========================

review_schedule: |
  Quarterly review of branch protection rules:

  1. Review effectiveness of current rules
  2. Assess new security requirements
  3. Update required status checks
  4. Review emergency bypass usage
  5. Update CODEOWNERS as needed
  6. Train team on any rule changes

# END OF CONFIGURATION
# ===================
#
# This file should be kept up-to-date with actual GitHub settings.
# Any changes to branch protection rules should be documented here first,
# then implemented in GitHub, ensuring consistency and auditability.
