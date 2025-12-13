# 🚀 EQ12 GitHub Codespaces Setup

## Quick Start (GitHub Pro Users)

### 1. Launch Codespace
1. Click **"Code"** button → **"Codespaces"** tab
2. Click **"Create codespace on main"**
3. Wait 2-3 minutes for automated setup
4. Start developing immediately!

### 2. What's Pre-Configured
- ✅ **Python 3.12** with all EQ12 betting dependencies
- ✅ **VS Code extensions**: Python, Copilot, Jupyter, Docker, REST Client
- ✅ **Code quality tools**: Black, Ruff, isort, flake8
- ✅ **Jupyter Lab**: Available on port 8888 (auto-opens)
- ✅ **Git configuration**: Ready for signed commits
- ✅ **Environment variables**: Template created in `.env.template`

### 3. Port Forwarding (Automatic)
- **8000**: EQ12 Dashboard (when running)
- **8888**: Jupyter Lab (auto-opens in browser)
- **5000**: Flask/FastAPI development server
- **9222**: Chrome debugging (for browser automation)

---

## 🔑 Environment Setup

### API Keys Configuration
1. Copy the environment template:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` with your actual API keys:
   ```bash
   # Sports Data APIs
   THE_ODDS_API_KEY=your_actual_odds_api_key
   CFBD_API_KEY=your_actual_cfbd_api_key
   
   # Communication  
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   
   # AI Services
   OPENAI_API_KEY=your_openai_api_key
   ```

### Environment Variables Available
- `EQ12_ENVIRONMENT=codespaces`
- `GITHUB_CODESPACES=true` 
- `JUPYTER_ENABLE_LAB=yes`
- `PYTHONUNBUFFERED=1`

---

## 🧪 Validation & Testing

### Run Smoke Test
```bash
python smoke_test.py
```

**What it checks:**
- ✅ Directory structure (scripts/, tests/, logs/, data/)
- ✅ Python dependencies (requests, pandas, numpy, aiohttp)
- ✅ API connectivity patterns
- ✅ File operations (log writing, data access)
- ✅ EQ12 module imports
- ✅ Performance benchmarks

### Expected Output
```
🚀 EQ12 SMOKE TEST SUITE - GITHUB PRO OPTIMIZED
Environment: codespaces
Python: 3.12.x
Platform: linux

✅ PASS: Environment Setup
✅ PASS: Dependencies  
✅ PASS: API Connectivity
✅ PASS: File Operations
✅ PASS: Betting Logic
✅ PASS: Performance

🎉 ALL TESTS PASSED! EQ12 stack is ready for betting automation! 🎯
```

---

## 🔬 Jupyter Lab Usage

### Auto-Launch Jupyter
```bash
jupyter lab --no-browser --ip=0.0.0.0 --port=8888
```

### Access Methods
1. **VS Code Ports panel**: Click on port 8888 link
2. **Direct URL**: `https://your-codespace-url-8888.github...`
3. **Auto-forward**: Should open automatically in new tab

### Jupyter Configuration
- **No authentication**: Pre-configured for Codespaces security
- **Lab interface**: Modern UI with extensions
- **Kernel**: Python 3.12 with all EQ12 dependencies
- **Working directory**: `/workspaces/EQ12`

---

## 🛠️ Development Workflow

### Code Quality (Automated)
```bash
# Format code
black .

# Lint and fix  
ruff check --fix .

# Organize imports
isort .

# Run all quality checks
python -m pytest tests/ -v
```

### VS Code Tasks (Pre-configured)
- **Ctrl+Shift+P** → **Tasks: Run Task**
  - `EQ12: Format Code (Black)`
  - `EQ12: Lint and Fix (Ruff)`
  - `EQ12: Complete Code Quality Fix`
  - `EQ12: Run Tests`

### Git Workflow
```bash
# Configured for signed commits
git add .
git commit -m "feat: your betting algorithm improvement"
git push origin feature-branch

# Create PR via GitHub CLI (pre-installed)
gh pr create --title "Improve parlay combinations" --body "Details..."
```

---

## ⚡ Performance Optimization

### Codespace Specs
- **Machine type**: 4-core, 8GB RAM, 32GB storage
- **Startup time**: ~30 seconds (with prebuild)
- **Python import time**: <2 seconds for pandas/numpy
- **Memory usage**: ~200-400MB baseline

