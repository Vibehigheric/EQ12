# PHP Installation Guide for EQ12 Platform

## 🔵 Installing PHP & Composer on Windows

Since PHP is not currently installed on your system, follow these steps to enable the complete tri-language EQ12 platform:

---

## 📥 Installation Options

### Option 1: XAMPP (Recommended for Beginners)

1. **Download XAMPP**
   - Visit: https://www.apachefriends.org/
   - Download the latest version for Windows
   - XAMPP includes PHP, Apache, MySQL, and phpMyAdmin

2. **Install XAMPP**
   - Run the downloaded installer
   - Choose installation directory (default: `C:\xampp`)
   - Select components (PHP is included by default)
   - Complete the installation

3. **Add PHP to PATH**
   ```powershell
   # Add to system PATH environment variable:
   C:\xampp\php
   ```

4. **Install Composer**
   - Visit: https://getcomposer.org/download/
   - Download and run `Composer-Setup.exe`
   - Follow the installation wizard

### Option 2: Standalone PHP Installation

1. **Download PHP**
   - Visit: https://windows.php.net/download/
   - Download "Thread Safe" version (x64)
   - Extract to `C:\php\`

2. **Configure PHP**
   - Copy `php.ini-development` to `php.ini`
   - Enable required extensions:
     ```ini
     extension=curl
     extension=json
     extension=openssl
     extension=mbstring
     ```

3. **Add to PATH**
   ```powershell
   # Add C:\php to system PATH environment variable
   ```

4. **Install Composer**
   - Download from: https://getcomposer.org/
   - Run the installer

### Option 3: Using Chocolatey

```powershell
# If you have Chocolatey package manager:
choco install php composer

# Verify installation
php --version
composer --version
```

---

## ⚡ Quick Setup After PHP Installation

### 1. Verify Installation

```powershell
# Test PHP
php --version     # Should show PHP 8.0+ or 7.4+

# Test Composer
composer --version # Should show Composer 2.x+

# Test basic PHP functionality
php -r "echo 'PHP is working!' . PHP_EOL;"
```

### 2. Install EQ12 PHP Dependencies

```powershell
# Navigate to EQ12 directory
cd C:\EQ12

# Install all required packages
composer install

# This will install:
# - guzzlehttp/guzzle (HTTP client for API requests)
# - Other dependencies as needed
```

### 3. Test the PHP Platform

```powershell
# Test basic PHP functionality (without API key)
php eq12_php_odds_client.php

# Run complete demo (requires ODDS_API_KEY)
php eq12_php_betting_suite.php

# Test using Composer scripts
composer demo
```

### 4. Set Environment Variables

```powershell
# Set API key for Odds API
setx ODDS_API_KEY "your-odds-api-key-here"

# Optional: Set other API keys
setx OPENAI_API_KEY "your-openai-key"
setx TELEGRAM_BOT_TOKEN "your-telegram-token"

# Restart PowerShell after setting environment variables
```

---

## 🎮 VS Code Tasks (After Installation)

Once PHP and Composer are installed, these tasks will be available:

### Setup Tasks
- **EQ12: Install PHP Dependencies** - `composer install`

### Demo Tasks
- **EQ12: PHP Odds Client Demo** - Basic odds client test
- **EQ12: PHP Complete Betting Suite** - Full platform demo
- **EQ12: PHP NFL Analysis** - NFL-specific analysis
- **EQ12: PHP Arbitrage Detection** - Real-time arbitrage scanning

### Master Task
- **EQ12: Ultimate Multi-Language Betting Platform** - Python + Node.js + PHP integration

---

## 🔍 Troubleshooting

### "php is not recognized" Error
- **Solution**: Restart PowerShell/VS Code after PHP installation
- **Alternative**: Add PHP to PATH manually:
  - XAMPP: `C:\xampp\php`
  - Standalone: `C:\php`

### Composer Installation Issues
```powershell
# If Composer installer fails, manual installation:
# 1. Download composer.phar from https://getcomposer.org/composer.phar
# 2. Place in C:\composer\
# 3. Create composer.bat:
echo @php "C:\composer\composer.phar" %* > C:\composer\composer.bat
# 4. Add C:\composer to PATH
```

### Extension Loading Errors
```powershell
# Check which extensions are loaded:
php -m

# If missing extensions, edit php.ini:
# Uncomment lines like: ;extension=curl
# Remove the semicolon: extension=curl
```

---

## 🚀 What You Get After Installation

### Complete PHP Betting Platform
- ✅ Real-time odds API client (600+ lines)
- ✅ Complete betting suite (900+ lines)
- ✅ NFL/NBA analysis engines
- ✅ Arbitrage detection algorithms
- ✅ Live monitoring system
- ✅ Portfolio performance tracking
- ✅ Cross-platform Python and Node.js integration

### Professional Development Environment
- ✅ Composer dependency management
- ✅ PSR-12 coding standards
- ✅ VS Code task integration
- ✅ Comprehensive logging system
- ✅ Error handling and recovery
- ✅ Modern PHP 8+ features

### Tri-Language Platform
- 🐍 **Python**: AI analysis, Google Sheets, ML models
- 🟢 **Node.js**: Real-time performance, efficient APIs
- 🔵 **PHP**: Web integration, robust processing
- 🔗 **Integration**: Shared data, unified workflows

---

## 📊 Platform Status Check

Run this after PHP installation to verify everything works:

```powershell
cd C:\EQ12

# Check PHP version
php --version

# Check Composer version
composer --version

# Install dependencies
composer install

# Test EQ12 platform
php -r "
require_once 'eq12_php_odds_client.php';
echo '🔵 EQ12 PHP Platform: READY' . PHP_EOL;
echo '📦 Required modules: Available' . PHP_EOL;
echo '🔑 API Key: Set ODDS_API_KEY to activate' . PHP_EOL;
echo '🎯 Run: composer demo for full test' . PHP_EOL;
"
```

---

## 💡 Immediate Next Steps

### 1. Install PHP & Composer
- **XAMPP**: https://www.apachefriends.org/ (easiest)
- **Standalone**: https://windows.php.net/download/
- **Composer**: https://getcomposer.org/

### 2. Install EQ12 Dependencies
```powershell
cd C:\EQ12
composer install
```

### 3. Set API Keys
```powershell
setx ODDS_API_KEY "your-key-here"
# Restart PowerShell
```

### 4. Run First Demo
```powershell
composer demo
# Or use VS Code task: "EQ12: PHP Complete Betting Suite"
```

---

## 🏆 Benefits of PHP Integration

### Web Development Advantages
- **Native Web Support**: Built for web applications
- **Database Integration**: Native MySQL, PostgreSQL support
- **Template Engines**: Twig, Smarty for web interfaces
- **Frameworks**: Laravel, Symfony for enterprise apps

### Development Benefits
- **Easy Learning Curve**: C-like syntax, widely adopted
- **Mature Ecosystem**: Vast Packagist package repository
- **Cross-Platform**: Consistent behavior across operating systems
- **Memory Efficient**: Optimized for server-side processing

### Integration Benefits
- **Complements Python & Node.js**: Best of all three worlds
- **Web Dashboard Ready**: Perfect for building betting interfaces
- **API Development**: Excellent for REST API creation
- **Database ORM**: Eloquent, Doctrine for data management

---

**Once PHP and Composer are installed, your EQ12 platform will be the most comprehensive tri-language sports betting automation system available!** 🚀

---

*PHP Installation: Choose XAMPP for easiest setup, or standalone for minimal installation*
