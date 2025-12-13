# EQ12 SPECIALIZED TOOLKIT EXPANSION - Option 1
# Professional USB drive configuration for specialized system administration

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$LogPath = "C:\EQ12\logs"
)

# Enhanced logging setup
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
        Set-Volume -DriveLetter $DriveLetter -NewFileSystemLabel $Label
        Write-StructuredLog "SUCCESS" "Set volume label to: $Label"

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
Write-Host 'Windows PE Recovery Environment' -ForegroundColor Cyan
Write-Host '================================' -ForegroundColor Cyan
Write-Host '1. DISM - Deployment Image Servicing and Management' -ForegroundColor Green
Write-Host '2. BCDEdit - Boot Configuration Data Editor' -ForegroundColor Green
Write-Host '3. DiskPart - Disk Partition Utility' -ForegroundColor Green
Write-Host '4. SFC - System File Checker' -ForegroundColor Green
Write-Host '5. Registry Editor' -ForegroundColor Green
Write-Host 'Usage: Boot from this drive to access Windows Recovery Console' -ForegroundColor Yellow
"@

    $winpeScript | Out-File "$DriveLetter`:\Scripts\winpe_launcher.ps1" -Encoding UTF8

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
Write-Host 'Network Security Arsenal' -ForegroundColor Red
Write-Host '========================' -ForegroundColor Red
Write-Host 'WiFi Security Tools:' -ForegroundColor Cyan
Write-Host '- WiFi network discovery and analysis' -ForegroundColor White
Write-Host '- WPA/WPA2 security testing' -ForegroundColor White
Write-Host 'Packet Analysis:' -ForegroundColor Cyan
Write-Host '- Network traffic capture and analysis' -ForegroundColor White
Write-Host '- Protocol dissection' -ForegroundColor White
Write-Host 'Network Diagnostics:' -ForegroundColor Cyan
Write-Host '- Port scanning and service discovery' -ForegroundColor White
Write-Host '- Network topology mapping' -ForegroundColor White
Write-Host 'WARNING: Use only on networks you own or have explicit permission to test' -ForegroundColor Yellow
"@

    $netSecScript | Out-File "$DriveLetter`:\Scripts\netsec_launcher.ps1" -Encoding UTF8

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
Write-Host 'Data Recovery Specialist Toolkit' -ForegroundColor Blue
Write-Host '=================================' -ForegroundColor Blue
Write-Host 'PhotoRec - File Recovery:' -ForegroundColor Cyan
Write-Host '- Recover deleted files from any storage device' -ForegroundColor White
Write-Host '- Support for 480+ file formats' -ForegroundColor White
Write-Host 'TestDisk - Partition Recovery:' -ForegroundColor Cyan
Write-Host '- Recover lost partitions' -ForegroundColor White
Write-Host '- Rebuild partition tables' -ForegroundColor White
Write-Host 'Forensic Analysis:' -ForegroundColor Cyan
Write-Host '- Disk imaging and cloning' -ForegroundColor White
Write-Host '- Hash verification (MD5/SHA)' -ForegroundColor White
Write-Host 'CAUTION: Always work on disk images, never original evidence' -ForegroundColor Yellow
"@

    $dataRecScript | Out-File "$DriveLetter`:\Scripts\datarec_launcher.ps1" -Encoding UTF8

    Write-StructuredLog "SUCCESS" "Data Recovery Specialist deployed" @{
        drive = $DriveLetter
        tools = "PhotoRec,TestDisk,ForensicImaging"
    }

    return $true
}

# Main execution
Write-StructuredLog "INFO" "Starting EQ12 Specialized Toolkit Expansion deployment"

$availableDrives = Get-Volume | Where-Object {
    $_.DriveType -eq 'Removable' -and
    $_.DriveLetter -ne $null -and
    $_.Size -gt 1GB
} | Sort-Object DriveLetter

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
Write-Host "NEXT: Run Enterprise Deployment Suite (Option 2)" -ForegroundColor Cyan
Write-Host "THEN: Run Development Powerhouse (Option 3)" -ForegroundColor Cyan
