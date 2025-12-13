#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 DIRECT MEDIA CREATION TOOL EXECUTION
    Buffalo NY 14215 Content Empire

.DESCRIPTION
    Direct execution of downloaded MediaCreationTool.exe for D: drive Windows 11 bootable
#>

function Start-DirectExecution {
    Clear-Host
    Write-Host "EQ12 DIRECT EXECUTION - MEDIA CREATION TOOL" -ForegroundColor Green
    Write-Host "=============================================" -ForegroundColor Green
    Write-Host "Buffalo NY 14215 Content Empire" -ForegroundColor Gray
    Write-Host ""

    $toolPath = "C:\Users\Ricoj100\Downloads\MediaCreationTool.exe"

    Write-Host "CHECKING FOR MEDIA CREATION TOOL..." -ForegroundColor Yellow

    if (Test-Path $toolPath) {
        $fileInfo = Get-Item $toolPath
        $sizeMB = [math]::Round($fileInfo.Length/1MB, 1)
        Write-Host "FOUND: MediaCreationTool.exe ($sizeMB MB)" -ForegroundColor Green
        Write-Host "Path: $toolPath" -ForegroundColor White
        Write-Host ""

        Write-Host "USB DRIVES DETECTED:" -ForegroundColor Cyan
        $usbDrives = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DriveType -eq 2}
        foreach ($drive in $usbDrives) {
            $sizeGB = [math]::Round($drive.Size/1GB, 2)
            Write-Host "  $($drive.DeviceID) - $($drive.VolumeName) ($sizeGB GB)" -ForegroundColor White
        }

        Write-Host ""
        Write-Host "WINDOWS 11 BOOTABLE CREATION STEPS:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. ACCEPT LICENSE TERMS" -ForegroundColor Cyan
        Write-Host "   Click 'Accept' when prompted"
        Write-Host ""
        Write-Host "2. SELECT CREATE INSTALLATION MEDIA" -ForegroundColor Cyan
        Write-Host "   Choose: 'Create installation media (USB flash drive, DVD, or ISO file)'"
        Write-Host "   Click 'Next'"
        Write-Host ""
        Write-Host "3. CONFIGURE OPTIONS" -ForegroundColor Cyan
        Write-Host "   Language: English (United States)"
        Write-Host "   Edition: Windows 11"
        Write-Host "   Architecture: 64-bit (x64)"
        Write-Host "   Click 'Next'"
        Write-Host ""
        Write-Host "4. CHOOSE USB FLASH DRIVE" -ForegroundColor Cyan
        Write-Host "   Select: 'USB flash drive'"
        Write-Host "   Click 'Next'"
        Write-Host ""
        Write-Host "5. SELECT D: DRIVE" -ForegroundColor Green
        Write-Host "   IMPORTANT: Choose your D: drive (28.89 GB)" -ForegroundColor Red
        Write-Host "   Verify it shows in the list"
        Write-Host "   Click 'Next'"
        Write-Host ""
        Write-Host "6. DOWNLOAD AND CREATE" -ForegroundColor Cyan
        Write-Host "   Downloads Windows 11 (approximately 5-6 GB)"
        Write-Host "   Creates bootable USB automatically"
        Write-Host "   Process takes 30-60 minutes"
        Write-Host "   DO NOT remove USB during this process"
        Write-Host ""
        Write-Host "7. COMPLETION" -ForegroundColor Green
        Write-Host "   Shows: 'Your USB flash drive is ready'"
        Write-Host "   D: drive becomes Windows 11 rescue/installation drive"

        Write-Host ""
        Write-Host "CRITICAL WARNINGS:" -ForegroundColor Red
        Write-Host "- ALL DATA ON D: DRIVE WILL BE PERMANENTLY ERASED"
        Write-Host "- Keep computer connected to internet"
        Write-Host "- Do not remove USB or shut down computer"
        Write-Host "- Process cannot be paused or interrupted"

        Write-Host ""
        Write-Host "Ready to launch Media Creation Tool with administrator privileges?" -ForegroundColor Yellow
        Write-Host "Press Y to START, N to cancel: " -ForegroundColor Cyan -NoNewline

        $response = Read-Host

        if ($response -eq 'Y' -or $response -eq 'y') {
            Write-Host ""
            Write-Host "LAUNCHING MEDIA CREATION TOOL..." -ForegroundColor Green

            try {
                Start-Process $toolPath -Verb RunAsAdministrator
                Write-Host "Media Creation Tool launched successfully!" -ForegroundColor Green
                Write-Host ""
                Write-Host "FOLLOW THE STEPS ABOVE IN THE TOOL WINDOW" -ForegroundColor Yellow
                Write-Host ""
                Write-Host "WHEN COMPLETE:" -ForegroundColor Cyan
                Write-Host "1. You'll see 'Your USB flash drive is ready'"
                Write-Host "2. D: drive will contain Windows 11 installation files"
                Write-Host "3. Drive will be bootable for any computer"
                Write-Host "4. Use for emergency recovery or clean Windows installation"
                Write-Host ""
                Write-Host "Return here when process is complete for verification..." -ForegroundColor Green

                Read-Host "Press ENTER when bootable creation is finished"
                Verify-BootableCreation

            } catch {
                Write-Host "ERROR: Failed to launch Media Creation Tool" -ForegroundColor Red
                Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
                Write-Host ""
                Write-Host "TRY MANUAL LAUNCH:" -ForegroundColor Yellow
                Write-Host "1. Navigate to: $toolPath"
                Write-Host "2. Right-click and 'Run as administrator'"
                Write-Host "3. Follow the steps above"
            }
        } else {
            Write-Host "Operation cancelled by user." -ForegroundColor Yellow
        }

    } else {
        Write-Host "ERROR: MediaCreationTool.exe not found at expected location" -ForegroundColor Red
        Write-Host "Expected: $toolPath" -ForegroundColor White
        Write-Host ""
        Write-Host "ALTERNATIVE LOCATIONS TO CHECK:" -ForegroundColor Yellow

        $possiblePaths = @(
            "$env:USERPROFILE\Downloads\MediaCreationTool.exe",
            "$env:USERPROFILE\Downloads\MediaCreationTool11.exe",
            "$env:USERPROFILE\Downloads\Windows11_Tools\MediaCreationTool.exe",
            "$env:USERPROFILE\Downloads\Windows11_Tools\MediaCreationTool11.exe"
        )

        foreach ($path in $possiblePaths) {
            if (Test-Path $path) {
                Write-Host "FOUND: $path" -ForegroundColor Green
                $global:foundTool = $path
                return
            } else {
                Write-Host "NOT FOUND: $path" -ForegroundColor Red
            }
        }

        Write-Host ""
        Write-Host "DOWNLOAD INSTRUCTIONS:" -ForegroundColor Cyan
        Write-Host "1. Go to: https://www.microsoft.com/en-us/software-download/windows11"
        Write-Host "2. Click 'Download Media Creation Tool Now'"
        Write-Host "3. Save to Downloads folder"
        Write-Host "4. Run this script again"
    }
}

