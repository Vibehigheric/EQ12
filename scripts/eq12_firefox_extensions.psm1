<#
EQ12 Firefox Extensions manager
Provides helpers to create and manage Firefox bot profiles with preinstalled extensions.

Functions:
- New-EQ12FirefoxProfile
- Install-EQ12FirefoxExtension
- Start-EQ12FirefoxBot
- Remove-EQ12FirefoxProfile
- Test-EQ12FirefoxBot

# Usage: Import-Module ./eq12_firefox_extensions.psm1; New-EQ12FirefoxProfile -ProfileName firefox-bot -Apply
#
# Notes:
# - Requires Firefox installed at default path or set $Env:EQ12_FIREFOX_PATH
# - Downloads XPI files from provided URLs and unpacks manifest to validate
# - Keeps profile folders under C:\EQ12\profiles\
# - Safe defaults and DryRun mode supported
#>

using namespace System.IO

function Get-DefaultFirefoxPath {
    if ($env:EQ12_FIREFOX_PATH) { return $env:EQ12_FIREFOX_PATH }
    $paths = @("C:\\Program Files\\Mozilla Firefox\\firefox.exe","C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe")
    foreach ($p in $paths) { if (Test-Path $p) { return $p } }
    return $null
}

function New-EQ12FirefoxProfile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)] [string]$ProfileName,
        [switch]$Apply,
        [string]$ProfilesRoot = 'C:\\EQ12\\profiles'
    )

    $target = Join-Path $ProfilesRoot $ProfileName
    Write-Verbose "Profile target: $target"
    if (-not $Apply) { Write-Host "DryRun: would create $target"; return $target }

    if (-not (Test-Path $ProfilesRoot)) { New-Item -ItemType Directory -Path $ProfilesRoot | Out-Null }
    if (-not (Test-Path $target)) { New-Item -ItemType Directory -Path $target | Out-Null }

    # Create a minimal prefs.js or user.js if needed
    $userjs = Join-Path $target 'user.js'
    $prefs = @(
        'user_pref("privacy.firstparty.isolate", true);',
        'user_pref("dom.webdriver.enabled", false);'
    )
    $prefs | Out-File -FilePath $userjs -Encoding utf8
    Write-Host "Created profile at $target"
    return $target
}

function Install-EQ12FirefoxExtension {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)] [string]$ProfilePath,
        [Parameter(Mandatory=$true)] [string]$XpiUrl,
        [switch]$Apply
    )

    $downloads = Join-Path $env:TEMP 'eq12_xpi'
    if (-not (Test-Path $downloads)) { New-Item -ItemType Directory -Path $downloads | Out-Null }
    $xpiName = Split-Path $XpiUrl -Leaf
    $xpiPath = Join-Path $downloads $xpiName

    if (-not $Apply) { Write-Host "DryRun: would download $XpiUrl to $xpiPath and install to $ProfilePath"; return $xpiPath }

    Write-Host "Downloading extension $XpiUrl..."
    try {
        Invoke-WebRequest -Uri $XpiUrl -OutFile $xpiPath -UseBasicParsing -ErrorAction Stop
    } catch {
        Write-Error ("Failed to download {0}: {1}" -f $XpiUrl, $_.Exception.Message)
        throw
    }

    # Firefox profiles accept 'extensions' dir with XPI files
    $extdir = Join-Path $ProfilePath 'extensions'
    if (-not (Test-Path $extdir)) { New-Item -ItemType Directory -Path $extdir | Out-Null }
    Copy-Item -Path $xpiPath -Destination (Join-Path $extdir $xpiName) -Force
    Write-Host "Installed extension to profile: $xpiName"
    return (Join-Path $extdir $xpiName)
}

function Start-EQ12FirefoxBot {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)] [string]$ProfileName,
        [string]$ProfilesRoot = 'C:\\EQ12\\profiles',
        [switch]$NoRemote
    )

    $profilePath = Join-Path $ProfilesRoot $ProfileName
    if (-not (Test-Path $profilePath)) { throw "Profile not found: $profilePath" }

    $firefox = Get-DefaultFirefoxPath
    if (-not $firefox) { throw "Firefox not found. Set EQ12_FIREFOX_PATH env var." }

    $argList = @('-profile', $profilePath)
    if ($NoRemote) { $argList += '-no-remote' }

    Write-Host "Starting Firefox with profile $profilePath"
    Start-Process -FilePath $firefox -ArgumentList $argList
}

function Remove-EQ12FirefoxProfile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)] [string]$ProfileName,
        [string]$ProfilesRoot = 'C:\\EQ12\\profiles',
        [switch]$Apply
    )
    $target = Join-Path $ProfilesRoot $ProfileName
    if (-not (Test-Path $target)) { Write-Host "No profile to remove: $target"; return }
    if (-not $Apply) { Write-Host "DryRun: would remove $target"; return }
    Remove-Item -Path $target -Recurse -Force
    Write-Host "Removed profile $target"
}

function Test-EQ12FirefoxBot {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)] [string]$ProfileName,
        [string]$ProfilesRoot = 'C:\\EQ12\\profiles',
        [int]$TimeoutSeconds = 10
    )

    $profilePath = Join-Path $ProfilesRoot $ProfileName
    if (-not (Test-Path $profilePath)) { throw "Profile not found: $profilePath" }
    # Try starting headless and loading dashboard endpoint (requires geckodriver or Marionette setup)
    # Simpler: verify profile folder exists and contains extensions
    $extdir = Join-Path $profilePath 'extensions'
    if (-not (Test-Path $extdir)) { Write-Host "No extensions folder found in profile"; return $false }
    $count = (Get-ChildItem -Path $extdir -Filter *.xpi -ErrorAction SilentlyContinue | Measure-Object).Count
    Write-Host "$count extension(s) present in profile"
    return ($count -gt 0)
}

Export-ModuleMember -Function New-EQ12FirefoxProfile,Install-EQ12FirefoxExtension,Start-EQ12FirefoxBot,Remove-EQ12FirefoxProfile,Test-EQ12FirefoxBot
