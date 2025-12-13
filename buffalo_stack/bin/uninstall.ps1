#Requires -RunAsAdministrator
# Buffalo Stack + EQ12 Integration Uninstaller
# Removes scheduled tasks and optionally removes files

[CmdletBinding()]
param(
    [switch]$RemoveFiles,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "=== Uninstalling Buffalo Stack (EQ12 Integration) ===" -ForegroundColor Red

$base = "C:\EQ12\buffalo_stack"

# Remove scheduled tasks
Write-Host "⏰ Removing scheduled tasks..." -ForegroundColor Yellow

$tasks = @(
    "BuffaloStack\CivilServiceTracker",
    "BuffaloStack\EQ12ComboRunner"
)

foreach ($taskName in $tasks) {
    try {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($task) {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
            Write-Host "✅ Removed task: $taskName" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Task not found: $taskName" -ForegroundColor Yellow
        }
    } catch {
        Write-Warning "Could not remove task $taskName: $_"
        # Try with schtasks as fallback
        try {
            & schtasks /Delete /TN $taskName /F 2>$null
            Write-Host "✅ Removed task (fallback): $taskName" -ForegroundColor Green
        } catch {
            Write-Warning "Fallback removal also failed for $taskName"
        }
    }
}

# Remove desktop shortcut
try {
    $shortcutPath = "$env:USERPROFILE\Desktop\EQ12 Buffalo Stack.lnk"
    if (Test-Path $shortcutPath) {
        Remove-Item $shortcutPath -Force
        Write-Host "✅ Removed desktop shortcut" -ForegroundColor Green
    }
} catch {
    Write-Warning "Could not remove desktop shortcut: $_"
}

# Remove files if requested
if ($RemoveFiles) {
    if (Test-Path $base) {
        if ($Force -or (Read-Host "Remove all files in $base? (y/N)") -match '^[Yy]') {
            try {
                # Stop any running processes first
                Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*buffalo_stack*" } | Stop-Process -Force -ErrorAction SilentlyContinue
                
                Remove-Item $base -Recurse -Force
                Write-Host "✅ Removed all files: $base" -ForegroundColor Green
            } catch {
                Write-Error "Failed to remove files: $_"
            }
        } else {
            Write-Host "📁 Files preserved in: $base" -ForegroundColor Cyan
            Write-Host "   You can manually delete this directory if needed" -ForegroundColor Cyan
        }
    } else {
        Write-Host "📁 Directory not found: $base" -ForegroundColor Yellow
    }
}

# Clean up registry entries (if any were created)
try {
    $regPath = "HKCU:\Software\EQ12\BuffaloStack"
    if (Test-Path $regPath) {
        Remove-Item $regPath -Recurse -Force
        Write-Host "✅ Cleaned registry entries" -ForegroundColor Green
    }
} catch {
    Write-Warning "Could not clean registry: $_"
}

Write-Host "
=== Uninstallation Complete ===" -ForegroundColor Green

if (-not $RemoveFiles) {
    Write-Host "📁 Files preserved in: $base" -ForegroundColor Cyan
    Write-Host "   Run with -RemoveFiles to delete all files" -ForegroundColor Cyan
}

Write-Host "🔄 To reinstall: Run install.ps1 as Administrator" -ForegroundColor Yellow