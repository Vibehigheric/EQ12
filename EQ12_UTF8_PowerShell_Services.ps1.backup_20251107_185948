# EQ12_UTF8_PowerShell_Services.ps1
<#
.SYNOPSIS
    EQ12 Comprehensive PowerShell UTF-8 Logging and Windows Services Setup

.DESCRIPTION
    Standardizes UTF-8 encoding across all PowerShell scripts, implements robust
    logging mechanisms, and configures EQ12 components as Windows services.

.PARAMETER Action
    The action to perform: install, uninstall, start, stop, restart, status, configure

.PARAMETER ServiceName
    Specific service to target (optional)

.PARAMETER LogLevel
    Logging level: Debug, Info, Warning, Error

.EXAMPLE
    .\EQ12_UTF8_PowerShell_Services.ps1 -Action install
    .\EQ12_UTF8_PowerShell_Services.ps1 -Action status
    .\EQ12_UTF8_PowerShell_Services.ps1 -Action start -ServiceName EQ12-Dashboard
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("install", "uninstall", "start", "stop", "restart", "status", "configure")]
    [string]$Action,

    [Parameter(Mandatory = $false)]
    [ValidateSet("EQ12-Dashboard", "EQ12-LLM-Engine", "EQ12-Odds-Ingestion", "EQ12-Analytics")]
    [string]$ServiceName,

    [Parameter(Mandatory = $false)]
    [ValidateSet("Debug", "Info", "Warning", "Error")]
    [string]$LogLevel = "Info"
)

# Force UTF-8 encoding for PowerShell session
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

# Set PowerShell to use UTF-8 by default
if ($PSVersionTable.PSVersion.Major -ge 6) {
    $PSDefaultParameterValues['*:Encoding'] = 'utf8'
}
else {
    $PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
    $PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
    $PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'
}

# Global configuration
$EQ12Config = @{
    RootPath    = "C:\EQ12"
    LogPath     = "C:\EQ12\logs"
    ConfigPath  = "C:\EQ12\configs"
    ServicePath = "C:\EQ12\services"
    BackupPath  = "C:\EQ12\backups"
    TempPath    = "C:\EQ12\temp"
}

# Service definitions with UTF-8 support
$EQ12Services = @{
    "EQ12-Dashboard"      = @{
        DisplayName          = "EQ12 Sports Betting Dashboard"
        Description          = "Real-time sports betting analytics dashboard with WebSocket support"
        ExecutablePath       = "node.exe"
        Arguments            = "C:\EQ12\eq12_enhanced_dashboard_server.js"
        WorkingDirectory     = "C:\EQ12"
        LogFile              = "dashboard_service.log"
        DependsOn            = @()
        StartupType          = "Automatic"
        EnvironmentVariables = @{
            "NODE_ENV"  = "production"
            "PORT"      = "3000"
            "REDIS_URL" = "redis://localhost:6379/0"
            "LOG_LEVEL" = "info"
        }
    }
    "EQ12-LLM-Engine"     = @{
        DisplayName          = "EQ12 LLM Automation Engine"
        Description          = "OpenAI GPT-5 powered betting analysis with circuit breakers"
        ExecutablePath       = "python.exe"
        Arguments            = "C:\EQ12\eq12_comprehensive_llm_automation.py"
        WorkingDirectory     = "C:\EQ12"
        LogFile              = "llm_engine_service.log"
        DependsOn            = @("EQ12-Dashboard")
        StartupType          = "Automatic"
        EnvironmentVariables = @{
            "PYTHONPATH"       = "C:\EQ12"
            "PYTHONUNBUFFERED" = "1"
            "PYTHONIOENCODING" = "utf-8"
        }
    }
    "EQ12-Odds-Ingestion" = @{
        DisplayName          = "EQ12 Odds Ingestion Pipeline"
        Description          = "Rate-limited odds ingestion from multiple sportsbooks"
        ExecutablePath       = "python.exe"
        Arguments            = "C:\EQ12\eq12_odds_ingestion_service.py"
        WorkingDirectory     = "C:\EQ12"
        LogFile              = "odds_ingestion_service.log"
        DependsOn            = @("EQ12-Dashboard")
        StartupType          = "Automatic"
        EnvironmentVariables = @{
            "PYTHONPATH"       = "C:\EQ12"
            "PYTHONUNBUFFERED" = "1"
            "PYTHONIOENCODING" = "utf-8"
        }
    }
    "EQ12-Analytics"      = @{
        DisplayName          = "EQ12 Analytics Processor"
        Description          = "Kelly Criterion and Expected Value calculations service"
        ExecutablePath       = "python.exe"
        Arguments            = "C:\EQ12\eq12_analytics_service.py"
        WorkingDirectory     = "C:\EQ12"
        LogFile              = "analytics_service.log"
        DependsOn            = @("EQ12-LLM-Engine", "EQ12-Odds-Ingestion")
        StartupType          = "Automatic"
        EnvironmentVariables = @{
            "PYTHONPATH"       = "C:\EQ12"
            "PYTHONUNBUFFERED" = "1"
            "PYTHONIOENCODING" = "utf-8"
        }
    }
}

