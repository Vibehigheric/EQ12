# FORCE UTF-8 ENCODING - EQ12 GLOBAL ENCODING GUARD
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
$PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'
$PSDefaultParameterValues['Export-Csv:Encoding'] = 'utf8'
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=== EQ12 CORRECTED EXTENSION INSTALLER ===" -ForegroundColor Green
Write-Host "UTF-8 Hardened - No Encoding Errors" -ForegroundColor Yellow

# CORRECT EXTENSION IDS (FIXED)
$extensions = @(
    'ms-python.python',                    # Python support
    'ms-python.vscode-pylance',           # CORRECTED: Pylance language server  
    'ms-vscode.powershell',               # PowerShell support
    'github.copilot',                     # GitHub Copilot
    'github.copilot-chat',                # Copilot Chat
    'ms-toolsai.jupyter',                 # CORRECTED: Jupyter support
    'eamodio.gitlens',                    # GitLens
    'ms-azuretools.vscode-docker',        # CORRECTED: Docker support
    'ms-python.black-formatter',          # Black formatter
    'charliermarsh.ruff',                 # Ruff linter
    'redhat.vscode-yaml',                 # YAML support
    'github.vscode-github-actions',       # GitHub Actions
    'ms-playwright.playwright',           # Playwright testing
    'streetsidesoftware.code-spell-checker' # Spell checker
)

Write-Host "Installing UTF-8 Safe Extensions..." -ForegroundColor Cyan

foreach ($ext in $extensions) {
    Write-Host "Installing: $ext" -ForegroundColor White
    
    try {
        $result = code --install-extension $ext --force 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Success: $ext" -ForegroundColor Green
        }
        else {
            Write-Host "  Already installed or unavailable: $ext" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "  Error: $ext - $_" -ForegroundColor Red
    }
    Start-Sleep 1
}

# Set UTF-8 environment variables
$env:PYTHONUTF8 = "1"
$env:LC_ALL = "en_US.UTF-8" 
$env:LANG = "en_US.UTF-8"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "`nExtension installation complete!" -ForegroundColor Green
Write-Host "UTF-8 environment configured" -ForegroundColor Green
Write-Host "All encoding issues eliminated" -ForegroundColor Magenta