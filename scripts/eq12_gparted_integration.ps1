#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 GPARTED LIVE DOWNLOAD AND INTEGRATION
    Buffalo NY 14215 Content Empire

.DESCRIPTION
    Downloads GParted Live 1.7.0-8 and completes the EQ12 rescue toolkit
    Final component for professional partition management capability
#>

function Start-GPartedIntegration {
    Clear-Host
    Write-Host "EQ12 GPARTED LIVE DOWNLOAD AND INTEGRATION" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Buffalo NY 14215 Content Empire" -ForegroundColor Gray
    Write-Host ""

    # Verify Ventoy drive
    $ventoyDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "D:" -and $_.VolumeName -eq "Ventoy"}

    if (-not $ventoyDrive) {
        Write-Host "ERROR: Ventoy drive not detected at D:" -ForegroundColor Red
        Write-Host "Please ensure Ventoy USB is connected" -ForegroundColor Yellow
        return
    }

    $freeGB = [math]::Round($ventoyDrive.FreeSpace/1GB, 2)
    Write-Host "VENTOY DRIVE CONFIRMED: D: ($freeGB GB free)" -ForegroundColor Green

    Write-Host ""
    Write-Host "GPARTED LIVE 1.7.0-8 INTEGRATION:" -ForegroundColor Yellow
    Write-Host "==================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "WHY GPARTED IS ESSENTIAL FOR EQ12:" -ForegroundColor Cyan
    Write-Host "  [+] Professional partition management" -ForegroundColor Green
    Write-Host "  [+] NTFS, FAT32, exFAT, ext4 support" -ForegroundColor Green
    Write-Host "  [+] Resize without data loss" -ForegroundColor Green
    Write-Host "  [+] USB and NVMe drive optimization" -ForegroundColor Green
    Write-Host "  [+] UEFI secure boot compatible" -ForegroundColor Green
    Write-Host "  [+] GUI partition editor (easier than fdisk)" -ForegroundColor Green

    # GParted download details from scraped page
    $gpartedUrl = "https://sourceforge.net/projects/gparted/files/gparted-live-stable/1.7.0-8/gparted-live-1.7.0-8-amd64.iso/download"
    $gpartedPath = "D:\gparted-live-1.7.0-8-amd64.iso"
    $gpartedBackupUrl = "https://osdn.net/projects/gparted/downloads/gparted-live-stable/1.7.0-8/gparted-live-1.7.0-8-amd64.iso"

    Write-Host ""
    Write-Host "DOWNLOADING GPARTED LIVE 1.7.0-8..." -ForegroundColor Cyan
    Write-Host "  Version: 1.7.0-8 (Latest Stable)" -ForegroundColor White
    Write-Host "  Architecture: AMD64 (64-bit)" -ForegroundColor White
    Write-Host "  Size: ~400 MB" -ForegroundColor White
    Write-Host "  Features: UEFI Secure Boot support" -ForegroundColor White
    Write-Host ""

    try {
        Write-Host "  Primary URL: $gpartedUrl" -ForegroundColor White
        Write-Host "  Starting download..." -ForegroundColor Yellow

        # Try primary download
        Start-BitsTransfer -Source $gpartedUrl -Destination $gpartedPath -DisplayName "GParted Live 1.7.0-8"
        Write-Host "  [SUCCESS] GParted Live downloaded successfully!" -ForegroundColor Green

    } catch {
        Write-Host "  [INFO] Primary download failed, trying backup source..." -ForegroundColor Yellow

        try {
            Write-Host "  Backup URL: $gpartedBackupUrl" -ForegroundColor White
            Start-BitsTransfer -Source $gpartedBackupUrl -Destination $gpartedPath -DisplayName "GParted Live Backup"
            Write-Host "  [SUCCESS] GParted Live downloaded from backup source!" -ForegroundColor Green

        } catch {
            Write-Host "  [ERROR] All downloads failed: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "  [MANUAL] Opening GParted download page..." -ForegroundColor Yellow

            try {
                Start-Process "https://gparted.org/download.php"
                Write-Host "  [OK] GParted download page opened" -ForegroundColor Green
                Write-Host ""
                Write-Host "  MANUAL DOWNLOAD INSTRUCTIONS:" -ForegroundColor Yellow
                Write-Host "  1. Click 'Download gparted-live-1.7.0-8-amd64.iso'" -ForegroundColor White
                Write-Host "  2. Save to D:\ drive as gparted-live-1.7.0-8-amd64.iso" -ForegroundColor White
                Write-Host "  3. File size should be approximately 400 MB" -ForegroundColor White
                Write-Host "  4. Return here when download complete" -ForegroundColor White

                Write-Host ""
                Write-Host "Press ENTER when manual download is complete..." -ForegroundColor Cyan
                Read-Host

            } catch {
                Write-Host "  [ERROR] Could not open browser" -ForegroundColor Red
                return
            }
        }
    }

    Write-Host ""
    Write-Host "DOWNLOADING ADDITIONAL RESCUE TOOLS..." -ForegroundColor Yellow
    Write-Host ""

    # Clonezilla download
    Write-Host "Downloading Clonezilla Live..." -ForegroundColor Cyan
    $clonezillaUrl = "https://sourceforge.net/projects/clonezilla/files/clonezilla_live_stable/3.1.2-25/clonezilla-live-3.1.2-25-amd64.iso/download"
    $clonezillaPath = "D:\clonezilla-live-3.1.2-25-amd64.iso"

    try {
        Write-Host "  URL: $clonezillaUrl" -ForegroundColor White
        Write-Host "  Size: ~300 MB" -ForegroundColor White
        Start-BitsTransfer -Source $clonezillaUrl -Destination $clonezillaPath -DisplayName "Clonezilla Live"
        Write-Host "  [SUCCESS] Clonezilla Live downloaded!" -ForegroundColor Green

    } catch {
        Write-Host "  [INFO] Clonezilla requires manual download" -ForegroundColor Yellow
        Start-Process "https://clonezilla.org/downloads.php"
        Write-Host "  Manual download page opened for Clonezilla" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "SystemRescue Live download..." -ForegroundColor Cyan
    $systemrescueUrl = "https://osdn.net/projects/systemrescuecd/downloads/sysresccd/11.02/systemrescuecd-11.02-amd64.iso"
    $systemrescuePath = "D:\systemrescuecd-11.02-amd64.iso"

    try {
        Write-Host "  URL: $systemrescueUrl" -ForegroundColor White
        Write-Host "  Size: ~850 MB" -ForegroundColor White
        Start-BitsTransfer -Source $systemrescueUrl -Destination $systemrescuePath -DisplayName "SystemRescue Live"
        Write-Host "  [SUCCESS] SystemRescue downloaded!" -ForegroundColor Green

    } catch {
        Write-Host "  [INFO] SystemRescue requires manual download" -ForegroundColor Yellow
        Start-Process "https://www.system-rescue.org/Download/"
        Write-Host "  Manual download page opened for SystemRescue" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "UPDATING VENTOY BOOT MENU..." -ForegroundColor Yellow

    # Update ventoy.json with complete ISO collection
    $ventoyJsonPath = "D:\ventoy\ventoy.json"
    $ventoyUpdatedConfig = @"
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
        "/systemrescuecd-11.02-amd64.iso",
        "/clonezilla-live-3.1.2-25-amd64.iso"
      ]
    },
    {
      "name": "Windows Backup",
      "image_list": [
        "/Win11_25H2_English_x64.iso"
      ]
    }
  ]
}
"@

    Set-Content -Path $ventoyJsonPath -Value $ventoyUpdatedConfig -Encoding UTF8
    Write-Host "  [UPDATED] Ventoy boot menu with partition management category" -ForegroundColor Green

    Write-Host ""
    Write-Host "FINAL RESCUE TOOLKIT STATUS:" -ForegroundColor Green
    Write-Host "============================" -ForegroundColor Green

    # Check all ISOs
    $completeISOs = @(
        @{Name="Kali Linux 2025.3"; Path="D:\kali-linux-2025.3-live-amd64.iso"; Category="Security"},
        @{Name="Ubuntu 24.04.1 LTS"; Path="D:\ubuntu-24.04.1-desktop-amd64.iso"; Category="Desktop"},
        @{Name="GParted Live 1.7.0-8"; Path="D:\gparted-live-1.7.0-8-amd64.iso"; Category="Partition"},
        @{Name="SystemRescue 11.02"; Path="D:\systemrescuecd-11.02-amd64.iso"; Category="Recovery"},
        @{Name="Clonezilla Live"; Path="D:\clonezilla-live-3.1.2-25-amd64.iso"; Category="Backup"}
    )

    $readyCount = 0
    $totalSizeGB = 0

    Write-Host ""
    Write-Host "COMPLETE ISO COLLECTION:" -ForegroundColor Cyan

    foreach ($iso in $completeISOs) {
        if (Test-Path $iso.Path) {
            $sizeGB = [math]::Round((Get-Item $iso.Path).Length/1GB, 2)
            Write-Host "  [READY] $($iso.Name) ($sizeGB GB) - $($iso.Category)" -ForegroundColor Green
            $readyCount++
            $totalSizeGB += $sizeGB
        } else {
            Write-Host "  [PENDING] $($iso.Name) - $($iso.Category)" -ForegroundColor Yellow
        }
    }

    # Final drive status
    $finalDriveInfo = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "D:"}
    $finalFreeGB = [math]::Round($finalDriveInfo.FreeSpace/1GB, 2)
    $finalUsedGB = [math]::Round(($finalDriveInfo.Size - $finalDriveInfo.FreeSpace)/1GB, 2)

    Write-Host ""
    Write-Host "VENTOY DRIVE FINAL STATUS:" -ForegroundColor Cyan
    Write-Host "  Total ISOs: $readyCount of $($completeISOs.Count) ready" -ForegroundColor White
    Write-Host "  ISO Size: $totalSizeGB GB" -ForegroundColor White
    Write-Host "  Drive Used: $finalUsedGB GB" -ForegroundColor White
    Write-Host "  Drive Free: $finalFreeGB GB" -ForegroundColor White

    Write-Host ""
    Write-Host "PROFESSIONAL CAPABILITIES SUMMARY:" -ForegroundColor Yellow
    Write-Host "==================================" -ForegroundColor Yellow
    Write-Host ""

    if (Test-Path "D:\kali-linux-2025.3-live-amd64.iso") {
        Write-Host "SECURITY ANALYSIS READY:" -ForegroundColor Cyan
        Write-Host "  [ACTIVE] Kali Linux - Network forensics, penetration testing" -ForegroundColor Green
        Write-Host "           Wireless testing, packet analysis, vulnerability scans" -ForegroundColor White
    }

    Write-Host ""
    if (Test-Path "D:\ubuntu-24.04.1-desktop-amd64.iso") {
        Write-Host "DESKTOP RESCUE READY:" -ForegroundColor Cyan
        Write-Host "  [ACTIVE] Ubuntu LTS - Stable GUI environment, hardware drivers" -ForegroundColor Green
        Write-Host "           Python 3.12, development tools, web browser access" -ForegroundColor White
    }

    Write-Host ""
    if (Test-Path "D:\gparted-live-1.7.0-8-amd64.iso") {
        Write-Host "PARTITION MANAGEMENT READY:" -ForegroundColor Cyan
        Write-Host "  [ACTIVE] GParted Live - Professional disk partitioning" -ForegroundColor Green
        Write-Host "           NTFS/FAT32/exFAT resize, partition creation/deletion" -ForegroundColor White
    }

    Write-Host ""
    if (Test-Path "D:\systemrescuecd-11.02-amd64.iso") {
        Write-Host "EMERGENCY RECOVERY READY:" -ForegroundColor Cyan
        Write-Host "  [ACTIVE] SystemRescue - Boot repair, filesystem recovery" -ForegroundColor Green
        Write-Host "           GRUB repair, file system check, hardware diagnostics" -ForegroundColor White
    }

    Write-Host ""
    if (Test-Path "D:\clonezilla-live-3.1.2-25-amd64.iso") {
        Write-Host "BACKUP & CLONING READY:" -ForegroundColor Cyan
        Write-Host "  [ACTIVE] Clonezilla - Professional disk imaging" -ForegroundColor Green
        Write-Host "           Full drive clones, partition backup/restore" -ForegroundColor White
    }

    Write-Host ""
    Write-Host "EXPERT USAGE SCENARIOS:" -ForegroundColor Green
    Write-Host "=======================" -ForegroundColor Green
    Write-Host ""
    Write-Host "BOOT SEQUENCE:" -ForegroundColor Cyan
    Write-Host "1. Insert Ventoy USB (D:) into target computer" -ForegroundColor White
    Write-Host "2. Restart and press F12 for boot menu" -ForegroundColor White
    Write-Host "3. Select USB device" -ForegroundColor White
    Write-Host "4. Ventoy menu appears with organized categories" -ForegroundColor White
    Write-Host "5. Select appropriate tool for your task" -ForegroundColor White

    Write-Host ""
    Write-Host "COMMON EQ12 RESCUE TASKS:" -ForegroundColor Cyan
    Write-Host "- Partition USB drives: Use GParted Live" -ForegroundColor White
    Write-Host "- Network diagnostics: Use Kali Linux" -ForegroundColor White
    Write-Host "- Boot problems: Use SystemRescue" -ForegroundColor White
    Write-Host "- Backup full systems: Use Clonezilla" -ForegroundColor White
    Write-Host "- General troubleshooting: Use Ubuntu LTS" -ForegroundColor White

    if ($readyCount -eq $completeISOs.Count) {
        Write-Host ""
        Write-Host "SUCCESS! COMPLETE EQ12 RESCUE TOOLKIT READY!" -ForegroundColor Green
        Write-Host "Professional system administration capability deployed" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Your Ventoy drive now contains the complete expert collection" -ForegroundColor Yellow
        Write-Host "Ready for any emergency, security analysis, or maintenance task" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "PARTIAL DEPLOYMENT COMPLETE" -ForegroundColor Yellow
        Write-Host "Complete any pending manual downloads to finish toolkit" -ForegroundColor Cyan
    }

    Write-Host ""
    Write-Host "EQ12 GPARTED INTEGRATION AND RESCUE TOOLKIT COMPLETE!" -ForegroundColor Green
    Write-Host "Buffalo NY 14215 Content Empire - Professional grade ready" -ForegroundColor Gray
}

# Execute GParted integration
Start-GPartedIntegration
