#!/usr/bin/env powershell
# VS Code Extensions Recovery Installer
Write-Host "Installing VS Code extensions..." -ForegroundColor Green

$extensions = @(
    "ms-python.python",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "GitHub.copilot",
    "ms-vscode.powershell",
    "ms-toolsai.jupyter",
    "redhat.vscode-yaml",
    "ms-vscode.vscode-json"
)

foreach ($ext in $extensions) {
    Write-Host "Installing $ext..." -ForegroundColor Yellow
    code --install-extension $ext --force
}

Write-Host "VS Code extensions installed!" -ForegroundColor Green
