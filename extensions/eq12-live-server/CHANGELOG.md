# Changelog

All notable changes to the EQ12 Live Server extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-03

### Added
- **Initial release** of EQ12 Live Server extension
- **Live server functionality** for EQ12 dashboard development
- **Status bar integration** with server state indicators
- **Command palette integration** with EQ12 operations
- **Configuration management** for EQ12-specific settings
- **Health check integration** with EQ12 system diagnostics
- **Browser governance shortcuts** for Firefox and Chrome automation
- **Log management** with quick access to EQ12 logs directory
- **Script execution** for common EQ12 automation tasks
- **Auto-start options** for development workflows

### Features
- Real-time file watching with automatic browser refresh
- Custom port and host configuration (default 5500)
- HTTPS support with custom certificates
- Workspace-aware configuration management
- Error handling with comprehensive status reporting
- Integration with EQ12 Python scripts and PowerShell wrappers

### Commands
- `EQ12: Start Live Server` - Start the live server (`Alt+L Alt+O`)
- `EQ12: Stop Live Server` - Stop the live server (`Alt+L Alt+C`)
- `EQ12: Open Dashboard` - Open EQ12 dashboard in browser
- `EQ12: Health Check` - Run system health diagnostics
- `EQ12: Open Logs` - Open logs directory
- `EQ12: Firefox Governance` - Run Firefox governance automation
- `EQ12: Chrome Governance` - Run Chrome governance automation
- `EQ12: Change Workspace` - Select workspace folder for live server

### Configuration
- `eq12.liveServer.port` - Server port (default: 5500)
- `eq12.liveServer.host` - Server host (default: 127.0.0.1)
- `eq12.liveServer.showOnStatusbar` - Show status bar item (default: true)
- `eq12.liveServer.dashboardPath` - EQ12 dashboard path
- `eq12.liveServer.eq12Root` - EQ12 installation root
- `eq12.liveServer.autoStartServices` - Auto-start server (default: false)
- `eq12.liveServer.logLevel` - Logging level (default: info)

### Technical Details
- Built with TypeScript for VS Code API integration
- Follows EQ12 project standards from AGENTS.md
- Compatible with VS Code 1.74.0+
- Requires EQ12 stack installation at C:/EQ12
- Integrates with Python 3.12+ and PowerShell 5.1+

### Known Issues
- Requires manual @types/vscode installation for development
- Some TypeScript compilation warnings in development mode
- Node.js dependency management needs manual setup for building

### Documentation
- Comprehensive README with feature overview
- INSTALL.md with detailed setup instructions
- TypeScript source code with inline documentation
- VS Code task and launch configurations for development

---

## Development Notes

This extension was created as part of the EQ12 automation stack integration, specifically to provide VS Code Live Server functionality optimized for EQ12 dashboard development and system management.

### Architecture
- **extension.ts** - Main activation and command registration
- **Config.ts** - Centralized configuration management with VS Code workspace integration
- **StatusBarUI.ts** - Status bar visual indicators and user interaction
- **LiveServerHelper.ts** - Core server operations and EQ12 script execution

### Design Principles
- Follows EQ12 AGENTS.md standards for code quality and structure
- Prioritizes integration with existing EQ12 workflows
- Provides both beginner-friendly UI and advanced configuration options
- Maintains compatibility with EQ12 Python/PowerShell automation stack
