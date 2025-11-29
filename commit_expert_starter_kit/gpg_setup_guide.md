# ============================================================
# EQ12 GPG Key Setup Guide
# Complete GPG Configuration for Signed Commits
# ============================================================

## What is GPG Signing?

GPG (GNU Privacy Guard) signing proves:
- ✅ **Authenticity**: You actually made the commit
- ✅ **Integrity**: Code hasn't been tampered with
- ✅ **Non-repudiation**: You can't deny making the commit

GitHub shows a **"Verified"** badge on signed commits.

---

## Prerequisites

- GPG installed: `gpg --version` (should show 2.4.8+)
- Git installed: `git --version` (should show 2.52.0+)

---

## Step-by-Step Setup (15 minutes)

### Step 1: Generate GPG Key

```powershell
# Generate key (follow prompts)
gpg --gen-key
```

**Prompts:**
```
Please select what kind of key you want:
   (1) RSA and RSA (default)
   -> Select: 1

What keysize do you want?
   -> Enter: 4096

Key is valid for?
   -> Enter: 0 (doesn't expire) or 2y (2 years)

Is this correct?
   -> Enter: y

Real name: Your Name
Email address: your-email@example.com  (MUST match Git email!)
Comment: EQ12 Commit Signing
```

GPG will generate your key (takes 30-60 seconds).

**Important:** Use the SAME email as your Git configuration:
```powershell
git config user.email  # Should match GPG email
```

---

### Step 2: List Your Keys

```powershell
gpg --list-keys
```

**Output:**
```
pub   rsa4096 2025-11-29 [SC]
      3AA5C34371567BD2ABC123DEF456789012345678  <-- This is your KEY ID (40 chars)
uid           [ultimate] Your Name (EQ12 Commit Signing) <your-email@example.com>
sub   rsa4096 2025-11-29 [E]
```

**Copy the 40-character KEY ID** (full fingerprint).

---

### Step 3: Configure Git to Use Your Key

```powershell
# Replace YOUR_KEY_ID with the 40-character fingerprint
git config --global user.signingkey 3AA5C34371567BD2ABC123DEF456789012345678

# Enable commit signing by default
git config --global commit.gpgsign true

# Set GPG program path (Windows)
git config --global gpg.program "C:\Program Files (x86)\GnuPG\bin\gpg.exe"
```

Verify:
```powershell
git config --global --list | Select-String "gpg\|sign"
```

**Expected Output:**
```
commit.gpgsign=true
gpg.program=C:\Program Files (x86)\GnuPG\bin\gpg.exe
user.signingkey=3AA5C34371567BD2ABC123DEF456789012345678
```

---

### Step 4: Test Signing

```powershell
# Create a test commit
git add .
git commit -S -m "test: GPG signing verification"

# Verify signature
git log --show-signature -1
```

**Expected Output:**
```
gpg: Signature made Fri Nov 29 12:34:56 2025 PST
gpg:                using RSA key 3AA5C34371567BD2ABC123DEF456789012345678
gpg: Good signature from "Your Name (EQ12 Commit Signing) <your-email@example.com>" [ultimate]

commit abc123def456...
Author: Your Name <your-email@example.com>
Date:   Fri Nov 29 12:34:56 2025 -0800

    test: GPG signing verification
```

✅ If you see **"Good signature"**, signing works!

---

### Step 5: Add GPG Key to GitHub (Optional but Recommended)

1. **Export your public key:**
   ```powershell
   gpg --armor --export your-email@example.com
   ```

2. **Copy the output** (starts with `-----BEGIN PGP PUBLIC KEY BLOCK-----`)

3. **Add to GitHub:**
   - Go to: https://github.com/settings/keys
   - Click "New GPG key"
   - Paste your public key
   - Click "Add GPG key"

4. **Verify on GitHub:**
   - Push a signed commit
   - GitHub will show a green **"Verified"** badge

---

## Troubleshooting

### Problem: "gpg: signing failed: No secret key"

**Cause:** Git can't find your GPG key

**Solution:**
```powershell
# List keys to verify it exists
gpg --list-secret-keys

# If key exists, verify Git config
git config --global user.signingkey YOUR_KEY_ID

# If key missing, regenerate with Step 1
```

