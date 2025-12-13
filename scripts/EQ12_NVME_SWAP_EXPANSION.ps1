<#
.SYNOPSIS
    EQ12 NVMe Swap Expansion - Expand pagefile to 200-512GB for AI/Docker workloads

.DESCRIPTION
    Optimizes Windows pagefile and WSL2 swap for heavy workloads:
    - Expands Windows pagefile to utilize 2TB NVMe drive
    - Configures WSL2 .wslconfig for optimal swap
    - Prevents OOM crashes during AI inference, Docker builds, HuggingFace, etc.

.NOTES
    Author: EQ12 System (Expert System Engineer)
    Created: 2025-11-27
    Requires: Administrator privileges
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateRange(50000, 524288)]
    [int]$PagefileSizeMB = 204800,  # 200GB default (adjust based on available NVMe space)
    
    [Parameter()]
    [switch]$WSL2Optimize = $true,
    
    [Parameter()]
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$LogPath = "C:\EQ12_BROKEN_20251122_210342\logs\nvme_swap_expansion.log"

# ============================================================================
# LOGGING
# ============================================================================

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp [$Level] $Message"
    
    # Create log directory if not exists
    $logDir = Split-Path $LogPath -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    # Write to log file
    Add-Content -Path $LogPath -Value $logEntry
    
    # Write to console with color
    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        default { Write-Host $logEntry }
    }
}

# ============================================================================
# ADMIN CHECK
# ============================================================================

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Log "This script requires Administrator privileges. Please run as Administrator." -Level "ERROR"
    exit 1
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Write-Log "========================================" -Level "INFO"
Write-Log "EQ12 NVMe Swap Expansion Started" -Level "INFO"
Write-Log "========================================" -Level "INFO"
Write-Log "System: $env:COMPUTERNAME" -Level "INFO"
Write-Log "User: $env:USERNAME" -Level "INFO"
Write-Log "Target Pagefile Size: $($PagefileSizeMB / 1024) GB" -Level "INFO"

if ($DryRun) {
    Write-Log "DRY RUN MODE - No changes will be made" -Level "WARNING"
}

# ============================================================================
# STEP 1: DETECT NVMe DRIVE
# ============================================================================

Write-Log "Step 1: Detecting NVMe drives..." -Level "INFO"

$nvmeDrives = Get-PhysicalDisk | Where-Object { $_.BusType -eq "NVMe" }

if ($nvmeDrives.Count -eq 0) {
    Write-Log "No NVMe drives detected. Checking for SSD alternatives..." -Level "WARNING"
    $nvmeDrives = Get-PhysicalDisk | Where-Object { $_.MediaType -eq "SSD" }
}

if ($nvmeDrives.Count -eq 0) {
    Write-Log "No suitable drives found for swap expansion." -Level "ERROR"
    exit 1
}

foreach ($drive in $nvmeDrives) {
    $sizeGB = [math]::Round($drive.Size / 1GB, 2)
    Write-Log "  Found: $($drive.FriendlyName) - $sizeGB GB - BusType: $($drive.BusType)" -Level "INFO"
}

# ============================================================================
# STEP 2: CHECK CURRENT PAGEFILE CONFIGURATION
# ============================================================================

Write-Log "Step 2: Checking current pagefile configuration..." -Level "INFO"

$currentPagefile = Get-CimInstance -ClassName Win32_PageFileUsage
if ($currentPagefile) {
    $currentSizeMB = $currentPagefile.AllocatedBaseSize
    $currentSizeGB = [math]::Round($currentSizeMB / 1024, 2)
    Write-Log "  Current Pagefile: $($currentPagefile.Name)" -Level "INFO"
    Write-Log "  Current Size: $currentSizeGB GB ($currentSizeMB MB)" -Level "INFO"
    Write-Log "  Current Usage: $($currentPagefile.CurrentUsage) MB" -Level "INFO"
    Write-Log "  Peak Usage: $($currentPagefile.PeakUsage) MB" -Level "INFO"
}
else {
    Write-Log "  No pagefile configured (system-managed)" -Level "WARNING"
    $currentSizeMB = 0
}

