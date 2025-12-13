import { ConfigurationTarget, workspace } from 'vscode';

export interface IProxy {
    enable: boolean;
    baseUri: string;
    proxyUri: string;
}

export interface IHttps {
    enable: boolean;
    cert: string;
    key: string;
    passphrase: string;
}

export class EQ12Config {
    public static get configuration() {
        return workspace.getConfiguration('eq12.liveServer');
    }

    private static getSettings<T>(val: string): T {
        return EQ12Config.configuration.get(val) as T;
    }

    private static setSettings(key: string, val: any, target: ConfigurationTarget = ConfigurationTarget.Workspace): Thenable<void> {
        return EQ12Config.configuration.update(key, val, target);
    }

    public static get getHost(): string {
        return EQ12Config.getSettings<string>('host') || '127.0.0.1';
    }

    public static get getLocalIp(): boolean {
        return EQ12Config.getSettings<boolean>('useLocalIp') || false;
    }

    public static get getPort(): number {
        return EQ12Config.getSettings<number>('port') || 5500;
    }

    public static setPort(port: number): Thenable<void> {
        return EQ12Config.setSettings('port', port);
    }

    public static get getRoot(): string {
        return EQ12Config.getSettings<string>('root') || '/dashboard';
    }

    public static get getNoBrowser(): boolean {
        return EQ12Config.getSettings<boolean>('NoBrowser') || false;
    }

    public static get getCustomBrowser(): string | null {
        return EQ12Config.getSettings<string | null>('CustomBrowser');
    }

    public static get getChromeDebuggingAttachment(): boolean {
        return EQ12Config.getSettings<boolean>('ChromeDebuggingAttachment') || false;
    }

    public static get getIgnoreFiles(): string[] {
        return EQ12Config.getSettings<string[]>('ignoreFiles') || [
            '.vscode/**',
            '**/*.scss',
            '**/*.sass',
            '**/*.ts',
            '**/*.py[co]',
            '**/__pycache__/**',
            '**/node_modules/**',
            '**/.git/**'
        ];
    }

    public static get getDonotShowInfoMsg(): boolean {
        return EQ12Config.getSettings<boolean>('donotShowInfoMsg') || false;
    }

    public static setDonotShowInfoMsg(val: boolean): Thenable<void> {
        return EQ12Config.setSettings('donotShowInfoMsg', val);
    }

    public static get getDonotVerifyTags(): boolean {
        return EQ12Config.getSettings<boolean>('donotVerifyTags') || false;
    }

    public static setDonotVerifyTags(val: boolean): Thenable<void> {
        return EQ12Config.setSettings('donotVerifyTags', val);
    }

    public static get getHttps(): IHttps {
        return EQ12Config.getSettings<IHttps>('https') || {
            enable: false,
            cert: '',
            key: '',
            passphrase: ''
        };
    }

    public static get getProxy(): IProxy {
        return EQ12Config.getSettings<IProxy>('proxy') || {
            enable: false,
            baseUri: '',
            proxyUri: ''
        };
    }

    public static get getMount(): Array<Array<string>> {
        return EQ12Config.getSettings<Array<Array<string>>>('mount') || [];
    }

    public static get getFile(): string {
        return EQ12Config.getSettings<string>('file') || '';
    }

    public static get getWait(): number {
        return EQ12Config.getSettings<number>('wait') || 100;
    }

    public static get getFullReload(): boolean {
        return EQ12Config.getSettings<boolean>('fullReload') || false;
    }

    public static get getShowOnStatusbar(): boolean {
        return EQ12Config.getSettings<boolean>('showOnStatusbar') !== false;
    }

    // EQ12-specific configurations
    public static get getDashboardPath(): string {
        return EQ12Config.getSettings<string>('dashboardPath') || 'C:/EQ12/dashboard';
    }

    public static get getEQ12Root(): string {
        return EQ12Config.getSettings<string>('eq12Root') || 'C:/EQ12';
    }

    public static get getAutoStartServices(): boolean {
        return EQ12Config.getSettings<boolean>('autoStartServices') || false;
    }

    public static get getHealthCheckInterval(): number {
        return EQ12Config.getSettings<number>('healthCheckInterval') || 30000; // 30 seconds
    }

    public static get getLogLevel(): string {
        return EQ12Config.getSettings<string>('logLevel') || 'info';
    }
}
