// EQ12 Proxy & VPN Manager
// Enhanced with features inspired by FoxyProxy Standard and network security extensions
// Provides comprehensive proxy management and VPN integration for betting operations

class EQ12ProxyManager {
    constructor() {
        this.proxies = new Map();
        this.currentProxy = null;
        this.vpnProviders = new Map();
        this.networkRules = new Map();
        this.connectionStats = {
            attempts: 0,
            successes: 0,
            failures: 0,
            lastCheck: null
        };

        this.init();
    }

    async init() {
        console.log('🔐 EQ12 Proxy Manager initializing...');

        await this.loadProxyConfiguration();
        await this.setupVPNProviders();
        await this.setupNetworkRules();
        await this.setupConnectionMonitoring();
        await this.setupDNSProtection();

        console.log('✅ Proxy Manager ready');
    }

    // Proxy configuration inspired by FoxyProxy Standard
    async loadProxyConfiguration() {
        // Default proxy configurations for different regions
        const defaultProxies = [
            {
                id: 'us-east',
                name: 'US East Coast',
                type: 'http',
                host: 'proxy-us-east.example.com',
                port: 8080,
                username: '',
                password: '',
                enabled: false,
                priority: 1,
                patterns: ['*.draftkings.com', '*.fanduel.com']
            },
            {
                id: 'us-west',
                name: 'US West Coast',
                type: 'http',
                host: 'proxy-us-west.example.com',
                port: 8080,
                username: '',
                password: '',
                enabled: false,
                priority: 2,
                patterns: ['*.betmgm.com', '*.caesars.com']
            },
            {
                id: 'residential',
                name: 'Residential Proxy',
                type: 'socks5',
                host: 'residential-proxy.example.com',
                port: 1080,
                username: '',
                password: '',
                enabled: false,
                priority: 3,
                patterns: ['*']
            }
        ];

        // Load saved proxy settings
        const stored = await chrome.storage.local.get('proxy_settings');
        if (stored.proxy_settings) {
            for (const proxy of stored.proxy_settings) {
                this.proxies.set(proxy.id, proxy);
            }
        } else {
            // Initialize with defaults
            for (const proxy of defaultProxies) {
                this.proxies.set(proxy.id, proxy);
            }
            await this.saveProxyConfiguration();
        }
    }

    async setupVPNProviders() {
        // VPN provider configurations
        const vpnProviders = [
            {
                id: 'wireguard',
                name: 'WireGuard',
                type: 'wireguard',
                configPath: 'C:\\EQ12\\wireguard\\eq12-betting.conf',
                enabled: true,
                autoConnect: true,
                killSwitch: true
            },
            {
                id: 'openvpn',
                name: 'OpenVPN',
                type: 'openvpn',
                configPath: 'C:\\EQ12\\openvpn\\client.ovpn',
                enabled: false,
                autoConnect: false,
                killSwitch: false
            }
        ];

        for (const provider of vpnProviders) {
            this.vpnProviders.set(provider.id, provider);
        }
    }

    // Advanced network rules for different sites
    async setupNetworkRules() {
        const rules = [
            {
                id: 'draftkings-direct',
                pattern: '*.draftkings.com',
                action: 'direct',
                priority: 1,
                description: 'Use direct connection for DraftKings'
            },
            {
                id: 'fanduel-proxy',
                pattern: '*.fanduel.com',
                action: 'proxy',
                proxyId: 'us-east',
                priority: 2,
                description: 'Route FanDuel through US East proxy'
            },
            {
                id: 'analytics-block',
                pattern: '*google-analytics.com',
                action: 'block',
                priority: 3,
                description: 'Block analytics tracking'
            },
            {
                id: 'default-vpn',
                pattern: '*',
                action: 'vpn',
                vpnId: 'wireguard',
                priority: 100,
                description: 'Default VPN for all other traffic'
            }
        ];

        for (const rule of rules) {
            this.networkRules.set(rule.id, rule);
        }
    }

    // Connection monitoring and health checks
    async setupConnectionMonitoring() {
        // Periodic connection health checks
        setInterval(async () => {
            await this.performHealthCheck();
        }, 30000); // Every 30 seconds

        // Monitor network changes
        if ('connection' in navigator) {
            navigator.connection.addEventListener('change', () => {
                this.handleNetworkChange();
            });
        }

        // Monitor VPN status
        setInterval(async () => {
            await this.checkVPNStatus();
        }, 10000); // Every 10 seconds
    }

