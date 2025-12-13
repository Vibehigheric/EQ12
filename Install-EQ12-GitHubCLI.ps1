# EQ12 GitHub CLI Installer - PowerShell Version
# Professional GitHub CLI installation for EQ12 automation stack

[CmdletBinding()]
param(
    [string]$EQ12Root = "C:\EQ12",
    [string]$TokenFile = "github_token.txt",
    [switch]$GUI,
    [switch]$TestOnly,
    [switch]$Verbose
)

# Configure logging
$LogPath = Join-Path $EQ12Root "logs\github_cli_install_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$null = New-Item -Path (Split-Path $LogPath) -ItemType Directory -Force

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    Write-Host $logEntry
    Add-Content -Path $LogPath -Value $logEntry
}

function Test-AdminPrivileges {
    try {
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
        return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    }
    catch {
        return $false
    }
}

function Test-GitHubCLIInstalled {
    try {
        $null = & gh --version 2>$null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Install-GitHubCLI {
    param([bool]$Silent = $true)

    $installerPath = Join-Path $env:USERPROFILE "Downloads\gh_2.81.0_windows_amd64.msi"

    if (-not (Test-Path $installerPath)) {
        Write-EQ12Log "ERROR: Installer not found at $installerPath" "ERROR"
        return $false
    }

    try {
        Write-EQ12Log "Installing GitHub CLI from $installerPath"

        if ($Silent) {
            $arguments = "/i `"$installerPath`" /qn /norestart"
        }
        else {
            $arguments = "/i `"$installerPath`""
        }

        Write-EQ12Log "Running: msiexec.exe $arguments"

        $process = Start-Process -FilePath "msiexec.exe" -ArgumentList $arguments -Wait -PassThru -NoNewWindow

        if ($process.ExitCode -eq 0) {
            Write-EQ12Log "GitHub CLI installation completed successfully"

            # Verify installation
            Start-Sleep -Seconds 3  # Give it a moment to register

            if (Test-GitHubCLIInstalled) {
                $version = & gh --version 2>$null | Select-Object -First 1
                Write-EQ12Log "Installation verified: $version"
                return $true
            }
            else {
                Write-EQ12Log "Installation completed but verification failed" "ERROR"
                return $false
            }
        }
        else {
            Write-EQ12Log "Installation failed with exit code: $($process.ExitCode)" "ERROR"
            return $false
        }
    }
    catch {
        Write-EQ12Log "Installation error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Set-GitHubAuthentication {
    param([string]$TokenFile)

    $tokenPath = Join-Path $EQ12Root "tokens\$TokenFile"

    if (-not (Test-Path $tokenPath)) {
        Write-EQ12Log "ERROR: GitHub token file not found: $tokenPath" "ERROR"
        return $false
    }

    try {
        $token = Get-Content -Path $tokenPath -Raw | ForEach-Object { $_.Trim() }

        if ([string]::IsNullOrEmpty($token)) {
            Write-EQ12Log "ERROR: GitHub token file is empty" "ERROR"
            return $false
        }

        Write-EQ12Log "Configuring GitHub CLI authentication..."

        # Login with token using stdin
        $token | & gh auth login --with-token

        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "GitHub CLI authentication successful"

            # Verify authentication
            $null = & gh auth status 2>$null

            if ($LASTEXITCODE -eq 0) {
                Write-EQ12Log "Authentication verified successfully"
                return $true
            }
            else {
                Write-EQ12Log "Authentication completed but verification failed" "ERROR"
                return $false
            }
        }
        else {
            Write-EQ12Log "Authentication failed" "ERROR"
            return $false
        }
    }
    catch {
        Write-EQ12Log "Authentication error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Set-EQ12GitConfig {
    try {
        Write-EQ12Log "Configuring Git settings for EQ12 stack..."

        $gitConfigs = @{
            "user.name"          = "EQ12-Automation"
            "user.email"         = "eq12@automation.local"
            "init.defaultBranch" = "main"
            "core.autocrlf"      = "true"
            "push.default"       = "simple"
            "pull.rebase"        = "false"
        }

        foreach ($config in $gitConfigs.GetEnumerator()) {
            & git config --global $config.Key $config.Value

            if ($LASTEXITCODE -eq 0) {
                Write-EQ12Log "Git config set: $($config.Key) = $($config.Value)"
            }
            else {
                Write-EQ12Log "Failed to set Git config: $($config.Key)" "ERROR"
                return $false
            }
        }

        Write-EQ12Log "Git configuration completed successfully"
        return $true
    }
    catch {
        Write-EQ12Log "Git configuration error: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-GitHubIntegration {
    Write-EQ12Log "Running GitHub CLI functionality tests..."

    $tests = @{}

    # Test 1: CLI Version
    try {
        $null = & gh --version 2>$null
        $tests["cli_version"] = ($LASTEXITCODE -eq 0)
    }
    catch {
        $tests["cli_version"] = $false
    }

    # Test 2: Authentication Status
    try {
        $null = & gh auth status 2>$null
        $tests["auth_status"] = ($LASTEXITCODE -eq 0)
    }
    catch {
        $tests["auth_status"] = $false
    }

    # Test 3: API Connectivity
    try {
        $null = & gh api user 2>$null
        $tests["api_connectivity"] = ($LASTEXITCODE -eq 0)
    }
    catch {
        $tests["api_connectivity"] = $false
    }

    # Test 4: Repository Access
    try {
        $null = & gh repo list --limit 1 2>$null
        $tests["repo_access"] = ($LASTEXITCODE -eq 0)
    }
    catch {
        $tests["repo_access"] = $false
    }

    return $tests
}

function New-InstallationReport {
    param(
        [bool]$InstallSuccess,
        [bool]$AuthSuccess,
        [bool]$GitConfigSuccess,
        [hashtable]$TestResults
    )

    $report = @{
        timestamp           = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        installer_version   = "gh_2.81.0_windows_amd64.msi"
        eq12_root           = $EQ12Root
        installation        = @{
            success = $InstallSuccess
            method  = "MSI Silent Install"
        }
        authentication      = @{
            success = $AuthSuccess
            method  = "Token-based"
        }
        git_configuration   = @{
            success = $GitConfigSuccess
        }
        functionality_tests = $TestResults
        overall_success     = $InstallSuccess -and $AuthSuccess -and $GitConfigSuccess -and ($TestResults.Values | ForEach-Object { $_ } | Measure-Object -Sum).Sum -eq $TestResults.Count
    }

    return $report
}

function Save-InstallationReport {
    param([hashtable]$Report)

    $reportFile = Join-Path $EQ12Root "logs\github_cli_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

    try {
        $Report | ConvertTo-Json -Depth 10 | Set-Content -Path $reportFile
        Write-EQ12Log "Installation report saved: $reportFile"
    }
    catch {
        Write-EQ12Log "Failed to save installation report: $($_.Exception.Message)" "ERROR"
    }
}

# Main execution
Write-EQ12Log "🚀 EQ12 GitHub CLI Installation Process Starting"
Write-EQ12Log "=" * 60

# Handle test-only mode
if ($TestOnly) {
    Write-EQ12Log "Running functionality tests only..."

    $tests = Test-GitHubIntegration

    Write-Host "`n🧪 GitHub CLI Functionality Tests:"
    foreach ($test in $tests.GetEnumerator()) {
        $status = if ($test.Value) { "✅ PASS" } else { "❌ FAIL" }
        Write-Host "  $($test.Key): $status"
    }

    $overall = ($tests.Values | Where-Object { -not $_ }).Count -eq 0
    $overallStatus = if ($overall) { "✅ ALL TESTS PASSED" } else { "❌ SOME TESTS FAILED" }
    Write-Host "`nOverall: $overallStatus"

    exit $(if ($overall) { 0 } else { 1 })
}

# Check prerequisites
Write-EQ12Log "Checking prerequisites..."

$isAdmin = Test-AdminPrivileges
$alreadyInstalled = Test-GitHubCLIInstalled
$installerExists = Test-Path (Join-Path $env:USERPROFILE "Downloads\gh_2.81.0_windows_amd64.msi")

Write-EQ12Log "Admin privileges: $isAdmin"
Write-EQ12Log "Already installed: $alreadyInstalled"
Write-EQ12Log "Installer exists: $installerExists"

if (-not $installerExists) {
    Write-EQ12Log "ERROR: Installer not found in Downloads folder" "ERROR"
    Write-Host "❌ Installer not found: ~\Downloads\gh_2.81.0_windows_amd64.msi"
    exit 1
}

if (-not $isAdmin) {
    Write-EQ12Log "WARNING: Not running as administrator - installation may fail" "WARN"
}

# Install GitHub CLI
if ($alreadyInstalled) {
    Write-EQ12Log "GitHub CLI already installed, skipping installation..."
    $installSuccess = $true
}
else {
    $installSuccess = Install-GitHubCLI -Silent (-not $GUI)
}

# Setup authentication
$authSuccess = Set-GitHubAuthentication -TokenFile $TokenFile

# Configure Git settings
$gitConfigSuccess = Set-EQ12GitConfig

# Test functionality
$testResults = Test-GitHubIntegration

# Generate and save report
$report = New-InstallationReport -InstallSuccess $installSuccess -AuthSuccess $authSuccess -GitConfigSuccess $gitConfigSuccess -TestResults $testResults
Save-InstallationReport -Report $report

# Display summary
Write-Host "`n🎯 EQ12 GitHub CLI Installation Summary"
Write-Host "=" * 50

$overallSuccess = $report.overall_success
$successIcon = if ($overallSuccess) { "✅" } else { "❌" }

Write-Host "Overall Success: $successIcon $(if ($overallSuccess) { 'YES' } else { 'NO' })"
Write-Host "Installation: $(if ($report.installation.success) { '✅' } else { '❌' })"
Write-Host "Authentication: $(if ($report.authentication.success) { '✅' } else { '❌' })"
Write-Host "Git Config: $(if ($report.git_configuration.success) { '✅' } else { '❌' })"

Write-Host "`nFunctionality Tests:"
foreach ($test in $report.functionality_tests.GetEnumerator()) {
    $status = if ($test.Value) { "✅" } else { "❌" }
    Write-Host "  $status $($test.Key)"
}

Write-Host "`nInstallation completed: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

if ($overallSuccess) {
    Write-EQ12Log "✅ GitHub CLI installation and setup completed successfully!"
}
else {
    Write-EQ12Log "⚠️ GitHub CLI installation completed with issues" "WARN"
}

exit $(if ($overallSuccess) { 0 } else { 1 })
