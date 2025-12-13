// EQ12 Privacy & Security Manager
// Enhanced with features inspired by Ghostery, Privacy Badger, Port Authority, and Disconnect
// Provides comprehensive protection for betting operations

class EQ12PrivacyManager {
    constructor() {
        this.trackerDatabase = new Map();
        this.blockedRequests = new Map();
        this.securityRules = new Map();
        this.privacySettings = {
            blockTrackers: true,
            blockAds: true,
            blockSocialMedia: true,
            blockAnalytics: true,
            blockCryptomining: true,
            blockFingerprinting: true,
            protectWebRTC: true,
            spoofUserAgent: false,
            clearDataOnClose: true
        };

        this.init();
    }

    async init() {
        console.log('🛡️ EQ12 Privacy Manager initializing...');

        await this.loadSecurityRules();
        await this.loadPrivacySettings();
        await this.setupRequestBlocking();
        await this.setupUserAgentProtection();
        await this.setupWebRTCProtection();

        console.log('✅ Privacy Manager ready');
    }

    // Enhanced tracker and ad blocking inspired by Ghostery and Privacy Badger
    async setupRequestBlocking() {
        // Known tracker domains and patterns
        const trackerPatterns = [
            // Analytics
            '*://www.google-analytics.com/*',
            '*://googletagmanager.com/*',
            '*://facebook.com/tr*',
            '*://connect.facebook.net/*',
            '*://doubleclick.net/*',

            // Social Media Trackers
            '*://platform.twitter.com/*',
            '*://instagram.com/embed*',
            '*://linkedin.com/px/*',

            // Ad Networks
            '*://googlesyndication.com/*',
            '*://amazon-adsystem.com/*',
            '*://adsystem.amazon.com/*',

            // Crypto Mining
            '*://coinhive.com/*',
            '*://coin-hive.com/*',
            '*://authedmine.com/*',

            // Fingerprinting
            '*://fingerprintjs.com/*',
            '*://iovation.com/*',
            '*://threatmetrix.com/*'
        ];

        // Setup declarative net request rules
        await chrome.declarativeNetRequest.updateDynamicRules({
            removeRuleIds: Array.from({ length: 1000 }, (_, i) => i + 1),
            addRules: trackerPatterns.map((pattern, index) => ({
                id: index + 1,
                priority: 1,
                action: { type: 'block' },
                condition: {
                    urlFilter: pattern,
                    resourceTypes: ['script', 'xmlhttprequest', 'image', 'sub_frame']
                }
            }))
        });

        // Additional port scanning protection (inspired by Port Authority)
        await this.setupPortScanProtection();
    }

    async setupPortScanProtection() {
        // Block common port scanning attempts
        const portScanPatterns = [
            'http://127.0.0.1:*',
            'http://localhost:*',
            'http://192.168.*:*',
            'http://10.*:*',
            'http://172.16.*:*',
            // Common router IPs
            'http://192.168.1.1:*',
            'http://192.168.0.1:*'
        ];

        // Monitor for suspicious network requests
        chrome.webRequest?.onBeforeRequest.addListener(
            (details) => {
                const url = new URL(details.url);

                // Check for port scanning
                if (this.isPortScanAttempt(url)) {
                    console.warn('🚫 Blocked port scan attempt:', details.url);
                    this.logSecurityEvent('port_scan_blocked', {
                        url: details.url,
                        tabId: details.tabId,
                        timestamp: Date.now()
                    });
                    return { cancel: true };
                }

                // Check for data collection attempts
                if (this.isDataCollectionAttempt(details)) {
                    console.warn('🚫 Blocked data collection:', details.url);
                    this.logSecurityEvent('data_collection_blocked', details);
                    return { cancel: true };
                }

                return {};
            },
            {
                urls: ['<all_urls>'],
                types: ['xmlhttprequest', 'script', 'image']
            },
            ['blocking']
        );
    }

