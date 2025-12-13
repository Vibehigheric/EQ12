# ==================================================================
# EQ12 MCP SERVER SELECTION GUIDE
# ==================================================================
# Based on system analysis and EQ12 project needs
# Repository: vibehigheric/edgegod-parlay
# ==================================================================

Write-Host "`n=== EQ12 MCP SERVER SELECTION GUIDE ===" -ForegroundColor Cyan
Write-Host ""

# Project Analysis Results
Write-Host "PROJECT ANALYSIS:" -ForegroundColor Yellow
Write-Host "  Repository: vibehigheric/edgegod-parlay (sports betting/odds analysis)" -ForegroundColor White
Write-Host "  Stack: Python, PowerShell, web scraping, API integration" -ForegroundColor White
Write-Host "  Key Needs: File ops, Git, web fetching, data processing, system monitoring" -ForegroundColor White
Write-Host ""

# ==================================================================
# RECOMMENDED MCP SERVERS FOR EQ12
# ==================================================================

$RecommendedServers = @(
    @{
        Name = "filesystem (@modelcontextprotocol/server-filesystem)"
        Priority = "CRITICAL"
        Reason = "Essential for AI to read/write project files, navigate workspace structure"
        Command = "npx -y @modelcontextprotocol/server-filesystem C:\EQ12"
    },
    @{
        Name = "git (mcp-server-git)"
        Priority = "CRITICAL"
        Reason = "Essential for AI to manage repo, check status, create commits, handle branches"
        Command = "python -m mcp_server_git --repository C:\EQ12"
    },
    @{
        Name = "fetch (mcp-server-fetch)"
        Priority = "HIGH"
        Reason = "Critical for web scraping, API calls, fetching odds data (core EQ12 feature)"
        Command = "python -m mcp_server_fetch"
    },
    @{
        Name = "time (mcp-server-time)"
        Priority = "MEDIUM"
        Reason = "Useful for timestamp conversions, timezone handling in sports data"
        Command = "python -m mcp_server_time"
    },
    @{
        Name = "GitHub"
        Priority = "HIGH"
        Reason = "Manage issues, PRs, releases for vibehigheric/edgegod-parlay repository"
        Command = "npx -y @modelcontextprotocol/server-github"
        Note = "Requires GITHUB_PERSONAL_ACCESS_TOKEN environment variable"
    },
    @{
        Name = "Playwright"
        Priority = "HIGH"
        Reason = "Browser automation for scraping betting sites (core EQ12 capability)"
        Command = "npx -y @modelcontextprotocol/server-playwright"
    }
)

$OptionalServers = @(
    @{
        Name = "Netdata"
        Priority = "OPTIONAL"
        Reason = "System monitoring - useful for production deployment but not development"
        Command = "docker run -d -p 19999:19999 netdata/netdata"
    },
    @{
        Name = "Context7"
        Priority = "OPTIONAL"
        Reason = "Code docs - redundant if using GitHub + filesystem MCPs"
        Command = "Skip - covered by filesystem + GitHub"
    },
    @{
        Name = "ChromeDevTools"
        Priority = "OPTIONAL"
        Reason = "Similar to Playwright but more complex - use Playwright instead"
        Command = "Skip - use Playwright"
    },
    @{
        Name = "MongoDB/Elasticsearch/Supabase"
        Priority = "NOT NEEDED"
        Reason = "No database layer detected in EQ12 project"
        Command = "Skip - not using these databases"
    }
)

# Display Recommendations
Write-Host "=== RECOMMENDED MCP SERVERS (INSTALL THESE) ===" -ForegroundColor Green
Write-Host ""

foreach ($server in $RecommendedServers) {
    $colorMap = @{
        "CRITICAL" = "Red"
        "HIGH" = "Yellow"
        "MEDIUM" = "Cyan"
    }
    $color = $colorMap[$server.Priority]
    
    Write-Host "[$($server.Priority)] $($server.Name)" -ForegroundColor $color
    Write-Host "  Reason: $($server.Reason)" -ForegroundColor DarkGray
    Write-Host "  Command: $($server.Command)" -ForegroundColor White
    if ($server.Note) {
        Write-Host "  NOTE: $($server.Note)" -ForegroundColor DarkYellow
    }
    Write-Host ""
}

