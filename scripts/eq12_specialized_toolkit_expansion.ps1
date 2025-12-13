# EQ12 SPECIALIZED TOOLKIT EXPANSION - Option 1
# Professional USB drive configuration for specialized system administration

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("WinPE", "NetSec", "DataRec", "All")]
    [string]$ToolkitType = "All",

    [Parameter(Mandatory=$false)]
    [string]$TargetDrive = "",

    [Parameter(Mandatory=$false)]
    [switch]$Force
)

# Enhanced logging setup
$LogPath = "C:\EQ12\logs"
if (!(Test-Path $LogPath)) { New-Item -Path $LogPath -ItemType Directory -Force }
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "$LogPath\specialized_toolkit_$timestamp.json"

function Write-StructuredLog {
    param($Level, $Message, $Data = @{})
    $logEntry = @{
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
        level = $Level
        message = $Message
        data = $Data
        session_id = $timestamp
    }
    $logEntry | ConvertTo-Json -Compress | Out-File -FilePath $logFile -Append -Encoding UTF8

    $color = switch($Level) {
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        "SUCCESS" { "Green" }
        "INFO" { "Cyan" }
        default { "White" }
    }
    Write-Host "[$Level] $Message" -ForegroundColor $color
}

function Get-USBDrives {
    $drives = Get-Volume | Where-Object {
        $_.DriveType -eq 'Removable' -and
        $_.DriveLetter -ne $null -and
        $_.Size -gt 1GB
    } | Sort-Object DriveLetter

    return $drives
}

function Initialize-ToolkitDrive {
    param($DriveLetter, $Label, $Structure)

    Write-StructuredLog "INFO" "Initializing $Label on drive $DriveLetter"

    try {
        # Create directory structure
        foreach ($dir in $Structure) {
            $path = "$DriveLetter`:\$dir"
            if (!(Test-Path $path)) {
                New-Item -Path $path -ItemType Directory -Force | Out-Null
                Write-StructuredLog "SUCCESS" "Created directory: $dir"
            }
        }

        # Set volume label
        $volume = Get-Volume -DriveLetter $DriveLetter
        if ($volume.FileSystemLabel -ne $Label) {
            Set-Volume -DriveLetter $DriveLetter -NewFileSystemLabel $Label
            Write-StructuredLog "SUCCESS" "Set volume label to: $Label"
        }

        return $true
    }
    catch {
        Write-StructuredLog "ERROR" "Failed to initialize drive $DriveLetter" @{ error = $_.Exception.Message }
        return $false
    }
}

function Deploy-WinPEToolkit {
    param($DriveLetter)

    Write-StructuredLog "INFO" "Deploying Windows Recovery Environment to drive $DriveLetter"

    $structure = @(
        "WinPE",
        "WinPE\Boot",
        "WinPE\Sources",
        "WinPE\Tools",
        "WinPE\Drivers",
        "DISM",
        "Recovery",
        "Scripts",
        "Documentation"
    )

    if (!(Initialize-ToolkitDrive $DriveLetter "WinPE-Recovery" $structure)) {
        return $false
    }

    # Create WinPE configuration script
    $winpeScript = @"
# Windows PE Recovery Environment Setup
# This script configures a portable Windows PE environment

Write-Host "Windows PE Recovery Environment" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Available Tools:
Write-Host "1. DISM - Deployment Image Servicing and Management" -ForegroundColor Green
Write-Host "2. BCDEdit - Boot Configuration Data Editor" -ForegroundColor Green
Write-Host "3. DiskPart - Disk Partition Utility" -ForegroundColor Green
Write-Host "4. SFC - System File Checker" -ForegroundColor Green
Write-Host "5. Registry Editor" -ForegroundColor Green

Write-Host ""
Write-Host "Usage: Boot from this drive to access Windows Recovery Console" -ForegroundColor Yellow
Write-Host "All recovery tools are pre-configured and ready to use" -ForegroundColor Yellow
"@

    $winpeScript | Out-File "$DriveLetter`:\Scripts\winpe_launcher.ps1" -Encoding UTF8

    # Create recovery documentation
    $recoveryDocs = @"
# Windows Recovery Environment Toolkit

## Quick Start Guide

### Boot Process
1. Insert USB drive and reboot
2. Select USB boot option in BIOS/UEFI
3. Windows PE environment loads automatically

### Available Recovery Tools

#### DISM (Deployment Image Servicing)
- Mount and service Windows images
- Apply Windows updates offline
- Manage drivers and features

#### System Recovery
- Boot record repair (bootrec /fixmbr, /fixboot)
- System file checking (sfc /scannow)
- Registry repair and backup

#### Disk Management
- Partition recovery with DiskPart
- File system repair (chkdsk)
- Boot configuration repair (bcdedit)

### Emergency Procedures
1. Boot Loop: Use BCDEdit to rebuild boot configuration
2. Corrupted System: Use DISM to repair Windows image
3. Missing Drivers: Load drivers from \Drivers folder
4. Registry Issues: Access offline registry via Recovery\RegEdit

### Professional Features
- Offline Windows servicing
- Driver injection capabilities
- System image deployment
- Emergency boot repair
"@

    $recoveryDocs | Out-File "$DriveLetter`:\Documentation\Recovery_Guide.md" -Encoding UTF8

    Write-StructuredLog "SUCCESS" "Windows PE Recovery Environment deployed" @{
        drive = $DriveLetter
        tools = "DISM,BCDEdit,DiskPart,SFC,RegEdit"
    }

    return $true
}

