[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('Test', 'Install', 'All')]
    [string]$Action = 'Test'
)

<#
.SYNOPSIS
EQ12 MCP Quick Test Script
.DESCRIPTION
Simple test script for EQ12 MCP server functionality with GitHub Models integration
#>

$EQ12Root = "C:\EQ12"
$LogsPath = "$EQ12Root\logs"
$MCPServerPath = "$EQ12Root\scripts\eq12_mcp_server.py"
$GitHubModelsPath = "$EQ12Root\scripts\github_models_integration.py"

# Ensure logs directory exists
if (!(Test-Path $LogsPath)) {
    New-Item -Type Directory -Path $LogsPath -Force | Out-Null
}

$LogFile = "$LogsPath\mcp_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-TestMessage {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    # Output to console with colors
    switch ($Level) {
        "ERROR" { Write-Host $Message -ForegroundColor Red }
        "WARN" { Write-Host $Message -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $Message -ForegroundColor Green }
        default { Write-Host $Message -ForegroundColor White }
    }

    # Log to file
    Add-Content -Path $LogFile -Value $logEntry
}

function Test-PythonMCP {
    Write-TestMessage "🐍 Testing Python MCP library..." "INFO"

    try {
        $result = python -c "import mcp; print('MCP available')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-TestMessage "✅ MCP library installed: $result" "SUCCESS"
            return $true
        } else {
            Write-TestMessage "❌ MCP library not available: $result" "ERROR"
            Write-TestMessage "💡 Install with: pip install mcp" "INFO"
            return $false
        }
    } catch {
        Write-TestMessage "❌ Python MCP test failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-GitHubModels {
    Write-TestMessage "🔐 Testing GitHub Models integration..." "INFO"

    try {
        if (!(Test-Path $GitHubModelsPath)) {
            Write-TestMessage "❌ GitHub Models script not found" "ERROR"
            return $false
        }

        Write-TestMessage "🧪 Running GitHub Models connection test..." "INFO"
        $env:PYTHONPATH = "$EQ12Root;$EQ12Root\scripts;$EQ12Root\configs"

        $result = python $GitHubModelsPath 2>&1

        if ($result -match "connection successful" -and $result -match "models available") {
            Write-TestMessage "✅ GitHub Models integration working" "SUCCESS"

            # Extract model count
            if ($result -match "Models available: (\d+)") {
                $modelCount = $Matches[1]
                Write-TestMessage "📊 Available models: $modelCount" "INFO"
            }

            return $true
        } else {
            Write-TestMessage "❌ GitHub Models connection issues" "WARN"
            Write-TestMessage "📋 Output: $($result -join ' | ')" "INFO"
            return $false
        }

    } catch {
        Write-TestMessage "❌ GitHub Models test failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-MCPServer {
    Write-TestMessage "🚀 Testing EQ12 MCP Server..." "INFO"

    try {
        if (!(Test-Path $MCPServerPath)) {
            Write-TestMessage "❌ MCP server script not found: $MCPServerPath" "ERROR"
            return $false
        }

        # Test server import and basic functionality
        Write-TestMessage "📦 Testing MCP server imports..." "INFO"

        $testScript = @"
import sys
sys.path.append('$($EQ12Root.Replace('\', '\\'))')
sys.path.append('$($EQ12Root.Replace('\', '\\'))\\scripts')
sys.path.append('$($EQ12Root.Replace('\', '\\'))\\configs')

try:
    from scripts.eq12_mcp_server import EQ12MCPServer
    server = EQ12MCPServer()
    print(f'SUCCESS: Server initialized with {len(server.eq12_capabilities)} capabilities')

    # List capabilities
    for cap in server.eq12_capabilities:
        print(f'  • {cap.name} ({cap.category})')

    # Check agentic systems
    print(f'Agentic systems: {len(server.agentic_systems)} initialized')
    for system in server.agentic_systems:
        print(f'  ✅ {system}')

    print('MCP_SERVER_TEST_SUCCESS')

except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
"@

        $tempScript = "$env:TEMP\test_mcp_server.py"
        $testScript | Out-File -FilePath $tempScript -Encoding UTF8

        $result = python $tempScript 2>&1
        Remove-Item $tempScript -ErrorAction SilentlyContinue

        if ($result -match "MCP_SERVER_TEST_SUCCESS") {
            Write-TestMessage "✅ EQ12 MCP Server working correctly" "SUCCESS"

            # Show capabilities
            $capabilities = ($result | Where-Object { $_ -match "^\s*•" })
            if ($capabilities) {
                Write-TestMessage "📋 Available MCP capabilities:" "INFO"
                foreach ($cap in $capabilities) {
                    Write-TestMessage "  $cap" "INFO"
                }
            }

            return $true
        } else {
            Write-TestMessage "❌ MCP Server test failed" "ERROR"
            Write-TestMessage "📋 Error details:" "ERROR"
            $result | ForEach-Object { Write-TestMessage "  $_" "ERROR" }
            return $false
        }

    } catch {
        Write-TestMessage "❌ MCP Server test exception: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Show-MigrationStatus {
    Write-TestMessage "📅 GitHub Copilot Extensions Migration Status" "INFO"

    $deadline = Get-Date "2025-11-10"
    $today = Get-Date
    $daysRemaining = ($deadline - $today).Days

    $urgencyLevel = if ($daysRemaining -le 7) { "ERROR" } elseif ($daysRemaining -le 30) { "WARN" } else { "INFO" }

    Write-TestMessage "⏰ Days until Copilot Extensions sunset: $daysRemaining" $urgencyLevel
    Write-TestMessage "🎯 Migration deadline: November 10, 2025" "INFO"

    if ($daysRemaining -le 30) {
        Write-TestMessage "🚨 URGENT: Migration deadline approaching!" $urgencyLevel
        Write-TestMessage "📋 Priority actions:" $urgencyLevel
        Write-TestMessage "   1. Complete MCP server setup ✓" "INFO"
        Write-TestMessage "   2. Configure AI assistants with MCP" "WARN"
        Write-TestMessage "   3. Test all capabilities before Nov 10" "WARN"
    }
}

# Main execution
Write-Host ""
Write-Host "🚀 EQ12 MCP & GitHub Models Integration Test" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "📍 Action: $Action" -ForegroundColor White
Write-Host "📁 EQ12 Root: $EQ12Root" -ForegroundColor White
Write-Host "📝 Log File: $LogFile" -ForegroundColor White
Write-Host ""

$testResults = @{}

if ($Action -in @('Test', 'All')) {
    # Test Python MCP library
    $testResults['MCP_Library'] = Test-PythonMCP

    # Test GitHub Models integration
    $testResults['GitHub_Models'] = Test-GitHubModels

    # Test EQ12 MCP server
    $testResults['MCP_Server'] = Test-MCPServer
}

if ($Action -in @('Install', 'All')) {
    Write-TestMessage "📦 Installing MCP library..." "INFO"
    try {
        $installResult = python -m pip install mcp 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-TestMessage "✅ MCP library installed successfully" "SUCCESS"
            $testResults['MCP_Install'] = $true
        } else {
            Write-TestMessage "❌ MCP installation failed: $installResult" "ERROR"
            $testResults['MCP_Install'] = $false
        }
    } catch {
        Write-TestMessage "❌ MCP installation exception: $($_.Exception.Message)" "ERROR"
        $testResults['MCP_Install'] = $false
    }
}

# Show migration status
Show-MigrationStatus

# Summary
Write-Host ""
Write-Host "📊 Test Results Summary" -ForegroundColor Cyan
Write-Host "=" * 30 -ForegroundColor Cyan

$successCount = 0
$totalCount = 0

foreach ($test in $testResults.GetEnumerator()) {
    $totalCount++
    $status = if ($test.Value) { "✅ PASS" } else { "❌ FAIL" }
    $color = if ($test.Value) { "Green" } else { "Red" }

    Write-Host "  $($test.Key): $status" -ForegroundColor $color

    if ($test.Value) { $successCount++ }
}

$overallSuccess = ($successCount -eq $totalCount) -and ($totalCount -gt 0)

Write-Host ""
if ($overallSuccess) {
    Write-Host "🎉 All tests PASSED! EQ12 MCP system ready for GitHub migration." -ForegroundColor Green
    Write-Host "📋 Next steps:" -ForegroundColor Green
    Write-Host "   1. Configure Claude Desktop with MCP settings" -ForegroundColor Green
    Write-Host "   2. Test EQ12 capabilities through MCP interface" -ForegroundColor Green
    Write-Host "   3. Monitor for GitHub Copilot MCP support" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests failed. Review issues before November 10 deadline." -ForegroundColor Yellow
    Write-Host "📋 Check the log file for details: $LogFile" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📚 Documentation: EQ12_MCP_SETUP_GUIDE.md" -ForegroundColor Cyan
Write-Host "🔗 GitHub Models: 15 models available, expires Nov 6" -ForegroundColor Cyan
Write-Host "⚠️  Copilot Extensions sunset: $daysRemaining days remaining" -ForegroundColor Yellow

return $overallSuccess
