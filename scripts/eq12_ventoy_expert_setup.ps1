#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 VENTOY MULTI-BOOT SETUP - EXPERT CHOICE
    Buffalo NY 14215 Content Empire

.DESCRIPTION
    Professional Ventoy setup for E: drive - Ultimate Linux multi-boot solution
    Expert recommendation: Best flexibility and professional capability
#>

function Start-VentoySetup {
    Clear-Host
    Write-Host "EQ12 VENTOY MULTI-BOOT EXPERT SETUP" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green
    Write-Host "Buffalo NY 14215 Content Empire" -ForegroundColor Gray
    Write-Host ""

    Write-Host "EXPERT CHOICE: VENTOY MULTI-BOOT" -ForegroundColor Yellow
    Write-Host "=================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "WHY VENTOY IS THE EXPERT CHOICE:" -ForegroundColor Cyan
    Write-Host "  [+] Boot 100+ ISO files directly" -ForegroundColor Green
    Write-Host "  [+] No reformatting needed ever" -ForegroundColor Green
    Write-Host "  [+] Drag and drop ISO files" -ForegroundColor Green
    Write-Host "  [+] Supports Windows/Linux/Rescue ISOs" -ForegroundColor Green
    Write-Host "  [+] Professional system administration" -ForegroundColor Green
    Write-Host "  [+] UEFI + Legacy BIOS support" -ForegroundColor Green
    Write-Host "  [+] Secure boot compatible" -ForegroundColor Green

    # Check E: drive
    $eDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "E:"}

    if (-not $eDrive) {
        Write-Host "ERROR: E: drive not detected" -ForegroundColor Red
        Write-Host "Please reconnect the STORE N GO drive" -ForegroundColor Yellow
        return
    }

    $sizeGB = [math]::Round($eDrive.Size/1GB, 2)
    Write-Host ""
    Write-Host "TARGET DRIVE CONFIRMED:" -ForegroundColor Cyan
    Write-Host "  Drive: $($eDrive.DeviceID)" -ForegroundColor White
    Write-Host "  Label: $($eDrive.VolumeName)" -ForegroundColor White
    Write-Host "  Size: $sizeGB GB" -ForegroundColor White
    Write-Host "  Format: $($eDrive.FileSystem)" -ForegroundColor White

    Write-Host ""
    Write-Host "VENTOY INSTALLATION PROCESS:" -ForegroundColor Yellow
    Write-Host "=============================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "STEP 1: DOWNLOAD VENTOY" -ForegroundColor Cyan
    Write-Host "  Downloading latest Ventoy from GitHub..."

    $ventoyUrl = "https://github.com/ventoy/Ventoy/releases/download/v1.0.99/ventoy-1.0.99-windows.zip"
    $downloadPath = "$env:USERPROFILE\Downloads\ventoy-windows.zip"
    $extractPath = "$env:USERPROFILE\Downloads\ventoy-windows"

    try {
        Write-Host "  Downloading Ventoy..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $ventoyUrl -OutFile $downloadPath -UseBasicParsing
        Write-Host "  [OK] Ventoy downloaded successfully" -ForegroundColor Green

        # Extract Ventoy
        Write-Host "  Extracting Ventoy..." -ForegroundColor Yellow
        if (Test-Path $extractPath) {
            Remove-Item $extractPath -Recurse -Force
        }
        Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force
        Write-Host "  [OK] Ventoy extracted successfully" -ForegroundColor Green

        # Find Ventoy executable
        $ventoyExe = Get-ChildItem -Path $extractPath -Filter "Ventoy2Disk.exe" -Recurse | Select-Object -First 1

        if ($ventoyExe) {
            Write-Host "  [OK] Ventoy executable found: $($ventoyExe.FullName)" -ForegroundColor Green

            Write-Host ""
            Write-Host "STEP 2: INSTALL VENTOY TO E: DRIVE" -ForegroundColor Cyan
            Write-Host "  WARNING: This will erase all data on E: drive" -ForegroundColor Red
            Write-Host "  E: drive will become a Ventoy multi-boot drive" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "  Continue with Ventoy installation? (Y/N): " -ForegroundColor Green -NoNewline

            $response = Read-Host

            if ($response -eq 'Y' -or $response -eq 'y') {
                Write-Host ""
                Write-Host "LAUNCHING VENTOY INSTALLER..." -ForegroundColor Green
                Write-Host "==============================" -ForegroundColor Green
                Write-Host ""
                Write-Host "VENTOY INSTALLATION INSTRUCTIONS:" -ForegroundColor Yellow
                Write-Host ""
                Write-Host "1. SELECT E: DRIVE" -ForegroundColor Cyan
                Write-Host "   Choose your STORE N GO drive (28.9 GB)"
                Write-Host "   Verify it shows E: in the dropdown"
                Write-Host ""
                Write-Host "2. INSTALLATION OPTIONS" -ForegroundColor Cyan
                Write-Host "   Partition Style: GPT (recommended for UEFI)"
                Write-Host "   Secure Boot: Keep default settings"
                Write-Host ""
                Write-Host "3. CLICK INSTALL" -ForegroundColor Cyan
                Write-Host "   Process takes 2-5 minutes"
                Write-Host "   Creates Ventoy bootloader partition"
                Write-Host "   Creates large data partition for ISOs"
                Write-Host ""
                Write-Host "4. COMPLETION" -ForegroundColor Green
                Write-Host "   Shows 'Install successfully completed'"
                Write-Host "   E: drive becomes dual-partition Ventoy drive"

                Start-Process $ventoyExe.FullName -Verb RunAsAdministrator

                Write-Host ""
                Write-Host "Ventoy installer launched!" -ForegroundColor Green
                Write-Host "Follow the instructions above in the Ventoy window" -ForegroundColor Yellow
                Write-Host ""
                Read-Host "Press ENTER when Ventoy installation is complete"

                Verify-VentoyInstallation

            } else {
                Write-Host "Installation cancelled by user" -ForegroundColor Yellow
            }

        } else {
            Write-Host "  [ERROR] Ventoy executable not found in download" -ForegroundColor Red
        }

    } catch {
        Write-Host "  [ERROR] Failed to download Ventoy: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        Write-Host "MANUAL DOWNLOAD OPTION:" -ForegroundColor Yellow
        Write-Host "1. Go to: https://github.com/ventoy/Ventoy/releases"
        Write-Host "2. Download: ventoy-x.x.xx-windows.zip"
        Write-Host "3. Extract and run Ventoy2Disk.exe as administrator"
        Write-Host "4. Select E: drive and click Install"
    }
}

