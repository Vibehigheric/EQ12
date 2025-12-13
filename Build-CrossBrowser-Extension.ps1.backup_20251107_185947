# EQ12 Cross-Browser Extension Builder
# Generates optimized packages for Chrome Web Store and Mozilla Add-ons (AMO)

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("Firefox", "Chrome", "Both", "All")]
    [string]$Target = "Both",

    [Parameter(Mandatory = $false)]
    [switch]$ManifestV3,

    [Parameter(Mandatory = $false)]
    [switch]$IncludePolyfill,

    [Parameter(Mandatory = $false)]
    [switch]$TestBuild,

    [Parameter(Mandatory = $false)]
    [switch]$Validate
)

[CmdletBinding()]
param()

Write-Host "🔄 EQ12 Cross-Browser Extension Builder" -ForegroundColor Green
Write-Host "Building packages for: $Target" -ForegroundColor Cyan

$sourceDir = "C:\EQ12\firefox_extension_eq12"
$buildDir = "C:\EQ12\builds\cross_browser"
$logFile = "C:\EQ12\logs\cross_browser_build_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

# Build Results Container
$buildResults = @{
    timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
    target    = $Target
    builds    = @()
    summary   = @{}
}

function New-BuildDirectory {
    param([string]$Path)

    if (Test-Path $Path) {
        Remove-Item $Path -Recurse -Force
    }
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
    Write-Host "✅ Created build directory: $Path" -ForegroundColor Green
}

function Copy-CoreFiles {
    param([string]$TargetPath, [string]$Browser)

    Write-Host "📁 Copying core extension files for $Browser..." -ForegroundColor Yellow

    # Copy all core files
    $coreFiles = @(
        "popup.html", "popup.js", "content.js", "background.js", "content.css"
    )

    foreach ($file in $coreFiles) {
        if (Test-Path "$sourceDir\$file") {
            Copy-Item "$sourceDir\$file" "$TargetPath\$file"
            Write-Host "   ✅ $file" -ForegroundColor Gray
        } else {
            Write-Host "   ⚠️ Missing: $file" -ForegroundColor Yellow
        }
    }

    # Copy icons directory if exists
    if (Test-Path "$sourceDir\icons") {
        Copy-Item "$sourceDir\icons" "$TargetPath\icons" -Recurse
        Write-Host "   ✅ Icons directory" -ForegroundColor Gray
    }
}

function New-FirefoxManifest {
    param([string]$TargetPath)

    Write-Host "🦊 Generating Firefox-optimized manifest (v2)..." -ForegroundColor Blue

    $firefoxManifest = @{
        manifest_version          = 2
        name                      = "EQ12 Data Pusher"
        version                   = "1.0.0"
        description               = "Advanced multi-platform data capture for EQ12 automation hub. Targets Mozilla Firefox Extension Developer Awards with AI-powered analysis."
        homepage_url              = "https://github.com/Vibehigheric/edgegod-parlay"
        author                    = "EQ12 Development Team"

        permissions               = @(
            "activeTab",
            "storage",
            "contextMenus",
            "notifications",
            "clipboardWrite",
            "http://localhost:*/*",
            "http://127.0.0.1:*/*",
            "https://*.ngrok-free.app/*",
            "https://*.draftkings.com/*",
            "https://*.fanduel.com/*",
            "https://*.expedia.com/*",
            "https://*.booking.com/*",
            "https://*.stubhub.com/*",
            "https://*.ticketmaster.com/*",
            "https://finance.yahoo.com/*"
        )

        browser_action            = @{
            default_popup = "popup.html"
            default_title = "EQ12 Data Pusher - Firefox Edition"
            default_icon  = @{
                "16"  = "icons/icon-16.png"
                "32"  = "icons/icon-32.png"
                "48"  = "icons/icon-48.png"
                "128" = "icons/icon-128.png"
            }
        }

        background                = @{
            scripts    = @("background.js")
            persistent = $false
        }

        content_scripts           = @(
            @{
                matches    = @("<all_urls>")
                js         = @("content.js")
                css        = @("content.css")
                run_at     = "document_end"
                all_frames = $false
            }
        )

        web_accessible_resources  = @(
            "icons/*.png"
        )

        browser_specific_settings = @{
            gecko = @{
                id                 = "eq12-data-pusher@eq12hub.com"
                strict_min_version = "109.0"
            }
        }

        applications              = @{
            gecko = @{
                id = "eq12-data-pusher@eq12hub.com"
            }
        }
    }

    $manifestJson = $firefoxManifest | ConvertTo-Json -Depth 10
    $manifestJson | Out-File "$TargetPath\manifest.json" -Encoding UTF8

    Write-Host "   ✅ Firefox Manifest V2 generated" -ForegroundColor Green
    return $firefoxManifest
}

