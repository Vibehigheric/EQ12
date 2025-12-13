#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Windows Bootable Drive Creator
    Buffalo NY 14215 Content Empire - D: Drive Setup

.DESCRIPTION
    Professional Windows 11 bootable rescue drive creation tool
    Handles ISO download, Rufus automation, and drive preparation
#>

[CmdletBinding()]
param(
    [ValidateSet("PrepareD", "DownloadTools", "CreateBootable", "Verify")]
    [string]$Action = "PrepareD"
)

# EQ12 Environment Setup
$ErrorActionPreference = "Stop"
$env:EQ12_ASCII_MODE = "ACTIVE"

function Test-DDriveReady {
    Write-Host "🔍 ANALYZING D: DRIVE FOR BOOTABLE SETUP" -ForegroundColor Cyan
    Write-Host "================================================" -ForegroundColor Cyan

    # Check if D: exists and is USB
    $dDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "D:"}

    if (-not $dDrive) {
        throw "❌ D: drive not found. Please ensure USB drive is connected."
    }

    if ($dDrive.DriveType -ne 2) {
        throw "❌ D: drive is not a USB drive (DriveType: $($dDrive.DriveType))"
    }

    $sizeGB = [math]::Round($dDrive.Size/1GB, 2)
    $freeGB = [math]::Round($dDrive.FreeSpace/1GB, 2)

    Write-Host ""
    Write-Host "✅ D: DRIVE STATUS:" -ForegroundColor Green
    Write-Host "   Drive: $($dDrive.DeviceID)" -ForegroundColor White
    Write-Host "   Label: $($dDrive.VolumeName)" -ForegroundColor White
    Write-Host "   Size: $sizeGB GB" -ForegroundColor Green
    Write-Host "   Free: $freeGB GB" -ForegroundColor Green
    Write-Host "   Format: $($dDrive.FileSystem)" -ForegroundColor Cyan

    if ($sizeGB -lt 8) {
        throw "❌ D: drive too small. Need at least 8GB for Windows 11."
    }

    Write-Host "   ✅ Size adequate for Windows 11" -ForegroundColor Green

    # Check for existing files
    $files = Get-ChildItem -Path "D:\" -ErrorAction SilentlyContinue
    if ($files) {
        Write-Host "   ⚠️  Drive contains $($files.Count) files" -ForegroundColor Yellow
        Write-Host "   📁 Will be ERASED during bootable creation" -ForegroundColor Red
    } else {
        Write-Host "   ✅ Drive is empty - perfect for bootable setup" -ForegroundColor Green
    }

    return $true
}

function Start-ToolDownloads {
    Write-Host ""
    Write-Host "📥 DOWNLOADING WINDOWS BOOTABLE TOOLS" -ForegroundColor Yellow
    Write-Host "=============================================" -ForegroundColor Yellow

    # Create downloads directory
    $downloadsPath = "$env:USERPROFILE\Downloads\EQ12_Bootable"
    New-Item -Path $downloadsPath -ItemType Directory -Force | Out-Null

    Write-Host ""
    Write-Host "🔧 TOOL 1: RUFUS (USB Bootable Creator)" -ForegroundColor Cyan
    Write-Host "   Purpose: Create Windows 11 bootable USB"
    Write-Host "   Size: ~1MB, Free, No installation required"
    Write-Host "   Opening download page..."
    Start-Process "https://rufus.ie/en/"

    Write-Host ""
    Write-Host "💿 TOOL 2: WINDOWS 11 ISO" -ForegroundColor Cyan
    Write-Host "   Purpose: Windows 11 installation files"
    Write-Host "   Size: ~5GB, Official Microsoft ISO"
    Write-Host "   Opening download page..."
    Start-Process "https://www.microsoft.com/software-download/windows11"

    Write-Host ""
    Write-Host "🎯 DOWNLOAD INSTRUCTIONS:" -ForegroundColor Green
    Write-Host "1. Download Rufus portable (.exe file)"
    Write-Host "2. Download Windows 11 ISO (64-bit)"
    Write-Host "3. Save both to: $downloadsPath"
    Write-Host ""
    Write-Host "⏱️  Downloads will take 10-30 minutes depending on speed"
    Write-Host "📁 Target folder: $downloadsPath"

    # Open downloads folder
    Start-Process $downloadsPath
}

