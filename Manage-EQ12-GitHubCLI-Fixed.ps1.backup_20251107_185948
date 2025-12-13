# EQ12 GitHub CLI Manager - Task Wrapper (Fixed)
# Simple wrapper for EQ12 tasks.json integration

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('Install', 'Test', 'Status', 'Configure', 'Download')]
    [string]$Action = 'Install',

    [switch]$GUI,
    [switch]$VerboseOutput
)

$EQ12Root = "C:\EQ12"
$InstallerScript = Join-Path $EQ12Root "Install-EQ12-GitHubCLI.ps1"

function Write-EQ12Status {
    param([string]$Message, [string]$Icon = "[*]")
    Write-Host "$Icon $Message" -ForegroundColor Cyan
}

function Get-GitHubCLIStatus {
    try {
        $version = & gh --version 2>$null | Select-Object -First 1
        if ($LASTEXITCODE -eq 0) {
            $null = & gh auth status 2>$null
            $isAuthenticated = ($LASTEXITCODE -eq 0)
            return @{
                installed     = $true
                version       = $version
                authenticated = $isAuthenticated
            }
        }
        else {
            return @{
                installed     = $false
                version       = $null
                authenticated = $false
            }
        }
    }
    catch {
        return @{
            installed     = $false
            version       = $null
            authenticated = $false
        }
    }
}

function Get-InstallerDownloadUrl {
    return "https://github.com/cli/cli/releases/download/v2.81.0/gh_2.81.0_windows_amd64.msi"
}

# Main execution
Write-EQ12Status "EQ12 GitHub CLI Manager - Action: $Action"

switch ($Action.ToLower()) {
    'status' {
        Write-EQ12Status "Checking GitHub CLI status..." "[INFO]"

        $status = Get-GitHubCLIStatus

        Write-Host "`nGitHub CLI Status Report:" -ForegroundColor Yellow
        Write-Host "Installed: $(if ($status.installed) { '[YES]' } else { '[NO]' })"

        if ($status.installed) {
            Write-Host "Version: $($status.version)"
            Write-Host "Authenticated: $(if ($status.authenticated) { '[YES]' } else { '[NO]' })"
        }

        $installerPath = Join-Path $env:USERPROFILE "Downloads\gh_2.81.0_windows_amd64.msi"
        $installerExists = Test-Path $installerPath
        Write-Host "Installer Available: $(if ($installerExists) { '[YES]' } else { '[NO]' })"

        if (-not $installerExists) {
            Write-Host "Download URL: $(Get-InstallerDownloadUrl)" -ForegroundColor Blue
        }
    }

    'download' {
        Write-EQ12Status "Downloading GitHub CLI installer..." "[DOWNLOAD]"

        $downloadUrl = Get-InstallerDownloadUrl
        $downloadPath = Join-Path $env:USERPROFILE "Downloads\gh_2.81.0_windows_amd64.msi"

        try {
            Write-Host "Downloading from: $downloadUrl"
            Write-Host "Saving to: $downloadPath"

            Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath -UseBasicParsing

            if (Test-Path $downloadPath) {
                $fileSize = (Get-Item $downloadPath).Length / 1MB
                Write-Host "[SUCCESS] Download completed ($([math]::Round($fileSize, 1)) MB)" -ForegroundColor Green
            }
            else {
                Write-Host "[ERROR] Download failed - file not found" -ForegroundColor Red
                exit 1
            }
        }
        catch {
            Write-Host "[ERROR] Download failed: $($_.Exception.Message)" -ForegroundColor Red
            exit 1
        }
    }

    'test' {
        Write-EQ12Status "Running GitHub CLI functionality tests..." "[TEST]"

        if (-not (Test-Path $InstallerScript)) {
            Write-Host "[ERROR] Installer script not found: $InstallerScript" -ForegroundColor Red
            exit 1
        }

        & powershell.exe -ExecutionPolicy Bypass -File $InstallerScript -TestOnly
        exit $LASTEXITCODE
    }

    'configure' {
        Write-EQ12Status "Configuring GitHub CLI for EQ12..." "[CONFIG]"

        $status = Get-GitHubCLIStatus

        if (-not $status.installed) {
            Write-Host "[ERROR] GitHub CLI not installed. Run with -Action Install first." -ForegroundColor Red
            exit 1
        }

        # Check for token file
        $tokenFile = Join-Path $EQ12Root "tokens\github_token.txt"
        if (-not (Test-Path $tokenFile)) {
            Write-Host "[ERROR] GitHub token file not found: $tokenFile" -ForegroundColor Red
            Write-Host "Please create this file with your GitHub personal access token." -ForegroundColor Yellow
            exit 1
        }

        # Run configuration only
        & powershell.exe -ExecutionPolicy Bypass -File $InstallerScript -TestOnly
    }

    'install' {
        Write-EQ12Status "Starting GitHub CLI installation process..." "[INSTALL]"

        if (-not (Test-Path $InstallerScript)) {
            Write-Host "[ERROR] Installer script not found: $InstallerScript" -ForegroundColor Red
            exit 1
        }

        # Check if installer MSI exists
        $installerPath = Join-Path $env:USERPROFILE "Downloads\gh_2.81.0_windows_amd64.msi"
        if (-not (Test-Path $installerPath)) {
            Write-Host "[WARNING] Installer MSI not found. Downloading..." -ForegroundColor Yellow

            # Download first
            & $MyInvocation.MyCommand.Path -Action Download

            if ($LASTEXITCODE -ne 0) {
                Write-Host "[ERROR] Download failed. Cannot proceed with installation." -ForegroundColor Red
                exit 1
            }
        }

        # Run installation
        $arguments = @()
        if ($GUI) { $arguments += "-GUI" }
        if ($VerboseOutput) { $arguments += "-Verbose" }

        & powershell.exe -ExecutionPolicy Bypass -File $InstallerScript @arguments
        exit $LASTEXITCODE
    }

    default {
        Write-Host "[ERROR] Unknown action: $Action" -ForegroundColor Red
        Write-Host "Valid actions: Install, Test, Status, Configure, Download" -ForegroundColor Yellow
        exit 1
    }
}

Write-EQ12Status "GitHub CLI Manager action completed: $Action" "[COMPLETE]"
