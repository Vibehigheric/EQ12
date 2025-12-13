<#
.SYNOPSIS
    EQ12 MCP Server Setup - Install and configure all required MCP servers
.DESCRIPTION
    Scans workspace, identifies needed MCPs, and sets them up automatically
.EXAMPLE
    .\EQ12_MCP_SETUP.ps1
#>

[CmdletBinding()]
param()

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   EQ12 MCP SERVER SETUP" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$RepoRoot = "C:\EQ12_BROKEN_20251122_210342"
$MCPConfigFile = "$env:APPDATA\Code\User\mcp.json"

# Essential MCP servers for EQ12 workspace
$RequiredMCPs = @{
    "filesystem" = @{
        Name = "Filesystem MCP"
        Command = "npx"
        Args = @("-y", "@modelcontextprotocol/server-filesystem", $RepoRoot)
        Description = "File operations and workspace navigation"
        Required = $true
    }
    "git" = @{
        Name = "Git MCP"
        Command = "python"
        Args = @("-m", "mcp_servers.git")
        Description = "Git repository operations"
        Required = $true
        PythonPackage = "mcp-server-git"
    }
    "github" = @{
        Name = "GitHub MCP"
        Command = "npx"
        Args = @("-y", "@modelcontextprotocol/server-github")
        Description = "GitHub API integration"
        Required = $false
        EnvVars = @{
            GITHUB_TOKEN = $env:GITHUB_TOKEN
        }
    }
    "docker" = @{
        Name = "Docker MCP"
        Command = "node"
        Args = @("$RepoRoot\docker_mcp_server\index.js")
        Description = "Docker container management"
        Required = $true
    }
    "fetch" = @{
        Name = "Web Fetch MCP"
        Command = "python"
        Args = @("-m", "mcp_servers.fetch")
        Description = "Web scraping and API calls"
        Required = $true
        PythonPackage = "mcp-server-fetch"
    }
    "brave-search" = @{
        Name = "Brave Search MCP"
        Command = "npx"
        Args = @("-y", "@modelcontextprotocol/server-brave-search")
        Description = "Web search capabilities"
        Required = $false
        EnvVars = @{
            BRAVE_API_KEY = $env:BRAVE_API_KEY
        }
    }
    "postgres" = @{
        Name = "PostgreSQL MCP"
        Command = "npx"
        Args = @("-y", "@modelcontextprotocol/server-postgres")
        Description = "Database operations"
        Required = $false
    }
    "eq12-custom" = @{
        Name = "EQ12 Custom MCP"
        Command = "python"
        Args = @("$RepoRoot\scripts\eq12_mcp_server.py")
        Description = "EQ12-specific automation"
        Required = $true
    }
}

Write-Host "[1/4] Checking existing MCP configuration..." -ForegroundColor Yellow
Write-Host ""

$ExistingConfig = @{
    mcpServers = @{}
}

if (Test-Path $MCPConfigFile) {
    try {
        $ExistingConfig = Get-Content $MCPConfigFile -Raw | ConvertFrom-Json
        Write-Host "  ✓ Found existing MCP config" -ForegroundColor Green
        Write-Host "    Location: $MCPConfigFile" -ForegroundColor Gray
        Write-Host "    Servers: $($ExistingConfig.mcpServers.PSObject.Properties.Count)" -ForegroundColor Gray
    }
    catch {
        Write-Host "  ! Existing config is invalid, will recreate" -ForegroundColor Yellow
    }
}
else {
    Write-Host "  ! No existing MCP config found" -ForegroundColor Yellow
    Write-Host "    Will create: $MCPConfigFile" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[2/4] Installing required dependencies..." -ForegroundColor Yellow
Write-Host ""

# Check Node.js
try {
    $NodeVersion = node --version 2>$null
    Write-Host "  ✓ Node.js: $NodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Node.js not found - install from https://nodejs.org" -ForegroundColor Red
    $HasErrors = $true
}

# Check Python
try {
    $PythonVersion = python --version 2>$null
    Write-Host "  ✓ Python: $PythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Python not found - install from https://python.org" -ForegroundColor Red
    $HasErrors = $true
}

# Install Python MCP packages
if (-not $HasErrors) {
    Write-Host ""
    Write-Host "  Installing Python MCP packages..." -ForegroundColor Cyan
    
    $PythonMCPs = @("mcp-server-git", "mcp-server-fetch", "mcp-server-time")
    foreach ($Package in $PythonMCPs) {
        try {
            Write-Host "    Installing $Package..." -ForegroundColor Gray
            pip install $Package --quiet 2>$null
            Write-Host "    ✓ $Package installed" -ForegroundColor Green
        }
        catch {
            Write-Host "    ! $Package install failed (may already be installed)" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "[3/4] Configuring MCP servers..." -ForegroundColor Yellow
Write-Host ""

$NewConfig = @{
    mcpServers = @{}
}

foreach ($MCPKey in $RequiredMCPs.Keys) {
    $MCP = $RequiredMCPs[$MCPKey]
    
    # Check if already configured
    if ($ExistingConfig.mcpServers.PSObject.Properties.Name -contains $MCPKey) {
        Write-Host "  ✓ $($MCP.Name) - already configured" -ForegroundColor Green
        $NewConfig.mcpServers[$MCPKey] = $ExistingConfig.mcpServers.$MCPKey
        continue
    }
    
    # Build new configuration
    $MCPConfig = @{
        command = $MCP.Command
        args = $MCP.Args
    }
    
    if ($MCP.EnvVars) {
        $MCPConfig.env = $MCP.EnvVars
    }
    
    $NewConfig.mcpServers[$MCPKey] = $MCPConfig
    
    if ($MCP.Required) {
        Write-Host "  + $($MCP.Name) - ADDED (required)" -ForegroundColor Cyan
    }
    else {
        Write-Host "  + $($MCP.Name) - ADDED (optional)" -ForegroundColor Gray
    }
    Write-Host "    $($MCP.Description)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "[4/4] Saving MCP configuration..." -ForegroundColor Yellow
Write-Host ""

try {
    # Ensure directory exists
    $MCPConfigDir = Split-Path $MCPConfigFile -Parent
    if (-not (Test-Path $MCPConfigDir)) {
        New-Item -Path $MCPConfigDir -ItemType Directory -Force | Out-Null
    }
    
    # Write config
    $NewConfig | ConvertTo-Json -Depth 10 | Set-Content $MCPConfigFile -Encoding UTF8
    Write-Host "  ✓ Configuration saved" -ForegroundColor Green
    Write-Host "    Location: $MCPConfigFile" -ForegroundColor Gray
}
catch {
    Write-Host "  ✗ Failed to save configuration: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "   MCP SETUP COMPLETE" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""

Write-Host "Configured MCP Servers:" -ForegroundColor Cyan
foreach ($MCPKey in $NewConfig.mcpServers.Keys) {
    $MCP = $RequiredMCPs[$MCPKey]
    Write-Host "  • $($MCP.Name)" -ForegroundColor White
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Restart VS Code to load MCP servers" -ForegroundColor Gray
Write-Host "  2. Open Copilot Chat and test with:" -ForegroundColor Gray
Write-Host "     '@workspace what MCPs are available?'" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Set environment variables for optional MCPs:" -ForegroundColor Gray
Write-Host "     - GITHUB_TOKEN (for GitHub MCP)" -ForegroundColor Gray
Write-Host "     - BRAVE_API_KEY (for search)" -ForegroundColor Gray
Write-Host ""

return @{
    ConfigFile = $MCPConfigFile
    ServersConfigured = $NewConfig.mcpServers.Keys.Count
    RequiresRestart = $true
}
