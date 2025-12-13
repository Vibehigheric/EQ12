# EQ12 Security Monitoring & Compliance Configuration
# ==================================================

# This file defines the comprehensive security monitoring setup for the EQ12 platform,
# including automated scanning schedules, alert routing, compliance reporting, and
# incident response procedures.

# 📊 Security Monitoring Dashboard Configuration
security_monitoring:
  platform: "GitHub Advanced Security + Custom Monitoring"
  primary_tools:
    - "GitHub Security Advisories"
    - "CodeQL Analysis"
    - "Dependabot"
    - "Secret Scanning"
    - "Custom EQ12 Security Scripts"

  monitoring_frequency:
    continuous: ["Secret Scanning", "Code Push Analysis"]
    daily: ["Dependency Vulnerability Check", "Custom Security Audit"]
    weekly: ["Full Repository Scan", "Compliance Report Generation"]
    monthly: ["Security Posture Assessment", "Threat Model Review"]

# 🚨 Alert Routing Configuration
alert_routing:
  channels:
    critical:
      - type: "immediate_notification"
        targets: ["security-team@eq12.com", "admin@eq12.com"]
        methods: ["email", "sms", "slack"]

    high:
      - type: "priority_notification"
        targets: ["dev-team@eq12.com", "#eq12-security-alerts"]
        methods: ["email", "slack"]

    medium:
      - type: "standard_notification"
        targets: ["#eq12-monitoring"]
        methods: ["slack", "dashboard"]

    low:
      - type: "batch_notification"
        targets: ["#eq12-general"]
        methods: ["daily-digest"]

  alert_types:
    secrets_detected:
      severity: "critical"
      response_time: "5 minutes"
      escalation: "automatic_to_ciso"

    critical_vulnerability:
      severity: "critical"
      response_time: "15 minutes"
      escalation: "security_team_lead"

    compliance_violation:
      severity: "high"
      response_time: "2 hours"
      escalation: "compliance_officer"

    suspicious_activity:
      severity: "medium"
      response_time: "4 hours"
      escalation: "security_analyst"

# 🔍 Automated Security Scanning Schedules
scanning_schedules:
  secret_scanning:
    frequency: "real-time"
    scope: "all_commits_and_prs"
    tools: ["GitLeaks", "TruffleHog", "GitHub Secret Scanning"]
    alert_threshold: "any_detection"

  vulnerability_scanning:
    frequency: "daily_at_0300_utc"
    scope: "dependencies_and_code"
    tools: ["Safety", "Bandit", "Semgrep", "CodeQL"]
    alert_threshold: "medium_and_above"

  compliance_scanning:
    frequency: "weekly_monday_0600_utc"
    scope: "entire_repository"
    tools: ["Custom EQ12 Compliance Scanner", "SAST Tools"]
    alert_threshold: "any_violation"

  infrastructure_scanning:
    frequency: "daily_at_0200_utc"
    scope: "docker_files_and_configs"
    tools: ["Trivy", "Hadolint", "Checkov"]
    alert_threshold: "high_and_above"

# 📋 Compliance Reporting Configuration
compliance_reporting:
  gambling_regulations:
    frameworks: ["UKGC", "MGA", "AGCO", "US_State_Regulations"]
    report_frequency: "monthly"
    required_checks:
      - "responsible_gambling_messaging"
      - "age_verification_requirements"
      - "data_protection_compliance"
      - "financial_transaction_monitoring"

  data_privacy:
    frameworks: ["GDPR", "CCPA", "PIPEDA"]
    report_frequency: "quarterly"
    required_checks:
      - "personal_data_handling"
      - "consent_management"
      - "data_retention_policies"
      - "breach_notification_procedures"

  financial_security:
    frameworks: ["PCI_DSS", "SOX", "AML"]
    report_frequency: "monthly"
    required_checks:
      - "payment_data_protection"
      - "transaction_monitoring"
      - "audit_trail_maintenance"
      - "suspicious_activity_reporting"

