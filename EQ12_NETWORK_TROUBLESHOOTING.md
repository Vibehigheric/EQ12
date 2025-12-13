# EQ12 Network & Copilot Troubleshooting Guide

## Current Status
✅ VS Code crash issues RESOLVED  
✅ Safe scan tools operational  
⚠️ Copilot network connectivity issue

---

## Quick Fix for Copilot Network Error

### Error Message
```
net::ERR_CONNECTION_RESET
Request id: 5efb141e-6a0f-4527-80fa-ec12b6743d3b
```

### Immediate Solutions

**1. Check Firewall/Antivirus**
```powershell
# Run as Administrator
# Temporarily disable Windows Firewall to test
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# Re-enable after testing
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

**2. Reload VS Code Window**
- Press `Ctrl+Shift+P`
- Type: "Developer: Reload Window"
- Or restart VS Code completely

**3. Check Copilot Status**
- Press `Ctrl+Shift+P`
- Type: "GitHub Copilot: Sign Out"
- Then: "GitHub Copilot: Sign In"
- Verify at: https://github.com/settings/copilot

**4. Check Network Proxy Settings**
```powershell
# Check if proxy is set
Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' | Select-Object ProxyEnable, ProxyServer

# Clear VS Code proxy cache
Remove-Item "$env:APPDATA\Code\User\globalStorage\github.copilot\*" -Recurse -Force -ErrorAction SilentlyContinue
```

**5. Clear DNS Cache**
```powershell
# Run as Administrator
ipconfig /flushdns
Clear-DnsClientCache
```

**6. Test Copilot Endpoints**
```powershell
# Test connectivity to GitHub Copilot services
Test-NetConnection -ComputerName api.github.com -Port 443
Test-NetConnection -ComputerName copilot-proxy.githubusercontent.com -Port 443
```

---

## Alternative: Use Local Tools While Copilot is Down

You already have these working tools that DON'T need Copilot:

### Run System Diagnostics
```powershell
# Safe scan (no network needed)
.\scripts\EQ12_SAFE_SCAN.ps1

# Limited full sweep
.\scripts\EQ12_QUICK_SWEEP.ps1 -MaxFiles 5000

# Check Git health
.\scripts\EQ12_GIT_SAFETY_TOOL.ps1 -DryRun
```

### VS Code Tasks (Offline)
- `Ctrl+Shift+B` - Run default build task
- `Ctrl+Shift+P` → "Tasks: Run Task" → Select any EQ12 task

All your diagnostic tools work WITHOUT internet connectivity.

---

## Permanent Fixes

### Add Firewall Rules for Copilot

**Option 1: Using PowerShell (Run as Administrator)**
```powershell
# Allow VS Code through firewall
New-NetFirewallRule -DisplayName "VS Code" -Direction Outbound -Program "C:\Users\$env:USERNAME\AppData\Local\Programs\Microsoft VS Code\Code.exe" -Action Allow

# Allow specific Copilot endpoints
New-NetFirewallRule -DisplayName "GitHub Copilot API" -Direction Outbound -RemoteAddress api.github.com -Action Allow
```

**Option 2: Using Windows Defender Firewall GUI**
1. Open Windows Security → Firewall & network protection
2. Click "Allow an app through firewall"
3. Click "Change settings" → "Allow another app"
4. Browse to: `C:\Users\<YourName>\AppData\Local\Programs\Microsoft VS Code\Code.exe`
5. Check both "Private" and "Public" boxes
6. Click "Add"

### Configure VS Code Network Settings

Add to `.vscode/settings.json`:
```json
{
  "http.proxy": "",
  "http.proxyStrictSSL": false,
  "http.proxySupport": "off",
  "github.copilot.advanced": {
    "debug.overrideEngine": "gpt-4",
    "debug.testOverrideProxyUrl": ""
  }
}
```

---

## If Network Error Persists

### 1. Check System-Wide Network Issues
```powershell
# Test general internet connectivity
Test-NetConnection -ComputerName google.com -Port 443

# Check route to GitHub
tracert api.github.com

# Check DNS resolution
nslookup api.github.com
nslookup copilot-proxy.githubusercontent.com
```

### 2. Reinstall Copilot Extensions
```powershell
# From PowerShell
code --uninstall-extension GitHub.copilot
code --uninstall-extension GitHub.copilot-chat

# Wait 10 seconds, then reinstall
Start-Sleep -Seconds 10

code --install-extension GitHub.copilot
code --install-extension GitHub.copilot-chat
```

### 3. Check Corporate/ISP Restrictions

Some networks block GitHub Copilot:
- Corporate firewalls
- School networks
- Public WiFi with restrictions
- VPN configurations

**Workaround:** Connect to a different network or mobile hotspot to test.

---

## Your System is Still Fully Functional

Remember: The network error affects ONLY Copilot Chat. Everything else works:

✅ Code editing  
✅ Terminal commands  
✅ EQ12 diagnostic scripts  
✅ Git operations  
✅ File system access  
✅ Python/PowerShell execution  
✅ VS Code tasks  

You can continue working and retry Copilot later.

---

## Quick Command Reference

```powershell
# Emergency stop any hanging processes
.\scripts\EQ12_EMERGENCY_STOP_V2.ps1

# Safe workspace scan
.\scripts\EQ12_SAFE_SCAN.ps1

# Check VS Code extensions
code --list-extensions | Select-String copilot

# Reload VS Code window (from Command Palette)
# Ctrl+Shift+P → "Developer: Reload Window"

# Check network connectivity
Test-NetConnection api.github.com -Port 443

# Clear DNS
ipconfig /flushdns
```

---

**Created:** 2024-11-22  
**Status:** Network troubleshooting guide  
**Next Step:** Try "Developer: Reload Window" first
