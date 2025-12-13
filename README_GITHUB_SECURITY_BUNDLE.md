# EQ12 Security-Hardened GitHub Repository Structure

Complete secure GitHub repository bundle for EQ12 automation platform.

## 🔒 Security-First Architecture

### Critical Security Features Implemented:

✅ **Encrypted Credential Management**
- All API keys stored in encrypted `credentials.enc`
- No secrets in version control
- Password-protected access via `EQ12CredentialManager`

✅ **Pre-Commit Security Hooks**
- Automatic secret scanning before commits
- Blocks sensitive file uploads
- Validates security patterns

✅ **Automated Vulnerability Scanning**
- GitHub Actions security CI/CD pipeline
- Daily security scans with `eq12_security_scanner.py`
- Dependency vulnerability checks

✅ **Comprehensive .gitignore**
- Protects `keys/`, `logs/`, `data/`, `.env` files
- Excludes personal information and runtime data
- OS and IDE specific exclusions

---

## 📂 Repository Structure

```
eq12-automation-suite/
├── .github/
│   ├── workflows/
│   │   ├── security-ci.yml          # Security scanning pipeline
│   │   ├── python-tests.yml         # Python component tests
│   │   └── powershell-tests.yml     # PowerShell script validation
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       ├── feature_request.md
│       └── security_issue.md
├── .vscode/
│   ├── settings.json                # VS Code workspace settings
│   ├── launch.json                  # Debug configurations
│   ├── extensions.json              # Recommended extensions
│   └── tasks.json                   # Build/run tasks
├── app/                             # Core Python applications
│   ├── eq12_telegram_master_bot.py  # Telegram bot (67+ commands)
│   ├── eq12_discord_bot.py          # Discord dual-server bot
│   ├── eq12_snip_watcher.py         # OCR visual input processor
│   ├── eq12_appletv_manager.py      # Apple TV command center
│   ├── eq12_appletv_streaming_engine.py # AirPlay streaming
│   ├── eq12_credential_manager.py   # Secure credential management
│   ├── eq12_security_scanner.py     # Vulnerability scanner
│   └── requirements.txt             # Python dependencies
├── scripts/
│   ├── powershell/                  # Windows PowerShell automation
│   │   ├── eq12_admin.ps1          # Admin toolkit (firewall, services)
│   │   ├── eq12_user.ps1           # User toolkit (daily operations)
│   │   ├── eq12_wireguard_switcher.ps1 # VPN profile management
│   │   ├── eq12_telegram_master_bot.ps1 # Telegram wrapper
│   │   ├── eq12_discord_bot.ps1    # Discord wrapper
│   │   └── eq12_snip_watcher.ps1   # Snip watcher wrapper
│   └── ubuntu/                      # Ubuntu/WSL automation
│       ├── eq12_user.sh            # Ubuntu user toolkit
│       ├── eq12_admin.sh           # Ubuntu admin toolkit
│       └── eq12_wireguard_manager.sh # Linux VPN management
├── configs/
│   ├── telegram_config.example.json # Telegram bot configuration
│   ├── discord_config.example.json  # Discord server setup
│   ├── appletv_config.example.json  # Apple TV device config
│   └── wireguard_configs/           # VPN profile templates
│       ├── wg-betting.conf.example
│       ├── wg-travel.conf.example
│       └── wg-finance.conf.example
├── docs/
│   ├── README_MULTI_PLATFORM_BOTS.md # Multi-platform architecture guide
│   ├── SECURITY_AUDIT_RESULTS.md   # Security audit documentation
│   ├── SETUP_GUIDE.md              # Complete setup instructions
│   ├── COMMAND_REFERENCE.md        # Bot commands and usage
│   └── TROUBLESHOOTING.md          # Common issues and solutions
├── tests/
│   ├── python/                      # Python unit tests
│   │   ├── test_telegram_bot.py
│   │   ├── test_discord_bot.py
│   │   ├── test_security_scanner.py
│   │   └── test_credential_manager.py
│   └── powershell/                  # PowerShell Pester tests
│       ├── eq12_admin.Tests.ps1
│       ├── eq12_user.Tests.ps1
│       └── eq12_wireguard.Tests.ps1
├── deployment/
│   ├── docker/
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── docker-compose.prod.yml
│   ├── systemd/                     # Linux service files
│   │   ├── eq12-telegram-bot.service
│   │   ├── eq12-discord-bot.service
│   │   └── eq12-snip-watcher.service
│   └── windows/                     # Windows deployment
│       ├── install.ps1
│       └── task-scheduler/
├── .gitignore                       # Comprehensive security exclusions
├── .pre-commit-config.yaml         # Pre-commit hook configuration
├── pre-commit-security-hook.sh     # Security validation script
├── eq12_production_launcher.py     # Main production orchestrator
├── requirements.txt                 # Core dependencies
├── requirements-dev.txt             # Development dependencies
├── LICENSE                          # MIT License
└── README.md                        # Main documentation
```

