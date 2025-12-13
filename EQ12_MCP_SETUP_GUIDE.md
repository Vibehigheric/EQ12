# EQ12 Model Context Protocol (MCP) Server Setup Guide

## 🚨 URGENT: GitHub Copilot Extensions Deprecation
**Deadline: November 10, 2025** - All Copilot Extensions will be sunset and discontinued.

**Action Required**: Migrate to Model Context Protocol (MCP) servers for continued AI assistant integration.

---

## 🔄 MCP Transition Overview

### What is MCP?
The **Model Context Protocol (MCP)** is an open standard for connecting AI assistants to external tools and data sources. It's the replacement for GitHub's deprecated Copilot Extensions.

### Why the Change?
- **Universal Standard**: Works with GitHub Copilot, Claude, and other AI assistants
- **Open Source**: No vendor lock-in, community-driven development
- **Enhanced Security**: Better sandboxing and permission model
- **Extended Capabilities**: More powerful than Copilot Extensions

---

## 📋 Installation Steps

### 1. Install MCP Library
```powershell
# Install the Model Context Protocol library
pip install mcp

# Verify installation
python -c "import mcp; print('✅ MCP library installed successfully')"
```

### 2. Test EQ12 MCP Server
```powershell
# Test server startup (should show initialization messages)
python C:\EQ12\scripts\eq12_mcp_server.py

# Expected output:
# 🚀 Starting EQ12 Model Context Protocol (MCP) Server
# ✅ Secret detection engine initialized
# ✅ DevOps accelerator initialized
# ✅ Security intelligence hub initialized
```

### 3. Configure GitHub Copilot (Claude Desktop)
Add to your MCP configuration file:

**For Claude Desktop** (`%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "eq12-agentic-ai": {
      "command": "python",
      "args": ["C:\\EQ12\\scripts\\eq12_mcp_server.py"],
      "env": {
        "PYTHONPATH": "C:\\EQ12;C:\\EQ12\\scripts;C:\\EQ12\\configs"
      }
    }
  }
}
```

**For GitHub Copilot** (when MCP support is available):
```json
{
  "mcpServers": {
    "eq12-agentic-ai": {
      "command": "python",
      "args": ["C:\\EQ12\\scripts\\eq12_mcp_server.py"],
      "env": {
        "PYTHONPATH": "C:\\EQ12;C:\\EQ12\\scripts;C:\\EQ12\\configs"
      }
    }
  }
}
```

### 4. Restart AI Assistant
- **Claude Desktop**: Restart the application
- **GitHub Copilot**: Follow GitHub's MCP integration instructions (coming soon)

---

## 🛡️ Available EQ12 Capabilities

Once connected, you can use these EQ12 agentic AI capabilities in any MCP-compatible assistant:

### Security Analysis
```
Analyze this code for potential secret leaks using EQ12's ML-powered detection
```

### DevOps Optimization
```
Optimize my GitHub Actions workflow using EQ12's agentic DevOps intelligence
```

### Comprehensive Security Audit
```
Run a complete security audit of my EQ12 system
```

### Goal Decomposition
```
Break down this high-level objective into actionable steps using EQ12 agentic planning
```

### System Status
```
Show me the current status of all EQ12 agentic AI systems
```

---

## 🔧 Troubleshooting

### Common Issues

**"mcp module not found"**
```powershell
pip install --upgrade mcp
```

**"EQ12 systems not available"**
- Verify `PYTHONPATH` includes EQ12 directories
- Check that EQ12 agentic systems are properly installed

**Connection Failed**
- Ensure MCP server starts without errors
- Verify configuration file syntax is correct
- Check that Python path is accessible

### Debug Mode
```powershell
# Run with verbose logging
$env:EQ12_DEBUG = "true"
python C:\EQ12\scripts\eq12_mcp_server.py
```

### Validate Configuration
```powershell
# Test MCP configuration
python -c "
import json
config = json.load(open('C:\\EQ12\\configs\\eq12_mcp_config.json'))
print('✅ MCP config is valid JSON')
print(f'Server: {config[\"mcpServers\"][\"eq12-agentic-ai\"][\"command\"]}')
"
```

---

## 📈 Benefits of MCP Migration

### 🔒 Enhanced Security
- Sandboxed execution environment
- Granular permission controls
- Audit logging for all operations

### 🌐 Universal Compatibility
- Works with multiple AI assistants
- Future-proof against vendor changes
- Open source community support

### ⚡ Improved Performance
- Async operation support
- Better resource management
- Reduced latency vs. Extensions

### 🛠️ Extended Functionality
- Access to EQ12's full agentic AI capabilities
- Real-time system integration
- Custom workflow automation

---

## 📅 Migration Timeline

| Date | Milestone |
|------|-----------|
| **Now** | Install and test EQ12 MCP server |
| **Nov 3-7, 2025** | GitHub brownout period (final testing) |
| **Nov 10, 2025** | GitHub Copilot Extensions sunset ⚠️ |
| **Post Nov 10** | MCP-only operation |

---

## 🚀 Next Steps

1. **Immediate** (Today): Install MCP library and test EQ12 server
2. **This Week**: Configure your AI assistant with MCP settings
3. **Before Nov 10**: Validate all EQ12 capabilities work via MCP
4. **Ongoing**: Expand MCP server with additional EQ12 features

---

## 📚 Resources

- **MCP Specification**: https://modelcontextprotocol.io/docs
- **Claude Desktop MCP Setup**: https://claude.ai/docs/mcp
- **GitHub MCP Integration**: (Coming soon)
- **EQ12 Agentic AI Documentation**: `EQ12_AGENTIC_AI_ECOSYSTEM_SUMMARY.md`

---

## ❓ Support

For issues with EQ12 MCP server:
1. Check the troubleshooting section above
2. Review logs in `C:\EQ12\logs\`
3. Test individual agentic systems separately
4. Validate MCP configuration syntax

**Remember**: You have only **35 days** until the GitHub Copilot Extensions deadline. Act now to ensure uninterrupted access to EQ12's agentic AI capabilities! 🚨