    // User Agent spoofing inspired by User-Agent Switcher and Chrome Mask
    async setupUserAgentProtection() {
        if (!this.privacySettings.spoofUserAgent) return;

        const commonUserAgents = [
            // Chrome on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            // Chrome on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            // Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        ];

        // Rotate user agent periodically
        setInterval(() => {
            const randomUA = commonUserAgents[Math.floor(Math.random() * commonUserAgents.length)];
            this.setUserAgent(randomUA);
        }, 300000); // Every 5 minutes
    }

    async setUserAgent(userAgent) {
        try {
            await chrome.declarativeNetRequest.updateSessionRules({
                addRules: [{
                    id: 9999,
                    priority: 1,
                    action: {
                        type: 'modifyHeaders',
                        requestHeaders: [{
                            header: 'User-Agent',
                            operation: 'set',
                            value: userAgent
                        }]
                    },
                    condition: {
                        resourceTypes: ['main_frame', 'sub_frame']
                    }
                }],
                removeRuleIds: [9999]
            });

            console.log('🎭 User agent updated for privacy protection');
        } catch (error) {
            console.error('User agent update failed:', error);
        }
    }

    // WebRTC leak protection
    async setupWebRTCProtection() {
        if (!this.privacySettings.protectWebRTC) return;

        // Inject script to disable WebRTC
        const webrtcScript = `
            (function() {
                const originalRTC = window.RTCPeerConnection;
                const originalGetUserMedia = navigator.getUserMedia;

                // Disable RTCPeerConnection
                window.RTCPeerConnection = function() {
                    throw new Error('WebRTC disabled for privacy protection');
                };

                // Disable getUserMedia
                if (navigator.getUserMedia) {
                    navigator.getUserMedia = function() {
                        throw new Error('getUserMedia disabled for privacy protection');
                    };
                }

                console.log('🔒 WebRTC protection enabled');
            })();
        `;

        // Inject into all sportsbook sites
        chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
            if (changeInfo.status === 'complete' && this.isSportsbookSite(tab.url)) {
                await chrome.scripting.executeScript({
                    target: { tabId },
                    func: new Function(webrtcScript)
                });
            }
        });
    }

    // Advanced fingerprinting protection
    async setupFingerprintingProtection() {
        const fingerprintingScript = `
            (function() {
                // Canvas fingerprinting protection
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(type, quality) {
                    // Add noise to canvas data
                    const context = this.getContext('2d');
                    const imageData = context.getImageData(0, 0, 1, 1);
                    const pixel = imageData.data;
                    pixel[0] = pixel[0] + Math.floor(Math.random() * 10) - 5;
                    pixel[1] = pixel[1] + Math.floor(Math.random() * 10) - 5;
                    pixel[2] = pixel[2] + Math.floor(Math.random() * 10) - 5;
                    context.putImageData(imageData, 0, 0);

                    return originalToDataURL.call(this, type, quality);
                };

                // Audio fingerprinting protection
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                if (AudioContext) {
                    const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
                    AudioContext.prototype.createAnalyser = function() {
                        const analyser = originalCreateAnalyser.call(this);
                        const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;
                        analyser.getFloatFrequencyData = function(array) {
                            originalGetFloatFrequencyData.call(this, array);
                            // Add noise to audio data
                            for (let i = 0; i < array.length; i++) {
                                array[i] += Math.random() * 0.0001 - 0.00005;
                            }
                        };
                        return analyser;
                    };
                }

                // Screen resolution spoofing
                Object.defineProperty(screen, 'width', {
                    get: () => 1920 + Math.floor(Math.random() * 100)
                });
                Object.defineProperty(screen, 'height', {
                    get: () => 1080 + Math.floor(Math.random() * 100)
                });

                console.log('🛡️ Fingerprinting protection enabled');
            })();
        `;

        // Apply to all sportsbook sites
        chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
            if (changeInfo.status === 'loading' && this.isSportsbookSite(tab.url)) {
                await chrome.scripting.executeScript({
                    target: { tabId },
                    func: new Function(fingerprintingScript),
                    world: 'MAIN'
                });
            }
        });
    }

    // Cookie and storage management inspired by Clear Browsing Data
    async setupDataProtection() {
        if (!this.privacySettings.clearDataOnClose) return;

        // Auto-clear data when closing sportsbook tabs
        chrome.tabs.onRemoved.addListener(async (tabId, removeInfo) => {
            const tab = await chrome.tabs.get(tabId).catch(() => null);
            if (tab && this.isSportsbookSite(tab.url)) {
                await this.clearSportsbookData(tab.url);
            }
        });

        // Clear data on browser shutdown
        chrome.runtime.onSuspend.addListener(async () => {
            await this.clearAllSportsbookData();
        });
    }

    async clearSportsbookData(url) {
        try {
            const domain = new URL(url).hostname;

            // Clear cookies
            await chrome.cookies.getAll({ domain }, async (cookies) => {
                for (const cookie of cookies) {
                    await chrome.cookies.remove({
                        url: `${cookie.secure ? 'https' : 'http'}://${cookie.domain}${cookie.path}`,
                        name: cookie.name
                    });
                }
            });

            // Clear local storage and indexedDB
            await chrome.storage.local.remove([domain]);

            console.log(`🧹 Cleared data for ${domain}`);
        } catch (error) {
            console.error('Data clearing failed:', error);
        }
    }

    // Security event logging and analysis
    async logSecurityEvent(type, details) {
        const event = {
            type,
            timestamp: Date.now(),
            details,
            userAgent: navigator.userAgent,
            vpnStatus: await this.getVPNStatus()
        };

        // Store security events
        const events = await chrome.storage.local.get('security_events') || { security_events: [] };
        events.security_events.push(event);

        // Keep only last 1000 events
        if (events.security_events.length > 1000) {
            events.security_events = events.security_events.slice(-1000);
        }

        await chrome.storage.local.set({ security_events: events.security_events });

        // Send critical events to backend
        if (this.isCriticalEvent(type)) {
            await this.sendSecurityAlert(event);
        }
    }

    // Advanced threat detection
    isPortScanAttempt(url) {
        const hostname = url.hostname;
        const port = url.port;

        // Check for private IP ranges
        const privateIPs = [
            /^127\./,
            /^192\.168\./,
            /^10\./,
            /^172\.1[6-9]\./,
            /^172\.2[0-9]\./,
            /^172\.3[0-1]\./
        ];

        return privateIPs.some(pattern => pattern.test(hostname)) ||
            hostname === 'localhost' ||
            (port && ['22', '23', '80', '443', '8080', '8443'].includes(port));
    }

    isDataCollectionAttempt(details) {
        const url = details.url.toLowerCase();
        const suspiciousPatterns = [
            'fingerprint',
            'tracking',
            'analytics',
            'collect',
            'beacon',
            'pixel',
            'facebook.com/tr',
            'google-analytics.com'
        ];

        return suspiciousPatterns.some(pattern => url.includes(pattern));
    }

    isSportsbookSite(url) {
        if (!url) return false;
        const sportsbookDomains = [
            'draftkings.com',
            'fanduel.com',
            'betmgm.com',
            'caesars.com',
            'pointsbet.com'
        ];

        return sportsbookDomains.some(domain => url.includes(domain));
    }

    isCriticalEvent(type) {
        const criticalTypes = [
            'port_scan_blocked',
            'data_collection_blocked',
            'malicious_script_detected',
            'vpn_disconnected'
        ];

        return criticalTypes.includes(type);
    }

    async sendSecurityAlert(event) {
        try {
            // Send to EQ12 backend
            const response = await fetch('http://localhost:8000/api/security/alert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(event)
            });

            if (response.ok) {
                console.log('🚨 Security alert sent successfully');
            }
        } catch (error) {
            console.error('Failed to send security alert:', error);
        }
    }

    async getVPNStatus() {
        try {
            const response = await fetch('https://api.ipify.org?format=json');
            const data = await response.json();
            return { connected: true, ip: data.ip };
        } catch (error) {
            return { connected: false, error: error.message };
        }
    }

    // Privacy settings management
    async updatePrivacySettings(newSettings) {
        this.privacySettings = { ...this.privacySettings, ...newSettings };
        await chrome.storage.local.set({ privacy_settings: this.privacySettings });

        // Re-initialize protection systems
        await this.init();
    }

    async loadPrivacySettings() {
        const stored = await chrome.storage.local.get('privacy_settings');
        if (stored.privacy_settings) {
            this.privacySettings = { ...this.privacySettings, ...stored.privacy_settings };
        }
    }

    async loadSecurityRules() {
        // Load custom security rules
        const stored = await chrome.storage.local.get('security_rules');
        if (stored.security_rules) {
            this.securityRules = new Map(Object.entries(stored.security_rules));
        }
    }

    // Public API methods
    getBlockedRequestsCount() {
        return Array.from(this.blockedRequests.values()).reduce((total, count) => total + count, 0);
    }

    getTrackerCount() {
        return this.trackerDatabase.size;
    }

    getSecurityEventCount() {
        return chrome.storage.local.get('security_events').then(data =>
            data.security_events ? data.security_events.length : 0
        );
    }

    async exportSecurityReport() {
        const events = await chrome.storage.local.get('security_events');
        const report = {
            timestamp: Date.now(),
            blockedRequests: this.getBlockedRequestsCount(),
            trackers: this.getTrackerCount(),
            events: events.security_events || [],
            settings: this.privacySettings
        };

        return report;
    }

    // Integration with main extension
    async clearAllSportsbookData() {
        const sportsbookDomains = [
            'draftkings.com',
            'fanduel.com',
            'betmgm.com',
            'caesars.com',
            'pointsbet.com'
        ];

        for (const domain of sportsbookDomains) {
            await this.clearSportsbookData(`https://${domain}`);
        }

        console.log('🧹 All sportsbook data cleared for privacy protection');
    }
}

// Export for use in background script
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EQ12PrivacyManager;
} else if (typeof self !== 'undefined') {
    self.EQ12PrivacyManager = EQ12PrivacyManager;
}
