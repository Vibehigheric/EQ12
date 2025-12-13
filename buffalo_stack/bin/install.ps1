#Requires -RunAsAdministrator
# Buffalo Stack + EQ12 Integration Installer
# Installs civil service tracker, task schedulers, and EQ12 godmode runner

[CmdletBinding()]
param(
    [switch]$SkipTasks,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "=== Installing Buffalo Stack (EQ12 Integration 14215) ===" -ForegroundColor Green

$base = "C:\EQ12\buffalo_stack"
$logsDir = "$base\logs"
$configDir = "$base\config"
$civilDir = "$base\civil"
$binDir = "$base\bin"

# Create directory structure
@($base, $logsDir, $configDir, $civilDir, $binDir) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
        Write-Host "✅ Created directory: $_" -ForegroundColor Green
    }
}

# Copy configuration templates if missing
if (-not (Test-Path "$configDir\config.yaml") -or $Force) {
    if (Test-Path "$base\config.example.yaml") {
        Copy-Item "$base\config.example.yaml" "$configDir\config.yaml"
        Write-Host "✅ Copied config template" -ForegroundColor Green
    }
}

if (-not (Test-Path "$base\.env") -or $Force) {
    if (Test-Path "$base\.env.example") {
        Copy-Item "$base\.env.example" "$base\.env"
        Write-Host "✅ Copied environment template" -ForegroundColor Green
    } else {
        # Create basic .env template
        @"
# Buffalo Stack Environment Variables
# Added by installer $(Get-Date)

# OpenAI API for ChatGPT integration
OPENAI_API_KEY=your_openai_api_key_here

# Odds API for betting automation
ODDS_API_KEY=your_odds_api_key_here

# Telegram notifications
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Civil Service Settings
CIVIL_SERVICE_CHECK_INTERVAL=3600
CIVIL_SERVICE_KEYWORDS=police,firefighter,emt,dispatcher
"@ | Out-File "$base\.env" -Encoding UTF8
        Write-Host "✅ Created .env template" -ForegroundColor Green
    }
}

# Install Python requirements
Write-Host "📦 Installing Python requirements..." -ForegroundColor Yellow
try {
    if (Test-Path "$base\requirements.txt") {
        & python -m pip install -r "$base\requirements.txt" --upgrade
        Write-Host "✅ Python requirements installed" -ForegroundColor Green
    } else {
        Write-Warning "requirements.txt not found, skipping pip install"
    }
} catch {
    Write-Error "Failed to install Python requirements: $_"
}

# Initialize database (run civil tracker once to create tables)
Write-Host "🗄️ Initializing civil service database..." -ForegroundColor Yellow
try {
    if (Test-Path "$civilDir\civil_service_tracker.py") {
        & python "$civilDir\civil_service_tracker.py" --init-only
        Write-Host "✅ Database initialized" -ForegroundColor Green
    }
} catch {
    Write-Warning "Could not initialize database: $_"
}

# Register scheduled tasks
if (-not $SkipTasks) {
    Write-Host "⏰ Registering scheduled tasks..." -ForegroundColor Yellow
    
    $tasks = @(
        @{Name="BuffaloStack\CivilServiceTracker"; XML="$base\tasks\schedule_civil_tracker.xml"},
        @{Name="BuffaloStack\EQ12ComboRunner"; XML="$base\tasks\schedule_eq12_combo.xml"}
    )
    
    foreach ($task in $tasks) {
        try {
            if (Test-Path $task.XML) {
                & schtasks /Create /TN $task.Name /XML $task.XML /F
                Write-Host "✅ Registered task: $($task.Name)" -ForegroundColor Green
            } else {
                Write-Warning "Task XML not found: $($task.XML)"
            }
        } catch {
            Write-Warning "Failed to register task $($task.Name): $_"
        }
    }
}

# Create desktop shortcuts
$WshShell = New-Object -comObject WScript.Shell
$shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\EQ12 Buffalo Stack.lnk")
$shortcut.TargetPath = "python"
$shortcut.Arguments = '"C:\EQ12\buffalo_stack\eq12_godmode_runner_plus.py"'
$shortcut.WorkingDirectory = "C:\EQ12\buffalo_stack"
$shortcut.IconLocation = "C:\Windows\System32\shell32.dll,21"
$shortcut.Description = "EQ12 Buffalo Stack Automation Runner"
$shortcut.Save()
Write-Host "✅ Created desktop shortcut" -ForegroundColor Green

# Set up logging permissions
try {
    $acl = Get-Acl $logsDir
    $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "FullControl", "Allow")
    $acl.SetAccessRule($accessRule)
    Set-Acl $logsDir $acl
    Write-Host "✅ Set logging permissions" -ForegroundColor Green
} catch {
    Write-Warning "Could not set logging permissions: $_"
}

Write-Host "
=== Installation Complete ===" -ForegroundColor Green
Write-Host "📍 Base Directory: $base" -ForegroundColor Cyan
Write-Host "📝 Logs Directory: $logsDir" -ForegroundColor Cyan
Write-Host "⚙️  Config: $configDir\config.yaml" -ForegroundColor Cyan
Write-Host "🔐 Environment: $base\.env" -ForegroundColor Cyan
Write-Host "
🚀 To run: python \"$base\eq12_godmode_runner_plus.py\"" -ForegroundColor Yellow
Write-Host "📋 Or use desktop shortcut: EQ12 Buffalo Stack" -ForegroundColor Yellow

if (-not $SkipTasks) {
    Write-Host "⏰ Scheduled tasks registered - check Task Scheduler" -ForegroundColor Yellow
}

Write-Host "
⚠️  Remember to update API keys in .env file before first run!" -ForegroundColor Red