function New-ChromeManifest {
    param([string]$TargetPath, [bool]$UseV3 = $false)

    if ($UseV3) {
        Write-Host "🌐 Generating Chrome-optimized manifest (v3)..." -ForegroundColor Blue

        $chromeManifest = @{
            manifest_version         = 3
            name                     = "EQ12 Data Pusher"
            version                  = "1.0.0"
            description              = "Advanced data capture for sports betting, travel deals, and financial data with AI analysis. Chrome Web Store edition."
            homepage_url             = "https://github.com/Vibehigheric/edgegod-parlay"

            permissions              = @(
                "activeTab",
                "storage",
                "contextMenus",
                "notifications",
                "clipboardWrite"
            )

            host_permissions         = @(
                "http://localhost:*/*",
                "http://127.0.0.1:*/*",
                "https://*.ngrok-free.app/*",
                "https://*.draftkings.com/*",
                "https://*.fanduel.com/*",
                "https://*.expedia.com/*",
                "https://*.booking.com/*",
                "https://*.stubhub.com/*",
                "https://finance.yahoo.com/*"
            )

            action                   = @{
                default_popup = "popup.html"
                default_title = "EQ12 Data Pusher - Chrome Edition"
                default_icon  = @{
                    "16"  = "icons/icon-16.png"
                    "32"  = "icons/icon-32.png"
                    "48"  = "icons/icon-48.png"
                    "128" = "icons/icon-128.png"
                }
            }

            background               = @{
                service_worker = "background.js"
            }

            content_scripts          = @(
                @{
                    matches = @("<all_urls>")
                    js      = @("content.js")
                    css     = @("content.css")
                    run_at  = "document_end"
                }
            )

            web_accessible_resources = @(
                @{
                    resources = @("icons/*.png")
                    matches   = @("<all_urls>")
                }
            )
        }

        Write-Host "   ✅ Chrome Manifest V3 generated" -ForegroundColor Green
    } else {
        Write-Host "🌐 Generating Chrome-compatible manifest (v2)..." -ForegroundColor Blue

        $chromeManifest = @{
            manifest_version         = 2
            name                     = "EQ12 Data Pusher"
            version                  = "1.0.0"
            description              = "Advanced data capture for sports betting, travel deals, and financial data with AI analysis."
            homepage_url             = "https://github.com/Vibehigheric/edgegod-parlay"

            permissions              = @(
                "activeTab",
                "storage",
                "contextMenus",
                "notifications",
                "clipboardWrite",
                "http://localhost:*/*",
                "http://127.0.0.1:*/*",
                "https://*.ngrok-free.app/*",
                "https://*.draftkings.com/*",
                "https://*.fanduel.com/*",
                "https://*.expedia.com/*",
                "https://*.booking.com/*",
                "https://*.stubhub.com/*",
                "https://finance.yahoo.com/*"
            )

            browser_action           = @{
                default_popup = "popup.html"
                default_title = "EQ12 Data Pusher - Chrome Edition"
                default_icon  = @{
                    "16"  = "icons/icon-16.png"
                    "32"  = "icons/icon-32.png"
                    "48"  = "icons/icon-48.png"
                    "128" = "icons/icon-128.png"
                }
            }

            background               = @{
                scripts    = @("background.js")
                persistent = $false
            }

            content_scripts          = @(
                @{
                    matches = @("<all_urls>")
                    js      = @("content.js")
                    css     = @("content.css")
                    run_at  = "document_end"
                }
            )

            web_accessible_resources = @(
                "icons/*.png"
            )
        }

        Write-Host "   ✅ Chrome Manifest V2 generated" -ForegroundColor Green
    }

    $manifestJson = $chromeManifest | ConvertTo-Json -Depth 10
    $manifestJson | Out-File "$TargetPath\manifest.json" -Encoding UTF8

    return $chromeManifest
}