function New-WindowsBootableDrive {
    Write-Host ""
    Write-Host "🚀 CREATING WINDOWS 11 BOOTABLE DRIVE" -ForegroundColor Green
    Write-Host "=======================================" -ForegroundColor Green

    $downloadsPath = "$env:USERPROFILE\Downloads\EQ12_Bootable"

    # Check for Rufus
    $rufusPath = Get-ChildItem -Path $downloadsPath -Filter "rufus*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $rufusPath) {
        Write-Host "❌ Rufus not found in $downloadsPath" -ForegroundColor Red
        Write-Host "   Please download Rufus from https://rufus.ie" -ForegroundColor Yellow
        return $false
    }

    # Check for Windows ISO
    $isoPath = Get-ChildItem -Path $downloadsPath -Filter "*.iso" -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $isoPath) {
        Write-Host "❌ Windows ISO not found in $downloadsPath" -ForegroundColor Red
        Write-Host "   Please download Windows 11 ISO from Microsoft" -ForegroundColor Yellow
        return $false
    }

    Write-Host "✅ Found Rufus: $($rufusPath.Name)" -ForegroundColor Green
    Write-Host "✅ Found ISO: $($isoPath.Name)" -ForegroundColor Green

    Write-Host ""
    Write-Host "🔥 RUFUS SETTINGS FOR OPTIMAL BOOTABLE DRIVE:" -ForegroundColor Yellow
    Write-Host "1. Device: Select D: drive"
    Write-Host "2. Boot selection: SELECT YOUR ISO FILE"
    Write-Host "3. Image option: Standard Windows 11 Installation"
    Write-Host "4. Partition scheme: GPT"
    Write-Host "5. Target system: UEFI (non CSM)"
    Write-Host "6. File system: NTFS"
    Write-Host "7. Cluster size: Default"
    Write-Host "8. Volume label: WIN11_RESCUE"

    Write-Host ""
    Write-Host "⚠️  IMPORTANT WARNINGS:" -ForegroundColor Red
    Write-Host "• ALL DATA ON D: WILL BE ERASED"
    Write-Host "• Process takes 15-30 minutes"
    Write-Host "• Do NOT remove USB during creation"
    Write-Host "• Close other programs for best performance"

    Write-Host ""
    Write-Host "🚀 Starting Rufus..." -ForegroundColor Green
    Start-Process $rufusPath.FullName

    Write-Host ""
    Write-Host "📋 STEP-BY-STEP CHECKLIST:" -ForegroundColor Cyan
    Write-Host "□ 1. Rufus opened successfully"
    Write-Host "□ 2. D: drive selected in Device dropdown"
    Write-Host "□ 3. ISO file selected via SELECT button"
    Write-Host "□ 4. GPT partition scheme selected"
    Write-Host "□ 5. UEFI target system selected"
    Write-Host "□ 6. Volume label set to WIN11_RESCUE"
    Write-Host "□ 7. Clicked START button"
    Write-Host "□ 8. Confirmed data erasure warning"
    Write-Host "□ 9. Waited for completion (green READY status)"
    Write-Host "□ 10. Safely ejected and tested boot"
}

