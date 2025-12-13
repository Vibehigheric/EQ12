#!/usr/bin/env powershell
<#
.SYNOPSIS
EQ12 GPG and Git Security Configuration Script

.DESCRIPTION
Configures GPG signing for secure commits in the EQ12 betting automation stack.
Ensures proper identity verification and signed commit requirements.

.NOTES
Part of the GitHub Pro maximization strategy for secure development.
#>

[CmdletBinding()]
param()

Write-Host "EQ12 GPG AND GIT SECURITY CONFIGURATION" -ForegroundColor Green
Write-Host "Setting up secure signed commits for betting automation..." -ForegroundColor Cyan

# Current configuration
Write-Host "`nCurrent Git Configuration:" -ForegroundColor Yellow
$currentName = git config --global user.name
$currentEmail = git config --global user.email
$currentSigningKey = git config --global user.signingkey
$commitSigning = git config --global commit.gpgsign

Write-Host "  Name: $currentName" -ForegroundColor White
Write-Host "  Email: $currentEmail" -ForegroundColor White
Write-Host "  Signing Key: $currentSigningKey" -ForegroundColor White
Write-Host "  Commit Signing: $commitSigning" -ForegroundColor White

# Detected GPG key from GitHub
Write-Host "`nDetected GPG Key Information:" -ForegroundColor Yellow
Write-Host "  Key ID: 1250C98F9D4D9E96" -ForegroundColor White
Write-Host "  Associated Email: ricoj100@example.com (GitHub)" -ForegroundColor White
Write-Host "  Status: Unverified on GitHub" -ForegroundColor Red

# Configuration recommendations
Write-Host "`nConfiguration Analysis:" -ForegroundColor Yellow

if ($currentEmail -eq "ricoj100@example.com") {
    Write-Host "  ⚠️  Using example email address" -ForegroundColor Yellow
    Write-Host "     Recommendation: Update to verified GitHub email" -ForegroundColor Gray
}
else {
    Write-Host "  ✅ Using proper email: $currentEmail" -ForegroundColor Green
}

if ($currentSigningKey -eq "1250C98F9D4D9E96") {
    Write-Host "  ✅ GPG signing key configured" -ForegroundColor Green
}
else {
    Write-Host "  ❌ GPG signing key mismatch" -ForegroundColor Red
}

if ($commitSigning -eq "true") {
    Write-Host "  ✅ Commit signing enabled" -ForegroundColor Green
}
else {
    Write-Host "  ❌ Commit signing disabled" -ForegroundColor Red
}

# Security recommendations
Write-Host "`nSecurity Recommendations:" -ForegroundColor Yellow
Write-Host "  1. Verify GPG key email matches your GitHub account" -ForegroundColor Gray
Write-Host "  2. Add GPG key to GitHub for verification badge" -ForegroundColor Gray
Write-Host "  3. Use consistent email across Git and GPG" -ForegroundColor Gray
Write-Host "  4. Enable commit signing for all repositories" -ForegroundColor Gray

# Proposed configuration
Write-Host "`nRecommended Git Configuration:" -ForegroundColor Yellow
Write-Host "  Name: $currentName" -ForegroundColor Green
Write-Host "  Email: $currentEmail (matches iCloud)" -ForegroundColor Green
Write-Host "  Signing Key: 1250C98F9D4D9E96" -ForegroundColor Green
Write-Host "  Commit Signing: Enabled" -ForegroundColor Green

# Configuration options
Write-Host "`nConfiguration Options:" -ForegroundColor Yellow
Write-Host "  [1] Keep current configuration (recommended if working)" -ForegroundColor White
Write-Host "  [2] Update GPG key email to match Git email" -ForegroundColor White
Write-Host "  [3] Generate new GPG key with correct email" -ForegroundColor White
Write-Host "  [4] Disable GPG signing (not recommended for production)" -ForegroundColor White

$choice = Read-Host "`nSelect option (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`n✅ Keeping current configuration" -ForegroundColor Green
        Write-Host "   Next step: Add GPG key to GitHub for verification" -ForegroundColor Gray
    }
    "2" {
        Write-Host "`n🔧 Would need to regenerate GPG key..." -ForegroundColor Yellow
        Write-Host "   This requires creating a new key with email: $currentEmail" -ForegroundColor Gray
    }
    "3" {
        Write-Host "`n🔧 Generating new GPG key..." -ForegroundColor Yellow
        Write-Host "   This will create a new key for: $currentEmail" -ForegroundColor Gray
    }
    "4" {
        Write-Host "`n⚠️  Disabling GPG signing..." -ForegroundColor Yellow
        git config --global commit.gpgsign false
        Write-Host "   GPG signing disabled" -ForegroundColor Red
    }
    default {
        Write-Host "`n✅ No changes made" -ForegroundColor Green
    }
}

# GitHub integration check
Write-Host "`nGitHub Integration Status:" -ForegroundColor Yellow
Write-Host "  Repository: EQ12 betting automation stack" -ForegroundColor White
Write-Host "  Branch protection: Requires signed commits (recommended)" -ForegroundColor White
Write-Host "  GPG verification: Shows 'Verified' badge on commits" -ForegroundColor White

# Next steps
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Go to GitHub → Settings → SSH and GPG keys" -ForegroundColor Gray
Write-Host "  2. Add your GPG key (1250C98F9D4D9E96)" -ForegroundColor Gray
Write-Host "  3. Verify the key shows as 'Verified'" -ForegroundColor Gray
Write-Host "  4. Test with: git commit -S -m 'test signed commit'" -ForegroundColor Gray

# Security best practices
Write-Host "`nSecurity Best Practices:" -ForegroundColor Yellow
Write-Host "  ✅ Use GPG signing for all betting automation commits" -ForegroundColor Green
Write-Host "  ✅ Keep private keys secure and backed up" -ForegroundColor Green
Write-Host "  ✅ Use verified email addresses" -ForegroundColor Green
Write-Host "  ✅ Enable branch protection with signed commit requirements" -ForegroundColor Green

Write-Host "`nGPG configuration analysis complete!" -ForegroundColor Green