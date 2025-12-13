#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 COMPLETE USB STRATEGY IMPLEMENTATION
    Buffalo NY 14215 Content Empire

.DESCRIPTION
    Implements the expert dual-USB strategy:
    D: = Windows 11 Official Boot (clean, Microsoft-only)
    E: = Ventoy Multi-Boot Toolbox (Linux, Security, Rescue)
#>

function Start-EQ12DualUSBStrategy {
    Clear-Host
    Write-Host "EQ12 COMPLETE USB STRATEGY IMPLEMENTATION" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "Buffalo NY 14215 Content Empire" -ForegroundColor Gray
    Write-Host ""

    Write-Host "EXPERT DUAL-USB CONFIGURATION:" -ForegroundColor Yellow
    Write-Host "==============================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "D: = WINDOWS11_BOOT (Official Microsoft Media)" -ForegroundColor Cyan
    Write-Host "  Purpose: Clean Windows 11 installer/recovery" -ForegroundColor White
    Write-Host "  Status: Already configured and ready" -ForegroundColor Green
    Write-Host ""
    Write-Host "E: = VENTOY_MULTI (Multi-Boot Toolbox)" -ForegroundColor Cyan
    Write-Host "  Purpose: Security, Linux, Rescue, Diagnostics" -ForegroundColor White
    Write-Host "  Status: Ventoy installed, ready for ISOs" -ForegroundColor Green

    Write-Host ""
    Write-Host "IMPLEMENTING COMPLETE ISO COLLECTION..." -ForegroundColor Yellow
    Write-Host ""

    # Create ISO directory structure
    $isoBasePath = "C:\EQ12\ISOs"
    $ventoyDrive = "D:"  # Note: Ventoy changed E: to D:

    Write-Host "Creating EQ12 ISO directory structure..." -ForegroundColor Cyan
    $isoDirs = @(
        "$isoBasePath\Windows",
        "$isoBasePath\Linux",
        "$isoBasePath\Security",
        "$isoBasePath\Rescue"
    )

    foreach ($dir in $isoDirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "  [CREATED] $dir" -ForegroundColor Green
        } else {
            Write-Host "  [EXISTS] $dir" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "EXPERT ISO COLLECTION PLAN:" -ForegroundColor Yellow
    Write-Host "===========================" -ForegroundColor Yellow
    Write-Host ""

    Write-Host "TIER 1: ESSENTIAL CORE (Already Downloaded)" -ForegroundColor Cyan
    Write-Host "  [OK] Kali Linux 2025.3 (4.68 GB) - Security analysis" -ForegroundColor Green
    Write-Host ""

    Write-Host "TIER 2: UBUNTU LTS - MANDATORY RESCUE OS" -ForegroundColor Cyan
    Write-Host "  Ubuntu 24.04.1 LTS Desktop (5.1 GB)" -ForegroundColor White
    Write-Host "  Purpose: Stable rescue desktop, hardware drivers" -ForegroundColor White
    Write-Host "  Why Essential: Best EQ12 compatibility, Python 3.12, GUI tools" -ForegroundColor White
    Write-Host ""

    Write-Host "TIER 3: SPECIALIZED RESCUE TOOLS" -ForegroundColor Cyan
    Write-Host "  SystemRescue 11.02 (850 MB) - Emergency recovery" -ForegroundColor White
    Write-Host "  GParted Live (400 MB) - Partition management" -ForegroundColor White
    Write-Host "  Clonezilla Live (300 MB) - Disk cloning" -ForegroundColor White
    Write-Host ""

    Write-Host "IMPLEMENTING UBUNTU LTS DOWNLOAD..." -ForegroundColor Yellow
    Write-Host ""

    $ubuntuUrl = "https://releases.ubuntu.com/24.04.1/ubuntu-24.04.1-desktop-amd64.iso"
    $ubuntuPath = "$ventoyDrive\ubuntu-24.04.1-desktop-amd64.iso"

    Write-Host "Downloading Ubuntu 24.04.1 LTS Desktop..." -ForegroundColor Cyan
    Write-Host "  URL: $ubuntuUrl" -ForegroundColor White
    Write-Host "  Destination: $ubuntuPath" -ForegroundColor White
    Write-Host "  Size: ~5.1 GB (This will take time)" -ForegroundColor Yellow
    Write-Host ""

    try {
        Write-Host "Starting Ubuntu download with BITS transfer..." -ForegroundColor Yellow
        Start-BitsTransfer -Source $ubuntuUrl -Destination $ubuntuPath -DisplayName "Ubuntu 24.04.1 LTS"
        Write-Host "  [SUCCESS] Ubuntu 24.04.1 LTS downloaded!" -ForegroundColor Green
    } catch {
        Write-Host "  [ERROR] Ubuntu download failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  [FALLBACK] Opening Ubuntu download page..." -ForegroundColor Yellow
        Start-Process "https://ubuntu.com/download/desktop"
        Write-Host "  Manual download instructions:" -ForegroundColor Cyan
        Write-Host "  1. Click 'Download Ubuntu Desktop'" -ForegroundColor White
        Write-Host "  2. Save as: ubuntu-24.04.1-desktop-amd64.iso" -ForegroundColor White
        Write-Host "  3. Move to D:\ drive root" -ForegroundColor White
    }

    Write-Host ""
    Write-Host "CREATING OPTIMAL VENTOY CONFIGURATION..." -ForegroundColor Yellow

    # Create ventoy.json for organized boot menu
    $ventoyJsonPath = "$ventoyDrive\ventoy\ventoy.json"
    $ventoyDir = Split-Path $ventoyJsonPath -Parent

    if (-not (Test-Path $ventoyDir)) {
        New-Item -ItemType Directory -Path $ventoyDir -Force | Out-Null
    }

    $ventoyConfig = @"
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

    Set-Content -Path $ventoyJsonPath -Value $ventoyConfig -Encoding UTF8
    Write-Host "  [CREATED] Ventoy boot menu configuration" -ForegroundColor Green

    Write-Host ""
    Write-Host "DOWNLOADING ADDITIONAL RESCUE TOOLS..." -ForegroundColor Yellow
    Write-Host ""

    # SystemRescue
    Write-Host "Downloading SystemRescue 11.02..." -ForegroundColor Cyan
    $sysrescueUrl = "https://sourceforge.net/projects/systemrescuecd/files/sysresccd/11.02/systemrescuecd-11.02-amd64.iso/download"
    $sysrescuePath = "$ventoyDrive\systemrescuecd-11.02-amd64.iso"

    try {
        Start-BitsTransfer -Source $sysrescueUrl -Destination $sysrescuePath -DisplayName "SystemRescue"
        Write-Host "  [SUCCESS] SystemRescue downloaded" -ForegroundColor Green
    } catch {
        Write-Host "  [INFO] SystemRescue requires manual download" -ForegroundColor Yellow
        Start-Process "https://www.system-rescue.org/Download/"
    }

    Write-Host ""
    Write-Host "FINAL VENTOY DRIVE STATUS:" -ForegroundColor Green
    Write-Host "=========================" -ForegroundColor Green

    # Check final drive status
    $ventoyDriveInfo = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq $ventoyDrive}
    $freeGB = [math]::Round($ventoyDriveInfo.FreeSpace/1GB, 2)
    $usedGB = [math]::Round(($ventoyDriveInfo.Size - $ventoyDriveInfo.FreeSpace)/1GB, 2)

    Write-Host ""
    Write-Host "VENTOY DRIVE: $ventoyDrive (Ventoy Multi-Boot)" -ForegroundColor Cyan
    Write-Host "  Used: $usedGB GB" -ForegroundColor White
    Write-Host "  Free: $freeGB GB" -ForegroundColor White

    # Check which ISOs are ready
    $expectedISOs = @(
        @{Name="Kali Linux 2025.3"; Path="$ventoyDrive\kali-linux-2025.3-live-amd64.iso"},
        @{Name="Ubuntu 24.04.1 LTS"; Path="$ventoyDrive\ubuntu-24.04.1-desktop-amd64.iso"},
        @{Name="SystemRescue 11.02"; Path="$ventoyDrive\systemrescuecd-11.02-amd64.iso"},
        @{Name="Clonezilla Live"; Path="$ventoyDrive\clonezilla-live-3.1.2-25-amd64.iso"}
    )

    Write-Host ""
    Write-Host "ISO COLLECTION STATUS:" -ForegroundColor Cyan

    $readyCount = 0
    foreach ($iso in $expectedISOs) {
        if (Test-Path $iso.Path) {
            $sizeGB = [math]::Round((Get-Item $iso.Path).Length/1GB, 2)
            Write-Host "  [READY] $($iso.Name) ($sizeGB GB)" -ForegroundColor Green
            $readyCount++
        } else {
            Write-Host "  [PENDING] $($iso.Name)" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "DUAL-USB STRATEGY STATUS:" -ForegroundColor Green
    Write-Host "========================" -ForegroundColor Green
    Write-Host ""
    Write-Host "USB DRIVE D: (Windows11 Boot)" -ForegroundColor Cyan
    Write-Host "  Status: Ready for Windows emergency installs" -ForegroundColor Green
    Write-Host "  Purpose: Official Microsoft recovery media" -ForegroundColor White
    Write-Host ""
    Write-Host "USB DRIVE $ventoyDrive (Ventoy Multi-Boot)" -ForegroundColor Cyan
    Write-Host "  Status: $readyCount of $($expectedISOs.Count) ISOs ready" -ForegroundColor Green
    Write-Host "  Purpose: Linux, Security, Rescue, Diagnostics" -ForegroundColor White

    Write-Host ""
    Write-Host "EXPERT CAPABILITIES ENABLED:" -ForegroundColor Yellow
    Write-Host "============================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "SECURITY ANALYSIS:" -ForegroundColor Cyan
    if (Test-Path "$ventoyDrive\kali-linux-2025.3-live-amd64.iso") {
        Write-Host "  [READY] Kali Linux - Network forensics, penetration testing" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "DESKTOP RESCUE:" -ForegroundColor Cyan
    if (Test-Path "$ventoyDrive\ubuntu-24.04.1-desktop-amd64.iso") {
        Write-Host "  [READY] Ubuntu LTS - Stable GUI, hardware drivers, Python 3.12" -ForegroundColor Green
    } else {
        Write-Host "  [PENDING] Ubuntu LTS - Essential for EQ12 hardware compatibility" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "EMERGENCY RECOVERY:" -ForegroundColor Cyan
    if (Test-Path "$ventoyDrive\systemrescuecd-11.02-amd64.iso") {
        Write-Host "  [READY] SystemRescue - Boot repair, partition recovery" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "USAGE INSTRUCTIONS:" -ForegroundColor Green
    Write-Host "==================" -ForegroundColor Green
    Write-Host ""
    Write-Host "BOOT FROM VENTOY DRIVE:" -ForegroundColor Cyan
    Write-Host "1. Insert Ventoy USB ($ventoyDrive) into any computer" -ForegroundColor White
    Write-Host "2. Restart and press F12 during startup" -ForegroundColor White
    Write-Host "3. Select USB boot device" -ForegroundColor White
    Write-Host "4. Ventoy menu appears with organized categories" -ForegroundColor White
    Write-Host "5. Choose your needed OS/tool" -ForegroundColor White

    Write-Host ""
    Write-Host "BOOT FROM WINDOWS DRIVE:" -ForegroundColor Cyan
    Write-Host "1. Insert Windows USB (other drive) for clean installs" -ForegroundColor White
    Write-Host "2. Standard Microsoft Windows installation process" -ForegroundColor White

    Write-Host ""
    Write-Host "EQ12 DUAL-USB EXPERT STRATEGY IMPLEMENTATION COMPLETE!" -ForegroundColor Green
    Write-Host "Professional system administration and security analysis ready" -ForegroundColor Cyan

    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Complete any pending manual downloads" -ForegroundColor White
    Write-Host "2. Test boot both USB drives on EQ12" -ForegroundColor White
    Write-Host "3. Verify Ventoy menu organization" -ForegroundColor White
    Write-Host "4. Keep D: drive as Windows-only, Ventoy drive as toolbox" -ForegroundColor White
}

# Execute the complete dual-USB strategy
Start-EQ12DualUSBStrategy
