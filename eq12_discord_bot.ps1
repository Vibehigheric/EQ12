# EQ12 Discord Bot
# PowerShell wrapper for Discord integration bot
# Manages dual server architecture (Ops + Community)

[CmdletBinding()]
param(
    [switch]$Start,
    [switch]$Stop,
    [switch]$Status,
    [switch]$Setup,
    [switch]$Config,
    [string]$Command,
    [string]$Server = "ops"
)

$ErrorActionPreference = "Stop"

# EQ12 Configuration
$EQ12_HOME = $env:EQ12_HOME
if (-not $EQ12_HOME) {
    $EQ12_HOME = "C:\EQ12"
}

$DISCORD_BOT_PY = Join-Path $EQ12_HOME "eq12_discord_bot.py"
$DISCORD_CONFIG = Join-Path $EQ12_HOME "configs\discord_config.json"
$LOGS_DIR = Join-Path $EQ12_HOME "logs\discord_bot"
$PID_FILE = Join-Path $LOGS_DIR "discord_bot.pid"

# Ensure directories exist
if (-not (Test-Path (Split-Path $DISCORD_CONFIG))) {
    New-Item -ItemType Directory -Path (Split-Path $DISCORD_CONFIG) -Force | Out-Null
}
if (-not (Test-Path $LOGS_DIR)) {
    New-Item -ItemType Directory -Path $LOGS_DIR -Force | Out-Null
}

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp | $Level | DiscordBot | $Message"
    Write-Host $logMessage
    Add-Content -Path (Join-Path $LOGS_DIR "discord_bot_ps.log") -Value $logMessage -Encoding UTF8
}

function Test-DiscordDependencies {
    Write-EQ12Log "Checking Discord bot dependencies..."

    $dependencies = @(
        "discord.py",
        "aiohttp"
    )

    $missing = @()
    foreach ($dep in $dependencies) {
        try {
            $importName = $dep.Replace('.py', '').Replace('-', '_')
            python -c "import $importName" 2>$null
            if ($LASTEXITCODE -ne 0) {
                $missing += $dep
            }
        } catch {
            $missing += $dep
        }
    }

    if ($missing.Count -gt 0) {
        Write-EQ12Log "Missing dependencies: $($missing -join ', ')" "ERROR"
        Write-EQ12Log "Install with: pip install $($missing -join ' ')" "INFO"
        return $false
    }

    Write-EQ12Log "All Discord dependencies available"
    return $true
}

function Test-BotToken {
    $token = $env:DISCORD_BOT_TOKEN
    if (-not $token) {
        Write-EQ12Log "DISCORD_BOT_TOKEN environment variable not set" "ERROR"
        Write-EQ12Log "Get bot token from: https://discord.com/developers/applications" "INFO"
        return $false
    }

    Write-EQ12Log "Discord bot token configured"
    return $true
}

function Initialize-DiscordConfig {
    Write-EQ12Log "Creating Discord configuration..."

    if (Test-Path $DISCORD_CONFIG) {
        Write-EQ12Log "Config file already exists: $DISCORD_CONFIG" "WARN"
        return
    }

    $defaultConfig = @{
        ops_server           = @{
            server_id = $null
            channels  = @{
                alerts  = $null
                betting = $null
                travel  = $null
                finance = $null
                appletv = $null
                snips   = $null
                logs    = $null
            }
            roles     = @{
                admin    = $null
                operator = $null
            }
        }
        community_server     = @{
            server_id = $null
            channels  = @{
                general   = $null
                betting   = $null
                travel    = $null
                premium   = $null
                affiliate = $null
            }
            roles     = @{
                premium   = $null
                vip       = $null
                elite     = $null
                affiliate = $null
            }
        }
        telegram_integration = @{
            enabled             = $true
            cross_post_channels = @("betting", "travel", "alerts")
        }
        apple_tv_integration = @{
            enabled         = $true
            stream_channels = @("appletv", "premium")
        }
    }

    $defaultConfig | ConvertTo-Json -Depth 4 | Out-File $DISCORD_CONFIG -Encoding UTF8
    Write-EQ12Log "Created default config at: $DISCORD_CONFIG"

    Write-Host ""
    Write-Host "=== Discord Bot Setup Instructions ==="
    Write-Host "1. Create Discord application: https://discord.com/developers/applications"
    Write-Host "2. Get bot token and set DISCORD_BOT_TOKEN environment variable"
    Write-Host "3. Invite bot to both servers (ops + community)"
    Write-Host "4. Edit config file with server/channel/role IDs"
    Write-Host "5. Run: .\eq12_discord_bot.ps1 -Start"
    Write-Host ""
    Write-Host "Config file: $DISCORD_CONFIG"
}

