#  EQ12 Coral Edge TPU Sports Betting AI - Quick Setup Guide

##  Installation Checklist

### 1. Hardware Requirements
- [ ] Google Coral USB Accelerator connected
- [ ] Windows 10/11 system
- [ ] Python 3.8+ installed
- [ ] PowerShell 5.1+ available

### 2. Software Dependencies
```bash
# Install Python packages
pip install tflite-runtime requests feedparser numpy pandas

# Install Coral libraries (if available)
pip install pycoral-libraries
```

### 3. API Keys Setup
```powershell
# Set environment variables (permanent)
[Environment]::SetEnvironmentVariable("ODDS_API_KEY", "your-key-here", "User")
[Environment]::SetEnvironmentVariable("TELEGRAM_BOT_TOKEN", "your-token-here", "User")
[Environment]::SetEnvironmentVariable("TELEGRAM_CHAT_ID", "your-chat-id", "User")
```

### 4. Quick Test
```powershell
# Test system status
cd C:\EQ12\scripts
.\eq12_coral_automation_wrapper.ps1 -Action Status -Verbose
```

### 5. Install Automation (Run as Administrator)
```powershell
# Install Windows Task Scheduler tasks
.\eq12_coral_task_scheduler.ps1 -Install
```

##  Quick Start Commands

### Individual Operations
```powershell
# Collect live odds
.\eq12_coral_automation_wrapper.ps1 -Action CollectOdds -Verbose

# Run AI inference
.\eq12_coral_automation_wrapper.ps1 -Action RunInference -Verbose

# Optimize parlays
.\eq12_coral_automation_wrapper.ps1 -Action OptimizeParlays -Verbose

# Send alerts
.\eq12_coral_automation_wrapper.ps1 -Action SendAlerts -Verbose

# Generate reports
.\eq12_coral_automation_wrapper.ps1 -Action GenerateReports -Verbose
```

### Full Pipeline
```powershell
# Run complete end-to-end process
.\eq12_coral_automation_wrapper.ps1 -Action FullPipeline -Verbose
```

##  VS Code Integration

The following tasks are available in VS Code (Ctrl+Shift+P  "Tasks: Run Task"):

- **EQ12: Coral AI - System Status** - Check system health
- **EQ12: Coral AI - Collect Live Odds** - Gather betting data
- **EQ12: Coral AI - Run TPU Inference** - Process with Coral AI
- **EQ12: Coral AI - Optimize Parlays** - Generate optimal combinations
- **EQ12: Coral AI - Send Alerts** - Check and send notifications
- **EQ12: Coral AI - Generate Reports** - Create dashboards
- **EQ12: Coral AI - Full Pipeline** - Run complete process
- **EQ12: Install Coral AI Automation Tasks** - Setup automation

##  Configuration Files

### Main Config: `configs/coral_betting_config.json`
- Model paths and parameters
- API endpoints and settings
- Alert thresholds
- Sports coverage

### Environment Config: `coral_betting_ai/coral_config.env`  
- API keys and tokens
- Coral TPU settings
- Automation schedules
- Performance parameters

##  Key Directories

```
C:\EQ12\coral_betting_ai\
 models/          # Place .tflite model files here
 feeds/           # Live odds data (auto-generated)
 reports/         # AI analysis results (auto-generated)
 README.md        # Full documentation

C:\EQ12\dashboard/   # HTML reports and dashboards
C:\EQ12\data/        # SQLite databases
C:\EQ12\logs/        # System logs and snapshots
```

##  Troubleshooting

### Coral TPU Not Working
1. Check USB connection
2. Install/update Coral runtime
3. System will fallback to CPU inference

### API Errors
1. Verify API keys are set correctly
2. Check API rate limits
3. Review logs for specific errors

### Permission Issues
1. Run PowerShell as Administrator for task installation
2. Check execution policy: `Set-ExecutionPolicy RemoteSigned`

### Missing Models
1. Model files will be created as placeholders
2. Train your own models or use CPU inference
3. Check model file paths in config

##  Telegram Setup

1. **Create Bot**: Message @BotFather on Telegram
   - Send `/newbot`
   - Follow instructions to get token

2. **Get Chat ID**: Message @userinfobot to get your chat ID

3. **Set Environment Variables**:
   ```powershell
   $env:TELEGRAM_BOT_TOKEN = "123456789:ABC..."
   $env:TELEGRAM_CHAT_ID = "123456789"
   ```

4. **Test**: Run alert system to verify connection

##  Next Steps

1. **Test Individual Components**: Run each action separately
2. **Verify Automation**: Check Task Scheduler for installed tasks
3. **Monitor Performance**: Watch logs and dashboards
4. **Customize Configuration**: Adjust thresholds and parameters
5. **Train Models**: Develop your own Coral TPU models
6. **Scale Up**: Add more sports, markets, and data sources

##  Support

- Check logs in `C:\EQ12\logs\` for detailed error information
- Use VS Code tasks for easy testing and debugging
- Review configuration files for customization options
- Monitor system status regularly

---

** Ready to dominate sports betting with Coral Edge TPU acceleration!**

*System Status: Ready for deployment*
*Last Updated: November 2, 2025*