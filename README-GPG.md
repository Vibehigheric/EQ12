# GPG & Codespaces notes for EQ12

This repo contains helpers to set up GPG commit signing locally and inside Codespaces.

Quick steps:

1. Run the provided helper to set GNUPGHOME and configure git:

```powershell
# from Windows PowerShell (non-elevated)
C:\EQ12\scripts\set_gpg_env.ps1 -GpgPath 'C:\Program Files (x86)\GnuPG\bin\gpg.exe'
```

2. Open a new PowerShell session (so the user env picks up) and verify:

```powershell
gpg --list-secret-keys --keyid-format LONG
git config --global user.signingkey
git config --global gpg.program
```

3. To sign commits in Codespaces, enable GPG signing in the Codespace settings and ensure your dotfiles repository provides any `gpg-agent.conf` or `gpg.conf` entries you need.

Do not store private keys in the repo. Use Codespaces secrets and GitHub's GPG key UI to add public keys.