# ============================================================================
# STEP 3: CALCULATE OPTIMAL PAGEFILE SIZE
# ============================================================================

Write-Log "Step 3: Calculating optimal pagefile size..." -Level "INFO"

$ramBytes = (Get-CimInstance -ClassName Win32_ComputerSystem).TotalPhysicalMemory
$ramGB = [math]::Round($ramBytes / 1GB, 2)

Write-Log "  System RAM: $ramGB GB" -Level "INFO"

# Check available space on C: drive
$cDrive = Get-PSDrive -Name C
$freeSpaceGB = [math]::Round($cDrive.Free / 1GB, 2)
$usedSpaceGB = [math]::Round($cDrive.Used / 1GB, 2)
$totalSpaceGB = [math]::Round(($cDrive.Free + $cDrive.Used) / 1GB, 2)

Write-Log "  C: Drive - Total: $totalSpaceGB GB, Used: $usedSpaceGB GB, Free: $freeSpaceGB GB" -Level "INFO"

# Recommended size: 200GB for AI workloads (adjust if space limited)
$recommendedSizeMB = 204800  # 200GB
$maxSafeSizeMB = [math]::Floor(($freeSpaceGB - 100) * 1024)  # Leave 100GB free

if ($PagefileSizeMB -gt $maxSafeSizeMB) {
    Write-Log "  Requested size ($($PagefileSizeMB / 1024) GB) exceeds safe limit." -Level "WARNING"
    Write-Log "  Adjusting to max safe size: $($maxSafeSizeMB / 1024) GB" -Level "WARNING"
    $PagefileSizeMB = $maxSafeSizeMB
}

Write-Log "  Final Pagefile Size: $($PagefileSizeMB / 1024) GB ($PagefileSizeMB MB)" -Level "SUCCESS"

# ============================================================================
# STEP 4: CONFIGURE PAGEFILE
# ============================================================================

Write-Log "Step 4: Configuring pagefile..." -Level "INFO"

if (-not $DryRun) {
    try {
        # Disable automatic pagefile management
        $cs = Get-CimInstance -ClassName Win32_ComputerSystem
        if ($cs.AutomaticManagedPagefile) {
            Write-Log "  Disabling automatic pagefile management..." -Level "INFO"
            $cs | Set-CimInstance -Property @{AutomaticManagedPagefile = $false }
        }
        
        # Remove existing pagefile settings
        $existingPagefiles = Get-CimInstance -ClassName Win32_PageFileSetting
        foreach ($pf in $existingPagefiles) {
            Write-Log "  Removing existing pagefile: $($pf.Name)" -Level "INFO"
            $pf | Remove-CimInstance
        }
        
        # Create new pagefile with custom size
        Write-Log "  Creating new pagefile: C:\pagefile.sys" -Level "INFO"
        Write-Log "  Initial Size: $PagefileSizeMB MB" -Level "INFO"
        Write-Log "  Maximum Size: $PagefileSizeMB MB" -Level "INFO"
        
        New-CimInstance -ClassName Win32_PageFileSetting -Property @{
            Name        = "C:\pagefile.sys"
            InitialSize = $PagefileSizeMB
            MaximumSize = $PagefileSizeMB
        } | Out-Null
        
        Write-Log "✅ Pagefile configured successfully" -Level "SUCCESS"
        Write-Log "⚠️  REBOOT REQUIRED for changes to take effect" -Level "WARNING"
        
    }
    catch {
        Write-Log "❌ Error configuring pagefile: $($_.Exception.Message)" -Level "ERROR"
        exit 1
    }
}
else {
    Write-Log "  [DRY RUN] Would configure pagefile: C:\pagefile.sys" -Level "INFO"
    Write-Log "  [DRY RUN] Size: $PagefileSizeMB MB" -Level "INFO"
}

