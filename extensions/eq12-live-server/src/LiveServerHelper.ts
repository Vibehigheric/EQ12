import * as vscode from 'vscode';
import { EQ12Config } from './Config';
import { EQ12StatusBarUI } from './StatusBarUI';

export class EQ12LiveServer {
    private static serverProcess: any = null;
    private static isServerRunning: boolean = false;

    public static startServer(): void {
        if (EQ12LiveServer.isServerRunning) {
            vscode.window.showInformationMessage('EQ12 Live Server is already running');
            return;
        }

        EQ12StatusBarUI.Working();

        // For now, simulate server startup
        setTimeout(() => {
            EQ12LiveServer.isServerRunning = true;
            EQ12StatusBarUI.Live();
            vscode.window.showInformationMessage(`EQ12 Live Server started at http://${EQ12Config.getHost}:${EQ12Config.getPort}`);
        }, 2000);
    }

    public static stopServer(): void {
        if (!EQ12LiveServer.isServerRunning) {
            vscode.window.showInformationMessage('EQ12 Live Server is not running');
            return;
        }

        EQ12LiveServer.isServerRunning = false;
        EQ12StatusBarUI.Offline(EQ12Config.getPort);
        vscode.window.showInformationMessage('EQ12 Live Server stopped');
    }

    public static healthCheck(): void {
        const terminal = vscode.window.createTerminal('EQ12 Health Check');
        terminal.show();
        terminal.sendText(`cd "${EQ12Config.getEQ12Root}"`);
        terminal.sendText('python eq12_system_health.py');
    }

    public static openDashboard(): void {
        const dashboardUri = vscode.Uri.file(`${EQ12Config.getDashboardPath}/index.html`);
        vscode.env.openExternal(vscode.Uri.parse(`http://${EQ12Config.getHost}:${EQ12Config.getPort}`));
    }

    public static changeWorkspace(): void {
        const folders = vscode.workspace.workspaceFolders;
        if (!folders || folders.length === 0) {
            vscode.window.showErrorMessage('No workspace folder found');
            return;
        }

        const items = folders.map(folder => ({
            label: folder.name,
            description: folder.uri.fsPath,
            folder: folder
        }));

        vscode.window.showQuickPick(items, {
            placeHolder: 'Select workspace folder for EQ12 Live Server'
        }).then(selected => {
            if (selected) {
                vscode.window.showInformationMessage(`EQ12 Live Server workspace: ${selected.label}`);
            }
        });
    }

    public static runScript(scriptName: string): void {
        const terminal = vscode.window.createTerminal(`EQ12 ${scriptName}`);
        terminal.show();
        terminal.sendText(`cd "${EQ12Config.getEQ12Root}/scripts"`);
        terminal.sendText(`python ${scriptName}`);
    }

    public static openLogs(): void {
        const logsUri = vscode.Uri.file(`${EQ12Config.getEQ12Root}/logs`);
        vscode.commands.executeCommand('vscode.openFolder', logsUri, true);
    }
}