# 🔧 Security Monitoring Tools Configuration
monitoring_tools:
  github_security:
    secret_scanning:
      enabled: true
      custom_patterns:
        - name: "EQ12 API Keys"
          pattern: "eq12_[a-zA-Z0-9]{32}"
        - name: "Sportsbook Tokens"
          pattern: "sb_[a-zA-Z0-9]{24,}"
        - name: "Betting API Keys"
          pattern: "bet_[a-zA-Z0-9_-]{20,}"

    code_scanning:
      enabled: true
      queries: ["security-and-quality", "security-extended"]
      schedule: "weekly"

    dependency_review:
      enabled: true
      vulnerability_threshold: "medium"
      license_restrictions: ["GPL-3.0", "AGPL-3.0"]

  custom_monitoring:
    betting_data_integrity:
      script: "scripts/monitor_betting_data.py"
      frequency: "hourly"
      checks: ["data_consistency", "anomaly_detection", "corruption_check"]

    api_security_monitoring:
      script: "scripts/monitor_api_security.py"
      frequency: "continuous"
      checks: ["rate_limiting", "authentication", "authorization"]

    financial_transaction_monitoring:
      script: "scripts/monitor_financial_transactions.py"
      frequency: "real-time"
      checks: ["suspicious_patterns", "limit_violations", "compliance"]

# 🚨 Incident Response Procedures
incident_response:
  security_incident_levels:
    level_1_critical:
      description: "Active breach, data exposure, or system compromise"
      response_time: "immediate"
      team: ["CISO", "Security Team", "Executive Team"]
      procedures:
        - "immediate_system_isolation"
        - "activate_incident_response_team"
        - "notify_regulatory_authorities"
        - "initiate_forensic_analysis"

    level_2_high:
      description: "Potential breach, critical vulnerability, or compliance violation"
      response_time: "within_1_hour"
      team: ["Security Team", "Dev Team Lead"]
      procedures:
        - "assess_threat_scope"
        - "implement_containment_measures"
        - "notify_stakeholders"
        - "begin_remediation"

    level_3_medium:
      description: "Security policy violation or non-critical vulnerability"
      response_time: "within_4_hours"
      team: ["Security Analyst", "Dev Team"]
      procedures:
        - "investigate_incident"
        - "document_findings"
        - "implement_fixes"
        - "update_security_policies"

# 📈 Security Metrics and KPIs
security_metrics:
  detection_metrics:
    - name: "Time to Detection (TTD)"
      target: "< 5 minutes for critical issues"
      measurement: "automated_monitoring"

    - name: "Mean Time to Response (MTTR)"
      target: "< 15 minutes for critical, < 2 hours for high"
      measurement: "incident_tracking_system"

    - name: "False Positive Rate"
      target: "< 10% for security alerts"
      measurement: "alert_validation_tracking"

  compliance_metrics:
    - name: "Compliance Score"
      target: "> 95% across all frameworks"
      measurement: "automated_compliance_scanning"

    - name: "Policy Adherence Rate"
      target: "100% for critical policies"
      measurement: "policy_violation_tracking"

    - name: "Training Completion Rate"
      target: "100% annual security training"
      measurement: "training_management_system"

  vulnerability_metrics:
    - name: "Critical Vulnerability Remediation Time"
      target: "< 24 hours"
      measurement: "vulnerability_management_system"

    - name: "Dependency Update Frequency"
      target: "Weekly for security updates"
      measurement: "dependency_tracking"

# 🔐 Access Control and Audit Configuration
access_control:
  privileged_access:
    monitoring: "continuous"
    logging: "all_actions"
    review_frequency: "monthly"

  repository_access:
    monitoring: "all_changes"
    approval_required: "admin_level_changes"
    audit_trail: "permanent_retention"

  security_tool_access:
    monitoring: "all_usage"
    multi_factor_auth: "required"
    session_timeout: "30_minutes"

