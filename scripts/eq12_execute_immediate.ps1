#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 EXECUTE D: DRIVE BOOTABLE - IMMEDIATE ACTION
    Buffalo NY 14215 Content Empire

.DESCRIPTION
    Immediate execution and monitoring for Windows 11 D: drive bootable creation
#>

function Start-ExecuteMonitor {
    Clear-Host
    Write-Host "EQ12 EXECUTE - D: DRIVE BOOTABLE CREATION" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "Buffalo NY 14215 Content Empire" -ForegroundColor Gray
    Write-Host ""

    $downloadPath = "$env:USERPROFILE\Downloads\Windows11_Tools"

    Write-Host "IMMEDIATE ACTION REQUIRED:" -ForegroundColor Red
    Write-Host ""
    Write-Host "STEP 1: DOWNLOAD MEDIA CREATION TOOL" -ForegroundColor Yellow
    Write-Host "Browser should have opened to Microsoft download page"
    Write-Host "If not, manually go to: https://go.microsoft.com/fwlink/?linkid=2156295"
    Write-Host ""
    Write-Host "ON THE MICROSOFT PAGE:" -ForegroundColor Cyan
    Write-Host "1. Click the blue 'Download Media Creation Tool Now' button"
    Write-Host "2. Save the file as: MediaCreationTool11.exe"
    Write-Host "3. Save location: $downloadPath"
    Write-Host "4. File downloads in 30-60 seconds (~20MB)"

    Write-Host ""
    Write-Host "MONITORING DOWNLOAD..." -ForegroundColor Yellow

    $maxWait = 300  # 5 minutes max wait
    $waited = 0
    $interval = 5

    while ($waited -lt $maxWait) {
        # Check for any Media Creation Tool file
        $toolFiles = Get-ChildItem -Path $downloadPath -Filter "*MediaCreation*.exe" -ErrorAction SilentlyContinue

        if ($toolFiles) {
            $toolFile = $toolFiles[0]
            $sizeKB = [math]::Round($toolFile.Length/1KB, 0)
            Write-Host "FOUND: $($toolFile.Name) ($sizeKB KB)" -ForegroundColor Green

            if ($toolFile.Length -gt 1MB) {
                Write-Host "Download complete! File size looks good." -ForegroundColor Green
                Start-MediaCreationTool $toolFile.FullName
                return
            }
        }

        Write-Host "Waiting for download... ($waited seconds)" -ForegroundColor Yellow
        Start-Sleep $interval
        $waited += $interval

        # Show current folder contents
        $allFiles = Get-ChildItem -Path $downloadPath -ErrorAction SilentlyContinue
        if ($allFiles) {
            Write-Host "Current files in folder: $($allFiles.Count)" -ForegroundColor Cyan
        }
    }

    Write-Host ""
    Write-Host "Download timeout reached. Starting manual check..." -ForegroundColor Yellow
    Start-ManualCheck
}

function Start-ManualCheck {
    $downloadPath = "$env:USERPROFILE\Downloads\Windows11_Tools"

    Write-Host ""
    Write-Host "MANUAL VERIFICATION:" -ForegroundColor Cyan
    Write-Host "Check if MediaCreationTool11.exe was downloaded to:"
    Write-Host "$downloadPath" -ForegroundColor White

    # List current files
    $files = Get-ChildItem -Path $downloadPath -ErrorAction SilentlyContinue
    if ($files) {
        Write-Host ""
        Write-Host "Files in download folder:" -ForegroundColor Yellow
        foreach ($file in $files) {
            $sizeKB = [math]::Round($file.Length/1KB, 0)
            Write-Host "  $($file.Name) ($sizeKB KB)" -ForegroundColor White
        }
    }

    Write-Host ""
    Write-Host "If you downloaded the file:" -ForegroundColor Green
    Write-Host "1. Press 1 and ENTER to launch it"
    Write-Host "2. Press 2 and ENTER to check again"
    Write-Host "3. Press 3 and ENTER to open download page again"

    $choice = Read-Host "Enter choice (1/2/3)"

    switch ($choice) {
        "1" {
            $toolFiles = Get-ChildItem -Path $downloadPath -Filter "*MediaCreation*.exe" -ErrorAction SilentlyContinue
            if ($toolFiles) {
                Start-MediaCreationTool $toolFiles[0].FullName
            } else {
                Write-Host "No Media Creation Tool found. Please download it first." -ForegroundColor Red
            }
        }
        "2" {
            Start-ManualCheck
        }
        "3" {
            Start-Process "https://go.microsoft.com/fwlink/?linkid=2156295"
            Start-ManualCheck
        }
        default {
            Write-Host "Invalid choice. Please try again." -ForegroundColor Red
            Start-ManualCheck
        }
    }
}

