#!/usr/bin/env powershell
<#
.SYNOPSIS
EQ12 GitHub Commit Verification Quick Setup

.DESCRIPTION
Simple setup for GitHub commit verification and vigilant mode for EQ12 betting automation.
#>

[CmdletBinding()]
param()

Write-Host "EQ12 GITHUB COMMIT VERIFICATION SETUP" -ForegroundColor Green
Write-Host "Setting up vigilant mode and signature verification..." -ForegroundColor Cyan

# Current Git configuration
Write-Host "`nCurrent Git Configuration:" -ForegroundColor Yellow
$currentName = git config --global user.name
$currentEmail = git config --global user.email  
$commitSigning = git config --global commit.gpgsign

Write-Host "  Name: $currentName" -ForegroundColor White
Write-Host "  Email: $currentEmail" -ForegroundColor White
Write-Host "  Commit Signing: $commitSigning" -ForegroundColor White

# GitHub verification explanation
Write-Host "`nGitHub Commit Verification Options:" -ForegroundColor Yellow
Write-Host "  [1] GitHub Web Signing (Recommended)" -ForegroundColor Green
Write-Host "      - Automatic signing for web commits" -ForegroundColor Gray
Write-Host "      - Perfect for GitHub Pro + Codespaces" -ForegroundColor Gray
Write-Host "      - No local GPG setup required" -ForegroundColor Gray
Write-Host ""
Write-Host "  [2] Local GPG Signing" -ForegroundColor Yellow  
Write-Host "      - Requires GPG key generation" -ForegroundColor Gray
Write-Host "      - Complex setup and management" -ForegroundColor Gray
Write-Host "      - Not ideal for cloud development" -ForegroundColor Gray

# Current status analysis
Write-Host "`nCurrent Status Analysis:" -ForegroundColor Yellow
if ($commitSigning -eq "false") {
    Write-Host "  Status: Local GPG signing disabled (Good for GitHub Pro workflow)" -ForegroundColor Green
    Write-Host "  Result: Local commits will show as Unsigned" -ForegroundColor Blue
    Write-Host "  Recommendation: Enable GitHub vigilant mode" -ForegroundColor Green
} else {
    Write-Host "  Status: Local GPG signing enabled" -ForegroundColor Yellow
    Write-Host "  Result: May show verification errors if GPG not properly configured" -ForegroundColor Yellow
}

# Vigilant mode setup
Write-Host "`nVigilant Mode Setup Instructions:" -ForegroundColor Yellow
Write-Host "  1. Go to: GitHub.com -> Settings -> SSH and GPG keys" -ForegroundColor White
Write-Host "  2. Scroll down to Vigilant mode section" -ForegroundColor White
Write-Host "  3. Check: Flag unsigned commits as unverified" -ForegroundColor White
Write-Host "  4. Save changes" -ForegroundColor White

# Benefits for EQ12
Write-Host "`nBenefits for EQ12 Betting Automation:" -ForegroundColor Yellow
Write-Host "  Clear verification status on all commits" -ForegroundColor Green
Write-Host "  Enhanced security for betting algorithm changes" -ForegroundColor Green
Write-Host "  Professional appearance for code reviews" -ForegroundColor Green
Write-Host "  Compliance with enterprise standards" -ForegroundColor Green

# Configuration choice
Write-Host "`nConfiguration Options:" -ForegroundColor Yellow
Write-Host "  [1] Optimize for GitHub Pro workflow (Recommended)" -ForegroundColor White
Write-Host "  [2] Keep current configuration" -ForegroundColor White
Write-Host "  [3] Show verification status only" -ForegroundColor White

$choice = Read-Host "`nSelect option (1-3)"

switch ($choice) {
    "1" {
        Write-Host "`nOptimizing for GitHub Pro workflow..." -ForegroundColor Yellow
        
        # Ensure proper email configuration
        if ($currentEmail) {
            Write-Host "  Email configured: $currentEmail" -ForegroundColor Green
        } else {
            $email = Read-Host "  Enter your GitHub email address"
            git config --global user.email $email
            Write-Host "  Email configured: $email" -ForegroundColor Green
            $currentEmail = $email
        }
        
        # Disable local GPG signing for optimal GitHub Pro workflow
        git config --global commit.gpgsign false
        git config --global --unset user.signingkey 2>$null
        
        Write-Host "  Local GPG signing disabled" -ForegroundColor Green
        Write-Host "  Configuration optimized for GitHub Pro + Codespaces" -ForegroundColor Green
        
        Write-Host "`nNext Steps:" -ForegroundColor Cyan
        Write-Host "  1. Enable vigilant mode on GitHub (instructions above)" -ForegroundColor White
        Write-Host "  2. Verify email $currentEmail is added to GitHub account" -ForegroundColor White
        Write-Host "  3. Use GitHub web interface for critical commits (auto-signed)" -ForegroundColor White
        Write-Host "  4. Local commits will show as Unverified (expected behavior)" -ForegroundColor White
    }
    
    "2" {
        Write-Host "`nKeeping current configuration..." -ForegroundColor Green
        Write-Host "  No changes made to Git settings" -ForegroundColor Gray
    }
    
    "3" {
        Write-Host "`nCurrent Verification Status:" -ForegroundColor Yellow
        Write-Host "  Git Name: $currentName" -ForegroundColor White
        Write-Host "  Git Email: $currentEmail" -ForegroundColor White
        Write-Host "  Local Signing: $commitSigning" -ForegroundColor White
        
        if ($commitSigning -eq "false") {
            Write-Host "`n  Prediction: Local commits will be unsigned" -ForegroundColor Blue
            Write-Host "  With vigilant mode: Will show Unverified status" -ForegroundColor Blue
        } else {
            Write-Host "`n  Prediction: Local commits will attempt signing" -ForegroundColor Yellow
            Write-Host "  Result depends on GPG key availability" -ForegroundColor Yellow
        }
        
        Write-Host "`n  GitHub web commits: Always Verified" -ForegroundColor Green
    }
    
    default {
        Write-Host "`nNo changes made" -ForegroundColor Green
    }
}

# Final summary
Write-Host "`nEQ12 Commit Verification Strategy:" -ForegroundColor Yellow
Write-Host "  For professional betting automation development:" -ForegroundColor Gray
Write-Host "  Enable GitHub vigilant mode for transparency" -ForegroundColor Green
Write-Host "  Use GitHub web commits for verified signatures" -ForegroundColor Green  
Write-Host "  Focus on automated code quality via CI/CD" -ForegroundColor Green
Write-Host "  Leverage GitHub Pro features for security" -ForegroundColor Green

Write-Host "`nQuick Actions:" -ForegroundColor Yellow
Write-Host "  GitHub.com -> Settings -> SSH and GPG keys -> Enable vigilant mode" -ForegroundColor Cyan
Write-Host "  Verify email $currentEmail is added to your GitHub account" -ForegroundColor Cyan

Write-Host "`nEQ12 commit verification setup complete!" -ForegroundColor Green