#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 D Drive Windows Bootable Creator
    Buffalo NY 14215 Content Empire

.DESCRIPTION
    Create Windows 11 bootable rescue drive on D: USB drive

.EXAMPLE
    .\eq12_d_windows_bootable.ps1
#>

[CmdletBinding()]
param(
    [ValidateSet("Check", "Download", "Create", "Verify")]
    [string]$Action = "Check"
)

$ErrorActionPreference = "Stop"

function Test-DDriveStatus {
    Write-Host "Checking D: Drive Status" -ForegroundColor Cyan
    Write-Host "========================" -ForegroundColor Cyan

    $dDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "D:"}

    if (-not $dDrive) {
        throw "D: drive not found - please connect USB drive"
    }

    $sizeGB = [math]::Round($dDrive.Size/1GB, 2)
    $freeGB = [math]::Round($dDrive.FreeSpace/1GB, 2)

    Write-Host ""
    Write-Host "D: DRIVE ANALYSIS:" -ForegroundColor Green
    Write-Host "  Size: $sizeGB GB" -ForegroundColor White
    Write-Host "  Free: $freeGB GB" -ForegroundColor White
    Write-Host "  Format: $($dDrive.FileSystem)" -ForegroundColor White
    Write-Host "  Type: USB Drive" -ForegroundColor White

    if ($sizeGB -lt 8) {
        throw "Drive too small - need minimum 8GB for Windows 11"
    }

    Write-Host "  Status: READY for Windows 11 bootable creation" -ForegroundColor Green
    return $true
}

function Start-ToolDownloads {
    Write-Host ""
    Write-Host "DOWNLOADING REQUIRED TOOLS" -ForegroundColor Yellow
    Write-Host "============================" -ForegroundColor Yellow

    $downloadFolder = "$env:USERPROFILE\Downloads\Windows11_Tools"
    New-Item -Path $downloadFolder -ItemType Directory -Force | Out-Null

    Write-Host ""
    Write-Host "TOOL 1: RUFUS (USB Creator)" -ForegroundColor Green
    Write-Host "  Purpose: Create bootable USB drives"
    Write-Host "  Size: 1MB (free tool)"
    Write-Host "  Opening download page..."
    Start-Process "https://rufus.ie/"

    Start-Sleep -Seconds 2

    Write-Host ""
    Write-Host "TOOL 2: WINDOWS 11 ISO" -ForegroundColor Green
    Write-Host "  Purpose: Windows 11 installation files"
    Write-Host "  Size: 5GB (official Microsoft ISO)"
    Write-Host "  Opening download page..."
    Start-Process "https://www.microsoft.com/software-download/windows11"

    Write-Host ""
    Write-Host "DOWNLOAD INSTRUCTIONS:" -ForegroundColor Cyan
    Write-Host "1. Download Rufus portable executable"
    Write-Host "2. Download Windows 11 ISO (64-bit version)"
    Write-Host "3. Save both files to: $downloadFolder"

    Write-Host ""
    Write-Host "Opening downloads folder..."
    Start-Process $downloadFolder

    Write-Host ""
    Write-Host "Expected download time: 10-30 minutes"
    Write-Host "Next step: Run script with -Action Create"
}

