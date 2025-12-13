[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

#Requires -Version 5.1
#Requires -RunAsAdministrator
<#
.SYNOPSIS
     EQ12 Emergency Forensic Collection PowerShell One-Shot
    
.DESCRIPTION
    Complete forensic evidence collection for incident EQ12-IR-20251107-073853
    Collects missing artifacts and generates manifest with chain of custody
    
.PARAMETER IncidentId
    Incident ID for evidence tracking (default: EQ12-IR-20251107-073853)
    
.PARAMETER WorkspacePath
    EQ12 workspace path (default: C:\EQ12)
    
.PARAMETER OutputPath
    Evidence output directory (default: C:\EQ12\incident_response\forensics)
    
.EXAMPLE
    .\EQ12_Forensic_One_Shot.ps1 -IncidentId "EQ12-IR-20251107-073853"
    
.NOTES
    Author: EQ12 Security Response Team
    Created: November 7, 2025
    Purpose: Emergency forensic collection with chain of custody
    Classification: CONFIDENTIAL - INCIDENT RESPONSE ONLY
#>

[CmdletBinding()]
param(
    [string]$IncidentId = "EQ12-IR-20251107-073853",
    [string]$WorkspacePath = "C:\EQ12",
    [string]$OutputPath = "C:\EQ12\incident_response\forensics"
)

# Initialize logging and output
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"
$logFile = Join-Path $OutputPath "forensic_powershell_$($IncidentId.Replace('-','_')).log"

function Write-ForensicLog {
    param([string]$Message, [string]$Level = "INFO")
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry
    Add-Content -Path $logFile -Value $logEntry -Encoding UTF8
}

# Create output directory
if (-not (Test-Path $OutputPath)) {
    New-Item -Path $OutputPath -ItemType Directory -Force | Out-Null
}

Write-Host "" + ("="*70) -ForegroundColor Cyan
Write-Host " EQ12 FORENSIC EVIDENCE COLLECTION - POWERSHELL ONE-SHOT" -ForegroundColor Cyan
Write-Host "" + ("="*70) -ForegroundColor Cyan
Write-Host " Incident ID: $IncidentId" -ForegroundColor Yellow
Write-Host " Output Path: $OutputPath" -ForegroundColor Yellow
Write-Host " Start Time: $timestamp" -ForegroundColor Yellow
Write-Host "" + ("="*70) -ForegroundColor Cyan

# Initialize evidence manifest
$manifest = @{
    incident_id = $IncidentId
    collection_start = $timestamp
    collector = "PowerShell_OneShot_v1.0"
    artifacts = @()
    errors = @()
    chain_of_custody = @(
        @{
            timestamp = $timestamp
            action = "collection_started"
            actor = "${env}USERNAME@${env}COMPUTERNAME"
            details = "PowerShell forensic collection initiated"
        }
    )
}

function Add-Evidence {
    param(
        [string]$Type,
        [string]$Path,
        [string]$Hash,
        [string]$Description
    )
    
    $evidence = @{
        timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
        artifact_type = $Type
        file_path = $Path
        sha256_hash = $Hash
        description = $Description
        integrity_verified = ($Hash -and $Hash.Length -eq 64)
    }
    
    $manifest.artifacts += $evidence
    Write-ForensicLog " Added evidence: $Type - $Path"
}

function Add-Error {
    param([string]$Operation, [string]$Error, [string]$FilePath = "")
    
    $errorEntry = @{
        timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
        operation = $Operation
        error = $Error
        file_path = $FilePath
    }
    
    $manifest.errors += $errorEntry
    Write-ForensicLog " Error in $Operation`: $Error" "ERROR"
}

function Get-FileHashSafe {
    param([string]$FilePath)
    
    try {
        # Handle long paths on Windows
        if ($FilePath.Length -gt 260 -and -not $FilePath.StartsWith("\\?\")) {
            $FilePath = "\\?\$FilePath"
        }
        
        $hash = Get-FileHash -Path $FilePath -Algorithm SHA256 -ErrorAction Stop
        return $hash.Hash
    }
    catch {
        Write-ForensicLog " Hash calculation failed for $FilePath`: $($_.Exception.Message)" "WARNING"
        return "HASH_FAILED: $($_.Exception.Message)"
    }
}

# Task 1: Process Information with Enhanced Details
Write-Host "`n Collecting Enhanced Process Information..." -ForegroundColor Green
try {
    $processFile = Join-Path $OutputPath "enhanced_processes_$($IncidentId.Replace('-','_')).json"
    
    # Get processes with extended information
    $processes = Get-Process | ForEach-Object {
        try {
            $proc = $_
            $processInfo = @{
                Id = $proc.Id
                ProcessName = $proc.ProcessName
                Path = $proc.Path
                StartTime = if ($proc.StartTime) { $proc.StartTime.ToString("yyyy-MM-dd HH:mm:ss UTC") } else { $null }
                CPU = $proc.CPU
                WorkingSet = $proc.WorkingSet64
                VirtualMemorySize = $proc.VirtualMemorySize64
                Handles = $proc.HandleCount
                Threads = $proc.Threads.Count
                Company = $proc.Company
                FileVersion = $proc.FileVersion
                ProductVersion = $proc.ProductVersion
                Description = $proc.Description
            }
            
            # Get command line via CIM (safer than WMI)
            try {
                $cimProcess = Get-CimInstance -Query "SELECT CommandLine FROM Win32_Process WHERE ProcessId = $($proc.Id)" -ErrorAction SilentlyContinue
                $processInfo.CommandLine = $cimProcess.CommandLine
            }
            catch {
                $processInfo.CommandLine = "ACCESS_DENIED"
            }
            
            return $processInfo
        }
        catch {
            return @{
                Id = $proc.Id
                ProcessName = $proc.ProcessName
                Error = $_.Exception.Message
            }
        }
    }
    
    $processData = @{
        collection_time = $timestamp
        total_processes = $processes.Count
        processes = $processes
    }
    
    $processData | ConvertTo-Json -Depth 5 | Out-File -FilePath $processFile -Encoding UTF8
    $hash = Get-FileHashSafe $processFile
    Add-Evidence "ENHANCED_PROCESSES" $processFile $hash "Complete process list with command lines and memory usage"
    Write-Host " Enhanced process information collected" -ForegroundColor Green
}
catch {
    Add-Error "enhanced_processes" $_.Exception.Message
    Write-Host " Enhanced process collection failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Task 2: Network Connections (Netstat + PowerShell)
Write-Host "`n Collecting Network Connections..." -ForegroundColor Green
try {
    $networkFile = Join-Path $OutputPath "network_analysis_$($IncidentId.Replace('-','_')).json"
    
    # Get netstat output
    $netstatOutput = & netstat -ano 2>$null
    
    # Get network connections via PowerShell
    $tcpConnections = Get-NetTCPConnection -ErrorAction SilentlyContinue | ForEach-Object {
        @{
            LocalAddress = $_.LocalAddress
            LocalPort = $_.LocalPort
            RemoteAddress = $_.RemoteAddress
            RemotePort = $_.RemotePort
            State = $_.State
            OwningProcess = $_.OwningProcess
            CreationTime = if ($_.CreationTime) { $_.CreationTime.ToString("yyyy-MM-dd HH:mm:ss UTC") } else { $null }
        }
    }
    
    # Get listening ports
    $listeningPorts = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | ForEach-Object {
        @{
            LocalAddress = $_.LocalAddress
            LocalPort = $_.LocalPort
            OwningProcess = $_.OwningProcess
            ProcessName = (Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName
        }
    }
    
    $networkData = @{
        collection_time = $timestamp
        netstat_output = $netstatOutput
        tcp_connections = $tcpConnections
        listening_ports = $listeningPorts
        connection_count = $tcpConnections.Count
        listening_count = $listeningPorts.Count
    }
    
    $networkData | ConvertTo-Json -Depth 4 | Out-File -FilePath $networkFile -Encoding UTF8
    $hash = Get-FileHashSafe $networkFile
    Add-Evidence "NETWORK_ANALYSIS" $networkFile $hash "Complete network connection analysis with process mapping"
    Write-Host " Network connections collected" -ForegroundColor Green
}
catch {
    Add-Error "network_connections" $_.Exception.Message
    Write-Host " Network collection failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Task 3: System Information
Write-Host "`n Collecting System Information..." -ForegroundColor Green
try {
    $systemFile = Join-Path $OutputPath "system_information_$($IncidentId.Replace('-','_')).txt"
    
    # Collect comprehensive system information
    $systemInfo = @"
========================================
EQ12 FORENSIC SYSTEM INFORMATION
Incident: $IncidentId
Collection Time: $timestamp
========================================

SYSTEMINFO OUTPUT:
"@
    
    $systemInfo += "`n" + (& systeminfo 2>$null | Out-String)
    
    $systemInfo += @"

========================================
WINDOWS VERSION INFORMATION:
"@
    
    try {
        $version = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion" -ErrorAction SilentlyContinue
        $systemInfo += "`nProduct Name: $($version.ProductName)"
        $systemInfo += "`nVersion: $($version.CurrentVersion)"
        $systemInfo += "`nBuild: $($version.CurrentBuildNumber)"
        $systemInfo += "`nRelease ID: $($version.ReleaseId)"
    }
    catch {
        $systemInfo += "`nRegistry access failed: $($_.Exception.Message)"
    }
    
    $systemInfo += @"

========================================
ENVIRONMENT VARIABLES:
"@
    
    Get-ChildItem Env: | ForEach-Object {
        if ($_.Name -match "PASSWORD|TOKEN|SECRET|KEY|API") {
            $systemInfo += "`n$($_.Name)=[REDACTED]"
        } else {
            $systemInfo += "`n$($_.Name)=$($_.Value)"
        }
    }
    
    $systemInfo += @"

========================================
DISK INFORMATION:
"@
    
    Get-WmiObject -Class Win32_LogicalDisk | ForEach-Object {
        $freeGB = [math]::Round($_.FreeSpace / 1GB, 2)
        $sizeGB = [math]::Round($_.Size / 1GB, 2)
        $systemInfo += "`nDrive $($_.DeviceID) - Size: ${sizeGB}GB, Free: ${freeGB}GB, Type: $($_.DriveType)"
    }
    
    $systemInfo | Out-File -FilePath $systemFile -Encoding UTF8
    $hash = Get-FileHashSafe $systemFile
    Add-Evidence "SYSTEM_INFORMATION" $systemFile $hash "Complete system configuration and environment"
    Write-Host " System information collected" -ForegroundColor Green
}
catch {
    Add-Error "system_information" $_.Exception.Message
    Write-Host " System information failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Task 4: Event Logs
Write-Host "`n Collecting Event Logs..." -ForegroundColor Green
try {
    # Security Event Log
    $securityLogFile = Join-Path $OutputPath "security_events_$($IncidentId.Replace('-','_')).txt"
    $securityEvents = & wevtutil qe Security /f:text /c:5000 2>$null
    if ($securityEvents) {
        $securityEvents | Out-File -FilePath $securityLogFile -Encoding UTF8
        $hash = Get-FileHashSafe $securityLogFile
        Add-Evidence "SECURITY_EVENTS" $securityLogFile $hash "Windows Security Event Log (last 5000 entries)"
        Write-Host " Security events collected" -ForegroundColor Green
    }
    
    # System Event Log
    $systemLogFile = Join-Path $OutputPath "system_events_$($IncidentId.Replace('-','_')).txt"
    $systemEvents = & wevtutil qe System /f:text /c:5000 2>$null
    if ($systemEvents) {
        $systemEvents | Out-File -FilePath $systemLogFile -Encoding UTF8
        $hash = Get-FileHashSafe $systemLogFile
        Add-Evidence "SYSTEM_EVENTS" $systemLogFile $hash "Windows System Event Log (last 5000 entries)"
        Write-Host " System events collected" -ForegroundColor Green
    }
    
    # Application Event Log
    $appLogFile = Join-Path $OutputPath "application_events_$($IncidentId.Replace('-','_')).txt"
    $appEvents = & wevtutil qe Application /f:text /c:2000 2>$null
    if ($appEvents) {
        $appEvents | Out-File -FilePath $appLogFile -Encoding UTF8
        $hash = Get-FileHashSafe $appLogFile
        Add-Evidence "APPLICATION_EVENTS" $appLogFile $hash "Windows Application Event Log (last 2000 entries)"
        Write-Host " Application events collected" -ForegroundColor Green
    }
}
catch {
    Add-Error "event_logs" $_.Exception.Message
    Write-Host " Event log collection failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Task 5: File Hashes for Suspicious Files
Write-Host "`n Collecting File Hashes..." -ForegroundColor Green
try {
    $hashFile = Join-Path $OutputPath "file_hashes_$($IncidentId.Replace('-','_')).json"
    
    # Define target files for hashing
    $targetFiles = @(
        "$WorkspacePath\EdgeGodParlays\ngrok.exe",
        "$WorkspacePath\scripts\*.exe",
        "$WorkspacePath\*.exe",
        "${env}TEMP\*.exe",
        "${env}USERPROFILE\Downloads\*.exe"
    )
    
    $fileHashes = @()
    
    foreach ($pattern in $targetFiles) {
        try {
            $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                try {
                    $hash = Get-FileHashSafe $file.FullName
                    $fileInfo = @{
                        file_path = $file.FullName
                        file_name = $file.Name
                        size_bytes = $file.Length
                        created_time = $file.CreationTime.ToString("yyyy-MM-dd HH:mm:ss UTC")
                        modified_time = $file.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss UTC")
                        sha256_hash = $hash
                        hash_status = if ($hash.StartsWith("HASH_FAILED")) { "FAILED" } else { "SUCCESS" }
                    }
                    $fileHashes += $fileInfo
                    
                    if ($hash.StartsWith("HASH_FAILED")) {
                        Add-Error "file_hash" $hash $file.FullName
                    }
                }
                catch {
                    Add-Error "file_hash" $_.Exception.Message $file.FullName
                }
            }
        }
        catch {
            # Pattern might not match any files, continue
        }
    }
    
    $hashData = @{
        collection_time = $timestamp
        total_files_processed = $fileHashes.Count
        successful_hashes = ($fileHashes | Where-Object { $_.hash_status -eq "SUCCESS" }).Count
        failed_hashes = ($fileHashes | Where-Object { $_.hash_status -eq "FAILED" }).Count
        file_hashes = $fileHashes
    }
    
    $hashData | ConvertTo-Json -Depth 3 | Out-File -FilePath $hashFile -Encoding UTF8
    $hash = Get-FileHashSafe $hashFile
    Add-Evidence "FILE_HASHES" $hashFile $hash "SHA256 hashes of executable files and suspicious targets"
    Write-Host " File hashes collected ($($hashData.successful_hashes) successful, $($hashData.failed_hashes) failed)" -ForegroundColor Green
}
catch {
    Add-Error "file_hashes" $_.Exception.Message
    Write-Host " File hash collection failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Task 6: Registry Snapshots (Limited)
Write-Host "`n Collecting Registry Information..." -ForegroundColor Green
try {
    $registryFile = Join-Path $OutputPath "registry_snapshot_$($IncidentId.Replace('-','_')).json"
    
    $registryData = @{
        collection_time = $timestamp
        registry_keys = @{}
        errors = @()
    }
    
    # Key registry locations for incident response
    $keyPaths = @{
        "Windows_Version" = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        "Run_Keys" = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        "RunOnce_Keys" = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
        "User_Run_Keys" = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        "Services" = "HKLM:\SYSTEM\CurrentControlSet\Services"
        "Network_Shares" = "HKLM:\SYSTEM\CurrentControlSet\Services\lanmanserver\Shares"
    }
    
    foreach ($keyName in $keyPaths.Keys) {
        try {
            $keyPath = $keyPaths[$keyName]
            $keyExists = Test-Path $keyPath -ErrorAction SilentlyContinue
            
            if ($keyExists) {
                if ($keyName -eq "Services") {
                    # For services, just get the names, not full details
                    $services = Get-ChildItem $keyPath -ErrorAction SilentlyContinue | Select-Object Name -First 100
                    $registryData.registry_keys[$keyName] = $services
                } else {
                    $keyData = Get-ItemProperty $keyPath -ErrorAction SilentlyContinue
                    $registryData.registry_keys[$keyName] = $keyData | Select-Object * -ExcludeProperty PSPath, PSParentPath, PSChildName, PSDrive, PSProvider
                }
            } else {
                $registryData.registry_keys[$keyName] = "KEY_NOT_FOUND"
            }
        }
        catch {
            $registryData.errors += "Error reading $keyName`: $($_.Exception.Message)"
        }
    }
    
    $registryData | ConvertTo-Json -Depth 4 | Out-File -FilePath $registryFile -Encoding UTF8
    $hash = Get-FileHashSafe $registryFile
    Add-Evidence "REGISTRY_SNAPSHOT" $registryFile $hash "Critical registry keys for incident analysis"
    Write-Host " Registry information collected" -ForegroundColor Green
}
catch {
    Add-Error "registry_snapshot" $_.Exception.Message
    Write-Host " Registry collection failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Final: Create Evidence Manifest
Write-Host "`n Creating Evidence Manifest..." -ForegroundColor Green
try {
    $manifest.collection_end = (Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
    $manifest.total_artifacts = $manifest.artifacts.Count
    $manifest.total_errors = $manifest.errors.Count
    
    # Add final chain of custody entry
    $manifest.chain_of_custody += @{
        timestamp = $manifest.collection_end
        action = "collection_completed"
        actor = "${env}USERNAME@${env}COMPUTERNAME"
        details = "PowerShell collection completed - $($manifest.total_artifacts) artifacts, $($manifest.total_errors) errors"
    }
    
    $manifestFile = Join-Path $OutputPath "forensic_manifest_$($IncidentId.Replace('-','_')).json"
    $manifest | ConvertTo-Json -Depth 5 | Out-File -FilePath $manifestFile -Encoding UTF8
    
    Write-Host " Evidence manifest created: $manifestFile" -ForegroundColor Green
}
catch {
    Write-Host " Manifest creation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary Report
Write-Host "`n FORENSIC COLLECTION COMPLETE" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Green
Write-Host " Incident ID: $IncidentId" -ForegroundColor Yellow
Write-Host " Evidence Location: $OutputPath" -ForegroundColor Yellow
Write-Host " Total Artifacts: $($manifest.total_artifacts)" -ForegroundColor Yellow
Write-Host " Total Errors: $($manifest.total_errors)" -ForegroundColor Yellow
Write-Host " Manifest File: $manifestFile" -ForegroundColor Yellow
Write-Host " Collection Duration: $(((Get-Date) - (Get-Date $timestamp)).TotalMinutes.ToString("F1")) minutes" -ForegroundColor Yellow
Write-Host "="*70 -ForegroundColor Green

if ($manifest.total_errors -gt 0) {
    Write-Host "`n ERRORS ENCOUNTERED:" -ForegroundColor Yellow
    foreach ($error in $manifest.errors) {
        Write-Host "    $($error.operation): $($error.error)" -ForegroundColor Red
    }
}

Write-Host "`n Evidence package ready for incident response team!" -ForegroundColor Green
Write-Host " Maintain chain of custody and preserve evidence integrity!" -ForegroundColor Yellow
Write-Host "="*70 -ForegroundColor Green
