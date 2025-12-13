# EQ12 VS Code Extension Installation Guide

## Prerequisites

Before installing the EQ12 Live Server extension, ensure you have:

### Required Software
- **VS Code 1.74.0+** - The extension host environment
- **Python 3.12+** - For EQ12 script execution
- **PowerShell 5.1+** - For EQ12 automation wrappers
- **Node.js 16+** (Optional) - For development and building from source

### EQ12 Stack Setup
- **EQ12 project** installed at `C:/EQ12`
- **Python environment** configured with EQ12 dependencies
- **Workspace folders** properly structured

## Installation Methods

### Method 1: Direct Installation (Recommended)
1. **Copy extension folder** to VS Code extensions directory:
   ```
   C:\Users\<username>\.vscode\extensions\eq12-live-server-0.1.0\
   ```

2. **Restart VS Code** to load the extension

3. **Verify installation** by checking Extensions panel or Command Palette (`Ctrl+Shift+P`)

### Method 2: Development Installation
1. **Clone/copy** the extension source to your development workspace
2. **Open in VS Code** and press `F5` to launch Extension Development Host
3. **Test functionality** in the new VS Code window

## Configuration

### Workspace Settings
Add to your VS Code `settings.json`:

```json
{
    "eq12.liveServer.port": 5500,
    "eq12.liveServer.host": "127.0.0.1",
    "eq12.liveServer.showOnStatusbar": true,
    "eq12.liveServer.dashboardPath": "C:/EQ12/dashboard",
    "eq12.liveServer.eq12Root": "C:/EQ12",
    "eq12.liveServer.autoStartServices": false,
    "eq12.liveServer.logLevel": "info",
    "eq12.liveServer.healthCheckInterval": 30000
}
```

### Environment Variables
Ensure these environment variables are set for full EQ12 functionality:
- `EQ12_LOGS` - Path to logs directory
- `OPENAI_API_KEY` - For AI-powered features
- `TELEGRAM_BOT_TOKEN` - For notifications (optional)

## Usage Quick Start

### Basic Operations
1. **Open EQ12 workspace** in VS Code
2. **Start live server** via status bar click or `Ctrl+Shift+P` → "EQ12: Start Live Server"
3. **View dashboard** at `http://localhost:5500`
4. **Monitor system** with built-in health checks

### Key Features
- **Live reload** for dashboard development
- **One-click** browser governance automation
- **Integrated** health monitoring and logging
- **Quick access** to EQ12 scripts and utilities

### Status Bar Integration
The EQ12 status bar item shows:
- 🔴 **Offline** - Server stopped, click to start
- 🟢 **Live** - Server running, click to stop
- 🟡 **Working** - Server starting up
- 🔴 **Error** - Server error, click for diagnostics

## Troubleshooting

### Common Issues

#### Extension Not Loading
- Check VS Code version compatibility (1.74.0+)
- Verify extension is in correct directory
- Restart VS Code completely
- Check Developer Console (`Help > Toggle Developer Tools`)

#### TypeScript Compilation Errors
- Install Node.js and run: `npm install --save-dev @types/vscode typescript`
- Build extension: `npm run compile`
- Check for missing dependencies

#### EQ12 Scripts Not Found
- Verify `eq12.liveServer.eq12Root` points to correct EQ12 installation
- Check Python path and environment activation
- Ensure EQ12 scripts have proper permissions

#### Live Server Won't Start
- Check port availability (default 5500)
- Verify dashboard path exists
- Review EQ12 logs for system issues
- Run health check: `EQ12: Health Check` command

### Debug Mode
Enable extension debugging:
1. Open **Command Palette** (`Ctrl+Shift+P`)
2. Run **Developer: Reload Window**
3. Check **Developer Console** for error messages
4. Enable **Log Level** to debug in settings

### Health Diagnostics
Use built-in health check:
- **Command**: `EQ12: Health Check`
- **Reports**: System status, dependency validation, configuration issues
- **Logs**: Detailed diagnostic information in `C:/EQ12/logs`

## Development

### Building from Source
```bash
cd C:/EQ12/extensions/eq12-live-server
npm install
npm run compile
```

### Extension Structure
```
eq12-live-server/
├── package.json          # Extension manifest
├── tsconfig.json         # TypeScript configuration
├── src/
│   ├── extension.ts      # Main entry point
│   ├── Config.ts         # Configuration management
│   ├── StatusBarUI.ts    # Status bar integration
│   └── LiveServerHelper.ts # Core functionality
└── .vscode/
    ├── launch.json       # Debug configuration
    └── tasks.json        # Build tasks
```

### Contributing
See `AGENTS.md` in the EQ12 root for development standards and contribution guidelines.

## Support

For issues, feature requests, and support:
- **Check EQ12 logs**: `C:/EQ12/logs`
- **Run health check**: VS Code Command Palette → "EQ12: Health Check"
- **Review documentation**: EQ12 project README and AGENTS.md
- **Debug mode**: Enable verbose logging and check Developer Console

---

*This extension is part of the EQ12 automation and governance stack.*
