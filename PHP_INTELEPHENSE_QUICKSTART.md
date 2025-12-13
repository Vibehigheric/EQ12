# EQ12 PHP with Intelephense - Quick Start

## 🚀 What's Configured

Your EQ12 stack now includes **Intelephense** - the fastest PHP language server for VS Code. No Java required!

## 📦 Installed Components

### VS Code Extensions
- `bmewburn.vscode-intelephense-client` - PHP IntelliSense

### PHP Development Tools (via Composer)
- `phpunit/phpunit` - Unit testing framework
- `phpstan/phpstan` - Static analysis
- `squizlabs/php_codesniffer` - Code style checker
- `friendsofphp/php-cs-fixer` - Code style fixer

### Configuration Files
- `.vscode/settings.json` - Intelephense configuration
- `.php-cs-fixer.php` - Code style rules
- `composer.json` - Dependencies and scripts

## 🔧 Quick Setup

Run the setup script:
```powershell
.\Setup-EQ12-Intelephense.ps1
```

Or manually:
```powershell
# Install extension
code --install-extension bmewburn.vscode-intelephense-client

# Install PHP dependencies
composer install --dev
```

## 🎯 Daily Workflow

### Available Tasks (Ctrl+Shift+P → "Tasks: Run Task")

1. **PHP: Lint Check** - Check syntax of current file
2. **PHP: Lint All Files** - Check all PHP files
3. **PHP: Code Style Fix** - Auto-format code
4. **PHP: Run Tests** - Execute PHPUnit tests
5. **PHP: Install Dependencies** - Run composer install

### Composer Scripts
```bash
composer demo          # Run betting suite demo
composer test          # Run PHPUnit tests
composer cs            # Check code style
composer cs-fix        # Fix code style
composer stan          # Static analysis
```

## 🏒 EQ12 PHP Files

Your main PHP betting files:
- `eq12_php_odds_client.php` - Odds API integration
- `eq12_php_betting_suite.php` - Betting analysis suite
- `EdgeGodParlays/` - Parlay optimization
- `samples-php/` - Example implementations

## ⚡ Performance Tips

### If Intelephense feels slow:
1. **Clear cache**: Task → "PHP: Clear Intelephense Cache"
2. **Restart VS Code** after major composer changes
3. **Exclude large folders**: Already configured in settings

### Configuration is optimized for:
- XAMPP PHP 8.2+ at `C:\xampp\php\`
- EQ12 folder structure with exclusions
- Memory limit: 8GB for large projects
- Common PHP extensions (curl, json, mysqli, etc.)

## 🎁 Premium Features ($35 one-time)

**Free features** (already working):
- Autocomplete, hover info, diagnostics
- Go to definition, find references
- Format on save, syntax checking

**Premium features** (worth it for refactoring):
- **Rename symbol** across files safely
- **Go to implementation/declaration**
- **Code actions** and smart selections
- **Type hierarchy** navigation

Get license key at: https://intelephense.com

Add to settings.json:
```json
"intelephense.licenceKey": "your-license-key-here"
```

## 🔍 Troubleshooting

### Common Issues:

**"Undefined function/class" warnings:**
```powershell
composer dump-autoload -o
# Then: Task → "PHP: Clear Intelephense Cache"
```

**Path issues:**
- Verify XAMPP at `C:\xampp\php\php.exe`
- Update `intelephense.environment.phpVersion` in settings

**Memory issues:**
- Increase `intelephense.files.maxMemory` in settings
- Add more folders to `intelephense.files.exclude`

### Force refresh:
1. Ctrl+Shift+P → "Intelephense: Clear Cache"
2. Restart VS Code
3. Re-run `composer dump-autoload -o`

## 🎯 Integration with EQ12

Intelephense works seamlessly with your existing EQ12 tools:
- **Python betting engine** - PHP provides web dashboard
- **PowerShell automation** - PHP handles API endpoints
- **XAMPP development** - Local testing environment
- **Odds API integration** - PHP client libraries

## 📁 Folder Structure

```
C:\EQ12\
├── .vscode/
│   ├── settings.json         # Intelephense config
│   └── tasks.json           # PHP workflow tasks
├── .php-cs-fixer.php       # Code style config
├── composer.json            # Dependencies
├── eq12_php_odds_client.php # Main odds client
├── eq12_php_betting_suite.php # Betting suite
└── vendor/                  # Composer packages
```

## 🚀 Next Steps

1. **Open any .php file** - See autocomplete in action
2. **Try Tasks** - Ctrl+Shift+P → "Tasks: Run Task"
3. **Run demos** - `composer demo` or `composer odds-client`
4. **Consider Premium** - For advanced refactoring workflows
5. **Integrate with dashboard** - Build PHP endpoints for your betting data

---

**EQ12 Stack: Python + PowerShell + PHP + JavaScript = Complete automation platform** 🎯
