<#
.SYNOPSIS
    EQ12 MCP Server Setup
.DESCRIPTION
    Downloads and configures essential MCP servers
#>

param()

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   EQ12 MCP SERVER SETUP" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$MCPConfigFile = "$env:APPDATA\Code\User\mcp.json"
$RepoRoot = "C:\EQ12_BROKEN_20251122_210342"

Write-Host "[1/3] Checking prerequisites..." -ForegroundColor Yellow

# Check Node.js
try {
    $NodeVersion = node --version 2>$null
    Write-Host "  ✓ Node.js: $NodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Node.js not found" -ForegroundColor Red
    Write-Host "    Install from: https://nodejs.org" -ForegroundColor Gray
    exit 1
}

# Check Python  
try {
    $PythonVersion = python --version 2>$null
    Write-Host "  ✓ Python: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found" -ForegroundColor Red
    Write-Host "    Install from: https://python.org" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "[2/3] Installing Python MCP packages..." -ForegroundColor Yellow

pip install mcp-server-git mcp-server-fetch mcp-server-time --quiet
Write-Host "  ✓ Python MCP packages installed" -ForegroundColor Green

Write-Host ""
Write-Host "[3/3] Creating MCP configuration..." -ForegroundColor Yellow

$Config = @"
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "$($RepoRoot.Replace('\', '\\'))"]
    },
    "git": {
      "command": "python",
      "args": ["-m", "mcp_servers.git"]
    },
    "fetch": {
      "command": "python",
      "args": ["-m", "mcp_servers.fetch"]
    },
    "docker": {
      "command": "node",
      "args": ["$($RepoRoot.Replace('\', '\\'))\\docker_mcp_server\\index.js"]
    },
    "eq12-custom": {
      "command": "python",
      "args": ["$($RepoRoot.Replace('\', '\\'))\\scripts\\eq12_mcp_server.py"],
      "env": {
        "PYTHONPATH": "$($RepoRoot.Replace('\', '\\'))"
      }
    }
  }
}
"@

# Ensure directory exists
$MCPDir = Split-Path $MCPConfigFile -Parent
if (-not (Test-Path $MCPDir)) {
    New-Item -Path $MCPDir -ItemType Directory -Force | Out-Null
}

$Config | Set-Content $MCPConfigFile -Encoding UTF8

Write-Host "  ✓ Configuration saved to:" -ForegroundColor Green
Write-Host "    $MCPConfigFile" -ForegroundColor Gray

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "   SETUP COMPLETE" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "MCPs Configured:" -ForegroundColor Cyan
Write-Host "  • Filesystem MCP - File operations" -ForegroundColor White
Write-Host "  • Git MCP - Repository management" -ForegroundColor White
Write-Host "  • Fetch MCP - Web requests" -ForegroundColor White
Write-Host "  • Docker MCP - Container management" -ForegroundColor White
Write-Host "  • EQ12 Custom MCP - Workspace automation" -ForegroundColor White
Write-Host ""
Write-Host "Next:" -ForegroundColor Yellow
Write-Host "  1. Restart VS Code" -ForegroundColor Gray
Write-Host "  2. MCPs will load automatically" -ForegroundColor Gray
Write-Host ""