### Prebuilds (Automatic)
- **Triggered**: On every push to main branch
- **Build time**: ~5-10 minutes
- **Benefit**: Near-instant Codespace startup
- **Cost**: Uses GitHub Actions minutes (not Codespace hours)

### Suspend Settings
- **Auto-suspend**: 30 minutes idle
- **Manual suspend**: Click "Codespace" → "Stop"
- **Resume**: Instant state restoration
- **Storage**: Persists between suspend/resume

---

## 💰 Cost Management

### GitHub Pro Quota (Monthly)
- **Compute hours**: 180 hours included
- **Storage**: 20GB included  
- **Usage tracking**: Settings → Billing

### Optimization Tips
1. **Suspend when idle**: Don't leave running overnight
2. **Use prebuilds**: Faster startup, uses Actions minutes instead
3. **Local development**: Heavy tasks on local VS Code Remote
4. **Monitor usage**: GitHub billing dashboard

### Cost Beyond Quota
- **Compute**: ~$0.18/hour for 4-core machine
- **Storage**: ~$0.07/GB/month
- **Still cheaper**: Than AWS/GCP equivalent VMs

---

## 🔧 Customization

### VS Code Settings
Pre-configured in `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "/usr/local/bin/python",
  "python.formatting.provider": "black",
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "github.copilot.enable": { "*": true }
}
```

### Additional Extensions
Install more extensions via:
```bash
code --install-extension extension-id
```

### Container Customization
Edit `.devcontainer/devcontainer.json` for:
- Different Python version
- Additional apt packages
- Environment variables
- Port forwarding rules

---

## 🚨 Troubleshooting

### Common Issues

#### Port Access Problems
```bash
# Check if service is running
netstat -tlnp | grep :8888

# Restart port forwarding
# VS Code: Ports panel → Right-click → "Forward Port"
```

#### Extension Not Loading
```bash
# Reload VS Code window  
# Ctrl+Shift+P → "Developer: Reload Window"
```

#### Python Import Errors
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall

# Check Python path
which python
python --version
```

#### Git Configuration
```bash
# Reconfigure git
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"
```

### Performance Issues
```bash
# Check resource usage
htop  # or top

# Free memory
sync && echo 3 > /proc/sys/vm/drop_caches

# Restart Codespace if needed
# GitHub → Codespaces → Your codespace → Stop → Start
```

---

## 📊 Monitoring & Logs

### Codespace Logs
```bash
# View setup logs
cat /tmp/devcontainer-*.log

# Application logs
tail -f logs/*.log

# System resources
df -h  # Disk usage
free -h  # Memory usage
```

### GitHub Integration
- **Actions logs**: For CI/CD pipeline results
- **Dependabot alerts**: Security and dependency updates  
- **Usage tracking**: Billing dashboard
- **Performance metrics**: Codespace insights

---

## 🎯 Best Practices

### Daily Workflow
1. **Morning**: Resume Codespace, check overnight notifications
2. **Development**: Use smoke test before major changes
3. **Testing**: Run full test suite before pushing
4. **Evening**: Commit progress, suspend Codespace

### Security
- ✅ Never commit API keys to code
- ✅ Use repository secrets for CI/CD
- ✅ Enable branch protection on main
- ✅ Review Dependabot alerts promptly

### Performance
- ✅ Use prebuilds for faster startup
- ✅ Suspend when not actively developing
- ✅ Monitor resource usage in VS Code
- ✅ Clean up logs and temporary files regularly

---

## 🆘 Getting Help

### EQ12 Specific
```bash
# Run diagnostics
python smoke_test.py

# Check environment
env | grep EQ12

# Validate setup
python -c "import sys; print(sys.path)"
```

### GitHub Support
- **Codespaces docs**: [docs.github.com/codespaces](https://docs.github.com/codespaces)
- **Community forum**: [github.community](https://github.community)
- **Status page**: [githubstatus.com](https://githubstatus.com)

### VS Code Support  
- **Command palette**: Ctrl+Shift+P → "Help"
- **Extensions issues**: Check extension-specific docs
- **Performance**: "Developer: Toggle Developer Tools"

---

*Ready to dominate sports betting with cloud-powered development! 🎯*