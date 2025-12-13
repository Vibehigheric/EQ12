[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('Install', 'Test', 'Configure', 'Validate', 'All')]
    [string]$Action = 'All',

    [Parameter()]
    [switch]$Verbose
)

<#
.SYNOPSIS
EQ12 Model Context Protocol (MCP) Server Installation and Testing

.DESCRIPTION
Automates the installation, configuration, and testing of EQ12's MCP server
for GitHub Copilot Extensions migration (deadline: November 10, 2025)

.PARAMETER Action
Action to perform: Install, Test, Configure, Validate, or All

.PARAMETER Verbose
Enable verbose logging

.EXAMPLE
.\Install-EQ12MCP.ps1 -Action All -Verbose
#>

# EQ12 paths
$EQ12Root = "C:\EQ12"
$ScriptsPath = "$EQ12Root\scripts"
$ConfigsPath = "$EQ12Root\configs"
$LogsPath = "$EQ12Root\logs"
$MCPServerPath = "$ScriptsPath\eq12_mcp_server.py"
$MCPConfigPath = "$ConfigsPath\eq12_mcp_config.json"

# Logging setup
$LogFile = "$LogsPath\mcp_installation_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
if (!(Test-Path $LogsPath)) { New-Item -Type Directory -Path $LogsPath -Force | Out-Null }

function Write-LogMessage {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Output $logEntry
    Add-Content -Path $LogFile -Value $logEntry

    switch ($Level) {
        "ERROR" { Write-Host $Message -ForegroundColor Red }
        "WARN" { Write-Host $Message -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $Message -ForegroundColor Green }
        default { Write-Host $Message -ForegroundColor White }
    }
}

