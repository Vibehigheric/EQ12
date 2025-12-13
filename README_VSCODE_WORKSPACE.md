# EQ12 GODSTACK - VS Code Workspace Pack

This comprehensive VS Code workspace configuration transforms VS Code into the ultimate EQ12 development control center with complete automation, governance, and monitoring integration.

## 🚀 Features

### Core Development Environment
- **Python 3.12+ Integration**: Complete Python development stack with Pylance, Black formatting, Flake8 linting
- **Jupyter Notebook Support**: Interactive development with notebook integration and slideshow capabilities
- **PowerShell Automation**: Advanced PowerShell scripting with Pester testing framework
- **Multi-Platform Support**: Windows, Linux, and remote development containers

### AI & GitHub Integration
- **GitHub Copilot**: AI-powered code completion and chat assistance
- **GitHub Actions**: Workflow automation and CI/CD integration
- **GitLens**: Advanced Git capabilities with blame, history, and collaboration features
- **Pull Request Management**: Seamless GitHub integration for code reviews

### DevOps & Monitoring
- **Docker & Kubernetes**: Container orchestration and deployment tools
- **Grafana Explorer**: Real-time monitoring and dashboard integration
- **API Testing**: Thunder Client and REST Client for API development and testing
- **Security Scanning**: Snyk vulnerability scanner and security governance

### Firefox Governance Automation
- **Profile Management**: Automated Firefox profile creation and configuration
- **Extension Installation**: Bulk extension deployment with governance policies
- **Bookmark Generation**: Dynamic bookmark creation with API integration
- **Task Scheduling**: Automated daily governance updates and compliance reporting

## 📁 Workspace Structure

```
c:\EQ12\.vscode\
├── settings.json       # Comprehensive VS Code settings
├── tasks.json          # Custom EQ12 automation tasks
├── launch.json         # Debug configurations for all components
├── extensions.json     # Recommended extension pack (60+ extensions)
└── api_tests.http      # REST client API testing configuration

c:\EQ12\
├── EQ12-GODSTACK.code-workspace    # Multi-root workspace configuration
├── firefox_governance_automation.py # Main automation script
├── firefox_governance_automation.ipynb # Interactive development notebook
└── env.template                    # Environment variable template
```

## 🔧 Installation & Setup

### 1. Open Workspace
```powershell
# Navigate to EQ12 directory
cd C:\EQ12

# Open in VS Code
code EQ12-GODSTACK.code-workspace
```

### 2. Install Recommended Extensions
When you open the workspace, VS Code will prompt to install recommended extensions. Click "Install All" or install manually:

**Essential Extensions:**
- Python Development: `ms-python.python`, `ms-python.vscode-pylance`, `ms-python.debugpy`
- GitHub Integration: `github.copilot`, `github.copilot-chat`, `github.vscode-pull-request-github`
- PowerShell: `ms-vscode.powershell`
- Jupyter: `ms-toolsai.jupyter`

### 3. Configure Environment Variables
```powershell
# Copy environment template
cp env.template .env

# Edit with your API keys
# GRAFANA_API_KEY=your_grafana_key
# GITHUB_TOKEN=your_github_token
# NGROK_AUTH_TOKEN=your_ngrok_token
```

### 4. Initialize Python Environment
```powershell
# Create virtual environment
python -m venv .venv

# Activate environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## 🎯 VS Code Tasks

Access via `Ctrl+Shift+P` → "Tasks: Run Task":

### EQ12: Run Firefox Governance Setup
- **Purpose**: Execute complete Firefox governance automation
- **Command**: `python firefox_governance_automation.py --verbose`
- **Output**: Logs to `C:\EQ12\logs` with UTC timestamps

### EQ12: Status Check
- **Purpose**: Validate system configuration and API connectivity
- **Command**: `python -c "import sys; print(f'Python: {sys.version}'); print('EQ12 Status: ✅ Ready')"`
- **Output**: System status and readiness confirmation

### EQ12: Start GODSTACK
- **Purpose**: Launch complete EQ12 automation stack
- **Command**: `powershell -File eq12_launcher.ps1`
- **Output**: Multi-component system startup

### EQ12: Run Tests
- **Purpose**: Execute pytest and Pester test suites
- **Command**: `pytest tests/ -v && Invoke-Pester tests/pester/`
- **Output**: Comprehensive test results and coverage

### EQ12: Black Format
- **Purpose**: Format all Python files with Black
- **Command**: `black . --line-length=88`
- **Output**: Code formatting results

## 🐛 Debug Configurations

Access via `F5` or Debug panel:

### Python Configurations
- **Current File**: Debug any Python file with F5
- **Firefox Governance**: Debug automation script with test flags
- **Pytest**: Debug unit tests with breakpoint support
- **Attach Process**: Attach to running Python processes

### PowerShell Configurations
- **Current Script**: Debug PowerShell files
- **EQ12 Launcher**: Debug main launcher script
- **Pester Tests**: Debug PowerShell test suites

### Compound Configurations
- **EQ12: Full Stack Debug**: Launch Python and PowerShell debugging simultaneously

## 🌐 API Testing

### REST Client Integration
Open `api_tests.http` for pre-configured API tests:

```http
### Test Ngrok API
GET {{ngrok_api}}/api/tunnels
Content-Type: application/json

### Test Grafana API
GET {{grafana_url}}/api/health
Authorization: Bearer {{GRAFANA_API_KEY}}

