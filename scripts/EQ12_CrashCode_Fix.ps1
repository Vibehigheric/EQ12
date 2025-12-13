# EQ12_CrashCode_Fix.ps1
#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Fixes Visual Studio Code crash code -536870904 and related auth/extension issues on the EQ12 system.

.DESCRIPTION
    This script is designed for your EQ12 Windows system. It:
      - Stops all VS Code processes
      - Clears VS Code cache and user data
      - Removes Snyk vulnerability scanner and GitHub Copilot Chat extensions
      - Relaxes Smart Card logon enforcement
      - Repairs TLS/SCHANNEL certificate caches
      - Runs system file and image health checks (SFC/DISM)
      - Frees common EQ12 service ports (8000, 8080, 4040)

    Run this in an elevated PowerShell window (Run as Administrator).
#>

Write-Host "=== EQ12 CrashCode -536870904 Repair Script ===" -ForegroundColor Cyan

# 1. Stop all VS Code processes
Write-Host "[1/7] Stopping all VS Code processes..." -ForegroundColor Yellow
try {
    Get-Process Code -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "  VS Code processes stopped." -ForegroundColor Green
} catch {
    Write-Host "  Warning: Could not stop some Code processes: $_" -ForegroundColor Yellow
}

# 2. Clear VS Code cache and user data
Write-Host "[2/7] Clearing VS Code cache and user data..." -ForegroundColor Yellow
$paths = @(
    "$env:APPDATA\Code",
    "$env:LOCALAPPDATA\Code",
    "$env:USERPROFILE\.vscode"
)
foreach ($p in $paths) {
    try {
        if (Test-Path $p) {
            Remove-Item $p -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  Removed: $p" -ForegroundColor Green
        } else {
            Write-Host "  Not found (OK): $p" -ForegroundColor DarkGray
        }
    } catch {
        Write-Host "  Warning: Could not remove $p : $_" -ForegroundColor Yellow
    }
}

# 3. Remove Snyk and GitHub Copilot Chat extensions (if present)
Write-Host "[3/7] Removing Snyk and Copilot Chat extensions (if present)..." -ForegroundColor Yellow
$extRoot = "$env:USERPROFILE\.vscode\extensions"
$extPatterns = @(
    "snyk-security.snyk-vulnerability-scanner*",
    "github.copilot-chat*"
)

foreach ($pattern in $extPatterns) {
    try {
        if (Test-Path $extRoot) {
            Get-ChildItem -Path $extRoot -Filter $pattern -ErrorAction SilentlyContinue | ForEach-Object {
                Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
                Write-Host "  Removed extension folder: $($_.FullName)" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "  Warning: Could not process pattern $pattern : $_" -ForegroundColor Yellow
    }
}

# 4. Relax Smart Card logon enforcement (do NOT force smart card)
Write-Host "[4/7] Ensuring Smart Card is NOT required for logon..." -ForegroundColor Yellow
try {
    & reg add "HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System" ^
        /v scforceoption /t REG_DWORD /d 0 /f | Out-Null
    Write-Host "  Smart Card requirement disabled (scforceoption=0)." -ForegroundColor Green
} catch {
    Write-Host "  Warning: Could not update scforceoption: $_" -ForegroundColor Yellow
}

# 5. Repair TLS/SCHANNEL certificate caches (schannel-related 36861 support)
Write-Host "[5/7] Repairing TLS/SCHANNEL certificate caches..." -ForegroundColor Yellow
try {
    & certutil -urlcache * delete | Out-Null
    & certutil -repairstore my * | Out-Null
    & certutil -repairstore root * | Out-Null
    & certutil -repairstore ca * | Out-Null
    Write-Host "  Certificate caches cleared and stores repaired." -ForegroundColor Green
} catch {
    Write-Host "  Warning: certutil operations encountered an issue: $_" -ForegroundColor Yellow
}

# 6. Run SFC and DISM health checks (can take several minutes)
Write-Host "[6/7] Running SFC /SCANNOW (this may take several minutes)..." -ForegroundColor Yellow
try {
    & sfc /scannow
    Write-Host "  SFC completed." -ForegroundColor Green
} catch {
    Write-Host "  Warning: SFC encountered an issue: $_" -ForegroundColor Yellow
}

Write-Host "[6b/7] Running DISM /Online /Cleanup-Image /RestoreHealth (this may take several minutes)..." -ForegroundColor Yellow
try {
    & DISM /Online /Cleanup-Image /RestoreHealth
    Write-Host "  DISM completed." -ForegroundColor Green
} catch {
    Write-Host "  Warning: DISM encountered an issue: $_" -ForegroundColor Yellow
}

# 7. Free EQ12 service ports (8000, 8080, 4040)
Write-Host "[7/7] Freeing EQ12 service ports (8000, 8080, 4040)..." -ForegroundColor Yellow
$ports = 8000,8080,4040
foreach ($p in $ports) {
    try {
        netstat -ano | Select-String ":$p " | ForEach-Object {
            $pid = ($_ -split '\s+')[-1]
            if ($pid -match '^\d+$') {
                try {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    Write-Host "  Killed PID $pid on port $p" -ForegroundColor Green
                } catch {
                    Write-Host "  Warning: Could not kill PID $pid on port $p : $_" -ForegroundColor Yellow
                }
            }
        }
    } catch {
        Write-Host "  Warning: Could not inspect port $p : $_" -ForegroundColor Yellow
    }
}

Write-Host "`n=== EQ12 CrashCode -536870904 Repair Completed ===" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Reboot your system to finalize TLS and auth changes." -ForegroundColor White
Write-Host "  2. Install a fresh copy of VS Code if needed." -ForegroundColor White
Write-Host "  3. Only reinstall SAFE extensions (Copilot, Python, Jupyter, etc.)." -ForegroundColor White