function Install-MCPDependencies {
    Write-LogMessage "🔧 Installing Model Context Protocol dependencies..." "INFO"

    try {
        # Check if pip is available
        $pipCheck = python -m pip --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-LogMessage "❌ Python pip not available" "ERROR"
            return $false
        }

        Write-LogMessage "✅ Python pip available: $pipCheck" "SUCCESS"

        # Install MCP library
        Write-LogMessage "📦 Installing MCP library..." "INFO"
        $mcpInstall = python -m pip install mcp 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "✅ MCP library installed successfully" "SUCCESS"
        }
        else {
            Write-LogMessage "❌ MCP installation failed: $mcpInstall" "ERROR"
            return $false
        }

        # Verify MCP installation
        $mcpTest = python -c "import mcp; print('MCP version available')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-LogMessage "✅ MCP import test successful: $mcpTest" "SUCCESS"
            return $true
        }
        else {
            Write-LogMessage "❌ MCP import test failed: $mcpTest" "ERROR"
            return $false
        }

    }
    catch {
        Write-LogMessage "❌ Exception during MCP installation: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-EQ12MCPServer {
    Write-LogMessage "🧪 Testing EQ12 MCP Server startup..." "INFO"

    try {
        if (!(Test-Path $MCPServerPath)) {
            Write-LogMessage "❌ EQ12 MCP server not found: $MCPServerPath" "ERROR"
            return $false
        }

        # Test server startup (timeout after 10 seconds)
        Write-LogMessage "🚀 Starting MCP server test (10 second timeout)..." "INFO"

        $job = Start-Job -ScriptBlock {
            param($ServerPath, $EQ12Root)
            $env:PYTHONPATH = "$EQ12Root;$EQ12Root\scripts;$EQ12Root\configs"
            python $ServerPath 2>&1
        } -ArgumentList $MCPServerPath, $EQ12Root

        # Wait for startup or timeout
        $timeout = 10
        $elapsed = 0

        while ($job.State -eq "Running" -and $elapsed -lt $timeout) {
            Start-Sleep -Seconds 1
            $elapsed++
            Write-Progress -Activity "Testing MCP Server" -Status "Waiting for startup..." -PercentComplete (($elapsed / $timeout) * 100)
        }

        # Stop the job
        Stop-Job $job -ErrorAction SilentlyContinue
        $output = Receive-Job $job
        Remove-Job $job -ErrorAction SilentlyContinue

        # Analyze output
        $outputStr = $output -join "`n"

        if ($outputStr -match "Starting EQ12 Model Context Protocol") {
            Write-LogMessage "✅ MCP server started successfully" "SUCCESS"
            Write-LogMessage "📋 Server output preview:" "INFO"
            $output | Select-Object -First 5 | ForEach-Object {
                Write-LogMessage "   $_" "INFO"
            }
            return $true
        }
        else {
            Write-LogMessage "❌ MCP server startup failed" "ERROR"
            Write-LogMessage "📋 Error output:" "ERROR"
            $output | ForEach-Object { Write-LogMessage "   $_" "ERROR" }
            return $false
        }

    }
    catch {
        Write-LogMessage "❌ Exception during MCP server test: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Set-MCPConfiguration {
    Write-LogMessage "⚙️ Configuring MCP client settings..." "INFO"

    try {
        # Verify MCP config exists
        if (!(Test-Path $MCPConfigPath)) {
            Write-LogMessage "❌ MCP config not found: $MCPConfigPath" "ERROR"
            return $false
        }

        # Test JSON validity
        $config = Get-Content $MCPConfigPath -Raw | ConvertFrom-Json
        Write-LogMessage "✅ MCP configuration JSON is valid" "SUCCESS"

        # Show configuration
        Write-LogMessage "📋 MCP Server Configuration:" "INFO"
        Write-LogMessage "   Command: $($config.mcpServers.'eq12-agentic-ai'.command)" "INFO"
        Write-LogMessage "   Args: $($config.mcpServers.'eq12-agentic-ai'.args -join ' ')" "INFO"

        # Instructions for different clients
        Write-LogMessage "📝 Client Configuration Instructions:" "INFO"
        Write-LogMessage "   Claude Desktop: Copy config to %APPDATA%\Claude\claude_desktop_config.json" "INFO"
        Write-LogMessage "   GitHub Copilot: MCP support coming soon" "WARN"

        return $true

    }
    catch {
        Write-LogMessage "❌ Exception during MCP configuration: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-EQ12AgenticSystems {
    Write-LogMessage "🤖 Validating EQ12 Agentic AI systems..." "INFO"

    try {
        # Test individual agentic systems
        $systemTests = @(
            @{ Name = "Secret Detection"; Script = "agentic_secret_detection.py" },
            @{ Name = "DevOps Accelerator"; Script = "agentic_devops_accelerator.py" },
            @{ Name = "Security Hub"; Script = "eq12_security_intelligence_hub.py" }
        )

        $successCount = 0

        foreach ($test in $systemTests) {
            $scriptPath = "$ScriptsPath\$($test.Script)"

            if (Test-Path $scriptPath) {
                Write-LogMessage "✅ Found: $($test.Name)" "SUCCESS"
                $successCount++
            }
            else {
                Write-LogMessage "❌ Missing: $($test.Name) ($scriptPath)" "WARN"
            }
        }

        $successRate = ($successCount / $systemTests.Count) * 100
        Write-LogMessage "📊 Agentic systems availability: $successCount/$($systemTests.Count) ($successRate%)" "INFO"

        if ($successCount -ge 2) {
            Write-LogMessage "✅ Sufficient agentic systems available for MCP operation" "SUCCESS"
            return $true
        }
        else {
            Write-LogMessage "⚠️ Limited agentic systems available - MCP server will have reduced functionality" "WARN"
            return $false
        }

    }
    catch {
        Write-LogMessage "❌ Exception during agentic systems validation: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Show-MCPMigrationStatus {
    Write-LogMessage "📅 GitHub Copilot Extensions Migration Status" "INFO"

    $deadline = Get-Date "2025-11-10"
    $today = Get-Date
    $daysRemaining = ($deadline - $today).Days

    Write-LogMessage "⏰ Days remaining until Copilot Extensions sunset: $daysRemaining" $(if ($daysRemaining -lt 30) { "ERROR" } else { "WARN" })
    Write-LogMessage "🎯 Migration deadline: November 10, 2025" "INFO"
    Write-LogMessage "🔄 Brownout testing period: November 3-7, 2025" "INFO"

    if ($daysRemaining -lt 30) {
        Write-LogMessage "🚨 URGENT: Less than 30 days remaining for migration!" "ERROR"
        Write-LogMessage "📋 Immediate action required:" "ERROR"
        Write-LogMessage "   1. Complete MCP server setup and testing" "ERROR"
        Write-LogMessage "   2. Configure AI assistants with MCP settings" "ERROR"
        Write-LogMessage "   3. Validate all EQ12 capabilities work via MCP" "ERROR"
    }
}

# Main execution
Write-LogMessage "🚀 EQ12 Model Context Protocol (MCP) Installation Started" "INFO"
Write-LogMessage "📍 Action: $Action" "INFO"
Write-LogMessage "📁 EQ12 Root: $EQ12Root" "INFO"
Write-LogMessage "📝 Log File: $LogFile" "INFO"

$allSuccess = $true

if ($Action -in @('Install', 'All')) {
    $installResult = Install-MCPDependencies
    $allSuccess = $allSuccess -and $installResult
}

if ($Action -in @('Test', 'All')) {
    $testResult = Test-EQ12MCPServer
    $allSuccess = $allSuccess -and $testResult
}

if ($Action -in @('Configure', 'All')) {
    $configResult = Set-MCPConfiguration
    $allSuccess = $allSuccess -and $configResult
}

if ($Action -in @('Validate', 'All')) {
    $validateResult = Test-EQ12AgenticSystems
    $allSuccess = $allSuccess -and $validateResult
}

# Always show migration status
Show-MCPMigrationStatus

# Final summary
Write-LogMessage ("=" * 60) "INFO"
if ($allSuccess) {
    Write-LogMessage "🎉 EQ12 MCP Setup Complete - Ready for GitHub Migration!" "SUCCESS"
    Write-LogMessage "📋 Next steps:" "SUCCESS"
    Write-LogMessage "   1. Configure your AI assistant with MCP settings" "SUCCESS"
    Write-LogMessage "   2. Test EQ12 capabilities through MCP interface" "SUCCESS"
    Write-LogMessage "   3. Prepare for Copilot Extensions sunset (Nov 10)" "SUCCESS"
}
else {
    Write-LogMessage "⚠️ EQ12 MCP Setup completed with issues" "WARN"
    Write-LogMessage "📋 Review the log file for details: $LogFile" "WARN"
    Write-LogMessage "🔧 Fix any errors before the November 10 deadline" "WARN"
}

Write-LogMessage "📊 Installation log saved to: $LogFile" "INFO"
Write-LogMessage "📚 See EQ12_MCP_SETUP_GUIDE.md for detailed instructions" "INFO"
Write-LogMessage ("=" * 60) "INFO"

# Return success status
return $allSuccess