function Start-DiscordBot {
    Write-EQ12Log "Starting EQ12 Discord Bot..."

    # Check if already running
    if (Test-Path $PID_FILE) {
        $processId = Get-Content $PID_FILE
        if (Get-Process -Id $processId -ErrorAction SilentlyContinue) {
            Write-EQ12Log "Discord Bot already running (PID: $processId)" "WARN"
            return
        }
    }

    # Verify dependencies
    if (-not (Test-DiscordDependencies)) {
        throw "Missing Discord dependencies"
    }

    if (-not (Test-BotToken)) {
        throw "Discord bot token not configured"
    }

    if (-not (Test-Path $DISCORD_CONFIG)) {
        Write-EQ12Log "Config file not found - run with -Setup first" "ERROR"
        throw "Discord config not found"
    }

    # Start Python process
    $processArgs = @{
        FilePath         = "python"
        ArgumentList     = $DISCORD_BOT_PY
        WorkingDirectory = $EQ12_HOME
        WindowStyle      = "Hidden"
        PassThru         = $true
    }

    $process = Start-Process @processArgs

    # Save PID
    $process.Id | Out-File $PID_FILE -Encoding ASCII

    Write-EQ12Log "Discord Bot started (PID: $($process.Id))"
    Write-EQ12Log "Multi-server architecture: Ops + Community"
    Write-EQ12Log "Integrations: Telegram, Apple TV, Snip Watcher"
    Write-EQ12Log "Logs: $LOGS_DIR"
}

function Stop-DiscordBot {
    Write-EQ12Log "Stopping EQ12 Discord Bot..."

    if (-not (Test-Path $PID_FILE)) {
        Write-EQ12Log "PID file not found - may not be running" "WARN"
        return
    }

    $processId = Get-Content $PID_FILE
    $process = Get-Process -Id $processId -ErrorAction SilentlyContinue

    if ($process) {
        Stop-Process -Id $processId -Force
        Write-EQ12Log "Stopped process $processId"
    } else {
        Write-EQ12Log "Process $processId not running" "WARN"
    }

    Remove-Item $PID_FILE -ErrorAction SilentlyContinue
}

function Get-DiscordBotStatus {
    Write-EQ12Log "Checking Discord Bot status..."

    $isRunning = $false
    $processId = $null

    if (Test-Path $PID_FILE) {
        $processId = Get-Content $PID_FILE
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        $isRunning = $null -ne $process
    }

    Write-Host "=== EQ12 Discord Bot Status ==="
    Write-Host "Running: $isRunning"

    if ($isRunning) {
        Write-Host "PID: $processId"
        Write-Host "CPU: $([math]::Round($process.CPU, 2))s"
        Write-Host "Memory: $([math]::Round($process.WorkingSet / 1MB, 2))MB"
    }

    Write-Host "Config: $DISCORD_CONFIG"
    Write-Host "Logs: $LOGS_DIR"

    # Check configuration
    if (Test-Path $DISCORD_CONFIG) {
        $config = Get-Content $DISCORD_CONFIG | ConvertFrom-Json
        $opsConfigured = $null -ne $config.ops_server.server_id
        $communityConfigured = $null -ne $config.community_server.server_id

        Write-Host "Configuration:"
        Write-Host "  Ops Server: $opsConfigured"
        Write-Host "  Community Server: $communityConfigured"
        Write-Host "  Telegram Integration: $($config.telegram_integration.enabled)"
        Write-Host "  Apple TV Integration: $($config.apple_tv_integration.enabled)"
    } else {
        Write-Host "Configuration: Not found (run -Setup)"
    }

    # Dependencies
    Write-Host "Dependencies:"
    Write-Host "  Discord.py: $(Test-DiscordDependencies)"
    Write-Host "  Bot Token: $(Test-BotToken)"
}

