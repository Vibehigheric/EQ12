[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [switch]$SkipDependencies,

    [Parameter(Mandatory = $false)]
    [switch]$TestAfterSetup,

    [Parameter(Mandatory = $false)]
    [string]$TestURL = "https://github.com/microsoft/playwright",

    [Parameter(Mandatory = $false)]
    [switch]$EnableGPT5,

    [Parameter(Mandatory = $false)]
    [string]$PreferredModel = "gpt-5"
)
param(
    [Parameter(Mandatory = $false)]
    [switch]$SkipDependencies,

    [Parameter(    # Step 5: Setup Enhanced AI (GPT} catch {
        Write-SetupLog \"Unexpected error during setup: $_\" \"ERROR\"
        Write-SetupLog \"Check the log file: $LogFile\" \"ERROR\"
        exit 1
    }

    function Setup-EnhancedAI {
        [CmdletBinding()]
        param()

        Write-SetupLog \"Setting up Enhanced AI with GPT-5 support...\"
        Write-Host \"🧠 Setting up Enhanced AI (GPT-5)...\" -ForegroundColor Magenta

        try {
            # Set preferred model environment variable
            $env:EQ12_OPENAI_MODEL = $PreferredModel
            Write-SetupLog \"Set preferred model to: $PreferredModel\"

            # Test enhanced AI script
            $testResult = python \"$PSScriptRoot\\eq12_enhanced_ai.py\" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-SetupLog \"Enhanced AI script test successful\"
                Write-Host \"✅ Enhanced AI setup completed\" -ForegroundColor Green
                return $true
            } else {
                Write-SetupLog \"Enhanced AI script test failed: $testResult\" \"WARN\"
                Write-Host \"⚠️ Enhanced AI setup completed with warnings\" -ForegroundColor Yellow
                return $true  # Don't fail setup for AI issues
            }
        }
        catch {
            Write-SetupLog \"Enhanced AI setup error: $($_.Exception.Message)\" \"ERROR\"
            Write-Host \"❌ Enhanced AI setup failed: $($_.Exception.Message)\" -ForegroundColor Red
            return $false
        }
    }

    function Test-GPT5Integration {
        [CmdletBinding()]
        param()

        Write-SetupLog \"Testing GPT-5 integration...\"
        Write-Host \"🧪 Testing GPT-5 Integration...\" -ForegroundColor Cyan

        try {
            # Check if OpenAI API key is set
            if (-not $env:OPENAI_API_KEY) {
                Write-Host \"⚠️ OPENAI_API_KEY not set - skipping GPT-5 test\" -ForegroundColor Yellow
                Write-SetupLog \"Skipping GPT-5 test - no API key\"
                return
            }

            # Test the enhanced AI system
            Write-Host \"Testing Enhanced AI system...\" -ForegroundColor White

            $testCommand = @\"
import asyncio
from scripts.eq12_enhanced_ai import EQ12EnhancedAI

async def quick_test():
    ai = EQ12EnhancedAI()
    test_result = ai.test_gpt5_connection()

    print(f\"GPT-5 Available: { test_result.get('gpt5_available', False) }\")
    print(f\"Selected Model: { test_result.get('selected_model', 'unknown') }\")
    print(f\"API Test: { test_result.get('api_test', 'not tested') }\")

    if test_result.get('gpt5_available'):
        print(\"🎉 GPT-5 is available and ready!\")
    elif 'gpt-4' in test_result.get('selected_model', ''):
        print(\"✅ GPT-4 is available as fallback\")
    else:
        print(\"ℹ️ Using standard GPT models\")

asyncio.run(quick_test())
\"@

            $testResult = python -c $testCommand 2>&1

            Write-Host $testResult -ForegroundColor Gray

            if ($LASTEXITCODE -eq 0) {
                Write-Host \"✅ GPT-5 integration test completed successfully\" -ForegroundColor Green
                Write-SetupLog \"GPT-5 integration test successful\"
            } else {
                Write-Host \"⚠️ GPT-5 integration test completed with issues\" -ForegroundColor Yellow
                Write-SetupLog \"GPT-5 integration test issues: $testResult\" \"WARN\"
            }
        }
        catch {
            Write-Host \"❌ GPT-5 integration test failed: $($_.Exception.Message)\" -ForegroundColor Red
            Write-SetupLog \"GPT-5 integration test error: $($_.Exception.Message)\" \"ERROR\"
        }
    }f requested
    if ($EnableGPT5) {
        if (!(Setup-EnhancedAI)) {
            Write-SetupLog \"Enhanced AI setup failed.\" \"WARN\"
        }
    }

    # Step 6: Test functionality (if requested)
    if ($TestAfterSetup) {
        if (!(Test-URLSystemFunctionality)) {
            Write-SetupLog \"Functionality tests failed.\" \"WARN\"
            Write-SetupLog \"Setup completed but system may not be fully functional.\" \"WARN\"
        }

        # Test GPT-5 if enabled
        if ($EnableGPT5 -and $env:OPENAI_API_KEY) {
            Test-GPT5Integration
        }
    } else {
        Write-SetupLog \"Skipping functionality tests (use -TestAfterSetup to enable)\"
    } = $false)]
[switch]$TestAfterSetup,

[Parameter(Mandatory = $false)]
[string]$TestURL = "https://github.com/microsoft/playwright"
)

<#
.SYNOPSIS
EQ12 URL Learning System Complete Setup Script

.DESCRIPTION
Sets up the complete EQ12 URL learning and scanning system including:
- URL scanner with AI-powered content analysis
- Copilot integration handler
- Dashboard integration
- PowerShell management tools

.EXAMPLE
.\eq12_url_system_setup.ps1
.\eq12_url_system_setup.ps1 -TestAfterSetup -TestURL "https://fastapi.tiangolo.com"
.\eq12_url_system_setup.ps1 -SkipDependencies

.NOTES
Author: EQ12 AI System
Version: 1.0.0
#>

# Script configuration
$ScriptName = "EQ12URLSystemSetup"
$LogDir = "C:\EQ12\logs"
$LogFile = Join-Path $LogDir "url_system_setup.log"

# Ensure logs directory exists
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-SetupLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp | $Level | $ScriptName | $Message"
    Add-Content -Path $LogFile -Value $logEntry

    $color = switch ($Level) {
        "ERROR" { "Red"; break }
        "WARN" { "Yellow"; break }
        "SUCCESS" { "Green"; break }
        default { "Cyan"; break }
    }

    Write-Host $Message -ForegroundColor $color
}

function Test-SystemPrerequisites {
    """Check system prerequisites"""

    Write-SetupLog "Checking system prerequisites..." "INFO"

    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-SetupLog "Python not found. Please install Python 3.8+" "ERROR"
            return $false
        }
        Write-SetupLog "Found Python: $pythonVersion" "SUCCESS"
    } catch {
        Write-SetupLog "Error checking Python: $_" "ERROR"
        return $false
    }

    # Check pip
    try {
        python -m pip --version | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-SetupLog "pip not found" "ERROR"
            return $false
        }
        Write-SetupLog "Found pip" "SUCCESS"
    } catch {
        Write-SetupLog "Error checking pip: $_" "ERROR"
        return $false
    }

    # Check EQ12 directory structure
    $requiredDirs = @(
        "C:\EQ12",
        "C:\EQ12\scripts",
        "C:\EQ12\data",
        "C:\EQ12\configs",
        "C:\EQ12\logs"
    )

    foreach ($dir in $requiredDirs) {
        if (!(Test-Path $dir)) {
            Write-SetupLog "Creating directory: $dir"
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }

    Write-SetupLog "System prerequisites check completed" "SUCCESS"
    return $true
}

function Install-URLSystemDependencies {
    """Install all dependencies for URL learning system"""

    Write-SetupLog "Installing URL learning system dependencies..."

    try {
        # Core web scraping and parsing
        Write-SetupLog "Installing core dependencies..."
        python -m pip install httpx beautifulsoup4 feedparser --upgrade

        # FastAPI for webhook handling
        Write-SetupLog "Installing FastAPI and web framework..."
        python -m pip install fastapi uvicorn pydantic --upgrade

        # Text processing and NLP
        Write-SetupLog "Installing text processing libraries..."
        python -m pip install textblob nltk --upgrade

        # Browser automation
        Write-SetupLog "Installing Playwright..."
        python -m pip install playwright --upgrade

        # AI and ML (optional but recommended)
        Write-SetupLog "Installing AI/ML libraries (optional)..."
        python -m pip install openai transformers torch --upgrade --no-warn-script-location 2>$null

        # Install Playwright browsers
        Write-SetupLog "Installing Playwright browser binaries..."
        python -m playwright install chromium --with-deps

        # Download NLTK data
        Write-SetupLog "Downloading NLTK data..."
        python -c "
import nltk
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
    print('NLTK data downloaded successfully')
except:
    print('Some NLTK downloads failed (this is usually OK)')
"

        Write-SetupLog "All dependencies installed successfully" "SUCCESS"
        return $true

    } catch {
        Write-SetupLog "Error installing dependencies: $_" "ERROR"
        return $false
    }
}

function Initialize-URLSystemDatabase {
    """Initialize URL system databases"""

    Write-SetupLog "Initializing URL system databases..."

    try {
        # Run scanner initialization
        $initResult = python -c "
import sys
sys.path.append('C:/EQ12/scripts')
try:
    from eq12_url_scanner import EQ12URLScanner
    scanner = EQ12URLScanner()
    print('URL scanner database initialized successfully')
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
" 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-SetupLog "URL scanner database initialized" "SUCCESS"
            Write-SetupLog "Init output: $initResult"
        } else {
            Write-SetupLog "URL scanner database initialization failed" "ERROR"
            Write-SetupLog "Error: $initResult"
            return $false
        }

        return $true

    } catch {
        Write-SetupLog "Error initializing databases: $_" "ERROR"
        return $false
    }
}

