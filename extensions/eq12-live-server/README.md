# EQ12 Live Server Extension

A powerful VS Code extension that provides live server functionality specifically designed for the EQ12 automation and governance stack.

## Features

### 🚀 Live Server Capabilities
- **One-click live server** for EQ12 dashboard development
- **Real-time file watching** with automatic browser refresh
- **Custom port and host configuration**
- **HTTPS support** with custom certificates
- **Status bar integration** showing server state

### 🎯 EQ12-Specific Integration
- **Health monitoring** integration with EQ12 system health checks
- **Governance automation** shortcuts for Firefox and Chrome
- **Log management** with quick access to EQ12 logs directory
- **Script execution** for common EQ12 automation tasks
- **Dashboard deployment** optimized for EQ12 stack

### 🔧 Developer Experience
- **Command palette integration** with all EQ12 operations
- **Workspace-aware configuration**
- **Error handling** with comprehensive status reporting
- **Auto-start options** for development workflows

## Quick Start

1. **Install the extension** in your VS Code workspace
2. **Open your EQ12 project folder**
3. **Press `Ctrl+Shift+P`** and type "EQ12" to see available commands
4. **Click the EQ12 server icon** in the status bar to start

## Commands

| Command | Description | Keybinding |
|---------|-------------|------------|
| `EQ12: Start Live Server` | Start the live server | `Alt+L Alt+O` |
| `EQ12: Stop Live Server` | Stop the live server | `Alt+L Alt+C` |
| `EQ12: Open Dashboard` | Open EQ12 dashboard in browser | - |
| `EQ12: Health Check` | Run system health diagnostics | - |
| `EQ12: Open Logs` | Open logs directory | - |
| `EQ12: Firefox Governance` | Run Firefox governance automation | - |
| `EQ12: Chrome Governance` | Run Chrome governance automation | - |

## Configuration

Configure the extension through VS Code settings (`Ctrl+,`):

```json
{
    "eq12.liveServer.port": 5500,
    "eq12.liveServer.host": "127.0.0.1",
    "eq12.liveServer.showOnStatusbar": true,
    "eq12.liveServer.dashboardPath": "C:/EQ12/dashboard",
    "eq12.liveServer.eq12Root": "C:/EQ12",
    "eq12.liveServer.autoStartServices": false,
    "eq12.liveServer.logLevel": "info"
}
```

## EQ12 Integration

This extension is specifically designed to work with the EQ12 automation stack:

- **Python Scripts**: Executes EQ12 Python automation scripts
- **PowerShell Integration**: Supports EQ12 PowerShell wrappers
- **Dashboard System**: Serves the EQ12 dashboard with live reload
- **Governance Tools**: Quick access to browser governance automation
- **Health Monitoring**: Integration with EQ12 system health checks

## Development

### File Structure
```
src/
├── extension.ts        # Main extension entry point
├── Config.ts          # Configuration management
├── StatusBarUI.ts     # Status bar integration
└── LiveServerHelper.ts # Core live server functionality
```

### Building
1. Install dependencies: `npm install`
2. Compile TypeScript: `npm run compile`
3. Package extension: `vsce package`

## Requirements

- **VS Code** 1.74.0 or higher
- **Python 3.12+** for EQ12 script execution
- **PowerShell** for EQ12 automation wrappers
- **EQ12 stack** installed at `C:/EQ12`

## Known Issues

- Requires manual VS Code API types installation for development
- Some TypeScript compilation warnings in development mode
- Node.js dependency management needs manual setup

## Release Notes

### 0.1.0
- Initial release
- Basic live server functionality
- EQ12 dashboard integration
- Status bar controls
- Command palette integration

## Contributing

This extension is part of the EQ12 project. See `AGENTS.md` for contribution guidelines and development standards.

## License

MIT License - see the EQ12 project for details.