Write-Host ""
Write-Host "=== OPTIONAL/SKIP SERVERS ===" -ForegroundColor DarkGray
Write-Host ""

foreach ($server in $OptionalServers) {
    Write-Host "[$($server.Priority)] $($server.Name)" -ForegroundColor DarkGray
    Write-Host "  Reason: $($server.Reason)" -ForegroundColor DarkGray
    Write-Host ""
}

# ==================================================================
# INSTALLATION INSTRUCTIONS
# ==================================================================

Write-Host ""
Write-Host "=== INSTALLATION STEPS ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Install Python MCP packages:" -ForegroundColor Yellow
Write-Host "   pip install mcp-server-git mcp-server-fetch mcp-server-time" -ForegroundColor White
Write-Host ""

Write-Host "2. Verify Node.js/NPX installed:" -ForegroundColor Yellow
Write-Host "   npx --version" -ForegroundColor White
Write-Host ""

Write-Host "3. Create mcp.json configuration:" -ForegroundColor Yellow
Write-Host "   Location: C:\Users\$env:USERNAME\AppData\Roaming\Code\User\mcp.json" -ForegroundColor White
Write-Host ""

Write-Host "4. Use configuration template below:" -ForegroundColor Yellow
Write-Host ""

# ==================================================================
# MCP.JSON TEMPLATE
# ==================================================================

$mcpJsonPath = "$env:APPDATA\Code\User\mcp.json"

Write-Host "=== RECOMMENDED MCP.JSON CONFIGURATION ===" -ForegroundColor Green
Write-Host ""

$mcpConfig = @"
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\EQ12"]
    },
    "git": {
      "command": "python",
      "args": ["-m", "mcp_server_git", "--repository", "C:\\EQ12"]
    },
    "fetch": {
      "command": "python",
      "args": ["-m", "mcp_server_fetch"]
    },
    "time": {
      "command": "python",
      "args": ["-m", "mcp_server_time"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "PASTE_YOUR_TOKEN_HERE"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-playwright"]
    }
  }
}
"@

Write-Host $mcpConfig -ForegroundColor White
Write-Host ""

# Offer to create the file
Write-Host "=== AUTO-INSTALLATION ===" -ForegroundColor Cyan
Write-Host ""
$response = Read-Host "Create mcp.json file now? (y/n)"

if ($response -eq 'y' -or $response -eq 'Y') {
    $mcpDir = Split-Path -Path $mcpJsonPath -Parent
    if (-not (Test-Path $mcpDir)) {
        New-Item -ItemType Directory -Path $mcpDir -Force | Out-Null
    }
    
    # Backup existing if present
    if (Test-Path $mcpJsonPath) {
        $backupPath = "$mcpJsonPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item -Path $mcpJsonPath -Destination $backupPath -Force
        Write-Host "  Backed up existing mcp.json to: $backupPath" -ForegroundColor Yellow
    }
    
    $mcpConfig | Set-Content -Path $mcpJsonPath -Encoding UTF8
    Write-Host "  Created: $mcpJsonPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "  IMPORTANT: Edit the file and replace 'PASTE_YOUR_TOKEN_HERE' with your GitHub token" -ForegroundColor Red
    Write-Host "  Get token from: https://github.com/settings/tokens" -ForegroundColor Cyan
} else {
    Write-Host "  Skipped. Copy the JSON above manually to: $mcpJsonPath" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== NEXT STEPS ===" -ForegroundColor Green
Write-Host ""
Write-Host "1. Restart VS Code completely (close all windows)" -ForegroundColor White
Write-Host "2. Open C:\EQ12 workspace" -ForegroundColor White
Write-Host "3. Open Copilot Chat" -ForegroundColor White
Write-Host "4. Test MCP servers with: '@workspace what files are in scripts/'" -ForegroundColor White
Write-Host "5. Verify no tikTokenizer errors" -ForegroundColor White
Write-Host ""
Write-Host "Recommended MCPs installed: 6 (filesystem, git, fetch, time, github, playwright)" -ForegroundColor Green
Write-Host "Estimated setup time: 5 minutes" -ForegroundColor White
Write-Host ""