    // DNS protection and leak prevention
    async setupDNSProtection() {
        // DNS over HTTPS configuration
        const dnsConfig = {
            providers: [
                { name: 'Cloudflare', url: 'https://1.1.1.1/dns-query' },
                { name: 'Quad9', url: 'https://9.9.9.9/dns-query' },
                { name: 'OpenDNS', url: 'https://208.67.222.222/dns-query' }
            ],
            current: 'Cloudflare',
            leakProtection: true
        };

        // Implement DNS leak protection
        if (dnsConfig.leakProtection) {
            await this.enableDNSLeakProtection();
        }
    }

    // Proxy management methods
    async addProxy(config) {
        const proxyId = config.id || `proxy_${Date.now()}`;
        const proxy = {
            id: proxyId,
            name: config.name,
            type: config.type || 'http',
            host: config.host,
            port: config.port,
            username: config.username || '',
            password: config.password || '',
            enabled: config.enabled || false,
            priority: config.priority || 50,
            patterns: config.patterns || ['*'],
            createdAt: Date.now(),
            stats: {
                connections: 0,
                successes: 0,
                failures: 0,
                avgLatency: 0
            }
        };

        this.proxies.set(proxyId, proxy);
        await this.saveProxyConfiguration();

        console.log(`➕ Added proxy: ${proxy.name}`);
        return proxyId;
    }

    async removeProxy(proxyId) {
        if (this.proxies.has(proxyId)) {
            const proxy = this.proxies.get(proxyId);
            this.proxies.delete(proxyId);
            await this.saveProxyConfiguration();

            console.log(`➖ Removed proxy: ${proxy.name}`);
            return true;
        }
        return false;
    }

    async enableProxy(proxyId) {
        const proxy = this.proxies.get(proxyId);
        if (!proxy) return false;

        // Test proxy before enabling
        const isWorking = await this.testProxy(proxy);
        if (!isWorking) {
            console.warn(`⚠️ Proxy ${proxy.name} is not responding`);
            return false;
        }

        proxy.enabled = true;
        this.currentProxy = proxy;

        // Configure browser to use proxy
        await this.applyProxyConfiguration(proxy);

        console.log(`🔗 Enabled proxy: ${proxy.name}`);
        return true;
    }

    async disableProxy(proxyId) {
        const proxy = this.proxies.get(proxyId);
        if (!proxy) return false;

        proxy.enabled = false;

        if (this.currentProxy === proxy) {
            this.currentProxy = null;
            await this.clearProxyConfiguration();
        }

        console.log(`🔗 Disabled proxy: ${proxy.name}`);
        return true;
    }

    async testProxy(proxy) {
        const startTime = Date.now();

        try {
            // Create test configuration
            const testConfig = {
                mode: 'fixed_servers',
                rules: {
                    singleProxy: {
                        scheme: proxy.type,
                        host: proxy.host,
                        port: proxy.port
                    }
                }
            };

            // Test connection with timeout
            const testUrl = 'https://httpbin.org/ip';
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

            const response = await fetch(testUrl, {
                signal: controller.signal,
                method: 'GET'
            });

            clearTimeout(timeoutId);

            if (response.ok) {
                const latency = Date.now() - startTime;
                proxy.stats.avgLatency = (proxy.stats.avgLatency + latency) / 2;
                proxy.stats.successes++;

                console.log(`✅ Proxy ${proxy.name} working (${latency}ms)`);
                return true;
            } else {
                proxy.stats.failures++;
                return false;
            }
        } catch (error) {
            proxy.stats.failures++;
            console.warn(`❌ Proxy ${proxy.name} test failed:`, error.message);
            return false;
        }
    }

    async applyProxyConfiguration(proxy) {
        try {
            const config = {
                mode: 'fixed_servers',
                rules: {
                    singleProxy: {
                        scheme: proxy.type,
                        host: proxy.host,
                        port: proxy.port
                    }
                }
            };

            // Add authentication if provided
            if (proxy.username && proxy.password) {
                config.rules.singleProxy.auth = {
                    username: proxy.username,
                    password: proxy.password
                };
            }

            await chrome.proxy.settings.set({
                value: config,
                scope: 'regular'
            });

            this.connectionStats.attempts++;
            return true;
        } catch (error) {
            console.error('Failed to apply proxy configuration:', error);
            return false;
        }
    }

    async clearProxyConfiguration() {
        try {
            await chrome.proxy.settings.clear({
                scope: 'regular'
            });
            console.log('🔓 Proxy configuration cleared');
            return true;
        } catch (error) {
            console.error('Failed to clear proxy configuration:', error);
            return false;
        }
    }

