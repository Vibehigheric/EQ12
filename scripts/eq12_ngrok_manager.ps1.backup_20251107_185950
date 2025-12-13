# EQ12 Ngrok Manager
# Comprehensive PowerShell script for managing ngrok tunnels in EQ12 GODSTACK

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "test", "deploy", "cleanup")]
    [string]$Action,

    [string]$Service = "all",
    [string]$Environment = "development",
    [switch]$Sensitive,
    [switch]$Monitoring,
    [switch]$Force
)

# Configuration
$EQ12_ROOT = "C:\EQ12"
$NGROK_CONFIG = "$EQ12_ROOT\configs\ngrok.yml"
$NGROK_LOGS = "$EQ12_ROOT\logs\ngrok.log"
$NGROK_API = "http://localhost:4040/api"

# Business stack definitions
$BUSINESS_STACKS = @{
    "betting"    = @("betting-api", "betting-dashboard")
    "cannabis"   = @("cannabis-compliance", "cannabis-inventory")
    "credit"     = @("credit-gateway", "credit-fraud")
    "analytics"  = @("scraper-api", "analytics-dashboard")
    "ai"         = @("ai-inference")
    "ecommerce"  = @("ecommerce-api")
    "mobile"     = @("mobile-api")
    "governance" = @("compliance-api", "governance-dashboard")
    "core"       = @("dashboard", "api", "webhook")
    "monitoring" = @("prometheus", "grafana")
}

$SENSITIVE_SERVICES = @("betting-api", "betting-dashboard", "cannabis-compliance", "cannabis-inventory", "credit-gateway", "credit-fraud", "compliance-api", "governance-dashboard")

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"

    switch ($Level) {
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "WARN" { Write-Host $logMessage -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $logMessage -ForegroundColor Green }
        "INFO" { Write-Host $logMessage -ForegroundColor Cyan }
        default { Write-Host $logMessage }
    }

    # Log to file
    Add-Content -Path "$EQ12_ROOT\logs\ngrok_manager.log" -Value $logMessage
}

