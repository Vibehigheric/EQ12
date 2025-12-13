# EQ12 PHP Development Setup: VS Code + XAMPP Integration
## Clean, No-Nonsense PHP Development on Windows

**Professional PHP development environment for EQ12 project with XAMPP integration, no Java dependencies.**

---

## 🎯 Quick Setup Overview

This setup gives you:
- ✅ **Professional IntelliSense** with Intelephense (type hints, auto-completion, error detection)
- ✅ **Step-through debugging** with Xdebug integration
- ✅ **Real-time error checking** with PHP linting on save
- ✅ **Zero Java extensions** - pure PHP tooling
- ✅ **EQ12 project optimization** with betting-specific configurations

---

## 1️⃣ Point VS Code at Your PHP

You already have PHP with XAMPP. Tell VS Code where to find it:

### Method 1: VS Code Settings UI
1. Open VS Code → `Ctrl+,` → search "php validate"
2. Click "Edit in settings.json" under **PHP › Validate: Executable Path**
3. Add the configuration below

### Method 2: Direct settings.json Edit
Open VS Code settings (`Ctrl+Shift+P` → "Preferences: Open Settings (JSON)") and add:

```json
{
  "php.validate.enable": true,
  "php.validate.executablePath": "C:/xampp/php/php.exe",
  "php.validate.run": "onSave",
  "php.suggest.basic": false
}
```

> 💡 **Path Tip**: If XAMPP is installed elsewhere, adjust the path (e.g., `"D:/xampp/php/php.exe"`)

---

## 2️⃣ Install Essential Extensions

### PowerShell Installation (Recommended)
```powershell
# Core PHP extensions
code --install-extension bmewburn.vscode-intelephense-client
code --install-extension xdebug.php-debug

# Optional but recommended for EQ12
code --install-extension ms-vscode.vscode-json
code --install-extension bradlc.vscode-tailwindcss
```

### VS Code Marketplace Alternative
1. Open Extensions (`Ctrl+Shift+X`)
2. Search and install:
   - **Intelephense** by Ben Mewburn
   - **PHP Debug** by Xdebug

---

## 3️⃣ Configure Intelephense for Maximum Performance

Add to your VS Code `settings.json`:

```json
{
  "php.suggest.basic": false,
  "intelephense.files.exclude": [
    "**/.git/**", 
    "**/node_modules/**", 
    "**/vendor/**", 
    "**/.venv/**",
    "**/logs/**",
    "**/data/**"
  ],
  "intelephense.format.enable": true,
  "intelephense.completion.insertUseDeclaration": true,
  "intelephense.completion.fullyQualifyGlobalConstantsAndFunctions": false,
  "intelephense.diagnostics.enable": true,
  "intelephense.diagnostics.run": "onSave",
  "intelephense.environment.phpVersion": "8.2",
  "intelephense.stubs": [
    "apache",
    "bcmath", 
    "Core",
    "curl",
    "date",
    "dom",
    "fileinfo",
    "filter",
    "gd",
    "hash",
    "iconv",
    "json",
    "libxml",
    "mbstring",
    "mcrypt",
    "mysql",
    "mysqli",
    "openssl",
    "pcre",
    "PDO",
    "pdo_mysql",
    "Phar",
    "readline",
    "Reflection",
    "session",
    "SimpleXML",
    "sockets",
    "sodium",
    "SPL",
    "standard",
    "superglobals",
    "tokenizer",
    "xml",
    "xdebug",
    "xmlreader",
    "xmlwriter",
    "yaml",
    "zip",
    "zlib"
  ]
}
```

---

## 4️⃣ Enable Xdebug for Step Debugging

### Configure XAMPP's php.ini

1. Open `C:\xampp\php\php.ini` in a text editor
2. Find the Xdebug section (usually at the bottom)
3. Replace or add these lines:

```ini
; --- Xdebug v3 Configuration ---
zend_extension = "C:\xampp\php\ext\php_xdebug.dll"
xdebug.mode = debug,develop
xdebug.start_with_request = yes
xdebug.client_host = 127.0.0.1
xdebug.client_port = 9003
xdebug.log_level = 0
xdebug.idekey = VSCODE

; Performance settings
xdebug.max_nesting_level = 512
xdebug.var_display_max_depth = 10
xdebug.var_display_max_children = 256
xdebug.var_display_max_data = 1024
```

4. **Restart Apache** through XAMPP Control Panel
5. Verify by creating a test file with `<?php phpinfo(); ?>` - you should see Xdebug listed

### VS Code Debug Configuration

