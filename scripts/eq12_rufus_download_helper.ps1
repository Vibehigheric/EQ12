#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Rufus Download Assistant
    Buffalo NY 14215 Content Empire - D: Drive Bootable Helper

.DESCRIPTION
    Guide user through Rufus download and Windows 11 ISO acquisition
#>

function Get-RufusDownloadGuide {
    Write-Host "RUFUS DOWNLOAD GUIDE" -ForegroundColor Cyan
    Write-Host "====================" -ForegroundColor Cyan

    $downloadPath = "$env:USERPROFILE\Downloads\Windows11_Tools"

    Write-Host ""
    Write-Host "You're at https://rufus.ie/downloads/" -ForegroundColor Green
    Write-Host ""
    Write-Host "DOWNLOAD THE CORRECT VERSION:" -ForegroundColor Yellow
    Write-Host "1. Look for 'Rufus 4.x' section (latest version)" -ForegroundColor White
    Write-Host "2. Click on 'Rufus 4.x (1 MB)' - the PORTABLE version" -ForegroundColor Green
    Write-Host "3. Do NOT download the installer version" -ForegroundColor Red
    Write-Host "4. Save as: rufus.exe" -ForegroundColor White

    Write-Host ""
    Write-Host "SAVE LOCATION:" -ForegroundColor Cyan
    Write-Host "$downloadPath" -ForegroundColor White

    Write-Host ""
    Write-Host "WHY RUFUS PORTABLE?" -ForegroundColor Yellow
    Write-Host "• No installation required" -ForegroundColor Green
    Write-Host "• Runs directly from download" -ForegroundColor Green
    Write-Host "• Clean and simple" -ForegroundColor Green
    Write-Host "• Trusted by IT professionals worldwide" -ForegroundColor Green

    Write-Host ""
    Write-Host "AFTER RUFUS DOWNLOAD:" -ForegroundColor Cyan
    Write-Host "1. Download Windows 11 ISO from Microsoft" -ForegroundColor White
    Write-Host "2. Both files should be in Windows11_Tools folder" -ForegroundColor White
    Write-Host "3. Run: .\eq12_d_windows_bootable.ps1 -Action Create" -ForegroundColor Green
}

function Get-Windows11DownloadGuide {
    Write-Host ""
    Write-Host "WINDOWS 11 ISO DOWNLOAD GUIDE" -ForegroundColor Cyan
    Write-Host "=============================" -ForegroundColor Cyan

    Write-Host ""
    Write-Host "STEP 1: Visit Microsoft's official page" -ForegroundColor Yellow
    Write-Host "https://www.microsoft.com/software-download/windows11" -ForegroundColor White

    Write-Host ""
    Write-Host "STEP 2: Select download option" -ForegroundColor Yellow
    Write-Host "• Scroll to 'Download Windows 11 Disk Image (ISO)'" -ForegroundColor White
    Write-Host "• Select 'Windows 11 (multi-edition ISO)'" -ForegroundColor Green
    Write-Host "• Click 'Download'" -ForegroundColor White

    Write-Host ""
    Write-Host "STEP 3: Choose language and edition" -ForegroundColor Yellow
    Write-Host "• Language: English (or your preference)" -ForegroundColor White
    Write-Host "• Edition: 64-bit Download" -ForegroundColor Green
    Write-Host "• File size: ~5GB" -ForegroundColor White

    Write-Host ""
    Write-Host "STEP 4: Save location" -ForegroundColor Yellow
    $downloadPath = "$env:USERPROFILE\Downloads\Windows11_Tools"
    Write-Host "$downloadPath" -ForegroundColor White
    Write-Host "• File name: Keep default (Win11_*.iso)" -ForegroundColor White

    Write-Host ""
    Write-Host "DOWNLOAD TIME ESTIMATE:" -ForegroundColor Cyan
    Write-Host "• Fast connection (100+ Mbps): 5-10 minutes" -ForegroundColor Green
    Write-Host "• Medium connection (50 Mbps): 15-20 minutes" -ForegroundColor Yellow
    Write-Host "• Slower connection (25 Mbps): 30-40 minutes" -ForegroundColor Red
}