function Verify-BootableCreation {
    Write-Host ""
    Write-Host "VERIFYING D: DRIVE BOOTABLE CREATION..." -ForegroundColor Green
    Write-Host "=======================================" -ForegroundColor Green

    # Check D: drive status
    $dDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "D:"}

    if (-not $dDrive) {
        Write-Host "WARNING: Cannot detect D: drive" -ForegroundColor Red
        Write-Host "Drive may have been renamed during process" -ForegroundColor Yellow
        return
    }

    $totalGB = [math]::Round($dDrive.Size/1GB, 2)
    $usedGB = [math]::Round(($dDrive.Size - $dDrive.FreeSpace)/1GB, 2)
    $freeGB = [math]::Round($dDrive.FreeSpace/1GB, 2)

    Write-Host ""
    Write-Host "D: DRIVE STATUS AFTER CREATION:" -ForegroundColor Cyan
    Write-Host "  Drive: $($dDrive.DeviceID)" -ForegroundColor White
    Write-Host "  Label: $($dDrive.VolumeName)" -ForegroundColor White
    Write-Host "  Total: $totalGB GB" -ForegroundColor White
    Write-Host "  Used: $usedGB GB" -ForegroundColor White
    Write-Host "  Free: $freeGB GB" -ForegroundColor White
    Write-Host "  Format: $($dDrive.FileSystem)" -ForegroundColor White

    # Check for Windows 11 files
    $windowsFiles = @(
        "D:\setup.exe",
        "D:\sources\boot.wim",
        "D:\sources\install.wim",
        "D:\bootmgr.efi"
    )

    $foundFiles = 0
    Write-Host ""
    Write-Host "WINDOWS 11 BOOTABLE FILES CHECK:" -ForegroundColor Cyan

    foreach ($file in $windowsFiles) {
        if (Test-Path $file) {
            $fileInfo = Get-Item $file
            $fileSizeMB = [math]::Round($fileInfo.Length/1MB, 1)
            Write-Host "  [OK] $file ($fileSizeMB MB)" -ForegroundColor Green
            $foundFiles++
        } else {
            Write-Host "  [X] $file (missing)" -ForegroundColor Red
        }
    }

    Write-Host ""
    if ($foundFiles -eq $windowsFiles.Count) {
        Write-Host "SUCCESS! WINDOWS 11 BOOTABLE DRIVE CREATED!" -ForegroundColor Green
        Write-Host ""
        Write-Host "D: DRIVE IS NOW READY FOR:" -ForegroundColor Yellow
        Write-Host "  - Emergency Windows 11 installation"
        Write-Host "  - System recovery and repair"
        Write-Host "  - Clean Windows installation on any PC"
        Write-Host "  - Boot problem troubleshooting"

        Write-Host ""
        Write-Host "HOW TO USE YOUR BOOTABLE DRIVE:" -ForegroundColor Green
        Write-Host "1. Insert D: drive into target computer"
        Write-Host "2. Restart the computer"
        Write-Host "3. Press F12 during startup (boot menu)"
        Write-Host "4. Select your USB drive from boot options"
        Write-Host "5. Windows 11 setup will start automatically"

        Write-Host ""
        Write-Host "EQ12 WINDOWS 11 BOOTABLE CREATION COMPLETE!" -ForegroundColor Green

    } else {
        Write-Host "WARNING: Bootable creation appears incomplete" -ForegroundColor Yellow
        Write-Host "Found $foundFiles of $($windowsFiles.Count) essential Windows files" -ForegroundColor Red
        Write-Host ""
        Write-Host "POSSIBLE CAUSES:" -ForegroundColor Cyan
        Write-Host "- Process was interrupted"
        Write-Host "- Download failed"
        Write-Host "- USB drive issues"
        Write-Host "- Insufficient space"
        Write-Host ""
        Write-Host "RECOMMENDATION: Run Media Creation Tool again" -ForegroundColor Yellow
    }
}

# Execute the direct tool
Start-DirectExecution