function Test-Prerequisites {
    Write-EQ12Log "🔍 Checking EQ12 Ngrok prerequisites..."

    # Check if ngrok is installed
    try {
        $ngrokVersion = & ngrok version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "✅ Ngrok installed: $($ngrokVersion.Split("`n")[0])" "SUCCESS"
        } else {
            throw "Ngrok not found"
        }
    } catch {
        Write-EQ12Log "❌ Ngrok is not installed or not in PATH" "ERROR"
        Write-EQ12Log "💡 Install with: choco install ngrok" "INFO"
        return $false
    }

    # Check config file
    if (-not (Test-Path $NGROK_CONFIG)) {
        Write-EQ12Log "❌ Ngrok config file not found: $NGROK_CONFIG" "ERROR"
        return $false
    }

    # Check auth token
    if (-not $env:NGROK_AUTHTOKEN) {
        Write-EQ12Log "⚠️ NGROK_AUTHTOKEN environment variable not set" "WARN"
        Write-EQ12Log "💡 Set with: ngrok config add-authtoken YOUR_TOKEN" "INFO"
    }

    # Check if services are running
    $runningServices = Get-EQ12Services
    if ($runningServices.Count -eq 0) {
        Write-EQ12Log "⚠️ No EQ12 services detected running" "WARN"
        Write-EQ12Log "💡 Start your services before creating tunnels" "INFO"
    } else {
        Write-EQ12Log "✅ Detected $($runningServices.Count) running EQ12 services" "SUCCESS"
    }

    return $true
}

function Get-EQ12Services {
    $services = @()

    # Check common ports for EQ12 services
    $ports = @(5000, 8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8011, 8012, 8013, 8014, 8018, 9090, 3000)

    foreach ($port in $ports) {
        try {
            $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
            if ($connection.TcpTestSucceeded) {
                $services += $port
            }
        } catch {
            # Port not available
        }
    }

    return $services
}

function Start-NgrokTunnels {
    param([string]$ServiceFilter, [bool]$SensitiveOnly = $false, [bool]$MonitoringOnly = $false)

    Write-EQ12Log "🚀 Starting EQ12 Ngrok tunnels..." "INFO"

    if (-not (Test-Prerequisites)) {
        return
    }

    # Determine which services to start
    $servicesToStart = @()

    if ($ServiceFilter -eq "all") {
        if ($SensitiveOnly) {
            $servicesToStart = $SENSITIVE_SERVICES
        } elseif ($MonitoringOnly) {
            $servicesToStart = $BUSINESS_STACKS["monitoring"]
        } else {
            # Start all core services by default
            $servicesToStart = $BUSINESS_STACKS["core"] + $BUSINESS_STACKS["monitoring"]
        }
    } elseif ($BUSINESS_STACKS.ContainsKey($ServiceFilter)) {
        $servicesToStart = $BUSINESS_STACKS[$ServiceFilter]
    } else {
        $servicesToStart = @($ServiceFilter)
    }

    # Security check for sensitive services
    if ($servicesToStart | Where-Object { $_ -in $SENSITIVE_SERVICES }) {
        if (-not $Sensitive) {
            Write-EQ12Log "⚠️ Attempting to start sensitive services without -Sensitive flag" "WARN"
            Write-EQ12Log "🔒 Sensitive services require explicit authorization" "INFO"

            $confirmation = Read-Host "Start sensitive services? (y/N)"
            if ($confirmation -ne "y" -and $confirmation -ne "Y") {
                Write-EQ12Log "❌ Sensitive service startup cancelled" "INFO"
                return
            }
        }

        Write-EQ12Log "🔒 Starting sensitive business stack services with enhanced security" "WARN"
    }

    # Start ngrok with specified services
    try {
        if ($servicesToStart.Count -eq 1) {
            $ngrokArgs = @("start", $servicesToStart[0], "--config=$NGROK_CONFIG")
        } else {
            $serviceList = $servicesToStart -join ","
            if ($servicesToStart.Count -gt 5) {
                # Start all if more than 5 services
                $ngrokArgs = @("start", "--all", "--config=$NGROK_CONFIG")
            } else {
                $ngrokArgs = @("start") + $servicesToStart + @("--config=$NGROK_CONFIG")
            }
        }

        Write-EQ12Log "📡 Executing: ngrok $($ngrokArgs -join ' ')" "INFO"

        # Start ngrok in background
        $process = Start-Process -FilePath "ngrok" -ArgumentList $ngrokArgs -NoNewWindow -PassThru

        # Wait for initialization
        Write-EQ12Log "⏳ Waiting for tunnels to initialize..." "INFO"
        Start-Sleep -Seconds 15

        # Verify tunnels are active
        Get-NgrokStatus

    } catch {
        Write-EQ12Log "❌ Failed to start ngrok tunnels: $($_.Exception.Message)" "ERROR"
    }
}

function Stop-NgrokTunnels {
    Write-EQ12Log "🛑 Stopping EQ12 Ngrok tunnels..." "INFO"

    try {
        $ngrokProcesses = Get-Process -Name "ngrok" -ErrorAction SilentlyContinue

        if ($ngrokProcesses) {
            foreach ($process in $ngrokProcesses) {
                Write-EQ12Log "🔪 Terminating ngrok process (PID: $($process.Id))" "INFO"
                Stop-Process -Id $process.Id -Force
            }
            Write-EQ12Log "✅ All ngrok processes terminated" "SUCCESS"
        } else {
            Write-EQ12Log "ℹ️ No ngrok processes found running" "INFO"
        }

        # Clean up any lingering connections
        Start-Sleep -Seconds 2

    } catch {
        Write-EQ12Log "❌ Error stopping ngrok: $($_.Exception.Message)" "ERROR"
    }
}

function Get-NgrokStatus {
    Write-EQ12Log "📊 EQ12 Ngrok Tunnel Status:" "INFO"

    try {
        $response = Invoke-RestMethod -Uri "$NGROK_API/tunnels" -Method Get -TimeoutSec 10

        if ($response.tunnels.Count -eq 0) {
            Write-EQ12Log "ℹ️ No active tunnels found" "INFO"
            return
        }

        Write-Host ""
        Write-Host "┌─────────────────────┬──────────────────────────────────────────────┬─────────────┐" -ForegroundColor Gray
        Write-Host "│ Service             │ Public URL                                   │ Status      │" -ForegroundColor Gray
        Write-Host "├─────────────────────┼──────────────────────────────────────────────┼─────────────┤" -ForegroundColor Gray

        foreach ($tunnel in $response.tunnels) {
            $serviceName = $tunnel.name.PadRight(19)
            $publicUrl = $tunnel.public_url.PadRight(44)
            $status = if ($tunnel.public_url) { "🟢 Active" } else { "🔴 Error" }
            $status = $status.PadRight(11)

            $color = if ($tunnel.name -in $SENSITIVE_SERVICES) { "Yellow" } else { "Green" }
            Write-Host "│ $serviceName │ $publicUrl │ $status │" -ForegroundColor $color

            # Log metrics if available
            if ($tunnel.metrics) {
                $requests = $tunnel.metrics.http.count
                $bytes = [math]::Round($tunnel.metrics.http.bytes / 1024, 2)
                Write-EQ12Log "   📈 $($tunnel.name): $requests requests, $bytes KB transferred" "INFO"
            }
        }

        Write-Host "└─────────────────────┴──────────────────────────────────────────────┴─────────────┘" -ForegroundColor Gray
        Write-Host ""

        # Security status for sensitive services
        $sensitiveActive = $response.tunnels | Where-Object { $_.name -in $SENSITIVE_SERVICES }
        if ($sensitiveActive) {
            Write-EQ12Log "🔒 $($sensitiveActive.Count) sensitive business stack tunnels active" "WARN"
            Write-EQ12Log "⚡ Ensure compliance monitoring is enabled" "INFO"
        }

        # Web interface info
        Write-EQ12Log "🌐 Ngrok Web Interface available at: http://localhost:4040" "INFO"

    } catch {
        Write-EQ12Log "❌ Unable to retrieve tunnel status: $($_.Exception.Message)" "ERROR"
        Write-EQ12Log "💡 Ngrok may not be running or web interface unavailable" "INFO"
    }
}

function Get-NgrokLogs {
    param([int]$Lines = 50)

    Write-EQ12Log "📋 EQ12 Ngrok Logs (last $Lines lines):" "INFO"

    if (Test-Path $NGROK_LOGS) {
        try {
            $logs = Get-Content $NGROK_LOGS -Tail $Lines
            foreach ($log in $logs) {
                if ($log -match "ERROR|error") {
                    Write-Host $log -ForegroundColor Red
                } elseif ($log -match "WARN|warn") {
                    Write-Host $log -ForegroundColor Yellow
                } else {
                    Write-Host $log -ForegroundColor White
                }
            }
        } catch {
            Write-EQ12Log "❌ Error reading log file: $($_.Exception.Message)" "ERROR"
        }
    } else {
        Write-EQ12Log "❌ Ngrok log file not found: $NGROK_LOGS" "ERROR"
        Write-EQ12Log "💡 Logs may be configured to write elsewhere or ngrok hasn't been started" "INFO"
    }
}

function Test-NgrokTunnels {
    Write-EQ12Log "🧪 Testing EQ12 Ngrok tunnel connectivity..." "INFO"

    try {
        $response = Invoke-RestMethod -Uri "$NGROK_API/tunnels" -Method Get

        foreach ($tunnel in $response.tunnels) {
            Write-EQ12Log "🔍 Testing tunnel: $($tunnel.name)" "INFO"

            try {
                $testResponse = Invoke-WebRequest -Uri $tunnel.public_url -Method GET -TimeoutSec 10 -UseBasicParsing
                $statusCode = $testResponse.StatusCode

                if ($statusCode -eq 200) {
                    Write-EQ12Log "✅ $($tunnel.name): HTTP $statusCode - OK" "SUCCESS"
                } elseif ($statusCode -eq 401) {
                    Write-EQ12Log "🔐 $($tunnel.name): HTTP $statusCode - Authentication required (expected)" "INFO"
                } else {
                    Write-EQ12Log "⚠️ $($tunnel.name): HTTP $statusCode - Unexpected response" "WARN"
                }

            } catch {
                Write-EQ12Log "❌ $($tunnel.name): Connection failed - $($_.Exception.Message)" "ERROR"
            }
        }

    } catch {
        Write-EQ12Log "❌ Unable to test tunnels: $($_.Exception.Message)" "ERROR"
    }
}

function Deploy-PreviewEnvironment {
    Write-EQ12Log "🚀 Deploying EQ12 preview environment with ngrok..." "INFO"

    # Start core services for preview
    $previewServices = @("dashboard", "api", "webhook")

    Write-EQ12Log "📦 Starting preview services: $($previewServices -join ', ')" "INFO"

    try {
        # Start services
        Start-NgrokTunnels -ServiceFilter "core"

        Start-Sleep -Seconds 10

        # Get URLs for preview
        $response = Invoke-RestMethod -Uri "$NGROK_API/tunnels" -Method Get
        $previewUrls = @{}

        foreach ($tunnel in $response.tunnels | Where-Object { $_.name -in $previewServices }) {
            $previewUrls[$tunnel.name] = $tunnel.public_url
        }

        # Generate preview summary
        Write-Host ""
        Write-EQ12Log "🎯 EQ12 Preview Environment Ready!" "SUCCESS"
        Write-Host "┌─────────────────────┬──────────────────────────────────────────────┐" -ForegroundColor Green
        Write-Host "│ Service             │ Preview URL                                  │" -ForegroundColor Green
        Write-Host "├─────────────────────┼──────────────────────────────────────────────┤" -ForegroundColor Green

        foreach ($service in $previewServices) {
            if ($previewUrls.ContainsKey($service)) {
                $serviceName = $service.PadRight(19)
                $url = $previewUrls[$service].PadRight(44)
                Write-Host "│ $serviceName │ $url │" -ForegroundColor Cyan
            }
        }

        Write-Host "└─────────────────────┴──────────────────────────────────────────────┘" -ForegroundColor Green
        Write-Host ""

        Write-EQ12Log "🔑 Default credentials: dev / eq12dev123" "INFO"
        Write-EQ12Log "⏰ Preview environment will remain active until manually stopped" "INFO"

    } catch {
        Write-EQ12Log "❌ Preview deployment failed: $($_.Exception.Message)" "ERROR"
    }
}

function Cleanup-NgrokResources {
    Write-EQ12Log "🧹 Cleaning up EQ12 ngrok resources..." "INFO"

    # Stop all tunnels
    Stop-NgrokTunnels

    # Clean up log files
    if (Test-Path "$EQ12_ROOT\logs\ngrok.log") {
        try {
            # Archive old logs
            $archiveDate = Get-Date -Format "yyyyMMdd_HHmmss"
            Move-Item "$EQ12_ROOT\logs\ngrok.log" "$EQ12_ROOT\logs\ngrok_$archiveDate.log"
            Write-EQ12Log "📁 Archived old ngrok logs" "SUCCESS"
        } catch {
            Write-EQ12Log "⚠️ Could not archive logs: $($_.Exception.Message)" "WARN"
        }
    }

    # Clean up temporary files
    $tempFiles = Get-ChildItem "$env:TEMP" -Filter "ngrok*" -ErrorAction SilentlyContinue
    if ($tempFiles) {
        $tempFiles | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-EQ12Log "🗑️ Cleaned up temporary ngrok files" "SUCCESS"
    }

    Write-EQ12Log "✅ Cleanup completed" "SUCCESS"
}

# Main execution logic
Write-EQ12Log "🎯 EQ12 Ngrok Manager - Action: $Action" "INFO"

switch ($Action.ToLower()) {
    "start" {
        Start-NgrokTunnels -ServiceFilter $Service -SensitiveOnly:$Sensitive -MonitoringOnly:$Monitoring
    }
    "stop" {
        Stop-NgrokTunnels
    }
    "restart" {
        Stop-NgrokTunnels
        Start-Sleep -Seconds 5
        Start-NgrokTunnels -ServiceFilter $Service -SensitiveOnly:$Sensitive -MonitoringOnly:$Monitoring
    }
    "status" {
        Get-NgrokStatus
    }
    "logs" {
        Get-NgrokLogs
    }
    "test" {
        Test-NgrokTunnels
    }
    "deploy" {
        Deploy-PreviewEnvironment
    }
    "cleanup" {
        Cleanup-NgrokResources
    }
    default {
        Write-EQ12Log "❌ Unknown action: $Action" "ERROR"
    }
}

Write-EQ12Log "🏁 EQ12 Ngrok Manager completed" "INFO"
