#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Firefox Extension Build and Distribution System
.DESCRIPTION
    Builds Firefox extension packages for both AMO distribution and self-hosting
.PARAMETER BuildType
    Type of build: AMO (public) or SelfHosted (private)
.PARAMETER Version
    Version number for the extension (e.g., "1.0.1")
.PARAMETER Sign
    Whether to create signed package (requires Mozilla signing)
.PARAMETER Deploy
    Whether to deploy to hosting after build
.EXAMPLE
    .\eq12_firefox_build.ps1 -BuildType AMO -Version "1.0.0"
    Build AMO-ready package
.EXAMPLE
    .\eq12_firefox_build.ps1 -BuildType SelfHosted -Version "1.0.1" -Sign -Deploy
    Build, sign, and deploy self-hosted package
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("AMO", "SelfHosted", "Both")]
    [string]$BuildType,

    [Parameter(Mandatory = $true)]
    [string]$Version,

    [Parameter(Mandatory = $false)]
    [switch]$Sign,

    [Parameter(Mandatory = $false)]
    [switch]$Deploy,

    [Parameter(Mandatory = $false)]
    [string]$OutputDir = "C:\EQ12\firefox_builds"
)

# Set up logging
$LogPath = "C:\EQ12\logs"
if (-not (Test-Path $LogPath)) {
    New-Item -Path $LogPath -ItemType Directory -Force | Out-Null
}

$LogFile = Join-Path $LogPath "firefox_build.log"

function Write-Log {
    param($Message, $Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Level: $Message"
    Write-Output $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Test-Prerequisites {
    Write-Log "Checking build prerequisites..."

    $Issues = @()

    # Check if source directory exists
    $SourceDir = "C:\EQ12\firefox_extension_eq12"
    if (-not (Test-Path $SourceDir)) {
        $Issues += "Source directory not found: $SourceDir"
    }

    # Check required files
    $RequiredFiles = @(
        "manifest.json",
        "popup.html",
        "popup.js",
        "content.js",
        "background.js",
        "content.css"
    )

    foreach ($File in $RequiredFiles) {
        $FilePath = Join-Path $SourceDir $File
        if (-not (Test-Path $FilePath)) {
            $Issues += "Required file missing: $File"
        }
    }

    # Check if web-ext is available (for validation)
    try {
        $WebExtVersion = web-ext --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "web-ext found: $WebExtVersion"
        } else {
            Write-Log "web-ext not found, will skip validation" "WARN"
        }
    } catch {
        Write-Log "web-ext not available, will skip validation" "WARN"
    }

    return $Issues
}

function Update-ManifestVersion {
    param($ManifestPath, $Version)

    Write-Log "Updating manifest version to $Version..."

    try {
        $ManifestContent = Get-Content $ManifestPath -Raw | ConvertFrom-Json
        $ManifestContent.version = $Version

        # Pretty-print JSON
        $UpdatedContent = $ManifestContent | ConvertTo-Json -Depth 10 -Compress:$false
        $UpdatedContent | Set-Content $ManifestPath -Encoding UTF8

        Write-Log "Manifest updated successfully"
    } catch {
        throw "Failed to update manifest version: $($_.Exception.Message)"
    }
}

function Build-AMOPackage {
    param($SourceDir, $OutputDir, $Version)

    Write-Log "Building AMO package..."

    # Create build directory
    $BuildDir = Join-Path $OutputDir "amo_build"
    if (Test-Path $BuildDir) {
        Remove-Item $BuildDir -Recurse -Force
    }
    New-Item -Path $BuildDir -ItemType Directory -Force | Out-Null

    # Copy source files (excluding self-hosted specific files)
    $ExcludeFiles = @("manifest_self_hosted.json", "firefox_updates.json", "*.log", "*.tmp")

    Get-ChildItem $SourceDir -Recurse | Where-Object {
        $Exclude = $false
        foreach ($Pattern in $ExcludeFiles) {
            if ($_.Name -like $Pattern) {
                $Exclude = $true
                break
            }
        }
        -not $Exclude
    } | Copy-Item -Destination {
        $RelativePath = $_.FullName.Substring($SourceDir.Length + 1)
        $DestPath = Join-Path $BuildDir $RelativePath
        $DestDir = Split-Path $DestPath -Parent
        if (-not (Test-Path $DestDir)) {
            New-Item -Path $DestDir -ItemType Directory -Force | Out-Null
        }
        $DestPath
    }

    # Update version in manifest
    $ManifestPath = Join-Path $BuildDir "manifest.json"
    Update-ManifestVersion $ManifestPath $Version

    # Validate with web-ext if available
    try {
        $ValidationResult = web-ext lint --source-dir $BuildDir 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Extension validation passed"
        } else {
            Write-Log "Validation warnings: $ValidationResult" "WARN"
        }
    } catch {
        Write-Log "Skipping validation (web-ext not available)" "WARN"
    }

    # Create XPI package
    $XpiPath = Join-Path $OutputDir "eq12_data_pusher_amo_v$Version.xpi"

    try {
        # Use PowerShell compression
        Compress-Archive -Path "$BuildDir\*" -DestinationPath $XpiPath -Force
        Write-Log "AMO package created: $XpiPath"

        # Get package size
        $FileSize = (Get-Item $XpiPath).Length
        Write-Log "Package size: $([math]::Round($FileSize / 1KB, 2)) KB"

        return $XpiPath
    } catch {
        throw "Failed to create XPI package: $($_.Exception.Message)"
    }
}

