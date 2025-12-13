# EQ12 OpenAI Community Monitor

Automated monitoring system for OpenAI Community forum that tracks relevant updates, alerts on important changes, and creates actionable GitHub issues.

## 🎯 Features

- **Real-time Monitoring**: Tracks multiple OpenAI Community RSS feeds
- **Smart Classification**: Automatically categorizes posts by priority and actionability
- **Multi-channel Alerts**: Slack, Teams, and GitHub issue notifications
- **Intelligent Filtering**: Focuses on EQ12-relevant topics (webhooks, rate limits, Azure OpenAI, etc.)
- **Comprehensive Reporting**: Daily/weekly activity summaries
- **Production Ready**: Error handling, state persistence, and logging

## 📡 Monitored Topics

### High Priority Feeds
- **Announcements**: Official OpenAI updates and changes
- **API Updates**: Core API functionality and breaking changes
- **Rate Limits**: Quota, billing, and usage policy changes
- **Webhooks**: Signature verification and event handling
- **Azure OpenAI**: Deployment and configuration updates
- **Deprecations**: Model and feature sunset announcements

### Keywords Tracked
- `rate limit`, `429`, `insufficient_quota`
- `webhook`, `signature`, `responses api`
- `azure openai`, `deployment`
- `model unavailable`, `quota exceeded`
- `pricing change`, `deprecation`

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
# Using PowerShell wrapper (recommended)
.\eq12_community_monitor.ps1 -Action install-deps

# Or manually with pip
pip install feedparser requests PyGithub
```

### 2. Configure Notifications (Optional)
```powershell
# Copy example configuration
copy .env.community_monitor.example .env.community_monitor

# Edit with your actual webhook URLs and tokens
notepad .env.community_monitor
```

### 3. Run Single Monitoring Cycle
```powershell
# PowerShell wrapper (recommended)
.\eq12_community_monitor.ps1 -Action single -Verbose

# Direct Python execution
python eq12_community_monitor.py --single
```

### 4. Start Continuous Monitoring
```powershell
# Monitor every 15 minutes (default)
.\eq12_community_monitor.ps1 -Action continuous

# Custom interval (30 minutes)
.\eq12_community_monitor.ps1 -Action continuous -Interval 30
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL | No |
| `TEAMS_WEBHOOK_URL` | Teams connector webhook URL | No |
| `GITHUB_TOKEN` | Personal access token for issues | No |
| `GITHUB_REPO` | Repository for issues (owner/repo) | No |

### Notification Setup

#### Slack Integration
1. Go to your Slack workspace
2. Apps > Incoming Webhooks > Add to Slack
3. Select channel and copy webhook URL
4. Set `SLACK_WEBHOOK_URL` environment variable

#### Teams Integration
1. Go to your Teams channel
2. Connectors > Incoming Webhook > Configure
3. Name the webhook and copy URL
4. Set `TEAMS_WEBHOOK_URL` environment variable

#### GitHub Issues
1. Create personal access token: https://github.com/settings/tokens
2. Grant `repo` scope (private) or `public_repo` (public)
3. Set `GITHUB_TOKEN` environment variable
4. Set `GITHUB_REPO` to `owner/repository-name`

## 📊 Usage Examples

### PowerShell Wrapper (Recommended)
```powershell
# Install dependencies
.\eq12_community_monitor.ps1 -Action install-deps

# Single monitoring cycle
.\eq12_community_monitor.ps1 -Action single -Verbose

# Continuous monitoring (15 min intervals)
.\eq12_community_monitor.ps1 -Action continuous -Interval 15

# Generate 7-day activity report
.\eq12_community_monitor.ps1 -Action report -ReportDays 7
```

### Direct Python Usage
```bash
# Single cycle
python eq12_community_monitor.py --single

# Continuous monitoring
python eq12_community_monitor.py --continuous --interval 30

# Generate report
python eq12_community_monitor.py --report 14
```

