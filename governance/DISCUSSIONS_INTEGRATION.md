# GitHub Discussions Integration & Governance Automation

This document describes the automated GitHub Discussions integration for EQ12 GODSTACK governance and compliance monitoring.

## Overview

The `discussion-sync.yml` workflow automatically creates and manages GitHub Discussions for:
- **Governance workflow failures** (immediate alerts)
- **Quarterly compliance audits** (scheduled reviews)
- **Manual governance discussions** (on-demand)

## Triggers

### 1. Workflow Failure Detection
- **Trigger**: When any governance workflow completes with failure status
- **Monitored Workflows**: 
  - Secrets Gate
  - Security Scan
  - CI All-in-One
  - Governance Board Sync
- **Action**: Creates failure alert discussion + Telegram notification

### 2. Quarterly Audit Automation
- **Trigger**: Scheduled quarterly (Jan 1, Apr 1, Jul 1, Oct 1 at 9 AM UTC)
- **Action**: Creates comprehensive audit discussion with checklists

### 3. Manual Discussion Creation
- **Trigger**: Manual workflow dispatch
- **Options**: governance, security, audit, ci-cd
- **Action**: Creates category-specific discussion thread

## Discussion Categories

The workflow creates discussions in appropriate categories:

| Category | Purpose | Auto-Created For |
|----------|---------|------------------|
| **Governance & Compliance** | PR process, CODEOWNERS, governance gates | Workflow failures, manual governance |
| **Security & Secrets** | CodeQL, secret scanning, vulnerabilities | Security workflow failures, manual security |
| **Audits & Reviews** | Quarterly audits, compliance reviews | Scheduled audits, manual audit |
| **CI/CD & Actions** | Pipeline issues, workflow debugging | CI workflow failures, manual ci-cd |

## Failure Alert Features

When governance workflows fail, the system automatically:

### 1. Creates Alert Discussion
- **Title**: `🚨 Governance Failure: [Workflow Name] - [Timestamp]`
- **Content**: 
  - Workflow details and failure link
  - Analysis checklist
  - Related PR listing
  - Sensitive stack escalation procedures

### 2. Sensitive Stack Protection
For failures involving sensitive business stacks:
- **Immediate escalation** to @Vibehigheric
- **Telegram alert** with details
- **PR blocking** until resolution
- **Compliance review** requirement

### 3. Related PR Management
- Adds `governance-discussion` label to open PRs
- Creates critical issues for security failures
- Links discussions to affected PRs

## Quarterly Audit Process

Automated quarterly audits include:

### Audit Scope
- **Security Controls**: Secret scanning, CodeQL, dependency review
- **Governance Process**: PR templates, CODEOWNERS effectiveness
- **Business Stack Compliance**: Betting, Cannabis, Credit regulations
- **Access Controls**: Authentication, authorization, session management
- **Workflow Security**: Action verification, SHA pinning

### Audit Timeline
- **Week 1**: Security and technical controls review
- **Week 2**: Governance process assessment  
- **Week 3**: Business stack compliance validation
- **Week 4**: Report compilation and recommendations

### Compliance Tracking
- Review metrics and KPIs
- Track previous quarter recommendations
- Document regulatory changes
- Update governance policies

## Integration Points

### 1. Telegram Notifications
- **Alert Channel**: Immediate failure notifications
- **Message Format**: Markdown with workflow details
- **Escalation**: Direct mention for sensitive stacks

### 2. GitHub Projects Board
- Discussions automatically link to governance board
- Failure discussions create tracking cards
- Audit discussions pin for quarterly visibility

### 3. Compliance Bot Integration
- Webhook triggers for discussion events
- Automated discussion updates
- Copilot extension awareness

## Setup Requirements

### Repository Secrets
```yaml
# Required for discussion creation
GITHUB_TOKEN: <GitHub PAT with discussions:write>

# Optional for Telegram alerts
TELEGRAM_BOT_TOKEN: <Bot token from @BotFather>
TELEGRAM_CHAT_ID: <Target chat/channel ID>
```

### Repository Settings
1. **Enable Discussions**: Repository settings → Features → Discussions
2. **Discussion Categories**: Create categories matching workflow expectations
3. **Permissions**: Ensure workflow can write to discussions

### Category Setup
Create these discussion categories in your repository:
- **Governance & Compliance** (General discussion)
- **Security & Secrets** (General discussion)  
- **Audits & Reviews** (Announcement style)
- **CI/CD & Actions** (Q&A style)

## Usage Examples

### Manual Discussion Creation
```bash
# Create governance discussion
gh workflow run discussion-sync.yml -f discussion_type=governance

# Create security discussion  
gh workflow run discussion-sync.yml -f discussion_type=security

# Create audit discussion
gh workflow run discussion-sync.yml -f discussion_type=audit

# Create CI/CD discussion
gh workflow run discussion-sync.yml -f discussion_type=ci-cd
```

### Viewing Active Discussions
```bash
# List all governance discussions
gh api graphql -f query='
  query($owner: String!, $repo: String!) {
    repository(owner: $owner, name: $repo) {
      discussions(first: 20, orderBy: {field: CREATED_AT, direction: DESC}) {
        nodes {
          title
          createdAt
          url
          category { name }
        }
      }
    }
  }
' -f owner="Vibehigheric" -f repo="EQ12"
```

## Monitoring & Maintenance

### Discussion Lifecycle
1. **Creation**: Automatic on trigger events
2. **Activity**: Team discussion and resolution tracking
3. **Resolution**: Manual closure with summary
4. **Archive**: Automatic after 90 days inactive

### Metrics Tracking
- Discussion creation frequency
- Resolution time for governance failures
- Audit completion rates
- Community engagement levels

### Troubleshooting
- **No discussions created**: Check repository permissions and category setup
- **Telegram alerts not working**: Verify bot token and chat ID secrets
- **Wrong category assignment**: Review category name matching in workflow

---

**Maintenance Contact**: compliance@eq12-godstack.local  
**Last Updated**: 2024-01-20  
**Workflow Version**: 1.0.0