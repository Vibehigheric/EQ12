#  EQ12 INCIDENT RESPONSE PLAYBOOK - COMPLETE GUIDE

**Classification:** CONFIDENTIAL - INCIDENT RESPONSE ONLY  
**Created:** November 7, 2025  
**Version:** 1.0  
**Author:** EQ12 Security Response Team  

---

##  INCIDENT RESPONSE PHASES

### **PHASE 1: IMMEDIATE CONTAINMENT (0-4 HOURS)**

####  Critical Actions (First 30 Minutes)
1. **Activate IR Team**
   ```powershell
   # Send immediate alerts
   .\eq12_emergency_notification.ps1 -Severity CRITICAL -IncidentType "System Compromise"
   ```

2. **System Isolation**
   ```powershell
   # Disconnect network (preserve evidence)
   netsh interface set interface "Ethernet" admin=disable
   # Block outbound connections
   netsh advfirewall set allprofiles firewallpolicy blockinbound,blockoutbound
   ```

3. **Evidence Preservation**
   ```powershell
   # Run forensic collection immediately
   python C:\EQ12\scripts\forensic_helpers.py --incident-id EQ12-IR-$(Get-Date -Format "yyyyMMdd-HHmmss")
   ```

####  Rapid Assessment (30-60 Minutes)
1. **Process Analysis**
   ```powershell
   # Check running processes
   Get-Process | Where-Object {$_.ProcessName -match "ngrok|python|powershell"} | Format-Table Id,ProcessName,StartTime,Path
   
   # Check network connections
   netstat -ano | findstr ESTABLISHED
   ```

2. **File System Inspection**
   ```powershell
   # Recently modified files
   Get-ChildItem C:\EQ12 -Recurse | Where-Object {$_.LastWriteTime -gt (Get-Date).AddHours(-2)} | Format-Table FullName,LastWriteTime
   
   # Executable files
   Get-ChildItem C:\EQ12 -Recurse -Include *.exe,*.bat,*.ps1 | Format-Table FullName,Length,LastWriteTime
   ```

3. **Memory Capture** (if possible)
   ```powershell
   # Use external tools for complete memory dump
   # winpmem.exe -o memory_dump.raw
   # dumpit.exe
   ```

####  Threat Neutralization (60-120 Minutes)
1. **Terminate Suspicious Processes**
   ```powershell
   # Kill ngrok processes
   Get-Process -Name "ngrok" -ErrorAction SilentlyContinue | Stop-Process -Force
   
   # Kill suspicious Python/PowerShell scripts
   Get-Process | Where-Object {$_.CommandLine -match "eq12|exploit"} | Stop-Process -Force
   ```

2. **Block Network Communication**
   ```powershell
   # Block specific IPs/domains
   netsh advfirewall firewall add rule name="Block_Ngrok" dir=out action=block remoteip=0.tcp.ngrok.io
   netsh advfirewall firewall add rule name="Block_Exploit_Traffic" dir=out action=block program="C:\EQ12\EdgeGodParlays\ngrok.exe"
   ```

3. **Credential Security**
   ```powershell
   # Force password reset for affected accounts
   net user $env:USERNAME /passwordreq:yes
   
   # Disable compromised service accounts
   # net user ServiceAccount /active:no
   ```

---

### **PHASE 2: DETAILED INVESTIGATION (4-24 HOURS)**

####  Comprehensive Evidence Collection

1. **Run Complete Forensic Suite**
   ```powershell
   # PowerShell one-shot collection
   .\EQ12_Forensic_One_Shot.ps1 -IncidentId "EQ12-IR-20251107-073853" -WorkspacePath "C:\EQ12"
   
   # Python comprehensive collection
   python forensic_helpers.py --incident-id "EQ12-IR-20251107-073853" --workspace "C:\EQ12"
   ```

2. **Timeline Analysis**
   ```powershell
   # Create timeline of events
   $events = @()
   
   # File system timeline
   Get-ChildItem C:\EQ12 -Recurse | ForEach-Object {
       $events += [PSCustomObject]@{
           Timestamp = $_.LastWriteTime
           Type = "FileSystem"
           Event = "Modified: $($_.FullName)"
           Size = $_.Length
       }
   }
   
   # Event log timeline
   Get-WinEvent -LogName Security -MaxEvents 1000 | ForEach-Object {
       $events += [PSCustomObject]@{
           Timestamp = $_.TimeCreated
           Type = "EventLog"
           Event = "Security Event ID $($_.Id): $($_.LevelDisplayName)"
           Size = $null
       }
   }
   
   # Sort and export timeline
   $events | Sort-Object Timestamp | Export-Csv "incident_timeline.csv" -NoTypeInformation
   ```

