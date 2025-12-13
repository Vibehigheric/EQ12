# 🦊 EQ12 GODSTACK Firefox Governance Automation

**Complete Firefox automation suite for EQ12 development environment with dynamic governance bookmarks, extension management, and VS Code integration.**

## 🎯 Overview

This comprehensive automation solution transforms Firefox into a **governance-first development control center** for EQ12 GODSTACK, featuring:

- ✅ **Automated Extension Installation** (security & devops focused)
- 🔗 **Dynamic Bookmark Generation** from live APIs
- 📊 **Grafana Dashboard Integration** 
- 🐙 **GitHub Governance Discussion Sync**
- ⏰ **Cross-platform Daily Scheduling**
- 🛠️ **VS Code Workspace Integration**
- 📸 **Audit Compliance Logging**

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp env.template .env

# Edit .env with your API keys:
# - GRAFANA_API_KEY
# - GH_TOKEN
# - GITHUB_REPO
```

### 2. Run Automation

```bash
# Test configuration
python scripts/firefox_governance_automation.py --test-only

# Full execution
python scripts/firefox_governance_automation.py

# Skip Firefox launch
python scripts/firefox_governance_automation.py --skip-launch
```

### 3. VS Code Integration

1. Open EQ12 directory in VS Code
2. Install recommended extensions when prompted
3. Use **Ctrl+Shift+P** → "Tasks: Run Task" → "EQ12: Run Firefox Governance Setup"

## 📋 Features Detail

### 🔐 Security Extensions Auto-Install

- **uBlock Origin** - Ad & tracker blocking
- **Privacy Badger** - Cross-site tracker protection
- **Octotree** - GitHub code tree navigation
- **Refined GitHub** - Enhanced GitHub interface
- **GitHub Actions** - Workflow status monitoring

### 🔗 Dynamic Governance Bookmarks

**Static Essentials:**
- EQ12 GitHub Repository
- Prometheus Metrics Dashboard
- Telegram Web Interface
- Ngrok Tunnel Status
- Local Development Services

**Live API Integration:**
- **Grafana**: Auto-discovered dashboards by category
- **GitHub**: Latest governance discussions and audit logs
- **Repository**: Issues, PRs, Actions, Settings quick access

### ⏰ Automated Daily Refresh

**Windows (Task Scheduler):**
```powershell
# Auto-generated XML configuration
schtasks /create /tn "EQ12_Firefox_Governance" /xml C:\EQ12\tasks\FirefoxGovernance.xml /f
```

**Linux (systemd):**
```bash
# Auto-generated service files
sudo systemctl enable firefox-governance.timer
sudo systemctl start firefox-governance.timer
```

### 🛠️ VS Code Development Integration

**Extensions Configured:**
- Python development suite (Pylance, Black, Flake8)
- GitHub integration (Copilot, Actions, Pull Requests)
- DevOps tools (Docker, REST Client, YAML)
- Remote development support

**Custom Tasks Available:**
- `EQ12: Run Firefox Governance Setup`
- `EQ12: Status Check`
- `EQ12: Start GODSTACK`
- `EQ12: Run Tests`
- `EQ12: Black Format`

## 📊 File Structure

```
C:\EQ12\
├── .vscode/
│   ├── extensions.json      # Recommended extensions
│   ├── settings.json        # EQ12-specific settings
│   ├── tasks.json          # Custom automation tasks
│   └── launch.json         # Debug configurations
├── scripts/
│   └── firefox_governance_automation.py  # Main automation script
├── notebooks/
│   └── firefox_governance_automation.ipynb  # Interactive development
├── tasks/
│   └── FirefoxGovernance.xml  # Windows Task Scheduler config
├── systemd/
│   ├── firefox-governance.service  # Linux systemd service
│   └── firefox-governance.timer    # Linux systemd timer
├── logs/                   # All automation logs (JSON format)
├── api_tests.http         # REST client API testing
└── env.template          # Environment variables template
```

## 🔧 API Integration

### Grafana Integration
- **Endpoint**: `/api/search?type=dash-db`
- **Authentication**: Bearer token via `GRAFANA_API_KEY`
- **Features**: Auto-discovery of dashboards, folder organization

### GitHub Integration  
- **Endpoint**: GraphQL API (`/graphql`)
- **Authentication**: Personal access token via `GH_TOKEN`
- **Features**: Governance discussions, repository links, audit trails

### REST Client Testing
Use `api_tests.http` with VS Code REST Client extension:
- Test Ngrok tunnel status
- Validate Grafana connectivity
- Check GitHub API access
- Test webhook endpoints

## 📈 Monitoring & Logging

All operations logged to `C:\EQ12\logs\` with UTC timestamps:
- `firefox_governance_YYYYMMDD.log` - Daily automation log
- `firefox_extensions_YYYYMMDD.json` - Extension installation details
- `firefox_bookmarks_YYYYMMDD.json` - Bookmark generation log
- `grafana_dashboards_YYYYMMDD.json` - Grafana integration log
- `github_discussions_YYYYMMDD.json` - GitHub API responses
- `execution_report_YYYYMMDD_HHMMSS.json` - Complete session reports

## ⚙️ Configuration Options

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GRAFANA_URL` | Grafana instance URL | No | `http://localhost:3000` |
| `GRAFANA_API_KEY` | Grafana API key | Yes* | None |
| `GITHUB_REPO` | Repository in `owner/repo` format | No | `Vibehigheric/edgegod-parlay` |
| `GH_TOKEN` | GitHub personal access token | Yes* | None |

*Required for full functionality; script will run with limited features if missing

### Command Line Options

```bash
python scripts/firefox_governance_automation.py [OPTIONS]

Options:
  --test-only     Test configuration without making changes
  --skip-launch   Skip Firefox launch after setup
  --verbose, -v   Enable verbose logging
  --help         Show help message
```

## 🔒 Security & Compliance

- **Environment Variables**: All secrets read from environment only
- **Audit Logging**: Complete session tracking with JSON logs
- **Signed Commits**: VS Code configured for commit signing
- **Extension Verification**: Downloads only from official Mozilla Add-ons
- **API Rate Limiting**: Built-in timeout and retry logic

## 🚨 Troubleshooting

### Common Issues

**Firefox Profile Not Found:**
```bash
# Check profile location
ls ~/AppData/Roaming/Mozilla/Firefox/Profiles/  # Windows
ls ~/.mozilla/firefox/                           # Linux
```

**API Connection Failures:**
```bash
# Test API connectivity
python scripts/firefox_governance_automation.py --test-only --verbose
```

**VS Code Tasks Not Working:**
1. Ensure VS Code is opened in `C:\EQ12` directory
2. Install recommended extensions
3. Check terminal profile settings

### Debug Mode

Enable verbose logging for detailed troubleshooting:
```bash
python scripts/firefox_governance_automation.py --verbose
```

## 🔄 Next Steps

1. **Screenshot Automation**: Add Selenium/Playwright for audit compliance screenshots
2. **Browser Profiles**: Support multiple Firefox profiles for different environments
3. **Plugin Development**: Custom Firefox extension for EQ12 GODSTACK integration
4. **Mobile Support**: Extend to Firefox Mobile bookmark sync

## 📞 Support

- **Logs**: Check `C:\EQ12\logs\` for detailed execution information
- **VS Code**: Use integrated terminal and tasks for debugging
- **API Testing**: Use `api_tests.http` for connectivity validation

---

**🎉 Your Firefox is now a governance-ready development control center for EQ12 GODSTACK!**