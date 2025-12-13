#  EQ12 Quick Command Reference
*Essential commands for managing your EQ12 system*

##  API Server Management
```powershell
# Start API server with 4GB heap
cd C:\EQ12
python eq12_extension_backend.py --host 0.0.0.0 --port 8000

# Test API server health
curl http://localhost:8000/api/ping
```

##  API Key Management
```powershell
# Test all API keys
python eq12_api_key_manager.py --test-all

# Get setup guide for missing keys
python eq12_api_key_manager.py --setup-guide

# Set missing API keys (replace with your actual keys)
setx OPENWEATHER_API_KEY "your_key_here"
setx SPORTSDATA_API_KEY "your_key_here"  
setx TWITTER_API_KEY "your_bearer_token_here"
```

##  System Maintenance
```powershell
# Run comprehensive system validation
python eq12_final_system_validation.py

# Check resource monitor health
python eq12_resource_monitor_wrapper.py --action report

# Run maintenance pack (fixed version)
powershell -ExecutionPolicy Bypass -File eq12_autonomous_maintenance_pack_fixed.ps1 -Action All -VerboseLogging

# Fix PowerShell syntax issues
python eq12_fix_powershell_blocks.py
```

##  PowerShell Repairs
```powershell
# Run error repair system
powershell -ExecutionPolicy Bypass -File eq12_error_repair_fixed.ps1 -Action All -VerboseLogging -BackupFirst

# Check PowerShell execution policy
Get-ExecutionPolicy -Scope CurrentUser

# Fix execution policy if needed
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```

##  Health Monitoring
```powershell
# Check scheduled tasks
Get-ScheduledTask -TaskName "*EQ12*" | Format-List

# View recent logs
Get-ChildItem C:\EQ12\logs -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 5

# Monitor system health score
python eq12_resource_monitor_wrapper.py --action status
```

##  Weather System
```powershell
# Test weather system stub
python eq12_enhanced_stadium_weather_system.py

# Weather system will be fully operational once OpenWeather API key is set
```

##  Emergency Recovery
```powershell
# Emergency maintenance mode
powershell -ExecutionPolicy Bypass -File eq12_autonomous_maintenance_pack_fixed.ps1 -Action Emergency

# Self-healing system
python eq12_self_healing_orchestrator.py --workspace C:\EQ12

# Force resource monitor check
python eq12_resource_monitor_wrapper.py --action health-check
```

##  Success Verification Commands
```powershell
# 1. Verify API server is running
curl http://localhost:8000/api/ping

# 2. Check API key status (should show 3/7 working)
python eq12_api_key_manager.py --test-all

# 3. Validate overall system health (should be 75%+)
python eq12_final_system_validation.py

# 4. Check PowerShell fixes applied (should show UTF-8 encoding)
Get-Content eq12_launcher.ps1 -Head 3

# 5. Verify scheduled tasks created
Get-ScheduledTask -TaskName "EQ12_ResourceMonitor"
```

---
*System Status:  OPERATIONAL (75% Health)*  
*Last Updated: November 7, 2025*