function Start-MediaCreationTool {
    param([string]$toolPath)

    Write-Host ""
    Write-Host "LAUNCHING MEDIA CREATION TOOL" -ForegroundColor Green
    Write-Host "==============================" -ForegroundColor Green

    Write-Host ""
    Write-Host "D: DRIVE BOOTABLE CREATION STEPS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. ACCEPT LICENSE" -ForegroundColor Cyan
    Write-Host "   Click 'Accept' on the license terms"
    Write-Host ""
    Write-Host "2. CHOOSE ACTION" -ForegroundColor Cyan
    Write-Host "   Select: 'Create installation media (USB flash drive, DVD, or ISO file)'"
    Write-Host "   Click 'Next'"
    Write-Host ""
    Write-Host "3. SELECT OPTIONS" -ForegroundColor Cyan
    Write-Host "   Language: English (United States)"
    Write-Host "   Edition: Windows 11"
    Write-Host "   Architecture: 64-bit (x64)"
    Write-Host "   Click 'Next'"
    Write-Host ""
    Write-Host "4. CHOOSE MEDIA" -ForegroundColor Cyan
    Write-Host "   Select: 'USB flash drive'"
    Write-Host "   Click 'Next'"
    Write-Host ""
    Write-Host "5. SELECT D: DRIVE" -ForegroundColor Cyan
    Write-Host "   Choose: D: drive from the list" -ForegroundColor Green
    Write-Host "   VERIFY it shows your USB drive" -ForegroundColor Red
    Write-Host "   Click 'Next'"
    Write-Host ""
    Write-Host "6. WAIT FOR COMPLETION" -ForegroundColor Cyan
    Write-Host "   Downloads Windows 11 (~5GB)"
    Write-Host "   Creates bootable USB"
    Write-Host "   Takes 30-60 minutes total"
    Write-Host "   Shows 'Your USB flash drive is ready' when done"

    Write-Host ""
    Write-Host "CRITICAL REMINDERS:" -ForegroundColor Red
    Write-Host "- ALL DATA ON D: DRIVE WILL BE ERASED"
    Write-Host "- DO NOT remove USB during process"
    Write-Host "- Keep computer running and connected to internet"

    Write-Host ""
    Write-Host "Starting tool with administrator privileges..." -ForegroundColor Green

    try {
        Start-Process $toolPath -Verb RunAsAdministrator
        Write-Host "Media Creation Tool launched successfully!" -ForegroundColor Green

        Write-Host ""
        Write-Host "PROCESS MONITORING:" -ForegroundColor Yellow
        Write-Host "The tool is now running. Follow the steps above."
        Write-Host "Come back here when you see 'Your USB flash drive is ready'"
        Write-Host ""
        Write-Host "Press ENTER when the bootable creation is complete..." -ForegroundColor Cyan
        Read-Host

        Test-FinalResult

    } catch {
        Write-Host "Error launching Media Creation Tool: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Try running as administrator manually from: $toolPath" -ForegroundColor Yellow
    }
}

