import * as vscode from 'vscode';
import { EQ12Config } from './Config';
import { EQ12LiveServer } from './LiveServerHelper';
import { EQ12StatusBarUI } from './StatusBarUI';

export function activate(context: vscode.ExtensionContext) {
    console.log('EQ12 Live Server extension is now active');

    // Initialize Status Bar
    EQ12StatusBarUI.Init();

    // Register commands
    const startCommand = vscode.commands.registerCommand('eq12.liveServer.start', () => {
        EQ12LiveServer.startServer();
    });

    const stopCommand = vscode.commands.registerCommand('eq12.liveServer.stop', () => {
        EQ12LiveServer.stopServer();
    });

    const changeWorkspaceCommand = vscode.commands.registerCommand('eq12.liveServer.changeWorkspace', () => {
        EQ12LiveServer.changeWorkspace();
    });

    const healthCheckCommand = vscode.commands.registerCommand('eq12.liveServer.healthCheck', () => {
        EQ12LiveServer.healthCheck();
    });

    const openDashboardCommand = vscode.commands.registerCommand('eq12.liveServer.openDashboard', () => {
        EQ12LiveServer.openDashboard();
    });

    const openLogsCommand = vscode.commands.registerCommand('eq12.liveServer.openLogs', () => {
        EQ12LiveServer.openLogs();
    });

    const runFirefoxGovernanceCommand = vscode.commands.registerCommand('eq12.liveServer.runFirefoxGovernance', () => {
        EQ12LiveServer.runScript('firefox_governance_automation.py');
    });

    const runChromeGovernanceCommand = vscode.commands.registerCommand('eq12.liveServer.runChromeGovernance', () => {
        EQ12LiveServer.runScript('chrome_governance_automation.py');
    });

    const runSystemHealthCommand = vscode.commands.registerCommand('eq12.liveServer.runSystemHealth', () => {
        EQ12LiveServer.runScript('eq12_system_health.py');
    });

    // Register all commands with context
    context.subscriptions.push(
        startCommand,
        stopCommand,
        changeWorkspaceCommand,
        healthCheckCommand,
        openDashboardCommand,
        openLogsCommand,
        runFirefoxGovernanceCommand,
        runChromeGovernanceCommand,
        runSystemHealthCommand
    );

    // Auto-start server if configured
    if (EQ12Config.getAutoStartServices) {
        setTimeout(() => {
            EQ12LiveServer.startServer();
        }, 1000);
    }

    // Watch for configuration changes
    const configWatcher = vscode.workspace.onDidChangeConfiguration(event => {
        if (event.affectsConfiguration('eq12.liveServer.showOnStatusbar')) {
            if (EQ12Config.getShowOnStatusbar) {
                EQ12StatusBarUI.Show();
            } else {
                EQ12StatusBarUI.Hide();
            }
        }

        if (event.affectsConfiguration('eq12.liveServer.port')) {
            EQ12StatusBarUI.UpdatePort(EQ12Config.getPort);
        }
    });

    context.subscriptions.push(configWatcher);

    // Show welcome message
    if (!EQ12Config.getDonotShowInfoMsg) {
        vscode.window.showInformationMessage(
            'EQ12 Live Server extension activated! Use Ctrl+Shift+P and search for "EQ12" to see available commands.',
            'Don\'t show again'
        ).then(selection => {
            if (selection === 'Don\'t show again') {
                EQ12Config.setDonotShowInfoMsg(true);
            }
        });
    }
}

export function deactivate() {
    EQ12StatusBarUI.dispose();
    console.log('EQ12 Live Server extension deactivated');
}