function Test-DownloadProgress {
    Write-Host ""
    Write-Host "CHECKING DOWNLOAD PROGRESS" -ForegroundColor Cyan
    Write-Host "==========================" -ForegroundColor Cyan

    $downloadPath = "$env:USERPROFILE\Downloads\Windows11_Tools"

    # Check for Rufus
    $rufusFiles = Get-ChildItem -Path $downloadPath -Filter "rufus*.exe" -ErrorAction SilentlyContinue
    if ($rufusFiles) {
        $rufus = $rufusFiles[0]
        $sizeKB = [math]::Round($rufus.Length/1KB, 0)
        Write-Host "✅ RUFUS FOUND: $($rufus.Name) ($sizeKB KB)" -ForegroundColor Green
    } else {
        Write-Host "⏳ RUFUS: Not downloaded yet" -ForegroundColor Yellow
        Write-Host "   Expected: rufus.exe (~1MB)" -ForegroundColor White
    }

    # Check for Windows ISO
    $isoFiles = Get-ChildItem -Path $downloadPath -Filter "*.iso" -ErrorAction SilentlyContinue
    if ($isoFiles) {
        $iso = $isoFiles[0]
        $sizeGB = [math]::Round($iso.Length/1GB, 1)
        Write-Host "✅ WINDOWS 11 ISO FOUND: $($iso.Name) ($sizeGB GB)" -ForegroundColor Green
    } else {
        Write-Host "⏳ WINDOWS 11 ISO: Not downloaded yet" -ForegroundColor Yellow
        Write-Host "   Expected: Win11_*.iso (~5GB)" -ForegroundColor White
    }

    Write-Host ""
    if ($rufusFiles -and $isoFiles) {
        Write-Host "🎉 ALL DOWNLOADS COMPLETE!" -ForegroundColor Green
        Write-Host ""
        Write-Host "READY FOR BOOTABLE CREATION:" -ForegroundColor Yellow
        Write-Host "Run: .\eq12_d_windows_bootable.ps1 -Action Create" -ForegroundColor Green
    } else {
        Write-Host "⏳ Downloads still in progress..." -ForegroundColor Yellow
        Write-Host "   Run this check again in a few minutes" -ForegroundColor White
    }
}

function Start-MicrosoftDownload {
    Write-Host ""
    Write-Host "OPENING MICROSOFT WINDOWS 11 DOWNLOAD PAGE" -ForegroundColor Green
    Start-Process "https://www.microsoft.com/software-download/windows11"
    Start-Sleep -Seconds 2
    Get-Windows11DownloadGuide
}

function Show-NextSteps {
    Write-Host ""
    Write-Host "COMPLETE DOWNLOAD CHECKLIST:" -ForegroundColor Cyan
    Write-Host "============================" -ForegroundColor Cyan

    Write-Host ""
    Write-Host "DOWNLOADS NEEDED:" -ForegroundColor Yellow
    Write-Host "[ ] Rufus portable (rufus.exe) - 1MB" -ForegroundColor White
    Write-Host "[ ] Windows 11 ISO (Win11_*.iso) - 5GB" -ForegroundColor White

    Write-Host ""
    Write-Host "AFTER DOWNLOADS:" -ForegroundColor Yellow
    Write-Host "1. Check progress: .\eq12_d_windows_bootable.ps1 -Action Check" -ForegroundColor White
    Write-Host "2. Create bootable: .\eq12_d_windows_bootable.ps1 -Action Create" -ForegroundColor Green
    Write-Host "3. Verify result: .\eq12_d_windows_bootable.ps1 -Action Verify" -ForegroundColor White

    Write-Host ""
    Write-Host "TIME ESTIMATE:" -ForegroundColor Cyan
    Write-Host "• Downloads: 10-40 minutes (depending on speed)" -ForegroundColor White
    Write-Host "• Bootable creation: 15-30 minutes" -ForegroundColor White
    Write-Host "• Total process: ~1 hour" -ForegroundColor White

    Write-Host ""
    Write-Host "D: DRIVE WILL BECOME:" -ForegroundColor Green
    Write-Host "• Windows 11 Emergency Installer" -ForegroundColor White
    Write-Host "• System Recovery Tool" -ForegroundColor White
    Write-Host "• Boot Problem Resolver" -ForegroundColor White
}

# Main execution
Clear-Host
Write-Host "EQ12 RUFUS DOWNLOAD ASSISTANT" -ForegroundColor Cyan
Write-Host "Buffalo NY 14215 Content Empire" -ForegroundColor Gray
Write-Host ""

Get-RufusDownloadGuide
Start-MicrosoftDownload
Test-DownloadProgress
Show-NextSteps

Write-Host ""
Write-Host "🎯 CURRENT STATUS: Download phase in progress" -ForegroundColor Yellow
Write-Host "📁 Save location: $env:USERPROFILE\Downloads\Windows11_Tools" -ForegroundColor Gray
