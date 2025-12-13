# EQ12 Java Installation Script
Write-Host "🚀 EQ12 JAVA INSTALLATION" -ForegroundColor Green
Write-Host "=========================="

$JavaZipPath = "C:\EQ12\java-1.8.0-openjdk-1.8.0.392-1.b08.redhat.windows.x86_64.zip"
$InstallPath = "C:\EQ12\java"

# Check ZIP exists
if (-not (Test-Path $JavaZipPath)) {
    Write-Host "❌ Java ZIP not found" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Found Java ZIP" -ForegroundColor Green

# Create directory
if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
}
Write-Host "📁 Install directory ready" -ForegroundColor Cyan

# Extract
Write-Host "📦 Extracting Java..." -ForegroundColor Yellow
Expand-Archive -Path $JavaZipPath -DestinationPath $InstallPath -Force
Write-Host "✅ Extraction complete" -ForegroundColor Green

# Find Java
$JavaDirs = Get-ChildItem -Path $InstallPath -Directory
$JavaHome = $JavaDirs[0].FullName
$JavaExe = Join-Path $JavaHome "bin\java.exe"

# Test Java
Write-Host "☕ Testing Java..." -ForegroundColor Yellow
& $JavaExe -version

# Set environment
$env:JAVA_HOME = $JavaHome
$env:PATH = "$JavaHome\bin;$env:PATH"

Write-Host "✅ Java installation complete!" -ForegroundColor Green
Write-Host "Java Home: $JavaHome" -ForegroundColor Cyan

# Create activation script
$Script = "`$env:JAVA_HOME = `"$JavaHome`"`n`$env:PATH = `"$JavaHome\bin;`$env:PATH`"`nWrite-Host `"☕ Java activated`" -ForegroundColor Green"
Set-Content -Path "C:\EQ12\scripts\activate-java.ps1" -Value $Script

Write-Host "📜 Activation script created" -ForegroundColor Green
Write-Host "🎉 Installation complete!" -ForegroundColor Green