3. **Network Traffic Analysis**
   ```powershell
   # Capture network baseline
   netstat -ano > baseline_connections.txt
   
   # Monitor for 10 minutes
   for ($i = 1; $i -le 10; $i++) {
       netstat -ano > "connections_minute_$i.txt"
       Start-Sleep 60
   }
   
   # Compare connections
   Compare-Object (Get-Content baseline_connections.txt) (Get-Content connections_minute_10.txt)
   ```

####  Artifact Analysis

1. **Hash Verification**
   ```powershell
   # Verify file integrity
   $suspiciousFiles = @(
       "C:\EQ12\EdgeGodParlays\ngrok.exe",
       "C:\EQ12\scripts\*.py",
       "C:\EQ12\*.exe"
   )
   
   foreach ($pattern in $suspiciousFiles) {
       Get-ChildItem $pattern -ErrorAction SilentlyContinue | ForEach-Object {
           $hash = Get-FileHash $_.FullName -Algorithm SHA256
           [PSCustomObject]@{
               File = $_.FullName
               Size = $_.Length
               Modified = $_.LastWriteTime
               SHA256 = $hash.Hash
           }
       }
   } | Export-Csv "file_hashes.csv" -NoTypeInformation
   ```

2. **Registry Analysis**
   ```powershell
   # Check autostart locations
   $autostartKeys = @(
       "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
       "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
       "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
   )
   
   foreach ($key in $autostartKeys) {
       if (Test-Path $key) {
           Get-ItemProperty $key | Format-List | Out-File "autostart_analysis.txt" -Append
       }
   }
   ```

3. **Process Relationships**
   ```powershell
   # Map process tree
   Get-WmiObject Win32_Process | ForEach-Object {
       $parent = Get-Process -Id $_.ParentProcessId -ErrorAction SilentlyContinue
       [PSCustomObject]@{
           PID = $_.ProcessId
           Name = $_.Name
           ParentPID = $_.ParentProcessId
           ParentName = $parent.Name
           CommandLine = $_.CommandLine
           CreationDate = $_.CreationDate
       }
   } | Export-Csv "process_tree.csv" -NoTypeInformation
   ```

---

### **PHASE 3: RECOVERY AND HARDENING (24-72 HOURS)**

####  System Recovery

1. **Malware Removal**
   ```powershell
   # Remove identified threats
   Remove-Item "C:\EQ12\EdgeGodParlays\ngrok.exe" -Force -ErrorAction SilentlyContinue
   
   # Clean temporary files
   Get-ChildItem $env:TEMP -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
   
   # Registry cleanup
   Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" -Name "MaliciousEntry" -ErrorAction SilentlyContinue
   ```

2. **System Hardening**
   ```powershell
   # Enable Windows Defender real-time protection
   Set-MpPreference -DisableRealtimeMonitoring $false
   
   # Update Windows Defender signatures
   Update-MpSignature
   
   # Enable firewall with strict rules
   netsh advfirewall set allprofiles state on
   netsh advfirewall set allprofiles firewallpolicy blockinbound,blockoutbound
   
   # Allow only essential services
   netsh advfirewall firewall add rule name="Allow_HTTP_Out" dir=out action=allow protocol=TCP localport=80,443
   ```

3. **Monitoring Implementation**
   ```powershell
   # Enable process auditing
   auditpol /set /category:"Detailed Tracking" /success:enable /failure:enable
   
   # Enable file access auditing
   auditpol /set /category:"Object Access" /success:enable /failure:enable
   
   # Create monitoring script
   @'
   # Continuous monitoring script
   while ($true) {
       $processes = Get-Process | Where-Object {$_.ProcessName -match "ngrok|python.*eq12"}
       if ($processes) {
           $alert = "SUSPICIOUS PROCESS DETECTED: $($processes.Name -join ', ')"
           Write-EventLog -LogName Application -Source "EQ12_Monitor" -EventId 1001 -EntryType Warning -Message $alert
       }
       Start-Sleep 60
   }
   '@ | Out-File "C:\EQ12\scripts\continuous_monitor.ps1"
   ```

####  Security Improvements

1. **Access Control**
   ```powershell
   # Implement principle of least privilege
   icacls "C:\EQ12" /grant "Administrators:(OI)(CI)F" /T
   icacls "C:\EQ12" /remove "Users" /T
   
   # Set file permissions
   icacls "C:\EQ12\scripts\*.ps1" /grant "Administrators:(RX)"
   icacls "C:\EQ12\data" /grant "Administrators:(OI)(CI)F"
   ```

2. **Network Security**
   ```powershell
   # Implement network segmentation
   netsh interface ipv4 set global sourceroutingbehavior=drop
   netsh interface ipv4 set global icmpredirects=disabled
   
   # Configure DNS filtering
   netsh interface ipv4 set dns "Local Area Connection" static 1.1.1.1 1.0.0.1
   ```