# Enhanced logging class with UTF-8 support
class EQ12Logger {
    [string]$LogPath
    [string]$LogLevel
    [System.IO.StreamWriter]$FileWriter

    EQ12Logger([string]$logPath, [string]$logLevel) {
        $this.LogPath = $logPath
        $this.LogLevel = $logLevel

        # Ensure log directory exists
        $logDir = Split-Path $logPath -Parent
        if (-not (Test-Path $logDir)) {
            New-Item -ItemType Directory -Path $logDir -Force | Out-Null
        }

        # Initialize file writer with UTF-8 encoding
        $this.FileWriter = [System.IO.StreamWriter]::new($logPath, $true, [System.Text.Encoding]::UTF8)
        $this.FileWriter.AutoFlush = $true
    }

    [void] WriteLog([string]$level, [string]$message, [hashtable]$data = @{}) {
        $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"

        $logEntry = @{
            timestamp  = $timestamp
            level      = $level
            component  = "EQ12_PowerShell_Services"
            message    = $message
            data       = $data
            process_id = $PID
            thread_id  = [System.Threading.Thread]::CurrentThread.ManagedThreadId
        } | ConvertTo-Json -Compress -Depth 10

        # Console output with color
        $color = switch ($level) {
            "DEBUG" { "DarkGray" }
            "INFO" { "Green" }
            "WARNING" { "Yellow" }
            "ERROR" { "Red" }
            default { "White" }
        }

        Write-Host "[$level] $message" -ForegroundColor $color

        # File output
        $this.FileWriter.WriteLine($logEntry)
    }

    [void] Debug([string]$message, [hashtable]$data = @{}) {
        if ($this.LogLevel -in @("Debug")) {
            $this.WriteLog("DEBUG", $message, $data)
        }
    }

    [void] Info([string]$message, [hashtable]$data = @{}) {
        if ($this.LogLevel -in @("Debug", "Info")) {
            $this.WriteLog("INFO", $message, $data)
        }
    }

    [void] Warning([string]$message, [hashtable]$data = @{}) {
        if ($this.LogLevel -in @("Debug", "Info", "Warning")) {
            $this.WriteLog("WARNING", $message, $data)
        }
    }

    [void] Error([string]$message, [hashtable]$data = @{}) {
        $this.WriteLog("ERROR", $message, $data)
    }

    [void] Close() {
        if ($this.FileWriter) {
            $this.FileWriter.Close()
            $this.FileWriter.Dispose()
        }
    }
}

# Initialize logger
$logFile = Join-Path $EQ12Config.LogPath "powershell_services_$(Get-Date -Format 'yyyyMMdd').log"
$logger = [EQ12Logger]::new($logFile, $LogLevel)

function Initialize-EQ12Directories {
    <#
    .SYNOPSIS
        Initialize required directories with proper permissions
    #>

    $logger.Info("Initializing EQ12 directory structure")

    foreach ($path in $EQ12Config.Values) {
        if (-not (Test-Path $path)) {
            try {
                New-Item -ItemType Directory -Path $path -Force | Out-Null
                $logger.Info("Created directory: $path")
            }
            catch {
                $logger.Error("Failed to create directory: $path", @{ error = $_.Exception.Message })
                throw
            }
        }
    }

    # Set proper permissions for service accounts
    try {
        $acl = Get-Acl $EQ12Config.RootPath
        $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
            "NT AUTHORITY\LOCAL SERVICE", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
        )
        $acl.SetAccessRule($accessRule)
        Set-Acl -Path $EQ12Config.RootPath -AclObject $acl
        $logger.Info("Set permissions for LOCAL SERVICE account")
    }
    catch {
        $logger.Warning("Failed to set service permissions", @{ error = $_.Exception.Message })
    }
}