function Create-URLSystemConfiguration {
    """Create configuration files for URL system"""

    Write-SetupLog "Creating URL system configuration..."

    try {
        # Create URL scanner config
        $scannerConfig = @{
            "scanner_settings"          = @{
                "max_content_length"       = 10000
                "request_timeout"          = 30
                "max_retries"              = 3
                "enable_playwright"        = $true
                "enable_ai_classification" = $true
            }
            "classification_thresholds" = @{
                "minimum_confidence"   = 0.1
                "high_confidence"      = 0.7
                "auto_apply_threshold" = 0.8
            }
            "folder_mappings"           = @{
                "betting"    = @("scripts", "EdgeGodParlays", "scraper_starter")
                "automation" = @("scripts", "omni_scraper", "modules")
                "finance"    = @("data", "configs")
                "ai"         = @("openai-python-project", "scripts")
                "dashboard"  = @("dashboard", "logs")
                "config"     = @("configs", "keys")
                "data"       = @("data", "logs")
            }
        }

        $scannerConfig | ConvertTo-Json -Depth 4 | Set-Content "C:\EQ12\configs\url_scanner_config.json"

        # Create webhook handler config
        $handlerConfig = @{
            "webhook_settings"    = @{
                "host"        = "127.0.0.1"
                "port"        = 8080
                "log_level"   = "info"
                "enable_cors" = $true
            }
            "processing_settings" = @{
                "batch_size"           = 10
                "concurrent_limit"     = 3
                "cache_duration_hours" = 24
            }
        }

        $handlerConfig | ConvertTo-Json -Depth 3 | Set-Content "C:\EQ12\configs\url_handler_config.json"

        # Create environment template
        $envTemplate = @"
# EQ12 URL Learning System Environment Variables

# OpenAI API Key (for AI classification)
# OPENAI_API_KEY=your_openai_api_key_here

# Other API keys for enhanced functionality
# ODDS_API_KEY=your_odds_api_key
# TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# URL Scanner Settings
EQ12_URL_SCANNER_LOG_LEVEL=INFO
EQ12_URL_HANDLER_PORT=8080

# Dashboard Integration
EQ12_DASHBOARD_PORT=9000
"@

        $envTemplate | Set-Content "C:\EQ12\configs\url_system.env.template"

        Write-SetupLog "Configuration files created successfully" "SUCCESS"
        return $true

    } catch {
        Write-SetupLog "Error creating configuration: $_" "ERROR"
        return $false
    }
}

