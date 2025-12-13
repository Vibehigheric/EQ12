# fix-eq12-everything.ps1
#Requires -RunAsAdministrator

Write-Host "=== EQ12 FULL SYSTEM STABILIZATION SCRIPT ===" -ForegroundColor Cyan

# 1. Reset VS Code
Write-Host "[1/5] Resetting VS Code..." -ForegroundColor Yellow
Get-Process -Name Code -ErrorAction SilentlyContinue | Stop-Process -Force
Remove-Item "$env:APPDATA\Code" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\Code" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$env:USERPROFILE\.vscode" -Recurse -Force -ErrorAction SilentlyContinue

# 2. Remove Copilot Chat
Write-Host "[2/5] Removing GitHub Copilot Chat..." -ForegroundColor Yellow
Remove-Item "$env:USERPROFILE\.vscode\extensions\github.copilot-chat*" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Kill ports 8000,8080,4040
Write-Host "[3/5] Clearing blocked ports..." -ForegroundColor Yellow
foreach ($port in 8000,8080,4040) {
  netstat -ano | Select-String ":$port " | ForEach-Object {
    $pid = ($_ -split '\s+')[-1]
    if ($pid -match '^\d+$') {
      Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
  }
}

# 4. Run full EQ12 repair
Write-Host "[4/5] Running EQ12 full TLS/SSL/system repair..." -ForegroundColor Yellow
Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','C:\EQ12\scripts\eq12_full_system_repair.ps1','-WorkspaceRoot','C:\EQ12'

# 5. Restart EQ12 services
Write-Host "[5/5] Restarting EQ12 services..." -ForegroundColor Yellow
try { eq12-recycle } catch {}
try { eq12-launcher } catch {}

Write-Host "`n=== COMPLETE ===" -ForegroundColor Green