### VS Code Tasks
Use Ctrl+Shift+P > "Tasks: Run Task":
- `EQ12: Install Community Monitor Dependencies`
- `EQ12: Run Community Monitor (Single)`
- `EQ12: Start Community Monitor (Continuous)`
- `EQ12: Community Activity Report (7 days)`

## 📋 Output & Logs

### Log Files
- `C:/EQ12/logs/community_monitor.log` - Main application log
- `C:/EQ12/logs/community_monitor_state.json` - Seen items state
- `C:/EQ12/logs/community_posts_YYYYMMDD.jsonl` - Daily post archive

### Notifications
- **High Priority**: Sent to all configured channels (Slack/Teams/GitHub)
- **Actionable Items**: Create GitHub issues with proper labels
- **Regular Posts**: Logged for reporting and analysis

### Report Output
```json
{
  "period_days": 7,
  "total_posts": 45,
  "high_priority": 8,
  "actionable": 12,
  "categories": {
    "rate_limits": 5,
    "webhooks": 3,
    "azure": 4
  },
  "top_keywords": {
    "rate limit": 6,
    "webhook": 4,
    "azure openai": 3
  }
}
```

## 🔍 Monitoring Strategy

### Classification Logic
Posts are classified based on:
- **Priority**: High (immediate attention) vs Low (informational)
- **Actionability**: Requires EQ12 system updates vs awareness only
- **Categories**: Webhooks, rate limits, Azure, responses API, cost, etc.

### EQ12 Integration Points
Monitor focuses on topics affecting:
- **Rate Limiting System**: Quota changes, new limits, enforcement updates
- **Webhook Infrastructure**: Signature changes, new event types, security updates
- **Model Policies**: New models, deprecations, availability changes
- **Cost Management**: Pricing updates, billing policy changes
- **Azure Integration**: Deployment changes, regional availability

## 🛠️ Advanced Usage

### Custom Keywords
Edit the script to add domain-specific keywords:
```python
KEYWORDS_HIGH_PRIORITY = [
    "rate limit", "429", "insufficient_quota",
    "your_custom_keyword", "another_priority_term"
]
```

### Feed Customization
Add or modify RSS feeds in the `FEEDS` dictionary:
```python
FEEDS = {
    "custom_feed": "https://community.openai.com/c/your-topic.rss",
    # ... existing feeds
}
```

### Webhook Payload Customization
Modify `notify_slack()` method to customize message format:
```python
def notify_slack(self, title, link, category, priority):
    # Custom Slack payload formatting
    pass
```

## 🔒 Security Considerations

- Store sensitive tokens in environment variables only
- Use least-privilege GitHub tokens (public_repo vs repo)
- Validate webhook URLs before configuration
- Monitor logs for authentication failures
- Consider rate limiting for API calls

## 🐛 Troubleshooting

### Common Issues
1. **No notifications received**: Check webhook URLs and token validity
2. **Python import errors**: Run dependency installation
3. **Permission denied**: Check file system permissions for log directory
4. **Rate limit exceeded**: Reduce monitoring frequency

### Debug Mode
Enable verbose logging:
```powershell
.\eq12_community_monitor.ps1 -Action single -Verbose
```

### Manual Testing
Test individual components:
```python
monitor = OpenAICommunityMonitor()
monitor.monitor_feeds()  # Single cycle
report = monitor.generate_report(7)  # 7-day report
```

## 📈 Integration with EQ12 Stack

### Rate Limiting Coordination
Monitor detects rate limit policy changes and can trigger:
- Automatic rate limit configuration updates
- Budget threshold adjustments
- Model routing policy updates

### Webhook Security Updates
Tracks webhook signature and security changes for:
- HMAC verification updates
- New event type additions
- Security best practice changes

### Model Policy Maintenance
Monitors for:
- New model announcements
- Deprecation schedules
- Regional availability changes
- Capability updates

## 📚 References

- [OpenAI Community Forum](https://community.openai.com/)
- [Slack Webhook Documentation](https://api.slack.com/messaging/webhooks)
- [Teams Webhook Guide](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)
- [GitHub API Documentation](https://docs.github.com/en/rest)