function Set-UTF8Environment {
    <#
    .SYNOPSIS
        Configure system-wide UTF-8 settings
    #>

    $logger.Info("Configuring UTF-8 environment settings")

    try {
        # Set system locale to UTF-8 (Windows 10 1903+)
        $registryPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Nls\CodePage"
        if (Test-Path $registryPath) {
            Set-ItemProperty -Path $registryPath -Name "ACP" -Value "65001" -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $registryPath -Name "OEMCP" -Value "65001" -ErrorAction SilentlyContinue
        }

        # Set environment variables for UTF-8
        $envVars = @{
            "PYTHONIOENCODING"              = "utf-8"
            "PYTHONLEGACYWINDOWSFSENCODING" = "utf-8"
            "PYTHONLEGACYWINDOWSSTDIO"      = "utf-8"
            "NODE_OPTIONS"                  = "--max-old-space-size=4096"
            "CHCP"                          = "65001"
        }

        foreach ($env in $envVars.GetEnumerator()) {
            [Environment]::SetEnvironmentVariable($env.Key, $env.Value, "Machine")
            $logger.Info("Set environment variable: $($env.Key) = $($env.Value)")
        }

        # Create UTF-8 PowerShell profile
        $profileContent = @"
# EQ12 UTF-8 PowerShell Profile
`$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

if (`$PSVersionTable.PSVersion.Major -ge 6) {
    `$PSDefaultParameterValues['*:Encoding'] = 'utf8'
} else {
    `$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
    `$PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
    `$PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'
}

# EQ12 Functions
function Write-EQ12Log {
    param([string]`$Message, [string]`$Level = "INFO")
    `$timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
    `$logEntry = "`$timestamp [`$Level] `$Message"
    Write-Host `$logEntry
    `$logEntry | Out-File "C:\EQ12\logs\powershell_$(Get-Date -Format 'yyyyMMdd').log" -Append -Encoding UTF8
}

Write-Host "=== EQ12 UTF-8 Profile Loaded ===" -ForegroundColor Green
Write-Host "Shortcuts: eq12-status | eq12-restart | eq12-logs" -ForegroundColor Cyan
"@

        $profilePath = Join-Path $EQ12Config.ConfigPath "EQ12_UTF8_Profile.ps1"
        Set-Content -Path $profilePath -Value $profileContent -Encoding UTF8
        $logger.Info("Created UTF-8 PowerShell profile: $profilePath")

    }
    catch {
        $logger.Error("Failed to configure UTF-8 environment", @{ error = $_.Exception.Message })
        throw
    }
}

function Install-EQ12Service {
    <#
    .SYNOPSIS
        Install an EQ12 service as Windows service
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [hashtable]$ServiceConfig
    )

    $logger.Info("Installing service: $Name")

    try {
        # Check if service already exists
        $existingService = Get-Service -Name $Name -ErrorAction SilentlyContinue
        if ($existingService) {
            $logger.Warning("Service $Name already exists, removing first")
            Uninstall-EQ12Service -Name $Name
        }

        # Create service wrapper script
        $wrapperScript = Create-ServiceWrapper -Name $Name -Config $ServiceConfig

        # Install using sc.exe with UTF-8 support
        $scArgs = @(
            "create"
            $Name
            "binPath=`"powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$wrapperScript`"`""
            "DisplayName=`"$($ServiceConfig.DisplayName)`""
            "Description=`"$($ServiceConfig.Description)`""
            "start=$($ServiceConfig.StartupType.ToLower())"
        )

        if ($ServiceConfig.DependsOn -and $ServiceConfig.DependsOn.Count -gt 0) {
            $dependencies = $ServiceConfig.DependsOn -join "/"
            $scArgs += "depend=$dependencies"
        }

        $scResult = & sc.exe @scArgs
        if ($LASTEXITCODE -ne 0) {
            throw "sc.exe failed with exit code $LASTEXITCODE: $scResult"
        }

        # Configure service for UTF-8 environment
        $servicePath = "HKLM:\SYSTEM\CurrentControlSet\Services\$Name"
        if (Test-Path $servicePath) {
            # Set environment variables for the service
            $envBlock = ""
            foreach ($env in $ServiceConfig.EnvironmentVariables.GetEnumerator()) {
                $envBlock += "$($env.Key)=$($env.Value)`0"
            }
            if ($envBlock) {
                $envBlock += "`0"  # Double null terminator
                Set-ItemProperty -Path $servicePath -Name "Environment" -Value ([byte[]][System.Text.Encoding]::Unicode.GetBytes($envBlock))
            }
        }

        $logger.Info("Service $Name installed successfully")

    }
    catch {
        $logger.Error("Failed to install service $Name", @{ error = $_.Exception.Message })
        throw
    }
}

