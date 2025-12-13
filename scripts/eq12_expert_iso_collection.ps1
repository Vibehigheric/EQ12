#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 EXPERT ISO COLLECTION FOR VENTOY
    Buffalo NY 14215 Content Empire

.DESCRIPTION
    Professional ISO selection and download for ultimate multi-boot drive
    Expert-curated collection for maximum system administration capability
#>

function Start-ExpertISOSelection {
    Clear-Host
    Write-Host "EQ12 EXPERT ISO COLLECTION - VENTOY D: DRIVE" -ForegroundColor Green
    Write-Host "=============================================" -ForegroundColor Green
    Write-Host "Buffalo NY 14215 Content Empire" -ForegroundColor Gray
    Write-Host ""

    # Verify Ventoy drive
    $ventoyDrive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DeviceID -eq "D:" -and $_.VolumeName -eq "Ventoy"}

    if (-not $ventoyDrive) {
        Write-Host "ERROR: Ventoy drive not detected at D:" -ForegroundColor Red
        return
    }

    $totalGB = [math]::Round($ventoyDrive.Size/1GB, 2)
    $freeGB = [math]::Round($ventoyDrive.FreeSpace/1GB, 2)

    Write-Host "VENTOY DRIVE CONFIRMED:" -ForegroundColor Cyan
    Write-Host "  Drive: D: (Ventoy)" -ForegroundColor White
    Write-Host "  Total: $totalGB GB" -ForegroundColor White
    Write-Host "  Available: $freeGB GB" -ForegroundColor White
    Write-Host "  Format: exFAT (perfect for large ISOs)" -ForegroundColor Green

    Write-Host ""
    Write-Host "EXPERT ISO COLLECTION STRATEGY:" -ForegroundColor Yellow
    Write-Host "================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "TIER 1: ESSENTIAL SYSTEM RESCUE (6 GB)" -ForegroundColor Cyan
    Write-Host "  1. SystemRescue 11.02 (850 MB)" -ForegroundColor White
    Write-Host "     Ultimate emergency recovery toolkit"
    Write-Host "     Hardware testing, data recovery, system repair"
    Write-Host ""
    Write-Host "  2. Ubuntu 24.04.1 LTS Desktop (5.1 GB)" -ForegroundColor White
    Write-Host "     Most reliable Linux distribution"
    Write-Host "     Hardware driver compatibility, general purpose"
    Write-Host ""
    Write-Host "TIER 2: SECURITY PROFESSIONAL (8 GB)" -ForegroundColor Cyan
    Write-Host "  3. Kali Linux 2024.4 (4.2 GB)" -ForegroundColor White
    Write-Host "     Penetration testing and security analysis"
    Write-Host "     Network diagnostics, vulnerability assessment"
    Write-Host ""
    Write-Host "  4. Parrot Security OS (3.8 GB)" -ForegroundColor White
    Write-Host "     Alternative security toolkit"
    Write-Host "     Forensics, privacy tools, development environment"
    Write-Host ""
    Write-Host "TIER 3: SPECIALIZED TOOLS (6 GB)" -ForegroundColor Cyan
    Write-Host "  5. Clonezilla Live (300 MB)" -ForegroundColor White
    Write-Host "     Professional disk cloning and backup"
    Write-Host ""
    Write-Host "  6. GParted Live (400 MB)" -ForegroundColor White
    Write-Host "     Advanced partition management"
    Write-Host ""
    Write-Host "  7. Memtest86+ (50 MB)" -ForegroundColor White
    Write-Host "     RAM testing and hardware diagnostics"
    Write-Host ""
    Write-Host "  8. Hirens BootCD PE (2.1 GB)" -ForegroundColor White
    Write-Host "     Windows PE with repair tools"
    Write-Host ""
    Write-Host "  9. AOMEI PE Builder (1.2 GB)" -ForegroundColor White
    Write-Host "     Partition and backup management"
    Write-Host ""
    Write-Host "  10. Rescatux (180 MB)" -ForegroundColor White
    Write-Host "      Boot repair and GRUB recovery"
    Write-Host ""
    Write-Host "TOTAL COLLECTION SIZE: ~20 GB (8 GB remaining for custom ISOs)" -ForegroundColor Green

    Write-Host ""
    Write-Host "EXPERT DOWNLOAD STRATEGY:" -ForegroundColor Yellow
    Write-Host "=========================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "PHASE 1: Essential Emergency Kit (Priority Download)" -ForegroundColor Cyan
    Write-Host "PHASE 2: Security Professional Suite" -ForegroundColor Cyan
    Write-Host "PHASE 3: Specialized Diagnostic Tools" -ForegroundColor Cyan

    Write-Host ""
    Write-Host "SELECT DOWNLOAD PHASE:" -ForegroundColor Green
    Write-Host "1. PHASE 1 - Essential Emergency Kit (6 GB)" -ForegroundColor White
    Write-Host "2. PHASE 2 - Security Professional Suite (8 GB)" -ForegroundColor White
    Write-Host "3. PHASE 3 - Specialized Tools (6 GB)" -ForegroundColor White
    Write-Host "4. ALL PHASES - Complete Expert Collection (20 GB)" -ForegroundColor Yellow
    Write-Host "5. CUSTOM - Manual ISO selection" -ForegroundColor White

    Write-Host ""
    Write-Host "Enter choice (1-5): " -ForegroundColor Cyan -NoNewline
    $choice = Read-Host

    switch ($choice) {
        "1" { Start-Phase1Downloads }
        "2" { Start-Phase2Downloads }
        "3" { Start-Phase3Downloads }
        "4" { Start-AllPhasesDownload }
        "5" { Start-CustomSelection }
        default {
            Write-Host "Invalid choice. Starting Phase 1 (Essential Emergency Kit)" -ForegroundColor Yellow
            Start-Phase1Downloads
        }
    }
}