---

## 🚀 Quick Start

### 1. Clone and Setup Security
```bash
git clone https://github.com/yourusername/eq12-automation-suite.git
cd eq12-automation-suite

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup encrypted credentials
python app/eq12_credential_manager.py --setup
```

### 2. Configure Environment
```powershell
# Windows
$env:EQ12_HOME = "C:\EQ12"
$env:EQ12_CREDENTIAL_PASSWORD = "your_secure_password"

# Copy example configs
Copy-Item "configs\*.example.json" -Destination "configs\" -Force
# Edit configs with your settings
```

### 3. Security Validation
```bash
# Run security scan
python app/eq12_security_scanner.py --scan-all

# Install pre-commit hooks
pre-commit install
```

### 4. Launch Production
```bash
# Full production launch
python eq12_production_launcher.py --launch

# Or start individual components
python eq12_production_launcher.py --component telegram_master_bot
python eq12_production_launcher.py --component discord_bot
```

---

## 🔧 VS Code Integration

### Extensions (Auto-installed via `.vscode/extensions.json`)
- **GitHub Copilot** - AI code completion
- **GitHub Copilot Chat** - Conversational coding assistant
- **Python** - Full Python development support
- **PowerShell** - PowerShell script development
- **Thunder Client** - API testing for EQ12 endpoints
- **GitLens** - Enhanced Git capabilities
- **Better Comments** - Enhanced code documentation
- **Error Lens** - Inline error highlighting

### Workspace Features
- **Integrated Terminal** - Multiple terminal support (PowerShell, WSL, Command Prompt)
- **Debug Configurations** - Pre-configured debug setups for all Python components
- **Task Runner** - One-click build/test/deploy tasks
- **Copilot Integration** - EQ12-aware code completion and suggestions

### Security Integration
- **Secret Detection** - VS Code warns about potential secrets before commit
- **Linting** - Automatic security pattern validation
- **Testing** - Integrated test runner for Python and PowerShell tests

---

## 🤖 Multi-Platform Bot Architecture

### Telegram Master Bot (67+ Commands)
**Sports Betting:** `/parlay [size] [sport]`, `/hrparlay`, `/locks [count]`, `/odds [game]`
**Travel Deals:** `/deal [from] [to]`, `/watchlist`, `/hotels [city]`, `/nextmove`
**Finance:** `/finance`, `/credit`, `/income`, `/housing`
**Apple TV:** `/sendtv_parlay`, `/sendtv_deals`, `/appletv_devices`
**System:** `/status`, `/logs`, `/restart`, `/update`