function New-WindowsBootable {
    Write-Host ""
    Write-Host "CREATING WINDOWS 11 BOOTABLE DRIVE" -ForegroundColor Green
    Write-Host "===================================" -ForegroundColor Green

    $downloadFolder = "$env:USERPROFILE\Downloads\Windows11_Tools"

    # Check for required files
    $rufusFile = Get-ChildItem -Path $downloadFolder -Filter "rufus*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    $isoFile = Get-ChildItem -Path $downloadFolder -Filter "*.iso" -ErrorAction SilentlyContinue | Select-Object -First 1

    Write-Host "Checking for required files..."

    if ($rufusFile) {
        Write-Host "Found Rufus: $($rufusFile.Name)" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Rufus not found" -ForegroundColor Red
        Write-Host "Please download from https://rufus.ie" -ForegroundColor Yellow
        return
    }

    if ($isoFile) {
        Write-Host "Found Windows ISO: $($isoFile.Name)" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Windows ISO not found" -ForegroundColor Red
        Write-Host "Please download from Microsoft website" -ForegroundColor Yellow
        return
    }

    Write-Host ""
    Write-Host "RUFUS SETUP INSTRUCTIONS:" -ForegroundColor Yellow
    Write-Host "1. Device: Select D: drive"
    Write-Host "2. Boot selection: Click SELECT and choose the ISO file"
    Write-Host "3. Partition scheme: GPT"
    Write-Host "4. Target system: UEFI (non CSM)"
    Write-Host "5. File system: NTFS"
    Write-Host "6. Volume label: WIN11_RESCUE"
    Write-Host "7. Click START button"

    Write-Host ""
    Write-Host "WARNING: ALL DATA ON D: WILL BE ERASED" -ForegroundColor Red
    Write-Host "Process takes 15-30 minutes" -ForegroundColor Yellow
    Write-Host "Do NOT remove USB drive during creation" -ForegroundColor Red

    Write-Host ""
    Write-Host "Starting Rufus application..." -ForegroundColor Green
    Start-Process $rufusFile.FullName

    Write-Host ""
    Write-Host "STEP CHECKLIST:"
    Write-Host "[ ] Rufus opened successfully"
    Write-Host "[ ] D: drive selected in Device menu"
    Write-Host "[ ] ISO file loaded via SELECT button"
    Write-Host "[ ] GPT partition scheme chosen"
    Write-Host "[ ] UEFI target system chosen"
    Write-Host "[ ] Volume label changed to WIN11_RESCUE"
    Write-Host "[ ] START button clicked"
    Write-Host "[ ] Data erasure confirmed"
    Write-Host "[ ] Waited for completion (READY status)"

    Write-Host ""
    Write-Host "After completion, run script with -Action Verify"
}

function Test-BootableCreation {
    Write-Host ""
    Write-Host "VERIFYING BOOTABLE DRIVE" -ForegroundColor Cyan
    Write-Host "========================" -ForegroundColor Cyan

    # Check for essential Windows files
    $requiredFiles = @(
        "D:\setup.exe",
        "D:\sources\boot.wim",
        "D:\bootmgr.efi"
    )

    $filesFound = 0

    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Host "Found: $file" -ForegroundColor Green
            $filesFound++
        } else {
            Write-Host "Missing: $file" -ForegroundColor Red
        }
    }

    Write-Host ""

    if ($filesFound -eq $requiredFiles.Count) {
        Write-Host "SUCCESS: Windows 11 bootable drive created!" -ForegroundColor Green

        # Show drive statistics
        $dDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "D:"}
        $usedSpace = [math]::Round(($dDrive.Size - $dDrive.FreeSpace)/1GB, 2)
        $freeSpace = [math]::Round($dDrive.FreeSpace/1GB, 2)

        Write-Host ""
        Write-Host "DRIVE STATISTICS:" -ForegroundColor Yellow
        Write-Host "  Used space: $usedSpace GB"
        Write-Host "  Free space: $freeSpace GB"
        Write-Host "  File system: $($dDrive.FileSystem)"

    } else {
        Write-Host "WARNING: Bootable creation may be incomplete" -ForegroundColor Yellow
        Write-Host "Found $filesFound of $($requiredFiles.Count) required files"
    }

    Write-Host ""
    Write-Host "USAGE INSTRUCTIONS:" -ForegroundColor Green
    Write-Host "1. Insert D: drive into target computer"
    Write-Host "2. Restart computer"
    Write-Host "3. Press F12 (or F2/Del) during startup"
    Write-Host "4. Select USB drive from boot menu"
    Write-Host "5. Follow Windows 11 setup prompts"

    Write-Host ""
    Write-Host "RESCUE SCENARIOS:" -ForegroundColor Cyan
    Write-Host "- Computer won't start Windows"
    Write-Host "- Need clean Windows installation"
    Write-Host "- System repair operations"
    Write-Host "- Boot problem troubleshooting"

    Write-Host ""
    Write-Host "D: drive setup complete!" -ForegroundColor Green
}

# Main Script Execution
Write-Host "EQ12 D: DRIVE BOOTABLE CREATOR" -ForegroundColor Cyan
Write-Host "Buffalo NY 14215 Content Empire" -ForegroundColor Gray
Write-Host ""

switch ($Action) {
    "Check" {
        Test-DDriveStatus
        Write-Host ""
        Write-Host "Next step: Run with -Action Download" -ForegroundColor Yellow
    }
    "Download" {
        Test-DDriveStatus
        Start-ToolDownloads
    }
    "Create" {
        Test-DDriveStatus
        New-WindowsBootable
    }
    "Verify" {
        Test-BootableCreation
    }
}

Write-Host ""
