# EQ12 VS Code Workspace & Profile Automation Guide

## 🚀 **Quick Start - Add EQ12 Folder to Workspace**

### **Option 1: Single Root (Recommended)**
```powershell
# Open EQ12 as single workspace root
code "C:\EQ12"

# Or use the optimal workspace file
code "C:\EQ12\EQ12-GODSTACK-OPTIMAL.code-workspace"
```

### **Option 2: CLI with Profile**
```powershell
# Launch with specific profile
code --new-window --profile "EQ12 Dev (Professional)" "C:\EQ12"
```

---

## 📋 **Available Profiles**

### 🔧 **EQ12 Dev (Professional)** - *Primary Development*
- **Use for**: Daily coding, Copilot assistance, CI/CD pipeline work
- **Features**: Full Ruff + Copilot + PowerShell + Testing
- **Auto-actions**: Format on save, organize imports, lint fixes
- **Launch**: `code --profile "EQ12 Dev (Professional)" C:\EQ12`

### 📊 **EQ12 Data (Heavy)** - *Analysis & Notebooks*
- **Use for**: Jupyter notebooks, CSV analysis, ML experiments
- **Features**: Enhanced Jupyter, CSV tools, Docker support
- **Extensions**: DataWrangler, Rainbow CSV, Jupyter
- **Launch**: `code --profile "EQ12 Data (Heavy)" C:\EQ12`

### 🔍 **EQ12 Triage (Minimal)** - *Fast Debugging*
- **Use for**: Log analysis, quick fixes, performance triage
- **Features**: Minimal extensions, no auto-formatting, fast startup
- **UI**: High contrast, no minimap, simple layout
- **Launch**: `code --profile "EQ12 Triage (Minimal)" C:\EQ12`

### 🔒 **EQ12 Ops (Read-Only)** - *Safe Inspection*
- **Use for**: Production inspection, code reviews, audits
- **Features**: Read-only mode, no Git, no auto-saves
- **Safety**: Cannot modify files accidentally
- **Launch**: `code --profile "EQ12 Ops (Read-Only)" C:\EQ12`

### 🤖 **EQ12 AI/ML (Specialized)** - *Advanced ML Development*
- **Use for**: Model development, advanced AI features
- **Features**: Strict typing, inlay hints, enhanced Copilot
- **Tools**: Enhanced debugging, advanced Python analysis
- **Launch**: `code --profile "EQ12 AI/ML (Specialized)" C:\EQ12`

---

## ⚡ **Automated Tasks**

All tasks available via **Command Palette** (`Ctrl+Shift+P`) → **Tasks: Run Task**

### 🛠️ **Core Automation**
- **`EQ12: Bootstrap Environment`** - Sets up venv, installs dependencies
- **`EQ12: CI/CD Pipeline`** - Runs full pipeline (format + lint + test + security)
- **`EQ12: System Validation`** - Validates environment health
- **`EQ12: Lint & Format`** - Quick code cleanup with Ruff

### 🧪 **Testing & Quality**
- **`EQ12: Run Tests (Fast)`** - Quick pytest execution
- **`EQ12: Full Setup & Validation`** - Complete bootstrap → test → validation

### 🎯 **Sports Betting Specialized**
- **`EQ12: Run Firefox Governance Setup`** - Browser automation
- **`EQ12: Chrome Daily Refresh + Launch`** - Chrome governance automation
- **`EQ12: AI Security Audit`** - AI-powered security analysis

---

## 🏗️ **Workspace Architecture**

### **Single Root Philosophy** ✅
```
C:\EQ12\                          # Single workspace root
├── .vscode/                      # Workspace configuration
│   ├── settings.json            # Enhanced with profiles
│   ├── tasks.json               # Comprehensive automation
│   ├── launch.json              # Debug configurations
│   └── profiles/                # Custom profile definitions
├── scripts/                     # Python automation scripts
├── tests/                       # Test suite
├── configs/                     # Configuration files
├── logs/                        # Runtime logs
└── EQ12-GODSTACK-OPTIMAL.code-workspace  # Optimal workspace file
```

### **Multi-Root Alternative** (Optional)
```json
{
  "folders": [
    { "name": "EQ12 Root", "path": "C:\\EQ12" }
  ],
  "settings": {
    "python.defaultInterpreterPath": "C:\\EQ12\\.venv\\Scripts\\python.exe"
  }
}
```

---

## 🔄 **Automation Workflows**

### **On Workspace Open** (Automatic)
1. ✅ **Bootstrap Environment** task runs automatically
2. ✅ Virtual environment activation check
3. ✅ Dependencies validation
4. ✅ Python interpreter pinning

### **On File Save** (Automatic)
1. ✅ **Ruff format** (Python files)
2. ✅ **Import organization** (Python)
3. ✅ **Lint fixes** (auto-fixable issues)
4. ✅ **Trailing whitespace cleanup** (all files)
5. ✅ **Final newline insertion** (all files)