### Discord Dual-Server Bot
**Ops Server (Private):** Mission control with admin channels (#alerts, #betting, #travel, #finance, #appletv, #snips, #logs)
**Community Server (Public):** Affiliate funnel with public/premium channels

### Visual Input System
**Snip Watcher:** Screenshot → OCR → Automatic API routing (betting/travel/finance)

### Apple TV Command Center
**AirPlay Streaming:** Real-time parlay/deal/finance dashboard streaming
**HomeKit Integration:** Smart home device control

---

## 🔐 Security Features

### Credential Management
```bash
# Setup encrypted credentials (one-time)
python app/eq12_credential_manager.py --setup
python app/eq12_credential_manager.py --encrypt

# Daily usage (credentials auto-loaded)
$env:EQ12_CREDENTIAL_PASSWORD = "password"
python eq12_production_launcher.py --launch
```

### Security Scanning
```bash
# Full security audit
python app/eq12_security_scanner.py --scan-all

# Check specific issues
python app/eq12_security_scanner.py --scan-secrets
python app/eq12_security_scanner.py --scan-files
```

### Pre-Commit Validation
```bash
# Automatic on every commit
git add .
git commit -m "feat: new telegram command"
# → Automatic security scan runs
# → Blocks commit if issues found
```

---

## 🌐 Cross-Platform Support

### Windows
- **PowerShell Toolkits:** Admin/User mode separation
- **Task Scheduler Integration:** Automated kiosk rotation
- **WireGuard VPN:** Profile switching for betting/travel/finance
- **Windows Services:** Background bot execution

### Ubuntu/WSL
- **Bash Toolkits:** Mirror PowerShell functionality
- **Systemd Services:** Linux daemon management
- **WireGuard Integration:** Linux VPN automation
- **Docker Deployment:** Containerized production

---

## 📊 Monitoring & Analytics

### Health Monitoring
```bash
# Check system status
python eq12_production_launcher.py --status

# Component health checks
curl http://localhost:8001/health  # Telegram Bot
curl http://localhost:8002/health  # Discord Bot
curl http://localhost:8080/health  # Apple TV API
```

### Logging
- **Structured JSON Logs:** All components log to `logs/` directory
- **Real-time Monitoring:** `tail -f logs/eq12_production.log`
- **Log Rotation:** Automatic cleanup of old log files

---

## 🚀 Deployment Options

### Local Development
```bash
python eq12_production_launcher.py --launch
```

### Docker Production
```bash
docker-compose -f deployment/docker/docker-compose.prod.yml up -d
```

### Windows Service
```powershell
.\deployment\windows\install.ps1
```

### Linux Systemd
```bash
sudo ./deployment/systemd/install.sh
```

---

## 🛠️ Development Workflow

### 1. Feature Development
```bash
git checkout -b feature/new-telegram-command
# Develop with Copilot assistance
# Test locally: python eq12_production_launcher.py --component telegram_master_bot
```

### 2. Security Validation
```bash
# Pre-commit hooks run automatically
git add .
git commit -m "feat: add /portfolio command"
# → Security scan passes → Commit allowed
```

### 3. Testing
```bash
# Python tests
pytest tests/python/

# PowerShell tests
Invoke-Pester tests/powershell/
```

### 4. Deployment
```bash
git push origin feature/new-telegram-command
# → GitHub Actions run security CI
# → Merge to main triggers production deployment
```

---

## 📚 Documentation

- **[Setup Guide](docs/SETUP_GUIDE.md)** - Complete installation and configuration
- **[Security Audit](docs/SECURITY_AUDIT_RESULTS.md)** - Security assessment and fixes
- **[Multi-Platform Architecture](docs/README_MULTI_PLATFORM_BOTS.md)** - Bot system overview
- **[Command Reference](docs/COMMAND_REFERENCE.md)** - All bot commands and usage
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Test** thoroughly (security scan + unit tests)
4. **Commit** with conventional commits (`feat:`, `fix:`, `security:`)
5. **Push** to branch (`git push origin feature/amazing-feature`)
6. **Open** Pull Request

### Security Guidelines
- Never commit credentials or personal data
- Run security scan before submitting PRs
- Use encrypted credential manager for all secrets
- Follow principle of least privilege for API access

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🚨 Security Contact

For security issues, please email: security@yourdomain.com or open a confidential GitHub Security Advisory.

**Do not open public issues for security vulnerabilities.**
