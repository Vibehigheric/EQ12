# EQ12 GODSTACK Branch Protection Configuration
# Apply these settings in GitHub repository settings

## Main Branch Protection (production)
```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "ci/secret-scan",
      "ci/lint-python", 
      "ci/lint-powershell",
      "ci/test-python",
      "ci/test-eq12-components",
      "compliance/detect-sensitive",
      "compliance/regulatory-compliance"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "bypass_pull_request_allowances": {
      "users": ["Vibehigheric"]
    }
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": true,
  "required_conversation_resolution": true
}
```

## Develop Branch Protection (staging)
```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "ci/secret-scan",
      "ci/lint-python",
      "ci/test-python"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": false,
    "require_code_owner_reviews": true
  },
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

## Sensitive Module Branch Rules

### Betting/Gambling Branches
- Require @Vibehigheric approval
- Additional compliance checks mandatory
- No auto-merge allowed

### Cannabis/CBD Branches  
- Require @Vibehigheric approval
- Regulatory compliance verification
- Legal review for major changes

### Credit/Financial Branches
- Require @Vibehigheric approval
- Data protection compliance
- FCRA compliance verification

## Repository Settings

### General Settings
- Private repository (required)
- Issues enabled
- Projects disabled (use external tracking)
- Wiki disabled
- Discussions disabled

### Security Settings  
- Dependency graph enabled
- Dependabot alerts enabled
- Dependabot security updates enabled
- Code scanning enabled
- Secret scanning enabled
- Push protection enabled

### Merge Settings
- Allow merge commits: ✅ Enabled
- Allow squash merging: ✅ Enabled  
- Allow rebase merging: ✅ Enabled
- Automatically delete head branches: ✅ Enabled

### Branch Settings
- Default branch: main
- Branch protection rules applied as above
- Signed commits encouraged (not required)

## Webhook Configuration (Optional)

### Telegram Notifications
```json
{
  "url": "https://api.telegram.org/bot{TOKEN}/sendMessage",
  "content_type": "json",
  "events": [
    "pull_request",
    "push",
    "release"
  ],
  "active": true
}
```

### Security Monitoring
```json
{
  "url": "https://your-security-endpoint.com/webhook",
  "content_type": "json", 
  "events": [
    "security_advisory",
    "repository_vulnerability_alert"
  ],
  "active": true
}
```