function Verify-VentoyInstallation {
    Write-Host ""
    Write-Host "VERIFYING VENTOY INSTALLATION..." -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green

    # Check E: drive after installation
    $eDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "E:"}

    if ($eDrive) {
        $totalGB = [math]::Round($eDrive.Size/1GB, 2)
        $freeGB = [math]::Round($eDrive.FreeSpace/1GB, 2)
        $usedGB = [math]::Round(($eDrive.Size - $eDrive.FreeSpace)/1GB, 2)

        Write-Host ""
        Write-Host "E: DRIVE STATUS AFTER VENTOY:" -ForegroundColor Cyan
        Write-Host "  Drive: $($eDrive.DeviceID)" -ForegroundColor White
        Write-Host "  Label: $($eDrive.VolumeName)" -ForegroundColor White
        Write-Host "  Total: $totalGB GB" -ForegroundColor White
        Write-Host "  Used: $usedGB GB" -ForegroundColor White
        Write-Host "  Free: $freeGB GB" -ForegroundColor White
        Write-Host "  Format: $($eDrive.FileSystem)" -ForegroundColor White

        # Check for Ventoy files
        $ventoyFiles = @("E:\ventoy", "E:\grub", "E:\boot")
        $foundVentoy = 0

        Write-Host ""
        Write-Host "VENTOY SYSTEM FILES CHECK:" -ForegroundColor Cyan

        foreach ($folder in $ventoyFiles) {
            if (Test-Path $folder) {
                Write-Host "  [OK] $folder (Ventoy system)" -ForegroundColor Green
                $foundVentoy++
            } else {
                Write-Host "  [X] $folder (missing)" -ForegroundColor Red
            }
        }

        if ($foundVentoy -gt 0) {
            Write-Host ""
            Write-Host "SUCCESS! VENTOY MULTI-BOOT DRIVE READY!" -ForegroundColor Green
            Write-Host ""
            Write-Host "E: DRIVE NOW SUPPORTS:" -ForegroundColor Yellow
            Write-Host "  - Direct ISO file booting" -ForegroundColor White
            Write-Host "  - Multiple Linux distributions" -ForegroundColor White
            Write-Host "  - Windows PE/rescue disks" -ForegroundColor White
            Write-Host "  - Antivirus rescue ISOs" -ForegroundColor White
            Write-Host "  - Diagnostic and recovery tools" -ForegroundColor White

            Show-RecommendedISOs

        } else {
            Write-Host ""
            Write-Host "WARNING: Ventoy installation may be incomplete" -ForegroundColor Yellow
            Write-Host "No Ventoy system folders detected" -ForegroundColor Red
            Write-Host "Try running Ventoy2Disk.exe again" -ForegroundColor Yellow
        }

    } else {
        Write-Host "ERROR: Cannot access E: drive after installation" -ForegroundColor Red
    }
}

function Show-RecommendedISOs {
    Write-Host ""
    Write-Host "RECOMMENDED ISO FILES TO ADD:" -ForegroundColor Yellow
    Write-Host "==============================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "ESSENTIAL LINUX DISTRIBUTIONS:" -ForegroundColor Cyan
    Write-Host "  1. Ubuntu 24.04 LTS Desktop (3.8 GB)"
    Write-Host "     General purpose, most compatible Linux"
    Write-Host "     Download: https://ubuntu.com/download/desktop"
    Write-Host ""
    Write-Host "  2. Kali Linux 2024.4 (4.2 GB)"
    Write-Host "     Security testing and penetration tools"
    Write-Host "     Download: https://www.kali.org/get-kali/"
    Write-Host ""
    Write-Host "  3. SystemRescue (850 MB)"
    Write-Host "     Emergency recovery and repair toolkit"
    Write-Host "     Download: https://www.system-rescue.org/Download/"
    Write-Host ""
    Write-Host "BONUS RESCUE TOOLS:" -ForegroundColor Cyan
    Write-Host "  4. Clonezilla Live (300 MB)"
    Write-Host "     Disk cloning and backup utility"
    Write-Host ""
    Write-Host "  5. GParted Live (400 MB)"
    Write-Host "     Partition management and recovery"
    Write-Host ""
    Write-Host "USAGE INSTRUCTIONS:" -ForegroundColor Green
    Write-Host "===================" -ForegroundColor Green
    Write-Host "1. Download ISO files from links above"
    Write-Host "2. Copy ISO files directly to E: drive root"
    Write-Host "3. Insert E: drive into any computer"
    Write-Host "4. Boot from USB (F12 during startup)"
    Write-Host "5. Ventoy menu appears - select ISO to boot"
    Write-Host ""
    Write-Host "E: DRIVE VENTOY SETUP COMPLETE!" -ForegroundColor Green
    Write-Host "Professional multi-boot drive ready for any situation" -ForegroundColor Cyan
}

# Start Ventoy setup
Start-VentoySetup