Create `.vscode/launch.json` in your project root:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "🌐 Listen for Xdebug (Apache/XAMPP)",
      "type": "php",
      "request": "launch",
      "port": 9003,
      "hostname": "127.0.0.1",
      "pathMappings": {
        "/xampp/htdocs": "C:/xampp/htdocs"
      },
      "xdebugSettings": {
        "max_children": 256,
        "max_data": 1024,
        "max_depth": 10
      }
    },
    {
      "name": "🔧 EQ12 PHP CLI Debugging", 
      "type": "php",
      "request": "launch",
      "port": 9003,
      "hostname": "127.0.0.1",
      "pathMappings": {
        "C:/EQ12": "C:/EQ12"
      },
      "program": "${file}",
      "cwd": "${workspaceFolder}",
      "args": [],
      "runtimeArgs": [
        "-dxdebug.start_with_request=yes",
        "-dxdebug.mode=debug"
      ]
    },
    {
      "name": "🎲 EQ12 Sports Betting Scripts",
      "type": "php", 
      "request": "launch",
      "port": 9003,
      "hostname": "127.0.0.1",
      "pathMappings": {
        "C:/EQ12": "C:/EQ12"
      },
      "program": "${workspaceFolder}/scripts/eq12_odds_analyzer.php",
      "cwd": "${workspaceFolder}",
      "env": {
        "ODDS_API_KEY": "${env:ODDS_API_KEY}",
        "EQ12_ENV": "development"
      }
    }
  ]
}
```

---

## 5️⃣ EQ12-Specific Workspace Configuration

Create `.vscode/settings.json` in your EQ12 project root:

```json
{
  "files.associations": {
    "*.inc": "php",
    "*.module": "php",
    "*.install": "php",
    "*.profile": "php",
    "*.view": "php"
  },
  "editor.formatOnSave": true,
  "editor.formatOnPaste": true,
  "editor.insertSpaces": true,
  "editor.tabSize": 4,
  "editor.detectIndentation": false,
  
  "php.validate.enable": true,
  "php.validate.executablePath": "C:/xampp/php/php.exe",
  "php.validate.run": "onSave",
  
  "intelephense.environment.includePaths": [
    "C:/EQ12/scripts",
    "C:/EQ12/configs", 
    "C:/xampp/htdocs"
  ],
  "intelephense.files.maxSize": 10000000,
  "intelephense.completion.triggerParameterHints": true,
  
  "search.exclude": {
    "**/logs/**": true,
    "**/data/**": true,
    "**/.git/**": true,
    "**/vendor/**": true
  },
  
  "files.exclude": {
    "**/.DS_Store": true,
    "**/Thumbs.db": true,
    "**/.phpunit.result.cache": true
  },
  
  "emmet.includeLanguages": {
    "php": "html"
  }
}
```

---

## 6️⃣ Quick Sanity Checks

### Test PHP Validation
1. Create `C:\EQ12\test_php_setup.php`:
```php
<?php
// Test file for EQ12 PHP setup validation
declare(strict_types=1);

class EQ12TestSetup 
{
    private string $message;
    
    public function __construct(string $message = "EQ12 PHP Setup Working!") 
    {
        $this->message = $message;
    }
    
    public function validate(): array 
    {
        return [
            'php_version' => PHP_VERSION,
            'xdebug_loaded' => extension_loaded('xdebug'),
            'xampp_detected' => file_exists('C:/xampp/php/php.exe'),
            'message' => $this->message,
            'timestamp' => date('Y-m-d H:i:s')
        ];
    }
}

$test = new EQ12TestSetup();
var_dump($test->validate());

// Intentional error for testing linting
// $undefined_variable->someMethod(); // Uncomment to test error detection
?>
```

2. Open the file in VS Code
3. Save (`Ctrl+S`) → Should see real-time error checking
4. Type `$test->` → Should see method suggestions

### Test Debugging
1. Set a breakpoint on the `var_dump` line
2. Run "EQ12 PHP CLI Debugging" from Debug panel (`F5`)
3. VS Code should stop at the breakpoint

### Test Web Debugging
1. Copy the test file to `C:\xampp\htdocs\eq12_test.php`
2. Start Apache in XAMPP
3. Set breakpoint and visit `http://localhost/eq12_test.php`
4. VS Code should catch the breakpoint

---

## 7️⃣ EQ12 Sports Betting Specific Setup

### Odds API Integration
Create `C:\EQ12\configs\php_odds_config.php`:

```php
<?php
/**
 * EQ12 Odds API Configuration
 * Professional PHP setup for sports betting data processing
 */
declare(strict_types=1);

namespace EQ12\Config;

class OddsApiConfig 
{
    public const API_BASE_URL = 'https://api.the-odds-api.com/v4';
    public const SUPPORTED_SPORTS = [
        'americanfootball_nfl',
        'basketball_nba', 
        'icehockey_nhl',
        'baseball_mlb'
    ];
    
    public static function getApiKey(): ?string 
    {
        return $_ENV['ODDS_API_KEY'] ?? null;
    }
    
    public static function getHeaders(): array 
    {
        return [
            'Content-Type' => 'application/json',
            'User-Agent' => 'EQ12-OddsAnalyzer/1.0'
        ];
    }
}
```

