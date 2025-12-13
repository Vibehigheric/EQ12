# EQ12 Copilot Devcontainer Prompt

# EQ12 patch
You are Copilot. When asked to patch devcontainer or Codespaces files:

- Ensure Playwright and browsers are installed in the postCreate step.
- Ensure `GNUPGHOME` and `EQ12_LOGS` are set in `containerEnv`.
- Add postCreate script to install dotfiles and pip requirements.
- Add `install_extensions.sh` and run it during postCreate.
- Add TODO markers: `# TODO: export as JSON for dashboard`, `# TODO: add pytest unit test for schema`, `# TODO: add Pester test for PowerShell wrapper`.

*** End EQ12 patch
