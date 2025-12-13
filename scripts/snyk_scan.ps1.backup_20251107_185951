param(
  [string]$Image = "",
  [switch]$Monitor
)

$ErrorActionPreference = 'Stop'

$cli = Join-Path $env:USERPROFILE ".snyk\snyk.exe"
if (-not (Test-Path $cli)) {
  Write-Error "Snyk CLI not found at $cli. Run the setup step first."
}

# Ensure authenticated
try {
  & $cli auth --help | Out-Null
} catch {
  Write-Host "Run: & \"$cli\" auth" -ForegroundColor Yellow
}

# Code + Open Source scans in repo
Push-Location (Resolve-Path "..\")
try {
  if ($Monitor) {
    & $cli monitor --all-projects
  } else {
    & $cli test --all-projects
  }
} finally {
  Pop-Location
}

# Container scans if an image is provided
if ($Image) {
  try {
    if ($Monitor) {
      & $cli container monitor $Image
    } else {
      & $cli container test $Image
    }
  } catch {
    Write-Warning "Container scan failed. Ensure Docker is installed and the image exists: $Image"
  }
}
