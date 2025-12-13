<#
.SYNOPSIS
    EQ12 Sysinternals Integration Toolkit
.DESCRIPTION
    Integrates the Sysinternals Suite located at C:\Users\Ricoj100\OneDrive\Desktop\SysinternalsSuite
    into the EQ12 workflow.
#>
[CmdletBinding()]
param()

$SysinternalsPath = "C:\Users\Ricoj100\OneDrive\Desktop\SysinternalsSuite"

if (-not (Test-Path $SysinternalsPath)) {
    Write-Error "Sysinternals Suite not found at $SysinternalsPath"
    return
}

Write-Host "✅ EQ12 Sysinternals Toolkit Loaded from: $SysinternalsPath" -ForegroundColor Green

# Add to PATH for this session
if ($env:PATH -notlike "*$SysinternalsPath*") {
    $env:PATH += ";$SysinternalsPath"
    Write-Host "   -> Added to Session PATH" -ForegroundColor Gray
}

function Start-EQ12ProcessMonitor {
    Write-Host "🚀 Launching Process Explorer..." -ForegroundColor Cyan
    Start-Process "$script:SysinternalsPath\procexp64.exe"
}

function Start-EQ12NetworkMonitor {
    Write-Host "🚀 Launching TCPView..." -ForegroundColor Cyan
    Start-Process "$script:SysinternalsPath\tcpview64.exe"
}

function Start-EQ12Autoruns {
    Write-Host "🚀 Launching Autoruns..." -ForegroundColor Cyan
    Start-Process "$script:SysinternalsPath\autoruns64.exe"
}

function Get-EQ12DiskUsage {
    param([string]$Path = ".")
    Write-Host "📊 Analyzing Disk Usage for: $Path" -ForegroundColor Cyan
    & "$script:SysinternalsPath\du64.exe" -v $Path
}

function Get-EQ12FileLocks {
    param([string]$Path)
    if (-not $Path) { $Path = $PWD }
    Write-Host "🔒 Checking for open handles in: $Path" -ForegroundColor Cyan
    & "$script:SysinternalsPath\handle64.exe" $Path
}

function Get-EQ12SystemInfo {
    Write-Host "ℹ️  System Information (PsInfo)..." -ForegroundColor Cyan
    & "$script:SysinternalsPath\PsInfo64.exe"
}

# Export aliases
Set-Alias -Name eq12-procexp -Value Start-EQ12ProcessMonitor
Set-Alias -Name eq12-tcpview -Value Start-EQ12NetworkMonitor
Set-Alias -Name eq12-du -Value Get-EQ12DiskUsage
Set-Alias -Name eq12-locks -Value Get-EQ12FileLocks

Write-Host "   -> Commands Available:" -ForegroundColor Yellow
Write-Host "      eq12-procexp      : Launch Process Explorer"
Write-Host "      eq12-tcpview      : Launch TCPView"
Write-Host "      eq12-du [path]    : Check Disk Usage"
Write-Host "      eq12-locks [path] : Check file handles"
Write-Host "      Get-EQ12SystemInfo: View System Info"
