<#
.SYNOPSIS
  Sync bookmarks.json into a Firefox profile (Windows).

.DESCRIPTION
  Conservative tool: Dry-run by default. Use -Apply to perform writes.
  Writes a simple Netscape-style bookmarks HTML (bookmarks_auto.html) into the profile
  and optionally appends startup URLs to user.js so the profile opens tabs on start.

.PARAMETER Profile
  Path to Firefox profile folder (contains places.sqlite). Defaults to C:\EQ12\profiles\firefox-bot

.PARAMETER BookmarksJson
  Path to the JSON bookmarks file. Defaults to C:\EQ12\configs\bookmarks.json

.PARAMETER Apply
  Switch to actually perform destructive writes. If not present, only a dry-run report is produced.

.EXAMPLE
  .\eq12_firefox_bookmarks.ps1 -Apply
#>
param(
  [string]$ProfilePath = 'C:\EQ12\profiles\firefox-bot',
  [string]$BookmarksJson = 'C:\EQ12\configs\bookmarks.json',
  [switch]$Apply
)

Set-StrictMode -Version Latest

function Write-Log {
    param([string]$Message)
    $logdir = Join-Path -Path (Split-Path -Parent $PSScriptRoot) '..\logs' | Resolve-Path -ErrorAction SilentlyContinue
    if (-not $logdir) { $logdir = 'C:\EQ12\logs' }
    $logdir = (Resolve-Path $logdir).ProviderPath
    if (-not (Test-Path $logdir)) { New-Item -Path $logdir -ItemType Directory -Force | Out-Null }
    $file = Join-Path $logdir 'firefox_bookmarks.log'
    "$((Get-Date).ToString('s')) `t $Message" | Out-File -FilePath $file -Append -Encoding utf8
}

if (-not (Test-Path $BookmarksJson)) {
    Write-Log "Bookmarks JSON not found: $BookmarksJson"
    Write-Error "Bookmarks JSON not found: $BookmarksJson"
    exit 2
}

$bookmarks = Get-Content -Path $BookmarksJson -Raw | ConvertFrom-Json
if ($null -eq $bookmarks -or $bookmarks.Count -eq 0) {
    Write-Log "Bookmarks JSON empty or invalid: $BookmarksJson"
    Write-Output "No bookmarks to apply."
    exit 0
}

Write-Output "Found $($bookmarks.Count) bookmark(s) to process. Dry-run: $(-not $Apply)"
Write-Log "Processing $($bookmarks.Count) bookmarks from $BookmarksJson (Apply=$Apply)"

# Build a simple Netscape bookmark HTML which Firefox can import/open
$html = @()
$html += '<!DOCTYPE NETSCAPE-Bookmark-file-1>'
$html += '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">'
$html += '<TITLE>EQ12 Bookmarks</TITLE>'
$html += '<H1>EQ12 Bookmarks</H1>'
$html += '<DL><p>'

foreach ($bm in $bookmarks) {
  $title = $bm.title -replace '[`"<>]',''
  $url = $bm.url
  # Use backtick to escape embedded double-quotes in PowerShell strings
  $html += "    <DT><A HREF=`"$url`">$title</A>"
    Write-Output "Bookmark: $title -> $url"
    Write-Log "Bookmark: $title -> $url"
}

$html += '</DL><p>'

if ($Apply) {
  if (-not (Test-Path $ProfilePath)) { New-Item -Path $ProfilePath -ItemType Directory -Force | Out-Null }
  $outFile = Join-Path $ProfilePath 'bookmarks_auto.html'
    $html -join "`n" | Out-File -FilePath $outFile -Encoding utf8
    Write-Output "Wrote bookmarks HTML to: $outFile"
    Write-Log "Wrote bookmarks HTML to: $outFile"

    # Optionally add startup URLs to user.js (non-destructive: appended)
  $startupUrls = ($bookmarks | ForEach-Object { $_.url }) -join ', '
  $userJs = Join-Path $ProfilePath 'user.js'
  # Escape double quotes with backtick so PowerShell emits valid user.js content
  $startupLine = "user_pref(`"browser.startup.homepage`", `"$startupUrls`());"
  # The above uses a simple representation; if you prefer multiple start pages use browser.startup.homepage_override.mstone or prefs for multiple URLs.
  Add-Content -Path $userJs -Value $startupLine -Encoding utf8
    Write-Output "Appended startup URLs to user.js"
    Write-Log "Appended startup URLs to user.js"
} else {
    Write-Output "Dry-run only; no files written. Rerun with -Apply to perform changes."
}