function Build-SelfHostedPackage {
    param($SourceDir, $OutputDir, $Version)

    Write-Log "Building self-hosted package..."

    # Create build directory
    $BuildDir = Join-Path $OutputDir "self_hosted_build"
    if (Test-Path $BuildDir) {
        Remove-Item $BuildDir -Recurse -Force
    }
    New-Item -Path $BuildDir -ItemType Directory -Force | Out-Null

    # Copy all source files
    Copy-Item "$SourceDir\*" $BuildDir -Recurse -Force

    # Use self-hosted manifest
    $SelfHostedManifest = Join-Path $BuildDir "manifest_self_hosted.json"
    $MainManifest = Join-Path $BuildDir "manifest.json"

    if (Test-Path $SelfHostedManifest) {
        Copy-Item $SelfHostedManifest $MainManifest -Force
        Remove-Item $SelfHostedManifest
    }

    # Update version
    Update-ManifestVersion $MainManifest $Version

    # Update updates.json
    $UpdatesPath = Join-Path $BuildDir "firefox_updates.json"
    if (Test-Path $UpdatesPath) {
        try {
            $UpdatesContent = Get-Content $UpdatesPath -Raw | ConvertFrom-Json

            # Add new version entry
            $NewUpdate = @{
                version                   = $Version
                update_link               = "https://yourdomain.com/extensions/eq12_data_pusher_v$Version.xpi"
                update_info_url           = "https://yourdomain.com/extensions/eq12_data_pusher_changelog.html"
                browser_specific_settings = @{
                    gecko = @{
                        strict_min_version = "60.0"
                    }
                }
            }

            $UpdatesContent.addons."eq12-data-pusher@vibehigheric.com".updates += $NewUpdate

            $UpdatesContent | ConvertTo-Json -Depth 10 | Set-Content $UpdatesPath -Encoding UTF8
            Write-Log "Updates.json updated with version $Version"
        } catch {
            Write-Log "Failed to update updates.json: $($_.Exception.Message)" "ERROR"
        }
    }

    # Create XPI package
    $XpiPath = Join-Path $OutputDir "eq12_data_pusher_self_hosted_v$Version.xpi"

    try {
        Compress-Archive -Path "$BuildDir\*" -DestinationPath $XpiPath -Force
        Write-Log "Self-hosted package created: $XpiPath"

        # Copy updates.json to output for hosting
        $UpdatesOutputPath = Join-Path $OutputDir "firefox_updates.json"
        Copy-Item $UpdatesPath $UpdatesOutputPath -Force

        return @{
            xpi     = $XpiPath
            updates = $UpdatesOutputPath
        }
    } catch {
        throw "Failed to create self-hosted package: $($_.Exception.Message)"
    }
}

function Invoke-Signing {
    param($XpiPath)

    Write-Log "Signing extension package..."

    # This would integrate with Mozilla's signing service
    # For now, we'll just log the process
    Write-Log "Note: To sign extensions, submit to https://addons.mozilla.org/developers/" "INFO"
    Write-Log "Signing process would be handled by Mozilla's web service" "INFO"

    return $XpiPath
}