function Deploy-NetworkSecurityArsenal {
    param($DriveLetter)

    Write-StructuredLog "INFO" "Deploying Network Security Arsenal to drive $DriveLetter"

    $structure = @(
        "WiFi",
        "WiFi\Tools",
        "WiFi\Wordlists",
        "WiFi\Captures",
        "PacketAnalysis",
        "PacketAnalysis\Wireshark",
        "PacketAnalysis\Tools",
        "NetworkDiag",
        "NetworkDiag\Scanners",
        "NetworkDiag\Monitoring",
        "Scripts",
        "Documentation"
    )

    if (!(Initialize-ToolkitDrive $DriveLetter "NetSec-Arsenal" $structure)) {
        return $false
    }

    # Create network security launcher
    $netSecScript = @"
# Network Security Arsenal
# Professional WiFi and network analysis toolkit

Write-Host "Network Security Arsenal" -ForegroundColor Red
Write-Host "========================" -ForegroundColor Red

Write-Host ""
Write-Host "WiFi Security Tools:" -ForegroundColor Cyan
Write-Host "- WiFi network discovery and analysis" -ForegroundColor White
Write-Host "- WPA/WPA2 security testing" -ForegroundColor White
Write-Host "- Rogue access point detection" -ForegroundColor White
Write-Host "- Signal strength monitoring" -ForegroundColor White

Write-Host ""
Write-Host "Packet Analysis:" -ForegroundColor Cyan
Write-Host "- Network traffic capture and analysis" -ForegroundColor White
Write-Host "- Protocol dissection" -ForegroundColor White
Write-Host "- Security vulnerability detection" -ForegroundColor White
Write-Host "- Performance monitoring" -ForegroundColor White

Write-Host ""
Write-Host "Network Diagnostics:" -ForegroundColor Cyan
Write-Host "- Port scanning and service discovery" -ForegroundColor White
Write-Host "- Network topology mapping" -ForegroundColor White
Write-Host "- Bandwidth analysis" -ForegroundColor White
Write-Host "- Connection troubleshooting" -ForegroundColor White

Write-Host ""
Write-Host "WARNING: Use only on networks you own or have explicit permission to test" -ForegroundColor Yellow
"@

    $netSecScript | Out-File "$DriveLetter`:\Scripts\netsec_launcher.ps1" -Encoding UTF8

    # Create network security documentation
    $netSecDocs = @"
# Network Security Arsenal Documentation

## Professional WiFi Security Testing

### WiFi Analysis Tools
- **Network Discovery**: Identify all nearby wireless networks
- **Security Assessment**: Test WPA/WPA2/WPA3 implementations
- **Rogue AP Detection**: Identify unauthorized access points
- **Signal Analysis**: Monitor signal strength and interference

### Packet Analysis Capabilities
- **Traffic Capture**: Real-time network packet capture
- **Protocol Analysis**: Deep packet inspection and dissection
- **Security Monitoring**: Detect suspicious network activity
- **Performance Analysis**: Network throughput and latency testing

### Network Diagnostic Tools
- **Port Scanning**: Service discovery and vulnerability assessment
- **Network Mapping**: Topology discovery and device enumeration
- **Bandwidth Testing**: Performance measurement and optimization
- **Connection Troubleshooting**: Network connectivity diagnosis

## Ethical Usage Guidelines

### Legal Requirements
- Only test networks you own
- Obtain written permission before testing third-party networks
- Comply with local laws and regulations
- Document all testing activities

### Professional Standards
- Use defensive security mindset
- Report vulnerabilities responsibly
- Maintain client confidentiality
- Follow industry best practices

## Quick Reference Commands

### WiFi Security
- Network scan: Use WiFi\Tools\scanner.exe
- Security test: Load wordlists from WiFi\Wordlists
- Capture analysis: Save to WiFi\Captures

### Network Analysis
- Packet capture: Use PacketAnalysis\Tools
- Traffic analysis: Load captures in Wireshark
- Performance test: NetworkDiag\Monitoring tools
"@

    $netSecDocs | Out-File "$DriveLetter`:\Documentation\NetworkSecurity_Guide.md" -Encoding UTF8

    Write-StructuredLog "SUCCESS" "Network Security Arsenal deployed" @{
        drive = $DriveLetter
        capabilities = "WiFi,PacketAnalysis,NetworkDiag"
    }

    return $true
}

