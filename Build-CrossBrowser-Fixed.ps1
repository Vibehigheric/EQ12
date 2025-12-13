# EQ12 Cross-Browser Extension Builder
# Generates packages for both Chrome and Firefox

param([string]$Target = "Both")

Write-Host "Cross-Browser Extension Builder" -ForegroundColor Green

$sourceDir = "C:\EQ12\firefox_extension_eq12"
$buildDir = "C:\EQ12\builds"

if (!(Test-Path $buildDir)) {
  New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
}

Write-Host "Source: $sourceDir" -ForegroundColor Cyan
Write-Host "Output: $buildDir" -ForegroundColor Cyan

if ($Target -eq "Firefox" -or $Target -eq "Both") {
  Write-Host "Building Firefox Version..." -ForegroundColor Blue

  $firefoxDir = "$buildDir\firefox_eq12"
  if (Test-Path $firefoxDir) { Remove-Item $firefoxDir -Recurse -Force }
  New-Item -ItemType Directory -Path $firefoxDir -Force | Out-Null

  Copy-Item "$sourceDir\*" $firefoxDir -Recurse -Force

  Write-Host "Firefox build ready: $firefoxDir" -ForegroundColor Green

  $firefoxZip = "$buildDir\eq12-firefox-v1.0.0-amo.zip"
  if (Test-Path $firefoxZip) { Remove-Item $firefoxZip -Force }

  Compress-Archive -Path "$firefoxDir\*" -DestinationPath $firefoxZip -Force
  Write-Host "Firefox package: $firefoxZip" -ForegroundColor Green
}

if ($Target -eq "Chrome" -or $Target -eq "Both") {
  Write-Host "Building Chrome Version..." -ForegroundColor Blue

  $chromeDir = "$buildDir\chrome_eq12"
  if (Test-Path $chromeDir) { Remove-Item $chromeDir -Recurse -Force }
  New-Item -ItemType Directory -Path $chromeDir -Force | Out-Null

  Copy-Item "$sourceDir\*" $chromeDir -Recurse -Force

  # Create Chrome manifest
  $chromeManifest = @"
{
  "manifest_version": 2,
  "name": "EQ12 Data Pusher",
  "version": "1.0.0",
  "description": "Advanced data capture for sports betting, travel deals, and financial data. Chrome Web Store edition.",
  "permissions": [
    "activeTab",
    "storage",
    "contextMenus",
    "notifications",
    "http://localhost:*/*",
    "https://*.draftkings.com/*",
    "https://*.fanduel.com/*",
    "https://*.expedia.com/*"
  ],
  "browser_action": {
    "default_popup": "popup.html",
    "default_title": "EQ12 Data Pusher - Chrome Edition"
  },
  "background": {
    "scripts": ["background.js"],
    "persistent": false
  },
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content.js"],
    "run_at": "document_end"
  }]
}
"@

  $chromeManifest | Out-File "$chromeDir\manifest.json" -Encoding UTF8

  Write-Host "Chrome build ready: $chromeDir" -ForegroundColor Green

  $chromeZip = "$buildDir\eq12-chrome-v1.0.0-webstore.zip"
  if (Test-Path $chromeZip) { Remove-Item $chromeZip -Force }

  Compress-Archive -Path "$chromeDir\*" -DestinationPath $chromeZip -Force
  Write-Host "Chrome package: $chromeZip" -ForegroundColor Green
}

Write-Host "Cross-Browser Build Summary:" -ForegroundColor Yellow
Write-Host "Firefox: Ready for Mozilla Add-ons" -ForegroundColor Green
Write-Host "Chrome: Ready for Chrome Web Store" -ForegroundColor Green

Write-Host "Testing Instructions:" -ForegroundColor Cyan
Write-Host "Firefox: about:debugging -> Load Temporary Add-on" -ForegroundColor White
Write-Host "Chrome: chrome://extensions/ -> Load unpacked" -ForegroundColor White

Write-Host "Cross-Browser Extension Build Complete!" -ForegroundColor Green