---

### Problem: "gpg: signing failed: Inappropriate ioctl for device"

**Cause:** GPG can't prompt for passphrase

**Solution (Windows):**
```powershell
# Set GPG TTY
$env:GPG_TTY = (Get-Process -Id $PID).StandardInput.Handle

# Or use pinentry-basic
echo "pinentry-program C:/Program Files (x86)/GnuPG/bin/pinentry-basic.exe" | Out-File $env:APPDATA\gnupg\gpg-agent.conf -Encoding utf8
```

**Solution (Git Bash):**
```bash
export GPG_TTY=$(tty)
echo "test" | gpg --clearsign
```

---

### Problem: "error: gpg failed to sign the data"

**Cause:** GPG program path incorrect

**Solution:**
```powershell
# Find GPG location
Get-Command gpg | Select-Object Source

# Update Git config
git config --global gpg.program "C:\Program Files (x86)\GnuPG\bin\gpg.exe"
```

---

### Problem: GitHub shows "Unverified" despite signature

**Causes:**
1. Email mismatch (Git email ≠ GPG email ≠ GitHub email)
2. Public key not added to GitHub
3. Key expired

**Solution:**
```powershell
# Check all emails match
git config user.email
gpg --list-keys  # Check email in key

# Add public key to GitHub (Step 5)

# Check expiration
gpg --list-keys  # Look for [expires: date]

# Extend expiration if needed
gpg --edit-key YOUR_KEY_ID
gpg> expire
gpg> save
```

---

## Advanced: Multiple Signing Keys

If you have multiple projects or identities:

```powershell
# Generate second key with different email
gpg --gen-key

# Use different keys per repository
cd C:\EQ12_BROKEN_20251122_210342
git config user.signingkey KEY_FOR_EQ12

cd C:\OtherProject
git config user.signingkey KEY_FOR_OTHER
```

---

## Security Best Practices

### 1. Backup Your Private Key

```powershell
# Export private key (KEEP SECURE!)
gpg --export-secret-keys your-email@example.com > C:\Secure\gpg_private_key.asc

# Store on encrypted USB drive or password manager
```

### 2. Revoke Key If Compromised

```powershell
# Generate revocation certificate
gpg --gen-revoke YOUR_KEY_ID > revoke.asc

# If key is compromised, publish revocation
gpg --import revoke.asc
gpg --keyserver keys.openpgp.org --send-keys YOUR_KEY_ID
```

### 3. Set Expiration Date

Keys should expire (can be extended later):

```powershell
gpg --edit-key YOUR_KEY_ID
gpg> expire
  -> Enter: 2y (2 years)
gpg> save
```

---

## Automated Signing (EQ12 Integration)

### Always Sign Commits

```powershell
# Already configured globally:
git config --global commit.gpgsign true

# All commits are now signed automatically
git commit -m "feat: add feature"  # Automatically signed
```

### Sign in PowerShell Scripts

```powershell
# Use EQ12's automated commit script
.\eq12_auto_commit.ps1 -Message "chore: update config" -Sign

# Or use the existing helper
.\_do_signed_commit.ps1 -Message "feat: new module"
```

### Verify Signatures in CI/CD

```yaml
# GitHub Actions
- name: Verify Commit Signature
  run: |
    git log --show-signature -1
    git verify-commit HEAD
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `gpg --gen-key` | Generate new GPG key |
| `gpg --list-keys` | List public keys |
| `gpg --list-secret-keys` | List private keys |
| `gpg --armor --export EMAIL` | Export public key |
| `git commit -S -m "msg"` | Sign single commit |
| `git config commit.gpgsign true` | Auto-sign all commits |
| `git log --show-signature -1` | Verify last commit |
| `git verify-commit HASH` | Verify specific commit |

---

## Next Steps

1. ✅ Generate GPG key
2. ✅ Configure Git
3. ✅ Test signing
4. ✅ Add public key to GitHub
5. ✅ Update EQ12 automation scripts to use signing
6. ✅ Backup private key securely

**Signing ensures your $8.5M/year EQ12 codebase has cryptographic proof of authorship!**

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-29  
**EQ12 System**
