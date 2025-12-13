param(
  [string]$Proj = "C:\EQ12\EQ12.ChatGPT.InlineRefactor\EQ12.ChatGPT.InlineRefactor.csproj",
  [string]$Cfg  = "Release"
)
$ErrorActionPreference = "Stop"

# Try vswhere first
$vswhere = "$env:ProgramFiles(x86)\Microsoft Visual Studio\Installer\vswhere.exe"
$msbuild = $null
$vsixInstaller = $null

if (Test-Path $vswhere) {
  $instPath = & $vswhere -latest -products * -requires Microsoft.Component.MSBuild -property installationPath 2>$null
  if ($instPath) {
    $msbuild = Join-Path $instPath "MSBuild\Current\Bin\MSBuild.exe"
    $vsixInstaller = Join-Path $instPath "Common7\IDE\VSIXInstaller.exe"
  }
}

# Fallback to common MSBuild/VSIX paths
if (-not (Test-Path $msbuild)) {
  $msCandidates = @(
    "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe",
    "C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Current\Bin\MSBuild.exe",
    "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\MSBuild\Current\Bin\MSBuild.exe"
  )
  $msbuild = $msCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not (Test-Path $vsixInstaller)) {
  $vxCandidates = @(
    "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\VSIXInstaller.exe",
    "C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\IDE\VSIXInstaller.exe",
    "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Common7\IDE\VSIXInstaller.exe"
  )
  $vsixInstaller = $vxCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}

if (-not (Test-Path $msbuild)) {
  Write-Warning "MSBuild not found. Open **Developer PowerShell for VS 2022** and run:`n`"$Proj`" /t:Restore,Build /p:Configuration=$Cfg"
  exit 1
}

Write-Host "Using MSBuild: $msbuild"
& $msbuild $Proj /t:Restore,Build /p:Configuration=$Cfg
if ($LASTEXITCODE -ne 0) { throw "Build failed. Check MSBuild output above." }

$vsix = Get-ChildItem -Path (Join-Path (Split-Path $Proj) "bin\$Cfg") -Filter *.vsix -File -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $vsix) { throw "No .vsix found in bin\$Cfg" }
Write-Host "Found VSIX: $($vsix.FullName)"

if (Test-Path $vsixInstaller) {
  Write-Host "Installing VSIX with: $vsixInstaller"
  & $vsixInstaller $vsix.FullName
  Write-Host "If installation succeeded, restart Visual Studio."
} else {
  Write-Warning "VSIXInstaller not found. Double-click the VSIX to install: $($vsix.FullName)"
}