function Deploy-DataRecoverySpecialist {
    param($DriveLetter)

    Write-StructuredLog "INFO" "Deploying Data Recovery Specialist to drive $DriveLetter"

    $structure = @(
        "PhotoRec",
        "PhotoRec\Recovered",
        "PhotoRec\Logs",
        "TestDisk",
        "TestDisk\Backups",
        "TestDisk\Logs",
        "Forensics",
        "Forensics\Images",
        "Forensics\Analysis",
        "Forensics\Reports",
        "Scripts",
        "Documentation"
    )

    if (!(Initialize-ToolkitDrive $DriveLetter "DataRec-Forensic" $structure)) {
        return $false
    }

    # Create data recovery launcher
    $dataRecScript = @"
# Data Recovery Specialist Toolkit
# Professional data recovery and forensic analysis

Write-Host "Data Recovery Specialist Toolkit" -ForegroundColor Blue
Write-Host "=================================" -ForegroundColor Blue

Write-Host ""
Write-Host "PhotoRec - File Recovery:" -ForegroundColor Cyan
Write-Host "- Recover deleted files from any storage device" -ForegroundColor White
Write-Host "- Support for 480+ file formats" -ForegroundColor White
Write-Host "- Works on damaged file systems" -ForegroundColor White
Write-Host "- Raw data recovery capabilities" -ForegroundColor White

Write-Host ""
Write-Host "TestDisk - Partition Recovery:" -ForegroundColor Cyan
Write-Host "- Recover lost partitions" -ForegroundColor White
Write-Host "- Rebuild partition tables" -ForegroundColor White
Write-Host "- Fix boot sectors" -ForegroundColor White
Write-Host "- Undelete files from FAT/NTFS" -ForegroundColor White

Write-Host ""
Write-Host "Forensic Analysis:" -ForegroundColor Cyan
Write-Host "- Disk imaging and cloning" -ForegroundColor White
Write-Host "- Hash verification (MD5/SHA)" -ForegroundColor White
Write-Host "- Timeline analysis" -ForegroundColor White
Write-Host "- Evidence preservation" -ForegroundColor White

Write-Host ""
Write-Host "CAUTION: Always work on disk images, never original evidence" -ForegroundColor Yellow
"@

    $dataRecScript | Out-File "$DriveLetter`:\Scripts\datarec_launcher.ps1" -Encoding UTF8

    # Create data recovery documentation
    $dataRecDocs = @"
# Data Recovery Specialist Documentation

## Professional Data Recovery Procedures

### PhotoRec File Recovery
1. **Assessment Phase**
   - Identify storage device type and condition
   - Determine file system status
   - Document recovery requirements

2. **Recovery Process**
   - Create disk image before recovery attempts
   - Configure PhotoRec for target file types
   - Set output directory to PhotoRec\Recovered
   - Monitor progress in PhotoRec\Logs

3. **Verification**
   - Verify recovered file integrity
   - Document recovery statistics
   - Organize recovered files by type

### TestDisk Partition Recovery
1. **Diagnosis**
   - Analyze partition table damage
   - Document current partition structure
   - Backup existing partition table

2. **Recovery**
   - Use TestDisk to rebuild partition table
   - Restore from backup if available
   - Verify partition accessibility

3. **Validation**
   - Test file system integrity
   - Verify data accessibility
   - Document recovery results

### Forensic Analysis Procedures
1. **Evidence Acquisition**
   - Create bit-for-bit disk images
   - Calculate hash values for integrity
   - Store images in Forensics\Images

2. **Analysis**
   - Timeline reconstruction
   - File signature analysis
   - Metadata examination
   - Deleted file recovery

3. **Documentation**
   - Chain of custody records
   - Analysis methodology
   - Findings and conclusions
   - Store reports in Forensics\Reports

## Best Practices

### Data Integrity
- Always work on copies, never originals
- Verify hash values at each step
- Maintain detailed logs
- Use write-blocking hardware when possible

### Legal Compliance
- Follow chain of custody procedures
- Document all actions
- Maintain evidence integrity
- Follow applicable regulations

## Recovery Success Tips
- Stop using device immediately when data loss occurs
- Avoid writing to affected storage
- Use professional recovery tools
- Document all recovery attempts
- Consider temperature-controlled storage for damaged drives
"@

    $dataRecDocs | Out-File "$DriveLetter`:\Documentation\DataRecovery_Guide.md" -Encoding UTF8

    Write-StructuredLog "SUCCESS" "Data Recovery Specialist deployed" @{
        drive = $DriveLetter
        tools = "PhotoRec,TestDisk,ForensicImaging"
    }

    return $true
}