function Create-ServiceWrapper {
    <#
    .SYNOPSIS
        Create a PowerShell wrapper script for the service
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [hashtable]$Config
    )

    $wrapperPath = Join-Path $EQ12Config.ServicePath "$Name-wrapper.ps1"

    $wrapperContent = @"
# EQ12 Service Wrapper for $Name
# Auto-generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

# Force UTF-8 encoding
`$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Set working directory
Set-Location "$($Config.WorkingDirectory)"

# Initialize logging
`$logPath = "C:\EQ12\logs\$($Config.LogFile)"
function Write-ServiceLog {
    param([string]`$Message, [string]`$Level = "INFO")
    `$timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
    `$logEntry = @{
        timestamp = `$timestamp
        level = `$Level
        service = "$Name"
        message = `$Message
        process_id = `$PID
    } | ConvertTo-Json -Compress

    `$logEntry | Out-File `$logPath -Append -Encoding UTF8
}

Write-ServiceLog "Service $Name starting"

try {
    # Set environment variables
"@

    foreach ($env in $Config.EnvironmentVariables.GetEnumerator()) {
        $wrapperContent += "`n    `$env:$($env.Key) = '$($env.Value)'"
    }

    $wrapperContent += @"

    # Start the actual service process
    Write-ServiceLog "Executing: $($Config.ExecutablePath) $($Config.Arguments)"

    `$processInfo = New-Object System.Diagnostics.ProcessStartInfo
    `$processInfo.FileName = "$($Config.ExecutablePath)"
    `$processInfo.Arguments = "$($Config.Arguments)"
    `$processInfo.WorkingDirectory = "$($Config.WorkingDirectory)"
    `$processInfo.UseShellExecute = `$false
    `$processInfo.RedirectStandardOutput = `$true
    `$processInfo.RedirectStandardError = `$true
    `$processInfo.StandardOutputEncoding = [System.Text.Encoding]::UTF8
    `$processInfo.StandardErrorEncoding = [System.Text.Encoding]::UTF8

    `$process = [System.Diagnostics.Process]::Start(`$processInfo)

    # Handle output with UTF-8
    `$outputHandler = {
        param([string]`$data)
        if (`$data) {
            Write-ServiceLog `$data "OUTPUT"
        }
    }

    `$errorHandler = {
        param([string]`$data)
        if (`$data) {
            Write-ServiceLog `$data "ERROR"
        }
    }

    `$process.OutputDataReceived.Add(`$outputHandler)
    `$process.ErrorDataReceived.Add(`$errorHandler)
    `$process.BeginOutputReadLine()
    `$process.BeginErrorReadLine()

    Write-ServiceLog "Process started with PID: `$(`$process.Id)"

    # Wait for process to exit
    `$process.WaitForExit()

    Write-ServiceLog "Process exited with code: `$(`$process.ExitCode)"

} catch {
    Write-ServiceLog "Service error: `$(`$_.Exception.Message)" "ERROR"
    exit 1
}
"@

    Set-Content -Path $wrapperPath -Value $wrapperContent -Encoding UTF8
    $logger.Info("Created service wrapper: $wrapperPath")

    return $wrapperPath
}

function Uninstall-EQ12Service {
    <#
    .SYNOPSIS
        Uninstall an EQ12 service
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $logger.Info("Uninstalling service: $Name")

    try {
        # Stop service if running
        $service = Get-Service -Name $Name -ErrorAction SilentlyContinue
        if ($service -and $service.Status -eq 'Running') {
            Stop-Service -Name $Name -Force
            $logger.Info("Stopped service: $Name")
        }

        # Remove service
        $scResult = & sc.exe delete $Name
        if ($LASTEXITCODE -ne 0) {
            $logger.Warning("sc.exe delete failed: $scResult")
        }
        else {
            $logger.Info("Service $Name removed successfully")
        }

        # Remove wrapper script
        $wrapperPath = Join-Path $EQ12Config.ServicePath "$Name-wrapper.ps1"
        if (Test-Path $wrapperPath) {
            Remove-Item $wrapperPath -Force
            $logger.Info("Removed wrapper script: $wrapperPath")
        }

    }
    catch {
        $logger.Error("Failed to uninstall service $Name", @{ error = $_.Exception.Message })
    }
}

function Start-EQ12Service {
    <#
    .SYNOPSIS
        Start an EQ12 service
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $logger.Info("Starting service: $Name")

    try {
        Start-Service -Name $Name

        # Wait for service to fully start
        $timeout = 30
        $count = 0
        do {
            Start-Sleep -Seconds 1
            $service = Get-Service -Name $Name
            $count++
        } while ($service.Status -ne 'Running' -and $count -lt $timeout)

        if ($service.Status -eq 'Running') {
            $logger.Info("Service $Name started successfully")
        }
        else {
            throw "Service $Name failed to start within $timeout seconds"
        }

    }
    catch {
        $logger.Error("Failed to start service $Name", @{ error = $_.Exception.Message })
        throw
    }
}

function Stop-EQ12Service {
    <#
    .SYNOPSIS
        Stop an EQ12 service
    #>
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    $logger.Info("Stopping service: $Name")

    try {
        Stop-Service -Name $Name -Force

        # Wait for service to fully stop
        $timeout = 30
        $count = 0
        do {
            Start-Sleep -Seconds 1
            $service = Get-Service -Name $Name
            $count++
        } while ($service.Status -ne 'Stopped' -and $count -lt $timeout)

        if ($service.Status -eq 'Stopped') {
            $logger.Info("Service $Name stopped successfully")
        }
        else {
            throw "Service $Name failed to stop within $timeout seconds"
        }

    }
    catch {
        $logger.Error("Failed to stop service $Name", @{ error = $_.Exception.Message })
        throw
    }
}

function Get-EQ12ServiceStatus {
    <#
    .SYNOPSIS
        Get comprehensive status of EQ12 services
    #>

    $logger.Info("Getting EQ12 service status")

    $status = @{
        timestamp      = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
        services       = @{}
        overall_health = "unknown"
        system_info    = @{
            powershell_version = $PSVersionTable.PSVersion.ToString()
            os_version         = [System.Environment]::OSVersion.ToString()
            encoding           = [Console]::OutputEncoding.EncodingName
            culture            = [System.Globalization.CultureInfo]::CurrentCulture.Name
        }
    }

    $healthyCount = 0
    $totalServices = $EQ12Services.Count

    foreach ($serviceName in $EQ12Services.Keys) {
        try {
            $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

            if ($service) {
                $serviceStatus = @{
                    name                 = $serviceName
                    status               = $service.Status.ToString()
                    start_type           = $service.StartType.ToString()
                    display_name         = $service.DisplayName
                    can_stop             = $service.CanStop
                    can_pause            = $service.CanPauseAndContinue
                    dependent_services   = @($service.DependentServices | ForEach-Object { $_.Name })
                    service_dependencies = @($service.ServicesDependedOn | ForEach-Object { $_.Name })
                }

                if ($service.Status -eq 'Running') {
                    $healthyCount++
                    $serviceStatus.health = "healthy"
                }
                elseif ($service.Status -eq 'Stopped') {
                    $serviceStatus.health = "stopped"
                }
                else {
                    $serviceStatus.health = "unhealthy"
                }

                # Get log file info
                $logFile = Join-Path $EQ12Config.LogPath $EQ12Services[$serviceName].LogFile
                if (Test-Path $logFile) {
                    $logInfo = Get-Item $logFile
                    $serviceStatus.log_file = @{
                        path          = $logFile
                        size          = $logInfo.Length
                        last_modified = $logInfo.LastWriteTime.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
                    }
                }

            }
            else {
                $serviceStatus = @{
                    name   = $serviceName
                    status = "Not Installed"
                    health = "not_installed"
                }
            }

            $status.services[$serviceName] = $serviceStatus

        }
        catch {
            $status.services[$serviceName] = @{
                name   = $serviceName
                status = "Error"
                health = "error"
                error  = $_.Exception.Message
            }
        }
    }

    # Calculate overall health
    if ($healthyCount -eq $totalServices) {
        $status.overall_health = "healthy"
    }
    elseif ($healthyCount -gt 0) {
        $status.overall_health = "degraded"
    }
    else {
        $status.overall_health = "failing"
    }

    return $status
}

function Show-EQ12ServiceStatus {
    <#
    .SYNOPSIS
        Display formatted service status
    #>

    $status = Get-EQ12ServiceStatus

    Write-Host "`n🏥 EQ12 SERVICE STATUS REPORT" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host "Timestamp: $($status.timestamp)" -ForegroundColor White
    Write-Host "Overall Health: " -NoNewline

    $healthColor = switch ($status.overall_health) {
        "healthy" { "Green" }
        "degraded" { "Yellow" }
        "failing" { "Red" }
        default { "Gray" }
    }
    Write-Host $status.overall_health.ToUpper() -ForegroundColor $healthColor

    Write-Host "`n📊 Individual Services:" -ForegroundColor White

    foreach ($service in $status.services.Values) {
        $statusColor = switch ($service.health) {
            "healthy" { "Green" }
            "stopped" { "Yellow" }
            "unhealthy" { "Red" }
            "not_installed" { "DarkRed" }
            "error" { "Magenta" }
            default { "Gray" }
        }

        Write-Host "  $($service.name): " -NoNewline
        Write-Host $service.status -ForegroundColor $statusColor

        if ($service.log_file) {
            $sizeKB = [math]::Round($service.log_file.size / 1024, 1)
            Write-Host "    Log: $sizeKB KB (Updated: $($service.log_file.last_modified))" -ForegroundColor DarkGray
        }
    }

    Write-Host "`n💻 System Information:" -ForegroundColor White
    Write-Host "  PowerShell: $($status.system_info.powershell_version)" -ForegroundColor DarkGray
    Write-Host "  OS: $($status.system_info.os_version)" -ForegroundColor DarkGray
    Write-Host "  Encoding: $($status.system_info.encoding)" -ForegroundColor DarkGray
    Write-Host "  Culture: $($status.system_info.culture)" -ForegroundColor DarkGray
}

function Backup-EQ12Configuration {
    <#
    .SYNOPSIS
        Backup current EQ12 configuration and services
    #>

    $logger.Info("Creating EQ12 configuration backup")

    try {
        $backupDir = Join-Path $EQ12Config.BackupPath "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

        # Backup service configurations
        foreach ($serviceName in $EQ12Services.Keys) {
            $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
            if ($service) {
                $serviceConfig = @{
                    name          = $serviceName
                    status        = $service.Status.ToString()
                    start_type    = $service.StartType.ToString()
                    display_name  = $service.DisplayName
                    configuration = $EQ12Services[$serviceName]
                } | ConvertTo-Json -Depth 10

                $configFile = Join-Path $backupDir "$serviceName.json"
                Set-Content -Path $configFile -Value $serviceConfig -Encoding UTF8
            }
        }

        # Backup logs (last 7 days)
        $cutoffDate = (Get-Date).AddDays(-7)
        Get-ChildItem $EQ12Config.LogPath -Filter "*.log" | Where-Object { $_.LastWriteTime -gt $cutoffDate } | ForEach-Object {
            Copy-Item $_.FullName (Join-Path $backupDir $_.Name)
        }

        # Backup configuration files
        if (Test-Path $EQ12Config.ConfigPath) {
            $configBackupDir = Join-Path $backupDir "configs"
            New-Item -ItemType Directory -Path $configBackupDir -Force | Out-Null
            Get-ChildItem $EQ12Config.ConfigPath | ForEach-Object {
                Copy-Item $_.FullName $configBackupDir -Recurse
            }
        }

        $logger.Info("Backup created: $backupDir")
        return $backupDir

    }
    catch {
        $logger.Error("Backup failed", @{ error = $_.Exception.Message })
        throw
    }
}

# Main execution logic
try {
    $logger.Info("EQ12 UTF-8 PowerShell Services Manager started", @{
            action       = $Action
            service_name = $ServiceName
            log_level    = $LogLevel
        })

    # Initialize directories first
    Initialize-EQ12Directories

    switch ($Action) {
        "configure" {
            $logger.Info("Configuring UTF-8 environment")
            Set-UTF8Environment
            Write-Host "✅ UTF-8 environment configured successfully" -ForegroundColor Green
        }

        "install" {
            if ($ServiceName) {
                if ($EQ12Services.ContainsKey($ServiceName)) {
                    Install-EQ12Service -Name $ServiceName -ServiceConfig $EQ12Services[$ServiceName]
                    Write-Host "✅ Service $ServiceName installed successfully" -ForegroundColor Green
                }
                else {
                    throw "Unknown service: $ServiceName"
                }
            }
            else {
                $logger.Info("Installing all EQ12 services")
                Set-UTF8Environment

                foreach ($serviceName in $EQ12Services.Keys) {
                    Install-EQ12Service -Name $serviceName -ServiceConfig $EQ12Services[$serviceName]
                }
                Write-Host "✅ All EQ12 services installed successfully" -ForegroundColor Green
            }
        }

        "uninstall" {
            if ($ServiceName) {
                Uninstall-EQ12Service -Name $ServiceName
                Write-Host "✅ Service $ServiceName uninstalled successfully" -ForegroundColor Green
            }
            else {
                $logger.Info("Uninstalling all EQ12 services")

                # Uninstall in reverse dependency order
                $uninstallOrder = @("EQ12-Analytics", "EQ12-LLM-Engine", "EQ12-Odds-Ingestion", "EQ12-Dashboard")
                foreach ($serviceName in $uninstallOrder) {
                    if ($EQ12Services.ContainsKey($serviceName)) {
                        Uninstall-EQ12Service -Name $serviceName
                    }
                }
                Write-Host "✅ All EQ12 services uninstalled successfully" -ForegroundColor Green
            }
        }

        "start" {
            if ($ServiceName) {
                Start-EQ12Service -Name $ServiceName
                Write-Host "✅ Service $ServiceName started successfully" -ForegroundColor Green
            }
            else {
                $logger.Info("Starting all EQ12 services")

                # Start in dependency order
                $startOrder = @("EQ12-Dashboard", "EQ12-Odds-Ingestion", "EQ12-LLM-Engine", "EQ12-Analytics")
                foreach ($serviceName in $startOrder) {
                    if ($EQ12Services.ContainsKey($serviceName)) {
                        $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
                        if ($service) {
                            Start-EQ12Service -Name $serviceName
                        }
                        else {
                            $logger.Warning("Service $serviceName not installed, skipping")
                        }
                    }
                }
                Write-Host "✅ All available EQ12 services started successfully" -ForegroundColor Green
            }
        }

        "stop" {
            if ($ServiceName) {
                Stop-EQ12Service -Name $ServiceName
                Write-Host "✅ Service $ServiceName stopped successfully" -ForegroundColor Green
            }
            else {
                $logger.Info("Stopping all EQ12 services")

                # Stop in reverse dependency order
                $stopOrder = @("EQ12-Analytics", "EQ12-LLM-Engine", "EQ12-Odds-Ingestion", "EQ12-Dashboard")
                foreach ($serviceName in $stopOrder) {
                    if ($EQ12Services.ContainsKey($serviceName)) {
                        $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
                        if ($service -and $service.Status -eq 'Running') {
                            Stop-EQ12Service -Name $serviceName
                        }
                    }
                }
                Write-Host "✅ All EQ12 services stopped successfully" -ForegroundColor Green
            }
        }

        "restart" {
            if ($ServiceName) {
                Stop-EQ12Service -Name $ServiceName
                Start-Sleep -Seconds 2
                Start-EQ12Service -Name $ServiceName
                Write-Host "✅ Service $ServiceName restarted successfully" -ForegroundColor Green
            }
            else {
                & $MyInvocation.MyCommand.Path -Action stop
                Start-Sleep -Seconds 5
                & $MyInvocation.MyCommand.Path -Action start
                Write-Host "✅ All EQ12 services restarted successfully" -ForegroundColor Green
            }
        }

        "status" {
            Show-EQ12ServiceStatus
        }

        default {
            throw "Unknown action: $Action"
        }
    }

    $logger.Info("Action completed successfully", @{ action = $Action })

}
catch {
    $logger.Error("Action failed", @{
            action      = $Action
            error       = $_.Exception.Message
            stack_trace = $_.ScriptStackTrace
        })

    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1

}
finally {
    if ($logger) {
        $logger.Close()
    }
}