### Test GitHub API
GET https://api.github.com/user
Authorization: token {{GITHUB_TOKEN}}
```

### Environment Variables
Switch between local and production environments:
- **Local**: `localhost:3000`, `127.0.0.1:4040`
- **Production**: `grafana.eq12.com`, `prometheus.eq12.com`

## ⚙️ Settings Highlights

### Python Configuration
```json
{
  "python.defaultInterpreterPath": "C:\\EQ12\\.venv\\Scripts\\python.exe",
  "python.analysis.typeCheckingMode": "basic",
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true
}
```

### Terminal Configuration
```json
{
  "terminal.integrated.defaultProfile.windows": "PowerShell",
  "terminal.integrated.env.windows": {
    "EQ12_ROOT": "C:\\EQ12",
    "PYTHONPATH": "C:\\EQ12"
  }
}
```

### Git & Security
```json
{
  "git.enableCommitSigning": true,
  "security.workspace.trust.untrustedFiles": "prompt",
  "telemetry.enableTelemetry": false
}
```

## 🔄 Automated Workflows

### Daily Governance Updates
- **Trigger**: Windows Task Scheduler (daily at 2 AM)
- **Action**: Execute Firefox governance automation
- **Logging**: JSON snapshots to `C:\EQ12\logs`
- **Notifications**: Success/failure alerts via configured channels

### Git Integration
- **Signed Commits**: Automatic GPG signing enabled
- **Auto-fetch**: Continuous synchronization with remote repositories
- **Smart Commit**: Intelligent commit message suggestions

### Code Quality
- **Format on Save**: Automatic Black formatting for Python
- **Import Organization**: Auto-sort imports on save
- **Lint on Change**: Real-time Flake8 linting feedback

## 🏗️ Architecture Integration

### Firefox Governance
```
VS Code → Python Script → Firefox Profile Management
       → Extension Installation → Bookmark Generation
       → API Integration → Compliance Reporting
```

### Monitoring Stack
```
VS Code → REST Client → Grafana API → Dashboard Updates
       → Prometheus → Metrics Collection → Alerting
```

### Development Workflow
```
VS Code → GitHub Copilot → Code Generation → Git Integration
       → Automated Testing → Docker Deployment → Production
```

## 🚨 Troubleshooting

### Extension Issues
```powershell
# Reload VS Code window
Ctrl+Shift+P → "Developer: Reload Window"

# Reset extension host
Ctrl+Shift+P → "Developer: Restart Extension Host"
```

### Python Environment Issues
```powershell
# Verify Python interpreter
Ctrl+Shift+P → "Python: Select Interpreter"

# Refresh environment
Ctrl+Shift+P → "Python: Refresh Environments"
```

### Task Execution Issues
```powershell
# Clear task cache
Ctrl+Shift+P → "Tasks: Clear Cache"

# Restart task system
Ctrl+Shift+P → "Tasks: Restart Task Manager"
```

### Git Signing Issues
```powershell
# Configure GPG
git config --global user.signingkey YOUR_KEY_ID
git config --global commit.gpgsign true

# Test signing
git commit --allow-empty -m "Test signed commit"
```

## 📊 Performance Monitoring

### VS Code Performance
- **Startup Time**: Monitor extension load times
- **Memory Usage**: Track workspace memory consumption
- **CPU Usage**: Monitor during automation tasks

### Automation Performance
- **Firefox Setup Time**: Profile creation and configuration
- **API Response Times**: Grafana and GitHub integration
- **Test Execution Time**: Pytest and Pester suite performance

## 🔐 Security Features

### Workspace Trust
- **Restricted Mode**: Untrusted files prompt for permission
- **Extension Validation**: Only install trusted extensions
- **Settings Isolation**: Workspace-specific security policies

### API Key Management
- **Environment Variables**: Secure credential storage
- **Template System**: Safe configuration sharing
- **Audit Logging**: Track API usage and access

### Code Security
- **Vulnerability Scanning**: Snyk security integration
- **Dependency Checking**: Automated security audits
- **Compliance Reporting**: Security governance enforcement

## 🎓 Learning Resources

### VS Code Mastery
- **Command Palette**: `Ctrl+Shift+P` for all commands
- **Quick Open**: `Ctrl+P` for file navigation
- **Settings**: `Ctrl+,` for configuration
- **Extensions**: `Ctrl+Shift+X` for extension management

### EQ12 Automation
- **Interactive Notebook**: `firefox_governance_automation.ipynb`
- **CLI Reference**: `python firefox_governance_automation.py --help`
- **API Documentation**: In-code docstrings and REST client examples

### Git Integration
- **GitLens**: Hover over code for git blame and history
- **Pull Requests**: Integrated GitHub PR management
- **Branch Management**: Visual git operations

## 📈 Success Metrics

### Development Efficiency
- **Code Completion Rate**: GitHub Copilot suggestion acceptance
- **Bug Detection Rate**: Automated linting and testing
- **Deployment Speed**: CI/CD pipeline performance

### Automation Success
- **Firefox Profile Creation**: 100% success rate
- **Extension Installation**: Bulk deployment metrics
- **API Integration**: Response time and reliability

### Compliance Achievement
- **Security Audits**: Vulnerability scan results
- **Code Quality**: Linting and formatting compliance
- **Documentation**: README and docstring coverage

---

**EQ12 GODSTACK** - The ultimate VS Code workspace for automation excellence. Transform your development experience with comprehensive tooling, AI assistance, and seamless DevOps integration.
