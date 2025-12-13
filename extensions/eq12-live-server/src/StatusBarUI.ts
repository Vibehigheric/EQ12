import { StatusBarAlignment, StatusBarItem, ThemeColor, window } from 'vscode';
import { EQ12Config } from './Config';

export class EQ12StatusBarUI {
    private static statusBarItem: StatusBarItem;

    public static Init() {
        if (!EQ12StatusBarUI.statusBarItem) {
            EQ12StatusBarUI.statusBarItem = window.createStatusBarItem(StatusBarAlignment.Right, 100);
            EQ12StatusBarUI.statusBarItem.name = 'EQ12 Live Server';
        }

        if (EQ12Config.getShowOnStatusbar) {
            EQ12StatusBarUI.statusBarItem.show();
            EQ12StatusBarUI.Offline(EQ12Config.getPort);
        }
    }

    public static Live() {
        EQ12StatusBarUI.statusBarItem.text = '$(broadcast) EQ12 Live';
        EQ12StatusBarUI.statusBarItem.command = 'eq12.liveServer.stop';
        EQ12StatusBarUI.statusBarItem.tooltip = 'EQ12 Live Server is running - Click to stop';
        EQ12StatusBarUI.statusBarItem.backgroundColor = new ThemeColor('statusBarItem.prominentBackground');
        EQ12StatusBarUI.statusBarItem.color = new ThemeColor('statusBarItem.prominentForeground');
    }

    public static Offline(port?: number) {
        const portText = port ? ` : ${port}` : '';
        EQ12StatusBarUI.statusBarItem.text = `$(circle-slash) EQ12 Server${portText}`;
        EQ12StatusBarUI.statusBarItem.command = 'eq12.liveServer.start';
        EQ12StatusBarUI.statusBarItem.tooltip = 'EQ12 Live Server is offline - Click to start';
        EQ12StatusBarUI.statusBarItem.backgroundColor = undefined;
        EQ12StatusBarUI.statusBarItem.color = undefined;
    }

    public static Working() {
        EQ12StatusBarUI.statusBarItem.text = '$(sync~spin) EQ12 Starting...';
        EQ12StatusBarUI.statusBarItem.command = undefined;
        EQ12StatusBarUI.statusBarItem.tooltip = 'EQ12 Live Server is starting...';
        EQ12StatusBarUI.statusBarItem.backgroundColor = new ThemeColor('statusBarItem.warningBackground');
        EQ12StatusBarUI.statusBarItem.color = new ThemeColor('statusBarItem.warningForeground');
    }

    public static Error() {
        EQ12StatusBarUI.statusBarItem.text = '$(error) EQ12 Error';
        EQ12StatusBarUI.statusBarItem.command = 'eq12.liveServer.healthCheck';
        EQ12StatusBarUI.statusBarItem.tooltip = 'EQ12 Live Server error - Click for health check';
        EQ12StatusBarUI.statusBarItem.backgroundColor = new ThemeColor('statusBarItem.errorBackground');
        EQ12StatusBarUI.statusBarItem.color = new ThemeColor('statusBarItem.errorForeground');
    }

    public static Hide() {
        if (EQ12StatusBarUI.statusBarItem) {
            EQ12StatusBarUI.statusBarItem.hide();
        }
    }

    public static Show() {
        if (EQ12StatusBarUI.statusBarItem) {
            EQ12StatusBarUI.statusBarItem.show();
        }
    }

    public static UpdatePort(port: number) {
        if (EQ12StatusBarUI.statusBarItem.text.includes('EQ12 Live')) {
            // Server is running, don't change the text
            return;
        }
        EQ12StatusBarUI.Offline(port);
    }

    public static dispose() {
        if (EQ12StatusBarUI.statusBarItem) {
            EQ12StatusBarUI.statusBarItem.dispose();
        }
    }
}
