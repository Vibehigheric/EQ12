# EQ12 Java Installation Script - Simple Version
param(
    [string]$JavaZipPath = "C:\EQ12\java-1.8.0-openjdk-1.8.0.392-1.b08.redhat.windows.x86_64.zip",
    [string]$InstallPath = "C:\EQ12\java"
)

Write-Host "🚀 EQ12 JAVA INSTALLATION" -ForegroundColor Green
Write-Host "=========================="

# Check if ZIP exists
if (-not (Test-Path $JavaZipPath)) {
    Write-Host "❌ Java ZIP not found: $JavaZipPath" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found Java ZIP: $JavaZipPath" -ForegroundColor Green

# Create install directory
if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
    Write-Host "📁 Created directory: $InstallPath" -ForegroundColor Cyan
}

# Extract ZIP
Write-Host "📦 Extracting Java..." -ForegroundColor Yellow
try {
    Expand-Archive -Path $JavaZipPath -DestinationPath $InstallPath -Force
    Write-Host "✅ Extraction complete" -ForegroundColor Green
} catch {
    Write-Host "❌ Extraction failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Find Java directory
$JavaDirs = Get-ChildItem -Path $InstallPath -Directory
if ($JavaDirs.Count -eq 0) {
    Write-Host "❌ No Java directory found" -ForegroundColor Red
    exit 1
}

$JavaHome = $JavaDirs[0].FullName
$JavaExe = Join-Path $JavaHome "bin\java.exe"

# Test Java
if (Test-Path $JavaExe) {
    Write-Host "☕ Testing Java installation..." -ForegroundColor Yellow
    & $JavaExe -version
    Write-Host "✅ Java installation successful!" -ForegroundColor Green
    
    # Set environment for current session
    $env:JAVA_HOME = $JavaHome
    $env:PATH = "$JavaHome\bin;$env:PATH"
    
    Write-Host "🌍 Environment set for current session:" -ForegroundColor Cyan
    Write-Host "   JAVA_HOME = $JavaHome" -ForegroundColor White
    
    # Create activation script
    $ActivationScript = @"
# EQ12 Java Environment Activation
`$env:JAVA_HOME = "$JavaHome"
`$env:PATH = "$JavaHome\bin;`$env:PATH"
Write-Host "☕ Java environment activated for EQ12" -ForegroundColor Green
"@
    
    $ActivationPath = "C:\EQ12\scripts\activate-java.ps1"
    Set-Content -Path $ActivationPath -Value $ActivationScript
    Write-Host "📜 Created activation script: $ActivationPath" -ForegroundColor Green
    
} else {
    Write-Host "❌ Java executable not found: $JavaExe" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 JAVA INSTALLATION COMPLETE!" -ForegroundColor Green
Write-Host "Java Home: $JavaHome" -ForegroundColor Cyan
Write-Host "Use '. C:\EQ12\scripts\activate-java.ps1' in new sessions" -ForegroundColor Yellow