# 📊 Monitoring Dashboard Configuration
dashboard_config:
  security_dashboard_url: "https://security.eq12.internal/dashboard"

  panels:
    - name: "Threat Overview"
      metrics: ["active_threats", "vulnerability_count", "compliance_status"]

    - name: "Alert Status"
      metrics: ["open_alerts", "response_times", "escalation_status"]

    - name: "System Health"
      metrics: ["monitoring_tool_status", "scan_completion_rates"]

    - name: "Compliance Tracking"
      metrics: ["compliance_scores", "policy_violations", "audit_status"]

  refresh_rate: "real_time"
  access_control: "security_team_and_above"

# 🔄 Automated Response Actions
automated_responses:
  secret_detection:
    - action: "immediately_revoke_token"
    - action: "notify_security_team"
    - action: "create_incident_ticket"
    - action: "force_password_reset_if_applicable"

  critical_vulnerability:
    - action: "create_high_priority_ticket"
    - action: "notify_dev_and_security_teams"
    - action: "trigger_emergency_patch_process"

  suspicious_login:
    - action: "temporarily_lock_account"
    - action: "require_additional_verification"
    - action: "log_security_event"
    - action: "notify_user_and_security_team"

  compliance_violation:
    - action: "create_compliance_ticket"
    - action: "notify_compliance_officer"
    - action: "trigger_policy_review"

# 🎯 EQ12-Specific Security Monitoring
eq12_specific_monitoring:
  betting_data_protection:
    - monitor: "betting_history_access"
    - monitor: "odds_data_integrity"
    - monitor: "bankroll_calculation_accuracy"
    - monitor: "parlay_builder_security"

  api_endpoint_monitoring:
    - monitor: "sportsbook_api_calls"
    - monitor: "rate_limiting_effectiveness"
    - monitor: "authentication_success_rates"
    - monitor: "data_extraction_patterns"

  gambling_compliance_monitoring:
    - monitor: "responsible_gambling_messaging"
    - monitor: "underage_access_prevention"
    - monitor: "problem_gambling_indicators"
    - monitor: "regulatory_reporting_accuracy"

# 📞 Emergency Contact Information
emergency_contacts:
  primary_security_contact:
    name: "Security Team Lead"
    email: "security-lead@eq12.com"
    phone: "+1-XXX-XXX-XXXX"
    availability: "24/7"

  compliance_officer:
    name: "Compliance Officer"
    email: "compliance@eq12.com"
    phone: "+1-XXX-XXX-XXXX"
    availability: "Business Hours + On-Call"

  executive_escalation:
    name: "Chief Information Security Officer"
    email: "ciso@eq12.com"
    phone: "+1-XXX-XXX-XXXX"
    availability: "Critical Incidents Only"

# 🔧 Implementation Checklist
implementation_checklist: |
  Security Monitoring Setup:

  ✅ Configure GitHub Advanced Security features
  ✅ Set up custom secret scanning patterns
  ✅ Implement automated vulnerability scanning
  ✅ Configure compliance monitoring scripts
  ✅ Set up incident response procedures
  ✅ Configure alert routing and escalation
  ✅ Implement security metrics collection
  ✅ Set up monitoring dashboard
  ✅ Configure automated response actions
  ✅ Train team on security procedures
  ✅ Test incident response procedures
  ✅ Document all security processes

  Integration Requirements:
  ✅ Slack integration for alerts
  ✅ Email notification system
  ✅ Ticket system integration (Jira/GitHub Issues)
  ✅ SIEM integration if applicable
  ✅ Compliance reporting system
  ✅ Audit logging system

# 📚 Training and Documentation Requirements
training_requirements: |
  Required Security Training:

  1. All Developers:
     - Secure coding practices
     - Secret management
     - Incident response procedures
     - Compliance requirements

  2. Security Team:
     - Advanced threat detection
     - Incident response leadership
     - Compliance frameworks
     - Forensic analysis

  3. Management:
     - Security risk assessment
     - Regulatory compliance
     - Business continuity
     - Crisis communication

  Training Schedule: Quarterly updates, Annual recertification

# END OF SECURITY MONITORING CONFIGURATION
# ========================================
#
# This configuration should be reviewed and updated quarterly.
# All security monitoring tools and procedures should be tested regularly.
# Incident response procedures should be practiced through tabletop exercises.