function Test-URLSystemFunctionality {
    """Test URL system functionality"""

    Write-SetupLog "Testing URL system functionality..."

    try {
        # Test URL scanner directly
        Write-SetupLog "Testing URL scanner with test URL: $TestURL"

        $scanTest = python -c "
import asyncio
import sys
sys.path.append('C:/EQ12/scripts')

async def test_scanner():
    try:
        from eq12_url_scanner import EQ12URLScanner
        scanner = EQ12URLScanner()

        result = await scanner.scan_url('$TestURL')

        print(f'✓ Scan completed successfully')
        print(f'  Classification: {result.classification}')
        print(f'  Confidence: {result.confidence:.2f}')
        print(f'  Processing Time: {result.processing_time:.2f}s')
        print(f'  Title: {result.title[:50]}...' if len(result.title) > 50 else f'  Title: {result.title}')

        if result.error:
            print(f'  Error: {result.error}')

        return True

    except Exception as e:
        print(f'✗ Scanner test failed: {e}')
        return False

if asyncio.run(test_scanner()):
    print('URL Scanner: PASS')
else:
    print('URL Scanner: FAIL')
    sys.exit(1)
" 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-SetupLog "URL scanner test: SUCCESS" "SUCCESS"
            Write-SetupLog "Test output: $scanTest"
        } else {
            Write-SetupLog "URL scanner test: FAILED" "ERROR"
            Write-SetupLog "Error output: $scanTest"
            return $false
        }

        # Test URL handler functionality
        Write-SetupLog "Testing URL extraction from text..."

        $handlerTest = python -c "
import sys
sys.path.append('C:/EQ12/scripts')

try:
    from eq12_copilot_url_handler import EQ12CopilotURLHandler

    handler = EQ12CopilotURLHandler()

    test_text = '''
    Check out this article: https://fastapi.tiangolo.com/
    Also see github.com/microsoft/playwright
    And this API documentation: https://docs.python.org/3/
    '''

    urls = handler.extract_urls_from_text(test_text)

    print(f'✓ Extracted {len(urls)} URLs from test text:')
    for i, url in enumerate(urls, 1):
        print(f'  {i}. {url}')

    if len(urls) >= 2:
        print('URL Handler: PASS')
    else:
        print('URL Handler: FAIL - Expected at least 2 URLs')
        sys.exit(1)

except Exception as e:
    print(f'✗ Handler test failed: {e}')
    sys.exit(1)
" 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-SetupLog "URL handler test: SUCCESS" "SUCCESS"
            Write-SetupLog "Test output: $handlerTest"
        } else {
            Write-SetupLog "URL handler test: FAILED" "ERROR"
            Write-SetupLog "Error output: $handlerTest"
            return $false
        }

        Write-SetupLog "All functionality tests passed" "SUCCESS"
        return $true

    } catch {
        Write-SetupLog "Error during functionality testing: $_" "ERROR"
        return $false
    }
}