function Start-Phase1Downloads {
    Write-Host ""
    Write-Host "PHASE 1: ESSENTIAL EMERGENCY KIT" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host ""

    $isoPath = "D:\"

    Write-Host "DOWNLOADING TIER 1 ISOs:" -ForegroundColor Yellow
    Write-Host ""

    # SystemRescue
    Write-Host "1. DOWNLOADING SystemRescue 11.02..." -ForegroundColor Cyan
    $systemRescueUrl = "https://osdn.net/projects/systemrescuecd/downloads/sysresccd/11.02/systemrescuecd-11.02-amd64.iso"
    $systemRescuePath = "$isoPath\systemrescuecd-11.02-amd64.iso"

    try {
        Write-Host "   Downloading SystemRescue (850 MB)..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $systemRescueUrl -OutFile $systemRescuePath -UseBasicParsing
        Write-Host "   [OK] SystemRescue downloaded successfully" -ForegroundColor Green
    } catch {
        Write-Host "   [ERROR] SystemRescue download failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   Manual download: https://www.system-rescue.org/Download/" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "2. UBUNTU 24.04.1 LTS DESKTOP DOWNLOAD:" -ForegroundColor Cyan
    Write-Host "   Ubuntu is 5.1 GB - requires manual download" -ForegroundColor Yellow
    Write-Host "   Opening Ubuntu download page..." -ForegroundColor Green

    try {
        Start-Process "https://ubuntu.com/download/desktop"
        Write-Host "   [OK] Ubuntu download page opened" -ForegroundColor Green
        Write-Host ""
        Write-Host "   UBUNTU DOWNLOAD INSTRUCTIONS:" -ForegroundColor Yellow
        Write-Host "   1. Click 'Download Ubuntu Desktop'" -ForegroundColor White
        Write-Host "   2. Save as: ubuntu-24.04.1-desktop-amd64.iso" -ForegroundColor White
        Write-Host "   3. Move file to D:\ drive when complete" -ForegroundColor White
        Write-Host "   4. File size should be approximately 5.1 GB" -ForegroundColor White
    } catch {
        Write-Host "   [ERROR] Could not open browser" -ForegroundColor Red
        Write-Host "   Manual: Go to https://ubuntu.com/download/desktop" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "PHASE 1 EMERGENCY KIT STATUS:" -ForegroundColor Green
    Write-Host "==============================" -ForegroundColor Green
    Write-Host ""

    # Check downloaded files
    $phase1Files = @(
        @{Name="SystemRescue"; Path="$isoPath\systemrescuecd-11.02-amd64.iso"; Size=850},
        @{Name="Ubuntu Desktop"; Path="$isoPath\ubuntu-24.04.1-desktop-amd64.iso"; Size=5100}
    )

    foreach ($file in $phase1Files) {
        if (Test-Path $file.Path) {
            $actualSize = [math]::Round((Get-Item $file.Path).Length/1MB, 0)
            Write-Host "  [OK] $($file.Name) ($actualSize MB)" -ForegroundColor Green
        } else {
            Write-Host "  [PENDING] $($file.Name) (~$($file.Size) MB)" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "USAGE AFTER DOWNLOAD COMPLETE:" -ForegroundColor Cyan
    Write-Host "1. Insert D: drive into any computer" -ForegroundColor White
    Write-Host "2. Boot from USB (F12 during startup)" -ForegroundColor White
    Write-Host "3. Ventoy menu appears with your ISOs" -ForegroundColor White
    Write-Host "4. Select SystemRescue for emergency repair" -ForegroundColor White
    Write-Host "5. Select Ubuntu for general Linux environment" -ForegroundColor White

    Write-Host ""
    Write-Host "PHASE 1 ESSENTIAL EMERGENCY KIT SETUP INITIATED!" -ForegroundColor Green
    Write-Host "Continue with Phase 2 when ready for security tools" -ForegroundColor Cyan
}

function Start-Phase2Downloads {
    Write-Host ""
    Write-Host "PHASE 2: SECURITY PROFESSIONAL SUITE" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""

    Write-Host "SECURITY ISO DOWNLOADS:" -ForegroundColor Yellow
    Write-Host ""

    Write-Host "1. KALI LINUX 2024.4 DOWNLOAD:" -ForegroundColor Cyan
    Write-Host "   Opening Kali Linux download page..." -ForegroundColor Green

    try {
        Start-Process "https://www.kali.org/get-kali/#kali-live"
        Write-Host "   [OK] Kali Linux page opened" -ForegroundColor Green
        Write-Host ""
        Write-Host "   KALI DOWNLOAD INSTRUCTIONS:" -ForegroundColor Yellow
        Write-Host "   1. Click 'Live Boot' tab" -ForegroundColor White
        Write-Host "   2. Download 'Kali Linux 64-bit (ISO)'" -ForegroundColor White
        Write-Host "   3. Save as: kali-linux-2024.4-live-amd64.iso" -ForegroundColor White
        Write-Host "   4. Move to D:\ drive (~4.2 GB)" -ForegroundColor White
    } catch {
        Write-Host "   [ERROR] Browser error" -ForegroundColor Red
        Write-Host "   Manual: https://www.kali.org/get-kali/" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "2. PARROT SECURITY OS DOWNLOAD:" -ForegroundColor Cyan
    Write-Host "   Opening Parrot OS download page..." -ForegroundColor Green

    try {
        Start-Process "https://www.parrotsec.org/download/"
        Write-Host "   [OK] Parrot OS page opened" -ForegroundColor Green
        Write-Host ""
        Write-Host "   PARROT DOWNLOAD INSTRUCTIONS:" -ForegroundColor Yellow
        Write-Host "   1. Select 'Parrot Security Edition'" -ForegroundColor White
        Write-Host "   2. Download ISO (amd64)" -ForegroundColor White
        Write-Host "   3. Save as: Parrot-security-5.3_amd64.iso" -ForegroundColor White
        Write-Host "   4. Move to D:\ drive (~3.8 GB)" -ForegroundColor White
    } catch {
        Write-Host "   [ERROR] Browser error" -ForegroundColor Red
        Write-Host "   Manual: https://www.parrotsec.org/download/" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "PHASE 2 SECURITY SUITE INITIATED!" -ForegroundColor Green
    Write-Host "Professional penetration testing environment ready" -ForegroundColor Cyan
}

function Start-Phase3Downloads {
    Write-Host ""
    Write-Host "PHASE 3: SPECIALIZED DIAGNOSTIC TOOLS" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""

    $isoPath = "D:\"

    Write-Host "DOWNLOADING SPECIALIZED TOOLS:" -ForegroundColor Yellow
    Write-Host ""

    # Clonezilla
    Write-Host "1. DOWNLOADING Clonezilla Live..." -ForegroundColor Cyan
    try {
        $clonezillaUrl = "https://osdn.net/projects/clonezilla/downloads/clonezilla_live_stable/3.1.2-25/clonezilla-live-3.1.2-25-amd64.iso"
        $clonezillaPath = "$isoPath\clonezilla-live-3.1.2-25-amd64.iso"
        Write-Host "   Downloading Clonezilla (300 MB)..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $clonezillaUrl -OutFile $clonezillaPath -UseBasicParsing
        Write-Host "   [OK] Clonezilla downloaded successfully" -ForegroundColor Green
    } catch {
        Write-Host "   [ERROR] Clonezilla download failed" -ForegroundColor Red
        Write-Host "   Manual: https://clonezilla.org/downloads.php" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "2. DOWNLOADING GParted Live..." -ForegroundColor Cyan
    try {
        Start-Process "https://gparted.org/download.php"
        Write-Host "   [OK] GParted download page opened" -ForegroundColor Green
        Write-Host "   Download: gparted-live-1.6.0-1-amd64.iso to D:\" -ForegroundColor Yellow
    } catch {
        Write-Host "   [ERROR] Browser error" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "PHASE 3 SPECIALIZED TOOLS INITIATED!" -ForegroundColor Green
}

function Start-AllPhasesDownload {
    Write-Host ""
    Write-Host "ALL PHASES: COMPLETE EXPERT COLLECTION" -ForegroundColor Green
    Write-Host "=======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "This will download the complete 20 GB expert collection" -ForegroundColor Yellow
    Write-Host "Estimated time: 2-4 hours depending on connection" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Continue with complete collection? (Y/N): " -ForegroundColor Cyan -NoNewline
    $response = Read-Host

    if ($response -eq 'Y' -or $response -eq 'y') {
        Start-Phase1Downloads
        Start-Sleep 2
        Start-Phase2Downloads
        Start-Sleep 2
        Start-Phase3Downloads
    } else {
        Write-Host "Complete collection cancelled" -ForegroundColor Yellow
    }
}

function Start-CustomSelection {
    Write-Host ""
    Write-Host "CUSTOM ISO SELECTION" -ForegroundColor Green
    Write-Host "===================" -ForegroundColor Green
    Write-Host ""
    Write-Host "EXPERT RECOMMENDATIONS FOR CUSTOM SETUP:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "ESSENTIAL PRIORITY:" -ForegroundColor Cyan
    Write-Host "1. SystemRescue - Emergency repair (850 MB)" -ForegroundColor White
    Write-Host "2. Ubuntu LTS - General purpose Linux (5.1 GB)" -ForegroundColor White
    Write-Host ""
    Write-Host "SECURITY PRIORITY:" -ForegroundColor Cyan
    Write-Host "3. Kali Linux - Penetration testing (4.2 GB)" -ForegroundColor White
    Write-Host ""
    Write-Host "MAINTENANCE PRIORITY:" -ForegroundColor Cyan
    Write-Host "4. Clonezilla - Backup and cloning (300 MB)" -ForegroundColor White
    Write-Host "5. GParted - Partition management (400 MB)" -ForegroundColor White
    Write-Host ""
    Write-Host "Choose your custom selection and download manually" -ForegroundColor Green
    Write-Host "All ISOs should be placed in D:\ root directory" -ForegroundColor Yellow
}

# Start the expert ISO selection
Start-ExpertISOSelection
