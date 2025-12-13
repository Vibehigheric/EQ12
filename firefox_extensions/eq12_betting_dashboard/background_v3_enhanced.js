// EQ12 Background Service Worker - Enhanced with MDN Best Practices
// Implements modern Manifest V3 patterns for VPN monitoring, API communication, and notifications

class EQ12ServiceWorker {
    constructor() {
        this.vpnStatus = { connected: false, lastCheck: null };
        this.apiHealth = { eq12: false, telegram: false };
        this.activeConnections = new Map();
        this.init();
    }

    async init() {
        console.log('EQ12 Service Worker initializing...');

        // Setup all listeners
        await this.setupMessageListeners();
        await this.setupAlarms();
        await this.setupTabListeners();
        await this.setupNotificationListeners();

        // Initialize monitoring
        await this.startVpnMonitoring();
        await this.checkApiHealth();

        console.log('EQ12 Service Worker ready');
    }

    // Enhanced message handling with better error handling and validation
    async setupMessageListeners() {
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender)
                .then(response => {
                    if (response !== undefined) {
                        sendResponse({ success: true, data: response });
                    }
                })
                .catch(error => {
                    console.error('Message handling error:', error);
                    sendResponse({
                        success: false,
                        error: error.message,
                        timestamp: Date.now()
                    });
                });
            return true; // Keep channel open for async response
        });

        // Handle external connections
        chrome.runtime.onConnect.addListener((port) => {
            this.handleConnection(port);
        });
    }

    async handleMessage(message, sender) {
        if (!message.action) {
            throw new Error('Invalid message format: missing action');
        }

        const actions = {
            'getVpnStatus': () => this.getVpnStatus(),
            'toggleVpn': () => this.toggleVpn(),
            'checkApiHealth': () => this.checkApiHealth(),
            'logBettingOperation': (data) => this.logBettingOperation(data),
            'sendTelegram': (data) => this.sendTelegramMessage(data),
            'getSportsbookData': (data) => this.getSportsbookData(data),
            'getTabsInfo': () => this.getTabsInfo(),
            'injectContentScript': (data) => this.injectContentScript(data),
            'captureTab': (data) => this.captureVisibleTab(data)
        };

        const handler = actions[message.action];
        if (!handler) {
            throw new Error(`Unknown action: ${message.action}`);
        }

        return await handler(message.data);
    }

    // Advanced connection handling for long-lived connections
    handleConnection(port) {
        const connectionId = `${port.sender.tab?.id || 'unknown'}_${Date.now()}`;
        this.activeConnections.set(connectionId, port);

        port.onMessage.addListener((message) => {
            this.handlePortMessage(message, port, connectionId);
        });

        port.onDisconnect.addListener(() => {
            this.activeConnections.delete(connectionId);
            console.log(`Connection ${connectionId} closed`);
        });

        console.log(`New connection established: ${connectionId}`);
    }

    async handlePortMessage(message, port, connectionId) {
        try {
            const response = await this.handleMessage(message, port.sender);
            port.postMessage({
                id: message.id,
                success: true,
                data: response
            });
        } catch (error) {
            port.postMessage({
                id: message.id,
                success: false,
                error: error.message
            });
        }
    }

    // Enhanced alarm system with better scheduling
    async setupAlarms() {
        // Clear existing alarms
        await chrome.alarms.clearAll();

        // Setup monitoring alarms
        await chrome.alarms.create('vpn-monitor', { periodInMinutes: 0.5 }); // 30 seconds
        await chrome.alarms.create('api-health-check', { periodInMinutes: 5 });
        await chrome.alarms.create('betting-audit', { periodInMinutes: 15 });

        chrome.alarms.onAlarm.addListener((alarm) => {
            this.handleAlarm(alarm);
        });
    }

    async handleAlarm(alarm) {
        try {
            switch (alarm.name) {
                case 'vpn-monitor':
                    await this.performVpnCheck();
                    break;
                case 'api-health-check':
                    await this.checkApiHealth();
                    break;
                case 'betting-audit':
                    await this.performBettingAudit();
                    break;
            }
        } catch (error) {
            console.error(`Alarm ${alarm.name} handler error:`, error);
        }
    }

    // Advanced tab management following MDN Tabs API patterns
    async setupTabListeners() {
        chrome.tabs.onActivated.addListener((activeInfo) => {
            this.handleTabActivation(activeInfo);
        });

        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            this.handleTabUpdate(tabId, changeInfo, tab);
        });

        chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
            this.handleTabRemoval(tabId, removeInfo);
        });
    }

    async handleTabActivation(activeInfo) {
        try {
            const tab = await chrome.tabs.get(activeInfo.tabId);
            if (this.isSportsbookTab(tab)) {
                await this.activateSportsbookMode(tab);
            }
        } catch (error) {
            console.error('Tab activation error:', error);
        }
    }

    async handleTabUpdate(tabId, changeInfo, tab) {
        if (changeInfo.status === 'complete' && this.isSportsbookTab(tab)) {
            await this.injectEnhancedContentScript(tab);
        }
    }

    handleTabRemoval(tabId, removeInfo) {
        // Clean up any tab-specific data
        this.activeConnections.forEach((port, connectionId) => {
            if (connectionId.startsWith(`${tabId}_`)) {
                this.activeConnections.delete(connectionId);
            }
        });
    }

    // Enhanced notification system
    async setupNotificationListeners() {
        chrome.notifications.onClicked.addListener((notificationId) => {
            this.handleNotificationClick(notificationId);
        });

        chrome.notifications.onButtonClicked.addListener((notificationId, buttonIndex) => {
            this.handleNotificationButton(notificationId, buttonIndex);
        });
    }

    async handleNotificationClick(notificationId) {
        if (notificationId.startsWith('vpn-')) {
            // Open VPN settings
            chrome.tabs.create({ url: 'chrome://extensions/?id=' + chrome.runtime.id });
        } else if (notificationId.startsWith('bet-')) {
            // Open betting dashboard
            chrome.tabs.create({ url: 'http://localhost:8000/dashboard' });
        }
    }

    // VPN monitoring with enhanced error handling
    async performVpnCheck() {
        try {
            const vpnStatus = await this.checkVpnConnection();
            const statusChanged = this.vpnStatus.connected !== vpnStatus.connected;

            this.vpnStatus = {
                ...vpnStatus,
                lastCheck: Date.now()
            };

            if (statusChanged) {
                await this.handleVpnStatusChange(vpnStatus);
            }

            // Broadcast status to all connected tabs
            await this.broadcastVpnStatus();

        } catch (error) {
            console.error('VPN check error:', error);
            await this.showNotification('vpn-error', {
                type: 'basic',
                iconUrl: 'icons/eq12-48.png',
                title: 'EQ12 VPN Monitor',
                message: `VPN check failed: ${error.message}`
            });
        }
    }

    async checkVpnConnection() {
        // Check multiple endpoints for reliability
        const endpoints = [
            'https://api.ipify.org?format=json',
            'https://httpbin.org/ip'
        ];

        for (const endpoint of endpoints) {
            try {
                const response = await fetch(endpoint, {
                    method: 'GET',
                    signal: AbortSignal.timeout(5000)
                });

                if (response.ok) {
                    const data = await response.json();
                    const ip = data.ip || data.origin?.split(',')[0];

                    return {
                        connected: await this.validateVpnIp(ip),
                        ip: ip,
                        endpoint: endpoint,
                        timestamp: Date.now()
                    };
                }
            } catch (error) {
                console.warn(`VPN check failed for ${endpoint}:`, error);
                continue;
            }
        }

        throw new Error('All VPN check endpoints failed');
    }

    async validateVpnIp(ip) {
        // Load VPN IP ranges from storage or config
        const vpnRanges = await chrome.storage.local.get(['vpnIpRanges']);
        const ranges = vpnRanges.vpnIpRanges || [];

        return ranges.some(range => this.ipInRange(ip, range));
    }

    ipInRange(ip, range) {
        // Implement CIDR range checking
        // This is a simplified version - you'd want a proper CIDR library
        return range.includes(ip.split('.').slice(0, 2).join('.'));
    }

    async handleVpnStatusChange(newStatus) {
        const message = newStatus.connected
            ? 'VPN connection established'
            : 'VPN connection lost - betting operations paused';

        await this.showNotification('vpn-status', {
            type: 'basic',
            iconUrl: newStatus.connected ? 'icons/eq12-48.png' : 'icons/eq12-error-48.png',
            title: 'EQ12 VPN Monitor',
            message: message,
            buttons: [
                { title: 'Check Status' },
                { title: 'Open Dashboard' }
            ]
        });

        // Log the change
        await this.logBettingOperation({
            type: 'vpn_status_change',
            status: newStatus.connected ? 'connected' : 'disconnected',
            timestamp: Date.now(),
            ip: newStatus.ip
        });
    }

    async broadcastVpnStatus() {
        const message = {
            action: 'vpnStatusUpdate',
            data: this.vpnStatus
        };

        // Send to all content scripts
        const tabs = await chrome.tabs.query({});
        for (const tab of tabs) {
            if (this.isSportsbookTab(tab)) {
                try {
                    await chrome.tabs.sendMessage(tab.id, message);
                } catch (error) {
                    // Tab might not have content script - ignore
                }
            }
        }

        // Send to all open connections
        this.activeConnections.forEach((port) => {
            try {
                port.postMessage(message);
            } catch (error) {
                // Port might be closed - ignore
            }
        });
    }

    // Enhanced sportsbook detection and management
    isSportsbookTab(tab) {
        if (!tab?.url) return false;

        const sportsbookDomains = [
            'draftkings.com',
            'fanduel.com',
            'betmgm.com',
            'caesars.com',
            'pointsbet.com'
        ];

        return sportsbookDomains.some(domain => tab.url.includes(domain));
    }

    async activateSportsbookMode(tab) {
        console.log(`Activating sportsbook mode for ${tab.url}`);

        // Update extension badge
        await chrome.action.setBadgeText({
            text: '●',
            tabId: tab.id
        });
        await chrome.action.setBadgeBackgroundColor({
            color: this.vpnStatus.connected ? '#00ff00' : '#ff0000',
            tabId: tab.id
        });

        // Ensure content script is injected
        await this.injectEnhancedContentScript(tab);
    }

    async injectEnhancedContentScript(tab) {
        try {
            // Check if already injected
            const results = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: () => window.EQ12_INJECTED || false
            });

            if (!results[0]?.result) {
                await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    files: ['sportsbook_scraper.js']
                });

                console.log(`Content script injected into tab ${tab.id}`);
            }
        } catch (error) {
            console.error('Content script injection error:', error);
        }
    }

    // API health monitoring
    async checkApiHealth() {
        const results = {
            eq12: await this.checkEndpoint('http://localhost:8000/health'),
            telegram: await this.checkTelegramBot(),
            timestamp: Date.now()
        };

        this.apiHealth = results;

        // Notify if any service is down
        const downServices = Object.entries(results)
            .filter(([key, value]) => key !== 'timestamp' && !value)
            .map(([key]) => key);

        if (downServices.length > 0) {
            await this.showNotification('api-health', {
                type: 'basic',
                iconUrl: 'icons/eq12-warning-48.png',
                title: 'EQ12 API Health Alert',
                message: `Services down: ${downServices.join(', ')}`
            });
        }

        return results;
    }

    async checkEndpoint(url) {
        try {
            const response = await fetch(url, {
                method: 'HEAD',
                signal: AbortSignal.timeout(3000)
            });
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    async checkTelegramBot() {
        try {
            const botToken = await this.getStoredValue('telegramBotToken');
            if (!botToken) return false;

            const response = await fetch(`https://api.telegram.org/bot${botToken}/getMe`, {
                signal: AbortSignal.timeout(3000)
            });
            const data = await response.json();
            return data.ok === true;
        } catch (error) {
            return false;
        }
    }

    // Enhanced storage utilities
    async getStoredValue(key) {
        const result = await chrome.storage.local.get([key]);
        return result[key];
    }

    async setStoredValue(key, value) {
        await chrome.storage.local.set({ [key]: value });
    }

    // Notification helper
    async showNotification(id, options) {
        await chrome.notifications.create(id, {
            requireInteraction: true,
            ...options
        });
    }

    // Public API methods
    async getVpnStatus() {
        return this.vpnStatus;
    }

    async toggleVpn() {
        // This would integrate with VPN client API
        throw new Error('VPN toggle not implemented - requires VPN client integration');
    }

    async sendTelegramMessage(data) {
        const botToken = await this.getStoredValue('telegramBotToken');
        const chatId = await this.getStoredValue('telegramChatId');

        if (!botToken || !chatId) {
            throw new Error('Telegram configuration missing');
        }

        const response = await fetch(`https://api.telegram.org/bot${botToken}/sendMessage`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chat_id: chatId,
                text: data.message,
                parse_mode: data.parseMode || 'HTML'
            })
        });

        const result = await response.json();
        if (!result.ok) {
            throw new Error(`Telegram API error: ${result.description}`);
        }

        return result;
    }

    async logBettingOperation(data) {
        const logEntry = {
            ...data,
            timestamp: Date.now(),
            vpnStatus: this.vpnStatus,
            sessionId: await this.getStoredValue('sessionId') || 'unknown'
        };

        // Store locally
        const logs = await this.getStoredValue('bettingLogs') || [];
        logs.push(logEntry);

        // Keep only last 1000 entries
        if (logs.length > 1000) {
            logs.splice(0, logs.length - 1000);
        }

        await this.setStoredValue('bettingLogs', logs);

        // Send to EQ12 API if available
        if (this.apiHealth.eq12) {
            try {
                await fetch('http://localhost:8000/api/log', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(logEntry)
                });
            } catch (error) {
                console.warn('Failed to send log to EQ12 API:', error);
            }
        }
    }

    async startVpnMonitoring() {
        console.log('VPN monitoring started');
        // Initial check
        await this.performVpnCheck();
    }

    async getTabsInfo() {
        const tabs = await chrome.tabs.query({});
        return tabs
            .filter(tab => this.isSportsbookTab(tab))
            .map(tab => ({
                id: tab.id,
                url: tab.url,
                title: tab.title,
                active: tab.active
            }));
    }

    async captureVisibleTab(data) {
        const screenshot = await chrome.tabs.captureVisibleTab(
            data.windowId,
            { format: 'png', quality: 90 }
        );

        // Store screenshot with metadata
        await this.logBettingOperation({
            type: 'screenshot',
            tabId: data.tabId,
            screenshot: screenshot,
            reason: data.reason || 'manual'
        });

        return { screenshot };
    }

    async performBettingAudit() {
        const logs = await this.getStoredValue('bettingLogs') || [];
        const recentLogs = logs.filter(log =>
            Date.now() - log.timestamp < 900000 // Last 15 minutes
        );

        if (recentLogs.length > 0) {
            await this.sendTelegramMessage({
                message: `🎯 EQ12 Audit Report\n📊 Operations: ${recentLogs.length}\n🔒 VPN: ${this.vpnStatus.connected ? '✅' : '❌'}\n⏰ Time: ${new Date().toLocaleTimeString()}`
            });
        }
    }
}

// Initialize the service worker
const eq12ServiceWorker = new EQ12ServiceWorker();

// Handle service worker lifecycle
self.addEventListener('install', (event) => {
    console.log('EQ12 Service Worker installing...');
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    console.log('EQ12 Service Worker activating...');
    event.waitUntil(clients.claim());
});
