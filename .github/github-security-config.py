# GitHub Advanced Security Configuration
# Repository-level security settings for EQ12 GODSTACK

# This file documents the required security settings for the EQ12 GODSTACK repository
# These settings should be configured through the GitHub web interface under Settings > Security

# =============================
# REPOSITORY SECURITY SETTINGS
# =============================

REPOSITORY_SECURITY_CONFIG = {
    # Basic Security
    "private_repository": True,
    "restrict_pushes_to_collaborators": True,
    "require_signed_commits": True,
    "enable_vulnerability_alerts": True,
    # GitHub Advanced Security Features (GitHub Enterprise required)
    "advanced_security_enabled": True,
    "secret_scanning_enabled": True,
    "secret_scanning_push_protection": True,
    "dependency_review_enabled": True,
    "code_scanning_enabled": True,
    "codeql_analysis_enabled": True,
    # Security Policies
    "security_policy_file": ".github/SECURITY.md",
    "security_advisory_enabled": True,
    "private_vulnerability_reporting": True,
    # Access Controls
    "restrict_team_access": True,
    "require_2fa": True,
    "codeowners_file": ".github/CODEOWNERS",
}

# =============================
# BRANCH PROTECTION RULES
# =============================

BRANCH_PROTECTION = {
    "main": {
        "protection_enabled": True,
        "required_status_checks": {
            "strict": True,
            "contexts": [
                "GitHub Advanced Security Suite",
                "EQ12 Business Stack Security Validation",
                "Security Policy Enforcement",
                "Regulatory Compliance Validation",
            ],
        },
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "required_approving_review_count": 2,
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True,
            "require_last_push_approval": True,
        },
        "restrictions": {
            "users": ["Vibehigheric"],
            "teams": ["eq12-security-team"],
            "apps": [],
        },
        "allow_force_pushes": False,
        "allow_deletions": False,
        "required_linear_history": True,
        "required_conversation_resolution": True,
    },
    "develop": {
        "protection_enabled": True,
        "required_status_checks": {
            "strict": True,
            "contexts": [
                "GitHub Advanced Security Suite",
                "EQ12 Business Stack Security Validation",
            ],
        },
        "required_pull_request_reviews": {
            "required_approving_review_count": 1,
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True,
        },
        "allow_force_pushes": False,
        "allow_deletions": False,
    },
}

# =============================
# SECRET SCANNING CONFIGURATION
# =============================

SECRET_SCANNING_CONFIG = {
    "enabled": True,
    "push_protection_enabled": True,
    # Custom patterns for EQ12-specific secrets
    "custom_patterns": [
        {
            "name": "EQ12 API Keys",
            "pattern": r"eq12_[a-zA-Z0-9]{32,}",
            "description": "EQ12 internal API keys",
        },
        {
            "name": "Sports Betting API Keys",
            "pattern": r"(draftkings|fanduel|bovada)_[a-zA-Z0-9]{20,}",
            "description": "Sports betting platform API keys",
        },
        {
            "name": "Cannabis API Keys",
            "pattern": r"(metrc|leaflogix|biotrack)_[a-zA-Z0-9]{20,}",
            "description": "Cannabis compliance platform API keys",
        },
        {
            "name": "Credit Bureau API Keys",
            "pattern": r"(experian|equifax|transunion)_[a-zA-Z0-9]{20,}",
            "description": "Credit bureau API keys",
        },
    ],
    # Alert settings
    "alert_threshold": "high",
    "notification_settings": {"email": True, "web": True, "security_advisories": True},
}

# =============================
# CODE SCANNING CONFIGURATION
# =============================

CODE_SCANNING_CONFIG = {
    "enabled": True,
    "codeql_enabled": True,
    # CodeQL configuration
    "codeql_config": {
        "languages": ["python", "javascript", "typescript"],
        "queries": ["security-extended", "security-and-quality"],
        "paths_ignore": ["node_modules/**", "venv/**", ".git/**", "logs/**", "*.log"],
        "paths": [
            "scripts/**",
            "omni_scraper/**",
            "scraper_starter/**",
            "dashboard/**",
        ],
    },
    # Third-party integrations
    "third_party_tools": [
        {
            "name": "Bandit",
            "language": "python",
            "config": "bandit -r . -f sarif -o bandit.sarif",
        },
        {
            "name": "ESLint Security",
            "language": "javascript",
            "config": "eslint --format @microsoft/eslint-formatter-sarif",
        },
        {
            "name": "Semgrep",
            "language": "multi",
            "config": "semgrep --config=auto --sarif --output=semgrep.sarif",
        },
    ],
    # Alert settings
    "alert_settings": {
        "severity_threshold": "medium",
        "auto_dismiss_rules": ["test files", "example code", "documentation"],
    },
}

# =============================
# DEPENDENCY SECURITY SETTINGS
# =============================

DEPENDENCY_SECURITY = {
    "dependency_graph_enabled": True,
    "dependency_review_enabled": True,
    "dependabot_alerts_enabled": True,
    "dependabot_security_updates": True,
    # Dependabot configuration
    "dependabot_config": {
        "update_schedule": "daily",
        "security_updates_only": False,
        "auto_merge_security_updates": True,
        "reviewer_requirements": {
            "security_updates": 0,  # Auto-approve security updates
            "version_updates": 1,  # Require review for version updates
        },
    },
    # Vulnerability thresholds
    "vulnerability_thresholds": {
        "critical": "block_merge",
        "high": "require_review",
        "medium": "warn_only",
        "low": "ignore",
    },
    # License compliance
    "license_policy": {
        "allowed_licenses": [
            "MIT",
            "Apache-2.0",
            "BSD-3-Clause",
            "BSD-2-Clause",
            "ISC",
            "GPL-3.0",
            "LGPL-2.1",
            "LGPL-3.0",
        ],
        "forbidden_licenses": ["AGPL-3.0", "GPL-2.0-only", "WTFPL"],
    },
}