function Test-FinalResult {
    Write-Host ""
    Write-Host "FINAL VERIFICATION - D: DRIVE BOOTABLE" -ForegroundColor Green
    Write-Host "=======================================" -ForegroundColor Green

    # Check D: drive
    $dDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "D:"}

    if (-not $dDrive) {
        Write-Host "ERROR: Cannot access D: drive" -ForegroundColor Red
        Write-Host "USB may have been disconnected or renamed" -ForegroundColor Yellow
        return
    }

    $totalGB = [math]::Round($dDrive.Size/1GB, 2)
    $usedGB = [math]::Round(($dDrive.Size - $dDrive.FreeSpace)/1GB, 2)
    $freeGB = [math]::Round($dDrive.FreeSpace/1GB, 2)

    Write-Host ""
    Write-Host "D: DRIVE FINAL STATUS:" -ForegroundColor Cyan
    Write-Host "  Drive: $($dDrive.DeviceID)" -ForegroundColor White
    Write-Host "  Label: $($dDrive.VolumeName)" -ForegroundColor White
    Write-Host "  Total: $totalGB GB" -ForegroundColor White
    Write-Host "  Used: $usedGB GB" -ForegroundColor White
    Write-Host "  Free: $freeGB GB" -ForegroundColor White
    Write-Host "  Format: $($dDrive.FileSystem)" -ForegroundColor White

    # Check essential Windows files
    $criticalFiles = @(
        "D:\setup.exe",
        "D:\sources\boot.wim",
        "D:\sources\install.wim",
        "D:\bootmgr.efi"
    )

    $foundFiles = 0
    Write-Host ""
    Write-Host "WINDOWS 11 BOOTABLE FILES:" -ForegroundColor Cyan

    foreach ($file in $criticalFiles) {
        if (Test-Path $file) {
            $fileInfo = Get-Item $file
            $fileSizeMB = [math]::Round($fileInfo.Length/1MB, 1)
            Write-Host "  FOUND: $file ($fileSizeMB MB)" -ForegroundColor Green
            $foundFiles++
        } else {
            Write-Host "  MISSING: $file" -ForegroundColor Red
        }
    }

    Write-Host ""
    if ($foundFiles -eq $criticalFiles.Count) {
        Write-Host "SUCCESS! D: DRIVE BOOTABLE CREATION COMPLETE!" -ForegroundColor Green
        Write-Host ""
        Write-Host "WINDOWS 11 RESCUE DRIVE READY:" -ForegroundColor Yellow
        Write-Host "  Emergency Windows 11 installation" -ForegroundColor White
        Write-Host "  System recovery and repair" -ForegroundColor White
        Write-Host "  Clean Windows installation" -ForegroundColor White
        Write-Host "  Boot problem resolution" -ForegroundColor White

        Write-Host ""
        Write-Host "HOW TO USE YOUR BOOTABLE DRIVE:" -ForegroundColor Green
        Write-Host "1. Insert D: drive into any computer" -ForegroundColor White
        Write-Host "2. Restart computer" -ForegroundColor White
        Write-Host "3. Press F12 during startup (boot menu)" -ForegroundColor White
        Write-Host "4. Select your USB drive from the list" -ForegroundColor White
        Write-Host "5. Windows 11 setup will start automatically" -ForegroundColor White

        Write-Host ""
        Write-Host "EXECUTION COMPLETE!" -ForegroundColor Green
        Write-Host "D: drive is now a professional Windows 11 rescue drive" -ForegroundColor Cyan

    } else {
        Write-Host "WARNING: Bootable creation may be incomplete" -ForegroundColor Yellow
        Write-Host "Found $foundFiles of $($criticalFiles.Count) essential files" -ForegroundColor Red
        Write-Host ""
        Write-Host "POSSIBLE ISSUES:" -ForegroundColor Cyan
        Write-Host "- Media Creation Tool didn't complete successfully"
        Write-Host "- Process was interrupted"
        Write-Host "- USB drive has issues"
        Write-Host "- Try running the Media Creation Tool again"
    }

    Write-Host ""
    Write-Host "EQ12 D: DRIVE BOOTABLE EXECUTION COMPLETE" -ForegroundColor Green
    Write-Host "Buffalo NY 14215 Content Empire" -ForegroundColor Gray
}

# Start the execution monitor
Start-ExecuteMonitor