function Deploy-Package {
    param($PackageInfo, $BuildType)

    Write-Log "Deploying $BuildType package..."

    # This would deploy to your hosting service
    # For now, we'll create a deployment script

    $DeployScript = @"
# EQ12 Firefox Extension Deployment Script
# Generated on $(Get-Date)

# For AMO Distribution:
# 1. Go to https://addons.mozilla.org/developers/
# 2. Upload: $($PackageInfo -is [string] ? $PackageInfo : $PackageInfo.xpi)
# 3. Choose "On this site" for public distribution
# 4. Fill out listing details and submit for review

# For Self-Hosted Distribution:
# 1. Upload XPI file to your web server
# 2. Upload updates.json to your web server
# 3. Ensure HTTPS access to both files
# 4. Update manifest.json update_url to point to your updates.json

# Example hosting commands:
# scp eq12_data_pusher_v$Version.xpi user@yourserver.com:/var/www/html/extensions/
# scp firefox_updates.json user@yourserver.com:/var/www/html/

Write-Host "Deployment files prepared in: $OutputDir" -ForegroundColor Green
Write-Host "Follow the deployment guide above to complete the process" -ForegroundColor Yellow
"@

    $DeployScriptPath = Join-Path $OutputDir "deployment_guide.ps1"
    $DeployScript | Set-Content $DeployScriptPath -Encoding UTF8

    Write-Log "Deployment guide created: $DeployScriptPath"
}

# Main execution
try {
    Write-Log "=== EQ12 Firefox Extension Build Starting ==="
    Write-Log "Build Type: $BuildType"
    Write-Log "Version: $Version"
    Write-Log "Output Directory: $OutputDir"

    # Check prerequisites
    $Issues = Test-Prerequisites
    if ($Issues.Count -gt 0) {
        Write-Log "Prerequisites check failed:" "ERROR"
        foreach ($Issue in $Issues) {
            Write-Log "  - $Issue" "ERROR"
        }
        exit 1
    }

    # Create output directory
    if (-not (Test-Path $OutputDir)) {
        New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null
    }

    $SourceDir = "C:\EQ12\firefox_extension_eq12"

    # Build packages based on type
    switch ($BuildType) {
        "AMO" {
            $Package = Build-AMOPackage $SourceDir $OutputDir $Version

            if ($Sign) {
                $Package = Invoke-Signing $Package
            }

            if ($Deploy) {
                Deploy-Package $Package "AMO"
            }
        }

        "SelfHosted" {
            $Package = Build-SelfHostedPackage $SourceDir $OutputDir $Version

            if ($Sign) {
                $Package.xpi = Invoke-Signing $Package.xpi
            }

            if ($Deploy) {
                Deploy-Package $Package "SelfHosted"
            }
        }

        "Both" {
            # Build AMO package
            $AMOPackage = Build-AMOPackage $SourceDir $OutputDir $Version

            # Build self-hosted package
            $SelfHostedPackage = Build-SelfHostedPackage $SourceDir $OutputDir $Version

            if ($Sign) {
                $AMOPackage = Invoke-Signing $AMOPackage
                $SelfHostedPackage.xpi = Invoke-Signing $SelfHostedPackage.xpi
            }

            if ($Deploy) {
                Deploy-Package $AMOPackage "AMO"
                Deploy-Package $SelfHostedPackage "SelfHosted"
            }
        }
    }

    Write-Log "Build completed successfully!" "SUCCESS"
    Write-Log "Output files in: $OutputDir"

    # Show next steps
    Write-Log ""
    Write-Log "=== NEXT STEPS ==="
    Write-Log "1. Review generated packages in: $OutputDir"
    Write-Log "2. For AMO: Submit to https://addons.mozilla.org/developers/"
    Write-Log "3. For Self-Hosted: Upload XPI and updates.json to your server"
    Write-Log "4. Test installation on clean Firefox profile"
    Write-Log "5. Submit to Firefox Extension Developer Awards!"

} catch {
    Write-Log "Build failed: $($_.Exception.Message)" "ERROR"
    Write-Log "Stack trace: $($_.ScriptStackTrace)" "ERROR"
    exit 1
}