# =============================
# SUPPLY CHAIN SECURITY
# =============================

SUPPLY_CHAIN_CONFIG = {
    "sbom_generation": True,
    "package_provenance": True,
    "vulnerability_database_sync": True,
    # Package verification
    "package_verification": {
        "npm_packages": True,
        "pypi_packages": True,
        "github_actions": True,
        "docker_images": True,
    },
    # Signing requirements
    "signing_requirements": {"commits": True, "tags": True, "releases": True},
    # Attestation requirements
    "attestation": {
        "build_provenance": True,
        "slsa_level": 3,
        "sigstore_integration": True,
    },
}

# =============================
# SECURITY MONITORING
# =============================

SECURITY_MONITORING = {
    "security_events_log": True,
    "audit_log_streaming": True,
    # Monitoring thresholds
    "alert_thresholds": {
        "failed_login_attempts": 5,
        "suspicious_ip_access": True,
        "unusual_download_patterns": True,
        "privilege_escalation": True,
    },
    # Integration with external tools
    "siem_integration": {
        "enabled": False,  # Configure if enterprise SIEM available
        "endpoint": "https://siem.eq12-internal.local/webhook",
        "auth_method": "token",
    },
    # Notification channels
    "notification_channels": [
        {
            "type": "email",
            "address": "security@eq12-internal.local",
            "events": ["critical", "high"],
        },
        {"type": "slack", "webhook": "SLACK_SECURITY_WEBHOOK", "events": ["all"]},
        {
            "type": "telegram",
            "bot_token": "TELEGRAM_BOT_TOKEN",
            "chat_id": "TELEGRAM_SECURITY_CHAT_ID",
            "events": ["critical", "high", "medium"],
        },
    ],
}

# =============================
# COMPLIANCE CONFIGURATION
# =============================

COMPLIANCE_CONFIG = {
    "regulatory_frameworks": [
        "SOC2_TYPE2",
        "GDPR",
        "CCPA",
        "PCI_DSS",  # If handling payment data
        "FCRA",  # For credit-related operations
        "HIPAA",  # If handling health data (cannabis medical)
    ],
    # Data classification
    "data_classification": {
        "public": ["documentation", "marketing"],
        "internal": ["business_logic", "configurations"],
        "confidential": ["api_keys", "customer_data"],
        "restricted": ["financial_data", "compliance_records"],
    },
    # Retention policies
    "data_retention": {
        "security_logs": "7_years",
        "audit_trails": "7_years",
        "vulnerability_reports": "3_years",
        "incident_reports": "7_years",
    },
    # Compliance automation
    "automated_compliance": {
        "policy_enforcement": True,
        "audit_trail_generation": True,
        "compliance_reporting": True,
        "evidence_collection": True,
    },
}

# =============================
# INCIDENT RESPONSE CONFIG
# =============================

INCIDENT_RESPONSE = {
    "automated_response": {
        "secret_exposure": "revoke_and_regenerate",
        "vulnerability_detection": "create_security_advisory",
        "compliance_violation": "block_and_alert",
        "suspicious_access": "rate_limit_and_monitor",
    },
    "escalation_matrix": {
        "critical": {
            "response_time": "15_minutes",
            "escalation_path": ["security_lead", "cto", "legal"],
        },
        "high": {
            "response_time": "1_hour",
            "escalation_path": ["security_lead", "dev_lead"],
        },
        "medium": {"response_time": "4_hours", "escalation_path": ["security_lead"]},
        "low": {"response_time": "24_hours", "escalation_path": ["dev_team"]},
    },
    "communication_templates": {
        "internal_alert": ".github/templates/security_alert_internal.md",
        "customer_notification": ".github/templates/security_notification_customer.md",
        "regulatory_report": ".github/templates/security_report_regulatory.md",
    },
}

# =============================
# SECURITY CONFIGURATION NOTES
# =============================

"""
IMPLEMENTATION CHECKLIST:

Repository Settings:
□ Enable private repository
□ Configure branch protection rules
□ Set up CODEOWNERS file
□ Enable vulnerability alerts

GitHub Advanced Security:  
□ Enable Advanced Security features
□ Configure secret scanning with push protection
□ Set up CodeQL analysis
□ Enable dependency review
□ Configure custom secret patterns

Access Management:
□ Enable 2FA requirement
□ Configure team access restrictions  
□ Set up signed commit requirement
□ Review collaborator permissions

Monitoring & Alerts:
□ Configure notification channels
□ Set up security event monitoring
□ Enable audit log streaming
□ Configure SIEM integration (if available)

Compliance:
□ Document regulatory requirements
□ Set up compliance automation
□ Configure data classification
□ Implement retention policies

Incident Response:
□ Create incident response procedures
□ Set up escalation matrix
□ Configure automated responses
□ Prepare communication templates

SECURITY VALIDATION:
- Test secret scanning with dummy secrets
- Verify branch protection enforcement
- Validate CodeQL analysis results
- Check dependency vulnerability detection
- Test incident response procedures

REGULATORY CONSIDERATIONS:
- Gambling/Sports Betting: Ensure responsible use disclaimers
- Cannabis: Verify state-legal compliance requirements  
- Financial/Credit: Implement FCRA compliance measures
- General: Meet data protection and privacy requirements

This configuration provides enterprise-grade security for the EQ12 GODSTACK
private repository, with specialized protections for sensitive business stacks.
"""