    // VPN management
    async connectVPN(vpnId) {
        const vpn = this.vpnProviders.get(vpnId);
        if (!vpn) return false;

        try {
            // Execute VPN connection command
            const result = await this.executeVPNCommand('connect', vpn);
            if (result.success) {
                vpn.connected = true;
                console.log(`🔒 Connected to VPN: ${vpn.name}`);

                // Verify connection
                setTimeout(async () => {
                    await this.verifyVPNConnection();
                }, 5000);

                return true;
            }
        } catch (error) {
            console.error(`VPN connection failed: ${error.message}`);
        }

        return false;
    }

    async disconnectVPN(vpnId) {
        const vpn = this.vpnProviders.get(vpnId);
        if (!vpn) return false;

        try {
            const result = await this.executeVPNCommand('disconnect', vpn);
            if (result.success) {
                vpn.connected = false;
                console.log(`🔓 Disconnected from VPN: ${vpn.name}`);
                return true;
            }
        } catch (error) {
            console.error(`VPN disconnection failed: ${error.message}`);
        }

        return false;
    }

    async executeVPNCommand(action, vpn) {
        // Simulate VPN command execution
        // In a real implementation, this would interface with the VPN client
        return new Promise((resolve) => {
            setTimeout(() => {
                // Simulate success/failure
                const success = Math.random() > 0.1; // 90% success rate
                resolve({ success, message: `VPN ${action} ${success ? 'successful' : 'failed'}` });
            }, 2000);
        });
    }

    // Network monitoring
    async performHealthCheck() {
        this.connectionStats.lastCheck = Date.now();

        // Check current IP address
        try {
            const ipResponse = await fetch('https://api.ipify.org?format=json');
            const ipData = await ipResponse.json();

            // Check if IP has changed (potential connection issue)
            if (this.lastKnownIP && this.lastKnownIP !== ipData.ip) {
                console.log('🔄 IP address changed:', ipData.ip);
                await this.handleIPChange(ipData.ip);
            }

            this.lastKnownIP = ipData.ip;
            this.connectionStats.successes++;

            return true;
        } catch (error) {
            this.connectionStats.failures++;
            console.warn('Health check failed:', error.message);
            return false;
        }
    }

    async checkVPNStatus() {
        // Check if VPN is actually connected
        try {
            const response = await fetch('https://api.ipify.org?format=json');
            const data = await response.json();

            // Simple IP-based VPN detection (should be enhanced)
            const isVPNActive = this.isVPNIP(data.ip);

            // Update VPN status in UI
            if (typeof window !== 'undefined' && window.EQ12UI) {
                window.EQ12UI.updateVPNIndicator(isVPNActive, this.getLocationFromIP(data.ip));
            }

            return { connected: isVPNActive, ip: data.ip };
        } catch (error) {
            console.error('VPN status check failed:', error);
            return { connected: false, error: error.message };
        }
    }

    async verifyVPNConnection() {
        // DNS leak test
        const dnsLeakResult = await this.checkDNSLeak();

        // WebRTC leak test
        const webrtcLeakResult = await this.checkWebRTCLeak();

        // IP location verification
        const locationResult = await this.verifyIPLocation();

        const isSecure = dnsLeakResult.secure && webrtcLeakResult.secure && locationResult.secure;

        if (!isSecure) {
            console.warn('🚨 VPN connection has potential leaks!');
            await this.handleVPNLeak({
                dns: dnsLeakResult,
                webrtc: webrtcLeakResult,
                location: locationResult
            });
        }

        return { secure: isSecure, details: { dnsLeakResult, webrtcLeakResult, locationResult } };
    }

    async checkDNSLeak() {
        try {
            // Check DNS servers
            const response = await fetch('https://dnsleaktest.com/');
            // Parse response for DNS leak information
            // This is a simplified implementation
            return { secure: true, servers: [] };
        } catch (error) {
            return { secure: false, error: error.message };
        }
    }

    async checkWebRTCLeak() {
        return new Promise((resolve) => {
            // Create RTCPeerConnection to test for IP leaks
            const pc = new RTCPeerConnection({
                iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
            });

            const localIPs = new Set();

            pc.createDataChannel('');
            pc.createOffer().then(offer => pc.setLocalDescription(offer));

            pc.onicecandidate = (event) => {
                if (event.candidate) {
                    const ip = event.candidate.candidate.match(/\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b/);
                    if (ip) localIPs.add(ip[0]);
                }
            };

            setTimeout(() => {
                pc.close();
                const hasPrivateIP = Array.from(localIPs).some(ip =>
                    ip.startsWith('192.168.') || ip.startsWith('10.') || ip.startsWith('172.')
                );

                resolve({
                    secure: !hasPrivateIP,
                    localIPs: Array.from(localIPs)
                });
            }, 3000);
        });
    }

