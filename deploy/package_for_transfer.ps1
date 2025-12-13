# EQ12 Packaging Script
$timestamp = Get-Date -Format "yyyyMMdd_HHmm"
$zipName = "EQ12_Cluster_Deploy_$timestamp.zip"
$sourceDir = Get-Location
$exclude = @(".venv", "__pycache__", ".git", "*.zip", "deploy\*.zip")

Write-Host "Packaging EQ12 Cluster for Deployment..." -ForegroundColor Cyan

# Create a temporary directory for staging
$stagingDir = Join-Path $sourceDir "deploy_staging"
if (Test-Path $stagingDir) { Remove-Item $stagingDir -Recurse -Force }
New-Item -ItemType Directory -Path $stagingDir | Out-Null

# Copy files
Write-Host "Copying files..." -ForegroundColor Yellow
Copy-Item -Path "src" -Destination $stagingDir -Recurse
Copy-Item -Path "scripts" -Destination $stagingDir -Recurse
Copy-Item -Path "config" -Destination $stagingDir -Recurse
Copy-Item -Path "requirements.txt" -Destination $stagingDir
Copy-Item -Path "deploy\setup_lenovo.ps1" -Destination $stagingDir
Copy-Item -Path "deploy\README_DEPLOY.md" -Destination $stagingDir

# Zip it up
Write-Host "Zipping to $zipName..." -ForegroundColor Yellow
Compress-Archive -Path "$stagingDir\*" -DestinationPath "deploy\$zipName" -Force

# Cleanup
Remove-Item $stagingDir -Recurse -Force

Write-Host "Package created: deploy\$zipName" -ForegroundColor Green
Write-Host "Transfer this zip file to your Lenovo M70q."
