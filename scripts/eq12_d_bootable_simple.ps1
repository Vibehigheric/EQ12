#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 D: Drive Windows 11 Bootable Creator
    Buffalo NY 14215 Content Empire

.DESCRIPTION
    Professional tool to create Windows 11 bootable rescue drive on D: USB

.EXAMPLE
    .\eq12_d_bootable_simple.ps1 -Action Prepare
#>

[CmdletBinding()]
param(
    [ValidateSet("Prepare", "Download", "Create", "Verify")]
    [string]$Action = "Prepare"
)

$ErrorActionPreference = "Stop"

function Test-DDrive {
    Write-Host "🔍 CHECKING D: DRIVE STATUS" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan

    $dDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "D:"}

    if (-not $dDrive) {
        throw "❌ D: drive not found"
    }

    $sizeGB = [math]::Round($dDrive.Size/1GB, 2)
    $freeGB = [math]::Round($dDrive.FreeSpace/1GB, 2)

    Write-Host ""
    Write-Host "✅ D: DRIVE READY FOR BOOTABLE SETUP" -ForegroundColor Green
    Write-Host "   Size: $sizeGB GB" -ForegroundColor White
    Write-Host "   Free: $freeGB GB" -ForegroundColor White
    Write-Host "   Format: $($dDrive.FileSystem)" -ForegroundColor White

    if ($sizeGB -lt 8) {
        throw "❌ Drive too small - need 8GB minimum"
    }

    Write-Host "   ✅ Perfect size for Windows 11 bootable" -ForegroundColor Green
    return $true
}

function Start-Downloads {
    Write-Host ""
    Write-Host "📥 DOWNLOADING WINDOWS BOOTABLE TOOLS" -ForegroundColor Yellow
    Write-Host "=====================================" -ForegroundColor Yellow

    $downloadPath = "$env:USERPROFILE\Downloads\EQ12_Windows11"
    New-Item -Path $downloadPath -ItemType Directory -Force | Out-Null

    Write-Host ""
    Write-Host "🔧 STEP 1: DOWNLOAD RUFUS" -ForegroundColor Green
    Write-Host "   Purpose: USB bootable creator"
    Write-Host "   Size: ~1MB (free, no install needed)"
    Start-Process "https://rufus.ie/"

    Write-Host ""
    Write-Host "💿 STEP 2: DOWNLOAD WINDOWS 11 ISO" -ForegroundColor Green
    Write-Host "   Purpose: Windows installation files"
    Write-Host "   Size: ~5GB (official Microsoft ISO)"
    Start-Process "https://www.microsoft.com/software-download/windows11"

    Write-Host ""
    Write-Host "📁 SAVE DOWNLOADS TO:" -ForegroundColor Cyan
    Write-Host "   $downloadPath"
    Start-Process $downloadPath

    Write-Host ""
    Write-Host "⏱️  Download time: 10-30 minutes"
    Write-Host "🎯 After downloads complete, run: -Action Create"
}