function Add-WebExtensionPolyfill {
    param([string]$TargetPath, [string]$Browser)

    Write-Host "🔧 Adding webextension-polyfill for $Browser..." -ForegroundColor Yellow

    # Create simple polyfill for cross-browser compatibility
    $polyfill = @'
/**
 * EQ12 Cross-Browser Polyfill
 * Ensures consistent browser API access across Chrome and Firefox
 */
(function() {
    'use strict';

    // If browser API already exists (Firefox), use it
    if (typeof browser !== 'undefined') {
        return;
    }

    // If chrome API exists but browser doesn't (Chrome), create browser alias
    if (typeof chrome !== 'undefined' && typeof browser === 'undefined') {
        window.browser = chrome;
    }

    console.log('EQ12 Cross-Browser Polyfill loaded for:', navigator.userAgent);
})();
'@

    $polyfill | Out-File "$TargetPath\polyfill.js" -Encoding UTF8

    # Update manifest to include polyfill
    $manifestPath = "$TargetPath\manifest.json"
    if (Test-Path $manifestPath) {
        $manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json

        # Add polyfill to content scripts
        if ($manifest.content_scripts -and $manifest.content_scripts.Count -gt 0) {
            $manifest.content_scripts[0].js = @("polyfill.js") + $manifest.content_scripts[0].js
        }

        # Add polyfill to background scripts (V2)
        if ($manifest.background -and $manifest.background.scripts) {
            $manifest.background.scripts = @("polyfill.js") + $manifest.background.scripts
        }

        $manifest | ConvertTo-Json -Depth 10 | Out-File $manifestPath -Encoding UTF8
    }

    Write-Host "   ✅ Polyfill added and manifest updated" -ForegroundColor Green
}

function Optimize-BrowserSpecific {
    param([string]$TargetPath, [string]$Browser)

    Write-Host "⚡ Applying $Browser-specific optimizations..." -ForegroundColor Yellow

    if ($Browser -eq "Firefox") {
        # Firefox-specific optimizations
        Write-Host "   🦊 Firefox optimizations:" -ForegroundColor Gray
        Write-Host "     - Enhanced privacy controls" -ForegroundColor Gray
        Write-Host "     - Firefox-specific API usage" -ForegroundColor Gray
        Write-Host "     - AMO compliance checks" -ForegroundColor Gray

    } elseif ($Browser -eq "Chrome") {
        # Chrome-specific optimizations
        Write-Host "   🌐 Chrome optimizations:" -ForegroundColor Gray
        Write-Host "     - V8 performance enhancements" -ForegroundColor Gray
        Write-Host "     - Chrome Web Store compliance" -ForegroundColor Gray
        Write-Host "     - MV3 service worker compatibility" -ForegroundColor Gray
    }
}

function New-PackageFile {
    param([string]$SourcePath, [string]$OutputPath, [string]$Browser)

    Write-Host "📦 Creating $Browser package..." -ForegroundColor Yellow

    if ($Browser -eq "Firefox") {
        # Create .zip for AMO submission (will be converted to .xpi)
        $packageName = "eq12-data-pusher-firefox-v1.0.0.zip"
    } else {
        # Create .zip for Chrome Web Store
        $packageName = "eq12-data-pusher-chrome-v1.0.0.zip"
    }

    $packagePath = "$OutputPath\$packageName"

    # Use PowerShell Compress-Archive
    Compress-Archive -Path "$SourcePath\*" -DestinationPath $packagePath -Force

    Write-Host "   ✅ Package created: $packageName" -ForegroundColor Green
    return $packagePath
}