### **On Debug Launch** (Pre-Launch)
1. ✅ **System Validation** (ensures environment health)
2. ✅ **Environment variables** (PYTHONPATH, EQ12_ROOT)
3. ✅ **Working directory** (set to workspace root)

---

## 🎮 **Hotkeys & Shortcuts**

### **Profile Management**
- **`Ctrl+Shift+P`** → **"Profiles: New Window with Profile"**
- **`Ctrl+Shift+P`** → **"Profiles: Switch Profile"**
- **`Ctrl+Shift+P`** → **"Profiles: Export Profile"**

### **Task Execution**
- **`Ctrl+Shift+P`** → **"Tasks: Run Task"**
- **`Ctrl+Shift+B`** → **Default Build Task** (Bootstrap Environment)
- **`Ctrl+Shift+T`** → **Test Task**

### **EQ12 Specialized**
- **`F5`** → **Debug Current File** (with pre-launch validation)
- **`Ctrl+F5`** → **Run Current File** (no debugging)

---

## 🔧 **Configuration Files**

### **Enhanced Settings** (`C:\EQ12\.vscode\settings.json`)
```json
{
  "python.defaultInterpreterPath": "C:\\EQ12\\.venv\\Scripts\\python.exe",
  "ruff.nativeServer": "on",
  "editor.formatOnSave": true,
  "github.copilot.enable": { "*": true },
  // ... comprehensive automation settings
}
```

### **Task Automation** (`C:\EQ12\.vscode\tasks.json`)
```json
{
  "tasks": [
    {
      "label": "EQ12: Bootstrap Environment",
      "command": "powershell",
      "runOptions": { "runOn": "folderOpen" }
    }
  ]
}
```

### **Debug Configuration** (`C:\EQ12\.vscode\launch.json`)
```json
{
  "configurations": [
    {
      "name": "EQ12: Debug Current File",
      "preLaunchTask": "EQ12: System Validation"
    }
  ]
}
```

---

## 📈 **Benefits for EQ12 Development**

### **🎯 Consistency**
- **Same interpreter** across all folders (`C:\EQ12\.venv\Scripts\python.exe`)
- **Unified settings** prevent "different interpreters per folder" issues
- **Profile isolation** prevents extension conflicts

### **⚡ Productivity**
- **Auto-bootstrap** on workspace open
- **Format-on-save** with Ruff (no manual formatting)
- **One-click** CI/CD pipeline execution
- **Integrated testing** with pytest

### **🛡️ Safety**
- **Read-only profile** for production inspection
- **Environment validation** before debugging
- **Unicode handling** (resolved encoding issues)
- **Comprehensive error checking**

### **🤖 AI Enhancement**
- **GitHub Copilot** optimized for sports betting domain
- **Context-aware** suggestions with EQ12 codebase
- **Profile-specific** AI assistance levels

---

## 🚀 **Next Steps**

1. **Import a profile**:
   ```powershell
   # Command Palette → "Profiles: Import Profile"
   # Select: C:\EQ12\.vscode\profiles\EQ12-Dev-Professional.code-profile
   ```

2. **Open workspace**:
   ```powershell
   code "C:\EQ12\EQ12-GODSTACK-OPTIMAL.code-workspace"
   ```

3. **Trigger bootstrap**:
   ```powershell
   # Command Palette → "Tasks: Run Task" → "EQ12: Bootstrap Environment"
   ```

4. **Validate setup**:
   ```powershell
   # Command Palette → "Tasks: Run Task" → "EQ12: System Validation"
   ```

---

## 🔍 **Troubleshooting**

### **Profile Import Issues**
- Ensure profile files are in `C:\EQ12\.vscode\profiles\`
- Use **Command Palette** → **"Profiles: Import Profile"**
- Restart VS Code after import

### **Task Automation Issues**
- Check **Terminal** → **Output** → **Tasks** for error details
- Verify PowerShell execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Ensure virtual environment exists: `C:\EQ12\.venv\`

### **Extension Conflicts**
- Use **Triage profile** to isolate issues
- Check **Extensions** view for conflicting extensions
- Disable workspace extensions if needed

---

## 📚 **Advanced Usage**

### **Custom Profile Creation**
```json
{
  "name": "My EQ12 Profile",
  "settings": {
    "python.defaultInterpreterPath": "C:\\EQ12\\.venv\\Scripts\\python.exe"
  },
  "extensions": ["ms-python.python", "charliermarsh.ruff"]
}
```

### **Workspace Policies**
- **`.editorconfig`** - Enforces formatting standards
- **`pyproject.toml`** - Ruff configuration
- **`CODEOWNERS`** - Review gates
- **Pre-commit hooks** - Git automation

---

**🎉 Your EQ12 workspace is now optimized for professional sports betting automation development!**