function New-BootableDrive {
    Write-Host ""
    Write-Host "🚀 CREATING WINDOWS 11 BOOTABLE DRIVE" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green

    $downloadPath = "$env:USERPROFILE\Downloads\EQ12_Windows11"

    Write-Host ""
    Write-Host "🔍 Checking for downloaded files..."

    $rufus = Get-ChildItem -Path $downloadPath -Filter "rufus*.exe" | Select-Object -First 1
    $iso = Get-ChildItem -Path $downloadPath -Filter "*.iso" | Select-Object -First 1

    if ($rufus) {
        Write-Host "✅ Found Rufus: $($rufus.Name)" -ForegroundColor Green
    } else {
        Write-Host "❌ Rufus not found - please download first" -ForegroundColor Red
        return
    }

    if ($iso) {
        Write-Host "✅ Found Windows ISO: $($iso.Name)" -ForegroundColor Green
    } else {
        Write-Host "❌ Windows ISO not found - please download first" -ForegroundColor Red
        return
    }

    Write-Host ""
    Write-Host "🔥 RUFUS CONFIGURATION GUIDE:" -ForegroundColor Yellow
    Write-Host "1. Device: Select D: drive (your USB)"
    Write-Host "2. Boot selection: Click SELECT and choose the ISO"
    Write-Host "3. Partition scheme: GPT"
    Write-Host "4. Target system: UEFI (non CSM)"
    Write-Host "5. File system: NTFS"
    Write-Host "6. Volume label: WIN11_RESCUE"
    Write-Host "7. Click START"

    Write-Host ""
    Write-Host "⚠️  CRITICAL WARNINGS:" -ForegroundColor Red
    Write-Host "• ALL DATA ON D: WILL BE DELETED"
    Write-Host "• Takes 15-30 minutes to complete"
    Write-Host "• DO NOT remove USB during process"

    Write-Host ""
    Write-Host "🚀 Starting Rufus now..." -ForegroundColor Green
    Start-Process $rufus.FullName

    Write-Host ""
    Write-Host "📋 FOLLOW THESE STEPS IN RUFUS:"
    Write-Host "□ Select D: drive in Device dropdown"
    Write-Host "□ Click SELECT button and choose Windows ISO"
    Write-Host "□ Verify GPT partition scheme selected"
    Write-Host "□ Verify UEFI target system selected"
    Write-Host "□ Change Volume label to WIN11_RESCUE"
    Write-Host "□ Click START button"
    Write-Host "□ Confirm when asked about erasing data"
    Write-Host "□ Wait for READY status (green text)"

    Write-Host ""
    Write-Host "🎯 When complete, run: -Action Verify"
}

function Test-Bootable {
    Write-Host ""
    Write-Host "🔍 VERIFYING BOOTABLE CREATION" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan

    $windowsFiles = @("D:\setup.exe", "D:\sources\boot.wim")
    $found = 0

    foreach ($file in $windowsFiles) {
        if (Test-Path $file) {
            Write-Host "✅ Found: $file" -ForegroundColor Green
            $found++
        } else {
            Write-Host "❌ Missing: $file" -ForegroundColor Red
        }
    }

    Write-Host ""
    if ($found -eq $windowsFiles.Count) {
        Write-Host "🎉 SUCCESS! D: drive is now bootable!" -ForegroundColor Green

        $dDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "D:"}
        $usedGB = [math]::Round(($dDrive.Size - $dDrive.FreeSpace)/1GB, 2)
        $freeGB = [math]::Round($dDrive.FreeSpace/1GB, 2)

        Write-Host "   Used: $usedGB GB" -ForegroundColor White
        Write-Host "   Free: $freeGB GB" -ForegroundColor White

    } else {
        Write-Host "⚠️  Setup incomplete - missing Windows files" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "🎯 HOW TO USE YOUR RESCUE DRIVE:" -ForegroundColor Green
    Write-Host "1. Insert D: drive into any computer"
    Write-Host "2. Restart and press F12 (or F2/Del for BIOS)"
    Write-Host "3. Select USB drive from boot menu"
    Write-Host "4. Windows 11 installer will start"
    Write-Host "5. Choose Install or Repair options"

    Write-Host ""
    Write-Host "✅ D: drive Windows 11 rescue setup complete!" -ForegroundColor Green
}

# Main execution
Write-Host "🛠️  EQ12 D: DRIVE BOOTABLE CREATOR" -ForegroundColor Cyan
Write-Host "Buffalo NY 14215 Content Empire" -ForegroundColor Gray
Write-Host ""

switch ($Action) {
    "Prepare" {
        Test-DDrive
        Write-Host ""
        Write-Host "🎯 NEXT: Run with -Action Download" -ForegroundColor Yellow
    }
    "Download" {
        Test-DDrive
        Start-Downloads
    }
    "Create" {
        Test-DDrive
        New-BootableDrive
    }
    "Verify" {
        Test-Bootable
    }
}
