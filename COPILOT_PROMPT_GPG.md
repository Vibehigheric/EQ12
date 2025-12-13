EQ12 GPG/Kleopatra Integration Copilot Prompt

You are GitHub Copilot assisting with integrating Kleopatra/Gpg4win into the EQ12 stack.

Rules:
- Always prefer the gpg CLI (`gpg.exe`) on Windows. If unavailable, instruct user to install Gpg4win.
- Provide both PowerShell and Python wrappers for encrypting, decrypting, signing, and verifying files.
- Tests:
  - Add Pester tests that assert `gpg --version` is available.
  - Add pytest tests that run clearsign/decrypt flows when a key is present; else skip.
- When generating code, include guidance for importing public keys and creating a backup.
- Add README section describing how to use Kleopatra GUI + EQ12 CLI wrappers.
