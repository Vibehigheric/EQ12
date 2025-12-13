# eq12_firefox.psm1 - EQ12 Firefox helpers
# Provides Start/Stop wrappers and utility functions for Firefox bot profiles and geckodriver

function Start-EQ12FirefoxBot {
    param(
        [string]$ProfilePath = 'C:\EQ12\profiles\firefox-bot',
        [switch]$Headless,
        [switch]$NoRemote
    )
    $exe = 'C:\Program Files\Mozilla Firefox\firefox.exe'
    if (-not (Test-Path $exe)) {
        throw "Firefox executable not found at $exe"
    }
    $args = @()
    if ($Headless) { $args += '-headless' }
    if ($NoRemote) { $args += '-no-remote' }
    $args += '-profile'
    $args += "`"$ProfilePath`""
    Start-Process -FilePath $exe -ArgumentList $args -PassThru
}

function New-EQ12GeckoDriver {
    param(
        [string]$Destination = 'C:\EQ12\bin\geckodriver.exe'
    )
    $destDir = Split-Path $Destination -Parent
    if (-not (Test-Path $destDir)) { New-Item -Path $destDir -ItemType Directory -Force | Out-Null }
    # This function will not download automatically for security reasons. It will create a stub placeholder with instructions.
    $placeholder = @"
GeckoDriver placeholder created at: $Destination
Please download geckodriver.exe from https://github.com/mozilla/geckodriver/releases and place it at the path above.
"@
    $placeholder | Out-File -FilePath "$Destination.txt" -Encoding UTF8 -Force
    return $Destination
}

function Register-EQ12FirefoxAliases {
    Set-Alias -Name eq12-firefox-bot -Value Start-EQ12FirefoxBot -Force
    function eq12-dashboard-firefox { param([string]$Path='C:\EQ12\dashboard\index.html') & 'C:\Program Files\Mozilla Firefox\firefox.exe' $Path }
}

Export-ModuleMember -Function *-EQ12* , Register-EQ12FirefoxAliases
