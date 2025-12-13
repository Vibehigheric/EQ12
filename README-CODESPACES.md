# EQ12 Codespaces / Devcontainer notes

EQ12 devcontainer auto-installs requirements, dotfiles, and tries to enable GPG signing.

Secrets to add in Codespaces: ODDS_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, DOTFILES_REPO

postCreateCommand runs `./.devcontainer/post_create.ps1` which installs pip requirements and Playwright browsers.

# TODO: add Pester test for PowerShell wrappers
EQ12 Codespaces Quickstart

This repo includes a devcontainer for Codespaces and helpers for GPG-signed commits.

Highlights:
- Devcontainer image: mcr.microsoft.com/devcontainers/python:3.12
- GPG: container will have GNUPGHOME at /home/vscode/.gnupg
- Secrets (add in repo Codespaces secrets): ODDS_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

Usage:
- Open in Codespaces and let the post-create script run. It will install requirements and create GNUPGHOME.
- To create a signed commit locally on Windows, run `C:\EQ12\_do_signed_commit.ps1` from a repository root.

Logs:
- Local logs path: C:\EQ12\logs
- Codespaces logs path: /workspaces/EQ12/logs