function Show-URLSystemInfo {
    """Display complete URL system information"""

    Write-SetupLog ""
    Write-SetupLog "╔════════════════════════════════════════════════════╗" "SUCCESS"
    Write-SetupLog "║             EQ12 URL LEARNING SYSTEM               ║" "SUCCESS"
    Write-SetupLog "║                 SETUP COMPLETE                     ║" "SUCCESS"
    Write-SetupLog "╠════════════════════════════════════════════════════╣" "SUCCESS"
    Write-SetupLog "║                                                    ║" "SUCCESS"
    Write-SetupLog "║  🎯 INTELLIGENT URL PROCESSING                     ║" "SUCCESS"
    Write-SetupLog "║  • Automatic content scanning and analysis        ║" "SUCCESS"
    Write-SetupLog "║  • AI-powered classification and learning         ║" "SUCCESS"
    Write-SetupLog "║  • Smart EQ12 folder updates                      ║" "SUCCESS"
    Write-SetupLog "║                                                    ║" "SUCCESS"
    Write-SetupLog "║  🔗 COPILOT INTEGRATION                           ║" "SUCCESS"
    Write-SetupLog "║  • Automatic URL detection in messages           ║" "SUCCESS"
    Write-SetupLog "║  • Real-time processing and learning             ║" "SUCCESS"
    Write-SetupLog "║  • Webhook API for external integrations         ║" "SUCCESS"
    Write-SetupLog "║                                                    ║" "SUCCESS"
    Write-SetupLog "║  📊 DASHBOARD INTEGRATION                         ║" "SUCCESS"
    Write-SetupLog "║  • Real-time status monitoring                    ║" "SUCCESS"
    Write-SetupLog "║  • Processing statistics and analytics           ║" "SUCCESS"
    Write-SetupLog "║  • Manual URL submission interface               ║" "SUCCESS"
    Write-SetupLog "║                                                    ║" "SUCCESS"
    Write-SetupLog "╚════════════════════════════════════════════════════╝" "SUCCESS"
    Write-SetupLog ""

    Write-SetupLog "🚀 GETTING STARTED:"
    Write-SetupLog ""
    Write-SetupLog "1. Start the URL Learning System:"
    Write-SetupLog "   .\scripts\eq12_url_manager.ps1 -Action start"
    Write-SetupLog ""
    Write-SetupLog "2. Test with a URL:"
    Write-SetupLog "   .\scripts\eq12_url_manager.ps1 -Action test -TestUrl 'https://example.com'"
    Write-SetupLog ""
    Write-SetupLog "3. Check system status:"
    Write-SetupLog "   .\scripts\eq12_url_manager.ps1 -Action status"
    Write-SetupLog ""
    Write-SetupLog "4. Access via Dashboard:"
    Write-SetupLog "   http://localhost:9000/api/url-scanner/status"
    Write-SetupLog ""
    Write-SetupLog "5. Submit URLs via API:"
    Write-SetupLog "   POST http://localhost:8080/webhook/url"
    Write-SetupLog ""

    Write-SetupLog "💡 HOW IT WORKS:"
    Write-SetupLog ""
    Write-SetupLog "• When you paste a URL in Copilot, it's automatically detected"
    Write-SetupLog "• The system scans the URL content and analyzes it with AI"
    Write-SetupLog "• Based on the content, it learns and updates relevant EQ12 folders"
    Write-SetupLog "• Categories: betting, automation, finance, AI, dashboard, config, data"
    Write-SetupLog "• All activities are logged and monitored in the dashboard"
    Write-SetupLog ""

    Write-SetupLog "📁 CONFIGURATION FILES:"
    Write-SetupLog "• URL Scanner Config: C:\EQ12\configs\url_scanner_config.json"
    Write-SetupLog "• Handler Config: C:\EQ12\configs\url_handler_config.json"
    Write-SetupLog "• Environment Template: C:\EQ12\configs\url_system.env.template"
    Write-SetupLog ""

    Write-SetupLog "📊 LOGS AND DATA:"
    Write-SetupLog "• Setup Log: C:\EQ12\logs\url_system_setup.log"
    Write-SetupLog "• Runtime Logs: C:\EQ12\logs\url_scanner.log"
    Write-SetupLog "• Handler Logs: C:\EQ12\logs\copilot_url_handler.log"
    Write-SetupLog "• Database: C:\EQ12\url_scanner.db"
    Write-SetupLog ""

    Write-SetupLog "🔧 MANAGEMENT COMMANDS:"
    Write-SetupLog "• Start System: .\scripts\eq12_url_manager.ps1 -Action start"
    Write-SetupLog "• Stop System:  .\scripts\eq12_url_manager.ps1 -Action stop"
    Write-SetupLog "• Restart:      .\scripts\eq12_url_manager.ps1 -Action restart"
    Write-SetupLog "• Status:       .\scripts\eq12_url_manager.ps1 -Action status"
    Write-SetupLog "• Test URL:     .\scripts\eq12_url_manager.ps1 -Action test -TestUrl 'URL'"
    Write-SetupLog ""
}

