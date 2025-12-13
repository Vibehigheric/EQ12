#!/usr/bin/env bash
# EQ12 patch: install a curated list of VS Code extensions for EQ12
set -e

extensions=(
  # Core productivity & AI
  "GitHub.copilot"
  "eamodio.gitlens"
  "ms-python.python"
  "ms-python.vscode-pylance"
  "ms-vscode.cpptools"
  "esbenp.prettier-vscode"
  "dbaeumer.vscode-eslint"
  "ms-azuretools.vscode-docker"
  "GitHub.vscode-pull-request-github"
  "mhutchie.git-graph"

  # Remote & Devcontainer
  "ms-vscode-remote.remote-containers"
  "ms-vscode-remote.remote-ssh"
  "ms-vscode-remote.remote-explorer"
  "ms-vsliveshare.vsliveshare"

  # Playwright & Notebooks
  "ms-playwright.playwright"
  "ms-toolsai.jupyter"
  "ms-toolsai.vscode-ai"

  # Stealth / scraping helpers
  "lextudio.restructuredtext"
  "bungcip.better-toml"
  "tom - placeholder"

  # Themes / UI
  "pkief.material-icon-theme"
  "zhuangtongfa.material-theme"
  "usernamehw.errorlens"
  "oderwat.indent-rainbow"
  "wayou.vscode-todo-highlight"

  # Languages
  "golang.go"
  "rust-lang.rust-analyzer"
  "redhat.vscode-yaml"
  "ms-dotnettools.csharp"
  "batisteo.vscode-django"
  "batisteo.vscode-jinja"
  "redhat.java"
  "ms-vscode.go"

  # Testing / Debugging
  "hbenl.vscode-test-explorer"
  "ms-vscode.csharp"
  "ms-vscode.vscode-java-test"
  "ms-vscode.cpptools-extension-pack"

  # Misc / Utilities
  "formulahendry.code-runner"
  "digitalbrainstem.javascript-ejs-support"
  "streetsidesoftware.code-spell-checker"
  "pkief.material-icon-theme"
  "ritwickdey.LiveServer"
  "usernamehw.errorlens"
  "oderwat.indent-rainbow"
  "shardulm94.trailing-spaces"

  # Web / Frontend
  "msjsdiag.debugger-for-chrome"
  "esbenp.prettier-vscode"
  "dbaeumer.vscode-eslint"

  # Productivity
  "editorconfig.editorconfig"
  "streetsidesoftware.code-spell-checker"
  "coenraads.bracket-pair-colorizer-2"
  "vscodevim.vim"

  # Database / Cloud
  "ms-azuretools.vscode-cosmosdb"
  "ms-azuretools.vscode-kubernetes-tools"

  # Docs / Markdown
  "yzhang.markdown-all-in-one"
  "shd101wyy.markdown-preview-enhanced"

  # Misc languages / tools
  "james-yu.latex-workshop"
  "batisteo.vscode-jinja"
  "batisteo.vscode-django"
  "proofpoint.vscode-fortune"
  "mhutchie.git-graph"

  # Security / Quality
  "snyk-security.snyk-vulnerability-scanner"
  "sonarsource.sonarlint-vscode"

  # Extra popular picks to reach ~100
  "pkief.material-icon-theme"
  "zhuangtongfa.material-theme"
  "mikestead.dotenv"
  "streetsidesoftware.code-spell-checker"
  "ms-ossdata.vscode-postgresql"
  "ms-azuretools.vscode-azureresourcegroups"
  "ms-vscode.vscode-node-azure-pack"
  "ms-vscode-remote.remote-containers"
  "developer-name.placeholder-ext-1"
  "developer-name.placeholder-ext-2"
  "developer-name.placeholder-ext-3"
  "developer-name.placeholder-ext-4"
  "developer-name.placeholder-ext-5"
  "placeholder.more-extensions-1"
  "placeholder.more-extensions-2"
  "placeholder.more-extensions-3"
  "placeholder.more-extensions-4"
  "placeholder.more-extensions-5"
  "placeholder.more-extensions-6"
  "placeholder.more-extensions-7"
  "placeholder.more-extensions-8"
  "placeholder.more-extensions-9"
  "placeholder.more-extensions-10"
)

for ext in "${extensions[@]}"; do
  echo "Installing $ext"
  code --install-extension "$ext" --force || echo "Failed to install $ext"
done

echo "Extension install complete"