function Show-DiscordConfig {
    if (-not (Test-Path $DISCORD_CONFIG)) {
        Write-Host "Config file not found: $DISCORD_CONFIG"
        Write-Host "Run with -Setup to create default config"
        return
    }

    Write-Host "=== Discord Bot Configuration ==="
    Write-Host "File: $DISCORD_CONFIG"
    Write-Host ""

    $config = Get-Content $DISCORD_CONFIG | ConvertFrom-Json

    Write-Host "Ops Server (Mission Control):"
    Write-Host "  Server ID: $($config.ops_server.server_id)"
    Write-Host "  Channels: $($config.ops_server.channels | ConvertTo-Json -Compress)"
    Write-Host "  Roles: $($config.ops_server.roles | ConvertTo-Json -Compress)"
    Write-Host ""

    Write-Host "Community Server (Public/Affiliate):"
    Write-Host "  Server ID: $($config.community_server.server_id)"
    Write-Host "  Channels: $($config.community_server.channels | ConvertTo-Json -Compress)"
    Write-Host "  Roles: $($config.community_server.roles | ConvertTo-Json -Compress)"
    Write-Host ""

    Write-Host "Integrations:"
    Write-Host "  Telegram: $($config.telegram_integration.enabled)"
    Write-Host "  Apple TV: $($config.apple_tv_integration.enabled)"
    Write-Host ""

    Write-Host "Edit this file to configure server/channel/role IDs"
}

function Send-DiscordCommand {
    param([string]$Command, [string]$Server)

    Write-EQ12Log "Sending Discord command: $Command (Server: $Server)"

    # This would integrate with the Discord bot API
    # For now, just log the command
    Write-Host "Command sent to Discord bot: $Command"
    Write-Host "Target server: $Server"

    # In a full implementation, this would make an HTTP request
    # to the Discord bot's command API endpoint
}

# Main script logic
try {
    if ($Start) {
        Start-DiscordBot
    } elseif ($Stop) {
        Stop-DiscordBot
    } elseif ($Status) {
        Get-DiscordBotStatus
    } elseif ($Setup) {
        Initialize-DiscordConfig
    } elseif ($Config) {
        Show-DiscordConfig
    } elseif ($Command) {
        Send-DiscordCommand -Command $Command -Server $Server
    } else {
        Write-Host "EQ12 Discord Bot - Multi-Server Integration"
        Write-Host ""
        Write-Host "Usage:"
        Write-Host "  .\eq12_discord_bot.ps1 -Setup      # Create initial configuration"
        Write-Host "  .\eq12_discord_bot.ps1 -Start      # Start the Discord bot"
        Write-Host "  .\eq12_discord_bot.ps1 -Stop       # Stop the Discord bot"
        Write-Host "  .\eq12_discord_bot.ps1 -Status     # Check bot status"
        Write-Host "  .\eq12_discord_bot.ps1 -Config     # Show configuration"
        Write-Host "  .\eq12_discord_bot.ps1 -Command 'parlay 5 nfl' -Server ops"
        Write-Host ""
        Write-Host "Architecture:"
        Write-Host "  Ops Server     - Private mission control (admin/team coordination)"
        Write-Host "  Community Server - Public affiliate funnel (premium content)"
        Write-Host ""
        Write-Host "Commands (via Discord):"
        Write-Host "  !eq12 status   - Bot status and stats"
        Write-Host "  !eq12 parlay   - Generate betting parlay"
        Write-Host "  !eq12 deal     - Find travel deals"
        Write-Host "  !eq12 sendtv   - Stream to Apple TV"
        Write-Host "  !eq12 snip     - Snip watcher status"
        Write-Host ""
        Write-Host "Integrations: Telegram cross-posting, Apple TV streaming, Snip Watcher"
        Write-Host "Dependencies: discord.py, aiohttp"
    }
} catch {
    Write-EQ12Log "Error: $($_.Exception.Message)" "ERROR"
    throw
}