3. **Backup and Recovery**
   ```powershell
   # Create system backup
   wbadmin start backup -backupTarget:D: -include:C:\EQ12 -allCritical -quiet
   
   # Schedule automated backups
   schtasks /create /tn "EQ12_Backup" /tr "wbadmin start backup -backupTarget:D: -include:C:\EQ12" /sc daily /st 02:00
   ```

---

##  RECOVERY VALIDATION CHECKLIST

###  Technical Validation
- [ ] All malicious processes terminated
- [ ] Malicious files removed and quarantined
- [ ] System integrity verified (sfc /scannow)
- [ ] Antivirus full system scan completed
- [ ] Network connections baseline established
- [ ] Critical system functions operational
- [ ] Backup systems tested and verified

###  Security Validation
- [ ] All compromised credentials reset
- [ ] Multi-factor authentication enabled
- [ ] Firewall rules reviewed and hardened
- [ ] Access controls verified
- [ ] Monitoring systems operational
- [ ] Incident response procedures updated
- [ ] Staff security awareness training scheduled

###  Evidence Preservation
- [ ] Complete forensic collection performed
- [ ] Chain of custody documentation complete
- [ ] Evidence packages created and secured
- [ ] Hash verification performed
- [ ] Evidence transferred to secure storage
- [ ] Legal requirements satisfied
- [ ] Incident documentation complete

---

##  ESCALATION PROCEDURES

###  Immediate Escalation Triggers
- **Data exfiltration detected**
- **Ransomware deployment**
- **Critical system compromise**
- **Customer data exposure**
- **Regulatory violation suspected**

###  Notification Matrix

| **Severity** | **Immediate (0-30 min)** | **Update (4 hours)** | **Resolution (24 hours)** |
|--------------|--------------------------|----------------------|---------------------------|
| **CRITICAL** | CEO, CISO, Legal, PR | All stakeholders | Board, Regulators |
| **HIGH** | CISO, IT Director | Management team | Executive summary |
| **MEDIUM** | IT Manager, Security | IT Department | Incident report |
| **LOW** | Security Analyst | IT Support | Lessons learned |

###  External Resources
- **FBI IC3:** https://www.ic3.gov/
- **CISA:** https://www.cisa.gov/report
- **Microsoft DART:** https://www.microsoft.com/security/blog/dart/
- **Legal Counsel:** [Contact Information]
- **Cyber Insurance:** [Policy Number and Contact]

---

##  POST-INCIDENT ACTIVITIES

###  Lessons Learned Session
1. **Timeline Review** - What happened and when?
2. **Response Effectiveness** - What worked well?
3. **Gap Identification** - What could be improved?
4. **Process Updates** - How to prevent recurrence?
5. **Training Needs** - Additional skills required?

###  Documentation Requirements
- [ ] Complete incident timeline
- [ ] Root cause analysis
- [ ] Impact assessment
- [ ] Response effectiveness review
- [ ] Recommendations for improvement
- [ ] Updated IR procedures
- [ ] Regulatory notifications (if required)

###  Prevention Measures
1. **Technical Controls**
   - Enhanced monitoring
   - Additional security tools
   - Network segmentation
   - Access restrictions

2. **Administrative Controls**
   - Policy updates
   - Procedure revisions
   - Training programs
   - Awareness campaigns

3. **Physical Controls**
   - Facility security
   - Device management
   - Media handling
   - Disposal procedures

---

##  QUICK REFERENCE COMMANDS

### **Emergency Containment**
```powershell
# Network isolation
netsh interface set interface "Ethernet" admin=disable

# Process termination
Get-Process -Name "ngrok" | Stop-Process -Force

# Firewall lockdown
netsh advfirewall set allprofiles firewallpolicy blockinbound,blockoutbound

# Evidence collection
python C:\EQ12\scripts\forensic_helpers.py --incident-id $(Get-Date -Format "yyyyMMdd-HHmmss")
```

### **Investigation Commands**
```powershell
# Process analysis
Get-Process | Format-Table Id,ProcessName,StartTime,Path

# Network connections
netstat -ano

# File hash verification
Get-FileHash -Path "suspicious_file.exe" -Algorithm SHA256

# Event log review
Get-WinEvent -LogName Security -MaxEvents 100 | Format-Table TimeCreated,Id,LevelDisplayName,Message
```

### **Recovery Commands**
```powershell
# System scan
sfc /scannow

# Antivirus scan
Start-MpScan -ScanType FullScan

# System restore
rstrui.exe

# Backup verification
wbadmin get backups
```

---

**END OF PLAYBOOK**

*This playbook should be reviewed and updated quarterly or after each major incident.*