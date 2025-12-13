#!/usr/bin/env bash
# EQ12 patch: Git Bash helper

eq12-dashboard() {
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:/EQ12/scripts/eq12_build_dashboard.ps1
}

eq12-elite() {
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:/EQ12/scripts/eq12_market_sports_job_runner.ps1 --dry-run
}

eq12-py() {
  ./venv/Scripts/python.exe "$@"
}

# TODO: add pytest unit test for schema
#!/usr/bin/env bash
# EQ12 patch: Git Bash helper to run PowerShell EQ12 scripts and venv
set -euo pipefail

# Activate venv if present
if [ -f "./venv/bin/activate" ]; then
  echo "Activating venv"
  source ./venv/bin/activate
fi

# Wrapper to run a named PS script with args
run_ps() {
  local script="$1"; shift
  if command -v pwsh >/dev/null 2>&1; then
    pwsh -NoProfile -ExecutionPolicy Bypass -File "$script" "$@"
  else
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$script" "$@"
  fi
}

if [ "$#" -gt 0 ]; then
  run_ps "$@"
else
  echo "Usage: bash_helper.sh <ps1-script> [args...]"
fi
