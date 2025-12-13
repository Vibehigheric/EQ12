#!/usr/bin/env bash
# EQ12 patch: Git Bash wrapper to invoke PowerShell eq12-elite-run
# Use pwsh in Codespaces (Linux) or powershell.exe on Windows

LOGS=${EQ12_LOGS:-/workspaces/EQ12/logs}
mkdir -p "$LOGS"

if command -v pwsh >/dev/null 2>&1; then
  echo "Using pwsh"
  pwsh -NoProfile -ExecutionPolicy Bypass -File "/workspaces/EQ12/eq12-elite-run.ps1" -OutJson "$LOGS/scraper_output.json"
else
  echo "Using Windows PowerShell"
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\EQ12\eq12-elite-run.ps1" -OutJson "$LOGS/scraper_output.json"
fi

echo "eq12-elite-run.sh complete"