### Type Definitions for Betting
Create `C:\EQ12\scripts\eq12_betting_types.php`:

```php
<?php
/**
 * EQ12 Betting Type Definitions
 * Comprehensive type safety for sports betting operations
 */
declare(strict_types=1);

namespace EQ12\Types;

class AmericanOdds 
{
    public function __construct(
        public readonly int $value,
        public readonly float $impliedProbability,
        public readonly float $decimalEquivalent
    ) {}
    
    public static function fromValue(int $odds): self 
    {
        $implied = $odds > 0 
            ? 100 / ($odds + 100)
            : (-$odds) / ((-$odds) + 100);
            
        $decimal = $odds > 0
            ? ($odds / 100) + 1
            : (100 / (-$odds)) + 1;
            
        return new self($odds, $implied, $decimal);
    }
}

class BettingLine 
{
    public function __construct(
        public readonly string $bookmaker,
        public readonly AmericanOdds $homeOdds,
        public readonly AmericanOdds $awayOdds,
        public readonly \DateTimeImmutable $timestamp
    ) {}
}

interface OddsCalculator 
{
    public function calculateArbitrage(array $lines): ?float;
    public function findValueBets(array $lines, float $threshold): array;
    public function getKellyCriterion(AmericanOdds $odds, float $trueProbability, float $bankroll): float;
}
```

---

## 8️⃣ Composer Integration (Optional)

If you use Composer for dependencies:

1. **Install Composer** (if not already installed): https://getcomposer.org/download/
2. **Create** `C:\EQ12\composer.json`:

```json
{
    "name": "eq12/sports-betting-analyzer",
    "description": "EQ12 Sports Betting Analysis Tools",
    "type": "project",
    "require": {
        "php": ">=8.2",
        "ext-curl": "*",
        "ext-json": "*",
        "guzzlehttp/guzzle": "^7.0"
    },
    "require-dev": {
        "phpunit/phpunit": "^10.0",
        "phpstan/phpstan": "^1.0"
    },
    "autoload": {
        "psr-4": {
            "EQ12\\": "scripts/",
            "EQ12\\Config\\": "configs/",
            "EQ12\\Tests\\": "tests/"
        }
    },
    "config": {
        "optimize-autoloader": true,
        "sort-packages": true
    }
}
```

3. **Run** `composer install` in `C:\EQ12\`

4. **Update Intelephense settings** to include Composer autoloading:

```json
{
  "intelephense.files.exclude": [
    "**/.git/**", 
    "**/node_modules/**", 
    "**/.venv/**",
    "**/logs/**",
    "**/data/**"
  ]
}
```

Note: Removed `**/vendor/**` from exclusions so Intelephense can analyze dependencies.

---

## 9️⃣ Troubleshooting

### Common Issues & Solutions

**❌ "PHP executable not found"**
- Verify XAMPP installation path in settings
- Ensure `C:\xampp\php\php.exe` exists
- Restart VS Code after changing settings

**❌ Xdebug not working**
- Check `php.ini` configuration
- Restart Apache after changes
- Verify port 9003 is not blocked by firewall
- Test with `php -m | findstr xdebug` in terminal

**❌ Intelephense not providing suggestions**
- Check if PHP files are properly associated
- Verify workspace trust settings
- Clear Intelephense cache: `Ctrl+Shift+P` → "Intelephense: Clear Cache"

**❌ Performance issues with large projects**
- Increase `intelephense.files.maxSize` limit
- Add more specific exclusions to `intelephense.files.exclude`
- Consider excluding large data directories

### Performance Optimization

Add to your workspace `settings.json`:

```json
{
  "intelephense.trace.server": "off",
  "intelephense.files.maxSize": 5000000,
  "intelephense.maxMemory": 1024,
  "search.followSymlinks": false,
  "search.useIgnoreFiles": true
}
```

---

## 🎉 You're Ready!

Your VS Code + XAMPP + EQ12 setup now includes:

- ✅ **Professional IntelliSense** with type hints and auto-completion
- ✅ **Real-time error detection** and PHP linting
- ✅ **Step-through debugging** for both web and CLI scripts
- ✅ **EQ12-optimized configurations** for sports betting development
- ✅ **Zero Java dependencies** - pure PHP tooling
- ✅ **Production-ready settings** following EQ12 standards

### Next Steps:

1. **Test the setup** with the provided validation scripts
2. **Create your first EQ12 odds analyzer script**
3. **Set up automated testing** with PHPUnit (optional)
4. **Integrate with EQ12 logging standards** for production monitoring

---

**Happy coding with your professional PHP development environment! 🚀**

*For more EQ12 resources and advanced configurations, check the [EQ12 documentation](https://github.com/eq12/documentation).*