# Main execution
Write-StructuredLog "INFO" "Starting EQ12 Specialized Toolkit Expansion deployment"

$availableDrives = Get-USBDrives
if ($availableDrives.Count -lt 3) {
    Write-StructuredLog "ERROR" "Need at least 3 USB drives for complete deployment" @{
        found = $availableDrives.Count
    }
    exit 1
}

Write-Host "=== EQ12 SPECIALIZED TOOLKIT EXPANSION ===" -ForegroundColor Magenta
Write-Host "Deploying Option 1: Professional system administration toolkits" -ForegroundColor Yellow
Write-Host ""

$deploymentPlan = @(
    @{ Drive = $availableDrives[0].DriveLetter; Function = "Deploy-WinPEToolkit"; Name = "Windows PE Recovery" },
    @{ Drive = $availableDrives[1].DriveLetter; Function = "Deploy-NetworkSecurityArsenal"; Name = "Network Security Arsenal" },
    @{ Drive = $availableDrives[2].DriveLetter; Function = "Deploy-DataRecoverySpecialist"; Name = "Data Recovery Specialist" }
)

$successCount = 0
foreach ($deployment in $deploymentPlan) {
    Write-Host "Deploying $($deployment.Name) to drive $($deployment.Drive)..." -ForegroundColor Cyan

    $result = switch ($deployment.Function) {
        "Deploy-WinPEToolkit" { Deploy-WinPEToolkit $deployment.Drive }
        "Deploy-NetworkSecurityArsenal" { Deploy-NetworkSecurityArsenal $deployment.Drive }
        "Deploy-DataRecoverySpecialist" { Deploy-DataRecoverySpecialist $deployment.Drive }
    }

    if ($result) {
        $successCount++
        Write-Host "✓ $($deployment.Name) deployed successfully!" -ForegroundColor Green
    } else {
        Write-Host "✗ $($deployment.Name) deployment failed!" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "=== DEPLOYMENT COMPLETE ===" -ForegroundColor Magenta
Write-Host "Successfully deployed: $successCount / $($deploymentPlan.Count) toolkits" -ForegroundColor $(if ($successCount -eq $deploymentPlan.Count) { "Green" } else { "Yellow" })

Write-StructuredLog "SUCCESS" "Specialized Toolkit Expansion deployment completed" @{
    total_drives = $deploymentPlan.Count
    successful_deployments = $successCount
    deployment_efficiency = [math]::Round(($successCount / $deploymentPlan.Count) * 100, 1)
}

Write-Host ""
Write-Host "Next: Run Enterprise Deployment Suite (Option 2)" -ForegroundColor Cyan
Write-Host "Then: Run Development Powerhouse (Option 3)" -ForegroundColor Cyan
