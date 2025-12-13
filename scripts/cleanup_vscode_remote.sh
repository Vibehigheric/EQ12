#!/bin/bash
# ================================
# EQ12 VS Code Remote Cleanup Script
# Purges corrupted VS Code server files
# ================================

set -e

echo "🧹 EQ12 VS Code Remote Cleanup Script"
echo "======================================"

# Remove VS Code server files
if [ -d "$HOME/.vscode-server" ]; then
    echo "🗑️  Removing .vscode-server..."
    rm -rf "$HOME/.vscode-server"
    echo "   ✅ Removed"
else
    echo "   ℹ️  .vscode-server not found"
fi

# Remove VS Code remote containers
if [ -d "$HOME/.vscode-remote-containers" ]; then
    echo "🗑️  Removing .vscode-remote-containers..."
    rm -rf "$HOME/.vscode-remote-containers"
    echo "   ✅ Removed"
else
    echo "   ℹ️  .vscode-remote-containers not found"
fi

# Remove VS Code local storage
if [ -d "$HOME/.vscode" ]; then
    echo "🗑️  Removing .vscode local storage..."
    rm -rf "$HOME/.vscode"
    echo "   ✅ Removed"
else
    echo "   ℹ️  .vscode not found"
fi

# Remove VS Code CLI cache
if [ -d "$HOME/.vscode-cli" ]; then
    echo "🗑️  Removing .vscode-cli..."
    rm -rf "$HOME/.vscode-cli"
    echo "   ✅ Removed"
fi

# Clean npm cache (can cause issues)
if command -v npm &> /dev/null; then
    echo "🧹 Cleaning npm cache..."
    npm cache clean --force 2>/dev/null || true
    echo "   ✅ Cleaned"
fi

# Clean Python cache
echo "🧹 Cleaning Python cache..."
find /workspaces/EQ12 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /workspaces/EQ12 -type f -name "*.pyc" -delete 2>/dev/null || true
find /workspaces/EQ12 -type f -name "*.pyo" -delete 2>/dev/null || true
echo "   ✅ Cleaned"

echo ""
echo "✅ VS Code Remote cleanup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Exit WSL: exit"
echo "2. Shutdown WSL completely: wsl --shutdown (from Windows PowerShell)"
echo "3. Reopen VS Code"
echo "4. Connect to WSL (VS Code will reinstall server automatically)"
echo ""
