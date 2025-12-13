#!/usr/bin/env powershell
<#
.SYNOPSIS
EQ12 GPG Key Recovery and Setup Script

.DESCRIPTION
Resolves GPG key issues and sets up proper signed commit configuration
for the EQ12 betting automation stack.
#>

[CmdletBinding()]
param()

Write-Host "EQ12 GPG KEY RECOVERY AND SETUP" -ForegroundColor Green
Write-Host "Resolving GPG configuration for secure betting automation commits..." -ForegroundColor Cyan

# Check current Git configuration
Write-Host "`nCurrent Git Configuration:" -ForegroundColor Yellow
$gitName = git config --global user.name
$gitEmail = git config --global user.email
$gitSigningKey = git config --global user.signingkey
$commitSigning = git config --global commit.gpgsign

Write-Host "  Name: $gitName" -ForegroundColor White
Write-Host "  Email: $gitEmail" -ForegroundColor White
Write-Host "  Signing Key: $gitSigningKey" -ForegroundColor White
Write-Host "  Commit Signing: $commitSigning" -ForegroundColor White

# Check if the configured key exists locally
Write-Host "`nChecking GPG Key Availability:" -ForegroundColor Yellow
$keyExists = $false
if ($gitSigningKey) {
    $keyCheck = gpg --list-secret-keys $gitSigningKey 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  GPG Key Found: $gitSigningKey" -ForegroundColor Green
        $keyExists = $true
    } else {
        Write-Host "  GPG Key Missing: $gitSigningKey (configured but not available)" -ForegroundColor Red
    }
} else {
    Write-Host "  No GPG key configured" -ForegroundColor Yellow
}

# List available GPG keys
Write-Host "`nAvailable GPG Keys:" -ForegroundColor Yellow
$availableKeys = gpg --list-secret-keys --keyid-format=long 2>$null
if ($LASTEXITCODE -eq 0 -and $availableKeys) {
    Write-Host "$availableKeys" -ForegroundColor White
} else {
    Write-Host "  No GPG keys found locally" -ForegroundColor Red
}

# Resolution options
Write-Host "`nResolution Options:" -ForegroundColor Yellow
Write-Host "  [1] Generate new GPG key with current email ($gitEmail)" -ForegroundColor White
Write-Host "  [2] Disable GPG signing (not recommended for production)" -ForegroundColor White
Write-Host "  [3] Import existing GPG key from backup" -ForegroundColor White
Write-Host "  [4] Configure GitHub Codespaces without local GPG" -ForegroundColor White

$choice = Read-Host "`nSelect option (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`nGenerating new GPG key..." -ForegroundColor Yellow
        
        # Create GPG key generation script
        $gpgScript = @"
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: $gitName
Name-Email: $gitEmail
Name-Comment: EQ12 Betting Automation Stack
Expire-Date: 0
%no-protection
%commit
"@
        
        # Write to temp file
        $tempFile = [System.IO.Path]::GetTempFileName()
        $gpgScript | Out-File -FilePath $tempFile -Encoding ASCII
        
        Write-Host "  Creating GPG key with email: $gitEmail" -ForegroundColor Gray
        $result = gpg --batch --generate-key $tempFile 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  GPG key generated successfully!" -ForegroundColor Green
            
            # Get the new key ID
            $newKeys = gpg --list-secret-keys --keyid-format=long | Select-String "sec.*rsa4096/([A-F0-9]{16})" 
            if ($newKeys) {
                $newKeyId = $newKeys.Matches[0].Groups[1].Value
                Write-Host "  New Key ID: $newKeyId" -ForegroundColor Green
                
                # Configure Git to use the new key
                git config --global user.signingkey $newKeyId
                git config --global commit.gpgsign true
                
                Write-Host "  Git configured to use new GPG key" -ForegroundColor Green
                
                # Export public key for GitHub
                Write-Host "`nExporting public key for GitHub:" -ForegroundColor Yellow
                $publicKey = gpg --armor --export $newKeyId
                Write-Host "Copy this key to GitHub (Settings -> SSH and GPG keys):" -ForegroundColor Cyan
                Write-Host "----------------------------------------" -ForegroundColor Gray
                Write-Host $publicKey -ForegroundColor White
                Write-Host "----------------------------------------" -ForegroundColor Gray
                
                # Save to file for easy access
                $publicKey | Out-File -FilePath "C:\EQ12\gpg-public-key.txt" -Encoding UTF8
                Write-Host "Public key saved to: C:\EQ12\gpg-public-key.txt" -ForegroundColor Green
            }
        } else {
            Write-Host "  Failed to generate GPG key: $result" -ForegroundColor Red
        }
        
        # Cleanup
        Remove-Item $tempFile -ErrorAction SilentlyContinue
    }
    
    "2" {
        Write-Host "`nDisabling GPG signing..." -ForegroundColor Yellow
        git config --global commit.gpgsign false
        git config --global --unset user.signingkey
        Write-Host "  GPG signing disabled" -ForegroundColor Green
        Write-Host "  WARNING: Commits will not be signed (not recommended for production)" -ForegroundColor Red
    }
    
    "3" {
        Write-Host "`nTo import existing GPG key:" -ForegroundColor Yellow
        Write-Host "  1. Locate your GPG key backup file" -ForegroundColor Gray
        Write-Host "  2. Run: gpg --import your-key-file.asc" -ForegroundColor Gray
        Write-Host "  3. Run this script again to configure Git" -ForegroundColor Gray
    }
    
    "4" {
        Write-Host "`nConfiguring for GitHub Codespaces..." -ForegroundColor Yellow
        git config --global commit.gpgsign false
        Write-Host "  Disabled local GPG signing (Codespaces handles this differently)" -ForegroundColor Green
        Write-Host "  Your commits will be signed by GitHub when using Codespaces" -ForegroundColor Green
    }
    
    default {
        Write-Host "`nNo changes made" -ForegroundColor Yellow
    }
}

# Test configuration
Write-Host "`nTesting Configuration:" -ForegroundColor Yellow
$finalName = git config --global user.name
$finalEmail = git config --global user.email  
$finalSigningKey = git config --global user.signingkey
$finalSigning = git config --global commit.gpgsign

Write-Host "  Name: $finalName" -ForegroundColor White
Write-Host "  Email: $finalEmail" -ForegroundColor White
Write-Host "  Signing Key: $finalSigningKey" -ForegroundColor White
Write-Host "  Commit Signing: $finalSigning" -ForegroundColor White

if ($finalSigning -eq "true" -and $finalSigningKey) {
    Write-Host "`nNext Steps:" -ForegroundColor Yellow
    Write-Host "  1. Add GPG key to GitHub (Settings -> SSH and GPG keys)" -ForegroundColor Gray
    Write-Host "  2. Test with: git commit -S -m 'test: GPG signing verification'" -ForegroundColor Gray
    Write-Host "  3. Verify 'Verified' badge appears on GitHub commits" -ForegroundColor Gray
} elseif ($finalSigning -eq "false") {
    Write-Host "`nGPG signing disabled - commits will not be signed" -ForegroundColor Yellow
}

Write-Host "`nEQ12 GPG configuration complete!" -ForegroundColor Green