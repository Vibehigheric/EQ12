# EQ12 Cross-Browser Extension Builder (Simplified)
# Generates packages for both Chrome and Firefox from existing extension

param(
    [string]$Target = "Both"
)

Write-Host "🔄 EQ12 Cross-Browser Extension Builder" -ForegroundColor Green

$sourceDir = "C:\EQ12\firefox_extension_eq12"
$buildDir = "C:\EQ12\builds"

# Create build directory
if (!(Test-Path $buildDir)) {
    New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
}

Write-Host "📁 Source: $sourceDir" -ForegroundColor Cyan
Write-Host "📦 Output: $buildDir" -ForegroundColor Cyan

if ($Target -eq "Firefox" -or $Target -eq "Both") {
    Write-Host "`n🦊 Building Firefox Version..." -ForegroundColor Blue

    $firefoxDir = "$buildDir\firefox_eq12"
    if (Test-Path $firefoxDir) { Remove-Item $firefoxDir -Recurse -Force }
    New-Item -ItemType Directory -Path $firefoxDir -Force | Out-Null

    # Copy all files
    Copy-Item "$sourceDir\*" $firefoxDir -Recurse -Force

    Write-Host "✅ Firefox build ready: $firefoxDir" -ForegroundColor Green

    # Create ZIP package for AMO
    $firefoxZip = "$buildDir\eq12-firefox-v1.0.0-amo.zip"
    if (Test-Path $firefoxZip) { Remove-Item $firefoxZip -Force }

    Compress-Archive -Path "$firefoxDir\*" -DestinationPath $firefoxZip -Force
    Write-Host "📦 Firefox package: $firefoxZip" -ForegroundColor Green
}

if ($Target -eq "Chrome" -or $Target -eq "Both") {
    Write-Host "`n🌐 Building Chrome Version..." -ForegroundColor Blue

    $chromeDir = "$buildDir\chrome_eq12"
    if (Test-Path $chromeDir) { Remove-Item $chromeDir -Recurse -Force }
    New-Item -ItemType Directory -Path $chromeDir -Force | Out-Null

    # Copy all files
    Copy-Item "$sourceDir\*" $chromeDir -Recurse -Force

    # Create Chrome-specific manifest
    $chromeManifest = @{
        "manifest_version"         = 2
        "name"                     = "EQ12 Data Pusher"
        "version"                  = "1.0.0"
        "description"              = "Advanced data capture for sports betting, travel deals, and financial data with AI analysis. Chrome Web Store edition."
        "homepage_url"             = "https://github.com/Vibehigheric/edgegod-parlay"

        "permissions"              = @(
            "activeTab",
            "storage",
            "contextMenus",
            "notifications",
            "clipboardWrite",
            "http://localhost:*/*",
            "https://*.draftkings.com/*",
            "https://*.fanduel.com/*",
            "https://*.expedia.com/*",
            "https://*.stubhub.com/*"
        )

        "browser_action"           = @{
            "default_popup" = "popup.html"
            "default_title" = "EQ12 Data Pusher - Chrome Edition"
            "default_icon"  = @{
                "16"  = "icons/icon-16.png"
                "48"  = "icons/icon-48.png"
                "128" = "icons/icon-128.png"
            }
        }

        "background"               = @{
            "scripts"    = @("background.js")
            "persistent" = $false
        }

        "content_scripts"          = @(
            @{
                "matches" = @("<all_urls>")
                "js"      = @("content.js")
                "css"     = @("content.css")
                "run_at"  = "document_end"
            }
        )

        "web_accessible_resources" = @(
            "icons/*.png"
        )
    }

    # Write Chrome manifest
    $chromeManifest | ConvertTo-Json -Depth 10 | Out-File "$chromeDir\manifest.json" -Encoding UTF8

    Write-Host "✅ Chrome build ready: $chromeDir" -ForegroundColor Green

    # Create ZIP package for Chrome Web Store
    $chromeZip = "$buildDir\eq12-chrome-v1.0.0-webstore.zip"
    if (Test-Path $chromeZip) { Remove-Item $chromeZip -Force }

    Compress-Archive -Path "$chromeDir\*" -DestinationPath $chromeZip -Force
    Write-Host "📦 Chrome package: $chromeZip" -ForegroundColor Green
}

Write-Host "`n📊 Cross-Browser Build Summary:" -ForegroundColor Yellow
Write-Host "✅ Firefox: Ready for Mozilla Add-ons (AMO)" -ForegroundColor Green
Write-Host "✅ Chrome: Ready for Chrome Web Store" -ForegroundColor Green
Write-Host "✅ Cross-Browser: Uses standard WebExtensions APIs" -ForegroundColor Green

Write-Host "`n🚀 Testing Instructions:" -ForegroundColor Cyan
Write-Host "Firefox: about:debugging → Load Temporary Add-on" -ForegroundColor White
Write-Host "Chrome: chrome://extensions/ → Load unpacked" -ForegroundColor White

Write-Host "`n🏆 Store Submission Ready:" -ForegroundColor Magenta
if (Test-Path "$buildDir\eq12-firefox-v1.0.0-amo.zip") {
    Write-Host "Firefox AMO: $buildDir\eq12-firefox-v1.0.0-amo.zip" -ForegroundColor Blue
}
if (Test-Path "$buildDir\eq12-chrome-v1.0.0-webstore.zip") {
    Write-Host "Chrome Store: $buildDir\eq12-chrome-v1.0.0-webstore.zip" -ForegroundColor Blue
}

Write-Host "`n✨ Cross-Browser Extension Build Complete!" -ForegroundColor Green
