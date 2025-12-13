# EQ12 VS Code Optimization Guide
## Complete Setup for AI Betting Automation Stack

### 🚀 Quick Setup Commands

```powershell
# Install essential VS Code extensions
code --install-extension ms-python.python `
     --install-extension ms-toolsai.jupyter `
     --install-extension github.copilot `
     --install-extension ms-azuretools.vscode-docker `
     --install-extension esbenp.prettier-vscode `
     --install-extension ms-python.black-formatter `
     --install-extension charliermarsh.ruff `
     --install-extension humao.rest-client `
     --install-extension aaron-bond.better-comments `
     --install-extension ms-vscode.powershell `
     --install-extension ms-vscode-remote.remote-containers

# Install Python code quality tools
pip install black[jupyter] ruff isort autoflake autopep8 flake8
```

### 🔧 VS Code Settings for EQ12 Stack

Create/update `.vscode/settings.json`:

```json
{
  "python.defaultInterpreter": "C:\\Program Files\\Python312\\python.exe",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": ["--max-line-length=100"],
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=100"],
  "ruff.args": ["--line-length=100"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true,
    "source.fixAll.ruff": true
  },
  "files.exclude": {
    "**/envs/**": true,
    "**/research/**": true,
    "**/EdgeGodParlays/**": true,
    "**/__pycache__/**": true,
    "**/*.pyc": true
  },
  "jupyter.defaultKernel": "Python 3.12",
  "github.copilot.enable": {
    "*": true,
    "yaml": false,
    "plaintext": false
  }
}
```

### 📋 Essential Extensions Breakdown

#### Core Development
- **Python (ms-python.python)** - Full Python support
- **Jupyter (ms-toolsai.jupyter)** - Notebook support
- **GitHub Copilot** - AI code completion
- **Black Formatter** - Code formatting
- **Ruff** - Fast Python linter

#### Automation & DevOps
- **Docker** - Container development
- **PowerShell** - Windows automation
- **Remote Containers** - Isolated environments
- **REST Client** - API testing

#### Code Quality
- **Better Comments** - Enhanced commenting
- **Prettier** - General formatting
- **GitLens** - Advanced Git features

### ⚡ Performance Optimizations

#### Memory Management
```json
{
  "python.analysis.memory.keepLibraryAst": false,
  "python.analysis.autoImportCompletions": true,
  "python.analysis.indexing": false,
  "extensions.experimental.affinity": {
    "ms-python.python": 1,
    "github.copilot": 1
  }
}
```

#### Large Codebase Settings
```json
{
  "search.exclude": {
    "**/node_modules": true,
    "**/envs": true,
    "**/research": true,
    "**/.git": true,
    "**/__pycache__": true
  },
  "files.watcherExclude": {
    "**/envs/**": true,
    "**/research/**": true
  }
}
```

### 🎯 EQ12-Specific Tasks

Create `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "EQ12: Format Code",
      "type": "shell",
      "command": "black",
      "args": [".", "--line-length=100"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
      }
    },
    {
      "label": "EQ12: Lint Code",
      "type": "shell",
      "command": "ruff",
      "args": ["check", ".", "--fix"],
      "group": "test",
      "presentation": {
        "echo": true,
        "reveal": "always"
      }
    },
    {
      "label": "EQ12: Run Tests",
      "type": "shell",
      "command": "python",
      "args": ["-m", "pytest", "tests/", "-v"],
      "group": "test"
    },
    {
      "label": "EQ12: Start Betting Bot",
      "type": "shell",
      "command": "python",
      "args": ["eq12_betting_arbitrage_bot.py"],
      "group": "build"
    }
  ]
}
```

### 🔍 Debugging Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "EQ12 Betting Bot",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/eq12_betting_arbitrage_bot.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    },
    {
      "name": "EQ12 Sports API",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/scripts/eq12_multi_sports_api_client.py",
      "console": "integratedTerminal"
    },
    {
      "name": "Debug Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    }
  ]
}
```

### 🛡️ Security & Environment

#### Environment Variables Setup
```json
{
  "terminal.integrated.env.windows": {
    "ODDS_API_KEY": "${env:ODDS_API_KEY}",
    "TELEGRAM_BOT_TOKEN": "${env:TELEGRAM_BOT_TOKEN}",
    "OPENAI_API_KEY": "${env:OPENAI_API_KEY}"
  }
}
```

#### Workspace Security
```json
{
  "security.workspace.trust.enabled": true,
  "security.workspace.trust.startupPrompt": "once",
  "git.ignoreLimitWarning": true,
  "files.associations": {
    "*.env": "properties",
    "*.env.*": "properties"
  }
}
```

### 🔄 Code Quality Automation

Create `autofix_code.ps1` for comprehensive fixes:

```powershell
#!/usr/bin/env pwsh
# EQ12 Comprehensive Code Quality Automation

Write-Host "🎨 Running black formatter..." -ForegroundColor Blue
black . --line-length=100

Write-Host "🔧 Running ruff linter and fixer..." -ForegroundColor Green  
ruff check --fix --unsafe-fixes .

Write-Host "📦 Organizing imports..." -ForegroundColor Yellow
isort .

Write-Host "🧹 Removing unused imports..." -ForegroundColor Cyan
autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive . --exclude=envs,research

Write-Host "✨ Running final flake8 check..." -ForegroundColor Magenta
flake8 . --statistics --count --max-line-length=100 --exclude=envs,research

Write-Host "✅ Code quality automation complete!" -ForegroundColor Green
```

### 📊 Current Code Quality Status

Based on the latest flake8 analysis:
- **384 total issues** (down from 10,596+ originally!)  
- **95%+ improvement achieved** 🎉
- Most remaining issues are line length (E501) and syntax errors

### 🎯 Priority Fixes Remaining

1. **Syntax Errors (E999)** - 18 files need manual fixes
2. **Line Length (E501)** - 303 cases, easily fixed with black
3. **Undefined Variables (F821)** - 23 cases, need import fixes
4. **Bare Exceptions (E722)** - 3 cases, add specific exceptions

### 🚀 Performance Benefits vs Visual Basic Studio

| Feature | VS Code + Extensions | Visual Basic Studio |
|---------|---------------------|-------------------|
| **Startup Time** | 2-3 seconds | 15-30 seconds |
| **Memory Usage** | 100-300MB | 1-2GB |
| **AI Integration** | Native Copilot | Limited/None |
| **Cross-platform** | ✅ | ❌ |
| **Modern Tooling** | ✅ | ❌ |
| **API Integration** | Excellent | Poor |
| **Automation Support** | Excellent | Limited |

### 🔧 Next Steps

1. **Run the autofix script**: `.\autofix_code.ps1`
2. **Fix remaining syntax errors** manually
3. **Set up environment variables** for API keys
4. **Configure debugging** for your betting bots
5. **Enable Copilot** for AI-assisted development

### 💡 Pro Tips for EQ12 Development

1. **Use Copilot Chat** for sports betting algorithm help
2. **Set up REST Client files** for API testing
3. **Use Jupyter notebooks** for data analysis
4. **Configure Docker** for isolated environments
5. **Set up Git hooks** for automatic code formatting

This setup gives you a professional, fast, and AI-enhanced development environment perfect for your EQ12 betting automation stack! 🚀