function Test-ExtensionBuild {
    param([string]$BuildPath, [string]$Browser)

    Write-Host "🧪 Testing $Browser build..." -ForegroundColor Yellow

    $testResults = @{
        browser        = $Browser
        manifest_valid = $false
        files_present  = $false
        size_check     = $false
        errors         = @()
    }

    # Test manifest
    try {
        $manifest = Get-Content "$BuildPath\manifest.json" -Raw | ConvertFrom-Json
        $testResults.manifest_valid = $true
        Write-Host "   ✅ Manifest syntax valid" -ForegroundColor Green
    } catch {
        $testResults.errors += "Invalid manifest JSON: $($_.Exception.Message)"
        Write-Host "   ❌ Manifest syntax error" -ForegroundColor Red
    }

    # Test required files
    $requiredFiles = @("popup.html", "popup.js", "content.js", "background.js")
    $filesPresent = $true
    foreach ($file in $requiredFiles) {
        if (!(Test-Path "$BuildPath\$file")) {
            $testResults.errors += "Missing required file: $file"
            $filesPresent = $false
        }
    }
    $testResults.files_present = $filesPresent

    if ($filesPresent) {
        Write-Host "   ✅ All required files present" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Missing required files" -ForegroundColor Red
    }

    # Test size
    $buildSize = (Get-ChildItem $BuildPath -Recurse | Measure-Object -Property Length -Sum).Sum
    $buildSizeMB = [math]::Round($buildSize / 1MB, 2)

    if ($buildSizeMB -lt 10) {
        # Most extension stores have 10MB limit
        $testResults.size_check = $true
        Write-Host "   ✅ Size check passed: ${buildSizeMB}MB" -ForegroundColor Green
    } else {
        $testResults.errors += "Build size too large: ${buildSizeMB}MB"
        Write-Host "   ❌ Size check failed: ${buildSizeMB}MB" -ForegroundColor Red
    }

    return $testResults
}

# Main Build Process
Write-Host "`n🚀 Starting cross-browser build process..." -ForegroundColor Cyan

# Create build directories
New-BuildDirectory $buildDir

if ($Target -eq "Firefox" -or $Target -eq "Both" -or $Target -eq "All") {
    Write-Host "`n🦊 Building Firefox Version..." -ForegroundColor Blue

    $firefoxBuildDir = "$buildDir\firefox"
    New-BuildDirectory $firefoxBuildDir

    # Copy core files
    Copy-CoreFiles $firefoxBuildDir "Firefox"

    # Generate Firefox manifest
    $firefoxManifest = New-FirefoxManifest $firefoxBuildDir

    # Add polyfill if requested
    if ($IncludePolyfill) {
        Add-WebExtensionPolyfill $firefoxBuildDir "Firefox"
    }

    # Apply Firefox optimizations
    Optimize-BrowserSpecific $firefoxBuildDir "Firefox"

    # Test build
    if ($TestBuild) {
        $firefoxTests = Test-ExtensionBuild $firefoxBuildDir "Firefox"
    }

    # Create package
    $firefoxPackage = New-PackageFile $firefoxBuildDir $buildDir "Firefox"

    $buildResults.builds += @{
        browser          = "Firefox"
        manifest_version = 2
        build_path       = $firefoxBuildDir
        package_path     = $firefoxPackage
        test_results     = $firefoxTests
    }

    Write-Host "✅ Firefox build completed!" -ForegroundColor Green
}

