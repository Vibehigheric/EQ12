# EQ12 Clean PHP Development - Ready-to-Drop VS Code Configurations

This directory contains **ready-to-drop** VS Code configurations for clean PHP development with XAMPP, following the "no Java extensions" approach.

## 🎯 Available Configurations

### 1. **EQ12 Project Configuration** (Current)
- **Location**: `C:\EQ12\.vscode\`
- **Purpose**: Sports betting analysis + general PHP development
- **Features**: Full Intelephense, debugging, Python integration

### 2. **XAMPP Web Project Configuration** (Template)
- **Location**: `C:\EQ12\configs\xampp_vscode_template\`
- **Purpose**: General PHP web development
- **Features**: Simplified Intelephense, web debugging only

## 📋 What's Configured

### Core Settings (`settings.json`)
```json
{
  // PHP validation points to XAMPP
  "php.validate.enable": true,
  "php.validate.executablePath": "C:/xampp/php/php.exe", 
  "php.validate.run": "onSave",
  "php.suggest.basic": false,
  
  // Clean Intelephense configuration
  "intelephense.files.exclude": [
    "**/.git/**", "**/node_modules/**", 
    "**/vendor/**", "**/.venv/**"
  ],
  "intelephense.format.enable": true,
  
  // PHP file associations
  "files.associations": {
    "*.inc": "php",
    "*.module": "php"
  },
  "editor.formatOnSave": true
}
```

### Debug Configuration (`launch.json`)
```json
{
  "configurations": [
    {
      "name": "Listen for Xdebug (Apache/XAMPP)",
      "type": "php",
      "request": "launch",
      "port": 9003,
      "hostname": "127.0.0.1",
      "pathMappings": {
        "/xampp/htdocs": "C:/xampp/htdocs"
      }
    },
    {
      "name": "Listen for Xdebug (EQ12 PHP CLI)",
      "type": "php",
      "request": "launch", 
      "port": 9003,
      "hostname": "127.0.0.1",
      "pathMappings": {
        "C:/EQ12": "C:/EQ12"
      }
    }
  ]
}
```

## 🚀 Quick Setup Instructions

### For New Projects:
1. **Copy template**: `xcopy "C:\EQ12\configs\xampp_vscode_template" "C:\your-project\.vscode\" /E /I`
2. **Update paths** in `launch.json` pathMappings if needed
3. **Install extensions**: `code --install-extension bmewburn.vscode-intelephense-client --install-extension xdebug.php-debug`

### For EQ12-like Projects:
1. **Copy current config**: `xcopy "C:\EQ12\.vscode" "C:\your-project\.vscode\" /E /I`
2. **Remove Python settings** if not needed
3. **Update pathMappings** in `launch.json`

## 🔧 Enabling Xdebug (Optional)

### Edit `C:\xampp\php\php.ini`:
```ini
; Xdebug v3 configuration
zend_extension = "C:\xampp\php\ext\php_xdebug.dll"
xdebug.mode = debug
xdebug.start_with_request = yes
xdebug.client_host = 127.0.0.1
xdebug.client_port = 9003
```

### After editing php.ini:
1. **Restart Apache** in XAMPP Control Panel
2. **Test**: Set breakpoint in VS Code, press F5, browse to your PHP file
3. **Verify**: `php -m | grep -i xdebug` should show Xdebug loaded

## ✅ Sanity Check Commands

```powershell
# 1. PHP validation test
php -l C:\your-file.php

# 2. Extension check  
php -m | grep -i intelephense  # (won't show - it's VS Code only)
code --list-extensions | findstr intelephense

# 3. Xdebug status
php -m | grep -i xdebug
```

## 🎯 What You Get

- ✨ **Real-time syntax validation** (errors show inline)
- 🔍 **Full IntelliSense** (auto-completion, go-to-definition, hover info)  
- 🐛 **Step-through debugging** (when Xdebug enabled)
- 📝 **Automatic formatting** on save
- 🚫 **No Java dependencies** (pure PHP + VS Code)
- ⚡ **Fast performance** (optimized file exclusions)

## 📁 Directory Structure

```
.vscode/
├── settings.json      # Main VS Code settings
├── launch.json        # Debug configurations  
└── extensions.json    # Recommended extensions (optional)
```

---

**Result**: Drop-in VS Code configuration for professional PHP development without complexity! 🎉