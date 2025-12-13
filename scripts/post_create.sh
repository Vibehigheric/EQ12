#!/usr/bin/env bash
# EQ12 patch: post_create.sh for Codespaces (Linux)
set -e

# Ensure logs dir
mkdir -p "$EQ12_LOGS"

# Load dotfiles if present
if [ -d "$HOME/.dotfiles" ]; then
  if [ -f "$HOME/.dotfiles/install.sh" ]; then
    echo "Running dotfiles install"
    bash "$HOME/.dotfiles/install.sh" || true
  fi
fi

# Ensure GNUPG home
if [ -n "$GNUPGHOME" ]; then
  mkdir -p "$GNUPGHOME"
  chmod 700 "$GNUPGHOME"
fi

# Install Python requirements (user scope)
if [ -f "/workspaces/EQ12/requirements.txt" ]; then
  echo "Installing Python requirements"
  pip install --user -r /workspaces/EQ12/requirements.txt || true
fi

# Install Playwright and browsers
if command -v playwright >/dev/null 2>&1; then
  echo "Installing Playwright browsers"
  playwright install chromium firefox || true
else
  echo "Installing Playwright package"
  pip install --user playwright || true
  python -m playwright install chromium firefox || true
fi

# Install stealth libs quietly
pip install --user undetected-chromedriver playwright-stealth fake-useragent || true

# Install VS Code extensions via helper script
if [ -f "/workspaces/EQ12/scripts/install_extensions.sh" ]; then
  bash /workspaces/EQ12/scripts/install_extensions.sh || true
fi

# Run the devcontainer post_create.ps1 fallback if present
if [ -f "/workspaces/EQ12/.devcontainer/post_create.ps1" ]; then
  echo "Running PowerShell post-create fallback"
  pwsh -NoProfile -ExecutionPolicy Bypass -File "/workspaces/EQ12/.devcontainer/post_create.ps1" || true
fi

echo "EQ12 post-create script completed"