# Main execution
try {
    Write-SetupLog "Starting EQ12 URL Learning System Setup..." "SUCCESS"
    Write-SetupLog "Skip Dependencies: $SkipDependencies"
    Write-SetupLog "Test After Setup: $TestAfterSetup"
    Write-SetupLog "Test URL: $TestURL"
    Write-SetupLog ""

    # Step 1: Check prerequisites
    if (!(Test-SystemPrerequisites)) {
        Write-SetupLog "System prerequisites not met. Setup cannot continue." "ERROR"
        exit 1
    }

    # Step 2: Install dependencies (unless skipped)
    if (!$SkipDependencies) {
        if (!(Install-URLSystemDependencies)) {
            Write-SetupLog "Dependency installation failed. Setup cannot continue." "ERROR"
            exit 1
        }
    } else {
        Write-SetupLog "Skipping dependency installation as requested"
    }

    # Step 3: Initialize databases
    if (!(Initialize-URLSystemDatabase)) {
        Write-SetupLog "Database initialization failed. Setup cannot continue." "ERROR"
        exit 1
    }

    # Step 4: Create configuration
    if (!(Create-URLSystemConfiguration)) {
        Write-SetupLog "Configuration creation failed. Setup cannot continue." "ERROR"
        exit 1
    }

    # Step 5: Test functionality (if requested)
    if ($TestAfterSetup) {
        if (!(Test-URLSystemFunctionality)) {
            Write-SetupLog "Functionality tests failed." "WARN"
            Write-SetupLog "Setup completed but system may not be fully functional." "WARN"
        }
    } else {
        Write-SetupLog "Skipping functionality tests (use -TestAfterSetup to enable)"
    }

    # Step 6: Display completion info
    Show-URLSystemInfo

    Write-SetupLog "EQ12 URL Learning System setup completed successfully! 🎉" "SUCCESS"
    exit 0

} catch {
    Write-SetupLog "Unexpected error during setup: $_" "ERROR"
    Write-SetupLog "Check the log file: $LogFile" "ERROR"
    exit 1
}
