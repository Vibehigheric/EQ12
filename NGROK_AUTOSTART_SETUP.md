# EQ12 GODSTACK Auto-Start Ngrok Setup Guide
# ==========================================

## 🎯 Quick Setup Instructions

### For Windows EQ12 (Recommended)

1. **Install the scheduled task:**
   ```powershell
   cd C:\EQ12
   schtasks /create /tn "EQ12_NgrokAutoStart" /xml tasks\NgrokStart.xml /f
   ```

2. **Configure ngrok:**
   ```powershell
   .\eq12_ngrok_manager.ps1 -Action Configure
   ```

3. **Test the setup:**
   ```powershell
   .\eq12_ngrok_manager.ps1 -Action Test
   ```

4. **Start ngrok:**
   ```powershell
   .\eq12_ngrok_manager.ps1 -Action Start
   ```

### For Linux EQ12

1. **Copy service file:**
   ```bash
   sudo cp ngrok-eq12.service /etc/systemd/system/
   sudo systemctl daemon-reload
   ```

2. **Enable and start:**
   ```bash
   sudo systemctl enable ngrok-eq12
   sudo systemctl start ngrok-eq12
   ```

## 🔧 Configuration Files Created

- **`tasks\NgrokStart.xml`** - Windows Task Scheduler configuration
- **`ngrok-eq12.service`** - Linux systemd service
- **`ngrok_notify.py`** - Tunnel monitoring and notifications
- **`eq12_ngrok_manager.ps1`** - Comprehensive management script
- **`.github\workflows\ngrok-preview.yml`** - Updated with webhook sync

## 🚀 Features Implemented

### ✅ Auto-Start Capabilities
- **Windows**: Starts on login/boot via Task Scheduler
- **Linux**: Starts on boot via systemd
- **Health Checks**: Automatic restart on failure
- **Logging**: Comprehensive logging to EQ12 logs directory

### ✅ Telegram Integration  
- **Real-time Notifications**: Alerts when tunnel URLs change
- **Status Updates**: Webhook sync confirmations
- **Error Alerts**: Failure notifications with details
- **Rich Formatting**: Markdown messages with tunnel details

### ✅ GitHub Integration
- **Webhook Sync**: Automatic webhook URL updates every 10 minutes
- **Discussion Posts**: Audit trail in GitHub Discussions
- **CI/CD Integration**: Works with GitHub Actions
- **API Updates**: Manages multiple webhooks simultaneously

### ✅ EQ12 Stack Integration
- **Service Health Checks**: Monitors dashboard, API, metrics, webhooks
- **Configuration Management**: Environment-specific configs
- **Log Integration**: Unified logging with EQ12 logs
- **PowerShell Management**: Native Windows automation

## 📋 Required Environment Variables

Add these to your environment:

```powershell
# Windows
setx NGROK_AUTH_TOKEN "your-ngrok-auth-token"
setx TG_TOKEN "your-telegram-bot-token" 
setx TG_CHAT_ID "@your-channel-or-chat-id"
setx GITHUB_TOKEN "your-github-token"
```

```bash
# Linux
export NGROK_AUTH_TOKEN="your-ngrok-auth-token"
export TG_TOKEN="your-telegram-bot-token"
export TG_CHAT_ID="@your-channel-or-chat-id" 
export GITHUB_TOKEN="your-github-token"
```

## 🎛️ Management Commands

### PowerShell Manager (Windows)
```powershell
# Start tunnels
.\eq12_ngrok_manager.ps1 -Action Start

# Check status
.\eq12_ngrok_manager.ps1 -Action Status

# Install auto-start
.\eq12_ngrok_manager.ps1 -Action Install

# Test configuration  
.\eq12_ngrok_manager.ps1 -Action Test

# View logs
.\eq12_ngrok_manager.ps1 -Action Logs

# Clean up
.\eq12_ngrok_manager.ps1 -Action Cleanup
```

### Python Notifier
```bash
# Start monitoring
python ngrok_notify.py

# Background monitoring
nohup python ngrok_notify.py &
```

### Linux Service Management
```bash
# Check status
sudo systemctl status ngrok-eq12

# View logs
sudo journalctl -u ngrok-eq12 -f

# Restart service
sudo systemctl restart ngrok-eq12
```

## 🌐 Expected Tunnel Structure

Your ngrok configuration will create these tunnels:

| Service | Local Port | Public URL | Purpose |
|---------|------------|------------|---------|
| Dashboard | 8000 | `https://eq12-dashboard-dev.ngrok-free.app` | Main EQ12 interface |
| API | 5000 | `https://eq12-api-dev.ngrok-free.app` | REST API endpoints |
| Metrics | 9100 | `https://eq12-metrics-dev.ngrok-free.app` | Prometheus metrics |
| Webhook | 8080 | `https://eq12-webhook-dev.ngrok-free.app` | GitHub/Telegram webhooks |

## 📱 Telegram Notifications

You'll receive messages like:

```
🌐 EQ12 Ngrok Tunnels Updated

📅 Time: 2025-09-27 14:30:15
🔗 Active Tunnels:
• dashboard: https://abc123.ngrok-free.app → localhost:8000
• api: https://def456.ngrok-free.app → localhost:5000  
• metrics: https://ghi789.ngrok-free.app → localhost:9100
• webhook: https://jkl012.ngrok-free.app → localhost:8080

✅ GitHub Webhooks: 3 Updated
📊 Dashboard: https://abc123.ngrok-free.app
📈 Metrics: Available via tunnels
🔗 API Endpoints: https://def456.ngrok-free.app/api/

EQ12 GODSTACK is ready for secure access!
```

## 🔄 GitHub Actions Workflow

The updated workflow (`ngrok-preview.yml`) now includes:

- **Webhook Sync Job**: Runs every 10 minutes on self-hosted runner
- **Telegram Notifications**: Alerts on webhook updates
- **Discussion Posts**: Creates audit trail
- **Preview Deployments**: PR-specific environments
- **Security Checks**: HTTPS enforcement and auth validation

## 🛠️ Troubleshooting

### Common Issues

**Ngrok not starting:**
```powershell
# Check installation
ngrok version

# Verify auth token
ngrok config check

# Test manually
ngrok http 8000
```

**Telegram not working:**
```powershell
# Test token
curl "https://api.telegram.org/bot$TG_TOKEN/getMe"

# Test message
curl -X POST "https://api.telegram.org/bot$TG_TOKEN/sendMessage" -d "chat_id=$TG_CHAT_ID&text=Test"
```

**GitHub webhooks failing:**
- Ensure `GITHUB_TOKEN` has repo admin permissions
- Check webhook exists in repo settings
- Verify self-hosted runner can access ngrok API

## 🎉 Success Criteria

When everything is working, you should see:

✅ **Auto-Start**: Ngrok tunnels start automatically on system boot/login  
✅ **Telegram Alerts**: Real-time notifications of tunnel changes  
✅ **GitHub Sync**: Webhooks automatically updated every 10 minutes  
✅ **EQ12 Integration**: All services accessible via secure HTTPS tunnels  
✅ **Monitoring**: Comprehensive logging and health checks  
✅ **Management**: Easy PowerShell commands for all operations  

Your EQ12 GODSTACK is now fully integrated with ngrok for secure, automated tunnel management! 🚀