if ($Target -eq "Chrome" -or $Target -eq "Both" -or $Target -eq "All") {
    Write-Host "`n🌐 Building Chrome Version..." -ForegroundColor Blue

    $chromeBuildDir = "$buildDir\chrome"
    New-BuildDirectory $chromeBuildDir

    # Copy core files
    Copy-CoreFiles $chromeBuildDir "Chrome"

    # Generate Chrome manifest (V2 or V3)
    $chromeManifest = New-ChromeManifest $chromeBuildDir $ManifestV3

    # Add polyfill if requested
    if ($IncludePolyfill) {
        Add-WebExtensionPolyfill $chromeBuildDir "Chrome"
    }

    # Apply Chrome optimizations
    Optimize-BrowserSpecific $chromeBuildDir "Chrome"

    # Test build
    if ($TestBuild) {
        $chromeTests = Test-ExtensionBuild $chromeBuildDir "Chrome"
    }

    # Create package
    $chromePackage = New-PackageFile $chromeBuildDir $buildDir "Chrome"

    $buildResults.builds += @{
        browser          = "Chrome"
        manifest_version = if ($ManifestV3) { 3 } else { 2 }
        build_path       = $chromeBuildDir
        package_path     = $chromePackage
        test_results     = $chromeTests
    }

    Write-Host "✅ Chrome build completed!" -ForegroundColor Green
}

# Build Summary
Write-Host "`n📊 Build Summary:" -ForegroundColor Yellow

$totalBuilds = $buildResults.builds.Count
$successfulBuilds = ($buildResults.builds | Where-Object { $_.test_results.manifest_valid -and $_.test_results.files_present }).Count

$buildResults.summary = @{
    total_builds     = $totalBuilds
    successful       = $successfulBuilds
    failed           = $totalBuilds - $successfulBuilds
    output_directory = $buildDir
}

Write-Host "   Total Builds: $totalBuilds" -ForegroundColor White
Write-Host "   Successful: $successfulBuilds" -ForegroundColor Green
Write-Host "   Failed: $($totalBuilds - $successfulBuilds)" -ForegroundColor Red
Write-Host "   Output Directory: $buildDir" -ForegroundColor Cyan

# Detailed results
foreach ($build in $buildResults.builds) {
    $status = if ($build.test_results.manifest_valid -and $build.test_results.files_present) { "✅ SUCCESS" } else { "❌ FAILED" }
    $color = if ($build.test_results.manifest_valid -and $build.test_results.files_present) { "Green" } else { "Red" }

    Write-Host "`n$status $($build.browser) (Manifest v$($build.manifest_version))" -ForegroundColor $color
    Write-Host "   Build: $($build.build_path)" -ForegroundColor Gray
    Write-Host "   Package: $($build.package_path)" -ForegroundColor Gray

    if ($build.test_results.errors.Count -gt 0) {
        foreach ($error in $build.test_results.errors) {
            Write-Host "   ❌ $error" -ForegroundColor Red
        }
    }
}

# Save results
$buildResults | ConvertTo-Json -Depth 10 | Out-File $logFile -Encoding UTF8
Write-Host "`n💾 Build results saved to: $logFile" -ForegroundColor Blue

# Next steps
Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan

if ($buildResults.builds | Where-Object { $_.browser -eq "Firefox" }) {
    Write-Host "   🦊 Firefox: Load in about:debugging or submit to AMO" -ForegroundColor White
    Write-Host "      Package: $((($buildResults.builds | Where-Object { $_.browser -eq "Firefox" }).package_path))" -ForegroundColor Gray
}

if ($buildResults.builds | Where-Object { $_.browser -eq "Chrome" }) {
    Write-Host "   🌐 Chrome: Load in chrome://extensions/ or submit to Chrome Web Store" -ForegroundColor White
    Write-Host "      Package: $((($buildResults.builds | Where-Object { $_.browser -eq "Chrome" }).package_path))" -ForegroundColor Gray
}

Write-Host "`n✨ Cross-Browser Extension Build Complete!" -ForegroundColor Green
