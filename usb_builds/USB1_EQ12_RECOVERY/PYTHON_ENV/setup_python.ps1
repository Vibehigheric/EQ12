#!/usr/bin/env powershell
# Python Environment Setup for EQ12 Recovery
Write-Host "Setting up Python environment..." -ForegroundColor Green

# Install Python packages
$packages = @(
    "requests",
    "beautifulsoup4", 
    "playwright",
    "transformers",
    "torch",
    "opencv-python",
    "pandas",
    "numpy",
    "Pillow",
    "cryptography",
    "pycoral"
)

foreach ($package in $packages) {
    Write-Host "Installing $package..." -ForegroundColor Yellow
    pip install $package
}

Write-Host "Python environment ready!" -ForegroundColor Green
