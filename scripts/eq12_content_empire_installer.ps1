# EQ12 Content Empire Installer
param([switch]$AllComponents)

Write-Host "=== EQ12 Content Empire Installation ===" -ForegroundColor Green
Write-Host "Target: 273750/year automated revenue" -ForegroundColor Yellow

# Core extensions
$extensions = @(
    'ms-python.python',
    'ms-vscode.powershell', 
    'GitHub.copilot',
    'GitHub.copilot-chat',
    'ms-toolsai.jupyter',
    'eamodio.gitlens',
    'ms-python.black-formatter',
    'charliermarsh.ruff'
)

Write-Host "Installing extensions..." -ForegroundColor Cyan
foreach ($ext in $extensions) {
    Write-Host "Installing: $ext" -ForegroundColor White
    code --install-extension $ext --force
}

# Deploy settings
$settingsPath = "$env:APPDATA\Code\User\settings.json"
$settings = @{
    "python.defaultInterpreterPath"   = "python"
    "github.copilot.enable"           = $true
    "editor.formatOnSave"             = $true
    "terminal.integrated.env.windows" = @{
        "CONTENT_EMPIRE_MODE"  = "ACTIVATED"
        "REVENUE_TARGET_DAILY" = "750"
    }
}

Write-Host "Deploying settings..." -ForegroundColor Cyan
$settings | ConvertTo-Json -Depth 10 | Out-File -FilePath $settingsPath -Encoding UTF8 -Force

# Set environment variables
[Environment]::SetEnvironmentVariable("CONTENT_EMPIRE_MODE", "ACTIVATED", "User")
[Environment]::SetEnvironmentVariable("REVENUE_TARGET_DAILY", "750", "User")

Write-Host "Content Empire installation complete!" -ForegroundColor Green
Write-Host "Restart VS Code to activate features." -ForegroundColor Yellow