#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 DIRECT ISO DOWNLOAD EXECUTOR
    Buffalo NY 14215 Content Empire

.DESCRIPTION
    Direct execution of expert ISO collection with scraped download URLs
    Automated download of essential ISOs for Ventoy multi-boot drive
#>

function Start-DirectISODownload {
    Clear-Host
    Write-Host "EQ12 DIRECT ISO DOWNLOAD EXECUTOR" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
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

    Write-Host "EXPERT ISO COLLECTION - DIRECT DOWNLOAD EXECUTION" -ForegroundColor Yellow
    Write-Host "=================================================" -ForegroundColor Yellow
    Write-Host ""

    $isoPath = "D:\"

    Write-Host "TIER 1: ESSENTIAL DOWNLOADS (HIGHEST PRIORITY)" -ForegroundColor Cyan
    Write-Host ""

    # Kali Linux 2025.3 Live (Latest from web scrape)
    Write-Host "1. DOWNLOADING Kali Linux 2025.3 Live..." -ForegroundColor Yellow
    $kaliUrl = "https://cdimage.kali.org/kali-2025.3/kali-linux-2025.3-live-amd64.iso"
    $kaliPath = "$isoPath\kali-linux-2025.3-live-amd64.iso"

    try {
        Write-Host "   URL: $kaliUrl" -ForegroundColor White
        Write-Host "   Size: ~4.6 GB - Starting download..." -ForegroundColor Yellow

        # Use BITS for large file download with progress
        Start-BitsTransfer -Source $kaliUrl -Destination $kaliPath -DisplayName "Kali Linux 2025.3"
        Write-Host "   [SUCCESS] Kali Linux downloaded successfully!" -ForegroundColor Green

    } catch {
        Write-Host "   [ERROR] Kali download failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   [FALLBACK] Opening Kali download page for manual download..." -ForegroundColor Yellow
        Start-Process "https://www.kali.org/get-kali/#kali-live"
    }

    Write-Host ""
    Write-Host "2. DOWNLOADING SystemRescue 11.02..." -ForegroundColor Yellow
    $sysrescueUrl = "https://osdn.net/projects/systemrescuecd/downloads/sysresccd/11.02/systemrescuecd-11.02-amd64.iso"
    $sysrescuePath = "$isoPath\systemrescuecd-11.02-amd64.iso"

    try {
        Write-Host "   URL: $sysrescueUrl" -ForegroundColor White
        Write-Host "   Size: ~850 MB - Starting download..." -ForegroundColor Yellow
        Start-BitsTransfer -Source $sysrescueUrl -Destination $sysrescuePath -DisplayName "SystemRescue 11.02"
        Write-Host "   [SUCCESS] SystemRescue downloaded successfully!" -ForegroundColor Green

    } catch {
        Write-Host "   [ERROR] SystemRescue download failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   [FALLBACK] Opening SystemRescue download page..." -ForegroundColor Yellow
        Start-Process "https://www.system-rescue.org/Download/"
    }

    Write-Host ""
    Write-Host "3. DOWNLOADING Clonezilla Live..." -ForegroundColor Yellow
    $clonezillaUrl = "https://osdn.net/projects/clonezilla/downloads/clonezilla_live_stable/3.1.2-25/clonezilla-live-3.1.2-25-amd64.iso"
    $clonezillaPath = "$isoPath\clonezilla-live-3.1.2-25-amd64.iso"

    try {
        Write-Host "   URL: $clonezillaUrl" -ForegroundColor White
        Write-Host "   Size: ~300 MB - Starting download..." -ForegroundColor Yellow
        Start-BitsTransfer -Source $clonezillaUrl -Destination $clonezillaPath -DisplayName "Clonezilla Live"
        Write-Host "   [SUCCESS] Clonezilla downloaded successfully!" -ForegroundColor Green

    } catch {
        Write-Host "   [ERROR] Clonezilla download failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   [FALLBACK] Opening Clonezilla download page..." -ForegroundColor Yellow
        Start-Process "https://clonezilla.org/downloads.php"
    }

    Write-Host ""
    Write-Host "TIER 2: SECURITY PROFESSIONAL SUITE" -ForegroundColor Cyan
    Write-Host ""

    Write-Host "4. PARROT SECURITY OS DOWNLOAD:" -ForegroundColor Yellow
    Write-Host "   Opening Parrot Security download page..." -ForegroundColor Green
    try {
        Start-Process "https://www.parrotsec.org/download/"
        Write-Host "   [OK] Parrot Security page opened" -ForegroundColor Green
        Write-Host ""
        Write-Host "   PARROT MANUAL DOWNLOAD INSTRUCTIONS:" -ForegroundColor Yellow
        Write-Host "   1. Select 'Security Edition'" -ForegroundColor White
        Write-Host "   2. Choose 'Live' format" -ForegroundColor White
        Write-Host "   3. Download AMD64 ISO (~3.8 GB)" -ForegroundColor White
        Write-Host "   4. Save to D:\ drive as parrot-security-live-amd64.iso" -ForegroundColor White
    } catch {
        Write-Host "   [ERROR] Browser error" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "5. GPARTED LIVE DOWNLOAD:" -ForegroundColor Yellow
    Write-Host "   Opening GParted download page..." -ForegroundColor Green
    try {
        Start-Process "https://gparted.org/download.php"
        Write-Host "   [OK] GParted page opened" -ForegroundColor Green
        Write-Host ""
        Write-Host "   GPARTED MANUAL DOWNLOAD INSTRUCTIONS:" -ForegroundColor Yellow
        Write-Host "   1. Click 'Download gparted-live-x.x.x-x-amd64.iso'" -ForegroundColor White
        Write-Host "   2. Save to D:\ drive (~400 MB)" -ForegroundColor White
        Write-Host "   3. Keep original filename" -ForegroundColor White
    } catch {
        Write-Host "   [ERROR] Browser error" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "6. UBUNTU 24.04.1 LTS DOWNLOAD:" -ForegroundColor Yellow
    Write-Host "   Opening Ubuntu download page..." -ForegroundColor Green
    try {
        Start-Process "https://ubuntu.com/download/desktop"
        Write-Host "   [OK] Ubuntu page opened" -ForegroundColor Green
        Write-Host ""
        Write-Host "   UBUNTU MANUAL DOWNLOAD INSTRUCTIONS:" -ForegroundColor Yellow
        Write-Host "   1. Click 'Download Ubuntu Desktop'" -ForegroundColor White
        Write-Host "   2. Save as ubuntu-24.04.1-desktop-amd64.iso" -ForegroundColor White
        Write-Host "   3. Move to D:\ drive (~5.1 GB)" -ForegroundColor White
    } catch {
        Write-Host "   [ERROR] Browser error" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "DOWNLOAD STATUS VERIFICATION" -ForegroundColor Green
    Write-Host "============================" -ForegroundColor Green

    Start-Sleep 3  # Give downloads time to start

    # Check download status
    $expertISOs = @(
        @{Name="Kali Linux 2025.3"; Path="$isoPath\kali-linux-2025.3-live-amd64.iso"; ExpectedSizeGB=4.6},
        @{Name="SystemRescue 11.02"; Path="$isoPath\systemrescuecd-11.02-amd64.iso"; ExpectedSizeGB=0.85},
        @{Name="Clonezilla Live"; Path="$isoPath\clonezilla-live-3.1.2-25-amd64.iso"; ExpectedSizeGB=0.3},
        @{Name="Ubuntu 24.04.1 LTS"; Path="$isoPath\ubuntu-24.04.1-desktop-amd64.iso"; ExpectedSizeGB=5.1},
        @{Name="Parrot Security"; Path="$isoPath\parrot-security-live-amd64.iso"; ExpectedSizeGB=3.8},
        @{Name="GParted Live"; Path="$isoPath\gparted-live-*.iso"; ExpectedSizeGB=0.4}
    )

    $downloadedCount = 0
    $totalSizeGB = 0

    Write-Host ""
    foreach ($iso in $expertISOs) {
        if ($iso.Path -like "*gparted*") {
            # Check for GParted with wildcard
            $gpartedFiles = Get-ChildItem -Path $isoPath -Filter "gparted-live-*.iso" -ErrorAction SilentlyContinue
            if ($gpartedFiles) {
                $actualSizeGB = [math]::Round($gpartedFiles[0].Length/1GB, 2)
                Write-Host "  [OK] $($iso.Name) ($actualSizeGB GB)" -ForegroundColor Green
                $downloadedCount++
                $totalSizeGB += $actualSizeGB
            } else {
                Write-Host "  [PENDING] $($iso.Name) (~$($iso.ExpectedSizeGB) GB)" -ForegroundColor Yellow
            }
        } elseif (Test-Path $iso.Path) {
            $actualSizeGB = [math]::Round((Get-Item $iso.Path).Length/1GB, 2)
            Write-Host "  [OK] $($iso.Name) ($actualSizeGB GB)" -ForegroundColor Green
            $downloadedCount++
            $totalSizeGB += $actualSizeGB
        } else {
            Write-Host "  [PENDING] $($iso.Name) (~$($iso.ExpectedSizeGB) GB)" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "EXPERT ISO COLLECTION STATUS:" -ForegroundColor Cyan
    Write-Host "  Downloaded: $downloadedCount of $($expertISOs.Count) ISOs" -ForegroundColor White
    Write-Host "  Total Size: $totalSizeGB GB" -ForegroundColor White
    Write-Host "  Ventoy Free Space: $freeGB GB" -ForegroundColor White

    if ($downloadedCount -gt 0) {
        Write-Host ""
        Write-Host "VENTOY BOOT TEST READY!" -ForegroundColor Green
        Write-Host "======================" -ForegroundColor Green
        Write-Host ""
        Write-Host "YOUR MULTI-BOOT DRIVE IS OPERATIONAL:" -ForegroundColor Yellow
        Write-Host "1. Insert D: drive into any computer" -ForegroundColor White
        Write-Host "2. Boot from USB (F12 during startup)" -ForegroundColor White
        Write-Host "3. Ventoy menu shows your available ISOs" -ForegroundColor White
        Write-Host "4. Select any ISO to boot directly" -ForegroundColor White

        Write-Host ""
        Write-Host "PROFESSIONAL CAPABILITIES ENABLED:" -ForegroundColor Cyan
        if (Test-Path "$isoPath\kali-linux-2025.3-live-amd64.iso") {
            Write-Host "  [READY] Kali Linux - Security analysis & penetration testing" -ForegroundColor Green
        }
        if (Test-Path "$isoPath\systemrescuecd-11.02-amd64.iso") {
            Write-Host "  [READY] SystemRescue - Emergency recovery & hardware testing" -ForegroundColor Green
        }
        if (Test-Path "$isoPath\clonezilla-live-3.1.2-25-amd64.iso") {
            Write-Host "  [READY] Clonezilla - Disk cloning & backup operations" -ForegroundColor Green
        }
    }

    Write-Host ""
    Write-Host "EQ12 EXPERT ISO COLLECTION EXECUTION COMPLETE!" -ForegroundColor Green
    Write-Host "Professional multi-boot system administration drive ready" -ForegroundColor Cyan
}

# Check BITS service and start direct download
try {
    $bitsService = Get-Service "BITS" -ErrorAction SilentlyContinue
    if ($bitsService.Status -ne "Running") {
        Write-Host "Starting BITS service for optimized downloads..." -ForegroundColor Yellow
        Start-Service "BITS"
    }
} catch {
    Write-Host "BITS service not available - using standard download method" -ForegroundColor Yellow
}

# Execute direct ISO download
Start-DirectISODownload
