// EQ12 Background Script - Service Worker for Firefox Extension
// Handles VPN monitoring, API communication, and notifications

class EQ12Background {
    constructor() {
        this.vpnCheckInterval = null;
        this.lastVpnStatus = null;
        this.init();
    }

    init() {
        console.log('EQ12 Background service starting...');

        // Set up listeners
        this.setupMessageListeners();
        this.setupAlarms();

        // Start VPN monitoring
        this.startVpnMonitoring();
    }

    setupMessageListeners() {
        // Listen for messages from popup/content scripts
        browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
            switch (message.action) {
                case 'getVpnStatus':
                    this.getVpnStatus().then(sendResponse);
                    return true; // Keep channel open for async response

                case 'toggleVpn':
                    this.toggleVpn().then(sendResponse);
                    return true;

                case 'checkApiHealth':
                    this.checkApiHealth().then(sendResponse);
                    return true;

                case 'logBettingOperation':
                    this.logBettingOperation(message.data);
                    break;

                default:
                    console.log('Unknown message action:', message.action);
            }
        });
    }

    setupAlarms() {
        // Create periodic alarms for monitoring
        browser.alarms.create('vpn-check', { periodInMinutes: 1 });
        browser.alarms.create('api-health', { periodInMinutes: 5 });

        browser.alarms.onAlarm.addListener((alarm) => {
            switch (alarm.name) {
                case 'vpn-check':
                    this.performVpnCheck();
                    break;
                case 'api-health':
                    this.performApiHealthCheck();
                    break;
            }
        });
    }

    async startVpnMonitoring() {
        console.log('Starting VPN monitoring...');

        // Initial VPN check
        await this.performVpnCheck();

        // Set up continuous monitoring
        this.vpnCheckInterval = setInterval(() => {
            this.performVpnCheck();
        }, 30000); // Check every 30 seconds
    }

    async performVpnCheck() {
        try {
            const currentStatus = await this.getVpnStatus();

            // Check for VPN status changes
            if (this.lastVpnStatus !== null && this.lastVpnStatus.active !== currentStatus.active) {
                if (!currentStatus.active) {
                    // VPN dropped
                    await this.handleVpnDrop();
                } else {
                    // VPN reconnected
                    await this.handleVpnReconnect(currentStatus);
                }
            }

            this.lastVpnStatus = currentStatus;

            // Update extension badge
            this.updateBadge(currentStatus);

        } catch (error) {
            console.error('VPN check failed:', error);
            this.updateBadge({ active: false, error: true });
        }
    }

    async getVpnStatus() {
        try {
            // First, try to get status from EQ12 VPN Guard API
            const apiStatus = await this.checkEQ12VpnApi();
            if (apiStatus) {
                return apiStatus;
            }

            // Fallback: check IP-based VPN detection
            const ipResponse = await fetch('https://api.ipify.org?format=json');
            const ipData = await ipResponse.json();
            const currentIP = ipData.ip;

            return {
                active: !this.isLocalIP(currentIP),
                ip: currentIP,
                region: 'Unknown',
                source: 'ip-detection'
            };

        } catch (error) {
            console.error('Error getting VPN status:', error);
            return {
                active: false,
                error: error.message,
                source: 'error'
            };
        }
    }

    async checkEQ12VpnApi() {
        try {
            const settings = await browser.storage.local.get(['eq12_api_url']);
            const apiUrl = settings.eq12_api_url || 'http://localhost:8000';

            const response = await fetch(`${apiUrl}/vpn/status`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
                signal: AbortSignal.timeout(5000) // 5 second timeout
            });

            if (response.ok) {
                const data = await response.json();
                return {
                    active: data.vpn_active || false,
                    ip: data.current_ip || 'Unknown',
                    region: data.region || 'eq12-betting',
                    source: 'eq12-api'
                };
            }

            return null;
        } catch (error) {
            console.log('EQ12 VPN API not available:', error.message);
            return null;
        }
    }

    isLocalIP(ip) {
        const localRanges = [
            /^192\.168\./,
            /^10\./,
            /^172\.(1[6-9]|2\d|3[01])\./,
            /^127\./
        ];

        return localRanges.some(range => range.test(ip));
    }

    async handleVpnDrop() {
        console.warn('🚨 VPN CONNECTION DROPPED!');

        // Show critical notification
        await this.showNotification({
            type: 'basic',
            iconUrl: 'icons/eq12-48.png',
            title: '🚨 EQ12 VPN Alert',
            message: 'VPN connection dropped! Betting operations may be at risk.',
            priority: 2
        });

        // Try to trigger VPN Guard reconnection
        try {
            const settings = await browser.storage.local.get(['eq12_api_url']);
            const apiUrl = settings.eq12_api_url || 'http://localhost:8000';

            await fetch(`${apiUrl}/vpn/reconnect`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

        } catch (error) {
            console.error('Failed to trigger VPN reconnection:', error);
        }

        // Log the incident
        await this.logSecurityIncident('vpn_drop', {
            timestamp: Date.now(),
            previous_status: this.lastVpnStatus
        });
    }

    async handleVpnReconnect(newStatus) {
        console.log('✅ VPN reconnected:', newStatus);

        await this.showNotification({
            type: 'basic',
            iconUrl: 'icons/eq12-48.png',
            title: '✅ EQ12 VPN Restored',
            message: `VPN reconnected successfully. IP: ${newStatus.ip}`,
            priority: 1
        });

        await this.logSecurityIncident('vpn_reconnect', {
            timestamp: Date.now(),
            new_ip: newStatus.ip,
            region: newStatus.region
        });
    }

    async performApiHealthCheck() {
        try {
            const settings = await browser.storage.local.get(['eq12_api_url']);
            const apiUrl = settings.eq12_api_url || 'http://localhost:8000';

            const response = await fetch(`${apiUrl}/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(10000)
            });

            if (!response.ok) {
                console.warn('EQ12 API health check failed');
            }

        } catch (error) {
            console.error('API health check error:', error);
        }
    }

    async toggleVpn() {
        try {
            const settings = await browser.storage.local.get(['eq12_api_url']);
            const apiUrl = settings.eq12_api_url || 'http://localhost:8000';

            const response = await fetch(`${apiUrl}/vpn/toggle`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                const result = await response.json();

                await this.showNotification({
                    type: 'basic',
                    iconUrl: 'icons/eq12-48.png',
                    title: 'EQ12 VPN Control',
                    message: `VPN ${result.status}`,
                    priority: 1
                });

                return { success: true, status: result.status };
            } else {
                throw new Error('VPN toggle failed');
            }

        } catch (error) {
            console.error('Error toggling VPN:', error);

            await this.showNotification({
                type: 'basic',
                iconUrl: 'icons/eq12-48.png',
                title: 'EQ12 VPN Error',
                message: 'Failed to toggle VPN. Check VPN Guard service.',
                priority: 2
            });

            return { success: false, error: error.message };
        }
    }

    async checkApiHealth() {
        try {
            const settings = await browser.storage.local.get(['eq12_api_url']);
            const apiUrl = settings.eq12_api_url || 'http://localhost:8000';

            const response = await fetch(`${apiUrl}/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(5000)
            });

            return {
                healthy: response.ok,
                status: response.status,
                url: apiUrl
            };

        } catch (error) {
            return {
                healthy: false,
                error: error.message,
                url: 'Unknown'
            };
        }
    }

    async logBettingOperation(operationData) {
        try {
            const vpnStatus = await this.getVpnStatus();

            const logEntry = {
                timestamp: Date.now(),
                operation: operationData.operation || 'unknown',
                vpn_active: vpnStatus.active,
                vpn_ip: vpnStatus.ip,
                vpn_region: vpnStatus.region,
                success: operationData.success !== false,
                details: operationData.details || {}
            };

            // Store locally
            const logs = await browser.storage.local.get(['betting_operations']) || { betting_operations: [] };
            logs.betting_operations.push(logEntry);

            // Keep only last 100 entries
            if (logs.betting_operations.length > 100) {
                logs.betting_operations = logs.betting_operations.slice(-100);
            }

            await browser.storage.local.set(logs);

            // Send to EQ12 API if available
            try {
                const settings = await browser.storage.local.get(['eq12_api_url']);
                const apiUrl = settings.eq12_api_url || 'http://localhost:8000';

                await fetch(`${apiUrl}/audit/log`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(logEntry)
                });

            } catch (error) {
                console.log('Could not send to EQ12 API:', error);
            }

        } catch (error) {
            console.error('Error logging betting operation:', error);
        }
    }

    async logSecurityIncident(type, data) {
        try {
            const incident = {
                timestamp: Date.now(),
                type: type,
                data: data,
                user_agent: navigator.userAgent
            };

            const incidents = await browser.storage.local.get(['security_incidents']) || { security_incidents: [] };
            incidents.security_incidents.push(incident);

            // Keep only last 50 incidents
            if (incidents.security_incidents.length > 50) {
                incidents.security_incidents = incidents.security_incidents.slice(-50);
            }

            await browser.storage.local.set(incidents);

        } catch (error) {
            console.error('Error logging security incident:', error);
        }
    }

    updateBadge(vpnStatus) {
        try {
            if (vpnStatus.active) {
                browser.browserAction.setBadgeText({ text: '🛡️' });
                browser.browserAction.setBadgeBackgroundColor({ color: '#00ff88' });
                browser.browserAction.setTitle({ title: `EQ12 VPN Active (${vpnStatus.ip})` });
            } else {
                browser.browserAction.setBadgeText({ text: '⚠️' });
                browser.browserAction.setBadgeBackgroundColor({ color: '#ff4444' });
                browser.browserAction.setTitle({ title: 'EQ12 VPN Disconnected - Click to check' });
            }
        } catch (error) {
            console.error('Error updating badge:', error);
        }
    }

    async showNotification(options) {
        try {
            await browser.notifications.create(options);
        } catch (error) {
            console.error('Error showing notification:', error);
        }
    }
}

// Initialize background service
const eq12Background = new EQ12Background();