# ============================================================================
# STEP 5: OPTIMIZE WSL2 SWAP (if enabled)
# ============================================================================

if ($WSL2Optimize) {
    Write-Log "Step 5: Optimizing WSL2 swap configuration..." -Level "INFO"
    
    $wslConfigPath = "$env:USERPROFILE\.wslconfig"
    
    # Calculate WSL2 swap size (50% of pagefile)
    $wsl2SwapGB = [math]::Floor($PagefileSizeMB / 2048)
    
    $wslConfig = @"
[wsl2]
# Memory allocation (75% of system RAM)
memory=$([math]::Floor($ramGB * 0.75))GB

# Swap size (optimized for AI/Docker)
swap=$($wsl2SwapGB)GB

# Processor count (all cores)
processors=12

# Localhostforwarding (enable Docker/WSL networking)
localhostForwarding=true

# Enable nested virtualization
nestedVirtualization=true

# Swap file location (use fast NVMe)
swapFile=C:\\temp\\wsl-swap.vhdx
"@

    if (-not $DryRun) {
        try {
            Write-Log "  Writing .wslconfig to: $wslConfigPath" -Level "INFO"
            $wslConfig | Out-File -FilePath $wslConfigPath -Encoding UTF8 -Force
            
            Write-Log "✅ WSL2 configuration optimized" -Level "SUCCESS"
            Write-Log "  Memory: $([math]::Floor($ramGB * 0.75))GB" -Level "INFO"
            Write-Log "  Swap: $($wsl2SwapGB)GB" -Level "INFO"
            Write-Log "  Processors: 12" -Level "INFO"
            Write-Log "⚠️  Run 'wsl --shutdown' to apply changes" -Level "WARNING"
            
        }
        catch {
            Write-Log "⚠️  Error writing .wslconfig: $($_.Exception.Message)" -Level "WARNING"
        }
    }
    else {
        Write-Log "  [DRY RUN] Would create .wslconfig with:" -Level "INFO"
        Write-Log "  Memory: $([math]::Floor($ramGB * 0.75))GB" -Level "INFO"
        Write-Log "  Swap: $($wsl2SwapGB)GB" -Level "INFO"
    }
}

# ============================================================================
# STEP 6: SUMMARY & NEXT STEPS
# ============================================================================

Write-Log "========================================" -Level "INFO"
Write-Log "EQ12 NVMe Swap Expansion Complete" -Level "SUCCESS"
Write-Log "========================================" -Level "INFO"

if (-not $DryRun) {
    Write-Log "CHANGES MADE:" -Level "SUCCESS"
    Write-Log "  ✅ Pagefile expanded: $($PagefileSizeMB / 1024) GB" -Level "SUCCESS"
    if ($WSL2Optimize) {
        Write-Log "  ✅ WSL2 swap configured: $wsl2SwapGB GB" -Level "SUCCESS"
    }
    
    Write-Log "" -Level "INFO"
    Write-Log "NEXT STEPS:" -Level "WARNING"
    Write-Log "  1. REBOOT your system for pagefile changes to apply" -Level "WARNING"
    Write-Log "  2. Run 'wsl --shutdown' and restart WSL for WSL2 changes" -Level "WARNING"
    Write-Log "  3. Verify with: Get-CimInstance Win32_PageFileUsage" -Level "INFO"
    Write-Log "  4. Test with heavy workload (Docker build, AI inference)" -Level "INFO"
    
    Write-Log "" -Level "INFO"
    Write-Log "Log saved to: $LogPath" -Level "INFO"
}
else {
    Write-Log "DRY RUN COMPLETE - No changes made" -Level "WARNING"
    Write-Log "Run without -DryRun to apply changes" -Level "INFO"
}

Write-Log "========================================" -Level "INFO"
