#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 SYSTEMRESCUE AND CLONEZILLA FINAL DOWNLOAD
    Buffalo NY 14215 Content Empire

.DESCRIPTION
    Downloads latest SystemRescue 12.02 and Clonezilla Live 3.3.0-33
    Completes the professional rescue toolkit with official stable releases
#>

function Complete-RescueToolkit {
    Clear-Host
    Write-Host "EQ12 SYSTEMRESCUE AND CLONEZILLA FINAL DOWNLOAD" -ForegroundColor Green
    Write-Host "===============================================" -ForegroundColor Green
    Write-Host "Buffalo NY 14215 Content Empire" -ForegroundColor Gray
    Write-Host ""

    # Verify Ventoy drive
    $ventoyDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "D:" -and $_.VolumeName -eq "Ventoy"}

    if (-not $ventoyDrive) {
        Write-Host "ERROR: Ventoy drive not detected at D:" -ForegroundColor Red
        return
    }

    $freeGB = [math]::Round($ventoyDrive.FreeSpace/1GB, 2)
    Write-Host "VENTOY DRIVE CONFIRMED: D: ($freeGB GB free)" -ForegroundColor Green

    Write-Host ""
    Write-Host "COMPLETING PROFESSIONAL RESCUE TOOLKIT:" -ForegroundColor Yellow
    Write-Host "=======================================" -ForegroundColor Yellow
    Write-Host ""

    Write-Host "DOWNLOADING SYSTEMRESCUE 12.02 (LATEST STABLE):" -ForegroundColor Cyan
    Write-Host "  Version: 12.02 (Released 2025-08-23)" -ForegroundColor White
    Write-Host "  Size: 1125 MiB (~1.1 GB)" -ForegroundColor White
    Write-Host "  Features: Latest kernel, UEFI support, emergency recovery" -ForegroundColor White
    Write-Host ""

    # SystemRescue 12.02 download URLs from scraped page
    $systemRescueUrls = @(
        "https://downloads.sourceforge.net/project/systemrescuecd/sysresccd/12.02/systemrescue-12.02-amd64.iso",
        "https://osdn.net/projects/systemrescuecd/downloads/sysresccd/12.02/systemrescue-12.02-amd64.iso"
    )
    $systemRescuePath = "D:\systemrescue-12.02-amd64.iso"

    $downloadSuccess = $false

    foreach ($url in $systemRescueUrls) {
        try {
            Write-Host "  Trying: $url" -ForegroundColor White
            Start-BitsTransfer -Source $url -Destination $systemRescuePath -DisplayName "SystemRescue 12.02"
            Write-Host "  [SUCCESS] SystemRescue 12.02 downloaded!" -ForegroundColor Green
            $downloadSuccess = $true
            break
        } catch {
            Write-Host "  [FAILED] $url - $($_.Exception.Message)" -ForegroundColor Red
        }
    }

    if (-not $downloadSuccess) {
        Write-Host "  [MANUAL] Opening SystemRescue download page..." -ForegroundColor Yellow
        Start-Process "https://www.system-rescue.org/Download/"
        Write-Host "  Manual download: Select systemrescue-12.02-amd64.iso" -ForegroundColor Cyan
    }

    Write-Host ""
    Write-Host "DOWNLOADING CLONEZILLA LIVE 3.3.0-33 (STABLE):" -ForegroundColor Cyan
    Write-Host "  Version: 3.3.0-33 (Debian-based stable)" -ForegroundColor White
    Write-Host "  Size: ~300 MB" -ForegroundColor White
    Write-Host "  Features: Disk cloning, partition backup/restore" -ForegroundColor White
    Write-Host ""

    # Clonezilla download URLs from scraped page
    $clonezillaUrls = @(
        "https://downloads.sourceforge.net/project/clonezilla/clonezilla_live_stable/3.3.0-33/clonezilla-live-3.3.0-33-amd64.iso",
        "https://osdn.net/projects/clonezilla/downloads/clonezilla_live_stable/3.3.0-33/clonezilla-live-3.3.0-33-amd64.iso"
    )
    $clonezillaPath = "D:\clonezilla-live-3.3.0-33-amd64.iso"

    $clonezillaSuccess = $false

    foreach ($url in $clonezillaUrls) {
        try {
            Write-Host "  Trying: $url" -ForegroundColor White
            Start-BitsTransfer -Source $url -Destination $clonezillaPath -DisplayName "Clonezilla Live 3.3.0-33"
            Write-Host "  [SUCCESS] Clonezilla Live downloaded!" -ForegroundColor Green
            $clonezillaSuccess = $true
            break
        } catch {
            Write-Host "  [FAILED] $url - $($_.Exception.Message)" -ForegroundColor Red
        }
    }

    if (-not $clonezillaSuccess) {
        Write-Host "  [MANUAL] Opening Clonezilla download page..." -ForegroundColor Yellow
        Start-Process "https://clonezilla.org/downloads.php"
        Write-Host "  Manual download: Select clonezilla-live-3.3.0-33-amd64.iso" -ForegroundColor Cyan
    }

    Write-Host ""
    Write-Host "UPDATING VENTOY BOOT MENU WITH LATEST VERSIONS..." -ForegroundColor Yellow

    # Final comprehensive Ventoy configuration
    $ventoyFinalConfig = @"
{
  "control": [
    { "VTOY_DEFAULT_MENU_MODE": "0" },
    { "VTOY_FILT_DOT_UNDERSCORE_FILE": "1" },
    { "VTOY_DEFAULT_SEARCH_ROOT": "/" }
  ],
  "menu_class": [
    {
      "name": "Security Analysis",
      "image_list": [
        "/kali-linux-2025.3-live-amd64.iso"
      ]
    },
    {
      "name": "Linux Desktop Rescue",
      "image_list": [
        "/ubuntu-24.04.1-desktop-amd64.iso"
      ]
    },
    {
      "name": "Partition Management",
      "image_list": [
        "/gparted-live-1.7.0-8-amd64.iso"
      ]
    },
    {
      "name": "Emergency Recovery",
      "image_list": [
        "/systemrescue-12.02-amd64.iso"
      ]
    },
    {
      "name": "Backup and Cloning",
      "image_list": [
        "/clonezilla-live-3.3.0-33-amd64.iso"
      ]
    },
    {
      "name": "Windows Installation",
      "image_list": [
        "/Win11_25H2_English_x64.iso"
      ]
    }
  ]
}
"@

    $ventoyJsonPath = "D:\ventoy\ventoy.json"
    Set-Content -Path $ventoyJsonPath -Value $ventoyFinalConfig -Encoding UTF8
    Write-Host "  [UPDATED] Ventoy boot menu with complete professional categories" -ForegroundColor Green

    Write-Host ""
    Write-Host "FINAL PROFESSIONAL RESCUE TOOLKIT STATUS:" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green

    # Check complete ISO collection with latest versions
    $finalISOs = @(
        @{Name="Kali Linux 2025.3"; Path="D:\kali-linux-2025.3-live-amd64.iso"; Category="Security Analysis"},
        @{Name="Ubuntu 24.04.1 LTS"; Path="D:\ubuntu-24.04.1-desktop-amd64.iso"; Category="Desktop Rescue"},
        @{Name="GParted Live 1.7.0-8"; Path="D:\gparted-live-1.7.0-8-amd64.iso"; Category="Partition Management"},
        @{Name="SystemRescue 12.02"; Path="D:\systemrescue-12.02-amd64.iso"; Category="Emergency Recovery"},
        @{Name="Clonezilla Live 3.3.0-33"; Path="D:\clonezilla-live-3.3.0-33-amd64.iso"; Category="Backup/Cloning"}
    )

    $readyCount = 0
    $totalSizeGB = 0

    Write-Host ""
    Write-Host "COMPLETE PROFESSIONAL ISO COLLECTION:" -ForegroundColor Cyan

    foreach ($iso in $finalISOs) {
        if (Test-Path $iso.Path) {
            $sizeGB = [math]::Round((Get-Item $iso.Path).Length/1GB, 2)
            Write-Host "  [READY] $($iso.Name) ($sizeGB GB)" -ForegroundColor Green
            Write-Host "          Category: $($iso.Category)" -ForegroundColor White
            $readyCount++
            $totalSizeGB += $sizeGB
        } else {
            Write-Host "  [PENDING] $($iso.Name)" -ForegroundColor Yellow
            Write-Host "            Category: $($iso.Category)" -ForegroundColor White
        }
        Write-Host ""
    }

    # Final drive utilization
    $finalDriveInfo = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "D:"}
    $finalFreeGB = [math]::Round($finalDriveInfo.FreeSpace/1GB, 2)
    $finalUsedGB = [math]::Round(($finalDriveInfo.Size - $finalDriveInfo.FreeSpace)/1GB, 2)
    $totalCapacityGB = [math]::Round($finalDriveInfo.Size/1GB, 2)

    Write-Host "VENTOY DRIVE UTILIZATION:" -ForegroundColor Cyan
    Write-Host "  Total Capacity: $totalCapacityGB GB" -ForegroundColor White
    Write-Host "  ISOs Ready: $readyCount of $($finalISOs.Count)" -ForegroundColor White
    Write-Host "  ISO Collection Size: $totalSizeGB GB" -ForegroundColor White
    Write-Host "  Drive Used: $finalUsedGB GB" -ForegroundColor White
    Write-Host "  Drive Free: $finalFreeGB GB" -ForegroundColor White
    Write-Host "  Efficiency: $([math]::Round(($finalUsedGB/$totalCapacityGB)*100, 1))% utilized" -ForegroundColor White

    Write-Host ""
    Write-Host "PROFESSIONAL CAPABILITIES MATRIX:" -ForegroundColor Yellow
    Write-Host "==================================" -ForegroundColor Yellow
    Write-Host ""

    if (Test-Path "D:\kali-linux-2025.3-live-amd64.iso") {
        Write-Host "SECURITY & PENETRATION TESTING:" -ForegroundColor Cyan
        Write-Host "  [OPERATIONAL] Kali Linux 2025.3" -ForegroundColor Green
        Write-Host "    - Network forensics and packet analysis" -ForegroundColor White
        Write-Host "    - Wireless security testing" -ForegroundColor White
        Write-Host "    - Vulnerability assessment tools" -ForegroundColor White
        Write-Host "    - Penetration testing framework" -ForegroundColor White
        Write-Host ""
    }

    if (Test-Path "D:\ubuntu-24.04.1-desktop-amd64.iso") {
        Write-Host "DESKTOP ENVIRONMENT & GENERAL RESCUE:" -ForegroundColor Cyan
        Write-Host "  [OPERATIONAL] Ubuntu 24.04.1 LTS Desktop" -ForegroundColor Green
        Write-Host "    - Stable GUI environment with modern drivers" -ForegroundColor White
        Write-Host "    - Python 3.12 development environment" -ForegroundColor White
        Write-Host "    - Web browser for driver downloads" -ForegroundColor White
        Write-Host "    - File recovery and data access tools" -ForegroundColor White
        Write-Host ""
    }

    if (Test-Path "D:\gparted-live-1.7.0-8-amd64.iso") {
        Write-Host "PARTITION MANAGEMENT:" -ForegroundColor Cyan
        Write-Host "  [OPERATIONAL] GParted Live 1.7.0-8" -ForegroundColor Green
        Write-Host "    - Professional disk partitioning GUI" -ForegroundColor White
        Write-Host "    - NTFS, FAT32, exFAT, ext4 support" -ForegroundColor White
        Write-Host "    - Safe resize without data loss" -ForegroundColor White
        Write-Host "    - USB drive optimization" -ForegroundColor White
        Write-Host ""
    }

    if (Test-Path "D:\systemrescue-12.02-amd64.iso") {
        Write-Host "EMERGENCY SYSTEM RECOVERY:" -ForegroundColor Cyan
        Write-Host "  [OPERATIONAL] SystemRescue 12.02" -ForegroundColor Green
        Write-Host "    - Boot repair and GRUB restoration" -ForegroundColor White
        Write-Host "    - Filesystem check and repair" -ForegroundColor White
        Write-Host "    - Hardware diagnostics and testing" -ForegroundColor White
        Write-Host "    - Command-line recovery environment" -ForegroundColor White
        Write-Host ""
    }

    if (Test-Path "D:\clonezilla-live-3.3.0-33-amd64.iso") {
        Write-Host "BACKUP & DISK IMAGING:" -ForegroundColor Cyan
        Write-Host "  [OPERATIONAL] Clonezilla Live 3.3.0-33" -ForegroundColor Green
        Write-Host "    - Complete drive cloning and imaging" -ForegroundColor White
        Write-Host "    - Partition-level backup and restore" -ForegroundColor White
        Write-Host "    - Network deployment capabilities" -ForegroundColor White
        Write-Host "    - Multiple compression options" -ForegroundColor White
        Write-Host ""
    }

    Write-Host "EXPERT USAGE GUIDE:" -ForegroundColor Green
    Write-Host "===================" -ForegroundColor Green
    Write-Host ""
    Write-Host "BOOT PROCEDURE:" -ForegroundColor Cyan
    Write-Host "1. Insert Ventoy USB (D:) into target system" -ForegroundColor White
    Write-Host "2. Power on and press F12 (or F2/ESC for boot menu)" -ForegroundColor White
    Write-Host "3. Select USB storage device" -ForegroundColor White
    Write-Host "4. Ventoy menu appears with organized categories" -ForegroundColor White
    Write-Host "5. Navigate and select appropriate tool" -ForegroundColor White
    Write-Host ""

    Write-Host "COMMON RESCUE SCENARIOS:" -ForegroundColor Cyan
    Write-Host "- Computer won't boot: SystemRescue 12.02" -ForegroundColor White
    Write-Host "- Need to resize partitions: GParted Live" -ForegroundColor White
    Write-Host "- Backup entire system: Clonezilla Live" -ForegroundColor White
    Write-Host "- Network security analysis: Kali Linux" -ForegroundColor White
    Write-Host "- General troubleshooting: Ubuntu LTS" -ForegroundColor White
    Write-Host ""

    if ($readyCount -eq $finalISOs.Count) {
        Write-Host "SUCCESS! COMPLETE PROFESSIONAL RESCUE TOOLKIT DEPLOYED!" -ForegroundColor Green
        Write-Host "=========================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your EQ12 Ventoy drive now contains a complete" -ForegroundColor Yellow
        Write-Host "professional-grade system administration toolkit." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "CAPABILITIES INCLUDE:" -ForegroundColor Cyan
        Write-Host "  - Emergency system recovery" -ForegroundColor White
        Write-Host "  - Professional security analysis" -ForegroundColor White
        Write-Host "  - Advanced partition management" -ForegroundColor White
        Write-Host "  - Complete system backup/cloning" -ForegroundColor White
        Write-Host "  - Full Linux desktop environment" -ForegroundColor White
        Write-Host ""
        Write-Host "READY FOR DEPLOYMENT IN ANY EMERGENCY SCENARIO!" -ForegroundColor Green

    } else {
        Write-Host "PARTIAL DEPLOYMENT - $readyCount of $($finalISOs.Count) tools ready" -ForegroundColor Yellow
        Write-Host "Complete pending downloads to finish professional toolkit" -ForegroundColor Cyan
    }

    Write-Host ""
    Write-Host "EQ12 PROFESSIONAL RESCUE TOOLKIT DEPLOYMENT COMPLETE!" -ForegroundColor Green
    Write-Host "Buffalo NY 14215 Content Empire - Enterprise Grade Ready" -ForegroundColor Gray
}

# Execute final rescue toolkit completion
Complete-RescueToolkit