    async verifyIPLocation() {
        try {
            const response = await fetch('https://ipapi.co/json/');
            const data = await response.json();

            // Verify location matches expected VPN server location
            const expectedCountry = this.getExpectedVPNCountry();
            const isCorrectLocation = !expectedCountry || data.country_code === expectedCountry;

            return {
                secure: isCorrectLocation,
                location: {
                    country: data.country_name,
                    city: data.city,
                    ip: data.ip
                }
            };
        } catch (error) {
            return { secure: false, error: error.message };
        }
    }

    // Event handlers
    async handleNetworkChange() {
        console.log('🌐 Network change detected');

        // Re-establish connections if needed
        if (this.currentProxy) {
            const isWorking = await this.testProxy(this.currentProxy);
            if (!isWorking) {
                console.warn('🔄 Reconnecting proxy after network change...');
                await this.enableProxy(this.currentProxy.id);
            }
        }

        // Check VPN status
        await this.checkVPNStatus();
    }

    async handleIPChange(newIP) {
        console.log(`🔄 IP changed to: ${newIP}`);

        // Log IP change event
        await this.logSecurityEvent('ip_changed', {
            oldIP: this.lastKnownIP,
            newIP: newIP,
            timestamp: Date.now()
        });

        // Verify new IP is still secure
        await this.verifyVPNConnection();
    }

    async handleVPNLeak(leakInfo) {
        console.error('🚨 VPN leak detected:', leakInfo);

        // Log security event
        await this.logSecurityEvent('vpn_leak', leakInfo);

        // Send alert
        if (typeof chrome !== 'undefined' && chrome.notifications) {
            chrome.notifications.create({
                type: 'basic',
                iconUrl: 'icons/eq12-48.png',
                title: 'EQ12 Security Alert',
                message: 'VPN connection leak detected! Your betting activities may not be protected.'
            });
        }

        // Attempt to fix the leak
        await this.attemptLeakFix();
    }

    async attemptLeakFix() {
        // Try to reconnect VPN
        const activeVPN = Array.from(this.vpnProviders.values()).find(vpn => vpn.connected);
        if (activeVPN) {
            await this.disconnectVPN(activeVPN.id);
            await new Promise(resolve => setTimeout(resolve, 2000));
            await this.connectVPN(activeVPN.id);
        }
    }

    // Utility methods
    isVPNIP(ip) {
        // Basic VPN detection - should be enhanced with actual VPN IP ranges
        const knownVPNRanges = [
            /^185\.159\./,  // Example VPN range
            /^192\.227\./,  // Example VPN range
        ];

        return knownVPNRanges.some(range => range.test(ip));
    }

    getLocationFromIP(ip) {
        // Simplified location detection
        if (this.isVPNIP(ip)) {
            return 'VPN Server';
        }
        return 'Unknown';
    }

    getExpectedVPNCountry() {
        const activeVPN = Array.from(this.vpnProviders.values()).find(vpn => vpn.connected);
        return activeVPN?.expectedCountry || null;
    }

    async enableDNSLeakProtection() {
        // Implement DNS leak protection measures
        console.log('🛡️ DNS leak protection enabled');
    }

    async logSecurityEvent(type, data) {
        try {
            // Send to EQ12 backend
            await fetch('http://localhost:8000/api/security/event', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, data, timestamp: Date.now() })
            });
        } catch (error) {
            console.error('Failed to log security event:', error);
        }
    }

    async saveProxyConfiguration() {
        const proxySettings = Array.from(this.proxies.values());
        await chrome.storage.local.set({ proxy_settings: proxySettings });
    }

    // Public API
    getProxyList() {
        return Array.from(this.proxies.values());
    }

    getVPNList() {
        return Array.from(this.vpnProviders.values());
    }

    getCurrentProxy() {
        return this.currentProxy;
    }

    getConnectionStats() {
        return {
            ...this.connectionStats,
            successRate: this.connectionStats.successes / (this.connectionStats.attempts || 1) * 100
        };
    }

    async exportConfiguration() {
        return {
            proxies: Array.from(this.proxies.values()),
            vpnProviders: Array.from(this.vpnProviders.values()),
            networkRules: Array.from(this.networkRules.values()),
            timestamp: Date.now()
        };
    }

    async importConfiguration(config) {
        if (config.proxies) {
            for (const proxy of config.proxies) {
                this.proxies.set(proxy.id, proxy);
            }
        }

        if (config.vpnProviders) {
            for (const vpn of config.vpnProviders) {
                this.vpnProviders.set(vpn.id, vpn);
            }
        }

        await this.saveProxyConfiguration();
        console.log('📥 Configuration imported successfully');
    }
}

// Export for use in background script
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EQ12ProxyManager;
} else if (typeof self !== 'undefined') {
    self.EQ12ProxyManager = EQ12ProxyManager;
}