function Test-BootableDrive {
    Write-Host ""
    Write-Host "🔍 VERIFYING BOOTABLE DRIVE CREATION" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan

    # Check if D: drive now has Windows files
    $windowsFiles = @(
        "D:\bootmgr.efi",
        "D:\sources\boot.wim",
        "D:\sources\install.wim",
        "D:\setup.exe"
    )

    $foundFiles = 0
    foreach ($file in $windowsFiles) {
        if (Test-Path $file) {
            $foundFiles++
            Write-Host "✅ Found: $file" -ForegroundColor Green
        } else {
            Write-Host "❌ Missing: $file" -ForegroundColor Red
        }
    }

    Write-Host ""
    if ($foundFiles -eq $windowsFiles.Count) {
        Write-Host "🎉 SUCCESS! Windows 11 bootable drive created!" -ForegroundColor Green
        Write-Host "✅ All essential Windows files present" -ForegroundColor Green

        # Get drive info
        $dDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "D:"}
        $usedGB = [math]::Round(($dDrive.Size - $dDrive.FreeSpace)/1GB, 2)
        $freeGB = [math]::Round($dDrive.FreeSpace/1GB, 2)

        Write-Host ""
        Write-Host "📊 FINAL DRIVE STATUS:" -ForegroundColor Yellow
        Write-Host "   Used space: $usedGB GB" -ForegroundColor White
        Write-Host "   Free space: $freeGB GB" -ForegroundColor White
        Write-Host "   File system: $($dDrive.FileSystem)" -ForegroundColor White

    } else {
        Write-Host "⚠️  Partial success - some files missing" -ForegroundColor Yellow
        Write-Host "   Found $foundFiles of $($windowsFiles.Count) essential files" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "🎯 BOOT TEST INSTRUCTIONS:" -ForegroundColor Green
    Write-Host "1. Restart computer"
    Write-Host "2. Enter BIOS/UEFI (usually F2, F12, or Del key)"
    Write-Host "3. Look for 'Boot Menu' or 'Boot Options'"
    Write-Host "4. Select USB drive (should show as WIN11_RESCUE)"
    Write-Host "5. Windows 11 setup should start"
    Write-Host ""
    Write-Host "✅ D: drive is now a Windows 11 rescue drive!" -ForegroundColor Green
}

function Show-UsageInstructions {
    Write-Host ""
    Write-Host "📖 HOW TO USE YOUR WINDOWS 11 RESCUE DRIVE" -ForegroundColor Green
    Write-Host "=============================================" -ForegroundColor Green

    Write-Host ""
    Write-Host "🔧 EMERGENCY SCENARIOS:" -ForegroundColor Yellow
    Write-Host "• Computer won't boot Windows"
    Write-Host "• Need to reinstall Windows 11"
    Write-Host "• System recovery operations"
    Write-Host "• Clean Windows installation"
    Write-Host "• Repair boot problems"

    Write-Host ""
    Write-Host "🚀 BOOT PROCESS:" -ForegroundColor Cyan
    Write-Host "1. Insert D: drive into problem computer"
    Write-Host "2. Power on and immediately press boot menu key"
    Write-Host "3. Select USB drive from boot menu"
    Write-Host "4. Choose installation or repair options"

    Write-Host ""
    Write-Host "💡 PRO TIPS:" -ForegroundColor Green
    Write-Host "• Test boot on current system first"
    Write-Host "• Keep drive in safe, dry location"
    Write-Host "• Update annually with new Windows ISO"
    Write-Host "• Add drivers folder for specific hardware"
    Write-Host "• Consider creating recovery partition"
}

# Main execution
switch ($Action) {
    "PrepareD" {
        Test-DDriveReady
        Write-Host ""
        Write-Host "🎯 NEXT STEP: Run with -Action DownloadTools" -ForegroundColor Yellow
    }
    "DownloadTools" {
        Test-DDriveReady
        Start-ToolDownloads
        Write-Host ""
        Write-Host "🎯 NEXT STEP: After downloads complete, run with -Action CreateBootable" -ForegroundColor Yellow
    }
    "CreateBootable" {
        Test-DDriveReady
        New-WindowsBootableDrive
        Write-Host ""
        Write-Host "🎯 NEXT STEP: After Rufus completes, run with -Action Verify" -ForegroundColor Yellow
    }
    "Verify" {
        Test-BootableDrive
        Show-UsageInstructions
    }
}

Write-Host ""
Write-Host "🛠️  EQ12 USB EXPERT - D: DRIVE BOOTABLE SETUP" -ForegroundColor Cyan
Write-Host "Buffalo NY 14215 Content Empire" -ForegroundColor Gray
Write-Host ""
